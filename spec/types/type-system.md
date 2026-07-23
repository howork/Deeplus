# Deeplus Type System 0.1.2 — RCTS-V5 TS-R45 — R51f3 Current Canonical

This companion is a checker-oriented projection of the canonical specification. It does not override the specification or exact Grammar. Product checker support is `NOT_RUN`.

## 1. Judgment families

The checker owns well-formedness, expression typing, subtyping, conformance evidence, call-shape admission, ownership/place access, effect/error rows, construction, pattern coverage, and Deeplus MIR handoff judgments.

## 2. Normalization and identity

Aliases, option layers, closed unions/intersections, associated projections, rows, labels, ownership modes, effects, errors, cancellation, measures, shapes, and witness identities normalize before comparison. Normalization is terminating, performs an occurs check, and preserves every responsibility-bearing distinction. Inference is bidirectional and local: it never invents an implicit generic, anonymous union, hidden authority, cancellation conversion, or open runtime type test.

A semantic value identity is independent from storage, serialization, runtime discriminant, ABI, and backend layout identity. `Int` normalizes to the signed 64-bit mathematical domain. `IntN`, `UIntN`, `ISize`, and `USize` are separate domains; contextual adaptation of a signless unsuffixed integer succeeds only for one exact representable `IntN` or `UIntN` target. A sign remains an AST prefix operator. With an independently fixed exact `Int`, `IntN`, or `UIntN` target, the checker may additionally recognize only `PrefixExpr(-, UnsuffixedIntegerLiteral)`, consume the validated magnitude fact, compute `-magnitude`, and test that signed candidate against the exact target domain. This adapter neither folds any other expression nor inserts widening/narrowing; an unrepresentable candidate is rejected by the enclosing owner's exact range diagnostic. `ISize`/`USize` require an exact suffix or explicit checked conversion. An unsuffixed floating literal remains `Float64`, and `Float32` requires `f32`. No operator judgment inserts hidden widening, narrowing, mixed signedness, or mixed-width conversion. `Float32` and `Float64` preserve their separate IEEE-754 binary domains; NaN is unordered and cannot establish implicit `Ord` or `Keyable` evidence.

## 3. Named rest, function-type residue, and unfold

Named-rest parameters use attached triple-star `***`: `options***: Record`. Function types and public API digests preserve the exact `Record***` named-rest residue. Call/materialization named unfold uses attached prefix `**record`. Parameter/type `**` and unfold-prefix `***` are rejected. The collector is unique, final, and exactly canonical structural `Record`; Map is not admissible.

## 4. Nominal and structural domains

Subclassing, Trait conformance, extension activation, containment/association, and dynamic/tooling views are separate. Concrete classes are final by default. Sealed exhaustiveness recursively covers the complete family. Conformance is not inherited merely from nominal subclassing.

## 5. Generics and function types

Current parameter kinds are type, StaticInt, EffectRow, and ErrorSet; rows and labels are checker identities, not further user generic kinds. Generic constructors are invariant by default. Function compatibility preserves value/context/witness/rest channels, ownership, callable profile, effect/error rows, cancellation, suspension, isolation, capture, and return type. Return type and source order are not overload tie-breakers. Ordinary callable parameters contain identifiers, modes, labels, and types rather than refutable Patterns; decomposition occurs in the body or an exhaustive declarative clause family.

## 6. Union, intersection, Option, Result, and Facet

Union injection is unique after normalization. Contract intersections require every constituent obligation. Option and Result have explicit alternatives. Every Result use-site spells its error channel `Result<T, error E>`; the generic declaration may bind `E: ErrorSet` without repeating the role marker. Borrow Facet is current; owned/inout Facet packages remain Preview-design.

The accepted nonactivatable Enum subset design adds no open subtyping search. A
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
`VariantId`, storage, or alias-local Trait witness. The surface remains
`PREVIEW_DESIGN`/nonactivatable.

Absence is an explicit `Option` alternative. The recovery spelling `null` has no typing judgment, does not infer `Option<T>`, and produces `NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE`; only `::none` in an expected `Option` context or explicit `Option<T>::none` constructs the absent alternative.

