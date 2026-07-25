# 09-04 — `law`, callable contract, assertion과 `def#guard`

## 1. 상태와 읽는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

여기서 assertion은 `law` body의 제한된 predicate assertion을 뜻한다.
`assert(...)`라는 별도 canonical Prelude API를 발명하지 않는다.

## 2. 학습 목표

- `requires`와 `ensures` callable contract를 읽는다.
- `law`가 실행 함수나 proof block이 아님을 설명한다.
- law body의 pure predicate 제한을 적용한다.
- `def#guard`의 책임과 narrowing 한계를 이해한다.

## 3. 선수 지식

pure callable, refinement R0 predicate, Trait/conformance, HIR/MIR 경계를
알고 있어야 한다.

## 4. 문제에서 출발하기

“이 함수는 양수만 받는다”, “이 Trait은 반사 법칙을 만족한다”,
“이 predicate는 안전한 guard다”는 서로 비슷해 보여도 owner가 다르다.
계약은 callable boundary를 설명하고, law는 선언적 tooling metadata이며,
guard는 실제 Bool callable이다.

## 5. 핵심 모델

- callable `requires`/`ensures`: 호출 전후의 정적 계약.
- `law Name { ... }`: Trait/conformance/bitfield에 붙는 비실행 metadata.
- law assertion: `requires`, `ensures`, `invariant` 역할의 restricted pure
  predicate.
- `def#guard`: total, terminating, pure, nonsuspending, nonconsuming Bool
  callable.
- 현재 guard 호출에는 refinement summary owner가 없으므로 자동
  narrowing fact를 만들지 않는다.

## 6. 단계별 예제

callable contract는 함수 signature와 body 사이의 경계를 설명한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def boundedAdd(left: Int, right: Int) -> Int
    throws Never
    effects {}
    requires left >= 0 and right >= 0
    ensures true
= {
    return left + right
}
```

law body는 ordinary statement block이 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait ReflexiveRelation {
    law Reflexive {
        requires true
        ensures true
        invariant 1 == 1
    }
}
```

tooling이 property evidence를 결합할 수 있지만 law 자체가 호출되거나
MIR event를 만들지는 않는다.

## 7. 허용·거부·경계 사례

현행 guard profile:

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def#guard validPort(port: Int) -> Bool = {
    return port >= 1 and port <= 65_535
}

if validPort(candidate) {
    useCandidate(candidate)
}
```

위 branch가 `candidate`의 declared type을 자동 refinement type으로
바꾸지는 않는다. inline R0 predicate와 typed pattern이 만드는 flow fact와
guard call result를 구분해야 한다.

거부: law body에서 I/O와 arbitrary call을 실행한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
trait InvalidAudit {
    law BadLaw {
        writeAudit("not a pure proposition")
    }
}
// LAW_BODY_ITEM_NOT_ADMITTED
```

mutation, I/O, `await`, `spawn`, `throw`, cleanup도 같은 이유로 거부된다.

## 8. 다른 기능과의 연결

- refinement type은 explicit construction/cast/pattern boundary에서
  proof를 요구한다.
- guarded match arm은 이미 허용된 structural partition만 좁히며 coverage를
  대신하지 않는다.
- conformance law가 witness나 default implementation을 자동 합성하지 않는다.
- Preview의 conformance proof block은 현재 law와 별도이며 nonactivatable이다.

### 판정 추적

호출 전에는 `requires`를 callable boundary의 전제로, 정상 반환 뒤에는
`ensures`를 결과 계약으로 읽는다. `law`를 만나면 실행 graph가 아니라
Trait·conformance tooling metadata에 등록하고, body item이 제한된 pure
predicate family인지 검사한다. `def#guard` 호출은 ordinary Bool 결과를
만들되 total·terminating·pure·nonsuspending·nonconsuming 조건을 먼저
검사한다. 이 세 경로는 이름이 비슷해도 HIR residue가 다르다.

미니 사례로 `validPort(candidate)`가 참이면 그 branch에서 Bool 사실은
알 수 있지만 `candidate: Port`라는 새 typed fact는 생기지 않는다.
정말 `Port`가 필요하면 refinement construction, checked conversion 또는
typed pattern 같은 증명 owner를 사용해야 한다.

### 흔한 오해

law가 test처럼 매 실행마다 호출된다고 보거나, contract가 body 실패를
자동 복구한다고 보아서는 안 된다. `def#guard`라는 이름만으로 arbitrary
predicate가 narrowing summary를 제공하지도 않는다. 튜토리얼 fixture의
`assert` test oracle 역시 이 language-level law assertion과 다른
application-owned 경계다.

설계 검토에서는 같은 조건을 세 열로 다시 써 보면 차이가 선명해진다.
“호출 전에 범위가 유효해야 한다”는 `requires`, “관계가 모든 구현에서
반사적이어야 한다”는 Trait `law`, “현재 입력이 범위 안인가”를 계산하는
것은 `def#guard`다. 첫째는 호출 책임, 둘째는 선언적 명제, 셋째는 실행
값이다. 하나의 조건을 무조건 세 곳에 복제하면 진단 owner가 셋으로
갈라지므로 실제 소비자가 요구하는 경계 하나를 먼저 고른다.

또한 contract가 정적으로 기록되었다는 사실과 target에서 contract
instrumentation이 실행되었다는 사실을 구분한다. 이 튜토리얼은 전자의
설계만 설명하며 후자의 제품 PASS를 주장하지 않는다.

## 9. Deeplus다운 작성 관례

실행해야 하는 검증은 ordinary pure/guard 함수로, API boundary의 전제와
결과는 contract로, 모든 구현이 지켜야 할 선언적 성질은 law로 쓴다.
세 surface가 비슷한 단어를 공유해도 서로의 권위를 빌리지 않는다.

## 10. 연습 문제

1. **따라 하기:** 1-based index가 양수인지 검사하는 `def#guard`를
   작성하라.
2. **빈칸 완성:** pure law body에서 허용되지 않는 `await`, mutation,
   arbitrary call 세 칸을 찾아 설명하라.
3. **스스로 설계하기:** 유효한 식별자 규칙을 contract, guard, law 중
   어디에 두어야 하는지 use-site별로 나누어라.

## 11. 빠른 복습

- contract, law, guard는 서로 다른 owner다.
- law는 ordinary MIR statement가 아니다.
- guard는 Bool callable이지만 자동 narrowing summary는 없다.
- runtime `assert` API를 이 장이 새로 정의하지 않는다.

## 12. 정본 근거와 다음 장

- [Class/Trait law 참조](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [refinement와 guard](../../grammar-reference/04-types-generics-and-refinement.md)
- [정확 LawDecl 문법](../../../spec/grammar/deeplus.ebnf)

다음 장에서는 잘못된 source가 어느 단계에서 어떤 첫 진단으로 끝나는지
읽는다.
