# 문맥별 문법과 production 탐색 안내서

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->
<!-- deeplus-status-fence: CURRENT -->

## 1. 이 장의 목적

이 장은
[`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)의 560개
production을 다시 나열하는 색인이 아니다.
독자가 실제 소스 조각을 보았을 때 어느 source root와 parser goal에서
읽기 시작해야 하는지, 같은 token이 문맥에 따라 왜 다른 production의
소유가 되는지, 구문 분석 성공과 의미 허용이 왜 별개의 판정인지 설명하는
탐색 안내서다.

정확한 token 순서와 구조적 중첩의 권위는
[`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)에 있다.
Pratt binding power, 입력 공급, token 부착, owner별 admission 및
CST/AST/HIR 책임은
[`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)에
있다.
정적 의미와 관측 가능한 동작은
[`spec/language.md`](../../spec/language.md),
[`spec/types/type-system.md`](../../spec/types/type-system.md),
[`spec/mir/semantics.md`](../../spec/mir/semantics.md)에 있다.

이 장의 예제는 설명을 위한 문서 예제다.
제품 parser, checker, formatter, xVM 및 LLVM 실행 증거는 별도 receipt가
없으므로 `NOT_RUN`이다.
따라서 “parse된다”는 설명은 통합 문법과 frontend model에 따른
설계 판정이고, 실제 제품 실행을 주장하지 않는다.

## 2. 문법을 읽는 네 단계

Deeplus 소스 한 조각을 판정할 때에는 다음 순서를 지킨다.

1. 파일의 역할로 source root를 고른다.
2. 현재 token 위치의 structural owner를 고른다.
3. owner가 위임한 parser goal로 내부를 읽는다.
4. 완성된 CST에 owner admission과 정적 의미를 적용한다.

이 순서를 뒤집으면 흔히 두 종류의 오류가 생긴다.

- 어떤 production에서 token 배열을 만들 수 있다는 이유만으로 현행
  프로그램이라고 잘못 결론 내린다.
- 의미상 거부될 프로그램을 parser가 처음부터 읽지 못한다고 잘못
  설명한다.

구문과 의미의 경계는 다음 식으로 기억할 수 있다.

```text
source role
  → source-root production
  → structural owner
  → nested parser goal
  → lossless CST
  → owner admission
  → typed HIR
  → MIR의 관측 의미
```

`RecoverySyntax`는 이 흐름의 예외처럼 보이지만 실제로는 예외가 아니다.
recovery owner도 CST와 진단까지만 만들며 admitted AST/HIR/MIR을 만들지
않는다는 별도의 admission 결과를 갖는다.

## 3. 첫 진입점: 파일 역할과 source root

### 3.1 안정 source root

통합 문법의 최상위 stable 진입점은 다음과 같다.

```ebnf
Deeplus ::= LibrarySourceFile
          | ExecutableSourceFile
          | ScriptSourceFile

LibrarySourceFile    ::= ModuleDecl? LibrarySourceItem*
ExecutableSourceFile ::= ModuleDecl? ExecutableSourceItem*
ScriptSourceFile     ::= Shebang? ModuleDecl? ScriptSourceItem*
```

parser가 첫 token만 보고 세 root 중 하나를 추측하는 것은 아니다.
빌드 manifest 또는 호출자가 source role을 선택하고, 선택된 root parser는
반드시 `EOF`까지 도달해야 한다.
이 규칙은 frontend model의 `SOURCE_ROOT` parser commitment다.

세 root의 차이는 “파일 확장자”가 아니라 허용되는 최상위 owner다.

| source role | 문법 진입점 | 중요한 현재 제한 |
|---|---|---|
| library | `LibrarySourceFile` | import/use와 `TopLevelDecl`을 받는다 |
| executable | `ExecutableSourceFile` | top-level binding을 받지 않고 `EntryFunctionDecl`을 받을 수 있다 |
| script | `ScriptSourceFile` | shebang과 top-level binding을 받지만 entry 함수는 받지 않는다 |

다음은 executable root의 최소 구조다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
module demo::hello

def#entry launch(args: Sequence<String>) -> ExitCode
    throws Never
    effects {io}
= {
    print(args)
    return ExitCode::success
}
```

판정 순서는 다음과 같다.

1. manifest가 executable role을 공급한다.
2. `ModuleDecl`이 선택적으로 소비된다.
3. `def#entry` 때문에 `EntryFunctionDecl`을 선택한다.
4. `EntryFunctionRest`가 parameter, return, throws, effects, contract와
   body를 순서대로 읽는다.
5. checker가 entry ABI, 이름, parameter/return shape 및 effect 정책을
   별도로 검사한다.

같은 token 열이 script root에 들어오면 `EntryFunctionDecl`을 소유할
`ScriptAnnotatableDecl`이 없으므로 root-level parse/admission 경계에서
거부된다.
반대로 script의 top-level `let`을 executable root에 놓으면
`TopLevelBindingDecl` 선택지가 없으므로 executable item이 아니다.

### 3.2 item wrapper와 annotation attachment

source item은 declaration 하나와 정확히 같지 않다.
annotation이 붙은 선언과 annotation이 없는 선언을 wrapper가 구분한다.

```ebnf
LibrarySourceItem ::= AnnotationAttachment LibraryAnnotatableDecl
                    | ImportOrUseDecl
                    | TopLevelDecl

AnnotationAttachment ::= Annotation+
Annotation ::= "@" Identifier ArgumentList? LineBreakBoundary
```

`Annotation`은 이름과 선택적 argument list 뒤에 물리 line break를
요구한다.
다음 줄의 declaration을 attachment 대상(owner)으로 삼는다.
annotation을 expression prefix `@if`나 implicit argument `@`와 같은
goal에서 읽지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
@deprecated("use parseStrict")
public def parse(text: String) -> Result<Int, error ParseError>
    throws Never
    effects {}
= {
    return parseStrict(text)
}
```

여기서 parser는 `@deprecated(...)`를 `Annotation`으로 읽고 줄바꿈에서
commit한다.
checker는 annotation 이름, 대상 declaration 종류, 인자 형식 및 중복
정책을 나중에 검사한다.
존재하지 않는 annotation이라도 구조가 맞으면 CST는 만들 수 있으므로,
“알 수 없는 annotation”은 보통 lexical/structural parse 실패가 아니라
resolver 또는 checker 진단이다.

annotation과 declaration을 같은 물리 줄에 쓰면 `LineBreakBoundary`를
만족하지 않는다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
@deprecated("use parseStrict") public def parse(text: String) -> Int = {
    return 0
}
// Annotation의 LineBreakBoundary가 없으므로 structural rejection
```

### 3.3 module, import, use, export

관련 production의 역할은 다음처럼 나뉜다.

| 의도 | 시작 production | 핵심 하위 production |
|---|---|---|
| 파일의 논리 이름 | `ModuleDecl` | `QualifiedPath` |
| 이름을 가져오기 | `ImportDecl` | `ImportTail`, `ImportAlias`, `ImportSelection` |
| 확장/프로필 활성화 | `UseDecl` | `QualifiedPath` |
| 활성화를 다시 노출 | `UseExportDecl` | `QualifiedPath` |
| API 항목 노출 | `ExportDecl` | `ExportItem` |

`import`와 `use`는 resolver에서 같은 의미가 아니다.
둘 다 `QualifiedPath`를 읽는다는 구문적 유사성만으로 namespace import와
extension/profile activation을 합치면 안 된다.
또한 block prologue의 `UseDecl`/`ImportDecl`과
`ScopedUseStmt`/`ScopedImportStmt`는 서로 다른 lifetime owner다.

## 4. declaration introducer를 보고 owner 찾기

### 4.1 최상위 선택 표

`TopLevelDecl`과 `NonBindingTopLevelDecl`은 declaration 탐색의 중심이다.
정확한 전체 대안은 EBNF를 보아야 하지만, 독자는 다음 표로 첫 owner를
찾을 수 있다.

| source spelling의 시작 | 우선 확인할 production |
|---|---|
| `def`, `def#...` | `ModuleFunctionDecl`, root에 따라 `EntryFunctionDecl` |
| `class`, `value class`, `resource class`, `data class` | `ClassDecl` |
| `trait` | `TraitDecl` |
| `conformance` | `ConformanceDecl` |
| `extension T as name` | `ExtensionSetDecl` |
| `extension pack` | `ExtensionPackDecl` |
| `enum` | `EnumDecl` |
| `schema` | `SchemaDecl` |
| `type` | `TypeAliasDecl` |
| `actor` | `ActorDecl` |
| `protocol` | `ActorProtocolDecl` |
| `typestate` | `TypestateResourceDecl` |
| `unit catalog` | `UnitCatalogDecl` |
| `bitfield`, `bitfield#flags` | `BitfieldDecl` |
| `capability` | `NamedEffectCapabilityDecl` |
| `module signature`, `opaque module` | `ModuleInterfaceDecl` |
| `let`, `var` | root와 위치에 따라 `TopLevelBindingDecl`, `LocalBindingStmt`, `FieldDecl` |

이 표는 keyword만으로 최종 owner가 정해진다는 뜻이 아니다.
예를 들어 `def` 뒤의 hash role, 현재 선언이 class body인지 trait body인지,
이름 뒤의 dispatch/witness marker 및 source root가 함께 owner를 결정한다.

### 4.2 `def`는 하나의 production이 아니다

함수 계열은 공통 조각을 공유하지만 owner별 tail과 admission이 다르다.

```ebnf
DefIntroducer      ::= "def" HashTag*
ModuleFunctionDecl ::= TopLevelVisibility? DefIntroducer Identifier FunctionRest
EntryFunctionDecl  ::= DefIntroducer Identifier EntryFunctionRest
LocalFunctionDecl  ::= CaptureList? DefIntroducer Identifier FunctionRest

MemberFunctionDecl ::= MemberVisibility? DefIntroducer Identifier
                       ClassDispatchMarker FunctionRest

TraitMethodDecl ::= MemberVisibility? DefIntroducer Identifier
                    TraitWitnessMarker TypeParameterList?
                    ParameterList TraitFunctionTail
```

따라서 `def#entry`를 발견했다고 곧바로 entry 함수로 승인하지 않는다.
executable root여야 하고, `DefIntroducer`의 role 조합이
`EntryFunctionDecl` owner에 허용되어야 하며, ABI shape도 통과해야 한다.

instance method는 이름 뒤의 `ClassDispatchMarker`를 요구한다.
field declaration에는 같은 marker를 붙이지 않는다.
trait method의 같은 glyph는 `TraitWitnessMarker`이며 AST 의미가 다르다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
public class Counter {
    -var value: Int = 0

    +def read.() -> Int
        throws Never
        effects {}
    = {
        return value
    }

    +def#mut increment.() -> Unit
        throws Never
        effects {}
    = {
        value += 1
    }
}
```

첫 메서드의 `.`는 final instance dispatch, 두 번째의 `.`도 같은
dispatch owner다.
앞의 `+`는 member visibility이고 `def#mut`의 `#mut`는 callable profile다.
세 표지를 한 “modifier 문자열”로 합쳐 해석하지 않는다.

### 4.3 hash role과 줄 경계

`HashTag ::= "#" RoleWord`는 문법상 단순하지만 token boundary는 frontend
model이 보충한다.
`#`와 role word 사이에는 같은 물리 줄의 horizontal space 또는 comment가
허용될 수 있고 formatter는 보통 `#word`로 붙인다.
물리 line break는 role을 끊는다.

hash literal sigil은 정반대다.
`#map{`, `#set{`, `#mut[`, `#[`, `#dims[` 등은 sigil과 payload opener
사이에 trivia를 허용하지 않는다.
`def # pure` 같은 role 표면과 `# [1, 2]` 같은 literal 표면을 하나의
“hash 뒤 공백 규칙”으로 설명하면 잘못이다.

## 5. parameter와 argument: 비슷해 보이는 서로 다른 goal

### 5.1 parameter goal

declaration의 `ParameterList` 안에서는 `Parameter`를 읽는다.

```ebnf
Parameter ::= StoredParameter
            | ContextParameter
            | WitnessParameter
            | RepeatedParameter
            | NamedRestParameter
            | ValueParameter

ValueParameter     ::= ParameterMode? ParameterPatternSlot TypeAnnotation
ParameterPatternSlot ::= Identifier
ContextParameter   ::= "context" Identifier ":" TypeRef
WitnessParameter   ::= "using" Identifier ":" "witness" TypeRef
RepeatedParameter  ::= Identifier "..." TypeAnnotation
NamedRestParameter ::= Identifier "***" TypeAnnotation
```

callable parameter는 refutable `Pattern`이 아니라 identifier slot만
받는다.
`StoredParameter`는 primary/data class parameter list에서 field, input,
initialization을 합성하는 별도 lowering owner다.
겉으로 `let id: Int`처럼 보인다는 이유로 local binding과 같은 AST를
만들지 않는다.

### 5.2 argument goal

호출의 `ArgumentList` 안에서는 `Argument`를 읽는다.

```ebnf
Argument ::= ContextArgument
           | WitnessArgument
           | NamedArgument
           | PositionalUnfoldArgument
           | NamedUnfoldArgument
           | Expr

ContextArgument          ::= "context" Expr
WitnessArgument          ::= "using" WitnessArgumentValue
NamedArgument            ::= Identifier ":" Expr
PositionalUnfoldArgument ::= "*" Expr
NamedUnfoldArgument      ::= "**" Expr
```

parameter와 argument의 role은 호출 compatibility identity에 남는다.
ordinary positional argument는 `context` parameter를 채우지 못하고,
ordinary value나 활성 extension은 `using ...: witness T`를 자동으로
대체하지 못한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public def render(
    value: Float64,
    context format: FormatPattern,
    using display: witness Display<Float64>,
) -> String
    throws Never
    effects {}
= {
    return renderValue(value, context format, using display)
}

let text = render(
    3.14,
    context FormatPattern!("{:.2f}"),
    using floatDisplay,
)
```

parser는 `context`와 `using`을 owner-local contextual word로 읽는다.
checker는 각 channel이 선언의 동일 role과 일치하는지 검사한다.
`using` 뒤의 witness selector 문법은 identifier,
`ConformanceEvidenceSelector`, `NamedConformanceEvidenceSelector` 중
하나다.

### 5.3 `...`, `***`, `**`의 소유자

세 표면은 문맥을 보지 않고 token 모양만 비교하면 오판하기 쉽다.

| 표면 | owner | 의미 |
|---|---|---|
| suffix `...` | `RepeatedParameter`, `ParenTypeItem` | positional residue |
| `for ... Pattern in Expr` | `UnfoldClause` | comprehension source unfold |
| suffix `***` | `NamedRestParameter`, `ParenTypeItem` | named residue |
| prefix `**Expr` | `NamedUnfoldArgument`, materialization entry | named unfold |
| spaced infix `a ** b` | expression Pratt goal | linear product operator |

부착 정책도 의미의 일부다.
parameter/type의 residue marker는 앞 type 또는 identifier에 붙고,
call/materialization unfold marker는 뒤 expression의 prefix다.
linear product는 이항 연산자로 읽힐 수 있는 간격과 양 operand가 필요하다.

## 6. type goal: `TypeRef` 안으로 들어가는 법

### 6.1 type Pratt entry

대부분의 type 위치는 `TypeRef ::= PrattType`으로 위임한다.
함수 반환 위치처럼 최상위 function type을 금지하는 곳은
`NonFunctionTypeRef ::= PrattNonFunctionType`을 사용한다.

type Pratt goal의 현재 결합력은 낮은 순서로 union `|`,
intersection `&`, prefix ownership qualifier, postfix optional `?`다.
정확한 값은 frontend model의 `pratt.type.operators`가 소유한다.

```ebnf
TypeRef            ::= PrattType
NonFunctionTypeRef ::= PrattNonFunctionType
TypePrimary        ::= QualifiedTypeReference
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

`?`는 `T?`의 attached postfix다.
expression conditional의 `? :`와 Option coalescing token `?:`는 다른
goal이다.
type parser에 들어온 뒤에는 expression ternary를 찾지 않는다.

### 6.2 괄호 type의 commitment

`ParenTypeSyntax`는 grouping, tuple type, repeated/named-rest residue,
function type의 공통 owner다.

```ebnf
ParenTypeSyntax  ::= HashTag* "(" ParenTypeItemList? ")" FunctionTypeTail?
ParenTypeItem    ::= TypeRef | TypeRef "..." | TypeRef "***"
FunctionTypeTail ::= "->" NonFunctionTypeRef ThrowsClause? EffectsClause?
```

닫는 괄호 뒤의 `->`와 내부 comma shape가 commitment에 중요하다.
`(Int) -> String`은 function type이고 `(Int, String)`은 tuple type이다.
named rest를 표기할 때에는 `Record***`를 쓰며 `Record**`는 recovery
대상이다.

### 6.3 type argument와 type parameter는 다르다

`TypeParameterList`는 declaration이 새 parameter를 bind한다.
`TypeArgumentList`는 이미 존재하는 generic identity를 적용한다.

```ebnf
TypeParameter ::= VarianceMarker? Identifier TypeParameterKindAnnotation?
TypeArgument  ::= TypeRef | StaticIntLiteral | ErrorTypeArgument
```

type parameter kind는 `type`, `StaticInt`, `EffectRow`, `ErrorSet` 중 하나다.
type argument의 bare decimal integer는 `StaticIntLiteral` goal이며,
recoverable error channel을 명시하는 argument는 `error TypeRef`다.
둘을 expression argument와 섞지 않는다.

### 6.4 where, refinement, requires, ensures

네 표면은 모두 조건처럼 읽히지만 owner와 판정 시점이 다르다.

| 표면 | production | 소유자와 목적 |
|---|---|---|
| type annotation 뒤 `where` | `RefinementClause` | 값이 refinement predicate를 만족 |
| generic tail의 `where` | `WhereClause` | conformance/equality/row 제약 |
| callable의 `requires` | `RequiresClause` | 호출 전제 계약 |
| callable의 `ensures` | `EnsuresClause` | 정상 반환 보장 계약 |
| schema field 뒤 `where` | `SchemaConstraint` | field 유효성 제약 |

`RefinementClause ::= "where" PredicateExpr`이므로 여기의 오른쪽은
type goal이 아니라 predicate expression goal이다.
`WhereClause`의 각 `WherePredicate`는 제한된 구조를 가지므로 arbitrary
Bool expression을 받지 않는다.
계약 clause는 callable tail에 나타나며 body보다 앞선다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
public type Positive = Int where this > 0

public def clamp<T>(value: T, lower: T, upper: T) -> T
    throws Never
    effects {}
    requires lower <= upper
    ensures lower <= upper
    where T conforms Ordered
= {
    if value < lower {
        return lower
    }
    if value > upper {
        return upper
    }
    return value
}
```

이 예제에서 첫 `where`는 `TypeAliasRhs`의 refinement다.
`requires`와 `ensures`는 `ContractClause`다.
마지막 `where`는 `FunctionTail`의 generic constraint다.
동일 spelling을 발견했다고 하나의 공통 `where-expression` node로
낮추면 안 된다.

## 7. expression goal과 Pratt parser

### 7.1 세 expression entry

문법에는 목적이 다른 세 Pratt entry가 있다.

```ebnf
Expr           ::= PrattExpr
PredicateExpr  ::= PrattPredicateExpr
SliceIndexExpr ::= PrattSliceIndexExpr
```

`Expr`는 일반 값 계산을 읽는다.
`PredicateExpr`는 refinement, contract, law처럼 정적 제약이 추가되는
owner에서 읽는다.
`SliceIndexExpr`는 index suffix가 slice delimiter와 anchor를 직접
소유하도록 제한된 terminator 집합을 사용한다.

EBNF의 `EXPRESSION_PRATT_ENTRY` 같은 외부 terminal은 “아무 expression”을
뜻하지 않는다.
frontend model의 parselet registry, binding power와 owner별 admission을
함께 읽어야 한다.

### 7.2 prefix, primary, postfix, infix

일반 expression은 다음 사고 순서로 읽을 수 있다.

1. prefix parselet이 있으면 오른쪽 operand를 binding power 170으로 읽는다.
2. 아니면 `PrimaryExpr` 하나를 읽는다.
3. 현재 왼쪽 값에 붙는 postfix parselet을 반복한다.
4. lookahead의 infix binding power가 현재 goal보다 강하면 오른쪽을 읽는다.

prefix 후보는 `+`, `-`, `not`, `~~`, `move`, `borrow`, `&`, `await`다.
postfix 후보에는 call, tuple ordinal, index, member, message,
NumericArray transpose, constructor, derivation, cast가 있다.

`PrimaryExpr`에는 literal, identifier/static reference, paren expression,
block-like control expression, closure, generator, spawn, unsafe, collection
literal 등이 들어간다.
production 목록은 appendix A에서 찾되 의미는 해당 owner 장을 함께 읽는다.

### 7.3 우선순위가 만드는 경계 사례

`-2 ^ 2`에서 power는 prefix보다 낮은 숫자가 아니라 더 약한/강한
결합 규칙을 정확히 registry대로 적용해야 한다.
숫자의 sign은 lexer token 일부가 아니라 prefix operator다.
`a ?: b ?: c`는 오른쪽 결합이고 RHS는 필요할 때만 평가한다.
`a and then b`는 sequential Bool이며 `a and b`와 flow fact 전달이
다르다.

`is`와 `!is`는 comparison parselet에 있지만 직접 comparison chain에
들어갈 수 없는 checker-bounded case다.
따라서 parselet 등록과 semantic chain admission을 구별해야 한다.

### 7.4 postfix base는 implicit Pratt input

`value[index].member(args)`의 각 suffix production에는 base expression을
문법 인자로 다시 쓰지 않는다.
frontend input-supply policy의 `POSTFIX_BASE`가 앞서 완성된 Pratt left
node를 `ImplicitPrattLeft(expr_id)`로 공급한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let result = records[2].name~trim()
```

읽기 순서는 `records` → `IndexSuffix` → `MemberSuffix` →
`MessageSuffix`다.
각 suffix가 `records`를 다시 평가하는 것이 아니며, lowering은
source-defined single evaluation과 failure order를 보존한다.

### 7.5 `^`의 세 owner

caret는 token 하나지만 적어도 세 문맥이 있다.

- `A^`: 앞 token에 붙고 RHS가 없으면 NumericArray transpose postfix
- `a ^ b`: 양쪽에 연산자 간격과 RHS가 있으면 power infix
- `m^2`: `UnitExpr` 안에서는 `UnitPostfixParselet`의 static exponent

comment나 line break는 attachment 증거가 아니다.
postfix와 infix 해석이 동시에 가능하도록 섞으면
`CARET_ATTACHMENT_AMBIGUOUS` 경계 진단이 우선한다.

### 7.6 `~` message suffix

`MessageSuffix`는 receiver를 Pratt left에서 공급받고
`MessageSelector`를 읽는다.
selector는 identifier 또는 `QualifiedExtensionSelector`다.
HIR은 `spawn` selector를 예약해 concurrency 의미를 부여하지만,
parser가 별도의 `SpawnMessageSyntax`를 만들지는 않는다.

`receiver ~ f arg { ... }`의 parenless call 예외는 정확히 하나의
`AtomicCallArgument`와 정확히 하나의 closure로 제한된다.
일반적인 다중 positional argument 생략 문법으로 확장하지 않는다.

## 8. 괄호와 hash prefix의 parser commitment

### 8.1 expression 괄호

```ebnf
ParenExprSyntax  ::= "(" ParenExprContent? ")"
ParenExprContent ::= Expr ParenExprTail?
ParenExprTail    ::= ","
                   | "," Expr ("," Expr)* ","?
```

`(value)`는 grouping이고 `(value,)`는 1-tuple expression이다.
comma shape가 node identity를 바꾼다.
빈 `()`는 unit syntax와 expression context의 Unit value owner를
구별하여 읽는다.

### 8.2 type 괄호와 expression 괄호

parser 호출자가 type goal을 선택한 상태라면 `ParenTypeSyntax`,
expression goal이라면 `ParenExprSyntax`를 사용한다.
괄호 안 token만 보고 전역적으로 “tuple parser” 하나를 부르면 안 된다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
private type Unary = (Int) -> Int
private type Pair = (Int, String)

let grouped = (1 + 2)
let singleton = (1,)
```

`Unary`의 괄호는 type goal이고 닫는 괄호 뒤 `->`가 function type tail을
commit한다.
`grouped`와 `singleton`의 차이는 comma 하나다.

### 8.3 hash literal dispatcher

expression prefix `#`를 보면 attached payload를 먼저 구분한다.

| attached prefix | owner |
|---|---|
| `#map{` | `MapLiteral` 또는 `MapComprehensionExpr` |
| `#set{` | `SetLiteral` 또는 `SetComprehensionExpr` |
| `#mut[` | `MutListLiteral` |
| `#[` | `ShapeInferredArrayLiteral` 또는 column-vector form |
| `#<dims>[` | `ExactShapeArrayLiteral` |

`# role`이 허용하는 trivia 정책을 hash literal에 적용하지 않는다.
obsolete prefixed collection spelling은 현재 owner가 아니며 recovery나
removed-surface 진단 정책을 따른다.

## 9. block, statement, value body

### 9.1 일반 block

```ebnf
Block         ::= "{" BlockPrologue? BlockSequence "}"
BlockPrologue ::= (UseDecl | ImportDecl)+
BlockSequence ::= BlockItem* BlockFinalItem?
BlockItem     ::= LocalFunctionDecl | Stmt
BlockFinalItem ::= ControlTransfer | BindingCore | Expr
```

block 첫머리의 import/use는 `BlockPrologue`다.
중간 statement는 `StatementBoundary`를 요구할 수 있고,
마지막 expression은 block의 허용된 owner에 따라 final item이 된다.
EOF는 root statement boundary에는 허용되지만 nested block에서는
닫는 `}`를 대신할 수 없다.

### 9.2 이름 있는 함수 body

```ebnf
FunctionBody        ::= "=" FunctionBodyContent
FunctionBodyContent ::= Block | ReturnShorthand | ClauseFunctionBody
ReturnShorthand     ::= "return" Expr StatementBoundary
ClauseFunctionBody  ::= "{{" LineBreakBoundary? MatchArmSequence "}}"
```

현행 named function body는 `= { ... }`, `= return Expr`,
`= {{ ... }}` 중 하나다.
bare `= Expr`는 현행 named function body가 아니다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
public def double(value: Int) -> Int = value * 2
// NAMED_FUNCTION_BODY commitment: bare '= Expr'는 거부
```

같은 expression이 lambda body에서는 허용될 수 있다는 사실은
`FunctionBody`를 느슨하게 만들 근거가 아니다.
owner가 다르면 body engine도 다르다.

### 9.3 `ValueBody`와 `ret`

`@if`, `@try`, `@scope` 같은 value-control owner는 `ValueBody`를 쓴다.

```ebnf
ValueBody               ::= SingleExpressionValueBody
                          | ExplicitRetValueBody
SingleExpressionValueBody ::= "{" Expr "}"
ExplicitRetValueBody     ::= "{" BlockItem* RetTransfer "}"
RetTransfer              ::= "ret" Expr? GuardClause?
```

`ret`는 이 로컬 value boundary와 lambda 결과를 끝낸다.
`return`은 이름 있는 callable의 control target을 끝낸다.
두 token을 스타일 차이로 취급하면 closure 또는 value-control 경계를
잘못 넘어간다.

### 9.4 statement boundary

`StatementBoundary`는 단순 `";"?`가 아니다.
root에서는 semicolon, trivia의 line break, EOF가 가능하다.
nested context에서는 EOF가 불가능하다.
match arm과 schema layout처럼 owner 자체 separator 정책을 가진 곳에서는
그 owner가 line break/comma를 소비한다.

loop 뒤의 attached `match`는 semicolon이나 intervening item이 없을 때만
preceding loop의 outcome을 implicit subject로 받는다.
line break와 comment는 attachment를 끊지 않지만 semicolon은 끊는다.

## 10. pattern goal과 binding goal

### 10.1 두 entry family

일반 match/catch/loop/if-let 위치는 `Pattern`을 사용한다.
local binding은 `BindingPattern`을 사용하여 whole-pattern type annotation
정책을 별도로 보존한다.

```ebnf
Pattern        ::= OrPattern
OrPattern      ::= AliasPattern ("|" AliasPattern)*
AliasPattern   ::= MovePattern ("as" Identifier)?
MovePattern    ::= "move"? PatternPrimary

BindingPattern ::= BindingOrPattern TypeAnnotation?
```

callable parameter는 둘 중 어느 것도 아니고
`ParameterPatternSlot ::= Identifier`다.
이 세 구분은 refutability, binding transaction, public signature identity
때문에 필요하다.

### 10.2 pattern primary 찾기

`PatternPrimary`에서 자주 찾는 owner는 다음과 같다.

| 모양 | production |
|---|---|
| `name: T` | `TypedBindingPattern` |
| `(pattern)` | `ParenthesizedPattern` |
| `${ field, name: p }` | `RecordPattern` |
| `[head, .._]` | `ListPattern` |
| `Type::case(...)` 또는 `::case(...)` | `VariantPattern` |
| literal | literal pattern branch |
| `_` | wildcard branch |

현재 tuple pattern과 record rest는 current가 아니다.
list rest는 마지막의 무시 rest `.._` 하나만 허용한다.
parameter pattern은 identifier 하나뿐이다.

### 10.3 expected-type input

`VariantPattern`의 qualifier가 `::`뿐이면 scrutinee의 expected type이
variant owner를 공급한다.
`TypeRef::case`이면 type을 source가 명시한다.
이 차이는 frontend input-supply policy의 `VARIANT_EXPECTED`와
`VARIANT_QUALIFIED`다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
public def describe(value: Option<Int>) -> String = {{
    ::some(number) => "value=${number}"
    ::none         => "none"
}}
```

clause function의 subject는 함수 parameter parent가 암시적으로 공급한다.
각 `::some`/`::none`은 그 expected `Option<Int>`를 사용한다.
문법에서 생략된 subject나 type을 전역 optional로 만들지 않는다.

### 10.4 transactional binding

`if let`, `while let`, `for let`, guarded binding은 pattern 성공 edge에서만
binding을 commit한다.
실패 edge에는 부분 binding이 새지 않는다.
`move` pattern의 ownership 이동도 성공 commit과 함께 관측되어야 한다.

parser는 pattern shape를 만들고,
checker는 irrefutability/refutability, exhaustiveness, binding consistency,
closed Union narrowing을 판정한다.
따라서 “pattern이 parse됨”은 “그 context에서 pattern이 허용됨”보다 약한
주장이다.

## 11. 문자열 interpolation의 두 parser goal

scanner는 plain string과 interpolated string을 처음부터 별도 outcome으로
만든다.
interpolation mode boundary는 scanner가 소유하고,
`${...}` 내부 expression과 shorthand path CST는 parser가 소유한다.

```ebnf
InterpolatedString     ::= STRING_START InterpolatedStringPart* STRING_END
InterpolatedStringPart ::= STRING_TEXT
                         | STRING_ESCAPE
                         | InterpolationExpr
                         | InterpolationPath
InterpolationExpr      ::= INTERPOLATION_OPEN Expr
                           InterpolationFormat? INTERPOLATION_CLOSE
InterpolationPath      ::= "$" InterpolationPathRoot
                           InterpolationPathSelector*
                           INTERPOLATION_BOUNDARY?
```

braced interpolation은 일반 `Expr` goal을 연다.
shorthand path는 root와 member/static-index selector만 읽으며 call을
허용하지 않는다.
복잡한 expression에는 braces를 사용한다.
명시 boundary 문자는 shorthand의 뒤 text와 identifier continuation을
나눈다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let first = "user=$user.name"
let second = "total=${price * count:money}"
```

첫 줄은 `InterpolationPath`, 둘째 줄은 `InterpolationExpr`와
`InterpolationFormat`이다.
format text는 expression Pratt parser가 아니라 scanner의 format mode가
소유한다.

호출을 shorthand 뒤에 바로 붙이는 것은 경계 오류다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let invalid = "name=$user.display()"
// INTERPOLATION_COMPLEX_EXPRESSION_REQUIRES_BRACES
```

올바른 의도는 `${user.display()}`처럼 braces로 일반 expression goal을
여는 것이다.

## 12. literal, comprehension, generator

### 12.1 literal과 materialization

서로 닮은 중괄호라도 owner는 다르다.

| 표면 | owner | 결과 plane |
|---|---|---|
| `Type${ ... }` | `TypedMaterializationExpr` | 명시 type materialization |
| `#map{ ... }` | `MapLiteral` | runtime-key map |
| `#set{ ... }` | `SetLiteral` | set |
| `${ ... }` pattern | `RecordPattern` | pattern, value 아님 |
| `source!{ ... }` | `PrototypeDerivationSuffix` | prototype derivation |

materialization entry의 punning과 named unfold는 parser에서 entry shape를
보존하고, checker/lowering에서 label과 field identity를 결정한다.

### 12.2 comprehension clause

```ebnf
ComprehensionExpr    ::= "[" Expr ComprehensionClause+ "]"
MapComprehensionExpr ::= "#" "map" "{" MapEntry ComprehensionClause+ "}"
SetComprehensionExpr ::= "#" "set" "{" Expr ComprehensionClause+ "}"

ComprehensionClause ::= ForClause
                      | PositiveGuard
                      | IfLetClause
                      | UnfoldClause
ForClause    ::= "for" Pattern "in" Expr
IfLetClause  ::= "if" "let" Pattern "=" Expr
UnfoldClause ::= "for" "..." Pattern "in" Expr
```

첫 element/map entry를 읽은 뒤 `for`가 나타나면 literal sequence가 아니라
comprehension owner로 commit한다.
clause는 source order로 중첩되고 guard와 if-let은 앞 clause가 만든
binding을 볼 수 있다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
let names = [
    user.name
    for user in users
    if user.active
]

let byId = #map{
    user.id: user
    for user in users
    if let ::some(profile) = user.profile
}
```

두 comprehension은 일반 list/map literal과 같은 opener를 공유하지만
`ComprehensionClause+`가 node identity를 바꾼다.
`if let`의 binding은 성공한 iteration에서만 뒤 clause와 result
expression에 제공된다.

### 12.3 generator expression

```ebnf
GeneratorExpr ::= CaptureList? GeneratorCore
GeneratorCore ::= "@" "for" Pattern "in" Expr Block
                | "@" "while" Expr Block
                | "@" "repeat" Block "while" Expr
