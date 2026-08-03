# Deeplus R72 Member/Extension Collision Dynamic Trace Closure R1

## 1. Decision

`member_extension_collision_error_policy / DYNAMIC_LOWERING` changes from
`APPLICABLE_BLOCKED_BY_GAP(IR-XCUT-P1-054)` to `NOT_APPLICABLE`.

```text
reason_code: NA_DYNAMIC_REJECTED_BEFORE_LOWERING
authority_boundary: MIR_RUNTIME_AUTHORITY
product_execution: NOT_RUN
```

This feature owns one static cross-domain rejection law. For an ordinary
selector, nonempty applicable nominal-member and active-extension domains
reject with `MEMBER_EXTENSION_COLLISION`, commit `selected_count = 0`, and
produce no admitted HIR. Consequently there is no feature-specific MIR, xVM,
runtime-ABI, or Cranelift behavior to bind.

## 2. Authority and baseline

| Item | Exact value |
|---|---|
| Canonical repository | `howork/Deeplus` |
| Canonical baseline | `39a5d50cc770341c4b9776d00d84520b780d0c62` |
| Local predecessor | `d54633b10c1b92bcd2445afc9906ecf9bafec5c9` |
| Candidate status | `NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY` |
| Feature | `member_extension_collision_error_policy` |
| Stage | `DYNAMIC_LOWERING` |
| Source activation | `none` |

## 3. Static terminal boundary

The collision law is evaluated after applicability has produced two distinct
sets but before any within-domain ranking:

1. If either applicable set is empty, the predicate admits and leaves the
   applicable domain's winner to its existing owner.
2. An exact qualified-extension selector restricts lookup to its named
   extension domain before the cross-domain predicate and therefore bypasses
   only this collision test.
3. If both sets are nonempty, neither set is ranked. The checker emits the sole
   active primary `MEMBER_EXTENSION_COLLISION`, records `selected_count = 0`,
   and creates no selected member, `HirCallPlan`, recovery HIR, or runtime
   fallback.

This cluster does not choose a generic substitution, overload winner,
applicability rank, specificity winner, or expected-type-directed result.

## 4. Diagnostic ordering

`MEMBER_EXTENSION_COLLISION` remains the exact-owner primary. It precedes a
same-stage generic fallback, and the retired
`EXTENSION_SHADOWED_BY_MEMBER_COMPAT` and
`STABLE_MEMBER_EXTENSION_COLLISION` identities remain nonemitting. A collision
also precedes any within-domain ambiguity ranking: even if one nonempty domain
contains multiple applicable candidates, the cross-domain collision still
terminates the ordinary selector with selected count zero.

## 5. R71 preservation and runtime fence

R71 remains unchanged. A call for which static resolution has already selected
one extension terminal still delegates its dynamic execution through the
unified-call contract. R72 covers only the rejected cross-domain branch and
does not alter `HM-LR-CALL-004`, `HM-LR-CALL-008`, call evaluation order,
outcome projection, or cleanup ownership.

The rejected branch has exactly zero:

- admitted HIR nodes and selected call plans;
- MIR operations and terminators;
- xVM instructions or selector payloads;
- runtime helper calls or provider lookup;
- backend instructions, reselection, or address/link-order winners.

## 6. Acceptance binding

Nine design-static cases bind the boundary without claiming product execution.

| Case | Class | Obligation |
|---|---|---|
| `R72-MECD-ACC-001` | positive | Only the nominal domain is nonempty; collision admits and winner selection stays outside R72. |
| `R72-MECD-ACC-002` | positive | Only the active-extension domain is nonempty; collision admits and winner selection stays outside R72. |
| `R72-MECD-ACC-003` | boundary | Exact qualification restricts the extension domain and bypasses only the cross-domain collision. |
| `R72-MECD-ACC-004` | boundary | Source, import, use, nesting, address, and link order are never collision winners. |
| `R72-MECD-ACC-005` | boundary | The exact collision primary precedes a same-stage generic fallback. |
| `R72-MECD-ACC-006` | reject | One applicable candidate in each domain rejects with selected count zero before HIR. |
| `R72-MECD-ACC-007` | reject | Multiple candidates in one domain cannot cause ranking that escapes a nonempty cross-domain collision. |
| `R72-MECD-ACC-008` | reject | Recovery cannot manufacture an admitted call plan or runtime fallback. |
| `R72-MECD-ACC-009` | reject | MIR, xVM, runtime, and Cranelift cannot reselect the rejected call. |

Every case has execution state `DESIGN_STATIC_NOT_RUN`.

## 7. Projected trace result

Exactly one of 4,221 cells changes. The other 4,220 cells retain digest
`3cdbe4a509df453151f7e4900610acf2acbb6dfe0a8734f52e375a86082299e2`.

| Metric | Predecessor | R72 projection |
|---|---:|---:|
| `BOUND_DIRECT` | 2,467 | 2,467 |
| `BOUND_DELEGATED` | 4 | 4 |
| `NOT_APPLICABLE` | 502 | 503 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,248 | 1,247 |
| Applied overlays | 17 | 18 |
| Overlay bindings | 133 | 134 |
| Evidence registry entries | 3,145 | 3,146 |

The post-overlay missing-cell and conflict-cell counts remain zero.

## 8. Governance guards

- semantic P0: `0`
- feature P1: `22_OPEN_UNCHANGED`
- M13 actions: `4_OPEN_UNCHANGED`
- product lanes: `15_OF_15_NOT_RUN`
- GitHub publication: `SUSPENDED`
- implementation claim: `NONE`
