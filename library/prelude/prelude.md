# Deeplus Prelude 0.1.2 — R51f3 Current Canonical

Prelude supplies canonical language-facing identities without turning them into hard keywords. Product implementation is `NOT_RUN`. The machine-readable signature authority is `library/prelude/signatures`; this guide explains its domains and does not duplicate all 65 rows.

Revision: `r51f3-current-concur-role-coherence-r1`

## 1. Core domains

The catalog covers canonical language-facing numeric constants and identities, `Bool`, Unicode-scalar `Char`, immutable `String`, `Bytes`, Option, Result, `ArithmeticDefect`, `IndexError`, sequence/set/map families, structural `Record`, iterator protocols, named behavior protocols, callable profiles, measures, construction and evidence facades. Primitive semantic types remain language identities even when they do not require a separate catalog row. `array` remains an ordinary identifier.

## 2. Call channels

Public signatures preserve `T..` repeated positional residue and `NamedPack**`
named-rest residue. The body bindings are respectively finite, call-scoped,
nonescaping `PositionalPack<T>` and `NamedPack<rho>` values; neither channel is
erased to `Sequence<T>`, `Record`, or `Map`. Named unfold remains `**value` and
is admitted only after a static named-row proof. The normalized named row and
witness digest are part of module API identity.

## 3. Option, Result and cleanup

Option has explicit `::some` and `::none` alternatives. `?:` is lazy in its fallback. Result and errors are separate from Option absence. Every Result use site writes the error-channel role as `Result<T, error E>`; the generic declaration itself may bind `E: ErrorSet` without repeating that use-site role. Resource-facing Prelude contracts preserve move and exactly-once cleanup responsibility.

`Failable` is the sole core `trait#binding` root. It declares associated types
`Success` and `Failure` and one associated static operation:

```deeplus
public trait#binding Failable {
    type Success
    type Failure

    def ::branch(move source: Self)
        -> BindingBranch<Success, Failure>
        throws Never
        effects {}
}
```

`BindingBranch<S,F>` has exactly `success(value: S)` and
`failure(reason: F)`. The operation consumes its input once and returns exactly
one owner-bearing alternative. `Option<T>` supplies the sealed direct mapping
`Success = T`, `Failure = Unit`; `Result<T,error E>` maps `Failure = E`.
Guarded local `let?` requires `else`, irrefutable success and failure patterns,
and a structurally unconditional failure exit. It does not imply propagation.
There is no `if let?`, `while let?`, `var?`, or bare `let?`; use explicit
Option/Result patterns in conditional and loop positions.

`ActorMessageError` is the closed current actor admission/reply failure family:
`mailboxFull`, `receiverClosedBeforeAdmission`, and
`receiverClosedBeforeReply`. One-way message expressions return
`Result<Unit, error ActorMessageError>`. Request expressions immediately return
`Result<Reply<T>, error ActorMessageError>`; callers extract the reply handle
before one-shot `await`. Cancellation remains a distinct control outcome and is
not an enum case.

The Stable source spelling `Run<T>` names the affine one-shot observation handle
for exactly one successfully spawned execution. Only `spawn` creates a run, and
the nearest lexical `concur` owns it. Its responsibility preserves result type,
normalized ErrorSet, Cancellation, owner `ConcurId`, isolation, cleanup, and
terminal policy. A bare async invocation is not a run, `Run<T>` cannot escape its
owner, and awaiting it consumes its observation right. A run never carries actor
request correlation or transport responsibility.

