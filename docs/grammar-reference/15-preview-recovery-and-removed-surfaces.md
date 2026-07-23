<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# Preview, 복구 및 제거된 표면

<!-- deeplus-status-fence: CURRENT -->

## 상태

이 장은 현행 Stable 언어가 아닌 표면을 한곳에서 분류한다. “도입을
검토할 수 있을 정도로 설계가 구체적임”, “명시적 gate로 현재 소스에서
사용할 수 있음”, “제품 구현이 실행됨”은 서로 다른 상태다.

이 장의 Preview 설계 문서화는 구문, 구현, 제품 지원 또는 활성화 권위를 부여하지 않는다.

| 분류 | 현재 관측값 | 소스 의미 |
|---|---:|---|
| feature registry의 `PREVIEW` | 3 | `explicit_feature_gate`가 있는 Preview 루트에서만 허용 가능 |
| feature registry의 `PREVIEW_DESIGN` | 47 | 모두 `nonactivatable`; Stable/Preview parser route 없음 |
| EBNF `PREVIEW` profile | 13 production | Preview 루트, gate 및 FFI 구조 |
| EBNF `RECOVERY` profile | 15 production | 진단 인식 전용; 허용된 AST/HIR/MIR residue 0 |
| gate map의 activatable entry | 3 | FFI 2개와 NumericArray elementwise power 1개 |
| 제품 lane | 15/15 `NOT_RUN` | 정적 설계와 예제만으로 실행을 주장하지 않음 |

이 장은 상태·governance·review-card의 단일 장부다. 각 기능의 동기,
표면 후보, 판정, 평가·소유권·오류, 현행 대안, migration 및 활성화
선행 조건과 예제는 다음 상세 장에서 읽는다.

- [Preview Gated 상세 참조](20-preview-gated-reference.md): 실제
  `#preview(...)` route가 있는 3개
- [Preview Design — 타입, 객체 및 Trait](21-preview-design-types-objects-and-traits.md)
- [Preview Design — 컬렉션, 문맥 및 제어](22-preview-design-collections-context-and-control.md)
- [Preview Design — 동시성, FFI 및 런타임](23-preview-design-concurrency-ffi-and-runtime.md)

semantic P0는 `0`이다. OPEN feature P1은 Class 6개,
Enumeration 8개, Trait Conformance 7개, `SFD-P1-009` 1개로 정확히
22개다. `M13-A002..005`는 이 22개에 합치지 않는 별도 OPEN action이다.
문서 생성, 정적 표, schema 또는 예제의 존재로 닫히는 P1은 0개다.

15개 제품 lane은 `rust_frontend_lexer`, `rust_frontend_parser`,
`rust_hir_lowering`, `rust_integrated_checker`, `deeplus_mir_lowering`,
`xvm_bytecode_emitter`, `xvm_interpreter`, `llvm_aot_backend`,
`llvm_orc_jit_backend`, `formatter_lsp`, `stdlib_provider_runner`,
`official_tooling`, `independent_conformance`, `cross_backend_conformance`,
`actual_user_team_study`이며 모두 `NOT_RUN`이다.

다음 블록은 위 상태를 `current/current-pointer.json`과 정확히 대조하기
위한 기계 판독형 투영이다. 사람이 읽는 ledger와 이 블록이 다르면
생성기는 참조서 생성을 거부한다.

<!-- deeplus-governance-invariants: begin -->
```json
{
  "semantic_p0": 0,
  "feature_p1_status": "OPEN",
  "feature_p1_ids": [
    "CE-C-P1-001",
    "CE-C-P1-002",
    "CE-C-P1-003",
    "CE-C-P1-004",
    "CE-C-P1-005",
    "CE-C-P1-006",
    "CE-E-P1-001",
    "CE-E-P1-002",
    "CE-E-P1-003",
    "CE-E-P1-004",
    "CE-E-P1-005",
    "CE-E-P1-006",
    "CE-E-P1-007",
    "CE-E-P1-008",
    "TCC-P1-002",
    "TCC-P1-003",
    "TCC-P1-004",
    "TCC-P1-005",
    "TCC-P1-006",
    "TCC-P1-007",
    "TCC-P1-008",
    "SFD-P1-009"
  ],
  "separate_action_status": "OPEN",
  "separate_open_action_ids": [
    "M13-A002",
    "M13-A003",
    "M13-A004",
    "M13-A005"
  ],
  "product_lanes": {
    "rust_frontend_lexer": "NOT_RUN",
    "rust_frontend_parser": "NOT_RUN",
    "rust_hir_lowering": "NOT_RUN",
    "rust_integrated_checker": "NOT_RUN",
    "deeplus_mir_lowering": "NOT_RUN",
    "xvm_bytecode_emitter": "NOT_RUN",
    "xvm_interpreter": "NOT_RUN",
    "llvm_aot_backend": "NOT_RUN",
    "llvm_orc_jit_backend": "NOT_RUN",
    "formatter_lsp": "NOT_RUN",
    "stdlib_provider_runner": "NOT_RUN",
    "official_tooling": "NOT_RUN",
    "independent_conformance": "NOT_RUN",
    "cross_backend_conformance": "NOT_RUN",
    "actual_user_team_study": "NOT_RUN"
  }
}
```
<!-- deeplus-governance-invariants: end -->

## 문법

<!-- deeplus-status-fence: PREVIEW_GATED -->

### source-gated Preview 루트

Preview source는 Stable source와 다른 루트를 선택하고, 선택적 shebang
직후이자 `ModuleDecl`과 모든 source item보다 앞에 정확한 gate를 둔다.

```ebnf
DeeplusPreview ::= PreviewLibrarySourceFile
                 | PreviewExecutableSourceFile
                 | PreviewScriptSourceFile ;
PreviewLibrarySourceFile ::= PreviewGate ModuleDecl? PreviewLibraryItem* ;
PreviewExecutableSourceFile ::= PreviewGate ModuleDecl? PreviewExecutableItem* ;
PreviewScriptSourceFile ::= Shebang? PreviewGate ModuleDecl? PreviewScriptItem* ;

PreviewGate ::= "#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary ;
PreviewFeatureList ::= Identifier ("," Identifier)* ;
```

현행 gate map의 전체 activatable 집합은 다음 세 행이다.

| 기능 ID | 경로 | gate 특성 |
|---|---|---|
| `ffi_minimum_sound_profile` | `PreviewFfiFunctionDecl` | FFI 최소 soundness profile |
| `ffi_c_extern_unsafe_surface_msp` | `PreviewFfiFunctionDecl`, `PreviewFfiBlockDecl` | 위 profile을 명시적 의존성으로 함께 요구 |
| `numeric_array_elementwise_power_msp` | 의미 route `PrattExpr` | 새 CFG production 없이 checker가 infix `A ^ n`을 gate |

`#preview(...)`는 알려진 ID를 나열하는 일반 feature switch가 아니다.
registry에서 `status_enum = PREVIEW`이고
`source_activation = explicit_feature_gate`인 기능만 쓸 수 있다.
`PREVIEW_DESIGN` ID는 gate에 적어도 활성화되지 않는다.

### Preview FFI 문법

```ebnf
PreviewFfiDecl ::= PreviewFfiFunctionDecl | PreviewFfiBlockDecl ;
PreviewFfiFunctionDecl ::= "extern" "#" "C" "def" "#" "unsafe"
                           Identifier ParameterList ReturnClause?
                           ThrowsClause? EffectsClause? StatementBoundary ;
PreviewFfiBlockDecl ::= "extern" "c" "(" PLAIN_STRING_LITERAL ")"
                        "{" PreviewFfiBlockMember* "}" ;
PreviewFfiBlockMember ::= "unsafe" "def" Identifier ParameterList
                          ReturnClause? ThrowsClause? EffectsClause?
                          StatementBoundary ;
```

FFI와 unsafe의 상세 soundness 경계는 [FFI, unsafe, 메타프로그래밍 및
프로필](14-ffi-unsafe-metaprogramming-and-profiles.md)에 있다.

<!-- deeplus-status-fence: RECOVERY_ONLY -->

### Recovery overlay

Recovery root는 별도 프로그램 종류가 아니며 Stable/Preview parse 실패를
의미론적으로 수선하지 않는다.

```ebnf
RecoverySyntax ::= RecoveryGenericEntryFunctionDecl
                 | RecoveryFacetPackExpr
                 | RecoveryFacetType
                 | RecoveryNullLiteral
                 | RecoveryEmptyIndexSuffix
                 | RecoveryCustomOperatorDeclaration
                 | RecoveryNamedRestDoubleStar
                 | RecoveryFunctionTypeNamedRestDoubleStar
                 | RecoveryLazyBindingAt
                 | RecoveryUnitMiddleDot
                 | RecoveryQuarantineScope ;
```

47개 `PREVIEW_DESIGN` feature 가운데 quarantine과 owned/inout Facet
family만 현재 Recovery overlay에 직접 대응하는 형태가 있다.
`dynamic_unsafe_quarantine_scope_msp`는 `RecoveryQuarantineScope`의 정밀
진단 probe를 사용하고, owned/inout Facet은 `RecoveryFacetPackExpr`와
`RecoveryFacetType`을 사용한다. 현재 허용되는 Facet은 borrow뿐이다.
나머지 설계는 exact EBNF가 없는 design-only 상태이며, 문서가 임의
production을 발명해서는 안 된다.

## 허용과 정적 의미

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### `PREVIEW_NONACTIVATABLE` 공통 법칙

비활성 Preview 설계를 registry에 보존하는 이유는 거부가 확정되었기
때문이 아니라, 현재 권위를 바꾸지 않은 채 도입 판단을 가능하게 하기
위해서다. 각 설계는 다음 공통 경계를 따른다.

- 현행 Stable source, current lowercase `via`, Enum marker
  `.`, `+`, `*.`, `*+`, borrow Facet 및 intrinsic-only operator dispatch를
  변경하지 않는다.
- 정확한 source route가 없는 경우 후보 철자를 예시할 수는 있어도
  current syntax라고 가르치지 않는다.
- parser-cover grammar가 `false`인 설계는 Recovery가 대신 활성화하지
  않는다.
