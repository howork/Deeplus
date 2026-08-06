# Deeplus Integrated Surface Atomic Cutover R77

## 0. Decision identity

```text
decision_id: DSGN-CURRENT-INTEGRATED-SURFACE-ATOMIC-CUTOVER-R77-R1
repository: howork/Deeplus
branch: codex/r77-range-trait-indexing-migration
baseline_commit: 9f7041c6aff80cf2a725b737d68a197caabc0005
baseline_tree: 18c627e294b28d6b3f4a04f54d3c7caacd892c38
authority: Codex Design_ under the user's current delegated language-design authority
status: LOCAL_ACCEPTED_NOT_PUBLISHED
current_binding: false
product_lanes: 15/15 NOT_RUN
github_mutation: none
```

This decision reconstructs eight review inputs into one Deeplus contract. It
does not copy a proposal wholesale. It preserves the current responsibility,
owner, evaluation, and fixed-operator laws, accepts only the parts that can be
made deterministic, and rejects proposal text that would make meaning depend
on an expected type, an overload result, or a runtime value.

The source transition is atomic. Admitted legacy spellings do not coexist as
aliases after the cutover. Recovery may recognize a removed spelling only to
emit its dedicated diagnostic and commits no canonical AST, HIR, MIR, API, or
runtime residue.

## 1. Input precedence and dispositions

| Input | Disposition |
|---|---|
| Integrated Range/Rest/Unfold/NamedPack/Requires R1 | historical predecessor; R2 supersedes its prefix-pattern direction |
| Integrated Range/Rest/Unfold/NamedPack/Requires R2 | `ACCEPT_WITH_AMENDMENTS` |
| Trait Language Role Reconstruction R2 | `ACCEPT_WITH_AMENDMENTS`; proof role deferred |
| Numeric Literal Suffix Removal R1 | design rationale retained; R2 controls the cutover |
| Numeric Literal Suffix Forced Cutover R2 | `ACCEPT_WITH_AMENDMENTS` |
| Comma Axis Indexing and Selector R1 | `ACCEPT_WITH_AMENDMENTS`; rank-preserving mixed selection rejected |
| MutableList Structural Edit Surface R1 | surface and atomicity preimage retained |
| MutableList Sugar and Open Slice R2 | `ACCEPT_WITH_AMENDMENTS`; it supersedes R1 only for lowering architecture |

## 2. Collect and unfold direction

Deeplus uses one direction law:

- collection into a binder is an attached suffix;
- structural expansion out of a value is an attached prefix.

The current forms are therefore:

```deeplus
def invoke(command: String, arguments..: String, options**) = {
    execute(command, *arguments, **options)
}

let [first, middle.., last] = values
let ${timeout: timeoutPattern, remaining**} = settings
```

The exact source forms are:

| Responsibility | Current spelling |
|---|---|
| positional formal collection | `items..: T` |
| positional function-type residue | `T..` |
| static named formal collection | `options**` |
| static named function-type residue | `NamedPack**` |
| positional pattern collection/sink | `items..` / `_..` |
| static named pattern collection/sink | `fields**` / `_**` |
| owner-bounded structural unfold | `*value` |

`*value` is not a general Pratt prefix expression. The parser admits it only
inside the closed call-argument, List/Record/Map materialization, insertion
payload, or comprehension-source owners. It first builds a neutral structural
unfold node. The checker seals its source shape before overload selection. An
expected formal, expected result, selected overload, or runtime key never
chooses whether the value is positional or named.

Comprehension source unfold is `for pattern in *source`. The removed
`for ... pattern in source` form commits no canonical node.

### 2.1 Positional rest binding

There may be at most one positional rest formal. Explicit labels bind first.
The call binder then reserves fixed positional suffix formals from right to
left, binds fixed prefix formals from left to right, and collects only the
residual actuals into the rest. A fixed suffix formal after a rest has no
default. The value, context, witness, and static-named channels remain distinct.

The body sees a finite, call-scoped `PositionalPack<T>`. Public callable
identity preserves the `T..` channel instead of erasing it to `Sequence<T>`.

### 2.2 Named rest and `requires`

`options**` collects one finite, statically labelled, heterogeneous row. Its
body type is a call-scoped and nonescaping `NamedPack<rho>`. Duplicate labels,
dynamic labels, Map input, reflection, serialization, escaping storage, and
runtime row choice are rejected. Public callable identity preserves the exact
`NamedPack**` residue and a versioned normalized row/witness digest.

The optional clause

```deeplus
def connect(options** requires {
    timeout: Duration
    retries: Int
}) = { ... }
```

belongs only to the named-rest parameter. It is represented by
`NamedRestRequirementClause`, not by the existing callable
`RequiresClause ::= requires PredicateExpr`. It can state required static
labels and their types; it cannot state an arbitrary value predicate.

The compiler-internal `RowContains` proof is not a public `trait#proof` in this
cutover. Its representation remains internal until NamedPack implementation
evidence and a separate promotion decision exist.

### 2.3 Pattern direction and residual ownership

