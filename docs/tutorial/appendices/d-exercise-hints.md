# 부록 D — 연습 문제를 푸는 방법과 힌트

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 힌트는 학습용이며 test 또는 product execution PASS가 아니다. 실행
> 검증 상태는 `NOT_RUN`이다.

## 1. 세 단계 연습의 목적

- **따라 하기**는 syntax와 evaluation trace를 손으로 재현한다.
- **빈칸 완성**은 이미 주어진 invariant를 보존하며 작은 결정을 한다.
- **직접 설계**는 signature, failure, ownership, status를 스스로
  명시한다.

정답 코드 한 줄보다 “왜 그 책임이 그 경계에 있는가”를 설명하는 것이
중요하다.

## 2. 공통 풀이 순서

1. 입력과 기대 결과를 값이 아니라 type까지 적는다.
2. Current/Preview/Recovery 상태를 표시한다.
3. owner와 mutable place를 표시한다.
4. throws/effect/cancellation을 signature에 쓴다.
5. pattern이면 test와 binding commit을 분리한다.
6. index는 1-based 경계표를 만든다.
7. 마지막에 HIR/MIR까지 보존해야 할 observation을 한 줄로 적는다.

## 3. Part별 핵심 힌트

### Part 01–03

`let`과 `var`를 단순히 “상수/변수”라고 외우지 말고 이후 narrowing
증거가 유지되는 place인지 생각한다. 함수 call은 value/context/witness
channel을 위치 인자 하나로 합치지 않는다. trailing closure의 owner와
message selector가 ordinary call과 같은지 먼저 확인한다.

### Part 04–06

Union, refinement, Enum, Trait witness의 identity를 표의 별도 열에 둔다.
`def#guard` 이름만으로 narrowing한다고 가정하지 않는다. 검증된
`GuardSummaryV1`, direct truth-test와 stable actual을 확인한다.
conformance 문제는 DIRECT exact witness부터 찾고, inactive `AUTO`나
successor `VIA`를 끌어오지 않는다.

### Part 07–09

owner timeline을 “평가 전 → commit 전 → commit 후 → cleanup”으로
그린다. error와 defect, failure와 cancellation을 같은 화살표로 그리지
않는다. `finally` 또는 `defer`가 성공 경로에만 실행된다고 가정하지
않는다.

### Part 10–12

actor는 thread가 아니라 isolated state owner와 mailbox identity로
생각한다. Preview Design 과제는 구현 코드를 완성하는 문제가 아니라
activation prerequisite와 반례를 찾는 문제다.

## 4. 예상 결과를 쓰는 형식

실제 compiler가 없는 현재 단계에서는 다음과 같이 쓴다.

```text
design-static expectation:
  admission: ACCEPT | REJECT | GATED
  type: ...
  effect/error: ...
  ownership: ...
  observation order: ...
  product execution: NOT_RUN
```

“출력은 반드시 42”라고만 쓰지 말고 어떤 정본 규칙에서 나온
기대인지 연결한다.

## 5. 막혔을 때 확인할 자료

1. 현재 장의 빠른 복습
2. [문법 빠른 찾기](a-syntax-quick-reference.md)
3. [진단 안내](c-diagnostics-guide.md)
4. [문법 명세 및 언어 참조서](../../grammar-reference/README.md)
5. exact contract/registry/schema

## 6. 자기 검토 질문

- syntax를 발명하지 않았는가?
- Current와 Preview를 한 코드 블록에 섞지 않았는가?
- failure를 sentinel 값으로 숨기지 않았는가?
- borrow를 escape나 suspension 너머로 보냈는가?
- source order와 tie rule을 우연에 맡겼는가?
- product `NOT_RUN`을 PASS로 바꾸지 않았는가?
