# Deeplus Type System 0.1.2 — RCTS-V5 TS-R45 — R51f3 Current Canonical

This companion is a checker-oriented projection of the canonical specification. It does not override the specification or exact Grammar. Product checker support is `NOT_RUN`.

Revision: `r51f3-current-numeric-guard-call-enum-coherence-r1`

## 1. Judgment families

The checker owns well-formedness, expression typing, subtyping, conformance evidence, call-shape admission, ownership/place access, effect/error rows, construction, pattern coverage, and Deeplus MIR handoff judgments.

## 2. Normalization and identity

Aliases, option layers, closed unions/intersections, associated projections, rows, labels, ownership modes, effects, errors, cancellation, measures, shapes, and witness identities normalize before comparison. Normalization is terminating, performs an occurs check, and preserves every responsibility-bearing distinction. Inference is bidirectional and local: it never invents an implicit generic, anonymous union, hidden authority, cancellation conversion, or open runtime type test.

A semantic value identity is independent from storage, serialization, runtime discriminant, ABI, and backend layout identity. `Int` normalizes to the signed 64-bit mathematical domain. `UInt` is the separate default unsigned mathematical domain `0..18446744073709551615`; it is not an alias of `UInt64`, `USize`, `Int`, or `Int64` and grants no storage or ABI identity. `IntN`, `UIntN`, `ISize`, and `USize` remain separate domains. Contextual adaptation of a signless unsuffixed integer succeeds only for one independently fixed exact and representable `UInt`, `IntN`, `UIntN`, `ISize`, or `USize` target; absent such a target, the literal still normalizes to `Int`. A sign remains an AST prefix operator. With an independently fixed exact signed target, the checker may additionally recognize only `PrefixExpr(-, UnsuffixedIntegerLiteral)`, consume the validated token magnitude, compute `-magnitude`, and test that candidate against the exact target domain. Negative source never adapts to an unsigned target. This adapter neither folds any other expression nor inserts widening/narrowing; an unrepresentable candidate is rejected by the enclosing owner's exact range diagnostic. Width/type suffixes are not source type selectors.

An unconstrained floating-look literal defaults to `Float64`; one independently fixed exact `Float32` target may contextually adapt the atomic literal when exactly representable under the Float32 rounding law. `Float` is a Stable closed alias of `Float64`: normalization erases the alias spelling before comparison, so it creates no distinct nominal, precision, serialization, runtime-discriminant, storage, layout, or ABI identity. No operator judgment inserts hidden widening, narrowing, mixed signedness, or mixed-width conversion. In particular an expected operator result cannot retroactively select operand types or a fixed-glyph candidate. `Float32` and `Float64` preserve their separate IEEE-754 binary domains; NaN is unordered and cannot establish implicit `Ord` or `Keyable` evidence.

The scanner maximal-munches every removed type-suffix-shaped candidate
(`i8/i16/i32/i64/i128/isize`, `u8/u16/u32/u64/u128/usize`, `f32/f64`) and emits
one `NUMERIC_TYPE_SUFFIX_REMOVED`; it never tokenizes that candidate as a
number followed by an identifier and emits no admitted CST/AST/HIR residue.
Exact atomic target adaptation replaces source suffix selection. Untyped
constants remain exact until a valid target is independently fixed, and
unconstrained defaults remain `Int`, `Float64`, and `Complex<Float64>`.

Resolver identities are typed by owner domain. `TargetId` is the canonical
triple `(PackageId, manifest_target_name, target_kind)`, where `target_kind` is
`library`, `executable`, or `script`; source-role policy, activation profile,
file order, absolute path, timestamp, and content digest are not key inputs.
`DependencyBindingId` is
`(consumer_package_id, source_visible_binding)`: changing the provider keeps
that binding identity but changes its bound content and dependency-graph
digest. It has no direct HIR value projection.

`ResolverScopeId` is a closed tagged sum of package-root, target, module,
source-contribution, item-owner, and body-local scopes. Only the body-local
variant projects to `HirScopeId = (HirBodyId, owner_local_scope_id)`.
`HirLocalId = (HirBodyId, owner_local_binding_id)` is allocated only to a
committed normalized binding; a provisional or failed pattern probe allocates
none. `ImportBindingId` is
`(ResolverScopeId, namespace, local_binding_name)`. Its resolved target is
required content but is not part of identity. These recipes never use an
absolute path, source span, timestamp, traversal order, or recovery node.

`Rational` normalizes to one opaque `(BigInt numerator, BigInt denominator)`
identity with positive denominator, relatively prime magnitudes, and canonical
zero `0/1`. A `<p/q>` CST retains both unsigned source magnitudes, while the
typed HIR value stores the normalized pair. The literal is never integer
division and cannot be selected by a type-parser goal. Rational supplies
sealed unary `+`/`-`, binary `+`/`-`/`*`/`/`/`%`, `Eq`, and `Ord` evidence;
exact integer/Rational mixed arithmetic is admitted only for the exact pairs
listed by the Prelude contract. Decimal, Float, and Complex conversions are
explicit named conversions. Division and remainder by zero raise
`ArithmeticDefect` before any enclosing place commit. Rational also has
strong `Hash` and `Keyable` laws.

The initial `Complex<Rep>` profile admits exactly invariant
`Complex<Float32>` and `Complex<Float64>`; bare `Complex` is the closed alias
of the latter. Its semantic identity contains exact real and imaginary
component values but no public layout or ABI identity. An attached `4.0i`
literal has real component positive zero and Float64 imaginary component;
an atomic `4.0i` may adapt to `Complex<Float32>` only under an independently fixed direct literal target. In `lhs + 4.0i`, candidate selection is fixed by the already typed operands; an expected `Complex<Float32>` result does not push a target into both operands, so nondefault arithmetic requires an explicit typed operand anchor. Integer `4i`, separated or radix forms do not enter
this judgment. Float-profile Complex supplies sealed unary `+`/`-`, binary
`+`/`-`/`*`/`/`, and partial IEEE equality evidence. It supplies no `%`,
`Ord`, strong `Hash`, or `Keyable` evidence; an exact zero complex divisor
raises `ArithmeticDefect` before commit.

The numeric-system successor is `PREVIEW_DESIGN_NONACTIVATABLE`. It introduces
only a thin capability taxonomy—`Numeric`, `ExactNumeric`,
`ApproximateNumeric`, `IntegralNumeric`, `RealScalar`, `BinaryFloating`, and
`ComplexScalar`—for stating generic requirements. Membership does not imply
representation subtyping, implicit conversion, ordering, hashing, keyability,
remainder, transcendental support, operator activation, or a common runtime
layout. This Preview design neither changes the Stable fixed-glyph set nor
creates a universal numeric supervalue.

The same Preview profile proposes attached decimal-integer imaginary literals.
At an expression-primary goal, an unsuffixed decimal integer followed
immediately by `i` and then an identifier boundary may normalize to
`Complex<Float64>`; thus `4i` means `Complex!(real: +0.0, imag: 4.0)`.
Radix, width-suffixed, separated, and chained identifier forms remain rejected,
and `4index` is one invalid numeric-suffix candidate rather than `4i` plus
`ndex`. This paragraph is a design contract only: current source admission and
product execution remain unchanged.

Preview Rational completion adds only integral `^` and optional named
alternative APIs such as `modEuclid` and `divRemTrunc`. Stable Rational `/`
and `%` already use the fixed `Divide`/`Remainder` evidence and the truncation
law above; they do not depend on this Preview feature. The `std::math` core facade is a current `STDLIB_PROFILE` covering
constants, classification, basic arithmetic helpers, rounding, exact helpers,
power and roots, exponential and logarithmic functions, trigonometric and
hyperbolic functions, complex functions, and approximation helpers. Special
functions and calculus remain separate Preview profiles. Neither the current
facade nor either Preview inventory supplies an operator witness, hidden
conversion, or product-support receipt.

## 3. Named rest, function-type residue, and unfold

Named-rest parameters use attached suffix `**`: `options**`. Function types and public API digests preserve the exact `NamedPack**` residue. The body binding is a finite call-scoped, nonescaping `NamedPack<rho>` whose normalized static label row and witness digest are public callable identity. Duplicate or dynamic labels, Map input, reflection, serialization, escaping storage and runtime row selection reject. Call/materialization named unfold remains attached prefix `**value`, distinguished by its closed structural owner. A named-rest parameter may own a `NamedRestRequirementClause` of required static labels and types; this node is separate from callable `RequiresClause ::= requires PredicateExpr` and cannot express a value predicate.

## 4. Nominal and structural domains

Subclassing, Trait conformance, extension activation, containment/association, and dynamic/tooling views are separate. Concrete classes are final by default. Sealed exhaustiveness recursively covers the complete family. Conformance is not inherited merely from nominal subclassing.

## 5. Generics and function types

Current parameter kinds are type, StaticInt, EffectRow, and ErrorSet; rows and
labels are checker identities, not further user generic kinds. Generic
constructors are invariant by default. Function compatibility preserves
value/context/witness/rest channels, ownership, callable profile, effect/error
rows, cancellation, suspension, isolation, capture, and return type. Return
type and source order are not overload tie-breakers. An ordinary callable
parameter begins with an Identifier that retains its call label, whole-value
local, overload identity and public API/ABI identity. An optional following
structural Pattern is checker-proven irrefutable and lowers only as body-entry
decomposition; its child binders do not alter the call channel.

Ordinary and message calls share one trailing-closure binding judgment. One
trailing closure may be unlabeled or labeled; two or more are well formed only
when every item has a unique label. Labeled items bind by the visible
function-typed parameter label. An unlabeled item binds only when ordinary
channel matching leaves exactly one compatible trailing function parameter.
Defaults cannot be skipped through trailing syntax, and the spelling changes
none of the capture, ownership, effect, error, cancellation, isolation, or
cleanup judgments.

Every call normalizes to one `CallExpr` with mode `Ordinary`, `Message`, or
`ActorMessage`. It preserves one ordered zero-or-more `CallArgument` list whose
kinds are positional, named, positional unfold, named unfold, context, and
witness, followed by the ordered trailing-closure group. Message and actor
message calls reuse the ordinary static channel matcher; they do not create a
message-payload AST node and do not project a Tuple or Record into hidden
arguments. Parentheses group an expression, so `(x, y)` is one Tuple argument,
whereas `x, y` are two positional arguments. Duplicate or unknown labels,
invalid ordering or unfolds, and arity mismatches reject before overload
ranking. Context and witness channels remain explicit argument kinds and
cannot be synthesized from ordinary value arguments.

## 6. Union, intersection, Option, Result, and Facet

Union injection is unique after normalization. Contract intersections require every constituent obligation. Option and Result have explicit alternatives. Every Result use-site spells its error channel `Result<T, error E>`; the generic declaration may bind `E: ErrorSet` without repeating the role marker. Borrow Facet is current; owned/inout Facet packages remain Preview-design.

The accepted Stable Enum subset design adds no open subtyping search. A
payload-free exact variant is normalized to `(EnumId, VariantId)`, and a named
subset is normalized to one owner `EnumId`, a finite allowed-`VariantId` set,
and the frozen enum-universe digest. Distinct variants of one owner are disjoint.
Injection selects one exact included variant; subset-to-owner conversion uses the
bounded `VariantOwnerWidening` proof; subset-to-subset conversion is implicit only
for proven finite-set inclusion. Owner-to-subset conversion is never implicit and
uses `as?` or an admitted pattern. Pattern coverage for a subset is exactly its
allowed set, so an outside case is unreachable and an omitted allowed case remains
in the exhaustiveness residual. When the normalized allowed set equals the frozen
owner universe, the canonical type is the nominal owner Enum; an associated alias
is only a non-identifying source spelling. This judgment is separate from the closed-Union
typed-alternative judgment and creates no wrapper, runtime membership test, case,
`VariantId`, storage, or alias-local Trait witness. The surface is current
`STABLE_DESIGN`; parser, checker, backend, and tooling product lanes remain
`NOT_RUN`.

