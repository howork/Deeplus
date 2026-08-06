<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-implementation-readiness-g4-audit-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 656 | 656 | `통과` |
| `features` | 723 | 723 | `통과` |
| `diagnostics` | 1486 | 1486 | `통과` |
| `predicates` | 283 | 283 | `통과` |
| `prelude_entries` | 81 | 81 | `통과` |
| `examples` | 763 | 763 | `통과` |
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
| `human_language` | `spec/language.md` | `d0ad95a0ec72a626f06e9a1138b8f9a736de5b16a096d4b4a6512e5d8049b620` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `914399e4fd35f552cab3111613244cb6844b6313f8b9bd17ebbead0ad7df9bd9` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `a51660b756a44b45e118ed0526000a7b8be011545663e9160cab36e7d38b1abc` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `daf3d867bfb4979771afd5ea4795324664d343f26b5fe3fb4646abd06c5c2fda` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `2187c63e9b41aaa64a029292a683c3e72182e1a75fb966074242357a756e7ebe` |
| `type_system` | `spec/types/type-system.md` | `7f4c5e94ae00cbe7fc5c2da0c2b7cdec2d1be58782452cbbca3eaf1ecc6730a9` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `2a4ed9d732cfb25e4c97816f72010a6c34fb6fc5aa82e40b6bd40681ca3d667f` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `45fd39519a3b88f6ff5182c368f4cee760febe4414e4a2d52cdc75f59f69ef84` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `d085b7a1965f037698578c4447685c1f3804ece00d933401cd2066b32a13b976` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `355c295018e32054e08082b07494efdd0d7f282a2df3ddc923d4ad2cb3a9f7c3` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `a6094a7c9862e764b13aa935804b086a5d3a7e9ebf087b3b5506ed84c3e4a899` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `b6f2763556c02feafcb415130b0567a315b38c9321bb48d81f776ec71cecd7be` |
| `current_decisions` | `decisions/language/current-decisions.json` | `52d0fe4ec14af39282ec2f739e0d0869e90056279325341ba543a6f927af186d` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `28e81c95a4e02a6472f313a5854ac85457ae7eeb7c5ab26c26d3b624df85e2a5` |
