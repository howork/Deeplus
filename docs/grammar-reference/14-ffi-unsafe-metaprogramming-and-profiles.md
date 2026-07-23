<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# FFI, unsafe, 메타프로그래밍 및 프로필

## 상태

이 장은 외부 시스템이나 컴파일 시간 구조와 맞닿는 경계를 설명한다.
구문이 존재한다는 사실, 설계가 성숙했다는 사실, 제품에서 실행되었다는
사실은 서로 다른 주장이다.

| 표면 또는 계약 | 현행 상태 | 경계 |
|---|---|---|
| `unsafe { ... }` | `CURRENT` 구조 구문 | unsafe 권위를 가시화하지만 효과·오류·소유권·정리 의무를 지우지 않음 |
| `extern#C def#unsafe`와 `extern c("...")` | `PREVIEW_GATED` | 정확한 Preview 루트와 기능 gate가 있을 때만 설계상 허용 |
| `@scope#dynamic`, `@scope#unsafe` | `PREVIEW_NONACTIVATABLE` / `RECOVERY_ONLY` | 진단을 위한 형태만 인식하며 현행 의미 노드를 만들지 않음 |
| `typeof <static-sample>` | `CURRENT` | 타입 위치의 정적 표본 투영이며 runtime reflection이 아님 |
| `value!{...}`, `value!!{...}` | `CURRENT` | 같은 명목 타입의 얕은/깊은 derivation이며 소스 생성이나 reflection이 아님 |
| compiler CST/AST/HIR/MIR | 내부 구현 자료 | 소스에서 인용·변형하는 값이 아님 |
| provider/공식 도구가 만든 소스 | `OFFICIAL_TOOLING` 또는 별도 provider 프로필 | 생성된 소스도 일반 소스와 같은 scanner-to-MIR 검사를 다시 받음 |
| `@ast`, `^{...}`, 붙은 `?Identifier` | `REMOVED` | Stable, Preview, Recovery 어느 프로필에도 없음 |

언어 설계 상태와 별개로 Rust scanner/parser, checker, MIR, xVM, LLVM,
formatter/LSP를 포함한 제품 15개 lane은 모두 `NOT_RUN`이다. 이 장은
정확히 22개인 OPEN feature P1을 폐쇄하지 않으며 `M13-A002..005`도 별도
OPEN action으로 유지한다.

## 문법

### 현행 unsafe, 정적 타입 투영 및 derivation

`unsafe` block은 Stable 표현식 primary다. `typeof`는 타입 위치에만 있고
일반 표현식을 실행하지 않는다. derivation은 postfix owner가 `!` 또는
`!!`와 바로 이어지는 delta block을 소유한다.

```ebnf
UnsafeBlockExpr ::= "unsafe" Block ;

TypeofType ::= "typeof" TypeofStaticSampleOperand ;
TypeofStaticSampleOperand ::= Literal
                            | ListLiteral
                            | StaticPrefixedCollectionSample
                            | NumericArrayLiteral
                            | MeasureLiteralExpr ;
StaticPrefixedCollectionSample ::= MapLiteral | SetLiteral | MutListLiteral ;

PrototypeDerivationSuffix ::= ("!" | "!!") DerivationBody ;
DerivationBody ::= "{" MaterializationEntryList? "}" ;
```

`unsafe`는 일반 `EffectRow` 원자가 아니다. 이름 있는 일반 함수에
`def#unsafe`를 붙이는 경로도 없다. 해당 철자는 아래의 C FFI Preview
owner만 소유한다.

<!-- deeplus-status-fence: PREVIEW_GATED -->

### 명시적으로 gated인 FFI

Preview 파일은 Stable 파일과 다른 루트를 사용한다. 선택적 shebang 뒤,
모듈 선언과 모든 source item보다 앞에 gate가 와야 한다.

