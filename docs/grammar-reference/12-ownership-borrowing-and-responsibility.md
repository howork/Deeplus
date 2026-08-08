# 소유권, 대여, 책임

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 Deeplus의 owner/place state, `move`, `borrow`, `inout`,
resource cleanup, capture, borrowed Facet, shared-state 최소 프로필을
설명한다. type spelling 하나로 representation, alias, shareability,
transferability를 추정하지 않는다.

현행 예제는 corpus의 `expected_outcome: accept`,
`source_activation: none` 항목이다. `source_activation: stdlib` 예제는
별도 표준 라이브러리 경계로 구분한다. 제품 parser/checker/lowering/
runtime/tooling 실행은 모두 `NOT_RUN`이다.

## 문법

### parameter와 type의 ownership mode

```ebnf
ParameterMode      ::= "borrow" | "mut" | "move" | "inout"
OwnershipQualifier ::= "owned" | "borrowed" | "mut" | "inout"
TypePrefixParselet ::= OwnershipQualifier
```

type qualifier는 다음의 닫힌 책임 집합을 이룬다.

| 표면 | 정규화 identity | 뜻 | region |
|---|---|---|---|
| 접두사 없음 | `UNQUALIFIED` | base type의 기본 책임을 그대로 사용 | 없음 |
| `owned T` | `OWNED` | 명시적 단독 owner와 cleanup/transfer 책임 | 없음 |
| `borrowed T` | `BORROWED` | 읽기 전용 shared view | 반드시 결속 |
| `mut T` | `MUT` | 변경 가능한 단독 owner | 없음 |
| `inout T` | `INOUT` | 변경 가능한 exclusive view | 반드시 결속 |

`owned`가 representation이나 ABI를 뜻하는 것은 아니며, 접두사가 없는
타입을 자동으로 `owned`로 바꾸지도 않는다. `mut T`는 mutable owner이고
`inout T`는 region-bound view이므로 둘은 교환할 수 없다. 모든 qualified
wrapper는 invariant이며 qualifier 사이의 암시적 subtype/coercion은 없다.

alias를 펼친 뒤 qualifier는 정확히 하나 이하여야 한다. 따라서
`owned borrowed T`, `mut inout T`처럼 겹친 형태는 앞의 qualifier가
이긴다고 해석하지 않고 거부한다. postfix `?`가 qualifier보다 강하게
결합하고 `&`, `|`는 약하게 결합한다. 예를 들어 `borrowed A?`는
`borrowed (A?)`이고 `borrowed A | B`는 `(borrowed A) | B`다. 합성 타입
전체를 qualify하려면 `borrowed (A | B)`처럼 괄호를 쓴다.

함수 타입의 anonymous input에는 기존 parameter mode 표면을 그대로
쓴다. 바깥 괄호 뒤의 `->`를 확인한 같은 `ParenTypeSyntax` owner만
`(borrow T)`, `(mut T)`, `(move T)`, `(inout T)`의 첫 단어를 channel
mode로 commit한다. 함수 입력 자체를 `mut T` 또는 `inout T` qualified
type으로 쓰려면 `((mut T)) -> R`처럼 안쪽 TypeRef를 한 번 더 묶는다.
parser와 formatter는 이 두 identity를 서로 바꾸지 않는다.

`owned T`와 `mut T`는 base type이 허용하는 local/storage/result/public
위치에 남을 수 있다. `borrowed T`는 정확한 owner region이 모든 use보다
길 때만 허용한다. borrowed result는 invocation-bounded callable이며 HIR과
module API residue가 정확히 하나의 input/receiver origin을 지목할 때만
허용한다. `inout T`는 local 또는 private invocation-bounded exclusive
view로만 허용하며 field/static/result/export/capture/suspension/actor/
concur/FFI 경계를 넘을 수 없다. region 누락이나 escape는
`BORROW_ESCAPE_OWNER_REGION`, 그 밖의 qualifier 조합·문맥 위반은
`OWNERSHIP_MODE_ADMISSION_FAILED`가 primary다.

parameter mode는 호출 경계의 책임이고 type qualifier는 normalized type
책임이다. 같은 단어를 사용해도 문법 owner와 identity field는 보존된다.

