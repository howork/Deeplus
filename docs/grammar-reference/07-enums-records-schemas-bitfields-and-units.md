# 열거형, 레코드, 스키마, 비트필드, 단위

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 Deeplus `0.1.2-internal`의 유한 명목 합(Enum), 정적 label
Record, 선언된 schema materialization, unsigned bitfield/flags 및 exact
measure/unit 표면을 설명한다.

| 영역 | 현행 상태 |
|---|---|
| bare Enum case 이름, named/positional/mixed payload, `. + *. *+` 멤버 도달성 | `CURRENT` |
| static-label Record와 typed schema materialization | `CURRENT` |
| 얕은/깊은 same-type derivation `!{}`/`!!{}` | `CURRENT` |
| unsigned strict bitfield와 `bitfield#flags` | `CURRENT` |
| measure literal, 단위 곱/몫/거듭제곱, exact-ratio catalog | `CURRENT` |
| dynamic/calendar/market conversion | 명시적 `STDLIB_PROFILE`/provider만 |
| successor uniform-within-case payload와 final-dot-only Enum member | `PREVIEW_DESIGN_NONACTIVATABLE` |
| Enum order/display/subset, raw/ABI profile, external residual spelling, A3, empty Enum | `PREVIEW_DESIGN_NONACTIVATABLE` 또는 deferred |
| 제품 parser/checker/MIR/runtime/formatter/LSP | `NOT_RUN` |

현행 mixed Enum payload와 현행 marker reachability를 바꾸지 않는다.
비활성 successor 설계는 current syntax가 아니다. semantic P0/P1 및
product support를 이 장이 변경하지 않으며 product lane은 정확히
`15/15 NOT_RUN`이다.

## 문법

### Enum 선언과 case

```ebnf
EnumDecl ::= TopLevelVisibility? "enum" Identifier
             TypeParameterList? EnumBody

EnumBody ::= "{" (EnumCommaCaseSequence | EnumLayoutBody)? "}"
EnumCommaCaseSequence ::= EnumCaseCore ("," EnumCaseCore)+ ","?
EnumLayoutBody ::= EnumCaseDecl* EnumMemberDecl*

EnumCaseDecl ::= EnumCaseCore StatementBoundary?
EnumCaseCore ::= Identifier EnumCasePayload?
EnumCasePayload ::= "(" EnumCaseFieldList? ")"
EnumCaseFieldList ::= EnumCaseField ("," EnumCaseField)* ","?
EnumCaseField ::= Identifier TypeAnnotation | TypeRef

EnumMemberDecl ::= MemberFunctionDecl
                 | TypeSideFieldDecl
                 | TypeSideMemberFunctionDecl
                 | AccessorPropertyDecl
```

Enum case에는 `case` keyword를 쓰지 않는다. `case`는 ordinary identifier다.
case는 `draft`, `blocked(reason: String)`, `value(Int)`처럼 bare
identifier로 선언한다.

한 줄 body에서는 둘 이상의 case를 comma로 나열할 수 있다.
여러 줄 body는 layout/statement boundary로 case를 나열하며 comma-list
문법과 섞지 않는다. payload field 하나는 `name: Type`인 named field
또는 `Type`인 positional field다. 현행 문법은 한 case 안의 named와
positional field가 섞이는 mixed payload도 허용한다.

값 표면은 expected context의 `::case`, 명시적 owner의 `Enum::case`,
그리고 payload가 있을 때 뒤따르는 argument list를 사용한다. pattern은
`::case(patterns)` 또는 `Enum::case(patterns)`이다. dot-case shorthand와
`case` declaration keyword는 없다.

Enum member function은 Class member와 같은 source glyph
`.`, `+`, `*.`, `*+`를 현행 reachability domain으로 사용한다. 이
marker가 case identity, ordinal, raw value 또는 Trait witness를 뜻하지는
않는다.

### Record와 materialization

