use std::collections::HashMap;

use neo4rs::{query, Graph};

use crate::models::graph::{GraphData, GraphEdge, GraphNode};

/// Retrieve the full graph structure for a crawl (unique nodes + edges).
pub async fn get_graph_data(
    graph: &Graph,
    crawl_id: &str,
) -> Result<Option<GraphData>, anyhow::Error> {
    // Verify crawl exists
    let mut check = graph
        .execute(
            query("MATCH (r:ROOT {crawl_id: $crawl_id}) RETURN r LIMIT 1")
                .param("crawl_id", crawl_id),
        )
        .await?;

    if check.next().await?.is_none() {
        return Ok(None);
    }

    let mut seen = HashMap::new();

    // Get the ROOT node
    let mut root_result = graph
        .execute(
            query(
                "MATCH (r:ROOT {crawl_id: $crawl_id}) \
                 RETURN r.http_type + r.name AS id, r.name AS name, \
                   r.domain AS domain, 0 AS depth, 'root' AS status, 'ROOT' AS node_type",
            )
            .param("crawl_id", crawl_id),
        )
        .await?;

    while let Some(row) = root_result.next().await? {
        let id: String = row.get("id")?;
        let name: String = row.get("name")?;
        let domain: String = row.get("domain").unwrap_or_default();
        seen.insert(
            id.clone(),
            GraphNode {
                id,
                label: name,
                domain,
                depth: 0,
                status: "root".to_string(),
                node_type: "ROOT".to_string(),
            },
        );
    }

    // Get all URL nodes for this crawl
    let mut nodes_result = graph
        .execute(
            query(
                "MATCH (u:URL {crawl_id: $crawl_id}) \
                 RETURN u.http_type + u.name AS id, u.name AS name, \
                   u.domain AS domain, u.current_depth AS depth, \
                   u.job_status AS status",
            )
            .param("crawl_id", crawl_id),
        )
        .await?;

    while let Some(row) = nodes_result.next().await? {
        let id: String = row.get("id")?;
        let name: String = row.get("name")?;
        let domain: String = row.get("domain").unwrap_or_default();
        let depth: i64 = row.get("depth")?;
        let status: String = row.get("status").unwrap_or_default();

        seen.entry(id.clone()).or_insert_with(|| GraphNode {
            id,
            label: name,
            domain,
            depth,
            status,
            node_type: "URL".to_string(),
        });
    }

    // Get all Lead edges for this crawl
    let mut edges = Vec::new();
    let mut edges_result = graph
        .execute(
            query(
                "MATCH (parent)-[:Lead]->(child:URL {crawl_id: $crawl_id}) \
                 RETURN parent.http_type + parent.name AS parent_id, \
                   child.http_type + child.name AS child_id",
            )
            .param("crawl_id", crawl_id),
        )
        .await?;

    while let Some(row) = edges_result.next().await? {
        let parent_id: String = row.get("parent_id")?;
        let child_id: String = row.get("child_id")?;

        edges.push(GraphEdge {
            source: parent_id,
            target: child_id,
        });
    }

    let nodes: Vec<GraphNode> = seen.into_values().collect();
    Ok(Some(GraphData { nodes, edges }))
}
