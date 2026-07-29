# 제어 흐름, 오류, 효과, 정리

<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

## 상태

이 장은 현행 Deeplus의 제어 이전, loop outcome, `try`/`throw`, `Result`,
effect/error row, `defer`, lifecycle cleanup, cancellation 경계를 설명하는
문서 투영이다.

현행 예제는 `examples/guide/review-corpus.md`의
`expected_outcome: accept`, `source_activation: none` 항목을 그대로
사용한다. 설계 정적 증거만 존재하며 제품 parser/checker/HIR/MIR/xVM/
Cranelift/formatter/LSP 실행은 `NOT_RUN`이다.

> 이 장의 조각 예제에 선언 없이 나타나는 `print`는 canonical Prelude
> API가 아니라 [문서 fixture의 host adapter](../guide/example-host-adapters.md)다.

## 문법

### 제어 이전

```ebnf
ControlTransfer ::= ReturnTransfer | ThrowTransfer | BreakTransfer
                  | ContinueTransfer | YieldTransfer
ReturnTransfer   ::= "return" Expr? GuardClause?
ThrowTransfer    ::= "throw" Expr GuardClause?
BreakTransfer    ::= ("break")+ Expr? GuardClause?
ContinueTransfer ::= ("break")* "continue" GuardClause?
YieldTransfer    ::= "yield" Expr? (GuardClause | YieldResponseBinding)?
```

`return`은 이름 있는 callable의 control owner다. lambda와 value body의
로컬 결과는 `ret`가 소유한다. `break`를 반복한 chain은 바깥 loop를
구조적으로 가리키며 label/depth 표기는 현행 Stable 형식이 아니다.

loop 뒤 subjectless `match`는 직전 loop가 제공한 outcome을 소비한다.
정상 완료는 `::completed`, break는 payload가 없어도 `::break(())`다.

### 오류, 효과, Result

```ebnf
ThrowsClause ::= "throws" ErrorSetTerm
EffectsClause ::= "effects" CallableEffectTerm
CallableEffectTerm ::= Identifier | QualifiedTypeReference | EmptyEffectSet
EmptyEffectSet ::= "{" "}"
ErrorSet      ::= ErrorSetTerm ("|" ErrorSetTerm)*
EffectRow     ::= EffectRowTerm ("|" EffectRowTerm)*
EffectSetLiteral ::= "{" IdentifierList? "}"
```

`throws E`는 callable의 recoverable error channel이고
`effects io` 같은 row는 observable effect 책임이다. `Result<T, error E>`
는 값 안의 명시적 success/error alternatives다. 한 operation이 같은
recoverable error family를 `Result`와 `throws` 양쪽에 중복 노출하면
거부한다.

여러 책임은 comma나 하나의 set literal로 모으지 않고 절을 반복한다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/contracts/type-flow-callable-coherence.json -->
```deeplus
def transfer(request: Request) -> Receipt
    throws NetworkError
    throws DecodeError
    effects network
    effects audit
= {
    return sendAndRecord(request)
}
```

선언에서는 모든 `throws`가 먼저, 모든 `effects`가 뒤에 온다.
`throws Never`와 `effects {}`만 명시적 빈 row를 나타낸다. 반면 generic
constraint나 row 계산 같은 type-level 위치에서는 `E1 | E2`,
`Eff | {state, io}` 대수가 그대로 유지된다. 반복 절은 정규화될 때
중복 없는 ErrorSet/EffectRow 하나로 결합되며, 같은 term을 두 번 적으면
거부한다.

Error, Defect, Cancellation, suspension은 별도 축이다. Cancellation은
`ErrorSet` member가 아니고 suspension은 `EffectRow` 안에 숨지 않는다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### 비활성 Preview 설계: 빈 `throws`/`effects` 절 생략

이 절은
[`concise-throws-effects-preview-design.json`](../../spec/contracts/concise-throws-effects-preview-design.json)의
`PREVIEW_DESIGN_NONACTIVATABLE` 투영이다. 현행 Stable 의미를 바꾸지 않으며
source activation, compiler 지원, conformance 증거가 없다. 특히 현행
`private_error_set_inference`는 그대로 `STABLE_DESIGN`이다. 따라서 아래
생략 법칙을 현재 프로그램에 적용하거나, 현행 private/local 추론이
사라졌다고 해석하면 안 된다.

Preview 설계가 장래 활성화될 경우 clause를 문법적으로 소유하는 callable은
다음 닫힌 선언으로 정규화된다.

```text
omitted throws  => throws Never
omitted effects => effects {}

normalize(body error residual)  subset_of normalize(declared ErrorSet)
normalize(body effect residual) subset_of normalize(declared EffectRow)
```