Absence is an explicit `Option` alternative. `::none` in an expected `Option`
context or explicit `Option<T>::none` constructs the absent alternative; no
implicit nullable type or sentinel conversion is inferred.

## 7. Ownership, effects, and cleanup

Move, borrow, inout, resource, isolation, suspension, effect, error, defect, cancellation, and cleanup obligations remain explicit. Cancellation is not an ErrorSet member and suspension is not hidden in an EffectRow. Borrow escape and inout aliasing are rejected. Cleanup is deterministic across normal return, failure, and cancellation.

Construction uses one explicit lifecycle plan and one `ConstructionTokenId`.
Allocation begins an unpublished owner; field/default/delegation steps update
the lifecycle masks only after their responsibilities are admitted. Commit is
legal exactly once after every required mask is complete and publishes exactly
one owner. Abort publishes nothing and runs the registered responsibilities in
reverse order. A failing field, delegation, default, conformance, effect, error,
or cancellation edge cannot expose a partially initialized owner.

## 8. Patterns, clauses, and laws

Every Pattern owner uses one normalized Pattern AST plus an explicit context
policy. Plain `let`/`var`, bare `for`, callable/lambda parameter decomposition,
and direct-local Pattern assignment require irrefutability; guarded
`let`/`var`, `if let`, `while let`, `for let`, ordered `catch`, and `match`
admit refutable patterns under their own failure dispositions. `let!`/`var!`
are explicitly refutable and raise `PatternMatchDefect` on mismatch. Each
refutable owner creates one `PatternAttempt`: the subject is evaluated once;
structural probing is pure and nonconsuming; probe binders are read-only and
nonescaping; and zero or one terminating pure Bool guard runs exactly once
after structural success. Only final guarded success performs exactly one
logical commit of all bindings, moves, loans, views, and authority. Child
pattern-row `BINDING_COMMIT` entries are compositional requirements that
collapse into that single top-level commit, not separate executable commits.
Failure or a false guard publishes none of those results. `if let` takes its
false branch, `while let` exits the loop, `for let` skips the candidate, and an
unmatched catch continues or propagates.

Current coverage domains include enum/union/Option/Result alternatives, exact
Tuple products, exact/open Record and Map rows, closed List length/rest cells,
transparent nominal products, exact ordered scalar intervals, and loop
outcome. Record-family patterns are exact by default; `_**` ignores and
`name**` captures an exact static named residual. Map patterns remain distinct:
`.._` ignores and `..name` captures an exact keyed residual. A nominal type opens only through schema/data/value
identity or an explicit pattern-transparent descriptor. Sealed-Class closure
does not expose private fields or create a constructor Pattern. Pin keys/bounds
must be stable and use statically selected pure total equality/order. Float
interval patterns, arbitrary Class/getter/provider opening, dynamic extractors,
and backtracking remain outside the Stable domain. Declarative clauses use the
same finite partition algorithm. Law bodies admit only pure predicate
assertions.

A List Pattern has exact shape or one suffix positional collector:
`[prefix, rest.., suffix]` or the sink `_..`. The collector may occupy the
beginning, middle or end; a middle collector requires fixed children on both
sides. Prefix-rest and double-sided legacy spellings are not aliases. The
closed built-in descriptor returns borrowed
`ListRestView<T>` with an explicit intrinsic `Sequence<T>` witness,
`SourceOwnerId`, `BorrowRegionId`, `RankSpan(start_rank,count)` and original
logical-coordinate projection. Empty rest uses `count = 0`, not an invalid
source Range. The view cannot outlive or retain its source, and ordinary
`ReadonlyView<T>` gains no Sequence witness. A moved List may return an exact
owned `List<T>` residual only through its closed descriptor. Generic Sequence
opening and temporary-owner retention remain Preview.

Bare comma return types/values/bindings and direct-local parallel assignment
normalize to existing Tuple identities. They have arity at least two and one
semantic result channel; Expr has no comma operator. Parallel assignment
requires distinct mutable direct LocalPlaceIds, stages the complete RHS
left-to-right exactly once, performs one failure-atomic logical group commit,
and has result Unit. It promises no hardware/cross-thread atomicity. Resource,
field/index/property/shared/actor/FFI targets remain Preview.

## 9. NumericArray, bitfield, and measures

NumericArray typing preserves element, shape, rank, orientation, and typed coordinate domain. Each built-in default source-visible axis is exactly `1..dimension`, but it is not an ordinary Sequence witness. IndexSuffix supplies exactly one comma-separated axis per source rank. Each scalar axis is removed; all-scalar selection returns the element and mixed selection result rank equals the number of non-scalar axes. Multi-axis selection is Cartesian. A rank-one List does not reinterpret a comma list as gather, Tuple-as-gather is absent, and no implicit linear index exists. Coordinate type/count mismatch is static, and a dynamic coordinate outside the declared axis raises `IndexError::outOfLogicalDomain`. A NumericArray slice produces an owner-bounded `ReadonlyView` that preserves source coordinates and provenance. Open slice ends use a boundary identity that can denote one-past-last without forming `last + 1`; an empty view retains owner, region, coordinate domain and insertion boundary. Bitfield uses unsigned strict layout and finite flags universe. Exact-ratio units are core; calendar units require the stdlib/provider profile.

Current `Set<T>` is an immutable unique-element collection. Literal and
comprehension elements require one exact normalized `T` plus admitted equality
and keyability evidence. Duplicate literal entries reject, membership never
widens or stringifies the probe, and iteration order is not a semantic
contract. Set has no bracket-indexing judgment.

An immutable `Map<K,V>` literal fixes one exact normalized `K`, one exact
normalized `V`, and one `Keyable<K>` witness before its `MapLiteralPlan`
evaluates. Direct entries and unfolded Maps must preserve those exact domains;
neither branch drives widening, stringification, conversion, or anonymous
Union inference. The selected Keyable equality/hash operations are borrowed,
nonconsuming, synchronous, `throws Never effects {}`, cancellation-forbidden,
and authority-free. Entry expressions retain their own visible responsibility
channels, and the plan's failure-atomic cleanup handles those channels without
publishing a partial Map.

## 10. RCTS-V5 and MIR handoff

RCTS-V5 descriptors are closed discriminated inputs to design predicates and preserve cancellation independently from effects and errors. Static validation is E2 evidence only. Dyn-RCTS is nonactivatable. Every admitted surface lowers to Deeplus MIR with call shape, labels, ownership, effects/errors/cancellation, cleanup, evidence, and evaluation order preserved.

The typed frontend boundary is
`HirSkeleton -> CheckSession -> TypedHirDraft ->
Verified<CanonicalHirH1> -> ExecutableHirH1`. Only the verified form may be a
MIR input. It contains no unresolved or invalid type, name, operator, witness,
extension, responsibility, or capability field. The verifier independently
recomputes every selected declaration, conformance and intrinsic operation from
the normalized input residue. `ExecutableHirH1` adds a target capability
receipt; it cannot add a language feature or reinterpret the verified HIR.
HIR-H1 is backend-neutral and does not make the noncanonical MIR-X1 proposal
current.

## 11. Core judgment notation

The implementation may choose internal Rust types, but it must preserve the following conceptual judgments:

```text
Γ ; Ω ; Ε ⊢ e : T ▷ R
Γ ⊢ T wf
Γ ⊢ T <: U
Γ ⊢ C conforms Trait via WitnessId
Γ ⊢ call callee(args) ⇝ CallShape, Result, Responsibility
Γ ; PlaceState ⊢ place access Mode ⇒ PlaceState'
Γ ⊢ pattern partitions SubjectType ⇒ Coverage
Γ ⊢ construct Target from Fields ⇒ ConstructionPlan
```

`Γ` is the static identity/type environment, `Ω` is the ownership/place environment, `Ε` is the permitted effect/error context, and `R` is the responsibility result. A diagnostic-producing failure returns the failed predicate and primary diagnostic, not a guessed fallback type. Judgment evaluation is deterministic for the same normalized inputs and activated profile.

## 12. Call-shape algorithm

Call checking performs these steps in order:

1. resolve the callee domain and candidate set without using the result type as a tie-breaker;
2. evaluate argument expressions in source order;
3. bind fixed positional and fixed named parameters;
4. bind the optional repeated positional channel `T..` into a finite nonescaping `PositionalPack<T>`;
5. prove and expand each named unfold `**record` from a statically known Record label row;
6. bind the optional static named-rest channel `NamedPack**` into a finite nonescaping `NamedPack<rho>` and verify its optional required-label clause;
7. reject missing, duplicate, overlapping, indeterminate, or extra labels;
8. check ownership, context, witness, effects, errors, isolation, and return compatibility;
9. choose the unique most-specific candidate, preferring fixed arity, then repeated positional, then named rest;
10. emit a normalized CallShape for Deeplus MIR.

The source parameter `options**` and the function-type item `NamedPack**` denote the same named-rest residue. The body binding is a `NamedPack<rho>`, not a Record or Map; its finite normalized row/witness digest remains public call identity. `*value` is the owner-bounded positional outward unfold and `**value` is the owner-bounded static-named outward unfold, not a parameter/type suffix. The lexical marker fixes the channel before overload selection; expected formals, results, selected overloads and runtime values cannot choose it.

## 13. Classes, Traits, conformance, and extensions

Nominal subclassing establishes class ancestry and inherited class slots. Trait conformance establishes witness evidence. An extension contributes members only under its activation/import domain. These relations are checked independently and then combined by explicit resolution rules.

Concrete classes are final unless declared open. Sealed classes close direct
subclass declarations to the declared family scope; nominal-family analysis
recursively includes current descendants and rejects foreign direct children.
This closure does not invent a constructor-pattern carrier. Class dispatch
markers lower to `ClassDispatchKind`; Trait witness markers lower to
`TraitWitnessKind`. Associated requirements have their own item identities and
do not acquire method markers.

Top-level type visibility is a three-domain lattice. `private` is
module-local, `common` is package-wide but nonexportable, and `public` is
eligible for external API only through an admitted export/module interface.
The exact type-producing owner set is `ClassDecl`, `TraitDecl`, `EnumDecl`,
`TypeAliasDecl`, `SchemaDecl`, `ActorDecl`, `ActorProtocolDecl`,
`TypestateResourceDecl`, and `BitfieldDecl`. Each of those nine owners requires
an explicit domain in all library, executable, script, preview-library,
preview-executable, and preview-script roots. Omission is rejected by the
checker: it emits `TYPE_DECL_VISIBILITY_REQUIRED` and produces zero admitted HIR
type nodes, type identities, and API-digest entries.

Package and Module identity remain separate type/linking axes. PackageId is
owned by the resolved build/dependency graph and scopes distribution,
dependencies, artifact provenance, orphan coherence, and `common` visibility.
ModuleId is `(PackageId, ModulePath)` and scopes namespace, `private`
visibility, name lookup, and source composition. A filesystem path is not a
ModulePath and cannot participate in type identity or coherence comparison.

Module artifacts use three noninterchangeable identities. The interface hash
is the exact effective public semantic residue after visibility and opaque
facade projection; it excludes source paths, source/origin/proof IDs,
dependency receipts, private bodies, and debug spans. The implementation hash
binds that interface identity and the verified private HIR semantics. The full
compilation receipt separately binds target/module ownership, source
provenance, package and resolver graphs, dependency, visibility and
initialization receipts, plus interface and implementation hashes. A
non-importable script has no interface hash. Equal interface hashes therefore
do not imply equal private implementation or compilation provenance.

For every other top-level owner whose Grammar production carries
`TopLevelVisibility?`, omission normalizes to `private`; this default never
applies to the nine type-producing owners. After that normalization, wider API
residue cannot mention a narrower identity, `common` residue cannot be
externally exported or re-exported, and `public` residue enters external API
only through a separately admitted export or module interface.

