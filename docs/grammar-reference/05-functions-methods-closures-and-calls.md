# 함수, 메서드, 클로저, 호출

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 callable 선언, parameter channel, 함수 profile, 메서드
marker, local function, closure, lambda, 호출을 설명하는 문서 투영이다.
예제는 현행 corpus의 `accept` 및 `source_activation: none` 항목이다.
제품 parser/checker/lowering/runtime/tooling은 `NOT_RUN`이다.

## 문법

### 이름 있는 함수

```ebnf
DefIntroducer      ::= "def" HashTag*
ModuleFunctionDecl ::= TopLevelVisibility? DefIntroducer Identifier FunctionRest
LocalFunctionDecl  ::= CaptureList? DefIntroducer Identifier FunctionRest

FunctionRest       ::= TypeParameterList? ParameterList FunctionTail
FunctionTail       ::= ReturnClause? ThrowsClause* EffectsClause*
                       ContractClause* WhereClause? FunctionBody
FunctionBody       ::= "=" FunctionBodyContent
FunctionBodyContent ::= Block | ReturnShorthand | ClauseFunctionBody
ReturnShorthand    ::= "return" Expr StatementBoundary
```

이름 있는 함수의 값 본문은 block, `= return Expr`, 또는 `{{ ... }}`의
선언적 clause body다. bare `= Expr`는 이름 있는 함수 본문이 아니다.

선언 owner별 현행 profile은 닫혀 있다.

`throws`와 `effects`는 명목 선언의 반복 `conforms`와 같은 방식으로
책임 하나당 절 하나를 반복한다. 모든 `throws` 절은 모든 `effects` 절보다
앞선다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
public def loadReport(path: Path) -> Report
    throws IOError
    throws DecodeError
    effects io
    effects decode
= {
    return decodeReport(read(path))
}
```

`throws Never`와 `effects {}`는 각각 명시적 빈 ErrorSet과 EffectRow다.
`throws IOError | DecodeError`와 nonempty `effects {io, decode}`는 callable
목록 표면이 아니다. `|`와 nonempty set literal은 type-level
ErrorSet/EffectRow 대수에서만 유지된다. AST/HIR은 반복 절을 중복 없는
정규화 row로 접고, source order는 진단과 formatter에만 보존한다.

| owner | 허용 profile |
|---|---|
| 모듈 함수 | `def`, `def#async`, `def#pure`, `def#guard` |
| 진입 함수 | `def#entry`, `def#entry#async` |
| 확장 함수 | `def`, `def#async` |
| 인스턴스 메서드 | `def`, `def#mut`, `def#consume`, `def#async`, `def#pure` |
| 로컬 함수 | `def`, `def#pure`, `def#async`, `def#guard` |
| Trait 메서드 | `def`, `def#pure`, `def#async` |
| conformance 메서드 | `def`, `def#async`, `def#mut`, `def#consume`, `def#pure` |
| 정리 함수 | `def#cleanup` |

중복 profile과 owner에 없는 조합은 거부한다.

### 함수 static activation

`static { ... }`은 이름 있는 동기 함수의 실제 구현에 결합되는
Stable activation prologue다. 함수 값의 생성, 이름 조회, overload 후보
수집 또는 JIT compilation 때가 아니라, 최종 구현을 실제로 호출할 때
처음 한 번만 실행된다. 이 기능은 persistent function-local value나 cache,
module initializer, type-side `def::` 또는 top-level `static def`가 아니다.

```ebnf
FunctionBodyContent      ::= CallableBlock | ReturnShorthand | ClauseFunctionBody
CallableBlock            ::= "{" BlockPrologue?
                                  FunctionStaticActivation?
                                  BlockSequence "}"
FunctionStaticActivation ::= "static" StaticActivationBlock
StaticActivationBlock    ::= "{" BlockSequence "}"
```

`static`은 hard keyword로 승격되지 않는 callable-owned contextual
introducer다. CallableBlock의 optional `use`/`import` prologue 뒤, 첫
runtime semantic item 앞에서 Block이 이어질 때 activation으로 commit한다.
formatter는 `static { ... }`을 출력한다. activation은 이 위치에 최대
하나이며 expression body와 clause body에는 직접 붙지 않는다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/function-static-activation.json -->
```deeplus
def decode(bytes: Bytes) -> Packet = {
    static {
        verifyDecoderTables()
    }

    return decodePacket(bytes)
}
```

