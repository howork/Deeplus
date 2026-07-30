# 6.3 Extension과 named extension

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

named extension set/pack과 lexical activation은 현행 설계다. extension은
runtime plugin도, Class member 삽입도, Trait conformance도 아니다.

## 2. 학습 목표

- `extension T as name`을 선언한다.
- `use T::name`과 explicit selector를 구분한다.
- activation이 lexical compile-time frame임을 이해한다.
- extension이 private construction authority나 witness를 얻지 못함을
  설명한다.

## 3. 선수 지식

module qualified name `::`, message call `~`, nominal member와 conformance의
차이를 알아야 한다.

## 4. 문제에서 출발하기

단위 변환처럼 타입의 core 정의에 넣고 싶지는 않지만 특정 scope에서
읽기 좋은 API가 필요할 수 있다. 전역 monkey patch나 runtime registration은
의미를 import order에 의존하게 만든다. named extension은 owner identity와
activation scope를 명시한다.

## 5. 핵심 모델

```text
target type + extension set id + member id
```

extension function은 plain `def name`이며 Class dispatch marker나 Trait
witness marker를 자동으로 얻지 않는다. `use`/`import`는 compile-time
lexical frame을 열고 scope exit에서 닫는다. collision은 마지막 import가
이기는 방식이 아니라 ambiguity로 진단한다.

## 6. 단계별 예제

### 깊이 읽기: lexical capability와 nominal evidence 분리

extension은 기존 type의 stored representation이나 명목 identity를
바꾸지 않고 특정 lexical activation에서 callable candidate를 제공한다.
named extension은 그 candidate group에 explicit qualification identity를
준다. 이는 subclass slot, Trait witness, runtime service value와 각각
다른 resolution domain이다.

receiver type을 한 번 정한 뒤 scope에서 활성화된 exact extension set을
모은다. selector와 전체 callable signature를 대조하고 가장 구체적인
단 하나의 candidate가 있는지 확인한다. import·use·declaration·source
order는 ambiguity tie-break가 아니다. 둘이 동등하면 qualification을
쓰거나 activation 범위를 줄인다.

두 package가 `UserId.display()`를 제공하는 작은 trace에서 signature가
같고 둘 다 활성화됐다면 먼저 import된 쪽을 고르지 않는다.
`UserId::AuditFormatting::display`처럼 named extension을 한정하면 선택
identity가 명시된다. receiver와 argument는 ordinary call 평가 순서를
따르고 lexical activation 자체는 runtime effect를 만들지 않는다.

extension으로 private representation을 열거나 stored field를 추가할 수
있다는 생각은 흔한 오해다. visibility와 ownership을 우회하지 않으며
Trait requirement와 이름이 같아도 explicit conformance 없이 witness
call로 승격되지 않는다.

extension resolution은 “target에 method가 보인다”에서 끝나지 않는다.
먼저 lexical scope에서 활성화된 extension set을 확인하고, explicit
selector가 있으면 그 이름으로 candidate를 제한한 다음 exact receiver와
signature를 대조한다. 성공한 call은 그 lexical choice를 고정하지만
target type의 명목 정의나 Trait conformance table을 바꾸지는 않는다.

같은 이름을 가진 `ui`와 `storage` set이 있어도 import order로 하나를
고르지 않는다. selector가 빠져 모호하면 call site에서 보완하고,
foreign target에 편의 함수를 붙였다는 이유로 upstream owner fact나
witness를 생성하지 않는다. runtime locale, cache, I/O처럼 상태와
effect가 필요한 capability는 lexical sugar에 숨기지 않고 explicit
service 경계로 남긴다. 이렇게 하면 파일을 옮기거나 import를 정리해도
semantic evidence가 조용히 바뀌지 않는다.

작은 검토표에는 활성화된 set, explicit selector, receiver exact type,
선택 signature, call의 error/effect, 결과 owner를 순서대로 적는다.
selector를 제거했을 때 다른 후보가 생기거나 scope를 벗어났을 때 호출이
사라지는 것은 lexical capability의 정상 경계다. 이를 public nominal
API 안정성이나 동작의 전역 override로 문서화하지 않는다. extension
선택 실패는 원래 타입 정의를 고치지 않고 import/selector 또는 explicit
service 경계를 보완해 해결한다.

### 6.1 이름 붙인 단위 extension

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public extension Int as metric {
    +def m() -> Length = {
        return Length!(value: self, unit: Unit::meter)
    }
}

