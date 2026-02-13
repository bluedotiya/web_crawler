use std::env;

pub struct Config {
    pub neo4j_uri: String,
    pub neo4j_username: String,
    pub neo4j_password: String,
    pub http_timeout_secs: u64,
    pub max_attempts: i64,
    pub max_dns_depth: usize,
    pub sleep_min_secs: u64,
    pub sleep_max_secs: u64,
}

impl Config {
    pub fn from_env() -> Self {
        let dns_name = env::var("NEO4J_DNS_NAME")
            .unwrap_or_else(|_| "neo4j.default.svc.cluster.local:7687".to_string());

        Self {
            neo4j_uri: format!("bolt://{}", dns_name),
            neo4j_username: env::var("NEO4J_USERNAME").unwrap_or_else(|_| "neo4j".to_string()),
            neo4j_password: env::var("NEO4J_PASSWORD").unwrap_or_else(|_| "password".to_string()),
            http_timeout_secs: 1,
            max_attempts: 3,
            max_dns_depth: 5,
            sleep_min_secs: 1,
            sleep_max_secs: 4,
        }
    }
}
