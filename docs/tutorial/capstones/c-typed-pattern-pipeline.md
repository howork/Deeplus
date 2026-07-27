# 종합 프로젝트 C — 타입 검증과 패턴 파이프라인

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 정적 의미는 현행 설계를 따르며 compiler·fixture·runtime 제품 실행은
> `NOT_RUN`이다.

## 1. 만들 것

문자열 또는 정수로 들어오는 raw 식별자를 검증해 도메인 식별자로
바꾸고, 결과를 Enum과 pattern으로 처리하는 파이프라인을 만든다.
목표는 Union, refinement, narrowing, `def#guard`, Enum, pattern이
서로 대신하는 기능이 아니라 서로 다른 단계의 증거 owner라는 점을
이해하는 것이다.

## 2. raw type와 도메인 type 분리

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::identity::pipeline

public type RawIdentifier = Int | String
public type PositiveId = Int where this > 0
public type NonEmptyText = String where this.length > 0

public enum ParsedId {
    numeric(PositiveId)
    symbolic(NonEmptyText)
}
```

Union은 값이 `Int` 또는 `String`이라는 닫힌 대안을 보존한다.
refinement는 각각의 기반 타입에 추가 predicate를 붙인다. Enum은
검증이 끝난 결과가 어느 도메인 case인지 명목 identity로 표현한다.

## 3. guard와 narrowing의 역할

`def#guard`의 순수·전체 Bool 계약은 재사용 가능한 판정을 만든다.
eligible body에서 검증한 `GuardSummaryV1`은 direct truth-test와 stable
actual에 branch-local narrowing fact를 만든다. exact refined value를
경계 밖에 보존하거나 상세 실패가 필요하면 checked refinement
conversion을 사용한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def#guard hasText(value: String) -> Bool = {
    return value.length > 0
}

public def parse(raw: RawIdentifier) -> Option<ParsedId>
    throws Never
    effects {}
= {{
    number: Int if number > 0 =>
        @match (number as? PositiveId) {
            ::some(valid) => ::some(ParsedId::numeric(valid))
            ::none => ::none
        }

    text: String if text.length > 0 =>
        @match (text as? NonEmptyText) {
            ::some(valid) => ::some(ParsedId::symbolic(valid))
            ::none => ::none
        }

    _ => ::none
}}
```

각 typed pattern은 Union injection identity를 확인한다. guard는
binding을 읽지만 실패하면 arm의 binding transaction을 commit하지
않는다. `as?`는 proof가 실패할 수 있음을 `Option`에 남긴다.

## 4. 소비 단계

검증 이후에는 raw Union을 반복해서 판정하지 않는다. `ParsedId`의
닫힌 case universe를 match한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def canonicalText(value: ParsedId) -> String
    throws Never
    effects {}
= {{
    ParsedId::numeric(number) => "id:${number}"
    ParsedId::symbolic(text)   => "name:${text}"
}}
```

새 case가 추가되면 exhaustive match가 검토 지점을 만든다. wildcard로
모든 미래 case를 숨기는 것보다 명시적 arm이 조기 오류 검출에 유리하다.

## 5. 잘못된 지름길

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
public def#guard isPositive(value: Int) -> Bool = {
    return value > 0
}

public def unsafeId(raw: Int) -> PositiveId = {
    if isPositive(raw) {
        return raw
    }
    return raw
}
```

두 branch를 구분한다. `isPositive(raw)` direct truth-test의 true edge에는
`raw > 0` fact가 있어 첫 반환을 증명할 수 있다. 그러나 false branch는
그 보완 fact만 가지므로 같은 raw 값을 `PositiveId`로 반환할 수 없다.
올바른 API는 failure를 `Option`/`Result`에 드러내거나 checked conversion을
사용한다.

## 6. stable place와 mutation

narrowing fact는 “한 번 검사했으니 영원히 참”인 메모가 아니다. 값이
다시 쓰일 수 있는 place라면 검사와 사용 사이의 mutation이 증거를
무효화할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
var raw: RawIdentifier = 7

if raw is Int {
    raw = "changed"
    // raw를 Int라고 가정하는 사용은 허용되지 않는다.
}
```

checker는 usable stable place와 control-flow edge를 기준으로 narrowing
fact를 추적해야 한다. 캡처, alias, `inout`, suspension도 같은 질문을
일으킨다.

## 7. 파이프라인 acceptance 표

| 입력 | Union 대안 | refinement | 결과 |
|---|---|---|---|
| `7` | `Int` | `> 0` 성공 | `ParsedId::numeric` |
| `0` | `Int` | 실패 | `Option::none` |
| `"deeplus"` | `String` | non-empty 성공 | `ParsedId::symbolic` |
| `""` | `String` | 실패 | `Option::none` |

