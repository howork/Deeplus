# 비동기, 태스크, 액터와 동시성

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 Deeplus의 비동기 함수, 명시적 중단점, 구조화된 태스크,
비동기 순회, 액터 격리, 메시지 admission, mailbox backpressure,
취소·실패·정리 순서와 공유 상태 경계를 함께 설명한다.

현행 설계 계약은 다음을 허용한다.

- 이름 있는 `def#async` 선언과 명시적 `await`;
- `task scope`, `task group`, `spawn`으로 표현하는 구조화된 태스크;
- `for await` 비동기 순회;
- `actor`, 선택적 `#mailbox(capacity: N)`, `on`, `request`;
- actor protocol의 `send`와 `request` 요구 사항;
- `receiver ~ message(...)` 형태의 비동기 메시지 전송.

이 장의 현행 예제는
`examples/guide/review-corpus.md`에서 `expected_outcome: accept`,
`source_activation: none`인 항목을 그대로 인용한다. 제품 parser,
checker, MIR, xVM, LLVM, formatter, LSP를 이 문서 작성 과정에서 실행하지
않았으며 제품 lane은 정확히 `15/15 NOT_RUN`이다. 정적 계약의 존재는
구현 완료, 제품 지원 또는 실행 적합성을 뜻하지 않는다.

## 문법

### 비동기 함수와 명시적 중단

```ebnf
DefIntroducer ::= "def" HashTag* ;
AsyncForLoop ::= "for" "await"
                 ("let" Pattern | Pattern)
                 "in" Expr GuardClause? Block ;
```

`def#async`는 `def`에 현행 callable profile `#async`를 붙인 이름 있는
선언이다. `await`는 expression prefix parselet이 소유하는 단항
연산자다. 최상위 `await`는 현행 Stable script root에서 허용되지 않으며
필요하면 `def#entry#async` 같은 허용된 비동기 owner 안으로 옮긴다.

`for await`는 하나의 `AsyncForLoop` 문법 owner다. `for`와 `await` 사이를
다른 구문이 나누지 않으며, 현재의 동기 `for`와 별도 의미 규칙을 갖는다.

### 구조화된 태스크

```ebnf
TaskGroupStmt ::= "task" "group" Identifier? Block ;

SpawnExpr ::= "spawn" TaskBody ;
TaskBody ::= "{" "=>" TaskBodySequence "}"
           | "async" "{" "=>" TaskBodySequence "}" ;
TaskBodySequence ::= LineBreakBoundary? BlockSequence ;

StructuredTaskScope ::= "task" "scope" Block ;
```

`spawn { => ... }`와 `spawn async { => ... }`는 제한된 task body
표면이다. 이것은 일반 closure 문법을 비동기 callable로 바꾸지 않는다.
모든 현행 child task는 lexical task scope나 허용된 task group에
소속된다.

`receiver ~ spawn`은 별도의 task-spawn suffix가 아니다. 일반
`MessageSuffix`가 `spawn` selector를 파싱하고 HIR이 예약된 의미를
결정한다. 같은 표면을 소유하는 두 번째 suffix 문법은 허용되지 않는다.

### 액터와 액터 프로토콜

```ebnf
ActorDecl ::= TopLevelVisibility? "actor" MailboxClause?
              Identifier ActorBody ;
MailboxClause ::= HashTag "(" "capacity" ":" StaticIntLiteral ")" ;
ActorBody ::= "{" ActorItem* "}" ;
ActorItem ::= ActorOnDecl | ActorRequestDecl | MemberDecl ;
ActorOnDecl ::= MemberVisibility? "on" Identifier
                ParameterList? ThrowsClause? EffectsClause?
                FunctionBody ;
ActorRequestDecl ::= MemberVisibility? "request" Identifier
                     ParameterList? ReturnClause ThrowsClause?
                     EffectsClause? FunctionBody ;

ActorProtocolDecl ::= TopLevelVisibility? "protocol" Identifier
                      ActorProtocolBody ;
ActorProtocolBody ::= "{" ActorProtocolItem* "}" ;
ActorProtocolItem ::= ActorProtocolSendRequirement
                    | ActorProtocolRequestRequirement ;
ActorProtocolSendRequirement ::= "send" Identifier ParameterList?
                                 ThrowsClause? EffectsClause?
                                 StatementBoundary ;
ActorProtocolRequestRequirement ::= "request" Identifier ParameterList?
                                    ReturnClause ThrowsClause?
                                    EffectsClause? StatementBoundary ;
```

