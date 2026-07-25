# Lab 6 — Generic renderer

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 목표

두 명목 타입에 `Display` conformance를 제공하고 generic renderer가 exact
witness를 사용하게 한다. extension은 별도 audit formatting에만 사용하고
operator/custom surface를 만들지 않는다.

## 준비

- 6.1~6.5를 읽는다.
- `where T conforms Display`와 `value ~ display()`를 설명할 수 있어야 한다.
- 결과는 static design이며 제품 실행이 아님을 기록한다.

## 누적 프로젝트 연결

| 연결 | 내용 |
|---|---|
| input prior | Part 05에서 만든 명목 domain type과 validated Enum 결과 |
| output | explicit `Display` evidence를 쓰는 renderer와 별도 audit extension |
| next | Part 07에서 renderer argument와 capture의 borrow·move 책임 추적 |

## 1단계 — Trait와 도메인 타입

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait Display {
    +def display+() -> String
        throws Never
        effects {}
}

public data class UserId(+let raw: Int)
public data class Invoice(+let number: Int, +let total: Rational)
```

## 2단계 — 두 explicit conformance

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public conformance UserId conforms Display {
    +def display+() -> String throws Never effects {} = {
        return "user:${self.raw}"
    }
}

public conformance Invoice conforms Display {
    +def display+() -> String throws Never effects {} = {
        return "invoice:${self.number} total=${self.total}"
    }
}
```

각 ground pair는 다른 conformance/witness identity를 갖는다.

## 3단계 — Generic renderer

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def renderOne<T>(borrow value: T) -> String
    where T conforms Display
= {
    return value ~ display()
}

public def renderAll<T>(values: List<T>) -> List<String>
    where T conforms Display
= {
    return [
        value ~ display()
        for value in values
    ]
}
```

comprehension 각 iteration에서 이미 고정된 `Display` evidence를 사용한다.
runtime reflection이나 문자열 method lookup은 없다.

## 중간 점검

- [ ] Trait method에 witness marker가 있다.
- [ ] conformance signature가 requirement의 error/effect와 맞는다.
- [ ] generic bound가 explicit하다.
- [ ] extension이나 import order를 witness로 쓰지 않았다.

## End-to-end evidence trace

`renderOne<UserId>` 호출을 끝까지 추적한다. generic substitution이
`T = UserId`를 고정하면 checker는 normalized target과 `Display`
instantiation으로 unique conformance를 선택한다. requirement의 receiver,
return, error, effect와 implementation responsibility를 맞추고 selected
`TraitWitnessId`를 HIR call에 결합한다. argument는 한 번 평가되며
renderer는 witness channel을 통해 `display+`를 호출한다. 반환 String이
준비된 뒤 결과를 한 번 publish한다.

conformance가 없으면 runtime duck typing을 시도하지 않고 checker
경계에서 거부한다. 같은 ground pair evidence가 둘이면 import order로
승자를 정하지 않고 ambiguity를 terminal로 남긴다. implementation이
`effects {}`를 초과하면 출력이 같아 보여도 responsibility mismatch다.
세 실패는 missing evidence, coherence, signature/effect 불일치로
구분한다.

named audit extension을 활성화해도 witness identity는 바뀌지 않는다.
extension call은 lexical candidate resolution을 따르고 generic renderer의
Trait channel을 대체하지 않는다. renderer가 borrow argument를 받으면
call region 밖 저장이나 actor transfer가 없다. 실패 전후 cleanup이
필요한 resource를 표시 대상으로 추가할 때도 witness 선택과 owner
transfer를 하나의 암시적 동작으로 합치지 않는다.

## Review rubric

1. **계약:** requirement가 label·ownership·return·throws·effect를
   빠짐없이 선언하는가?
2. **evidence:** target/Trait pair마다 explicit하고 unique한 conformance가
   있는가?
3. **lowering:** selected witness가 HIR/MIR에 고정되고 runtime 재검색이
   없는가?
4. **extension 분리:** audit extension이 conformance를 만들거나
   override하지 않는가?
5. **실패:** missing, ambiguity, responsibility mismatch를 구분하는가?
6. **상태:** TCC P1 7개와 product lanes를 OPEN/NOT_RUN으로 유지하는가?

각 항목을 `충족`, `부분 충족`, `재설계 필요`로 기록한다. 출력 문자열이
맞더라도 evidence identity나 effect 계약이 빠졌다면 완료가 아니다.
이 rubric은 design-static 검토이며 product PASS를 대신하지 않는다.

## 실패 회수와 책임 이전

missing evidence에서는 renderer body에 진입하지 않으므로 argument owner와
외부 effect는 caller에 그대로 남는다. ambiguity에서도 import order로
후보를 골라 계속하지 않고 exact target/Trait pair와 competing identity를
diagnostic으로 돌려준다. responsibility mismatch는 conformance
implementation을 고칠 문제이지 call site가 error/effect를 몰래
흡수할 문제가 아니다.

성공 trace에서는 caller가 `borrow value` region을 열고, checker가 고정한
witness를 통해 `display+`가 실행되며, 완성된 String만 새 owner로
publish된다. display 중 실패나 effect가 계약상 `Never`/`{}`를 넘는
설계로 바뀐다면 기존 requirement 아래에 끼워 넣지 않고 Trait 계약부터
재검토한다. audit extension은 lexical formatting만 담당하고 conformance
owner, result publication, cleanup을 대신하지 않는다.

rollback ledger에는 `검사 단계`, `아직 생성되지 않은 값`, `계속 살아
있는 owner`, `노출할 diagnostic`을 적는다. 이 네 항목을 채우면 출력
문자열이 같은 두 구현도 coherence와 effect 책임이 다른지 구별할 수 있다.
실제 compiler·backend 실행 전에는 모든 행을 design-static 예상으로
표시하고 product lane을 `NOT_RUN`으로 유지한다.

마지막 검토에서는 `UserId`와 `Invoice`를 서로 바꿔도 generic algorithm이
동일하고 선택된 witness만 정확히 달라지는지 확인한다. 새 타입을
추가했을 때 renderer를 수정하지 않고 해당 ground pair의 conformance만
제공하는지도 본다. 반대로 conformance를 제거하면 정적 missing evidence로
실패해야 하며 runtime fallback이나 audit extension으로 성공해서는 안
된다. 이 세 비교가 generic abstraction과 evidence 소유권을 함께
검증한다.

## 4단계 — 별도 audit extension

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public extension Invoice as audit {
    +def auditLabel() -> String = {
        return "INV-${self.number}"
    }
}

use Invoice::audit
let invoice = Invoice${ number: 7, total: <25/2> }
let publicText = renderOne(invoice)
let auditText = invoice ~ auditLabel()
```

