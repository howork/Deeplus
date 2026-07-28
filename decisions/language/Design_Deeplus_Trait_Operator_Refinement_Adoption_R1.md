# Deeplus Trait Conformance, Operator, and Refinement Adoption R1

Status: `CURRENT_DESIGN_STATIC`

Revision: `r51f3-current-trait-operator-refinement-r1`

Product execution: `15/15 NOT_RUN`

## Decision

The Trait Conformance shared-design report is accepted with guards. The
canonical surface is the successor surface:

```deeplus
public type Money conforms Display {
    def Display::display.() -> String = {
        return amountText
    }
}
```

Nominal headers may repeat `conforms`, class and Trait inheritance use
`derives`, a Trait may declare `supports auto`, an admitted closed synthesis
policy may be selected with `by auto`, and `conform Trait { ... }` groups
Trait-owned items. The existing `as name`, lowercase `via`, associated
projection `<T as Trait>::Item`, and the exact `.`, `+`, `*.`, `*+` witness
markers remain authoritative.

The former `conformance A conforms B`, class `: Base`, and Trait-inheritance
`requires Parent` spellings are removed rather than retained as historical or
recovery surfaces. Callable contracts continue to use `requires`.

## Fixed-glyph conformance

Arbitrary operator declaration remains outside Deeplus. Stable fixed-glyph
conformance covers exactly:

- unary `+`, `-`;
- binary `+`, `-`, `*`, `/`, `%`;
- equality `==`, `!=`;
- ordering `<`, `<=`, `>`, `>=`.

The Prelude evidence roots are `UnaryPlus`, `UnaryMinus`, `Add<Rhs>`,
`Subtract<Rhs>`, `Multiply<Rhs>`, `Divide<Rhs>`, `Remainder<Rhs>`, `Eq<Rhs>`,
and `Ord<Rhs>`. `!=` is derived from `Eq`; all four ordering glyphs are
derived from one `Ord.compare` result. Compound assignment is derived from its
binary operation plus exact assignment admissibility and never introduces an
independent witness.

Intrinsic-reserved operand pairs remain closed. Selection for an admitted
non-intrinsic pair is one left-owner direct-global conformance with no
conversion search, source ordering, fallback, specialization, dynamic lookup,
or result-directed selection.

Division and remainder failures such as a zero divisor raise
`ArithmeticDefect` before commit. Rational supports the complete arithmetic,
equality, and ordering profile. Complex supports arithmetic and its existing
equality profile but never receives `Ord`.

## Ordered Enum

A payload-free, nongeneric `enum#increasing` or `enum#decreasing` receives one
whole-Enum `Eq` and `Ord` witness and may be used by `<`, `<=`, `>`, `>=`,
`..`, and `..<`. Semantic rank, not source identity, serialization tag,
runtime discriminant, layout, or ABI identity, controls ordering.

Range iteration advances in semantic `Ord` order. `..` includes the final
endpoint and `..<` excludes it. Reverse traversal is explicit through
`downTo`; an endpoint pair does not silently choose a direction.

## Refinement and match shorthand

The following forms are canonical shorthands:

```deeplus
let count: Int where > 0 = 20
let score: Int in 0..100 = 70

let label = @match score {
    0 <= value <= 100 => "normal"
    otherwise => "abnormal"
}
```

`T where > rhs` inserts the refinement subject `this`. `T in a..b` and
`T in a..<b` form inclusive and upper-exclusive interval refinements.
`T > rhs` is not admitted because it conflicts with the generic-close role of
`>`.

A monotone chained binder Pattern binds the match subject exactly once to its
middle identifier and exposes the resulting refinement fact inside the arm.
Mixed-direction chains reject. Existing Range Patterns, Pattern aliases, and
explicit `if` guards remain available. The fallback separator remains `=>`.

## Guards

- AUTO is available only through a canonical closed synthesis-policy record.
- local/runtime conformance, arbitrary structural synthesis, specialization,
  and child-local parent-witness replacement remain absent.
- static validation does not claim implementation or product support.
- semantic P0 remains zero; the exact existing feature-P1 set remains 22 OPEN.
- the separate M13 actions remain unchanged.
