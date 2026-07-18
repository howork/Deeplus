# Deeplus Operational Semantics 0.1.2 — R51f3 Current Canonical

Deeplus MIR is the canonical semantic authority. Rust frontend structures, xVM bytecode, LLVM IR, AOT code, and ORC JIT code are projections that must preserve MIR-observable behavior. Product execution is `NOT_RUN`.

## 1. Machine state and observation

A step state contains the current MIR frame, ordered operand stack, places and ownership states, cleanup-region stack, effect/error continuation, task/actor state, provider bindings, and source provenance. Observable events are ordered result/failure, I/O or authority events, message enqueue/dequeue, suspension/resume, cancellation, cleanup and provider observation. Backend-private allocation and instruction selection are not observations.

## 2. Evaluation and calls

Operands, arguments, guards, interpolation segments, collection entries and cleanup registrations evaluate left-to-right unless a named law fixes another order. Calls preserve value, context, witness, repeated positional and named channels. `options***: Record` declares a named-rest channel; `**record` supplies static labels. Labels, witness ids, extension ids and providers are fixed before MIR execution.

## 3. Ordinary and rightward local bindings

An ordinary local binding evaluates its initializer exactly once while the target is absent from scope. On success it commits one immutable or mutable place; on failure it commits none and transfers along the initializer failure edge. Rightward binding has no MIR operation: `$`/`$$` is eliminated by frontend normalization to this rule. Cleanup responsibility moves into the committed local exactly as for direct `let`/`var`.

`yield value -> $response` first emits the coroutine suspension event. After resume, the response value is passed to the ordinary binding rule. This does not make general rightward binding a suspension form.

## 4. Strings

Plain and raw source strings lower to immutable `ConstString` payloads. The raw scanner supplies the exact body scalars; escape and interpolation machines are not invoked. xVM and both LLVM backends observe the same String value.

## 5. Failure and cleanup

Errors, defects and cancellation are distinct. Primary/suppressed failure order is deterministic. Cleanup executes exactly once in LIFO region order and cannot be skipped by return, throw, break, cancellation or suspension. A cleanup failure is appended according to the suppression law and never reorders an already selected primary outcome.

## 6. Option coalescing and lazy evaluation

For `lhs ?: fallback`, `lhs` is evaluated first. When it is `some(v)`, `v` is returned and `fallback` is not evaluated. Only `none` evaluates the fallback. Ownership extraction follows the Option payload law. This short-circuit rule is a backend-visible observation.

`let#lazy` evaluates at first force, publishes exactly one immutable committed value, and reuses the cached result. Reentrant force is rejected. It does not silently retry an effect or hide an error channel.

## 7. Actors and messages

Actor isolation is explicit. Within one sender/receiver channel and one admitted mailbox profile, enqueue order is FIFO; no backend may reverse it. Message send is not a method call. Request/reply, cancellation, capacity and protocol outcomes remain explicit MIR events.

## 8. Objects, evidence and construction

Nominal dispatch, Trait evidence, extension resolution, construction and materialization lower to explicit MIR identities. Runtime strings and Map keys never become static labels or witnesses. Tooling certificates and provider-derive sidecars are consumed before ordinary source checking and never become execution authority.

## 9. Dynamic providers

A dynamic unit conversion MIR event exists only after stdlib profile, provider and policy checks. It records provider identity/version, observation timestamp, rounding and failure/effect policy, cache key and replay token. No source Preview gate activates this event.

## 10. xVM and LLVM preservation

The Rust xVM bytecode interpreter is the first development, validation and REPL execution path. LLVM AOT is the first native path; LLVM ORC JIT follows. Differential conformance compares ordered observable event traces, final value or failure, place/cleanup balance and provider replay identity. A design-static PASS in this package is not such a receipt.


## 11. Elaboration and evaluation preservation

Field puns and grouped forwarding are eliminated before MIR while preserving source-order evaluation and static identities. A scoped import/use group changes only compile-time resolution. Multiline String dedent is completed by the scanner before `ConstString`; interpolation segments retain ordinary left-to-right evaluation. Pattern-control subjects evaluate once and their bindings commit atomically. `for let` mismatch emits no body events and advances to the next candidate. A rejected quarantine design probe creates no MIR event.


## 12. Removed-surface MIR boundary

Map indexing lowers through the ordinary index/API contract; dot member selection never becomes a runtime key lookup. Explicit assignments lower through ordinary place read, arithmetic, and place write operations; there is no increment/decrement MIR opcode. Recursive calls remain ordinary calls and carry no tail-recursion source contract. Regex construction is a library call from `String` or `Bytes`, not a literal MIR constant kind. An explicitly expected List union lowers the declared element type and injections; MIR never receives an automatically inferred heterogeneous List union.


