# Design: Enum body commitment and match fallback boundary

Status: `CURRENT_DESIGN_STATIC_VALIDATED_PRODUCT_NOT_RUN`

Baseline main: `10e64f492f0529610673846139afcf0d95175663`

Audit gap: `IR-PARSE-P1-059`

Contract identities: `EnumBodyCommitmentV1` and `MatchFallbackBoundaryV1`

## Decision

Current Enum declarations are inhabited nominal sums. An `EnumBody` therefore
contains at least one bare `EnumCase` before any Enum member. `{}` and a body
whose first item is a member are rejected with `ENUM_BODY_REQUIRES_CASE`.

After the first case, the next structural boundary commits one of two modes:

- comma mode: a same-line list of at least two cases, with one optional trailing
  comma and no member declarations;
- layout mode: one or more layout-separated cases followed by the admitted Enum
  member sequence.

One comma followed immediately by `}` is rejected with
`ENUM_COMMA_MODE_REQUIRES_TWO_CASES`. Mixing comma and layout case separators
remains `ENUM_CASE_SEPARATOR_MIXED`. Empty Enum remains non-current; this repair
does not create a bottom-type, uninhabited nominal or FFI placeholder profile.

`otherwise` is the sole fallback head for match and declarative clause families.
It is unguarded, occurs at most once and is final. The exact source form is
`otherwise => body`. `otherwise if condition => body` is rejected by the parser
with `OTHERWISE_GUARD_FORBIDDEN`; no guarded fallback AST is formed. Duplicate,
non-final and exhaustiveness diagnostics remain independently ordered after that
surface gate.

## Implementation boundary

The lossless CST preserves Enum mode and match-arm head identity. Normalized AST
contains a nonempty Enum case vector and distinguishes `PatternMatchArm` from
`OtherwiseMatchArm`. The fallback node has no guard field. Rejected input has no
HIR/MIR/runtime residue. Product parser, checker, formatter and LSP execution
remain `NOT_RUN`.

This current stable design decision creates or closes no feature P1. The
existing 22 feature P1 remain OPEN, semantic P0 remains 0, and product
execution remains `15/15 NOT_RUN`. This bounded authority repair does not claim
GitHub publication or product implementation.
