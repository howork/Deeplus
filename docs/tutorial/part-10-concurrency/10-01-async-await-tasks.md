# 10-01 — 이름 있는 `def#async`, `await`와 task

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이름 있는 async 선언은 current design이다. 실제 scheduler, suspend,
resume 및 backend 실행은 확인되지 않았다.

## 2. 학습 목표

- `def#async`와 일반 lambda를 구분한다.
- source에 드러난 `await` 지점을 찾는다.
- task handle의 result/error/cancellation 책임을 읽는다.
- `for await`와 ordinary `for`를 구분한다.

## 3. 선수 지식

함수 profile, ErrorSet, effects, ownership과 cleanup을 알고 있어야 한다.

## 4. 문제에서 출발하기

비동기 함수가 호출 순간에 값 전체를 돌려주지 않는다면, 언제 중단하고
어떤 실패를 보존하는지 보여야 한다. Deeplus는 이름 있는 `def#async`와
명시적 `await`를 사용한다. 일반 closure를 암시적으로 async로 바꾸지
않는다.

## 5. 핵심 모델

`def#async`는 허용된 named callable profile이다. `await`는 expression
prefix owner이며 피연산자가 이미 awaitable이어야 한다. 중단 지점에서도
live owner, borrow region, effect/error row, Cancellation, cleanup obligation이
사라지지 않는다.

`for await`는 `AsyncSequence<T,E>`의 source-ordered next channel을
순회한다. source Error `E`와 Cancellation은 별도 terminal이다.

## 6. 단계별 예제

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async fetch(url: String) -> Bytes
    throws NetworkError
    effects {network}
= {
    return await (client ~ get url)
}
```

`await` 앞에서 URL과 receiver가 한 번 평가되고, resume 뒤에도
`NetworkError`, effect와 cleanup 책임이 보존된다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async sum(source: AsyncSequence<Int, IOError>) -> Int
    throws IOError
= {
    var total = 0
    for await value in source {
        total += value
    }
    return total
}
```

sequence를 미리 List로 만들거나 replay 가능하다고 가정하지 않는다.

## 7. 허용·거부·경계 사례

허용: async owner 안의 명시적 await.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#entry#async launch() -> ExitCode = {
    let status = await loadStatus()
    return ExitCode::success
}
```

거부: Stable script root의 top-level await.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let status = await loadStatus()
// TOP_LEVEL_AWAIT_NOT_CURRENT
```

일반 `{ value => ... }` closure도 expected callable이 있다고 해서 async
callable literal이 되지 않는다. 그 설계는 Preview Design nonactivatable이다.

## 8. 다른 기능과의 연결

- `#async` callable의 ErrorSet과 effect row는 ordinary call compatibility에
  포함된다.
- live `inout` borrow가 await를 건너려면 별도 안전 증명이 필요하다.
- AsyncCollector는 async comprehension을 활성화하지 않는 current stdlib
  profile이다.
- actor handler의 await는 actor turn identity를 유지한다.

### 판정 추적

async 호출을 볼 때는 먼저 selected named callable의 value, ErrorSet,
effect, suspension 책임을 결합한다. 인자와 receiver는 source 순서대로
한 번 평가하고, 반환된 awaitable 책임에 원래 Error와 Cancellation을
남긴다. `await` 지점에서는 live owner와 borrow가 suspension을 건널 수
있는지 검사한 뒤 suspend event를 기록한다. resume 때 다른 overload를
고르거나 error family를 다시 추측하지 않는다.

`for await`도 같은 원칙을 반복한다. source를 한 번 만들고, 각 next
요청의 성공값은 loop binding에 commit하며, source Error와 Cancellation은
서로 다른 terminal로 보존한다. loop가 중간 종료되면 sequence resource의
cleanup owner가 누구인지까지 trace에 남겨야 한다.

### 흔한 오해와 미니 사례

`def#async`를 호출하면 자동으로 새 병렬 child가 생긴다고 생각하기
쉽다. 병렬 child의 lexical owner를 만들려면 `task scope`와 `spawn`이
별도로 보여야 한다. 또한 `await`는 OS thread를 반드시 막는다는 뜻도,
실패를 정상값으로 바꾼다는 뜻도 아니다.

미니 사례에서 `await loadHeader()` 다음에 `await loadBody()`를 쓰면
source 순서의 두 suspension이다. 둘을 동시에 시작하려면 다음 장의
scope에서 두 child를 spawn하고 각각 join해야 한다. 짧은 철자 차이가
실행 순서와 failure owner를 바꾸므로 성능 추측으로 생략하지 않는다.

세 표면의 책임도 나누어 적는다. named async 호출은 선택된 callable과
awaitable 책임을 만들고, `await`는 그 책임의 한 suspension/terminal을
소비하며, `for await`는 source-ordered next를 반복한다. 호출만 했다고
결과값을 이미 얻은 것도 아니고, await했다고 task의 ErrorSet이나
Cancellation이 지워진 것도 아니다.

검토용 미니 trace는 `receiver 평가 → argument 평가 → async 책임 생성
→ await 전 owner 검사 → suspend → value/Error/Cancellation resume →
cleanup` 순서로 쓴다. 각 단계에 동일 receiver와 callable identity가
남는지 확인한다. resume 뒤 dynamic 이름 검색이나 다른 overload 선택이
있다면 HIR-H1에서 닫아야 할 결정을 runtime으로 미룬 것이므로 거부한다.

## 9. Deeplus다운 작성 관례

중단 가능성을 이름과 source 지점에 드러낸다. 비동기 전환을 호출자에게
숨기거나, task failure를 Option으로 지우거나, Cancellation을 Error로
접지 않는다.

## 10. 연습 문제

1. **따라 하기:** `def#async` 함수 안에서 하나의 task를 await하는 코드를
   작성하라.
2. **빈칸 완성:** `AsyncSequence<Item, ___>`의 source failure와
   Cancellation 차이를 채워라.
3. **스스로 설계하기:** 두 network request를 순차 실행할 때와 병렬 child
   task로 실행할 때 owner/cleanup 차이를 표로 적어라.

## 11. 빠른 복습

- named `def#async`와 explicit `await`가 current surface다.
- top-level await와 async callable literal은 current가 아니다.
- `for await`는 AsyncSequence의 ordered suspension loop다.
- task 책임에는 Cancellation과 cleanup이 남는다.

## 12. 정본 근거와 다음 장

- [비동기 문법·의미](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [Prelude AsyncSequence](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)
- [정확 grammar](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 child task를 lexical scope에 묶고 취소 시 cleanup을 닫는다.
