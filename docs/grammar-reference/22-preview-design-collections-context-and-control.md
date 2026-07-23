<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# Preview Design: 컬렉션, context 및 제어

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

이 장의 여덟 기능은 모두 `source_activation = nonactivatable`인 설계
검토안이다. 아래 코드가 선택된 후보 철자를 보이더라도 current
Stable/Preview source가 아니며, 철자가 미선정인 항목은 ordinary Deeplus로
작성한 현행 명시적 대안만 보여 준다. 문서와 정적 예시는 구현·제품
지원을 만들지 않는다. parser, checker, MIR, xVM, LLVM, formatter/LSP를
포함한 15개 제품 lane은 모두 `NOT_RUN`이다.

<!-- deeplus-preview-feature-example: contextual_operation_anchor_dmad; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-contextual_operation_anchor_dmad"></a>

## 일반화된 contextual operation anchor

> **Feature metadata**
> - Feature ID: `contextual_operation_anchor_dmad`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
연산에 필요한 외부 context 또는 provider를 receiver 가까이 명시하려는
요구를 검토한다. 일반화된 `&expr` 아이디어는 NumericArray가 이미
소유하는 `&` polarity, borrow/address처럼 보이는 해석과 충돌할 수 있다.
token 모양만으로 의미 owner를 추측하지 않고 call signature에 context
책임이 드러나게 하는 것이 우선이다.

**제안 표면**
일반 operation anchor의 exact grammar와 provider API는 미선정이다.
아래는 current `context` parameter/argument를 사용하는 explicit
대안이다. 양성 검토는 parameter role과 provider identity가 signature에
있는 경우, 음성은 ambient provider 검색, 경계는 NumericArray 문맥과
ordinary call 문맥에서 같은 punctuation이 다른 owner 후보를 갖는 경우다.

**정적 판정과 상호작용**
token owner, context parameter role, call-shape identity, provider
visibility와 effect/authority를 함께 닫아야 한다. generalized anchor가
broadcast, borrow, address, extension activation 또는 AOP interception을
암시하지 않아야 한다. NumericArray 전용 current `&` surface 밖으로
의미를 자동 확장할 수 없다.

**평가·소유권·오류**
context expression은 일반 argument order에서 정확히 한 번 평가되고
borrow·owner·effect가 signature에 남아야 한다. provider 부재나 ambiguity는
호출 전 terminal diagnostic이며 다른 ambient service로 fallback하지
않는다. 전용 successor diagnostic와 MIR event는 미선정이고 제품 checker와
runtime은 `NOT_RUN`이다.

**현행 대안과 이행**
`context name: Type` parameter와 `context expression` argument 또는 ordinary
named parameter가 대안이다. migration은 기존 punctuation을 자동
anchor로 바꾸지 않고 provider dependency와 authority를 report한다.
formatter/LSP는 context role과 NumericArray token owner를 구분해 표시한다.

**활성화 선행 조건**
Design_의 token-owner 판정, exact EBNF/recovery, type/effect/authority
contract, ambiguity mutation corpus, API digest, formatter/LSP와
artifact-bound execution receipt가 필요하다. 문서만으로 P1이나
`NOT_RUN` lane은 닫히지 않는다.

**설계 검토 시나리오**
- **양성 전제·기대:** call signature가 context parameter와 provider
  identity를 명시하면 anchor는 그 channel 하나에만 값을 공급한다.
- **음성/거부:** ambient service 검색이나 type-check 결과로 `&` owner를
  바꾸면 call shape와 authority가 숨으므로 거부한다.
- **경계:** 같은 punctuation이 NumericArray와 ordinary call에서 모두
  후보가 되면 parse owner를 먼저 확정하지 못하는 설계는 보류한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: context role이 declaration과 call에 모두 보인다.
public def format(value: Float64, context pattern: FormatPattern) -> String = {
    return pattern ~ render value
}
let text = format(3.14, context FormatPattern!("{:.2f}"))
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: explicit_broadcast_marker_msp; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-explicit_broadcast_marker_msp"></a>

## NumericArray explicit broadcast marker

