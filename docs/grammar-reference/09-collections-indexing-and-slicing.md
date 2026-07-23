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

## 현행 예제

현행 예제 `EX-R51a1-009`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let names: List<String> = ["Ada", "Grace", "Edsger"]
```

현행 예제 `EX-R51VOI-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let ordinary = [10, 20, 30]
let first = ordinary[1]
let bounded = [3..5: 10, 20, 30]
let declaredFirst = bounded[3]
```

현행 예제 `EX-R51VOI-006`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let ports = #map{ "https": 443 }
let secure = ports["https"]
```

현행 예제 `EX-R51VOI-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let matrix = #2,2[1, 2; 3, 4]
let topLeft = matrix[1; 1]
let firstRow = matrix[1; *]
```

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

현행 예제 `EX-R51VOI-008`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let values = [10, 20, 30, 40]
let middle = values[2..$]
let sameCoordinate = middle[3]
```

`middle`은 source coordinate 2부터 4를 고르며 rebase하지 않으므로
coordinate 3을 그대로 사용한다.

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
