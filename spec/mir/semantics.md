# Deeplus Operational Semantics 0.1.2 — R51f3 Current Canonical

Deeplus MIR is the canonical semantic authority. Rust frontend structures, xVM bytecode, Cranelift IR (CLIF), AOT code, and Cranelift JITModule code are projections that must preserve MIR-observable behavior. Product execution is `NOT_RUN`.

Member visibility is sealed before MIR. `MemberVisibilityOmissionV1` preserves
an absent sigil only through CST and AST, resolves it after exact owner and slot
binding, and requires a non-null effective domain in typed HIR. MIR receives no
`OMITTED` state, performs no visibility lookup or runtime access check, and adds
no operation for `IR-VIS-P1-057`. xVM and Cranelift may not reinterpret an
owner default, inherited slot, Trait requirement, or actor transport domain.

Source-item ownership is likewise sealed before HIR and MIR.
`SourceItemCommitmentV1` preserves its row and marker span only in the lossless
CST; normalized AST contains the selected declaration or statement owner, and
MIR receives neither a commitment node nor a fallback branch. A contextual
declaration that fails after its marker has no runtime meaning and never lowers.
MIR, xVM and Cranelift perform zero contextual-word, symbol, type, overload or
source-order lookup and cannot reinterpret `actor Worker { ... }` as a call.
The parenthesized `actor(Worker) { ... }` form is already an ordinary call before
lowering. Product frontend and backend execution remain `NOT_RUN`.

## 1. Machine state and observation

A step state contains the current MIR frame, ordered operand stack, places and ownership states, cleanup-region stack, effect/error continuation, execution/concur/actor state, provider bindings, and source provenance. Observable events are ordered result/failure, I/O or authority events, message enqueue/dequeue, run spawn/join, suspension/resume, cancellation, cleanup and provider observation. Backend-private allocation and instruction selection are not observations.

## 2. Evaluation and calls

Operands, arguments, guards, interpolation segments, collection entries and cleanup registrations evaluate left-to-right unless a named law fixes another order. Calls preserve value, context, witness, repeated positional and named channels. `values..: T` declares a repeated-positional channel, while `options**: NamedPack<rho>` declares a finite, nonescaping named-rest row; `*sequence` and `**namedPack` are the corresponding positional and named unfolds. The checker seals source order, labels, row identity and normalized row digest before overload selection or MIR emission. Labels, witness ids, extension ids and providers are fixed before MIR execution.

Every ordinary, message, and actor-transport surface normalizes to one
`CallExpr` carrying one `CallMode` (`Ordinary`, `Message`, or `ActorMessage`),
one ordered `CallArgument` sequence, and one closed `ResolvedCallPlan`.
`CallArgument` preserves positional, named, positional-unfold, named-unfold,
context, witness, and trailing-closure channels. There is no message payload
aggregate and no Tuple/Record-to-formal projection. `receiver ~ send ()`
therefore carries one Unit argument, while `receiver ~ ping` carries none. The
closed plan variants are `DirectImplementation`, `VirtualSlot`,
`TraitWitness`, `ExtensionStatic`, `ActorTransport`, and
`ReservedOperation`. Labels, selected formals, source evaluation order, and
formal binding order survive lowering and are never recovered from runtime
selector search, provider order, expected result type, or source order.

A Trait-qualified associated-static selection is a non-structural
`TraitAssociatedStaticSelection` descriptor, not a new HIR expression or MIR
operation. It binds one `SelectionId` and the exact `TraitId`, `RequirementId`,
`ConformanceId`, `TraitWitnessId`, `ImplementationId`, `SubstitutionId`, and
`ResponsibilityId` selected by the checker. Representation metadata also binds
the direct static symbol when one exists and maps an associated function's
`ImplementationId` to its `CallableImplementationId`. An associated type emits
no runtime operation. An associated value or bare associated-function reference
reuses `ResolvedRef::DirectDecl`, `HM-LR-REF-002` (`STATIC_REF`), and
`HM-LR-TOP-002`; an invoked associated function reuses
`ORDINARY::TRAIT_WITNESS`, `HM-LR-CALL-003`, `STATIC_REF`, and `INVOKE`.
MIR preserves the same descriptor in the closed
`TRAIT_ASSOCIATED_STATIC_SELECTION` static-identity domain with
`identity_id == SelectionId`. Lowering preserves all eleven responsibility
axes and never reconstructs or searches for a conformance, witness,
implementation, provider, order winner, specialization, fallback, or
child-local replacement at runtime.

The nonactivatable concise throws/effects Preview creates no MIR syntax or
presence bit. If later activated, the frontend normalizes every omitted
declaration axis before MIR: missing `throws` becomes `Never` and missing
`effects` becomes `{}`. MIR receives only complete normalized rows and checks
every emitted throw/effect edge against them. Explicitly empty and omitted rows
are indistinguishable below the lossless CST. Current private ErrorSet
inference remains authoritative until a separate migration and supersession
decision.

Operator syntax and precedence remain closed. An intrinsic-reserved normalized
operand pair lowers to its closed intrinsic MIR operation and performs no
conformance lookup. A non-intrinsic exact unary `+`/`-`, binary
`+`/`-`/`*`/`/`/`%`, equality, or ordering role may instead lower to
`FixedOperatorConformanceCall`. That node preserves
`OperatorId`, normalized left/right type IDs, `ConformanceId`, `WitnessId`,
`MethodId`, normalized substitution, `OutputTypeId`, and
`ResponsibilityProfileId` selected statically by the checker.

For strong Eq/Ord, the checker also seals
`StrongComparisonFamilyId?`, `ReverseWitnessId?`, and
`NormalizationDomainId?`. All three are null for a homogeneous Self row. A
heterogeneous row reaches MIR only when one compiler/Prelude-sealed bilateral
family supplies all three identities and proves the paired law vector; the
current family registry is empty. MIR cannot pair independent witness rows,
infer a reverse relation, normalize through an implicit conversion, or repeat
comparison selection at runtime.

Automatic Trait synthesis also closes before MIR. `supports auto` binds only a
core/Prelude-owned `(TraitId, PolicyVersion)` row in
`TraitAutoPolicyRegistryV1`; it does not define an executable source policy.
The only current rows are Shareable and Transferable under
`RESPONSIBILITY_STRUCTURAL_FIXED_POINT_R1`. A successful bodyless `by auto`
request seals `TraitAutoPolicyId`, policy digest, finite sorted input evidence,
`ConformanceId`, emitted `TraitWitnessId` values and `DerivationDigest` in HIR
and public conformance residue. MIR adds no auto-policy operation and performs
zero extension, provider, registry, source-order or runtime relookup; later
uses consume the already selected witness and existing responsibility residue.

Both operands evaluate once, left-to-right, before the borrowed, pure, total,
synchronous witness call. The node has no implicit conversion, expected-result
selection, provider/extension/local/case/`via`/`VIA`/`AUTO`/specialization
route, source/import-order winner, runtime lookup, or fallback edge. Its
`throws Never effects {}` responsibility cannot introduce mutation,
consumption, suspension, or authority. Other glyph families remain intrinsic
or rejected. Strict Boolean `and`/`or` evaluate both operands left-to-right;
sequential `and then`/`otherwise` evaluate the right operand only when required.
The existing `?:` Option law remains separately lazy.

Spaced infix `^` lowers only from a verified closed
`HirIntrinsicPlan`. Its operation is one of `CheckedIntPow`,
`FloatPowInt`, `FloatPow`, `ComplexPowInt`, `ComplexPowPrincipal`, or
`MeasurePowStatic`; there is no generic `Pow` call and no conformance/runtime
lookup. The plan preserves source evaluation order `[base, exponent]`,
source/adapted operand types, result type, `ImplementationId`,
`ResponsibilityProfileId`, `NumericSemanticsProfileId`, and
`SpecialValueProfileId`. Its operand adaptation is one of `Identity`,
`DirectLiteralToF64Exact`, `F32ToF64`, `F32ToComplex64`, or
`F64ToComplex64` and never becomes a selected call.

`CheckedIntPow` is a checked operation whose overflow Defect occurs before an
enclosing commit. Float and Complex power are pure total value operations:
NaN, infinity, signed zero and branch-cut results are ordinary values under
the bound special-value profile. Real power never changes its static result to
Complex at runtime. Principal Complex power uses the signed-zero-aware
principal logarithm. Constant evaluation and every backend bind the same
profile identity and canonical NaN policy. A backend math helper symbol is a
projection detail rather than semantic callee identity.

A ternary lowers to one Bool condition evaluation, one two-way branch, exactly
one lazy arm evaluation, and one explicit responsibility join. It cannot
evaluate both arms, synthesize a Union at the join, duplicate a place
observation, or discard an effect, error, cancellation, ownership, or cleanup
obligation that exists on either incoming edge.

An assignment evaluates its target place once and its right operand once. A compound assignment evaluates the place, reads the original value, evaluates the right operand, completes one intrinsic operation, and commits at most one write, in that order. Every assignment returns `Unit`. Any failure before commit preserves the original owner and value; no compound-assignment MIR opcode may hide a second place evaluation or partial write.

An ordinary `mut` parameter is lowered as one callee-owned mutable local place. The argument is evaluated and acquired once before that place is committed; an affine argument moves into it, no caller-place alias or write-back edge is created, and the callee owns its exactly-once cleanup. This is distinct from `inout`, which borrows one caller place exclusively and commits writes to that same place, and from a `mut T` responsibility, which denotes a unique mutable owner rather than a call channel. A failure before parameter commit retains the caller owner and publishes no callee local.

Type ownership qualifiers are closed before MIR sealing. `UNQUALIFIED`
delegates to the already checked base-type responsibility; `OWNED` retains the
base type's `REUSABLE` or `OWNED` value class with null region and loan;
`BORROWED` produces a `BORROWED` value
with one exact `RegionId` and `LoanId`; `MUT` produces an `OWNED` value whose
admitted place capability is mutable; and `INOUT` produces an `INOUT` value
with one exact region and exclusive loan. The source qualifier remains HIR and
module-API identity even where two variants share the same MIR ownership enum.