> **Feature metadata**
> - Feature ID: `explicit_broadcast_marker_msp`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM`; dependencies:
>   `numeric_array_sharp_shape_literal_msp`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
NumericArray operand가 어떤 axis로 broadcast되는지 call site에서 명시해
shape 오류와 암시적 NumPy식 확장을 줄이려는 요구를 검토한다. 과거
`matrix + &row` 후보는 `&`가 context anchor와 충돌하고, axis/shape
proof가 드러나지 않아 아직 exact source 표면으로 선택되지 않았다.

**제안 표면**
marker의 polarity, parse owner와 axis spelling은 미선정이다. 아래 코드는
사용자가 정의한 named adapter로 row를 matrix shape에 맞춘 뒤 ordinary
same-shape 연산을 하는 explicit 대안이다. 양성 검토는 axis와 target
shape가 명시된 경우, 음성은 ambient broadcast, 경계는 singleton axis가
여러 방식으로 맞는 경우다.

**정적 판정과 상호작용**
rank, axis identity, one-based logical coordinates, element domain과 result
shape를 결정적으로 증명해야 한다. marker가 context argument, borrow,
address나 elementwise-power gate를 활성화하지 않아야 한다. transpose,
matrix multiplication과 same-shape arithmetic은 각각 별도 operator
owner다.

**평가·소유권·오류**
matrix, adapted operand와 axis argument는 왼쪽에서 오른쪽으로 한 번씩
평가된다. shape mismatch는 write/publication 전에 진단되고 input owner를
소비하거나 부분 결과를 남기지 않는다. 현행 rejected trace의
`EXPLICIT_BROADCAST_MARKER_NOT_CURRENT`가 activation을 뜻하지 않으며,
successor diagnostic와 backend lowering은 미결/`NOT_RUN`이다.

**현행 대안과 이행**
same-shape operand 또는 명시적인 named broadcast/expand helper가 대안이다.
migration은 implicit broadcast를 marker로 자동 표기하거나 과거 `. ^`
철자를 이 기능으로 재분류하지 않는다. formatter는 token spacing을
보존하고 IDE는 axis proof와 source coordinates를 표시해야 한다.

**활성화 선행 조건**
exact parse owner, axis/shape algorithm, failure-atomic allocation, diagnostic
spans, formatter/LSP, rank·singleton·mismatch mutation corpus와 xVM/LLVM
parity receipt가 필요하다. 모든 제품 lane은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** marker가 axis와 target shape를 명시하고 결과 shape가
  유일하면 operand를 한 번씩 평가해 그 shape의 새 NumericArray를 만든다.
- **음성/거부:** singleton dimension만 보고 implicit broadcast하거나
  mismatch를 runtime 반복 규칙으로 숨기면 거부한다.
- **경계:** row/column orientation이 같은 extent를 가져도 axis identity가
  다르면 크기만으로 고르지 않고 명시적 orientation을 요구한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/value-operator-indexing-coherence.json -->
```deeplus
// 현행 명시적 대안: user-defined named adapter가 axis와 target을 소유한다.
let expandedRow = expandRow(row, columns: matrix.columns)
let result = matrix + expandedRow
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: explicit_context_argument_ampersand_spelling; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-explicit_context_argument_ampersand_spelling"></a>

## Ampersand context-argument spelling

> **Feature metadata**
> - Feature ID: `explicit_context_argument_ampersand_spelling`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: `contextual_operation_anchor_dmad`,
>   `explicit_context_parameter_msp`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
호출에서 context argument를 짧게 표시하려는 `&expr` 철자 아이디어를
검토한다. 간결함보다 parameter/call identity, evaluation order와 token
owner가 분명해야 하며 broadcast marker, generalized context anchor와
borrow/address처럼 읽히는 표면을 하나의 추측 규칙으로 합칠 수 없다.

**제안 표면**
ampersand argument와 대응 parameter spelling은 미선정이다. 아래는
current `context` keyword를 사용하는 명시적 대안이다. 양성 검토는
signature의 context role과 일치하는 argument, 음성은 ordinary parameter에
context 값을 공급하는 경우, 경계는 trailing closure나 overloaded call
shape 옆에서 punctuation owner가 모호한 경우다.

