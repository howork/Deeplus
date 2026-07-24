<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# 이름 해석, 타입 추론 및 호출 판정

<!-- deeplus-status-fence: CURRENT -->

## 1. 이 장이 필요한 이유

Deeplus에서 이름 하나를 찾고 호출 하나를 허용하는 일은
문자열을 심볼 테이블에서 찾는 한 단계로 끝나지 않는다.
같은 철자가 모듈 선언, 지역 바인딩, 명목 멤버, 활성 extension,
Trait witness, context 채널 또는 명시적 evidence 채널에 나타날 수 있다.
각 도메인은 서로 다른 정적 identity를 만들며,
한 도메인의 후보가 다른 도메인의 후보로 몰래 변환되어서는 안 된다.

타입 추론도 호출 결과를 보고 가장 편리한 후보를 고르는
전역 탐색이 아니다.
현행 정본은 추론을 지역적이고 양방향인 판정으로 제한하고,
결과 타입이나 소스 선언 순서를 overload 승자 결정에 사용하지 않는다.
추론이 충분한 정보를 얻지 못하면
익명 Union, 숨은 generic, 암시적 권위 또는 runtime type test를
발명하는 대신 진단을 내야 한다.

이 장은 다음 질문에 답한다.

1. 소스 역할과 모듈 경계는 어떤 이름을 후보로 만드는가.
2. lexical 이름, 명목 멤버, extension, witness는 어떤 순서와
   identity로 분리되는가.
3. `Type::item`, `Type::extension::item`, `<T as Trait>::item`,
   explicit runtime owner의 네 capability domain은 왜 합쳐지지 않는가.
4. generic Phase A가 현재 확정한 부분과 아직 확정하지 않은 부분은
   무엇인가.
5. 값, context, witness, 반복 positional, named-rest 채널은
   어떻게 별도로 결합되는가.
6. lambda와 trailing closure는 언제 expected callable type을
   사용할 수 있는가.
7. `catch`는 왜 일반적인 runtime pattern dispatch가 아닌가.
8. 허용 판정 뒤 평가·소유권·효과·오류·정리 책임은 어떻게
   호출 계획에 남는가.

이 장은 정확 문법,
[`spec/language.md`](../../spec/language.md),
[`spec/types/type-system.md`](../../spec/types/type-system.md),
[`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json),
[`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json),
[`spec/contracts/companion-capability-coherence.json`](../../spec/contracts/companion-capability-coherence.json),
그리고 관련 checker predicate를 설명용으로 투영한다.
문서 자체는 새 overload, 새 inference fallback 또는 새 evidence authority를
만들지 않는다.

## 2. 판정 파이프라인 개요

하나의 호출 표현식은 대략 다음 정적 단계를 지난다.
이 순서는 구현 자료 구조를 강제하지 않지만,
각 단계가 관찰 가능한 책임을 앞 단계로 되돌려 바꾸지 못한다는
경계를 고정한다.

1. **소스 역할 확정**
   - library, executable, script 중 정확히 하나의 Stable root를 고른다.
   - 모듈 선언, import, use, export의 구조적 위치를 확인한다.
2. **CST/AST owner 확정**
   - `*`, `**`, `***`, `context`, `using`, trailing closure가
     어느 문법 owner에 속하는지 결정한다.
   - 타입 정보를 사용해 잘못 파싱한 토큰열을 고치지 않는다.
3. **lexical 및 정적 identity 해석**
   - 지역 이름, 선언 이름, 타입 이름, 명목 멤버, extension set,
     witness identity를 분리해 기록한다.
4. **호출 모양 정규화**
   - positional, named, context, witness, repeated, named-rest 잔여를
     별도 채널로 만든다.
   - 중복 label과 정적으로 알 수 없는 고정 positional arity를 거부한다.
5. **후보 집합 필터**
   - 호출 모양과 non-lambda 인수로 먼저 후보를 줄인다.
   - 반환 타입과 선언 순서는 tie-breaker가 아니다.
6. **generic 및 expected-type 판정**
   - 선언의 generic kind와 인수에서 생긴 지역 제약을 검사한다.
   - expected callable type을 사용할 수 있는 bounded lambda 형식만
     그 뒤에 검사한다.
7. **책임 호환성 판정**
   - ownership mode, call-right, capture, effect/error row,
     suspension, isolation, cancellation, cleanup을 비교한다.
8. **단일 후보 확정**
   - 정확히 하나의 호환 후보가 남아야 한다.
   - ambiguity에는 source-order fallback이 없다.
9. **HIR/MIR handoff**
   - 선택한 declaration, label row, witness, extension,
     context/evidence origin을 고정 identity로 넘긴다.
   - lowering은 이름 검색을 다시 수행하지 않는다.

이 파이프라인의 각 실패는
뒤 단계의 추측으로 복구되지 않는다.
예를 들어 고정 formal을 채우는 `*sequence`의 arity가 정적으로
알 수 없다면,
반환 expected type이 특정 overload를 선호한다는 이유로
그 호출을 허용할 수 없다.

## 3. 정확한 소스·모듈 문법

### 3.1 Stable 소스 루트

```ebnf
Deeplus ::= LibrarySourceFile
          | ExecutableSourceFile
          | ScriptSourceFile ;

LibrarySourceFile    ::= ModuleDecl? LibrarySourceItem* ;
ExecutableSourceFile ::= ModuleDecl? ExecutableSourceItem* ;
ScriptSourceFile     ::= Shebang? ModuleDecl? ScriptSourceItem* ;

ModuleDecl ::= "module" QualifiedPath StatementBoundary ;
```

소스 파일은 파일명만으로 여러 역할을 동시에 얻지 않는다.
manifest와 정규화된 프로젝트 상대 경로가
한 파일에 정확히 하나의 source role을 부여한다.
그 역할이 선택된 뒤에야 허용되는 최상위 item 집합이 결정된다.

`module` 선언은 이름 공간을 만든다고 해서
runtime module object를 만드는 표현식이 아니다.
모듈 path는 HIR의 정적 identity이며 runtime String으로 조회하거나
바꿀 수 없다. 완전한 identity는 build graph의 `PackageId`와 source의
`ModulePath`를 결합한다. Package는 배포·의존성·build 단위이고 Module은
이름 공간·가시성·source 구성 단위다. manifest가 source file을
ModulePath에 대응시키므로 directory tree와 ModulePath가 같을 필요는
없다.

### 3.2 import, use, export

```ebnf
ImportDecl ::= "import" QualifiedPath ImportTail? StatementBoundary ;
UseDecl    ::= "use" QualifiedPath StatementBoundary ;
ExportDecl ::= "export" ExportItem StatementBoundary? ;
```

세 선언은 같은 일을 하지 않는다.

- `import`는 모듈 또는 선언 이름을 정적 해석 범위에 들인다.
- `use`는 정본이 허용한 extension set 같은 활성화 대상을
  명시적으로 활성화한다.
- `export`는 외부 API 가시성 잔여를 만든다.

`import`만 했다는 이유로 extension selector lookup이 활성화되지 않는다.
반대로 `use`는 runtime plugin loading이나 동적 provider 검색을 뜻하지 않는다.
block-local import도 compile-time 이름 가시성 변화일 뿐,
제어가 그 문장에 도달할 때 모듈을 적재하는 효과가 아니다.

### 3.3 경로와 identity

`QualifiedPath`는 하나 이상의 identifier segment를 가지며 segment
사이는 `::`다. 그 구성 토큰은 소스 철자다.
해석 결과는 정규화된 모듈·선언 identity다.
정본은 다음을 서로 분리한다.

- 소스에 적힌 path
- 해석된 module identity
- 선언 identity
- public API digest의 path residue
- linker 또는 backend symbol
- FFI symbol