`MailboxClause`에서 현재 허용되는 tag는 정확히 `#mailbox`다.
`capacity`는 양의 `StaticIntLiteral`이어야 한다. actor 안의 `on`은
one-way handler이고 `request`는 응답형을 갖는 handler다. protocol의
`send`와 `request`는 각각 이 두 handler 계열의 요구 사항이다.

### 메시지 접미 구문

```ebnf
MessageSuffix ::= "~" MessageSelector MessageArguments? ClosureExpr? ;
MessageSelector ::= Identifier | QualifiedExtensionSelector ;
MessageArguments ::= ArgumentList | AtomicCallArgument ;
```

액터 메시지도 일반 `MessageSuffix`를 사용하지만 ordinary method
호출로 폴백하지 않는다. selector는 enqueue 전에 actor 또는 actor
protocol domain에서 정적으로 결정된다. 런타임 문자열 lookup이나
source order에 따른 overload 승자는 없다.

### 비동기 범위 한정자

```ebnf
AtScopeExpr ::= "@" "scope" ScopeModifier* ValueBody ;
ScopeModifier ::= "isolated" | "cancellable" | "shielded" ;
```

이 modifier는 기존 경계를 보존할 뿐 숨은 권한을 만들지 않는다.
`shielded`도 Cancellation을 버리거나 Error로 바꾸지 않고 정리를
건너뛰지 않는다.

## 허용과 정적 의미

### 비동기 호출 가능 값과 `await`

이름 있는 비동기 선언은 현행이다. 호출 결과를 기다리는 지점은 항상
소스의 `await`로 드러난다. `await`는 task나 메시지를 만들지 않고,
피연산자가 독립적으로 awaitable이어야 한다. 일반 lambda 호출은
동기식이며 암시적 async 변환은 없다.

비동기 중단점에서도 다음 증명이 유지되어야 한다.

- live borrow와 `inout`의 region이 중단을 가로질러도 안전하다.
- actor isolation과 현재 actor turn의 mutation 권한이 보존된다.
- Cancellation 관찰과 cleanup 책임이 사라지지 않는다.
- callable의 effect, error, isolation, suspension 책임이 호환된다.

### 구조화된 동시성

task scope나 허용된 task group은 모든 child task의 owner다. scope는
각 child가 join되거나 취소되고 필수 cleanup이 끝날 때까지 종료할 수
없다. 현행 Deeplus에는 detached child 권한이 없으며, 별도 owner-transfer
계약 없이 task handle이 scope 밖으로 escape하면 거부된다.

관찰되지 않은 child failure도 scope의 terminal outcome에서 사라지지
않는다. task group의 세부 collect/join 정책과 반복 `await` 규칙은
target-bound checker/runtime 증거가 필요한 미완료 제품 gate다. 문법이
존재한다는 사실만으로 임의 기본 정책을 부여하지 않는다.

### 현행 `AsyncCollector` 표준 라이브러리 프로필

`AsyncCollector::list<T,U,ES,ET>`는 async comprehension을 대신하는
정책 노출형 current stdlib 설계다. 입력은 **finite evidence가 있는**
`AsyncSequence<T, ES>`, policy는 현재 `CollectPolicy::sequential`,
transform은 이름 있는 `#async (T) -> U throws ET`다. 결과의 error channel은
정확히 normalize된 `ES | ET`이고 Cancellation은 이 Union 밖의 별도
제어 결과다.

평가는 source order를 보존하고 buffer bound는 1이다. 첫 failure에서
fail-fast하고 pending child가 있으면 취소한 뒤 cleanup barrier를 지난다.
전체 성공 전에는 partial `List<U>`를 publish하지 않는다. source failure,
transform failure, Cancellation을 서로 바꾸거나 지우지 않는다.

