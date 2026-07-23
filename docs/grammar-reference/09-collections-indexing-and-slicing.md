# 컬렉션, 인덱싱, 슬라이싱

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 value-level collection literal, 닫힌 built-in bracket carrier
matrix, 1-based logical coordinate, slice를 설명한다.

현행 value literal과 별도의 literal-shaped *type-position* 제안을 혼동하면
안 된다. type spelling `[T]`, `#mut[T]`, `#set{T}`, `#map{K: V}`,
`${label: T}`는 `PREVIEW_DESIGN`, `nonactivatable`이며 이 Reference가
현행으로 만들지 않는다.

예제는 corpus의 `expected_outcome: accept`,
`source_activation: none`인 항목이다. 제품 parser/checker/lowering/runtime/
tooling 실행은 `NOT_RUN`이다.

## 문법

### 값 리터럴

```ebnf
ListLiteral        ::= "[" ExpressionList? "]"
BoundedListLiteral ::= "[" StaticIntLiteral ".." StaticIntLiteral
                       ":" ExpressionList? "]"
MutListLiteral     ::= "#" "mut" "[" ExpressionList? "]"
SetLiteral         ::= "#" "set" "{" ExpressionList? "}"
MapLiteral         ::= "#" "map" "{" MapEntryList? "}"
MapEntry           ::= Expr ":" Expr | NamedUnfoldArgument
NamedUnfoldArgument ::= "**" Expr

TypedMaterializationExpr ::= TypeRef MaterializationBody
MaterializationBody      ::= "${" MaterializationEntryList? "}"
```

ordinary immutable List는 `[...]`, MutableList value는 `#mut[...]`, Set은
`#set{...}`, Map은 `#map{...}`다. Record/materialization은 `${...}` 또는
`Type${...}`다. prefix와 body는 결합되어 있고 collection identity를 서로
바꾸지 않는다.

```ebnf
ComprehensionExpr    ::= "[" Expr ComprehensionClause+ "]"
MapComprehensionExpr ::= "#" "map" "{" MapEntry ComprehensionClause+ "}"
SetComprehensionExpr ::= "#" "set" "{" Expr ComprehensionClause+ "}"
```

### 수치 배열

```ebnf
NumericArrayLiteral ::= ShapeInferredArrayLiteral
                      | ShapeInferredColumnVectorLiteral
                      | ExactShapeArrayLiteral
ShapeInferredArrayLiteral        ::= "#" "[" ExpressionList? "]"
ShapeInferredColumnVectorLiteral ::= "#" "[" Expr (";" Expr)+ "]"
ExactShapeArrayLiteral           ::= "#" StaticDimensionList
                                     "[" ArrayInitializer? "]"
```

`#[1, 2, 3]`은 row vector, `#[1; 2; 3]`은 column vector다. `#2,3[...]`
같은 exact shape는 dimension을 명시한다. comma는 현재 axis의 element,
semicolon run은 더 깊은 axis boundary를 구분한다. NumericArray는 List가
아니며 List index evidence를 상속하지 않는다.

### 인덱스와 슬라이스

```ebnf
IndexSuffix   ::= "[" SliceAxisList "]"
SliceAxisList ::= SliceAxis (";" SliceAxis)*
SliceAxis     ::= SliceRange | SliceIndexExpr | AxisWildcard
SliceRange    ::= SliceBound (".." | "..<") SliceBound
SliceBound    ::= SliceIndexExpr | "^" | "$" | "^" OffsetExpr | "$" OffsetExpr
AxisWildcard  ::= "*"
```

index suffix에는 axis가 하나 이상 있어야 한다. slice bound에서 `^`는 첫
logical coordinate, `$`는 마지막 logical coordinate다. `*`는 axis
selector가 허용된 곳에서만 complete axis를 뜻한다.

## 허용과 정적 의미

### 컬렉션 identity

- `List`, `Map`, `Set`, `String`, `Bytes`, Tuple, Record는 immutable
  owned default다.
- `MutableList`는 List의 subtype이 아닌 별도 mutable owner다.
- Map key는 정확한 `K`의 runtime value다.
- Record field는 정적인 identifier label이다.
- Map과 Record 사이의 암시적 변환, dot-key 공유, identity collapse는 없다.
- Sequence conformance는 traversal evidence일 뿐 bracket, mutation,
  freeze, snapshot, view를 활성화하지 않는다.

