# Deeplus Prelude 0.1.2 — R51f3 Current Canonical

Prelude supplies canonical language-facing identities without turning them into hard keywords. Product implementation is `NOT_RUN`. The machine-readable signature authority is `library/prelude/signatures`; this guide explains its domains and does not duplicate all 55 rows.

## 1. Core domains

The catalog covers canonical language-facing numeric constants and identities, `Bool`, Unicode-scalar `Char`, immutable `String`, `Bytes`, Option, Result, `ArithmeticDefect`, `IndexError`, sequence/set/map families, structural `Record`, iterator protocols, named behavior protocols, callable profiles, measures, construction and evidence facades. Primitive semantic types remain language identities even when they do not require a separate catalog row. `array` remains an ordinary identifier.

## 2. Call channels

Public signatures preserve `T...` repeated positional residue and `Record***` named-rest residue. A body may expose a sequence-like or Record binding, but module API identity retains the channel. Named unfold is `**record`; Map is not a static named-argument source.

## 3. Option, Result and cleanup

Option has explicit `::some` and `::none` alternatives. `?:` is lazy in its fallback. Result and errors are separate from Option absence. Every Result use site writes the error-channel role as `Result<T, error E>`; the generic declaration itself may bind `E: ErrorSet` without repeating that use-site role. Resource-facing Prelude contracts preserve move and exactly-once cleanup responsibility.

`ActorMessageError` is the closed current actor admission/reply failure family: `mailboxFull`, `receiverClosedBeforeAdmission`, and `receiverClosedBeforeReply`. One-way message expressions return `Result<Unit, error ActorMessageError>`. Request expressions immediately return `Result<Task<T>, error ActorMessageError>`; callers extract the task before `await`. Cancellation remains a distinct control outcome and is not an enum case.

## 4. Fixed operators and protocols

The operator vocabulary and precedence table are closed, and every current glyph dispatches as `INTRINSIC_ONLY`. Prelude Trait and protocol names expose named behavior only; conformance, extension, witness, provider, or source order cannot add or replace a glyph implementation. `Bitwise` and `Ord<T>` are named contract vocabulary, not punctuation hooks. Arbitrary custom operator declaration and fixed-operator conformance expansion remain `PREVIEW_DESIGN`/nonactivatable, and all `TCC-P1-002..008` remain OPEN.

## 4A. Current numeric and indexing boundary

`Int` has the signed 64-bit mathematical domain. Integer operators are checked and raise deterministic `ArithmeticDefect` on dynamic overflow or division or remainder by zero before assignment commit; named APIs own wrapping and saturating behavior. `Float32` and `Float64` follow IEEE-754 binary32/binary64 value behavior with round-to-nearest, ties-to-even; NaN is unordered, signed zero compares equal, and Float receives no implicit `Ord`/`Keyable` evidence. None of these laws selects storage, ABI, or backend layout.

`ArithmeticDefect` is the closed nonrecoverable intrinsic family `overflow | divisionByZero`; the latter covers both integer division and remainder by zero. It is neither an `ErrorSet` member nor an enum-as-error. `IndexError` is the closed recoverable family `outOfLogicalDomain | keyNotFound`. `List<T>`, `String`, and `Bytes` have built-in one-based domains. Every `ReadonlyView<T>` preserves its source owner's declared logical coordinates and provenance: views of those ordinary owners are therefore one-based, while views of bounded or sliced owners retain their source domain. String indexing returns `Char` and Bytes indexing returns `UInt8`. Map lookup requires the exact key type. NumericArray uses separate typed axes whose built-in default source coordinates are each `1..dimension`. `Indexable`, `Sequence`, and `LogicalIndexDomain` are checker/library descriptors and named behavior contracts; source conformance to them does not activate `[]`.

NumericArray slicing yields an owner-bounded `ReadonlyView` that preserves source coordinates and provenance. No Prelude operation silently rebases, copies, makes the view mutable, crosses isolation, or extends its owner lifetime. An independent value or rebased coordinate domain requires an explicit named operation.

## 5. Profile boundaries

Calendar and dynamic unit conversions are stdlib/provider profiles, not core syntax and not `#preview` features. R2 solver and provider derive-via are official tooling; neither changes Prelude type identity or injects evidence. UML remains an official tooling family only where its schema and fixture contract is current.

## 6. Navigation and evidence

Use the signature catalog for exact names, generic channels, parameter labels, return types and feature references. Use the TypeSystem for compatibility and responsibility judgments, Operational Semantics for MIR behavior, and the example corpus for accepted/rejected design-static surfaces. All runtime/provider results remain `NOT_RUN` until artifact-bound receipts exist.

