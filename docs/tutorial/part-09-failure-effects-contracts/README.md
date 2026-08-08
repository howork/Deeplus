# Part 09 — 실패, 효과, 계약과 진단

> 상태: `MIXED_STATUS`
>
> 기본 학습면은 `CURRENT_DESIGN_PRODUCT_NOT_RUN`이다. Preview 표면은
> activation 상태를 별도로 표시한다. 모든 제품 레인은
> `15/15 NOT_RUN`이다.

실패를 모두 “예외”라는 한 상자에 넣으면 프로그램의 책임이 흐려진다.
Deeplus는 recoverable `Error`, 값 안의 `Result`, 프로그램 불변식을 깨는
`Defect`, 구조화된 취소인 `Cancellation`을 분리한다. 여기에
`effects`와 명시적 capability, `defer`와 `finally`, 선언적 `law`와
callable 계약이 결합된다.

## 이 Part의 질문

1. 호출자가 회복할 실패와 값으로 다룰 실패를 어떻게 구분하는가?
2. `throws`, `effects`, `Result`는 왜 서로 대체 관계가 아닌가?
3. `try`와 값 식 `@try`는 어떤 결과와 cleanup을 소유하는가?
4. 계약과 `def#guard`의 검증된 direct-call narrowing은 어떻게 다른가?
5. parser가 잘못된 입력을 진단할 수 있다는 사실이 왜 기능 활성화를
   뜻하지 않는가?

## 학습 순서

1. [Error와 Defect](09-01-errors-defects.md)
2. [effects, throws와 Result](09-02-effects-throws-result.md)
3. [try, @try와 finally](09-03-try-at-try-finally.md)
4. [law, contract, assertion과 def#guard](09-04-law-contract-assert-guard.md)
5. [진단 우선순위와 오류 경계](09-05-diagnostics.md)
6. [실습 — 회복 가능한 import pipeline](lab-09-resilient-import.md)

## 두 개의 기준 예

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def decode(bytes: Bytes) -> Result<Image, error DecodeError>
    throws IOError
    effects io
= {
    return parseImage(bytes)
}
```

`IOError`는 호출 경계의 recoverable error이고 `DecodeError`는 반환값
안에서 분기할 데이터다. 두 channel을 한데 합치지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
def invalid(bytes: Bytes) -> Result<Image, error DecodeError>
    throws DecodeError
= {
    return parseImage(bytes)
}
// 같은 DecodeError family를 Result와 throws에 중복 노출한다.
```

## Part 불변 조건

- `catch`는 `ErrorSet`만 처리하며 Defect와 Cancellation을 삼키지 않는다.
- `defer`는 block이 아니라 정확히 하나의 cleanup invocation을 등록한다.
- cleanup은 정상 반환, Error, Defect, Cancellation에서 건너뛰지 않는다.
- `law`는 실행 함수가 아니라 제한된 pure predicate metadata다.
- `def#guard` direct truth-test는 검증된 `GuardSummaryV1`과 stable actual이
  있을 때만 branch-local narrowing fact를 만든다.
- 설계 정적 예시는 compiler 실행 영수증이 아니다.

## 정본 지도

- [제어 흐름, 오류, 효과, 정리](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [타입 시스템의 효과·오류·취소](../../../spec/types/type-system.md)
- [MIR failure와 cleanup](../../../spec/mir/semantics.md)
- [정확 문법](../../../spec/grammar/deeplus.dpg)
- [진단 색인](../../grammar-reference/appendices/d-diagnostic-predicate-index.md)
