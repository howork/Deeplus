# 어휘 구조

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 Deeplus `0.1.2-internal`의 현행 어휘 설계를 독자용으로 재구성한
문서 투영이다. 정본 grammar, scanner vocabulary, value contract를
대체하지 않는다.

현행 예제는 `examples/guide/review-corpus.md`에서
`expected_outcome: accept`, `source_activation: none`인 항목을 그대로
복사했다. 모두 설계 정적 증거이며 제품 lexer/parser/checker/formatter/
runtime은 `NOT_RUN`이다.

이 장에서 추가로 설명하는 정확 수와 복소수의 registry identity는 각각
`rational_exact_numeric_value`, `complex_core_numeric_value`다. 이 이름은
기능을 식별하기 위한 정적 identity이지, 문서가 제품 구현이나 실행을
증명한다는 뜻이 아니다. 관련 15개 제품 lane은 모두 `NOT_RUN`이다.

## 문법

### 소스 문자와 줄 끝

```ebnf
SourceCharacter ::= UnicodeScalar
LineTerminator  ::= "\r\n" | "\n"
HorizontalSpace ::= " " | "\t"
```

어휘 정본은 Unicode 15.1 scalar를 사용한다. source spelling은 보존되며
identifier에 NFC/NFD 정규화를 암시적으로 적용하지 않는다. 도구는 혼동
가능성을 진단할 수 있지만 normalization을 이름 동등성으로 삼지 않는다.

### 식별자, 와일드카드, 단어 역할

```ebnf
IDENTIFIER         ::= UnicodeXIDStart IdentifierContinue*
                     | "_" IdentifierContinue+
IdentifierContinue ::= UnicodeXIDContinue
WILDCARD           ::= "_"
```

단독 `_`는 항상 wildcard다. `_` 뒤에 identifier-continue 문자가 있으면
identifier다.

scanner hard keyword 30개는 다음과 같다.

```text
and as catch class def defer else enum false finally for if import in
let match module not null or repeat return throw trait true try type
use var while
```

`null`은 정밀한 recovery 진단을 위한 예약어일 뿐 현행 값 literal이 아니다.
`actor`, `async`, `await`, `conformance`, `effects`, `entry`, `guard`,
`move`, `public`, `schema`, `throws`, `where` 같은 contextual word는
소유 parser 문맥에서만 허용한다. `array`와 `case`는 이 두 keyword
목록뿐 아니라 sigil-role 목록에도 들어가지 않으며, 항상 ordinary
`IDENTIFIER`로 시작한다.

### 주석과 부가 정보

```ebnf
LineComment        ::= "//" LineCommentScalar*
DocLineComment     ::= "//!" DocLineCommentScalar*
NestedBlockComment ::= BlockCommentOpen BlockCommentItem* BlockCommentClose
BlockCommentOpen   ::= "//" DashRun
BlockCommentClose  ::= DashRun "//"
DocBlockComment    ::= "//!!" DocBlockCommentScalar* "!!//"
WordComment        ::= "`" WordCommentScalar+
```

block comment는 중첩된다. 양의 길이를 가진 dash-run closer는 가장 안쪽
comment를 닫으며 opener와 dash 수가 같지 않아도 된다. 불일치는 style
warning 대상이 될 수 있다. 공백, comment, 물리적 줄 끝은 lossless
trivia이며 newline의 statement/layout boundary 판단은 parent 문맥이 한다.

shebang은 `#!`로 시작해 첫 line terminator에서 끝나며 script source의
처음에서만 허용한다.

### 숫자 literal

```ebnf
NUMERIC_LITERAL ::= FLOAT_LITERAL | INTEGER_LITERAL
INTEGER_LITERAL ::= BinaryInteger IntegerSuffix?
                  | OctalInteger IntegerSuffix?
                  | HexInteger IntegerSuffix?
                  | DECIMAL_INTEGER IntegerSuffix?
FLOAT_LITERAL   ::= DecimalFraction ExponentPart? FloatSuffix?
                  | DECIMAL_INTEGER ExponentPart FloatSuffix?
                  | DECIMAL_INTEGER FloatSuffix

RATIONAL_LITERAL_CANDIDATE
                ::= "<" DecimalMagnitude "/" DecimalMagnitude ">"
IMAGINARY_LITERAL
                ::= UnsuffixedDecimalFloat AttachedImaginaryMarker
                  | Float32Literal AttachedImaginaryMarker
UnsuffixedDecimalFloat
                ::= DecimalFraction ExponentPart?
                  | DECIMAL_INTEGER ExponentPart
Float32Literal  ::= DecimalFraction ExponentPart? "f32"
                  | DECIMAL_INTEGER ExponentPart "f32"
                  | DECIMAL_INTEGER "f32"
AttachedImaginaryMarker ::= "i"
```

