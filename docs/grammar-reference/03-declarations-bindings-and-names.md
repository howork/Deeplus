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

멤버 가시성의 넓이 순서는 `- < # < +`다. `#`는 같은 Trait을 만족하거나
구조가 비슷하다는 이유로 접근을 허용하지 않는다. 같은 모듈이나 패키지의
peer, conformer, witness holder도 nominal subclass가 아니면 접근할 수 없다.
멤버의 유효 가시성은 이 멤버 domain과 최상위 owner reachability의
교집합이다. 따라서 `private` class의 `+` 멤버가 모듈 밖으로 노출되거나,
도달할 수 없는 owner의 `#` 멤버가 owner보다 넓게 공개되지 않는다.

현행 정본 문법에서 `MemberVisibility?`를 직접 소유하는 production은 정확히
15개다: `MemberFunctionDecl`, `TypeSideMemberFunctionDecl`,
`ConstructorDecl`, `StoredParameter`, `FieldDecl`, `TypeSideFieldDecl`,
`AccessorDecl`, `ForwardDecl`, `TraitMethodDecl`, `ConformanceMethodDecl`,
`ExtensionSetFunctionDecl`, `ActorOnDecl`, `ActorRequestDecl`,
`BitfieldNamedSlot`, `FlagNamedSlot`. 이 목록은 새 표기를 추가하지 않으며
문법 표기는 계속 `+`, `-`, `#`뿐이다.

`MemberVisibility?`가 생략되면 CST/frontend는 그 상태를 `OMITTED`/`null`로
보존한다. R58은 전역 기본값을 지정하지 않는다. 바로 위 parent owner의
계약이 생략을 해석하거나 거부하며, 결정되지 않은 `OMITTED`는
`- < # < +` 비교에 참여하지 않는다.

override는 최초 slot의 declaring nominal access anchor를 계속 사용한다.
parent owner가 생략을 처리한 뒤 override는 원래 가시성을 유지하거나 넓힐
수만 있고 좁힐 수 없다. 좁히면 `OVERRIDE_VISIBILITY_CANNOT_NARROW`다.
Trait witness가 requirement 가시성을 만족하지 못하는 별도 실패는 기존
`TRAIT_REQUIREMENT_VISIBILITY_MISMATCH`를 유지한다.

멤버 callable에 `public`, `common`, `private` 또는 `protected`를 쓰면 owner-form 오류인
`CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN`가 먼저 선택되고 override/Trait 비교는
하지 않는다. 올바른 sigil을 쓴 override가 좁아지면
`OVERRIDE_VISIBILITY_CANNOT_NARROW`가 이후 Trait mismatch보다 먼저다.
가시성은 정적 증명이며 runtime lookup/check, registry, MIR operation, xVM
instruction 또는 backend instruction을 추가하지 않는다. 공개 API residue는
owner와 멤버 가시성 및 서명 의존성을 정확히 기록한다. 거부된 선언이나
접근은 HIR residue를 남기지 않는다.

정상적인 owner 내부 접근:

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/member-visibility-trace-closure-r1.json -->
```deeplus
module core::base
public open class Base {
    #def hook*+() -> Int = return 1
    +def value() -> Int = return self ~ hook
}
```

다른 source unit과 모듈이어도 nominal subclass이면 `#` 접근이 되는 경계
예제:

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/member-visibility-trace-closure-r1.json -->
```deeplus
module app::derived
import core::base::Base
public class Derived derives Base {
    #def hook*.() -> Int = return 2
    +def expose() -> Int = return self ~ hook
}
```

거부 예제:

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/member-visibility-trace-closure-r1.json -->
```deeplus
// 같은 모듈의 peer일 뿐 subclass가 아니므로 거부한다.
module core::base

public class Peer {
    +def probe(base: Base) -> Int = return base ~ hook
    // REFERENCE_VISIBILITY_OR_ACTIVATION_VIOLATION
}

public class WrongWord {
    public def value() -> Int = return 1
    // CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN
}

public open class WideBase {
    +def value*+() -> Int = return 1
}
public class NarrowChild derives WideBase {
    #def value*.() -> Int = return 2
    // OVERRIDE_VISIBILITY_CANNOT_NARROW
}
```

### 바인딩

```ebnf
TopLevelBindingDecl ::= TopLevelVisibility? ("let" | "var")
                        Identifier TypeAnnotation? "=" Expr StatementBoundary

BindingCore         ::= ("let" | "var") BindingPattern "=" Expr
AssertiveBindingStmt ::= ("let" | "var") "!" BindingPattern "=" Expr
LocalBindingStmt    ::= BindingCore StatementBoundary
                      | RightwardLocalBindingSurface
                      | LazyBindingStmt
                      | GuardedBindingStmt
                      | AssertiveBindingStmt

LazyBindingStmt     ::= "let" HashTag Identifier TypeAnnotation? "=" Expr
                        StatementBoundary
GuardedBindingStmt  ::= "let" "?" BindingPattern "=" Expr
                        "else" Pattern "=>" GuardedBindingExit
                        StatementBoundary?
GuardedBindingExit  ::= GuardedReturnExit | GuardedThrowExit
                      | GuardedBreakExit | GuardedContinueExit
GuardedReturnExit   ::= "return" Expr?
GuardedThrowExit    ::= "throw" Expr
GuardedBreakExit    ::= ("break")+ Expr?
GuardedContinueExit ::= ("break")* "continue"
```

