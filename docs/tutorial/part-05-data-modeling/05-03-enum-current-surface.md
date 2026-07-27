# 5.3 현행 Enum 표면

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

이 장은 **현재 Enum만** 설명한다. 현재 표면은 bare case, named·positional·
mixed payload, `::case`/`Enum::case`, 그리고 `.`, `+`, `*.`, `*+` member
reachability다. successor의 uniform payload와 final-dot-only member는
`PREVIEW_DESIGN_NONACTIVATABLE`이며 아래 positive 코드에 사용하지 않는다.

## 2. 학습 목표

- `case` keyword 없이 Enum case를 선언한다.
- expected owner shorthand와 explicit owner를 사용한다.
- case payload의 선언·값·Pattern plane을 구분한다.
- Enum source order와 serialization/raw/ordinal identity를 분리한다.
- 현재 Enum member marker를 정확히 읽는다.
- Stable declaration-order `Ord`, case Display와 exact subset을 사용한다.

## 3. 선수 지식

명목 타입, named/positional argument, Class dispatch marker를 알고 있어야
한다. pattern의 자세한 commit 규칙은 다음 두 장에서 배운다.

## 4. 문제에서 출발하기

문자열 `"ready"`와 `"failed"`는 오타를 막지 못하고 실패 이유가 필요한
상태를 안전하게 담기도 어렵다. Enum은 owner가 가능한 variant 우주를
닫고 각 case에 별도 `VariantId`를 준다.

## 5. 핵심 모델

```text
EnumId
 ├─ VariantId(ready)
 ├─ VariantId(running)
 └─ VariantId(failed)
```

기본 Enum의 선언 순서는 source presentation일 뿐 raw value, ordinal,
ABI, 우선순위, match winner가 아니다. `enum#increasing` 또는
`enum#decreasing`을 명시한 제한된 Enum만 별도의 semantic order vector를
얻는다. 이 vector도 raw/tag/layout/ABI가 아니다. case payload는 다음
세 plane을 가진다.

1. declaration: `failed(code: Int, String)`
2. value argument: `JobState::failed(code: 13, "disk")`
3. pattern: `::failed(code, message)`

세 plane은 비슷해도 별도 parser/checker owner다. 현행은 case마다 named,
positional, 그리고 한 case 안의 mixed field를 허용한다.

## 6. 단계별 예제

### 깊이 읽기: case·payload·표현 identity 분리

Enum을 읽을 때 선언 순서나 marker를 값의 모든 identity로 사용하면
안 된다. 의미 case는 `(EnumId, VariantId)`로 구분되고 declaration
order, serialization tag, runtime discriminant, raw/ABI 값은 별도
domain이다. 외부 tag를 바꾸는 작업과 의미 case를 바꾸는 작업은 서로
다른 호환성 검토를 요구한다.

case 판정은 owner를 찾는 데서 시작한다. expected type이 있으면
`::ready`, 멀거나 모호하면 `State::ready`로 owner를 명시한다. 이어
VariantId가 그 owner에 속하는지 확인하고 declaration payload의
arity·label·position을 expression 또는 Pattern payload와 대조한다.
마지막으로 child expression을 왼쪽부터 한 번씩 평가하고 case 값을
한 번 publish한다.

`State::failed(loadCode(), loadMessage())`에서 둘째 호출이 실패하는
trace를 보자. 첫 호출 결과에 resource가 있어도 `failed` 값은
publish되지 않고 formation plan이 임시 책임을 정리한다. Pattern에서도
case identity나 payload shape가 틀리면 guard를 실행하거나 binder를
commit하지 않는다.

현재 mixed payload와 네 member marker는 compatibility authority다.
이는 successor uniform payload나 final-dot-only 표면의 activation이
아니다. 새 API가 일관된 label 전략을 택할 수는 있지만 current 문법을
자동 rewrite하거나 기존 case 의미를 재해석할 수 없다. `case` keyword와
dot-prefixed shorthand를 되살리는 것도 같은 경계를 어긴다.

한 case Enum을 자동으로 wrapper로 바꾸는 것도 흔한 오해다. 한 case도
명목 case identity와 exhaustive boundary를 가질 수 있으며 formatter가
이 의미 선택을 대신하지 않는다.

### 6.1 bare case와 payload

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum JobState {
    ready
    running(worker: String)
    failed(code: Int, String)
}

let first: JobState = ::ready
let active = JobState::running(worker: "node-1")
```

`case ready`라고 쓰지 않는다. expected type이 있으면 `::ready`, 없거나
명확성을 높이고 싶으면 `JobState::ready`를 쓴다. mixed payload는 current
compatibility surface지만 새 API는 한 case 안에서 일관된 label 전략을
선택하는 편이 읽기 쉽다. 이는 successor 활성화가 아니라 작성 관례다.

### 6.2 case Pattern과 exhaustive value match

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def label(state: JobState) -> String = {
    return @match state {
        ::ready => "ready"
        ::running(worker) => "running:${worker}"
        ::failed(code, message) => "failed:${code}:${message}"
    }
}
```

세 VariantId를 모두 덮으므로 `otherwise` 없이 total하다. payload Pattern은
case identity가 맞은 뒤에만 probe binder를 만든다.