최초 Stable owner matrix는 다음처럼 닫혀 있다.

| owner | activation |
|---|---|
| 동기 module/extension 함수 | 허용 |
| 동기 instance/type-side member | 허용 |
| body가 있는 동기 Trait default와 explicit conformance method | 허용 |
| `def#pure` | activation body가 같은 pure proof를 통과할 때 허용 |
| entry/local function, constructor, cleanup/drop | 거부 |
| lambda, anonymous closure, actor handler/request | 거부 |
| async, generator, FFI declaration | 거부 |
| `def#guard` | 거부; guard의 total narrowing 계약과 terminal activation failure를 섞지 않음 |

정확한 once owner는 source 이름 하나가 아니라
`FunctionStaticOwnerId`다. 이 ID는 activation semantics version,
`CallableImplementationId`, 정규화한 owner/callable generic substitution,
activation body contract digest에서 결정된다. 그 digest는 body가 실제
사용하는 Witness/Conformance ID와 정적으로 선택한 helper ID 및 helper
safety digest를 정렬해 결합한다. 사용하지 않은 ambient witness나
`Context`는 ID를 나누지 않는다. overload, selected override와 서로 다른
generic specialization은 별도 owner이며, inline/LTO/JIT clone은 같은
owner state를 공유한다. runtime key는
`(RuntimeInstanceId, FunctionStaticOwnerId)`다.

호출 사건 순서는 다음과 같다.

1. 최종 callable implementation을 선택한다.
2. receiver와 explicit/default argument를 기존 규칙대로 한 번씩 평가하고
   검증하여 staging한다.
3. `EnsureFunctionStaticActivated(owner)` barrier를 통과한다.
4. parameter ownership을 0회 또는 1회 원자적으로 commit한다.
5. requires/`old(expr)`와 ordinary body로 진입한다.

activation이 실패하면 parameter ownership commit과 ordinary body 진입은
모두 0이다. caller owner는 caller에게 남고 staged argument, frame/result
reservation과 activation-local temporary는 각각 정확히 한 번 정리된다.

Activation body는 `safe`, synchronous, non-suspending, `throws Never`,
`effects {}`다. literal, compile-time constant, immutable module/type
constant, 정규화된 generic argument, activation-local temporary와
정적으로 선택된 activation-free pure helper만 사용할 수 있다. 다음은
금지한다.

- `self`, receiver, parameter, default result, caller `Context`;
- caller run/thread/actor identity, time, random, environment, locale;
- mutable global state, ambient provider/authority, dynamic witness lookup;
- I/O, FFI, actor send/request, `await`, `yield`, cancellation observation;
- Resource 획득·escape, persistent `needsDrop` residue, body 밖 control transfer;
- indirect/provider/dynamic call과 activation을 가진 다른 callable 호출.

상태 기계는 `Dormant -> Initializing -> Ready | Failed`뿐이다. 동시 첫
호출에서는 winner 하나만 activation body를 실행하고 나머지는
non-cancellable synchronous barrier에서 기다린다. `Ready`와 `Failed`는
release로 publish하고 acquire로 관찰한다. partial observation, reset,
implicit retry는 없다.

Activation body의 terminal Defect 또는 same-owner reentry는 하나의
canonical `Failed(FailureRecord)`를 만든다. winner, waiter와 이후 caller는
모두 `FUNCTION_STATIC_ACTIVATION_FAILED`를 같은 failure identity로
관찰하며, 원래 Defect 또는
`FUNCTION_STATIC_ACTIVATION_REENTRANCY`는 cause로 보존된다. reentry는
deadlock이나 undefined behavior가 아니다. 최초 Stable profile은
activation-bearing/dynamic/provider callee를 정적으로 거부하여
cross-owner activation cycle을 구성할 수 없게 한다.

