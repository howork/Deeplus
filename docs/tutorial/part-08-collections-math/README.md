# Part 8 — 컬렉션, 좌표, 수치 계산

> 과정 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> semantic P0: `0` · OPEN feature P1: `22` · product lanes: `15/15 NOT_RUN`

이 부에서는 여러 값을 담고 순회하는 방법에서 시작해 view provenance,
generator lifetime, NumericArray shape, exact numeric과 unit dimension까지
확장한다. Deeplus의 기본 ordered index는 `1`에서 시작한다.

## 학습 경로

1. [Sequence, Map과 1-based index](08-01-sequence-map-one-based-index.md)
2. [Slice, view, provenance](08-02-slicing-view-provenance.md)
3. [Comprehension과 generator](08-03-comprehensions-generators.md)
4. [NumericArray와 선형대수](08-04-numeric-array-linear-algebra.md)
5. [Measure, unit, exact numeric](08-05-measures-units-exact-numeric.md)
6. [실습: 과학 데이터 pipeline](lab-08-scientific-pipeline.md)

## 이 부의 불변선

- ordinary List/String/Bytes의 유효 index는 `1..length`다.
- bounded List와 slice/view는 source logical coordinate를 보존한다.
- Map key는 exact runtime `K`이며 1-based로 바꾸지 않는다.
- Sequence conformance만으로 `[]`, mutation, freeze, view가 생기지 않는다.
- NumericArray rank, shape, orientation, element와 axis coordinate는 별도
  identity다.
- implicit broadcasting이나 shape/width widening은 없다.
- Rational, Complex, Measure는 닫힌 numeric contract를 따른다.
- NumericArray infix elementwise power와 async comprehension은 현행 Stable
  표면이 아니다.

정적 예제의 계산 결과는 설계상 설명일 뿐 xVM/LLVM 실행 receipt가 아니다.

## 이 부를 읽는 관점

컬렉션 코드는 값만 좇으면 금세 모호해진다. 매 식에서 먼저 carrier의
정확한 타입을 확인하고, 그다음 사용자가 보는 logical coordinate와
backend storage offset을 분리한다. slice가 나오면 새 컬렉션인지
source-bound view인지, comprehension이나 generator가 나오면 eager
materialization인지 single-pass 생산자인지 확인한다. 수치 계산에서는
숫자 모양만 비교하지 말고 element domain, rank, shape, orientation,
unit dimension을 차례로 읽는다.

이 순서는 오류를 늦게 발견하는 암묵적 보정을 피하기 위한 것이다.
Deeplus는 0-based offset, hidden rebase, implicit broadcast, unit 소거를
사용자 모델에 섞지 않는다. 따라서 예제를 따라 할 때에도 “값이 우연히
맞는가”보다 “어떤 identity와 evidence가 이 연산을 허용하는가”를 먼저
설명한다. 이 부의 모든 실행 결과는 설계 예측이며 product lane은 계속
`NOT_RUN`이다.

각 장의 실패 예제도 같은 순서로 읽는다. 범위, lifetime, shape, dimension
검사가 실패한 지점을 찾고, 그보다 뒤의 read·allocation·mutation·외부
effect가 시작되지 않았음을 확인한다. 이 습관이 정상 결과 암기보다
다른 입력에 적용하기 쉽다.