```

generator는 collection comprehension이 아니다.
`@for` introducer, 선택적 capture list, block과 `yield` control transfer를
소유하며 lazy/resumable 평가와 ownership 책임을 남긴다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
let evens = @for value in values {
    yield value if value % 2 == 0
}
```

parser는 `GeneratorExpr`와 `YieldTransfer`를 만든다.
checker는 yield type, generator lifetime, capture 책임, effect/error row를
검사하고 MIR은 resume와 cleanup 순서를 보존한다.

## 13. slice/index 전용 goal

### 13.1 `IndexSuffix`와 axis

```ebnf
IndexSuffix  ::= "[" SliceAxisList "]"
SliceAxisList ::= SliceAxis (";" SliceAxis)*
SliceAxis    ::= SliceRange | SliceIndexExpr | AxisWildcard
SliceRange   ::= SliceBound (".." | "..<") SliceBound
SliceBound   ::= SliceIndexExpr | "^" | "$" | "^" OffsetExpr | "$" OffsetExpr
AxisWildcard ::= "*"
```

현재 index suffix에는 axis가 하나 이상 필요하다.
빈 `[]`는 `RecoveryEmptyIndexSuffix`의 진단 전용 owner다.
slice range는 양 bound를 요구하며 생략 bound 대신 첫 좌표 `^`와 마지막
좌표 `$` anchor를 쓴다.

