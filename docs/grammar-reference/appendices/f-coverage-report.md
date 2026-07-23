<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-grammar-reference-semantic-coherence-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 560 | 560 | `통과` |
| `features` | 688 | 688 | `통과` |
| `diagnostics` | 1281 | 1281 | `통과` |
| `predicates` | 247 | 247 | `통과` |
| `prelude_entries` | 56 | 56 | `통과` |
| `examples` | 703 | 703 | `통과` |
| `hard_keywords` | 30 | 30 | `통과` |
| `contextual_words` | 101 | 101 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 89 |
| `STABLE` | 443 |
| `PREVIEW` | 13 |
| `RECOVERY` | 15 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `b97cae319eadb662d66802bbbed5bc6defe9ad937ac298614a7b67291383ce5f` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `1da0324d78b27ebe1942520e8105d07fa95557471c591b5a49c1215d5e3bcb29` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `2738ac79204ff5da23873778a90f85d9600345976894e2df58230c89d0602049` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `b80efb9cc58582b318d614e7604625d048043213b4a274275e232589be48d984` |
| `type_system` | `spec/types/type-system.md` | `846ac8f55219fe310e077eff8c55f8aa53e052c47174755001c31d175e96b0ea` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `13ab29caa082d1debf89df9b4a6e7e304f0e1aeb755609d1cd10148981b51cbe` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `049354dc08fece753a694ef28dd22791c93480f0a98fc8f9160ef4f7b8f3be49` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `bcac1f2c6ace1049af61574f94980e6edf01c9231328513cb7b7dc95e03c1240` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `c448b9a803218dd04bea320824ee1c4e7e763e2b0717523e69aa110660131474` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `136511ff5e4d6303c5ebd21ce4680e55852b16c4076d83af260bb6403de8a0db` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `b4c92f4eea032853addf07afe8cb8a32e43b8a42e998762bdde3226dfc602f42` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `bc4fb86b14e34ad123c4ed663ab5158d9ff02ff565703799c7f8a580d3d4f5b4` |
| `prelude` | `library/prelude/prelude.md` | `d9cfa081620c15d84e76ac963ba41296c6ef686c19720a58e626c770dec18003` |
| `current_decisions` | `decisions/language/current-decisions.json` | `0359f3fca22195b46e67408a7513678eb9fe0a389a36c73ec73f33b4dff42e77` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `ac50a544b383ae7d8fb94fc05299a2eaaa09eea695e5591986a2fff5f5c5bc8f` |
