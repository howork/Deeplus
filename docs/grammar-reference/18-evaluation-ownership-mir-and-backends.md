<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# 평가, 소유권, MIR 및 backend 보존

<!-- deeplus-status-fence: CURRENT -->

## 1. 이 장의 관점

문법은 프로그램의 구조를 정하지만
실행 중 무엇이 몇 번, 어떤 순서로 관찰되는지까지
모두 말해 주지는 않는다.
Deeplus의 실행 의미 권위는
[`spec/mir/semantics.md`](../../spec/mir/semantics.md)의
Deeplus MIR에 있다.

Rust scanner/parser와 typed HIR은
소스 의미를 MIR로 넘기기 위한 frontend projection이다.
xVM bytecode, Cranelift ObjectModule AOT, Cranelift JITModule는
MIR을 실행하는 backend projection이다.
어느 projection도
평가 횟수, 실패 전후 commit, owner, cleanup,
effect/error/cancellation, actor ordering,
provider observation을 바꿀 수 없다.

이 장은 다음을 자세히 설명한다.

- source에서 CST, AST, HIR, MIR로 내려가는 책임
- machine state와 observable event
- 왼쪽에서 오른쪽, 정확히 한 번인 평가
- precommit failure와 atomic commit
- move, borrow, inout, resource cleanup
- collection, assignment, pattern의 transaction
- ternary, 보간, Map unfold와 transpose의 정적으로 폐쇄된 MIR 법칙
- actor와 shared-state의 관찰 identity
- semantic value와 layout/ABI/backend identity의 분리
- xVM/Cranelift differential conformance
- 설계 정적 계약과 제품 실행 receipt의 차이

이 장은 MIR opcode 목록이나 storage layout을 발명하지 않는다.
이번 정본 보완으로 필수 20개 MIR 감사 집합의
`DEFERRED_PRODUCT_HANDOFF`는 0개다. format-spec도 닫힌
source-observable 법칙을 갖지만, 이는 제품 구현이 끝났다는 뜻이 아니다.
xVM·Cranelift 실행, backend opcode, 표현, 성능 및 제품 지원은
계속 `NOT_RUN`이다.

## 2. source에서 실행까지

### 2.1 scanner와 lossless CST

scanner는 Unicode source와 lexical mode를 읽어
token과 trivia를 만든다.
lossless CST는 토큰, delimiter, 줄바꿈과 주석을 보존한다.

이 단계가 책임지는 대표적인 결정은 다음과 같다.

- raw String body와 ordinary String body 구분
- numeric literal token과 prefix sign 분리
- attached postfix `A^`와 spaced infix `a ^ b` 경계
- `#map`, `#set`, `#mut`, `#raw`, `#bytes` prefixed goal
- Stable과 Preview entry point 분리
- 문장 경계와 layout separator 보존

scanner는 타입을 보고 token을 다시 나누지 않는다.
예를 들어 `-128`은 부호를 포함한 단일 numeric token이 아니라
prefix `-`와 signless literal의 AST 후보다.

### 2.2 AST

parser는 declaration, statement, type, Pattern,
Pratt expression owner를 확정한다.
AST는 소스 구조를 나타내지만
아직 모든 static identity와 ownership plan을 갖지 않는다.

문법 또는 owner admission에 실패한 source를 허용된 Stable AST로
가장해서는 안 된다. 실패한 구조는 그 값이나 연산의 MIR identity를
만들지 않는다.

### 2.3 HIR

HIR은 다음 정적 identity를 닫는다.

- module과 declaration
- nominal type와 member
- label row
- extension set와 selected extension
- Trait conformance와 witness
- constructor/materialization target
- closed Union alternative와 Enum VariantId
- actor, mailbox profile, message selector
- context/evidence origin
- callable signature와 ownership/effect/error 책임

HIR은 runtime 문자열을
정적 label, member, witness, provider로 바꾸지 않는다.
이름 해석 결과는 MIR lowering 전에 고정된다.

### 2.3.1 HIR-H1의 단계 타입

`hir_h1_current_mir_bridge_design`은 위 원칙을 기계적으로 검사할 수 있게
만드는 bounded 설계다. fully typed/resolved/responsibility-closed
verifier boundary의 상태는 `STABLE_DESIGN`이고
`source_activation: none`이다. current 설계 파이프라인과 RFC draft
확장 경계는 다음과 같다.

`STABLE_DESIGN`은 구현 receipt가 아니다. 관련 제품 lane은
`15/15 NOT_RUN`이며, source activation과 구현·실행 authority는 없다.

이 문서화로 semantic P0가 새로 생기거나 닫히지 않으며 현재 값은 0이다.
기존 OPEN feature P1도 Class 6개, Enumeration 8개, Trait Conformance
7개, SFD 1개로 정확히 22개다. HIR schema나 fixture의 존재는 그중 어느
항목도 폐쇄하지 않는다.

```text
LosslessCST
  -> NormalizedAST
  -> HirSkeleton
  -> CheckSession
  -> TypedHirDraft
  -> Verified<CanonicalHirH1>
  -> ExecutableHirH1
  -> Verified<DeeplusMirR1>
```

각 이름은 동일한 struct의 phase flag가 아니다. 역할이 다른 값을 서로
다른 타입으로 나눠, 미해결 analysis 값이 canonical 또는 executable
권위로 잘못 직렬화되는 일을 막는다.

| 단계 | 할 수 있는 일 | 아직 권위가 아닌 것 |
|---|---|---|
| `LosslessCST` | token, trivia와 원 spelling 보존 | type·witness·ownership 선택 |
| `NormalizedAST` | surface sugar를 구조적으로 정규화 | overload나 backend representation 선택 |
| `HirSkeleton` | owner/body/scope/generated declaration의 뼈대 구성 | unresolved slot을 canonical로 저장 |
| `CheckSession` | name, type, call, label, evidence, ownership, effect, error, cancellation, isolation, cleanup을 fixed point로 폐쇄 | 실행 |
| `TypedHirDraft` | 모든 결정을 담되 verifier 전 상태로 유지 | canonical seal |
| `Verified<CanonicalHirH1>` | 닫힌 의미와 identity의 검증된 표현 | target 실행 가능성 |
| `ExecutableHirH1` | exact target capability receipt를 결합 | 의미 재선택이나 backend 전환 |
| `Verified<DeeplusMirR1>` | current backend-neutral MIR machine schema 결과 | product implementation·execution |
| `Verified<ProposedMirX1>` | 비정본 compatibility target | current MIR authority·activation |

`CanonicalHirH1`은 모든 expression, binder, capture, payload에 normalized
type이 있고, 이름과 선택이 resolved되며, responsibility가 닫혀 있어야
한다. 구체적으로 declaration/member/label, conformance/witness/requirement,
extension, substitution, construction target, ownership/place, effect,
ErrorSet, Defect, cancellation, suspension, isolation, authority, cleanup
identity를 보존한다.

`nonescaping_lexical_access` Stable design은 callable responsibility를
하나의 `Closed | LexicalScoped | Captured` 합으로 압축하지 않는다.
HIR의 residence는 `FrameIndependent | RegionBound(RegionId)`,
environment는 `Empty | Explicit(CapturePlan)`이라는 독립 축이다.
capture list의 absent/present-empty/present-nonempty 상태, present-empty의
closed assertion, lexical dependency place set도 별도로 보존한다. 따라서
explicit capture environment를 가지면서 residual lexical dependency로
region-bound인 callable도 표현할 수 있다.

반대로 다음 값의 canonical variant 수는 정확히 0이다.

- 문법 또는 admission에 실패한 node
- unresolved lookup 또는 candidate set
- inference variable와 placeholder/error type
- missing expression
- generic operator dispatch
- runtime string을 static identity로 바꾸는 node
- backend layout 또는 ABI identity

verifier는 “나중에 MIR에서 해결한다”는 TODO를 허용하지 않는다. 이 경계를
통과하지 못한 source는 진단을 위한 analysis provenance로 남을 수 있지만
MIR event나 executable value를 만들지 않는다.

R4 이름 해석은 noncall `ResolvedRef`, name/import trace와 visibility
proof를 만들 수 있다. callable 후보는 `ResolvedOverloadSetRef`로
`AnalysisHir`에만 있을 수 있고 exact winner와 complete generic
substitution 전에는 `CanonicalHirH1`으로 seal할 수 없다.
`ImportBindingId`, `ResolverScopeId`, `SourceOriginId`,
`ActivationOriginId`는 compile-time provenance이며 runtime 값이나 MIR
lookup key가 아니다.

### 2.3.2 canonical과 executable 사이의 capability receipt

`Verified<CanonicalHirH1>`이 의미적으로 완전하다는 사실만으로 특정 MIR
schema가 모든 reachable variant를 내릴 수 있다고 결론 내리지 않는다.
`ExecutableHirH1`을 만들려면 `MirCapabilityReceiptR1`이 다음을
결합해야 한다.

```text
hir_semantic_digest
mir_schema_digest
lowering_rules_digest
required_capabilities
provided_capabilities
unsupported_reachable_variant_count
```

required와 provided capability 집합은 정확히 같고,
`unsupported_reachable_variant_count`는 0이어야 한다. receipt는 누락된
variant를 opaque runtime callback이나 TODO pseudo-operation으로 덮지
못한다. 또한 receipt 자체는 실행, 구현, MIR-X1 채택, backend switch,
publication 또는 promotion 권위를 주지 않는다.

### 2.3.3 Rational·Complex constant residue

Rational source `<p/q>`는 canonical HIR에서 `RationalConst`가 된다. payload
`ConstRational`은 부호와 최단 unsigned big-endian numerator/denominator
magnitude를 보존하고, 분모 양수·기약분수·positive `0/1` invariant를
만족한다. CST의 `<6/8>` spelling과 canonical `3/4` 값은 서로 다른
provenance 층이다. backend가 고정 폭 integer나 `Float64`를 거쳐 값을
근사해서는 안 된다.

붙은 `i` literal의 `Complex<Float64>` profile은 canonical HIR의
`ComplexLiteral`과 `ConstComplex64` payload로 간다. 두 component는 real
먼저, imaginary 다음 순서의 정확한 IEEE binary64 bit identity를 갖고,
`+0.0`과 `-0.0` bit를 보존한다. `Complex<Float32>` source profile을
일반적으로 `Float64`로 넓혀도 된다는 뜻은 아니다. 이 payload는 principal
power의 branch side를 보존하기 위한 수치 의미이지, struct field offset,
SIMD layout 또는 foreign ABI를 정하는 계약도 아니다.

### 2.3.4 닫힌 power plan

