# 6.5 Stable fixed-glyph conformance

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

fixed-glyph conformance는 Stable 설계이며 admitted glyph는 정확히
`+`, `-`, `*`다. 임의 custom operator는 Current와 Preview Design
모두에서 수용하지 않는다. `/`, `%`, `^`, 비교·논리·대입·range
glyph도 이 통로에 없다.

## 2. 학습 목표

- intrinsic pair와 user nominal pair의 선택 순서를 이해한다.
- `Add`, `Subtract`, `Multiply` conformance를 읽는다.
- left-owner와 `DIRECT_GLOBAL` coherence 조건을 설명한다.
- custom operator와 admitted set 밖 glyph를 사용하지 않는다.

## 3. 선수 지식

explicit conformance와 associated `Output`, operand ownership,
operator 평가 순서를 알고 있어야 한다.

## 4. 문제에서 출발하기

벡터 덧셈을 `left.add(right)`로만 쓰면 수학식이 장황하다. 반대로 사용자가
새 glyph와 precedence를 만들게 하면 parser, formatter, overload와 학습
모델이 열린다. Deeplus는 기존 세 glyph만 exact Prelude Trait에 연결한다.

## 5. 핵심 모델

| glyph | Prelude Trait | method |
|---|---|---|
| `+` | `Add<Rhs>` | `add` |
| `-` | `Subtract<Rhs>` | `subtract` |
| `*` | `Multiply<Rhs>` | `multiply` |

checker는 먼저 normalized operand pair가 intrinsic 예약 domain인지
검사한다. 예약 pair이면 intrinsic만 사용하고 conformance lookup은
0회다. 그 밖에서는 left nominal owner를 정의한 package의 유일한
`DIRECT_GLOBAL` conformance 하나를 선택한다.

선택 key는 `(OperatorId, LeftType, RightType)`다. expected result,
implicit conversion, import order, extension, provider, specialization은
후보나 tie-breaker가 아니다.

## 6. 단계별 예제

### 깊이 읽기: glyph가 아니라 닫힌 conformance profile

fixed-glyph conformance는 사용자가 새 연산자 언어를 만드는 기능이
아니다. Stable admitted set은 정확히 `+`, `-`, `*`이며 각 glyph는
정해진 Trait requirement와 operand/result domain에 결합된다. precedence,
associativity, evaluation order는 grammar가 소유하고 conformance가
다시 정의하지 않는다.

parser가 current glyph를 식별한 뒤 operand type과 exact requirement를
정규화한다. left owner package의 `DIRECT_GLOBAL` conformance가 유일한지
확인하고 두 operand borrow, 동기성, `throws Never`, `effects {}`,
non-consuming·non-mutating 책임을 검사한다. 실패하면 ordinary method나
다른 glyph로 fallback하지 않는다.

`left + right` trace에서는 left와 right를 차례로 한 번 평가한 뒤 선택된
`Add` witness의 `add.`를 호출한다. rhs 평가가 실패하면 witness call은
시작되지 않는다. runtime provider 검색과 source-order winner count는
영이어야 한다.

`/`도 익숙한 산술 glyph이니 같은 방식으로 추가할 수 있다는 생각은
흔한 오해다. admitted set 밖 glyph은 conformance dispatch 대상이 아니다.
필요한 operation은 named API나 별도
수용된 intrinsic corridor를 사용한다.

fixed glyph 식도 임의 method lookup으로 읽지 않는다. checker는 glyph가
허용된 닫힌 family인지 확인하고, 정규화된 left type, right type, operation
Trait의 exact row를 찾는다. unique conformance가 requirement를 만족하면
Output identity를 고정하고 두 operand를 source order로 한 번씩 평가한다.
admission이 실패하면 계산이나 부분 mutation은 시작하지 않는다.

`Vec2 + Vec2`와 `Vec2 * Int`는 glyph가 익숙하더라도 서로 다른 ground
pair와 Output 계약이다. commutativity나 역방향 row를 자동 생성하지
않으며, custom glyph declaration과 admitted set 밖의 overload도
거부한다. overflow, division failure, matrix shape처럼 별도 실패 모델이
필요한 연산을 간단한 conformance로 감추지 않는다. 코드 리뷰에는 선택된
row, operand 평가 순서, result owner와 failure effect를 함께 적는다.

