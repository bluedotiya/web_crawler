use std::sync::Arc;

use axum::{extract::State, http::StatusCode, response::IntoResponse, Json};
use serde_json::json;

use crate::state::AppState;
use shared::neo4j_client;

pub async fn health() -> impl IntoResponse {
    (StatusCode::OK, Json(json!({"status": "ok"})))
}

pub async fn ready(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    if neo4j_client::health_check(&state.graph).await {
        (StatusCode::OK, Json(json!({"status": "ready"})))
    } else {
        (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(json!({"status": "not ready", "reason": "neo4j unavailable"})),
        )
    }
}