현행 예제 `EX-R51a1-ACOLLECT-P-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public def#async collectProfiles(userIds: AsyncSequence<UserId, IOError>) -> List<Profile>
    throws IOError | NetworkError = {
    // checker evidence for `userIds` proves a finite source
    // loadProfileForCollect: #async (UserId) -> Profile throws NetworkError
    return await AsyncCollector::list(
        source: userIds,
        policy: CollectPolicy::sequential,
        transform: loadProfileForCollect,
    )
}
```

같은 signature라도 source의 finiteness가 증명되지 않으면
`ASYNC_COLLECTOR_POLICY_NOT_ADMITTED`로 거부된다. 이 프로필은 일반
async callable literal이나 async comprehension 구문을 활성화하지 않는다.

### 액터 격리와 turn

각 actor identity는 하나의 격리된 mutable state region과 mailbox를
소유한다. 한 번에 하나의 admitted actor turn만 그 상태를 변경한다.
turn이 `await`에서 중단되어도 같은 turn identity와 mutation/dequeue
권한을 유지한다. 그동안 새 메시지가 mailbox에 들어올 수는 있지만,
중단된 turn이 끝나기 전에는 다른 turn이 actor state를 관찰하거나
변경하지 않는다.

checker가 자기 자신 또는 dependency cycle에 의해 진행 불가능한
request-await를 정적으로 증명하면 거부한다. 교착을 피하려고 암시적
재진입을 추가하거나 actor authority를 잠시 풀어 주지 않는다.

actor 경계를 건너는 입력은 다음 중 하나여야 한다.

- `move`로 넘기는 owned value와 `Transferable` 증명;
- 명시적으로 공유되는 value와 `Shareable` 증명.

borrow나 `inout` payload는 격리 경계를 건널 수 없다. actor reference가
있다는 사실만으로 주변 authority나 protocol conformance를 추론하지
않는다.

### 사서함 프로필과 역압

mailbox clause가 없으면 `logical_unbounded_v1`이다. 이것은
언어 수준의 capacity rejection이 없다는 뜻일 뿐, 구현 저장 공간이
무한하다는 뜻이 아니다. 자원 고갈을
`ActorMessageError::mailboxFull`로 바꾸지도 않는다.

`#mailbox(capacity: N)`이 있으면 `bounded_reject_v1`이다. `N`은 양의
정적 정수이며, mailbox가 가득 찬 경우 enqueue commit 전에 즉시
`Result::err(ActorMessageError::mailboxFull)`을 반환한다. 현행 bounded
profile은 대기, suspension, 암시적 retry, silent drop을 하지 않는다.
동적 capacity와 mailbox 정책 selector 문법도 없다.

`ActorMessageError`의 현행 closed family는 정확히 다음 세 case다.

| case | 발생 단계 |
|---|---|
| `mailboxFull` | bounded mailbox가 가득 찬 precommit admission |
| `receiverClosedBeforeAdmission` | receiver가 admission 전에 닫힌 precommit |
| `receiverClosedBeforeReply` | admitted request의 reply 전에 receiver가 닫힘 |

Cancellation은 이 error family로 바뀌지 않는다.

### 단방향 전송과 요청

one-way message expression의 정확한 형식은
`Result<Unit, error ActorMessageError>`이다. `Result::ok(Unit)`은 enqueue
commit 뒤에만 생기며 reply channel은 없다.

reply type이 `T`인 request expression의 즉시 형식은
`Result<Task<T>, error ActorMessageError>`이다. source는 먼저 admission
`Result`에서 `Task<T>`를 꺼낸 뒤 그 task에 `await`를 적용해야 한다.
request enqueue commit 뒤에 correlation identity가 한 번 만들어지며,
reply, 선언된 failure, Cancellation 중 정확히 하나로 끝난다. request를
ordinary method return처럼 취급하거나 암시적으로 기다리지 않는다.

visible type spelling의 `Task<T>`가 handler의 declared ErrorSet을 지우지는
않는다. typed HIR, module API digest와 MIR은 non-forgeable
`TaskResponsibility`를 함께 보존한다. 이 descriptor는 result type,
normalized handler ErrorSet, Cancellation axis, isolation owner,
`correlation_id`와 terminal transport failure를 가진다. terminal
transport failure 집합은 정확히
`{receiverClosedBeforeReply}` 하나다. `mailboxFull`과
`receiverClosedBeforeAdmission`은 enqueue commit 전 admission `Result`의
오류이므로 이 descriptor에 들어가면 안 된다. 따라서
`throws E`인 request handler의 task를 await하면 정확히
`E | ActorMessageError::receiverClosedBeforeReply`가 노출된다. 이를
`Task<T,E>`라는 새 source type으로 임의 재작성하거나 Error를
Cancellation으로 접지 않는다.

