# R65 Associated Requirement AST and Diagnostic Parity

Status: `LOCAL_APPROVED_CANDIDATE`

Canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`

Local predecessor: `f2e7353b1c44fc066eba47f6d013cbe0a20e9239`

Gap: `IR-TRACE-P1-056`

Scope: exactly two trace cells for `associated_requirement_phase_a`,
`AST_FRONTEND` and `DIAGNOSTICS`. Both cells change from `NOT_APPLICABLE` to
`BOUND_DIRECT`. The repair is overlay-only: it does not change the feature
catalog, source spelling, grammar production, CST or AST model, checker
semantics, diagnostic registry or relation topology, HIR or MIR, runtime
behavior, source activation, product support, or GitHub state.

## Existing AST authority

The associated-requirement declaration already has one current source-graph
AST owner. The exact authority is
`spec/contracts/grammar-production-disposition-registry-r1.json#/production_rows/237`:

- production: `AssociatedRequirementDecl`;
- disposition: `ast_node`;
- CST kind: `CST/AssociatedRequirementDecl`;
- AST target: `AST/AssociatedRequirementDecl`;
- AST output cardinality: `EXACTLY_ONE`;
- invalid or recovery AST count: `0`.

This existing node covers the type, value, and function requirement forms. R65
does not add an AST identity, child-node kind, normalization rule, or parser
commitment.

The binding helper is deliberately not a second AST owner. The exact boundary
is
`spec/contracts/grammar-production-disposition-registry-r1.json#/production_rows/251`:

- production: `AssociatedRequirementBinding`;
- disposition: `cst_only`;
- CST shape: `INLINE_IN_PARENT_PRODUCTION_NODE`;
- AST target: `null`;
- AST output cardinality: `ZERO`.

Its exact tokens and order remain inline in the enclosing current conformance
syntax and normalize into the existing `AST/ConformanceDecl` responsibility.
R65 does not materialize `AssociatedRequirementBinding` as a standalone child
AST node.

## Existing diagnostic authority

`AssociatedRequirementAdmitted` remains the sole controlling predicate. Its
active public rejection is already registered at
`spec/diagnostics/catalog/chunks/part-0001.json#/39` as
`ASSOCIATED_REQUIREMENT_UNRESOLVED`, an active checker error with source
emission and product support `NOT_RUN`.

The exact primary relation is
`spec/diagnostics/relations/chunks/part-0001.json#/8`:
`AssociatedRequirementAdmitted:default` maps to
`ASSOCIATED_REQUIREMENT_UNRESOLVED` with relation `primary`. No secondary
diagnostic is admitted.

R9's `spec/contracts/diagnostic-dispatch-closure-r1.json` fixes four ordered
rejection reasons:

1. `1_requirement_identity_or_kind_conflict`;
2. `2_requirement_bounds_or_default_not_admitted`;
3. `3_implementation_binding_unresolved_or_ambiguous`;
4. `4_recursive_requirement_obligation_cycle`.

The lowest detected numeric rank wins, followed by canonical culprit identity;
source order is locator-only and never selects the result. R64 rule
`ARPTC-R006` in
`spec/contracts/associated-requirement-phase-a-trace-closure-r1.json` remains
exact: every rejection emits exactly one
`ASSOCIATED_REQUIREMENT_UNRESOLVED` primary diagnostic and leaves every later
candidate `NOT_EVALUATED`. An admitted case emits no diagnostic and has no
later rejection candidate to evaluate.

## Exact trace transitions

R65 transitions exactly two cells:

1. `associated_requirement_phase_a / AST_FRONTEND` changes from
   `NOT_APPLICABLE` to `BOUND_DIRECT`, bound to the existing
   `AssociatedRequirementDecl` AST owner and the inline binding boundary above.
2. `associated_requirement_phase_a / DIAGNOSTICS` changes from
   `NOT_APPLICABLE` to `BOUND_DIRECT`, bound to the active diagnostic catalog
   row, primary predicate relation, and the unchanged R9/R64 dispatch contract.

Neither cell is delegated. Both have `not_applicable: null`, no blocked gap,
and structured static evidence only. Exactly `4219` other trace cells retain
their predecessor semantic bytes.

## Acceptance

The R65 candidate is accepted only if all of the following hold:

- the overlay contains exactly one feature and exactly two bindings;
- the bound cells are exactly `AST_FRONTEND` and `DIAGNOSTICS` for
  `associated_requirement_phase_a`;
- `/production_rows/237` remains the unique associated-requirement declaration
  AST owner;
- `/production_rows/251` remains `cst_only`, inline, and emits zero AST nodes;
- no standalone binding child AST identity is created;
- `AssociatedRequirementAdmitted` retains exactly the four rank keys above;
- every rejection selects `ASSOCIATED_REQUIREMENT_UNRESOLVED`, emits exactly
  one primary, and leaves later candidates `NOT_EVALUATED`;
- the active catalog row and primary relation remain `/39` and `/8`;
- R64 acceptance cases and their expected decisions remain byte-identical;
- exactly `4219` non-target cells retain their predecessor semantic bytes;
- the derived trace totals are exactly `BOUND_DIRECT=2463`,
  `BOUND_DELEGATED=3`, `NOT_APPLICABLE=501`, and
  `APPLICABLE_BLOCKED_BY_GAP=1254`;
- applied evidence overlay count is `11`, cumulative binding count is `127`,
  and evidence registry count is `3140`;
- semantic P0 remains zero, feature P1 remains exactly 22 OPEN, M13 remains
  four OPEN actions, and all 15 product lanes remain `NOT_RUN`;
- source, grammar, frontend model, predicate semantics, diagnostics, fixtures,
  conformance cases, runtime artifacts, and GitHub are otherwise unchanged.

After these local acceptance checks pass, `IR-TRACE-P1-056` has no remaining
AST or diagnostic parity gap in the local candidate. This statement is local
trace closure only; it is not canonical publication or product execution.

## Expected trace totals

- `BOUND_DIRECT`: `2463`
- `BOUND_DELEGATED`: `3`
- `NOT_APPLICABLE`: `501`
- `APPLICABLE_BLOCKED_BY_GAP`: `1254`
- applied evidence overlays: `11`
- cumulative overlay bindings: `127`
- evidence registry entries: `3140`

These are static acceptance constraints and do not constitute product
execution evidence.

## Governance fence

- candidate status: `LOCAL_APPROVED_CANDIDATE`
- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15_NOT_RUN`
- product implementation or execution: `NONE / NOT_RUN`
- source, syntax, semantics, registry, or activation change: `NONE`
- GitHub publication: `SUSPENDED`
- changed trace cells: `2`
- unchanged trace cells: `4219`
- `IR-TRACE-P1-056` after successful local validation:
  `NO_REMAINING_GAP_IN_LOCAL_CANDIDATE`
