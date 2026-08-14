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
| `diagnostics` | 1526 | 1526 | `통과` |
| `predicates` | 293 | 293 | `통과` |
| `prelude_entries` | 81 | 81 | `통과` |
| `examples` | 769 | 769 | `통과` |
| `hard_keywords` | 29 | 29 | `통과` |
| `contextual_words` | 106 | 106 | `통과` |

## 문법 프로파일

| 프로파일 | production 수 |
|---|---:|
| `LEXICAL` | 87 |
| `STABLE` | 556 |
| `PREVIEW` | 13 |

## 결합된 의미론 원천

| 도메인 | 경로 | SHA-256 |
|---|---|---|
| `human_language` | `spec/language.md` | `5ac6541d53617277d1f574c744d9ef26b50a879be7c02fe710e6963b8c4a7975` |
| `exact_grammar` | `spec/grammar/deeplus.dpg` | `b2082354f28bccabe919867e9413cc99ecf664ae4f045c5abba79f24fa92d8c7` |
| `parser_contexts` | `spec/grammar/deeplus.parser-contexts.json` | `c6dc864277f5b02b7a89cc508f55bac23d27f14ee3ed1259052dd2e74b5144a7` |
| `legacy_surface_census` | `spec/grammar/deeplus.ebnf` | `42780c57b387aa1f369cf28591f1007a8819c73da1715d73cf60f434282dabda` |
| `parser_grammar_differential` | `spec/contracts/parser-grammar-differential-r1.json` | `de047ac5b82a785a89d8f400192bed237e9a7baa7b7f7bd38165fbc2a60f211c` |
| `grammar_topology_closure` | `spec/contracts/grammar-topology-closure-r1.json` | `40d9b6196003608c8b2bcba5bdd4e4603d2c542858255d00b4fc5ad20fff1654` |
| `grammar_production_disposition` | `spec/contracts/grammar-production-disposition-registry-r1.json` | `3a9d38ad9eae55562a89ffafe36958ad80eca75c7997ff48fbdf02d47b71bfbb` |
| `keyword_vocabulary` | `spec/grammar/keyword-vocabulary.json` | `feeb593046823ac2c9e7326cbc7789058ea4c99cc28449437cdd53c699b2c2c8` |
| `frontend_admission` | `spec/frontend/frontend-model.json` | `9a3255747e6c219cf7e9d7ea05d28a981329848bc51ee544dc81b9bb1f38d356` |
| `type_system` | `spec/types/type-system.md` | `fdf812422bb25068f84db577647face9837265d16ff4340fce89ff8c491c14ff` |
| `mir_observable_semantics` | `spec/mir/semantics.md` | `3dfb2d399d6432b6ccec06c6b7992505fe08a317c4b6388b820ff261380f131c` |
| `type_flow_callable_coherence` | `spec/contracts/type-flow-callable-coherence.json` | `f8f6e8e0eb9acdce4a905ac043b8e86ebc6c3f99f379f9e7a166d04e7f83f185` |
| `value_operator_indexing_coherence` | `spec/contracts/value-operator-indexing-coherence.json` | `d2dda762d32a007037792a1ab7e68d00baf05244169d0aea24d7faf4db47be46` |
| `actor_concurrency_coherence` | `spec/contracts/actor-concurrency-coherence.json` | `5c6ef7686d1abca934c311df34b75138ca3f40bb2a437a8c07f73abb67dc4843` |
| `shared_state_coherence` | `spec/contracts/shared-state-coherence.json` | `da7e1244ee4bcd24bb81287065d74e0f5cfeb5662650fbc6cf5adae94dfd27d5` |
| `tooling_profiles` | `spec/contracts/tooling-and-profiles.json` | `c145655ee26dfb6916f14e4bd071976974c521be7ce3c59afb214ed0e68f5aff` |
| `provider_derive_via` | `spec/contracts/provider-derive-via.json` | `385b9dc084cd80189a223bdc7d3f5e496de37385cbf52c13ca6a9264166d38d9` |
| `enum_derived_capabilities` | `spec/contracts/enum-derived-capabilities.json` | `6a2f5fe17b427741dbe79694edfe28cc467175ae73ff256b04f2fa1b3563196f` |
| `literal_shaped_collection_design` | `spec/contracts/literal-shaped-collection-design.json` | `a83467df9ae86922569a90388c69c44443c5d2f0142cb9ea32fd2e31c8aafdad` |
| `prelude` | `library/prelude/prelude.md` | `5236d0e83e2fddc3e85b98b9ed156ee06606b1735079f7bd9a4ccaabe8d4f27f` |
| `current_decisions` | `decisions/language/current-decisions.json` | `b4a4a051e4ae5b863ab491b7e153b6a3f0825b3e8fd864813cd196d72708ad52` |
| `coverage_schema` | `schemas/language/grammar-reference-coverage.schema.json` | `55f2f64a3d7df074182dbdfca326846375c0d6659474d07f15ede8b369aff2de` |
