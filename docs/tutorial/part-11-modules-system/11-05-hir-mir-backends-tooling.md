# 11-05 — HIR-H1, MIR, xVM/Cranelift와 tooling evidence

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`

HIR-H1 verifier boundary(검증기 경계)는 current Stable design이다.
DP-RFC-0002의 concrete
implementation proposal과 MIR-X1 xVM-only RFC는 noncanonical/
nonactivatable draft다. compiler/backend/tooling 제품은 `15/15 NOT_RUN`이다.

## 2. 학습 목표

- scanner/CST/AST/HIR-H1/MIR/backend 단계의 책임을 구분한다.
- HIR-H1이 open lookup을 닫는 verifier boundary임을 이해한다.
- semantic identity와 backend representation을 분리한다.
- static artifact integrity와 target execution receipt를 구분한다.

## 3. 선수 지식

name resolution, typed responsibility, API digest, ownership/effect semantics를
알고 있어야 한다.

## 4. 문제에서 출발하기

source가 parse되었다는 사실만으로 실행 의미가 닫힌 것은 아니다. 이름,
conformance, ownership, effect/error, cleanup, source provenance가
결정되어야 하고 MIR lowering이 이를 다시 추측해서는 안 된다.

## 5. 핵심 모델

1. scanner(스캐너)/lossless CST(손실 없는 구체 구문 트리): token,
   trivia, attachment 보존.
2. AST(추상 구문 트리): admitted structural owner.
3. HIR-H1(고수준 중간 표현 H1): resolved identity와 typed
   responsibility를 닫고 verifier(검증기) 통과.
4. MIR(중간 표현): 관찰 가능한 평가/commit/failure/cleanup event.
5. xVM/Cranelift backend(후단): 같은 Deeplus MIR observation을 보존.

capability receipt가 없는 HIR unit은 canonical source design일 수 있어도
executable unit으로 넘어가지 않는다. MIR은 provider/witness/member lookup을
다시 수행하지 않는다.

## 6. 단계별 예제

Rational/Complex constants와 closed power plan은 HIR에 exact residue를
남긴다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let ratio = <6/8>
let z = 3.0 + 4.0i
let powered = z ^ 2
```

HIR-H1은 Rational normalized pair, Complex Rep, power operand/result domain,
adaptation plan을 고정한다. expected result나 runtime lookup이 operator를
다시 고르지 않는다.

ownership/effect source도 commit plan을 남긴다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def update(inout value: Counter, delta: Int) -> Unit
= {
    value.count += delta
}
```

MIR은 target place/read/right operand/final write 순서를 보존하고 failure
전 original owner/value를 지켜야 한다.

### R4: resolver seal과 module initialization

R4 resolver가 닫는 것은 noncall `ResolvedRef`, name/import trace,
visibility proof다. callable 후보는 `ResolvedOverloadSetRef`로 analysis
HIR에만 남을 수 있다. exact overload winner와 complete generic
substitution 전에는 canonical HIR나 MIR로 갈 수 없다.

`ResolverScopeId`, `ImportBindingId`, `SourceOriginId`,
`ActivationOriginId`는 typed compile-time identity다. absolute path, span,
timestamp, source/import order를 identity로 쓰지 않는다. MIR는 이
identity로 이름 검색을 다시 하지 않고 이미 선택된 target만 소비한다.

immutable module static value graph는 compile time에 모두 성공한 뒤
atomic commit하고 runtime initializer를 0개 만든다. cycle, stale
dependency receipt, incomplete resolver seal은 admitted HIR/MIR를 만들지
않는다.

모듈 hash 하나가 모든 책임을 겸하지 않는다. interface hash는 외부에
보이는 semantic API만 나타내고, implementation hash는 그 interface와
비공개 HIR 의미를 함께 나타낸다. full compilation receipt는 source
provenance와 package/resolver graph, dependency, visibility,
initialization, interface, implementation 관계를 재현 가능하게 닫는다.
따라서 private helper의 구현만 바뀌면 interface hash는 그대로일 수
있지만 implementation과 full receipt는 바뀐다. 반대로 source path나
trivia는 public interface identity가 아니며, script는 importable
interface를 만들지 않는다.

## 7. 허용·거부·경계 사례

허용: statically selected Trait associated function.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let decoded = <Packet as TextDecodable>::decode(text)
```