`^`는 generic call이 아니라 `HirPowerPlan`이다. base를 먼저 한 번,
exponent를 다음에 한 번 평가한 뒤, checker가 이미 선택한 다음 여섯
operation 중 하나를 기록한다.

1. `CheckedIntPow`
2. `FloatPowInt`
3. `FloatPow`
4. `ComplexPowInt`
5. `ComplexPowPrincipal`
6. `MeasurePowStatic`

operand adaptation도 `Identity`, `DirectLiteralToF64Exact`, `F32ToF64`,
`F32ToComplex64`, `F64ToComplex64` 다섯 개로 닫힌다. plan에는 원래와
적응 후의 base/exponent type, result type, selected identity,
responsibility profile, `math_profile_id`, `special_value_profile_id`,
source origin이 함께 들어간다.

MIR lowerer는 이 plan을 보고 operation을 다시 고르지 않는다. expected
result, runtime 부호나 exponent 정수성, Trait/witness, provider,
source/import order, backend helper availability로 operation을 바꾸는
경로는 0개다. `POWER_EXPECTED_RESULT_SELECTION_FORBIDDEN`은 특히 result
annotation으로 이 결정을 바꾸려는 시도를 seal 전에 막는다.

### 2.3.5 DP-RFC-0002 구현 제안 경계

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

`DP-RFC-0002`의 구체 Rust HIR 구현, capability-aware lowering 코드,
`Verified<ProposedMirX1>` 생성 및 MIR-X1 activation은
`DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE`이다. 이 구현 제안은 앞의
`STABLE_DESIGN` verifier invariant를 구현 대상으로 소비하지만, 그
invariant와 같은 authority 상태를 갖지 않는다. 반대로 verifier boundary가
current라는 이유만으로 이 RFC의 schema, lowering, backend path가
구현되었거나 활성화되었다고 해석해서도 안 된다.

<!-- deeplus-status-fence: CURRENT -->

### 2.4 MIR

MIR은 source-observable 의미의 정본이다.
MIR state는 적어도 다음 개념을 보존한다.

- 현재 frame
- ordered operand state
- place와 ownership state
- cleanup-region stack
- effect/error continuation
- run/reply와 actor state
- provider binding과 replay identity
- source provenance

qualified lexical read는 ordinary ancestor-rooted place access와 검증된
region requirement로 내린다. 별도의 source-observable
`ancestor_place_read` event나 capture가 0개인 `callable_create` event를
합성하지 않는다. backend가 hidden static link를 사용할 수는 있지만
그 link는 capture environment, observable event 또는 public ABI가 아니다.

구현은 이 개념을 같은 Rust struct로 표현할 필요가 없다.
그러나 backend가 관찰 가능한 차이를 만들지 않도록
동등한 정보를 보존해야 한다.

### 2.5 xVM과 Cranelift

xVM bytecode interpreter는
첫 개발·검증·REPL execution path다.
Cranelift `ObjectModule` AOT는 첫 native object path이고
Cranelift `JITModule`은 in-memory native path다. 두 경로는 하나의
verified-MIR-to-CLIF lowering을 공유하며 finalization, linking과 code
lifetime에서만 갈라진다.

세 backend는 같은 source를 받았다는 사실만으로
동등하다고 주장할 수 없다.
ordered observable trace,
최종 value/failure,
place/cleanup balance,
provider replay identity를 비교한
target-bound differential receipt가 필요하다.

current backend authority는 정확히 `xVM initial execution`,
`Cranelift ObjectModule AOT`, `Cranelift JITModule`이다. xVM-only
architecture나 superseded native backend로 전환되지 않았다.
`ProposedMirX1`은
noncanonical/nonactivatable 설계 대상이므로 current Deeplus MIR을
대체하지 않는다.

CLIF value/block/stack slot/signature, register, relocation과 machine
address는 backend-private이며 HIR/MIR identity가 아니다. native
receipt는 MIR digest, target triple, ISA/settings, Cranelift family,
module kind, calling convention, runtime ABI, optimization과
object/linker 또는 JIT import map을 고정한다. Error, Defect,
Cancellation, suspension과 cleanup은 명시적 MIR edge로 유지되며 native
exception, host unwind 또는 임의 trap으로 대체할 수 없다.

internal runtime ABI R1은 source 문법이 아니라 MIR 이후의 implementation
contract다. fixed primitive scalar만 direct이고 aggregate/nominal은 typed
indirect slot이다. aggregate result는 normal sret slot을 사용하며 target
register 분할은 없다. dispatcher 결과는 `COMPLETE(OutcomeTag) |
PARKED(ContinuationReceiptId)`다. 완료된 호출에서만 `NORMAL(0)`,
`ERROR(1)`, `DEFECT(2)`, `CANCELLATION(3)` 가운데 하나가 선택되고 선택되지
않은 slot은 초기화되지 않는다. `PARKED`는 outcome을 commit하지 않고 owner,
loan, cleanup token과 root를 continuation receipt로 한 번 옮기는 별도
transition이다.

호출 전에는 argument 평가·acquire·ABI와 helper signature 검증·slot 준비·
root publication을 마친 뒤 `ownership_commit`을 정확히 한 번 수행한다.
entry 전 실패만 caller owner를 보존하며 entry 뒤 outcome은 transferred
input을 rollback하지 않는다. xVM helper table, AOT symbol sidecar와 JIT
import map은 모두 같은 logical helper ID/signature set을 결속한다. exact ABI
digest가 다르거나 host unwind가 경계를 넘으면 실행 전에 거부한다.

현재 이 계약은 Stable design이지만 product support는 `NOT_RUN`이다.
managed-reference와 suspension dependency digest는 exact contract에 결속된다.
suspending helper 여섯 개는 22개 base allowlist에 포함되고 managed-memory
helper 세 개가 조건부로 admit되어 active helper는 25개다. digest가 없거나
stale이면 fail-closed한다. function-static/lazy/mutex의 host blocking은
`COMPLETE`-only이고 semantic suspension이 아니다. external FFI는 별도 Preview
경계이며 이 계약이 활성화하지 않는다.

## 3. 무엇이 관찰 가능한가

### 3.1 관찰 event

MIR 의미에서 관찰 가능한 대표 event는 다음과 같다.

- 정상 result
- recoverable Error
- Defect
- Cancellation lifecycle
- I/O와 authority 사용
- message enqueue와 dequeue
- suspension과 resume
- cleanup registration과 execution
- provider observation
- shared-state synchronization
- owner transfer commit

event는 의미상 순서를 가진다.
backend가 같은 최종 숫자를 냈더라도
I/O 순서, cleanup 순서, message sequence가 다르면
동등하지 않다.

### 3.2 비관찰 구현 선택

정본이 별도로 노출하지 않는 다음 선택은
backend-private일 수 있다.

- instruction selection
- register allocation
- stack slot 배치
- 내부 temporary address
- 특정 최적화 pass 이름
- internal allocation strategy

단, private 선택이
공개 allocation/effect contract,
pointer provenance,
observable provider call,
failure/cleanup 순서를 바꾸면 더 이상 private가 아니다.

### 3.3 statically rejected source

checker가 거부한 source는 MIR event를 만들지 않는다.
정적 overflow, invalid Pattern, missing witness,
nonexhaustive match, invalid Preview gate는
runtime failure로 내리지 않는다.

진단 emission 자체는 tooling observation일 수 있지만,
프로그램 execution event와 섞이지 않는다.

## 4. 평가 순서

### 4.1 기본 규칙

정본이 별도 법칙을 정하지 않는 한
operand, argument, guard,
interpolation segment, collection entry,
cleanup registration은
왼쪽에서 오른쪽으로 정확히 한 번 평가된다.

“정확히 한 번”은 다음을 금지한다.

- overload마다 argument를 다시 평가
- compound assignment place를 두 번 평가
- optimizer가 effectful expression을 복제
- failed pattern probe 뒤 payload를 다시 평가
- named argument를 formal 순서로 재평가

#### `defer` registration의 정확한 순서

`defer`는 일반 호출의 선택과 argument binding을 재사용하지만 실행
시점을 둘로 나눈다. exact call target, substitution, formal binding과
result responsibility는 정적으로 닫힌다. 등록 시점 runtime 순서는
runtime callee/receiver(있는 경우) → `context`를 포함한 explicit runtime
argument의 source order → omitted-formal default expression의 formal
declaration order다. statically bound direct/type-side callee identity와
`using` evidence는 static이므로 runtime evaluation이 0회다.

준비된 value/place에는 기존 call transfer mode가 붙고
`SNAPSHOT_VALUE`, `SHARED_LOAN`, `EXCLUSIVE_LOAN`, `MOVE_INTO_PLAN`,
`OWNED_TEMPORARY`, `PINNED_PLACE_RESERVATION`, zero-evaluation
`STATIC_EVIDENCE` 중 하나로 acquisition된다. reusable value의 copy,
exact view/borrow reservation, affine owner의 consume을 서로 바꾸지 않는다.
consume은 준비 도중이 아니라 하나의 registration seal에서 plan owner로
commit된다. seal 전에 실패하면 temporary와 reversible
reservation을 준비 역순으로 정리하고 `CLEANUP_REGISTER` 관찰은 0개다.
이미 실행된 I/O나 authority effect를 되감거나 실패한 준비를 retry하지는
않는다. seal 뒤 cleanup 실행에서는 receiver, index, argument, default를
다시 평가하거나 target을 다시 찾지 않는다.

### 4.2 strict와 sequential Bool

`and`와 `or`는 strict Bool operator다.
왼쪽 operand 다음 오른쪽 operand를 모두 평가한다.

`and then`은 왼쪽이 true일 때만 오른쪽을 평가한다.
`otherwise`는 왼쪽이 false일 때만 오른쪽을 평가한다.

