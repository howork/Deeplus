# 8.4 NumericArray와 선형대수

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

여기서 **rank**는 array가 가진 axis의 수이고, **shape**는 각 axis의
길이를 순서대로 적은 tuple이며, 둘은 element 값과 별도의 identity다.

NumericArray literal, exact shape, 1-based axis, `*+` dot product,
`**` matrix product, attached postfix `A^` transpose는 현행 설계다.
elementwise infix power는 Preview-gated이며 이 장의 current 계산에
사용하지 않는다.

## 2. 학습 목표

- row/column/exact-shape literal을 구분한다.
- rank, shape, orientation과 element domain을 읽는다.
- elementwise `*`, dot `*+`, matrix `**`를 구분한다.
- transpose와 complex adjoint를 구분한다.

## 3. 선수 지식

1-based multi-axis index, exact numeric operation과 view provenance가
필요하다.

## 4. 문제에서 출발하기

두 vector를 `*`로 곱했을 때 elementwise 결과인지 scalar dot product인지
rank에 따라 몰래 바뀌면 코드를 읽기 어렵다. Deeplus는 operation glyph와
shape admission을 분리한다.

## 5. 핵심 모델

- `#[1, 2, 3]`: rank 1, shape `[3]`, `ROW` orientation
- `#[1; 2; 3]`: rank 1, shape `[3]`, `COLUMN` orientation
- `#1,3[...]` / `#3,1[...]`: 서로 구별되는 exact rank-2 matrix
- `#2,3[...]`: exact rank-2 shape
- `a * b`: admitted same-shape elementwise multiply
- `u *+ v`: equal-length rank-1 dot product
- `A ** B`: compatible rank-2 matrix product
- `A^`: attached transpose readonly view
- `A ~ adjoint`: named complex conjugate transpose

`#`와 `[`는 붙여 쓴다. 두 inferred form의 orientation은 separator가
결정하며 expected result type이 다시 고르지 않는다. ordinary List를
NumericArray로 바꾸거나 implicit broadcasting, nested-rank inference,
element widening을 삽입하지 않는다.

## 6. 단계별 예제

### 깊이 읽기: operator보다 shape admission을 먼저 증명한다

NumericArray 식은 glyph만 보고 계산하지 않는다. 먼저 두 operand를 각각
한 번 평가하고 element domain, rank, shape, orientation을 얻는다. 다음에
선택한 operation row가 요구하는 exact 조건을 검사한다. `*`는 허용된
same-shape elementwise row, `*+`는 길이가 같은 rank-1 vector의 scalar
dot product, `**`는 왼쪽 마지막 dimension과 오른쪽 첫 dimension이 맞는
rank-2 matrix product다. 조건을 통과한 뒤에만 결과 shape와 element
domain을 정하고 계산을 시작한다.

이 순서 덕분에 `#2,3[...] ** #2,1[...]`은 element loop 중간이 아니라
shape admission에서 거부된다. 길이 1 axis가 있더라도 implicit
broadcast를 삽입하지 않고, integer와 float element를 몰래 widening하지
않는다. 필요한 shape transformation이나 numeric conversion은 이름 있는
API로 먼저 표현해야 하므로 리뷰어가 비용과 실패 지점을 볼 수 있다.

postfix `A^`는 source owner에 묶인 readonly coordinate view이며 단순
matrix에서는 axis order를 바꾼다. complex value에서 conjugation까지
필요한 연산은 같은 것으로 축약하지 않고 named `adjoint`를 사용한다.
따라서 trace에는 operand identity, admission 결과, result shape,
view provenance 또는 allocation owner, element failure 정책을 차례로
남긴다. 계산값이 맞아도 이 다섯 항목 중 하나가 암묵적이면 Deeplus다운
수치 계약으로 완성되지 않은 것이다.

shape trace를 표처럼 읽어 보자. row vector와 column vector는 모두
rank 1, shape `[N]`이며 각각 `ROW`와 `COLUMN` orientation을 함께
보존한다. exact `#1,N[...]`과 `#N,1[...]`은 이들과 동일시되지 않는
rank-2 matrix다. `#2,3[...]`은 두 axis 길이가 각각 2와 3이다. `u *+ v`에서는 두
vector 길이를 같게 증명한 뒤 scalar result를 만들고, `A ** B`에서는
inner dimension을 같게 증명한 뒤 outer dimension으로 result shape를
정한다. orientation이나 rank가 맞지 않으면 element 값이 같은 배열도
다른 operand다.

계산 단계에서는 결과 storage를 준비한 뒤 checked element operation을
정해진 순서로 수행하고, 전체 성공 뒤 result owner를 publish한다. 어떤
element에서 failure가 가능한 domain이라면 partial matrix를 성공
결과처럼 반환하지 않는다. pure exact domain과 실패 가능한 domain을
같은 구현 shortcut으로 합치지 않고 error/effect row를 보존한다.

