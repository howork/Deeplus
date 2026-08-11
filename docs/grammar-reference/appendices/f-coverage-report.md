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
| `diagnostics` | 1498 | 1498 | `통과` |
| `predicates` | 287 | 287 | `통과` |
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
| `human_language` | `spec/language.md` | `bbf4b359e1a08445235700fecb894d79e48c39a172166fadf223091a2946a788` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `d06dceda812d6965da447f1f6a173d93ba23860f987e4de28dc31c0be78717fb` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `d44c118a3de94313ba31ecd35eecaf084ce34f270d1d167ecbb85f1753217f1f` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `f69b2e438df00e62afe805a1bcef2d1b7e069bda988862fa35d58942828d7be2` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `d15f215920059220c163de1ddd4804a6718193bbd663235cb23e3e947f8a04b3` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `f507c99654d6af6b0beede05b510f736445f6146a605a7d5184c8362bf247ff7` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `402438a23f7940741e8f512beaa60af8e028f6f372a6075cc42778021f22fc23` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `53adb13f1871568e025d5a1e225f00294a56ad2278feebbca5d3a7f6952038dd` |
| `type_system` | `spec/types/type-system.md` | `2800f23b874375d9ada2692baf3d8c8755cd2cbf58720003d34a6b98533638df` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `2feae9e1d9dd3dd67925a3bb2ee911db762893891fedb9b1e8d821ed48ce951c` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `f8f6e8e0eb9acdce4a905ac043b8e86ebc6c3f99f379f9e7a166d04e7f83f185` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `fdf63cd121a82de4d3b751d8179b634a3358917b8d1772e334c6a6a0b95dd536` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `4e1948381756bd0c5d940b9f40b3c57165d44df6886f718815b3c7c3ee09e979` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `6a2f5fe17b427741dbe79694edfe28cc467175ae73ff256b04f2fa1b3563196f` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `e1a316a76505a1922155342eda24b3b12fbea129863b8cf57c19b25eec229eca` |
| `current_decisions` | `decisions/language/current-decisions.json` | `25e1c817ea5e2d29b2a416dec1dd5de8c5fa211af8fe87ef13210646afae48a8` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `b15658c50eef3ab2b870f0482d51f01e0ea40cd41ac6f39a320bfb38f0430283` |