`?:`는 Option coalescing owner이며
Bool operator와 별도다.
왼쪽이 `some(v)`면 fallback을 평가하지 않고
`none`일 때만 fallback을 평가한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private let strictResult = leftCheck() and rightCheck()
private let guardedResult = leftCheck() and then rightCheck()
```

첫 줄은 두 호출을 순서대로 관찰한다.
둘째 줄은 `leftCheck()`가 false면
`rightCheck()` event가 없다.

### 4.3 callable argument

static label binding과 runtime evaluation은 분리된다.
named argument는 formal label에 정적으로 결합되지만
runtime expression은 source order를 따른다.

context, witness, repeated positional,
named-rest channel도 source order identity를 보존한다.
witness identity는 runtime lookup을 하지 않지만
그 channel이 signature와 MIR call descriptor에서 사라지지 않는다.

ordinary call과 message call은 ordered trailing-closure channel을 공유한다.
explicit closure capture environment는 ordinary argument 뒤 source
order로 획득되고, 각 label과 선택된 function-typed formal identity가
HIR/MIR에 남는다. qualified lexical dependency는 이 시점에 environment
획득을 만들지 않고 call site에서 ancestor place의 live read requirement를
사용한다. surface brace attachment만 지울 수 있고 evaluation order나
selected dispatch identity는 지우지 않는다.

ordinary/message/actor-message는 하나의 ordered argument vector를
lowering한다. message 전용 payload aggregate와 Tuple/Record projection
map은 없다. `receiver ~ moveTo x, y`는 두 argument를 왼쪽부터 평가하고,
`receiver ~ moveTo (x, y)`는 `x`, `y`로 Tuple 값 하나를 만든 뒤 그 값
하나를 formal 하나에 결합한다.

### 4.4 collection entry

List, Set, Map literal의 entry expression은
소스 순서대로 평가된다.
Map은 각 key 다음 value라는 source 구조를 보존한다.
한 entry 실패를 다른 collection kind로 재해석하지 않는다.

Set은 uniqueness와 keyability admission을 거친다.
iteration order가 source semantic contract가 아니므로
literal 평가 순서와 이후 iteration order를 혼동하면 안 된다.

## 5. place와 owner

### 5.1 place state

place는 값의 단순 주소가 아니다.
checker와 MIR handoff는 다음 상태를 추적한다.

- initialized 또는 absent
- usable 또는 moved
- shared borrow의 live region
- exclusive inout region
- mutable access 가능성
- cleanup owner
- isolation owner

하나의 source binding이 같은 normalized type을 유지해도
move 뒤 place state는 달라진다.
flow join은 type만 맞는다고 성공하지 않고
incoming place state가 호환되어야 한다.

### 5.2 move

move는 owner를 정확히 한 번 이전한다.
성공한 commit 뒤 source place는
reusable value가 아닌 한 사용할 수 없다.
resource cleanup responsibility도 새 owner로 이동한다.

precommit failure는 source owner를 보존한다.
MIR은 transfer 의도가 있었다는 이유만으로
실패 전에 source를 moved로 바꾸지 않는다.

### 5.3 borrow

borrow는 nonowning view다.
source owner보다 오래 살 수 없고
owner move/drop과 충돌한다.

live shared borrow가 있는 동안
충돌하는 mutation 또는 exclusive access는 거부된다.
borrow가 run/reply, actor, return, storage,
escaping closure를 건너려면
별도 admitted lifetime proof가 필요하다.

### 5.4 inout

inout은 한 dynamic call extent의 exclusive place access다.
다른 borrow/inout과 겹치지 않는다.

inout place에 새 값을 대입하는 replacement는
RHS를 먼저 평가하고,
old value cleanup/return과 새 value install을
정본의 replacement plan에 따라 commit한다.
현재 value를 inout place 밖으로 move해
place를 비우는 동작은 current minimum이 아니다.

### 5.5 `mut` parameter와 `mut T`

ordinary `mut name: T` parameter는 callee가 소유하는
mutable local place 하나를 만든다. argument는 한 번 평가되고,
place commit 전에 한 번 획득된다. affine owner이면 그 local place로
move되며 caller 쪽에는 write-back alias가 생기지 않는다.
callee가 최종 cleanup을 정확히 한 번 소유한다.

이는 caller place를 한 dynamic call 동안 독점적으로 빌리고
같은 place에 write-back하는 `inout`과 다르다.
또한 `mut T`는 unique mutable owner/view 책임을 나타내는 type
qualifier이지 parameter channel의 다른 철자가 아니다.
parameter commit 전 실패는 caller owner를 보존하고
부분 callee local을 만들지 않는다.

MIR 법칙이 닫혔다는 사실은 제품 구현 증거가 아니다.
backend는 `mut`를 `inout` alias, hidden clone 또는
두 번째 argument 평가로 바꿀 수 없으며,
제품 지원은 계속 `NOT_RUN`이다.

## 6. initializer와 local commit

### 6.1 ordinary binding

local initializer는 target binding이 아직 scope에 없는
pre-binding environment에서 정확히 한 번 평가된다.

성공하면 immutable 또는 mutable place 하나를 commit한다.
실패하면 binding을 하나도 commit하지 않고
initializer failure edge로 이동한다.
이미 만든 temporary는 cleanup plan을 따른다.

### 6.2 rightward binding

`expr -> $name`과 `expr -> $$name`은
frontend에서 ordinary `let`/`var` binding으로 정규화된다.
별도의 HIR/MIR opcode가 없다.

initializer evaluation, type inference,
ownership, effect/error, failure, cleanup,
shadowing, scope는 ordinary binding과 같다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private def decodeText(bytes: Bytes) -> String = {
    decode(bytes) -> $text
    return text
}
```

`text`는 `decode(bytes)`가 성공한 뒤에만 commit된다.
rightward 화살표가 hidden pipeline runtime을 만들지 않는다.

### 6.3 coroutine response binding

`yield value -> $response`는 예외다.
먼저 coroutine suspension event를 내고,
resume 뒤 받은 response를 ordinary binding 규칙으로 commit한다.

이 형식이 있다고 해서
일반 rightward binding이 suspension을 허용하는 것은 아니다.

## 7. assignment transaction

### 7.1 simple assignment

assignment는 target place를 한 번 평가하고
RHS를 한 번 평가한다.
성공하면 write 하나를 commit하고
결과 type은 `Unit`이다.

target가 member/index chain이어도
base와 selector를 재평가하지 않는다.

### 7.2 compound assignment

compound assignment의 순서는 다음과 같다.

1. target place 평가
2. original value 한 번 읽기
3. RHS 평가
4. exact intrinsic operation 수행
5. failure가 없으면 write 한 번 commit
6. `Unit` 산출

overflow, division by zero, IndexError 같은
precommit failure는 original owner와 value를 보존한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/value-operator-indexing-coherence.json -->
```deeplus
private def increment(inout value: Int) -> Unit = {
    value += nextDelta()
}
```

`value` place는 한 번 평가된다.
`nextDelta()` 뒤 intrinsic addition이 성공해야
write가 한 번 commit된다.

### 7.3 hidden compound opcode 금지

backend가 편의를 위해 compound opcode를 만들 수는 있지만
그 opcode가 다음을 숨길 수 없다.

- 두 번째 place evaluation
- failure 뒤 partial write
- implicit wrapping
- old owner의 이중 cleanup
- effect order 변경

MIR observable trace가 같아야 한다.

### 7.4 지역 병렬 대입

bare comma와 Tuple target은 하나의 `PatternAssignmentPlan`으로
정규화된다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
left, right = right, left
```

Stable plan은 서로 겹치지 않는 direct mutable Plain local만 받는다.

1. target place를 왼쪽부터 각각 한 번 resolve한다.
2. overlap, mutability, liveness와 exclusivity를 검사한다.
3. RHS Tuple을 한 번 평가한다.
4. 구조와 각 target type/ownership을 검사한다.
5. 새 value와 교체될 old owner를 private staging에 준비한다.
6. 하나의 `PatternAssignmentCommitId`로 논리적 commit한다.
7. old owner를 deterministic reverse order로 정리한다.

commit 전 어느 단계에서 실패해도 target write는 0이고 old value와 owner는
그대로다. commit 중 user callback, suspension 또는 recoverable
conversion은 허용하지 않는다.

## 8. integer와 floating value

### 8.1 semantic domain

`Int`는 signed 64-bit mathematical domain이다.
이 말은 반드시 C `long long` layout이나
특정 Cranelift integer ABI를 공개한다는 뜻이 아니다.

`Int8`부터 `Int128`,
`UInt8`부터 `UInt128`,
`ISize`, `USize`는 별도 domain이다.
operator는 hidden widening, narrowing,
mixed signedness를 삽입하지 않는다.

### 8.2 checked integer operation

dynamic overflow와 division/remainder by zero는
deterministic `ArithmeticDefect`다.
recoverable ErrorSet member가 아니다.

integer division은 zero 방향으로 truncate한다.
remainder는 다음 법칙을 만족한다.

`a == trunc(a / b) * b + r`

그리고 `r == 0`이거나 dividend와 같은 sign이며
`|r| < |b|`다.
signed `MIN / -1`과 `MIN % -1`은 overflow다.

Defect edge는 enclosing assignment commit보다 앞선다.
정적으로 증명된 실패는 checker rejection이며
MIR event가 없다.

### 8.3 floating

`Float32`와 `Float64`는
IEEE-754 binary32/binary64 value behavior를 보존하고
round-to-nearest, ties-to-even을 사용한다.

NaN은 unordered이며
implicit `Ord` 또는 `Keyable` evidence를 만들지 않는다.
positive zero와 negative zero는 source comparison에서 같다.
payload bit identity나 backend NaN representation은
source value identity가 아니다.

### 8.4 Rational과 Complex value

`Rational`은 `BigInt` numerator와 strictly positive `BigInt`
denominator로 이루어진 exact value다. 두 값은 항상 기약분수이고 zero는
`0/1` 하나로 정규화된다. 리터럴 정규화는 compile-time exact arithmetic
이므로 overflow wrap, saturation, float approximation이 없다. resource
budget을 초과하면 값을 축약해 받는 것이 아니라 정적 진단으로 끝난다.

ordinary constructor `Rational!(numerator, denominator)`와
`numerator ~ over denominator` message는 두 operand를 왼쪽에서 오른쪽으로
정확히 한 번 평가한 뒤 0 denominator를 검사하고, 성공할 때만 canonical
value를 publish한다. 실패 전에 임시 numerator owner를 소비하거나
부분적으로 만들어진 Rational을 관찰 가능하게 해서는 안 된다.

`Complex<Rep>`은 `real`, `imag` 두 IEEE component의 immutable semantic
value다. admitted initial Rep은 `Float32`, `Float64`이고 두 component는
같은 exact Rep을 가진다. signed zero, infinity, NaN classification은
component별로 보존된다. 단, source value 법칙이 storage layout이나
foreign complex ABI를 자동으로 정하지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let ratio: Rational = <6/8>  // exact canonical 3/4
let z: Complex = 3.0 + 4.0i
let belowCut: Complex = Complex!(real: -1.0, imag: -0.0)
```

마지막 값의 imaginary `-0.0`은 equality에서 `+0.0`과 같더라도 principal
Complex function의 branch side를 보존할 때 지워서는 안 된다.

### 8.5 power의 평가와 실패 경계

`base ^ exponent`의 관찰 순서는 다음으로 고정된다.

1. checker가 두 operand의 normalized static type으로 operation과 result를
   닫는다.
