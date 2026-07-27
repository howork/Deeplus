# 03-02. 매개변수, label, rest와 unfold

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 value/context/witness channel, positional rest, named rest와
call-side unfold의 현행 call-shape를 설명한다.

## 2. 학습 목표

- parameter label과 runtime value를 구분한다.
- ownership mode, context, witness channel을 식별한다.
- `...`, `***`, `*`, `**`의 위치별 역할을 구분한다.
- source evaluation order와 formal binding을 따로 설명한다.

## 3. 선수 지식

[함수, `return`, 오류와 effect](03-01-functions-return-effects.md)의
기본 서명과 ordinary call `f(...)`를 읽을 수 있어야 한다.

### 미리 보는 최소 모델과 후속 심화

이 장에서 `Record`는 이름 있는 field를 가진 구조 값이라는 최소 직관만
사용한다. `options***: Record`는 남은 named argument를 label row로
모으는 call channel이며, Record/Map/schema의 전체 차이는 Part 5에서
배운다. `borrow`/`move`는 값을 읽거나 소유권을 넘기는 parameter mode라는
정도만 먼저 사용하고 Part 7에서 place와 lifetime을 증명한다.
`witness Trait`는 선택된 conformance 증거를 받는 별도 channel이며
Trait 선언과 coherence는 Part 6의 후속 심화다. 따라서 이 개념들은 이
장의 선수 조건이 아니라 call shape를 정확히 읽기 위한 작은 안내판이다.

## 4. 문제에서 출발하기

호출에 위치 인수, 이름 있는 인수, 가변 인수와 설정 row가 한꺼번에
들어오면 단순한 “값 목록”만으로는 API identity를 보존할 수 없다.
Deeplus는 positional repeated channel과 named Record channel을 서로
다른 residue로 유지한다. label은 runtime `String`이 아니며, 선택된
formal parameter와의 정적 결합 정보다.

## 5. 핵심 모델

- value parameter는 필요하면 `borrow`, `mut`, `move`, `inout` mode를
  갖는다.
- `context x: T`는 ambient capability/context channel이다.
- `using w: witness Trait`는 conformance witness channel이다.
- `items...: T`는 repeated positional parameter다.
- `options***: Record`는 유일하고 마지막인 named-rest parameter다.
- 호출의 `*values`는 positional unfold, `**record`는 named unfold다.
- named-rest parameter/type은 `***`, call-side named unfold는 `**`다.
- argument expression은 source에 적힌 순서로 정확히 한 번 평가된다.
- ordinary value parameter는 call-channel 이름 뒤에 checker-proven
  irrefutable structural Pattern을 body-entry plan으로 둘 수 있다.

## 6. 단계별 예제

positional rest와 named rest를 한 함수에 둘 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure command(
    name: String,
    args...: String,
    options***: Record,
) -> Record
= {
    return options
}

let args = ["a.txt", "b.txt"]
let options = ${ overwrite: true, mode: "safe" }
let selected = command("copy", *args, **options)
```

`args...`와 `options***`는 public call identity에도 각각 `String...`,
`Record***`로 남는다. body의 `options` 값은 Record지만 channel identity가
사라지는 것은 아니다.

ownership, context와 witness도 call shape의 일부다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure renderWith<T>(
    borrow value: T,
    context locale: Locale,
    using display: witness Display<T>,
) -> String
= {
    return renderValue(value, context locale, using display)
}
```

같은 `T` 값이라도 `borrow` value, `context Locale`, `witness Display<T>`는
서로 바꿀 수 없는 channel이다.
여기서 `renderValue`는 예제 Module이 선언한 helper다. `display` evidence를
ordinary receiver value처럼 호출하거나 저장하지 않고 `using` channel로
그대로 전달한다.

