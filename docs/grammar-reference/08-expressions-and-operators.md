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
                     | AtomicCallArgument ClosureExpr
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

unsuffixed integer literal은 기본적으로 signed 64-bit `Int`다. 기대
타입이 이미 정확한 `IntN` 또는 `UIntN`으로 고정되었을 때만 표현 가능한
양의 literal을 그 domain으로 문맥 적응한다. 직접 결합된
`PrefixExpr(-, UnsuffixedIntegerLiteral)`에는 음수 최솟값을 표현하기
위한 한정 적응이 있지만 `ISize`/`USize`, 임의 상수식, 일반 unary
계산에는 확대되지 않는다. 즉 `-128`은 `Int8` 문맥에서 한 값으로
검사할 수 있지만 `-(64 + 64)`를 같은 규칙으로 접어 주지 않는다.

integer `/`는 0 방향으로 절단한다. `%`의 결과 `r`은
`a == trunc(a / b) * b + r`을 만족하고 0이 아니면 dividend와 같은
부호이며 `|r| < |b|`다. 0 divisor와 signed `MIN / -1`,
`MIN % -1`은 place commit 전에 `ArithmeticDefect`로 끝난다. 명시적인
wrapping 또는 saturating 계산은 이름 있는 API를 써야 한다.

`Float32`와 `Float64`는 각각 IEEE-754 binary32/binary64 값 법칙을
따르고 ties-to-even으로 반올림한다. `+0.0 == -0.0`은 참이지만 NaN은
unordered이므로 암시적 `Ord`나 `Keyable` evidence를 공급하지 않는다.
따라서 NaN 가능 float를 Set/Map key로 사용하는 것은 별도 명시적 정책
없이 허용되지 않는다.

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

spaced ternary `condition ? whenTrue : whenFalse`는 Bool condition을 한 번
평가하고 선택된 arm 하나만 한 번 평가한다. 두 arm은 같은 normalized
type이어야 하거나 이미 독립적으로 고정된 expected type에 각각
부합해야 한다. join을 만들기 위해 anonymous Union을 합성하지 않는다.
두 edge의 place state, ownership, effects, errors, cancellation,
suspension과 cleanup도 모두 합법적으로 합쳐져야 한다. MIR에는 condition
branch, 두 lazy region과 하나의 responsibility join이 남는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
def choosePort(secure: Bool) -> Int
    throws Never
    effects {}
= {
    let port = secure ? 443 : 80
    return port
}
```

`443`과 `80`은 같은 `Int`다. 한 arm이 `String`이면 기대 타입 없이
`Int | String`을 자동 합성하지 않고 type join에서 거부한다. arm이 길거나
지역 `ret`이 필요하면 total `@if`가 더 명확한 현행 표면이다.

대입은 target place를 한 번, RHS를 한 번 평가한다. compound assignment는
place를 한 번 읽고 intrinsic operation 뒤 최대 한 번 commit한다.
overflow, divide-by-zero, `IndexError` 등 commit 전 실패는 원래 값을
보존한다.

prefix `move`는 owner를 이전하고 `borrow`/`&`는 허용된 borrow/view 책임만
만든다. `await`는 suspension과 structured-task 효과를 보존한다.

### `String::render`와 interpolation의 경계

`String::render<T>(arg, renderer)`는 구조화된 값 하나를 명시적으로
문자열로 바꾸는 Prelude helper다. 첫 인자 `arg`를 정확히 한 번 평가한
뒤, 그 값을 borrow하는 nonescaping trailing renderer closure를 정확히
한 번 호출한다. renderer는 반드시 `String`을 반환해야 하며, capture와
effect/error 책임은 일반 closure·호출 규칙을 그대로 따른다. 이 helper는
interpolation의 숨은 구현 hook도 아니고 locale·serialization·provider를
자동 선택하는 통로도 아니다. 기본 interpolation은 별도로 미리 선택된
`Display` evidence와 hole 평가 계획을 사용한다.

omitted-parameter closure의 expected parameter가 정확히 하나이면 가장
가까운 closure 안의 `@`가 그 parameter를 뜻한다. 현행 예제
`EX-R51a1-INTERPOLATION-P-002`는 List를 한 번 만들고 그 동일한 borrowed
List의 one-based index `1`, `2`를 읽는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let text = String::render(["first", "second"]) {
    "$@[1],$@[2]"
}
assert(text == "first,second")
```

explicit parameter를 쓰면 `@`는 더 이상 같은 closure의 parameter가
아니다. 다음처럼 `p`와 `@`를 섞으면 어느 값을 가리키는지 추측하지 않고
`IMPLICIT_AT_WITH_EXPLICIT_PARAMETER`로 거부한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let person = ${name: "John"}
let text = String::render(person) { p =>
    "${@.name}"
}
// IMPLICIT_AT_WITH_EXPLICIT_PARAMETER
```

renderer 결과가 `String`이 아닌 경우에도 암시적 `toString`, `Display`,
serialization 변환을 삽입하지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let person = ${name: "John", age: 25}
let text = String::render(person) { p =>
    p.age
}
// STRING_RENDERER_MUST_RETURN_STRING
```

