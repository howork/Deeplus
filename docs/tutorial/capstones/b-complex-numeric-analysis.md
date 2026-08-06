# 종합 프로젝트 B — Complex와 NumericArray 신호 분석

> 상태: `MIXED_STATUS`
>
> scalar Complex와 NumericArray transpose는 현행 Stable 설계다. 일부
> NumericArray power 표면은 Preview gated다. 모든 product 실행은
> `NOT_RUN`이다.

## 1. 만들 것

복소 신호 표본의 에너지를 계산하고, 표본을 행렬 형태로 정리해 transpose
관계를 설명하는 순수 분석 모듈을 설계한다. 핵심은 `3.0 + 4.0i`가
`Float64` 두 개를 어림짐작으로 붙인 문법 설탕이 아니라 닫힌
`Complex<Float64>` 값이라는 점, 그리고 scalar `^`와 NumericArray
표면을 혼동하지 않는 것이다.

## 2. 입력 모델

bare `i`는 보통 식별자다. 허수 리터럴 token은 실수 literal에 붙은
형태이고, 명시적 단위는 `Complex::i`다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
module tutorial::signal::model

public let reference: Complex = 3.0 + 4.0i
public let phaseUnit: Complex = Complex::i

public type Signal = Sequence<Complex<Float64>>
public type Energy = Float64 where >= 0.0
```

`3.0 + 4.0i`에서 `4.0i`는 하나의 허수 literal token이며, 덧셈은 닫힌
same-Rep Complex corridor 안에서 해석된다. `Float32` 성분을 원하면 결과
annotation으로 두 operand를 역으로 고르지 말고 typed anchor를 둔다.

```deeplus
let real32: Float32 = 1.5
let compact: Complex<Float32> = real32 + 0.25i
```

## 3. scalar 분석

복소수 에너지는 실수 성분과 허수 성분의 제곱 합으로 정의할 수 있다.
실제 API 이름은 정본 library surface에 따라 확인해야 하므로 여기서는
도메인 함수의 signature와 책임을 중심으로 본다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def energy(sample: Complex<Float64>) -> Float64
    throws Never
    effects {}
= {
    return sample.real * sample.real + sample.imag * sample.imag
}

public def totalEnergy(signal: Signal) -> Float64
    throws Never
    effects {}
= {
    var total = 0.0
    for sample in signal {
        total += energy(sample)
    }
    return total
}
```

이 코드는 source order로 각 표본을 한 번씩 평가한다. 순수 함수라는
사실은 임의 재결합으로 IEEE 결과를 바꿔도 된다는 뜻이 아니다. 부동소수
연산의 관찰 가능한 값 규칙은 별도로 보존한다.

## 4. NumericArray와 방향

NumericArray는 shape와 orientation 증거를 가진다. 붙은 postfix `A^`는
transpose이고, 띄어 쓴 infix `base ^ exponent`는 power다. glyph가
같아도 token adjacency와 grammar goal이 다르다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let samples = #2,2[
    3.0 + 4.0i, 1.0 + 0.0i;
    0.0 + 2.0i, 2.0 - 1.0i;
]

let transposed = samples^
```

이 예제의 정확한 literal sigil과 element domain은 NumericArray 정본
profile을 함께 확인해야 한다. transpose는 새 orientation witness를
만들며 원본을 암시적으로 mutable place로 만들지 않는다.

## 5. Preview gated power 울타리

다음 예제는 일반 현행 코드가 아니다. 해당 exact gate와 profile이
선택된 검토 환경에서만 의미 후보가 된다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN -->
```deeplus
// PREVIEW_GATED_PRODUCT_NOT_RUN
#preview(numeric_array_elementwise_power_msp)
let squared = samples ^ 2
```

이 표면이 보인다고 arbitrary custom operator가 허용되는 것은 아니다.
또한 scalar `2.0 ^ 3.0`과 NumericArray elementwise power는 서로 다른
admission row다.

## 6. 거부와 경계 사례

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let a: Complex = i                 // i는 내장 상수가 아님
let real32: Float32 = 1.0
let b = real32 + 2.0               // real끼리 더해 Complex가 되지 않음
let c = samples %% 2               // 임의 custom operator 없음
```

첫째 줄은 `Complex::i` 또는 허수 literal을 사용해야 한다. 둘째 줄은
Float32/Float64 Rep가 다르다. 셋째 줄은 사용자 정의 operator 표면을
발명한다. operator overloading은 admitted fixed glyph와 exact Trait
conformance corridor를 넘어가지 않는다.

## 7. 분석 보고서 설계

분석 결과를 Record로 묶되 runtime layout이나 ABI identity로 의미
identity를 대체하지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public schema SignalReport {
    count: Int
    totalEnergy: Float64
    peak: Complex<Float64>
}

public def report(signal: Signal) -> Option<SignalReport>
    throws Never
    effects {}
