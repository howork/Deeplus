# Design Deeplus Cranelift Backend Adoption R1

## 1. 판정

`ACCEPT_CURRENT_BACKEND_REPLACEMENT_WITH_EVIDENCE_GUARDS`

Deeplus의 native backend authority에서 LLVM 계열을 제거하고 Cranelift로
교체한다. xVM은 교체 대상이 아니며 초기 개발·검증·REPL 실행 경로로
유지한다.

현재 backend architecture는 다음과 같다.

1. `xVM bytecode interpreter`: 초기 개발·검증·REPL 경로
2. `Cranelift ObjectModule AOT`: 첫 native object 경로
3. `Cranelift JITModule`: in-memory native JIT 경로

Deeplus MIR은 계속 유일한 실행 의미 정본이다. Cranelift IR(CLIF),
native object, JIT image, register, stack slot, relocation과 machine address는
MIR을 구현하는 비정본 projection이다.

이 판정은 backend architecture와 정적 계약을 바꾸지만 실제 backend
구현이나 실행 성공을 주장하지 않는다. 15개 product lane은 모두
`NOT_RUN`이며 semantic P0는 0, OPEN feature P1은 정확히 22건이다.

## 2. 교체 범위

다음 이전 native 경로는 current authority에서 supersede된다.

- LLVM AOT
- LLVM ORC JIT
- LLVM IR, bitcode, pass pipeline, personality, intrinsic 또는 LTO를
  Deeplus 구현 계약으로 전제하는 표면

기존 candidate, 과거 changelog, migration receipt와 완료된 handoff에 남은
당시 backend 표기는 immutable historical evidence다. 이들은 현재 backend
authority로 읽지 않는다.

## 3. HIR-H1 경계

HIR-H1의 자료형과 의미 node에는 Cranelift 전용 표현을 추가하지 않는다.
다음 항목은 canonical HIR에 들어갈 수 없다.

- CLIF `Value`, `Block`, `StackSlot`, `FuncRef` 또는 `Signature`
- register class, instruction encoding, relocation, object section
- target calling convention이나 native data layout
- JIT address, linker symbol spelling 또는 load order

HIR은 source와 checker가 닫은 타입, callable, conformance, witness,
ownership, effect, error, cancellation, isolation, cleanup, source order와
debug origin만 보존한다. `backend_layout_identity_count`는 계속 0이다.

## 4. MIR에서 Cranelift로의 projection

검증된 Deeplus MIR만 native projection의 입력이 될 수 있다.

```text
Verified<CanonicalHirH1>
  -> ExecutableHirH1
  -> Verified<DeeplusMir>
  -> CraneliftProjectionPlan
  -> backend-private CLIF
  -> ObjectModule | JITModule
```

`CraneliftProjectionPlan`은 MIR 의미 node가 아니라 target-bound compile
receipt의 일부다. MIR semantic digest와 다음 입력을 결합한다.

- exact target triple
- ISA 이름과 feature/settings 집합
- Cranelift crate family와 lockfile identity
- module kind: `ObjectAot` 또는 `InMemoryJit`
- pointer width, endianness, object format와 code/relocation model
- selected calling convention와 Deeplus runtime ABI digest
- optimization setting과 deterministic configuration digest
- object mode의 linker identity·arguments 또는 JIT mode의 import resolver
- runtime helper, safepoint/stack-map와 symbol-map identity

host default, 환경 변수, link order 또는 symbol lookup order가 이 입력을
암묵적으로 대신할 수 없다.

## 5. 공통 lowering과 두 finalization 경로

Object AOT와 JIT는 하나의 MIR→CLIF lowering 법칙을 공유한다. 두 경로는
다음 finalization 책임에서만 갈라진다.

- Object AOT는 relocatable object를 만들고 object bytes, object format,
  linker identity, linker arguments와 최종 artifact digest를 기록한다.
- JIT는 code/data를 memory에 finalize하고 import allowlist, resolved import
  map, executable-memory policy, finalized image identity와 lifetime을
  기록한다.

module-local function/data ID나 symbol spelling은 Deeplus의
`FunctionId`, `CallableImplementationId`, `WitnessId` 또는 다른 정적
identity를 새로 만들지 못한다. 정적 identity와 runtime metadata는
MIR digest에 결합된 sidecar/symbol map을 통해서만 연결한다.

## 6. 오류, trap, unwind와 cleanup

Deeplus의 `Error`, `Defect`, `Cancellation`, suspension과 cleanup은 명시적
MIR outcome/edge다.

- recoverable Error를 native exception으로 바꾸지 않는다.
- Defect를 임의 backend trap으로 대체하지 않는다.
- cancellation과 suspension을 host unwind로 구현하지 않는다.
- cleanup 순서를 personality routine이나 platform unwinder가 결정하지
  않는다.
- checked arithmetic는 MIR가 정한 성공/`ArithmeticDefect` 경계를
  보존한다.

Cranelift trap은 MIR가 이미 같은 terminal Defect를 선택했거나 verifier가
도달 불가능을 증명한 site에서만 사용할 수 있다. trap code와 MIR
`DefectId`의 대응은 target receipt에 결합한다. FFI unwind는 별도의
명시적 target/ABI profile이 없으면 경계를 넘을 수 없다.

