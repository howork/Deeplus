<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# Preview Design: 타입, 객체 및 Trait

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

이 장의 모든 항목은 설계 검토용이며 source activation이
`nonactivatable`이다. 선택된 후보 철자를 보여 주는 코드도 현행
Stable/Preview source가 아니고, 철자가 미선정인 항목의 코드는 오직
현행 명시적 대안을 보여 준다. 문서와 예제는 parser, checker, MIR,
runtime 또는 제품 지원을 만들지 않는다. 15개 제품 lane은 모두
`NOT_RUN`이고 OPEN P1을 닫는 항목은 없다.

<!-- deeplus-preview-feature-example: class_static_activation; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-class_static_activation"></a>

## Class 수준 static activation

> **Feature metadata**
> - Feature ID: `class_static_activation`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
Class owner에 공유 초기화와 수명 주기를 결합하려는 요구를 검토한다.
과거 `static class` 철자는 제거되었고 successor 철자는 선택되지 않았다.
핵심 질문은 Class identity와 module storage identity 중 누가 값을
소유하며, 상속·visibility·generic instantiation마다 초기화 cell이 몇
개 생기는가이다.

**제안 표면**
새 declaration surface는 미선정이다. 따라서 아래 코드는 설계 철자를
발명하지 않고 module binding과 ordinary function이라는 현행 대안을
보인다. 양성 검토 시나리오는 owner와 초기화 호출이 명시된 경우,
음성은 제거된 top-level static Class를 되살리는 경우, 경계는 generic
Class별 cell 수가 불명확한 경우다.

**정적 판정과 상호작용**
declaration identity, initialization order/cycle, inheritance,
visibility, API digest와 authority가 모두 닫혀야 한다. type-side
`def::`는 이미 owner가 있는 member이며 숨은 module initializer가 아니다.
Class/Enum/Trait dispatch identity나 CE-G6 책임을 static storage identity와
합쳐서는 안 된다.

**평가·소유권·오류**
초기화는 성공 시 한 번만 publish되고 실패 시 부분 object나 delegated
owner가 남지 않아야 한다. retry, failure caching, cleanup과 module unload
정책은 미결이다. 제거된 철자에는 `STATIC_CLASS_DECLARATION_NOT_CURRENT`가
적용되며 다른 constructor 진단으로 fallback하지 않는다.

**현행 대안과 이행**
module-level static-admissible `let`과 명시적 lifecycle 함수가 대안이다.
도구는 제거된 철자를 자동 복구하거나 Class를 임의 module singleton으로
rewrite하지 않는다. owner 선택과 호출 순서를 사용자가 정한 뒤에만
migration을 제안하며 formatter/LSP는 binding과 Class API를 분리한다.

**활성화 선행 조건**
Design_의 owner 선택, exact EBNF/root, cycle과 failure algorithm, API/link
identity, cleanup MIR, multi-module mutation corpus와 target-bound receipt가
필요하다. 현재 lexer부터 actual user study까지 제품 lane은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** module이 공유 cell 하나와 명시적 초기화 함수를
  소유하면, 첫 성공 publication 뒤 모든 Class 사용자가 같은 값을 본다.
- **음성/거부:** import만으로 IO를 수행하거나 제거된 `static class`가
  숨은 singleton을 만들면 owner와 effect가 보이지 않으므로 거부한다.
- **경계:** generic Class에서 type argument별 cell인지 단일 module
  cell인지 결정되지 않았다면 어느 쪽도 선택하지 않고 설계를 보류한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: Class activation을 암시하지 않는다.
private let cache = Cache!()
public def warmCache() -> Unit = {
    cache ~ warm()
}
```

두 `@match`가 각각 `left`와 `right`를 독립적으로 좁히므로 네 조합이
source에 모두 드러난다. 바깥 arm에서 `right`를 그대로
`toFloat64()`에 넘기면 `Int | Float64`가 아직 좁혀지지 않아
`UNION_VALUE_REQUIRES_NARROWING`이므로 현행 대안이 될 수 없다. 이 명시적
4-cell 표현은 multimethod를 활성화하지 않으면서도 제안된 dispatch
matrix가 해결하려는 중복을 정확히 보여 준다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: conformance_law_proof_block_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-conformance_law_proof_block_preview_design"></a>

## Conformance law proof block

> **Feature metadata**
> - Feature ID: `conformance_law_proof_block_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM / CHECKER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
Trait conformance가 구현 signature뿐 아니라 identity, associativity,
purity 같은 법칙을 만족한다는 기계 증거를 source 가까이에 둘 수 있는지
검토한다. 문서 주석이나 test 통과를 formal proof로 오인하지 않게 trusted
base와 증명 artifact의 경계를 명시하는 것이 목적이다.

**제안 표면**
proof block의 exact syntax, term language와 artifact 연결 방식은
미선정이다. 아래는 현행 conformance와 별도 test 함수라는 명시적
대안이다. 양성 검토는 종료하는 proof term, 음성은 unchecked assume,
경계는 generic substitution 후 법칙이 보존되는지 여부다.

**정적 판정과 상호작용**
proof calculus는 종료하고 canonical `WitnessId`, associated binding,
parent evidence와 같은 ground conformance에 결합되어야 한다. runtime
method body, optimizer hint, provider order 또는 source order가 proof
authority를 만들 수 없다. specialization/local witness와 결합할 때
coherence를 약화해서도 안 된다.

**평가·소유권·오류**
proof는 runtime effect, allocation이나 hidden owner를 생성하지 않는다.
실패는 deterministic checker diagnostic이고 executable fallback이
아니다. 현재 proof surface를 인식하는 경우
`CONFORMANCE_LAW_PROOF_BLOCK_REQUIRES_PREVIEW`로 거부하며, 전용 proof
failure code와 span 순서는 아직 미결이다.

**현행 대안과 이행**
ordinary conformance, 독립 property test와 외부 provenance-bound proof
artifact가 대안이다. migration은 주석이나 test를 자동 proof로 승격하지
않고 요구 법칙과 미검증 case를 보고한다. IDE에는 proof goal, trusted
dependency와 selected conformance identity를 별도 표시해야 한다.

