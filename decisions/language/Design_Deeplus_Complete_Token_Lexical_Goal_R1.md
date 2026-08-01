# Design Deeplus Complete Token and Lexical-Goal Contract R1

Status: `CURRENT_USER_DELEGATED_DESIGN_ADOPTION`

- effective revision: `r51f3-current-frontend-readiness-r11-r19-r1`
- law ID: `DSGN-CURRENT-COMPLETE-TOKEN-LEXICAL-GOAL`
- implementation-readiness gap: `IR-FE-P1-032`
- production implementation: `NOT_STARTED`
- product lanes: `15/15 NOT_RUN`

## Decision

The scanner uses a closed lexical-goal and complete-token registry. Token
selection follows the declared priority order, performs speculative forms in
failure-atomic transactions, and never commits an incomplete prefix. Trivia,
ordinary atomic tokens, interpolated-part tokens, and mode transitions have
separate owners.

Rational-looking input uses the bounded rational probe and falls back without
losing bytes when the complete rational token is not admitted. String,
interpolation, raw-string, byte-string, and multiline modes obey their declared
delimiter and transition owners. Scanner success preserves an exact source-byte
partition for the parser.

This adoption changes no surface syntax or feature status. Final malformed-form
diagnostic code, span, and fix-it bindings remain owned by `IR-FE-P1-035`.
