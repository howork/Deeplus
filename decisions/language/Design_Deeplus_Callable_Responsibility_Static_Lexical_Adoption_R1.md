# Deeplus callable responsibility, lexical access, and function-static adoption

Status: `CURRENT_DESIGN_DECISION`
Language version: `0.1.2-internal`
Decision revision: `r51f3-current-callable-responsibility-static-lexical-r1`
Product evidence: `15/15 NOT_RUN`

## 1. Intake and provenance

This decision was made against repository `howork/Deeplus`, branch `main`,
commit `7b8fbdd5e78c5ca19c85d7889e184ae1e57fb07e`. The following byte identities
were verified before semantic review.

| Input | SHA-256 | Disposition |
|---|---|---|
| `Design_Deeplus_Concise_Throws_Effects_Declaration_Proposal_R1.zip` | `88be33d1948cb29893962c172895cfc0a45dd7aa99b17f2d649af8e81144922c` | accepted as amended Preview Design |
| `Design_Deeplus_Numeric_System_Std_Math_R1.zip` | `92f6488adeaccd0e26ad510c9319a78e9e9a9419018adac9e93fbd673666f79f` | already reflected exactly; no duplicate feature or P1 |
| `Design_Deeplus_Nonescaping_Lexical_Access_R1.zip` | `291229811f39faff3137ce1906817f046cb258165084d220a6c2a456aae6c1d6` | accepted with compatibility amendments |
| `Deeplus_Current_Main_Resync_Report_R1.md` | `e24d6a5e4398454d6608efcf4926bff384ff185ee6c3be516e44f965b9660512` | accepted as synchronization evidence |
| `Design_Deeplus_Function_Static_Namespace_Redesign_Pack_R1.zip` | `8d27f405bdbbba09656d2af2483e150fe5f46b10157cb38599487c585227ec54` | S0 accepted; S1 accepted as amended Preview Design |

The numeric pack has the same identity as the pack already materialized by the
current numeric/guard/call/Enum coherence revision. Reprocessing it would create
duplicate authority rather than a new language delta.

## 2. Decision A — concise throws and effects

The proposed normalization is sound and Deeplus-like:

```text
omitted throws  => Never
omitted effects => {}
body errors     ⊆ normalized declared ErrorSet
body effects    ⊆ normalized declared EffectRow
```

It is adopted as `PREVIEW_DESIGN_NONACTIVATABLE`, not as current Stable
semantics. Current Stable `private_error_set_inference` assigns different
meaning to an omitted private/local `throws` clause. Silently changing that
meaning would invalidate existing source without a migration inventory.

The Preview contract therefore:

- preserves omission presence only in the lossless CST;
- always carries both normalized rows in typed AST/HIR, callable identity,
  module API digest, and MIR;
- treats omission and an explicit empty row as type/API-equivalent;
- checks implementation bodies by row inclusion;
- keeps Trait witness row narrowing, exact override compatibility, and
  function-value row subsumption as distinct rules;
- excludes lambdas, accessors, and other owners with no responsibility-clause
  surface;
- does not change the current `= return Expr` implicit-pure rule.

Promotion requires a deterministic inventory and rewrite of affected
private/local declarations, formatter/API-digest evidence, and an explicit
supersession of `private_error_set_inference`.

## 3. Decision B — nonescaping lexical access

Read-only access to an outer place is not automatically an environment capture.
The checker may classify it as `LexicalScoped` only when all of the following
are proven:

1. the callable is synchronous and remains in the same isolation;
2. the callable cannot escape the declaring region;
3. the dependency is read-only and nonconsuming;
4. the place stays live and readable for every possible invocation;
5. no snapshot, move, mutation, lifetime extension, suspension, task, actor, or
   unknown callback behavior is required.

The initial closed proof routes are direct immediate invocation, a local
function with a closed use graph inside its declaring block, and an exact
invocation-bounded `#scoped` parameter contract. `#scoped` spelling alone is not
proof when the selected callee contract is unknown.

Callable normalization uses two orthogonal axes, plus a closed-assertion bit:

```text
Residence  = FrameIndependent | RegionBound(region_id)
Environment = Empty | Explicit(environment_id, ordered_capture_plan)
closed_ancestor_frame_assertion: Bool
lexical_dependencies: sorted_unique_dependencies
```

The axes are not a sum type: a callable may be both
`RegionBound(region_id)` and `Explicit(environment_id, ordered_capture_plan)`.
In that mixed state, explicit captures live in the environment while residual
qualified outer reads remain call-time lexical dependencies. A lexical
dependency creates no environment field, acquisition, snapshot, move, cleanup
obligation, or capture-plan item. Mutation, ownership transfer, escape,
suspension, isolation crossing, `def#guard`, async, generator, task, and actor
owners require an explicit existing carrier or capture route.

For compatibility, the current bare capture item `[name]` remains admitted and
retains its current explicit-capture meaning. It is not reinterpreted as
lexical access. An explicitly present empty capture list `[]` is a closed
callable assertion: every outer callable-local or parameter reference is
rejected. This preserves existing source while making programmer intent
machine-checkable.

## 4. Decision C — function static

### 4.1 Stable S0 spelling

The current Stable activation surface is renamed from `scope#static { ... }` to
the contextual prologue `static { ... }`. This is a source spelling repair, not
a semantic owner change. Placement, owner admission, body profile,
`FunctionStaticOwnerId`, actual-invocation trigger, state machine, cached
failure, publication edge, module API residue, and product boundary remain
unchanged.

The old spelling is recovery-only and deterministically suggests the new
surface. Old and new spellings normalize to the same activation HIR and owner
identity recipe; source spelling is not an identity input.

### 4.2 Preview S1 immutable slots

Persistent values are a separate, nonactivatable Preview profile. Bare
activation-local `let`/`var` declarations keep their existing meaning. A future
persistent slot uses an explicit marker:

```deeplus
static {
    static#slot table: LookupTable = buildTable()
    let verified = verifyTableShape(tableSource)
}

return static#slot::table.find(key)
```

`static#slot name` and `static#slot::name` do not occur in current parser-cover
grammar and cannot be confused with Stable type-side `let::name`,
`QualifiedStaticExpr`, or an ordinary identifier named `static`.
The Preview contract owns a fifth closed lookup domain,
`FUNCTION_STATIC_NAMESPACE`, with no nominal, extension, Trait, provider,
import, export, reflection, bare-name, or runtime-string fallback.

The minimum M0 value is deeply immutable, statically materializable, no-drop,
resource-free, authority-free, borrow-free, and free of interior mutable state.
`SharedCell` and `SharedMutex` remain explicit runtime owners and are not M0
slots. Initialization follows declaration order, permits only prior staged-slot
reads, rejects self/forward/cyclic references, publishes all slots atomically
with `Ready`, and preserves the existing activation failure and reentry
identities.

## 5. Invariants

- semantic P0: `0`
- exact feature P1: `22 OPEN`
- separate actions: `M13-A002..005 OPEN`
- product lanes: `15/15 NOT_RUN`
- new source implementation claim: none
- runtime/backend/formatter/LSP execution claim: none
- existing numeric/Std.Math identity: unchanged
- candidate and historical evidence: unchanged
