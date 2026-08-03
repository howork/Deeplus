# R66 Responsibility Identity Dynamic Trace Closure

Status: `LOCAL_APPROVED_CANDIDATE`

Canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`

Local predecessor: `5c36347f7ed7d2d23e5342f311766cea93b6aa89`

Gap: `IR-XCUT-P1-054`

Scope: exactly one implementation-target trace cell,
`responsibility_identity_registry_r1 / DYNAMIC_LOWERING`. R66 changes that
cell from `APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`. It changes no source
spelling, grammar production, AST or HIR node identity, responsibility rule,
admission predicate, runtime operation, MIR operation or terminator kind,
diagnostic, source activation, feature P1, or product-support claim.

## Direct dynamic-lowering ownership

The R30 responsibility registry directly owns a deterministic, non-structural
typed-HIR-to-MIR evidence projection. Every admitted responsibility fact is
represented in typed HIR by one `ResponsibilityEvidenceDescriptor` and in MIR
by the corresponding row in `responsibility_evidence_table`. The descriptor
is evidence residue, not a standalone expression, statement, operation,
dispatch, search, or runtime behavior.

The projection is direct rather than delegated because the registry defines
the responsibility identity domains and the exact evidence record being
preserved. A consumer may use a verified evidence row for its own operation,
but it does not become the lowering owner of the registry row. R66 therefore
creates no delegate feature, delegate reason, fallback edge, runtime provider,
or backend route.

## Controlling evidence binding

The direct trace cell is bound to the following existing authorities:

- `spec/contracts/responsibility-identity-registry-r1.json#/evidence_residue`
  defines the exact typed-HIR and MIR residue, exact identity and selected
  witness preservation, and zero Clone or DeepClone runtime relookup.
- `schemas/language/canonical-hir-h1.schema.json#/$defs/CanonicalModuleBase/properties/responsibility_evidence_descriptors`
  and
  `schemas/language/canonical-hir-h1.schema.json#/$defs/ResponsibilityEvidenceDescriptor`
  define the closed non-structural typed-HIR table and descriptor. The table
  adds no HIR identity-catalog row and is disjoint from callable
  `ResponsibilityProfileId`.
- `spec/contracts/hir-mir-lowering-registry.json#/profile_contract/responsibility_evidence_projection_contract`
  requires exact field projection except that typed-HIR `source_provenance`
  projects to MIR `source_origin_id`; it permits neither runtime nor backend
  relookup and does not reuse the callable responsibility-profile domain.
- `schemas/language/deeplus-mir.schema.json#/properties/responsibility_evidence_table`
  and
  `schemas/language/deeplus-mir.schema.json#/$defs/responsibilityEvidenceDescriptor`
  define the backend-neutral MIR table and its closed 15-field row.
- `spec/contracts/mir-machine-registry.json#/responsibility_evidence_projection_contract`
  requires strict ascending Unicode-scalar order by
  `responsibility_evidence_id`, uniqueness on that key, exact-domain
  resolution for every non-null identity, and comparison of the complete
  typed-HIR descriptor before MIR admission.

Together these artifacts determine the lowering residue completely. Product
execution is not required to classify the trace cell, and the structured
static evidence level remains `E2_STRUCTURED_STATIC`.

## Exact identity-preservation fence

R66 preserves the six registry identities without implication, substitution,
or domain collapse:

1. `PlainValue`
2. `Shareable`
3. `Transferable`
4. `CopyValue`
5. `Clone`
6. `DeepClone`

The typed-HIR and MIR descriptors preserve the exact
`ResponsibilityRuleId`, `ResponsibilityEvidenceId`, normalized `TypeId`,
evidence kind, registry revision, derivation digest, and nullable selected
Trait witness, error set, effect row, result-acquisition plan, cleanup plan,
owner, region, and destination-isolation identities. The MIR row replaces only
source provenance with its exact `SourceOriginId` projection.

`ResponsibilityRuleId` and `ResponsibilityEvidenceId` never reuse the callable
`ResponsibilityProfileId`/`responsibility_id` domain. Intrinsic evidence does
not become a runtime object, vtable, dispatch entry, allocation, layout, ABI,
or backend identity. xVM, runtime, and Cranelift may consume an already
verified row but cannot derive, search, re-resolve, replace, or synthesize its
responsibility evidence.

`DeepClone` remains `RESERVED_PREVIEW_NONACTIVATABLE`; the existence and
projection of its reserved identity neither activates `deep` nor closes its
graph, cycle, alias-preservation, traversal, rollback, or cleanup policy.

## Consumer-operation ownership fence

The registry's direct evidence projection does not absorb the behavior of its
consumers:

- `closure_capture_descriptor_msp` owns capture acquisition, environment
  commit, rollback, and cleanup. Its `copy`, `clone`, and reserved `deep`
  branches consume the exact `CopyValue`, `Clone`, or `DeepClone` evidence but
  do not own registry-row projection.
- `actor_protocol_family` owns transport admission and actor-message behavior.
  It consumes exact `TransferableAcrossIsolation` evidence; it does not create
  a responsibility rule, evidence identity, witness, or registry derivation.
- Plain-value, public-Plain alias, and shareable-observation features consume
  their static predicates and retain their own behavior or non-behavior
  boundaries.
- `trait_witness_coherence_phase_a` remains a prerequisite for exact selected
  witnesses. It is not the delegate or runtime owner of responsibility
  evidence projection.

No consumer creates an owner-definition feedback edge. R66 does not close any
consumer's separate dynamic or conformance-test trace gap.

## Exact trace transition

R66 performs exactly this one transition:

1. `responsibility_identity_registry_r1 / DYNAMIC_LOWERING` changes from
   `APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT` with direct evidence rooted at
   `spec/contracts/hir-mir-lowering-registry.json#/profile_contract/responsibility_evidence_projection_contract`.

The other `4220` implementation-target trace cells remain byte-for-byte and
classification-for-classification unchanged. R66 adds one applied overlay and
one overlay binding; it adds no delegated binding and no not-applicable
classification.

## Expected trace totals

After applying the exact one-cell transition, the implementation-target trace
has these derived totals:

- `BOUND_DIRECT`: `2464`
- `BOUND_DELEGATED`: `3`
- `NOT_APPLICABLE`: `501`
- `APPLICABLE_BLOCKED_BY_GAP`: `1253`
- applied evidence overlays: `12`
- overlay bindings: `128`
- evidence-bound stage and outcome cells: `3141`

These totals are static trace-closure constraints, not parser, checker, MIR,
xVM, runtime, Cranelift, formatter, LSP, or product-execution receipts.

## Governance fence

- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15_NOT_RUN`
- canonical source mutation: `0`
- GitHub publication: `SUSPENDED`
- production implementation: `NOT_AUTHORIZED`

R66 closes only the evidence omission in `IR-XCUT-P1-054`. It does not change
language meaning, expand source activation, activate `DeepClone`, claim a
runtime implementation, or authorize GitHub publication.
