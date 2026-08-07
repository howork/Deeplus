# Lab 12 — 설계 제안의 승격과 잔여 표면 검토하기

> 상태: `MIXED_STATUS`
>
> 이 실습은 Stable로 수용된 설계와 여전히 비활성인 표면을 분리하는
> 방법을 익힌다. 정적 설계 증거를 product PASS로 해석하지 않는다.

## 목표

- exact feature ID와 현행 상태를 먼저 확인한다.
- 승격된 최소 표면과 거부되거나 남은 확장을 구분한다.
- 문법, 타입, 소유권, lowering, 진단, 테스트 책임을 한 검토 카드에 묶는다.
- `CURRENT_ACCEPTED`, `KEEP_NONACTIVATABLE`, `REVISE_PROPOSAL`,
  `REJECT_DESIGN` 중 하나를 증거와 함께 선택한다.

## 사례: Failable guarded local binding

과거 Option 전용 후보는 현행 `trait#binding Failable` 계약으로
대체되었다. 이 변경은 Option에 특수 문법을 붙이는 대신 “성공 또는 실패로
분기 가능한 값을 한 번 소비한다”는 공통 책임을 소유자 Trait에 둔다.

검토 카드의 상태는 다음과 같다.

```text
feature_id: trait_binding_failable_v1
current_disposition: SUPERSEDED_BY_STABLE_FAILABLE_BINDING
current_surface: let? successPattern = expression else failurePattern => unconditionalExit
product_lanes: 15/15_NOT_RUN
p1_delta: 0
```

ID 이름은 과거 제안의 계보를 보존한다. 그러나 그 이름 때문에 현행 의미를
Option 전용 Preview로 해석해서는 안 된다.

## 1단계 — 현행 표면을 확인한다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let? configuration = loadConfiguration()
else error => throw error

start(configuration)
```

오른쪽 식은 정확히 한 번 평가되고 선택된 `Failable::branch`에 한 번
소비된다. 성공 pattern과 실패 pattern은 각각 연관 타입 `Success`와
`Failure`에 대해 irrefutable이어야 한다. 실패 arm은 현재 local
continuation을 반드시 벗어나므로 `else` 이후에는 성공 binding만 보인다.

## 2단계 — carrier별 의미를 분리한다

`Option<T>`의 실패 타입은 `Unit`, `Result<T, E>`의 실패 타입은 `E`다.
둘은 같은 문법을 쓸 수 있지만 실패 identity가 같아지는 것은 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let? user = findUser(id)
else _ => return guestUser()

let? profile = loadProfile(user)
else error => throw error
```

첫 번째 실패 pattern `_`는 Option의 `Unit`을 받는다. 두 번째 `error`는
Result의 실제 오류 타입을 받는다. automatic propagation이나 truthiness는
이 표면의 일부가 아니다.

## 3단계 — 잔여 확장을 거부 사례로 기록한다

`if let?`, `while let?`, `var?`, `else` 없는 bare `let?`는 현행 문법이
아니다.

<!-- deeplus-example: illustrative; surface: REJECTED; product: NOT_RUN; expected: REJECT -->
```deeplus
if let? user = findUser(id) {
    show(user)
}
```

조건부 Option probing이 필요하면 명시적 pattern을 사용한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
if let Option::some(user) = findUser(id) {
    show(user)
}
```

이 대안은 실패 시 local continuation을 벗어나지 않으므로 guarded local
binding과 다른 제어 흐름이다.

## 4단계 — 추적성 표를 완성한다

| lane | 확인할 계약 | 이 사례의 결론 |
|---|---|---|
| grammar | 하나의 root-connected 표면인가 | `let? ... else ... => exit`만 current |
| AST | 성공·실패 pattern과 exit가 보존되는가 | 전용 guarded-binding shape |
| type | carrier와 연관 타입이 결정적인가 | exact `Failable` witness |
| ownership | subject 평가·소비 횟수가 고정되는가 | 한 번 평가, 한 번 소비 |
| control flow | 실패 arm이 continuation을 벗어나는가 | 구조적으로 강제 |
| lowering | 새 unwrap runtime node가 필요한가 | 필요 없음; branch 결과로 정규화 |
| diagnostic | 비 irrefutable pattern과 비탈출 arm을 거부하는가 | deterministic primary diagnostic 필요 |
| product | 실행 영수증이 있는가 | `NOT_RUN` |

## 5단계 — 정상·경계·거부 사례를 쓴다

- 정상: `Result<T,E>`를 한 번 소비하고 실패 시 `throw error`한다.
- 경계: `Option<T>`의 `Unit` 실패를 `_`로 받고 `return`한다.
- 거부: 실패 arm이 단순 호출만 하고 이어서 실행된다.

<!-- deeplus-example: illustrative; surface: REJECTED; product: NOT_RUN; expected: REJECT -->
```deeplus
let? value = lookup(key)
else error => log(error)
```

마지막 예제의 실패 arm은 local continuation을 벗어나지 않으므로 binding의
가시성과 definite-assignment를 닫을 수 없다.

## 연습 — 설계 상태와 제품 증거를 분리한다

각 답에는 feature ID, source 상태, 실패 경로의 책임, 필요한 진단과 실제
실행 증거의 유무를 함께 적는다. 문법이 읽기 좋다는 이유만으로 Stable이나
product PASS를 선언하지 말고, 같은 책임을 더 작은 현행 표면으로 표현할 수
있는지도 확인한다.

1. **성공·실패 carrier 비교:** `Option<User>`와 `Result<User, LoadError>`에
   각각 guarded local binding을 적용하고, 두 실패 pattern의 타입과
   unconditional-exit 방법이 왜 다른지 설명한다.
2. **경계 사례 설계:** subject가 move-only 값일 때 단일 평가·단일 소비와
   성공 binding의 atomic commit을 검증할 boundary test를 작성한다.
3. **거부 사례 판정:** `if let?`, `while let?`, non-exiting `else` 중 하나를
   골라 primary diagnostic, AST 잔여 생성 여부와 product lane 상태를 적는다.

## 완료 체크리스트

- [ ] historical feature ID와 current disposition을 함께 기록했다.
- [ ] Stable 최소 표면과 거부된 확장을 분리했다.
- [ ] carrier identity와 failure identity를 합치지 않았다.
- [ ] subject 단일 평가·단일 소비와 atomic binding commit을 기록했다.
- [ ] 실패 arm의 unconditional-exit 규칙을 확인했다.
- [ ] 정상·경계·거부 사례를 각각 하나 이상 만들었다.
- [ ] 실행하지 않은 parser/checker/runtime/tooling을 PASS로 쓰지 않았다.

이 검토의 결론은 `CURRENT_ACCEPTED`다. 다만 이는 language-design 상태이며
production compiler 또는 runtime 구현 완료를 뜻하지 않는다.
