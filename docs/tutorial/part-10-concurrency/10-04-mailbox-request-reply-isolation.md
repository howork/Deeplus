# 10-04 — Mailbox, request/reply와 isolation

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

mailbox와 request responsibility의 current static contract를 설명한다.
실제 queue/scheduler 실행은 `NOT_RUN`이다.

## 2. 학습 목표

- logical-unbounded와 bounded-reject mailbox를 구분한다.
- enqueue precommit failure와 postcommit reply failure를 나눈다.
- one-way와 request expression의 정확한 Result shape을 읽는다.
- actor crossing의 ownership/isolation 조건을 적용한다.
- actor incarnation과 task execution의 `SenderId` lifetime을 구분한다.

## 3. 선수 지식

Actor/message, Result pattern, Reply/await, move와 Shareable을 알아야 한다.

## 4. 문제에서 출발하기

mailbox가 가득 찼다면 message는 들어가지 않았고 sender가 payload를
계속 소유해야 한다. 반면 enqueue 뒤 receiver가 reply 전에 닫히면 이미
message와 correlation이 존재한다. 두 실패를 하나로 합치면 owner와
retry safety를 판단할 수 없다.

## 5. 핵심 모델

- clause 없음: `logical_unbounded_v1`; 언어 capacity rejection 없음.
- `#mailbox(capacity: N)`: `bounded_reject_v1`; N은 positive StaticInt.
- one-way result: `Result<Unit,error ActorMessageError>`.
- request immediate result: `Result<Reply<T>,error ActorMessageError>`.
- transport dynamic responsibility: `throws AllocationError effects allocate`.
- `logical_unbounded_v1`은 capacity rejection이 없을 뿐 무한 storage를
  보장하지 않는다.
- admission errors: `mailboxFull`, `receiverClosedBeforeAdmission`.
- admitted reply terminal transport error:
  `receiverClosedBeforeReply`.
- each successful request creates one non-forgeable `ReplyId` and one request
  correlation identity; module API records only their
  `per_value_non_forgeable` policy markers.
- sender key는 `Actor(ActorInstanceId)` 또는 `Execution(ExecutionId)`의
  태그된 내부 identity다. actor suspend/resume은 같은 key를 유지하고,
  actor restart와 structured child spawn은 새 key를 만든다.

Cancellation은 이 family에 들어가지 않는다.

## 6. 단계별 예제

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public actor #mailbox(capacity: 8) Directory {
    request find(id: Int) -> Status throws LookupError = {
        return loadStatus(id)
    }
}
```

admission Result를 먼저 푼 뒤 reply를 await한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#async inspect(directory: Directory, id: Int) -> Status
    throws ActorMessageError throws LookupError throws AllocationError
    effects allocate
= {
    let Result::ok(reply) = directory :~ find id: id
    else Result::err(admissionError) => throw admissionError
    return await reply
}
```

`directory :~ find id: id`의 실패 시점에는 reply/correlation이 없다.
`Result::ok(reply)` 뒤에야 reply 책임이 존재한다.

## 7. 허용·거부·경계 사례

허용: move owner는 successful enqueue commit에서만 넘어간다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def dispatch(worker: Worker, move job: Job)
    -> Result<Unit, error ActorMessageError>
    throws AllocationError effects allocate
= {
    return worker :~ run move job
}
```

거부: admission Result를 풀지 않고 직접 await한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let status = await (directory :~ find id: id)
// request expression은 먼저 Result<Reply<Status>, ...> admission을 반환한다.
```

borrow와 `inout` payload도 actor 경계를 건너지 못한다. owned
`Transferable` move 또는 명시적 `Shareable` value가 필요하다.

## 8. 다른 기능과의 연결

- request의 `Reply<T>`와 structured execution의 `Run<T>`는 nominal
  identity부터 분리되며 서로 암시 변환되지 않는다.
- module API digest는 correlation policy를 기록하되 runtime ID를 미리
  만들지 않는다.
- Cancellation이 committed message를 철회하지 않는다.
- bounded rejection에는 channel sequence가 없다.

### 판정 추적

송신자는 receiver와 payload를 한 번 평가한 뒤 payload crossing 조건을
검사한다. bounded mailbox라면 capacity admission을 확인하며 이때까지는
sender가 moved owner를 유지한다. admission 성공 순간 enqueue commit과
mailbox sequence가 생기고 owner가 이동한다. request라면 같은 commit에서
reply correlation과 `Reply<T>` 책임이 생기며, 이후 handler Error와
`receiverClosedBeforeReply`는 reply terminal에서 관찰한다.