```ebnf
DeeplusPreview ::= PreviewLibrarySourceFile
                 | PreviewExecutableSourceFile
                 | PreviewScriptSourceFile ;
PreviewLibrarySourceFile ::= PreviewGate ModuleDecl? PreviewLibraryItem* ;
PreviewExecutableSourceFile ::= PreviewGate ModuleDecl? PreviewExecutableItem* ;
PreviewScriptSourceFile ::= Shebang? PreviewGate ModuleDecl? PreviewScriptItem* ;

PreviewGate ::= "#" "preview" "(" PreviewFeatureList ")" LineBreakBoundary ;
PreviewFeatureList ::= Identifier ("," Identifier)* ;

PreviewFfiDecl ::= PreviewFfiFunctionDecl | PreviewFfiBlockDecl ;
PreviewFfiFunctionDecl ::= "extern" "#" "C" "def" "#" "unsafe"
                           Identifier ParameterList ReturnClause?
                           ThrowsClause? EffectsClause? StatementBoundary ;
PreviewFfiBlockDecl ::= "extern" "c" "(" PLAIN_STRING_LITERAL ")"
                        "{" PreviewFfiBlockMember* "}" ;
PreviewFfiBlockMember ::= "unsafe" "def" Identifier ParameterList
                          ReturnClause? ThrowsClause? EffectsClause?
                          StatementBoundary ;
```

현행 feature gate map에서 소스로 활성화할 수 있는 FFI 기능은 두 개다.

| 기능 ID | 문법 경로 | 정확한 의존성 |
|---|---|---|
| `ffi_minimum_sound_profile` | `PreviewFfiFunctionDecl` | `ffi_minimum_sound_profile` |
| `ffi_c_extern_unsafe_surface_msp` | `PreviewFfiFunctionDecl`, `PreviewFfiBlockDecl` | `ffi_c_extern_unsafe_surface_msp`, `ffi_minimum_sound_profile` |

두 번째 표면의 완전한 gate 예시는 corpus `EX-R48-026`과 같은
bytes를 사용한다.

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

<!-- deeplus-status-fence: RECOVERY_ONLY -->

### 비활성 quarantine의 Recovery 형태

다음 production은 제안된 설계를 정밀하게 거부하기 위한
Recovery 전용이다. Stable 또는 activatable Preview route가 아니다.

```ebnf
RecoveryQuarantineScope ::= "@" "scope" "#" ("dynamic" | "unsafe")
                            Block QuarantineExport? ;
QuarantineExport ::= "->" "$" Identifier TypeAnnotation
                   | "->" "$" "(" QuarantineExportField
                     ("," QuarantineExportField)* ")" ;
QuarantineExportField ::= Identifier TypeAnnotation ;
```

<!-- deeplus-status-fence: CURRENT -->

## 허용과 정적 의미

### unsafe 권위는 효과 집합과 별도다

`UnsafeAxisSeparated`와 `UnsafeBoundaryAdmitted`가 다음 경계를 고정한다.

- `unsafe`는 `effects {...}` 안에 쓰는 효과 원자가 아니다.
- unsafe 연산은 이를 허용하는 명시적 boundary 안에서만 검사할 수 있다.
- boundary는 원래 연산의 `EffectRow`, `ErrorSet`, ownership, borrow region,
  cleanup 및 source role을 숨기거나 약화하지 않는다.
- 타입이나 `Plain` 성질만으로 pointer provenance, layout, ABI 또는 unsafe
  권위를 얻지 않는다.
- `unsafe` block의 범위가 끝났다고 pointer·borrow·resource의 수명이
  자동으로 안전해지지는 않는다.

따라서 다음 표기는 거부된다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public def read(ptr: RawPtr) -> Int
    throws Never
    effects {unsafe}