Member visibility is a separate three-point order:

```text
rank(-) = 0 < rank(#) = 1 < rank(+) = 2
```

The fifteen current grammar owners are `MemberFunctionDecl`,
`TypeSideMemberFunctionDecl`, `ConstructorDecl`, `StoredParameter`,
`FieldDecl`, `TypeSideFieldDecl`, `AccessorDecl`, `ForwardDecl`,
`TraitMethodDecl`, `ConformanceMethodDecl`, `ExtensionSetFunctionDecl`,
`ActorOnDecl`, `ActorRequestDecl`, `BitfieldNamedSlot`, and `FlagNamedSlot`.
Each carries the existing `MemberVisibility?`; this list adds no production or
spelling. Frontend projection is lossless:

```text
MemberVisibilitySurface ::= EXPLICIT_MINUS | EXPLICIT_HASH | EXPLICIT_PLUS | OMITTED
OMITTED                  ::= null
```

`OMITTED` is not an element of the three-point order. R58 supplies no global
default. The immediate parent-owner contract must preserve, resolve, or reject
it before a judgment that needs a concrete member domain.

For a concrete visibility `v`, static access is admitted exactly when both
`OwnerReachable(owner, site)` and `MemberDomainAdmits(v, anchor, site)` hold.
`-` requires the access context's nominal identity to equal the original
declaring nominal anchor; `#` permits that identity or a transitive nominal
subclass; `+` adds no member-local restriction. Same-module and same-package
peers, conformers, witness holders, extensions, and structurally similar types
do not satisfy the subclass predicate. Thus effective member visibility is an
intersection, never an escape from top-level owner visibility.

An override retains `(OriginalSlotId, OriginalDeclaringNominalId)` as its
access anchor. Once omission has been handled by the immediate owner contract,
slot admission requires `rank(override_visibility) >= rank(slot_visibility)`.
It may preserve or widen visibility, but may neither narrow the slot nor
replace the original anchor with the overriding type. Narrowing emits
`OVERRIDE_VISIBILITY_CANNOT_NARROW`. A separate Trait requirement comparison
continues to emit `TRAIT_REQUIREMENT_VISIBILITY_MISMATCH` when a well-formed
witness does not satisfy the requirement.

Primary diagnostics follow declaration admission order. On a member callable,
the wrong word `public`, `common`, `private`, or `protected` emits
`CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN` before any slot comparison. With a
valid sigil, override narrowing emits `OVERRIDE_VISIBILITY_CANNOT_NARROW`
before a later Trait requirement visibility comparison. The visibility proof
is compile-time metadata only: it introduces no runtime lookup, check, registry,
MIR operation, xVM instruction, or backend instruction. A rejected declaration
or access produces no HIR residue.

Conformance selection must produce a unique `WitnessId`. Extension-member selection must produce a unique `ExtensionMemberId` and activation origin. Source order is never coherence evidence. Dynamic Trait state and first-class/local Witness values remain nonactivatable until their scope, escape, coherence, cleanup, and ABI laws are closed.

For an ordinary member selector, nominal and active-extension applicability are
computed as independent sets. If both sets are nonempty, the judgment fails
with `MEMBER_EXTENSION_COLLISION` and produces no selected member. No
within-domain or cross-domain source/import/activation-order rank is attempted
to escape that collision. An exact qualified extension selector restricts the
candidate domain before this test. The former
`EXTENSION_SHADOWED_BY_MEMBER_COMPAT` and
`STABLE_MEMBER_EXTENSION_COLLISION` names are nonemitting retired
compatibility identities.

The Stable declaration surface is normalized before evidence selection.
`type Target conforms Trait` forms an external record, while `type Name = Type`
forms an alias; the decisive `conforms`/`=` lookahead prevents either route from
being reinterpreted as the other. A class admits at most one `derives Base`
clause and then zero or more `conforms Trait` clauses. Ordinary, value,
resource, and data classes and Enums admit those repeated conformance clauses.
A Trait admits repeated `derives Parent` clauses. Every nominal relation starts
at a physical line boundary, which closes any clause-local `where` before the
next relation. Class subtyping, parent-Trait proof obligations, and ground
conformance records retain separate identities.

An external record may retain `as name`, lowercase `via Provider`, a local
`where` condition, and an explicit body. Lowercase `via` may have a body and
does not denote a separate semantic conformance for the same normalized ground
key. A bodyless direct record is admitted only when compatible defaults close
every requirement. `supports auto` registers a closed synthesis policy on the
Trait; bodyless `by auto` invokes only that exact policy. An unregistered,
ambiguous, structural, extension-derived, provider-discovered, or runtime
policy produces zero candidates.

A nominal `conform Trait { ... }` block groups witnesses for one matching
header clause and is admitted only inside that Class or Enum body. Lexical
containment fixes the target nominal owner, so `conform Trait for Type` and a
top-level `conform` block have no production. Names inside the matching block
are unqualified; an external `type Target conforms Trait { ... }` body may use
`Trait::member` to bind one exact requirement. The witness-marker domain stays
exactly `.`, `+`, `*.`, and `*+`; `as name`, `<T as Trait>::Item`, associated
bindings, and lowercase `via` retain their existing identities. Conformance is
not admitted in a function/block scope, and it cannot create storage, layout,
constructors, general extension members, or private construction authority.

Actor Protocol conformance uses a separate direct-only relation. An Actor may
repeat `conforms Protocol` header clauses, each resolving to exactly one
`ActorProtocolId`, and each relation requires exactly one lexical
`conform Protocol { ... }` block in that Actor body. The Actor-specific block
contains only `ActorOnDecl` and `ActorRequestDecl`; it is not the Class/Enum
Trait witness block. Matching declarations outside the block are concrete Actor
operations and create no structural evidence. `via`, `by auto`, external or
runtime conformance, ordinary Trait targets, specialization, priority, and
source/import-order selection are not admitted by this profile.

The terminating predicate `ActorProtocolGateAdmitted` interns one
`ActorProtocolConformanceId`, enumerates the finite direct requirement set, and
maps every exact `ActorProtocolRequirementId` to exactly one block-local
`ActorHandlerId` or `ActorRequestId`, producing one
`ActorProtocolBindingId`. `send` binds only `on`; `request` binds only
`request`. Parameter channels, labels, transfer modes, and types are exact after
normalization; request result type is exact; implementation ErrorSet and
EffectRow are subsets of the requirement rows. A zero or multiple candidate
set is terminal and has no fallback or order winner.

Inherited parent evidence retains its original owner and is interned when the
normalized instantiation is equal. A child-local replacement, specialization,
priority, import/source-order winner, fallback, and runtime witness lookup are
forbidden. The frontend preserves `TraitId`, `ConformanceId`,
`TraitWitnessId`, `RequirementId`, `ImplementationId`, substitution,
responsibility, and authority through HIR, public API residue, and MIR.

Static capability selection is domain-directed. `Type::item` checks only the
nominal/type-side domain; `Type::extension::item` checks only that exact named
extension; `<T as Trait>::item` checks one already-selected conformance/witness
and emits the exact Trait requirement identity; runtime service/Actor/shared
state begins from an explicit value owner. The checker must not make
`T::item` search imported Traits. A selected Trait-associated value/function
retains `TraitId`, `RequirementId`, `ConformanceId`, `TraitWitnessId`,
`ImplementationId`, substitution and responsibility through HIR/API/MIR.
These fields are carried by one non-structural
`TraitAssociatedStaticSelection` keyed by `SelectionId`; substitution and
responsibility are explicit `SubstitutionId` and `ResponsibilityId`, not
implicit checker state. For an associated function, representation metadata
maps `ImplementationId` to the exact `CallableImplementationId` and preserves
the direct static symbol. An associated type has no runtime operation; an
associated value or bare function reference uses the existing static-reference
lowering; an invoked function uses the existing
`ORDINARY::TRAIT_WITNESS` static-reference-plus-`INVOKE` lowering. The MIR
static identity table preserves the descriptor exactly and cannot reconstruct,
search, reorder, specialize, fall back, or replace its witness.
Initial associated `let::` values must be immutable, Shareable, no-drop,
authority-free, acyclic and statically materializable. No companion object,
metatype value, activation trigger, fallback, provider order, or runtime lookup
is synthesized.

The operator token and precedence table is closed. Arbitrary custom
glyph/fixity/precedence declarations are rejected rather than Preview. Stable
fixed-glyph conformance selection owns exactly thirteen roles:

- unary `+` and `-` through `UnaryPlus` and `UnaryMinus`;
- binary `+`, `-`, `*`, `/`, and `%` through `Add<Rhs>`,
  `Subtract<Rhs>`, `Multiply<Rhs>`, `Divide<Rhs>`, and `Remainder<Rhs>`,
  each with one associated `Output`;
- `==` and `!=` through one `Eq<Rhs>.equals` witness;
- `<`, `<=`, `>`, and `>=` through one `Ord<Rhs>.compare` witness.

`!=` is the Boolean negation of the selected equality result. Each order glyph
projects the sign of the same comparison result; no per-glyph order witness
exists. `Ord<Rhs> derives Eq<Rhs>`, and comparison zero must be exactly the
strong-equality relation.

Intrinsic-reserved normalized operand pairs use `INTRINSIC_ONLY` and perform no
conformance lookup. Every other admitted operand or pair must select exactly one
left-nominal-owner `DIRECT_GLOBAL` conformance from
`(OperatorId, OperandType)` or `(OperatorId, LeftType, RightType)`. Expected result, implicit conversion,
extension/local/case/provider/`via`/`VIA`/`AUTO`/specialization evidence,
source/import order, runtime relookup, and fallback neither create nor rank a
candidate. The selected conformance, witness, method, substitution, output type,
and responsibility profile are static identity. Its method borrows both
operands, is synchronous, non-consuming and non-mutating, and has
`throws Never effects {}`. An admitted numeric operation may terminate through
the closed nonrecoverable `ArithmeticDefect` profile before commit; that
terminal is not an ErrorSet member.

Compound `+=`, `-=`, `*=`, `/=`, and `%=` derive from the corresponding binary
row plus exact assignment admissibility. They own no separate Trait, witness,
or overload-resolution pass. The target place is evaluated once, the original
value is read once, and a terminal before final write preserves it.

Rational supplies the full admitted arithmetic profile, strong Eq, and total
Ord. Its remainder is `a - trunc(a / b) * b`, with quotient truncated toward
zero. Zero-divisor division or remainder raises `ArithmeticDefect` before
commit; the named checked division API remains available. Complex has its
admitted arithmetic and intrinsic partial equality but neither Remainder nor
Ord. Float/Complex partial equality cannot satisfy strong Eq by inference.

An ordered Enum is eligible only when its nominal owner is nonempty,
payload-free, nongeneric, and selects exactly one of `enum#increasing` or
`enum#decreasing`. The owner receives one whole-Enum Eq/Ord witness pair;
`SemanticOrderRank`, rather than `VariantId`, tag, discriminant, layout, or ABI,
drives all six comparison glyphs. Explicit `..` and `..<` ranges advance in
semantic ascending order and respectively include and exclude the upper
endpoint. Reverse traversal uses `downTo`; reversed endpoints, different Enum
owners, unordered Enums, payload Enums, and generic Enums reject before range
construction. This language-owned range rule creates no operator-conformance
hook or implicit whole-Enum iteration.

Other glyph families remain intrinsic-only or excluded from conformance
overloading. Power, strict/short-circuit logical, bitwise, range, and arbitrary
custom glyphs have no user hook. `TCC-P1-002..008` remain OPEN product and
independent-conformance evidence gates.

