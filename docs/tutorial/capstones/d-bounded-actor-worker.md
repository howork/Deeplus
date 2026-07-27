# 종합 프로젝트 D — 용량이 제한된 actor worker

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> actor, mailbox, structured task의 현행 설계를 설명한다. runtime,
> scheduler, cancellation, cross-backend 실행 증거는 `NOT_RUN`이다.

## 1. 만들 것

용량이 정해진 mailbox를 가진 worker actor를 설계한다. 호출자는 작업을
send하고 결과가 필요한 경우 request/reply를 사용한다. 프로젝트의
핵심은 동시성 문법보다 다음 책임을 명시하는 것이다.

- 누가 mutable state를 소유하는가?
- 메시지는 어느 시점에 enqueue commit되는가?
- commit 전후 failure에서 moved payload의 owner는 누구인가?
- request task가 cancel되면 receiver와 reply 책임은 어떻게 되는가?
- actor 내부 `await`가 재진입을 암시하는가?

## 2. protocol 먼저 설계하기

메시지 payload는 actor 경계를 건널 수 있는 owner-safe 값이어야 한다.
borrow와 `inout` payload는 격리 경계를 넘지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::worker::protocol

public schema Job {
    id: Int
    payload: String
}

public protocol WorkerProtocol {
    send submit(job: Job)
    request processedCount() -> Int
}
```

send는 enqueue 후 reply를 요구하지 않는 메시지이고, request는 typed
reply task와 correlation을 갖는다. ordinary method 호출과 actor
message resolution은 서로 fallback하지 않는다.

이 선언은 requirement 집합을 보여 준다. 아래 `Worker`의 handler 철자가
같다는 사실만으로 `WorkerProtocol` conformance가 생기지는 않는다.
실제 결합에는 checker가 검증한 별도 conformance evidence가 필요하며,
그 제품 증거는 이 프로젝트에서 `NOT_RUN`이다.

## 3. actor와 mailbox

mailbox capacity는 양의 `StaticIntLiteral`이어야 한다. `0`이나 runtime
변수는 current bounded mailbox profile을 만족하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public actor #mailbox(capacity: 8) Worker {
    -var completed: Int = 0

    on submit(job: Job) = {
        accept(job)
        completed += 1
    }

    request processedCount() -> Int = {
        return completed
    }
}
```

actor identity는 하나의 격리된 mutable state region과 mailbox를
소유한다. admitted actor turn 하나만 그 state를 변경한다. `completed`는
handler가 끝낸 작업 수이지 runtime mailbox backlog가 아니다. mailbox에
대기 중인 메시지 수를 handler-local 증감으로 흉내 내지 않으며, 외부
객체가 actor state를 직접 쓰는 API도 만들지 않는다.

## 4. 메시지 호출과 owner 전이

정확한 selector와 actor reference가 필요하다. payload expression은
source order로 평가되고 admission이 성공하면 enqueue commit된다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def submitOne(worker: Worker, move job: Job)
    -> Result<Unit, error ActorMessageError>
= {
    return worker :~ submit move job
}

public def#async countProcessed(worker: Worker) -> Int
    throws ActorMessageError
= {
    task scope {
        let Result::ok(replyTask) = worker :~ processedCount
        else Result::err(error) => throw error
        return await replyTask
    }
}
```

이 코드는 교육용 surface projection이다. exact message selector와
Task failure descriptor는 정본 actor contract를 함께 확인한다.
enqueue commit 전 실패라면 sender가 moved owner를 보존해야 하고,
commit 뒤에는 receiver mailbox가 payload 책임을 가진다.

## 5. cancellation과 structured scope

request를 시작한 task가 취소될 수 있다고 해서 이미 commit된 actor
message가 자동으로 “실행되지 않은 것”이 되지는 않는다. cancellation,
receiver closure, reply abandonment는 서로 다른 사건이다. 호출자는
structured scope에서 child task의 수명과 관찰 책임을 명시해야 한다.

정확한 책임 순서는 세 단계다. 먼저 request admission이 성공해
`replyTask`와 correlation identity를 만든다. 다음으로 caller
cancellation은 그 task의 관찰 책임을 끝낼 수 있지만 이미 commit된
receiver 작업을 자동 취소하지 않는다. 마지막으로 receiver 쪽 취소가
필요하면 별도 protocol message와 명시적 상태 전이를 설계한다. 이름 있는
async 함수는 `def#async`로 쓰며 Preview async callable literal을
Current로 끌어오지 않는다.

## 6. `await`와 actor turn

Deeplus 현행 actor 모델에서 handler의 `await`가 곧바로 state authority를
다른 mutating turn에 넘기는 재진입 허가가 되지는 않는다. 따라서
재진입을 전제로 state snapshot을 복구하는 예제를 만들지 않는다.
반대로 긴 suspension은 진행성 문제를 만들 수 있으므로, 외부 작업을
작은 actor turn과 별도 task로 분해할지 설계 검토가 필요하다.

