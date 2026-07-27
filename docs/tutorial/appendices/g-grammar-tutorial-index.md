# 부록 G — 문법 명세와 튜토리얼 교차 색인

> 상태: `MIXED_STATUS`
>
> 이 표는 탐색 도구다. semantic authority는 문법·contract·registry에
> 있고 product 상태는 `15/15 NOT_RUN`이다.

## 1. 주제별 연결

| 주제 | 튜토리얼 | 문법/언어 참조 |
|---|---|---|
| 상태와 authority | [01-01](../part-01-orientation/01-01-language-status.md) | [00](../../grammar-reference/00-status-authority-and-notation.md) |
| lexical/literal | [Part 02](../part-02-values/README.md) | [01](../../grammar-reference/01-lexical-structure.md) |
| Package/Module/import | [01-04](../part-01-orientation/01-04-package-module-source.md), [11-01](../part-11-modules-system/11-01-package-module-import-visibility.md) | [02](../../grammar-reference/02-programs-modules-and-imports.md) |
| binding/name | [01-05](../part-01-orientation/01-05-names-bindings-blocks.md) | [03](../../grammar-reference/03-declarations-bindings-and-names.md) |
| type/refinement | [Part 04](../part-04-type-system/README.md) | [04](../../grammar-reference/04-types-generics-and-refinement.md) |
| callable | [Part 03](../part-03-flow-callables/README.md) | [05](../../grammar-reference/05-functions-methods-closures-and-calls.md) |
| Class/Trait | [Part 06](../part-06-traits/README.md) | [06](../../grammar-reference/06-classes-traits-conformance-and-extensions.md) |
| Enum/Record/Schema | [Part 05](../part-05-data-modeling/README.md) | [07](../../grammar-reference/07-enums-records-schemas-bitfields-and-units.md) |
| expression/operator | [02-04](../part-02-values/02-04-operators-power-boolean.md) | [08](../../grammar-reference/08-expressions-and-operators.md) |
| collection/index/slice | [Part 08](../part-08-collections-math/README.md) | [09](../../grammar-reference/09-collections-indexing-and-slicing.md) |
| pattern/match | [05-04](../part-05-data-modeling/05-04-patterns-destructuring.md) | [10](../../grammar-reference/10-patterns-destructuring-and-matching.md) |
| flow/error/effect | [Part 09](../part-09-failure-effects-contracts/README.md) | [11](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md) |
| ownership | [Part 07](../part-07-ownership/README.md) | [12](../../grammar-reference/12-ownership-borrowing-and-responsibility.md) |
| async/actor | [Part 10](../part-10-concurrency/README.md) | [13](../../grammar-reference/13-async-tasks-actors-and-concurrency.md) |
| FFI/unsafe | [11-04](../part-11-modules-system/11-04-ffi-unsafe-quarantine.md) | [14](../../grammar-reference/14-ffi-unsafe-metaprogramming-and-profiles.md) |
| Preview/Recovery | [Part 12](../part-12-preview-evolution/README.md) | [15](../../grammar-reference/15-preview-recovery-and-removed-surfaces.md) |
| resolution/inference | [04-03](../part-04-type-system/04-03-narrowing-stable-place.md) | [17](../../grammar-reference/17-name-resolution-type-inference-and-calls.md) |
| HIR/MIR/backend | [11-05](../part-11-modules-system/11-05-hir-mir-backends-tooling.md) | [18](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md) |
| Prelude/provider | [11-03](../part-11-modules-system/11-03-prelude-provider-console-adapter.md) | [19](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md) |
| Preview gated | [12-02](../part-12-preview-evolution/12-02-preview-gated.md) | [20](../../grammar-reference/20-preview-gated-reference.md) |
| Preview Design 타입 | [12-03](../part-12-preview-evolution/12-03-preview-design-types-traits.md) | [21](../../grammar-reference/21-preview-design-types-objects-and-traits.md) |
| Preview Design 컬렉션 | [12-04](../part-12-preview-evolution/12-04-preview-design-collections-control.md) | [22](../../grammar-reference/22-preview-design-collections-context-and-control.md) |
| Preview Design runtime | [12-05](../part-12-preview-evolution/12-05-preview-design-concurrency-runtime.md) | [23](../../grammar-reference/23-preview-design-concurrency-ffi-and-runtime.md) |

## 2. 어떤 문서를 먼저 볼까

- 개념을 처음 배우면 튜토리얼을 먼저 읽는다.
- exact syntax, static rule, diagnostic family가 필요하면 문법 참조로
  이동한다.
- 기계 검증이나 authority identity가 필요하면 참조서의 source link를
  따라 contract·registry·schema를 읽는다.
- Preview를 채택할지 검토할 때는 Tutorial 예제만으로 결정하지 않고
  activation prerequisite와 OPEN P1을 확인한다.

## 3. 누락을 발견했을 때

튜토리얼과 문법 참조가 다르면 곧바로 한쪽을 맞추지 않는다.

1. current pointer와 source revision을 확인한다.
2. exact semantic authority를 찾는다.
3. 문서 projection만 stale인지, 실제 contract gap인지 분리한다.
4. actual source delta가 필요하면 diagnostic, grammar, type, HIR/MIR,
   example, validation까지 같은 변경 집합으로 결합한다.
5. product PASS는 실제 target-bound execution receipt가 있을 때만
   바꾼다.

## 4. coverage 자료

`docs/tutorial/coverage-manifest.json`은 이 목차의 파일, byte hash,
한국어 설명량, Deeplus 코드 블록, 연습 표식을 기계적으로 결합한다.
이는 교육 문서의 completeness 증거이지 semantic conformance나 product
support 증거가 아니다.

## 5. 학습 질문에서 정본까지 가는 예

“왜 첫 원소가 `items[1]`인가?”라는 질문은 먼저 Part 08의 직관과
경계 예제로 답한다. 정확한 index production과 owner별 logical domain은
문법 참조 09장을 보고, built-in owner와 `Indexable`의 차이는 Prelude
signature와 indexing coherence contract에서 확인한다. 마지막으로
fixture catalog는 accept/reject row를 제공하지만 실제 backend 실행
PASS를 대신하지 않는다.

“왜 이 `def#guard` 호출은 type을 좁히고 저 호출은 그렇지 않은가?”라는
질문은 Part 04와 09의 flow 설명을 읽고, 문법 참조 04장의 summary,
direct truth-test, usable-place/Phi 규칙을 확인한다. 이 순서가
튜토리얼 → 참조서 → exact authority → fixture의 일반 탐색 경로다.

## 6. 색인 유지 원칙

새 장을 추가할 때는 비슷한 제목만 연결하지 말고 그 장이 실제로
설명하는 semantic owner를 확인한다. Preview Design 링크에는 상태를
숨기지 않고, Recovery 링크는 positive 예제로 사용하지 않는다. 링크
target이 존재하는지만 검사한 결과를 의미 completeness로 해석하지
않는다.
