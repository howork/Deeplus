<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# Prelude, provider, 진단 및 적합성 확인서

<!-- deeplus-status-fence: CURRENT -->

## 1. 이 장이 다루는 경계

언어 문법만으로는
`Option`, `Result`, `Task`, `AsyncSequence`,
`SharedCell`, `Pattern` 같은
language-facing identity의 전체 계약을 설명할 수 없다.

반대로 Prelude나 공식 도구가 존재한다는 사실만으로
새 keyword, 새 operator, 새 MIR instruction,
새 authority가 생기지도 않는다.

이 장은 다음 네 층을 분리한다.

1. **Prelude identity와 signature**
   - 소스 프로그램이 참조하는 canonical type, protocol, function
2. **stdlib/provider profile**
   - core syntax가 아닌 명시적 API와 정책
3. **official tooling**
   - source나 MIR을 분석·생성하지만 언어 의미를 바꾸지 않는 도구
4. **diagnostic/conformance receipt**
   - 설계 정적 row와 실제 제품 실행 증거를 구별하는 기록

특히 다음 항목을 상세히 설명한다.

- Prelude lookup과 signature authority
- `AsyncSequence`, `AsyncCollector`, `CollectPolicy::sequential`
- explicit pattern-engine library
- xVM agent framework
- tail-call analysis tooling
- UML state-machine provider
- provider derive-via
- R2 proof tooling
- checker predicate와 diagnostic dispatch
- API·backend·independent conformance receipt
- 모든 제품 lane의 `NOT_RUN` 경계

정확한 권위는
[`library/prelude/prelude.md`](../../library/prelude/prelude.md),
[`library/prelude/signatures`](../../library/prelude/signatures),
[`spec/contracts/tooling-and-profiles.json`](../../spec/contracts/tooling-and-profiles.json),
[`spec/contracts/provider-derive-via.json`](../../spec/contracts/provider-derive-via.json),
[`spec/contracts/proof-r2-tooling.json`](../../spec/contracts/proof-r2-tooling.json),
[`spec/types/predicates`](../../spec/types/predicates),
[`spec/diagnostics`](../../spec/diagnostics),
[`current/product-lanes.json`](../../current/product-lanes.json)에 있다.

## 2. Prelude는 무엇인가

### 2.1 language-facing identity

Prelude는
프로그램이 별도 구현 세부를 알지 않고 참조해야 하는
canonical language-facing identity를 공급한다.

대표 영역은 다음과 같다.

- `Bool`, `Char`, `String`, `Bytes`
- integer와 floating identity
- `Option<T>`, `Result<T, error E>`
- `List<T>`, `Set<T>`, `Map<K,V>`
- `MutableList<T>`, `ReadonlyView<T>`
- `Box<T>`, `OwnedDowncast<Target,Source>`
- `Task<T>`, `Actor`, `ActorMessageError`
- `AsyncSequence<T,E>`, `AsyncCollector`, `CollectPolicy`
- `ArithmeticDefect`, `IndexError`
- checker-known protocol과 function signature descriptor
- unit catalog, construction/evidence facade

이 identity 중 일부는 core semantic type이고,
일부는 protocol,
일부는 stdlib profile,
일부는 checker descriptor다.
같은 Prelude catalog에 있다는 이유로
모두 같은 runtime representation을 갖지 않는다.

### 2.2 keyword가 아니다

Prelude name은
scanner hard keyword를 자동 추가하지 않는다.
문법이 별도 keyword로 소유하는 이름과
Prelude scope에서 해석되는 identifier를 구분해야 한다.

예를 들어 `Task`가 canonical type이라고 해서
`Task` token 전용 scanner mode가 생기지 않는다.
`Pattern` library가 있다고 해서
regex literal token이 생기지 않는다.

### 2.3 signature catalog

machine-readable signature authority는
`library/prelude/signatures`다.
각 row는 일반적으로 다음 정보를 갖는다.

- entry identity
- source-facing symbol
- kind
- design/profile status
- feature reference
- normalized signature record
- responsibility
- notes
- product support
- baseline과 schema version
- normalized contract digest

`library/prelude/prelude.md`의 사람용 표는
catalog를 탐색하기 위한 projection이다.
정확한 generic channel, label,
return, throws, responsibility는
signature row를 확인해야 한다.

### 2.4 prelude intrinsic dialect

일부 signature record는
`prelude_intrinsic` dialect이고
`grammar_root`가 없다.

이는 signature 계약을 표현하기 위한
machine dialect이지,
같은 문자열을 ordinary Deeplus source file에 넣으면
항상 exact grammar로 parse된다는 뜻이 아니다.

특히 async callable descriptor 같은 표기가
Prelude contract에 나타나도
일반 async callable literal source syntax를
암시적으로 활성화하지 않는다.

## 3. Prelude lookup

### 3.1 정적 공급

resolver는 canonical Prelude environment를
정적 name graph의 한 입력으로 사용한다.
lookup 결과는 HIR identity로 고정된다.
runtime registry나 provider가
동일한 문자열의 Prelude identity를 바꾸지 못한다.

Prelude lookup은 다음과 별도다.

- lexical local lookup
- current module declaration lookup
- imported declaration lookup
- nominal member lookup
- extension set lookup
- Trait witness lookup
- dynamic provider invocation

### 3.2 identity와 spelling

같은 소스 spelling이 보인다는 사실만으로
canonical Prelude identity와 같아지지 않는다.
API digest와 checker descriptor는
선택된 declaration identity를 기록한다.

도구가 pretty-print한 이름도
identity를 대체하지 않는다.
이름 충돌이 있으면
정본의 qualification과 visibility 규칙으로 해소해야 한다.

### 3.3 operator는 Prelude overload가 아니다

current operator glyph vocabulary는 닫혀 있고
모든 glyph dispatch는 `INTRINSIC_ONLY`다.

Prelude의 `Bitwise`, `Ord<T>` 같은 이름은
named contract vocabulary다.
conformance, extension, witness, provider가
`+`, `^`, `[]`의 새 glyph candidate를
추가하거나 바꾸지 못한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: library/prelude/prelude.md -->
```deeplus
private def combine(left: Custom, right: Custom) -> Custom = {
    return left ~ combineWith(right)
}
```

