<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-global-implementation-target-trace-closure-r76-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 644 | 644 | `통과` |
| `features` | 723 | 723 | `통과` |
| `diagnostics` | 1484 | 1484 | `통과` |
| `predicates` | 283 | 283 | `통과` |
| `prelude_entries` | 77 | 77 | `통과` |
| `examples` | 752 | 752 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 105 | 105 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 540 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `4280ee36b20a4c9a6c95a6dc58e75d6be52822e7be84a918b58e79d1399aeeb6` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `303e90004386609777013bb6f15d139277e39ab0bf71301ace990a1f0092fb2a` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `cfb11253ff4b67122bfa25786a05c4598da71ce682ed8de822a9a092d6f7cc35` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `0744e9353a24a016c279ceb91c3585cf5094608e59f676515b7e254f4223f03c` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `40b27fc2c3064fe59c7b2df42b549eeb658f4ca1783269a650c0299d98be85f9` |
| `type_system` | `spec/types/type-system.md` | `b54ddb02abee8aa5cb47129df5b2a8551d274f59a91f7b495fabddbcc376a8d8` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `2e0a04915416df6137065d8a8cda4758b593bf5ff853428e3dc166b767b34bbe` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `92fd16dc3bc87f43521e6066159015adcde128300dfe9f1bab866a4d04401370` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `35c20cccef65dcb19c0477b4470a11c8f97a08f8a0dde4cef1098b573df998f1` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `355c295018e32054e08082b07494efdd0d7f282a2df3ddc923d4ad2cb3a9f7c3` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `3cd9f28d0483090d6558e24ce7f50fc0d0dbdb2299ad4d0b3ff51d0a035cfe39` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `94175d3dd153cb9759cb6b3f4f1d858f8defbab82b5c1431bb57f2d771cf8673` |
| `current_decisions` | `decisions/language/current-decisions.json` | `010688423f182d3a7f7d7778accfca54a0acba629d0b76437b980c24e66b640b` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `076b0a89a0720e5afb811dac319a31004ab53dae66ce0e0393ad29a96a5fd2d6` |
