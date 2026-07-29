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
