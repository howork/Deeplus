# 패턴, 구조 분해, 매칭

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

Pattern은 `match`에만 붙는 보조 문법이 아니다. Deeplus에서는 지역
바인딩, 조건, 반복, 함수 진입, 예외 처리와 지역 병렬 대입이 같은
정규화 Pattern AST를 사용한다. 문맥은 Pattern을 다시 정의하지 않고
성공 조건, 실패 경로, 소유권 commit과 coverage 의무만 공급한다.

이 장의 Stable 설계는 source 정본이다. 제품 lexer, parser, checker,
HIR/MIR, xVM과 backend의 실행 증거는 여전히 `NOT_RUN`이다. Preview
표면은 해당 절에서 별도로 표시하며 Stable이라고 해석하지 않는다.

## 문법

### 공통 Pattern 대수

```ebnf
Pattern      ::= OrPattern
OrPattern    ::= AliasPattern ("|" AliasPattern)*
AliasPattern ::= MovePattern ("as" Identifier)?
MovePattern  ::= "move"? PatternPrimary

PatternPrimary ::= TypedBindingPattern
                 | Identifier
                 | "_"
                 | UnitSyntax
                 | Literal
                 | ParenthesizedPattern
                 | TuplePattern
                 | ListPattern
                 | RecordPattern
                 | MapPattern
                 | VariantPattern
                 | NominalPattern
                 | PinPattern
                 | RangePattern
                 | RelationalPattern
```

`(p)`는 grouping이고 `(p,)`는 원소가 하나인 Tuple Pattern이다. 쉼표가
둘 이상의 항목을 나누면 Tuple Pattern이다. bare comma product도 같은
Tuple로 정규화되므로 별도의 다중 값 runtime carrier를 만들지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let (id, name) = pair
let singleton = (13,)
let id, name = pair
```

마지막 두 바인딩 형식의 결과 type은 모두 Tuple이다. 문맥이 다르더라도
Tuple 요소를 임의의 `Sequence`로 다시 해석하지 않는다.

### Sequence rest

List의 위치 기반 rest는 binder에 붙은 suffix로 collection 방향을
드러낸다. Stable Tuple Pattern은 exact fixed product이며 rest를 갖지 않는다.

```ebnf
ListRestPattern   ::= RestBinding ".."
RestBinding       ::= Identifier | "_"
```

Stable 철자는 다음과 같다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
[head, tail..]                  // 뒤쪽 remainder
[leadings.., last]              // 앞쪽 remainder
[first, middle.., last]         // 양쪽 고정 항목 사이
[_..]                           // 전체 remainder를 무시
```

marker는 이름에 붙으며 한 Pattern에 rest는 최대 하나다. middle rest에는
앞뒤로 적어도 하나의 고정 child가 있어야 한다. 제거된 prefix
`[head, ..tail]`이나 double-sided `[first, ..middle.., last]`는 recovery
진단만 내고 canonical Pattern을 만들지 않는다.

동적 List의 길이는 runtime에 판정하므로 일반적으로 refutable하다.
borrowed List에서 capture한 remainder는 `ListRestView<T>`다. 이 view는
원본 owner region, 원래 1-based coordinate projection과 길이가 0일 수도
있는 `RankSpan`을 보존한다. compiler가 부여하는 intrinsic
`Sequence<T>` witness 외에 일반 `Sequence` conformance가 rest 분해를
활성화하지 않으며, 숨은 복사·할당·수명 연장은 없다.

### Record Pattern

```ebnf
RecordPattern ::= "${" RecordPatternEntries? "}"
RecordPatternEntry ::= Identifier
                     | Identifier ":" RecordDestination
                     | RecordRestPattern
RecordRestPattern ::= ("_" | Identifier) "**"
```

Record는 exact-by-default다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
${x, y}          // field set이 정확히 x, y
${x, y, _**}    // x, y를 요구하고 나머지는 명시적으로 무시
${x, y, rest**} // 나머지를 static named residual로 capture
```

mapping의 왼쪽은 source label이고 오른쪽은 destination Pattern이다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let ${x: horizontal, y: vertical} = point
```