두 소스 path가 같은 backend symbol로 내려갈 수 있다는 사실은
두 Deeplus 선언을 같은 identity로 만들지 않는다.
반대로 같은 Deeplus declaration identity를 서로 다른 backend가
다른 mangled symbol로 표현할 수 있다.

## 4. 이름 공간과 가시성

### 4.1 lexical lookup

지역 `let`, `var`, parameter, local function은
각 lexical owner가 만든 범위에서 해석된다.
local function은 선언 뒤부터 보이며,
앞선 위치에서 호출할 수 있는 암시적 hoisting이 없다.
현행 local mutual recursion도 자동으로 만들어지지 않는다.

지역 shadowing은 일반 lexical shadowing 규칙을 따른다.
다만 rightward flow binding의 `$name`과 `$$name`은
현재 block에서 fresh identifier만 허용하므로,
기존 지역을 shadow하거나 대입하는 표면이 아니다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def choose(input: Int) -> Int = {
    let value = input + 1
    {
        let value = input + 2
        consume(value)
    }
    return value
}
```

안쪽 `value`는 안쪽 block의 lexical identity다.
block을 나가면 바깥 `value`가 다시 보인다.
두 binding은 같은 문자열을 사용하지만
HIR identity와 cleanup 범위가 다르다.

### 4.2 최상위 가시성

타입을 생성하는 최상위 owner는
정본이 지정한 `public`, `common`, `private` 중 하나를
명시해야 한다.
다른 최상위 owner에서 가시성을 생략하면
정본이 허용한 경우 `private`로 정규화된다.

가시성은 단순한 문서 태그가 아니다.
더 넓은 공개 선언의 signature가
더 좁은 private type이나 witness identity를 유출하면
API visibility closure가 실패한다.

type member는 최상위 단어가 아니라
`+`, `-`, `#` member visibility owner를 사용한다.
여기서 `#`는 declaring nominal type과
그 명목 subclass 범위의 hierarchy-protected visibility다.
같은 package에 있다는 사실만으로 접근할 수 없다.

### 4.3 선언보다 문자열을 우선하지 않는다

reflection, provider 또는 runtime registry가
소스 identifier와 같은 문자열을 제공해도
그 문자열은 정적 declaration identity가 아니다.
callable lookup, member lookup, witness lookup은
정적 graph를 닫은 뒤 끝난다.
MIR에서 문자열을 다시 읽어 winner를 바꾸는 경로는 없다.

## 5. 멤버, extension 및 witness 해석

### 5.1 서로 다른 후보 도메인

정적 selector 해석은 적어도 다음 identity를 구분한다.

1. receiver의 명목 멤버
2. 명시적으로 활성화된 extension set의 멤버
3. 선택된 Trait conformance record의 witness member
4. type-side 또는 associated projection

extension이 존재한다고 Trait conformance가 생기지 않는다.
Trait conformance가 존재한다고 같은 이름의 extension이
witness member로 바뀌지 않는다.
같은 glyph 또는 selector를 공유하더라도
AST/HIR owner와 API residue가 다르다.

#### 5.1.1 네 capability 표면은 closed search domain이다

정적 capability 선택은 다음 네 표면을 구분한다.

| 표면 | 최초 owner | 허용 후보 | 실패 뒤 fallback |
|---|---|---|---|
| `Type::item` | normalized nominal type | 그 type의 `let::`/`def::` 또는 그 namespace가 소유한 Enum case | 없음 |
| `Type::extension::item` | exact named extension set | 그 set 안의 exact type-side item | 없음 |
| `<T as Trait>::item` | exact Trait와 selected conformance | associated type/value/function requirement의 exact binding | 없음 |
| `owner.item(...)` | explicit ordinary runtime value | 그 값의 visible instance operation | 정적 type-side/Trait domain으로 이동하지 않음 |

이 분리는 철자 취향이 아니라 의미 안정성 규칙이다. 예를 들어
`T::zero`가 visible Trait를 암시적으로 검색한다면 새 Trait import 하나가
기존 프로그램의 후보 수와 winner를 바꿀 수 있다. Deeplus는 이를
허용하지 않는다. generic `T`의 Trait associated item은 보이는 후보가
하나뿐이어도 `<T as Trait>::item`으로 exact Trait를 써야 한다.

`Type::extension::item`도 nominal lookup의 긴 철자가 아니다. 가운데
`extension` segment는 `ExtensionSetId`를 고정한다. set이 inactive이거나
item이 없으면 그 domain에서 terminal failure가 되고 `Type::item`,
Trait witness 또는 provider registry를 대신 검색하지 않는다.

explicit runtime owner는 type token이 아니다. service, Actor handle,
shared-state object처럼 실제로 구성되거나 context로 주입된 ordinary
value이며, 그 값의 ownership·isolation·effect·error·cleanup 책임을
가진다. resolver가 type name을 runtime metatype value나 숨은 companion
singleton으로 변환하는 단계는 없다.

#### 5.1.2 Trait-qualified associated selector 문법

```ebnf
TraitQualifiedAssociatedSelector ::=
    "<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier

AssociatedProjection ::= TraitQualifiedAssociatedSelector

QualifiedStaticExpr ::= StaticQualifier "::" Identifier
                      | TraitQualifiedAssociatedSelector

StaticQualifier ::= QualifiedTypeReference | AssociatedProjection
```

type context에서는 마지막 `Identifier`가 associated type이어야 한다.
expression context에서는 associated immutable value 또는 associated
function이어야 한다. CallSuffix가 붙으면 선택된 item의 kind가 function인지
먼저 확인하고 그 뒤 ordinary call-shape 판정을 수행한다.

`<T as Trait>::Assoc::member`는 두 단계를 명시한다.

1. `<T as Trait>::Assoc`를 selected conformance의 associated type으로
   정규화한다.
2. 정규화된 결과 타입의 nominal type-side domain에서 `member`를 찾는다.

두 번째 단계는 original Trait의 다른 requirement, visible extension,
runtime provider를 후보로 추가하지 않는다. associated value에
`::member`를 붙이거나 associated type을 expression 값처럼 쓰면
`TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH`다.

#### 5.1.3 exact identity residue

Trait-qualified selection은 이름 문자열 하나만 HIR에 넘기지 않는다.
적어도 다음 일곱 축을 한 selection record로 보존한다.

1. `TraitId`
2. `RequirementId`
3. `ConformanceId`
4. `TraitWitnessId`
5. `ImplementationId`
6. normalized substitution인 `SubstitutionId`
7. normalized responsibility인 `ResponsibilityId`

responsibility 축에는 호출 또는 값 사용에 필요한 ownership,
effect, error, suspension, isolation, publication/cleanup 조건이 들어간다.
일곱 축이 완성되기 전에는 MIR operation을 만들 수 없다. 일부를
지우고 runtime에서 이름, table, provider 또는 registration order로
복원하려 하면
`TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE` 또는
`TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN`이다.

### 5.2 정적 receiver type

extension lookup은 receiver의 runtime class가 아니라
정적 normalized type을 사용한다.
동적 subclass에 더 가까운 extension을 runtime에서 다시 고르는
dispatch는 현행이 아니다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def renderName(value: User) -> String = {
    return value ~ displayName()
}
```

이 호출에서 `displayName` 후보 집합은
`User`의 정적 멤버와 현재 활성 extension/witness 도메인으로 닫힌다.
runtime payload가 `AdminUser`라는 이유로
새 extension set을 검색하지 않는다.

### 5.3 ambiguity

같은 우선 tier 안에서 호환 후보가 둘 이상이면 ambiguity다.
다음은 winner가 아니다.

- 먼저 import한 선언
- 먼저 `use`한 extension
- 파일에서 먼저 선언된 overload
- 더 가까운 소스 위치
- provider registration 순서
- 반환 expected type만으로 선호되는 후보

호출자는 selector를 한정하거나
활성 set을 줄이거나
인수 모양을 명확히 해야 한다.

### 5.4 명시적 associated selection 예

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
public trait DefaultValue {
    def ::make() -> Self
        throws Never
        effects {}
}

private def makeDefault<T>() -> T
    where T conforms DefaultValue
= {
    return <T as DefaultValue>::make()
}
```

