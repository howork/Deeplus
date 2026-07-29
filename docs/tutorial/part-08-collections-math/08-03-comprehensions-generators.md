# 8.3 Comprehension과 generator

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

List/Set/Map comprehension과 synchronous generator expression은 현행
설계다. async comprehension은 `PREVIEW_DESIGN_NONACTIVATABLE`이며 현행
source 예제를 만들지 않는다.

## 2. 학습 목표

- comprehension clause를 source order로 읽는다.
- `for`, guard, `if let`, `for ...` unfold를 사용한다.
- eager collection과 single-pass generator를 구분한다.
- generator capture/lifetime/cleanup 경계를 이해한다.

## 3. 선수 지식

collection literal, Pattern, guard, closure capture를 알고 있어야 한다.

## 4. 문제에서 출발하기

사용자 목록에서 active 이름만 만들 때 loop와 mutable accumulator를 직접
관리할 필요는 없다. 결과 collection이 즉시 필요하면 comprehension,
값을 필요할 때 하나씩 만들면 generator가 알맞다.

## 5. 핵심 모델

comprehension:

```text
result expression → for/if/if let/unfold clauses → eager collection
```

clause는 source order로 중첩되고 앞 clause의 binding을 뒤 clause와 result
expression이 본다.

generator:

```text
@for/@while/@repeat + block + yield → lazy/resumable single-pass owner
```

generator는 collection이 아니며 capture, yield type, lifetime,
effect/error와 cleanup을 따로 가진다.

## 6. 단계별 예제

### 깊이 읽기: eager 결과와 resumable producer를 먼저 고른다

comprehension과 generator는 비슷한 clause를 쓰더라도 owner와 실행
시점이 다르다. comprehension은 source order로 clause를 모두 평가해
완성된 collection owner를 반환한다. generator는 호출 시 collection을
만드는 것이 아니라, 소비자가 다음 값을 요구할 때 재개되는 single-pass
상태와 capture를 소유한다. 결과를 반복 순회해야 하거나 source lifetime과
분리해야 한다면 eager 결과가 자연스럽고, 큰 입력을 한 번씩 처리하거나
early stop이 중요하면 generator가 후보가 된다.

comprehension 판단은 왼쪽에서 오른쪽으로 진행한다. 각 `for`가 binding을
도입하고, guard나 `if let`이 residual을 제거한 뒤, 살아남은 환경에서
result expression을 평가한다. 뒤 clause는 앞 binding을 볼 수 있지만
반대 방향은 아니다. element 계산이 실패하면 partial collection을
성공값처럼 공개하지 않는 failure contract가 필요하다.

generator에서는 capture mode, yield type, effect/error, cleanup을 별도
항목으로 적는다. borrow capture가 generator보다 짧게 살거나 run 경계를
넘으면 거부하며, 중간에 소비가 끝나도 cleanup 책임이 사라지지 않는다.
흔한 오해는 generator를 List처럼 여러 번 순회하거나 `length`, bracket
index를 당연히 제공한다고 생각하는 것이다. 필요한 경우에는 명시적으로
collect하여 새 owner와 새 1-based domain을 만든다. async comprehension은
Preview 경계를 넘지 않으며 이 설명으로 활성화되지 않는다.

짧은 clause trace에서는 source collection을 한 번 얻고 첫 `for` binding을
만든 뒤 guard를 검사한다. guard가 거짓이면 result expression과 뒤
clause는 평가하지 않고 다음 source element로 간다. `if let` mismatch도
새 binding을 publish하지 않는다. 모든 clause가 성공한 iteration만
result value를 만들며 eager builder가 성공적으로 끝난 뒤 collection을
한 번 publish한다.

generator trace에는 `created`, `suspended`, `running`, `completed` 또는
`failed` 상태와 현재 capture owner를 남긴다. 소비자가 일찍 멈추면
남은 source를 억지로 평가하지 않지만 예약된 cleanup은 끝낸다. 한 번
완료한 producer를 암시적으로 초기 상태로 돌리거나 다른 소비자와
동시에 진행하지 않는다.

### 6.1 List comprehension

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let names = [
    user.name
    for user in users
    if user.active
]
```

각 user를 source order로 방문하고 guard가 true인 iteration만 name을
평가해 List plan에 넣는다. partial List는 전체 성공 전 publish되지 않는다.

### 6.2 Map comprehension과 `if let`

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let byId = #map{
    user.id: profile
    for user in users
    if let Option::some(profile) = user.profile
}
```

Pattern success iteration에서만 `profile` binder가 result Map entry에
보인다. duplicate key와 failure는 Map transaction law를 따른다.

### 6.3 lazy generator

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let positives = @for value in values {
    if value > 0 {
        yield value
    }
}
```

`positives`는 eager List가 아니다. 각 resume에서 loop를 진행하고 yield
point와 cleanup responsibility를 보존한다.

### 6.4 yield guard

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let visible = @for item in items {
    yield item if item.visible
}
```

guard는 terminating/pure 조건을 따라 yield admission을 결정한다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: GENERATOR_EXPR_IS_SINGLE_PASS_NOT_COLLECTION; product: NOT_RUN -->
```deeplus
let generated = @for x in values { yield x }
let first = generated[1]
// GENERATOR_EXPR_IS_SINGLE_PASS_NOT_COLLECTION
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: GENERATOR_BORROW_CAPTURE_FORBIDDEN; product: NOT_RUN -->
```deeplus
let g = [borrow owner] @for item in owner {
    yield item
}
// escaping generator borrow가 owner region을 넘음
```

async comprehension은 source spelling과 iteration/cancellation/ownership
계약이 활성화되지 않았다. ordinary `for#await` statement와 stdlib
collector를 comprehension으로 암시 승격하지 않는다.

## 8. 다른 기능과의 연결

- comprehension의 `if let`은 transactional Pattern이다.
- Map duplicate replacement와 cleanup은 source order를 보존한다.
- generator의 `yield`는 response binding이나 cancellation과 별도 규칙을
  갖는다.
- Sequence evidence는 iteration만 제공하며 bracket/index를 만들지 않는다.

## 9. Deeplus다운 작성 관례

- 결과를 여러 번 읽을 collection이면 comprehension을 쓴다.
- 큰/무한/단일 통과 stream이면 generator를 고려하고 lifecycle을 적는다.
- clause를 filtering pipeline 순서로 배치해 binding 가시성을 읽기 쉽게 한다.
- async가 필요하면 현행 structured async API를 쓰고 비활성 syntax를
  발명하지 않는다.

## 10. 연습 문제

1. **복사:** 짝수만 제곱하는 List comprehension을 작성하라.
2. **빈칸 완성:** `[value for item in items if let
   Option::some(___) = item]`의 빈칸에 `value`를 넣어 완성하라.
3. **설계:** 백만 행 파일을 eager List와 generator 중 무엇으로 처리할지
   memory, failure, cleanup, 재순회 요구를 기준으로 결정하라.

## 11. 빠른 복습

- comprehension은 eager collection owner다.
- generator는 lazy single-pass owner다.
- clause와 iteration order는 source order다.
- generator capture는 escape/lifetime 검사를 받는다.
- async comprehension은 현행이 아니다.

## 12. 정본 근거와 다음 장

- [문법 owner 가이드](../../grammar-reference/16-contextual-syntax-and-production-guide.md)
- [collection 레퍼런스](../../grammar-reference/09-collections-indexing-and-slicing.md)
- [generator grammar](../../../spec/grammar/deeplus.ebnf)
- [언어 명세 §24](../../../spec/language.md)

다음 장에서는 shape가 type identity에 들어가는 NumericArray를 배운다.
