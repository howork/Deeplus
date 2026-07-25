# 실습 04. typed parser와 guard 경계

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 실행:** `15/15 NOT_RUN`

## 목표

문자열 parsing과 port refinement를 서로 다른 Result layer로 보존하고,
`def#guard`가 Bool을 만들지만 자동 narrowing summary는 만들지 않는다는
경계를 코드로 확인한다.

## 준비

- [refinement 변환](04-01-inference-aliases-refinement.md)
- [Option과 Result](04-02-union-intersection-option-result.md)
- [narrowing](04-03-narrowing-stable-place.md)
- [함수와 error/effect](../part-03-flow-callables/03-01-functions-return-effects.md)

## 1단계. 두 실패 경계를 타입으로 분리한다

parse 실패와 range 실패를 강제로 한 error로 뭉개지 않고 nested Result로
보존한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private type Port = Int where this >= 0 and this <= 65_535
private type CheckedPort = Result<Port, error RefinementError>

private def#pure parseThenCheck(
    text: String,
    parse: (String) -> Result<Int, error ParseError>
        throws Never
        effects {},
) -> Result<CheckedPort, error ParseError>
    throws Never
    effects {}
= {
    return @match parse(text) {
        Result::ok(raw) => Result::ok(Port::check(raw))
        Result::err(error) => Result::err(error)
    }
}
```

바깥 Result는 caller가 제공한 text parser의 결과이고, 안쪽 Result는
Port predicate의 상세 결과다. 이 예제는 특정 parser가 Prelude에 있다고
가정하지 않는다. 실제 API에서 두 error family를 하나의 명시적 error
set으로 정규화할 authority가 있다면 별도 설계를 할 수 있지만, 이
실습은 자동 합성을 하지 않는다.

### 확인 지점

- Result 사용 지점마다 `error` role marker가 있는가?
- 함수는 같은 오류를 `throws`에 중복 노출하지 않는가?
- `Port::check` 결과를 Option으로 축소하지 않았는가?

## 2단계. 모든 case를 total하게 설명한다

두 layer를 `@match`로 차례로 해체한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure explainPort(
    text: String,
    parse: (String) -> Result<Int, error ParseError>
        throws Never
        effects {},
) -> String
    throws Never
    effects {}
= {
    return @match parseThenCheck(text, parse: parse) {
        Result::ok(checked) => @match checked {
            Result::ok(port) => "port:${port}"
            Result::err(error) => "out-of-range:${error}"
        }
        Result::err(error) => "not-an-integer:${error}"
    }
}
```

각 Result owner가 만든 case를 정확히 소비하므로 누락된 정상 경로가
없다. branch join type은 모두 `String`이다.

## 판정 trace

이 실습은 callable 호출과 type proof를 다음 순서로 나눈다.

1. caller가 공급한 parser function의 parameter, Result return,
   `throws Never effects {}` identity를 `parse` formal과 비교한다.
2. parser의 바깥 Result를 판정하고 `Result::ok(raw)` edge에서만 raw
   `Int` binding을 만든다.
3. `Port::check(raw)`을 한 번 수행해 안쪽 Result를 만든다. 성공 payload는
   `Port`, 실패 payload는 `RefinementError`다.
4. `explainPort`의 nested `@match`가 바깥 parsing error와 안쪽 range
   error를 각각 닫는지 확인한다.
5. 세 정상 value arm이 모두 `String`인지 join하고 named function의
   `return`으로 전달한다.

이 trace에서 Bool 조건이 우연히 같은 범위를 검사해도 3단계의
`Port::check`를 대신하지 않는다. parser API는 caller가 주입하므로
튜토리얼이 canonical `Int::parse`나 console 입력 함수를 발명하지 않는다.

### 확인 지점

- 바깥/안쪽 오류를 어느 arm이 소유하는가?
- 두 `@match`가 각각 exhaustive한가?
- named function의 결과에 `return`을 사용했는가?

## 실패 실험 — guard의 한계

