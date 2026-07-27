# 02-03. String, Char, Bytes와 `#raw`

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`
> **제품 증거:** `15/15 NOT_RUN`

이 장의 plain/interpolated/raw/multiline String, Char, Bytes lexical
표면은 CURRENT다. 실제 encoding I/O나 formatter 실행은 주장하지 않는다.

## 2. 학습 목표

- `Char`, `String`, `Bytes`의 값 domain을 구분한다.
- plain String interpolation과 raw String body를 구분한다.
- shorthand interpolation과 `${expr}`의 용도를 안다.
- text와 byte sequence 사이의 암시적 변환이 없음을 이해한다.

## 3. 선수 지식

literal, type annotation, semantic/representation identity를 이해해야 한다.

## 4. 문제에서 출발하기

경로 문자열 `C:\temp\$name`에서 backslash와 dollar를 있는 그대로
보존하고 싶을 때 ordinary String escape와 interpolation을 하나씩
피하는 것은 읽기 어렵다. 반대로 사용자 이름을 문자열에 넣고 싶을 때
raw String을 쓰면 interpolation이 일어나지 않는다. 두 의도를 delimiter로
분리해야 한다.

## 5. 핵심 모델

- `Char`: Unicode scalar 정확히 하나.
- plain String: `"..."`, escape를 처리한다.
- interpolated String: `$name`, `$name.member`, `${expression}`.
- raw String: `#raw"..."`, escape와 interpolation을 적용하지 않는다.
- Bytes: `#bytes"..."`, Unicode String과 다른 byte sequence.

`#`, `raw`, 여는 quote는 붙어 있어야 한다. raw multiline String은
현행 표면에 없다.

## 6. 단계별 예제

세 text-related domain을 명시적으로 나눈다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let initial: Char = 'D'
let language: String = "Deeplus"
let magic: Bytes = #bytes"\x44\x50"
```

`initial`은 UTF-8 byte 한 개라는 뜻이 아니라 Unicode scalar 하나다.
`magic`은 String이 아니므로 text API에 자동 전달되지 않는다.

ordinary interpolation과 raw body의 차이를 보자.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let learner: String = "Mina"
let lesson: Int = 2
let title: String = "$learner - lesson ${lesson + 1}"

let path: String = #raw"C:\temp\$learner"
```

`title`은 shorthand와 braced expression을 평가한다. `path`의 backslash와
`$learner`는 그대로 body text다.

여러 줄의 설명·query·template를 표현할 때는 triple-quoted String을
사용한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let learner = "Mina"
let welcome = """
    안녕하세요, ${learner}님.

    Deeplus 튜토리얼의 여러 줄 문자열입니다.
        이 줄의 추가 네 칸은 값에 남습니다.
    """
```

opener 뒤 newline과 독립된 closer line이 필수다. closer의 들여쓰기가
공통 여백을 정하므로 위 예제의 비어 있지 않은 각 내용 줄에서는 네
칸을 제거한다. 빈 줄과 내용 줄 사이의 newline은 값에 남는다.
multiline String도 escape와 interpolation을 처리하므로 literal text를
그대로 보존해야 한다면 한 줄 `#raw"..."`를 사용하거나 명시적 파일/API
경계를 선택한다. 한 줄 triple quote와 raw multiline 형식은 없다.

### 판정 trace, 미니 사례와 흔한 오해

text literal은 delimiter와 prefix를 먼저 판정한다. plain String이면
escape와 interpolation hole을 source order로 읽고, `#raw`이면 body의
backslash와 dollar를 그대로 보존한다. `#bytes`이면 Unicode text가 아니라
byte sequence domain을 선택한다. 그다음 expected type과 각 interpolation
expression의 effect/error를 확인한다. 마지막으로 encoding이나 decoding이
필요한 지점은 별도 API 경계로 남긴다.

미니 사례에서 `"$name"`은 binding을 읽지만 `#raw"$name"`은 body를
그대로 보존한다. `#bytes"DP"`는 화면에 같은 문자가 보여도 String이
아니다. 흔한 오해는 raw literal이 “파일 경로 전용 문자열”이거나 Bytes가
“더 빠른 String”이라는 생각이다. 둘은 사용 목적이 아니라 lexical
처리와 value domain이 다르다.

사용 시점은 delimiter 편의가 아니라 데이터 경계로 정한다. 사용자가
읽고 편집하는 내용은 String, protocol header나 암호화 입력처럼 byte가
identity인 값은 Bytes다. raw String은 text이되 source escape와
interpolation을 끄고 싶을 때 사용한다. decoding이 실패할 수 있거나
replacement policy가 필요하면 그 선택을 변환 API의 Result/error
계약에 남기며 literal 자체가 정책을 추측하지 않는다.

검토 표에는 code point 수, byte 수, 사용자에게 보이는 grapheme 수도
서로 다른 열로 둔다. Char 하나가 화면의 글자 하나나 UTF-8 byte 하나와
항상 같다고 가정하지 않는다.

## 7. 허용·거부·경계 사례

String과 Bytes를 같은 값으로 대입해도 안 된다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: STRING_NOT_IMPLICITLY_CONVERTIBLE_TO_BYTES -->
```deeplus
let packet: Bytes = "DP"
```

명시적인 encoding/decoding API는 failure, replacement policy, effect를
드러내야 한다. interpolation shorthand 뒤에 call-like `(`를 이어
복잡한 식을 만들지 말고 `${...}`를 사용한다.

## 8. 다른 기능과의 연결

interpolation hole은 source order로 한 번씩 평가되고 각 expression의
effect/error/suspension을 그대로 보존한다. `String::render`는 명시적
renderer helper이지 interpolation의 hidden hook가 아니다. raw String은
HIR `ConstString`으로 내려가며 `$`에 별도 의미가 없다.

## 9. Deeplus다운 작성 관례

- text와 protocol bytes를 타입으로 구분한다.
- 단순 경로는 shorthand, 복잡한 식은 `${...}`를 쓴다.
- escape/interpolation이 모두 불필요할 때 `#raw`를 쓴다.
- byte decoding 정책을 암시하지 않는다.
- Unicode scalar와 사용자가 보는 grapheme를 같은 것으로 설명하지 않는다.

## 10. 연습 문제

1. **따라 하기:** 이름과 점수를 보간한 String, `$`를 그대로 가진 raw
   String, 두 byte를 가진 Bytes를 각각 선언한다.
2. **빈칸 완성:** escape와 interpolation이 없는 raw delimiter는
   `___"..."`이다.
3. **스스로 설계하기:** 파일 경로, 사용자 표시 이름, wire header를 각각
   어떤 타입과 literal로 표현할지 정하고 변환이 필요한 경계를 설명한다.

## 11. 빠른 복습

- Char는 scalar 하나, String은 Unicode text, Bytes는 byte sequence다.
- `#raw"..."`에서는 escape와 interpolation이 없다.
- `$name`은 shorthand, `${expr}`는 일반 expression hole이다.
- text/bytes 암시 변환은 없다.
- interpolation evaluation은 원래 effect와 순서를 숨기지 않는다.

## 12. 정본 근거와 다음 장

- [문자열 lexical EBNF](../../../spec/grammar/deeplus.ebnf)
- [어휘 구조](../../grammar-reference/01-lexical-structure.md)
- [String evaluation](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [value/operator contract](../../../spec/contracts/value-operator-indexing-coherence.json)

다음은 [연산자, power와 Bool](02-04-operators-power-boolean.md)을 배운다.
