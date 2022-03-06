use ring::digest;
use openssl::{
    base64, 
    rsa::{Padding, Rsa}, 
    x509::X509}
    ;

const CERT: &str = r#"-----BEGIN CERTIFICATE-----
MIIEYDCCA0igAwIBAgIIW0FOUNCBSHEwDQYJKoZIhvcNAQELBQAwdzEkMCIGA1UE
Awwbcm9vdC5iYWFzLmNvbmZsdXgtY2hhaW4ub3JnMRAwDgYDVQQLDAdpdC1kZXB0
MRYwFAYDVQQKDA1jb25mbHV4LWNoYWluMQswCQYDVQQHDAJTSDELMAkGA1UECAwC
U0gxCzAJBgNVBAYTAkNOMB4XDTIyMDIwODEwMjgzM1oXDTI3MDIwNzEwMjgzM1ow
eDEqMCgGA1UEAwwhY29uc29ydGl1bS5iYWFzLmNvbmZsdXgtY2hhaW4ub3JnMQsw
CQYDVQQLDAJyZDEWMBQGA1UECgwNY29uZmx1eC1jaGFpbjELMAkGA1UEBwwCU0gx
CzAJBgNVBAgMAlNIMQswCQYDVQQGEwJDTjCCASIwDQYJKoZIhvcNAQEBBQADggEP
ADCCAQoCggEBAKfUJq33oEkxXK1Z7iundG44XbAFq3+PBOywsEBeQtK0ydiiHrlN
MmU6oqLKKlqw5B9B0SV2TUdmzpAjU8f59IUzcbdfT5VhBOoe6NPbZH32KBcEQOkz
HMQDPhgMi56iDTIafBFIWG9y2ylF61jIA17rSkvux6XjPbmHCJLcOwd0Cnk1JCcR
Y5FmP/VzCoaO/dnHadqmk0fSwG6gifPaqC8ybnpVVKBb/d8tvmW/dG9wqHmrLybT
VW8eDeGtLg+b5SpartlruT056rGq/NDgl4K+B0M3Ho1UnOlU9WpGKdtiRigOF4w7
mq3802g8T+uoQn6qp7zz43Wp4e8UIllKuIcCAwEAAaOB7jCB6zAPBgNVHRMBAf8E
BTADAQH/MA4GA1UdDwEB/wQEAwIChDCBqAYDVR0jBIGgMIGdgBSfMhXaiPc1Tumv
qEgB8E+rk3mtdqF7pHkwdzEkMCIGA1UEAwwbcm9vdC5iYWFzLmNvbmZsdXgtY2hh
aW4ub3JnMRAwDgYDVQQLDAdpdC1kZXB0MRYwFAYDVQQKDA1jb25mbHV4LWNoYWlu
MQswCQYDVQQHDAJTSDELMAkGA1UECAwCU0gxCzAJBgNVBAYTAkNOgghdgPkyoYJN
+zAdBgNVHQ4EFgQUaIK9SYFvIGj0Vqpb+qvEK/q7Ng4wDQYJKoZIhvcNAQELBQAD
ggEBAAobQEIyueeU+wOglyP73EJ2zgEcqs3wkLJfKVqaxq41Oluf9/XTpe3amuSR
9DBbhxK+2eQlG/uLYj3u8lJvwiufmh8F9cayiFeyVZw6JEiZg1e8Sw+jggHArEFg
8uFPkI54a9QupBg3C0ogT8lTDElBE/GXj9mnKmOdtIIroONo1v9koYNC0gpaPUg2
WV7EZJOMZi34UQVz71XOnyAa2yYiQVkCaHTrjHzYrw/1fZKCEtQBVVIlWuBLfB1Q
1wCzwNXY/sK5c0wwO8Ow0Wvsrda4/CFDcIHcc62TtQAixFIsnSZuOCguRhTukpSX
zZzPQ78IxUpTX7jATtH2+lb0tjk=
-----END CERTIFICATE-----"#;

fn main() {
    let mut bytes = [0u8; 32];
    let data = "a2e9d2183a48c9c456bd3e3251280b99eea738e41a391561a71e93ac3ddfdd26";
    hex::decode_to_slice(data, &mut bytes).unwrap();
    println!("{:?}", bytes);

    // 
    let intermediate_ca =
        match X509::from_pem(CERT.as_bytes()) {
            Ok(x509_content) => x509_content,
            Err(e) => {
                panic!("BaaS Certificate invalid format:{:?}", e);
            }
        };
    let consortium_rsa_pub =
        intermediate_ca.public_key().unwrap().rsa().unwrap();
    let mut text: Vec<u8> = vec![
        0;
        String::from_utf8(
            intermediate_ca
                .public_key()
                .unwrap()
                .rsa()
                .unwrap()
                .public_key_to_pem()
                .unwrap()
        )
        .unwrap()
        .len()
    ];
    let consortium_nodes_digest = "gfjgodyeUBM5JK4ZMrEb6G0Yd/F0dMg3BNuIHx5EKJoqFy/bv2QOK1cF13NWqHFbf7nN6PMXbbcvyp3Rm96IOHrlS/xDjdPqhwEmS+w/mqc4JdY7idGV6Pbdl8xZDGX0eu//vtjKGFlyb8ljyJNtFkE/wwvWlMSXJPJFOjNKDITKEmf/nBvRBUMivyvYuNteorZXCtN6vw66AMcFSQTz5Hfm9ijE2P9WbpFtknujXnTRTEfaQJjOXiDuK7NN6pqZI1tNoBjTeOvCepqeUoZTKeYjlBs0Y7WseMfUTPEaIp8sjcnhwxU46w0/vG50w/Mi7KW7jkmO9azfgFAspfg6Mg==";
    consortium_rsa_pub
        .public_decrypt(
            &base64::decode_block(&consortium_nodes_digest).unwrap(),
            &mut text,
            Padding::PKCS1,
        )
        .unwrap();
    let message = "cfxnode://465d54a08d967abb7714d2a2d9f1c7a50fc318f1a4cf03b1e1009008fbb99b5e1548cbb021c0e2210c6619b607eca73275476112b7a7ecb4bf02a948e6afed29@192.168.1.102:39000,cfxnode://9d34bc2f6a11f3fa0b000d9bf1b2db3bb5c6335cbf5b23de5b598dea839cbdc8e97f79f485c56b5d9734455437488969d3a361dbc9b7408625d615cfbfbbdbff@192.168.1.242:39000,cfxnode://d677514750fb3de6e79cf5a8a78165868deee8c7ef8a2da3af2426518b09229a64e4fae1c8bf2e85937aa13ab668c0af4c565debaf32b155e577bc5f01313db6@192.168.1.21:39000,cfxnode://29cae59ca8d7c50da2f8e5ad07180439a40552541338c4876edf43e41e0174eaee9b3159bc0bffe0f8ce2c4dc4e312471a5f35c56125420a1da021ad17bc3e61@192.168.1.31:39000";

    let d = digest::digest(&digest::SHA256, message.as_bytes());
    let d = hex::decode("6d0799ff5a5165ed1699b4e8324f450e72ebb4981f9872733f2f2e067a14c50b").unwrap();
    println!("{:?}", d);
    text.truncate(d.len());
    println!("{:?}", text);
    assert_eq!(d, text);

}