//! Observable MIR plan for the bounded SFD-P1-009 projection.

use deeplus_hir::sfd_p1_009::HirCase;
pub use deeplus_types::sfd_p1_009::Outcome;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct MirEvent {
    pub event_index: u32,
    pub phase_ordinal: u32,
    pub phase: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct MirPlan {
    pub oracle_id: String,
    pub subfixture_id: String,
    pub operation_id: String,
    pub outcome: Outcome,
    pub events: Vec<MirEvent>,
    pub fallback_attempt_count: u32,
    pub unresolved_lookup_count: u32,
}

pub fn verify(plan: &MirPlan) -> Result<(), &'static str> {
    if plan.fallback_attempt_count != 0 {
        return Err("fallback is forbidden");
    }
    if plan.unresolved_lookup_count != 0 {
        return Err("unresolved lookup remains in MIR");
    }
    for (index, event) in plan.events.iter().enumerate() {
        let ordinal = u32::try_from(index + 1).map_err(|_| "event count overflow")?;
        if event.event_index != ordinal || event.phase_ordinal != ordinal {
            return Err("event identity is not deterministic");
        }
    }
    Ok(())
}

pub fn phases_for(hir: &HirCase) -> &'static [&'static str] {
    match hir.ownership_mode {
        "borrow" => &[
            "PLACE_AVAILABLE",
            "SHARED_VIEW_RESERVED",
            "BORROW_FACET_LIVE",
            "VIEW_ENDED",
        ],
        "inout" => &[
            "PLACE_AVAILABLE",
            "EXCLUSIVE_VIEW_RESERVED",
            "INOUT_FACET_LIVE",
            "EXCLUSIVITY_RELEASED",
        ],
        _ => &[
            "OWNER_AVAILABLE",
            "PREPARE",
            "VALIDATE",
            "COMMIT_OR_ROLLBACK",
            "CLEANUP",
        ],
    }
}
