use ethabi::{
	param_type::ParamType,
	token::{LenientTokenizer, StrictTokenizer, Token, Tokenizer}
};

/// Parse single token, matching with parse_tokens(params: &[(ParamType, &str)], lenient: bool), which parse lots of tokens one-time.
pub fn parse_token(param_tuple: &(ParamType, &str), lenient: bool) -> anyhow::Result<Token> {
    let param = &param_tuple.0;
    let value = param_tuple.1;
    match lenient {
        true => LenientTokenizer::tokenize(param, value),
        false => StrictTokenizer::tokenize(param, value),        
    }
    .map_err(|e| e.into())  // .map_err(From::from)
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
}