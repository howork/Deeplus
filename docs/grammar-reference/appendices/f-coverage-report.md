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
| `diagnostics` | 1525 | 1525 | `통과` |
| `predicates` | 293 | 293 | `통과` |
| `prelude_entries` | 81 | 81 | `통과` |
| `examples` | 769 | 769 | `통과` |
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
| `human_language` | `spec/language.md` | `073254cae03dc93a8824651b31a85a0306eeac4b2e7921bdc161f69ac49dffb6` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `fefec3a3c8425d4911c8a162fd7f51ee4a63c946f32bcbba0face055a1c9863f` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `91c6fe48284dfdc810a02680ac980bcd1daf4edb19667b0ef8e33dc88bd5b409` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `797c846e71c9f784b214dee1e9c88d3752920b4115302ba6a86d072f00256d84` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `fab0836cca0357142daebdbfe114fc6294fe8f8561a8c0c57c109b20abf70de8` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `b6a82b1acd41af91d2d14329c7faa054b02a66f9e7335e261aa2f1b8e1e1d35a` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `83de3ac03aa0ada2fd23691c58d99f0b78a1e9fcc67b663bd5969905ffcb566a` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `dfed1c57701a47f002fcdd151cebdc7a079a0bd0d69e6b64ed9f13e3d9818bd4` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `dd7d0307bfa29b9b007cbd8e6465744c44521c22153cb1f6606390ac36a782aa` |
| `type_system` | `spec/types/type-system.md` | `1c7428a3d6cd98c3a8021ee32f9149964b86ae6a7ee01138e3d8f8d935c14e75` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `3dfb2d399d6432b6ccec06c6b7992505fe08a317c4b6388b820ff261380f131c` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `f8f6e8e0eb9acdce4a905ac043b8e86ebc6c3f99f379f9e7a166d04e7f83f185` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `4526759326b19d3754997fcf77ca6254f1dd890642d892fb8ba18e5be55616c4` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `5c6ef7686d1abca934c311df34b75138ca3f40bb2a437a8c07f73abb67dc4843` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `6a2f5fe17b427741dbe79694edfe28cc467175ae73ff256b04f2fa1b3563196f` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `5236d0e83e2fddc3e85b98b9ed156ee06606b1735079f7bd9a4ccaabe8d4f27f` |
| `current_decisions` | `decisions/language/current-decisions.json` | `b4a4a051e4ae5b863ab491b7e153b6a3f0825b3e8fd864813cd196d72708ad52` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `d54841f2c6120ee786473b39fd65a73b7d5eec4f0e85b70bec9a8bc6cb8b64b0` |