이 residue는 타입을 출력할 때만 붙이는 설명용 주석이 아니다.
compatibility, control-flow join, collection이나 field storage, module API
export/import가 모두 보존해야 하는 정적·값 책임이다. 기본 compatibility는
`result_type`, normalized handler ErrorSet, Cancellation axis, isolation
owner와 terminal transport failure의 정확한 normalized equality를
요구한다. 서로 다른 request 값의 `correlation_id`는 같게 만들지 않고 각
값에 그대로 따라간다. 오직 checker가 명시적으로 받아들인 ErrorSet
subsumption proof가 있을 때만 handler ErrorSet을 더 넓은 집합으로 올릴 수
있으며, 이 경우에도 나머지 field와 각 correlation identity는 지워지지
않는다. bare `Task<T>`만 남기는 join/export는
`RCTS_RESPONSIBILITY_AXIS_DROPPED`, 증명 없이 error set을 합치는 조합은
`RCTS_RESPONSIBILITY_COMBINATION_INVALID` 계열로 거부한다.

module API digest는 아직 존재하지 않는 runtime request ID를 미리 만들지
않는다. 대신 actor-request result channel의 descriptor shape와
`correlation_id = per_value_non_forgeable` 정책 marker를 canonical bytes에
기록한다. 실제 enqueue commit이 일어나면 typed HIR/MIR의 value-level
residue가 그 request만의 concrete correlation identity를 보존한다.

이 규칙은 모든 `Task<T>`에 actor transport 의미를 붙이지 않는다.
ordinary `def#async` 호출이나 structured `spawn`이 만든 task의
`task_origin`은 `ordinary_async`이며 actor correlation이나
`receiverClosedBeforeReply` descriptor를 가지면 오히려 거부된다. enqueue
commit을 성공한 request가 만든 task만 `actor_request_admitted` origin을
가지며 위 여섯 field descriptor가 필수다. 두 origin은 source type
spelling을 바꾸지 않고 typed HIR/API/MIR residue로 구분한다.

예를 들어 handler가 `throws LookupError`라면 admission 식 자체의 오류는
여전히 `mailboxFull | receiverClosedBeforeAdmission`이고, 성공 branch에서
꺼낸 task를 `await`할 때의 오류만
`LookupError | receiverClosedBeforeReply`다. 두 시점의 오류를 하나의
큰 `ActorMessageError` 집합으로 미리 합치면 commit 전·후 책임 경계와 owner
보존 여부를 구별할 수 없으므로 현행 계약에 맞지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
public protocol DirectoryProtocol {
    request find(id: Int) -> Status throws LookupError
}

actor Directory {
    request find(id: Int) -> Status throws LookupError = {
        return loadStatus(id)
    }
}

