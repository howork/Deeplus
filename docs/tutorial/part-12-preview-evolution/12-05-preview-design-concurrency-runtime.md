# 12-05 — Preview Design: 동시성, runtime와 MIR-X1

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`

이 장의 동시성·FFI·runtime feature 15개는 전부
`PREVIEW_DESIGN_NONACTIVATABLE`이다. 한편 current actor/task 및 HIR-H1
verifier boundary는 현행 설계이고, DP-RFC-0001의 xVM-only MIR-X1과
DP-RFC-0002의 concrete HIR-H1 schema/implementation proposal은
`DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE`이다. 현행 backend authority는
xVM initial + LLVM AOT + LLVM ORC JIT이며 RFC draft가 이를 대체하지 않는다.

## 2. 학습 목표

- 동시성·runtime Preview Design 15개를 exact ID로 분류한다.
- current structured concurrency와 nonactivatable sugar를 구분한다.
- observation, isolation, cancellation, memory ordering 검토 축을 세운다.
- current HIR-H1 boundary, draft HIR schema와 MIR-X1 제안을 구분한다.
- IR 제안 병합과 backend activation/product evidence를 혼동하지 않는다.

## 3. 선수 지식

Part 10의 task scope, actor protocol/mailbox/isolation, cancellation/cleanup과
Part 11의 HIR/MIR/backend 경계를 알고 있어야 한다.

## 4. 문제에서 출발하기

비동기 callable을 한 줄로 쓰는 문법은 매력적이지만 capture owner,
suspension ABI, cancellation과 cleanup이 닫히지 않으면 짧은 syntax가
숨은 lifetime을 만든다. weak atomic ordering도 spelling만 정하면 target별
reordering과 happens-before가 달라질 수 있다. xVM-only MIR 제안 역시
문서가 상세하다는 이유만으로 LLVM preservation authority를 지울 수
없다.

## 5. 핵심 모델

15개 exact Preview Design ID를 다음처럼 나눈다.

1. **async composition**
   - `async_callable_literal_profile`
   - `async_comprehension`
   - `directed_coroutine_group`
2. **observation·protocol·state**
   - `automatic_observation_tracking`
   - `session_protocol_lite_provider`
   - `state_machine_source_syntax`
3. **dynamic inspection·unsafe**
   - `dyn_inspection`
   - `dynamic_unsafe_quarantine_scope_msp`
4. **C interop 확장**
   - `c_aggregate`
   - `c_stored_callback`
   - `c_variadic`
5. **lifecycle·runtime object**
   - `module_static_entrance`
   - `prototype_delta`
   - `static_once_value`
6. **memory model**
   - `weak_atomic_ordering`

모든 항목은 nonactivatable이며 exact gate가 없다. C aggregate/callback/
variadic proposal은 Part 12-02의 제한된 FFI Preview Gated surface가
자동으로 여는 하위 기능도 아니다.

IR 층은 별도 표로 읽는다.

| 항목 | 현재 역할 | 상태 |
|---|---|---|
| HIR-H1 verifier boundary | resolved identity와 typed responsibility를 lowering 전에 닫음 | current Stable design |
| `deeplus.hir/h1` concrete schema·crate reorganization | DP-RFC-0002의 제안 | noncanonical/nonactivatable |
| MIR-X1 xVM-only model | DP-RFC-0001의 제안 | noncanonical/nonactivatable |
| backend authority | xVM initial + LLVM AOT + LLVM ORC JIT | current; product `NOT_RUN` |

## 6. 단계별 예제

### 1단계: async callable literal 대신 이름 있는 declaration을 쓴다

candidate literal은 current parser가 거부하는 probe다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: async_callable_literal_profile
let loader = #async{ => await loadProfile() }
```

current 대안에서는 effect/error/capture owner가 signature와 declaration에
드러난다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def#async loadProfileTask() -> Profile
    throws NetworkError
    effects io
= {
    return await loadProfile()
}
```

### 2단계: async collection policy를 이름으로 고정한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def#async collectProfiles(ids: AsyncSequence<UserId, IOError>) -> List<Profile>
    throws IOError throws NetworkError
= {
    return await AsyncCollector::list(
        source: ids,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
```

이 form은 source order, finiteness, backpressure, fail-fast, pending
cancellation과 partial result publication을 named collector 계약에서
검토하게 한다. `async_comprehension`은 이 정보를 숨긴 sugar로 아직
활성화되지 않았다.

### 3단계: lexical owner가 있는 task scope를 유지한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
task scope {
    let producer = spawn async { => await produce() }
    let consumer = spawn async { => await consume() }
    await producer
    await consumer
}
```

`directed_coroutine_group`은 endpoint direction, escape, child order,
cancellation graph와 cleanup을 더 강하게 표현하려는 proposal이다.
현재 task scope를 몰래 directed group으로 낮추거나 detached child를
허용하지 않는다.

### 4단계: shared mutation은 current scoped synchronization을 쓴다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let mutex = SharedMutex::new(move state)
mutex.withLock() { inout protected =>
    protected.count += 1
}
```

