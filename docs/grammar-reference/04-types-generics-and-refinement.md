# 타입, 제네릭, 리파인먼트

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 Deeplus `0.1.2-internal`의 현행 타입 문법과 정적 의미를
읽기 쉽게 투영한다. 정확한 구문은 EBNF, 타입 판정은 타입 시스템과
checker predicate가 소유한다. 이 문서가 새 타입, 암시적 변환, 런타임
타입 검사 또는 제품 지원을 만들지는 않는다.

| 표면 | 현행 상태 |
|---|---|
| 명목 타입, generic, 함수/tuple 타입, optional, closed Union, contract intersection | `CURRENT` |
| `any Trait`, `some Trait`, 명시적 associated projection | `CURRENT` |
| `Facet<borrow any Trait ...>`와 borrow Facet 포장 | `CURRENT` |
| refinement `where`, 정적 정수 범위 alias, `as?`, `as!`, `T::check` | `CURRENT` |
| closed Union을 대상으로 한 정확한 typed-pattern narrowing | `CURRENT` |
| closed Union exact-alternative `is`/`!is` | `CURRENT`, 일반 런타임 타입 검사는 현행 아님 |
| owned/inout Facet, 동적 Trait 상태, first-class/local Witness, solver 기반 일반 refinement | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 제품 parser/checker/MIR/runtime/formatter/LSP | `NOT_RUN` |

현행 product lane은 모두 `NOT_RUN`이다. 이 장의 예제는 검토 corpus의
정적 설계 증거이며 실행 영수증이 아니다. 현행 OPEN P1을 폐쇄하거나
새 P1을 만들지 않는다.

## 문법

### 타입 참조와 Pratt 타입 문법

```ebnf
TypeRef            ::= PrattType
NonFunctionTypeRef ::= PrattNonFunctionType

TypePrimary ::= QualifiedTypeReference
              | FacetType
              | ParenTypeSyntax
              | SharpShapeType
              | ExistentialType
              | OpaqueType
              | TypeofType
              | AssociatedProjection

TypePrefixParselet  ::= OwnershipQualifier
TypePostfixParselet ::= "?"
TypeInfixOperator   ::= "&" | "|"
```

`?`는 바로 앞 타입에 optional 한 층을 붙인다. `|`는 명시적 closed
Union, `&`는 모든 구성 의무를 함께 만족해야 하는 contract intersection을
만든다. 복합 타입에서 의도를 명확히 하려면 괄호를 사용한다. 함수 반환
위치는 기본적으로 `NonFunctionTypeRef`이므로 함수 타입을 반환할 때는
함수 타입 전체를 괄호로 감싼다.

### 이름, generic 매개변수와 인수

```ebnf
QualifiedTypeReference ::= QualifiedPath TypeArgumentList?
QualifiedPath          ::= Identifier ("::" Identifier)*

TypeParameterList ::= "<" TypeParameter ("," TypeParameter)* ","? ">"
TypeParameter     ::= VarianceMarker? Identifier TypeParameterKindAnnotation?
VarianceMarker    ::= "out" | "in"

TypeParameterKind ::= "type" | "StaticInt" | "EffectRow" | "ErrorSet"

TypeArgumentList  ::= "<" TypeArgument ("," TypeArgument)* ","? ">"
TypeArgument      ::= TypeRef | StaticIntLiteral | ErrorTypeArgument
ErrorTypeArgument ::= "error" TypeRef
```

종류 annotation을 생략한 매개변수는 타입 매개변수이다. `Result`의
사용 지점은 오류 채널을 반드시 `Result<T, error E>`처럼 표시한다.
generic 선언 자체에서 `E: ErrorSet`을 결합할 때는 `error` 역할 표지를
반복하지 않는다.

기본 generic constructor는 invariant이다. `out`과 `in`은 현재 허용된
Trait 타입 매개변수 위치에서만 사용할 수 있으며, 생산/소비 위치
검사를 통과해야 한다. Class 소유자가 variance를 선언하는 표면은
현행에 들어오지 않는다.