2진수, 8진수, 16진수 prefix는 `0b`, `0o`, `0x`다. digit 사이에는
underscore를 둘 수 있다. integer suffix는 다음과 같다.

```text
i8 i16 i32 i64 i128 isize
u8 u16 u32 u64 u128 usize
```

float suffix는 `f32`, `f64`다. 부호는 숫자 token의 일부가 아니므로 `-1`은
signless token `1`에 prefix `-`를 적용한 expression이다. NaN과 infinity는
literal token이 아니며 `Float64::nan`, `Float64::positiveInfinity` 같은
type-side constant를 사용한다.

위 EBNF의 두 마지막 형식은 ordinary 숫자 token과 소유 방식이 다르다.
`<p/q>`는 식의 prefix 또는 primary가 시작될 수 있는 위치에서만
transactional하게 탐사하는 복합 리터럴이고, 허수 리터럴은 이미 유효한
unsuffixed 10진 부동소수 또는 `f32` literal 바로 뒤에 ASCII `i`가 붙은
하나의 최장 일치 scanner token이다. 명시적 `f64` 뒤에 `i`를 다시 붙이는
suffix 연쇄는 허용하지 않는다. 두 규칙 모두 type parser나 임의 identifier
문맥에서 추측으로 켜지지 않는다.

### 정확한 Rational 복합 리터럴

`Rational`의 source 형식은 `<p/q>`다. `p`와 `q`는 기존 underscore 규칙을
따르는 부호 없는 10진 정수 크기이며, 다음 요소는 내부에 둘 수 없다.

- `+` 또는 `-` 부호
- `0b`, `0o`, `0x` 기수 prefix
- `i32`, `u64` 같은 integer suffix
- 공백, 줄바꿈 또는 comment
- `/`가 아닌 다른 separator

음수는 `-<2/3>`처럼 리터럴 바깥의 ordinary prefix `-`가 소유한다.
따라서 CST는 부호와 리터럴을 별도 node로 보존하고, formatter가
`<-2/3>` 같은 새 spelling을 발명하지 않는다.

scanner/parser의 탐사는 다음 순서로 fail-closed하게 동작한다.

1. parent parser가 현재 위치를 expression-prefix goal로 확정한다.
2. scanner가 입력 위치에 checkpoint를 만든다.
3. `<`, 첫 decimal magnitude, `/`, 둘째 decimal magnitude, `>`의 정확한
   전체 모양을 확인한다.
4. 전체 모양이 완성되지 않으면 checkpoint로 돌아가며, 이 탐사로 소비된
   token 수는 0이다.
5. 완성되면 하나의 Rational literal 후보를 만들고, checker가 분모와
   resource limit을 검사한다.

이 transactional 규칙 때문에 `a < 2 / 3 > b`는 비교와 나눗셈으로,
`Box<Int>`는 type argument로 그대로 해석된다. type parser에서는 Rational
literal goal 자체가 꺼져 있으므로 `Box<2/3>`을 값 인자로 오인하지 않는다.
`<2/3>>x`에서는 첫 `>`까지만 Rational literal이 소유하고, 다음 `>`는
바깥 비교 연산자가 소유한다.

리터럴의 두 component는 고정 폭 정수가 아니라 `BigInt` magnitude로
읽힌다. 승인된 값은 HIR 경계에서 다음 canonical invariant를 만족한다.

```text
denominator > 0
gcd(abs(numerator), denominator) == 1
zero == 0/1
```