body가 선언을 넓히는 추론은 없다. `throws _`, `throws auto`, `effects _`,
`effects auto` 같은 placeholder도 도입하지 않는다.

| owner | 생략 정규화 | 추가 Preview 법칙 |
|---|---|---|
| module/entry/extension/local/member/Trait-default/conformance/extension-set 함수 | `Never`, `{}` | body residual은 선언 row의 부분집합 |
| constructor와 cleanup | `Never`, `{}` | 기존 delegation과 cleanup failure 법칙 유지 |
| bodyless Trait method/associated function | `Never`, `{}` | 정규화 row가 requirement |
| actor `on`/`request` | `Never`, `{}` | mailbox·cancellation·suspension·isolation은 별도 축 |
| bodyless actor protocol send/request | `Never`, `{}` | 정규화 row가 protocol requirement |
| function type | `Never`, `{}` | 정규화 row가 semantic type identity에 포함 |
| gated FFI declaration | `Never`, `{}` | 기존 FFI gate와 unsafe profile을 별도로 요구 |

lambda/capture lambda, accessor, typestate transition에는 해당 clause 문법이
없으므로 이 기본값을 적용하지 않는다. `#pure`와 `#guard`는 빈 row 외에도
기존 suspension, authority, mutation, ownership, capture 제약을 계속
요구한다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/concise-throws-effects-preview-design.json -->
```deeplus
private def magnitudeSquared(x: Int, y: Int) -> Int = {
    return x * x + y * y
}
```

Preview에서 위 서명은 `throws Never effects {}`와 동일하게 정규화된다.
반대로 nonempty 책임은 계속 양수로 적는다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/concise-throws-effects-preview-design.json -->
```deeplus
def load(path: String, context files: FileIO) -> Bytes
    throws IOError
    effects io
= {
    return readFile(path, context files)
}
```

CST는 사용자가 절을 적었는지 보존하지만 AST/HIR/API digest/MIR은 완전히
정규화된 row만 본다. 따라서 생략과 명시적 빈 row는 semantic callable
identity와 API digest가 같다. 이 동일성은 모든 호환성 관계를 하나의
규칙으로 바꾸지 않는다.

- Trait witness는 requirement보다 좁거나 같은 error/effect row를 허용한다.
- class override는 기존 exact responsibility-profile 일치를 유지한다.
- function value는 기존 variance와 row subsumption을 유지한다.
- responsibility profile 차이만으로 overload slot을 나눌 수 없다.

Stable 승격 전에는 `private_error_set_inference` supersession, 기존
private/local source에 추론 결과를 명시적 `throws`로 삽입하는 migrator,
digest 동치와 deterministic diagnostic fixture, 제품 receipt가 모두
필요하다. 현재 수치는 semantic P0 `0`, OPEN feature P1 `22`, 제품 lane
`15/15 NOT_RUN`이다.

<!-- deeplus-status-fence: CURRENT -->

이 네 축에 더해 named capability는 효과를 **설명**하는 row와 그 효과를
수행할 **권한**을 구분한다.

```ebnf
NamedEffectCapabilityDecl ::= TopLevelVisibility?
    "capability" Identifier "for" EffectRow StatementBoundary
```

`capability FileIO for {io}`는 nominal non-value capability identity 하나를
선언할 뿐 global value나 권한을 생성하지 않는다. 필요한 callable은
`context` parameter로 capability를 명시적으로 받고 동시에 실제
`effects` row를 선언한다. effect 이름이 보인다는 이유로 capability를
forge하거나 ambient하게 찾을 수 없다.

<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; authority-source: spec/language.md -->
```deeplus
public capability FileIO for {io}

def load(path: String, context fileIO: FileIO) -> Bytes
    throws IOError
    effects io
= {
    return readFile(path, context fileIO)
}
```

위 함수는 `effects io`만 선언하거나 ordinary `FileIO` value를 넘겨
권위를 대체할 수 없다. 반대로 capability를 갖고 있다는 사실만으로
호출이 실제 `io` effect를 수행했다고 간주하지도 않는다.

### try, catch, finally 구문

```ebnf
TryStmt ::= "try" Block
            (CatchClause+ FinallyClause? | FinallyClause)
CatchClause   ::= "catch" Pattern? GuardClause? Block
FinallyClause ::= "finally" Block

AtTryExpr ::= "@" "try" ValueBody
              (ValueCatchClause+ FinallyClause? | FinallyClause)
```

statement `try`는 적어도 하나의 `catch` 또는 `finally`를 가져야 한다.
catch는 recoverable Error subject를 한 번 평가하고 source order의
refutable Pattern과 optional pure guard를 시험한다. 첫 성공 catch만
binding을 commit한다. value `@try`는 모든 정상 경로의 값 type을 join하고
`finally` 자체는 값을 생산하지 않는다. 처리되지 않은 Error는
`finally` 뒤 전파된다.

