# Deeplus Development and Governance System R1

## 0. 문서 목적과 결론

Deeplus는 이제 아이디어 수집 중심 단계에서 언어 정본과 구현이 함께 전진해야 하는 단계로 넘어왔다. R51f3 패키지는 언어 설계의 정적 폐쇄성은 높지만, 검사한 제품 lane은 Rust lexer부터 독립 conformance까지 모두 NOT_RUN이다. 따라서 새 체계의 최우선 목표는 더 많은 문법을 추가하는 것이 아니라 다음 세 가지를 동시에 달성하는 것이다.

1. 언어 규칙의 단일 책임과 변경 경로를 명확히 한다.
2. Rust compiler, Deeplus MIR, xVM, LLVM 구현 증거를 릴리즈마다 누적한다.
3. ChatGPT 역할 담당자가 전체 과거를 매번 다시 읽지 않아도 같은 품질로 협업하게 한다.

채택하는 운영 모델은 다음과 같다.

- RFC 중심 설계이되 모든 변경을 RFC로 보내지 않는다.
- Git 기반 Cargo 모노리포를 작업 정본으로 사용한다.
- ChatGPT Library는 승인된 스냅샷, 보고서, 역할 인계 및 릴리즈 보관에 사용한다.
- 정본 소스, 생성 산출물, 실행 증거, 배포 파일을 분리한다.
- 5개 Work 역할이 모든 릴리즈를 독립된 관점으로 검토한다.
- 제품 지원은 해당 target baseline에서 실행한 receipt가 있을 때만 주장한다.
- 초기 자가호스팅은 추진하지 않는다. Rust 구현과 xVM/LLVM 검증이 먼저다.

## 1. 현황과 증거 경계

### 1.1 확인한 기준선

검토 기준은 0.1.2-baseline.r51f3이다. 인벤토리 결과 패키지는 86개 파일, 약 9.5MB이며 다음 대형 산출물을 포함한다.

| 항목 | 관찰값 |
|---|---:|
| 언어 기능 행 | 681 |
| 진단 행 | 1,251 |
| 예제 행 | 656 |
| checker predicate catalog | 약 0.87MB |
| checker predicate fixtures | 약 1.5MB |
| feature registry | 약 1.2MB |
| diagnostic registry | 약 1.3MB |
| 전체 패키지 | 약 9.5MB |

패키지는 self-contained 정적 설계 패키지다. 그러나 Rust lexer/parser/checker, MIR lowering, xVM, LLVM AOT/ORC, formatter/LSP, stdlib runner, 독립 conformance 및 사용자 연구는 모두 NOT_RUN이다. 이 보고서가 말하는 “현행”은 언어 설계와 패키지 상태를 뜻하며 제품 구현 완료를 뜻하지 않는다.

### 1.2 보존할 구조적 결정

- frontend, lossless CST/AST, typed HIR, MIR, xVM은 Rust로 구현한다.
- Deeplus MIR가 고유 의미론의 정본이다.
- xVM bytecode interpreter를 초기 개발, 검증, REPL의 실행 기준으로 사용한다.
- LLVM AOT를 첫 native backend로 사용한다.
- LLVM ORC JIT는 AOT와 MIR 동등성 검증 후 도입한다.
- 사람용 명세, 정확한 EBNF, frontend model, type system, MIR semantics, diagnostics, Prelude, examples를 별도 정본으로 관리한다.
- package 전체가 self-contained이며, 하나의 거대 spec 파일을 요구하지 않는다.

## 2. 운영 원칙

### 2.1 책임 기반 정본

한 사실은 한 편집 원본만 가진다. 다른 파일은 링크하거나 생성한다.

| 사실 | 편집 정본 |
|---|---|
| 사람에게 설명하는 언어 규칙 | spec/language.md |
| 정확한 표면 문법 | spec/grammar/deeplus.ebnf |
| contextual admission과 lowering | spec/frontend/frontend-model.json |
| 타입과 checker 법칙 | spec/types/type-system.md 및 source shards |
| 관찰 가능한 실행 의미 | spec/mir/semantics.md |
| 진단 ID와 lifecycle | spec/diagnostics source shards |
| Prelude public surface | library/prelude |
| 실행 가능한 예제 | examples 및 tests/conformance |
| 설계 결정 | rfcs 및 decisions |

동일 규칙을 여러 정본에 복사하지 않는다. 인간 문서가 규칙을 설명하고, exact grammar나 machine model을 링크하며, CI가 일치 여부를 검사한다.

