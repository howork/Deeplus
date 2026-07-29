# Part 6 — Trait, 적합성, 정적 capability

> 과정 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> semantic P0: `0` · OPEN feature P1: `22` · product lanes: `15/15 NOT_RUN`

Trait는 “메서드 이름이 우연히 같다”는 관찰이 아니라 명시적 요구사항과
coherent evidence의 계약이다. 이 부에서는 Trait declaration,
conformance, witness call, extension, associated item과 Stable
fixed-glyph conformance를 하나의 흐름으로 배운다.

## 학습 경로

1. [Trait 요구사항](06-01-trait-requirements.md)
2. [Conformance와 witness](06-02-conformance-witness.md)
3. [Extension과 named extension](06-03-extensions-named-extensions.md)
4. [Associated type과 명시적 qualification](06-04-associated-types-qualification.md)
5. [Stable fixed-glyph conformance](06-05-fixed-glyph-conformance.md)
6. [실습: generic renderer](lab-06-generic-renderer.md)

## 이 부의 경계

- subclassing, Trait conformance, extension, containment, dynamic view는
  서로 다른 관계다.
- 현재 conformance surface는
  `type T conforms Trait { ... }`다.
- 현재 route 철자는 소문자 `via`다. successor `VIA`/`AUTO`,
  specialization, child/case-local witness replacement는 활성화하지 않는다.
- associated item은 `<T as Trait>::item`으로 명시한다.
- fixed-glyph conformance의 Stable 집합은 정확히 13개 역할(unary
  `+`/`-`, binary `+`/`-`/`*`/`/`/`%`, equality와 ordering)과 9개
  Prelude Trait root다.
- 임의 custom operator는 Current와 Preview Design 모두에서 수용하지
  않으며 positive 예제가 없다.

Trait Conformance 관련 `TCC-P1-002..008`은 정확히 7개 모두 OPEN이다.
이 튜토리얼은 문서만으로 witness 구현, formatter/LSP 또는 backend
지원 PASS를 주장하지 않는다.

## 이 부를 읽는 관점

각 장에서는 같은 질문을 더 정밀하게 반복한다. 먼저 generic 알고리즘이
요구하는 capability를 Trait requirement로 적는다. 다음으로 target type과
Trait 사이에 explicit conformance가 있는지 확인하고, 그 evidence가
coherence 규칙에서 유일한지 판정한다. 마지막으로 call 또는 associated
projection이 어느 `TraitWitnessId`와 `RequirementId`를 사용하는지
고정한다. runtime에서 이름이 비슷한 method를 다시 찾거나 import order로
승자를 정하지 않는다.

오류도 세 층으로 나눈다. requirement signature 불일치는 계약 문제이고,
같은 ground pair의 복수 evidence는 coherence 문제이며, 선택된 witness
뒤 associated item kind 불일치는 projection 문제다. 셋을 모두 “Trait가
구현되지 않았다”로 표현하면 안전한 수정 방향을 제시하기 어렵다.

이 부의 예제는 design-static evidence다. 실제 witness table,
cross-module linker metadata, formatter·LSP navigation, xVM 또는 Cranelift
dispatch 실행을 뜻하지 않는다. 작은 trace는 향후 receipt가 보존해야
할 identity와 순서를 드러내기 위한 것이다.
