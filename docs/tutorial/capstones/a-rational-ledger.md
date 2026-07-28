# 종합 프로젝트 A — Rational 원장

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 이 프로젝트의 결과는 정본 설계에 따른 정적·의미적 예상이다. 실제
> compiler, runtime, serialization, product lane 실행은 `NOT_RUN`이다.

## 1. 만들 것

금액의 비율과 배분을 부동소수 오차 없이 계산하는 작은 원장을 설계한다.
원장은 거래를 Enum으로 분류하고, `Rational`로 비율을 보존하며,
refinement와 pattern으로 잘못된 거래를 입력 경계에서 거부한다.

이 프로젝트는 다음 질문을 한꺼번에 다룬다.

- 왜 `<p/q>`가 단순한 나눗셈 식이 아닌 정확한 값인가?
- raw 입력과 검증된 도메인 값을 어떻게 분리하는가?
- Enum payload와 pattern guard가 어떻게 조기 오류 검출을 돕는가?
- 반올림 정책은 숫자 타입이 아니라 어느 경계가 소유해야 하는가?

## 2. 도메인 불변식

비율은 `0`보다 크거나 같고 `1`보다 작거나 같아야 한다. 잔액은 원장
내부에서는 정확한 `Rational`로 유지한다. 화면 표시나 외부 통화 단위로
바꾸는 반올림은 이 프로젝트의 핵심 모델 밖에 둔다. 따라서
`Float64`로 자동 변환하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::ledger::model

public type Ratio = Rational in <0/1> .. <1/1>
public type PositiveAmount = Rational where > <0/1>

public enum RawEntry {
    credit(Rational)
    debit(Rational)
    allocate(Rational, Rational)
}

public enum Entry {
    credit(PositiveAmount)
    debit(PositiveAmount)
    allocate(PositiveAmount, Ratio)
}
```

`RawEntry`는 외부에서 온 아직 검증되지 않은 값을 보존한다. `Entry`는
checked refinement conversion이 성공한 뒤에만 만들 수 있는 도메인
값이다. 이 둘을 나누면 public 원장 연산이 raw payload를 우회해 받지
않으면서도 입력 경계를 명시적으로 연습할 수 있다.

## 3. 검증과 정규화

`def#guard`는 순수하고 전체적인 Bool callable profile이다. eligible
body의 `GuardSummaryV1`은 direct truth-test와 stable actual에서만
branch-local narrowing을 제공한다. stored Bool이나 arbitrary wrapper의
결과까지 proof로 확대하지 않는다. exact refined payload나 상세 실패가
필요하면 checked cast를 사용한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def#guard isRatio(value: Rational) -> Bool = {
    return <0/1> <= value <= <1/1>
}

public def normalize(entry: RawEntry) -> Option<Entry>
    throws Never
    effects {}
= {{
    RawEntry::credit(amount) =>
        @match (amount as? PositiveAmount) {
            ::some(valid) => ::some(Entry::credit(valid))
            ::none => ::none
        }

    RawEntry::debit(amount) =>
        @match (amount as? PositiveAmount) {
            ::some(valid) => ::some(Entry::debit(valid))
            ::none => ::none
        }

    RawEntry::allocate(amount, ratio) if isRatio(ratio) =>
        @match (amount as? PositiveAmount) {
            ::some(validAmount) =>
                @match (ratio as? Ratio) {
                    ::some(validRatio) =>
                        ::some(Entry::allocate(validAmount, validRatio))
                    ::none => ::none
                }
            ::none => ::none
        }

    RawEntry::allocate(_, _) => ::none
}}
```

여기서 각 arm의 binding은 arm-local transaction이다. 구조와 guard가
모두 성공한 edge에서만 binding이 commit된다. 실패한 arm의 `amount`나
`ratio`는 다음 arm으로 새지 않는다. `isRatio`는 빠른 판정일 뿐
refinement proof를 만들지는 않으므로, 성공 arm에서도 `as? Ratio`가
검증된 payload를 별도로 만든다.

## 4. 원장 fold

현재 `Rational`의 닫힌 연산 corridor를 사용한다. division을 임의 fixed
glyph conformance로 넓히지 않고, 필요한 나눗셈은 정본 named API 계약을
따른다. 배분은 이미 검증된 비율과 곱하므로 `*`를 사용할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def apply(balance: Rational, entry: Entry) -> Rational
    throws Never
    effects {}
= {{
    Entry::credit(amount)          => balance + amount
    Entry::debit(amount)           => balance - amount
    Entry::allocate(amount, ratio) => balance - (amount * ratio)
}}

public def foldLedger(entries: Sequence<Entry>) -> Rational
    throws Never
    effects {}
= {
    var balance = <0/1>
    for entry in entries {
        balance = apply(balance, entry)
    }
    return balance
}
```

평가 순서는 source order다. 각 거래는 한 번만 읽고, 앞 거래의 결과가
다음 거래의 입력이 된다. optimizer는 관찰 가능한 failure·cleanup·effect
순서를 바꿀 수 없다.

## 5. 거부와 경계 사례

