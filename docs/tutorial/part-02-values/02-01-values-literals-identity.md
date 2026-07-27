# 02-01. 값, 리터럴과 identity

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 Stable scalar, Unit, Bool, numeric, Char, String, Bytes literal과
semantic identity 분리를 다룬다. storage 크기나 backend layout을
추측하지 않는다.

## 2. 학습 목표

- 리터럴 철자, 정규화된 값, 타입을 구분한다.
- suffix가 exact numeric domain을 고정한다는 사실을 이해한다.
- semantic identity와 representation identity를 분리한다.
- mixed numeric operation이 자동 widening되지 않는 이유를 설명한다.

## 3. 선수 지식

`let` 바인딩과 명시적 type annotation을 읽을 수 있어야 한다.

## 4. 문제에서 출발하기

소스의 `42`, `42i32`, `42u32`는 수학적으로 같은 크기를 나타낼 수 있지만
같은 Deeplus 타입은 아니다. 정적 연산은 width와 signedness를 지운 뒤
“적당히 큰 타입”을 고르지 않는다. 어떤 domain을 사용했는지가 overflow,
API identity, HIR/MIR 책임에 남기 때문이다.

## 5. 핵심 모델

- `()`는 유일한 `Unit` 값이다.
- `true`, `false`는 `Bool`이다.
- suffix 없는 integer는 기본 `Int`다.
- `UInt`는 별도 64-bit unsigned 기본 의미 domain이며 `UInt64` 별칭이 아니다.
- suffix 없는 decimal float는 `Float64`, `f32`는 `Float32`다.
- `Float`는 새 정밀도나 ABI를 만들지 않는 `Float64`의 닫힌 별칭이다.
- 부호는 token의 일부가 아니라 prefix expression이다.
- `Char`는 Unicode scalar 하나다.
- String과 Bytes 사이에는 암시적 변환이 없다.

리터럴의 source spelling은 lossless CST에 남고, 정규화 값은 typed HIR에
들어간다. 둘은 다시 storage layout이나 ABI identity와도 구분된다.

## 6. 단계별 예제

기본 literal을 명시적 타입에 결합해 보자.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let nothing: Unit = ()
let enabled: Bool = true
let count: Int = 42
let mask: UInt = 42
let exact: Int32 = 42i32
let ratio: Float = 1.5
let compact: Float32 = 1.5f32
```

`42`는 기본적으로 `Int`, `42i32`는 `Int32`다. `mask`의 독립적인 target
type이 먼저 `UInt`로 고정되어 있고 값이 정확히 표현 가능하므로 signless
literal이 그 domain에 제한적으로 적응한다. 이것은 signedness 사이의
일반 implicit conversion이 아니다. `ratio`의 `Float`는 정규화 뒤 정확히
`Float64`다.

Unicode 값과 byte 값도 분리한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let mark: Char = '\N{COPYRIGHT SIGN}'
let word: String = "Deeplus"
let header: Bytes = #bytes"\x44\x50"
```

`mark`는 byte나 grapheme cluster가 아니라 scalar 하나다. `header`를
String에 대입하거나 `word`를 Bytes에 대입하려면 별도의 명시적 API
계약이 필요하다.

### 판정 trace, 미니 사례와 흔한 오해

literal을 만나면 먼저 token spelling과 suffix를 읽고, expected type이
있는지 확인한 뒤 semantic value identity를 결정한다. 그다음 실제 저장
representation이 언어 의미에 노출되는지 구분한다. `let count = 3`과
`let count: Int = 3`은 이 문맥에서 같은 Int domain으로 수렴할 수 있지만,
`3.0`이나 `<3/1>`을 같은 값이라고 자동 대입하지 않는다. conversion이
필요하면 어느 corridor가 그 책임을 소유하는지 별도로 찾는다.

미니 사례로 `let code: UInt8 = 255`는 exact literal이 범위 안인지
정적으로 판정할 수 있다. `256`은 representation에서 우연히 잘릴 값이
아니라 domain 모순이다. 흔한 오해는 literal의 모양이 곧 runtime byte
layout이라는 생각이다. semantic identity가 먼저이고 ABI/serialization
tag는 별도 계약이므로, 화면에 같은 숫자가 보여도 그 경계를 생략하지
않는다.

## 7. 허용·거부·경계 사례

exact domain이 다른 두 정수를 operator가 자동 통합하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: OPERATOR_CONFORMANCE_REQUIRES_EXPLICIT_CONVERSION -->
```deeplus
let left: Int32 = 1i32
let right: UInt32 = 2u32
let mixed = left + right
```

명시적인 checked conversion으로 한 domain을 먼저 고정해야 한다.
`NaN`과 `Infinity`는 lexical literal이 아니며
`Float64::nan`, `Float64::positiveInfinity` 같은 type-side constant를
사용한다. `-1`은 signless `1`에 prefix `-`를 적용한 expression이다.

## 8. 다른 기능과의 연결

operator admission은 literal context adaptation 뒤 exact normalized
operand domain을 검사한다. closed Union은 값의 injection identity를,
Enum은 `(EnumId, VariantId)`를 사용한다. 어떤 경우에도 semantic identity를
serialization tag나 runtime discriminant와 직접 동일시하지 않는다.

## 9. Deeplus다운 작성 관례

- public boundary와 domain-sensitive 계산에는 타입을 명시한다.
- suffix는 크기 과시가 아니라 exact domain 계약이 필요할 때 쓴다.
- String과 Bytes를 역할에 따라 분리한다.
- backend 크기나 ABI를 source 타입 설명에 끌어오지 않는다.
- 숨은 widening을 기대하지 않고 conversion을 의도적으로 표시한다.

## 10. 연습 문제

1. **따라 하기:** `Int`, `Int16`, `Float32` 값을 각각 하나씩 선언하고
   어떤 literal suffix를 사용했는지 적는다.
2. **빈칸 완성:** suffix 없는 소수 `2.5`의 기본 타입은 `___`이고,
   `2.5f32`의 타입은 `___`이다.
3. **스스로 설계하기:** 네트워크 packet 길이와 사용자 화면의 개수를
   서로 다른 exact domain으로 표현하고, 왜 자동 혼합을 피해야 하는지
   설명한다.

## 11. 빠른 복습

- literal spelling, semantic value, storage/ABI는 다른 identity 층이다.
- integer sign은 prefix operator가 소유한다.
- suffix는 exact width/domain을 고정한다.
- String, Char, Bytes는 암시적으로 섞이지 않는다.
- mixed width/signedness operator는 hidden conversion 없이 거부한다.

## 12. 정본 근거와 다음 장

- [어휘 EBNF](../../../spec/grammar/deeplus.ebnf)
- [어휘 구조 참고서](../../grammar-reference/01-lexical-structure.md)
- [타입 정규화](../../../spec/types/type-system.md)
- [MIR의 identity 분리](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음은 [Rational과 Complex](02-02-rational-complex.md)에서 정확 수와
복소수의 특별한 lexical/value law를 배운다.
