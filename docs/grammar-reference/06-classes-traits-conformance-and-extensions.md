# 클래스, 트레이트, 적합성, 확장

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 Deeplus `0.1.2-internal`의 명목 Class, Trait 계약, 명시적
conformance evidence와 lexical extension을 설명한다. 네 관계는 서로
다른 identity와 판정 경로를 가지며, 모양이 비슷하거나 이름이 같다는
이유로 합쳐지지 않는다.

| 영역 | 현행 상태 |
|---|---|
| `final`/`open`/`abstract`/`sealed` Class와 `value`/`resource` flavor | `CURRENT` |
| Class 필드, 생성자, 정리, 접근자, forwarding, dispatch marker | `CURRENT` |
| Trait method/associated requirement와 명시적 conformance | `CURRENT` |
| `Type::item`, `Type::extension::item`, `<T as Trait>::item`의 분리된 정적 capability lookup | `STABLE_DESIGN` |
| 암시적 companion object/singleton 또는 type-name의 runtime value 변환 | 현행 아님; 거부 |
| 함수 body의 `scope#static` activation | `STABLE` |
| Class body의 `scope#static` activation | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 현재 소문자 `via` conformance route | `CURRENT` |
| named extension set/pack과 lexical activation | `CURRENT` |
| sealed Class constructor-pattern 또는 Class 내부 분해 pattern | 현행 아님 |
| 미래 `VIA`/`AUTO`, specialization, 자식 로컬 parent witness replacement | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 임의 custom operator declaration | 현행 아님; 거부 및 recovery/no-go 진단만 유지 |
| fixed glyph Trait conformance overloading | `STABLE_DESIGN` (`+`, `-`, `*` 제한 프로필) |
| 제품 parser/checker/MIR/runtime/formatter/LSP | `NOT_RUN` |

문서의 정적 예제는 제품 실행이 아니다. Trait Conformance의
`TCC-P1-002..008`은 정확히 7개 모두 OPEN인 상태를 유지하며 이 장은
어떤 P1도 폐쇄하지 않는다. product lane은 모두 `NOT_RUN`이다.

## 문법

### Class 선언

```ebnf
ClassDecl ::= OrdinaryClassDecl | DataClassDecl

OrdinaryClassDecl ::= TopLevelVisibility? ClassFlavor?
                      ClassModifierSequence? "class" Identifier
                      TypeParameterList? ParameterList?
                      InheritanceClause? WhereClause?
                      CleanupBudgetClause? ClassBody

DataClassDecl ::= TopLevelVisibility? "data" "class" Identifier
                  TypeParameterList? ParameterList?
                  InheritanceClause? WhereClause?
                  CleanupBudgetClause? ClassBody?

ClassFlavor           ::= "value" | "resource"
ClassModifierSequence ::= "final" | "open" | "abstract" | "sealed"
                        | "abstract" "sealed"
InheritanceClause     ::= ":" TypeRef
ClassBody             ::= "{" MemberDecl* "}"
```

구체 Class는 modifier를 쓰지 않아도 의미상 final이다.

- `final class`: subclass를 허용하지 않는 구체 Class.
- `open class`: 명시적으로 subclass를 허용.
- `abstract class`: 직접 구성할 수 없음.
- `sealed class`: module contract가 정한 sealed family scope 안에서만
  direct subclass를 선언.
- `abstract sealed class`: 직접 구성할 수 없는 닫힌 family root.

`value`와 `resource`는 책임 flavor이다. 이것만으로 equality, hashing,
ordering, display, clone, serialization 또는 Trait evidence가 합성되지는
않는다.

문법의 optional visibility는 lossless parse/recovery를 위한 구조다.
현행 type declaration admission은 `private`, `common`, `public` 중 하나의
정확한 visibility를 요구한다. `private`는 module-local, `common`은
package-wide이지만 외부 export 불가, `public`은 적법한 export/module
interface를 통해서만 외부 API 후보가 된다.

### Class member와 dispatch marker

```ebnf
MemberDecl ::= FieldDecl
             | MemberFunctionDecl
             | ConstructorDecl
             | CleanupDecl
             | TypeSideFieldDecl
             | TypeSideMemberFunctionDecl
             | AccessorPropertyDecl
             | ForwardDecl

FieldDecl ::= MemberVisibility? ("let" | "var") Identifier
              TypeAnnotation? Initializer? StatementBoundary

MemberFunctionDecl ::= MemberVisibility? DefIntroducer Identifier
                       ClassDispatchMarker FunctionRest

ClassDispatchMarker ::= "." | "+" | "*." | "*+"

ConstructorDecl ::= MemberVisibility? "def" "!" Identifier ParameterList
                    ConstructorSignatureTail?
                    ConstructorDelegationClause? "=" Block

ForwardDecl ::= MemberVisibility? "forward" ForwardMemberSpec
                "to" Expr StatementBoundary
```

member visibility는 `+`(공개), `-`(private), `#`(subclass/family 범위)
domain이다. stored field는 nonvirtual이며 dispatch marker를 쓰지 않는다.
Class-like instance method는 이름 뒤에 정확히 하나의 marker를 둔다.

