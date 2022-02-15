mod cluster_resolver;

use anyhow::Result;
use cluster_resolver::tfconfig_cluster_resolver::TfConfig;

#[derive(Debug, Clone)]
pub enum StrategyConfig {
    WithMirroredStrategy(), // TODO
    WithMultiWorkerMirroredStrategy(MultiWorkerMirroredStrategyConfig),
}

#[derive(Debug, Clone)]
pub struct MultiWorkerMirroredStrategyConfig {
    /// Machine learning task type
    pub task_type: String,
    /// Machine learning task id
    pub task_id: String,
    /// Cluster information
    pub cluster: Vec<String>,
}

impl StrategyConfig {
    /// Create `StrategyConfig` for task using given value
    pub fn new_multiwork(task_type: &str, task_id: &str, cluster: Vec<String>) -> Result<Self> {

        let multi_w_config = MultiWorkerMirroredStrategyConfig {
            task_type: task_type.to_string(),
            task_id: task_id.to_string(),
            cluster,
        };

        Ok(Self::WithMultiWorkerMirroredStrategy(multi_w_config))
    }


    /// Crate `StrategyConfig` from Universe Swarm runtime configuration.
    pub fn from_tf_config(config: &TfConfig) -> Result<Self> {
        Self::new_multiwork(&config.task_type, &config.task_id, config.cluster.worker.to_vec())
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        let result = 2 + 2;
        assert_eq!(result, 4);
    }
}
