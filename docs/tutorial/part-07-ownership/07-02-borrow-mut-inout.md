# 7.2 `borrow`, `mut`, `inout`

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

parameter mode와 type ownership qualifier는 현행 표면이다. 같은 단어라도
call channel과 normalized type responsibility를 한 identity field로
합치지 않는다.

## 2. 학습 목표

- `borrow`를 nonowning view로 사용한다.
- `inout`을 caller place의 exclusive dynamic access로 이해한다.
- `mut` parameter가 callee-owned local place임을 설명한다.
- live borrow, mutation, suspension과 escape의 충돌을 찾는다.

## 3. 선수 지식

place state와 move commit을 알고 있어야 한다.

## 4. 문제에서 출발하기

함수가 큰 Buffer를 읽기만 하는데 owner를 옮길 필요는 없다. 반대로 같은
caller place를 직접 갱신해야 하면 복사본을 바꾸어서는 안 된다. `borrow`,
`mut`, `inout`은 이 세 책임을 구분한다.

## 5. 핵심 모델

| mode | callee가 얻는 것 | caller 관계 |
|---|---|---|
| `borrow x: T` | nonowning read view | owner 유지 |
| `mut x: T` | callee-owned mutable local place | write-back alias 없음 |
| `inout x: T` | caller exact place의 exclusive access | 같은 place에 commit |
| `move x: T` | transferred owner | source는 성공 뒤 moved |

`mut T` type qualifier는 unique mutable owner 책임이다. `inout`
parameter의 다른 철자가 아니다.

### type qualifier를 별도 축으로 읽기

type 위치에는 `owned T`, `borrowed T`, `mut T`, `inout T`가 올 수 있다.
각각 명시적 owner, shared read view, mutable owner, exclusive mutable
view를 뜻한다. 접두사가 없는 `T`도 별도 상태이며 자동으로 `owned T`가
되지 않는다. `borrowed`와 `inout` view에는 checker가 추적하는 owner
region이 필요하지만, 사용자가 존재하지 않는 lifetime 이름을 문법에
만들어 적지는 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let owner: owned Box<Node> = Box!(Node!(value: 1))
let writable: mut Buffer = Buffer!()
let view: borrowed Bytes = borrow bytes
```

`var value: T`는 binding을 다시 대입할 수 있다는 뜻이고 `value: mut T`는
그 값이 unique mutable owner라는 뜻이다. 같은 이유로 다음 두 parameter는
같지 않다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def localCopy(mut value: Buffer) -> Unit = {
    value = normalize(value)
}

private def receiveMutableOwner(value: mut Buffer) -> Unit = {
    value ~ normalizeInPlace
}
```

첫 함수의 `mut`는 callee local channel mode다. 둘째 함수의 parameter
mode는 ordinary이고 `mut`는 value type qualifier다. formatter는 두
표면을 서로 바꾸지 않는다.

함수 타입 안에서는 바깥 `)` 다음의 `->`가 보일 때만 직접 선행하는
`borrow`, `mut`, `move`, `inout`를 anonymous channel mode로 읽는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let inspect: #scoped (borrow Bytes) -> Int = #scoped{ borrow data => data.length }
let edit: #scoped (inout Buffer) -> Unit = #scoped{ inout data => data ~ clear }
let takeMutableOwner: ((mut Buffer)) -> Unit = { value: mut Buffer => value ~ clear }
```

마지막 예제의 안쪽 괄호는 `mut`를 channel mode가 아니라 type qualifier로
유지한다. qualifier를 겹쳐 쓰거나 unbound borrowed result를 반환하거나
`inout T`를 field/static/escaping capture에 저장하는 코드는 거부된다.

## 6. 단계별 예제

### 깊이 읽기: parameter mode를 호출 책임으로 읽기

ordinary parameter는 callee local value를 받는다. `borrow`는 caller
owner를 유지한 shared read region, `inout`은 caller place 하나에 대한
exclusive mutable borrow, `mut`는 callee가 소유한 mutable local을 뜻한다.
철자가 비슷해도 writeback과 alias 책임이 다르다. API가 어떤 변화를
관찰시키려는지 먼저 결정한 뒤 mode를 고른다.

판정은 argument expression이 value인지 stable place인지 확인하고,
요구 mode에 맞는 access capability를 획득하는 순서로 진행한다. borrow
동안 겹치는 mutation·move·drop을 금지하고 inout 동안 다른 alias의
read/write를 막는다. callee가 성공하면 inout write가 caller에 보이고,
precommit failure에서는 partial write를 publish하지 않는다.

`adjust(inout account, by: delta)`의 작은 trace에서 account place를
exclusive하게 예약한다. delta를 평가하고 validator를 통과한 뒤 새 값을
한 번 write한다. validation이 실패하면 old account가 live하고 다른
관찰자는 중간 값을 보지 않는다. 같은 place를 두 inout argument로
겹치게 전달하면 호출 전에 거부한다.

borrow를 단지 raw pointer처럼 보고 region을 임의로 늘리는 것은 흔한
오해다. closure 저장, async suspension, actor send가 owner보다 오래 살
수 있으면 borrow는 escape한다. 필요하다면 독립 snapshot이나 명시적
move를 택하되 의미와 copy 비용을 API에 드러낸다.

API 선택표를 만들면 오해를 줄일 수 있다. 읽기만 하고 저장하지 않으면
`borrow`, caller place 자체를 atomic하게 갱신하면 `inout`, callee가
독립된 mutable local을 소유하면 `mut`, 생명주기와 cleanup까지 넘기면
`move`를 검토한다. “성능을 위해 참조 전달”처럼 목적을 모호하게 쓰지
않고 caller가 호출 뒤 무엇을 관찰하는지부터 적는다.

실패 trace에서는 access region 획득 전, argument 평가 중, callee body,
write commit 뒤를 구분한다. exclusive region을 얻지 못하면 body는
시작하지 않는다. inout body의 checked 변경이 실패하면 old value와
caller owner를 보존하고, 성공한 최종 값만 한 번 publish한다. borrow
region은 정상 반환뿐 아니라 Error, Defect, Cancellation edge에서도
종료되어야 한다.

`mut` local을 `inout` write-back으로 오해하면 caller가 보지 못할 변경을
API 효과처럼 문서화하게 된다. 반대로 inout을 일반 mutable value처럼
복사하면 alias와 rollback 계약이 사라진다. 리뷰에는 region owner,
겹침 검사, escape 여부, success/failure publication을 모두 적는다.

### 6.1 읽기와 교체를 한 signature에서 구분한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def replace(
    borrow label: String,
    inout target: Buffer,
    move replacement: Buffer,
) -> Unit = {
    log(label)
    target = move replacement
}
```