Public callable metadata는 activation presence, owner recipe, semantics
version, contract/safety/dependency digest, terminal cached failure profile과
release/acquire publication profile을 보존한다. backend-local initializer
entry와 state-cell address는 public digest에 들어가지 않는다. activation을
추가·제거하거나 contract digest를 바꾸는 것은 relink가 필요한 API/link
변경이다. formatter/LSP/runtime/backend 지원은 target-bound receipt가
없으므로 여전히 `NOT_RUN`이다.

`static_once_value`, effectful/module/class activation은 별도 Preview
설계이며 이 Stable 승급으로 활성화되지 않는다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

#### Preview Design: function-static namespace

Persistent immutable slot은 Stable activation rename과 별개인
`PREVIEW_DESIGN_NONACTIVATABLE` 설계다. 다음 철자는 설계 표면일 뿐
current parser-cover grammar가 아니다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/function-static-namespace-preview-design.json -->
```deeplus
static {
    static#slot table = buildTable()
    let temp = verifyTableShape() // activation-local ordinary binding
}

let result = evaluate(borrow static#slot::table)
```

`static#slot`이 persistent slot을 명시하고 plain `let`/`var`는 기존
activation-local 의미를 유지한다. 따라서 구 activation source를
persistent storage로 blind rewrite하지 않는다.

`static#slot::name`은 nominal `Type::item`, named extension,
`<T as Trait>::item`, explicit runtime owner와 섞이지 않는 다섯 번째
closed compile-time domain 후보다. exact lexical `FunctionStaticOwnerId`의
한 `FunctionStaticSlotId`만 선택하며 fallback, runtime string lookup,
external function access, import/use/export/alias/reflection/wildcard,
bare-name fallback은 없다. lexical descendant의 참조는 stack capture가
아니라 owner/slot HIR dependency다.

M0 slot은 immutable, deterministic static-materializable, deeply
immutable/read-only Shareable, no-drop, authority/resource/escaping-borrow-free
값만 허용한다. reachable interior mutation, `SharedCell`/`SharedMutex`,
direct persistent `var`, write/compound write, exclusive borrow, move/consume,
implicit locking/atomicity는 허용하지 않는다.

Initializer는 source order로 private staging에 값을 만들며 앞서 성공한
slot만 읽을 수 있다. self/forward/cycle과 hidden topological reorder는
거부한다. initializer staged read와 ordinary Ready read는 별도 HIR/MIR
책임이다. 전체 activation이 성공한 뒤 모든 slot과 `Ready`를 한 번에
publish하고, 실패하면 역순 cleanup 뒤 slot 0개와 기존 canonical
`FUNCTION_STATIC_ACTIVATION_FAILED` identity를 publish한다.

정확한 nonactivatable 계약은
[`spec/contracts/function-static-namespace-preview-design.json`](../../spec/contracts/function-static-namespace-preview-design.json)에
있다. 이 Preview는 semantic P0와 기존 OPEN P1 집합을 바꾸지 않고 모든
제품 lane을 `NOT_RUN`으로 유지한다.

<!-- deeplus-status-fence: CURRENT -->

### 매개변수 채널

```ebnf
Parameter ::= StoredParameter
            | ContextParameter
            | WitnessParameter
            | RepeatedParameter
            | NamedRestParameter
            | ValueParameter

ValueParameter    ::= ParameterMode? ParameterEntrySlot TypeAnnotation
ParameterEntrySlot ::= Identifier IrrefutableParameterPattern?
ParameterMode     ::= "borrow" | "mut" | "move" | "inout"
ContextParameter  ::= "context" Identifier ":" TypeRef
WitnessParameter  ::= "using" Identifier ":" "witness" TypeRef
RepeatedParameter ::= Identifier "..." TypeAnnotation
NamedRestParameter ::= Identifier "***" TypeAnnotation
StoredParameter   ::= MemberVisibility? ("let" | "var") Identifier
                      TypeAnnotation?
```

일반 parameter는 call channel `Identifier`를 보존하면서 선택적으로
irrefutable structural Pattern을 body-entry plan으로 가질 수 있다.
Pattern은 overload, named-argument label, function type 또는 public ABI
identity에 참여하지 않는다. refutable Pattern은 formal에서 정적으로
거부한다. 반복 positional channel은 `values...: T`, named rest channel은
유일하고 마지막인 `options***: Record`다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/pattern-sequence-multivalue-r1.json -->
```deeplus
private def distance(point Point${x, y}: Point) -> Float = {
    return sqrt(x ^ 2 + y ^ 2)
}
```

