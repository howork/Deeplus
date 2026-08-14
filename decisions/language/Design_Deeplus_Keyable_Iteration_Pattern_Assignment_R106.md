# Deeplus R106 — Keyable, Iteration, and Local Pattern Assignment Closure

## Verdict

`LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF`

R106 closes three implementation-readiness gaps without adding syntax:

1. deterministic Keyable witness and hash-policy selection;
2. deterministic synchronous `for` source and Iterator plan selection;
3. failure-atomic local structural Pattern assignment.

The exact predecessor is
`cc16fdd33112394861adea38846b40ae3373fb4b`. This document and the machine
contract are local successor material. They do not claim current GitHub
integration or production parser/checker/runtime support.

## Controlling machine artifacts

- `spec/contracts/keyable-iteration-pattern-assignment-r106.json`
- `schemas/language/keyable-iteration-pattern-assignment-r106.schema.json`
- `tests/fixtures/current/keyable-iteration-pattern-assignment-r106.json`
- `schemas/language/keyable-iteration-pattern-assignment-fixtures-r106.schema.json`
- `tools/validators/validate_keyable_iteration_pattern_assignment_r106.py`

## Closed decisions

### KeyableSelectionV1

The checker normalizes one key type and selects exactly one direct-global
family containing strong `Eq<Self>`, stable `Hash<Self>`, `Keyable`, and one
`HashPolicyId`. Eq must be an equivalence relation and must imply hash
congruence. Equality and hashing borrow without consumption, mutation,
allocation, suspension, cancellation, authority, Error, or Effect residue.

Float and floating Complex domains, mutable/lifecycle identities, partial
equality, provider lookup, reflection, and per-instance policies reject before
collection planning. Accepted HIR seals `KeyableWitnessId`, `EqWitnessId`,
`HashWitnessId`, and `HashPolicyId`.

### ForIteratorPlanV1

The source evaluates exactly once. Route precedence is
`DIRECT_ITERATOR`, then `SEQUENCE_ACQUIRE`, then rejection. The checker seals
the exact Sequence conformance when used, Iterator conformance and witness,
associated `Item`, Pattern policy, and cleanup plan. Current `next` is
synchronous, returns `Option<Item>`, `throws Never`, and has `effects state`.

Bare `for` requires an irrefutable Pattern. `for let` mismatch or a false pure
Bool guard skips only the current candidate. Every control, failure, Defect,
and cancellation exit reverse-cleans the current item, iterator, and source.
No source-order, provider, or runtime fallback exists.

### LocalPatternAssignmentV1

`PatternAssignmentStmt` and the bare-comma `ParallelAssignmentStmt` normalize
to one plan. Tuple, statically irrefutable List, Record, pattern-transparent
nominal Record shape, and bare-comma Tuple sugar are admitted. Every
non-wildcard leaf and rest capture must resolve to an existing distinct mutable
direct `LocalPlaceId`; assignment never declares a binding.

The RHS evaluates once. Ordered projections and replacement reservations stage
with zero target writes. One infallible callback-free
`PatternAssignmentCommitId` publishes the replacements, after which displaced
owners clean in reverse target order. Overlapping, member, index, property,
shared, actor, FFI, or otherwise potentially aliasing targets reject.

## Surface consistency migration

Map ownership now uses one owner-bounded prefix convention:

- Map literal unfold: `*expr`
- Map Pattern ignore residual: `*_`
- Map Pattern capture residual: `*name`
- Record/static-named residual: `_**` or `name**`

The former Map Pattern spellings `.._` and `..name` are removed from the
current contract. List positional rest remains the suffix `name..`/`_..`; the
two owner domains are not conflated.

## Traceability

| Surface | Checker predicate | HIR residue | MIR obligation | Primary diagnostic |
|---|---|---|---|---|
| Map/Set key | `KeyableAdmissible` | Keyable/Eq/Hash/policy IDs | use sealed family only | `TYPE_KEY_REQUIRES_KEYABLE` |
| synchronous `for` | `ForSourceIterableAdmitted` | `ForIteratorPlanId`, Item and cleanup IDs | exact route and reverse cleanup | `FOR_SOURCE_NOT_ITERABLE` |
| structural local assignment | `LocalGroupAssignmentAdmitted` | plan/place/commit/cleanup IDs | zero-write staging and one commit | `PATTERN_ASSIGNMENT_REQUIRES_EXISTING_VAR` |

## Acceptance

The fixture contains exactly 24 cases: 8 positive, 7 boundary, and 9 reject.
The validator also executes 12 bounded mutations covering algorithm identity,
route order, partial-equality admission, suspension, surface ownership, Map
rest spelling, fixture cardinality/identity, predicate emission, feature
production binding, and product-support overclaim.

```powershell
py -3 tools/validators/validate_keyable_iteration_pattern_assignment_r106.py --root . --mutations
```

Expected result: `PASS`, with `12/12` mutation rejections.

## Governance fence

- semantic P0: `0`
- feature P1: exact existing `22 OPEN`, unchanged
- new/closed feature P1: `0/0`
- product lanes: `15/15 NOT_RUN`
- production checker/runtime: `NOT_RUN`
- source syntax added: `0`
- GitHub mutation: `0`

Static contract validation is implementation handoff evidence, not product
conformance or activation evidence.
