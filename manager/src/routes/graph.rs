use std::sync::Arc;

use axum::{extract::Path, extract::State, http::StatusCode, response::IntoResponse, Json};
use serde_json::json;

use crate::services::graph_service;
use crate::state::AppState;

/// GET /api/v1/crawls/:id/graph — Get graph data for visualization.
pub async fn get_graph(
    State(state): State<Arc<AppState>>,
    Path(crawl_id): Path<String>,
) -> impl IntoResponse {
    match graph_service::get_graph_data(&state.graph, &crawl_id).await {
        Ok(Some(data)) => (StatusCode::OK, Json(json!(data))),
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Crawl not found"})),
        ),
        Err(e) => {
            tracing::error!("Failed to get graph data: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database error"})),
            )
        }
    }
}