| marker | Class dispatch 의미 |
|---|---|
| `.` | final slot |
| `+` | open slot |
| `*.` | override하고 닫음 |
| `*+` | override하고 계속 open |

따라서 `+def value.()`에서 앞의 `+`는 member visibility이고,
`value` 뒤의 `.`은 Class dispatch이다. 둘을 한 의미로 합치지 않는다.
type-side field/method는 `let ::name`, `def ::name` 형태로 별도 identity를
갖는다.

`AccessorPropertyDecl`의 프로퍼티 헤더에는 member visibility sigil을
붙이지 않는다. 접근자 가시성이 필요하면 개별 `get` 또는 `set`에
`+`, `-`, `#`를 붙인다.

constructor는 `def! name(...)`으로 선언하고 외부에서는 기본
constructor를 `Type!(...)`, named constructor를 `Type!name(...)`으로
호출한다. delegation은 같은 타입의 `name(...)` 또는
`super!name?(...)`을 사용하며 construction session의 단일 commit
owner를 보존한다.

### Trait와 associated requirement

```ebnf
TraitDecl ::= TopLevelVisibility? "trait" Identifier
              TypeParameterList? SuperTraitClause? TraitBody?
SuperTraitClause ::= "requires" TraitReferenceList

TraitItem ::= TraitMethodDecl
            | AssociatedRequirementDecl
            | LawDecl

TraitMethodDecl ::= MemberVisibility? DefIntroducer Identifier
                    TraitWitnessMarker TypeParameterList?
                    ParameterList TraitFunctionTail

TraitWitnessMarker ::= "." | "+" | "*." | "*+"

AssociatedTypeRequirementDecl ::= "type" Identifier
                                  AssociatedTypeConstraintList?
                                  StatementBoundary
AssociatedValueRequirementDecl ::= "let" "::" Identifier
                                   TypeAnnotation StatementBoundary
AssociatedFunctionRequirementDecl ::= "def" "::" Identifier ParameterList
                                      ReturnClause? ThrowsClause?
                                      EffectsClause? StatementBoundary
```

Trait method의 marker는 Class marker와 glyph를 공유하지만 AST와 identity
domain은 `TraitWitnessKind`이다. associated type/value/non-method function은
method witness marker를 얻지 않는다. supertrait는 `requires` 뒤에
명시한다.

### Associated selector와 companion capability 분해

Deeplus는 다른 언어의 단일한 “companion object” 개념으로 정적 기능을
묶지 않는다. 명목 타입 소유 기능, 이름 붙인 extension 기능, Trait
associated 기능, 실행 중 상태를 가진 서비스는 서로 다른 owner와
수명·가시성·identity를 갖는다. 문법도 이 차이를 지우지 않는다.

```ebnf
TraitQualifiedAssociatedSelector ::=
    "<" TypeRef "as" QualifiedTypeReference ">" "::" Identifier

AssociatedProjection ::= TraitQualifiedAssociatedSelector

QualifiedStaticExpr ::= StaticQualifier "::" Identifier
                      | TraitQualifiedAssociatedSelector

StaticQualifier ::= QualifiedTypeReference | AssociatedProjection
```

`TraitQualifiedAssociatedSelector`는 문맥에 따라 정확히 한 kind로
판정된다.

- type 문맥의 `<T as Trait>::Item`은 associated type projection이다.
- expression 문맥의 `<T as Trait>::value`는 associated immutable value다.
- expression 문맥에서 CallSuffix가 이어지는
  `<T as Trait>::make(...)`는 associated function 선택 후의 보통 호출이다.
- `<T as Trait>::Item::member`는 먼저 associated type을 하나로 정규화한
  뒤 그 결과 타입의 nominal type-side domain에서 `member`를 찾는다.

같은 token sequence를 여러 kind로 동시에 후보화하지 않는다. 선택된
requirement의 선언 kind가 문맥과 다르면
`TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH`이고, 다른 이름 공간으로
fallback하지 않는다.

| capability domain | canonical surface | 찾는 대상 | 찾지 않는 대상 |
|---|---|---|---|
| nominal type-side | `Type::item` | 해당 명목 owner의 `let::`/`def::`, 해당 namespace가 소유한 Enum case | Trait associated item, extension, runtime service |
| named type-side extension | `Type::extension::item` | 정확히 이름 붙은 extension set의 item | nominal fallback, Trait witness, owner-private authority |
| Trait-qualified associated static | `<T as Trait>::item` | 선택된 conformance가 결합한 associated type/value/function | 보이는 다른 Trait, nominal/extension fallback, runtime provider |
| explicit runtime owner | `service.item(...)` 같은 ordinary value expression | 명시적으로 구성·주입한 service, Actor handle, shared-state owner | type token, 암시적 singleton, 저장 가능한 witness |

따라서 generic `T`에 여러 Trait가 보이더라도 `T::item`은 Trait를
검색하지 않는다. Trait item을 원하면 항상 `<T as Trait>::item`을 쓴다.
“현재 보이는 Trait가 하나뿐”이라는 우연한 사실도 단축 표면을 허용하지
않는다. 이 규칙은 새 Trait import가 기존 `T::item`의 의미를 바꾸는
취약성을 차단한다.

