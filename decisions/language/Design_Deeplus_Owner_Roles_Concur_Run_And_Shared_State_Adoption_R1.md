# Deeplus owner role·`concur`·`Run`·shared-state 수용 결정 R1

## 1. 상태

- 판정: `ACCEPT_WITH_GUARDS`
- 의미 P0: `0`
- OPEN feature P1: 기존 22건 유지
- 제품 레인: `15/15 NOT_RUN`
- 구현·제품 지원 주장: 없음

이 결정은 다음 다섯 설계 검토를 현행 Deeplus의 호출, callable profile,
소유권, actor transport 및 문법 경계에 맞게 하나로 재구성한다.

- owner-attached static role
- `concur + #async + Run<T>` 명명
- concur-local async lambda와 direct async spawn
- shared-state surface coherence
- `concur` region과 `RunGroup<T>`의 역할 분리

검토 입력은 읽기 전용으로 확인했으며 ZIP CRC, path safety와 nested
archive 부재를 통과했다.

| 입력 | bytes | SHA-256 |
|---|---:|---|
| `Supp_Deeplus_Owner_Attached_Static_Role_System_Design_Review_R1.zip` | 9,693 | `ec00c04b837eee4dc1f43ab035a5a07ee95e729785b28d664c9370c41cee1887` |
| `Supp_Deeplus_Concur_Async_Run_Naming_Design_Review_R1.zip` | 8,774 | `505564143c2941f4cbc1e45b616fdd64175c3e9c5e366bd281674957795ab635` |
| `Supp_Deeplus_Task_Local_Async_Lambda_and_Direct_Async_Spawn_Design_Review_R1.zip` | 10,237 | `67201926c68cd2ff47d2d41b329112cc7b5fd55401d3b73158f1e67a3e6cd4ca` |
| `Supp_Deeplus_Shared_State_Surface_Coherence_Design_Review_R1.zip` | 9,265 | `324f29ef1807975c4d15a4b65e6c6957e28a691727ea8ce64331031dc497db3d` |
| `Supp_Deeplus_Concur_Region_and_Run_Group_Necessity_Design_Review_R1.zip` | 11,903 | `9be5c7e761c3a55dff58a80eb7cf782fdb55365e1986d3498165bf78aadcd3da` |

## 2. 수용한 현재 표면

### 2.1 owner-attached role

`#role`은 바로 앞의 문법 owner에 붙고, owner가 닫힌 수용 집합과 정확한
tag 순서를 결정한다. 같은 단어라도 owner가 다르면 자동으로 같은 의미를
얻지 않는다. 알 수 없는 role, 중복 role 및 정의되지 않은 조합은
admitted HIR을 만들기 전에 거부한다.

현행 문법은 임의 provider role, 일반 role argument, 임의 조합을 열지
않는다. `def#async`, callable `#scoped`, `let#lazy`,
`enum#increasing/#decreasing`, `#mailbox(capacity: N)` 등은 각자의 기존
owner 계약을 유지한다. `class#sealed`, `if#likely`, `var#atomic` 같은
보고서의 예시는 현행 표면으로 수용하지 않는다.

비동기 순회는 owner-attached 표면으로 정리한다.

```deeplus
for#await item in stream {
    consume(item)
}
```

`#await`는 `for`에만 허용되는 built-in semantic role이다. 일반 `await
expr`은 별도의 prefix expression이며 두 표면은 같은 AST owner가 아니다.

### 2.2 structured concurrency

```deeplus
concur {
    let profile: Run<Profile> = spawn loadProfile(id)
    let settings: Run<Settings> = spawn loadSettings(id)

    render(await profile, await settings)
}
```

`concur`는 구조화된 동시성의 유일한 기본 lexical owner다. 영역 자체는
문장을 병렬화하지 않으며, 오직 `spawn`이 run을 만든다. 성공적으로
spawn된 모든 run의 lifetime, cancellation, terminal barrier, cleanup과
결정적 failure aggregation은 해당 `ConcurId`가 소유한다.

기존 `task scope`와 의미가 닫히지 않았던 `task group`은 호환 alias 없이
제거한다. 이름 있는 `concur name { ... }`도 현행에는 없다.

### 2.3 async invocation, direct spawn과 concur-local lambda

```deeplus
let direct = await loadProfile(id)
```

`await`는 선택된 async invocation을 현재 `ExecutionId`에서 실행하고
기다린다. bare async invocation은 background work나 `Run<T>`를 만들지
않으며 `await` 또는 `spawn`이 소비해야 한다.

```deeplus
concur {
    let run = spawn loadProfile(id)
    use(await run)
}
```