resolver는 `T`의 모든 type-side item을 먼저 모으지 않는다.
`DefaultValue`를 exact Trait로 고정하고, `T conforms DefaultValue`
obligation을 정규화한 뒤, 하나의 conformance와 `make` requirement
implementation을 결합한다. 그 뒤에야 빈 ordinary argument list와
return/ownership/effect/error 계약을 검사한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
public final class UserId {
    +let raw: Int

    +def! new(raw: Int)
        : super!()
    = {
        self.raw = raw
    }

    +def ::fromInt(raw: Int) -> UserId
        throws Never
        effects {}
    = {
        return UserId!new(raw)
    }
}

public extension UserId as hexadecimal {
    +def ::parse(text: String) -> UserId
        throws ParseError
        effects {}
    = {
        return UserId::fromInt(parseHex(text))
    }
}

use UserId::hexadecimal

private let direct = UserId::fromInt(42)
private let parsed = UserId::hexadecimal::parse("2a")
```

`direct`와 `parsed`는 반환 타입이 같아도 서로 다른 domain이다.
`UserId::fromInt`에는 nominal declaration identity가, 두 번째 호출에는
`UserId::hexadecimal`의 exact extension-set/member identity가 남는다.
extension 호출 실패가 nominal `fromInt`를 대체 후보로 만들지 않는다.

### 5.5 거부 예와 terminal 판정

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
private def makeImplicitly<T>() -> T
    where T conforms DefaultValue
= {
    return T::make()
}
// TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION
```

`T::make`는 nominal type-side domain만 연다. 그 domain에 item이 없다고
`DefaultValue` requirement를 검색하지 않는다. 정확한 수정은
`<T as DefaultValue>::make()`다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
public trait Versioned {
    let ::version: Int
}

private def invalidType<T>(
    value: <T as Versioned>::version,
) -> Unit
    where T conforms Versioned
= {
}
// TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH
```

type 위치의 selector는 associated type이어야 하지만 `version`은
associated value다. checker는 같은 이름의 nominal nested type 또는
extension type alias를 찾아 의미를 바꾸지 않는다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
private let hidden = DefaultValue
private let value = hidden.make()
// COMPANION_OBJECT_NOT_CURRENT
```

Trait/type 이름은 runtime value가 아니며, 숨은 companion instance나
storable witness로 변환되지 않는다. stateful behavior가 필요하면
명시적으로 구성하거나 주입한 ordinary owner 값을 선언해야 한다.

### 5.6 private authority는 selector가 아니라 lexical owner가 결정한다

명목 type body 안의 `def::`는 declaring owner의 private construction
authority를 사용할 수 있다. 그러나 같은 module의 top-level helper,
`Type::extension::item`, 외부 conformance의 associated `def::`는 ordinary
visibility만 가진다. `::`가 같다는 이유로 private constructor 접근권을
전이하지 않는다.

이 경계를 어기면
`TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN`이다. 특히 conformance
associated function은 `ImplementationId`를 만들지만 nominal
type-side member의 `ImplementationId`를 새로 만들지 않는다. 공개 nominal
factory가 필요하면 owner body에 선언하고 외부 implementation은 그
factory를 정상 호출해야 한다.

### 5.7 Associated `let::` admission은 lookup보다 먼저 닫힌다

associated value가 이름 해석에 참여하려면 binding 자체가 최소 Stable
profile을 통과해야 한다. initializer는 const-evaluable 또는 deterministic
static-materializable이어야 하고, 결과는 immutable이며 deeply immutable
또는 명시적으로 `Shareable`이어야 한다. 초기화는 pure/synchronous이고,
Resource·drop/finalizer·ambient authority·escaping borrow·cycle을
포함하지 않아야 한다.

persistent mutable cache, runtime registry, lifecycle이 정의되지 않은
allocation은 immutable `let` 이름 아래 숨겨도 허용되지 않는다.
`ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED`가 binding을 거부하면
그 item은 이후 `<T as Trait>::item` 후보가 되지 않으며 recovery node도
Stable HIR/MIR로 내려가지 않는다. runtime owner가 필요한 기능은
ordinary value나 Actor/shared-state owner로 명시한다.

## 6. generic 문법과 kind

### 6.1 정확 문법

```ebnf
TypeParameterList ::= "<" TypeParameter ("," TypeParameter)* ","? ">" ;
TypeParameter     ::= VarianceMarker? Identifier
                      TypeParameterKindAnnotation? ;
VarianceMarker    ::= "out" | "in" ;

TypeParameterKind ::= "type"
                    | "StaticInt"
                    | "EffectRow"
                    | "ErrorSet" ;

TypeArgumentList  ::= "<" TypeArgument ("," TypeArgument)* ","? ">" ;
TypeArgument      ::= TypeRef
                    | StaticIntLiteral
                    | ErrorTypeArgument ;
ErrorTypeArgument ::= "error" TypeRef ;

WhereClause    ::= "where" WherePredicate
                   ("," WherePredicate)* ;
```

kind annotation을 생략한 매개변수는
일반 type parameter다.
`StaticInt`, `EffectRow`, `ErrorSet`은
서로 바꿔 쓸 수 있는 별칭이 아니다.
checker는 substitution 전에 kind identity를 보존한다.

`Result<T, error E>`의 `error`는
사용 지점에서 오류 역할을 드러내는 표지다.
generic 선언의 `E: ErrorSet` 안에서는
같은 역할을 다시 철자하지 않는다.

### 6.2 Phase A가 닫은 것

현행 정본이 확정한 최소 경계는 다음과 같다.

- generic parameter의 닫힌 kind 집합
- 기본 constructor invariance
- 제한된 Trait parameter 위치의 `out`/`in`
- normalization과 occurs check 필요성
- function compatibility가 보존해야 할 책임 축
- return type과 source order의 tie-break 금지
- hidden implicit generic과 anonymous Union 발명 금지
- 불충분하거나 모호한 제약의 deterministic rejection

이 항목은 제품 checker가 실행되었다는 뜻이 아니다.
관련 `GenericConstraintSatisfied`와
`TypeParamKindAdmitted` predicate는 현재
설계 정적 seed이며 product support가 `NOT_RUN`이다.

### 6.3 아직 닫히지 않은 추론 세부

정본은 완전한 product inference solver의
다음 세부를 아직 실행 계약으로 닫지 않았다.

- 모든 제약의 수집 자료 구조
- 제약 간 우선순위와 상세 진단 순서
- `StaticInt` 식 추론의 허용 범위
- EffectRow/ErrorSet 매개변수의 명시·추론 경계 전부
- higher-rank inference
- 일반화 시점과 value restriction
- 다수 해가 가능한 경우의 principal type 계산

따라서 구현자는 문서의 예제를 근거로
임의의 Hindley–Milner 일반화,
반환 타입 기반 overload 선택,
row 변수 자동 생성,
소스 순서 기반 default를 추가할 수 없다.

문서에서 “양방향 지역 추론”이라고 말하는 것은
허용된 expected type과 source expression 사이에서
지역적인 검사를 수행할 수 있다는 경계이지,
미정인 solver 정책을 승인한다는 뜻이 아니다.

### 6.4 보수적인 판정 순서

현재 정본을 침범하지 않고 설명할 수 있는
검사 순서는 다음과 같다.

1. 선언된 generic parameter와 kind를 읽는다.
2. 호출 callee 뒤의 `TypeArgumentList`를 type-goal 문법으로 오인하지
   않는다. 현행 call suffix에는 명시적 type argument가 없다.
