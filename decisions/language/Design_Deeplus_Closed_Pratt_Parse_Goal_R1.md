# Design Deeplus Closed Pratt Parse-Goal Contract R1

Status: `CURRENT_USER_DELEGATED_DESIGN_ADOPTION`

- effective revision: `r51f3-current-frontend-readiness-r11-r19-r1`
- law ID: `DSGN-CURRENT-CLOSED-PRATT-PARSE-GOAL`
- implementation-readiness gap: `IR-FE-P1-031`
- production implementation: `NOT_STARTED`
- product lanes: `15/15 NOT_RUN`

## Decision

The closed Pratt goal domain is exactly `EXPRESSION`, `PREDICATE`,
`SLICE_INDEX`, `TYPE`, `NON_FUNCTION_TYPE`, and `UNIT`. Dispatch is keyed by
the parse goal and the exact attached token sequence or structured lookahead.
A registered parselet wins only at an admitted binding power, an owner stop
token terminates the goal, and every other pair is rejected.

`PREDICATE` excludes assignment. `SLICE_INDEX` leaves `..` and `..<` to the
slice-range owner. `NON_FUNCTION_TYPE` forbids an outer function tail while an
explicitly nested `TYPE` goal may contain one. `UNIT` admits only symbol,
qualified-symbol, and parenthesized primaries with its closed operators.

Message-call operators are not generic postfix operators: `~` is a
left-associative structured led parselet and `:~` is terminal and
nonassociative, both at binding rank 15.

This is a design and machine-contract adoption only. It adds no spelling,
changes no feature maturity, and supplies no parser, formatter, or product
execution receipt.
