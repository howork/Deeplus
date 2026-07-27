# 03-04. 조건, 반복, `match`와 값 흐름

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 statement control과 value-producing control, pattern-binding
control, guarded transfer의 현행 표면을 설명한다.

## 2. 학습 목표

- statement `if`/`match`와 value `@if`/`@match`를 구분한다.
- `if let`, `while let`, `for let`의 transactional binding을 이해한다.
- `return`/`break`/`continue`의 `if`와 `!if` guard를 읽는다.
- value arm의 totality와 type join 요구를 적용한다.

## 3. 선수 지식

Part 2의 `Bool` expression과 이 Part 앞 장의 function/block을 읽을 수
있어야 한다.

### 미리 보는 최소 모델과 후속 심화

Option은 값이 있거나 없는 두 case, Result는 성공값이나 오류값을 가진
두 case라는 최소 모델만 사용한다. `Option::some(value)` 같은 pattern은
case가 맞을 때만 이름을 만드는 refutable pattern이다. closed Union,
상세 Option/Result type은 Part 4에서, Enum과 transactional pattern
commit은 Part 5에서 다시 증명한다. 이 장에서는 이미 알아야 할 선수
지식이 아니라 `if let`과 `@match`를 이해하기 위한 국소 정의로 제공한다.

## 4. 문제에서 출발하기

조건에 따라 동작만 달라지는 경우와 값을 만들어야 하는 경우를 같은
문법으로 처리하면 “모든 경로가 값을 주는가”를 놓치기 쉽다. Deeplus는
statement control과 `@` value control을 표면에서 구분한다. 또한 pattern
control은 성공하기 전까지 binding이나 move를 commit하지 않는다.

## 5. 핵심 모델

- `if condition { ... } else { ... }`는 statement 흐름이다.
- `@if condition { value } else { value }`는 total value expression이다.
- `match subject { ... }`와 `@match subject { ... }`도 같은 구분을 갖는다.
- `@match` direct arm은 expression이 결과이고 block arm은 `ret`를 쓴다.
- `if let`/`while let`/`for let`은 refutable pattern만 받는다.
- `and then` condition chain의 뒤 단계는 앞 단계가 만든 probe binder를
  읽을 수 있다.
- `let!`/`var!`은 mismatch를 명시적 `PatternMatchDefect`로 assert한다.
- control-transfer 뒤 `if` 또는 `!if`는 해당 transfer만 guard한다.
- guard condition은 정확히 `Bool`이어야 한다.

## 6. 단계별 예제

값을 만드는 분기를 먼저 보자.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let label: String = @if score >= 80 {
    "pass"
} else {
    "retry"
}

let stateText: String = @match state {
    ::ready => "ready"
    ::failed(message) => "failed:${message}"
    otherwise => "unknown"
}
```

두 expression은 모든 정상 경로가 `String`을 만든다. `@if`의 `else`,
`@match`의 exhaustive arm 또는 `otherwise`가 totality를 닫는다.

pattern-binding control은 성공한 경우에만 이름을 연다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
if let Option::some(value) = candidate {
    consume(value)
}

for let Result::ok(value) in results if value > 0 {
    accept(value)
}

for item in items {
    continue !if item.active
    break item if item.ready
}
```

실패한 Option/Result pattern은 binding을 남기지 않는다. 반복의 `if`
filter와 transfer guard도 반드시 `Bool`이다.

여러 구조와 조건이 순서대로 의존하면 condition chain을 쓴다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
if let ::some(user) = lookup(id)
    and then let ${email, .._} = user.profile
    and then isVerified(email)
{
    publish(user)
}
```

앞 단계가 실패하면 뒤 단계는 평가하지 않는다. 성공한 probe binder는
read-only로 다음 condition에 보이지만 전체 성공 전에는 final ownership
commit이 일어나지 않는다.

### 판정 trace, 미니 사례와 흔한 오해

control을 만나면 먼저 statement인지 `@` value expression인지 결정한다.
value control이면 모든 정상 경로가 값을 만들고 exact type으로 join되는지
확인한다. pattern control이면 pattern이 refutable한지 nonconsuming하게
시험하고, 성공 edge에만 binding/move를 commit한다. loop transfer의
`if`/`!if` guard는 정확히 Bool인지 확인한 뒤 해당 transfer만 실행한다.

미니 사례에서 `@if ready { "yes" } else { "no" }`는 String 하나를
만들지만 ordinary `if`는 동작의 분기다. 흔한 오해는 `@`가 값을
자동 return하거나 `if let value = candidate`처럼 실패할 수 없는
pattern도 편의상 허용된다는 생각이다. `return`은 named function owner,
`ret`는 local value body owner이며 totality를 우회하지 않는다.

언제 어떤 표면을 쓸지도 분명히 한다. 분기 결과가 이후 식의 입력이면
`@if`/`@match`, 단지 작업 순서만 나누면 statement control을 선택한다.
두 방식을 한 block에서 암묵적으로 섞지 않는다.

## 7. 허용·거부·경계 사례

값 `@if`에 `else`가 없으면 결과를 total하게 만들 수 없다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: IF_EXPR_REQUIRES_ELSE -->
```deeplus
let label = @if ready {
    "ready"
}

if let value = candidate {
    consume(value)
}
```

첫 항목은 total `@if`가 아니고, 두 번째의 단순 binding pattern은
irrefutable이므로 pattern control의 실패 분기를 만들지 못한다.
`return value if condition`의 `if`는 새 `if` statement가 아니라 transfer
guard라는 점도 경계해야 한다.

## 8. 다른 기능과의 연결

`@match`의 exhaustiveness는 Enum과 closed Union, refinement narrowing에
연결된다. 반복의 `break value`는 loop outcome을 만들 수 있으며
`::break(value)`와 `::completed` case로 관찰한다. pattern은 성공 전
nonconsuming하게 시험하고 성공 뒤 binding/move를 commit하므로 ownership
모델과도 연결된다.

## 9. Deeplus다운 작성 관례

- 동작 분기는 `if`/`match`, 값 분기는 `@if`/`@match`로 의도를 드러낸다.
- value control은 처음부터 모든 경로와 exact join type을 설계한다.
- Option/Result 해체에는 `if let` 또는 `match`를 사용한다.
- 순차적인 구조 의존성은 nested lookup이나 숨은 mutation 대신
  `and then` chain으로 드러낸다.
- 반복 안의 짧은 탈출은 guarded transfer로 국소화한다.
- expected type 없이 서로 다른 arm을 anonymous Union으로 합치지 않는다.

## 10. 연습 문제

1. **따라 하기:** 점수를 `@if`로 세 등급 중 하나의 `String`으로 만든다.
2. **빈칸 완성:** `@match option { ::some(value) => value; ___ => fallback }`
   의 total arm을 채운다.
3. **스스로 설계하기:** `for let`과 guarded `continue`를 함께 쓰는
   필터링 흐름을 만들고 binding commit 시점을 설명한다.

## 11. 빠른 복습

- `@` control은 값을 만들며 totality와 type join이 필요하다.
- pattern control은 refutable pattern만 허용한다.
- pattern 실패는 binding이나 move를 commit하지 않는다.
- `if`/`!if`는 control transfer를 국소적으로 guard한다.

## 12. 정본 근거와 다음 장

- [제어 흐름](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [pattern과 narrowing](../../grammar-reference/10-patterns-destructuring-and-matching.md)
- [평가와 commit](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음은 [closure capture와 `static { ... }`](03-05-closures-captures-static.md)에서
실행 환경과 함수별 activation을 다룬다.
