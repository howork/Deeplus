# Design Deeplus Codex Design_ Authority Transition R1

## 1. 판정

`AUTHORITY_TRANSITION_READY_FOR_PROMOTION`

이 기록은 활성 **Deeplus 구현 준비도 완성 Goal**과 그 안의 bounded
promotion cycle에 한해, 사용자가 명시적으로 위임한 Design_ 통합·판정·
정본화 권한을 Codex Design_에 결속한다. 기존 언어 의미를 바꾸거나,
production 구현을 시작하거나, 실행 증거 없이 P0/P1 또는 product lane을
폐쇄하는 문서가 아니다.

## 2. 기준선과 증거 경계

| 항목 | 값 |
|---|---|
| repository | `howork/Deeplus` |
| branch | `main` |
| verified publication baseline | `cfd5946c52571119564b9c8beb430f8dd0356750` |
| exact tree | `db6044e2764ea42de8fa63d904ea88568a4d7d31` |
| baseline disposition | PR #44 병합 후 live/local main 일치 |
| semantic P0 | 기존 상태 유지 |
| feature P1 | 정확히 22 OPEN 유지 |
| product lanes | 정확히 15/15 `NOT_RUN` |

이 전환은 repository-static governance와 GitHub workflow authority만
다룬다. parser, checker, HIR, MIR, xVM, Cranelift, formatter/LSP 또는
conformance product 실행 영수증을 만들지 않는다.

## 3. 위임 범위와 supersession

현재 Goal이 지속되는 동안 Codex Design_은 다음을 수행할 수 있다.

- cross-role 결과 통합, gap/P0/P1 판정과 closure gate 관리
- canonical specification·registry·governance 후보의 정본화 판정
- 승인된 promotion cycle의 branch, commit, push, PR, merge와 readback
- 정본과 충돌하는 GitHub Issue의 bounded correction

이 위임은 같은 범위에서 활성 상태였던 “ChatGPT Design_만 최종
판정한다”는 운영 제한을 supersede한다. 다만 과거 ChatGPT Design_의
receipt, candidate, immutable pack과 당시의 역할 표기는 역사적 evidence로
그대로 보존한다. 이 전환은 다음 권한을 자동으로 만들지 않는다.

- production compiler/runtime/backend/tooling 구현
- feature P1 closure 또는 Stable/activation 승격
- publication, release 또는 product-support PASS
- 실행하지 않은 validator/test/product lane의 PASS

효력은 사용자의 명시적 철회, 이 Goal의 완료 또는 후속 governance
authority가 있을 때까지 이 Goal의 promotion cycle에 한정된다.

## 4. bounded truth-map 전환

| 항목 | 전환 전 | 전환 후 |
|---|---|---|
| pointer publication commit | historical `b6ff1f6e…` | verified main `cfd5946c…` |
| audited document-consistency base | historical `4c85d5b9…` | 변경 없음; current cluster baseline과 별도 identity |
| obsolete Library source snapshot | M1.2 bytes를 current pointer에 노출 | `null`; historical receipt는 그대로 보존 |
| `SFD-P1-009` closure authority | `ChatGPT Design_` | `Codex Design_` |
| `SFD-P1-009` 상태 | `OPEN P1 / NOT_RUN` | 변경 없음 |
| 실행 owner | `Impl_ + Test_` | 변경 없음 |
| exact feature P1 | 22 OPEN | 변경 없음 |
| product lanes | 15/15 `NOT_RUN` | 변경 없음 |

`publication_authority_source`는 실제로 존재하고 검증된
`cfd5946c…`를 가리킨다. `audited_implementation_baseline`의
`4c85d5b9…`는 과거 document-consistency repair base라는 별도 identity로
보존한다. M1.2 Library snapshot receipt도 immutable history로 남기되,
그 bytes를 current snapshot으로 오해하지 않도록 pointer 필드는 `null`이다.
이 PR 자신의 아직 존재하지 않는 merge SHA를 미리 기록하지 않는다.
`candidate_binding.current_binding`은 계속 `false`,
`self_binding_forbidden`은 계속 `true`이다. 전환 merge identity는
post-merge readback/receipt에서 별도로 기록한다.

## 5. SFD-P1-009 불변 조건

`SFD-P1-009`는 target-bound executable evidence를 요구하는 단 하나의
SFD OPEN P1이다. `SFD-P1-001..008`의 기존 정적 폐쇄는 되돌리지 않는다.
Codex Design_은 다음이 모두 결속된 실제 receipt가 있을 때만
`SFD-P1-009` closure를 판정할 수 있다.

- exact baseline, toolchain, target와 command
- exact positive/negative/boundary fixtures
- parser/checker/runtime/tooling별 output
- lane별 evidence와 재현성

이번 authority transition에는 그런 실행이 없으므로 closure count는 0이다.

## 6. Issue #24 전환

2026-07-29T19:19:45Z의 live read에서 Issue #24는 `OPEN`, label 0,
comment 0이었다. 원래 제목과 본문은 current backend authority를 LLVM
AOT/LLVM ORC JIT으로 적고 있어 현재 main과 충돌한다.

정본은 다음과 같다.

- Deeplus MIR: 유일한 실행 의미 authority
- xVM: 초기 개발·검증·REPL 경로
- Cranelift ObjectModule AOT: 최초 native backend
- Cranelift JITModule: 후속 in-memory JIT 경로
- MIR-X1 xVM-only RFC: `DRAFT_PROPOSAL_NONCANONICAL_NONACTIVATABLE`

Issue의 역사적 본문은 삭제하거나 덮어쓰지 않는다. authority-transition
PR의 merge/readback 뒤 제목을 current Cranelift authority에 맞게 고치고,
정본 commit과 위 규칙을 연결하는 correction comment를 추가한다.
미래의 xVM-only 채택 여부는 여전히 미결이므로 Issue는 `OPEN`으로
유지하고, 근거 없는 label도 만들지 않는다.

## 7. promotion gate

다음 조건을 모두 만족해야 이 전환을 병합한다.

1. `SFD-P1-009`가 정확히 한 건의 OPEN P1이며 15 lane이 모두 `NOT_RUN`이다.
2. pointer의 publication target `cfd5946c…`와 역사적
   document-consistency audit base `4c85d5b9…`가 각각 실제 Git commit
   object로 존재하고, 두 identity의 서로 다른 역할과 ancestry가 검증된다.
3. Design_ memory의 Goal-scoped authority와 history-preservation fence가
   기계적으로 검증된다.
4. current decision index가 현재 active adoption 문서와 일치한다.
5. current integrity, workspace validator, mutation tests, Cargo checks와
   GitHub CI가 통과한다.
6. merge 후 live main SHA/tree와 Issue 상태를 다시 읽는다.

이 전환이 닫히면 R4 Name Resolution·Modules·Package/Visibility frozen
candidate를 새 closure SHA에 재기준화한다.