**활성화 선행 조건**
formal calculus와 trusted base ratification, exact syntax/recovery,
termination/resource cap, artifact digest, generic proof corpus, independent
checker와 formatter/LSP receipt가 필요하다. 모든 제품 실행 상태는
`NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** 정규화된 conformance와 종료하는 proof term이 같은
  authority digest에 묶이면 checker는 법칙별 증명을 독립 확인한다.
- **음성/거부:** `assume` 같은 무검증 escape나 외부 test의 성공만으로
  proof를 합성하면 trusted base를 우회하므로 거부한다.
- **경계:** generic substitution 뒤 증명 명제가 달라지는 경우에는
  재검증 가능한 proof가 없으면 원래 증명을 재사용하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
public conformance UserId conforms Display {
    +def display+() -> String = { return self.raw ~ toString() }
}
// 현행 대안: 법칙은 별도 test/proof artifact로 검증한다.
def displayIsStable(id: UserId) -> Bool = {
    return id ~ display() == id ~ display()
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: custom_operator; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-custom_operator"></a>

## 임의 custom operator

> **Feature metadata**
> - Feature ID: `custom_operator`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
도메인별 기호를 선언하고 precedence를 선택하려는 요구를 검토한다.
그러나 module마다 다른 precedence나 glyph meaning은 parser, formatter,
API와 link 결과를 source/import order에 의존하게 만들 수 있다. 그래서
현행은 닫힌 intrinsic operator 표와 named behavior를 우선한다.

**제안 표면**
Recovery는 과거 `operator <symbol> precedence N` 모양을 진단용으로만
인식하며 activatable declaration은 없다. 아래는 exact syntax가
미선정인 상태에서 사용하는 named function 대안이다. 양성 검토는 전역
고정 glyph/precedence, 음성은 module-local 변경, 경계는 기존 token과의
maximal-munch 충돌이다.

**정적 판정과 상호작용**
glyph vocabulary, fixity, associativity, precedence, overload candidate,
Trait evidence와 formatter ownership이 하나의 결정적 registry로
닫혀야 한다. custom declaration이 fixed operator, message tilde 또는
extension resolution에 후보를 몰래 추가해서는 안 된다.

**평가·소유권·오류**
operand는 일반 expression order대로 한 번씩 평가되어야 하고 선택 실패
후 named API나 다른 operator로 fallback하지 않는다. 현행 probe는
`CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT`를 내며, precedence ambiguity를
runtime failure로 미루지 않는다. 결과/overflow/cleanup은 named operation
계약으로 명시한다.

**현행 대안과 이행**
named function, Trait method와 기존 intrinsic operator가 대안이다.
formatter가 알 수 없는 기호를 재배치하거나 migration이 precedence를
추측해 named call로 blind rewrite하면 안 된다. LSP는 symbol owner와
candidate origin을 보여 주되 비활성 declaration completion을 제공하지
않는다.

**활성화 선행 조건**
token authority, exact EBNF와 Pratt table, deterministic resolution,
public metadata, formatter idempotence, lexer/parser ambiguity mutation
corpus와 backend receipt가 필요하다. 현재 제품 lane은 전부 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** 전역 catalog가 glyph, fixity, precedence와 유일한
  dispatch owner를 고정하면 모든 module이 같은 parse tree를 만든다.
- **음성/거부:** module별 precedence 변경이나 보이는 import 순서로
  operator 의미가 달라지는 선언은 결정성을 깨므로 거부한다.
- **경계:** 새 glyph가 기존 maximal-munch token의 prefix와 겹치면
  lexer·Pratt 표 전체의 무모순 증명 전에는 후보로 수용하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/value-operator-indexing-coherence.json -->
```deeplus
// 현행 명시적 대안: 새 glyph 대신 의미가 드러나는 named API를 쓴다.
public def mergeScores(left: Score, right: Score) -> Score = {
    return Score!(value: left.value + right.value)
}
let total = mergeScores(a, b)
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: dependent_refinement_value_capture; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-dependent_refinement_value_capture"></a>

## 주변 값을 포획하는 dependent refinement

> **Feature metadata**
> - Feature ID: `dependent_refinement_value_capture`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
타입 predicate가 `limit` 같은 주변 값에 의존하는 관계를 정적으로
표현하려는 요구를 검토한다. 값의 mutation과 lifetime이 타입 의미를
바꾸거나 public API가 runtime environment를 숨겨 포획하지 않도록
decidability와 dependency identity를 먼저 닫아야 한다.

**제안 표면**
value-capturing predicate의 철자와 API residue는 미선정이다. 아래는
ordinary Bool 검사라는 현행 대안이다. 양성 검토는 immutable static
capture, 음성은 mutable local capture, 경계는 module 밖으로 나간 alias가
어떤 값을 가리키는지 불명확한 경우다.

**정적 판정과 상호작용**
predicate substitution, lifetime, mutation kill, normalization,
serialization과 separate compilation이 종료 가능한 규칙이어야 한다.
현행 finite R0 refinement나 flow fact를 일반 dependent type으로
자동 확대하지 않으며 solver-backed refinement로 fallback하지 않는다.

**평가·소유권·오류**
type checking이 runtime predicate 호출을 숨겨 삽입해서는 안 된다.
명시적 runtime 검사는 Bool/Result 계약대로 한 번 평가되고 capture
owner를 보존한다. 전용 source diagnostic은 아직 결합되지 않았으므로
문서는 코드를 약속하지 않고, 미인식 설계 철자에 generic activation
오류를 임의 배정하지 않는다.

**현행 대안과 이행**
finite R0, named validation 함수와 explicit `Result`/`Option` narrowing이
대안이다. migration은 Bool 검사를 타입으로 자동 승격하지 않고 captured
dependency와 mutation 지점을 report한다. LSP는 proof fact와 declared
type을 분리해 보여야 한다.

**활성화 선행 조건**
제한 calculus, termination metric, capture lifetime/kill algorithm,
public API certificate, deterministic diagnostics, checker mutation corpus와
artifact-bound receipt가 필요하다. 제품 상태는 모두 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** immutable compile-time 값만 포획하고 그 값과
  predicate digest가 타입 identity에 남으면 같은 입력은 같은 판정을 낸다.
- **음성/거부:** mutable local이나 clock·IO 결과를 포획해 타입 판정이
  실행 상태에 의존하면 정적 재현성이 없으므로 거부한다.
- **경계:** 포획한 값의 module lifetime보다 alias가 오래 살아남는 경우
  public certificate와 kill point가 없으면 export하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: 주변 limit는 ordinary value로 명시한다.
