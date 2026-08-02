# Design Deeplus R23 Actor Protocol Binding Descriptor Publication Closure R1

## 1. Closure candidate verdict

`READY_FOR_PUBLICATION_CLOSURE_MERGE`

R23 canonically integrates the closed cross-module binding descriptor for the
already canonical R41 direct Actor Protocol conformance contract. The semantic
PR preserves the R41 stable binding identity, adds a content digest and
receipt-bound module/executable projection, and introduces no source spelling,
grammar production, or final diagnostic ID.

`IR-ACTOR-P1-006` becomes `VERIFIED_CLOSED` only after this separate closure
PR is merged and the resulting GitHub `main` commit and tree are read back.
This is implementation-readiness specification closure, not production
compiler, linker, loader, MIR/xVM, runtime, Cranelift, formatter, LSP, or
product execution.

## 2. Exact semantic publication identity

| Field | Value |
|---|---|
| repository | `https://github.com/howork/Deeplus.git` |
| promotion cycle | `R43 / R23 rebase` |
| semantic PR | `#61` |
| semantic branch | `codex/r43-actor-protocol-binding-rebase` |
| semantic source commit | `212dd8c0b8ac1541d89ec0f8d4f555fc04fe00c6` |
| semantic merge commit | `b4a4ff8fa183c65577b18e6b7001c4ccab52befa` |
| semantic merge tree | `bf273631afecdbe68e86a264d0e1a01e27229fe7` |
| previous publication baseline | `53bbc11cf4b4b5980ae07c04f97a41d7bdd12012` |
| merged at | `2026-08-02T04:53:26Z` |

The merge parents are the previous publication baseline and exact semantic
source commit. The publication-closure commit is intentionally not predicted.

## 3. Semantic repair and evidence

The historical local R23 candidate made `ActorProtocolBindingId` depend on
mutable implementation content. Canonical R41 instead fixes the ID to
`(ActorProtocolConformanceId, ActorProtocolRequirementId)`. The rebased
candidate preserves that slot ID and changes the row/table digests on a
content-only rebind.

Bound static evidence:

- focused R23 descriptor validation: `55/55 PASS`
- legacy R4 module mutation suite: `73/73 REJECTED`, baseline PASS
- generator idempotence: PASS
- full workspace validator: `6129/6129 PASS`
- source-tree manifest: 729 files, tree digest
  `4c6a2e9ee6ca8193e96d796a7b509c57ea03a99bcac3600e711657bf14ec0107`
- semantic PR GitHub CI: Canonical integrity and Rust workspace SUCCESS
- semantic merge `main` CI: Canonical integrity and Rust workspace SUCCESS

No product execution or support is inferred from static validation or CI.

## 4. Projection boundary

- the new `R41_ACTOR_PROTOCOL_BINDINGS` profile requires a present module API
  table field; `[]` is the sole empty encoding
- legacy R4 artifact bytes remain accepted under the legacy profile
- module API is the exact byte-identical common/public filter of the complete
  implementation table set
- executable projection is owned by `ExecutableImageId` and every table is
  covered by one declaring package/module origin receipt
- MIR preserves the complete R41 tuple plus table and row digest
- runtime lookup, fallback, registration-order selection, and R22 lifecycle
  generation are absent

## 5. Gap and governance transition

The exact closure set is only `IR-ACTOR-P1-006`. It moved to
`INTEGRATED_UNVERIFIED` at semantic merge and becomes `VERIFIED_CLOSED` only
after closure merge readback.

- semantic P0: `0`
- canonical feature P1: exactly `22 OPEN`
- M13 actions: exactly `4 OPEN`
- product lanes: `15/15 NOT_RUN`
- source syntax / grammar production / new final diagnostic ID: `0 / 0 / 0`

## 6. Pointer and next baseline

The semantic publication target is
`b4a4ff8fa183c65577b18e6b7001c4ccab52befa`. The canonical revision becomes
`r51f3-current-actor-protocol-binding-descriptor-r1`. The closure merge SHA is
recorded only by external post-merge readback. The next cluster starts from
that closure SHA; it does not stack unpublished R22 bytes implicitly.