### defer와 lifecycle cleanup

```ebnf
DeferStmt ::= "defer" DeferredCleanupInvocation StatementBoundary
DeferredCleanupInvocation ::= DeferredDirectCall | DeferredMessageCall
DeferredDirectCall  ::= DeferredReceiver ArgumentList
DeferredMessageCall ::= DeferredReceiver "~" MessageSelector
                        TildeArgumentSequence?

CleanupDecl ::= DefIntroducer "(" ")" ThrowsClause* EffectsClause* FunctionBody
```

`defer`는 direct/member/type-side/message cleanup invocation 하나만
등록한다. block, trailing closure, inline callable, `await`, `spawn`,
guard를 cleanup invocation으로 암시 변환하지 않는다. message cleanup도
일반 message와 같은 ordered argument channel을 사용하지만, cleanup
등록에는 `TrailingClosureGroup`을 허용하지 않는다. actor `:~`는
admission `Result`를 버릴 수 있으므로 `defer`에 등록할 수 없다.

## 허용과 정적 의미

- non-Unit named callable의 모든 정상 경로는 명시적으로 값을
  `return`해야 한다.
- `Unit` 함수의 마지막 valueless `return`은 생략하는 것이 canonical이다.
  조기 `return`은 여전히 의미가 있다.
- `#pure`는 `throws Never`, `effects {}`이고 suspension, authority,
  mutable/resource capture가 없어야 한다.
- `#guard`는 terminating, nonsuspending, nonconsuming pure Bool이다.
- `catch` header는 binder, wildcard와 refutable variant/value/transparent
  product Pattern을 허용한다. 구조 또는 guard 실패는 부분 binding이나
  move 없이 다음 catch로 진행한다.
- catch guard는 pure Bool, nonthrowing, nonsuspending이며 probe binder를
  consume, escape, mutate-through하거나 authority 획득에 사용할 수 없다.
- 한 catch가 남은 ErrorSet 전체에 irrefutable이면 뒤의 catch는
  unreachable이다. Defect와 Cancellation은 어떤 catch residual에도
  들어오지 않는다.
- `try`의 branch type, place/ownership state, effect/error row, isolation,
  cleanup state가 join 지점에서 호환되어야 한다.
- `defer` 등록 대상은 정확히 하나이며 정상 return, Error, Defect,
  Cancellation을 포함한 모든 terminal path에서 실행한다.
- throwing cleanup은 body failure를 primary로 보존하고 cleanup failure를
  실제 deterministic LIFO 실행 순서로 suppressed list에 추가한다.

## 평가·소유권·효과

expression과 argument는 정본이 별도 short-circuit를 정하지 않는 한
왼쪽부터 평가한다. pattern binding은 transactional이며 실패 시 binding,
partial move가 없다. branch cleanup은 join 또는 exit 전에 완료된다.

`defer`는 등록 역순의 deterministic LIFO로 정확히 한 번 실행된다.
`return`, `break`, `continue`, `throw`, suspension, cancellation은 필요한
cleanup을 건너뛸 수 없다. suspension은 live ownership, borrow, isolation,
cleanup obligation을 그대로 보존한다.

Cancellation은 cooperative boundary에서만 관측하며 Error로 바꾸거나
버리지 않는다. `concur`는 owned child가 terminal이 되고
required cleanup이 끝난 뒤에만 종료한다.

## 현행 예제

### Unit fallthrough와 조기 return

현행 예제 `EX-R49C-RETURN-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def announce() -> Unit
    throws Never
    effects io
= {
    print("ready")
}
```

현행 예제 `EX-R49C-RETURN-002`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def validate(x: Int) -> Unit
= {
    if x < 0 {
        return
    }
    audit(x)
}
```

### Result와 throws의 분리

현행 예제 `EX-R51a1-060`,
원본 `examples/guide/review-corpus.md`:

```deeplus
def decode(bytes: Bytes) -> Result<Image, error DecodeError>
    throws IOError
    effects io
= {
    return parseImage(bytes)
}
```

### loop outcome

현행 예제 `EX-R48C-079`,
원본 `examples/guide/review-corpus.md`:

```deeplus
for x in xs {
    if x == 0 {
        break 1
    }
}
match {
    ::break(v) => print(v)
    ::completed => ()
}
```

### defer와 cleanup declaration

현행 예제 `EX-R51a1-DEFER-001`,
원본 `examples/guide/review-corpus.md`:

```deeplus
let handle = open(path)
defer handle ~ close
process(handle)
```

현행 예제 `EX-R51a1-NEW-020`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public resource class File {
    def#cleanup()
        throws CloseError
        effects io
    = {
        closeHandle()
    }
}
```