사용자-defined behavior는
named method 또는 named API를 사용한다.
같은 behavior를 `left + right`의 hidden Trait hook으로
등록하지 않는다.

### 3.4 conformance가 bracket을 활성화하지 않는다

`Sequence`, `Indexable`,
`LogicalIndexDomain`은
checker/library descriptor이자 named behavior contract다.

사용자 type이 그 protocol을 만족해도
current closed built-in bracket carrier matrix에
자동으로 들어가지 않는다.
`[]` lowering은 current built-in owner만 가진다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: library/prelude/prelude.md -->
```deeplus
private let item = customSequence[1]
// Sequence conformance만으로 bracket syntax가 활성화되지 않는다.
```

사용자 type은
정본이 허용한 named selector를 제공해야 한다.

## 4. Option, Result 및 failure identity

### 4.1 Option

Option은 absence를 값으로 표현한다.
`::some`과 `::none` alternative가 명시적이다.
recovery spelling `null`은
Option 값을 만들지 않는다.

`?:`는 lazy fallback을 가진
Option-specific intrinsic이다.

### 4.2 Result

Result use-site는
`Result<T, error E>`처럼
error 역할을 명시한다.
generic declaration에서 `E: ErrorSet`을 결합할 때는
역할 표지를 반복하지 않는다.

Result 안의 error alternative와
callable `throws E`는 다른 channel이다.
같은 recoverable family를 둘에 중복 노출하면 안 된다.

### 4.3 intrinsic failure

`ArithmeticDefect`는
checked integer overflow와 division/remainder by zero의
nonrecoverable intrinsic family다.
ErrorSet member가 아니다.

`IndexError`는 recoverable family이며
`outOfLogicalDomain`, `keyNotFound`를 갖는다.

Cancellation은 둘 중 어느 family에도 들어가지 않는다.
Prelude identity가 있다고 해서
control outcome 분리가 사라지지 않는다.

## 5. collection과 owner-facing Prelude

### 5.1 immutable collection

`List<T>`, `Set<T>`, `Map<K,V>`는
서로 다른 identity다.

- List는 ordered sequence
- Set은 immutable unique-element collection
- Map은 exact runtime key lookup

Record는 static label product이며
Map과 같지 않다.
Map key는 member name이나 named argument label이 아니다.

### 5.2 MutableList, snapshot, freeze

`MutableList<T>`는
`List<T>`의 subtype이 아닌
exclusive mutable owner다.

`ListSnapshot<T>`은
독립된 point-in-time value이며
copy 또는 copy-on-write cost가 공개 계약에 남아야 한다.

`FrozenList<T>`은
exclusive freeze transition의 immutable result다.
freeze와 snapshot은 같은 operation이 아니다.
cross-isolation shareability에는
payload capability proof가 별도로 필요하다.

### 5.3 ReadonlyView

`ReadonlyView<T>`은
source coordinate와 provenance를 보존하는
nonowning view다.

Prelude operation은
hidden rebase, hidden copy,
mutable access, owner lifetime extension,
isolation crossing을 만들지 않는다.

독립 value나 새 coordinate domain이 필요하면
명시적 named operation을 사용하고
allocation/ownership observation을 보존해야 한다.

## 6. AsyncSequence

### 6.1 identity

current async source profile은
`AsyncSequence<T, E: ErrorSet>`다.

`T`는 element type이고
`E`는 source terminal failure set이다.
error type을 자유 terminal channel로 남기지 않는다.

source는 single-consumer이고
하나의 source-ordered async `next` channel을 가진다.
terminal outcome은 다음 중 하나다.

- end
- error `E`
- Cancellation

Cancellation은 `E`에 들어가지 않는다.

### 6.2 intrinsic signature 의미

Prelude catalog는 개념적으로 다음 책임을 기록한다.

- associated `Item = T`
- associated `Failure = E`
- async `next`가 `Option<T>`를 만들고 `throws E`
- terminal cancellation 분리

이 record는 `prelude_intrinsic` dialect다.
ordinary source에 async callable literal을 추가하지 않는다.

### 6.3 for await

`for await`는
AsyncSequence 순회를 위한 current statement owner다.
source의 `E`는 enclosing callable의 error context에서
처리 또는 전파되어야 한다.

loop cancellation은
source error로 접히지 않는다.
borrow, cleanup, isolation 책임은
suspension을 지나 보존된다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private def#async consume(
    source: AsyncSequence<Int, IOError>,
) -> Unit
    throws IOError
= {
    for await value in source {
        record(value)
    }
}
```

source failure는 `IOError`이고
Cancellation은 별도 control outcome이다.

## 7. AsyncCollector

### 7.1 세 identity

Stage-1 async collection profile은
core syntax를 추가하지 않고
다음 Prelude identity를 결합한다.

- `AsyncSequence<T,ES>`
- `AsyncCollector`
- `CollectPolicy::sequential`

`AsyncCollector::list`는
finite async source를
`List<U>`로 모으는 explicit stdlib service다.

### 7.2 signature responsibility

machine signature는 개념적으로 다음 parameter를 갖는다.

- source: `AsyncSequence<T,ES>`
- policy: `CollectPolicy`
- transform: named async callable from `T` to `U`, `throws ET`

result는 `List<U>`이고
callable failure는 정확히
`normalize(ES | ET)`다.

source error와 transform error를
지우거나 Cancellation로 바꿀 수 없다.
Cancellation도 error union에 넣지 않는다.

### 7.3 transform boundary

checker predicate는 transform이
named `def#async`라고 요구한다.
일반 async callable literal은
이 profile 때문에 활성화되지 않는다.

Prelude signature record의 `#async (T) -> U` 표기는
callable responsibility descriptor다.
ordinary source literal 문법을 승인하는 증거가 아니다.

### 7.4 finite evidence

collector는 source가 finite임을
checker evidence로 요구한다.

“언젠가 끝날 것 같다”는 runtime 기대,
timeout,
사용자가 적은 주석은 evidence가 아니다.
finite proof가 없으면
`ASYNC_COLLECTOR_POLICY_NOT_ADMITTED`로 거부한다.

### 7.5 exact policy

current policy는 정확히
`CollectPolicy::sequential` 하나다.
이 이름은 다음 묶음을 뜻한다.

1. source-order result
2. first failure에서 fail-fast
3. pending work cancellation
4. buffer capacity one
5. partial result commit 없음
6. return 전 cleanup 완료

