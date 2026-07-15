# Deeplus Configuration Management and Artifact Lifecycle R1

## 0. 결론

새 형상관리의 중심은 Canonical_Release_Bundle이 아니라 **Deeplus Canonical Workspace**다. 기존 bundle은 당시 상태를 보관하는 immutable snapshot으로만 남기고, 일상 작업은 stable path의 source of truth를 변경한 뒤 generator와 CI로 검증한다.

권장 구성은 다음 네 평면이다.

1. **Git/Cargo workspace**: 유일한 변경 이력과 작업 정본
2. **CI artifact store**: 생성물, test result, receipt, provenance
3. **ChatGPT Library**: 승인 스냅샷, 역할 보고서, 인계 캡슐, 사람 검토 파일
4. **Release archive**: 변경 불가능한 source/binary/docs/evidence 배포물

Library에 모든 중간 생성물을 누적하지 않으며, 각 역할에게 전체 release bundle을 반복 전달하지 않는다. 역할은 current pointer가 지정한 baseline과 자신의 delta context pack만 받는다.

## 1. 기존 방식에서 확인된 문제

R51f3는 self-contained closure를 달성했지만 작업 형상으로는 다음 문제가 있다.

- 모든 파일에 baseline 문자열이 반복되어 작은 수정도 대규모 rename을 유발한다.
- feature, diagnostic, predicate, crosswalk, coverage, example manifest가 서로 같은 정보를 확장해 저장한다.
- 1MB급 JSON이 여러 개이고 전체가 약 9.5MB다.
- 사람 편집 원본과 verifier 입력, 생성 projection의 경계가 불명확해질 수 있다.
- 새 역할이 전체 패키지와 모든 audit history를 읽어야 한다.
- release snapshot이 일상 작업 정본 역할까지 맡아 diff와 ownership이 흐려진다.

따라서 “완전히 병합된 정본”의 의미를 바꾼다.

> fully merged current-canonical은 모든 과거 자료를 한 ZIP에 복제한다는 뜻이 아니다. 현재 Git revision에서 모든 domain authority가 연결되고, 생성 및 검증 명령으로 self-contained release를 재현할 수 있다는 뜻이다.

## 2. 권장 repository 구조

~~~text
deeplus/
├── Cargo.toml
├── Cargo.lock
├── rust-toolchain.toml
├── README.md
├── GOVERNANCE.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── current/
│   ├── language-version.toml
│   ├── authority-map.yaml
│   ├── decision-index.yaml
│   └── implementation-status.yaml
├── governance/
│   ├── roles/
│   ├── policies/
│   └── meeting-notes/
├── rfcs/
│   ├── draft/
│   ├── active/
│   ├── completed/
│   └── archive/
├── decisions/
│   ├── language/
│   ├── implementation/
│   └── governance/
├── spec/
│   ├── language.md
│   ├── grammar/
│   │   ├── deeplus.ebnf
│   │   ├── profiles.yaml
│   │   └── lexical.yaml
│   ├── frontend/
│   │   └── frontend-model.json
│   ├── types/
│   │   ├── type-system.md
│   │   └── predicates/
│   ├── mir/
│   │   ├── semantics.md
│   │   └── schema/
│   ├── diagnostics/
│   │   ├── catalog/
│   │   └── lifecycle.yaml
│   └── compatibility/
├── examples/
│   ├── guide/
│   ├── positive/
│   ├── negative/
│   ├── preview/
│   └── manifests/
├── tests/
│   ├── conformance/
│   ├── differential/
│   ├── mutation/
│   ├── regression/
│   └── fixtures/
├── crates/
│   ├── deeplus-lexer/
│   ├── deeplus-parser/
│   ├── deeplus-hir/
│   ├── deeplus-types/
│   ├── deeplus-mir/
│   ├── deeplus-xvm/
│   └── ...
├── library/
│   ├── prelude/
│   └── std/
├── tools/
│   ├── generators/
│   ├── validators/
│   ├── release/
│   └── xtask/
├── schemas/
├── docs/
│   ├── guide/
│   └── internals/
├── roles/
│   ├── prompts/
│   ├── current-memory/
│   └── handoffs/
├── dist/
└── target/
~~~

