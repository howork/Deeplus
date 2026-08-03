# R64 Associated Requirement Phase A Trace Closure

Status: `LOCAL_APPROVED_CANDIDATE`

Canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`

Local predecessor: `19d8ea962a884f57e45d16883a128405d419bbe6`

Scope: exactly four trace cells for `associated_requirement_phase_a`: the
`DYNAMIC_LOWERING` cell and the `POSITIVE`, `BOUNDARY`, and `REJECT`
`CONFORMANCE_TESTS` outcome cells. This decision changes no source spelling,
grammar production, AST/HIR identity, MIR operation or terminator kind,
diagnostic registry row, source activation, feature P1, or product-support
claim.

## Static declaration and binding boundary

An associated type, value, or non-method function declaration creates a
canonical static requirement identity. `AssociatedRequirementAdmitted` owns
the admission decision. It normalizes the requirement kind and contract,
requires exactly one compatible explicit or canonical inherited binding, and
rejects identity or kind conflicts, inadmissible bounds or defaults, unresolved
or ambiguous bindings, and recursive requirement-obligation cycles before MIR.

`AssociatedRequirementWitnessAdmitted` and `WherePredicateAdmitted` remain
supporting predicates. Their existing contracts are unchanged and they do not
control the R64 trace transition.

An admitted declaration or binding is checker-only metadata. It creates no
standalone HIR expression, MIR operation, runtime service, lookup, fallback,
activation, or backend decision. Its `RequirementId` remains available to
static conformance and projection metadata, but the declaration itself does not
lower.

## Selected-item ownership fence

Use of an associated item is a different responsibility from admission of its
declaration or binding. `trait_qualified_associated_static_selection` remains
the sole owner of the R62 `TraitAssociatedStaticSelectionId` descriptor and its
existing HIR/MIR projection:

- an associated type emits no runtime operation;
- an associated value or bare function reference reuses `HM-LR-REF-002` and
  `HM-LR-TOP-002`;
- an invoked associated function reuses `HM-LR-CALL-003`.

R64 neither delegates `associated_requirement_phase_a` to that feature nor
duplicates its descriptor, identity residue, lowering rows, operations,
terminators, or runtime rules. R62 continues to preserve the exact selected
`TraitId`, `RequirementId`, `ConformanceId`, `TraitWitnessId`,
`ImplementationId`, `SubstitutionId`, and `ResponsibilityId`.

## Exact trace transitions

R64 transitions exactly four cells:

1. `associated_requirement_phase_a / DYNAMIC_LOWERING` changes from
   `APPLICABLE_BLOCKED_BY_GAP` to `NOT_APPLICABLE` with reason
   `NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR` and authority boundary
   `MIR_RUNTIME_AUTHORITY`.
2. `associated_requirement_phase_a / CONFORMANCE_TESTS:POSITIVE` changes from
   `APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`.
3. `associated_requirement_phase_a / CONFORMANCE_TESTS:BOUNDARY` changes from
   `APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`.
4. `associated_requirement_phase_a / CONFORMANCE_TESTS:REJECT` changes from
   `APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`.

No other feature or stage cell transitions in R64.

## Acceptance evidence

The three conformance outcomes bind exactly eight existing R9 static-reference
cases:

- positive, two: `R9-AR-POS-001` and `R9-ADV-AR-VALUE-ADMIT`;
- boundary, one: `R9-AR-BOUNDARY-001`;
- reject, five: `R9-AR-NEG-001`, `R9-AR-NEG-002`, `R9-AR-NEG-003`,
  `R9-AR-NEG-004`, and `R9-ADV-MULTI-ASSOCIATED`.

The positive and boundary cases admit exact type, value, or function bindings
without emitting a diagnostic or runtime operation. The reject cases exercise
the four ordered `AssociatedRequirementAdmitted` reason ranks. Each rejection
emits exactly one `ASSOCIATED_REQUIREMENT_UNRESOLVED`, leaves later candidates
`NOT_EVALUATED`, and reaches neither HIR lowering nor MIR.

All eight cases are structured static evidence. Parser, checker, MIR, xVM,
Cranelift, formatter, LSP, and product execution remain `NOT_RUN` unless a
separate execution receipt says otherwise.

## Expected trace totals

After applying the exact four transitions, the implementation-target trace has
the following derived totals:

- `BOUND_DIRECT`: `2461`
- `BOUND_DELEGATED`: `3`
- `NOT_APPLICABLE`: `503`
- `APPLICABLE_BLOCKED_BY_GAP`: `1254`
- applied evidence overlays: `10`
- overlay bindings: `125`

These totals are acceptance constraints, not product-execution claims.

## Bounded follow-up

R64 discovered `IR-TRACE-P1-056`: the same feature's `AST_FRONTEND` and
`DIAGNOSTICS` classification parity requires a separate bounded review. The
current AST classification does not explicitly identify the existing
associated-requirement declaration AST owner, while the diagnostic
classification does not reflect the active `AssociatedRequirementAdmitted`
rejection contract. This follow-up is recorded but explicitly outside R64; R64
does not transition either cell and does not expand into a diagnostic or AST
repair.

## Governance fence

- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15_NOT_RUN`
- GitHub publication: `SUSPENDED`
- production implementation: `NOT_AUTHORIZED`
