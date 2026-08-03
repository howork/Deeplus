# Deeplus R74 Member/Extension Collision Diagnostic Trace Closure R1

## 1. Decision

R74 corrects one stale canonical feature-catalog reference and the one trace
cell derived from it:

| Item | Predecessor | R74 |
|---|---|---|
| `normative_trace_refs.diagnostics` | `[]` | `["MEMBER_EXTENSION_COLLISION"]` |
| `member_extension_collision_error_policy / DIAGNOSTICS` | `NOT_APPLICABLE` | `BOUND_DIRECT` |

The predecessor rationale claimed that the feature declared no distinct
rejection condition. That is false: `MemberExtensionCollisionRejected` emits
the active checker error `MEMBER_EXTENSION_COLLISION` as its sole primary.
R74 repairs the false empty forward reference rather than masking it with an
additional evidence overlay.

## 2. Authority and baseline

| Item | Exact value |
|---|---|
| Canonical repository | `howork/Deeplus` |
| Canonical baseline | `39a5d50cc770341c4b9776d00d84520b780d0c62` |
| Local predecessor | `f6581b6fba8f0f48e8b3ac2ea893298e7713d51d` |
| Candidate status | `NONCANONICAL_LOCAL_CANONICAL_METADATA_CORRECTION` |
| Feature | `member_extension_collision_error_policy` |
| Stage | `DIAGNOSTICS` |
| Evidence level | `E2_STRUCTURED_STATIC` |
| Product execution | `NOT_RUN` |

The controlling authorities are the current feature catalog, the checker
predicate registry, the active diagnostic catalog and relation registry, the
frontend collision contract, and the R72 static collision contract. R73
records the stale cell and bounds R74 to this correction.

## 3. Exact evidence binding

The generated trace binds directly to the existing identities:

```text
EV-55d02c2cea739b77d7d95070b34e6b350f4aa3b3c0b838597263a576b85115fa
  DIAGNOSTIC_REGISTRY_ID
  spec/diagnostics/catalog
  MEMBER_EXTENSION_COLLISION

EV-c3f43ca9fc5692e6da578ae1a0701cc340951ff85144c9263e69c60a0d358bb4
  FEATURE_REGISTRY_ROW
  spec/features/catalog/chunks/part-0009.json#/18
  member_extension_collision_error_policy
```

No new diagnostic ID, predicate, semantic contract, fixture, source surface,
or evidence-registry identity is created. The diagnostic catalog's reverse
`feature_refs` remains owned by its shared resolution-policy registration and
is not treated as an exhaustive inverse index.

## 4. Semantic preservation

The existing rule is unchanged. For an ordinary selector, nominal-member and
active-extension applicability remain separate domains. If both are nonempty,
the checker emits `MEMBER_EXTENSION_COLLISION`, commits no selected candidate,
and admits no HIR. Exact qualified extension selection still restricts the
domain before the cross-domain collision test. R72 dynamic rejection and R73
boundary/reject acceptance partitions are unchanged.

R74 therefore changes trace truth, not language syntax, typing, resolution,
lowering, runtime behavior, recovery, diagnostic wording, or product support.

## 5. Preservation and projected trace

Exactly the named diagnostic cell transitions. The other 4,220 atomic cells
retain digest:

```text
0f134da58b8045ad157b08b5a3eb7ce32509716eb7ab95fd67ce3e551299d827
```

| Metric | Predecessor | R74 projection |
|---|---:|---:|
| `BOUND_DIRECT` | 2,469 | 2,470 |
| `BOUND_DELEGATED` | 4 | 4 |
| `NOT_APPLICABLE` | 503 | 502 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,245 | 1,245 |
| Applied overlays | 19 | 19 |
| Overlay bindings | 136 | 136 |
| Evidence registry entries | 3,148 | 3,148 |

## 6. Acceptance gates

- the feature row names exactly `MEMBER_EXTENSION_COLLISION` in its diagnostic
  forward references;
- the predecessor cell is exactly the stale `NOT_APPLICABLE` disposition;
- the generated successor cell is exactly `BOUND_DIRECT` with the two existing
  evidence references and no N/A, delegation, or blocked-gap payload;
- the predicate retains the same sole primary and no secondary diagnostic;
- the diagnostic remains an active `error` at the checker stage in the source
  emission domain;
- R72 and R73 contracts remain unchanged;
- the exact non-target digest and projected counts hold;
- focused normal validation, 14 bounded mutations, global trace validation,
  current-integrity verification, source-manifest verification, and workspace
  validation pass.

## 7. Governance guards

- semantic P0: `0`
- feature P1: `22_OPEN_UNCHANGED`
- M13 actions: `4_OPEN_UNCHANGED`
- product lanes: `15_OF_15_NOT_RUN`
- product execution receipts: `0`
- new syntax, AST, semantic, HIR, MIR, xVM, runtime, backend, or diagnostic
  identity: `0`
- GitHub publication during local freeze: `SUSPENDED`
- implementation claim: `NONE`
