# Lab 10 — 용량 제한 Worker와 request/reply

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

이 실습은 bounded mailbox, one-way job transfer, status request,
Cancellation cleanup을 한 흐름에 결합한다. 실행 결과가 아니라 정적
responsibility trace를 만든다.

## 목표

- protocol과 actor handler를 분리한다.
- enqueue admission을 명시적으로 처리한다.
- request Result를 풀고 `Reply<T>`를 await한다.
- moved job의 owner를 commit 전후로 추적한다.

## 준비

Part 10의 앞 장과 Part 09의 Result/throws/Cancellation을 복습한다.

### 누적 프로젝트 연결

| 연결 | 이 실습에서 이어 받거나 넘기는 것 |
|---|---|
| input | Lab 09의 import job, transport/domain failure 구분과 cleanup trace를 입력으로 받는다. |
| output | bounded admission, move commit, reply correlation, cancellation terminal을 결합한 worker 책임표를 만든다. |
| next | Part 11에서 Worker protocol과 payload schema를 public Module API로 배치하고 digest 경계를 검토한다. |

코드를 쓰기 전에 `Job` owner timeline을 그린다. submit 진입 시 caller,
admission 검사 중에도 caller, enqueue commit 뒤 mailbox, handler
dequeue 뒤 actor turn이 owner다. 어느 시점에도 caller와 actor가 동시에
유일 owner라고 기록해서는 안 된다. status request에는 payload owner
대신 admission Result, correlation, `Reply<T>`의 세 identity를 적는다.

## 단계별 구현

### 1단계 — protocol과 actor

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public protocol WorkerProtocol {
    send run(job: Job)
    request status() -> WorkerStatus
}

public actor #mailbox(capacity: 8) Worker {
    on run(job: Job) = {
        process(move job)
    }
    request status() -> WorkerStatus = {
        return currentStatus()
    }
}
```

handler spelling만으로 protocol conformance가 생긴다고 주장하지 않는다.
checker가 별도 identity 결합을 검증해야 한다.

### 2단계 — job admission

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def submit(worker: Worker, move job: Job)
    -> Result<Unit, error ActorMessageError>
= {
    return worker :~ run move job
}
```

실패가 precommit이면 caller가 `job` owner를 보존하고, 성공 commit이면
mailbox message가 owner를 얻는다.

### 3단계 — status request

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async query(worker: Worker) -> WorkerStatus
    throws ActorMessageError
= {
    let Result::ok(reply) = worker :~ status
    else Result::err(admissionError) => throw admissionError
    return await reply
}
```

admission 실패와 reply 전 receiver close는 서로 다른 시점이다.

### 4단계 — cancellation과 shutdown policy

scope가 취소되면 아직 commit되지 않은 submit은 caller owner를 보존한다.
이미 admitted된 job을 Cancellation이 mailbox에서 자동 회수하지는 않는다.
query task의 await가 취소되어도 actor turn이나 committed command가
철회되었다고 가정하지 않는다. application shutdown policy는 새 admission을
닫고, admitted work의 drain 또는 explicit cancel protocol을 선택하며,
각 actor/resource cleanup이 terminal인 뒤 scope를 닫아야 한다.

판정 trace는 `payload crossing 적합성 → capacity admission → enqueue
commit → dequeue/turn → handler terminal → request reply`다. one-way는
reply 단계가 없고 request만 correlation을 갖는다. 이 차이를 하나의
“send 성공” Bool로 줄이면 precommit retry와 postcommit 중복 실행을
구분할 수 없다.

## 중간 점검

- capacity가 positive static integer인가?
- run payload가 borrow/inout가 아닌 move owner인가?
- request Result를 await 전에 풀었는가?
- Cancellation을 ActorMessageError로 바꾸지 않았는가?
- enqueue commit 전후의 `job` owner가 정확히 하나인가?
- shutdown이 admitted command를 묵시적으로 취소했다고 주장하지 않는가?

## 실패 실험

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
public actor #mailbox(capacity: 0) InvalidWorker {
    on run(job: Job) = { }
}

let status = await (worker :~ status)
```

