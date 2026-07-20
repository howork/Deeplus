//! Typed AST facade for the bounded SFD-P1-009 root.

use deeplus_parser::sfd_p1_009::ParsedCase;
use deeplus_source::sfd_p1_009::IngressPhase;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AstCase {
    pub oracle_id: String,
    pub subfixture_id: String,
    pub ingress_phase: IngressPhase,
    pub selected_mode: String,
    pub token_count: usize,
}

pub fn lower(parsed: ParsedCase) -> AstCase {
    AstCase {
        oracle_id: parsed.lexed.source.oracle_id,
        subfixture_id: parsed.lexed.source.subfixture_id,
        ingress_phase: parsed.lexed.source.ingress_phase,
        selected_mode: parsed.lexed.source.selected_mode,
        token_count: parsed.lexed.tokens.len(),
    }
}
