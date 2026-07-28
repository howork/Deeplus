<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-trait-operator-refinement-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 635 | 635 | `통과` |
| `features` | 719 | 719 | `통과` |
| `diagnostics` | 1423 | 1423 | `통과` |
| `predicates` | 268 | 268 | `통과` |
| `prelude_entries` | 71 | 71 | `통과` |
| `examples` | 733 | 733 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 106 | 106 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 531 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `6aab0b617278d1f22556a1cd3951aae4f64ca238a61f581f29e922c116a0109c` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `226c5bff9d35aa8e6d4b678f7d3545980b1047e6d1e7f6b5f7941039ce4dac85` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `0b7f25305e0843a161642f9dbc37d387bfb96cb8c56e8d6e70a2351cb2bb8e53` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `d10c86e03bef92e2edfc6e04dff5cf94fb2ce0d971253114f74f2d6f85bbdc74` |
| `type_system` | `spec/types/type-system.md` | `f9a2b130c3d5bfa8989a5a0029a3edcfb76c16b05718b61aaa96db63c3954916` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `206958e0b341937b4dd13be581b5cc6e4b5605e99da1937e1579ae9df9e62bbe` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `fa4744e2272dc4ad80fd941150174d72157aa0deb1c9010d4c8e0e57dfb89f6f` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `8280bbd6eb161099fc3ce802dd35ad1e69f813f0dabe6b822f98f392674f787d` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `d6ad1c9c5ed48d63d88baac85e9619b53377e9a3d5e4154ddb34c81c1725d48e` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `afc16fbce335f73d772809f3b8e0e5f769a41bebf48a401f7de469f28502bf43` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `3cd9f28d0483090d6558e24ce7f50fc0d0dbdb2299ad4d0b3ff51d0a035cfe39` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `4327168a3dc9d79391237b20af8d8ac48d4c11b50803a129a8b6534187026366` |
| `prelude` | `library/prelude/prelude.md` | `e5535d68ef27f5e60ec6b9eb92d55a5667e763c9e95be248f8da8507eb2ad8fc` |
| `current_decisions` | `decisions/language/current-decisions.json` | `c87ff71579704950554891f03c81017fa2a0acede43504a7ade8023e2c7a08f1` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `4c3bde3b499381cdee6731f63edd8104dc9b7b9584efe5e2169139533671da1f` |
