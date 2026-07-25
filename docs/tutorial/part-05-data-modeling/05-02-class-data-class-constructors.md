# 5.2 Class, data class, constructor

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

## 1. 상태와 읽는 법

Class, data class, `def!` constructor와 generated data-class
materialization은 현행 설계다. “생성할 수 있다”와 “제품 runtime에서
검증되었다”는 다른 주장이다. 이 장은 전자만 설명한다.

## 2. 학습 목표

- Class가 nominal identity와 construction responsibility를 갖는 이유를
  이해한다.
- concrete Class가 기본적으로 final임을 기억한다.
- ordinary constructor, named constructor, data-class promoted field를 쓴다.
- constructor `Type!(...)`와 materialization `Type${...}`를 구별한다.

## 3. 선수 지식

Record/schema label, visibility `public/common/private`, member visibility
`+/-/#`의 차이를 알고 있어야 한다.

## 4. 문제에서 출발하기

사용자 ID는 단순한 `Int`처럼 보이지만 아무 정수나 들어오면 안 되고
다른 ID와 섞여서도 안 된다. 명목 Class는 “필드 모양이 같다”는 이유로
다른 타입과 같아지지 않는다. 생성자는 검증과 owner publish의 한 경계를
제공한다.

## 5. 핵심 모델

ordinary Class는 body가 필요하고 concrete Class는 modifier가 없으면
final이다. `open`, `abstract`, `sealed`, `abstract sealed`는 상속과 family
경계를 명시한다. `value`와 `resource` flavor는 책임 profile이지
equality, clone, display 또는 conformance 자동 합성이 아니다.

constructor는 `def! name`으로 선언한다.

- 기본 외부 호출: `Type!(...)`
- 이름 있는 외부 호출: `Type!name(...)`
- 같은 construction session delegation: `name(...)`
- 부모 delegation: `super!name?(...)`

data class의 primary parameter에 `+let`, `-let`, `#var`처럼 storage keyword와
visibility를 붙이면 promoted field가 된다. eligible final data class는
label materialization을 제공할 수 있지만 모든 data class에 자동으로
허용되는 것은 아니다.

## 6. 단계별 예제

### 깊이 읽기: construction session과 명목 identity

Class를 field가 붙은 Record로만 이해하면 constructor와 lifecycle의
책임을 놓친다. Class 값에는 명목 owner가 있고 생성 과정은 storage
확보, argument 평가, delegation, field 초기화, postcondition 확인,
publish를 거치는 하나의 construction session이다. 호출자는 완성된
값만 관찰해야 하며 초기화 중인 `self`가 callback이나 registry로
빠져나가면 이 불변식이 깨진다.

판정은 선언 flavor와 상속 경계를 확인하는 데서 시작한다. 선택된
constructor identity와 argument label을 결정하고 argument를 source
order로 한 번씩 평가한다. base delegation과 stored field의 초기화
책임을 검사한 뒤 모든 단계가 성공한 경우에만 LIVE 값을 publish한다.
실패하면 이미 획득한 resource를 역순으로 정리한다.

두 번째 field validator가 실패하는 작은 trace를 생각해 보자. 첫 field가
resource owner여도 construction session이 그 owner를 정리하며 caller는
반쪽 객체를 받지 않는다. 성공 trace의 publication count는 하나이고
실패 trace는 영이다. 먼저 global registry에 객체를 넣고 실패하면
지우는 구현은 잠깐이라도 미완성 identity를 노출하므로 허용되지 않는다.

data class도 이 규칙을 우회하는 특별한 Record가 아니다. 합성 가능한
constructor나 비교 기능은 exact profile이 만족될 때만 생기며 field의
ownership·visibility·cleanup은 남는다. “data이므로 serialization과
모든 conformance가 자동 생성된다”는 흔한 오해다. 각 기능은 별도
계약과 authority를 확인해야 한다.

### 6.1 검증된 명목 값 만들기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public class UserId {
    +let raw: Int

    +def! new(raw: Int)
        : super!()
    = {
        self.raw = raw
    }

    +def value.() -> Int
        throws Never
        effects {}
    = {
        return self.raw
    }
}

