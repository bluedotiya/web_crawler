use neo4rs::{query, Graph};

/// Creates indexes and constraints for optimal query performance.
/// All statements are idempotent (`IF NOT EXISTS`), safe to call on every startup.
pub async fn ensure_schema(graph: &Graph) -> Result<(), neo4rs::Error> {
    let statements = [
        "CREATE INDEX url_job_status IF NOT EXISTS FOR (n:URL) ON (n.job_status)",
        "CREATE INDEX url_name_http IF NOT EXISTS FOR (n:URL) ON (n.name, n.http_type)",
        "CREATE INDEX root_name_depth IF NOT EXISTS FOR (n:ROOT) ON (n.name, n.requested_depth)",
        "CREATE INDEX url_claimed_at IF NOT EXISTS FOR (n:URL) ON (n.claimed_at)",
        "CREATE CONSTRAINT root_crawl_id IF NOT EXISTS FOR (n:ROOT) REQUIRE n.crawl_id IS UNIQUE",
        "CREATE INDEX url_crawl_id IF NOT EXISTS FOR (n:URL) ON (n.crawl_id)",
    ];

    for stmt in &statements {
        graph.run(query(stmt)).await?;
    }

    tracing::info!("Database schema indexes ensured");
    Ok(())
}
