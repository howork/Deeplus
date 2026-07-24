<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# Deeplus 문법 명세 및 참조서

이 탐색 문서는 검토된 문법 참조서 계약에서 결정론적으로 생성됩니다.

## 본문 참조서

- [landing — Deeplus 문법 명세 및 참조서](README.md)
- [00 — 상태, 권위 및 표기법](00-status-authority-and-notation.md)
- [01 — 어휘 구조](01-lexical-structure.md)
- [02 — 프로그램, 모듈 및 가져오기](02-programs-modules-and-imports.md)
- [03 — 선언, 바인딩 및 이름](03-declarations-bindings-and-names.md)
- [04 — 타입, 제네릭 및 리파인먼트](04-types-generics-and-refinement.md)
- [05 — 함수, 메서드, 클로저 및 호출](05-functions-methods-closures-and-calls.md)
- [06 — 클래스, 트레이트, 적합성 및 확장](06-classes-traits-conformance-and-extensions.md)
- [07 — 열거형, 레코드, 스키마, 비트필드 및 단위](07-enums-records-schemas-bitfields-and-units.md)
- [08 — 표현식 및 연산자](08-expressions-and-operators.md)
- [09 — 컬렉션, 인덱싱 및 슬라이싱](09-collections-indexing-and-slicing.md)
- [10 — 패턴, 구조 분해 및 패턴 매칭](10-patterns-destructuring-and-matching.md)
- [11 — 제어 흐름, 오류, 효과 및 정리](11-control-flow-errors-effects-and-cleanup.md)
- [12 — 소유권, 대여 및 책임](12-ownership-borrowing-and-responsibility.md)
- [13 — 비동기, 태스크, 액터 및 동시성](13-async-tasks-actors-and-concurrency.md)
- [14 — FFI, unsafe 경계, 메타프로그래밍 및 프로파일](14-ffi-unsafe-metaprogramming-and-profiles.md)
- [15 — 프리뷰, 복구 및 제거된 표면](15-preview-recovery-and-removed-surfaces.md)
- [16 — 문맥별 구문과 production 길잡이](16-contextual-syntax-and-production-guide.md)
- [17 — 이름 해석, 타입 추론 및 호출 판정](17-name-resolution-type-inference-and-calls.md)
- [18 — 평가, 소유권, MIR 및 백엔드](18-evaluation-ownership-mir-and-backends.md)
- [19 — Prelude, 공급자, 진단 및 적합성](19-prelude-providers-diagnostics-and-conformance.md)
- [20 — Preview Gated 상세 참조](20-preview-gated-reference.md)
- [21 — Preview Design — 타입, 객체 및 Trait](21-preview-design-types-objects-and-traits.md)
- [22 — Preview Design — 컬렉션, 문맥 및 제어](22-preview-design-collections-context-and-control.md)
- [23 — Preview Design — 동시성, FFI 및 런타임](23-preview-design-concurrency-ffi-and-runtime.md)
- [24 — 통합 예제로 읽는 현행 Deeplus](24-integrated-worked-examples.md)

## 긴 장을 빠르게 찾는 경로

- exact production과 contextual admission: [16 — 문맥별 구문과 production 길잡이](16-contextual-syntax-and-production-guide.md)
- 이름·generic·overload·call channel 결정: [17 — 이름 해석, 타입 추론 및 호출 결정](17-name-resolution-type-inference-and-calls.md)
- 평가 순서·소유권·MIR·backend 관찰: [18 — 평가, 소유권, MIR 및 backend](18-evaluation-ownership-mir-and-backends.md)
- Prelude·provider·진단·conformance evidence: [19 — Prelude, 공급자, 진단 및 적합성](19-prelude-providers-diagnostics-and-conformance.md)
- 여러 기능을 함께 추적하는 완성 예제: [24 — 통합 예제로 읽는 현행 Deeplus](24-integrated-worked-examples.md)

## Preview와 Preview Design 상세 카드

아래 47개 행은 registry identity에서 상태 fence, 상세 설명, 양성·음성·경계 시나리오와 예제로 직접 연결됩니다. 카드가 존재한다는 사실은 source activation 또는 제품 지원을 뜻하지 않습니다.

