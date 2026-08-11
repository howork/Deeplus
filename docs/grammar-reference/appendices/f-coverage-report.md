<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-r77-publication-policy-closure-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 656 | 656 | `통과` |
| `features` | 723 | 723 | `통과` |
| `diagnostics` | 1491 | 1491 | `통과` |
| `predicates` | 285 | 285 | `통과` |
| `prelude_entries` | 81 | 81 | `통과` |
| `examples` | 769 | 769 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 105 | 105 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 87 |
| `STABLE` | 556 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `4cb49e2afd42a39aae426f8fe5753a4c4f9517a916bf277837cd653ea30e4f3d` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `d06dceda812d6965da447f1f6a173d93ba23860f987e4de28dc31c0be78717fb` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `d44c118a3de94313ba31ecd35eecaf084ce34f270d1d167ecbb85f1753217f1f` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `f69b2e438df00e62afe805a1bcef2d1b7e069bda988862fa35d58942828d7be2` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `d15f215920059220c163de1ddd4804a6718193bbd663235cb23e3e947f8a04b3` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `f507c99654d6af6b0beede05b510f736445f6146a605a7d5184c8362bf247ff7` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `402438a23f7940741e8f512beaa60af8e028f6f372a6075cc42778021f22fc23` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `d3555a70eb98913943041ab0bcf1399fa4f382e23ca76302b3b0016f5aa7c61f` |
| `type_system` | `spec/types/type-system.md` | `07e6ebcd219486d5c3fab519454d6bc9500499498efb36471badf6f03d988783` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `1998d954c9eeffe5bd524a175d6b41b7ebe95106d14c2860a1ec69246e2617ab` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `45fd39519a3b88f6ff5182c368f4cee760febe4414e4a2d52cdc75f59f69ef84` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `d085b7a1965f037698578c4447685c1f3804ece00d933401cd2066b32a13b976` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `4e1948381756bd0c5d940b9f40b3c57165d44df6886f718815b3c7c3ee09e979` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `a6094a7c9862e764b13aa935804b086a5d3a7e9ebf087b3b5506ed84c3e4a899` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `b6f2763556c02feafcb415130b0567a315b38c9321bb48d81f776ec71cecd7be` |
| `current_decisions` | `decisions/language/current-decisions.json` | `25e1c817ea5e2d29b2a416dec1dd5de8c5fa211af8fe87ef13210646afae48a8` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `372324120d6883e7fe16c9d34e6d225fbf7e73fc6a6fb8fe636b918198700049` |
