# Design Deeplus HIR/MIR Machine Contract R1

Status: `CURRENT_USER_DELEGATED_DESIGN_ADOPTION`

- effective revision: `r51f3-current-hir-mir-machine-contract-r1`
- law ID: `DSGN-CURRENT-HIR-MIR-MACHINE-CONTRACT`
- feature ID: `hir_h1_current_mir_bridge_design`
- implementation-readiness gap: `IR-OWN-P0-015`
- production implementation: `NOT_STARTED`
- product lanes: `15/15 NOT_RUN`

## Decision

The Current Stable-design machine authorities are:

```text
deeplus.canonical-hir-h1/r1
deeplus.hir-h1-identity-catalog/r1
deeplus.mir/r1
deeplus.mir-machine-registry/r1
deeplus.hir-mir-lowering-row/r1
deeplus.hir-mir-lowering-registry/r1
deeplus.mir-capability-receipt/r1
deeplus.hir-mir-machine-contract-fixtures/r1
```

`Verified<CanonicalHirH1>` is fully typed, resolved, responsibility-closed,
and free of recovery or analysis-only nodes. `MirCapabilityReceiptR1` is
recomputed from reachable HIR lowering keys, the exact lowering registry, the
acyclic capability dependency graph, and independently resolved provider
evidence. A capability failure preserves the verified HIR and prevents only
`ExecutableHirH1`. Successful deterministic lowering produces
`Verified<DeeplusMirR1>`.

The closed machine counts are exactly 128 HIR identities, 102 Current lowering
rows, 111 rows at the explicit-Preview maximum, 29 MIR operations, 17
terminators, 12 linear token kinds, 11 ordered responsibility axes, 26 design
capabilities, and ten admitted call mode/target pairs. Lowering dispositions
are only `LOWER` and `NO_RUNTIME_EMISSION`.

## Diagnostic and checker boundary

R10 adds exactly five `release_verifier` diagnostics and zero source
diagnostics. `RECEIVER_MODE_MISMATCH` remains the exact source-diagnostic reuse
for `ACTOR_MESSAGE::VIRTUAL_SLOT`.
`RCTS_RESPONSIBILITY_AXIS_DROPPED` is reused only when an entire responsibility
axis is absent. `R10_HM_LOWERING_TARGET_UNKNOWN` owns both unknown target
vertices and dependency cycles, with `failure_detail=DEPENDENCY_CYCLE` for the
latter.

The R10 verifier is independent of the RCTS checker catalog. This adoption
creates no RCTS predicate, diagnostic-relation row, or generic
checker-predicate fixture.

## Nonactivation fence

This decision creates no source syntax, source-profile activation, canonical
HIR or MIR instance, provider capability receipt, production parser/checker/
HIR/MIR/xVM/runtime/Cranelift implementation, formatter or LSP support, feature
P1 closure, M13 closure, or product execution. `ProposedMirX1` remains a
noncanonical, nonactivatable compatibility target. The bridge keeps
`current_binding=false`, the exact 22 feature P1 remain OPEN, and all 15
product lanes remain `NOT_RUN`.

## Determinism

HIR, MIR, lowering, capability, and pair semantic projections use RFC 8949
deterministic CBOR with definite lengths, shortest encodings, deterministic
map-key order, preserved semantic-array order, and decode/re-encode byte
equality. This decision introduces no arbitrary digest or future commit
identity.
