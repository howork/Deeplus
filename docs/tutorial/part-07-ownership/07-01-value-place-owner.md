# 7.1 Value, place, owner

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

place state와 owner tracking은 현행 정본 설계다. 이 장은 physical pointer
layout을 고정하지 않고 source/checker/HIR/MIR에서 관찰해야 할 책임을
설명한다.

## 2. 학습 목표

- value, place, owner를 서로 구분한다.
- immutable binding과 mutable place를 구분한다.
- move 전후의 place state를 읽는다.
- flow join이 타입뿐 아니라 responsibility state도 합쳐야 함을 이해한다.

## 3. 선수 지식

`let`, `var`, assignment, 함수 scope를 알고 있어야 한다.

## 4. 문제에서 출발하기

`file`이라는 이름에 `File` 값이 들어 있다고 말하는 것만으로는 충분하지
않다. 그 place가 초기화되었는지, 이미 move되었는지, borrow 중인지,
cleanup owner인지가 프로그램의 안전성을 결정한다.

## 5. 핵심 모델

- **value:** 계산된 의미 값
- **place:** 값을 저장하고 읽거나 변경할 수 있는 source 위치
- **owner:** value와 cleanup responsibility를 정확히 한 번 책임지는 주체

checker와 MIR handoff는 place마다 다음을 추적한다.

- initialized/absent
- usable/moved
- live shared borrow region
- exclusive inout region
- mutable access
- cleanup owner
- isolation owner

같은 normalized type이어도 place state가 다르면 flow join이 실패할 수 있다.

## 6. 단계별 예제

### 깊이 읽기: 값의 내용과 책임 위치를 따로 묻기

value는 계산된 의미 내용이고 place는 그 값을 읽거나 갱신할 수 있는
정적 위치다. owner는 값이나 resource의 생명주기와 cleanup 책임을 가진
identity다. 한 place가 owner를 담을 수 있지만 두 개념은 같다 할 수
없다. temporary value처럼 이름 붙은 place가 없어도 owner 책임이 있을
수 있고, shared value place는 독점 owner transfer를 허용하지 않을 수
있다.

판정은 expression이 value만 만드는지 assignable place를 가리키는지
분류하는 데서 시작한다. 이어 place path의 root와 projection, 현재
live/moved/borrowed state를 확인한다. operation이 owner를 바꾸면 성공
commit 지점을 하나로 정하고 precommit failure가 source state를
보존하는지 검사한다.

작은 trace에서 `let archived = move session`을 생각해 보자. rhs와
destination 준비 중 실패하면 `session`은 caller owner로 live다. commit이
성공한 순간 `archived`가 owner와 cleanup 책임을 받고 source place는
사용할 수 없다. 같은 bytes가 메모리에 남아 보인다는 사실은 semantic
owner를 되돌리지 않는다.

흔한 오해는 `let`이면 복사되고 `var`이면 참조된다는 생각이다. binding의
가변성과 값의 ownership mode는 별도 축이다. 또한 member projection을
읽었다고 parent owner가 자동 분할되는 것도 아니다. resource partial
move와 join은 exact type 책임 규칙을 따라야 한다.

리뷰 trace에는 operation 전 place state, 필요한 capability, commit
조건, 성공 후 owner, 실패 후 owner를 한 줄씩 적는다. branch마다 이 표를
작성한 뒤 join에서 동일한 responsibility state로 만나는지 확인한다.
한쪽은 live이고 다른 쪽은 moved라면 값의 normalized type이 같아도
안전한 사용을 계속할 수 없다. 이때 임의 copy를 삽입해 맞추지 않고
분기 구조나 owner transfer 위치를 다시 설계한다.

### 6.1 immutable value와 mutable place

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let taxRate: Rational = <1/10>
var subtotal: Rational = <50/1>

subtotal = subtotal + <5/1>
let total = subtotal + subtotal * taxRate
```

`taxRate`는 immutable binding, `subtotal`은 mutable place다. assignment는
target place와 RHS를 각각 한 번 평가하고 성공할 때 한 번 write한다.

### 6.2 owner 이전 뒤 place state

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let node: Box<Node> = Box!(Node!(value: 1))
let moved = move node

use(moved)
```

`move` commit 뒤 reusable value가 아닌 source `node`는 `moved` 상태다.
cleanup responsibility도 `moved` binding의 owner로 이동한다.

### 6.3 branch의 responsibility join

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let selected = @if chooseLeft {
    move left
} else {
    move right
}

consume(move selected)
```

두 arm은 값 type뿐 아니라 owner와 cleanup responsibility가 하나의
`selected` binding으로 합법적으로 join되어야 한다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: OWNERSHIP_MODE_ADMISSION_FAILED; product: NOT_RUN -->
```deeplus
let owned = acquire()
let transferred = move owned
use(owned)
// OWNERSHIP_MODE_ADMISSION_FAILED
```

허용되는 reusable Plain value는 copy law에 따라 source를 계속 쓸 수 있지만,
그 사실을 모든 같은-looking type으로 일반화하지 않는다.

경계:

- `Plain`은 lifecycle owner가 없다는 책임이지 raw bit layout이 아니다.
- `Shared<T>`는 alias를 만드는 owner/handle이고 `Shareable` evidence와
  다르다.
- type equality가 cleanup/isolation state를 지우지 않는다.

## 8. 다른 기능과의 연결

Pattern은 structural test 뒤에 owner transfer를 commit한다. constructor,
Map, schema와 assignment도 성공 전 partial value/place를 publish하지
않는다. Actor enqueue는 commit 전 sender owner, 성공 뒤 receiver owner를
구분한다.

## 9. Deeplus다운 작성 관례

- owner 변경을 `move`로 눈에 보이게 한다.
- mutable place의 scope를 작게 유지한다.
- branch마다 owner를 다르게 소모한 채 합류하지 않는다.
- type 설명에 cleanup/isolation responsibility를 함께 적는다.

## 10. 연습 문제

1. **복사:** `Box<Node>`를 한 번 move하고 새 binding만 사용하는 코드를
   작성하라.
2. **빈칸 완성:** assignment trace `target place 예약 → ___ 평가 →
   validation → ___ commit`의 두 빈칸을 `RHS`, `한 번`으로 채워라.
3. **설계:** 두 branch 중 하나가 resource를 move하고 다른 branch는
   유지하는 코드의 join을 어떻게 재구성할지 제안하라.

## 11. 빠른 복습

- value, place, owner는 다른 개념이다.
- place state는 type과 별도로 흐른다.
- move commit 뒤 source place는 사용할 수 없다.
- precommit failure는 source owner를 보존한다.
- cleanup responsibility는 owner를 따라간다.

## 12. 정본 근거와 다음 장

- [소유권 레퍼런스](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)
- [MIR place와 owner](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [타입 시스템](../../../spec/types/type-system.md)

다음 장에서는 owner를 옮기지 않고 읽거나 독점 변경하는 channel을 배운다.
