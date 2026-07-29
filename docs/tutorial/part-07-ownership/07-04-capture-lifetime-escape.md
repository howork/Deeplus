# 7.4 Capture, lifetime, escape

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

명시적 capture list, closure lifetime/call-right/environment profile과 escape
검사는 현행 설계다. nonescaping lexical access는
`CURRENT_NORMATIVE_STABLE_DESIGN_CONTRACT`, `source_activation: none`이며
제품 lane은 `15/15_NOT_RUN`이다. 이 장의 해당 예제는 구현 완료나 source
acceptance가 아니라 고정된 설계 의미를 설명한다.

## 2. 학습 목표

- capture list가 environment construction plan임을 이해한다.
- nonescaping lexical dependency와 environment capture를 구분한다.
- live call-time read와 explicit snapshot의 차이를 설명한다.
- borrow/inout/move/clone capture의 lifetime 차이를 설명한다.
- return, storage, run, Actor, generator가 escape boundary임을 찾는다.
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

여기에 callable residence와 environment를 독립적으로 본다.

- residence: `FrameIndependent` 또는 `RegionBound(RegionId)`
- environment: `Empty` 또는 `Explicit(CapturePlan)`

그래서 explicit capture가 있으면서 동시에 남은 ancestor lexical
dependency 때문에 region-bound일 수 있다. `[]`는 “아무 dependency도
없다”가 아니라 “ancestor-frame dependency가 없다”는 assertion이다.

escape boundary에는 closure return/storage, generator, async suspension,
run/Actor crossing, Facet packaging과 resource owner 이동이 있다.

## 6. 단계별 예제

### 깊이 읽기: closure 환경도 하나의 owner

closure나 local function은 code와 함께 explicit capture environment를
가질 수 있다. 각 capture는 borrow, move, mutable call right와 lifetime을
결정하며 환경 전체의 callable identity에 참여한다. 하지만 정확히
nonescaping인 동기 callable의 read-only·nonconsuming outer use는 environment
field가 아니라 call-time lexical dependency일 수 있다.

판정은 closure가 호출 지점 안에서만 쓰이는지 저장·반환·run·actor로
escape하는지 분류하는 데서 시작한다. capture place의 owner와 region,
call right ordinary/`#mut`/`#once`, suspension과 isolation crossing을
검사한다. local `def` direct call only, closure immediate invocation,
direct-call-only local binding, 선택된 정확한 `#scoped` formal은 bounded
closed proof가 될 수 있다. unknown flow는 거부한다. borrow capture는 owner
region을 넘지 않고 move capture는 source를 한 번 consume한다.

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

lexical read는 이 transaction에 참여하지 않는다. callable 생성 때 값을
복사하거나 borrow field를 만들지 않고, 호출 때 ancestor place의 현재
값을 읽는다. `[copy value]`는 반대로 생성 시점 snapshot이다. 두 형식을
비용 차이만으로 보면 안 된다. 관찰하는 값과 escape 가능성이 다르다.

escape 검사는 단순히 “반환하는가”만 보지 않는다. heap storage, callback
등록, generator suspension, run spawn, actor mailbox, Facet packaging도
호출 시점을 현재 region 밖으로 옮길 수 있다. 각 경계에서 capture별
최소 lifetime, transferability, isolation, effect/error budget을 다시
대조한다. `#scoped`는 해당 lifetime을 제한하고 `#once`는 call right를
한 번으로 제한하므로 서로 대신하지 않는다.

리뷰어는 capture마다 source owner, mode, environment field, closure
종료 시 cleanup을 한 행으로 쓴다. lexical dependency에는 ancestor place,
최소 region, closed proof route, read-only/nonconsuming 여부를 적는다.
“필요하면 runtime이 lifetime을 연장한다”는 설명은 proof가 아니다.

또한 정상 호출, 호출하지 않고 폐기, 한 번 호출 뒤 재호출, body 실패의
네 경로를 대조한다. 각 경로에서 environment field가 live인지 consumed인지,
borrow region이 닫혔는지, cleanup이 정확히 한 번인지가 일치해야 한다.

### 6.1 local function의 nonescaping lexical read

<!-- deeplus-example: illustrative; status: STABLE_DESIGN; source-activation: none; product: NOT_RUN; authority-source: spec/contracts/nonescaping-lexical-access.json -->
```deeplus
def outer(x: Int) -> Int = {
    def inner(y: Int) -> Int = {
        return x + y
    }

    return inner(1)
}
```

`inner`는 declaration 뒤 direct call로만 사용된다. `x`는 environment
capture가 아니라 호출 동안 필요한 lexical dependency다. `inner`를
반환하거나 aggregate에 저장하면 이 proof는 사라진다.

### 6.2 live read와 copy snapshot

<!-- deeplus-example: illustrative; status: STABLE_DESIGN; source-activation: none; product: NOT_RUN; authority-source: spec/contracts/nonescaping-lexical-access.json -->
```deeplus
var count = 1
def current() -> Int = {
    return count
}
let snapshot = [copy count] { => count }

count = 2
assert current() == 2
assert snapshot() == 1
```

