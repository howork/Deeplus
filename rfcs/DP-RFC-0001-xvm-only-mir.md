# DP-RFC-0001 — xVM 전용 Deeplus MIR-X1 설계 기획

## Metadata

| Field | Value |
|---|---|
| Status | `DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE` |
| Baseline | `howork/Deeplus@b5ae4eccee54b185915d7905e45177dc6c276a2e` |
| Scope | Deeplus MIR의 의미, 자료구조, 검증, 직렬화, xVM 투영 경계 |
| Current backend authority | xVM 초기 실행 + LLVM AOT + 후속 LLVM ORC JIT |
| Proposed alternative | xVM-only MIR-X1 |
| Target language version | `FUTURE_0_1_3_DECISION_NOT_ESTABLISHED` |
| Target spec revision | `FUTURE_REVISION_NOT_ESTABLISHED` |
| Tracking issue | `#24` |
| Supersedes | None |
| Required primary roles | Design_, Spec_, Impl_, Test_, Devel_ |
| Required auxiliary roles | Build_, Archive_ (future adoption review only) |
| Author | TBD |
| Sponsor | user authority |
| Created | 2026-07-22 |

## Authority and execution fence

- 이 문서는 토론과 향후 판정을 위한 비정규·비활성 제안이다. 현재 정본은 [management policy](../governance/policies/management-policy.yaml)와 [MIR 의미 문서](../spec/mir/semantics.md)이며, xVM 초기 실행, LLVM AOT, 후속 LLVM ORC JIT를 보존한다.
- 제목의 “xVM 전용”과 문서 안의 규범형 문장은 모두 **제안 내부에서만** 효력이 있는 대안이다. 현행 backend architecture를 제한하거나 변경하지 않는다.
- canonical/source 변경, 구현, 활성화, publication 또는 promotion authority는 모두 `NONE`이다.
- X1-A..X1-E 실행은 Deeplus 0.1.3이 확립되고 별도 Design_ authority가 부여된 뒤에만 검토할 수 있다. 현재 상태는 전부 `NOT_AUTHORIZED / NOT_RUN`이다.
- 현행 ledger의 semantic P0는 0이다. 이 Draft는 신규 P0/P1을 판정하거나 기존 P1을 폐쇄하지 않으며, 기존 feature P1 22건은 모두 OPEN 상태를 유지한다. product lane은 정확히 15/15 `NOT_RUN`이다.
- 이 Draft의 병합은 제안의 보존과 검토 가능성만 뜻한다. MIR-X1 채택이나 아래 19·20절의 실행을 승인하지 않는다.

| Profile | Backend contract | Disposition |
|---|---|---|
| Current authority | xVM initial execution + LLVM AOT + later LLVM ORC JIT | 변경 없음 |
| This proposal | xVM-only | 미결; 별도 Design_ 판정 필요 |

### Open authority question

| Question | Owner | Closure method | Status |
|---|---|---|---|
| 현행 xVM + LLVM backend architecture를 xVM-only로 변경할 것인가? | Design_ | 0.1.3 확립 여부를 판정하는 future cycle에서 cross-role evidence를 결합한 명시적 채택·보류·기각 판정 | OPEN |

### Role decisions

| Role | Decision | Main concern | Preferred alternative | Required gate |
|---|---|---|---|---|
| Design_ | NOT_REVIEWED | backend architecture 및 language-version authority | TBD | 명시적 채택·보류·기각 판정 |
| Spec_ | NOT_REVIEWED | normative MIR/backend preservation contract | TBD | 완결된 normative delta |
| Impl_ | NOT_REVIEWED | vertical-slice implementability 및 execution architecture | TBD | 승인된 구현 범위와 실행 증거 |
| Test_ | NOT_REVIEWED | verifier·differential-conformance acceptance matrix | TBD | target-bound acceptance matrix |
| Devel_ | NOT_REVIEWED | 단계·tooling·migration dependency | TBD | 승인된 dependency order |

[EXPR-001_BINDING]
clause_id: EXPR-001
authority: governance/policies/management-policy.yaml#EXPR-001
clause_digest: 42250c554d2d5f9cfb29bbd3668bed40ec1390fce658ac1804f7c6de29b1ac39
classification: non-authoritative proposal expressing alternatives; no restriction activation

## 1. 결론

이 RFC가 향후 대안으로 제안하는 MIR은 다음 형식이다.

> **타입 있는 블록 인자 기반 CFG + 불변 SSA 값 + 명시적 mutable Place + 명시적 소유권/정리 책임 + Error·Defect·Cancellation을 분리한 terminator + xVM이 직접 보존하는 cleanup/suspend frame**

이 문서에서는 이 형식을 **Deeplus MIR-X1**이라고 부른다.

MIR-X1은 스택 머신 IR이 아니다. 식은 중첩되지 않고, 계산 결과는 `ValueId`, 변경 가능한 저장소는 `PlaceId + Projection`, 제어 합류 값은 블록 인자로 표현한다. xVM은 `ValueId`와 `PlaceId`를 함수별 고정 frame slot에 직접 대응시킬 수 있다. 블록 인자 전달은 임시 튜플을 통한 동시 복사로 실행하므로 초기 구현에 별도 out-of-SSA나 물리 레지스터 할당이 필요 없다.

MIR-X1은 bytecode도 아니다. opcode 폭, branch offset, frame slot 폭, object layout, collector 방식은 xVM 투영의 구현 세부다. 반대로 평가 순서, 호출 채널, 정적 identity, ownership/place 전이, cleanup, 실패, suspension, actor/provider 관찰은 MIR 의미다.

## 2. 현 상태와 설계 출발점

현재 저장소 자체는 greenfield가 아니다. 다만 실행 가능한 MIR representation은 아직 확립되거나 product evidence로 검증되지 않았으므로, 현행 authority를 보존한 채 successor 대안을 설계할 여지가 있다.

- 모든 MIR/XBC/xVM 제품 경로는 `NOT_RUN`이다: [implementation-status.yaml](../current/implementation-status.yaml).
- 범용 `deeplus-mir`, `deeplus-xbc`, `deeplus-xvm`은 책임 경계를 표시하는 scaffold다.
- 현재 `sfd_p1_009`의 `MirPlan`은 CFG가 아니라 이벤트 배열과 카운터이며, XBC는 그 값을 감싸고 xVM은 outcome을 카운트로 바꾼다.
- 기존 [MIR 의미 문서](../spec/mir/semantics.md)와 [헌법적 법칙](../spec/contracts/constitutional-laws.json)은 풍부한 관찰 규칙을 제공하지만, 실행 가능한 block/value/place/terminator 형식은 정의하지 않는다.
- [mir-responsibility 스키마](../schemas/language/mir-responsibility.schema.json)와 [RCTS MIR event 스키마](../schemas/language/rcts-v5-mir-event.schema.json)는 실행 IR보다 trace/receipt 형식에 가깝다.

따라서 이 제안이 별도 authority로 채택되는 경우에는 기존 `MirPlan`을 일반화하지 않고 MIR-X1을 successor model 후보로 삼으며, 기존 이벤트 스키마는 MIR-X1 실행 trace에서 생성되는 conformance projection으로 유지한다. 현재 canonical model과 backend authority는 이 문서로 변경되지 않는다.

## 3. 설계 목표

MIR-X1은 다음 불변식을 만족해야 한다.

1. **한 번의 의미 결정**: HIR/checker가 정한 타입, label, witness, extension, provider, ownership, effect/error를 MIR에서 다시 검색하지 않는다.
2. **한 번의 평가**: 피연산자·인수·guard·collection entry·cleanup capture의 좌→우 평가가 CFG와 operation 순서에 완전히 드러난다.
3. **숨은 제어 없음**: 실패, cleanup, cancellation, suspend, actor protocol 결과가 host Rust panic이나 숨은 exception table에 의존하지 않는다.
4. **책임 보존**: move, borrow, inout, resource, call-right, task ownership을 verifier가 경로별로 증명한다.
5. **실행 전 거부**: 검증되지 않은 MIR은 xVM에 도달하지 않는다. 잘못된 MIR은 수정하거나 추측하지 않고 결정적으로 거부한다.
6. **무정의 값 없음**: `undef`, poison, 암묵적 overflow, 암묵적 widening, 타입 혼동을 허용하지 않는다.
7. **결정성**: 같은 normalized input은 같은 canonical bytes와 semantic digest를 만든다.
8. **xVM 직접성**: MIR을 xVM fixed frame과 명시적 runtime operation으로 단순하게 투영할 수 있어야 한다.
9. **관찰 경계**: 결과/실패, I/O·authority, actor enqueue/dequeue, suspend/resume, cancellation, cleanup, provider observation은 보존하고, frame 배치와 GC 알고리즘 같은 구현 세부는 관찰로 만들지 않는다.

## 4. 제안 내부에서 선택한 선행 설계 원칙

인터넷의 1차 자료에서 다음 원칙만 이 제안 내부의 후보로 취한다.