위 코드는 `point.x`를 `horizontal`에, `point.y`를 `vertical`에
바인딩한다. source와 destination이 같은 `${x}`만 colon을 생략한다.
destination 자체가 typed 또는 nested Pattern이면 colon owner가 보이도록
괄호로 묶는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let ${id: (id: UserId), _**} = payload
let ${address: ${city, zip}, _**} = user
```

field order는 의미 identity가 아니지만 source ordinal은 진단과 평가
provenance에 남는다. 같은 source field를 두 번 요구하거나 보이지 않는
field를 여는 Pattern은 정적으로 거부한다.

### Map Pattern

```ebnf
MapPattern ::= "#" "map" "{" MapPatternEntries? "}"
MapPatternEntry ::= MapValueTarget ":" MapKeyPattern
                  | MapRestPattern
MapKeyPattern ::= Literal | PinPattern
MapRestPattern ::= ".." ("_" | Identifier)
```

Map도 exact-by-default지만 keyed orientation은 Record-family의 label-first
방향과 다르다. Map은 기존 `destination: key`와 `..rest`/`.._`를 그대로
유지하며 static named residual이나 `NamedPack`을 만들지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
if let #map{
    userId: "id"
    displayName: "name"
    ..rest
} = payload {
    publish(userId, displayName)
}
```

왼쪽은 destination value Pattern, 오른쪽은 source key다. key에는 literal
또는 `^stableValue`만 쓸 수 있다. key normalization과 equality는
compiler가 선택한 pure·total key law를 사용하고 arbitrary call,
provider lookup이나 iteration-order winner를 만들지 않는다. normalized
duplicate key는 정적 오류다.

### transparent nominal product와 Enum

Record, schema, data class와 명시적으로 pattern-transparent인 nominal
product는 field identity로 분해한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let Point${x, y} = point
let User${displayName: name, _**} = user
```

ordinary Class가 `sealed` 또는 `final`이라는 이유만으로 내부 field가
열리지는 않는다. Dyn, Facet, FFI와 opaque representation도 자동으로
Pattern carrier가 되지 않는다.

Enum의 positional payload와 labeled payload는 서로 다른 모양을 보존한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
match result {
    ::ok(value) => consume(value)
    ::error${message, code, _**} => report(code, message)
}
```

case identity를 먼저 확인한 뒤 active payload만 projection한다. inactive
payload의 place, serialization tag, runtime discriminant 또는 ABI
identity를 Pattern binder로 취급하지 않는다.

### pin, range와 relational Pattern

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
match measurement {
    ^expected => ::same
    0..<10 => ::low
    >= 10 => ::high
}
```

`^expected`는 새 binder가 아니다. 이미 존재하는 stable value를 정확히
한 번 읽어 compiler-selected strong equality로 비교한다. mutable place,
arbitrary call 또는 equality evidence가 없는 값은 pin operand가 아니다.

range와 relational Pattern의 Stable domain은 `Int`, `UInt`, `Char`,
명시적으로 ordered인 Enum과 exact total-order domain이다. Float는 NaN,
signed zero와 partial-order 문제 때문에 Preview다. Pattern 검사는
사용자 정의 operator lookup을 수행하지 않는다.

### bounded binder Pattern

match arm에서 범위 검사와 subject binding을 함께 표현하려면 monotone
chained binder를 쓴다.

```ebnf
MatchHead ::= BoundedBinderPattern | Pattern | "otherwise"
BoundedBinderPattern ::= PatternBound OrderedComparisonOperator Identifier
                         OrderedComparisonOperator PatternBound
