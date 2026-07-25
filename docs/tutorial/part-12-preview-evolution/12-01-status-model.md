# 12-01 — 상태 모델: 정본, gate, 설계 probe, recovery

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`

이 장은 서로 다른 상태를 나란히 비교한다. Current/Stable은 현행 언어
설계 authority, Preview Gated는 명시적 source gate가 있는 제한 표면,
Preview Design은 `NONACTIVATABLE`, Recovery는 admitted AST/HIR/MIR을
만들지 않는 이행 진단이다. 어느 상태도 제품 PASS를 뜻하지 않는다.

## 2. 학습 목표

- language status와 product evidence를 서로 다른 축으로 읽는다.
- source가 어느 admission route를 택하는지 판정한다.
- Preview Design과 Recovery를 현행 대안처럼 오해하지 않는다.
- 제안 검토에서 authority, dependency, diagnostic, activation 조건을
  기록한다.

## 3. 선수 지식

source root, parser admission, AST/HIR/MIR, diagnostic의 기본 뜻을 알고
있어야 한다. Part 11의 authority와 lowering 경계를 먼저 읽으면 좋다.

## 4. 문제에서 출발하기

문서에 코드가 있다고 해서 모두 실행 가능한 예제는 아니다. 다음 네
문장은 서로 다른 주장이다.

1. “이 문법은 current design이다.”
2. “이 문법은 명시적 Preview gate 아래에서만 admitted된다.”
3. “이 표면은 설계 검토를 위해 정확히 적어 둔 probe다.”
4. “이 옛 표면은 더 이상 admitted되지 않지만 이행 진단은 제공한다.”

상태를 생략하면 독자는 proposal을 Stable로, recovery spelling을 호환
별칭으로, static validation을 runtime PASS로 오해하기 쉽다.

## 5. 핵심 모델

상태는 두 축으로 읽는다.

| 축 | 질문 | 대표 값 |
|---|---|---|
| language admission | parser/checker가 어떤 authority로 받는가? | Current, Preview Gated, nonactivatable, recovery-only |
| product evidence | 실제 compiler/runtime/tooling/target 실행 receipt가 있는가? | 현재 `15/15 NOT_RUN` |

상태별 route는 다음과 같다.

- `CURRENT_DESIGN_PRODUCT_NOT_RUN`: current pointer와 정본 계약이 선택한
  언어 설계. 구현·실행 완료를 뜻하지 않는다.
- `PREVIEW_GATED_PRODUCT_NOT_RUN`: registry가 허용한 exact feature ID를
  source root `#preview(...)`에서 명시해야 한다.
- `PREVIEW_DESIGN_NONACTIVATABLE`: gate를 적어도 켤 수 없다. candidate
  syntax는 expected reject probe다.
- `RECOVERY_ONLY`: scanner/parser가 더 나은 진단을 위해 알아볼 수 있지만
  admitted AST/HIR/MIR/API residue를 만들지 않는다.
- `MIXED_STATUS`: 한 문서가 여러 상태를 다루므로 각 예제에서 다시
  surface를 표시한다.

## 6. 단계별 예제

첫째, current Enum과 exhaustive match는 별도 gate가 없다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private enum LoadState {
    Idle
    Loading
    Failed(message: String)
}

def label(state: LoadState) -> String = {
    return @match state {
        ::Idle => "idle"
        ::Loading => "loading"
        ::Failed(message) => message
    }
}
```

이 예제의 `CURRENT`는 exhaustiveness와 payload binding의 설계 authority를
말한다. 실제 compiler가 이 파일을 실행했다는 receipt는 아니다.

둘째, Recovery-only 표면은 current alias가 아니다.

<!-- deeplus-example: illustrative; surface: RECOVERY_ONLY; product: NOT_RUN; expected: REJECT -->
```deeplus
// expected diagnostic family: NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE
let missing = null
```

도구는 `Option::none`을 안내할 수 있지만 `null`을 몰래 admitted node로
바꾸거나 HIR에 nullable value로 남겨서는 안 된다.

셋째, Preview Design은 gate 후보처럼 보여도 활성화 route가 없다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: enum_case_display_mapping_preview_design
private enum Status {
    Ready ~> "ready"
    Busy ~> "busy"
}
```

