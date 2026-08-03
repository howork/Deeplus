# Deeplus Ownership Tooling Projection R1

Status: `STABLE_DESIGN_IMPLEMENTATION_READINESS_CANDIDATE`

Candidate class: `LOCAL_NONCANONICAL_NONACTIVATABLE`

Gap: `IR-OWN-P2-027`

R48 fusion baseline: canonical R47 publication closure at
`39a5d50cc770341c4b9776d00d84520b780d0c62` (tree
`b19b2a86c0f29c1f73763c8526a3a7bde23d530a`). The original R39 decision was
derived from `4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`; that identity remains
historical provenance rather than the active local-fusion binding.

## Decision

Deeplus tooling is a read-only projection of sealed source, HIR, ownership and
MIR evidence. The formatter, LSP and debugger do not participate in ownership
admission and cannot create an owner, loan, cleanup token, root, continuation,
Trait witness or transfer authority.

Every request binds the exact R28 `ParseSnapshotId` and extends it with checker
and ownership-contract digests; it does not create a second document-revision
authority. Hover reports exact
normalized type, mode, place state, owner/loan/region relation, cleanup
responsibility and proof certainty. An unavailable or recovered fact is shown
as unavailable; it is never guessed.

An ownership diagnostic has one primary location. Its exact diagnostic row,
and where applicable its typed rejection-reason variant, selects the complete
related-role multiset and cardinality; family labels are grouping only.
Candidate locations are serialized by stable `SourceOriginId` and a typed
semantic-reference tie-break; source, fixture, catalog and CFG iteration order
never decides. Conflict diagnostics show every conflicting access, and join
diagnostics show every relevant predecessor.

Formatting preserves ownership-bearing tokens, responsibility order,
normalized HIR and the responsibility digest, and a second pass emits no edit.
Rename is admitted only from an exact symbol graph and proves ownership graph
isomorphism across the authorized spelling substitution. Automatic actions are
limited to presentation-only or responsibility-neutral edits whose HIR,
responsibility and checker result remain identical. Inserting `move`, `clone`,
sharing/transfer proof, capture mode, region widening, cleanup or conformance
authority is never automatic.

The debugger uses semantic IDs from an activation-scoped, receipt-bound
ownership observation. `RuntimeInstanceId`, `ExecutionId`, activation frame,
`pause_epoch` and the exact runtime/debug receipt prevent observations from
different activations from colliding.
Machine addresses, registers, stack slots, xVM slots and CLIF values may be
ephemeral display-only locations. They are excluded from semantic equality,
digests and persistence. The root and continuation panel schemas bind the
canonical managed-reference and continuation-interface digests. Runtime rows
remain unavailable until an exact runtime/debug receipt is supplied; tooling
must not synthesize them from design-static evidence.

Actor transfer remains sender-owned before commit. Exactly at
`enqueue_committed`, one commit produces receiver ownership or admitted shared
evidence and a channel-local sequence. Tooling cannot manufacture dual owners,
precommit sequence values or cross-channel/global ordering. Runtime/debugger
execution remains `NOT_RUN`.

## Evidence fence

- Source syntax change: 0
- Grammar production change: 0
- Language semantic change: 0
- New source diagnostic: 0
- New release-verifier diagnostic: 1,
  `OWNERSHIP_TOOLING_PROJECTION_DRIFT`
- Existing open feature P1: exactly 22, unchanged
- Separate M13 actions: exactly 4, unchanged
- Formatter, LSP and debugger product execution: `NOT_RUN`
- Product lanes: 15/15 `NOT_RUN`
- GitHub publication: suspended

Static schemas, fixtures and validators establish only design-contract
consistency. They are not formatter, LSP, debugger, compiler, runtime or
backend execution receipts.
