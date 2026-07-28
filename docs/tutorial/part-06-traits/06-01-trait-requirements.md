# 6.1 Trait 요구사항

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

Trait method, associated requirement, supertrait `derives`, 선언적 `law`는
현행 설계다. Class dispatch marker와 Trait witness marker는 glyph를
공유하지만 서로 다른 AST/identity domain이다.

## 2. 학습 목표

- Trait를 구조적 duck typing이 아닌 명시적 계약으로 이해한다.
- method와 associated type/value/function requirement를 구분한다.
- witness marker와 member visibility를 따로 읽는다.
- `law`가 실행 body나 witness 합성기가 아님을 설명한다.

## 3. 선수 지식

Class member의 `+` visibility와 `. + *. *+` dispatch marker를 알고 있어야
한다. generic `where T conforms Trait`는 이 부에서 반복해 사용한다.

## 4. 문제에서 출발하기

서로 다른 타입을 문자열로 표시하고 싶을 때 `display`라는 이름만
검색하면 우연한 메서드나 extension까지 후보가 된다. 새 import가 기존
코드의 의미를 바꿀 수도 있다. Trait는 요구사항 identity를 선언하고
conformance가 그 요구사항을 정확히 충족하도록 한다.

## 5. 핵심 모델

Trait item은 세 영역이다.

1. instance method requirement:
   `+def display+() -> String`
2. associated requirement:
   `type Item`, `let ::zero: T`, `def ::make()`
3. declarative `law`:
   순수 proposition metadata

Trait method 이름 뒤 marker는 witness slot kind다.

| marker | Trait slot 의미 |
|---|---|
| `.` | final/default witness slot |
| `+` | open witness slot |
| `*.` | inherited open slot을 override하고 닫음 |
| `*+` | inherited open slot을 override하고 열어 둠 |

앞의 `+/-/#`는 visibility다. 같은 `+`가 두 번 보여도 한 field로 합치지
않는다.

## 6. 단계별 예제

### 깊이 읽기: requirement는 이름이 아니라 전체 callable 계약

Trait requirement identity에는 method 이름만 들어가지 않는다. parameter
순서와 label, receiver와 ownership mode, generic 조건, return type,
throws와 effect row가 함께 참여한다. 이름과 결과가 같아 보여도 rhs를
consume하거나 I/O effect를 숨기면 다른 계약이다. generic caller는 이
전체 signature로 안전한 호출을 준비한다.

먼저 Trait owner와 requirement kind를 결정하고 exact signature를
정규화한다. associated type이나 value는 method slot과 섞지 않는다.
이어 law가 문서 계약인지 별도 proof surface가 필요한지 구분한다.
현재 law 설명은 임의 실행 block을 conformance body에 추가하는 권한이
아니다.

`Display::display`가 `throws Never effects {}`를 요구하는 작은 trace를
보자. target method가 String을 반환해도 logging I/O를 수행하면 effect
row가 다르다. checker는 이름을 보고 witness를 먼저 만든 뒤 effect를
지우지 않고, 전체 계약이 맞는 implementation만 slot에 결합한다.

default body가 있으면 모든 type이 자동으로 Trait를 만족한다는 생각은
흔한 오해다. default는 explicit conformance가 선택된 뒤 requirement
implementation을 제공할 수 있을 뿐 target/Trait 관계를 만들지 않는다.
requirement 선언만으로 runtime interface object가 생기지도 않는다.

요구사항을 검토할 때에는 이름만 대조하지 않는다. receiver mode, generic
parameter와 label, return identity, `throws`, `effects`, witness marker를
한 행으로 정규화해 implementation responsibility와 비교한다. associated
type·value·function은 instance member와 다른 identity 공간에 둔다.
law 문장은 이 비교가 지켜야 할 성질을 설명하지만 실행 body나 숨은
default implementation을 만들지 않는다. 어느 칸이 비어 있으면 “대충
같은 함수”로 수용하지 않고 정확한 계약을 먼저 보완한다.