`current`는 call-time live read다. `snapshot`의 `count`는 closure 생성 때
explicit capture environment에 복사된다. lexical access가 outer `var`를
쓸 수 있다는 뜻은 아니다. body의 write, `inout`, move, consume은 이
설계에서 거부한다.

### 6.3 trailing closure의 좁은 borrow

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let prefix = "user:"
let labels = users ~ map { user =>
    "${prefix}${user.name}"
}
```

선택된 `map`의 callback이 정확한 `#scoped` 동기 경로이고 `prefix`를
읽기만 하므로 이 use는 call-time lexical dependency다. trailing syntax가
escape·mutation·capture·effect/error 검사를 완화하지는 않는다.

### 6.4 once owner를 environment로 옮기기

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
Facet도 별도 lifetime proof 없이 run/Actor isolation을 넘지 않는다.

present-empty capture list도 중요한 경계다.

<!-- deeplus-example: illustrative; status: REJECTED_STABLE_DESIGN; source-activation: none; diagnostic: CLOSED_CALLABLE_HAS_OUTER_REFERENCE; product: NOT_RUN; authority-source: spec/contracts/nonescaping-lexical-access.json -->
```deeplus
def invalidClosed(base: Int) -> Int = {
    return [] { => base + 1 }()
}
// CLOSED_CALLABLE_HAS_OUTER_REFERENCE
```

capture list를 생략하면 qualified lexical access를 추론할 수 있지만,
`[]`는 ancestor-frame dependency가 0이라는 author assertion이다. module,
type 또는 Prelude 이름 사용까지 금지하지는 않는다. `[base]`도 `[]`와
다르다. bare item은 현행 explicit capture-item 의미를 유지한다.

<!-- deeplus-example: illustrative; status: REJECTED_STABLE_DESIGN; source-activation: none; diagnostic: ESCAPING_LEXICAL_DEPENDENCY_REQUIRES_CAPTURE; product: NOT_RUN; authority-source: spec/contracts/nonescaping-lexical-access.json -->
```deeplus
def invalidFactory(base: Int) -> (() -> Int) = {
    def read() -> Int = {
        return base
    }
    return read
}
// ESCAPING_LEXICAL_DEPENDENCY_REQUIRES_CAPTURE
```

`read`를 호출하는 대신 반환하면 ancestor activation 뒤 호출될 수 있다.
ordinary callable argument, opaque flow, field/aggregate storage도 같은
closed proof를 주지 않는다. exact selected `#scoped` formal만 call-duration
proof route가 될 수 있다.

## 8. 다른 기능과의 연결

- generator는 eager collection이 아니라 resumable owner다.
- nonescaping lexical access는 async, generator, concur/spawn, Actor,
  isolation crossing과 guard owner에 적용되지 않는다.
- Actor trailing closure가 isolation을 건너면 Transferable capture,
  suspension/effect/error/cleanup을 독립 검사한다.
- `ReadonlyView`도 owner-bounded이므로 escaping closure에 넣을 수 없다.
- `defer` 등록은 closure block이 아니라 단일 cleanup invocation이다.

## 9. Deeplus다운 작성 관례

- 값 snapshot, ownership transfer, mutable access가 목적이면 capture를
  explicit하게 적는다.
- lexical access를 사용할 때는 direct/immediate/`#scoped` proof를 좁고
  쉽게 보이게 유지한다.
- dependency가 없어야 하는 closure에는 `[]` assertion을 사용한다.
- 오래 사는 callback에는 borrow 대신 필요한 Plain snapshot이나 owned
  value를 의도적으로 만든다.
- `#once`를 lifecycle 의미가 있는 closure에 사용한다.
- async/Actor boundary에서는 capture마다 transfer와 cleanup을 문서화한다.

## 10. 연습 문제

1. **비교:** direct-only local function과 `[copy prefix]` closure를 작성하고
   outer 값 변경 뒤 각각 무엇을 읽는지 설명하라.
2. **빈칸 완성:** capture list `[___ count]`의 빈칸을 `copy`로 채우고
   source owner와 environment owner가 각각 무엇을 유지하는지 적어라.
3. **설계:** UI callback을 장기 저장해야 할 때 borrow, clone, service
   handle 중 하나를 선택하고 lifetime/effect/cleanup 표를 작성하라.

## 11. 빠른 복습

- capture list는 실제 environment construction plan이다.
- proven-nonescaping read-only outer use는 call-time lexical dependency일
  수 있다.
- capture list 없음, `[]`, nonempty list는 서로 다른 의미다.
- `[name]` bare capture item은 현행 의미를 유지한다.
- lexical read는 live value, `[copy name]`은 creation-time snapshot을 본다.
- return/storage/run/Actor/generator는 escape boundary다.
- `#once`와 capture `once`는 별도 축이다.
- borrow는 proof 없이 owner보다 오래 살 수 없다.

## 12. 정본 근거와 다음 장

- [함수·closure 레퍼런스](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [소유권 레퍼런스](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)
- [nonescaping lexical access 계약](../../../spec/contracts/nonescaping-lexical-access.json)
- [grammar](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 모든 exit path에서 cleanup과 failure transaction을 닫는다.