```

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.dpg -->
```deeplus
let description = @match score {
    0 <= value <= 100 => "normal:${value}"
    otherwise => "abnormal"
}
```

checker는 match subject를 정확히 한 번 읽고 두 경계를 비교한 뒤, 둘 다
참인 arm에서만 subject를 `value`에 bind한다. arm body의 `value`에는
`0 <= value <= 100`이라는 branch-local refinement fact가 붙지만 새로운
nominal type, serialization tag 또는 runtime discriminant를 만들지는
않는다.

두 연산자는 모두 `<`/`<=` 방향이거나 모두 `>`/`>=` 방향이어야 한다.
따라서 `0 <= value >= 100`은
`MATCH_CHAIN_BINDER_DIRECTION_MIXED`로 거부한다. 서로 독립된 조건이
필요하면 기존 guard를 명시한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.dpg -->
```deeplus
let description = @match score {
    value if value >= 0 and value <= limit => "bounded:${value}"
    otherwise => "outside"
}
```

`otherwise`는 항상 `=>`를 사용한다. `otherwise =`라는 별도 fallback
문법은 없다. bounded binder는 match arm head만의 표면이며 일반 type,
declaration 또는 standalone expression으로 확장되지 않는다.

### 바인딩과 제어 문맥

```ebnf
BindingCore          ::= ("let" | "var") BindingPattern "=" Expr
AssertiveBindingStmt ::= ("let" | "var") "!" BindingPattern "=" Expr
GuardedBindingStmt   ::= "let" "?" BindingPattern "=" Expr
                         "else" Pattern "=>" GuardedBindingExit
                         StatementBoundary?
GuardedBindingExit   ::= GuardedReturnExit | GuardedThrowExit
                       | GuardedBreakExit | GuardedContinueExit
GuardedReturnExit    ::= "return" Expr?
GuardedThrowExit     ::= "throw" Expr
GuardedBreakExit     ::= ("break")+ Expr?
GuardedContinueExit  ::= ("break")* "continue"
PatternConditionChain ::= PatternCondition
                          ("and" "then" PatternCondition)*
PatternCondition      ::= Expr | "let" Pattern "=" Expr
```

`BindingPattern`은 top-level type annotation의 owner를 보존한다. child의
`name: Type`과 binding subject 전체의 `: Type`을 parser가 추측으로
뒤집지 않는다.

plain `let`/`var`는 checker가 irrefutable임을 증명해야 한다. `let!`과
`var!`는 refutable Pattern을 명시적으로 assert하며 mismatch 때
`PatternMatchDefect`를 만든다. 실패 전에 component binding, move,
exclusive borrow 또는 assignment write가 생기지 않는다.

Stable `trait_binding_failable_v1`의 `let?`는 임의 refutable Pattern의
mismatch sugar가 아니다. core
`trait#binding Failable`의 유일한 direct-global witness를 먼저 선택하고,
source를 정확히 한 번 소비해 `Failable::branch`를 한 번 호출한다. success와
failure Pattern은 각각 associated `Success`/`Failure` type에 irrefutable해야
하며 failure arm은 `return`, `throw`, `break` 또는 `continue`로 enclosing
local continuation을 반드시 떠난다. `Option<T>`의 Failure는 `Unit`,
`Result<T, error E>`의 Failure는 `E`다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let! [head, tail..] = nonemptyValues

let? document = parse(text)
else error => throw error
```

condition chain은 왼쪽에서 오른쪽으로 진행하며 뒤 condition은 앞에서
성공한 probe binder를 읽을 수 있다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
if let ::some(user) = lookup(id)
    and then let ${email, _**} = user.profile
    and then isVerified(email)
{
    publish(user)
}
```

중간 단계가 실패하면 뒤 단계는 평가하지 않고 tentative binder는 모두
폐기한다.

### 함수·lambda parameter

이름 있는 함수는 call channel identifier를 보존한 채 body-entry에
irrefutable structural Pattern을 둘 수 있다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
private def distance(point Point${x, y}: Point) -> Float = {
    return sqrt(x ^ 2 + y ^ 2)
}
```

`point`는 call label과 whole-value local identity다. `Point${x, y}`는
호출 인수 결합과 ownership commit이 끝난 뒤 body 진입에서 수행된다.
Pattern은 overload 선택, function type 또는 public ABI identity에
참여하지 않는다. refutable parameter Pattern은 거부한다.

lambda에서도 irrefutable Pattern만 허용한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let sumPair = { (x, y): (Int, Int) => x + y }
let add = { x: Int, y: Int => x + y }
```

