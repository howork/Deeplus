# Deeplus Responsibility Identity Registry R1

Status: `STABLE_DESIGN_STATIC_CANDIDATE`
Gap: `IR-OWN-P1-023`
Baseline: `howork/Deeplus main` at
`4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`
Product support: `15/15 NOT_RUN`

## Decision

Deeplus responsibility facts form independent axes. They are not a subtype
chain and they do not silently manufacture one another. The current grammar is
sufficient: ordinary type and Trait references, `conforms`, `supports auto`,
`by auto`, and the existing capture-mode tokens already provide every required
source route. R1 therefore adds no source spelling and no grammar production.

The registry assigns one stable identity and one kind to each current name:

| Surface or operation | Canonical identity kind | Source conformance |
|---|---|---|
| public `Plain`, formal internal `PlainValue` | sealed intrinsic predicate; the public spelling resolves to one `ResponsibilityRuleId` | direct/manual conformance forbidden |
| `Shareable` | sealed compiler-governed responsibility Trait with one closed auto policy | direct/manual conformance forbidden |
| `Transferable` | sealed compiler-governed responsibility Trait with one closed auto policy | direct/manual conformance forbidden |
| capture `copy` | internal `CopyValue` predicate; there is no public `Copy` Trait in R1 | not source-implementable |
| `Clone` | public behavioral Trait selected through one exact witness | ordinary explicit conformance allowed |
| `DeepClone` / capture `deep` | separately identified Preview behavioral Trait/profile | nonactivatable until graph policy closes |
| `Reusable`, `Affine`, `Resource` | internal lifecycle classes | not source Traits |
| `Shared<T>` | nominal shared-owner handle | neither a responsibility Trait nor an alias of `Shareable` |

`PlainValue` as source text, `Sendable`, `ShareSafe`, `Copyable`, `Duplicable`,
`Aliasable`, `PlainData`, and `Deep` as a Trait name produce no admitted
responsibility identity. `PlainValue` is the formal internal identity behind
the sole public spelling `Plain`; it is not a second spelling available to a
program. The remaining names
are removed or stale vocabulary, not compatibility aliases. In particular,
`Sendable` is replaced by the narrower current name `Transferable`, and
`ShareSafe` is replaced by `Shareable` only where the text means observation
safety.

## Independent responsibility axes

The checker normalizes a type to a product, not an inheritance lattice:

```text
Lifecycle       = Reusable | Affine | Resource
ImplicitCopy    = None | CopyValue
ExplicitClone   = None | Clone(TraitWitnessId)
DeepClone       = None | DeepClone(ProfileId, EvidenceId)
Observation     = LocalOnly | Shareable(ResponsibilityEvidenceId)
IsolationMove   = LocalOnly | Transferable(ResponsibilityEvidenceId)
Storage         = Direct | SharedHandle(PayloadTypeId)
```

The sole public-to-internal mapping is `Plain -> PlainValue`. Every cross-axis semantic
implication count is zero. Specifically:

- `Plain` does not imply `CopyValue`, `Shareable`, `Transferable`, raw layout,
  ABI layout, JSON, dynamic dispatch, serialization, or FFI safety.
- `CopyValue` does not imply `Plain`, `Clone`, or `DeepClone`.
- `Clone` does not imply `CopyValue`, `DeepClone`, `Shareable`, or
  `Transferable`.
- `Shareable` proves observation safety only. It does not create an alias,
  construct `Shared<T>`, or imply transfer.
- `Transferable` proves one owned move across one isolation boundary. It does
  not prove shared observation, authority delegation, copying, cloning, or
  layout safety.
- No responsibility identity controls destruction. Cleanup remains
  language-owned through lifecycle class, cleanup tokens/plans, and
  `def#cleanup()`.

## Admission algorithms

All intrinsic admission is deterministic, import-order independent, and
terminating. The checker first expands transparent aliases, interns the exact
normalized `TypeId`, applies fail-closed negative gates, and then evaluates a
finite owner-closed component graph. Positive recursive obligations are solved
per finite strongly connected component with memoized states
`UNSEEN | VISITING | PASS | FAIL`; encountering a forbidden axis immediately
sets the component to `FAIL`. An opaque nominal has no structural inference and
passes only through its exact registered compiler policy. An annotation, type
alias, wrapper, import order, source order, link order, or runtime lookup cannot
create evidence.

### PlainValue

