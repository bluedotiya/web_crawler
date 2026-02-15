use std::sync::Arc;
use std::time::Duration;

use axum::{
    extract::{
        ws::{Message, WebSocket},
        Path, State, WebSocketUpgrade,
    },
    response::IntoResponse,
};
use serde_json::json;

use crate::services::crawl_service;
use crate::state::AppState;

/// GET /api/v1/crawls/:id/ws — WebSocket for real-time progress updates.
pub async fn crawl_ws(
    ws: WebSocketUpgrade,
    State(state): State<Arc<AppState>>,
    Path(crawl_id): Path<String>,
) -> impl IntoResponse {
    ws.on_upgrade(move |socket| handle_socket(socket, state, crawl_id))
}

async fn handle_socket(mut socket: WebSocket, state: Arc<AppState>, crawl_id: String) {
    loop {
        tokio::time::sleep(Duration::from_secs(2)).await;

        let progress = match crawl_service::get_crawl_progress(&state.graph, &crawl_id).await {
            Ok(Some(p)) => p,
            Ok(None) => {
                let msg = json!({"error": "Crawl not found"}).to_string();
                let _ = socket.send(Message::Text(msg.into())).await;
                break;
            }
            Err(e) => {
                tracing::error!("WebSocket progress query failed: {}", e);
                break;
            }
        };

        let is_complete = progress.status == "completed" || progress.status == "cancelled";
        let msg = serde_json::to_string(&progress).unwrap_or_default();

        if socket.send(Message::Text(msg.into())).await.is_err() {
            break; // Client disconnected
        }

        if is_complete {
            break; // Crawl done, close socket
        }
    }
}