예를 들어 `<6/8>`의 source spelling은 lossless CST에 남지만 값 identity는
`3/4`다. `<0/25>`도 값으로는 `0/1`이다. 정규화 과정에 wrap, saturate,
근삿값 변환 또는 `Float64` 경유는 없다. 분모가 0인 `<2/0>`은 전체
리터럴로 인식한 다음 `RATIONAL_LITERAL_DENOMINATOR_ZERO`로 정적으로
거부하며, malformed 후보는 `RATIONAL_LITERAL_MALFORMED`로 진단한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let reduced: Rational = <6/8>     // canonical value 3/4
let zero: Rational = <0/25>       // canonical value 0/1
let negative: Rational = -<2/3>   // prefix '-' + Rational literal
```

### 붙은 `i` 허수 리터럴 marker

허수 리터럴은 admitted unsuffixed 또는 `f32` decimal floating magnitude
뒤에 공백 없이 `i`가 붙어야 한다.
`4.0i`는 실수 성분이 `+0.0`, 허수 성분이 `4.0`인
`Complex<Float64>`이고, `4.0f32i`는 두 성분이 `Float32`인
`Complex<Float32>`다. bare `Complex`는 닫힌 Prelude 약칭
`Complex<Float64>`로 정규화된다.

```text
4.0i       -> Complex<Float64>(real: +0.0, imag: 4.0)
4.0f32i    -> Complex<Float32>(real: +0.0f32, imag: 4.0f32)
3.0 + 4.0i -> canonical Cartesian source expression
```

`i`는 hard keyword도 전역 허수 상수도 아니다. 단독 `i`는 ordinary
identifier이며 명시적 허수 단위는 `Complex::i`다. Deeplus는 implicit
multiplication을 제공하지 않으므로 `4.0 i`를 `4.0 * i`로 보정하지
않는다.

최장 일치는 유효한 prefix만 떼어 내지 않는다. 따라서 `4.0index`를
`4.0i`와 `ndex`로 쪼개거나, `4.0f64i`를 `4.0f64`와 `i`로 쪼개지 않는다.
정수형 `4i`, bare `i`, 분리된 `4.0 i`, historical `4.0j`, radix 형식
`0x4.0i`, suffix 연쇄 `4.0f64i`는 모두 거부된다. 진단은 다음 책임을
구분한다.

| source | 판정 |
|---|---|
| `4.0 i` | `IMAGINARY_LITERAL_MARKER_MUST_BE_ATTACHED` |
| `4i`, `0x4.0i`, `4.0f64i`, chained suffix | `IMAGINARY_LITERAL_FORM_NOT_ADMITTED` |
| `4.0j` | `HISTORICAL_IMAGINARY_J_NOT_CURRENT` |
| bare `i` | ordinary identifier; 허수 literal이 아님 |

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let axis: Complex = 4.0i
let compact: Complex<Float32> = 4.0f32i
let cartesian: Complex = 3.0 + 4.0i
let unit: Complex = Complex::i
```

### 문자, 문자열, 바이트

```ebnf
CHAR_LITERAL ::= "'" CharScalar "'"
CharScalar   ::= DirectCharScalar | SimpleCharEscape
               | UnicodeScalarEscape | NamedUnicodeEscape

StringLiteralExpr ::= PLAIN_STRING_LITERAL
                    | RAW_STRING_LITERAL
                    | MULTILINE_STRING_LITERAL
                    | InterpolatedString
BytesLiteral      ::= BYTES_LITERAL
```

`Char`는 정확히 하나의 Unicode scalar이며 byte, UTF-16 code unit,
grapheme cluster가 아니다. simple escape, `\u{...}`, `\N{...}`를
사용할 수 있다.

plain String은 double quote를 쓴다. interpolation은 `${expr}`와 `$name`,
`$name.member`, `$name.1`, `$name[index]`의 연속 shorthand path를
지원한다. 호출을 포함한 expression은 braced form을 사용한다.

Stable raw String delimiter는 `#raw"..."` 하나뿐이다. `#`, `raw`, 여는
따옴표 사이에 trivia를 둘 수 없다. body에는 escape와 interpolation을
적용하지 않는다. multiline Unicode String은 triple
quote를 쓰며 opener 뒤 newline과 독립된 closer line이 필요하다.
raw multiline String은 현행이 아니다.

`#bytes"..."`는 `Bytes`를 만든다. `String`, `Char`, `Bytes` 사이의
암시적 변환은 없다.

### 최장 일치 구두점

```text
::  =>  ->  ..  ..<  ..>  ...  ***  **  *+  *.
&&  ||  ^^  ?:  $$  ==  !=  <=  >=  +=  -=  *=  /=
%=  ~~  :=  !!  {{  }}  ${
```

token이 존재한다고 모든 문맥에서 의미가 생기는 것은 아니다. `..>`는
range로 거부되고 `...`는 repeated positional 및 comprehension unfold
owner만 가진다. `&&`는 Bool conjunction이 아니라 bitwise operator다.

## 허용과 정적 의미

- unsuffixed integer는 `Int`, unsuffixed float는 `Float64`로 정규화된다.
- 명시적 suffix는 정확한 numeric domain을 고정한다.
- `Char` literal은 escape 처리 뒤 정확히 하나의 Unicode scalar여야 한다.
- plain/raw/multiline/interpolated String의 type은 `String`이다.
- bytes literal의 type은 `Bytes`다.
- `()`는 유일한 `Unit` 값이다.
- absence는 `::none` 또는 `Option<T>::none`이다.
- `null` recovery는 value AST/HIR/MIR node를 만들지 않는다.
- contextual word는 owner syntax가 commit된 뒤에만 해당 역할을 얻는다.

## 평가·소유권·효과

