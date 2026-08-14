# Design Deeplus R78 DPG Implementation Target Traceability Closure R1

## Verdict

`LOCAL_VERIFIED_CANDIDATE_NOT_INTEGRATED`

This bounded repair removes a false implementation-readiness closure without
changing Deeplus language semantics. The parser-oriented DPG remains the
structural grammar authority. The legacy EBNF remains a non-authoritative exact
surface census and cannot independently satisfy a `SOURCE_GRAMMAR` trace cell.

## Baseline and scope

- repository: `howork/Deeplus`
- canonical main baseline: `10e64f492f0529610673846139afcf0d95175663`
- local predecessor: `7d4e6c48b9374bec34a60b970530174dd9b4e145`
- scope: Implementation Target Profile source-grammar evidence only
- language semantic changes: `0`
- feature status changes: `0`
- product execution: `15/15 NOT_RUN`

## Controlling repair

Each directly bound source-grammar cell now carries all four current parser
authority axes:

1. `spec/grammar/deeplus.dpg` — structural entry and delegation points;
2. `spec/grammar/deeplus.parser-contexts.json` — context, owner admission,
   commitment, boundary and external-binding registries;
3. `spec/contracts/closed-pratt-parse-goal-contract-r1.json` — Pratt goals,
   parselets, stop sets, precedence and associativity;
4. `spec/contracts/complete-token-lexical-goal-contract-r1.json` — scanner
   goals, transactions, modes and atomic token outcomes.

Feature-local production names remain exact locators into
`spec/grammar/deeplus.ebnf`, but their evidence class is
`GRAMMAR_SURFACE_CENSUS_ID` and their stage role is explicitly
`SURFACE_CENSUS_NONAUTHORITY`. A direct source cell is rejected unless all
four authority axes resolve. EBNF-only replacement is a failing mutation.

The stale feature locator `StructuralUnfoldArgument` was corrected to the
existing exact census production `PositionalUnfoldArgument`; no source surface
or semantics changed.

## Static acceptance snapshot

- implementation target rows: `469`
- direct source-grammar cells: `438`
- non-applicable source-grammar cells: `31`
- surface census locators: `297`
- legacy EBNF authority evidence: `0`
- blocked/missing/conflicting trace cells: `0/0/0`
- focused mutation cases rejected: `18/18`
- existing feature P1: `22 OPEN`, unchanged
- semantic P0: `0`
- product lanes: `15/15 NOT_RUN`

## Authority and publication fence

The historical G4 audit artifact is preserved unchanged. The successor
revalidation contract records that its old grammar evidence is a historical
snapshot, not current parser authority. This local candidate does not alter
GitHub, current pointer, feature activation, production implementation, or
product-support state. A later explicitly authorized publication cycle must
provide post-merge readback before this repair is canonical on `main`.

## Next blocking cluster

`PREIMPL-P0-003`: repair the structurally impossible target-bound execution
route for `SFD-P1-009` while preserving `OPEN P1 / NOT_RUN` until exact
target-bound execution evidence exists.