3. call shape를 generic 추론보다 먼저 닫는다.
4. non-lambda explicit argument를
   해당 formal의 normalized type과 비교한다.
5. occurs check와 responsibility-preserving normalization을 적용한다.
6. 독립적으로 고정된 expected type이 허용되는 위치에서는
   후보를 고르는 것이 아니라 이미 남은 후보를 검사한다.
7. `where` constraint와 witness requirement를 검사한다.
8. 유일한 호환 결과를 증명하지 못하면 거부한다.

5~8단계의 세부 solver가 제품에서 실행되었다는 receipt는 없다.
이 순서는 금지된 fallback을 분명히 하는 설명 경계다.

### 6.5 지역 generic 추론 예제

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private def identity<T>(value: T) -> T = {
    return value
}

private let answer: Int = identity(42)
```

값 인수 `42`의 `Int` domain이 `T`에 지역 제약을 준다.
호출 shape는 값 인수 하나를 요구하고, 왼쪽의 `Int` annotation은
이미 선택된 선언의 substitution 결과를 검사할 뿐 별도의
call-site type argument를 만들지 않는다.

다음은 kind 역할을 섞는 형식이 허용되지 않는다는
설명용 경계다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private type Invalid = Result<Int, String>
// error 역할 인수는 Result<Int, error String>처럼 표시해야 한다.
```

구문상 type argument처럼 보이는 문자열을
checker가 ErrorSet 역할로 추측해서 고치지 않는다.

## 7. callable signature identity

### 7.1 매개변수 문법

```ebnf
Parameter ::= StoredParameter
            | ContextParameter
            | WitnessParameter
            | RepeatedParameter
            | NamedRestParameter
            | ValueParameter ;

ValueParameter     ::= ParameterMode? ParameterPatternSlot
                       TypeAnnotation ;
ParameterMode      ::= "borrow" | "mut" | "move" | "inout" ;
ContextParameter   ::= "context" Identifier ":" TypeRef ;
WitnessParameter   ::= "using" Identifier ":" "witness" TypeRef ;
RepeatedParameter  ::= Identifier "..." TypeAnnotation ;
NamedRestParameter ::= Identifier "***" TypeAnnotation ;
```

ordinary parameter는 identifier slot이다.
refutable Pattern을 formal에 직접 넣지 않는다.
구조 분해는 함수 body의 pattern owner나
별도의 exhaustive declarative clause owner가 담당한다.

callable signature identity에는
다음이 보존된다.

- parameter 순서
- visible label
- value/context/witness channel
- ownership mode
- repeated positional residue
- named-rest residue
- return type
- throws ErrorSet
- EffectRow
- suspension과 async profile
- isolation
- callable call-right와 capture responsibility

반환 타입이 identity에 포함된다는 사실과
반환 타입이 overload tie-breaker가 아니라는 사실은
모순이 아니다.
전자는 API 호환성을 말하고,
후자는 후보 선택 authority를 제한한다.

### 7.2 `mut` parameter와 `mut T`

ordinary `mut name: T` parameter는
callee-owned mutable local place 하나를 만든다.
argument는 한 번 평가·획득되고,
affine owner이면 그 local place로 move된다.
caller place를 가리키는 alias나 write-back edge는 생기지 않으며
callee가 cleanup을 정확히 한 번 소유한다.
parameter commit 전 실패는 caller owner를 보존한다.

이는 같은 caller place를 한 dynamic call extent 동안
독점적으로 borrow하고 그 place에 변경을 반영하는 `inout`과 다르다.
`move`는 ownership transfer를 강조하지만 그 자체로
callee local의 mutation permission을 만들지 않는다.
`mut T` type qualifier는 unique mutable owner/view 책임이며
parameter channel의 다른 철자가 아니다.

따라서 caller-visible 변경이 목적이면 `inout`,
callee-owned mutable working copy/owner가 목적이면 `mut`,
명시적 transfer만 필요하면 `move`,
공유 관찰이면 `borrow`를 선택한다.
이 구분은 current design-static law지만
parser/checker/MIR/backend 실행은 계속 `NOT_RUN`이다.

## 8. 호출 인수의 정확한 채널

### 8.1 문법

```ebnf
Argument ::= ContextArgument
           | WitnessArgument
           | NamedArgument
           | PositionalUnfoldArgument
           | NamedUnfoldArgument
           | Expr ;

ContextArgument         ::= "context" Expr ;
WitnessArgument         ::= "using" WitnessArgumentValue ;
WitnessArgumentValue    ::= Identifier
                          | ConformanceEvidenceSelector
                          | NamedConformanceEvidenceSelector ;
NamedArgument           ::= Identifier ":" Expr ;
PositionalUnfoldArgument ::= "*" Expr ;
NamedUnfoldArgument     ::= "**" Expr ;
```

각 channel은 source order를 보존하지만
한 flat value 목록으로 합쳐지지 않는다.
`context expr`는 context formal에만 결합하고,
`using evidence`는 witness formal에만 결합한다.
ordinary `Expr`가 우연히 같은 타입이라는 이유로
둘 중 하나를 채우지 않는다.

### 8.2 context channel

context parameter는 ambient lookup 요청이 아니다.
호출자는 `context Expr`로 값을 명시한다.
허용되는 context value는 재사용 가능하고 Shareable하며,
drop responsibility, resource ownership, authority를 숨기지 않아야 한다.
context marker 자체는 저장하거나 반환하는 first-class 값이 아니다.

이 경계는 named effect capability와도 중요하다.
EffectRow는 무엇을 관찰하는지 기술하고,
capability는 그 효과를 수행할 권위를 나타낸다.
둘은 별도 판정이다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
capability FileAccess for {io}

private def readConfig(
    context access: FileAccess,
    path: String,
) -> String
    effects {io}
= {
    return openText(context access, path)
}
```

이 예제의 핵심은
`effects {io}`가 capability를 합성하지 않고,
`context access`가 효과 row를 지우지 않는다는 것이다.
구체 Prelude API 이름은 구현 라이브러리 계약에 따라야 하며,
이 예제는 channel과 책임 분리를 설명한다.

### 8.3 witness channel

explicit witness는 ordinary runtime value가 아니다.
formal은 `using name: witness Trait`이고,
호출은 `using identifier` 또는
허용된 conformance evidence selector를 사용한다.

witness는 borrowed, nonescaping static evidence다.
저장, 반환, escaping closure capture,
runtime key 선택은 허용되지 않는다.
같은 Trait 이름을 가진 임의 값은 witness를 대신할 수 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
private def compareWith<T>(
    left: T,
    right: T,
    using order: witness Ord<T>,
) -> Bool = {
    return orderedEqual(left, right, using order)
}
```

이 예제는 formal 철자를 설명한다.
실제 conformance selector의 이름과 제공 Trait은
프로그램의 정적 conformance graph에서 유일하게 해석되어야 한다.

### 8.4 positional unfold

`*expr`는 다음 두 source만 허용한다.

- `Sequence<T>` element stream
- 정적으로 길이와 순서를 아는 tuple

NumericArray를 평탄화하거나
Record field를 positional로 바꾸지 않는다.
source expression은 한 번 평가되고,
생성되는 positional 값은 source order를 따른다.

고정 positional formal을 채우려면
남은 arity가 정적으로 알려져 정확히 일치해야 한다.
길이를 runtime에서만 아는 Sequence는
repeated positional formal에는 공급할 수 있지만,
고정 formal 여러 개를 추측해서 채울 수 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private def sumAll(values...: Int) -> Int = {
    return reduceSum(values)
}