일반 expression range도 `..`/`..<`를 사용하지만,
index suffix에서는 `SliceRange`가 delimiter를 소유한다.
`PrattSliceIndexExpr`는 `..`, `..<`, `;`, `]` 앞에서 멈춘다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let first = values[1]
let last = values[values.length]
let middle = values[^ + 1 ..< $ - 1]
let column = matrix[*; 2]
```

`^`와 `$`는 단독 element index가 아니라 `SliceRange`의 bound에서만
유효하다. 따라서 ordinary one-based sequence의 첫 element는 `values[1]`,
마지막 element는 `values[values.length]`로 읽는다.
`*` full-axis는 NumericArray axis에서만 의미가 있다.
List에 같은 syntax가 parse되더라도 checker가 collection kind별 axis
admission을 판정한다.
1-based logical indexing, bound failure, view/copy 결과는 collection
semantic owner가 결정한다.

### 13.2 slice anchor의 범위

`^`와 `$`는 `SliceBound`만 소유한다.
일반 expression primary로 승격되지 않는다.
따라서 index 밖의 `$`를 “last value” 전역 상수로 해석하지 않는다.
잘못된 위치는 `SLICE_ANCHOR_OUTSIDE_SLICE`이고 semantic anchor node는
0개다.

## 14. parse 성공과 semantic admission

### 14.1 세 가지 결과를 구분한다

한 source fragment에는 적어도 다음 세 결과가 가능하다.

| 결과 | CST | HIR/MIR | 예 |
|---|---|---|---|
| current admitted | lossless CST 있음 | owner 검사를 통과해 생성 | 올바른 module function |
| structurally valid, semantically rejected | CST 있음 | 진단 뒤 admitted node 없음 또는 poison | 잘못된 variance 위치 |
| recovery-only recognized | recovery CST 있음 | 항상 0 | `null`, 빈 index |

“문법에 production이 있다”는 두 번째와 세 번째 결과도 포함할 수 있다.
production profile과 frontend feature profile을 반드시 확인한다.

### 14.2 owner admission 사례

다음 항목은 대개 token sequence parse 뒤에 checker가 판정한다.

- top-level type declaration의 explicit visibility
- callable owner별 `#async`, `#mut`, `#entry` profile 조합
- class flavor와 modifier compatibility
- member dispatch marker와 trait witness marker
- parameter channel 순서와 named-rest 유일성
- type parameter kind와 variance 위치
- effect/error row의 정규화와 overlap
- pattern의 context별 refutability와 binding consistency
- collection axis, element type, exact shape
- unsafe operation의 lexical boundary와 proof obligation

