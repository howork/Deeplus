# 선언, 바인딩, 이름

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 Deeplus 선언, 가시성, 바인딩, 지연 값, 프로퍼티를 독자가
찾기 쉽게 재구성한 문서 투영이다. 정본 문법과 계약을 대체하지 않는다.

예제는 `examples/guide/review-corpus.md`에서 `expected_outcome: accept`,
`source_activation: none`인 항목을 그대로 가져왔다. 이 증거는 설계 정적
검증이며 제품 lexer/parser/checker/runtime 실행은 `NOT_RUN`이다.

## 문법

### 최상위 선언과 멤버 가시성

```ebnf
TopLevelVisibility ::= "public" | "private" | "common"
MemberVisibility   ::= "+" | "-" | "#"
```

두 가시성 어휘는 서로 바꿔 쓸 수 없다.

| 위치 | 표기 | 의미 |
|---|---|---|
| 최상위 | `public` | 외부 패키지 API에 들어갈 자격이 있으며, 실제 외부 노출에는 허용된 export/module interface가 필요하다 |
| 최상위 | `common` | 선언 패키지의 모듈 사이에서 보이지만 외부 API와 재수출에는 들어가지 않는다 |
| 최상위 | `private` | 선언 모듈 안에서만 보인다 |
| 멤버 | `+` | 공개 멤버 |
| 멤버 | `-` | 선언 nominal type 전용 private 멤버 |
| 멤버 | `#` | 선언 nominal type과 그 nominal subclass에서만 보이는 hierarchy-protected 멤버 |

`#`는 같은 Trait을 만족하거나 구조가 비슷하다는 이유로 접근을 허용하지
않는다. 공개 API residue는 가시성과 그 서명 의존성을 정확히 기록한다.

### 바인딩

```ebnf
TopLevelBindingDecl ::= TopLevelVisibility? ("let" | "var")
                        Identifier TypeAnnotation? "=" Expr StatementBoundary

BindingCore         ::= ("let" | "var") BindingPattern "=" Expr
LocalBindingStmt    ::= BindingCore StatementBoundary
                      | RightwardLocalBindingSurface
                      | LazyBindingStmt
                      | GuardedBindingStmt

LazyBindingStmt     ::= "let" HashTag Identifier TypeAnnotation? "=" Expr
                        StatementBoundary
```

`let`은 불변 바인딩, `var`는 가변 바인딩이다. 지연 바인딩의 현행 표기는
`let#lazy`이며 `var#lazy`는 없다.

오른쪽 방향 로컬 바인딩은 다음 두 형식만 쓴다.

```ebnf
RightwardLocalBindingSurface ::= Expr "->" DollarLocalBinding
                                  StatementBoundary
DollarLocalBinding            ::= "$" Identifier TypeAnnotation?
                                | "$$" Identifier TypeAnnotation?
```

`$name`은 평범한 `let name`, `$$name`은 평범한 `var name`으로 정규화된다.
화살표와 달러 표기는 CST에 보존되지만 별도 AST/HIR/MIR 의미를 만들지
않는다.

### 프로퍼티와 접근자

```ebnf
AccessorPropertyDecl ::= ("let" | "var") Identifier TypeAnnotation
                         ":=" AccessorSpec
AccessorSpec         ::= AccessorDecl | "{" AccessorDecl+ "}"
AccessorDecl         ::= MemberVisibility? "get" Block
                       | MemberVisibility? "set" "(" Identifier ")" Block
```

프로퍼티 헤더는 `let` 또는 `var`로 시작하며 멤버 가시성 sigil을 붙이지
않는다. 가시성을 명시하려면 개별 `get`/`set`에 `+`, `-`, `#`를 붙인다.
단일 bare `get` 또는 bare `set`도 현행 접근자 형식이다. 접근자가 둘
이상이면 중괄호 블록을 사용한다. 구분자는 반드시 `:=`이다.

## 허용과 정적 의미

- 최상위 class, trait, enum은 정해진 최상위 가시성을 명시해야 한다.
- `public` 서명이 `common` 또는 `private` identity를 외부에 노출하면
  public API closure가 거부한다.
- primary constructor의 `+let`, `-let`, `#let`과 대응 `var` 형식은 생성
  멤버의 가시성만 정한다.
- `let#lazy` initializer는 순수하고 동기적이며 nonthrowing,
  authority-free, resource-free여야 하고 재사용 가능한 불변 값만
  capture한다.