### 6.1 작은 Display 계약

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait Display {
    +def display+() -> String
        throws Never
        effects {}
}

private def describe<T>(borrow value: T) -> String
    where T conforms Display
= {
    return value ~ display
}
```

`where`는 `T`에 exact `Display` conformance evidence가 필요함을 말한다.
호출 시 source/import order가 아니라 coherent witness identity가 선택된다.

### 6.2 associated type을 가진 Source

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait Source {
    type Item

    +def next+() -> <Self as Source>::Item?
        throws Never
        effects {}
}

private def first<S>(borrow source: S) -> <S as Source>::Item?
    where S conforms Source
= {
    return source ~ next
}
```

`Item`은 instance method가 아니며 witness marker를 갖지 않는다.
`<S as Source>::Item`은 exact Trait associated type projection이다.

### 6.3 law는 실행 코드가 아니다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait ReflexiveRelation {
    law Reflexive {
        requires true
        ensures true
        invariant 1 == 1
    }
}
```

`law`는 tooling이 property evidence와 연결할 선언적 metadata다. callable,
runtime branch, proof executor 또는 conformance method를 합성하지 않는다.

## 7. 허용·거부·경계 사례

허용:

- 명시적 method marker
- physical line에서 반복하는 `derives ParentTrait` supertrait
- associated type/value/function requirement
- restricted pure logic의 `law`

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: TRAIT_METHOD_MARKER_REQUIRED; product: NOT_RUN -->
```deeplus
public trait InvalidDisplay {
    +def display() -> String
}
// TRAIT_METHOD_MARKER_REQUIRED
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: LAW_BODY_ITEM_NOT_ADMITTED; product: NOT_RUN -->
```deeplus
public trait InvalidAudit {
    law BadLaw {
        print("not a proposition")
    }
}
// LAW_BODY_ITEM_NOT_ADMITTED
```

`law` 안의 mutation, I/O, await, spawn, throw, arbitrary call은 실행
statement이므로 허용되지 않는다.

## 8. 다른 기능과의 연결

- Trait requirement를 만족하는 것은 explicit conformance다.
- extension member 이름이 같아도 witness가 되지 않는다.
- associated selector는 명목 type-side, extension, runtime service와
  분리된다.
- fixed operator glyph는 아무 Trait method나 연결하지 않고 정해진 세
  Prelude Trait에만 연결된다.

## 9. Deeplus다운 작성 관례

- Trait는 작고 의미 있는 capability로 나눈다.
- method의 effect/error/ownership까지 계약 일부로 쓴다.
- associated item은 instance마다 달라지는 상태 대신 type/conformance
  수준에서 고정되는 정보에 사용한다.
- law는 사람이 읽을 법칙과 tooling evidence의 연결점으로 사용하고
  실행 검증인 것처럼 쓰지 않는다.

## 10. 연습 문제

1. **복사:** `Display`와 같은 형식으로 `Named` Trait를 작성하라.
2. **빈칸 완성:** `let ::empty: ___`의 타입 빈칸을 `Bool`로 채우고,
   instance method와 다른 identity를 갖는 이유를 한 문장으로 적어라.
3. **설계:** 로그 sink capability를 instance method, associated function,
   runtime service 중 어디에 둘지 수명과 상태를 기준으로 결정하라.

## 11. 빠른 복습

- Trait는 명시적 requirement identity다.
- visibility와 witness marker는 별도다.
- associated type은 method가 아니다.
- law는 nonexecutable metadata다.
- 제품 witness/runtime 지원은 `NOT_RUN`이다.

## 12. 정본 근거와 다음 장

- [Class·Trait 레퍼런스](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [Trait 문법](../../../spec/grammar/deeplus.ebnf)
- [타입 시스템](../../../spec/types/type-system.md)
- [언어 명세](../../../spec/language.md)

다음 장에서는 requirement를 실제 타입에 결합하는 conformance와 witness를
다룬다.