private def total(xs: List<Int>) -> Int = {
    return sumAll(*xs)
}
```

여기서는 repeated channel이 source의 유한 element stream을 받는다.
같은 `*xs`를 `pair(left: Int, right: Int)`에 전달하면
`xs`의 runtime 길이가 2일 수도 있다는 이유로 허용되지 않는다.

### 8.5 named unfold와 named rest

call-side `**record`는 정적 label row를 공급한다.
formal-side `options***: Record`는
결합되지 않은 named argument를 받는 유일하고 마지막인
named-rest channel이다.

`**`와 `***`는 교환할 수 없다.
Map key는 runtime value이므로
call named label을 만들지 못한다.
`#map{ **base }`의 Map literal unfold는
호출 named unfold와 같은 의미 owner가 아니다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private def command(
    name: String,
    args...: String,
    options***: Record,
) -> Unit = {
    dispatch(name, *args, **options)
}
```

`args`는 positional stream이고,
`options`는 static label row다.
두 residue는 public function type과 API digest에도 남는다.

## 9. call-shape admission 알고리즘

### 9.1 source-order scan

checker는 ordinary argument list 또는 message payload syntax를 왼쪽에서
오른쪽으로 읽는다.
각 인수는 아직 실행하지 않고
먼저 다음 structural descriptor를 만든다.

- ordinary positional
- explicit named label
- positional unfold
- named unfold
- context
- witness
- trailing closure

같은 인수를 둘 이상의 descriptor에 넣지 않는다.
label token을 runtime String으로 평가하지 않는다.

message call은 ordinary descriptor 목록을 그대로 쓰지 않는다. 먼저
정확히 하나의 payload descriptor를 만든다.

- 생략 또는 호환형 `()` → `none`
- bare/grouped expression → `scalar`
- positional `(x, y, ...)` → `tuple`
- all-named `(x: a, y: b, ...)` → `record`

`function(x, y)`의 두 ordinary argument와
`receiver ~ selector (x, y)`의 Tuple payload 하나를 이 단계에서
구분한다. 공백 유무는 의미가 아니므로 `selector(x, y)`와
`selector (x, y)`의 payload shape는 같다.

### 9.2 formal channel 결합

후보별로 다음을 판정한다.

1. positional 인수를 남은 positional formal에 순서대로 결합한다.
2. tuple unfold는 정적 arity만큼 펼친다.
3. Sequence unfold가 fixed formal로 흘러가면
   static arity evidence를 요구한다.
4. explicit named label은 정확히 같은 visible formal label 하나에 결합한다.
5. named unfold의 모든 label을 정적으로 열거한다.
6. 중복 label을 즉시 거부한다.
7. context는 context formal에만 결합한다.
8. witness는 witness formal에만 결합한다.
9. 남은 positional은 repeated channel 하나에만 결합한다.
10. 남은 named는 named-rest channel 하나에만 결합한다.
11. 인수가 빠지거나 두 번 결합되면 후보를 제거한다.

message payload는 선택된 selector의 value-input product에 투영한다.
`none`은 0개, scalar는 1개, Tuple은 declaration order의 positional
formal, Record는 exact static label의 named formal을 채운다. 한 Tuple
formal 후보와 여러 positional formal 후보가 둘 다 맞는다면 임의로
선택하지 않고 ambiguity다. payload가 context/witness channel을 채우거나
actor isolation evidence를 합성하지 않는다.

이 단계는 overload ranking보다 먼저 끝난다.
declaration order와 반환 타입은
shape failure를 고치지 못한다.

### 9.3 후보 우선 경계

정본은 fixed arity,
repeated positional,
named rest를 구별한다.
그러나 같은 admissibility tier에서 둘 이상이 남으면
source order로 고르지 않는다.
특히 서로 다른 rest overload가 모두 같은 호출을 받을 수 있으면
ambiguity다.

### 9.4 인수 평가와 결합의 분리

정적 call-shape scan은 runtime evaluation이 아니다.
호출이 허용되면 MIR은 원래 source order로
각 인수 expression을 정확히 한 번 평가한다.
formal 선언 순서로 재배열해서 평가하지 않는다.

named argument가 formal 목록에서 앞쪽에 있더라도
소스에서 뒤에 적혔다면 뒤에 평가된다.
label 결합과 평가 순서는 별도 관찰값이다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private let result = build(
    second: trace("second"),
    first: trace("first"),
)
```

정적 label은 `first`와 `second` formal에 결합되지만,
관찰 가능한 `trace` 호출은 소스 순서대로
`"second"` 다음 `"first"`다.

## 10. overload와 expected type

### 10.1 금지된 tie-break

다음 정보만으로 overload winner를 고를 수 없다.

- 반환 expected type
- 선언 순서
- import 순서
- extension activation 순서
- provider registration 순서
- runtime receiver identity

반환 타입은 선택된 callable의 호환성을 검사하는 데 쓰일 수 있지만,
같은 인수 모양의 후보 둘 중 하나를 고르는 authority가 아니다.

### 10.2 익명 Union 금지

branch나 overload 결과가 서로 다르다는 이유로
checker가 자동으로 `A | B`를 만들지 않는다.
모든 reachable value path는
같은 normalized type을 내거나,
독립적으로 고정된 expected type 하나에 각각 호환되어야 한다.

List literal이나 lambda 결과가 heterogeneous라면
호출 결과를 보고 Union을 발명하는 대신
호출자가 명시적인 closed Union expected type을 제공해야 한다.

### 10.3 expected callable이 먼저 고정되어야 하는 경우

implicit lambda parameter `@`,
arrow-elided nullary closure,
빈 closure body는
각각 독립적으로 고정된 callable type이 있을 때만 허용된다.
이 expected type을 얻기 위해 lambda body를 여러 후보에 반복 검사하면
안 된다.

## 11. lambda와 closure

### 11.1 정확 문법

```ebnf
ClosureExpr ::= CaptureList? HashTag* "{" ClosureContent "}" ;

ExplicitLambdaContent ::= LambdaParameterList? "=>" LambdaBody ;
LambdaParameterList    ::= LambdaParameter
                           ("," LambdaParameter)* ","? ;
LambdaParameter        ::= ParameterMode? Identifier
                           TypeAnnotation? ;

CaptureList ::= "[" CaptureItemList? "]" ;
CaptureItem ::= ("let" | "var") Identifier "=" Expr
              | CaptureMode Identifier
              | Identifier ;
CaptureMode ::= "borrow" | "inout" | "move"
              | "clone" | "deep" | "copy" | "once" ;
```

lambda parameter list에는 괄호를 쓰지 않는다.
명시적 nullary lambda는 `{ => body }`다.
parameter는 identifier이며
context, witness, repeated positional, named-rest,
stored parameter channel을 가질 수 없다.

### 11.2 lambda body 결과

단일 expression body는 local result를 만든다.
여러 문장인 non-Unit body는
모든 reachable normal path에서 `ret`를 사용해야 한다.
`return`은 바깥 named function을 대상으로 추측되지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private let add = { left: Int, right: Int => left + right }
private let ready = { => true }
```

첫 closure는 두 parameter를 명시한다.
둘째 closure는 명시적인 zero-parameter arrow를 사용한다.

### 11.3 implicit `@`

implicit `@` body는
call shape와 non-lambda 인수만으로
정확히 하나의 one-parameter callable type을
독립적으로 선택한 뒤 한 번 검사한다.

후보가 둘 이상이면
각 후보에 body를 대입해 가장 잘 맞는 것을 고르지 않는다.
parameter가 0개나 2개인 expected callable에도
implicit `@`를 적용하지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private let names = users ~ map { @.name }
```

이 형식은 `map`의 callback formal이
독립적으로 정확히 one-parameter callable로 선택된 경우에만
검사할 수 있다.

### 11.4 trailing closure

ordinary call은 괄호를 사용한다.
bounded 예외는
정확히 하나의 atomic argument 뒤 trailing-closure group이 붙는
형식이다. ordinary call과 message call은 같은 group 구조를 쓴다.

