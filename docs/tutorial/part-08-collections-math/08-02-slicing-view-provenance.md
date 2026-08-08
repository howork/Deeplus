# 8.2 Slice, view, provenance

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

inclusive/half-open/open slice, `^`/`$` anchor, NumericArray axis wildcard와
owner-bounded `ReadonlyView`는 현행 설계다. mutable slice는 현행이 아니다.

## 2. 학습 목표

- inclusive `i..j`, half-open `i..<j`, open-bound slice를 구분한다.
- `^`와 `$`를 첫/마지막 coordinate anchor로 사용한다.
- view가 copy/rebase가 아님을 이해한다.
- provenance, lifetime, mutation 충돌을 설명한다.

## 3. 선수 지식

1-based index, owner와 borrow의 기초가 필요하다.

## 4. 문제에서 출발하기

`values[2..4]`를 새 List로 복사해 1부터 다시 세면 원본의 coordinate 3이
무엇이었는지 잃는다. Deeplus slice view는 source owner와 coordinate
mapping을 보존한다.

## 5. 핵심 모델

- `value[i..j]`: 양 끝 포함
- `value[i..<j]`: 끝 제외, canonical
- `value[..<j]`, `value[..j]`, `value[i..]`: 한쪽 경계를 연 slice
- `value[..]`: general full slice
- `^`: slice owner의 첫 coordinate
- `$`: 마지막 coordinate
- `*`: 허용된 NumericArray axis 전체

ReadonlyView는 nonowning projection이다. copy, hidden allocation, rebase,
actor transfer를 자동 수행하지 않는다. source owner보다 오래 살 수 없고
충돌하는 mutation/move/drop과 함께 존재할 수 없다.

## 6. 단계별 예제

### 깊이 읽기: view는 값이 아니라 추적 가능한 projection이다

view의 의미는 element 목록만으로 설명되지 않는다. 최소한 source owner
identity, source logical domain, view에서 source로 가는 coordinate
mapping, 허용된 access mode, lifetime bound가 함께 있어야 한다.
`values[2..4]`가 `[20, 30, 40]`처럼 보이더라도 새 ordinary List와 같다고
가정하면 coordinate와 owner 정보를 잃는다. 이 장의 readonly view는
source의 2..4를 그대로 가리키며 allocation이나 1-based rebase를 숨기지
않는다.

판단 절차는 범위를 먼저 정규화하고 양 끝이 domain 안에 있는지 확인한
다음, source owner에 borrow 충돌이 없는지 검사하는 순서다. 성공하면
provenance가 붙은 view를 만들고, 실패하면 view를 전혀 만들지 않는다.
view가 살아 있는 동안 source를 충돌하게 mutate, move, drop하는 연산은
거부한다. task나 actor 경계를 넘기려면 view를 몰래 복사하는 대신
명시적으로 소유 값을 materialize하거나 더 긴 owner 계약을 설계한다.

`^`와 `$`는 정수 상수가 아니라 현재 slice owner의 첫 coordinate와 마지막
coordinate를 뜻한다. 따라서 bounded source에서는 `^`가 반드시 `1`인
것도 아니다. NumericArray의 `*`는 허용된 axis 전체를 선택하지만 rank와
남은 axis identity를 보존한다. 리뷰할 때에는 결과 값뿐 아니라
“누가 소유하고, 어느 coordinate를 유지하며, 언제 더는 사용할 수
없는가”를 한 문장으로 답할 수 있어야 한다.

open exclusive end는 마지막 coordinate에 1을 더한 정수로 만들지 않는다.
별도 boundary identity가 one-past-last를 나타내므로 최대 폭 정수 domain도
overflow하지 않는다. 빈 view 역시 source owner, region, coordinate domain,
삽입 경계를 잃지 않는다.

view 사용을 끝낼 때에는 별도 rebase 결과를 남기는 것이 아니라 borrow
region을 닫는다. 그 뒤 source owner는 다시 허용된 mutation이나 move를
수행할 수 있다. 반대로 view를 반환하거나 저장하려면 반환값의 lifetime이
source owner와 어떻게 연결되는지 signature가 증명해야 한다. 증명이
없으면 runtime reference counting을 기대해 통과시키지 않는다.

실패 trace는 range normalization, domain 검사, borrow admission,
projection publication 네 단계다. 시작 coordinate가 끝보다 크거나
허용되지 않은 빈 범위이면 publication은 영이다. borrow 충돌이 있으면
coordinate가 유효해도 거부한다. 어느 실패에서도 source를 소비하거나
부분 view를 외부에 노출하지 않는다. copy가 필요하면 명시적
materialization으로 새 owner와 새 domain을 만든 사실을 적는다.

