<!-- tools/generators/generate_grammar_reference.py가 생성함; 직접 수정하지 마십시오. -->
# 부록 F — 커버리지 보고서

- 리비전: `r51f3-current-numeric-guard-call-enum-coherence-r1`
- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`
- 의미론 권위: `false`
- 제품 지원: `NOT_RUN`

## 커버리지

| 도메인 | 목표 | 관측 | 결과 |
|---|---:|---:|---|
| `grammar_productions` | 578 | 578 | `통과` |
| `features` | 705 | 705 | `통과` |
| `diagnostics` | 1367 | 1367 | `통과` |
| `predicates` | 255 | 255 | `통과` |
| `prelude_entries` | 65 | 65 | `통과` |
| `examples` | 715 | 715 | `통과` |
| `hard_keywords` | 30 | 30 | `통과` |
| `contextual_words` | 101 | 101 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 91 |
| `STABLE` | 459 |
| `PREVIEW` | 13 |
| `RECOVERY` | 15 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `5b006e47b3c1b51cc82a818e1d31cf3f6e049a71eb8c29e817d0dc888ea4353e` |
| `exact_grammar` | `spec/grammar/deeplus.ebnf` | `40ae31b95cc8b34e1dee61ef66e8c42aacd87ff2902c30db445a5eff68cd93a3` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `4ab834629d519913fef68ba3489fc81942d9661c46bdb8735f8439863eb42cbb` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `4904018c4d0008b65b2f06ab160ff019af0db7c38d2ff05c5467fbdd9064b522` |
| `type_system` | `spec/types/type-system.md` | `a3126f322dfb337ca84ab02e124dba2ea76f2ce573f78d0ea71a3622e470fed7` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `830c17a2ef30f77f78114dda445e451ab76625f02110d3d5dd15ea6e37fb5ad5` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `d6caf43083136671c9af8d29393d8b2fdd079f69a640f8b21a57394e35c337d7` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `4335ad4e209d46b2279531a79e7dbbe2dac260418d566a8b0408a76db06f0b34` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `d6ad1c9c5ed48d63d88baac85e9619b53377e9a3d5e4154ddb34c81c1725d48e` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `afc16fbce335f73d772809f3b8e0e5f769a41bebf48a401f7de469f28502bf43` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `7087ef404dbb9bb68df446741e7228a2b80493cb1dfeb376f7478aed642a7a3a` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `ceac6b52a7f8c0ff14908853fa628e26383d5fbe26b7565e6d96365983224eab` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `760a5318168fa550f5412cd35b33a0d7c9626815f6d703d6ba116deedf28ac9f` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `8d037139154362491f60a4ece5c476a64883b00e1e49189405f8b7954bafe81f` |
| `prelude` | `library/prelude/prelude.md` | `7544f97a440e8caa7a74d9698259d7136219c2d5c7e4249ec603bf7cb322ce59` |
| `current_decisions` | `decisions/language/current-decisions.json` | `71b89fa43132f7f0ec4316fad670992c4e2a2a0750d8734366e0a8c698070c4c` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `fad781ceb2f840aa0576902f1feeb1d4d3e4a8bccb688549197f67d99c8f30df` |
