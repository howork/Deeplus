# Deeplus Canonical Workspace

이 저장소는 Deeplus의 일상 작업 정본이다. `0.1.2-baseline.r51f3`의 언어 설계를 Development Management System R1.1로 이관했으며, 기존 버전명 반복 파일 대신 안정 경로를 사용한다. 현재 브랜치는 GitHub 정본 도입을 검토하는 `r51f3-repository-bootstrap-m1.2` 후보 상태다.

## 현재 사실

- 언어 설계 기준선: `0.1.2-baseline.r51f3`
- 작업 revision: `r51f3-repository-bootstrap-m1.2`
- 구현 언어: Rust
- 고유 의미론 정본: Deeplus MIR
- 초기 실행: xVM bytecode interpreter
- 첫 native backend: LLVM AOT
- 후속 backend: LLVM ORC JIT
- 제품 lane: 모두 `NOT_RUN`

Cargo crate는 책임 경계를 고정하는 골격일 뿐 lexer, parser, checker, MIR, xVM 또는 LLVM 제품 지원 증거가 아니다.

## 정본 읽기 순서

1. 발행 후에는 `current/current-pointer.json`; 검토 중에는 `release/candidate-state.json`
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


## M1.2 repository bootstrap 상태

후보 검토 중에는 candidate state와 current pointer가 동시에 존재하지 않는다. 모든 필수 역할 gate와 GitHub CI가 닫힌 뒤 별도 pointer-only 변경에서 schema-valid current pointer를 생성하고 candidate state를 제거한다. 이 bootstrap은 언어 의미를 변경하지 않으며 제품 lane은 모두 `NOT_RUN`이다.