The HIR-to-MIR verifier rejects a missing required region, a region on an
owner qualifier, qualifier stacking after alias expansion, public residue
that erased the qualifier, and every mapping other than the exact table above.
Borrowed and inout values may not cross a return, storage, capture,
suspension, isolation, actor, concur, or FFI boundary unless the exact
qualifier contract admits and records the corresponding origin relation.
Cranelift receives only the verified MIR ownership, place, region, loan, and
cleanup plan. It cannot infer qualifier legality from address shape or choose
a different responsibility in AOT or JIT lowering.

### 2.1 Function static activation

An admitted synchronous named callable may own one `static { ... }`
prologue. It is a dedicated callable-body declaration, not an ordinary block
item. Optional compile-time `use`/`import` block prologue directives precede
it, and it precedes every runtime semantic item. The exact admitted owner and
profile matrix is fixed by
`spec/contracts/function-static-activation.json`; entry/local functions,
constructors, cleanup declarations, actor handlers and requests, closures,
async or generator callables, FFI/recovery declarations, bodyless Trait
requirements, and `def#guard` do not acquire this route.

The selected implementation has one typed `CallableImplementationId`.
`FunctionStaticOwnerId` is the deterministic hash-domain identity of the
activation semantics version, that implementation identity, normalized owner
and callable generic instantiations, and one canonical activation-contract
digest. The contract digest binds the normalized activation HIR plus sorted
actually used `WitnessId`, `ConformanceId`, and statically selected helper
records; every helper record carries its `CallableImplementationId`,
`activation_present=false`, and safety-summary digest. Trivia, source path,
import/use/source order, runtime address, machine-code sharing, inlining, LTO,
and JIT compilation identity are excluded. Runtime state is keyed by
`(RuntimeInstanceId, FunctionStaticOwnerId)`. Equal hash IDs with unequal
canonical recipes are a terminal link collision, never an order-selected
winner.

Only actual invocation of the final selected `CallableImplementationId`
triggers the barrier. Name lookup, overload candidate collection, Trait
checking, function-value creation or copying, reflection, inlining, and
compilation are not triggers. For an activation-bearing call, MIR preserves
this order:

```text
evaluate callee or receiver
evaluate explicit arguments left-to-right
evaluate defaults under the current call law
validate and acquire staged temporaries
ensure (RuntimeInstanceId, FunctionStaticOwnerId)
perform the existing atomic ownership_commit for callee input channels
emit callable_invoke and enter the ordinary contract/body
```

No new `CALL_INPUT_COMMIT` event is invented. If evaluation or staging fails,
the ensure does not run. If ensure fails, `ownership_commit` and ordinary-body
entry counts are zero, caller-owned places remain with the caller, and staged
temporaries and reservations clean exactly once in reverse acquisition order.
The Ready/Failed fast path remains after argument/default evaluation, so an
optimizer may not move it earlier across observable evaluation.

The state machine is closed:

```text
Dormant -> Initializing -> Ready
                     -> Failed(FailureRecord)
Ready  -> Ready
Failed -> Failed
```

Exactly one entrant claims `Initializing`. Other entrants may wait
internally, but that wait is neither source-level suspension nor a
cancellation point and promises no fairness. `Ready` or `Failed` publication
happens-before every caller that leaves the ensure barrier; a backend may use
release/acquire or stronger ordering, but this grants no weak-atomic source
surface. Partial publication is forbidden.

Activation normal completion is `Unit`. Its checked body is safe,
synchronous, nonsuspending, noncancelling, `throws Never`, `effects {}`, and
authority-free. It observes no receiver, parameter, evaluated default,
`Context`, caller execution/actor/thread identity, time, random, environment,
ambient provider, or mutable global state. It creates no persistent mutable
publication, Resource escape, or `needsDrop` residue; performs no outward
control transfer, local-function declaration, lazy force, dynamic/indirect/
provider call, or call whose metadata has `activation_present=true`. Pure
statically selected helpers are admitted only through the closed dependency
records above.

Any initiating Defect is captured as the cause of one owner-bound
`FUNCTION_STATIC_ACTIVATION_FAILED` record. The winner, every waiter, and every
later caller observe that same terminal failure identity and cause chain;
there is no scheduler-dependent “original for the winner, wrapper for
waiters” split, implicit retry, or reset. Same-owner reentry records
`FUNCTION_STATIC_ACTIVATION_REENTRANCY` as the canonical cause and transitions
the owner to the same terminal `Failed` state; deadlock and undefined behavior
are forbidden. Product lexer/parser/checker, MIR lowering, xVM, Cranelift,
formatter/LSP, and executable concurrency evidence remain `NOT_RUN`.

Closure environments are built by one ordered capture plan. `borrow` and
`inout` create bounded nonescaping observations, `move` transfers one owner,
and `copy` requires the sealed `CopyValue` responsibility while preserving a
null Trait witness. Both `copy` and `clone` carry one exact
`ResponsibilityEvidenceId`; their referenced descriptors remain distinct.
The `CopyValue` descriptor is an intrinsic predicate proof with a null Trait
witness, while the `Clone` descriptor owns one exact selected witness together
with its normalized ErrorSet, EffectRow, result acquisition, and cleanup plan.
`deep` is rejected before typed HIR or MIR because its distinct `DeepClone`
profile is nonactivatable; it never falls back to Clone and leaves no typed
lowering residue. Callable responsibility profiles remain a separate identity
domain. The backend receives the already selected responsibility/evidence
identities and performs no runtime lookup. A capture-level
`once` field is one-shot but does not consume the closure's callable right
unless the closure independently has `#once`. During the fallible preparation
interval, `move` and capture-level `once` emit only `MOVE_RESERVE`; neither
`PLACE_MOVE` nor their field `BUILDER_STAGE` may occur. A failed preparation
cancels reservations, ends loans, and cleans staged values in reverse
acquisition order without restoring an already consumed source, because no
source has yet been consumed. After every fallible preparation succeeds, one
infallible final interval performs source-ordered `PLACE_MOVE` and
`BUILDER_STAGE` for reserved fields, then `BUILDER_COMMIT`, followed by
infallible `CLOSURE_MAKE`. It publishes no partial environment or closure.

A proven lexical dependency is not a capture-plan item. The callable descriptor
keeps residence and environment orthogonal, so a region-bound callable may
also have an explicit environment for other names. Each lexical dependency
lowers to an ordinary read whose place root is the exact ancestor frame/region
and place identity. It emits no capture acquire, commit, snapshot, move, or
cleanup event, and the hidden static-link representation is backend-private.
The call boundary validates the ancestor place as `LiveReadable` and keeps any
shared-read requirement active for the invocation region. A present empty
capture list is a closed assertion and makes an ancestor-rooted read
unreachable.

The Preview function-static namespace adds no current MIR operation. Its future
initialization plan distinguishes a read of a prior privately staged slot while
the owner is `Initializing` from an ordinary Ready-slot read. It preserves
declaration order, has no self/forward/cycle/topological-reorder route, and
publishes every immutable M0 slot only with the existing atomic `Ready`
transition. Failure and reentry retain the existing function-static diagnostic
and identity families.

## 3. Ordinary and rightward local bindings

An ordinary local binding evaluates its initializer exactly once while the target is absent from scope. On success it commits one immutable or mutable place; on failure it commits none and transfers along the initializer failure edge. Rightward binding has no MIR operation: `$`/`$$` is eliminated by frontend normalization to this rule. Cleanup responsibility moves into the committed local exactly as for direct `let`/`var`.

`yield value -> $response` first emits the coroutine suspension event. After resume, the response value is passed to the ordinary binding rule. This does not make general rightward binding a suspension form.

## 4. Values, literals, strings, and bytes

Plain and raw source strings lower to immutable `ConstString` payloads. The raw scanner supplies the exact body scalars; escape and interpolation machines are not invoked. xVM and both Cranelift backends observe the same String value.

Interpolated strings lower to an ordered segment plan. Direct segments are
constants; each hole retains one source evaluation, a direct String route or
one preselected `Display` witness invocation. Shorthand projections are read-only and braced
expressions use ordinary MIR. The plan commits one final String only after all
segments succeed, carries no locale/provider/serialization/redaction
observation, and performs reverse temporary cleanup on an earlier failure.

### 4.1 Stable interpolation format plan

An admitted colon format lowers as the hole's immutable `FORMAT_SPEC_V1` plan:
alignment is `LEFT`, `RIGHT`, or `CENTER`; minimum width is 1 through 1,000,000;
fill is U+0020; and the width unit is Unicode scalar value. The ordered builder
stage evaluates the hole value once, uses a String value directly or invokes
the preselected `Display` evidence once for a non-String value, counts the
resulting segment's scalars, applies only the missing padding,
and stages that segment once. Center padding uses floor on the left and the
remainder on the right. A segment already at or above the minimum is unchanged;
there is no truncation operation or hidden call into a locale, provider,
serialization or reflection service. Invalid format text is rejected before
HIR and creates no MIR. Padding allocation and cleanup remain within the same
interpolation builder transaction and introduce no new outcome family.

MIR value identity records the semantic type and value, not a storage address, serialization tag, runtime discriminant, ABI, or backend layout. Unsuffixed `Int` constants inhabit the signed 64-bit mathematical domain. Explicit integer domains remain distinct. Integer arithmetic is checked: a dynamic overflow or division or remainder by zero emits deterministic `ArithmeticDefect` before any enclosing place commit; wrapping and saturation occur only through named calls. Integer division truncates toward zero, and remainder preserves `a == trunc(a / b) * b + r` with `r == 0` or the dividend sign and `|r| < |b|`; signed `MIN / -1` and `MIN % -1` take the overflow edge. Floating and Complex `%` have no MIR operation. A statically rejected failure creates no MIR.

