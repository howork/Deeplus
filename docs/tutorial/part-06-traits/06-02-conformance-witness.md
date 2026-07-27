# 6.2 Conformance와 witness

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

명시적 `conformance`, coherent evidence와 witness call은 현행 설계다.
future `VIA`/`AUTO` provider route나 specialization을 현재 소문자 `via`와
혼동하지 않는다.

## 2. 학습 목표

- conformance declaration을 작성한다.
- Class method와 Trait witness implementation을 구분한다.
- ground conformance가 유일해야 하는 이유를 설명한다.
- structural shape, extension, subclassing이 evidence를 만들지 않음을
  확인한다.

## 3. 선수 지식

Trait requirement, Class/data class, generic `where` clause를 알고 있어야
한다.

## 4. 문제에서 출발하기

`Logger`에 `display()`라는 메서드가 있어도 그것이 `Display`의 error,
effect, ownership과 law를 만족한다고 자동으로 결론낼 수 없다.
Deeplus는 exact target·Trait pair에 conformance를 선언하고 하나의
witness를 선택한다.

## 5. 핵심 모델

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
conformance Target conforms Trait { ... }
```

선택은 normalized target, instantiated Trait와 coherence authority에
대해 유일해야 한다. declaration spelling, alias, source/import/link order,
expected return type이 winner가 아니다.

`as name`은 conformance 이름, 소문자 `via path`는 현재 route다. 같은 ground
conformance를 별개 의미 evidence로 복제할 수 없다. selected
`ConformanceId`, `TraitWitnessId`, `RequirementId`, implementation과
responsibility는 HIR/API에 고정되어 MIR/runtime이 다시 검색하지 않는다.

## 6. 단계별 예제

### 깊이 읽기: evidence 선택과 coherence

conformance는 target의 method 목록을 포장한 표가 아니라 “이 exact
target이 이 instantiated Trait를 만족한다”는 명목 evidence다. checker는
alias를 정규화한 target, generic argument가 적용된 Trait, declaration
authority를 결합해 `ConformanceId`와 `TraitWitnessId`를 결정한다. 같은
ground pair에 두 winner가 남으면 source order로 고르지 않고 ambiguity를
terminal로 처리한다.

판정 순서는 owner admission, requirement completeness, signature와
responsibility 일치, overlap/coherence, route availability, 최종 evidence
binding이다. 비활성 `AUTO`/`VIA`를 가져오지 않는다. 현행 소문자
`via`는 이미 선언된 route spelling이며 fallback search가 아니다.

generic `render<T>`에서 `T = UserId`가 정해지는 trace를 보자. checker는
exact evidence를 선택하고 requirement implementation과 associated
binding을 HIR에 기록한다. MIR call에는 선택된 witness identity가
전달되며 runtime은 import를 다시 훑거나 같은 이름 method를 duck
typing하지 않는다.

extension에 맞는 method가 있으면 conformance를 대신한다는 생각은 흔한
오해다. extension은 lexical candidate를 주지만 evidence를 만들지
않는다. 다른 package의 동일 ground conformance도 더 가까운 import라는
이유로 승자가 되지 않는다. 하나로 닫히지 않으면 선언 경계를 고친다.

선택 trace는 target type과 instantiated Trait를 정규화하는 데서
시작한다. checker는 그 exact ground pair에 허용된 conformance 후보를
모으고, requirement 전체와 implementation responsibility를 대조한다.
후보가 하나면 `TraitWitnessId`를 호출에 고정하고, 없으면 missing
evidence, 둘 이상이면 ambiguity로 끝낸다. import 순서나 우연한 method
이름으로 승자를 만들지 않는다.

성공한 witness는 generic 경계 안에서 재검색되는 문자열 표가 아니다.
lowering은 선택 identity를 보존하고 receiver·argument owner, error와
effect를 requirement대로 전달한다. structural duck typing, extension,
child-local 대체 evidence가 같은 결과 문자열을 만들더라도 이 channel을
대체하지 않는다. 이 설명은 열린 TCC P1을 닫거나 successor route를
활성화하는 실행 증거가 아니다.

### 6.1 UserId의 Display evidence

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public data class UserId(+let raw: Int)

public trait Display {
    +def display+() -> String
        throws Never
        effects {}
}

public conformance UserId conforms Display {
    +def display+() -> String
        throws Never
        effects {}
    = {
        return "UserId(${self.raw})"
    }
}

let id = UserId${ raw: 13 }
let text = id ~ display
```