Trait language roles are a closed, core-owned registry keyed by a
`TraitLanguageRoleId` distinct from `TraitId`. The role and version are carried
by the Trait contract, consumer HIR and module API digest; adding or changing a
role is an API/source change. `trait#operator` applies only to the nine roots
above and does not select glyphs. `trait#iteration` applies only to core
`Sequence` and `Iterator`, `trait#interpolation` only to core `Display`, and
`trait#binding` only to core `Failable`. Users may declare direct global
conformances to an eligible role-bearing Trait but may not declare a new
role-bearing root. Generic `#role`/`#profile`, a public `#proof`, and
conversion/literal/actor/message/derive/marker/intrinsic roles reject.

`Failable` fixes associated types `Success` and `Failure` and the associated
static function
`def ::branch(move source: Self) -> BindingBranch<Success, Failure> throws Never effects {}`.
One unique direct-global witness must be selected before the guarded binding is
sealed. `let? successPattern = expression else failurePattern => exit` evaluates
and consumes the expression once, invokes `branch` once, requires both patterns
to be irrefutable for their associated types, and commits all success bindings
once only on the success alternative. The failure alternative publishes no
success loan/move/binding residue and must structurally leave the enclosing
continuation. `Option<T>` fixes `Failure = Unit`; `Result<T,error E>` fixes
`Failure = E`. No `if let?`, `while let?`, `var?`, bare `let?`, borrowed probe,
runtime role lookup, provider fallback, local evidence, `VIA`, `AUTO`, or
specialization route exists.

The Stable `&&`, `||`, `^^`, and prefix `~~` family has a pointwise logical
type rule. A packed known-width integer or identical bitfield/flags pair returns
that same domain. A binary pair of exact same-shape `NumericArray<I>` values
returns the same shape and element domain when `I` is one exact known-width
integer type; unary complement preserves the same shaped carrier. Scalar
`Bool`, `NumericArray<Bool>`, differing shapes or element domains, implicit
broadcast/conversion, dynamic shape, generic collections, and user carriers
are not admitted. The result is never implicitly convertible to a Bool
predicate and contributes no flow fact.

Function static activation is not a value or effect captured from the first
caller. The checker assigns one `FunctionStaticOwnerId` to the exact
`CallableImplementationId`, normalized owner/callable substitutions, activation
contract digest, and sorted actually-used Witness/Conformance/helper identities
and safety digests. The activation body has `throws Never`, `effects {}`, no
caller capture, no authority, suspension, Resource or persistent `needsDrop`
residue, and no dynamic/provider/activation-bearing callee. Receiver and
arguments are staged first; parameter ownership commits only after the
activation reaches `Ready`. `Failed` is terminal and cached, and reentry is a
canonical cause rather than a second type/effect channel. The callable type
does not gain a parameter or effect, but exported metadata and link identity
retain the activation profile and digest.

The current contextual surface is `static { ... }`. Persistent
`static#slot name` declarations and
`static#slot::name` references are a separate nonactivatable Preview Design.
The explicit `#slot` marker avoids the Stable `let::` and
`QualifiedStaticExpr` grammar domains. That design owns one
closed `FUNCTION_STATIC_NAMESPACE` lookup domain and a distinct
`FunctionStaticSlotId(FunctionStaticOwnerId, canonical_name)`. Its M0 slot type
must be deeply immutable and static-materializable and must contain no interior
mutable state, Resource, authority, borrow, finalizer, or `needsDrop`
responsibility. A staged initializer may read only prior slots; self, forward,
cyclic, hidden-reordered, mutable, exclusive-borrow, move/consume, and external
access plans are rejected. Slot publication is atomic with the existing
`Ready` state and creates no new retry or failure identity.

## 14. Rows, labels, Records, and schema materialization

A structural Record type carries an ordered canonical label row for identity/digest purposes while source construction preserves declared evaluation order. Label equality is static identifier equality, not runtime string equality. Row combination requires provable disjointness or an explicit overriding law owned by the operation.

Typed labeled materialization checks the target schema/Record row, field defaults, computed-field restrictions, duplicate labels, and source evaluation sequence. Schema unfolding does not weaken required fields and does not treat a runtime Map as a schema. Public API digests retain labels and construction responsibility where observable.

## 15. Ownership and place-state transitions

Each place has a state sufficient to reject use-after-move, overlapping inout access, mutable/shared alias violations, and borrow escape. A move consumes the source place unless the normalized type is reusable. A shared borrow prevents conflicting mutation for its admitted region. An inout borrow is exclusive and cannot be duplicated. Resource cleanup responsibility follows the owned value across moves.

### 15.1 Type ownership qualifier normalization

`TypeOwnershipQualifier` is the closed identity domain `UNQUALIFIED`,
`OWNED`, `BORROWED`, `MUT`, and `INOUT`. Source prefixes map one-to-one from
`owned`, `borrowed`, `mut`, and `inout`; an absent prefix maps to
`UNQUALIFIED`. The normalized identity tuple is
`(qualifier, base_normalized_type_id, region_binding_or_null)`. Region binding
is required exactly for `BORROWED` and `INOUT` and is null for `UNQUALIFIED`,
`OWNED`, and `MUT`. A qualifier does not imply a representation, layout, ABI,
serialization, discriminant, or backend pointer choice.

Alias expansion precedes qualifier-admission checking and leaves at most one
qualifier. Any nested or mixed qualifier is ill-formed, including when the
second qualifier is revealed only by an alias. All qualified wrappers are
invariant in their base type. There is no implicit qualifier covariance,
contravariance, erasure, or source-order precedence. `Optional` binds inside a
prefix qualifier. Union and intersection bind outside it unless parentheses
make the whole composite the qualified base. A union or intersection may not
combine differently qualified alternatives and then erase that difference at
join.

The qualifier capability table is exact:

| qualifier | owner class | read | write | region | MIR projection |
|---|---|---:|---:|---|---|
| `UNQUALIFIED` | base-type-defined | base-defined | base-defined | none | base responsibility |
| `OWNED` | explicit value owner | yes | base-defined | none | base `REUSABLE` or `OWNED` class retained |
| `BORROWED` | shared view | yes | no | required | `BORROWED` + `RegionId` + `LoanId` |
| `MUT` | unique mutable owner | yes | yes | none | `OWNED` + mutable-place capability |
| `INOUT` | exclusive mutable view | yes | yes | required | `INOUT` + `RegionId` + `LoanId` |

`OWNED` and `MUT` are storable and returnable subject to the base type's
ordinary laws. `BORROWED` may be used only while one exact owner region is
live. A borrowed result additionally requires an invocation-bounded callable
and one exact input or receiver origin recorded in HIR and the module API
digest. `INOUT` is limited to a local or private invocation-bounded exclusive
view and cannot enter storage, results, public residue, captures, suspension,
isolation transfer, or FFI. Missing/escaping regions select
`BORROW_ESCAPE_OWNER_REGION`; illegal qualifier composition or context selects
`OWNERSHIP_MODE_ADMISSION_FAILED`.

Parameter mode is a separate axis. `mut name: T` creates a mutable callee local
whose normalized value type is `T`; `name: mut T` receives an ordinary channel
whose normalized value type is `MUT(T)`. Likewise `inout name: T` acquires an
exclusive caller-place channel, whereas `name: inout T` would be an ordinary
channel carrying an already-proven exclusive view and is rejected outside the
narrow private invocation-bounded profile. Neither syntax is rewritten to the
other by the parser, formatter, checker, HIR, or API digest.

The construction lifecycle is represented in HIR by one structural plan and in
Deeplus MIR by the closed construction/cleanup operation family. The token,
owner, phase, required/initialized/delegated/registered masks, and terminal
publish-or-abort transition remain explicit across lowering. A backend may
coalesce storage only after preserving this state machine and its failure edges.

Closure capture, async suspension, actor isolation, Facet packaging, defer registration, and return are escape boundaries. The checker must prove every captured borrow outlives its use and every resource has exactly one cleanup path. Borrow Facet packaging is current because it cannot outlive its source region; owned and inout Facet packaging remain Preview-design.

### 15.1 Suspension-frame responsibility

`await` and `yield` do not delegate ownership decisions to a coroutine backend.
For every async or generator callable, HIR records one static
`ContinuationFramePlanId`. Every source suspension site has one stable
`SuspensionPointId`, and every live place admitted across that boundary has a
deterministic `FrameSlotId`. A runtime invocation owns one non-forgeable
`ContinuationFrameId`. Each visit to a suspension site, including repeated
visits from a loop, allocates a fresh monotonically increasing
`SuspensionEpochId`; a site identity is therefore never reused as a race
identity.

At suspension commit, all live owners, admitted static loans, cleanup tokens
and retained authority tokens are partitioned atomically between the running
scope and the continuation frame. The two sides are disjoint and their union
is the complete live set. A partial, duplicated or lost transfer is invalid.
Managed `RootId` values identify storage locations, so a root identity itself
is never transferred: verified source roots are bijectively rebound to fresh
destination roots with equal descriptor, generation and provenance. The
destination root map is installed and the immutable continuation receipt is
published before source roots are removed; collector entry during that handover
is forbidden. Preparation may allocate and validate the proposed frame, but it
changes no owner. Only the commit moves the exact responsibility partition.
Resume returns it to the running scope; cancel keeps it in the frame and begins
cleanup.

The first implementation profile admits only four slot dispositions:

- `NOT_LIVE_AFTER_SUSPEND`: no slot and no responsibility crosses;
- `REUSABLE_COPY`: one reusable value slot, with no owner or cleanup token;
- `OWNED_TRANSFER`: one owned slot carrying its exact `OwnerId`, deterministic
  per-token cleanup bindings and zero or more destination root projections;
- `STATIC_SHARED_BORROW`: one immutable shared borrow whose root is proven
  static and nonmoving.

Stack- or region-rooted shared borrows, `inout`/exclusive loans, temporary
views, callback borrows and borrow Facets must end before suspension. An actor
turn may persist only as the explicit `ACTOR_TURN` scope carrying `ActorTurnId`,
state region, mailbox, and the retained `STATE_REGION_MUTATION` and `DEQUEUE`
authority axes. An actor-state borrow may not cross the boundary; state access
is reacquired with a fresh `LoanId` only after resume.
The specific `FACET_BORROW_CROSSES_SUSPENSION` diagnostic takes precedence for
a borrow Facet. Other forbidden loans use `BORROW_CROSSES_SUSPENSION`.

One committed epoch admits exactly one winner between resume and cancel. A
late or duplicate signal has no ownership effect, and a terminal frame cannot
resume. Cancellation cleans frame-held responsibilities exactly once in
reverse registration order within reverse nested cleanup-region order. A
cleanup failure does not skip later cleanup and is recorded by the existing
primary/suppressed failure law. A terminal frame retains no owner, loan,
cleanup token, root, frame slot or actor authority.

The machine-readable contracts are
`spec/contracts/continuation-interface-r1.json` and
`spec/contracts/suspension-frame-responsibility-r1.json`, with typed immutable
commit and winner-claim receipts defined by
`schemas/language/continuation-receipt-r1.schema.json`. They add no source
spelling or grammar production; the existing `await`, `yield`, `for#await` and
async callable surfaces remain unchanged.

A free read of an ancestor local or parameter is classified independently from
environment capture. It is admitted as a lexical dependency only for a
synchronous same-isolation callable whose residence is proven region-bounded,
whose access is normalized `Read`, whose rooted borrows do not escape, and
whose target is `LiveReadable` at each call. Immediate invocation, a
block-closed local-function use graph, a bounded local binding whose uses are
all direct calls, and an exact selected invocation-bounded `#scoped` formal are
the initial proof routes. An unknown or merely textual `#scoped` route is not
evidence.

