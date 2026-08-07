# 7.5 Cleanup, failure, transaction

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

`defer`, `def#cleanup`, try/finally, deterministic LIFO와
failure-before-commit 법칙은 현행 설계다. Error, Defect, Cancellation은
서로 대체되지 않는다.

## 2. 학습 목표

- cleanup region과 exactly-once 책임을 설명한다.
- `defer`의 단일 invocation 규칙을 쓴다.
- body failure와 cleanup failure의 primary/suppressed 순서를 이해한다.
- assignment, pattern, constructor의 transaction 공통점을 찾는다.

## 3. 선수 지식

resource owner, move, effect/error row와 basic `try`를 알고 있어야 한다.

## 4. 문제에서 출발하기

파일 처리 중 parse가 실패해도 handle은 닫혀야 한다. 닫기 자체가 실패할
수 있다고 해서 원래 parse 오류를 잃어도 안 된다. cleanup은 모든 terminal
edge를 덮고 failure identity와 순서를 보존해야 한다.

## 5. 핵심 모델

cleanup은 source order로 등록되고 deterministic LIFO로 실행된다.
`return`, `throw`, `break`, `continue`, Defect, Cancellation, suspension은
필요한 cleanup을 건너뛰지 못한다.

body failure가 있으면 그것이 primary다. cleanup failure는 실제 LIFO
실행 순서로 suppressed list에 붙는다. Cancellation은 ErrorSet member로
바뀌지 않고 cleanup barrier 뒤 terminal cancellation로 간다.

## 6. 단계별 예제

### 깊이 읽기: cleanup을 별도 책임 축으로 보기

`defer`는 scope exit에서 실행할 정확히 한 개의 non-suspending invocation을
등록한다. block이나 임의 closure를 나중에 실행하는 표면이 아니다.
exact callee와 formal binding은 정적으로 닫고, 등록 순간 runtime
callee/receiver, explicit runtime argument, default expression을 정해진
순서로 한 번 준비한다. scope exit에서 같은 expression을 다시 평가하지
않는다.

판정은 cleanup invocation의 exact callee, prepared value/place,
formal별 transfer mode, result responsibility, effect/error budget을 확인하는
데서 시작한다. operand acquisition은 `SNAPSHOT_VALUE`, `SHARED_LOAN`,
`EXCLUSIVE_LOAN`, `MOVE_INTO_PLAN`, `OWNED_TEMPORARY`,
`PINNED_PLACE_RESERVATION`, `STATIC_EVIDENCE`로 구분한다. `CONSUME`는
seal할 때 affine owner를 cleanup plan으로 한 번 옮기고, borrow/view는
suspension을 포함한 남은 lifetime 동안 exact place를 유지해야 한다.
scope 안에서 reserved place를 move하거나 rebind해 예약을 깨지 않는지
검사한다.

두 cleanup `closeInner`, `closeOuter`를 그 순서로 등록한 작은 trace에서
scope exit는 역순으로 inner가 먼저 실행된다. body가 실패하고 inner도
실패해도 처음 failure를 임의로 덮거나 둘을 하나의 Error로 뭉개지
않는다. 이미 성공한 cleanup을 retry해 count를 늘리지도 않는다.

흔한 오해는 `finally`와 `defer`가 문법만 다른 같은 block이라는 생각이다.
둘은 owner와 evaluation 시점이 다르다. `defer await close()`처럼
suspension을 숨기거나 cleanup block에 여러 action을 넣으면 책임과
실패 순서가 모호해지므로 current 단일 invocation 계약을 사용한다.

cleanup ledger는 등록 순서와 실행 순서를 모두 보존한다. 각 행에
invocation identity, 준비된 receiver/value/place, formal binding과 transfer,
실행을 요구하는 terminal edge, result responsibility, error/effect row를
적는다. scope를 나갈 때 live한 행을 역순으로 정확히 한 번 소비하고,
이미 실행한 행을 retry하거나 성공 경로에서만 정리하는 최적화를 허용하지
않는다.

transaction과 cleanup은 연결되지만 같은 단계는 아니다. assignment,
Pattern, constructor는 검사를 모두 마친 뒤 publication을 한 번 commit해
부분 값을 막는다. cleanup은 commit 전 임시 resource와 commit 후 owner
모두에 대해 각 failure edge의 책임을 닫는다. constructor가 실패하면
완성되지 않은 `Self`는 publish하지 않지만 이미 얻은 handle은 정리해야
하는 식이다.