= {
    return 0
}
```

주 진단은 `EFFECTROW_UNSAFE_AXIS_FORBIDDEN`이며, 필요한 경우
`UNSAFE_AUTHORITY_NOT_EFFECT` 또는 `UNSAFE_REQUIRES_UNSAFE_BOUNDARY`가
경계를 설명한다.

<!-- deeplus-status-fence: PREVIEW_GATED -->

### Preview gate 허용 알고리즘

`PreviewFeatureGateAdmitted`는 다음 순서로 하나의 결과를 낸다.

1. 선택한 루트가 정확히 `Preview*SourceFile`인지 확인한다.
2. gate가 모듈 선언과 source item보다 앞에 있는지 확인한다.
3. ID를 왼쪽에서 오른쪽으로 읽어 unknown ID, nonactivatable ID, 첫
   duplicate ID를 판정한다.
4. 요청한 기능의 명시적 transitive Preview 의존성 집합과 gate의 ID
   집합이 정확히 같은지 확인한다. 의존성을 암시적으로 활성화하지 않는다.
5. 실제로 파싱한 production이 gate map의 허용 route에 속하는지
   확인한다.
6. 마지막으로 기능별 FFI 정적 predicate를 적용한다.

앞의 1–5는 **구문 route admission**이고 6은 별도의 **의미
admission**이다. gate가 있다고 해서 target ABI가 정해지거나 C type과
Deeplus type의 layout이 같아지지 않는다. target triple, ABI manifest와
emitting representability predicate가 결합되지 않은 선언은 source를
구조적으로 읽을 수 있어도 semantic profile이 unbound이며
`FFI_LAYOUT_RECEIPT_REQUIRED` 경계에서 executable FFI로 승인할 수 없다.
예를 들어 Deeplus `Int`는 signed 64-bit 값
domain이지만 C `int`의 width는 target ABI가 정한다. 이름이 비슷하다는
이유로 같은 foreign type으로 lowering하면 안 된다.

이에 대응하는 진단은 `PREVIEW_GATE_UNKNOWN_FEATURE`,
`PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE`, `PREVIEW_GATE_DUPLICATE_FEATURE`,
`PREVIEW_GATE_DEPENDENCY_MISSING`, `PREVIEW_GATE_PLACEMENT_INVALID`다.

### FFI 최소 soundness 경계

gate는 FFI가 Stable이거나 제품에서 안전하게 실행된다는 증명이 아니다.
각 외부 선언은 최소한 다음을 닫아야 한다.

- 정확한 target triple, calling convention, foreign ABI와 symbol identity
- 파라미터·결과의 representability, 크기, 정렬, signedness 및 layout
- raw pointer의 provenance, nullability, alias, lifetime 및 mutability
- 값과 resource의 소유권 이전, allocator/deallocator 및 cleanup owner
- callback의 저장 가능 기간, 호출 thread/isolation 및 reentrancy
- foreign unwind, Deeplus Error/Defect/Cancellation과의 변환 경계
- C aggregate, variadic 및 stored callback별 독립 프로필
- Deeplus MIR에서 xVM/LLVM으로 가는 backend-equivalence 증거

`Plain`은 layout-safe나 C-compatible을 뜻하지 않는다.
`FFI_SIGNATURE_UNREPRESENTABLE`과 `PLAIN_IS_NOT_LAYOUT_SAFE`는 이
혼동을 차단한다.

따라서 이 참조서의 gated `c_abs` 같은 예제는 gate·parser·정적 검토
형식을 보여 주는 자료이지 target-bound 실행 가능 선언이 아니다.
실행 수용을 주장하려면 target/ABI manifest, representability 결과,
symbol binding, provenance·ownership plan, unwind/cleanup law와 xVM/LLVM
동등성 확인서가 같은 artifact identity에 결합되어야 한다. 현재 모든
관련 product lane은 `NOT_RUN`이다.

<!-- deeplus-status-fence: CURRENT -->

### 메타프로그래밍과 compiler tree 경계

Deeplus의 현행 경계는 “정적 정보 사용”과 “프로그램이 compiler tree를
조작함”을 분리한다.

- `typeof`는 static sample의 타입을 투영할 뿐 표본을 runtime에서
  평가하거나 constructor/provider/FFI/reflection 권위를 실행하지 않는다.
- 타입 토큰은 타입 위치, 정적 selector 및 descriptor projection에만
  쓰이며 일반 runtime 값이나 권위 원천이 아니다.
- `!{...}`와 `!!{...}`는 같은 명목 타입의 construction row를 따르는
  derivation이다. 임의 AST 변환이나 새 선언 생성을 뜻하지 않는다.
- R2 proof certificate와 provider derive-via sidecar는 도구 증거다.
  witness, 타입, MIR 값 또는 실행 권위를 만들지 않는다.
- 도구가 소스를 생성하면 그 소스는 handwritten source와 동일하게
  scanner, parser, checker, MIR 단계를 다시 거친다.
- Rust 내부 lossless CST, AST, typed HIR 및 Deeplus MIR은 구현 자료이며
  source quotation 대상이 아니다.

### 서로 다른 프로필 축

| 축 | 값의 예 | 의미 |
|---|---|---|
| 문법 profile | `LEXICAL`, `STABLE`, `PREVIEW`, `RECOVERY` | scanner/parser reachability |
| 기능 maturity | `STABLE_DESIGN`, `PREVIEW`, `PREVIEW_DESIGN` | 언어 설계의 성숙도와 source activation |
| library/tooling | `STDLIB_PROFILE`, `OFFICIAL_TOOLING` | core syntax 밖의 API 또는 도구 계약 |
| 제품 evidence | `NOT_RUN` 또는 target-bound receipt | 실제 구현·실행 주장 |

한 축의 승격은 다른 축을 자동으로 승격하지 않는다. LLVM backend가
존재한다는 사실만으로 FFI가 sound해지지 않고, 공식 도구가 있다는
사실만으로 core syntax가 생기지 않는다.

## 평가·소유권·효과

- `unsafe` boundary 안에서도 표현식은 현행 왼쪽-오른쪽 평가 순서,
  Error/Defect/Cancellation 구분 및 cleanup 순서를 보존한다.
- foreign call argument는 정확히 한 번 평가되어야 하며, ABI lowering은
  소스 평가 순서를 재배열할 권위를 갖지 않는다.
- ownership transfer는 호출 commit 전·후를 구별해야 한다. 거부된
  admission이나 실패한 pre-call marshalling이 source owner를 몰래
  소비해서는 안 된다.
- callback, pointer 및 foreign handle은 명시된 lifetime과 drop authority
  없이 closure, task 또는 actor 경계를 넘을 수 없다.
- foreign unwind를 Deeplus recoverable Error로 임의 변환하거나,
  Cancellation을 foreign error code로 접어서는 안 된다.
- compiler/provider/tooling 결과는 MIR에 도달하기 전에 검증된 정적
  identity로 닫혀야 하며 runtime 이름 검색으로 되돌아가서는 안 된다.

현재 이 모든 항목은 정적 설계 계약이다. 실제 ABI, provenance, xVM/LLVM
동등성 및 target 실행은 `NOT_RUN`이다.

## 현행 예제

### `EX-R48-038` — `typeof` 정적 표본

```deeplus
use std::units::si