The normalized callable descriptor is the product of
`Residence = FrameIndependent | RegionBound(RegionId)`,
`Environment = Empty | Explicit(CapturePlan)`, a `closed_assertion` bit, and a
source-ordered capture plan whose field identity is `CaptureFieldId(CapturePlanId, source ordinal, canonical name)`. Reference captures and `let`/`var` initializer captures are distinct HIR variants. Every initializer resolves outside the capture-binder scope; `var` requires a mutable environment, `inout` requires `#scoped#mut`, and capture `once` requires an explicit callable `#once`. Preparation is left-to-right exactly once, rollback is reverse-order over the prepared prefix, and publication is one atomic environment commit. The plan is bound by `spec/contracts/closure-capture-plan-r1.json`. The callable also carries a
sorted unique lexical-dependency row. This form preserves mixed explicit
capture and lexical read. RegionId is value-level and must not escape through a
function type or module API digest. A region-bound callable converts only to a
compatible `#scoped` use. Present empty `[]` asserts no ancestor-frame
dependency; a bare `[name]` remains an explicit-capture compatibility form.
Lexical access never creates a snapshot or capture-plan acquisition. Writes,
moves, consume, suspension, async/generator/run/actor/FFI isolation,
`def#guard`, place death, and escape require another explicit admitted route.

`SharedCell<T>` admits only normalized Plain payload. Construction remains the
ordinary qualified call `SharedCell::new(move value)`; receiver operations use
message-call syntax: `cell ~ withValue { borrow value => body }` and
`cell ~ replace move next`. `withValue` has a `#scoped` callback callable
profile, while `borrow` alone is the callback binder mode. Its region is owned
by that invocation, so the borrow cannot escape or suspend. `replace` commits
one new owner while returning the old owner; Plain supplies neither raw layout
nor lock-free representation. `SharedMutex<T: SharedMutexPayload>` admits the
no-lifecycle-payload minimum profile. `SharedMutexPayload` is a sealed,
context-specific public constraint, not a Trait and not a user conformance or
synthesis surface. The internal `SharedMutexPayloadAdmitted` predicate first
normalizes aliases and the finite owner-closed payload graph. It admits only a
Reusable or Affine payload for which every reachable component has no Resource
lifecycle, cleanup token or hook, cleanup ErrorSet or EffectRow, authority,
suspension or cancellation responsibility, and no borrow or `inout` view. An
opaque component or unbounded generic is rejected; a generic payload therefore
requires the explicit `SharedMutexPayload` bound. Successful admission creates
no Plain, Copy, Clone, Shareable, Transferable, layout, ABI, serialization or
other responsibility implication, and the exact bound remains in public API
identity. `SharedMutex::new(move value)` checks the predicate before move commit
and is otherwise an ordinary qualified call, while
`mutex ~ withLock { inout state => body }` is a receiver message call.
`#scoped` belongs to the callback type/profile and `inout` is the binder mode;
the invocation owns the non-reentrant, non-suspending region. Unlock is an
infallible exactly-once cleanup on every terminal path and establishes the
mutex handoff edge to the next successful lock. No type rule infers weaker
ordering, poisoning, fairness, lock ordering, actor transferability, or hidden
cleanup.

Actor message typing has one closed admission family. It first resolves the preserved selector path in the actor or actor-protocol domain, with no ordinary-method fallback, and then applies the ordinary static channel matcher to the preserved ordered `CallArgument` list. A trailing closure that crosses actor isolation must independently satisfy transferable capture, suspension, effect, error, and cleanup requirements; trailing syntax supplies no such evidence. An actor with no `MailboxClause` has profile `logical_unbounded_v1`; a positive static `#mailbox(capacity: N)` has profile `bounded_reject_v1`. A one-way send checks as `Result<Unit, error ActorMessageError>`. A request whose declared reply type is `T` checks immediately as `Result<Reply<T>, error ActorMessageError>`; `await` applies only after pattern-matching or otherwise extracting that `Reply<T>`. Each successfully admitted request carries a non-forgeable `ReplyResponsibility` descriptor in typed HIR, module API digest, and MIR. Its exact fields are normalized result type, handler ErrorSet, cancellation axis, isolation owner, `ReplyId`, request correlation identity, and terminal transport failure. Module API identity stores static `reply_id = per_value_non_forgeable` and `correlation_id = per_value_non_forgeable` policy markers, while each committed request keeps its concrete identities only in value-level typed HIR/MIR. Awaiting a handler declared `throws E` therefore exposes exactly `E | ActorMessageError::receiverClosedBeforeReply` without adding a visible second `Reply` type parameter. The exact admission error cases are `mailboxFull`, `receiverClosedBeforeAdmission`, and `receiverClosedBeforeReply`. The first two are precommit admission results. The third is a declared terminal failure axis of an already admitted reply and does not retroactively change the successful admission Result.

A one-way protocol `send` requirement and its bound `on` implementation must
both normalize to the empty recoverable ErrorSet; omission and explicit
`throws Never` are equal. Any nonempty recoverable ErrorSet is rejected before
HIR binding because the admission result observes enqueue only, not handler
completion. A fallible acknowledged command is a `request` returning `Unit`,
and its admitted ErrorSet is preserved in `ReplyResponsibility`. Defect remains
a distinct lifecycle outcome.

Structured concurrency uses a separate nominal `Run<T>` responsibility. `concur { ... }` is its only lexical owner; each successfully admitted `spawn` creates one owner-bound `ConcurRunId` and child `ExecutionId`. `Run<T>` and `Reply<T>` are both one-shot awaitable values, but neither converts to, substitutes for, or joins with the other. A `Run<T>` cannot escape, be exported, or enter unowned storage without a separately admitted owner-transfer contract. A bounded `#async` lambda is admitted only inside its nearest `concur`, only with no capture or an explicitly proven reusable copy-only capture plan, and only for nonescaping inward use. General escaping async callable literals remain nonactivatable.

`AsyncSequence<T, E: ErrorSet>` binds its source failure set instead of leaving a free terminal type. Its `next` operation throws `E`, while cancellation remains a distinct control outcome. For `AsyncCollector::list<T, U, ES, ET>`, the source is `AsyncSequence<T, ES>`, the named asynchronous transform throws `ET`, and the result throws exactly `normalize(ES | ET)`. Neither source nor transform errors may be erased or converted to cancellation.

Before enqueue commit, all moved argument places remain live at the sender and a rejection allocates neither `MessageId` ownership nor `channel_sequence`. A successful commit consumes each moved sender place exactly once, installs exactly one actor-owned payload, and allocates the next strictly increasing sequence for the normalized `(SenderId, ReceiverActorId, MailboxProfileId)` key. Cancellation before commit aborts without transfer; cancellation after commit cannot restore the sender place or retract the message. Cancellation is a control axis and never a member of `ActorMessageError`.

An assignment target is checked and evaluated as one place. Compound assignment reads that place once, checks one exact intrinsic operand domain, evaluates the right operand once, and commits at most one result. A precommit `ArithmeticDefect`, `IndexError`, or other failure leaves the prior owner and value unchanged. Assignment expressions have result type `Unit`. Every admitted slice result is a `ReadonlyView`, never an assignable place; its borrow cannot escape its owner, cross isolation, hide a copy, or be implicitly rebased.

MutableList structural-edit statements are not ordinary index assignment. The
checker requires one exact exclusive `MutableList<T>` place and resolves each
surface to one of the closed Prelude operations `insertBefore`, `insertAfter`,
`prepend`, `append`, their four `insertAll*` forms, `removeAt`, `removeRange`,
`removeSelected`, `popFirst`, or `popLast`. A bulk payload is one finite
nonescaping `PositionalPack<T>` with reusable/copyable element evidence; plain
`Sequence<T>` conformance is insufficient. Receiver, selectors and payload are
evaluated once left-to-right; all coordinates, duplicates, alias/overlap,
borrows/views/iterators, payload ownership and required capacity/result storage
are validated or staged before one mutation commit. Failure preserves the
receiver and every source owner. Point removal returns `T`; multi-removal
returns `List<T>` in selector order while preserving survivor order, using
pre-mutation coordinates. The checker creates one ordinary `CallPlan` and
`CallableImplementationId`; it creates no edit-specific HIR/MIR identity.

For a simple mutable place and the same admitted operator domain, the canonical
source spelling is the compound form—for example, `count += 1`. This is a
source-style rule over the existing single-evaluation compound-assignment
judgment, not an increment operator.

## 16. Effects, errors, cancellation, and callable profiles

Effect rows and error sets are normalized finite rows. A named effect
capability is a nominal, non-value permission identity bound to one normalized
nonempty effect row. Declaring it neither performs the effect nor grants
authority. An effectful callable must expose the observable row and, where the
operation requires authority, receive the matching capability through an
explicit context channel. Effect description and authority possession are
disjoint judgments; neither is inferred from the other. `#pure` admits no
observable effect or hidden authority. `#guard` is a terminating,
nonsuspending, nonconsuming pure Bool predicate profile. A callable value's
type includes its effect row, error set, cancellation responsibility,
ownership/capture responsibility, suspension capability, isolation, and
relevant context/witness channels.

Stable callable responsibility spelling repeats one clause per normalized
term. `throws E1 throws E2` contributes the set union of `E1` and `E2`;
`effects io effects state` contributes the corresponding effect-row union.
The formatter places repeated clauses on separate aligned lines. `throws Never`
and `effects {}` are the only explicit empty spellings. A callable clause never
uses `|` or a nonempty `{...}` as list punctuation; those forms remain
type-level ErrorSet/EffectRow algebra. All throws clauses precede all effects
clauses, duplicate normalized identities are rejected, and source order is
retained only for deterministic diagnostics. Typed AST/HIR, callable identity,
API digest, and MIR carry duplicate-free normalized rows.

Class cleanup budgets reuse the same normalized ErrorSet and EffectRow identity
domains but have a distinct header surface and admission judgment. Let
`CleanupErrors(X)` and `CleanupEffects(X)` denote duplicate-free sorted sets.
For a class `C`, the checker computes both sets by unioning, in evidence order,
the base segment's transitive computed obligation when present, every owned
cleanup-bearing field's effective envelope in declaration order, and the
declared rows of `C`'s `def#cleanup` hook when present. Stable resource
inheritance is same-module and sealed, so the base computation is available to
the family checker without exporting private contribution identities. Every
statically reachable contribution is included; runtime path selection cannot
shrink a public envelope.

```text
ComputedErrors(C)  = Normalize(union contribution.error_ids)
ComputedEffects(C) = Normalize(union contribution.effect_ids)
Admitted(C)        = ComputedErrors(C)  subset_of EffectiveErrors(C)
                  and ComputedEffects(C) subset_of EffectiveEffects(C)
```

In a present `cleanup budget` block, each axis item has cardinality zero or one.
An absent `effects` item is `{}`, an absent `errors` item is `Never`, and an
empty block makes both axes empty. A repeated axis, a duplicate normalized
identity, or an `errors` type that is not ErrorSet-kinded is rejected. For a
non-inheritance class with no block, the effective envelope is exactly the
computed envelope and is still materialized in typed AST/HIR and public API
residue where the type is exported.

A Stable resource hierarchy has one same-module sealed root with an explicit
envelope. An implicit child inherits the root envelope. An explicit child may
normalize to an equal or narrower envelope, must cover its complete computed
obligation, and must prove both of its rows are subsets of the root rows. The
root envelope is therefore the family substitutability ceiling. Declaration or
subclass discovery order is not semantic. Cleanup budget admission does not
alter lifecycle ordering, failure suppression, loan closing, or runtime effect
authorization.

The concise omission successor remains Preview Design and does not supersede
current private ErrorSet inference. In that Preview, omission of a syntactically
admitted `throws` axis normalizes to `Never`, omission of `effects` normalizes
to `{}`, and a callable implementation is admitted only when its body rows are
subsets of those normalized declaration rows. Lossless spelling presence is a
CST concern only; typed AST/HIR, callable identity, API digest, and MIR always
carry complete rows. Trait witness compatibility uses row narrowing, override
compatibility retains its exact current profile law, and function-value
compatibility uses row subsumption under current variance. Stable promotion
requires a deterministic migration of every affected inferred private/local
signature and an explicit supersession of `private_error_set_inference`.

