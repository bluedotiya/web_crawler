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

fn required_env(key: &str) -> String {
    env::var(key).unwrap_or_else(|_| panic!("{} must be set", key))
}

fn env_or<T: std::str::FromStr>(key: &str, default: T) -> T {
    env::var(key)
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(default)
}

impl Config {
    pub fn from_env() -> Self {
        Self {
            neo4j_uri: format!("bolt://{}", required_env("NEO4J_DNS_NAME")),
            neo4j_username: required_env("NEO4J_USERNAME"),
            neo4j_password: required_env("NEO4J_PASSWORD"),
            http_timeout_secs: env_or("HTTP_TIMEOUT_SECS", 10),
            max_attempts: env_or("MAX_ATTEMPTS", 3),
            max_dns_depth: env_or("MAX_DNS_DEPTH", 5),
            sleep_min_secs: env_or("SLEEP_MIN_SECS", 1),
            sleep_max_secs: env_or("SLEEP_MAX_SECS", 4),
        }
    }
}
