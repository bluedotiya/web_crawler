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

    let root_row = match check.next().await? {
        Some(row) => row,
        None => return Ok(None),
    };

    let root_node: neo4rs::Node = root_row.get("r")?;
    let root_name: String = root_node.get("name")?;
    let root_http: String = root_node.get("http_type")?;
    let root_domain: String = root_node.get("domain").unwrap_or_default();
    let _root_depth: i64 = root_node.get("requested_depth")?;

    let root_id = format!("{}{}", root_http, root_name);
    let mut seen = HashMap::new();
    seen.insert(
        root_id.clone(),
        GraphNode {
            id: root_id,
            label: root_name.clone(),
            domain: root_domain,
            depth: 0,
            status: "root".to_string(),
            node_type: "ROOT".to_string(),
        },
    );

    let mut edges = Vec::new();

    // Get all URL nodes and relationships for this crawl
    let mut result = graph
        .execute(
            query(
                "MATCH (parent)-[:Lead]->(child:URL {crawl_id: $crawl_id}) \
                 RETURN parent.name AS parent_name, parent.http_type AS parent_http, \
                   child.name AS name, child.http_type AS http_type, \
                   child.domain AS domain, child.current_depth AS depth, \
                   child.job_status AS status \
                 ORDER BY child.current_depth",
            )
            .param("crawl_id", crawl_id),
        )
        .await?;

    while let Some(row) = result.next().await? {
        let name: String = row.get("name")?;
        let http_type: String = row.get("http_type")?;
        let domain: String = row.get("domain").unwrap_or_default();
        let depth: i64 = row.get("depth")?;
        let status: String = row.get("status").unwrap_or_default();
        let parent_name: String = row.get("parent_name")?;
        let parent_http: String = row.get("parent_http").unwrap_or_default();

        let node_id = format!("{}{}", http_type, name);
        let parent_id = format!("{}{}", parent_http, parent_name);

        seen.entry(node_id.clone()).or_insert_with(|| GraphNode {
            id: node_id.clone(),
            label: name,
            domain,
            depth,
            status,
            node_type: "URL".to_string(),
        });

        edges.push(GraphEdge {
            source: parent_id,
            target: node_id,
        });
    }

    let nodes: Vec<GraphNode> = seen.into_values().collect();
    Ok(Some(GraphData { nodes, edges }))
}
