<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-callable-responsibility-static-lexical-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 579 | 579 | `통과` |
| `features` | 708 | 708 | `통과` |
| `diagnostics` | 1395 | 1395 | `통과` |
| `predicates` | 258 | 258 | `통과` |
| `prelude_entries` | 65 | 65 | `통과` |
| `examples` | 723 | 723 | `통과` |
| `hard_keywords` | 30 | 30 | `통과` |
| `contextual_words` | 101 | 101 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 458 |
| `PREVIEW` | 13 |
| `RECOVERY` | 17 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `29dc6cba2ef1ceb2f416e4b2d45dcd4944e36f10df500997c4d5247399b65b6d` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `171f94a3352af971e56f606f0b59aaf80a55cfea93df4d87adf583cf0497cf4b` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `4ab834629d519913fef68ba3489fc81942d9661c46bdb8735f8439863eb42cbb` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `2a61c0992d16b25d2c5359abae7db3588d0fa98fd54dcd568796d0d80770e56c` |
| `type_system` | `spec/types/type-system.md` | `f558775fee8bda0c3ee1d17f808251e8e4da9952dc2e02a5d657b50d4fb28963` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `1d8db61d790580a4c8c508b857f44f5ab491fa99c1d18b8c99300d13865bacb2` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `5077822d4cab6be56826ce1be7198593c3b420c214cde7bb16a820c5196c89c0` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `1c178e2765e52ca7c436786867e311bb4dd4285bf431f92b84410539173382af` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `d6ad1c9c5ed48d63d88baac85e9619b53377e9a3d5e4154ddb34c81c1725d48e` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `afc16fbce335f73d772809f3b8e0e5f769a41bebf48a401f7de469f28502bf43` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `e181c9309a2a43fbe49dca29f69f23aeb4c514d209ad93f7cf0e7e237f8a1caa` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `5e55393e40b10a69abfcb9e2bb82229653a94f46022c9724e4802cd079f632d4` |
| `prelude` | `library/prelude/prelude.md` | `7544f97a440e8caa7a74d9698259d7136219c2d5c7e4249ec603bf7cb322ce59` |
| `current_decisions` | `decisions/language/current-decisions.json` | `4abbdf5b12a208283d51dff4aa7ba0506192b67d1582e37482f35298118efec4` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `f7214f2a4eb16a3fc9d08b051f94c47c1f212775c2a71ac347b69c54f61fb1c2` |