### 6.1 Vec2 덧셈

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public data class Vec2(+let x: Int, +let y: Int)

public conformance Vec2 conforms Add<Vec2> {
    type Output = Vec2

    +def add.(borrow rhs: Vec2) -> Vec2
        throws Never
        effects {}
    = {
        return Vec2${
            x: self.x + rhs.x
            y: self.y + rhs.y
        }
    }
}

let combined = left + right
```

안쪽 `Int + Int`는 intrinsic pair다. 바깥 `Vec2 + Vec2`만 selected
conformance를 사용한다. 두 operand는 왼쪽부터 한 번 평가되고 witness는
borrow, synchronous, nonmutating, `throws Never effects {}`다.

### 6.2 서로 다른 RHS와 Output

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public conformance Vec2 conforms Multiply<Int> {
    type Output = Vec2

    +def multiply.(borrow rhs: Int) -> Vec2
        throws Never
        effects {}
    = {
        return Vec2${
            x: self.x * rhs
            y: self.y * rhs
        }
    }
}

let doubled = point * 2
```

`Output`은 selected conformance가 고정한다. expected annotation으로 다른
conformance를 선택하지 않는다.

### 6.3 exact numeric 표준 row

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let a: Rational = <2/3>
let b: Rational = <5/7>
let exact: Rational = a + b

let z: Complex = 3.0 + 4.0i
let shifted: Complex = z - 1.0
```

Rational/Complex 표준 row도 sealed `DIRECT_GLOBAL` identity이며 admitted
set을 넓히지 않는다. `Rational / Rational`은 checked named
`dividedBy`, `^`는 language intrinsic이다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: OPERATOR_NOT_CONFORMANCE_OVERLOADABLE; product: NOT_RUN -->
```deeplus
public conformance Ratio conforms Divide<Ratio> {
    type Output = Ratio
}
// /는 fixed-glyph conformance admitted set이 아님
```

left owner 밖의 declaration은
`OPERATOR_CONFORMANCE_LEFT_OWNER_REQUIRED`, 후보가 둘이면 terminal
ambiguity다. 실패 뒤 intrinsic/named API로 fallback하지 않는다.

## 8. 다른 기능과의 연결

- extension은 operator 후보를 만들지 않는다.
- current lowercase `via`나 successor route는 operator ranking에 참여하지
  않는다.
- `^` power, `**` matrix product, `*+` dot product는 language-owned
  intrinsic이며 fixed-glyph Trait 통로와 다르다.
- selected IDs와 responsibility는 HIR/MIR/API metadata에 고정된다.

## 9. Deeplus다운 작성 관례

- 수학적으로 보편적이고 오류·효과 없는 세 연산에만 glyph를 사용한다.
- 실패하거나 policy가 필요한 연산은 이름 있는 API로 만든다.
- 새 의미에 glyph를 억지로 재사용하지 않는다.
- expected result나 import 순서에 의존하는 overload를 설계하지 않는다.

## 10. 연습 문제

1. **복사:** `Vec2 conforms Subtract<Vec2>`를 작성하라.
2. **빈칸 완성:** `left: ___`, `right: ___`, `Output: ___`의 빈칸을
   `Vec2`, `Int`, `Vec2`로 채우고 operand가 한 번씩 평가됨을 적어라.
3. **설계:** 실패 가능한 행렬 역연산을 operator와 named API 중 어디에
   둘지 admitted glyph, error channel, policy를 기준으로 결정하라.

## 11. 빠른 복습

- Stable glyph는 정확히 `+`, `-`, `*`다.
- primitive 예약 pair는 intrinsic 전용이다.
- user row는 left owner의 유일한 `DIRECT_GLOBAL` conformance다.
- witness는 borrow, pure/synchronous/no-failure profile이다.
- 임의 custom operator는 positive 표면이 없다.

## 12. 정본 근거와 다음 장

- [표현식·연산자 레퍼런스](../../grammar-reference/08-expressions-and-operators.md)
- [Trait 경계](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [값·연산자 coherence](../../../spec/contracts/value-operator-indexing-coherence.json)
- [정확 수 coherence](../../../spec/contracts/rational-complex-numeric-coherence.json)

이제 실습에서 Trait, conformance, associated item과 generic rendering을
한 번에 결합한다.
