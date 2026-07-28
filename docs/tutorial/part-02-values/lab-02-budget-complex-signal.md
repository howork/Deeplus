# Lab 02. 정확한 예산과 복소 신호

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

## 목표

Rational로 정확한 예산 비율을 계산하고 Complex로 2차원 신호를 표현한다.
두 domain을 Float 하나로 뭉개지 않고 각 closed operator 책임을 보존한다.

## 준비

- [값과 identity](02-01-values-literals-identity.md)
- [Rational과 Complex](02-02-rational-complex.md)
- [연산자와 power](02-04-operators-power-boolean.md)

## 단계별 구현

### 1단계: 예산의 exact ratio 계산

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::labs::numeric

private def#pure addRate(
    base: Rational,
    rate: Rational,
) -> Rational
= {
    return base + base * rate
}

let principal: Rational = <1_000/1>
let feeRate: Rational = <3/100>
let total: Rational = addRate(base: principal, rate: feeRate)
```

Rational multiplication과 addition은 정확하다. `total`의 정본상 값은
`1030/1`이며 Float rounding을 거치지 않는다.

### 2단계: Complex 신호 회전

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure rotateQuarter(signal: Complex) -> Complex
= {
    return Complex::i * signal
}

let source: Complex = 3.0 + 4.0i
let rotated: Complex = rotateQuarter(source)
let energyScale: Complex = source * 2.0
```

각 식은 same-Rep Complex 또는 exact real/Complex sealed row를 사용한다.
runtime provider lookup이나 result-directed conversion은 없다.

## 판정 trace

예산 계산은 literal admission부터 시작한다. `<1_000/1>`과 `<3/100>`의
분자·분모를 읽고 denominator가 0이 아닌지 확인한 뒤 각각 canonical
기약분수 identity를 만든다. `base * rate`에서 Rational multiplication
owner와 exact result를 고르고, 그 결과를 `base`와 더한다. 두 operation
사이에는 Float conversion이나 rounding event가 없다. 마지막으로
`addRate`의 정상 경로가 Rational을 return하고 빈 error/effect row를
유지하는지 확인한다.

신호 계산은 `3.0`과 `4.0i`를 별도 literal로 판정한 뒤 `+`의 admitted
Complex corridor를 선택한다. `rotateQuarter`에서는 `Complex::i`와
signal의 representation parameter가 호환되는지 확인하고 multiplication
result를 만든다. `source * 2.0`도 result expected type이 winner를 고르는
것이 아니라 operand domain의 닫힌 adaptation row를 따른다. 이 trace에
source spelling, normalized value, selected operation, result domain,
failure/commit의 다섯 열을 사용하라.

## 중간 점검

- `<p/q>` 안에 공백, 부호, radix prefix를 넣지 않았는가?
- 허수 marker `i`가 floating literal에 붙어 있는가?
- `Rational`과 `Complex`를 hidden Float conversion으로 섞지 않았는가?
- 함수가 recoverable error/effect를 숨기지 않는가?
- design-static expected value를 product PASS로 부르지 않았는가?

## 실패 실험

다음 두 source는 서로 다른 lexical/static 이유로 거부된다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: RATIONAL_LITERAL_* / IMAGINARY_LITERAL_* -->
```deeplus
let zeroDenominator: Rational = <5/0>
let integerImaginary: Complex = 4i
```

첫 줄은 완성된 Rational 후보의 denominator rule, 둘째 줄은 imaginary
literal의 floating-prefix rule을 위반한다. compiler가 `4 * i`로
implicit multiplication을 발명하지 않는다.

## 흔한 오해와 미니 사례

`<3/100>`을 실행 전에 `0.03`으로 바꾸어도 같다고 생각하기 쉽지만,
Float로 바꾸는 순간 representation과 rounding 책임이 추가된다. exact
예산 계산이 목적이면 Rational domain을 끝까지 유지한다. 반대로 화면에
소수점이 있다는 이유만으로 `3.0 + 4.0i`가 두 Float의 Tuple인 것도
아니다. 선택된 `+`가 하나의 Complex value를 만든다.

미니 사례로 principal이 `<1/3>`, rate가 `<1/10>`일 때 손으로
`<1/3> + <1/30> = <11/30>`을 계산해 보라. decimal 근삿값과 비교하되
튜토리얼의 정본 결과는 normalized Rational pair다. Complex 쪽에서는
`Complex::i * (3.0 + 4.0i)`의 real/imaginary 성분을 계산하고, `i`를
이름 조회나 custom operator로 해석하지 않았는지 확인한다.

실제 설계 선택에서는 계산값뿐 아니라 공개 경계도 본다. 예산 API가
Rational을 반환하면 caller는 exact pair를 받으며 serialization mapping을
별도로 정해야 한다. 신호 API가 Complex를 반환하면 representation
parameter와 real/imaginary order가 public type identity에 남는다.
둘을 편의를 위해 String으로 미리 render하면 후속 계산 능력과 오류
위치를 잃는다. 표현은 마지막 adapter에서, 계산은 typed core에서
소유하게 하라.

보고서에는 principal, rate, normalized total을 별도 칸에 쓰고, Complex는
real/imaginary 성분과 representation parameter를 기록한다. 예상값을
손으로 계산한 표는 학습 증거이지 compiler나 target 실행 영수증이
아니다. 이 구분을 완료 체크리스트에도 그대로 유지한다.

## 확장 과제

1. **따라 하기:** principal `2500`, rate `7/200`으로 바꾸고 exact total을
   기약분수로 계산한다.
2. **빈칸 완성:** `let wave: Complex<Float32> = 1.0f32 + ___`를
   `2.0f32`의 허수 성분으로 완성한다.
3. **스스로 설계하기:** Rational 두 개를 결합한 세금 계산과 Complex 두
   개를 결합한 신호 합성을 각각 함수로 만든다. operand/result exact
   domain을 주석 대신 설명 표에 적는다.
4. **심화:** Rational division의 `/`가 0 제수에서
   `ArithmeticDefect`를 내는 경계와, 상세 실패를 보존하는
   `dividedBy` API를 비교한다.

## 누적 프로젝트 연결

| 구분 | 이 실습의 artifact |
|---|---|
| 이전 입력 | Lab 01의 pure callable, 명시적 parameter label과 `NOT_RUN` 판정 방식 |
| 이번 출력 | exact Rational 예산 함수, Complex 신호 함수와 5열 판정 trace |
| 다음 handoff | Lab 03가 pure core를 유지하며 Bool predicate와 closure 정책을 연결 |

누적 프로젝트에서 값 domain을 바꿀 때는 기존 함수를 몰래 widening하지
않고 새 경계 함수를 만든다. 이후 lab이 이 결과를 사용해도 실제 Module
import나 compiler 실행이 완료되었다고 주장하지 않는다.

## 완료 체크리스트

- [ ] Rational이 canonical 기약분수로 해석된다.
- [ ] Complex literal에 canonical `i` marker를 썼다.
- [ ] Float32/Float64 Rep를 숨게 섞지 않았다.
- [ ] arbitrary custom operator를 만들지 않았다.
- [ ] `+`, `-`, `*` 이외의 glyph conformance를 주장하지 않았다.
- [ ] product lane `15/15 NOT_RUN`을 유지했다.

## 정본 근거

- [numeric lexical law](../../grammar-reference/01-lexical-structure.md)
- [Rational/Complex operator law](../../grammar-reference/08-expressions-and-operators.md)
- [numeric coherence contract](../../../spec/contracts/rational-complex-numeric-coherence.json)
- [value/operator contract](../../../spec/contracts/value-operator-indexing-coherence.json)