- 문서, fixture, schema, registry 행은 P1, 구현 또는 product lane을
  닫지 않는다.
- source activation에는 Design_ 판정, exact EBNF와 root/profile,
  frontend owner/admission, diagnostic, formatter/LSP, migration, MIR 및
  target-bound evidence가 별도로 필요하다.

### Registry 전체 분류 — async, 동시성 및 상태

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `async_callable_literal_profile` | `#async` callable literal family; exact EBNF 미선정 | call/return, cancellation, capture, lowering, ABI를 닫아야 하며 ordinary lambda는 동기 호출 |
| `async_comprehension` | exact source surface 미선정 | iteration, failure order, cancellation, ownership 및 collection/stream 결과 identity 필요 |
| `automatic_observation_tracking` | 자동 dependency observation API 미선정 | observation identity, mutation invalidation, lifetime, isolation 및 hidden authority 금지 필요 |
| `directed_coroutine_group` | exact source route 미선정 | direction, structured scope, cancellation, cleanup 및 gated fixture가 없음 |
| `session_protocol_lite_provider` | core syntax가 아닌 provider 후보 | protocol identity, duality, message order, cancellation 및 actor mailbox 결합을 별도 정의해야 함 |
| `state_machine_source_syntax` | exact source syntax 미선정 | 현행 `uml_state_machine_provider`는 ordinary source를 생성하는 도구일 뿐 새 syntax가 아님 |
| `weak_atomic_ordering` | ordering spelling/API 미선정 | closed memory model, happens-before, compiler reorder 한계, litmus 및 xVM/LLVM receipt 필요 |

### Registry 전체 분류 — FFI, Dyn 및 Facet

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `c_aggregate` | C aggregate mapping profile; source/API 미선정 | field layout, padding, alignment, ownership 및 target ABI가 열려 있음 |
| `c_stored_callback` | stored callback profile; source/API 미선정 | capture lifetime, thread/isolation, reentrancy, revoke 및 cleanup owner 필요 |
| `c_variadic` | C variadic profile; source/API 미선정 | promotion rules, sentinel/count, representability 및 ABI별 lowering 필요 |
| `dyn_inspection` | privileged inspection service 또는 checked API 미선정 | static type·label·conformance·authority를 만들어서는 안 되며 effect/ownership surface가 열려 있음 |
| `dyn_rcts_family` | explicit owned Dyn checked-carrier family; exact syntax 미선정 | ambient dynamic fallback, structural conformance 및 dynamic Trait mutation은 금지 |
| `dynamic_trait_attach_detach_stateless_preview_design` | attach/detach syntax 미선정 | statelessness, atomicity, concurrency, reflection, state capture 및 witness coherence가 미결 |
| `dynamic_unsafe_quarantine_scope_msp` | `@scope#dynamic` / `@scope#unsafe`와 typed export probe | Recovery-only; provenance, authority, escape, suspension 및 backend equivalence가 열려 있음 |
| `facet_inout_pack_preview_design` | `facet[inout value as Trait]`, `Facet<inout any Trait>` | exclusive nonescaping place, alias/isolation 및 suspension law 필요 |
| `facet_owned_pack_preview_design` | `facet[move value as Trait]`, `Facet<move any Trait>` | exact owner 반환/소비, cleanup, transfer, ABI 및 actor crossing을 닫아야 함 |

### Registry 전체 분류 — static과 prototype

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `class_static_activation` | 과거 후보 `static class`; exact successor 미선정 | declaration identity, initialization, inheritance, authority 및 API residue가 열려 있어 현행 grammar에서 제거 |
| `effectful_static_activation` | exact surface/API 미선정 | compile-time과 runtime effect, failure, ordering, cache 및 authority를 분리해야 함 |
| `function_static_activation` | 과거 후보 `static def`; exact successor 미선정 | type-side `def::`와 충돌하지 않는 owner 및 initialization law 필요 |
| `module_static_entrance` | 후보 `static { ... }` | storage identity, multi-file order/cycle, failure 및 cleanup이 열려 있음 |
| `static_once_value` | once-initialized static value API 미선정 | publication, retry/failure, thread/actor isolation, drop 및 module lifecycle 필요 |
| `prototype_delta` | exact rooted syntax 미선정 | 현행 same-type `!{}`/`!!{}` derivation과 별개이며 ownership/rollback이 닫히지 않음 |
| `structural_prototype_extension` | exact syntax 미선정 | nominal conformance 방향과 충돌하며 shape가 owner/evidence를 만들 수 없음 |

### Registry 전체 분류 — Trait, conformance, extension 및 operator

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `conformance_law_proof_block_preview_design` | proof-language block surface 미선정 | proof calculus, termination, checker trust 및 diagnostic가 필요 |
| `custom_operator` | Recovery 후보 `operator <symbol> precedence N` | 임의 glyph/precedence/dispatch는 비활성; named Trait method/function/API 사용 |
| `extension_dot_call_sugar` | extension을 `value.member(...)`처럼 부르는 후보 | dot/member와 tilde/message domain을 합치지 않으며 ambiguity/coherence 필요 |
| `first_class_witness_value_not_current` | raw Witness value surface 미선정 | evidence는 checker-visible, non-forgeable이며 runtime 값/권위가 아님 |
| `fixed_operator_conformance_overloading` | 현행 glyph를 Trait witness에 연결하는 후보 | intrinsic-only dispatch 유지; TCC P1 7개와 deterministic no-fallback registry가 열려 있음 |
| `generic_named_extension_set_target` | generic target form 미선정 | Phase A는 exact nominal target뿐이며 normalization/overlap/API residue 필요 |
| `local_witness_preview_design` | local evidence surface 미선정 | scope-dependent program meaning, separate compilation 및 coherence 위험 |
| `negative_impl_preview_design` | general negative impl surface 미선정 | compiler-known closed-world fact 밖에서는 overlap/evolution을 안정적으로 증명할 수 없음 |
| `sealed_multimethod_family` | exact declaration/call surface 미선정 | finite dispatch universe, overlap, visibility, ordering 및 separate compilation 필요 |
| `specialization_preview_design` | specialization surface 미선정 | unique-maximal partial order, substitution stability, link determinism 및 diagnostics 필요 |

### Registry 전체 분류 — 타입, context, NumericArray 및 control

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `contextual_operation_anchor_dmad` | 일반화된 `&expr` context/provider anchor | NumericArray에 한정된 현행 `&` owner 밖으로 확장하지 않음 |
| `dependent_refinement_value_capture` | value-capturing refinement surface 미선정 | decidability, lifetime, substitution, public API 및 runtime dependency 금지 필요 |
| `explicit_broadcast_marker_msp` | 후보 `matrix + &row` | `&` polarity가 context anchor와 충돌하며 현행 source가 아님 |
| `explicit_context_argument_ampersand_spelling` | 후보 `&expr` argument | broadcast/context-anchor와 owner 충돌; parameter/call identity 미결 |
| `nullsafe_control` | exact surface 미선정 | Option/match/current control과 중복되지 않는 semantics, diagnostic 및 trace가 없음 |
| `solver_backed_general_refinement` | solver query/API와 source surface 미선정 | termination, resource budget, proof reproducibility, provider authority 및 ABI stability 필요 |
| `use_site_projection_dmad` | Java/Kotlin형 use-site projection 후보; exact Deeplus spelling 미선정 | Phase A role-named facade와 variance law를 우선하며 ABI/API residue 미결 |

### Registry 전체 분류 — 수용된 Enum successor 설계

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `enum_declaration_order_ord_preview_design` | 정확히 하나의 `enum#increasing` 또는 `enum#decreasing` | payload-free/nonempty/nongeneric whole-Enum `Ord` witness; glyph routing·raw·tag·layout·ABI와 분리 |
| `enum_case_display_mapping_preview_design` | case-owned `~>` restricted String template | inhabitable case 전체를 all-or-none으로 매핑하고 whole-Enum `Display` witness 하나만 생성 |
| `enum_exact_variant_subset_alias_preview_design` | enum body의 `+type Weekend = Sat \| Sun` | 같은 owner의 payload-free `VariantId` finite set; owner widening은 lossless, narrowing은 checked |

세 기능은 current `EnumDecl`, mixed payload, marker `.`, `+`, `*.`, `*+`,
lowercase `via`를 변경하지 않는다. order는 `SemanticOrderRank`, display는
표현 동작, subset은 resolution identity이며 raw/serialization/layout/ABI와
독립이다. payload ordering, payload-bearing exact variant, automatic reverse
parsing, subset range/iteration 및 bundled Trait derivation은 deferred다.

### Registry 전체 분류 — 수용된 collection successor 설계

| 기능 ID | 정확 후보 표면/API | 도입 판단과 현행 경계 |
|---|---|---|
| `literal_shaped_collection_type_surface_preview_design` | type goal의 `[T]`, `#mut[T]`, `#set{T}`, `#map{K:V}` | canonical `List`, `MutableList`, `Set`, `Map` identity로 normalize; value/pattern/index goal은 불변 |
| `literal_shaped_closed_record_type_surface_preview_design` | type goal의 `${label:T,...}` | closed required static-Identifier row만 후보; open/optional/rest/string label/empty row는 deferred |
| `immutable_first_collection_ownership_preview_design` | immutable-first owner naming과 distinct mutable owner | `Sequence`는 traversal-only; 현행 Prelude와 `FrozenList`/`ListSnapshot` identity 보존 |
| `freeze_snapshot_view_responsibility_preview_design` | no-argument receiver형 freeze/snapshot/view successor | freeze는 shallow·failure-atomic, snapshot은 독립 point-in-time, view는 owner-bounded·coordinate/provenance preserving |

이 후보 철자는 type-position 설계 예시이며 current parser route가 없다.
bracket, mutation, Trait witness, Copy, deep freeze, shareability, transfer 또는
actor crossing을 암시하지 않는다.

### 기계 검증 가능한 Preview Design 도입 검토 카드

다음 47개 카드는 feature registry의 `PREVIEW_DESIGN` 전체 집합과
일대일이다. 각 필드는 비어 있을 수 없으며, 구문이나 API가 아직
선택되지 않은 경우에도 그 사실과 현재 대안을 명시한다. 카드의 존재는
활성화가 아니라 도입 검토 가능성을 보장한다.