Errors, defects, and cancellation are distinct control outcomes. Propagation operators consume only their declared family. Cleanup executes under a deterministic budget before the outcome escapes. Async suspension preserves live-place and cleanup obligations, and cancellation cannot silently bypass a registered cleanup. Callable compatibility is contravariant/covariant only where the declared responsibility profile permits; default inference remains invariant and conservative.

Checked integer overflow and integer division or remainder by zero produce
deterministic `ArithmeticDefect`, not a recoverable ErrorSet member. Integer
quotient truncates toward zero; remainder obeys
`a == trunc(a / b) * b + r`, with `r == 0` or the dividend sign and
`|r| < |b|`. Signed `MIN / -1` and `MIN % -1` are overflow. If the checker
proves failure statically it rejects the expression; otherwise the Defect edge
occurs before an enclosing assignment commit. Floating and Complex remainder
are absent; wrapping, saturating, or alternate remainder behavior is available
only through explicitly named APIs.

`CaretPowerAdmitted(Base, Exponent)` is a finite static-domain judgment and
never a conformance query. It selects one of `CheckedIntPow`, `FloatPowInt`,
`FloatPow`, `ComplexPowInt`, `ComplexPowPrincipal`, or
`MeasurePowStatic`, fixes the result type, and produces a closed operand
adaptation plan. Expected-result type, runtime sign/integrality, import order
and Trait evidence participate zero times. Integer power requires a statically
nonnegative exact exponent. Float power stays Float; a negative finite base and
nonintegral finite exponent yields canonical quiet NaN. Complex power uses the
principal branch. The exact plan and its numeric/special-value profile
identities become HIR-H1 residue and are recomputed by the verifier before MIR.
NumericArray infix power, transpose and linear algebra retain their separate
intrinsic judgments.

The Preview numeric successor may extend this finite judgment with
`RationalPowInteger` and exact literal adaptation plans, but it does not add a
`Power` Trait, runtime integrality test, expected-result route, mixed-width
conversion, or current product cell. `Rational ^ Int` remains
nonactivatable until the Preview profile receives separate activation evidence.

## 17. Pattern partition and exhaustiveness

Pattern checking first normalizes the subject domain, then constructs disjoint
partitions for enum/union/Option/Result alternatives, exact Tuple arity and
child cells, exact/open Record and Map rows, closed List length/rest cells,
transparent nominal products, admitted ordered scalar intervals, and loop
outcome. Sealed-Class closure informs nominal analysis but does not expose an
ordinary Class representation. A guard refines only the already admitted
structural partition and may read ephemeral probe binders, including a probe
rest, without moving, escaping, suspending, mutating through, publishing a
final view, or acquiring authority from them. Enum cases use `::case` or
`Type::case`.

Exhaustiveness succeeds only when the normalized current pattern partition is
covered. That partition is finite either by closed constructor/type identity or
by an admitted symbolic scalar split with one complement cell. For each arm the
checker intersects structural coverage with the subject domain and removes only
coverage from earlier reachable unguarded arms. An empty result is
`MATCH_ARM_UNREACHABLE`; an `otherwise` arm after an empty residual is
`OTHERWISE_UNREACHABLE`. Guarded arms remain useful but do not subtract
coverage. `MATCH_NONEXHAUSTIVE_AFTER_GUARDS` applies only when every final
residual cell was structurally mentioned by guarded arms; a never-mentioned
residual instead selects `MATCH_NOT_EXHAUSTIVE`. A sealed Class may prove
nominal-family closure for other checker judgments, but that proof is not a
substitute for absent constructor-pattern syntax. Clause functions and
declarative clauses reuse the same partition engine while preserving their own
input-supply, overlap, and return-totality rules.

The flow-proof environment `Phi` records closed-union alternative identities, enum-case identities, admitted finite R0 refinement facts, and usable-place state without changing a declaration's normalized semantic type. Structural success narrows an arm to the intersection of `Phi` and its coverage cell. Join is set intersection across incoming paths. Assignment, aliasing mutation, exclusive borrow, escape or capture, consume, and calls whose responsibility summary may mutate the subject kill the affected facts.

For a normalized closed Union only, `subject is Alternative` and the adjacent
negation `subject !is Alternative` read the stored injection identity once and
produce complementary `Phi` facts. `Alternative` must be exactly one declared
alternative identity; the test performs no subtyping search, refinement
execution, reflection, Trait discovery, or provider lookup and binds no value.
For `is`, the true edge intersects the current alternative set with the target
and the false edge removes it; `!is` swaps the two results. `and then` supplies
the left true edge to its right operand and `otherwise` supplies the left false
edge. Strict `and` and `or` do not pre-narrow their right operand. A durable
fact requires a stable place and is killed by assignment, aliasing mutation,
exclusive borrow, escape or capture with possible mutation, consume, or a
call whose responsibility summary may mutate or consume the subject. Every
other runtime type-test shape is rejected. `as?`/`as!` own conversion, and
typed patterns own alternative binding.

For a closed Union scrutinee only, a typed child binder naming exactly one declared alternative elaborates to `UnionAlternativeBindPattern`. Its test is the existing Union injection identity; it is not a subtype test or a refinement check. Union formation itself requires every normalized alternative pair to be proven disjoint by the finite R0 relation procedure. Equivalent or implying members are subsumed; overlap or an unknown relation rejects rather than choosing a runtime winner.

Refinement admission at construction, typed-pattern, argument, return, and explicit cast boundaries is three-valued: `PROVED` admits, `DISPROVED` emits the exact literal/range contradiction, and `UNKNOWN` emits `REFINEMENT_PROOF_REQUIRED`. A silent conversion outside those boundaries emits `REFINEMENT_IMPLICIT_NARROWING_FORBIDDEN`. `as?`, `as!`, and `T::check` retain their distinct Option, defect, and Result outcomes.

`T where > bound` is syntax sugar only for `T where this > bound`. Its right
side uses the bounded `RefinementComparisonOperand` parse goal—literal,
identifier, or qualified static value—rather than `PredicateExpr`; compound
logic therefore requires the explicit `this` form. `T in lower..upper` and
`T in lower..<upper` normalize to inclusive and upper-exclusive interval
facts. Bare `T > bound` is never a refinement, so a generic close such as
`Box<Int>` remains unambiguous before a following `where`. Every nonliteral
bound must resolve statically to one stable pure ordered value. Runtime bounds
are rejected, and normalization reads lower then upper without duplication or
reordering.

In statement and value `match` only, a
`lower OrderedRelOp name OrderedRelOp upper` head is a
`BoundedBinderPattern`. The scrutinee was already evaluated once before the arm
sequence; an attempted arm reads its literal or pinned stable bounds in written
source order and requires a monotone operator pair. Mixed strictness is
admitted, mixed direction is rejected before HIR. Success exposes one
arm-local subject binder and one normalized interval fact; failure exposes
neither. The interval is structural coverage, so exact open/closed endpoints,
overlap subtraction, residual witnesses, and `otherwise` use the ordinary
exhaustiveness algorithm rather than guarded-arm rules.

`def#guard` is an exact Bool, pure, total, terminating, nonsuspending,
nonconsuming, authority-free callable profile. An exact direct call contributes
branch-local facts to `Phi` only when the selected declaration exports a fresh,
valid `GuardSummaryV1` whose predicate is in finite R0 and whose formal
parameters substitute capture-free to stable actual places. The true edge adds
the normalized summary and the false edge adds its normalized complement.
Stored Bool results, wrappers, indirect calls, invalid or stale summaries, and
unstable actuals remain opaque. Existing mutation, aliasing, borrow, capture,
consume, suspension, and may-mutate/may-consume-call rules kill such facts. A
guarded arm never subtracts from exhaustiveness coverage.

## 18. MIR responsibility projection and evidence boundary

The checker hands MIR a normalized descriptor containing the selected static identities, call channels, labels, type arguments, ownership transitions, cleanup regions, effects/errors, failure edges, suspension/isolation, construction plan, and source provenance. MIR lowering must not repeat open-ended name, witness, extension, or provider lookup.

The canonical architecture is Rust frontend/checker, Deeplus MIR, Rust xVM bytecode/interpreter, Cranelift ObjectModule AOT, and later Cranelift JITModule. This file defines the design handoff only. Until artifact-bound target receipts exist, production parser, integrated checker, MIR lowering, xVM, Cranelift, formatter/LSP, and independent conformance remain `NOT_RUN` regardless of static schema or verifier success.

## Name resolution, visibility and lexical environment judgments

The checker keeps three environment families separate:

```text
NameEnv              : (Namespace, Spelling) -> Binding | OverloadSet
ActivationEnv        : ExtensionSetId -> ActivationOriginId
WitnessVisibilityEnv : (ResolverScopeId, EvidenceOriginId) -> VisibleEvidence
```

`NameEnv` lookup begins at the innermost frame and stops at the first frame with
an exact `(Namespace, Spelling)` entry. Outer entries do not join that tier.
Different namespaces may reuse a spelling. In one frame, two single bindings
reject, and callable declarations form one overload set only when their
canonical overload-slot keys are pairwise distinct. A result type,
responsibility-only difference, or declaration order does not make a slot.
Parameters and the root callable body share one collision frame.

A syntactically admitted declaration in a proper child block may shadow an
ancestor module, type, value, callable-overload-set, or import-alias binding,
and it receives a fresh typed ID. It may not merge an overload set across
frames. Member/type-side/associated/extension/witness capabilities are not
lexical shadowing. R4 has no root-connected control-label surface, so
control-label reuse is not applicable in the current profile; if a future
`FLOW_CONTROL_PROFILE` activates such a carrier, it must reject live-ancestor
reuse. A local function is visible only after its declaration. Transactional
pattern binders remain
provisional until commit; a successful commit allocates fresh `HirLocalId`
values and a failed probe changes none of the environments.

The following judgments are independent and fail closed:

```text
Γgraph ⊢ PackageGraph acyclic
Γgraph ⊢ ReexportGraph acyclic
Γheaders ⊢ ModuleHeaderScc header_only
Γstatic ⊢ StaticBindingGraph acyclic
Γscope ⊢ (namespace, spelling) ⇓ first_nonempty_frame
Γimport ⊢ ImportBindingId ↦ ImportTargetIdentity
Γvis ⊢ ImportTargetIdentity visible_in ResolverScopeId
Γmodule ⊢ normalized_public_residue ≡ ModuleSignature
Γhir ⊢ resolver_output sealed
```

A module-header SCC is admitted only after complete header collection and only
for module-header, type-declaration, and signature references. Static-value,
runtime-initializer, and re-export edges are forbidden within it. Static module
values use an acyclic compile-time graph, publish atomically only after every
value succeeds, and create zero runtime initializer operations.

Every imported local key is exactly
`(ResolverScopeId, Namespace, local_name)`. The same key is a duplicate even
when its target is equal, and is a collision when the target differs.
Different explicit aliases to one target are distinct.
`ImportTargetIdentity` is `Module(ModuleId)` for the `MODULE` namespace and
`Declaration(DeclId)` for `TYPE`, `VALUE`, and `CALLABLE_OVERLOAD_SET`.
A module target stays a resolver identity and creates no expression-HIR
reference. Only a declaration used as an expression projects to
`ResolvedRef::DirectDecl(DeclId)`; `ImportBindingId` remains resolver-trace
provenance. `SourceOriginId` orders diagnostic locations without turning span
or file traversal order into semantic priority.

Every admitted import or extension activation carries the provider pair
`(provider_binding_id_or_self, provider_module_id)`. `self` means that the
provider package equals the consumer package; it does not mean that the
provider module equals the consumer module. The nearest ancestor
`TargetScope` supplies the consumer `TargetId`, and each used pair must match
exactly one package-graph `visible_module_bindings` row for that target. The
dependency receipt's `required_interfaces` is exactly the unique used pair set
after excluding only `provider_module_id == consumer_module_id`. A
same-package, different-module provider therefore remains required with
binding `self`. Missing, extra, stale, or graph-unbound pairs fail
`DependencyInterfaceBindingClosed` before canonical HIR.