= {
    if signal.length == 0 {
        return ::none
    }
    // peak 선택의 tie rule은 호출자가 읽을 수 있게 별도 helper에 둔다.
    return ::some(buildReport(signal))
}
```

빈 입력 정책을 `Option`에 드러내므로 숨은 sentinel Complex 값을 만들지
않는다. peak의 tie rule도 iteration order에 우연히 맡기지 않는다.

### 7.1 type과 shape 판정 장부

분석 함수를 작성하기 전에 operand마다 다음 장부를 채운다.

| 식 | scalar/array | Rep 또는 element type | shape/orientation | 상태 |
|---|---|---|---|---|
| `3.0 + 4.0i` | scalar | `Complex<Float64>` | 해당 없음 | Current |
| `let i32: Complex<Float32> = 1.0i` | scalar | `Complex<Float32>` | 해당 없음 | Current |
| `samples` | NumericArray | `Complex<Float64>` | literal에서 고정 | Current |
| `samples^` | NumericArray | 동일 element | transpose orientation | Current |
| `samples ^ 2` | NumericArray | gate matrix가 결정 | 동일 shape 후보 | Preview gated |

이 표를 먼저 만들면 expected result가 operand domain을 몰래 선택하거나,
Float32/Float64를 결과 type에 맞춰 암시적으로 올리는 오류를 막을 수
있다. 특히 `let z: Complex = 2 ^ -3`처럼 결과 annotation만으로 real
base/exponent를 Complex power cell에 넣을 수 없다.

### 7.2 계산과 표시를 분리하기

분석 core는 Complex와 Float 값을 반환하고 locale, 자릿수, 단위 표시는
별도 adapter가 소유한다. `magnitude`를 문자열로 너무 일찍 바꾸면
후속 threshold 비교와 exact Rep 추적이 어려워진다. 반대로 보고서
경계에서는 signed zero, NaN, branch 정보가 사용자에게 어떻게 보이는지
정책을 명시해야 한다. 이 정책은 `Display`, serialization, scientific
codec 가운데 하나를 자동 선택하지 않는다.

### 7.3 관찰 순서

Sequence의 표본 식은 source order로 한 번씩 평가한다. 계산이 순수해도
IEEE 덧셈의 재결합이 항상 같은 bit 결과를 준다고 가정할 수 없다.
따라서 “parallel reduction으로 바꿔도 의미가 같다”는 최적화 주장을 이
프로젝트가 만들지 않는다. 성능과 병렬 reduction profile은 결과 허용
오차와 결정성 계약을 가진 별도 설계가 필요하다.

### 7.4 branch와 특수값을 문서화하기

Complex의 `sqrt`, `log`, non-integer power는 하나의 principal branch를
선택한다. “수학적으로 답이 여러 개다”라는 사실과 ordinary API가 어느
값을 반환하는지는 구분해야 한다. alternate branch가 필요하면 branch
identity를 받는 named API를 사용하고, expected result나 주변
NumericArray shape가 branch를 몰래 고르게 하지 않는다.

실수 영역의 음수 제곱근이 자동으로 Complex로 넓어지지 않는 점도
중요하다. real power cell은 real 규칙을 따르고, Complex 결과를 원하면
입력 domain을 명시적으로 Complex로 만든다. NaN, infinity, signed zero가
있는 표본은 equality·ordering·peak 선택에서 별도 boundary case다.
`Complex`가 strong `Ord`나 `Keyable`을 암시적으로 얻는다고 가정하지
않는다.

## 8. 연습 문제

1. **따라 하기:** `3.0 + 4.0i`의 에너지를 계산하고 왜 결과가 실수인지
   설명하라.
2. **빈칸 완성:** `totalEnergy`에 빈 Sequence를 넣었을 때의 결과와
   effect/error row를 적어라.
3. **직접 설계:** peak가 같은 두 표본의 tie rule을 source-order와
   index identity 중 하나로 명시하라.
4. **경계 과제:** `A^`와 `A ^ 2`가 token과 AST에서 어떻게 달라야
   하는지 서술하라.
5. **Preview 검토:** NumericArray power를 Current로 올리기 전에 필요한
   shape, element-domain, diagnostic, product test 증거를 목록화하라.

## 9. 완료 체크리스트

- [ ] 허수 literal과 ordinary `i`를 구분했다.
- [ ] Complex Rep를 암시적으로 섞지 않았다.
- [ ] transpose와 power를 구분했다.
- [ ] Preview gated 예제를 Current로 소개하지 않았다.
- [ ] custom operator를 만들지 않았다.
- [ ] product 실행 상태는 `NOT_RUN`이다.

## 10. 정본 근거

- [Rational과 Complex](../part-02-values/02-02-rational-complex.md)
- [NumericArray와 선형대수](../part-08-collections-math/08-04-numeric-array-linear-algebra.md)
- [Preview gated](../part-12-preview-evolution/12-02-preview-gated.md)
- `spec/contracts/rational-complex-numeric-coherence.json`
- `spec/contracts/value-operator-indexing-coherence.json`