def#async inspect(directory: Directory, id: Int) -> Status
    throws ActorMessageError | LookupError = {
    let Result::ok(task) = directory ~ find(id)
    else Result::err(admissionError) => throw admissionError

    return await task
}
```

`directory ~ find(id)`가 실패하는 순간에는 task 자체가 아직 없으므로
`mailboxFull` 또는 `receiverClosedBeforeAdmission`만 admission error로
다룬다. `Result::ok(task)` 뒤에는 correlation이 존재하고, `await task`는
handler의 `LookupError` 또는 유일한 terminal transport failure인
`receiverClosedBeforeReply`로 끝날 수 있다. source에는 여전히
`Task<Status>`만 보이지만 두 단계의 책임은 HIR/API/MIR descriptor가
구별한다.

handler spelling만으로 actor protocol conformance가 생기지 않는다.
요구 사항과 handler identity의 결합은 checker가 별도 conformance
규칙으로 확인해야 한다.

### 순서 보장

현행 FIFO key는 정확히
`(sender identity, receiver actor identity, mailbox profile identity)`다.
같은 key에서 성공적으로 commit된 메시지만 `channel_sequence`가
엄격하게 증가하고 그 순서로 dequeue된다. 거부된 시도에는 sequence가
없다.

언어가 보장하는 최소 happens-before edge는 다음과 같다.

- 한 task 안의 program order;
- parent의 spawn 이전 동작에서 child start로의 순서;
- child terminal과 cleanup에서 해당 `await` resume으로의 순서;
- 성공한 enqueue에서 일치하는 dequeue로의 순서;
- Cancellation cleanup 완료에서 scope exit로의 순서.

서로 다른 sender 사이의 global FIFO, cross-sender tie-break, scheduler
fairness, distributed delivery, exactly-once delivery는 보장하지 않는다.

## 평가·소유권·효과

### 메시지 평가와 커밋

메시지 전송은 receiver를 정확히 한 번 평가하고, 인수를 왼쪽에서
오른쪽으로 정확히 한 번 평가한다. prepare 단계에서는 아직 owner를
넘기지 않는다. 성공한 enqueue commit이 유일한 소유권 이전점이다.

- precommit 실패에서는 sender가 모든 moved owner를 유지한다.
- 성공한 commit에서는 receiver actor가 각 moved owner를 정확히 한 번
  얻는다.
- postcommit에는 메시지를 철회하거나 owner를 sender에게 되돌리지
  않는다.
- 모든 terminal path에서 cleanup owner는 정확히 하나다.

Cancellation이 commit 전에 관찰되면 message와
`channel_sequence` 없이 중단되고 sender가 owner를 유지한다. commit
후에 관찰되면 이미 actor가 소유한 payload와 admission `Result`를
되돌리지 않는다. admitted request를 기다리는 task의 Cancellation은
그 correlation에 결합되지만 메시지 자체를 철회하지 않는다.

### 액터 턴의 중단

actor handler가 `await`해도 state region을 다른 mutating turn에
넘기지 않는다. 이 규칙은 actor state가 중단 사이에 예상치 못하게
바뀌는 재진입 오류를 막는다. 반대로 긴 `await`는 actor 진행성을
제한할 수 있으므로, 프로그램은 독립 작업을 child task로 구조화하고
self-request dependency cycle을 만들지 않아야 한다.

### 취소, 실패와 정리

Cancellation은 Error와 Defect와 구분되는 제어 결과다. 최소 순서는
요청, 관찰, cleanup 완료, terminal cancellation이며 cooperative
boundary에서만 관찰한다. `catch`가 Cancellation을 Error처럼 회복하거나
cleanup을 우회할 수 없다.

task scope의 실패 집계는 scheduler 완료 순서와 무관하다.

1. body failure가 있으면 cleanup failure보다 먼저 primary로 보존한다.
2. child failure만 경쟁하면 lexical `spawn_index`가 가장 작은 것이
   primary다.
3. 나머지 child failure는 `spawn_index` 오름차순으로 suppressed된다.
4. cleanup failure는 실제 LIFO cleanup 실행 순서로 뒤에 붙는다.

`defer`와 resource cleanup은 return, throw, break, Cancellation,
suspension 어느 경로에서도 정확히 한 번 실행되어야 한다.

### MIR 관찰 식별자

정확한 하위 표현은 구현될 때 task scope, task, actor, sender, channel,
mailbox profile, message, channel sequence, request correlation identity를
보존해야 한다. spawn/join, Cancellation lifecycle, enqueue/dequeue,
admission 성공·거부, request lifecycle, primary/suppressed failure가
필수 event family다. 이 문서는 아직 없는 backend event를 암시적으로
만들지 않는다.

## 현행 예제

### 이름 있는 비동기 함수와 명시적 `await`

현행 예제 `EX-R51a1-NEW-017`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def#async fetch(url: String) -> Bytes
    throws NetworkError
    effects {io}
= {
    return await client ~ get(url)
}
```

