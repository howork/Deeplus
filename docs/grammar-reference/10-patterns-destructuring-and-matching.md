# 패턴, 구조 분해, 매칭

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 Pattern 문법, 문맥별 허용 정책, 구조 분해, guarded binding,
statement `match`, value `@match`, exhaustiveness와 flow narrowing을 설명한다.
모든 Pattern owner는 하나의 lossless CST와 하나의 정규화 AST를 공유한다.

예제는 현행 corpus의 `accept`, `source_activation: none` 항목이다. 제품
parser/checker/lowering/runtime 실행은 `NOT_RUN`이며 정적 fixture를 제품
conformance PASS로 해석하지 않는다.

## 문법

### Pattern 형식

```ebnf
Pattern      ::= OrPattern
OrPattern    ::= AliasPattern ("|" AliasPattern)*
AliasPattern ::= MovePattern ("as" Identifier)?
MovePattern  ::= "move"? PatternPrimary

PatternPrimary ::= TypedBindingPattern
                 | Identifier
                 | RecordPattern
                 | ListPattern
                 | VariantPattern
                 | "_"
                 | UnitSyntax
                 | Literal
                 | ParenthesizedPattern

TypedBindingPattern ::= Identifier ":" TypeRef
RecordPattern       ::= "${" PatternFieldList? "}"
ListPattern         ::= "["
                        (ListPatternPrefix ("," IgnoredListRest)? ","?
                        | IgnoredListRest ","?)?
                        "]"
IgnoredListRest     ::= ".." "_"
VariantPattern      ::= VariantQualifier Identifier VariantPatternPayload?
VariantQualifier    ::= TypeRef "::" | "::"
```

괄호는 하나의 Pattern을 묶을 뿐 tuple Pattern을 만들지 않는다. Record
Pattern은 정적으로 알려진 label subset을 열며 rest 형식이 없다. List
Pattern은 exact length이거나 마지막에 단 하나의 ignored remainder
`.._`만 둘 수 있다.

### 바인딩 문맥

```ebnf
BindingCore       ::= ("let" | "var") BindingPattern "=" Expr
GuardedBindingStmt ::= "let" BindingPattern "=" Expr
                       "else" GuardedBindingFailure StatementBoundary?

PatternControlCondition ::= Expr | "let" Pattern "=" Expr
ForLoop          ::= "for" ("let" Pattern | Pattern) "in" Expr
                     GuardClause? Block MatchStatement?
WhileLoop        ::= "while" PatternControlCondition Block MatchStatement?
MatchStatement   ::= "match" MatchCore
MatchExpr        ::= "@" "match" MatchCore
```

`BindingPattern`의 마지막 type annotation은 binding subject 전체의 정적
expected type을 정한다. recursive child의 `name: Type`은 계속 child typed
binder다.

### match 분기

```ebnf
MatchArm ::= MatchHead GuardClause? "=>" MatchArmBodySlot
MatchHead ::= Pattern | "otherwise"
```

statement `match`는 statement body를 실행한다. value `@match`는 각 정상
arm에서 값을 만들어야 한다. value arm의 block은 마지막 `ret`로 로컬
값을 전달할 수 있다.

## 허용과 정적 의미

### 문맥별 refutability

| 문맥 | 허용 정책 | mismatch |
|---|---|---|
| ordinary/lambda parameter | identifier-only | 정적 거부 |
| plain `let`/`var` | checker가 irrefutable임을 증명 | 정적 거부 |
| bare `for` | iteration item에 대해 irrefutable | 정적 거부 |
| guarded `let` | refutable | 구조적으로 unconditional인 `else` exit |
| `if let` | refutable | false 분기 |
| `while let` | refutable | loop 종료 |
| `for let` | refutable | 해당 candidate를 건너뜀 |
| statement/value match | refutable | 다음 arm |
| declarative function clause | 정적으로 disjoint하고 exhaustive인 partition | 다음 clause 또는 정적 거부 |

guard는 최대 하나이며 terminating, pure, nonthrowing, nonsuspending Bool
이어야 한다. probe binder를 consume/escape하거나 authority를 얻지 않는다.
guarded arm은 usefulness에는 참여하지만 unconditional coverage를
제공하지 않는다.

