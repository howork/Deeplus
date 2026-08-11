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
| `diagnostics` | 1496 | 1496 | `통과` |
| `predicates` | 286 | 286 | `통과` |
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
| `human_language` | `spec/language.md` | `cd2133000fe9a5178026f45fb5032820aa1b4423028cd6d33f57d2555d109fa9` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `d06dceda812d6965da447f1f6a173d93ba23860f987e4de28dc31c0be78717fb` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `d44c118a3de94313ba31ecd35eecaf084ce34f270d1d167ecbb85f1753217f1f` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `f69b2e438df00e62afe805a1bcef2d1b7e069bda988862fa35d58942828d7be2` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `d15f215920059220c163de1ddd4804a6718193bbd663235cb23e3e947f8a04b3` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `f507c99654d6af6b0beede05b510f736445f6146a605a7d5184c8362bf247ff7` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `402438a23f7940741e8f512beaa60af8e028f6f372a6075cc42778021f22fc23` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `52a8cda53f353002731d58fd150dd28075e9b0d25cb54624195f70d0cb600880` |
| `type_system` | `spec/types/type-system.md` | `1f3b94220bcce52254dcea43c5f4a7f552129d6a846f52db8fbcecf00da1a180` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `a556a8daab75de29955a1ed84bdcc1a5e6bcf7dbcfae918cf504bd23365bb036` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `f8f6e8e0eb9acdce4a905ac043b8e86ebc6c3f99f379f9e7a166d04e7f83f185` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `d085b7a1965f037698578c4447685c1f3804ece00d933401cd2066b32a13b976` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `4e1948381756bd0c5d940b9f40b3c57165d44df6886f718815b3c7c3ee09e979` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `a6094a7c9862e764b13aa935804b086a5d3a7e9ebf087b3b5506ed84c3e4a899` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `b6f2763556c02feafcb415130b0567a315b38c9321bb48d81f776ec71cecd7be` |
| `current_decisions` | `decisions/language/current-decisions.json` | `25e1c817ea5e2d29b2a416dec1dd5de8c5fa211af8fe87ef13210646afae48a8` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `f2992cc3caa63d4ae0ed832506785d02e50bf70aeee8c83d910212e753233491` |