| 선행 사례 | 채택 | 배제 |
|---|---|---|
| [Rust MIR](https://rustc-dev-guide.rust-lang.org/mir/index.html), [MIR RFC 1211](https://rust-lang.github.io/rfcs/1211-mir.html) | 완전 타입화 CFG, 비중첩 식, Place, 명시적 copy/move, statement/terminator 구분, drop obligation 분석 | native stack allocation 힌트, 단일 unwind 채널, target-specific cleanup topology |
| [Swift SIL](https://github.com/swiftlang/swift/blob/main/docs/SIL/SIL.md), [Ownership SSA](https://github.com/swiftlang/swift/blob/main/docs/SIL/Ownership.md) | 블록 인자, SSA dominance, consuming/non-consuming use, 경로별 exactly-once ownership 검증 | ARC retain/release, address-only ABI, target calling convention |
| [Slang IR design](https://shader-slang.org/slang/design/ir.html) | successor block argument와 edge의 동시 할당 의미 | shader stage/type, GPU target 표현 |
| [WebAssembly validation](https://webassembly.github.io/spec/core/appendix/algorithm.html) | 선언적 validity와 실행 전 fail-closed validator, value/control/init 상태의 분리 | operand-stack IR, 구조적 label depth, 모든 비정상 결과를 하나의 trap으로 통합 |
| [JVMS verification](https://docs.oracle.com/javase/specs/jvms/se26/html/jvms-4.html#jvms-4.10.1) | block-entry type state와 전이 규칙으로 안전성을 재증명하는 방식 | JVM operand stack, category 슬롯, 단일 Throwable 계층, 실행 중 symbolic 재탐색 |
| [Dalvik bytecode](https://source.android.com/docs/core/runtime/dalvik-bytecode), [Lua VM 논문](https://www.lua.org/doc/sblp2005.pdf) | 함수 진입 시 크기가 정해지는 register frame과 적은 dispatch를 위한 3주소 실행 | 32비트 슬롯 규칙, wide register pair, 동적 tag/metamethod 재탐색 |
| [Rust coroutine transform](https://doc.rust-lang.org/nightly/nightly-rustc/rustc_mir_transform/coroutine/index.html) | suspend를 가로질러 live인 local과 drop/close 상태를 정확히 보존해야 한다는 원칙 | compiler-generated state-machine layout을 MIR 의미로 고정 |
| [OpenJDK safepoint/GC map](https://openjdk.org/groups/hotspot/docs/HotSpotGlossary.html) | safepoint마다 live managed reference 위치를 알 수 있어야 한다는 원칙 | 특정 collector, object header, native pointer 표현 |
| [Erlang signal ordering](https://www.erlang.org/doc/system/ref_man_processes.html) | 같은 sender→receiver 채널의 전송 순서만 보장하는 경계 | 전역 sender 순서 또는 scheduler 결정성 |
| [RFC 8949 deterministic CBOR](https://www.rfc-editor.org/rfc/rfc8949.html#section-4.2) | shortest encoding, 확정 길이, 정렬된 key를 이용한 byte-level 결정성 | 임의 CBOR 표현을 모두 허용하는 느슨한 decoder |

### 4.1 제안 내부 형식 선택

| 후보 | Proposal disposition | 이유 |
|---|---|---|
| operand-stack MIR | EXCLUDED_FROM_PROPOSAL | block merge, owned 값 전달, suspend live set, root map을 stack-height 관례에 숨긴다. |
| memory-only non-SSA CFG | EXCLUDED_FROM_PROPOSAL | immutable 계산의 dominance, use, liveness, canonical numbering이 불필요하게 간접적이다. |
| pure SSA + memory token | EXCLUDED_FROM_PROPOSAL | Deeplus `var`, partial move, borrow/inout, transactional construction과 cleanup owner를 과도하게 인코딩한다. |
| block-argument SSA value + Place + linear capability | SELECTED_FOR_PROPOSAL | immutable 계산과 mutable/ownership 책임을 각자 자연스러운 형식으로 검증하고 xVM fixed frame에 직접 대응한다. |
| cleanup block 복제 | EXCLUDED_FROM_PROPOSAL | 백엔드가 하나인데 모든 이탈 edge에 cleanup CFG를 복제해 code size와 suppression 검증만 늘린다. |
| xVM logical cleanup stack | SELECTED_FOR_PROPOSAL | 동적 `defer`, LIFO, exact disarm, suspend/cancel 보존을 한 실행 모델로 닫는다. |
| compiler state-machine expansion | EXCLUDED_FROM_PROPOSAL | PC/state/layout을 MIR 의미에 고정하고 cleanup·GC 정보를 중복시킨다. |
| xVM suspended frame | SELECTED_FOR_PROPOSAL | MIR suspend point와 live responsibility를 그대로 보존한다. |

결과적으로 MIR-X1은 특정 기존 IR의 복제품이 아니라 Deeplus 법칙에 필요한 요소만 결합한 xVM 전용 형식이다.

## 5. MIR 단계와 권위

두 Rust 자료형을 분리한다.

```text
Typed HIR
  -> MirDraft                 // lowering 중간값, pseudo-op 허용, 실행·직렬화 금지
  -> canonicalize + verify
  -> ProposedMirX1            // 채택될 경우에만 successor MIR 후보
  -> xVM projection
```

`MirDraft`와 `ProposedMirX1`은 동일한 `Body`에 phase flag를 붙인 것이 아니라 서로 다른 타입이어야 한다. 이 제안이 채택된 뒤의 실행 함수와 serializer는 `Verified<ProposedMirX1>`만 받는다. 이 구분은 불완전한 lowering 상태가 우연히 실행되거나 receipt identity가 되는 것을 막는다.

초기 MIR-X1에는 의미 최적화 pass를 두지 않는다. canonicalization은 ID 재번호화, table 정렬, pseudo-op 제거, 명시적 edge 형성처럼 의미를 선택하지 않는 변환만 수행한다. 향후 최적화 variant는 자기 canonical content로 계산한 `variant_content_digest`와 원본을 가리키는 `source_semantic_digest`를 따로 가진다. 원본 digest를 variant content hash처럼 재사용하지 않는다. pass별 equivalence verifier와 `(source_digest, variant_digest, pass_id)` receipt가 생기기 전에는 variant를 실행할 수 없다.

## 6. 핵심 자료구조

### 6.1 Module과 Body

```text
MirModuleX1 {
  schema_version: Version,
  authority_digest: Digest,
  feature_set: FeatureSet,
  type_table: [MirType],
  identity_table: [StaticIdentity],
  constant_table: [Constant],
  functions: [MirFunction],
}

MirFunction {
  function_id: FunctionId,
  signature: MirSignature,
  body: MirBody,
}

MirBody {
  entry: BlockId,
  places: [PlaceDecl],
  loans: [LoanDecl],
  cleanup_regions: [CleanupRegionDecl],
  blocks: [BasicBlock],
  provenance: ProvenanceTable,
}

BasicBlock {
  params: [BlockParam],
  ops: [Operation],
  terminator: Terminator,
}
```

모든 ID는 index newtype이며 Rust pointer나 hash-map 주소를 포함하지 않는다. 한 block에는 정확히 하나의 terminator가 있다. 암시적 fallthrough는 없다.

### 6.2 Value, Place, token

| 종류 | 의미 | 규칙 |
|---|---|---|
| `ValueId` | operation 결과, block parameter, 선형 token을 포함한 모든 SSA 값 | 한 번 정의되고 dominance를 만족한다. |
| `BlockParam` | predecessor가 공급하는 `ValueId` 정의 지점 | 모든 incoming edge의 개수·타입·ownership mode가 정확히 같아야 한다. |
| `PlaceId` | `var`, local storage, capture storage, aggregate storage | 초기화·move·borrow 상태를 별도 dataflow로 추적한다. |
| `Projection` | field, tuple element, active variant, statically in-range index | 평가와 실패가 없는 projection만 허용한다. |
| `LoanId` | 정적 또는 checked origin과 region에 결합된 borrow/inout identity | derived view와 `AccessToken`이 같은 loan을 가리켜야 한다. |
| `AccessToken` | 한 `LoanId`의 shared borrow 또는 exclusive inout 권리 | 선형이며 `access.end`가 정확히 한 번 소비한다. |
| `CleanupKey` | runtime cleanup stack의 정확히 한 entry를 조작하는 scoped key | 같은 block에서 pin, owner token에 seal, 또는 합법적 disarm 중 하나로 소비한다. |
| `BuilderToken` | construction의 부분 초기화 상태 | commit 또는 rollback으로 정확히 한 번 끝난다. |
| `TaskToken` | structured task ownership | join/cancel/transfer 중 정확히 하나로 끝난다. |
| `CallRightToken` | `once` callable 호출권 | 한 번의 consuming call로 끝난다. |

동적 index, downcast, bounds check처럼 실패 가능한 계산은 `Projection` 안에 숨기지 않는다. checked terminator의 성공 edge가 element 값 또는 `(AccessToken, CheckedView)`를 직접 정의한다. 분리된 재사용 가능 proof는 만들지 않는다. mutable base의 checked view와 함께 정의된 `AccessToken`이 base mutation을 막고, immutable SSA aggregate는 원래 변경될 수 없다. 따라서 check 뒤 base를 바꾸고 낡은 proof로 projection하는 경로가 존재하지 않는다.

Loan은 다음 관계를 정적으로 가진다.

```text
LoanOrigin =
    Static { base: PlaceId | ValueId, projection: Projection }
  | CheckedIndex { base: PlaceId, index: ValueId, check_site: CheckSiteId }
  | CheckedDowncast { base: PlaceId, variant: TypeId, check_site: CheckSiteId }

LoanDecl {
  loan_id: LoanId,
  kind: shared | inout,
  origin: LoanOrigin,
  region_id: RegionId,
}

borrow.begin_shared -> (AccessToken<LoanId>, BorrowedView<LoanId>)
inout.begin          -> (AccessToken<LoanId>, InoutView<LoanId>)
checked_index_shared -> ok(AccessToken<LoanId>, BorrowedView<LoanId>) | bounds(...)
checked_index_inout  -> ok(AccessToken<LoanId>, InoutView<LoanId>) | bounds(...)
access.end AccessToken<LoanId>
```

모든 derived view는 `LoanId`를 type metadata로 가진다. view가 block edge를 건너면 같은 edge에서 그 loan의 live `AccessToken`도 `consume`되어 successor token parameter로 전달되어야 한다. `access.end` 뒤에는 해당 LoanId의 view가 live하거나 사용될 수 없다. 초기 X1은 서로 다른 LoanId를 하나의 block parameter로 합치는 것을 금지한다. 각 predecessor에서 loan을 끝내고 join 뒤 다시 borrow해야 한다.

mutable dynamic projection의 checked terminator는 성공 edge에서 token과 view를 원자적으로 함께 정의한다. immutable SSA aggregate의 checked index는 element `ValueId`만 반환해도 된다. 초기 X1의 alias 판정은 base 단위로 보수적이다. 같은 mutable base에 inout loan이 하나라도 live하면 index 값이 달라도 두 번째 inout 또는 shared loan을 거부하고, shared loan이 live한 base에도 inout을 거부한다. 서로 다른 동적 index의 disjointness를 이용하려면 향후 `checked_disjoint` 법과 terminator를 별도로 추가한다.

`BlockParam`, `AccessToken`, `CleanupKey`, `BuilderToken`, `TaskToken`, `CallRightToken`은 별도 operand ID 공간이 아니다. 모두 각자의 capability `MirType`을 가진 `ValueId`다. 따라서 `EdgeArg`의 `ValueId` 하나로 ordinary value와 선형 token을 loop/back-edge를 포함한 모든 successor에 전달할 수 있다. 단, raw `CleanupKey`는 같은 block에서 반드시 소비되고 edge를 건널 수 없다. 봉인된 cleanup entry identity는 `BuilderToken`이나 owned value responsibility의 일부로 이동한다.

### 6.3 Ownership mode

MIR 값의 최소 ownership mode는 다음과 같다.

```text
reusable                 // 명시적 copy가 허용되는 값
owned                    // move/consume가 필요한 값
borrowed(region_id)      // shared view
inout(region_id)         // exclusive mutable view
```

`resource`, actor isolation, cleanup 필요성은 type responsibility에 포함한다. `borrowed`와 `inout`은 raw pointer가 아니라 base place/value와 projection에 연결된 논리적 view다.

`Absent`는 lexical scope metadata이며 runtime join lattice의 원소가 아니다. scope 안의 각 leaf move path는 다음 nonempty state set을 가진다.

```text
ExactUninit = {Uninitialized}
ExactInit   = {Initialized}
ExactMoved  = {Moved}
MaybeInitialized = {Initialized, Uninitialized and/or Moved}
```

- unreachable predecessor는 join에서 제외하고, 나머지 predecessor state set의 합집합이 block-entry state다.
- 일반 read/move/borrow와 `place.replace`는 state set이 정확히 `{Initialized}`일 때만 가능하다.
- `store.init`는 state set이 `{Uninitialized}` 또는 `{Moved}`일 때만 가능하다.
- `MaybeInitialized`에는 xVM init bit가 있으며 conditional cleanup 또는 verifier가 만든 `switch_init` edge가 상태를 좁힐 때만 사용한다. source program은 init bit를 관찰할 수 없다.
- aggregate state는 leaf move-path state의 product다. parent read/move는 모든 active leaf가 `{Initialized}`이고 live conflicting loan이 없을 때만 가능하며, parent move는 모든 leaf를 `{Moved}`로 바꾼다.
- enum/union은 active tag가 허용한 leaf만 product에 포함한다. branch refinement는 해당 successor에서만 tag와 state set을 좁힌다.

### 6.4 타입과 static identity

`MirTypeId`는 normalized Deeplus type을 가리킨다. source alias나 spelling은 없다. 최소한 다음 책임을 보존한다.

- nominal identity와 generic arguments
- closed union/intersection/Option/Result alternatives
- ordered Record label row
- function call channels와 callable profile
- ownership/reusable/resource 성질
- effect row, ErrorSet, internal DefectSet, cancellation/suspension capability, isolation
- NumericArray shape/rank/orientation과 measure dimension/ratio

MIR은 다음 identity domain을 서로 다른 ID type으로 유지한다.

```text
FunctionId
TypeId
ClassSlotId
TraitId
WitnessId
ExtensionMemberId
LabelId
ProviderId
AuthorityId
ActorProtocolId
```

runtime `String`이나 `Map` key는 이 ID들로 변환될 수 없다.

`MirSignature`는 value/context/witness channel과 함께 `EffectRow`, `ErrorSet`, verifier가 body와 runtime intrinsic 계약에서 닫은 `DefectSet`, cancellation/suspension capability, isolation, authority requirement를 가진다. `DefectSet`은 source의 `throws`와 섞이지 않지만 call boundary의 defect successor 완전성을 검증하기 위한 MIR 계약이다.

MIR 타입은 xVM object layout이나 collector를 고정하지 않는다. `Char`, `Bytes`처럼 현재 표현 법칙이 닫히지 않은 형식은 semantic `TypeId`까지만 존재하며, 해당 operation family는 feature gate가 닫힐 때까지 executable MIR에 들어올 수 없다.

## 7. CFG와 실행 규칙

### 7.1 블록 인자

phi instruction 대신 블록 인자를 사용한다.

```text
bb0(%opt: Option<Int>):
  switch_enum %opt
    some(%v) -> bb_some(%v)
    none     -> bb_none

bb_some(%v: Int):
  br bb_join(%v)

bb_none:
  invoke @fallback()
    ok(%v)       -> bb_join(%v)
    error(%fail) -> bb_error(%fail)

bb_join(%result: Int):
  leave return_plan(consume %result)  // depth-0 bb_complete_return을 target으로 함
```

xVM은 edge 인수 전체를 임시 튜플에 읽은 후 successor의 block-param slot에 동시에 쓴다. 따라서 loop back-edge와 swap도 명확하며 phi 해석 순서 문제가 없다.

각 edge 인수는 값만이 아니라 전달 방식을 가진다.

```text
EdgeArg = copy(ValueId) | consume(ValueId) | forward_view(ValueId)
```

- `copy`는 `reusable` 값에만 허용한다.
- `consume`은 `owned` 값과 선형 token을 successor parameter로 이동한다.
- `forward_view`는 같은 region과 `LoanId`의 `borrowed`/`inout` view만 전달하며 lifetime을 늘리지 않는다. 그 edge에는 대응 `AccessToken<LoanId>`의 `consume`도 있어야 한다.
- 한 terminator의 서로 배타적인 successor 여러 곳에 같은 owned 값을 `consume`으로 적을 수는 있지만, 선택된 동적 경로에서는 정확히 한 번만 소비되어야 한다. 동일 successor나 동일 실행 경로에서의 중복 소비는 거부한다.

따라서 block-argument 합류는 타입뿐 아니라 ownership mode, region, consume/copy 방식까지 검증한다.

### 7.2 Operation과 terminator의 경계

`Operation`은 현재 block 안에서 정확히 다음 operation으로 진행하는 단일 단계다. 제어를 바꿀 수 있는 연산은 `Terminator`다.

주요 operation family:

- constants, pure unary/binary operations
- aggregate/enum/record construction의 total 단계
- `place.load_copy`, `place.load_move`, `place.store_init`
- `borrow.begin_shared`, `inout.begin`, `access.end`
- `cleanup.region_enter`, `cleanup.register`
- `construction.begin`, `construction.field`, `construction.commit`
- `closure.make`, static projection, union inject/project
- law/source/observation site metadata

최소 terminator family:

```text
br
cond_br
switch_enum / switch_int
invoke
checked
place_replace
leave
suspend
cancel_check
task_op
actor_op
provider_op
complete
unreachable_proven
```

`unreachable_proven`은 `Never` 또는 verifier가 확인한 완전한 partition 뒤에서만 허용한다. 임의의 dead block이나 poison 생성 수단이 아니다.

### 7.3 명시적 outcome

Error, Defect, Cancellation을 하나의 exception으로 합치지 않는다. 함수 호출자 경계의 결과는 다음과 같다.

```text
Outcome<T> =
    Return(T)
  | Error(ErrorId, payload)
  | Defect(DefectId, payload)
  | Cancel(CancelToken)
```

함수 내부의 region 이탈은 `Outcome`을 곧바로 반환하지 않고 다음 `LeavePlan`을 사용한다.

```text
FailureAtom = Error(ErrorId, payload) | Defect(DefectId, payload)

FinalPayload =
    Normal([runtime value])
  | Failed { primary: Error | Defect, suppressed: [FailureAtom] }
  | Cancelled { token: CancelToken, suppressed: [FailureAtom] }

LeaveContinuation {
  target: BlockId,
  fixed_args: [EdgeArg],
  bind: FinalPayloadShape,
}

LeavePlan {
  target_region_depth,
  pending: Normal([EdgeArg]) | Error(EdgeArg) | Defect(EdgeArg) | Cancel(EdgeArg),
  continuations: {
    normal?: LeaveContinuation,
    error?:  LeaveContinuation,
    defect?: LeaveContinuation,
    cancel?: LeaveContinuation,
  },
}
```

cleanup이 정상 이탈을 Error/Defect로 바꿀 수 있으므로 `leave`는 최종 family별 continuation을 미리 갖는다. `bind`는 정적 predecessor 값이 아니라 drain이 만든 `FinalPayload`를 target block의 지정 block parameter에 원자적으로 정의하는 **leave 전용 binder**다. error/defect/cancel continuation은 primary와 ordered suppressed list를 잃지 않고 받는다. 각 continuation은 함수 signature, lexical handler, cleanup budget에서 실제로 발생 가능한 family와 정확히 일치해야 한다.

final payload parameter는 ordinary `br`가 공급하는 parameter와 definition class가 다르다. binder target block에는 같은 `FinalPayloadShape`의 `leave` predecessor만 들어올 수 있고 ordinary predecessor와 섞을 수 없다. `fixed_args`와 final payload parameter의 arity/type/ownership은 별도로 검증한 뒤 동시에 slot에 쓴다.

`Caller`라는 특별 continuation은 두지 않는다. 함수 밖으로 나가는 모든 plan은 cleanup depth 0의 family별 completion block을 target으로 삼고, 그 block의 유일한 terminator `complete FinalPayload`가 `Outcome`을 호출자에게 방출한다. 따라서 `leave` 자체가 host return을 수행하는 우회 경로는 없다.

```text
bb_complete_return(%p: FinalNormal<T>): complete return(%p)
bb_complete_error(%p: FinalFailed<Error>): complete error(%p)
bb_complete_defect(%p: FinalFailed<Defect>): complete defect(%p)
bb_complete_cancel(%p: FinalCancelled): complete cancel(%p)
```

`invoke`는 callee signature가 허용한 successor만 가진다.

```text
invoke callee, args
  ok(values...)       -> bb_ok(...)
  error(failure)      -> bb_error(...)   // declared ErrorSet이 있을 때만
  defect(failure)     -> bb_defect(...)  // declared DefectSet이 있을 때만
  cancel(token)       -> bb_cancel(...)  // CancellationPointId가 있을 때만
```

`throws Never` 호출에 error edge를 넣는 것, `DefectSet`과 defect edge가 불일치하는 것, `CancellationPointId`와 cancel edge 중 하나만 있는 것은 모두 verifier 오류다. Host Rust panic은 xVM의 내부 결함 보고에만 쓰며 Deeplus outcome 전달에는 쓰지 않는다.

### 7.4 checked operation

초기 MIR에는 unchecked integer arithmetic을 넣지 않는다.

```text
checked_add.i32 %a, %b
  ok(%sum)             -> bb_next(%sum)
  overflow(%fault)     -> bb_fault(%fault)
```

별도 의미가 승인된 경우에만 `wrapping` 또는 `saturating` family를 추가한다. division by zero, signed `MIN / -1`, invalid shift count, checked cast failure도 명시적 reason을 가진다. 실패 edge에서는 결과 값을 정의하지 않는다.

constant folding은 같은 width, signedness, rounding, failure 규칙을 그대로 사용한다.

## 8. 호출 형식과 dispatch

### 8.1 CallShape

MIR signature와 call site는 parameter channel을 보존한다.

```text
CallShape {
  fixed_positional: [ValueId],
  fixed_named: [(LabelId, ValueId)],
  repeated_positional: [ValueId],
  named_tail: [(LabelId, ValueId)],
  context: [ValueId],
  witnesses: [(WitnessId, ValueId?)],
}
```

`named_tail`은 `**record`를 HIR/checker가 정적 label row로 닫은 결과다. label 순서는 source evaluation order를 유지한다. xVM에서 Map entry를 순회해 argument label을 만들지 않는다. callee의 `Record***` collector는 이 정적 row로 하나의 Record 값을 만든다.

### 8.2 CalleeRef

```text
CalleeRef =
    Direct(FunctionId)
  | ClassDispatch(ClassSlotId, receiver)
  | WitnessDispatch(WitnessId, requirement_id, receiver)
  | ExtensionDispatch(ExtensionMemberId, receiver)
  | Closure(ValueId)
```

MIR에서 overload resolution, witness coherence, extension activation, provider lookup을 다시 수행하지 않는다. runtime dispatch가 필요한 class slot도 slot identity는 이미 고정되어 있어야 한다.

### 8.3 Closure

Closure 값은 다음 논리 형식을 가진다.

```text
ClosureValue {
  function_id: FunctionId,
  environment_type: TypeId,
  captures: [CaptureDescriptor],
  call_kind: shared | mut | once,
  callable_profile: effects/errors/defects/cancel/suspend/isolation/context/witness,
}
```

Capture descriptor는 source order, capture mode(`borrow`, `inout`, `move`, `clone`, `deep`, `copy`, `once`), type, ownership, cleanup order를 보존한다.

`closure.make`는 이미 준비된 capture만 environment에 설치한다. `clone`/`deep` 준비가 allocation, effect, Error/Defect, cancellation을 일으킬 수 있으면 source order의 별도 `invoke`/checked terminator로 먼저 수행하고 성공 edge의 owned `PreparedCapture`를 넘긴다. 그러므로 `closure.make` 안에는 사용자 clone/deep 호출이나 숨은 실패 edge가 없다. environment storage allocation 자체는 `OpProfile.may_allocate/may_collect`로 표시하며 OOM 의미는 닫힐 때까지 xVM-fatal 경계를 유지한다.

- `shared` call은 environment를 소비하지 않는다.
- `mut` call은 environment에 exclusive access가 있어야 한다.
- `once` call은 `CallRightToken`과 closure를 소비한다.
- escaping/non-escaping environment의 실제 frame/heap 배치는 xVM 세부다.
- captured resource의 cleanup은 GC finalization이 아니라 명시적 closure cleanup 책임이다.

## 9. cleanup, failure, construction

### 9.1 xVM cleanup stack

이 RFC의 xVM-only 대안을 채택한다고 가정할 때 cleanup block을 모든 CFG edge에 복제하지 않는다. 제안된 MIR-X1과 xVM은 논리적 cleanup stack을 직접 가진다.

```text
CleanupRegionDecl {
  region_id,
  parent_region,
  budget: CleanupBudget { effects: EffectRow, errors: ErrorSet },
  derived_defects: DefectSet,
}

cleanup.region_enter RegionId
cleanup.register RegionId, CleanupFunctionId, evaluated_captures, CleanupProfile
  -> CleanupKey
cleanup.pin CleanupKey
cleanup.seal CleanupKey, OwnerToken -> OwnerToken
cleanup.disarm CleanupKey | OwnerToken, DischargeKind
leave LeavePlan
```

Region nesting은 정적이며 block entry마다 일치해야 한다. 한 region 안의 등록 개수는 runtime에 따라 달라질 수 있다. branch나 loop 안의 조건부 `defer`도 같은 region의 동적 stack에 등록한다.

`cleanup.register` 전에 capture를 좌→우로 정확히 한 번 평가한다. 등록 후 action과 capture의 ownership은 runtime region stack으로 이동하고, 반환된 선형 `CleanupKey`는 stack의 정확한 `(RegionId, registration_ordinal)` entry를 가리키는 조작 권리일 뿐 action owner가 아니다.

- ordinary `defer`는 key를 즉시 `cleanup.pin`해 이후 disarm할 수 없는 stack-owned action으로 만든다. loop iteration마다 생기는 임의 개수의 action도 SSA collection으로 운반하지 않고 runtime stack에 쌓인다.
- construction/resource owner가 나중에 exact disarm/transfer해야 하면 key를 해당 linear owner token에 `cleanup.seal`한다. owner move와 함께 sealed identity가 이동한다.
- `DischargeKind`는 `ConstructionCommitted`, `ResponsibilityRehomed`, `ActionCompleted`의 닫힌 enum이며 arbitrary producer가 만드는 proof value가 아니다. verifier가 해당 instruction의 typestate 전제에서 직접 재구성한다.
- non-top entry를 disarm하면 그 ordinal을 tombstone으로 바꾼다. 이후 등록 순서는 바뀌지 않고 `leave` drain은 tombstone을 건너뛰므로 `begin B → defer D → commit B`도 D를 잘못 해제하지 않는다.

`leave`는 이탈 region의 stack-owned armed action을 LIFO로 실행한다. 정상 payload로 ownership이 region 밖에 이동하면 그 sealed responsibility는 `ResponsibilityRehomed`로 현재 entry를 해제하고 target region 또는 caller frame의 새 responsibility로 원자적으로 이전한다. `def#cleanup`은 일반 `invoke` 대상이 아니며 등록된 cleanup action으로만 실행된다.

`CleanupBudget`은 시간 제한이 아니라 현재 Deeplus의 **허용 effect row와 escaping ErrorSet 대수**다. 등록되는 호출의 effect/error profile은 enclosing region budget의 부분집합이어야 하고, cleanup에서 새로 primary가 될 수 있는 Error는 enclosing function/handler continuation에도 포함되어야 한다. `derived_defects`는 등록 action들의 `DefectSet` 합집합이며 surface budget syntax를 새로 만들지 않는다. Defect는 Error로 바꾸지 않고 function `DefectSet`과 별도 continuation에 보존한다.

초기 MIR-X1 cleanup entry는 **non-suspending, non-cancellable**이다. drain 도중 들어온 cancellation 요청은 cleanup을 중단하거나 기존 primary를 바꾸지 않으며, 다음 명시적 cancellation point까지 전달되지 않는다. async cleanup이 필요해지면 cleanup-frame 재진입, 중첩 cancellation, suppression 순서를 별도 법으로 닫은 뒤 feature를 추가한다.

### 9.2 leave 알고리즘

`leave LeavePlan`은 return, throw, break/continue depth transfer, cancellation, construction abort가 region을 빠져나가는 유일한 방법이다.

1. pending payload의 모든 `EdgeArg`를 고정하고 owned 값을 consume한다. target depth 위에서 그 값에 결합된 sealed cleanup entry는 실행하지 않고 원자적으로 `Armed -> Reserved(PendingId)`로 바꾼다. acquisition 순서와 responsibility를 pending payload가 소유한다.
2. `primary`는 pending Error/Defect/Cancel이면 그 값으로 시작하고, pending Normal이면 비어 있다. `suppressed`는 빈 배열로 시작한다.
3. target depth 위의 cleanup stack을 registration 역순으로 drain한다. `Armed` action만 실행하고 tombstone과 `Reserved` entry는 건너뛴다.
4. 각 action failure를 원자적으로 reduce한다: `primary`가 비어 있으면 그 failure가 primary가 되고, 이미 있으면 그때만 suppressed 끝에 append한다. 같은 failure를 primary와 suppressed에 동시에 넣을 수 없다. failure payload의 ownership도 `FinalPayload`가 인수한다.
5. drain 뒤 pending family가 최종 family로 유지되면 모든 `Reserved(PendingId)` responsibility를 target block/region의 새 owner로 원자적으로 rehome한 뒤 pending payload를 해당 binder에 전달한다. Error/Defect/Cancel primary는 cleanup failure에 의해 family가 바뀌지 않는다.
6. pending Normal인데 cleanup failure가 primary가 되면 normal payload는 선택되지 않는다. reserved entry를 acquisition 역순으로 실행해 owned payload를 정리하고, 여기서 난 failure에도 4의 reducer를 적용한다. 해당 normal 값은 어떤 target parameter에도 정의되지 않는다.
7. 모든 reserved entry는 rehome 또는 실행 중 정확히 하나로 끝나야 한다. `Reserved` 상태가 남은 채 continuation을 선택하면 verifier/runtime integrity 오류다.
8. 최종 primary family에 해당하는 `LeavePlan.continuations` 하나만 선택하고, drain이 만든 `FinalPayload`를 그 continuation의 binder에 공급한다.

이 규칙은 `OP-TEMP-002`, `OP-CLEANUP-021`, `OP-FAIL-011`, `OP-LOOP-019`를 직접 구현한다.

### 9.3 suspension과 cleanup

`suspend`는 cleanup을 실행하지 않는다. active region stack, 등록 action, pending failure state를 suspend frame에 보존한다. resume은 같은 상태에서 계속한다. cancellation successor는 `leave`를 통해 동일한 cleanup 규칙을 실행한다. 따라서 suspension이 cleanup을 잃게 만들 수 없고 cancellation이 cleanup을 우회할 수도 없다.

### 9.4 assignment

`place.replace`는 다음 순서를 하나의 제어 가능한 terminator로 보장한다.

```text
place.replace %dst, consume %new
  ok                         -> bb_ok                 // dst = Initialized(new)
  error(FinalPayload.Failed) -> bb_error(%failure)    // dst = Uninitialized
  defect(FinalPayload.Failed)-> bb_defect(%failure)   // dst = Uninitialized
```

1. RHS를 완전히 평가한다.
2. 새 값과 그 cleanup responsibility를 protected temporary로 보존한다.
3. 기존 place responsibility에 봉인된 cleanup entry를 소비해 cleanup을 정확히 한 번 실행한다.
4. old cleanup이 성공한 경우에만 새 값과 handle을 place에 commit하고 success edge에서 state를 `{Initialized}`로 둔다.
5. old cleanup이 Error/Defect로 실패하면 그것을 primary로 삼고 destination은 `{Uninitialized}`가 된다. old responsibility는 호출됐으므로 종료된 것으로 본다.
6. 실패 경로에서 protected new temporary를 정리한다. 그 cleanup 실패는 old primary 뒤에 append되고, new responsibility도 종료된다.
7. error/defect successor는 최종 primary family와 `FailureBundle`을 받는다. verifier는 old failure와 그때만 실행되는 new cleanup의 reachable 조합을 계산하고, 가능한 **primary family**와 successor 집합이 정확히 일치하는지 검사한다.

단순 reusable/no-cleanup type은 canonicalization 후 total `store`로 축약할 수 있다.

### 9.5 construction

부분 초기화 aggregate는 선형 `BuilderToken`으로 표현한다.

```text
construction.begin TargetType, FieldOrder -> BuilderToken
construction.field BuilderToken, FieldId, owned_value -> BuilderToken
construction.commit BuilderToken -> constructed_value
```

`begin`은 rollback action을 현재 cleanup region에 등록하고 그 `CleanupKey`를 `BuilderToken`에 봉인한다. 각 `field`는 이전 token과 sealed entry identity를 소비하고 다음 초기화 상태를 나타내는 새 token을 반환하며 source/row 순서와 정확히 일치해야 한다. token은 xVM의 동일 builder handle을 가리킬 수 있지만 MIR에서는 SSA version이 다르다. commit 전 이탈하면 `leave`가 armed rollback entry를 실행해 완료된 field를 역순으로 정리한다. `commit`은 마지막 token과 정확한 sealed key를 `ConstructionCommitted`로 disarm하고 완성 값을 만든다. 완성 값이 resource이면 별도 lifecycle cleanup responsibility가 그 owned 값에 결합된다. verifier는 field 중복·누락·순서·key identity·token double-use를 검사한다.

### 9.6 transactional pattern binding

Pattern subject는 한 번 평가한다. 구조 test와 guard를 수행하는 동안 source place를 변경하지 않는다. 성공 block에서 모든 binding과 move를 하나의 `binding.commit` operation으로 적용한다. commit은 실패하지 않으며 모든 target place를 동시에 `Initialized`로 바꾼다. 실패 edge에는 binding이나 partial move가 없다.

## 10. async, task, actor

### 10.1 suspend

```text
suspend SuspendPointId, kind, payload
  resume(resume_value) -> bb_resume(...)
  cancel(cancel_token) -> bb_cancel(...)
```

MIR은 suspend를 `switch(state)` 함수로 전개하지 않는다. xVM suspended frame이 coroutine state record다.

```text
SuspendedFrame {
  FunctionId,
  SuspendPointId / bytecode_pc,
  atomic_state: Suspended | Resumed | Cancelled,
  SuspensionToken,
  live Value/Place slots,
  cleanup region/action stack,
  pending outcome,
  task/context/isolation state,
  root-map id,
}
```

초기 구현은 frame slot 전체를 저장해도 된다. verifier와 root map은 정확한 live-across-suspend 집합을 계산해야 한다. 이후 저장 frame을 그 집합으로 압축할 수 있다.

불변식:

- async/coroutine body 밖에는 `suspend`가 없다.
- resume 값과 resume block param type이 정확히 일치한다.
- suspend를 가로지를 수 없는 borrow/inout는 live set에 없다.
- `suspend`는 running frame ownership을 선형 `SuspensionToken`으로 바꿔 scheduler/task owner에 이전한다. resume과 cancel은 원자적 `Suspended -> Resumed | Cancelled` compare-and-transition 중 정확히 하나만 성공시키고 token을 소비한다.
- double resume, resume/cancel 경합의 패자, token 유실은 source outcome을 두 번 실행하지 못하며 xVM integrity defect가 된다. owner가 frame을 버리려면 cancel/close 경로를 선택해 `leave`로 cleanup을 끝내야 한다. GC는 live token이 결합된 frame을 finalization 없이 폐기할 수 없다.
- cancel은 suspend 시점의 resource, task, cleanup responsibility를 정확히 한 번 종료한다.
- `yield value -> $response`는 suspend/resume 후 ordinary binding commit으로 이어진다.
- 별도 generator close 의미가 필요하면 Cancellation과의 관계를 먼저 법으로 닫고 feature를 추가한다.

### 10.2 task

`task.spawn`은 owned `TaskToken`을 만든다. lexical task scope를 나갈 때 모든 owned child token은 `join`, `cancel_then_join`, 또는 명시적 transfer 중 하나로 끝나야 한다. task scope 종료가 suspend할 수 있으므로 task operation은 terminator다. cleanup region과 task scope의 상대 순서는 CFG에 명시하며 runtime 관례로 추측하지 않는다.

### 10.3 actor

Actor operation은 일반 method call이 아니다.

```text
actor.send / actor.request / actor.receive {
  actor_id,
  protocol_id,
  sender_channel,
  mailbox_profile,
  message_type,
  payload,
  observation_site,
}
```

capacity, protocol, cancellation, suspension 가능성에 따라 명시적 successor를 가진다. xVM은 같은 sender/receiver channel에서 enqueue 순서를 보존한다. 서로 다른 sender 사이의 전역 순서나 scheduler fairness는 MIR이 고정하지 않는다.

## 11. effect, authority, provider

Function signature에는 normalized `EffectRow`, `ErrorSet`, `DefectSet`, cancellation capability, suspension capability, isolation, authority requirement가 들어간다. effect, failure, suspension, allocation은 서로 배타적인 enum이 아니므로 각 operation/terminator는 직교 profile을 가진다.

```text
OpProfile {
  effects: EffectRow,
  error_set: ErrorSet,
  defect_set: DefectSet,
  cancellation_point: CancellationPointId?,
  may_suspend: bool,
  may_allocate: bool,
  may_collect: bool,
  observable: bool,
}
```

`PureTotal`은 `effects/error_set/defect_set`이 비고 cancel/suspend/allocate/collect/observable이 모두 false인 profile에서 파생되는 판정이다. 실패 가능한 profile은 반드시 명시적 successor를 가진 terminator여야 한다. Stateful이면서 실패하거나, observable이면서 suspend하는 등의 조합도 이 record 하나로 표현한다.

Operation 순서와 CFG edge가 effect 순서를 결정하므로 별도 world token은 두지 않는다. 파생 판정 `PureTotal`만 제한적으로 CSE/reorder할 수 있다. Error/Defect/Cancel 가능성은 첫 실패와 관찰 순서를 바꾸므로 barrier로 취급한다.

Dynamic provider operation은 적어도 다음을 정적/명시적 operand로 가진다.

- `ProviderId`와 version
- observation timestamp
- rounding policy
- failure/effect policy
- cache key
- replay token
- observation site

Provider를 runtime 이름으로 재검색하지 않는다. 같은 replay token의 trace identity를 보존한다.

## 12. 메모리 관리와 safepoint

현재 Deeplus 법은 특정 GC, RC, arena, object header, weak-reference 정책을 정하지 않는다. MIR-X1도 이를 언어 의미로 고정하지 않는다.

다만 xVM이 tracing/moving collector를 선택해도 안전하도록 다음 실행 메타데이터를 지원한다.

- xVM type layout은 `none`, `managed`, `aggregate(mask)` 같은 trace class를 제공한다.
- 모든 MIR operation/terminator와 xVM runtime intrinsic은 닫힌 `may_collect` 속성을 가진다. `may_collect=true`이면 `SafepointId`와 root map이 반드시 있어야 하고, `false`이면 그 instruction 실행 중 collector 진입이나 GC callback을 금지한다.
- 초기 X1에서는 allocation, 모든 call, suspend, actor/task runtime 진입, 명시적 `gc_poll`을 보수적으로 `may_collect=true`로 둔다. 이후 `no_collect`를 증명하더라도 signature와 loader 검증 없이 생략할 수 없다.
- `SafepointId -> RootMap`은 MIR liveness와 xVM slot allocation에서 파생한다.
- root에는 live managed value slot, initialized managed Place, cleanup capture, pending outcome, closure environment, suspended frame이 포함된다.
- derived root map은 semantic digest에 포함하지 않으며 loader/verifier가 재계산해 대조한다.
- moving collector에 대비해 field borrow는 `base handle + projection`이며 raw interior address가 아니다.
- resource cleanup은 collector finalization으로 대체할 수 없다.

GC safepoint와 cancellation 전달점은 분리한다. `gc_poll`을 추가하거나 이동해도 cancellation 관찰 시점이 바뀌면 안 된다. Cancellation은 `cancel_check` 또는 signature가 cancellable인 `suspend`/task/actor terminator처럼 `CancellationPointId`를 가진 지점에서만 전달한다. 모든 cancellation point는 cancel successor를 가지며, `gc_poll` 자체는 cancellation point가 될 수 없다.

`OpProfile.cancellation_point != none`과 cancel successor 존재는 iff 관계다. cancellable `invoke`도 call-site `CancellationPointId`를 반드시 가지며, non-cancellable signature/operation에는 둘 다 없어야 한다. ID는 canonical operation encounter order로 부여한다.

OOM과 stack exhaustion이 Deeplus Defect인지 xVM-fatal인지 법이 닫히기 전에는 recoverable edge를 추정하지 않는다.

## 13. Verifier

Verifier는 다음 순서로 fail-closed 검증한다.

| 단계 | 검증 내용 |
|---|---|
| 1. Envelope | magic, schema version, feature set, section length/count, integer overflow, resource limit |
| 2. Identity | ID 범위와 domain, 중복 없음, authority digest, unresolved lookup 없음 |
| 3. CFG | entry 존재, block reachability, terminator 1개, successor 유효성, switch 중복 없음 |
| 4. SSA | 통합 ValueId 단일 정의, dominance, block-argument arity/type/mode, simultaneous edge transfer |
| 5. Types | operation signature, normalized exact type, no implicit subtype/coercion/widening |
| 6. Place | move-path product state의 transfer/join/refinement, projection origin, replace edge typestate |
| 7. Ownership | edge의 copy/consume/view 방식, LoanId-view-token 결합, base alias, raw CleanupKey edge 금지, owned/call-right/token 선형성 |
| 8. Outcome | ErrorSet/DefectSet/CancellationPoint와 edge iff, `LeavePlan` dynamic binder, abandoned normal payload 정리, handler family 분리 |
| 9. Cleanup | region nesting, continuation 완전성, key seal/pin/disarm producer, tombstone, effect/error/derived-defect budget, non-suspend/non-cancel, LIFO/suppression |
| 10. Transaction | binding/construction commit 또는 rollback의 exactly-once 종료 |
| 11. Async/actor/task | suspend live set, resume type, atomic SuspensionToken 소비, borrow escape, task token, isolation, channel identity |
| 12. Effects | body effect/error/defect/cancel/authority가 signature 범위 안, OpProfile 직교성, pure profile 위반 없음 |
| 13. Safepoint | 모든 `may_collect` site의 mandatory safepoint, live managed root, raw/interior reference 금지, exact root map 대조 |
| 14. Canonical form | table/order/ID/encoding이 유일한 canonical form인지 확인 |

검증기는 결정적인 첫 오류를 `(diagnostic_id, function_id, block_id, op_index, provenance)`로 반환한다. hash iteration order나 thread scheduling이 오류 순서를 바꾸면 안 된다.

Block-entry type/place/region state certificate를 artifact에 캐시할 수 있지만 신뢰 근거로 사용하지 않는다. xVM loader는 전이 규칙으로 다시 계산한다. MIR verifier와 XBC verifier는 별도여야 한다.

## 14. xVM 투영 계약

이 RFC 내부의 xVM-only 대안을 채택한다는 조건 아래, MIR-X1의 기계적 투영 계약을 다음과 같이 제안한다. 이는 현행 LLVM preservation authority를 변경하지 않는다.

### 14.1 함수 frame

xVM 함수 frame은 load 시점에 크기가 닫힌다.

```text
FrameLayout {
  value_slots: ValueId -> SlotId,
  place_slots: PlaceId -> SlotRange,
  token_slots: linear token -> SlotId,
  edge_scratch: max successor argument tuple,
  cleanup_stack_handle,
  context/isolation slots,
}
```

- 초기 구현은 각 MIR value/block-param/place에 독립 slot을 준다.
- branch는 모든 `EdgeArg`를 `edge_scratch`에 읽은 뒤 successor slot에 동시에 쓴다.
- `consume`은 source slot을 moved 상태로 만들고, `copy`는 reusable 값만 복제한다.
- frame slot 재사용은 MIR liveness와 ownership 검증 뒤의 비관찰 최적화다.
- xVM operand stack은 opcode 내부 임시 계산에만 쓸 수 있으며 block 경계를 가로지르는 의미 상태가 아니다.

### 14.2 instruction과 control lowering

각 MIR operation은 타입이 고정된 xVM instruction 또는 identity가 고정된 runtime intrinsic 하나로 내려간다. 각 terminator는 명시적인 bytecode PC successor table을 가진다. lowering은 overload, witness, extension, label, provider, handler를 다시 검색하지 않고, failure edge를 합치거나 새로 만들지 않는다.

```text
Verified<ProposedMirX1>
  -> emit_canonical_xbc
  -> XbcCandidate { mir_semantic_digest, canonical_payload, xbc_digest }
  -> verify_projection(Verified MIR, XbcCandidate)
  -> VerifiedProjection<Xbc>
  -> verify_xbc_loader
  -> LoadedXbc
  -> execute
```

`leave`, `suspend`, task/actor/provider, safepoint는 xVM runtime instruction으로 보존한다. host call stack unwind, Rust panic, GC finalizer, 암시적 scheduler hook으로 대체하지 않는다.

`verify_projection`은 digest 두 개가 각각 맞는지만 보지 않는다. verified MIR에서 frame layout, typed instruction, successor table, cleanup/suspend/root-map metadata를 결정적으로 다시 방출하고 XBC의 canonical executable payload와 byte-for-byte 비교한다. 따라서 `return 0` MIR digest에 `return 1` XBC를 붙인 artifact는 각 hash가 맞아도 거부된다. 실행 API와 receipt writer는 `VerifiedProjection<Xbc>` 이후 타입만 받는다.

portable XBC bundle은 canonical `.dmir.cbor` bytes를 내장하거나 그 bytes를 얻을 수 있는 content-addressed reference를 가진다. loader가 digest에 해당하는 verified MIR을 확보하지 못하면 실행을 거부한다. `.dmir.cbor` 자체도 직접 실행하지 않는다. “direct MIR→xVM”은 optimizer를 거치지 않는다는 뜻일 뿐, in-memory canonical XBC 방출·projection 검증·loader 검증을 우회한다는 뜻이 아니다.

### 14.3 loader와 실행 oracle

xVM loader는 XBC를 불신하고 다음을 독립적으로 다시 검증한다.

- embedded/content-addressed MIR의 canonical bytes와 `mir_semantic_digest`
- 결정적 재방출 XBC와 artifact executable payload의 byte equality
- opcode operand/result slot kind와 초기화 상태
- branch target의 block-entry frame state
- successor tuple의 arity/type/transfer mode
- cleanup depth와 `LeavePlan` continuation table
- cancellation/suspend/safepoint metadata
- 재계산한 root map과 artifact root map
- XBC canonical payload와 domain-separated XBC digest

실행 oracle은 최종 `Outcome`, ordered observation trace, place/cleanup balance, provider replay identity를 receipt로 낸다. 따라서 MIR conformance는 “bytecode가 실행됐다”가 아니라 같은 semantic digest에 대해 이 관찰들이 일치한다는 것으로 판정한다.

## 15. 결정적 직렬화와 digest

두 표현을 둔다.

- `.dmir`: 사람이 읽고 diff할 수 있는 canonical text
- `.dmir.cbor`: cache, receipt, XBC projection 검증 입력용 deterministic CBOR profile. 그 자체는 실행 형식이 아니다.

CBOR profile 규칙:

1. array와 작은 정수 field tag를 우선 사용한다.
2. 정수, 길이, tag는 shortest form만 허용한다.
3. indefinite-length item을 금지한다.
4. map이 필요한 경우 encoded-key byte 순서로 정렬한다.
5. float constant는 NaN payload와 signed zero를 보존하기 위해 고정폭 IEEE bit string으로 저장한다.
6. unknown mandatory field/feature는 거부한다.
7. `encode(decode(bytes)) == bytes`가 아니면 noncanonical encoding으로 거부한다.

Canonical numbering:

- static identity는 authority가 정한 fully-qualified identity kind/name/signature key, constant는 `(TypeId, canonical payload bytes)`, type은 `(kind, nominal identity, canonical child keys)`로 정렬한다. 같은 key의 동일 entry는 intern하고, 같은 key인데 bytes가 다르면 tie-break하지 않고 canonicalization 오류로 거부한다.
- X1의 recursive type은 nominal `StaticIdentity`를 통해서만 cycle을 만들 수 있다. anonymous structural recursive SCC는 feature로 닫히기 전까지 거부하므로 입력 순서에 의존한 SCC numbering이 없다.
- function은 body와 무관한 `(FunctionId static key, canonical MirSignature)`로 정렬한다.
- terminator successor 순서는 schema가 다음처럼 고정한다: `br`; `cond_br[true,false]`; `switch_enum[canonical tag...,default]`; `switch_int[numeric key ascending...,default]`; `invoke[ok,error,defect,cancel]`; `checked[ok, reason-tag ascending]`; `place_replace[ok,error,defect]`; `leave[normal,error,defect,cancel]`; `suspend[resume,cancel]`; `cancel_check[continue,cancel]`. task/actor/provider 결과는 opcode schema의 numeric outcome tag 순서다. 존재하지 않는 family는 건너뛰되 상대 순서는 바꾸지 않는다.
- entry에서 위 successor order로 DFS한 reverse-postorder를 block order로 쓴다. unreachable block은 제거한다.
- function parameter place는 signature 순서, 나머지 place는 canonical block/op traversal의 최초 정의 site와 result ordinal 순서다. cleanup region은 parent-first이며 sibling은 최초 `region_enter` encounter 순서다.
- block parameter와 operation result는 canonical traversal 순서로 하나의 `ValueId` 공간에 번호를 준다. `LoanId`, `CheckSiteId`, `SuspendPointId`, `CancellationPointId`, semantic observation site는 각 producer의 encounter 순서로 번호를 준다.
- table/ID 종류에 위 규칙이 없거나 동률이 해소되지 않으면 serializer가 입력 collection iteration order를 쓰지 않고 거부한다.

semantic projection은 schema/authority/features, canonical type·identity·constant table, **전체 function signature와 body**, ownership/loan/cleanup/operation profile, 의미적으로 관찰되는 site를 포함한다. source path/span/local spelling/inline scope와 derived frame/root map은 `DebugProjection` 또는 XBC projection으로 분리한다.

digest preimage와 framing을 정확히 고정한다.

```text
XbcCanonicalPayloadWithoutDigest = [
  xbc_schema_version,
  mir_semantic_digest,
  feature_set,
  canonical_constant_pool,
  function_frame_tables,
  typed_instruction_streams,
  successor_tables,
  cleanup_tables,
  suspend_and_cancellation_tables,
  safepoint_root_maps,
]

semantic_bytes = deterministic_cbor(
  SemanticMirProjection(ProposedMirX1)
)

semantic_digest = SHA-256(
  utf8("deeplus.mir.semantic/x1\0") || u64be(len(semantic_bytes)) || semantic_bytes
)

variant_content_digest = SHA-256(
  utf8("deeplus.mir.variant/x1\0") ||
  u64be(len(variant_semantic_bytes)) || variant_semantic_bytes
)

debug_bytes = deterministic_cbor(DebugProjection)
debug_digest = SHA-256(
  utf8("deeplus.mir.debug/x1\0") || semantic_digest ||
  u64be(len(debug_bytes)) || debug_bytes
)

xbc_payload = deterministic_cbor(XbcCanonicalPayloadWithoutDigest)
xbc_digest = SHA-256(
  utf8("deeplus.xbc/x1\0") || u64be(len(xbc_payload)) || xbc_payload
)
```

`xbc_digest`는 payload 밖 envelope field에 저장하거나, encoding 시 명시적으로 제외되는 field여야 한다. 자기 digest를 preimage에 넣지 않는다. decoder는 canonical payload bytes를 재생성해 digest를 대조한다.

timestamp, absolute path, process address, hash seed, thread count, derived frame/root map은 semantic bytes에 들어가지 않는다. xVM 실행 receipt는 `semantic_digest`, `xbc_digest`, 최적화가 승인된 경우 `source_semantic_digest`와 `variant_content_digest`를 함께 기록한다.

## 16. 최적화 경계

초기에는 무최적화 `Verified MIR → canonical in-memory XBC → projection verify → loader verify → xVM`만 실행한다. 다음 pass는 pass별 equivalence verifier가 생긴 뒤에만 후보가 된다.

- `PureTotal` constant folding
- copy propagation
- block parameter simplification
- unreachable successor 제거
- 동일 의미의 switch compaction
- ownership 검증 후 frame slot reuse

다음 변환은 금지한다.

- 효과·실패·cleanup·provider·message·suspend·cancel check의 재배열
- speculative evaluation
- fallback/guard arm 선실행
- checked arithmetic을 unchecked로 교체
- runtime witness/extension/provider 재탐색
- tail-call을 source/MIR callable kind로 승격
- JIT guard, patch point, inline cache, deopt/side exit
- GC poll을 cancellation poll로 사용

Dead-code elimination은 값이 사용되지 않는다는 사실만으로 허용하지 않는다. operation이 `PureTotal`, non-allocating, non-cleanup, non-authority임을 증명해야 한다.

## 17. 기존 Deeplus 법과 MIR-X1 대응

| 법/의미 | MIR-X1 구성 |
|---|---|
| `OP-EVAL-001` | block operation 순서, ordered operand vector, explicit edge |
| `OP-TEMP-002` | cleanup registration order와 `leave` LIFO drain |
| `OP-ASSIGN-003` | RHS 이후 `place.replace` commit |
| `OP-CONSTRUCT-004` | linear `BuilderToken`, field order, rollback action |
| `OP-OPTION-006`, `028` | `switch_enum`; none edge만 fallback CFG에 도달 |
| `OP-INIT-009` | static initializer dependency DAG와 one-shot commit |
| `OP-FAIL-011` | typed primary outcome + ordered suppressed list |
| `OP-CANCEL-012` | 별도 Cancel edge와 `leave` |
| `OP-TASK-013` | linear `TaskToken`과 scope-exit join/cancel |
| `OP-ACTOR-014`, `029` | actor channel identity와 enqueue order |
| `OP-NUMERIC-015` | width/mode별 checked terminator, no hidden widening |
| `OP-NUMARR-016` | shape check edge와 explicit allocation/authority site |
| `OP-GUARD-017` | structural test→guard→binding commit CFG |
| `OP-LOOP-019` | target depth를 가진 `leave`와 final handler edge |
| `OP-CALLABLE-020` | closure environment/profile/call-right token |
| `OP-CLEANUP-021` | 일반 call과 분리된 cleanup registration/entry |
| `OP-EVIDENCE-022` | `WitnessId`가 고정된 `CalleeRef` |
| `OP-NAMED-REST-023` | static `CallShape.named_tail`과 `Record***` residue |
| `OP-RIGHTWARD-BIND-024` | 별도 op 없음; ordinary initializer + binding commit |
| `OP-RAW-STRING-025` | exact scalar `ConstString`; raw 여부는 provenance |
| `OP-DYNAMIC-UNIT-027` | fully bound provider/policy/replay operation |

## 18. 닫히지 않은 의미의 처리

현재 문서가 명시적으로 보류한 의미를 MIR opcode로 추정하지 않는다. 해당 feature bit는 verifier가 거부한다. 다음 표는 새 P1을 만들거나 기존 P1을 폐쇄하지 않는 제안 내부의 deferred inventory다.

| Deferred meaning | Owner | Closure method / trigger | Status |
|---|---|---|---|
| Char/Bytes runtime representation과 conversion | Spec_ | normative value·conversion law와 Test_ oracle을 Design_이 수용 | DEFERRED |
| strict/sequential Boolean 세부 관찰 | Spec_ | evaluation/short-circuit law와 boundary test 확정 | DEFERRED |
| ternary arm semantics | Spec_ | typing·evaluation·ownership law와 negative test 확정 | DEFERRED |
| interpolation rendering/provider/failure | Spec_ | provider identity, effect/failure law 및 Impl_/Test_ evidence 확정 | DEFERRED |
| NumericArray transpose의 view/copy/ownership | Spec_ | representation-independent ownership law와 observable test 확정 | DEFERRED |
| catch pattern과 `finally`의 완전한 outcome 결합 | Spec_ | outcome composition law 및 cleanup/error matrix 확정 | DEFERRED |
| OOM/stack exhaustion | Impl_ | runtime failure boundary와 Design_ observable policy 확정 | DEFERRED |
| generator close와 Cancellation의 관계 | Spec_ | close/cancel/cleanup ordering law와 Test_ trace oracle 확정 | DEFERRED |
| GC/RC/arena 선택과 weak reference | Impl_ | memory-model boundary와 Design_ observation rule 확정 | DEFERRED |
| 전역 actor ordering과 scheduler fairness | Spec_ | concurrency observation law와 Test_ schedule oracle 확정 | DEFERRED |

새 의미가 승인될 때는 type rule, MIR operation/edge, verifier rule, xVM trace oracle가 함께 추가되어야 한다. opcode만 먼저 예약하지 않는다.

## 19. 채택 시 예상되는 정본 delta (현재 미적용)

이 RFC를 향후 별도 authority로 채택하려면 최소한 다음 prospective delta를 함께 판정해야 한다.

1. [management policy](../governance/policies/management-policy.yaml)의 현행 `initial_native_backend: LLVM AOT` 및 `later_native_backend: LLVM ORC JIT` 계약을 유지할지, xVM-only로 수정할지 명시적으로 판정한다.
2. [MIR 의미 문서](../spec/mir/semantics.md)의 “ordered operand stack”을 **ordered operation stream + explicit operand vectors + xVM frame slots**로 명확히 한다. persistent operand-stack merge는 MIR 의미가 아니다.
3. 같은 문서의 현행 xVM·LLVM preservation law를 변경하려면 Spec_ 계약과 Design_ authority를 별도로 확정한다.
4. Deeplus 0.1.3이 확립된 뒤에만 `current/language-version.toml`의 `mir_schema`를 `deeplus.mir/x1`로 배정할 수 있다.
5. 기존 MIR responsibility/RCTS event 스키마를 executable MIR가 아니라 deterministic trace projection으로 분류한다.
6. MIR receipt가 `semantic_digest`, authority digest, feature set, xVM artifact digest를 함께 기록하도록 한다.
7. 채택된 canonical target, authority map, source-tree manifest와 current-integrity projection을 승인된 generator로 함께 재생성·검증한다.

이 목록은 prospective adoption delta일 뿐 write authority가 아니다. 이 문서는 현재 정본 파일을 직접 변경하거나 변경을 승인하지 않는다.

## 20. 향후 구현 의존성과 종료 조건 (현재 미승인)

아래는 조직 역할이나 일정이 아니라 MIR capability 의존성만 정의한다. X1-A..X1-E는 모두 `NOT_AUTHORIZED / NOT_RUN`이며, Deeplus 0.1.3 확립과 별도 Design_ implementation authority 전에는 시작할 수 없다.

### X1-A — Core form

- Module/Function/Block/Value/Place/BlockParam Rust 타입
- canonical text와 deterministic CBOR
- envelope/CFG/type/SSA verifier

종료 조건: round-trip canonical bytes, malformed corpus 전부 거부, hash seed/OS/thread 수를 바꿔도 같은 digest.

### X1-B — Scalar control와 outcome

- branch/switch/invoke/checked/complete
- local binding, Option coalescing, checked numeric
- static CallShape와 CalleeRef
- fixed-frame xVM instruction/successor 투영과 독립 XBC loader verifier

종료 조건: 좌→우 한 번 평가, fallback suppression, error/defect/cancel edge가 golden MIR과 xVM trace에서 구별되고, 변조된 slot/target/transfer metadata를 loader가 전부 거부함.

### X1-C — Place, ownership, cleanup

- move path, borrow/inout token, replace
- cleanup region/register/leave
- construction/binding transaction

종료 조건: use-after-move, overlapping inout, borrow escape, double cleanup, cleanup budget 초과, primary replacement, partial construction mutant를 모두 verifier/trace가 검출.

### X1-D — Closure와 suspension

- closure capture/call-right
- suspend/resume/cancel frame metadata
- live-across-suspend와 safepoint root map

종료 조건: invalid borrow across suspend, double once-call, lost cleanup, missing live root가 모두 거부됨.

### X1-E — Task, actor, provider, domain operation

- structured TaskToken
- actor channel/protocol operation
- provider replay operation
- 승인된 NumericArray/measure operation

종료 조건: task leak, sender/receiver FIFO reversal, hidden provider lookup, shape/effect omission mutant가 모두 검출됨.

## 21. 최종 채택 기준

MIR-X1 설계는 다음을 모두 만족할 때 채택할 수 있다.

- current constitutional law마다 MIR 구성 또는 명시적 pre-MIR/no-op 경계가 있다.
- accepted MIR에 unresolved name/label/witness/extension/provider lookup이 없다.
- xVM은 verified MIR을 고정 frame slot과 명시적 runtime operation으로 기계적으로 투영할 수 있다.
- cleanup, failure, cancellation, suspension을 host exception이나 GC finalizer에 맡기지 않는다.
- verifier가 CFG/type/ownership/place/cleanup/outcome/async를 실행 전에 증명한다.
- 같은 normalized MIR은 byte-for-byte 동일하게 직렬화된다.
- 기존 event schema는 MIR 자체가 아니라 MIR 실행 trace receipt로 생성된다.
- 아직 닫히지 않은 언어 의미에 opcode나 표현을 추정하지 않는다.

이 기준에서 가장 중요한 선택은 **블록 인자 기반 SSA 값과 Place를 함께 쓰는 것**, **cleanup과 suspend를 xVM frame의 직접 의미로 유지하는 것**, **네 가지 정상/비정상 outcome을 명시적 edge로 분리하는 것**이다.