- 실패 가능한 지연 계산은 숨은 throw 채널 대신 명시적인
  `Result<T, error E>` 값을 사용한다.
- 오른쪽 방향 바인딩 대상은 같은 block에서 새로 생기는 단일
  identifier여야 한다. member/index/place/pattern이나 기존 이름을
  대상으로 삼을 수 없다.
- 로컬 함수 이름은 선언 뒤부터 보이며 `public/common/private`를 붙일
  수 없다.
- 프로퍼티 값과 접근자는 저장소 소유권, 변경 권한, 수명 책임을
  보존해야 한다. 값으로 반환하는 안정 프로퍼티는 재사용 가능하고
  no-drop/lifecycle-free 조건을 만족해야 한다.

## 평가·소유권·효과

일반 바인딩과 오른쪽 방향 바인딩은 initializer를 정확히 한 번 평가한다.
평가가 성공한 뒤에만 새 이름과 move/borrow 책임을 원자적으로 commit한다.
실패하면 부분 바인딩이나 별도 flow-binding node가 남지 않는다.

지연 바인딩에는 initialization owner와 commit이 각각 하나뿐이다. 동시
force는 하나의 불변 결과만 공개해야 하며, cycle과 재진입은 결정적으로
거부된다. 실패를 값으로 보존해야 한다면 그 값은 명시적인 `Result`이다.

`var` 대입과 프로퍼티 setter는 가변 place 및 접근 권한 검사를 통과해야
한다. 접근자 문법만으로 숨은 공유, actor crossing, effect, authority를
얻지 않는다.

## 현행 예제

### 최상위와 생성 멤버 가시성

현행 예제 `EX-R49-PRIMARY-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public data class UserProfile(
    +let name: String
    +let age: Int
    -let passwordHash: PasswordHash
)
```

### 현행 지연 바인딩

현행 예제 `EX-R51b-GRAM-P-002`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let#lazy model: Result<Model, error ParseError> = parseResult(text)
inspect(model)
```

### 오른쪽 방향 불변·가변 바인딩

현행 예제 `EX-R51a1-NEW-005`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def readPort() -> Int = {
    loadPort() -> $port: Int
    return port
}
```

현행 예제 `EX-R51a1-NEW-006`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def incrementCount() -> Int = {
    loadCount() -> $$count: Int
    count += 1
    return count
}
```

## 거부되거나 격리된 형식

| 형식 | 판정 |
|---|---|
| 멤버에 `public/private/common` 사용 | 거부; `+/-/#`를 사용한다 |
| 로컬 함수에 최상위 가시성 사용 | 거부 |
| 프로퍼티 헤더에 `+/-/#` 사용 | 거부; sigil은 개별 접근자에 둔다 |
| 접근자 구분자로 `=` 사용 | 거부; `:=`가 필요하다 |
| `let@lazy` | recovery-only; `let#lazy`를 사용한다 |
| `var#lazy` | 거부 |
| 숨은 실패 채널을 memoize하는 lazy 값 | 거부; 명시적 `Result`를 사용한다 |
| `expr -> let name` | 제거된 형식 |
| `expr -> object.field`, `expr -> values[i]` | 거부; fresh local만 가능하다 |
| 오른쪽 방향 바인딩 chaining | 거부 |

## 상호작용

- BindingPattern의 허용 범위와 원자적 commit은
  [패턴, 구조 분해, 매칭](10-patterns-destructuring-and-matching.md)이
  정한다.
- 함수 profile, parameter, local function capture는
  [함수, 메서드, 클로저, 호출](05-functions-methods-closures-and-calls.md)이
  정한다.
- 최상위 이름의 외부 노출은 source root, module interface, export,
  public API digest가 함께 결정한다.
- 멤버 가시성과 class dispatch marker는 서로 다른 축이다. 예를 들어
  `+def render.()`의 `+`는 가시성이고 `.`은 final dispatch slot이다.
- `#lazy`의 `#`는 member visibility가 아니라 선언 profile role이다.

## 정본 근거

- 문법: [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- frontend 허용 정책:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 선언·바인딩 정본 설명:
  [`spec/language.md`](../../spec/language.md)
- callable/flow 계약:
  [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
- 기능 registry:
  [`spec/features/catalog`](../../spec/features/catalog)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
