# Design Deeplus Shorthand Interpolation State Machine R1

Status: `CURRENT_USER_DELEGATED_DESIGN_ADOPTION`

- effective revision: `r51f3-current-frontend-readiness-r11-r19-r1`
- law ID: `DSGN-CURRENT-SHORTHAND-INTERPOLATION-STATE-MACHINE`
- implementation-readiness gap: `IR-FE-P1-033`
- production implementation: `NOT_STARTED`
- product lanes: `15/15 NOT_RUN`

## Decision

Shorthand interpolation is scanned by the closed state machine bound in the
frontend model. It recognizes only the admitted shorthand host forms, preserves
the exact source partition, and stops at the first token that cannot belong to
the shorthand path. Delimited interpolation continues to use its existing
parser-owned expression goal.

The scanner determines token boundaries; the parser and checker retain name,
member, type, purity, and availability responsibilities. Recovery does not
materialize an admitted shorthand AST from a malformed token sequence.

This adoption adds no syntax and does not claim implementation support. Final
diagnostic metadata remains delegated to `IR-FE-P1-035`.