호출자는 `url`을 한 번 평가하고 이름 있는 `def#async` 호출로
`Bytes` 성공 channel, `NetworkError` 오류 집합과 `io` effect를 가진 task
책임을 얻는다. body의 `client ~ get(url)` message/call 결과를 `await`하는
지점만 명시적 suspension point이며 성공하면 그 `Bytes`를 반환한다.
failure나 Cancellation은 숨은 `Option`으로 바뀌지 않고 cleanup region을
통과해 선언된 channel로 전파된다. 실제 task 생성·suspend·resume과 backend
실행은 `NOT_RUN`이다.

### 비동기 순회

현행 예제 `EX-R51a1-066`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def#async consume(stream: AsyncSequence<Int, Never>) -> Unit = {
    for await value in stream {
        print(value)
    }
}
```

`stream`은 item `Int`, source error `Never`인 `AsyncSequence`다. `for await`는
다음 item 요청, suspension, resume, binder commit, body를 source order로
반복하며 한 번에 한 item만 `value`에 결합한다. `print`의 `io` 책임은
주변 callable contract가 별도로 보존해야 하고, loop 종료나 Cancellation은
pending item과 body cleanup을 마친 뒤 terminal이 된다. sequence를
`List<Int>`로 미리 수집하거나 재생 가능하다고 가정하지 않는다. 제품
iterator/task 실행은 `NOT_RUN`이다.

### 구조화된 자식 태스크

현행 예제 `EX-R51a1-025`,
원본 `examples/guide/review-corpus.md`:

```deeplus
task scope {
    let profile = spawn async { =>
        await loadProfile(id)
    }
    await profile
}
```

`task scope`가 child owner다. `spawn async`는 `loadProfile(id)`를 수행할
하나의 child task handle `profile`을 만들고, `await profile`은 그 handle의
완료를 명시적으로 기다린다. scope 정상·오류·Cancellation 종료 모두에서
admitted child가 terminal이 될 때까지 join/cleanup barrier를 통과하므로
detached child나 숨은 background work가 남지 않는다. child failure는
정해진 scope failure ordering을 따르며 실제 scheduler 실행은
`NOT_RUN`이다.

### 용량 제한 액터, 전송과 요청

현행 예제 `EX-R51f3-COH-008`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public protocol CounterProtocol {
    send add(value: Int)
    request current() -> Int
}
public actor #mailbox(capacity: 8) Counter {
    on add(value: Int) = { }
    request current() -> Int = { return 0 }
}
public def#async observe(counter: Counter) -> Int
    throws ActorMessageError
= {
    task scope {
        let Result::ok(_) = counter ~ add(value: 1)
        else Result::err(error) => throw error
        let Result::ok(_) = counter ~ add(value: 2)
        else Result::err(error) => throw error
        let Result::ok(replyTask) = counter ~ current()
        else Result::err(error) => throw error
        return await replyTask
    }
}
```

두 `add` 전송과 한 `current` 요청은 source order로 준비된다. 각 `~`는
receiver와 argument를 한 번 평가하고 mailbox capacity/admission을 통과한
enqueue commit에서만 message와 이동 owner를 actor에 넘긴다. 전송의
`Result::ok`는 성공 enqueue를, 요청의 `Result::ok(replyTask)`는 reply를
기다릴 task handle을 뜻한다. 같은 sender/receiver/protocol key에서는
두 add 뒤 current가 FIFO로 관측되어야 하며, rejection은
`ActorMessageError`로 끝나고 다음 tier로 fallback하지 않는다. parser,
checker, mailbox와 scheduler 실행은 모두 `NOT_RUN`이다.

### 취소 경계의 구조화된 정리

현행 예제 `EX-R51f3-COH-011`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public def#async supervise() -> Unit = {
    task scope {
        defer cleanup()
        let child = spawn async { => await work() }
        await child
    }
}
```

scope 진입 시 `defer cleanup()`을 현재 cleanup region에 등록한 뒤 child를
spawn하고 명시적으로 await한다. child 성공·실패 또는 parent Cancellation
어느 경우에도 child terminal/join 뒤 `cleanup()`이 정확히 한 번 실행되어
scope barrier를 닫는다. primary failure와 cleanup failure가 함께 나면
정해진 primary/suppressed 순서를 보존하고 Cancellation을 ordinary Error로
접지 않는다. 실제 cancellation race와 cleanup trace 실행은 `NOT_RUN`이다.

### 사서함 절 생략

현행 예제 `EX-R51f3-COH-012`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public actor Worker {
    on run(job: Job) = { }
}
public def dispatch(worker: Worker, move job: Job)
    -> Result<Unit, error ActorMessageError>
= {
    return worker ~ run(move job)
}
```

