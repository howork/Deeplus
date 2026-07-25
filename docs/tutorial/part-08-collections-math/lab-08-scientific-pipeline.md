# Lab 8 — 과학 데이터 pipeline

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 목표

1-based sample series를 검증하고 view와 comprehension으로 정리한 뒤,
NumericArray projection과 exact calibration 경계·unit 변환을 설계한다.

## 준비

- 8.1~8.5를 읽는다.
- 입력 collection owner와 output owner를 구분한다.
- 계산 결과는 정본 설계의 예상값이며 target 실행 증거가 아님을 적는다.

## 누적 프로젝트 연결

| 연결 | 내용 |
|---|---|
| input prior | Part 7에서 확정한 resource owner, borrow, failure, cleanup 경계 |
| output | 1-based sample view, exact calibration 경계, shape-checked projection, typed report |
| next | Part 9에서 Result/error, effect, contract로 pipeline 실패를 외부 API에 노출 |

앞 부의 ownership 규칙은 이 Lab에서 수치 계산의 전제다. view가 source보다
오래 살지 않는지, generator로 확장할 때 capture가 안전한지, 실패한
calibration이나 matrix product가 부분 report를 남기지 않는지를 함께
검토한다.

## 1단계 — sample과 window

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let samples = [12.0, 15.0, -1.0, 18.0, 21.0]
let first = samples[1]
let analysisWindow = samples[2..$]

let admitted = [
    value
    for value in analysisWindow
    if value >= 0.0
]
```

`analysisWindow` coordinate는 2..5이고 `admitted`는 새 eager List다.
view는 rebase하지 않지만 새 comprehension 결과는 자신의 ordinary
1-based domain을 갖는다.

## 2단계 — exact calibration 경계와 unit

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
use std::units::si

let calibration: Rational = <3/2>
let distance = 2500[m]
let duration = 125[s]
let speed = distance / duration
let speedMetersPerSecond = speed ~ scalarIn(1[m/s])
```

calibration은 exact control value다. 실제 Float sample에 적용하려면 어떤
checked conversion을 허용할지 별도 API가 정해야 하며 hidden widening을
넣지 않는다.

## 중간 점검

- [ ] `samples[0]`을 쓰지 않았다.
- [ ] view coordinate와 새 List coordinate를 구분했다.
- [ ] Rational을 Float로 암시 변환하지 않았다.
- [ ] speed dimension을 `Length/Time`으로 보존했다.

## End-to-end 계산·책임 trace

첫째, `samples`가 ordinary List owner로 만들어지고 공개 coordinate는
1..5가 된다. `samples[2..$]`는 값을 복사하지 않고 같은 owner의 2..5를
가리키는 readonly view다. 이 view가 살아 있는 동안 source를 충돌하게
mutate하거나 move하지 않는다. comprehension은 허용된 값을 새 ordinary
List에 eager하게 모으므로 결과 owner와 1-based domain이 새로 생긴다.

둘째, `<3/2>` calibration은 exact control value로 남는다. Float sample에
적용하려면 어느 representation으로 변환하며 어떤 rounding을 허용하는지
이름 있는 checked API가 필요하다. 거리와 시간의 division은
`Length/Time` dimension을 만들고, `scalarIn(1[m/s])` projection은 exact
unit evidence를 요구한다. conversion이 실패하면 report field를 일부만
commit하지 않는다.

셋째, `transform`과 `vector`를 각각 한 번 평가한 후 `2×3`과 `3×1`의
inner dimension을 검사한다. admission 성공 시에만 `2×1` result owner를
계산한다. `transform^`는 원본에 묶인 transpose view이고
`projected[1; 1]`의 axis coordinate는 모두 1-based다. 마지막으로
Complex metadata와 계산 결과를 Record로 조립하되, serialization tag나
외부 publication을 이 Lab이 자동 승인하지 않는다.

오류 경로에서도 owner와 effect를 기록한다. index 또는 shape 검사가
실패하면 element read와 numeric loop는 시작하지 않는다. 계산 도중
checked element failure가 가능한 확장에서는 partial output을 버리고
입력 owner를 보존한다. cleanup은 source owner를 가진 scope가 담당하며,
task/actor로 넘기는 확장에서는 enqueue commit 전후의 owner를 별도
설계해야 한다.

## Review rubric

