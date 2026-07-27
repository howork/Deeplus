# 3부. 흐름 제어와 호출 가능한 값

이 부에서는 값을 계산하는 작은 함수에서 시작해, Deeplus의 호출 모양,
메시지 호출, 패턴 기반 제어 흐름, 명시적 capture와 함수별 정적
activation까지 단계적으로 확장한다.

> **부 상태:** `MIXED_STATUS`  
> **제품 실행:** `15/15 NOT_RUN`

여기서 설명하는 문법과 정적 계약은 현행 설계 정본을 따른다. 예제는
설계 수준의 설명용이며 compiler/runtime 제품이 통과했다는 뜻이 아니다.
`print`나 `readLine`을 암묵적 Prelude로 가정하지 않고, 가능한 한 순수한
함수와 값으로 흐름을 관찰한다.

## 학습 경로

1. [함수, `return`, 오류와 effect](03-01-functions-return-effects.md)
2. [매개변수, label, rest와 unfold](03-02-parameters-labels-rest-unfold.md)
3. [메서드, 메시지와 trailing closure](03-03-methods-messages-trailing-closures.md)
4. [조건, 반복, `match`와 값 흐름](03-04-control-flow.md)
5. [closure capture와 `static { ... }`](03-05-closures-captures-static.md)
6. [실습: 검증 파이프라인](lab-03-validation-pipeline.md)

## 이 부의 학습 판정 trace

호출 가능한 값을 읽을 때는 declaration profile, call shape, argument
evaluation, body control, return/error/effect의 순서로 본다. label과 rest
channel은 어느 formal에 값이 결합되는지를 정하고, source order는 그
값이 언제 한 번 평가되는지를 정한다. closure를 밖으로 빼는 trailing
표면도 이 책임을 줄이지 않는다. 각 장에서는 “무엇이 호출되는가”와
“어떤 값을 어떤 순서로 준비하는가”를 별도 표로 적는다.

## 흔한 오해와 미니 사례

메시지 `worker ~ run job`을 괄호 없는 일반 함수 호출로 읽거나,
`def#pure`를 body 검사와 무관한 장식으로 보는 것이 대표적인 오해다.
미니 사례에서는 같은 두 값을 ordinary argument 둘과 message의 Tuple
argument 하나로 각각 표현해 AST 경계를 말로 설명한다. 또한 closure capture와
`static { ... }`을 “함수가 기억하는 값”이라는 한 개념으로 합치지 않는다.

## 이 부에서 지킬 경계

- 이름 있는 non-`Unit` 함수의 정상 경로는 `return`으로 값을 돌려준다.
- lambda와 값 arm의 block-local 결과에는 `ret`를 사용한다.
- label은 문자열이 아니라 call-shape의 정적 identity다.
- 일반 호출 `f(...)`와 메시지 호출 `receiver ~ selector payload`를
  하나의 문법으로 섞지 않는다.
- 여러 trailing closure에는 모두 서로 다른 label을 쓴다.
- capture는 명시적으로 적으며 ownership/effect/error 검사를 우회하지
  않는다.
- `static { ... }`은 허용된 이름 있는 동기 함수의 activation prologue일
  뿐, 전역 변수나 type-side member가 아니다.

## 정본 안내

- [함수·메서드·closure·호출](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [제어·오류·effect·cleanup](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [이름 해석·추론·호출 선택](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [호출 가능 요소 정합성 계약](../../../spec/contracts/type-flow-callable-coherence.json)
