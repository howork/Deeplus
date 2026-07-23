# 표현식과 연산자

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 Deeplus expression grammar, Pratt registry,
value/operator coherence contract의 문서 투영이다. 현행 operator token,
precedence, glyph dispatch는 닫혀 있다.

예제는 corpus의 `expected_outcome: accept`,
`source_activation: none`인 항목이다. 제품 parser/checker/HIR/MIR/xVM/
LLVM/formatter/LSP 실행은 `NOT_RUN`이다.

## 문법

### Pratt 진입점과 parselet

```ebnf
Expr           ::= PrattExpr
PredicateExpr  ::= PrattPredicateExpr
SliceIndexExpr ::= PrattSliceIndexExpr

ExpressionPrefixParselet ::= "+" | "-" | "not" | "~~"
                           | "move" | "borrow" | "&" | "await"

ExpressionPostfixParselet ::= CallSuffix | TupleOrdinalSuffix | IndexSuffix
                            | MemberSuffix | MessageSuffix
                            | NumericArrayTransposeSuffix
                            | ConstructorCallSuffix
                            | NamedConstructorCallSuffix
                            | PrototypeDerivationSuffix | CastSuffix
```

EBNF는 parselet family를 열거하고 정확한 binding power와 associativity는
Pratt registry 및 operator contract가 소유한다.

### 우선순위

아래 표는 낮은 binding power에서 높은 순서다.

