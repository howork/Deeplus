//! Deterministic bounded lexer projection for SFD-P1-009 contract inputs.

use deeplus_diagnostics::sfd_p1_009::CandidateDiagnostic;
use deeplus_source::sfd_p1_009::SourceCase;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Token {
    pub text: String,
    pub start: usize,
    pub end: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LexedCase {
    pub source: SourceCase,
    pub tokens: Vec<Token>,
}

pub fn lex(source: SourceCase) -> Result<LexedCase, CandidateDiagnostic> {
    let text = source.utf8().map_err(|error| {
        CandidateDiagnostic::structural("SFD009-CONTRACT-UTF8", error.to_string())
    })?;
    let mut tokens = Vec::new();
    let mut start = None;
    for (index, character) in text.char_indices() {
        let separator = character.is_whitespace() || "{}[]():,;".contains(character);
        if separator {
            if let Some(token_start) = start.take() {
                tokens.push(Token {
                    text: text[token_start..index].to_owned(),
                    start: token_start,
                    end: index,
                });
            }
            if !character.is_whitespace() {
                let end = index + character.len_utf8();
                tokens.push(Token {
                    text: text[index..end].to_owned(),
                    start: index,
                    end,
                });
            }
        } else if start.is_none() {
            start = Some(index);
        }
    }
    if let Some(token_start) = start {
        tokens.push(Token {
            text: text[token_start..].to_owned(),
            start: token_start,
            end: text.len(),
        });
    }
    Ok(LexedCase { source, tokens })
}
