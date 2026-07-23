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

parameter mode는 호출 경계의 책임이고 type qualifier는 normalized type
책임이다. 같은 단어를 사용해도 문법 owner와 identity field는 보존된다.

parameter `mut x: T`는 argument를 한 번 얻어 callee-owned mutable local
place에 넣는다. affine owner는 callee로 이전되고 caller에는 write-back
alias가 없다. `inout x: T`는 caller의 정확한 place를 exclusive하게
빌려 같은 place에 변경을 commit한다. `move x: T`는 transfer를 요구하되
그 자체로 mutation 권한을 만들지 않는다. type-side `mut T`는 unique
mutable owner/view 책임이며 `inout` channel의 다른 철자가 아니다.

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

capture `copy`는 admitted copy 책임, `clone`은 선택된 `Clone` witness,
`deep`은 별도 deep-copy profile을 요구한다. `clone`/`deep`이 선언하는
failure와 effect는 closure construction에 그대로 나타난다. capture
`once`는 환경 field를 한 번만 소비하게 할 뿐 callable의 `#once`
profile을 자동으로 만들지 않는다. 여러 capture는 왼쪽부터 얻고,
environment publish 전 실패하면 temporary를 역순으로 정리해 partial
closure가 escape하지 않게 한다.

### resource와 borrowed Facet

```ebnf
ClassFlavor ::= "value" | "resource"
CleanupDecl ::= DefIntroducer "(" ")" ThrowsClause? EffectsClause? FunctionBody

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

`SharedCell<T>`는 normalized Plain payload만 받는다. `withValue`는
sequentially consistent한 `#scoped borrow T` 관찰을 하나 제공하며 그
borrow는 escape/suspend할 수 없다. `replace`는 새 owner를 한 번 commit하고
이전 owner를 반환한다.

`SharedMutex<T>` 최소 프로필은 lifecycle/effectful-cleanup payload를
받지 않는다. `withLock`은 receiver-bound, non-reentrant, nonsuspending
`#scoped inout T`를 하나 제공한다. unlock은 return, Error, Defect,
Cancellation의 모든 경로에서 infallible exactly-once cleanup이다.

MIR 관찰은 API 이름만 남기지 않는다. `SharedCell`의 관찰은 같은
`sync_id`, 고유한 `operation_id`, `owner_id`, `cleanup_region_id`를 가진
`observe_begin`/`observe_end` 쌍이고, `replace` 성공은 그 사이의 단 하나
`replace_commit`이다. `SharedMutex`는 같은 식별자 묶음의
`lock_acquire`/`lock_release`를 남기며 release는 모든 terminal edge에서
정확히 한 번이다. xVM과 LLVM은 이 ordered trace와 owner/cleanup balance를
같게 보존해야 하지만, 현재는 대상 실행 확인서가 없어 `NOT_RUN`이다.

이 두 API는 표준 라이브러리 프로필이며 core source syntax가 아니다.

## 평가·소유권·효과

owner를 바꾸는 operation은 성공 commit 지점이 하나다. commit 전 실패는
원래 owner와 value state를 보존하며 성공은 새 owner에 정확히 한 번
이전한다.

borrow와 view는 owner-bounded다. owner보다 오래 살거나 owner의 move/drop,
task/actor isolation crossing을 지나서는 안 된다. suspension은 live
borrow, isolation, cleanup obligation을 지우지 않는다.

클로저(closure), generator, async suspension, actor message, Facet packaging,
`defer`, return은 escape boundary다. checker는 capture borrow의 lifetime과
resource의 exactly-one cleanup path를 증명해야 한다.

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
let outcome: OwnedDowncast<Target, Source> = value ~ downcastOwned()
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
let text = printable ~ print()
```

### 표준 라이브러리 프로필 경계

다음 corpus 항목은 syntax는 현행이지만 `source_activation: stdlib`이므로
core 언어 실행 증거로 해석하지 않는다.

`EX-R51COH-SHARED-001`:

```deeplus
let cell = SharedCell::new(move state)
let label = cell.withValue() { borrow value => describe(value) }
let previous = cell.replace(move nextState)
```

`EX-R51COH-SHARED-002`:

```deeplus
let mutex = SharedMutex::new(move state)
mutex.withLock() { inout value => value = update(value) }
```

두 예제 모두 제품 실행은 `NOT_RUN`이다.

## 거부되거나 격리된 형식

### 현행에서 거부

| 형식 또는 주장 | 판정 |
|---|---|
| move 뒤 affine source 재사용 | 거부 |
| 겹치는 `inout` access | 거부 |
| borrow/view의 region escape | 거부 |
| borrowed Facet의 suspension/task/actor crossing | 거부 |
| `Facet<T as Trait>` concrete-payload spelling | 제거됨 |
| owner를 암시적으로 `Shared<T>`로 승격 | 거부 |
| `Shareable`만으로 alias 생성 | 거부 |
| Plain에 resource/drop 책임 숨김 | 거부 |
| `SharedMutex`에 lifecycle payload 숨김 | 거부 |
| shared wrapper가 `Transferable` 자동 생성 | 거부 |

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### `PREVIEW_NONACTIVATABLE`: owned/inout Facet 검토안

`facet[inout value as Trait]`, `facet[move value as Trait]` 및 대응
`Facet<inout ...>`, `Facet<move ...>`는 Recovery가 진단을 위해 알아보는
Preview-design이다. 현행 Facet grammar는 `borrow`만 허용한다.

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
6. API/ABI, MIR, xVM/LLVM lowering identity의 일치;
7. formatter/LSP와 target-bound positive/negative 실행 증거.

문서화는 owned/inout Facet activation, `TCC-P1-002..008` closure, 구현
authority, product PASS가 아니다.

### `PREVIEW_NONACTIVATABLE`: 약한 atomic ordering

weak atomic ordering은 닫힌 memory model과 target receipt contract가 없어
source gate조차 없는 설계 제안이다. 현행 SharedCell/SharedMutex의
sequentially consistent 최소 프로필을 약화하지 않는다.

도입 전에는 operation별 ordering vocabulary, data-race 및 happens-before
법칙, failure ordering, compiler reorder 한계, xVM/LLVM parity, litmus
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
- actor message와 structured task는 owner transfer, cancellation,
  cleanup을 독립 축으로 보존한다.
- type equality는 ownership, effect, error, cancellation, suspension,
  isolation, cleanup residue를 지우지 않는다.

## 정본 근거

- ownership 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- place state와 type 책임:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- shared-state 계약:
  [`spec/contracts/shared-state-coherence.json`](../../spec/contracts/shared-state-coherence.json)
- actor owner 이전:
  [`spec/contracts/actor-concurrency-coherence.json`](../../spec/contracts/actor-concurrency-coherence.json)
- callable capture와 cleanup:
  [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
- collection ownership Preview 경계:
  [`spec/contracts/literal-shaped-collection-design.json`](../../spec/contracts/literal-shaped-collection-design.json)
- 정본 설명과 진단:
  [`spec/language.md`](../../spec/language.md)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