#### 선택 identity와 lowering residue

`<T as Trait>::item`의 정적 판정은 다음 순서로 닫힌다.

1. `T`, `Trait`, `item`의 source identity와 visibility를 판정한다.
2. `T`와 generic substitution을 정규화한다.
3. exact Trait에 대한 visible compatible conformance를 하나로 선택한다.
4. selected Trait requirement에서 `item`과 선언 kind를 확인한다.
5. conformance body의 exact implementation binding을 확인한다.
6. `TraitId`, `RequirementId`, `ConformanceId`, `TraitWitnessId`,
   `ImplementationId`, normalized substitution(`SubstitutionId`),
   responsibility(`ResponsibilityId`)의 일곱 축을 HIR/API residue에
   결합한다.
7. 값 사용 또는 호출의 타입·ownership·effect·error 계약을 검사한다.
8. MIR lowering은 이 결정을 소비할 뿐 다시 이름·provider·registry를
   검색하지 않는다.

일곱 identity/responsibility 축 중 하나라도 소실되면
`TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE`다. source/import/link
순서, 메모리 주소, runtime registration 순서와 expected return type은
identity 입력이나 tie-breaker가 아니다.

#### Associated `let::`의 최소 값 profile

초기 Stable associated value profile은 의도적으로 작다. `let::` binding은
다음을 모두 만족해야 한다.

- const-evaluable이거나 정적으로 재현 가능한 materialization이다.
- 값은 immutable이고, 내부 graph도 deeply immutable이거나 명시적으로
  `Shareable`이다.
- 초기화는 pure, synchronous이며 safe publication이 가능하다.
- `Resource`, drop/finalizer, unload 책임을 소유하지 않는다.
- ambient authority, escaping borrow, cycle을 만들지 않는다.
- persistent mutable cache, runtime registry, 수명이 정의되지 않은
  allocation을 숨기지 않는다.

`var::`는 이 profile에 들어오지 않는다. 상태 있는 factory, cache,
provider가 필요하면 explicit ordinary value, Actor 또는 shared-state
owner로 모델링한다. “type마다 하나”라는 설명만으로 숨은 singleton
수명과 동시성 규칙을 합성하지 않는다.

#### Nominal owner와 private construction authority

명목 owner body에 lexical하게 선언된 `def::`만 그 declaring owner의
private constructor와 private representation에 접근할 수 있다. 이 권한은
선언 위치에서 생기는 owner-local authority이지 `::` glyph 자체가 주는
권한이 아니다.

다음은 모두 ordinary visibility만 가진다.

- top-level qualified type-side function;
- named type-side extension function;
- 외부 conformance의 associated function;
- 같은 module/package에 우연히 놓인 helper.

이들이 private constructor에 접근하거나 nominal `def::` identity로
위장하면 `TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN`이다.
conformance의 `def::`는 Trait requirement implementation이지 nominal
type-side member를 추가하는 선언도 아니다.

### 선언적 `law`의 정확한 범위

`law`는 실행할 함수가 아니라 Trait·conformance·bitfield 계약에 붙는
순수 선언적 tooling metadata다. 정확한 공통 production은 다음과 같다.

```ebnf
LawDecl      ::= "law" Identifier LawBody? StatementBoundary
LawBody      ::= "{" LawBodyItem* "}"
LawBodyItem  ::= LawAssertion StatementBoundary
LawAssertion ::= ("requires" | "ensures" | "invariant")? PredicateExpr
```

body를 생략하면 이름이 있는 계약 항목만 선언한다. body가 있으면 각
항목은 `requires`, `ensures`, `invariant` 중 하나를 명시하거나 맨
Predicate를 쓸 수 있다. 이 세 단어는 여기서 실행 순서를 만드는 statement
introducer가 아니라 assertion의 역할을 분류한다. `LawAdmission`은
`PredicateExpr`가 현재의 restricted pure logic subset인지 정적으로
검사한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
trait ReflexiveRelation {
    law Reflexive {
        requires true
        ensures true
        invariant 1 == 1
    }
}
```

위 law는 세 assertion의 역할, predicate text와 source identity를
보존하지만 호출 가능한 method, runtime branch 또는 proof body를 만들지
않는다. 실제 law가 이름을 참조한다면 그 이름은 enclosing owner의 정상
정적 name-resolution으로 먼저 결합되어야 하며 law가 암시적 변수를
합성하지 않는다. checker와 공식 tooling은 이 text에 property-generation
evidence를 결합할 수 있다. 그러나 evidence가 없다는 사실은 law의
문구를 바꾸거나 law를 자동 폐쇄·삭제하지 않는다. 반대로 evidence가
있다는 사실도 conformance method나 witness를 합성하지 않는다.

Law body는 ordinary statement block이 아니므로 mutation, I/O, `await`,
`spawn`, `throw`, arbitrary call과 실행 cleanup을 넣을 수 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
trait InvalidAudit {
    law BadLaw {
        print("not a proposition")
    }
}
// LAW_BODY_ITEM_NOT_ADMITTED
```