`Float32` and `Float64` operations preserve IEEE-754 binary32/binary64 behavior and round to nearest with ties to even. NaN is unordered and signed zero compares equal. Char constants contain exactly one Unicode scalar. String indexing observes Unicode scalar position; Bytes indexing observes one `UInt8`. Neither lowering implies UTF-16, grapheme, text/byte conversion, or a public representation. The recovery spelling `null` creates no MIR constant; Option absence lowers only from the explicit `none` alternative.

A Rational literal lowers as `ConstRational` containing one normalized
arbitrary-precision numerator and positive denominator. Its raw `<p/q>` source
spelling is debug/source provenance and is never evaluated as integer
division. Construction and checked named division distinguish
`zeroDenominator` from `divisionByZero`; both preserve failure-before-commit.

An imaginary literal lowers as one Complex constant with exact
`ComplexTypeId`, `RepTypeId`, positive-zero real component and validated
imaginary component. `4.0i` defaults to exact Float64 component values; an
atomic unsuffixed imaginary literal may instead adapt directly to an exact
contextual target such as `Complex<Float32>`. Numeric type suffixes never reach
MIR, and the expected result type never selects an operator witness. Complex arithmetic preserves
`OperatorId`, selected `ConformanceId`/`WitnessId`/`MethodId` where the
Stable `+`/`-`/`*` corridor is used, `ImplementationId`, substitutions,
responsibility and numeric-semantics profile. It must not erase the value to
an anonymous pair before those identities are represented. Complex division
is a closed intrinsic; named transcendental functions may project to a shared
runtime implementation without inventing one MIR opcode per API. No public
foreign ABI follows from the semantic pair.

## 5. Failure and cleanup

Errors, defects and cancellation are distinct. Cancellation progresses through request, observation, acknowledgement, cleanup barrier, and terminal outcome events; each event is monotonic and idempotent for one CancellationId. Primary/suppressed failure order is deterministic: at one `concur` terminal barrier, the failed run with the lowest lexical `spawn_index` becomes primary and the remaining run failures are appended in ascending `spawn_index`; scheduler completion order is not evidence. Cleanup executes exactly once in LIFO region order and cannot be skipped by return, throw, break, cancellation or suspension. Cleanup failures are then appended in their actual deterministic LIFO execution order according to the suppression law and never reorder an already selected primary outcome.

### Scope cancellation plans

`CleanupScopePlan.scope_cancellation_plan` lowers through `HM-LR-TOP-021` and
threads one linear `CANCELLATION` state through the cleanup region. `INHERIT`
adds no observation boundary, `OBSERVE` admits the ordinary cancellation point,
and `DEFER_TO_OUTERMOST_SHIELD_EXIT` emits ordered `shield_enter`, optional
`observation_deferred`, exact-once `scope_cleanup_complete`, and `shield_exit`
events. An inner shield never observes while its parent remains active. After
the outermost cleanup and exit, a still-selected cancellation emits exactly one
`cancel_observe` followed by one `cancel_acknowledge`; a selected Error or
Defect follows the bound failure-precedence plan instead. Lowering may neither
reselect the source mode nor introduce a backend-specific shield operation.

Cleanup-budget checking is completed before verified MIR. Canonical HIR binds
each construction lifecycle plan to one `CleanupBudgetId`; the module table
retains declaration mode, family-root identity, normalized effective error and
effect rows, ordered compiler-local base/field/hook contributions, and their
subset proofs. The HIR-to-MIR verifier recomputes both unions and rejects a
forged envelope, missing contribution, widened child, unresolved identity, or
digest mismatch.

Verified MIR carries the normalized envelope table and references its existing
`cleanup_budget_id` from construction-lifecycle payloads. No cleanup-budget
evaluation, branch, or new MIR operation is introduced. Existing cleanup
operations preserve the closed live-object order (hook, reverse-acquisition
fields, recursive base) and construction-abort order (live fields, committed
base, no whole-object hook). A budget neither authorizes an effect nor changes
which failure is primary or suppressed. xVM and Cranelift consume only the
already-verified lifecycle operations; backend policy cannot reinterpret the
envelope.

## 6. Option coalescing and lazy evaluation

For `lhs ?: fallback`, `lhs` is evaluated first. When it is `some(v)`, `v` is returned and `fallback` is not evaluated. Only `none` evaluates the fallback. Ownership extraction follows the Option payload law. This short-circuit rule is a backend-visible observation.

`let#lazy` evaluates at first force, publishes exactly one immutable committed value, and reuses the cached result. Reentrant force is rejected. It does not silently retry an effect or hide an error channel.

## 7. Actors and messages

Actor Protocol binding is completed before MIR. Each admitted transport plan
carries exact `ActorProtocolConformanceId`, `ActorProtocolRequirementId`,
`ActorProtocolBindingId`, and `ActorHandlerId` or `ActorRequestId` residue.
MIR performs no selector-string, provider, registration-order, or fallback
lookup. A `send` binding always targets `on`; a `request` binding always targets
`request`. The bound implementation ErrorSet and EffectRow have already been
proven subsets of the requirement rows, and a one-way send/on binding always
has an empty recoverable ErrorSet. A fallible acknowledged command therefore
enters MIR as a request returning Unit with its ErrorSet preserved in the
correlated `ReplyResponsibility`.

The cross-module projection adds `ActorProtocolBindingTableId` without
replacing that R41 tuple. Every selected MIR row therefore carries the table,
conformance, requirement, stable binding, typed handler-or-request,
`ResponsibilityId`, and binding-row digest together. The binding ID remains
stable across a content-only implementation rebind; the row and table digests
change. A send/on row has an empty implementation ErrorSet and no reply
responsibility digest. A request/request row carries the exact static
`ReplyResponsibility` digest. Admission errors, Cancellation, Defect, concrete
`ReplyId`, concrete `CorrelationId`, and runtime Actor instance identities do
not enter module API binding rows.

`MODULE_API` is the byte-identical common/public filter of
`MODULE_IMPLEMENTATION`; present `[]` is the unique empty encoding in the
binding profile. Link input verifies the receipt-bound typed-HIR proof and one
compiled symbol for each implementation identity. An executable union is
owned by `ExecutableImageId` and retains one exact origin receipt for every
table. xVM or Cranelift may derive a backend-private slot or address only after
this verification. Neither backend may replace the semantic identities,
reselect a handler, widen visibility, or use selector, registration, import,
or link order.

Actor isolation is explicit. One ActorId owns one isolated StateRegionId and MailboxId; one admitted ActorTurnId has mutation authority at a time, including across its suspension. Suspend/resume preserves that same turn identity and does not release dequeue or mutation authority. A statically proven self/dependency-cycle request await is rejected before MIR rather than represented as implicit reentrancy. The exact FIFO key is `(SenderId, ReceiverActorId, MailboxProfileId)`; `ChannelId` is derived from that tuple rather than adding another ordering component. Each successful enqueue commit allocates the next strictly increasing `channel_sequence`, and dequeue preserves that order. No rejected attempt has a `channel_sequence`. No global order or fairness is implied.

Actor transport is not a method call. The Stable `:~` surface selects one
`ActorTransport` plan before MIR; it has no ordinary-message or method fallback.
Prepare-send evaluates the receiver and every `CallArgument` left-to-right
exactly once without transferring ownership, binds the selected formals, proves
transfer/isolation, and stages one compiler-internal envelope. A trailing
closure crossing actor isolation is admitted only when its capture environment
independently satisfies transfer, suspension, effect, error, and cleanup rules.
The absence of a mailbox clause binds `logical_unbounded_v1`; positive static
`#mailbox(capacity: N)` binds `bounded_reject_v1`. The bounded profile never
blocks, retries, suspends, or drops. All failures before commit retain every
sender owner and allocate neither envelope nor sequence. Admission commits
exactly one envelope, one ownership transition, and one sequence. A one-way
commit returns `Result::ok(Unit)`; a request commit creates one CorrelationId and
ReplyId and returns `Result::ok(Reply<T>)` plus its non-forgeable
`ReplyResponsibility` descriptor. The descriptor preserves normalized result
type, handler ErrorSet, cancellation axis, isolation owner, ReplyId,
CorrelationId, and terminal transport failure. `:~` itself never suspends or retries; source
extracts an admitted reply handle and then awaits it explicitly once. If `on` and
`request` share one selector and canonical call shape, the declaration or link
is rejected before MIR. Actor transport is forbidden in `defer`. Await restores
exactly the normalized handler ErrorSet plus
`ActorMessageError::receiverClosedBeforeReply`; it does not infer them from the
nominal `Reply<T>` spelling. A reply handle never converts to `Run<T>` and no
spawned run carries an actor transport descriptor. Exactly one correlated
reply/failure/cancellation
terminal event is admitted. Distributed and exactly-once delivery events have
no current MIR identity.

The cancellation race is phase-split by enqueue commit. Observation before commit emits the cancellation outcome, aborts admission, retains sender ownership, and allocates no `channel_sequence`; it is not converted into `ActorMessageError`. Observation after commit cannot retract or renumber the message, restore a moved sender place, or rewrite the already produced admission Result. For an admitted request it affects only the correlation-bound reply lifecycle under the existing cancellation law.

One non-forgeable internal `ActorRuntimeRootOwnerId` owns the terminal
lifecycle observation of each Actor incarnation. Static `ActorId` remains the
source declaration and R23 binding-table identity; one runtime incarnation has
a distinct internal `ActorInstanceId`. The provisional instance may exist
during creation, but no `ActorRef` capability exists before
`actor_publish_committed`. MIR orders `create_prepare`, state initialization,
mailbox initialization, and publication; publication happens-before external
prepare-send or enqueue through that reference. A prepublication failure emits
no ActorRef, enters `CREATION_ABORTED`, rolls back only initialized resources
exactly once in reverse initialization order, and reports one `FailureId` to
the root owner. `supervisor_id` remains null.