`def#guard`는 total pure Bool predicate로 쓸 수 있지만 호출만으로
refinement proof를 만들지는 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: NARROWING_PROOF_* -->
```deeplus
private def#guard validPort(raw: Int) -> Bool = {
    return raw >= 0 and raw <= 65_535
}

let raw: Int = 8_080
if validPort(raw) {
    let port: Port = raw
}
```

정상 수정은 `Port::check(raw)`을 수행하고 `Result::ok(port)` pattern에서
이미 refinement identity를 가진 payload를 사용하는 것이다.

## 흔한 오해와 미니 사례

첫 번째 오해는 nested Result가 불필요하게 복잡하므로 compiler가 두
error를 자동으로 합쳐야 한다는 생각이다. 합쳐진 public error identity와
conversion rule은 별도 authority가 필요하다. 이 실습은 parser failure와
refinement failure의 owner를 보존한다. 두 번째 오해는 `def#guard`라는
이름이 checker의 hidden narrowing summary를 뜻한다는 생각이다.
현행 profile은 total pure Bool callable이지만 API metadata에 refinement
summary owner가 없다.

미니 사례로 `validPort(raw)`가 true인 branch와
`Port::check(raw)`의 `Result::ok(port)` branch를 나란히 그려 보라.
앞쪽에는 raw `Int`와 Bool 사실만 있고, 뒤쪽에는 exact Port payload가
있다. 이후 mutation으로 raw 값이 바뀔 수 있다면 이전 Bool 결과도 새
값의 proof가 아니다. 성공 payload를 별도 이름으로 유지하면 이 차이가
코드에 드러난다.

## 4단계. 완성 체크리스트

- [ ] parsing과 refinement 실패를 별도 Result layer로 보존했다.
- [ ] 모든 Result use-site에 `error` role을 썼다.
- [ ] 같은 오류를 Result와 `throws`에 중복하지 않았다.
- [ ] 모든 `@match`가 total하고 arm join type이 같다.
- [ ] `def#guard`를 자동 narrowing proof로 사용하지 않았다.
- [ ] 순수 함수의 `throws Never effects {}` 경계를 유지했다.
- [ ] 제품 실행 상태를 `NOT_RUN`으로 유지했다.

## 확장 과제

1. **따라 하기:** `raw as? Port` 버전을 만들고 상세 오류가 사라지는
   지점을 표시한다.
2. **빈칸 완성:** `Result<Port, ___ RefinementError>`의 role marker와
   `Port::___(raw)`의 검사 member를 채운다.
3. **스스로 설계하기:** parse와 refinement 오류를 UI 문구로 바꾸는
   함수를 설계하되, 원래 Result layer를 변경하지 않고 caller policy로
   분리한다.

## 누적 프로젝트 연결

| 구분 | 이 실습의 artifact |
|---|---|
| 이전 입력 | Lab 03의 caller-supplied predicate/policy closure와 label/evaluation trace |
| 이번 출력 | caller-supplied parser, nested Result, exact Port success payload |
| 다음 handoff | Lab 05가 checked primitive를 Record/Class/Enum domain model에 배치 |

Lab 03의 Bool predicate는 UI의 빠른 분기 정책으로 재사용할 수 있지만
Port construction authority로 승격하지 않는다. 다음 Part에서는 이
checked payload를 data model field에 넣을 때 schema/class constructor와
pattern owner가 무엇을 추가로 검증하는지 이어서 기록한다.

## 빠른 복습

- parse와 refinement는 서로 다른 실패 경계일 수 있다.
- Result nesting은 불편함이 아니라 authority 없는 오류 합성을 피하는
  정확한 중간 표현이다.
- `def#guard`는 Bool callable이지 refinement-summary owner가 아니다.
- 성공 payload를 pattern으로 얻어야 exact refined type을 사용할 수 있다.

## 근거와 다음 단계

- [refinement/narrowing 계약](../../../spec/contracts/type-refinement-narrowing-coherence.json)
- [타입 시스템](../../../spec/types/type-system.md)
- [pattern matching](../../grammar-reference/10-patterns-destructuring-and-matching.md)

다음 부에서는 collection의 1-based indexing, sequence와 iterator를
다루며 여기서 만든 exact type과 Result 책임을 실제 데이터 흐름에
적용한다.