scalar, Char, raw/plain String, Bytes constant 생성은 provider lookup을
일으키지 않는다. interpolation 안 expression은 원래의 평가 순서,
소유권, 실패, suspension, effect를 그대로 유지한다.

source value identity는 storage layout, serialization tag, runtime
discriminant, foreign ABI, backend lowering identity와 독립적이다. 어느 한
identity의 동일성을 다른 영역의 동일성으로 추정해서는 안 된다.

## 현행 예제

현행 예제 `EX-R51a1-006`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let mask = 0xDEAD_BEEFu32
let count = 0b1010_0101u8
let ratio = 6.022_140_76e23f64
let inf = Float64::positiveInfinity
```

현행 예제 `EX-R51VOI-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let count: Int = 42
let exact: Int32 = 42i32
let ratio: Float64 = 1.5
let compact: Float32 = 1.5f32
let sum: Int = count + 1
```

현행 예제 `EX-R51a1-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let png = #bytes"\x89PNG\x0D\x0A"
let mark: Char = '\N{COPYRIGHT SIGN}'
```

현행 예제 `EX-R51d-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let path = #raw"C:\temp\$name"
```

마지막 예제의 backslash와 dollar sign은 raw body text이며 interpolation이
아니다.

## 거부되거나 격리된 형식

| 형식 | 판정과 대안 |
|---|---|
| `null` | recovery-only; `::none` 또는 `Option<T>::none` 사용 |
| 숫자 token으로 쓴 `NaN`, `Infinity` | 거부; type-side constant 사용 |
| raw multiline String | 거부 |
| prefixless `raw"..."` 또는 다른 raw delimiter family | 거부; `#raw"..."` 사용 |
| regex literal | 없음; named API에 String/Bytes 전달 |
| 단독 `_`를 이름으로 사용 | wildcard이므로 거부 |
| `array`, `case`를 hard keyword로 취급 | 잘못된 해석 |
| 임의 custom operator punctuation | recovery-only이며 stable token route가 아님 |
| `<2/0>` | 전체 Rational literal로 인식한 뒤 `RATIONAL_LITERAL_DENOMINATOR_ZERO` |
| `<-2/3>`, `<2 / 3>`, `<0x2/3>` | `RATIONAL_LITERAL_MALFORMED`; 부호는 바깥 prefix에 두고 component는 붙은 10진 magnitude로 쓴다 |
| `4i`, `0x4.0i`, `4.0f64i` | `IMAGINARY_LITERAL_FORM_NOT_ADMITTED`; 붙은 marker는 10진 `Float64` 또는 `Float32` literal만 허용 |
| `4.0 i` | `IMAGINARY_LITERAL_MARKER_MUST_BE_ATTACHED`; implicit multiplication 없음 |
| `4.0j` | `HISTORICAL_IMAGINARY_J_NOT_CURRENT`; current marker는 ASCII `i` |
| bare `i`를 내장 허수 단위로 가정 | ordinary identifier다. `Complex::i`를 사용 |

Preview source는 첫머리에 명시적 `#preview(...)` gate가 필요하다. 이 장은
Preview feature를 현행으로 승격하지 않는다.

## 상호작용

- 숫자 부호는 lexing 뒤 expression prefix operator가 소유한다.
- Rational `<p/q>` 탐사는 expression-prefix goal에 한정되며 실패 시
  비교·나눗셈·type argument token을 하나도 소비하지 않는다.
- 붙은 `i`는 `FLOAT_LITERAL`과 함께 허수 literal token을 만들지만,
  detached/bare `i`에는 그런 역할이 없다.
- interpolation의 braced body는 ordinary expression parser가 소유한다.
- newline은 declaration, statement, match arm, layout 문맥이 boundary
  여부를 판단할 수 있도록 보존된다.
- `#raw`, `#bytes`, `#map`, `#set`, `#mut`, `#preview`는 parent grammar goal이
  역할을 정한다.
- `::`는 qualified path, expected Enum variant, type-side selector,
  associated projection이 문맥별로 공유한다.
- literal의 collection/index 의미는
  [컬렉션, 인덱싱, 슬라이싱](09-collections-indexing-and-slicing.md)을
  참고한다.
- punctuation의 operator 의미는
  [표현식과 연산자](08-expressions-and-operators.md)를 참고한다.

## 정본 근거

- [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- [`spec/grammar/keyword-vocabulary.json`](../../spec/grammar/keyword-vocabulary.json)
- [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- [`spec/contracts/value-operator-indexing-coherence.json`](../../spec/contracts/value-operator-indexing-coherence.json)
- [`spec/contracts/rational-complex-numeric-coherence.json`](../../spec/contracts/rational-complex-numeric-coherence.json)
- [`spec/language.md`](../../spec/language.md)
- [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