parameter `mut x: T`는 argument를 한 번 얻어 callee-owned mutable local
place에 넣는다. affine owner는 callee로 이전되고 caller에는 write-back
alias가 없다. `inout x: T`는 caller의 정확한 place를 exclusive하게
빌려 같은 place에 변경을 commit한다. `move x: T`는 transfer를 요구하되
그 자체로 mutation 권한을 만들지 않는다. type-side `mut T`는 unique
mutable owner 책임이며 `inout` channel의 다른 철자가 아니다.

### expression과 capture

```ebnf
ExpressionPrefixParselet ::= "+" | "-" | "not" | "~~"
                           | "move" | "borrow" | "&" | "await"

CaptureItem ::= ("let" | "var") Identifier "=" Expr
              | CaptureMode Identifier
              | Identifier
CaptureMode ::= "borrow" | "inout" | "move" | "clone"
              | "deep" | "copy" | "once"
```

`move place`는 owner를 이전하고 `borrow`/`&`는 허용된 region의 view를
만든다. closure capture descriptor는 lifetime, call-right, environment
receiver, effect/error/isolation/suspension 책임의 일부다.

capture `copy`는 exact `CopyValue` responsibility evidence를 요구하고,
`clone`은 선택된 `Clone` witness와 그 error/effect residue를 보존한다.
`deep`은 별도 graph/cycle/alias profile이 닫히지 않았으므로 Preview
Design으로 parse되지만 현행 gate에서 활성화되지 않는다. capture `once`와
callable `#once`는 다른 identity이며 자동 추론하지 않는다. 현행 profile은
one-shot field를 가진 callable에도 명시적 `#once`를 요구한다.

각 capture는 `CaptureFieldId(CapturePlanId, source ordinal, canonical name)`로
식별한다. reference capture와 `let`/`var` initializer capture는 별도 HIR
variant다. initializer는 enclosing scope에서 왼쪽부터 정확히 한 번
평가하고 capture binder는 body에서만 함께 보인다. 중복 binder·중복 source
place·self/forward initializer reference는 평가 전에 거부한다. 실패하면
준비된 prefix의 loan, move reservation, owned temporary만 역순 정리하고,
성공하면 하나의 complete environment만 commit한다. 외부 effect 자체를
rollback하거나 partial environment를 publish하지 않는다.

### nonescaping lexical access와 capture의 구분

`nonescaping_lexical_access`는
`CURRENT_NORMATIVE_STABLE_DESIGN_CONTRACT`이며 `source_activation: none`,
제품 15개 lane은 모두 `NOT_RUN`이다. 이 설계에서 동기적이고 같은
isolation에 있으며 escape하지 않는다고 정확히 증명된 local `def` 또는
closure는 ancestor place를 capture environment에 넣지 않고 호출 시점에
읽을 수 있다.

이 접근은 read-only·nonconsuming이다. ancestor place에 대한 write,
`inout`, `move`, consume, 호출보다 오래 사는 derived borrow에는 적용되지
않는다. local `def`의 direct call only, closure의 immediate invocation,
direct call만 있는 bounded local binding, 선택된 정확한 `#scoped` formal
같이 닫힌 proof가 있을 때만 허용하며, opaque flow나 return/storage,
generator/async/concur/spawn/Actor/isolation crossing에서는 거부한다.

capture list의 세 상태는 서로 다르다.

- capture list 없음: 위 조건을 만족하는 lexical dependency를 추론할 수 있다.
- `[]`: ancestor-frame dependency가 없다는 assertion이다. module, type,
  Prelude dependency나 purity까지 없다는 뜻은 아니다.
- nonempty list: 기존 explicit capture acquisition plan이다. explicit
  capture와 남은 lexical dependency는 동시에 존재할 수 있다.

따라서 residence는 `FrameIndependent | RegionBound(RegionId)`,
environment는 `Empty | Explicit(CapturePlan)`이라는 독립 축으로 기록한다.
`[name]` bare capture item은 현행 의미를 그대로 유지한다. lexical read는
호출 시점의 live value를 보지만 `[copy name]`은 생성 시점 snapshot을
유지한다.

### resource와 borrowed Facet