## 7. Ownership, effects, and cleanup

Move, borrow, inout, resource, isolation, suspension, effect, error, defect, cancellation, and cleanup obligations remain explicit. Cancellation is not an ErrorSet member and suspension is not hidden in an EffectRow. Borrow escape and inout aliasing are rejected. Cleanup is deterministic across normal return, failure, and cancellation.

## 8. Patterns, clauses, and laws

Every Pattern owner uses one normalized Pattern AST plus an explicit context policy. Plain `let`/`var`, bare `for`, and ordinary parameters require irrefutability; guarded `let`, `if let`, `while let`, `for let`, and `match` admit refutable patterns under their own failure disposition. The subject is evaluated once, structural testing is nonconsuming, probe binders are nonowning, the optional guard is terminating/pure/Bool, and final moves/borrows/bindings commit atomically only after success. Failure commits no binding, partial move, irreversible borrow, escape, suspension, or authority. `while let` failure completes the loop and `for let` failure skips the candidate. Pattern coverage is closed over enum, union, Option, Result, Record required-label subsets, exact-or-final-ignored-tail List shapes, and loop outcome. Sealed-Class closure does not create constructor patterns. Tuple patterns, scalar-interval patterns, and Record rest patterns are not current. Declarative clauses use the finite partition algorithm. Law bodies admit only pure predicate assertions.

## 9. NumericArray, bitfield, and measures

NumericArray typing preserves element, shape, rank, orientation, and typed coordinate domain. Each built-in default source-visible axis is exactly `1..dimension`, but it is not an ordinary Sequence witness. A full rank-matching coordinate list selects one element; coordinate type/count mismatch is static, and a dynamic coordinate outside the declared axis raises `IndexError::outOfLogicalDomain`. A NumericArray slice produces an owner-bounded `ReadonlyView` that preserves source coordinates and provenance. Bitfield uses unsigned strict layout and finite flags universe. Exact-ratio units are core; calendar units require the stdlib/provider profile.

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
4. bind the optional repeated positional channel `T...`;
5. prove and expand each named unfold `**record` from a statically known Record label row;
6. bind the optional final named-rest channel `Record***`;
7. reject missing, duplicate, overlapping, indeterminate, or extra labels;
8. check ownership, context, witness, effects, errors, isolation, and return compatibility;
9. choose the unique most-specific candidate, preferring fixed arity, then repeated positional, then named rest;
10. emit a normalized CallShape for Deeplus MIR.

The source parameter `options***: Record` and the function-type item `Record***` denote the same named-rest residue. The body binding may be a Record value, but its public type identity remains a call channel. `**record` is an argument-supply operation, not a parameter and not a type suffix. A Map never satisfies the static label-row proof.

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
preview-executable, and preview-script roots. Omission is checker recovery
only: it emits `TYPE_DECL_VISIBILITY_REQUIRED` and produces zero admitted HIR
type nodes, type identities, and API-digest entries.

For every other top-level owner whose Grammar production carries
`TopLevelVisibility?`, omission normalizes to `private`; this default never
applies to the nine type-producing owners. After that normalization, wider API
residue cannot mention a narrower identity, `common` residue cannot be
externally exported or re-exported, and `public` residue enters external API
only through a separately admitted export or module interface.

Conformance selection must produce a unique `WitnessId`. Extension-member selection must produce a unique `ExtensionMemberId` and activation origin. Source order is never coherence evidence. Dynamic Trait state and first-class/local Witness values remain nonactivatable until their scope, escape, coherence, cleanup, and ABI laws are closed.

Operator glyph selection is not a conformance goal in the current profile. The closed operator table uses `INTRINSIC_ONLY` dispatch over built-in admitted operand domains. A Trait method may expose equivalent named behavior, but conformance, extension, witness, provider, or source order cannot add an operator candidate. Arbitrary custom operators and fixed-operator conformance overloading remain nonactivatable, and `TCC-P1-002..008` remain OPEN.

