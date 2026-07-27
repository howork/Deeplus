# 02-05. 표현식과 평가 순서

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 source-observable evaluation, branch laziness, assignment commit의
현행 설계를 설명한다. optimizer/backend 실행을 검증했다는 뜻은 아니다.

## 2. 학습 목표

- expression과 argument가 왼쪽부터 한 번 평가되는 원칙을 이해한다.
- label binding과 runtime evaluation order를 분리한다.
- ternary, `@if`, Option coalescing의 lazy arm을 구분한다.
- precommit failure가 원래 place를 보존하는 이유를 설명한다.

## 3. 선수 지식

함수 호출, `let`/`var`, operator precedence를 알고 있어야 한다.

## 4. 문제에서 출발하기

named argument를 formal 순서와 다르게 적었을 때 compiler가 먼저 formal
순서로 재배열해 평가하면 I/O, failure, cleanup 순서가 바뀔 수 있다.
Deeplus는 label 결합과 source evaluation order를 분리한다. label은
정적으로 parameter를 고르지만 expression은 source에 적힌 순서로
평가된다.

## 5. 핵심 모델

- 별도 short-circuit 법칙이 없으면 왼쪽부터 정확히 한 번 평가.
- named label은 static call-shape identity이고 runtime String이 아님.
- ternary와 total `@if`는 선택된 arm만 평가.
- `?:`는 Option의 한 layer만 lazy fallback.
- assignment는 target place와 RHS를 한 번씩 평가하고 성공 뒤 commit.
- 정적으로 거부된 expression은 runtime evaluation 자체가 없음.

## 6. 단계별 예제

named binding과 source order를 분리해 읽는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure difference(first: Int, second: Int) -> Int
= {
    return first - second
}

let value = difference(
    second: 20,
    first: 50,
)
```

두 label은 각각 formal에 결합되지만 expression 평가 순서는 source의
`20`, `50` 순서다. 순수 literal이라 관찰 차이는 없지만 effectful
expression이어도 이 순서를 formal 순서로 바꿀 수 없다.

조건식은 arm을 lazy하게 선택한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let port: Int = secure ? 443 : 80
let selected: Int = maybePort ?: 80

let detailed: String = @if secure {
    "secure"
} else {
    "plain"
}
```

ternary condition은 `Bool`이어야 하고 두 arm의 normalized type과
responsibility가 join되어야 한다. `@if`는 값 표현식이므로 total
`else`가 필요하다.

### 판정 trace, 미니 사례와 흔한 오해

복합 expression은 먼저 source에 나타난 evaluation event를 번호로 적고,
label binding이나 branch 선택 같은 정적 결정을 별도 열에 기록한다.
named argument를 formal 순서와 다르게 써도 expression event는 source
순서다. lazy control에서는 condition을 먼저 평가하고 선택된 arm만
이어진다. assignment는 target place와 RHS를 각각 한 번 판정한 뒤 모든
검사가 성공해야 최종 write를 commit한다.

미니 사례로 `choose(second: loadB(), first: loadA())`를 생각하자. label은
각 formal에 정확히 결합하지만 `loadB()`가 먼저 평가된다. 흔한 오해는
compiler가 formal order로 재배열하거나 순수해 보이는 호출을 자동으로
한 번만 실행할 것이라는 기대다. exactly-once는 한 expression occurrence의
평가 법칙이지 서로 다른 두 occurrence의 memoization 약속이 아니다.
failure가 commit 전에 나면 원래 target place와 owner가 보존된다.

이 규칙은 성능을 막는 지침이 아니다. backend는 관찰 결과가 같은 범위에서
최적화할 수 있지만 effect, failure, owner transfer와 cleanup 순서를
바꾸어서는 안 된다.

## 7. 허용·거부·경계 사례

기대 타입 없이 서로 다른 arm을 anonymous Union으로 합성하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic: TERNARY_BRANCH_TYPE_MISMATCH -->
```deeplus
let mixed = ready ? 1 : "one"
```

의도한 closed Union이 있다면 먼저 alias/expected type을 명시하고 각
arm을 그 정확한 alternative로 검사해야 한다. compound assignment에서
RHS failure나 overflow가 나면 기존 place는 유지되며 hidden partial
load/store가 남지 않는다.

## 8. 다른 기능과의 연결

호출 unfold, collection entry, capture acquisition도 source order로 한
번 평가된다. pattern은 구조를 nonconsuming하게 시험하고 성공 뒤 binding과
move를 원자 commit한다. actor send는 enqueue commit 전과 후의 owner
책임이 다르며 backend가 이를 재배열할 수 없다.

## 9. Deeplus다운 작성 관례

- effect나 failure 순서가 중요하면 source order가 보이게 줄을 나눈다.
- 복잡한 branch는 ternary보다 total `@if`를 선호한다.
- expected type 없이 branch 결과를 암묵 Union으로 기대하지 않는다.
- mutation은 계산 성공 뒤 commit된다는 모델로 읽는다.
- expression을 두 번 호출해도 compiler가 memoize할 것이라 가정하지 않는다.

## 10. 연습 문제

1. **따라 하기:** named argument 세 개를 formal과 다른 순서로 호출하고
   binding 순서와 evaluation 순서를 각각 적는다.
2. **빈칸 완성:** `let value = condition ? left : ___`에서 두 arm이 같은
   exact type이 되도록 expression을 채운다.
3. **스스로 설계하기:** Option fallback과 total `@if`를 각각 사용하는
   사례를 만들고 어떤 branch가 평가되지 않는지 설명한다.

## 11. 빠른 복습

- label binding과 expression evaluation은 별도다.
- 기본 평가는 source order, exactly once다.
- ternary/`@if`/`?:`는 각자의 닫힌 lazy 법칙을 가진다.
- branch join이 anonymous Union을 만들지 않는다.
- precommit failure는 원래 place와 owner를 보존한다.

## 12. 정본 근거와 다음 장

- [expression/operator 참고서](../../grammar-reference/08-expressions-and-operators.md)
- [평가·commit·MIR](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [call-shape와 source order](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [MIR semantics](../../../spec/mir/semantics.md)

이제 [실습: 예산과 복소 신호](lab-02-budget-complex-signal.md)에서 exact
numeric 값과 평가 법칙을 합친다.
