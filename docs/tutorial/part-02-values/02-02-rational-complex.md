# 02-02. Rational과 Complex exact numeric

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

`Rational`과 `Complex`는 현행 Stable Design의 닫힌 numeric value
profile이다. parser/checker/HIR/backend 실제 실행은 `NOT_RUN`이며,
이 장은 새 연산자 확장 권위를 만들지 않는다.

## 2. 학습 목표

- Rational `<p/q>`의 lexical 조건과 canonical normalization을 이해한다.
- 붙은 `i` 허수 리터럴의 exact Float domain을 구분한다.
- Rational/Complex의 unary·산술·equality·ordering 경계를 안다.
- power가 fixed-glyph conformance와 별도 owner라는 사실을 설명한다.

## 3. 선수 지식

numeric target adaptation, prefix sign, exact domain 개념을 알고 있어야 한다.

## 4. 문제에서 출발하기

`0.1 + 0.2` 같은 floating 계산과 정확한 분수 계산은 목적이 다르다.
또한 복소수는 실수부와 허수부의 signed zero까지 수치 의미에 영향을 줄
수 있다. Deeplus는 이를 일반 numeric widening 한 덩어리로 처리하지 않고
Rational과 `Complex<Rep>`의 identity를 닫아 둔다.

## 5. 핵심 모델

Rational source는 `<p/q>`다. 두 component는 붙어 있는 부호 없는 10진
magnitude이며, 음수는 `-<p/q>`처럼 바깥 prefix가 소유한다. 값은
BigInt numerator/denominator로 읽고 다음을 만족하도록 정규화한다.

```text
denominator > 0
gcd(abs(numerator), denominator) == 1
zero == 0/1
```

허수 리터럴은 decimal floating-look literal 뒤에 `i`가 붙은 scanner
token이다. target이 없으면 `4.0i`는 `Complex<Float64>`다. 직접 atomic
literal을 `let imaginary: Complex<Float32> = 4.0i`처럼 target에 결합할 수
있다. `4i`, `4.0 i`와 제거된 type suffix를 섞은 `4.0f64i`는 허용되지
않는다.

## 6. 단계별 예제

source spelling과 canonical 값의 차이를 확인한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let reduced: Rational = <6/8>
let zero: Rational = <0/25>
let negative: Rational = -<2/3>
```

lossless CST에는 `<6/8>`이 남지만 값 identity는 `3/4`다. `zero`는
canonical `0/1`이며 floating approximation을 거치지 않는다.

복소수의 권장 Cartesian source는 실수와 붙은 허수 literal을 더한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let signal: Complex = 3.0 + 4.0i
let compactReal: Float32 = 1.0
let compact: Complex<Float32> = compactReal - 2.0i
let rotated: Complex = Complex::i * signal

let rate: Rational = <3/100>
let scaled: Rational = 5 * rate
let quotient: Rational = <7/3> / <2/3>
let remainder: Rational = <7/3> % <2/3>
let ordered: Bool = <1/3> < <1/2>

let divided: Complex = signal / (1.0 - 1.0i)
```

`3.0 + 4.0i`는 일반적인 “real을 Complex로 바꾸는” conversion search가
아니라, exact `(Float64, Complex<Float64>)` sealed 표준 `BinaryAdd`
row를 선택한다. 반면 결과 annotation만으로 binary operand 둘을
`Float32`로 역전파하지 않는다. nondefault operator domain이 필요하면
`compactReal`처럼 이미 typed된 operand 하나가 candidate를 고정해야 한다.

### 판정 trace, 미니 사례와 흔한 오해

Rational은 `<p/q>` token을 읽은 뒤 denominator가 0이 아닌지 확인하고,
부호와 최대공약수로 normalized pair를 만든다. Complex expression에서는
먼저 real/imaginary operand domain을 고르고, 선택된 `+` operation이
Complex result를 만드는지 판정한다. `3.0 + 4.0i`의 `i`는 독립 변수나
후위 곱셈이 아니라 imaginary literal suffix의 일부다. power까지 이어지면
base와 exponent domain, negative exponent corridor, result domain을
따로 기록한다.