| 순위 | 계층 | token/형식 | 결합 |
|---:|---|---|---|
| 10 | 대입 | `=`, `+=`, `-=`, `*=`, `/=`, `%=` | 오른쪽 |
| 20 | 조건 | `? :` | 오른쪽, 구조적 |
| 30 | 순차 대안 | `otherwise` | 왼쪽 |
| 40 | strict Bool OR | `or` | 왼쪽 |
| 50 | sequential Bool AND | `and then` | 왼쪽 |
| 60 | strict Bool AND | `and` | 왼쪽 |
| 70 | 비교 | `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `!in`; `is`, `!is` | 앞 집합은 checker-bounded chain, `is`/`!is`는 non-chainable |
| 80 | Option coalescing | `?:` | 오른쪽 |
| 90 | bitwise OR | `||` | 왼쪽 |
| 100 | bitwise XOR | `^^` | 왼쪽 |
| 110 | bitwise AND | `&&` | 왼쪽 |
| 120 | range | `..`, `..<` | 비결합 |
| 130 | 덧셈 | `+`, `-` | 왼쪽 |
| 140 | 곱셈 | `*`, `/`, `%` | 왼쪽 |
| 150 | linear product | `**`, `*+` | 왼쪽 |
| 160 | 거듭제곱 | `^` | 오른쪽 |
| 170 | prefix | `+`, `-`, `not`, `~~`, `move`, `borrow`, `&`, `await` | 오른쪽 |
| 180 | cast | `as?`, `as!` | 비결합 |
| 190 | postfix | call, ordinal, index, member, message, transpose, constructor, derivation, trailing closure | 왼쪽, 구조적 |

괄호는 precedence를 명시적으로 바꾼다. index suffix 안 range delimiter는
slice parser가 소유하며 바깥 expression range로 소비하지 않는다.

### 구조적 후위 연산

```ebnf
CallSuffix         ::= ArgumentList ClosureExpr?
IndexSuffix        ::= "[" SliceAxisList "]"
MemberSuffix       ::= "." Identifier | "." "\\" NAME_TOKEN
MessageSuffix      ::= "~" MessageSelector MessageArguments? ClosureExpr?
CastSuffix         ::= "as" "?" TypeRef | "as" "!" TypeRef
TupleOrdinalSuffix ::= "." StaticIntLiteral
```

lexer가 `as`와 `?`/`!`를 별도 token으로 내더라도 parser는 붙어 있는
`as?`/`as!` cast operation으로 처리한다.

## 허용과 정적 의미

### 닫힌 operator authority

- 현행 token vocabulary와 precedence는 닫혀 있다.
- 모든 glyph dispatch는 `INTRINSIC_ONLY`다.
- Trait, conformance, extension, witness, provider, runtime lookup은 glyph를
  만들거나 재정의하지 못한다.
- 사용자 확장은 named Trait method 또는 named API를 쓴다.
- source order는 overload tie-breaker가 아니다.

### 숫자, 비트 연산, Bool

`+`, `-`, `*`, `/`, `%`는 하나의 정확한 normalized scalar domain을
요구한다. integer 연산은 checked이며 암시적 wrap, saturate, width 변경,
signedness 변경이 없다. float는 정확한 `Float32` 또는 `Float64` domain을
사용한다.

integer `^`는 exponent가 정적으로 nonnegative임을 증명할 때 현행이다.
Measure power는 별도 static-dimension owner를 가진다. `^`는 오른쪽
결합이다. NumericArray infix power는 Preview gate 전용이고 postfix
NumericArray transpose `^`와도 별도 owner다.

`||`, `^^`, `&&`, prefix `~~`는 하나의 exact known-width integer 또는
허용된 bitfield/flags domain의 bitwise operation이다. Bool operator가
아니다.

- `and`, `or`: 양 operand를 왼쪽부터 모두 평가하는 strict Bool
- `and then`: 필요할 때만 오른쪽을 평가하는 sequential Bool
- `otherwise`: 필요할 때만 오른쪽 대안을 평가
- `not`: 유일한 Bool negation
- `?:`: 한 layer의 lazy Option coalescing

### 대입과 cast

대입 대상은 허용된 mutable place여야 하며 결과 type은 `Unit`이다.
`as? T`는 `Option<T>`를 반환한다. `as! T`는 정해진 checked-or-defect
cast law를 따른다. 어느 형식도 operator overloading 요청이 아니다.

### closed Union 타입 판정

`subject is Alternative`와 `subject !is Alternative`는 subject의 정적
타입이 하나의 normalized closed Union이고 target이 그 Union의 정확한
단일 alternative identity일 때만 현행이다. subject를 한 번 평가하고
저장된 injection identity를 한 번 읽어 `Bool`을 만든다. 두 결과 edge는
서로 보완적인 flow fact를 남기지만 값을 바인딩하지 않는다.

검사 직전의 가능한 대안 집합이 `C`이고 target이 `T`이면 `is`의 true
edge는 `C ∩ {T}`, false edge는 `C \ {T}`다. `!is`는 두 edge를
맞바꾼다. `and then` 오른쪽은 왼쪽의 true fact를, `otherwise` 오른쪽은
false fact를 받는다. strict `and`와 `or`는 오른쪽을 평가하기 전에
narrowing하지 않는다.

fact는 stable place에만 붙는다. assignment, alias mutation, exclusive
borrow, escape, capture, consume, may-mutate call 또는 may-consume call은
관련 fact를 제거한다. `is`/`!is`는 직접 comparison chain에 들어갈 수
없다. 적용 가능한 진단의 우선순위는
`COMPARISON_CHAIN_OPERATOR_NOT_IN_PHASE_A`,
`TYPE_TEST_SUBJECT_MUST_BE_CLOSED_UNION`,
`UNION_TYPE_TEST_ALTERNATIVE_NOT_EXACT` 순이다.

이 연산은 open runtime type test가 아니다. subclass, refinement,
reflection, Trait 또는 provider를 탐색하지 않는다. 값을 바인딩할 때에는
typed pattern, 변환할 때에는 `as?` 또는 `as!`를 사용한다. 부정형의 `!`와
`is` 사이에는 trivia를 둘 수 없다.

## 평가·소유권·효과

별도 법칙이 short-circuit 또는 오른쪽 결합을 정하지 않는 한 expression은
왼쪽부터 결정적으로 평가한다. 최적화는 failure, cleanup, suspension,
message, provider의 관측 순서를 바꿀 수 없다.

대입은 target place를 한 번, RHS를 한 번 평가한다. compound assignment는
place를 한 번 읽고 intrinsic operation 뒤 최대 한 번 commit한다.
overflow, divide-by-zero, `IndexError` 등 commit 전 실패는 원래 값을
보존한다.

prefix `move`는 owner를 이전하고 `borrow`/`&`는 허용된 borrow/view 책임만
만든다. `await`는 suspension과 structured-task 효과를 보존한다.

## 현행 예제

### closed Union `is`/`!is` 검증 예제

`EX-R51f3-UNION-ISTEST-P-001`은 `and then` 오른쪽에 true-edge
narrowing을 전달한다.

```deeplus
public type TextOrNumber = Int | String

public def isPositiveNumber(value: TextOrNumber) -> Bool = {
    return value is Int and then value > 0
}
```

`EX-R51f3-UNION-ISTEST-P-002`는 `!is`가 정확한 보완 대안 집합을
검사함을 보인다.

```deeplus
public type TextOrNumber = Int | String