이름의 “sequential”만 보고
각 항목을 생략하면 안 된다.
반대로 completion-order,
unbounded buffer,
partial success,
dynamic concurrency limit을
숨은 default로 추가하지 않는다.

### 7.6 성공 trace

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: library/prelude/prelude.md -->
```deeplus
private def#async loadProfileForCollect(
    userId: UserId,
) -> Profile
    throws NetworkError
= {
    return await loadProfile(userId)
}

private def#async collectProfiles(
    userIds: AsyncSequence<UserId, IOError>,
) -> List<Profile>
    throws IOError | NetworkError
= {
    return await AsyncCollector::list(
        source: userIds,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
```

이 예제의 static 전제는
`userIds`에 finite evidence가 있다는 것이다.
source `IOError`와 transform `NetworkError`가
정확한 union으로 노출된다.

개념적인 성공 과정은 다음과 같다.

1. source와 policy, named transform identity를 고정한다.
2. `ES = IOError`, `ET = NetworkError`를 정규화한다.
3. finite evidence를 확인한다.
4. policy가 exact current policy인지 확인한다.
5. source order로 element를 요청한다.
6. transform을 current bound에 따라 실행한다.
7. 완료 element를 source order slot에 둔다.
8. terminal end를 확인한다.
9. pending cleanup을 끝낸다.
10. 완성된 List 하나를 commit한다.

### 7.7 source failure

source가 실패하면
transform error로 바꾸지 않는다.
첫 failure를 보존하고
pending work를 취소하며
cleanup barrier를 지난다.
partial List를 반환하지 않는다.

### 7.8 transform failure

transform이 `ET`로 실패하면
source failure로 바꾸지 않는다.
정확한 `ES | ET` callable error set 안에서
원래 failure identity를 보존한다.

### 7.9 Cancellation

Cancellation은
pending work cancellation과 cleanup을 거쳐
terminal cancellation로 남는다.
`ES | ET`의 case로 변환되지 않는다.

### 7.10 finite evidence가 없는 경계

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/predicates/chunks/part-0001.json -->
```deeplus
private def#async invalidCollect(
    stream: AsyncSequence<UserId, IOError>,
) -> List<Profile>
    throws IOError | NetworkError
= {
    return await AsyncCollector::list(
        source: stream,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
// stream의 finiteness를 checker가 증명하지 못하면 admission이 실패한다.
```

runtime에서 몇 개만 읽어 본다는 추측으로
finite requirement를 우회하지 않는다.

### 7.11 error union 누락

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/predicates/chunks/part-0001.json -->
```deeplus
private def#async invalidErrors(
    userIds: AsyncSequence<UserId, IOError>,
) -> List<Profile>
    throws NetworkError
= {
    return await AsyncCollector::list(
        source: userIds,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
// source IOError를 지울 수 없다.
```

## 8. pattern-engine library profile

### 8.1 syntax가 아니다

Deeplus에는 regex literal token이나
scanner mode가 없다.
pattern compilation은
String 또는 Bytes를 받는
ordinary library call이다.

따라서 `/.../`, `r/.../` 같은
익숙한 타 언어 spelling을
parser가 추측해서 Pattern constant로 만들지 않는다.

### 8.2 input identity

pattern compilation input은 다음을 명시한다.

- pattern text 또는 bytes
- engine identity
- engine version
- flags
- Unicode mode
- resource budget

cache key는
engine, version, flags,
input digest를 포함한다.

### 8.3 output과 failure

compile 결과는
`Result<Pattern, error PatternCompileError>`다.

compile failure와 no-match는 다르다.

- invalid syntax, unknown engine,
  invalid flags, budget exceeded는 compile failure
- 성공적으로 compile된 Pattern이
  input을 찾지 못하는 것은 ordinary no-match result

두 결과를 같은 Bool false로 합치면
진단과 failure 책임이 사라진다.

### 8.4 explicit example

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/tooling-and-profiles.json -->
```deeplus
private let compiled = Pattern::compile(
    raw"[A-Z]+",
    engine: PatternEngine::default,
    budget: PatternBudget::standard,
)
```

raw String은 escape/interpolation을 실행하지 않는다.
engine과 budget은 명시적 argument다.

### 8.5 budget

budget은 implementation hint가 아니라
resource policy identity다.
budget exceeded를 no-match로 바꾸지 않는다.

engine cache가 있어도
다른 version이나 flags의 결과를 재사용하면 안 된다.
provider/engine choice는 runtime hidden lookup이 아니다.

### 8.6 product 경계

profile contract는 design static이다.
실제 engine binary,
cache implementation,
Unicode conformance,
resource enforcement receipt는
`NOT_RUN`이다.

## 9. xVM agent framework

### 9.1 목적

xVM agent는
MIR 또는 xVM bytecode를
bounded 환경에서 분석·실행하고
재현 가능한 side receipt를 내는 official tooling이다.

agent가 존재해도
source syntax나 program semantics가 바뀌지 않는다.

### 9.2 required input

contract input은 다음을 포함한다.

- Deeplus MIR digest 또는 xVM bytecode digest
- declared host capabilities
- deterministic execution budget

agent는 digest가 가리키는 artifact를
임의로 바꿀 수 없다.
declared host capability 밖의 authority를
획득할 수 없다.

### 9.3 output

output은 다음 receipt family다.

- ordered event receipt
- diagnostic receipt
- output digest

receipt는 input digest,
capability set,
budget과 결합되어야 한다.
이 결합이 없으면
어떤 artifact에 대한 결과인지 검증할 수 없다.

### 9.4 법칙

xVM agent는 다음을 할 수 없다.

- MIR 위조
- bytecode 위조
- authority 위조
- agent availability에 따라 language semantics 변경
- target receipt 없이 product execution PASS 주장

### 9.5 성공 scenario

성공한 bounded run은
input digest와 capability digest를 기록하고
ordered events와 output digest를 낸다.

agent가 없어도
원래 프로그램의 의미는 같다.
달라지는 것은 side evidence의 존재뿐이다.

### 9.6 실패 scenario

다음은 deterministic refusal 또는 diagnostic 대상이다.

- undeclared host capability 요청
- input digest mismatch
- budget mismatch
- receipt event order mismatch

