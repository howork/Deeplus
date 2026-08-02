# Deeplus Ownership Type Qualifier Normalization — R1

Status: `LOCAL_NONCANONICAL_NONACTIVATABLE`

Decision: `APPROVED_FOR_LOCAL_IMPLEMENTATION_READINESS_CANDIDATE`

Gap: `IR-OWN-P1-018`

Baseline repository: `howork/Deeplus`

Baseline branch: `main`

Baseline commit: `4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`

Baseline tree: `49831ccd810ee4aa4e419ce6a414b54950977549`

Product support: `NOT_RUN`

GitHub publication: `SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION`

## Decision

Deeplus retains all four already-published type prefix spellings and closes
their implementation contract. The normalized `TypeOwnershipQualifier` domain
is exactly `UNQUALIFIED`, `OWNED`, `BORROWED`, `MUT`, and `INOUT`.

- `UNQUALIFIED` delegates value responsibility to the base type.
- `OWNED` makes value ownership and transfer/cleanup responsibility explicit
  while retaining the base reusable-or-affine class.
- `BORROWED` is a region-bound shared read-only view.
- `MUT` is a unique mutable owner.
- `INOUT` is a region-bound exclusive mutable view.

The qualifier is neither a representation nor an ABI decision. Every wrapper
is invariant. Alias expansion leaves zero or one qualifier; stacking is
rejected rather than erased or source-order selected.

Parameter mode and type qualifier remain separate identities. `mut value: T`
is a callee-local mutable channel, while `value: mut T` is an ordinary channel
whose value type is a mutable owner. A channel mode plus a qualified input is
not silently combined.

## Function type reachability repair

The audit found a bounded source-truth contradiction in the same identity
boundary. Published Stable signatures use `(borrow T) -> R` and
`(inout T) -> R`, but `ParenTypeItem` previously admitted only `TypeRef`.
`borrow` therefore had no TYPE NUD, and `inout` could be misclassified as a
general qualifier.

No new punctuation or spelling is introduced. `ParenTypeSyntax` already
classifies its contents only after observing the optional `->`. When that same
outer owner observes `FunctionTypeTail`, a direct item-leading
`borrow|mut|move|inout` is committed to `FunctionTypeParameter.channel_mode`.
Without `->`, it is not a function-mode item. A qualified input that begins
with an overlapping token uses an inner TypeRef grouping:

```deeplus
#scoped (inout Buffer) -> Unit
((mut Buffer)) -> Unit
```

The first is an exclusive caller-place channel. The second is an ordinary
channel whose input value is a `MUT(Buffer)` owner.

## Context and escape profile

`OWNED` and `MUT` may survive local, parameter, result, storage, and public API
positions when the base type is independently admitted. `BORROWED` requires
one exact owner region. A borrowed result requires an invocation-bounded
callable plus exactly one input or receiver origin recorded in HIR and module
API residue. `INOUT` is limited to a local or private invocation-bounded view
and is forbidden from fields, statics, results, public residue, captures,
suspension, actor/concur transfer, and FFI.

Concrete `RegionId` values remain value-level HIR/MIR identities. Public API
residue records only the qualifier and origin channel relation. It never
invents lifetime source syntax.

## Diagnostics and lowering

Missing or escaping borrowed/inout regions select
`BORROW_ESCAPE_OWNER_REGION`. Qualifier stacking, identity-only use, and other
illegal qualifier contexts select `OWNERSHIP_MODE_ADMISSION_FAILED`.
`INOUT_ALIAS_CONFLICT` and `PLACE_STATE_JOIN_MISMATCH` remain later
place-analysis diagnostics.

HIR retains the qualifier separately from base type, parameter mode, region
relation, and responsibility profile. MIR uses the existing
`REUSABLE|OWNED|BORROWED|INOUT` ownership domain plus place mutability and exact
region/loan identities. Cranelift consumes the verified MIR plan and never
reselects source ownership.

## Alternatives rejected

1. Limiting the first milestone to unqualified and mutable owners was rejected
   because all four spellings and borrowed/inout contracts are already Stable
   and used by the canonical Prelude. A fail-closed complete table is smaller
   than maintaining reachable but semantically unspecified syntax.
2. Treating the first word of every function input as a type qualifier was
   rejected because it erases the published callback channel mode.
3. Adding a colon or another new function-type spelling was rejected because
   the existing outer-parenthesis commitment can disambiguate without source
   migration.
4. Exporting concrete region IDs or inventing lifetime syntax was rejected;
   public residue records the stable origin-channel relation only.

## Evidence boundary

This decision closes a design and implementation-handoff ambiguity in a local
candidate. It is not canonical publication, parser/checker/runtime/backend
implementation, conformance execution, activation, or product support.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
