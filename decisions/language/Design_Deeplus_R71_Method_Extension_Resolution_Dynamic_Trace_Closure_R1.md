# Deeplus R71 Method/Extension Resolution Dynamic Trace Closure R1

## 1. Decision

`method_extension_resolution_policy / DYNAMIC_LOWERING` changes from
`APPLICABLE_BLOCKED_BY_GAP(IR-XCUT-P1-054)` to `BOUND_DELEGATED`.

```text
delegate_feature_id: unified_call_expression_and_tilde_modes
authority_boundary: MIR_RUNTIME_AUTHORITY
product_execution: NOT_RUN
```

The method/extension feature retains ownership of activation, lookup domains,
candidate applicability, collision rejection, ambiguity, and exact extension
identity. After those static decisions produce one sealed `HirCallPlan`, dynamic
execution is already owned by the unified-call feature. R71 therefore delegates
only the dynamic cell; it neither changes a winner nor adds runtime dispatch.

## 2. Authority and baseline

| Item | Exact value |
|---|---|
| Canonical repository | `howork/Deeplus` |
| Canonical baseline | `39a5d50cc770341c4b9776d00d84520b780d0c62` |
| Local predecessor | `7babf6b0d6a3c806784ef052308cf7026f3fecb2` |
| Candidate status | `NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY` |
| Feature | `method_extension_resolution_policy` |
| Stage | `DYNAMIC_LOWERING` |
| Source activation | `none` |

## 3. Static owner and dynamic delegate

The ownership split is exact:

1. `method_extension_resolution_policy` computes nominal-member and active
   extension domains independently, applies the collision and ambiguity laws,
   and either rejects or selects exactly one terminal.
2. A selected extension terminal preserves exact `ExtensionSetId`,
   `ExtensionMemberId`, and `CallableImplementationId` identity in a resolved
   `CallPlan(mode_target_pair, call_head_id)`.
3. Ordinary extension execution delegates through
   `ORDINARY::EXTENSION_STATIC` and `HM-LR-CALL-004`.
4. Message extension execution delegates through
   `MESSAGE::EXTENSION_STATIC` and `HM-LR-CALL-008`.
5. Both rows evaluate the receiver once, perform `CONTEXT_ADAPT`, and terminate
   with `INVOKE`. The message row additionally preserves its existing reply
   correlation responsibility.
6. xVM, the runtime ABI, and Cranelift consume the sealed selected identity and
   never search by provider, extension-set name, selector string, import order,
   source order, address, or link order.

The trace overlay deliberately reuses the existing unified-call dynamic rule
`UCTC-R011` in `spec/contracts/unified-call-tilde-trace-closure-r1.json`.
`MERTC-R009` records why this feature delegates to that owner, while the reused
evidence identity avoids duplicating one canonical dynamic execution proof:

```text
EV-8612c9785d1ec77315d24c4f6700d39e07b38f8c115155f519c698e406770b5b
```

## 4. Preserved static and adjacent gaps

R71 does not alter or close:

- lexical activation or `use` rules;
- qualified-extension selector admission;
- ordinary nominal/extension collision or within-domain ambiguity;
- member, virtual, direct, Trait-witness, actor-transport, or reserved-operation
  call selection;
- boundary/reject conformance-test cells still blocked by their existing gaps;
- dynamic extension dispatch rejection;
- Trait witness construction or extension-to-conformance conversion;
- any feature P1, source activation, implementation, or product-support lane.

## 5. Acceptance binding

Ten design-static cases bind the boundary without claiming product execution.

| Case | Class | Obligation |
|---|---|---|
| `R71-MER-ACC-001` | positive | A preselected ordinary extension uses exact identity and `HM-LR-CALL-004`. |
| `R71-MER-ACC-002` | positive | A qualified extension selector uses its exact domain and the same ordinary lowering row. |
| `R71-MER-ACC-003` | positive | A preselected message extension uses exact identity and `HM-LR-CALL-008`. |
| `R71-MER-ACC-004` | boundary | Receiver and arguments are evaluated once before context adaptation and invocation. |
| `R71-MER-ACC-005` | boundary | Existing normal/error/defect/cancellation outcome and cleanup responsibilities are preserved. |
| `R71-MER-ACC-006` | reject | An applicable nominal member and active extension reject before HIR with selected count zero. |
| `R71-MER-ACC-007` | reject | Multiple applicable extensions reject without source/import-order winner. |
| `R71-MER-ACC-008` | reject | An inactive extension cannot be rescued by runtime lookup. |
| `R71-MER-ACC-009` | reject | Dynamic extension provider/selector dispatch is forbidden. |
| `R71-MER-ACC-010` | reject | An extension does not synthesize a Trait witness. |

Every case has execution state `DESIGN_STATIC_NOT_RUN`.

## 6. Projected trace result

Exactly one of 4,221 cells changes. The other 4,220 cells retain digest
`79510a1255de566d0dffe331717e2833b426ebc8ef871e07bce0d9a85e7a798a`.

| Metric | Predecessor | R71 projection |
|---|---:|---:|
| `BOUND_DIRECT` | 2,467 | 2,467 |
| `BOUND_DELEGATED` | 3 | 4 |
| `NOT_APPLICABLE` | 502 | 502 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,249 | 1,248 |
| Applied overlays | 16 | 17 |
| Overlay bindings | 132 | 133 |
| Evidence registry entries | 3,145 | 3,145 |

The post-overlay missing-cell and conflict-cell counts remain zero.

## 7. Governance guards

- semantic P0: `0`
- feature P1: `22_OPEN_UNCHANGED`
- M13 actions: `4_OPEN_UNCHANGED`
- product lanes: `15_OF_15_NOT_RUN`
- GitHub publication: `SUSPENDED`
- implementation claim: `NONE`
