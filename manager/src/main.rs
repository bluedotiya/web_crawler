mod config;

use std::sync::Arc;
use std::time::Duration;

use axum::{extract::State, http::StatusCode, response::IntoResponse, routing::post, Json, Router};
use hickory_resolver::TokioResolver;
use neo4rs::{query, Graph};
use serde::Deserialize;
use serde_json::json;
use tracing_subscriber::EnvFilter;

use config::Config;
use shared::{crawler, dns, neo4j_client, url_normalize};

struct AppState {
    graph: Graph,
    client: reqwest::Client,
    resolver: TokioResolver,
    config: Config,
}

#[derive(Deserialize)]
struct CrawlRequest {
    url: String,
    depth: i64,
}

/// Check if a ROOT node with the same name and depth already exists.
async fn root_exists(graph: &Graph, name: &str, depth: i64) -> Result<bool, neo4rs::Error> {
    let mut result = graph
        .execute(
            query("MATCH (n:ROOT {name: $name, requested_depth: $depth}) RETURN n LIMIT 1")
                .param("name", name)
                .param("depth", depth),
        )
        .await?;
    Ok(result.next().await?.is_some())
}

struct CrawlGraph {
    root_name: String,
    root_ip: String,
    root_domain: String,
    http_type: String,
    depth: i64,
    request_time: String,
    children: Vec<(String, String, String, String)>, // (name, ip, domain, http_type)
}

/// Create ROOT node and child URL nodes in a single transaction.
/// Uses MERGE for children to prevent duplicates from concurrent requests.
async fn create_crawl_graph(graph: &Graph, cg: &CrawlGraph) -> Result<(), neo4rs::Error> {
    let mut txn = graph.start_txn().await?;

    // Create ROOT node
    txn.run(
        query(
            "CREATE (:ROOT {name: $name, ip: $ip, domain: $domain, http_type: $http_type, \
             requested_depth: $req_depth, current_depth: 0, request_time: $req_time})",
        )
        .param("name", cg.root_name.as_str())
        .param("ip", cg.root_ip.as_str())
        .param("domain", cg.root_domain.as_str())
        .param("http_type", cg.http_type.as_str())
        .param("req_depth", cg.depth)
        .param("req_time", cg.request_time.as_str()),
    )
    .await?;

    // Create child URL nodes and Lead relationships
    for (child_name, child_ip, child_domain, child_http_type) in &cg.children {
        txn.run(
            query(
                "MATCH (root:ROOT {name: $root_name, requested_depth: $req_depth}) \
                 MERGE (c:URL {name: $name, http_type: $http_type}) \
                 ON CREATE SET c.ip = $ip, c.domain = $domain, \
                     c.job_status = 'PENDING', c.requested_depth = $req_depth, \
                     c.current_depth = 1, c.request_time = $req_time \
                 MERGE (root)-[:Lead]->(c)",
            )
            .param("root_name", cg.root_name.as_str())
            .param("req_depth", cg.depth)
            .param("name", child_name.as_str())
            .param("ip", child_ip.as_str())
            .param("domain", child_domain.as_str())
            .param("http_type", child_http_type.as_str())
            .param("req_time", cg.request_time.as_str()),
        )
        .await?;
    }

    txn.commit().await?;
    Ok(())
}

async fn handle_crawl(
    State(state): State<Arc<AppState>>,
    Json(req): Json<CrawlRequest>,
) -> impl IntoResponse {
    // 1. Normalize root URL
    let (root_name, http_type) = url_normalize::normalize_url(&req.url);

    // 2. Fetch page HTML
    let page_data = match crawler::get_page_data(&state.client, &req.url).await {
        Some(pd) => pd,
        None => {
            return (
                StatusCode::NOT_FOUND,
                Json(json!({"Error": "Requested URL was not found"})),
            )
        }
    };

    // 3. Extract URLs from HTML
    let extracted_urls = crawler::extract_urls(&page_data.html);

    // 4. Check if ROOT already exists
    match root_exists(&state.graph, &root_name, req.depth).await {
        Ok(true) => {
            return (
                StatusCode::OK,
                Json(json!({"Info": "requested url was already searched"})),
            )
        }
        Ok(false) => {}
        Err(e) => {
            tracing::error!("Neo4j query failed: {}", e);
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"Error": "Database error"})),
            );
        }
    }

    tracing::info!("Requested url is not on database, starting search!");

    // 5. DNS resolve root URL
    let root_stats =
        match dns::get_network_stats(&state.resolver, &root_name, state.config.max_dns_depth)
            .await
        {
            Ok(stats) => stats,
            Err(e) => {
                tracing::error!("Root DNS failed: {}", e);
                return (
                    StatusCode::NOT_FOUND,
                    Json(json!({"Error": "Requested URL was not found"})),
                );
            }
        };

    // 6. Resolve DNS for each extracted URL, build children list
    let request_time = format!("{:?}", page_data.elapsed);
    let mut children: Vec<(String, String, String, String)> = Vec::new();

    for url in &extracted_urls {
        let (norm_name, child_http_type) = url_normalize::normalize_url(url);
        match dns::get_network_stats(&state.resolver, &norm_name, state.config.max_dns_depth).await
        {
            Ok(stats) => {
                children.push((norm_name, stats.ip, stats.domain, child_http_type));
            }
            Err(_) => continue,
        }
    }

    // 7. Create ROOT + children in Neo4j
    let cg = CrawlGraph {
        root_name: root_name.clone(),
        root_ip: root_stats.ip,
        root_domain: root_stats.domain,
        http_type,
        depth: req.depth,
        request_time,
        children,
    };
    if let Err(e) = create_crawl_graph(&state.graph, &cg).await
    {
        tracing::error!("Failed to create graph: {}", e);
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({"Error": "Database error"})),
        );
    }

    (StatusCode::OK, Json(json!({"Success": "Job started"})))
}


#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("manager=info")),
        )
        .init();

    // Load config
    let _ = dotenvy::dotenv();
    let config = Config::from_env();

    // Connect to Neo4j
    let graph =
        neo4j_client::connect(&config.neo4j_uri, &config.neo4j_username, &config.neo4j_password)
            .await?;
    tracing::info!("Connected to Neo4j at {}", config.neo4j_uri);

    // Create HTTP client
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(config.http_timeout_secs))
        .build()?;

    // Create DNS resolver
    let resolver = TokioResolver::builder_tokio()?.build();

    let addr = format!("0.0.0.0:{}", config.server_port);
    tracing::info!("Manager listening on {}", addr);

    let state = Arc::new(AppState {
        graph,
        client,
        resolver,
        config,
    });

    let app = Router::new()
        .route("/", post(handle_crawl))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
