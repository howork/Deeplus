# Design Deeplus R76 Global Implementation Target Trace Closure R1

## 1. Decision

`LOCAL_CANDIDATE_READY_FOR_SEMANTIC_PROMOTION`

R76 closes the design/static locator omission represented by
`IR-XCUT-P1-054`. It does not add or change a Deeplus source form, type rule,
runtime behavior, backend behavior, feature status, or source-activation
state. The exact baseline is GitHub `main`
`40a826af29410af1a14c6a7dec3193cd59ba9b12`.

The candidate is not `VERIFIED_CLOSED` until semantic publication, a separate
publication-closure binding, and exact-main readback are complete.

## 2. Exact denominator and transition

| Metric | Predecessor | R76 candidate |
|---|---:|---:|
| target feature rows | 469 | 469 |
| stage cells | 3,283 | 3,283 |
| test outcome cells | 1,407 | 1,407 |
| `BOUND_DIRECT` | 2,473 | 3,709 |
| `BOUND_DELEGATED` | 4 | 4 |
| `NOT_APPLICABLE` | 502 | 508 |
| `APPLICABLE_BLOCKED_BY_GAP` | 1,242 | 0 |
| product rows `NOT_RUN` | 469 | 469 |

The 1,242 predecessor cells cover 409 distinct target features:

- AST/frontend: 11
- static semantics: 64
- dynamic/lowering: 206
- conformance-test outcomes: 961
  - positive: 145
  - boundary: 408
  - reject: 408

Six prohibited predecessor surfaces are explicitly `NOT_APPLICABLE` to
admitted AST construction. The other 1,236 cells receive exact E2
design/static contract locators.

## 3. Evidence model

The controlling cell contract is
`spec/contracts/implementation-target-global-trace-closure-r1.json`.
Every entry binds:

1. one exact feature-catalog row and JSON pointer;
2. its status, authority/dependency/source-activation fence, display name, and
   normative notes;
3. one exact frontend, static, lowering, or conformance obligation;
4. the predecessor `IR-XCUT-P1-054` cell identity;
5. `E2_STRUCTURED_STATIC` evidence and `NOT_RUN` product execution.

The evidence overlay maps each cell to its exact contract JSON pointer. It
does not treat file existence as parser/checker/runtime success.

## 4. Frontend and static-semantics policy

An admitted source feature must preserve one canonical CST/AST
interpretation through the existing frontend model. A prohibited surface
that has no admitted AST is recorded as such instead of inventing an error
node as canonical semantic residue.

Static bindings require the implementation to enforce the exact feature-row
contract, declared dependencies, existing checker predicates, and existing
diagnostic fence. R76 creates no new final diagnostic ID or checker predicate
identity.

## 5. Dynamic/lowering policy

Each applicable dynamic cell binds either:

- `ZERO_DYNAMIC_RESIDUE` for a contract that terminates before admitted
  runtime behavior; or
- `CANONICAL_HIR_H1_MIR_PROJECTION`, which preserves the exact language
  semantics through the existing HIR-H1 bridge and backend-neutral Deeplus
  MIR registry.

Cranelift remains a downstream projection. It may implement the canonical
MIR responsibility but may not reinterpret the language rule. R76 creates no
new HIR identity, MIR operation kind, runtime ABI identity, or backend
capability.

## 6. Conformance-test specification

Existing review-corpus examples are reused before any model-level obligation;
669 distinct registered example IDs are referenced. When an exact feature has
no dedicated source example for an outcome, R76 specifies a model-level test
against the immutable feature contract:

- positive: admit only the exact canonical contract;
- boundary: preserve authority, dependency, source-activation, and residue
  fences without implicit widening;
- reject: reject an unauthorized contract-widening mutation before it creates
  canonical AST/HIR/MIR/API residue.

These are implementation acceptance specifications, not executed product
tests. Production parser, checker, HIR/MIR, xVM, runtime, Cranelift,
formatter/LSP, independent conformance, and product support remain `NOT_RUN`.

## 7. Validation

- exact 469-row trace validation: PASS
- exact 1,242-cell R76 contract validation: PASS
- R76 bounded mutation suite: 8/8 PASS
- legacy/current trace mutation suite: 14/14 PASS
- repeated JSON locator parsing is cached per validator process; this changes
  no evidence and reduces one validation from about 18 seconds to under one
  second on the local environment
- full workspace and canonical CI are required before promotion

## 8. Preserved authority fence

- semantic P0: 0
- canonical feature P1: exactly 22 OPEN
- M13-A002..005: exactly 4 OPEN actions
- product lanes: 15/15 `NOT_RUN`
- feature status changes: 0
- source activation changes: 0
- new language semantics: 0
- E4/E5 execution evidence: 0

## 9. Closure rule and next gate

`IR-XCUT-P1-054` may transition from `APPROVED_NOT_INTEGRATED` to
`INTEGRATED_UNVERIFIED` after semantic merge. It becomes `VERIFIED_CLOSED`
only after publication-closure ledger/pointer binding, successful CI, and
exact-main readback. The next independent readiness cluster must begin from
that publication-closure SHA rather than this local candidate or semantic
source commit.