- closure 1개: unnamed 또는 named.
- closure 2개 이상: 모든 closure가 named이고 label이 서로 달라야 한다.
- labeled closure: 같은 visible label의 function-typed formal과 결합.
- unlabeled closure: ordinary channel binding 뒤 정확히 하나의 trailing
  function formal이 남을 때만 결합.
- 어떤 형식도 default parameter를 건너뛰거나 formal 순서를 재배열하지
  않는다.

trailing closure는
capture, ownership, effects, throws, isolation, cleanup 검사를
완화하지 않는다.
overload가 모호하면 return type이나 source order가
winner를 만들지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private let labels = users ~ map { user => user.name }

private let value = transaction()
    onCommit:{ => recordCommit() }
    onRollback:{ error => recordRollback(error) }
```

첫 호출은 하나의 trailing closure다.
둘째 호출은 callback이 둘이므로 모두 정적 named label을 사용한다.
`transaction(onCommit: { ... })` 같은 ordinary named argument와
`transaction() onCommit:{ ... }` 같은 named trailing closure는 CST에서
서로 다른 source owner지만, call matching 뒤에는 같은 formal identity를
가리킬 수 있다.

closure body의 brace가 닫힌 뒤 다음 postfix가 나오면 그 postfix는
완성된 call 결과에 붙는다. line break와 indentation은 formatter cue일
뿐 attachment authority가 아니다.

### 11.5 capture 획득과 환경 책임

borrow capture는 source region 밖으로 escape할 수 없다.
inout capture는 exclusive하며 겹치지 않는다.
move capture는 source owner를 closure environment로 이전한다.
resource capture는 모든 종료 path를 합쳐
정확히 하나의 cleanup owner를 가져야 한다.

`copy`는 현재 admitted bit/value-copy 책임이 있을 때만
source를 유효하게 남기고 environment value를 만든다.
`clone`은 하나의 명시적으로 선택된 `Clone` witness를 호출하므로
그 witness의 Error와 EffectRow를 capture acquisition에 보존한다.
`deep`은 별도의 deep-copy profile/evidence를 요구하며,
checker가 field를 재귀적으로 훑어 cloneability를 추측하지 않는다.

capture-level `once`는 owner를 environment로 옮기고
해당 environment field의 읽기를 one-shot으로 만든다.
closure 전체의 call-right를 소비하는 callable profile `#once`와
서로 다른 descriptor field이므로 어느 하나가 다른 하나를
자동 생성하지 않는다.

capture item은 왼쪽에서 오른쪽으로 획득한다.
environment commit 전 clone/deep acquisition이 실패하면
이미 얻은 temporary를 역순 cleanup하고
부분 closure를 publish하지 않으며 아직 commit되지 않은 source
owner를 보존한다. 이 규칙은 current design-static law이고
제품 실행은 `NOT_RUN`이다.

## 12. callable profile과 책임

callable은 단순히 parameter와 result만 갖지 않는다.
현행 compatibility는 다음 축을 보존한다.

- lifetime: ordinary 또는 허용된 `#scoped`
- call-right: repeatable 또는 `#once`
- environment receiver: shared 또는 `#mut`
- behavior: ordinary, `#pure`, `#guard`
- throws ErrorSet
- EffectRow
- suspension
- isolation
- cancellation responsibility
- capture ownership
- cleanup responsibility

`#pure`는 `throws Never`, `effects {}`,
무중단, 무권한, mutable/resource capture 없음이 필요하다.
그렇다고 totality, determinism, CTFE 가능성,
allocation freedom까지 자동으로 증명하지 않는다.

`#guard`는 terminating, nonsuspending,
nonconsuming pure Bool callable이다.
하지만 `def#guard`를 호출했다는 사실만으로
flow narrowing fact가 생기지 않는다.
정본이 허용한 inline R0 predicate만
true edge에 유한 proof fact를 더할 수 있다.

`#once` callable은 첫 invocation attempt에서
call-right를 원자적으로 소비한다.
두 번째 attempt는 거부된다.
capture-level mode와 callable-level right는
서로 다른 descriptor field다.

## 13. catch 판정

### 13.1 정확 문법

```ebnf
TryStmt      ::= "try" Block
                 (CatchClause+ FinallyClause? | FinallyClause) ;
CatchClause  ::= "catch" Pattern? Block ;
FinallyClause ::= "finally" Block ;
```

문법은 `CatchClause+`를 허용한다.
그러나 현행 최소 의미는
일반적인 runtime pattern-dispatch chain이 아니다.

### 13.2 허용되는 catch pattern

catch pattern은 다음 중 하나여야 한다.

- 단순 binder
- wildcard
- checker가 해당 error residual 전체에서
  irrefutable임을 증명한 transactional Pattern

refutable pattern을 runtime에서 순서대로 시험하고
다음 catch로 fallthrough하는 의미는 현행이 아니다.
refutable catch는 MIR 전에 거부된다.

첫 catch가 irrefutable이면
뒤 catch는 statically unreachable이며
새 fallthrough route를 만들지 않는다.
처리되지 않은 Error는 `finally`를 정확히 한 번 거친 뒤 전파된다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private def load() -> Unit
    throws IOError
= {
    try {
        readAll()
    } catch error {
        report(error)
    } finally {
        releaseTemporaryState()
    }
}
```

`error`는 residual 전체를 받는 binder다.
`finally`는 정상 완료와 catch 완료,
그리고 전파되는 실패에서 각각 정확히 한 번 실행된다.

### 13.3 refutable catch 경계

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private def invalidCatch() -> Unit
    throws IOError
= {
    try {
        readAll()
    } catch IOError::permissionDenied(path) {
        report(path)
    }
}
// 현행 최소 catch는 refutable runtime dispatch를 만들지 않는다.
```

variant별 error dispatch가 필요하다면
irrefutable binder로 Error를 받은 뒤
body 안의 현행 `match` owner에서 명시적으로 분기한다.
이 방식은 catch selection과 pattern match의 의미 owner를
혼합하지 않는다.

## 14. 평가, commit 및 cleanup

### 14.1 정확히 한 번 평가

호출의 receiver와 argument expression은
정본이 별도 short-circuit를 정하지 않는 한
왼쪽에서 오른쪽으로 정확히 한 번 평가된다.

positional unfold source와 named unfold source도
각각 한 번 평가된다.
그 결과의 element 또는 static label projection이
source order로 공급된다.

### 14.2 pre-call 책임

호출 전에는 다음 임시 책임이 존재할 수 있다.

- 평가된 owned argument
- live shared borrow
- exclusive inout region
- move 예정 source place
- context value
- borrowed witness evidence
- unfold에서 생성된 temporary

shape 또는 type admission이 정적으로 실패하면
runtime 평가 자체가 없다.
runtime argument 평가가 실패하면
아직 commit되지 않은 move owner를 소비하지 않고,
이미 초기화된 temporary를 정해진 역순으로 정리해야 한다.

### 14.3 call commit

정본이 move 또는 owner transfer를 요구하는 호출은
하나의 명시적 commit 경계를 가진다.
commit 전 실패는 source owner를 보존한다.
commit 성공 뒤에는 callee 또는 새 owner가
정확히 한 번 cleanup 책임을 얻는다.

ordinary borrow는 owner를 넘기지 않는다.
inout은 한 dynamic call extent의 exclusive access이며
겹치는 borrow/inout을 허용하지 않는다.
live borrow나 inout이 suspension, task escape,
actor transfer, return, storage를 건너려면
별도의 admitted proof가 있어야 한다.

### 14.4 effect와 error

호출의 observed EffectRow와 recoverable ErrorSet은
선택된 callable signature에 남는다.
context capability나 witness 전달이
effect 또는 error를 지우지 않는다.

