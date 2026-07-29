# 10-02 — `concur`, 구조화된 실행과 Cancellation

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

`concur`의 lexical ownership과 cancellation ordering은 현행 Stable
설계다. runtime 제품 실행은 `NOT_RUN`이다.

## 2. 학습 목표

- `concur`, `spawn`, `Run<T>`의 owner 관계를 그린다.
- detached child가 허용되지 않는 이유를 설명한다.
- Cancellation 요청·관찰·cleanup·terminal 순서를 추적한다.
- 경쟁 failure의 deterministic primary/suppressed 순서를 읽는다.
- Preview `RunGroup<T>`가 두 번째 lifetime owner가 아님을 구분한다.

## 3. 핵심 모델

`concur { ... }`는 구조화된 동시성의 유일한 lexical owner다. body가
성공, Error, Defect 또는 Cancellation으로 끝나더라도 모든 admitted
child와 필수 cleanup이 terminal이 되기 전에 바깥으로 나갈 수 없다.

`spawn`은 다음 두 operand만 받는다.

- checker가 정적으로 async invocation으로 선택한 expression
- 명시적 inline spawn body `{ => ... }`

둘 다 `Run<T>`를 만들며 별도의 `async` marker를 `spawn` 뒤에 반복하지
않는다.

## 4. 단계별 예제

가장 간결한 형식은 async invocation을 직접 spawn하는 것이다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
concur {
    let profile: Run<Profile> = spawn loadProfile(id)
    render(await profile)
}
```

inline body가 필요한 경우에는 explicit arrow로 경계를 드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async supervise() -> Unit = {
    concur {
        defer cleanup()
        let child: Run<Unit> = spawn { =>
            await work()
        }
        await child
    }
}
```

child 성공, 실패, parent Cancellation 모두에서 child terminal 뒤
cleanup이 정확히 한 번 실행된다.

두 child를 동시에 시작할 수도 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
concur {
    let first = spawn loadFirst()
    let second = spawn loadSecond()
    consume(await first, await second)
}
```

## 5. admission과 identity

`concur` 진입은 하나의 `ConcurId`를 만든다. 각 성공한 spawn은 lexical
`spawn_index`, `ConcurRunId`와 child `ExecutionId`를 만든다. callee와
argument는 parent execution에서 먼저 한 번 평가하므로, 평가 실패에는
run identity나 child execution이 생기지 않는다.

```text
ConcurId
  ├─ spawn_index 0 → ConcurRunId → ExecutionId
  └─ spawn_index 1 → ConcurRunId → ExecutionId
```

`Run<T>`는 이 owner 안에서 한 번 관찰한다. return, module export,
unowned storage나 다른 `concur`로의 전달은 owner-transfer authority가
없으므로 거부한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
def#async detached() -> Run<Int> = {
    concur {
        let child = spawn compute()
        return child
    }
}
// RUN_ESCAPES_CONCUR_OWNER
```

## 6. Cancellation과 terminal barrier

Cancellation lifecycle은 다음 순서를 갖는다.

1. owner가 cancellation을 요청한다.
2. child가 cooperative boundary에서 요청을 관찰한다.
3. child와 owner가 등록한 cleanup을 끝낸다.
4. child가 terminal cancellation을 기록한다.
5. 모든 child terminal과 cleanup이 끝난 뒤 `concur`가 닫힌다.

Cancellation은 Error case가 아니며 `catch`가 회복하지 않는다. shield나
timeout 같은 정책도 cleanup을 건너뛰거나 terminal을 숨기는 권한이
아니다.

## 7. 결정적 failure 집계

동시에 보이는 실패의 정본 순서는 scheduler 완료 시각과 무관하다.

1. body failure가 있으면 primary다.
2. body failure가 없고 child failure만 있으면 가장 작은 lexical
   `spawn_index`의 실패가 primary다.
3. 나머지 child failure는 `spawn_index` 오름차순으로 suppressed에
   붙는다.
4. cleanup failure는 실제 LIFO cleanup 실행 순서로 그 뒤에 붙는다.

따라서 index 1 child가 index 0보다 먼저 실패해도 index 0의 실패가
primary다. 이 규칙은 backend와 scheduler가 달라도 같은 관찰 결과를
보장한다.

## 8. `RunGroup<T>`의 Preview 경계

동종 `Run<T>`의 집합 관찰을 위한 `RunGroup<T>`는
`PREVIEW_DESIGN_NONACTIVATABLE`이다. 이는 새 lexical owner가 아니라
하나의 `ConcurId` 안에서만 사는 observation/collection value 후보다.
현재 source syntax, race/quorum/completion-order/backpressure 기본값은
없다. 따라서 `RunGroup`을 사용한 예시는 현행 코드가 아니며
implementation이나 activation을 주장하지 않는다.

## 9. 흔한 오해

- block 마지막 문장에 도달했다고 `concur`가 닫힌 것은 아니다.
- `await`를 생략했다고 child failure가 사라지지 않는다. exit barrier가
  terminal 책임을 보존한다.
- `Run<T>`를 반환하면 자동으로 owner가 이전되지 않는다.
- `receiver ~ spawn`은 ordinary message selector이며 구조화된 prefix
  `spawn`과 다른 문법 owner다.
- `concur name { ... }` 같은 named region surface는 없다.

## 10. Deeplus다운 작성 관례

병렬 실행의 lifetime과 책임을 lexical code에 보이게 한다. “fire and
forget” 대신 누가 child를 소유하고, 어디서 결과를 관찰하며, 취소와
cleanup이 언제 끝나는지를 먼저 설계한다.

## 11. 연습 문제

1. **구조화하기:** 두 async invocation을 spawn하고 둘 다 기다리는 `concur`를 작성하라.
2. **순서 적기:** cancellation lifecycle 다섯 단계를 순서대로 적어라.
3. **실패 계산:** body, child 둘과 cleanup 둘이 실패할 때 primary/suppressed 순서를
   계산하라.
4. **경계 설명:** `RunGroup<T>`가 `concur`의 대체 owner가 될 수 없는 이유를 설명하라.

## 12. 빠른 복습

- `concur`가 유일한 structured concurrency owner다.
- `spawn`은 async invocation 또는 inline body에서 `Run<T>`를 만든다.
- `Run<T>`는 owner-bound, one-shot observation handle이다.
- Cancellation과 cleanup이 끝나기 전에는 owner가 닫히지 않는다.
- failure ordering은 lexical하고 deterministic하다.

## 13. 정본 근거와 다음 장

- [비동기·actor·동시성 참조](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [actor concurrency contract](../../../spec/contracts/actor-concurrency-coherence.json)
- [MIR 책임 계약](../../../spec/mir/semantics.md)

다음 장은 mutable state를 actor turn 안에 격리하고 message로 접근한다.