The Stable source spelling `Reply<T>` names the affine one-shot correlated reply
handle created by one successfully admitted actor request. Typed HIR, module API
digest, and MIR retain one non-forgeable `ReplyResponsibility` descriptor with
the exact fields `result_type`, `normalized_handler_error_set`,
`cancellation_axis`, `isolation_owner`, `correlation_id`, and
`terminal_transport_failure`. The last field is exactly
`{receiverClosedBeforeReply}`. Awaiting the reply exposes
`normalize(normalized_handler_error_set |
ActorMessageError::receiverClosedBeforeReply)`. `mailboxFull` and
`receiverClosedBeforeAdmission` belong only to the precommit admission `Result`
and must never appear in the reply descriptor. Compatibility, join, storage, and
API export preserve the descriptor residue: the normalized static fields must
match exactly unless an explicit admitted ErrorSet-subsumption proof widens the
handler ErrorSet, and each value keeps its own non-forgeable `correlation_id`.
The module API digest stores the static marker
`correlation_id = per_value_non_forgeable`, never a concrete runtime request ID;
typed HIR and MIR carry the distinct value-level identity created after commit.
`Reply<T>` never converts to `Run<T>` and never shares its responsibility
descriptor. Erasing either handle's responsibility residue is rejected with the
existing `RCTS_RESPONSIBILITY_AXIS_DROPPED` family; an unproved combination uses
the existing `RCTS_RESPONSIBILITY_COMBINATION_INVALID` family.

## 4. Fixed operators and protocols

The operator vocabulary and precedence table are closed. Language-reserved
operand domains remain intrinsic and cannot be overridden. Stable fixed-glyph
conformance admits exactly thirteen existing roles: prefix `+`/`-`; binary
`+`, `-`, `*`, `/`, `%`; and `==`, `!=`, `<`, `<=`, `>`, `>=`. Their nine
Trait roots are `UnaryPlus`, `UnaryMinus`, `Add<Rhs>`, `Subtract<Rhs>`,
`Multiply<Rhs>`, `Divide<Rhs>`, `Remainder<Rhs>`, `Eq<Rhs>`, and `Ord<Rhs>`.
`!=` negates the same `Eq.equals` result as `==`; all four order glyphs project
one `Ord.compare` result, and compare zero equals the `Eq` relation. Selection
admits one left-owner `DIRECT_GLOBAL` conformance and never uses conversion,
result context, source/import order, alternate evidence, fallback, or runtime
lookup. Witnesses borrow operands and are synchronous, non-consuming, and
non-mutating. `Eq` has the exact empty responsibility envelope. The other eight
Trait roots admit only the maximum envelope
`throws AllocationError effects allocate`, and every concrete witness seals an
exact subset. Primitive, fixed-width, current Complex, and Rational equality
rows are empty; BigInt/Rational value-producing arithmetic and Rational order
carry the full allocation row. Numeric overflow or zero division/remainder may
terminate only through nonrecoverable `ArithmeticDefect` before commit.
Compound assignment derives its base binary role and owns no separate hook.
Range, power, bitwise, logical, membership and identity hooks remain closed,
as do arbitrary custom operators. Product execution is `NOT_RUN`, and all
`TCC-P1-002..008` remain OPEN evidence gates.

These core declarations carry `trait#operator`. The tag records the closed
language role in `TraitLanguageRoleId`; it does not select glyphs or enlarge the
thirteen-glyph matrix. `Sequence` and `Iterator` similarly carry
`trait#iteration`, and `Display` carries `trait#interpolation`. Only the core
language may declare a role-bearing Trait root. A user type may still provide
one admitted direct global conformance to such a root.

The synchronous R106 iteration handoff treats `Iterator` and `Sequence` as two
ordered static routes, not an `Iterable` facade. A `for` source is evaluated
once; one direct Iterator witness wins, otherwise one Sequence witness may
acquire an Iterator once. The exact associated `Item` and all acquisition,
`next`, cleanup, error, effect and ownership responsibilities are sealed before
loop entry. Current `Iterator.next()` returns `Option<Item>`, `throws Never`,
and has `effects state`; product execution remains `NOT_RUN`.

Keyability likewise selects one coherent direct-global family containing
strong `Eq<Self>`, stable `Hash<Self>`, `Keyable` and one `HashPolicyId`.
Float/Complex partial equality, mutable or lifecycle identity and hidden
provider/policy lookup never create Keyable evidence.

## 4A. Current numeric and indexing boundary