```ebnf
TypedMaterializationExpr ::= TypeRef MaterializationBody
MaterializationBody ::= "${" MaterializationEntryList? "}"

MaterializationEntryList ::= MaterializationEntry
                             (MaterializationSeparator
                              MaterializationEntry)*
                             MaterializationSeparator?

MaterializationEntry ::= Identifier
                       | Identifier ":" Expr
                       | StringLiteralExpr ":" Expr
                       | NamedUnfoldArgument

NamedUnfoldArgument ::= "**" Expr
MaterializationSeparator ::= "," LineBreakBoundary?
                           | LineBreakBoundary

PrototypeDerivationSuffix ::= ("!" | "!!") DerivationBody
DerivationBody ::= "{" MaterializationEntryList? "}"
```

Record는 정적으로 알려진 label row를 갖는 structural value domain이다.
Map의 runtime key domain과 다르다.

- `${ id, name }`: 문맥에 따라 구조적 또는 typed materialization으로
  해석되는 본문.
- `Target${ id: value }`: target의 visible schema/construction row에 대한
  타입이 지정된 label materialization.
- `**record`: 정적으로 알려진 label을 call/materialization에 펼침.
- `source!{ field: value }`: 같은 명목 타입의 shallow derivation.
- `source!!{ field: value }`: deep-clone 책임이 허용하는 같은 명목 타입의
  deep derivation.

field pun `id`는 `id: id`로 정규화되며 lexical binding 하나를 정확히
한 번 읽는다. `expr${...}`는 derivation이 아니다. 같은 타입의
derivation은 반드시 `!{...}` 또는 `!!{...}`를 사용한다.

### Schema

```ebnf
SchemaDecl ::= TopLevelVisibility? "schema" Identifier
               TypeParameterList? SchemaBody
SchemaBody ::= "{" SchemaFieldSequence? "}"

SchemaFieldSequence ::= CommaSchemaFields | LayoutSchemaFields
CommaSchemaFields ::= SchemaFieldDecl ("," SchemaFieldDecl)* ","?
LayoutSchemaFields ::= LineBreakBoundary LayoutSchemaFieldDecl
                       (LineBreakBoundary LayoutSchemaFieldDecl)*
                       LineBreakBoundary?

SchemaFieldDecl ::= Identifier TypeAnnotation Initializer?
                    SchemaConstraint* StatementBoundary?
LayoutSchemaFieldDecl ::= Identifier TypeAnnotation Initializer?
                          SchemaConstraint*
SchemaConstraint ::= "where" Expr
```

schema는 required label, optional/default field, field type, construction
authority와 constraint를 선언한다. schema construction은
`SchemaName${...}`이며 ordinary Class constructor `Type!(...)`와 별도
domain이다. layout form과 comma form을 한 body에서 임의로 섞지 않는다.

### Bitfield와 flags

```ebnf
BitfieldDecl ::= TopLevelVisibility? BitfieldIntroducer Identifier
                 BitfieldBackingClause BitfieldOrderClause BitfieldBody
BitfieldIntroducer ::= "bitfield" HashTag?
BitfieldBackingClause ::= "backing" TypeRef
BitfieldOrderClause ::= "order" "::" "lsb0"

BitfieldBody ::= "{" BitfieldLayoutSection BitfieldMemberDecl* "}"
BitfieldLayoutSection ::= BitfieldSlotDecl+ | FlagSlotDecl+

BitfieldNamedSlot ::= MemberVisibility? Identifier ":"
                      StaticIntLiteral BitfieldDefault?
BitfieldReservedSlot ::= "_" ":" StaticIntLiteral
FlagNamedSlot ::= MemberVisibility? Identifier
```

일반 bitfield slot은 `name: width`, reserved bit은 `_: width`로 쓴다.
현행 backing은 `UInt8`, `UInt16`, `UInt32`, `UInt64`, `UInt128` 중 exact
unsigned fixed-width 타입이어야 하며 order는 `::lsb0`이다. 암시적
padding은 없으므로 남는 폭도 reserved slot으로 명시한다.

`bitfield#flags`는 유한 flags universe를 선언한다. named flag는 각각 한
bit identity를 갖고 `||`, `&&`, `^^`, `~~`의 flags 전용 intrinsic
결과가 같은 명목 flags 타입을 보존한다. 이 연산 결과를 `Bool`로
해석하지 않는다.