### 6.1 parameter Pattern은 call shape를 바꾸지 않는다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def distance(point Point${x, y}: Point) -> Float = {
    return sqrt(x ^ 2 + y ^ 2)
}
```

`point`는 외부 call label과 whole-value local이다. `Point${x, y}`는
parameter ownership commit 뒤 body-entry에서만 실행된다. overload와
function type은 여전히 `point: Point`의 call channel을 사용한다.
Pattern은 parameter type에 대해 irrefutable이어야 한다.

```deeplus
private def first(values: List<Int>) -> Int = {
    let [head, .._] = values
    else throw DomainError::empty
    return head
}
```

동적 List처럼 빈 값이 가능한 carrier는 formal에서 직접 분해하지 않고
body에서 failure owner를 선택한다.

### 판정 trace, 미니 사례와 흔한 오해

호출을 판정할 때는 먼저 positional, named, context, witness, rest
channel을 분류한다. fixed formal에 값을 결합한 뒤 repeated positional과
마지막 named-rest를 채우고, 누락·중복 label을 검사한다. 이 binding
trace와 별도로 각 expression은 source order로 한 번 평가한다. 함수
타입을 만들 때도 `T...`와 `Record***` residue를 지우지 않는다.

미니 사례에서 `command("copy", *args, **options)`의 `*args`는 여러
positional value를 공급하고 `**options`는 정적 Record label을 공급한다.
흔한 오해는 별 개수가 많을수록 더 깊은 spread라는 생각이다. 위치와
개수가 문법 owner를 고르므로 parameter의 `***`와 call의 `**`를 서로
대칭으로 바꿀 수 없다. Map key도 Record label로 승격되지 않는다.

## 7. 허용·거부·경계 사례

formal은 `options***: Record`, call unfold는 `**options`여야 한다.
named-rest는 canonical structural `Record`만 받으며 `Map`을 펼쳐 label
proof를 대신할 수 없다. label을 formal과 다른 순서로 적어도 expression
평가 순서는 source order다.

## 8. 다른 기능과의 연결

이 정확한 call shape는 overload resolution, function type, public API
digest, trailing closure label, Trait conformance에 연결된다. repeated와
named-rest를 함수 값에 저장할 때도 `(String, String..., Record***) ->
Record`처럼 residue를 보존한다.

## 9. Deeplus다운 작성 관례

- API의 필수 값은 고정 parameter, 여분의 위치 값은 `...`로 구분한다.
- 열린 이름 설정이 정말 필요할 때만 최종 `Record***`를 둔다.
- `Map`을 이름 있는 인수처럼 암묵 변환하지 않는다.
- ownership/context/witness channel을 value parameter로 위장하지 않는다.
- label과 expression 순서를 읽을 때 binding과 evaluation을 따로 적는다.
- parameter Pattern을 쓸 때도 call-channel 이름을 남기고 refutable
  검사는 body에 둔다.

## 10. 연습 문제

1. **따라 하기:** `event`, `tags...`, `metadata***`를 받는 함수 서명을
   쓰고 배열과 Record를 각각 펼쳐 호출한다.
2. **빈칸 완성:** `dispatch(name, ___args, ___options)`에서 positional
   unfold와 named unfold prefix를 채운다.
3. **스스로 설계하기:** 고정 parameter와 `Record***`를 함께 쓰는 API를
   설계하고, 왜 `Map`을 받지 않는지 설명한다.

## 11. 빠른 복습

- label은 runtime 문자열이 아니라 정적 call identity다.
- `...`/`***`는 parameter, `*`/`**`는 call unfold다.
- named-rest는 하나, 마지막, canonical `Record`다.
- context와 witness는 일반 value channel이 아니다.

## 12. 정본 근거와 다음 장

- [호출과 parameter](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [call-shape 타입 계약](../../../spec/types/type-system.md)
- [평가·overload 선택](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)

다음은 [메서드, 메시지와 trailing closure](03-03-methods-messages-trailing-closures.md)에서
호출 표면을 확장한다.
