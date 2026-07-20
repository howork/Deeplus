//! Normalized typed HIR for one frozen SFD-P1-009 case.

use deeplus_types::sfd_p1_009::TypedCase;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct HirCase {
    pub typed: TypedCase,
    pub operation_id: String,
    pub ownership_mode: &'static str,
    pub unresolved_lookup_count: u32,
}

pub fn lower(typed: TypedCase) -> HirCase {
    let mode = typed.ast.selected_mode.as_str();
    let ownership_mode = if mode.contains("inout") {
        "inout"
    } else if mode.contains("borrow") || mode.contains("view") {
        "borrow"
    } else {
        "owned"
    };
    let operation_id = operation_for(&typed.ast.oracle_id, mode).to_owned();
    HirCase {
        typed,
        operation_id,
        ownership_mode,
        unresolved_lookup_count: 0,
    }
}

fn operation_for(oracle_id: &str, mode: &str) -> &'static str {
    if mode.contains("adapter") {
        "EV-ADAPTER-TRANSACTION"
    } else if mode.contains("registry") || mode.contains("provider") {
        "EV-REGISTRY-PROJECTION"
    } else if mode.contains("conformance") || mode.contains("witness") {
        "EV-CONFORMANCE-WITNESS"
    } else if mode.contains("variant") || mode.contains("enum") {
        "EV-ENUM-VARIANT"
    } else if oracle_id.starts_with("SFD-PROP-") {
        "EV-PROPERTY-CHECK"
    } else {
        "EV-FACET-BORROW"
    }
}