이 예제의 생략된 clause는 `logical_unbounded_v1`을 선택한다. `move job`의
owner는 enqueue commit에서만 actor로 넘어간다. `worker ~ run(move job)`의
정적 결과는 `Result<Unit, error ActorMessageError>`이고 receiver와 `job`을
한 번씩 평가한다. admission이나 enqueue가 실패하면 `job`은 actor에
부분 전달되지 않고 caller 쪽 실패 경계가 owner를 보존한다. 성공하면
`job` owner가 mailbox message로 넘어가며 handler completion을 기다리는
request task는 생성되지 않는다. logical-unbounded는 물리적 무한 메모리를
보장하지 않고 제품 mailbox/runtime 실행은 `NOT_RUN`이다.

## 거부되거나 격리된 형식

### 현행에서 거부되는 형식

| 형식 또는 주장 | 판정 |
|---|---|
| `actor #mailbox(capacity: 0) ...` | 양의 `StaticInt`가 아니므로 거부 |
| 동적 mailbox capacity | 현행 최소 profile에서 거부 |
| mailbox full에서 암시적 대기·retry·drop | 거부 |
| actor 경계의 borrow 또는 `inout` payload | 격리 위반으로 거부 |
| actor state의 외부 직접 변경 | actor isolation 위반으로 거부 |
| message selector의 ordinary method 폴백 | 거부 |
| request admission `Result`를 풀지 않고 바로 `await` | 거부 |
| `catch ...: Cancellation`으로 회복 | Cancellation/Error 분리 위반 |
| lexical scope를 벗어나는 detached child | 현행 authority 없음 |
| top-level `await` | Stable script root에서 거부 |
| 서로 다른 sender 사이의 global FIFO 또는 fairness 주장 | 보장되지 않음 |

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### `PREVIEW_NONACTIVATABLE`: 일반 비동기 호출 가능 리터럴

후보 surface는 corpus가 회복·진단용으로 고정한 `#async{ => ... }`다.
의도된 의미는 중단 가능한 callable value이지만, 현행 ordinary lambda는
동기식이고 이 후보는 source gate가 없는 `PREVIEW_DESIGN`이다.

비활성 예제 `EX-R51a1-AUD-NG-023`:

```deeplus
let f = #async{ => await load() }
```

활성화 전에는 다음이 모두 닫혀야 한다.

1. 호출 결과와 return 형식, `await` 책임;
2. capture의 move/borrow/inout 및 escape 수명;
3. Error, Defect, Cancellation, effect와 isolation 호환성;
4. task owner와 구조화 scope 결합;
5. AST/HIR/MIR lowering identity와 xVM/LLVM ABI;
6. parser/checker/formatter/LSP 진단과 target-bound 실행 증거.

현행 대안은 이름 있는 `def#async` 선언이다.

### `PREVIEW_NONACTIVATABLE`: 비동기 컴프리헨션

async comprehension은 feature catalog에 `PREVIEW_DESIGN`으로 남아 있지만
현행 exact EBNF와 source gate가 없다. `for await` statement와 stdlib
`AsyncCollector`가 이 후보를 암시적으로 활성화하지 않는다. 후보가
활성화되려면 comprehension의 exact surface, finite-source 조건, 순서와
backpressure, transform의 error-set union, Cancellation, 부분 결과의
cleanup, lowering과 tooling 계약이 먼저 정해져야 한다.

정확한 후보 철자가 아직 정본화되지 않았으므로 이 문서는 예시 구문을
발명하지 않는다. 철자 부재 자체가 비활성 경계다.

### `PREVIEW_NONACTIVATABLE`: 경량 세션 프로토콜 공급자

`session_protocol_lite_provider`는 actor message에 protocol-state 증거를
제공하려는 Preview-design provider다. 현행 `send`/`request` protocol은
session 진행 상태, distributed delivery 또는 exactly-once delivery를
보장하지 않는다. 이 후보에는 현재 source syntax가 없다.

