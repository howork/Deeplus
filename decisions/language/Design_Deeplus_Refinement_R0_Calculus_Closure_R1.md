# Deeplus Refinement R0 Calculus Closure R1

Status: `LOCAL_VERIFIED_CANDIDATE_NOT_INTEGRATED`
Gap: `IR-REF-P1-056`
Baseline: GitHub `howork/Deeplus` main `10e64f492f0529610673846139afcf0d95175663`, local predecessor `1423d9a9cee637f496b3a948913d8de285bc15c3`

## Decision

Adopt `RefinementR0V1` as the single checker-internal representation and
decision contract for Stable refinement predicates, inline R0 guards,
`GuardSummaryV1`, flow facts, and closed-Union relation queries. This decision
adds no source spelling. It replaces prose-only “finite R0” references and the
incompatible ad-hoc JSON formula shapes with one closed typed AST.
Checker admission and proof calls use the companion closed
`RefinementR0QueryV1` descriptor rather than an untyped `subject` string.

The admitted value domains are Bool, exact signed/unsigned integers,
`StaticInt`, Float32/Float64, Rational, Char scalar, and ordered Enum.
String/Bytes/List/ReadonlyView length is available only through the four
registered total value projections. A source operator enters R0 only after
selection of an exact sealed compiler or Prelude R0 row; user conformance,
provider lookup, reflection, runtime discovery, and arbitrary calls never do.

Checked integer arithmetic must be proven total over the declared input
domain. Integer division and remainder require a static safe divisor; Rational
division and remainder require a static nonzero divisor. IEEE arithmetic is
total under its exact Float32/Float64 value law, including NaN and infinities.
This preserves the current `Int where this % 2 == 0`, Float/Rational bounds,
ordered Enum intervals, and `String where this.length > 0` without admitting a
general solver.

## Formula and proof boundary

The canonical formula is bounded negation-normal form. `NOT` owns one compare
atom; `ALL` and `ANY` are flattened, constant-folded, duplicate-free, and sorted
by canonical child bytes. Arithmetic terms are never reassociated. In
particular `not(x > c)` for an IEEE value is not rewritten to `x <= c`: the
former includes unordered NaN and the latter does not.

The reference procedure expands a bounded DNF, intersects typed interval,
identity, exclusion, congruence, Bool, and IEEE-NaN cells, and returns
`SAT`, `UNSAT`, or `UNKNOWN`. Implication, disjointness, overlap, and refinement
boundary decisions are derived from those results. Exceeding an admission
limit rejects the formula as non-R0. Exceeding only a relation proof budget
returns `UNKNOWN`; it never becomes PASS.

## Rejected alternatives

- Free-form source strings in summaries: not identity-safe or implementable.
- Host SMT or unbounded symbolic search: violates termination and reproducible
  diagnostics.
- Algebraic Float complement inversion: unsound in the presence of NaN.
- Arbitrary user operator/method calls: their totality and responsibility are
  not a closed R0 authority.
- Treating proof-budget exhaustion as disjoint or proved: unsound.

## Evidence boundary

This is a design-static implementation handoff. It closes no existing feature
P1, executes no product parser/checker/MIR/xVM/backend/tooling lane, and creates
no runtime proof object. Semantic P0 remains zero, the exact 22 feature P1 stay
OPEN, and all 15 product lanes remain `NOT_RUN`. GitHub publication was not
performed.
