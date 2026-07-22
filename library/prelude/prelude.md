# Deeplus Prelude 0.1.2 — R51f3 Current Canonical

Prelude supplies canonical language-facing identities without turning them into hard keywords. Product implementation is `NOT_RUN`. The machine-readable signature authority is `library/prelude/signatures`; this guide explains its domains and does not duplicate all 52 rows.

## 1. Core domains

The catalog covers primitive numeric types, `Bool`, Unicode-scalar `Char`, immutable `String`, `Bytes`, Option, Result, sequence/set/map families, structural `Record`, iterator protocols, fixed operator protocols, callable profiles, measures, construction and evidence facades. `array` remains an ordinary identifier.

## 2. Call channels

Public signatures preserve `T...` repeated positional residue and `Record***` named-rest residue. A body may expose a sequence-like or Record binding, but module API identity retains the channel. Named unfold is `**record`; Map is not a static named-argument source.

## 3. Option, Result and cleanup

Option has explicit `::some` and `::none` alternatives. `?:` is lazy in its fallback. Result and errors are separate from Option absence. Resource-facing Prelude contracts preserve move and exactly-once cleanup responsibility.

## 4. Fixed operators and protocols

The operator vocabulary is closed. Prelude protocol names provide fixed semantic ownership; arbitrary custom operator declaration and fixed operator conformance expansion remain nonactivatable until their coherence and MIR obligations close.

## 5. Profile boundaries

Calendar and dynamic unit conversions are stdlib/provider profiles, not core syntax and not `#preview` features. R2 solver and provider derive-via are official tooling; neither changes Prelude type identity or injects evidence. UML remains an official tooling family only where its schema and fixture contract is current.

## 6. Navigation and evidence

Use the signature catalog for exact names, generic channels, parameter labels, return types and feature references. Use the TypeSystem for compatibility and responsibility judgments, Operational Semantics for MIR behavior, and the example corpus for accepted/rejected design-static surfaces. All runtime/provider results remain `NOT_RUN` until artifact-bound receipts exist.


## 7. Surface neutrality

Field puns, grouped forwarding, scoped activation grouping, enum comma lists, multiline String dedent, single guards, and pattern-control syntax add no Prelude identity. Their normalized types and callable residues are those of existing Record/schema, member, import/use, enum, String, Bool and pattern domains. The quarantine proposal adds no Prelude type or authority while nonactivatable.


## 8. Explicit library boundary

Map exposes ordinary index and named API contracts; Prelude supplies no key-as-member projection. Pattern-matching libraries may define `Regex` or other pattern types, but construction consumes explicit `String`/`Bytes` arguments and is not syntax. Prelude supplies no increment/decrement operator protocol and no tail-recursion callable profile. List and anonymous Union remain separate identities: only an explicit expected `List<A | B>` admits mixed elements.


## 9. R51f3 bounded profiles

The pattern-engine profile is an explicit library boundary, not literal syntax:

```deeplus
public type PatternCompileError
public type PatternEngine
public type PatternBudget

public def Pattern::compile(
    source: String,
    engine: PatternEngine,
    budget: PatternBudget,
) -> Result<Pattern, error PatternCompileError>
```

An implementation records engine/version, flags, Unicode mode and budget in the cache and execution identity. No-match is an ordinary match result; it is not a compile failure. Tooling-only xVM agent, tail-call analysis and UML provider contracts add no Prelude callable.

## 10. Human index of the 52 canonical Prelude entries

This generated review index mirrors the machine catalog without replacing it. `status` is design/profile maturity; every product-support cell remains `NOT_RUN`.