| 검토 항목 | 통과 기준 | 실패 시 되돌릴 곳 |
|---|---|---|
| coordinate | carrier별 logical domain과 1-based 규칙이 명시됨 | indexing 설계 |
| provenance | view의 source owner, mapping, lifetime이 설명됨 | slice 생성 |
| materialization | eager List와 single-pass generator가 구분됨 | collection 선택 |
| numeric domain | Rational, Float, Complex 변환이 명시적임 | calibration 경계 |
| shape | operand rank/shape를 계산 전에 검증함 | operation admission |
| dimension | Measure dimension과 conversion evidence를 보존함 | unit projection |
| failure | partial report 없이 owner와 cleanup 책임이 남음 | commit 경계 |
| evidence | 결과를 설계 예측으로 표시하고 `NOT_RUN`을 유지함 | publication 주장 |

리뷰어는 각 행에 값 하나만 적지 않고 “검사 주체, 실패 효과, 성공 후
owner”를 함께 적는다. 어느 행도 답할 수 없다면 뒤 단계 결과가 맞더라도
앞 단계 계약으로 돌아가 보완한다.

최종 rollback 요약에서는 `analysisWindow`가 source borrow인지,
`admitted`와 `projected`, `report`가 새 owner인지 구분한다. window
admission 실패는 source List를 보존하고, comprehension 실패는 새 List
publication을 막는다. shape 실패는 projected owner를 만들지 않으며,
unit conversion 실패는 report commit을 막는다. 이미 검증된 입력을
조용히 폐기하거나 실패한 출력의 일부를 다음 단계에 넘기지 않는다.

누적 프로젝트의 다음 단계에는 성공한 typed report와 명시된 failure
contract만 전달한다. 실험용 view, 임시 matrix storage, 계산 중간
binding은 API 결과가 아니다. 이 구분을 유지하면 Part 9가 error/effect를
정교화해도 Part 8의 coordinate와 numeric identity를 다시 해석할 필요가
없다.

## 3단계 — shape가 닫힌 projection

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let transform = #2,3[
    1.0, 0.0, 0.0;
    0.0, 1.0, 1.0;
]

let vector = #3,1[
    12.0;
    15.0;
    18.0;
]

let projected = transform ** vector
let firstProjected = projected[1; 1]
let transposedView = transform^
```

inner dimension은 3으로 일치하고 result shape는 2×1이다. transpose는
copy가 아닌 readonly coordinate view다.

## 4단계 — Complex signal metadata

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let phase: Complex = 3.0 + 4.0i
let normalizedPhase = phase - 1.0

let report = ${
    firstProjected
    speedMetersPerSecond
    phase: normalizedPhase
}
```

Record label은 runtime Map key가 아니며 각 field expression이 성공한 뒤
report가 한 번 publish된다.

## 실패 실험

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: MATRIX_PRODUCT_DIMENSION_MISMATCH; product: NOT_RUN -->
```deeplus
let invalid =
    #2,3[1, 2, 3; 4, 5, 6;] **
    #2,1[7; 8;]
// MATRIX_PRODUCT_DIMENSION_MISMATCH
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: INDEX_OUT_OF_LOGICAL_DOMAIN; product: NOT_RUN -->
```deeplus
let invalidFirst = admitted[0]
// INDEX_OUT_OF_LOGICAL_DOMAIN
```

## 확장 과제

1. **복사:** 두 길이 3 vector의 `*+` dot product를 추가한다.
2. **빈칸 완성:** `let window = samples[___..___]`에 `2`, `4`를 넣고
   `window[___]`이 source coordinate `3`을 읽도록 마지막 빈칸을 채운다.
3. **설계:** streaming sensor를 generator로 바꾸고 owner, yield failure,
   cleanup, 재순회 가능성의 차이를 표로 작성한다.

## 완료 체크리스트

- [ ] 모든 ordinary index가 1-based다.
- [ ] slice view의 provenance와 lifetime을 보존했다.
- [ ] comprehension과 generator를 혼동하지 않았다.
- [ ] NumericArray shape를 명시하고 implicit broadcast를 쓰지 않았다.
- [ ] Rational/Complex/Measure의 exact domain을 보존했다.
- [ ] semantic P0 `0`, OPEN P1 `22`, product lanes `15/15 NOT_RUN`을
      유지했다.

## 정본 근거

- [1-based collection 통합 예제](../../grammar-reference/24-integrated-worked-examples.md)
- [컬렉션 레퍼런스](../../grammar-reference/09-collections-indexing-and-slicing.md)
- [numeric/operator 레퍼런스](../../grammar-reference/08-expressions-and-operators.md)
- [정본 언어 명세](../../../spec/language.md)
