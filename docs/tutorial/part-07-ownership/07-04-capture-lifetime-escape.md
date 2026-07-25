# 7.4 Capture, lifetime, escape

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

명시적 capture list, closure lifetime/call-right/environment profile과 escape
검사는 현행 설계다. local function은 outer local을 암시적으로 capture하지
않는다.

## 2. 학습 목표

- capture list가 environment construction plan임을 이해한다.
- borrow/inout/move/clone capture의 lifetime 차이를 설명한다.
- return, storage, task, Actor, generator가 escape boundary임을 찾는다.
- `#scoped`, `#once`와 capture mode를 구분한다.

## 3. 선수 지식

borrow region, move/copy/clone, lambda 문법 `{ x: T => ... }`를 알고 있어야
한다.

## 4. 문제에서 출발하기

함수 안의 local 변수를 closure가 사용하면 closure가 언제까지 사는지에
따라 안전성이 달라진다. 즉시 호출되는 closure의 borrow와 함수 밖으로
반환되는 closure의 borrow는 같지 않다.

## 5. 핵심 모델

closure profile은 다음 축을 보존한다.

- lifetime: ordinary / `#scoped`
- call-right: repeatable / `#once`
- environment receiver: shared / `#mut`
- behavior: ordinary / `#pure` / `#guard`
- effect/error/isolation/suspension
- capture descriptors와 cleanup

escape boundary에는 closure return/storage, generator, async suspension,
task/Actor crossing, Facet packaging과 resource owner 이동이 있다.

## 6. 단계별 예제

### 깊이 읽기: closure 환경도 하나의 owner

closure나 local function은 code만 전달하지 않고 captured environment를
함께 가진다. 각 capture는 borrow, move, mutable call right와 lifetime을
결정하며 환경 전체의 callable identity에 참여한다. 이름을 본문에서
사용했다는 이유로 checker가 안전한 mode를 추측하면 escape와 effect가
API 밖에 숨는다.

판정은 closure가 호출 지점 안에서만 쓰이는지 저장·반환·task·actor로
escape하는지 분류하는 데서 시작한다. capture place의 owner와 region,
call right ordinary/`#mut`/`#once`, suspension과 isolation crossing을
검사한다. borrow capture는 owner region을 넘지 않고 move capture는
source를 한 번 consume한다.

작은 trace에서 borrow한 buffer를 캡처한 callback을 즉시 호출하면
callback region이 borrow 안에 닫힐 수 있다. 같은 callback을 반환하면
caller가 buffer owner 종료 뒤 호출할 수 있어 escape로 거부된다.
독립 snapshot을 move capture하면 가능할 수 있지만 copy 비용과 cleanup
책임이 새 환경 owner로 이동한다.

흔한 오해는 `async`를 붙이면 lifetime이 자동 연장된다는 생각이다.
suspension은 오히려 borrow 사용 시점을 뒤로 미루므로 stronger proof가
필요하다. actor 경계를 건너는 closure도 함수 하나가 아니라 capture
environment 전체의 transfer·effect·error·cleanup을 만족해야 한다.

environment construction도 transaction으로 읽는다. capture expression과
clone witness가 모두 성공하고 lifetime·isolation 검사를 통과한 뒤에만
closure owner를 publish한다. 중간 clone이 실패하면 앞서 준비한 임시
값을 정리하고 source place를 계약대로 보존한다. move capture의 commit
뒤에는 closure environment가 owner와 cleanup을 이어받는다.

escape 검사는 단순히 “반환하는가”만 보지 않는다. heap storage, callback
등록, generator suspension, task spawn, actor mailbox, Facet packaging도
호출 시점을 현재 region 밖으로 옮길 수 있다. 각 경계에서 capture별
최소 lifetime, transferability, isolation, effect/error budget을 다시
대조한다. `#scoped`는 해당 lifetime을 제한하고 `#once`는 call right를
한 번으로 제한하므로 서로 대신하지 않는다.

