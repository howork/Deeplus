//! Bounded source identity used only by the noncanonical SFD-P1-009 candidate.

use std::fmt;

pub const REQUIRED_BASELINE: &str = "f509fce5df6c16b77d3accdccde4c640b093da0a";
pub const PROFILE_ID: &str = "SFD_MINIMUM_SUCCESSOR_NONCANONICAL_NONACTIVATABLE";

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub enum IngressPhase {
    CurrentSource,
    ApiModel,
    TypedHirOnly,
}

impl IngressPhase {
    pub fn parse(value: &str) -> Result<Self, SourceError> {
        match value {
            "current_source" => Ok(Self::CurrentSource),
            "api_model" => Ok(Self::ApiModel),
            "typed_hir_only" => Ok(Self::TypedHirOnly),
            _ => Err(SourceError::UnsupportedIngress(value.to_owned())),
        }
    }

    pub const fn as_str(self) -> &'static str {
        match self {
            Self::CurrentSource => "current_source",
            Self::ApiModel => "api_model",
            Self::TypedHirOnly => "typed_hir_only",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SourceCase {
    pub oracle_id: String,
    pub subfixture_id: String,
    pub ingress_phase: IngressPhase,
    pub selected_mode: String,
    pub media_type: String,
    pub bytes: Vec<u8>,
}

impl SourceCase {
    pub fn utf8(&self) -> Result<&str, SourceError> {
        std::str::from_utf8(&self.bytes).map_err(|_| SourceError::InvalidUtf8)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct ByteSpan {
    pub start: usize,
    pub end: usize,
}

impl ByteSpan {
    pub fn new(start: usize, end: usize, len: usize) -> Result<Self, SourceError> {
        if start > end || end > len {
            return Err(SourceError::InvalidSpan { start, end, len });
        }
        Ok(Self { start, end })
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum SourceError {
    InvalidUtf8,
    UnsupportedIngress(String),
    InvalidSpan {
        start: usize,
        end: usize,
        len: usize,
    },
}

impl fmt::Display for SourceError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidUtf8 => formatter.write_str("source bytes are not strict UTF-8"),
            Self::UnsupportedIngress(value) => {
                write!(formatter, "unsupported ingress phase: {value}")
            }
            Self::InvalidSpan { start, end, len } => {
                write!(
                    formatter,
                    "invalid UTF-8 byte span {start}..{end} for length {len}"
                )
            }
        }
    }
}

impl std::error::Error for SourceError {}
