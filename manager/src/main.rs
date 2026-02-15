mod config;
mod models;
mod routes;
mod services;
mod state;

use std::sync::Arc;
use std::time::Duration;

use axum::{
    routing::{delete, get, post},
    Router,
};
use tower_http::{
    compression::CompressionLayer,
    cors::{Any, CorsLayer},
    trace::TraceLayer,
};
use tracing_subscriber::EnvFilter;

use config::Config;
use shared::{neo4j_client, schema};
use state::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("manager=info,tower_http=info")),
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

    // Ensure database schema (indexes)
    schema::ensure_schema(&graph).await?;

    // Create HTTP client
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(config.http_timeout_secs))
        .user_agent("Mozilla/5.0 (compatible; WebCrawler/1.0)")
        .build()?;

    // Create DNS resolver
    let resolver = hickory_resolver::TokioResolver::builder_tokio()?.build();

    let addr = format!("0.0.0.0:{}", config.server_port);
    tracing::info!("Manager listening on {}", addr);

    let state = Arc::new(AppState {
        graph,
        client,
        resolver,
        config,
    });

    // Permissive CORS — acceptable behind nginx reverse proxy
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // API v1 routes
    let api_v1 = Router::new()
        .route("/crawls", post(routes::crawl::create_crawl))
        .route("/crawls", get(routes::status::list_crawls))
        .route("/crawls/{id}", get(routes::status::get_crawl))
        .route("/crawls/{id}", delete(routes::crawl::delete_crawl))
        .route("/crawls/{id}/graph", get(routes::graph::get_graph))
        .route("/crawls/{id}/stats", get(routes::status::get_crawl_stats))
        .route("/crawls/{id}/ws", get(routes::ws::crawl_ws));

    let app = Router::new()
        // Health endpoints
        .route("/livez", get(routes::health::livez))
        .route("/readyz", get(routes::health::readyz))
        // API v1
        .nest("/api/v1", api_v1)
        .layer(CompressionLayer::new())
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app)
        .with_graceful_shutdown(async {
            let _ = tokio::signal::ctrl_c().await;
            tracing::info!("Received shutdown signal, draining connections...");
        })
        .await?;

    Ok(())
}
