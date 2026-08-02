# Deeplus Formatter, LSP, and Incremental Parsing Contract R1

## Decision

`ACCEPT_MINIMUM_SOUND_PROFILE_AS_LOCAL_IMPLEMENTATION_READINESS_CANDIDATE`

This decision closes the design ambiguity identified by `IR-FE-P1-037` in the
R28 local candidate. It does not publish the candidate, activate new source
syntax, or claim formatter, LSP, or incremental-parser implementation.

Baseline:

- repository: `howork/Deeplus`
- branch: `main`
- commit: `39a5d50cc770341c4b9776d00d84520b780d0c62`
- tree: `b19b2a86c0f29c1f73763c8526a3a7bde23d530a`

## Chosen profile

The formatter is a deterministic projection over the existing lossless CST.
The 644 R47 grammar productions are covered by six total, disjoint
disposition classes with exact counts `56/35/320/204/10/19`. An explicit owner
rule may change only its declared whitespace or layout slots. Token spellings,
comments, and their lossless owners remain fixed; when a unique rule is absent,
exact source bytes are preserved. Every rewrite proves equal
`NormalizedAstSemanticDigest` values and second-pass idempotence. It does not
require occurrence-local `AstNodeId` values to remain equal.

The five R41 Actor productions are part of that exact domain.
`ActorProtocolConformanceClause` and `ActorProtocolConformBlock` are structural
FD-04 owners; `ActorMemberDecl`, `ActorProtocolConformanceBody`, and
`ActorProtocolConformanceItem` are inline FD-03 owners. The formatter preserves
the distinct `conforms` header and body-local `conform` surfaces, qualified type
references, required line-break boundaries, and comment ownership. It never
moves a comment across an Actor header/body boundary or converts one owner into
the other. Formatting and incremental reparsing must recompute the same R41/R23
Actor semantic identities from the normalized source; no CST or editor handle
may become an Actor identity preimage.

Whole-file formatting rejects recovery-tainted input. Range formatting selects
one smallest recovery-free structural owner, emits one replacement, and proves
that bytes outside the owner are unchanged. The formatter and checker cannot
clear recovery taint.

Incremental reparsing uses lexical expansion, smallest eligible owner
selection, deterministic parent ascent, and source-root fallback. A subtree is
spliced only after the old owner interval has been transformed through the
ordered edit set into one exact new interval and token interval, scanner state,
profile/digest, byte partition, production owner, and unique node-reuse proofs
all close.

Editor identities are separated into session, revision, snapshot, CST content,
CST occurrence, incremental handle, and reuse-receipt domains. `CstNodeId` is
the serialized, snapshot-scoped representation of exactly one
`CstOccurrenceId`; `CstContentId` is position-independent content and an
`IncrementalNodeHandleId` is only a session-local editor handle. Equal content
does not equate occurrences or handles. A reuse receipt names both old and new
revision/snapshot identities, the old interval, its deterministic edit transform
and the new interval, and proves a one-to-one mapping. None is a canonical
language, HIR, MIR, ABI, or runtime identity.

Each document head is an immutable snapshot published by compare-and-swap from
the exact expected old revision. A parse or LSP worker holds a lease on the
snapshot it reads; the lease preserves storage, not currentness. Losing the CAS
or observing a different head makes the result stale: it is rejected, never
merged or silently retried, and all leases are released exactly once.

LSP storage coordinates are zero-based half-open UTF-8 byte intervals. A
session negotiates one declared position encoding; line/character positions are
converted against the bound snapshot and must land on exact scalar boundaries.
Out-of-range, split-scalar, stale, or differently encoded positions are rejected
without clamping. Requests and results echo the exact revision, snapshot,
encoding, source role/profile, grammar digest, frontend digest set, and source
bytes digest.

A full parse and an admitted incremental parse of the same bound source must
produce the same normalized semantic digest and the same ordered diagnostics:
primary identity, arguments, byte span, related information, fix-it and cascade
suppression. Task completion order cannot reorder diagnostics. Reused
diagnostics require an unchanged owner and dependency proof; any intersecting
or dependency-invalidating edit recomputes the affected diagnostic closure.

Failure precedence is fixed: validate the request/session/encoding envelope;
bind the exact expected revision and snapshot; validate and convert positions
and edits; perform lexical expansion, parse and splice checks; enforce recovery,
semantic-digest, diagnostic-parity, range and idempotence gates; then publish by
CAS. An earlier failure suppresses later tooling failures, and a final CAS loss
returns the stale-result outcome without publishing partial state.

## Rejected alternatives

- Best-effort formatting of unknown owners is rejected because it makes source
  spelling depend on implementation order and can change meaning.
- Recovery-node deletion by the formatter is rejected because it would turn an
  analysis artifact into false canonical evidence.
- Byte-offset node identity is rejected because edits invalidate positions and
  duplicate subtrees make reuse ambiguous.
- Treating `AstNodeId` equality as formatting equivalence is rejected because
  it is occurrence-bound; `NormalizedAstSemanticDigest` is the semantic proof.
- Unbounded incremental fallback is rejected; ascent is deterministic and ends
  at the selected source root.
- Cross-revision LSP result merging is rejected because it mixes authority from
  different source bytes and parser snapshots.
- Position clamping and best-effort encoding conversion are rejected because
  they can target a different token than the request names.

## Traceability

- exact contract:
  `spec/contracts/formatter-lsp-incremental-parsing-contract-r1.json`
- schema:
  `schemas/language/formatter-lsp-incremental-parsing.schema.json`
- positive/boundary/negative fixtures:
  `tests/fixtures/current/formatter-lsp-incremental-parsing-r1.json`
- focused validator:
  `tools/validators/validate_formatter_lsp_incremental_parsing.py`
- frontend binding: `spec/frontend/frontend-model.json`
- human-readable authority: `spec/language.md`, section 52

The successor validation binds all 644 disposition rows, including the five
Actor rows, and covers semantic-digest parity, old/new snapshot reuse,
interval transforms, CAS loss, stale LSP results, position-encoding rejection,
diagnostic ordering/cascade parity, and failure precedence. It adds zero grammar
productions, source spellings, language semantics, or final diagnostic IDs.

## Evidence and remaining boundary

Evidence level is `E2_STATIC_CLOSURE`. Product execution remains `NOT_RUN` for
the formatter, LSP, and incremental parser. Semantic P0 remains `0`, the exact
canonical feature P1 set remains `22 OPEN`, and all 15 product lanes remain
`NOT_RUN`. This bounded rebase claims neither production implementation nor
GitHub publication; canonical promotion and publication closure remain separate
receipted steps.