conformance body의 method marker는 Trait witness slot을 구현한다. data class
자체의 member dispatch와 다른 identity다.

### 6.2 generic 경계에서 evidence 요구

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def render<T>(borrow value: T) -> String
    where T conforms Display
= {
    return value ~ display
}

let label = render(id)
```

`render`는 아무 타입이나 받은 뒤 runtime reflection을 하지 않는다.
call admission 때 `T conforms Display` evidence와 substitution이 하나로
닫힌다.

### 6.3 explicit witness channel

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def sort<T>(xs: List<T>, using order: witness Ord<T>) -> List<T> = {
    return stableSort(xs, using order)
}

def ordered(using intOrder: witness Ord<Int>) -> List<Int> = {
    return sort([3, 1, 2], using intOrder)
}
```

`using`은 ordinary runtime value나 named payload가 아니라 non-forgeable,
borrowed, nonescaping evidence channel이다.

## 7. 허용·거부·경계 사례

허용:

- exact requirement signature를 구현하는 conformance
- coherent generic witness selection
- explicit `using evidence`
- current lowercase `via`

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN; product: NOT_RUN -->
```deeplus
public class Logger {
    +def display.() -> String = {
        return "logger"
    }
}

let text = render(Logger!())
// STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN
```

이름과 반환 타입이 닮아도 explicit conformance가 없다. extension 역시
`EXTENSION_AUTO_WITNESS_FORBIDDEN`이며 subclassing도 unrelated Trait
evidence를 상속 합성하지 않는다.

## 8. 다른 기능과의 연결

- operator fixed glyph는 left owner package의 `DIRECT_GLOBAL` conformance
  하나만 선택한다.
- `<T as Trait>::item`은 selected conformance를 통해 associated binding을
  찾는다.
- Facet은 borrowed Trait evidence를 package하지만 새 conformance를
  만들지 않는다.
- public API digest는 witness와 ownership/effect/error residue를 보존한다.

## 9. Deeplus다운 작성 관례

- capability 채택을 explicit conformance declaration으로 눈에 보이게 한다.
- generic API의 `where`에 필요한 최소 Trait만 쓴다.
- witness ambiguity를 import order나 우선순위로 해결하지 않는다.
- runtime provider가 필요하면 conformance가 아니라 명시적 service value로
  모델링한다.

## 10. 연습 문제

1. **복사:** `OrderId`가 `Display`를 만족하는 conformance를 작성하라.
2. **빈칸 완성:** `def renderAll<T>(values: List<T>) -> List<String>
   where T conforms ___`의 빈칸을 `Display`로 채우고 각 element 호출이
   같은 evidence를 쓰는 이유를 적어라.
3. **설계:** 두 package가 같은 foreign target/Trait conformance를
   선언하려는 상황에서 coherence owner를 어디에 둘지 제안하라.

## 11. 빠른 복습

- conformance는 explicit evidence다.
- ground selection은 하나여야 한다.
- structural shape와 extension은 witness가 아니다.
- `using`은 별도 evidence channel이다.
- runtime relookup/fallback은 없다.

## 12. 정본 근거와 다음 장

- [Trait/conformance 계약](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [호출과 witness channel](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [타입 시스템](../../../spec/types/type-system.md)
- [통합 예제](../../grammar-reference/24-integrated-worked-examples.md)

다음 장에서는 기존 타입에 lexical API를 더하되 witness는 만들지 않는
extension을 배운다.