리뷰어는 capture마다 source owner, mode, environment field, closure
종료 시 cleanup을 한 행으로 쓴다. 암시 capture나 “필요하면 runtime이
연장한다”는 설명이 남아 있으면 설계를 완료하지 않는다.

또한 정상 호출, 호출하지 않고 폐기, 한 번 호출 뒤 재호출, body 실패의
네 경로를 대조한다. 각 경로에서 environment field가 live인지 consumed인지,
borrow region이 닫혔는지, cleanup이 정확히 한 번인지가 일치해야 한다.

### 6.1 local function의 explicit borrow capture

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def outer(x: Int) -> Int = {
    [borrow x] def inner(y: Int) -> Int = {
        return x + y
    }

    return inner(1)
}
```

`inner`는 declaration 뒤부터 보이고 `x` 사용을 capture list에 드러낸다.
함수 호출 범위 안에서 borrow가 끝난다.

### 6.2 trailing closure의 좁은 borrow

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let prefix = "user:"
let labels = users ~ map [borrow prefix] { user =>
    "${prefix}${user.name}"
}
```

선택된 `map`의 closure lifetime이 borrow region을 넘지 않는지 검사한다.
trailing syntax가 capture/effect/error 검사를 완화하지 않는다.

### 6.3 once owner를 environment로 옮기기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let permit = acquirePermit()
let submit = [move permit] #once { job =>
    sendWithPermit(permit, job)
}
```

closure가 owner가 되었으므로 original binding은 사용할 수 없다.
정상/오류/취소를 합쳐 permit cleanup path가 정확히 하나여야 한다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: CLOSURE_BORROW_CAPTURE_ESCAPES; product: NOT_RUN -->
```deeplus
private def invalidFactory(borrow prefix: String) -> (() -> String) = {
    return [borrow prefix] { => prefix }
}
// CLOSURE_BORROW_CAPTURE_ESCAPES
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: GENERATOR_BORROW_CAPTURE_FORBIDDEN; product: NOT_RUN -->
```deeplus
let g = [borrow owner] @for item in owner {
    yield item
}
// GENERATOR_BORROW_CAPTURE_FORBIDDEN
```

inout capture는 겹치거나 iteration/suspension을 건널 수 없다. borrowed
Facet도 별도 lifetime proof 없이 task/Actor isolation을 넘지 않는다.

## 8. 다른 기능과의 연결

- generator는 eager collection이 아니라 resumable owner다.
- Actor trailing closure가 isolation을 건너면 Transferable capture,
  suspension/effect/error/cleanup을 독립 검사한다.
- `ReadonlyView`도 owner-bounded이므로 escaping closure에 넣을 수 없다.
- `defer` 등록은 closure block이 아니라 단일 cleanup invocation이다.

## 9. Deeplus다운 작성 관례

- capture를 모두 explicit하게 적고 scope를 좁힌다.
- 오래 사는 callback에는 borrow 대신 필요한 Plain snapshot이나 owned
  value를 의도적으로 만든다.
- `#once`를 lifecycle 의미가 있는 closure에 사용한다.
- async/Actor boundary에서는 capture마다 transfer와 cleanup을 문서화한다.

## 10. 연습 문제

1. **복사:** `[borrow prefix]` local function을 작성하라.
2. **빈칸 완성:** capture list `[___ count]`의 빈칸을 `copy`로 채우고
   source owner와 environment owner가 각각 무엇을 유지하는지 적어라.
3. **설계:** UI callback을 장기 저장해야 할 때 borrow, clone, service
   handle 중 하나를 선택하고 lifetime/effect/cleanup 표를 작성하라.

## 11. 빠른 복습

- capture list는 실제 environment construction plan이다.
- local function의 outer capture는 explicit하다.
- return/storage/task/Actor/generator는 escape boundary다.
- `#once`와 capture `once`는 별도 축이다.
- borrow는 proof 없이 owner보다 오래 살 수 없다.

## 12. 정본 근거와 다음 장

- [함수·closure 레퍼런스](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [소유권 레퍼런스](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)
- [grammar](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 모든 exit path에서 cleanup과 failure transaction을 닫는다.
