<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# Preview Design: 동시성, FFI 및 runtime

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

이 장의 열다섯 기능은 모두 `PREVIEW_DESIGN/nonactivatable`이다. 선택된
Recovery probe와 후보 철자는 current source가 아니며, exact syntax가
미선정인 기능의 코드는 현행 이름 있는 declaration 또는 explicit API만
사용한다. 설명·schema·fixture는 activation, 구현 완료나 product support가
아니다. 15개 제품 lane은 모두 `NOT_RUN`이고 OPEN P1은 그대로 유지된다.

<!-- deeplus-preview-feature-example: async_callable_literal_profile; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-async_callable_literal_profile"></a>

## Asynchronous callable literal profile

> **Feature metadata**
> - Feature ID: `async_callable_literal_profile`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / TYPE_SYSTEM / RUNTIME`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
이름 있는 declaration 없이 중단 가능한 callable value를 구성하려는
요구를 검토한다. ordinary closure가 동기 호출이라는 current 법칙을
유지하면서 capture ownership, return channel, `await`, Cancellation,
isolation과 callable ABI를 한 identity에 담을 수 있어야 한다.

**제안 표면**
`#async{ => ... }` 계열 후보는 존재하지만 exact EBNF, parameter/result
형식과 ABI가 미선정이다. 아래는 거부되는 설계 probe다. 양성 검토는
명시적 capture와 structured owner, 음성은 ambient await/borrow escape,
경계는 호출하지 않은 literal이 scope 밖으로 이동하거나 actor를 건너는
경우다.

**정적 판정과 상호작용**
call-shape, capture descriptor, error/effect/cancellation, isolation,
return ownership과 task owner를 닫아야 한다. named `def#async`, restricted
`spawn async` body와 ordinary closure는 각각 별도 current owner이며,
marker가 서로를 암시적으로 변환하지 않는다.

**평가·소유권·오류**
literal 생성 시 capture는 한 번 확정되고 호출마다 어떤 owner가 소비되는지
`once/mut/shared` law가 필요하다. suspension을 가로지르는 borrow와 cleanup,
failure/Cancellation ordering을 보존해야 한다. 현행은
`ASYNC_CALLABLE_LITERAL_NOT_CURRENT`로 거부되며 parser/checker/runtime은
`NOT_RUN`이다.

**현행 대안과 이행**
이름 있는 `def#async` declaration과 lexical `spawn async` task body가
대안이다. migration은 named function을 literal로 inline하거나 ordinary
closure에 async marker를 자동 추가하지 않는다. LSP는 capture, suspension,
error와 cancellation channel을 별도로 표시해야 한다.