<!-- deeplus-preview-design-review-cards: begin -->
```json
[
  {
    "feature_id": "async_callable_literal_profile",
    "motivation": "중단 가능한 호출 가능 값을 이름 있는 선언 없이 안전하게 전달하려는 제안이다.",
    "surface_or_api": "후보는 #async{ => ... } 계열이며 exact EBNF와 반환 형식은 아직 미선정이다.",
    "static_semantics_and_interactions": "capture ownership, await 책임, Error/Defect/Cancellation, isolation과 structured task owner를 함께 검사해야 하며 ordinary lambda는 동기식으로 유지한다.",
    "diagnostics_migration_tooling": "현행은 비활성 feature 진단만 허용하고 자동 이행은 없으며 formatter/LSP가 profile과 capture 책임을 보존해야 한다.",
    "open_alternatives": "이름 있는 def#async가 현행 대안이고 implicit async lambda 및 ambient await 승격은 거부 대안이다.",
    "activation_prerequisites": "exact root와 EBNF, callable ABI, HIR/MIR lowering, cancellation corpus 및 xVM/LLVM target receipt가 필요하다."
  },
  {
    "feature_id": "async_comprehension",
    "motivation": "비동기 원천의 변환과 수집을 하나의 구조화된 표현으로 기술하려는 제안이다.",
    "surface_or_api": "exact source surface와 결과 collection 또는 stream API는 미선정이다.",
    "static_semantics_and_interactions": "finite-source 조건, 순서, backpressure, transform error-set union, cancellation과 부분 결과 cleanup을 닫아야 한다.",
    "diagnostics_migration_tooling": "for await를 자동 rewrite하지 않으며 recovery, formatter round-trip과 cancellation span 진단을 새로 정해야 한다.",
    "open_alternatives": "현행 for await statement와 stdlib AsyncCollector 조합이 대안이고 이를 comprehension으로 암묵 승격하는 방식은 거부한다.",
    "activation_prerequisites": "exact grammar, collector identity, ownership/effect 규칙, lowering 및 positive/negative/boundary 실행 증거가 필요하다."
  },
  {
    "feature_id": "automatic_observation_tracking",
    "motivation": "관측 의존성을 반복 수동 등록하지 않고도 반응형 갱신을 표현하려는 제안이다.",
    "surface_or_api": "자동 dependency observation의 source surface와 API는 미선정이다.",
    "static_semantics_and_interactions": "observation identity, mutation invalidation, lifetime, actor isolation과 hidden authority 금지를 보장해야 한다.",
    "diagnostics_migration_tooling": "암묵 추적 실패와 cycle의 결정적 진단, 명시적 registration에서의 opt-in 이행 및 tooling graph 표시가 필요하다.",
    "open_alternatives": "명시적 observer 등록이 현행 대안이며 전역 ambient dependency capture는 거부 대안이다.",
    "activation_prerequisites": "closed invalidation model, ownership proof, cycle policy, MIR event와 재현 가능한 동시성 receipt가 필요하다."
  },
  {
    "feature_id": "directed_coroutine_group",
    "motivation": "여러 coroutine의 방향과 수명을 하나의 구조화된 owner 아래 표현하려는 제안이다.",
    "surface_or_api": "group과 direction을 나타내는 exact source route 및 API는 미선정이다.",
    "static_semantics_and_interactions": "direction compatibility, structured scope, cancellation propagation, cleanup과 send/request interaction을 고정해야 한다.",
    "diagnostics_migration_tooling": "detached coroutine을 자동 포섭하지 않으며 direction mismatch와 escape span을 위한 진단 및 debugger 표기가 필요하다.",
    "open_alternatives": "현행 task group과 actor protocol이 대안이고 lexical owner 없는 coroutine 집합은 거부한다.",
    "activation_prerequisites": "exact grammar, owner typestate, cancellation/cleanup equations, MIR identity와 cross-backend corpus가 필요하다."
  },
  {
    "feature_id": "session_protocol_lite_provider",
    "motivation": "actor 메시지 순서에 경량 protocol-state 증거를 부여하려는 provider 제안이다.",
    "surface_or_api": "core syntax는 없으며 provider input/output 및 evidence API가 미선정이다.",
    "static_semantics_and_interactions": "protocol identity, duality, transition totality, linearity, actor handler conformance와 receiver closure를 닫아야 한다.",
    "diagnostics_migration_tooling": "기존 send/request를 자동 세션화하지 않으며 illegal transition 진단과 IDE state navigation이 필요하다.",
    "open_alternatives": "현행 actor protocol과 명시적 state machine provider가 대안이고 exactly-once delivery 암시는 거부한다.",
    "activation_prerequisites": "versioned evidence schema, cancellation terminal law, MIR correlation 및 target-bound actor receipt가 필요하다."
  },
  {
    "feature_id": "state_machine_source_syntax",
    "motivation": "상태와 전이를 직접 언어 표면에서 선언하려는 제안이다.",
    "surface_or_api": "과거 아이디어와 달리 exact current-compatible source syntax는 미선정이다.",
    "static_semantics_and_interactions": "state identity, transition totality, reentrancy, actor isolation, error/effect와 persistence 경계를 정해야 한다.",
    "diagnostics_migration_tooling": "현행 UML provider 출력을 새 syntax로 재해석하거나 자동 rewrite하지 않으며 formatter와 diagram round-trip 계약이 필요하다.",
    "open_alternatives": "ordinary Enum과 match 또는 uml_state_machine_provider가 현행 대안이고 provider evidence를 syntax authority로 쓰는 방식은 거부한다.",
    "activation_prerequisites": "Design_ syntax 선택, exact EBNF, checker algorithm, MIR transition event와 provider parity receipt가 필요하다."
  },
  {
    "feature_id": "weak_atomic_ordering",
    "motivation": "필요한 경우 순차 일관성보다 약한 ordering으로 동시성 비용을 제어하려는 제안이다.",
    "surface_or_api": "ordering spelling, operation별 API와 ordering lattice는 미선정이다.",
    "static_semantics_and_interactions": "data race, happens-before, failure ordering, compiler reorder 한계와 actor mailbox 순서를 분리해야 한다.",
    "diagnostics_migration_tooling": "현행 SharedCell/SharedMutex를 자동 약화하지 않으며 invalid ordering 진단과 tooling memory-order 표시가 필요하다.",
    "open_alternatives": "현행 sequentially consistent 최소 profile이 대안이고 target별 임의 의미는 거부한다.",
    "activation_prerequisites": "닫힌 memory model, xVM/LLVM parity, litmus suite와 target-bound reproducibility receipt가 필요하다."
  },
  {
    "feature_id": "c_aggregate",
    "motivation": "C 구조체와 공용체를 명시적 FFI profile로 교환하려는 제안이다.",
    "surface_or_api": "aggregate 선언, import 또는 mapping API의 exact surface는 미선정이다.",
    "static_semantics_and_interactions": "field order, padding, alignment, bitfield, ownership, provenance와 target ABI identity를 의미 identity와 분리해야 한다.",
    "diagnostics_migration_tooling": "Plain aggregate를 자동 C-safe로 승격하지 않으며 layout mismatch 진단과 header/tooling projection이 필요하다.",
    "open_alternatives": "현행 scalar 중심 최소 FFI와 명시적 byte buffer가 대안이고 추정 layout은 거부한다.",
    "activation_prerequisites": "target ABI authority, representability schema, bindgen parity와 다중 target 실행 receipt가 필요하다."
  },
  {
    "feature_id": "c_stored_callback",
    "motivation": "C가 호출 시점 이후에도 보관하는 callback을 안전하게 표현하려는 제안이다.",
    "surface_or_api": "stored callback registration, revoke 및 context API는 미선정이다.",
    "static_semantics_and_interactions": "capture lifetime, thread/actor isolation, reentrancy, panic/unwind, cleanup owner와 exactly-once revoke를 닫아야 한다.",
    "diagnostics_migration_tooling": "ordinary closure를 자동 장수 callback으로 변환하지 않으며 escape 진단과 lifetime tooling이 필요하다.",
    "open_alternatives": "동기 FFI callback 또는 명시적 opaque handle이 대안이고 숨은 global registry는 거부한다.",
    "activation_prerequisites": "owner token API, unwind policy, race corpus, MIR callback identity와 native target receipt가 필요하다."
  },
  {
    "feature_id": "c_variadic",
    "motivation": "기존 C variadic API를 제한된 FFI profile에서 호출하려는 제안이다.",
    "surface_or_api": "variadic parameter와 call-site spelling 및 sentinel/count API는 미선정이다.",
    "static_semantics_and_interactions": "default promotion, representability, arity/sentinel contract, ownership과 ABI별 lowering을 고정해야 한다.",
    "diagnostics_migration_tooling": "ordinary Deeplus rest parameter를 C variadic으로 간주하지 않으며 promotion 진단과 signature help가 필요하다.",
    "open_alternatives": "typed wrapper 함수가 현행 대안이고 무검사 vararg 전달은 거부한다.",
    "activation_prerequisites": "지원 타입 폐쇄 집합, target ABI matrix, negative corpus와 native execution receipt가 필요하다."
  },
  {
    "feature_id": "dyn_inspection",
    "motivation": "open-world 경계에서 runtime 값을 제한적으로 조사하려는 제안이다.",
    "surface_or_api": "privileged inspection service 또는 checked API의 exact 형태는 미선정이다.",
    "static_semantics_and_interactions": "inspection은 static type, label, conformance, witness 또는 authority를 제조하지 않고 ownership/effect를 보존해야 한다.",
    "diagnostics_migration_tooling": "reflection fallback을 자동 삽입하지 않으며 capability denial과 failed inspection 진단, debugger 격리가 필요하다.",
    "open_alternatives": "closed Union, Enum, match와 명시적 schema가 현행 대안이고 ambient reflection은 거부한다.",
    "activation_prerequisites": "권한 모델, closed result carrier, MIR event, data-leak review와 target-bound receipt가 필요하다."
  },
  {
    "feature_id": "dyn_rcts_family",
    "motivation": "닫힌 정적 RCTS descriptor를 명시적 runtime checked carrier로 확장하려는 제안이다.",
    "surface_or_api": "owned Dyn carrier와 check/cast API 및 exact source syntax는 미선정이다.",
    "static_semantics_and_interactions": "type erasure, owner/drop plan, cast failure, authority non-forging과 Trait evidence coherence를 닫아야 한다.",
    "diagnostics_migration_tooling": "ordinary value를 자동 box하지 않으며 failed cast의 typed 진단과 erased-type tooling 표시가 필요하다.",
    "open_alternatives": "closed Union과 explicit nominal wrapper가 현행 대안이고 ambient dynamic fallback은 거부한다.",
    "activation_prerequisites": "runtime representation, checker/MIR lowering, SFD-P1-009 실행 권위와 xVM/LLVM receipt가 필요하다."
  },
  {
    "feature_id": "dynamic_trait_attach_detach_stateless_preview_design",
    "motivation": "상태 없는 동작 묶음을 runtime 경계에서 명시적으로 부착하거나 해제하려는 제안이다.",
    "surface_or_api": "attach/detach syntax, handle 및 query API는 미선정이다.",
    "static_semantics_and_interactions": "statelessness, atomicity, concurrency, reflection, capture 금지와 static Trait witness coherence를 보장해야 한다.",
    "diagnostics_migration_tooling": "static conformance를 자동 dynamic attachment로 바꾸지 않으며 race/conflict 진단과 inspector 표시가 필요하다.",
    "open_alternatives": "명시적 strategy object와 static conformance가 대안이고 stateful monkey patching은 거부한다.",
    "activation_prerequisites": "closed registry protocol, owner/epoch model, deterministic dispatch와 concurrent target receipt가 필요하다."
  },
  {
    "feature_id": "dynamic_unsafe_quarantine_scope_msp",
    "motivation": "불가피한 legacy, dynamic 또는 unsafe 작업의 권위와 escape를 한 lexical owner에 가두려는 제안이다.",
    "surface_or_api": "Recovery probe는 @scope#dynamic 또는 @scope#unsafe와 typed export를 인식하지만 activatable route는 없다.",
    "static_semantics_and_interactions": "outer mutation, suspension, pointer, authority, borrow, resource, closure, task와 actor escape를 금지해야 한다.",
    "diagnostics_migration_tooling": "현행은 QUARANTINE_SCOPE_NOT_ACTIVATABLE만 내고 자동 이행은 없으며 formatter는 offending spelling을 보존한다.",
    "open_alternatives": "typed wrapper와 explicit FFI boundary가 현행 대안이고 untyped result escape 및 ambient unsafe는 거부한다.",
    "activation_prerequisites": "provenance/authority accounting, escape proof, exact MIR, backend differential execution과 별도 Design_ 승인이 필요하다."
  },
  {
    "feature_id": "facet_inout_pack_preview_design",
    "motivation": "은닉된 concrete payload에 receiver-bound exclusive mutable view를 제공하려는 제안이다.",
    "surface_or_api": "후보는 facet[inout value as Trait]와 Facet<inout any Trait>이며 현행에는 Recovery probe만 있다.",
    "static_semantics_and_interactions": "unique place, alias exclusion, nonescape, suspension 금지, isolation과 witness coherence를 보장해야 한다.",
    "diagnostics_migration_tooling": "borrow Facet을 자동 inout으로 승격하지 않으며 alias/escape 진단과 lifetime-aware IDE 표시가 필요하다.",
    "open_alternatives": "현행 borrow Facet과 명시적 inout parameter가 대안이고 shared mutable existential은 거부한다.",
    "activation_prerequisites": "region algorithm, HIR/MIR place identity, cleanup law, formatter 및 target-bound negative corpus가 필요하다."
  },
  {
    "feature_id": "facet_owned_pack_preview_design",
    "motivation": "은닉된 concrete payload와 정확한 drop plan을 함께 이동하는 owned existential을 제공하려는 제안이다.",
    "surface_or_api": "후보는 facet[move value as Trait]와 Facet<move any Trait>이며 activatable grammar는 없다.",
    "static_semantics_and_interactions": "exact owner 소비/반환, allocation/drop plan, cast failure, transfer, ABI와 actor crossing을 닫아야 한다.",
    "diagnostics_migration_tooling": "borrow Facet을 자동 owned로 바꾸지 않으며 use-after-move 진단과 owner trace tooling이 필요하다.",
    "open_alternatives": "명시적 nominal Box와 borrow Facet이 대안이고 owner를 잃는 type erasure는 거부한다.",
    "activation_prerequisites": "existential layout, move/drop MIR, TCC evidence closure, SFD-P1-009 receipt와 별도 activation이 필요하다."
  },
  {
    "feature_id": "class_static_activation",
    "motivation": "Class owner 수준의 초기화와 공유 상태를 명시하려는 과거 제안이다.",
    "surface_or_api": "과거 static class 철자는 제거되었고 exact successor surface는 미선정이다.",
    "static_semantics_and_interactions": "declaration identity, initialization order, inheritance, visibility, authority와 API residue를 닫아야 한다.",
    "diagnostics_migration_tooling": "제거된 철자를 자동 복원하지 않으며 current type-side API로의 수동 이행 안내만 허용한다.",
    "open_alternatives": "module-level binding과 type-side def::가 현행 대안이고 hidden eager initialization은 거부한다.",
    "activation_prerequisites": "새 Design_ 선택, exact grammar, cycle/failure law, linker identity와 multi-module execution receipt가 필요하다."
  },
  {
    "feature_id": "effectful_static_activation",
    "motivation": "정적 초기화가 필요한 effectful 작업의 순서와 실패를 명시하려는 제안이다.",
    "surface_or_api": "source surface, callable profile와 cache API는 미선정이다.",
    "static_semantics_and_interactions": "compile-time과 runtime effect, failure, ordering, retry, cache, authority와 cleanup을 분리해야 한다.",
    "diagnostics_migration_tooling": "ordinary static value에 effect를 추론해 넣지 않으며 cycle/failure 진단과 build graph 표시가 필요하다.",
    "open_alternatives": "명시적 entry initialization 함수가 현행 대안이고 build-time 실행과 runtime 실행의 혼합은 거부한다.",
    "activation_prerequisites": "closed phase model, reproducibility/supply-chain review, MIR semantics와 clean-build receipts가 필요하다."
  },
  {
    "feature_id": "function_static_activation",
    "motivation": "함수 owner에 결합된 정적 초기화 또는 정적 callable을 표현하려는 과거 제안이다.",
    "surface_or_api": "과거 static def는 제거되었고 def::와 충돌하지 않는 successor는 미선정이다.",
    "static_semantics_and_interactions": "function identity, initialization, capture 금지, visibility, generic instantiation과 type-side dispatch를 분리해야 한다.",
    "diagnostics_migration_tooling": "static def를 자동 def::로 바꾸지 않으며 owner-sensitive migration 진단이 필요하다.",
    "open_alternatives": "ordinary def, module binding과 type-side def::가 대안이고 모호한 dual owner는 거부한다.",
    "activation_prerequisites": "owner 선택, exact EBNF, API digest, initialization cycle algorithm과 linker receipt가 필요하다."
  },
  {
    "feature_id": "module_static_entrance",
    "motivation": "모듈 적재 시 한 번 수행되는 명시적 초기화 영역을 표현하려는 제안이다.",
    "surface_or_api": "후보 static { ... }가 있으나 current source route와 exact contract는 미선정이다.",
    "static_semantics_and_interactions": "storage identity, multi-file order, cycles, failure, retry, effects, cleanup과 import visibility를 닫아야 한다.",
    "diagnostics_migration_tooling": "top-level statement를 자동 이동하지 않으며 cycle/order 진단과 module graph tooling이 필요하다.",
    "open_alternatives": "명시적 entry 또는 init 함수 호출이 대안이고 import 시 숨은 effect는 거부한다.",
    "activation_prerequisites": "module lifecycle authority, deterministic ordering, MIR init event와 clean-link execution receipt가 필요하다."
  },
  {
    "feature_id": "static_once_value",
    "motivation": "한 번만 초기화되는 공유 값을 명시적 책임과 함께 제공하려는 제안이다.",
    "surface_or_api": "once value declaration과 get/init API는 미선정이다.",
    "static_semantics_and_interactions": "publication, retry/failure, thread/actor isolation, drop, module lifecycle와 memory ordering을 닫아야 한다.",
    "diagnostics_migration_tooling": "ordinary let을 자동 once로 바꾸지 않으며 reentrancy/cycle 진단과 state tooling이 필요하다.",
    "open_alternatives": "SharedCell/SharedMutex 또는 명시적 owner object가 대안이고 poison 상태의 암묵 처리는 거부한다.",
    "activation_prerequisites": "closed state machine, happens-before law, cleanup receipt와 cross-backend concurrency tests가 필요하다."
  },
  {
    "feature_id": "prototype_delta",
    "motivation": "기존 값에서 다른 명목 또는 prototype shape로의 명시적 delta 구성을 표현하려는 제안이다.",
    "surface_or_api": "rooted prototype delta syntax는 미선정이며 현행 !{}/!!{} same-type derivation과 별개다.",
    "static_semantics_and_interactions": "target identity, field evaluation, ownership, validation, rollback과 construction authority를 닫아야 한다.",
    "diagnostics_migration_tooling": "현행 derivation을 prototype delta로 확대하지 않으며 target/owner mismatch 진단과 refactoring guard가 필요하다.",
    "open_alternatives": "명시적 named constructor와 same-type derivation이 대안이고 structural owner inference는 거부한다.",
    "activation_prerequisites": "exact rooted syntax, formation plan, cleanup equations, API residue와 execution corpus가 필요하다."
  },
  {
    "feature_id": "structural_prototype_extension",
    "motivation": "명목 선언 수정 없이 shape 기반 동작 확장을 표현하려는 제안이다.",
    "surface_or_api": "structural extension의 target 및 activation syntax는 미선정이다.",
    "static_semantics_and_interactions": "shape matching은 nominal conformance, witness, owner identity와 API stability를 제조하지 않아야 한다.",
    "diagnostics_migration_tooling": "duck-typing fallback을 자동 삽입하지 않으며 overlap/shape drift 진단과 navigation 경계가 필요하다.",
    "open_alternatives": "named extension set과 explicit Trait conformance가 대안이고 ambient structural dispatch는 거부한다.",
    "activation_prerequisites": "closed applicability algorithm, coherence/termination proof, API digest 및 link-order mutation receipt가 필요하다."
  },
  {
    "feature_id": "conformance_law_proof_block_preview_design",
    "motivation": "Trait conformance가 만족하는 법칙과 기계 증거를 source 가까이 명시하려는 제안이다.",
    "surface_or_api": "proof-language block의 syntax, calculus와 artifact API는 미선정이다.",
    "static_semantics_and_interactions": "proof termination, trusted base, generic substitution, witness identity와 runtime code 분리를 보장해야 한다.",
    "diagnostics_migration_tooling": "주석이나 test를 proof로 자동 승격하지 않으며 proof failure 진단과 IDE goal display가 필요하다.",
    "open_alternatives": "외부 proof artifact와 conformance test가 대안이고 unchecked assume block은 거부한다.",
    "activation_prerequisites": "formal calculus ratification, deterministic checker, artifact provenance와 independent proof corpus가 필요하다."
  },
  {
    "feature_id": "custom_operator",
    "motivation": "도메인별 표기 편의성을 위해 새 glyph와 precedence를 선언하려는 과거 제안이다.",
    "surface_or_api": "Recovery는 operator <symbol> precedence N을 진단하지만 activatable declaration surface는 없다.",
    "static_semantics_and_interactions": "glyph vocabulary, precedence, associativity, overload resolution, Trait evidence와 formatter ownership을 닫아야 한다.",
    "diagnostics_migration_tooling": "현행은 CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT를 내고 named API로 수동 이행하며 blind rewrite는 금지한다.",
    "open_alternatives": "named function, method와 닫힌 intrinsic operator가 대안이고 module-local precedence 변경은 거부한다.",
    "activation_prerequisites": "새 glyph authority, exact parser table, deterministic resolution, formatting 및 ambiguity corpus가 필요하다."
  },
  {
    "feature_id": "extension_dot_call_sugar",
    "motivation": "활성화된 extension 함수를 ordinary member처럼 간결하게 호출하려는 제안이다.",
    "surface_or_api": "value.member(...) 후보가 있으나 selector와 activation 경계의 exact surface는 미선정이다.",
    "static_semantics_and_interactions": "dot/member, extension, tilde pipeline과 actor message domain을 합치지 않고 ambiguity/coherence를 닫아야 한다.",
    "diagnostics_migration_tooling": "tilde 또는 explicit selector를 자동 dot으로 바꾸지 않으며 후보 출처 진단과 completion 구분이 필요하다.",
    "open_alternatives": "현행 value ~ extension::name(...)와 명시적 selector가 대안이고 ordinary member fallback은 거부한다.",
    "activation_prerequisites": "ranked resolution, no-fallback law, import/link invariance, formatter와 mutation corpus가 필요하다."
  },
  {
    "feature_id": "first_class_witness_value_not_current",
    "motivation": "Trait evidence를 인수로 저장하거나 전달하는 명시적 값을 제공하려는 제안이다.",
    "surface_or_api": "raw Witness value type, constructor와 projection API는 미선정이다.",
    "static_semantics_and_interactions": "evidence는 non-forgeable이어야 하고 checker-visible identity, lifetime, ownership과 runtime representation을 분리해야 한다.",
    "diagnostics_migration_tooling": "using parameter를 raw value로 자동 노출하지 않으며 forged/stale witness 진단과 identity navigation이 필요하다.",
    "open_alternatives": "현행 using witness parameter와 static conformance가 대안이고 reflection으로 witness 생성은 거부한다.",
    "activation_prerequisites": "canonical witness ABI, construction authority, HIR/MIR metadata, separate compilation과 target receipt가 필요하다."
  },
  {
    "feature_id": "fixed_operator_conformance_overloading",
    "motivation": "현행 닫힌 glyph의 의미를 Trait conformance로 확장하면서 결정성을 유지하려는 제안이다.",
    "surface_or_api": "기존 glyph를 canonical Trait witness에 연결하는 후보이며 exact source route는 미선정이다.",
    "static_semantics_and_interactions": "intrinsic-only current를 유지하고 unique ground witness, no specialization, no priority, no fallback과 operator domain 분리를 요구한다.",
    "diagnostics_migration_tooling": "final registry code는 미선정이고 current intrinsic call을 rewrite하지 않으며 TCC rank와 formatter provenance가 필요하다.",
    "open_alternatives": "named Trait method와 intrinsic operator가 대안이고 AUTO/VIA, case-local witness 및 order winner는 거부한다.",
    "activation_prerequisites": "TCC-P1-002..008, deterministic registry, closed MIR dispatch, permutation corpus와 Design_ activation이 필요하다."
  },
  {
    "feature_id": "generic_named_extension_set_target",
    "motivation": "generic nominal family에 재사용 가능한 named extension set을 적용하려는 제안이다.",
    "surface_or_api": "generic target parameterization과 where-clause surface는 미선정이다.",
    "static_semantics_and_interactions": "exact target normalization, substitution, overlap, locality, coherence와 public API residue를 닫아야 한다.",
    "diagnostics_migration_tooling": "현행 exact nominal extension을 자동 일반화하지 않으며 overlap/ambiguous target 진단과 IDE specialization 표시가 필요하다.",
    "open_alternatives": "각 exact nominal target의 named extension이 대안이고 structural target 및 hidden specialization은 거부한다.",
    "activation_prerequisites": "generic applicability algorithm, termination proof, link-order tests, metadata와 formatter corpus가 필요하다."
  },
  {
    "feature_id": "local_witness_preview_design",
    "motivation": "좁은 lexical 범위에서만 다른 Trait evidence를 선택하려는 제안이다.",
    "surface_or_api": "local evidence declaration, import와 call-site selection syntax는 미선정이다.",
    "static_semantics_and_interactions": "scope-dependent meaning, separate compilation, capture, escape, overlap과 global coherence 위험을 닫아야 한다.",
    "diagnostics_migration_tooling": "current global conformance를 자동 shadow하지 않으며 ambiguity/escape 진단과 scope-aware navigation이 필요하다.",
    "open_alternatives": "명시적 strategy 값이나 using witness parameter가 대안이고 ambient local override는 거부한다.",
    "activation_prerequisites": "lexical identity model, API digest rules, coherence theorem, HIR/MIR transport와 link permutation receipt가 필요하다."
  },
  {
    "feature_id": "negative_impl_preview_design",
    "motivation": "특정 타입과 Trait 조합이 성립하지 않음을 명시해 overlap과 API 의도를 고정하려는 제안이다.",
    "surface_or_api": "general negative impl 또는 conformance surface는 미선정이다.",
    "static_semantics_and_interactions": "closed-world compiler fact, evolution, generic overlap, downstream ownership과 coherence를 구별해야 한다.",
    "diagnostics_migration_tooling": "absence를 자동 negative evidence로 만들지 않으며 contradiction/evolution 진단과 API diff tooling이 필요하다.",
    "open_alternatives": "sealed compiler-known exclusions와 positive bound 설계가 대안이고 open-world negation은 거부한다.",
    "activation_prerequisites": "orphan/locality policy, versioning law, overlap solver, package evolution corpus와 Design_ ratification이 필요하다."
  },
  {
    "feature_id": "sealed_multimethod_family",
    "motivation": "닫힌 인수 타입 조합에 대해 대칭적 다중 dispatch를 결정적으로 표현하려는 제안이다.",
    "surface_or_api": "declaration, case family와 call syntax는 미선정이다.",
    "static_semantics_and_interactions": "finite dispatch universe, overlap, visibility, ordering, exhaustiveness와 separate compilation을 닫아야 한다.",
    "diagnostics_migration_tooling": "ordinary overload를 자동 multimethod로 바꾸지 않으며 ambiguous/missing cell 진단과 matrix tooling이 필요하다.",
    "open_alternatives": "double dispatch, visitor 또는 match가 대안이고 open-world order winner는 거부한다.",
    "activation_prerequisites": "sealed universe identity, total resolution algorithm, API evolution lanes, MIR dispatch와 permutation receipt가 필요하다."
  },
  {
    "feature_id": "specialization_preview_design",
    "motivation": "generic 기본 구현보다 더 구체적인 구현을 선택해 성능과 표현력을 높이려는 제안이다.",
    "surface_or_api": "specialization declaration, relation과 visibility surface는 미선정이다.",
    "static_semantics_and_interactions": "unique-maximal partial order, substitution stability, termination, coherence와 link determinism을 보장해야 한다.",
    "diagnostics_migration_tooling": "현행 conformance에 priority를 추론하지 않으며 incomparable/unstable 진단과 selected-origin tooling이 필요하다.",
    "open_alternatives": "명시적 named API와 exact conformance가 대안이고 declaration order 또는 numeric priority winner는 거부한다.",
    "activation_prerequisites": "formal ordering calculus, overlap proof, cross-package mutation corpus, closed metadata와 target receipt가 필요하다."
  },
  {
    "feature_id": "contextual_operation_anchor_dmad",
    "motivation": "연산에 필요한 외부 context나 provider를 명시적으로 고정하려는 제안이다.",
    "surface_or_api": "일반화된 &expr anchor 후보가 있으나 owner와 parameter/call API는 미선정이다.",
    "static_semantics_and_interactions": "NumericArray의 현행 & polarity, borrow, address-like 해석과 provider authority를 충돌 없이 분리해야 한다.",
    "diagnostics_migration_tooling": "기존 &를 자동 재해석하지 않으며 owner-sensitive 진단과 formatter spacing 보존이 필요하다.",
    "open_alternatives": "context keyword argument와 명시적 provider value가 대안이고 token 모양만으로 owner를 고르는 방식은 거부한다.",
    "activation_prerequisites": "token owner 결정, exact grammar, type/effect contract, ambiguity corpus와 API digest가 필요하다."
  },
  {
    "feature_id": "dependent_refinement_value_capture",
    "motivation": "타입 refinement가 주변 값에 의존하는 관계를 정적으로 표현하려는 제안이다.",
    "surface_or_api": "value-capturing predicate syntax와 public API representation은 미선정이다.",
    "static_semantics_and_interactions": "decidability, lifetime, substitution, mutation kill, module boundary와 runtime dependency 금지를 닫아야 한다.",
    "diagnostics_migration_tooling": "현행 finite R0를 자동 확대하지 않으며 escaped capture와 undecidable predicate 진단, hover proof 표시가 필요하다.",
    "open_alternatives": "명시적 runtime check와 closed R0 refinement가 대안이고 hidden runtime validation은 거부한다.",
    "activation_prerequisites": "제한 calculus, termination metric, proof certificate, API serialization과 checker receipt가 필요하다."
  },
  {
    "feature_id": "explicit_broadcast_marker_msp",
    "motivation": "NumericArray broadcast 의도를 호출 지점에서 명시해 shape 오류를 줄이려는 제안이다.",
    "surface_or_api": "후보는 matrix + &row이나 &의 정확한 polarity와 owner는 미선정이다.",
    "static_semantics_and_interactions": "shape proof, axis alignment, one-based coordinate, context anchor와 borrow 의미를 분리해야 한다.",
    "diagnostics_migration_tooling": "implicit broadcast를 자동 표기하지 않으며 axis/shape 진단과 formatter token ownership이 필요하다.",
    "open_alternatives": "명시적 broadcast API와 현행 same-shape 연산이 대안이고 NumPy형 ambient broadcast는 거부한다.",
    "activation_prerequisites": "exact parse owner, shape algorithm, diagnostic spans, NumericArray corpus와 backend parity가 필요하다."
  },
  {
    "feature_id": "explicit_context_argument_ampersand_spelling",
    "motivation": "호출에서 context argument를 짧고 명시적으로 공급하려는 철자 제안이다.",
    "surface_or_api": "후보 &expr argument가 있으나 parameter와 call identity는 미선정이다.",
    "static_semantics_and_interactions": "broadcast marker, context anchor, borrow와 address-like owner를 분리하고 evaluation order를 보존해야 한다.",
    "diagnostics_migration_tooling": "현행 context keyword spelling을 자동 교체하지 않으며 owner ambiguity 진단과 signature help가 필요하다.",
    "open_alternatives": "현행 context expr spelling과 named parameter가 대안이고 동일 token의 추측 기반 dispatch는 거부한다.",
    "activation_prerequisites": "token owner ratification, exact grammar, call-shape/API digest, formatter와 mutation tests가 필요하다."
  },
  {
    "feature_id": "nullsafe_control",
    "motivation": "Option 값을 간결하게 분기하거나 연쇄 처리하는 제어 표면을 제공하려는 제안이다.",
    "surface_or_api": "nullsafe operator 또는 control syntax는 미선정이며 null literal도 current가 아니다.",
    "static_semantics_and_interactions": "Option identity, evaluation count, short-circuit, ownership, effects, pattern matching과 narrowing을 보존해야 한다.",
    "diagnostics_migration_tooling": "null 또는 기존 match를 자동 rewrite하지 않으며 Option-required 진단과 desugaring 표시가 필요하다.",
    "open_alternatives": "match, if let과 Option combinator가 현행 대안이고 nullable ambient type은 거부한다.",
    "activation_prerequisites": "동기와 유스케이스 승인, exact syntax, lowering, diagnostics/migration policy와 execution corpus가 필요하다."
  },
  {
    "feature_id": "solver_backed_general_refinement",
    "motivation": "finite R0보다 풍부한 수학적 predicate를 정적 증명에 사용하려는 제안이다.",
    "surface_or_api": "solver query, proof annotation과 source predicate calculus는 미선정이다.",
    "static_semantics_and_interactions": "termination, resource budget, proof reproducibility, mutation invalidation, provider authority와 ABI stability를 보장해야 한다.",
    "diagnostics_migration_tooling": "R0 실패를 solver로 자동 fallback하지 않으며 timeout/unknown의 결정적 진단과 proof trace tooling이 필요하다.",
    "open_alternatives": "finite R0와 명시적 runtime validation이 대안이고 환경 의존 solver guess는 거부한다.",
    "activation_prerequisites": "제한 논리, 버전 고정 solver/proof certificate, deterministic resource cap과 independent checker receipt가 필요하다."
  },
  {
    "feature_id": "use_site_projection_dmad",
    "motivation": "generic 사용 지점에서 읽기/쓰기 방향을 제한해 API 적합성을 표현하려는 제안이다.",
    "surface_or_api": "Java/Kotlin형 projection 개념만 있으며 exact Deeplus spelling은 미선정이다.",
    "static_semantics_and_interactions": "Phase A role-named facade, Trait-only variance, capture conversion, ownership과 API digest를 일관되게 해야 한다.",
    "diagnostics_migration_tooling": "기존 generic 인수를 자동 projection으로 바꾸지 않으며 variance/capture 진단과 signature display가 필요하다.",
    "open_alternatives": "명시적 facade Trait와 invariant generic이 대안이고 wildcard 기반 hidden capture는 거부한다.",
    "activation_prerequisites": "normative variance calculus, exact syntax, substitution/capture algorithm, ABI/API tests와 migration plan이 필요하다."
  },
  {
    "feature_id": "enum_declaration_order_ord_preview_design",
    "motivation": "선언 순서를 명시적으로 선택한 Enum에서만 안전한 전체 순서를 파생하려는 제안이다.",
    "surface_or_api": "정확히 하나의 enum#increasing 또는 enum#decreasing modifier가 후보다.",
    "static_semantics_and_interactions": "payload-free, nonempty, nongeneric whole-Enum에 SemanticOrderRank와 Ord witness 하나를 만들며 raw/tag/layout/ABI와 분리한다.",
    "diagnostics_migration_tooling": "final registry code는 미선정이고 기존 Enum을 자동 modifier화하지 않으며 declaration-order 변화 진단과 formatter 보존이 필요하다.",
    "open_alternatives": "명시적 compare 함수가 현행 대안이고 payload ordering, case-local witness와 raw ordinal 재사용은 거부한다.",
    "activation_prerequisites": "TCC/CE P1 closure, witness conflict 규칙, link summary, diagnostics와 permutation 실행 receipt가 필요하다."
  },
  {
    "feature_id": "enum_case_display_mapping_preview_design",
    "motivation": "Enum case의 사용자 표시를 owner 가까이에 전체적으로 정의하려는 제안이다.",
    "surface_or_api": "case-owned ~> restricted String template가 후보다.",
    "static_semantics_and_interactions": "inhabitable case 전체의 all-or-none mapping과 whole-Enum Display witness 하나를 요구하며 parsing/serialization과 분리한다.",
    "diagnostics_migration_tooling": "partial mapping fallback과 자동 reverse parser를 만들지 않으며 missing/impure template 진단 및 formatter round-trip이 필요하다.",
    "open_alternatives": "명시적 display match 함수가 현행 대안이고 partial default, runtime effect와 case-local witness는 거부한다.",
    "activation_prerequisites": "restricted template grammar, purity checker, TCC/CE evidence, diagnostic binding과 target corpus가 필요하다."
  },
  {
    "feature_id": "enum_exact_variant_subset_alias_preview_design",
    "motivation": "같은 Enum의 정확한 case 부분집합을 타입 안전한 alias로 표현하려는 제안이다.",
    "surface_or_api": "enum body의 +type Weekend = Sat | Sun 형태가 후보다.",
    "static_semantics_and_interactions": "payload-free same-owner VariantId finite set이며 owner widening은 lossless, narrowing은 checked이고 range/iteration과 분리한다.",
    "diagnostics_migration_tooling": "case 목록을 자동 subset으로 만들지 않으며 foreign/payload variant 진단과 rename/navigation 보존이 필요하다.",
    "open_alternatives": "closed Union 또는 explicit predicate가 현행 대안이고 cross-owner subset과 implicit narrowing은 거부한다.",
    "activation_prerequisites": "frozen VariantId universe, exact grammar, narrowing API, exhaustiveness integration과 CE/TCC receipt가 필요하다."
  },
  {
    "feature_id": "literal_shaped_collection_type_surface_preview_design",
    "motivation": "값 literal과 닮은 간결한 컬렉션 타입 표기로 읽기 비용을 줄이려는 제안이다.",
    "surface_or_api": "type goal의 [T], #mut[T], #set{T}, #map{K:V}가 후보다.",
    "static_semantics_and_interactions": "각 표면은 canonical List, MutableList, Set, Map identity로만 normalize하며 value/pattern/index goal과 one-based indexing은 불변이다.",
    "diagnostics_migration_tooling": "기존 canonical type을 자동 rewrite하지 않으며 goal ambiguity 진단, formatter round-trip과 LSP canonical hover가 필요하다.",
    "open_alternatives": "현행 canonical generic spelling이 대안이고 syntax identity를 새 nominal identity로 만드는 방식은 거부한다.",
    "activation_prerequisites": "goal-separated parser, exact recovery, canonicalization proof, Prelude/API compatibility와 target parser receipt가 필요하다."
  },
  {
    "feature_id": "literal_shaped_closed_record_type_surface_preview_design",
    "motivation": "작은 닫힌 label row 타입을 값 materialization과 닮은 표기로 기술하려는 제안이다.",
    "surface_or_api": "type goal의 ${label:T,...}가 후보이며 closed required static-Identifier row만 포함한다.",
    "static_semantics_and_interactions": "label order 정규화, exact row identity, Record materialization, Union과 API serialization을 보존해야 한다.",
    "diagnostics_migration_tooling": "open/optional/rest/string label과 empty row는 진단하며 canonical Record schema 자동 rewrite는 별도 선택 없이 하지 않는다.",
    "open_alternatives": "현행 named Record/schema type이 대안이고 structural row를 nominal schema로 추정하는 방식은 거부한다.",
    "activation_prerequisites": "exact grammar/recovery, label uniqueness, canonical row schema, formatter/LSP와 compatibility corpus가 필요하다."
  },
  {
    "feature_id": "immutable_first_collection_ownership_preview_design",
    "motivation": "기본 collection을 불변 owner로 두고 mutation과 snapshot 책임을 명시하려는 설계다.",
    "surface_or_api": "immutable-first owner naming과 distinct mutable owner 책임 모델이며 exact migration surface는 미선정이다.",
    "static_semantics_and_interactions": "Sequence는 traversal-only이고 List/MutableList, FrozenList/ListSnapshot identity, Copy, shareability와 actor transfer를 분리한다.",
    "diagnostics_migration_tooling": "현행 Prelude identity를 자동 합치거나 rename하지 않으며 mutation/ownership 진단과 API migration report가 필요하다.",
    "open_alternatives": "현행 명시적 immutable/mutable carriers가 대안이고 mutable default 및 shallow 이름 alias는 거부한다.",
    "activation_prerequisites": "Prelude migration 선택, ownership/borrow law, ABI/serialization review, formatter와 actor/backend receipts가 필요하다."
  },
  {
    "feature_id": "freeze_snapshot_view_responsibility_preview_design",
    "motivation": "freeze, snapshot과 view가 서로 다른 책임과 비용을 갖도록 API 의미를 고정하려는 설계다.",
    "surface_or_api": "no-argument receiver형 freeze(), snapshot(), view() successor API가 후보이며 carrier 이름 일부는 미선정이다.",
    "static_semantics_and_interactions": "freeze는 shallow·failure-atomic, snapshot은 독립 point-in-time, view는 owner-bounded nonowning projection으로 coordinate와 provenance를 보존한다.",
    "diagnostics_migration_tooling": "기존 FrozenList/ListSnapshot을 자동 List로 합치지 않으며 escape/mutation 진단과 API diff/migration report가 필요하다.",
    "open_alternatives": "현행 명시적 carrier API가 대안이고 deep freeze 암시, owner escape와 actor shareability 자동 부여는 거부한다.",
    "activation_prerequisites": "exact API signatures, ownership/MIR events, failure cleanup, serialization/indexing review와 target-bound execution receipt가 필요하다."
  }
]
```
<!-- deeplus-preview-design-review-cards: end -->

