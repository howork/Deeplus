# 02-04. 연산자, power와 Bool

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

현행 operator token과 precedence는 닫혀 있다. Stable fixed-glyph
conformance는 기존 glyph의 정확한 13개 역할, 즉 unary `+`/`-`, binary
`+`/`-`/`*`/`/`/`%`, `==`/`!=`, `<`/`<=`/`>`/`>=`에만 존재한다.
임의 custom operator는 Current와 Preview Design 모두에서 수용하지 않는다.

## 2. 학습 목표

- 산술과 power의 precedence/associativity를 읽는다.
- strict Bool과 sequential Bool을 구분한다.
- Bool word operator와 pointwise double-glyph family를 구분한다.
- operator conformance가 새 glyph나 hidden conversion을 만들지 못함을
  이해한다.

## 3. 선수 지식

exact numeric domain, Rational/Complex 기본 연산을 알아야 한다.

## 4. 문제에서 출발하기

`-2 ^ 2`를 `(-2) ^ 2`로 읽을지 `-(2 ^ 2)`로 읽을지가 정해져 있지 않으면
사람과 parser가 다른 계산을 할 수 있다. 또한 `&&`를 Bool AND로 착각하면
pointwise integer operator와 flow narrowing을 혼동한다. Deeplus는
token owner와 결합 법칙을 닫아 둔다.

## 5. 핵심 모델

중요한 binding 순서는 낮은 쪽부터 대입, 조건, Bool, 비교, coalescing,
pointwise, range, 덧셈, 곱셈, linear product, power, prefix, cast,
postfix다. power `^`는 오른쪽 결합이고 numeric sign보다 강하게 묶인다.

Bool family는 다음과 같다.

- `and`, `or`: 두 operand를 모두 평가하는 strict Bool.
- `and then`: 왼쪽이 참일 때만 오른쪽을 평가.
- `otherwise`: 왼쪽 대안이 충분하지 않을 때만 오른쪽을 평가.
- `not`: Bool negation.
- `&&`, `||`, `^^`, `~~`: integer/flags/허용 NumericArray의 pointwise
  family이며 Bool short-circuit가 아니다.

## 6. 단계별 예제

power의 parse를 비교한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let negatedSquare = -2.0 ^ 2.0
let squareOfNegative = (-2.0) ^ 2.0
let reciprocalCube = 2.0 ^ -3
let tower = 2 ^ 3 ^ 2
```

정본상 parse는 각각 `-(2.0 ^ 2.0)`, `(-2.0) ^ 2.0`,
`2.0 ^ (-3)`, `2 ^ (3 ^ 2)`다. 결과 annotation은 operation을
선택하지 않는다.

Bool 평가 정책을 의도에 맞춰 고른다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let bothFacts: Bool = ready and valid
let safeAccess: Bool =
    1 <= index <= values.length and then values[index] == target
let allowed: Bool = cached otherwise mayLoad
```

`and then` 오른쪽은 comparison chain이 참일 때만 평가된다. strict
`and`는 오른쪽을 항상 평가하며 사전 narrowing fact를 전달하지 않는다.

### 판정 trace, 미니 사례와 흔한 오해

operator expression은 token만 보고 끝내지 않는다. 먼저 precedence와
associativity로 tree를 만들고, operand의 exact domain과 admitted owner를
찾는다. 그다음 result type과 failure channel을 확정하고, strict 또는
sequential evaluation law를 기록한다. `-2^2`는 unary sign이 base literal에
붙은 하나의 token이 아니라 power tree 바깥의 negation이므로
`-(2^2)`로 읽는다. `2^-3`은 exponent 쪽 unary sign이 허용되는 별도
형태다.

미니 사례에서 `ready and expensive()`는 양쪽을 모두 평가하지만
`ready and then expensive()`는 왼쪽이 true일 때만 오른쪽을 평가한다.
흔한 오해는 `&&`와 `and`가 같은 Bool 연산자라는 생각이다. pointwise
logical glyph는 known-width integer/shape domain을 가지며 Bool
short-circuit를 대신하지 않는다. Stable conformance는 닫힌 13개 역할에만
가능하며 새 precedence나 custom glyph를 만들 수 없다. `!=`는 하나의
`Eq` 결과에서, 네 ordering glyph는 하나의 `Ord.compare` 결과에서
파생하므로 glyph마다 별도 witness를 만들지 않는다.

