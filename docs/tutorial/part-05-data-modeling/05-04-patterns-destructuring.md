# 5.4 패턴과 구조 분해

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

현행 Pattern은 모든 문맥에서 같은 정규화 AST를 사용하지만 문맥마다
refutability 정책이 다르다. 코드 모양만 보고 binding이 항상 성공한다고
가정하지 않는다.

## 2. 학습 목표

- irrefutable binding과 refutable Pattern을 구분한다.
- Enum/Option/Result, Record, List, closed Union의 현재 carrier를 쓴다.
- guarded `let`, `if let`, `while let`, `for let`, `match`를 선택한다.
- 현재 없는 Tuple·Class constructor·Record rest Pattern을 피한다.

## 3. 선수 지식

Enum case와 Record label, List, closed Union의 기초가 필요하다. `move`,
`borrow`의 자세한 의미는 Part 7에서 다시 다룬다.

## 4. 문제에서 출발하기

`Result<Document, error ParseError>`에서 성공 값만 꺼내려면 실패 경로도
반드시 정해야 한다. 단순 `let`이 조용히 실패하게 만들면 binding의
존재와 owner 상태를 알 수 없다. Deeplus는 refutable owner마다 mismatch
처리를 문법에 드러낸다.

## 5. 핵심 모델

현행 구조 분해 carrier:

- Enum, Option, Result 등 명목 variant payload
- 정적으로 알려진 Record label subset
- exact List 또는 마지막 `.._` 하나가 있는 List
- normalized closed Union의 exact alternative typed binder

plain `let`/`var`, ordinary parameter, bare `for`는 irrefutable Pattern만
허용한다. refutable Pattern은 guarded `let`, `if let`, `while let`,
`for let`, statement/value match에 둔다.

## 6. 단계별 예제

### 깊이 읽기: transactional test plan

Pattern은 값을 편리하게 꺼내는 문법 설탕만이 아니다. checker는 subject를
한 번 평가하고 owner/place를 확보한 뒤 값을 소비하지 않는 structural
test plan을 수행한다. 구조가 성공해야 probe binder가 보이고, pure
guard까지 성공한 뒤에야 move·borrow·최종 binding을 원자적으로
commit한다. 이 순서는 뒤늦은 mismatch가 앞 payload만 소비하는 문제를
막는다.

먼저 carrier가 현행 분해 대상인지 판정한다. Enum·Option·Result의
nominal variant, 정적 Record label, List exact shape와 final `.._`,
closed Union typed binder는 각자 닫힌 규칙을 가진다. Tuple decomposition
및 Class constructor pattern은 current가 아니다. 다음으로 binder의
이름·type·ownership mode·region과 alias 충돌을 검사한다.

`Result::ok(${value}) if valid(value)`의 작은 trace에서 subject는 한 번만
읽힌다. 먼저 `ok` VariantId와 Record label을 확인하고 `value`를
nonowning probe로 노출한다. guard가 false면 move와 binding commit은
영이며 다음 arm으로 간다. true일 때만 최종 binder와 body가 활성화된다.
guard가 mutation이나 suspension을 허용하면 이 transaction을 보장할 수
없다.

wildcard가 모든 미래 대안을 안전하게 처리한다는 생각도 흔한 오해다.
현재 값은 받을 수 있지만 새 Enum case를 설계 검토에서 숨길 수 있다.
닫힌 공개 domain은 명시적 case를 선호하고, 실제 residual 정책이 있는
경계에서만 wildcard의 의미를 문서화한다.

### 6.1 Result를 guarded let으로 연다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let ::ok(document) = parse(text)
else ::err(error) => throw error

persist(document)
```

subject `parse(text)`는 한 번 평가된다. `::ok` 구조가 맞지 않으면
unconditional `else` exit가 실행되고 `document`는 scope에 들어오지 않는다.

### 6.2 Record와 List를 필요한 만큼만 연다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let profile = ${ name: "Ada", active: true }
let ${name, active} = profile

if let [head, .._] = values {
    consume(head)
}
```