public def within(value: Int, limit: Int) -> Bool = {
    return value >= 0 and value <= limit
}
if within(candidate, maximum) {
    consume(candidate)
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: dyn_rcts_family; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-dyn_rcts_family"></a>

## Dynamic RCTS checked-carrier family

> **Feature metadata**
> - Feature ID: `dyn_rcts_family`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM / CHECKER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
닫힌 정적 RCTS descriptor를 open-world 경계에서 명시적인 checked dynamic
carrier로 확장하는 설계를 검토한다. ambient dynamic fallback이나
structural conformance를 허용하지 않고, erased payload의 owner와 exact
drop plan을 끝까지 보존하는 것이 목표다.

**제안 표면**
owned Dyn carrier, check/cast API와 source syntax는 미선정이다. 아래는
closed Union이라는 현행 대안이다. 양성 검토는 explicit pack과 checked
cast, 음성은 ordinary 값을 자동 box하는 경우, 경계는 unknown descriptor
또는 allocator/drop authority가 없는 payload다.

**정적 판정과 상호작용**
runtime representation, normalized type identity, provenance, cast result와
Trait evidence가 닫혀야 한다. inspection이 static type/witness/label을
만들 수 없고 dynamic Trait attach와도 자동 결합하지 않는다. SFD의
compiler retry/fallback/order winner 수는 0이어야 한다.

**평가·소유권·오류**
pack은 owner를 정확히 한 번 이동하거나 실패 시 원 owner를 반환·정리한다.
cast failure는 typed 결과이고 다른 mechanism 재시도가 아니다. 현행
`dyn` source probe는 `DYN_RCTS_SOURCE_NOT_CURRENT`로 거부된다. runtime
representation과 xVM/LLVM 실행은 `NOT_RUN`이다.

**현행 대안과 이행**
closed Union, explicit nominal wrapper와 borrow Facet이 대안이다. migration
도구는 `Any`류 값을 자동 Dyn으로 바꾸거나 cast fallback을 삽입하지 않는다.
IDE는 erased identity, owner/drop plan과 실패 channel을 보존해서 보여야
한다.

**활성화 선행 조건**
versioned descriptor와 carrier ABI, pack/cast/drop MIR, authority
non-forging proof, negative/mutation corpus, SFD-P1-009 target evidence와
별도 Design_ activation이 필요하다. 정적 schema만으로 P1은 닫히지 않는다.

**설계 검토 시나리오**
- **양성 전제·기대:** explicit pack이 owner와 versioned descriptor를
  기록하면 checked cast는 성공 payload 또는 원본 owner가 있는 실패를 낸다.
- **음성/거부:** ordinary 값을 자동 boxing하거나 실패 뒤 ambient
  structural lookup을 시도하면 identity와 비용이 숨으므로 거부한다.
- **경계:** 소비자가 descriptor version을 알지 못하면 값을 추측해
  unpack하지 않고 typed mismatch로 원본 carrier를 보존한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: 가능한 payload identity를 닫힌 Union으로 적는다.
private type InputValue = Int | String
let input: InputValue = readValue()
let text = @match input {
    n: Int => n ~ toString()
    s: String => s
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: dynamic_trait_attach_detach_stateless_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-dynamic_trait_attach_detach_stateless_preview_design"></a>

## Stateless dynamic Trait attach/detach

> **Feature metadata**
> - Feature ID: `dynamic_trait_attach_detach_stateless_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
runtime 경계에서 상태 없는 동작 묶음을 값에 부착·해제하려는 요구를
검토한다. static conformance와 달리 epoch 중간에 dispatch set이 변할 수
있으므로 atomicity, reflection, state capture와 concurrent reader의
일관성을 먼저 설계해야 한다.

**제안 표면**
attach/detach declaration, handle와 query API는 미선정이다. 아래는 static
conformance라는 현행 대안이다. 양성 검토는 stateless immutable entry,
음성은 captured mutable state, 경계는 호출과 detach가 경합하는 경우다.

**정적 판정과 상호작용**
dynamic attachment가 canonical Trait witness, associated binding 또는
operator candidate를 제조해서는 안 된다. registry epoch, visibility,
owner와 dispatch identity가 결정적이어야 하며 local witness,
specialization과 monkey patching은 별도 거부 경계다.

**평가·소유권·오류**
attach/detach는 성공 또는 실패가 atomic하고 partial registry를
publish하지 않아야 한다. 호출 중 detach의 lifetime과 cleanup owner는
미결이다. 현행 후보 철자는 `DYNAMIC_TRAIT_ATTACH_NOT_CURRENT`로 거부되며
정적 conformance로 fallback하지 않는다.

**현행 대안과 이행**
static conformance와 explicit strategy object가 대안이다. migration은
dynamic attach를 static witness로 자동 고정하지 않고 capture, race와
call-site inventory를 제시한다. debugger/LSP는 runtime attachment를
static conformance와 다른 층으로 표시해야 한다.

**활성화 선행 조건**
closed registry protocol, stateless proof, epoch/owner model, deterministic
dispatch, concurrency/rollback corpus와 xVM/LLVM target receipt가 필요하다.
모든 제품 lane은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** immutable stateless entry를 handle로 부착하고 epoch가
  일치하면 이후 호출은 그 handle의 정확한 behavior identity를 사용한다.
- **음성/거부:** attachment가 mutable capture나 새 owner fact를 만들면
  static conformance와 authority 경계를 위조하므로 거부한다.
- **경계:** 호출과 detach가 경합하면 정해진 epoch의 호출 완료 또는
  terminal detach 중 하나만 관측되어야 하며 반쯤 해제된 dispatch는 없다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: 동작은 선언 시 static conformance로 고정한다.
public conformance User conforms Display {
    +def display+() -> String = { return self.name }
}
let text = user ~ display()
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: effectful_static_activation; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-effectful_static_activation"></a>

## Effectful static activation

> **Feature metadata**
> - Feature ID: `effectful_static_activation`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
공유 값 초기화에 IO나 외부 provider가 필요한 경우 그 phase, 순서와 실패를
명시하려는 요구를 검토한다. compile-time 실행, link-time 생성과 runtime
entry 효과를 섞지 않고 reproducibility와 supply-chain authority를
보존하는 것이 핵심이다.

**제안 표면**
declaration/profile/cache API는 미선정이다. 아래는 entry에서 explicit
initializer를 호출하는 현행 대안이다. 양성 검토는 phase와 effect가
명시된 경우, 음성은 import 시 hidden IO, 경계는 실패 후 retry와 cache
reuse 정책이 불명확한 경우다.

**정적 판정과 상호작용**
phase identity, `throws`/`effects`, dependency graph, authority, cache key와
cleanup을 닫아야 한다. module/class/function static proposal과 같은
storage owner를 공유한다고 가정하지 않으며 provider 실행을 compiler
effect로 자동 승격하지 않는다.

**평가·소유권·오류**
initializer는 명시된 phase에서 한 번 평가되고 성공 전에는 value를
publish하지 않는다. failure, retry, poison과 partial resource cleanup은
별도 상태 전이로 정의해야 한다. 전용 diagnostic은 아직 미결이며 숨은
effect를 ordinary static success로 간주할 수 없다.

**현행 대안과 이행**
entry 또는 explicit lifecycle API에서 effectful 함수를 호출한다.
migration은 top-level initializer를 자동 이동하지 않고 effect와 ordering
dependency를 report한다. build tool과 LSP는 compile-time artifact와
runtime value를 분리해 표시한다.

**활성화 선행 조건**
closed phase model, deterministic graph/cycle algorithm, reproducible
cache/provenance, error/cleanup MIR, clean-build mutation corpus와 target
receipt가 필요하다. compiler·runtime·tooling 제품 lane은 모두 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** activation phase, effect row와 dependency graph가
  명시되면 같은 clean build는 같은 순서와 artifact identity를 낸다.
- **음성/거부:** import 시점의 숨은 network/IO나 환경별 initializer는
  effect와 provenance를 숨기므로 거부한다.
- **경계:** 초기화가 한 번 실패한 뒤 재시도할 수 있는지 미정이면 cache,
  poison, cleanup 중 어느 정책도 구현이 임의 선택하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: effect와 호출 phase를 entry가 소유한다.
public def initializeCache() -> Cache
    throws IOError
    effects {io}
= {
    return loadCache()
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: enum_case_display_mapping_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-enum_case_display_mapping_preview_design"></a>

## Enum case-owned Display mapping

> **Feature metadata**
> - Feature ID: `enum_case_display_mapping_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / PRELUDE / TYPE_SYSTEM`; dependencies:
>   `string_interpolation_braced_expr_core`, `trait_witness_formal_judgment_core`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
Enum case의 사용자 표시를 owner 가까이에 두면서 parsing, serialization,
localization과 혼동하지 않게 하는 수용된 설계다. inhabitable case 전체를
all-or-none으로 매핑해 partial fallback과 case-local witness를 없애는
것이 목적이다.

**제안 표면**
case 뒤의 `~>`와 restricted String template가 선택된 후보다. 아래 코드는
설계 검토용이며 current source가 아니다. 양성은 모든 case의 pure mapping,
음성은 일부 case 누락, 경계는 payload expression이 effect나 비허용
formatting을 요구하는 경우다.

**정적 판정과 상호작용**
Enum owner는 whole-Enum `Display` witness 하나만 합성한다. case witness,
hidden provider, automatic reverse parser, serialization tag와 localization
권위를 만들지 않는다. explicit same-ground witness와의 충돌은 terminal이고
source order fallback이 없다.

**평가·소유권·오류**
template는 허용된 payload field를 읽는 순수한 String 구성으로 제한되고
payload를 이동하거나 effect를 실행하지 않는다. mapping 누락·중복·impure
template의 final diagnostic ID는 아직 미선정이다. 정적 예시의 parser,
checker와 runtime은 `NOT_RUN`이다.

**현행 대안과 이행**
ordinary exhaustive `match` display 함수가 대안이다. migration은 기존
함수를 자동 mapping으로 옮기거나 reverse parser를 생성하지 않는다.
formatter는 case/template 결합을 보존하고 LSP는 synthesized witness와
serialization identity를 분리한다.

**활성화 선행 조건**
restricted template grammar/purity, all-or-none checker, TCC/CE P1,
witness conflict와 link summary, diagnostic binding, formatter 및 target
corpus가 필요하다. 별도 activation 전에는 지원을 주장할 수 없다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
// 비활성 설계 표면: 현행 parser에는 들어가지 않는다.
private enum Status {
    Ready ~> "ready"
    Busy ~> "busy"
}
```

<!-- deeplus-preview-feature-example: enum_declaration_order_ord_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-enum_declaration_order_ord_preview_design"></a>

## Enum declaration-order Ord derivation

> **Feature metadata**
> - Feature ID: `enum_declaration_order_ord_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / PRELUDE / TYPE_SYSTEM`; dependencies:
>   `trait_witness_formal_judgment_core`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
선언 순서를 의미 순서로 쓰려는 의도를 명시적으로 선택한 Enum에만 전체
순서를 파생한다. `VariantId`, raw value, serialization tag, layout와 ABI를
semantic order로 재사용하지 않아 evolution과 foreign mapping을 분리하는
것이 핵심이다.

**제안 표면**
정확히 하나의 `enum#increasing` 또는 `enum#decreasing` modifier가 선택된
후보다. 아래 코드는 비활성 설계 예시다. 양성은 payload-free nonempty
nongeneric Enum, 음성은 두 modifier 동시 사용, 경계는 reorder가 public
order behavior를 바꾸는 경우다.

**정적 판정과 상호작용**
owner는 `SemanticOrderRank`와 whole-Enum `Ord` witness 하나를 만든다.
payload ordering, comparison glyph routing, case-local witness와 raw ordinal
추론은 없다. explicit same-ground `Ord`와 synthesized witness의 충돌은
deterministic terminal error다.

**평가·소유권·오류**
비교는 payload나 foreign tag를 읽지 않고 selected declaration rank만
비교한다. empty/generic/payload-bearing Enum은 거부하며 one-case Enum은
자명한 순서만 갖는다. final diagnostic registry code와 runtime lowering은
미결이고 제품 evidence는 `NOT_RUN`이다.

**현행 대안과 이행**
explicit compare 함수나 ranking match가 대안이다. migration은 기존 Enum을
자동 modifier화하지 않고 case reorder의 behavior diff를 보고한다.
formatter는 modifier와 declaration order를 보존하고 API diff는 raw/layout
변화와 semantic-order 변화를 별도 lane으로 표시한다.

**활성화 선행 조건**
TCC/CE P1 closure, witness synthesis/conflict, link metadata, reorder
diagnostics, formatter/LSP와 permutation·serialization·ABI 분리 corpus,
target receipt가 필요하다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
// 비활성 설계 표면: source order를 raw/tag로 사용하지 않는다.
private enum#increasing Priority {
    Low
    Normal
    High
}
```

<!-- deeplus-preview-feature-example: enum_exact_variant_subset_alias_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-enum_exact_variant_subset_alias_preview_design"></a>

## Enum exact-variant subset alias

> **Feature metadata**
> - Feature ID: `enum_exact_variant_subset_alias_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM`; dependencies:
>   `closed_anonymous_union_type_msp`, `enum_member_declaration_surface`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
같은 Enum owner의 payload-free case 일부를 별도 타입처럼 안전하게
표현하되 새 runtime wrapper나 open subtyping search를 만들지 않는
수용된 설계다. widening은 lossless이고 owner 값의 narrowing은 명시적으로
실패 가능해야 한다.

**제안 표면**
Enum body의 `+type Name = CaseA | CaseB`가 선택된 후보다. 아래 코드는
비활성 설계 예시다. 양성은 same-owner finite set, 음성은 foreign 또는
payload-bearing case, 경계는 owner universe 변경 후 stored subset
metadata의 digest mismatch다.

**정적 판정과 상호작용**
identity는 `(EnumId, allowed VariantId set, universe digest)`로 정규화된다.
owner representation과 legal whole-Enum witness를 재사용하지만 alias-local
witness, range/iteration, implicit narrowing과 cross-owner Union을 만들지
않는다. exhaustiveness는 exact finite set만 소비한다.

**평가·소유권·오류**
subset-to-owner widening은 값 이동 없이 identity proof로 성립한다.
owner-to-subset은 checked result이며 실패 시 owner를 손실하지 않는다.
foreign/payload variant와 stale universe의 final diagnostic는 미결이다.
parser/checker/backend는 모두 `NOT_RUN`이다.

**현행 대안과 이행**
closed Union, explicit predicate와 checked constructor가 대안이다.
migration은 case 목록을 자동 subset alias로 만들지 않고 rename과 universe
change를 보고한다. IDE는 owner와 allowed cases, narrowing channel을
탐색 가능하게 보여야 한다.

**활성화 선행 조건**
frozen `VariantId` universe, exact grammar, narrowing API와 ownership,
exhaustiveness integration, API digest/versioning, CE/TCC evidence와 target
receipt가 필요하다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
// 비활성 설계 표면: owner widening은 lossless, 반대 방향은 checked다.
private enum Day {
    Mon
    Tue
    Sat
    Sun
    +type Weekend = Sat | Sun
}
```

<!-- deeplus-preview-feature-example: extension_dot_call_sugar; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-extension_dot_call_sugar"></a>

## Extension dot-call sugar

> **Feature metadata**
> - Feature ID: `extension_dot_call_sugar`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: `named_extension_set_block_msp`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
활성화된 extension function을 ordinary member처럼 간결하게 호출하려는
요구를 검토한다. dot/member, tilde pipeline, explicit extension selector와
actor message domain을 합치면 candidate origin과 dispatch 의미가
불투명해지므로 resolution의 no-fallback 경계가 우선이다.

**제안 표면**
`value.member(...)` 후보의 exact admission과 ranking은 미선정이다. 아래
`EX-R48-016`은 tilde와 qualified selector라는 현행 대안이다. 양성 검토는 유일한 extension,
음성은 real member와 extension 충돌, 경계는 서로 다른 import가 같은
selector를 노출하는 경우다.

**정적 판정과 상호작용**
ordinary member와 extension candidate를 섞더라도 unique origin과 import/link
invariance를 보장해야 한다. dot call이 Trait witness, operator glyph나
message send를 만들지 않으며 실패 후 tilde/ordinary member로 재시도하지
않는다.

**평가·소유권·오류**
receiver와 argument는 한 번씩 일반 호출 순서로 평가된다. resolution
ambiguity는 평가 전에 terminal error이고 receiver를 소비하지 않는다.
전용 diagnostic와 exact candidate ranking은 미결이며 현재 dot sugar
제품 실행은 `NOT_RUN`이다.

**현행 대안과 이행**
`value ~ name(...)`과 `value ~ Set::name(...)`가 대안이다. migration은
tilde를 자동 dot으로 바꾸지 않고 candidate origin을 보존한다. completion은
ordinary member와 active extension을 다른 범주로 표시해야 한다.

**활성화 선행 조건**
ranked resolution/no-fallback law, exact grammar, import/link permutation
tests, diagnostic provenance, formatter/LSP round-trip와 MIR call identity
receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** receiver의 static type에서 유일한 active extension이
  선택되면 dot sugar는 그 exact extension selector로만 정규화된다.
- **음성/거부:** real member와 extension 또는 두 extension이 같은 call
  shape를 제공하면 import 순서로 고르지 않고 ambiguity로 거부한다.
- **경계:** 별도 module import가 후보 하나를 추가하는 경우 기존 call의
  의미가 조용히 바뀌지 않도록 API/link compatibility 진단을 낸다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// Current alternative: explicit tilde/qualified extension selection.
public extension Int as metric {
    +def m() -> Length = { return Length!(value: self, unit: Unit::meter) }
}
use Int::metric
let a = 3 ~ m
let b = 3 ~ Int::metric::m
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: facet_inout_pack_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-facet_inout_pack_preview_design"></a>

## Inout Facet package

> **Feature metadata**
> - Feature ID: `facet_inout_pack_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM / CHECKER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
숨겨진 concrete payload에 receiver-bound exclusive mutable view를 제공하는
existential package를 검토한다. borrow Facet의 read-only evidence sealing을
공유 mutable existential로 확대하지 않고, 정확히 하나의 place와
nonescape lifetime을 보존하는 것이 목적이다.

**제안 표면**
`facet[inout value as Trait]`와 대응 `Facet<inout any Trait>`가 Recovery에
있는 선택 후보다. 아래는 비활성 설계 예시다. 양성은 unique local place,
음성은 alias가 겹치는 pack, 경계는 suspension 또는 return으로 region을
벗어나는 경우다.

**정적 판정과 상호작용**
exclusive place identity, alias exclusion, isolation, Trait witness coherence와
method receiver capability가 닫혀야 한다. borrow Facet을 자동 inout으로
승격하지 않고 shared wrapper나 actor crossing이 mutation 권위를 만들지
않는다.

**평가·소유권·오류**
pack은 payload를 이동하지 않지만 exclusive loan을 정확히 한 번 열고
종료 시 되돌린다. 실패·panic·cancellation에도 loan residue가 없어야 한다.
현행은 Recovery 후 semantic node 0으로 거부되고 전용 final diagnostic와
MIR region execution은 미결이다.

**현행 대안과 이행**
ordinary `inout` parameter 또는 current borrow Facet과 owner가 수행하는
명시적 mutation이 대안이다. migration은 borrow pack을 자동 변경하지
않고 alias/escape 지점을 report한다. IDE는 exclusive region과 suspension
금지를 표시해야 한다.

**활성화 선행 조건**
region/alias algorithm, HIR/MIR place identity, failure cleanup, formatter,
positive/negative/escape corpus, TCC evidence와 target receipt가 필요하다.
제품 lane은 모두 `NOT_RUN`이다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/types/type-system.md -->
```deeplus
// 비활성 설계 표면: 현재는 Recovery 진단만 가능하다.
let editable = facet[inout value as Editable]
editable ~ update()
```

<!-- deeplus-preview-feature-example: facet_owned_pack_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-facet_owned_pack_preview_design"></a>

## Owned Facet package

> **Feature metadata**
> - Feature ID: `facet_owned_pack_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM / CHECKER / RUNTIME`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
숨겨진 concrete payload와 정확한 allocator/drop plan을 함께 이동하는
owned existential을 검토한다. type erasure 뒤에도 owner를 잃지 않고
성공·실패·cast·transfer마다 누가 payload를 소비하거나 반환하는지
정적으로 추적해야 한다.

**제안 표면**
`facet[move value as Trait]`와 `Facet<move any Trait>`가 선택 후보지만
activatable grammar는 없다. 아래는 비활성 설계 예시다. 양성은 unique
owner와 known drop plan, 음성은 borrowed/aliased value, 경계는 actor
crossing 또는 failed pack 후 owner 반환이다.

**정적 판정과 상호작용**
exact concrete cleanup, witness identity, existential layout, transferability,
isolation과 cast result를 닫아야 한다. Dyn carrier나 Box identity와
자동 합치지 않고 case/local witness나 hidden provider를 넣지 않는다.

**평가·소유권·오류**
pack 성공은 원 binding을 소비하고 package가 drop 책임을 갖는다. 실패는
원 owner를 그대로 반환하거나 unpublished payload를 정확히 한 번
cleanup해야 한다. compiler fallback/retry는 0이고 현행 Recovery는
admitted AST/HIR/MIR를 만들지 않는다.

**현행 대안과 이행**
explicit nominal Box/owner wrapper와 current borrow Facet이 대안이다.
migration은 borrow를 move로 자동 변경하지 않고 use-after-move와 drop
plan을 report한다. LSP는 erased type보다 owner/provenance를 우선 표시한다.

**활성화 선행 조건**
existential ABI, move/drop/cast MIR, transactional failure law, TCC closure,
SFD-P1-009와 xVM/LLVM receipt가 필요하다. 모든 제품 지원은 `NOT_RUN`이다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/types/type-system.md -->
```deeplus
// 비활성 설계 표면: 성공 시 value의 유일 owner를 package가 받는다.
let printable = facet[move value as Printable]
consume(move printable)
```

<!-- deeplus-preview-feature-example: first_class_witness_value_not_current; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-first_class_witness_value_not_current"></a>

## First-class Witness value

> **Feature metadata**
> - Feature ID: `first_class_witness_value_not_current`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM / CHECKER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
Trait evidence를 일반 값처럼 저장·전달하려는 요구를 검토한다. 현행
evidence는 checker-visible이고 non-forgeable이며, raw runtime value로
노출하면 scope, lifetime, ABI와 reflection을 통해 coherence를 우회할 수
있다.

**제안 표면**
raw Witness value type, constructor와 projection API는 미선정이다. 아래는
explicit `using` parameter라는 현행 대안이다. 양성 검토는 canonical
evidence의 bounded 전달, 음성은 임의 constructor, 경계는 closure/global
escape와 stale package version이다.

**정적 판정과 상호작용**
`WitnessId`, ground conformance key, associated binding과 visibility를
보존하고 local witness, dynamic attachment 또는 reflection이 evidence를
제조하지 못해야 한다. operator dispatch나 specialization candidate로
암시 승격하지 않는다.

**평가·소유권·오류**
현행 using evidence는 call boundary에만 존재하고 반환·저장되지 않는다.
raw value probe는 `RAW_WITNESS_VALUE_NOT_CURRENT`로 거부된다. 미래
representation이 생겨도 forged/stale evidence는 runtime fallback 없이
terminal validation failure여야 한다.

**현행 대안과 이행**
static conformance와 explicit witness parameter가 대안이다. migration은
using parameter를 raw value로 바꾸지 않고 escape site를 report한다.
IDE는 evidence origin과 lifetime을 값 debugger와 별도로 표시한다.

**활성화 선행 조건**
canonical witness ABI, construction authority, HIR/MIR transport, lifetime와
separate compilation law, forgery corpus와 target receipt가 필요하다.
제품 실행은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** canonical checker가 만든 witness만 bounded parameter로
  전달되며 callee는 같은 conformance identity를 재검색 없이 사용한다.
- **음성/거부:** 사용자 constructor나 deserialization으로 witness를
  위조하면 evidence authority가 없으므로 terminal validation failure다.
- **경계:** witness가 closure·global·foreign ABI로 escape하려 하면 lifetime
  및 representation 계약이 닫히기 전에는 저장을 허용하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: evidence는 bounded using channel로만 전달한다.
def sort<T>(xs: List<T>, using order: witness Ord<T>) -> List<T> = {
    return stableSort(xs, using order)
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: fixed_operator_conformance_overloading; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-fixed_operator_conformance_overloading"></a>

## Fixed operator conformance overloading

> **Feature metadata**
> - Feature ID: `fixed_operator_conformance_overloading`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM / CHECKER`; dependencies:
>   `closed_operator_symbols_open_named_extensions`
> - P1 영향: 없음. `TCC-P1-002..008` 7개는 모두 OPEN으로 유지한다.

**검토 목적**
현행 닫힌 glyph를 Trait conformance에 연결하면서 intrinsic operator의
결정성과 읽기 비용을 보존할 수 있는지 검토한다. import/source order,
priority, specialization 또는 fallback이 같은 식의 의미를 바꾸지 않게
하는 것이 핵심이다.

**제안 표면**
operator-to-Trait registry와 source route는 미선정이다. 아래는 named Trait
method라는 현행 대안이다. 양성 검토는 unique ground witness, 음성은 두
candidate 또는 AUTO/VIA, 경계는 intrinsic domain과 user conformance가
동시에 맞는 경우다.

**정적 판정과 상호작용**
current `INTRINSIC_ONLY` table, operator domain 분리와 unique witness를
보존해야 한다. extension/local witness/case witness/provider가 glyph
candidate를 추가하지 않으며 실패 뒤 intrinsic이나 named method로
재시도하지 않는다. TCC P1 7개는 그대로 OPEN이다.

**평가·소유권·오류**
operand는 한 번씩 평가되고 selected dispatch identity가 MIR에 닫혀야
한다. 현행 비-intrinsic 후보는
`FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT`로 거부된다. final successor
diagnostic registry와 runtime dispatch는 아직 미결이다.

**현행 대안과 이행**
named Trait method/function과 admitted intrinsic operator가 대안이다.
migration은 method call을 glyph로 자동 축약하지 않고 origin을 보존한다.
formatter/LSP는 intrinsic과 named evidence를 명확히 구분한다.

**활성화 선행 조건**
TCC-P1-002..008, deterministic registry/no-fallback algorithm, closed MIR
dispatch, import permutation과 mutation corpus, Design_ 판정 및 target
receipt가 필요하다. 제품 lane은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** intrinsic domain 밖에서 exact operand pair에 유일한
  ground witness가 있으면 operator registry가 하나의 dispatch identity를 낸다.
- **음성/거부:** 후보 둘, `AUTO`/`VIA` fallback 또는 source-order winner가
  필요하면 ambiguity를 terminal로 보고 lower tier를 평가하지 않는다.
- **경계:** intrinsic과 사용자 conformance가 같은 operand domain을
  주장하면 precedence authority가 확정될 때까지 어느 후보도 활성화하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/value-operator-indexing-coherence.json -->
```deeplus
public trait Merge {
    +def mergedWith+(other: Self) -> Self
}
// 현행 대안: glyph가 아니라 named Trait method를 호출한다.
let combined = left ~ mergedWith(right)
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: function_static_activation; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-function_static_activation"></a>

## Function static activation

> **Feature metadata**
> - Feature ID: `function_static_activation`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
함수 owner에 결합된 정적 callable 또는 초기화 상태를 표현하려는 과거
요구를 검토한다. 제거된 top-level `static def`가 ordinary function,
module binding과 type-side `def::` 중 무엇을 뜻했는지 모호했으므로
owner와 lifecycle을 먼저 선택해야 한다.

**제안 표면**
successor 철자는 미선정이다. 아래는 owning nominal 안의 current type-side
member 대안이다. 양성 검토는 명시적 nominal owner, 음성은 top-level
static function, 경계는 generic instantiation마다 code/state identity가
분리되는 경우다.

**정적 판정과 상호작용**
function identity, capture 금지, visibility, generic monomorphization,
initialization과 API digest를 닫아야 한다. `def::`는 type-side member이지
module load hook이 아니며 class/module/effectful static proposal과
자동 결합하지 않는다.

**평가·소유권·오류**
초기화 상태가 있다면 publication/failure/cleanup을 별도 정의해야 한다.
ordinary type-side call은 일반 호출 규칙을 따른다. 제거된 top-level
철자는 `STATIC_FUNCTION_DECLARATION_NOT_CURRENT`이고 자동 `def::` 전환은
안전하지 않다.

**현행 대안과 이행**
ordinary module function, explicit binding과 owner 내부 `def::`가 대안이다.
migration은 owner를 사용자에게 물어보고 capture/API 차이를 report한다.
formatter와 LSP는 type-side member를 static initializer로 표시하지 않는다.

**활성화 선행 조건**
owner/lifecycle decision, exact grammar, initialization cycle/failure,
generic/API/link identity, formatter와 multi-module execution receipt가
필요하다. 모든 제품 lane은 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** nominal owner 내부의 type-side function은 그 owner와
  API identity가 분명하고 ordinary call 규칙으로 실행된다.
- **음성/거부:** top-level `static def`가 임의 global owner나 hidden
  initializer를 만들면 `STATIC_FUNCTION_DECLARATION_NOT_CURRENT`로 거부한다.
- **경계:** generic owner에서 instantiation별 code/state identity가
  불명확하면 단일 함수로 합치거나 복제하지 않고 owner 결정을 요구한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public class BatchPolicy {
    // 현행 명시적 대안: owner가 분명한 type-side member.
    def:: defaultBatch() -> Int = { return 32 }
}
let size = BatchPolicy::defaultBatch()
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: generic_named_extension_set_target; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-generic_named_extension_set_target"></a>

## Generic named extension-set target

> **Feature metadata**
> - Feature ID: `generic_named_extension_set_target`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM`; dependencies:
>   `generic_parameter_model_phase_a`, `named_extension_set_block_msp`,
>   `where_clause_constraint_core`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
한 generic nominal family에 재사용 가능한 named extension set을 적용하려는
요구를 검토한다. Phase A exact nominal target의 단순성을 잃지 않으면서
substitution, overlap, locality와 public API residue를 결정적으로 만들 수
있는지가 핵심이다.

**제안 표면**
generic target parameter와 where-clause의 exact extension syntax는
미선정이다. 아래는 exact nominal target의 현행 extension 대안이다.
양성 검토는 단일 normalized target, 음성은 overlapping generic sets,
경계는 alias/where substitution 후 두 target이 같아지는 경우다.

**정적 판정과 상호작용**
applicability와 termination, overlap/coherence, visibility/import와
`ExtensionSetId`를 닫아야 한다. structural target, hidden specialization,
Trait witness와 dot-call sugar를 암시하지 않고 link order가 winner를
만들 수 없다.

**평가·소유권·오류**
extension call은 receiver/argument를 한 번 평가하고 static selected
member를 호출한다. ambiguous target은 평가 전 terminal diagnostic이며
다른 extension으로 fallback하지 않는다. generic 전용 diagnostic와
product checker는 아직 미결/`NOT_RUN`이다.

**현행 대안과 이행**
각 exact nominal target의 named extension이나 ordinary generic function이
대안이다. migration은 여러 exact set을 자동 합치지 않고 overlap/API
diff를 report한다. IDE는 substitution 결과와 activation origin을 표시한다.

**활성화 선행 조건**
generic applicability/normalization, termination proof, metadata/API digest,
link permutation corpus, formatter/LSP와 target receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** substitution 뒤 target이 하나의 exact nominal
  identity로 정규화되고 적용 가능한 set이 유일하면 그 set만 선택한다.
- **음성/거부:** 두 generic target이 겹치거나 unconstrained parameter가
  남으면 선언 순서나 import 순서로 고르지 않고 거부한다.
- **경계:** 서로 다른 alias가 substitution 뒤 같은 target이 되면 link
  단계에서 중복 identity를 검출하고 body 중 하나를 임의 승자로 삼지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: exact nominal Int target만 확장한다.
public extension Int as metric {
    +def m() -> Length = { return Length!(value: self, unit: Unit::meter) }
}
use Int::metric
let distance = 3 ~ m
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: local_witness_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-local_witness_preview_design"></a>

## Local Witness

> **Feature metadata**
> - Feature ID: `local_witness_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
좁은 lexical 범위에서 다른 Trait evidence를 선택하려는 요구를 검토한다.
같은 call text가 scope, import 또는 closure capture에 따라 다른 의미를
갖지 않도록 global coherence와 explicit evidence 전달 사이의 경계를
유지해야 한다.

**제안 표면**
local declaration, shadowing과 selection syntax는 미선정이다. 아래는
explicit `using` parameter 대안이다. 양성 검토는 call-site가 evidence를
명시하는 경우, 음성은 ambient shadowing, 경계는 closure/API 밖으로 local
evidence가 escape하는 경우다.

**정적 판정과 상호작용**
lexical `WitnessId`, capture/lifetime, overlap, separate compilation과 API
digest를 닫아야 한다. global conformance, specialization, fixed operator와
extension resolution을 local declaration이 몰래 바꾸지 않아야 한다.

**평가·소유권·오류**
current using channel은 selected evidence를 call에 명시하고 raw value로
반환하지 않는다. local witness 철자는 `LOCAL_WITNESS_NOT_CURRENT`로
거부되며 global candidate로 fallback하지 않는다. runtime relookup은 0이어야
한다.

**현행 대안과 이행**
explicit witness parameter 또는 strategy value가 대안이다. migration은
scope-local behavior를 call-site argument로 수동 노출하도록 inventory를
만들 뿐 자동 shadowing 변환을 하지 않는다. LSP는 origin/lifetime을
표시한다.

**활성화 선행 조건**
lexical identity/coherence theorem, exact syntax, HIR/MIR transport, capture
및 link permutation corpus, formatter/LSP와 target receipt가 필요하다.
제품 lane은 전부 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** lexical scope의 evidence가 call에 명시되고 escape하지
  않으면 그 call만 정확한 local identity를 사용할 수 있다.
- **음성/거부:** 같은 이름의 local witness가 ambient shadowing으로 기존
  call 의미를 바꾸거나 global candidate처럼 보이면 coherence 위반이다.
- **경계:** local evidence를 포획한 closure가 scope 밖으로 나가려 하면
  lifetime/ABI 계약이 없으므로 closure export를 거부한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: 선택할 evidence가 call shape에 드러난다.
def ordered(using intOrder: witness Ord<Int>) -> List<Int> = {
    return sort([3, 1, 2], using intOrder)
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: negative_impl_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-negative_impl_preview_design"></a>

## General negative implementation

> **Feature metadata**
> - Feature ID: `negative_impl_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
특정 type/Trait 조합이 성립하지 않음을 선언해 overlap과 API 의도를
고정하려는 요구를 검토한다. open-world package evolution에서 “현재
positive evidence가 없음”과 “영원히 성립하지 않음”을 구분하지 않으면
downstream extension과 coherence를 깨뜨릴 수 있다.

**제안 표면**
negative impl/conformance의 exact syntax는 미선정이다. 아래는 positive
bound로 허용 영역을 명시하는 현행 대안이다. 양성 검토는 compiler-known
sealed fact, 음성은 foreign open type의 부정, 경계는 새 package version이
positive conformance를 추가하는 경우다.

**정적 판정과 상호작용**
orphan/locality, generic overlap, closed-world proof와 versioning을 닫아야
한다. absence, failed lookup 또는 source order를 negative evidence로
바꾸지 않고 specialization/local witness의 candidate 제거 수단으로
사용하지 않는다.

**평가·소유권·오류**
negative evidence는 runtime value나 branch가 아니며 dispatch 전에
정적으로만 작동한다. contradiction은 terminal diagnostic이고 다른
provider로 fallback하지 않는다. 현재 general form은
`NEGATIVE_IMPL_NOT_CURRENT`이며 product checker는 `NOT_RUN`이다.

**현행 대안과 이행**
positive bound, sealed compiler-known exclusion과 명시적 API 분리가
대안이다. migration은 누락 conformance를 negative declaration으로
자동 만들지 않고 downstream impact를 report한다. API diff는 부정 계약을
breaking change lane으로 다뤄야 한다.

**활성화 선행 조건**
closed-world/orphan policy, overlap solver, package evolution law,
contradiction diagnostics, cross-version corpus와 Design_ ratification 및
target receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** compiler-known sealed universe의 명시적 부정 fact는
  새 구성원이 없는 동일 version에서만 overlap 판정에 사용할 수 있다.
- **음성/거부:** foreign open type에 대한 부정 선언은 미래 conformance를
  가로막고 package authority를 넘으므로 거부한다.
- **경계:** dependency version이 전진해 새 type/conformance가 생기면
  이전 부정 fact를 재사용하지 않고 compatibility 검사를 다시 수행한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: 허용되는 positive capability만 요구한다.
public def encode<T>(value: T) -> Bytes
    where T conforms Encodable
= {
    return value ~ encode()
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: sealed_multimethod_family; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-sealed_multimethod_family"></a>

## Sealed multimethod family

> **Feature metadata**
> - Feature ID: `sealed_multimethod_family`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
둘 이상의 인수 type 조합에 대칭적인 dispatch를 제공하려는 요구를 검토한다.
sealed universe 안에서도 cell overlap, exhaustiveness, visibility와
separate compilation을 결정적으로 처리해야 하며 declaration order가
winner가 되어서는 안 된다.

**제안 표면**
family declaration, case와 call syntax는 미선정이다. 아래는 closed Union과
`match`를 이용한 현행 explicit dispatch 대안이다. 양성 검토는 완전한
finite matrix, 음성은 overlapping cell, 경계는 새 sealed subtype 추가로
matrix residual이 생기는 경우다.

**정적 판정과 상호작용**
sealed universe identity, unique cell selection, visibility, API evolution과
link invariance를 닫아야 한다. ordinary overload, Class virtual slot,
Trait witness와 pattern source order를 multimethod dispatch로 재해석하지
않는다.

**평가·소유권·오류**
모든 argument는 한 번 평가된 후 정적으로 닫힌 dispatch key로 cell을
선택한다. missing/ambiguous cell은 body 실행 전 terminal error이고 다른
overload로 fallback하지 않는다. 전용 diagnostics와 MIR dispatch는
미결이며 제품은 `NOT_RUN`이다.

**현행 대안과 이행**
visitor/double dispatch, named API와 exhaustive match가 대안이다.
migration은 overload를 자동 family로 묶지 않고 matrix와 uncovered cells를
report한다. IDE는 dispatch matrix와 selected cell origin을 표시해야 한다.

**활성화 선행 조건**
finite universe와 total resolution algorithm, exact syntax, evolution
lanes, ambiguity/exhaustiveness corpus, MIR/backend parity와 target receipt가
필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** sealed argument universe의 모든 조합에 정확히 한
  dispatch cell이 있으면 호출은 그 finite matrix의 유일 cell을 선택한다.
- **음성/거부:** cell overlap 또는 uncovered 조합이 있으면 runtime
  fallback 없이 declaration/check 단계에서 거부한다.
- **경계:** sealed subtype이 추가되면 기존 matrix는 자동 완전하다고
  간주하지 않고 새 조합의 coverage를 API evolution 단계에서 재검사한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private type Number = Int | Float64
// 현행 명시적 대안: dispatch cell을 closed match로 드러낸다.
def combine(left: Number, right: Number) -> Float64 = {
    return @match left {
        i: Int => @match right {
            j: Int => i ~ toFloat64() + j ~ toFloat64()
            g: Float64 => i ~ toFloat64() + g
        }
        f: Float64 => @match right {
            j: Int => f + j ~ toFloat64()
            g: Float64 => f + g
        }
    }
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: solver_backed_general_refinement; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-solver_backed_general_refinement"></a>

## Solver-backed general refinement

> **Feature metadata**
> - Feature ID: `solver_backed_general_refinement`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM / PROVIDER / AGENT`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
finite R0보다 풍부한 수학 predicate를 정적으로 증명하려는 요구를
검토한다. solver version, timeout과 host 자원에 따라 build 결과가
달라지지 않도록 proof reproducibility와 `unknown`의 의미를 먼저
고정해야 한다.

**제안 표면**
solver query, proof annotation과 predicate calculus는 미선정이다. 아래는
현행 finite R0와 explicit check 대안이다. 양성 검토는 제한 논리의
certificate, 음성은 비종료/환경 의존 query, 경계는 resource cap에서
`unknown`이 발생하는 경우다.

**정적 판정과 상호작용**
논리 fragment, normalization, termination, resource budget, mutation kill,
provider authority와 API certificate를 닫아야 한다. R0 실패 후 solver로
자동 fallback하거나 dependent capture에 runtime validation을 숨기지
않는다.

**평가·소유권·오류**
정적 proof는 runtime effect가 없고 failure/timeout/unknown을 deterministic
diagnostic으로 구분한다. explicit `check`는 Result를 한 번 반환하며 solver
guess로 성공시키지 않는다. 전용 source diagnostic와 independent product
checker는 미결/`NOT_RUN`이다.

**현행 대안과 이행**
finite R0, named runtime validation과 external provenance-bound proof
artifact가 대안이다. migration은 복잡한 Bool을 자동 refinement로 바꾸지
않고 unsupported predicate를 report한다. IDE는 certificate와 runtime
check를 분리한다.

**활성화 선행 조건**
제한 논리 ratification, version-pinned solver 또는 independently checkable
certificate, deterministic cap, mutation corpus, API serialization과
independent checker receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** 제한 논리 안의 query가 cap 내에서 종료하고 독립
  검증 가능한 certificate를 내면 같은 입력은 같은 refinement fact를 얻는다.
- **음성/거부:** environment·network에 의존하거나 비종료 가능성이 있는
  solver query는 타입 판정의 재현성을 깨므로 거부한다.
- **경계:** cap에 정확히 도달한 query는 성공/실패를 추측하지 않고
  resource-limit 진단을 내며 runtime check로 자동 강등하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: 닫힌 R0 predicate와 명시적 Result 검사.
public type Port = Int where this >= 0 and this <= 65_535
let checked: Result<Port, error RefinementError> = Port::check(raw)
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: specialization_preview_design; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-specialization_preview_design"></a>

## Conformance specialization

> **Feature metadata**
> - Feature ID: `specialization_preview_design`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM / CHECKER`; dependencies: 없음
> - P1 영향: 없음. `TCC-P1-002..008` 7개는 모두 OPEN으로 유지한다.

**검토 목적**
generic 기본 구현보다 구체적인 구현을 선택해 성능과 표현력을 높이려는
요구를 검토한다. overlapping candidates 사이에서 unique maximal
implementation이 존재하고 substitution·import·link 순서가 결과를
바꾸지 않아야 한다.

**제안 표면**
specialization relation, declaration과 visibility syntax는 미선정이다.
아래는 의도를 named API로 분리하는 현행 대안이다. 양성 검토는 엄밀한
partial order의 유일 최대, 음성은 incomparable pair, 경계는 generic
alias 정규화 후 두 candidate가 동률이 되는 경우다.

**정적 판정과 상호작용**
ordering calculus, overlap, termination, coherence와 public metadata를
닫아야 한다. numeric priority, declaration order, AUTO/VIA, local witness와
fixed operator dispatch를 winner 근거로 사용할 수 없다.

**평가·소유권·오류**
selected implementation identity는 type check에서 고정되어 MIR runtime
relookup이 0이어야 한다. incomparable/unstable selection은 terminal
diagnostic이고 less-specific body로 fallback하지 않는다. 현행은
`SPECIALIZATION_NOT_CURRENT`; 제품 checker/runtime은 `NOT_RUN`이다.

**현행 대안과 이행**
exact conformance, explicit named fast path와 caller가 선택하는 strategy가
대안이다. migration은 overload를 자동 specialization hierarchy로 만들지
않고 overlap matrix를 report한다. IDE는 selected origin을 명시한다.

**활성화 선행 조건**
formal partial order, substitution stability와 termination proof,
cross-package mutation/permutation corpus, closed HIR/MIR metadata,
diagnostics와 target receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** substitution 뒤 partial order에 유일한 maximal
  implementation이 있으면 그 identity를 HIR/MIR에 고정한다.
- **음성/거부:** incomparable 후보가 둘 이상이면 source/import order로
  고르거나 덜 구체적인 body로 fallback하지 않는다.
- **경계:** generic substitution이 원래 순서를 뒤집거나 동률을 만들면
  declaration-time 결과를 재사용하지 않고 ambiguity를 보고한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: fast path 선택이 API 이름에 드러난다.
public def encodeBytesFast(value: Bytes) -> Bytes = {
    return value
}
public def encodeGeneric<T>(value: T) -> Bytes
    where T conforms Encodable
= {
    return value ~ encode()
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: structural_prototype_extension; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-structural_prototype_extension"></a>

## Structural prototype extension

> **Feature metadata**
> - Feature ID: `structural_prototype_extension`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
명목 선언을 수정하지 않고 같은 shape의 값에 동작을 확장하려는 요구를
검토한다. shape match가 nominal conformance, witness, owner identity와 API
stability를 제조하면 separate compilation과 evolution이 불안정해지므로
static-first nominal 경계를 유지한다.

**제안 표면**
structural target와 activation syntax는 미선정이다. 아래는 exact nominal
named extension이라는 현행 대안이다. 양성 검토는 closed explicit shape
contract, 음성은 ambient duck typing, 경계는 field rename 또는 visibility
변화로 shape가 달라지는 경우다.

**정적 판정과 상호작용**
applicability, overlap, termination, visibility와 API digest를 닫아야 한다.
shape는 Trait witness, subtype, owner나 dynamic fallback을 만들지 않고
prototype delta 및 generic extension target과도 별도 mechanism이다.

**평가·소유권·오류**
선택된 extension call은 receiver를 한 번 평가하고 static member를
호출한다. shape drift/ambiguity는 body 실행 전 terminal error이며 nominal
extension으로 fallback하지 않는다. 현행 후보는
`STRUCTURAL_PROTOTYPE_EXTENSION_REQUIRES_FEATURE_GATE`로 거부되지만 source
gate는 존재하지 않는다.

**현행 대안과 이행**
named exact extension set과 explicit Trait conformance가 대안이다.
migration은 duck-typed call을 자동 nominal witness로 만들지 않고 required
shape와 owner를 report한다. LSP navigation은 nominal origin만 따른다.

**활성화 선행 조건**
closed applicability/coherence algorithm, exact syntax, shape evolution/API
digest, link-order mutation corpus, formatter/LSP와 target receipt가
필요하다. 제품 lane은 전부 `NOT_RUN`이다.

**설계 검토 시나리오**
- **양성 전제·기대:** 명시적으로 닫힌 shape와 owner가 하나의 structural
  contract를 만족하면 유일한 extension identity를 선택한다.
- **음성/거부:** ambient duck typing이나 field 이름 우연만으로 extension을
  활성화하면 nominal evidence와 visibility를 우회하므로 거부한다.
- **경계:** field rename 또는 visibility 축소로 shape가 달라지면 기존
  selection을 유지하지 않고 API compatibility failure로 처리한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: target은 exact nominal Int다.
public extension Int as metric {
    +def centimeters() -> Length = {
        return Length!(value: self, unit: Unit::centimeter)
    }
}
use Int::metric
let length = 12 ~ centimeters()
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: use_site_projection_dmad; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-use_site_projection_dmad"></a>

## Use-site generic projection

> **Feature metadata**
> - Feature ID: `use_site_projection_dmad`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `TYPE_SYSTEM / CHECKER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
generic 사용 지점에서 읽기/쓰기 방향을 제한하려는 Java/Kotlin 계열의
개념을 Deeplus 책임 모델에 맞게 검토한다. wildcard capture가 ownership과
API identity를 숨기지 않게 하고, Phase A의 Trait-only variance와
role-named facade를 우선한다.

**제안 표면**
projection과 capture의 exact Deeplus spelling은 미선정이다. 아래는
declaration-site covariant facade Trait이라는 현행 대안이다. 양성 검토는
read-only producer, 음성은 projected mutable consumer, 경계는 capture가
public return type나 owner 이동을 통과하는 경우다.

**정적 판정과 상호작용**
variance calculus, capture conversion, substitution, lifetime/ownership과
API digest를 닫아야 한다. Class/container variance를 암시하지 않고
invariant mutable owner를 projected view로 자동 바꾸지 않는다.

**평가·소유권·오류**
projection은 runtime wrapper나 cast를 숨겨 만들지 않아야 한다.
incompatible read/write는 정적 diagnostic이고 runtime failure나 wildcard
fallback이 아니다. 전용 source diagnostic와 ABI residue는 미결이며
제품 checker는 `NOT_RUN`이다.

**현행 대안과 이행**
role-named facade Trait, declaration-site Trait variance와 invariant generic이
대안이다. migration은 wildcard를 추측해 넣지 않고 read/write use를
inventory한다. signature help는 captured type과 owner limitation을
명시해야 한다.

**활성화 선행 조건**
normative variance/capture calculus, exact syntax, substitution/ownership
algorithm, ABI/API compatibility corpus, formatter/LSP와 migration plan,
target receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** read-only producer projection은 쓰기 권한 없이
  선언된 covariant bound 안의 값만 관측하게 한다.
- **음성/거부:** projected mutable consumer에 값을 쓰거나 owner를
  이동시키면 capture boundary를 깨므로 정적으로 거부한다.
- **경계:** capture가 public API나 closure 밖으로 escape할 때 exact
  lifetime/ABI identity가 없으면 projection을 저장 가능한 타입으로 만들지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: 읽기 역할을 declaration-site Trait로 명시한다.
public trait Source<out T> {
    +def next+() -> Option<T>
        throws Never
        effects {}
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->
