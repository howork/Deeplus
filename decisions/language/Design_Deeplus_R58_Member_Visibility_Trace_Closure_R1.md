# Deeplus R58 Member Visibility Trace Closure R1

## Decision

`APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE`

R58 is a local-only E2 structured-static trace closure. It closes the bounded
member-visibility evidence gap without activating source, executing a product
parser/checker/runtime, or publishing to GitHub.

## Exact scope

The dependency-closed scope is exactly these three features and no others:

1. `member_visibility_sigil_surface_phase_a`;
2. `member_visibility_hierarchy_protected`;
3. `member_visibility_sigils_only`.

The predecessor has exactly twelve `IR-XCUT-P1-054` cells in this scope:

| feature | four local E2 cells |
|---|---|
| `member_visibility_sigil_surface_phase_a` | `STATIC_SEMANTICS`; `CONFORMANCE_TESTS.POSITIVE`; `CONFORMANCE_TESTS.BOUNDARY`; `CONFORMANCE_TESTS.REJECT` |
| `member_visibility_hierarchy_protected` | `DYNAMIC_LOWERING`; `CONFORMANCE_TESTS.POSITIVE`; `CONFORMANCE_TESTS.BOUNDARY`; `CONFORMANCE_TESTS.REJECT` |
| `member_visibility_sigils_only` | `DYNAMIC_LOWERING`; `CONFORMANCE_TESTS.POSITIVE`; `CONFORMANCE_TESTS.BOUNDARY`; `CONFORMANCE_TESTS.REJECT` |

The two blocked dynamic-lowering cells close as static-only `NOT_APPLICABLE`,
and the already-`NOT_APPLICABLE` surface dynamic cell is reaffirmed: member
visibility requires no runtime lookup, check, registry, MIR operation, xVM
instruction, or backend instruction. The remaining ten predecessor cells close
from direct or delegated structured static semantics and
normal/boundary/rejection examples. This decision does not claim closure for an
adjacent visibility, accessor, property, constructor-promotion, Trait-export,
or top-level-visibility feature.

## Closed semantic contract

The source vocabulary remains exactly `+`, `-`, and `#`, ordered
`- < # < +`. Private `-` is limited to the declaring nominal type. Protected
`#` is limited to that nominal type and its nominal subclasses; module/package
peers, conformers, witness holders, and structurally similar types do not
qualify. Effective access intersects this member domain with top-level owner
reachability.

The existing Grammar retains exactly fifteen `MemberVisibility?` owners:
`MemberFunctionDecl`, `TypeSideMemberFunctionDecl`, `ConstructorDecl`,
`StoredParameter`, `FieldDecl`, `TypeSideFieldDecl`, `AccessorDecl`,
`ForwardDecl`, `TraitMethodDecl`, `ConformanceMethodDecl`,
`ExtensionSetFunctionDecl`, `ActorOnDecl`, `ActorRequestDecl`,
`BitfieldNamedSlot`, and `FlagNamedSlot`. Omission is preserved as
`OMITTED`/`null`. R58 establishes no global default; the immediate parent-owner
contract decides how omission is resolved or rejected.

An override keeps the original slot's declaring-nominal access anchor. After
owner-specific omission handling, it may preserve or widen visibility but may
not narrow it. `OVERRIDE_VISIBILITY_CANNOT_NARROW` remains the narrowing
diagnostic. Trait witness requirement mismatch remains the distinct
`TRAIT_REQUIREMENT_VISIBILITY_MISMATCH` diagnostic.

Diagnostic precedence is declaration-first. `public`, `common`, `private`, or
`protected` on a member callable emits
`CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN` before slot or Trait visibility
comparison; `public def` is the canonical wrong-word rejection. A valid member
sigil that narrows an inherited slot emits
`OVERRIDE_VISIBILITY_CANNOT_NARROW` before a later Trait requirement visibility
mismatch. Every rejected declaration or access leaves zero HIR residue.

## Evidence boundary and release guards

The normal set includes explicit private/protected/public member access within
the admitted domain. The boundary set includes a `#` access by a nominal
subclass from another module. Rejections include a same-module non-subclass
peer, `public def` on a member callable, and a `#` override of a `+` slot. These
are local E2 structured-static receipts only; product parser, integrated
checker, MIR, runtime, formatter/LSP, and independent conformance remain
`NOT_RUN`.

The preserved guards are exact:

- semantic P0: `0`;
- feature P1: `22` OPEN;
- M13 actions: `4` OPEN;
- product lanes: `15/15 NOT_RUN`;
- source activation: none;
- GitHub publication: `SUSPENDED`.

No generator execution, catalog expansion, frontend activation, runtime claim,
or GitHub publication is authorized by this decision.