```ebnf
ClassFlavor ::= "value" | "resource"
CleanupDecl ::= DefIntroducer "(" ")" ThrowsClause* EffectsClause* FunctionBody

FacetType ::= "Facet" "<" "borrow" "any" QualifiedTypeReference
              AssociatedTypeConstraintList? ">"
FacetExpr ::= "facet" "[" "borrow" Expr "as" QualifiedTypeReference
              AssociatedTypeConstraintList? "]"
```

현행 Facet은 borrow packaging만 허용한다. payload의 concrete type을
노출하지 않고 Trait evidence를 seal하지만 object owner를 이전하거나
복제하지 않는다.

### typestate resource

```ebnf
TypestateResourceDecl ::= TopLevelVisibility? "typestate" Identifier
                          TypeParameterList? TypestateBody
TypestateBody ::= "{" TypestateTransitionDecl* "}"
TypestateTransitionDecl ::= Identifier "->" Identifier FunctionBody?
```

`TypestateResourceDecl`은 현행 Phase A의 타입·도구 metadata owner이므로
`public`, `common`, `private` 중 하나가 반드시 필요하다. 각 행은
출발 상태와 도착 상태의 이름 및 선택적인 전이 본문을 기록한다. 이
표면만으로 runtime Enum tag, layout/ABI, Trait witness, 권위 또는
암시적 owner 복제가 생기지 않는다. Phase A에는 전이를 호출하는 별도
source suffix, state-bearing generic type, branch narrowing, 실패 rollback
또는 MIR transition event가 없다. 선택적 body는 ordinary checker 규칙으로
정적 검토되는 계약 body이며, 선언만으로 실행 가능한 state mutation API가
생기지 않는다. 실행 가능한 typestate activation에는 초기 state,
명시적 호출 표면, linear owner 전이, 실패/cleanup/join과 MIR identity를
별도 정본에서 닫아야 한다. 제품 실행은 `NOT_RUN`이다.

## 허용과 정적 의미

### place state와 owner

각 place는 use-after-move, overlapping inout, mutable/shared alias,
borrow escape를 거부할 수 있는 상태를 가진다.

- reusable type이 아니면 `move` 뒤 source place를 사용할 수 없다.
- shared borrow가 살아 있는 동안 충돌하는 mutation은 거부된다.
- `inout`은 exclusive이며 복제하거나 겹칠 수 없다.
- resource cleanup responsibility는 move를 따라 새 owner에게 간다.
- consuming receiver가 owner를 계속 반환하는 API라면 모든 성공 경로에서
  `Self`-compatible owner를 정확히 한 번 명시적으로 반환해야 한다.
- owned downcast는 성공 시 target owner, 실패 시 원래 source owner 중
  정확히 하나를 보존한다.

### Plain과 Shared, 공유 가능성

`Plain`은 lifecycle/resource owner가 없는 normalized value 책임이다.
raw layout이나 lock-free representation을 뜻하지 않는다. `Shared<T>`는
alias를 만드는 shared owner/handle이며 `Plain`과 다르다. `Shareable`은
관찰 안전성 evidence일 뿐 alias를 만들지 않는다. 어떤 shared wrapper도
payload의 `Transferable` evidence를 자동 합성하지 않는다.

### current shared-state 최소 프로필

`SharedCell<T>`는 normalized Plain payload만 받는다.
`SharedCell::new(move value)`는 ordinary qualified call이다. receiver
operation은 `cell ~ withValue { borrow value => body }`와
`cell ~ replace move next`처럼 `~` message call로 쓴다. `withValue`가
요구하는 `#scoped`는 callback callable profile이고 `borrow`가 source
binder mode다. invocation이 region을 소유하므로 borrow는
escape/suspend할 수 없다. `replace`는 새 owner를 한 번 commit하고 이전
owner를 반환한다.