도구가 편의를 위해 capability를 자동 추가하면
authority contract를 위반한다.

## 10. tail-call analysis tooling

### 10.1 source profile이 아니다

Deeplus에는
`#tailrec` callable kind가 없다.
recursive function은 ordinary call semantics를 가진다.

tail-call analyzer는
optimization eligibility를 설명하는
official tooling이다.
optimization이 없다고 program error가 되지 않는다.

### 10.2 input

analyzer는 다음을 읽는다.

- Deeplus MIR control-flow graph
- pending cleanup
- effect boundary
- suspension boundary
- actor boundary

source spelling만 보고
tail position을 선언하지 않는다.

### 10.3 output

output은 다음 중 하나다.

- tail-position classification
- backend-specific optimization receipt
- explicit refusal reason

self recursion과 mutual recursion은
구별되어야 한다.

### 10.4 eligible scenario

callee return 뒤
관찰할 cleanup, conversion,
suspension, actor delivery가 없으면
tail-position 후보가 될 수 있다.

analyzer가 eligible이라고 해도
backend가 반드시 최적화해야 하는
source guarantee는 아니다.

### 10.5 refusal scenario

다음은 대표적인 refusal reason이다.

- pending cleanup
- suspension boundary
- actor delivery boundary

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/tooling-and-profiles.json -->
```deeplus
private def visit(node: Node) -> Int = {
    defer recordVisit(node)
    return visit(node.next)
}
```

recursive call이 문법상 마지막 expression처럼 보여도
pending `defer`가 있으므로
ordinary return/cleanup observation을 지워서는 안 된다.

### 10.6 backend parity

xVM, LLVM AOT, LLVM ORC는
optimization 적용 여부가 달라도
program observation이 같아야 한다.

stack depth를 source semantic promise로 만들지 않는다.
tail analyzer receipt는
backend conformance receipt를 대체하지 않는다.

## 11. UML state-machine provider

### 11.1 역할

UML state-machine provider는
typed state/transition metadata를 받아
ordinary Deeplus source 또는 test를 생성하는
official tooling이다.

runtime state machine authority나
새 source keyword를 추가하지 않는다.

### 11.2 input

input은 다음을 포함한다.

- typed state metadata
- typed transition metadata
- source symbol trace ID

state와 transition은
정적 identity를 가져야 한다.
diagram label 문자열만으로
declaration identity를 만들지 않는다.

### 11.3 output

output은 다음이다.

- ordinary generated Deeplus source 또는 tests
- content-addressed sidecar

generated source는
handwritten source와 같은
Rust scanner, parser, checker,
Deeplus MIR lowering을 다시 거친다.

### 11.4 금지

provider는 다음을 할 수 없다.

- runtime semantics injection
- MIR injection
- witness injection
- unchecked actor authority 생성
- source trace 없는 declaration 생성

### 11.5 positive scenario

finite traced state graph가
ordinary actor 또는 typestate-shaped source와
tests를 생성할 수 있다.

단, current typestate source semantics가
미폐쇄인 부분을 provider가 몰래 채울 수 없다.
generated source도 같은 current checker boundary를 따른다.

### 11.6 negative scenario

다음은 거부되어야 한다.

- dangling transition endpoint
- duplicate state identity
- source trace가 없는 generated declaration

provider가 임의 default state를 골라
결손 graph를 통과시키면 안 된다.

## 12. provider derive-via

### 12.1 목적

derive-via contract는
typed source information을
검토 가능한 ordinary source로 변환하는
provider pipeline을 고정한다.

trusted compiler plugin이나
MIR macro가 아니다.

### 12.2 input

required input은 다음이다.

- `typed_ast`
- `rcts_v5`
- `provider_id`
- `provider_version`
- `input_sha256`

provider identity와 version이 없으면
같은 input에서 나온 output을
재현·검증할 수 없다.

### 12.3 output

output은 다음이다.

- `ordinary_deeplus_source`
- `sidecar_sha256`
- `provider_id`
- `provider_version`

sidecar는 source를 대신 실행하는 authority가 아니다.
source와 provider provenance를 결합하는 증거다.

### 12.4 mandatory pipeline

generated output은 반드시 다음 단계를 지난다.

1. deterministic generation
2. Rust scanner
3. Rust parser
4. Rust checker
5. Deeplus MIR lowering

한 단계라도 건너뛰면
ordinary source와 같은 검증 경계를 갖지 않는다.

### 12.5 forbidden path

derive-via는 다음을 금지한다.

- witness injection
- authority injection
- MIR injection
- LLVM IR injection
- recheck bypass

provider가 “이미 타입을 안다”는 이유로
checker를 건너뛸 수 없다.

### 12.6 generated source example

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/provider-derive-via.json -->
```deeplus
private def generatedProjection(value: SourceRecord) -> TargetRecord = {
    return TargetRecord${
        id: value.id,
        name: value.name,
    }
}
```

이 source가 provider에서 나왔더라도
ordinary materialization과 visibility,
ownership, effect/error, cleanup 검사를 모두 받는다.
comment나 sidecar가 type error를 면제하지 않는다.

## 13. R2 proof tooling

### 13.1 공식 도구 경계

R2 solver는
복잡한 obligation을 검증하거나
R0/R1로 줄여 검사하는 official tooling이다.
source semantics variance는 없다.

### 13.2 input

required input은 다음이다.

- normalized obligation
- obligation SHA-256
- provider ID
- provider version

normalization과 digest가 결합되어야
certificate가 어떤 obligation을 증명하는지 알 수 있다.

### 13.3 output

required output은 다음이다.

- result
- certificate SHA-256
- original obligation SHA-256
- provider ID
- provider version

success result는
`verified_certificate` 또는
`reduced_to_r0_r1_and_checked`다.

### 13.4 non-success

다음은 proof가 아니다.

- timeout
- unknown
- provider error

unknown을 false나 true로 바꾸지 않는다.
timeout을 성공으로 cache하지 않는다.

### 13.5 API/MIR 금지 residue

다음은 public API 또는 MIR에 남지 않는다.

- solver search trace
- nondeterministic search order
- unverified certificate

certificate는 admitted proof를 뒷받침할 수 있지만
runtime authority나 first-class value를 만들지 않는다.

## 14. provider와 runtime의 분리

