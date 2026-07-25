# 12-04 — Preview Design: 컬렉션, context와 제어

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`
>
> 미니 범례: `CURRENT`는 named adapter·Option match 같은 현행 대안,
> `PREVIEW_DESIGN_NONACTIVATABLE`은 아직 선택되지 않은 surface probe다.
> 어느 예제도 product PASS를 뜻하지 않는다.

이 장의 여덟 feature는 모두 설계 검토용이며 source activation route가
없다. candidate spelling은 expected reject probe이고, exact spelling이
미선정인 항목은 current explicit alternative만 보여 준다. 예제나 schema가
있다는 사실은 parser/checker/runtime/tooling 구현을 뜻하지 않는다.

## 2. 학습 목표

- 컬렉션 shape와 broadcast 책임을 surface sugar와 분리한다.
- context parameter와 ordinary value argument의 정적 역할을 구분한다.
- snapshot/view, immutable-first ownership proposal의 lifetime 질문을
  세운다.
- literal-shaped type와 null-safe control이 숨길 수 있는 정보를 찾는다.

## 3. 선수 지식

1-based indexing, array와 NumericArray의 차이, named/context argument,
Option과 flow narrowing, owner/borrow/view 책임을 알고 있어야 한다.

## 4. 문제에서 출발하기

컬렉션과 제어 sugar는 짧지만 많은 결정을 숨긴다. `matrix + row`가
broadcast라면 어느 axis를 늘리고 mismatch는 언제 거부하는가? snapshot은
복사인가 view인가? `user?.address`가 있다면 subject는 몇 번 평가되고
어느 `Option` layer가 열리는가? 이 질문이 닫히지 않은 상태에서 기호만
고르면 backend나 formatter가 의미 owner가 된다.

## 5. 핵심 모델

여덟 exact feature를 네 쌍으로 읽는다.

| 문제군 | exact feature ID | 닫아야 할 핵심 |
|---|---|---|
| context 표면 | `contextual_operation_anchor_dmad`, `explicit_context_argument_ampersand_spelling` | parameter role, call binding, `&` polarity 충돌 |
| collection shape | `explicit_broadcast_marker_msp`, `literal_shaped_collection_type_surface_preview_design` | axis/shape proof, element type, rank, runtime check |
| record/ownership view | `literal_shaped_closed_record_type_surface_preview_design`, `immutable_first_collection_ownership_preview_design`, `freeze_snapshot_view_responsibility_preview_design` | row closure, alias/lifetime, copy/view/freeze, mutation visibility |
| control sugar | `nullsafe_control` | exact `Option` layer, one evaluation, type/effect/ownership join |

모두 `PREVIEW_DESIGN/nonactivatable`이다. 특히 과거의 일반화된 `&expr`
아이디어는 NumericArray `&` polarity나 borrow처럼 보이는 surface와
충돌할 수 있으므로 토큰 모양만으로 owner를 고르지 않는다.

## 6. 단계별 예제

### 1단계: context 역할을 current declaration과 call에 드러낸다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def format(value: Float64, context pattern: FormatPattern) -> String = {
    return pattern ~ render value
}

let text = format(3.14, context FormatPattern!("{:.2f}"))
```

`context`는 ordinary positional argument를 몰래 ambient lookup으로 바꾸는
표식이 아니다. declaration의 parameter role과 call-site binding이
대응해야 한다. `explicit_context_argument_ampersand_spelling`은 이
current form을 `&` spelling으로 교체한 authority가 아니다.

### 2단계: broadcast를 named adapter로 명시한다

explicit broadcast marker의 exact successor syntax는 선택되지 않았다.
current 대안은 axis와 target shape를 API 이름과 인자로 드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let expandedRow = expandRow(row, columns: matrix.columns)
let result = matrix + expandedRow
```

첫 유효 index가 `1`이라는 current law와 shape adaptation은 서로 다른
책임이다. broadcast가 도입되더라도 `0` 기반 indexing으로 바뀌거나
shape mismatch가 padding으로 fallback해서는 안 된다.

### 3단계: null-safe 요구를 current Option match로 표현한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let city = @match userAddress {
    ::some(address) => address.city
    ::none => "unknown"
}
```

명시적 match는 어느 layer를 열고, 어떤 branch에서 payload를
borrow/move하며, fallback effect가 언제 실행되는지 보여 준다.

candidate optional chaining은 현행 프로그램이 아니다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: nullsafe_control
let city = user?.address?.city
```

Deeplus에는 ambient nullable type이나 current `null` value가 없다.
proposal이 ratify되려면 exact `Option<T>` 입력, nested layer, one-evaluation
lowering과 branch join을 먼저 닫아야 한다.

## 7. 허용·거부·경계 사례

허용: 1-based index와 실패 channel을 명시한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let first = values[1]
let section = values[2..4]
```

