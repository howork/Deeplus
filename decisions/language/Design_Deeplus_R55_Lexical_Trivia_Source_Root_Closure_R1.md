# Deeplus R55 Lexical Trivia and Source-Root Closure

Status: `LOCAL_STABLE_DESIGN_CANDIDATE`

Canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`

Local predecessor: `89ded1ab5c9110476f7043e5f44b71ddd72d19a1`

GitHub publication: `SUSPENDED`

## Decision

R55 closes the implementation-handoff predicates for nine already Stable-design
lexical and source-root features. It adds no programmer-visible spelling and
does not activate a feature. The bounded contract is
`spec/contracts/lexical-trivia-source-root-attachment-r1.json`.

The scanner resolves shared comment prefixes in the fixed order `//!!`, `//!`,
`//-`, then `//`. A word comment consumes maximal nonempty
`UnicodeXIDContinue`, is byte-adjacent to exactly one eligible completed left
anchor, preserves one CST trivia occurrence, and is erased before normalized
AST and semantic processing.

A documentation `DocGroup` attaches only inside one declaration container.
Horizontal whitespace and the contract's bounded physical-line separation are
allowed; blank lines, ordinary or word comments, shebang, container boundaries,
and EOF are fences. An annotation cluster does not break attachment when it
belongs to the same underlying documentable declaration. The parser attachment
pass owns `DOC_COMMENT_NOT_ATTACHED_TO_DECL`.

All six direct Stable/Preview library, executable, and script roots explicitly
end in `EOF_TOKEN`. Success requires exact trailing-trivia ownership, parser EOF,
and scanner byte exhaustion. Specific committed lexical/item diagnostics precede
`SOURCE_TRAILING_TOKENS`; failed roots commit no canonical source-unit AST.

## Traceability closure

| Measure | Exact result |
|---|---:|
| Target features | 9 |
| Prior blocked cells | 38 |
| `BOUND_DIRECT` transitions | 18 |
| `BOUND_DELEGATED` transitions | 0 |
| `NOT_APPLICABLE` transitions | 20 |
| New bounded acceptance cases | 10 |
| Total overlay acceptance bindings | 18 |
| Ledger direct cells after R55 | 2416 |
| Ledger delegated cells after R55 | 1 |
| Ledger N/A cells after R55 | 501 |
| Ledger blocked cells after R55 | 1303 |

The structural N/A decisions are stage fences, not missing evidence: lexical
trivia has no canonical AST identity, static type effect, or dynamic lowering;
closed scanner modes have no programmer-visible AST/runtime identity; source
root full consumption is a parser commit predicate; ordinary line comments have
no distinct rejection class.

## Governance fences

- semantic P0: `0`
- feature P1: exactly `22 OPEN`, unchanged
- M13 actions: exactly `4 OPEN`, unchanged
- product lanes: `15/15 NOT_RUN`
- production implementation claim: `NONE`
- GitHub source/branch/PR/merge mutation: `0`

Static validators establish design-contract and evidence binding only. They do
not claim lexer, parser, formatter, LSP, runtime, or product execution support.