거부되는 lowering: MIR에서 `Packet::decode` 문자열을 보고 Trait/provider
registry를 다시 검색한다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let decoded = Packet::decode(text)
// Trait associated static은 explicit qualification이 필요하다.
```

xVM initial, Cranelift `ObjectModule` AOT, Cranelift `JITModule`은 current
backend authority에 함께 남는다. MIR-X1 draft 문서가 xVM-only
architecture를 제안했다는 사실은 current backend set을 바꾸지 않는다.

두 Cranelift 경로는 별도 언어 의미를 갖지 않는다. 검증된 같은 MIR을
한 번 CLIF로 낮춘 다음 `ObjectModule`은 relocatable object를, `JITModule`은
process memory의 code/data를 finalize한다. object path는 object bytes,
linker와 최종 artifact를 기록하고, JIT path는 import allowlist, resolved
import map, executable-memory policy와 image lifetime을 기록한다.

target triple, ISA settings, Cranelift version, module kind, calling convention,
runtime ABI와 optimization 설정이 하나라도 빠지면 target receipt가 아니다.
Error나 Cancellation을 host exception으로 바꾸거나 cleanup을 unwinder에
맡기는 것도 허용되지 않는다. 이들은 MIR의 명시적 edge와 ordered action
그대로 남아야 한다.

또한 CLIF value, block, stack slot, signature, register와 machine address는
Deeplus semantic identity가 아니다. managed reference가 live인 site에서
필요한 root-map/stack-map capability가 없다면 backend는 raw pointer로
우회하지 않고 lowering을 중단한다.

최초 memory profile은
`STW_NONMOVING_TRACING_WITH_OPAQUE_STABLE_HANDLES_R1`이다. xVM과 Cranelift는
같은 논리적 root map을 소비하지만 실제 VM slot, native stack slot과 register
배치는 서로 달라도 된다. 중요한 것은 주소가 아니라 어떤 live storage가
어느 owner의 root인지, suspension 때 root가 continuation으로 한 번만
이전되는지, cleanup과 최종 outcome이 같은지이다.

예를 들어 call 직전에 두 지역 변수가 같은 managed handle을 담고 있다면
root는 객체 하나가 아니라 지역 저장 위치 두 개다. compiler는 두 root를
shadow-root frame에 게시한 뒤 call에 들어가며, call outcome이 commit될 때까지
receipt를 유지한다. 반대로 managed object 내부를 잠시 가리키는 native
address는 no-collect 구간 안에서만 사용할 수 있고 call, safepoint,
suspension, actor boundary 또는 FFI를 넘어갈 수 없다. suspension root
transfer와 native projection은 통합된 `IR-OWN-P0-017` interface digest를
결합해야 하므로, 그 digest가 없는 설계 후보는 정본 승격 대상이 아니다.

이 프로파일은 moving/concurrent GC, weak reference, finalizer, pinning을
지원한다고 주장하지 않는다. collector가 `def#cleanup` 또는 cancellation을
대신 실행하는 것도 허용하지 않는다. 이러한 기능은 별도 설계 authority와
실행 증거가 생기기 전까지 닫혀 있다.
내부 runtime 호출도 같은 원칙을 따른다. Deeplus는
`DEEPLUS_INTERNAL_RUNTIME_ABI_R1` 하나를 logical contract로 두고 xVM,
Object AOT, JIT가 각각 target projection을 만든다. primitive scalar는
direct channel로 전달할 수 있지만 Tuple, Record, Enum, Option, Result,
class value, closure, collection, Rational, Complex 같은 값은 typed indirect
slot을 사용한다. aggregate result는 caller-owned normal sret slot에만
쓴다. 한 필드짜리 aggregate라고 해서 target 편의에 따라 scalar로
바꾸지 않는다.

fallible runtime call을 생각해 보자. caller는 Normal, Error, Defect,
Cancellation용 서로 다른 slot을 준비한다. dispatcher 결과가
`COMPLETE(tag)`이면 네 tag 중 정확히 하나만 반환한다. 예를 들어 `ERROR`
tag와 Error slot이 함께 commit되면
Normal/Defect/Cancellation slot은 초기화되지 않는다. `ERROR`를 host
exception으로 던지거나 Cancellation을 Error slot에 넣는 구현은
`RUNTIME_ABI_OUTCOME_TRANSPORT_INVALID` 또는
`RUNTIME_ABI_HOST_UNWIND_FORBIDDEN`으로 실행 전에 거부된다.

ownership도 ABI가 새로 해석하지 않는다. argument를 왼쪽에서 오른쪽으로
한 번 평가하고 모든 digest, helper signature, slot, root 조건을 검증한
뒤 callee entry 직전에 ownership을 한 번 commit한다. 그 전의 실패는
caller owner를 보존하지만 entry 뒤 Error나 Cancellation은 이미 넘긴
owner를 되돌리지 않는다. cleanup과 loan 종료는 MIR의 명시적 edge가
담당한다.