let id = UserId!(13)
```

앞의 `+`는 공개 visibility이고 `value.`의 `.`은 final dispatch slot이다.
constructor는 argument를 한 번 평가하고 storage 초기화가 모두 성공한
뒤 owner를 publish한다.

### 6.2 data class의 promoted field

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public data class UserProfile(
    +let name: String,
    +let age: Int,
    -let passwordHash: PasswordHash,
)

let profile = UserProfile!(
    name: "Ada"
    age: 36
    passwordHash: PasswordHash::fromSecret(secret)
)
```

`+let name`은 public immutable field, `-let passwordHash`는 declaring
boundary 밖에서 보이지 않는 field다. all-named layout call에서는 줄바꿈이
separator가 된다.

### 6.3 eligible data-class materialization과 derivation

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public data class Point(+let x: Int, +let y: Int)

let point = Point${ x: 3, y: 4 }
let moved = point!{ x: 8 }
```

`Point${...}`는 generated ConstructionRow 자격을 만족한 data class의
typed materialization이다. `point!{...}`는 같은 명목 타입의 shallow
derivation이다. ordinary Class constructor를 `${}`로 부르는 일반 규칙은
없다.

## 7. 허용·거부·경계 사례

허용:

- body가 있는 ordinary Class
- body를 생략할 수 있는 data class
- `Type!name(...)` named constructor
- eligible final data class의 `Type${...}`

거부 예제:

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: CLASS_BODY_REQUIRED; product: NOT_RUN -->
```deeplus
public class Point(x: Int, y: Int)
// CLASS_BODY_REQUIRED
```

<!-- deeplus-example: illustrative; surface: CURRENT; expected: REJECT; diagnostic: DATA_CLASS_MATERIALIZATION_PROFILE_NOT_SATISFIED; product: NOT_RUN -->
```deeplus
public data class Session(+var handle: Handle)
let session = Session${ handle: openHandle() }
// DATA_CLASS_MATERIALIZATION_PROFILE_NOT_SATISFIED
```

mutable handle과 lifecycle 책임은 자동 ConstructionRow의 닫힌 profile을
만족하지 않는다. structural shape만 같다는 이유로 constructor나
conformance를 합성할 수도 없다.

## 8. 다른 기능과의 연결

- Class method marker와 Trait witness marker는 같은 glyph라도 identity
  domain이 다르다.
- sealed family closure는 subtype 분석에 쓰이지만 Class constructor
  Pattern을 만들지 않는다.
- resource Class의 cleanup owner는 move를 따라간다.
- schema materialization은 ordinary constructor를 우회하지 않는다.

## 9. Deeplus다운 작성 관례

- 상속을 의도하지 않으면 기본 final을 그대로 둔다.
- 생성 검증과 표현 공개를 constructor owner 한 곳에 모은다.
- data class는 “짧게 쓰는 Class”가 아니라 닫힌 data responsibility에
  사용한다.
- private construction authority가 필요한 helper는 nominal `def::`로
  소유자를 분명히 한다.
- `${}`와 `!()`를 시각적 취향으로 교환하지 않는다.

## 10. 연습 문제

1. **복사:** `UserId`를 복사해 `OrderId`를 만들고 기본 constructor를
   호출하라.
2. **빈칸 완성:** `Point${ x: x, y: y, label: ___ }`와
   `point!{ label: ___ }`의 두 빈칸을 문자열로 채워 materialization과
   shallow derivation을 완성하라.
3. **설계:** 파일 handle을 가진 `Session`을 data class로 둘 수 없는
   이유를 owner·cleanup·failure commit 관점에서 설명하고 resource Class
   경계를 제안하라.

## 11. 빠른 복습

- concrete Class는 기본 final이다.
- Class는 nominal identity와 construction responsibility를 소유한다.
- `def!`는 constructor, `Type!name`은 named constructor 호출이다.
- 일부 eligible data class만 generated materialization을 갖는다.
- sealed Class는 자동 constructor Pattern을 만들지 않는다.

## 12. 정본 근거와 다음 장

- [언어 명세의 Class 계약](../../../spec/language.md)
- [Class 문법](../../../spec/grammar/deeplus.ebnf)
- [Class·Trait 레퍼런스](../../grammar-reference/06-classes-traits-conformance-and-extensions.md)
- [통합 예제](../../grammar-reference/24-integrated-worked-examples.md)

다음 장에서는 가능한 상태를 명목적으로 닫는 현행 Enum을 배운다.