`#set{...}`은 immutable `Set<T>`를 만든다. 모든 원소는 한 exact
normalized `T`여야 하고 equality와 `Keyable` evidence가 필요하다. literal
안의 중복은 조용히 제거하지 않고 거부한다. membership은 같은 `T`
domain에서만 검사하며 문자열화나 widening을 하지 않는다. 순회 순서는
semantic API가 아니므로 출력이나 직렬화 identity로 의존할 수 없고,
`set[1]` 같은 bracket access도 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
let ports: Set<Int> = #set{80, 443, 8080}
let servesTls = 443 in ports
```

`#set{443, 443}`은 duplicate literal 진단으로 거부된다. NaN 가능 Float는
암시적 `Keyable` evidence가 없으므로 별도 key policy 없이
`Set<Float64>`의 literal 원소 domain이 될 수 없다.

### 닫힌 대괄호 carrier 행렬

| carrier | index domain | 결과 |
|---|---|---|
| `List<T>` | `Int`의 `1..length` | read-only `T`, range는 `ReadonlyView<T>` |
| `ReadonlyView<T>` | source owner에서 보존된 coordinate | borrowed element 또는 coordinate-preserving view |
| `String` | `1..UnicodeScalarCount` | `Char` |
| `Bytes` | `1..byteCount` | `UInt8` |
| bounded List | 선언한 `L..U` | read-only element 또는 view |
| `NumericArray<T, rank R>` | axis별 typed coordinate, built-in default `1..dimension` | 모든 axis가 scalar면 `T`, 아니면 rank/shape-preserving view |
| `Map<K,V>` | 정확한 `K` | `V`, 없으면 `IndexError::keyNotFound` |
| Tuple | static `.1`부터 `.arity` | 정적으로 선택한 element |
| Record | static label | 정적으로 선택한 field |

현행 runtime bracket matrix는 `MutableList`, `FrozenList`, `ListSnapshot`을
명시적으로 제외한다. 사용자 type이 `Sequence`, `Indexable`,
`LogicalIndexDomain`을 만족해도 bracket이 생기지 않는다.

### 1-based 좌표와 슬라이스

ordinary ordered built-in은 `1..length`를 쓴다. storage offset 공식은
`logical_index - 1`이지만 storage offset은 source identity가 아니다.
index `0`, 음수 index, 음수를 from-end로 바꾸는 암시적 rewrite는 없다.

bounded List는 선언한 `L..U`, Map은 정확한 `K`를 사용하므로 1-based로
재작성하지 않는다. NumericArray built-in axis는 기본적으로 1-based다.

- `value[i..j]`: 양 끝을 포함하는 현행 canonical slice
- `value[i..<j]`: 허용되지만 noncanonical warning
- `value[^..$]`: 첫 coordinate부터 마지막까지
- `value[*]`: 허용된 axis owner의 full axis
- slice는 coordinate와 provenance를 보존하며 암시적으로 rebase/copy하지
  않는다.

단계 지정, 역방향 slice, mutable slice 대입, lifetime escape, isolation
crossing은 현행이 아니다.

## 평가·소유권·효과

collection literal의 element와 Map key/value는 owner sequence에 따라
왼쪽부터 평가된다. 실패한 element/key/value를 다른 collection kind로
재해석하지 않는다.