use Int::metric

let short = 3 ~ m
let explicit = 3 ~ Int::metric::m
```

두 호출은 같은 extension set/member identity를 가리킨다. explicit selector는
활성 extension이 많을 때 의도를 더 잘 드러낸다.

### 6.2 lexical scope에서만 활성화하기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def measure() -> Length = {
    use Int::metric
    let inside = 5 ~ m
    return inside
}

let outside = 5 ~ Int::metric::m
```

unqualified `m` lookup은 함수 scope를 벗어나지 않는다. qualified selector는
exact extension identity를 직접 지정한다.

### 6.3 extension과 Trait는 별개다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public extension UserId as audit {
    +def auditLabel() -> String = {
        return "user-id:${self.raw}"
    }
}

use UserId::audit
let label = id ~ auditLabel
```

이 선언은 `UserId conforms Display`를 만들지 않는다. audit API와 Display
witness는 서로 다른 capability다.

### 6.4 nominal member와 extension이 함께 맞을 때

ordinary selector에 적용 가능한 nominal member와 active extension
member가 동시에 있으면 Deeplus는 nominal을 우선하지 않는다.
`MEMBER_EXTENSION_COLLISION`으로 거부하고 selected candidate는 0개다.

```deeplus
use UserId::audit

// nominal auditLabel과 active extension auditLabel이 모두 맞으면 거부
let ambiguous = id ~ auditLabel

// exact extension domain을 고르면 cross-domain collision을 피한다.
let explicit = id ~ UserId::audit::auditLabel
```

import/use/declaration 순서와 중첩 깊이는 winner가 아니다. `import`는
이름 frame, `use`는 activation frame만 바꾸며 어느 쪽도 Trait witness를
만들지 않는다.

## 7. 허용·거부·경계 사례

허용:

- exact target과 set name이 있는 extension
- lexical `use`
- `Type::extension::member` explicit selector
- 여러 set을 서로 다른 이름으로 병존
- exact qualified extension selector로 cross-domain collision을 피하기

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: EXTENSION_AUTO_WITNESS_FORBIDDEN; product: NOT_RUN -->
```deeplus
public extension Logger as text {
    +def display() -> String = { return "logger" }
}

let label = render(Logger!())
// EXTENSION_AUTO_WITNESS_FORBIDDEN
```

extension이 nominal owner의 private constructor를 호출하면
`TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN`이다. extension 실패 뒤
nominal/Trait/provider domain으로 fallback하지 않는다.
nominal member와 active extension이 모두 적용 가능한 ordinary selector는
`MEMBER_EXTENSION_COLLISION`이며 import order로 해결하지 않는다.

## 8. 다른 기능과의 연결

- `receiver ~ Type::Extension::selector`는 message selector의 exact extension
  domain을 고른다.
- `Type::item`은 nominal type-side, `<T as Trait>::item`은 associated
  domain이며 extension과 다르다.
- extension pack은 여러 declaration을 묶지만 runtime load/unload owner가
  아니다.
- extension method는 arbitrary operator glyph를 만들지 않는다.

## 9. Deeplus다운 작성 관례

- extension set에 domain 의미가 드러나는 이름을 붙인다.
- 넓은 scope의 unqualified activation보다 좁은 scope 또는 explicit
  selector를 선호한다.
- core invariant나 private representation 접근이 필요하면 nominal owner에
  둔다.
- 계약 채택이 목적이면 extension이 아니라 explicit conformance를 쓴다.

## 10. 연습 문제

1. **복사:** `String as audit` extension에 `redacted()` 함수를 추가하라.
2. **빈칸 완성:** 같은 target의 두 set을
   `value ~ Target::___::render`와 `value ~ Target::___::render`로
   호출하도록 `ui`, `storage` 빈칸을 채워라.
3. **설계:** 날짜 formatting API가 extension인지 runtime locale service인지
   effect/authority/lifecycle을 기준으로 결정하라.

## 11. 빠른 복습

- extension은 이름 붙은 lexical API다.
- activation은 compile-time scope다.
- extension은 witness, subtype, storage를 만들지 않는다.
- collision은 import order로 해결하지 않는다.
- explicit selector는 fallback하지 않는다.

## 12. 정본 근거와 다음 장

- [Extension 문법과 resolution](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [호출·message selector](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [정확한 EBNF](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 정적 capability의 네 domain과 associated qualification을
구분한다.
