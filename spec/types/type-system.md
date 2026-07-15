# Deeplus Type System 0.1.2 — RCTS-V5 TS-R45 — R51f3 Current Canonical

This companion is a checker-oriented projection of the canonical specification. It does not override the specification or exact Grammar. Product checker support is `NOT_RUN`.

## 1. Judgment families

The checker owns well-formedness, expression typing, subtyping, conformance evidence, call-shape admission, ownership/place access, effect/error rows, construction, pattern coverage, and Deeplus MIR handoff judgments.

## 2. Normalization and identity

Aliases, option layers, closed unions/intersections, associated projections, rows, labels, ownership modes, effects, errors, measures, shapes, and witness identities normalize before comparison. Normalization is terminating and responsibility preserving.

## 3. Named rest, function-type residue, and unfold

Named-rest parameters use attached triple-star `***`: `options***: Record`. Function types and public API digests preserve the exact `Record***` named-rest residue. Call/materialization named unfold uses attached prefix `**record`. Parameter/type `**` and unfold-prefix `***` are rejected. The collector is unique, final, and exactly canonical structural `Record`; Map is not admissible.

## 4. Nominal and structural domains

Subclassing, Trait conformance, extension activation, containment/association, and dynamic/tooling views are separate. Concrete classes are final by default. Sealed exhaustiveness recursively covers the complete family. Conformance is not inherited merely from nominal subclassing.

## 5. Generics and function types

Current parameter kinds are type, StaticInt, EffectRow, and ErrorSet. Generic constructors are invariant by default. Function compatibility preserves value/context/witness/rest channels, ownership, callable profile, effect/error rows, isolation, and return type. Return type and source order are not overload tie-breakers.

## 6. Union, intersection, Option, Result, and Facet

Union injection is unique after normalization. Contract intersections require every constituent obligation. Option and Result have explicit alternatives. Borrow Facet is current; owned/inout Facet packages remain Preview-design.

## 7. Ownership, effects, and cleanup

Move, borrow, inout, resource, isolation, effect, error, defect, cancellation, and cleanup obligations remain explicit. Borrow escape and inout aliasing are rejected. Cleanup is deterministic across normal return, failure, and cancellation.

## 8. Patterns, clauses, and laws

Pattern-control binding is immutable and transactional: the initializer is evaluated once, failure commits no binding or partial move, `while let` failure completes the loop, and `for let` failure skips the candidate. Pattern coverage is closed over enum, union, Option, Result, sealed families, and loop outcome. Declarative clauses use the finite partition algorithm. Law bodies admit only pure predicate assertions.

## 9. NumericArray, bitfield, and measures

NumericArray typing preserves element, shape, rank, orientation, and coordinate domain. Bitfield uses unsigned strict layout and finite flags universe. Exact-ratio units are core; calendar units require the stdlib/provider profile.

## 10. RCTS-V5 and MIR handoff

RCTS-V5 descriptors are closed discriminated inputs to design predicates. Static validation is E2 evidence only. Dyn-RCTS is nonactivatable. Every admitted surface lowers to Deeplus MIR with call shape, labels, ownership, effects/errors, cleanup, evidence, and evaluation order preserved.

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

Concrete classes are final unless declared open. Sealed classes close direct subclass declarations to the declared family scope; exhaustiveness recursively includes current descendants and rejects foreign direct children. Class dispatch markers lower to `ClassDispatchKind`; Trait witness markers lower to `TraitWitnessKind`. Associated requirements have their own item identities and do not acquire method markers.

Conformance selection must produce a unique `WitnessId`. Extension-member selection must produce a unique `ExtensionMemberId` and activation origin. Source order is never coherence evidence. Dynamic Trait state and first-class/local Witness values remain nonactivatable until their scope, escape, coherence, cleanup, and ABI laws are closed.

## 14. Rows, labels, Records, and schema materialization

A structural Record type carries an ordered canonical label row for identity/digest purposes while source construction preserves declared evaluation order. Label equality is static identifier equality, not runtime string equality. Row combination requires provable disjointness or an explicit overriding law owned by the operation.

Typed labeled materialization checks the target schema/Record row, field defaults, computed-field restrictions, duplicate labels, and source evaluation sequence. Schema unfolding does not weaken required fields and does not treat a runtime Map as a schema. Public API digests retain labels and construction responsibility where observable.

## 15. Ownership and place-state transitions

Each place has a state sufficient to reject use-after-move, overlapping inout access, mutable/shared alias violations, and borrow escape. A move consumes the source place unless the normalized type is reusable. A shared borrow prevents conflicting mutation for its admitted region. An inout borrow is exclusive and cannot be duplicated. Resource cleanup responsibility follows the owned value across moves.

Closure capture, async suspension, actor isolation, Facet packaging, defer registration, and return are escape boundaries. The checker must prove every captured borrow outlives its use and every resource has exactly one cleanup path. Borrow Facet packaging is current because it cannot outlive its source region; owned and inout Facet packaging remain Preview-design.

## 16. Effects, errors, cancellation, and callable profiles

Effect rows and error sets are normalized finite rows. `#pure` admits no observable effect or hidden authority. `#guard` is a terminating pure predicate profile. A callable value's type includes its effect row, error set, ownership/capture responsibility, suspension capability, isolation, and relevant context/witness channels.

Errors, defects, and cancellation are distinct control outcomes. Propagation operators consume only their declared family. Cleanup executes under a deterministic budget before the outcome escapes. Async suspension preserves live-place and cleanup obligations, and cancellation cannot silently bypass a registered cleanup. Callable compatibility is contravariant/covariant only where the declared responsibility profile permits; default inference remains invariant and conservative.

## 17. Pattern partition and exhaustiveness

Pattern checking first normalizes the subject domain, then constructs disjoint partitions for enum cases, union alternatives, Option, Result, sealed families, tuple/Record shapes, and loop outcomes. A guard refines only the already admitted structural partition. Dot-case shorthand is not current; enum cases use `::case` or `Type::case`.

Exhaustiveness succeeds only when the finite current partition is covered. Redundant or unreachable arms are diagnosed deterministically. An unknown future child is not assumed impossible unless the sealed-family authority proves closure. Clause functions and declarative clauses reuse the same partition engine but preserve their own input-supply and return-totality rules.

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

`if let`, `while let`, and `for let` use one transactional pattern-commit judgment. The checker evaluates the subject once, tests the refutable pattern, validates ownership/move effects, and commits all immutable bindings atomically. Failed `for let` matching skips the current element; it is not an error or loop failure.

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