send가 `SenderId`를 새로 할당하는 것은 아니다. actor turn 안에서는 이미
존재하는 `ActorInstanceId`, 일반/root/child execution에서는 이미 존재하는
`ExecutionId`를 `ActorSenderIdentityPlanV1`이 선택한다. actor handler가
spawn한 child는 lexical 위치와 무관하게 actor-turn authority를 상속하지
않으므로 child의 execution sender를 사용한다.

| 단계 | one-way 관찰 | request 관찰 |
|---|---|---|
| precommit admission 거부 | `Result::err(ActorMessageError)`와 sender owner 유지 | 같은 admission error, reply/correlation 없음 |
| precommit allocation 실패 | `AllocationError`, sender owner 유지, Result 없음 | `AllocationError`, reply/correlation 없음 |
| enqueue commit | `Result::ok(Unit)`과 owner 이동 | `Result::ok(Reply<T>)`와 correlation 생성 |
| postcommit terminal | 별도 reply 없음 | value, handler Error, reply transport failure 또는 Cancellation |

### 흔한 오해와 미니 사례

mailbox가 가득 찬 뒤에도 move가 이미 끝났다고 생각하면 retry용 payload를
복제하게 된다. precommit 거부에서는 원래 owner가 남는다. 반대로
reply가 생긴 뒤 receiver가 닫혔다고 메시지 자체를 되돌려 retry하면 이미
수행된 side effect를 중복할 수 있다.

미니 사례로 조회 query는 application이 idempotent하다고 보장하면
postcommit retry 정책을 설계할 수 있지만, 결제 command는 correlation과
domain idempotency key 없이 재전송해서는 안 된다. 이 차이는 mailbox
API가 자동 결정하지 않고 application contract가 소유한다.

owner trace도 결과 type과 함께 적는다. precommit `mailboxFull`에서는
payload owner가 sender에 남고 sequence/correlation count가 0이다.
commit 뒤에는 mailbox가 payload owner이고 request correlation count가
1이다. handler가 값을 만들면 `Reply`가 정상 terminal이 되고,
handler domain Error 또는 receiver-close transport Error도 같은
`ReplyResponsibility`에서 구분된다. 이 숫자와 owner가 맞아야 retry 판단이
가능하다.

“request가 실패했다”라는 한 문장만으로는 부족하다. immediate Result가
실패했는지, admitted reply가 handler Error로 끝났는지, reply 전에
receiver가 닫혔는지, await owner가 Cancellation을 관찰했는지를 정확히
쓴다. 네 경우는 cleanup과 side-effect 관찰 범위가 다르다.

bounded와 logical-unbounded도 구현 queue 크기만 다른 별칭이 아니다.
bounded profile은 언어에 보이는 precommit `mailboxFull` admission을
만들지만 logical-unbounded profile은 그 capacity rejection을 만들지
않는다. 후자도 memory가 무한하다는 제품 보장은 아니며 runtime resource
failure를 임의의 `mailboxFull`로 재분류하지 않는다. 미니 trace에서
capacity clause 유무, admission error set, commit event count를 함께
적어야 두 profile을 정확히 비교할 수 있다.

request의 reply value와 transport responsibility도 분리한다. handler가
도메인 `LookupError`를 내는 경우와 reply 전달 전에 receiver가 닫히는
경우는 호출자가 선택할 재시도 정책이 다르다. `Reply<T>`의 correlation과
terminal transport residue를 bare value로 지우지 않는다.

## 9. Deeplus다운 작성 관례

retry를 설계하기 전에 commit 여부부터 구분한다. precommit failure는
sender owner를 보존하지만 postcommit failure는 message를 되돌리지
않는다. reply의 visible result type만 보고 책임 descriptor를 지우지 않는다.

## 10. 연습 문제

1. **따라 하기:** capacity 4 actor와 one-way send result를 작성하라.
2. **빈칸 완성:** request의 immediate type과 await 단계의 transport failure를
   채워라.
3. **스스로 설계하기:** mailboxFull에서 안전하게 retry할 수 있는 payload와
   receiverClosedBeforeReply에서 retry하기 위험한 operation을 비교하라.

## 11. 빠른 복습

- mailbox capacity는 positive static bound다.
- one-way와 request의 result shape이 다르다.
- admission과 reply failure는 commit 전후로 분리된다.
- actor crossing은 borrow/inout를 허용하지 않는다.

## 12. 정본 근거와 다음 장

- [mailbox/request 상세](../../grammar-reference/13-async-tasks-actors-and-concurrency.md)
- [actor contract](../../../spec/contracts/actor-concurrency-coherence.json)
- [type responsibility](../../../spec/types/type-system.md)

다음 장은 actor 밖의 명시적 shared-state owner와 최소 ordering law를
다룬다.