Map literal은 먼저 하나의 `MapLiteralPlan`을 만든다. direct entry와
`**base` Map unfold를 source order로 각각 한 번 평가하고, 같은 key가
다시 나오면 나중 값이 이기며 대체된 owner는 정확히 한 번 cleanup한다.
전체 plan이 끝나기 전 key/value 평가, unfold, equality/keyability,
Error, Defect 또는 Cancellation이 발생하면 partial Map은 publish되지
않고 이미 얻은 temporary를 역순으로 정리한다. hidden clone, key
stringification, widening은 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
let defaults = #map{
    "host": "localhost"
    "port": "80"
}
let production = #map{
    **defaults
    "port": "443"
}
```

결과의 `"port"`는 `"443"`이다. 이 `**defaults`는 runtime Map entry
unfold다. 호출의 `configure(**options)`가 Record의 정적 label을 공급하는
것과 identity·검사 단계·실행 의미가 다르다.

indexing은 owner와 index expression을 일반 평가 순서로 처리한다. 범위를
벗어난 sequence index와 없는 Map key는 지정된 `IndexError`를 일으키며
숨은 sentinel을 반환하지 않는다.

`ReadonlyView`는 nonowning projection이다. coordinate와 provenance를
보존하고 암시적으로 copy/rebase하지 않으며 owner보다 오래 살거나
isolation을 넘을 수 없다. live view와 충돌하는 mutation, move, freeze는
거부한다.

literal-shaped type design의 freeze/snapshot 책임은 미래 설계일 뿐 현행
syntax, bracket evidence, shareability, deep-freeze, actor-transfer proof를
주지 않는다.

attached postfix `A^`는 현행 NumericArray transpose다. operand를 한 번
평가하고 implicit element copy나 언어에서 관찰 가능한 allocation 권한
없이 owner-bounded readonly view를 만든다. 이 규칙은 backend의 내부
표현이나 incidental storage strategy까지 고정하지 않는다.
rank 2의 dimension vector `(R, C)`는 `(C, R)`가 되고 `(i, j)`는
`(j, i)`에 투영된다. 여기서 `(R, C)`는 의미를 설명하기 위한 추상 shape
tuple이며 source type spelling이 아니다. 현행 shape 표면은
`NumericArrayType`의 `"#" StaticDimensionList "[" TypeRef "]"` 문법,
예를 들어 `#2,3[Int]`를 따른다.
rank 1은 row/column orientation witness가 있어야 하며 이를 뒤집는다.
view는 원본의 1-based logical coordinate, provenance, lifetime과 isolation
경계를 보존하고 complex adjoint를 뜻하지 않는다.

## 현행 예제

현행 예제 `EX-R51a1-009`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let names: List<String> = ["Ada", "Grace", "Edsger"]
```

세 element는 왼쪽부터 한 번씩 평가되고 exact `String` domain을 만족한 뒤
immutable `List<String>` 하나가 commit된다. 논리 coordinate는
`1..3`이므로 `names[1]`은 `"Ada"`다. element 평가가 실패하면 partial
List를 publish하지 않고 이미 만든 temporary를 역순 cleanup한다. 이
예제는 정적 설계이며 실제 collection allocator와 backend 실행은
`NOT_RUN`이다.

현행 예제 `EX-R51VOI-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let ordinary = [10, 20, 30]
let first = ordinary[1]
let bounded = [3..5: 10, 20, 30]
let declaredFirst = bounded[3]
```

`ordinary`는 coordinate `1..3`을 가지므로 `first`의 타입은 `Int`, 값은
`10`이다. bounded List는 저장 offset과 별개로 선언 coordinate `3..5`를
identity로 가지며 `declaredFirst`도 `Int` 값 `10`이다. `ordinary[0]`이나
`bounded[1]`은 0-based 또는 rebased access로 바꾸지 않고
`IndexError`로 끝난다. owner와 index를 한 번씩 평가하며 실패 시 원
collection은 변하지 않는다. 제품 indexing 실행은 `NOT_RUN`이다.

현행 예제 `EX-R51VOI-006`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let ports = #map{ "https": 443 }
let secure = ports["https"]
```

literal은 key `String`, value `Int`인 immutable `Map<String, Int>`를 만든다.
Map plan은 key와 value를 source order로 한 번씩 평가한 뒤 전체 성공에서만
publish한다. 정확한 key lookup의 결과 `secure`은 `Int` 값 `443`이다.
없는 key는 sentinel이나 `Option`으로 바꾸지 않고
`IndexError::keyNotFound`를 낸다. 실제 hashing·allocation·lookup 실행은
`NOT_RUN`이다.

현행 예제 `EX-R51VOI-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let matrix = #2,2[1, 2; 3, 4]
let topLeft = matrix[1; 1]
let firstRow = matrix[1; *]
```

