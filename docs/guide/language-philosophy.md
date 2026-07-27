# Deeplus 언어 철학

> 문서 역할: 언어 설계의 방향과 선택 기준을 설명하는 안내 문서
>
> 현행 언어 버전: `0.1.2-internal`
>
> 상태 경계: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

Deeplus가 추구하는 바를 한 문장으로 줄이면 다음과 같다.

> **프로그래머의 의도를 쉽고 일관되며 책임 있게 표현하고, 그 의도와
> 어긋나는 프로그램은 가능한 한 이른 단계에 정확한 이유와 함께
> 드러낸다.**

여기서 표현력은 단순히 짧은 문법이나 많은 기능을 뜻하지 않는다.
프로그래머가 값, 타입, 소유권, 실패, 효과, 동시성 및 외부 경계에 관한
의도를 소스에 자연스럽게 남길 수 있어야 하고, 컴파일러와 도구는 그
정보를 추측으로 바꾸지 않고 끝까지 보존해야 한다. Deeplus는 편의와
안전을 대립시키기보다, 책임이 분명한 표현을 사용하기 쉽게 만드는
방향을 택한다.

이 문서는 언어 명세를 대신하지 않는다. 정확한 수용 여부는
[`spec/language.md`](../../spec/language.md), 정확 문법은
[`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf), 타입과
관측 의미는 각각 [`spec/types/type-system.md`](../../spec/types/type-system.md)와
[`spec/mir/semantics.md`](../../spec/mir/semantics.md)를 따른다.

## 1. Deeplus가 해결하려는 문제

큰 프로그램의 결함은 흔히 “문법을 몰라서”보다 서로 다른 층이 같은
의도를 다르게 해석해서 생긴다.

- 호출자는 값을 빌린다고 생각하지만 구현은 소유권을 넘긴다.
- 한 분기는 타입을 좁혔다고 생각하지만 다른 분기나 클로저가 그
  사실을 무효화한다.
- Enum 패턴은 모든 경우를 다뤘다고 보이지만 guard와 residual case가
  빠져 있다.
- 실패가 반환값인지 효과인지 defect인지 불분명하다.
- 동시성 경계를 넘은 값이 공유되는지 복사되는지 이동되는지 모호하다.
- 역할과 변경 주기가 서로 다른 소스 선언 identity, 직렬화 tag,
  runtime discriminant 및 외부 ABI identity를 하나의 식별자로 묶어
  각각 독립적으로 정의하고 변경할 수 없게 한다.
- 설계 문서에 기능이 있다는 사실이 실제 compiler나 runtime이 그
  기능을 지원한다는 주장으로 바뀐다.

Deeplus는 이런 어긋남을 하나의 “마법 같은 자동 추론”으로 덮지 않는다.
대신 각 층의 책임을 분리하고, 층 사이에 전달되어야 할 증거를
명시적으로 모델링한다.

## 2. 핵심 설계 원칙

### 2.1 표현력 우선은 “의도 보존”이다

Deeplus의 **Expressiveness First**는 같은 뜻을 더 짧게 쓰는 것만을
의미하지 않는다. 다음 세 조건을 함께 만족해야 한다.

1. **쉽게** — 자주 쓰는 올바른 표현은 불필요한 의식 없이 작성한다.
2. **일관되게** — 같은 개념은 선언, 타입, 호출 및 관측 단계에서 같은
   규칙을 따른다.
3. **책임 있게** — 소유권, 효과, 실패, 격리 또는 변환 비용을 숨기지
   않는다.

언어가 어떤 표현을 제한해야 한다면 단순히 금지하는 데 그치지 않고,
프로그래머의 원래 의도를 보존하는 대안을 제공해야 한다. 예를 들어
자동으로 의미가 달라지는 변환보다 검사된 명시적 변환을, 공유 가변
상태보다 소유자와 격리 경계가 드러나는 모델을 선호한다.

### 2.2 가능한 오류는 이른 단계에 닫는다

Deeplus의 타입 시스템은 단순한 이름표 모음이 아니다. 타입
리파인먼트, Union과 Intersection, narrowing, `def#guard`, Enum,
패턴 매칭 및 exhaustiveness가 각자 맡은 증거 단계를 분명히 하면서
하나의 정적 판정 과정에 참여한다.

```deeplus
public enum Lookup {
    found(value: Int)
    missing
}

public def describe(result: Lookup) -> String = {
    return @match result {
        ::found(value) if value > 0 => "positive: ${value}"
        ::found(value) => "non-positive: ${value}"
        ::missing => "missing"
    }
}
```

위 `describe`는 명시적 `@match`의 subject로 `result`를 넘기고 inline
guard로 양수인 `found` case를 먼저 처리한다. 같은 함수는 재사용 가능한
guard와 clause-function body를 이용해 다음처럼 쓸 수도 있다.

```deeplus
public def#guard isPositive(value: Int) -> Bool = {
    return value > 0
}

public def describe(result: Lookup) -> String = {{
    ::found(value) if isPositive(value) => "positive: ${value}"
    ::found(value) => "non-positive: ${value}"
    ::missing => "missing"
}}
```

`= {{ ... }}`의 암시적 subject는 단일 매개변수 `result`다. 두 형식
모두 첫 guard가 이미 선택된 `found` case의 일부만 통과시키므로 다음
`found` arm이 residual을 닫고 `missing` arm이 나머지 case를 닫는다.
`def#guard`는 재사용 가능한 pure·total Bool 판정을 정의한다. 검증된
`GuardSummaryV1`이 있는 `isPositive(value)` direct truth-test는 true
edge에 `value > 0`, false edge에 그 보완 fact를 남긴다. 다만 `value`의
선언 타입은 계속 `Int`이고, stored Bool·wrapper·unstable place에서는
이 narrowing을 만들지 않는다. 또한 guard는 이미 선택된 `found` case의
일부만 통과시킬 뿐 structural exhaustiveness cell을 만들지 않는다.
Deeplus는 이처럼 pattern fact, refinement fact와 coverage 증거를
구분하면서 한 정적 오류 검출 체계 안에서 조합한다. 자세한 규칙은
[`def#guard` 직접 호출 narrowing](../grammar-reference/04-types-generics-and-refinement.md#guard-callable-refinement-summary)을
따른다.

### 2.3 값, 이름 및 표현 identity를 분리한다

하나의 대상에는 여러 identity가 있을 수 있다.

- 소스와 의미론이 사용하는 값 또는 명목 identity
- Module과 선언이 사용하는 정적 경로 identity
- 직렬화 형식의 tag
- runtime discriminant
- 메모리 layout과 ABI identity
- Trait conformance와 dispatch가 사용하는 witness identity

이들을 우연히 같은 정수나 문자열로 표현할 수 있다는 이유로 같은
개념으로 취급하지 않는다. 예를 들어 Enum의 `VariantId`는 직렬화 tag나
배치 순서가 아니며, Class의 slot identity는 source order가 아니다.
이 분리는 리팩터링과 독립 컴파일, 직렬화 호환성 및 여러 backend 사이의
일관성을 지키는 기반이다.

### 2.4 소유권은 메모리 기법을 넘어 책임 모델이다

Deeplus의 ownership은 “누가 메모리를 해제하는가”만 답하지 않는다.
누가 값을 변경하고, 이동하고, 격리 경계를 통과시키며, 실패 시 정리를
완료할 책임이 있는지도 함께 표현한다.

```deeplus
let handle = open(path)
defer handle ~ close

let bytes = handle ~ readAll
process(bytes)
```

`inout`, move, borrow, consume, cleanup 및 transactional commit은 각자
다른 책임을 가진다. 위 `defer`는 block이 아니라 정확히 한 cleanup
invocation을 등록하며, 정상 반환뿐 아니라 실패와 취소 경로에서도
결정적인 LIFO 책임을 지킨다. 성공 경로뿐 아니라 부분 초기화, 실패,
취소 및 unwind 경로에서도 값과 자원의 책임이 사라지지 않아야 한다.

### 2.5 실패·효과·defect를 한 바구니에 넣지 않는다

복구 가능한 domain 실패, 호출 계약에 드러나는 effect, 프로그래머
오류나 깨진 불변식에서 발생하는 defect는 서로 다른 책임을 가진다.
Deeplus는 모든 실패를 sentinel 값이나 숨은 전역 예외 통로로 축약하지
않는다.

- 예상 가능한 부재에는 `Option`을 사용한다.
- domain 결과에는 `Result` 또는 명시된 error/effect 계약을 사용한다.
- 정적으로 판정할 수 있는 위반은 진단으로 거부한다.
- 실행 중 깨진 비복구 불변식은 결정적인 defect 경계를 따른다.
- cleanup은 성공 여부와 관계없이 소유권 법칙을 지킨다.

이 구분 덕분에 호출자는 무엇을 처리해야 하는지 알고, optimizer와
runtime은 소스가 약속하지 않은 실패 통로를 발명하지 않는다.

### 2.6 동시성의 기본 단위는 격리된 책임이다

Deeplus는 actor, task, structured concurrency와 cancellation을 별개의
부가 기능으로 보지 않는다. 이들은 ownership과 effect를 시간 및
동시성 축으로 확장한다.

```deeplus
public protocol CounterProtocol {
    send add(value: Int)
    request current() -> Int
}

public actor Counter {
    on add(value: Int) = { }
    request current() -> Int = { return 0 }
}

counter :~ add value: 3
let admission = counter :~ current
```

Actor의 상태는 actor가 소유한다. 메시지와 격리 경계를 넘는 값은
정해진 전달 규칙을 따라야 하며, 외부 코드가 내부 가변 상태의 참조를
몰래 보유해서는 안 된다. 자식 task의 수명과 취소도 구조적 scope 밖으로
무책임하게 새지 않아야 한다.

### 2.7 정확성이 필요한 영역은 정확한 모델을 제공한다

Deeplus는 하나의 수 표현으로 모든 계산을 해결하려 하지 않는다.
고정 폭 정수, 부동소수, `Rational`, `Complex`, 단위와 수치 배열은 서로
다른 법칙과 사용 목적을 가진다.

```deeplus
let ratio: Rational = <2/3>
let impedance: Complex = 3.0 + 4.0i
let first = samples[1]
let window = samples[2..5]
```

`Rational`의 값 정규화, IEEE 부동소수 동작과 NaN의 순서 제약,
Complex 성분 타입, 1부터 시작하는 인덱싱 및 slice 경계는 편의상
암묵적으로 섞이지 않는다. 수학적 identity와 backend layout 또는 외부
ABI도 분리한다.

### 2.8 문법은 추측보다 소유자를 갖는다

같은 glyph가 여러 역할을 가질 수는 있지만, 그 역할은 문맥의 문법
owner가 결정해야 한다. type checker가 토큰화를 되돌리거나 formatter가
의미를 재추측하는 구조를 피한다.

Package와 Module도 분리한다. Package는 배포·의존성·빌드·artifact
provenance의 단위이고, Module은 namespace·가시성·정적 이름 해석·소스
구성의 단위다. Module 계층은 파일시스템 계층과 같을 수도 있지만 언어
identity상 같아야 하는 것은 아니다.

### 2.9 Trait 적합성은 증거이며 숨은 검색이 아니다

Trait requirement와 conformance는 type checker가 닫아 전달하는
증거다. 호출·generic specialization·lowering·runtime dispatch가 각자
다른 규칙으로 적합성을 다시 검색해서는 안 된다.

fixed-glyph operator overloading도 이 원칙을 따른다. Deeplus가 정한
연산자 glyph와 Trait 계약은 사용할 수 있지만, 사용자가 새로운 임의
operator glyph나 우선순위를 발명하는 방식은 허용하지 않는다. 이는
소스의 지역적 기교보다 읽기 가능성, parser 결정성, 도구 일관성과
library 간 조합 가능성을 우선한 선택이다.

### 2.10 Source에서 backend까지 결정은 한 번만 내린다

Frontend가 수용한 프로그램은 AST/HIR에서 정적 결정을 닫고, MIR은 그
결정을 관측 가능한 실행 계약으로 옮긴다. xVM, LLVM AOT 및 LLVM ORC
JIT 같은 backend가 언어 의미를 제각기 재해석해서는 안 된다.

이 원칙은 아직 모든 제품 구현이 존재한다는 주장이 아니다. 오히려
제품 구현이 생길 때 무엇을 동일하게 보존해야 하는지를 미리 고정한다.
언어 설계가 `Stable`인 것과 특정 compiler/backend가 실행 증거를 가진
것은 별도의 상태다.

### 2.11 진단과 도구는 언어 경험의 일부다

거부는 단순한 실패가 아니다. 좋은 진단은 다음을 알려야 한다.

- 어느 규칙이 깨졌는가
- 책임 있는 source span은 어디인가
- 어떤 타입·소유권·effect 또는 상태 증거가 부족한가
- 의미를 보존하는 안전한 수정이 있는가
- 자동 수정이 오히려 의미를 바꿀 수 있어 제공되지 않는가

Recovery 문법은 후속 진단과 편집 경험을 위한 것이며, 유효한
AST/HIR/MIR 잔여물을 만드는 우회로가 아니다. Formatter와 LSP도 문법
owner와 semantic identity를 보존해야 한다.

### 2.12 진화는 상태와 증거를 통해 이루어진다

Deeplus는 새로운 아이디어를 문서에 썼다는 이유만으로 현행 언어에
포함하지 않는다.

| 상태 | 의미 |
|---|---|
| `CURRENT` / `STABLE_DESIGN` | 현행 언어 설계에 수용됨 |
| `PREVIEW` | 명시적 source gate 아래 제한적으로 수용됨 |
| `PREVIEW_DESIGN` | 검토 가능한 설계이지만 source에서 활성화할 수 없음 |
| `RECOVERY_ONLY` | 오류 복구와 진단에만 사용되며 유효 프로그램을 만들지 않음 |
| `REMOVED` | 현행 표면이 아니며 필요하면 migration 진단만 제공 |
| `PRODUCT_NOT_RUN` | target-bound compiler/runtime/tool 실행 증거가 없음 |

기능의 존재, 설계의 안정성, 구현의 존재, 독립 적합성 검증 및 제품
지원은 서로 다른 주장이다. 이 구분은 느슨함이 아니라 증거를 과장하지
않기 위한 설계 규율이다.

## 3. Deeplus의 특장점

### 3.1 기능의 수보다 기능 사이의 결합을 설계한다

Deeplus의 차별점은 Union, Enum, pattern matching, ownership, actor 또는
Trait 중 하나만 따로 갖는 데 있지 않다. 이 기능들이 같은 identity와
증거 모델을 사용하도록 결합한다는 데 있다.

- refinement와 guard의 증거가 narrowing과 match 분석으로 이어진다.
- Enum payload와 pattern place가 ownership·move·cleanup 규칙을 따른다.
- Trait witness가 generic 호출에서 HIR, MIR, backend dispatch까지
  보존된다.
- actor isolation이 ownership과 effect 체계에 연결된다.
- diagnostic registry가 문법·타입 predicate·예제와 결합된다.

이 결합은 초기 학습량을 늘릴 수 있지만, 프로그램이 커질수록 각 기능의
예외 규칙을 따로 외우는 부담을 줄이는 것을 목표로 한다.

### 3.2 읽는 사람과 도구가 같은 결론에 도달하도록 한다

소스 순서, 우연한 파일 배치, hash iteration order 또는 backend 선택이
이름 해석과 적합성 결론을 바꾸지 않아야 한다. ambiguity는 정해진
규칙에 따라 terminal이며, 낮은 우선순위 후보를 몰래 fallback으로
선택하지 않는다.

이 결정성은 재현 가능한 build만을 위한 것이 아니다. 코드 리뷰,
diagnostic snapshot, formatter, LSP navigation, incremental compilation
및 독립 conformance test가 같은 언어를 관측하기 위한 조건이다.

### 3.3 현재와 미래를 같은 문서에서 보되 섞지 않는다

Deeplus 문서는 현행 기능과 Preview Design을 함께 보여 준다. 독자는
언어가 향하는 방향을 검토할 수 있지만, 예제에는 상태 fence가 붙고
비활성 설계가 current source로 오해되지 않도록 한다.

이는 “미래 기능을 숨기지 않는 개방성”과 “아직 없는 기능을 있다고
말하지 않는 정직성”을 함께 지키려는 선택이다.

### 3.4 정적 안전성과 수치·시스템·동시성 표현을 한 언어에서 다룬다

Deeplus는 domain modeling만을 위한 언어도, 저수준 제어만을 위한
언어도 아니다. 다음 영역이 같은 타입·소유권·효과 체계 안에서
상호작용하도록 설계한다.

- 정확 수와 부동소수, 복소수, 단위 및 수치 배열
- Class, Enum, Record, Schema와 pattern matching
- generic, Trait, associated type 및 fixed operator conformance
- 명시적 ownership, borrow, move, cleanup과 unsafe 격리
- async/task/actor와 structured cancellation
- Module·Package·독립 컴파일 identity
- HIR-H1, MIR, xVM 및 LLVM backend 경계

## 4. Deeplus가 지원하는 것

아래의 “지원”은 먼저 **현행 언어 설계가 해당 개념을 정의한다**는
뜻이다. 실제 제품 지원은 별도 target-bound receipt가 있을 때만
주장한다.

### 4.1 현행 설계가 정의하는 주요 영역

| 영역 | 현행 설계의 방향 |
|---|---|
| 값과 리터럴 | 명확한 값 domain, exact integer, IEEE float, `Rational`, `Complex`, String, Bytes |
| 이름과 구성 | Unicode identifier, 정적 한정 경로, Package와 Module의 분리 |
| 함수형 표현 | 함수·메서드·메시지 호출, label/rest/unfold, closure와 capture |
| 타입 | 추론, generic, Union·Intersection, refinement, narrowing, callable/effect identity |
| 데이터 모델링 | Class, Enum, Record, tuple, map, Schema, Bitfield, unit/measure |
| 분기와 패턴 | 구조 분해, pattern matching, guard, exhaustiveness와 reachability |
| 추상화 | Trait requirement, 명시적 conformance, associated type, extension |
| 연산자 | 닫힌 fixed-glyph 집합과 Trait 기반 적합성·overloading |
| 책임 | ownership, borrow, move, consume, cleanup, transaction |
| 실패 | `Option`, `Result`, error/effect, contract/law, defect의 분리 |
| 컬렉션 | 1-based indexing, slicing, comprehension, generator, NumericArray |
| 동시성 | async/await, structured task, cancellation, actor와 mailbox 격리 |
| 시스템 경계 | provider/Prelude, FFI, unsafe 격리, serialization identity 분리 |
| 컴파일 계약 | CST/AST, HIR-H1, MIR 및 다중 backend가 지켜야 할 의미 경계 |
| 언어 진화 | Current, Preview, Preview Design, Recovery, Removed 상태 fence |

주제별 정확한 설명과 예제는
[`docs/grammar-reference/`](../grammar-reference/README.md), 학습 순서는
[`docs/tutorial/`](../tutorial/README.md)에서 찾을 수 있다.

### 4.2 Preview와 Preview Design

Preview는 gate가 있는 시험적 source surface다. Preview Design은 미래
후보를 구체적으로 검토하기 위한 비활성 설계다. 둘 다 문서화하고
예시를 제공할 수 있지만, Preview Design 예제는 현행 프로그램으로
컴파일할 수 있다는 뜻이 아니다.

이 구분을 통해 Deeplus는 장기 방향을 논의하면서도 current 문법과
도구 계약을 안정적으로 유지한다.

## 5. Deeplus가 지원하지 않는 것

“지원하지 않는다”에는 세 가지 서로 다른 이유가 있다. 영구적인 설계
선택, 아직 활성화하지 않은 후보, 실행 증거가 없는 제품 상태를
구분해야 한다.

### 5.1 의도적으로 현행 표면에 두지 않는 것

- **`null` 값** — 부재는 `Option`, 결과는 `Result` 등 책임이 드러나는
  타입으로 표현한다. `null` 철자는 recovery 진단 대상일 뿐이다.
- **임의 custom operator glyph와 사용자 정의 우선순위** — 정해진
  fixed-glyph와 Trait 계약만 사용한다.
- **기본 0-based indexing** — Deeplus sequence의 첫 source index는
  `1`이다. 외부 0-based API와의 변환은 경계에서 명시한다.
- **숨은 의미 변환** — 손실 가능 numeric conversion, Enum migration,
  marker rewrite나 ABI mapping을 universal default로 자동 선택하지
  않는다.
- **Package와 Module의 동일시** — 배포 단위와 namespace 단위를 하나의
  source 경로 규칙으로 강제하지 않는다.
- **파일 경로를 Module identity로 강제** — project convention은 매핑을
  제공할 수 있지만 파일시스템 자체가 언어 identity는 아니다.
- **의미 identity와 storage/serialization/ABI identity의 혼합** —
  별도 mapping 계약 없이 같다고 간주하지 않는다.
- **공유 가변 상태를 기본 동시성 모델로 삼는 것** — actor와 소유권,
  격리 및 명시적 unsafe 경계를 우선한다.
- **runtime에서 Trait 적합성을 무제한 재검색하는 것** — 정적 단계에서
  닫힌 witness와 dispatch evidence를 전달한다.
- **Recovery syntax를 유효 프로그램으로 승격하는 것** — recovery
  residue는 진단을 돕지만 admitted semantic node를 만들지 않는다.

### 5.2 설계 후보는 있으나 아직 활성화하지 않은 것

Preview Design에 기록된 surface와 semantics는 검토 대상이지 current
지원이 아니다. 예를 들어 별도 activation gate, OPEN P1 또는 target
evidence가 요구되는 설계는 문서가 존재해도 사용할 수 없다.

특정 후보의 정확한 상태는
[`docs/grammar-reference/15-preview-recovery-and-removed-surfaces.md`](../grammar-reference/15-preview-recovery-and-removed-surfaces.md)와
Preview Design 세 장에서 확인한다. “좋은 아이디어”와 “현행 언어”의
차이는 명시적 authority와 acceptance evidence가 메운다.

### 5.3 아직 제품 지원을 주장하지 않는 것

현재 저장소에는 설계·schema·validator·Rust 골격이 있지만, 이것만으로
다음을 지원한다고 주장하지 않는다.

- 완전한 source-to-parser 제품
- 통합 type checker와 HIR lowering
- 실행 가능한 Deeplus MIR 및 xVM
- LLVM AOT 또는 ORC JIT 적합성
- formatter와 LSP의 제품 수준 동작
- stdlib/provider runner의 완전한 실행
- backend 간 conformance
- 실제 사용자·팀 사용성 검증

이 항목들은 언어의 목표나 설계가 없다는 뜻이 아니라, 독립적인
target-bound 실행 증거가 아직 없다는 뜻이다. 현행 정확 상태는
[`current/current-pointer.json`](../../current/current-pointer.json)의
product lane을 따른다.

## 6. 설계 선택을 평가하는 질문

새 문법이나 기능을 Deeplus에 넣을 때에는 “가능한가”보다 다음 질문을
먼저 묻는다.

1. 프로그래머의 어떤 의도를 더 잘 표현하는가?
2. 그 의도가 타입·소유권·효과·실패·격리 경계에 보존되는가?
3. 올바른 흔한 경우가 쉬운가?
4. 잘못된 경우를 더 이르고 정확하게 발견할 수 있는가?
5. Source, AST/HIR, MIR, runtime 및 tooling이 같은 결론을 내리는가?
6. 결정이 source order, file layout 또는 backend 우연성에 의존하지
   않는가?
7. 다른 기능과 결합할 때 별도의 예외 규칙이 폭증하지 않는가?
8. 제한이 필요하다면 의도를 보존하는 대안이 있는가?
9. migration과 자동 수정이 의미를 바꾸지 않는가?
10. 설계 수용과 제품 실행 증거를 정직하게 분리할 수 있는가?

이 질문에 답하지 못하는 기능은 편리해 보여도 더 다듬어야 한다.
반대로 문법이 조금 더 명시적이더라도 책임과 의미를 명확히 하고 도구가
신뢰할 수 있다면 Deeplus다운 선택일 수 있다.

## 7. Deeplus다운 프로그램

Deeplus다운 코드는 특정 formatting 취향보다 다음 특성을 가진다.

- domain 상태를 sentinel이나 주석 대신 타입과 Enum으로 표현한다.
- guard와 pattern을 이용해 타입 증거가 생기는 지점을 드러낸다.
- 값의 owner와 mutation 권한을 읽을 수 있다.
- 실패 가능성과 effect가 호출 계약에 나타난다.
- async 작업과 actor 메시지가 구조적 수명 및 격리 경계를 따른다.
- exact numeric과 floating approximation을 의도에 맞게 선택한다.
- 외부 ABI, serialization, provider 및 unsafe 경계를 작은 영역에
  격리한다.
- 현재 기능과 Preview Design을 같은 코드에서 무심코 섞지 않는다.

좋은 Deeplus 프로그램은 “컴파일러를 설득하기 위해 장황한 코드”도,
“많은 것을 추측하게 하는 짧은 코드”도 목표로 하지 않는다. 사람이
읽은 의도와 도구가 검증한 의도가 가능한 한 같은 프로그램을 목표로
한다.

## 8. 맺음말

Deeplus는 표현력, 정적 오류 검출, 책임 있는 자원 관리, 결정적 의미론과
정직한 증거 경계를 함께 추구한다. 이 가치들은 서로 경쟁하는 체크리스트가
아니라 하나의 언어 경험을 이룬다.

프로그래머에게는 복잡한 문제를 자연스럽게 표현할 수 있는 도구를,
코드 리뷰어에게는 의도와 책임을 읽을 수 있는 소스를, 구현자에게는
재추측 없이 전달할 수 있는 정적 결정을, 사용자에게는 실제로 검증된
범위만을 약속하는 언어를 제공하는 것이 Deeplus의 방향이다.