2. base expression을 정확히 한 번 평가한다.
3. exponent expression을 정확히 한 번 평가한다.
4. 두 operand adaptation을 plan에 기록된 순서로 적용한다.
5. 선택된 operation을 정확히 한 번 실행한다.
6. 성공하면 enclosing expression에 result를 전달하고, Defect면 enclosing
   place commit 전에 끝난다.

integer `CheckedIntPow`는 same-domain checked result를 만들고 dynamic
overflow는 `ArithmeticDefect`다. `FloatPow`의 real profile은 runtime
negative base를 보고 Complex로 route를 바꾸지 않는다.
`ComplexPowPrincipal`은 signed-zero-aware principal log/power profile을
사용한다. 두 profile 모두 `math_profile_id`와
`special_value_profile_id`가 semantic identity에 결합되어야 하며, host
libm 선택이 이 identity를 대신할 수 없다.

ordinary computational power는 각 결과 domain에서 `0 ^ 0`을 one으로
정의한다. 두 operand가 정적으로 0이면
`ZERO_TO_ZERO_POWER_USES_COMPUTATIONAL_CONVENTION` warning을 낼 수 있지만
MIR에서 별도 failure edge를 만들지 않는다. indeterminate 처리가 필요한
수치 알고리즘은 named checked API를 선택해야 한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/rational-complex-numeric-coherence.json -->
```deeplus
let inverseCube: Float64 = 2.0 ^ -3
let principal: Complex = Complex!(real: -1.0, imag: +0.0) ^ 0.5
let one: Int = 0 ^ 0
```

이 예는 source-observable 설계 trace다. 실제 HIR/MIR/xVM/Cranelift 실행
receipt는 없으며 제품 상태는 `NOT_RUN`이다.

## 9. pattern transaction

### 9.1 event 단계

성공 가능한 Pattern owner는
개념적으로 다음 순서를 갖는다.

1. `subject_evaluate`
2. `subject_acquire`
3. `test_plan_build`
4. `structural_test`
5. `probe_bind`
6. 선택적 `guard_evaluate`
7. `acquisition_stage`
8. `atomic_commit`
9. `final_bind`
10. `body`
11. `exit_or_join`

TestPlan과 probe binder는 nonconsuming이다.
guard는 probe를 읽을 수 있지만
move, escape, suspension, authority acquisition을 할 수 없다.

### 9.2 실패

structural mismatch는 structural test 뒤 종료한다.
false guard는 guard evaluation 뒤 종료한다.
둘 다 다음 count가 0이다.

- committed binding
- pattern move
- exclusive borrow
- authority acquisition
- escape
- suspension
- final binder

### 9.3 성공

성공은 precomputed ownership plan을
atomic commit에서 한 번 적용한다.
alias pattern은 clone이 아니라 borrow event다.
Or-pattern branch는 canonical binder interface와
같은 ownership state를 제공해야 한다.

Tuple, List rest, exact/open Record·Map, transparent nominal product,
named Enum payload, pin과 bounded range/relational test도 이 공통 event
family를 사용한다. 구조 종류가 늘어도 별도의 비원자적 binder path를
만들지 않는다. `let!`의 mismatch는 `PatternMatchDefect`로 나가지만
commit 전 zero-count 법칙은 동일하다. refutable catch의 mismatch는 다음
catch로 진행한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private def consumePositive(candidate: Option<Box<Item>>) -> Unit = {
    if let Option::some(move item) = candidate {
        if item.value > 0 {
            consume(move item)
        }
    }
}
```

구조 test와 guard가 모두 성공하기 전에는
`item` move가 commit되지 않는다.
false guard가 원본 owner를 부분 소비하지 않는다.

## 10. flow join

### 10.1 type join

모든 reachable value path는
같은 normalized type을 내거나
독립적으로 고정된 expected type 하나에 호환되어야 한다.

checker는 서로 다른 arm 결과를 보고
anonymous Union을 만들지 않는다.
unreachable path는 join에 기여하지 않는다.

### 10.2 responsibility join

join은 type 외에 다음을 비교한다.

- usable place state
- ownership state
- normalized effect union
- normalized recoverable error union
- cleanup balance
- isolation과 suspension responsibility

branch 하나가 owner를 move하고
다른 branch가 owner를 그대로 남기면
join 뒤 place 사용 가능성을 임의 선택할 수 없다.

### 10.3 compile-time proof

flow proof environment `Phi`는 compile-time evidence다.
runtime MIR value가 아니다.
MIR은 selected structural test와 branch edge를 받지만
`Phi` object를 allocate하지 않는다.

assignment, alias mutation, exclusive borrow,
escape/capture, consume, may-mutate call은
관련 durable fact를 kill한다.

## 11. ternary의 정확한 MIR 법칙

### 11.1 grammar와 static condition

ternary conditional expression은 Stable design surface에 존재하며
condition은 exact `Bool`이어야 한다.
truthiness, numeric truth, collection truth,
optional truth는 없다.

flow join의 일반 정적 법칙도 적용된다.
두 결과 arm은 같은 normalized type이거나
독립적으로 fixed expected type에 호환되어야 하고,
anonymous Union을 만들지 않는다.

### 11.2 MIR disposition

`ternary_conditional_expression`과
`ternary_short_expression_stable_profile`은 이제
모두 `LAW_PRESENT`다. lowering은 다음 순서를 고정한다.

1. condition을 정확히 한 번 평가한다.
2. exact `Bool` 결과로 두 successor 중 하나만 선택한다.
3. 선택된 arm만 정확히 한 번 평가한다.
4. 두 정상 edge의 normalized result type과 place state를 확인한다.
5. ownership, effect, Error, Cancellation, suspension 및 cleanup 책임을
   하나의 명시적 join에 보존한다.

checker는 join을 성립시키려고 anonymous Union을 합성하지 않는다.
optimizer도 effectful arm을 branchless select로 eager 평가하거나,
condition·place observation을 복제하거나,
한 edge의 cleanup/error 책임을 버릴 수 없다.
다만 이 법칙은 backend representation이나 실제 opcode를 선택하지 않는다.

### 11.3 설명용 syntax

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.dpg -->
```deeplus
private let label = ready ? "ready" : "waiting"
```

이 예제는 Stable syntax와 strict Bool static boundary를 보여 준다.
lazy-arm과 responsibility join은 정적으로 닫혔지만,
이 source가 xVM/Cranelift에서 실행되었다는 target-bound receipt는 아직 없다.

### 11.4 구현 금지 추론

backend 또는 optimizer는 다음 중 하나를 임의 선택할 수 없다.

- 두 arm 모두 eager 평가
- C 언어의 ternary semantics 그대로 채택
- branchless select로 effectful arm 실행
- 서로 다른 owner를 hidden clone으로 맞춤
- arm failure를 Option 또는 Result로 변환

design status는 유지되지만
product lane은 `NOT_RUN`이다.

## 12. List, Set 및 Map

### 12.1 List

ordinary List는 immutable owned collection이다.
literal element는 source order로 평가된다.
heterogeneous element를 보고
anonymous Union element type을 만들지 않는다.

명시적 expected `List<A | B>`가 있으면
각 element가 선언된 closed Union alternative로
유일하게 injection될 수 있어야 한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private type Scalar = Int | String
private let values: List<Scalar> = [1, "one"]
```

Union은 expected type에서 명시되었다.
MIR은 element type과 각 injection identity를 받는다.

### 12.2 Set static admission

`Set<T>`는 immutable unique-element collection이다.
literal과 comprehension element는
정확히 하나의 normalized `T`와
equality/keyability evidence를 요구한다.

duplicate literal entry는 static rejection이다.
membership probe는 widen하거나 stringify하지 않는다.
iteration order는 source semantic contract가 아니며
Set에는 bracket-indexing judgment가 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private let ports = #set{ 80, 443 }
```

두 element는 exact `Int` domain이고
literal uniqueness를 검사할 수 있다.

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private let invalidPorts = #set{ 80, 80 }
// duplicate literal entry는 Set construction 전에 거부된다.
```

거부된 literal은 runtime insert/overwrite event를 만들지 않는다.

### 12.3 Set runtime representation 비결정

Set semantics는 hash table, tree,
sorted vector, insertion-order table 중
어느 representation도 선택하지 않는다.

Keyable evidence가 필요하다는 사실은
public hash algorithm이나 seed를 고정하지 않는다.
iteration order가 semantic contract가 아니므로
backend 간 내부 순서 차이가 그 자체로 위반은 아니다.
단, 프로그램이 정본상 관찰할 수 없는 순서를
도구가 API guarantee로 노출하면 안 된다.

### 12.4 Map literal의 닫힌 부분

Map key는 exact `K` runtime value다.
Record label과 다르다.
entry의 key와 value는 source order로 평가된다.
lookup은 exact key type을 요구하며
missing key는 `IndexError::keyNotFound`다.

Map과 Record 사이에는
implicit conversion, dot-key sharing,
identity collapse가 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private let ports = #map{
    "http": 80,
    "https": 443,
}
private let secure = ports["https"]
```

`"https"`는 runtime String key다.
static member label이 아니다.

### 12.5 Map literal plan과 unfold

exact grammar는 `#map{ **expr }` entry를 허용한다.
진단은 제거된 `...expr`가 current map unfold가 아니며
call-side Record unfold와 별도임을 닫는다.

정본은 direct entry와 `**base`를
하나의 `MapLiteralPlan`에 넣는다.
각 key/value 및 unfold source는 source order대로 정확히 한 번
평가된다. unfold source는 같은 normalized key/value domain의
immutable Map이어야 하며, call-side static-label `**record`와
identity를 공유하지 않는다.

plan 안에서 같은 key가 다시 나타나면 뒤 occurrence가 이긴다.
교체된 old value의 owner는 정확히 한 번 cleanup된다.
모든 entry와 equality/keyability operation이 성공하기 전에는
Map을 publish하지 않는다. Error, Defect 또는 Cancellation으로
실패하면 이미 획득한 temporary를 역순 cleanup하고
부분 Map을 0개 publish한다. hidden clone, key String화,
numeric widening이나 implicit conversion은 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.dpg -->
```deeplus
private let merged = #map{
    **defaults,
    "port": "443",
}
```

이 예제에서 `defaults`에 이미 `"port"`가 있으면
뒤의 explicit entry가 그 값을 교체한다.
기존 value cleanup은 한 번이며,
완전한 plan이 성공한 뒤에만 `merged`가 publish된다.

### 12.6 collection failure와 cleanup

