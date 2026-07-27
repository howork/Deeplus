# 04-03. narrowing과 stable place

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 declared semantic type과 별도로 유지되는 flow-proof 환경 `Phi`,
closed Union의 `is`/`!is`, proof invalidation을 설명한다.

## 2. 학습 목표

- 선언 타입과 edge-local narrowing fact를 구분한다.
- closed Union exact alternative에만 `is`/`!is`를 적용한다.
- `and then`/`otherwise`가 전달하는 edge fact를 설명한다.
- mutation, borrow, escape와 consume이 fact를 제거하는 이유를 이해한다.

## 3. 선수 지식

closed Union, strict/short-circuit Bool operator, control-flow edge를 알고
있어야 한다.

## 4. 문제에서 출발하기

조건 왼쪽에서 “이 값은 Int다”라고 확인했더라도, 오른쪽을 보기 전에
값이 바뀔 수 있다면 그 증명은 쓸 수 없다. Deeplus는 이름 철자가 같은지
보는 대신 재평가 없이 같은 저장 위치를 뜻하는 stable place인지
검사하고, 값을 바꿀 수 있는 사건에서 proof를 제거한다.

## 5. 핵심 모델

- `Phi`는 binding의 declared type과 별도의 edge-local proof map이다.
- `value is Int`는 value가 closed Union이고 `Int`가 exact alternative일
  때만 허용된다.
- true edge는 target alternative, false edge는 나머지 alternatives다.
- `!is`는 두 edge 집합을 반대로 만든다.
- `and then` 오른쪽에는 left true fact, `otherwise` 오른쪽에는 left
  false fact가 전달된다.
- strict `and`/`or`는 오른쪽에 이 선행 narrowing을 제공하지 않는다.
- join은 모든 incoming edge에 공통인 사실만 남긴다.

## 6. 단계별 예제

closed Union과 sequential Bool operator를 함께 사용한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public type TextOrNumber = Int | String

public def#pure isPositiveNumber(value: TextOrNumber) -> Bool
    throws Never
    effects {}
= {
    return value is Int and then value > 0
}
```

`and then` 오른쪽의 `value > 0`에서 value는 Int alternative로 좁혀져
있다. strict `and`로 바꾸면 같은 선행 fact를 보장하지 않는다.

typed pattern은 검사와 binding을 함께 수행한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure textLength(value: TextOrNumber) -> Int
    throws Never
    effects {}
= {
    if let text: String = value {
        return text.length
    }

    return 0
}
```

pattern이 성공한 edge에서만 `text`가 생긴다. 실패는 partial binding이나
move를 남기지 않는다.

### 판정 trace, 미니 사례와 흔한 오해

`value is Int`를 만나면 먼저 value의 normalized declared type이 하나의
closed Union인지 확인한다. target이 exact single alternative이면 현재
candidate set을 true/false edge로 나눈다. `and then` 오른쪽에는 true
fact를 전달하지만 strict `and`에는 전달하지 않는다. 이후 assignment,
exclusive borrow, escape, capture, consume 또는 mutate 가능한 call이
있으면 해당 stable place fact를 kill한다. join에서는 모든 incoming
edge에 공통인 fact만 남긴다.

미니 사례로 immutable local `value`를 검사한 직후에는 Int operation을
쓸 수 있지만, alias를 통해 value를 바꿀 수 있는 호출 뒤에는 재검사가
필요하다. 흔한 오해는 변수 철자가 같으면 stable place도 같거나
`is`가 class hierarchy reflection을 수행한다는 생각이다. 현행 `is`는
저장된 closed-Union injection identity를 한 번 읽을 뿐 provider lookup이나
subclass search를 하지 않는다.

`is`는 값을 바인딩하지 않고 Bool과 edge fact만 필요할 때 적합하다.
alternative payload를 이름으로 사용해야 하면 typed pattern이 더
직접적이다. 검사 직후 mutation이 예상되면 좁힘을 오래 보존하려 하기보다
성공 payload를 immutable local로 binding해 책임을 분리한다.

진단을 설명할 때도 “타입이 틀렸다”로 끝내지 말고 closed Union owner,
target alternative, stable-place 유지 여부 중 어느 조건이 실패했는지
적는다.

## 7. 허용·거부·경계 사례

일반 runtime type test, Union 전체 target, comparison chain 참여는
현행 `is` 계약이 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: CLOSED_UNION_TYPE_TEST_* -->
```deeplus
private def invalidPlain(value: Int) -> Bool = {
    return value is Int
}

private def invalidTarget(value: TextOrNumber) -> Bool = {
    return value is TextOrNumber
}

private def invalidChain(value: TextOrNumber) -> Bool = {
    return value is Int == true
}
```

또한 `var value`를 좁힌 뒤 assignment, alias mutation, exclusive borrow,
escape/capture, consume 또는 value를 바꿀 수 있는 call을 통과하면
이전 fact는 제거된다. 그 뒤 Int operation을 쓰려면 다시 검사해야 한다.

## 8. 다른 기능과의 연결

Enum case pattern도 같은 `Phi`에 case fact를 남긴다. refinement는 허용된
inline R0 predicate와 검증된 `GuardSummaryV1` direct truth-test에서
유한 fact를 더할 수 있다. ordinary Bool 함수, summary 없는 guard,
stored Bool과 unstable actual은 opaque하다.
MIR은 discrimination과 binding/move commit 순서를 보존한다.

## 9. Deeplus다운 작성 관례

- 값을 써야 하면 `is`만 반복하기보다 typed pattern으로 이름을 연다.
- sequential dependency에는 `and then`/`otherwise`를 분명히 쓴다.
- mutable subject를 좁힌 뒤 effectful call을 사이에 끼우지 않는다.
- proof가 kill된 지점 뒤에서는 재검사한다.
- `is`를 Java/C#식 open-world runtime type test처럼 사용하지 않는다.

## 10. 연습 문제

1. **따라 하기:** `Int | String`에서 `!is Int`로 text alternative를
   판별하는 순수 함수를 작성한다.
2. **빈칸 완성:** `value is Int ___ value > 0`에서 true-edge fact를
   오른쪽에 전달하는 operator를 채운다.
3. **스스로 설계하기:** mutable Union 값의 fact가 assignment 때문에
   사라지는 예와, 재검사해 안전해지는 예를 나란히 작성한다.

## 11. 빠른 복습

- declared type과 flow fact는 같은 것이 아니다.
- `is`/`!is`는 closed Union exact alternative에만 적용한다.
- sequential Bool operator만 오른쪽에 edge fact를 전달한다.
- stable place가 깨지면 proof도 제거된다.

## 12. 정본 근거와 다음 장

- [refinement와 flow proof](../../grammar-reference/04-types-generics-and-refinement.md)
- [closed Union operator](../../grammar-reference/08-expressions-and-operators.md)
- [narrowing coherence 계약](../../../spec/contracts/type-refinement-narrowing-coherence.json)

다음은 [generic, variance와 `where`](04-04-generics-variance-where.md)에서
타입 책임을 여러 타입에 걸쳐 일반화한다.