**활성화 선행 조건**
exact root/grammar와 recovery, callable ABI와 capture/ownership calculus,
HIR/MIR lowering, cancellation/cleanup corpus, formatter/LSP와 xVM/LLVM
target receipt가 필요하다. 정적 예시는 제품 evidence가 아니다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
// 비활성 설계 probe: current parser는 이 callable literal을 거부한다.
let loader = #async{ => await loadProfile() }
```

<!-- deeplus-preview-feature-example: async_comprehension; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-async_comprehension"></a>

## Async comprehension

> **Feature metadata**
> - Feature ID: `async_comprehension`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
비동기 source의 transform, filter와 collection을 하나의 표현으로 쓰려는
요구를 검토한다. source order, finiteness, backpressure, source/transform
error union, Cancellation과 partial-result cleanup을 표면 뒤에 숨기지
않는 것이 우선이다.

**제안 표면**
comprehension syntax와 결과 collection/stream identity는 미선정이다.
아래는 current `AsyncCollector` stdlib profile을 사용하는 explicit
대안이다. 양성 검토는 finite evidence와 named async transform, 음성은
unbounded source를 List로 수집, 경계는 첫 failure와 pending cancellation이
동시에 관측되는 경우다.

**정적 판정과 상호작용**
current collector는 sequential/source-order/fail-fast/cancel-pending/
buffer-one 정책과 정확한 `ES | ET` error set을 요구한다. comprehension이
`for await`, generator, ordinary List comprehension이나 async callable
literal을 자동 활성화하지 않아야 한다.

**평가·소유권·오류**
source element는 한 번씩 source order로 소비되고 transform failure 시
pending work를 취소한 뒤 cleanup barrier를 지난다. 전체 성공 전 partial
List를 publish하지 않고 Cancellation을 Error로 접지 않는다. 전용 syntax
diagnostic는 미결이며 product collector/runtime은 `NOT_RUN`이다.

**현행 대안과 이행**
`for await` statement와 `AsyncCollector::list`가 대안이다. migration은
loop를 comprehension으로 자동 축약하거나 policy를 추측하지 않고
finiteness/error/cancellation 책임을 report한다. IDE는 source와 transform
failure를 분리한다.

**활성화 선행 조건**
exact grammar, collector/result identity, ownership/effect/cancellation
law, deterministic lowering, positive/negative/boundary execution corpus와
target receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** finite evidence가 있는 async source와 named transform의
  error union을 알고 있으면 source order로 처리해 완성된 결과만 publish한다.
- **음성/거부:** unbounded source를 암시적으로 `List`로 수집하거나 transform
  failure를 누락하면 termination과 오류 계약이 없으므로 거부한다.
- **경계:** 첫 failure와 pending Cancellation이 경합하면 정해진 primary
  outcome과 cleanup barrier를 보존하고 partial collection을 노출하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: policy와 named transform이 source에 드러난다.
public def#async collectProfiles(ids: AsyncSequence<UserId, IOError>) -> List<Profile>
    throws IOError | NetworkError
= {
    return await AsyncCollector::list(
        source: ids,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: automatic_observation_tracking; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-automatic_observation_tracking"></a>

## Automatic observation tracking

> **Feature metadata**
> - Feature ID: `automatic_observation_tracking`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
반응형 갱신에 필요한 dependency를 실행 중 자동 포착하려는 요구를
검토한다. hidden read가 authority를 얻거나 mutation 시점마다 invalidation
graph가 비결정적으로 바뀌지 않게 observation identity, lifetime, cycle과
actor isolation을 닫아야 한다.

**제안 표면**
자동 tracking scope와 API는 미선정이다. 아래는 application-defined
subscription handle을 명시적으로 보관하는 current-style 대안이다.
양성 검토는 dependency와 cleanup owner가 명시된 경우, 음성은 ambient
global capture, 경계는 observer callback이 source를 다시 mutate해 cycle을
만드는 경우다.

**정적 판정과 상호작용**
observed source identity, dependency edge, mutation invalidation, callback
effects, isolation과 subscription owner를 닫아야 한다. Shared handle이
mutable alias 권위를 만들지 않고 actor mailbox, provider lookup 또는
reflection으로 dependency를 자동 확대하지 않아야 한다.

**평가·소유권·오류**
registration은 dependency를 한 번 resolve하고 token owner가 unregister/
cleanup을 책임진다. cycle, callback failure와 concurrent invalidation의
order가 deterministic이어야 하며 failed registration은 partial edge를
publish하지 않는다. 전용 diagnostic와 MIR observation event는
미결/`NOT_RUN`이다.

**현행 대안과 이행**
explicit observer registration, named event/message와 scoped subscription
object가 대안이다. migration은 ordinary property read를 자동 dependency로
바꾸지 않고 registration/cleanup 누락을 report한다. tooling은 dependency
graph와 cycle을 시각화해야 한다.

**활성화 선행 조건**
closed invalidation/cycle model, owner/isolation proof, callback error policy,
MIR event와 reproducible concurrent mutation corpus, formatter/LSP와 target
receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** 명시된 observation scope가 dependency edge와 cleanup
  token을 소유하면 mutation 뒤 필요한 observer만 결정적으로 갱신한다.
- **음성/거부:** ordinary read를 ambient global dependency로 포획하거나
  observer가 숨은 authority를 얻으면 ownership/isolation을 우회하므로 거부한다.
- **경계:** observer callback이 관측 source를 다시 mutate해 cycle을 만들면
  cycle policy에 따른 단일 진단/terminal outcome 없이 재귀 실행하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: application API가 dependency와 cleanup token을 노출한다.
let subscription = profile ~ subscribe(observer: handleProfileChange)
defer subscription ~ close()
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: c_aggregate; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-c_aggregate"></a>

## C aggregate mapping

> **Feature metadata**
> - Feature ID: `c_aggregate`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
C struct/union과 Deeplus value를 명시적 FFI profile로 교환하려는 요구를
검토한다. semantic field identity를 field order, padding, alignment,
bitfield와 target ABI layout에 동일시하지 않고 ownership/provenance까지
별도 mapping으로 고정해야 한다.

**제안 표면**
aggregate declaration/import/mapping API는 미선정이다. 아래는 bytes를
명시적으로 decode하는 named wrapper 대안이다. 양성 검토는 target-bound
layout descriptor, 음성은 `Plain` Record를 자동 C-safe로 취급,
경계는 packing/alignment/endianness가 target마다 다른 aggregate다.

**정적 판정과 상호작용**
field representation, offset/padding, alignment, endian, union active member,
ownership과 ABI identity를 닫아야 한다. Deeplus schema/Record/bitfield
declaration만으로 C layout, raw value나 serialization witness를 만들 수
없다. 최소 FFI surface와도 별도 feature다.

**평가·소유권·오류**
encode/decode field는 정해진 order로 한 번 평가되고 bounds/layout mismatch
시 partial value를 publish하지 않는다. pointer/resource field의 owner와
cleanup은 descriptor에 명시되어야 한다. successor diagnostic와 native
lowering은 미결이고 관련 product lane은 `NOT_RUN`이다.

**현행 대안과 이행**
explicit `Bytes` codec, generated typed wrapper와 C-side adapter가 대안이다.
migration은 Record를 aggregate로 자동 annotate하지 않고 target ABI,
padding과 owner 공백을 report한다. tooling은 semantic/API layout과
foreign layout을 분리한다.

**활성화 선행 조건**
target ABI authority, versioned representability/layout schema, bindgen
round-trip, provenance/cleanup law, multi-target mutation corpus와 native
artifact-bound receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** target-bound descriptor가 field offset, alignment,
  endian과 owner direction을 모두 고정하면 aggregate를 한 번 encode/decode한다.
- **음성/거부:** `Plain` Record라는 이유만으로 C layout-safe로 간주하거나
  target padding을 추측하면 ABI identity가 없으므로 거부한다.
- **경계:** 같은 선언의 packing이 target마다 다르면 semantic Record
  identity와 ABI descriptor를 분리하고 target receipt 없는 export를 막는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: foreign layout을 Record identity로 추정하지 않는다.
private schema PointWire {
    x: Int32
    y: Int32
}
let decoded: Result<PointWire, error DecodeError> = decodePointWire(bytes)
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: c_stored_callback; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-c_stored_callback"></a>

## C stored callback

> **Feature metadata**
> - Feature ID: `c_stored_callback`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
C library가 registering call 종료 후에도 callback과 context를 보관하는
경계를 안전하게 표현하려는 요구를 검토한다. capture lifetime, foreign
thread, reentrancy, revoke, unwind와 cleanup owner가 ordinary synchronous
closure보다 길고 복잡하므로 별도 profile이어야 한다.

**제안 표면**
registration/revoke/context API와 source signature는 미선정이다. 아래는
application wrapper가 explicit registration owner를 반환하는 대안이다.
양성 검토는 exactly-once revoke와 owned context, 음성은 stack borrow
capture, 경계는 callback 실행과 revoke/foreign shutdown이 경합하는 경우다.

**정적 판정과 상호작용**
callback ABI, capture descriptor, lifetime, thread/actor isolation,
reentrancy, unwind와 token identity를 닫아야 한다. ordinary callable이나
borrowed closure를 장수 callback으로 자동 변환하지 않고 hidden global
registry를 authority로 삼지 않는다.

**평가·소유권·오류**
registration 성공 전에는 callback을 publish하지 않고 실패 시 capture
owner를 반환/정리한다. success 후 token이 revoke와 final cleanup을
정확히 한 번 소유한다. late callback, callback failure와 foreign unwind
정책은 미결이며 compiler/runtime/native 실행은 `NOT_RUN`이다.

**현행 대안과 이행**
synchronous FFI callback, explicit opaque handle와 owner object wrapper가
대안이다. migration은 closure를 stored callback으로 자동 escape시키지
않고 capture/threads/revoke inventory를 제공한다. IDE는 registration
lifetime과 cleanup path를 표시한다.

**활성화 선행 조건**
owner token API, callback ABI와 provenance, unwind/reentrancy/race policy,
MIR callback identity, concurrency mutation corpus와 native target receipt가
필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** owned context와 registration token이 callback lifetime을
  소유하고 revoke가 정확히 한 번 성공하면 이후 callback은 진입하지 않는다.
- **음성/거부:** stack borrow를 포획해 foreign code에 저장하거나 cleanup
  owner 없이 closure를 escape시키면 use-after-lifetime 위험으로 거부한다.
- **경계:** callback 실행과 revoke/foreign shutdown이 경합하면 실행 완료와
  revoke 완료의 허용 순서를 하나로 정의하고 이중 cleanup을 금지한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: wrapper가 registration lifetime과 cleanup을 소유한다.
let registration: CallbackRegistration =
    registerOwnedCallback(callback: handleEvent)
defer registration ~ close()
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: c_variadic; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-c_variadic"></a>

## C variadic call profile

> **Feature metadata**
> - Feature ID: `c_variadic`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
기존 C variadic API를 제한된 foreign profile에서 호출하려는 요구를
검토한다. C default argument promotion, sentinel/count와 ABI별 register/
stack lowering은 Deeplus repeated positional parameter와 다른 책임이므로
명시적으로 분리해야 한다.

**제안 표면**
variadic parameter/call spelling과 sentinel/count API는 미선정이다. 아래는
고정 arity typed wrapper 대안이다. 양성 검토는 closed representable type
set과 count, 음성은 arbitrary Deeplus value 전달, 경계는 format string과
argument type/arity가 불일치하는 경우다.

**정적 판정과 상호작용**
promotion table, permitted scalar/pointer set, arity/sentinel contract,
ownership, ABI와 unwind를 닫아야 한다. `values...: T`, named rest와 tuple
unfold를 C varargs로 해석하지 않고 c_aggregate/stored callback profile도
자동 포함하지 않는다.

**평가·소유권·오류**
fixed prefix와 each variadic argument는 왼쪽에서 오른쪽으로 한 번
평가된다. representability/format mismatch는 foreign call 전에 거부되고
owner를 넘기지 않는다. dynamic sentinel scan이나 unchecked promotion은
허용 후보가 아니다. 전용 diagnostics/backend는 미결/`NOT_RUN`이다.

**현행 대안과 이행**
typed fixed-arity C shim 또는 Deeplus named wrapper가 대안이다. migration은
rest parameter를 varargs로 자동 변환하지 않고 call-site type/count를
report한다. signature help는 각 promoted foreign type을 보여야 한다.

**활성화 선행 조건**
closed type/promotion table, ABI matrix, format/sentinel policy, ownership/
unwind law, negative corpus와 여러 native target의 reproducible receipt가
필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** closed promotion table과 명시적 count/sentinel이 모든
  argument의 foreign type을 고정하면 source order로 한 번 평가해 호출한다.
- **음성/거부:** 임의 Deeplus value를 default promotion하거나 format
  string만 믿고 unchecked call을 만들면 representability가 없어 거부한다.
- **경계:** format가 요구한 arity/type과 실제 variadic tail이 다르면
  foreign call 전에 실패하고 평가된 move owner를 전달하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: 고정 arity wrapper가 foreign contract를 닫는다.
public def logThree(format: String, a: Int, b: Int, c: Int) -> Unit
    effects {io}
= {
    typedLog3(format, a, b, c)
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: directed_coroutine_group; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-directed_coroutine_group"></a>

## Directed coroutine group

> **Feature metadata**
> - Feature ID: `directed_coroutine_group`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
여러 coroutine 사이의 생산/소비 방향과 lifetime을 하나의 structured
owner 아래 표현하려는 요구를 검토한다. 방향성만 추가하고 detached child,
implicit channel, cancellation leak이나 cleanup 생략을 허용하지 않아야
한다.

**제안 표면**
group/direction source route와 protocol API는 미선정이다. 아래는 current
`task scope`와 child handle을 명시하는 대안이다. 양성 검토는 lexical
owner와 compatible direction, 음성은 detached/escaping child, 경계는
한 child failure가 반대 방향의 blocked child를 취소하는 경우다.

**정적 판정과 상호작용**
direction compatibility, endpoint identity, structured scope, effect/error/
cancellation, send/request와 ownership transfer를 닫아야 한다. ordinary
task group, actor mailbox와 session protocol을 암시적으로 directed
coroutine으로 바꾸지 않는다.

**평가·소유권·오류**
child는 lexical spawn index로 등록되고 scope exit 전에 terminal/cleanup이
끝나야 한다. failure와 cancellation primary/suppressed order는 scheduler
order와 무관해야 하며 endpoint owner를 유실하지 않는다. 현행은
`DIRECTED_COROUTINE_GROUP_REQUIRES_FEATURE_GATE`지만 usable source gate는
없고 제품은 `NOT_RUN`이다.

**현행 대안과 이행**
`task scope`, current task group, explicit channel과 actor protocol이
대안이다. migration은 tasks를 자동 directed group으로 묶지 않고 owner,
escape와 cancellation graph를 report한다. debugger는 child/endpoint
관계를 표시해야 한다.

**활성화 선행 조건**
exact grammar, endpoint/owner typestate, cancellation/cleanup equations,
MIR identity, race/deadlock mutation corpus와 cross-backend receipt가
필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** lexical group이 producer/consumer endpoint와 모든
  child를 소유하면 scope 종료에서 정해진 방향으로 join·cleanup한다.
- **음성/거부:** detached child나 endpoint가 group 밖으로 escape하면
  cancellation과 cleanup owner를 잃으므로 거부한다.
- **경계:** send와 cancellation이 경합하면 endpoint state commit 전/후의
  한 결과만 관측하고 message와 owner를 동시에 잃지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
// 현행 명시적 대안: 모든 child의 lexical owner와 join이 보인다.
task scope {
    let producer = spawn async { => await produce() }
    let consumer = spawn async { => await consume() }
    await producer
    await consumer
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: dyn_inspection; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-dyn_inspection"></a>

## Privileged Dyn inspection

> **Feature metadata**
> - Feature ID: `dyn_inspection`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
open-world runtime 값의 제한된 metadata나 shape를 조사하려는 요구를
검토한다. inspection 결과가 static type, label, conformance, witness 또는
authority를 제조하지 않고 data disclosure와 ownership/effect 경계를
명시해야 한다.

**제안 표면**
privileged inspection service와 checked result API는 미선정이다. 아래는
closed Union과 exhaustive match라는 current 대안이다. 양성 검토는
capability-bound closed result, 음성은 ambient reflection, 경계는 erased
payload가 resource/private field를 포함하는 경우다.

**정적 판정과 상호작용**
inspection capability, allowed metadata, result carrier, visibility/redaction,
type erasure와 Trait evidence coherence를 닫아야 한다. failed static
resolution이 inspection으로 fallback하지 않고 dynamic attach/Dyn-RCTS와
자동 연결되지 않는다.

**평가·소유권·오류**
subject는 한 번 borrow되고 inspection은 declared effect/authority만
사용한다. denial/failure는 typed closed result이며 payload owner를
소비하지 않는다. 현행 candidate는
`DYN_INSPECTION_REQUIRES_FEATURE_GATE`로 거부되지만 source gate는 없고
runtime/debugger execution은 `NOT_RUN`이다.

**현행 대안과 이행**
closed Union/Enum, explicit schema, match와 audited named adapter가
대안이다. migration은 dynamic lookup을 자동 reflection으로 바꾸지 않고
required metadata/authority를 report한다. debugger와 program API 권위도
분리해야 한다.

**활성화 선행 조건**
capability/redaction model, closed result/representation, ownership/effect
law, MIR inspection event, privacy/security review, failure corpus와 target
receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** 명시 capability가 허용한 metadata만 redacted closed
  result로 반환하고 inspected value의 owner와 static type은 바꾸지 않는다.
- **음성/거부:** ambient reflection이 private field, witness 또는 authority를
  제조하면 visibility와 conformance를 우회하므로 거부한다.
- **경계:** erased descriptor가 현재 version에서 알려지지 않으면 구조를
  추측하지 않고 typed unknown/mismatch를 반환한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
// 현행 명시적 대안: runtime alternatives를 closed Union으로 고정한다.
private type Payload = Int | String
let text = @match payload {
    number: Int => number ~ toString()
    string: String => string
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: dynamic_unsafe_quarantine_scope_msp; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-dynamic_unsafe_quarantine_scope_msp"></a>

## Dynamic/unsafe quarantine scope

> **Feature metadata**
> - Feature ID: `dynamic_unsafe_quarantine_scope_msp`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / PARSER / CHECKER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
불가피한 legacy, dynamic 또는 unsafe 작업의 authority와 escape를 하나의
lexical owner에 가두려는 수용된 최소 설계다. safety laundering 없이
typed immutable 결과만 내보내고 outer mutation, suspension과 resource/
pointer/borrow/closure/task/actor escape를 금지한다.

**제안 표면**
`@scope#dynamic` 또는 `@scope#unsafe`와 typed export는 Recovery probe로만
선택되어 있고 activatable route는 없다. 아래는 거부되는 비활성 설계
예시다. 양성 검토는 plain typed immutable export, 음성은 pointer/resource
escape, 경계는 closure가 quarantined authority를 capture하는 경우다.