List patterns use one suffix rest: `[head, body.., tail]`. The rest may occur
at the beginning, middle, or end and has fixed-context semantics. `_..` is the
all-remainder sink. The residual is an owner-bounded `ListRestView<T>` and does
not copy, allocate, rebase, outlive, or isolate from its source.

Record, nominal named-payload, and variant named-payload patterns are
label-first: `${label: pattern, rest**}`. The static-named residual is exact and
is published only by the whole-pattern delayed commit. Map patterns retain
their keyed orientation and current `..rest` spelling; a Map is not a
NamedPack. Tuple rest remains Preview and is not promoted by this decision.

## 3. Range and slice partition

Expression Range owns:

```deeplus
start..end
start..<end
start...
start..end:step
start..<end:step
start...:step
```

`..` includes the end, `..<` excludes it, and `...` is one-sided and lazy.
The optional signed `:step` is consumed by the Range parselet and is not a
ternary delimiter. Start, end, and step evaluate exactly once from left to
right. Step zero is rejected. A positive step must advance toward a present
end; a negative step must retreat toward it. A bounded range terminates before
overflow and includes an exactly reached inclusive end. A finite ordered Enum
does not admit a one-sided range. `..>` is not current.

IndexSuffix is a separate owner. It uses comma-separated axes and admits:

```deeplus
values[2]
values[2..5]
values[..<5]
values[..5]
values[2..]
values[..]
matrix[1, ..]
matrix[*, 2]
```

Open bounds are legal only inside IndexSuffix. `k..<` is rejected because it
has no distinct contract from `k..`. `[..]` is the general full slice. `[*]`
remains a NumericArray full-axis form; for NumericArray the two normalize to
the same full-axis selector. `..<` is canonical and no longer warns.

Every default List/String/Bytes/NumericArray coordinate starts at one. An open
exclusive end uses a boundary identity that can denote the one-past-last
sentinel without computing `last + 1`, so maximum-width coordinates do not
overflow. Empty views retain source owner, region, coordinate domain, and the
insertion boundary. Slicing borrows; it does not allocate, copy, or rebase.

NumericArray requires exactly one comma-separated axis per source rank. A
scalar axis is removed from the result; result rank equals the number of
non-scalar axes. All-scalar selection yields an element. Multi-axis selection
is Cartesian. A rank-one List does not reinterpret `a[1, 3]` as gather. Tuple
as gather is rejected because receiver type must not reinterpret an ordinary
Tuple or a Map tuple key after parsing. No implicit linear indexing exists.

## 4. MutableList structural edits

Ordinary bracket read/replace remains closed for `MutableList<T>`. The
following statement-only forms are a separate structural-edit owner:

```deeplus
items[@i] = value
items[i@] = value
items[@^] = value
items[$@] = value
items[@i] = *finiteValues
items[-@i]
items[-@2..4] -> $removed
items[-@(2, 5, 7)] -> $$removed
items[-^] -> $first
items[-$] -> $last
```

They lower immediately to a closed Prelude call plan:

| Surface | Canonical operation |
|---|---|
| `a[@i] = x` | `MutableList::insertBefore` |
| `a[i@] = x` | `MutableList::insertAfter` |
| `a[@^] = x` | `MutableList::prepend` |
| `a[$@] = x` | `MutableList::append` |
| same with `*xs` | corresponding `insertAll*` operation |
| `a[-@i]` | `MutableList::removeAt` |
| `a[-@range]` | `MutableList::removeRange` |
| `a[-@(selectors)]` | `MutableList::removeSelected` |
| `a[-^]` / `a[-$]` | `MutableList::popFirst` / `popLast` |

The HIR uses existing `CallExpr` and the exact
`CallPlan(mode_target_pair, call_head_id)` / `CallableImplementationId`
identity. There is no edit-specific HIR, MIR instruction, runtime fallback, or
extension lookup.

The receiver is one exact mutable place. Receiver, selectors, and payload
evaluate once left to right. Validation, payload staging, and allocation finish
before one mutation commit. Failure leaves the target unchanged. A temporary,
shared or actor-isolated receiver; self-alias or `inout` overlap; and a live
borrow, view, or iterator reject before mutation. Initial bulk insertion accepts
only a finite reusable/copyable element source and performs no hidden clone,
snapshot, or move. Point removal returns `T`; multi-removal returns `List<T>` in
selector order, preserves survivor order, rejects duplicate selectors, and
interprets every selector in pre-mutation coordinates.

## 5. Trait language roles

Role annotations describe a closed language responsibility; they do not grant
arbitrary semantic hooks.

```deeplus
public trait#operator Add<Rhs> { ... }
public trait#iteration Sequence<T> { ... }
public trait#iteration Iterator { ... }
public trait#interpolation Display { ... }
public trait#binding Failable { ... }
```

- `#operator` is permitted only on the nine fixed roots that jointly own the
  thirteen current glyphs. It cannot select glyphs or widen the fixed-glyph
  matrix.