### 6.3 현재 Enum member marker

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum State {
    ready
    failed(reason: String)

    +def isReady.() -> Bool = {
        return self == ::ready
    }
}
```

앞의 `+`는 공개 member visibility다. 이름 뒤의 marker는 `. final`,
`+ open`, `*. override 후 close`, `*+ override 후 open`이다. marker는
case identity, raw value, ordinal 또는 Trait witness를 뜻하지 않는다.

### 6.4 declaration-order `Ord`

payload가 없고 비어 있지 않으며 generic이 아닌 Enum은 정확히 하나의
order role을 선택할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum#increasing Priority {
    low
    normal
    high
}
```

이 선언은 whole-Enum `Ord<Priority>` witness 하나를 만들고
`low < normal < high`의 semantic order를 고정한다. `#decreasing`이면
반대 방향이다. 같은 ground의 explicit `Ord`와 함께 둘 수 없고 payload
ordering, iteration, match priority, raw value 또는 comparison glyph의
새 dispatch route를 만들지 않는다. public order behavior가 있으므로
case reorder는 API compatibility 변경으로 검토한다.

### 6.5 case-owned Display mapping

case의 `~>`는 parsing·serialization·localization과 분리된 restricted
String template다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum Delivery {
    queued ~> "queued"
    moving(driver: String) ~> "moving: ${driver}"
    delivered ~> "delivered"
}
```

한 inhabitable case가 mapping을 가지면 모든 inhabitable case가 정확히
하나씩 가져야 한다. named payload는 read-only binder이고 interpolation
hole은 이미 선택 가능한 `Display` evidence만 사용한다. mapping은
payload를 move/mutate하거나 throw/suspend/spawn하지 않으며 fallback,
reverse parser, serialization tag나 hidden locale provider를 만들지
않는다.

### 6.6 exact-variant subset alias

payload 없는 same-owner case의 유한 부분집합은 Enum body의 associated
type으로 선언한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum Day {
    Mon
    Tue
    Wed
    Sat
    Sun

    +type Weekend = Sat | Sun
}
```

`Weekend` identity는 같은 `EnumId`, frozen `VariantId` set과 universe
digest로 정규화된다. 새 case, wrapper, storage, tag, allocation 또는
witness를 만들지 않는다. subset에서 owner `Day`로의 widening은
lossless지만 owner에서 subset으로의 narrowing은 `as?` 또는 pattern 같은
checked boundary를 요구한다. foreign owner case와 payload-bearing case는
subset member가 될 수 없다.

## 7. 허용·거부·경계 사례

허용:

- `public enum State { ready, failed }` 같은 한 줄 comma list
- layout body의 bare case
- `::ready`, `State::ready`
- payload가 있는 `State::failed(reason: "...")`
- 현재 네 member marker

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: ENUM_CASE_KEYWORD_NOT_CANONICAL; product: NOT_RUN -->
```deeplus
public enum State {
    case ready
}
// case는 keyword가 아니라 일반 식별자다.
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: DOT_ENUM_CASE_SHORTHAND_NOT_CURRENT; product: NOT_RUN -->
```deeplus
let state: State = .ready
// DOT_ENUM_CASE_SHORTHAND_NOT_CURRENT: ::ready 또는 State::ready 사용
```

경계:

- 한 case Enum은 허용하지만 rewrite/tooling advice를 만들지 않는다.
- empty Enum은 현행 source activation이 없다.
- source order를 raw/tag/ordinal로 사용하는 것은 거부한다.
- successor marker 자동 rewrite와 payload migration default는 없다.

## 8. 다른 기능과의 연결

Enum Pattern은 exhaustiveness와 flow narrowing을 제공한다. Enum conformance
witness는 case-local로 생기지 않으며 Trait 장의 coherence 규칙을 따른다.
직렬화 tag나 FFI discriminant가 필요하면 semantic `VariantId`와 별도
mapping을 선언해야 한다.

## 9. Deeplus다운 작성 관례

- 상태가 유한하고 payload가 case마다 다를 때 Enum을 쓴다.
- expected type이 멀리 있으면 explicit `Enum::case`를 쓴다.
- 새 case를 추가하면 match와 compatibility lane을 함께 검토한다.
- declaration order에 외부 의미를 싣지 않는다.
- current mixed payload를 보존하되 새 API에서는 사람에게 읽히는 일관된
  label 구성을 선택한다.

## 10. 연습 문제

1. **복사:** `JobState`에 payload 없는 `cancelled` case를 추가하라.
2. **빈칸 완성:** `::running(___) => "running:${___}"`의 두 빈칸에
   `worker`를 넣고, 같은 arm을 explicit `JobState::running`으로도 적어라.
3. **설계:** 결제 상태 Enum을 설계하되 declaration order와 외부
   serialization code를 분리하는 mapping 책임을 설명하라.

## 11. 빠른 복습

- Enum case는 bare identifier다.
- `case`와 `array`는 일반 식별자다.
- `::case`는 expected owner, `Enum::case`는 explicit owner를 쓴다.
- payload declaration/value/pattern plane은 서로 다르다.
- current와 nonactivatable successor를 섞지 않는다.
- declaration-order `Ord`, case Display와 exact subset은 Stable이지만
  successor uniform-payload/final-dot-only profile과는 별개다.

## 12. 정본 근거와 다음 장

- [Enum 정본 설명](../../../spec/language.md)
- [Enum 문법](../../../spec/grammar/deeplus.ebnf)
- [Enum·Record 레퍼런스](../../grammar-reference/07-enums-records-schemas-bitfields-and-units.md)
- [패턴 레퍼런스](../../grammar-reference/10-patterns-destructuring-and-matching.md)

다음 장에서는 Enum, Record, List와 closed Union을 Pattern으로 안전하게
여는 방법을 배운다.
