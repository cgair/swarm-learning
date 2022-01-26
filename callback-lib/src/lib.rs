use pyo3::prelude::*;
use grpc_server::run;

/// Run the grpc server.
#[pyfunction]
fn run_grpc_server() -> PyResult<()> {
    run();
    Ok(())
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn callback_api(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_grpc_server, m)?)?;

    Ok(())
}
