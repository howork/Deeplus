# 10-01 — `def#async`, `await`, `Run`과 비동기 순회

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이름 있는 async 선언, 명시적 suspension, `Run<T>`와 `Reply<T>`의 책임
분리는 현행 Stable 설계다. 실제 scheduler, suspend/resume와 backend
실행 증거는 아직 `NOT_RUN`이다.

## 2. 학습 목표

- `def#async`와 일반 callable을 구분한다.
- async invocation을 현재 실행에서 기다릴 때와 `concur` child로 시작할
  때를 구분한다.
- `Run<T>`와 actor의 `Reply<T>`를 혼동하지 않는다.
- `for#await`와 ordinary `for`를 구분한다.
- Error, Cancellation, cleanup 책임이 suspension을 지나도 남는 이유를
  설명한다.

## 3. 핵심 모델

`def#async`는 이름 있는 비동기 callable profile이다. 선택된 async
invocation은 다음 둘 중 하나의 명시적 소비 문맥에 있어야 한다.

1. `await invocation`: 현재 `ExecutionId`에서 호출을 시작하고 그 결과를
   기다린다.
2. `spawn invocation`: 가장 가까운 `concur`가 소유하는 child execution을
   만들고 `Run<T>`를 돌려준다.

bare async invocation은 조용히 background work를 시작하지 않는다.
`await`도 새로운 child를 만들지 않는다. 둘은 실행 책임이 다르므로
서로의 생략형이 아니다.

```deeplus
let profile = await loadProfile(id) // 현재 execution에서 기다린다.

concur {
    let profileRun: Run<Profile> = spawn loadProfile(id)
    let profile = await profileRun // concur child 결과를 한 번 관찰한다.
}
```

`Run<T>`는 `concur`에 소속된 one-shot observation handle이다. actor
request가 만드는 것은 별도의 `Reply<T>`이며 둘 사이에 암시 변환은
없다.

## 4. 이름 있는 async 함수와 `await`

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async fetch(url: String) -> Bytes
    throws NetworkError
    effects { network }
= {
    return await (client ~ get url)
}
```

receiver와 인자는 source 순서대로 한 번 평가된다. suspension 전후에
선택된 callable identity, `NetworkError`, effect row, live owner와 cleanup
obligation이 그대로 보존된다. resume 시점에 overload를 다시 고르거나
Error를 정상값으로 접지 않는다.

Stable script root의 top-level `await`는 허용하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let status = await loadStatus()
// TOP_LEVEL_AWAIT_NOT_CURRENT
```

## 5. `for#await`

`for#await`는 `for`에 붙은 하나의 owner role이다. `for`, `#`, `await`
사이에 trivia를 넣지 않는다. 이 표면은 `AsyncSequence<T,E>`의
source-ordered next channel을 순회하며 일반 `for`나 async
comprehension으로 재해석되지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async sum(source: AsyncSequence<Int, IOError>) -> Int
    throws IOError
= {
    var total = 0
    for#await value in source {
        total += value
    }
    return total
}
```

각 반복은 `next 요청 → suspend → value/Error/Cancellation resume →
binder commit → body` 순서다. sequence를 미리 `List`로 만들거나 replay
가능하다고 가정하지 않는다. source Error `E`와 Cancellation은 서로
다른 terminal이다.

## 6. `concur` 안의 제한형 `#async` lambda

일반 first-class async lambda는 아직 활성화하지 않는다. 다만 가장
가까운 `concur`가 lifetime을 소유하고 값이 밖으로 escape하지 않는
경우에는 다음 제한형을 사용할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
concur {
    let load = #async { id: UserId => await loadProfile(id) }
    let run: Run<Profile> = spawn load(userId)
    render(await run)
}
```

초기 profile의 fence는 다음과 같다.

- capture가 없거나, 반복 호출에도 안전하다고 증명된 명시적 `copy`
  capture만 사용한다.
- 같은 `concur` 안에서 inward use만 허용한다.
- return, export, storage, sibling/outward transfer, actor/shared carrier,
  unknown higher-order API와 erased callable conversion을 거부한다.
- `move`, `clone`, `deep`, `borrow`, `inout` capture를 이 profile이
  암시하지 않는다.

일반 closure에 expected type만 제공해 `#async`로 바꾸거나, 제한형 lambda를
`concur` 밖으로 반환하는 것은 거부한다.

## 7. 호출·spawn·await의 평가 경계

`spawn loadProfile(id)`에서 callee와 인자는 parent execution이 source
순서대로 정확히 한 번 평가하고 검사한다. 이 단계가 성공한 뒤에만
`ConcurRunId`와 lexical `spawn_index`를 commit한다. argument 평가가
실패하면 child와 handle은 만들어지지 않는다.

`await run`은 one-shot이다. 같은 `Run<T>`를 두 번 기다리거나 이미
소비된 handle을 다시 넘길 수 없다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
concur {
    let run = spawn compute()
    let first = await run
    let second = await run
    // RUN_ALREADY_CONSUMED
}
```

## 8. 흔한 오해

- async 함수를 호출했다고 자동으로 병렬 child가 생기지 않는다.
- `await`는 OS thread를 반드시 block한다는 뜻이 아니다.
- `Run<T>`는 자유롭게 detached할 수 있는 future가 아니다.
- actor request의 `Reply<T>`는 `Run<T>`의 다른 철자가 아니다.
- `for#await`는 여러 item을 동시에 처리하겠다는 선언이 아니다.

두 request를 순차 실행하려면 두 번 `await invocation`을 쓴다. 동시에
시작하려면 다음 장처럼 하나의 `concur` 안에서 두 `Run`을 만들고
관찰한다. 철자 차이는 lifetime owner와 failure aggregation을 바꾸므로
성능 최적화로 생략할 수 없다.

## 9. Deeplus다운 작성 관례

중단 가능성은 callable profile과 `await` 지점에, 병렬 lifetime은
`concur`와 `Run`에 드러낸다. 실패를 Option으로 지우거나 Cancellation을
Error로 접거나, background 실행을 암시적으로 시작하지 않는다.

## 10. 연습 문제

1. **직접 실행:** `def#async` 함수 안에서 하나의 invocation을 직접 기다리는 코드를
   작성하라.
2. **경로 분석:** `AsyncSequence<Item, IOError>`의 Error와 Cancellation 경로를 나누어
   적어라.
3. **책임 비교:** 같은 두 network 요청을 순차 실행할 때와 `concur`에서 병렬 실행할
   때의 owner·cleanup 차이를 비교하라.
4. **경계 설명:** 제한형 `#async` lambda가 `concur` 밖으로 반환될 수 없는 이유를
   설명하라.

## 11. 빠른 복습

- named `def#async`와 explicit `await`가 Stable surface다.
- `spawn`은 `concur` 안에서 `Run<T>`를 만든다.
- actor request는 별도의 `Reply<T>`를 만든다.
- `for#await`는 AsyncSequence의 ordered suspension loop다.
- Error, Cancellation과 cleanup은 suspension을 지나도 지워지지 않는다.

## 12. 정본 근거와 다음 장

- [비동기 문법·의미](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [Prelude AsyncSequence·Run·Reply](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)
- [정확 grammar](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 `concur`가 child lifetime, 취소와 실패 집계를 닫는 방식을
다룬다.
