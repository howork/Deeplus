# 04-01. 추론, alias와 refinement

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 local bidirectional inference, 명시적 type owner와 refinement
경계를 설명한다. 정적 설계 계약이며 compiler 제품 실행 증거는 아니다.

## 2. 학습 목표

- local inference와 명시적 public type 경계를 구분한다.
- type alias/refinement declaration의 visibility를 적용한다.
- `as?`, `as!`, `T::check`의 결과와 실패 책임을 구분한다.
- refinement의 `PROVED`/`DISPROVED`/`UNKNOWN` 판정을 설명한다.

## 3. 선수 지식

Part 1의 `let`/명시적 type visibility와 Part 2의 기본 literal을 알고
있어야 한다.

### 미리 보는 최소 모델과 후속 심화

`Option<T>`는 성공 payload가 있거나 없음을 나타내는 두-case container,
`Result<T, error E>`는 성공 payload와 상세 오류 payload를 구분하는
두-case container라는 최소 직관만 먼저 쓴다. 이 장에서는 `as?`와
`T::check`가 어떤 모양의 결과를 돌려주는지 비교하고, case 선언과
exhaustive pattern은 다음 장에서 자세히 배운다. 따라서 Option/Result는
선수 지식이 아니라 refinement 경계를 설명하기 위한 국소 안내다.

## 4. 문제에서 출발하기

정수 `8080`은 값만 보면 `Int`지만, 네트워크 port로 쓰려면 허용 범위를
증명해야 한다. 단순 대입이 그 증명을 몰래 수행하거나 실패 정보를
버리면 API 경계가 불명확해진다. Deeplus는 inferred base type과
refinement identity, 변환의 실패 channel을 분리한다.

## 5. 핵심 모델

- initializer와 expected type을 함께 사용해 local type을 추론한다.
- top-level type-producing declaration은 visibility를 명시한다.
- `type Port = Int where this ...`는 base type 위의 predicate를 소유한다.
- `value as? T`는 `Option<T>`를 돌려 상세 실패를 버린다.
- `value as! T`는 성공 시 `T`, 실패 시 명시된 assertion Defect다.
- `T::check(value)`는 `Result<T, error E>`로 상세 오류를 보존한다.
- 증명할 수 없는 `UNKNOWN`을 silent narrowing으로 바꾸지 않는다.

## 6. 단계별 예제

local inference와 public refinement 경계를 함께 본다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public type Port = Int where this >= 0 and this <= 65_535

let inferred = 8_080
let explicit: Int = inferred
let maybePort: Option<Port> = inferred as? Port
```

`inferred`의 local type은 initializer에서 알 수 있지만 `Port` proof는
별도다. `as?`는 성공 payload 또는 `Option::none`만 남긴다.

상세 진단이 필요하면 `check`를 사용한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let raw: Int = 70_000
let checked: Result<Port, error RefinementError> = Port::check(raw)

let message: String = @match checked {
    Result::ok(port) => "port:${port}"
    Result::err(error) => "invalid:${error}"
}
```

원래 expression은 한 번 평가되고, 성공 뒤에만 `Port` payload가
commit된다. 실패는 상세 `RefinementError`로 보존된다.

### 판정 trace, 미니 사례와 흔한 오해

refinement 경계에서는 source expression을 한 번 평가하고 base type을
확정한다. predicate가 정적으로 참이면 PROVED, 모순이면 DISPROVED,
runtime 정보가 필요하면 UNKNOWN이다. UNKNOWN을 자동 통과시키지 않고
선택한 corridor에 따라 `Option`, assertion Defect 또는 상세 `Result`
edge를 만든다. 성공 뒤에만 refined payload와 binding을 commit한다.

미니 사례로 literal `8080`은 Port 범위를 정적으로 증명할 수 있지만
runtime `raw: Int`는 값이 같을 수도 있다는 추측만으로 Port가 되지 않는다.
흔한 오해는 `type Port = Int where ...`가 주석이나 validation helper
별칭이라는 생각이다. Port는 별도 semantic identity이고 conversion
failure를 어느 channel에 둘지 caller가 명시해야 한다.

## 7. 허용·거부·경계 사례

runtime 값에 대해 근거 없이 refinement를 대입할 수 없다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: REFINEMENT_* -->
```deeplus
let raw: Int = 70_000
let port: Port = raw
```

literal과 range가 정적으로 모순이면 `DISPROVED`, runtime 값이라 증명이
없으면 `UNKNOWN`이다. 둘 다 implicit conversion으로 통과시키지 않는다.
반대로 exact literal이 predicate를 정적으로 만족하면 중복 runtime
predicate를 만들지 않고 `PROVED` construction을 사용할 수 있다.

## 8. 다른 기능과의 연결

refinement 성공 payload는 pattern matching과 flow proof에 연결된다.
`def#guard`는 pure total `Bool` callable이지만 현행 API metadata에
refinement-summary owner가 없으므로 호출 자체가 타입을 좁히지 않는다.
MIR lowering도 `as?`, `as!`, `check`의 Option/Defect/Result edge를 서로
바꾸지 않는다.

## 9. Deeplus다운 작성 관례

- local 값은 읽기 쉬울 때 추론하고 public/ownership 경계는 명시한다.
- 범위와 invariant에 이름을 주어 raw primitive와 구분한다.
- 상세 실패가 필요 없으면 `as?`, 필요하면 `T::check`를 쓴다.
- `as!`는 불가능함이 별도 증명된 assertion 경계에 제한한다.
- UNKNOWN proof를 comment나 관례로 덮지 않는다.

## 10. 연습 문제

1. **따라 하기:** `Percentage = Int where this >= 0 and this <= 100`을
   선언하고 `as?` 변환을 작성한다.
2. **빈칸 완성:** `let result: Result<Port, error RefinementError> =
   ___::check(raw)`의 owner를 채운다.
3. **스스로 설계하기:** 상세 오류가 필요한 입력과 필요 없는 입력을
   하나씩 골라 `check`와 `as?`를 배치하고 이유를 적는다.

## 11. 빠른 복습

- inference는 local하며 숨은 refinement proof를 만들지 않는다.
- refinement declaration은 base type과 predicate를 결합한다.
- `as?`, `as!`, `check`는 실패 책임이 서로 다르다.
- UNKNOWN은 허용이 아니라 명시적 proof/검사 요구다.

## 12. 정본 근거와 다음 장

- [타입과 refinement](../../grammar-reference/04-types-generics-and-refinement.md)
- [추론과 변환](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [refinement 계약](../../../spec/contracts/type-refinement-narrowing-coherence.json)

다음은 [Union, intersection, Option과 Result](04-02-union-intersection-option-result.md)에서
여러 대안과 실패 값을 닫힌 타입으로 구성한다.
