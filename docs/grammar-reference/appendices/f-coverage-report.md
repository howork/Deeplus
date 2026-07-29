<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-trait-operator-refinement-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 637 | 637 | `통과` |
| `features` | 719 | 719 | `통과` |
| `diagnostics` | 1424 | 1424 | `통과` |
| `predicates` | 268 | 268 | `통과` |
| `prelude_entries` | 71 | 71 | `통과` |
| `examples` | 733 | 733 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 106 | 106 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 533 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `01e34a201c43ba12a0725ed2bf3bef402736d138602787a01f6bdf9817724487` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `1e8b7e307763f73e566b160fc918dac18869ba958b3744c7c4e1e6abd90dfdc2` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `d9da69ecaf1f2be6e2497bf93c00cc39f4f47b1ebe5252fc5a65d4751a39831d` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `3410b4c81e9dcee5ac7e987c2e642921d155fa5c6f0b3ebb41eb3f5c70a4b149` |
| `type_system` | `spec/types/type-system.md` | `801777608e3d5ddd78acbc5a051ca84723c119ada6d7712415ddffe39991633e` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `206958e0b341937b4dd13be581b5cc6e4b5605e99da1937e1579ae9df9e62bbe` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `3735e8031e4b71950ec2832f05cec1777a816608cd4fab699a6bf2adf36e42b1` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `8280bbd6eb161099fc3ce802dd35ad1e69f813f0dabe6b822f98f392674f787d` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `d6ad1c9c5ed48d63d88baac85e9619b53377e9a3d5e4154ddb34c81c1725d48e` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `afc16fbce335f73d772809f3b8e0e5f769a41bebf48a401f7de469f28502bf43` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `3cd9f28d0483090d6558e24ce7f50fc0d0dbdb2299ad4d0b3ff51d0a035cfe39` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `4327168a3dc9d79391237b20af8d8ac48d4c11b50803a129a8b6534187026366` |
| `prelude` | `library/prelude/prelude.md` | `873128763921aff97cc35fe0b7fa6cac80463fea3254ed6393930354d27f517b` |
| `current_decisions` | `decisions/language/current-decisions.json` | `b0f3737a2ff4e9742b4ecc62ca25b3ebf2e3edab0cec5b87a206836f5892ab12` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `0839eb4a078f78729a32f0a9c8a412c10c40865ecef6d856c8f9989367645fa4` |
