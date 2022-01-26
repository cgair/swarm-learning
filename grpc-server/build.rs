fn main() -> Result<(), Box<dyn std::error::Error>> {
    let files = &["src/proto/swarm_control_service.proto"];

    tonic_build::compile_protos("src/proto/swarm_control_service.proto")?;

    // recompile protobufs only if any of the proto files changes.
    for file in files {
        println!("cargo:rerun-if-changed={}", file);
    }

    Ok(())
}