리뷰에서는 body outcome, LIFO cleanup outcome, 최종 terminal outcome을
세 칸으로 기록한다. primary failure와 suppressed failure의 identity와
순서를 유지하고, Cancellation을 ordinary Error로 재분류하지 않는다.
rollback은 “과거의 외부 effect를 지운다”는 뜻이 아니라 아직 publish하지
않은 semantic state와 owner balance를 보존한다는 뜻이다. 등록 준비 중
I/O가 이미 관찰된 뒤 다음 argument가 실패했다면 I/O를 되감을 수 없다.
대신 temporary와 reversible reservation만 준비 역순으로 정리하고 등록을
0개 publish한다.

### 6.1 단일 cleanup invocation 등록

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let handle = open(path)
defer handle ~ close

let bytes = handle ~ readAll
process(bytes)
```

`defer`는 현재 handle receiver와 cleanup call plan을 등록한다. block이나
trailing closure를 cleanup으로 추측하지 않는다. cleanup result는
`UNIT_NO_VALUE`, `DISCARD_CLEANUP_FREE_VALUE`,
`CLEAN_OWNED_TEMPORARY` 중 하나로 봉인되며, `Result`나 다른 미처리
책임을 조용히 버릴 수는 없다.

### 6.2 receiver, argument, default의 등록 순서

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
defer closeWith(
    acquireHandle(),
    context currentCleanupContext(),
    using closeEvidence,
)
```

선택된 `closeWith`에 빠진 ordinary formal의 default expression이 있다고
하자. runtime 관찰 순서는 다음과 같다.

1. statically bound direct callee identity 선택: runtime evaluation 0회
2. `acquireHandle()`: explicit runtime argument 첫 번째
3. `currentCleanupContext()`: explicit `context` argument 두 번째
4. `using closeEvidence`: static evidence이므로 runtime evaluation 0회
5. omitted-formal default expression: formal declaration order
6. ownership/region/budget 검사를 마친 뒤 registration seal 한 번

5단계에서 실패하면 `acquireHandle()`로 얻은 temporary를 역순 정리하고
등록은 0개다. 2~3단계에서 이미 관찰된 외부 effect는 취소하지 않으며,
scope exit에서 어떤 준비 expression도 다시 실행하지 않는다.

### 6.3 loop iteration과 suspension

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
for item in items {
    defer release(item)
    if skip(item) {
        continue
    }
    consume(item)
}
```

`defer`에 도달한 iteration만 registration을 가진다. `continue`는 그
iteration의 cleanup을 역순 실행한 뒤 다음 iteration으로 간다. normal
fallthrough, `return`, `break`, `continue`, Error 전파, Defect,
Cancellation이 일곱 exit다.

반면 `await` 같은 suspension은 exit가 아니므로 cleanup을 실행하지 않는다.
live owner/borrow/reservation이 suspension을 넘어 유효하다는 proof가 있으면
의무를 보존한 채 resume한다. proof가 없으면 suspension site가 거부된다.
즉 `defer`는 enclosing suspension의 blanket 금지가 아니다.

### 6.4 resource Class의 lifecycle cleanup

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public resource class File {
    def#cleanup()
        throws CloseError
        effects io
    = {
        closeHandle()
    }
}
```

#### 6.2.1 cleanup 책임의 정적 상한

Class header의 `cleanup budget`은 정리가 실제로 실행될 때 평가하는 값이
아니다. base, 소유 field, `def#cleanup`이 노출할 수 있는 recoverable
Error와 Effect의 정적 상한이다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private data class Tracked
cleanup budget {
    effects { audit, io }
    errors CloseError | FlushError
}
{
    def#cleanup()
        throws CloseError
        effects audit
        effects io
    = {
        auditHandle()
        closeHandle()
    }
}
```

이 예에서 hook의 `{CloseError}`와 `{audit, io}`는 header 상한 안에 있다.
field가 별도의 cleanup 책임을 가진다면 그 field의 공개 envelope도 함께
합친다. 선언한 `FlushError`를 현재 구현이 쓰지 않는 것은 허용된다. 상한은
현재 body의 정확한 실행 trace가 아니라 대체 가능한 공개 계약이기 때문이다.

두 가지 생략을 구분해야 한다.

- block 전체를 생략한 비상속 Class: 모든 기여를 합친 정확한 envelope을
  추론한다.
- block은 있지만 축을 생략함: 그 축은 비어 있다. `cleanup budget {}`은
  `Never`와 `{}`를 모두 명시한 것과 같다.

따라서 앞의 `File` 예제는 header가 없어도 `{CloseError}`와 `{io}`를
정확히 추론한다. 반면 같은 hook 앞에 `cleanup budget {}`을 쓰면 budget
초과로 거부된다. Stable resource 상속에서는 sealed root가 명시적 상한을
제시해야 한다. child는 이를 그대로 상속하거나 자기 책임을 모두 포함하는
범위에서 좁힐 수 있지만 넓힐 수 없다.

이 규칙은 `NOT_RUN`인 parser/checker 지원을 주장하지 않는다. 또한 기존
hook → 역획득 field → base 정리 순서와 primary/suppressed failure 순서를
변경하지 않는다.

File owner가 scope를 떠날 때 cleanup responsibility가 정확히 한 번
끝나야 한다. move하면 그 책임도 새 owner로 이동한다.

### 6.5 try/finally와 transaction

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
try {
    perform()
} finally {
    close()
}

var total = 10
total += nextDelta()
```

