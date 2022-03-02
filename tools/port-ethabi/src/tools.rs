//! Utils used by different modules.

use ethabi::Word; 	// pub type Word = [u8; 32];

/// Converts a u32 to a right aligned array of 32 bytes.
pub fn pad_u32(value: u32) -> Word {
	let mut padded = [0u8; 32];
	padded[28..32].copy_from_slice(&value.to_be_bytes());
	padded
}

#[cfg(test)]
mod tests {
	use super::pad_u32;
	use hex_literal::hex;

	#[test]
	fn test_pad_u32() {
		// this will fail if endianness is not supported
		assert_eq!(
			pad_u32(0).to_vec(),
			hex!("0000000000000000000000000000000000000000000000000000000000000000").to_vec()
		);
		assert_eq!(
			pad_u32(1).to_vec(),
			hex!("0000000000000000000000000000000000000000000000000000000000000001").to_vec()
		);
		assert_eq!(
			pad_u32(0x100).to_vec(),
			hex!("0000000000000000000000000000000000000000000000000000000000000100").to_vec()
		);
		assert_eq!(
			pad_u32(0xffffffff).to_vec(),
			hex!("00000000000000000000000000000000000000000000000000000000ffffffff").to_vec()
		);
	}
}