`Int` has the signed 64-bit mathematical domain. `UInt` is the distinct Stable
default unsigned mathematical domain `0..18446744073709551615`; it is not an
alias for `UInt64`, `USize`, `Int`, or `Int64`. An unsuffixed integer still
defaults to `Int`, but it may adapt to `UInt` only when an independently fixed
exact target exists and the magnitude is representable. Negative source,
implicit signedness conversion, and storage/ABI equivalence are not admitted.
Integer operators are checked and raise deterministic `ArithmeticDefect` on
dynamic overflow or division or remainder by zero before assignment commit;
named APIs own wrapping and saturating behavior.

`Float32` and `Float64` follow IEEE-754 binary32/binary64 value behavior with
round-to-nearest, ties-to-even. `Float` is the Stable closed alias of
`Float64`; it creates no distinct nominal, precision, serialization, runtime,
layout, or ABI identity. NaN is unordered, signed zero compares equal, and
neither `Float64` nor its `Float` spelling receives implicit
`Ord`/`Keyable` evidence. None of these laws selects storage, ABI, or backend
layout.

```deeplus
var attempts: UInt = 0
attempts += 1

let ratio: Float = 3.0 / 2.0
```

The compound spelling is canonical for a simple place; it preserves the
single-read, single-RHS-evaluation, failure-atomic assignment law and does not
introduce an increment operator.

`ArithmeticDefect` is the closed nonrecoverable intrinsic family `overflow | divisionByZero`; the latter covers integer and exact-number division or remainder by zero, including Rational fixed-glyph arithmetic. It is neither an `ErrorSet` member nor an enum-as-error and occurs before enclosing place commit. `IndexError` is the closed recoverable family `outOfLogicalDomain | keyNotFound`. `List<T>`, `String`, and `Bytes` have built-in one-based domains. Every `ReadonlyView<T>` preserves its source owner's declared logical coordinates and provenance: views of those ordinary owners are therefore one-based, while views of bounded or sliced owners retain their source domain. String indexing returns `Char` and Bytes indexing returns `UInt8`. Map lookup requires the exact key type. NumericArray uses separate typed axes whose built-in default source coordinates are each `1..dimension`. `Indexable`, `Sequence`, and `LogicalIndexDomain` are checker/library descriptors and named behavior contracts; source conformance to them does not activate `[]`.

NumericArray indexing uses one comma-separated axis per source rank. Scalar
axes disappear from the result; all-scalar selection returns an element and a
mixed selection has rank equal to the number of non-scalar axes. Selection is
Cartesian and never becomes implicit linear indexing or Tuple-as-gather.
NumericArray slicing yields an owner-bounded `ReadonlyView` that preserves
source coordinates and provenance. `[..]` is the general full slice; `[*]`
remains NumericArray-axis syntax and normalizes to the same full-axis selector
for that owner. Open slices `[..<end]`, `[..end]`, and `[start..]` use a
boundary identity capable of representing one-past-last without integer
increment. No Prelude operation silently rebases, copies, makes the view
mutable, crosses isolation, or extends its owner lifetime. An independent
value or rebased coordinate domain requires an explicit named operation.

`ListRestView<T>` is the dedicated borrowed result of an admitted positional
List-pattern rest. It is created only by the closed built-in decomposition
descriptor; ordinary construction and user-supplied conformance do not create
one. Its semantic identity records the source owner and borrow region, an
ordinal `RankSpan(start_rank, count)`, and the exact projection from those ranks
back to the source's logical coordinates and provenance. `count = 0` is a valid
empty residual at a preserved insertion boundary and is not represented by an
invalid or omitted source Range.

`ListRestView<T>` has one explicit intrinsic `Sequence<T>` witness so the
captured residual can be traversed without copying. That witness does not
activate brackets, List patterns, generic Sequence decomposition, mutation, or
an owner-lifetime extension. Existing `ReadonlyView<T>` deliberately receives
no Sequence witness from this rule. Pattern probing may expose a nonowning
rest view to an admitted pure guard, but the final binder is published only
after the entire Pattern succeeds; failure publishes no residual and performs
no hidden allocation.

### 4A.1 MutableList structural operations

`MutableList<T>` keeps ordinary bracket read/replace closed. Its structural
edit surface resolves to exactly thirteen Prelude operations:

```text
insertBefore  insertAfter  prepend  append
insertAllBefore  insertAllAfter  prependAll  appendAll
removeAt  removeRange  removeSelected  popFirst  popLast
```

