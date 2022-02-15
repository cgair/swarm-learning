use serde::{Serialize, Deserialize};
use anyhow::{Result};
use std::path::Path;
use std::fs::File;
use std::io::BufReader;

#[derive(Serialize, Deserialize, Debug)]
pub struct TfConfig {
    pub task_type: String,
    pub task_id: String,
    pub cluster: Woker,
    pub grpc_server: GrpcServer,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Woker {
    pub worker: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GrpcServer {
    pub ip: String,
    pub port: u16
}

impl TfConfig {
    pub fn from_json<P: AsRef<Path>>(path: P) -> Result<Self> {
        // Open the file in read-only mode with buffer.
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let tf_cong: TfConfig = serde_json::from_reader(reader)?;
        
        Ok(tf_cong)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_config_parse() {
        let path = "../config.json";
        let tf_conf = TfConfig::from_json(path).unwrap(); 
        assert_eq!(tf_conf.task_id, "uuid-001");
        if let Some(sock) = tf_conf.cluster.worker.get(0) {
            assert_eq!(sock, "localhost:12345");    // (*s, "localhost:12345".to_string());
        }
        assert_eq!(tf_conf.grpc_server.ip, "127.0.0.1");
        assert_eq!(tf_conf.grpc_server.port, 50051);
    }
}