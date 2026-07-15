# Deeplus Canonical Workspace

이 저장소는 Deeplus의 일상 작업 정본이다. `0.1.2-baseline.r51f3`의 언어 설계를 Development Management System R1.1로 이관했으며, 기존 버전명 반복 파일 대신 안정 경로를 사용한다. 현재 publication revision은 `r51f3-current-publication-m1.3`이다.

## 현재 사실

- 언어 설계 기준선: `0.1.2-baseline.r51f3`
- 작업 revision: `r51f3-current-publication-m1.3`
- source revision: Git merge commit `b6ff1f6e53ea8a21cfb706864478baa02545d3dd`
- 구현 언어: Rust
- 고유 의미론 정본: Deeplus MIR
- 초기 실행: xVM bytecode interpreter
- 첫 native backend: LLVM AOT
- 후속 backend: LLVM ORC JIT
- 제품 lane: 모두 `NOT_RUN`

Cargo crate는 책임 경계를 고정하는 골격일 뿐 lexer, parser, checker, MIR, xVM 또는 LLVM 제품 지원 증거가 아니다.

## 정본 읽기 순서

1. `current/current-pointer.json`
2. `current/authority-map.yaml`
3. `spec/language.md`
4. 필요한 domain의 exact source (`spec/grammar`, `spec/frontend`, `spec/types`, `spec/mir`)
5. `examples`와 `tests/conformance`

대형 feature, diagnostic, predicate 및 example registry는 개별 source shard로 이관되었다. `python tools/generators/export_legacy_catalogs.py --output dist/generated`로 R51f3 호환 projection을 재조립할 수 있다.

## 기본 검증

```text
python tools/validators/validate_workspace.py
cargo check --workspace
cargo test --workspace
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
