<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 E — Prelude 및 예제 색인

## Prelude

| 항목 ID | 심볼 | 종류 | 상태 | 제품 지원 |
|---|---|---|---|---|
| `actor_core` | `Actor` | `protocol` | `stable_design` | `NOT_RUN` |
| `actor_message_error` | `ActorMessageError` | `enum` | `stable_design` | `NOT_RUN` |
| `arithmetic_defect` | `ArithmeticDefect` | `language_intrinsic_defect` | `stable_design` | `NOT_RUN` |
| `async_collector` | `AsyncCollector` | `stdlib_profile` | `stable_design` | `NOT_RUN` |
| `async_sequence_t` | `AsyncSequence<T, E>` | `protocol` | `stable_design` | `NOT_RUN` |
| `bitfield_codec` | `BitfieldCodec` | `trait` | `stdlib` | `NOT_RUN` |
| `bitfield_raw` | `BitfieldRaw<Backing>` | `trait` | `stdlib` | `NOT_RUN` |
| `bitwise` | `Bitwise` | `internal_or_stdlib_trait_seed` | `stable_design` | `NOT_RUN` |
| `box_t` | `Box<T>` | `core_type` | `stable_design` | `NOT_RUN` |
| `byte_view` | `ByteView` | `core_type` | `stable_design` | `NOT_RUN` |
| `bytes` | `Bytes` | `core_type` | `stable_design` | `NOT_RUN` |
| `char` | `Char` | `scalar` | `stable_design` | `NOT_RUN` |
| `collect_policy` | `CollectPolicy` | `enum` | `stable_design` | `NOT_RUN` |
| `contextparameterrole` | `ContextParameterRole` | `function_signature_descriptor` | `stable_design` | `NOT_RUN` |
| `display` | `Display` | `trait/profile` | `stable_design` | `NOT_RUN` |
| `exit_code` | `ExitCode` | `entry_result` | `stable_design` | `NOT_RUN` |
| `extensionsetid` | `ExtensionSetId` | `tooling_schema` | `stable_design` | `NOT_RUN` |
| `facet_rcts_v5` | `Facet<Mode,Contract>` | `compiler_intrinsic_type` | `stable` | `NOT_RUN` |
| `fillrepeatadmissibilityprofile` | `FillRepeatAdmissibilityProfile` | `checker_known_protocol` | `stable_design` | `NOT_RUN` |
| `float32_nonfinite_constants` | `Float32` | `numeric_type_side_constants` | `stable_design` | `NOT_RUN` |
| `float64_nonfinite_constants` | `Float64` | `numeric_type_side_constants` | `stable_design` | `NOT_RUN` |
| `frozen_list_t` | `FrozenList<T>` | `core_type` | `stable_design` | `NOT_RUN` |
| `grapheme` | `Grapheme` | `stdlib_value_or_view` | `stable_design` | `NOT_RUN` |
| `implementationid` | `ImplementationId` | `compiler_identity` | `stable_design` | `NOT_RUN` |
| `index_error` | `IndexError` | `enum` | `stable_design` | `NOT_RUN` |
| `indexable` | `Indexable` | `checker_known_protocol` | `stable_design` | `NOT_RUN` |
| `iterator` | `Iterator` | `trait_profile` | `stable_design` | `NOT_RUN` |
| `jsonvalue` | `JsonValue` | `boundary_value` | `stable_design` | `NOT_RUN` |
| `list_snapshot_t` | `ListSnapshot<T>` | `core_type` | `stable_design` | `NOT_RUN` |
| `list_t` | `List<T>` | `collection` | `stable_design` | `NOT_RUN` |
| `logical_index_domain` | `LogicalIndexDomain<Index>` | `trait` | `stable_design` | `NOT_RUN` |
| `map_k_v` | `Map<K,V>` | `collection` | `stable_design` | `NOT_RUN` |
| `measure_rep_dim` | `Measure<Rep, Dim>` | `stdlib_profile` | `stdlib_profile` | `NOT_RUN` |
| `membershipprotocol` | `MembershipProtocol` | `checker_known_protocol` | `stable_design` | `NOT_RUN` |
| `modulesignature` | `ModuleSignature` | `language_surface` | `stable_design` | `NOT_RUN` |
| `mutable_list_t` | `MutableList<T>` | `core_type` | `stable_design` | `NOT_RUN` |
| `numeric_array` | `NumericArray<T, rank R>` | `core_type` | `stable_design` | `NOT_RUN` |
| `option_t` | `Option<T>` | `enum` | `stable_design` | `NOT_RUN` |
| `option_unwrap_or_else` | `Option<T>::unwrapOrElse` | `stdlib_operation` | `stable_design` | `NOT_RUN` |
| `ord_t` | `Ord<T>` | `trait` | `stable_design` | `NOT_RUN` |
| `owned_downcast_op` | `downcastOwned<Target,Source>` | `function` | `stable_design` | `NOT_RUN` |
| `owned_downcast_t` | `OwnedDowncast<Target,Source>` | `core_type` | `stable_design` | `NOT_RUN` |
| `readonly_view_t` | `ReadonlyView<T>` | `core_type` | `stable_design` | `NOT_RUN` |
| `replace_t` | `replace<T>` | `function` | `stable_design` | `NOT_RUN` |
| `result_t_error_e` | `Result<T, error E>` | `enum` | `stable_design` | `NOT_RUN` |
| `sequence_t` | `Sequence<T>` | `protocol` | `stable_design` | `NOT_RUN` |
| `set_t` | `Set<T>` | `collection` | `stable_design` | `NOT_RUN` |
| `shared_t` | `Shared<T>` | `shared_handle` | `stable_design` | `NOT_RUN` |
| `sharedcell_t` | `SharedCell<T>` | `synchronization` | `stable_design` | `NOT_RUN` |
| `sharedmutex_t` | `SharedMutex<T>` | `synchronization` | `stable_design` | `NOT_RUN` |
| `string` | `String` | `core_type` | `stable_design` | `NOT_RUN` |
| `string_render` | `String::render<T>` | `static_function` | `stdlib` | `NOT_RUN` |
| `task_t` | `Task<T>` | `core_type` | `stable_design` | `NOT_RUN` |
| `unitcatalog` | `UnitCatalog` | `stdlib_profile` | `stable_design` | `NOT_RUN` |
| `with_borrowed_t` | `withBorrowed<T,R>` | `function` | `stable_design` | `NOT_RUN` |
| `witnessid` | `WitnessId` | `checker_identity` | `stable_design` | `NOT_RUN` |