The current async collection profile binds three Prelude identities without introducing syntax: `AsyncSequence<T, E: ErrorSet>`, `AsyncCollector`, and `CollectPolicy::sequential`. `AsyncSequence<T, E>` is a single-consumer source with one source-ordered async `next` channel and one terminal end/error/cancellation outcome; `E` is the source failure set and cancellation remains a distinct control outcome. `AsyncCollector::list<T, U, ES, ET>` requires checker evidence that the source is finite and exposes exactly `throws ES | ET`, the normalized union of the source and transform failure sets. The single policy means source-order result, fail-fast first failure, cancellation of pending work, a capacity-one buffer, no partial commit, and cleanup before return. Completion-order and dynamically bounded alternatives are not current defaults.


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

## 10. Human index of the 55 canonical Prelude entries

This generated review index mirrors the machine catalog without replacing it. `status` is design/profile maturity; every product-support cell remains `NOT_RUN`.

| Symbol | Kind | Status | Responsibility |
| --- | --- | --- | --- |
| `JsonValue` | boundary_value | `stable_design` | external JSON model distinct from Plain and Dyn |
| `WitnessId` | checker_identity | `stable_design` | explicit conformance evidence identity; never synthesized from extension presence |
| `FillRepeatAdmissibilityProfile` | checker_known_protocol | `stable_design` | Stable checker law for shaped fill/repeat/generator initializer admissibility. |
| `Indexable` | checker_known_protocol | `stable_design` | built-in owner indexing descriptor; conformance does not activate brackets |
| `ArithmeticDefect` | language_intrinsic_defect | `stable_design` | closed nonrecoverable checked-integer failure family: overflow or division/remainder by zero |
| `IndexError` | enum | `stable_design` | closed recoverable out-of-domain and missing-key indexing failure family |
| `MembershipProtocol` | checker_known_protocol | `stable_design` | Current Prelude design vocabulary; product support NOT_RUN. |
| `List<T>` | collection | `stable_design` | ordered owned collection with one-based built-in indexing |
| `Map<K,V>` | collection | `stable_design` | exact-key lookup; no public Copyable or key-as-member projection |
| `ImplementationId` | compiler_identity | `stable_design` | implementation symbol reusable without merging extension and witness identity |
| `Facet<Mode,Contract>` | compiler_intrinsic_type | `stable` | RCTS-V5 ownership-qualified existential carrier; borrow mode Stable, inout/move nonactivatable |
| `Box<T>` | core_type | `stable_design` | unique owning indirection whose canonical constructor is Box!(value), with exactly-once payload cleanup |
| `ByteView` | core_type | `stable_design` | contiguous byte-addressable readonly bytes acquired by borrowing Bytes::view; the result retains owner provenance and assumes neither text encoding nor String semantics |
| `Bytes` | core_type | `stable_design` | raw byte sequence with one-based UInt8 indexing; no implicit String conversion |
| `FrozenList<T>` | core_type | `stable_design` | declared immutable/shareable result of an exclusive freeze transition |
| `ListSnapshot<T>` | core_type | `stable_design` | independent point-in-time list value with declared copy/COW cost |
| `MutableList<T>` | core_type | `stable_design` | exclusive mutable list owner; snapshot borrows without invalidating the source, while freeze consumes the receiver and completes its ownership transition |
| `NumericArray<T, rank R>` | core_type | `stable_design` | ranked numeric value with typed one-based default axes and visible allocation/backend responsibility |
| `OwnedDowncast<Target,Source>` | core_type | `stable_design` | sum channel that preserves exactly one owner on both downcast outcomes |
| `ReadonlyView<T>` | core_type | `stable_design` | nonowning nonmutating owner-bounded coordinate-preserving view |
| `String` | core_type | `stable_design` | immutable Unicode scalar sequence with one-based Char indexing |
| `Task<T>` | core_type | `stable_design` | structured asynchronous task handle |
| `AsyncCollector` | stdlib_profile | `stable_design` | finite policy-visible async collection with no partial commit |
| `AsyncSequence<T, E>` | protocol | `stable_design` | asynchronous element source with a bound error set and visible cancellation, isolation and cleanup responsibilities |
| `ExitCode` | entry_result | `stable_design` | Launcher-facing result; ordinary calls do not map it to process termination. |
| `CollectPolicy` | enum | `stable_design` | exact sequential/source/fail-fast/cancel-pending/buffer-one collection policy |
| `Option<T>` | enum | `stable_design` | recoverable absence as value, not Error |
| `Result<T, error E>` | enum | `stable_design` | value-level error channel distinct from throws |
| `downcastOwned<Target,Source>` | function | `stable_design` | generic target is selected from the exact expected OwnedDowncast result type; no runtime type-token argument is accepted |
| `replace<T>` | function | `stable_design` | one-evaluation exclusive place transaction returning the old owner |
| `withBorrowed<T,R>` | function | `stable_design` | invocation-bounded borrowed callback helper |
| `ContextParameterRole` | function_signature_descriptor | `stable_design` | function parameter role preserved in signature identity under the Stable design explicit context parameter law |
| `Bitwise` | internal_or_stdlib_trait_seed | `stable_design` | named bitwise contract seed; current bitwise glyphs remain intrinsic-only |
| `ModuleSignature` | language_surface | `stable_design` | public API boundary surface; stable design; not separate compilation receipt |
| `Float32` | numeric_type_side_constants | `stable_design` | IEEE binary32 value behavior; non-finite values are type-side constants. |
| `Float64` | numeric_type_side_constants | `stable_design` | IEEE binary64 value behavior; NaN supplies no implicit ordering/key evidence. |
| `Actor` | protocol | `stable_design` | isolated mailbox execution root |
| `ActorMessageError` | enum | `stable_design` | closed actor admission/reply failure family; cancellation excluded |
| `Sequence<T>` | protocol | `stable_design` | named ordered-sequence contract; conformance alone does not activate brackets |
| `Char` | scalar | `stable_design` | exactly one Unicode scalar value; surrogates excluded |
| `Shared<T>` | shared_handle | `stable_design` | shared observation handle, not mutable alias permission |
| `SharedCell<T>` | synchronization | `stable_design` | sequentially consistent scoped observation and owner replacement for Plain payloads; no raw-layout or lock-free inference |
| `String::render<T>` | static_function | `stdlib` | single-evaluation nonescaping structured-value renderer |
| `Option<T>::unwrapOrElse` | stdlib_operation | `stable_design` | Named lazy equivalent of one-layer Option coalescing; fallback executes only for none and preserves conditional ownership/error/effect/cleanup. |
| `Measure<Rep, Dim>` | stdlib_profile | `stdlib_profile` | Measure conversion APIs are explicit and use unit witness carriers. |
| `UnitCatalog` | stdlib_profile | `stable_design` | Stable design user unit catalog profile; product support NOT_RUN. Dynamic/provider conversion is outside this stable core. |
| `Grapheme` | stdlib_value_or_view | `stable_design` | extended grapheme cluster produced by named segmentation API |
| `SharedMutex<T>` | synchronization | `stable_design` | receiver-bound non-reentrant scoped mutation; non-suspending access and exactly-once unlock precede the next successful lock |
| `ExtensionSetId` | tooling_schema | `stable_design` | semantic identity seed for named extension set D-MAD; not current source |
| `BitfieldCodec` | trait | `stdlib` | explicit endian codec |
| `BitfieldRaw<Backing>` | trait | `stdlib` | checked raw carrier contract |
| `LogicalIndexDomain<Index>` | trait | `stable_design` | named logical-domain contract; built-in brackets remain closed-owner syntax |
| `Ord<T>` | trait | `stable_design` | nominal named ordering evidence, never an operator-glyph hook |
| `Display` | trait/profile | `stable_design` | string interpolation rendering/display; not serialization or redaction authority source-level display responsibility contract seed |