### Measure와 unit catalog

```ebnf
MeasureLiteralExpr ::= NumericLiteral "[" UnitExpr "]"
UnitExpr ::= PrattUnitExpr
UnitPrimary ::= Identifier | QualifiedPath | "(" UnitExpr ")"
UnitPostfixParselet ::= "^" SignedStaticInt
UnitInfixOperator ::= "*" | "/"

UnitCatalogDecl ::= TopLevelVisibility? "unit" "catalog" Identifier
                    UnitCatalogBody
UnitCatalogEntry ::= ExactRatioUnitConversionDecl
                   | Identifier "=" UnitExpr StatementBoundary
ExactRatioUnitConversionDecl ::= "unit" Identifier "equalsRatio"
                                 MeasureLiteralExpr "/"
                                 StaticIntLiteral StatementBoundary
```

`13[cm]`은 숫자와 unit expression을 결합한 measure literal이다.
`m/s`, `m*s`, `m^2`는 unit 차원 연산이며 일반 collection indexing과
다른 parser owner를 갖는다. 단위 symbol은 활성 unit catalog authority에서
유일하게 resolve되어야 한다.

core 변환은 exact ratio만 허용한다. calendar, currency 또는 관측 시점이
필요한 동적 변환은 명시적 stdlib/provider API와 policy를 요구한다.
그런 변환은 core exact-ratio conversion으로 암묵 변환되지 않는다.

## 허용과 정적 의미

### Enum identity, payload와 pattern

각 Enum은 하나의 명목 `EnumId`와 유한한 case universe를 소유하고 각
case는 별개의 `VariantId`를 갖는다. source declaration order는
직렬화 태그, 런타임 판별자, 순번, 원시 값, ABI, 레이아웃, 우선순위 또는
match winner가 아니다.

case 구성은 owner와 case를 먼저 resolve한 뒤 payload arity, named/positional
shape와 type를 검사한다. pattern도 scrutinee의 Enum owner 안에서
`VariantId`를 resolve하고 활성 payload만 분해한다. foreign/unknown case,
잘못된 arity/label/type, inactive payload projection은 guard나 ownership
commit 전에 거부한다.

현행 mixed payload는 그대로 current authority이다. 한 case 안에서
label-all, unlabel-all 또는 하나의 Record payload만 허용하는 successor
uniform profile은 비활성이며 자동 migration default가 없다.

한 case Enum은 의미적으로 허용되지만 warning, rewrite 또는 “Class로
바꾸라”는 tooling advice를 만들지 않는다. empty Enum은 현행 source
activation이 없다.

### Record, Map과 schema identity

Record label은 compile-time identifier identity이며 runtime String key가
아니다. 정규화된 Record row는 identity/digest를 위해 canonical order를
갖지만 source field expression은 작성 순서대로 평가한다.

typed materialization은 다음을 모두 검사한다.

1. target이 materialization authority를 공개하는 schema/Record domain인지;
2. required label이 모두 공급되었는지;
3. duplicate/unknown label이 없는지;
4. 각 value가 field type/refinement를 만족하는지;
5. default/computed field와 visibility가 허용되는지;
6. `**record`의 label row가 정적으로 알려지고 겹치지 않는지.

Map은 이 proof를 충족하지 않는다. `**map`을 named argument나 schema
field 공급자로 쓰지 않으며 runtime key를 static label로 승격하지 않는다.
`map.name`도 String key `"name"` projection이 아니다.

same-type derivation은 base의 정확한 명목 타입과 visible ConstructionRow를
보존한다. `!{}`는 shallow 책임, `!!{}`는 허용된 deep-clone 책임을
검사한다. 어느 표면도 새 structural conformance나 다른 nominal type을
만들지 않는다.

### Bitfield/flags layout

bitfield checker는 backing width와 slot 폭의 합이 정확히 일치하는지,
reserved slot이 명시되었는지, default/value가 폭에 맞는지 검사한다.
unknown bit, duplicate mask, width overflow, signed ambiguity와 layout
mismatch는 거부한다.

