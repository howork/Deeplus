# Deeplus R23 Actor Protocol Binding Descriptor Rebase

Baseline commit: `53bbc11cf4b4b5980ae07c04f97a41d7bdd12012`

Baseline tree: `3c9b282149489630df73736a2800530b8135aa13`

Predecessor local candidate: `R23-LOCAL-CANONICAL-PROJECTION-FREEZE-R1` at `3f0077dd8f021718dc87b3b239f417e5d3f770a6`

Verdict: `SEMANTIC_CANDIDATE_IMPLEMENTED_STATIC_VALIDATION`

## Decision

R23 closes the static cross-module residue for canonical R41 direct Actor
Protocol conformance. Each exact R41 conformance owns one finite binding table
for `(ActorId, ActorProtocolId, SubstitutionId:empty, AuthorityId)`. The
`ActorProtocolBindingId` remains the stable requirement-slot identity keyed
only by `(ActorProtocolConformanceId, ActorProtocolRequirementId)`. The old
local candidate's content-sensitive definition is superseded: an implementation
or contract rebind preserves the binding ID and changes the row and table
digests.

The current profile serializes only static Actor declaration identities and
the empty substitution. Typed HIR supplies the complete R41 conformance,
requirement, binding, typed handler-or-request, responsibility, contract, and
compatibility-proof residue. MIR adds `ActorProtocolBindingTableId` without
erasing that tuple. Runtime lookup, fallback, registration order, and
reselection remain zero.

## Artifact profile and projection law

`R41_ACTOR_PROTOCOL_BINDINGS` is an explicit successor artifact profile. It
requires the module API table field, the module implementation table-set
digest, and the compilation-receipt binding. Legacy R4 artifacts remain valid
without these fields; the format change is not silently applied under the old
profile.

The API projection is the exact byte-identical `common`/`public` filter of the
complete implementation table set, and present `[]` is the only empty encoding
in the new profile. `common` remains same-package only. Executable projection
is owned by `ExecutableImageId`; every table is covered by exactly one
declaring package/module origin receipt.

## Failure and responsibility axes

- `SEND_TO_ON` has an empty implementation ErrorSet and no reply
  responsibility digest.
- `REQUEST_TO_REQUEST` preserves exact `ResponsibilityId` and static
  `ReplyResponsibility` digest.
- admission errors remain outside handler ErrorSet;
  Cancellation and Defect remain separate axes.
- concrete `ReplyId`, `CorrelationId`, and runtime Actor instance identities
  never enter module API binding rows.

## Traceability

| Lane | Bound artifact |
|---|---|
| R41 source selection | `spec/contracts/actor-protocol-direct-conformance-r1.json` |
| Frontend identity | `spec/frontend/frontend-model.json` |
| Closed descriptor | `spec/contracts/actor-protocol-binding-descriptor.json` |
| Descriptor schema | `schemas/language/actor-protocol-binding-table.schema.json` |
| Module API profile | `schemas/language/module-api-digest.schema.json` |
| Implementation and receipt | `schemas/language/module-implementation-digest.schema.json`, `schemas/language/module-compilation-receipt.schema.json` |
| MIR residue | `schemas/language/mir-responsibility.schema.json`, `spec/mir/semantics.md` |
| Static fixture | `tests/fixtures/current/actor-protocol-binding-table-r1.json` |
| Generator | `tools/generators/bind_actor_protocol_binding_tables.py` |
| Focused validation | `tools/validators/validate_actor_protocol_binding_descriptors.py` |

## Acceptance

- exact baseline and controlling R41 binding-key parity
- stable TableId and BindingId across a content-only rebind
- changed row/table digest for that rebind
- one typed-HIR proof and one MIR selection per serialized requirement
- exact API/implementation visibility-filter relation
- module owner versus executable-image owner separation
- one receipt-bound origin per executable table
- zero runtime lookup, fallback, and order winners
- rejection of stale digest, missing row, wrong reply axis, concrete ReplyId
  leakage, and wrong executable owner
- no R22 byte contribution and no R24 implementation scope absorption

## Gap transition candidate

`IR-ACTOR-P1-006` becomes eligible for `INTEGRATED_UNVERIFIED` only after the
semantic PR is merged and live main is read back. It becomes
`VERIFIED_CLOSED` only after the separate publication-closure PR is merged and
its live-main commit and tree are read back.

## Preserved governance

- semantic P0: `0`
- canonical feature P1: exactly `22 OPEN`
- M13 actions: exactly `4 OPEN`
- product lanes: `15/15 NOT_RUN`
- production compiler, linker, loader, MIR/xVM, runtime, Cranelift, formatter,
  and LSP: `NOT_RUN`
- local R22 lifecycle candidate: not stacked
- source syntax and diagnostic catalog changes: `0 / 0`