### Controlling decision 및 frontend 결합

| 권위 행 | 보존되는 설계 | 활성화 fence |
|---|---|---|
| `DSGN-CURRENT-LITERAL-SHAPED-COLLECTION-DESIGN-PREVIEW` | literal-shaped type와 immutable-first/freeze-snapshot-view 책임 | nonactivatable, current indexing/Prelude 불변 |
| `DSGN-CURRENT-ENUM-DERIVED-CAPABILITIES-PREVIEW` | order, display, exact subset | nonactivatable, current Enum 불변 |
| `DSGN-QUARANTINE` | dynamic/unsafe quarantine minimum profile | Recovery probe만 존재 |
| `DSGN-POST-PR16-TRAIT-BASE` | `TC-R001..R016` | successor only, current conformance/`via` 불변 |
| `DSGN-POST-PR16-TRAIT-GUARDS` | `TCC-DG-001..008`, `TCC-DG-P2-009/A/B` | VIA/AUTO, specialization, child-local witness 비활성 |
| `DSGN-POST-PR16-CE-G6` | Class `C-01..C-11`, Enum `E-01..E-13`, `X-01..X-10`, `PC-09/10` | current Class/Enum authority 불변 |
| `DSGN-POST-PR16-SFD` | static-first Dyn/Facet successor | borrow Facet current, dynamic carrier 비활성 |
| `DSGN-POST-PR16-U07-EXCLUSION` | E-02/E-06 migration 선택 보류 | 자동 rewrite 0 |
| `DSGN-POST-PR16-STATUS-FENCE` | successor 전체 상태 | implementation/support 없음, 15/15 `NOT_RUN` |

