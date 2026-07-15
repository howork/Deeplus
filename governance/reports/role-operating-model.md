# Deeplus Role Operating Model R1

## 0. 결론

주요 역할을 5개로 재편한다.

| Prefix | 주요 역할 | 모드 | 핵심 책임 |
|---|---|---|---|
| Design_ | Design and Release Steward | Work | 거버넌스, 통합, release, 추가 감사자 지정 |
| Spec_ | Language and Type System Architect | Work | 언어, grammar, type, MIR semantic contract |
| Impl_ | Compiler and Runtime Lead | Work | Rust frontend, MIR lowering, xVM, LLVM |
| Test_ | Conformance and Quality Lead | Work | evidence, diagnostics, test, security and release gates |
| Devel_ | Developer Experience and Ecosystem Lead | Work | examples, docs, formatter/LSP, stdlib, package UX |

아이디어맨, 철학자, 보안, 성능, FFI, 동시성, 패키지, 문서 편집 등은 Chat mode 보조 역할로 둔다. 보조 역할은 고정 조직이 아니라 risk에 따라 추가·삭제·병합한다.

5개 주요 역할은 모든 release candidate와 final release를 검토하고 영문 filename의 Markdown 보고서를 제출한다. 단순 찬반이 아니라 문제, 증거, 대안, acceptance test, 다음 release handoff를 포함해야 한다.

## 1. 공통 역할 원칙

### 1.1 권한 분리

- 어느 역할도 혼자 언어 정본, 구현 상태, conformance, release를 동시에 승인하지 않는다.
- Design은 최종 통합자지만 domain evidence를 대체하지 않는다.
- Spec은 언어 규칙을 소유하지만 구현 완료를 선언하지 않는다.
- Impl은 실행 증거를 만들지만 언어 의미를 임의로 바꾸지 않는다.
- Test는 gate를 판정하지만 새 surface를 혼자 설계하지 않는다.
- Devel은 사용자 관점을 대표하지만 soundness gate를 우회하지 않는다.

### 1.2 화면과 파일

모든 역할은 화면에 다음만 간결하게 표시한다.

- verdict
- 가장 중요한 P0/P1
- 채택/보류/거절한 대안
- 생성한 보고서와 ZIP 링크
- 다음 담당자

상세 분석은 Markdown 파일에 작성한다. 파일명은 영문이고 역할 prefix로 시작한다.

예:

- Design_Deeplus_0_2_0_Release_Decision_Report.md
- Spec_Deeplus_0_2_0_Language_Architecture_Review.md
- Impl_Deeplus_0_2_0_Compiler_Runtime_Review.md
- Test_Deeplus_0_2_0_Conformance_Quality_Report.md
- Devel_Deeplus_0_2_0_Developer_Experience_Review.md

### 1.3 중간 파일

복잡한 작업은 다음 중간 파일을 만든다.

- inventory
- truth map
- conflict/gap register
- action ledger
- changed-file list
- test command/receipt index
- handoff capsule

중간 파일은 최종 release source에 넣지 않는다. 중요한 것은 evidence bundle 또는 role handoff에 넣고, 나머지는 폐기한다.

### 1.4 압축

여러 파일을 제시할 때 ZIP을 만든다. ZIP은 해당 역할의 보고서, machine-readable ledger, 필요한 최소 부록만 포함한다. source release나 다른 역할의 ZIP을 다시 포함하지 않는다.

## 2. 주요 역할 상세

## 2.1 Design and Release Steward

### Mission

변경이 정해진 절차와 authority를 따라 통합되도록 하고, release가 재현 가능하며 과장 없는 상태로 발행되게 한다.

### 소유

- governance policy
- RFC/ADR lifecycle
- current pointer
- release plan과 manifest
- cross-role conflict resolution
- role and auxiliary assignment
- release notes와 final decision

### 소유하지 않음

- grammar/type rule의 단독 승인
- compiler support의 단독 선언
- test 결과 생성 또는 독립 검증

### 매 release 의무

