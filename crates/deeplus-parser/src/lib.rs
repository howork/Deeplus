//! Deeplus responsibility-boundary scaffold: root-connected parsing and lossless CST construction.
//!
//! This crate has no product execution receipt at migration M1.

#![forbid(unsafe_code)]

/// The architecture responsibility assigned by Management System R1.1.
pub const RESPONSIBILITY: &str = "root-connected parsing and lossless CST construction";
/// A compiled scaffold must not be confused with language support.
pub const PRODUCT_STATUS: &str = "NOT_RUN";
/// Stable marker used by repository-structure tests only.
pub struct DeeplusParserScaffold;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scaffold_is_evidence_honest() {
        assert_eq!(PRODUCT_STATUS, "NOT_RUN");
    }
}