## 7. ABI, layout, GC와 debug

semantic identity, serialization tag, runtime discriminant, ordinal,
layout/ABI identity는 계속 분리한다. native layout과 calling convention은
검증된 MIR 뒤 target projection에서만 정한다.

managed reference가 있는 경로는 MIR `SafepointId`와 root-map requirement를
보존해야 한다. 선택한 Cranelift/runtime 조합이 필요한 stack-map 또는
stable-handle capability를 제공하지 못하면 lowering을 fail-closed하며,
raw pointer나 추측한 layout으로 대체하지 않는다.

source location과 `DebugOrigin`은 semantic digest와 분리된 debug digest로
투영한다. debug info, unwind table 또는 profiler metadata가 없거나
불완전해도 프로그램 의미를 바꿀 수 없고, 실제 target receipt 전에는
지원 PASS를 주장하지 않는다.

## 8. 동등성·보안·재현성

xVM, Cranelift Object AOT와 Cranelift JITModule는 다음을 동일하게 관찰해야 한다.

- 좌→우 exactly-once evaluation
- final value 또는 ordered failure
- ownership/place transition과 cleanup balance
- effect, authority와 provider replay identity
- cancellation, suspension, concur/run/reply와 actor ordering
- FFI boundary의 explicit ABI/ownership outcome

JIT import는 닫힌 allowlist와 정확한 signature로만 해결한다. missing,
duplicate 또는 signature-mismatched import는 terminal link failure다.
JIT executable memory의 allocate/write/finalize/retire lifecycle을 receipt에
기록하며 stale function pointer의 사용을 허용하지 않는다.

같은 source, MIR digest, target profile와 toolchain identity는 동일한
object 또는 동등한 JIT observation receipt를 만들어야 한다. optimization
level은 receipt 입력이며 의미 권위가 아니다.

## 9. Toolchain 결정

현재 Deeplus Rust toolchain은 1.85.0이다. 실제 implementation vertical
slice의 기본 호환선은 Rust 1.85.0을 지원하는 Cranelift 0.121.2 family로
고정한다. 더 최신 Cranelift family를 사용하려면 Rust toolchain 승급과
dependency/supply-chain 검토를 하나의 별도 Build decision으로 결합한다.

현재 `deeplus-codegen-cranelift` crate는 책임 경계를 나타내는 scaffold이며
외부 Cranelift dependency나 실행 receipt를 갖지 않는다. 따라서 crate가
컴파일된다는 사실만으로 Object AOT 또는 JIT lane을 실행한 것으로
판정하지 않는다.

## 10. Acceptance

- current native lane identity가 정확히
  `cranelift_object_aot_backend`, `cranelift_jit_backend`다.
- 전체 product lane은 정확히 15개이며 모두 `NOT_RUN`이다.
- HIR backend-specific field count는 0이다.
- MIR semantic authority와 xVM 초기 경로가 유지된다.
- current 계약에 LLVM IR/bitcode/ORC/LTO 전제가 남지 않는다.
- Object/JIT가 하나의 lowering law와 서로 다른 finalization receipt를
  갖는다.
- native exception/trap이 Deeplus outcome을 발명하지 못한다.
- exact target/toolchain/runtime ABI가 receipt에 결합된다.
- historical evidence와 `candidate/**`는 수정·삭제하지 않는다.
- semantic P0 0, OPEN feature P1 22를 유지한다.

## 11. 근거

- Cranelift `Module`은 function/data collection과 linking의 공통 경계다.
- `ObjectModule`은 object file을 방출한다.
- `JITModule`은 code/data를 memory에 방출하고 finalize한다.
- CLIF는 frontend가 생성하는 backend IR이며 Deeplus의 언어 의미 정본이
  아니다.

공식 참조:

- <https://docs.rs/cranelift-module/latest/cranelift_module/trait.Module.html>
- <https://docs.rs/cranelift-object/latest/cranelift_object/struct.ObjectModule.html>
- <https://docs.rs/cranelift-jit/latest/cranelift_jit/struct.JITModule.html>
- <https://github.com/bytecodealliance/wasmtime/blob/main/cranelift/docs/ir.md>

## 12. R36 managed-reference profile binding

The fail-closed managed-reference guard is refined by
`STW_NONMOVING_TRACING_WITH_OPAQUE_STABLE_HANDLES_R1`. Verified MIR binds a
deterministically recomputed `deeplus.managed-memory-plan/r1`; Cranelift maps
its logical roots to explicit shadow-root slots and records the mapping in a
`deeplus.managed-reference-native-projection-receipt/r1` receipt.

Phase 1 does not use a moving, concurrent or generational collector and exposes
no weak-reference, finalizer, resurrection, pinning or managed-handle FFI
surface. Missing or invalid memory-plan, target-root projection, runtime-root
registry or JIT lifetime evidence blocks native lowering. This binding changes
no HIR identity, source syntax, feature P1 or product-support lane.
