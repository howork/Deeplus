# 6.4 Associated type과 명시적 qualification

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

`Type::item`, `Type::extension::item`, `<T as Trait>::item`의 분리와
Trait-qualified associated type/value/function lookup은 `STABLE_DESIGN`이다.
제품 실행은 여전히 `NOT_RUN`이다.

## 2. 학습 목표

- 네 capability domain을 구분한다.
- associated type/value/function을 명시적으로 선택한다.
- `<T as Trait>::Item::member`의 두 단계 lookup을 읽는다.
- implicit companion object와 `T::item` Trait search가 없는 이유를
  이해한다.

## 3. 선수 지식

Trait requirement, conformance, named extension, nominal type-side
`def ::name`을 알고 있어야 한다.

## 4. 문제에서 출발하기

generic `T`에 `Codec`과 `Storage` 두 Trait가 모두 `Format`을 선언하면
`T::Format`은 어느 requirement인지 알 수 없다. 현재 보이는 Trait가
하나라는 우연에 기대도 새 import가 의미를 바꿀 수 있다. Deeplus는
`<T as Trait>::item`으로 exact domain을 쓴다.

## 5. 핵심 모델

| domain | 표면 | owner |
|---|---|---|
| nominal type-side | `Type::item` | type body의 `let::`/`def::`, Enum case |
| named extension | `Type::extension::item` | exact extension set |
| Trait associated | `<T as Trait>::item` | selected conformance |
| runtime service | `service.item(...)` | 명시적 ordinary value |

type 문맥의 `<T as Trait>::Item`은 associated type, expression 문맥의
`::value`는 immutable associated value, call suffix가 있는 `::make()`는
associated function이다. kind가 맞지 않으면 다른 namespace로 fallback하지
않는다.

여기서 **associated projection**은 선택된 Trait conformance가 제공하는
type·value·function을 `<대상 as Trait>::항목`으로 정확히 꺼내는 한정
표현을 뜻한다.

## 6. 단계별 예제

### 깊이 읽기: projection 전에 evidence 고정

`T::Item`은 nominal type-side member인지 여러 Trait의 associated item인지
모호할 수 있다. Deeplus는 import 수에 따라 뜻이 바뀌는 것을 피하려고
`<T as Trait>::Item`에 target과 Trait owner를 모두 적는다. projection은
새 witness를 찾는 연산이 아니라 이미 선택된 conformance binding을
읽는 연산이다.

`T`의 canonical type identity와 Trait instantiation을 정규화하고 unique
conformance를 선택한다. 이어 item 이름과 kind를 확인한다. type 문맥에
value를 쓰거나 call 문맥에 associated type을 쓰면 다른 namespace에서
재시도하지 않고 kind mismatch로 거부한다.

`Codec`과 `Storage`가 모두 `Format`을 선언하는 trace에서
`<T as Codec>::Format`은 Codec witness의 binding만 읽고
`<T as Storage>::Format`은 별도 binding을 읽는다. 최종 type이 우연히
같아도 projection identity는 다르다. HIR은 target, Trait,
RequirementId와 witness를 모두 보존한다.

associated value를 companion object runtime singleton으로 보는 것은
흔한 오해다. nominal `Type::item`, named extension item, Trait associated
item, service value는 서로 다른 owner다. 정본 `::` qualification으로
경계를 드러낸다.

projection 판단은 이름 검색보다 evidence 선택이 먼저다. `<T as
StorageModel>::Format`은 `T`라는 타입과 `StorageModel` conformance를
정확히 고정한 뒤 그 witness가 제공하는 associated member를 읽는다.
같은 `T`가 `Codec::Format`도 제공하면 spelling이 같다는 이유로 identity를
합치지 않는다. qualification은 장황함이 아니라 owner를 드러내는
증거다.

generic 함수에서는 bound가 candidate universe를 제한하고 selected
witness가 projection의 source가 된다. associated value나 function도
같은 절차를 따르며 runtime global slot이나 companion object를 암시하지
않는다. per-type mutable cache, locale, clock처럼 상태·lifetime·effect가
필요한 항목은 associated static으로 숨기지 않고 Actor 또는 explicit
service가 소유한다. projection 실패는 fallback 이름 검색으로 회수하지
않으며, selected witness와 member identity를 diagnostic에 함께 남긴다.

