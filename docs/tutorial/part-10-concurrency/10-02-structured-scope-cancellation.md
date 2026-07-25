# 10-02 — 구조화된 task scope와 Cancellation

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

구조화된 owner와 cancellation ordering은 current design이다. task runtime
실행은 `NOT_RUN`이다.

## 2. 학습 목표

- `task scope`, `task group`, `spawn`의 owner 관계를 그린다.
- detached child가 current가 아닌 이유를 설명한다.
- Cancellation 요청·관찰·cleanup·terminal 순서를 추적한다.
- 경쟁 failure의 deterministic primary/suppressed 순서를 읽는다.

## 3. 선수 지식

async/await, `defer`, Error/Defect/Cancellation 분리를 알아야 한다.

## 4. 문제에서 출발하기

함수가 끝났는데 background task가 남아 있으면 그 task의 실패와 resource를
누가 책임지는지 알 수 없다. Deeplus의 구조화된 동시성은 lexical scope가
child를 소유하고, 모든 child와 cleanup이 terminal이 된 뒤에만 scope를
닫는다.

## 5. 핵심 모델

`task scope` 또는 허용된 `task group`은 child owner다. `spawn { => ... }`
와 `spawn async { => ... }`는 제한된 task body이지 일반 closure profile이
아니다. scope는 child를 join하거나 cancel하고 cleanup barrier를 닫기
전에는 종료하지 않는다.

Cancellation lifecycle은 요청 → cooperative boundary 관찰 → cleanup
완료 → terminal cancellation이다. catch가 이를 회복하지 않는다.

## 6. 단계별 예제

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
task scope {
    let profile = spawn async { =>
        await loadProfile(id)
    }
    await profile
}
```

scope는 `profile` handle과 child failure의 owner다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async supervise() -> Unit = {
    task scope {
        defer cleanup()
        let child = spawn async { => await work() }
        await child
    }
}
```

child 성공, 실패, parent Cancellation 모두에서 child terminal 뒤 cleanup이
한 번 실행된다.

## 7. 허용·거부·경계 사례

허용: 두 child의 lexical owner와 명시적 join.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
task scope {
    let first = spawn async { => await loadFirst() }
    let second = spawn async { => await loadSecond() }
    consume(await first, await second)
}
```

거부: child handle escape.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
def#async detached() -> Task<Int> = {
    task scope {
        let child = spawn async { => await compute() }
        return child
    }
}
// 별도 owner-transfer authority가 없다.
```

경쟁 failure에서는 body failure가 우선한다. child failure끼리는 lexical
`spawn_index`가 작은 것이 primary이고 나머지는 index 순 suppressed,
cleanup failure는 실제 LIFO 순으로 뒤에 붙는다.

## 8. 다른 기능과의 연결

- resource cleanup과 defer는 cancellation barrier를 통과한다.
- actor request task에는 ordinary child와 다른 correlation residue가 있다.
- shielded scope도 Cancellation을 버리거나 cleanup을 건너뛰지 않는다.
- HIR/MIR은 scope/task/spawn index와 terminal events를 보존해야 한다.

### 판정 추적

scope에 들어가면 먼저 lexical scope identity를 만들고 각 `spawn`에
source 기준 `spawn_index`를 부여한다. child body가 끝났다고 곧바로
scope를 닫지 않고 모든 child terminal, 등록된 cleanup, parent resume
barrier를 확인한다. Cancellation이 요청되면 cooperative boundary에서
관찰한 child가 cleanup을 수행하고 terminal cancellation을 기록한 뒤에만
join이 풀린다.

실패가 경쟁하면 body failure, child failure, cleanup failure를 구분한다.
body failure가 있으면 primary이고, 그렇지 않으면 가장 작은
`spawn_index`의 child failure가 primary다. 나머지 child failure는 index
순서, cleanup failure는 실제 LIFO 실행 순서로 suppressed에 붙는다.
scheduler가 우연히 먼저 보고한 시각은 이 정본 순서를 바꾸지 않는다.

### 흔한 오해와 미니 사례

scope가 자식 lifetime을 소유한다고 해서 자식 실패를 자동으로 성공으로
바꾸지는 않는다. `await`를 생략해도 scope exit barrier가 책임을 닫지만,
반환값을 소비하고 실패 정책을 선택하려면 명시적 join 지점이 필요하다.

미니 사례로 index 1 child와 index 2 child가 모두 실패하고 `defer`도
실패하면, body failure가 없는 경우 index 1 failure가 primary, index 2와
cleanup failure가 차례로 suppressed다. 실제로 index 2가 먼저 끝났어도
결과 배열을 완료 시각 순으로 뒤집지 않는다.

scope exit를 검토할 때는 네 질문을 순서대로 답한다. 새 spawn admission이
닫혔는가, 모든 child가 success/Error/Cancellation 중 하나로 terminal인가,
등록된 cleanup이 실제 LIFO 순서로 끝났는가, parent가 관찰할 primary와
suppressed 배열이 결정되었는가다. 하나라도 미정이면 lexical block의
마지막 줄에 도달했어도 scope는 닫힌 것이 아니다.

또 다른 미니 사례는 parent body가 먼저 실패한 뒤 child 둘을 cancel하는
경우다. parent failure가 primary이며 child가 cancellation cleanup 중
만든 failure는 정본 suppressed 순서로 남는다. cleanup을 빨리 끝내려고
child handle을 버리거나 parent return을 먼저 관찰시키면 structured
owner와 happens-before 경계를 모두 깨뜨린다.

따라서 “block을 벗어났다”와 “scope가 안전하게 종료되었다”를 같은
사건으로 기록하지 않는다.

## 9. Deeplus다운 작성 관례

task lifetime을 lexical code에서 보이게 한다. “fire and forget” 대신
누가 join하고 누가 cancel하며 실패가 어디로 가는지 먼저 설계한다.

## 10. 연습 문제

1. **따라 하기:** 두 child를 spawn하고 둘 다 await하는 scope를 작성하라.
2. **빈칸 완성:** cancellation lifecycle 네 단계를 순서대로 채워라.
3. **스스로 설계하기:** child 둘과 cleanup 둘이 모두 실패한 경우의
   primary/suppressed 순서를 계산하라.

## 11. 빠른 복습

- 모든 current child는 lexical owner를 갖는다.
- scope는 child terminal과 cleanup 뒤에만 닫힌다.
- Cancellation은 Error catch residual이 아니다.
- failure aggregation은 scheduler 완료 순서가 아니라 정본 순서를 쓴다.

## 12. 정본 근거와 다음 장

- [task와 Cancellation](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [actor concurrency contract](../../../spec/contracts/actor-concurrency-coherence.json)
- [MIR cleanup](../../../spec/mir/semantics.md)

다음 장은 mutable state를 actor turn 안에 격리하고 message로 접근한다.
