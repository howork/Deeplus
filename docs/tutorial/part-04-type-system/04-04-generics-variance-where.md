# 04-04. generic, variance와 `where`

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 generic parameter kind, invariant 기본값, Trait 전용 variance와
`where` obligation을 설명한다.

## 2. 학습 목표

- type parameter와 type argument를 구분한다.
- invariant 기본값과 Trait의 `out`/`in` 위치 검사를 설명한다.
- `where T conforms Trait` 의무를 함수 body와 caller에 연결한다.
- type, `StaticInt`, `EffectRow`, `ErrorSet` kind를 구분한다.

## 3. 선수 지식

앞 장의 명시적 type identity와 Part 3의 함수 서명을 읽을 수 있어야 한다.

### 미리 보는 최소 모델과 후속 심화

Trait는 여러 타입이 만족할 수 있는 named requirement contract이고,
conformance는 특정 target이 그 contract를 어떤 구현과 witness로
만족하는지 명시하는 declaration이라는 최소 정의만 먼저 쓴다.
`where T conforms Display`는 generic body가 Display requirement를
사용하기 위해 caller가 증거를 제공해야 한다는 뜻이다. Trait member,
coherence, witness 선택과 associated type은 Part 6에서 심화한다.
따라서 Trait 경험을 선수 조건으로 요구하지 않는다.

## 4. 문제에서 출발하기

어떤 `T`든 받는 함수가 body에서 `display`를 호출한다면 실제로는 “모든
T”가 아니다. 필요한 witness 의무를 서명에 쓰지 않으면 구현이 숨은
provider를 찾게 된다. 또 `Box<Dog>`를 자동으로 `Box<Animal>`로 바꾸면
mutable 위치에서 soundness가 깨진다. Deeplus는 기본 invariant와 명시적
Trait obligation을 사용한다.

## 5. 핵심 모델

- `<T>`에서 `T`는 기본적으로 kind `type`이다.
- `N: StaticInt`, `ρ: EffectRow`, `E: ErrorSet`은 서로 다른 kind다.
- generic constructor는 기본 invariant다.
- `out`과 `in`은 현행 admitted Trait type parameter에서만 쓴다.
- `out T`는 생산 위치, `in T`는 소비 위치 규칙을 통과해야 한다.
- Class owner의 variance declaration은 현행 surface가 아니다.
- `where T conforms Display`는 선택 가능한 witness obligation을 만든다.
- associated projection은 `<I as Iterator>::Item`처럼 Trait 문맥을
  명시한다.

## 6. 단계별 예제

generic function이 사용하는 능력을 `where`에 적는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def render<T>(value: T) -> String
    throws Never
    effects {}
    where T conforms Display
= {
    return value ~ display
}

public def#pure identity<T>(value: T) -> T
    throws Never
    effects {}
= {
    return value
}
```

`identity`에는 추가 Trait가 필요 없지만 `render`는 Display witness가
필요하다. checker가 ambient reflection으로 witness를 발명하지 않는다.

Trait owner에서는 방향 variance를 선언할 수 있다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public trait Source<out T> {
    +def next+() -> Option<T>
        throws Never
        effects {}
}

public trait Sink<in T> {
    +def accept+(value: T) -> Unit
        throws Never
        effects {}
}
```

Source는 T를 생산하고 Sink는 T를 소비한다. 실제 member 전체가 선언
방향과 일치해야 한다.

### 판정 trace, 미니 사례와 흔한 오해

generic declaration은 parameter 이름마다 kind를 먼저 확정한다. type
parameter는 기본 invariant이고, `out`/`in`이 있으면 owner가 admitted
Trait인지와 모든 생산·소비 위치를 검사한다. body가 requirement를
사용하면 `where` obligation과 선택 가능한 witness를 확인한다. call
지점에서는 argument로 substitution을 만들고, obligation이 닫힌 뒤에만
body와 return type을 instantiate한다.

미니 사례로 read-only `Source<out T>`는 T를 생산하지만 mutable
`Box<T>`는 읽기와 쓰기를 모두 가질 수 있어 invariant가 안전하다.
흔한 오해는 `Dog`가 `Animal`과 관련되면 모든 `Container<Dog>`도 자동으로
`Container<Animal>`이 된다는 생각이다. variance는 이름 관계가 아니라
owner와 모든 member position이 증명하는 제한된 계약이다.

재사용 가능한 알고리즘이 실제로 요구하는 operation이 있을 때만
`where`를 추가한다. 단순 저장·반환 함수에 불필요한 Display나 Order
obligation을 붙이면 caller가 제공해야 할 witness만 늘고 generic
재사용 범위가 줄어든다.

## 7. 허용·거부·경계 사례

variance owner와 위치 검사를 어기면 거부한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: GENERIC_VARIANCE_* -->
```deeplus
public class InvalidBox<out T> {
    +let value: T
}

public trait BadSource<out T> {
    +def put+(value: T) -> Unit
        throws Never
        effects {}
}
```

첫 선언은 Class owner에 variance를 붙였고, 두 번째는 covariant T를
소비 위치에 사용했다. `MutableList<Dog>`를 `MutableList<Animal>`로
암묵 대입하는 것도 invariant 기본값에 어긋난다.

## 8. 다른 기능과의 연결

`where` obligation은 explicit conformance와 witness channel, overload
선택, API digest에 연결된다. `E: ErrorSet`은 generic declaration의 kind
표기이고 `Result<T, error E>`의 `error`는 use-site role 표지다.
`StaticInt`는 NumericArray shape 같은 compile-time identity를 보존한다.

## 9. Deeplus다운 작성 관례

- body가 요구하는 최소 Trait obligation만 `where`에 적는다.
- 기본 invariant를 먼저 사용하고 variance는 실제 producer/consumer
  Trait에만 제한한다.
- kind를 ordinary type으로 뭉개지 않는다.
- associated type은 projection owner Trait를 명시한다.
- 숨은 global provider 대신 conformance/witness 책임을 API에 드러낸다.

## 10. 연습 문제

1. **따라 하기:** `T conforms Display`를 요구하는 generic formatter
   서명을 작성한다.
2. **빈칸 완성:** `public trait Consumer<___ T>`에서 T가 오직 parameter로
   소비될 때의 variance marker를 채운다.
3. **스스로 설계하기:** invariant container와 covariant read-only Trait를
   각각 설계하고, 왜 owner가 달라야 하는지 설명한다.

## 11. 빠른 복습

- generic은 기본 invariant다.
- variance는 현행 Trait owner와 위치 검사에 한정된다.
- `where`는 body가 쓸 conformance 책임을 명시한다.
- type, static integer, effect row, error set은 서로 다른 kind다.

## 12. 정본 근거와 다음 장

- [generic과 variance](../../grammar-reference/04-types-generics-and-refinement.md)
- [generic resolution](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [Trait와 conformance](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)

다음은 [callable identity, effect와 cancellation](04-05-callable-identity-effects-cancellation.md)에서
함수 타입이 보존해야 할 책임을 정리한다.
