# R60 Pattern Match Ownership Split Trace Closure

Status: `LOCAL_APPROVED_CANDIDATE`

Baseline: `e120f83db380ee182f0117713a67e97886bfcd11`

Scope: `pattern_match_ownership_split` static semantics and dynamic lowering.
This decision changes no grammar production, AST/HIR identity, MIR opcode,
source activation, feature P1, or product-support claim.

## Decision

`PatternMatchOwnershipAdmitted` is the integrated-checker judgment for one
normalized Pattern attempt. Its binder interface is the exact tuple `(name,
canonical type, ownership mode, mutability, usable region, capability set)`.
Every Or alternative must expose the same interface. The first
source-ordered structural success wins; neither a later guard failure nor any
other failure retries a later alternative.

An Alias Pattern is a same-subject shared borrow and never a clone. It is
rejected when any descendant is moved or exclusively borrowed. A borrowed
subject cannot move an affine payload; the existing grammar-rooted
`move PatternPrimary` is admitted only when the subject supplies consuming
owner authority.

Probe and guard phases publish no ownership residue. Every aborted
preparation cancels its move reservations. Final success performs admitted
moves and shared-loan acquisition before one infallible group
`BINDING_COMMIT` publication barrier. Each resulting loan ends at the earliest
invalidating mutation, move, replacement, cleanup, or enclosing-region
frontier.

Normally returning arms join only after compatible place identity and
ownership state are proved. Divergent arms are excluded, and the capability
intersection is computed only after compatibility. No implicit clone, move,
or ownership join is synthesized.

## Diagnostic ownership

- `OR_PATTERN_BINDINGS_INCONSISTENT`: unequal normalized Or interface.
- `ALIAS_PATTERN_OWNERSHIP_CONFLICT`: Alias conflicts with moved/exclusive
  descendant.
- `PATTERN_BORROWED_MATCH_CANNOT_MOVE_PAYLOAD`: borrowed affine-payload move.
- `PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH`: incompatible returning-arm place
  state.
- `OWN_CAST_REQUIRES_REUSABLE_SOURCE` belongs to `owned_downcast_result`, not
  Pattern matching.

## Lowering repair

`HM-LR-PAT-027`, `HM-LR-PAT-028`, and `HM-LR-PAT-029` use only existing
operations. Or adds the final binding barrier; Alias begins the staged shared
loan before that barrier; Move orders `PLACE_MOVE` before the barrier and
provides `MOVE_CANCEL` for an aborted reservation. These child-row operations
remain compositional requirements collapsed into the enclosing single
PatternAttempt commit.

## Governance fence

- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15 NOT_RUN`
- GitHub publication: `SUSPENDED`
- production implementation: `NOT_AUTHORIZED`