`matrix`는 element `Int`, rank 2, shape `(2, 2)`의 NumericArray다. 두
scalar axis를 고른 `topLeft`는 `Int` 값 `1`이고, 둘째 axis의 `*`를 남긴
`firstRow`는 source owner에 묶인 rank-1 readonly view다. axis는 모두
1-based이며 `matrix[0; 1]`은 storage offset으로 rewrite하지 않는다.
view는 copy가 아니고 원본의 coordinate·provenance·lifetime을 보존한다.
실제 shape checker와 backend view 실행은 `NOT_RUN`이다.

현행 예제 `EX-R48-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let row = #[1, 2, 3]
let column = #[1; 2; 3]
let explicit = #3,1[
    1;
    2;
    3;
]
```

`row`와 `column`은 같은 세 `Int`를 담지만 각각 row/column orientation이
다른 rank-1 NumericArray다. `explicit`은 rank 2 shape `(3, 1)`이므로
`column`과도 rank identity가 같지 않다. element 수가 선언 shape와 맞지
않으면 partial array를 만들지 않고 shape 진단으로 거부한다. 연산자는
extent만 보고 orientation이나 rank를 암시 변환하지 않으며 제품
NumericArray 실행은 `NOT_RUN`이다.

현행 예제 `EX-R51VOI-008`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let values = [10, 20, 30, 40]
let middle = values[2..$]
let sameCoordinate = middle[3]
```

`middle`은 source coordinate 2부터 4를 고르며 rebase하지 않으므로
coordinate 3을 그대로 사용한다. 따라서 `sameCoordinate`의 타입은 `Int`,
설계상 값은 `30`이다. slice는 `ReadonlyView<Int>`이고 원본 `values`를
한 번 평가한 뒤 inclusive bounds를 검증한다. bounds failure에서는 view를
publish하지 않으며, owner보다 오래 살거나 conflicting mutation과 함께
사용할 수 없다. copy/rebase와 제품 실행은 모두 주장하지 않는다.

현행 예제 `EX-R48E-094`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public data class Config {
    +let endpoint: Url
    +let retryCount: Int
}

public let defaultConfig = Config${
    endpoint: Url!("https://example.com")
    retryCount: 3
}
```

`Config${...}`는 runtime Map이 아니라 정적 label과 field type이 닫힌
`Config` materialization이다. `endpoint`와 `retryCount` initializer를
source order로 한 번씩 평가하고 label uniqueness, constructor/ownership
조건을 모두 통과한 뒤 `Config` 값을 publish한다. 문자열 key lookup이나
Map-to-Record 변환은 없고, 어느 field가 실패하면 partial `Config`와
남은 owner를 노출하지 않는다. 실제 constructor/lowering 실행은
`NOT_RUN`이다.

## 거부되거나 격리된 형식

| 형식 또는 주장 | 판정 |
|---|---|
| ordinary sequence의 `values[0]` | 거부; 기본 domain은 1부터 시작 |
| 음수 from-end index | 거부 |
| `value[]` | recovery-only, `INDEX_SUFFIX_REQUIRES_AXIS` |
| `value[..]` | 거부; 두 bound 모두 필요 |
| `value[i..>j]`, `value[i...j]` | range로 거부 |
| `value[i..<j]` | 허용되지만 noncanonical warning |
| stepped/descending slice | 없음 |
| mutable slice assignment | 없음 |
| conformance가 `[]` 활성화 | nonactivatable |
| Map string key를 Record label로 취급 | 거부 |
| `#[...]`을 ordinary List로 취급 | 거부 |
| value literal spelling을 현행 type sugar로 취급 | 잘못된 해석; type-position 제안은 nonactivatable |

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### PREVIEW_NONACTIVATABLE — 리터럴 형태 컬렉션 타입 후보

다음 type-position 표면은 수용된 bounded Preview 설계이지만 현행
parser route와 source gate가 없는 비활성 후보다.

| 후보 표면 | 정규화 대상 |
|---|---|
| `[T]` | `List<T>` |
| `#mut[T]` | `MutableList<T>` |
| `#set{T}` | `Set<T>` |
| `#map{K: V}` | `Map<K, V>` |
| `${label: T, ...}` | 닫힌 필수 정적 label Record row |

이 표면은 CST에서만 spelling을 보존하는 sugar 후보다. HIR, API digest,
타입 identity, ABI와 serialization은 named canonical type을 사용하며
새 wrapper나 subtype을 만들지 않는다. type, value, pattern, index의
parser goal은 계속 분리된다. `#mut[`, `#set{`, `#map{`, `${`는
no-trivia attached candidate이고 `#N[T]`는 별도의 NumericArray
`SharpShapeType` owner다.

