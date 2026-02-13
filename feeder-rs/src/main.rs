mod config;
mod crawler;
mod dns;
mod error;
mod job;
mod neo4j_client;
mod url_normalize;

use std::time::Duration;

use hickory_resolver::TokioResolver;
use rand::Rng;
use tracing_subscriber::EnvFilter;

use config::Config;

async fn random_sleep(config: &Config) {
    let secs =
        rand::thread_rng().gen_range(config.sleep_min_secs..=config.sleep_max_secs);
    tokio::time::sleep(Duration::from_secs(secs)).await;
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("feeder=info")),
        )
        .init();

    // Load config
    let _ = dotenvy::dotenv();
    let config = Config::from_env();

    // Create shared resources
    let mut graph = neo4j_client::connect(&config).await?;

    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(config.http_timeout_secs))
        .build()?;

    let resolver = TokioResolver::builder_tokio()?.build();

    tracing::info!("Feeder started, connecting to {}", config.neo4j_uri);

    // Main loop -- mirrors Python main()
    loop {
        // Health check loop with reconnection (Bug #1 fixed)
        while !neo4j_client::health_check(&graph).await {
            if let Some(new_graph) = neo4j_client::restore_connection(&config).await {
                graph = new_graph;
            } else {
                random_sleep(&config).await;
            }
        }

        random_sleep(&config).await;

        // Fetch a pending job
        let mut url_job = match job::fetch_job(&graph).await {
            Ok(Some(j)) => j,
            Ok(None) => {
                tracing::info!("Job not found, Give me something to do");
                continue;
            }
            Err(e) => {
                tracing::error!("Failed to fetch job: {}", e);
                continue;
            }
        };

        // Process the job
        match job::feeding(&graph, &client, &resolver, &config, &mut url_job).await {
            Ok(true) => {
                tracing::info!("Feed Cycle Completed for: {}", url_job.name);
            }
            Ok(false) => {
                tracing::error!("Something went wrong during feeding :(");
            }
            Err(e) => {
                tracing::error!("Feed error: {}", e);
            }
        }
    }
}