## 7. 허용·거부·경계 사례

허용: current Option을 명시적으로 match한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let city = @match address {
    ::some(value) => value.city
    ::none => "unknown"
}
```

거부: Preview Design ID를 `#preview`에 넣어 활성화하려 한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
#preview(nullsafe_control)
let city = user?.address?.city
```

`nullsafe_control`은 registry의 Preview Design이며 source gate route가
없다. 알려진 이름이라는 사실과 activatable이라는 사실은 다르다.

경계: Recovery scanner가 옛 토큰을 알아보는 것은 formatter가 그것을
보존하거나 자동 rewrite해도 된다는 뜻이 아니다. rewrite가 의미를
선택한다면 migration inventory와 사용자 선택이 먼저다.

## 8. 다른 기능과의 연결

status는 문법 분류에만 머물지 않는다. HIR-H1 verifier는 admitted surface의
identity, type, responsibility, effect를 닫아야 한다. Recovery node나
nonactivatable proposal이 executable HIR로 내려가면 authority leak다.
MIR/backend는 status를 재해석해 숨은 activation을 할 수 없다.

### 판정 추적과 흔한 오해

코드 조각을 만나면 exact feature identity를 찾고, registry status와
source activation route를 확인한 뒤, 예제 metadata의 surface와 현재
대안을 대조한다. Current면 정본 책임을, Preview Gated면 gate closure를,
Preview Design이면 expected reject와 미해결 질문을, Recovery면 전용
진단과 residue zero를 기록한다. 마지막 product evidence 열은 네 경우
모두 별도로 판정한다.

흔한 오해는 Stable을 “구현·실행 완료”, registry에 이름이 있음을
“gate 가능”, recovery recognition을 “호환 alias”로 읽는 것이다. 미니
사례에서 `nullsafe_control`은 알려진 exact ID지만 nonactivatable이므로
`#preview`에 적을 수 없다. 반면 gated NumericArray power는 exact gate가
있어도 target product PASS를 만들지는 않는다.

## 9. Deeplus다운 작성 관례

- 예제 바로 앞에 `surface`와 `product: NOT_RUN`을 표시한다.
- “Stable” 뒤에 “구현 완료”를 암시하는 표현을 붙이지 않는다.
- proposal에는 exact feature ID, 상태, activation route와 현행 대안을
  함께 적는다.
- Recovery 예제에는 expected reject diagnostic family를 적는다.
- 하나의 코드 블록에서 Current와 Preview Design 표면을 섞지 않는다.

## 10. 연습 문제

1. **그대로 따라 하기:** 위 `LoadState` 예제를 복사하고 각 줄의 surface
   상태와 product evidence 상태를 두 문장으로 설명하라.
2. **빈칸 채우기:** `null` recovery probe의 current 대안을
   `Option::____`로 완성하고, recovery token이 HIR에 남아서는 안 되는
   이유를 적어라.
3. **스스로 설계하기:** 가상의 새 기능 한 개에 대해 feature ID, status,
   activation route, dependencies, expected reject, current alternative,
   필요한 execution receipt를 포함한 검토 카드를 작성하라.

## 11. 빠른 복습

- language admission과 product evidence는 독립 축이다.
- Preview Design은 `NONACTIVATABLE`이며 `#preview`로 켤 수 없다.
- Recovery는 진단용 인식이지 compatibility admission이 아니다.
- current Stable도 현재 product `15/15 NOT_RUN`을 바꾸지 않는다.

## 12. 정본 근거와 다음 장

- [상태와 fence](../../grammar-reference/15-preview-recovery-and-removed-surfaces.md)
- [current pointer](../../../current/current-pointer.json)
- [implementation status](../../../current/implementation-status.yaml)
- [feature gate registry](../../../spec/features/gates.json)

다음 장에서는 실제 source gate가 존재하는 정확히 세 기능만 분리해
읽는다.
