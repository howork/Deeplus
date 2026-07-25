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
명시한다. 단순한 `Int -> Int` 함수도 `throws Never effects {}`를 적으면
실패와 effect가 없는 경계가 눈에 보인다.

## 5. 핵심 모델

- `-> T`는 정상 완료 시 돌려줄 값의 타입이다.
- `throws Never`는 language error 경로가 없다는 뜻이다.
- `throws E`는 선언된 error set 안의 오류만 전파할 수 있다는 뜻이다.
- `effects {}`는 관찰 가능한 effect가 없는 닫힌 row다.
- 이름 있는 non-`Unit` 함수는 정상 완료 경로에서 `return`을 쓴다.
- lambda의 block-local 결과나 `@match`의 block arm에는 `ret`를 쓴다.
- `#pure`, `#async`, `#guard` 같은 profile은 임의 decorator가 아니라
  owner별 admitted matrix에서 선택한다.

## 6. 단계별 예제

가장 작은 순수 함수부터 읽어 보자.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure clamp(value: Int, lower: Int, upper: Int) -> Int
    throws Never
    effects {}
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
정적으로 결합한다.

오류를 값으로 받았다가 그대로 던지는 함수는 정상 return type과 error
경로가 다름을 보여 준다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure failParse(error: ParseError) -> Never
    throws ParseError
    effects {}
= {
    throw error
}
```

정상 완료가 없으므로 return type은 `Never`다. `ParseError`는 error
channel이고 `effects {}`는 외부 effect가 없다는 별도 계약이다.

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
    throws Never
    effects {}
= value * 2
```

본문을 `{ return value * 2 }`로 작성한다. 반대로 lambda의 단일
expression body에는 `return`을 넣지 않는다. `Unit` 함수는 정상 경로가
값을 요구하지 않지만, 오류와 effect 선언은 여전히 호출 계약의 일부다.

## 8. 다른 기능과의 연결

함수의 error/effect row는 closure type, overload identity, Trait
conformance, cancellation과 연결된다. `Result<T, error E>`를 반환하는
것과 `throws E`는 같은 channel이 아니며, 같은 오류를 두 채널에 중복
표현하지 않는다. `scope#static` activation도 owning 함수의 pure/effect
검사를 그대로 받는다.

## 9. Deeplus다운 작성 관례

- 작은 순수 함수도 `throws Never effects {}`로 경계를 드러낸다.
- 값 실패는 `Result`, 비국소 전파는 `throws` 중 하나로 책임을 정한다.
- named non-`Unit` 함수에는 명시적 `return`을 사용한다.
- body 안에서 발생한 effect를 빈 row로 숨기지 않는다.
- profile은 편의상 붙이지 말고 owner와 계약에 맞을 때만 선택한다.

## 10. 연습 문제

1. **따라 하기:** `Int` 두 개 중 작은 값을 돌려주는 `minimum`을
   `throws Never effects {}`로 작성한다.
2. **빈칸 완성:** `private def#pure identity(value: String) -> ___ throws
   Never effects {} = { return value }`의 return type을 채운다.
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