Normal stop is `DRAIN_ALL_COMMITTED_V1`. Its observable barriers are
`stop_requested -> admission_closed -> drain_started -> drain_completed ->
actor_state_cleanup_completed -> root_owner_observed ->
termination_published`. The drain set is exactly the envelopes whose enqueue
committed before admission closure. An indefinitely suspended active turn keeps
stop pending with its exact `ContinuationReceiptId`, continuation-interface
digest, state-region authority, managed roots, loans and cleanup tokens; it
emits no implicit resume, cancel, cancellation, cleanup, root observation,
reply or termination.

An uncaught Defect is `STOP_AND_FAIL_PENDING_V1`. After `defect_observed`, no
queued `turn_start` is legal. Admission closes; queued payloads, the active turn,
and Actor state clean exactly once before a still-open Reply becomes observably
terminal through `ActorMessageError::receiverClosedBeforeReply`. Every active
loan ends first through the existing infallible `LOAN_END`; deferred, capture
and owner cleanup tokens discharge exactly once within the enclosing cleanup
event. A reply already terminal before the Defect remains terminal and is not
duplicated. The primary `DefectId` is never replaced; cleanup Defects are
suppressed in contiguous reverse-cleanup execution order. Before the root owner
observes that outcome, each actor-owned managed `RootId` has one exact
transfer-or-removal receipt. `ActorRuntimeRootOwnerId` and managed `RootId`
remain disjoint identity domains, and termination is published last.

MIR preserves lifecycle policy and state transition, conditional cleanup sets,
reply-terminal counts and the complete R41/R23 selection residue:
`ActorProtocolBindingTableId`, `ActorProtocolBindingId`, the typed
`ActorHandlerId` or `ActorRequestId`, `ResponsibilityId`, and
`binding_row_sha256`. These fields resolve one already verified selection;
lifecycle processing performs no lookup, creation, reselection or digest
mutation. xVM and runtime own policy execution. Cranelift and the single typed
runtime ABI preserve the barriers but cannot choose policy, add a second ABI,
absorb R24 code-generation lifetime, or reorder observable events. A lifecycle
helper not present in the exact typed helper allowlist requires an explicit
registry and runtime-ABI digest rebind before admission.

`concur` regions record `ConcurId`, their owner `ExecutionId`, ordered
`ConcurRunId` children, cancellation state, and cleanup barrier. A region exit
joins every admitted run; no detached-run event is current. `spawn` first
evaluates its operand once and admits either an inline run body or one statically
selected async invocation. It then creates one `ConcurRunId` and returns one
owner-bound `Run<T>` without synthesizing a forwarding closure, forwarding
`await`, or nested run. `await` of a bare async invocation executes in the
current `ExecutionId`; `await Run<T>` or `await Reply<T>` consumes the
corresponding one-shot observation handle. Run spawn, async suspend/resume,
cancellation request/observe/acknowledge, run failure, terminal join, and
concur-exit events retain `FailureId` and lexical `spawn_index` so xVM and Cranelift
can reproduce the same primary/suppressed outcome.

A concur-local `#async` lambda retains its owning `ConcurId` and exact
environment plan in typed HIR and MIR. The initial Stable profile is
nonescaping and admits only an empty environment or an explicit reusable
copy-only capture plan; borrow, inout, move, clone, deep, scoped-access,
actor-isolated-reference, outward storage/export, and sibling transfer are
rejected before MIR. Its invocation may be consumed only by a local `await`,
local `spawn`, or an inward nested concur whose owner chain proves the same
residence. General escaping async-lambda events have no current MIR identity.

### 7.1 Continuation-frame machine

Suspension lowering consumes the verified
`ContinuationFramePlan` associated with the HIR `SuspendPlan`. The plan carries
only semantic identities and responsibility partitions; it contains no stack
offset, object layout, machine address, XBC slot, CLIF value or ABI decision.
`Xvm`, `ObjectAot` and `InMemoryJit` must consume the same plan, typed
continuation receipt and transition digest. `InMemoryJit` additionally binds
the exact image-generation identity and continuation lease; no code address is
a semantic identity.

The closed frame states are `RUNNING`, `SUSPENDED`, `CLEANING`,
`TERMINAL_COMPLETED`, `TERMINAL_FAILED` and `TERMINAL_CANCELLED`. A suspension
visit owns a separate epoch in `PREPARING`, `COMMITTED`, `RESUME_WON`,
`CANCEL_WON` or `DISCHARGED`. The admitted semantic operation family is:

1. `FRAME_CREATE`: create one running frame for an invocation;
2. `FRAME_SUSPEND_COMMIT`: atomically install the exact owner, admitted-loan,
   cleanup-token and retained-authority partition, bijectively rebind managed
   roots to fresh destination storage locations, publish one receipt and commit
   a fresh epoch;
3. `FRAME_RESUME_COMMIT`: win the epoch once, restore the exact partition and
   discharge the epoch;
4. `FRAME_CANCEL_COMMIT`: win the epoch once, retain the partition and enter
   cleanup;
5. `FRAME_CLEANUP_STEP`: discharge the next exact cleanup token in the
   prescribed order;
6. `FRAME_TERMINATE`: enter exactly one terminal state with zero owner, loan,
   cleanup-token, root, frame-slot and actor-authority balance.

`SUSPEND` and `CANCEL_CHECK` remain control-flow forms; they do not replace the
six responsibility operations. Each operation has its own closed payload shape;
nullable fields cannot encode a different operation's transition. The verifier
rejects a missing, duplicated or partially transferred
owner/loan/token/authority identity, a non-bijective root rebind, an
inadmissible state or epoch
transition, a stale or second race winner, a cleanup-order or balance error,
and any root-set disagreement. The corresponding verifier diagnostics are
`CONTINUATION_FRAME_OWNER_PARTITION_INVALID`,
`CONTINUATION_FRAME_TRANSITION_INVALID`,
`CONTINUATION_FRAME_CLEANUP_BALANCE_INVALID` and
`CONTINUATION_FRAME_ROOT_SET_INVALID`.

The generic frame machine treats actor delivery, mailbox, stop and supervision
state as out of scope. It may retain only the closed `ACTOR_TURN` scope with
`STATE_REGION_MUTATION` and `DEQUEUE` authority; it creates no actor lifecycle
authority and carries no actor-state loan. Resume and cancel re-enter generated
code only through the internal typed dispatcher after exact interface, receipt,
epoch and operation validation. This is distinct from—and grants no authority
to—an arbitrary runtime callback. Backend allocation and storage coalescing
occur only after the semantic partition and transition sequence have been
verified.

## 8. Objects, evidence and construction

Nominal dispatch, Trait evidence, extension resolution, construction and materialization lower to explicit MIR identities. Runtime strings and Map keys never become static labels or witnesses. Tooling certificates and provider-derive sidecars are consumed before ordinary source checking and never become execution authority.

One immutable Map literal lowers through `MapLiteralPlan`: direct entries and
unfolded Map sources evaluate left-to-right once, later equal keys replace
earlier values, displaced owners clean once, and publication occurs only after
the complete plan succeeds. A failure before publication emits reverse cleanup
for acquired temporaries and no partial Map result. Runtime Map unfold remains
distinct from static-label call unfold.

## 9. Dynamic providers

A dynamic unit conversion MIR event exists only after stdlib profile, provider and policy checks. It records provider identity/version, observation timestamp, rounding and failure/effect policy, cache key and replay token. No source Preview gate activates this event.

## 9.1 HIR-H1 verification boundary

The only admitted high-level input is
`ExecutableHirH1(Verified<CanonicalHirH1>, MirCapabilityReceiptR1)`.
`HirSkeleton`, `CheckSession`, and `TypedHirDraft` are analysis states and
cannot lower. Canonical HIR contains no recovery node, unresolved type/name,
candidate set, generic operator, deferred witness, or missing responsibility.
The verifier recomputes selected declarations, substitutions, conformances,
intrinsics and result types and binds deterministic semantic/API/debug
projections. MIR lowering expands that closed structure into control flow,
places and outcomes; it performs no lookup or semantic choice.

This bridge is backend-neutral. It does not activate the noncanonical MIR-X1
xVM-only proposal and does not change the current backend set.

## Compile-time module initialization and resolver seal

Package dependency, re-export, module-header, and static-binding dependency
graphs are frontend proof objects and create no runtime graph traversal. Package
dependencies and re-exports are acyclic. A module-header SCC is admitted only
after complete header collection and only for module-header, type-declaration,
and signature references; a static-value, runtime-initializer, or re-export edge
inside it is rejected before MIR.

An admitted immutable module static-binding graph is acyclic and evaluated at
compile time. All values publish in one atomic semantic commit only after every
initializer succeeds, and its deterministic receipt orders entries by canonical
`DeclId`. Its MIR runtime-initializer count is exactly zero. A failed
initializer or dependency cycle emits a static diagnostic and produces no
module initializer, partial global state, cleanup obligation, or backend symbol.
This is distinct from a function's current `static { ... }` first-call
activation, which retains the owner-bound runtime state machine specified in
§2.1.

The resolver-to-HIR seal may hand onward only:

- a closed noncall `ResolvedRef`;
- `NameResolutionTrace`, `ImportBindingTrace`, and `VisibilityProof` as
  compile-time provenance;
- an already selected `EvidenceOriginId` where another current contract
  supplied Trait evidence.

`ImportBindingId`, `ResolverScopeId`, `SourceOriginId`, and
`ActivationOriginId` do not become runtime values. An import target is
`ModuleId` in the `MODULE` namespace and `DeclId` in the other R4 name
namespaces. A module target has no expression-HIR projection; a declaration
used as an expression projects to `ResolvedRef::DirectDecl(DeclId)`.

The R4 import/activation provider pair
`(provider_binding_id_or_self, provider_module_id)` is compile-time
provenance, not a dynamic-provider MIR value. `self` means same package, not
same module. For the nearest consumer `TargetId`, every used pair matches
exactly one package-graph visible-module binding, and the dependency
subreceipt contains exactly the unique used pairs after excluding only the
consumer module itself. A same-package, different-module provider therefore
remains required with binding `self`. A missing, extra, stale, or graph-unbound
pair rejects before this seal and creates no provider lookup, event, or
backend repair route.