### 주요 successor family의 도입 판단 카드

| 계열 | 제안 동기 | 정확 후보 식별자·표면/API | 정적 의미와 상호작용 | 진단·이행·도구 및 남은 조건 |
|---|---|---|---|---|
| Trait Conformance | requirement·witness·parent evidence를 source/import/link 순서와 무관하게 하나로 닫기 | `RequirementId`, canonical ground conformance key, `SupertraitLink`; 최초 successor route 후보는 DIRECT뿐이며 source spelling은 미선정 | global coherence, locality, overlap rejection, associated binding closure, no specialization/priority, closed MIR evidence | `TC-R016`의 1..10 진단 rank; current lowercase `via` rewrite 금지; `TCC-P1-002..008` 모두 OPEN |
| Class/Enumeration CE-G6 | owner identity, construction/formation, cleanup, dispatch 및 evolution lane의 역할 혼동 제거 | `ClassResponsibilityDescriptor`, `ClassSlotId`, `EnumDescriptor`, `EnumId`, `VariantId`, `VariantFormationPlanId`; current syntax는 유지 | Class/Enum/Trait dispatch domain 분리, `PC-09` terminal tier, `PC-10` 8개 독립 lane, `X-01..X-10`은 owner-closed input만 소비 | final diagnostic registry ID는 null; E-02/E-06 migration default와 auto rewrite 없음; CE 14개와 TCC 7개 P1 OPEN |
| Static-first Dyn/Facet | 닫힌 정적 대안을 먼저 사용하고 open-world boundary에서만 명시적 dynamic carrier를 허용 | explicit owned Dyn pack, immutable `FacetRegistry<Trait>` borrow projection 등의 설계 identity; exact source route 미선정 | compiler retry/fallback/order winner 0, provenance·drop·owner·cast failure를 명시, borrow Facet current 유지 | `SFD-P1-001..008` 정적 폐쇄를 되돌리지 않음; 실행은 별도 `SFD-P1-009`; formatter/runtime route와 product claim 없음 |
| Enum-derived capability | order/display/subset을 raw/tag/layout이나 case-local witness 없이 owner 수준에서 표현 | `enum#increasing`/`enum#decreasing`, case `~>` template, `+type` exact subset 후보 | whole-Enum witness 하나, restricted pure template, finite same-owner subset 및 checked narrowing | explicit same-ground witness conflict는 terminal; P1/TCC gate와 link summary/diagnostic/execution evidence 필요 |
| Literal-shaped collection | 값 literal과 닮은 읽기 쉬운 type spelling 및 immutable-first 책임 모델 | `[T]`, `#mut[T]`, `#set{T}`, `#map{K:V}`, `${label:T,...}`와 freeze/snapshot/view successor | type-goal에서 canonical identity로만 normalize; one-based index, bracket matrix, Union, ABI/serialization 불변 | parser-goal 분리, formatter round-trip, Prelude migration, borrow/MIR/actor evidence 및 target receipt 필요 |
| Dynamic/unsafe quarantine | 불가피한 legacy/dynamic/unsafe 작업의 authority와 escape를 한 lexical owner에 가두기 | `@scope#dynamic` / `@scope#unsafe`와 typed immutable export probe | outer mutation·suspension·모든 authority/resource escape 금지, xVM/LLVM에서 하나의 MIR 의미 | 현행은 Recovery 진단만; provenance, authority accounting, escape proof 및 differential execution이 열려 있음 |