### 타입 바인더와 Union

`name: Type`은 기본적으로 irrefutable 정적 typed binder다. 다만 refutable
owner의 subject가 이미 정규화된 closed Union이고 `Type`이 그 Union의
정확한 한 alternative identity일 때만 `UnionAlternativeBindPattern`으로
정교화된다. 이때 읽는 것은 Union injection identity뿐이다.

이 형식은 일반 runtime type test가 아니다. subtype search, refinement
실행, reflection, Trait discovery, provider lookup을 하지 않는다.

### 현재 구조 분해 carrier

- Enum, Option, Result와 다른 nominal variant payload
- 정적으로 알려진 Record label subset
- exact List 또는 마지막 `.._`가 있는 List
- 명시적인 closed Union alternative binder

ordinary Class, Dyn, Facet, FFI/opaque representation은 Pattern이 직접 열지
않는다. 필요한 경우 정본이 허용한 explicit Record view, refinement,
borrowed refinement, verified adapter를 사용한다.

### 완전성과 유용성

분석은 하나의 순서 있는 유한 partition pass다.

- 새 structural cell을 더하지 않는 arm은 `MATCH_ARM_UNREACHABLE`이다.
- guard는 coverage cell을 제거하지 않는다.
- guard 때문에 residual이 남으면 `MATCH_NONEXHAUSTIVE_AFTER_GUARDS`다.
- residual이 없는데 `otherwise`가 오면 `OTHERWISE_UNREACHABLE`이다.
- 나머지 final residual은 `MATCH_NOT_EXHAUSTIVE`다.

Option, Result, closed Union, Enum, List exactness, loop outcome은 각자의
명시적 Pattern universe를 사용한다. sealed Class family의 닫힘은 subtype
분석과 명목적 도달 가능성에는 정보를 제공하지만 constructor Pattern
cell을 만들지 않는다. 따라서 sealed family가 닫혀 있다는 사실만으로
`Circle(radius)` 같은 Class 구조 분해나 Class 기반 exhaustiveness를
허용해서는 안 된다. 불완전하거나 결정할 수 없는 partition을
exhaustive라고 추정하지 않는다.

## 평가·소유권·효과

모든 refutable owner는 다음 순서를 지킨다.

1. subject를 정확히 한 번 평가한다.
2. place/owner를 얻는다.
3. nonconsuming structural `TestPlan`을 만들고 실행한다.
4. nonowning probe binder를 노출한다.
5. 있으면 pure Bool guard를 평가한다.
6. 성공할 때만 move/borrow/binding을 한 번 원자적으로 commit한다.
7. final binder를 노출하고 body를 실행한다.
8. owner별 exit 또는 join을 수행한다.

구조 실패나 false guard는 binding, move, exclusive borrow, authority를
부분 commit하지 않는다. `pattern as name`은 clone이 아니라 borrow alias며,
같은 subject의 moved/exclusive descendant와 함께 존재할 수 없다.

flow proof 환경은 선언 type과 별도다. 성공한 Enum/Union Pattern은 해당
case/alternative fact를 더할 수 있다. join은 모든 incoming edge에 있는
fact만 남긴다. subject 대입, alias mutation, exclusive borrow, escape,
capture, consume, 또는 subject를 바꿀 수 있는 호출은 관련 fact를 죽인다.

## 현행 예제

### 값 match와 문장 match

현행 예제 `EX-R51a1-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let label = @match state {
    ::ready => "ready"
    otherwise => "other"
}
match state {
    ::ready => start()
    otherwise => stop()
}
```

### guarded let의 Result 잔여

현행 예제 `EX-R51a1-GLET-P-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let ::ok(document) = parse(text)
else ::err(error) => throw error
persist(document)
```

### 패턴 제어군

현행 예제 `EX-R51e-013`,
원본 `examples/guide/review-corpus.md`:

```deeplus
if let Option::some(value) = candidate {
    consume(value)
}
```

현행 예제 `EX-R51e-014`,
원본 `examples/guide/review-corpus.md`:

```deeplus
while let Option::some(job) = queue.next() {
    process(job)
}
```

