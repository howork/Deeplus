# 실습 03. Bool predicate와 closure 검증 파이프라인

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 실행:** `15/15 NOT_RUN`

## 목표

정수 값을 검사하는 순수 Bool predicate와, 검사 결과에 따라 문구를
선택하는 두 closure를 하나의 파이프라인으로 결합한다. 이 실습은 아직
refinement, Option/Result 또는 `def#guard`를 선수 지식으로 요구하지
않는다. 핵심은 named function, function-typed parameter, label binding,
`@if`, source evaluation order와 error/effect 책임을 정확히 연결하는
것이다.

## 준비

- [함수, `return`, 오류와 effect](03-01-functions-return-effects.md)
- [매개변수와 label](03-02-parameters-labels-rest-unfold.md)
- [메시지와 trailing closure](03-03-methods-messages-trailing-closures.md)
- [값을 만드는 `@if`](03-04-control-flow.md)
- Part 2의 strict/sequential Bool operator와 source evaluation order

완성할 core는 외부 입력이나 console을 읽지 않는다. caller가 이미 가진
`Int`를 받아 `String`을 돌려주므로 canonical Prelude에 없는 I/O API를
발명하지 않는다.

## 1단계. 순수 predicate를 만든다

predicate는 값이 닫힌 범위에 있는지만 Bool로 답한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure inClosedRange(
    value: Int,
    lower: Int,
    upper: Int,
) -> Bool
    throws Never
    effects {}
= {
    return value >= lower and then value <= upper
}
```

`and then`의 오른쪽은 왼쪽 비교가 true일 때만 평가된다. 이 함수는
refined type을 만들어 주거나 caller의 binding type을 바꾸지 않는다.
그저 total pure Bool 값을 돌려준다. 범위 identity와 narrowing은 다음
Part에서 별도 증명한다.

### 확인 지점

- lower/upper가 parameter label로 분명한가?
- return type이 exact `Bool`인가?
- body가 authority나 observable effect를 숨기지 않는가?
- named function의 정상 경로가 `return`으로 끝나는가?

## 2단계. 정책 closure를 주입한다

검사와 표현 정책을 분리한다. 같은 predicate를 사용해도 caller가 성공과
실패 문구를 다르게 만들 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure chooseMessage(
    value: Int,
    predicate: (Int) -> Bool throws Never effects {},
    onAccept: (Int) -> String throws Never effects {},
    onReject: (Int) -> String throws Never effects {},
) -> String
    throws Never
    effects {}
= {
    return @if predicate(value) {
        onAccept(value)
    } else {
        onReject(value)
    }
}

let message = chooseMessage(
    84,
    predicate: { value: Int =>
        inClosedRange(value, lower: 0, upper: 100)
    },
    onAccept: { value: Int => "accepted:${value}" },
    onReject: { value: Int => "rejected:${value}" },
)
```

세 closure는 각각 function-typed formal에 label로 결합한다. 호출
expression은 source에 적힌 순서로 한 번 평가되고, `@if`는 predicate
결과에 따라 두 policy 중 하나만 호출한다. closure를 전달했다고 해서
error/effect row가 사라지지 않으며 여기서는 모두 `throws Never
effects {}`로 닫혀 있다.

## 판정 trace

1. `chooseMessage`의 fixed parameter 네 개와 call의 네 argument를 label에
   따라 결합한다.
2. argument expression을 source order로 평가해 function value 세 개와
   정수 하나를 staging한다.
3. `predicate(value)`의 callable identity, input type, empty error/effect
   row를 확인한다.
4. 결과가 exact Bool이면 `@if`의 선택된 arm만 평가한다.
5. `onAccept`와 `onReject`의 return type이 모두 `String`인지 확인하고
   total value join을 만든다.
6. named function의 `return`이 최종 String을 caller에게 전달하는지
   확인한다.

이 trace에서 label binding과 runtime evaluation을 같은 화살표로 그리지
않는다. 정적 결합이 먼저 확정되더라도 expression의 observable 순서는
source order다.