operator를 선택할 때는 “수학에서 익숙한가”보다 domain contract가
닫혀 있는가를 묻는다. 반복 조건처럼 오른쪽을 건너뛰어야 안전하면
`and then`/`otherwise`, 두 Bool 계산을 모두 관찰해야 하면 strict
`and`/`or`를 쓴다. vector나 bit domain의 pointwise 계산은 별도 glyph와
shape proof를 사용한다. 같은 기호를 편의상 다른 의미로 추가하면
precedence뿐 아니라 Trait witness와 진단의 결정성도 깨진다.

괄호는 precedence를 바꾸는 도구인 동시에 독자의 판정 tree를 보여 주는
문서 장치다. 경계가 낯설면 임의 operator를 만들기보다 괄호와 named
function으로 의도를 먼저 드러낸다.

## 7. 허용·거부·경계 사례

Bool에 pointwise glyph를 사용하면 거부한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: BITWISE_OPERATOR_DOES_NOT_ACCEPT_BOOL -->
```deeplus
let invalid = true && false
```

`&&`는 scalar Bool carrier가 아니다. `/`, `%`, equality와 ordering은
각각 `Divide`, `Remainder`, `Eq`, `Ord`의 닫힌 역할로만 conformance를
가질 수 있다. assignment와 logical glyph에는 독립 conformance를 붙일
수 없고, 모든 admitted non-intrinsic 역할은 left nominal owner package의
유일한 `DIRECT_GLOBAL` row만 선택한다. `^`는 Trait이 아닌 language
intrinsic이다.

## 8. 다른 기능과의 연결

`and then`은 closed Union `is`가 만든 true-edge fact를 오른쪽에
전달한다. `otherwise`는 false-edge fact를 전달한다. checked integer
overflow와 zero division은 commit 전 `ArithmeticDefect`이며 recoverable
ErrorSet이 아니다. HIR-H1은 선택된 operator identity와 source evaluation
order를 MIR에 넘기고 runtime에서 다시 lookup하지 않는다.

## 9. Deeplus다운 작성 관례

- short-circuit가 의도라면 `and then`/`otherwise`를 명시한다.
- precedence가 독자의 의도를 흐릴 때 괄호를 쓴다.
- extension 의도는 임의 glyph가 아니라 named Trait method/API로 표현한다.
- mixed domain은 명시적 checked conversion 뒤 연산한다.
- 결과 타입으로 operator route를 강제하지 않는다.

## 10. 연습 문제

1. **따라 하기:** `-3 ^ 2`, `(-3) ^ 2`, `2 ^ 3 ^ 2`의 parse tree를
   괄호로 다시 쓴다.
2. **빈칸 완성:** Bool 오른쪽을 조건부로 평가하려면 `and ___`을 쓴다.
3. **스스로 설계하기:** bounds 확인 뒤 one-based index를 읽는 조건과,
   두 정수 mask를 pointwise 결합하는 식을 각각 작성하고 operator
   family가 다른 이유를 설명한다.

## 11. 빠른 복습

- power는 오른쪽 결합이며 numeric sign보다 강하게 묶인다.
- `and`/`or`는 strict, `and then`/`otherwise`는 sequential이다.
- double-glyph pointwise family는 Bool short-circuit가 아니다.
- fixed-glyph conformance는 정확한 13개 역할과 9개 Prelude Trait root만
  허용한다.
- arbitrary custom operator는 current/Preview Design 모두 아니다.

## 12. 정본 근거와 다음 장

- [operator precedence와 의미](../../grammar-reference/08-expressions-and-operators.md)
- [value/operator coherence](../../../spec/contracts/value-operator-indexing-coherence.json)
- [Pratt frontend model](../../../spec/frontend/frontend-model.json)
- [type judgments](../../../spec/types/type-system.md)

다음은 [표현식과 평가 순서](02-05-expressions-evaluation-order.md)를
배운다.