The R4 seal may emit a closed noncall `ResolvedRef`, name/import traces, and a
visibility proof. A callable candidate group is
`ResolvedOverloadSetRef` in analysis HIR only. Selecting its function,
completing generics, expected-type-directed choice, applicability/specificity
ranking, row inference, and result-type-only choice are expressly outside this
judgment and must be closed before canonical HIR-H1. This section preserves
already admitted `EvidenceOriginId` values but neither creates nor replaces
Trait witnesses.

Primary failure is the first failed stage in this exact order:
package/module/source graph; module skeleton; dependency interface; resolver
scope tree; reference candidates; visibility/activation; noncall selection;
resolver-HIR seal; module-interface digest. An exact owner-bound diagnostic
within a stage precedes its generic fallback. Stable `SourceOriginId` orders
primary and related spans; enumeration order never does.

This design closure leaves the exact 22 feature P1 items OPEN and all 15 product
lanes `NOT_RUN`.


## 19. Rightward local-binding normalization judgment

The frontend proves `Γ ⊢ e -> $x[: T] ⇝ let x[: T] = e` and `Γ ⊢ e -> $$x[: T] ⇝ var x[: T] = e` before semantic checking. The target is a fresh identifier and is absent from `Γ` while `e` is checked. The checker evaluates one initializer descriptor, checks the optional annotation, ownership, effects, errors, borrow regions and cleanup, then commits exactly one ordinary local. Failure commits no local. The same ordinary local-binding judgment is used for direct and normalized surfaces.

There is no `FlowBinding` semantic type or responsibility. Coroutine response binding retains the preceding suspension/resume event but delegates the resumed value to the same ordinary binding judgment.

## 20. Raw String and official tooling boundaries

`#raw"..."` has type `String`; body scalars are not escape-decoded and `$` has no interpolation role. The only semantic payload is the exact scalar sequence, lowered to `ConstString`.

R2 proof certificates and provider derive-via sidecars are tooling evidence, never types, witnesses, authorities or MIR values. A certificate is accepted only after deterministic checker validation or reduction to an R0/R1 obligation. Generated derive source is checked from scanner through MIR like handwritten source.

## 21. Dynamic-unit profile judgment

Dynamic conversion admission is the conjunction `ProfileActive ∧ ProviderBound ∧ PolicyComplete ∧ ProviderSupportsConversion`. No `#preview` predicate participates. Policy completeness includes observation timestamp, rounding, failure/effect rows, cache identity and replay token.


## 22. Sugar-equivalence and quarantine judgments

Field punning elaborates `label` to `label: label` before construction-row checking, without inserting clone, move, authority or lookup. Grouped forwarding elaborates to a finite ordered list of ordinary forwarding declarations and rejects duplicate or colliding names. Scoped import/use grouping pushes exactly one compile-time lexical frame for its `in` block and pops it on every exit. Enum comma lists, multiline indentation, and the single-guard law are parser/scanner obligations whose normalized HIR is identical to their unsugared forms.

`if let`, `while let`, and `for let` use one transactional `PatternAttempt`
judgment: evaluate once, acquire, compile and run a pure nonconsuming TestPlan,
expose read-only nonescaping probe binders, evaluate zero or one pure Bool
guard once after structural success, collapse every child `BINDING_COMMIT`
requirement into exactly one final logical commit, expose final binders,
execute, and exit/join. An Or probe selects the first source-ordered structural
success and never retries or backtracks. Every alternative must expose the same
normalized binder interface `(name, canonical type, ownership mode, mutability,
usable region, capability set)` or the checker emits
`OR_PATTERN_BINDINGS_INCONSISTENT`.

An Alias probe preserves subject identity, performs no clone, and stages a
shared borrow. It is incompatible with a moved or exclusively borrowed
descendant of the same subject. A borrowed subject cannot move an affine
payload; `move PatternPrimary` requires consuming owner authority. Probe and
guard failure publish no binding, move, loan, view, or authority and cancel
every prepared move reservation. Final success first performs the admitted
moves and loan acquisitions and then crosses one infallible group
`BINDING_COMMIT` publication barrier. A resulting loan ends at the earliest
mutation, move, replacement, cleanup, or enclosing-region frontier that
invalidates it. `if let` takes the false branch, `while let` exits the loop,
and failed `for let` matching or a false guard skips the current element.

Normally returning Pattern arms may join only when their place identities and
ownership states are compatible. The capability intersection is computed only
after that compatibility proof; divergent arms are excluded. Otherwise the
checker emits `PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH` and does not infer a
clone, implicit move, or ownership join.

The quarantine-scope predicate is design-seed-only and nonemitting. Even its minimum sound profile requires a typed immutable export and rejects pointer, authority, borrow, resource, closure, run, actor, suspension and outer-mutation escape. No source profile activates it and no product support is claimed.


## 23. Closed typing boundaries

`Map<String,V>.name` has no key-projection judgment. Dot selection performs only nominal member, active extension, or witness lookup; a missing selector produces `MEMBER_NOT_FOUND`. Map key access uses indexing or an explicit API and preserves ordinary lookup failure.

No increment/decrement expression is typed. An explicit assignment checks the target place once under the ordinary assignment/place-state law. No implicit pre/post value result, overflow mode, or hidden mutation node is inferred.

The callable-profile set has no tail-recursion kind. Recursive ordinary functions are typed like other functions. A backend may optimize a recursion cycle only after proving observational equivalence to the same Deeplus MIR.

There is no regex-literal type rule. Pattern libraries receive ordinary `String` or `Bytes` values through explicit constructors and expose their own error/effect contracts.

List literal inference computes one homogeneous normalized element type. It never constructs an anonymous Union. When the expected type is explicitly `List<A | B>`, each element is independently injected into that already-declared closed union; ambiguity, subsumption, and narrowing follow the ordinary union laws.


## 24. R51f3 promoted profile typing boundaries

- `Pattern.compile` has explicit `String`, engine, and budget inputs and returns `Result<Pattern, error PatternCompileError>`; no contextual literal conversion or hidden engine lookup exists.
- xVM agent, tail-call analysis, and UML state-machine provider are tooling contracts and create no source type, witness, overload candidate, effect erasure, or public API residue.
- Tail-call eligibility is backend evidence over already-typed MIR; it never changes call typing, cleanup, errors, suspension, or authority.

## 25. Current value, operator, index, and slice judgments

The following conceptual judgments close the source-visible current profile without selecting an implementation representation:

```text
Γ ⊢ literal ⇒ SemanticValue : T
Γ ⊢ intrinsic-glyph(lhs, rhs) ⇒ T | Bool | Unit
Γ ; Π ⊢ owner[index] ⇒ Element throws IndexError
Γ ; Π ⊢ slice-carrier[range] ⇒ ReadonlyView<Element>
Γ ; Π ⊢ numeric-array[slice-axes] ⇒ ReadonlyView<Element>
```

`List<T>`, `String`, and `Bytes` have the built-in domain `1..length` and storage offset `index - 1`; their element results are respectively `T`, `Char`, and `UInt8`. Every `ReadonlyView<T>` preserves its source owner's declared logical domain, mapping, provenance, and open-end boundary identity and returns borrowed `T`; ordinary one-based sources remain one-based, while bounded or sliced sources retain their coordinates. These carriers accept exactly one scalar or range selector. An explicitly bounded List preserves its declared inclusive `L..U` domain. `Map<K,V>` requires an exact `K` and returns `V` or raises `IndexError::keyNotFound`. Tuple `.n` and Record labels are static projections, not bracket indexing. Merely conforming to `Sequence`, `Indexable`, or `LogicalIndexDomain` does not create any bracket judgment.

Expression Range admits inclusive `i..j`, exclusive `i..<j`, one-sided lazy
`i...`, and an optional attached Range-owned `:step`. Its start, present end,
and step evaluate once left-to-right. Zero or direction-incompatible steps
reject; bounded iteration terminates before overflow, and a finite ordered Enum
cannot form a one-sided Range. IndexSuffix is a separate owner. It admits
`[..<end]`, `[..end]`, `[start..]`, and `[..]`; `start..<` has no distinct law
and rejects. NumericArray additionally admits exact-rank comma-separated axes,
where a scalar, slice, or full-axis `*` may appear. Empty `[]`, implicit
negative-from-end rewriting, Tuple-as-gather, and implicit linear indexing have
no typing rule. Successful slicing retains selected coordinates and owner
region; explicit named rebase/copy is required for new coordinates or
independent ownership.

## 26. Post-R51f3 nonactivatable Preview design

> Status fence: this section is governed by Part XII's current preimplementation Preview boundary. Current type-system behavior remains authoritative; the successor material is nonactivatable, implementation begins only after Deeplus 0.1.3 is established, and this text closes no P1 or product lane.

### Literal-shaped canonicalization and collection ownership

The accepted literal-shaped collection spellings are design-only type-position
sugar. Normalization maps `[T]`, `#mut[T]`, `#set{T}`, and `#map{K:V}` to
`List<T>`, `MutableList<T>`, `Set<T>`, and `Map<K,V>` respectively, and maps
`${label:T,...}` to the existing closed structural Record-row identity.
Normalization creates no wrapper, subtype, ABI identity, serialization
identity, witness, or operation. It runs only after an independently ratified
type-goal parse; it cannot use type information to reinterpret a value,
pattern, index, or NumericArray token stream.

The Record minimum profile is closed and required-label-only. Labels are static
Identifiers, duplicate labels reject, and canonical row identity keeps the
current order-normalization law. Map keys remain runtime `K` values. No
conversion, named unfold, or dot-key projection relates these domains. An
explicit Union inside a collection type remains an ordinary Union and the
sugar neither relaxes disjointness nor creates implicit heterogeneous-List
inference.

Immutable and mutable collection owners are distinct, non-subtyping
identities. A shallow freeze changes the outer owner state only; payload
ownership, alias, `Shareable`, `Transferable`, and witness obligations remain
separate proofs. Freeze is a prepare/commit transaction: a live borrow rejects,
failure returns the exact original owner and value state, and success consumes
exactly once. Snapshot borrows and preserves its source while producing a
point-in-time result whose later value is independent of source mutation.
A view borrows its owner, preserves logical coordinates and provenance, and
cannot overlap mutation, move, freeze, escape, suspension without an admitted
region proof, or actor-isolation crossing.

The current result identities `FrozenList<T>` and `ListSnapshot<T>` remain
distinct from `List<T>`. Any successor unification is an observable migration
because the current bracket matrix and shareability statements differ; it
requires explicit API, ABI, serialization, indexing, and actor-evidence review.
No representation complexity, copy-on-write strategy, common view carrier, or
new mutable Prelude family is selected by this contract.

<!-- POST_PR16_UNIT_BEGIN:SFD-N002 -->
```json
{
    "carrier":  "DynOwned",
    "existential_shape":  "exists T where DynPackable(T)",
    "fields":  [
                   {
                       "name":  "payload",
                       "type":  "Own\u003cT\u003e"
                   },
                   {
                       "name":  "runtime_type",
                       "type":  "RuntimeTypeId"
                   },
                   {
                       "name":  "drop_plan",
                       "type":  "DropPlan\u003cT\u003e"
                   },
                   {
                       "name":  "provenance",
                       "type":  "OpaqueProvenance"
                   },
                   {
                       "name":  "descriptor_schema",
                       "type":  "DescriptorSchemaVersion"
                   }
               ],
    "storable_modes":  [
                           "OWNED"
                       ],
    "loan_modes":  [
                       "BORROW",
                       "INOUT_DEFERRED"
                   ],
    "borrowed_carrier_variant_count":  0,
    "runtime_tagged_mixed_envelope_count":  0,
    "implicit_mode_conversion_count":  0,
    "DynPackable":  {
                        "status":  "GUARDED_OPEN_PREDICATE",
                        "requires":  [
                                         "admitted runtime descriptor",
                                         "concrete drop plan",
                                         "owned responsibility profile",
                                         "target/runtime metadata authority"
                                     ],
                        "inferred_packable_type_count":  0,
                        "closure_dependency":  [
                                                   "SFD-P1-005",
                                                   "SFD-P1-007"
                                               ]
                    }
}
```
<!-- POST_PR16_UNIT_END:SFD-N002 -->