`PlainValue` requires a reusable, deterministic immutable semantic projection
with no lifecycle owner, cleanup, region-bound view, callable environment,
shared-owner handle, raw pointer/provenance authority, reflection/meta
authority, provider lease, actor owner, or hidden resource. Aggregate admission
recurses through every semantically stored component. The rule says nothing
about representation bytes.

### Shareable

`Shareable` requires that every observation reachable through admitted aliases
is immutable or otherwise governed by an exact registered synchronization law.
The derivation produces observation evidence only. A `Shared<T>` handle may
have a registered Shareable policy, but merely wrapping `T` does not derive
Transferable for either the wrapper or payload.

### Transferable

`Transferable` requires an owned value, no borrowed/inout region, and an exact
registered transfer law for every cleanup token, payload component, provider
lease, and authority. Authority delegation remains an independent proof. At a
cross-isolation move the ownership checker recomputes the evidence against the
exact `TypeId`, `OwnerId`, destination `IsolationDomainId`, and registry
revision. Missing, extra, stale, or mismatched evidence rejects before commit.
A moved `Shared<T>` handle is distinct from a cross-isolation shared loan; the
latter remains outside the current R5 ownership profile.

### CopyValue

`copy` capture asks the internal `CopyValue` predicate for a semantic,
source-preserving, cleanup-free duplication. It is not a byte copy, ABI copy,
or user Trait. HIR therefore carries the `CopyValue` responsibility identity
and a null Trait witness. The source remains live and the copied result owns no
new lifecycle obligation.

### Clone

`Clone` is a public behavioral Trait. Its selected requirement borrows the
source, returns one independent value of the exact same normalized type, never
suspends, and has a maximum public residue of `throws AllocationError effects
allocate`; a conformance may be strictly narrower. Selection produces exactly
one `TraitWitnessId`, normalized `ErrorSetId`, `EffectRowId`, result acquisition
plan, and cleanup plan. Failure leaves the source unchanged and publishes no
partial result. Runtime witness relookup is forbidden.

### DeepClone

`DeepClone` has a distinct identity. R1 records it so `deep` never falls back to
`Clone`, but keeps it nonactivatable until alias preservation, shared-subgraph
identity, cycle handling, graph traversal order, failure rollback, and cleanup
are closed. The same-type prototype derivation operator `!!` is not this Trait.

## HIR, API, and MIR residue

Every admitted fact creates a `ResponsibilityEvidenceDescriptor` containing
the canonical `ResponsibilityRuleId`, exact normalized `TypeId`, evidence kind,
registry revision, derivation digest, and optional `TraitWitnessId`. Clone-like
behavior additionally carries exact error/effect/result-acquisition/cleanup
identities. Concrete owner, region, and destination-domain identities stay in
value-level typed HIR/MIR; module API residue exports only the stable type-level
policy and witness identity.

Intrinsic evidence has no runtime object, vtable, dispatch, allocation, or
backend-specific meaning. MIR stores the same `ResponsibilityRuleId` and evidence
identity selected by typed HIR. Cranelift receives already-validated lowering;
it neither derives nor re-resolves responsibility evidence.

## Diagnostic order

1. Unknown, removed, stale, or wrong-domain name:
   `RESPONSIBILITY_IDENTITY_UNRESOLVED`.
2. Known identity whose exact derivation/conformance evidence is absent,
   stale, ambiguous, manually forged, or context-incompatible:
   `RESPONSIBILITY_EVIDENCE_NOT_ADMISSIBLE`.
3. A more specific existing Plain, borrow-region, lifecycle, authority,
   witness, or shared-wrapper diagnostic wins when its predicate branch is
   already known.

Diagnostics do not suggest that an annotation, wrapper, `unsafe` boundary, or
manual conformance can manufacture intrinsic evidence.

## Acceptance examples

Positive: the public spelling `Plain` for built-in `Int` resolves to the exact
internal `PlainValue` rule identity while independently carrying only the
responsibility facts registered for `Int`.

Boundary: a registered transferable resource can move across isolation only
with evidence bound to its exact owner and destination; this does not make the
resource Plain or Shareable.

Negative: `resource class File` cannot obtain Plain or Transferable from an
annotation, alias, wrapper, import, or direct conformance declaration. A stale
`Sendable` name resolves to no responsibility identity.

## Evidence boundary

This decision closes design-static identity, admission, residue, diagnostic,
and test obligations only. It does not execute a production parser, checker,
HIR/MIR lowerer, xVM, Cranelift backend, formatter, LSP, or conformance runner.
The global 22 feature P1 items and four M13 actions remain open and unchanged;
all 15 product lanes remain `NOT_RUN`.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