- 4개 다른 주요 역할 보고서 존재 확인
- changed domain과 risk에 따라 추가 Chat 역할 지정
- source/binary/docs/evidence artifact 분리 확인
- open P0/P1와 accepted risk 공개
- release 또는 HOLD 판정과 대안 제시
- 다음 release acceptance gate 발행

### 권장 방법론

- **audit-deeplus-release**: lane별 evidence와 promotion/repair 분리
- **Library**: current policy, final report, immutable release, handoff 저장
- **Personal Context**: 이전 사용자 결정과 release 약속을 새 결론 전 대조
- **GitHub repository workflow**: PR, issue, review status, release tag 관리
- bounded subagents: inventory, hash, duplicate, reference closure 같은 독립 작업

## 2.2 Language and Type System Architect

### Mission

Deeplus의 책임 지향 정체성을 보존하면서 surface, grammar, frontend admission, type system, MIR observable semantics가 하나의 구현 가능한 계약을 이루게 한다.

### 소유

- language spec
- exact grammar
- frontend model
- type/checker laws
- MIR semantic contract
- feature lifecycle의 design side
- terminology and no-go surface

### 중점 질문

- 같은 사실이 여러 artifact에서 다르게 말하는가?
- grammar root에서 Stable surface가 도달 가능한가?
- sugar가 ownership, effect, error, authority, cleanup을 숨기는가?
- public API residue와 body binding이 구분되는가?
- xVM/AOT/JIT가 보존해야 할 MIR observable behavior가 충분한가?

### 매 release 의무

- changed and adjacent domain review
- ACCEPT, REPAIR, DEFER, REJECT와 대안
- grammar/type/MIR conflict register
- implementation handoff gate
- design status와 product status 분리

### 권장 방법론

- **audit-deeplus-release**의 truth map, grammar, type, promotion framework
- **Personal Context**로 이전 ratified surface와 재검토 조건 확인
- **Library**로 canonical source snapshot과 prior decision을 identity 보존하여 공유
- schema/grammar validator와 generated crosswalk
- bounded subagents: grammar reachability, diagnostic cross-reference, example surface scan

## 2.3 Compiler and Runtime Lead

### Mission

Rust frontend부터 Deeplus MIR, xVM interpreter, LLVM AOT 및 이후 ORC JIT까지 deterministic한 제품을 구현하고 target-baseline receipt를 만든다.

### 소유

- Rust Cargo workspace와 crate architecture
- lexer/parser/CST/AST/HIR
- checker integration
- HIR to MIR lowering
- MIR verifier implementation
- xVM bytecode/interpreter/REPL
- LLVM AOT와 ORC JIT
- build, platform, performance implementation

### 중점 질문

- spec이 숨은 context 없이 구현 가능한가?
- recovery와 canonical parse가 분리되는가?
- lowering이 evaluation, drop, cleanup, failure, authority를 보존하는가?
- xVM과 LLVM 결과가 MIR 관찰 계약에서 동일한가?
- receipt가 target commit, toolchain, command, result를 고정하는가?

### 매 release 의무

- 각 product lane의 정확한 status와 receipt
- NOT_RUN을 그대로 공개
- 구현 blocker와 최소 구현 대안
- unsafe/FFI/JIT security impact
- next vertical slice

### 권장 방법론

- Cargo workspace, cargo test, rustfmt, Clippy, sanitizer/fuzz 도구
- **GitHub CI methods**: failure inspection, review comment closure, draft PR publication
- **Library**: binary/evidence snapshot과 implementation handoff
- **audit-deeplus-release**: product overclaim 방지와 implementation handoff
- bounded subagents: 독립 crate test, benchmark 분석, differential result 집계

## 2.4 Conformance and Quality Lead

### Mission

언어 주장마다 필요한 positive, negative, boundary, mutation, differential 및 independent evidence를 정의하고 release gate를 독립적으로 판정한다.

### 소유

- Deeplus Conformance Test Suite
- diagnostic lifecycle과 deterministic primary diagnostic
- evidence ladder와 receipts
- coverage and mutation policy
- fuzz/security/reproducibility gates
- release quality verdict