All are exact `CallableImplementationId` targets in the ordinary `CallExpr` /
`CallPlan(mode_target_pair, call_head_id)` path. There is no structural-edit
HIR node, MIR opcode, extension lookup, import fallback, or runtime method
search. A bulk insertion receives one finite nonescaping `PositionalPack<T>`
whose elements have reusable/copyable evidence; general `Sequence<T>` is not a
finite-source proof and no hidden clone, snapshot, or move is inserted.

The receiver is one exact exclusive mutable place. Receiver, selector, and
payload evaluate once from left to right. Coordinate and overlap checks,
payload staging, and required allocation finish before one mutation commit;
any failure preserves the receiver. Point removal returns `T`; range/selected
removal returns `List<T>` in selector order while preserving survivor order.
Selectors use pre-mutation coordinates and duplicates reject. A temporary,
shared or actor-isolated receiver, self-alias or `inout` overlap, or a live
borrow/view/iterator rejects before commit.

### 4B. BigInt, Rational, Complex, and power

`BigInt` is the public arbitrary-precision signed integer dependency of the
exact-number profile. It is not an alias for `Int`, and its storage and foreign
ABI are opaque. Its runtime value construction and value-producing arithmetic
declare `throws AllocationError effects allocate`; a small-value optimization
does not alter that contract.

`Rational` is an always-available exact value represented semantically by a
normalized BigInt numerator and positive denominator. Construction enforces
`gcd(abs(n), d) = 1` and canonical zero `0/1`. The compound source literal
`<p/q>` and the checked `Rational!` constructor produce the same value
contract. `Rational` supplies strong `Eq<Rational>`, total `Ord<Rational>`,
hashing, and keyability. The sealed Prelude supplies unary `+`/`-`, binary
`+`, `-`, `*`, `/`, `%`, equality and ordering evidence. `/` returns the exact
normalized quotient and zero terminates with
`ArithmeticDefect::divisionByZero`. `%` truncates the exact quotient toward
zero to integer `q` and returns `a - q * b`; the same zero terminal applies.
Named `dividedBy`, `remainderTrunc`, `modEuclid`, and `divRemTrunc` remain the
recoverable or explicitly alternate-law APIs. Decimal, Float and Complex
conversions remain explicit. `display()` may return `2/3`, while
`sourceRepr()` returns the parseable `<2/3>`. Rational `^` remains outside the
fixed-glyph profile.

Rational unary minus, value-producing binary arithmetic, and total ordering
carry `throws AllocationError effects allocate`; unary plus and normalized
equality remain empty. A generic operator call whose only evidence is the
Trait requirement must expose the maximum row. Allocation failure publishes no
partial value and performs no compound-assignment write. It is never converted
to a new OOM Defect.

`Complex<Rep>` is an immutable two-component core numeric value whose initial
Rep set is exactly Float32 and Float64. Bare `Complex` is the closed alias
`Complex<Float64>`. The values `Complex::zero`, `Complex::one`, and
`Complex::i` are type-side constants, not fields of an implicit companion
object. The canonical Cartesian source is:

```deeplus
let z: Complex = 3.0 + 4.0i
let real: Float32 = 1.0
let w: Complex<Float32> = real - 2.0i
```

The `i` marker belongs only to an attached floating-look literal. A direct
`2.0i` literal may adapt to an independently fixed `Complex<Float32>` target,
but the expected result of an operator cannot retroactively choose operand or
operator types; the typed `real` anchor above fixes that operation. Numeric
type suffixes such as `f32`, `u8`, and `i64` are removed. Complex supplies
partial IEEE equality but no implicit strong Eq, total ordering, Hash, or
Keyable. Prelude owns sealed same-Rep Complex and real/Complex unary `+`/`-`
and binary `+`, `-`, `*`, `/` conformances. Complex has neither `%` nor `Ord`;
scalar `^` remains a closed language intrinsic. Named APIs cover conjugate, magnitude, phase,
polar construction, robust checked division, principal exp/log/sqrt/cbrt,
integer/real/Complex power, alternate branches, trigonometric and hyperbolic
families, parsing, codecs, and explicit conversion.