거부된 item은 assertion residue나 MIR event를 만들지 않는다. 허용된
law도 executable MIR로 낮아지지 않으며 xVM·LLVM·제품 실행 PASS를
주장하지 않는다. 향후 conformance proof block은 별도 Preview authority가
필요하고, 현재 Stable law declaration을 proof 실행 표면으로 재해석할 수
없다.

### Conformance와 evidence

```ebnf
ConformanceDecl ::= TopLevelVisibility? "conformance" TypeRef
                    "conforms" QualifiedTypeReference
                    NameAliasClause? ConformanceViaClause?
                    WhereClause? ConformanceBody

NameAliasClause    ::= "as" Identifier
ConformanceViaClause ::= "via" QualifiedPath

ConformanceItem ::= ConformanceMethodDecl
                  | TypeSideMemberFunctionDecl
                  | AssociatedRequirementBinding
                  | ExtensionDelegationDecl
                  | LawDecl

AssociatedRequirementBinding ::= "type" Identifier "=" TypeRef
                                  StatementBoundary
                               | "let" "::" Identifier "=" Expr
                                  StatementBoundary
```

`conformance T conforms Trait { ... }`는 checker-visible evidence를
만든다. `as name`은 명시적 conformance 이름이고, 소문자 `via path`는
현행 route 표면이다. 이 `via`는 향후 설계 문서의 대문자 provider
`VIA`나 `AUTO` route와 동일하지 않다.

### 공유 Trait/conformance 보고서와 현행 authority의 조정

공유 설계 보고서에서 제시한 canonical requirement·conformance·witness
identity, 전역 coherence, orphan/overlap 검사, source·import·link order
비의존성, MIR 이후 provider 재탐색 금지는 이미
`TC-R001..R016`과 `TCC-DG-001..008`의 비활성 Preview 계약으로 수용되어
있다. 이 의미 핵심은 새 source spelling이나 제품 지원을 활성화하지 않는다.

현행 source는 계속 `conformance T conforms Trait { ... }`, Trait parent의
`requires`, 소문자 `via`를 사용한다. `type T conforms Trait`, nominal
header의 반복 `conforms`, parent `derives`, `supports auto`와 `by auto`,
`conform Trait { ... }`, local/first-class witness 및 specialization은
현행 문법으로 채택하지 않는다. 이 후보들은 별도 authority 없이는
formatter·LSP·migration 대상도 아니다.

`TCC-P1-002..008`은 정확히 7개 모두 `OPEN`이고 successor는
`NONACTIVATABLE`이다. parser, checker, HIR/MIR, runtime, formatter/LSP를
포함한 제품 실행과 지원 상태는 `NOT_RUN`이다.

### Extension

```ebnf
ExtensionSetDecl ::= TopLevelVisibility? "extension" TypeRef
                     "as" Identifier ExtensionSetBody
ExtensionSetBody ::= "{" ExtensionSetItem* "}"
ExtensionSetItem ::= ExtensionSetFunctionDecl
                   | TypeSideMemberFunctionDecl

ExtensionSetFunctionDecl ::= MemberVisibility? "def" Identifier
                             ParameterList? ReturnClause?
                             ThrowsClause? EffectsClause?
                             WhereClause? FunctionBody

ExtensionPackDecl ::= "extension" "pack" QualifiedPath ExtensionPackBody
```

named extension set은 정적으로 식별되고 `use`/`import`의 lexical 또는
module scope 안에서만 활성화된다. extension 안의 instance function은
plain `def name(...)`이며 Class dispatch 또는 Trait witness marker를
자동으로 얻지 않는다.

## 허용과 정적 의미

### 서로 다른 다섯 관계

checker는 다음 관계를 분리한다.

1. 명목 하위 클래스 관계(subclassing);
2. Trait 적합성(conformance);
3. extension 소속과 활성화;
4. 객체 포함·연관 관계(containment/association);
5. 동적·도구 전용 관점(dynamic/tooling-only view).

subclassing은 unrelated Trait conformance를 자동 생성하지 않는다.
extension도 conformance evidence가 아니며, containment는 subtype edge가
아니다. dynamic/tooling view는 정적 Class/Trait identity를 만들 수
없다.

### Class modifier와 sealed family

서로 배타적인 modifier/flavor 조합은 Class owner admission에서
거부한다. sealed direct subclass는 sealed family scope 안에 있어야
하고, concrete direct child는 자신의 `final` 또는 `open` disposition을
명시해야 한다. exhaustiveness나 subtype 분석이 sealed family closure를
사용할 수는 있지만, 그 사실이 Class constructor-pattern 문법을
합성하지 않는다.

override는 원래 slot을 정확히 가리켜야 한다. 입력 channel, generic,
ownership/isolation/effect/error 계약은 호환 법칙을 따라야 하며 source
order로 winner를 고르지 않는다. forwarding은 finite selector list만
허용하고 wildcard/rename/duplicate/collision을 허용하지 않는다.
forwarding은 subtype, witness, storage 또는 cleanup owner를 만들지 않는다.

### Trait evidence와 coherence

