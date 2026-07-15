# Contributing

1. `current/current-pointer.json`과 `current/authority-map.yaml`을 먼저 읽는다.
2. 하나의 branch/change set은 하나의 RFC, ADR 또는 change request만 다룬다.
3. source shard를 편집하고 generated projection은 generator로 만든다.
4. 문법·frontend·type·MIR·diagnostic·example 중 영향을 받는 항목을 같은 change set에서 닫는다.
5. `python tools/validators/validate_workspace.py`, `cargo check --workspace`, 관련 test를 실행한다.
6. 실행하지 않은 product lane은 `NOT_RUN`으로 남긴다.
7. 보고서는 영문 파일명과 역할 prefix를 사용하고, 상세 분석·대안·acceptance test·handoff를 포함한다.

GitHub 변경은 관련 Issue와 변경 ID를 먼저 만들고 short-lived branch에서 Draft PR로 제출한다. 5개 주요 Work 역할의 검토 보고서는 Library에 보관하며, Git에는 current decision, compact receipt, handoff와 재현 가능한 source만 유지한다.

Commit 예: `spec(DP-RFC-0042): define named-rest HIR channel`.