## 14. Rows, labels, Records, and schema materialization

A structural Record type carries an ordered canonical label row for identity/digest purposes while source construction preserves declared evaluation order. Label equality is static identifier equality, not runtime string equality. Row combination requires provable disjointness or an explicit overriding law owned by the operation.

Typed labeled materialization checks the target schema/Record row, field defaults, computed-field restrictions, duplicate labels, and source evaluation sequence. Schema unfolding does not weaken required fields and does not treat a runtime Map as a schema. Public API digests retain labels and construction responsibility where observable.

## 15. Ownership and place-state transitions

Each place has a state sufficient to reject use-after-move, overlapping inout access, mutable/shared alias violations, and borrow escape. A move consumes the source place unless the normalized type is reusable. A shared borrow prevents conflicting mutation for its admitted region. An inout borrow is exclusive and cannot be duplicated. Resource cleanup responsibility follows the owned value across moves.

Closure capture, async suspension, actor isolation, Facet packaging, defer registration, and return are escape boundaries. The checker must prove every captured borrow outlives its use and every resource has exactly one cleanup path. Borrow Facet packaging is current because it cannot outlive its source region; owned and inout Facet packaging remain Preview-design.

`SharedCell<T>` admits only normalized Plain payload and exposes sequentially consistent `withValue` scoped observation plus `replace` owner exchange. The borrow cannot escape or suspend, and `replace` commits one new owner while returning the old owner; Plain supplies neither raw layout nor lock-free representation. `SharedMutex<T>` admits the no-lifecycle-payload minimum profile and grants one receiver-bound, non-reentrant, non-suspending scoped inout place to `withLock`. Unlock is an infallible exactly-once cleanup on every terminal path and establishes the mutex handoff edge to the next successful lock. No type rule infers weaker ordering, poisoning, fairness, lock ordering, actor transferability, or hidden cleanup.

Actor message typing has one closed admission family. An actor with no `MailboxClause` has profile `logical_unbounded_v1`; a positive static `#mailbox(capacity: N)` has profile `bounded_reject_v1`. A one-way send checks as `Result<Unit, error ActorMessageError>`. A request whose declared reply type is `T` checks immediately as `Result<Task<T>, error ActorMessageError>`; `await` applies only after pattern-matching or otherwise extracting the `Task<T>`. Only a successfully admitted actor-request Task value carries a non-forgeable `TaskResponsibility` descriptor in typed HIR, module API digest, and MIR; an ordinary async Task has no actor transport descriptor. The actor-request descriptor records the normalized result type, handler ErrorSet, cancellation axis, isolation owner, correlation identity, and terminal transport failure. Module API identity stores the static `correlation_id = per_value_non_forgeable` policy marker, while each committed request keeps its concrete correlation identity only in value-level typed HIR/MIR. Awaiting a handler declared `throws E` therefore exposes exactly `E | ActorMessageError::receiverClosedBeforeReply` without adding a visible second Task type parameter. The exact admission error cases are `mailboxFull`, `receiverClosedBeforeAdmission`, and `receiverClosedBeforeReply`. The first two are precommit admission results. The third is a declared terminal failure axis of an already admitted request task and does not retroactively change the successful admission Result.

`AsyncSequence<T, E: ErrorSet>` binds its source failure set instead of leaving a free terminal type. Its `next` operation throws `E`, while cancellation remains a distinct control outcome. For `AsyncCollector::list<T, U, ES, ET>`, the source is `AsyncSequence<T, ES>`, the named asynchronous transform throws `ET`, and the result throws exactly `normalize(ES | ET)`. Neither source nor transform errors may be erased or converted to cancellation.

Before enqueue commit, all moved argument places remain live at the sender and a rejection allocates neither `MessageId` ownership nor `channel_sequence`. A successful commit consumes each moved sender place exactly once, installs exactly one actor-owned payload, and allocates the next strictly increasing sequence for the normalized `(SenderId, ReceiverActorId, MailboxProfileId)` key. Cancellation before commit aborts without transfer; cancellation after commit cannot restore the sender place or retract the message. Cancellation is a control axis and never a member of `ActorMessageError`.