semantic field identity와 packed representation은 구분된다. bitfield
선언만으로 C bitfield ABI, endianness codec, foreign layout 또는
serialization을 추론하지 않는다. raw 관측은 명시적 `.raw`, raw에서
값을 만들 때는 checked `Type::fromRaw`를 사용한다. reserved bit가
0이 아니거나 값이 유효 범위를 벗어나면 checked conversion이 실패한다.

flags는 finite universe 밖의 bit를 허용하지 않는다. flags glyph는 이
명목 flags domain의 intrinsic이고 user Trait overload가 아니다.

### Measure와 exact unit

measure type은 representation과 dimension을 함께 보존한다. `Length`와
`Time`, `Length/Time`은 서로 다른 normalized dimension이며 exact-ratio
catalog 변환은 값과 차원을 동시에 검사한다.

- `asUnit(sample)`은 같은 dimension의 exact unit으로 변환한다.
- `scalarIn(sample)`은 명시한 unit의 scalar를 얻는다.
- measure product/quotient는 dimension을 곱하거나 나눈다.
- `Measure ^ StaticInt`는 별도 exact measure-power law를 따른다.
- unit symbol ambiguity, dimension mismatch 또는 provider 부재는
  deterministic diagnostic이다.

dynamic conversion admission은 profile 활성화, provider binding,
완전한 policy와 provider support를 모두 요구한다. 관측 시간, rounding,
failure/effect row, cache/replay authority를 숨길 수 없다.

## 평가·소유권·효과

- Enum owner/case binding과 formation plan은 payload expression 평가 전에
  결정한다. payload는 source order대로 정확히 한 번 평가한다. 실패하면
  성공한 temporary를 역순 정리하고 Enum value를 publish하지 않는다.
- Enum pattern의 structural test와 optional guard는 nonconsuming이며
  성공한 뒤에만 move/borrow/binding을 원자적으로 commit한다.
- Record/schema field expression과 field pun은 source order대로 각각
  한 번 평가한다. canonical label sorting이 evaluation order를 바꾸지
  않는다.
- same-type derivation은 새 값 하나를 만든다. shallow derivation은
  field responsibility를 그대로 보존하고, deep derivation은 identity
  map을 사용해 cycle을 종료시키고 공유 subgraph를 보존해야 한다.
  실패한 partial graph는 publish하지 않고 정리한다.
- bitfield field는 직접 mutate하지 않는다. 변경은 same-type derivation을
  사용한다. raw decode/encode의 endianness와 failure는 명시적이다.
- exact-ratio unit conversion은 숨은 provider lookup이나 I/O를 만들지
  않는다. dynamic provider conversion은 선언한 effect/error/authority를
  그대로 보존한다.
- 어떤 정적 materialization도 runtime, ABI 또는 product-support PASS를
  뜻하지 않는다.

## 현행 예제

