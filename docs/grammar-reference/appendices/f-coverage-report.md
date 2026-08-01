<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-frontend-readiness-r11-r19-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 638 | 638 | `통과` |
| `features` | 719 | 719 | `통과` |
| `diagnostics` | 1443 | 1443 | `통과` |
| `predicates` | 277 | 277 | `통과` |
| `prelude_entries` | 72 | 72 | `통과` |
| `examples` | 743 | 743 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 105 | 105 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 534 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `fd77864fc6d911fbf91d3b712a27323df67c9226d15fb8359f4eb8f5e643b7a1` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `055ed7010ad8b78345d0414ffe696988abb52d13fa6f86e3dd1dae4610a4c962` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `b0fa913f3c9a7e8bc8206526c6139f40e42b6e0d2fbb597da068a530c93d8b56` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `445c44c909d2f29343aba8f8b78c9d34f8d043e0588b6448b2f320ce387aa61f` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `de80448f1a3d13f449b1e60a1cd20f0666281b336c095ccce262c41b1adf8337` |
| `type_system` | `spec/types/type-system.md` | `5f72e7ee39740a3bd329f2bbc45c17b9f7bb5707453ab94678b8e89cb62a0558` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `95199faee37482c25896a6bedb3eb1285087d6c9c522164d9f027c58b5da6559` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `e68a4237fd8e231ce74601295e5cb9975fc60afa03bbe81500e5368183d96efe` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `35c20cccef65dcb19c0477b4470a11c8f97a08f8a0dde4cef1098b573df998f1` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `bd1129ac846bb35eac6e155aee949cd74107b4583105f0d5a376456719f6072e` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `1d687664e37032f0a099abef6e4db0e83df5ea37d490d1ad026a92111a70e663` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `3cd9f28d0483090d6558e24ce7f50fc0d0dbdb2299ad4d0b3ff51d0a035cfe39` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `4327168a3dc9d79391237b20af8d8ac48d4c11b50803a129a8b6534187026366` |
| `prelude` | `library/prelude/prelude.md` | `699f06e8ce8a367b108f08d51060d01b41e69318a867f2eb15ce655735ce9c41` |
| `current_decisions` | `decisions/language/current-decisions.json` | `6a27668bc67646a8b06fd86881889acc3bbdb395ccfafb68cfb55d39378a420f` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `1f2a54974cafe8c62b81f843af0a7c420da23d6f8fbd588fc1559e06cf30541f` |