### finally와 cancellation boundary

현행 예제 `EX-R51f3-COH-004`,
원본 `examples/guide/review-corpus.md`:

```deeplus
try {
    perform()
} finally {
    close()
}
```

현행 예제 `EX-R51f3-COH-011`,
원본 `examples/guide/review-corpus.md`:

```deeplus
public def#async supervise() -> Unit = {
    concur {
        defer cleanup()
        let child = spawn { => await work() }
        await child
    }
}
```

## 거부되거나 격리된 형식

### 현행에서 거부

| 형식 또는 주장 | 판정 |
|---|---|
| handler/finally가 없는 bare statement `try` | 거부 |
| `defer await ...`, `defer spawn ...` | 거부 |
| named function의 `ret` | 거부 |
| lambda value body의 `return` | 거부 |
| non-Unit 정상 경로의 암시적 반환 | 거부 |
| 같은 recoverable error를 `Result`와 `throws`에 중복 | 거부 |
| Cancellation을 Error로 catch/변환 | 거부 |
| cleanup failure가 body failure를 덮어씀 | 거부 |
| loop label/depth break를 Stable 표기로 사용 | 거부; break-chain 사용 |

<!-- deeplus-status-fence: PREVIEW_GATED -->

### 명시적 Preview gate

FFI는 current core가 아니다. corpus `EX-R48-026`처럼 source root 첫머리의
명시적 gate가 있는 Preview에서만 `accept_with_gate`다.

```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

이 문서화는 FFI의 ABI, unsafe lowering, target 실행을 증명하지 않으며
제품 상태는 `NOT_RUN`이다.

<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->

### `PREVIEW_NONACTIVATABLE`: dynamic/unsafe 격리 영역

`@scope#dynamic`과 `@scope#unsafe` quarantine은 보존된 nonactivatable
Preview Design이다. 현행 AST/HIR/MIR source surface가 아니다.

검토 중인 최소 의미는 typed immutable export 하나, outer mutation 금지,
suspension 금지, pointer/authority/borrow/resource/closure/run/actor escape
금지, xVM과 Cranelift에서 하나의 Deeplus MIR 의미 보존이다.

도입 전에는 다음 guard가 모두 닫혀야 한다.

1. provenance와 activation authority;
2. export type 및 ownership closure;
3. escape/alias/cleanup 증명;
4. 효과·오류·Cancellation 격리 법칙;
5. xVM/Cranelift backend equivalence와 target-bound 실행 증거;
6. formatter/LSP 및 negative admission 검증.

비활성 설명용 예시는 다음과 같으며 현재 source로 사용하면
`QUARANTINE_SCOPE_NOT_ACTIVATABLE`이다.

<!-- deeplus-example: illustrative; status: PREVIEW_NONACTIVATABLE; authority-source: spec/contracts/quarantine-scope.json -->
```deeplus
@scope#dynamic {
    legacyCall()
} -> $result: PlainResult
```

이 항목을 Reference에 기록하는 행위는 activation, P1 closure,
implementation authority, product PASS가 아니다.

<!-- deeplus-status-fence: CURRENT -->

## 상호작용

- Pattern `else`/`catch`의 atomic commit은
  [패턴, 구조 분해, 매칭](10-patterns-destructuring-and-matching.md)을
  따른다.
- callable profile과 `return`/`ret` 경계는
  [함수, 메서드, 클로저, 호출](05-functions-methods-closures-and-calls.md)을
  따른다.
- resource owner와 borrow 책임은
  [소유권, 대여, 책임](12-ownership-borrowing-and-responsibility.md)을
  따른다.
- actor send/request와 run cancellation은 enqueue commit 전후의 owner를
  구분하며 later cancellation이 committed message를 되돌리지 않는다.
- ErrorSet, EffectRow, Cancellation, suspension, cleanup은 callable
  compatibility와 public API digest에서 독립적으로 보존된다.

## 정본 근거

- 제어·try·defer 문법:
  [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- callable flow와 cleanup:
  [`spec/contracts/type-flow-callable-coherence.json`](../../spec/contracts/type-flow-callable-coherence.json)
- actor/run 취소:
  [`spec/contracts/actor-concurrency-coherence.json`](../../spec/contracts/actor-concurrency-coherence.json)
- type/effect/error 책임:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- MIR failure와 cleanup:
  [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- 정본 설명과 진단:
  [`spec/language.md`](../../spec/language.md)
- 예제 원본:
  [`examples/guide/review-corpus.md`](../../examples/guide/review-corpus.md)