이 표는 설계 기대이며 실행 영수증이 아니다. 실제 제품 test가 생길 때는
positive, negative, boundary, mutation, cross-module case를 각각
fixture로 만들어야 한다.

### 7.1 증거 장부를 작성하는 법

각 control-flow edge에는 “현재 usable type”만 적지 말고 그 판단을 만든
owner도 함께 적는다. 예를 들어 첫 arm의 guard true-edge는 다음 장부를
가진다.

| 증거 | owner | 유효 범위 | 무효화 조건 |
|---|---|---|---|
| `raw`의 `Int` injection | closed Union type test | arm probe와 성공 edge | 다른 alternative |
| `number` binding | pattern transaction | arm body | arm 실패/종료 |
| `number > 0` | inline guard predicate | guard true-edge | mutable place write |
| `PositiveId` | checked refinement conversion | 변환 결과 값 | proof 없는 새 값 |
| `numeric` case | `ParsedId` owner | 생성된 Enum 값 | 다른 VariantId |

이렇게 적으면 `hasText(text)`라는 guard 함수의 Bool 결과를
`NonEmptyText` proof로 오해하는 실수를 발견할 수 있다. guard의 callable
계약과 refinement construction authority는 별개다.

### 7.2 `Option`과 `Result` 선택

입력이 단순히 도메인에 속하지 않는 것이 정상적인 부재라면 `Option`이
간결하다. 사용자가 무엇을 고쳐야 하는지 알려야 하거나 여러 failure
원인을 보존해야 하면 `Result<ParsedId, error ParseError>`가 낫다.
parser resource가 실패할 수 있다면 throws/effect row도 별도로 남긴다.
세 채널을 하나의 `none`이나 빈 문자열로 합치지 않는다.

### 7.3 cross-module 경계

다른 Module에 `ParsedId`를 공개할 때는 raw Union과 내부 predicate
구현까지 노출할 필요는 없다. 대신 공개 constructor/parse signature,
Enum case visibility, error family, serialization mapping을 API digest에
고정한다. runtime tag나 serialization number가 `VariantId`를 대신하지
않으며 Module 버전이 바뀌어도 그 분리를 유지한다.

### 7.4 오류를 가장 가까운 경계에 남기기

문자열을 숫자로 해석하는 library가 아직 선택되지 않았다면
`Int::parse` 같은 이름을 튜토리얼 편의로 발명하지 않는다. caller가
typed parser callable을 주입하거나, raw text를 그대로 다음 boundary에
넘기고 그 Module이 parse/error policy를 소유하게 한다. 이렇게 하면
encoding, locale, 허용 radix, overflow, whitespace 정책이 보이지 않는
전역 기본값으로 굳지 않는다.

parse가 성공한 뒤에도 refinement와 domain construction은 별도 단계다.
예를 들어 text `"7"`의 parsing 성공은 `Int(7)`을 제공하지만
`PositiveId` proof나 `ParsedId::numeric` VariantId를 자동으로 만들지
않는다. 각 단계가 실패 원인을 보존하면 사용자는 “문법을 읽지 못함”,
“정수지만 범위 밖”, “도메인 case를 만들 수 없음”을 구분할 수 있다.
이 구분이 error type과 diagnostic의 primary owner를 결정한다.

## 8. 연습 문제

1. **따라 하기:** 입력 네 개가 어느 arm을 통과하는지 binding transaction
   단위로 추적하라.
2. **빈칸 완성:** `ParsedId`에 checksum을 가진 case를 추가하고 모든
   exhaustive match를 갱신하라.
3. **직접 설계:** 오류 이유를 보존하는 `Result<ParsedId, ParseError>`
   버전을 작성하라.
4. **경계 과제:** 검사 뒤 `await`가 들어가면 stable place 증거가
   유지되는 조건을 ownership 관점에서 설명하라.
5. **진단 과제:** refinement proof가 없는 반환, non-exhaustive match,
   effectful guard를 서로 다른 diagnostic family로 분류하라.

## 9. 완료 체크리스트

- [ ] Union, refinement, Enum의 identity 역할을 구분했다.
- [ ] `def#guard` narrowing에 summary/direct-test/stable-place 조건을 확인했다.
- [ ] 실패를 `Option` 또는 `Result`로 보존했다.
- [ ] pattern binding은 성공 edge에서만 commit된다.
- [ ] exhaustive match를 유지했다.
- [ ] product lane 상태는 `NOT_RUN`이다.

## 10. 정본 근거

- [타입 시스템 Part](../part-04-type-system/README.md)
- [Enum과 pattern Part](../part-05-data-modeling/README.md)
- `spec/contracts/type-refinement-narrowing-coherence.json`
- `spec/contracts/destructuring-pattern-matching-static-fixtures.json`
- `spec/patterns/pattern-lowering.json`