`SharedMutex<T: SharedMutexPayload>` 최소 프로필은 sealed compiler-known
constraint `SharedMutexPayload`로 payload를 제한한다. 이 constraint는
Trait가 아니며 사용자가 `conform`하거나 annotation으로 증거를 만들 수
없다. 내부 `SharedMutexPayloadAdmitted` predicate는 cleanup-free Reusable
또는 Affine owner-closed graph를 허용하고 Resource lifecycle, cleanup
token/hook/error/effect/authority, suspension/cancellation 책임, borrow/inout
view, opaque 또는 unbounded generic을 거부한다. 이는 `Plain`, copy, clone,
sharing, transfer, layout, ABI, serialization을 추가로 증명하지 않는다.
생성은 이 판정을 move commit 전에 수행하는 ordinary qualified call
`SharedMutex::new(move value)`이고 receiver access는
`mutex ~ withLock { inout state => body }`다. `#scoped`는 callback
callable profile, `inout`은 source binder mode이며 invocation이 region을
소유한다. 이 access는 receiver-bound, non-reentrant, nonsuspending이다.
unlock은 return, Error, Defect, Cancellation의 모든 경로에서 infallible
exactly-once cleanup이다.

MIR 관찰은 API 이름만 남기지 않는다. `SharedCell`의 관찰은 같은
`sync_id`, 고유한 `operation_id`, `owner_id`, `cleanup_region_id`를 가진
`observe_begin`/`observe_end` 쌍이고, `replace` 성공은 그 사이의 단 하나
`replace_commit`이다. `SharedMutex`는 같은 식별자 묶음의
`lock_acquire`, exclusive `loan_begin`, callback, `loan_end`, `lock_release`
순서를 남기며 release는 모든 terminal edge에서 정확히 한 번이다. wrapper가
소유한 unlock cleanup은 payload predicate의 입력이 아니다. xVM과
Cranelift은 이 ordered trace와 owner/cleanup balance를 같게 보존해야 하지만,
현재는 대상 실행 확인서가 없어 `NOT_RUN`이다.

이 두 API는 표준 라이브러리 프로필이며 core source syntax가 아니다.

## 평가·소유권·효과

owner를 바꾸는 operation은 성공 commit 지점이 하나다. commit 전 실패는
원래 owner와 value state를 보존하며 성공은 새 owner에 정확히 한 번
이전한다.

borrow와 view는 owner-bounded다. owner보다 오래 살거나 owner의 move/drop,
run/actor isolation crossing을 지나서는 안 된다. suspension은 live
borrow, isolation, cleanup obligation을 지우지 않는다.

callable value의 return/storage, generator, async suspension, actor message,
Facet packaging, `defer`는 escape boundary다. checker는 capture borrow의
lifetime, lexical dependency의 closed proof와 resource의 exactly-one
cleanup path를 증명해야 한다. 즉시 호출이나 exact `#scoped` call은
계약이 정한 bounded proof가 될 수 있지만, ordinary callable argument는
그 자체로 proof가 아니다.

actor message enqueue commit 전 실패에서는 sender가 moved owner를
유지한다. commit 성공 뒤에는 receiver actor가 owner를 얻고 cancellation이
그 이전을 암시적으로 되돌리지 않는다.

## 현행 예제

### borrow, inout, move 매개변수

현행 예제 `EX-R51a1-059`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def replace(borrow label: String, inout target: Buffer, move replacement: Buffer) -> Unit = {
    log(label)
    target = move replacement
}
```

### 유일한 Box owner

현행 예제 `EX-R51a1-NEW-023`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let node: Box<Node> = Box!(Node!(value: 1))
let moved = move node
```

### owner 보존 downcast