| Feature ID | 상태 | 설명 |
|---|---|---|
| [`async_callable_literal_profile`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-async_callable_literal_profile) | `PREVIEW_DESIGN` | Asynchronous callable literal profile |
| [`async_comprehension`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-async_comprehension) | `PREVIEW_DESIGN` | Async comprehension |
| [`automatic_observation_tracking`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-automatic_observation_tracking) | `PREVIEW_DESIGN` | Automatic observation tracking |
| [`c_aggregate`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-c_aggregate) | `PREVIEW_DESIGN` | C aggregate |
| [`c_stored_callback`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-c_stored_callback) | `PREVIEW_DESIGN` | C stored callback |
| [`c_variadic`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-c_variadic) | `PREVIEW_DESIGN` | C variadic |
| [`class_static_activation`](21-preview-design-types-objects-and-traits.md#preview-feature-class_static_activation) | `PREVIEW_DESIGN` | Class static activation |
| [`conformance_law_proof_block_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-conformance_law_proof_block_preview_design) | `PREVIEW_DESIGN` | Conformance law proof block preview-design |
| [`contextual_operation_anchor_dmad`](22-preview-design-collections-context-and-control.md#preview-feature-contextual_operation_anchor_dmad) | `PREVIEW_DESIGN` | \`&expr\` contextual operation anchor D-MAD |
| [`dependent_refinement_value_capture`](21-preview-design-types-objects-and-traits.md#preview-feature-dependent_refinement_value_capture) | `PREVIEW_DESIGN` | Dependent refinement value capture |
| [`directed_coroutine_group`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-directed_coroutine_group) | `PREVIEW_DESIGN` | Directed coroutine group |
| [`dyn_inspection`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-dyn_inspection) | `PREVIEW_DESIGN` | Dyn inspection |
| [`dyn_rcts_family`](21-preview-design-types-objects-and-traits.md#preview-feature-dyn_rcts_family) | `PREVIEW_DESIGN` | Dynamic RCTS checked-carrier family |
| [`dynamic_trait_attach_detach_stateless_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-dynamic_trait_attach_detach_stateless_preview_design) | `PREVIEW_DESIGN` | Stateless dynamic trait attach/detach design placeholder |
| [`dynamic_unsafe_quarantine_scope_msp`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-dynamic_unsafe_quarantine_scope_msp) | `PREVIEW_DESIGN` | Dynamic/unsafe quarantine scope minimum sound profile |
| [`effectful_static_activation`](21-preview-design-types-objects-and-traits.md#preview-feature-effectful_static_activation) | `PREVIEW_DESIGN` | Effectful static activation |
| [`enum_case_display_mapping_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-enum_case_display_mapping_preview_design) | `PREVIEW_DESIGN` | Enum case Display mapping Preview design |
| [`enum_declaration_order_ord_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-enum_declaration_order_ord_preview_design) | `PREVIEW_DESIGN` | Enum declaration-order Ord derivation Preview design |
| [`enum_exact_variant_subset_alias_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-enum_exact_variant_subset_alias_preview_design) | `PREVIEW_DESIGN` | Enum exact-variant subset alias Preview design |
| [`explicit_broadcast_marker_msp`](22-preview-design-collections-context-and-control.md#preview-feature-explicit_broadcast_marker_msp) | `PREVIEW_DESIGN` | Explicit NumericArray broadcast operand marker candidate |
| [`explicit_context_argument_ampersand_spelling`](22-preview-design-collections-context-and-control.md#preview-feature-explicit_context_argument_ampersand_spelling) | `PREVIEW_DESIGN` | \`&expr\` context-argument spelling candidate |
| [`extension_dot_call_sugar`](21-preview-design-types-objects-and-traits.md#preview-feature-extension_dot_call_sugar) | `PREVIEW_DESIGN` | Extension dot-call sugar |
| [`facet_inout_pack_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-facet_inout_pack_preview_design) | `PREVIEW_DESIGN` | Inout Facet package design |
| [`facet_owned_pack_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-facet_owned_pack_preview_design) | `PREVIEW_DESIGN` | Owned Facet package design |
| [`ffi_c_extern_unsafe_surface_msp`](20-preview-gated-reference.md#preview-feature-ffi_c_extern_unsafe_surface_msp) | `PREVIEW` | FFI C extern unsafe surface disposition |
| [`ffi_minimum_sound_profile`](20-preview-gated-reference.md#preview-feature-ffi_minimum_sound_profile) | `PREVIEW` | Safe FFI minimum sound profile |
| [`first_class_witness_value_not_current`](21-preview-design-types-objects-and-traits.md#preview-feature-first_class_witness_value_not_current) | `PREVIEW_DESIGN` | First-class Witness value not current |
| [`freeze_snapshot_view_responsibility_preview_design`](22-preview-design-collections-context-and-control.md#preview-feature-freeze_snapshot_view_responsibility_preview_design) | `PREVIEW_DESIGN` | Freeze snapshot view responsibility Preview design |
| [`generic_named_extension_set_target`](21-preview-design-types-objects-and-traits.md#preview-feature-generic_named_extension_set_target) | `PREVIEW_DESIGN` | Generic named extension set target |
| [`immutable_first_collection_ownership_preview_design`](22-preview-design-collections-context-and-control.md#preview-feature-immutable_first_collection_ownership_preview_design) | `PREVIEW_DESIGN` | Immutable-first collection ownership Preview design |
| [`literal_shaped_closed_record_type_surface_preview_design`](22-preview-design-collections-context-and-control.md#preview-feature-literal_shaped_closed_record_type_surface_preview_design) | `PREVIEW_DESIGN` | Literal-shaped closed Record type surface Preview design |
| [`literal_shaped_collection_type_surface_preview_design`](22-preview-design-collections-context-and-control.md#preview-feature-literal_shaped_collection_type_surface_preview_design) | `PREVIEW_DESIGN` | Literal-shaped collection type surface Preview design |
| [`local_witness_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-local_witness_preview_design) | `PREVIEW_DESIGN` | Local witness preview-design |
| [`module_static_entrance`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-module_static_entrance) | `PREVIEW_DESIGN` | Module static entrance |
| [`negative_impl_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-negative_impl_preview_design) | `PREVIEW_DESIGN` | Negative impl preview-design |
| [`nullsafe_control`](22-preview-design-collections-context-and-control.md#preview-feature-nullsafe_control) | `PREVIEW_DESIGN` | Nullsafe control |
| [`numeric_array_elementwise_power_msp`](20-preview-gated-reference.md#preview-feature-numeric_array_elementwise_power_msp) | `PREVIEW` | NumericArray elementwise power law |
| [`prototype_delta`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-prototype_delta) | `PREVIEW_DESIGN` | Prototype delta |
| [`sealed_multimethod_family`](21-preview-design-types-objects-and-traits.md#preview-feature-sealed_multimethod_family) | `PREVIEW_DESIGN` | Sealed multimethod family |
| [`session_protocol_lite_provider`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-session_protocol_lite_provider) | `PREVIEW_DESIGN` | Session protocol lite provider |
| [`solver_backed_general_refinement`](21-preview-design-types-objects-and-traits.md#preview-feature-solver_backed_general_refinement) | `PREVIEW_DESIGN` | Solver backed general refinement |
| [`specialization_preview_design`](21-preview-design-types-objects-and-traits.md#preview-feature-specialization_preview_design) | `PREVIEW_DESIGN` | Specialization preview-design |
| [`state_machine_source_syntax`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-state_machine_source_syntax) | `PREVIEW_DESIGN` | State machine source syntax |
| [`static_once_value`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-static_once_value) | `PREVIEW_DESIGN` | Static once value |
| [`structural_prototype_extension`](21-preview-design-types-objects-and-traits.md#preview-feature-structural_prototype_extension) | `PREVIEW_DESIGN` | Structural prototype extension |
| [`use_site_projection_dmad`](21-preview-design-types-objects-and-traits.md#preview-feature-use_site_projection_dmad) | `PREVIEW_DESIGN` | Use-site generic projection D-MAD |
| [`weak_atomic_ordering`](23-preview-design-concurrency-ffi-and-runtime.md#preview-feature-weak_atomic_ordering) | `PREVIEW_DESIGN` | Weak atomic ordering |

## 생성된 부록

- [A — 정확한 production 색인](appendices/a-production-index.md)
- [B — 토큰, 키워드 및 연산자](appendices/b-token-keyword-operator-index.md)
- [C — 기능 및 상태 색인](appendices/c-feature-status-index.md)
- [D — 진단 및 술어](appendices/d-diagnostic-predicate-index.md)
- [E — Prelude 및 예제](appendices/e-prelude-example-index.md)
- [F — 커버리지 보고서](appendices/f-coverage-report.md)
- [기계 판독형 커버리지 manifest](coverage-manifest.json)