### 14.1 compile-time provider

derive-via, UML, proof tooling은
ordinary checking 전 또는 중간의
정적 pipeline에 속한다.

output은 source, test, certificate,
sidecar, diagnostic receipt다.
program runtime event를 직접 삽입하지 않는다.

### 14.2 dynamic provider

정본이 별도로 허용한 dynamic unit conversion 같은 경우에만
MIR provider event가 존재한다.

그 event는 다음을 기록한다.

- provider identity와 version
- observation timestamp
- rounding policy
- failure/effect policy
- cache key
- replay token

source Preview gate가
이 event를 자동 활성화하지 않는다.

### 14.3 hidden authority 금지

provider가 사용 가능하다는 사실은
program이 provider authority를 가진다는 뜻이 아니다.
operation의 context capability,
effect row,
error set을 별도로 검사한다.

provider fallback order나 registry iteration order를
overload winner 또는 conformance evidence로 사용하지 않는다.

## 15. checker predicate

### 15.1 predicate row

checker predicate catalog의 row는
대체로 다음 정보를 갖는다.

- predicate ID
- formal judgment ID
- algorithm owner
- input descriptor와 schema
- descriptor axes
- preconditions
- normalization
- dependency predicates
- decision procedure
- termination metric
- success result
- primary/secondary diagnostics
- positive/negative fixture IDs
- evaluation order
- maturity
- emission eligibility
- execution receipt
- product support

row가 존재한다는 사실만으로
제품 checker가 그 algorithm을 실행했다는 뜻이 아니다.

### 15.2 design seed

`predicate_maturity: design_seed`는
후보 vocabulary와 필요한 descriptor를 기록하지만
닫힌 terminating algorithm이 아직 없음을 뜻한다.

보통 다음 경계를 갖는다.

- documentation-only validation
- diagnostic 후보 기록
- diagnostic emission 없음
- product execution receipt 없음
- discriminating fixtures와 독립 검토 뒤에만 승격

design seed diagnostic을
active product diagnostic처럼 내면 안 된다.

### 15.3 design algorithm

`design_algorithm`은
precondition, normalization,
ordered dependency, local rule,
diagnostic dispatch가 닫힌 설계다.

그러나 `evidence_status`가
`DESIGN_STATIC_NOT_RUN`이고
`execution_receipt`가 null이면
제품 실행 PASS는 아니다.

AsyncCollector predicate가 그 예다.
알고리즘과 active primary diagnostic은 닫혀 있지만
product checker support는 `NOT_RUN`이다.

### 15.4 descriptor

RCTS-V5 input descriptor는
닫힌 discriminated data다.
normalization은 alias, ownership region,
label, evidence identity,
effect/error/cancellation을 보존해야 한다.

필드가 없다고 숨은 default를 만들거나
unknown variant를 가장 가까운 variant로 고치지 않는다.

### 15.5 dependency order

dependency predicate는
목록 순서대로 평가하고
선택된 diagnostic을 전파한다.

local rule가 실패했더라도
앞선 dependency failure를 덮어쓰지 않는다.
termination은 finite descriptor와
strictly decreasing dependency DAG rank로 설명된다.

## 16. diagnostic dispatch

### 16.1 primary diagnostic

한 판정 실패는
정본이 지정한 active primary diagnostic 하나를 선택한다.
secondary diagnostic 목록은
가능한 trace/설명 vocabulary이지
모두 동시에 emit하는 batch list가 아니다.

### 16.2 first failed condition

ordered condition algorithm은
첫 실패 조건을 primary로 고정한다.
source order와 registry order가
진단 winner를 바꾸지 않는다.

AsyncCollector에서는
다음 조건이 순서 있는 admission을 이룬다.

1. closed descriptor
2. normalization
3. dependency
4. finite source
5. named async transform
6. exact error union
7. cancellation 분리
8. exact policy

실패는
`ASYNC_COLLECTOR_POLICY_NOT_ADMITTED`로 귀결된다.

### 16.3 parse와 checker diagnostic

parser는 token owner와 structural form을 진단한다.
checker는 type, ownership,
effect/error, evidence, policy를 진단한다.

checker가 필요하다는 이유로
parser가 type information을 사용해
다른 AST로 repair하면 안 된다.

### 16.4 recovery

Recovery node는 offending spelling과
diagnostic span을 보존할 수 있다.
그러나 HIR/MIR value를 만들지 않는다.

formatter는 recovery spelling을
Stable accepted source처럼 정규화해서는 안 된다.

## 17. fixture와 example evidence

### 17.1 positive fixture

positive fixture는
설계 algorithm의 허용 branch를 구별한다.
input descriptor와 expected success contract가
content-addressed여야 한다.

### 17.2 negative fixture

negative fixture는
다른 condition을 통과하면서
목표 condition만 실패하도록 설계해야 한다.

모든 오류를 한 fixture에 섞으면
diagnostic order를 검증할 수 없다.

### 17.3 boundary fixture

boundary fixture는
최솟값, 최댓값,
empty/nonempty,
precommit/postcommit,
exact kind/near-miss kind를 구별한다.

### 17.4 example corpus

review corpus의 accepted/rejected example은
design static evidence다.
parser/checker status가 `not_run`이면
실제로 compile되었다는 뜻이 아니다.

문서 예제도 마찬가지다.
source semantics를 설명하지만
artifact-bound receipt가 아니다.

## 18. conformance identity

### 18.1 nominal evidence

Trait conformance는
nominal record와 `WitnessId`를 갖는다.
extension presence,
structural method similarity,
runtime provider lookup이
conformance를 합성하지 않는다.

### 18.2 locality

declaring package는
target nominal type 또는 Trait 중
적어도 한쪽을 소유해야 한다.

third package가
foreign target을 foreign Trait에 conform시키는
orphan conformance를 만들 수 없다.

module placement도
visibility와 package ownership을 만족해야 한다.

### 18.3 associated binding

associated requirement는
정확히 하나의 compatible binding을 가져야 한다.

다음은 MIR 전에 거부된다.

- missing
- duplicate
- ambiguous
- incompatible
- cyclic binding

same-name nested item이
associated binding을 자동 합성하지 않는다.

### 18.4 parent evidence

supertrait parent는
canonical parent record를 재사용한다.
diamond path가
서로 다른 shadow parent record를 만들지 않는다.