`ResolvedOverloadSetRef` is analysis-HIR-only and cannot enter
`ExecutableHirH1` or MIR. `OrdinaryCallSelectionV1` seals one exact declaration,
`CallableImplementationId`, complete `SubstitutionId`, canonical call shape,
candidate-set/argument-descriptor digests, and specificity proof before HIR
handoff. MIR must not rank applicability or specificity, choose by
expected/result type, infer a row, merge lexical overload sets, or perform
name/member/extension/witness lookup.

Call selection is a static, nonexecuting proof. Runtime evaluates the selected
callee or receiver and explicit arguments left-to-right only after the seal,
then evaluates omitted defaults of the selected declaration in formal order.
No unselected default, closure body, candidate body, or candidate-local
temporary is evaluated. xVM and Cranelift consume the same sealed selection
identity and have no fallback or re-ranking path.

For an ordinary selector with a nonempty nominal set and a nonempty active
extension set, the frontend emits `MEMBER_EXTENSION_COLLISION` and produces no
selected reference or MIR. Exact qualified extension selection restricts the
domain before the seal. Import, `use`, declaration, traversal, and source order
cannot affect the result.

The module-compilation handoff keeps three hash domains distinct. The module
interface digest contains only exact effective public semantic residue. The
module implementation digest contains private verified-HIR semantics and binds
that interface digest. The full compilation receipt closes target/module
identity, package graph, source-contribution provenance, dependency subreceipt,
resolver trace, visibility closure, initialization plan, interface, and
implementation hashes. Source path/origin/proof records and private body bytes
never enter the public interface preimage. A stale dependency-interface digest
is rejected before lowering. Private-body changes that preserve public residue
leave the interface digest unchanged while changing implementation and full
receipt identities. No backend link or load order can repair a failed seal.
Every one of these JSON artifact hashes uses
`DEEPLUS_CANONICAL_JSON_UTF8_SHA256_V1`; interface, implementation, and full
compilation hashes remain separate identity domains even when they use the
same canonical byte algorithm.

This design contract adds no production MIR implementation or execution
receipt. The exact 22 feature P1 items remain OPEN and all 15 product lanes
remain `NOT_RUN`.

## 10. xVM and Cranelift preservation

The Rust xVM bytecode interpreter is the first development, validation and REPL
execution path. Cranelift `ObjectModule` AOT is the first native path and
Cranelift `JITModule` is the in-memory native path. Both consume the same
verified-MIR-to-CLIF lowering and differ only in finalization, linking and code
lifetime. Differential conformance compares ordered observable event traces,
final value or failure, place/cleanup balance, provider replay identity,
cancellation/suspension and actor/concur ordering. A design-static PASS in this
package is not such a receipt.

CLIF is backend-private. Its values, blocks, stack slots, signatures, function
references, relocations, registers and native addresses never become HIR or MIR
semantic identity. Module-local function/data IDs and symbol spellings are
linked to Deeplus static identities only through a digest-bound sidecar; link,
load or lookup order cannot select a declaration, witness, provider or call.

Every native projection receipt binds the MIR semantic digest, target triple,
ISA and settings, Cranelift family and lockfile identity, module kind, pointer
width, endianness, object/code/relocation model, calling convention, runtime ABI
digest, optimization settings and runtime-helper/safepoint capability. Object
mode additionally binds object bytes, object format, linker identity and final
artifact. JIT mode binds the import allowlist, resolved import map, executable
memory policy, finalized image and retirement lifetime. Host defaults cannot
supply any omitted input.

Error, Defect, Cancellation, suspension and cleanup remain explicit MIR
outcomes and edges. They cannot be replaced by native exceptions, personality
routines, host unwind or an arbitrary backend trap. A Cranelift trap is
admitted only when it implements an already selected terminal Defect or a
verifier-proven unreachable site, and the trap-to-`DefectId` map is receipt
bound. Checked arithmetic preserves its explicit success/`ArithmeticDefect`
boundary. Missing stack-map or stable-handle capability for a live managed
reference blocks native lowering rather than inventing a layout.

Phase-1 managed references use
`STW_NONMOVING_TRACING_WITH_OPAQUE_STABLE_HANDLES_R1`. The backend-neutral
companion `deeplus.managed-memory-plan/r1` binds the exact MIR digest, trace
descriptors, safepoints, logical root maps, allocation plans, interior
projections and suspension root transfers. It is deterministically recomputed;
a matching claimed digest alone is insufficient.
The plan and every native projection receipt bind the exact integrated
`IR-OWN-P0-017` continuation-root interface digest. Until that digest exists,
R36 remains an approved local candidate and cannot pass canonical promotion.

The collector is cooperative stop-the-world, nonmoving, nongenerational and
nonconcurrent. It has no weak-reference, finalizer, resurrection or pinning
surface and never performs MIR cleanup or cancellation. Allocation fast paths
cannot collect. A slow allocation path uses an explicit `INVOKE` whose exact
call plan selects the sealed `managed.allocate_slow` helper and preserves the
existing `AllocationError effects allocate`; precommit failure cancels its
reservation, restores the input owner, reverse-cleans staged resources and
publishes nothing.

The closed safepoint set consists of non-tail `INVOKE`, managed-allocation
slow-path `INVOKE`, post-transfer `SUSPEND`, `CANCEL_CHECK`, runtime-entry `RUN_OP`,
`ACTOR_OP`, `PROVIDER_OP`, `ONCE_OP` and `SYNC_OP`, CFG backedges, and an FFI
transition after root publication. No backend-private implicit safepoint is
admitted. At each site the declared roots are the sorted unique union of
pairwise-disjoint running, continuation-frame and runtime roots. Root identity
denotes a live storage location, not an object, so two locations that contain
one handle remain two roots. The receipt is published before operation entry
and lives through outcome commit.

An interior projection is a stable handle plus semantic `ProjectionId`. A raw
address may exist only in a verified no-collect region and cannot cross a call,
safepoint, suspension, actor boundary or FFI. JIT image retirement requires
unpublished state plus zero active activations, suspended continuations and
outstanding root receipts. xVM, Object AOT and JIT compare logical safepoint,
root-owner, ownership, cleanup and outcome traces; target addresses, heap
layout, collection timing and stack offsets are excluded.

The R69 successor seam separates the compile-time managed-memory plan from an
execution-time managed-root receipt. Static root-map templates contain logical
storage-location `RootId` and trace-descriptor bindings, never a runtime handle
generation or receipt lifecycle. At an executed safepoint the runtime receipt
checks exact generations, is published before the may-collect entry, remains
live through MIR outcome commit, and is then released. The current continuation
interface digest is `2ccf2acd...c8b4`; predecessor `0dc489...1271` pointers do
not select successor semantics. `RegionId` and `LoanId` remain verifier
identities: a managed root neither creates nor extends a loan.

Source locations and `DebugOrigin` project through a separate nonsemantic debug
digest. Debug info, unwind tables and profiler metadata do not change program
meaning and remain unsupported until a target-bound receipt exists.

### Internal runtime ABI R1

Every generated-code/runtime crossing uses the backend-neutral logical identity
`DEEPLUS_INTERNAL_RUNTIME_ABI_R1`. Its canonical manifest, closed helper
registry, target projection and artifact-binding receipt are defined by
`spec/contracts/internal-runtime-abi-r1.json`. A matching-looking symbol name,
table index, native address, link order or host default is not ABI evidence.
R1 admits only exact ABI ID and full-digest equality.

Fixed primitive scalars use direct channels. Every aggregate, nominal value,
closure, collection, `Option`, `Result`, Rational, Complex and unrecognized
opaque value crosses through an indirect typed slot. A normal aggregate result
uses the caller-owned normal slot as sret. A one-field or zero-sized nominal
does not collapse to a scalar, and an aggregate is never split across target
registers at this boundary. Borrow and `inout` addresses are call-bounded target
coordinates: they neither escape nor become semantic identities.

The dispatcher returns the closed union `COMPLETE(OutcomeTag) |
PARKED(ContinuationReceiptId)`. A completed call carries exactly one `U8`
outcome tag: `NORMAL = 0`, `ERROR = 1`, `DEFECT = 2`, or `CANCELLATION = 3`.
The caller supplies four disjoint typed slots and only the selected completed-
call slot commits. `Unit` has no normal payload and `Never` cannot return.
Suspension is not a fifth outcome: `PARKED` commits no outcome tag, no outcome
slot and no MIR successor. It transfers committed owners, active loans,
cleanup tokens and roots exactly once to one continuation receipt, leaving zero
source residual; those loans end only at the resumed or cancelled terminal
edge.

Argument evaluation, acquisition, ABI/signature verification, slot preparation
and root publication precede one atomic `ownership_commit`, which immediately
precedes callee entry. Pre-entry failure cancels reservations and retains the
caller owner. After entry, Normal, Error, Defect and Cancellation never restore
transferred input ownership. Completed-call loans end and cleanup runs on the
explicit MIR edges; parked state remains owned by the continuation receipt.
Native exceptions and host unwind cannot cross this boundary; violation
is `RUNTIME_ABI_HOST_UNWIND_FORBIDDEN`.

The helper registry declares exactly the 22 runtime-bound base operations
already named by `CANCEL_CHECK`, `SUSPEND`, `RUN_OP`, `ACTOR_OP`,
`PROVIDER_OP`, `ONCE_OP` and `SYNC_OP`. Ordinary user calls and checked
arithmetic are not helpers. The six suspending rows bind the exact
`IR-OWN-P0-017` continuation-interface digest and remain part of those 22 base
operations. Three managed-memory helpers are conditionally admitted by the
exact `IR-OWN-P1-025` managed-reference profile digest, producing 25 active
helpers in this fused design contract. Function-static ensure, lazy force and
scoped mutex acquire are synchronous COMPLETE-only helpers; they may block a
host thread but never manufacture semantic PARKED. Both dependency fields are
exactly bound; a missing, stale, or substituted digest fails closed.