**정적 판정과 상호작용**
lexical scope identity, provenance, authority accounting, export type,
outer-state mutation과 escape graph를 닫아야 한다. quarantine이 FFI,
Dyn-RCTS, inspection 또는 unsafe effect atom을 자동 활성화하거나 static
proof로 바꾸지 않는다.

**평가·소유권·오류**
body는 별도 authority owner 아래 평가되고 모든 local cleanup이 끝난 뒤
허용 export만 commit한다. 실패·Cancellation·suspension에서 export 0,
resource residue 0이어야 한다. current Recovery는
`QUARANTINE_SCOPE_NOT_ACTIVATABLE`를 내며 semantic AST/HIR/MIR 0이다.

**현행 대안과 이행**
typed wrapper, explicit FFI boundary와 named validation API가 대안이다.
migration은 legacy block을 자동 quarantine으로 감싸지 않고 outer write,
escape와 authority를 report한다. formatter는 offending spelling을
lossless하게 보존한다.

**활성화 선행 조건**
provenance/authority calculus, exact escape/suspension proof, MIR owner와
cleanup, deterministic diagnostics, xVM/LLVM differential corpus,
security review와 별도 Design_ activation이 필요하다. 제품은 `NOT_RUN`이다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/quarantine-scope.json -->
```deeplus
// 비활성 Recovery probe: current source에서는 반드시 거부된다.
@scope#dynamic {
    let value: Int = inspect(payload)
} -> $value: Int
```

