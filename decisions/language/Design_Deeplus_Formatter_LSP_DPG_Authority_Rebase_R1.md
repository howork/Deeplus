# Deeplus Formatter/LSP DPG Authority Rebase R1

## Decision

`ACCEPT_DPG_AUTHORITY_REBASE_AS_LOCAL_IMPLEMENTATION_READINESS_CANDIDATE`

This decision closes audit gap `IR-FE-P1-063` against read-only GitHub main
`10e64f492f0529610673846139afcf0d95175663`. It does not activate syntax,
publish a canonical change, or claim a formatter, LSP, or incremental-parser
implementation.

## Problem

The R28 tooling contract was sound for snapshots and incremental ownership but
still named one EBNF digest and EBNF production identifiers in parse snapshot,
CST content, reuse, and LSP bindings. The parser-oriented cutover later made
`spec/grammar/deeplus.dpg` the structural grammar authority, delegated
contextual admission to `deeplus.parser-contexts.json`, expression parsing to
the closed Pratt contract, and lexical transactions to the scanner contract.
The EBNF remains useful as an exact surface census, but it is not sufficient
source-language authority. Leaving R28 EBNF-bound would allow tooling to admit
or reuse a tree without proving all current parser axes.

## Selected profile

`ParserAuthorityDigestSetR1` contains exactly four ordered axes:

1. `STRUCTURAL_DPG`
2. `PARSER_CONTEXT`
3. `PRATT`
4. `SCANNER`

`ParseSnapshotId`, every incremental-reuse receipt, and every LSP request or
result bind that complete set. A change to any axis forces source-root reparse
and permits zero old-handle reuse. `CstContentId` and reuse receipts bind a
`CstStructuralOwnerId`; an EBNF census production identifier is not structural
ownership authority.

The EBNF digest remains separately bound to the 656-row formatting disposition
census. An EBNF-only change may require census reclassification, but it cannot
change language admission, recovery, AST normalization, or semantic identity.
The formatter and LSP consume the parser ensemble; they never independently
choose parser semantics.

## Rejected alternatives

- A single generic `grammar_sha256` is rejected because it hides which parser
  axis changed and cannot prove DPG, contextual, Pratt, and scanner parity.
- EBNF-only admission is rejected because the EBNF is a non-authoritative
  census after the parser-oriented cutover.
- Reusing EBNF `production_id` as CST ownership is rejected because DPG may
  intentionally collapse equivalent census shapes and route them through
  context-specific commitments.
- Best-effort old-handle reuse after any authority-axis change is rejected;
  the source root is reparsed and all former handles become stale.
- A tooling-owned parser fork is rejected because formatter and LSP are
  projections of canonical parser evidence, not language-design authorities.

## Traceability and evidence

- authority ensemble: `spec/contracts/parser-authority-traceability-r1.json`
- tooling contract: `spec/contracts/formatter-lsp-incremental-parsing-contract-r1.json`
- frontend binding: `spec/frontend/frontend-model.json`
- fixtures: `tests/fixtures/current/formatter-lsp-incremental-parsing-r1.json`
- focused validator: `tools/validators/validate_formatter_lsp_dpg_authority_rebase.py`
- mutation gate: `tools/validators/run_formatter_lsp_dpg_authority_rebase_mutation_tests.py`

The acceptance matrix contains four positive, four boundary, and eight reject
cases. Ten independent mutations cover EBNF promotion, missing authority axes,
stale identity recipes, old-handle reuse, tooling semantic reselection, and
product-support overclaim.

## Governance boundary

Evidence is `E2_STATIC_CLOSURE`. Source syntax, language semantics, grammar
production cardinality, and final diagnostic IDs do not change. Semantic P0 is
`0`; the exact feature P1 set remains `22 OPEN`; all 15 product lanes remain
`NOT_RUN`. The candidate is `APPROVED_NOT_INTEGRATED`, and GitHub publication is
suspended until the user explicitly requests it.