예를 들어 `out T`는 `TypeParameter` 구조로 읽을 수 있지만 현재 variance가
허용되는 owner가 아니면 `VARIANCE_ONLY_ALLOWED_ON_TRAIT_TYPE_PARAMETER`
같은 checker 진단을 낸다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
public class InvalidBox<out T> {
    +let value: T
}
// parse 가능, class owner의 variance admission에서 거부
```

### 14.3 구조 오류의 우선순위

반대로 다음은 owner가 구조를 완성하지 못하는 parser 경계다.

- annotation 뒤 line break 누락
- named function의 bare `= Expr`
- index suffix의 axis 누락
- 현재 range가 아닌 `..>`/`...` spelling
- token attachment가 필요한 `as ?`, `! is`, `T ?`
- named rest와 unfold marker를 반대로 사용
- statement-only rightward binding을 expression 안에서 사용
- interpolation shorthand 뒤 복잡한 call continuation

recovery owner가 있는 경우 parser는 정확한 교정 진단을 위해 CST를
보존할 수 있지만 current AST로 승인하지 않는다.

## 15. ambiguity를 푸는 실전 절차

모호해 보이는 token을 만났을 때 다음 질문을 위에서 아래로 적용한다.

1. 호출자가 선택한 source role은 무엇인가?
2. 현재 위치는 declaration, type, expression, pattern, statement 중
   어느 goal인가?
3. 앞서 완성된 construct가 implicit input을 공급하는가?
4. token 사이 trivia가 semantic attachment를 만족하는가?
5. lookahead가 owner commitment를 확정하는가?
6. production profile은 `STABLE`, `PREVIEW`, `RECOVERY` 중 무엇인가?
7. 구조가 완성된 뒤 owner admission이 추가로 거부하는가?

### 15.1 빠른 ambiguity 표

| 표면 | 먼저 확인할 것 | 올바른 owner |
|---|---|---|
| `@` | declaration 시작인가 expression 위치인가 | `Annotation`, `AtControlExpr`, `ImplicitAtExpr` |
| `#` | attached literal opener인가 role word인가 | hash literal dispatcher 또는 `HashTag` |
| `(` | 현재 parser goal과 comma/arrow lookahead | `ParenExprSyntax` 또는 `ParenTypeSyntax` |
| `{` | 부모 owner가 block/value/closure를 요구하는가 | `Block`, `ValueBody`, `ClosureExpr` |
| `where` | type alias, annotation, schema field, callable tail 중 어디인가 | refinement/schema/generic owner |
| `*` | argument prefix, axis, arithmetic, capture/type인가 | owner별 parselet/production |
| `**` | prefix인가 양 operand 사이인가 | named unfold 또는 linear product |
| `***` | parameter/type suffix인가 | named rest |
| `^` | attachment, RHS, enclosing unit/index goal | transpose, power, unit exponent, slice anchor |
| `::name` | expression expected variant인가 pattern인가 | `ExpectedVariantExpr` 또는 `VariantPattern` |
| `match` | explicit subject인가 loop 직후인가 | explicit/implicit `MatchSubjectSlot` |
| `return`/`ret` | control target owner | callable transfer 또는 local value transfer |

