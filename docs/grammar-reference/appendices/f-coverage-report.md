<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-exact-numeric-hir-h1-coherence-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 573 | 573 | `통과` |
| `features` | 694 | 694 | `통과` |
| `diagnostics` | 1341 | 1341 | `통과` |
| `predicates` | 250 | 250 | `통과` |
| `prelude_entries` | 63 | 63 | `통과` |
| `examples` | 716 | 716 | `통과` |
| `hard_keywords` | 30 | 30 | `통과` |
| `contextual_words` | 101 | 101 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 454 |
| `PREVIEW` | 13 |
| `RECOVERY` | 15 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `bbbba13b15912139f7e1150ed4b3084823073c8cfae8397aaec52bb5c55940b0` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `d259fa3ee6b3c7ad03aef75460fccd06bc665dbd166b809446183e7b553aad0f` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `4ab834629d519913fef68ba3489fc81942d9661c46bdb8735f8439863eb42cbb` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `1dbd0bd8a12ed4d67a0aa49e95955131a3b6b5447cdd029fb40c97c38d04cf19` |
| `type_system` | `spec/types/type-system.md` | `ebc8590b3039801b45cdc56ec02750f297b983997a30d2b431f2470d8c47f7a1` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `290032ca480d8f03158b143cc0dad0425676042bbbd638afbb66cd93638c55e9` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `b07b58ae83abf8ef41e8b720630f906f536cfa7029781a76b77a938f6c6a47e7` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `c81ccd9d6ded9a9112698ce3aa2d893e5e8af5e747008ff464e832750019b692` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `f29689886d1fdf1d40c0fb92d698c5782160fe0f36fdbf69904034023679fdbb` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `2776d416f9c4d2e73c974123c04056dc59a58e5865787e9275208b07ad0ce677` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `d47c2860489138095bd93a85c076d3969d30013b9c04d2b3302f45b5bc398f15` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `8656465c6dcbcfb9f3c5e475e0d0ebb19cc36c5412f8bc7bb9c955439ac9f017` |
| `prelude` | `library/prelude/prelude.md` | `d5f2b4389a9076430085ef5b19bb942bb9fedcbd1db67a2b48ee901c89f29124` |
| `current_decisions` | `decisions/language/current-decisions.json` | `b9fc0ff5f84a5688c85a848f0842cffa4eb3f86dd514072640a722778511d23d` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `1c76469b43315f3beba27fe94c1f250ab93a7b289480973ceb3a67a49037bee1` |