### 2.2 증거 기반 상태

다음 상태를 혼합하지 않는다.

| 단계 | 의미 | 허용 주장 |
|---|---|---|
| E0 | 증거 없음 | NOT_AUDITABLE 또는 NOT_RUN |
| E1 | 제안·보고서 | 설계 의도 |
| E2 | 정본·schema·정적 verifier | 정적 폐쇄성과 패키지 일관성 |
| E3 | 기능 단위 실행 | 제한된 parser/checker/runtime 지원 |
| E4 | 통합 제품 실행 | 해당 lane과 baseline에서 통합 지원 |
| E5 | 독립 재현·사용자 연구 | 범위가 명시된 독립 또는 사용성 증거 |

언어 기능의 Stable은 design status다. compiler support는 별도 implementation status다. 둘은 release manifest에서 반드시 다른 필드로 기록한다.

### 2.3 작은 변경, 원자적 통합

- 하나의 change set은 하나의 중심 목적을 가진다.
- syntax, grammar, frontend model, checker, examples, diagnostics를 바꿔야 하는 기능은 한 change set 안에서 함께 바꾼다.
- 역할별 장기 branch를 만들지 않는다.
- 생성 registry를 직접 편집하지 않는다.
- 한 릴리즈가 이전 릴리즈 ZIP을 포함하지 않는다.

### 2.4 사용자의 결정과 재검토

사용자의 명시적 결정은 가장 강한 현재 추정으로 존중한다. 다만 영구 불변의 헌법은 아니다. 다음 중 하나가 나타나면 재검토 RFC를 열 수 있다.

- soundness 또는 security 결함
- grammar나 type system의 풀 수 없는 모순
- 구현 불가능성 또는 과도한 복잡성의 실행 증거
- 실제 사용자 연구에서 반복 확인된 심각한 사용성 결함
- 더 단순한 대안이 같은 표현력을 제공한다는 충분한 비교 증거

재검토 중에도 기존 current rule은 유효하다. 승인되지 않은 보고서가 정본을 덮어쓰지 않는다.

## 3. 거버넌스 구조

### 3.1 세 종류의 변경 문서

#### RFC

다음 변경은 RFC가 필요하다.

- 문법이나 의미론의 비편집 변경
- 타입, ownership, effect, error, resource, authority 규칙 변경
- MIR observable behavior 변경
- Stable surface의 추가·제거·호환성 파괴
- standard library public contract 또는 provider model 변경
- ABI, FFI, package identity, module compatibility 변경
- feature stabilization, downgrade 또는 removal
- 거버넌스와 release policy의 중대한 변경