`[T | U]`는 명시적인 `List<T | U>`일 뿐 heterogeneous Union을 자동
추론하지 않는다. Map key는 runtime `K` 값이고 Record label은 정적
`Identifier`이므로 두 domain을 서로 변환하거나 dot-key projection을
추론하지 않는다. 이 type sugar는 bracket, mutation, Copy, deep-freeze,
`ShareSafe`, `Transferable`, actor crossing, Trait witness 또는 operator
glyph evidence를 부여하지 않는다.

소유권 후보의 최소 의미는 다음과 같다.

- `freeze`는 mutable owner를 move로 받아 성공 commit 뒤 정확히 한 번
  소비하고, 실패하면 정확한 원래 owner와 값 상태를 반환한다. shallow
  전이이며 live borrow가 있으면 거부한다.
- `snapshot`은 mutable owner를 borrow하고 독립적인 point-in-time 불변
  결과를 만든다. source는 유지되며 이후 mutation이 snapshot을 바꾸지
  않는다.
- `view`는 owner-bounded nonowning projection이라는 책임만 정해졌고
  새로운 carrier 이름은 선택되지 않았다. 좌표와 provenance를 보존하며
  mutation, move, freeze, owner escape와 isolation crossing에 충돌한다.

현행 `MutableList<T>::freeze`와 `snapshot`의 결과 identity인
`FrozenList<T>`와 `ListSnapshot<T>`는 바뀌지 않는다. 이를 `List<T>`로
합치는 successor migration은 alias나 자동 rewrite가 아니며 API, ABI,
serialization, indexing, actor shareability 검토가 끝날 때까지
deferred다.

비활성 source 예:

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/literal-shaped-collection-design.json -->
```deeplus
let names: [String]
let cache: #mut[String]
let colors: #set{Color}
let lookup: #map{String: UserId}
let row: ${id: UserId, name: String}
```

위 코드는 현행 accept 예제가 아니다. 도입에는 exact type-goal grammar와
recovery, canonical identity와 closed Record row 판정, CST/HIR/API
정규화, transactional freeze/snapshot lowering, positive/negative/
boundary/migration 실행 증거, formatter/LSP 보존 및 별도 Design_
activation authority가 모두 필요하다.

이 Preview 문서화는 source activation, 구현 권한, 기존 feature P1 폐쇄,
새 feature P1 생성 또는 제품 PASS가 아니다. OPEN feature P1은 정확히
22개이고 별도 `M13-A002..005` action도 그대로 OPEN이며 제품 lane은
`15/15 NOT_RUN`이다.

<!-- deeplus-status-fence: CURRENT -->

corpus의 `EX-R51VOI-009`는 migration/noncanonical 설명에서만 사용하고
`SLICE_HALF_OPEN_RANGE_NONCANONICAL`을 함께 표시해야 한다.

```deeplus
let values = [10, 20, 30, 40]
let prefix = values[1..<4]
```

## 상호작용

- `[`는 List, bounded List, comprehension, index suffix가 공유하며 parent
  expression 위치가 owner를 정한다.
- attached `#mut[`, `#set{`, `#map{`, NumericArray `#[`/`#N[`는 서로 다른
  value owner다.
- `${...}`는 expression mode의 materialization이며 String scanner mode의
  interpolation과 owner가 다르다.
- `*`는 axis wildcard, positional unfold, multiplication, unit
  multiplication을 문맥별로 가진다.
- `**`는 named unfold 또는 infix linear product다. named-rest declaration은
  `***`다.
- Pattern form은 별도 parser goal이며 value literal 허용을 자동 재사용하지
  않는다.
- collection이 immutable하다는 사실만으로 actor shareability나
  transferability가 증명되지 않는다.

## 정본 근거

- [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- [`spec/contracts/value-operator-indexing-coherence.json`](../../spec/contracts/value-operator-indexing-coherence.json)
- [`spec/contracts/literal-shaped-collection-design.json`](../../spec/contracts/literal-shaped-collection-design.json)
- [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- [`spec/language.md`](../../spec/language.md)
- [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
