# Deeplus Frontend CST, Parser, Scanner, and Recovery Readiness R1

## Decision

The R12 through R18 frontend design candidates are accepted as one current
Stable-design implementation contract. This adoption changes no source spelling,
feature profile, or grammar byte. It makes previously implicit frontend
responsibilities deterministic while all production lanes remain `NOT_RUN`.

The canonical machine sources are:

- `spec/contracts/frontend-cst-boundary-recovery-contract.json` for R12–R14;
- `spec/frontend/frontend-model.json` for the R15–R18 Pratt, token, shorthand,
  and multiline bindings;
- `tests/fixtures/current/frontend-cst-boundary-recovery-r1.json` and
  `tests/fixtures/current/frontend-pratt-scanner-interpolation-r1.json` for the
  positive, boundary, negative, and mutation oracles.

## R12: lossless CST and normalized AST

Every production in the exact 638-production Grammar has one disposition:
`cst_only`, `ast_node`, `normalize_to`, or `external_parser_entry`. Recovery
kinds are separate `reject_before_ast` records. The projection is total over
the grammar digest bound by the machine contract. Ten source-sugar families
have exact normalization targets. CST preserves source bytes, tokens, trivia,
missing/unexpected evidence, and source form; normalized AST contains semantic
syntax only. Recovery data has zero canonical AST, HIR, MIR, or API residue.

## R13: contextual boundaries and match arms

`LineBreakBoundary` and `StatementBoundary` are parser-state decisions rather
than indentation heuristics. A newline ends a complete owner only when no
registered continuation is available at the owner's delimiter depth. `}` is
not a statement boundary; its enclosing grammar owner decides final-item
admission. Match-arm bodies select braced, control-transfer, or direct-expression
ownership by exact context. Newline starts a next arm only after a diagnostic-free,
non-consuming transactional parse of `MatchHead GuardClause? =>`. The open-range
tie-break and body stop rules are fixed in the contract.

## R14: bounded recovery and invalid-tree quarantine

Recovery chooses exactly one of structural insertion, one-token deletion,
nonempty skip to a context sync point, or budget termination. It never invents
an identifier, semantic operator, ownership/effect marker, authority, or
conformance. Every edit makes strict progress and every recovery episode taints
its containing CST root. `STRICT_CANONICAL` produces no analysis AST;
`ANALYSIS_RECOVERY` may expose quarantined analysis-only trees, but neither mode
allows tainted data into canonical AST/HIR/MIR or public artifacts.

## R15: closed Pratt goals

The exact parse-goal domain is `EXPRESSION`, `PREDICATE`, `SLICE_INDEX`, `TYPE`,
`NON_FUNCTION_TYPE`, and `UNIT`. Dispatch is goal plus exact attached token or
structured lookahead. Unknown or disabled pairs reject. `~` and `:~` are rank-15
structured led parselets; they are not rank-190 postfix members. `PREDICATE`
forbids assignment, `SLICE_INDEX` leaves range ownership to `SliceRange`,
`NON_FUNCTION_TYPE` forbids an outer function tail, and `UNIT` has its own
closed primary and operator set.

## R16: complete token and lexical goals

The scanner registry is total over grammar terminals, Pratt token components,
hard/contextual words, parser-visible atomic tokens, and retained trivia. Scanner
mode and parser lexical goal are independent. Token probes are transactions:
failed probes consume no bytes or tokens, emit no diagnostics, and restore the
exact checkpoint. Rational literal probing is enabled only at expression prefix
in normal or interpolation-code mode. `array` and `case` remain ordinary
identifiers.

## R17: shorthand interpolation

Shorthand interpolation admits only an identifier or `@` root followed by
read-only member/static-index selectors. `${` wins before shorthand. A committed
but incomplete selector rejects rather than becoming text. Other ordinary
delimiters terminate the complete path without consumption and are reprocessed
in String mode. Calls, mutation, await, assignment, arbitrary expressions, and
format suffixes require the existing braced form. The optional backtick boundary
is retained only in lossless CST.

## R18: multiline atomic payload

`MULTILINE_STRING_LITERAL` remains one parser-stream token envelope carrying
`MultilineStringTokenPayloadV1`; it is not itself a CST leaf. Payload leaves
partition source bytes exactly once. Dedent removes the longest exact common
space/tab prefix of nonblank content lines; closer indentation is metadata only.
Embedded token tapes are materialized lazily under the R16 lexical goals and
then parsed by the R17 shorthand or R15 braced-expression contract. Plain
content lowers to `ConstString`; interpolated content uses the existing ordered,
evaluate-once rendering transaction.

## Diagnostic and evidence fence

The contracts fix parser/scanner reason oracles but do not create public
diagnostic registry IDs. Final malformed-selector and interpolation diagnostic
ownership remains `IR-FE-P1-035`. This adoption closes no canonical feature P1,
keeps the exact feature set at 22 OPEN, keeps M13 actions at 4 OPEN, and leaves
all 15 product lanes `NOT_RUN` until production scanner/parser/checker/tooling
receipts exist.