The Preview numeric profile additionally proposes the compact `4i` spelling
for `Complex<Float64>(+0.0, 4.0)`. It is limited to an attached unsuffixed
decimal integer followed by an identifier boundary. `0x4i`, `4u8i`, `4 i`,
and `4index` do not enter that Preview literal judgment. The current admitted
floating forms above remain unchanged until separate activation evidence
exists.

NumericArray Complex dot product conjugates the left operand. `dotu` is the
explicit unconjugated operation. Attached `A^` is transpose and
`A ~ adjoint` is conjugate transpose.

Infix `^` has one closed static type matrix and uses no `Power` Trait,
expected-result selection, runtime sign/integrality test, provider, fallback or
runtime lookup. Real power remains real; Complex power uses the principal
branch. Ordinary `0 ^ 0` returns one in the selected result domain; named
`powChecked` may instead report `PowerError::indeterminate`. All of these are
language/Prelude design contracts; every product lane remains `NOT_RUN`.

### 4C. Numeric capabilities and `std::math`

The thin Preview lattice contains `Numeric`, `ExactNumeric`,
`ApproximateNumeric`, `IntegralNumeric`, `RealScalar`, `BinaryFloating`, and
`ComplexScalar`. These names express capability requirements only. They do not
create representation subtyping, implicit numeric conversion, ordering,
hashing, keyability, remainder, transcendental support, operator activation,
or a common runtime value.

The current `std::math` facade is a `STDLIB_PROFILE` with closed groups for:

- core classification and rounding;
- elementary, exponential, logarithmic, trigonometric and hyperbolic
  operations;
- complex principal-branch operations;
- approximation helpers.

Each callable must state its exact scalar family, result family, exceptional
value behavior, error/effect row, and approximation responsibility. Special
functions and calculus are separate Preview/nonactivatable profiles; the latter
returns an explicit `Result<Estimate<T>, error NumericAnalysisError<T>>`.
Neither current profile maturity nor a Preview inventory is a product-support
claim, and none activates a hidden conversion or operator witness.

## 5. Profile boundaries

Calendar and dynamic unit conversions are stdlib/provider profiles, not core syntax and not `#preview` features. R2 solver and provider derive-via are official tooling; neither changes Prelude type identity or injects evidence. UML remains an official tooling family only where its schema and fixture contract is current.

## 6. Navigation and evidence

Use the signature catalog for exact names, generic channels, parameter labels, return types and feature references. Use the TypeSystem for compatibility and responsibility judgments, Operational Semantics for MIR behavior, and the example corpus for accepted/rejected design-static surfaces. All runtime/provider results remain `NOT_RUN` until artifact-bound receipts exist.

The current async collection profile binds three Prelude identities without introducing syntax: `AsyncSequence<T, E: ErrorSet>`, `AsyncCollector`, and `CollectPolicy::sequential`. `AsyncSequence<T, E>` is a single-consumer source with one source-ordered async `next` channel and one terminal end/error/cancellation outcome; `E` is the source failure set and cancellation remains a distinct control outcome. `AsyncCollector::list<T, U, ES, ET>` requires checker evidence that the source is finite and exposes exactly `throws ES throws ET`, the normalized union of the source and transform failure sets. The single policy means source-order result, fail-fast first failure, cancellation of pending work, a capacity-one buffer, no partial commit, and cleanup before return. Completion-order and dynamically bounded alternatives are not current defaults.


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

## 10. Human index of the 71 canonical Prelude entries

This generated review index mirrors the machine catalog without replacing it. `status` is design/profile maturity; every product-support cell remains `NOT_RUN`.

