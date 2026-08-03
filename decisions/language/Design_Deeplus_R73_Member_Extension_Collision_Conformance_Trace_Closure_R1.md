# Deeplus R73 Member/Extension Collision Conformance Trace Closure R1

## 1. Decision

Exactly two cells of `member_extension_collision_error_policy` change:

| Stage | Outcome | Predecessor | R73 disposition |
|---|---|---|---|
| `CONFORMANCE_TESTS` | `BOUNDARY` | `APPLICABLE_BLOCKED_BY_GAP(IR-XCUT-P1-054)` | `BOUND_DIRECT` |
| `CONFORMANCE_TESTS` | `REJECT` | `APPLICABLE_BLOCKED_BY_GAP(IR-XCUT-P1-054)` | `BOUND_DIRECT` |

Both outcomes are owned by the feature's existing static collision judgment.
No delegation or not-applicable disposition is warranted. The `POSITIVE`
outcome remains `BOUND_DIRECT` and is not transitioned by R73.

## 2. Authority and baseline

| Item | Exact value |
|---|---|
| Canonical repository | `howork/Deeplus` |
| Canonical baseline | `39a5d50cc770341c4b9776d00d84520b780d0c62` |
| Local predecessor | `ab1ffd86db91d2b3b93e7c15e43829a7aa4704d3` |
| Candidate status | `NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY` |
| Feature | `member_extension_collision_error_policy` |
| Stage | `CONFORMANCE_TESTS` |
| Evidence level | `E2_STRUCTURED_STATIC` |
| Product execution | `NOT_RUN` |

## 3. Reused acceptance evidence

R73 creates no new semantic contract or conformance fixture. It reuses the
machine-validated R72 acceptance partition in
`spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json` and
`tests/fixtures/current/member-extension-collision-dynamic-trace-closure-r1.json`.

The boundary outcome binds directly to:

- `R72-MECD-ACC-003`: exact qualification restricts lookup to one extension
  domain and bypasses only the cross-domain collision;
- `R72-MECD-ACC-004`: discovery, source, import, use, address, and link order
  cannot choose a collision winner;
- `R72-MECD-ACC-005`: the exact collision primary precedes a same-stage generic
  fallback;
- the predecessor oracle pair `IR-R4-GAP-02-B` and
  `IR-R4-RES041-BOUND`.

The reject outcome binds directly to:

- `R72-MECD-ACC-006`: one applicable candidate in each domain rejects with
  selected count zero before HIR;
- `R72-MECD-ACC-007`: the cross-domain collision precedes within-domain
  ranking;
- `R72-MECD-ACC-008`: recovery cannot create admitted HIR or a runtime
  fallback;
- `R72-MECD-ACC-009`: MIR, xVM, runtime, and Cranelift cannot reselect the
  rejected call;
- the predecessor oracle pair `IR-R4-GAP-02-N` and `IR-R4-RES041-NEG`, plus
  rejected examples `EX-R48-017` and `EX-R4-RESOLVE-NG-002`.

The exact structured evidence pointers are:

```text
BOUNDARY:
  spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json#/acceptance_bindings/BOUNDARY
  EV-7af9345ab4c98882b2af77fc1814fc0352298f5d5f4dd9d4df357abc824c0c3f

REJECT:
  spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json#/acceptance_bindings/REJECT
  EV-ee837f7a965f93d9d84ad03a394d443692b235c6715b00ab2e748d5dbaf7850e
```

All reused cases remain `DESIGN_STATIC_NOT_RUN`. Their static schema and
validator receipts prove contract consistency, not parser, checker, runtime,
backend, tooling, or product execution.

## 4. Semantic boundary

`MemberExtensionCollisionRejected` remains the integrated-checker predicate.
For an ordinary selector, it computes nominal-member and active-extension
applicability as separate domains. If both are nonempty, it emits the sole
active primary `MEMBER_EXTENSION_COLLISION`, commits `selected_count = 0`, and
admits no HIR or downstream executable residue. If either domain is empty, the
collision predicate admits and leaves selection to the existing within-domain
owner. Exact qualification restricts the domain before this cross-domain test.

R73 does not alter this judgment, R71 selected-call dynamic delegation, R72's
pre-HIR rejection boundary, diagnostic identity, qualification semantics,
within-domain applicability or ranking, recovery, or runtime/backend behavior.

## 5. Preservation and projected trace

Exactly the two named outcome cells transition. Every positive and non-target
cell remains byte-semantically unchanged. The 4,219 non-target atomic cells
retain digest:

```text
7448ce347ec8ebf432af540973ec6e56bf9ddbd04049c57d4eca7a23ba544cf7
```

| Metric | Predecessor | R73 projection |
|---|---:|---:|
| `BOUND_DIRECT` | 2,467 | 2,469 |
| `BOUND_DELEGATED` | 4 | 4 |
| `NOT_APPLICABLE` | 503 | 503 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,247 | 1,245 |
| Applied overlays | 18 | 19 |
| Overlay bindings | 134 | 136 |
| Evidence registry entries | 3,146 | 3,148 |

## 6. Known nonblocking trace drift

The adjacent `DIAGNOSTICS` cell currently says `NOT_APPLICABLE` with a rationale
that the feature has no rejection condition. That trace metadata is stale:
the canonical predicate `MemberExtensionCollisionRejected` and active checker
diagnostic `MEMBER_EXTENSION_COLLISION` establish the opposite.

This is not a blocker for the two R73 conformance transitions because their
feature-specific boundary and rejection oracles are independently complete and
machine-bound. R73 nevertheless does not conceal or modify the drift: the
non-target cell is preserved exactly and the correction becomes the immediate,
bounded R74 successor candidate. R74 must correct only the diagnostic trace
binding and must not reopen the collision semantics or R73 acceptance sets.

## 7. Governance guards

- semantic P0: `0`
- feature P1: `22_OPEN_UNCHANGED`
- M13 actions: `4_OPEN_UNCHANGED`
- product lanes: `15_OF_15_NOT_RUN`
- product execution receipts: `0`
- new source surface, grammar, AST, HIR, MIR, xVM, runtime, backend, or
  diagnostic identity: `0`
- GitHub publication: `SUSPENDED`
- implementation claim: `NONE`