각 ground conformance 선택은 정규화된 target, instantiated Trait 및
coherence authority에 대해 하나의 유일한 evidence/Witness identity를
산출해야 한다. declaration spelling, alias path, source/import/link order가
winner가 될 수 없다.

conformance body는 요구 method, associated binding 및 law를 정확히
충족한다. 같은 glyph를 쓴 Class dispatch와 Trait witness requirement는
서로 다른 identity domain이므로 우연히 대신 충족하지 않는다.
extension member 역시 명시적 `delegate` 계약 없이 Trait requirement를
충족하거나 witness를 만들지 않는다.

현행 소문자 `via`를 사용해도 같은 ground conformance를 별개 의미
conformance로 복제할 수 없다. provider discovery, fallback, priority,
specialization 또는 hidden runtime lookup은 current evidence selection의
일부가 아니다.

### 네 capability domain의 실행 의미

네 domain은 모두 정적 selector처럼 보일 수 있지만 실행 model은 같지
않다.

- nominal `Type::item`은 명목 owner가 선언한 하나의 static declaration을
  가리킨다. type name 자체가 runtime 값으로 materialize되지는 않는다.
- `Type::extension::item`은 exact extension identity와 lexical activation을
  요구한다. 실패해도 nominal 또는 Trait domain으로 이동하지 않는다.
- `<T as Trait>::item`은 이미 선택된 conformance evidence를 통해 exact
  implementation을 고정한다. runtime witness table 순회나 provider lookup은
  0회다.
- explicit runtime owner는 ordinary value이므로 그 값의 ownership,
  isolation, effect, error, cancellation과 cleanup 책임을 그대로 따른다.
  정적 type-side lookup이 이 책임을 숨겨 주지 않는다.

“정적 철자”와 “전역 runtime singleton”은 동의어가 아니다. Deeplus의
capability 분해는 compile-time identity가 필요한 기능과 runtime state가
필요한 기능을 owner 단계에서 분리한다.

### Extension resolution

extension identity에는 declaring set이 들어간다. activation은
compile-time lexical frame이며 block을 벗어나 누출되거나 runtime
loading으로 바뀌지 않는다. nominal member, 활성 extension member,
conformance evidence의 resolution domain은 명시된 규칙대로 검사한다.
충돌 또는 ambiguity를 source/import 순서로 해결하지 않는다.

`~` message selector의 qualified path도 이 identity 분리를 재사용한다.
`receiver ~ SomeTrait::selector`는 receiver의 정적 타입에 대해 이미
유일한 `TraitWitnessId + RequirementId`가 있을 때만 그 witness domain을
지정한다. `receiver ~ Type::ExtensionSet::selector`는 exact
`ExtensionMemberId`와 lexical activation을 지정한다. actor receiver의
`Protocol::selector`는 exact actor-protocol handler/request identity를
지정한다. qualifier가 한 domain을 선택한 뒤 실패하면 다른 domain으로
fallback하지 않으며, 이 표면은 새 conformance, VIA/AUTO,
specialization이나 child-local witness를 만들지 않는다.

### 연산자와 Trait의 경계

현행 operator glyph table과 precedence는 닫혀 있다. primitive와 그 밖의
언어 예약 operand pair는 계속 intrinsic 전용이다. 다만 기존 glyph
`+`, `-`, `*`는 Stable fixed-glyph profile에서 left nominal owner가
제공하는 유일한 `DIRECT_GLOBAL` conformance를 정적으로 선택할 수 있다.
그 밖의 glyph와 임의 operator 철자는 named Trait method 또는 named API로
표현한다.

임의 custom operator declaration은 현행이 아니며 거부된다. 해당 철자는
recovery/no-go 진단에서만 보존되고 Preview activation 후보로 해석하지
않는다. fixed-glyph conformance overloading의 Stable 승급은 기존
`conformance T conforms Trait` 표면과 exact `+`, `-`, `*` mapping만
사용한다. `TCC-P1-002..008`은 제품·실행 검증 항목으로 계속 OPEN이다.

## 평가·소유권·효과

- Class constructor는 argument/delegation을 정해진 순서로 한 번씩
  평가하고 base/storage/post-init 단계를 거친 뒤 성공 시 정확히 한 번
  publish한다. 실패 시 미완성 객체를 publish하지 않고 획득한 책임을
  정리한다.
- `value`/`resource` flavor와 field ownership은 move/borrow/cleanup
  책임을 지우지 않는다. move는 owner를 옮기고 borrow는 owner를 만들지
  않는다.
- virtual Class call은 정적으로 선택된 Class slot domain을 사용한다.
  Trait call은 선택된 witness evidence를 사용한다. runtime에서 extension
  또는 provider를 다시 검색하지 않는다.
- conformance와 associated binding은 MIR handoff 전에 유일하게
  결정되어야 한다.
- extension receiver와 인수는 ordinary call 규칙으로 평가한다.
  lexical activation은 runtime effect가 아니다.
- forwarding receiver는 정확히 한 번 평가하고 인수, effect, error,
  ownership 순서를 보존한다.
- cleanup, error, defect, cancellation과 suspension은 서로 다른
  responsibility axis이며 dispatch가 숨겨서 추가하거나 제거하지 않는다.