첫 오류는 mailbox bound admission, 두 번째는 request admission Result
생략이다.

흔한 오해는 capacity 8을 actor가 동시에 여덟 turn을 실행한다는 뜻으로
읽는 것이다. capacity는 admission 가능한 mailbox bound이며 isolated
state는 한 admitted turn이 소유한다. 또 status reply가 늦다는 이유로
앞선 command가 실패했다고 추론해서는 안 된다. 검증 oracle은
enqueue/dequeue/correlation/cleanup identity와 허용된 partial order를
비교하고 wall-clock 완료 순서를 language law로 만들지 않는다.

정상 trace, mailboxFull trace, receiver-close-before-reply trace,
Cancellation trace를 각각 작성한다. 각 trace에는 commit 여부, owner,
primary failure, suppressed cleanup, 외부 관찰을 다섯 열로 기록한다.
이 표가 모두 채워져야 worker workflow가 단순 코드 예시가 아니라
책임 경계 연습이 된다.

최종 산출물은 actor source만이 아니다. 첫째 protocol requirement와
actor handler의 identity crosswalk, 둘째 one-way/request result shape
표, 셋째 `Job` owner timeline, 넷째 네 failure trace, 다섯째 partial-order
oracle을 함께 제출한다. crosswalk에는 handler spelling이 같다는 사실과
실제 conformance evidence를 별도 열로 둔다.

검토자는 정상 trace에서 enqueue commit이 정확히 한 번, request
correlation이 query마다 정확히 하나인지 확인한다. 실패 trace에서는
precommit error 뒤 mailbox sequence가 0인지, postcommit receiver close
뒤 sender owner가 부활하지 않는지, Cancellation 뒤 cleanup-before-scope-exit
edge가 있는지를 확인한다. 이 정적 검토가 통과해도 scheduler나 actor
runtime 제품이 실행되었다는 뜻은 아니다.

마지막으로 흔한 오해 두 가지를 반례로 적는다. capacity 8은 여덟 handler가
동시에 state를 바꾼다는 뜻이 아니며, one-way `Result::ok(Unit)`은
handler가 성공했다는 reply도 아니다. 전자는 mailbox admission bound,
후자는 enqueue commit 확인이다. handler domain result가 필요하면
명시적 request/reply protocol로 모델링한다.

누적 프로젝트의 import job을 실제 payload로 삼을 때는 decode 전 bytes
borrow를 보내지 말고 owner가 닫힌 `Job` 값을 만든 뒤 move한다. admission이
거부되면 caller가 같은 Job을 정책에 따라 재시도할 수 있고, commit 뒤에는
새 복사본을 만들어 중복 전송해서는 안 된다. 이 owner 규칙을 Lab 11의
public protocol API에도 그대로 전달한다.
## 확장 과제

1. **따라 하기:** 같은 sender가 job 두 개를 보내고 status를 요청하는
   순서를 작성하라.
2. **빈칸 완성:** one-way result와 request immediate result type을
   각각 채워라.
3. **스스로 설계하기:** mailboxFull retry policy를 named ordinary API로
   만들고 owner가 중복 전송되지 않게 설명하라.
4. **검증 설계:** enqueue/dequeue/correlation/cleanup event oracle을
   scheduler-independent 순서 제약으로 작성하라.

## 완료 체크리스트

- [ ] actor와 protocol domain을 구분했다.
- [ ] payload가 하나의 admitted aggregate다.
- [ ] admission과 reply failure를 분리했다.
- [ ] owner가 commit 지점에서 정확히 한 번 이동한다.
- [ ] global FIFO/fairness/product PASS를 주장하지 않았다.

## 정본 근거

- [actor/concurrency reference](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [actor contract](../../../spec/contracts/actor-concurrency-coherence.json)
- [MIR actor observation](../../../spec/mir/semantics.md)