List, Set, Map의 닫힌 construction law는
entry expression을 한 번 평가하고,
commit 전 실패 시 temporary를 역순 cleanup한다.
Map은 §12.5의 later-key replacement와
failure-atomic publication을 추가로 따른다.
이 정적 closure만으로 allocator, hash representation,
성능 또는 backend 제품 지원을 주장해서는 안 된다.

## 13. index와 slice

### 13.1 owner와 index

built-in indexing은 owner와 각 index를
왼쪽에서 오른쪽으로 한 번 평가한다.
그 뒤 logical domain을 검사하고
storage projection을 수행한다.

List, String, Bytes의 기본 domain은 `1..length`다.
bounded List는 선언한 `L..U`를 보존한다.
Map은 exact `K`,
NumericArray는 typed axis coordinate를 사용한다.

### 13.2 readonly view

slice는 owner를 변경하지 않고
source coordinate와 provenance를 보존하는
`ReadonlyView`를 만든다.

hidden rebase, hidden copy,
mutable slice assignment,
owner lifetime escape,
isolation crossing은 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private let values = [10, 20, 30, 40]
private let tail = values[2..]
private let originalCoordinate = tail[3]
```

`tail`은 source coordinate 2부터 4를 보존한다.
독립된 1-based collection으로 rebase하지 않는다.

Pattern으로 borrowed List remainder를 capture하면 별도 closed carrier인
`ListRestView<T>`를 만든다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
private def inspect(values: List<Int>) -> Unit = {
    if let [first, middle.., last] = values {
        consume(middle)
    }
}
```

`middle`은 원본 owner region, coordinate projection과 길이 0도 가능한
`RankSpan`을 보존한다. intrinsic `Sequence<T>` witness는 이 carrier의
정해진 traversal에만 적용되며 generic `Sequence`가 Pattern이나 bracket을
새로 활성화하지 않는다.

### 13.3 precommit failure

out-of-domain index는
projection 또는 enclosing assignment commit 전에 실패한다.
missing Map key와 NumericArray invalid coordinate도
old owner/value를 보존한다.

conformance to `Sequence`, `Indexable`,
`LogicalIndexDomain`은
새 bracket lowering route를 만들지 않는다.

### 13.4 `MutableList` structural-edit commit

statement-only structural edit는 ordinary index assignment가 아니다.
frontend는 exact marker를 닫힌 Prelude operation 하나로 결정한 뒤 기존
`CallExpr`/`ResolvedCallPlan`과 `CallableImplementationId`를 사용한다.
operation set은 `insertBefore`, `insertAfter`, `prepend`, `append`,
`insertAllBefore`, `insertAllAfter`, `prependAll`, `appendAll`, `removeAt`,
`removeRange`, `removeSelected`, `popFirst`, `popLast`의 정확한 13개다.
expected result는 operation을 선택하지 않으며 edit 전용 HIR node나 MIR
opcode는 없다.

관찰 가능한 순서는 다음과 같다.

1. 하나의 exact exclusive `MutableList<T>` receiver place를 결정한다.
2. selector와 payload를 source order로 각각 한 번 평가한다.
3. coordinate, duplicate selector, live borrow/view/iterator,
   self-alias/`inout` overlap과 bulk-source finiteness/element evidence를
   검증한다.
4. payload와 필요한 capacity/result storage를 staging한다.
5. 성공하면 구조 변경을 정확히 한 번 publish한다.
6. removal capture가 있으면 point 결과 `T` 또는 multi 결과 `List<T>`를
   ordinary dollar local에 commit한다.

1–4의 Error, Defect 또는 Cancellation에는 mutation commit이 0개다.
receiver와 source owner가 그대로 남고, 획득한 temporary만 정상 cleanup
순서로 정리한다. hidden clone/snapshot/move나 rollback용 두 번째 mutation은
없다. multi-removal은 모든 selector를 mutation 전 coordinate로 해석하고
selector 순서의 결과와 survivor 순서를 각각 보존한다.

## 14. resource와 cleanup

### 14.1 cleanup region

resource owner는 정확히 하나의 cleanup path를 가진다.
cleanup registration은 source order로 관찰되고
실행은 deterministic LIFO region order다.

cleanup을 일으키는 일곱 exit는 normal fallthrough, `return`, `break`,
`continue`, recoverable Error propagation, Defect, Cancellation이다.
return/break/throw payload를 먼저 staging하고 inner region부터 outer
region으로 나가며, 한 region 안에서는 실제 도달해 등록된 action을 역
dynamic registration order로 실행한다. loop body에는 도달한 iteration별
dynamic region이 있으므로 `continue`가 그 iteration의 cleanup을 먼저
끝낸다.

suspension은 exit가 아니며 cleanup action을 0개 실행한다. 대신 모든
live owner, borrow, reservation, isolation fact와 cleanup obligation을
그대로 보존한다. 이 상태가 suspension을 넘어 유효하다는 proof가 없으면
suspension site를 거부하며, `defer` 자체를 blanket suspension 금지로
해석하지 않는다.

### 14.2 primary와 suppressed failure

body failure가 있으면
cleanup failure가 그것을 덮어쓰지 않는다.
body failure는 primary로 남고,
cleanup failure는 실제 LIFO execution order로
suppressed list에 붙는다.

body가 정상일 때 처음 실패한 cleanup은 primary가 되고 뒤 cleanup
failure가 suppressed로 붙는다. cleanup을 retry하거나 Error, Defect,
Cancellation identity를 다른 축으로 바꾸지 않는다. deferred call의
정상 result는 ordinary expression statement와 같은 responsibility 검사를
받아 `UNIT_NO_VALUE`, `DISCARD_CLEANUP_FREE_VALUE`,
`CLEAN_OWNED_TEMPORARY` 중 하나로 봉인된다. 미처리 responsibility는
조용히 버리지 않는다.

`concur`에서 child failure만 경쟁하면
가장 작은 lexical `spawn_index`가 primary다.
나머지는 index 오름차순으로 suppressed된다.
scheduler completion order는 evidence가 아니다.

### 14.3 Cancellation lifecycle

Cancellation은 다음 monotonic event를 가진다.

1. request
2. observation
3. acknowledgement
4. cleanup barrier
5. terminal cancellation

한 CancellationId에서 event는 idempotent하고
뒤로 돌아가지 않는다.
Cancellation은 ErrorSet member로 변환되지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private def#async supervise() -> Unit = {
    concur {
        defer releaseResources()
        let child = spawn work()
        await child
    }
}
```

Cancellation이 관찰되어도
`releaseResources()` cleanup barrier를 건너뛰지 않는다.

## 15. actor observation

### 15.1 actor identity

한 `ActorId`는
한 isolated `StateRegionId`와 `MailboxId`를 소유한다.
한 번에 하나의 admitted `ActorTurnId`만
그 state를 변경한다.

turn이 suspend되어도
같은 turn identity와 dequeue/mutation authority를 보존한다.
암시적 reentrancy를 만들지 않는다.

### 15.2 mailbox profile

mailbox clause가 없으면
`logical_unbounded_v1`이다.
이는 language capacity rejection이 없다는 뜻이지
무한 저장 공간을 약속한다는 뜻이 아니다.

positive static `#mailbox(capacity: N)`은
`bounded_reject_v1`이다.
full이면 precommit에서 즉시
`ActorMessageError::mailboxFull`을 반환한다.
대기, retry, suspension, silent drop이 없다.

### 15.3 prepare와 enqueue commit

actor `:~` send는 ordinary method call이 아니다.
prepare 단계는 receiver를 한 번 평가하고 ordered argument를
왼쪽에서 오른쪽으로 한 번씩 평가하지만 owner를 아직 넘기지
않는다. trailing closure가 있으면 argument 다음에 capture environment를
source order로 획득한다.

actor isolation을 건너는 closure는 독립적으로 transfer 가능해야 한다.
borrow/inout escape, 허용되지 않은 suspension, 숨은 effect/error/cleanup을
trailing 표면이 합법화하지 않는다.

precommit rejection은 다음을 보장한다.

- sender owner 유지
- message sequence 없음
- ownership commit 없음
- hidden retry 없음

성공한 enqueue commit은
payload owner를 actor에 정확히 한 번 넘기고
다음 `channel_sequence`를 할당한다.

### 15.4 FIFO key

정확한 ordering key는
`(SenderId, ReceiverActorId, MailboxProfileId)`다.

같은 key에서 성공적으로 commit된 message만
strictly increasing sequence를 받고
그 순서로 dequeue된다.

서로 다른 sender 사이의 global order,
fairness, distributed delivery,
exactly-once delivery는 보장하지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
private def sendTwo(counter: Counter) -> Unit = {
    let first = counter :~ add value: 1
    let second = counter :~ add value: 2
}
```

두 send가 같은 sender/receiver/mailbox key에서
성공적으로 commit되면
두 번째 sequence는 첫 번째보다 크다.
거부된 send는 sequence를 소비하지 않는다.

### 15.5 request

reply type `T`의 request는 즉시
`Result<Reply<T>, error ActorMessageError>`를 만든다.
source는 admission Result에서 Reply를 꺼낸 뒤
명시적으로 `await`한다.

commit은 `CorrelationId`와 `ReplyId`를 하나 만든다.
correlation은 reply, declared failure,
Cancellation 중 정확히 하나의 terminal outcome을 가진다.

receiver가 admission 뒤 reply 전에 닫히면
admitted reply의 declared failure axis에서
`receiverClosedBeforeReply`가 발생한다.

structured spawn은 owner-bound `Run<T>`를 만들고 actor transport
descriptor를 갖지 않는다. 성공적으로 admission된 actor request만
`Reply<T>`를 만들며 typed HIR, module API digest와 MIR은 정확히 일곱
field의 `ReplyResponsibility` residue를 보존한다.

1. `result_type`
2. `normalized_handler_error_set`
3. `cancellation_axis`
4. `isolation_owner`
5. `reply_id`
6. `correlation_id`
7. `terminal_transport_failure = {receiverClosedBeforeReply}`

따라서 handler ErrorSet이 `E`이면 await의 ErrorSet은 정확히
`normalize(E | ActorMessageError::receiverClosedBeforeReply)`다.
`mailboxFull`과 `receiverClosedBeforeAdmission`은 admission `Result`에만
있고 descriptor에는 없다. compatibility, control-flow join, storage와
API export가 bare result type만 남기고 residue를 지우는 것은 금지된다.
기본 비교는 normalized static field equality이며, handler ErrorSet만
명시적으로 admitted된 subsumption proof로 넓힐 수 있다. 서로 다른
request의 `correlation_id`는 storage와 join 뒤에도 각 값에 남는다.
module API digest의 `reply_id`와 `correlation_id` field는 runtime ID가
아니라 `per_value_non_forgeable` 정책 marker다. concrete identity는 성공한
enqueue commit 이후 value-level typed HIR/MIR descriptor에만 생긴다.

이 법칙은 design-static contract로 닫혀 있지만 parser/checker/backend
제품 실행 증거는 여전히 `NOT_RUN`이다. 즉 backend가 구현될 때 지켜야 할
관찰 계약은 정해졌지만, 특정 opcode·layout이나 actor runtime PASS를
주장하지 않는다.

### 15.6 cancellation race

enqueue commit 전 Cancellation 관찰은
admission을 중단하고 sender owner를 보존한다.
sequence도 없다.

commit 뒤 Cancellation은
message를 철회하거나 renumber하지 않고,
moved source owner를 sender에 돌려주지 않는다.
request라면 correlation-bound reply lifecycle에만 영향을 준다.

## 16. shared-state observation

### 16.1 SharedCell admission

`SharedCell<T>`는 normalized Plain payload만 받는다.
Plain은 lifecycle owner가 없다는 책임이지
raw layout, byte-copy, lock-free representation을 뜻하지 않는다.

construction은 input owner를 move로 받고
성공 뒤 stored owner가 정확히 하나다.
hidden clone과 hidden cleanup은 없다.
source는 ordinary qualified call
`SharedCell::new(move value)`다.

### 16.2 withValue

`withValue`는 receiver의 `~` message operation이다.
callback callable profile은 `#scoped`, source binder mode는 `borrow`이며
invocation이 region을 소유한다.
borrow는 escape하거나 suspend할 수 없다.
ordering은 sequentially consistent다.
관찰을 위해 value를 복제하지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/shared-state-coherence.json -->
```deeplus
private def observe(cell: SharedCell<Int>) -> Int = {
    return cell ~ withValue { borrow value => value }
}
```