<!-- deeplus-preview-feature-example: module_static_entrance; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-module_static_entrance"></a>

## Module static entrance

> **Feature metadata**
> - Feature ID: `module_static_entrance`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE / RUNTIME`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
module load 시 한 번 수행되는 initializer block을 표현하려는 요구를
검토한다. multi-file module의 storage identity, import order/cycle,
failure/retry, effects, cleanup과 unload가 정해지지 않은 상태에서 hidden
load-time execution을 current로 만들 수 없다.

**제안 표면**
과거 `static { ... }` 후보는 있으나 exact lifecycle contract와 successor
route는 미선정이다. 아래는 explicit initialization function 대안이다.
양성 검토는 caller가 phase/order를 소유하는 경우, 음성은 import 시 hidden
IO, 경계는 두 module의 cyclic initializer와 partial publication이다.

**정적 판정과 상호작용**
module/storage identity, file aggregation, deterministic dependency order,
effects/errors, visibility와 API digest를 닫아야 한다. top-level binding,
class/function/effectful static과 entry execution을 자동 합치지 않는다.

**평가·소유권·오류**
initializer가 생긴다면 한 번 평가하고 full success 전 export를 publish하지
않아야 한다. failure, retry/poison, rollback과 reverse cleanup을 명시해야
한다. current probe는 `MODULE_STATIC_INITIALIZER_NOT_CURRENT`; parser/MIR/
link/runtime은 모두 `NOT_RUN`이다.

**현행 대안과 이행**
explicit `initializeModule()`을 entry 또는 application lifecycle에서
호출한다. migration은 block을 top-level let이나 entry로 자동 이동하지
않고 dependency/effect/cleanup graph를 report한다. IDE는 module load
graph와 ordinary call graph를 분리한다.

**활성화 선행 조건**
module lifecycle authority, exact grammar, cycle/failure/retry algorithm,
storage/API/link identity, clean-build/multi-file mutation corpus와 target
execution receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** application lifecycle이 module initializer의 phase,
  dependency와 effect를 명시하면 성공 뒤 완전한 state만 publish한다.
- **음성/거부:** import만으로 hidden IO를 실행하거나 partial state를 다른
  module에 보이면 초기화 순서와 오류 책임이 없어 거부한다.
- **경계:** 두 module initializer가 cycle을 이루면 파일/link 순서로
  끊지 않고 cycle diagnostic과 rollback/cleanup 정책을 요구한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/source-roles.json -->
```deeplus
// 현행 명시적 대안: 초기화 시점과 오류가 caller signature에 드러난다.
public def initializeModule() -> Cache
    throws IOError
    effects {io}