## 7. 거부와 경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
actor #mailbox(capacity: 0) Broken { }

def sendBorrow(worker: Worker, borrow job: Job) = {
    worker :~ submit job
}
```

첫째 선언은 양의 StaticInt가 아니다. 둘째 함수는 borrowed payload를
actor isolation boundary 너머로 보내려 한다. 복사 가능한 값이면
명시적으로 새 owner를 만들고, move라면 enqueue commit 전후의 rollback
책임을 보존해야 한다.

## 8. acceptance 시나리오

1. capacity 이하의 send가 source order로 admit된다.
2. full mailbox는 `mailboxFull` admission failure로 즉시 거부되며
   blocking·retry·drop으로 바뀌지 않는다.
3. request reply type이 protocol과 일치한다.
4. receiver가 닫힌 뒤 send/request의 failure owner가 구분된다.
5. cancellation 전·commit 중·commit 후를 별도 시나리오로 다룬다.
6. 외부에서 actor state를 직접 변경하는 경로가 없다.
7. 동일 입력 반복에서 요구되는 deterministic observation 범위를
   scheduler 우연과 분리한다.

실제 runtime 결과가 없으므로 이 목록은 실행 PASS가 아니라 향후
Test_/Implementation acceptance 설계다.

### 8.1 한 send의 시간선

`submit(job)` 한 건을 다음 다섯 구간으로 나누어 그린다.

1. sender가 `job` expression을 평가한다.
2. protocol selector와 receiver actor identity를 해석한다.
3. capacity, receiver-open 상태, payload crossing을 admission한다.
4. 성공하면 enqueue commit과 함께 payload owner가 mailbox로 이동한다.
5. receiver turn이 payload를 꺼내 handler를 실행하고 정리한다.

1~3 사이에 실패하면 sender가 owner를 잃어서는 안 된다. 4 이후에는
sender가 같은 moved owner를 다시 사용할 수 없다. 5의 handler failure가
3의 `mailboxFull`과 같은 error라고 가정하지 않는다. request라면 여기에
correlation identity, reply task, receiver-closed-before-reply terminal
축이 추가된다.

### 8.2 ordering을 정확히 말하기

“actor이므로 순서가 보장된다”는 설명은 너무 넓다. 어떤 sender의
program order, mailbox admission order, actor turn order, 서로 다른
sender 사이의 interleaving, reply observation은 각각 다른 관계다.
프로젝트는 필요한 관계만 protocol과 test oracle에 기록한다. source
order를 전체 시스템의 전역 순서라고 부르거나 scheduler 구현을 언어
의미로 승격하지 않는다.

### 8.3 진행성과 격리의 균형

긴 계산이나 외부 I/O를 actor turn 안에서 계속 기다리면 격리는
지켜져도 다른 message가 오래 대기할 수 있다. 작업을 child task로
분리할 때는 state snapshot의 owner, 결과를 돌려보내는 message,
cancellation과 cleanup을 함께 설계한다. 단순히 `await` 앞뒤에서 actor
state를 자유롭게 읽는 재진입 모델을 가정하지 않는다.

## 9. 연습 문제

1. **따라 하기:** send 한 건의 payload owner가 평가 전, commit 전,
   commit 후 누구인지 표로 적어라.
2. **빈칸 완성:** `Job`에 priority를 추가하되 mailbox admission과
   처리 순서를 같은 개념으로 합치지 마라.
3. **직접 설계:** full mailbox의 즉시 거부를 error signature와 owner
   timeline에 드러내고 blocking·retry를 추가하지 마라.
4. **경계 과제:** request task cancellation과 receiver-side 작업 취소를
   별도 protocol message 없이 동일시하면 안 되는 이유를 설명하라.
5. **테스트 과제:** runtime nondeterminism을 허용하면서도 owner leak과
   duplicate reply를 탐지할 observation schema를 설계하라.

## 10. 완료 체크리스트

- [ ] actor state owner가 하나다.
- [ ] capacity는 양의 StaticInt다.
- [ ] send와 request를 구분했다.
- [ ] borrow/`inout` payload를 보내지 않았다.
- [ ] enqueue commit 전후 owner를 기록했다.
- [ ] cancellation과 receiver execution을 동일시하지 않았다.
- [ ] product 실행은 `NOT_RUN`이다.

## 11. 정본 근거

- [동시성 Part](../part-10-concurrency/README.md)
- [ownership Part](../part-07-ownership/README.md)
- `spec/contracts/actor-concurrency-coherence.json`
- [문법 참조: async, task, actor](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