미니 사례에서 `<2/4>`와 `<1/2>`는 source spelling은 다르지만 같은
normalized Rational value다. 반면 `0.5`는 Float representation과 rounding
책임을 가진 별도 값이다. 흔한 오해는 `4i`나 `4.0f64i`처럼 익숙한 다른
언어 spelling도 허용될 것이라는 가정이다. 현행 imaginary literal은
정확한 admitted form만 사용하며, 실패 spelling을 곱셈으로 재해석하지
않는다.

사용 시점도 구분한다. 세금 비율, 비례식처럼 분수 정확성이 계약이면
Rational을 선택하고, 측정 오차와 근사 알고리즘이 본질이면 Float 정책을
명시한다. 회전·주파수처럼 실수부와 허수부가 함께 움직이는 값에는
Complex를 쓴다. 단지 표기가 짧다는 이유로 모든 수를 Rational이나
Complex로 올리면 operation set과 failure 책임이 오히려 불분명해진다.

## 7. 허용·거부·경계 사례

분모 0은 전체 Rational 후보로 인식한 뒤 정적으로 거부한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: RATIONAL_LITERAL_* -->
```deeplus
let invalid: Rational = <2/0>
```

- `<2 / 3>`, `<-2/3>`, `<0x2/3>`도 malformed다.
- `Rational / Rational`은 sealed `Divide<Rational>` row이고 0 제수는
  commit 전 `ArithmeticDefect`다. 상세 recoverable 실패가 필요하면
  named `dividedBy` API를 사용한다.
- `Rational ^ Int`는 초기 power matrix에 없고
  `POWER_OPERAND_DOMAIN_NOT_ADMITTED`다.
- Rational `%`는 `q = truncTowardZero(a / b)`, `r = a - q * b`를
  만족하고 0 제수는 commit 전 `ArithmeticDefect`다.
- Complex division은 같은 exact `Rep`에 한정된 sealed `Divide` row다.
- Complex에는 암시적 `Ord`, `Hash`, `Keyable` evidence가 없다.

## 8. 다른 기능과의 연결

Rational constant는 HIR에서 정규화된 `RationalConst`로, Complex literal은
component bit identity를 보존한 `ComplexLiteral`로 간다. `Complex`
principal power는 branch cut에서 imaginary `+0.0`/`-0.0`을 지우면 안
된다. 이 의미 계약은 struct field offset이나 ABI layout을 정하지 않는다.

## 9. Deeplus다운 작성 관례

- exact ratio가 목적이면 Float로 근사하지 않고 Rational을 쓴다.
- 복소수 source는 `3.0 + 4.0i`처럼 Cartesian 의도를 드러낸다.
- Float32/Float64 Complex를 한 식에서 숨게 섞지 않는다.
- 간결한 산술에는 `/`, 상세 recoverable 실패가 필요하면 named checked
  API를 사용한다.
- unsupported power를 결과 annotation으로 강제하지 않는다.

## 10. 연습 문제

1. **따라 하기:** `<10/20>`, `<0/7>`, `-<9/12>`의 canonical Rational
   값을 적는다.
2. **빈칸 완성:** `Complex<Float32>`의 순허수 2를 나타내는 literal은
   `___`이다.
3. **스스로 설계하기:** 정확한 할인율 두 개와 Complex 신호 하나를
   선언하고, 각 연산이 선택하는 exact operand/result domain을 표로
   정리한다.

## 11. 빠른 복습

- Rational component는 붙은 부호 없는 10진 magnitude다.
- 음수 부호는 literal 바깥 prefix가 소유한다.
- floating-look `4.0i`가 유일한 imaginary suffix 표면이며 target이 Rep를 고정한다.
- Rational은 unary `+`/`-`, binary `+`/`-`/`*`/`/`/`%`, strong
  `Eq`와 total `Ord`를 지원한다.
- Complex는 unary `+`/`-`, binary `+`/`-`/`*`/`/`와 기존 partial
  equality를 지원하지만 `%`와 `Ord`는 지원하지 않는다.
- Rational power는 fixed-glyph fallback으로 만들지 않는다.

## 12. 정본 근거와 다음 장

- [Rational/imaginary 어휘](../../grammar-reference/01-lexical-structure.md)
- [Rational/Complex 연산](../../grammar-reference/08-expressions-and-operators.md)
- [numeric coherence contract](../../../spec/contracts/rational-complex-numeric-coherence.json)
- [HIR constant residue](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음은 [String, Char, Bytes, `#raw`](02-03-text-bytes-raw.md)를 다룬다.
