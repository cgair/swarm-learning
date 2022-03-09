use pyo3::prelude::*;
use port_ethabi::decode_params;

/// Decodes vector of tokens into ABI compliant vector of bytes.
#[pyfunction]
pub fn decode_many(param_type: Vec<String>, data: String) -> PyResult<String> {
	let ret = decode_params(&param_type, &data)?;

	Ok(ret)
}
