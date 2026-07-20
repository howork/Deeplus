//! Deterministic xVM bytecode envelope for a verified MIR plan.

use deeplus_mir::sfd_p1_009::{MirPlan, verify};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BytecodePlan {
    pub version: &'static str,
    pub mir: MirPlan,
}

pub fn emit(mir: MirPlan) -> Result<BytecodePlan, &'static str> {
    verify(&mir)?;
    Ok(BytecodePlan {
        version: "SFD-P1-009-XBC-R1",
        mir,
    })
}
