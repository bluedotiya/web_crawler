use std::collections::HashSet;

use neo4rs::{query, Graph};

use crate::config::Config;
use crate::crawler::{self, PageData};
use crate::dns;
use crate::url_normalize;

/// Represents a URL job fetched from Neo4j.
pub struct UrlJob {
    pub name: String,
    pub http_type: String,
    pub job_status: String,
    pub requested_depth: i64,
    pub current_depth: i64,
    pub attempts: Option<i64>,
}

/// Represents a child node to be created in Neo4j.
struct ChildNode {
    name: String,
    ip: String,
    domain: String,
    http_type: String,
    requested_depth: i64,
    current_depth: i64,
    request_time: String,
}

/// Atomically fetches and claims a single PENDING URL job from Neo4j.
/// Sets status to IN-PROGRESS in the same query to prevent race conditions
/// when multiple feeder pods run concurrently.
pub async fn fetch_job(graph: &Graph) -> Result<Option<UrlJob>, anyhow::Error> {
    let mut result = graph
        .execute(query(
            "MATCH (n:URL) \
             WHERE n.current_depth <> n.requested_depth AND n.job_status = 'PENDING' \
             SET n.job_status = 'IN-PROGRESS' \
             RETURN n LIMIT 1",
        ))
        .await?;

    match result.next().await? {
        Some(row) => {
            let node: neo4rs::Node = row.get("n")?;
            Ok(Some(UrlJob {
                name: node.get("name")?,
                http_type: node.get("http_type")?,
                job_status: node.get("job_status")?,
                requested_depth: node.get("requested_depth")?,
                current_depth: node.get("current_depth")?,
                attempts: node.get::<i64>("attempts").ok(),
            }))
        }
        None => Ok(None),
    }
}

/// Updates a job's status and attempts counter in Neo4j.
async fn update_job_status(
    graph: &Graph,
    job: &UrlJob,
    status: &str,
    attempts: Option<i64>,
) -> Result<(), anyhow::Error> {
    let q = query(
        "MATCH (n:URL {name: $name, http_type: $http_type, current_depth: $current_depth}) \
         SET n.job_status = $status, n.attempts = $attempts",
    )
    .param("name", job.name.as_str())
    .param("http_type", job.http_type.as_str())
    .param("current_depth", job.current_depth)
    .param("status", status)
    .param("attempts", attempts.unwrap_or(0));

    graph.run(q).await?;
    Ok(())
}

/// Attempts to fetch a URL's HTML content. Implements retry logic.
///
/// Bug #3 fix: proper spacing in error messages.
async fn validate_job(
    graph: &Graph,
    client: &reqwest::Client,
    config: &Config,
    job: &mut UrlJob,
) -> Result<Option<PageData>, anyhow::Error> {
    let full_url = format!("{}{}", job.http_type, job.name);

    match crawler::get_page_data(client, &full_url).await {
        Some(page_data) => Ok(Some(page_data)),
        None => {
            let attempts = job.attempts.unwrap_or(0) + 1;
            job.attempts = Some(attempts);

            tracing::warn!("Request failed: {} -- Attempts: {}", full_url, attempts);

            if attempts >= config.max_attempts {
                tracing::error!(
                    "Failure limit reached! Giving up on {} after {} attempts.",
                    full_url,
                    attempts
                );
                update_job_status(graph, job, "FAILED", Some(attempts)).await?;
            } else {
                update_job_status(graph, job, &job.job_status.clone(), Some(attempts)).await?;
            }

            Ok(None)
        }
    }
}

/// Filters a list of candidate URLs against the database, returning only those
/// that don't already exist. Pushes the check into Cypher instead of loading
/// the entire graph into memory.
async fn filter_new_urls(
    graph: &Graph,
    candidates: &HashSet<String>,
) -> Result<HashSet<String>, anyhow::Error> {
    let candidate_list: Vec<&str> = candidates.iter().map(|s| s.as_str()).collect();
    let mut result = graph
        .execute(
            query(
                "UNWIND $urls AS url \
                 OPTIONAL MATCH (n:URL) \
                 WHERE (n.http_type + n.name) = url \
                 WITH url, n \
                 WHERE n IS NULL \
                 RETURN url",
            )
            .param("urls", candidate_list),
        )
        .await?;

    let mut new_urls = HashSet::new();
    while let Some(row) = result.next().await? {
        let url: String = row.get("url")?;
        new_urls.insert(url);
    }
    Ok(new_urls)
}