다음 코드는 모두
[`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)의
원문이다. 별도 표기가 없으면 `expected_outcome: accept`,
`source_activation: none`,
`certification_status: design_static_product_not_run`이다. 제품 실행은
전부 `NOT_RUN`이다.

### `EX-R51e-009` — 한 줄 Enum comma list

```deeplus
public enum State { draft, active, blocked(reason: String) }
```

`case` keyword가 없고 case 이름을 직접 쓴다.

### `EX-R48E-014` — schema materialization

```deeplus
public schema UserRow {
    id: UserId
    name: String
    active: Bool = true
}

let row = UserRow${
    id: UserId!(13)
    name: "Sing"
}
```

`UserRow${...}`는 schema domain이며 ordinary constructor alias가 아니다.

### `EX-R51e-001` — materialization field pun

```deeplus
let id = 7
let name = "Ada"
let user = User${ id, name }
```

`id`와 `name`은 각각 같은 이름의 lexical binding을 정확히 한 번
공급한다.

### `EX-R51a1-BITFIELD-P-001` — unsigned strict bitfield

```deeplus
public bitfield PacketHeader
    backing UInt32
    order ::lsb0
{
    +version: 4
    +kind: 4
    +length: 16
    _: 8
}
```

### `EX-R51a1-BITFIELD-P-002` — bitfield materialization과 derivation

```deeplus
let header = PacketHeader${ version: 1, kind: 2, length: 1024 }
let changed = header!{ length: 2048 }
assert(changed.length == 2048)
```

### `EX-R51a1-BITFIELD-P-003` — checked raw conversion

```deeplus
let raw: UInt32 = header.raw
let ::ok(decoded) = PacketHeader::fromRaw(raw)
else ::err(error) => throw error
```

### `EX-R51a1-FLAGS-P-001`과 `EX-R51a1-FLAGS-P-002` — flags

```deeplus
public bitfield#flags Permission backing UInt8 order ::lsb0 {
    +read
    +write
    +execute
    _: 5
}
```

```deeplus
let access = Permission::read || Permission::execute
let toggled = access ^^ Permission::write
let inverse = ~~toggled
```

### `EX-R48-009`과 `EX-R48-010` — exact unit

```deeplus
use std::units::si
let distance = 13[cm]
let time = 2[s]
let speed = distance / time
```

```deeplus
use std::units::si
let d = 2500[m]
let km = d ~ asUnit(1[km])
let scalar = d ~ scalarIn(1[m])
```

### `EX-R48E1-031` — 명시적 dynamic provider profile

이 예제만 `source_activation: stdlib`이며 core exact-ratio 규칙이 아니다.

```deeplus
let converted = price ~ asUnitUsing(provider, 1[USD])
```

## 거부되거나 격리된 형식

| 형태 | 처리 |
|---|---|
| `case blocked(...)` declaration | 거부; bare case name 사용 |
| dot-case `.blocked` | 제거됨; `::blocked` 또는 `State::blocked` 사용 |
| 여러 줄 comma case list | 거부; layout case body 사용 |
| empty Enum | `PREVIEW_DESIGN_NONACTIVATABLE` |
| 현행 mixed payload를 자동 label-all/unlabel-all/Record로 rewrite | 금지 |
| successor uniform-within-case payload | `PREVIEW_DESIGN_NONACTIVATABLE` |
| successor final-dot-only member로 marker 자동 rewrite | 금지/비활성 |
| Enum order/display/subset 자동 합성 | `PREVIEW_DESIGN_NONACTIVATABLE` |
| Enum source order를 raw/tag/ordinal/layout/ABI로 사용 | 거부 |
| case-local Trait witness 생성/교체 | 거부 |
| runtime Map key를 Record/schema label로 사용 | 거부 |
| `**map`으로 named/schema label unfold | 거부 |
| ordinary Class에 `Type${...}`를 constructor alias로 사용 | 거부 |
| `expr${...}` same-type derivation | 거부; `!{}`/`!!{}` 사용 |
| bitfield signed/variable-width backing, implicit padding | 거부 |
| bitfield의 implicit raw/ABI/endianness conversion | 거부 |
| flags 결과를 Bool로 사용 | 거부 |
| calendar/currency 변환을 implicit exact-ratio core로 처리 | 거부 |

Enum successor의 `AUTO`/`VIA`, specialization, child/case-local parent
witness replacement, raw/ABI profile, external residual spelling와 A3는
활성화되지 않는다. static schema, 문서 또는 fixture의 존재는 P1 closure,
activation, publication, promotion 또는 product support를 만들지 않는다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### PREVIEW_NONACTIVATABLE — Enum successor 기본 계약

Enum successor는 current `EnumDecl`, mixed payload, case 철자와 네 marker를
그대로 둔 채 미래 profile의 identity/formation/evolution을 닫으려는
설계다.

**의미**

- 하나의 `EnumDescriptor`가 `EnumId`, normalized binder, frozen case
  universe와 order-independent `VariantId`를 소유한다.
- successor payload는 한 case 안에서 label-all, unlabel-all 또는 하나의
  Record payload 중 하나로 uniform하다. migration은 사용자가 inventory
  이후 선택하며 automatic rewrite 수는 0이다.
- formation plan은 owner/case를 payload 평가 전에 고정하고 left-to-right
  once evaluation, reverse temporary cleanup, failure publish 0을 보장한다.
- pattern partition은 exact/residual/guard/module-relative cell을
  구분한다. guard-only coverage는 total이 아니며 external residual은
  runtime unknown case를 제조하지 않는다.
- successor Enum instance member는 trailing `.` final method만 허용하는
  후보이다. Class slot/subtype/case witness를 만들지 않으며 current
  `.`, `+`, `*.`, `*+`를 자동 rewrite하지 않는다.
- ordinary Enum은 raw-free이고 semantic identity를 raw, serialization,
  discriminant, ordinal, layout와 foreign ABI에서 분리한다.
- Trait 합성이 별도 허용되더라도 whole Enum에 정확히 한 evidence
  origin만 생기고 case-local witness 수는 0이다.
- public/evolution residue는 여덟 독립 compatibility lane을 유지한다.

**의존성과 미해결 guard**

| OPEN P1 | 도입 전에 필요한 증거 |
|---|---|
| `CE-E-P1-001` | EnumId/VariantId universe, payload profile, one/empty boundary |
| `CE-E-P1-002` | active-only place, inline acyclicity, move/drop/replace/cancel |
| `CE-E-P1-003` | formation/evaluation/cleanup 및 explicit migration receipt |
| `CE-E-P1-004` | exact/residual/guard/module partition과 external residual fence |
| `CE-E-P1-005` | final-dot-only admission, zero Class slot/witness, migration diagnostic |
| `CE-E-P1-006` | raw/ordinal/FFI mapping 분리와 target ABI authority |
| `CE-E-P1-007` | whole-Enum synthesis manifest와 TCC evidence origin |
| `CE-E-P1-008` | complete API/evolution residue와 여덟 lane 독립성 |

정확히 여덟 P1이 모두 OPEN이다. `CE-E-P1-007`은
`TCC-P1-002..008` 전체에, raw/ABI는 별도 target authority와 receipt에
의존한다. current four-marker fixture와 mixed-payload fixture는 successor
도입 검토 중에도 변하지 않아야 한다.

**도입 조건**

Spec_/TypeSystem_의 descriptor와 source profile ratification, explicit
migration 선택, checker/MIR/xVM의 formation·place·cleanup 실행 증거,
partition/exhaustiveness corpus, raw/ABI 별도 authority, tooling migration
검증, lane별 evidence 및 Design_ 최종 activation 판정이 필요하다.

**비활성 예**

아래는 source가 아닌 상태 projection이다.

```text
candidate: enum_successor_profile
payload_policy: uniform_within_each_case
member_policy: final_dot_only
current_marker_rewrite_count: 0
automatic_payload_migration_count: 0
current_admission: false
open_guards: CE-E-P1-001..008
```

### PREVIEW_NONACTIVATABLE — Enum-derived capabilities

세 기능은 조정된 Preview 설계로 수용되어 있지만 current parser에
도달하는 source route는 없다.

1. **declaration-order semantic ordering**: 미래
   `enum#increasing` 또는 `enum#decreasing` 중 하나가 nominal,
   nonempty, payload-free, nongeneric Enum에 whole-Enum `Ord<E>` witness
   하나를 합성하는 후보이다. order vector는 raw/tag/ordinal/layout/ABI,
   match priority, range 또는 iteration이 아니다. explicit same-ground
   `Ord<E>`와 충돌하며 comparison glyph overload를 활성화하지 않는다.
