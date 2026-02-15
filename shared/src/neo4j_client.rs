use neo4rs::{query, Graph};

/// Creates a new Neo4j connection.
pub async fn connect(uri: &str, username: &str, password: &str) -> Result<Graph, neo4rs::Error> {
    Graph::new(uri, username, password).await
}

/// Tests Neo4j connectivity with a simple query.
/// Uses `RETURN 1` instead of `MATCH () RETURN 1 LIMIT 1` to work on empty databases.
pub async fn health_check(graph: &Graph) -> bool {
    match graph.run(query("RETURN 1")).await {
        Ok(_) => true,
        Err(e) => {
            tracing::warn!("Database connection degraded: {}", e);
            false
        }
    }
}

/// Attempts to restore the database connection.
pub async fn restore_connection(uri: &str, username: &str, password: &str) -> Option<Graph> {
    match connect(uri, username, password).await {
        Ok(graph) => {
            if health_check(&graph).await {
                tracing::info!("Database connection restored");
                Some(graph)
            } else {
                None
            }
        }
        Err(_) => None,
    }
}