Frontend model은 quarantine, Enum-derived 3개, literal-shaped 3개,
immutable-first 및 freeze/snapshot/view를
`preview_design_nonactivatable`로 직접 결합한다. 이 목록은 대표적인
상세 결합이며 registry의 47개를 축소하는 대체 registry가 아니다.

## 평가·소유권·효과

### 공통 평가 법칙

- 비활성 표면은 평가되지 않으므로 AST/HIR/MIR/runtime event 수가 0이다.
- Preview gate 통과는 parser route 허용일 뿐 feature-local type,
  ownership, effect, error 및 authority 검사를 생략하지 않는다.
- source/import/declaration/provider 순서로 후보를 고르거나 실패 후 다른
  mechanism으로 자동 fallback해서는 안 된다.
- typed identity, semantic identity, serialization tag, discriminant,
  layout, foreign ABI, artifact digest 및 Git identity는 명시적 typed
  mapping 없이는 서로 같지 않다.
- 문서의 예제나 정적 schema는 parser/checker/xVM/LLVM 실행 evidence가
  아니다.

### 정확한 OPEN P1 ledger

| ID | 상태 | 활성화·구체화 대상 |
|---|---|---|
| `CE-C-P1-001` | `OPEN` | Class responsibility descriptor와 owner-admission variance |
| `CE-C-P1-002` | `OPEN` | sealed/final/open partition과 opaque open cell |
| `CE-C-P1-003` | `OPEN` | construction session, commit, publication 및 cleanup |
| `CE-C-P1-004` | `OPEN` | deterministic `ClassSlotId`와 exact callable contract |
| `CE-C-P1-005` | `OPEN` | whole-Class synthesis와 legal Trait evidence route |
| `CE-C-P1-006` | `OPEN` | complete API residue와 8개 독립 compatibility lane |
| `CE-E-P1-001` | `OPEN` | `EnumId`/`VariantId`, payload 및 one/empty boundary |
| `CE-E-P1-002` | `OPEN` | active place, responsibility, recursion 및 cleanup |
| `CE-E-P1-003` | `OPEN` | formation plan, evaluation, failure cleanup 및 payload migration |
| `CE-E-P1-004` | `OPEN` | exact/residual/guard/module-relative partition |
| `CE-E-P1-005` | `OPEN` | successor final-dot member admission과 E-06 migration |
| `CE-E-P1-006` | `OPEN` | raw/ordinal/FFI mapping과 semantic identity 분리 |
| `CE-E-P1-007` | `OPEN` | whole-Enum synthesis와 one Trait origin |
| `CE-E-P1-008` | `OPEN` | complete evolution residue와 8개 독립 lane |
| `TCC-P1-002` | `OPEN` | root-connected surface/profile/recovery/current 격리 |
| `TCC-P1-003` | `OPEN` | canonical identity, normalization, overlap 및 link algorithm |
| `TCC-P1-004` | `OPEN` | current marker coexistence와 exact diagnostic 결합 |
| `TCC-P1-005` | `OPEN` | DIRECT-only initial successor, VIA/AUTO 비활성 |
| `TCC-P1-006` | `OPEN` | closed HIR/MIR/API metadata와 zero relookup |
| `TCC-P1-007` | `OPEN` | independently executed corpus와 target receipt |
| `TCC-P1-008` | `OPEN` | terminology, tooling, formatter/LSP, migration 및 package readiness |
| `SFD-P1-009` | `OPEN` | 별도 authority에 따른 target-bound executable evidence |