| Symbol | Kind | Status | Responsibility |
| --- | --- | --- | --- |
| `JsonValue` | boundary_value | `stable_design` | external JSON model distinct from Plain and Dyn |
| `WitnessId` | checker_identity | `stable_design` | explicit conformance evidence identity; never synthesized from extension presence |
| `FillRepeatAdmissibilityProfile` | checker_known_protocol | `stable_design` | Stable checker law for shaped fill/repeat/generator initializer admissibility. |
| `Indexable` | checker_known_protocol | `stable_design` | built-in owner indexing descriptor; conformance does not activate brackets |
| `ArithmeticDefect` | language_intrinsic_defect | `stable_design` | closed nonrecoverable checked-integer failure family: overflow or division/remainder by zero |
| `Add<Rhs>` | trait | `stable_design` | exact non-intrinsic `BinaryAdd` evidence with associated `Output` |
| `Divide<Rhs>` | trait | `stable_design` | exact non-intrinsic `BinaryDivide` evidence with associated `Output` and precommit ArithmeticDefect law |
| `Eq<Rhs>` | trait | `stable_design` | one strong equality witness deriving both `==` and `!=` |
| `IndexError` | enum | `stable_design` | closed recoverable out-of-domain and missing-key indexing failure family |
| `MembershipProtocol` | checker_known_protocol | `stable_design` | Current Prelude design vocabulary; product support NOT_RUN. |
| `List<T>` | collection | `stable_design` | ordered owned collection with one-based built-in indexing |
| `Map<K,V>` | collection | `stable_design` | exact-key lookup; no public Copyable or key-as-member projection |
| `Set<T>` | collection | `stable_design` | immutable unique-element collection; equality and keyability are explicit, duplicate literal entries reject, and iteration order is not semantic |
| `ImplementationId` | compiler_identity | `stable_design` | implementation symbol reusable without merging extension and witness identity |
| `Facet<Mode,Contract>` | compiler_intrinsic_type | `stable` | RCTS-V5 ownership-qualified existential carrier; borrow mode Stable, inout/move nonactivatable |
| `Box<T>` | core_type | `stable_design` | unique owning indirection whose canonical constructor is Box!(value), with exactly-once payload cleanup |
| `ByteView` | core_type | `stable_design` | contiguous byte-addressable readonly bytes acquired by borrowing Bytes::view; the result retains owner provenance and assumes neither text encoding nor String semantics |
| `Bytes` | core_type | `stable_design` | raw byte sequence with one-based UInt8 indexing; no implicit String conversion |
| `FrozenList<T>` | core_type | `stable_design` | immutable result of an exclusive freeze transition; cross-isolation shareability requires an independent payload-capability proof |
| `ListSnapshot<T>` | core_type | `stable_design` | independent point-in-time list value with declared copy/COW cost |
| `MutableList<T>` | core_type | `stable_design` | exclusive mutable list owner; snapshot borrows without invalidating the source, while freeze consumes the receiver and completes its ownership transition |
| `PositionalPack<T>` | compiler_intrinsic_type | `stable_design` | finite call-scoped positional residue; never erased to Sequence and never escapes its call owner |
| `NamedPack<rho>` | compiler_intrinsic_type | `stable_design` | finite call-scoped static-label row with API-bound normalized row/witness digest |
| `NumericArray<T, rank R>` | core_type | `stable_design` | ranked numeric value with typed one-based default axes and visible allocation/backend responsibility |
| `OwnedDowncast<Target,Source>` | core_type | `stable_design` | sum channel that preserves exactly one owner on both downcast outcomes |
| `ReadonlyView<T>` | core_type | `stable_design` | nonowning nonmutating owner-bounded coordinate-preserving view |
| `ListRestView<T>` | core_type | `stable_design` | owner-bounded positional List-rest view with an explicit intrinsic Sequence witness and exact rank-to-coordinate provenance |
| `String` | core_type | `stable_design` | immutable Unicode scalar sequence with one-based Char indexing |
| `Run<T>` | core_type | `stable_design` | affine one-shot observation handle for one spawned execution owned by one lexical `concur`; preserves result, ErrorSet, Cancellation, isolation, cleanup, and terminal responsibility and carries no actor transport descriptor |
| `Reply<T>` | core_type | `stable_design` | affine one-shot correlated actor-request reply handle with typed-HIR/API/MIR `ReplyResponsibility`; preserves the exact handler ErrorSet, Cancellation, isolation owner, per-value correlation, and sole post-admission transport failure and never converts to `Run<T>` |
| `AsyncCollector` | stdlib_profile | `stable_design` | finite policy-visible async collection with no partial commit |
| `AsyncSequence<T, E>` | protocol | `stable_design` | asynchronous element source with a bound error set and visible cancellation, isolation and cleanup responsibilities |
| `ExitCode` | entry_result | `stable_design` | Launcher-facing result; ordinary calls do not map it to process termination. |
| `CollectPolicy` | enum | `stable_design` | exact sequential/source/fail-fast/cancel-pending/buffer-one collection policy |
| `Option<T>` | enum | `stable_design` | recoverable absence as value, not Error |
| `Result<T, error E>` | enum | `stable_design` | value-level error channel distinct from throws |
| `BindingBranch<S,F>` | enum | `stable_design` | exact success/failure owner carrier returned by Failable::branch |
| `Failable` | trait_profile | `stable_design` | core `trait#binding` root for consuming else-required guarded local `let?` |
| `downcastOwned<Target,Source>` | function | `stable_design` | generic target is selected from the exact expected OwnedDowncast result type; no runtime type-token argument is accepted |
| `replace<T>` | function | `stable_design` | one-evaluation exclusive place transaction returning the old owner |
| `withBorrowed<T,R>` | function | `stable_design` | invocation-bounded borrowed callback helper |
| `ContextParameterRole` | function_signature_descriptor | `stable_design` | function parameter role preserved in signature identity under the Stable design explicit context parameter law |
| `Bitwise` | internal_or_stdlib_trait_seed | `stable_design` | named bitwise contract seed; current bitwise glyphs remain intrinsic-only |
| `ModuleSignature` | language_surface | `stable_design` | public API boundary surface; stable design; not separate compilation receipt |
| `Float32` | numeric_type_side_constants | `stable_design` | IEEE binary32 value behavior; non-finite values are type-side constants. |
| `Float64` | numeric_type_side_constants | `stable_design` | IEEE binary64 value behavior; NaN supplies no implicit ordering/key evidence. |
| `Float` | numeric_alias | `stable_design` | Stable closed source alias of `Float64`; no distinct nominal, precision, serialization, layout, or ABI identity. |
| `UInt` | core_numeric_value | `stable_design` | Separate default unsigned 64-bit mathematical domain; checked arithmetic and no implicit signedness conversion or ABI identity. |
| `BigInt` | exact_numeric_value | `stable_design` | arbitrary-precision signed integer dependency; no implicit Int or ABI equivalence |
| `Rational` | exact_numeric_value | `stable_design` | normalized exact BigInt ratio with strong equality/order/hash/key laws |
| `Complex<Rep>` | core_numeric_value | `stable_design` | immutable Float32/Float64 complex value with partial equality and principal numeric APIs |
| `PowerError` | enum | `stable_design` | checked named analytic power outcome; ordinary infix 0^0 remains one |
| `Actor` | protocol | `stable_design` | isolated mailbox execution root |
| `ActorMessageError` | enum | `stable_design` | closed actor admission/reply failure family; cancellation excluded |
| `Sequence<T>` | protocol | `stable_design` | core `trait#iteration` ordered-sequence contract; conformance alone does not activate brackets |
| `Char` | scalar | `stable_design` | exactly one Unicode scalar value; surrogates excluded |
| `Shared<T>` | shared_handle | `stable_design` | shared observation handle, not mutable alias permission |
| `SharedCell<T>` | synchronization | `stable_design` | sequentially consistent scoped observation and owner replacement for Plain payloads; no raw-layout or lock-free inference |
| `String::render<T>` | static_function | `stdlib` | single-evaluation nonescaping structured-value renderer |
| `Option<T>::unwrapOrElse` | stdlib_operation | `stable_design` | Named lazy equivalent of one-layer Option coalescing; fallback executes only for none and preserves conditional ownership/error/effect/cleanup. |
| `Measure<Rep, Dim>` | stdlib_profile | `stdlib_profile` | Measure conversion APIs are explicit and use unit witness carriers. |
| `UnitCatalog` | stdlib_profile | `stable_design` | Stable design user unit catalog profile; product support NOT_RUN. Dynamic/provider conversion is outside this stable core. |
| `Grapheme` | stdlib_value_or_view | `stable_design` | extended grapheme cluster produced by named segmentation API |
| `SharedMutex<T: SharedMutexPayload>` | synchronization | `stable_design` | `SharedMutexPayload` is the sealed context-specific public payload constraint checked by internal `SharedMutexPayloadAdmitted`; it admits cleanup-free Reusable or Affine payloads without creating any other responsibility evidence, while receiver-bound non-reentrant scoped mutation provides non-suspending access and exactly-once unlock before the next successful lock |
| `ExtensionSetId` | tooling_schema | `stable_design` | semantic identity seed for named extension set D-MAD; not current source |
| `BitfieldCodec` | trait | `stdlib` | explicit endian codec |
| `BitfieldRaw<Backing>` | trait | `stdlib` | checked raw carrier contract |
| `LogicalIndexDomain<Index>` | trait | `stable_design` | named logical-domain contract; built-in brackets remain closed-owner syntax |
| `Ord<Rhs>` | trait | `stable_design` | total-order evidence deriving all four order glyphs from one compare result |
| `Multiply<Rhs>` | trait | `stable_design` | exact non-intrinsic `BinaryMultiply` evidence with associated `Output` |
| `Remainder<Rhs>` | trait | `stable_design` | exact non-intrinsic `BinaryRemainder` evidence with an explicit quotient law |
| `Subtract<Rhs>` | trait | `stable_design` | exact non-intrinsic `BinarySubtract` evidence with associated `Output` |
| `UnaryMinus` | trait | `stable_design` | exact non-intrinsic prefix `-` evidence with associated `Output` |
| `UnaryPlus` | trait | `stable_design` | exact non-intrinsic prefix `+` evidence with associated `Output` |
| `Display` | trait/profile | `stable_design` | core `trait#interpolation` rendering/display contract; not serialization or redaction authority |

