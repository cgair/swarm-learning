//! Encode ethereum ABI params.
use pyo3::prelude::*;
use itertools::Itertools;
use port_ethabi::{
	parse_token, parse_tokens,
	encode_single, encode_some, 
	ParamType
};

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

/// Encodes vector of tokens into ABI compliant vector of bytes.
#[pyfunction]
pub fn encode_many(params: Vec<String>) -> PyResult<String> {
	assert_eq!(params.len() % 2, 0);
    // we always use lenient tokenize
    let lenient = true;

	let params = params
		.iter()
		.tuples::<(_, _)>()
        .map(|(t, v)| (ParamType::from(t.as_str()), v.as_str()))
		.collect::<Vec<(ParamType, &str)>>();

	let tokens = parse_tokens(params.as_slice(), lenient)?;
	let result = encode_some(&tokens);

	Ok(hex::encode(&result))
}