현행 예제 `EX-R51a1-NEW-026`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let outcome: OwnedDowncast<Target, Source> = value ~ downcastOwned
@match outcome {
    ::matched(target) => use(target)
    ::unmatched(original) => recover(original)
}
```

### borrowed Facet

현행 예제 `EX-R51a1-FACET-P-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let printable: Facet<borrow any Printable> = facet[borrow user as Printable]
let text = printable ~ print
```

### 표준 라이브러리 프로필 경계

다음 corpus 항목은 syntax는 현행이지만 `source_activation: stdlib`이므로
core 언어 실행 증거로 해석하지 않는다.

`EX-R51COH-SHARED-001`:

```deeplus
let cell = SharedCell::new(move state)
let label = cell ~ withValue { borrow value => describe(value) }
let previous = cell ~ replace move nextState
```

`EX-R51COH-SHARED-002`:

```deeplus
let mutex = SharedMutex::new(move state)
mutex ~ withLock { inout value => value = update(value) }
```

두 예제 모두 제품 실행은 `NOT_RUN`이다.

## 거부되거나 격리된 형식

### 현행에서 거부

| 형식 또는 주장 | 판정 |
|---|---|
| move 뒤 affine source 재사용 | 거부 |
| 겹치는 `inout` access | 거부 |
| borrow/view의 region escape | 거부 |
| borrowed Facet의 suspension/run/actor crossing | 거부 |
| owner를 암시적으로 `Shared<T>`로 승격 | 거부 |
| `Shareable`만으로 alias 생성 | 거부 |
| Plain에 resource/drop 책임 숨김 | 거부 |
| `SharedMutex`에 lifecycle payload 숨김 | 거부 |
| shared wrapper가 `Transferable` 자동 생성 | 거부 |
| `cell.withValue()`·`mutex.withLock()` 점 호출 | 거부; receiver operation은 `~` |
| callback binder에 `#scoped` 반복 | 거부; `#scoped`는 callable profile |

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### `PREVIEW_NONACTIVATABLE`: owned/inout Facet 검토안

`facet[inout value as Trait]`, `facet[move value as Trait]` 및 대응
`Facet<inout ...>`, `Facet<move ...>`는 보존된 Preview Design이다.
현행 Facet grammar는 `borrow`만 허용한다.

비활성 예:

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/types/type-system.md -->
```deeplus
let mutableView = facet[inout value as Editable]
let ownedView = facet[move value as Printable]
```

도입 전에는 다음이 필요하다.

1. unique owner와 alias/exclusive region 증명;
2. concrete payload drop plan의 정확한 보존;
3. move 성공·실패의 owner 반환 법칙;
4. escape, suspension, actor isolation 규칙;
5. existential safety와 conformance evidence coherence;
6. API/ABI, MIR, xVM/Cranelift lowering identity의 일치;
7. formatter/LSP와 target-bound positive/negative 실행 증거.

문서화는 owned/inout Facet activation, `TCC-P1-002..008` closure, 구현
authority, product PASS가 아니다.

### `PREVIEW_NONACTIVATABLE`: 약한 atomic ordering

weak atomic ordering은 닫힌 memory model과 target receipt contract가 없어
source gate조차 없는 설계 제안이다. 현행 SharedCell/SharedMutex의
sequentially consistent 최소 프로필을 약화하지 않는다.

도입 전에는 operation별 ordering vocabulary, data-race 및 happens-before
법칙, failure ordering, compiler reorder 한계, xVM/Cranelift parity, litmus
test와 target-bound 실행 evidence가 필요하다. 비활성 상태에서는 어떤
atomic source spelling도 발명하거나 예제로 제시하지 않는다.

### 그 밖의 Preview ownership 경계

literal-shaped collection의 freeze/snapshot/view 책임, dynamic Trait state,
local/first-class Witness value는 각 설계 계약에 남아 있으나 현행 alias,
escape, cleanup, ABI, actor-transfer 법칙을 바꾸지 않는다. 새 syntax와
identity는 별도 activation authority 전까지 `PREVIEW_NONACTIVATABLE`이다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- Pattern move/borrow는 structural probe가 아니라 성공의 atomic commit
  시점에 적용된다.
- closure capture와 callable responsibility는
  [함수, 메서드, 클로저, 호출](05-functions-methods-closures-and-calls.md)을
  참고한다.
- failure와 cleanup ordering은
  [제어 흐름, 오류, 효과, 정리](11-control-flow-errors-effects-and-cleanup.md)를
  참고한다.
- ReadonlyView와 collection coordinate는
  [컬렉션, 인덱싱, 슬라이싱](09-collections-indexing-and-slicing.md)을
  참고한다.
- actor message와 structured `concur` run은 owner transfer, cancellation,
  cleanup을 독립 축으로 보존한다.
- type equality는 ownership, effect, error, cancellation, suspension,
  isolation, cleanup residue를 지우지 않는다.

## 소유권 정보를 도구에 표시하는 규칙