transpose view를 이어서 slice하면 두 projection의 coordinate mapping과
source owner를 합성해 추적한다. materialize가 필요한 경계에서는 named
API가 새 shape와 allocation owner를 만든다. 성능을 이유로 view와 copy를
서로 바꾸려면 관찰 가능한 lifetime과 owner 계약이 같다는 별도 증명이
필요하다. 단지 값이 같다는 테스트만으로는 충분하지 않다.

### 6.1 literal과 axis

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let row = #[1, 2, 3]
let column = #[1; 2; 3]
let matrix = #2,3[
    1, 2, 3;
    4, 5, 6;
]

let topLeft = matrix[1; 1]
let secondColumn = matrix[*; 2]
```

`row`, `column`, `matrix`는 element가 같아도 rank/orientation identity가
다르다.

### 6.2 dot product와 matrix product

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let u = #[1, 2, 3]
let v = #[4, 5, 6]
let dot = u *+ v

let a = #2,3[
    1, 2, 3;
    4, 5, 6;
]
let b = #3,2[
    7, 8;
    9, 10;
    11, 12;
]
let product = a ** b
```

`dot`의 설계상 값은 32다. matrix product는 inner dimension 3이 같아야
하고 결과 shape는 2×2다. checked element operation 실패 시 partial
result를 publish하지 않는다.

### 6.3 transpose와 adjoint

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let matrix = #2,2[
    1.0 + 2.0i, 3.0 + 4.0i;
    5.0 + 6.0i, 7.0 + 8.0i;
]

let transposed = matrix^
let conjugateTransposed = matrix ~ adjoint
```

`matrix^`는 coordinate를 바꾼 readonly view이고 Complex 값을 켤레화하지
않는다. `adjoint`는 별도 named API다. Complex `u *+ v`는 왼쪽 vector를
켤레화하는 inner product이고 unconjugated 계산은 named `dotu`가 소유한다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: MATRIX_PRODUCT_DIMENSION_MISMATCH; product: NOT_RUN -->
```deeplus
let invalid =
    #2,3[1, 2, 3; 4, 5, 6;] **
    #2,2[1, 2; 3, 4;]
// MATRIX_PRODUCT_DIMENSION_MISMATCH
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: NUMERIC_ARRAY_SHAPE_MISMATCH_NO_IMPLICIT_BROADCAST; product: NOT_RUN -->
```deeplus
let invalid = #2,2[1, 2; 3, 4;] + #[10, 20]
// NUMERIC_ARRAY_SHAPE_MISMATCH_NO_IMPLICIT_BROADCAST
```

spaced `a ^ b`는 scalar power, attached `A^`는 transpose다. formatter가
둘을 바꾸지 않는다. ungated NumericArray infix power는
`NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE`다.

## 8. 다른 기능과의 연결

- axis coordinate는 runtime Map key나 ordinary label이 아니다.
- transpose view는 source owner/lifetime/provenance를 보존한다.
- NumericArray pointwise logical은 same shape와 exact known-width integer
  element만 허용한다.
- fixed-glyph conformance는 NumericArray linear operators의 owner가 아니다.

## 9. Deeplus다운 작성 관례

- public API에 rank와 shape expectation을 명시한다.
- elementwise, dot, matrix, transpose/adjoint를 glyph와 이름으로 구분한다.
- implicit broadcast 대신 명시적 shape transformation API를 쓴다.
- Complex 계산에서는 conjugation convention을 문서화한다.

## 10. 연습 문제

1. **복사:** 2×2 matrix를 만들고 `[2; 1]` element를 읽어라.
2. **빈칸 완성:** `#[1, 2, 3] *+ #[4, 5, 6] = 1*4 + ___ + ___`의 두
   빈칸을 채우고 scalar 결과를 계산하라.
3. **설계:** batch×feature matrix와 weight matrix의 shape contract,
   mismatch diagnostic, result owner commit을 설계하라.

## 11. 빠른 복습

- NumericArray는 List가 아니다.
- axis는 1-based이고 rank/shape가 identity다.
- `*+`는 dot, `**`는 matrix product다.
- attached `A^`는 transpose, adjoint가 아니다.
- implicit broadcasting은 없다.

## 12. 정본 근거와 다음 장

- [NumericArray 정본](../../../spec/language.md)
- [operator 레퍼런스](../../grammar-reference/08-expressions-and-operators.md)
- [collection/axis 레퍼런스](../../grammar-reference/09-collections-indexing-and-slicing.md)
- [MIR transpose](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음 장에서는 값의 정확도와 물리 차원을 타입에 보존한다.


<!-- IR-OWN-R8-TUTORIAL-08-04 -->
### NumericArray 문맥 제공자

예: `let shifted = &matrix + row`

여기서 `&matrix`는 가장 가까운 연산에 NumericArray 문맥을 공급한다. matrix를
borrow하거나 런타임 provider를 검색하지 않으며 각 operand는 한 번만
평가된다.