### 15.2 input supply를 기록한다

생략된 source가 있을 때에는 “optional”이라고만 쓰지 말고 공급 종류를
기록한다.

| 공급 ID | owner | 공급 방식 |
|---|---|---|
| `MATCH_EXPLICIT` | `MatchCore` | source의 `Expr` |
| `MATCH_LOOP_OUTCOME` | loop 뒤 `MatchCore` | `ImplicitPreviousConstruct(loop_id)` |
| `CLAUSE_FUNCTION_SUBJECT` | `MatchArmSequence` | parent function parameter |
| `VARIANT_EXPECTED` | `VariantPattern` | expected type |
| `POSTFIX_BASE` | Pratt postfix | previous left expression |
| `CONTROL_TARGET` | transfer | lexical control target |
| `STORED_PARAMETER_EXPANSION` | stored parameter | synthesized field/input/init |

이 표는 parser implementation과 documentation이 서로 다른 “암시적 문법”을
발명하지 않도록 한다.

## 16. 양성·음성·경계 예제 묶음

### 16.1 current 양성: rightward local binding

`RightwardLocalBindingSurface`는 statement-only이고 target은 새 identifier
하나다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
decode(packet) -> $message: Message
process(message)
```

첫 줄의 RHS는 `$message` fresh local을 만들며 값을 반환하는 expression이
아니다.
member, index, 기존 place 또는 pattern을 target으로 쓸 수 없고 chaining도
현재가 아니다.

### 16.2 current 음성: expression 내부 rightward binding

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let result = (decode(packet) -> $message)
// RIGHTWARD_LOCAL_BINDING_STATEMENT_ONLY
```

