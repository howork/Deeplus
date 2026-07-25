# 5.5 완전성, guard, transaction

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

match partition, guard와 pattern commit 순서는 현행 정본이다. “모든
경우를 쓴 것처럼 보인다”가 아니라 finite partition을 실제로 덮었는지
판정한다.

## 2. 학습 목표

- usefulness와 exhaustiveness를 구분한다.
- guard가 unconditional coverage를 만들지 않는 이유를 이해한다.
- pattern test와 ownership commit의 8단계 transaction을 설명한다.
- `@match`와 statement `match`의 join 차이를 이해한다.

## 3. 선수 지식

Enum/Union Pattern과 `move`/`borrow`의 직관이 필요하다.

## 4. 문제에서 출발하기

`x if x > 0` arm은 양수만 처리한다. 이 arm이 `Int` Pattern을 썼다는
이유로 모든 정수를 덮었다고 계산하면 0과 음수가 빠진다. guard는 이미
선택된 structural cell 안에서 조건을 더할 뿐 그 cell을 완전히 제거하지
않는다.

## 5. 핵심 모델

완전성 분석은 순서 있는 유한 partition pass다.

- 새 structural cell을 더하지 않는 arm:
  `MATCH_ARM_UNREACHABLE`
- guard 때문에 residual이 남음:
  `MATCH_NONEXHAUSTIVE_AFTER_GUARDS`
- residual이 없는데 `otherwise`가 뒤에 옴:
  `OTHERWISE_UNREACHABLE`
- 최종 residual:
  `MATCH_NOT_EXHAUSTIVE`

refutable owner의 transaction:

1. subject를 한 번 평가
2. place/owner 획득
3. nonconsuming `TestPlan`
4. nonowning probe binder
5. pure Bool guard
6. 성공 시 move/borrow/binding atomic commit
7. final binder와 body
8. owner별 exit/join

## 6. 단계별 예제

### 깊이 읽기: coverage와 실행 순서 분리

exhaustiveness는 예제를 많이 적었다는 성질이 아니라 입력 universe의
모든 cell이 정확한 규칙으로 덮였다는 정적 증거다. Enum은 VariantId,
closed Union은 alternative identity, List는 길이와 rest profile처럼
carrier마다 cell 기준이 다르다. guard는 한 cell 일부를 통과시키므로
guarded arm 하나가 원래 cell 전체를 덮는다고 계산하지 않는다.

먼저 닫힌 universe와 structural Pattern cell을 만든다. guard 없는 total
arm과 guarded partial arm을 분리하고 overlap·누락을 검사한다. ordinary
match는 첫 admitted arm을 source order로 고르지만 declarative callable
clause처럼 순서가 tie-break가 아닌 owner에서는 겹침을 오류로 남긴다.

첫 arm 구조는 맞고 guard가 false인 작은 trace에서 subject를 다시
평가하지 않는다. probe binder를 폐기하며 move·exclusive borrow·authority
acquisition commit은 영이다. 다음 arm은 같은 원본 owner를 검사하고,
성공한 그 arm의 binding만 한 번 commit한다.

effectful guard는 false 이전에 I/O나 mutation을 남겨 “실패한 arm은
흔적이 없다”는 법칙을 깨뜨린다. 그래서 guard는 exact Bool,
deterministic, synchronous, no-throw, `effects {}`여야 한다. 일반
`def#guard` 호출도 자동 coverage cell이나 narrowing summary를 만들지
않는다.

마지막 catch-all을 넣으면 무조건 좋다는 생각은 흔한 오해다. 닫힌
domain에서는 새 case 검토를 숨길 수 있고, external residual이 실제
계약일 때만 residual policy를 명시해야 한다.

### 6.1 guard 없는 total match

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public enum Access {
    guest
    member(name: String)
    admin(name: String)
}

