# R61 Pattern Clause Exhaustiveness Trace Closure

Status: `LOCAL_APPROVED_CANDIDATE`

Baseline: `2db4f483ffdcb281ef765def67e510e63917500c`

Scope: the `clause_pattern_heads` dynamic-lowering cell and the boundary and
reject conformance outcomes of `clause_pattern_heads` and
`match_exhaustiveness_phase_a`. This decision changes no grammar production,
AST/HIR identity, MIR operation kind, source activation, feature P1, or
product-support claim.

## Declarative clause lowering

A clause function receives its implicit parent parameter subject exactly once.
Before lowering, `DeclarativeClausePartitionAdmitted` constructs the finite
normalized subject partition, rejects the first source-ordered overlap or an
undecidable intersection, subtracts unconditional coverage, gives one final
`otherwise` the exact remainder, and rejects any nonempty remainder.

For an admitted clause family, source order is a deterministic probe order and
never an overlap tiebreaker. Each clause performs the existing PatternAttempt,
its child-pattern projections, and one optional pure R0 guard. A mismatch or
false guard proceeds to the next declarative clause with no published binding,
move, loan, view, authority, or reservation. A successful attempt imports the
R60 ownership contract, performs one infallible atomic binding commit, evaluates
the selected body exactly once, checks the declared return type, and exits by
the existing `RETURN_TO`/`LEAVE` path. Exhaustiveness makes the all-failed
terminal unreachable; no implicit arm, fallback value, or PatternMatchDefect is
introduced.

The serialized `DECLARATIVE_PARTITION_REJECTION` disposition is therefore the
compile-time admission disposition. It does not describe the runtime control
edge of an already admitted family, which is `NEXT_DECLARATIVE_CLAUSE` for a
pattern mismatch or false guard.

## Match exhaustiveness outcomes

Match usefulness and exhaustiveness remain one ordered normalized-partition
pass. Earlier reachable unguarded arms subtract coverage. Guarded arms may be
useful and record a mention, but never subtract coverage. The boundary and
reject cases bind the exact distinction among:

- `MATCH_ARM_UNREACHABLE` for an empty ordinary-arm residual;
- `OTHERWISE_UNREACHABLE` for `otherwise` after an empty residual;
- `MATCH_NONEXHAUSTIVE_AFTER_GUARDS` when every remaining cell was mentioned
  only by guarded arms; and
- `MATCH_NOT_EXHAUSTIVE` when any remaining cell was never mentioned.

Enum case identity and payload admission precede coverage diagnostics. A
foreign case, unknown case, or payload-shape mismatch therefore remains
`ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH`, even if the surviving arms would also
be nonexhaustive.

## Existing lowering alignment

- `HM-LR-TOP-010`: match selection with `PATTERN_PROBE` and `SWITCH_ENUM`.
- `HM-LR-TOP-016`: PatternAttempt with `PATTERN_PROBE`, `BINDING_COMMIT`, and
  `COND_BR`.
- `HM-LR-TOP-026`: callable return with `LEAVE`.
- existing child rows cover List, Variant, Or, Alias, and Move patterns.
- existing operations provide projection, move reservation/cancellation,
  place move, shared-loan begin/end, and final binding commit.

No new HIR identity or MIR operation kind is required.

## Evidence boundary

The overlay directly transitions exactly five cells:

1. `clause_pattern_heads / DYNAMIC_LOWERING` through `PCETC-R006`;
2. `clause_pattern_heads / CONFORMANCE_TESTS:BOUNDARY`;
3. `clause_pattern_heads / CONFORMANCE_TESTS:REJECT`;
4. `match_exhaustiveness_phase_a / CONFORMANCE_TESTS:BOUNDARY`;
5. `match_exhaustiveness_phase_a / CONFORMANCE_TESTS:REJECT`.

The three clause positive cases are supporting design-static evidence because
the positive outcome was already direct at the R60 baseline. The four outcome
sets bind nineteen cases; all twenty-two cases remain product `NOT_RUN`.

## Governance fence

- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15_NOT_RUN`
- GitHub publication: `SUSPENDED`
- production implementation: `NOT_AUTHORIZED`
