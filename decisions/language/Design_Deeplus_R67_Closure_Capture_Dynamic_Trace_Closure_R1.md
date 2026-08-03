# Deeplus R67 Closure Capture Dynamic Trace Closure R1

## Decision

R67 accepts a bounded semantic repair of the already-Stable closure-capture
minimum sound profile and, only after that repair is verified, closes exactly
one implementation-target trace cell:

`closure_capture_descriptor_msp / DYNAMIC_LOWERING`.

The local predecessor is
`a1fc8b99db7e7392fa17ea78880d02239ffc5d1e`. The canonical publication
baseline remains `39a5d50cc770341c4b9776d00d84520b780d0c62`.

The predecessor cell is `APPLICABLE_BLOCKED_BY_GAP` under
`IR-XCUT-P1-054`. The repaired cell is `BOUND_DIRECT`. It is neither
delegated nor not-applicable because `closure_capture_descriptor_msp` owns
capture acquisition, closure-environment construction, commit, rollback, and
cleanup. The responsibility-identity registry remains an upstream proof
provider and does not absorb those consumer operations.

## Bounded semantic repair

### Move/once commit barrier

`MOVE` and `ONCE` preparation reserves ownership but does not execute
`PLACE_MOVE`, consume the source, or publish an environment field. All
fallible capture evaluation, evidence selection, acquisition, and cleanup
registration completes before one explicit commit barrier. Failure before
that barrier cancels every live move reservation and leaves its source live;
the prepared prefix is released in strict reverse acquisition order.

The interval after the barrier is branchless, nonsuspending, and infallible.
It executes source-ordered `PLACE_MOVE` plus `BUILDER_STAGE` for reserved
`MOVE`/`ONCE` fields, then one `BUILDER_COMMIT`, then one infallible
`CLOSURE_MAKE`. There is no error, defect, cancellation, suspension, or
rollback successor from this interval, and a partial environment or closure
is never published. R67 introduces no new MIR operation or terminator kind.

### Capture evidence domains

Capture admission is a closed three-way relation:

1. modes other than `COPY` and `CLONE` carry a null
   `responsibility_evidence_id_or_null`;
2. `COPY` admits the exact `CopyValue` rule and one exact
   `ResponsibilityEvidenceId`; its descriptor is an intrinsic predicate proof
   and carries a null `TraitWitnessId`;
3. `CLONE` admits the exact `Clone` rule and one exact
   `ResponsibilityEvidenceId`; the resolved descriptor owns the exact non-null
   `TraitWitnessId` together with its error, effect, acquisition, and cleanup
   residue.

The exact `ResponsibilityEvidenceId` (or null) projects byte-for-byte from
typed HIR into MIR; the descriptor remains the owner of the rule and witness
fields. The callable `ResponsibilityProfileId` remains a separate identity
domain and is never reused as capture evidence. Runtime, xVM, and backend
relookup or replacement counts remain zero.

### Deep capture fence

`deep` remains a source-level Preview rejection with
`FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE`. `DEEP` is absent from the
admitted canonical HIR and MIR capture-mode universes. Current lowering has
exactly zero DEEP capture rows and zero DEEP operations. R67 does not activate
`DeepClone` and does not decide graph, cycle, alias-preservation, traversal,
rollback, or cleanup policy.

## Direct evidence

The single trace binding uses one `ARTIFACT_POINTER`:

`spec/contracts/hir-mir-lowering-registry.json#/closure_capture_plan_lowering_contract`.

That closed contract owns the repaired capture projection, commit barrier,
evidence-domain preservation, DEEP zero fence, exact HIR-to-MIR projection,
zero new operation-kind count, and `NOT_RUN` product fence. The focused R67
validator binds it to the repaired R31 contract, HIR/MIR schemas, bridge,
machine registry, acceptance fixture, and API-private residue fence.

## Exact trace postcondition

R67 changes exactly one of 4,221 atomic trace cells. The other 4,220 cells
remain unchanged and have the predecessor digest
`cd52a1d81105c67d0033687047f1d819f165aac964fc88b414544474e50c2bcb`.

The post-overlay counts are:

- 469 feature rows;
- 3,283 stage cells and 1,407 conformance outcome cells;
- 2,465 `BOUND_DIRECT` cells;
- 3 `BOUND_DELEGATED` cells;
- 501 `NOT_APPLICABLE` cells;
- 1,252 `APPLICABLE_BLOCKED_BY_GAP` cells;
- 0 missing and 0 conflicting cells;
- 13 applied overlays, 129 cumulative bindings, and 3,142 evidence entries.

No P0, P1, or M13 action is created or closed. Semantic P0 remains zero,
feature P1 remains `22_OPEN_UNCHANGED`, and M13 actions remain
`4_OPEN_UNCHANGED`.

## Authority and evidence fences

This is a local noncanonical Design static-evidence closure. It makes no
production parser, checker, MIR, xVM, runtime, backend, formatter, LSP, or
conformance-execution claim. Product lanes remain `15_OF_15_NOT_RUN`, product
execution receipt count is zero, and GitHub publication remains `SUSPENDED`.
Canonical source activation, public syntax, diagnostics, feature identities,
and the R66 responsibility-identity authority are unchanged.