첫 lambda는 Tuple parameter 하나를 분해하고, 둘째는 parameter 두 개를
받는다.

### catch

catch Pattern은 refutable할 수 있다. error subject는 한 번 평가되고 첫
성공 catch가 선택된다. 어느 catch에도 맞지 않는 recoverable Error는
바깥 error 경계로 전파된다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
try {
    loadConfiguration()
}
catch IOError${path, _**} if isConfigPath(path) {
    useDefaults(path)
}
catch error: IOError {
    throw error
}
```

catch guard도 pure Bool, nonthrowing, nonsuspending이며 probe binder를
소비하거나 escape시키지 않는다.

### 지역 병렬 대입

bare comma product와 Tuple Pattern assignment는 하나의 Tuple plan으로
정규화된다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
left, right = right, left
(x, y) = nextPair
```

Stable target은 서로 겹치지 않는 direct local mutable Plain place와
`_`뿐이다. target을 왼쪽부터 한 번 resolve하고 RHS를 한 번 평가한 뒤,
모든 type·ownership·overlap 검사가 성공해야 하나의 logical commit을
수행한다. 이는 CPU multiword atomic instruction이나 actor isolation
bypass를 뜻하지 않는다. member/index/shared/actor target은 Preview 또는
별도 synchronized authority가 필요하다.

## 문맥별 refutability

| 문맥 | 허용 정책 | mismatch |
|---|---|---|
| ordinary/lambda parameter | subject type에 대해 irrefutable | 정적 거부 |
| plain `let`/`var` | checker-proven irrefutable | 정적 거부 |
| bare `for` | item type에 대해 irrefutable | 정적 거부 |
| `let!`/`var!` | refutable | `PatternMatchDefect` |
| guarded `let`/`var` | refutable | unconditional `else` exit |
| `if let` | refutable | false branch |
| `while let` | refutable | loop 종료 |
| `for let` | refutable | 해당 candidate를 건너뜀 |
| statement/value match | refutable | 다음 arm |
| catch | refutable | 다음 catch 또는 error 전파 |
| declarative clause | disjoint하고 exhaustive인 partition | 정적 거부 |
| 지역 Pattern assignment | irrefutable·distinct local places | 정적 거부 |

## 평가·소유권·효과

모든 refutable owner는 다음 순서를 지킨다.

1. subject를 정확히 한 번 평가한다.
2. place와 owner를 얻는다.
3. nonconsuming structural `TestPlan`을 만든다.
4. 구조, case, length, field/key와 value 조건을 검사한다.
5. nonowning probe binder를 노출한다.
6. 있으면 pure Bool guard를 한 번 평가한다.
7. 필요한 acquisition을 private staging에 준비한다.
8. 성공할 때만 move·borrow·binding을 한 번 commit한다.
9. final binder와 body를 노출한다.
10. owner별 exit, join과 cleanup을 수행한다.

commit 전 실패의 관찰값은 다음과 같다.

```text
final_bind_count = 0
move_commit_count = 0
exclusive_borrow_commit_count = 0
assignment_write_count = 0
authority_acquisition_count = 0
```

`pattern as whole`은 clone이 아니라 borrow alias다. moved 또는
exclusively borrowed descendant와 함께 살아야 하는 형식은 commit 전에
거부된다.

## 완전성과 narrowing

coverage engine은 Enum/Option/Result, closed Union, Tuple product, List
length와 rest, exact/open Record row, exact/open Map key set, bounded scalar
interval과 transparent nominal product를 구분한다.

- Or Pattern은 cell union이다.
- guard는 usefulness에는 참여하지만 unconditional coverage를 만들지
  않는다.
- exact `${x}`와 open `${x, _**}`는 서로 다른 row cell이다.
- opaque Preview Pattern View는 completeness를 만들지 않는다.
- `def#guard`의 검증된 `GuardSummaryV1`은 stable actual의 branch-local
  flow fact만 추가하며 Pattern coverage를 늘리지 않는다.

