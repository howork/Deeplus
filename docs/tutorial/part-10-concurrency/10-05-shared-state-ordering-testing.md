# 10-05 — Shared state, happens-before와 검증 설계

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

`SharedCell`과 `SharedMutex`의 bounded library profile은 current design이다.
실제 memory model, lock/runtime, concurrency test는 `NOT_RUN`이다.

## 2. 학습 목표

- actor isolation과 shared-state owner를 구분한다.
- `withValue`, `replace`, `withLock`의 scoped 책임을 읽는다.
- current 최소 happens-before edge를 열거한다.
- 동시성 test oracle이 scheduler 우연에 의존하지 않게 설계한다.

## 3. 선수 지식

borrow/inout, closure lifetime, `concur`, actor enqueue/dequeue를 알아야 한다.

## 4. 문제에서 출발하기

공유 상태를 global mutable variable처럼 노출하면 lifetime, mutation
authority, suspension, cleanup을 추적할 수 없다. current profile은 explicit
owner와 scoped callable 안에서만 관찰·변경하게 한다.

## 5. 핵심 모델

`SharedCell<T>`은 immutable observation과 whole-value replacement owner다.
`withValue`의 `#scoped`는 callback callable profile이고 source binder는
`borrow`다. invocation이 그 region을 소유하므로 borrow는 callback 밖으로
escape하지 않는다.
`SharedMutex<T: SharedMutexPayload>`는 receiver-bound non-suspending scoped
mutation을 제공한다. `SharedMutexPayload`는 Trait가 아닌 sealed public
constraint이고, cleanup 책임이 없는 Reusable/Affine payload graph만
허용한다. 따라서 mutable state를 담을 수 있지만 Resource나 `def#cleanup`,
borrow/inout view, proof가 닫히지 않은 generic을 숨길 수 없다. 이 bound는
`Plain`이나 `Transferable`을 자동으로 증명하지 않는다. 여기서도
`#scoped`는 callback profile, `inout`은 binder mode다. lock 안에서
await하거나 guard를 저장하지 않는다.

최소 ordering:

- 한 task의 program order;
- parent pre-spawn → child start;
- child terminal/cleanup → await resume;
- enqueue commit → matching dequeue;
- cancellation cleanup complete → scope exit.

global FIFO, scheduler fairness, cross-sender order는 보장하지 않는다.

## 6. 단계별 예제

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let cell = SharedCell::new(move initial)
let summary = cell ~ withValue {
    borrow value => summarize(value)
}
let previous = cell ~ replace move updated
```

observation borrow는 closure 밖으로 나오지 않고 replace는 whole owner
transition을 드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let mutex = SharedMutex::new(move state)
mutex ~ withLock {
    inout protected =>
    protected.count += 1
}
```

callback은 non-suspending이어야 하고 `protected` inout가 escape하지 않는다.
payload 판정은 constructor의 move commit보다 먼저 끝나므로 거부 시 원래
`state` owner가 보존된다. lock을 얻은 뒤에는 exclusive loan을 닫고 unlock을
정확히 한 번 수행한 다음 원래 outcome을 전달한다.

## 7. 허용·거부·경계 사례

허용: borrowed value에서 independent summary를 만든다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let count = cell ~ withValue { borrow items => items.length }
```

거부: lock 안에서 suspend하거나 borrow를 반환한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let leaked = mutex ~ withLock {
    inout state =>
    await refresh(state)
    state
}
```

weak atomic ordering은 Preview Design nonactivatable이다. current code에
memory-order spelling을 invent하지 않는다.

## 8. 다른 기능과의 연결

- actor state는 turn isolation owner이고 SharedMutex는 explicit library
  owner다.
- pure closure는 mutable shared state를 capture할 수 없다.
- MIR은 borrow acquire/release, replacement commit, lock scope와 ordering
  events를 보존해야 한다.
- test는 stdout 순서가 아니라 canonical event identity와 allowed partial
  order를 비교해야 한다.

### 판정 추적

공유 접근을 만나면 먼저 actor turn으로 격리할지, immutable observation과
whole replacement가 필요한지, scoped mutation이 필요한지 정한다. 각각
Actor, `SharedCell`, `SharedMutex`라는 다른 owner를 선택한다. 다음으로
callback의 borrow/inout lifetime을 scope 안에 닫고 suspension과 escape가
없는지 검사한다. 마지막에 acquire, read/write, commit, release event와
필요한 happens-before edge만 기록한다.

