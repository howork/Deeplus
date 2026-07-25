# Part 7 — 값, place, owner와 수명

> 과정 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> semantic P0: `0` · OPEN feature P1: `22` · product lanes: `15/15 NOT_RUN`

Deeplus의 소유권은 메모리 주소에 관한 규칙만이 아니다. 값이 어디에
commit되어 있는지, 누가 cleanup을 책임지는지, borrow가 어느 region까지
살 수 있는지, 실패 전후에 owner가 누구인지까지 함께 추적한다.

## 학습 경로

1. [Value, place, owner](07-01-value-place-owner.md)
2. [`borrow`, `mut`, `inout`](07-02-borrow-mut-inout.md)
3. [`move`, `copy`, `clone`, consume](07-03-move-copy-clone-consume.md)
4. [Capture, lifetime, escape](07-04-capture-lifetime-escape.md)
5. [Cleanup, failure, transaction](07-05-cleanup-failure-transaction.md)
6. [실습: resource workflow](lab-07-resource-workflow.md)

## 이 부의 불변선

- owner를 바꾸는 operation에는 성공 commit 지점이 하나다.
- precommit failure는 원래 owner와 value state를 보존한다.
- borrow는 owner보다 오래 살 수 없고 충돌하는 mutation/move/drop과
  함께 존재할 수 없다.
- `mut` parameter와 `inout` parameter는 다른 channel이다.
- resource cleanup responsibility는 move를 따라간다.
- capture mode는 hint가 아니라 실제 ownership/effect/error 계약이다.
- Error, Defect, Cancellation, suspension, cleanup은 독립 축이다.

HIR-H1/MIR 계약이 닫혀 있어도 backend 실행 PASS를 뜻하지 않는다.

## 이 부를 읽는 관점

모든 예제에 네 시점을 적어 보자. 평가 전에는 source place와 owner가
누구인지, commit 전에는 어떤 임시 borrow·resource가 준비됐는지, commit
뒤에는 owner와 cleanup responsibility가 어디로 이동했는지, scope
종료에서는 누가 정확히 한 번 정리하는지를 기록한다. 이 timeline을
그리면 같은 함수 호출도 borrow인지 move인지에 따라 왜 다른 결과를
갖는지 보인다.

소유권 오류를 “값을 쓸 수 없다”로만 읽지 않는다. 이미 move된 source를
다시 읽는 오류, shared borrow와 exclusive mutation 충돌, borrow escape,
cleanup 예약 place의 조기 move는 원인과 고치는 방법이 다르다. checker는
place path와 region, 현재 owner, pending responsibility를 함께 사용해
판정해야 한다.

이 부는 runtime reference counting이나 garbage collector 전략을 정하지
않는다. source 의미가 요구하는 one-owner transfer, nonescaping borrow,
failure atomicity, exact cleanup을 HIR-H1과 MIR에 보존하는 데 집중한다.
실제 allocator·filesystem·backend 실행은 계속 `NOT_RUN`이다.
따라서 예제의 owner trace는 설계 검증표이지 성능 또는 실행 성공 영수증이
아니다.