/// Creates child URL nodes and Lead relationships in a single transaction.
async fn batch_create_children(
    graph: &Graph,
    parent: &UrlJob,
    children: &[ChildNode],
) -> Result<(), anyhow::Error> {
    let mut txn = graph.start_txn().await?;

    for child in children {
        txn.run(
            query(
                "MATCH (p:URL {name: $pname, http_type: $phttp, current_depth: $pdepth}) \
                 CREATE (p)-[:Lead]->(c:URL { \
                     name: $name, ip: $ip, domain: $domain, http_type: $http_type, \
                     job_status: 'PENDING', requested_depth: $req_depth, \
                     current_depth: $cur_depth, request_time: $req_time \
                 })",
            )
            .param("pname", parent.name.as_str())
            .param("phttp", parent.http_type.as_str())
            .param("pdepth", parent.current_depth)
            .param("name", child.name.as_str())
            .param("ip", child.ip.as_str())
            .param("domain", child.domain.as_str())
            .param("http_type", child.http_type.as_str())
            .param("req_depth", child.requested_depth)
            .param("cur_depth", child.current_depth)
            .param("req_time", child.request_time.as_str()),
        )
        .await?;
    }

    txn.commit().await?;
    Ok(())
}

/// Main processing pipeline for a single job.
///
/// Orchestrates: validate -> IN-PROGRESS -> extract -> dedup -> DNS -> create -> COMPLETED
pub async fn feeding(
    graph: &Graph,
    client: &reqwest::Client,
    resolver: &hickory_resolver::TokioResolver,
    config: &Config,
    job: &mut UrlJob,
) -> Result<bool, anyhow::Error> {
    // Step 1: Validate (fetch HTML) — job is already IN-PROGRESS from fetch_job()
    let page_data = match validate_job(graph, client, config, job).await? {
        Some(pd) => pd,
        None => return Ok(false),
    };

    // Step 2: Extract URLs from HTML
    let extracted_urls = crawler::extract_urls(&page_data.html);

    // Step 3: Deduplicate against existing DB nodes (server-side)
    let upper_urls: HashSet<String> = extracted_urls.iter().map(|u| u.to_uppercase()).collect();
    let new_urls = filter_new_urls(graph, &upper_urls).await?;

    if new_urls.is_empty() {
        tracing::warn!("No new URLs found in: {}", job.name);
        update_job_status(graph, job, "COMPLETED", job.attempts).await?;
        return Ok(true);
    }

    // Step 4: Normalize, DNS resolve, build child list
    let normalized: HashSet<(String, String)> = new_urls
        .iter()
        .map(|u| url_normalize::normalize_url(u))
        .collect();

    let mut children: Vec<ChildNode> = Vec::new();
    let request_time = format!("{:?}", page_data.elapsed);

    for (name, http_type) in &normalized {
        match dns::get_network_stats(resolver, name, config.max_dns_depth).await {
            Ok(stats) => {
                children.push(ChildNode {
                    name: name.clone(),
                    ip: stats.ip,
                    domain: stats.domain,
                    http_type: http_type.clone(),
                    requested_depth: job.requested_depth,
                    current_depth: job.current_depth + 1,
                    request_time: request_time.clone(),
                });
            }
            Err(e) => {
                tracing::error!("URL: {} -- FAILED: {}", name, e);
                continue;
            }
        }
    }

    if children.is_empty() {
        update_job_status(graph, job, "FAILED", job.attempts).await?;
        return Ok(false);
    }

    // Step 6: Batch-create nodes and relationships
    batch_create_children(graph, job, &children).await?;

    // Step 7: Mark COMPLETED
    update_job_status(graph, job, "COMPLETED", job.attempts).await?;
    Ok(true)
}
