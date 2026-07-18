# DP-RFC-XXXX: Short title

## Metadata

| Field | Value |
|---|---|
| Status | Draft |
| Author | |
| Sponsor | |
| Created | YYYY-MM-DD |
| Target language version | |
| Target spec revision | |
| Tracking issue | |
| Supersedes | None |
| Required primary roles | Design_, Spec_, Impl_, Test_, Devel_ |
| Required auxiliary roles | |

## 1. Summary

State the proposal in five sentences or fewer.

## 2. Problem and evidence

- What concrete problem exists?
- Which current rule or product behavior demonstrates it?
- What evidence level exists?
- Why is an editorial change or ordinary issue insufficient?

## 3. Responsibility boundary

Explain ownership, failure, cleanup, suspension, authority, provider lookup,
call domain, public API residue, and any hidden context.

## 4. Proposed current rule

Write the complete normative rule, not a patch fragment.

## 5. Exact syntax impact

- Grammar productions changed:
- Lexical adjacency:
- Contextual keyword impact:
- Recovery-only forms:
- Removed/no-go forms:

## 6. Frontend and normalization

- CST shape:
- Contextual admission:
- HIR normalization:
- Source mapping and diagnostics:

## 7. Type/checker contract

- Typing judgments:
- Ownership/effect/error rules:
- Public type residue:
- Coherence and overload impact:
- Checker predicates:

## 8. MIR contract

- Lowering:
- Evaluation order:
- Cleanup/drop/resource release:
- Errors/traps:
- Suspension/concurrency:
- Authority:
- xVM/AOT/JIT observable equivalence:

## 9. Diagnostics and tooling

List new, changed, retired diagnostics and formatter/LSP behavior.

## 10. Examples

Provide positive, negative, boundary, Preview-gated, and formatting examples.
Every negative example needs the intended primary diagnostic.

## 11. Compatibility

- Source compatibility:
- MIR/bytecode compatibility:
- Stdlib/package impact:
- Migration plan, if public:

## 12. Alternatives

Include at least:

1. status quo
2. narrower surface
3. library/tooling solution
4. rejection

## 13. Implementation plan

Define the smallest Rust frontend → HIR → MIR → xVM vertical slice. LLVM support
may follow only with an explicit lane status.

## 14. Evidence and test plan

| Claim | Required evidence | Owner | Acceptance test |
|---|---|---|---|

## 15. Stabilization and rollback

- Preview activation:
- Stable gate:
- Rollback trigger:
- Removal of stale forms:

## 16. Open questions

Every open question must have an owner and closure method.

## 17. Role decisions

| Role | Decision | Main concern | Preferred alternative | Required gate |
|---|---|---|---|---|
| Design_ | | | | |
| Spec_ | | | | |
| Impl_ | | | | |
| Test_ | | | | |
| Devel_ | | | | |

[EXPR-001_BINDING]
clause_id: EXPR-001
authority: governance/policies/management-policy.yaml#EXPR-001
clause_digest: 42250c554d2d5f9cfb29bbd3668bed40ec1390fce658ac1804f7c6de29b1ac39
classification: non-authoritative projection
