# Deeplus Member Visibility Omission Closure R1

## Decision

`APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE`

This decision closes audit gap `IR-VIS-P1-057` at the design and static-contract
level. It does not change the source spelling, activate a product parser or
checker, or publish to GitHub. The exact machine contract is
`spec/contracts/member-visibility-omission-v1.json`.

## Problem

R58 correctly preserved a missing member sigil as `OMITTED`/`null` in CST and
AST, because the parser cannot infer the declaration's semantic owner. It then
delegated resolution to an immediate parent-owner contract that did not exist.
Consequently a compiler had to choose whether an omitted method, promoted
field, Trait fulfillment, actor operation, accessor, or bitfield slot was
private, inherited, public, or invalid. Leaving the value null until access or
API projection is not sound: it makes HIR identity and interface residue depend
on implementation policy.

## Closed rule

The parser still preserves exactly four surface states:
`EXPLICIT_MINUS`, `EXPLICIT_HASH`, `EXPLICIT_PLUS`, and `OMITTED`. Omission is
not a fourth visibility rank and there is still no global default. After name
and slot binding identifies the exact parent context, the checker applies one
of the following owner rows before canonical HIR sealing.

| owner | omitted result |
|---|---|
| `MemberFunctionDecl` | inherit the original slot for an override; otherwise `PRIVATE` |
| `TypeSideMemberFunctionDecl` | inherit the exact associated-function requirement domain inside a conformance; otherwise `PRIVATE` |
| `ConstructorDecl` | `PRIVATE` |
| `StoredParameter` | generated field is `PRIVATE`; construction input visibility remains a separate responsibility |
| `FieldDecl` | `PRIVATE` |
| `TypeSideFieldDecl` | `PRIVATE` |
| `AccessorDecl` | each omitted `get` or `set` is independently `PRIVATE` |
| `ForwardDecl` | every generated forward slot is `PRIVATE` |
| `TraitMethodDecl` | inherit an original supertrait slot for an override; otherwise `PRIVATE` |
| `ConformanceMethodDecl` | inherit the exact selected Trait requirement visibility |
| `ExtensionSetFunctionDecl` | `PRIVATE` |
| `ActorOnDecl` | derive the standalone Actor visibility, or the actor/protocol effective transport visibility in a conform block |
| `ActorRequestDecl` | same transport rule as `ActorOnDecl` |
| `BitfieldNamedSlot` | `PRIVATE` |
| `FlagNamedSlot` | `PRIVATE` |

"Private by default" therefore applies only to newly declared member slots. It
does not silently narrow a responsibility that the declaration fulfills.
Omitted override and conformance visibility restate no responsibility; they
inherit the already selected original slot. A missing original slot or
requirement is rejected instead of falling back to private.

Actor operations are the other deliberate exception. Their transport domain is
owned by the Actor declaration and, for protocol fulfillment, is exactly
`meet(ActorDecl.visibility, ActorProtocolDecl.visibility)`. It can therefore be
`private`, `common`, or `public`; it is not reconstructed as an unrelated
member sigil. This preserves concise public-Actor examples while keeping the
existing actor binding table's "handlers have no independent protocol
visibility" law.

## Frontend and HIR boundary

CST and AST retain the source state and token span. Resolution then records
`resolution_kind`, one concrete `effective_domain`, and an anchor when the row
requires one. Canonical HIR and module API admit neither `OMITTED` nor a null
effective domain. A grouped `forward` expands only after this resolution, so
all generated slots receive one identical domain.

The decision creates no runtime visibility lookup, MIR operation, xVM
instruction, or backend rule. Access checking consumes the sealed effective
domain. Formatter and LSP preserve whether the source was explicit or omitted;
they do not print a synthesized sigil unless a separately requested explicit
refactoring proves byte-preserving semantic equivalence.

## Diagnostic order

1. forbidden top-level visibility word on a member;
2. invalid owner/parent-context pair;
3. missing required original slot, requirement, Actor, or ActorProtocol anchor;
4. explicit override narrowing;
5. explicit Trait-requirement mismatch;
6. use outside the resolved access domain.

The two new closure diagnostics are
`MEMBER_VISIBILITY_OMISSION_OWNER_CONTEXT_INVALID` and
`MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING`. A rejection produces no canonical
HIR or module API residue.

## Alternatives rejected

- **One global private default** was rejected because it silently narrows
  conformance implementations, overrides, and public actor transport.
- **One global public default** was rejected because it widens ordinary fields,
  constructors, helpers, bitfield slots, and extension members.
- **Require a sigil everywhere** was rejected because omission is already a
  deliberate current surface and concise responsibility fulfillment should not
  repeat an authority owned by the selected slot.
- **Keep null in HIR** was rejected because access and API identity would remain
  implementation-defined.

## Evidence boundary

This is E2 structured-static evidence. The reference validator exercises every
owner row plus override, associated requirement, actor/protocol meet, grouped
forwarding, missing-anchor, and invalid-context boundaries. Product execution
remains `15/15 NOT_RUN`; semantic P0 remains `0`; the exact existing feature P1
set remains `22 OPEN`; GitHub publication is not performed.
