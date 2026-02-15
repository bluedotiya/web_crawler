use axum::{http::StatusCode, response::IntoResponse, routing::get, Json, Router};
use serde_json::json;

async fn health() -> impl IntoResponse {
    (StatusCode::OK, Json(json!({"status": "ok"})))
}

/// Spawns a minimal health check HTTP server on port 8081.
/// Runs as a background task — does not block.
pub fn spawn_health_server() {
    tokio::spawn(async {
        let app = Router::new().route("/livez", get(health));

        let listener = match tokio::net::TcpListener::bind("0.0.0.0:8081").await {
            Ok(l) => l,
            Err(e) => {
                tracing::error!("Failed to bind health server on :8081: {}", e);
                return;
            }
        };

        tracing::info!("Feeder health server listening on :8081");
        if let Err(e) = axum::serve(listener, app).await {
            tracing::error!("Health server error: {}", e);
        }
    });
}