**dist/**와 **target/**은 Git에 commit하지 않는다. 릴리즈 때 clean checkout에서 생성한다.

## 3. 정본 계층과 authority map

### 3.1 authority 우선순위

1. 승인된 current decision
2. 해당 domain의 편집 정본
3. 정본에서 생성한 machine projection
4. 실행 test와 receipt
5. 역할 보고서와 historical discussion

실행 receipt는 구현 사실의 최고 증거지만 언어 규칙을 혼자 바꾸지 않는다. 반대로 spec은 제품 실행을 증명하지 않는다.

### 3.2 domain owner

| Domain | Stable path | 편집 주체 | 검증 |
|---|---|---|---|
| human language | spec/language.md | Spec | link, terminology, examples |
| exact grammar | spec/grammar/deeplus.ebnf | Spec | parser grammar check |
| frontend admission | spec/frontend/frontend-model.json | Spec + Impl | schema, lowering crosswalk |
| type system | spec/types | Spec | predicate and fixture validation |
| MIR semantics | spec/mir | Spec + Impl | MIR verifier |
| diagnostics | spec/diagnostics/catalog | Test + Spec | ID, lifecycle, negative tests |
| examples | examples | Devel + Test | compile/run and expected result |
| implementation status | current/implementation-status.yaml | Test + release automation | receipt existence |
| release identity | current/language-version.toml | Design | tag/manifest parity |

### 3.3 source shard 규칙

feature나 diagnostic를 하나의 거대한 JSON array에 직접 편집하지 않는다.

권장 예:

~~~text
spec/diagnostics/catalog/parser/DP-PARSE-0001.yaml
spec/diagnostics/catalog/types/DP-TYPE-0104.yaml
spec/types/predicates/callshape/named-rest.yaml
examples/positive/callshape/named-rest-basic.dp
examples/negative/callshape/named-rest-double-star-decl.dp
~~~

generator는 deterministic order로 다음을 만든다.

- compact catalog index
- frontend crosswalk
- documentation table
- changed-feature fixture set
- release-only expanded registry

source shard의 ID는 파일 이동과 무관하게 안정적이어야 한다.

## 4. 파일명과 버전 정책

### 4.1 repository 내부

repository source는 버전 없는 stable filename을 사용한다.

좋은 예:

- spec/language.md
- spec/grammar/deeplus.ebnf
- spec/frontend/frontend-model.json
- spec/types/type-system.md
- spec/mir/semantics.md

피할 예:

- Deeplus_Grammar_0_1_2_R51f3_Current_Canonical.ebnf
- deeplus-0.1.2-baseline-r51f3-feature-registry.json

### 4.2 release archive

버전은 archive와 top-level release directory에만 둔다.

~~~text
deeplus-language-0.2.0-source.tar.zst
deeplus-toolchain-0.2.0-x86_64-unknown-linux-gnu.tar.zst
deeplus-docs-0.2.0.zip
deeplus-evidence-0.2.0.zip
~~~

release 내부 source path는 repository와 같게 유지한다. archive를 풀고도 baseline 접두어가 모든 파일명에 반복되지 않는다.

### 4.3 독립 compatibility identity

| identity | 변경 시 bump |
|---|---|
| language | source compatibility 의미 변경 |
| spec_revision | 설명·정본 수정 |
| grammar_schema | EBNF machine contract 변경 |
| frontend_model_schema | CST/HIR contract 변경 |
| mir_schema | MIR serialization/semantics contract 변경 |
| xbc_version | xVM bytecode compatibility 변경 |
| diagnostic_catalog | public diagnostic identity/lifecycle 변경 |
| stdlib | public library API 변경 |

하나의 release manifest가 이 identity 조합을 고정한다.

## 5. Git 운영

### 5.1 branch

- main은 항상 releaseable 또는 명시적 dev state다.
- short-lived branch만 사용한다: rfc/, feature/, fix/, docs/, release/.
- 역할별 long-lived branch는 만들지 않는다.
- 한 branch는 하나의 RFC 또는 change request를 참조한다.
- main merge 후 branch를 삭제한다.

### 5.2 commit

commit message에 change kind와 ID를 둔다.

~~~text
spec(DP-RFC-0042): define named-rest HIR channel
impl(DP-RFC-0042): lower named-rest to MIR callshape
test(DP-RFC-0042): add rejected double-star declaration
fix(DP-ISSUE-0191): restore diagnostic lifecycle link
~~~

generated file만 바뀐 commit은 허용하되 generator version과 source commit을 명시한다.

### 5.3 review ownership

CODEOWNERS 또는 동등한 정책으로 domain reviewer를 요구한다. 그러나 domain owner 한 명의 승인이 release review를 대신하지 않는다.

### 5.4 immutable point

- merge commit: 작업 이력
- annotated tag: release candidate와 release
- release manifest: artifact identity
- checksum/provenance: 생성물 identity

발행 tag의 내용은 수정하지 않는다. 오류는 새 patch 또는 replacement release로 처리한다.

## 6. ChatGPT Work와 일반 Chat 운영

### 6.1 Work mode

5개 주요 역할은 Work mode를 사용한다.

- local filesystem에서 실제 파일을 검사하고 변경한다.
- 중간 inventory, truth map, action ledger를 파일로 남긴다.
- 필요한 경우 명확히 한정된 subagent를 사용한다.
- audit-deeplus-release, Library, Personal Context, GitHub/CI 방법론을 역할에 맞게 사용한다.
- 최종 화면에는 핵심 결론과 파일 링크만 표시한다.

Work session은 release 또는 change 단위로 새로 시작할 수 있다. 역할의 영구 기억은 chat transcript가 아니라 current memory capsule과 Library handoff에 둔다.

### 6.2 일반 Chat mode

보조 역할은 Chat mode를 사용한다.

- 한정된 질문, 한정된 artifact, 한정된 위험을 분석한다.
- 전체 repository나 모든 history를 요구하지 않는다.
- 제안은 E1이며 current source를 직접 바꾸지 않는다.
- 필요한 경우 영문 filename과 역할 prefix의 Markdown 보고서를 만든다.
- release owner가 요청하지 않았고 중대한 문제가 없으면 매 release마다 보고하지 않는다.

### 6.3 subagent 규칙

주요 역할의 subagent 사용은 다음을 만족해야 한다.

- 독립적으로 수행 가능한 bounded task
- 명확한 입력과 출력 파일
- 정본 수정 권한 없음
- 결과를 본 역할이 다시 검증
- 같은 파일을 동시에 편집하지 않음
- 결과와 미확인 사항을 handoff에 기록

## 7. ChatGPT Library 구조

권장 Library folder:

~~~text
/Deeplus/
├── 00_Governance/
│   ├── Current_Policies/
│   ├── Role_Prompts/
│   └── Templates/
├── 01_Current/
│   ├── Deeplus_Current_Pointer.json
│   ├── Current_Source_Snapshot.zip
│   └── Current_Documentation.zip
├── 02_RFC/
│   ├── Draft/
│   ├── Active/
│   └── Decided/
├── 03_Reviews/
│   └── <release-id>/
├── 04_Releases/
│   └── <language-version>/
│       ├── Source/
│       ├── Binary/
│       ├── Documentation/
│       └── Evidence/
├── 05_Role_Handoffs/
│   ├── Design/
│   ├── Spec/
│   ├── Impl/
│   ├── Test/
│   └── Devel/
├── 06_Experiments/
└── 90_Archive/
~~~

### 7.1 Current Pointer

Library의 가장 중요한 파일은 작은 Current Pointer다.

포함 필드:

- language version과 spec revision
- Git repository와 commit/tag
- authority map digest
- current source snapshot Library identity
- open P0/P1
- product lane status
- required next review
- 이전 pointer identity

역할 담당자는 먼저 Current Pointer를 읽고 필요한 snapshot과 delta만 가져온다.

### 7.2 Library 저장 정책

저장:

- 승인된 governance 문서
- current source snapshot
- release artifact와 evidence bundle
- 최종 역할 보고서
- handoff/memory capsule
- 중요한 실험 결과

저장하지 않음:

- target directory
- 중간 build output
- 동일한 generated registry의 여러 사본
- 전체 chat transcript
- 새 release 안에 포함된 과거 release bundle
- 임시 압축 해제 directory

### 7.3 파일 identity와 update

- Current Pointer, role prompt, governance policy는 기존 Library identity를 유지하며 새 version으로 replace한다.
- immutable release와 review report는 새 file로 create한다.
- 파일명만 같고 identity가 다른 중복을 만들지 않는다.
- 새 버전으로 replace하기 전 expected current version을 확인한다.
- 삭제보다 archive 또는 Library version restore를 우선한다.

## 8. 역할 간 공유 단위

### 8.1 Release Review Pack

모든 주요 역할에게 전달:

- Current Pointer
- release manifest
- 이전 release 대비 semantic diff
- changed authority files
- changed test summary
- product lane receipts
- open conflict/gap register
- extra-auditor assignment

전체 source snapshot은 필요할 때만 가져온다.

### 8.2 Role Delta Pack

역할별로 추가:

| 역할 | 추가 내용 |
|---|---|
| Design | RFC/decision diff, release readiness |
| Spec | spec/grammar/type/MIR source diff |
| Impl | crate diff, lowering map, execution receipts |
| Test | changed tests, diagnostics, coverage, failures |
| Devel | examples, docs, formatter/LSP, stdlib/API diff |

### 8.3 Handoff Capsule

각 session 종료 때 다음만 남긴다.

- 완료한 decision/action ID
- 변경 파일과 hash 또는 commit
- 확인한 evidence level
- unresolved P0/P1/P2
- 다음 역할이 읽어야 할 최대 10개 파일
- 다음 명령 또는 acceptance test
- 폐기해도 되는 intermediate

## 9. 메모리 관리

### 9.1 역할 메모리 캡슐

각 주요 역할은 **roles/current-memory/<prefix>.json** 한 개를 유지한다.

권장 제한:

- 100KB 이하
- current facts 최대 50개
- open actions 최대 30개
- watch items 최대 20개
- recent releases 최대 3개
- full narrative 금지

각 fact는 ID, statement, authority, source, introduced revision, review date, status를 가진다. 중복 문장을 넣지 않는다.

### 9.2 rotation

- release 완료 시 current capsule을 정리한다.
- 완료 action은 changelog 또는 archive capsule로 이동한다.
- superseded fact는 삭제하지 않고 decision index 링크만 남긴다.
- 이전 3개보다 오래된 release summary는 current에서 제거한다.
- session 시작 시 chat memory보다 capsule과 Current Pointer를 우선한다.

### 9.3 shared memory

공유 메모리는 **current/decision-index.yaml**과 **current/implementation-status.yaml**이다. 역할별 의견은 shared fact가 아니다. 승인 decision과 receipt만 공유 정본으로 승격한다.

## 10. 용량 정책

### 10.1 기본 budget

| 항목 | 권장 상한 | 초과 시 |
|---|---:|---|
| 역할 memory capsule | 100KB | archive와 deduplicate |
| 단일 hand-authored registry shard | 64KB | domain/ID별 분할 |
| Review Pack | 5MB | delta와 optional appendix 분리 |
| Source Release | 25MB | generated/fixture 제외 재검토 |
| Evidence Bundle | 100MB | lane별 분리와 compression |
| 단일 Markdown 보고서 | 2MB | appendix 또는 data 파일 분리 |

상한은 hard limit가 아니라 review trigger다.

### 10.2 중복 방지

- content-addressed hash로 같은 blob 재업로드를 탐지한다.
- manifest는 파일을 embed하지 않고 path와 hash를 참조한다.
- expanded registry는 release evidence에서 한 번만 만든다.
- 예제 code block을 spec, gallery, corpus에 복제하지 않고 example ID로 transclude/render한다.
- source snapshot에는 evidence를 넣지 않는다.
- evidence bundle에는 source를 넣지 않고 source digest를 기록한다.

### 10.3 압축

- 사람 전달용과 Library 호환성이 중요하면 ZIP
- source와 binary 공식 배포에는 tar.zst도 허용
- 압축 archive 내부 path는 상대 경로만 허용
- archive path traversal, absolute path, duplicate basename을 CI에서 검사

## 11. 생성과 검증 pipeline

~~~text
hand-authored source
    ↓ validate
normalized index
    ↓ generate
docs / compact catalog / changed fixtures
    ↓ build and execute
compiler / xVM / LLVM / conformance
    ↓ collect
receipts / logs / provenance
    ↓ package
source / binary / docs / evidence releases
~~~

각 generated artifact header에는 다음을 기록한다.

- generator name/version
- source commit
- input digest set
- deterministic ordering rule
- generated-at은 재현성에 영향을 주지 않는 metadata 또는 별도 receipt에만 기록

generator와 generated output이 어긋나면 CI가 실패한다.

## 12. 릴리즈 매니페스트

필수 필드:

- release identity와 channel
- language/spec/MIR/xVM/stdlib identity
- source commit과 tree hash
- Rust toolchain과 LLVM version
- authority files와 digest
- generated artifacts와 generator
- product lanes: status, evidence level, receipt
- role review reports
- required auxiliary reviews
- open known issues
- SBOM/provenance/checksum

status enum:

- NOT_RUN
- BLOCKED
- FAILED
- PASSED_FOCUSED
- PASSED_INTEGRATED
- PASSED_INDEPENDENT

PASSED_FOCUSED를 production support로 표시하지 않는다.

## 13. R51f3 이관

### Phase 0: freeze

- R51f3 ZIP과 evidence를 immutable archive로 보존
- SHA-256과 Library identity 기록
- 제품 lane NOT_RUN 유지

### Phase 1: import

- R51f3 domain owner 파일을 stable path로 복사
- 모든 R51f3 파일을 repository root에 그대로 풀어 넣지 않음
- authority map으로 어떤 파일에서 어떤 source shard를 추출했는지 기록

### Phase 2: normalize

- feature/diagnostic/predicate/example를 source shard로 분할
- large registry를 generator output으로 전환
- duplicate prose와 historical residue 제거
- R51f3의 locked current syntax를 smoke suite로 고정

### Phase 3: execute

- Rust frontend vertical slice
- feature별 E3 receipt
- implementation status 갱신
- 첫 새 체계 release candidate

### Phase 4: retire old workflow

- 새 변경은 old baseline-numbered file을 직접 편집하지 않음
- old Canonical_Release_Bundle은 archive에서만 참조
- 첫 새 체계 release가 재현되면 old build scripts를 archive

## 14. 형상 감사 gate

release 전 기계적으로 확인한다.

1. 모든 authority path가 존재하고 hash가 맞다.
2. current decision이 정확히 한 domain source에 반영된다.
3. undefined grammar production과 unreachable Stable surface가 없다.
4. generated output이 clean regeneration과 byte-identical하다.
5. diagnostic ID와 example reference가 닫힌다.
6. source, docs, evidence bundle 사이에 금지된 중복이 없다.
7. 모든 PASSED lane에는 target release receipt가 있다.
8. 모든 주요 역할 보고서가 있고 대안과 acceptance test를 포함한다.
9. extra auditor assignment가 manifest에 있다.
10. archive가 clean checkout에서 재생성되고 checksum/provenance가 있다.

## 15. 즉시 채택 항목

- stable repository paths
- Git source authority와 Library exchange/archive 분리
- source shard와 generated projection 분리
- Current Pointer와 bounded role memory capsule
- 4종 release artifact 분리
- target baseline receipt 없는 product claim 금지
- R51f3를 immutable import baseline으로 보존

