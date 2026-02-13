use neo4rs::{query, Graph};

use crate::config::Config;

/// Creates a new Neo4j connection using the provided config.
pub async fn connect(config: &Config) -> Result<Graph, neo4rs::Error> {
    Graph::new(&config.neo4j_uri, &config.neo4j_username, &config.neo4j_password).await
}

/// Tests Neo4j connectivity with a simple query.
pub async fn health_check(graph: &Graph) -> bool {
    match graph.run(query("MATCH () RETURN 1 LIMIT 1")).await {
        Ok(_) => true,
        Err(e) => {
            tracing::warn!("Database connection degraded: {}", e);
            false
        }
    }
}

/// Attempts to restore the database connection.
pub async fn restore_connection(config: &Config) -> Option<Graph> {
    match connect(config).await {
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