포매터, LSP, 디버거는 소유권을 새로 판단하는 주체가 아니다. 이들은 한
소스 revision과 checker snapshot에 결속된 `PlaceId`, `OwnerId`, `LoanId`,
`RegionId`, `CleanupTokenId` 증거를 읽기 전용으로 표시한다. 증거가 없거나
recovery 상태이면 임의로 추론하지 않고 `사용할 수 없음`으로 표시한다.

- hover는 정규화된 타입, 매개변수/소유권 mode, place 상태, 활성 loan,
  cleanup 책임과 escape/suspension 의무를 함께 보여 준다.
- 각 진단의 규칙이 primary 역할과 필요한 관련 위치 수를 결정한다. 같은
  역할의 후보가 여럿이면 안정적인 `SourceOriginId`와 typed identity로
  정렬하며 소스·CFG 순회 순서로 승자를 고르지 않는다.
- 포매터는 `move`, `borrow`, `inout`, `owned`, `borrowed`, `mut`, capture,
  `defer`의 의미와 순서를 바꾸지 않는다. 두 번째 실행은 edit 0개여야 한다.
- 자동 수정은 clone/share/transfer/move/capture/region/cleanup/Trait 증거를
  만들어 내지 않는다. 이런 변경은 사용자가 의미를 검토해야 한다.
- actor 전송은 `enqueue_committed`에서만 sender owner를 receiver owner 또는
  shared evidence로 한 번 이전한다. 도구는 commit 전 owner나 channel 순서를
  만들어 내지 않는다.
- 디버거의 register, stack slot, machine address는 정확한 pause receipt가
  있을 때만 보이는 일시적인 정보이며 owner, root, continuation identity가
  아니다.

현재 이 계약은 설계·정적 검증 계약이다. 실제 formatter, LSP, debugger와
15개 product lane은 모두 `NOT_RUN`이다.

## 정본 근거

- ownership 문법:
  [`spec/grammar/deeplus.dpg`](../../spec/grammar/deeplus.dpg)
- place state와 type 책임:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- shared-state 계약:
  [`spec/contracts/shared-state-coherence.json`](../../spec/contracts/shared-state-coherence.json)
- actor owner 이전:
  [`spec/contracts/actor-concurrency-coherence.json`](../../spec/contracts/actor-concurrency-coherence.json)
- callable capture와 cleanup:
  [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
- nonescaping lexical dependency:
  [`spec/contracts/nonescaping-lexical-access.json`](../../spec/contracts/nonescaping-lexical-access.json)
- collection ownership Preview 경계:
  [`spec/contracts/literal-shaped-collection-design.json`](../../spec/contracts/literal-shaped-collection-design.json)
- 정본 설명과 진단:
  [`spec/language.md`](../../spec/language.md)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
<!-- IR-OWN-R8-REF-12 -->
<!-- IR-OWN-R34-LOAN-CLOSE -->
### 경로별 loan 종료

`borrow`와 `inout`의 종료는 소스에 별도 close 문장으로 쓰지 않는다.
checker가 typed use와 region 제약을 확정하면 MIR lowerer가 정상, Error,
Defect, Cancellation 및 조기 종료 경로에 명시적인 `LOAN_END`를 둔다.
하나의 정적 borrow site가 분기마다 다른 end site를 가질 수 있지만,
실행 중인 한 activation은 반드시 정확히 하나의 end만 지난다.

close frontier는 마지막 허용 사용 뒤이면서 충돌하는 mutation, move,
replacement, owner cleanup, region exit 또는 증명되지 않은 suspension보다
앞이다. 중첩 reborrow는 안쪽부터 닫으며 child가 끝난 뒤에만 parent가
다시 활성화된다. 이는 새 소스 문법이 아니라 backend가 지워도 의미를
보존해야 하는 MIR 검증 계약이다. 제품 실행 증거는 `NOT_RUN`이다.

### 일반 borrow와 문맥 증거의 책임 경계

일반 공유 borrow의 정본 철자는 `borrow`다. 이것은 MIR에서 하나의 Shared
loan을 만든다. 반면 식 `&`는 등록된 연산 문맥을 표시할 뿐 소유권,
수명, cleanup 또는 borrow 사건을 추가하지 않는다. 등록되지 않은
carrier에 `&`를 쓰면 소유권 추론 전에 거부된다.
