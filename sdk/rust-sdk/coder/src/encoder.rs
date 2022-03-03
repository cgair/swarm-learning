//! Encode ethereum ABI params.
use pyo3::prelude::*;
use port_ethabi::{parse_token, encode_single, ParamType};

/// Encode ethereum ABI params.
/// eg. int256, uint256, string, int[], address[5][], etc.
#[pyfunction]
pub fn encode(param_type: &str, value: &str) -> PyResult<String> {
    // we always use lenient tokenize
    let lenient = true;

    let param_tuple = (ParamType::from(param_type), value);
	let tokens = parse_token(&param_tuple, lenient)?;
	let result = encode_single(&tokens);

	Ok(hex::encode(&result))
}
