# Design Deeplus Multiline Interpolation Atomic Payload R1

Status: `CURRENT_USER_DELEGATED_DESIGN_ADOPTION`

- effective revision: `r51f3-current-frontend-readiness-r11-r19-r1`
- law ID: `DSGN-CURRENT-MULTILINE-INTERPOLATION-ATOMIC-PAYLOAD`
- implementation-readiness gap: `IR-FE-P0-030`
- production implementation: `NOT_STARTED`
- product lanes: `15/15 NOT_RUN`

## Decision

Multiline strings are emitted through one atomic scanner-stream envelope whose
payload leaves partition the token bytes exactly once. The dedent prefix is the
byte longest common prefix of nonblank content-line indentation; tab and space
remain distinct. The closer indentation is preserved as metadata and does not
participate in dedent calculation.

The parser lazily materializes embedded token tapes under the closed lexical
goals. Plain payloads lower to `ConstString`; interpolated payloads use the
existing top-level interpolation lowering contract. No multiline envelope is a
single lossless-CST leaf, and recovery cannot expose a partially committed
payload as canonical syntax.

This adoption adds no spelling and changes no feature maturity. Final malformed
multiline diagnostics remain owned by `IR-FE-P1-035`; runtime and tooling lanes
remain `NOT_RUN`.