반면 `PARKED(receipt)`는 다섯 번째 outcome이 아니다. outcome tag와 slot을
commit하지 않고 owner, loan, cleanup token, root의 정확한 상태를
continuation receipt에 한 번 넘긴다. exact continuation ABI digest가 결속된
현재 설계에서는 suspension helper 여섯 개가 22개 base allowlist에 포함된다.
세 managed-memory helper까지 조건부로 admit되어 active helper는 25개이며,
어느 dependency digest라도 없거나 stale이면 해당 경로는 fail-closed한다.
function static 초기화, lazy force와 scoped mutex acquire가 host thread를
기다리게 할 수 있어도 그것은 Deeplus suspension이 아니므로 COMPLETE-only다.

JIT는 helper 이름이 우연히 맞는다고 호출하지 않는다. exact
`RuntimeHelperId`, signature digest, provider map과 image generation을
allowlist receipt에 묶는다. image는 먼저 publish를 해제하고 active call과
suspended continuation lease가 모두 0이 된 뒤에만 retire할 수 있다.
이 설명은 design-static 계약이며 실제 xVM/native 실행은 여전히
`NOT_RUN`이다.

## 8. 다른 기능과의 연결

- diagnostics는 rejected source에 MIR residue가 생기지 않게 한다.
- public API digest는 semantic identity이지 native ABI bytes가 아니다.
- formatter/LSP는 parse/declaration identity와 trivia를 보존해야 한다.
- source archive/hash parity는 integrity evidence이며 semantic/runtime
  execution evidence가 아니다.

### 판정 추적

source는 scanner/CST에서 spelling과 attachment를 보존하고 AST에서
구조 owner를 얻는다. resolver/checker가 exact declaration, Trait witness,
call responsibility, ownership, ErrorSet/effect와 source provenance를
HIR-H1에 고정한다. verifier가 open lookup과 책임 누락이 0임을 확인한
뒤에만 MIR lowering이 evaluation, commit, failure와 cleanup event를
만든다. backend는 이 event를 target representation으로 옮기되 의미를
다시 선택하지 않는다.

동시성 lowering에서는 happens-before(선행-후행 보장) edge도 같은
방식으로 남긴다. child cleanup이 await resume보다 앞선다는 edge는 MIR
observation이지만, 독립 child 사이의 전체 순서는 만들지 않는다.
xVM과 Cranelift parity 검증은 stdout 문자열만이 아니라 owner transition,
primary/suppressed failure, cleanup과 이 edge를 비교해야 한다.

### 흔한 오해와 미니 사례

HIR JSON이 parse되고 digest가 맞으면 executable이라는 생각은 틀리다.
artifact integrity는 bytes와 provenance를 확인할 뿐 verifier receipt,
backend build, target execution을 대신하지 않는다. MIR-X1 draft가
xVM-only를 제안했다는 사실도 current xVM+Cranelift backend authority를
자동 supersede하지 않는다.

미니 사례로 `<6/8>`은 HIR에서 normalized Rational identity를 갖고,
`z ^ 2`는 selected power plan을 갖는다. MIR이 target에 따라 다시
floating approximation을 고르거나 expected result를 보고 overload를
바꾸면 authority drift다. backend 표현이 달라도 exact numeric 결과와
failure/cleanup 관찰은 같아야 한다.

### 단계별 책임 질문

각 단계에는 “무엇을 새로 결정하는가?”와 “무엇을 다시 결정하면 안
되는가?”를 한 쌍으로 적는다. CST는 spelling을 보존하지만 type을
선택하지 않고, HIR-H1은 type/witness를 닫지만 실행 순서를 target별로
바꾸지 않으며, MIR은 event order를 구체화하지만 name lookup을 반복하지
않는다. backend는 representation을 선택하지만 semantic identity를
재해석하지 않는다.

R4에서는 추가로 묻는다.

1. exact namespace/spelling의 first nonempty frame에서 멈췄는가.
2. import binding key와 resolved target을 분리했는가.
3. `NameEnv`, `ActivationEnv`, `WitnessVisibilityEnv`를 섞지 않았는가.
4. callable candidate set이 analysis HIR 밖으로 새지 않았는가.
5. module static value가 runtime initializer로 변하지 않았는가.
6. source/import/link order가 winner가 되지 않았는가.

