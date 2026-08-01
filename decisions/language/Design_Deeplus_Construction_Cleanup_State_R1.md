# Design Deeplus Construction, Initialization, and Cleanup State R1

Status: `STABLE_DESIGN_CANONICAL_CANDIDATE`

Gap: `IR-OWN-P0-016`

Baseline: `howork/Deeplus main@88bbc4fe6217fc1b0e8d5db05379ef046eb07abe`

Product support: `15_OF_15_NOT_RUN`

## Decision

Deeplus adopts a field-token construction transaction. A constructor attempt
owns one `ConstructionSessionId`, one provisional `ObjectOwnerId`, and one
linear `ConstructionTokenId`. Same-type delegation reuses those identities.
The token is consumed exactly once by commit or abort; only commit publishes a
`Self` value, and it publishes exactly one.

This decision adds no source spelling. It gives machine meaning to existing
`def!`, `Type!(...)`, named construction, constructor-header delegation, and
`def#cleanup` surfaces.

## Stored-field state

Every nominal stored field has a `FieldSlotId` distinct from behavioral
`ClassSlotId` and structural `CLOSED_ROW_FIELD_ID`. Its constructor state is
one of `Uninitialized`, `Live`, `Moved`, or `MaybeMoved`. Initializer
expressions evaluate into separate temporaries. Only an atomic
`FIELD_INIT_COMMIT` transfers the owner and cleanup token and changes the
complete required subtree to `Live`.

A `let` field rejects a second initialization. A `var` field's first
assignment is initialization and later assignments are ordinary live writes or
replacements. Optional type does not imply uninitialized storage; omission
requires an explicit or default `::none` plan. Every required slot must be
`Live` at commit.

## Delegation and prepublication self

Same-type delegation cannot allocate, create a nested session, publish, or
consume the construction token. Superclass construction completes its storage
segment before current-class storage begins. If derived construction later
fails, live derived fields are cleaned in reverse acquisition order before the
committed base segment is cleaned recursively.

Before commit, `self` is the internal capability
`PrepublicationSelf(ConstructionSessionId, InitMask)`, not an ordinary surface
type. It may initialize the current class's uninitialized field, read a fully
live projection, replace a live `var` field, perform selected header
delegation, call a nonescaping direct helper after the required mask is live,
or run a pure total post-init guard. It may not escape, be sent, cross FFI,
enter async/generator state, or participate in dynamic, witness, extension,
actor-message, or unknown dispatch.

## Commit, abort, and normal cleanup

`OBJECT_CONSTRUCTION_COMMIT` requires a complete live mask, one delegation
root, successful post-init guards, exact owner/token balance, no temporary
residue, no self escape, and zero prior publications. It atomically transfers
the construction-held ownership to the object, seals normal cleanup, publishes
once, and consumes the construction token.

Any pre-live failure performs `OBJECT_CONSTRUCTION_ABORT`. It first consumes
the construction token and preserves the triggering Error, Defect, or
Cancellation as primary. It then cleans only live, non-moved fields in reverse
successful acquisition order, followed by committed base segments. The
not-yet-committed most-derived `def#cleanup` is never called. Cleanup failures
are suppressed in actual execution order and cannot mask the triggering
outcome.

A live object's cleanup is hook-then-fields-then-base: consume the cleanup-once
guard, invoke the most-derived `def#cleanup`, clean remaining most-derived
fields in reverse acquisition order, then recursively process the direct base
segment. A user hook cannot suppress automatic cleanup.

## HIR and MIR binding

Canonical HIR gains the thirteenth structural plan,
`HIR-H1/STRUCT/CONSTRUCTION_LIFECYCLE_PLAN`, represented by
`HirConstructionLifecyclePlan`. It binds the constructor and class identities,
base and field slots, initial and CFG masks, delegation, field commits,
owner/token transfers, prepublication-self uses, guards, both cleanup orders,
the commit predicate, the unique publication site, and source provenance.

Backend-neutral Deeplus MIR expands its exact operation universe from 29 to 42
with thirteen nominal construction and cleanup operations. Every such
operation records the session, phase and mask transition, consumed and produced
owners and cleanup tokens, outcome edge, and HIR provenance. The existing MIR
`BUILDER` token is the representation class specialized as
`ConstructionTokenId`; no second linear-token kind is introduced. Cranelift
drop flags remain target projections and never define language semantics.

## Diagnostics and tests

Six deterministic source diagnostics cover early read, second let
initialization, CFG mask disagreement, incomplete commit, precommit self
escape, and precommit dispatch. Four release-verifier diagnostics cover HIR
mask validity, MIR token balance, cleanup order, and publication count.

The canonical fixture contains 24 design-static cases: six positive, eight
boundary, six negative, and four mutation cases. These are acceptance
specifications, not compiler or product execution receipts.

## Status fence

- semantic P0 introduced: `0`
- canonical feature P1: `22_OPEN_UNCHANGED`
- M13 actions: `4_OPEN_UNCHANGED`
- production parser/checker/MIR/xVM/runtime/backend/tooling: `NOT_RUN`
- product lanes: `15_OF_15_NOT_RUN`

`IR-OWN-P0-016` may be closed only after this candidate is integrated,
repository validation passes, and publication readback verifies the exact
canonical bytes. Design closure does not claim product implementation.