괄호를 썼다고 statement surface가 expression primary로 승격되지 않는다.

### 16.3 current 경계: cast token attachment

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let parsed = value as? Int
```

lexer는 `as`와 `?`를 별 token으로 낼 수 있지만 두 token 사이 trivia는
허용하지 않는다.
formatter는 `as?`로 canonicalize한다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
let parsed = value as ? Int
// CAST_MODIFIER boundary 위반
```

### 16.4 current 경계: loop outcome match

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
for item in items {
    if shouldRetry(item) {
        break item
    }
    consume(item)
}
match {
    ::break(_)  => retry()
    ::completed => finish()
}
```

semicolon과 intervening item이 없으므로 `match` subject는 preceding loop
outcome에서 공급된다.
문서 도구가 source에 없는 가짜 subject expression을 삽입해서는 안 된다.

## 17. production을 찾는 경로별 체크리스트

### 17.1 declaration을 찾을 때

1. source root item production을 찾는다.
2. annotation wrapper 여부를 확인한다.
3. introducer에서 concrete declaration owner로 간다.
4. visibility/profile/modifier를 owner admission과 대조한다.
5. header의 type/parameter/contract goal을 각각 연다.
6. body owner와 statement boundary를 확인한다.
7. HIR identity와 namespace/coherence 규칙을 확인한다.

### 17.2 type을 찾을 때

1. 위치가 `TypeRef`인지 `NonFunctionTypeRef`인지 확인한다.
2. `TypePrimary` 또는 prefix ownership qualifier를 고른다.
3. generic argument와 static/error argument를 구분한다.
4. type Pratt binding power로 `&`, `|`, `?`를 묶는다.
5. refinement/where가 어느 parent의 tail인지 확인한다.
6. normalization, variance, lifetime, ownership을 checker에서 판정한다.

### 17.3 expression을 찾을 때

1. 일반/predicate/slice-index Pratt entry를 고른다.
2. prefix 또는 primary를 읽는다.
3. postfix base 공급을 보존한다.
4. binding power와 attachment policy를 적용한다.
5. short-circuit와 evaluation-once 요구를 MIR로 넘긴다.
6. overload/effect/error/ownership admission을 적용한다.

### 17.4 pattern을 찾을 때

1. match/binding/parameter 중 context를 먼저 고른다.
2. expected type 또는 explicit qualifier 공급을 기록한다.
3. alternative마다 같은 binding set과 compatible mode인지 검사한다.
4. 성공 전까지 binding/move를 transaction으로 보유한다.
5. exhaustiveness와 unreachable arm을 검사한다.
6. failure edge에 binding이나 partial move가 새지 않는지 확인한다.

### 17.5 collection을 찾을 때

1. attached hash sigil 또는 plain bracket owner를 고른다.
2. literal과 comprehension commitment를 구분한다.
3. materialization label과 runtime map key를 구분한다.
4. index suffix에서는 slice 전용 Pratt terminator를 쓴다.
5. 1-based logical coordinate와 collection별 axis 정책을 적용한다.
6. view/copy/ownership 및 failure-before-commit을 MIR에서 보존한다.

## 18. Preview source root로 넘어가는 경계

<!-- deeplus-status-fence: PREVIEW_GATED -->

Preview 문법은 stable `Deeplus`의 숨은 대안이 아니다.
별도 진입점 `DeeplusPreview`와 파일 선두의 `PreviewGate`를 요구한다.

```ebnf
DeeplusPreview ::= PreviewLibrarySourceFile
                 | PreviewExecutableSourceFile
                 | PreviewScriptSourceFile