거부: explicit broadcast marker가 아직 없는데 `&`가 axis를 뜻한다고
추측한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: explicit_broadcast_marker_msp
let result = matrix + &row
```

이 spelling은 선택된 current/Preview Gated surface가 아니다. parser가
context anchor나 broadcast로 임의 recovery admission해서는 안 된다.

경계: freeze/snapshot/view를 하나의 단어로 합치면 다음 차이가 사라진다.

- freeze: 같은 identity의 mutation 권한을 닫는가?
- snapshot: 특정 시점 값을 복제해 새 owner를 만드는가?
- view: 원 owner에 lifetime으로 묶인 읽기 창인가?

`freeze_snapshot_view_responsibility_preview_design`은 이 세 책임을
분리하기 위한 검토 항목이며, current collection을 immutable-first로
자동 재해석하지 않는다.

## 8. 다른 기능과의 연결

literal-shaped collection/record type은 pattern destructuring, exhaustive
row closure, serialization schema와 이어진다. source literal 모양만으로
nominal identity나 ABI layout을 발명해서는 안 된다. broadcast와 pointwise
operator는 fixed-glyph owner, shape algebra, exponent/element failure와
결합한다. null-safe control은 Option narrowing, ownership/effect/error join,
cleanup과 연결된다.

HIR-H1은 선택된 context binding, shape proof, index normalization, view
responsibility와 branch join을 닫아야 한다. MIR은 이 결정을 다시
추론하거나 hidden second evaluation을 만들 수 없다.

### 판정 추적과 흔한 오해

collection proposal은 element type만 보지 않고 rank, axis, extent,
broadcast proof와 mismatch terminal을 적는다. view/snapshot proposal은
copy 여부, owner, lifetime과 mutation visibility를 닫는다. control sugar는
subject 단일 평가, 정확한 Option layer, branch type/effect/ownership join을
검사한다. 이 책임을 named current 대안과 candidate probe에 같은 표로
적어 차이를 비교한다.

흔한 오해는 짧은 표면이 기존 helper의 단순 별칭이라는 생각이다.
`expandRow`는 axis와 extent를 명시하지만 미선정 broadcast marker를
활성화하지 않는다. current Option match도 null-safe chain의 evaluation
law를 자동 승인하지 않는다. 첫 index가 `1`이라는 current law 역시
broadcast나 shaped literal proposal 때문에 바뀌지 않는다.

## 9. Deeplus다운 작성 관례

- shape adaptation은 named adapter와 target axis/extent로 드러낸다.
- index 예제는 첫 유효 위치 `1`을 사용한다.
- context role은 declaration과 call site 양쪽에 쓴다.
- snapshot, freeze, view를 동의어로 쓰지 않는다.
- absence는 `Option`과 exhaustive match로 표현한다.
- `array`와 `case`는 ordinary identifier이며 keyword처럼 피하지 않는다.
- raw text가 필요하면 current `#raw"..."` spelling을 쓴다.

## 10. 연습 문제

1. **그대로 따라 하기:** `format` 예제를 옮겨 적고 ordinary value
   argument와 context argument가 binding되는 위치를 표시하라.
2. **빈칸 채우기:** 1-based section 예제 `values[____..____]`에 두 번째부터
   네 번째 element를 넣고, 0을 사용했을 때 필요한 boundary diagnostic을
   설명하라.
3. **스스로 설계하기:** snapshot/view API 하나를 제안하지 말고 먼저
   identity, owner, lifetime, mutation visibility, cleanup, HIR residue,
   positive/negative/boundary test로 구성된 책임 표를 작성하라.

## 11. 빠른 복습

- 여덟 기능은 모두 `NONACTIVATABLE`이다.
- context, broadcast, borrow가 비슷한 기호를 공유해도 같은 owner가 아니다.
- shape와 1-based indexing은 별도 법칙이다.
- snapshot/freeze/view는 identity·ownership 책임이 다르다.
- null-safe sugar는 Option layer와 평가 횟수를 숨겨서는 안 된다.

## 12. 정본 근거와 다음 장

- [Preview Design — 컬렉션·context·제어](../../grammar-reference/22-preview-design-collections-context-and-control.md)
- [인덱싱·연산자 계약](../../../spec/contracts/value-operator-indexing-coherence.json)
- [type/flow/callable 계약](../../../spec/contracts/type-flow-callable-coherence.json)
- [문법 명세](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 async callable, observation, coroutine group, FFI/runtime
proposal과 MIR-X1 draft를 current backend authority와 분리한다.
