use serde::{Serialize, Deserialize};
use anyhow::{Result};
use std::path::Path;
use std::fs::File;
use std::io::BufReader;

#[derive(Serialize, Deserialize, Debug)]
pub struct TfConfig {
    pub cluster: Woker
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Woker {
    pub worker: Vec<String>,
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
        if let Some(sock) = tf_conf.cluster.worker.get(0) {
            assert_eq!(sock, "localhost:12345");
        }
    }
}