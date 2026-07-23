# 함수, 메서드, 클로저, 호출

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 callable 선언, parameter channel, 함수 profile, 메서드
marker, local function, closure, lambda, 호출을 설명하는 문서 투영이다.
예제는 현행 corpus의 `accept` 및 `source_activation: none` 항목이다.
제품 parser/checker/lowering/runtime/tooling은 `NOT_RUN`이다.

## 문법

### 이름 있는 함수

```ebnf
DefIntroducer      ::= "def" HashTag*
ModuleFunctionDecl ::= TopLevelVisibility? DefIntroducer Identifier FunctionRest
LocalFunctionDecl  ::= CaptureList? DefIntroducer Identifier FunctionRest

FunctionRest       ::= TypeParameterList? ParameterList FunctionTail
FunctionTail       ::= ReturnClause? ThrowsClause? EffectsClause?
                       ContractClause* WhereClause? FunctionBody
FunctionBody       ::= "=" FunctionBodyContent
FunctionBodyContent ::= Block | ReturnShorthand | ClauseFunctionBody
ReturnShorthand    ::= "return" Expr
```

이름 있는 함수의 값 본문은 block, `= return Expr`, 또는 `{{ ... }}`의
선언적 clause body다. bare `= Expr`는 이름 있는 함수 본문이 아니다.

선언 owner별 현행 profile은 닫혀 있다.

| owner | 허용 profile |
|---|---|
| 모듈 함수 | `def`, `def#async`, `def#pure`, `def#guard` |
| 진입 함수 | `def#entry`, `def#entry#async` |
| 확장 함수 | `def`, `def#async` |
| 인스턴스 메서드 | `def`, `def#mut`, `def#consume`, `def#async`, `def#pure` |
| 로컬 함수 | `def`, `def#pure`, `def#async`, `def#guard` |
| Trait 메서드 | `def`, `def#pure`, `def#async` |
| conformance 메서드 | `def`, `def#async`, `def#mut`, `def#consume`, `def#pure` |
| 정리 함수 | `def#cleanup` |

중복 profile과 owner에 없는 조합은 거부한다.

### 매개변수 채널

```ebnf
Parameter ::= ContextParameter
            | WitnessParameter
            | RepeatedParameter
            | NamedRestParameter
            | ValueParameter

ValueParameter    ::= ParameterMode? Identifier TypeAnnotation
ParameterMode     ::= "borrow" | "mut" | "move" | "inout"
ContextParameter  ::= "context" Identifier ":" TypeRef
WitnessParameter  ::= "using" Identifier ":" "witness" TypeRef
RepeatedParameter ::= Identifier "..." TypeAnnotation
NamedRestParameter ::= Identifier "***" TypeAnnotation
```

일반 parameter와 lambda parameter는 identifier를 bind하며 refutable
Pattern을 받지 않는다. 반복 positional channel은 `values...: T`, named
rest channel은 유일하고 마지막인 `options***: Record`다.

함수 type은 두 residue를 그대로 보존한다.

