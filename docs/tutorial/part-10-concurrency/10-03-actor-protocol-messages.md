# 10-03 — Actor, protocol과 message surface

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

current actor declaration과 message syntax를 설명한다. mailbox/runtime
동작의 target execution은 없다.

## 2. 학습 목표

- actor state region과 turn을 설명한다.
- protocol의 `send`와 `request` 요구를 구분한다.
- message payload의 0/1 aggregate 규칙을 적용한다.
- ordinary call과 message call의 resolution domain을 구분한다.

## 3. 선수 지식

Class/Trait 관계, function argument, Tuple/Record, move와 Shareable을 알아야
한다.

## 4. 문제에서 출발하기

actor reference를 ordinary object처럼 호출하면 state isolation과 enqueue
시점이 보이지 않는다. Deeplus는 `~` message suffix와 actor/protocol
selector domain을 사용하며 ordinary method fallback을 허용하지 않는다.

## 5. 핵심 모델

actor는 하나의 isolated mutable state region과 mailbox를 소유한다.
한 번에 하나의 admitted turn만 state를 변경한다. `on`은 one-way handler,
`request`는 reply type을 갖는 handler다. protocol에서는 각각 `send`,
`request` requirement로 기록한다.

message는 payload 없음 또는 하나의 scalar/Tuple/Record aggregate만 갖는다.
context/witness channel을 payload에서 합성하지 않는다.

## 6. 단계별 예제

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public protocol CounterProtocol {
    send add(value: Int)
    request current() -> Int
}

public actor Counter {
    on add(value: Int) = { }
    request current() -> Int = { return 0 }
}
```

message payload shape:

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
counter ~ add(value: 3)
let admission = counter ~ current()
```

첫 조각은 named Record payload 하나이며 두 번째는 payload 없음이다.
`current()`의 빈 괄호는 호환 표기지만 canonical message는
`counter ~ current`다.

## 7. 허용·거부·경계 사례

허용: Tuple 또는 Record 한 개로 payload를 닫는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
worker ~ moveTo (10, 20)
worker ~ configure(name: "Ada", retries: 3)
```

거부: positional과 named payload를 섞거나 ordinary method로 fallback한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
worker ~ configure("Ada", retries: 3)
unknownActor ~ missingMessage job
```

selector path는 `Protocol::message` 또는 `Type::ExtensionSet::message`처럼
정적으로 보존될 수 있지만, runtime 문자열 lookup이나 source-order
winner는 없다.

## 8. 다른 기능과의 연결

- message trailing closure는 ordinary call과 구조만 공유하며 actor-safe를
  자동 보장하지 않는다.
- move payload는 enqueue commit에서만 actor owner로 넘어간다.
- handler await 중에도 같은 turn identity와 mutation authority가 유지된다.
- protocol handler spelling만으로 conformance evidence가 생기지 않는다.

### 판정 추적

message 식은 먼저 receiver가 actor 또는 admitted protocol reference인지
확인하고 selector를 actor/protocol domain에서만 해석한다. 다음으로
payload가 없음, scalar 하나, Tuple 하나, named Record 하나 중 어느
shape인지 고정한다. 그 뒤 각 field의 type과 `Transferable`/`Shareable`
조건을 검사하고 mailbox admission 단계로 넘긴다. ordinary method
lookup이나 runtime 문자열 검색은 어느 단계에도 fallback하지 않는다.

handler 쪽에서는 admitted message identity가 turn을 열고 그 turn만
isolated state mutation authority를 갖는다. handler가 `await`하더라도
turn identity를 새 actor instance처럼 다시 만들지 않는다. protocol
requirement와 actor handler의 결합은 별도 conformance evidence가
필요하며 같은 spelling만으로 witness를 합성하지 않는다.

### 흔한 오해와 미니 사례

`worker ~ configure(name: "Ada", retries: 3)`의 두 label은 “인자 두 개”가
아니라 하나의 Record payload다. 반대로 `worker ~ moveTo (10, 20)`은
Tuple payload 하나다. positional과 named를 섞으면 convenient call
rewriting으로 고치지 않고 payload shape 단계에서 거부한다.

또한 `~`를 비동기 점 호출로 이해하면 admission Result와 enqueue commit을
놓치기 쉽다. 미니 사례에서 unknown selector가 있으면 actor가 메시지를
받은 뒤 실패하는 것이 아니라 정적 selector resolution에서 멈춘다.
따라서 mailbox owner나 correlation도 만들어지지 않는다.

검토 표는 selector, payload, crossing, admission 네 열로 만든다.
`configure`가 protocol requirement와 결합되는지, named fields가 exact
Record row인지, 각 field가 actor 경계를 건널 수 있는지, enqueue commit
전에 어떤 오류가 가능한지를 적는다. selector가 틀렸다면 뒤 세 열을
실행하지 않고, payload가 틀렸다면 crossing이나 mailbox 상태를 추측하지
않는다. 첫 결정적 실패가 primary 진단을 소유한다.

protocol은 actor의 “인터페이스처럼 보이는 목록”에 그치지 않는다.
requirement identity, reply/Error 책임, conformance evidence가 함께
닫혀야 reference를 통해 메시지를 보낼 수 있다. 같은 이름의 ordinary
method, extension member, actor message가 있어도 source order로 승자를
고르지 않고 각 lookup domain을 분리한다.

메시지 trailing closure도 payload aggregate의 일부로만 판정한다.
ordinary call과 비슷하게 보이더라도 closure capture가 actor crossing을
만족하는지 따로 검사하고, actor-local mutable borrow를 몰래 캡처하지
않게 한다. 미니 사례로 logging closure가 immutable `JobId`를 capture하는
경우와 local buffer의 `inout`를 capture하는 경우를 나누면 전자는
Shareable/Transferable 계약을 검토할 수 있지만 후자는 actor 경계를
통과할 수 없다. trailing spelling 자체가 안전 증명은 아니다.

## 9. Deeplus다운 작성 관례

actor 경계를 API 경계처럼 다룬다. payload aggregate, ownership transfer,
admission Result, reply task를 모두 source와 type responsibility에
드러낸다.

## 10. 연습 문제

1. **따라 하기:** one-way `send ping`과 `request status() -> Status`를
   가진 protocol을 작성하라.
2. **빈칸 완성:** `(x, y)`는 ___ payload, `(x: 1, y: 2)`는 ___ payload다.
3. **스스로 설계하기:** 주문 actor의 command와 query를 `on`/`request`로
   나누고 각 payload owner를 설명하라.

## 11. 빠른 복습

- actor state는 isolated turn이 소유한다.
- on/send는 one-way, request는 reply가 있다.
- message는 0/1 payload aggregate다.
- message resolution은 ordinary method fallback을 하지 않는다.

## 12. 정본 근거와 다음 장

- [actor와 message 참조](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [message/call coherence](../../../spec/contracts/type-flow-callable-coherence.json)
- [exact grammar](../../../spec/grammar/deeplus.ebnf)

다음 장은 mailbox admission과 request reply의 commit 전후를 추적한다.
