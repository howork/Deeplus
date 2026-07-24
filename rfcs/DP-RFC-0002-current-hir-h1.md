# DP-RFC-0002 — 현행 Deeplus용 Typed HIR-H1 설계

## Metadata

| Field | Value |
|---|---|
| Status | `DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE` |
| Inspected baseline | `howork/Deeplus@8aba9942b3e897f95397e8f32bd28bb2b859552e` |
| Live input snapshot | 위 baseline 위의 2026-07-24 로컬 working-tree 계약 변경 포함 |
| Scope | CST/AST와 MIR 사이의 Deeplus HIR 자료구조, 단계 경계, 불변식, 검증 및 결정적 직렬화 |
| Current authority | [`spec/language.md`](../spec/language.md), [`spec/frontend/frontend-model.json`](../spec/frontend/frontend-model.json), [`spec/types/type-system.md`](../spec/types/type-system.md), [`spec/mir/semantics.md`](../spec/mir/semantics.md) |
| Compatibility target | 현행 Deeplus 의미 계약과 비정본 [`DP-RFC-0001 ProposedMirX1`](./DP-RFC-0001-xvm-only-mir.md) |
| Proposed schema | `deeplus.hir/h1` |
| Target language version | `0.1.2-internal` |
| Target spec revision | `r51f3-current-exact-numeric-hir-h1-coherence-r1` |
| Tracking issue | `TBD` |
| Supersedes | None |
| Created | 2026-07-24 |

## Authority fence

- 이 문서는 **설계 제안**이다. 현재 언어 정본, 구현 상태, 제품 lane, backend 권위를 변경하거나 활성화하지 않는다.
- 현재 [`implementation-status.yaml`](../current/implementation-status.yaml)의 `rust_hir_lowering`, `rust_integrated_checker`, `deeplus_mir_lowering`은 모두 `NOT_RUN`이다. 이 문서는 그 상태를 구현 완료로 승격하지 않는다.
- 현재 [`language-version.toml`](../current/language-version.toml)에는 HIR schema authority가 없다. `deeplus.hir/h1`은 제안 이름일 뿐 배정된 정본 schema가 아니다.
- 이 설계는 조직 역할, 담당자, 일정, 승인 절차를 배정하지 않는다. 오직 HIR의 의미·자료구조·검증 경계만 다룬다.
- 이 문서를 작성하면서 기존 정본 및 현재 미커밋 변경 파일은 수정하지 않는다.
- 본 설계는 LLVM, Cranelift 또는 특정 native backend의 자료구조를 HIR에 도입하지 않는다. HIR-H1은 backend-neutral한 고수준 의미 계약이며, 실행 권위는 검증된 MIR 이후에만 생긴다.

## 1. 결론

현행 Deeplus에 가장 적합한 HIR은 다음 성격을 갖는다.

> **소스 구조를 진단 가능한 수준으로 보존하되, 모든 정적 선택·정규화 타입·책임·평가 계획이 닫혀 있고, CFG·SSA·xVM 배치를 아직 만들지 않은 owner/body 기반 typed arena**

이 문서에서는 이를 **HIR-H1**이라 부른다.

HIR-H1은 하나의 느슨한 트리에 `phase` 플래그를 붙인 형식이 아니다. 분석 중간 상태와 MIR 입력 권위를 Rust 타입 수준에서 분리한다.

```text
Lossless CST
  -> Normalized AST
  -> HirSkeleton                 // sugar 제거, scope/item 골격, generated decl
  -> CheckSession               // 이름 해석·호출 선택·추론·책임 검사를 상호 질의
  -> TypedHirDraft              // 선택은 닫혔지만 canonical/verified 전
  -> canonicalize + verify
  -> Verified<CanonicalHirH1>
  -> require_mir_capabilities
  -> ExecutableHirH1
  -> MirDraft
  -> canonicalize + verify
  -> Verified<ProposedMirX1>
```

IDE 복구용 `AnalysisHir`에는 missing node, error type, unresolved candidate가 있을 수 있다. 그러나 `CanonicalHirH1`, `ExecutableHirH1`, serializer와 MIR lowerer에는 그런 variant가 **자료형 자체에 존재하지 않아야 한다**.

핵심 분업은 다음과 같다.

| 단계 | 보존하는 것 | 만들지 않는 것 |
|---|---|---|
| CST | token, trivia, recovery, 원래 spelling | 의미 identity, type |
| AST | 정규화된 구문 의미와 문법 단계 enum | overload 선택, ownership plan |
| HIR-H1 | generated declaration, 정적 identity, 완결 타입·책임, 구조화된 실행 계획 | CFG, SSA, frame slot, root map |
| MIR-X1 | 평가 순서의 실행 형식, CFG, Value/Place, loan/token, cleanup/outcome/suspend | 이름·overload·witness·extension 재탐색 |
| xVM | 검증된 MIR의 frame/instruction 투영 | 언어 의미 재결정 |

## 2. 현행 저장소에서 확인한 출발점

### 2.1 정본이 이미 HIR에 요구하는 책임

현행 frontend 모델과 언어 문서는 HIR를 단순 typed AST wrapper로 취급하지 않는다. HIR가 담당해야 하는 의미는 이미 다음과 같이 흩어져 있다.

- generated declaration 생성
- property, forwarding, comprehension, loop 정규화
- actor/protocol 및 structured task scope identity
- module, declaration, member, label, associated item, witness, extension, provider entry identity
- rightward binding을 checker 전에 ordinary `let`/`var`로 정규화
- 모든 call/member/evidence 선택을 닫은 descriptor를 MIR로 전달
- pattern의 test/probe/guard/atomic commit 계획
- construction, cleanup, capture, suspension, message transfer 책임

따라서 HIR-H1은 AST를 꾸미는 부가 테이블이 아니라 frontend 의미의 닫힌 산출물이어야 한다.

### 2.2 현행 구현 scaffold의 한계

현재 scaffold는 개념적으로 다음 순서다.

```text
lexer -> parser -> AST -> deeplus-types::check(AST)
      -> deeplus-hir::lower(TypedCase) -> deeplus-lowering -> MirPlan
```

현행 [`deeplus-hir`](../crates/deeplus-hir/src/sfd_p1_009.rs)의 `HirCase`는 fixture용 `TypedCase`, 문자열 `operation_id`, 문자열 ownership mode, unresolved lookup count만 가진다. 실제 item/body tree, identity domain, source origin, call/pattern/cleanup plan은 없다.

장기 구조에서는 검사 전에 HIR 정규화가 필요하므로 `AST -> checker -> HIR` 순서를 유지할 수 없다. 또한 현재 `deeplus-types`가 AST fixture에 직접 의존하고 `deeplus-hir`가 다시 types에 의존하므로 checker를 HIR 입력으로 옮기면 crate cycle이 생긴다.

제안 의존 구조는 다음과 같다.

```text
deeplus-cst / deeplus-ast
            |
            v
       deeplus-hir  <------ deeplus-types
            |                   ^
            +----> deeplus-checker
                         |
                         v
              Verified<CanonicalHirH1>
                         |
                         v
                 deeplus-lowering
                         |
                         v
                       MIR-X1
```

- `deeplus-types`는 AST fixture 의존을 제거하고 normalized type/responsibility algebra만 소유한다.
- `deeplus-hir`는 AST lowering, HIR 자료형, owner/body arena, canonicalizer/verifier 인터페이스를 소유한다.
- `deeplus-checker`는 HIR와 types에 의존해 resolution, inference, admission, coherence, exhaustiveness를 수행한다.
- `deeplus-lowering`는 오직 `ExecutableHirH1`을 입력으로 받는다.

이는 구현 제안이며 현재 crate 추가를 승인하는 문장이 아니다.

### 2.3 live working-tree 입력 경계

본 RFC가 검사한 주요 live 파일의 SHA-256은 다음과 같다.

| Input | SHA-256 |
|---|---|
| `spec/language.md` | `148548c4d68e3c6b3848489f51c21b335e279ca469935348f36f7df5a3f3f480` |
| `spec/frontend/frontend-model.json` | `2332dff3c8181c0238182a3fd12cde441fa7d9970ed2bc0107bc5d299ea8e334` |
| `spec/types/type-system.md` | `8dded232a35c3d0b2766ccc45b29841f3321d2ec9da2fd964e23ee03a3bfb8f1` |
| `spec/mir/semantics.md` | `e60da014578168eaade01b3846510cddb0f16a9dc7ad6e324a55fae3b995794a` |
| `spec/contracts/type-flow-callable-coherence.json` | `8f90d3752d74be8ccad649d8250dde5f36e8ccfb9afa5d8ba838be1f92cb6749` |
| `spec/contracts/actor-concurrency-coherence.json` | `dc0442099982fa81089f3602f439507347baa911c4a2d500710da20007fea627` |

이 중 일부는 `current/authority-map.yaml`이 기록한 commit 기준 digest와 다르다. 특히 ordered trailing closure와 actor message payload 계약은 live working tree의 미커밋 입력이다. 따라서 이 RFC를 나중에 채택 후보로 삼을 때는 해당 변경이 정본에 들어갔는지 먼저 재검증해야 한다.

## 3. 설계 목표와 비목표

### 3.1 목표

1. 모든 lexical·nominal·extension·witness·actor·provider 선택을 HIR에서 한 번만 닫는다.
2. 모든 식과 binder에 normalized type과 직교적인 responsibility를 제공한다.
3. source evaluation order와 formal binding order를 분리하여 exactly-once를 보존한다.
4. pattern, construction, cleanup, task/message의 transactional 경계를 구조화된 plan으로 보존한다.
5. MIR lowerer가 의미를 새로 결정하지 않고 CFG/SSA/Place/token으로 기계적으로 전개하게 한다.
6. item header와 body를 분리하여 body 변경이 무관한 item/body를 무효화하지 않게 한다.
7. semantic origin과 debug origin을 분리해 generated node의 안정적 identity와 정확한 진단을 함께 얻는다.
8. 같은 normalized 의미가 같은 canonical bytes와 semantic digest를 만들게 한다.
9. 현재 의미 전체를 표현하는 HIR과 현재 MIR가 실제로 실행할 수 있는 HIR의 capability 경계를 분리한다.

### 3.2 비목표

- basic block, phi/block parameter, SSA `ValueId`
- MIR `PlaceId`, `LoanId`, `AccessToken`, `CleanupKey`
- xVM frame slot, bytecode opcode, object layout, root map
- optimizer 전용 canonicalization
- unresolved name, overload candidate set 또는 inference variable의 영구 직렬화
- IDE recovery tree를 실행 artifact로 승격
- backend별 ABI 또는 native IR 표현
- provider가 HIR/MIR node나 authority/witness를 직접 주입하는 확장점

## 4. 선행 사례에서 채택한 원칙

인터넷 탐색은 backend 구현이 아니라 frontend/HIR 경계를 다룬 공식 자료에 한정했다.