PreviewGate ::= "#" "preview" "(" PreviewFeatureList ")"
                LineBreakBoundary
```

gate 이름이 catalog에 존재하고 활성화 가능한 Preview feature여야 하며,
source role이 Preview root로 선택되어야 한다.
gate가 있다는 사실만으로 nonactivatable Preview Design을 켤 수 없다.

현재 gated FFI surface는 `PreviewFfiDecl`,
`PreviewFfiFunctionDecl`, `PreviewFfiBlockDecl`에서 찾는다.
구문 분석 뒤에도 ABI-safe type, unsafe proof, effect/error 및 backend
지원 판정이 남는다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(value: Int) -> Int
```

이 예제는 Preview source root에서만 후보가 된다.
stable root에 gate를 무시하고 FFI declaration만 주입하는 구현은
source-root commitment를 위반한다.

## 19. Recovery production을 읽는 법

<!-- deeplus-status-fence: RECOVERY_ONLY -->

`RecoverySyntax` 아래 production은 사용 가능한 대체 syntax 목록이 아니다.
parser가 폐기되었거나 잘못된 spelling을 정밀하게 인식하여 하나의
교정 진단과 안정적인 CST를 만들기 위한 owner다.

대표 production은 다음과 같다.

- `RecoveryNullLiteral`
- `RecoveryEmptyIndexSuffix`
- `RecoveryCustomOperatorDeclaration`
- `RecoveryGenericEntryFunctionDecl`
- `RecoveryFacetPackExpr`
- `RecoveryFacetType`
- `RecoveryNamedRestDoubleStar`
- `RecoveryFunctionTypeNamedRestDoubleStar`
- `RecoveryLazyBindingAt`
- `RecoveryUnitMiddleDot`
- `RecoveryQuarantineScope`

