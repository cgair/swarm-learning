use ethabi::{
	param_type::ParamType,
	token::{LenientTokenizer, StrictTokenizer, Token, Tokenizer}
};

/// Parse single token
pub fn parse_token(param_tuple: &(ParamType, &str), lenient: bool) -> anyhow::Result<Token> {
    let param = &param_tuple.0;
    let value = param_tuple.1;
    match lenient {
        true => LenientTokenizer::tokenize(param, value),
        false => StrictTokenizer::tokenize(param, value),        
    }
    .map_err(|e| e.into())
}

/// Parse lots of tokens one-time.
pub fn parse_tokens(params: &[(ParamType, &str)], lenient: bool) -> anyhow::Result<Vec<Token>> {
	params
		.iter()
		.map(|&(ref param, value)| match lenient {
			true => LenientTokenizer::tokenize(param, value),
			false => StrictTokenizer::tokenize(param, value),
		})
		.collect::<Result<_, _>>()
		.map_err(From::from)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_singel_token() {
        let param_tuple = (ParamType::Bool, "1");
		let expected = Token::Bool(true);
		assert_eq!(parse_token(&param_tuple, true).unwrap(), expected);
    }

    #[test]
    fn parse_some_tokens() {
        let mut param_vec = vec![];
        let param_tuple0 = (ParamType::Bool, "1");
        let param_tuple1 = (ParamType::String, "test");
        param_vec.push(param_tuple0);
        param_vec.push(param_tuple1);
		let expected = vec![Token::Bool(true), Token::String("test".to_string())];
		assert_eq!(parse_tokens(&param_vec, true).unwrap(), expected);
    }
}