호출 예를 추적할 때에는 generic argument 확정, bound 확인, conformance
선택, associated member projection, 실제 사용의 다섯 줄을 작성한다.
어느 단계에서든 identity가 둘이면 뒤 단계로 넘어가지 않는다. 특히
이름이 같은 두 `Format`을 결과 타입이 우연히 같다는 이유로 합치거나
package alias에 따라 owner를 바꾸지 않는다. qualification은 source와
diagnostic, HIR handoff에서 같은 witness를 가리켜야 한다.

### 6.1 associated type projection

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait StorageModel {
    type Key
}

public final class FileStore {
}

public type FileStore conforms StorageModel {
    type Key = Token
}

private let emptyKey =
    <FileStore as StorageModel>::Key::fromInt(0)
```

첫 `::Key`는 selected conformance의 associated type을 `Token`으로
정규화한다. 둘째 `::fromInt`는 그 결과 nominal 타입의 type-side function을
찾는다.

### 6.2 associated value와 function

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait DefaultToken {
    let ::code: Int
    def ::make() -> Token
        throws Never
        effects {}
}

public type Token conforms DefaultToken {
    let ::code = 0

    def ::make() -> Token
    = {
        return Token::fromInt(<Token as DefaultToken>::code)
    }
}

let code = <Token as DefaultToken>::code
let token = <Token as DefaultToken>::make()
```

associated immutable value는 const-evaluable/reproducible, deeply immutable
또는 Shareable, pure synchronous, resource-free인 최소 profile을 만족해야
한다.

### 6.3 generic 함수에서 exact Trait 고르기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def defaultCode<T>() -> Int
    where T conforms DefaultToken
= {
    return <T as DefaultToken>::code
}
```

`T::code`라고 줄이지 않는다. exact Trait requirement와 selected
conformance identity가 source에 남는다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION; product: NOT_RUN -->
```deeplus
private def implicitCode<T>() -> Int
    where T conforms DefaultToken
= {
    return T::code
}
// TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: COMPANION_OBJECT_NOT_CURRENT; product: NOT_RUN -->
```deeplus
companion Token {
    let cache: SharedCell<Int>
}
// COMPANION_OBJECT_NOT_CURRENT
```

mutable/cache/resource/ambient-authority associated value도
`ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED`다. 상태 있는 기능은
Actor, shared-state owner 또는 explicit service value로 둔다.

## 8. 다른 기능과의 연결

Trait-qualified lookup은 다음 일곱 축을 HIR/API residue에 묶는다:
`TraitId`, `RequirementId`, `ConformanceId`, `TraitWitnessId`,
`ImplementationId`, `SubstitutionId`, `ResponsibilityId`. MIR은 이 결정을
소비할 뿐 provider/registry를 재탐색하지 않는다.

nominal `def::`만 declaring owner의 private construction authority를 가질
수 있다. 외부 conformance의 associated function은 공개 nominal 경계를
거쳐야 한다.

## 9. Deeplus다운 작성 관례

- 정적 기능을 하나의 “companion” 상자에 몰아넣지 않는다.
- nominal, extension, Trait, runtime state 중 실제 owner를 먼저 선택한다.
- generic associated lookup은 항상 Trait를 적는다.
- 상태나 lifecycle을 숨겨야 하는 associated value 설계를 거부하고
  explicit service로 올린다.

## 10. 연습 문제

1. **복사:** `Source::Item`을 사용하는 `first<S>` 함수 signature를 작성하라.
2. **빈칸 완성:** `<T as ___>::Format`과 `<T as ___>::Format`의 두
   빈칸에 `StorageModel`, `Codec`을 넣어 서로 다른 projection을 완성하라.
3. **설계:** per-type cache를 associated value로 두지 않고 Actor/service로
   모델링하고 capability domain 표를 작성하라.

## 11. 빠른 복습

- `T::item`은 Trait를 검색하지 않는다.
- `<T as Trait>::item`은 exact selected conformance를 사용한다.
- associated type 뒤 nominal static lookup을 계속할 수 있다.
- type name은 runtime singleton value가 아니다.
- identity residue 일곱 축을 보존한다.

## 12. 정본 근거와 다음 장

- [Associated capability 레퍼런스](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [Companion coherence 계약](../../../spec/contracts/companion-capability-coherence.json)
- [문법](../../../spec/grammar/deeplus.dpg)

다음 장에서는 Trait conformance가 operator glyph에 연결될 수 있는 정확히
제한된 Stable 통로를 배운다.
