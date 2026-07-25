# Part 10 — 비동기, 구조화된 태스크, Actor와 공유 상태

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 이름 있는 `def#async`, `await`, 구조화된 task, current actor/message
> 표면을 설명한다. async callable literal과 async comprehension은 이
> Part에서 활성화하지 않는다. 제품 레인은 `15/15 NOT_RUN`이다.

동시성은 “여러 일을 동시에 한다”는 구호보다 owner와 commit 지점을
정확히 기록하는 일이다. Deeplus는 child task의 lexical owner, actor의
격리된 turn, message enqueue commit, request reply correlation,
Cancellation cleanup을 source와 typed residue에 남긴다.

이 부를 읽을 때 “동시에 끝났는가”보다 “누가 시작과 종료를 책임지는가”를
먼저 표시한다. 각 예제에서 task scope, actor mailbox, shared-state
wrapper 중 실제 owner에 밑줄을 긋고, owner가 바뀌는 commit과 실패해도
바뀌지 않는 precommit 경계를 나눈다. 이어 Error, Cancellation, reply
transport failure와 cleanup을 서로 다른 terminal로 적는다. 이런
responsibility trace가 있어야 scheduler의 한 번의 관찰을 언어 보장으로
오해하지 않는다.

## 학습 순서

1. [async, await와 task](10-01-async-await-tasks.md)
2. [구조화된 scope와 Cancellation](10-02-structured-scope-cancellation.md)
3. [actor, protocol과 message](10-03-actor-protocol-messages.md)
4. [mailbox, request/reply와 isolation](10-04-mailbox-request-reply-isolation.md)
5. [공유 상태, 순서와 검증](10-05-shared-state-ordering-testing.md)
6. [실습 — bounded worker](lab-10-bounded-worker.md)

## 기준 예

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async loadPair() -> Pair throws NetworkError = {
    task scope {
        let left = spawn async { => await loadLeft() }
        let right = spawn async { => await loadRight() }
        return Pair!(left: await left, right: await right)
    }
}
```

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let worker = spawn async { => await work() }
return worker
// 별도 owner-transfer 계약 없이 lexical task scope 밖으로 child가 escape한다.
```

## Part 불변 조건

- 모든 child task는 허용된 lexical owner를 갖는다.
- Cancellation은 Error로 변환되지 않고 cleanup 뒤 별도 terminal이다.
- actor 경계에는 borrow/inout payload가 통과하지 않는다.
- enqueue commit 전 실패에서는 sender가 moved owner를 유지한다.
- request admission과 reply await의 오류 시점을 분리한다.
- 서로 다른 sender의 global FIFO나 scheduler fairness를 주장하지 않는다.

## 정본 지도

- [비동기·Actor 참조](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [Actor coherence contract](../../../spec/contracts/actor-concurrency-coherence.json)
- [공유 상태 contract](../../../spec/contracts/shared-state-coherence.json)
- [MIR 관찰 semantics](../../../spec/mir/semantics.md)
