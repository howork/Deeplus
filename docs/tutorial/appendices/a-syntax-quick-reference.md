# 부록 A — 문법 빠른 찾기

> 상태: `MIXED_STATUS`
>
> 이 표는 학습용 축약이며 `spec/grammar/deeplus.ebnf`를 대체하지 않는다.
> 모든 product 문법 실행 상태는 `NOT_RUN`이다.

## 1. source와 이름

| 의도 | 대표 표면 | 주의 |
|---|---|---|
| Module 선언 | `module app::model` | Module 경로와 파일 경로는 동일할 필요 없음 |
| 한정 이름 | `app::model::User` | namespace/type/associated owner를 단계별 해석 |
| import | `import std::math::{sin, cos}` | 모듈에서 선택한 이름을 가져옴 |
| use | `use std::units::si` | 허용된 제공자·확장 표면을 활성화하며 context·witness를 암시적으로 만들지 않음 |
| 불변 binding | `let name: String = "Ada"` | type은 추론할 수 있음 |
| 가변 binding | `var count: Int = 0` | narrowing의 stable-place 조건에 영향 |
| ordinary identifier | `array`, `case` | 두 단어는 keyword가 아님 |

Package는 배포·의존성·빌드 단위이고 Module은 이름 공간·가시성·소스
구성 단위다. 한 Package에 여러 Module이 있을 수 있으며 Module 계층을
디렉터리 계층과 강제로 같게 만들지 않는다.

## 2. literal

| 종류 | 예 | 핵심 규칙 |
|---|---|---|
| 정수 | `42`, `1_000` | suffix와 범위는 lexical/type 규칙 참조 |
| 실수 | `3.5`, `1.5f32` | IEEE Rep가 identity에 포함됨 |
| Rational | `<2/3>` | 분모는 양수, 값은 기약형으로 정규화 |
| Complex | `3.0 + 4.0i` | 허수 literal의 Rep를 맞춤 |
| Char | `'한'` | escape 처리 뒤 Unicode scalar 하나 |
| String | `"hello"` | escape와 interpolation 가능 |
| multiline String | 삼중 따옴표 | opener/closer와 indentation 규칙 적용 |
| raw String | `#raw"C:\temp\$name"` | escape·interpolation 없음 |
| Bytes | `#bytes"..."` 계열 | String과 암시 변환 없음 |

bare `i`는 ordinary identifier다. 명시적 허수 단위는 `Complex::i`다.
prefixless `raw"..."`는 현행 표면이 아니다.

## 3. 함수와 callable

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def transform<T>(
    value: T,
    context environment: Environment,
    using display: witness Display<T>,
) -> String
    throws RenderError
    effects {render}
= {
    return render(value, context environment, using display)
}
```

signature identity에는 parameter 순서·label·role·ownership mode,
return, throws, effect가 모두 참여한다. ordinary, context, witness
argument를 위치만 같다고 서로 바꿀 수 없다.

이름 있는 async 함수는 `def#async`, entry는 `def#entry`, guard는
`def#guard`다. 함수 body의 `scope#static` activation은 Stable이지만
Class body의 같은 표면은 Preview Design nonactivatable이다.

## 4. 타입

| 의도 | 표면 |
|---|---|
| alias | `type Name = String` |
| refinement | `type Positive = Int where this > 0` |
| closed Union | `Int | String` |
| Intersection/constraint | 정본 type/where 문맥 참조 |
| checked cast | `value as? Positive` |
| type test | `value is Int`, `value !is String` |
| generic constraint | `where T conforms Display` |
| associated qualification | `<T as Trait>::Item` |

Union의 injection identity, refinement predicate proof, Enum의
`(EnumId, VariantId)`는 서로 다른 증거다.

## 5. 데이터 선언

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public schema Point {
    x: Float64
    y: Float64
}

public enum ParseState {
    ready
    token(text: String)
    failed(code: Int, message: String)
}
```

현행 Enum case는 `case` keyword 없이 쓴다. 현행 payload는 positional,
named, mixed shape를 보존한다. expected context의 `::ready`, 명시적
owner의 `ParseState::ready`는 문맥과 owner가 다르므로 Enum 장에서
정확히 확인한다. Pattern도 `::ready` 또는 `ParseState::ready`를
사용하며 dot-prefixed case는 현행 표면이 아니다.

## 6. 흐름과 pattern

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def normalize(value: Int | String) -> Option<Int>
    throws Never
    effects {}
= {{
    number: Int if number > 0 => ::some(number)
    _: Int                     => ::none
    _: String                  => ::none
}}
```

pattern binding은 구조·type·guard가 성공한 edge에서만 commit된다.
closed input에는 exhaustive match를 선호한다. guard는 Bool이어야 하며
허용되지 않은 effect/error를 숨기지 않는다.

## 7. 컬렉션과 index

Deeplus의 일반 indexing은 **1부터 시작**한다. 첫 원소는 `items[1]`이며
`items[0]`을 첫 원소로 가르치지 않는다. slice의 경계와 view provenance는
단일 index 규칙보다 더 많은 정보를 가지므로 컬렉션 Part를 함께 본다.

postfix `A^`와 infix `A ^ 2`를 구분한다. 전자는 Stable transpose,
후자의 NumericArray elementwise power는 Preview gated profile이다.

## 8. Trait와 fixed glyph

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public conformance Vec2 conforms Add<Vec2> {
    type Output = Vec2

    +def add.(borrow rhs: Vec2) -> Vec2
        throws Never
        effects {}
    = {
        return Vec2!(x: self.x + rhs.x, y: self.y + rhs.y)
    }
}
```

연산자 표면은 admitted fixed glyph와 exact Trait requirement에 닫혀 있다.
임의 custom operator의 선언, precedence, associativity를 만들 수 없다.
lowercase `via`가 보이는 현행 contract와 inactive successor
`VIA`/`AUTO` route를 혼동하지 않는다.

## 9. 상태별 사용

- `CURRENT`/Stable design: positive 학습 예제에 사용할 수 있으나 product
  실행은 `NOT_RUN`.
- `PREVIEW_GATED`: exact 세 feature와 gate 조건을 함께 표기.
- `PREVIEW_DESIGN_NONACTIVATABLE`: 설계 검토 예제만 허용.
- `RECOVERY_ONLY`: 잘못된 과거 표면을 진단하고 고치는 데만 사용.
- `REMOVED`: negative 예제에만 사용.

## 10. 더 정확한 근거

- [문법 명세 및 언어 참조서](../../grammar-reference/README.md)
- `spec/grammar/deeplus.ebnf`
- `spec/language.md`
- `spec/frontend/frontend-model.json`
