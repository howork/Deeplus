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
| `diagnostics` | 1506 | 1506 | `통과` |
| `predicates` | 292 | 292 | `통과` |
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
| `human_language` | `spec/language.md` | `5f9531d5af1d4a5b51ae98af0d0924960062b2e26dd06bd95f1145e8159f270d` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `fefec3a3c8425d4911c8a162fd7f51ee4a63c946f32bcbba0face055a1c9863f` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `9464f078bfac5429bc71339ed9ea52c68e18dc588fd65ddfb541ed0a8efbefaf` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `f69b2e438df00e62afe805a1bcef2d1b7e069bda988862fa35d58942828d7be2` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `b84debf113f949de6ca8e60b086dfb3f14682b3bed030d8464cf827741ab2772` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `f507c99654d6af6b0beede05b510f736445f6146a605a7d5184c8362bf247ff7` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `402438a23f7940741e8f512beaa60af8e028f6f372a6075cc42778021f22fc23` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `19eb6a1b2e929bac6f38e97ced5a6685b80f5a4c663e92ba2f6a55cf5b0e760b` |
| `type_system` | `spec/types/type-system.md` | `e927d9c4fd5bd2522230201ade051f650d1019f33fc6ee943c78841282a06ad2` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `d52a1db077323cfda4f8d1352a2a63a4804724d8d3fa7a9ecc638cea310c81ed` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `f8f6e8e0eb9acdce4a905ac043b8e86ebc6c3f99f379f9e7a166d04e7f83f185` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `fdf63cd121a82de4d3b751d8179b634a3358917b8d1772e334c6a6a0b95dd536` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `ed9368b3e97bb89afc273217f2db74ccfee09937a61d960753c9de06e83804a0` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `6a2f5fe17b427741dbe79694edfe28cc467175ae73ff256b04f2fa1b3563196f` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `e1a316a76505a1922155342eda24b3b12fbea129863b8cf57c19b25eec229eca` |
| `current_decisions` | `decisions/language/current-decisions.json` | `25e1c817ea5e2d29b2a416dec1dd5de8c5fa211af8fe87ef13210646afae48a8` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `58ea6d599f4eeaf163f514e2a8e46691da9f07d46d62c8953990c71cb1afb221` |