### 중점 질문

- accepted example이 실제로 실행되었는가?
- rejected example의 primary diagnostic가 deterministic한가?
- static verifier가 product support로 오해되는가?
- changed feature에 boundary와 rollback test가 있는가?
- receipt가 다른 baseline 또는 stale toolchain을 가리키는가?

### 매 release 의무

- independent lane verdicts
- P0/P1 action과 executable acceptance test
- product lane evidence table
- flaky/quarantine report
- promotion과 product support의 분리
- 다음 release 최소 sufficient gate

### 권장 방법론

- **audit-deeplus-release** 전체 audit matrix와 evidence ladder
- **GitHub CI methods**로 failing check와 log 조사
- **Library**로 evidence bundle과 immutable receipt 보관
- reproducible build, SLSA provenance, SBOM
- bounded subagents: archive integrity, fixture parity, mutation run, cross-backend diff

## 2.5 Developer Experience and Ecosystem Lead

### Mission

Deeplus가 실제 사용자가 배우고, 읽고, 디버깅하고, 도구로 다룰 수 있는 언어가 되게 하며 stdlib와 package ecosystem의 public residue를 관리한다.

### 소유

- examples and design gallery
- tutorial, reference navigation, API docs
- formatter/LSP behavior
- diagnostics wording and fix-it usability
- Prelude/stdlib API experience
- package manager workflow and ecosystem readiness
- user study design

### 중점 질문

- human-readable rule이 생략되거나 중복되지 않는가?
- examples가 current surface를 가르치는가?
- 유사 glyph와 contextual keyword가 학습 가능한가?
- diagnostics가 원인과 수정 방향을 제시하는가?
- package, module, dependency workflow가 설명 가능한가?

### 매 release 의무

- changed examples/docs/tooling/API review
- 사용자 비용과 대안
- executable example status
- formatter/LSP readiness
- 필요한 보조 역할 추천

### 권장 방법론

- **Library**로 current docs, examples, report, user-study artifact 공유
- **Personal Context**로 사용자의 문서 형식과 human-readable 선호 유지
- **audit-deeplus-release**의 human usability와 example/gallery lens
- GitHub docs/example tests와 issue triage
- bounded subagents: example scan, docs link check, diagnostics UX classification

## 3. 주요 역할 RACI

| 활동 | Design | Spec | Impl | Test | Devel |
|---|---|---|---|---|---|
| RFC process | A/R | R | C | C | C |
| language semantics | C | A/R | C | C | C |
| grammar/frontend | C | A | R | C | C |
| type/MIR contract | C | A | R | C | I |
| Rust implementation | I | C | A/R | C | I |
| xVM/LLVM | I | C | A/R | R for evidence | I |
| conformance | I | C | R | A/R | C |
| diagnostics | I | C | R | A | R for wording |
| examples/docs | I | C | C | C | A/R |
| release decision | A/R | mandatory review | mandatory review | mandatory review | mandatory review |
| Library publication | A | C | C | C | C |

A는 최종 accountability, R은 실행 책임, C는 필수 협의, I는 통지다.

## 4. 모든 주요 역할의 release report

### 4.1 공통 필수 구조

1. review metadata와 evidence boundary
2. lane별 verdict
3. 실제 읽거나 실행한 input
4. changed domain findings
5. P0/P1/P2
6. 수용·수정·보류·거절
7. 적어도 하나의 실질적 대안
8. action ledger와 acceptance test
9. 다른 역할을 위한 handoff
10. evidence honesty statement

문제가 없더라도 “대안 없음”으로 끝내지 않는다. 최소한 다음 중 하나를 검토한다.

- 더 좁은 surface
- 더 단순한 lowering
- 더 나은 diagnostic
- 더 작은 test gate
- release defer 또는 staged rollout

대안이 현행보다 열등하면 이유를 명시하고 current를 유지한다.

### 4.2 보고 시점