다음 코드는 세 가지 이유로 좋은 원장 코드가 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let ratio: Ratio = <5/4>       // refinement proof 실패
let amount = 0.1 + 0.2         // 정확한 원장 값 대신 Float 사용
let result = <1/3> / <2/5>     // Rational fixed-glyph division을 가정
```

첫째 줄은 `Ratio`의 상한을 위반한다. 둘째 줄은 문법 오류가 아닐 수
있지만 정확 수 원장이라는 도메인 계약을 잃는다. 셋째 줄은 Rational의
checked named division 정책을 건너뛴다. 문법상 쓸 수 있는지와 이
도메인에서 올바른지는 별개의 질문이다.

## 6. 단계별 구현 순서

1. `RawEntry`, `Entry`와 정확 수 refinement를 작성한다.
2. raw 거래를 checked conversion으로 `Option<Entry>`에 정규화한다.
3. 세 case를 모두 처리하는 `apply`를 만든다.
4. Sequence를 source order로 fold한다.
5. 표시 반올림을 core 원장 밖의 adapter 책임으로 문서화한다.
6. negative amount, 경계 ratio `0/1`, `1/1`, 범위 밖 ratio를 표로 만든다.

## 7. 중간 점검

- `<6/8>`의 source spelling은 CST에 남을 수 있지만 값은 `3/4`로
  정규화된다.
- `Rational`과 artifact SHA, serialization tag는 서로 다른 identity
  domain이다.
- pattern 성공 전에는 payload binding을 공개하지 않는다.
- `def#guard` narrowing의 summary/direct-test/stable-place 조건을 확인한다.
- 실행 결과나 성능 수치는 아직 주장하지 않는다.

### 7.1 한 거래를 끝까지 추적하기

`RawEntry::allocate(<9/2>, <2/3>)`가 들어왔다고 가정하자. parser는 두 `<p/q>`
철자를 각각 하나의 Rational literal 후보로 만들고 checker는 분모가
양수인지 확인한다. 값 계층에서는 이미 `9/2`, `2/3`인 기약 표현이다.
`normalize`의 `RawEntry::allocate` pattern이 VariantId와 payload shape를
먼저 검사하고, guard와 두 checked conversion이 성공한 뒤에만
`PositiveAmount`와 `Ratio` payload를 가진 `Entry::allocate`를 만든다.
`apply`는 이 검증된 값으로 `9/2 * 2/3 = 3/1`을 계산해 잔액에서 뺀다.

이 추적에서 source spelling, Rational value, Enum case identity, pattern
binding, 원장 잔액은 다섯 개의 다른 관찰 층이다. `<6/8>` 같은 철자를
보존하는 일은 audit provenance에 유용하지만 값 비교가 `6/8`과 `3/4`를
다르게 보게 만들지 않는다. 반대로 serialization code나 표시용 소수
문자열은 값 identity에서 자동 파생되는 외부 계약으로 가정하지 않는다.

### 7.2 실패가 원장을 부분 변경하지 않게 하기

거래 payload 계산이나 refinement 확인이 실패하면 그 거래의 잔액
변경은 publish되지 않아야 한다. 이를 위해 “먼저 balance를 바꾼 다음
되돌리는” 방식보다 입력을 전부 검증하고 새 balance를 계산한 뒤 한 번
commit하는 구조가 명료하다. cleanup이 필요한 payload가 있다면 성공한
temporary만 역순으로 정리한다. 이 원칙은 이후 ownership과 failure
transaction 장에서 더 일반적인 규칙으로 다시 등장한다.

## 8. 연습 문제

1. **따라 하기:** `RawEntry::credit(<5/2>)`,
   `RawEntry::debit(<1/3>)`를 정규화하고 접는 과정을 종이에 exact
   fraction으로 계산하라.
2. **빈칸 완성:** `normalize`에 `amount == 0` 정책을 명시하고 거부 또는
   수용 중 한쪽을 선택한 이유를 적어라.
3. **직접 설계:** 외부 통화 표시 adapter를 설계하되, rounding mode가
   원장 core에 암시적으로 스며들지 않게 signature를 작성하라.
4. **경계 과제:** `<2/0>`이 lexer 실패가 아니라 어떤 단계의 진단인지
   문법 참조서에서 찾아 설명하라.
5. **확장 과제:** 거래마다 audit label을 붙인 Record payload를
   설계하고 pattern exhaustiveness가 유지되는지 검토하라.

## 9. 완료 체크리스트

- [ ] 원장 내부 계산은 Rational이다.
- [ ] ratio refinement의 하한·상한이 명시됐다.
- [ ] 모든 Enum case를 다룬다.
- [ ] 실패한 pattern binding이 commit되지 않는다.
- [ ] 표시·직렬화 반올림은 별도 경계다.
- [ ] product 상태를 `NOT_RUN`으로 남겼다.

## 10. 정본 근거

- [리터럴과 exact numeric](../part-02-values/02-02-rational-complex.md)
- [refinement와 narrowing](../part-04-type-system/04-01-inference-aliases-refinement.md)
- [현행 Enum](../part-05-data-modeling/05-03-enum-current-surface.md)
- [언어 참조: lexical structure](../../grammar-reference/01-lexical-structure.md)
- `spec/contracts/rational-complex-numeric-coherence.json`