closure는 scoped observation 안에서만
borrowed value를 읽는다.
return되는 `Int`가 reusable value라는 사실과
borrow 자체의 escape는 별도다.

### 16.3 replace

`replace`는 새 owner를 move로 받고
commit 하나로 stored owner를 교체하며
old owner를 result로 돌려준다.
source는 `cell ~ replace move next`다.

성공 뒤 stored owner count는 하나다.
sequentially consistent ordering을 갖는다.
precommit failure는 old stored owner를 보존한다.

### 16.4 SharedMutex

current minimum의 공개 identity는
`SharedMutex<T: SharedMutexPayload>`다. `SharedMutexPayload`는 Trait가 아닌
sealed compiler-known constraint다. 전용 `SharedMutexPayloadDescriptorR1`을
통해 cleanup-free Reusable/Affine payload만 받고 Resource, cleanup 책임,
borrow/inout view, opaque 또는 unbounded generic을 거부한다. 이 판정은
다른 responsibility evidence를 합성하지 않으며 move commit 전에 끝난다.
poisoning과 recursive lock은 current가 아니다.
생성은 ordinary qualified call `SharedMutex::new(move value)`다.

`withLock`은 receiver의 `~` message operation이다. callback callable
profile은 `#scoped`, source binder mode는 `inout`이며 invocation이 region을
소유한다. 그 region은 receiver-bound, non-reentrant, nonsuspending이고
`inout T` place 하나를 제공한다.
place는 escape할 수 없다.

unlock은 return, Error, Defect,
Cancellation의 모든 path에서
infallible exactly-once cleanup이다.
body failure가 primary로 남는다.
MIR의 `SharedMutexWithLockPlan`은 `LOCK_ACQUIRE → LOAN_BEGIN_EXCLUSIVE →
callback → LOAN_END → LOCK_RELEASE` 순서를 네 terminal outcome에서 동일하게
검증한다. wrapper unlock은 payload cleanup으로 세지 않는다.

### 16.5 happens-before

같은 mutex에서 성공한 unlock은
다음 성공 lock보다 happens-before다.

이 법칙은 global lock order,
fairness, scheduler order,
deadlock freedom을 약속하지 않는다.

### 16.6 필수 MIR event

shared-state contract는
`synchronization` event family와
다음 identity를 요구한다.

- `sync_id`
- `operation_id`
- `owner_id`
- `cleanup_region_id`

필수 operation은 다음과 같다.

- `observe_begin`
- `observe_end`
- `replace_commit`
- `lock_acquire`
- `lock_release`

runtime receipt는 아직 `NOT_RUN`이다.
이 event 이름은 설계 정적 requirement이며
실제 xVM trace가 검증되었다는 뜻이 아니다.

## 17. string과 interpolation

### 17.1 닫힌 literal

plain String과 raw String은
immutable `ConstString` payload로 lowering된다.
raw scanner는 body scalar를 그대로 제공하고
escape와 interpolation machine을 실행하지 않는다.

Char는 정확히 한 Unicode scalar다.
String index는 scalar position을 관찰하고 `Char`를 반환한다.
Bytes index는 `UInt8`이며
String/Bytes implicit conversion은 없다.

### 17.2 interpolation plan

scanner/parser는 braced expression,
shorthand path, format boundary를 구분한다.
checker는 runtime 평가 전에 non-String hole마다
exact `Display` witness 하나를 선택한다.
direct segment와 hole은 source order대로 처리되며,
braced expression은 한 번 평가되고 shorthand path의 root도
한 번만 평가된다. shorthand selector는 read-only projection이다.

`Display.display()`는 receiver를 borrow하고,
동기·비소비·`throws Never effects {}` 계약으로
fresh String segment를 만든다. locale, serialization, parsing,
provider, reflection, redaction 또는 authority lookup은 암시되지 않는다.
`Secret`과 `Redacted`는 먼저 명시적 redaction API를 통과해야 한다.
hole 평가 실패는 final String publish 전에 발생하며
temporary segment를 역순 cleanup한다.

### 17.3 Stable format spec

`${expr:format}`의 내부 문법은 작은 `Align? Width`로 닫힌다. `Align`은
`<`, `>`, `^`이고 생략하면 왼쪽 정렬이다. `Width`는 선행 0·부호·밑줄·
공백이 없는 1부터 1,000,000까지의 10진수다. fill은 U+0020 SPACE 하나며,
폭은 Unicode scalar 개수로 센다. 폭보다 긴 결과는 절대 자르지 않는다.

왼쪽 정렬은 오른쪽, 오른쪽 정렬은 왼쪽을 채운다. 가운데 정렬은 부족한
개수의 절반을 왼쪽에 내림 배치하고 나머지를 오른쪽에 둔다. 따라서 홀수
padding의 여분 SPACE 하나는 오른쪽에 온다.

scanner는 raw format text와 span을 하나의 opaque token으로 보존하고,
checker가 내부 문법을 검증한다. 잘못된 text는
`INTERPOLATION_FORMAT_SPEC_INVALID`로 HIR 전에 거부된다. String hole은
값을 그대로 사용하고 non-String hole만 선택된 `Display`를 한 번 호출한
후 padding한다. format plan은 `Display`에 전달되지 않으며 locale,
provider, serialization 또는 custom formatter 권한을 만들지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/string-interpolation-format-spec-core-r1.json -->
```deeplus
let left = "${name:<12}"
let right = "${name:>12}"
let centered = "${name:^12}"
let defaultLeft = "${name:12}"
```

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/grammar/deeplus.dpg -->
```deeplus
private let greeting = "Hello, $user.name"
```

이 예제는 Stable interpolation syntax를 보여 준다.
ordered segment plan과 Display boundary는 정적으로 닫혔지만,
formatter, runtime 및 backend product execution은 `NOT_RUN`이다.

## 18. NumericArray transpose

attached postfix `A^`는
spaced infix numeric power와 다른 grammar owner다.
operand는 NumericArray여야 하고
rank-1에는 row/column orientation evidence가 필요하다.
complex adjoint가 아니다.

current MIR은 operand를 정확히 한 번 평가하고
semantic nonowning, owner-bounded read-only coordinate view 하나를 만든다.
추상 rank-2 shape tuple `(R,C)`는 `(C,R)`로 바뀌고
logical coordinate `(i,j)`는 source `(j,i)`를 가리킨다.
rank-1은 이미 admitted된 row/column orientation witness를 뒤집는다.

