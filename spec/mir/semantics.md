# Deeplus Operational Semantics 0.1.2 — R51f3 Current Canonical

Deeplus MIR is the canonical semantic authority. Rust frontend structures, xVM bytecode, LLVM IR, AOT code, and ORC JIT code are projections that must preserve MIR-observable behavior. Product execution is `NOT_RUN`.

## 1. Machine state and observation

A step state contains the current MIR frame, ordered operand stack, places and ownership states, cleanup-region stack, effect/error continuation, task/actor state, provider bindings, and source provenance. Observable events are ordered result/failure, I/O or authority events, message enqueue/dequeue, suspension/resume, cancellation, cleanup and provider observation. Backend-private allocation and instruction selection are not observations.

## 2. Evaluation and calls

Operands, arguments, guards, interpolation segments, collection entries and cleanup registrations evaluate left-to-right unless a named law fixes another order. Calls preserve value, context, witness, repeated positional and named channels. `options***: Record` declares a named-rest channel; `**record` supplies static labels. Labels, witness ids, extension ids and providers are fixed before MIR execution.

Current operator glyphs lower only to closed intrinsic MIR operations chosen from the normalized built-in operand domain. Lowering performs no conformance, extension, witness, provider, import-order, source-order, or runtime dispatch. Named Trait methods lower as ordinary named calls and never become glyph hooks. Strict Boolean `and`/`or` evaluate both operands left-to-right; sequential `and then`/`otherwise` evaluate the right operand only when required. The existing `?:` Option law remains separately lazy.

An assignment evaluates its target place once and its right operand once. A compound assignment evaluates the place, reads the original value, evaluates the right operand, completes one intrinsic operation, and commits at most one write, in that order. Every assignment returns `Unit`. Any failure before commit preserves the original owner and value; no compound-assignment MIR opcode may hide a second place evaluation or partial write.

## 3. Ordinary and rightward local bindings

An ordinary local binding evaluates its initializer exactly once while the target is absent from scope. On success it commits one immutable or mutable place; on failure it commits none and transfers along the initializer failure edge. Rightward binding has no MIR operation: `$`/`$$` is eliminated by frontend normalization to this rule. Cleanup responsibility moves into the committed local exactly as for direct `let`/`var`.

`yield value -> $response` first emits the coroutine suspension event. After resume, the response value is passed to the ordinary binding rule. This does not make general rightward binding a suspension form.

## 4. Values, literals, strings, and bytes

Plain and raw source strings lower to immutable `ConstString` payloads. The raw scanner supplies the exact body scalars; escape and interpolation machines are not invoked. xVM and both LLVM backends observe the same String value.

MIR value identity records the semantic type and value, not a storage address, serialization tag, runtime discriminant, ABI, or backend layout. Unsuffixed `Int` constants inhabit the signed 64-bit mathematical domain. Explicit integer domains remain distinct. Integer arithmetic is checked: a dynamic overflow or division or remainder by zero emits deterministic `ArithmeticDefect` before any enclosing place commit; wrapping and saturation occur only through named calls. Integer division truncates toward zero, and remainder preserves `a == trunc(a / b) * b + r` with `r == 0` or the dividend sign and `|r| < |b|`; signed `MIN / -1` and `MIN % -1` take the overflow edge. Floating `%` and floating glyph power have no MIR operation. A statically rejected failure creates no MIR.

`Float32` and `Float64` operations preserve IEEE-754 binary32/binary64 behavior and round to nearest with ties to even. NaN is unordered and signed zero compares equal. Char constants contain exactly one Unicode scalar. String indexing observes Unicode scalar position; Bytes indexing observes one `UInt8`. Neither lowering implies UTF-16, grapheme, text/byte conversion, or a public representation. The recovery spelling `null` creates no MIR constant; Option absence lowers only from the explicit `none` alternative.

## 5. Failure and cleanup

Errors, defects and cancellation are distinct. Cancellation progresses through request, observation, acknowledgement, cleanup barrier, and terminal outcome events; each event is monotonic and idempotent for one CancellationId. Primary/suppressed failure order is deterministic: at one task-scope terminal barrier, the failed child with the lowest lexical `spawn_index` becomes primary and the remaining child failures are appended in ascending `spawn_index`; scheduler completion order is not evidence. Cleanup executes exactly once in LIFO region order and cannot be skipped by return, throw, break, cancellation or suspension. Cleanup failures are then appended in their actual deterministic LIFO execution order according to the suppression law and never reorder an already selected primary outcome.

## 6. Option coalescing and lazy evaluation

For `lhs ?: fallback`, `lhs` is evaluated first. When it is `some(v)`, `v` is returned and `fallback` is not evaluated. Only `none` evaluates the fallback. Ownership extraction follows the Option payload law. This short-circuit rule is a backend-visible observation.

