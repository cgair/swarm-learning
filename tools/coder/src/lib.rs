use pyo3::prelude::*;
use port_ethabi::execute;

mod encoder;
mod decoder;

use crate::encoder::{__pyo3_get_function_encode, __pyo3_get_function_encode_many};
use crate::decoder::__pyo3_get_function_decode_many;

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn coder_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode, m)?)?;
    m.add_function(wrap_pyfunction!(encode_many, m)?)?;
    m.add_function(wrap_pyfunction!(decode_many, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
	fn array_encode() {
		let command = "ethabi encode params -v bool[] [1,0,false]".split(' ');
		let expected = "00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000";
		assert_eq!(execute(command).unwrap(), expected);
	}

	#[test]
	fn multi_decode() {
		let command = "ethabi decode params -t bool -t string -t bool 00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000096761766f66796f726b0000000000000000000000000000000000000000000000".split(' ');
		let expected = "bool true
string gavofyork
bool false";
		assert_eq!(execute(command).unwrap(), expected);
	}
}