2. **case display mapping**: 미래 case의 `~>` restricted String template
   후보이다. 한 inhabitable case가 mapping을 가지면 모두 정확히 하나씩
   가져야 한다. named payload는 read-only borrow binder이고 각
   interpolation hole은 이미 선택된 `Display` witness를 요구한다. hidden
   locale/provider, move, mutation, throw, suspension, spawn, escape와
   fallback은 없다. 이것은 serialization/parser/reverse map이 아니다.
3. **exact variant subset**: 미래 `+type Weekend = Sat | Sun` 같은 명시적
   associated alias 후보이다. subset identity는 같은 `EnumId`, frozen
   `VariantId` set과 universe digest이고 새 case, wrapper, storage, tag,
   allocation, raw mapping 또는 witness를 만들지 않는다. subset-to-owner는
   bounded widening, owner-to-subset은 `as?`/pattern 등 checked boundary를
   요구한다.

**의존성과 guard**

이 세 기능은 `CE-E-P1-004`, `CE-E-P1-007`, `CE-E-P1-008`과
`TCC-P1-002..008` 전체에 의존한다. ordering은 order-independent stable
VariantId와 별도의 order vector를, display는 total mapping과 기존
Display evidence를, subset은 `CE-E-P1-001`의 frozen universe를 추가로
필요로 한다. payload ordering, payload-bearing exact variant type, 제네릭
조건부 합성, 역파싱, 부분집합 순회/범위, 묶음 Trait derivation은
deferred다.

