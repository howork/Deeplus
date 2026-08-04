# Design Deeplus R75 Actor Cranelift Projection Rebase Publication Closure R1

## 1. Closure candidate verdict

`READY_FOR_PUBLICATION_CLOSURE_MERGE`

Semantic PR #69 canonically integrates the exact R75 Actor-to-Cranelift
projection candidate. The publication unit becomes `VERIFIED_CLOSED` only
after this separate publication-closure PR is merged and the resulting GitHub
`main` commit and tree are read back.

This closure adds no source syntax or production implementation. It records
design/static evidence at E2. Parser, checker, HIR/MIR, xVM, runtime,
Cranelift Object AOT/JIT, formatter/LSP, independent conformance, and product
execution remain `NOT_RUN`.

## 2. Exact semantic publication identity

| Field | Value |
|---|---|
| repository | `https://github.com/howork/Deeplus.git` |
| publication unit | `R75_ACTOR_CRANELIFT_PROJECTION_REBASE` |
| semantic PR | `#69` |
| semantic branch | `codex/r75-actor-cranelift-projection-rebase` |
| semantic source commit | `d0e3f459b55f4eeb9bf884ccf982d90602f0d2b7` |
| semantic merge commit | `420ccdcbe9dae1b267d9fa0277239195f0d72d1b` |
| semantic source/merge tree | `2c3b690cee13a28f89130728c5a8d0d9d39cccc9` |
| previous publication baseline | `c016871d5aa1c7515fd8a8df181744916f1e1849` |
| merged at | `2026-08-04T02:26:58Z` |

The publication-closure commit is intentionally not predicted.

## 3. Canonical projection contract

R75 preserves Deeplus MIR as the sole execution-semantic authority and binds
only the deterministic target projection into the current Cranelift contract.
`ActorCodeGenerationId` derives from the complete current base receipt, the
loader-verified `ExecutableImageId`, Actor Protocol binding table-set digest,
the sorted binding-row digest set, and origin-coverage digest. Source/import/
link order, runtime addresses, symbols, and enumeration order are excluded.

Generation lifetime is proven by replaying unique ordered lease events, not by
aggregate owner counts. Actor requests retain their generation through
terminal cleanup; caller Reply continuations own independent leases; one-way
SEND creates no Reply lease. JIT retirement requires unpublished state plus
zero exact leases, executing frames, and code-metadata users. Object AOT uses
image-unload or process lifetime and does not invent per-generation physical
retirement.

Managed-reference capability remains fail-closed. Missing or invalid root,
safepoint, callback, suspended-frame, or cleanup evidence blocks native
lowering; raw-pointer fallback is forbidden. Error, Defect, Cancellation,
suspension, cleanup, enqueue commitment, ActorTurn, and Reply terminality remain
selected Deeplus MIR outcomes rather than host-unwind or backend-trap policy.

## 4. Traceability snapshot

| Metric | Exact value |
|---|---:|
| target features | 469 |
| stage cells | 3,283 |
| test outcome cells | 1,407 |
| `BOUND_DIRECT` | 2,473 |
| `BOUND_DELEGATED` | 4 |
| `NOT_APPLICABLE` | 502 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,242 |
| evidence overlays | 20 |
| evidence bindings | 139 |
| evidence registry entries | 3,151 |

Exactly the Dynamic Lowering cells for `actor_mailbox_capacity`,
`actor_minimum_lifecycle_r1`, and `actor_request_reply` transition from blocked
to direct binding. No other trace cell changes.

## 5. Gap disposition

After this closure PR is merged and live-main readback succeeds,
`IR-ACTOR-P1-007` becomes `VERIFIED_CLOSED` at design/static evidence level E2.
`IR-ACTOR-P2-008` remains `EXPLICITLY_DEFERRED`. The umbrella trace gap
`IR-XCUT-P1-054` remains OPEN because 1,242 cells are still
`APPLICABLE_BLOCKED_BY_GAP`. No canonical feature P1 is closed or created.

## 6. Executed evidence

- focused R75 validation: 56 checks, 30 acceptance cases, 16 deterministic
  mutation controls, `PASS`
- full workspace validation: 7,705/7,705, `PASS`
- semantic PR Canonical integrity: run `30871351203`, job `91873833235`,
  `SUCCESS`
- semantic PR Rust workspace: run `30871351205`, job `91873833438`,
  `SUCCESS`
- semantic-merge `main` Rust workspace: run `30871815313`, job
  `91875190168`, `SUCCESS`
- semantic-merge `main` Canonical integrity: run `30871815342`, job
  `91875190265`, `SUCCESS`
- semantic source manifest: 1,017 files, 29,932,891 bytes, tree SHA-256
  `101f245aeecc4b96527a51757cbb284a26245d9cab1bb6c1fe3d6b7c045e73de`

Git commit/tree SHA-1 identities and source-manifest SHA-256 byte identities
remain separate hash domains. Repository tooling and CI do not prove product
execution.

## 7. Pointer and authority binding

The semantic publication target is
`420ccdcbe9dae1b267d9fa0277239195f0d72d1b`. The canonical revision is
`r51f3-current-actor-cranelift-projection-r75-r1`. The closure PR merge commit
is recorded only in the external post-merge readback receipt. Self-binding
remains forbidden, `current_binding` remains `false`, and `source_snapshot`
remains `null`.

## 8. Preserved guards

- semantic P0: `0`
- canonical feature P1: exactly `22 OPEN`
- M13 actions: exactly `4 OPEN`
- product lanes: `15/15 NOT_RUN`
- production implementation: `NOT_RUN`
- new or closed feature P1: `0 / 0`

## 9. Next checkpoint

After closure merge and live-main readback, the next cluster must start from
that exact closure SHA. The remaining global trace gap is not closed by this
bounded Actor projection publication.
