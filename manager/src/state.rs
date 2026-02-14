use hickory_resolver::TokioResolver;
use neo4rs::Graph;

use crate::config::Config;

pub struct AppState {
    pub graph: Graph,
    pub client: reqwest::Client,
    pub resolver: TokioResolver,
    pub config: Config,
}