`SFD-P1-001..008`은
`CLOSED_BY_DESIGN_NORMATIVE_STATIC_RATIFICATION_R1`이며 위 22개에 포함되지
않는다. P1의 exact 집합을 문서 목적에 맞춰 추가·삭제·재번호화하지
않는다.

### 별도 OPEN action

| ID | 상태 | 우선순위 | 대상 |
|---|---|---|---|
| `M13-A002` | `OPEN` | `P1` | 첫 Rust source-to-lexer-to-parser vertical slice와 실행 receipt |
| `M13-A003` | `OPEN` | `P2` | 최초 public release 전 license/usage notice |
| `M13-A004` | `OPEN` | `P2` | GitHub Actions full-SHA pin과 controlled update |
| `M13-A005` | `OPEN` | `P1` | Expressiveness First의 role/review contract 일치 |

이 네 action은 feature P1과 독립이며 Preview 문서화로 완료되지 않는다.

<!-- deeplus-status-fence: PREVIEW_GATED -->

## 상태별 검토 예제

### gated Preview — FFI

`EX-R48-026`은 정확한 gate가 있는 design-static
`accept_with_gate` 예제다.

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

### gated Preview — NumericArray elementwise power

다음은 `numeric_array_elementwise_power_msp`가 선택된 경우에만 infix
`^`를 elementwise power로 해석하는 검토 예시다. Stable에서 붙은 postfix
`A^`는 transpose라는 별도 owner다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(numeric_array_elementwise_power_msp)
let squared = values ^ 2
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### 비활성 설계 예시 — Enum order/display/subset