**정적 판정과 상호작용**
parameter role은 function identity와 API digest에 남고, argument는
해당 role에만 대응해야 한다. 동일 token이 broadcast/context/borrow
후보를 만들거나 type checking 결과에 따라 parse owner가 바뀌어서는
안 된다. named/default/rest argument evaluation 규칙도 보존한다.

**평가·소유권·오류**
context value는 lexical argument order에서 한 번 평가되고 authority와
lifetime이 call boundary를 넘을 때 검증된다. role mismatch는 call 전
diagnostic이고 ordinary argument로 fallback하지 않는다. ampersand
전용 diagnostic와 parser route는 미결이며 parser/checker 제품 상태는
`NOT_RUN`이다.

**현행 대안과 이행**
`context` keyword spelling과 ordinary named argument가 대안이다.
migration은 keyword를 punctuation으로 자동 축약하지 않고 call-shape와
public API 차이를 보고한다. signature help는 context channel을 positional,
named, witness channel과 분리해 보여야 한다.

**활성화 선행 조건**
token authority와 exact grammar, parameter/call identity, ownership/effect
contract, overload/trailing-closure mutation tests, formatter round-trip,
API compatibility와 target receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** `&` argument가 정확히 한 context formal에 결합되고
  ordinary argument order와 ownership/effect를 그대로 보존한다.
- **음성/거부:** ordinary positional formal에 공급하거나 ambient context를
  찾는 해석은 channel identity를 바꾸므로 거부한다.
- **경계:** trailing closure와 overload 후보가 같은 suffix를 공유하면
  punctuation을 tie-breaker로 쓰지 않고 call-shape ambiguity를 낸다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: punctuation 후보를 발명하지 않는다.
public def render(value: Money, context locale: Locale) -> String = {
    return locale ~ format(value)
}
let label = render(price, context Locale::koKR)
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: freeze_snapshot_view_responsibility_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-freeze_snapshot_view_responsibility_preview_design"></a>

## Freeze, snapshot 및 view 책임 분리

> **Feature metadata**
> - Feature ID: `freeze_snapshot_view_responsibility_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM / CHECKER`; dependencies:
>   `immutable_first_collection_ownership_preview_design`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
세 API가 모두 “읽기 전용 결과”처럼 보이더라도 owner transition과 비용을
명확히 분리하는 수용된 설계다. freeze는 mutable owner를 소비하는 shallow
transition, snapshot은 source를 보존하는 독립 point-in-time 값, view는
source보다 오래 살 수 없는 nonowning projection이어야 한다.

**제안 표면**
no-argument receiver형 `freeze()`, `snapshot()`, `view()` 책임이
후보이며 일부 successor carrier 이름은 미선정이다. 아래는 current
`MutableList`, `ListSnapshot`, `FrozenList` identity를 보존하는 explicit
대안이다. 양성 검토는 세 결과를 구분하는 경우, 음성은 deep-freeze 또는
shareability 추론, 경계는 live view 중 mutation/freeze다.

**정적 판정과 상호작용**
freeze는 shallow·failure-atomic이고 `Shareable`/`Transferable` 증명을
만들지 않는다. snapshot은 이후 source mutation과 독립적이며 source를
소비하지 않는다. view는 logical coordinates와 provenance를 보존하고
mutation, move, freeze, owner escape 및 isolation crossing과 충돌한다.

**평가·소유권·오류**
receiver는 한 번 평가된다. freeze 성공은 원 mutable binding을 소비하고
실패는 원 owner를 그대로 보존한다. snapshot allocation 실패는 source를
바꾸지 않고 partial snapshot을 publish하지 않는다. view는 allocation
copy가 아니며 region 종료 뒤 사용이 정적 오류다. 제품 실행은 `NOT_RUN`이다.

**현행 대안과 이행**
현재 `FrozenList<T>`, `ListSnapshot<T>`와 owner-bounded view API를 그대로
사용한다. migration은 세 identity를 `List`로 합치거나 deep copy 여부를
추측하지 않는다. API diff와 LSP는 consume/borrow/copy, lifetime와
coordinate domain을 각각 표시한다.

