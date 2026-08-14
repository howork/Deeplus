# Deeplus ordinary-call selection closure R1

## Decision

`IR-CALL-P1-055` is accepted as a bounded Stable-design closure.  The
`ResolvedOverloadSetRef` analysis residue is consumed by one versioned
`OrdinaryCallSelectionV1` judgment before canonical HIR-H1 is sealed.

This decision closes the missing candidate-local generic inference,
applicability, specificity, and winner contract.  It does not add syntax, does
not select Trait witnesses, does not compare nominal members with extensions,
and does not activate product implementation.

## Scope

The judgment owns ordinary direct, nominal member, Trait-requirement, and
qualified-extension callable sets used by `CallMode::Ordinary` or
`CallMode::Message`.  Actor transport, fixed-operator conformance selection,
Trait witness discovery/materialization, reserved operations, and dynamic
dispatch remain under their existing owners.

The existing member/extension collision policy runs on the independently
applicable nominal and extension domains before either domain may select a
winner.  Two nonempty applicable domains therefore reject with
`MEMBER_EXTENSION_COLLISION`; this cluster never ranks across the boundary.

## Candidate-local inference

Each candidate receives fresh variables for only its declared generic
parameters.  Explicit generic arguments and the statically described explicit
call arguments constrain that candidate alone.  Defaults do not infer generic
arguments.  A candidate must produce one complete normalized substitution
after kind, occurs, `where`, and conformance checks; constraints and failed
bindings never flow to a sibling candidate.

A fixed expected result verifies the already selected winner.  It never adds a
constraint, filters candidates, or breaks a tie.  Result-only overloads are
therefore ambiguous.

An implicit-parameter lambda or trailing closure contributes only its
structural arity/label shape while the candidate set is plural.  Selection
must first leave one expected callable type; the body is then checked exactly
once.  Candidate-by-candidate body probing is forbidden.

## Applicability and specificity

Applicability is a noncommitting static proof over the normalized argument
descriptors.  It closes call shape, candidate-local substitution, ownership,
effect/error context, isolation, suspension, and required evidence.  It does
not execute the callee, arguments, defaults, or closure body.

Specificity is a partial order inside one callable domain:

1. channel generality is `FIXED < REPEATED < NAMED_REST < REPEATED_AND_NAMED`;
2. at the same channel rank, one input domain is narrower only through the
   closed proof rules `EXACT_NOMINAL_SUBTYPE`,
   `CONCRETE_OR_CONSTRUCTED_OVER_BARE_TYPE_PARAMETER`, or
   `STRICT_TRAIT_BOUND_SUPERSET`;
3. every compared input slot must be equal or narrower and at least one must
   be strictly narrower;
4. ownership mode, effect/error row, result type, defaults consumed,
   refinement/`where` spelling, provider, declaration, import, and source order
   never add preference.

An unproved relation is `INCOMPARABLE`, not a guessed winner.  The unique
maximal applicable candidate wins.  Zero applicable candidates and multiple
maximal candidates reject deterministically.

## HIR and runtime fence

The winner seals one `OrdinaryCallSelectionV1` identity containing the exact
candidate-domain digest, selected callable declaration (`FunctionId` domain)
and callable implementation, complete substitution, canonical call shape, and
specificity proof. A
non-actor/non-reserved `CallPlan` cannot enter canonical HIR without it.

Runtime evaluation begins only after this seal.  The selected callee or
receiver, explicit arguments, and selected defaults evaluate exactly once in
their existing order.  No unselected candidate body or default is evaluated,
and MIR/xVM/Cranelift never re-rank or look up the call.

## Governance

- gap_id: IR-CALL-P1-055
- semantic_p0: 0
- feature_p1: 22_OPEN_UNCHANGED
- product_lanes: 15/15_NOT_RUN
- product implementation: NOT_RUN
- GitHub publication: NOT_PERFORMED
- local status: LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED
