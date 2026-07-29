# 03-01. 함수, `return`, 오류와 effect

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 이름 있는 함수의 서명, 본문 결과, error set과 effect row를
현행 정적 계약으로 설명한다. 실행 성공이나 표준 I/O provider의 존재를
주장하지 않는다.

## 2. 학습 목표

- 함수 서명의 return, `throws`, `effects` 축을 따로 읽는다.
- 이름 있는 non-`Unit` 함수와 lambda의 결과 표기를 구분한다.
- `Never`, error set, effect row가 각각 무엇을 약속하는지 설명한다.
- 함수 profile이 owner와 함께 닫힌 집합을 이룬다는 점을 이해한다.

## 3. 선수 지식

`let`/`var`, 기본 타입, expression과 block을 알고 있어야 한다.

## 4. 문제에서 출발하기

함수 이름과 매개변수만 보고 호출을 허용하면 “무엇을 돌려주는가”,
“어떤 오류로 빠질 수 있는가”, “어떤 외부 capability를 쓰는가”가
호출자에게 숨는다. Deeplus는 이 세 축을 함수 identity와 호출 계약에
보존한다. 다만 내부 구현 예제는 존재하지 않는 책임을 반복하지 않는다.
private/local `#pure` 함수의 빈 error/effect row는 짧게 쓰고, 공개 API와
명시적 callable type은 완전한 계약을 계속 표시한다.

## 5. 핵심 모델

- `-> T`는 정상 완료 시 돌려줄 값의 타입이다.
- `throws Never`는 language error 경로가 없다는 뜻이다.
- `throws E`는 선언된 error set 안의 오류만 전파할 수 있다는 뜻이다.
- `effects {}`는 관찰 가능한 effect가 없는 닫힌 row다.
- 이름 있는 non-`Unit` 함수는 정상 완료 경로에서 `return`을 쓴다.
- lambda의 block-local 결과나 `@match`의 block arm에는 `ret`를 쓴다.
- `#pure`, `#async`, `#guard` 같은 profile은 임의 decorator가 아니라
  owner별 admitted matrix에서 선택한다.

<!-- deeplus-status-fence: PREVIEW_DESIGN_NONACTIVATABLE -->

### 비활성 Preview: 모든 callable owner의 양수 책임 표면

다음 Preview는 현재의 내부 예제 간결화보다 넓다. 모든 callable owner에서
두 절을 독립적으로 생략하고 public API digest까지 같은 정규화 법칙으로
묶는 `PREVIEW_DESIGN_NONACTIVATABLE` 설계다. source에서 활성화할 수 없고
제품 lane은 `15/15 NOT_RUN`이다. 현행 Stable의
`private_error_set_inference`도 그대로 유지되므로 이 전체 owner 법칙을
현재 checker 동작으로 간주하면 안 된다.

Preview 설계에서는 clause를 소유하는 callable의 생략을 다음처럼 읽는다.

```text
throws 생략  => throws Never
effects 생략 => effects {}
```

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; expected: DESIGN_ONLY; product: NOT_RUN -->
```deeplus
private def distanceSquared(x: Int, y: Int) -> Int = {
    return x * x + y * y
}
```

위 함수의 완전한 Preview 계약은 `throws Never effects {}`다. body에서
recoverable Error나 observable effect가 남으면 빈 선언 안에 들어가지
않으므로 거부한다. body를 보고 서명을 자동으로 넓히지 않는다.

`= return Expr`에서 두 책임 절을 모두 생략한 경우에는 기존 implicit-pure
검사를 그대로 시도한다. 둘 중 하나라도 쓰면 ordinary shorthand로
검사하고, 생략된 다른 절만 빈 row로 정규화한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; expected: DESIGN_ONLY; product: NOT_RUN -->
```deeplus
def readText(path: String, context files: FileIO) -> String
    effects io
= return readFile(path, context files)
```

이 예는 ordinary callable이며 생략된 `throws`만 `Never`가 된다. 실제
`readFile`이 `IOError`도 남긴다면 명시적 `throws IOError`가 필요하다.

생략과 `throws Never effects {}`는 정규화 뒤 callable identity와 API
digest가 같다. 다만 Trait witness는 더 좁은 row를 허용하고, class
override는 exact profile을 요구하며, function value는 variance와 row
subsumption을 사용한다. responsibility row 차이만으로 overload를 만들
수도 없다. 정확한 owner 범위와 승격 gate는
[`concise-throws-effects-preview-design.json`](../../../spec/contracts/concise-throws-effects-preview-design.json)에
고정되어 있다.

<!-- deeplus-status-fence: CURRENT -->

## 6. 단계별 예제

가장 작은 순수 함수부터 읽어 보자.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure clamp(value: Int, lower: Int, upper: Int) -> Int
= {
    return @if value < lower {
        lower
    } else {
        @if value > upper {
            upper
        } else {
            value
        }
    }
}