첫 부분은 Error 전파 전 finally를 수행한다. 둘째 assignment는 original
value와 RHS operation이 성공한 뒤에만 한 번 write한다. overflow나 RHS
failure에서는 `total`이 10으로 남는다.

### 6.6 Pattern과 지역 병렬 대입의 commit

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
var left = acquireLeft()
var right = acquireRight()

left, right = right, left
```

두 target을 왼쪽부터 한 번 resolve하고 RHS Tuple을 한 번 평가한다.
overlap, type, liveness와 ownership transition을 모두 확인한 뒤 하나의
logical commit을 수행한다. commit 전 실패에서는 두 old owner가 그대로
live이고 write count가 0이다. commit 뒤 old owner cleanup은 deterministic
reverse target order로 정확히 한 번 수행한다.

refutable Pattern도 같은 zero-partial-publication 원칙을 쓴다.

```deeplus
let [head, tail..] = values
else return
```

length test나 rest carrier 준비가 실패하면 `head`와 `tail`은 final
binder가 되지 않는다. borrowed rest의 `ListRestView<T>`는 원본 owner
region을 보존하므로 view가 escape하도록 수명을 늘리지 않는다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: DEFER_REQUIRES_SINGLE_INVOCATION; product: NOT_RUN -->
```deeplus
defer await remoteClose()
// DEFER_REQUIRES_SINGLE_INVOCATION
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER; product: NOT_RUN -->
```deeplus
defer worker :~ stop
// ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER
```

actor transport는 immediate admission `Result`와 transfer responsibility를
만든다. `defer`는 그 책임을 조용히 버리는 통로가 아니다.

throwing cleanup이 body failure를 덮는 것, Cancellation을 catchable Error로
바꾸는 것, partial aggregate나 partial owner transfer를 publish하는 것은
거부된다.

## 8. 다른 기능과의 연결

- pattern mismatch와 false guard는 binding/move를 commit하지 않는다.
- 지역 병렬 대입은 target overlap을 정적으로 거부하고 하나의
  `PatternAssignmentCommitId`만 만든다.
- Map/schema/constructor는 partial result를 publish하지 않고 temporary를
  역순 cleanup한다.
- Actor enqueue precommit failure는 sender owner를 보존한다.
- run cancellation은 cleanup barrier를 지나 terminal state로 간다.

## 9. Deeplus다운 작성 관례

- resource를 획득한 바로 다음 줄에 cleanup 등록을 둔다.
- 한 `defer`에는 한 cleanup invocation만 쓴다.
- primary operation failure와 cleanup failure를 API 문서에서 분리한다.
- commit 이전과 이후의 owner를 표로 적어 복구 가능성을 명확히 한다.

## 10. 연습 문제

1. **복사:** 두 handle을 열고 두 `defer`를 등록해 LIFO 순서를 적어라.
2. **빈칸 완성:** `old target 유지 → RHS ___ → commit 횟수 ___`의
   빈칸을 `실패`, `0`으로 채워 failure trace를 완성하라.
3. **설계:** body Error, 두 cleanup Error, Cancellation이 가능한 scope의
   primary/suppressed/terminal ordering을 설계하라.

## 11. 빠른 복습

- cleanup은 모든 exit에서 exactly once다.
- defer는 단일 invocation이다.
- LIFO와 primary/suppressed ordering은 deterministic하다.
- precommit failure는 old owner/value를 보존한다.
- Cancellation은 Error가 아니다.

## 12. 정본 근거와 다음 장

- [제어·오류·cleanup 레퍼런스](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [MIR cleanup region](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [소유권 레퍼런스](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)

이제 실습에서 resource acquire, borrow, move, failure와 cleanup을 하나의
workflow로 합친다.