다음은 현행 문법을 설명하기 위한 예시다. 근거는
[`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)의
`ParenTypeSyntax`/`FunctionTypeTail`과
[`spec/types/type-system.md`](../../spec/types/type-system.md)의
named-rest residue 규칙이다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private type Handler = (String, Int..., Record***) -> Unit
```

`***`는 parameter/type suffix이고 `**record`는 call/materialization의
named unfold prefix다. 둘은 같은 의미가 아니다.

### 메서드와 type-side 함수

```ebnf
MemberFunctionDecl ::= MemberVisibility? DefIntroducer Identifier
                       ClassDispatchMarker FunctionRest
ClassDispatchMarker ::= "." | "+" | "*." | "*+"
TypeSideMemberFunctionDecl ::= MemberVisibility? "def" "::" Identifier FunctionRest
```

class/enum instance method marker는 `.` final, `+` open, `*.` override 후
close, `*+` override 후 open이다. Trait/conformance가 같은 glyph를
사용하더라도 AST 의미 영역은 `TraitWitnessKind`로 별개다. field에는
dispatch marker가 없고 associated nonmethod에도 witness marker가 없다.

### 클로저와 lambda

```ebnf
ClosureExpr       ::= CaptureList? HashTag* "{" ClosureContent "}"
ExplicitLambdaContent ::= LambdaParameterList? "=>" LambdaBody
LambdaParameterList ::= LambdaParameter ("," LambdaParameter)*
LambdaParameter   ::= ParameterMode? Identifier TypeAnnotation?

CaptureItem       ::= ("let" | "var") Identifier "=" Expr
                    | CaptureMode Identifier
                    | Identifier
CaptureMode       ::= "borrow" | "inout" | "move" | "clone"
                    | "deep" | "copy" | "once"
```

lambda parameter 목록에는 괄호를 쓰지 않는다. 명시적 nullary lambda는
`{ => body }`다. `{ x: T => body }`의 단일 expression은 로컬 결과가
되며 multiline non-Unit 경로에는 각 정상 경로의 `ret`가 필요하다.

### 호출

일반 호출은 `callee(arguments)`다. 예외는 정확히 하나의 atomic argument
뒤에 정확히 하나의 unlabeled trailing closure가 오는 bounded suffix다.
여러 callback은 named argument로 전달한다.

```ebnf
Argument ::= ContextArgument | WitnessArgument | NamedArgument
           | PositionalUnfoldArgument | NamedUnfoldArgument | Expr
NamedArgument            ::= Identifier ":" Expr
PositionalUnfoldArgument ::= "*" Expr
NamedUnfoldArgument      ::= "**" Expr
```

## 허용과 정적 의미

- overload identity에는 parameter 순서와 label, ownership mode,
  context/witness/rest channel, effect/error row, isolation, return type가
  들어간다.
- return type이나 source order만으로 overload를 선택하지 않는다.
- 고정 arity, repeated positional, named rest 순으로 우선하며 남은 tie는
  오류다.
- named rest의 carrier는 정적 label을 가진 canonical `Record`다. runtime
  key를 가진 Map은 named argument를 만들 수 없다.
- local function은 선언 뒤부터 보이고 사용한 outer local을 앞의
  CaptureList에 모두 명시한다. 현행 mutual recursion은 없다.
- closure profile은 lifetime(`ordinary/#scoped`), call-right
  (`repeatable/#once`), 환경 receiver(`shared/#mut`), 동작
  (`ordinary/#pure/#guard`)와 effects/errors/isolation/suspension을
  보존한다.
- implicit `@` parameter는 overload가 정확히 1-parameter callable을
  독립적으로 선택한 경우에만 허용된다.
- `#guard`는 terminating, nonsuspending, nonconsuming pure Bool
  callable이지만 호출했다는 사실만으로 flow narrowing proof가 생기지는
  않는다.

## 평가·소유권·효과

호출 인자는 source order로 정확히 한 번 평가된다. positional unfold와
named unfold는 별도 channel이며 Record unfold는 정적 label source order를
보존한다.

closure capture mode는 실제 owner/borrow 책임이다. borrow capture는 region
밖으로 escape할 수 없고 inout capture는 겹칠 수 없다. move capture는
원본 owner를 이전한다. resource capture에는 모든 종료 경로를 합쳐 정확히
하나의 cleanup path가 필요하다.

`return`은 이름 있는 함수·메서드·handler·local function의 control
transfer다. `ret`는 lambda와 `@if/@match/@try/@scope`의 로컬 value body에만
속하며 closure boundary를 넘지 않는다.

## 현행 예제

### named rest와 펼침

현행 예제 `EX-R51a1-NEW-003`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def command(name: String, args...: String, options***: Record) -> Unit = {
    dispatch(name, *args, **options)
}
```

현행 예제 `EX-R51a1-NEW-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
private type Command = (String, String..., Record***) -> Unit
```

### lambda와 로컬 함수

현행 예제 `EX-R51a1-003`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let add = { x: Int, y: Int => x + y }
```

현행 예제 `EX-R51a1-024`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def outer(x: Int) -> Int = {
    [borrow x] def inner(y: Int) -> Int = {
        return x + y
    }
    return inner(1)
}
```

현행 예제 `EX-R51a1-026`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let consumeOnce = [move token] #once { value => consume(token, value) }
```

### trailing closure와 여러 callback

현행 예제 `EX-R51a1-NEW-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let names = users ~ map { user => user.name }
```

현행 예제 `EX-R51a1-NEW-008`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let value = transaction(onCommit: { => logCommit() }, onRollback: { error => log(error) })
```

### 이름 있는 함수 profile

현행 예제 `EX-R51a1-NEW-017`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def#async fetch(url: String) -> Bytes
    throws NetworkError
    effects {io}
= {
    return await client ~ get(url)
}
```

현행 예제 `EX-R51a1-NEW-018`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def#guard validPort(port: Int) -> Bool = {
    return port >= 0 and port <= 65_535
}
```

## 거부되거나 격리된 형식

| 형식 | 판정 |
|---|---|
| `{ (x: Int) => x }` | 거부; lambda parameter에 목록 괄호를 쓰지 않는다 |
| refutable pattern parameter | 거부; body에서 명시적으로 구조 분해한다 |
| 이름 있는 함수의 `= expr` | 거부; block 또는 `= return expr`를 사용한다 |
| named function 안의 `ret` | 거부 |
| lambda value body 안의 `return` | 거부 |
| local function의 암시적 outer capture | 거부 |
| bare ordinary call | 거부; bounded trailing-closure 예외만 있다 |
| unlabeled trailing closure 여러 개 | 거부; named argument를 사용한다 |
| named argument의 `name = value` | 거부; `name: value`를 사용한다 |
| parameter/type의 `**` named rest | recovery-only; `***`를 사용한다 |
| call-side `***record` | 거부; unfold는 `**record`다 |
| `async def` 또는 `entry def` | 제거됨; `def#async`, `def#entry`를 사용한다 |
| ordinary `def#unsafe` | 거부; `extern#C def#unsafe`는 명시적 Preview gate의 FFI 전용이다 |

## 상호작용

- class dispatch marker와 Trait witness marker는 glyph가 같아도 의미 영역이
  다르다.
- parameter는 identifier-only지만 body의 `if let`이나 guarded let은
  refutable Pattern을 사용할 수 있다.
- trailing closure는 capture, effect, error, ownership 검사를 완화하지
  않는다.
- `~` message call은 ordinary call과 별도 postfix owner이며 actor
  request/reply 책임을 유지한다.
- `def#async`와 `await`는 suspension을 숨기지 않으며 structured task
  경계를 따라야 한다.
- 함수 type의 `T...` 및 `Record***`는 public API digest와 compatibility에
  남는다.

## 정본 근거

- callable/closure 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- profile, 호출, capture 계약:
  [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
- frontend owner 정책:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 정본 설명과 진단:
  [`spec/language.md`](../../spec/language.md)
- 함수 type 책임:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