### tuple, parenthesized type와 함수 타입

```ebnf
ParenTypeSyntax   ::= HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?
ParenTypeItemList ::= ParenTypeItem ("," ParenTypeItem)* ","?
ParenTypeItem     ::= TypeRef | TypeRef "..." | TypeRef "***"
FunctionTypeTail  ::= "->" NonFunctionTypeRef ThrowsClause? EffectsClause?
```

- `(T)`는 괄호 타입이다.
- `(T,)`와 `(T, U)`는 tuple 타입이다.
- `(T) -> U throws E effects Eff`는 함수 타입이다.
- `T...`는 반복 positional residue이고 `Record***`는 named-rest
  residue이다. 둘은 public API identity에 남는다.
- `Record***`와 `Map`은 같은 호출 채널이 아니다.

### 특수 타입 표면

```ebnf
OwnershipQualifier ::= "owned" | "borrowed" | "mut" | "inout"

SharpShapeType      ::= "#" StaticDimensionList "[" TypeRef "]"
StaticDimensionList ::= StaticIntLiteral ("," StaticIntLiteral)*

ExistentialType     ::= "any" QualifiedTypeReference
                        AssociatedTypeConstraintList?
OpaqueType          ::= "some" QualifiedTypeReference
                        AssociatedTypeConstraintList?
FacetType           ::= "Facet" "<" "borrow" "any"
                        QualifiedTypeReference
                        AssociatedTypeConstraintList? ">"

TypeofType          ::= "typeof" TypeofStaticSampleOperand
AssociatedProjection ::= "<" TypeRef "as" QualifiedTypeReference
                         ">" "::" Identifier
```

`#2,3[Int]`는 element type과 exact static shape를 함께 갖는
NumericArray 타입이다. `typeof`의 피연산자는 일반 표현식이 아니라
literal, 정적 collection sample, NumericArray literal, measure literal의
닫힌 집합이다.

`any Trait`는 명시적 existential, `some Trait`는 opaque result
표면이다. associated type은 `<I as Iterator>::Item`처럼 Trait 문맥을
명시해야 한다. `I.Item`은 associated projection 문법이 아니다.

현행 Facet source type은 정확히 `Facet<borrow any Trait ...>`이다.
구체 payload 타입을 철자에 노출하거나 mode를 생략할 수 없다.
owned/inout Facet 패키지는 현재 source route가 없는 비활성 설계이다.

### refinement와 확인 경계

```ebnf
TypeAnnotation  ::= ":" TypeRef RefinementClause?
RefinementClause ::= "where" PredicateExpr

TypeAliasDecl   ::= TopLevelVisibility? "type" Identifier
                    TypeParameterList? "=" TypeAliasRhs StatementBoundary
TypeAliasRhs    ::= TypeRef RefinementClause? | StaticRangeType
StaticRangeType ::= StaticIntLiteral ".." StaticIntLiteral

CastSuffix      ::= "as" "?" TypeRef | "as" "!" TypeRef
```

다음 표면은 역할이 다르다.

| 표면 | 결과와 실패 채널 |
|---|---|
| 정적으로 증명된 refinement 값의 구성/전달 | 대상 타입을 직접 산출 |
| `value as? T` | `Option<T>`; 실패 상세를 버리는 검사 |
| `value as! T` | `T`; 실패 시 명시된 `RefinementAssertionDefect` |
| `T::check(value)` | `Result<T, error E>`; 상세 오류를 보존 |

`type Port = 0..65_535`는 닫힌 정적 정수 범위 alias의 짧은 표면이다.
일반 refinement는 `type Port = Int where this >= 0 and this <= 65_535`
형태이다. refinement predicate는 유한 R0 whitelist, 정확한 `Bool`,
전체성, 종료성, 무효과, 무권한, 비중단 조건을 만족해야 한다.

## 허용과 정적 의미

### 정규화와 타입 identity

