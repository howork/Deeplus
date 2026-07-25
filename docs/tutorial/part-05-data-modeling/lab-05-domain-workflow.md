# Lab 5 — 주문 승인 domain workflow

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 목표

동적 입력을 schema row로 정리하고, 주문 상태를 Enum으로 닫은 뒤,
guarded Pattern과 exhaustive match로 승인 흐름을 모델링한다. 실제
네트워크나 database 구현이 아니라 정적 설계 연습이다.

## 준비

- 5.1~5.5를 읽는다.
- Record label과 Map key, constructor와 materialization을 구분한다.
- product lanes가 `15/15 NOT_RUN`임을 결과 설명에 남긴다.

## 누적 프로젝트 연결

| 연결 | 내용 |
|---|---|
| input prior | Part 4의 refinement, narrowing, Union, `def#guard` 증거 |
| output | schema row에서 명목 Order와 exhaustive OrderState로 이어지는 workflow |
| next | Part 6에서 Order와 상태 표시를 explicit Trait evidence로 일반화 |

입력 단계의 검증 증거는 명목 owner 생성보다 먼저 확정하며, 실패하면
부분 `Order`를 공개하지 않는다. 다음 부에는 이 owner를 바꾸지 않고
표시 capability만 explicit conformance로 결합한다.

누적 결과를 넘길 때에는 raw 입력, validated row, 명목 값, 상태 case를
서로 다른 칸에 기록한다. 다음 부가 소비하는 것은 검증된 명목 값이며
외부 Map이나 실패한 materialization의 임시 binding이 아니다. 이 경계를
지키면 표시 기능을 추가해도 입력 admission과 rollback 책임이 바뀌지
않는다.

## 1단계 — 입력 schema와 상태 Enum

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public schema OrderInput {
    id: Int
    customer: String
    amount: Rational
}

public enum OrderState {
    received
    approved(by: String)
    rejected(reason: String)
}

public data class Order(
    +let id: Int,
    +let customer: String,
    +let amount: Rational,
    +let state: OrderState,
)
```

`OrderInput`은 외부 row admission, `Order`는 내부 명목 값, `OrderState`는
유한 상태 identity를 담당한다.

## 2단계 — materialize하고 명목 값으로 옮기기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def acceptInput(id: Int, customer: String, amount: Rational) -> Order = {
    let row = OrderInput${
        id
        customer
        amount
    }

    return Order${
        id: row.id
        customer: row.customer
        amount: row.amount
        state: OrderState::received
    }
}
```

두 materialization은 각각 전체 field 검사 뒤 한 번 commit된다.

## 중간 점검

- [ ] `case` keyword를 쓰지 않았다.
- [ ] `OrderInput${...}`를 constructor 호출로 설명하지 않았다.
- [ ] `Order${...}`는 eligible data-class ConstructionRow임을 전제했다.
- [ ] `amount`를 Float가 아니라 exact `Rational`로 유지했다.

## End-to-end 책임 trace

한 요청이 `OrderInput${...}`로 들어와 승인 결과가 표시될 때까지를
일곱 단계로 추적한다. 먼저 schema materializer가 required label과
field type을 확인한다. field expression을 source order로 한 번씩
평가하고 모두 성공하면 raw row를 한 번 publish한다. validator가
refinement를 확인한 뒤 성공 증거가 있을 때만 명목 `Order`와
`OrderState`를 만든다. exhaustive Pattern은 case와 payload를
nonconsuming 방식으로 시험하고 guard 성공 뒤 binder를 commit한다.
마지막 표시 adapter는 이미 검증된 값을 borrow로 읽는다.

이름 field는 성공했지만 amount 변환이 실패하면 schema publication은
영이다. schema는 성공했지만 amount refinement가 실패하면 raw 입력
증거가 남을 수 있어도 validated `Order` owner는 생기지 않는다.
Pattern 구조가 맞고 guard가 false면 해당 arm의 binder와 move commit은
영이다. 이 세 실패를 하나의 검증 오류로 합치면 rollback owner와
diagnostic phase를 잃는다.

