# R62 Trait-Qualified Associated Static Selection Dynamic Trace Closure

Status: `LOCAL_APPROVED_CANDIDATE`

Canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`

Local predecessor: `0346f2cdd417618ffa0af144a1c37569da63a4c4`

Scope: exactly the
`trait_qualified_associated_static_selection / DYNAMIC_LOWERING` cell. This
decision repairs the descriptor that connects an already admitted
`<T as Trait>::item` selection to existing HIR-H1 and Deeplus MIR identities.
It changes no source spelling, grammar production, AST/HIR node kind, MIR
operation or terminator, source activation, feature P1, or product-support
claim.

## Closed static identity residue

The frontend interns one immutable `TraitAssociatedStaticSelectionId`. Its
descriptor preserves exactly these seven semantic axes:

1. `TraitId`
2. `RequirementId`
3. `ConformanceId`
4. `TraitWitnessId`
5. `ImplementationId`
6. `SubstitutionId`
7. `ResponsibilityId`

The descriptor also records the selected item kind. For an associated
function, `ImplementationId` maps one-to-one to the existing HIR
`CallableImplementationId`; the two names describe the language-level selected
implementation and its callable HIR projection, not two independently selected
candidates. The mapping is complete before HIR emission, injective within the
compilation identity domain, and cannot be reconstructed from a machine
address, spelling, source order, or runtime witness search.

`TraitAssociatedStaticSelectionId` is a closed static identity admitted by the
existing `STATIC_REF` operation. It is not a new HIR node or MIR opcode.

## Associated item lowering

The item kind is fixed by the checked source context before HIR lowering.

- An associated type produces no runtime operation. In
  `<T as Trait>::Assoc::member`, the first selection yields the normalized
  associated type and the second selection enters only that type's nominal
  type-side domain.
- An associated value uses `ResolvedRef::DirectDecl` with the selection ID.
  `HM-LR-REF-002` emits one `STATIC_REF`; `HM-LR-TOP-002` projects that value as
  an expression. No call or activation is introduced. The value must already
  satisfy the immutable, Shareable, no-drop, authority-free, acyclic, statically
  materializable profile.
- An associated function uses an ordinary call plan whose semantic target is
  `ORDINARY::TRAIT_WITNESS` and whose `call_head_id` is the selection ID.
  `HM-LR-CALL-003` emits one `STATIC_REF` followed by the existing `INVOKE`.
  Static symbol binding consumes the exact `CallableImplementationId` projection
  and `SubstitutionId`; it does not rediscover or rank a conformance.

Keeping the HIR target as `TRAIT_WITNESS` preserves the selected conformance
origin. A backend may issue a direct call to the resolved symbol, but it must not
rewrite the semantic identity to a bare direct implementation unless the exact
seven-field residue remains independently attached.

## Runtime and ordering fence

Runtime witness lookup, provider search, fallback, candidate enumeration,
source/import/use/link-order selection, expected-result selection, implicit
conversion selection, specialization, child-local witness replacement,
activation, new ownership or call-input commit events, runtime identity
reconstruction, and machine-address identity input all have count zero.
Inherited parent evidence retains its original
`ConformanceId` and `TraitWitnessId`. Different normalized substitutions receive
different selection IDs without becoming specialization candidates.

## Existing lowering alignment

- `HM-LR-REF-002`: `ResolvedRef::DirectDecl` to `STATIC_REF`.
- `HM-LR-TOP-002`: resolved reference value to expression value by
  `TOTAL_PROJECTION`.
- `HM-LR-CALL-003`: `ORDINARY::TRAIT_WITNESS` to `STATIC_REF` plus `INVOKE`.
- `DM-SEMOP-STATIC-REF-R1` already accepts one closed `static_identity_id`.

No HIR-H1 schema shape, MIR schema shape, backend ABI rule, or runtime service is
added by R62.

## Evidence boundary

The companion-capability contract already fixes the explicit lookup domain,
the seven identity axes, and the zero runtime/order rules. R62 adds the missing
normative projection and lowering descriptor. Exactly one trace cell changes
from `APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`; all thirteen acceptance
cases remain `DESIGN_STATIC_NOT_RUN`.

The existing catalog mentions
`TRAIT_ASSOCIATED_STATIC_AMBIGUOUS`, but it is not an active evidence locator
for this closure. Resolving or removing that unused catalog spelling is an
out-of-scope follow-up and does not alter the six active rejection diagnostics
used here.

## Governance fence

- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15_NOT_RUN`
- GitHub publication: `SUSPENDED`
- production implementation: `NOT_AUTHORIZED`