`auditLabel`은 Display requirement를 대신 충족하지 않는다.

## 실패 실험

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN; product: NOT_RUN -->
```deeplus
public class Accidental {
    +def display.() -> String = { return "looks similar" }
}

let invalid = renderOne(Accidental!())
// STRUCTURAL_DUCK_TYPING_CONFORMANCE_FORBIDDEN
```

두 번째 실험으로 custom `operator <+>` declaration을 작성한 뒤
`CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT`가 왜 올바른 경계인지 설명하라.
그 코드를 positive 예제로 바꾸지 않는다.

## 확장 과제

1. **복사:** `OrderId`와 Display conformance를 추가한다.
2. **빈칸 완성:** `let ::mediaType: ___`과
   `<T as ___>::mediaType`의 빈칸을 모두 채워 associated value를
   명시적으로 읽는다.
3. **설계:** locale을 가진 formatter를 associated static이 아니라 explicit
   runtime service로 분리하고 ownership/effect contract를 작성한다.

## 완료 체크리스트

- [ ] structural duck typing을 사용하지 않았다.
- [ ] extension과 conformance를 분리했다.
- [ ] associated lookup은 명시적으로 qualification한다.
- [ ] 임의 custom operator를 추가하지 않았다.
- [ ] fixed-glyph admitted set을 `+`, `-`, `*`로 유지했다.
- [ ] TCC P1 7개를 포함한 OPEN P1 `22`, product lanes `15/15 NOT_RUN`을
      유지했다.

## 정본 근거

- [Trait 통합 사례](../../grammar-reference/24-integrated-worked-examples.md)
- [Trait/conformance 레퍼런스](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [operator 경계](../../grammar-reference/08-expressions-and-operators.md)