## 예제

| 예제 ID | 제목 | 결과 | 원천 역할 | 증거 |
|---|---|---|---|---|
| `EX-R48-001` | Column-vector semicolon stable shorthand | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-002` | Column-vector malformed mixed separator rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-003` | NumericArray same-shape elementwise arithmetic | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-004` | Vector dot product stable operator | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-005` | Matrix multiplication stable operator | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-006` | Caret power stable operator | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-007` | Basic index operator stable core | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-008` | NumericArray context anchor stable MSP | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-009` | Measure literal and unit catalog stable core | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-010` | Unit operation policy exact conversion stable core | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-011` | Type schema construction and derivation | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-012` | Map unfold double star current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-013` | Declarative function clause with otherwise | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-014` | Clause pattern heads stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-015` | Explicit context parameter stable phase A | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-016` | Named extension set and qualified selector | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-017` | Member/extension collision is error | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-018` | Generic responsibility quantification | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-020` | Effect and error row polymorphism stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-021` | At-control expression restored | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-022` | Generator expression restored | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-023` | Refinement and as? Option law | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-024` | Closure capture descriptor stable current law | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-025` | Nested local function stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-026` | FFI remains preview-gated | `accept_with_gate` | `script` | `design_static_product_not_run` |
| `EX-R48-028` | Generic invariance rejects broad container covariance | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-029` | Trait-only variance producer surface | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-030` | Trait variance consumer-position misuse rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-031` | Result and throws cannot duplicate recoverable error channel | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-032` | Unsafe is not an EffectRow atom | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-033` | Context parameter role is part of function type identity | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-034` | Ordinary argument cannot satisfy context role | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-035` | Measure literal requires active unit catalog authority | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-036` | Active extension does not form trait witness | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-037` | as? returns Option and check returns Result | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-038` | typeof measure sample preserves UnitCatalog authority | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-040` | typeof invalid runtime/static-sample boundary | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-041` | typeof call form is forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-042` | Ordinary trailing closure preserves call responsibility | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-043` | Message trailing closure omits only the comma | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-044` | Bare ordinary call remains not-current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48-045` | Named constructor external call uses new by default | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-046` | Header constructor delegation is post-init | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48-047` | Constructor delegation list cannot mix same-type and super targets | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48B-048` | External named constructor call uses Type!name explicitly | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-050` | Trailing closure requires a closure parameter suffix | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48B-051` | Constructor delegation cycle is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48B-052` | Option explicit flow stdlib profile replaces optional chaining | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-055` | Option T? and double-colon case canonicalization | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-056` | Canonical Option cases use double colon | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-057` | Char/String current text law | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-058` | Bytes literal current Stable form | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-059` | Bytes literal is Stable and ungated | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-060` | Explicit return, def#pure, and lambda ret | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-061` | Named function expression body is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48B-062` | Lambda block without ret is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48B-063` | Type schema construction restored as schema domain | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-064` | All-named argument layout preview | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-065` | Rightward dollar local binding preview | `accept` | `library` | `design_static_product_not_run` |
| `EX-R48B-066` | Rightward dollar-local flow binding is current | `accept` | `library` | `design_static_product_not_run` |
| `EX-R48B-067` | String interpolation stable core | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-068` | String interpolation factor and format current form | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48B-069` | String interpolation dot shorthand is accepted | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-070` | Module and static path boundary is stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-071` | Dotted static path rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-072` | Strict and sequential Boolean forms | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-073` | Bool && is not logical AND | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-074` | Double-glyph bitwise operators stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-075` | Bitwise result is not Bool | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-076` | Control-transfer guard clauses stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-077` | Guard clause is not general postfix if | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-079` | Loop outcome match tagged and exhaustive | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-080` | Raw payload in loop outcome match rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-083` | Conformance declaration creates checker-visible witness | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-085` | Associated projection requires explicit trait context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-086` | Bare associated projection rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-087` | Extension does not create trait witness | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-088` | Explicit witness parameter cannot escape | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48C-089` | any Trait existential requires safety and binding | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-090` | some Trait remains gated | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48C-091` | Yield guard preview positive with gate | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-001` | \`typeof\` stable static-sample type projection | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-002` | \`typeof\` still rejects runtime/effectful samples | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-003` | Trailing closure is stable but bare ordinary parenless call remains rejected | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-005` | Rightward flow \`$name\` local binding is stable and statement-only | `accept` | `library` | `design_static_product_not_run` |
| `EX-R48E-006` | Old rightward \`-> let\` target remains removed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-007` | String interpolation factor and format spec are stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-008` | Interpolation shorthand dot stops before member access | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-009` | Bytes literal and named Unicode escape are stable design | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-010` | Option visible \`::some\` elision is stable only in explicit local target context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-011` | Broad Option implicit lift remains rejected outside visible local target | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-012` | Pure elision is stable only when the body is proven pure | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-013` | Pure elision rejects hidden effects | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-014` | Type schema construction is distinct from constructor domain | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-015` | Type schema construction cannot target undeclared labels | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-016` | Closure call modes are stable responsibility descriptors | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-017` | Async/await minimal core is language-design stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-018` | Structured task scope makes cancellation owner visible | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-019` | Actor protocol request/reply is not ordinary method dispatch | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-021` | First-class raw Witness values are still not current source | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-022` | Opaque \`some Trait\` result is stable under single-concrete-return law | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-023` | Opaque \`some Trait\` rejects multiple concrete returns | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-024` | Loop outcome match is tagged and exhaustive | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-092` | Schema construction requires schema authority | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-093` | Schema construction cannot call constructor-domain init | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E-094` | Schema construction preserves public API field residue | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E-095` | Schema construction and derivation remain separate | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-001` | Standalone Boolean negation uses word not | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-002` | Standalone bang Boolean negation is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-003` | Typed schema construction is current schema domain | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-004` | Type dollar is not constructor alias for ordinary class | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-005` | All named call layout separator stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-006` | Positional layout argument separator is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-007` | Rightward flow binding is stable dollar local | `accept` | `library` | `design_static_product_not_run` |
| `EX-R48E1-008` | Old rightward let target is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-009` | String interpolation factor and format are stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-010` | Interpolation member shorthand requires braces | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-011` | Bytes and named Unicode escape are stable design | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-012` | String to Bytes implicit conversion is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-013` | Visible Option some elision at explicit local target | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-014` | Broad Option lift remains rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-016` | Ordinary expression body remains rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-017` | Trailing closure suffix is stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-020` | typeof call form remains rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-021` | Ternary spacing law with ordinary operands | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-023` | R0 guard and source Boolean use word operators | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-024` | Bool double glyph operator rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-025` | Bitwise double glyph family stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-027` | Raw loop outcome arm rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-028` | Conformance declaration and explicit associated projection | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-029` | Structural conformance remains forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-030` | Async task actor minimum core stable design | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-031` | Dynamic unit conversion provider under stdlib profile | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48E1-032` | Raw first class witness remains not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48E1-033` | Standalone not in guard clause | `accept` | `library` | `design_static_product_not_run` |
| `EX-R48E1-034` | Yield guard and arrow binding cannot coexist | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-001` | @match direct expression arm result is current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-002` | @match block arm uses local ret | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-003` | return is not an @match arm result | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-004` | match guard pure predicate | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-005` | guarded arm is not exhaustive alone | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-006` | nullary lambda arrow elision with expected type | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-007` | empty nullary lambda needs expected type | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-008` | implicit @ lambda placeholder stable one-parameter context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-009` | implicit @ requires expected one-parameter function context | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-010` | NumericArray postfix transpose is Stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-011` | Neutral vector transpose requires orientation witness | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-012` | Inclusive slice range canonical | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-013` | Half-open slice is noncanonical ordinary style | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-014` | Complex vector dot product law | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-015` | Drop-preserving existential packaging | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-016` | Type schema construction is not constructor alias | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-017` | Type dollar is rejected when used as constructor alias | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48F-018` | Ternary spacing law with ordinary operands | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-020` | Stable typeof no preview gate | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-021` | Stable trailing closure no preview gate | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-022` | Stable #bytes literal | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-025` | String interpolation factor and format are current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-027` | Async function and await are current design | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-028` | Actor protocol request reply current design | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-029` | Yield guard current design | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48F-030` | Function semantic variance law current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-001` | R50b stable @match direct and block arm result | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-003` | R50b nullary lambda expected context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-004` | R50b implicit @ lambda is stable in expected one-parameter context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-005` | R50b NumericArray transpose is Stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-006` | NumericArray infix power requires current gate | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48G-007` | R50b inclusive slice canonical form | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-008` | R50b Type schema construction is not constructor call | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-009` | R50b current Option cases | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-010` | R50b current return and lambda ret | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48G-011` | R50b bare Some and None remain rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48H-001` | Trait witness slot markers open requirement and final helper | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48H-002` | Trait inherited witness slot override remains open | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48H-003` | Bodyless final witness requirement is Stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48H-004` | Trait method marker is required | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48H-005` | Trait final slot cannot be overridden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48H-006` | Implicit @ lambda stable expected one-parameter context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48H-007` | NumericArray orientation witness and A caret are Stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-001` | Type-side call uses double colon | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-002` | Dotted type-side call is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48L-003` | Associated projection uses double colon | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-004` | Dot associated projection is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48L-005` | Qualified extension selector uses double colon | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-006` | Full enum case qualification uses double colon | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-007` | Numeric power is right-associative | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-008` | NumericArray postfix transpose is Stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-009` | NumericArray infix power requires the Preview gate | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48L-010` | NumericArray infix power gated Preview | `accept_with_gate` | `script` | `design_static_product_not_run` |
| `EX-R48L-011` | Trait bodyless final witness requirement Stable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-012` | Trait associated item markers are Stable in the limited MSP | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-001` | Line comments are ignored to line end | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-002` | Nested block comments use //- and -// | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-003` | Documentation comments attach to declarations | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-004` | Shebang is allowed only as first-line script metadata | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-005` | Backtick word comments are Stable lossless trivia | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-006` | Backtick word comment cannot have whitespace after backtick | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48L-COMMENT-007` | Triple slash begins an ordinary line comment | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48M-ENUM-001` | Enum cases use bare declarations and \`::case\` expected shorthand | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48M-ENUM-002` | Full enum case path uses \`Type::case\` | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48M-ENUM-003` | Dot enum shorthand is no longer current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48M-ENUM-004` | \`case\` keyword in enum body is not canonical | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48M-ENUM-005` | Loop outcome match uses \`::break\` and \`::completed\` | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48M-SPREAD-001` | Record named-argument spread expands static labels | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48M-SPREAD-002` | Explicit named argument may combine with record spread without duplicates | `accept` | `script` | `design_static_product_not_run` |
| `EX-R48M-SPREAD-003` | Map cannot be expanded into named arguments | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48M-SPREAD-004` | Duplicate named argument from record spread is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R48M-SPREAD-005` | Record spread labels must match callable parameters | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-001` | Primary constructor promoted field visibility reaches current grammar | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-002` | All-named argument layout separator is current only for all-named calls | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-003` | Mixed positional layout remains rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-004` | Enum case expression payload is an argument list, not a declaration payload | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-005` | Enum pattern payload uses pattern payload plane | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-006` | Function type rest residue remains visible | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-007` | Named rest rejects Map feed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-008` | Type schema construction is schema-only | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-009` | Constructor-domain allocation still uses Type bang | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-ENUM-001` | Enum case pattern uses double colon shorthand | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-ENUM-002` | Dot enum case pattern is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-001` | Repeated positional parameter collects values | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-002` | Empty repeated call needs inference evidence | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-003` | Positional unfolding into repeated parameter | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-004` | Sequence unfolding into fixed parameters requires static arity | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-005` | Named rest parameter collects unmatched named arguments | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-006` | Named rest parameter must be last | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-PARAM-007` | Combined repeated and named rest call shape | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-PRIMARY-001` | Primary promoted field visibility sigils | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-PRIMARY-002` | Promoted field visibility applies to generated member only | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49-PRIMARY-003` | Promoted field visibility sigil must attach to storage keyword | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49-SPREAD-001` | Map cannot feed named rest or named argument spread | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-CHAR-001` | BMP Unicode scalar Char | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-CHAR-002` | Supplementary-plane Unicode scalar Char | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-CHAR-003` | Multi-scalar grapheme is not Char | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-CHAR-004` | Surrogate escape is not a Unicode scalar | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-CHAR-005` | Empty Char literal is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-CLASS-001` | Plain concrete class is final | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-CLASS-002` | Subclassing a default-final class is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-CLASS-003` | Open class explicitly admits subclasses | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-CLASS-004` | Abstract class is open and non-instantiable | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-DYNTRAIT-001` | Dynamic trait attach syntax remains non-current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-ESC-001` | Escaped hard-keyword member | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-ESC-002` | Escaped external identifier member | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-ESC-003` | Plain-dot hard keyword member is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-ESC-004` | Member escape requires adjacency | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-ESC-005` | Member escape cannot declare a local | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-EXT-001` | Extension-set member uses plain def; call retains tilde | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-EXT-002` | Superseded tilde declaration inside extension set | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-EXT-003` | Extension does not auto-create witness | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-EXT-004` | Conformance explicitly delegates to identified extension | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-EXT-006` | Source and use order cannot break selector ambiguity | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-OPTION-001` | Nested optionality is explicit | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-OPTION-002` | Repeated compact optional suffix is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-REST-001` | Named rest collects static Record labels | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-REST-002` | Map cannot feed named rest | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-ROW-001` | Effect and error rows use visible bar union | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-ROW-002` | Tokenless effect-row adjacency is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-SEALED-001` | Sealed hierarchy closes direct subclasses to one module | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49B-SEALED-002` | Sealed direct subclass outside module is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49B-SEALED-003` | Sealed direct subclass must state its disposition | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-001` | Option coalescing unwraps one layer lazily | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-002` | Right-associated fallback chain | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-003` | Nested Option removes exactly one layer | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-004` | Coalescing does not discard Result failure | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-005` | Coalescing requires an Option left operand | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-006` | Coalescing token is adjacent | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-007` | Affine payload extraction moves the owned Option | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-COALESCE-008` | Borrowed affine Option cannot yield owned payload | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-ENTRY-001` | Explicit entry has no magic name | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R49C-ENTRY-002` | Implicit script entry and explicit entry conflict | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-LAMBDA-001` | Lambda-only unparenthesized parameter list | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-LAMBDA-002` | Lambda list-level parentheses are removed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-LINALG-001` | Linear-product chain folds left | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-MAT-001` | Schema materialization and named unfolding | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-MAT-002` | Generated final data class materializes by labels | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-MAT-003` | Data class has no automatic named unfolding | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-MAT-004` | Map is not static named-unfold evidence | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-MATCH-001` | Value matching uses at-match only | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-MATCH-002` | Bare match cannot initialize a value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-MATCH-003` | Bare match remains a statement with guards | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-001` | Closed numeric literal positive matrix | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-002` | Invalid binary digit | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-003` | Separator cannot follow radix prefix | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-004` | Consecutive numeric separators are invalid | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-005` | Exponent requires digits | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-006` | Integer suffix cannot follow decimal fraction | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-007` | Radix float is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-NUM-008` | Non-finite values use type-side constants | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-PROJ-001` | Optional suffix attaches to associated projection | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-PROJ-002` | Associated projection parentheses are redundant | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-RESULT-001` | Result error argument is a grammar-visible channel | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-RETURN-001` | Canonical Unit fallthrough omits final return | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-RETURN-002` | Early valueless return remains meaningful | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-SCRIPT-001` | Selected script root executes ordered top-level statements | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-SCRIPT-002` | Library rejects loose top-level computation | `reject` | `library` | `design_static_product_not_run` |
| `EX-R49C-SEALED-001` | Canonical sealed-class hierarchy | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-SEALED-002` | Removed hash-combined sealed spelling | `reject` | `script` | `design_static_product_not_run` |
| `EX-R49C-STATIC-001` | Module static initializer is nonactivatable | `reject` | `library` | `design_static_product_not_run` |
| `EX-R49C-STRING-001` | Interpolation has explicit lexer-mode parts | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-TILDE-001` | Extension member declares a plain selector | `accept` | `script` | `design_static_product_not_run` |
| `EX-R49C-TILDE-002` | Leading tilde is forbidden in member declaration | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51COH-SHARED-001` | SharedCell scoped observation and owner replacement | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51COH-SHARED-002` | SharedMutex receiver-bound non-suspending scoped mutation | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-001` | Unsuffixed and suffixed numeric values keep exact domains | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-002` | Compound assignment evaluates one mutable place and commits once | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-003` | Option none is the only current absence value | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-004` | Ordinary and bounded logical domains remain explicit | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-005` | String and Bytes indexing use one-based scalar coordinates | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-006` | Map indexing remains in the exact key domain | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-007` | NumericArray built-in axes are typed and one-based | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-008` | Inclusive slices and anchors preserve source coordinates | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-009` | Explicit exclusive slice end is accepted with a warning | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-001` | null is reserved recovery, not a value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-002` | custom operator declarations are not current | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51VOI-NG-003` | Trait conformance cannot activate a fixed glyph | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51VOI-NG-004` | descending range glyph is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-005` | ellipsis is not an expression range operator | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-006` | an empty index suffix never implies a full slice | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-007` | NumericArray zero is outside every built-in positional axis | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-008` | mixed numeric widths require an explicit conversion | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51VOI-NG-009` | mutable slice assignment is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-001` | role-specific executable entry | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-002` | sealed class is the only current spelling | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-003` | canonical lambda parameter list | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-004` | value @match and statement match | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-005` | Unit terminal fallthrough | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-006` | closed numeric lexical matrix | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-007` | Bytes mode and named Unicode escape | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-008` | indexed interpolation shorthand and braced member access | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-009` | ordinary immutable list literal | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-010` | all-named newline argument layout | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-011` | primary constructor promoted-field layout | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-012` | annotation attaches structurally | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-013` | enum cases and enum members | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-014` | narrow explicit witness parameter and coherent call channel | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-015` | typed labeled materialization | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-016` | prototype derivation body | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-017` | lazy Option coalescing | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-018` | declarative clause body | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-019` | cleanup declaration has exact empty parameter list | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-020` | qualified static selector classification | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-021` | static-pure library binding | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-022` | rank-three exact-shape separator runs | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-023` | comma plus newline materialization and map entries | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-024` | nested local function with explicit outer capture | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-025` | task body owns a final await expression | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-026` | capture list attaches through an explicit closure mode | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-027` | postfix transpose continues through every suffix boundary | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-028` | multiline named call remains comma-form when commas are present | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-029` | multiline primary constructor and constrained schema remain comma-form | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-030` | ordinary function returns a lambda without entering clause-body mode | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-031` | layout schema gives every refinement to SchemaConstraint | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-032` | layout call ignores commas owned by an exact-shape argument | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-033` | layout declarations ignore shape and generic child commas | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-034` | ordinary parameter binds an identifier before body pattern control | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-035` | implicit lambda receiver reuses common postfix suffixes | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-036` | await has one unary-tier owner | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-037` | message suffix maximally owns immediate arguments and closures | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-038` | same-line module signature head selects the signature declaration | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-039` | explicit terminator permits a module named signature | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-040` | newline breaks the contextual sealed-class phrase | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-041` | optional data-class and trait braces belong to their declarations | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-042` | parentheses separate a lambda from a bodyless declaration | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-043` | cleanup budget maximally remains in the data-class header | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-044` | value-arm newline separates an open range from the next qualified pattern | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-045` | associated where binds inside some-trait before an outer function where | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-046` | refinement and contract predicates cannot absorb outer initialization or bodies | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-047` | measure and sharp-shape brackets use distinct opener tokens | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-048` | adjacent double caret is xor rather than two transpose tokens | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-049` | ordinary List inference and exact contextual integer adaptation | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-050` | extension-pack module interface has a current rooted route | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-051` | lone wildcard and underscore-prefixed identifiers are lexically disjoint | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-052` | control body owns its first brace and a condition trailing closure is parenthesized | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-053` | List suffix, target-size, boundary, empty-context, and nonnumeric identity admissions | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-054` | entry no-argument Unit shape | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-055` | entry argv Unit shape | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-056` | entry no-argument ExitCode shape | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-057` | async entry uses the exact argv ExitCode shape | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-058` | nested block comment dash-run mismatch remains valid | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-059` | explicit borrow inout and move modes | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-060` | Result and throws use disjoint recoverable error families | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-061` | closed R0 refinement predicate | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-062` | exact normalized named call shape | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-063` | type token is used only by static selection | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-064` | exact unit core normalizes equivalent linear dimensions | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-065` | explicit reusable authority-free context value | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-066` | stable async declaration and iteration need no preview gate | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-067` | terminal bare return is admitted with a noncanonical lint | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-ACOLLECT-NG-001` | Stage-1 collector rejects an AsyncSequence without finite-source evidence | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-ACOLLECT-P-001` | Stable Stage-1 policy-visible async collector | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-003` | context-free implicit nullary lambda | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-004` | flow binding cannot target a member | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-005` | two unlabeled trailing closures | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-006` | multi-statement local value body without ret | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-007` | old async declaration prefix | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-008` | old entry declaration prefix | `reject` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-009` | old drop spelling | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-010` | old caller callable profile | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-011` | callable profile must attach to brace | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-012` | callable profile order is closed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-013` | callable profile cannot repeat | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-014` | mutable and pure profiles conflict | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-015` | once mutable combination is not Phase A | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-016` | pure callable cannot throw | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-017` | pure callable cannot capture mutable state | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-018` | guard callable result is Bool | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-019` | guard callable cannot consume | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-020` | scoped callable cannot escape | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-021` | profiles alone cannot distinguish overloads | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-022` | sync callable literal marker is redundant and absent | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-023` | async callable literal remains nonactivatable | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-024` | cleanup declaration is not directly callable | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-025` | context anchor requires a registered evidence role | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-026` | conformance evidence must be unique | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-027` | dynamic extension dispatch remains forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-028` | explicit broadcast marker remains absent | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-029` | generator borrow capture cannot escape | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-030` | named arguments use colon | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-031` | empty slice range uses wildcard | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-032` | bare parenless ordinary call remains forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-033` | old dotted bitwise operator remains removed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-AUD-NG-034` | value-producing @if requires else | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BITFIELD-NG-001` | Bitfield layout requires exact closure | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BITFIELD-NG-002` | Implicit raw conversion forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BITFIELD-P-001` | Strict unsigned bitfield declaration | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BITFIELD-P-002` | Bitfield materialization and derivation | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BITFIELD-P-003` | Checked raw conversion with explicit result | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BOUND-NG-001` | Bounded list rejects call-only arguments | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-BOUND-P-001` | Stable bounded one-based logical domain | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-DEFER-001` | defer registers one cleanup invocation | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-DEFER-NG-001` | arbitrary defer block is removed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-EVIDENCE-NG-001` | named conformance is excluded from automatic search | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-EVIDENCE-NG-002` | evidence selector is not a value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-EVIDENCE-P-001` | Stable named conformance declaration | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-EVIDENCE-P-002` | Stable named static evidence selector | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-FACET-NG-001` | borrow Facet cannot escape its region | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-FACET-P-001` | Stable Borrow Facet seals evidence without changing the object | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-FLAGS-NG-001` | Flags result is not Bool | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-FLAGS-P-001` | Finite-universe flags declaration | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-FLAGS-P-002` | Flags operations preserve nominal type | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-GLET-NG-001` | guarded let failure pattern must cover the residual domain | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-GLET-P-001` | Stable guarded let preserves the failure payload | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-GUARDED-NG-001` | Guarded let conditional exit is forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-GUARDED-P-001` | Guarded let direct unconditional exit | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-GUARDED-P-002` | Guarded let exact residual exit | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-IMPORT-NG-001` | local import cannot mean runtime loading | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-IMPORT-NG-002` | scoped import block is not an expression | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-IMPORT-P-001` | Stable block-local import is prologue-only | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-IMPORT-P-002` | Stable scoped import limits name visibility | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INDEX-001` | ordinary sequences use one-based logical indices | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INDEX-NG-001` | sequence index zero is outside the logical domain | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INTERPOLATION-NG-001` | Ordinary sequence interpolation remains one-based | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INTERPOLATION-P-001` | Unicode interpolation boundary and read-only path | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INTERPOLATION-P-002` | Structured render with one-based collection selectors | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INTERSECT-NG-001` | two concrete bases cannot be intersected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-INTERSECT-P-001` | Stable closed contract intersection | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-LAZY-NG-001` | Lazy initialization cycle is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-LAZY-P-001` | Stable pure call-by-need binding | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NAMEDREST-NG-001` | Old double-star collector is recovery-only | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NAMEDREST-P-001` | Canonical named-rest collector uses triple star | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-002` | canonical asynchronous entry introducer | `accept` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-NEW-003` | named rest collector and named unfold are distinct | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-004` | function type retains repeated and named rest channels | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-005` | typed immutable flow binding | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-006` | typed mutable flow binding | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-007` | single unlabeled trailing closure | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-008` | multiple callbacks are ordinary named arguments | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-009` | explicit nullary lambda without expected callable | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-010` | single-expression local value body | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-011` | multi-statement local value body uses ret | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-012` | scoped callable lifetime profile | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-013` | pure callable behavior profile | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-014` | guard callable behavior profile | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-015` | mutable callable environment profile | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-016` | closed composite callable profile | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-017` | async named declaration profile | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-018` | guard named declaration profile | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-020` | cleanup declaration preserves failure policy | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-021` | root conformance evidence selector | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-022` | readonly view lifetime | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-023` | unique Box owner | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-024` | replace evaluates a place once | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-025` | mutable-list snapshot precedes consuming freeze | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-026` | owned downcast preserves unmatched source | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-027` | guarded transfer evaluates guard before payload | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NEW-028` | loop owns one outcome handler | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-029` | implicit placeholder is checked after overload selection | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-030` | scoped pure callback in Prelude | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NEW-031` | ByteView remains owner-bounded | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-001` | rejected: optional chaining | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-002` | rejected: optional callable invocation | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-003` | rejected: dotted static path | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-004` | rejected: where T : Trait | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-005` | rejected: structural conformance | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-006` | rejected: extension auto-witness | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-007` | rejected: raw first-class Witness value | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-008` | rejected: ordinary \`def = expr\` body | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-009` | rejected: standalone !expr | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-010` | rejected: unnamed def!(...) constructor | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-011` | rejected: bodyless ordinary function | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-012` | rejected: standalone annotation statement | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-013` | rejected: ordinary List literal without an admitted element join | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-014` | rejected: incoherent witness identity whose resolved trait does not match the explicit witness parameter | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-015` | rejected: effectful or mutable library top-level binding | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-016` | rejected: entry outside the four admitted signatures | `reject` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-NG-017` | rejected: stored field/constructor/drop inside enum | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-018` | rejected: semicolon run that does not match the exact-shape NumericArray rank boundary | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-019` | rejected: computed expression after the using keyword | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-020` | rejected: entry declaration in a library source, including an annotated entry | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-021` | rejected: top-level let/var in an executable source | `reject` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-NG-022` | rejected: extern#C def#unsafe without its current gate | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-023` | rejected: extern c block without its current gate | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-024` | rejected: dynamic unit conversion without active stdlib profile | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-026` | rejected: explicit entry declaration inside a script source | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-027` | rejected: unknown feature id in #preview | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-028` | rejected: PREVIEW_DESIGN id in #preview | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-029` | rejected: duplicate feature id in #preview | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-030` | rejected: missing explicit Preview dependency | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-031` | rejected: #preview after ModuleDecl or a source item | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-032` | rejected: top-level visibility modifier on a local function | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-033` | rejected: implicit outer capture by a local function | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-034` | rejected: local function reference before declaration | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-035` | rejected: CaptureList separated from its owner by NEWLINE | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-036` | rejected: radix-prefixed NumericArray static dimension | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-037` | rejected: suffixed NumericArray static dimension | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-038` | rejected: numeric radix prefix without a digit | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-039` | rejected: ordinary List literal mixing unsuffixed Int and suffixed u8 without context | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-040` | rejected: ordinary List literal mixing suffixed i8 and unsuffixed Int without context | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-041` | rejected: ordinary List literal mixing Int and Float64 without context | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-042` | rejected: out-of-range unsuffixed integer in a fixed-width contextual List | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-043` | rejected: lone underscore used where a declaration Identifier is required | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-046` | rejected: explicit witness parameter returned as an ordinary value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-047` | rejected: explicit witness parameter stored in a local binding | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-048` | rejected: explicit witness parameter captured by a closure | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-049` | rejected: explicit witness parameter passed through an ordinary argument channel | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-050` | rejected: ordinary forged value supplied as explicit witness evidence | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-051` | rejected: empty ordinary List literal without a fixed context | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-052` | rejected: unsuffixed Float64 literal in a contextual List<Float32> | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-053` | rejected: unsuffixed Int literal in a contextual List<ISize> | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-054` | rejected: out-of-range negative literal in a contextual List<Int8> | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-055` | rejected: negative literal in a contextual List<UInt8> | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-056` | rejected: explicit witness parameter assigned into a field | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-057` | rejected: explicit witness parameter inserted into a container | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-058` | rejected: cyclic library top-level let initializer graph | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-059` | rejected: library top-level let initializer that creates a task | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-060` | rejected: generic entry function | `reject` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-NG-061` | rejected: two selected entry declarations in one executable root | `reject` | `executable` | `design_static_product_not_run` |
| `EX-R51a1-NG-062` | rejected: constructor declaration inside an enum | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-063` | rejected: drop declaration inside an enum | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-064` | rejected: assignment-compatible subtype in a contextual List without normalized-type identity | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-065` | rejected: top-level static class declaration | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-066` | rejected: top-level static def declaration | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-067` | rejected: stored field inside an extension set | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-068` | rejected: one recoverable error family exposed through both Result and throws | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-069` | rejected: effectful or authority-bearing R0 refinement predicate | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-070` | rejected: duplicate or unknown named call shape | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-071` | rejected: type token used as a runtime reflective value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-072` | rejected: live inout borrow crossing await without proof | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-073` | rejected: dynamic unit exponent in the exact canonical core | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-074` | rejected: resource or authority-bearing context value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-075` | rejected: deep prototype derivation without deep-clone responsibility | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-076` | rejected: automatic ConstructionRow requested for an ineligible data class | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-NG-077` | rejected: matrix product with mismatched inner dimensions | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-NG-078` | rejected: mixed linear-product fold whose matrix result is used as a dot-product vector | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-FACET-NG-001` | Concrete-payload Facet spelling removed | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-FACET-P-001` | Canonical borrow Facet | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-INTERSECTION-NG-001` | Bare contract bundle is not a value carrier | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-INTERSECTION-P-001` | Concrete contract intersection | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-LAZY-NG-001` | Lazy hidden throw channel forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-LAZY-P-001` | Fallible lazy computation uses explicit Result | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-UNION-NG-001` | Automatic union join is forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RCTS-UNION-P-001` | Explicit closed union and exhaustive match | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RECEIVER-001` | Explicit consuming receiver-owner result | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RECEIVER-NG-001` | Implicit receiver result forbidden | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RENDER-NG-001` | Explicit and implicit renderer parameters cannot mix | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RENDER-P-001` | String render through braced implicit-at expression | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-RENDER-P-002` | Nested render binds the nearest implicit at | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-SLICE-001` | slice preserves selected logical coordinates | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-SLICE-NG-001` | preserved slice coordinates reject an out-of-domain index | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-TUPLE-001` | tuple ordinal projection is compile-time and one-based | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-TUPLE-NG-001` | tuple ordinal zero is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-UNION-NG-001` | union value requires narrowing | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-UNION-P-001` | Stable closed anonymous union | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-USE-001` | block-prologue use narrows lexical activation | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51a1-USE-002` | scoped use block is a lexical statement | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51a1-USE-NG-001` | use cannot acquire runtime authority | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51a1-USE-NG-002` | scoped use cannot be used as a value | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-001` | Old double-star named-rest collector is recovery-only | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-002` | At-sigil lazy spelling is recovery-only | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-004` | Unit middle dot is recovery-only | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-005` | Ordinary class requires a body | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-006` | Ret is not a generic block tail | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-007` | Guarded-let failure cannot use ret | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-008` | Defer block is not current | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-009` | Match arm admits at most one guard | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-010` | Standalone subjectless match is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-011` | Async for does not own an outcome match | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-012` | Cast modifier cannot contain trivia | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-013` | Negated relation cannot contain trivia | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-014` | Interpolation shorthand call requires braces | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-NG-015` | Exact at introducer cannot cross a physical line | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-001` | Named rest and named unfold have distinct markers | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-002` | Lazy binding uses the hash role | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-003` | Unit products use star and slash | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-004` | Data class may omit its body | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-005` | Typed binding pattern is current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-006` | Defer registers one cleanup invocation | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-007` | Subjectless match is owned by the preceding loop | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-008` | Checked cast and negated relations are attached parser sequences | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-009` | Full interpolation shorthand path is current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51b-GRAM-P-010` | Hash role trivia is accepted and formatter-normalized | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c-001` | Named rest uses triple-star while named unfold uses double-star | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c-002` | Double-star named-rest parameter is removed | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c-003` | Class instance methods require dispatch markers; fields do not | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c-004` | Missing class dispatch marker is rejected | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c-005` | Stored fields cannot be virtual | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c-006` | Trait method marker and unmarked associated requirements | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c-007` | Associated non-method marker is rejected | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c-008` | Full read-only interpolation path | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51c-009` | Interpolation calls require braces | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51c-010` | Caret transpose and power have distinct attachment | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51c-011` | Mixed caret attachment is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51c-012` | Declarative clauses explicitly cover Option | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c-013` | Option does not supply an implicit missing arm | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c-014` | Law body contains pure assertions only | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c-015` | Effectful law statement is rejected | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c-016` | Message spawn is owned by ordinary message syntax | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51c-017` | Shallow and deep same-type derivation | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51c-018` | Calendar conversion needs explicit stdlib provider context | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51c-019` | Dynamic RCTS source activation remains unavailable | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51c-020` | Source root cannot ignore trailing tokens | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51c1-001` | Named-rest parameter uses attached triple-star | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c1-002` | Function type preserves triple-star named-rest residue | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51c1-003` | Named unfold alone uses prefix double-star | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51c1-004` | Double-star named-rest parameter is removed | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c1-005` | Double-star function-type residue is removed | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51c1-006` | Triple-star cannot be used as named unfold | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51d-001` | Raw String Phase A preserves body text | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51d-002` | Alternate raw delimiter family is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51d-003` | Rightward immutable binding normalizes to let | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51d-004` | Rightward mutable binding normalizes to var | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51d-005` | Rightward binding evaluates a move-only initializer once | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51d-006` | Rightward target must be a fresh identifier | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51d-007` | Hash role admits same-line trivia | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51d-008` | Hash role cannot cross a physical newline | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51d-009` | Rightward chaining is rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51d-010` | Named function value uses explicit return shorthand | `accept` | `library` | `design_static_product_not_run` |
| `EX-R51d-011` | Named function bare expression body is rejected | `reject` | `library` | `design_static_product_not_run` |
| `EX-R51d-012` | Dynamic unit profile must be active | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51d-013` | Dynamic unit profile needs an explicit provider | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-001` | Materialization field pun | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-002` | Unbound materialization field pun rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-003` | Grouped forwarding | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-004` | Grouped forwarding collision rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-005` | Scoped grouped use | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-006` | Scoped activation requires in | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-007` | Dedented multiline Unicode String | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-008` | Multiline closer placement rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-009` | One-line enum case comma list | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-010` | Multiline enum comma list rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-011` | Single transfer guard | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-012` | Guard chain rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-013` | If-let transactional binding | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-014` | While-let transactional binding | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-015` | For-let filters candidates | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51e-016` | Irrefutable pattern control rejected | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-017` | Quarantine scope is nonactivatable | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51e-018` | Quarantine escape design boundary | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f-001` | Map String key uses explicit indexing | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f-002` | Map dot-key projection is not member lookup | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f-003` | Explicit assignment replaces increment | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f-004` | Postfix increment is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f-005` | Ordinary recursive function | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f-006` | Tail-recursion callable kind is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f-007` | Raw String can carry pattern text | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f-008` | Regex literal prefix is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f-009` | Explicit expected List union | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f-010` | Automatic heterogeneous List union is absent | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-001` | List pattern commits only after an admitted final ignored remainder probe | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-002` | For-let probe binder guard requires Bool before commit | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-003` | Tuple decomposition pattern is not current | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-004` | Statement try may use finally as its required terminal owner | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-005` | Bare statement try has no current failure owner | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-006` | Strict Boolean control accepts only Bool operands | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-007` | Array and case remain ordinary identifiers | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-008` | Bounded actor channel keeps send order and explicit request reply | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-009` | Actor mailbox capacity must be a positive static bound | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-010` | Cancellation is not recoverable through catch | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-011` | Structured task cleanup remains owned at cancellation boundary | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-COH-012` | Omitted mailbox clause selects logical-unbounded admission | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-R2-001` | Strict Boolean operands must be Bool | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-R2-002` | Sequential Boolean operands must be Bool | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-R2-003` | Ternary question mark requires spacing | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-R2-004` | Short single-line ternary is current | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-R2-005` | Bytes literal hex escape requires two hex digits | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-R2-006` | Interpolation format requires braced form | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-UNION-ISTEST-NG-001` | is rejects a subject that is not one closed Union | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-UNION-ISTEST-NG-002` | is rejects a target that is not one exact Union alternative | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-UNION-ISTEST-NG-003` | is cannot participate directly in a comparison chain | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-UNION-ISTEST-P-001` | closed Union is narrows the and then right-hand side | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-UNION-ISTEST-P-002` | closed Union !is tests the exact complementary alternative set | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-VIS-BOUNDARY-001` | Non-type top-level omission defaults to private | `accept` | `script` | `design_static_product_not_run` |
| `EX-R51f3-VIS-NG-001` | Preview-root type omission admits zero identities | `reject` | `script` | `design_static_product_not_run` |
| `EX-R51f3-VIS-P-001` | Exact type-producing owners use explicit visibility | `accept` | `library` | `design_static_product_not_run` |
