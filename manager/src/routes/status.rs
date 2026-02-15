use std::sync::Arc;

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use serde::Deserialize;
use serde_json::json;

use crate::models::crawl::CrawlListResponse;
use crate::services::crawl_service;
use crate::state::AppState;

#[derive(Deserialize)]
pub struct ListParams {
    pub status: Option<String>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

/// GET /api/v1/crawls — List crawls with optional filtering.
pub async fn list_crawls(
    State(state): State<Arc<AppState>>,
    Query(params): Query<ListParams>,
) -> impl IntoResponse {
    let limit = params.limit.unwrap_or(20).min(100);
    let offset = params.offset.unwrap_or(0).max(0);

    match crawl_service::list_crawls(
        &state.graph,
        params.status.as_deref(),
        limit,
        offset,
    )
    .await
    {
        Ok((crawls, total)) => (
            StatusCode::OK,
            Json(json!(CrawlListResponse {
                crawls,
                total,
                offset,
                limit,
            })),
        ),
        Err(e) => {
            tracing::error!("Failed to list crawls: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database error"})),
            )
        }
    }
}

/// GET /api/v1/crawls/:id — Get crawl detail with progress.
pub async fn get_crawl(
    State(state): State<Arc<AppState>>,
    Path(crawl_id): Path<String>,
) -> impl IntoResponse {
    match crawl_service::get_crawl_progress(&state.graph, &crawl_id).await {
        Ok(Some(progress)) => (StatusCode::OK, Json(json!(progress))),
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Crawl not found"})),
        ),
        Err(e) => {
            tracing::error!("Failed to get crawl: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database error"})),
            )
        }
    }
}

/// GET /api/v1/crawls/:id/stats — Get crawl statistics.
pub async fn get_crawl_stats(
    State(state): State<Arc<AppState>>,
    Path(crawl_id): Path<String>,
) -> impl IntoResponse {
    match crawl_service::get_crawl_stats(&state.graph, &crawl_id).await {
        Ok(Some(stats)) => (StatusCode::OK, Json(json!(stats))),
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(json!({"error": "Crawl not found"})),
        ),
        Err(e) => {
            tracing::error!("Failed to get stats: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database error"})),
            )
        }
    }
}
