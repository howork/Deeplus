//! xVM projection. Compilation does not execute this function.

use deeplus_mir::sfd_p1_009::{MirEvent, Outcome};
use deeplus_xbc::sfd_p1_009::BytecodePlan;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Observation {
    pub oracle_id: String,
    pub subfixture_id: String,
    pub operation_id: String,
    pub outcome: Outcome,
    pub events: Vec<MirEvent>,
    pub payload_eval_count: u32,
    pub lookup_count: u32,
    pub fallback_attempt_count: u32,
    pub commit_count: u32,
    pub rollback_count: u32,
    pub publication_count: u32,
    pub drop_count: u32,
}

pub fn execute(bytecode: BytecodePlan) -> Observation {
    let outcome = bytecode.mir.outcome;
    let (commit_count, rollback_count, publication_count) = match outcome {
        Outcome::Reject => (0, 1, 0),
        Outcome::Accept | Outcome::AssertRelation | Outcome::MutantKill => (1, 0, 1),
    };
    Observation {
        oracle_id: bytecode.mir.oracle_id,
        subfixture_id: bytecode.mir.subfixture_id,
        operation_id: bytecode.mir.operation_id,
        outcome,
        events: bytecode.mir.events,
        payload_eval_count: 1,
        lookup_count: 0,
        fallback_attempt_count: bytecode.mir.fallback_attempt_count,
        commit_count,
        rollback_count,
        publication_count,
        drop_count: 1,
    }
}
