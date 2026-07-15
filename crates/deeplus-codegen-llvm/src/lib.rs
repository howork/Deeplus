//! Deeplus responsibility-boundary scaffold: shared MIR-to-LLVM lowering for AOT and later ORC JIT.
//!
//! This crate has no product execution receipt at migration M1.

#![forbid(unsafe_code)]

/// The architecture responsibility assigned by Management System R1.1.
pub const RESPONSIBILITY: &str = "shared MIR-to-LLVM lowering for AOT and later ORC JIT";
/// A compiled scaffold must not be confused with language support.
pub const PRODUCT_STATUS: &str = "NOT_RUN";
/// Stable marker used by repository-structure tests only.
pub struct DeeplusCodegenLlvmScaffold;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scaffold_is_evidence_honest() {
        assert_eq!(PRODUCT_STATUS, "NOT_RUN");
        assert!(!RESPONSIBILITY.is_empty());
    }
}