| 선행 사례 | 확인한 원칙 | Deeplus 채택 |
|---|---|---|
| [rustc HIR](https://rustc-dev-guide.rust-lang.org/hir.html) | 파싱·확장·이름 해석 뒤의 compiler-friendly AST, 일부 sugar 제거, owner/local ID, item/body 분리 | owner/body arena, 정적 ID와 body-local ID 분리, incremental query 경계 |
| [rustc THIR](https://rustc-dev-guide.rust-lang.org/thir.html) | type checking 뒤 모든 타입을 채우고 자동 ref/deref, method/overload, destruction scope를 명시하여 MIR 생성에 사용 | Deeplus canonical HIR를 fully typed/resolved MIR 입력으로 정의 |
| [rust-analyzer architecture](https://rust-analyzer.github.io/book/contributing/architecture.html) | syntax는 의미를 갖지 않는 value tree, HIR은 fully resolved view, body 내부 변경이 global derived data를 무효화하지 않음 | CST/AST와 semantic HIR 분리, header/body별 query와 digest |
| [Swift compiler architecture](https://www.swift.org/documentation/swift-compiler/) | parsed AST를 fully type-checked AST로 만든 뒤 raw high-level IR로 낮추고 mandatory verification을 거쳐 canonical form으로 전환 | `TypedHirDraft -> canonicalize + verify -> CanonicalHirH1` 단계 분리 |
| [Kotlin K2](https://kotlinlang.org/docs/k2-compiler-migration-guide.html) | call resolution·type inference·semantic analysis가 풍부한 통합 frontend 자료구조를 공유 | 별도 분석 결과를 문자열 side table로 흩뜨리지 않고 HIR identity/type/plan으로 결합 |

그대로 복제하지 않는 부분도 명확하다.

- rustc의 구체적 lifetime/borrow 또는 Swift의 ARC/ABI를 가져오지 않는다.
- Kotlin FIR의 plugin surface를 HIR injection 권한으로 해석하지 않는다.
- 어느 사례의 backend 자료구조도 HIR-H1의 정본 의미가 아니다.

## 5. 단계와 권위 자료형

### 5.1 네 개의 서로 다른 HIR 자료형

```text
HirSkeleton {
  item_skeletons,
  generated_decl_skeletons,
  lexical_scopes,
  syntax_origins,
  unresolved_slots,
}

AnalysisHir {
  recoverable_items,
  partial_types,
  candidate_sets,
  diagnostics,
}

TypedHirDraft {
  closed_items,
  closed_bodies,
  normalized_types,
  complete_resolutions,
  checked_plans,
}

CanonicalHirH1 {
  canonical_tables,
  canonical_items,
  canonical_bodies,
  semantic_provenance,
  summaries,
}
```

`AnalysisHir`는 IDE와 진단용 파생 view다. serializer와 MIR lowerer는 이를 입력으로 받을 수 없다.

```text
Verified<T>                    // HIR verifier를 통과한 값
ExecutableHirH1 {
  hir: Verified<CanonicalHirH1>,
  mir_capabilities: MirCapabilityReceipt,
}
```

`unresolved_lookup_count == 0` 같은 숫자 검사는 권위 경계가 아니다. `CanonicalHirH1`에는 `UnresolvedRef`, `CandidateSet`, `InferenceVar`, `ErrorType`, `MissingExpr`, `RecoveryExpr` variant가 없어야 한다.

### 5.2 이름 해석과 타입 추론은 논리적으로 상호 질의한다

Deeplus의 overload, label, generic, witness, extension 선택은 타입 정보와 상호 의존한다. 따라서 구현을 다음과 같은 순수 직렬 pass로 강제하지 않는다.

```text
resolve everything -> infer everything -> check everything
```

대신 `CheckSession(HirSkeleton)` 안에서 owner 단위 query가 고정점에 도달한다.

```text
collect_item_headers(owner)
resolve_lexical_scope(owner)
infer_body_constraints(body)
select_call(candidate_set, constraints)
resolve_evidence(call)
check_responsibility(body)
check_patterns(body)
seal_typed_body(body)
```

중요한 것은 내부 알고리즘이 아니라 출력 불변식이다. `seal_typed_body` 뒤에는 선택 후보나 추론 변수가 남지 않는다.

## 6. 최상위 자료구조

```text
CanonicalHirH1 {
  schema_version: HirSchemaVersion,
  authority_digest: Digest,
  feature_set: FeatureSet,
  source_units: [SourceUnitDescriptor],
  identities: StaticIdentityTable,
  types: NormalizedTypeTable,
  responsibilities: ResponsibilityTable,
  item_headers: [HirItemHeader],
  body_store: [HirBody],
  body_index: [BodyIndexEntry],
  api_summary: HirApiSummary,
  dependency_summary: HirDependencySummary,
  provenance: SemanticProvenanceTable,
}

HirItemHeader {
  item_id: ItemId,
  owner: ItemOwnerId,
  kind: HirItemKind,
  visibility: Visibility,
  generic_signature: CompleteGenericSignature,
  callable_or_type_signature: ItemSignature,
  attributes: [ResolvedAttribute],
  generated_origin: Option<GeneratedOriginKey>,
  body_id: Option<HirBodyId>,
}

HirBody {
  body_id: HirBodyId,
  owner: BodyOwnerId,
  signature: HirBodySignature,
  parameters: [HirParameter],
  locals: [HirLocalDecl],
  scopes: [HirScope],
  regions: HirRegionGraph,
  lexical_blocks: Arena<HirLexicalBlock>,
  expressions: Arena<HirExpr>,
  statements: Arena<HirStmt>,
  patterns: Arena<HirPatternPlan>,
  root: HirLexicalBlockId,
  dependency_refs: [DependencyRef],
  semantic_origins: BodyOriginTable,
}

BodyIndexEntry {
  body_id: HirBodyId,
  owner: BodyOwnerId,
  body_table_index: CanonicalIndex,
  body_semantic_digest: Digest,
}

HirLexicalBlock {
  id: HirLexicalBlockId,
  scope: HirScopeId,
  statements_in_source_order: [HirStmtId],
  tail: Option<HirExprId>,
  result_type: NormalizedTypeId,
}

HirStmt {
  id: HirStmtId,
  origin: SourceOriginId,
  kind: HirStmtKind,
}

HirStmtKind =
    Evaluate(HirExprId)
  | LocalInit(LocalBindingPlan)
  | RegisterCleanup(HirCleanupRegistrationId)
  | NestedItem(ItemId)

LocalBindingPlan {
  declared_locals: [HirLocalId],
  binding_mode: Let | Var,
  initializer: HirExprId,
  pattern: Option<PatternAttemptId>,
  commit: AtomicBindingCommitPlan,
}
```

`body_store`는 self-contained canonical module에서 lowerer가 읽는 실제 body payload다. `body_index`는 owner/digest/index lookup이지 body의 대체물이 아니다. content-addressed 외부 저장 profile을 나중에 추가하더라도 canonical bundle은 참조된 body payload의 가용성과 digest를 검증해야 한다.

`HirLexicalBlock`은 MIR basic block이 아니다. lexical scope에 속한 statement의 전순서와 optional tail expression을 표현한다. body root에서 nested `Block` 식을 따라가면 모든 실행 node가 도달 가능해야 하며, orphan statement/expression은 verifier가 거부한다.

Executable body는 owning-child graph가 명확해야 한다.

- root lexical block을 제외한 각 lexical block, statement, expression은 정확히 하나의 owning parent edge를 갖는다.
- owning graph는 acyclic이고 body root에서 전부 도달 가능하다.
- schema는 각 ID field를 `OwningChild` 또는 `NonOwningUse`로 분류한다. 이 문서의 evaluation child `HirExprId` 표기는 기본적으로 `OwningChild<HirExprId>`의 축약이다.
- local use, `EvalSlotRef`, `ValueResultRef`, static projection, formal binding, region/provenance use는 non-owning reference다.
- call/message eval step이 receiver/argument/payload/trailing-closure 식을 소유한다. `ReceiverPreparation`, `MessagePayloadPlan`, `ResolvedTrailingClosureArg`, `FormalBinding`은 그 eval slot 또는 식을 non-owning으로 참조한다. Interpolation은 segment가 hole 식을 소유하고 `eval_order`는 non-owning 순서 view다.
- 같은 expression을 두 번 실행하려고 두 parent가 같은 `HirExprId`를 소유할 수 없다. 공유가 필요하면 한 번 평가해 local/eval slot/value result에 넣고 그 non-owning ref를 사용한다.

Item header와 body는 다른 query/digest 단위다. 함수 `foo`의 body만 바뀌면 `foo`의 공개 signature와 무관한 `bar`의 header/body query가 무효화되지 않아야 한다.

Closure, constant initializer, default-argument initializer, property accessor, generated forwarding body도 각각 독립적인 `BodyOwnerId`를 갖는다.

## 7. Identity 모델

### 7.1 domain을 섞지 않는 newtype

최소 identity domain은 다음과 같다.

```text
PackageId, ModuleId, SourceFileId
ItemId, ItemOwnerId, BodyOwnerId, DeclId, FunctionId, TypeDeclId
RuntimeTypeId, ClassId, EnumId, VariantId
MemberId, ClassSlotId, AssociatedItemId
TraitId, RequirementId, ConformanceId
WitnessId, WitnessParamId, RequirementBindingId
FacetTypeId, FacetInstanceId, AbiTag
ExtensionSetId, ExtensionMemberId, ActivationOriginId
LabelId, FormalId, EvidenceOriginId
ProviderId, AuthorityId, EntryCandidateId
ProviderVersionId, CacheIdentityId, ReplayTokenId
ActorId, ActorProtocolId, ActorHandlerId, ActorRequestId
ActorProtocolRequirementId
MailboxProfileId, ActorMessageErrorTypeId
SenderId, ReceiverActorId
TaskResponsibilityId, TaskScopeId, TaskChildId
HirBodyId, HirLocalId, HirScopeId, HirLexicalBlockId
HirExprId, HirStmtId, HirCleanupRegistrationId, HirRegionId
IsolationProofId, ResponsibilityId
PatternContextPolicyId, CoverageCellId, InitializedFieldId
ControlTargetId, PatternAttemptId, SuspendSiteId
MessageProducerSiteId, CorrelationProducerSiteId
ReplyProducerSiteId, TaskProducerSiteId
CancellationProducerSiteId, FailureProducerSiteId
```

한 domain의 정수나 문자열을 다른 domain으로 cast할 수 없어야 한다. runtime `String`은 어떠한 static identity로도 승격되지 않는다.

위 목록의 모든 ID가 `StableSymbolKey`인 것은 아니다. package/item/member/evidence identity는 static/exportable key를 사용하고, node/scope/region/task-responsibility instance/producer site는 owner-local key를 사용한다. module API는 body-local `TaskResponsibilityId` 숫자를 export하지 않고 그 descriptor의 static residue만 투영한다.

현행 frontend 모델이 요구하는 `MessageId`, `CorrelationId`, `ReplyId`, `TaskId`, `CancellationId`, `FailureId`는 typed HIR에 존재한다. 다만 이들은 compile-time `StableSymbolKey`가 아니라 runtime에서 생성되는 비위조 value의 정규화 타입과 result binding이다. Canonical HIR는 각 fresh value를 만드는 producer site와 책임을 보존하고, 구체 runtime identity 값을 source span hash나 정적 정수로 미리 만들지 않는다.

`MessageProducerSiteId` 등 여섯 producer-site ID는 각각 `ProducerSiteId<MessageId>`처럼 identity kind가 붙은 owner-local newtype이다. 서로 cast할 수 없고 body semantic traversal로 canonical numbering한다.

### 7.2 정적 reference는 닫힌 합타입이다

```text
ResolvedEvidenceRef {
  identity:
      Concrete(WitnessId)
    | Forwarded(WitnessParamId),
  evidence_origin: EvidenceOriginId,
  substitution: CompleteSubstitution,
  profile: EvidenceUseProfile,
}

ResolvedRef =
    Local(HirLocalId)
  | DirectDecl(DeclId)
  | EnumVariant(VariantId)
  | NominalMember(MemberId)
  | ClassSlot(ClassSlotId)
  | TraitRequirement {
      evidence: ResolvedEvidenceRef,
      requirement: RequirementId,
    }
  | ExtensionMember {
      member: ExtensionMemberId,
      activation: ActivationOriginId,
    }
  | TypeSide(AssociatedItemId)
  | ProviderEntry {
      provider: ProviderId,
      entry: EntryCandidateId,
    }
  | ActorHandler(ActorHandlerId)
  | ActorRequest(ActorRequestId)
  | ActorProtocolRequirement {
      protocol: ActorProtocolId,
      requirement: RequirementId,
    }
  | ReservedHirSelector(ReservedSelectorKind)
```

lexical, nominal member, extension, witness, type-side, actor message domain을 하나의 `operation_id: String`으로 합치지 않는다.

Call, Trait requirement, Map `Keyable`, interpolation `Display`, closure clone/deep처럼 evidence를 소비하는 모든 plan은 raw `WitnessId`가 아니라 `ResolvedEvidenceRef`를 사용한다. 한 node가 여러 evidence를 쓰면 각 use가 별도의 origin/substitution/profile을 가진다.

### 7.3 안정 identity와 body-local identity

```text
StableSymbolKey {
  package: PackageId,
  module_path: [ModuleSegment],
  declaration_path: [DeclarationSegment],
  identity: StaticIdentityKey,
}

StaticIdentityKey =
    Module { name }
  | NominalType { kind, name, canonical_binder_kinds }
  | Class { name, canonical_binder_kinds }
  | Enum {
      name,
      canonical_binder_kinds,
    }
  | Trait { name, canonical_binder_kinds }
  | Property { owner, static_name }
  | EnumVariant {
      enum_owner: EnumId,
      static_name,
      payload_shape_key,
    }
  | StaticBinding { owner, static_name, normalized_type }
  | Callable {
      kind,
      name,
      overload_slot: CanonicalOverloadSlotKey,
    }
  | Requirement {
      original_declaring_trait: TraitId,
      requirement_kind: RequirementKind,
      member_name: StaticName,
      overload_slot: CanonicalOverloadSlotKey,
    }
  | ClassSlot { original_owner, member_name, overload_slot }
  | AssociatedItem { owner, kind, static_name, binder_key }
  | Conformance {
      normalized_target,
      normalized_instantiated_trait,
      coherence_domain_authority: AuthorityId,
    }
  | Witness {
      conformance: ConformanceId,
      whole_binding_key: CanonicalWholeEvidenceBindingKey,
    }
  | RequirementBinding {
      witness: WitnessId,
      requirement: RequirementId,
      member_binding_key: CanonicalRequirementBindingKey,
    }
  | ExtensionSet {
      target_type,
      set_name,
    }
  | ExtensionMember {
      extension_set: ExtensionSetId,
      selector,
      normalized_signature_digest,
    }
  | Provider {
      static_name,
      registry_domain,
    }
  | ProviderVersion {
      provider: ProviderId,
      canonical_version_key,
    }
  | CacheIdentity {
      provider: ProviderId,
      canonical_cache_namespace,
    }
  | Authority {
      authority_namespace,
      static_name,
    }
  | ProviderEntry {
      provider: ProviderId,
      static_name,
      normalized_entry_signature,
    }
  | Actor { static_name }
  | ActorProtocol { static_name, canonical_binder_kinds }
  | ActorCallable {
      owner: ActorId | ActorProtocolId,
      kind: Handler | Request | ProtocolRequirement,
      selector,
      overload_slot: CanonicalOverloadSlotKey,
    }
  | BuiltinProfileIdentity {
      kind: MailboxProfile | ActorMessageErrorType,
      canonical_profile_name,
      version,
    }
  | FacetType {
      source_type,
      mode: Borrow | Owned | Inout,
      normalized_facet_contract,
    }
  | AbiTagIdentity { canonical_tag }
  | GeneratedStatic { owner, origin: GeneratedOriginKey }

CanonicalOverloadSlotKey {
  binder_arity_and_kinds,
  receiver_channel,
  ordered_external_labels,
  normalized_input_types,
  channel_kinds,
  repeated_and_rest_shape,
}

CanonicalPackageKey {
  registry_namespace,
  package_name,
  package_version_identity,
}

HirExprId {
  owner: BodyOwnerId,
  local: OwnerLocalExprId,
}

HirStmtId {
  owner: BodyOwnerId,
  local: OwnerLocalStmtId,
}

OwnerLocalExprId = newtype(u32)
OwnerLocalStmtId = newtype(u32)

HirNodeRef =
    Expr(HirExprId)
  | Stmt(HirStmtId)
```

- `StableSymbolKey`는 source order, byte offset, 절대 path, hash iteration order를 포함하지 않는다.
- `PackageId`만 `CanonicalPackageKey`로 bootstrap하고, 그 아래 모든 exportable static ID는 정확히 하나의 `StaticIdentityKey` variant를 통해 만들어진다.
- `LabelId`와 `FormalId`는 selected callable identity + formal ordinal/channel + visible external label의 parent-scoped child key다. local parameter name은 identity가 아니다.
- `ActivationOriginId`는 extension-set identity + activating lexical frame + activation kind + semantic site key이고, `EvidenceOriginId`는 conformance/witness binding의 canonical origin key다. import/use traversal order를 쓰지 않는다.
- `ProviderId`는 version-independent registry declaration key다. `ProviderVersionId`는 `(ProviderId, canonical version key)` child identity이고 version content는 provider API/content digest를 바꾼다. `CacheIdentityId`와 registry-owned profile ID도 해당 provider/profile의 canonical child key이며 runtime cache content나 timestamp가 identity를 만들지 않는다.
- `EnumId`는 declaration key, 각 `VariantId`는 `(EnumId, static variant name, payload shape key)`로 식별한다. frozen case-universe/order/behavior digest는 enum content/API contract이지 `EnumId` preimage가 아니다. source order, raw value, tag, ordinal, discriminant, layout, ABI가 `VariantId`를 만들지 않는다.
- `WitnessId`는 admitted whole conformance binding/table 하나를 가리키며 requirement마다 새 witness를 만들지 않는다. requirement별 선택은 `(WitnessId, RequirementId)` 또는 그 child `RequirementBindingId`이고 parent/diamond path는 canonical whole witness를 공유한다.
- `RuntimeTypeId`와 `FacetInstanceId`는 runtime value-level typed identity이고 static symbol key가 아니다. `FacetTypeId`만 normalized source type/mode/contract의 static key를 사용하며, 허용되지 않은 owned/inout Facet은 feature admission에서 canonical sealing을 통과하지 못한다.
- `CanonicalOverloadSlotKey`에는 result type, responsibility-profile-only 차이, marker, default, local name, declaration order, generated ordinal을 넣지 않는다. 이 차이들은 overload identity를 만들지 않고 `RequirementContract` 또는 item contract의 중복/호환성 검사 대상이다.
- `StaticIdentityKey`는 opaque digest가 아니다. verifier가 normalized declaration shape에서 field-by-field 재계산하는 닫힌 합타입이다.
- full item header/content digest는 identity key와 별도로 계산하고 `item_id` 자체를 preimage에 넣지 않는다. 따라서 identity↔header digest 순환이 없다.
- generated declaration은 `owner + GeneratedOriginKey`로 식별한다.
- body-local ID는 compilation session 내부 참조다. canonical serialization에서는 semantic traversal로 다시 번호를 부여한다.
- 같은 spelling이라도 다른 identity domain이면 다른 ID다.
- source/import/use/provider 등록 순서는 overload winner 또는 stable identity tie-breaker가 아니다.

```text
GeneratedOriginKey =
    PropertyAccessor { property: MemberId, kind: get | set }
  | ForwardingEntry { owner: ItemId, member_key: StaticMemberKey }

BodyGeneratedOriginKey =
    ComprehensionBody {
      owner: BodyOwnerId,
      site: SemanticChildPath,
      clause_path: ClausePath,
    }
  | SynthesizedClosure {
      owner: BodyOwnerId,
      site: SemanticChildPath,
      role: ClosureRole,
    }
```

`SemanticChildPath`는 schema-defined parent node path, child role, 의미 있는 ordered-child index로 구성한다. 이는 exportable declaration identity가 아니라 owner-local generated body identity다. 같은 owner/role의 closure가 여러 개여도 충돌하지 않으며 canonical body traversal과 함께 재번호화된다.

## 8. Source origin과 provenance

모든 semantic node는 origin을 가진다.

```text
SourceOrigin =
    Surface(SyntaxAnchor)
  | Desugared {
      kind: DesugaringKind,
      primary: SyntaxAnchor,
      contributors: [SyntaxAnchor],
    }
  | GeneratedStatic {
      owner: ItemId,
      key: GeneratedOriginKey,
      contributors: [SyntaxAnchor],
    }
  | GeneratedBody {
      owner: BodyOwnerId,
      key: BodyGeneratedOriginKey,
      contributors: [SyntaxAnchor],
    }
  | Fused {
      origins: [SourceOriginId],
      reason: FusionReason,
    }
```

`SyntaxAnchor`는 절대 path와 byte offset을 semantic identity로 쓰지 않는다. 논리 source unit, syntax role, 구조 경로를 사용하고 실제 span은 debug projection에 둔다.

```text
SemanticOrigin {
  source_role,
  package_id,
  module_id,
  generated_owner,
  evidence_origin,
  extension_activation_origin,
  provider_binding_origin,
}

DebugOrigin {
  source_file_id,
  byte_span,
  original_syntax_kind,
  desugaring_chain,
  related_spans,
  surface_spelling,
}
```

bare `Synthetic` origin은 금지한다. generated node의 owner/key/contributors를 복구할 수 없으면 canonical HIR가 아니다.

Origin attachment의 **존재와 semantics-affecting identity**는 semantic 검증 대상이지만, 모든 provenance byte가 semantic digest에 들어가는 것은 아니다. `source_role`, generated owner/key, evidence origin, extension activation origin, provider binding origin은 semantic projection에 들어간다. span, surface spelling, `DesugaringKind`, contributor anchor와 desugaring chain은 debug projection에만 들어간다. 따라서 direct `let`과 동치인 rightward binding은 같은 semantic digest를 가지면서도 서로 다른 진단 origin을 유지할 수 있다.

## 9. 타입과 responsibility

### 9.1 normalized type

각 식, place plan, binder, formal, capture, payload field는 정확한 `NormalizedTypeId`를 갖는다. 다음이 모두 닫혀 있어야 한다.

- alias expansion과 nominal identity
- union/intersection/Option
- associated projection과 selected evidence
- generic kind: type, `StaticInt`, `EffectRow`, `ErrorSet`
- row와 label
- ownership/view mode
- measure와 shape
- callable profile
- actor/protocol message profile

anonymous recursive structural type나 열린 projection은 별도 정본 의미 없이는 canonical HIR에 들어올 수 없다.

### 9.2 responsibility는 단일 enum이 아니다

```text
ResponsibilitySummary {
  value_mode: Reusable | Owned | Borrowed(HirRegionId) | Inout(HirRegionId),
  resource: ResourceProfile,
  place_access: PlaceAccessProfile,
  effects: EffectRow,
  recoverable_errors: ErrorSet,
  defects: DefectSet,
  cancellation: CancellationProfile,
  suspension: SuspensionProfile,
  isolation: IsolationProfile,
  authority: AuthorityRequirementSet,
  cleanup: CleanupObligationSet,
}
```

각 body는 borrow/inout/suspend 검증을 위한 owner-local region graph를 가진다.

```text
HirRegionGraph {
  regions: [HirRegionDecl],
  constraints: [HirRegionConstraint],
}

HirRegionDecl {
  id: HirRegionId,
  owner_scope: HirScopeId,
  kind: Lexical | Borrow | Inout | Capture | SuspensionBoundary,
}

HirRegionConstraint =
    Outlives(HirRegionId, HirRegionId)
  | ContainsUse(HirRegionId, HirNodeRef)
  | ExclusiveAt(HirRegionId, LogicalPlaceDomain, HirNodeRef)
  | MustEndBeforeSuspend(HirRegionId, SuspendSiteId)
  | TransferAcrossIsolationRequires(HirRegionId, IsolationProofId)
```

Region ID는 body root의 lexical scope와 borrow/inout producer를 semantic traversal한 순서로 canonical numbering한다. raw source span, allocator address, solver insertion order를 사용하지 않는다. verifier는 graph에서 borrow escape, overlapping inout, suspension/isolation crossing을 재계산한다.

다음 축은 서로 합치지 않는다.

- cancellation은 `ErrorSet`이 아니다.
- suspension은 `EffectRow`의 별칭이 아니다.
- resource/drop 책임은 value mode가 아니다.
- isolation은 authority가 아니다.
- defect는 recoverable error가 아니다.

각 `HirExpr`의 공통 header는 다음과 같다.

```text
HirExpr {
  id: HirExprId,
  origin: SourceOriginId,
  ty: NormalizedTypeId,
  result_category: Value | Place | Control,
  responsibility: ResponsibilityId,
  kind: HirExprKind,
}
```

Responsibility summary는 verifier가 body에서 다시 계산한다. 입력 summary를 신뢰하지 않는다.

`Unit`은 result category가 아니라 정규화 타입이다. Unit literal, Unit-returning call, assignment는 모두 `result_category = Value`와 `ty = Unit`을 갖는다. statement-only 구성은 `HirStmtKind`에 있고 expression category에 섞지 않는다.

## 10. HIR 식과 구조화된 제어

HIR-H1은 surface syntax 전체를 그대로 두지도 않고, CFG로 너무 일찍 평탄화하지도 않는다.

```text
HirExprKind =
    Literal
  | ResolvedRef
  | Block
  | ResolvedCall
  | MessageCall
  | Intrinsic
  | PlaceAccess
  | Replace
  | If
  | Ternary
  | Match
  | Loop
  | Try
  | StrictBool
  | SequentialBool
  | OptionCoalesce
  | PatternAttempt
  | Construction
  | MapLiteral
  | Interpolation
  | Closure
  | CleanupScope
  | Await
  | Yield
  | TaskScope
  | ProviderOperation
  | ReturnTo
  | RetTo
  | BreakTo
  | ContinueTo
  | Throw
  | CancelPropagate
```

`return`과 local `ret`는 같은 node가 아니다. 각각 정확한 `ControlTargetId`와 owner boundary를 갖는다. `break`와 `continue`도 label 문자열이나 depth가 아니라 resolved target을 갖는다.

HIR는 `if`, `match`, `loop`, `try`, task scope를 구조화된 채로 유지한다. MIR가 block/edge와 `LeavePlan`을 만든다.

## 11. 호출

### 11.1 정적 binding과 source evaluation order의 분리

flat `Vec<Expr>`는 Deeplus 호출 의미를 보존할 수 없다.

```text
ReceiverPreparation {
  evaluated_receiver: EvalSlotRef,
  adjustments: ReceiverAdjustmentPlan,
  resulting_type: NormalizedTypeId,
}

HirCallPlan {
  callee: HirCalleeRef,
  substitution: CompleteSubstitution,
  receiver: Option<ReceiverPreparation>,
  eval_order: [CallEvalStep],
  channels: CallChannels,
  formal_bindings: [FormalBinding],
  callable_profile: CallableProfile,
  outcome: ResponsibilitySummary,
  commit: CallCommitPlan,
}

CallEvalStep =
    EvaluateReceiver { expr: OwningChild<HirExprId>, ordinal }
  | EvaluateOrdinaryArgument {
      expr: OwningChild<HirExprId>,
      ordinal,
      eval_slot,
    }
  | EvaluatePositionalUnfold {
      aggregate_expr: OwningChild<HirExprId>,
      ordinal,
      eval_slot,
      projection: FixedTupleProjection | SequenceResidueProjection,
    }
  | EvaluateNamedUnfold {
      aggregate_expr: OwningChild<HirExprId>,
      ordinal,
      eval_slot,
      static_row: StaticLabelRow,
      projection: [StaticLabelProjection],
    }
  | EvaluateContextArgument {
      expr: OwningChild<HirExprId>,
      ordinal,
      eval_slot,
    }
  | EvaluateTrailingClosure {
      closure: OwningChild<HirExprId>,
      ordinal,
      eval_slot,
    }

CallChannels {
  fixed_positional: [FormalBinding],
  fixed_named: [FormalBinding],
  positional_unfold: [PositionalUnfoldBinding],
  repeated_positional: [FormalBinding],
  named_unfold: [NamedUnfoldBinding],
  named_tail: [NamedTailBinding],
  context: [FormalBinding],
  witnesses: [WitnessBinding],
  trailing_closures: [ResolvedTrailingClosureArg],
}

FormalBinding {
  formal: FormalId,
  formal_ordinal: u32,
  channel: Value | Repeated | NamedRest | Context | TrailingClosure,
  satisfaction:
      ExplicitEvalSlot(EvalSlotRef)
    | StaticProjection(ProjectionRef)
    | TrailingClosureArg(NonOwningUse<HirExprId>)
    | DeclaredDefault {
        value: DefaultValueRef,
        declaration_origin: SourceOriginId,
      },
}

DefaultValueRef {
  declaring_item: ItemId,
  formal: FormalId,
  body: HirBodyId,
  semantic_digest: Digest,
}

EvalSlotRef =
    Ordinary(CallEvalSlot)
  | Message(MessageEvalSlot)

WitnessBinding {
  evidence: ResolvedEvidenceRef,
  source_position: Option<SourceOriginId>,
}
```

`formal_bindings`는 formal/channel mapping이고 `eval_order`는 runtime evaluation ordering이다. named argument나 context/witness formal 순서가 source evaluation order를 바꾸지 않는다.

`using` evidence는 runtime argument expression이 아니다. checker-visible borrowed nonescaping evidence이며, canonical HIR에는 concrete `WitnessId` 또는 forwarded `WitnessParamId`만 남는다. computed value나 ordinary `HirExprId`를 `WitnessBinding`으로 승격할 수 없고, 따라서 witness는 runtime `eval_order`에도 들어가지 않는다.

Verifier는 `ResolvedFormalSignature`의 formal order/default profile과 `FormalBinding`을 다시 대조한다. trailing closure가 선택한 formal 앞에 `DeclaredDefault`로만 충족된 ordinary value formal이 하나라도 있으면 `default_parameter_skip = forbidden` 위반으로 sealing을 거부한다.

각 `EvalSlotRef`는 같은 call plan 안의 정확히 하나인 producing eval step을 가리킨다. ordinary slot과 message slot은 cast할 수 없고, payload projection은 자신의 `MessageEvalSlot` aggregate만 base로 삼는다.

`*expr`와 `**record`는 projection entry마다 원식을 복제하지 않는다. 각각 하나의 aggregate evaluation slot을 만들고, positional shape 또는 static label row를 그 slot에 투영한다. projection은 이미 평가된 aggregate를 읽는 정적 descriptor이며 runtime Map iteration이나 재평가가 아니다. unknown-arity positional residue는 fixed formal을 채우지 못하고, named unfold의 row가 정적으로 닫히지 않으면 sealing 전에 거부한다.

`HirCalleeRef`에는 candidate set이 아니라 다음이 모두 확정되어 있다.

- exact `FunctionId`, `MemberId`, `ClassSlotId`, `ExtensionMemberId` 또는 requirement identity
- complete generic substitution
- concrete `WitnessId` 또는 abstract `WitnessParamId`
- extension이면 `ActivationOriginId`
- callable kind와 receiver adjustment
- labels와 formal identities
- effect/error/defect/cancel/suspend/isolation/authority profile

MIR lowerer는 name, overload, label, witness, extension, provider를 다시 검색하지 않는다.

### 11.2 ordered trailing closure

ordinary call과 actor message는 다음 자료형을 공유한다.

```text
ResolvedTrailingClosureArg {
  source_eval_ordinal: u32,
  surface_label: Option<LabelId>,
  selected_formal: FormalId,
  selected_formal_ordinal: u32,
  closure_expr: NonOwningUse<HirExprId>,
  closure_profile: CallableProfile,
  transfer: ClosureTransferProfile,
}
```

검사 규칙은 live contract를 따른다.

- 하나이면 labeled 또는 unlabeled일 수 있다.
- 둘 이상이면 모두 label이 있고 label은 중복되지 않는다.
- label은 visible function-typed formal에 결합한다.
- unlabeled form은 남은 적합 formal이 정확히 하나일 때만 허용한다.
- trailing syntax로 defaulted formal을 건너뛸 수 없다. selected formal 앞의 ordinary value formal은 모두 explicit ordinary/payload binding으로 충족되어야 한다.
- ordinary arguments 또는 message payload가 먼저 평가되고, trailing closure는 그 뒤 source order로 각각 정확히 한 번 평가된다.
- HIR에는 surface label 유무와 무관하게 항상 `selected_formal`이 남는다.

## 12. Message call과 actor transport

`~` message는 하나의 별도 HIR 식이다. value carrier는 모든 dispatch 종류에서 `MessagePayloadPlan`을 사용하지만, 선택된 selector domain은 닫힌 합타입으로 구분한다.

```text
MessagePayloadPlan =
    None {
      formal_count: Zero,
    }
  | Scalar {
      aggregate_expr: NonOwningUse<HirExprId>,
      aggregate_type: NormalizedTypeId,
      formal: FormalId,
    }
  | Tuple {
      aggregate_expr: NonOwningUse<HirExprId>,
      aggregate_type: NormalizedTypeId,
      elements: [PayloadElement],
      projection: [PositionalPayloadProjection],
    }
  | Record {
      aggregate_expr: NonOwningUse<HirExprId>,
      aggregate_type: NormalizedTypeId,
      fields_in_source_order: [PayloadField],
      projection: [NamedPayloadProjection],
    }

ResolvedMessageDispatch {
  target: MessageDispatchTarget,
  substitution: CompleteSubstitution,
  receiver_adjustment: ReceiverAdjustmentPlan,
  callable_profile: CallableProfile,
  formal_signature: ResolvedFormalSignature,
}

MessageDispatchTarget =
    NominalMember {
      member: MemberId | ClassSlotId,
    }
  | TraitRequirement {
      requirement: RequirementId,
      evidence: ResolvedEvidenceRef,
    }
  | ExtensionMember {
      member: ExtensionMemberId,
      extension_set: ExtensionSetId,
      activation: ActivationOriginId,
    }
  | Actor {
      selector: ActorHandlerId | ActorRequestId
              | ActorProtocolRequirementId,
      transport: ActorTransportPlan,
    }
  | Reserved {
      selector: ReservedSelectorKind,
      plan: ReservedMessagePlan,
    }

ReservedMessagePlan =
    Spawn {
      task_scope: TaskScopeId,
      child: TaskChildId,
      lexical_spawn_index: u32,
      child_identity: FreshValueBinding<TaskId>,
      exit_obligation: ScopeOwnedUntilTerminalAndCleanupComplete,
      primary_failure_order: LexicalSpawnIndex,
      detached: Forbidden,
    }

MessageCallPlan {
  receiver: ReceiverPreparation,
  selector_path: ResolvedSelectorPath,
  dispatch: ResolvedMessageDispatch,
  payload: MessagePayloadPlan,
  trailing_closures: [ResolvedTrailingClosureArg],
  eval_order: [MessageEvalStep],
  formal_bindings: [FormalBinding],
  outcome: ResponsibilitySummary,
}

MessageEvalStep =
    EvaluateReceiver {
      expr: OwningChild<HirExprId>,
      ordinal: u32,
      eval_slot: MessageEvalSlot,
    }
  | EvaluatePayloadAggregate {
      expr: OwningChild<HirExprId>,
      kind: Scalar | Tuple | Record,
      ordinal: u32,
      eval_slot: MessageEvalSlot,
    }
  | EvaluateTrailingClosure {
      closure: OwningChild<HirExprId>,
      selected_formal: FormalId,
      ordinal: u32,
      eval_slot: MessageEvalSlot,
    }
```

`ResolvedSelectorPath`는 source의 complete qualified path와 선택된 identity를 연결한다. `selector`, `TraitOrProtocol::selector`, `Type::ExtensionSet::selector`를 같은 문자열로 평탄화하지 않는다. nominal/Trait/extension/reserved selector도 ordinary `ArgumentList`가 아니라 message payload carrier를 유지한다. actor subvariant는 actor/protocol domain에서만 선택되며 ordinary method fallback이 없다. reserved `~ spawn`도 두 번째 syntax owner를 만들지 않고 `Reserved` subvariant로 표현한다.

Payload 규칙은 다음과 같다.

| Payload | formal projection |
|---|---|
| none | parameter 0개 |
| scalar | 정확히 formal 1개 |
| tuple | positional formal로 정적 투영 |
| record | static label을 named formal로 정적 투영 |

- message는 ordinary `ArgumentList`를 재사용하지 않는다.
- payload aggregate는 0개 또는 1개다.
- `aggregate_expr`가 child evaluation을 소유하며 projection은 이미 평가된 aggregate를 읽을 뿐 재평가하지 않는다.
- payload aggregate와 그 child의 source order/evaluate-once가 보존된다.
- payload 평가가 끝난 뒤 trailing closure를 source order로 평가한다.
- context와 witness는 payload data에서 합성하지 않는다.
- `MessageEvalStep.ordinal`은 receiver, optional payload aggregate, trailing closures의 전순서를 만든다. none payload에는 payload step이 없고 projection은 evaluation step을 추가하지 않는다.

Actor transport가 선택된 경우에만 다음 descriptor를 추가한다.

```text
FreshValueBinding<IdentityKind> {
  producer_site: ProducerSiteId<IdentityKind>,
  value_result: ValueResultRef<IdentityKind>,
  freshness: PerEvaluationNonForgeable,
}

ActorRequestTaskResponsibility {
  identity: TaskResponsibilityId,
  task_value: ValueResultRef<TaskId>,
  result_type: NormalizedTypeId,
  normalized_handler_error_set: ErrorSet,
  cancellation_axis: CancellationProfile,
  isolation_owner: ValueResultRef<ReceiverActorId>,
  correlation_value: ValueResultRef<CorrelationId>,
  terminal_transport_failure:
    ExactSet<ActorMessageError::receiverClosedBeforeReply>,
}

ActorPrecommitPlan {
  transfer_sources: [PreparedTransferSource],
  admission_checks: [MailboxAdmissionCheck],
  rejection_errors:
    ExactSet<
      ActorMessageError::mailboxFull,
      ActorMessageError::receiverClosedBeforeAdmission
    >,
  rejection_disposition: PreserveAllSenderOwners,
  precommit_cancellation: AbortWithoutTransferIdentityOrSequence,
}

ActorCommitSuccessOutputs {
  message_identity: FreshValueBinding<MessageId>,
  channel_sequence: FreshChannelSequenceBinding,
  dispatch:
      OneWay {
        result_type: Result<Unit, ActorMessageErrorTypeId>,
      }
    | Request {
        reply_identity: FreshValueBinding<ReplyId>,
        correlation_identity: FreshValueBinding<CorrelationId>,
        task_identity: FreshValueBinding<TaskId>,
        responsibility: ActorRequestTaskResponsibility,
        admission_result_type:
          Result<TaskType, ActorMessageErrorTypeId>,
      },
}

ActorCommitPlan {
  transfer_each_source: ExactlyOnce,
  install_actor_owned_payload: ExactlyOnce,
  fifo_key: (
    ValueResultRef<SenderId>,
    ValueResultRef<ReceiverActorId>,
    MailboxProfileId
  ),
  outputs: ActorCommitSuccessOutputs,
  postcommit_cancellation: CannotRestoreSenderOrRetractMessage,
}

ActorTransportPlan {
  static_actor_or_protocol: ActorId | ActorProtocolId,
  sender_value: ValueResultRef<SenderId>,
  receiver_actor_value: ValueResultRef<ReceiverActorId>,
  mailbox_profile: MailboxProfileId,
  actor_message_error_type: ActorMessageErrorTypeId,
  precommit: ActorPrecommitPlan,
  commit: ActorCommitPlan,
}
```

`ValueResultRef<K>`는 runtime 값을 미리 계산한 정수가 아니라, 이 HIR evaluation이 생성하여 이후 typed value가 보유하는 exact non-forgeable identity result를 가리킨다. 그러므로 typed HIR는 concrete per-value `MessageId`, `CorrelationId`, `ReplyId`, `TaskId` 결합을 잃지 않으면서도 source span hash로 runtime identity를 위조하지 않는다. `CancellationId`와 `FailureId`도 해당 outcome producer의 `ValueResultRef`로 같은 원칙을 따른다.

`receiver_actor_value`는 `MessageEvalStep::EvaluateReceiver.eval_slot`의 actor identity projection을 정확히 참조한다. protocol-typed receiver라도 commit FIFO key와 request-task isolation owner는 이 runtime receiver value를 공유하며, static `ActorProtocolId`나 source type으로 대체하지 않는다. sender도 현재 actor context의 value identity를 명시적으로 참조한다.

Actor 불변식:

- actor boundary를 넘는 closure마다 capture transfer, isolation, effect/error/cancel/cleanup 적합성을 독립적으로 증명한다.
- admission 전 rejection은 moved sender place를 소비하지 않고 `MessageId` ownership이나 channel sequence를 할당하지 않는다.
- commit은 payload를 정확히 한 번 actor에 이전하고 message identity와 FIFO sequence를 생성한다.
- commit 뒤 cancellation은 sender ownership을 복구하거나 message를 retract하지 않는다.
- one-way 결과는 `Result<Unit, error ActorMessageError>`다.
- request admission 결과는 `Result<Task<T>, error ActorMessageError>`이고 explicit `await`는 Task를 추출한 뒤에만 적용한다.
- `ActorRequestTaskResponsibility`는 result type, handler `ErrorSet`, cancellation, isolation owner, **그 value의 correlation identity**, terminal `receiverClosedBeforeReply`를 모두 보존한다.
- request success에서 `responsibility.task_value == task_identity.value_result`, `responsibility.correlation_value == correlation_identity.value_result`, `responsibility.isolation_owner == receiver_actor_value`가 성립해야 한다.
- `mailboxFull`과 `receiverClosedBeforeAdmission`은 admission result에만 있고 request task descriptor에 들어가지 않는다.
- request task를 await할 때의 exact error set은 `normalize(handler ErrorSet | ActorMessageError::receiverClosedBeforeReply)`로 재계산된다.
- module API에는 runtime correlation 값이 아니라 `per_value_non_forgeable` policy marker만 들어간다.
- ordinary async task에는 actor transport descriptor를 붙이지 않는다.

## 13. Place와 ownership 계획

HIR는 `PlaceId`나 loan token을 만들지 않지만 lvalue를 단순 expression으로도 두지 않는다.

```text
HirPlacePlan {
  prepare: [PlacePrepareStep],
  root: PlaceRoot,
  static_tail: [StaticProjection],
  access: Read | Move | BorrowShared | BorrowInout | Replace,
  value_type: NormalizedTypeId,
  logical_domain: LogicalPlaceDomain,
  region_constraints: [HirRegionConstraint],
}

PlacePrepareStep =
    EvaluateBase { expr, temp }
  | EvaluateIndex { expr, temp }
  | ValidateBounds { base_temp, index_temp, check_site }
  | ValidateVariant { base_temp, variant, check_site }
  | EvaluateReplacement { expr, temp }
```

이 plan은 `a[f()] += g()`에서 `a`, `f()`, `g()`를 중복 평가하지 않게 한다. HIR는 preparation과 commit 경계를 고정하고, MIR가 `PlaceId`, checked edge, `LoanId`, `AccessToken`, replace transaction을 만든다.

다음은 HIR에서 이미 확정되어야 한다.

- read/copy/move/borrow/inout/replace intent
- base와 dynamic index의 source order
- logical mutable domain
- region 및 suspend escape constraint
- partial move path의 semantic projection
- replacement 실패 시 old/new value 책임

alias token의 실제 flow와 join은 MIR verifier 책임이다.

## 14. Pattern 계획

Pattern은 HIR에서 단순 tree도, 이미 펼쳐진 CFG도 아니다.

```text
HirPatternPlan {
  attempt_id: PatternAttemptId,
  context: PatternContextPolicyId,
  subject: EvaluateOnce<HirExprId>,
  subject_type: NormalizedTypeId,
  binding_owner_expected_subject_type: Option<NormalizedTypeId>,
  coverage_cell: CoverageCellId,
  test: NonConsumingPatternTest,
  probe_binders: [ProbeBinder],
  guard: Option<CheckedPatternGuard>,
  commit: AtomicBindingCommitPlan,
  final_binders: [FinalBinder],
  failure: PatternFailureDisposition,
}

NonConsumingPatternTest =
    EnumVariant {
      enum_owner: EnumId,
      variant: VariantId,
      active_payload_shape: VariantPayloadShapeKey,
      child_tests: [NonConsumingPatternTest],
    }
  | ClosedUnionAlternative { alternative_type, child_tests }
  | OptionAlternative { none | some, child_tests }
  | Literal { normalized_literal }
  | NominalOrStructuralTest { exact_test_descriptor }
```

불변식:

1. subject는 정확히 한 번 평가한다.
2. `binding_owner_expected_subject_type`은 source binding owner에 whole-pattern annotation이 있을 때만 `Some`이다. `Some`이면 independently evaluated subject와의 compatibility를 pattern admission 전에 증명하고, annotation이 없으면 `None`을 임의 inferred type으로 채우지 않는다.
3. structural test는 nonconsuming이다.
4. enum test는 scrutinee의 exact `EnumId` owner 아래 `VariantId`를 사용한다. foreign/unknown variant나 inactive payload projection은 guard 전에 거부하며 `MemberId`, raw tag 또는 source ordinal로 대체하지 않는다.
5. guard는 probe binder만 읽고, `Bool`, pure, total, nonthrowing, nonsuspending, non-authority다.
6. move/borrow/final binding은 guard 성공 뒤 하나의 infallible atomic commit으로 수행한다.
7. 실패 경로에는 partial move, partial binding, authority 획득이 없다.
8. or-pattern의 모든 성공 arm은 동일한 binder interface를 만든다.
9. exhaustiveness는 normalized coverage cell로 검사한다.
10. 아직 지원하지 않는 tuple/Record rest, captured List rest, extractor, backtracking variant는 만들지 않는다.

`Phi`는 선언 type을 바꾸는 HIR node가 아니다. flow refinement는 checker가 재계산 가능한 `FlowFactTable`로 보관하고, 각 식의 checked normalized type에 반영한다. `FlowFactTable`은 실행 의미가 아니라 검증/IDE certificate다.

## 15. Construction, collection, interpolation

### 15.1 transactional construction

```text
ConstructionPlan {
  target_type: NormalizedTypeId,
  target_variant: Option<VariantId>,
  target_row: ClosedRowDescriptor,
  entries_in_source_order: [ConstructionEntry],
  initialization_steps: [FieldInitStep],
  rollback_order: [InitializedFieldId],
  commit_boundary: ConstructionCommitPoint,
  outcome: ResponsibilitySummary,
}
```

- field, spread, default, computed entry는 source order로 정확히 한 번 평가한다.
- partial initialized set과 reverse rollback 순서를 보존한다.
- publish 전까지 constructed value는 외부에서 관찰되지 않는다.
- MIR가 linear `BuilderToken`과 commit/rollback edge를 만든다.

`Record`와 `Map`은 같은 HIR node가 아니다. `Record***` residue와 `**` named-tail unfold도 정적 label/row plan을 잃지 않는다.

### 15.2 immutable Map literal

```text
MapLiteralPlan {
  key_type: NormalizedTypeId,
  value_type: NormalizedTypeId,
  keyable_evidence: ResolvedEvidenceRef,
  entries_in_source_order: [
      DirectMapEntry { key: HirExprId, value: HirExprId }
    | MapUnfoldEntry {
        aggregate_expr: HirExprId,
        exact_key_type: NormalizedTypeId,
        exact_value_type: NormalizedTypeId,
      }
  ],
  equal_key_policy: LaterOccurrenceReplaces,
  displaced_owner_cleanup: ExactlyOnce,
  publication: CommitAfterCompleteSuccess,
  rollback: ReverseAcquiredTemporaryCleanup,
  outcome: ResponsibilitySummary,
}
```

Direct key/value와 Map `**base`는 source order로 각각 한 번 평가한다. `keyable_evidence`의 equality/hash는 borrowed, nonconsuming, synchronous, `throws Never effects {}`, noncancelling, non-authority여야 한다. later-equal key는 earlier value를 교체하고 displaced owner를 정확히 한 번 정리한다. 실패 전에는 partial Map을 publish하지 않는다.

Map literal의 `**base`는 exact `Map<K,V>` runtime unfold다. call-site `**record`의 static label projection과 같은 node나 channel을 사용하지 않는다.

### 15.3 comprehension과 loop

Surface comprehension은 HIR에서 collector/iteration/filter/yield plan으로 정규화한다. 그러나 MIR basic block으로 미리 펼치지 않는다.

```text
ComprehensionPlan {
  collector: ResolvedCollector,
  clauses: [ComprehensionClause],
  produced_value: HirExprId,
  cleanup_scope: HirScopeId,
}
```

### 15.4 interpolation

현행 core interpolation은 이미 닫힌 의미를 갖는다. shorthand는 root를 한 번 평가하고 명시적인 read-only projection으로 만들며, 각 hole은 미리 선택된 `Display` evidence를 사용한다.

```text
InterpolationSegment =
    Direct {
      value: ConstString,
    }
  | DisplayHole {
      value_expr: OwningChild<HirExprId>,
      display_evidence: ResolvedEvidenceRef,
      shorthand_projection: Option<RootOnceProjection>,
      temporary_cleanup: CleanupObligationSet,
    }

InterpolationPlan {
  segments_in_source_order: [InterpolationSegment],
  eval_order: [NonOwningUse<HirExprId>],
  final_type: String,
  publication: CommitFinalStringAfterAllSegments,
  rollback: ReverseTemporaryCleanup,
  forbidden_observations: Locale | Provider | Serialization | Redaction,
  outcome: ResponsibilitySummary,
}
```

각 hole은 정확히 한 번 평가하고 모든 segment가 성공한 뒤에만 final String을 publish한다. 앞선 hole의 temporary는 뒤의 실패에서 reverse order로 정리한다. locale/provider/serialization/redaction을 숨겨서 관찰시키지 않는다.

반면 colon format-spec의 grammar, argument mapping, width unit, padding/truncation, invalid-format outcome은 현행 정본에서 닫히지 않았다. `DeferredFormatSpec`은 `AnalysisHir`에만 있을 수 있고 `CanonicalHirH1`로 seal할 수 없다. 이는 lowering 구현 부재가 아니라 언어 의미 부재이므로 MIR capability gate로 늦춰서는 안 된다.

## 16. Cleanup과 control exit

```text
HirCleanupScope {
  scope_id: HirScopeId,
  parent: Option<HirScopeId>,
  budget: CleanupBudget,
  registrations: [HirCleanupRegistration],
}

HirCleanupRegistration {
  registration_site: HirNodeRef,
  action: ResolvedCleanupAction,
  capture_eval_order: [CapturePreparation],
  profile: CleanupProfile,
  disposition: StackOwned | SealedToOwner,
}

HirControlExit {
  target: ControlTargetId,
  payload: Option<HirExprId>,
  outcome_kind: Normal | Error | Defect | Cancel,
}
```

HIR는 lexical cleanup scope, 등록 시점, capture 책임, defer/rollback/finally 종류, semantic target을 보존한다. 각 exit에 cleanup depth나 복제된 cleanup block을 기록하지 않는다.

MIR lowerer가 scope ancestry로 `LeavePlan`을 계산하고 logical cleanup stack operation을 만든다.

필수 불변식:

- cleanup capture는 등록 시 source order로 평가한다.
- LIFO와 exactly-once를 잃지 않는다.
- return payload의 owned transfer와 cleanup 실행 순서를 분리한다.
- suspension은 live cleanup scope를 보존한다.
- cleanup 자체의 effect/error/defect/cancel/suspend budget을 검증한다.
- primary/suppressed outcome 결합 규칙 자체가 current authority에서 닫히지 않았으면 canonical sealing에서 거부한다. 규칙은 닫혔지만 ProposedMirX1 lowering만 없을 때에만 MIR capability gate에서 거부한다.

## 17. Closure

```text
ClosurePlan {
  body_owner: BodyOwnerId,
  callable_profile: CallableProfile,
  captures_in_source_order: [CaptureDescriptor],
  escaping: EscapingProfile,
  call_kind: Reusable | Once,
  environment_type: NormalizedTypeId,
}

CaptureDescriptor {
  captured: ResolvedRef,
  mode: Borrow | Inout | Move | Copy | Clone | Deep | Once,
  preparation: [CapturePreparation],
  selected_evidence: Option<ResolvedEvidenceRef>,
  responsibility: ResponsibilitySummary,
}
```

- callable-level `once`와 capture-level `once`를 구분한다.
- clone/deep capture 준비의 effect/failure/rollback은 closure 설치 전에 명시한다.
- capture 순서는 source order다.
- escaping closure의 borrow/suspend/isolation 위반은 canonical sealing 전에 거부한다.
- trailing closure는 별도 closure 종류가 아니다. 일반 `ClosurePlan`이 call/message의 trailing-closure channel에 binding된다.

## 18. Async, generator, task, actor

HIR는 state machine이 아니다.

```text
SuspendPlan {
  site: SuspendSiteId,
  kind: Await | Yield,
  payload_type: NormalizedTypeId,
  resume_type: NormalizedTypeId,
  cancellation: CancellationProfile,
  live_region_constraints: [HirRegionConstraint],
  isolation: IsolationProfile,
}

TaskScopePlan {
  scope: TaskScopeId,
  children: [TaskChildPlan],
  lexical_spawn_order: [TaskChildId],
  exit_policy: Join | CancelThenJoin,
  primary_failure_order: LexicalChildOrder,
}
```

- HIR는 await/yield, resume type, cancel/isolation constraint를 명시한다.
- live-across-suspend set, frame field, program counter, root map은 MIR/xVM에서 계산한다.
- scheduler completion order가 primary failure 선택을 결정하지 않는다. lexical spawn index를 보존한다.
- task scope 밖으로 나갈 때 child ownership이 남지 않도록 exit policy를 고정한다.
- actor enqueue/commit 전과 후의 cancellation 책임을 분리한다.

## 19. Provider 경계

```text
ProviderOperationPlan {
  provider: {
    identity: ProviderId,
    version: ProviderVersionId,
  },
  entry: EntryCandidateId,
  authority: AuthorityRequirementSet,
  input_plan: [ProviderInput],
  policy: {
    observation_timestamp: ObservationTimestampPlan,
    rounding: ExactRoundingPolicy,
    recoverable_failures: ErrorSet,
    effects: EffectRow,
    cancellation: CancellationProfile,
    cache_identity: CacheIdentityId,
    cache_key: CanonicalCacheKeyPlan,
    replay_token: ResolvedReplayToken<ReplayTokenId>,
  },
  result_type: NormalizedTypeId,
  outcome: ResponsibilitySummary,
}
```

Dynamic-unit operation은 profile active, provider bound, policy complete, provider supports conversion의 결합을 sealing 전에 증명한다. provider identity와 version, observation timestamp, rounding, exact failure/effect/cancellation policy, cache identity/key, replay token 중 하나라도 열려 있으면 canonical HIR가 아니다. MIR lowerer는 현재 시간, default rounding, ambient cache 또는 새 replay identity를 추측하지 않는다.

Provider 선택과 authority 요구는 HIR에서 닫힌다. 다만 derive-via/provider output은 HIR node, `WitnessId`, authority identity를 직접 주입하지 않는다. 생성된 Deeplus source는 다시 scanner → parser → AST → HIR/checker 경계를 통과해야 한다.

RCTS-V5, module API digest, method/extension trace, pattern registry, MIR responsibility event schema는 HIR 본체가 아니다. HIR-H1에서 생성하는 receipt/projection으로만 사용한다.

## 20. Surface syntax 정규화 표

### 20.1 canonical HIR에서 제거하는 spelling

| Surface form | HIR-H1 |
|---|---|
| rightward binding | ordinary `HirStmtKind::LocalInit` + binding plan, origin에 spelling 보존 |
| field pun | explicit label/value |
| grouped forwarding | owner/key가 있는 generated declaration |
| scoped import/use spelling | selected identity와 activation frame |
| operator glyph | resolved `IntrinsicOpId` 또는 exact callee |
| alias/projection spelling | `NormalizedTypeId`, debug origin에 surface type |
| parenthesized pattern | pattern origin만 보존 |
| raw/multiline string delimiter | final scalar payload, debug provenance |
| interpolation shorthand | root-once explicit projection/render plan |
| comprehension spelling | structured collector/loop plan |
| yield response rightward syntax | `Yield` 뒤 `HirStmtKind::LocalInit` |

direct `let`과 동치인 rightward binding은 같은 semantic digest를 가질 수 있다. debug digest는 다를 수 있다.

### 20.2 제거하면 안 되는 의미 구분

- mutable parameter와 `inout`
- `Record`와 `Map`
- ordinary method call과 actor message
- strict Boolean과 sequential Boolean
- recoverable Error, Defect, Cancellation
- concrete witness와 abstract witness parameter
- import visibility와 use/extension activation
- reusable callable과 once callable
- message payload와 ordinary argument list
- trailing closure의 selected `FormalId`

## 21. HIR에서 MIR-X1로의 계약

### 21.1 lowering은 의미 결정이 아니라 구조 확장이다

| HIR-H1 | MIR-X1 |
|---|---|
| exact normalized type/identity | `MirTypeId`, `StaticIdentity`, exact callee |
| structured `HirCallPlan` | ordered ops + `CallShape` + invoke outcome edges |
| `HirPlacePlan` | `PlaceId`, projection/check edge, loan/access token |
| `HirPatternPlan` | test/probe/guard blocks + atomic `binding.commit` |
| `ConstructionPlan` | `BuilderToken`, field init, rollback/commit |
| `HirCleanupScope` | cleanup region/register + `LeavePlan` |
| `ClosurePlan` | environment construction + call-right token |
| `SuspendPlan` | suspend terminator + liveness/frame/root metadata |
| `TaskScopePlan` | `TaskToken`과 exit join/cancel |
| `MessageCallPlan` | payload/closure eval + selected dispatch; actor subvariant면 transfer commit + actor runtime op |
| `ProviderOperationPlan` | fixed provider/replay/authority operation |
| `SourceOrigin` | MIR provenance projection |

MIR lowerer가 해서는 안 되는 일:

- 이름 또는 selector 검색
- overload ranking
- return type 기반 재선택
- label/trailing-closure formal 결합
- witness/extension/provider 탐색
- hidden coercion 또는 widening
- pattern binder type 재추론
- cleanup 종류 또는 primary outcome 정책 추측
- actor message를 ordinary method로 fallback

### 21.2 full lowering

HIR variant는 둘 중 하나여야 한다.

1. MIR-X1 lowering 규칙이 완전히 정의되어 있다.
2. `MirCapabilitySet`에서 명시적으로 unsupported라서 `ExecutableHirH1` 생성을 거부한다.

silent omission, `todo` pseudo-op, opaque runtime callback은 허용하지 않는다.

```text
require_mir_capabilities(
  Verified<CanonicalHirH1>,
  MirSchemaDigest,
  LoweringRulesDigest,
) -> Result<ExecutableHirH1, CapabilityDiagnostic>
```

이 구분으로 HIR는 현재 인정된 언어 의미 전체를 checker/IDE에 표현하면서도, MIR RFC에서 아직 미결인 의미를 실행 가능하다고 가장하지 않는다.

### 21.3 현 MIR-X1 제안에 필요한 compatibility delta

현재 [`DP-RFC-0001`](./DP-RFC-0001-xvm-only-mir.md)의 `CallShape`와 actor operation에는 live call contract를 lossless하게 받을 자리가 부족하다. 두 제안을 조화시키려면 MIR-X1 채택 전 다음을 보완해야 한다.

1. ordinary call에 ordered trailing-closure channel을 추가한다.
2. 각 trailing closure의 selected `FormalId`를 보존한다.
3. actor message에 ordinary args와 별개의 single payload aggregate를 둔다.
4. payload kind와 payload-to-formal projection을 보존한다.
5. payload 평가 뒤 trailing closures를 평가한다는 순서를 MIR operation stream에 명시한다.
6. `ModuleId`, `AssociatedItemId`, `ExtensionSetId`, `ActivationOriginId`, `FormalId`, `TaskResponsibilityId` 등 필요한 identity projection을 확정한다.
7. concrete `WitnessId`와 abstract `WitnessParamId`를 구분한다.

이 목록은 기존 RFC 파일을 자동 수정하거나 그 제안을 활성화하지 않는다.

### 21.4 HIR/MIR pair 검증

```text
VerifiedHirMirPair {
  hir_semantic_digest,
  mir_semantic_digest,
  mir_schema_digest,
  lowering_rules_digest,
  node_projection_map,
}
```

pair verifier는 digest 문자열만 비교하지 않는다.

1. canonical HIR와 고정 lowering rules로 MIR를 결정적으로 다시 낮춘다.
2. 결과를 canonicalize/verify한다.
3. 제출된 `SemanticMirProjection`의 canonical `semantic_bytes`와 byte-for-byte 비교한다.
4. HIR node → MIR op/terminator semantic provenance를 대조하고, span/spelling debug projection은 별도 debug digest로 검증한다.

현재 semantic authority는 [`spec/mir/semantics.md`](../spec/mir/semantics.md)가 정의한 canonical Deeplus MIR이고 모든 product execution은 `NOT_RUN`이다. `Verified<ProposedMirX1>`는 DP-RFC-0001이 별도로 채택된 미래에만 successor 실행 후보가 될 수 있으며 현재 권위가 없다. 어느 경우에도 HIR digest만으로 실행할 수 없다.

## 22. HIR verifier

검증기는 fail-closed이며 다음 순서로 검사한다.

1. **Envelope**: schema, authority digest, feature set, source role
2. **Static identity**: domain, 중복, stable key, generated owner/key
3. **Type table**: normalized type, projection termination, complete substitution
4. **Item/body**: body store/index 일치, owner/scope/local/control target, owning graph 단일 parent/acyclic/reachability, orphan node 없음
5. **Node typing**: kind signature, exact result type/category
6. **Resolution closure**: unresolved/candidate/inference/recovery variant 없음
7. **Calls**: exact callee/dispatch, unfold aggregate-once projection, channel/formal 일대일성, label, trailing closure, message payload projection
8. **Evaluation**: source ordinal 전순서, evaluate-once, 중복 temp/slot 없음
9. **Place/ownership**: access intent, move/borrow/inout/replace, region constraints
10. **Responsibility**: effect/error/defect/cancel/suspend/isolation/authority/cleanup 재계산
11. **Pattern**: nonconsuming test, probe guard, atomic commit, binder interface, coverage
12. **Construction/cleanup**: initialization/rollback, registration/LIFO, exit target
13. **Closure/async/task/actor/provider**: capture, escape, fresh value binding, per-value task/correlation descriptor, transport, replay, isolation
14. **Canonical form**: table order, ID renumbering, no unknown mandatory field
15. **Digest split**: semantic/API/debug projection과 digest 재계산

첫 결정적 오류를 다음 key로 반환한다.

```text
(diagnostic_id, owner_id, hir_node_ref, verifier_stage, source_origin)
```

hash seed, thread count, query scheduling이 오류 순서를 바꾸지 않아야 한다.

### 22.1 Executable capability verifier

Canonical HIR verifier는 MIR 구현 coverage를 검사하지 않는다. 그 검사를 섞으면 “의미는 닫혔으나 ProposedMirX1 lowering이 아직 없는 HIR”를 표현할 수 없고 `Verified<CanonicalHirH1>`과 `ExecutableHirH1` 경계가 무너진다.

별도 capability verifier만 다음을 검사한다.

1. 요청한 `MirSchemaDigest`와 `LoweringRulesDigest`가 허용된 조합인지 확인한다.
2. reachable HIR variant 각각에 total lowering rule이 있는지 확인한다.
3. lowering 전제조건과 feature bit를 검증하고 `MirCapabilityReceipt`를 발급한다.

따라서 canonical 의미 검증 실패는 `Verified<CanonicalHirH1>` 생성을 막고, MIR coverage 실패는 canonical HIR를 유지하되 `ExecutableHirH1` 생성만 막는다.

## 23. Canonicalization, serialization, digest

### 23.1 canonical form

- static identity는 `StableSymbolKey` 순으로 정렬한다.
- type은 normalized structural key로 intern한다.
- item은 static identity 순으로 정렬한다.
- body는 owner identity 순으로 정렬한다.
- body-local node는 root에서 schema가 정한 child 순서로 semantic traversal하여 재번호를 매긴다.
- source-order 의미가 있는 argument, field, capture, clause, cleanup registration, trailing closure는 정렬하지 않는다.
- map이 필요한 encoding은 deterministic encoded-key order를 사용한다.
- 절대 path, timestamp, process address, hash seed, thread count를 semantic bytes에 넣지 않는다.

직렬화 profile은 [RFC 8949 deterministic CBOR](https://www.rfc-editor.org/rfc/rfc8949.html#section-4.2)의 원칙을 따르는 제안이다. shortest encoding, definite length, canonical key order, decode 후 재인코딩 byte equality를 요구한다.

### 23.2 세 개의 projection

```text
SemanticHirProjection {
  authority,
  features,
  normalized identities/types,
  item signatures,
  complete bodies,
  evaluation/order plans,
  responsibilities,
  semantics-affecting origin identities,
}

ApiHirProjection {
  exported_symbols: [HirApiSymbolRow],
}

HirApiSymbolRow {
  exported_identity,
  kind,
  normalized_signature,
  responsibility_profile: {
    receiver_channel,
    parameter_channels,
    result_channel,
    capture_channels,
    per_channel_task_origin_and_static_task_responsibility,
  },
  ownership,
  cleanup,
  error_set,
  effect_row,
  cancellation,
  suspends,
  authority,
  isolation,
  evidence_ids,
  callable_profile: Option<CallableProfile>,
  labels_and_named_rest_residue,
  construction_row_sha256: Option<Digest>,
  projection_row_sha256: Option<Digest>,
}

DebugHirProjection {
  source files and spans,
  surface spelling,
  desugaring chains,
  local display names,
}
```

`HirApiSymbolRow`는 현행 [`module-api-digest.schema.json`](../schemas/language/module-api-digest.schema.json)의 symbol row를 lossless하게 생성하는 source다. type row의 construction/projection digest, callable row의 callable/named-rest profile, conformance/static-binding의 evidence residue를 schema 조건에 따라 정확히 보존한다. actor-request Task residue는 해당 responsibility channel의 `task_origin = actor_request_admitted`와 static `task_responsibility` descriptor 안에 들어가며 correlation 값 대신 `per_value_non_forgeable` marker를 기록한다. ordinary async Task channel에는 actor descriptor가 없어야 한다. API verifier는 HIR projection으로 해당 current schema payload를 다시 만들고 제출된 canonical API bytes와 byte-for-byte 비교한다.

### 23.3 domain-separated digest

```text
hir_semantic_digest = SHA-256(
  utf8("deeplus.hir.semantic/h1\0") ||
  u64be(len(semantic_bytes)) ||
  semantic_bytes
)

hir_api_digest = SHA-256(
  utf8("deeplus.hir.api/h1\0") ||
  u64be(len(api_bytes)) ||
  api_bytes
)

hir_debug_digest = SHA-256(
  utf8("deeplus.hir.debug/h1\0") ||
  hir_semantic_digest ||
  u64be(len(debug_bytes)) ||
  debug_bytes
)

hir_to_mir_key = SHA-256(
  utf8("deeplus.hir-to-mir/h1-x1\0") ||
  hir_semantic_digest ||
  mir_schema_digest ||
  lowering_rules_digest
)
```

각 item header와 body도 독립 digest를 갖고 module digest는 이들을 Merkle 방식으로 결합한다. debug-only span 변경은 semantic/API cache를 무효화하지 않는다.

## 24. Incremental query 경계

```text
parse_source(SourceFileId) -> CST
lower_ast(SourceFileId) -> AST
collect_item_tree(ModuleId) -> ItemSkeletonTree
generate_declarations(ItemOwnerId) -> GeneratedDeclSet
resolve_item_header(ItemId) -> ResolvedHeader
check_body(HirBodyId) -> TypedHirDraftBody
verify_body(HirBodyId) -> VerifiedBody
project_api(ModuleId) -> HirApiSummary
assemble_module(ModuleId) -> Verified<CanonicalHirH1>
```

필수 invalidation 규칙:

- 함수 body 변경은 그 함수의 body digest와 실제 dependency consumer만 무효화한다.
- 공개 signature 변경은 API digest와 이를 참조하는 body/header를 무효화한다.
- extension activation frame 변경은 해당 `ActivationOriginId`를 참조한 resolution query를 무효화한다.
- witness/conformance 변경은 해당 `WitnessId`/`WitnessParamId` dependency를 가진 body를 무효화한다.
- debug span만 바뀌면 semantic digest는 유지될 수 있다.
- query cache는 semantic truth가 아니다. verifier가 결과를 재검산한다.

## 25. 거부한 대안

| 대안 | 거부 이유 |
|---|---|
| AST node에 type side table만 붙임 | generated declaration, identity domain, call/pattern/cleanup plan을 닫지 못함 |
| 하나의 HIR enum과 `phase` 플래그 | recovery/unresolved node가 MIR 경계로 새기 쉬움 |
| 모든 call을 flat argument vector로 통합 | formal binding과 eval order, trailing closure, message payload 의미 손실 |
| message를 ordinary method call로 lowering | actor/protocol selector domain, mailbox, transfer, correlation 의미 손실 |
| HIR에서 CFG/SSA 생성 | source-level structure와 incremental/diagnostic 경계를 잃고 MIR와 중복 |
| 모든 identity를 문자열로 저장 | domain 혼합, rename 불안정성, runtime string의 static 승격 위험 |
| raw span을 stable ID로 사용 | 앞부분 편집만으로 identity/cache가 전부 흔들림 |
| flow Phi를 선언 type으로 덮어씀 | Deeplus pattern/type-flow 계약 위반 |
| provider의 HIR 직접 주입 | scanner/parser/checker 및 authority 경계를 우회 |
| unsupported 의미를 opaque runtime op로 전송 | MIR verifier와 xVM이 언어 의미를 추측하게 됨 |

## 26. Capability별 구현 절단면

이는 담당자나 일정이 아니라 의존 가능한 의미 단위다. 모두 현재 `NOT_AUTHORIZED / NOT_RUN`이다.

### H1-A — Core arena와 경계

- phase별 별도 자료형
- item header/body arena
- static/body-local ID newtype
- source origin
- canonical text/CBOR와 envelope/type/ID verifier

완료 조건: recovery HIR가 canonical serializer/lowerer에 전달되지 않으며, canonical round-trip과 hash-seed determinism이 성립한다.

### H1-B — Resolution과 call

- lexical/nominal/extension/witness/type-side identity
- complete substitution
- ordinary call channel과 eval order
- ordered trailing closure
- message payload/selector/formal projection

완료 조건: ambiguous/unresolved/hidden lookup mutant가 모두 sealing 단계에서 거부되고, call/message golden HIR가 current contract와 일치한다.

### H1-C — Type flow와 ownership

- responsibility algebra
- place plan
- pattern test/probe/guard/atomic commit
- construction와 cleanup scope

완료 조건: double evaluation, partial binding/move, overlapping inout, rollback/cleanup 누락 mutant를 verifier가 거부한다.

### H1-D — Closure와 suspension

- capture plan과 call-right
- await/yield
- structured task scope
- actor transfer/correlation freshness
- provider/replay plan

완료 조건: borrow escape, double once call, scheduler-order primary failure, actor ordinary fallback, hidden provider lookup mutant를 거부한다.

### H1-E — MIR handoff

- `MirCapabilitySet`
- total HIR→MIR lowering
- `VerifiedHirMirPair`
- deterministic relowering byte equality
- provenance projection

완료 조건: 지원 HIR variant 전부가 MIR에 lossless하게 투영되고, unsupported 의미는 capability gate에서 결정적으로 거부된다.

## 27. 필수 검증 행렬

| 축 | positive oracle | negative mutant |
|---|---|---|
| Identity | same declaration = same stable key | domain cast, source-order winner |
| Incremental | body edit가 무관한 header/body digest 유지 | whole-module invalidation |
| Call | argument와 trailing closure source order | formal order로 재배열, closure 중복 평가 |
| Message | single payload + static projection | ordinary args 재사용, method fallback |
| Pattern | test→probe→guard→atomic commit | guard 전 move/bind |
| Place | base/index/RHS exactly once | compound assignment double evaluation |
| Cleanup | registration order와 LIFO | double cleanup, lost primary outcome |
| Construction | partial init reverse rollback | publish-before-commit |
| Closure | ordered capture와 exact mode | once/capture mode 혼합 |
| Async/task | lexical failure order, live scope 보존 | scheduler completion order 의존 |
| Actor | fresh producer site, transfer commit | forged/cached correlation identity |
| Provider | fixed provider/entry/authority | runtime string lookup, HIR injection |
| Determinism | OS/hash seed/thread 변화에도 같은 bytes | path/span/timestamp가 semantic digest에 유입 |
| HIR→MIR | deterministic relowering byte equality | digest만 맞춘 다른 MIR payload |

## 28. 의미 closure와 lowering coverage를 혼동하지 않는 규칙

채택 감사에서는 각 feature를 다음 세 부류 중 하나로 분류해야 한다.

| 분류 | Canonical HIR | Executable HIR-H1→MIR-X1 |
|---|---|---|
| 현행 의미가 닫히고 X1 lowering도 있음 | 허용 | 허용 |
| 현행 의미는 닫혔지만 X1 lowering이 없음 | 허용 | capability gate에서 거부 |
| 현행 의미 자체가 미결 | 거부; `AnalysisHir`에만 보존 | 도달 불가 |

현행 canonical MIR에서 strict/sequential Boolean, ternary, core braced/shorthand interpolation, NumericArray transpose view에는 이미 `LAW_PRESENT` 의미가 있다. 이들을 “의미 미결”로 취급해서는 안 된다. ProposedMirX1 문서가 아직 해당 lowering을 완결하지 못했다면 두 번째 부류일 뿐이다.

현재 확인된 interpolation format-spec row는 세 번째 부류다. format text grammar, mapping, width/padding/truncation, invalid-format outcome이 닫히기 전에는 `DeferredFormatSpec`을 canonical HIR node로 만들 수 없다.

`catch/finally`, generator close/cancellation, actor ordering, OOM/stack exhaustion, weak reference처럼 별도 감사가 필요한 영역은 HIR 자료형이 임의 의미를 발명하지 않는다. 채택 시점의 canonical authority가 이미 observable law를 닫았는지 먼저 판정한 뒤 위 분류를 적용한다. GC/RC/arena처럼 관찰되지 않는 backend-private 선택은 애초에 HIR 의미가 아니다.

## 29. R51f3 수 체계 및 정적 capability 보충

이 RFC의 상태는 계속
`DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE`이다. 다만 현행 정본은
HIR-H1의 단계 경계와 verifier 원칙을 채택하고, 아래의 exact residue를
MIR handoff 설계에 결합한다.

- Rational literal은 source spelling과 분리된
  `RationalConst { numerator: BigInt, denominator: BigInt, type_id }`로
  정규화된다. `denominator > 0`, 기약분수, canonical zero가 verifier
  invariant이다.
- 허수 literal은 `ComplexTypeId`, `RepTypeId`, real/imag IEEE component
  bits와 source origin을 보존한다. `4.0i`의 real component는 `+0.0`이다.
- 정적 power는 다음 닫힌 plan이다.

```text
HirIntrinsicPlan {
  eval_order: [base, exponent],
  operands: [{ source_type, adapted_type, adaptation }],
  op: CheckedIntPow
    | FloatPowInt
    | FloatPow
    | ComplexPowInt
    | ComplexPowPrincipal
    | MeasurePowStatic,
  result_type,
  implementation_id,
  responsibility_id,
  numeric_semantics_profile_id,
  special_value_profile_id,
}
```

`adaptation`은 `Identity`, `DirectLiteralToF64Exact`, `F32ToF64`,
`F32ToComplex64`, `F64ToComplex64`만 가능하다. generic `Pow`, expected
result 선택, witness/runtime lookup은 canonical HIR에 남을 수 없다.

`Type::item`, `Type::extension::item`, `<T as Trait>::item`, explicit runtime
owner의 네 lookup domain도 HIR에서 분리된다. Trait-associated 선택은
`TraitId`, `RequirementId`, `ConformanceId`, `TraitWitnessId`,
`ImplementationId`, substitution과 responsibility를 보존한다. 이
보충으로 companion object, class activation, xVM-only backend 전환 또는
제품 구현이 활성화되지는 않는다.

## 30. 최종 채택 기준

HIR-H1 제안은 최소한 다음을 모두 만족할 때만 정본 채택 후보가 될 수 있다.

- current authority와 live delta가 하나의 명시적 canonical revision으로 고정된다.
- `deeplus.hir/h1` schema/version authority가 정식으로 배정된다.
- canonical HIR에 unresolved name, candidate set, inference variable, recovery node가 존재하지 않는다.
- 모든 식/binder/capture/payload에 exact normalized type과 responsibility가 있다.
- call, label, trailing closure, witness, extension, provider, actor selector가 재탐색 없이 닫혀 있다.
- message payload와 ordinary call arguments가 섞이지 않는다.
- pattern, construction, cleanup, task/message transaction이 구조화된 plan으로 lossless하게 보존된다.
- 같은 normalized 의미가 byte-for-byte 같은 canonical HIR를 만든다.
- item/body incremental invalidation과 semantic/debug digest 분리가 검증된다.
- 모든 executable HIR variant에 total MIR-X1 lowering과 adversarial verifier test가 있다.
- HIR→MIR pair는 deterministic relowering으로 검증된다.
- MIR와 xVM에 backend가 의미를 다시 결정해야 하는 opaque hole이 없다.

가장 중요한 경계는 한 문장으로 요약된다.

> **HIR-H1은 “소스에 가까운 마지막 의미 표현”이고, MIR-X1은 “실행에 가까운 첫 의미 권위”다. HIR에서 모든 정적 결정을 닫고, MIR에서는 그 결정을 CFG·Place·token·outcome으로만 전개한다.**
