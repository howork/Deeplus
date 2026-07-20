//! HIR-to-MIR lowering with explicit ordered observations.

use deeplus_hir::sfd_p1_009::HirCase;
use deeplus_mir::sfd_p1_009::{MirEvent, MirPlan, phases_for};

pub fn lower(hir: HirCase) -> MirPlan {
    let events = phases_for(&hir)
        .iter()
        .enumerate()
        .map(|(index, phase)| {
            let ordinal = u32::try_from(index + 1).expect("bounded phase count fits u32");
            MirEvent {
                event_index: ordinal,
                phase_ordinal: ordinal,
                phase: (*phase).to_owned(),
            }
        })
        .collect();
    MirPlan {
        oracle_id: hir.typed.ast.oracle_id,
        subfixture_id: hir.typed.ast.subfixture_id,
        operation_id: hir.operation_id,
        outcome: hir.typed.outcome,
        events,
        fallback_attempt_count: 0,
        unresolved_lookup_count: hir.unresolved_lookup_count,
    }
}