owner timeline도 적는다. field 평가 중 임시 resource는 formation plan이
소유한다. raw row publish 뒤에는 row owner, 명목 값 commit 뒤에는
domain owner가 책임진다. 표시 함수가 borrow를 받으면 호출 region을
벗어나지 않는다. 어느 단계도 실패를 빈 객체나 sentinel 문자열로
바꾸지 않는다.

effect timeline에서는 materialization과 validation을 `effects {}`로
유지한다. logging·저장은 commit 이후 adapter로 분리한다. 검증 도중
외부 기록을 먼저 남기면 뒤 단계 실패가 성공처럼 보일 수 있다. effect가
꼭 필요하면 signature와 failure ordering에 드러내고, 기록과 domain
commit의 관계를 별도 계약으로 둔다.

## Review rubric

리뷰어는 다음 항목을 `충족`, `부분 충족`, `재설계 필요`로 판정한다.

1. schema row, Class owner, Enum case의 identity를 분리했는가?
2. child expression의 once 평가와 all-or-nothing publication을
   설명했는가?
3. Pattern의 structural test, probe, guard, commit, body 순서를
   보존했는가?
4. schema 오류, refinement 실패, arm mismatch를 올바른 phase에
   남겼는가?
5. move·borrow·cleanup과 외부 effect 경계가 드러나는가?
6. current Enum만 positive 예제로 쓰고 product PASS를 주장하지
   않았는가?

하나라도 `재설계 필요`이면 예상 문자열이 맞는다는 이유만으로 실습을
완료로 판정하지 않는다. 이 rubric은 design-static 검토이며 실제
compiler·runtime 영수증을 대신하지 않는다.

## 3단계 — 승인 결과를 exhaustive하게 표시하기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def stateText(state: OrderState) -> String = {
    return @match state {
        ::received => "received"
        ::approved(by) => "approved by ${by}"
        ::rejected(reason) => "rejected: ${reason}"
    }
}

private def approve(order: Order, reviewer: String) -> Order = {
    return order!{
        state: OrderState::approved(by: reviewer)
    }
}
```

derivation은 같은 `Order` nominal identity를 유지한다. Enum source order는
승인 우선순위나 persistence tag가 아니다.

## 4단계 — 실패를 transactional Pattern으로 처리하기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def persistParsed(text: String) -> Unit = {
    let ::ok(input) = parseOrder(text)
    else ::err(error) => throw error

    let order = acceptInput(input.id, input.customer, input.amount)
    persist(order)
}
```

`parseOrder`가 실패하면 `input` binding과 이후 Order construction은
일어나지 않는다.

## 실패 실험

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD; product: NOT_RUN -->
```deeplus
let invalid = OrderInput${
    id: 13
    customer: "Ada"
    amount: <3/2>
    priority: "high"
}
// TYPE_DOLLAR_SCHEMA_UNKNOWN_FIELD
```

두 번째 실험으로 `stateText`에서 `::rejected` arm을 지우고
`MATCH_NOT_EXHAUSTIVE` residual을 설명하라. 정적 거부는 admitted MIR을
만들지 않는다.

## 확장 과제

1. **복사:** `cancelled(by: String)` case를 추가하고 모든 match를 갱신하라.
2. **빈칸 완성:** `let metadata = ${source: ___}`와
   `let headers = [___: "trace-1"]`의 label/key 빈칸을 채우고 각각
   허용되는 unfold를 적어라.
3. **설계:** persistence serialization code를 `VariantId`와 분리한 mapping
   schema로 설계하고 declaration order에 의존하지 않음을 설명하라.

## 완료 체크리스트

- [ ] schema, data class, Enum의 owner를 분리했다.
- [ ] current Enum 표면만 사용했다.
- [ ] 모든 match partition이 total하거나 residual을 명시했다.
- [ ] 실패 전 partial binding/value를 publish하지 않는다.
- [ ] semantic P0 `0`, OPEN P1 `22`, product lanes `15/15 NOT_RUN`을
      유지했다.
- [ ] compiler/runtime/tooling PASS를 주장하지 않았다.

## 정본 근거

- [통합 Enum·Record·schema 예제](../../grammar-reference/24-integrated-worked-examples.md)
- [패턴 transaction](../../grammar-reference/10-patterns-destructuring-and-matching.md)
- [타입 시스템](../../../spec/types/type-system.md)