let safeLevel: Int = clamp(120, lower: 0, upper: 100)
```

`@if`는 값을 만드는 total expression이고, 이름 있는 함수의 최종
결과는 `return`이 전달한다. 호출 label은 `lower`와 `upper` formal에
정적으로 결합한다. `#pure`가 이미 빈 error/effect row보다 강한 계약을
드러내므로 내부 예제에서 `throws Never effects {}`를 반복하지 않았다.

오류를 값으로 받았다가 그대로 던지는 함수는 정상 return type과 error
경로가 다름을 보여 준다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def failParse(error: ParseError) -> Never
    throws ParseError
    effects {}
= {
    throw error
}
```

정상 완료가 없으므로 return type은 `Never`다. `ParseError`는 error
channel이고 `effects {}`는 외부 effect가 없다는 별도 계약이다. 이
예제는 error 축을 가르치므로 완전한 두 행을 일부러 보여 준다.

### 판정 trace, 미니 사례와 흔한 오해

함수 declaration은 introducer와 owner가 허용되는지 확인한 뒤 parameter
channel과 return type을 만든다. body의 모든 정상 경로를 따라
`return` type을 join하고, 각 실패가 declared ErrorSet 안에 있는지,
사용한 observable effect가 row 안에 있는지 확인한다. 마지막으로 pure
profile이 authority·suspension·mutation을 숨기지 않았는지 판정한다.

미니 사례로 동일한 `String -> String` 모양의 두 함수 중 하나가 locale
service를 context로 받는다면 callable identity가 같지 않다. 흔한 오해는
`throws Never`가 body 내부의 모든 문제를 사라지게 하거나 `effects {}`
가 optimizer에게 호출을 지워도 된다고 지시한다는 생각이다. 두 표기는
호출자가 관찰할 책임을 닫으며, body가 그 약속을 증명해야 한다.

## 7. 허용·거부·경계 사례

이름 있는 함수의 단일 expression을 lambda처럼 곧바로 `=` 뒤에 놓는
축약은 현행 callable block 계약이 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: FUNCTION_BODY_REQUIRES_BLOCK_RETURN_OR_CLAUSE -->
```deeplus
private def#pure doubled(value: Int) -> Int
= value * 2
```

본문을 `{ return value * 2 }`로 작성한다. 반대로 lambda의 단일
expression body에는 `return`을 넣지 않는다. `Unit` 함수는 정상 경로가
값을 요구하지 않지만, 오류와 effect 선언은 여전히 호출 계약의 일부다.

## 8. 다른 기능과의 연결

함수의 error/effect row는 closure type, overload identity, Trait
conformance, cancellation과 연결된다. `Result<T, error E>`를 반환하는
것과 `throws E`는 같은 channel이 아니며, 같은 오류를 두 채널에 중복
표현하지 않는다. `static { ... }` activation도 owning 함수의 pure/effect
검사를 그대로 받는다.

## 9. Deeplus다운 작성 관례

- private/local 순수 함수는 `#pure`와 body proof가 빈 row를 닫는다면
  `throws Never effects {}`를 반복하지 않는다.
- public API, Trait requirement와 명시적 callable type은 검토 가능한
  완전한 책임 계약을 표시한다.
- 값 실패는 `Result`, 비국소 전파는 `throws` 중 하나로 책임을 정한다.
- named non-`Unit` 함수에는 명시적 `return`을 사용한다.
- body 안에서 발생한 effect를 빈 row로 숨기지 않는다.
- profile은 편의상 붙이지 말고 owner와 계약에 맞을 때만 선택한다.

## 10. 연습 문제

1. **따라 하기:** `Int` 두 개 중 작은 값을 돌려주는 private `#pure`
   `minimum`을 빈 책임 절 반복 없이 작성한다.
2. **빈칸 완성:** `private def#pure identity(value: String) -> ___ =
   { return value }`의 return type을 채운다.
3. **스스로 설계하기:** 실패를 `Result`로 돌려줄 함수와 `throws`로
   전파할 함수를 하나씩 설계하고, 두 선택의 호출자 책임을 비교한다.

## 11. 빠른 복습

- return type, error set, effect row는 서로 다른 축이다.
- `Never`는 정상 값이나 오류가 없음을 닫아 표현할 때 쓰인다.
- 이름 있는 함수는 `return`, 로컬 값 body는 `ret`를 쓴다.
- profile과 effect 선언은 문서 주석이 아니라 정적 계약이다.

## 12. 정본 근거와 다음 장

- [함수 profile과 본문](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [오류와 effect](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [타입 시스템](../../../spec/types/type-system.md)

다음은 [매개변수, label, rest와 unfold](03-02-parameters-labels-rest-unfold.md)에서
호출의 모양을 더 정밀하게 구성한다.