checker는 비교 전에 alias, optional 층, Union/intersection,
associated projection, row, label, 소유권 mode, effect, error,
cancellation, measure와 witness identity를 정규화한다. 정규화는
종료해야 하고 occurs check를 수행하며 책임 차이를 지우지 않는다.

의미 타입 identity는 저장 배치, serialization tag, runtime
discriminant, ABI 및 backend layout과 별개이다. 추론은 bidirectional이고
지역적이며 결과 타입이나 source order를 숨은 tie-breaker로 쓰지 않는다.

### closed Union

`A | B`는 열린 동적 합이 아니라 명시된 대안만 갖는 closed Union이다.
정규화는 nested Union을 평탄화하고 exact duplicate를 제거한 뒤 각
대안 쌍을 유한 R0 관계로 판정한다. 각 쌍이 `DISJOINT`임이 증명될 때만
Union을 허용한다. 동치/함의 관계는 subsumption 문제이며, overlap 또는
`UNKNOWN`은 런타임 winner를 만들지 않고 거부한다.

값을 Union에 넣을 때는 정규화 후 정확히 하나의 대안을 선택할 수
있어야 한다. 서로 다른 결과를 자동으로 Union으로 join하지 않는다.
예를 들어 heterogeneous List는 `List<Int | String>`이라는 expected
type을 먼저 명시해야 한다.

### closed Union typed pattern과 narrowing

`Identifier : TypeRef`는 기본적으로 irrefutable 정적 typed binder이다.
단, 다음 조건을 모두 만족할 때만 checker가
`UnionAlternativeBindPattern`으로 정규화한다.

1. 소유자가 `match`, guarded binding 등 refutable pattern 문맥이다.
2. subject의 정규화된 타입이 이미 선언된 closed Union이다.
3. `TypeRef`가 그 Union의 정확한 대안 identity 하나를 가리킨다.
4. 검사는 이미 저장된 Union injection identity만 읽는다.

이 검사는 subtype 탐색, refinement 실행, reflection, provider lookup,
Trait discovery가 아니다. 따라서 sealed Class family에 같은 모양의
constructor pattern을 합성하거나 임의 객체에 대해 일반 타입 검사를
수행하지 않는다.

### refinement 판정과 flow proof

refinement 경계는 `PROVED`, `DISPROVED`, `UNKNOWN`의 세 결과로
판정한다.

- `PROVED`: 대상 타입으로 허용한다.
- `DISPROVED`: exact literal/range 모순 diagnostic을 낸다.
- `UNKNOWN`: `REFINEMENT_PROOF_REQUIRED`를 낸다.
- 허용된 경계 밖의 silent narrowing:
  `REFINEMENT_IMPLICIT_NARROWING_FORBIDDEN`.

flow-proof 환경 `Phi`는 선언 타입과 별도로 closed-Union 대안,
Enum case, 허용된 유한 R0 refinement fact와 usable-place 상태를
기록한다. 성공한 구조 pattern과 inline R0 guard는 해당 edge에 fact를
추가할 수 있다. join은 모든 incoming edge에 공통인 fact만 남긴다.
assignment, aliasing mutation, exclusive borrow, escape/capture, consume 및
subject를 바꿀 수 있는 call은 관련 fact를 제거한다.

`def#guard`는 순수하고 전체적인 Bool callable profile이지만, 현재 API
metadata에는 refinement summary owner가 없다. 그러므로
`def#guard` 호출 자체는 `Phi`를 좁히지 않는다. inline으로 판정 가능한
R0 predicate만 narrowing fact를 제공한다.

### closed Union에 한정된 `is`/`!is`

현행 `subject is Alternative`와 붙여 쓰는
`subject !is Alternative`는 subject의 정적 타입이 normalized closed
Union이고 target이 그 Union에 선언된 정확한 단일 alternative
identity일 때만 허용된다. subject와 저장된 injection identity를 각각
한 번 읽어 `Bool`을 만들며, true/false edge에는 서로 보완적인 `Phi`
fact가 남는다. 값을 바인딩하지는 않는다.