`Ord<T>.compare(lhs, rhs)` borrows both operands, is deterministic, pure,
synchronous, non-consuming, authority-free, `throws Never`, and returns an `Int`
whose sign alone is contractually meaningful and stable. It must be total for every admitted ground `T`;
zero is the ground type's equality relation, and transitivity, antisymmetry and
trichotomy are required. This named evidence never activates `<`, `<=`, `>`, or
`>=`; the design-only example `EX-R48H-002` illustrates witness-slot markers and
does not replace this generic Prelude signature.

`Display.display()` borrows its receiver, is deterministic, synchronous,
non-consuming, authority-free, `throws Never`, and performs no hidden locale,
provider, serialization, parsing, or redaction operation. String interpolation
must select every nested `Display` witness before evaluation. The accepted Enum
case-mapping proposal may synthesize one whole-Enum witness only after its
nonactivatable feature gates close; it creates no case- or alias-local witness.
| `Iterator` | trait_profile | `stable_design` | for-loop protocol seed associated Item requirement and next selector seed synchronous iteration protocol core; stable design in R48; product support NOT_RUN Current Prelude design vocabulary; product support NOT_RUN. |

## 11. Nonactivatable collection ownership design note

The accepted literal-shaped collection proposal is a design projection and
adds no current Prelude entry or signature. Immutable-first naming is the
successor rule, but current `FrozenList<T>` and `ListSnapshot<T>` remain
distinct identities and are not aliases of `List<T>`. Freeze is shallow and
failure-atomic and supplies no implicit shareability proof; snapshot is an
independent point-in-time value; any collection view remains owner-bounded and
coordinate/provenance preserving.

`MutableMap`, `MutableSet`, `StringBuilder`, and `ByteBuffer` are reserved
successor names only. `MutableSequence`, `MutableTuple`, general
`MutableRecord`, and `MutableString` remain absent or deferred, and
`Sequence<T>` remains traversal-only. This note is `PREVIEW_DESIGN`,
`nonactivatable`, and closes no P1 or product lane.