<!-- POST_PR16_UNIT_BEGIN:SFD-N003 -->
```json
{
    "abstract_operations":  [
                                {
                                    "id":  "PACK_DYN",
                                    "signature":  "packDyn\u003cT: DynPackable\u003e(move value: T) -\u003e PackDynResult\u003cT\u003e",
                                    "kind":  "EXPLICIT_TRANSACTIONAL_PACK",
                                    "success":  "one Dyn owner",
                                    "failure":  "exact original T owner returned",
                                    "evaluation_count":  1,
                                    "commit_count":  "0_OR_1",
                                    "partial_publication_count":  0
                                },
                                {
                                    "id":  "IS_DYN_TYPE",
                                    "signature":  "isDynType\u003cT\u003e(value: borrow Dyn) -\u003e Bool",
                                    "kind":  "STATIC_TARGET_EXACT_TYPE_TEST",
                                    "requires_registry":  false,
                                    "owner_delta":  0,
                                    "witness_creation_count":  0
                                },
                                {
                                    "id":  "WITH_DYN_BORROW",
                                    "signature":  "withDynBorrow\u003cT,R\u003e(value: borrow Dyn, body: nonescaping (borrow T) -\u003e R) -\u003e Result\u003cR,DynProjectionFailure\u003e",
                                    "kind":  "DIRECT_CONCRETE_BORROW",
                                    "requires_registry":  false,
                                    "requires_static_concrete_target":  true,
                                    "escape_suspend_actor_cross_count":  0
                                },
                                {
                                    "id":  "DOWNCAST_OWNED",
                                    "signature":  "downcastOwned\u003cT\u003e(move value: Dyn) -\u003e OwnedDowncast\u003cT,Dyn\u003e",
                                    "kind":  "OWNER_PRESERVING_RESULT",
                                    "success":  "exactly one T owner",
                                    "mismatch":  "exact original Dyn owner",
                                    "both_or_zero_owner_count":  0
                                },
                                {
                                    "id":  "PROJECT_FACET_BORROW",
                                    "signature":  "FacetRegistry\u003cK\u003e.projectBorrow\u003cA\u003e(goal: ProjectionGoal\u003cK,A,Borrow\u003e, value: borrow Dyn) -\u003e Result\u003cFacet\u003cborrow any K where A\u003e,FacetProjectionFailure\u003e",
                                    "kind":  "STATIC_TRAIT_REGISTRY_PROJECTION",
                                    "requires_registry":  true,
                                    "requires_static_projection_goal":  true,
                                    "runtime_trait_token_allowed":  false,
                                    "initial_modes":  [
                                                          "BORROW"
                                                      ]
                                }
                            ],
    "transaction_laws":  {
                             "prepared_to_commit":  {
                                                        "suspension_count":  0,
                                                        "cancellation_checkpoint_count":  0,
                                                        "reentry_count":  0
                                                    },
                             "success_owner_disposition_count":  1,
                             "failure_owner_disposition_count":  1,
                             "cleanup_token_balance":  0,
                             "owner_failure_channel":  "OWNER_BEARING_RESULT_NOT_ERRORSET"
                         }
}
```
<!-- POST_PR16_UNIT_END:SFD-N003 -->

<!-- POST_PR16_UNIT_BEGIN:SFD-N005 -->
```json
{
    "schema":  "deeplus.codex-design.static-first-dynamic-typed-identity-matrix.r1",
    "status":  "LOCAL_NONCANONICAL_NONACTIVATABLE",
    "authority_facing_kinds":  [
                                   "RuntimeTypeId",
                                   "ClassId",
                                   "ClassSlotId",
                                   "EnumId",
                                   "VariantId",
                                   "TraitId",
                                   "ConformanceId",
                                   "TraitWitnessId",
                                   "FacetTypeId",
                                   "FacetInstanceId",
                                   "ProviderId",
                                   "AbiTag"
                               ],
    "kind_count":  12,
    "same_kind_round_trip_count":  12,
    "unordered_cross_kind_pair_count":  66,
    "directed_cross_kind_rejection_count":  132,
    "unnamed_cross_kind_conversion_policy":  "REJECT",
    "noncanonical_alias_emission_count":  0,
    "unresolved_identity_reference_count":  0,
    "internal_typed_kinds":  [
                                 "DynInstanceId",
                                 "DynDescriptorId",
                                 "DynPackPlanId",
                                 "DynProjectionPlanId",
                                 "OwnerTokenId",
                                 "LoanId",
                                 "PlaceId",
                                 "CleanupPlanId",
                                 "CleanupTokenId",
                                 "FacetConstructionPlanId",
                                 "RegistryId",
                                 "RegistrySnapshotId",
                                 "RegistryLineageId",
                                 "RegistryEpoch",
                                 "AuthorityScopeId",
                                 "ResponsibilityProfileId",
                                 "ProviderLeaseId",
                                 "DropPlanId",
                                 "DescriptorSchemaVersion",
                                 "ArtifactIdentity"
                             ],
    "domain_separation":  {
                              "semantic_identity_vs_runtime_type":  "DISTINCT",
                              "semantic_identity_vs_serialization_tag":  "DISTINCT",
                              "semantic_identity_vs_runtime_discriminant":  "DISTINCT",
                              "semantic_identity_vs_layout_or_abi":  "DISTINCT",
                              "semantic_identity_vs_hash_or_digest":  "DISTINCT",
                              "git_commit_vs_artifact_sha256":  "DISTINCT_HASH_DOMAINS"
                          },
    "named_checked_mapping_examples":  [
                                           {
                                               "name":  "emitRuntimeType",
                                               "from":  "ClassId or EnumId plus runtime image",
                                               "to":  "Option\u003cRuntimeTypeId\u003e",
                                               "authority":  "target/runtime descriptor authority"
                                           },
                                           {
                                               "name":  "runtimeMatches",
                                               "from":  "RuntimeTypeId plus expected ClassId or EnumId",
                                               "to":  "Match or NoMatch",
                                               "authority":  "checked descriptor table"
                                           },
                                           {
                                               "name":  "ownerOf",
                                               "from":  "VariantId",
                                               "to":  "EnumId",
                                               "authority":  "canonical total owner relation"
                                           },
                                           {
                                               "name":  "traitOf",
                                               "from":  "ConformanceId",
                                               "to":  "TraitId",
                                               "authority":  "normalized ground conformance record"
                                           },
                                           {
                                               "name":  "conformanceOf",
                                               "from":  "TraitWitnessId",
                                               "to":  "ConformanceId",
                                               "authority":  "one admitted whole-type binding"
                                           },
                                           {
                                               "name":  "providerRoute",
                                               "from":  "ProviderId",
                                               "to":  "validated ConformanceId and TraitWitnessId",
                                               "authority":  "validated registry entry"
                                           },
                                           {
                                               "name":  "facetTypeOf",
                                               "from":  "FacetInstanceId",
                                               "to":  "FacetTypeId",
                                               "authority":  "runtime metadata authority"
                                           },
                                           {
                                               "name":  "payloadRuntimeType",
                                               "from":  "FacetInstanceId",
                                               "to":  "RuntimeTypeId",
                                               "authority":  "privileged redacted inspection"
                                           },
                                           {
                                               "name":  "abiLookup",
                                               "from":  "RuntimeTypeId plus target and ABI manifest",
                                               "to":  "Option\u003cAbiTag\u003e",
                                               "authority":  "target-specific ABI authority"
                                           }
                                       ],
    "cross_service_guard":  {
                                "input":  "OWNER_CLOSED_IMMUTABLE_INPUT_ONLY",
                                "owner_fact_generation_count":  0,
                                "owner_identity_generation_count":  0,
                                "witness_generation_count":  0,
                                "authority_generation_count":  0,
                                "upstream_feedback_edge_count":  0
                            }
}
```
<!-- POST_PR16_UNIT_END:SFD-N005 -->

<!-- POST_PR16_UNIT_BEGIN:SFD-N006 -->
```json
{
    "current_authority":  {
                              "borrow_facet_type":  "Facet\u003cborrow any Trait\u003e",
                              "borrow_facet_construction":  "facet[borrow value as Trait]",
                              "surface_change_count":  0,
                              "lowercase_via_change_count":  0,
                              "class_enumeration_trait_change_count":  0
                          },
    "facet_profiles":  [
                           {
                               "mode":  "BORROW",
                               "status":  "CURRENT_SURFACE_PRESERVED_PRODUCT_NOT_RUN",
                               "payload_relation":  "shared region-bounded view",
                               "cleanup_owner":  "source",
                               "escape_suspend_isolation_count":  0
                           },
                           {
                               "mode":  "INOUT",
                               "status":  "GUARDED_PREVIEW_NONACTIVATABLE",
                               "payload_relation":  "one exclusive PlaceId loan",
                               "overlapping_exclusive_view_count":  0,
                               "store_return_suspend_cancel_actor_cross_count":  0,
                               "cleanup_owner":  "source; exclusive token released exactly once"
                           },
                           {
                               "mode":  "OWNED",
                               "status":  "GUARDED_PREVIEW_NONACTIVATABLE",
                               "authorized_source_spelling":  null,
                               "failure_owner_operation":  "move",
                               "payload_relation":  "one moved owner",
                               "failure":  "exact owner returned or discharged exactly once"
                           }
                       ],
    "terminology":  {
                        "ordinary_facet_create":  "construct or project a distinct Facet value",
                        "ordinary_facet_end":  "drop or release the Facet",
                        "attach_detach_successor_term_count":  0,
                        "facet_store":  "DEFERRED_SEPARATE_RFC_AFTER_NECESSITY_PROOF"
                    }
}
```
<!-- POST_PR16_UNIT_END:SFD-N006 -->


<!-- IR-OWN-R8-TYPE-CONTRACT -->
## Canonical ownership decision judgment

The checker first chooses the surface owner from the fixed parse goal:
expression `borrow`, expression context-anchor `&`, or type-intersection `&`.
The choice is terminal and has zero fallback.  General `borrow` proves one
owner-bounded shared loan; a context anchor proves one of the exact
NumericArray or Measure context roles and introduces no ownership state.

The predicate input catalog keeps `RCTSDescriptorV5` as its default and has
exactly three overrides—`BorrowEscapeAdmitted`, `BoxOwnershipAdmitted`, and
`OwnershipModeAdmitted`—to `OwnershipPredicateInputR1`.  That descriptor is
the exact union of `RCTSDescriptorV5` and `OwnershipDecisionInputR1`.
OwnershipDecisionInputR1 is closed, fully typed, and evaluated without fixture
inheritance, runtime patch lookup, implicit allocation, source-order identity
selection, or legacy semantic side-channel reads.

Every ownership unit retains immutable `OwnerDef` provenance and exactly one
derived state binding: Unissued, one unique state-local holder, one
state-level conditional predecessor-alternative group, or Retired.  A join
first requires byte-identical global loan, cleanup-token, reservation, and
prior-conflict state.  A divergent admitted place tuple becomes the internal
`MaybeMoved` marker only under the closed join law; its first
ownership-sensitive use or required cleanup emits
`PLACE_STATE_JOIN_MISMATCH`.  Exact overlapping inout or borrow access emits
`INOUT_ALIAS_CONFLICT`.  Specific Box and BorrowEscape failures precede the
generic ownership-mode diagnostic.
