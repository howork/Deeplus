# 4부. 타입 시스템과 흐름 증명

이 부에서는 지역 추론에서 시작해 refinement, closed Union과
intersection, Option/Result, stable-place narrowing, generic 제약과
callable responsibility까지 다룬다. Deeplus 타입 시스템은 단순히 값의
“모양”만 표시하지 않는다. ownership, error/effect, cancellation, call
channel과 증명 가능한 흐름 사실을 서로 다른 identity로 보존한다.

> **부 상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 실행:** `15/15 NOT_RUN`

## 학습 경로

1. [추론, alias와 refinement](04-01-inference-aliases-refinement.md)
2. [Union, intersection, Option과 Result](04-02-union-intersection-option-result.md)
3. [narrowing과 stable place](04-03-narrowing-stable-place.md)
4. [generic, variance와 `where`](04-04-generics-variance-where.md)
5. [callable identity, effect와 cancellation](04-05-callable-identity-effects-cancellation.md)
6. [실습: typed parser와 guard 경계](lab-04-typed-parser-guard.md)

## 이 부의 학습 판정 trace

타입 판단은 spelling에서 곧바로 runtime 검사를 만드는 일이 아니다.
먼저 declared type과 expected type을 정규화하고, explicit conversion
corridor가 필요한지 본다. control-flow edge에서는 declared type과
별도로 proof environment를 갱신하며, mutation이나 escape가 있으면 관련
fact를 제거한다. generic과 function type에서는 Trait obligation,
parameter channel, effect/error/cancellation 책임을 identity에 남긴다.
각 예제는 “선언 타입, 현재 proof, 수행한 경계, 성공 payload” 네 열로
추적한다.

## 흔한 오해와 미니 사례

`def#guard`라는 이름만으로 어떤 호출도 좁혀진다고 생각하거나,
`A | B`를 compiler가 필요할 때 만드는 동적 묶음으로 보는 것이 흔한
오해다. guard narrowing은 검증된 summary, direct truth-test와 stable
actual을 요구한다. 미니 사례에서 raw `Int`의 branch-local fact와
checked `Port` success payload를 비교한다. 두 경계는 비슷한 조건을
읽더라도 생성하는 정적 증거가 다르다.

## 이 부의 공통 원칙

- 추론은 bidirectional하고 local하며 숨은 generic이나 anonymous Union을
  만들지 않는다.
- refinement 변환은 `as?`, `as!`, `T::check`의 서로 다른 실패 경로를
  보존한다.
- `is`/`!is`는 이미 선언된 closed Union의 exact alternative 검사다.
- flow-proof 환경은 binding의 선언 타입과 별도로 유지된다.
- variance는 현재 허용된 Trait type parameter에서만 사용한다.
- Option, Result, thrown ErrorSet, Defect와 Cancellation을 합치지 않는다.
- 함수 타입은 value/context/witness/rest channel, ownership, effect/error,
  cancellation과 반환 책임을 함께 보존한다.

## 정본 안내

- [타입·generic·refinement](../../grammar-reference/04-types-generics-and-refinement.md)
- [이름 해석·타입 추론·호출](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [타입 시스템 정본](../../../spec/types/type-system.md)
- [refinement/narrowing 계약](../../../spec/contracts/type-refinement-narrowing-coherence.json)