검사 직전 subject의 가능한 대안 집합을 `C`, target의 단일 대안을
`T`라고 하면 edge 전이는 정확히 다음과 같다.

| 형식 | true edge | false edge |
|---|---|---|
| `subject is T` | `C ∩ {T}` | `C \ {T}` |
| `subject !is T` | `C \ {T}` | `C ∩ {T}` |

`and then`의 오른쪽에는 왼쪽 식의 true-edge fact가, `otherwise`의
오른쪽에는 false-edge fact가 전달된다. 두 operand를 모두 평가하는
strict `and`와 `or`의 오른쪽에는 이 사전 narrowing을 전달하지 않는다.
fact를 보존할 수 있는 subject는 재평가 없이 같은 저장 위치를 뜻하는
stable place뿐이다. assignment, alias mutation, exclusive borrow,
escape, capture, consume, subject를 변경할 수 있는 call 또는 subject를
소비할 수 있는 call이 발생하면 해당 fact를 제거한다.

`is`와 `!is`는 직접 comparison chain에 참여하지 않는다. 진단은
comparison-chain phase 위반인
`COMPARISON_CHAIN_OPERATOR_NOT_IN_PHASE_A`, closed Union이 아닌 subject의
`TYPE_TEST_SUBJECT_MUST_BE_CLOSED_UNION`, 정확한 단일 대안이 아닌 target의
`UNION_TYPE_TEST_ALTERNATIVE_NOT_EXACT` 순서로 먼저 적용 가능한 항목을
선택한다. 현행 positive/negative 원문 5개는
[표현식 및 연산자](08-expressions-and-operators.md#closed-union-is-is-검증-예제)에
그대로 제시한다.

이 판정은 subclass search, refinement 실행, reflection, Trait discovery
또는 provider lookup을 하지 않는다. 일반 객체·open family·정확하지 않은
Union target에 대한 runtime type test는 거부한다. 선택된 값을
바인딩하려면 typed pattern을, 변환하려면 `as?` 또는 `as!`, refinement
상세 검증에는 `T::check`를 사용한다.

## 평가·소유권·효과

타입 표면 자체는 값을 평가하지 않는다. 다만 타입이 붙는 경계는
원래 표현식을 정확히 한 번 평가하고, 정적 판정과 소유권 판정을 거친
뒤 한 번만 commit한다.

- Union injection은 하나의 대안 identity를 기록하며 값을 복제하지
  않는다.
- pattern discrimination은 commit 전의 nonconsuming test이다. 실패한
  대안은 partial move, irreversible borrow 또는 부분 binding을 남기지
  않는다.
- `as?`, `as!`, `T::check`는 각각 Option, defect, Result의 서로 다른
  failure edge를 보존한다.
- 이미 증명된 refinement 구성은 predicate를 중복 실행하지 않는다.
- borrow Facet은 payload borrow region 밖으로 escape하거나 suspension,
  task, actor/isolation 경계를 넘을 수 없다.
- function type compatibility는 값/context/witness/rest 채널, ownership,
  effects, errors, cancellation, suspension, isolation과 capture를 지우지
  않는다.

## 현행 예제

아래 코드는 모두
[`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)의
`expected_outcome: accept`, `source_activation: none`인 원문이다. 각각
`design_static_product_not_run`이며 parser/checker/runtime 실행 증거는
`NOT_RUN`이다.

### `EX-R51a1-RCTS-UNION-P-001` — 명시적 closed Union과 exhaustive match

```deeplus
private type TextOrNumber = Int | String
let value: TextOrNumber = 13
let text = @match value {
    n: Int => n ~ toString()
    s: String => s
}
```

`n: Int`와 `s: String`은 이 closed Union의 exact alternative binder이다.
일반 runtime type test가 아니다.

### `EX-R51a1-061` — 닫힌 R0 refinement

```deeplus
public type Port = Int where this >= 0 and this <= 65_535
```

### `EX-R48-023` — 정적 범위 alias와 `as?`

```deeplus
private type Port = 0..65_535
let maybePort: Option<Port> = raw as? Port
```

### `EX-R48-037` — Option 결과와 상세 Result의 분리

```deeplus
let maybePort: Option<Port> = raw as? Port
let checkedPort: Result<Port, error RefinementError> = Port::check(raw)
```

### `EX-R48-029` — Trait에 제한된 variance

```deeplus
public trait Source<out T> {
    +def next+() -> Option<T>
        throws Never
        effects {}
}
```

### `EX-R48C-085` — 명시적 associated projection

```deeplus
public def first<I>(it: I) -> <I as Iterator>::Item?
    throws Never
    effects {}
    where I conforms Iterator
= {
    return it ~ next
}
```

### `EX-R51a1-047` — exact shape type와 measure type sample

```deeplus
use std::units::si

public type Grid = #2,2[Int]
let tensor: Grid = #2,2[1, 2; 3, 4;]
let length = 13[cm]
```

## 거부되거나 격리된 형식

| 형태 | 처리 |
|---|---|
| expected Union 없이 서로 다른 branch/List element를 자동 join | 거부 |
| closed Union이 아닌 임의 subject에서 `x: T`를 runtime type test로 사용 | 거부 |
| closed Union이 아니거나 정확한 alternative가 아닌 `value is T`/`value !is T` | 거부 |
| refinement로의 silent implicit narrowing | 거부 |
| effectful, throwing, suspending, provider/authority-bearing refinement predicate | 거부 |
| `def#guard` 호출 결과를 자동 narrowing summary로 사용 | 거부 |
| Class variance | Class owner admission에서 거부 |
| bare associated projection `I.Item` | 거부; `<I as Trait>::Item` 사용 |
| Facet의 concrete payload spelling 또는 mode 생략 | 거부 |
| owned/inout Facet 포장 | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 동적 Trait 상태, 일급/로컬 Witness | `PREVIEW_DESIGN_NONACTIVATABLE` |
| solver-backed 일반 refinement와 Dyn-RCTS | `PREVIEW_DESIGN_NONACTIVATABLE` |

nonactivatable 표면은 feature gate로 켤 수 없고 admitted AST/HIR/MIR/API
residue를 만들지 않는다. 문서, fixture 또는 schema의 존재만으로
활성화되거나 제품 PASS가 되지 않는다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### PREVIEW_NONACTIVATABLE — 타입과 refinement 도입 후보

다음 항목은 단순히 이름만 남은 아이디어가 아니라 도입 판단을 위해
보존된 설계 후보이지만, 현재 source profile에는 진입 경로가 없다.

**의미**

1. **owned/inout Facet**은 borrow Facet보다 오래 사는 소유 existential
   또는 receiver-bound exclusive view를 표현하려는 후보이다. payload의
   concrete type은 계속 은닉하지만, 유일한 owner, allocator/drop plan,
   alias와 region을 손실 없이 보존해야 한다.
2. **Dyn-RCTS**는 닫힌 정적 RCTS descriptor를 runtime inspection
   경계로 확장하려는 후보이다. inspection 결과가 static type, label,
   conformance 또는 authority를 제조해서는 안 된다.
3. **solver-backed refinement**는 현재 finite R0를 넘어서는 predicate를
   다루려는 후보이다. proof failure와 runtime validation을 섞지 않고
   decidability/termination 및 재현 가능한 diagnostic을 먼저 닫아야 한다.

**의존성**

- owned/inout Facet은 concrete payload의 유일 owner와 witness,
  escape/alias/region 법칙, exactly-once cleanup, ABI/type-erasure 경계 및
  MIR move/drop event를 필요로 한다.
- Trait evidence를 포함하는 Facet은
  `TCC-P1-002..008`의 profile, canonical identity/coherence, diagnostic,
  route, HIR/MIR metadata, 실행 corpus와 tooling 계약에 의존한다.
- Dyn-RCTS는 닫힌 runtime representation, type-erasure law,
  cast/failure model, authority non-forging proof와 backend-independent MIR
  event를 필요로 한다.
- 일반 refinement solver는 제한된 source calculus, 종료 metric,
  proof certificate/diagnostic 계약, mutation kill rule 및 target-bound
  checker evidence가 필요하다.

**미해결 guard**

- `SFD-P1-009`는 exact baseline/toolchain/target/command/fixture/output에
  결합된 실행 receipt가 없으므로 OPEN이다.
- Trait evidence가 관여하는 후보에 대해 `TCC-P1-002..008`은 정확히
  7개 모두 OPEN이다.
- 현재 finite R0 밖의 predicate에는 admitted source grammar, 완결된
  decision procedure 및 실행 권위가 없다.
- 현재 borrow Facet을 owned/inout으로 암묵 승격하거나 fallback하는
  경로의 수는 0이어야 한다.

**도입 조건**

도입에는 별도 Design_ activation 판정, exact grammar/profile root,
lossless recovery와 diagnostic, checker/MIR/cleanup 계약, ABI 또는
backend 독립성 proof, 독립 Test_ corpus, formatter/LSP 보존 및
target-bound product receipt가 모두 필요하다. 각 관련 OPEN P1은 해당
closure authority가 독립 증거를 검토한 뒤에만 닫을 수 있다.

**비활성 예**

아래는 Deeplus source가 아니라 후보 상태를 설명하는 개념 record이다.
철자가 정해졌다고 해석해서는 안 된다.

```text
candidate_kind: owned_facet
source_spelling: UNASSIGNED
current_admission: REJECT_FEATURE_NOT_ACTIVATABLE
required_owner: unique
drop_plan: must_preserve_exactly
fallback_to_borrow: forbidden
product_lanes: 15/15_NOT_RUN
```

```text
candidate_kind: solver_refinement
predicate_outside_finite_R0: true
current_admission: REJECT_REFINEMENT_R0_PREDICATE_NOT_ADMITTED
runtime_guess: forbidden
product_lanes: 15/15_NOT_RUN
```

이 절의 문서화는 activation, implementation authority, P1 closure 또는
product PASS가 아니다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- **패턴/매칭:** closed Union typed binder와 Enum variant pattern은
  서로 다른 identity domain이다. 전자는 Union injection identity,
  후자는 `(EnumId, VariantId)`를 사용한다.
- **클래스/Trait:** 명목 subclassing과 Trait conformance는 별개이다.
  `any Trait`, associated projection 및 Facet은 explicit witness/evidence
  경계를 보존한다.
- **함수:** generic constraint, receiver ownership, context/witness/rest
  channel, throws/effects는 함수 type identity에 남는다.
- **컬렉션:** List literal은 expected type 없이 anonymous Union을
  발명하지 않는다. NumericArray의 shape kind는 `StaticInt`이다.
- **흐름 제어:** `Phi`는 branch-local proof일 뿐 binding의 선언 타입을
  다시 쓰지 않는다. join과 mutation kill rule을 통과해야 한다.
- **오류:** `Option`, `Result`, thrown ErrorSet, defect와 cancellation은
  서로 대체되지 않는다.
- **MIR:** lowering은 선택된 타입/대안/witness identity와 ownership,
  effect/error/cancellation을 보존하며 runtime에서 타입을 다시
  추측하지 않는다.

## 정본 근거

- 정확한 타입/parameter/refinement 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- 타입 정규화, Union, narrowing, refinement, Facet:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- 언어 규칙 Part III, VI 및 pattern 경계:
  [`spec/language.md`](../../spec/language.md)
- MIR refinement와 failure projection:
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- checker predicate:
  [`spec/types/predicates/`](../../spec/types/predicates/)
- current pattern 종류:
  [`spec/patterns/pattern-kinds.json`](../../spec/patterns/pattern-kinds.json)
- 검토 예제:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
