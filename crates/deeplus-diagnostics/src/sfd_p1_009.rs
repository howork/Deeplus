//! Candidate-local diagnostic identity. Nothing here registers a canonical diagnostic.

use deeplus_source::sfd_p1_009::ByteSpan;
use std::fmt;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DiagnosticNote {
    pub order: u32,
    pub role: String,
    pub text: String,
    pub span: Option<ByteSpan>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CandidateDiagnostic {
    pub code: String,
    pub logical_family: String,
    pub stage_rank: u8,
    pub primary_span: Option<ByteSpan>,
    pub notes: Vec<DiagnosticNote>,
    pub suppressed_stages: Vec<u8>,
    pub fallback_attempt_count: u32,
}

impl CandidateDiagnostic {
    pub fn structural(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            logical_family: message.into(),
            stage_rank: 1,
            primary_span: None,
            notes: Vec::new(),
            suppressed_stages: (2..=8).collect(),
            fallback_attempt_count: 0,
        }
    }
}

impl fmt::Display for CandidateDiagnostic {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}: {}", self.code, self.logical_family)
    }
}

impl std::error::Error for CandidateDiagnostic {}