Defect와 Cancellation은 ErrorSet과 별도다.
호출이 suspend할 수 있는지도 callable responsibility의 일부다.
cleanup은 normal return, Error, Defect,
Cancellation의 terminal path에서 건너뛸 수 없다.

## 15. 단계별 worked trace

다음 설명용 예제는
named argument, context, witness, lambda,
effect/error 책임이 한 호출에 함께 있을 때의
정적 판정 순서를 보여 준다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private def transform<T>(
    context environment: RenderEnvironment,
    value: T,
    using display: witness Display<T>,
    apply: (T) -> String,
) -> String
    throws RenderError
    effects {render}
= {
    return apply(value)
}

private let text = transform(
    context renderEnvironment,
    value: user,
    using userDisplay,
    apply: { item: User => item.name },
)
```

판정은 다음처럼 진행된다.

1. `transform` declaration identity를 lexical/module graph에서 찾는다.
2. argument를 context, named value, witness, named lambda로 분류한다.
3. 모든 label이 유일하고 visible formal에 정확히 결합되는지 확인한다.
4. `context renderEnvironment`를 context formal에만 결합한다.
5. `using userDisplay`가 ordinary value가 아니라
   허용된 explicit evidence인지 검사한다.
6. non-lambda `user`가 generic `T`에 주는 지역 제약을 검사한다.
7. 후보가 독립적으로 하나가 된 뒤
   `apply` lambda를 `(T) -> String` expected callable로 한 번 검사한다.
8. `RenderError`와 `{render}` 책임이 caller 문맥에서 허용되는지 검사한다.
9. capture, ownership, suspension, cleanup 책임을 검사한다.
10. 선택한 declaration, label row, context/evidence identity를 HIR에 고정한다.
11. runtime에서는 인수를 소스 순서대로 정확히 한 번 평가한다.
12. 호출이 실패하면 확정된 Error/cleanup 규칙을 따른다.

이 예제는 특정 Display 또는 RenderEnvironment Prelude 항목을
새로 표준화하지 않는다.
핵심은 채널과 판정 순서다.

## 16. 양성·음성·경계 예제

### 16.1 정적 tuple unfold

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private def pair(left: Int, right: Int) -> Int = {
    return left + right
}

private let items = (20, 22)
private let answer = pair(*items)
```

tuple arity가 정적으로 2이므로
남은 fixed formal 수와 정확히 일치한다.

### 16.2 runtime Sequence에서 fixed formal 공급

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private def invalid(values: List<Int>) -> Int = {
    return pair(*values)
}
// Sequence의 runtime 길이는 fixed formal arity evidence가 아니다.
```

`values`가 실행 중 두 원소일 수 있다는 사실은
정적 admission을 만들지 않는다.

### 16.3 Map을 named call unfold로 사용

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private let options = #map{ "timeout": 30 }
private let response = request(**options)
// Map key는 runtime 값이므로 static argument label을 만들 수 없다.
```

named unfold에는 canonical Record 또는
정본이 허용한 static ProjectionRow가 필요하다.

### 16.4 context를 ordinary argument로 대체

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private let text = readConfig(fileAccess, "app.conf")
// context formal은 `context fileAccess` 채널로만 공급한다.
```

타입이 같아 보여도 ordinary positional value는
context role을 채우지 않는다.

### 16.5 witness를 저장하려는 경우

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def keepEvidence(using order: witness Ord<Int>) -> Unit = {
    let saved = order
}
// explicit witness는 first-class storable value가 아니다.
```

evidence identity는 checker와 API/MIR handoff에 남지만,
일반 runtime payload로 바뀌지 않는다.

### 16.6 implicit lambda ambiguity

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
private let result = ambiguousMap(source, { @.name })
// non-lambda call shape만으로 callback type 하나가 선택되지 않으면 거부한다.
```

checker는 lambda body를 여러 overload에 시험해
우연히 맞는 후보를 고르지 않는다.

### 16.7 return type overload

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private let value: Int = parse("42")
// 같은 인수 모양의 parse overload를 반환 타입만으로 고를 수 없다.
```

실제 프로그램은 selector를 한정하거나
서로 다른 argument shape를 사용해야 한다.

### 16.8 local function capture

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def outer(base: Int) -> Int = {
    [borrow base] def add(delta: Int) -> Int = {
        return base + delta
    }
    return add(1)
}
```

local function은 outer local을 명시적으로 capture한다.
borrow region보다 오래 escape하면 거부된다.

### 16.9 암시적 local capture

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def invalidOuter(base: Int) -> Int = {
    def add(delta: Int) -> Int = {
        return base + delta
    }
    return add(1)
}
// outer local `base`가 capture list에 없다.
```

lexical name lookup이 성공할 수 있다는 사실과
capture admission은 별도 판정이다.

## 17. 진단 우선순위

같은 소스에 여러 문제가 보이더라도
checker는 안정적인 primary diagnostic을 선택해야 한다.
호출 관련 권장 판정 계층은 정본 계약에 맞춰
다음과 같이 읽는다.

1. lexical/parser owner 오류
2. source role 및 visibility 오류
3. 이름 없음 또는 정적 lookup ambiguity
4. call-shape 오류
5. duplicate/unknown label
6. context/witness channel 오류
7. unfold source/arity 오류
8. generic kind 또는 constraint 오류
9. ordinary argument type 오류
10. lambda expected-type 오류
11. ownership/capture/escape 오류
12. effect/error/suspension/isolation 오류
13. 남은 overload ambiguity

Trait-qualified associated static과 capability owner에는 다음 deterministic
dispatch를 적용한다.

| 실패 조건 | primary diagnostic | 뒤 단계 |
|---|---|---|
| generic `T::item`으로 Trait requirement를 요구 | `TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION` | exact `<T as Trait>::item`을 쓰기 전까지 중단 |
| exact selected Trait에 item 없음 | `TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND` | nominal/extension/provider fallback 없음 |
| type/value/function 문맥과 requirement kind 불일치 | `TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH` | 다른 kind 후보 탐색 없음 |
| HIR/API에 일곱 identity/responsibility 축 미결합 | `TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE` | MIR 생성 없음 |
| lowering/runtime이 static selection을 다시 검색 | `TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN` | 실행 fallback 없음 |
| 외부 helper/extension/conformance가 nominal private construction 권한 요구 | `TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN` | owner-local 공개 factory 경계 필요 |
| associated value가 immutable/static-safe profile 위반 | `ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED` | 해당 binding은 후보가 아님 |
| type/Trait 이름을 runtime companion value로 사용 | `COMPANION_OBJECT_NOT_CURRENT` | explicit runtime owner 필요 |

여러 조건이 겹치면 가장 이른 owner/qualification/kind/admission 실패를
primary로 삼는다. 예를 들어 `T::cache`가 mutable associated value를
의도했더라도 먼저 explicit Trait qualification 부재를 진단한다. 사용자가
`<T as CacheTrait>::cache`로 고친 다음에야 value profile을 검사한다.

이 목록은 새로운 diagnostic ID를 정의하지 않는다.
정확한 ID와 predicate 관계는
[`spec/diagnostics`](../../spec/diagnostics)와
생성된 진단 부록을 따른다.

한 단계가 실패하면
뒤 단계가 임의 후보를 골라 다른 오류로 바꾸지 않는다.
특히 call shape가 실패한 뒤
lambda body type error를 primary로 내는 방식은
불안정한 후보 선택을 노출할 수 있다.

## 18. 상호작용

### 18.1 pattern과 parameter

ordinary parameter는 identifier-only다.
body 안의 `if let`, guarded `let`, `match`는
각자의 Pattern owner에서 refutable destructuring을 수행한다.
parameter grammar가 Pattern을 받지 않는 경계는
호출 shape를 정적으로 닫게 한다.