parent/refinement evidence graph는 acyclic이어야 한다.

### 18.5 explicit witness channel

call site의 `using` channel은
이미 선택 가능한 conformance evidence를
명시적으로 전달한다.
witness는 borrowed, nonescaping이며
runtime value가 아니다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def same<T>(
    left: T,
    right: T,
    using equality: witness Equality<T>,
) -> Bool = {
    return equals(left, right, using equality)
}
```

actual Trait와 helper API는
program의 canonical conformance graph에 있어야 한다.
예제의 핵심은 evidence channel이다.

## 19. conformance selection

### 19.1 tier

정본의 conformance selection은
explicit, ordinary,
별도 승인된 default tier를 구분한다.

explicit set이 nonempty이면
그 tier가 committed된다.
정확히 하나의 compatible member가 있어야 한다.

explicit tier에서 ambiguity나 incompatibility가 나면
ordinary/default로 fallback하지 않는다.

### 19.2 ordinary

explicit witness가 없으면
visible compatible ordinary witness가
정확히 하나인지 검사한다.

- 하나면 선택
- 둘 이상이면 ambiguity
- 0이면 별도 승인된 default tier만 고려

declaration, import, provider order는 rank가 아니다.

### 19.3 default

default set은
별도 marker/default mapping이 승인될 때만 존재한다.
정본이 비어 있다고 한 default를
implementation convenience로 채우지 않는다.

### 19.4 HIR/MIR residue

선택된 conformance record,
requirement, associated binding,
parent link identity는
HIR/MIR 또는 lossless equivalent에 남는다.

lowering은 source/provider/default/fallback search를
다시 하지 않는다.

## 20. API conformance receipt

### 20.1 ModuleSignature

Prelude의 `ModuleSignature` identity는
public API boundary surface다.
separate compilation이 성공했다는 receipt 자체는 아니다.

API summary는 다음을 보존해야 한다.

- normalized declaration identity
- visibility
- generic binders와 constraints
- parameter channel과 labels
- ownership
- effects/errors/cancellation
- witness/conformance residue
- associated bindings
- relevant feature identity
- content digest

### 20.2 link verification

whole-image verifier는
다음을 object/package/import order와 독립적으로 검사한다.

- duplicate
- overlap
- locality
- visibility
- parent interning
- digest compatibility

link check가 없으면
독립 compile unit의 static row만으로
whole program conformance를 주장할 수 없다.

### 20.3 receipt binding

유효한 API receipt는 적어도 다음과 결합되어야 한다.

- baseline
- schema version
- compiler/tool version
- input manifest digest
- module signature digest
- target/profile
- command
- output digest
- pass/fail과 diagnostic

“검사했다”는 자유 텍스트는
재현 가능한 receipt가 아니다.

## 21. tooling receipt

### 21.1 공통 필드

official tooling receipt에는
대상에 따라 다음이 필요하다.

- tool ID와 version
- input artifact digest
- normalized option/policy digest
- capability set
- budget
- target
- ordered event 또는 diagnostic
- output digest
- timestamp/replay 정보가 의미상 필요한 경우 그 identity

### 21.2 side receipt

xVM agent와 tail analyzer output은
side receipt다.
program return value나 ErrorSet에
자동 삽입되지 않는다.

side receipt를 제거해도
program semantics가 같아야 한다.

### 21.3 generation receipt

UML과 derive-via output은
generated source digest와 sidecar를 갖는다.
그 뒤 ordinary frontend receipt가 별도로 필요하다.

generation PASS가
scanner/checker/MIR PASS를 의미하지 않는다.

### 21.4 proof receipt

R2 certificate는
obligation digest와 provider identity를 보존한다.
unverified output은 API/MIR에 들어가지 않는다.

proof PASS가
runtime backend PASS를 의미하지 않는다.

## 22. product lane registry

현재 product lane은 15개이며
모두 `NOT_RUN`, receipt는 null이다.

1. Rust lexer
2. Rust parser
3. Rust CST/AST→HIR normalization
4. Rust integrated checker
5. Deeplus MIR lowering
6. xVM bytecode emitter
7. xVM interpreter
8. LLVM AOT backend
9. LLVM ORC JIT backend
10. formatter/LSP
11. stdlib/provider runner
12. official proof/derive/UML tooling
13. independent conformance lab
14. cross-backend conformance
15. actual user/team usability study

한 lane의 미래 PASS는
다른 lane을 자동 PASS로 만들지 않는다.

예를 들어 parser receipt가 있어도
checker, MIR, runtime은 여전히 `NOT_RUN`일 수 있다.
official tooling이 source를 생성해도
provider runner와 frontend receipt가 각각 필요하다.

## 23. receipt의 상태 전이

### 23.1 design static

설계 문서,
machine-readable contract,
schema validation,
fixture manifest가 있는 상태다.

이 단계는
규칙의 일관성과 추적 가능성을 제공하지만
제품 binary 실행을 입증하지 않는다.

### 23.2 target-bound execution

실제 toolchain과 target,
command, input artifact,
output을 digest로 결합한 run이다.

PASS는 해당 lane과
해당 target/profile 범위에만 적용된다.

### 23.3 independent conformance

독립 환경이
동일 manifest와 expected observation을 사용해
결과를 재현해야 한다.

원 개발 환경의 receipt를 복사하는 것은
독립 execution이 아니다.

### 23.4 cross-backend

xVM, AOT, ORC의
ordered observable parity를 비교한다.

각 backend가 개별적으로 종료했다는 사실만으로
parity가 되지 않는다.

### 23.5 user study

실제 사용자·팀 study는
언어 semantic correctness와 다른 lane이다.
study가 없다는 사실이 semantics를 바꾸지는 않지만,
사용성 claim을 할 수 없다.

## 24. 진단 receipt

### 24.1 포함할 정보

diagnostic receipt는 다음을 결합해야 한다.

- source/input digest
- source role
- activated profile
- parser/checker version
- predicate ID
- primary diagnostic ID
- relevant span
- ordered notes
- recovery node disposition
- output artifact count

### 24.2 nonemitting seed

design seed predicate는
emission eligibility가 false다.
candidate diagnostic vocabulary가 있어도
product diagnostic receipt를 만들지 않는다.

### 24.3 active diagnostic

design algorithm row가
emission eligible이고
active primary를 정의해도
실제 receipt가 null이면
product emission은 검증되지 않았다.

### 24.4 no MIR residue

static rejection receipt는
MIR artifact count가 0임을 확인해야 한다.
recovery AST를 Stable HIR로 낮추지 않았다는
증거가 필요하다.

## 25. 예제: pattern compile과 진단

### 25.1 compile success

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: library/prelude/prelude.md -->
```deeplus
private let patternResult = Pattern::compile(
    raw"[a-z]+",
    engine: PatternEngine::default,
    budget: PatternBudget::standard,
)
```

design-level checker는
argument labels와 type,
Result error channel을 검사한다.
provider runner는
engine/version/flags/Unicode/budget identity를 기록해야 한다.

### 25.2 compile failure

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/tooling-and-profiles.json -->
```deeplus
private let invalidPattern = Pattern::compile(
    raw"[",
    engine: PatternEngine::default,
    budget: PatternBudget::standard,
)
```

invalid pattern은 compile failure다.
ordinary no-match로 바꾸지 않는다.

### 25.3 budget failure

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/tooling-and-profiles.json -->
```deeplus
private let boundedPattern = Pattern::compile(
    patternText,
    engine: selectedEngine,
    budget: tinyBudget,
)
```

budget exceeded는
PatternCompileError 경계를 따른다.
tooling이 더 큰 budget으로 몰래 retry하면
명시적 policy identity가 바뀐다.

## 26. 예제: generated source와 recheck

### 26.1 visibility failure

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/provider-derive-via.json -->
```deeplus
public def generatedPublic(value: PrivateModel) -> String = {
    return value ~ toString()
}
```

provider가 이 source를 생성했더라도
public API가 private type을 노출하면
visibility closure에서 거부된다.

### 26.2 ownership failure

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/provider-derive-via.json -->
```deeplus
private def generatedDuplicate(move resource: Resource) -> Pair = {
    return Pair!(resource, resource)
}
```

generated source는
use-after-move 또는 duplicate owner 검사를 면제받지 않는다.

### 26.3 witness injection 금지

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/provider-derive-via.json -->
```deeplus
private def generatedCompare(left: Model, right: Model) -> Bool = {
    return compareModels(left, right)
}
```

필요한 Trait evidence가 없다면
sidecar가 hidden witness를 주입해 통과시킬 수 없다.
source에 허용된 explicit evidence 경계를 사용해야 한다.

## 27. 예제: tooling이 의미를 바꾸지 않음

### 27.1 tail analysis 없음

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private def factorial(value: Int, acc: Int) -> Int = {
    if value == 0 {
        return acc
    }
    return factorial(value - 1, acc * value)
}
```