## 현행 예제

아래 `accept` 예제는 모두
[`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)의
원문이며 `source_activation: none`,
`certification_status: design_static_product_not_run`이다. 제품 실행은
`NOT_RUN`이다.

### `EX-R49B-SEALED-001` — sealed family

```deeplus
module expr
public sealed class Expr {
}
public final class Literal : Expr {
}
public open class Binary : Expr {
}
```

이 예제는 닫힌 명목 family를 만들지만 `Literal(...)` 같은 constructor
pattern을 허용하지 않는다.

### `EX-R48-045` — Class field와 기본 constructor

```deeplus
public class UserId {
    +let raw: Int

    +def! new(raw: Int)
        : super!()
    = {
        self.raw = raw
    }
}

let id = UserId!(1)
```

### `EX-R48C-083` — 명시적 Trait conformance evidence

```deeplus
public trait Display {
    +def display+() -> String
        throws Never
        effects {}
}

public conformance UserId conforms Display {
    +def display+() -> String
        throws Never
        effects {}
    = {
        return self.raw
    }
}
```

앞의 member visibility `+`와 이름 뒤의 Trait witness marker `+`는
서로 다른 역할이다.

### 명시적 Trait-qualified associated 값과 함수

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
public final class Token {
    +let raw: Int

    -def! privateNew(raw: Int) = {
        self.raw = raw
    }

    +def ::fromInt(raw: Int) -> Token
        throws Never
        effects {}
    = {
        return Token!privateNew(raw)
    }
}

public trait DefaultToken {
    let ::code: Int
    def ::make() -> Token
        throws Never
        effects {}
}

public conformance Token conforms DefaultToken {
    let ::code = 0

    def ::make() -> Token
        throws Never
        effects {}
    = {
        return Token::fromInt(<Token as DefaultToken>::code)
    }
}

private let code = <Token as DefaultToken>::code
private let token = <Token as DefaultToken>::make()
```

`Token::fromInt`는 nominal owner-local `def::`이므로 private named
constructor에 접근할 수 있다. 반면 `<Token as DefaultToken>::make`는
selected conformance의 associated function implementation이며
`Token::fromInt`라는 공개된 nominal 경계를 거친다. 두 함수가 같은
`Token`을 반환해도 owner identity와 private authority는 합쳐지지 않는다.

### Associated type 뒤의 nominal static 선택

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
public final class FileStore {
}

public trait StorageModel {
    type Key
}

public conformance FileStore conforms StorageModel {
    type Key = Token
}

private let emptyKey =
    <FileStore as StorageModel>::Key::fromInt(0)
```

첫 번째 `::Key`는 Trait associated type을 선택하고, 두 번째 `::fromInt`는
정규화된 `Token` 타입의 nominal type-side function을 선택한다.
`StorageModel` 자체나 활성 extension에서 `fromInt`를 다시 찾지 않는다.

### `EX-R48-016` — named extension set과 명시적 selector

```deeplus
public extension Int as metric {
    +def m() -> Length = { return Length!(value: self, unit: Unit::meter) }
}
use Int::metric
let a = 3 ~ m
let b = 3 ~ Int::metric::m
```

extension activation은 compile-time 범위이며 `Int`에 Trait witness나
operator overload를 추가하지 않는다.

### `EX-R51a1-002` — 유일한 현행 sealed 철자

```deeplus
public sealed class Node {
    +def value.() -> Int = { return 1 }
}
```

`value.`의 `.`은 final Class dispatch slot이다.

## 거부되거나 격리된 형식

| 형태 | 처리 |
|---|---|
| modifier 없는 concrete Class를 암묵적으로 open으로 해석 | 거부; 기본은 final |
| sealed family scope 밖의 direct subclass | 거부 |
| sealed direct child의 disposition 생략 | 거부 |
| sealed Class를 constructor pattern으로 분해 | 현행 pattern 문법 없음 |
| `class#sealed` 같은 제거된 철자 | 거부; `sealed class` 사용 |
| stored field에 dispatch marker 부여 | 거부 |
| Class marker와 Trait marker identity를 합침 | 거부 |
| structural shape 또는 extension만으로 conformance 추론 | 거부 |
| extension이 Trait witness를 자동 생성 | 거부 |
| member/extension 충돌을 import/source order로 해결 | 거부 |
| extension을 runtime plugin/provider lookup으로 해석 | 거부 |
| generic `T::item`으로 visible Trait associated item을 암시적으로 검색 | 거부; `<T as Trait>::item` 사용 |
| `<T as Trait>::item` 실패 뒤 nominal/extension/provider로 fallback | 거부 |
| type name을 runtime service value나 metatype singleton으로 변환 | 거부 |
| `companion` object/keyword 또는 hidden per-type singleton | 거부; `COMPANION_OBJECT_NOT_CURRENT` |
| conformance/extension/top-level helper가 nominal owner-private constructor authority 획득 | 거부; `TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN` |
| mutable/cache/resource/ambient-authority associated `let::` | 거부; `ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED` |
| 임의 custom operator declaration | 거부; recovery/no-go 진단만 유지 |
| admitted set 밖의 fixed glyph conformance overload | 거부; Stable 집합은 `+`, `-`, `*`뿐 |
| successor `VIA`/`AUTO`, specialization, fallback 경로 | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 자식/case 로컬 parent witness replacement | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 동적 attach/detach, 일급/로컬 Witness | `PREVIEW_DESIGN_NONACTIVATABLE` |

비활성 설계는 현행 소문자 `via`, 현행 marker 또는 current evidence
selection을 재해석하지 않는다. recovery로 인식된 철자는 admitted
AST/HIR/MIR/API residue를 만들지 않는다.

### 대표 거부 예

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
private def implicitCode<T>() -> Int
    where T conforms DefaultToken
= {
    return T::code
}
// TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION
// 올바른 표면: <T as DefaultToken>::code
```

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
companion Token {
    let cache: SharedCell<Int>
}
// COMPANION_OBJECT_NOT_CURRENT
```

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/companion-capability-coherence.json -->
```deeplus
public trait CachedToken {
    let ::cache: SharedCell<Int>
}

public conformance Token conforms CachedToken {
    let ::cache = SharedCell!(0)
}
// ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED
```

마지막 예는 immutable binding이라는 겉모양만으로 충분하지 않다.
binding이 가리키는 persistent mutable cell과 그 publication/lifecycle이
associated value의 최소 profile 밖이므로 거부한다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### PREVIEW_NONACTIVATABLE — Class successor 계약

Class successor 설계는 current Class syntax를 즉시 바꾸는 제안이 아니라
implementation 전에 정적 identity와 책임을 닫기 위한 후보 계약이다.

**의미**

- 이 Preview의 Class `scope#static`은 현행 함수 body
  `scope#static { ... }`과 다른 미래 owner다. 함수 표면은
  `FunctionStaticOwnerId`에 결합된 `STABLE` activation이고, Class 표면의
  current source acceptance/AST/HIR/MIR 수는 모두 0이다.
- 함수 activation은 최초 실제 invocation에서 argument/default staging 뒤,
  기존 `ownership_commit` 앞에 수행되는 caller-input-free한 동기
  initialization이다. persistent type value cache나 Class-wide barrier가
  아니다. Class Preview가 이 의미를 빌리거나 새 `CALL_INPUT_COMMIT`
  event를 발명하지 않는다.
- versioned Class responsibility descriptor는 flavor, ownership, isolation,
  construction, cleanup과 finite capability vector를 한 owner record에
  결합한다.
- sealed partition은 concrete self-cell, abstract zero-cell 및
  owner-qualified opaque open-subtree cell을 구분한다.
- construction session은 하나의 commit owner와
  `PRE_DELEGATION -> BASE_INITIALIZED -> STORAGE_INITIALIZING ->
  POST_INIT -> LIVE` 단계를 가지며 실패 publish 수는 0이어야 한다.
- deterministic Class slot identity는 selector와 normalized input
  channel/receiver responsibility를 보존한다. forwarder는 target과 다른
  final identity를 갖는다.
- whole-Class synthesis가 미래에 허용되더라도 operation manifest와 법칙
  proof 하나가 whole nominal witness 하나만 만들며 child-owned witness는
  만들지 않는다.
- compatibility는 `source`, `resolution`, `behavior`, `serialization`,
  `runtime_layout`, `foreign_ABI`, `tooling_reflection`, `product`의 정확히
  여덟 독립 record로 관찰한다. 한 lane 상태가 sibling으로 전파되지
  않는다.

**의존성과 미해결 guard**

| OPEN P1 | 도입 전에 필요한 증거 |
|---|---|
| `CE-C-P1-001` | descriptor/profile/identity freeze와 Class variance residue 0 |
| `CE-C-P1-002` | order-invariant sealed partition executable corpus |
| `CE-C-P1-003` | checker/MIR/xVM construction·publication·cleanup receipt |
| `CE-C-P1-004` | unique slot/override/forwarder identity와 diagnostic evidence |
| `CE-C-P1-005` | TCC closure, whole-Class witness origin과 child witness 0 |
| `CE-C-P1-006` | complete API residue와 여덟 lane의 독립성 검증 |

여섯 항목은 모두 OPEN이다. Class syntax와 fixture가 이미 존재한다는
사실은 이 successor metadata/algorithm P1을 닫지 않는다.

**도입 조건**

Spec_/TypeSystem_의 exact identity와 partition ratification, Impl_의
closed HIR/MIR metadata와 construction lowering, Test_의 order/mutation/
failure corpus, lane별 evidence와 Design_의 최종 activation 판정이
필요하다. product lane은 target receipt가 생기기 전까지 `NOT_RUN`이다.

**비활성 예**

```text
candidate: class_successor_descriptor
source_class: existing current ClassDecl
class_variance_residue: 0
sealed_partition_receipt: MISSING
construction_target_receipt: MISSING
status: PREVIEW_NONACTIVATABLE
```

이 record는 source syntax가 아니며 current Class의 의미를 변경하지
않는다.

### PREVIEW_NONACTIVATABLE — Trait conformance successor와 route

Trait successor는 `TC-R001..R016` 의미를 보존하는
`NONACTIVATABLE` 후보이다. 최소 첫 route는 DIRECT뿐이며, current
소문자 `via`는 그대로 별도 current 표면으로 남는다.

**의미**

- requirement/conformance/parent evidence/associated binding에 canonical
  identity와 전역 coherence를 적용한다.
- child evidence는 canonical parent record를 재사용하고 child-local
  replacement를 만들지 않는다.
- overlap, locality와 link 결과는 source/import/allocation/schedule
  order와 무관해야 한다.
- future provider route가 설계되더라도 availability와 selection을
  분리하고 ambiguity/incompatibility는 terminal이어야 한다. fallback,
  priority와 specialization은 없다.
- HIR/MIR/API는 선택된 evidence identity를 닫힌 metadata로 운반하고
  runtime provider relookup 수는 0이어야 한다.

**의존성과 미해결 guard**

도입 순서는 대략 다음과 같다.

1. `TCC-P1-002`: root/profile/recovery 및 current/successor 격리;
2. `TCC-P1-003`: 정본 ID, 정규화, locality, overlap, termination 및
   parent/associated/link 알고리즘;
3. `TCC-P1-004`: current marker 공존과 정확한 diagnostic registry;
4. `TCC-P1-005`: DIRECT-only 최초 경로, 미래 VIA/AUTO 비구성성,
   current `via` parity와 fallback 0;
5. `TCC-P1-006`: 닫힌 HIR/MIR/API metadata와 relookup 0;
6. `TCC-P1-007`: 독립 실행 corpus, mutant와 재현 가능한 target receipt;
7. `TCC-P1-008`: 상태, tooling, formatter/LSP, migration과 package 준비도.

일곱 P1은 모두 OPEN이다. `TCC-P1-003..006`은 profile owner인
`TCC-P1-002`에 순차 의존하고, 실행/도구 증거는 앞선 계약이 고정된
뒤에만 유효하다. Class/Enum whole-nominal synthesis도 이 TCC gate를
통과해야 한다.

**도입 조건**

exact source spelling을 임의 발명하지 않고 별도 Spec_ ratification을
거쳐야 한다. 그 뒤 canonical algorithms, deterministic diagnostics,
metadata/link verifier, independent Test_ 실행, tooling idempotence와
Design_ 최종 판정이 모두 필요하다. fixed-glyph operator overload의
Stable 설계는 현재 `conformance` 표면에만 결합되며 Trait successor를
자동으로 활성화하지 않는다. 제품 구현과 실행 evidence는 계속
`NOT_RUN`이다.

**비활성 예**

아래는 route 판정 예시이지 Deeplus source가 아니다.

```text
goal: User conforms Display
profile: successor
route: AUTO
current_result: REJECT_ROUTE_UNCONSTRUCTIBLE
fallback_count: 0
runtime_provider_lookup_count: 0
open_guards: TCC-P1-002..008
```

```text
goal: User conforms Display
profile: successor-initial
route: DIRECT
static_candidate_status: DESIGN_ONLY
activation: false
product_lanes: 15/15_NOT_RUN
```

이 두 Preview 절의 문서화, 표 또는 개념 record는 source activation,
implementation authority, P1 closure, publication/promotion 또는 product
support가 아니다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- **타입/제네릭:** Class identity, Trait constraint와 associated
  projection은 정규화되지만 서로 대체되지 않는다. Trait variance는
  허용된 위치에서만 적용되고 Class variance는 거부된다.
- **생성:** `Type!(...)`/`Type!name(...)` constructor domain과
  `Type${...}` schema materialization domain은 별개이다.
- **패턴:** Enum/Union/Record/List는 명시된 structural carrier를
  갖지만 Class private representation은 열지 않는다. sealed closure는
  coverage 정보일 뿐 constructor pattern syntax가 아니다.
- **연산자:** Trait named method와 intrinsic glyph는 별도 resolution
  domain이다.
- **소유권:** resource field, receiver mode, constructor failure,
  forwarding과 witness call은 cleanup owner를 정확히 보존한다.
- **모듈:** visibility, sealed family scope, extension activation,
  conformance coherence authority는 module/package 경계를 사용한다.
- **MIR/link:** Class slot, Trait evidence, extension member와 activation
  origin은 link 전에 고정되며 link/source order가 winner를 만들 수 없다.
- **capability owner:** nominal type-side, named extension,
  Trait-qualified associated static과 explicit runtime owner는 서로 다른
  identity·authority·lifecycle domain이다.

## 정본 근거

- 정확한 Class/Trait/conformance/extension 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- 관계 domain, marker, operator 및 current/Preview fence:
  [`spec/language.md`](../../spec/language.md)
- Class, evidence, extension resolution과 ownership:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- dispatch/evidence MIR 투영:
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- frontend owner와 admission model:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- companion capability 분해와 associated static/value/private-authority fence:
  [`spec/contracts/companion-capability-coherence.json`](../../spec/contracts/companion-capability-coherence.json)
- feature lifecycle:
  [`spec/features/catalog/`](../../spec/features/catalog/)
- 검토 예제:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