`label` owner는 caller에 남는다. `target`은 exact caller place를 독점하고,
`replacement` owner는 성공 commit에서 target으로 이동한다.

### 6.2 `mut`는 local mutable owner다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def normalize(mut value: Buffer) -> Buffer = {
    value = trim(value)
    return move value
}

let normalized = normalize(move source)
```

`value`는 callee local place다. `source`로 write-back하지 않는다.
affine argument는 local로 이전되고 함수가 반환하거나 정리할 책임을 진다.

### 6.3 `inout`의 한-place transaction

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def increment(inout value: Int) -> Unit = {
    value += nextDelta()
}

var count = 10
increment(inout count)
```

`count` place는 한 번 선택되고 old value, RHS, checked addition이 성공한
뒤 한 번 write된다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: OWNERSHIP_MODE_ADMISSION_FAILED; product: NOT_RUN -->
```deeplus
updateBoth(inout state, inout state)
// OVERLAPPING_INOUT_ACCESS
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: OWNERSHIP_MODE_ADMISSION_FAILED; product: NOT_RUN -->
```deeplus
let view = borrow buffer
buffer = replacement
use(view)
// live borrow와 owner 교체가 충돌
```

borrow가 run, Actor, return, storage 또는 escaping closure를 건너려면
별도 admitted lifetime proof가 필요하다. suspension이 책임을 지워 주지
않는다.

## 8. 다른 기능과의 연결

- `ReadonlyView`는 owner-bounded borrow projection이다.
- Pattern probe binder는 nonowning이며 commit 전 move하지 않는다.
- `SharedCell.withValue`의 `#scoped borrow`, `SharedMutex.withLock`의
  `#scoped inout`은 stdlib 최소 profile이다.
- Actor isolation crossing은 ordinary borrow를 자동 transferable로 만들지
  않는다.

## 9. Deeplus다운 작성 관례

- 읽기 전용이면 `borrow`, caller place 갱신이면 `inout`을 쓴다.
- local transformation이면 `mut`와 명시적 return owner를 고려한다.
- `inout` call 하나에 같은 place나 겹치는 descendant를 두 번 넘기지 않는다.
- borrow scope를 실제 사용 구간으로 제한한다.

## 10. 연습 문제

1. **복사:** `borrow text: String`을 받아 길이를 반환하는 함수를 작성하라.
2. **빈칸 완성:** 표의 `mut Buffer` caller 관찰 칸은 `___`,
   `inout Buffer` 성공 후 칸은 `___`로 채우고 이유를 적어라.
3. **설계:** 두 collection element를 swap하는 API가 overlapping place를
   어떻게 거부해야 하는지 index 평가와 commit 순서까지 적어라.

## 11. 빠른 복습

- borrow는 owner를 만들지 않는다.
- inout은 exact caller place를 독점한다.
- mut parameter는 callee local place다.
- overlapping inout과 conflicting mutation은 거부한다.
- lifetime proof 없는 escape/suspension crossing은 없다.

## 12. 정본 근거와 다음 장

- [소유권 mode 문법](../../../spec/grammar/deeplus.dpg)
- [소유권 레퍼런스](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)
- [MIR inout/assignment](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음 장에서는 owner 이전과 복제 책임을 더 세밀하게 구분한다.


<!-- IR-OWN-R8-TUTORIAL-07-02 -->
<!-- IR-OWN-R34-LOAN-CLOSE -->
### borrow는 언제 끝나는가

소스에는 borrow를 닫는 별도 문장이 없다. compiler는 마지막 허용 사용과
region 제약을 이용해 각 실행 경로의 close frontier를 정하고 MIR에
`LOAN_END`를 남긴다. view에서 값을 먼저 복사한 뒤 `await`하면 ordinary
loan은 `await` 직전에 끝날 수 있고 복사된 값은 계속 쓸 수 있다.
반대로 `await` 뒤에 view를 다시 사용하면 close를 앞당길 수 없으므로 기존
borrow/suspension 진단으로 거부된다. 중첩 borrow는 가장 안쪽 view부터
닫으며 owner cleanup은 겹치는 모든 loan이 끝난 뒤 시작한다.

### `borrow`를 소유권 철자로 기억하기

공유 소유권 borrow는 `borrow value`로 쓴다. `&value`는 borrow의 축약이
아니며 NumericArray/Measure 연산 문맥을 표시하는 별도 표면이다.

예: `let view = borrow values`