= {
    return loadCache()
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: prototype_delta; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-prototype_delta"></a>

## Prototype delta

> **Feature metadata**
> - Feature ID: `prototype_delta`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
기존 값에서 다른 nominal/prototype shape로 delta construction을 수행하려는
요구를 검토한다. current `!{}`/`!!{}`는 exact same nominal type derivation
이므로 target owner 추론, structural shape change와 rollback을 섞지
않아야 한다.

**제안 표면**
rooted target syntax와 formation API는 미선정이다. 아래는 current
same-type shallow derivation 대안이다. 양성 검토는 explicit target
descriptor와 construction row, 음성은 shape로 owner 추론, 경계는 field
evaluation 중 failure와 old/new resource ownership이다.

**정적 판정과 상호작용**
target identity, visible ConstructionRow, field mapping/default, validation,
ownership, structural/nominal conformance와 API residue를 닫아야 한다.
same-type derivation, schema materialization, structural extension과
자동 통합하지 않는다.

**평가·소유권·오류**
base와 supplied field는 한 번씩 정해진 order로 평가되고 full validation
후 한 번 publish한다. failure는 old value와 uncommitted resources를
정확히 보존/cleanup해야 한다. 현행 candidate는
`PROTOTYPE_DELTA_REQUIRES_FEATURE_GATE`지만 source gate는 없고 제품은
`NOT_RUN`이다.

**현행 대안과 이행**
named target constructor와 `source!{...}`/`source!!{...}` same-type
derivation이 대안이다. migration은 derivation을 cross-type delta로
확대하지 않고 target/owner/field mapping을 report한다. IDE는 formation
plan을 표시해야 한다.

**활성화 선행 조건**
exact rooted syntax, owner/formation plan, transactional cleanup equations,
validation/API metadata, positive/failure mutation corpus와 backend receipt가
필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** source와 target nominal identity, field mapping과
  constructor plan이 명시되면 모든 validation 성공 뒤 target만 publish한다.
- **음성/거부:** 비슷한 field shape만으로 target owner나 constructor를
  추론하면 structural authority를 발명하므로 거부한다.
- **경계:** 중간 field 생성이 실패하면 이미 만든 target-owned resource를
  역순 cleanup하고 source owner는 계약에 따라 보존한다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: exact same nominal User만 shallow derive한다.
let renamed = user!{
    name: "Lee"
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: session_protocol_lite_provider; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-session_protocol_lite_provider"></a>

## Session protocol lite provider

> **Feature metadata**
> - Feature ID: `session_protocol_lite_provider`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `PROVIDER`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
actor message sequence에 lightweight protocol-state evidence를 공급하려는
tool/provider 설계를 검토한다. current actor protocol은 handler shape를
검사하지만 session progression, distributed delivery나 exactly-once를
보장하지 않으므로 두 계약을 혼동하지 않아야 한다.

**제안 표면**
core syntax는 없고 provider input/output/evidence API도 미선정이다.
아래는 current actor protocol을 명시하는 대안이다. 양성 검토는 versioned
finite protocol과 terminal state, 음성은 illegal transition/hidden retry,
경계는 cancellation 또는 mailbox rejection 중 protocol state commit이다.

**정적 판정과 상호작용**
protocol identity, duality, transition totality/linearity, handler
conformance, actor mailbox policy와 receiver closure를 닫아야 한다. provider
evidence가 core syntax, delivery guarantee, dynamic capacity나 witness를
자동 만들지 않는다.

**평가·소유권·오류**
transition은 successful send/request commit에만 한 번 진행하고 rejected
enqueue에는 sequence/state commit이 없어야 한다. Cancellation, mailbox
error와 handler error를 분리하며 cleanup terminal을 보존한다. provider와
actor product lanes은 `NOT_RUN`이다.

**현행 대안과 이행**
current actor protocol, explicit state Enum과 UML/provider-generated ordinary
source가 대안이다. migration은 send/request를 자동 session화하지 않고
transition inventory를 report한다. IDE는 current state와 legal next
messages를 evidence 층으로 표시한다.

**활성화 선행 조건**
versioned evidence schema, duality/linearity checker, cancellation terminal
law, MIR correlation, provider provenance와 target-bound actor corpus가
필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** versioned finite protocol의 양 endpoint가 dual이고
  현재 state에서 message 하나가 합법이면 enqueue와 state를 함께 commit한다.
- **음성/거부:** illegal transition, hidden retry 또는 message 순서 생략은
  protocol evidence와 actor mailbox 의미를 깨므로 거부한다.
- **경계:** mailbox rejection과 Cancellation이 경합하면 protocol state,
  message owner와 terminal outcome이 하나의 correlation identity로 남는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
// 현행 명시적 대안: message set만 고정하며 session 진행을 암시하지 않는다.
public protocol CounterProtocol {
    send add(value: Int)
    request current() -> Int
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: state_machine_source_syntax; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-state_machine_source_syntax"></a>

## State-machine source syntax

> **Feature metadata**
> - Feature ID: `state_machine_source_syntax`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
state와 transition을 직접 언어 표면에서 선언하려는 요구를 검토한다.
state identity, transition totality, reentrancy, actor isolation, effects/
errors와 persistence가 닫히지 않은 상태에서 UML provider output을 새
syntax authority로 오인하지 않아야 한다.

**제안 표면**
current-compatible state-machine declaration syntax는 미선정이다. 아래는
Enum과 exhaustive match라는 explicit 대안이다. 양성 검토는 finite state와
total transition, 음성은 hidden transition/effect, 경계는 concurrent
event와 persistence restore가 같은 state를 갱신하는 경우다.

**정적 판정과 상호작용**
state/transition IDs, event payload, guard/effect order, totality,
reentrancy/isolation과 schema evolution을 닫아야 한다. actor, session
provider, UML tooling과 ordinary match가 source order나 code generation으로
새 language feature를 만들지 않는다.

**평가·소유권·오류**
event와 active state는 한 번 읽고 transition body 성공 후 next state를
commit해야 한다. false guard/failure는 old state를 보존하고 emitted
effect와 persistence cleanup 순서를 명시해야 한다. 전용 diagnostics/MIR
transition event와 runtime은 미결/`NOT_RUN`이다.

**현행 대안과 이행**
Enum+match, ordinary Class/actor state와 `uml_state_machine_provider`가
생성한 검토 가능한 ordinary source가 대안이다. migration은 Enum/match를
자동 DSL로 바꾸지 않고 state/transition graph를 report한다.

**활성화 선행 조건**
Design_ syntax 선택, exact grammar/recovery, totality/reentrancy/effect
checker, MIR event, persistence/versioning policy, provider parity와 target
receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** finite state와 total transition table에서 event와
  current state를 한 번 읽고 body 성공 뒤 next state를 commit한다.
- **음성/거부:** hidden transition이나 undeclared effect가 state를 바꾸면
  exhaustiveness와 관측 순서를 우회하므로 거부한다.
- **경계:** 두 event가 동시에 도착하거나 body가 재진입하면 isolation
  policy가 정한 한 순서만 허용하며 old/new state를 섞지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
// 현행 명시적 대안: state와 transition을 Enum/match로 드러낸다.
private enum DoorState {
    Closed
    Open
}
def toggle(state: DoorState) -> DoorState = {
    return @match state {
        ::Closed => DoorState::Open
        ::Open => DoorState::Closed
    }
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: static_once_value; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-static_once_value"></a>

## Static once value

> **Feature metadata**
> - Feature ID: `static_once_value`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
한 번만 초기화되는 공유 값을 explicit responsibility와 함께 제공하려는
요구를 검토한다. publication, concurrent initialization, reentrancy,
failure/retry/poison, module lifecycle와 final drop을 하나의 닫힌 state
machine으로 정의해야 한다.

**제안 표면**
once declaration과 get/init API는 미선정이다. 아래는 owner가 분명한
`SharedCell` 기반 application wrapper 대안이다. 양성 검토는 single
initializer와 successful publication, 음성은 hidden global lazy init,
경계는 initializer reentry 또는 두 thread의 failure/success 경쟁이다.

**정적 판정과 상호작용**
cell identity, initializer authority/effects, memory ordering, thread/actor
isolation, drop와 module unload를 닫아야 한다. ordinary `let`, module/class
static, SharedCell/SharedMutex를 자동 once semantics로 바꾸지 않는다.

**평가·소유권·오류**
initializer는 admitted winner에서 한 번 평가되고 full success 후 value를
publish한다. 실패 시 retry/poison/cache policy가 명시되어야 하며 partial
resource를 cleanup한다. waiter order와 Cancellation도 deterministic해야
한다. 전용 diagnostic/MIR state와 runtime은 `NOT_RUN`이다.

**현행 대안과 이행**
explicit owner object, application lifecycle initialization,
`SharedCell`/`SharedMutex` stdlib profile이 대안이다. migration은 global
binding을 자동 once로 바꾸지 않고 access/reentry/drop inventory를
report한다. tooling은 state와 owner를 보여야 한다.

**활성화 선행 조건**
closed once state machine, happens-before/failure/reentry/cleanup law,
module lifecycle, concurrency litmus/mutation corpus와 cross-backend target
receipt가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** single initializer가 성공 값을 한 번 publish하면
  이후 모든 waiter는 같은 identity와 happens-before edge를 관측한다.
- **음성/거부:** hidden global lazy init이나 owner 없는 resource cache는
  effect와 drop 책임을 감추므로 거부한다.
- **경계:** initializer 재진입 또는 한 thread의 failure와 다른 thread의
  success가 경합하면 retry/poison 정책에 따른 단일 terminal state를 낸다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/shared-state-coherence.json -->
```deeplus
// 현행 명시적 대안: application owner가 initialization과 shared cell을 소유한다.
let initial = Cache!()
let cacheCell = SharedCell::new(move initial)
let summary = cacheCell.withValue() { borrow cache => summarize(cache) }
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

<!-- deeplus-preview-feature-example: weak_atomic_ordering; registry-status: PREVIEW_DESIGN -->
<a id="preview-feature-weak_atomic_ordering"></a>

## Weak atomic ordering

> **Feature metadata**
> - Feature ID: `weak_atomic_ordering`
> - Registry status: `PREVIEW_DESIGN`; activation: `nonactivatable`
> - Authority: `LANGUAGE`; dependencies: 없음
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
순차 일관성보다 약한 ordering으로 shared-state 비용을 제어하려는 요구를
검토한다. target마다 임의 의미를 부여하지 않고 data race, happens-before,
load/store/RMW failure ordering과 compiler reorder 한계를 닫힌 memory
model로 제공해야 한다.

**제안 표면**
ordering spelling, lattice와 operation별 API는 미선정이다. 아래는 current
sequentially consistent scoped synchronization 대안이다. 양성 검토는
operation에 합법적인 explicit ordering, 음성은 invalid load/store pair,
경계는 compare-exchange success/failure ordering과 actor mailbox edge다.

**정적 판정과 상호작용**
ordering relation, compiler/CPU reorder, synchronization scope와 payload
eligibility를 닫아야 한다. actor enqueue/dequeue order와 SharedCell/
SharedMutex current guarantees를 약화하지 않고 raw layout, lock-free 또는
fairness를 자동 추론하지 않는다.

**평가·소유권·오류**
atomic operand와 closure는 operation contract대로 한 번 평가되고 failed
compare/exchange가 owner를 소비하지 않아야 한다. invalid ordering은
compile-time diagnostic이고 stronger/weaker ordering으로 fallback하지
않는다. 현행은 `WEAK_ATOMIC_ORDERING_REQUIRES_FEATURE_GATE`지만 source gate
없고 backend execution은 `NOT_RUN`이다.

**현행 대안과 이행**
current sequentially consistent `SharedCell`, receiver-bound
`SharedMutex`와 actor message transfer가 대안이다. migration은 operations를
자동 약화하지 않고 proof obligation과 happens-before graph를 report한다.
IDE는 selected ordering과 synchronization edge를 표시한다.

**활성화 선행 조건**
ratified memory model와 ordering lattice, xVM/LLVM semantic parity, target
codegen constraints, litmus/race suite, reproducible artifact-bound receipts와
별도 activation authority가 필요하다.

**설계 검토 시나리오**
- **양성 전제·기대:** operation별 합법 ordering과 required synchronization
  edge가 명시되면 compiler/backend는 그보다 약하게 재배치하지 않는다.
- **음성/거부:** load/store에 불법 ordering을 붙이거나 unsupported ordering을
  stronger/weaker 값으로 fallback하면 source contract를 바꾸므로 거부한다.
- **경계:** compare-exchange의 success/failure ordering 조합과 actor mailbox
  edge가 충돌하면 합법 lattice proof 없이는 operation을 활성화하지 않는다.

<!-- deeplus-status-fence: CURRENT -->

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
// 현행 명시적 대안: scoped SharedMutex가 current ordering을 소유한다.
let mutex = SharedMutex::new(move state)
mutex.withLock() { inout protected =>
    protected.count += 1
}
```

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->
