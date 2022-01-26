use std::net::{IpAddr, SocketAddr};
use tonic::{transport::Server, Request, Response, Status};
use config::TfConfig;
use tokio::runtime::Runtime;
// use anyhow::{Result, Context};

pub mod proto;
use proto::{ControlRequest, ControlResponse, SwarmNodeControl, SwarmNodeControlServer};

const CONFIG_PATH: &str = "../config.json";

#[derive(Default)]
pub struct CustomServer {}

#[tonic::async_trait]
impl SwarmNodeControl for CustomServer {
    async fn node_control(
        &self,
        request: Request<ControlRequest>
    ) -> Result<Response<ControlResponse>, Status> {
        log::debug!("Got a request from {:?}", request.remote_addr());
        log::trace!("Request: {:?}", request);

        let reply = ControlResponse {
            accept: true,
        };

        Ok(Response::new(reply))
    }
}

// Change to blocking server
pub fn run() {
    // Init logger
    env_logger::init_from_env(
        env_logger::Env::new()
        .filter_or("GRPC_LOG", "RUST_LOG")
        .write_style_or("GRPC_LOG_STYLE", "RUST_LOG_STYLE"),
    );

    let tf_conf = TfConfig::from_json(CONFIG_PATH).unwrap();
    let addr: IpAddr = tf_conf.grpc_server.ip.parse().expect("Ipv4Addr");
    let port = tf_conf.grpc_server.port;
    let socket = SocketAddr::new(addr, port);
    log::info!("GrpcServer listening on {}", socket.to_string());

    let cutomserver = CustomServer::default();

    let rt = Runtime::new().expect("failed to obtain a new RunTime object");
    let server_future = Server::builder()
                        .add_service(SwarmNodeControlServer::new(cutomserver))
                        .serve(socket);
    log::info!("Blocking Server...");
    rt.block_on(server_future).expect("failed to successfully run the future on RunTime");
}

// #[tokio::main]
// pub async fn run() -> Result<(), Box<dyn std::error::Error>>{
//     // Init logger
//     env_logger::init_from_env(
//         env_logger::Env::new()
//         .filter_or("GRPC_LOG", "RUST_LOG")
//         .write_style_or("GRPC_LOG_STYLE", "RUST_LOG_STYLE"),
//     );

//     let tf_conf = TfConfig::from_json(CONFIG_PATH).unwrap();
//     let addr: IpAddr = tf_conf.grpc_server.ip.parse().expect("Ipv4Addr");
//     let port = tf_conf.grpc_server.port;
//     let socket = SocketAddr::new(addr, port);

//     let cutomserver = CustomServer::default();
//     Server::builder()
//         .add_service(SwarmNodeControlServer::new(cutomserver))
//         .serve(socket)
//         .await?;

//     Ok(())
// }