`weak_atomic_ordering`은 spelling과 lattice, valid load/store/RMW pairing,
compiler/CPU reorder, backend parity가 미선정인 proposal이다. current
synchronization을 임의로 weaker ordering으로 rewrite하지 않는다.

## 7. 허용·거부·경계 사례

허용: actor state는 mailbox turn에서만 mutate하고 message transfer owner를
명시한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public actor Counter {
    on increment(by: Int) = {
        recordIncrement(by)
    }

    request current() -> Int = { return currentCount() }
}
```

거부: nonactivatable 기능을 gate로 켠다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
#preview(weak_atomic_ordering,static_once_value)
let counter = Atomic::new(0)
```

경계: MIR-X1 문서는 ValueId, PlaceId, CFG, block argument, cleanup/outcome/
suspension을 매우 상세히 제안한다. 그러나 상세함은 adoption receipt가
아니다. 현행 HIR decision을 MIR이 재탐색하지 않는다는 설계 원칙은
유용하지만, `deeplus.mir/x1` schema 배정, xVM-only backend 전환,
compiler/runtime 실행을 이 튜토리얼이 승인할 수는 없다.

## 8. 다른 기능과의 연결

async proposal은 callable capture, effect/error union, ownership, task
isolation과 이어진다. automatic observation은 hidden read와 actor isolation,
subscription cleanup을 닫아야 한다. C callback/variadic/aggregate는 FFI
representability, provenance, unwind와 foreign lifetime을 확장한다.
static once/module entrance는 Package import와 Module lifecycle을 혼동하지
않아야 한다.

HIR-H1은 source-level resolution을 닫는 마지막 의미 경계이고 MIR은 이를
평가·commit·failure·cleanup·suspend event로 펼치는 첫 실행 경계다.
backend들은 같은 Deeplus observation을 보존해야 하며 target별 편의를
언어 의미로 승격해서는 안 된다.

### 판정 추적과 흔한 오해

동시성 proposal은 surface보다 capture owner, child lifetime, cancellation,
cleanup, isolation과 happens-before를 먼저 채운다. FFI 확장은 provenance,
callback lifetime과 unwind를, runtime static proposal은 initialization
effect와 drop owner를 기록한다. IR 제안은 current HIR-H1 boundary에서
이미 닫힌 결정과 새 schema/implementation 선택을 분리한다.

흔한 오해는 상세 RFC가 current backend authority를 대체하거나,
Preview Gated FFI가 모든 C interop proposal을 함께 연다는 생각이다.
미니 사례에서 named `def#async`는 async literal의 current 대안이지
그 proposal의 activation evidence가 아니다. MIR-X1 event model의 유용한
질문을 재사용해도 xVM-only 전환이나 LLVM 제거를 승인한 것은 아니다.

## 9. Deeplus다운 작성 관례

- async sugar보다 capture, cancellation, cleanup owner를 먼저 드러낸다.
- task child는 lexical scope가 join/cancel 책임을 소유하게 한다.
- actor mailbox와 shared memory synchronization을 섞지 않는다.
- FFI 확장 기능을 minimum sound profile에서 자동 파생하지 않는다.
- weak ordering을 성능 최적화라는 이유만으로 기본값으로 만들지 않는다.
- RFC의 status, current backend authority, product receipt를 별도 열로
  기록한다.

## 10. 연습 문제

1. **그대로 따라 하기:** 이름 있는 `loadProfileTask`를 옮겨 적고 capture,
   error, effect, suspension owner를 표시하라.
2. **빈칸 채우기:** current backend authority를
   `xVM initial + ____ + ____`로 완성하고 MIR-X1 draft가 이를 바꾸지
   않는 이유를 적어라.
3. **스스로 설계하기:** `automatic_observation_tracking`에 대해 observed
   identity, dependency edge, mutation invalidation, callback effect,
   actor isolation, cycle, subscription cleanup과 deterministic diagnostic을
   포함한 negative/boundary review matrix를 작성하라.

## 11. 빠른 복습

- 동시성·FFI·runtime Preview Design은 정확히 15개이며 모두
  `NONACTIVATABLE`이다.
- current explicit concurrency form은 owner와 policy를 source에 드러낸다.
- HIR-H1 verifier boundary와 DP-RFC-0002 concrete proposal은 같은
  상태가 아니다.
- MIR-X1은 xVM-only noncanonical draft이며 현행 LLVM authority를
  대체하지 않는다.
- product lane은 여전히 `15/15 NOT_RUN`이다.

## 12. 정본 근거와 다음 장

- [Preview Design — 동시성·FFI·runtime](../../grammar-reference/23-preview-design-concurrency-ffi-and-runtime.md)
- [actor/concurrency 계약](../../../spec/contracts/actor-concurrency-coherence.json)
- [DP-RFC-0001 — MIR-X1](../../../rfcs/DP-RFC-0001-xvm-only-mir.md)
- [DP-RFC-0002 — HIR-H1 proposal](../../../rfcs/DP-RFC-0002-current-hir-h1.md)
- [implementation status](../../../current/implementation-status.yaml)

다음 실습에서는 한 proposal을 실제로 활성화하지 않고도 검토 가능한
증거 카드와 acceptance matrix를 만든다.