typed child binder는 일반 runtime subtype/refinement search가 아니다.
closed Union의 exact alternative identity를 읽거나 정적으로 증명된
refinement boundary를 적용할 뿐이다. runtime predicate가 필요하면
Pattern guard 또는 정확히 선택된 `def#guard`를 사용한다.

## Preview 표면

다음은 보존되는 nonactivatable Preview 설계이며 Stable과 섞지 않는다.
별도 activation authority와 실행 증거 전에는 source route를 만들지
않는다.

- And/Not Pattern
- removed Option-only `if let?`/`while let?` sugar; conditional tests use an explicit `Option::some` Pattern
- Set과 NumericArray Pattern
- Pattern Synonym과 direct pure Pattern View
- completeness manifest
- 명시적 search/find Pattern
- top-level destructuring
- member/index Pattern assignment
- Float range Pattern
- clone binder acquisition

Not Pattern은 binder를 만들 수 없다. And Pattern은 같은 subject를
검사하되 binder type·mode·region과 ownership이 충돌하면 거부한다.
Pattern View는 direct static identity, pure, nonthrowing, nonsuspending,
nonauthority, deterministic이어야 하며 completeness manifest 없이는
coverage cell을 만들지 않는다.

effectful/dynamic extractor, arbitrary getter, unbounded backtracking,
shared/actor multi-place assignment와 probe 중 suspension에는 Stable source
경로가 없다.

## 예제

### exact/open Record와 Map

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let ${x, y} = exactPoint
let ${x, y, _**} = extensiblePoint
let ${x: horizontal, y: vertical, rest**} = extensiblePoint

if let #map{id: "id", .._} = payload {
    consume(id)
}
```

### Sequence rest와 실패 경로

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
if let [head, tail..] = values {
    consume(head, tail)
}

if let [leadings.., last] = values {
    consume(last)
}

if let [first, middle.., last] = values {
    consume(first, middle, last)
}
```

### pin, range와 Enum

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
let expected = 200
let description = @match response {
    ::ok${status: code, body, _**} if code == expected => body
    ::ok${status: code, _**} if code >= 200 and then code < 300 => "ok"
    ::error${message, _**} => message
}
```

pin 자체는 Pattern 위치에서 쓴다. 일반 Bool 표현식에서는 ordinary
stable-place comparison을 사용한다.

## 거부 경계

| 형식 또는 주장 | 판정 |
|---|---|
| 제거된 `[head, ..tail]`, `[first, ..middle.., last]`, `[.._]` | 거부; suffix `tail..`, `middle..`, `_..` 사용 |
| Pattern 안의 rest 둘 이상 | 거부 |
| `${x, y}`를 subset으로 해석 | 거부; subset 의도는 `${x, y, _**}` |
| Record-family destination을 colon 왼쪽에 두기 | 거부; source label이 왼쪽 |
| arbitrary Map key call | 거부 |
| mutable/unstable pin | 거부 |
| ordinary Class 내부 자동 개방 | 거부 |
| refutable parameter Pattern | 거부 |
| guard의 effect, throw, suspend, consume, authority 획득 | 거부 |
| `if let?`, `while let?`, `var?`, bare `let?` without `else` | 제거됨/거부; exact consuming local `let? ... else ... => exit`만 current |
| Or branch마다 다른 binder/type/mode/region | 거부 |
| 실패 뒤 부분 move·binding·assignment | 금지 |
| generic Sequence conformance로 bracket/rest Pattern 활성화 | 거부 |

## 정본 근거

- [`spec/grammar/deeplus.dpg`](../../spec/grammar/deeplus.dpg)
- [`spec/patterns/pattern-context-policies.json`](../../spec/patterns/pattern-context-policies.json)
- [`spec/patterns/pattern-kinds.json`](../../spec/patterns/pattern-kinds.json)
- [`spec/patterns/pattern-lowering.json`](../../spec/patterns/pattern-lowering.json)
- [`spec/contracts/type-refinement-narrowing-coherence.json`](../../spec/contracts/type-refinement-narrowing-coherence.json)
- [`spec/language.md`](../../spec/language.md)
- [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