xVM binds typed helper-table entries. Object AOT binds an exact symbol sidecar
and linker receipt. JIT binds an exact import allowlist, resolved
signature/provider map, immutable image-generation identity and retirement
receipt. An image can retire only after it is unpublished and all active-call
and suspended-continuation leases are zero. External FFI and runtime-to-generated
callbacks are not part of R1.
## 11. Elaboration and evaluation preservation

Field puns and grouped forwarding are eliminated before MIR while preserving source-order evaluation and static identities. A scoped import/use group changes only compile-time resolution. Multiline String dedent is completed by the scanner before `ConstString`; interpolation segments retain ordinary left-to-right evaluation.

Postfix NumericArray transpose lowers to one semantic nonowning,
owner-bounded readonly coordinate view. It swaps the two rank-two logical axes
or flips an admitted rank-one orientation witness, preserves one-based
coordinate provenance and source lifetime, and authorizes no implicit element
copy, language-observable allocation, mutation, adjoint, shareability
inference, or isolation crossing. Backend representation and incidental
storage strategy remain unselected.

A Pattern owner lowers to exactly one logical `PatternAttempt`. The attempt
emits `subject_evaluate` once, then `subject_acquire`, `test_plan_build`, a pure
nonconsuming `structural_test`, read-only nonescaping `probe_bind` events, zero
or one `guard_evaluate`, exactly one `atomic_commit` after final guarded
success, `final_bind`, `body`, and `exit_or_join`. The optional guard has type
`Bool`, is pure, runs once only after structural success, and may read probe
binders without moving, escaping, suspending, mutating through, or acquiring a
loan, view, or authority from them.

Every child pattern-row `BINDING_COMMIT` entry is a compositional commit
requirement accumulated by the enclosing `PatternAttempt`. All such entries
collapse into its single top-level `atomic_commit`; they are not nested or
multiple executable commits. An Or probe chooses the first source-ordered
branch whose structural probe succeeds, requires the exact same normalized
binder interface `(name, canonical type, ownership mode, mutability, usable
region, capability set)` on every branch, and performs no retry or backtracking.
A false owner guard after that selection does not try another Or branch. An
Alias probe preserves the same subject identity, performs no clone, and stages
a shared-borrow requirement. The loan begins only on final success and cannot
coexist with a moved or exclusively borrowed descendant. A borrowed subject
cannot execute a `PK-MOVE` affine-payload extraction.

A structural mismatch terminates after `structural_test`; a false guard
terminates after `guard_evaluate`. Neither publishes bindings, moves, loans,
views, or authority, and neither leaves final binders. For pattern-control
owners the context-bound disposition is exact: `if let` takes the false
branch, `while let` exits the loop, and `for let` skips the current candidate.
Guarded-binding failure transfers to its required `else`; assertive binding
emits one `PatternMatchDefect`; ordered catch continues to the next handler or
propagates. Each phase carries the exact DPM fixture identity and attempt
disposition. Every failed preparation edge executes `MOVE_CANCEL` for each
reservation and leaves no loan. On success, admitted `PLACE_MOVE` and
`LOAN_BEGIN_SHARED` operations complete before one infallible group
`BINDING_COMMIT` publishes final binders. The resulting loan is closed at the
earliest invalidating mutation, move, replacement, cleanup, or region frontier.
A place join first proves compatible place identities and ownership states for
all normally returning arms, excludes divergent arms, and only then intersects
capabilities. A failed proof emits `PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH`.

Match usefulness and exhaustiveness are checker-only admission judgments and
create no HIR or MIR node, opcode, runtime branch, or witness object. Rejected
source produces no MIR. After admission, lowering receives only the established
source-ordered structural-test and guard plan. Clause heads reuse that same
static partition analysis, but their clause-owner overlap, input-supply, and
return-totality obligations are discharged before an admitted ordered clause
plan reaches lowering; no runtime clause search repairs a rejected partition.

Enum body-mode commitment and match fallback-head commitment are likewise
parser/checker-only. MIR receives a nonempty sealed Enum case vector and an
already validated arm plan. There is no empty-Enum opcode, fallback-guard field,
commitment opcode, runtime mode lookup, or recovery residue.

Tuple Pattern lowering is an exact static product projection. Record/Map
patterns first compare their exact or explicitly open row/key shapes; nominal
patterns require one statically selected pattern-transparent descriptor. Pin,
range and relational patterns receive a closed strong equality/order
descriptor before MIR and invoke no getter, provider, reflection or dynamic
extractor. A parameter's leading channel value is acquired by ordinary call
lowering before its checker-proven irrefutable decomposition plan runs at body
entry; the plan adds no call argument, overload key, ABI field or failure edge.

For a List positional rest, the frontend supplies one closed
`SequenceDecompositionDescriptorV1`. MIR evaluates length and the needed
front/back projections once over ordinal ranks, then builds only an ephemeral
probe-rest for guard observation. Successful final commit publishes the exact
descriptor result. A borrowed result is `ListRestView<T>` carrying
`SourceOwnerId`, `BorrowRegionId`, `RankSpan(start_rank,count)`, original
logical-coordinate projection, and an explicit intrinsic `Sequence<T>`
witness. `count = 0` represents an empty residual without constructing an
invalid source Range. The view never rebases, allocates, copies, retains a
temporary owner or escapes its source. Existing `ReadonlyView<T>` receives no
Sequence witness, and conformance alone cannot synthesize a descriptor.

Bare comma return type/value/binding surfaces disappear before MIR as the
existing TupleType/TupleExpr/TuplePattern identity. They do not create a comma
operator, ValuePack, Sequence return carrier or multiple-result ABI. A
direct-local parallel or structural assignment resolves only static distinct
mutable `LocalPlaceId`s, evaluates and stages the complete RHS left-to-right
once, validates arity/ownership/overlap before any write, then emits exactly one
`replace_group_commit` and returns Unit. A precommit failure emits zero target
writes; this is failure-atomic logical publication, not hardware or
cross-thread atomicity.


## 12. Removed-surface MIR boundary

Map indexing lowers through the ordinary index/API contract; dot member selection never becomes a runtime key lookup. Explicit assignments lower through the single-place transaction in §2; there is no increment/decrement MIR opcode. Recursive calls remain ordinary calls and carry no tail-recursion source contract. Regex construction is a library call from `String` or `Bytes`, not a literal MIR constant kind. An explicitly expected List union lowers the declared element type and injections; MIR never receives an automatically inferred heterogeneous List union. Arbitrary custom operator declarations and fixed-glyph conformance attempts outside the exact 13 unary, arithmetic, equality, and ordering roles create no MIR operation; admitted fixed-glyph calls use the sealed node defined in §2. `!=` and the four ordering glyphs preserve the selected `Eq`/`Ord` evidence identity, compound assignment creates no independent witness, and range never becomes an operator hook. `...` is the one-sided Range delimiter, while `..` and `..<` are the closed and half-open two-sided forms; repeated positional residue and comprehension unfold use their owner-bound `..`/`*` spellings and cannot be reinterpreted as Range. Rejected `..>` and empty `[]` create no MIR.

Built-in indexing evaluates the owner and each index once, left-to-right, then validates the declared logical domain before projecting storage. `List`, `String`, and `Bytes` use `1..length` with offset `index - 1`; an explicitly bounded List retains `L..U`. Every `ReadonlyView` carries its source owner's declared logical domain, coordinate-to-storage mapping, and provenance, so no view construction independently rebases it. A missing Map key emits `IndexError::keyNotFound`; any type-correct dynamic built-in positional or NumericArray coordinate outside its logical domain emits `IndexError::outOfLogicalDomain`. Both are precommit failures. Map uses the exact key type; tuple ordinals and Record labels are resolved before MIR and never become dynamic bracket lookup. Conformance to `Sequence`, `Indexable`, or `LogicalIndexDomain` does not add a lowering route.

An ordinary slice carrier accepts exactly one range selector, including the open forms `..<j`, `..j`, `i..`, and `..`. A rank-complete NumericArray coordinate list uses comma-separated axes, preserves typed axis identity, and gives every built-in default source-visible axis the domain `1..dimension`. NumericArray alone admits multiple axes and full-axis `*`; every scalar selector removes exactly its selected result axis, while range and full-axis selectors preserve theirs. Slice lowering first evaluates and validates every scalar/range/full-axis selector, including `^`/`$` anchor resolution, without mutating the owner. An omitted lower or upper endpoint is the corresponding owner-domain boundary identity, not an invented numeric sentinel. Success creates one readonly view carrying the source owner region, provenance, and selected logical coordinates. There is no implicit rebase, hidden copy, mutable slice assignment, isolation crossing, gather/linear-index fallback, or owner-lifetime escape. A named explicit rebase/copy call is an ordinary visible operation with its own allocation and ownership observations.

### 12.1 R77 integrated surface lowering boundary

Core-owned Trait language roles are static metadata identified by
`TraitLanguageRoleId`; they do not create runtime lookup, a new witness kind, or
a new MIR operation. In particular, `trait#operator` classifies only the closed
thirteen-glyph conformance law and cannot select or widen that glyph set.

Guarded binding lowers `Failable::branch(move source)` through the statically
selected `TraitWitness` call with the exact signature
`def ::branch(move source: Self) -> BindingBranch<Success, Failure> throws Never effects {}`.
MIR branches over the returned `BindingBranch`; only the success arm performs
the existing binding commit. The failure arm binds the typed failure payload and
executes the explicit exit. There is no runtime protocol search, hidden fallback,
or Failable-specific MIR opcode.