**활성화 선행 조건**
exact signatures와 carrier names, borrow/region 및 failure cleanup,
MIR owner events, indexing/serialization/actor review, formatter/LSP,
mutation·allocation-failure·escape corpus와 target-bound receipt가
필요하다. 현재 모든 product lane은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** freeze는 mutable owner를 성공 시 소비하고,
  snapshot은 독립 point-in-time 값, view는 owner-bound borrow를 만든다.
- **음성/거부:** 세 operation을 모두 deep copy 또는 모두 alias로 취급하면
  서로 다른 owner·failure·lifetime 책임을 지우므로 거부한다.
- **경계:** live view가 있는 동안 mutation/freeze를 요청하면 alias policy가
  허용하거나 거부하는 한 결과만 내며 view를 몰래 detach하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/literal-shaped-collection-design.json -->
```deeplus
// 현행 identity를 보존하는 explicit 책임 예시.
def snapshotThenFreeze(move values: MutableList<Int>) -> FrozenList<Int> = {
    let snapshot: ListSnapshot<Int> = values ~ snapshot()
    observe(snapshot)
    return values ~ freeze()
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: immutable_first_collection_ownership_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-immutable_first_collection_ownership_preview_design"></a>

## Immutable-first collection ownership

> **Feature metadata**
> - Feature ID: `immutable_first_collection_ownership_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / PRELUDE / TYPE_SYSTEM`; dependencies:
>   `one_based_sequence_logical_indexing`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
collection 기본 owner는 immutable이고 mutation은 이름이 다른 explicit
mutable owner만 수행하게 하는 수용된 책임 모델이다. 간결한 literal/type
surface가 mutable alias, Copy, shareability나 actor transfer를 암시하지
않게 하고 `Sequence`를 traversal-only contract로 유지한다.

**제안 표면**
immutable-first naming과 distinct mutable family가 설계 축이며 전체
migration surface는 미선정이다. 아래는 current `List`와
`MutableList`를 type으로 분리한 explicit 예다. 양성 검토는 mutation
owner가 드러난 경우, 음성은 immutable default에 write, 경계는 snapshot,
view와 live mutation이 겹치는 경우다.

**정적 판정과 상호작용**
`List`, `MutableList`, `FrozenList`, `ListSnapshot`, `Sequence` identity와
generic invariance를 보존해야 한다. conformance만으로 brackets나 mutable
place가 활성화되지 않고, literal-shaped sugar가 새로운 nominal identity,
ABI 또는 serialization form을 만들지 않는다.

**평가·소유권·오류**
mutation은 exclusive mutable place와 failure-atomic commit을 요구한다.
immutable value를 자동 copy-on-write owner로 바꾸거나 shared alias를
만들 수 없다. snapshot/freeze 실패와 index error가 원 owner를 보존해야
한다. successor migration/checker/runtime은 `NOT_RUN`이다.

**현행 대안과 이행**
current canonical generic spelling과 explicit mutable constructor를
사용한다. migration은 Prelude identity를 rename/merge하지 않고 mutation
site, ownership transition과 public ABI를 report한다. formatter/LSP는
immutable/mutable carrier와 view/snapshot을 분리한다.

**활성화 선행 조건**
Prelude naming/migration 결정, ownership·borrow·indexing law, ABI와
serialization review, actor transfer/shareability evidence, formatter와
cross-backend receipt가 필요하다. 정적 문서는 제품 지원이 아니다.

**설계 검토 시나리오**
- **양성 전제·기대:** literal default는 immutable `List<T>`가 되고
  mutation은 명시적 `MutableList<T>` owner에서만 수행된다.
- **음성/거부:** immutable literal에 쓰기를 허용하거나 hidden copy-on-write
  alias를 만들어 mutation 비용과 identity를 숨기면 거부한다.
- **경계:** snapshot·freeze·view 중 어느 책임인지 불명확한 API는
  `List`라는 공통 이름으로 합치지 않고 반환 carrier를 명시하게 한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/literal-shaped-collection-design.json -->
```deeplus
// 현행 명시적 구분: immutable List와 mutable owner는 다른 identity다.
let names: List<String> = ["Ada", "Grace"]
let queue: MutableList<String> = #mut["Ada", "Grace"]
queue ~ append("Lin")
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: literal_shaped_closed_record_type_surface_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-literal_shaped_closed_record_type_surface_preview_design"></a>