`let#lazy` evaluates at first force, publishes exactly one immutable committed value, and reuses the cached result. Reentrant force is rejected. It does not silently retry an effect or hide an error channel.

## 7. Actors and messages

Actor isolation is explicit. One ActorId owns one isolated StateRegionId and MailboxId; one admitted ActorTurnId has mutation authority at a time, including across its suspension. Suspend/resume preserves that same turn identity and does not release dequeue or mutation authority. A statically proven self/dependency-cycle request await is rejected before MIR rather than represented as implicit reentrancy. The exact FIFO key is `(SenderId, ReceiverActorId, MailboxProfileId)`; `ChannelId` is derived from that tuple rather than adding another ordering component. Each successful enqueue commit allocates the next strictly increasing `channel_sequence`, and dequeue preserves that order. No rejected attempt has a `channel_sequence`. No global order or fairness is implied.

Message send is not a method call. Prepare-send evaluates the receiver and payload once without transferring ownership. The absence of a mailbox clause binds `logical_unbounded_v1`; positive static `#mailbox(capacity: N)` binds `bounded_reject_v1`. The bounded profile never blocks, retries, suspends, or drops: full capacity emits an immediate `Result::err(ActorMessageError::mailboxFull)`, and receiver closure before admission emits `Result::err(ActorMessageError::receiverClosedBeforeAdmission)`. Both are precommit events, leave ownership with the sender, and allocate no sequence. Admission records exactly one successful enqueue plus exactly one ownership commit. A one-way commit returns `Result::ok` with a Unit payload; a request commit creates one CorrelationId and ReplyId and returns `Result::ok` with a `Task<T>` payload. If the receiver closes before the correlated reply, that admitted task terminates through `ActorMessageError::receiverClosedBeforeReply`. Exactly one correlated reply/failure/cancellation terminal event is admitted. Distributed and exactly-once delivery events have no current MIR identity.

The cancellation race is phase-split by enqueue commit. Observation before commit emits the cancellation outcome, aborts admission, retains sender ownership, and allocates no `channel_sequence`; it is not converted into `ActorMessageError`. Observation after commit cannot retract or renumber the message, restore a moved sender place, or rewrite the already produced admission Result. For an admitted request it affects only the correlation-bound task lifecycle under the existing cancellation law.

Task scopes record ScopeId, ParentTaskId, ordered ChildTaskIds, cancellation state, and cleanup barrier. A scope exit joins every admitted child; no detached task event is current. Spawn, suspend, resume, cancellation request/observe/acknowledge, child failure, join and scope terminal events retain FailureId and lexical child order so xVM and LLVM can reproduce the same primary/suppressed outcome.

## 8. Objects, evidence and construction

Nominal dispatch, Trait evidence, extension resolution, construction and materialization lower to explicit MIR identities. Runtime strings and Map keys never become static labels or witnesses. Tooling certificates and provider-derive sidecars are consumed before ordinary source checking and never become execution authority.

## 9. Dynamic providers

A dynamic unit conversion MIR event exists only after stdlib profile, provider and policy checks. It records provider identity/version, observation timestamp, rounding and failure/effect policy, cache key and replay token. No source Preview gate activates this event.

## 10. xVM and LLVM preservation

The Rust xVM bytecode interpreter is the first development, validation and REPL execution path. LLVM AOT is the first native path; LLVM ORC JIT follows. Differential conformance compares ordered observable event traces, final value or failure, place/cleanup balance and provider replay identity. A design-static PASS in this package is not such a receipt.


## 11. Elaboration and evaluation preservation

Field puns and grouped forwarding are eliminated before MIR while preserving source-order evaluation and static identities. A scoped import/use group changes only compile-time resolution. Multiline String dedent is completed by the scanner before `ConstString`; interpolation segments retain ordinary left-to-right evaluation.

A successful Pattern owner emits `subject_evaluate`, `subject_acquire`, `test_plan_build`, `structural_test`, `probe_bind`, optional `guard_evaluate`, `atomic_commit`, `final_bind`, `body`, and `exit_or_join`. A structural mismatch terminates after `structural_test`; a false guard terminates after `guard_evaluate`. In both cases only the context-bound `exit_or_join` edge follows. TestPlan and probe events are nonconsuming. Failure before `atomic_commit` has zero ownership commit, `pattern_move_count`, irreversible borrow, authority, escape, suspension, partial binding, and final binders. Guarded-let failure transfers to its required `else`; `for let` mismatch or false guard filters exactly one candidate and emits no body event. Each phase carries the exact DPM fixture identity and attempt disposition so successful match commit, precommit mismatch, false guard, guarded-let transfer, for-let filtering, and plain-let destructuring remain independently auditable. Or-pattern branches expose one canonical binder interface, alias binding is a borrow event, and a place join retains only the intersection of incoming capabilities. A rejected quarantine design probe creates no MIR event.