tail analyzer가 없거나 refusal을 내도
ordinary call semantics는 같다.

### 27.2 xVM agent 없음

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/tooling-and-profiles.json -->
```deeplus
private def compute(value: Int) -> Int = {
    return value * 2
}
```

agent가 receipt를 만들지 않아도
`compute`의 language result는 바뀌지 않는다.
단, 제품 execution claim은 receipt 없이 할 수 없다.

### 27.3 UML provider 없음

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/tooling-and-profiles.json -->
```deeplus
public enum ConnectionState {
    idle,
    connecting,
    connected,
}
```

handwritten source와 provider-generated source는
같은 frontend 검사를 받는다.
UML 도구의 부재가 Enum semantics를 바꾸지 않는다.

## 28. 상호작용

### 28.1 Prelude와 name resolution

Prelude identity는
정적 resolver input이다.
lexical/member/extension/witness domain과
섞이지 않는다.

선택 결과는 HIR/MIR에 고정되고
runtime provider가 바꾸지 않는다.

### 28.2 Prelude와 operator

Prelude protocol은
named behavior를 제공한다.
closed intrinsic glyph dispatch를
확장하지 않는다.

### 28.3 AsyncCollector와 async syntax

AsyncCollector는 stdlib profile이다.
`for await`와 named `def#async`를 사용할 수 있지만
일반 async callable literal이나
async comprehension syntax를 활성화하지 않는다.

### 28.4 provider와 effect

dynamic provider call은
provider identity뿐 아니라
EffectRow, ErrorSet, authority를 보존한다.

compile-time generator는
runtime effect를 삽입하지 않는다.

### 28.5 diagnostic과 formatter/LSP

formatter와 LSP는
active grammar/profile과 diagnostic registry를 따라야 한다.

Recovery-only spelling을
Stable source로 자동 고치거나
design-seed diagnostic을 product error로
표시해서는 안 된다.

### 28.6 conformance와 API

witness identity와 associated binding은
public signature residue에 남는다.
link verifier가
locality, visibility, digest를 검사해야 한다.

### 28.7 conformance와 MIR

MIR lowering은
selected witness identity를 받는다.
runtime iteration이나 registration order로
다시 선택하지 않는다.

## 29. 흔한 오해와 정확한 판정

| 오해 | 정확한 판정 |
|---|---|
| Prelude row가 있으면 keyword다 | 아니다. language-facing identity와 scanner keyword는 별도다 |
| Trait를 만들면 operator를 overload할 수 있다 | current glyph는 intrinsic-only다 |
| Sequence conformance가 `[]`를 준다 | built-in bracket matrix만 current다 |
| pattern engine은 regex literal이다 | explicit String/Bytes library call이다 |
| compile failure와 no-match는 같다 | 서로 다른 result다 |
| AsyncCollector가 async lambda를 활성화한다 | named `def#async` transform만 current profile이 요구한다 |
| `sequential`이면 buffer/cancel 규칙은 구현 자유다 | exact policy bundle에 포함된다 |
| finite는 runtime에서 끝나면 된다 | checker evidence가 필요하다 |
| provider가 witness를 생성할 수 있다 | derive-via는 witness injection을 금지한다 |
| generated source는 checker를 건너뛴다 | scanner→parser→checker→MIR을 다시 거친다 |
| tail-call eligible은 최적화 보장이다 | side tooling classification일 뿐이다 |
| xVM agent가 semantics를 추가한다 | side receipt만 만들며 authority를 위조할 수 없다 |
| predicate row가 있으면 제품 checker PASS다 | execution receipt와 lane PASS가 필요하다 |
| active diagnostic이면 실제 방출됐다 | product receipt가 null이면 검증되지 않았다 |
| fixture PASS가 backend PASS다 | design static과 target execution은 별도다 |
| 한 backend PASS면 cross-backend PASS다 | ordered differential receipt가 필요하다 |