## 13. R51f3 tooling/profile observability

Pattern compilation is an ordinary library call whose engine identity, version, flags, Unicode mode and budget are explicit observables. Tail-call analysis and xVM agents emit side receipts only; removing either tool cannot alter program observations. UML state-machine generation is complete before ordinary Rust frontend checking and therefore adds no MIR event. Product execution for all four contracts is `NOT_RUN`.

## 14. Normative document-consistency product-handoff dispositions

This section classifies the frozen required 20-feature audit set without changing any feature's design status. It is a product-handoff boundary, not an implementation design. All product lanes remain `NOT_RUN`.

| Feature ID | MIR disposition | Authority/boundary |
|---|---|---|
| `named_rest_parameter_record_msp` | `LAW_PRESENT` | §§2 and 8 bind the named-rest channel and static-label supply. |
| `schema_named_unfolding` | `GENERIC_LAW_PRESENT` | §§8 and 11 bind pre-MIR unfolding and materialization identity. |
| `unicode_char_literal_single_quote_msp` | `DEFERRED_PRODUCT_HANDOFF` | Char representation and lowering are not inferable. |
| `char_unicode_scalar_value_model` | `DEFERRED_PRODUCT_HANDOFF` | Scalar representation and conversion are not inferable. |
| `strict_boolean_word_operators_msp` | `DEFERRED_PRODUCT_HANDOFF` | Strict evaluation and failure observables are not closed. |
| `sequential_boolean_control_words_msp` | `DEFERRED_PRODUCT_HANDOFF` | Short-circuit and effect-suppression observables are not closed. |
| `standalone_bang_not_current_not_word_law` | `NO_DISTINCT_MIR_OP` | This is a frontend spelling boundary and authorizes no standalone Boolean `!` operation. |
| `rightward_flow_dollar_local_binding_msp` | `LAW_PRESENT` | §3 binds normalization to ordinary local binding and no distinct MIR operation. |
| `optional_chaining_not_current_law` | `NOT_APPLICABLE(rejected current surface)` | Rejected source creates no MIR event under §12. |
| `ternary_conditional_expression` | `DEFERRED_PRODUCT_HANDOFF` | Condition/arm evaluation and join observables are not closed. |
| `ternary_short_expression_stable_profile` | `DEFERRED_PRODUCT_HANDOFF` | Formatter guidance does not authorize ternary evaluation behavior. |
| `at_control_expression_family` | `GENERIC_LAW_PRESENT` | §§1, 2, and 11 supply generic ordered control-flow observations. |
| `local_value_body_msp` | `NO_DISTINCT_MIR_OP` | The local body result uses ordinary control-flow/block normalization. |
| `match_exhaustiveness_phase_a` | `NOT_APPLICABLE(checker-only rejection before MIR)` | Rejected non-exhaustive source creates no runtime MIR event. |
| `match_arm_guard_msp` | `GENERIC_LAW_PRESENT` | §§2 and 11 bind subject-once evaluation and atomic binding after static admission. |
| `bytes_literal_hash_bytes_msp` | `DEFERRED_PRODUCT_HANDOFF` | Bytes payload, representation, and conversion observables are not closed. |
| `string_interpolation_braced_expr_core` | `DEFERRED_PRODUCT_HANDOFF` | Rendering, provider, and failure observables are not closed. |
| `string_interpolation_format_spec_core` | `DEFERRED_PRODUCT_HANDOFF` | Formatting provider identity and failure behavior are not closed. |
| `string_interpolation_shorthand_factor_msp` | `DEFERRED_PRODUCT_HANDOFF` | Shorthand lowering cannot infer rendering or provider behavior. |
| `numeric_array_postfix_transpose_caret_msp` | `DEFERRED_PRODUCT_HANDOFF` | View/copy, ownership, representation, rank/orientation, and backend observables are not closed. |

The supplemental features `no_string_char_bytes_implicit_conversion_law` and `text_model_char_grapheme_current_law` are also `DEFERRED_PRODUCT_HANDOFF`; they do not replace or enlarge the required 20-feature set.

For every `DEFERRED_PRODUCT_HANDOFF` row, design status is unchanged and product lanes remain `NOT_RUN`. An implementer must not infer view/copy, ownership, conversion, strict or short-circuit evaluation, rendering/provider/failure, scalar or byte representation, rank/orientation, opcode, or backend behavior. Removing a block requires an approved future MIR law and a target-bound execution receipt. This repair chooses no opcode, representation, ownership, evaluation, provider, failure, or backend semantics.
