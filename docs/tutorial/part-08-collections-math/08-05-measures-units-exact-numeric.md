# 8.5 Measure, unit, exact numeric

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

여기서 **Measure**는 numeric magnitude와 unit dimension evidence를 함께
보존해 서로 다른 물리 차원의 값을 우연히 섞지 못하게 하는 typed
quantity다.

Rational literal, floating imaginary literal, Rational/Complex의 닫힌 산술,
Measure와 exact-ratio unit catalog는 현행 설계다. fixed-glyph
conformance는 정확한 13개 unary·산술·equality·ordering 역할에만
한정된다.

## 2. 학습 목표

- Rational과 Float의 정밀도 모델을 구분한다.
- canonical Complex literal `3.0 + 4.0i`를 쓴다.
- measure의 representation과 dimension을 함께 보존한다.
- exact unit conversion과 dynamic provider conversion을 구분한다.
- closed power matrix와 named failure API를 이해한다.

## 3. 선수 지식

numeric literal, fixed-glyph conformance, `^` power와 Result/error의 기초가
필요하다.

## 4. 문제에서 출발하기

금액 비율 `1/3`을 Float로 저장하면 반복 계산에서 오차가 생길 수 있다.
거리 13과 시간 13도 숫자는 같지만 차원이 다르다. exact numeric과
Measure는 값·표현·차원을 분리해 조기 오류를 만든다.

## 5. 핵심 모델

- `<p/q>`: BigInt-normalized exact `Rational`
- `4.0i`: floating-only attached imaginary token
- `3.0 + 4.0i`: `Complex<Float64>`의 canonical 표현
- `13[cm]`: numeric value와 unit expression의 Measure
- `m/s`, `m*s`, `m^2`: unit dimension algebra

Measure의 대괄호는 숫자에 붙여 쓴다. 다만 parser는 공백 하나만으로
Measure라고 단정하지 않고, 대괄호 안이 완전한 unit expression인지 먼저
transactional하게 확인한다.

| 입력 | 결과 |
|---|---|
| `13[cm]` | 올바른 `MeasureLiteralExpr` |
| `13 [cm]` | `UNIT_LITERAL_BRACKET_MUST_BE_ATTACHED`; 닫는 `]`까지 recovery CST 오류 하나로 보존하며 Measure/Index AST는 만들지 않음 |
| `13[0]` | 일반 `IndexExpr`로 parse한 뒤 1-based index domain 검사를 받음 |
| `13 [0]` | 공백이 있어도 일반 `IndexExpr`; Measure 진단 없이 같은 domain 검사를 받음 |

즉 `13 [cm]`은 잘못 띄어 쓴 Measure지만, `13 [0]`은 Index다. 실패한
unit 탐사는 토큰을 소비하거나 진단을 남기지 않으므로 이후 Index 해석을
방해하지 않는다.

Rational/Complex 표준 arithmetic row는 sealed `DIRECT_GLOBAL` identity다.
Rational과 Complex division은 `/`를 지원하고, 0 제수나 invalid domain은
commit 전 `ArithmeticDefect`로 닫는다. Rational의 named `dividedBy`는
상세 recoverable 실패가 필요한 별도 API다. `^`는 Trait가 아니라 closed
language intrinsic matrix다.

## 6. 단계별 예제

### 깊이 읽기: 숫자, 표현, 차원을 한 계약으로 뭉개지 않는다

수치 식을 읽을 때에는 먼저 numeric domain을 고른다. Rational은 정규화된
분자·분모로 exact 비율을 보존하고, Float는 유한 정밀도 근사를 표현한다.
Complex는 같은 representation domain의 실수부와 허수부를 가지며
`3.0 + 4.0i`처럼 floating imaginary token을 사용한다. Measure는 여기에
unit expression으로 계산한 dimension과 scale evidence를 더한다. 화면에
같은 `13`이 보여도 `13[m]`과 `13[s]`가 같은 operand가 아닌 이유다.

판단 순서는 operand domain과 representation을 확인하고, operation의
closed admission row를 고른 뒤, dimension algebra와 exact conversion
가능성을 검사하는 것이다. catalog에 exact ratio가 있는 unit conversion은
그 ratio를 보존할 수 있다. 환율처럼 시간·provider·rounding이 필요한
변환은 unit 문법으로 숨기지 않고 explicit service/API와 observation
metadata를 요구한다. 실패 시 target을 부분 갱신하거나 부정확한 Float
fallback을 자동 선택하지 않는다.

`^` power도 임의 Trait dispatch가 아니라 닫힌 language matrix이므로
base와 exponent domain을 먼저 대조한다. division처럼 zero나 domain
failure가 가능한 경우에는 named failure API와 Result/error 경계를
따른다. 흔한 오해는 unit spelling이 같으면 provenance도 같다고 보거나,
Rational을 언제든 Float로 바꿔도 exactness가 유지된다고 보는 것이다.
리뷰 trace에는 input representation, dimension, conversion evidence,
rounding policy, result owner를 따로 적어 이런 혼동을 막는다.

두 Measure를 더할 때에는 먼저 dimension equality를 증명하고, 서로 다른
unit spelling이면 exact scale conversion이 가능한지 확인한다. 이 검사가
끝나기 전에는 magnitude 연산을 시작하지 않는다. 곱셈과 나눗셈은 unit
expression으로 새 dimension을 계산하며, 숫자만 남기려고 unit을 자동
소거하지 않는다. dimensionless 결과도 어떤 연산으로 얻었는지 evidence를
보존한다.