## 12. Removed-surface MIR boundary

Map indexing lowers through the ordinary index/API contract; dot member selection never becomes a runtime key lookup. Explicit assignments lower through the single-place transaction in §2; there is no increment/decrement MIR opcode. Recursive calls remain ordinary calls and carry no tail-recursion source contract. Regex construction is a library call from `String` or `Bytes`, not a literal MIR constant kind. An explicitly expected List union lowers the declared element type and injections; MIR never receives an automatically inferred heterogeneous List union. Custom operator declarations and fixed-operator Trait dispatch create no MIR operation. `...` preserves only repeated-positional residue or the admitted comprehension-unfold structure and never creates a range; rejected `..>` and empty `[]` create no MIR.

Built-in indexing evaluates the owner and each index once, left-to-right, then validates the declared logical domain before projecting storage. `List`, `String`, and `Bytes` use `1..length` with offset `index - 1`; an explicitly bounded List retains `L..U`. Every `ReadonlyView` carries its source owner's declared logical domain, coordinate-to-storage mapping, and provenance, so no view construction independently rebases it. A missing Map key emits `IndexError::keyNotFound`; any type-correct dynamic built-in positional or NumericArray coordinate outside its logical domain emits `IndexError::outOfLogicalDomain`. Both are precommit failures. Map uses the exact key type; tuple ordinals and Record labels are resolved before MIR and never become dynamic bracket lookup. Conformance to `Sequence`, `Indexable`, or `LogicalIndexDomain` does not add a lowering route.

An ordinary closed slice carrier accepts exactly one bounded range selector. A rank-complete NumericArray coordinate list preserves typed axis identity, and every built-in default source-visible axis is `1..dimension`; only NumericArray admits semicolon-separated multi-axis selection and full-axis `*`. Slice lowering first evaluates and validates every scalar/range/full-axis selector, including `^`/`$` anchor resolution, without mutating the owner. Success creates one readonly view carrying the source owner region, provenance, and selected logical coordinates. There is no implicit rebase, hidden copy, mutable slice assignment, isolation crossing, or owner-lifetime escape. A named explicit rebase/copy call is an ordinary visible operation with its own allocation and ownership observations.


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
| `ternary_conditional_expression` | `DEFERRED_PRODUCT_HANDOFF` | Condition/arm evaluation and join observables are not closed. |
| `ternary_short_expression_stable_profile` | `DEFERRED_PRODUCT_HANDOFF` | Formatter guidance does not authorize ternary evaluation behavior. |
| `at_control_expression_family` | `GENERIC_LAW_PRESENT` | §§1, 2, and 11 supply generic ordered control-flow observations. |
| `local_value_body_msp` | `NO_DISTINCT_MIR_OP` | The local body result uses ordinary control-flow/block normalization. |
| `match_exhaustiveness_phase_a` | `NOT_APPLICABLE(checker-only rejection before MIR)` | Rejected non-exhaustive source creates no runtime MIR event. |
| `match_arm_guard_msp` | `GENERIC_LAW_PRESENT` | §§2 and 11 bind subject-once evaluation and atomic binding after static admission. |
| `bytes_literal_hash_bytes_msp` | `LAW_PRESENT` | §4 binds raw byte values and forbids hidden text conversion without selecting storage. |
| `string_interpolation_braced_expr_core` | `DEFERRED_PRODUCT_HANDOFF` | Rendering, provider, and failure observables are not closed. |
| `string_interpolation_format_spec_core` | `DEFERRED_PRODUCT_HANDOFF` | Formatting provider identity and failure behavior are not closed. |
| `string_interpolation_shorthand_factor_msp` | `DEFERRED_PRODUCT_HANDOFF` | Shorthand lowering cannot infer rendering or provider behavior. |
| `numeric_array_postfix_transpose_caret_msp` | `DEFERRED_PRODUCT_HANDOFF` | View/copy, ownership, representation, rank/orientation, and backend observables are not closed. |

The supplemental features `no_string_char_bytes_implicit_conversion_law` and `text_model_char_grapheme_current_law` are `LAW_PRESENT` under §4; they do not replace or enlarge the required 20-feature set.

For every remaining `DEFERRED_PRODUCT_HANDOFF` row, design status is unchanged and product lanes remain `NOT_RUN`. An implementer must not infer any still-unbound view/copy, ownership, conversion, rendering/provider/failure, representation, rank/orientation, opcode, or backend behavior. A `LAW_PRESENT` row closes only the source-observable MIR contract written above; it is not a product execution receipt and selects no backend opcode, storage layout, ABI, or support claim.

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
