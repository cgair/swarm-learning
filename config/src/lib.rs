mod runtime;
pub use runtime::TfConfig;
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        let conf = r#"{
            "cluster": {
            "worker" : ["localhost:12345", "localhost:23456"]
            }
        }"#;
        let js: serde_json::Value = serde_json::from_str(conf).expect("JSON was not well-formatted");
        assert_eq!(js["cluster"]["worker"][0], "localhost:12345");

        let tf_conf: TfConfig = serde_json::from_str(conf).expect("JSON was not well-formatted");
        if let Some(s) = tf_conf.cluster.worker.get(0) {
            assert_eq!(s, "localhost:12345"); // (*s, "localhost:12345".to_string());
        }
    }
}