### 6.1 coordinate를 보존하는 List view

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let values = [10, 20, 30, 40]
let middle = values[2..$]
let sameCoordinate = middle[3]
```

`middle`의 domain은 2..4다. `middle[3]`은 원본 coordinate 3의 값 30이다.
view를 `1..3`으로 rebase하지 않는다.

### 6.2 anchor로 전체와 내부 범위 쓰기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let all = values[^..$]
let withoutFirst = values[^ + 1 .. $]
let prefix = values[..<4]
let suffix = values[2..]
let full = values[..]
```

receiver와 length를 한 번 얻고 anchor offset과 bounds를 검사한 뒤 view를
publish한다.

### 6.3 NumericArray axis view

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let matrix = #2,3[
    1, 2, 3;
    4, 5, 6;
]

let secondColumn = matrix[*, 2]
let lowerRight = matrix[2, 2..3]
```

top-level comma가 index axis를 나눈다. NumericArray 리터럴의 semicolon은
row/orientation owner이므로 그대로 남는다. scalar가 아닌 axis가 남으면 rank/shape와
provenance를 보존한 view다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let all = values[..]
```

`[..]`는 모든 slice-capable owner의 full slice다. NumericArray axis에서는
`[..]`와 `[*]`가 같은 full-axis selector로 정규화되지만 ordinary List에는
`[*]`를 사용하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: SLICE_EXCLUSIVE_OPEN_END_REDUNDANT; product: NOT_RUN -->
```deeplus
let invalid = values[2..<]
// SLICE_EXCLUSIVE_OPEN_END_REDUNDANT
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: SLICE_VIEW_ESCAPES_OWNER; product: NOT_RUN -->
```deeplus
private def invalidView() -> ReadonlyView<Int> = {
    let local = [10, 20, 30]
    return local[1..2]
}
// SLICE_VIEW_ESCAPES_OWNER
```

`i..<j`는 warning 없는 canonical 표면이다. `i..<`는 `i..`와 구별되는
계약이 없으므로 거부한다. negative-from-end와 mutable slice assignment는
없다.

### 7.1 expression Range와 slice owner를 섞지 않는다

괄호 밖 expression Range는 `start..end`, `start..<end`, `start...`와
각각의 `:step` 형식을 가진다.

```deeplus
let odds = 1..10:2
let countdown = 10..1:-1
let naturals = 1...
```

start, end, step은 왼쪽부터 정확히 한 번 평가한다. step 0이나 end와
반대 방향인 step은 거부하고, bounded range는 overflow 전에 종료한다.
유한 ordered Enum에는 one-sided `...`를 쓸 수 없다. 이 `:step`은 Range
parselet 소유이며 slice step을 자동 활성화하지 않는다.

## 8. 다른 기능과의 연결

- attached `A^` transpose도 owner-bounded readonly coordinate view다.
- pattern의 List `_..`는 slice가 아니라 ignored remainder Pattern이다.
- live view는 source move/freeze/mutation과 충돌한다.
- Actor message에 view를 보내도 자동 snapshot/Transferable evidence가
  생기지 않는다.

## 9. Deeplus다운 작성 관례

- end 포함 여부를 API 의도에 맞춰 `..` 또는 `..<`로 분명히 쓴다.
- API가 view를 반환하면 owner region을 signature와 설명에 드러낸다.
- 독립된 수명이 필요하면 명시적 snapshot/copy API를 선택한다.
- `^`/`$`는 slice/index owner 안에서만 쓴다.

## 10. 연습 문제

1. **복사:** 다섯 값의 2..4 view를 만들고 coordinate 3을 읽어라.
2. **빈칸 완성:** `let tail = values[___ + 1..___]`의 두 빈칸에 `^`와
   `$`를 넣어 첫 값만 제외한 view를 완성하라.
3. **설계:** matrix row view를 task에 넘겨야 하는 상황에서 view 유지,
   snapshot, owner move를 비교하라.

## 11. 빠른 복습

- slice는 기본적으로 copy가 아니라 view다.
- view는 source coordinate와 provenance를 보존한다.
- `^`는 first, `$`는 last anchor다.
- owner보다 오래 살거나 isolation을 넘을 수 없다.
- `..<`와 open-bound slice는 warning 없는 canonical 표면이다.

## 12. 정본 근거와 다음 장

- [index/slice 레퍼런스](../../grammar-reference/09-collections-indexing-and-slicing.md)
- [MIR index와 slice](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [정확한 grammar](../../../spec/grammar/deeplus.dpg)

다음 장에서는 eager comprehension과 lazy generator를 구분한다.
