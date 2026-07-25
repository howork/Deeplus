# 7.3 `move`, `copy`, `clone`, consume

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

move와 capture의 `copy`/`clone`/`deep`/`once` mode는 현행 설계다. 이
단어들은 성능 hint가 아니라 source validity, witness, effect/error와
cleanup을 바꾸는 책임이다.

## 2. 학습 목표

- move와 copy의 source-place 결과를 비교한다.
- clone이 selected witness 호출임을 이해한다.
- consume 경계와 exactly-one owner 반환 조건을 설명한다.
- closure capture의 `move`, `copy`, `clone`, `once`를 읽는다.

## 3. 선수 지식

owner/place와 Trait conformance, closure의 기초를 알고 있어야 한다.

## 4. 문제에서 출발하기

“복사한다”는 말에는 최소 세 뜻이 섞인다. 작은 reusable 값을 그대로
복제하는 copy, 타입이 정의한 Clone evidence를 호출하는 clone, 원 owner를
다른 곳으로 옮기는 move다. Deeplus는 이를 숨기지 않는다.

## 5. 핵심 모델

- `move`: owner와 cleanup responsibility를 이전한다.
- `copy`: admitted reusable value/bit-copy 책임을 요구하고 source를
  valid하게 둔다.
- `clone`: exact `Clone` witness를 한 번 호출하며 그 effect/error를
  노출한다.
- `deep`: 별도 deep-copy profile과 graph identity/cycle 법칙이 필요하다.
- `once`: captured environment field를 한 번만 소비하게 한다.

consuming receiver/API가 owner를 계속 보존한다면 모든 성공 경로에서
`Self`-compatible owner를 정확히 한 번 명시적으로 반환해야 한다.

## 6. 단계별 예제

### 깊이 읽기: 네 동작의 관찰 가능성을 구분하기

`move`는 같은 owner 책임을 새 place로 한 번 이전한다. `copy`는 Copy
법이 있는 재사용 가능한 값을 독립 값으로 복제하며 source를 유지한다.
`clone`은 명시적 operation으로 allocation이나 failure 같은 비용을 가질
수 있다. consume parameter는 callee가 전달된 owner의 최종 사용과
cleanup을 책임진다. 네 동작을 성능 힌트로만 보면 실패 경계를 잃는다.

먼저 type이 reusable value인지 unique/resource owner인지 확인한다.
호출 뒤 source가 계속 필요하면 admitted copy 또는 명시적 clone을
검토하고, 책임 자체를 넘길 때만 move를 사용한다. destination 준비와
argument evaluation이 끝난 뒤 owner transfer를 한 번 commit한다.

작은 trace에서 `archive(move session)` 호출의 receiver와 다른 argument가
먼저 평가된다. admission 전에 실패하면 session owner는 caller에게
남는다. transfer commit 뒤 callee가 실패해도 source를 되살리지 않고
callee의 failure path가 cleanup한다. 이 구분이 duplicate close와 leak을
동시에 막는다.

흔한 오해는 clone을 넣으면 모든 borrow 오류가 해결된다는 생각이다.
clone 가능한 representation인지, semantic identity가 복제되어도 되는지,
effect와 error를 누가 관찰하는지 먼저 정해야 한다. copy와 clone 결과가
값으로 같아도 ownership·비용 contract는 다르다.

검토표에는 source의 호출 전 상태, 선택한 mode를 허용하는 evidence,
새 값 또는 이전 owner의 도착 place, 성공 뒤 source 상태, 실패 시
cleanup 주체를 적는다. consume 함수가 owner를 계속 보존한다고 선언하면
모든 성공 경로에서 호환 owner를 정확히 한 번 반환하는지도 검사한다.
한 분기에서 반환하고 다른 분기에서 조용히 drop하면 flow join의
responsibility가 맞지 않는다.

### 6.1 owner를 consume하는 함수

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def archive(move document: Document) -> Unit = {
    writeArchive(borrow document)
}

let document = loadDocument()
archive(move document)
```

call commit 뒤 `document` place는 moved다. `archive`가 owner와 cleanup을
받아 정상/오류/취소 경로에서 책임을 끝낸다.

### 6.2 reusable 값의 copy capture

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let offset: Int = 3
let addOffset = [copy offset] { value: Int =>
    value + offset
}

let first = addOffset(10)
let stillAvailable = offset
```

`Int`의 admitted copy 책임 때문에 closure environment와 original binding이
각자 값을 갖는다.

### 6.3 move와 once capture

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let token = acquireToken()
let consumeOnce = [move token] #once { value =>
    consume(token, value)
}
```

closure construction이 성공하면 original `token` owner는 environment로
이동한다. `#once` callable은 한 번 호출된다. capture `once token`과
callable `#once`는 별도 축이므로 문맥에 맞게 명시한다.

### 6.4 clone capture의 visible 책임

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
// config에는 exact Clone과 Display evidence가 있다고 가정한다.
let renderLater = [clone config] { =>
    config ~ display()
}
```

closure construction 시 Clone witness를 한 번 호출한다. clone이 오류나
effect를 선언하면 그 책임은 closure construction expression에 나타나야
한다.

## 7. 허용·거부·경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: OWNERSHIP_MODE_ADMISSION_FAILED; product: NOT_RUN -->
```deeplus
let token = acquireToken()
let action = [move token] #once { => use(token) }
use(token)
// OWNERSHIP_MODE_ADMISSION_FAILED
```

clone 가능해 보이는 자식이 있다는 이유로 deep clone을 합성하지 않는다.
environment publish 전 capture 하나가 실패하면 앞서 얻은 temporary를
역순 cleanup하고 partial closure를 escape시키지 않는다.

## 8. 다른 기능과의 연결

- `source!{...}` shallow derivation은 clone과 동의어가 아니다.
- `source!!{...}`는 admitted deep-clone responsibility를 요구한다.
- Pattern `move`는 structural test 성공 뒤 commit된다.
- Actor message move는 enqueue commit 전후 owner가 다르다.

## 9. Deeplus다운 작성 관례

- API signature에 consume/borrow 의도를 드러낸다.
- cheap해 보인다는 이유로 implicit copy를 추측하지 않는다.
- clone의 오류·효과가 허용되지 않는 경계에서는 explicit snapshot/value
  model을 선택한다.
- once-only resource는 `move`와 callable profile을 함께 검토한다.

## 10. 연습 문제

1. **복사:** `Int`를 `copy` capture하는 multiplier closure를 작성하라.
2. **빈칸 완성:** `archive(___ document)`와 호출
   `archive(___ document)`의 두 빈칸을 `move`로 채우고 성공 뒤 source
   place 상태를 적어라.
3. **설계:** graph snapshot API에서 shallow copy, Clone, deep copy 중
   무엇을 제공할지 cycle, shared subgraph, failure cleanup을 포함해 정하라.

## 11. 빠른 복습

- move는 owner를 옮기고 source를 moved로 만든다.
- copy는 admitted reusable 책임을 요구한다.
- clone은 witness 호출이며 effect/error가 있다.
- deep은 별도 graph profile이다.
- partial closure environment는 publish되지 않는다.

## 12. 정본 근거와 다음 장

- [Capture 계약](../../grammar-reference/05-functions-methods-closures-and-calls.md)
- [소유권 레퍼런스](../../grammar-reference/12-ownership-borrowing-and-responsibility.md)
- [타입 흐름 계약](../../../spec/contracts/type-flow-callable-coherence.json)

다음 장에서는 capture가 lifetime과 escape 경계에서 어떻게 검사되는지
배운다.