현행 예제 `EX-R51a1-RENDER-P-002`처럼 중첩 renderer에서는 `@`가 항상
가장 가까운 omitted-parameter closure에 결합한다. 바깥 값을 계속 써야
한다면 바깥 closure에 explicit 이름을 붙인다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let text = String::render(${name: "outer", inner: ${name: "inner"}}) { root =>
    String::render(root.inner) {
        "${root.name}/${@.name}"
    }
}
assert(text == "outer/inner")
```

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

`count`와 `sum`은 기본 signed 64-bit `Int`, suffix가 붙은 `exact`와
`compact`는 각각 `Int32`, `Float32`, suffix 없는 소수 `ratio`는
`Float64`다. `count + 1`은 두 operand를 왼쪽부터 한 번씩 평가하고 같은
normalized `Int` domain에서 checked addition을 수행하므로 이 입력의
설계상 결과는 `43`이다. 일반 입력에서 overflow가 나면 결과 binding을
commit하기 전에 `ArithmeticDefect`로 끝난다. 이 값·진단은 정적 계약이며
실제 checker/xVM 실행 증거는 아직 `NOT_RUN`이다.

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

첫 `and`는 strict라서 두 Bool을 모두 왼쪽부터 평가한다. 둘째 조건의
comparison chain은 `1 <= i`와 `i <= xs.length`를 한 chain으로 검사하고,
그 전체가 참일 때만 `and then` 오른쪽의 `xs[i]`를 평가한다. 따라서 범위
증명이 실패하면 index access 자체가 일어나지 않는다. `otherwise`도
왼쪽이 충분하지 않을 때만 오른쪽 대안을 평가한다. 각 조건은 `Bool`이며,
bitwise `&&`/`||`로 바꾸면 Bool 연산이 아니라 잘못된 domain이므로
거부된다. 실제 short-circuit trace와 bounds-check 실행은 `NOT_RUN`이다.

현행 예제 `EX-R51VOI-002`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def nextDelta() -> Int = return 1
var total: Int = 10
total += nextDelta()
```

`total += nextDelta()`는 `total` place를 한 번 정하고 기존 값 `10`을 한 번
읽은 다음 `nextDelta()`를 한 번 호출한다. intrinsic checked addition의
설계상 새 값은 `11`이고 성공 뒤에만 place를 한 번 갱신한다. RHS 실패나
overflow가 있으면 `total`은 `10`으로 남으며 hidden load/add/store를
사용자 정의 operator로 재해석하지 않는다. 제품 lowering 실행은
`NOT_RUN`이다.

현행 예제 `EX-R48L-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let tower = 2 ^ 3 ^ 2
let explicit = 2 ^ (3 ^ 2)
```

spaced infix `^`는 오른쪽 결합이므로 두 식은 모두 `2 ^ (3 ^ 2)`로
해석되고 설계상 `Int` 값 `512`를 만든다. exponent가 정적으로 음이 아님을
증명해야 하며, 같은 domain의 checked power 과정에서 overflow가 나면
결과 binding 전에 실패한다. attached `values^` transpose나 gated
NumericArray infix power와는 token attachment와 operand domain이 다르다.
제품 evaluator 실행은 `NOT_RUN`이다.

현행 예제 `EX-R48-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let u = #[1, 2, 3]
let v = #[4, 5, 6]
let d = u *+ v
```

두 literal은 길이 3의 rank-1 NumericArray로 추론되고 `*+`는 같은 길이의
두 vector에만 허용되는 intrinsic dot product다. 원소를 source coordinate
순서로 읽어 checked multiply/add를 수행하므로 이 입력의 설계상 `d`는
scalar `32`다. rank가 1이 아니거나 길이가 다르면 operand를 평가하기 전에
정적 shape 진단으로 거부한다. 실제
NumericArray backend 실행은 `NOT_RUN`이다.

현행 예제 `EX-R51a1-FLAGS-P-002`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let access = Permission::read || Permission::execute
let toggled = access ^^ Permission::write
let inverse = ~~toggled
```

세 식의 타입은 모두 같은 nominal `Permission` flags domain이다. `||`는
`read`와 `execute` bit를 합치고, `^^`는 그 domain 안에서 `write` bit를
toggle하며, prefix `~~`는 선언된 width/mask 안의 complement를 만든다.
다른 bitfield type, raw integer 또는 Bool과 섞으면 자동 변환하지 않고
`FLAGS_OPERATION_REQUIRES_SAME_NOMINAL_TYPE` 계열 판정으로 거부한다. 정확한
runtime bit pattern과 backend 실행은 `NOT_RUN`이다.

현행 예제 `EX-R51b-GRAM-P-008`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let parsed = value as? Int
if item !is Secret and item !in denied { use(item) }
```

`as? Int`는 실패를 숨은 예외로 만들지 않고 `Option<Int>`를 반환하며
`value`를 한 번 평가한다. `!is`는 subject가 정확한 closed Union이고
`Secret`이 그 Union의 단일 alternative일 때만 `Bool`과 보완 narrowing
fact를 만든다. 뒤의 strict `and`는 오른쪽 membership 검사 전에 그 fact를
전달하지 않지만, 전체 조건의 true edge에는 두 operand가 참이라는 사실이
함께 남는다. `!in`은 `denied`의 admitted membership law를 사용한다. 이
snippet은 주변 선언을 전제로 한 정적 예이며 제품 checker 실행은
`NOT_RUN`이다.

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
