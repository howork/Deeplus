<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-managed-root-runtime-fusion-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 643 | 643 | `통과` |
| `features` | 721 | 721 | `통과` |
| `diagnostics` | 1476 | 1476 | `통과` |
| `predicates` | 278 | 278 | `통과` |
| `prelude_entries` | 72 | 72 | `통과` |
| `examples` | 743 | 743 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 105 | 105 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 539 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `23beff0ecc3d8e40f7a9861f85233366a40db37bebfd76fffac72e584ef57e09` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `a95ce1649e872fa0803300bff4e720e1c1d6a5afa54fa546de584501c8da2276` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `6b7d2db6e3110667a4d431889245e94a1195afd9d34ee751a38e936ad314be5d` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `56f42fd6b7668c6cdd13c5461d8d51401e38b80474761b6b3209420dd9cd0c27` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `c61cfd429021bc89e36df028f5a82f44a28e1c18710b500cf774db95d8044f97` |
| `type_system` | `spec/types/type-system.md` | `f6dc240149a08f280d1ef073f385268ad3574ba6b781d8b5ffc77255b3e7eedd` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `14519a8a6d7e042f2af91c115c80e44ec13c39fe33e2f7a190fd791815edf102` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `e68a4237fd8e231ce74601295e5cb9975fc60afa03bbe81500e5368183d96efe` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `35c20cccef65dcb19c0477b4470a11c8f97a08f8a0dde4cef1098b573df998f1` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `dead650e9307bbd51c3cb70916ce26ef31a995f54ab3e537fb33cb625b83a2b2` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `1d687664e37032f0a099abef6e4db0e83df5ea37d490d1ad026a92111a70e663` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `3cd9f28d0483090d6558e24ce7f50fc0d0dbdb2299ad4d0b3ff51d0a035cfe39` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `4327168a3dc9d79391237b20af8d8ac48d4c11b50803a129a8b6534187026366` |
| `prelude` | `library/prelude/prelude.md` | `699f06e8ce8a367b108f08d51060d01b41e69318a867f2eb15ce655735ce9c41` |
| `current_decisions` | `decisions/language/current-decisions.json` | `9cbc16c4ab38eb9c1d571509e06f488cab4ba3720f79272dce3e03a36e7d3a30` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `f20be36a3c49c82fb3eca6a5a372adda52657b365715d9ba58e13a87c87340e2` |
