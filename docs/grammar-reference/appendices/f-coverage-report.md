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
| `diagnostics` | 1487 | 1487 | `통과` |
| `predicates` | 284 | 284 | `통과` |
| `prelude_entries` | 81 | 81 | `통과` |
| `examples` | 766 | 766 | `통과` |
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
| `human_language` | `spec/language.md` | `ce7caa3ea842fd06197c5ba5ce2bcba683f84f1528656c83162c9a159f772ab6` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `90f95ba7ff4e163eb1f99752cf70602d2042ab00b8a775cb3cab1259d59d706d` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `0ab24a754b9f95331c9eddb9bfdf737240f60b15bfb2eed99cdc5959508b7a1b` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `914399e4fd35f552cab3111613244cb6844b6313f8b9bd17ebbead0ad7df9bd9` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `54f3f08b27ceb58333ff70d0b7a522e51ff1b76116fdc78e216c3e2e57601043` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `4ede074bd28425c94eda7776093e58d3821dadf8a05212efe3eab5a4a6abb711` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `8d612dd6a54a80ec1c77192c3d8f0358e1bc6bea4efa1c822b4b2a4e2aeb8401` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `78945448e06e57d040a395089f7b9a7d5bff29485ef024a5c6655fbf797820cb` |
| `type_system` | `spec/types/type-system.md` | `7f4c5e94ae00cbe7fc5c2da0c2b7cdec2d1be58782452cbbca3eaf1ecc6730a9` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `1d15a36fbce78daec7002fa3032664c5aa41e78d34d607b6dd802f3719a6a797` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `45fd39519a3b88f6ff5182c368f4cee760febe4414e4a2d52cdc75f59f69ef84` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `d085b7a1965f037698578c4447685c1f3804ece00d933401cd2066b32a13b976` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `355c295018e32054e08082b07494efdd0d7f282a2df3ddc923d4ad2cb3a9f7c3` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `a6094a7c9862e764b13aa935804b086a5d3a7e9ebf087b3b5506ed84c3e4a899` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `b6f2763556c02feafcb415130b0567a315b38c9321bb48d81f776ec71cecd7be` |
| `current_decisions` | `decisions/language/current-decisions.json` | `25e1c817ea5e2d29b2a416dec1dd5de8c5fa211af8fe87ef13210646afae48a8` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `82589898f6546c58d1a01155341c3110aff58911422aaf07228170770d819580` |