## 30. 미폐쇄 경계

이 장의 일부 identity는 Stable design이지만
제품 또는 세부 의미가 미폐쇄다.

- 모든 Prelude row의 product support
- actual pattern engine runner
- xVM agent implementation
- tail-call analyzer implementation
- UML provider runner
- derive-via runner
- R2 proof provider
- generic design-seed predicate
- actor request arbitrary declared failure의 Task descriptor
- typestate provider가 기대할 executable typestate semantics

이 항목에 대해
문서가 취하는 태도는 다음과 같다.

1. 닫힌 input/output/law를 설명한다.
2. 미폐쇄 execution을 명시한다.
3. 익숙한 도구 behavior를 default로 발명하지 않는다.
4. receipt 없이 PASS를 주장하지 않는다.
5. provider가 language authority를 얻지 못하게 한다.

## 31. 제품 `NOT_RUN` 경계

현재 `current/product-lanes.json`의
15개 lane은 모두 `NOT_RUN`이며
receipt는 null이다.

따라서 이 장의 다음 문장은
설계 계약을 뜻한다.

- “AsyncCollector는 fail-fast다.”
- “xVM agent는 authority를 위조할 수 없다.”
- “tail analyzer는 pending cleanup을 본다.”
- “UML output은 recheck된다.”
- “derive-via는 MIR injection을 금지한다.”
- “predicate는 first failed condition을 고른다.”

다음 문장을 뜻하지 않는다.

- 실제 binary가 그 behavior를 수행했다.
- target에서 runtime trace가 수집됐다.
- formatter/LSP가 진단을 표시했다.
- provider가 재현 가능한 output을 만들었다.
- independent lab이 결과를 확인했다.

설계 정적 계약과
제품 실행 evidence를 정확히 분리해야 한다.

## 32. 검토 체크리스트

### 32.1 Prelude

1. symbol이 canonical signature row에 있는가.
2. kind와 status를 보존하는가.
3. signature dialect와 source grammar를 혼동하지 않는가.
4. generic channel과 label이 정확한가.
5. ownership/effect/error/cancellation 책임이 남는가.
6. product support를 과장하지 않는가.

### 32.2 AsyncCollector

1. source가 `AsyncSequence<T,ES>`인가.
2. `ES`가 ErrorSet에 bound되는가.
3. source finiteness evidence가 있는가.
4. transform이 named `def#async`인가.
5. `ET`가 ErrorSet에 bound되는가.
6. result throws가 exact `normalize(ES | ET)`인가.
7. Cancellation이 union 밖에 있는가.
8. policy가 exact `CollectPolicy::sequential`인가.
9. source order를 보존하는가.
10. fail-fast인가.
11. pending work를 취소하는가.
12. buffer bound가 1인가.
13. partial commit이 없는가.
14. return 전 cleanup이 끝나는가.
15. product receipt가 있는가.

### 32.3 pattern engine

1. input이 explicit String/Bytes인가.
2. engine과 version이 명시되는가.
3. flags와 Unicode mode가 identity에 있는가.
4. budget이 명시되는가.
5. cache key가 input digest를 포함하는가.
6. compile failure와 no-match를 분리하는가.
7. literal scanner mode를 추가하지 않는가.

### 32.4 official tooling

1. input artifact digest가 있는가.
2. tool/provider identity와 version이 있는가.
3. option/capability/budget이 정규화되는가.
4. output digest가 있는가.
5. side receipt가 program result를 바꾸지 않는가.
6. generated source가 recheck되는가.
7. witness/authority/MIR/LLVM injection이 없는가.
8. target receipt 없이 product PASS를 주장하지 않는가.

### 32.5 diagnostic

1. predicate maturity를 확인했는가.
2. emission eligibility가 true인가.
3. dependency order를 보존하는가.
4. first failed condition이 deterministic한가.
5. primary와 secondary를 구분하는가.
6. recovery node가 HIR/MIR로 가지 않는가.
7. fixture가 목표 branch를 분리하는가.
8. execution receipt가 있는가.

### 32.6 conformance

1. target 또는 Trait의 locality owner가 있는가.
2. visible compatible record가 정확히 하나인가.
3. explicit tier failure가 fallback하지 않는가.
4. provider/declaration order가 rank가 아닌가.
5. associated binding이 unique하고 acyclic인가.
6. parent record가 canonical하게 intern되는가.
7. witness identity가 API/MIR에 남는가.
8. whole-image link verification이 있는가.

## 33. 정본 근거

- [`library/prelude/prelude.md`](../../library/prelude/prelude.md)
  - Prelude 영역, async collector, pattern library boundary
- [`library/prelude/signatures`](../../library/prelude/signatures)
  - machine-readable signature, responsibility, digest
- [`spec/types/type-system.md`](../../spec/types/type-system.md)
  - Option/Result, collection, async, effects/errors
- [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
  - library/tooling observability와 backend boundary
- [`spec/contracts/tooling-and-profiles.json`](../../spec/contracts/tooling-and-profiles.json)
  - xVM agent, tail analyzer, pattern engine, UML
- [`spec/contracts/provider-derive-via.json`](../../spec/contracts/provider-derive-via.json)
  - generated source pipeline과 injection 금지
- [`spec/contracts/proof-r2-tooling.json`](../../spec/contracts/proof-r2-tooling.json)
  - obligation/certificate/provider contract
- [`spec/types/predicates`](../../spec/types/predicates)
  - predicate maturity, algorithm, diagnostic dispatch
- [`spec/diagnostics`](../../spec/diagnostics)
  - diagnostic registry와 predicate relation
- [`spec/language.md`](../../spec/language.md)
  - conformance, witness, provider, visibility 법칙
- [`current/product-lanes.json`](../../current/product-lanes.json)
  - 15개 제품 lane과 null receipt

이 장은 이 정본을 설명하는 projection이다.
Prelude나 도구 계약이 갱신되면
machine-readable row와 digest가 먼저 일치해야 하며,
문서만 바꾸어 새 authority나 product PASS를 만들 수 없다.