Rust RFC는 중대한 변경과 일반 수정의 절차를 분리하며, RFC 수락을 최종 구현 승인과 동일시하지 않는다. Deeplus도 이 원리를 채택한다. [Rust RFC process](https://rust-lang.github.io/rfcs/0002-rfc-process.html)

#### ADR

다음은 Architecture Decision Record로 관리한다.

- Rust crate boundary
- parser library 또는 hand-written parser 선택
- data structure, cache, incremental compilation 전략
- xVM instruction encoding
- LLVM integration 방식
- CI runner와 artifact store 선택

ADR은 language semantics를 바꿀 권한이 없다. 언어 의미에 영향을 주면 RFC로 승격한다.

#### Change Request

다음은 일반 change request로 처리한다.

- 뜻을 바꾸지 않는 문장 정리
- typo, link, example label 수정
- 기존 규칙에 대한 추가 test
- 성능 개선 중 관찰 가능한 동작이 불변인 것
- generated artifact 재생성

### 3.2 RFC lifecycle

| 상태 | 진입 조건 | 종료 산출물 |
|---|---|---|
| Draft | 문제와 책임 경계 기술 | RFC 초안 |
| Screening | 중복·범위·대안 확인 | 담당 역할·필수 실험 |
| Design Review | 5개 주요 역할 검토 | 쟁점·대안·위험 |
| Trial | grammar/checker/MIR slice와 예제 | E3 이전의 prototype evidence |
| Accepted | 설계 방향 합의 | accepted RFC, 구현 gate |
| Implemented | target baseline 통합 실행 | E3/E4 receipt |
| Stabilization | Preview 사용성과 호환성 확인 | Stable 제안 |
| Stable | release gate 통과 | 정본과 public commitment |
| Superseded/Rejected | 대체 또는 불수용 | 이유와 대안 기록 |

Accepted는 “구현해 볼 가치가 있음”을 뜻하며 Stable이나 제품 지원을 뜻하지 않는다.

### 3.3 결정 규칙

- Design and Release Steward가 절차와 통합을 책임진다.
- Language and Type System Architect가 언어 정본의 일관성에 동의해야 한다.
- Compiler and Runtime Lead가 구현 가능성과 lowering을 확인해야 한다.
- Conformance and Quality Lead가 기계적으로 닫히는 acceptance test를 승인해야 한다.
- Developer Experience and Ecosystem Lead가 teaching, diagnostics, tooling, stdlib residue를 검토해야 한다.
- P0 soundness/security/authority 충돌은 합의 수로 덮을 수 없다.
- 의견 충돌은 majority vote보다 증거 수준과 domain authority를 우선한다.
- 결론이 안 나면 current rule을 유지하고 GAP으로 기록한다.

## 4. 개발 구조

### 4.1 Cargo 모노리포

현재는 compiler와 specification이 동시에 빠르게 변하므로 단일 저장소가 가장 안전하다. Cargo workspace는 공통 Cargo.lock, 공통 출력 디렉터리, workspace 전체 명령, 공통 metadata와 lint를 제공한다. [Cargo workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html)

권장 crate 경계:

| crate | 책임 |
|---|---|
| deeplus-source | source text, span, source map |
| deeplus-lexer | tokenization과 recovery token |
| deeplus-parser | lossless CST |
| deeplus-ast | typed AST facade |
| deeplus-hir | contextual admission과 normalized HIR |
| deeplus-types | RCTS checker, constraints, effects, ownership |
| deeplus-mir | canonical MIR model과 verifier |
| deeplus-lowering | HIR to MIR |
| deeplus-xbc | xVM bytecode model와 verifier |
| deeplus-xvm | interpreter, debugger, REPL runtime |
| deeplus-codegen-llvm | 공통 LLVM lowering |
| deeplus-aot | AOT driver |
| deeplus-jit | ORC JIT driver, 후속 단계 |
| deeplus-diagnostics | stable diagnostic catalog와 renderer |
| deeplus-fmt | formatter |
| deeplus-lsp | language server |
| deeplusc | compiler CLI |
| deeplus-testkit | fixture, differential, mutation harness |

crate boundary는 책임 경계이지 팀 경계가 아니다. 과도한 미세 crate 분리는 빌드와 변경 비용을 높이므로 실제 의존 그래프를 보고 병합할 수 있다.

### 4.2 MIR 중심 구현 순서

1. source/span과 lexer
2. grammar의 Stable root를 처리하는 parser
3. lossless CST와 AST normalization
4. contextual frontend model과 typed HIR
5. RCTS checker의 최소 핵심
6. Deeplus MIR data model, verifier, textual dump
7. HIR to MIR lowering
8. xVM bytecode와 interpreter
9. xVM 기반 conformance와 REPL
10. LLVM AOT, xVM differential execution
11. formatter/LSP와 package tooling
12. LLVM ORC JIT와 AOT/xVM differential execution

MIR verifier가 준비되기 전에 LLVM backend를 의미론 정본처럼 사용하지 않는다. xVM, AOT, JIT는 같은 MIR 관찰 계약을 구현한다.

### 4.3 자가호스팅 정책

제안된 초기 bootstrap은 채택하지 않는다.

- Deeplus는 아직 공개 전이며 surface와 type system이 계속 변한다.
- compiler를 Deeplus로 다시 쓰면 Rust 구현과 자가호스팅 구현을 동시에 유지해야 한다.
- portability는 Rust와 LLVM target 지원으로 먼저 확보할 수 있다.

자가호스팅은 1.0의 조건이 아니다. 0.3 이후 compiler plugin 또는 표준 라이브러리 일부를 Deeplus로 작성해 비용과 효익을 측정한 뒤 별도 RFC로 결정한다.

## 5. 품질 보증과 CI

### 5.1 변경 단계 gate

| Gate | 모든 변경 | 조건부 변경 |
|---|---|---|
| source hygiene | format, lint, link, schema | license/header |
| spec closure | authority link, term, ID uniqueness | grammar reachability |
| Rust check | cargo fmt, clippy, check | target matrix |
| tests | unit, integration, doc examples | parser/checker/runtime |
| conformance | changed-feature positive/negative | full Stable suite |
| MIR | verifier, dump snapshot | semantic differential |
| security | dependency and unsafe review | fuzz, sanitizer, FFI |
| release | manifest, hashes, provenance | reproducibility |

Cargo는 workspace 전체 unit, integration, documentation test를 공통 명령으로 실행할 수 있다. 문서 예제도 가능한 범위에서 executable doctest 또는 conformance input으로 연결한다. [cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)

### 5.2 CI 등급

#### Fast gate: 모든 change

- source format과 schema
- changed shards에서 generated index 재생성
- cargo check와 관련 unit test
- grammar undefined/reachability 검사
- diagnostic ID와 example reference 검사
- 금지 surface scan

목표 시간은 10분 이내다.

#### Integration gate: main 통합 전

- cargo test --workspace
- Stable parser/checker corpus
- MIR verifier와 xVM focused suite
- example compilation
- snapshot drift
- changed-feature mutation tests

#### Nightly gate

- fuzzing
- sanitizer 또는 Miri 적용 가능한 crate
- performance benchmark
- full conformance
- cross-platform build
- dependency/security scan
- xVM/AOT differential when available

#### Release gate

- clean checkout build
- full Stable suite
- package self-contained closure
- release manifest와 checksum
- SBOM와 provenance
- 서로 다른 두 환경의 receipt를 결합한 reproducible build 비교
- 각 주요 역할의 signed-off report

재현 가능한 빌드는 같은 source, environment, instruction에서 bit-for-bit 동일한 artifact를 재생성하는 것으로 정의하고 hash로 비교한다. [Reproducible Builds definition](https://reproducible-builds.org/docs/definition/)

source content-tree SHA-256은 압축 환경과 독립된 source identity이고, ZIP byte SHA-256은 OS, Python, zlib, zipfile 및 builder fingerprint가 결합된 환경 범위 identity이다. 같은 관찰 환경에서 두 번 byte-identical한 결과는 `SAME_OBSERVED_ENVIRONMENT_REPEAT_PASS`만 입증하며, 실제로 서로 다른 두 environment receipt의 pairwise 비교 전까지 cross-environment byte identity는 `NOT_ESTABLISHED`이다. 이 tooling evidence는 product lane 실행 또는 PASS를 뜻하지 않는다.

SLSA는 source와 build provenance를 단계적으로 강화하는 기준으로 사용하되 초기부터 최고 level을 주장하지 않는다. 첫 목표는 자동화된 build provenance와 검증 가능한 source revision이다. [SLSA v1.2](https://slsa.dev/spec/v1.2/)

### 5.3 실패와 성능 정책

- flaky test는 재실행으로 숨기지 않고 quarantine owner와 expiry를 기록한다.
- benchmark는 절대 수치보다 기준선 대비 회귀를 본다.
- 성능 최적화는 MIR observable equivalence를 유지해야 한다.
- unsafe Rust는 crate-level policy와 safety comment, reviewer를 요구한다.
- FFI, allocator, JIT memory permission, bytecode verifier는 별도 security review 대상이다.

## 6. 릴리즈 체계

### 6.1 버전과 cadence

SemVer는 공개 API가 명확해야 의미가 있고, 0.y.z는 초기 개발 단계다. [Semantic Versioning 2.0.0](https://semver.org/)

Deeplus에는 다음 cadence가 맞다.

- 내부 design checkpoint: 필요 기반, 최대 2주 간격
- implementation integration milestone: 6주
- public preview 이후 minor release: 분기 단위
- patch: 회귀와 보안 수정 시 수시
- emergency security release: 즉시

지금 6개월에서 1년의 major cadence를 강제하면 NOT_RUN lane을 오래 방치할 수 있다. 0.3 공개 전에는 짧은 구현 milestone이 더 중요하다.

### 6.2 독립 버전 축

| 축 | 예 |
|---|---|
| Language | 0.2.0 |
| Spec revision | spec-r1 |
| Compiler | deeplusc 0.2.0-dev.3 |
| MIR schema | mir-v1 |
| xVM bytecode | xbc-v1 |
| Stdlib | 0.2.0 |
| Conformance suite | dcts-v1 |

R51f3 같은 설계 revision을 compiler SemVer로 오해하지 않는다. 새 체계로 이관한 뒤 내부 revision은 Git commit과 spec revision으로 관리한다.

### 6.3 릴리즈 산출물

| 산출물 | 내용 | 금지 |
|---|---|---|
| Source Release | source, normative spec, generator, compact tests | 실행 log, 과거 ZIP |
| Binary Release | compiler/xVM/tool binaries, license, SBOM | source registry 중복 |
| Documentation | rendered spec, guide, API docs | machine fixtures |
| Evidence Bundle | receipts, logs, expanded matrices, provenance | 정본을 대체하는 규칙 |

릴리즈는 변경 불가능하다. 수정은 새 버전으로 발행한다.

릴리즈 후보를 만든 Design_은 검토를 요청하기 전에 5개 주요 역할별
review-request 텍스트와 보조 역할 assignment 텍스트를 하나의 요청 pack으로
발행한다. 이 pack은 각 역할의 입력, 질문, 증거 경계, 보고서 filename, 대안
제출 의무를 고정한다.

## 7. 에코시스템 단계

### Stage A: compiler bring-up

- parser/checker/MIR/xVM
- executable examples
- deterministic diagnostics
- 최소 formatter

### Stage B: 0.3 public preview

- package manifest와 local dependency resolution
- standard library core
- formatter와 LSP 기본 기능
- installation and platform matrix
- language reference와 tutorial

### Stage C: ecosystem growth

- registry service
- signed package metadata
- package audit and yanking policy
- documentation portal
- compatibility and deprecation tooling

중앙 package registry를 compiler bring-up보다 먼저 운영하지 않는다. 먼저 manifest, resolver, lockfile, local/URL source와 signature model을 설계하고 실제 수요가 생길 때 hosted registry를 연다.

## 8. 지표와 의사결정

### 8.1 핵심 지표

- Stable feature 중 E3/E4 구현 증거 비율
- grammar Stable root reachability
- diagnostic-to-negative-test coverage
- spec example executable coverage
- xVM과 LLVM differential pass rate
- release build reproducibility
- open P0/P1 age
- RFC median lead time
- flaky test 수와 quarantine age
- 역할 memory capsule 크기
- Library Current 폴더의 중복률

기능 수 자체는 성공 지표가 아니다.

### 8.2 중단 조건

다음 상황에서는 feature 추가를 일시 중단하고 closure sprint를 실행한다.

- P0가 1개 이상 미해결
- Stable grammar unreachable production 발생
- current/no-go contradiction
- release manifest가 source revision을 재현하지 못함
- 제품 지원 overclaim
- 주요 역할 보고서 미제출
- 두 milestone 연속으로 E3/E4 비율이 증가하지 않음

## 9. 90일 전환 계획

### 0–14일: 정본 이관

- 새 repository skeleton 생성
- R51f3를 immutable import tag로 보관
- stable filename의 normative source로 이관
- current pointer와 decision index 생성
- generated artifact 목록과 source generator 지정

### 15–35일: frontend vertical slice

- lexer와 Stable grammar subset
- CST/AST/HIR 경계
- named-rest, let#lazy, sealed class 등 locked current surface smoke suite
- parser receipt 생성

### 36–60일: checker와 MIR slice

- 핵심 nominal/type/effect/error 규칙
- MIR model과 verifier
- focused positive/negative corpus
- E3 receipt를 feature 단위로 발행

### 61–90일: xVM과 release automation

- bytecode verifier와 interpreter
- examples를 xVM에서 실행
- release manifest, SBOM, provenance
- 첫 새 체계 milestone 발행

## 10. 주요 위험과 대응

| 위험 | 대응 |
|---|---|
| 설계가 구현보다 계속 앞섬 | Stable 승급에 implementation plan과 acceptance test 요구 |
| generated registry가 다시 비대해짐 | source shards만 commit, expanded projection은 evidence bundle |
| 역할 보고서가 서로 복사됨 | 독립 lens와 공통 report schema, 중복 요약 금지 |
| ChatGPT memory가 과다해짐 | bounded capsule, delta packet, release 후 rotation |
| Library가 정본처럼 사용됨 | current pointer는 Git revision을 가리키고 Library는 snapshot만 보관 |
| 사용자 결정이 검증 없이 고착 | strong presumption + evidence-based reconsideration RFC |
| LLVM이 MIR보다 사실상 정본이 됨 | xVM/AOT/JIT differential와 MIR verifier gate |
| 자가호스팅이 조기 목표가 됨 | 0.3 이후 별도 RFC 전까지 scope 제외 |

## 11. 승인 제안

이 보고서를 Deeplus Development and Governance System R1으로 채택한다. 채택 즉시 효력이 있는 것은 변경 절차, 역할 의무, 증거 정직성, source/generated/evidence 분리 원칙이다. 실제 저장소 구조와 자동화는 형상관리 보고서의 전환 계획을 따라 단계적으로 적용한다.
