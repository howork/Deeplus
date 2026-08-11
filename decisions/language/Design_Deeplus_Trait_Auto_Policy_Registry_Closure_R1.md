# Trait Auto-Policy Registry Closure R1

Status: `LOCAL_VERIFIED_DESIGN_CANDIDATE`
Feature action: existing `TCC-P1-005` remains OPEN
Product support: `15/15 NOT_RUN`

## Decision

`supports auto` is not a user-extensible policy language. It is a source-level
assertion on a core/Prelude-owned Trait that the exact normalized `TraitId` has
one current row in `TraitAutoPolicyRegistryV1`. The declaration does not create,
modify, inherit, discover, or prioritize a policy. A user-owned Trait carrying
the clause is rejected. The machine owner constant is
`CORE_OR_PRELUDE_ONLY`.

`by auto` is a bodyless request for that exact row. Before canonical HIR the
checker binds `TraitAutoPolicyId`, policy version and digest, finite normalized
input evidence, deterministic algorithm ID, synthesized `ConformanceId`, and
the emitted `TraitWitnessId` set. Missing or mismatched rows yield zero
candidates. Extensions, providers, same-named members, source/import order and
runtime state never contribute evidence.

The current registry contains exactly two core responsibility policies:

- `TraitId:core::Shareable` using `ShareableObservationSafe`;
- `TraitId:core::Transferable` using `TransferableAcrossIsolation`.

Both reuse `RESPONSIBILITY_STRUCTURAL_FIXED_POINT_R1` and its finite nominal
graph, memoized pair and cycle-detection law. `Display`, `Eq`, `Ord`, arbitrary
user Traits and Preview `DeepClone` have no current auto-policy row. Adding a
row is an API- and authority-changing registry revision, not an effect of source
declaration.

Successful synthesis creates no runtime lookup or new MIR operation. The
generated conformance and witness are ordinary sealed static evidence; policy
identity and derivation digest remain in HIR and public conformance residue.

This closes the availability/constructibility ambiguity inside `TCC-P1-005`.
It does not close the feature P1 and does not claim parser, checker, MIR, xVM,
Cranelift, formatter or LSP execution.