`let`은 불변 바인딩, `var`는 가변 바인딩이다. 지연 바인딩의 현행 표기는
`let#lazy`이며 `var#lazy`는 없다.

plain `let`/`var`의 Pattern은 checker가 irrefutable임을 증명해야 한다.
`let!`/`var!`은 refutable Pattern의 성공을 프로그래머가 assert하며,
mismatch는 `PatternMatchDefect`다. ordinary refutable 입력 검증에는
`if let`/`match`를 사용한다. Stable `trait_binding_failable_v1`의 `let?`는
core `trait#binding Failable` success/failure carrier를 한 번 소비하는 별도
owner이고 mandatory `else failurePattern => GuardedBindingExit` arm은
enclosing continuation을 구조적으로 떠나야 한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
if let [head, tail..] = values {
    consume(head, tail)
}

let! [x, y] = protocolGuaranteedPair
```

두 형식 모두 subject를 한 번 평가하고 성공 전에 component binder나
move를 공개하지 않는다.

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
- bare comma binding `let id, name = pair`는 Tuple Pattern으로
  정규화된다. List/Record/Map의 refutable 구조는 `if let`, `match` 또는
  명시적 `let!` owner를 사용한다. `let?`는 임의 Pattern mismatch sugar가
  아니다.
- 로컬 함수 이름은 선언 뒤부터 보이며 `public/common/private`를 붙일
  수 없다.
- 프로퍼티 값과 접근자는 저장소 소유권, 변경 권한, 수명 책임을
  보존해야 한다. 값으로 반환하는 안정 프로퍼티는 재사용 가능하고
  no-drop/lifecycle-free 조건을 만족해야 한다.

### R4 lexical frame and resolver identity

lexical lookup은 innermost `NameEnv`에서 시작해 exact
`(namespace, spelling)`이 있는 첫 frame에서 멈춘다. outer binding은 같은
tier 후보에 합쳐지지 않는다. 같은 철자는 서로 다른 namespace에서 공존할
수 있다. 한 frame에서는 single binding 중복을 거부하고, callable은
canonical overload-slot key가 모두 다를 때만 하나의 overload set을 만든다.
return type, responsibility-only 차이, 선언 순서는 새 slot이 아니다.
parameter와 callable root body local은 한 collision domain이다.

proper child block의 문법상 허용된 module/type/value/callable 또는 import
alias declaration은 ancestor 이름을 shadow할 수 있다. 이때 fresh typed
identity를 만들며 scope exit 뒤 outer identity가 다시 보인다. overload
set을 frame 사이에서 merge하지 않는다. member, associated item,
extension, witness capability는 lexical shadow가 아니다. 현행 profile에는
root-connected control-label surface가 없으므로 control-label 재사용
판정은 적용되지 않는다. 미래 `FLOW_CONTROL_PROFILE`이 별도 carrier를
활성화하면 그때 live ancestor 재사용을 거부한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/name-resolution-modules-current.json -->
```deeplus
private def inspect(value: Int) -> Int = {
    {
        let value = 2       // fresh child HirLocalId
        consume(value)
    }
    return value            // parameter identity is visible again
}
```

match/pattern probe의 binder는 provisional이므로 `NameEnv`에 들어가지
않는다. 성공 commit만 fresh `HirLocalId`를 만들고 실패는 0개를 만든다.
local function은 declaration 뒤부터 보이며 hoisting하지 않는다.
`NameEnv`, extension `ActivationEnv`, `WitnessVisibilityEnv`는 서로
독립이고 scope exit는 해당 frame만 pop한다.

## 평가·소유권·효과

일반 바인딩과 오른쪽 방향 바인딩은 initializer를 정확히 한 번 평가한다.
평가가 성공한 뒤에만 새 이름과 move/borrow 책임을 원자적으로 commit한다.
실패하면 부분 바인딩이나 별도 flow-binding node가 남지 않는다.

지역 direct mutable Plain place의 병렬 대입도 같은 transaction 원칙을
따른다. `left, right = right, left`는 target을 왼쪽부터 한 번 resolve하고
RHS Tuple을 한 번 평가한 뒤 하나의 logical commit을 수행한다. target
overlap, member/index/shared place와 commit 중 user callback은 Stable
profile에서 거부한다.

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
| `var#lazy` | 거부 |
| 숨은 실패 채널을 memoize하는 lazy 값 | 거부; 명시적 `Result`를 사용한다 |
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
- import alias identity는 `(ResolverScopeId, namespace, local_name)`이며
  resolved target과 `SourceOriginId`는 trace content다.
- canonical HIR에는 analysis-HIR의 unresolved name이나
  `ResolvedOverloadSetRef`를 남기지 않는다. exact callable winner는
  다음 generic/ordinary-overload cluster의 책임이다.
- 멤버 가시성과 class dispatch marker는 서로 다른 축이다. 예를 들어
  `+def render.()`의 `+`는 가시성이고 `.`은 final dispatch slot이다.
- `#lazy`의 `#`는 member visibility가 아니라 선언 profile role이다.

## 정본 근거

- 문법: [`spec/grammar/deeplus.dpg`](../../spec/grammar/deeplus.dpg)
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