Each admitted `MutableList` structural edit lowers as an ordinary direct call
selected in `CallExpr`/`ResolvedCallPlan` and bound to one
`CallableImplementationId`. The closed operation set is `insertBefore`,
`insertAfter`, `prepend`, `append`, `insertAllBefore`, `insertAllAfter`,
`prependAll`, `appendAll`, `removeAt`, `removeRange`, `removeSelected`,
`popFirst`, and `popLast`. Selection consumes no result context, performs no
hidden copy, and adds no opcode; each successful operation publishes exactly one
structural commit after all validation and element acquisition succeeds.


## 13. R51f3 tooling/profile observability

Pattern compilation is an ordinary library call whose engine identity, version, flags, Unicode mode and budget are explicit observables. Tail-call analysis and xVM agents emit side receipts only; removing either tool cannot alter program observations. UML state-machine generation is complete before ordinary Rust frontend checking and therefore adds no MIR event. Product execution for all four contracts is `NOT_RUN`.

## 14. Normative document-consistency product-handoff dispositions

This section classifies the frozen required 20-feature audit set without changing any feature's design status. It is a product-handoff boundary, not an implementation design. All product lanes remain `NOT_RUN`.

| Feature ID | MIR disposition | Authority/boundary |
|---|---|---|
| `named_rest_parameter_record_msp` | `LAW_PRESENT` | §§2 and 8 bind the named-rest channel and static-label supply. |
| `schema_named_unfolding` | `GENERIC_LAW_PRESENT` | §§8 and 11 bind pre-MIR unfolding and materialization identity. |
| `unicode_char_literal_single_quote_msp` | `LAW_PRESENT` | §4 binds one Unicode scalar without selecting a backend representation. |
| `char_unicode_scalar_value_model` | `LAW_PRESENT` | §4 separates Char, String scalar, Bytes, UTF-16 and grapheme domains. |
| `strict_boolean_word_operators_msp` | `LAW_PRESENT` | §2 binds strict left-to-right two-operand evaluation. |
| `sequential_boolean_control_words_msp` | `LAW_PRESENT` | §2 binds short-circuit right-operand suppression. |
| `standalone_bang_not_current_not_word_law` | `NO_DISTINCT_MIR_OP` | This is a frontend spelling boundary and authorizes no standalone Boolean `!` operation. |
| `rightward_flow_dollar_local_binding_msp` | `LAW_PRESENT` | §3 binds normalization to ordinary local binding and no distinct MIR operation. |
| `optional_chaining_not_current_law` | `NOT_APPLICABLE(rejected current surface)` | Rejected source creates no MIR event under §12. |
| `ternary_conditional_expression` | `LAW_PRESENT` | §2 binds condition-once, one lazy arm and the responsibility join. |
| `ternary_short_expression_stable_profile` | `LAW_PRESENT` | The short spelling uses the same §2 law; formatter guidance adds no semantic route. |
| `at_control_expression_family` | `GENERIC_LAW_PRESENT` | §§1, 2, and 11 supply generic ordered control-flow observations. |
| `local_value_body_msp` | `NO_DISTINCT_MIR_OP` | The local body result uses ordinary control-flow/block normalization. |
| `match_exhaustiveness_phase_a` | `NOT_APPLICABLE(checker-only rejection before MIR)` | Rejected non-exhaustive source creates no runtime MIR event. |
| `match_arm_guard_msp` | `GENERIC_LAW_PRESENT` | §§2 and 11 bind subject-once evaluation and atomic binding after static admission. |
| `bytes_literal_hash_bytes_msp` | `LAW_PRESENT` | §4 binds raw byte values and forbids hidden text conversion without selecting storage. |
| `string_interpolation_braced_expr_core` | `LAW_PRESENT` | §4 binds ordered single evaluation, preselected Display evidence, final publication and cleanup. |
| `string_interpolation_format_spec_core` | `LAW_PRESENT` | §4.1 binds `Align? Width`, Unicode-scalar minimum width, SPACE padding, no truncation, checker rejection and the ordered Display-then-padding builder plan. |
| `string_interpolation_shorthand_factor_msp` | `LAW_PRESENT` | §4 binds one root evaluation and read-only projection before the same Display plan. |
| `numeric_array_postfix_transpose_caret_msp` | `LAW_PRESENT` | §11 binds an owner-bounded readonly view, axis/orientation transform, lifetime, and the no-implicit-element-copy boundary without selecting backend storage. |

The supplemental features `no_string_char_bytes_implicit_conversion_law` and `text_model_char_grapheme_current_law` are `LAW_PRESENT` under §4; they do not replace or enlarge the required 20-feature set.

No required row remains `DEFERRED_PRODUCT_HANDOFF` in this 20-feature audit set. The interpolation format row is now `LAW_PRESENT` under §4.1. All product lanes remain `NOT_RUN`. A `LAW_PRESENT` row closes only the source-observable MIR contract written above; it is not a product execution receipt and selects no backend opcode, storage layout, ABI, or support claim. In particular, this static closure does not prove that xVM or either Cranelift backend implements ternary branching, interpolation planning, padding, or transpose-view lowering.

## 14.1 Closed-union, refinement, guard, and pattern-flow handoff

The checker lowers an admitted closed-union typed arm to
`UnionAlternativeTest(UnionTypeId, AlternativeTypeId)` followed by nonowning
probe bindings. The distinct expression forms `subject is Alternative` and
`subject !is Alternative` lower to
`ClosedUnionAlternativeTest(UnionTypeId, AlternativeTypeId, negated)` and
produce `Bool` without a binding. Both operations read only the discriminator
already required by the closed Union representation. MIR must not replace
either operation with a generic `TypeTest`, RTTI, subtype search, reflection, a
Trait query, provider or witness lookup, or evaluation of a refinement
predicate.

`ClosedUnionAlternativeTest` evaluates its subject once, reads the stored
injection identity once, and introduces no ownership commit, effect, authority,
allocation, or hidden failure. The checker has already rejected a non-Union
subject, a target that is not exactly one declared alternative, and direct
comparison chaining. Its `negated` bit only swaps the true and false
successors.

`Phi` is compile-time evidence and is not a runtime value. MIR receives only the selected structural test, the admitted guard evaluation, a delayed commit plan, and explicit failure edges. False structural tests, false guards, and statically unreachable arms commit zero bindings, moves, exclusive borrows, or authorities. Guarded arms do not become exhaustive in MIR merely because their predicate returns Bool.

For an expression test over a stable place, the checker may attach bounded
complementary alternative facts to the two successors. `and then` passes the
left true fact to its right operand and `otherwise` passes the left false fact;
strict `and` and `or` receive no such pre-narrowing. Assignment, aliasing
mutation, exclusive borrow, escape or capture with possible mutation, consume,
or a may-mutate/may-consume call kills the durable fact. MIR does not materialize
`Phi`, and these facts never change the declared semantic type.

Refinement boundaries preserve their selected outcome: proven construction has no duplicate predicate call, `as?` retains Option success/failure, `as!` retains its declared defect edge, and `T::check` retains Result detail. For a direct truth test, checker/HIR may substitute facts from a verified finite `GuardSummaryV1` and omit a redundant later refinement check. No summary or proof value is carried into MIR or runtime; stored, indirect, wrapped, or invalidated guard results remain opaque.

`RefinementR0V1` is exhausted before MIR. Canonical HIR may retain the selected
boundary outcome and the exact formula digest needed for static provenance,
but never an open solver, source-text predicate, or runtime proof plan. MIR
either lowers the already selected predicate evaluation with its existing
failure edge or omits a check proved redundant by the checker. It does not
renormalize the formula, invert IEEE comparisons, repeat a guard call, search
for a witness, or ask xVM/Cranelift/host code to decide implication or
disjointness. The normative static contract is
`spec/contracts/refinement-r0-calculus-v1.json`.

## 15. Post-PR16 nonactivatable Preview operational contracts

> Status fence: this section is governed by Part XII's current preimplementation Preview boundary. Current MIR behavior remains authoritative; the successor material is nonactivatable, implementation begins only after Deeplus 0.1.3 is established, and this text closes no P1 or product lane.