다음은 수용된 설계의 후보 표면을 함께 보여 주지만 current source가
아니다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
private enum#increasing Day {
    Mon ~> "Monday"
    Tue ~> "Tuesday"
    Sat ~> "Saturday"
    Sun ~> "Sunday"

    +type Weekend = Sat | Sun
}
```

Display 설계는 inhabitable case 전체의 all-or-none mapping을 요구하며,
partial mapping fallback은 없다.

### 비활성 설계 예시 — literal-shaped type

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/literal-shaped-collection-design.json -->
```deeplus
private type Names = [String]
private type Counts = #map{String: Int}
private type UserRow = ${id: Int, name: String}
```

이는 각각 `List<String>`, `Map<String,Int>`, closed required-label Record
row로 normalize하는 후보일 뿐 current parser syntax가 아니다.

<!-- deeplus-status-fence: RECOVERY_ONLY -->

### 비활성 설계 예시 — quarantine

<!-- deeplus-example: illustrative; status: RECOVERY_ONLY; authority-source: spec/contracts/quarantine-scope.json -->
```deeplus
@scope#dynamic {
    legacyCall()
} -> $result: PlainResult
```

현행에서는 `QUARANTINE_SCOPE_NOT_ACTIVATABLE`로 거부된다.

## 거부되거나 격리된 형식

<!-- deeplus-status-fence: PREVIEW_GATED -->

### gate 실패와 nonactivatable feature

| 조건 | 진단 또는 결과 |
|---|---|
| unknown gate ID | `PREVIEW_GATE_UNKNOWN_FEATURE` |
| registry에는 있으나 `PREVIEW/explicit_feature_gate`가 아님 | `PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE` |
| 첫 duplicate gate ID | `PREVIEW_GATE_DUPLICATE_FEATURE` |
| transitive dependency 누락 | `PREVIEW_GATE_DEPENDENCY_MISSING` |
| gate가 root 첫머리에 없음 | `PREVIEW_GATE_PLACEMENT_INVALID` |
| 비활성 design surface를 ordinary source로 사용 | `NONACTIVATABLE_DESIGN_PROJECTION_NOT_CURRENT` 또는 feature별 진단 |

<!-- deeplus-status-fence: RECOVERY_ONLY -->

### `RECOVERY_ONLY` 표면

Recovery는 offending spelling과 diagnostic span을 보존하지만 허용된
semantic node를 만들지 않는다.

| 복구 표면 | 현행 대안 또는 주 진단 |
|---|---|
| generic `def#entry name<T>(...)` | `ENTRY_SIGNATURE_NOT_ADMITTED`; non-generic entry 사용 |
| `facet[inout ...]`, `facet[move ...]` | owned/inout Facet 비활성; borrow Facet만 current |
| `Facet<inout ...>`, `Facet<move ...>` | 비활성 타입 probe; admitted HIR 0 |
| `null` | `NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE`; `::none` 또는 `Option<T>::none` |
| `value[]` | `INDEX_SUFFIX_REQUIRES_AXIS`; scalar/range/`*` axis 명시 |
| `operator <symbol> precedence N` | `CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT`; named API 사용 |
| parameter `name**: T` | `NAMED_REST_DOUBLE_STAR_REMOVED_USE_TRIPLE_STAR`; `name***: Record` |
| function type `T**` | 같은 진단; `Record***` |
| `let@lazy` | `LAZY_BINDING_USE_HASH`; `let#lazy` |
| unit `A · B` | `UNIT_MULTIPLICATION_USE_STAR`; `A * B` |
| `@scope#dynamic` / `@scope#unsafe` | `QUARANTINE_SCOPE_NOT_ACTIVATABLE` |

<!-- deeplus-status-fence: REMOVED -->

### `REMOVED` 표면

다음 다섯 family는 compatibility gate 없이 제거되었다.

| 제거된 표면 | 현행 대안 | 대표 진단 |
|---|---|---|
| Map String-key dot projection `map.key` | `map["key"]` 또는 명시적 Map API | `MEMBER_NOT_FOUND` |
| prefix/postfix `++`, `--` | 명시적 assignment | `POSTFIX_MUTATION_OPERATOR_NOT_CURRENT` 등 |
| callable kind `def#tailrec` | ordinary recursive function; tail 분석은 tooling | `CALLABLE_PROFILE_COMBINATION_NOT_ADMITTED` |
| regex literal | `String`/`Bytes`를 받는 명시적 pattern library | `UNKNOWN_PREFIXED_LITERAL` |
| automatic heterogeneous-List Union inference | expected `List<A | B>` 명시 | `LIST_LITERAL_ELEMENT_JOIN_FAILED` |

source AST quote `@ast`, 그 mode spelling, 붙은 `^{...}`, 붙은
`?Identifier`, legacy `#array{...}` constructor도 완전히 제거되어
Stable/Preview/Recovery production, scanner mode, AST/HIR/MIR identity가
없다. `class#sealed`, parameter/type named-rest `**`, `expr${...}`와 같은
역사적 철자는 각각 현행 `sealed class`, `***`, `!{}`/`!!{}` 경계를
따른다. Recovery production이 명시되지 않은 removed spelling을
formatter나 migration option이 다시 활성화해서는 안 된다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- Trait/Conformance successor와 TCC P1은 [클래스, Trait, 적합성 및
  확장](06-classes-traits-conformance-and-extensions.md)을 따른다.
- Enum/Record 및 Enum-derived 설계는 [Enum, Record, 스키마, 비트필드 및
  단위](07-enums-records-schemas-bitfields-and-units.md)을 따른다.
- literal-shaped collection과 one-based indexing은 [컬렉션, 인덱싱 및
  슬라이싱](09-collections-indexing-and-slicing.md)을 따른다.
- owned/inout Facet, weak atomics 및 transfer는 [소유권, 대여 및
  책임](12-ownership-borrowing-and-responsibility.md)을 따른다.
- async callable/comprehension, coroutine 및 session proposal은 [비동기,
  태스크, 액터 및 동시성](13-async-tasks-actors-and-concurrency.md)을
  따른다.
- refinement, solver, use-site projection 및 Dyn-RCTS는 [타입, 제네릭 및
  리파인먼트](04-types-generics-and-refinement.md)을 따른다.
- custom/fixed operator와 NumericArray power는 [표현식 및
  연산자](08-expressions-and-operators.md)을 따른다.

Preview promotion은 다음 순서를 건너뛸 수 없다.

1. exact design decision과 current 대안/비활성 fence
2. exact EBNF root/route와 frontend owner/admission
3. terminating type/ownership/effect/coherence algorithm
4. deterministic diagnostics, recovery 및 migration policy
5. formatter/LSP와 public API/metadata residue
6. MIR identity와 xVM/LLVM observable equivalence
7. positive/negative/boundary/mutation corpus
8. target-bound product receipt와 별도 activation authority

## 정본 근거

- 전체 언어 상태와 Post-PR16 Preview 설계:
  [`spec/language.md`](../../spec/language.md)
- exact profile production:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- source root, gate, Recovery 및 비활성 상세 결합:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 688-row feature registry:
  [`spec/features/catalog`](../../spec/features/catalog)
- activatable/nonactivatable gate map:
  [`spec/features/gates.json`](../../spec/features/gates.json)
- controlling current decision:
  [`decisions/language/current-decisions.json`](../../decisions/language/current-decisions.json)
- exact 22 OPEN P1과 별도 M13 action:
  [`current/current-pointer.json`](../../current/current-pointer.json)
- Enum-derived 계약:
  [`spec/contracts/enum-derived-capabilities.json`](../../spec/contracts/enum-derived-capabilities.json)
- literal-shaped collection 계약:
  [`spec/contracts/literal-shaped-collection-design.json`](../../spec/contracts/literal-shaped-collection-design.json)
- quarantine 계약:
  [`spec/contracts/quarantine-scope.json`](../../spec/contracts/quarantine-scope.json)
- type/MIR 권위:
  [`spec/types/type-system.md`](../../spec/types/type-system.md),
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- diagnostic, predicate 및 example evidence:
  [`spec/diagnostics/catalog`](../../spec/diagnostics/catalog),
  [`spec/types/predicates`](../../spec/types/predicates),
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
