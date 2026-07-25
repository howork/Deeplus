# 03-03. 메서드, 메시지와 trailing closure

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 ordinary call과 message call을 분리하고, bounded trailing
closure가 두 호출 표면에 어떻게 결합하는지 설명한다.

## 2. 학습 목표

- 일반 호출과 `~` 메시지 호출의 AST 모양을 구분한다.
- 메시지의 0개/1개 aggregate payload 규칙을 이해한다.
- 한 개와 여러 개의 trailing closure label 규칙을 적용한다.
- instance/type-side/conformance member surface를 혼동하지 않는다.

## 3. 선수 지식

[매개변수, label, rest와 unfold](03-02-parameters-labels-rest-unfold.md)의
ordinary call과 label binding을 알고 있어야 한다.

### 미리 보는 최소 모델과 후속 심화

Tuple은 위치로, Record는 label로 구성되는 aggregate라는 최소 직관만
사용하며 자세한 data modeling은 Part 5에서 배운다. `{ value => body }`는
함수 값을 만드는 lambda의 가장 작은 형태다. 이 장에서는 trailing
argument의 call shape만 보고 capture mode와 lifetime은 다음
[closure 장](03-05-closures-captures-static.md)과 Part 7에서 심화한다.
따라서 lambda를 이미 알고 있어야 하는 선수 조건으로 두지 않는다.

## 4. 문제에서 출발하기

`moveTo(x, y)`와 `receiver ~ moveTo (x, y)`는 눈으로 비슷해 보여도 같은
호출이 아니다. 앞은 ordinary argument 두 개, 뒤는 receiver와 selector,
Tuple payload 하나로 구성된 message다. 이 구분이 무너지면 overload,
actor delivery, ownership과 진단 위치가 모두 모호해진다.

## 5. 핵심 모델

- ordinary call은 `callee(arguments)`다.
- message call은 `receiver ~ selector payload`다.
- message selector 뒤에는 payload AST node가 0개 또는 1개만 온다.
- `(x, y)`는 Tuple payload, `(x: a, y: b)`는 all-named Record payload다.
- positional/named mixed payload는 거부한다.
- trailing closure가 하나면 label 생략 또는 명시가 가능하다.
- 둘 이상이면 모든 closure에 서로 다른 label이 필요하다.
- label은 문자열이 아니라 visible function-typed parameter identity다.

## 6. 단계별 예제

ordinary call과 message call을 나란히 읽는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let point = moveTo(10, 20)
let receipt = worker ~ moveTo (10, 20)

let configured = worker ~ configure(name: "Ada", retries: 3)
let pinged = worker ~ ping
```

첫 줄은 인수 두 개의 함수 호출이다. 두 번째 줄은 Tuple payload 하나의
message다. 세 번째는 Record payload 하나이고 네 번째는 no-payload
message다.

trailing closure는 bounded call suffix다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let names = users ~ map { user => user.name }

let outcome = transaction()
    onCommit:{ => "committed" }
    onRollback:{ error => "rolled-back:${error}" }
```

첫 호출에는 closure가 하나라 label을 생략했다. 두 번째에는 둘이므로
`onCommit`, `onRollback`을 모두 적었다. 괄호 밖으로 closure를 보낸다고
capture/effect/error 검사가 완화되지는 않는다.

### 판정 trace, 미니 사례와 흔한 오해

먼저 `(` call suffix인지 `~ selector` message suffix인지 결정한다.
message라면 selector 뒤 payload AST가 0개 또는 1개인지, Tuple/all-named
Record 중 어느 envelope인지 판정한다. 그 뒤 trailing closure 수를 세어
하나면 optional label, 둘 이상이면 모든 unique label을 요구한다.
마지막으로 각 closure의 parameter, capture, effect/error를 일반 함수
값과 같은 수준으로 검사한다.

미니 사례에서 `moveTo(1, 2)`는 ordinary argument 둘이지만
`worker ~ moveTo (1, 2)`는 Tuple payload 하나다. 흔한 오해는 `~`가
모든 호출을 더 읽기 좋게 만드는 pipe이거나 trailing closure가 callback
검사를 느슨하게 한다는 생각이다. 둘 다 구조를 바꾸는 정확한 문법이며
ownership과 failure 책임을 숨기지 않는다.

## 7. 허용·거부·경계 사례

메시지 Record payload는 all-named여야 하고 여러 trailing closure는 모두
label이 있어야 한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; expected-rule: MESSAGE_PAYLOAD_TUPLE_OR_ALL_NAMED_RECORD; diagnostic: MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT -->
```deeplus
let badPayload = worker ~ configure("Ada", retries: 3)

let badCallbacks = transaction()
    { => "ok" }
    onRollback:{ error => "failed:${error}" }
```

첫 호출은 positional/named를 섞었고, 두 번째는 두 closure 중 하나의
label이 없다. 한편 `receiver ~ ping()`은 no-payload 호환 입력일 수
있지만 formatter의 canonical surface는 `receiver ~ ping`이다.
`MESSAGE_PAYLOAD_TUPLE_OR_ALL_NAMED_RECORD`는 교육용 admission rule
label이며 stable diagnostic ID가 아니다. 두 번째 오류의 exact ID는
`MULTIPLE_UNLABELED_TRAILING_CLOSURES_NOT_CURRENT`다.

## 8. 다른 기능과의 연결

메서드 선언의 `.`, `+`, `*.`, `*+` 표면은 현행 owner/member
reachability를 보존한다. type-side member `def::`와
function-local `scope#static`은 이름이 비슷해도 별개다. message는 actor
delivery와 연결될 수 있지만 모든 `~`가 곧 actor spawn 또는 비동기
실행을 뜻하지는 않는다.

## 9. Deeplus다운 작성 관례

- 일반 계산 호출은 `f(...)`, receiver-directed message는 `~`로 분명히
  구분한다.
- 메시지에 여러 값을 보낼 때 Tuple 또는 all-named Record 하나로
  envelope를 만든다.
- callback이 둘 이상이면 처음부터 모두 label을 붙인다.
- closure label은 API 계약으로 안정되게 이름 짓는다.
- `~`를 괄호 없는 일반 함수 호출의 대체 표면으로 쓰지 않는다.

## 10. 연습 문제

1. **따라 하기:** no-payload, Tuple payload, Record payload message를
   각각 하나씩 작성한다.
2. **빈칸 완성:** 두 trailing closure의 `___:{ => ... }` label을 모두
   채워 valid call shape를 만든다.
3. **스스로 설계하기:** 성공/실패 callback을 받는 ordinary API와 message
   API를 각각 설계하고 payload와 closure의 책임을 비교한다.

## 11. 빠른 복습

- ordinary call의 argument list와 message payload는 같은 문법이 아니다.
- message에는 payload node가 최대 하나다.
- 두 개 이상의 trailing closure에는 label이 모두 필요하다.
- trailing closure는 ownership/effect/error 검사를 우회하지 않는다.

## 12. 정본 근거와 다음 장

- [메서드·메시지·trailing closure](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [actor와 동시성](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [callable coherence 계약](../../../spec/contracts/type-flow-callable-coherence.json)

다음은 [조건, 반복, `match`와 값 흐름](03-04-control-flow.md)에서 호출
결과를 제어 흐름으로 연결한다.