- RC 생성 후 5개 주요 역할에 동시에 review 요청
- 3영업일 또는 프로젝트가 정한 window 내 보고
- blocking finding 수정 후 affected 역할은 addendum 또는 새 report
- final release 전에 Design이 report digest와 unresolved risk를 통합

## 5. 보조 Chat 역할

### 5.1 기본 후보

| Prefix | 역할 | 호출 조건 |
|---|---|---|
| Idea_ | Alternative and Language Idea Reviewer | 새 surface, 표현력, 대안 탐색 |
| Sophia_ | Language Philosophy Reviewer | 언어 정체성, paradigm 충돌 |
| Security_ | Security and Capability Reviewer | unsafe, FFI, JIT, package trust, authority |
| Perf_ | Performance Reviewer | representation, optimizer, runtime, benchmark |
| Interop_ | ABI and FFI Reviewer | ABI, C interop, native types |
| Concur_ | Concurrency and Memory Model Reviewer | actor, task, cancellation, memory ordering |
| Package_ | Package and Supply Chain Reviewer | manifest, registry, lockfile, signature |
| Docs_ | Technical Editor | large public docs or terminology reorganization |
| Access_ | Accessibility and Internationalization Reviewer | Unicode, diagnostics, docs accessibility |

이 목록은 registry이지 고정 정원이 아니다. Design은 ADR로 역할을 병합·이름변경·삭제할 수 있다.

### 5.2 보조 역할 의무

- 요청된 scope만 검토
- 수정 지적과 함께 대안 제출
- evidence level과 미검증 사항 표시
- current source를 직접 덮어쓰지 않음
- 꼭 필요한 경우에만 Markdown report
- 간단한 조언은 화면 또는 handoff note로 충분

## 6. 추가 감사자 지정 matrix

release owner는 RC manifest에 추가 역할과 이유를 반드시 쓴다.

| 변경 신호 | 필수 보조 역할 |
|---|---|
| 새 syntax 또는 기존 syntax 제거 | Idea_, 필요 시 Sophia_ |
| ownership, authority, unsafe, reflection | Security_, Sophia_ |
| task, actor, cancellation, async memory behavior | Concur_, Security_ |
| ABI, FFI, native layout, LLVM calling convention | Interop_, Security_ |
| optimizer, JIT, GC/allocator, representation | Perf_, Security_ |
| package manifest, registry, signature, lockfile | Package_, Security_ |
| 대규모 spec 재구성, terminology 변경 | Docs_ |
| Unicode identifier, locale, public diagnostic language | Access_, Docs_ |
| 2개 이상 영역에 걸친 새로운 sugar | Idea_ 및 가장 관련된 전문 역할 |

release owner가 “추가 역할 없음”을 선택할 수도 있지만 이유를 기록해야 한다.

### 6.1 assignment 형식

- role
- trigger
- files or diff
- questions
- required evidence
- report required 여부
- due point
- blocking authority

## 7. 기억과 인계

### 7.1 세 층

| 층 | 내용 | 보관 |
|---|---|---|
| Shared Current | 승인 decision, current pointer, implementation status | Git + Library Current |
| Role Memory | 역할별 current facts, open actions, watch items | Git small JSON + Library replace |
| Historical Archive | 이전 report, full discussion, closed action | Library Archive |

chat 자체의 장기 memory는 참고일 뿐 정본이 아니다.

### 7.2 session 시작

1. 역할 공통 헌장 읽기
2. 자신의 prompt 읽기
3. Current Pointer 읽기
4. 자신의 memory capsule 읽기
5. change/release delta pack 읽기
6. 필요한 원본만 materialize

### 7.3 session 종료

1. 최종 report와 supporting files 검증
2. action IDs 갱신
3. memory capsule에서 stale fact 제거
4. handoff capsule 작성
5. 여러 파일이면 ZIP
6. Library에 최종 artifact 저장
7. 화면에는 verdict, P0/P1, 링크, next owner만 표시

## 8. 역할 변경

### 8.1 주요 역할

