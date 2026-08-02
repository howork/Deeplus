# Deeplus R41 Actor Protocol Direct Conformance Rebase

Baseline commit: `b6ff0f80d74e93bc7b25c54cfde08f8b40ca54e3`

Baseline tree: `6ffe1dccce5e8557244b316f129f9ddc9634c1c2`

Predecessor candidate commit: `2e511cede2e1bfca4a60aa124fc55b650f68ba30`

Verdict: `SEMANTIC_CANDIDATE_IMPLEMENTED_STATIC_VALIDATION`

## Decision

An actor conforms to an Actor Protocol only through an explicit direct header
relation and exactly one matching body-local conform block. A protocol `send`
requirement binds to one `on` handler, while a protocol `request` requirement
binds to one `request` handler. Matching is exact over selector, canonical
parameter shape, result type, normalized error set, and normalized effect row.

Structural inference, fallback, source or import order winners, runtime lookup,
VIA, AUTO, and specialization remain rejected. A successful binding preserves
`ActorProtocolConformanceId`, `ActorProtocolRequirementId`, and
`ActorProtocolBindingId`, plus `ActorHandlerId` for SEND or `ActorRequestId` for
REQUEST. The typed residue is consumed by `HM-LR-CALL-010`; no runtime selector
lookup is introduced.

One-way `send` and its `on` handler normalize to `throws Never`. A fallible
acknowledged command is expressed as a request returning `Unit`.

## Traceability

| Lane | Bound artifact |
|---|---|
| Source and grammar | `spec/grammar/deeplus.ebnf` |
| CST and AST disposition | `spec/contracts/grammar-production-disposition-registry-r1.json` |
| Static admission | `spec/contracts/actor-protocol-direct-conformance-r1.json` |
| Closed descriptor | `schemas/language/actor-protocol-direct-conformance-descriptor.schema.json` |
| Typed HIR identity | `spec/contracts/hir-h1-current-mir-bridge.json` |
| MIR lowering | `spec/contracts/hir-mir-lowering-registry.json#HM-LR-CALL-010` |
| Diagnostics | `spec/diagnostics/catalog/chunks/part-0029.json` and relation catalog |
| Acceptance and mutation | `tests/fixtures/current/actor-protocol-direct-conformance-r1.json` |
| Focused validator | `tools/validators/validate_actor_protocol_direct_conformance.py` |

## Gap transition candidate

The following gaps become eligible to move from `APPROVED_NOT_INTEGRATED` to
`INTEGRATED_UNVERIFIED` only after semantic PR merge and live-main readback:

- `IR-ACTOR-P0-001`
- `IR-ACTOR-P0-002`
- `IR-ACTOR-P0-004`
- `IR-ACTOR-P1-003`

They become `VERIFIED_CLOSED` only after the separate publication-closure PR is
merged and its live-main commit and tree are read back.

## Executed static evidence

- focused Actor Protocol validation: 10 semantic checks, 11 predicate fixtures,
  26 acceptance cases, 10 mutation oracles, and 9 diagnostics: `PASS`
- R5 bounded successor compatibility: 13/13: `PASS`
- R9 diagnostic dispatch compatibility: 9/9: `PASS`
- HIR/MIR machine contract: 129 identities and 111 lowering rows: `PASS`
- R27 grammar topology: 643/643 bindings and 6/6 rejected mutations: `PASS`

The final workspace and GitHub CI receipts are bound by the semantic PR and the
publication-closure receipt rather than predicted here.

## Preserved governance

- semantic P0: `0`
- canonical feature P1: exactly `22 OPEN`
- closed or new feature P1: `0 / 0`
- M13 actions: exactly `4 OPEN`
- product lanes: `15/15 NOT_RUN`
- production parser, checker, MIR/xVM, runtime, Cranelift, formatter, and LSP:
  `NOT_RUN`
- current binding: `false`

