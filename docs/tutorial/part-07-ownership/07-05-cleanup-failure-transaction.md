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
등록 순간 receiver와 argument place를 예약하고 정상 return, Error,
Defect, Cancellation 경로에서 deterministic LIFO 순서를 보존한다.

판정은 cleanup invocation의 exact callee, captured place, effect/error
budget을 확인하는 데서 시작한다. scope 안에서 그 place를 move하거나
rebind해 예약을 깨지 않는지 검사한다. body outcome과 cleanup outcome을
별도 축으로 유지하고 primary/suppressed ordering을 명시한다.

두 cleanup `closeInner`, `closeOuter`를 그 순서로 등록한 작은 trace에서
scope exit는 역순으로 inner가 먼저 실행된다. body가 실패하고 inner도
실패해도 처음 failure를 임의로 덮거나 둘을 하나의 Error로 뭉개지
않는다. 이미 성공한 cleanup을 retry해 count를 늘리지도 않는다.

흔한 오해는 `finally`와 `defer`가 문법만 다른 같은 block이라는 생각이다.
둘은 owner와 evaluation 시점이 다르다. `defer await close()`처럼
suspension을 숨기거나 cleanup block에 여러 action을 넣으면 책임과
실패 순서가 모호해지므로 current 단일 invocation 계약을 사용한다.

cleanup ledger는 등록 순서와 실행 순서를 모두 보존한다. 각 행에
invocation identity, 예약된 receiver/place, 실행을 요구하는 terminal
edge, error/effect row를 적는다. scope를 나갈 때 live한 행을 역순으로
정확히 한 번 소비하고, 이미 실행한 행을 retry하거나 성공 경로에서만
정리하는 최적화를 허용하지 않는다.

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
않은 semantic state와 owner balance를 보존한다는 뜻이다.

### 6.1 단일 cleanup invocation 등록

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let handle = open(path)
defer handle ~ close

let bytes = handle ~ readAll
process(bytes)
```

`defer`는 현재 handle receiver와 cleanup call plan을 등록한다. block이나
trailing closure를 cleanup으로 추측하지 않는다.

### 6.2 resource Class의 lifecycle cleanup

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public resource class File {
    def#cleanup()
        throws CloseError
        effects {io}
    = {
        closeHandle()
    }
}
```

File owner가 scope를 떠날 때 cleanup responsibility가 정확히 한 번
끝나야 한다. move하면 그 책임도 새 owner로 이동한다.

### 6.3 try/finally와 transaction

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

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL; product: NOT_RUN -->
```deeplus
defer {
    closePrimary()
    closeSecondary()
}
// DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL: 각각의 invocation을 따로 등록
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: DEFER_REQUIRES_SINGLE_INVOCATION; product: NOT_RUN -->
```deeplus
defer await remoteClose()
// DEFER_REQUIRES_SINGLE_INVOCATION
```

throwing cleanup이 body failure를 덮는 것, Cancellation을 catchable Error로
바꾸는 것, partial aggregate나 partial owner transfer를 publish하는 것은
거부된다.

## 8. 다른 기능과의 연결

- pattern mismatch와 false guard는 binding/move를 commit하지 않는다.
- Map/schema/constructor는 partial result를 publish하지 않고 temporary를
  역순 cleanup한다.
- Actor enqueue precommit failure는 sender owner를 보존한다.
- task cancellation은 cleanup barrier를 지나 terminal state로 간다.

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
