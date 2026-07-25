# 01-05. 이름, 바인딩과 블록

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 현행 `let`, `var`, lexical block, local commit, 오른쪽 방향
바인딩을 설명한다. 실제 memory layout이나 optimizer 동작은 정하지 않는다.

## 2. 학습 목표

- 불변 바인딩과 가변 바인딩을 구분한다.
- 이름의 lexical scope와 lifetime을 설명한다.
- initializer가 성공한 뒤 이름이 원자적으로 생긴다는 모델을 이해한다.
- 오른쪽 방향 바인딩을 ordinary local binding으로 읽는다.

## 3. 선수 지식

함수 block과 Module의 기본 역할을 알고 있어야 한다.

## 4. 문제에서 출발하기

값을 계산하는 도중 실패할 수 있는데 이름을 먼저 공개하면, 다른 코드가
절반만 초기화된 값을 볼 수 있다. Deeplus local binding은 initializer를
한 번 평가하고 타입·ownership·effect 의무를 확인한 뒤 이름을 commit한다.
실패하면 부분 바인딩이 남지 않는다.

## 5. 핵심 모델

- `let`: 다시 대입할 수 없는 binding.
- `var`: 허용된 mutable place를 가진 binding.
- `{ ... }`: lexical scope와 cleanup region을 만드는 block.
- `expr -> $name`: `let name = expr`로 정규화되는 rightward surface.
- `expr -> $$name`: `var name = expr`로 정규화되는 rightward surface.

이 표면들은 initializer를 정확히 한 번 평가한다. `$`/`$$` 표기는 CST에
남지만 별도 `FlowBinding` AST/HIR/MIR identity를 만들지 않는다.

## 6. 단계별 예제

불변 중간값과 가변 작업값을 구분해 보자.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure clampAtZero(value: Int) -> Int
    throws Never
    effects {}
= {
    let doubled = value * 2
    var adjusted = doubled

    if adjusted < 0 {
        adjusted = 0
    }

    return adjusted
}
```

`doubled`은 다시 대입할 필요가 없으므로 `let`, branch에서 변경되는
`adjusted`는 `var`다. assignment는 place와 RHS를 한 번씩 평가하고
성공 뒤 최대 한 번 commit한다.

같은 local-binding 의미를 rightward surface로 쓸 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure successor(raw: Int) -> Int
    throws Never
    effects {}
= {
    raw + 1 -> $value: Int
    return value
}
```

`value`는 fresh local이어야 한다. 기존 이름, member, index, pattern을
rightward target으로 사용할 수 없다.

### 판정 trace, 미니 사례와 흔한 오해

binding을 만나면 이름이 선언되는 lexical scope, mutable 여부, initializer
평가, publish 시점을 차례로 본다. `let total = risky()`에서 `risky()`가
실패하면 `total`이라는 절반짜리 이름이 생기는 것이 아니다. `var`도
최초 binding은 원자적으로 만들어지고, 이후 assignment가 별도의 place
mutation을 수행한다. inner block이 같은 철자의 이름을 선언하면 두
이름의 identity와 수명은 다르며 block을 나갈 때 안쪽 이름만 사라진다.

미니 사례로 계산 중간값을 한 번 정한 뒤 바꾸지 않는다면 `let`을
선택한다. 반복 누적처럼 실제 상태 변화가 필요하면 `var`를 사용하되,
mutation 전후 invariant를 적는다. 흔한 오해는 `let`을 literal만 담는
칸, `var`를 아무 때나 바꿔도 되는 칸으로 보는 것이다. 둘 다 typed
binding이며 차이는 이후 place mutation 허용 여부다. shadowing도 기존
값의 갱신이 아니라 새 lexical identity의 생성이다.

## 7. 허용·거부·경계 사례

블록 안 이름은 밖으로 새어 나오지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; expected-rule: LOCAL_NAME_OUT_OF_BLOCK_SCOPE -->
```deeplus
private def invalidScope() -> Int = {
    if true {
        let local = 13
    }

    return local
}
```

`local`은 `if` block의 lexical scope에만 있다. checker가 같은 철자의
다른 이름을 추측하거나 값을 block 밖으로 승격하지 않는다.
`LOCAL_NAME_OUT_OF_BLOCK_SCOPE`는 교육용 name-resolution rule label이며
stable diagnostic ID가 아니다. 현재 catalog에는 이 일반 local-name
실패를 단독으로 소유하는 exact diagnostic ID가 없다.
`let@lazy`는 Recovery이고 현행 지연 표면은 `let#lazy`다. 지연 바인딩은
순수·동기·nonthrowing·resource-free 조건을 별도로 만족해야 한다.

## 8. 다른 기능과의 연결

pattern binding은 테스트와 binding을 하나의 transaction으로 commit한다.
move/borrow/inout 책임은 바인딩의 place state에 남는다. closure가 local을
capture하면 해당 이름의 lexical lifetime만으로 충분한지 escape 검사를
추가로 통과해야 한다. block을 나갈 때 resource cleanup 의무도 함께
검사한다.

## 9. Deeplus다운 작성 관례

- 기본은 `let`이고 실제 재대입이 필요할 때만 `var`를 쓴다.
- scope를 작게 유지해 이름과 borrow의 lifetime을 분명히 한다.
- rightward binding은 데이터 흐름을 읽기 쉽게 할 때만 사용한다.
- 실패 가능한 값을 숨기지 말고 `Option` 또는 `Result`로 드러낸다.
- 이름은 역할이 보이는 영어 단어를 사용한다.

## 10. 연습 문제

1. **따라 하기:** `let base = 10`, `var total = base`를 가진 함수를 만들고
   `total += 5` 뒤 반환한다.
2. **빈칸 완성:** `raw * 2 -> ___ doubled: Int`가 ordinary `let`으로
   정규화되도록 `$` 또는 `$$`를 고른다.
3. **스스로 설계하기:** 중첩 block 두 개를 가진 계산을 만들고 각 이름이
   보이는 범위를 표로 정리한다. 어떤 이름도 scope 밖에서 참조하지 않는다.

## 11. 빠른 복습

- `let`은 immutable binding, `var`는 mutable place다.
- initializer 성공 전에는 새 이름이 commit되지 않는다.
- block은 lexical scope와 cleanup 경계를 만든다.
- `$name`/`$$name`은 fresh ordinary local로 정규화된다.
- scope 밖 이름은 자동 승격되지 않는다.

## 12. 정본 근거와 다음 장

- [바인딩·block EBNF](../../../spec/grammar/deeplus.ebnf)
- [선언·바인딩·이름 참고서](../../grammar-reference/03-declarations-bindings-and-names.md)
- [평가·place·commit](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [타입과 place state](../../../spec/types/type-system.md)

이제 [실습: 타입이 있는 인사말](lab-01-typed-greeting.md)에서 Part 1을
한 source로 합친다.