| Symbol | Kind | Status | Responsibility |
| --- | --- | --- | --- |
| `JsonValue` | boundary_value | `stable_design` | external JSON model distinct from Plain and Dyn |
| `WitnessId` | checker_identity | `stable_design` | explicit conformance evidence identity; never synthesized from extension presence |
| `FillRepeatAdmissibilityProfile` | checker_known_protocol | `stable_design` | Stable checker law for shaped fill/repeat/generator initializer admissibility. |
| `Indexable` | checker_known_protocol | `stable_design` | Stable basic indexing law; advanced slicing/custom indexing are separate. |
| `MembershipProtocol` | checker_known_protocol | `stable_design` | Current Prelude design vocabulary; product support NOT_RUN. |
| `List<T>` | collection | `stable_design` | ordered owned collection |
| `Map<K,V>` | collection | `stable_design` | key admissibility without public Copyable |
| `ImplementationId` | compiler_identity | `stable_design` | implementation symbol reusable without merging extension and witness identity |
| `Facet<Mode,Contract>` | compiler_intrinsic_type | `stable` | RCTS-V5 ownership-qualified existential carrier; borrow mode Stable, inout/move nonactivatable |
| `Box<T>` | core_type | `stable_design` | unique owning indirection whose canonical constructor is Box!(value), with exactly-once payload cleanup |
| `ByteView` | core_type | `stable_design` | contiguous byte-addressable readonly bytes acquired by borrowing Bytes::view; the result retains owner provenance and assumes neither text encoding nor String semantics |
| `Bytes` | core_type | `stable_design` | raw byte sequence; no implicit String conversion |
| `FrozenList<T>` | core_type | `stable_design` | declared immutable/shareable result of an exclusive freeze transition |
| `ListSnapshot<T>` | core_type | `stable_design` | independent point-in-time list value with declared copy/COW cost |
| `MutableList<T>` | core_type | `stable_design` | exclusive mutable list owner; snapshot borrows without invalidating the source, while freeze consumes the receiver and completes its ownership transition |
| `NumericArray<T, rank R>` | core_type | `stable_design` | ranked numeric storage with visible allocation/backend responsibility |
| `OwnedDowncast<Target,Source>` | core_type | `stable_design` | sum channel that preserves exactly one owner on both downcast outcomes |
| `ReadonlyView<T>` | core_type | `stable_design` | nonowning nonmutating owner-bounded view |
| `String` | core_type | `stable_design` | immutable Unicode scalar sequence |
| `Task<T>` | core_type | `stable_design` | structured asynchronous task handle |
| `ExitCode` | entry_result | `stable_design` | Launcher-facing result; ordinary calls do not map it to process termination. |
| `CollectPolicy` | enum | `preview` | explicit async ordering and back-pressure policy |
| `Option<T>` | enum | `stable_design` | recoverable absence as value, not Error |
| `Result<T, error E>` | enum | `stable_design` | value-level error channel distinct from throws |
| `downcastOwned<Target,Source>` | function | `stable_design` | generic target is selected from the exact expected OwnedDowncast result type; no runtime type-token argument is accepted |
| `replace<T>` | function | `stable_design` | one-evaluation exclusive place transaction returning the old owner |
| `withBorrowed<T,R>` | function | `stable_design` | invocation-bounded borrowed callback helper |
| `ContextParameterRole` | function_signature_descriptor | `stable_design` | function parameter role preserved in signature identity under the Stable design explicit context parameter law |
| `Bitwise` | internal_or_stdlib_trait_seed | `stable_design` | bitwise operator admission uses checker-visible witness/admissibility |
| `ModuleSignature` | language_surface | `stable_design` | public API boundary surface; stable design; not separate compilation receipt |
| `Float32` | numeric_type_side_constants | `stable_design` | Non-finite Float32 values are type-side constants rather than lexical numeric literals. |
| `Float64` | numeric_type_side_constants | `stable_design` | Non-finite Float64 values are type-side constants rather than lexical numeric literals. |
| `Actor` | protocol | `stable_design` | isolated mailbox execution root |
| `Sequence<T>` | protocol | `stable_design` | ordered finite or lazy sequence contract with an exact associated Item binding |
| `Char` | scalar | `stable_design` | exactly one Unicode scalar value; surrogates excluded |
| `Shared<T>` | shared_handle | `stable_design` | shared observation handle, not mutable alias permission |
| `String::render<T>` | static_function | `stdlib` | single-evaluation nonescaping structured-value renderer |
| `Option<T>::unwrapOrElse` | stdlib_operation | `stable_design` | Named lazy equivalent of one-layer Option coalescing; fallback executes only for none and preserves conditional ownership/error/effect/cleanup. |
| `Measure<Rep, Dim>` | stdlib_profile | `stdlib_profile` | Measure conversion APIs are explicit and use unit witness carriers. |
| `UnitCatalog` | stdlib_profile | `stable_design` | Stable design user unit catalog profile; product support NOT_RUN. Dynamic/provider conversion is outside this stable core. |
| `Grapheme` | stdlib_value_or_view | `stable_design` | extended grapheme cluster produced by named segmentation API |
| `SharedMutex<T>` | synchronization | `stable_design` | mutation via scoped lock and effect propagation |
| `ExtensionSetId` | tooling_schema | `stable_design` | semantic identity seed for named extension set D-MAD; not current source |
| `BitfieldCodec` | trait | `stdlib` | explicit endian codec |
| `BitfieldRaw<Backing>` | trait | `stdlib` | checked raw carrier contract |
| `LogicalIndexDomain<Index>` | trait | `stable_design` | one-based logical-domain to storage-offset contract |
| `Ord<T>` | trait | `stable_design` | nominal ordering evidence for T |
| `Display` | trait/profile | `stable_design` | string interpolation rendering/display; not serialization or redaction authority source-level display responsibility contract seed |
| `Iterator` | trait_profile | `stable_design` | for-loop protocol seed associated Item requirement and next selector seed synchronous iteration protocol core; stable design in R48; product support NOT_RUN Current Prelude design vocabulary; product support NOT_RUN. |