<!-- POST_PR16_UNIT_BEGIN:SFD-N004 -->
```json
{
    "schema":  "deeplus.codex-design.static-first-dynamic-registry-snapshot-route-liveness.r1",
    "status":  "LOCAL_NONCANONICAL_NONACTIVATABLE",
    "projection_split":  {
                             "direct_concrete_borrow":  {
                                                            "operation":  "withDynBorrow\u003cT,R\u003e",
                                                            "static_target":  true,
                                                            "registry_lookup_count":  0,
                                                            "witness_lookup_count":  0
                                                        },
                             "static_trait_registry_projection":  {
                                                                      "operation":  "FacetRegistry\u003cK\u003e.projectBorrow\u003cA\u003e",
                                                                      "static_goal":  "ProjectionGoal\u003cK,A,Borrow\u003e",
                                                                      "registry_authority":  "EXPLICIT_IMMUTABLE_INPUT",
                                                                      "runtime_trait_token_allowed":  false
                                                                  }
                         },
    "registry_key":  {
                         "ordered_fields":  [
                                                "AuthorityScopeId",
                                                "RuntimeTypeId",
                                                "TraitId",
                                                "NormalizedAssociatedBindings",
                                                "FacetMode",
                                                "ResponsibilityProfileId"
                                            ],
                         "exact_field_count":  6,
                         "forbidden_fields":  [
                                                  "RegistryEpoch",
                                                  "RegistrySnapshotId",
                                                  "RegistryLineageId",
                                                  "ProviderId",
                                                  "SourceOrder",
                                                  "ImportOrder",
                                                  "DiscoveryOrder",
                                                  "WallClock"
                                              ],
                         "raw_digest_is_semantic_identity":  false,
                         "field_deletion_allowed":  false,
                         "field_substitution_allowed":  false
                     },
    "responsibility_profile":  {
                                   "identity":  "ResponsibilityProfileId",
                                   "normalized_components":  [
                                                                 "receiver",
                                                                 "effects",
                                                                 "errors",
                                                                 "authority",
                                                                 "suspension",
                                                                 "isolation",
                                                                 "cleanup"
                                                             ],
                                   "raw_digest_role":  "INTEGRITY_ONLY"
                               },
    "snapshot":  {
                     "typed_metadata_fields":  [
                                                   "RegistryId",
                                                   "RegistryLineageId",
                                                   "RegistrySchemaVersion",
                                                   "RegistryEpoch",
                                                   "CanonicalSortedEntries",
                                                   "ContentDigest"
                                               ],
                     "selection":  "EXPLICIT_OPERATION_INPUT",
                     "capture_per_operation":  1,
                     "immutable":  true,
                     "in_place_mutation":  false,
                     "duplicate_normalized_key_policy":  "REJECT_SNAPSHOT",
                     "same_key_equivalent_route_policy":  "REJECT_DUPLICATE_EQUIVALENT",
                     "same_key_non_equivalent_route_policy":  "REJECT_DUPLICATE_CONFLICT",
                     "silent_deduplication":  false,
                     "lookup_tie_breaker":  "NONE_FAIL_CLOSED",
                     "permutation_preserves_canonical_digest":  true
                 },
    "routes":  {
                   "admitted_kinds":  [
                                          {
                                              "kind":  "ExistingConformance",
                                              "requires":  [
                                                               "ConformanceId",
                                                               "TraitWitnessId",
                                                               "sealed behavior and drop metadata"
                                                           ]
                                          },
                                          {
                                              "kind":  "SynchronousNominalAdapterFactory",
                                              "requires":  [
                                                               "explicit nominal adapter type",
                                                               "already admitted conformance",
                                                               "prepare/failure/commit cleanup contract"
                                                           ]
                                          }
                                      ],
                   "forbidden_action_counts":  {
                                                   "create_conformance":  0,
                                                   "create_witness":  0,
                                                   "create_static_label":  0,
                                                   "create_authority":  0,
                                                   "use_extension_as_evidence":  0,
                                                   "perform_fallback":  0
                                               },
                   "provider_import_source_order_winner_count":  0
               },
    "live_facet_seal":  {
                            "captured":  [
                                             "ConformanceId",
                                             "TraitWitnessId",
                                             "ProviderId",
                                             "sealed behavior",
                                             "normalized associated bindings",
                                             "responsibility profile",
                                             "RegistrySnapshotId",
                                             "RegistryEpoch",
                                             "ProviderLeaseId"
                                         ],
                            "later_snapshot_retarget_count":  0,
                            "removal_revokes_existing_facet":  false,
                            "future_projection_uses_new_snapshot":  true
                        },
    "provider_liveness":  {
                              "ProviderLeaseId":  {
                                                      "visibility":  "IMPLEMENTATION_PRIVATE",
                                                      "registry_key_member":  false,
                                                      "public_semantic_identity":  false,
                                                      "source_authority":  false,
                                                      "trait_witness":  false
                                                  },
                              "unload_rule":  "UNLOAD_ONLY_AFTER_LAST_LIVE_PROVIDER_LEASE",
                              "existing_live_facet_behavior_change_count":  0
                          },
    "deferred":  [
                     "REGISTRY_INOUT_PROJECTION",
                     "REGISTRY_OWNED_PROJECTION",
                     "STRUCTURAL_CONFORMANCE",
                     "RUNTIME_TRAIT_TO_TYPED_FACET",
                     "FACET_STORE"
                 ]
}
```
<!-- POST_PR16_UNIT_END:SFD-N004 -->


<!-- IR-OWN-R8-MIR-CONTRACT -->
## Ownership and context-anchor lowering fence

`borrow place` reuses
`HirExprKind::PlaceAccess { plan: HirPlacePlan(access = BorrowShared) }`.
The checker selects one static `RegionId` and `LoanId` before typed-HIR sealing;
the `HirPlacePlan` preserves both identities, and MIR lowering preserves them
exactly in the matching value and loan rows. A loop may create multiple dynamic
activations of that static loan site, represented by the existing linear
`ACCESS` state machine rather than by inventing another `LoanId`.

Expression context-anchor `&` is not an ownership borrow.  The enclosing
NumericArray or Measure operation owns one `HirContextAdaptationPlan` with
`context_adaptation_plan_id`, `role_id`, `provider_operand_eval_id`,
`adapted_operand_eval_id`, `unit_witness_id_or_null`, and `source_origin_id`.
Operands are evaluated once in source order.  NumericArray requires a null
unit witness; Measure requires the statically selected `UnitWitnessId`.
The plan is resolved before MIR and leaves no standalone context node,
`LoanId`, borrow event, runtime role lookup, or unresolved provider.

The ownership decision state machine consumes the canonical typed descriptor.
Moves preserve immutable origin provenance, reservations use exact
`ReservationId` values, n-ary joins are predecessor-order invariant, and
divergent global loan/token/reservation/conflict state is terminal without an
output state.  Static execution of the contract does not claim a production
MIR, xVM, runtime, or Cranelift implementation.

### Path-sensitive loan closing

Source keeps loan closing implicit. MIR makes it explicit with the existing
`LOAN_BEGIN_SHARED`, `LOAN_BEGIN_EXCLUSIVE`, `LOAN_BEGIN_REBORROW`, `LOAN_END`,
and linear `ACCESS(LoanId)` identities. Each loan-table row binds one static
begin operation, one optional parent loan, and a nonempty canonical set of
static end operations. The lowerer derives the earliest close frontier after
all authorized uses and children and before every conflicting owner mutation,
move, replacement, cleanup, region exit, or unadmitted suspension. Critical
edges are split when only part of a successor frontier closes the loan.

Every dynamic begin executes exactly one matching end on every reachable
normal, Error, Defect, Cancellation, early-exit, and terminal path. Multiple
static ends are legal only on mutually exclusive paths. A loop iteration must
return the static loan site to inactive before its backedge; a later iteration
creates a fresh dynamic activation of that same site. Predecessors at a join
must have identical loan and ACCESS-token states.

Reborrows close leaf-first. Beginning a child suspends its immediate parent;
ending that child resumes only that parent, and a parent cannot end while any
child is live. `LOAN_END` is infallible and nonsuspending. It consumes exactly
the ACCESS token bound to its LoanId, invalidates the activation's borrowed or
inout views, and discharges ViewRelease. It creates no value, effect, Error,
Defect, Cancellation, cleanup token, user cleanup call, or failure-order event.
A malformed table, token binding, close order, join, suspension, owner barrier,
or terminal balance is rejected by the release verifier as
`MIR_LOAN_UNBALANCED`; the original source diagnostic remains primary when
source itself was inadmissible.

A deferred call that uses a loan is a final authorized use: invoke it, close
the loan, then begin overlapping owner cleanup. This ordering rule does not
activate or import any separate defer candidate. Existing primary outcomes
remain primary, while later cleanup failures retain the deterministic LIFO
suppression law in §5. Loan closing contributes no cleanup budget row.

### Region graph and loan projection

The typed HIR body owns a finite, reference-closed region forest and exact
place-to-storage-region bindings. Its region extent kinds are `LEXICAL`,
`INVOCATION`, and `PROCESS_STATIC_IMMUTABLE`; borrow, inout, capture, and
suspension are uses of an extent, not additional extent kinds. Parent links are
acyclic, entry nodes dominate contained uses, and every reachable path from a
contained use crosses one declared end frontier before leaving the extent.

`NormalizedTypeDescriptor.region_profile_id_or_null` is a type-level relation
profile. It is never a concrete per-value `RegionId` and never participates as
one in a normalized `TypeId`. Concrete value-level identities live in
`PlacePlan.result_region_id_or_null` and `PlacePlan.loan_id_or_null`, and lower
exactly to the MIR value and loan tuple. Concrete region or loan identities are
not exported through a module API.

Region and loan projection is a body-wide pass after ordinary node-row
lowering and before the release verifier. It preserves region ID, extent kind,
parent, isolation domain, entry, and end frontiers; maps every place to its
storage region; and emits one existing loan-begin operation for each admitted
borrow site. Reborrows require the exact active parent `LoanId` and a strict
child region. The existing R34 close-frontier contract owns all `LOAN_END`
placement and path balance.

Region and loan identities are compiler-local value-level verifier identities,
not runtime region objects, ABI identities, source names, or backend handles.
After region projection and loan balance verify, xVM and Cranelift may erase
them when doing so preserves every language observation. Runtime or backend
relookup, reselection, or inference of either identity is forbidden.

## 15. Current HIR-H1/MIR R1 machine contract

<!-- R10-HIR-MIR-MACHINE-CONTRACT -->

The current Stable-design machine schema is `deeplus.mir/r1`, and deterministic
lowering produces `Verified<DeeplusMirR1>`. The closed machine registry is
`deeplus.mir-machine-registry/r1`: exactly 29 semantic operations, 17
terminators, 12 linear token kinds, 11 responsibility axes in their canonical
order, and 26 design capabilities. These are backend-neutral identities; XBC,
CLIF, registers, addresses, object layout, calling convention, and ABI remain
target-projection concerns.

`MirCapabilityReceiptR1` is validated against
`deeplus.mir-capability-receipt/r1`. Required capabilities are recomputed from
the exact reachable HIR lowering keys and then closed over the acyclic
capability dependency graph. Provider evidence is resolved independently.
Receipt claims never prove themselves. A mismatch preserves the exact
`Verified<CanonicalHirH1>` and prevents only `ExecutableHirH1`.

The lowering registry contains exactly 102 Current rows and 111 rows at the
explicit-Preview maximum. A row disposition is only `LOWER` or
`NO_RUNTIME_EMISSION`; capability rejection is not a lowering disposition.
HIR/MIR semantic and pair projections use RFC 8949 deterministic CBOR and pair
verification deterministically relowers before comparing semantic bytes and
ordered provenance.

`ProposedMirX1` remains a noncanonical, nonactivatable compatibility target.
This machine-schema adoption creates no implementation or product execution;
all 15 product lanes remain `NOT_RUN`.
