# 04-02. Union, intersection, Option과 Result

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 명시적 closed Union, contract intersection, optional layer와
value-level error channel을 설명한다.

## 2. 학습 목표

- `A | B`와 `A & B`의 의미를 구분한다.
- closed Union의 exact alternative를 exhaustive하게 해체한다.
- `T?`/`Option<T>`와 `Result<T, error E>`를 올바르게 사용한다.
- Result와 `throws`의 오류 중복을 피한다.

## 3. 선수 지식

[추론, alias와 refinement](04-01-inference-aliases-refinement.md)의
명시적 type owner와 Part 3의 total `@match`를 알고 있어야 한다.

### 미리 보는 최소 모델과 후속 심화

typed pattern `value: Int`는 subject가 그 exact alternative일 때만
성공하고 이름을 여는 구조라는 최소 정의로 시작한다. pattern의
transactional binding/move는 Part 5에서 심화한다. `Option<Port>`의
꺾쇠 안 `Port`는 generic constructor에 주는 type argument이며, generic
parameter·variance·`where`는 이 Part의 04-04에서 배운다. 이 두 개념을
이미 안다고 요구하지 않고 Union/Option/Result의 닫힌 case를 읽는 데
필요한 만큼만 먼저 설명한다.

## 4. 문제에서 출발하기

“값이 숫자 또는 문자열이다”, “값이 없을 수 있다”, “작업이 실패 이유와
함께 끝날 수 있다”는 서로 다른 상황이다. 모두 nullable object 하나로
표현하면 exhaustiveness와 error responsibility를 잃는다. Deeplus는
Union, Option, Result를 별도 닫힌 구조로 유지한다.

## 5. 핵심 모델

- `A | B`는 선언된 exact alternatives의 closed Union이다.
- `A & B`는 두 contract 의무를 모두 만족하는 intersection이다.
- compiler는 기대 타입 없이 서로 다른 expression을 anonymous Union으로
  자동 합성하지 않는다.
- `T?`는 optional 한 층이며 `Option<T>`의 명시적 case를 갖는다.
- `Result<T, error E>`는 `ok(T)`와 `err(E)` value alternatives다.
- Result 사용 지점의 error type에는 `error` 역할 표지를 쓴다.
- 같은 recoverable error를 Result와 `throws`에 동시에 노출하지 않는다.

## 6. 단계별 예제

closed Union은 먼저 이름을 주고 exact typed pattern으로 해체한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private type TextOrNumber = Int | String

private def#pure describe(value: TextOrNumber) -> String
= {
    return @match value {
        number: Int => number ~ toString
        text: String => text
    }
}
```

두 arm은 이미 선언된 alternatives를 정확히 덮는다. 이것은 open-world
subclass 검색이나 reflection이 아니다.

Option과 Result는 실패 정보의 양이 다르다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let maybePort: Option<Port> = raw as? Port
let checkedPort: Result<Port, error RefinementError> = Port::check(raw)

let fallback: Port = @match maybePort {
    Option::some(port) => port
    Option::none => defaultPort
}

let report: String = @match checkedPort {
    Result::ok(port) => "accepted:${port}"
    Result::err(error) => "rejected:${error}"
}
```

Option은 실패 상세를 버리고, Result는 caller가 검사할 오류 payload를
보존한다.

### 판정 trace, 미니 사례와 흔한 오해

closed Union을 만들 때 normalized alternative 집합을 선언하고 각 값의
injection identity가 정확히 하나인지 확인한다. `@match`에서는 pattern이
덮는 alternative를 빼며 residual이 0인지 판정한다. Option과 Result도
각각 두 case를 같은 방식으로 닫지만, “부재”와 “상세 오류”라는 책임을
서로 바꾸지 않는다. Result를 선택했다면 같은 recoverable family가
`throws`에도 중복되는지 마지막에 검사한다.

미니 사례에서 `Int | String`은 값 두 개를 동시에 담는 Tuple도,
아무 객체를 runtime 검사하는 open family도 아니다. 흔한 오해는
branch type이 다르면 compiler가 익명 Union을 알아서 만들거나 `T?`와
`Result<T,error E>`를 모두 nullable처럼 취급한다는 생각이다. expected
closed type과 explicit case가 없으면 그 책임을 발명하지 않는다.

## 7. 허용·거부·경계 사례

expected Union 없이 branch 결과를 자동 합치거나 같은 오류를 두 channel에
복제하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: UNION_OR_RESULT_CHANNEL_* -->
```deeplus
let mixed = ready ? 1 : "one"

public def parse(text: String) -> Result<User, error ParseError>
    throws ParseError
    effects {}
= {
    return parseUser(text)
}
```

첫 항목에는 명시적 closed Union expected type이 없다. 두 번째는
`ParseError`를 Result와 throws에 중복 노출한다. Defect와 Cancellation도
Result/throws로 자동 변환하지 않는다.

## 8. 다른 기능과의 연결

Union typed pattern과 `is`/`!is`는 flow-proof 환경을 좁힌다. Option과
Result는 `if let`, `while let`, `for let`, `match`의 refutable pattern과
결합한다. intersection은 Trait/contract 의무를 함께 요구하지만 Tuple이나
두 runtime payload의 곱으로 읽지 않는다.

## 9. Deeplus다운 작성 관례

- 대안 domain은 명시적 type owner로 닫는다.
- 값 부재에는 Option, 실패 상세에는 Result를 쓴다.
- 비국소 실패 전파가 필요할 때만 `throws`를 선택한다.
- case pattern은 canonical `Option::some`, `Result::ok`처럼 owner를
  드러내면 문맥 밖에서도 이해하기 쉽다.
- 서로 다른 arm을 “compiler가 알아서 Union으로 만들 것”이라 기대하지
  않는다.

## 10. 연습 문제

1. **따라 하기:** `Bool | String` closed Union과 두 arm의 `@match`를
   작성한다.
2. **빈칸 완성:** `Result<Value, ___ ParseError>`의 error 역할 표지를
   채운다.
3. **스스로 설계하기:** 하나의 입력 API를 Option 버전과 Result 버전으로
   설계하고 caller가 잃거나 얻는 정보를 비교한다.

## 11. 빠른 복습

- Union은 closed alternatives, intersection은 누적 contract다.
- Option은 값의 부재, Result는 상세 success/error value다.
- anonymous Union inference와 Result/throws 중복은 허용하지 않는다.
- exhaustive pattern은 exact identity를 바탕으로 한다.

## 12. 정본 근거와 다음 장

- [복합 타입과 Option/Result](../../grammar-reference/04-types-generics-and-refinement.md)
- [pattern과 exhaustiveness](../../grammar-reference/10-patterns-destructuring-and-matching.md)
- [error channel](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)

다음은 [narrowing과 stable place](04-03-narrowing-stable-place.md)에서
closed Union fact가 control-flow edge를 따라 이동하는 법을 배운다.
