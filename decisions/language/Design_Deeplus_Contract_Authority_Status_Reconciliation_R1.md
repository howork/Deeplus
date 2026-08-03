# Deeplus Contract Authority Status Reconciliation R1

Status: `LOCAL_CANONICAL_CANDIDATE / APPROVED_NOT_INTEGRATED`

## Decision

Five current contract files retain candidate-era status fields because those fields participate in byte- and digest-bound historical evidence. Rewriting them would create a broad hash cascade without changing Deeplus syntax or semantics.

`spec/contracts/current-contract-authority-status-r1.json` is therefore the typed precedence registry for those exact bytes. Its `current_authority` object is the active authority interpretation. Embedded fields listed under `historical_provenance.field_values` are immutable predecessor provenance and must not be interpreted as the current integration state.

The registry may declare a contract `CANONICAL_CURRENT` only when it binds the exact contract SHA-256, the exact gap identity, the semantic publication commit, the publication-closure commit, and an existing canonical closure receipt. `current_binding: false` in the managed-reference profile remains a prohibition on artifact self-binding; it does not mean that the contract is unintegrated.

## Scope fence

- Source spelling change: `0`
- Language semantic change: `0`
- Canonical feature P1 change: `0` (`22 OPEN` remains exact)
- Product execution: `15/15 NOT_RUN`
- Production implementation: `NOT_RUN`
- GitHub publication in R53: `SUSPENDED`

This local candidate closes only the metadata interpretation ambiguity `IR-XCUT-P1-053` after canonical publication and readback. Until then its gap disposition is `APPROVED_NOT_INTEGRATED`.