**도입 조건**

각 표면의 exact grammar/recovery/diagnostic이 ratify되고, generated
witness 충돌/coherence/termination 법칙과 HIR/MIR/API residue가 닫히며,
exhaustiveness·link permutation·formatter corpus가 독립 실행된 후
Design_이 별도로 활성화해야 한다. 한 기능의 증거가 다른 기능이나
product lane의 PASS로 전파되어서는 안 된다.

**비활성 source 예**

다음은 controlling Preview 설계의 의도를 보이는 예시이며 current
Deeplus source로 제출하면 `FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE`로
거부되어야 한다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
public enum#increasing Day {
    Mon
    Tue
    Wed
}
```

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
public enum Status {
    ready ~> "ready"
    failed(reason: String) ~> "failed: $reason"
}
```

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/enum-derived-capabilities.json -->
```deeplus
public enum Day {
    Mon
    Tue
    Wed
    Sat
    Sun
    +type Weekend = Sat | Sun
}
```

이 철자 예시는 activation도, corpus `accept`도, 구현 handoff도 아니다.
세 기능은 모두 `PREVIEW_DESIGN_NONACTIVATABLE`이며 관련 P1과
`15/15 NOT_RUN`을 그대로 유지한다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- **타입:** Enum은 명목 `EnumId`/`VariantId`, Record는 structural label
  row, schema는 construction authority를 가진 선언 domain이다.
  serialization/layout identity와 semantic identity를 섞지 않는다.
- **패턴:** Enum pattern은 exact case/payload를, Record pattern은
  statically known label subset을 연다. Class private representation과
  Map runtime key는 열지 않는다.
- **Trait:** Trait evidence는 whole Enum/type에 속한다. case membership,
  flags bit 또는 schema field는 witness를 만들지 않는다.
- **연산자:** flags glyph와 measure operators는 닫힌 built-in domain의
  intrinsic이다. extension/conformance가 새 glyph candidate를 만들지
  않는다.
- **생성:** `Type!(...)`, `Type${...}`, `source!{...}`,
  `source!!{...}`는 각각 constructor, typed materialization, shallow,
  deep same-type derivation이라는 서로 다른 책임 경계다.
- **소유권:** payload/field/resource의 move와 cleanup은 formation,
  materialization, pattern 및 derivation에서 보존된다.
- **직렬화/FFI:** Enum/bitfield 선언은 serialization tag나 foreign
  ABI를 암시하지 않는다. explicit codec/profile이 별도 authority를 가진다.
- **모듈:** unit symbol과 schema/construction visibility는 활성
  catalog/module authority를 따라 resolve된다.

## 정본 근거

- 정확한 Enum/schema/bitfield/unit/materialization 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- current data-domain, identity, materialization과 Preview fence:
  [`spec/language.md`](../../spec/language.md)
- Union/Enum/Record/bitfield/measure 타입 판정:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- formation, cleanup와 unit/bitfield 관찰:
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- 연산자/단위 계약:
  [`spec/contracts/value-operator-indexing-coherence.json`](../../spec/contracts/value-operator-indexing-coherence.json)
- 패턴 registry:
  [`spec/patterns/pattern-kinds.json`](../../spec/patterns/pattern-kinds.json)
- Prelude와 library profile:
  [`library/prelude/`](../../library/prelude/)
- 검토 예제:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