An assignment target is checked and evaluated as one place. Compound assignment reads that place once, checks one exact intrinsic operand domain, evaluates the right operand once, and commits at most one result. A precommit `ArithmeticDefect`, `IndexError`, or other failure leaves the prior owner and value unchanged. Assignment expressions have result type `Unit`. Every admitted slice result is a `ReadonlyView`, never an assignable place; its borrow cannot escape its owner, cross isolation, hide a copy, or be implicitly rebased.

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

Errors, defects, and cancellation are distinct control outcomes. Propagation operators consume only their declared family. Cleanup executes under a deterministic budget before the outcome escapes. Async suspension preserves live-place and cleanup obligations, and cancellation cannot silently bypass a registered cleanup. Callable compatibility is contravariant/covariant only where the declared responsibility profile permits; default inference remains invariant and conservative.

Checked integer overflow and integer division or remainder by zero produce deterministic `ArithmeticDefect`, not a recoverable ErrorSet member. Integer quotient truncates toward zero; remainder obeys `a == trunc(a / b) * b + r`, with `r == 0` or the dividend sign and `|r| < |b|`. Signed `MIN / -1` and `MIN % -1` are overflow. If the checker proves failure statically it rejects the expression; otherwise the Defect edge occurs before an enclosing assignment commit. Floating remainder and floating glyph power are not current, and wrapping, saturating, or alternate remainder behavior is available only through explicitly named APIs. Integer `^` requires one exact integer domain, a statically proven nonnegative exponent in that domain, and a checked same-domain result; negative or proof-unknown exponents reject with `NUMERIC_OPERATOR_CORE_REQUIRED`. Measure power and linear-algebra operators use their separate intrinsic judgments.

## 17. Pattern partition and exhaustiveness

Pattern checking first normalizes the subject domain, then constructs disjoint partitions for enum cases, union alternatives, Option, Result, Record required-label subsets, exact-or-final-ignored-tail List shapes, and loop outcomes. Sealed-Class closure informs nominal analysis but has no current constructor-pattern carrier. Tuple patterns, scalar-interval patterns, captured/middle/multiple List rests, and Record rest patterns are not current. A guard refines only the already admitted structural partition and may read probe binders without moving, escaping, suspending, mutating through, or acquiring authority from them. Dot-case shorthand is not current; enum cases use `::case` or `Type::case`.

Exhaustiveness succeeds only when the finite current pattern partition is
covered. Redundant or unreachable arms are diagnosed deterministically. A
sealed Class may prove nominal-family closure for other checker judgments, but
that proof is not a substitute for absent constructor-pattern syntax. Clause
functions and declarative clauses reuse the same partition engine but preserve
their own input-supply and return-totality rules.

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

`def#guard` is an exact Bool, pure, total, terminating, nonsuspending, nonconsuming, authority-free callable profile. Because current source and API metadata contain no refinement-summary owner, calling one is opaque to `Phi`; only an inline admitted R0 guard may contribute a refinement fact. A guarded arm never subtracts from exhaustiveness coverage.

## 18. MIR responsibility projection and evidence boundary

The checker hands MIR a normalized descriptor containing the selected static identities, call channels, labels, type arguments, ownership transitions, cleanup regions, effects/errors, failure edges, suspension/isolation, construction plan, and source provenance. MIR lowering must not repeat open-ended name, witness, extension, or provider lookup.

The canonical architecture is Rust frontend/checker, Deeplus MIR, Rust xVM bytecode/interpreter, LLVM AOT, and later LLVM ORC JIT. This file defines the design handoff only. Until artifact-bound target receipts exist, production parser, integrated checker, MIR lowering, xVM, LLVM, formatter/LSP, and independent conformance remain `NOT_RUN` regardless of static schema or verifier success.


## 19. Rightward local-binding normalization judgment