## Literal-shaped closed Record type

> **Feature metadata**
> - Feature ID: `literal_shaped_closed_record_type_surface_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / PARSER / TYPE_SYSTEM`; dependencies:
>   `record_literal_surface`,
>   `literal_shaped_collection_type_surface_preview_design`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
작은 closed label row type을 Record value materialization과 닮은 표기로
읽기 쉽게 만드는 수용된 설계다. runtime Map key와 static Record label을
혼동하지 않고, named schema나 nominal owner를 structural row로 추정하지
않는 것이 핵심이다.

**제안 표면**
type goal의 `${label:T,...}`가 선택된 후보이며 required static-Identifier
label만 허용한다. 아래 코드는 비활성 설계 예시다. 양성은 nonempty closed
unique row, 음성은 optional/open/rest/string label, 경계는 label 순서만
다른 두 표면의 canonical identity다.

**정적 판정과 상호작용**
label order를 정규화하고 exact row identity, field type, Record
materialization과 API metadata를 보존해야 한다. Map, named schema,
Union, value/pattern/index parser goal과 섞이지 않으며 string value가
compile-time label로 승격되지 않는다.

**평가·소유권·오류**
type surface 자체는 runtime 평가가 없고 Record construction은 field를
일반 순서로 한 번씩 평가한다. duplicate/unknown/missing label은 construction
commit 전에 거부되고 owner를 부분 publish하지 않는다. final successor
diagnostic와 parser/checker는 미결/`NOT_RUN`이다.

**현행 대안과 이행**
named Record/schema type 또는 canonical structural Record spelling이
대안이다. migration은 schema를 후보 sugar로 자동 rewrite하지 않고
open/optional/empty row 선택을 사용자에게 남긴다. formatter/LSP는 surface
hover에 canonical row를 보여야 한다.

**활성화 선행 조건**
exact type-goal grammar/recovery, label uniqueness/canonicalization,
row/API schema, formatter round-trip, Map/Record negative corpus와 target
parser/checker receipt가 필요하다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/literal-shaped-collection-design.json -->
```deeplus
// 비활성 type-goal 후보: current parser source가 아니다.
private type UserRow = ${id: Int, name: String}
let user: UserRow = ${id: 7, name: "Ada"}
```

<!-- deeplus-preview-feature-example: literal_shaped_collection_type_surface_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-literal_shaped_collection_type_surface_preview_design"></a>

## Literal-shaped collection type surface

> **Feature metadata**
> - Feature ID: `literal_shaped_collection_type_surface_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / LEXER / PARSER / TYPE_SYSTEM`; dependencies:
>   `basic_index_operator`, `one_based_sequence_logical_indexing`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
값 literal과 닮은 type spelling으로 common collection type의 읽기 비용을
줄이려는 수용된 설계다. 이 sugar가 새 collection identity를 만들거나
type/value/pattern/index parser goal을 합쳐 current bracket와 one-based
indexing 의미를 바꾸지 않게 한다.

**제안 표면**
type goal의 `[T]`, `#mut[T]`, `#set{T}`, `#map{K:V}`가 선택된 후보다.
아래 코드는 비활성 설계 예시다. 양성은 각 canonical identity로 유일하게
normalize되는 경우, 음성은 value/index goal에서 type으로 재해석,
경계는 `[T | U]`와 heterogeneous literal inference의 구분이다.

**정적 판정과 상호작용**
표면은 각각 `List`, `MutableList`, `Set`, `Map` identity로만 normalize된다.
`#N[T]` NumericArray shape, one-based indexing, bracket activation, Union,
Trait witness, ABI와 serialization은 그대로다. Map key와 Record label도
서로 다른 domain이다.