Rational에서 Float로 가는 경계에는 정밀도 손실 가능성과 rounding
정책을, Float에서 Rational로 가는 경계에는 정확한 원래 비율을 복원하는
연산이 아니라는 사실을 적는다. Complex의 실수부·허수부 representation도
같이 유지한다. 실패하면 기존 target magnitude와 unit metadata를
보존하고 새 값을 publish하지 않는다. 결과 출력이 짧더라도 이 변환
ledger가 있어야 계산을 재현하고 오차 책임을 검토할 수 있다.

### 6.1 exact 비율

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let a: Rational = <2/3>
let b: Rational = <5/7>
let sum: Rational = a + b
let scaled: Rational = 3 * a

let divisor: Rational = <4/9>
let quotient: Rational = a / divisor
let remainder: Rational = a % divisor
let checkedQuotient = a.dividedBy(divisor)
```

`/`는 fixed `Divide<Rational>`, `%`는 fixed `Remainder<Rational>` row를
사용하며 zero divisor에서 `ArithmeticDefect`를 낸다. `%`는
`q = truncTowardZero(a / divisor)`, `remainder = a - q * divisor`를
만족한다. `dividedBy`는 같은 조건의 상세 실패를 이름 있는 recoverable
API로 보존한다.

### 6.2 Complex literal과 power

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let z: Complex = 3.0 + 4.0i
let shifted: Complex = z - 1.0
let rotated: Complex = Complex::i * z

let principalRoot: Complex =
    Complex!(real: -1.0, imag: +0.0) ^ 0.5
```

imaginary suffix는 decimal floating literal에 붙는다. `4i`, bare `i`,
separated `4.0 i`, `j` suffix는 현행 literal이 아니다. Complex power는
principal branch와 signed zero를 보존한다.

### 6.3 unit과 dimension

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
use std::units::si

let distance = 2500[m]
let time = 125[s]
let speed = distance / time

let kilometers = distance ~ asUnit 1[km]
let scalarMeters = distance ~ scalarIn 1[m]
```

`distance / time`은 normalized `Length/Time` dimension을 만든다.
`asUnit`은 같은 dimension의 exact-ratio conversion이다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: IMAGINARY_LITERAL_FORM_NOT_ADMITTED; product: NOT_RUN -->
```deeplus
let invalid = 3 + 4i
// IMAGINARY_LITERAL_FORM_NOT_ADMITTED
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: POWER_OPERAND_DOMAIN_NOT_ADMITTED; product: NOT_RUN -->
```deeplus
let invalid: Rational = <2/3> ^ 2
// POWER_OPERAND_DOMAIN_NOT_ADMITTED
```

calendar/currency처럼 시간·policy·provider가 필요한 변환은
`asUnitUsing(provider, sample)` 같은 explicit stdlib profile을 사용한다.
core exact-ratio conversion으로 숨기지 않는다.

## 8. 다른 기능과의 연결

- Rational은 `+ - * / %`, Eq, Ord를, Complex는 `+ - * /`와 partial
  equality를 Stable bounded profile로 제공한다. Complex에는 `%`와
  `Ord`가 없다.
- NumericArray는 exact element/shape law를 요구하고 hidden
  Float32/Float64 widening을 하지 않는다.
- Measure power는 `StaticInt` exponent와 normalized dimension을 보존한다.
- HIR-H1 numeric plan은 selected operation/type/profile을 기록하고 runtime
  witness/provider를 다시 찾지 않는다.

## 9. Deeplus다운 작성 관례

- exact 비율에는 Rational, 측정 오차가 본질인 계산에는 Float를 쓴다.
- Complex literal은 실수부와 floating imaginary token을 명시한다.
- 물리량 API는 raw scalar 대신 Measure를 받는다.
- 동적 변환의 provider, policy, effect/error를 signature에 드러낸다.

## 10. 연습 문제

1. **복사:** `<3/4>`와 `<1/8>`을 더하는 exact 식을 작성하라.
2. **빈칸 완성:** `let shifted = (___ + 4.0i) - ___`의 두 빈칸에 `5.0`과
   `1.0`을 넣고 결과의 실수부와 허수부를 적어라.
3. **설계:** 환율 변환 API의 provider, observation time, rounding,
   failure/effect row를 exact unit conversion과 비교해 설계하라.

## 11. 빠른 복습

- Rational은 exact normalized fraction이다.
- imaginary literal은 floating magnitude와 attached `i`다.
- Complex power는 principal branch다.
- Measure는 값과 dimension을 함께 보존한다.
- dynamic provider 변환은 core exact ratio가 아니다.

## 12. 정본 근거와 다음 장

- [연산자·exact numeric 레퍼런스](../../grammar-reference/08-expressions-and-operators.md)
- [Measure·unit 레퍼런스](../../grammar-reference/07-enums-records-schemas-bitfields-and-units.md)
- [numeric coherence](../../../spec/contracts/rational-complex-numeric-coherence.json)
- [HIR/MIR numeric plan](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

이제 실습에서 collection, view, NumericArray, Rational과 Measure를
과학 데이터 pipeline으로 결합한다.


<!-- IR-OWN-R8-TUTORIAL-08-05 -->
### Measure 문맥과 `UnitWitnessId`

예를 들어 `let metre = 1.0 m` 뒤에
`let result = &metre + 25.0`을 평가할 수 있다.

Measure 문맥 anchor는 단위 witness가 정적으로 알려진 경우에만
허용된다. 단위가 불명확하면 추측하지 않고 진단한다.