public type Meter = typeof 1[m]
public def move(distance: Meter) -> Unit
    throws Never
    effects {}
= {
}
```

`typeof 1[m]`는 active UnitCatalog를 사용해 타입을 투영하지만 `1[m]`을
runtime에서 실행하지 않는다. 반대로 `typeof(value)` 호출형과 runtime
지역 변수를 표본으로 쓰는 형식은 거부된다.

### `EX-R48-011` — 같은 타입 derivation

```deeplus
let user = User!(id: UserId!(1), name: "Kim")
let renamed = user!{
    name: "Lee"
}
```

이는 `User`의 construction/ownership 계약을 보존하는 얕은 derivation이지
reflection이나 AST rewrite가 아니다.

<!-- deeplus-status-fence: PREVIEW_GATED -->

### `EX-R48-026` — gate가 있는 FFI

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

예제 판정은 `accept_with_gate`이고 certification은
`design_static_product_not_run`이다. parser/checker/ABI 실행 증거가 아니다.

<!-- deeplus-status-fence: CURRENT -->

### 설명용 Stable unsafe block

다음은 이름 해석이 제공된다고 가정한 구조 예시다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.ebnf -->
```deeplus
def readByte(pointer: RawPtr<Byte>) -> Byte
= {
    unsafe {
        return pointer ~ load()
    }
}
```

`unsafe`는 `load`에 필요한 권위를 가시화할 뿐 `RawPtr`의 provenance,
반환 타입, 오류, cleanup 또는 lifetime 검사를 생략하지 않는다.

## 거부되거나 격리된 형식

| 형식 또는 주장 | 판정 |
|---|---|
| Stable root의 `extern#C def#unsafe` | gate 누락으로 거부 |
| `#preview(ffi_c_extern_unsafe_surface_msp)`만 사용 | `ffi_minimum_sound_profile` 의존성 누락 |
| 모듈 선언이나 source item 뒤의 `#preview(...)` | `PREVIEW_GATE_PLACEMENT_INVALID` |
| gate 안의 `PREVIEW_DESIGN` ID | `PREVIEW_GATE_FEATURE_NOT_ACTIVATABLE` |
| 일반 이름 있는 `def#unsafe` | 거부; FFI Preview owner만 해당 철자를 소유 |
| `effects {unsafe}` | 거부; unsafe는 효과 원자가 아님 |
| `Plain`을 C layout-safe로 간주 | 거부 |
| C aggregate, variadic, stored callback을 최소 FFI로 암시 | 비활성 별도 설계 |
| `typeof(runtimeExpr)` 또는 `typeof(...)` 호출형 | 거부 |
| type token을 runtime reflection 값으로 저장 | 거부 |
| `@scope#dynamic`, `@scope#unsafe` | Recovery 진단 후 비활성 거부 |
| source `@ast`, `^{...}`, 붙은 `?Identifier` | 완전히 제거됨 |
| 도구가 만든 sidecar를 witness나 실행 권위로 사용 | 거부 |
| 문서 예제만으로 FFI/unsafe product PASS 주장 | 거부 |

