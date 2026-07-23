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
소유 parser 문맥에서만 허용한다. 특히 `array`와 `case`는 ordinary
identifier다.

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

현행 raw String delimiter는 `raw"..."` 하나뿐이다. body에는 escape와
interpolation을 적용하지 않는다. multiline Unicode String은 triple
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
let path = raw"C:\temp\$name"
```

마지막 예제의 backslash와 dollar sign은 raw body text이며 interpolation이
아니다.

## 거부되거나 격리된 형식

| 형식 | 판정과 대안 |
|---|---|
| `null` | recovery-only; `::none` 또는 `Option<T>::none` 사용 |
| 숫자 token으로 쓴 `NaN`, `Infinity` | 거부; type-side constant 사용 |
| raw multiline String | 거부 |
| 다른 raw delimiter family | 거부; `raw"..."`만 현행 |
| regex literal | 없음; named API에 String/Bytes 전달 |
| 단독 `_`를 이름으로 사용 | wildcard이므로 거부 |
| `array`, `case`를 hard keyword로 취급 | 잘못된 해석 |
| 임의 custom operator punctuation | recovery-only이며 stable token route가 아님 |

Preview source는 첫머리에 명시적 `#preview(...)` gate가 필요하다. 이 장은
Preview feature를 현행으로 승격하지 않는다.

## 상호작용

- 숫자 부호는 lexing 뒤 expression prefix operator가 소유한다.
- interpolation의 braced body는 ordinary expression parser가 소유한다.
- newline은 declaration, statement, match arm, layout 문맥이 boundary
  여부를 판단할 수 있도록 보존된다.
- `#bytes`, `#map`, `#set`, `#mut`, `#preview`는 parent grammar goal이
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
- [`spec/language.md`](../../spec/language.md)
- [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
