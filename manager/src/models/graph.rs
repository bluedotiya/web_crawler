use serde::Serialize;

#[derive(Serialize)]
pub struct GraphNode {
    pub id: String,
    pub label: String,
    pub domain: String,
    pub depth: i64,
    pub status: String,
    pub node_type: String,
}

#[derive(Serialize)]
pub struct GraphEdge {
    pub source: String,
    pub target: String,
}

#[derive(Serialize)]
pub struct GraphData {
    pub nodes: Vec<GraphNode>,
    pub edges: Vec<GraphEdge>,
}
