# Deeplus Parser-Oriented DPG Cutover R1

## 0. Decision identity

```text
decision_id: DSGN-CURRENT-PARSER-ORIENTED-DPG-CUTOVER-R1
repository: howork/Deeplus
baseline_commit: da734c608c0d583a671c0da9e14da00bff42affd
baseline_tree: ab37f3a91745c3b90e87eeaf15868007ef08ef69
authority: Codex Design_ under the user's delegated language-design authority
status: CURRENT_DESIGN_STATIC_VALIDATED_PRODUCT_NOT_RUN
source_surface_change_count: 0
product_lanes: 15/15 NOT_RUN
```

## 1. Decision

`spec/grammar/deeplus.dpg` is the exact compact structural parser grammar for
the current Deeplus source language. It is interpreted together with the
closed ParserContext registry in
`spec/grammar/deeplus.parser-contexts.json` and the parser-facing contracts in
`spec/frontend/frontend-model.json`.

The DPG is intentionally not a complete frontend encoded as a context-free
grammar, and standard EBNF notation is not a requirement. Deeplus targets a
handwritten recursive-descent parser with closed contextual dispatch and Pratt
parsers. The responsibility boundary is:

| Layer | Canonical responsibility |
|---|---|
| scanner | characters, Unicode/XID, trivia, strings and interpolation modes, numeric transactionality, and longest-match compound tokens |
| DPG | source roots, structural token order, parser entry shapes, and explicit delegation points |
| ParserContext / Pratt | contextual words, owner admission, commitment, attachment, stop sets, precedence, associativity, and parselet registration |
| lossless CST / recovery | byte and trivia preservation, recovery nodes, synchronization, and stable source ownership |
| AST / checker | normalization and name, type, effect, ownership, and coherence legality |

No layer may silently widen the accepted source language. A recovery node may
support analysis but creates no canonical AST, HIR, MIR, API, or conformance
residue.

The former `spec/grammar/deeplus.ebnf` is retained byte-for-byte as a
non-authoritative differential surface census. Its 656 rows remain useful as a
CST/AST/formatter responsibility crosswalk, but they are not a second grammar
authority and do not force the DPG to repeat the whole frontend.

## 2. Input disposition

| Input | Disposition |
|---|---|
| `Deeplus_Grammar_Current_Main_Audit_R77_2026-08-07.zip` | accepted as audit evidence; all five findings resolved or explicitly fenced |
| `Deeplus_Grammar_Parser_Oriented_Rewrite_R1.zip` | accepted with repairs; compact layered architecture retained, bindings and contextual owner rules closed |

The audit package SHA-256 is
`a6b0c24f597ba2eb7b1e29fc9355c4ca37f7c80f25c63b4d6966b719e73e9453`.
The rewrite package SHA-256 is
`02cf62b2f78ef38d642b999d7ff3a08b8283d3b37dbdd5c166255b08d9fbacd2`.

## 3. Differential closure

The design/static validator binds:

- 280 DPG rule families and 301 context-specialized clauses;
- all 656 legacy surface-census rows in their exact order;
- all 181 nonlexical terminal spellings with zero loss;
- every `@Set`, dispatcher, admission predicate, Pratt entry, scanner outcome,
  parser slot, and metanode with zero unbound external;
- every non-null normalization target to the closed AST kind domain with zero
  domain misses.

Six mutation cases are rejected: unknown set, tilde trailing-comma drift,
spaced `: ~` actor-message attachment, missing `AST/CallExpr`, missing Preview
gate, and entry-parameter owner-context drift.

The following boundaries are intentional:

- an ordinary parenthesized call may own a trailing comma; a tilde argument
  sequence has no closing delimiter and does not;
- `:~` is one longest-match attached scanner outcome, while `: ~` is not the
  same operator;
- parameter forms are selected by their owning parser context rather than by a
  copied universal parameter production;
- recovery and post-parse semantic rules stay outside the structural DPG.

## 4. Evidence boundary and governance

This cutover changes no Deeplus source spelling or language meaning. Semantic
P0 remains 0, the exact feature P1 set remains 22 OPEN, the four M13 actions
remain separate and OPEN, and all 15 product lanes remain `NOT_RUN`.

Static differential closure does not claim production scanner/parser
execution, CST round-trip execution, AST normalization execution, formatter or
LSP support, activation, publication, or product conformance. Those require a
future target-bound implementation receipt.
