# 01-03. 첫 설계 정적 프로그램

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

여기서 “프로그램”은 현행 source 문법과 정적 의미로 설명할 수 있는
작은 source를 뜻한다. 공식 compiler나 runtime에서 실행됐다는 뜻은
아니다. 출력 API를 가정하지 않고 입력값을 새 값으로 바꾸는 순수 함수로
시작한다.

## 2. 학습 목표

- 이름 있는 함수의 기본 모양을 작성한다.
- parameter, return type, `return`의 역할을 이해한다.
- `def#pure`, `throws Never`, `effects {}`의 책임을 구분한다.
- 문자열 보간으로 입력값에서 결과값을 만든다.

## 3. 선수 지식

상태 표식과 source/diagnostic 처리 단계를 알고 있어야 한다. 아직
Package 설정이나 실행 entry point는 필요하지 않다.

## 4. 문제에서 출발하기

“이름을 받아 인사말을 만든다”는 문제는 I/O가 없어도 완전하다. 입력은
`String`, 출력도 `String`이며 같은 입력에 어떤 값을 만들지 정적으로
설명할 수 있다. 이런 작은 변환부터 시작하면 출력 장치, terminal,
권한, effect를 언어의 기본 문법과 혼동하지 않는다.

## 5. 핵심 모델

이름 있는 함수의 중심 모양은 다음과 같다.

```text
visibility? def#profile name(parameters) -> ReturnType
    throws ErrorSet
    effects EffectRow
= {
    statements
    return expression
}
```

non-Unit 함수의 모든 정상 경로는 `return`으로 값을 내야 한다.
`def#pure`는 `throws Never`, `effects {}`이고 suspension, hidden authority,
mutable/resource capture가 없어야 한다. `#pure`라고 해서 compiler가
실행했거나 allocation이 없다는 뜻은 아니다.

## 6. 단계별 예제

먼저 가장 작은 인사 함수를 작성한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure greeting(name: String) -> String
= {
    return "안녕하세요, $name"
}
```

`name`은 parameter가 만든 지역 이름이다. `$name`은 interpolation
shorthand이며, 함수 호출이나 복잡한 식은 `${...}` 형식을 사용한다.

이제 함수 결과를 명시적 타입의 바인딩에 넣는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let learner: String = "Mina"
let message: String = greeting(learner)
```

호출 인수는 한 번 평가되고 `name` parameter에 결합된다. 설계상
`message`는 `"안녕하세요, Mina"`지만 실제 formatter/runtime 출력
receipt는 없다.

### 판정 trace, 미니 사례와 흔한 오해

작은 함수를 검토할 때도 declaration owner, parameter type, body의 정상
경로, error/effect row 순서로 판정한다. `String`을 돌려준다고 선언한
함수가 두 분기 중 하나에서 값 없이 끝나면 이름과 parameter가 유효해도
callable totality에서 거부된다. 모든 경로가 값을 만들면 `return` 값의
exact type을 확인하고, 그 뒤 body가 선언한 `throws Never effects {}`보다
더 큰 책임을 사용하지 않는지 본다.

미니 사례로 이름을 대문자로 바꾸는 helper가 외부 locale service를
몰래 찾는다면 단순 문자열 변환처럼 보여도 순수 함수가 아니다. 이
장에서는 외부 provider를 가정하지 않는 변환만 선택한다. 흔한 오해인
“design-static은 compile-time 실행”도 피한다. 이 말은 정본 설계가
예상 타입과 의미를 설명한다는 뜻이며, `def#pure` 역시 속도 표지가
아니라 책임을 검사하는 callable profile이다.

## 7. 허용·거부·경계 사례

이름 있는 함수의 bare expression body는 현행이 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: FUNCTION_BODY_REQUIRES_BLOCK_RETURN_OR_CLAUSE -->
```deeplus
private def#pure invalidGreeting(name: String) -> String
    = "안녕하세요, $name"
```

block, `= return Expr`, 또는 선언적 `{{ ... }}` body를 사용해야 한다.
lambda는 별도의 로컬 value-body 규칙을 가지므로 이름 있는 함수와
혼동하지 않는다. 또한 non-Unit 함수의 정상 경로에서 `return`을
빠뜨리면 implicit return을 추측하지 않고 거부한다.

## 8. 다른 기능과의 연결

이 함수는 앞으로 배울 Module 안에 놓을 수 있고, 다른 함수의
trailing closure가 될 수도 있다. effect가 생기면 `effects` row와
필요한 capability channel을 함께 드러내야 한다. 함수의 타입 identity는
parameter와 return뿐 아니라 effects, errors, suspension, ownership도
보존한다.

## 9. Deeplus다운 작성 관례

- 처음에는 입력과 출력을 명시적으로 타입화한다.
- 관찰 가능한 effect가 필요하지 않다면 순수 값 변환으로 문제를 쪼갠다.
- non-Unit 함수는 모든 정상 경로에 명시적 `return`을 둔다.
- 예제의 예상값과 실제 제품 실행을 구분해 쓴다.

## 10. 연습 문제

1. **따라 하기:** `greeting`의 문자열을 `"반갑습니다, $name"`으로 바꾸고
   `String`에서 `String`으로 가는 책임이 그대로인지 확인한다.
2. **빈칸 완성:** `private def#pure square(value: Int) -> Int = { ___ }`의
   빈칸을 `return`을 사용해 채운다.
3. **스스로 설계하기:** 이름과 과정 이름 두 `String`을 받아 한 문장의
   안내문을 만드는 순수 함수를 작성하라. parameter와 return type,
   `throws Never`, `effects {}`를 모두 표시한다.

## 11. 빠른 복습

- 함수 parameter는 입력 이름과 타입을 만든다.
- `->` 뒤는 return type이다.
- 이름 있는 non-Unit 함수는 명시적으로 `return`한다.
- `#pure`는 정적 책임 profile이지 실행 증거가 아니다.
- plain call은 괄호를 쓴다.

## 12. 정본 근거와 다음 장

- [함수 문법](../../../spec/grammar/deeplus.ebnf)
- [함수·호출 참고서](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [타입·callable 책임](../../../spec/types/type-system.md)
- [현행 예제 corpus](../../../examples/guide/review-corpus.md)

다음은 함수를 실제 source 단위에 놓기 위해
[Package, Module, source role](01-04-package-module-source.md)을 배운다.