public def isText(value: TextOrNumber) -> Bool = {
    return value !is Int
}
```

`EX-R51f3-UNION-ISTEST-NG-001`은 closed Union이 아닌 subject를
거부한다.

```deeplus
public def invalidTypeTest(value: Int) -> Bool = {
    return value is Int
}
// TYPE_TEST_SUBJECT_MUST_BE_CLOSED_UNION
```

`EX-R51f3-UNION-ISTEST-NG-002`는 Union 전체처럼 정확한 단일 대안이
아닌 target을 거부한다.

```deeplus
public type TextOrNumber = Int | String

public def invalidAlternative(value: TextOrNumber) -> Bool = {
    return value is TextOrNumber
}
// UNION_TYPE_TEST_ALTERNATIVE_NOT_EXACT
```

`EX-R51f3-UNION-ISTEST-NG-003`은 `is`가 직접 comparison chain에
참여할 수 없음을 보인다.

```deeplus
public type TextOrNumber = Int | String

public def invalidComparisonChain(value: TextOrNumber) -> Bool = {
    return value is Int == true
}
// COMPARISON_CHAIN_OPERATOR_NOT_IN_PHASE_A
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

현행 예제 `EX-R48C-072`,
원본 `examples/guide/review-corpus.md`:

```deeplus
if isReady and isValid {
    commit()
}

if 1 <= i <= xs.length and then xs[i] == 0 {
    handleZero(i)
}

if cacheHit otherwise loadAllowed {
    serve()
}
```

현행 예제 `EX-R51VOI-002`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def nextDelta() -> Int = return 1
var total: Int = 10
total += nextDelta()
```

현행 예제 `EX-R48L-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let tower = 2 ^ 3 ^ 2
let explicit = 2 ^ (3 ^ 2)
```

현행 예제 `EX-R48-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let u = #[1, 2, 3]
let v = #[4, 5, 6]
let d = u *+ v
```

현행 예제 `EX-R51a1-FLAGS-P-002`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let access = Permission::read || Permission::execute
let toggled = access ^^ Permission::write
let inverse = ~~toggled
```

현행 예제 `EX-R51b-GRAM-P-008`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let parsed = value as? Int
if item !is Secret and item !in denied { use(item) }
```

## 거부되거나 격리된 형식

| 형식 또는 주장 | 판정 |
|---|---|
| `true && false`를 Bool conjunction으로 사용 | 거부; `and`/`and then` 사용 |
| standalone `!value` Bool negation | 거부; `not value` 사용 |
| `operator <+> precedence 130` | recovery-only, `CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT` |
| Trait conformance로 `+` 정의 | nonactivatable, `FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT` |
| mixed-width/signedness bitwise | 명시적 checked conversion 없이는 거부 |
| float `%`, float `^` | 현행 glyph route 없음; named API 사용 |
| `i..>j`, `i...j` range | 거부 |
| ungated NumericArray infix `^` | 현행 아님 |

corpus의 `EX-R48L-010`은 명시적 Preview gate가 있는 경우에만
`accept_with_gate`다.

<!-- deeplus-status-fence: PREVIEW_GATED -->

```deeplus
#preview(numeric_array_elementwise_power_msp)
let a = #2,2[
    1, 2;
    3, 4;
]
let squared = a ^ 2
```

이 gate는 custom operator나 Trait 기반 fixed-glyph dispatch를 허용하지
않는다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- numeric literal adaptation은 homogeneous operator admission 전에
  일어나며 일반 implicit numeric conversion이 아니다.
- `^`는 Pratt 위치에 따라 infix power, postfix transpose, unit static
  power로 구분된다.
- `**`는 infix linear product와 argument/materialization의 named unfold를
  문맥별로 가진다. named-rest parameter는 `***`다.
- message `~`, call, member, index, constructor, derivation, trailing closure는
  user-overloadable punctuation이 아니라 구조적 postfix다.
- index/slice 의미는
  [컬렉션, 인덱싱, 슬라이싱](09-collections-indexing-and-slicing.md)을
  참고한다.
- predicate 문맥의 bounded Pratt entry는 effectful general expression을
  자동으로 모두 허용하지 않는다.

## 정본 근거

- [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- [`spec/contracts/value-operator-indexing-coherence.json`](../../spec/contracts/value-operator-indexing-coherence.json)
- [`spec/contracts/provider-derive-via.json`](../../spec/contracts/provider-derive-via.json)
- [`spec/language.md`](../../spec/language.md)
- [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
