//! ABI encoder.
// most of the code is borrowed from https://github.com/rust-ethereum/ethabi/blob/master/ethabi/src/encoder.rs
use crate::tools::pad_u32;

use ethabi::{
    Word,
    token::Token,
};

fn pad_bytes(bytes: &[u8]) -> Vec<Word> {
	let mut result = vec![pad_u32(bytes.len() as u32)];
	result.extend(pad_fixed_bytes(bytes));
	result
}

fn pad_fixed_bytes(bytes: &[u8]) -> Vec<Word> {
	let len = (bytes.len() + 31) / 32;
	let mut result = Vec::with_capacity(len);
	for i in 0..len {
		let mut padded = [0u8; 32];

		let to_copy = match i == len - 1 {
			false => 32,
			true => match bytes.len() % 32 {
				0 => 32,
				x => x,
			},
		};

		let offset = 32 * i;
		padded[..to_copy].copy_from_slice(&bytes[offset..offset + to_copy]);
		result.push(padded);
	}

	result
}

#[derive(Debug)]
enum Mediate {
	Raw(Vec<Word>),
	Prefixed(Vec<Word>),
	PrefixedArray(Vec<Mediate>),
	PrefixedArrayWithLength(Vec<Mediate>),
	RawTuple(Vec<Mediate>),
	PrefixedTuple(Vec<Mediate>),
}

impl Mediate {
	fn head_len(&self) -> u32 {
		match *self {
			Mediate::Raw(ref raw) => 32 * raw.len() as u32,
			Mediate::RawTuple(ref mediates) => mediates.iter().map(|mediate| mediate.head_len()).sum(),
			Mediate::Prefixed(_)
			| Mediate::PrefixedArray(_)
			| Mediate::PrefixedArrayWithLength(_)
			| Mediate::PrefixedTuple(_) => 32,
		}
	}

	fn tail_len(&self) -> u32 {
		match *self {
			Mediate::Raw(_) | Mediate::RawTuple(_) => 0,
			Mediate::Prefixed(ref pre) => pre.len() as u32 * 32,
			Mediate::PrefixedArray(ref mediates) => mediates.iter().fold(0, |acc, m| acc + m.head_len() + m.tail_len()),
			Mediate::PrefixedArrayWithLength(ref mediates) => {
				mediates.iter().fold(32, |acc, m| acc + m.head_len() + m.tail_len())
			}
			Mediate::PrefixedTuple(ref mediates) => mediates.iter().fold(0, |acc, m| acc + m.head_len() + m.tail_len()),
		}
	}

	fn head(&self, suffix_offset: u32) -> Vec<Word> {
		match *self {
			Mediate::Raw(ref raw) => raw.clone(),
			Mediate::RawTuple(ref raw) => raw.iter().map(|mediate| mediate.head(0)).flatten().collect(),
			Mediate::Prefixed(_)
			| Mediate::PrefixedArray(_)
			| Mediate::PrefixedArrayWithLength(_)
			| Mediate::PrefixedTuple(_) => vec![pad_u32(suffix_offset)],
		}
	}

	fn tail(&self) -> Vec<Word> {
		match *self {
			Mediate::Raw(_) | Mediate::RawTuple(_) => vec![],
			Mediate::PrefixedTuple(ref mediates) => encode_head_tail(mediates),
			Mediate::Prefixed(ref raw) => raw.clone(),
			Mediate::PrefixedArray(ref mediates) => encode_head_tail(mediates),
			Mediate::PrefixedArrayWithLength(ref mediates) => {
				// + 32 added to offset represents len of the array prepanded to tail
				let mut result = vec![pad_u32(mediates.len() as u32)];

				let head_tail = encode_head_tail(mediates);

				result.extend(head_tail);
				result
			}
		}
	}
}

fn encode_head_tail(mediates: &[Mediate]) -> Vec<Word> {
	let heads_len = mediates.iter().fold(0, |acc, m| acc + m.head_len());

	let (mut result, len) =
		mediates.iter().fold((Vec::with_capacity(heads_len as usize), heads_len), |(mut acc, offset), m| {
			acc.extend(m.head(offset));
			(acc, offset + m.tail_len())
		});

	let tails = mediates.iter().fold(Vec::with_capacity((len - heads_len) as usize), |mut acc, m| {
		acc.extend(m.tail());
		acc
	});

	result.extend(tails);
	result
}

/// Encodes single token into ABI compliant vector of bytes.
pub fn encode(token: &Token) -> Vec<u8> {
	let mediate = encode_token(&token);
    let mediates = vec![mediate];   // TODO: FIXME
	encode_head_tail(&mediates).iter().flat_map(|word| word.to_vec()).collect()
}