활성화하려면 provider input/output identity, 상태 전이의 totality와
linearity, actor handler conformance, cancellation·receiver closure 시
세션 terminal 규칙, MIR correlation, versioned evidence와 재현 가능한
target receipt가 필요하다.

### `PREVIEW_NONACTIVATABLE`: 약한 원자 순서

약한 atomic ordering은 닫힌 memory model과 target receipt가 없는
Preview-design이다. actor의 enqueue/dequeue 순서와 stdlib
`SharedCell`/`SharedMutex`의 현행 보장을 약화하지 않는다. source
spelling, ordering lattice, data-race 법칙, compiler reorder 한계,
xVM/LLVM parity와 litmus 실행 증거가 닫히기 전에는 사용할 수 없다.

위 Preview 설명은 activation, feature P1 폐쇄, 구현 권한 또는 제품
PASS가 아니다. 이 장은 기존 feature P1을 닫거나 새 P1을 만들지 않는다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- callable profile, lambda와 호출 규칙은
  [함수, 메서드, 클로저와 호출](05-functions-methods-closures-and-calls.md)을
  함께 본다.
- actor protocol conformance와 Trait evidence는
  [클래스, Trait, conformance와 extension](06-classes-traits-conformance-and-extensions.md)을
  함께 본다.
- `Result`, Error/Defect/Cancellation, `defer`와 suppression 순서는
  [제어 흐름, 오류, 효과와 정리](11-control-flow-errors-effects-and-cleanup.md)을
  함께 본다.
- `move`, borrow/inout escape, `Transferable`, `Shareable`, shared-state
  profile은
  [소유권, 대여와 책임](12-ownership-borrowing-and-responsibility.md)을
  함께 본다.
- `let Result::ok(...) else ...` admission 처리는
  [패턴, 구조 분해와 매칭](10-patterns-destructuring-and-matching.md)의
  refutable binding 규칙을 따른다.
- `AsyncSequence<T, E>`의 `E`는 ErrorSet이며 Cancellation을 포함하지
  않는다.
- actor message는 `~` suffix를 사용하지만 ordinary method dispatch와
  actor admission은 서로 다른 의미 owner다.
- shared-state closure는 중단할 수 없다. 그 안에서 `await`하거나 scoped
  observation을 escape하면 거부된다.

## 정본 근거

- `spec/grammar/deeplus.ebnf`
  - `DefIntroducer`, `AsyncForLoop`, `TaskGroupStmt`, `SpawnExpr`,
    `StructuredTaskScope`, `ActorDecl`, `ActorProtocolDecl`,
    `MessageSuffix`, `AtScopeExpr`.
- `spec/language.md`
  - 비동기 함수·task·suspension, actor와 message, Preview·비현행 경계.
- `spec/contracts/actor-concurrency-coherence.json`
  - `ACC-R001..R018`, mailbox profile, actor admission, structured task,
    Cancellation, ordering, MIR와 제품 증거 경계.
- `spec/contracts/type-flow-callable-coherence.json`
  - 이름 있는 async 선언과 비활성 async callable literal의 구분.
- `spec/contracts/shared-state-coherence.json`
  - `Shareable`, `SharedCell`, `SharedMutex`의 현행 stdlib 경계.
- `spec/mir/semantics.md`
  - task/actor identity, enqueue commit, channel sequence, failure와 cleanup
    event 순서.
- `spec/features/gates.json`
  - `async_callable_literal_profile`, `async_comprehension`,
    `session_protocol_lite_provider`, `weak_atomic_ordering`의
    nonactivatable 상태.
- `spec/features/catalog/`
  - 기능별 상태, authority와 제품 실행 상태.
- `examples/guide/review-corpus.md`
  - 이 장의 현행·거부 예제와 `design_static_product_not_run` 경계.

정적 문서 투영 결과는 actor/concurrency 설계 계약을 변경하지 않는다.
미완료 제품 gate `ACC-G001..ACC-G005`에는 target-bound parser/checker/
MIR/xVM 및 schedule-permutation 실행 증거가 필요하다. 현재 제품
receipt 수는 0이며 제품 lane은 `15/15 NOT_RUN`이다.
