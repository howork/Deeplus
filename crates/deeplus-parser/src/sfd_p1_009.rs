//! Root-connected bounded parser projection.

use deeplus_diagnostics::sfd_p1_009::CandidateDiagnostic;
use deeplus_lexer::sfd_p1_009::LexedCase;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ParsedCase {
    pub lexed: LexedCase,
    pub root_kind: &'static str,
}

pub fn parse(lexed: LexedCase) -> Result<ParsedCase, CandidateDiagnostic> {
    if lexed.tokens.is_empty() {
        return Err(CandidateDiagnostic::structural(
            "SFD009-CONTRACT-EMPTY",
            "bounded input must contain a root-connected payload",
        ));
    }
    Ok(ParsedCase {
        lexed,
        root_kind: "SFD_P1_009_CONTRACT_ROOT",
    })
}