<!-- deeplus-status-fence: RECOVERY_ONLY -->

quarantine의 비활성 예시는 다음과 같다.

<!-- deeplus-example: illustrative; status: RECOVERY_ONLY; authority-source: spec/contracts/quarantine-scope.json -->
```deeplus
@scope#dynamic {
    legacyCall()
} -> $result: PlainResult
```

이 형태는 `QUARANTINE_SCOPE_NOT_ACTIVATABLE`의 대상이다. 제안된 최소
계약조차 typed immutable export만 허용하고 outer mutation, suspension,
pointer/authority/borrow/resource/closure/task/actor escape를 금지한다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- Error, effect, Cancellation 및 cleanup 순서는 [제어 흐름, 오류, 효과 및
  정리](11-control-flow-errors-effects-and-cleanup.md)를 따른다.
- pointer와 resource의 move/borrow/escape는 [소유권, 대여 및
  책임](12-ownership-borrowing-and-responsibility.md)을 따른다.
- type token, `typeof` 및 refinement 경계는 [타입, 제네릭 및
  리파인먼트](04-types-generics-and-refinement.md)를 따른다.
- derivation과 data layout identity는 [Enum, Record, 스키마, 비트필드 및
  단위](07-enums-records-schemas-bitfields-and-units.md)를 따른다.
- callable profile과 FFI signature channel은 [함수, 메서드, 클로저 및
  호출](05-functions-methods-closures-and-calls.md)을 따른다.
- Preview·Recovery·Removed의 전체 분류와 OPEN gate는 [Preview, 복구 및
  제거된 표면](15-preview-recovery-and-removed-surfaces.md)을 따른다.

## 정본 근거

- 언어 경계와 제품 상태:
  [`spec/language.md`](../../spec/language.md)
- 정확한 Stable/Preview/Recovery 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- source root, gate, unsafe 및 quarantine 허용:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 기능 maturity와 trace:
  [`spec/features/catalog`](../../spec/features/catalog)
- 정확한 gate map:
  [`spec/features/gates.json`](../../spec/features/gates.json)
- unsafe/FFI/checker predicate:
  [`spec/types/predicates`](../../spec/types/predicates)
- quarantine 설계 계약:
  [`spec/contracts/quarantine-scope.json`](../../spec/contracts/quarantine-scope.json)
- tooling/library 프로필:
  [`spec/contracts/tooling-and-profiles.json`](../../spec/contracts/tooling-and-profiles.json)
- 타입·MIR 경계:
  [`spec/types/type-system.md`](../../spec/types/type-system.md),
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- 검토 예제:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