evidence 표에도 범위를 적는다. source/hash 검사는 bytes identity,
HIR-H1 receipt는 closed typed responsibility, MIR verifier는 event
invariant, backend parity는 target별 observable equivalence를 증명한다.
한 receipt의 PASS를 다음 열로 복사하지 않는다. 특히 formatter/LSP
round-trip은 spelling·attachment 보존 evidence이지 type checker나
runtime 동작 evidence가 아니다.

검증 실패가 나면 결정 owner가 있는 앞 단계로 되돌리고, backend가
임의 fallback으로 의미를 완성하게 하지 않는다.

## 9. Deeplus다운 작성 관례

각 단계가 무엇을 새로 결정하고 무엇을 절대 재결정하지 않는지 기록한다.
“파일이 있다”, “JSON이 parse된다”, “Cargo scaffold가 빌드된다”를 language
execution PASS로 표현하지 않는다.

## 10. 연습 문제

1. **따라 하기:** 한 call의 source→AST→HIR-H1→MIR identity를 표로 적어라.
2. **빈칸 완성:** open lookup이 끝나야 하는 단계와 observable event가
   시작되는 단계를 채워라.
3. **스스로 설계하기:** xVM/Cranelift parity test가 stdout 외에 비교해야 할
   ownership/failure/cleanup event를 설계하라.

## 11. 빠른 복습

- HIR-H1은 resolved typed verifier boundary다.
- MIR은 open-ended lookup을 반복하지 않는다.
- backend는 같은 observable semantics를 보존한다.
- current design과 draft implementation RFC를 분리한다.

## 12. 정본 근거와 다음 장

- [evaluation/HIR/MIR/backend](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [HIR-H1 contract](../../../spec/contracts/hir-h1-current-mir-bridge.json)
- [Cranelift backend contract](../../../spec/contracts/cranelift-backend-current.json)
- [MIR semantics](../../../spec/mir/semantics.md)
- [DP-RFC-0001](../../../rfcs/DP-RFC-0001-xvm-only-mir.md)
- [DP-RFC-0002](../../../rfcs/DP-RFC-0002-current-hir-h1.md)

이제 Module/API/adapter를 한 library package 설계로 묶는다.

## 13. 소유권 오류를 도구가 설명하는 방법

다음 코드는 `file`의 owner를 `saved`로 옮긴 뒤 원래 place를 다시
사용하려는 예다.

```deeplus
let file = openFile("notes.txt")?
let saved = move file
file.write("late")
```

checker가 이 사용을 거부하면 도구는 마지막 호출을 primary 위치로,
`move file`을 이전 transfer 위치로, 최초 선언을 owner 선언 위치로 보여
준다. 포매터는 `move`를 지우거나 위치를 바꾸지 않는다. LSP는 자동으로
`clone`, `share` 또는 다른 owner를 삽입하지 않는다. 그러한 수정은 새로운
권한이나 수명·cleanup 의미를 만들 수 있기 때문이다.

디버거에서는 같은 owner가 backend마다 서로 다른 register나 stack slot에
있을 수 있다. Deeplus는 그 기계 위치를 owner identity로 사용하지 않는다.
값이 최적화로 사라졌다면 `OPTIMIZED_OUT`으로 표시하며 임의의 값을 만들지
않는다. paused runtime 값은 runtime instance, execution, activation frame,
pause epoch와 정확한 debug receipt가 모두 맞을 때만 표시한다.

actor message의 owner도 도구가 옮기는 것이 아니다. commit 전이나 거부된
send에서는 sender가 owner를 유지하고, `enqueue_committed`에서만 한 번
receiver owner 또는 shared evidence로 전이한다. 이때의 sequence는 해당
channel 안에서만 의미가 있다. 이 규칙은 설계 계약이며 실제
formatter/LSP/debugger 지원은 아직 `NOT_RUN`이다.

## 14. Current machine-contract checkpoint

<!-- R10-HIR-MIR-MACHINE-CONTRACT -->

The current Stable-design handoff is:

```text
Verified<CanonicalHirH1>
  -> recompute MirCapabilityReceiptR1
  -> ExecutableHirH1
  -> deterministic lowering
  -> Verified<DeeplusMirR1>
```

Remember the failure boundary: missing capability evidence does not make the
verified HIR invalid. It preserves `Verified<CanonicalHirH1>` and prevents only
`ExecutableHirH1`. The machine registries are design authorities, not proof
that a compiler or backend implements them.

The useful audit numbers are 128 HIR identities, 102 Current lowering rows,
111 at the explicit-Preview maximum, 48 MIR operations, 17 terminators, 12
linear token kinds, 11 responsibility axes, and 26 design capabilities.
`ProposedMirX1` is still compatibility-only, and all 15 product lanes remain
`NOT_RUN`.