Record Pattern은 required label subset을 연다. List의 `.._`는 마지막에
하나만 둘 수 있고 remainder를 capture하지 않는다. exact empty/nonempty
구조가 실패하면 `if let` body를 건너뛴다.

### 6.3 closed Union alternative를 바인딩한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private type TextOrNumber = Int | String
let value: TextOrNumber = 13

let text = @match value {
    n: Int => n ~ toString()
    s: String => s
}
```

`n: Int`는 일반 runtime type test가 아니다. subject가 정확한 closed
Union이고 `Int`가 exact alternative identity일 때만 refutable alternative
binder가 된다.

## 7. 허용·거부·경계 사례

허용:

- `if let Option::some(value) = candidate`
- `while let Option::some(job) = queue.next()`
- `for let Result::ok(value) in results if value > 0`
- `${name}` Record subset, `[head, .._]` final ignored rest

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: TUPLE_PATTERN_NOT_CURRENT; product: NOT_RUN -->
```deeplus
let pair = (13, "Ada")
let (id, name) = pair
// TUPLE_PATTERN_NOT_CURRENT
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: PATTERN_PRIVATE_REPRESENTATION_FORBIDDEN; product: NOT_RUN -->
```deeplus
let area = @match shape {
    Circle(radius) => radius * radius
    otherwise => 0
}
// sealed Class도 constructor Pattern carrier가 아님
```

Record rest, captured List rest `..tail`, middle/multiple rest, ordinary
parameter 구조 분해도 현행이 아니다.

## 8. 다른 기능과의 연결

- Pattern success edge는 Enum/Union narrowing fact를 더할 수 있다.
- `pattern as name`은 clone이 아니라 borrow alias다.
- `move pattern`은 structural probe가 아니라 성공 commit 때 적용된다.
- `def#guard` 호출은 Bool을 만들지만 자체로 narrowing summary를 만들지
  않는다.

## 9. Deeplus다운 작성 관례

- API parameter는 identifier로 받고 body에서 실패 경로를 드러내며 분해한다.
- `if let`은 선택적인 한 단계, guarded `let`은 실패 시 현재 경로를
  떠나야 할 때 사용한다.
- 여러 variant에서 값을 만들면 `@match`, side effect만 수행하면
  statement `match`를 쓴다.
- Class 내부를 열 필요가 있으면 명시적인 Record view/adapter를 제공한다.

## 10. 연습 문제

1. **복사:** `if let Option::some(value)` 예제를 작성하고 `value`를 출력하라.
2. **빈칸 완성:** `if let [___, ___] = values`의 두 빈칸에 `first`,
   `second`를 넣고 body가 실행되는 exact List 길이를 적어라.
3. **설계:** `Result<Order, error ValidationError>`를 처리하는 guarded
   `let`과 `@match` 두 버전을 만들고 어느 API 경계에 더 알맞은지 논하라.

## 11. 빠른 복습

- Pattern owner마다 mismatch disposition이 명시된다.
- subject는 한 번 평가되고 probe는 nonconsuming이다.
- Tuple와 Class constructor Pattern은 현행이 아니다.
- closed Union typed binder는 open runtime type test가 아니다.
- 성공할 때만 binding과 ownership이 commit된다.

## 12. 정본 근거와 다음 장

- [타입 시스템의 Pattern 계약](../../../spec/types/type-system.md)
- [Pattern 문법](../../../spec/grammar/deeplus.ebnf)
- [패턴 레퍼런스](../../grammar-reference/10-patterns-destructuring-and-matching.md)
- [타입 refinement 레퍼런스](../../grammar-reference/04-types-generics-and-refinement.md)

다음 장에서는 match의 완전성, guard의 한계와 transactional commit을
정확히 연결한다.