recovery 성공의 공통 결과는 admitted semantic node 0개다.
formatter가 recovery spelling을 current spelling으로 조용히 정본화해서도
안 된다.
명시적 fix-it은 사용자가 적용하기 전까지 source를 바꾸지 않는다.

<!-- deeplus-example: illustrative; status: RECOVERY_ONLY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
let missing = null
let invalid = values[]
```

첫 줄은 `RecoveryNullLiteral`, 둘째 줄은
`RecoveryEmptyIndexSuffix`가 정확한 진단을 위한 CST를 만들 수 있다.
둘 다 current value 또는 index operation을 만들지 않는다.

named rest의 옛 `**` suffix도 같은 원칙이다.

<!-- deeplus-example: illustrative; status: RECOVERY_ONLY; authority-source: spec/frontend/frontend-model.json -->
```deeplus
def legacy(options**: Record) -> Unit = {
}
// parameter owner에서는 options***: Record로 교정
```

call의 prefix `**options`는 current이지만 parameter suffix `options**`는
recovery다.
token 모양만으로 둘을 한꺼번에 제거하면 current named unfold까지
손상한다.

<!-- deeplus-status-fence: CURRENT -->

## 20. 독자와 구현자를 위한 최종 판정표

문법 질문에 답할 때에는 최소한 다음 여덟 항목을 기록한다.

| 항목 | 기록할 내용 |
|---|---|
| source role | library/executable/script 및 stable/Preview root |
| structural owner | 가장 작은 concrete production |
| nested goal | declaration/type/expression/predicate/slice/pattern/block |
| input supply | explicit 또는 정확한 implicit supply ID |
| boundary | attachment, line break, separator, lookahead commitment |
| profile | STABLE/PREVIEW/RECOVERY |
| admission | owner별 checker 조건과 실패 진단 |
| lowering | CST/AST/HIR/MIR 중 책임 단계와 관측 순서 |

이 표를 채우지 않은 설명은 대개 “token이 보인다”는 수준에 머문다.
반대로 표를 채우면 560개 production을 복제하지 않고도 독자가 정확한
권위 source로 이동하고, parse 가능성과 현행 언어 허용을 구별하며,
부착·입력 공급·평가 순서의 빈틈을 찾을 수 있다.
