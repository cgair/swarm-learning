//! Encode ethereum ABI params.
use pyo3::prelude::*;
use port_ethabi::{parse_token, encode_single, ParamType};

/// Encode array of params with unknown size.
/// eg. int[], bool[], address[5][]
#[pyfunction]
pub fn encode_array(param_type: &str, value: &str) -> PyResult<String> {
    // we always use lenient tokenize
    let lenient = true;

    let param_tuple = (ParamType::from(param_type), value);
	let tokens = parse_token(&param_tuple, lenient)?;
	let result = encode_single(&tokens);

	Ok(hex::encode(&result))
}