생성은 type-side 일반 한정 호출 `SharedCell::new(...)`와
`SharedMutex::new(...)`다. 이미 생성된 owner의 `withValue`, `replace`,
`withLock`은 메시지 호출이므로 `~`를 쓴다. 점 메서드 호출은 이 profile의
대체 표면이 아니다. 또한 `{ #scoped borrow value => ... }`처럼
`#scoped`를 binder 자리에 반복하지 않는다.

검증기는 전체 실행을 하나의 순서로 만들지 않는다. parent pre-spawn이
child start보다 앞선다는 edge와 child cleanup이 await resume보다 앞선다는
edge는 요구하지만, 관계가 없는 두 child event 중 누가 먼저인지까지
정하지 않는다. actor도 같은 sender의 admitted sequence와 matching
enqueue/dequeue를 볼 뿐 서로 다른 sender의 global FIFO를 합성하지 않는다.

### 흔한 오해와 미니 사례

mutex 안이면 어떤 borrow도 안전하게 반환할 수 있다는 생각은 틀리다.
guard가 풀린 뒤에도 `state`를 가리키면 scoped authority가 escape한다.
또 한 번의 test log에서 A가 B보다 먼저 찍혔다고 language ordering을
추가해서도 안 된다.

미니 사례로 두 sender가 같은 actor에 각각 메시지를 보낼 때 각
enqueue→matching dequeue edge는 검사한다. 그러나 sender 사이의
dequeue 순서는 contract에 없으므로 oracle은 두 순서를 모두 허용해야
한다. 필요한 business order는 message 안의 explicit sequence나 별도
coordinator가 소유하게 한다.

테스트 oracle은 event 목록과 필수 edge 집합을 따로 둔다. 예를 들어
`spawn(parent, child)`, `child_cleanup_done`, `await_resume` 세 event에는
앞에서 뒤로 두 edge가 필요하지만 다른 독립 child의 read event와는
전체 순서를 요구하지 않는다. 실행 로그를 정렬해 같은 문자열인지
비교하면 허용된 interleaving을 실패로 오인하거나, 필수 edge 위반을
우연히 숨길 수 있다.

SharedCell 교체도 old value 관찰, replacement commit, new value 관찰을
구분한다. callback이 만든 독립 summary는 scope 밖으로 나갈 수 있지만
borrowed reference 자체는 나갈 수 없다. SharedMutex에서는 mutation
commit 전 failure가 원래 owner/value를 보존하는지, lock release가 모든
terminal에서 한 번 일어나는지도 함께 검증한다.

이렇게 만든 oracle은 허용된 실행의 집합을 판정하며 특정 scheduler를
정답으로 고정하지 않는다.

## 9. Deeplus다운 작성 관례

공유해야 할 이유와 owner를 명시한다. 읽기는 scoped borrow, 변경은
whole replacement 또는 scoped inout로 제한한다. 구현 scheduler의 한 번의
출력 순서를 언어 보장으로 승격하지 않는다.

## 10. 연습 문제

1. **따라 하기:** SharedCell에서 length만 계산하는 scoped observation을
   작성하라.
2. **빈칸 완성:** SharedMutex callback에 허용되지 않는 suspension과
   escaping ___를 채워라.
3. **스스로 설계하기:** actor, SharedCell, SharedMutex 중 설정 cache에
   맞는 owner를 선택하고 failure/ordering 이유를 설명하라.

## 11. 빠른 복습

- shared state는 explicit owner를 갖는다.
- 생성은 일반 한정 호출, receiver operation은 `~` 메시지 호출이다.
- `#scoped`는 callback profile이고 source binder는 `borrow` 또는 `inout`다.
- borrow/inout는 scoped callback 밖으로 escape하지 않는다.
- lock 안 suspension은 current가 아니다.
- ordering test는 정본 happens-before만 요구한다.

## 12. 정본 근거와 다음 장

- [공유 상태 contract](../../../spec/contracts/shared-state-coherence.json)
- [평가·shared observation](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [ownership 참조](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)

이제 이 Part의 법칙을 bounded worker workflow에 통합한다.