- `#iteration` is permitted only on core `Sequence` and `Iterator` owners.
- `#interpolation` is permitted only on core `Display`.
- `#binding` is permitted only on core `Failable`.
- Users may conform directly to eligible role-bearing Traits but cannot declare
  new role-bearing Trait roots.
- Generic `#role`/`#profile`, conversion/literal/actor/message/derive/marker/
  intrinsic roles, arbitrary user roles, and a public `#proof` role are rejected.

`TraitLanguageRoleId` is distinct from `TraitId`. The role registry, Trait
contract digest, public API digest, and consumer HIR carry the exact role and
version. Adding a role is a source/API change, not metadata that may drift.

### 5.1 Failable binding

`Failable` supplies exactly one consuming global direct conformance operation:

```deeplus
public trait#binding Failable {
    type Success
    type Failure
    def ::branch(move source: Self) -> BindingBranch<Success, Failure>
        throws Never
        effects {}
}
```

The admitted local form is:

```deeplus
let? value = expression else failurePattern => exitStatement
```

The `else` arm is mandatory. Success and failure patterns are irrefutable, the
source is consumed once, and the failure arm must unconditionally leave the
enclosing local continuation. There is no `var?`, bare `let?`, generalized
`if let?`, or `while let?`. Existing Option-specific Preview routes are
superseded; conditional Option tests use explicit `Option::some` patterns.
`Option<T>` uses `Failure = Unit`; `Result<T, E>` uses `Failure = E`.

## 6. Numeric literal suffix cutover

The scanner removes these source suffixes in one cutover:

```text
i8 i16 i32 i64 i128 isize
u8 u16 u32 u64 u128 usize
f32 f64
```

Untyped integer, real, imaginary, and rational constants remain exact until a
valid target is imposed. Unconstrained defaults are `Int`, `Float64`, and
`Complex<Float64>`. There is no smallest-fit, implicit unsigned/BigInt/platform
selection, width-fit overload ranking, or expected-result-driven operator
selection.

A direct atomic literal may adapt to its declared target:

```deeplus
let byte: UInt8 = 255
let ratio: Float32 = 0.5
let imaginary: Complex<Float32> = 4.0i
```

For an operator expression, the fixed-glyph candidate still comes from its
operands. A result annotation cannot retroactively type both operands. Use an
explicitly typed anchor when a nondefault operator domain is intended:

```deeplus
let real: Float32 = 3.0
let z: Complex<Float32> = real + 4.0i
```

`Type!(literal)` is not introduced as a generic cast: the current `Type!`
surface remains the matching `def! new` constructor call. `1f32` migrates to a
floating-look literal such as `1.0` under an exact Float32 target. Imaginary
syntax remains suffix-free floating-look `4.0i`; integer-look `4i` is not made
current.

The scanner maximal-munches a suffix-shaped candidate and emits one
`NUMERIC_TYPE_SUFFIX_REMOVED` diagnostic. It does not split the input into a
number plus identifier and creates no admitted CST/AST/HIR.

## 7. Atomic migration and evidence boundary

The migration updates grammar, frontend model, type/pattern/MIR contracts,
Prelude roles and operations, registries, diagnostics, conformance fixtures,
Grammar Reference, tutorial, guide examples, and current non-historical source
corpus together. Historical receipts and immutable evidence remain unchanged.

The following conditions hold after local freeze:

- semantic P0 remains zero;
- the existing exact 22 feature P1 actions remain open and unchanged;
- M13-A002..A005 remain separate open actions;
- all fifteen product lanes remain `NOT_RUN`;
- no parser/checker/MIR/xVM/runtime/Cranelift/tooling implementation or product
  support is claimed;
- GitHub and the published current pointer remain unbound until a later
  authorized publication cycle.

## 8. Acceptance gates

1. Grammar has one current spelling for every migrated owner and no admitted
   legacy alias.
2. `*value` is reachable only through a closed structural owner.
3. callable `requires PredicateExpr` and named-rest required-field clauses have
   distinct AST owners.
4. Record-family label-first migration does not alter Map pattern orientation.
5. Range operands evaluate once left to right; zero/direction/overflow/end laws
   are exact.
6. Index commas are local to IndexSuffix; statement, attribute, and shaped-array
   semicolons remain unchanged.
7. scalar-axis removal, Cartesian selection, owner-bounded view provenance, and
   one-past-last boundary identity are exact.
8. MutableList structural edit sugar lowers only to the closed Prelude plan and
   satisfies single-place/single-commit/no-hidden-copy laws.
9. Trait roles are core-owned and cannot widen the fixed-glyph set.
10. removed numeric suffixes yield one recovery diagnostic and zero canonical
    residue; literal context does not alter overload choice.
11. user-facing documentation and examples use only the current spellings,
    except explicitly marked rejected examples.
12. R77-focused validators, JSON parsing, grammar topology, catalog assembly,
    generated-document checks, and affected cross-contract rebind validators
    pass. The aggregate published-current validator may continue to report
    immutable predecessor byte fences, publication identities, or Git
    worktree/index parity until this local candidate receives a later
    authorized commit/publication cycle; those reports are recorded rather
    than misrepresented as product execution.