**평가·소유권·오류**
type alias에는 runtime 평가가 없다. value construction과 indexing은
canonical type의 기존 allocation/ownership/error law를 따른다. parser
goal ambiguity는 type checker가 고치는 것이 아니라 exact owner에서
진단해야 한다. product parser/checker/formatter는 `NOT_RUN`이다.

**현행 대안과 이행**
`List<T>`, `MutableList<T>`, `Set<T>`, `Map<K,V>`가 current 대안이다.
migration은 canonical spelling을 자동 sugar로 바꾸지 않고 public API
identity가 같다는 hover만 제공한다. formatter는 goal과 sigil/brace
attachment를 보존한다.

**활성화 선행 조건**
goal-separated grammar와 lossless recovery, canonicalization proof,
Prelude/API compatibility, formatter/LSP, ambiguity·Union·NumericArray
mutation corpus와 target receipt가 필요하다. 모든 제품 lane은 `NOT_RUN`이다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/literal-shaped-collection-design.json -->
```deeplus
// 비활성 type-goal 후보: canonical identity에만 normalize한다.
private type Names = [String]
private type Queue = #mut[String]
private type Tags = #set{String}
private type Counts = #map{String: Int}
```

<!-- deeplus-preview-feature-example: nullsafe_control; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-nullsafe_control"></a>

## Null-safe control surface

> **Feature metadata**
> - Feature ID: `nullsafe_control`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
Option value를 짧게 분기하거나 연쇄 처리하려는 요구를 검토한다. Deeplus는
`null`이나 ambient nullable type을 current value/type으로 갖지 않으므로,
새 sugar가 `Option`, `match`, `if let`, coalescing의 evaluation count,
ownership과 flow narrowing을 숨기지 않아야 한다.

**제안 표면**
optional chaining 또는 null-safe control의 exact syntax는 미선정이다.
아래는 current `Option` case를 명시적으로 match하는 대안이다. 양성 검토는
한 layer의 Option과 single evaluation, 음성은 `null`/implicit nullable,
경계는 nested `Option<Int?>`에서 어느 layer를 여는지 불명확한 경우다.

**정적 판정과 상호작용**
subject는 exact `Option<T>`여야 하고 short-circuit branch의 result type,
effects/errors, flow facts와 ownership join을 닫아야 한다. Result failure를
absence로 바꾸거나 arbitrary member lookup 실패를 `none`으로 접지 않고
pattern/exhaustiveness 법칙을 보존한다.

**평가·소유권·오류**
subject는 한 번 평가된다. `some` branch만 payload를 borrow/move하며 `none`
branch는 member/call effect를 실행하지 않는다. optional chaining probe는
`OPTIONAL_CHAINING_NOT_CURRENT`, `null`은
`NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE`으로 거부된다. successor runtime은
`NOT_RUN`이다.

**현행 대안과 이행**
`match`, `if let`, `Option::unwrapOrElse`와 explicit `::none`이 대안이다.
migration은 nullable syntax를 자동 Option으로 바꾸지 않고 nested layer와
fallback effect를 report한다. IDE는 desugaring과 conditional ownership을
표시해야 한다.

**활성화 선행 조건**
승인된 use case와 exact syntax, one-evaluation lowering, type/ownership/effect
join, deterministic diagnostics/recovery, migration/formatter corpus와
backend receipt가 필요하다. 제품 lane은 모두 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** 한 `Option` layer를 열고 subject를 한 번 평가한 뒤
  some branch와 none fallback의 type·effect·ownership join을 계산한다.
- **음성/거부:** `null`을 새 값으로 만들거나 실패를 자동 `Option::none`으로
  바꾸는 control은 현행 오류·Result 축을 지우므로 거부한다.
- **경계:** nested `Option<Option<T>>`에서는 어느 layer를 여는지 source에서
  확정되지 않으면 연쇄 해제를 추측하지 않고 명시적 match를 요구한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: Option layer와 branch가 source에 드러난다.
let city = @match userAddress {
    ::some(address) => address.city
    ::none => "unknown"
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->
