# Deeplus Canonical Workspace

이 저장소는 Deeplus의 일상 작업 정본이다. `0.1.2-baseline.r51f3`의 언어 설계를 Development Management System R1.1로 이관했으며, 기존 버전명 반복 파일 대신 안정 경로를 사용한다. 현재 publication revision은 `r51f3-current-publication-m1.3`이다.

## 현재 사실

- 언어 설계 기준선: `0.1.2-baseline.r51f3`
- publication revision: `r51f3-current-publication-m1.3`
- authority source snapshot revision: Git merge commit `b6ff1f6e53ea8a21cfb706864478baa02545d3dd` (`r51f3-repository-bootstrap-m1.2`)
- pointer-containing publication commit/tag: PR #7 merge 후 별도 release receipt에서 확정
- 구현 언어: Rust
- 고유 의미론 정본: Deeplus MIR
- 계획된 초기 실행 경로: xVM bytecode interpreter — `NOT_RUN`
- 계획된 첫 native backend: LLVM AOT — `NOT_RUN`
- 계획된 후속 backend: LLVM ORC JIT — `NOT_RUN`
- 제품 lane: 모두 `NOT_RUN`

Cargo crate는 책임 경계를 고정하는 골격일 뿐 lexer, parser, checker, MIR, xVM 또는 LLVM 제품 지원 증거가 아니다. 이 저장소의 internal current publication은 public release 또는 license grant가 아니다. 공개 사용 조건은 Current Pointer의 `M13-A003`이 닫히기 전까지 미결정이다.

## 정본 읽기 순서

1. `current/current-pointer.json`
2. `current/authority-map.yaml`
3. `spec/language.md`
4. 필요한 domain의 exact source (`spec/grammar`, `spec/frontend`, `spec/types`, `spec/mir`)
5. `examples`와 `tests/conformance`

대형 feature, diagnostic, predicate 및 example registry는 개별 source shard로 이관되었다. `python3 tools/generators/export_legacy_catalogs.py --output dist/generated`로 R51f3 호환 projection을 재조립할 수 있다.

## 기본 검증

```text
python3 tools/validators/validate_workspace.py
cargo check --workspace --locked
cargo test --workspace --locked
```

첫 명령은 정본·shard·권위·개수·해시·경로 폐쇄성을 검사한다. Cargo 명령은 저장소 골격의 Rust 빌드 가능성만 검사한다.

## 변경 규칙

- 의미, 문법, 타입, MIR observable behavior 변경은 RFC를 따른다.
- generated projection을 직접 편집하지 않는다.
- 언어 design status와 product implementation status를 분리한다.
- 릴리스마다 5개 주요 Work 역할의 검토 보고서와 추가 감사자 지정이 필요하다.
- source, documentation, binary, evidence를 서로 다른 artifact로 발행한다.

자세한 규칙은 `governance/`에 있다.


## M1.3 current publication 상태

M1.2 repository bootstrap의 source tree와 GitHub merge commit을 current pointer가 결속한다. `release/candidate-state.json`은 제거되었고 schema-valid `current/current-pointer.json`이 source revision, authority digest, Library source snapshot과 open action을 기록한다. 이 publication은 언어 의미를 변경하지 않으며 제품 lane은 모두 `NOT_RUN`이다.

여기서 M1.3은 publication metadata의 revision이고, 언어 authority source는 M1.2 bootstrap snapshot이다. Current Pointer 파일은 source snapshot commit 자체가 아니라 PR #7이 병합된 main commit 또는 후속 tag에서 읽는다. M1.3의 7개 역할 검토는 `release/evidence/current-publication-m1.3-role-review-index.json`에 보존하고, pointer의 `required_next_reviews`는 발행 후에도 남아 있는 action별 다음 검토만 가리킨다.

Deeplus의 최우선 설계 목표는 programmer intent를 쉽고, 일관되고, 책임성 있게 source로 옮기는 Expressiveness다. 이 원칙의 정본 charter·role prompt 결속은 Issue #8 및 pointer `M13-A005`에서 추적하며, 다음 semantic PR 전에 닫는다.
