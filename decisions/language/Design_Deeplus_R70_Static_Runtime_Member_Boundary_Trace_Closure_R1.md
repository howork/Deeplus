# Deeplus R70 Static/Runtime Member Boundary Trace Closure R1

## 1. Decision

`static_runtime_member_boundary_law / DYNAMIC_LOWERING` changes from
`APPLICABLE_BLOCKED_BY_GAP` to `NOT_APPLICABLE`.

```text
reason_code: NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR
authority_boundary: MIR_RUNTIME_AUTHORITY
product_execution: NOT_RUN
```

This is a design-static trace closure. It does not add syntax, an HIR identity,
a MIR operation, a runtime module object, or product implementation evidence.

## 2. Authority and baseline

| Item | Exact value |
|---|---|
| Canonical repository | `howork/Deeplus` |
| Canonical baseline | `39a5d50cc770341c4b9776d00d84520b780d0c62` |
| Local predecessor | `29059c1b23de7d32398f582d2a37d5ce24d31341` |
| Candidate status | `NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY` |
| Feature | `static_runtime_member_boundary_law` |
| Stage | `DYNAMIC_LOWERING` |
| Source activation | `none` |

The canonical feature row remains the language-design authority. The R70
overlay supplies only the missing trace disposition and its static proof. The
MIR/runtime boundary is authoritative for the conclusion that no new dynamic
behavior is admitted.

## 3. Static-boundary proof

The qualified module/static path is resolved before runtime lowering:

1. A module import target is a resolver `ModuleId`; it is not an expression
   value and is not materialized as an HIR runtime object.
2. A successful qualified selection erases the module qualifier and retains
   the selected declaration identity or the already-defined call plan.
3. When the selected declaration is used as a value, existing
   `ResolvedRef::DirectDecl(DeclId)` lowering supplies the existing
   `STATIC_REF` route.
4. When the selected declaration is called, the existing `CallExpr` route is
   used. R70 adds neither dispatch nor lookup behavior.
5. Invalid module-as-value, wrong-separator, and same-frame collision cases
   are rejected before typed HIR/MIR commitment. Runtime lookup cannot rescue
   them.

The direct evidence pointer is:

```text
spec/contracts/hir-h1-current-mir-bridge.json
JSON pointer: /name_resolution_module_bridge
computed evidence identity:
EV-8ab19e684aca7aeae5d3a2c0f9418ff5db42f41bb9f061af7e580d51d3a7c3aa
```

The conclusion is therefore narrowly `NOT_APPLICABLE`: static resolution
selects or rejects the target, while existing selected-declaration lowering
continues unchanged.

## 4. Adjacent-cell fence

R70 does not reinterpret or transition any adjacent trace cell.

- Ordinary dot member access remains value-receiver access and continues to
  use its existing `PLACE_ACCESS`/`PLACE_LOAD` or `CallExpr` lowering.
- Existing `double_colon` cells remain unchanged.
- Existing `method_extension` cells remain unchanged.
- A module name does not become a runtime value or module object.
- No runtime or backend re-lookup, fallback, or re-selection is admitted.
- No new syntax, declaration identity, P1, activation, or product-support
  claim is created.

## 5. Acceptance binding

The single trace acceptance record binds the nine design-static cases
`R70-SRMB-ACC-001` through `R70-SRMB-ACC-009` from
`spec/contracts/static-runtime-member-boundary-trace-closure-r1.json`.

| Case | Class | Bound obligation |
|---|---|---|
| `R70-SRMB-ACC-001` | positive | `Type::value` selects a terminal declaration and hands off an existing `DirectDecl` projection. |
| `R70-SRMB-ACC-002` | positive | `Type::make(argument)` hands off the existing direct `CallPlan`. |
| `R70-SRMB-ACC-003` | positive | An explicit runtime owner using dot remains under the separate existing `PlacePlan` or `CallPlan` owner. |
| `R70-SRMB-ACC-004` | boundary | `<T as Trait>::Assoc::member` emits no operation for the associated type before nominal type-side selection. |
| `R70-SRMB-ACC-005` | boundary | Ordinary-dot direct, virtual, and extension-static routes are preselected through their existing lowering rows. |
| `R70-SRMB-ACC-006` | reject | A module/static qualifier used as a runtime value is rejected before expression HIR. |
| `R70-SRMB-ACC-007` | reject | A dotted type-side call is rejected; it is not reinterpreted as static selection. |
| `R70-SRMB-ACC-008` | reject | An unresolved `Type::missing` terminal is rejected without runtime fallback. |
| `R70-SRMB-ACC-009` | reject | A static alias/local collision is rejected before HIR; declaration order is not a winner. |

These cases cover the successful qualified declaration/call projections, the
ordinary-dot boundary, and pre-HIR rejection boundaries without claiming that
a parser, checker, MIR, xVM, runtime, backend, formatter, or LSP was executed.

Every case therefore has execution state `DESIGN_STATIC_NOT_RUN` and supports
only this trace-classification decision.

## 6. Projected trace result

Exactly one of 4,221 trace cells changes. The other 4,220 cells retain digest
`a6a56943d6b8b51c177b4ff282ef3db50dcc3f85a950495d80553d4c552bec35`.

| Metric | Predecessor | R70 projection |
|---|---:|---:|
| `BOUND_DIRECT` | 2,467 | 2,467 |
| `BOUND_DELEGATED` | 3 | 3 |
| `NOT_APPLICABLE` | 501 | 502 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,250 | 1,249 |
| Applied overlays | 15 | 16 |
| Overlay bindings | 131 | 132 |
| Evidence registry entries | 3,144 | 3,145 |

The post-overlay missing-cell and conflict-cell counts remain zero.

## 7. Governance guards

- semantic P0: `0`
- feature P1: `22_OPEN_UNCHANGED`
- M13 actions: `4_OPEN_UNCHANGED`
- product lanes: `15_OF_15_NOT_RUN`
- GitHub publication: `SUSPENDED`
- implementation claim: `NONE`

R70 closes only one traceability gap cell. It does not close or create a
language feature P1 and does not establish product implementation support.
