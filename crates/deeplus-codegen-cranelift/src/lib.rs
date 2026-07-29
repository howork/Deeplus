//! Deeplus responsibility-boundary scaffold for MIR-to-Cranelift lowering.
//!
//! This crate has no product execution receipt at migration M1.

#![forbid(unsafe_code)]

/// The architecture responsibility assigned by Management System R1.1.
pub const RESPONSIBILITY: &str =
    "verified Deeplus MIR to backend-private CLIF for object AOT and in-memory JIT";
/// Deeplus MIR remains the semantic authority. CLIF is only a projection.
pub const SEMANTIC_AUTHORITY: &str = "Deeplus MIR";
/// A compiled scaffold must not be confused with language support.
pub const PRODUCT_STATUS: &str = "NOT_RUN";
/// The two native realization paths share one MIR-to-CLIF lowering contract.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum CraneliftModuleKind {
    /// Emit a relocatable object and finish it with the platform linker.
    ObjectAot,
    /// Finalize code and data in memory for direct execution.
    InMemoryJit,
}

/// Stable marker used by repository-structure tests only.
pub struct DeeplusCodegenCraneliftScaffold;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scaffold_is_evidence_honest() {
        assert_eq!(PRODUCT_STATUS, "NOT_RUN");
        assert_eq!(SEMANTIC_AUTHORITY, "Deeplus MIR");
        assert_ne!(
            CraneliftModuleKind::ObjectAot,
            CraneliftModuleKind::InMemoryJit
        );
    }
}