`point`는 외부 call channel과 whole-value local이고 `Point${x, y}`는
인수 결합과 parameter ownership commit 뒤 body 진입에서 실행된다.
구조 분해 실패 가능성이 있는 동적 List는 parameter에서 직접 열지 않고
body의 guarded `let`으로 처리한다.

`mut x: T`는 callee가 소유하는 mutable local place다. argument를 한 번
얻고, affine owner라면 그 place로 이전하며, caller에 write-back alias를
남기지 않는다. 반대로 `inout x: T`는 caller의 정확한 한 place를
exclusive하게 빌리고 같은 place에 변경이 관측된다. `move x: T`는
ownership transfer를 강조하지만 그 표기만으로 mutation 권한을 새로
만들지는 않는다.

함수 type은 두 residue를 그대로 보존한다.

다음은 현행 문법을 설명하기 위한 예시다. 근거는
[`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)의
`ParenTypeSyntax`/`FunctionTypeTail`과
[`spec/types/type-system.md`](../../spec/types/type-system.md)의
named-rest residue 규칙이다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/types/type-system.md -->
```deeplus
private type Handler = (String, Int..., Record***) -> Unit
```

`***`는 parameter/type suffix이고 `**record`는 call/materialization의
named unfold prefix다. 둘은 같은 의미가 아니다.

### 메서드와 type-side 함수

```ebnf
MemberFunctionDecl ::= MemberVisibility? DefIntroducer Identifier
                       ClassDispatchMarker FunctionRest
ClassDispatchMarker ::= "." | "+" | "*." | "*+"
TypeSideMemberFunctionDecl ::= MemberVisibility? "def" "::" Identifier FunctionRest
```

class/enum instance method marker는 `.` final, `+` open, `*.` override 후
close, `*+` override 후 open이다. Trait/conformance가 같은 glyph를
사용하더라도 AST 의미 영역은 `TraitWitnessKind`로 별개다. field에는
dispatch marker가 없고 associated nonmethod에도 witness marker가 없다.

### 클로저와 lambda

```ebnf
ClosureExpr       ::= CaptureList? HashTag* "{" ClosureContent "}"
ExplicitLambdaContent ::= LambdaParameterList? "=>" LambdaBody
LambdaParameterList ::= LambdaParameter ("," LambdaParameter)* ","?
LambdaParameter   ::= ParameterMode? IrrefutableParameterPattern TypeAnnotation?

CaptureItem       ::= ("let" | "var") Identifier "=" Expr
                    | CaptureMode Identifier
                    | Identifier
CaptureMode       ::= "borrow" | "inout" | "move" | "clone"
                    | "deep" | "copy" | "once"
```

lambda parameter 목록 자체에는 바깥 괄호를 쓰지 않는다. 다만
`{ (x, y): (Int, Int) => ... }`의 괄호는 Tuple parameter 하나를
분해하고, `{ x: Int, y: Int => ... }`는 parameter 둘을 받는다. 두
형식의 call arity는 같다고 추측되지 않는다. 명시적 nullary lambda는
`{ => body }`다. 단일 expression은 로컬 결과가 되며 multiline
non-Unit 경로에는 각 정상 경로의 `ret`가 필요하다.

### 호출

일반 호출의 기본형은 `callee(arguments)`다. 괄호 없는 bounded 예외는
하나의 atomic argument 뒤에 하나 이상의 trailing closure가 이어지는
형식뿐이다. 이 예외가 일반적인 괄호 없는 인수 목록을 허용하는 것은
아니다.

```ebnf
CallSuffix ::= ArgumentList TrailingClosureGroup?
             | AtomicCallArgument TrailingClosureGroup

Argument ::= ContextArgument | WitnessArgument | NamedArgument
           | PositionalUnfoldArgument | NamedUnfoldArgument | Expr
NamedArgument            ::= Identifier ":" Expr
PositionalUnfoldArgument ::= "*" Expr
NamedUnfoldArgument      ::= "**" Expr

TrailingClosureGroup    ::= TrailingClosureArgument+
TrailingClosureArgument ::= ClosureExpr | Identifier ":" ClosureExpr
```

trailing closure가 하나이면 label을 생략하거나 쓸 수 있다. 두 개 이상이면
모든 closure에 서로 다른 label을 써야 한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
run(1) { value => consume(value) }
run(1) completion:{ value => consume(value) }

transaction()
    onCommit:{ => logCommit() }
    onRollback:{ error => log(error) }
```

두 번째 묶음에서 하나라도 label이 없거나 label이 중복되면 call shape를
만들지 않는다. label은 문자열이 아니라 선택된 함수의 visible
function-typed parameter identity다.

### 통합 호출 AST와 `~`/`:~`

ordinary, message, actor-transport 호출은 하나의 `CallExpr`와
`CallMode = Ordinary | Message | ActorMessage`로 정규화된다. 세 mode는
같은 ordered `CallArgument[0..N]` family와 trailing-closure 판정을
사용한다. message 전용 payload AST나 Tuple/Record를 parameter 목록으로
투영하는 규칙은 없다.

```ebnf
TildeCallLed ::= TildeCallToken MessageSelector
                 TildeArgumentSequence? TrailingClosureGroup?
TildeCallToken ::= "~" | ":~"
MessageSelector ::= Identifier | QualifiedMessageSelector
QualifiedMessageSelector ::= TypeRef "::" Identifier
                             ("::" Identifier)?
TildeArgumentSequence ::= TildeArgument ("," TildeArgument)*
TildeArgument ::= ContextArgument | WitnessArgument | NamedArgument
                | PositionalUnfoldArgument | NamedUnfoldArgument | Expr
```

`~`는 Stable message mode이며 왼쪽 결합한다. `:~`는 Stable
actor-transport mode이며 terminal·비결합이다. 두 표면 모두 rank 15라서
rank 10 assignment보다 강하다. 바깥 호출의 comma 뒤에 nested tilde
call을 놓으려면 그 tilde call을 괄호로 감싸 comma owner를 명확히 한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/unified-call-actor-transport.json -->
```deeplus
receiver ~ ping                         // 인수 0개
receiver ~ send ()                     // Unit 인수 1개
receiver ~ moveTo x, y                 // positional 인수 2개
receiver ~ moveTo (x, y)               // Tuple 인수 1개
receiver ~ configure base, retries: 3  // positional 1 + named 1
receiver ~ configure ${ base: base retries: 3 } // Record 인수 1개
receiver ~ SomeTrait::transform value
receiver ~ Value::text::render value
worker :~ submit move job
directory :~ find id: id
```

따라서 `receiver ~ moveTo x, y`와 `receiver ~ moveTo (x, y)`는 서로
다른 call shape다. 앞은 인수 두 개이고 뒤는 Tuple 값 하나다.
`receiver ~ ping()`을 zero-argument 호환 표기로 보존하지 않는다.
canonical zero-argument 표면은 `receiver ~ ping`이다.

prefix `await`은 tilde call보다 강하다. 따라서
`await receiver ~ fetch key`는 `(await receiver) ~ fetch key`다. call
전체의 결과를 기다리려면 반드시 `await (receiver ~ fetch key)`처럼
괄호로 owner를 고정한다. actor `:~` 자체는 suspend하거나 retry하지
않는다. request는 먼저 `Result<Reply<T>, error ActorMessageError>`에서
reply를 추출한 뒤 그 reply에 `await`을 적용한다.

## 허용과 정적 의미

- overload identity에는 parameter 순서와 label, ownership mode,
  context/witness/rest channel, effect/error row, isolation, return type가
  들어간다.
- return type이나 source order만으로 overload를 선택하지 않는다.
- 고정 arity, repeated positional, named rest 순으로 우선하며 남은 tie는
  오류다.
- named rest의 carrier는 정적 label을 가진 canonical `Record`다. runtime
  key를 가진 Map은 named argument를 만들 수 없다.
- local function은 선언 뒤부터 보인다. 증명된 비탈출·동기·same-isolation
  read-only outer use는 lexical dependency이며 CaptureList에 반복하지
  않는다. snapshot, mutation, ownership transfer, escape 또는 suspension은
  명시적 capture가 필요하다. 현행 mutual recursion은 없다.
- closure profile은 lifetime(`ordinary/#scoped`), call-right
  (`repeatable/#once`), 환경 receiver(`shared/#mut`), 동작
  (`ordinary/#pure/#guard`)와 effects/errors/isolation/suspension을
  보존한다.
- implicit `@` parameter는 overload가 정확히 1-parameter callable을
  독립적으로 선택한 경우에만 허용된다.
- `#guard`는 terminating, nonsuspending, nonconsuming pure Bool
  callable이다. 검증된 `GuardSummaryV1`과 stable actual을 가진 direct
  truth-test는 branch-local flow narrowing fact를 만든다.

호출 판정은 다음 순서를 고정한다.

1. return type을 tie-breaker로 쓰지 않고 한 declaration identity를
   선택한다.
2. actual을 positional, label, `*` repeated, `**` named unfold,
   `context`, `using` evidence channel로 분리한다.
3. generic constraint를 ordinary argument의 source order로 모아 하나의
   exact substitution을 만든다.
4. 고정 parameter의 arity를 먼저 확인한다. `*expr`은 statically known
   Tuple 또는 admitted `Sequence` residue에만 쓰며 unknown length로 fixed
   parameter를 채우지 않는다.
5. `context expr`은 선언된 context parameter 하나를 명시적으로
   공급한다. 이름을 보고 ambient lookup하지 않는다.
6. `using evidence`는 non-forgeable, borrowed, nonescaping witness를
   공급한다. ordinary runtime value로 대체할 수 없다.
7. ownership, effects, ErrorSet, cancellation, isolation, return obligation을
   확인한 뒤에만 call을 commit한다.

message/actor-message call도 같은 argument channel 판정을 그대로
적용한다. `context`와 `using` evidence는 각각 명시적 channel이며
ordinary Record field나 positional 값에서 합성하지 않는다. qualified
selector는 CST/AST에 전체 경로를 보존한 뒤 nominal, Trait, extension,
actor 또는 actor-protocol domain의 declaration identity로 해석한다.
actor `:~` domain에서는 ordinary method fallback이 없다.

lambda의 contextual shorthand `@`는 이 모든 판정이 먼저 끝나 정확히
하나의 ordinary one-value parameter가 남을 때만 생긴다. context,
witness, repeated 또는 named-rest channel이 있거나 overload가 남아
있으면 shorthand를 만들지 않는다.

## 평가·소유권·효과

호출 인자는 source order로 정확히 한 번 평가된다. positional unfold와
named unfold는 별도 channel이며 Record unfold는 정적 label source order를
보존한다.

closure capture mode는 실제 owner/borrow 책임이다. borrow capture는 region
밖으로 escape할 수 없고 inout capture는 겹칠 수 없다. move capture는
원본 owner를 이전한다. resource capture에는 모든 종료 경로를 합쳐 정확히
하나의 cleanup path가 필요하다.

나머지 capture도 이름뿐인 hint가 아니다.

- `copy`는 admitted value/bit-copy 책임을 요구하고 source를 계속 valid로
  둔다.
- `clone`은 선택된 `Clone` witness를 한 번 호출하므로 그 witness의
  effects와 errors를 그대로 노출한다.
- `deep`은 별도의 deep-copy profile을 요구하며 자식이 clone 가능해
  보인다는 이유로 재귀 복사를 추측하지 않는다.
- capture `once`는 환경 field owner를 한 번만 읽을 수 있게 한다.
  callable 자체의 `#once` profile과는 별도 축이다.

capture acquisition은 왼쪽부터 한 번씩 수행한다. 환경 publish 전에
어느 capture가 실패하면 이미 얻은 temporary를 역순으로 cleanup하고
partial closure를 외부에 노출하지 않는다.

`return`은 이름 있는 함수·메서드·handler·local function의 control
transfer다. `ret`는 lambda와 `@if/@match/@try/@scope`의 로컬 value body에만
속하며 closure boundary를 넘지 않는다.

## 현행 예제

### named rest와 펼침

현행 예제 `EX-R51a1-NEW-003`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def command(name: String, args...: String, options***: Record) -> Unit = {
    dispatch(name, *args, **options)
}
```

현행 예제 `EX-R51a1-NEW-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
private type Command = (String, String..., Record***) -> Unit
```

### lambda와 로컬 함수

현행 예제 `EX-R51a1-003`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let add = { x: Int, y: Int => x + y }
```

현행 예제 `EX-R51a1-024`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def outer(x: Int) -> Int = {
    def inner(y: Int) -> Int = {
        return x + y
    }
    return inner(1)
}
```

현행 예제 `EX-R51a1-026`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let consumeOnce = [move token] #once { value => consume(token, value) }
```

### trailing closure와 여러 callback

현행 예제 `EX-R51a1-NEW-007`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let names = users ~ map { user => user.name }
```

하나의 named trailing closure:

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
let value = transaction() completion:{ result => log(result) }
```

현행 예제 `EX-R51a1-NEW-008`처럼 여러 callback은 모두 이름을 붙여
괄호 밖에 둘 수 있다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
let value = transaction()
    onCommit:{ => logCommit() }
    onRollback:{ error => log(error) }
```

message call도 같은 규칙을 쓴다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
let outcome = worker ~ process job
    success:{ value => publish(value) }
    failure:{ error => recover(error) }
```

### 이름 있는 함수 profile

현행 예제 `EX-R51a1-NEW-017`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def#async fetch(url: String) -> Bytes
    throws NetworkError
    effects io
= {
    return await (client ~ get url)
}
```

현행 예제 `EX-R51a1-NEW-018`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def#guard validPort(port: Int) -> Bool = {
    return 0 <= port <= 65_535
}
```

## 거부되거나 격리된 형식

| 형식 | 판정 |
|---|---|
| `{ (x: Int) => x }` | 거부; lambda parameter에 목록 괄호를 쓰지 않는다 |
| refutable pattern parameter | 거부; body에서 명시적으로 구조 분해한다 |
| 이름 있는 함수의 `= expr` | 거부; block 또는 `= return expr`를 사용한다 |
| named function 안의 `ret` | 거부 |
| lambda value body 안의 `return` | 거부 |
| local function의 암시적 outer capture | 거부 |
| bare ordinary call | 거부; bounded trailing-closure 예외만 있다 |
| 둘 이상의 trailing closure 중 label 누락 | 거부; 모든 closure에 label을 쓴다 |
| trailing closure label 중복 | 거부; 각 label은 정확히 한 번만 쓴다 |
| `receiver ~ ping()`을 zero-argument message로 사용 | 거부; `receiver ~ ping`을 쓴다 |
| message/actor call을 payload aggregate로 해석 | 거부; ordinary argument channel을 그대로 사용한다 |
| actor operation에 `~` 사용 | 거부; exact actor operation은 `:~`를 사용한다 |
| named argument의 `name = value` | 거부; `name: value`를 사용한다 |
| call-side `***record` | 거부; unfold는 `**record`다 |
| ordinary `def#unsafe` | 거부; `extern#C def#unsafe`는 명시적 Preview gate의 FFI 전용이다 |

## 상호작용

- class dispatch marker와 Trait witness marker는 glyph가 같아도 의미 영역이
  다르다.
- parameter의 structural Pattern은 irrefutable body-entry plan이다.
  refutable 구조는 body의 `if let`이나 guarded let에서 처리한다.
- trailing closure는 capture, effect, error, ownership 검사를 완화하지
  않는다.
- `~` message call은 ordinary call과 별도 postfix owner이고 payload는
  0/1 aggregate지만, `TrailingClosureGroup`의 구조 검사는 공유한다.
- actor 경계를 건너는 closure는 독립적으로 transfer/capture/isolation
  검사를 통과해야 하며 trailing 표면이 그 권한을 만들지 않는다.
- `def#async`와 `await`는 suspension을 숨기지 않으며 structured `concur`
  경계를 따라야 한다.
- 함수 type의 `T...` 및 `Record***`는 public API digest와 compatibility에
  남는다.

## 정본 근거

- callable/closure 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- profile, 호출, capture 계약:
  [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
- frontend owner 정책:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 정본 설명과 진단:
  [`spec/language.md`](../../spec/language.md)
- 함수 type 책임:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