### 18.2 effect capability

named capability declaration은
effect를 수행하지도 권위를 자동 부여하지도 않는다.
필요한 operation은 capability를
explicit context channel로 받는다.
callable의 EffectRow는 여전히 signature에 남는다.

### 18.3 extension과 witness

extension activation은 `use`의 정적 범위 효과다.
witness는 conformance graph의 evidence identity다.
한쪽의 존재가 다른 쪽 후보를 합성하지 않는다.
같은 selector가 두 domain에서 경쟁하면
정본의 명시적 lookup tier와 ambiguity 규칙을 따른다.

### 18.4 async와 lambda

이름 있는 `def#async`는 current다.
ordinary lambda invocation은 synchronous다.
일반 async callable literal은 nonactivatable Preview design이며,
ordinary closure에 `await`가 나타났다는 이유로
implicit async conversion을 만들지 않는다.

### 18.5 actor와 call channel

actor message는 `~` suffix를 사용하며
ordinary call/method fallback이 아니다.
selector path는 AST/HIR에 보존되고 admission 전에 actor/protocol
domain의 exact identity로 결정된다. message에는 0/1 payload aggregate가
있고 Tuple/Record payload가 handler value formal에 투영된다.
context 또는 witness argument가 있더라도
actor isolation과 message ownership transfer를 완화하지 않는다.
message trailing closure가 isolation을 건너면 그 closure environment가
별도로 transfer/capture/suspension/effect/error/cleanup 검사를 통과해야
한다.

### 18.6 cleanup

argument evaluation 중 만든 temporary,
closure capture environment,
resource parameter는
호출 성공·실패·Cancellation의 cleanup plan에 포함된다.
이름 해석과 overload 선택은 cleanup을 실행하지 않지만,
선택된 callable responsibility가
MIR cleanup region을 결정하는 입력이 된다.

### 18.7 함수 `scope#static`과 Class Preview의 분리

이름 있는 허용 동기 함수 body의 `scope#static { ... }`은 Stable
`FunctionStaticOwnerId` activation이다. exact
`CallableImplementationId + normalized specialization`마다 최초 실제
호출에서 한 번 판정되며, argument/default staging 뒤 기존
`ownership_commit` 앞에 놓인다. caller 입력을 읽거나 effect, suspension,
resource/authority, 다른 activation dependency를 숨길 수 없다.

Class body의 `scope#static`은 이 규칙의 단순한 receiver 확장이 아니다.
그 표면은 `PREVIEW_NONACTIVATABLE`이고 current source acceptance,
AST/HIR/MIR operation 수가 0이다. resolver는 Class 이름을 함수 static
owner나 persistent cache로 재사용하지 않으며 새 `CALL_INPUT_COMMIT`
event도 만들지 않는다.

## 19. 미폐쇄 의미를 읽는 법

이 장에는 문법 또는 Stable design identity가 존재하지만
세부 product algorithm이 닫히지 않은 항목이 있다.

- generic inference solver 세부
- `mut` parameter와 `mut T`의 완전한 ownership law
- `clone`, `deep`, `copy`, capture-level `once`
- 일반 async callable literal
- runtime refutable catch dispatch

앞의 세 항목은 일부 Stable design surface를 가지지만 product-unbound다.
뒤의 두 항목은 현행 current 의미로 활성화되지 않는다.
이 차이를 “파서가 토큰을 볼 수 있다”는 이유로 합치면 안 된다.

미폐쇄 의미에 대해 구현자가 취할 수 있는 안전한 행동은
다음뿐이다.

1. 닫힌 subset만 수용한다.
2. 정본의 active diagnostic으로 거부한다.
3. product receipt 없이 지원을 주장하지 않는다.
4. 새 의미가 필요하면 별도 승인된 design action에서
   grammar, checker, MIR, API, migration을 함께 닫는다.

## 20. 제품 증거 경계

이 장의 알고리즘과 예제는
설계 정적 설명이다.
현재 다음 제품 증거는 모두 `NOT_RUN`이다.

- production scanner
- production parser
- integrated name resolver
- generic inference checker
- call-shape checker
- ownership/effect checker
- HIR/MIR lowering
- xVM runtime
- LLVM AOT backend
- LLVM ORC backend
- formatter
- LSP
- public API compatibility runner
- actual user/team study
- independent conformance

정적 predicate row,
accepted example corpus,
generated coverage index가 존재해도
target-bound execution receipt를 대신하지 않는다.
특히 generic design seed를 product solver PASS로,
call-shape 설명을 backend call ABI PASS로,
문서 예제를 runtime success로 읽어서는 안 된다.

## 21. 구현 및 검토 체크리스트

이름·추론·호출 변경을 검토할 때는
적어도 다음 질문에 답해야 한다.

1. token owner가 exact grammar와 일치하는가.
2. source role이 하나로 확정되는가.
3. path가 정적 identity로 닫히는가.
4. visibility closure를 통과하는가.
5. lexical, member, extension, witness 도메인이 섞이지 않는가.
6. runtime String lookup이 정적 identity를 대신하지 않는가.
7. argument channel이 각각 보존되는가.
8. positional unfold arity evidence가 충분한가.
9. named unfold가 static label row인가.
10. Map key를 argument label로 바꾸지 않는가.
11. context가 explicit channel로 공급되는가.
12. witness가 explicit nonescaping evidence인가.
13. return type과 source order가 tie-breaker가 아닌가.
14. lambda를 한 expected callable에 한 번만 검사하는가.
15. generic kind와 occurs check를 보존하는가.
16. 익명 Union이나 hidden generic을 만들지 않는가.
17. ownership/capture/cleanup 책임이 signature에 남는가.
18. effects/errors/cancellation/suspension이 서로 분리되는가.
19. catch가 refutable runtime dispatch로 확장되지 않는가.
20. HIR/MIR가 lookup 결과를 고정하고 재검색하지 않는가.
21. product support가 receipt 범위를 넘지 않는가.
22. 네 capability domain이 selector 철자와 owner 단계에서 분리되는가.
23. generic associated static이 `<T as Trait>::item`으로 exact Trait를
    지정하는가.
24. associated item의 type/value/function kind가 문맥과 맞는가.
25. 일곱 identity/responsibility 축이 lowering까지 보존되는가.
26. associated `let::`가 immutable/static-safe 최소 profile을 만족하는가.
27. owner-private construction authority가 lexical nominal `def::` 밖으로
    전이되지 않는가.
28. companion singleton, type-as-runtime-value, runtime provider fallback
    수가 모두 0인가.
29. 함수 `scope#static` Stable owner와 Class Preview owner가 분리되는가.

## 22. 정본 근거

- [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
  - source root, module/import/use/export
  - type parameter와 type argument
  - parameter, argument, closure, catch productions
- [`spec/language.md`](../../spec/language.md)
  - visibility, lexical/local function, lookup
  - callable identity, inference 금지 경계
  - context/witness와 진단
- [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
  - parser owner, visibility admission, lookup domain
- [`spec/types/type-system.md`](../../spec/types/type-system.md)
  - normalization, generic kind, callable compatibility
  - ownership/effects/errors/cancellation 책임
- [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
  - call shape, unfold arity, lambda staging
  - catch minimum과 flow join
- [`spec/contracts/companion-capability-coherence.json`](../../spec/contracts/companion-capability-coherence.json)
  - 네 capability domain, direct Trait-associated static selection
  - associated value admission, private authority와 runtime lookup fence
- [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
  - argument order, fixed identities, cleanup handoff
- [`library/prelude/prelude.md`](../../library/prelude/prelude.md)
  - public signature residue와 evidence/library boundary

이 장과 정본이 충돌하면
상태·권위 장에 적힌 우선순위에 따라
정본 원천이 우선한다.