The frontend proves `Γ ⊢ e -> $x[: T] ⇝ let x[: T] = e` and `Γ ⊢ e -> $$x[: T] ⇝ var x[: T] = e` before semantic checking. The target is a fresh identifier and is absent from `Γ` while `e` is checked. The checker evaluates one initializer descriptor, checks the optional annotation, ownership, effects, errors, borrow regions and cleanup, then commits exactly one ordinary local. Failure commits no local. The same ordinary local-binding judgment is used for direct and normalized surfaces.

There is no `FlowBinding` semantic type or responsibility. Coroutine response binding retains the preceding suspension/resume event but delegates the resumed value to the same ordinary binding judgment.

## 20. Raw String and official tooling boundaries

`raw"..."` has type `String`; body scalars are not escape-decoded and `$` has no interpolation role. The only semantic payload is the exact scalar sequence, lowered to `ConstString`.

R2 proof certificates and provider derive-via sidecars are tooling evidence, never types, witnesses, authorities or MIR values. A certificate is accepted only after deterministic checker validation or reduction to an R0/R1 obligation. Generated derive source is checked from scanner through MIR like handwritten source.

## 21. Dynamic-unit profile judgment

Dynamic conversion admission is the conjunction `ProfileActive ∧ ProviderBound ∧ PolicyComplete ∧ ProviderSupportsConversion`. No `#preview` predicate participates. Policy completeness includes observation timestamp, rounding, failure/effect rows, cache identity and replay token.


## 22. Sugar-equivalence and quarantine judgments

Field punning elaborates `label` to `label: label` before construction-row checking, without inserting clone, move, authority or lookup. Grouped forwarding elaborates to a finite ordered list of ordinary forwarding declarations and rejects duplicate or colliding names. Scoped import/use grouping pushes exactly one compile-time lexical frame for its `in` block and pops it on every exit. Enum comma lists, multiline indentation, and the single-guard law are parser/scanner obligations whose normalized HIR is identical to their unsugared forms.

`if let`, `while let`, and `for let` use one transactional pattern-commit judgment: evaluate once, acquire, compile a nonconsuming TestPlan, test, expose probe binders, evaluate zero or one guard, commit atomically, expose final binders, execute, and exit/join. Failed `for let` matching or a false guard skips the current element; it is not an error or loop failure.

The quarantine-scope predicate is design-seed-only and nonemitting. Even its minimum sound profile requires a typed immutable export and rejects pointer, authority, borrow, resource, closure, task, actor, suspension and outer-mutation escape. No source profile activates it and no product support is claimed.


## 23. Removed-surface typing laws

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

`List<T>`, `String`, and `Bytes` have the built-in domain `1..length` and storage offset `index - 1`; their element results are respectively `T`, `Char`, and `UInt8`. Every `ReadonlyView<T>` preserves its source owner's declared logical domain, mapping, and provenance and returns borrowed `T`; ordinary one-based sources remain one-based, while bounded or sliced sources retain their coordinates. These carriers accept exactly one bounded range slice. An explicitly bounded List preserves its declared inclusive `L..U` domain. `Map<K,V>` requires an exact `K` and returns `V` or raises `IndexError::keyNotFound`. Tuple `.n` and Record labels are static projections, not bracket indexing. Merely conforming to `Sequence`, `Indexable`, or `LogicalIndexDomain` does not create any bracket judgment.

The current bounded range forms are inclusive `i..j` and explicit exclusive end `i..<j`; `^`/`$` are first/last bound anchors. NumericArray additionally admits exact-rank semicolon-separated axes, where a scalar coordinate or full-axis `*` may appear. Empty `[]`, omitted range bounds, descending/step forms, and implicit negative-from-end rewriting have no typing rule. Half-open input retains a warning. Successful slicing retains the selected logical coordinates and owner region; explicit named rebase/copy is required for new coordinates or independent ownership.

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
ownership, alias, `ShareSafe`, `Transferable`, and witness obligations remain
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
                                    "kind":  "OWNER_PRESERVING_RECOVERY",
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
                               "recovery_operation":  "move",
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