## 중간 점검

- `predicate`, `onAccept`, `onReject`가 서로 다른 label을 갖는가?
- 세 function type의 parameter와 result가 call body에 맞는가?
- `@if`에 total `else`가 있는가?
- 두 value arm의 normalized type이 모두 `String`인가?
- 하나의 arm만 호출되는 lazy law를 설명할 수 있는가?
- `print`, `readLine`, 숨은 locale/provider를 가정하지 않았는가?

## 실패 실험

필수 policy argument를 생략하면 call shape가 완성되지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: CALL_SHAPE_* -->
```deeplus
let invalid = chooseMessage(
    84,
    predicate: { value: Int => value >= 0 },
    onAccept: { value: Int => "accepted:${value}" },
)
```

checker가 임의 기본 closure를 발명하거나 `onAccept`를 실패 arm에도
재사용해서는 안 된다. 또 predicate closure가 `Int` 대신 `String`을
받거나 effectful body를 빈 row 함수 자리에 넣으면 별도의 callable
responsibility mismatch로 거부된다.

## 흔한 오해와 미니 사례

첫 번째 오해는 Bool predicate가 refined type을 자동 생성한다는 생각이다.
이 실습에서 `inClosedRange(84, ...)`가 true여도 원래 binding의 declared
type은 `Int`다. 두 번째 오해는 closure label이 runtime dictionary key라는
생각이다. label은 call shape identity이며 expression value와 별도로
결합한다.

미니 사례로 동일한 `inClosedRange`를 점수와 배터리 비율에 재사용하되
서로 다른 `onReject` 문구를 전달해 보라. 검사는 동일하지만 표현 정책은
caller가 소유한다. 그 뒤 parameter 순서를 바꾼 호출을 작성하고 binding
순서와 evaluation 순서를 두 줄로 따로 기록한다.

## 확장 과제

1. **따라 하기:** 허용 범위를 1부터 10으로 바꾸고 성공/실패 문구를
   복사해 새로운 call을 만든다.
2. **빈칸 완성:** `predicate: (Int) -> ___ throws Never effects {}`와
   `return @if ___(value)`의 두 빈칸을 채운다.
3. **스스로 설계하기:** 온도 값을 검사하는 pure predicate와 세 개의
   policy closure를 설계한다. 세 번째 policy가 정말 필요하다면
   `@if` 두 개 또는 다른 total control을 어떻게 구성할지 설명한다.

## 누적 프로젝트 연결

| 구분 | 이 실습의 artifact |
|---|---|
| 이전 입력 | Lab 02의 pure callable, exact value domain과 source-order 판정 표 |
| 이번 출력 | Bool predicate, 두 policy closure, label/evaluation 분리 trace |
| 다음 handoff | Lab 04가 같은 raw `Int` 입력에 명시적 refinement·Result 경계를 추가 |

Lab 04는 이 Bool 결과를 refined proof로 소급 해석하지 않는다. 다음 단계의
`T::check`가 별도 success/error payload를 만들며, 이 실습의 pure policy
분리는 그대로 재사용할 수 있다.

## 완료 체크리스트

- [ ] predicate가 exact Bool을 돌려준다.
- [ ] 모든 callable의 error/effect row를 명시했다.
- [ ] label binding과 source evaluation order를 분리해 설명했다.
- [ ] `@if`가 total하고 선택된 policy만 호출한다.
- [ ] closure가 숨은 refinement proof나 authority를 만들지 않는다.
- [ ] canonical Prelude에 없는 I/O 함수를 가정하지 않았다.
- [ ] 제품 실행 상태를 `15/15 NOT_RUN`으로 유지했다.

## 정본 근거와 다음 부

- [함수·closure·call shape](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [제어 흐름](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [호출 선택과 평가](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [callable coherence 계약](../../../spec/contracts/type-flow-callable-coherence.json)

다음은 [4부 타입 시스템](../part-04-type-system/README.md)에서 Bool 판정과
구분되는 refinement proof, Option/Result와 stable-place narrowing을
배운다.