transpose는 implicit element copy·language-observable allocation·mutation
authority를 만들지 않고
source owner, one-based coordinate, provenance, effect와 lifetime을
보존한다. view는 source보다 오래 살거나 isolation boundary를
건널 수 없고, shareability를 새로 증명하지 않는다.
complex adjoint가 아니며 backend representation과 incidental storage
strategy는 별도로 남는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
private let matrix = #2,3[
    1, 2, 3;
    4, 5, 6;
]
private let transposed = matrix^
```

syntax와 static operand boundary는 Stable design이며
`transposed`는 위 법칙의 read-only coordinate view다.
실제 xVM/Cranelift view representation과 실행 지원은 `NOT_RUN`이다.

## 19. semantic identity와 representation identity

### 19.1 분리되는 domain

source semantic value identity는
다음과 독립적이다.

- storage layout
- serialization tag
- runtime discriminant
- foreign ABI identity
- backend lowering identity

semantic equivalence가 layout equality를 뜻하지 않고,
layout equality가 source type equivalence를 뜻하지 않는다.

### 19.2 closed Union

closed Union alternative identity는
source semantic injection을 결정한다.
runtime representation이 tag byte,
niche encoding, pointer bit를 쓰는지는
별도 backend/layout 계약이다.

`subject is Alternative`는
저장된 injection identity를 한 번 읽는
bounded structural test다.
generic RTTI, subtype search,
reflection, provider lookup으로 바꾸지 않는다.

### 19.3 Enum

Enum `VariantId`는
declaring Enum owner 안에서 정적으로 해석된다.
serialization number나 C discriminant와 같은 것이 아니다.

public wire format이나 FFI layout이 필요하면
별도의 explicit contract와 digest가 필요하다.

### 19.4 Plain

Plain은 lifecycle/resource owner가 없는
normalized value responsibility다.
다음을 뜻하지 않는다.

- C-compatible layout
- all-bit-pattern valid
- byte-copy safe
- lock-free
- stable serialization

FFI나 shared-state backend가
Plain만 보고 representation authority를 얻을 수 없다.

## 20. ABI 경계

### 20.1 Deeplus call identity와 backend ABI

Deeplus callable signature는
value/context/witness/rest channel,
ownership, effect/error,
suspension, isolation, return을 보존한다.

backend ABI는 이를 register, stack,
hidden pointer, metadata로 표현할 수 있다.
그러나 source channel을 지우거나
runtime lookup으로 되돌릴 수 없다.

지역 proof에 사용된 `RegionId`와 backend hidden static link는 public API
digest에 export하지 않는다. region-bound callable이 public signature나
escaping value가 될 수 없다는 admission이 먼저 닫혀야 하며, backend
표현 선택이 그 실패를 ABI로 우회해서는 안 된다.

### 20.2 FFI

foreign ABI는 별도 Preview gated boundary다.
target triple, calling convention,
size/alignment/signedness/layout,
pointer provenance,
ownership transfer,
unwind, callback lifetime이 닫혀야 한다.

현재 FFI surface predicate는
design seed이며 product execution은 `NOT_RUN`이다.
Deeplus `Int`를 C `int`와 같은 layout으로
가정해서는 안 된다.

### 20.3 public API digest

API digest는 normalized source responsibility를 보존한다.
backend mangling이나 object file order를
source identity로 사용하지 않는다.

module API compatibility receipt와
runtime execution receipt는 별도다.
하나가 PASS여도 다른 하나를 자동 PASS로 만들지 않는다.

## 21. backend parity

### 21.1 비교 대상

xVM, Cranelift ObjectModule AOT, Cranelift JITModule의 differential run은
다음을 비교해야 한다.

1. ordered observable event trace
2. final normalized value 또는 failure
3. place owner balance
4. cleanup registration/execution balance
5. primary/suppressed failure order
6. concur/run/reply/actor identity와 ordering
7. provider identity와 replay token
8. source provenance가 필요한 diagnostic trace

단순 stdout 비교만으로는 부족하다.

### 21.2 허용되는 차이

다음 차이는 공개 관찰을 바꾸지 않는 범위에서 허용될 수 있다.

- instruction count
- register allocation
- inlining
- stack frame layout
- private allocation address
- JIT compilation timing

하지만 timing이 provider timestamp나
observable scheduling contract에 들어가면
더 이상 무관한 차이가 아니다.

### 21.3 최적화 안전성

optimizer는 다음 보존 의무를 가진다.

- effectful expression 복제 금지
- lazy branch 억제 보존
- precommit failure 전 write 금지
- cleanup LIFO 보존
- actor sequence 보존
- cancellation phase 보존
- witness/provider identity 보존

tail-call optimization이 적용되어도
pending cleanup, suspension,
actor boundary의 관찰을 지울 수 없다.

## 22. worked transaction trace

다음 예제는
argument evaluation, Map lookup,
checked arithmetic, assignment commit,
cleanup을 한 경로에서 보여 준다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private def update(
    inout total: Int,
    deltas: Map<Key, Int>,
    key: Key,
) -> Unit
    throws IndexError
= {
    defer recordAttempt(key)
    total += deltas[key]
}
```

성공 trace는 개념적으로 다음 순서다.

1. call site에서 `total`, `deltas`, `key`를 소스 순서대로 평가
2. `total` inout place 획득
3. cleanup invocation 등록
4. `total` target place 한 번 평가
5. old value 한 번 읽기
6. RHS의 `deltas`와 `key`를 읽고 Map lookup 수행
7. checked addition
8. write 한 번 commit
9. scope exit
10. `recordAttempt(key)` cleanup 실행

Map key가 없으면
6단계에서 `IndexError::keyNotFound`가 발생하고
write는 없다.
checked addition이 overflow하면
7단계에서 ArithmeticDefect가 발생하고
old value는 보존된다.
두 실패 모두 cleanup은 실행된다.

## 23. 양성·음성·경계 예제

### 23.1 Option lazy fallback

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private let chosen = cached ?: loadFromDisk()
```

`cached`가 `some`이면
`loadFromDisk()` event가 없다.

### 23.2 hidden rebase 금지

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private let bounded = [3..5: 10, 20, 30]
private let view = bounded[4..5]
private let item = view[4]
```

view coordinate는 4와 5를 보존한다.
`view[1]`로 암시적 rebase하지 않는다.

### 23.3 precommit owner 보존

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/actor-concurrency-coherence.json -->
```deeplus
private let outcome = worker :~ run move job
```

mailbox admission이 commit 전에 실패하면
sender의 `job` owner가 유지된다.
성공한 enqueue 뒤에는 actor가 owner이며
Cancellation이 되돌리지 않는다.

### 23.4 shared borrow escape

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/shared-state-coherence.json -->
```deeplus
private def invalid(cell: SharedCell<Document>) -> borrowed Document = {
    return cell ~ withValue { borrow value => value }
}
// scoped observation borrow는 call 밖으로 escape할 수 없다.
```

### 23.5 lock 안 suspension

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/contracts/shared-state-coherence.json -->
```deeplus
private def#async invalidLock(mutex: SharedMutex<State>) -> Unit
    effects state
= {
    mutex ~ withLock { inout state =>
        await refresh(state)
    }
}
// withLock의 scoped inout은 nonsuspending이다.
```

### 23.6 static rejection은 MIR 없음