private def badge(access: Access) -> String = {
    return @match access {
        ::guest => "guest"
        ::member(name) => "member:${name}"
        ::admin(name) => "admin:${name}"
    }
}
```

세 case가 exact `VariantId` 우주를 모두 덮는다. 각 arm의 String type과
place/cleanup state가 join된다.

### 6.2 guard가 residual을 남기는 경우

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def privileged(access: Access) -> Bool = {
    return @match access {
        ::admin(name) if name != "" => true
        ::guest => false
        ::member(_) => false
        ::admin(_) => false
    }
}
```

첫 `::admin` arm의 guard는 nonempty name만 처리한다. 마지막
`::admin(_)`이 structural residual을 닫는다. 첫 arm만 있다고 admin cell
전체가 덮인 것으로 계산하지 않는다.

### 6.3 실패 전에는 owner를 옮기지 않는다

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let outcome = receive()
if let move Result::ok(packet) = outcome {
    deliver(move packet)
}
```

구조 test와 guard가 있다면 guard까지 성공한 뒤에만 `packet` move가
commit된다. mismatch에서는 `outcome`을 부분 이동 상태로 만들지 않는다.

## 7. 허용·거부·경계 사례

guard는 terminating, pure, nonthrowing, nonsuspending Bool이며 probe를
consume/escape하거나 authority를 얻을 수 없다.

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: MATCH_NONEXHAUSTIVE_AFTER_GUARDS; product: NOT_RUN -->
```deeplus
let label = @match access {
    ::guest => "guest"
    ::member(name) => name
    ::admin(name) if name != "" => name
}
// MATCH_NONEXHAUSTIVE_AFTER_GUARDS
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: MATCH_GUARD_EFFECT_NOT_ALLOWED; product: NOT_RUN -->
```deeplus
match access {
    ::admin(name) if audit(name) => allow()
    otherwise => deny()
}
// effectful/throwing/suspending guard는 거부
```

`otherwise`는 불완전한/open partition을 안전하게 닫는 수단이지만,
이미 total한 exact Enum match 뒤에서는 unreachable이다.

## 8. 다른 기능과의 연결

- flow narrowing fact는 assignment, alias mutation, exclusive borrow,
  escape, capture, consume 또는 may-mutate call에서 죽는다.
- assignment도 target/RHS를 한 번 평가하고 성공 시 한 번 commit하는
  transaction이다.
- constructor, Record/schema, Map literal 역시 partial value를 publish하지
  않는 같은 철학을 따른다.
- HIR-H1은 chosen partition, binder mode와 commit point를 보존하고 MIR은
  runtime provider를 다시 찾지 않는다.

## 9. Deeplus다운 작성 관례

- guard를 coverage 대신으로 쓰지 않는다.
- positive guard arm 뒤에는 같은 structural cell의 residual arm을 눈에
  보이게 둔다.
- total한 domain에는 불필요한 `otherwise`를 두지 않아 새 case 추가가
  정적 오류로 드러나게 한다.
- 소유권을 옮기는 Pattern은 commit point가 명확한 작은 scope에 둔다.

## 10. 연습 문제

1. **복사:** `Access`의 세 case를 모두 덮는 statement `match`를 작성하라.
2. **빈칸 완성:** `::member(name) if name != ___`와 residual
   `::member(___)`의 빈칸을 `""`, `_`로 채워 모든 이름을 닫게 하라.
3. **설계:** move payload를 가진 Result 처리에서 parse 실패, false guard,
   성공 commit 각각의 owner 상태표를 작성하라.

## 11. 빠른 복습

- usefulness와 exhaustiveness는 다르다.
- guard는 unconditional coverage를 제공하지 않는다.
- test는 nonconsuming, commit은 성공 뒤 한 번이다.
- `@match`의 정상 arm은 모두 값을 만들고 책임 상태를 join한다.
- 문서 존재는 P1 closure나 제품 PASS가 아니다.

## 12. 정본 근거와 다음 장

- [Pattern partition 정본](../../../spec/types/type-system.md)
- [MIR pattern transaction](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [패턴 레퍼런스](../../grammar-reference/10-patterns-destructuring-and-matching.md)
- [진단 목록](../../../spec/language.md)

이제 Part 5 실습에서 schema, Enum, Pattern transaction을 하나의 domain
workflow로 합친다.