`Eq<Rhs>.equals(rhs)` uses the instance marker's implicit borrowed `Self`
receiver and one explicit borrowed `rhs`. It is deterministic, pure,
synchronous, non-consuming, authority-free, `throws Never`, and returns
`Bool`. It is reflexive, symmetric, and transitive. `!=` always negates this
exact result and never selects a second witness.

`Ord<Rhs>.compare(rhs)` likewise uses the implicit borrowed `Self` receiver and
one explicit borrowed `rhs`. It is deterministic, pure, synchronous,
non-consuming, authority-free, `throws Never`, and returns an `Int` whose sign
alone is contractually meaningful and stable. It must be total for every admitted ground `T`;
zero is the ground type's equality relation, and transitivity, antisymmetry and
trichotomy are required. `Ord<Rhs>` derives `Eq<Rhs>`, so zero must coincide
with `Eq.equals`. One witness derives `<`, `<=`, `>`, and `>=`. An eligible
payload-free nongeneric ordered Enum receives one whole-Enum Eq/Ord pair; an
explicit Enum range is semantic-ascending under that order and never follows a
raw/tag/layout/ABI identity.

User and language-derived strong comparison rows are homogeneous:
`NORMALIZED_RHS_MUST_EQUAL_SELF`. A heterogeneous strong comparison is
`SEALED_BILATERAL_FAMILY_ONLY` and must be owned by one compiler/Prelude row
family containing both orientations, a shared normalization domain, Eq
symmetry, Ord reverse-sign and zero/equality agreement. The current Prelude
registers no heterogeneous strong-comparison family. Intrinsic-reserved pairs
remain outside this conformance lookup, and separately named partial equality
does not create Eq evidence.

`Display.display()` borrows its receiver, is deterministic, synchronous,
non-consuming, authority-free, `throws Never`, and performs no hidden locale,
provider, serialization, parsing, or redaction operation. String interpolation
must select every nested `Display` witness before evaluation. The accepted Enum
case-mapping proposal may synthesize one whole-Enum witness only after its
nonactivatable feature gates close; it creates no case- or alias-local witness.
| `Iterator` | trait_profile | `stable_design` | R106 core `trait#iteration` synchronous iterator with exact associated Item and sealed acquisition/next/cleanup responsibility; product support NOT_RUN |

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