`spawn`은 정적으로 선택된 async invocation 또는 inline spawn body만
받는다. 동기식, 일반 값, 이미 생성된 `Run<T>`, actor request admission
결과는 거부한다. callee와 argument를 부모 실행에서 왼쪽부터 정확히 한
번 평가하고 검증한 뒤에만 `ConcurRunId`, `spawn_index`와 ownership
commit을 만든다. 실패 전에는 세 값 모두 만들어지지 않는다.

초기 concur-local async lambda는 다음 좁은 Stable design만 허용한다.

```deeplus
concur {
    let load = #async { id: UserId => await loadProfile(id) }
    let run = spawn load(id)
    use(await run)
}
```

- 가장 가까운 `concur`가 owner다.
- 빈 capture 또는 반복 호출이 증명된 값의 명시적 `copy` capture만
  허용한다.
- local `await`/`spawn`과 안쪽으로 중첩된 `concur`에서만 호출한다.
- return, export, storage, sibling/outward transfer, actor/shared carrier,
  unknown higher-order API 및 erased callable conversion을 거부한다.
- implicit outer access와 `move`/`clone`/`deep`/`borrow`/`inout` capture는
  초기 profile에서 거부한다.

일반적이거나 escaping하는 first-class async lambda는 계속
Preview Design nonactivatable이다.

### 2.4 `Run<T>`와 `Reply<T>`

`Run<T>`는 `spawn`이 만든 하나의 concur-owned execution handle이다.
`Reply<T>`는 성공적으로 admit된 actor request의 correlated reply
handle이다.

```deeplus
let Result::ok(reply) = directory :~ find id: id
else Result::err(error) => throw error

return await reply
```

Actor request의 즉시 타입은 다음과 같다.

```text
Result<Reply<T>, error ActorMessageError>
```

`Run<T>`와 `Reply<T>`는 암시적으로 변환·join·대입 호환되지 않는다.
둘 다 one-shot observation handle이며 반복 `await`는 거부한다.

정적 및 MIR identity domain은 다음처럼 분리한다.

```text
ExecutionId   일반 continuation
ConcurId      lexical structured owner
ConcurRunId   성공적으로 spawn된 execution
ReplyId       성공적으로 admit된 actor request reply
```

일반 suspension event는 `AsyncSuspend`/`AsyncResume`다.

### 2.5 shared-state 호출

```deeplus
let count = cell ~ withValue { borrow items => items.length }
let previous = cell ~ replace move updated
mutex ~ withLock { inout state => state.count += 1 }
```

`withValue`, `replace`, `withLock`은 receiver-bound Message call이며
`TildeCallLed`를 사용한다. `SharedCell::new(...)`와
`SharedMutex::new(...)` 같은 type-side constructor는 ordinary qualified
call로 남는다.

`#scoped`는 제거하지 않는다. 이는 선택된 callback type의
invocation-bounded callable profile이다. Lambda binder에는
`borrow value` 또는 `inout value`만 쓰며, callback profile이 region
owner와 escape/suspension 금지를 공급한다.

짧은 단일식 lambda는 폭과 주석이 허용하는 경우 한 줄이 canonical이다.

## 3. Preview로 수용한 항목

`RunGroup<T>`는 `PREVIEW_DESIGN_NONACTIVATABLE`이다. 두 번째 lexical
owner나 core statement가 아니라 하나의 `ConcurId` 안에서만 사는 동종
`Run<T>` observation/collection 값이다. 초기 설계는 Open → Sealed →
Terminal → Consumed, one-shot await, spawn-index 결과 순서, 결정적 failure,
남은 run cancellation 요청, cleanup 완료, partial result 없음 및 escape
금지를 요구한다.

Race, quorum, completion-order stream, concurrency limit와 backpressure는
`RunGroup<T>`의 묵시적 기본값이 아니며 별도 설계가 필요하다.

## 4. 기각하거나 수정한 제안

- 임의 custom owner role과 open provider extension은 수용하지 않는다.
- `class#sealed`, `if#likely`, `var#atomic` 예시는 현행 표면이 아니다.
- 정의되지 않은 여러 role 조합은 수용하지 않는다.
- `#scoped` 전면 제거는 현행 Stable callable profile과 충돌하므로
  기각한다.
- `TaskGroupStmt`를 이름만 바꾼 별도 concurrency group은 만들지 않는다.
- `RunGroup<T>`를 execution lifetime owner로 만들지 않는다.
- actor request와 spawn 결과를 한 nominal handle로 합치지 않는다.
- bare async invocation은 암시적으로 실행되거나 detached되지 않는다.

## 5. 검증 경계

정적 fixture, JSON/schema parse 및 문서 생성은 설계 일관성 증거다.
Parser, checker, HIR, MIR, xVM, Cranelift, formatter/LSP와 backend-equivalence
제품 실행은 계속 `NOT_RUN`이다. 이 결정은 기존 feature P1을 닫거나
새 P1을 만들지 않는다.