fn encode_token(token: &Token) -> Mediate {
	match *token {
		Token::Address(ref address) => {
			let mut padded = [0u8; 32];
			padded[12..].copy_from_slice(address.as_ref());
			Mediate::Raw(vec![padded])
		}
		Token::Bytes(ref bytes) => Mediate::Prefixed(pad_bytes(bytes)),
		Token::String(ref s) => Mediate::Prefixed(pad_bytes(s.as_bytes())),
		Token::FixedBytes(ref bytes) => Mediate::Raw(pad_fixed_bytes(bytes)),
		Token::Int(int) => Mediate::Raw(vec![int.into()]),
		Token::Uint(uint) => Mediate::Raw(vec![uint.into()]),
		Token::Bool(b) => {
			let mut value = [0u8; 32];
			if b {
				value[31] = 1;
			}
			Mediate::Raw(vec![value])
		}
		Token::Array(ref tokens) => {
			let mediates = tokens.iter().map(encode_token).collect();

			Mediate::PrefixedArrayWithLength(mediates)
		}
		Token::FixedArray(ref tokens) => {
			let mediates = tokens.iter().map(encode_token).collect();

			if token.is_dynamic() {
				Mediate::PrefixedArray(mediates)
			} else {
				Mediate::Raw(encode_head_tail(&mediates))
			}
		}
		Token::Tuple(ref tokens) if token.is_dynamic() => {
			let mediates = tokens.iter().map(encode_token).collect();

			Mediate::PrefixedTuple(mediates)
		}
		Token::Tuple(ref tokens) => {
			let mediates = tokens.iter().map(encode_token).collect();

			Mediate::RawTuple(mediates)
		}
	}
}

#[cfg(test)]
mod tests {
	use hex_literal::hex;
    use super::*;
	#[test]
	fn encode_address() {
		let address = Token::Address([0x11u8; 20].into());
		let encoded = encode(&address);
		let expected = hex!("0000000000000000000000001111111111111111111111111111111111111111");
		assert_eq!(encoded, expected);
	}

	#[test]
	fn encode_dynamic_array_of_addresses() {
		let address1 = Token::Address([0x11u8; 20].into());
		let address2 = Token::Address([0x22u8; 20].into());
		let addresses = Token::Array(vec![address1, address2]);
		let encoded = encode(&addresses);
		let expected = hex!(
			"
			0000000000000000000000000000000000000000000000000000000000000020
			0000000000000000000000000000000000000000000000000000000000000002
			0000000000000000000000001111111111111111111111111111111111111111
			0000000000000000000000002222222222222222222222222222222222222222
		"
		)
		.to_vec();
		assert_eq!(encoded, expected);
	}

	#[test]
	fn encode_fixed_array_of_addresses() {
		let address1 = Token::Address([0x11u8; 20].into());
		let address2 = Token::Address([0x22u8; 20].into());
		let addresses = Token::FixedArray(vec![address1, address2]);
		let encoded = encode(&addresses);
		let expected = hex!(
			"
			0000000000000000000000001111111111111111111111111111111111111111
			0000000000000000000000002222222222222222222222222222222222222222
		"
		)
		.to_vec();
		assert_eq!(encoded, expected);
	}

	#[test]
	fn encode_dynamic_array_of_dynamic_arrays() {
		let address1 = Token::Address([0x11u8; 20].into());
		let address2 = Token::Address([0x22u8; 20].into());
		let array0 = Token::Array(vec![address1]);
		let array1 = Token::Array(vec![address2]);
		let dynamic = Token::Array(vec![array0, array1]);
		let encoded = encode(&dynamic);
		let expected = hex!(
			"
			0000000000000000000000000000000000000000000000000000000000000020
			0000000000000000000000000000000000000000000000000000000000000002
			0000000000000000000000000000000000000000000000000000000000000040
			0000000000000000000000000000000000000000000000000000000000000080
			0000000000000000000000000000000000000000000000000000000000000001
			0000000000000000000000001111111111111111111111111111111111111111
			0000000000000000000000000000000000000000000000000000000000000001
			0000000000000000000000002222222222222222222222222222222222222222
		"
		)
		.to_vec();
		assert_eq!(encoded, expected);
	}

	#[test]
	fn encode_dynamic_array_of_dynamic_arrays2() {
		let address1 = Token::Address([0x11u8; 20].into());
		let address2 = Token::Address([0x22u8; 20].into());
		let address3 = Token::Address([0x33u8; 20].into());
		let address4 = Token::Address([0x44u8; 20].into());
		let array0 = Token::Array(vec![address1, address2]);
		let array1 = Token::Array(vec![address3, address4]);
		let dynamic = Token::Array(vec![array0, array1]);
		let encoded = encode(&dynamic);
		let expected = hex!(
			"
			0000000000000000000000000000000000000000000000000000000000000020
			0000000000000000000000000000000000000000000000000000000000000002
			0000000000000000000000000000000000000000000000000000000000000040
			00000000000000000000000000000000000000000000000000000000000000a0
			0000000000000000000000000000000000000000000000000000000000000002
			0000000000000000000000001111111111111111111111111111111111111111
			0000000000000000000000002222222222222222222222222222222222222222
			0000000000000000000000000000000000000000000000000000000000000002
			0000000000000000000000003333333333333333333333333333333333333333
			0000000000000000000000004444444444444444444444444444444444444444
		"
		)
		.to_vec();
		assert_eq!(encoded, expected);
	}
}