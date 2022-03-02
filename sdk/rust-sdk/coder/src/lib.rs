use pyo3::prelude::*;
use port_ethabi::execute;

mod encoder;
mod decoder;

use crate::encoder::__pyo3_get_function_encode_array;

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn coder_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encode_array, m)?)?;

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
}