<!-- deeplus-example: illustrative; status: REJECTED_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private let impossible: Int8 = 200
// 정적으로 범위를 벗어나므로 runtime overflow event가 없다.
```

package/re-export/static-value cycle, duplicate import binding, module
signature mismatch, stale interface digest, incomplete resolver seal도 같은
원칙을 따른다. 이 실패들은 admitted HIR와 MIR module initializer,
backend symbol, partial global state를 모두 0개 만든다.

### 23.7 String과 Bytes

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/mir/semantics.md -->
```deeplus
private let text: String = "A"
private let bytes: Bytes = #bytes"\x41"
private let scalar: Char = text[1]
private let octet: UInt8 = bytes[1]
```

같은 문자처럼 보여도
String scalar와 byte value는 다른 domain이다.

## 24. 상호작용

### 24.1 이름 해석과 MIR

label, witness, extension, provider identity는
MIR execution 전에 고정된다.
backend는 runtime registry를 검색해
다른 identity를 선택할 수 없다.

name lookup은 innermost exact namespace/spelling frame에서 끝나며 outer
frame이나 source/import order를 candidate rank로 사용하지 않는다.
ordinary selector의 nominal과 active extension domain이 모두 nonempty면
`MEMBER_EXTENSION_COLLISION`으로 끝나고 MIR call은 없다. exact qualified
extension selector만 그 domain을 직접 고정한다.

### Compile-time module initialization plan

Package dependency와 re-export graph는 acyclic이다. Module-header SCC는
complete header collection 뒤 header/type/signature edge만 있을 때
허용한다. static-value/runtime-initializer/re-export edge는 SCC에서
거부한다.

immutable module static value graph는 compile time에 acyclic하게 평가한다.
모든 value가 성공한 뒤 canonical `DeclId` order receipt와 함께 한 번
atomic commit하고 runtime initializer count는 0이다. 실패는 partial
publication과 cleanup/runtime event를 만들지 않는다. 이 plan은 함수
`static { ... }`의 first-call activation과 다른 owner다.

모듈 artifact는 세 hash domain을 분리한다. `ModuleInterfaceDigest`는
effective public semantic residue만 결속하고 source path/file identity,
origin/proof ID, dependency receipt, private body와 debug span을 제외한다.
`ModuleImplementationDigest`는 그 interface identity와 verified private HIR
semantics를 결속한다. `ModuleCompilationReceipt`는 `TargetId`/`ModuleId`,
package graph, module source-contribution provenance, dependency subreceipt,
resolver trace, visibility closure, initialization plan, interface와
implementation hash를 결속한다. 따라서 private-body-only 변경은 interface
hash를 유지하면서 implementation과 full receipt hash를 바꾼다. script는
importable interface가 없어서 `interface_sha256 = null`이다. dependency
subreceipt는 imports, activations, required provider interfaces만 결속하며
전체 receipt와 같은 artifact가 아니다. stale receipt는 lowering 전에
거부하며 backend link/load order로 고칠 수 없다. 이 문서 계약은 22 OPEN
P1과 15/15 `NOT_RUN`을 그대로 유지한다.

### 24.2 pattern과 ownership

Pattern test는 nonconsuming probe이고
guard 성공 뒤에만 move/inout commit을 적용한다.
flow proof와 runtime owner state는 별도지만
commit plan에서 일치해야 한다.

### 24.3 effects와 cleanup

EffectRow는 observable operation을 기술한다.
ErrorSet은 recoverable failure를 기술한다.
Defect와 Cancellation은 별도 terminal axis다.
cleanup은 네 경로 모두에서 책임을 유지한다.

### 24.4 actor와 shared state

actor isolation과 SharedCell/SharedMutex는
서로 다른 concurrency owner다.
shared wrapper가 actor transferability를 자동 합성하지 않고,
actor reference가 shared-state lock authority를 주지 않는다.

### 24.5 tooling

xVM agent와 tail-call analyzer는 side receipt를 낸다.
UML provider는 ordinary source를 생성한 뒤
frontend를 다시 통과한다.
도구가 MIR event를 삽입하거나
language semantics를 바꿀 수 없다.

## 25. 정적 closure와 남은 제품 handoff

이번 보완은 이전 문서에서 서로 흩어져 있거나 미폐쇄였던
source-observable 법칙을 다음처럼 고정한다.

| 항목 | 현재 정적으로 닫힌 법칙 | 여전히 주장하지 않는 것 |
|---|---|---|
| ternary | condition-once, one lazy arm, responsibility join | backend opcode·실행 PASS |
| interpolation | braced/shorthand의 direct String 또는 preselected Display, ordered holes, `Align? Width`, Unicode-scalar SPACE padding, no truncation, atomic publication | parser/checker/xVM/Cranelift/formatter 제품 실행 PASS |
| NumericArray postfix transpose | owner-bounded read-only coordinate view | 실제 layout·backend 지원 |
| Map unfold | later key wins, exact cleanup, failure-atomic plan | hash representation·성능 |
| actor request declared failure | `ReplyResponsibility`에 ErrorSet·correlation·terminal failure 보존 | actor runtime 실행 PASS |
| `mut` | callee-owned local, no write-back alias, exact cleanup | compiler/backend 구현 PASS |
| Rational | transactional `<p/q>`, BigInt 기약분수, `RationalConst` residue | parser/checker/HIR/MIR/runtime 실행 PASS |
| Complex | 붙은 float-`i`, exact Rep, signed-zero-aware component residue | layout·ABI·stdlib/runtime 실행 PASS |
| scalar power | static matrix, base-then-exponent once, closed operation/profile identity | HIR/MIR/backend 실행 PASS |
| HIR-H1 bridge | closed verified phase types와 capability receipt 설계 | source activation·MIR-X1 채택·구현 |
| nonescaping lexical access | exact closed proof, call-time read, orthogonal residence/environment | source activation·frontend/checker/MIR/backend 실행 PASS |

정적 closure는 feature P1을 닫거나
15개 제품 lane을 실행한 것으로 해석되지 않는다.
구현은 이 표의 observable law를 그대로 지켜야 하지만,
opcode·layout·ABI·최적화는 그 관찰을 바꾸지 않는 범위에서만
자유롭게 선택할 수 있다. target-bound receipt가 나오기 전까지
제품 상태는 `NOT_RUN`이다.

## 26. 제품 `NOT_RUN` 경계

현재 operational 계약은 E2 설계 정적 증거다.
다음은 실행되지 않았다.

- parser가 모든 source를 수용하는지
- checker가 모든 rejection을 내는지
- HIR identity가 실제로 안정적인지
- MIR lowering이 event를 방출하는지
- xVM이 event order를 지키는지
- Cranelift ObjectModule AOT가 xVM과 같은지
- Cranelift JITModule가 xVM/AOT와 같은지
- cancellation race fixture가 통과하는지
- actor schedule permutation이 통과하는지
- shared-state synchronization trace가 존재하는지
- ABI layout이 target에서 검증됐는지
- independent conformance runner가 통과하는지

15개 lane을 생략 없이 적으면 다음과 같다.

| # | product lane | 상태 |
|---:|---|---|
| 1 | Rust frontend lexer | `NOT_RUN` |
| 2 | Rust frontend parser | `NOT_RUN` |
| 3 | Rust HIR lowering | `NOT_RUN` |
| 4 | Rust integrated checker | `NOT_RUN` |
| 5 | Deeplus MIR lowering | `NOT_RUN` |
| 6 | xVM bytecode emitter | `NOT_RUN` |
| 7 | xVM interpreter | `NOT_RUN` |
| 8 | Cranelift ObjectModule AOT backend | `NOT_RUN` |
| 9 | Cranelift JITModule backend | `NOT_RUN` |
| 10 | formatter/LSP | `NOT_RUN` |
| 11 | stdlib/provider runner | `NOT_RUN` |
| 12 | official tooling | `NOT_RUN` |
| 13 | independent conformance | `NOT_RUN` |
| 14 | cross-backend conformance | `NOT_RUN` |
| 15 | actual user/team study | `NOT_RUN` |

즉 “15/15”는 15개 중 15개가 성공했다는 뜻이 아니라, **15개 모두
실행하지 않았다**는 뜻이다. 문서 parse나 static fixture 검증을 어느
lane의 target-bound PASS로 바꾸어 기록해서는 안 된다.

문서의 단계별 trace는
normative design을 설명하는 conceptual trace다.
실제 artifact hash와 target receipt가 없으면
제품 PASS가 아니다.

## 27. backend 검토 체크리스트

1. source role과 parser owner가 고정되었는가.
2. 문법 또는 admission에 실패한 node가 MIR로 내려가지 않는가.
3. HIR identity가 runtime String lookup으로 바뀌지 않는가.
4. operand와 argument를 정확히 한 번 평가하는가.
5. source order를 보존하는가.
6. strict/lazy operator 차이를 보존하는가.
7. assignment place를 한 번 평가하는가.
8. failure 전 partial write가 없는가.
9. move commit 전 source owner를 보존하는가.
10. borrow/inout region을 넘기지 않는가.
11. resource cleanup owner가 정확히 하나인가.
12. cleanup LIFO와 suppression 순서를 보존하는가.
13. Cancellation lifecycle이 monotonic한가.
14. Pattern probe가 nonconsuming인가.
15. false guard가 partial move를 만들지 않는가.
16. flow join이 place state를 보존하는가.
17. anonymous Union을 만들지 않는가.
18. Set iteration order를 semantic promise로 만들지 않는가.
19. Map key를 static label로 바꾸지 않는가.
20. Map unfold의 later-key·cleanup·atomic-publication 법칙을 보존하는가.
21. readonly slice를 hidden copy/rebase하지 않는가.
22. actor precommit rejection에서 owner와 sequence를 보존하는가.
23. actor turn identity를 suspension에서 유지하는가.
24. shared-state event identity를 보존하는가.
25. Plain에서 raw layout을 추론하지 않는가.
26. semantic type과 ABI/layout을 분리하는가.
27. interpolation의 `Align? Width`, scalar padding, direct String/Display-once와 no-truncation 법칙을 그대로 보존하는가.
28. xVM/Object AOT/JIT trace를 같은 기준으로 비교하는가.
29. tooling side receipt가 program event를 바꾸지 않는가.
30. product claim이 target-bound receipt를 갖는가.
31. canonical HIR에 invalid, unresolved, candidate 또는 placeholder가
    남지 않는가.
32. Rational constant가 BigInt 기약분수와 positive denominator를
    보존하는가.
33. Complex constant와 principal power가 component signed zero를
    보존하는가.
34. power base와 exponent를 그 순서로 정확히 한 번 평가하는가.
35. power operation/profile을 expected result나 runtime 값으로 다시
    고르지 않는가.
36. MIR-X1 또는 backend helper availability를 current semantic authority나
    HIR dispatch로 오해하지 않는가.

## 28. 정본 근거

- [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
  - machine state와 observation
  - 평가, call, assignment, binding
  - failure, cleanup, actor, backend parity
  - deferred product handoff
- [`spec/types/type-system.md`](../../spec/types/type-system.md)
  - normalization과 value identity
  - ownership, Set, actor, AsyncSequence
  - numeric, Pattern, flow proof
- [`spec/contracts/value-operator-indexing-coherence.json`](../../spec/contracts/value-operator-indexing-coherence.json)
  - integer/float/operator/assignment/index/slice
- [`spec/contracts/rational-complex-numeric-coherence.json`](../../spec/contracts/rational-complex-numeric-coherence.json)
  - Rational/Complex value, fixed arithmetic와 scalar power
- [`spec/contracts/hir-h1-current-mir-bridge.json`](../../spec/contracts/hir-h1-current-mir-bridge.json)
  - closed HIR-H1 phase, literal/power plan, capability receipt
- [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
  - evaluation, flow join, cleanup
- [`spec/contracts/nonescaping-lexical-access.json`](../../spec/contracts/nonescaping-lexical-access.json)
  - orthogonal HIR residence/environment와 ordinary ancestor-rooted place read
- [`spec/contracts/type-refinement-narrowing-coherence.json`](../../spec/contracts/type-refinement-narrowing-coherence.json)
  - Pattern probe/commit과 flow proof
- [`spec/contracts/actor-concurrency-coherence.json`](../../spec/contracts/actor-concurrency-coherence.json)
  - mailbox, message, correlation, cancellation
- [`spec/contracts/shared-state-coherence.json`](../../spec/contracts/shared-state-coherence.json)
  - SharedCell, SharedMutex, synchronization event
- [`spec/language.md`](../../spec/language.md)
  - source surface와 진단 경계
- [`library/prelude/prelude.md`](../../library/prelude/prelude.md)
  - language-facing identity와 library boundary

이 장은 위 정본의 projection이다.
MIR 정적 법칙이 닫혔다는 사실과 target-bound 구현·제품 증거는
서로 다른 층이다. 이 장의 예제나 설명만으로
xVM·Cranelift·formatter·runtime 지원을 주장할 수 없다.


<!-- IR-OWN-R8-REF-18 -->
### HIR/MIR 투영과 zero-fabrication fence

`borrow place`는 기존 HIR-H1 `PlaceAccess/BorrowShared` 계획을 재사용하고
MIR에서 Shared `LoanId`를 만든다. 문맥 anchor는 enclosing operation의
`HirContextAdaptationPlan`에 흡수되어 MIR에 독립 node를 남기지 않는다.
두 경우 모두 source operand는 정확히 한 번, 소스 순서대로 평가된다.

### 2.3.5 Current R10 machine-schema binding

<!-- R10-HIR-MIR-MACHINE-CONTRACT -->

The Stable-design pipeline now binds
`Verified<CanonicalHirH1> -> ExecutableHirH1 ->
Verified<DeeplusMirR1>`. `MirCapabilityReceiptR1` is recomputed from the exact
reachable lowering keys and capability dependency closure; a failure retains
the verified HIR and constructs no executable HIR.

The HIR catalog contains 128 identities. The lowering registry has 102 Current
rows and 111 at the explicit-Preview maximum. Deeplus MIR R1 has 29 operations,
17 terminators, 12 linear token kinds, 11 responsibility axes, and 26 design
capabilities. These design-machine counts are not production or target
execution evidence. `ProposedMirX1` remains a noncanonical compatibility
target, and all 15 product lanes remain `NOT_RUN`.

## 소유권 tooling sidecar와 backend 위치

소유권 tooling projection은 HIR/MIR을 바꾸지 않는 sidecar다. 각 row는
정확한 semantic identity와 program point를 가리키며 place, owner, loan,
cleanup token 상태를 원본 ownership state와 손실 없이 대응시킨다.
`MaybeMoved`에서는 특정 predecessor를 선택하지 않고 `JoinConflictId`와
관련 predecessor 전체를 보존한다. `Suspended`나 `Ended` loan은 화면에
표시할 수 있지만 접근 권한을 부여하지 않는다. `Consumed` cleanup token은
다시 `Available`로 표시될 수 없다.

paused runtime row는 `RuntimeInstanceId`, `ExecutionId`, activation frame,
`pause_epoch`와 정확한 runtime/debug receipt에 결속된다. 이 receipt가 없으면
row와 backend location sidecar는 사용할 수 없다. xVM slot, CLIF value,
register, stack slot과 machine address는 pause 동안만 유효하며 semantic
identity, 동등성 근거, module/API residue 또는 projection digest에 포함되지
않고 resume과 함께 만료된다.

현행 main은 managed-reference profile과 continuation interface의 exact
digest를 정본으로 결속한다. 따라서 `RootId`와 `ContinuationReceiptId`의
패널 스키마는 이 digest에 결속되지만, runtime/debug 실행 영수증이 없는
동안 실제 row는 `UNAVAILABLE_RUNTIME_NOT_RUN`으로 비워 둔다. 정적 설계
결속만으로 runtime identity나 관측값을 합성하지 않는다.

actor 전송 projection도 commit receipt만 읽는다. 거부되었거나 commit 전인
send에서는 sender가 owner를 유지하며, `enqueue_committed`에서만 receiver
owner 또는 shared evidence와 channel-local sequence가 생긴다. 도구는 dual
owner나 cross-channel/global order를 합성하지 않는다.

이 절은 design/static obligation만 닫는다. runtime과 debugger 실행 및 모든
product lane은 `NOT_RUN`이다.
