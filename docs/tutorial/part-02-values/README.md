# Part 2. 값, 리터럴과 표현식

> **부 상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 실행:** `15/15 NOT_RUN`

이 부는 source에 적힌 리터럴이 어떤 의미 값이 되고, 연산자가 그 값을
어떤 정적 domain에서 결합하는지 배운다. Deeplus는 값의 semantic
identity를 storage layout, serialization tag, runtime discriminant,
foreign ABI와 분리한다. 같은 값이라고 해서 같은 byte 표현이나 같은
backend 배치를 뜻하지 않는다.

모든 예제는 `CURRENT_DESIGN_PRODUCT_NOT_RUN`인 설계 정적 설명이다.
product lane은 `15/15 NOT_RUN`이며 실제 수치 backend 실행을 주장하지
않는다.

## 학습 순서

1. [값, 리터럴, identity](02-01-values-literals-identity.md)
2. [Rational과 Complex](02-02-rational-complex.md)
3. [String, Char, Bytes, `#raw`](02-03-text-bytes-raw.md)
4. [연산자, power와 Bool](02-04-operators-power-boolean.md)
5. [표현식과 평가 순서](02-05-expressions-evaluation-order.md)
6. [실습: 예산과 복소 신호](lab-02-budget-complex-signal.md)

## 이 부의 학습 판정 trace

값을 읽을 때는 source spelling, semantic domain, representation,
operation result를 한 줄로 합치지 않는다. 먼저 scanner가 suffix-free
literal spelling을 고르고, checker가 direct atomic literal의 유효한
declared target에서 exact domain을 확정한다. target이 없으면 `Int`,
`Float64`, `Complex<Float64>`로 default하며 suffix나 smallest-fit
inference를 사용하지 않는다. 그다음 operator owner와 adaptation plan을 고르고,
마지막에 source order와 failure/commit을 기록한다. 예를 들어 `4.0i`는
imaginary literal이고 `3.0 + 4.0i`는 두 값을 더해 Complex를 만드는
expression이다. 둘을 하나의 특별한 “복소수 문자열”로 해석하지 않는다.

## 흔한 오해와 미니 사례

`1`, `1.0`, `<1/1>`이 화면에 같은 수를 나타낸다고 같은 identity가 되는
것은 아니다. Int, Float, Rational은 연산 corridor와 실패 방식이 다르다.
또 `and`와 `and then`은 철자만 다른 동의어가 아니며 오른쪽 평가와
narrowing 전달이 달라진다. 미니 사례를 풀 때는 값 표, 선택된 연산,
평가 순서, 예상 실패의 네 열을 작성한다. optimizer가 결과만 같게
만든다고 해도 이 관찰 가능한 순서를 재해석할 수 없다.

## 이 부를 마치면

- suffix-free direct atomic numeric literal의 exact declared-target adaptation
  (`ISize`/`USize` 포함)과 `Int`/`Float64`/`Complex<Float64>` default를
  구분한다.
- 제거된 14개 numeric type suffix (`i8`, `i16`, `i32`, `i64`, `i128`,
  `isize`, `u8`, `u16`, `u32`, `u64`, `u128`, `usize`, `f32`, `f64`)
  candidate가 `NUMERIC_TYPE_SUFFIX_REMOVED` 하나로 거부됨을 설명한다.
- `<p/q>`와 붙은 `i` 리터럴을 정확히 쓴다.
- String, Char, Bytes와 raw String의 경계를 설명한다.
- Bool word operator와 pointwise double-glyph operator를 구분한다.
- 오른쪽 결합 power와 numeric prefix의 결합을 괄호 없이도 읽는다.
- 왼쪽부터 정확히 한 번인 평가와 atomic commit을 설명한다.

## 학습할 때 지킬 경계

- 임의 custom operator는 current나 Preview 설계가 아니다.
- Stable fixed-glyph conformance는 unary `+`/`-`, binary
  `+`/`-`/`*`/`/`/`%`, equality `==`/`!=`, ordering
  `<`/`<=`/`>`/`>=`의 정확한 13개 역할뿐이다.
- numeric 혼합 domain을 hidden widening으로 보정하지 않는다.
- 예상 결과는 정적 의미 설명이며 실행 receipt가 아니다.

## 정본 찾아가기

- [어휘 구조](../../grammar-reference/01-lexical-structure.md)
- [표현식과 연산자](../../grammar-reference/08-expressions-and-operators.md)
- [값·연산·인덱싱 계약](../../../spec/contracts/value-operator-indexing-coherence.json)
- [타입 시스템](../../../spec/types/type-system.md)