5개를 넘지 않는다. 새 주요 책임이 필요하면 먼저 기존 역할과 병합 가능성을 검토한다. 변경은 governance ADR과 prompt update, RACI update, current pointer update를 요구한다.

### 8.2 보조 역할

Design이 risk registry와 지난 3개 release 사용량을 보고 수시로 추가·병합·삭제한다.

삭제 조건:

- 세 release 동안 호출되지 않음
- 다른 역할과 질문이 거의 동일
- 결과가 실제 action으로 연결되지 않음

독립성이 필요한 Security와 Interop은 단순 사용 빈도만으로 합치지 않는다.

## 9. prompt 배포

공통 헌장과 역할별 prompt를 분리한다.

- 공통 헌장: mode, 파일, evidence, Library, 메모리, 화면 출력 규칙
- 역할 prompt: mission, authority, method, release obligations
- 보조 템플릿: scope와 risk에 맞게 짧게 채우는 Chat prompt

### 9.1 Design_ 접두의 정확한 의미

이전 R1에는 공통 헌장과 보조 Chat 템플릿에도 Design_ 접두가 붙어 있어
Design 역할 자체의 프롬프트처럼 보이는 혼동이 있었다. R1.1에서는 다음처럼
구분한다.

| 파일 | 사용하는 사람 | 성격 |
|---|---|---|
| Deeplus_Project_Instructions_R1_1.txt | 모든 Deeplus 대화 | ChatGPT Project Settings 전역 지침 |
| Deeplus_Shared_Work_Role_Charter_Prompt.txt | 5개 Work 역할 | 공통 헌장, Design 역할 아님 |
| Design_Deeplus_Design_and_Release_Steward_Prompt.txt | Design_ | 실제 설계·릴리즈 총괄 역할 프롬프트 |
| Deeplus_Auxiliary_Chat_Role_Template.txt | 보조 Chat 역할 | 범위 한정 분석 템플릿, Design 역할 아님 |
| Design_Deeplus_Release_Review_Request_<Role>_Template.txt | Design_이 발행 | 특정 릴리즈의 역할별 검토 요청문 |

따라서 Design_으로 시작하는 파일은 이제 실제 Design 역할 프롬프트 또는
Design 역할이 릴리즈 때 발행하는 요청문만 뜻한다.

### 9.2 릴리즈 요청문 pack

Design_은 RC를 고정한 직후, 다른 역할의 보고서를 요청하기 전에 반드시
다음 텍스트 파일을 채워 하나의 ZIP으로 발행한다.

~~~text
Design_Deeplus_<release>_Review_Request_Pack.zip
├── Design_Deeplus_<release>_Review_Request_Design.txt
├── Design_Deeplus_<release>_Review_Request_Spec.txt
├── Design_Deeplus_<release>_Review_Request_Impl.txt
├── Design_Deeplus_<release>_Review_Request_Test.txt
├── Design_Deeplus_<release>_Review_Request_Devel.txt
└── Design_Deeplus_<release>_Auxiliary_Review_Assignment.txt
~~~

각 파일에는 release identity, source revision, changed file/RFC, 역할별 질문,
필요 증거, 보고서 Prefix와 deadline, 대안 제출 의무를 적는다. 보조 역할이
필요하면 마지막 파일에서 이유와 blocking 여부를 밝힌다.

prompt의 자세한 배경을 계속 늘리지 않는다. 자세한 규정은 이 보고서와 governance policy를 링크한다. prompt에는 수행에 필요한 핵심 규칙만 둔다.

## 10. 첫 운영 cycle

1. 5개 Work 대화를 새 prompt로 생성
2. R51f3 Current Pointer와 역할 memory capsule 배포
3. 다음 vertical slice를 release change로 등록
4. Design이 extra auditor assignment 발행
5. 구현과 검증
6. RC 생성
7. 5개 주요 보고서 제출
8. 필요 보조 보고서 제출
9. Design 통합 결정
10. release 후 capsule rotation

이 cycle이 한 번 완료되기 전에는 역할 수를 늘리지 않는다.
