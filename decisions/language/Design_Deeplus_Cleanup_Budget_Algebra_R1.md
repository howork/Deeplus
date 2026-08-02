# Design Deeplus Cleanup Budget Algebra R1

Status: `CURRENT_DESIGN_STATIC_CONTRACT_LOCAL_CANDIDATE`

Gap: `IR-OWN-P1-021`

Baseline: `howork/Deeplus main@4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`

Product support: `15_OF_15_NOT_RUN`

## Decision

Deeplus retains the existing class-header surface:

```deeplus
cleanup budget {
    effects { io, audit }
    errors CloseError | FlushError
}
```

No grammar production changes. Each axis item occurs at most once. Within a
present block, an omitted `effects` item means the empty EffectRow and an
omitted `errors` item means the empty ErrorSet `Never`. The empty block is an
explicit empty envelope. A whole omitted header on a non-inheritance class
instead exports its exact computed envelope.

Effects and recoverable errors resolve through their canonical identity
domains, expand aliases, reject duplicate normalized identities, and sort into
finite sets. Defects, cancellation, suspension, and authority remain separate
axes. The budget is a static upper envelope, not runtime permission or a value.

## Composition and admission

The compiler records contributions in this evidence order: the base segment's
transitive computed obligation when present, owned cleanup-bearing fields'
effective envelopes in declaration order, and the owner's `def#cleanup` hook
when present. Same-module sealed checking makes the base computation available
without exporting private contribution identities. Both computed rows are
normalized set unions. Every statically reachable contribution is included;
runtime path selection does not narrow the public result.

Admission requires the computed recoverable-error set and effect row to be
subsets of the effective envelope. Unused capacity is admitted. Source evidence
order is not cleanup execution order and cannot change the existing live-object
or construction-abort lifecycle law.

## Sealed resource families

Stable resource inheritance remains limited to one same-module sealed family.
Its root must declare an explicit budget and that envelope is the family
substitutability ceiling. A child without a header inherits the root envelope.
An explicit child may equal or narrow that envelope only if it covers all of
its computed base, field, and hook obligations. Widening either row is rejected.

## HIR and MIR boundary

Typed HIR gives every admitted owner one `CleanupBudgetId` and retains complete
normalized effective rows plus compiler-local contribution evidence. Public API
residue exports the declaration mode, family-root identity, effective rows, and
envelope digest for cleanup-bearing public types, not private contribution
identities.

Verified Deeplus MIR references the envelope from existing construction and
cleanup payloads. Verification recomputes union and subset proofs. No new MIR
operation, runtime budget evaluation, cleanup ordering rule, failure ordering,
loan-close policy, xVM behavior, or Cranelift semantic selection is introduced.

## Diagnostics and examples

The bounded active diagnostic families are duplicate axis/identity,
non-ErrorSet `errors`, computed or inherited envelope exceedance, and the
existing same-module sealed-root requirement. The review corpus binds normal,
boundary, and reject examples under `EX-R33-CBA-*`. The previous
`EX-R51a1-043` brace-free effect item was corpus drift and is corrected to the
unchanged grammar spelling `effects { io }`.

## Status fence

- semantic P0 introduced: `0`
- canonical feature P1: `22_OPEN_UNCHANGED`
- separate actions: `4_OPEN_UNCHANGED`
- production parser/checker/MIR/xVM/runtime/backend/tooling: `NOT_RUN`
- product lanes: `15_OF_15_NOT_RUN`
- GitHub publication: `SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION`

`IR-OWN-P1-021` remains open until this candidate is integrated, focused
validation passes, and an authorized publication closure records canonical
readback. Design-static acceptance is not product implementation.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
