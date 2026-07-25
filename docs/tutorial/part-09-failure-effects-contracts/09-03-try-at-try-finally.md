# 09-03 — statement `try`, value `@try`, `catch`와 `finally`

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

`try`의 정적 join과 cleanup 순서를 설명한다. backend 실행 증거는 없다.

## 2. 학습 목표

- statement `try`와 value `@try`를 구분한다.
- catch pattern의 irrefutability 조건을 이해한다.
- finally가 값을 만들지 않는다는 법칙을 적용한다.
- body failure와 cleanup failure의 우선순위를 추적한다.

## 3. 선수 지식

ErrorSet, pattern transaction, branch type join, `return`과 `ret`를 알아야
한다.

## 4. 문제에서 출발하기

실패를 처리한 뒤 계속 실행하려는 문장과, 성공·회복 경로에서 하나의
값을 만들려는 식은 서로 다른 owner가 필요하다. 하나의 애매한 `try`가
둘 다 맡으면 암시적 반환과 branch join이 불명확해진다.

## 5. 핵심 모델

```text
try { statements } catch pattern { statements } finally { cleanup }
@try { value } catch pattern { value } finally { cleanup }
```

statement `try`는 적어도 하나의 catch 또는 finally가 있어야 한다.
`@try`의 모든 정상 경로는 compatible value type으로 join되어야 하며,
finally는 그 값에 참여하지 않는다. 처리되지 않은 Error는 finally 뒤
전파된다.

## 6. 단계별 예제

statement `try`는 side effect와 control flow를 소유한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
try {
    importBatch(batch)
} catch error {
    recordFailure(error)
} finally {
    releaseBatch(batch)
}
```

값을 만드는 경우에는 `@try`를 명시한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let profile = @try {
    loadProfile(id)
} catch error {
    defaultProfile(error)
} finally {
    releaseRequest(id)
}
```

각 ValueBody는 하나의 값으로 끝나고 `finally`는 cleanup만 수행한다.

## 7. 허용·거부·경계 사례

허용: catch 없이 finally만 소유한 statement try.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
try {
    perform()
} finally {
    close()
}
```

거부: handler와 finally가 모두 없는 bare try.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
try {
    perform()
}
// BARE_TRY_WITHOUT_HANDLER_OR_FINALLY_NOT_CURRENT 계열
```

catch header는 binder, wildcard, 또는 남은 ErrorSet에서 checker가
irrefutable하다고 증명한 transactional Pattern이어야 한다. 일부 variant만
시험하고 실패하면 다음 catch로 넘기는 runtime dispatch는 현행이 아니다.
Defect와 Cancellation도 catch residual에 들어오지 않는다.

body와 cleanup/finally가 함께 실패할 때의 정본 순서는 다음 네 행으로
추적한다. “suppressed”는 실패를 지운다는 뜻이 아니라 primary 뒤에
관찰 가능한 순서로 보존한다는 뜻이다.

| body 결과 | cleanup/finally 결과 | primary | suppressed |
|---|---|---|---|
| 성공 | 모두 성공 | 없음, 정상 값 또는 정상 제어 유지 | 없음 |
| 실패 | 모두 성공 | body failure | 없음 |
| 성공 | 하나 이상 실패 | 실제 cleanup 순서의 첫 failure | 나머지 cleanup failure를 실제 실행 순서로 |
| 실패 | 하나 이상 실패 | body failure | cleanup/finally failure를 실제 실행 순서로 |

다음 미니 사례에서는 `importBatch`가 `ImportError`로 실패한 뒤
`releaseBatch`도 `ReleaseError`로 실패한다고 가정한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
try {
    importBatch(batch)
} finally {
    releaseBatch(batch)
}
```

관찰 결과의 primary는 `ImportError`이고 `ReleaseError`는 첫 suppressed
failure다. 반대로 body가 성공하고 release만 실패하면 `ReleaseError`가
primary가 된다. `@try`에서도 계산된 성공값이 cleanup failure를
덮어쓰지 않는다.

## 8. 다른 기능과의 연결

- `@try`는 `@if`, `@match`와 같은 value-control family다.
- catch pattern binding은 성공할 때만 atomic commit된다.
- `defer`는 lexical cleanup region에 등록되고 finally와 함께 LIFO/owner
  법칙을 만족해야 한다.
- async suspension과 Cancellation도 finally/defer를 건너뛰지 않는다.

### 판정 추적

먼저 statement/value owner를 고르고, body에서 남는 ErrorSet을 계산한
다음 각 catch pattern의 irrefutability와 residual 제거를 확인한다.
정상 경로라면 `@try` value join을 계산하고, 그 뒤에 finally와 lexical
cleanup event를 실제 실행 순서로 붙인다. 마지막으로 위 표에 따라
primary와 suppressed 배열을 만든다. scheduler 완료 시점이나 source에
먼저 적힌 cleanup 이름으로 순서를 다시 정하지 않는다.

### 흔한 오해

`finally`가 마지막에 있으니 항상 그 실패가 primary라고 생각하기 쉽지만
이미 body failure가 있으면 틀리다. 또 catch pattern을 일반 match arm처럼
부분 일치 dispatch에 쓸 수 있다고 오해하기 쉽다. 현행 catch는 남은
ErrorSet을 확실히 받는 header이며, 값 계산은 `@try`의 ValueBody가
소유한다.

## 9. Deeplus다운 작성 관례

값이 필요하면 `@try`, 제어와 side effect가 목적이면 statement `try`를
쓴다. finally에서 성공값을 슬쩍 바꾸지 않는다. recoverable Error를
가장 좁은 owner에서 처리하고, 처리할 수 없으면 signature에 보존한다.

## 10. 연습 문제

1. **따라 하기:** `@try` 두 branch가 모두 `String`을 만드는 예제를
   작성하라.
2. **빈칸 완성:** `try`에 catch가 없을 때 반드시 필요한 절을 채워라.
3. **스스로 설계하기:** resource 획득, parsing, fallback, release가 있는
   workflow를 statement와 value control 중 어디에 둘지 설명하라.

## 11. 빠른 복습

- `try`는 statement, `@try`는 value expression이다.
- bare statement try는 현행이 아니다.
- finally는 값을 만들지 않고 처리되지 않은 Error 뒤에도 실행된다.
- Defect와 Cancellation은 catch 대상이 아니다.

## 12. 정본 근거와 다음 장

- [try 정확 문법](../../../spec/grammar/deeplus.ebnf)
- [제어와 cleanup 참조](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [평가·MIR](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음 장은 실행되는 callable 계약과 실행되지 않는 선언적 law metadata를
분리한다.
