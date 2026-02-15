use neo4rs::{query, Graph};

/// Creates indexes and constraints for optimal query performance.
/// All statements are idempotent (`IF NOT EXISTS`), safe to call on every startup.
pub async fn ensure_schema(graph: &Graph) -> Result<(), neo4rs::Error> {
    let statements = [
        // Fast job claiming: find PENDING/stale URLs by status
        "CREATE INDEX url_job_status IF NOT EXISTS FOR (n:URL) ON (n.job_status)",
        // Deduplication: MERGE uses (name, http_type) to prevent duplicate URL nodes
        "CREATE INDEX url_name_http IF NOT EXISTS FOR (n:URL) ON (n.name, n.http_type)",
        // Stale job detection: find old IN-PROGRESS jobs by claimed_at timestamp
        "CREATE INDEX url_claimed_at IF NOT EXISTS FOR (n:URL) ON (n.claimed_at)",
        // Uniqueness: one ROOT per crawl_id
        "CREATE CONSTRAINT root_crawl_id IF NOT EXISTS FOR (n:ROOT) REQUIRE n.crawl_id IS UNIQUE",
        // Crawl scoping: efficiently query all URLs belonging to a crawl
        "CREATE INDEX url_crawl_id IF NOT EXISTS FOR (n:URL) ON (n.crawl_id)",
        // Exact match for status updates, cancellation checks, and reset-to-pending
        "CREATE INDEX url_name_http_crawl IF NOT EXISTS FOR (n:URL) ON (n.name, n.http_type, n.crawl_id)",
    ];

    for stmt in &statements {
        graph.run(query(stmt)).await?;
    }

    tracing::info!("Database schema indexes ensured");
    Ok(())
}
