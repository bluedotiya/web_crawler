use thiserror::Error;

#[derive(Error, Debug)]
pub enum FeederError {
    #[error("Neo4j connection failed: {0}")]
    Neo4jConnection(#[from] neo4rs::Error),

    #[error("DNS resolution failed for {domain} after {attempts} attempts")]
    DnsResolution { domain: String, attempts: u32 },
}
