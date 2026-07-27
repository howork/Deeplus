<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-pattern-sequence-multivalue-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 620 | 620 | `통과` |
| `features` | 719 | 719 | `통과` |
| `diagnostics` | 1414 | 1414 | `통과` |
| `predicates` | 268 | 268 | `통과` |
| `prelude_entries` | 66 | 66 | `통과` |
| `examples` | 726 | 726 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 101 | 101 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 516 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `9842960e29a1b56f59d27df6dd049a7416dc229df3d5ea12711b49e6a78c2b5d` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `0d945d649c4f185feca30ca7594e298cfe3c55e22ed1534cc340fe0881cba46d` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `40eb56cb2f8f2ce504c0cbe2e90ab3b644d353a720222008886814fce2a75f34` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `d01a474be4a1ad4eae8a9f6befa5a12ae08959972f552b8fb2ebbdcc89a4b027` |
| `type_system` | `spec/types/type-system.md` | `ebe1122be357d7f676ba5deb56deafbcf5d78b18f0c617e37233a1acb2939942` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `77eb73a375e3f6d770a03d97e5044ba46e92b96fb595068cff644f46b01a1d39` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `57be18eb3edf66b5395d0f232d8fab326f33ed2bfbe0ee875dea38e057931ea5` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `82e03c1cf67ccbd6679c421f2379afd78687a4cd82870f17bb90168ac7126f27` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `d6ad1c9c5ed48d63d88baac85e9619b53377e9a3d5e4154ddb34c81c1725d48e` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `afc16fbce335f73d772809f3b8e0e5f769a41bebf48a401f7de469f28502bf43` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `128206e616f549e5ed236a529970f1deeea2883ed915ac54673ee972abf95b09` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `0034e304788fe5b255f5f26d988265d992bd339558d38792126ee67e633528cb` |
| `prelude` | `library/prelude/prelude.md` | `da2f765591f73ecd026d3094e74d1f315d9d9aec3b8a153a49a5f8e89b61d7b6` |
| `current_decisions` | `decisions/language/current-decisions.json` | `d11f3262976510dd4f6f718102c389474e53106e36c5e528836dd6f6539063a6` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `4a59e443a9527079c78e6196273dade5b795368550bd4f22ee04ab9fd2057e1a` |