현행 예제 `EX-R51e-015`,
원본 `examples/guide/review-corpus.md`:

```deeplus
for let Result::ok(value) in results if value > 0 {
    consume(value)
}
```

### List의 무시된 나머지

현행 예제 `EX-R51f3-COH-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
if let [head, .._] = values {
    consume(head)
}
```

### 닫힌 Union 대안 바인더

현행 예제 `EX-R51a1-RCTS-UNION-P-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
private type TextOrNumber = Int | String
let value: TextOrNumber = 13
let text = @match value {
    n: Int => n ~ toString()
    s: String => s
}
```

## 거부되거나 격리된 형식

sealed Class도 현행 constructor Pattern carrier가 아니다. 다음 예시는
명목 family가 닫혀 있더라도 Class 내부 표현을 Pattern으로 열려고 하므로
거부된다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
public sealed class Shape {}
public final class Circle : Shape {
    +let radius: Int
}

let area = @match shape {
    Circle(radius) => radius * radius
    otherwise => 0
}
```

Class가 명시적으로 제공하는 Record view 또는 별도의 안전한 adapter를
통해 Pattern carrier로 변환한 뒤 매칭해야 한다. 이 구분은 Class의
봉인성, layout, 생성자 형식과 Pattern의 데이터 공개 권위를 섞지 않게
한다.

| 형식 또는 주장 | 판정 |
|---|---|
| ordinary parameter의 구조 분해 Pattern | 거부; identifier를 받은 뒤 body에서 분해한다 |
| tuple Pattern `(a, b)` | 현행 아님; 괄호는 Pattern 하나만 묶는다 |
| Record rest/open tail Pattern | 현행 아님 |
| captured List rest `..tail` | 현행 아님 |
| middle 또는 여러 List rest | 현행 아님 |
| dot-case `.ready` | 제거됨; `::ready` 또는 `State::ready`를 사용한다 |
| bare `Some`/`None` | 제거됨; Option case qualification을 사용한다 |
| ordinary Class 내부를 직접 여는 Pattern | 거부 |
| typed binder를 일반 runtime `is-a` test로 사용 | 거부 |
| guard 안의 effect, throw, suspend, consume, authority acquisition | 거부 |
| Or-pattern branch마다 다른 binder/type/mode/region | 거부 |
| Pattern 실패 뒤 부분 move 또는 부분 binding | 금지 |
| user-defined extractor/backtracking Pattern | 현행 아님 |

## 상호작용

- Enum case expression payload는 argument plane이고 Pattern payload는 Pattern
  plane이므로 각각 별도 검사를 거친다.
- `def#guard` 호출은 Bool을 만들지만 호출 자체는 narrowing fact를 만들지
  않는다. 정본이 허용한 inline R0 guard만 true edge에 유한 fact를 더한다.
- Union injection과 normalization이 먼저 닫혀 있어야 typed alternative
  binder가 작동한다.
- ownership mode `move`는 structural test 때가 아니라 atomic commit 때
  적용된다.
- List/Record value literal 문법과 Pattern 문법은 opener를 공유해도 서로
  다른 parser goal이다.
- closed Union의 `is`/`!is`는 `Bool`과 보완적인 flow fact만 만들고 값을
  바인딩하지 않는다. alternative 값을 바인딩하는 owner는 이 장의 typed
  pattern이다.
- callable clause의 source order는 겹침을 해결하지 않는다. clause family는
  먼저 disjoint/exhaustive여야 한다.

## 정본 근거

- Pattern 및 match 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- 문맥 정책:
  [`spec/patterns/pattern-context-policies.json`](../../spec/patterns/pattern-context-policies.json)
- Pattern 종류:
  [`spec/patterns/pattern-kinds.json`](../../spec/patterns/pattern-kinds.json)
- lowering 책임:
  [`spec/patterns/pattern-lowering.json`](../../spec/patterns/pattern-lowering.json)
- narrowing 계약:
  [`spec/contracts/type-refinement-narrowing-coherence.json`](../../spec/contracts/type-refinement-narrowing-coherence.json)
- 정본 설명과 진단:
  [`spec/language.md`](../../spec/language.md)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
