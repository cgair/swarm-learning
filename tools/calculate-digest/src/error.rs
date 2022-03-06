#[derive(Debug)]
pub enum Error {
   IO(std::io::Error),
   BadPrivateKey,
   OOM,
   BadSignature,
}
