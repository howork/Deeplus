# Changelog

## r51f3-repository-bootstrap-m1.2 — 2026-07-15

- GitHub를 일상 source authority로 사용하는 R1.1 canonical workspace를 도입했다.
- 기존 M1.1 Library snapshot의 불변 identity와 GitHub 운영 revision을 분리했다.
- candidate/current XOR, CODEOWNERS, change request, PR template, Dependabot 및 CI gate를 추가했다.
- Rust 1.85.0 toolchain과 workspace lockfile을 고정했지만 제품 lane은 모두 `NOT_RUN`으로 유지했다.
- 언어 의미, feature status, grammar, type system 및 MIR observable semantics는 변경하지 않았다.

## r51f3-migration-m1.1 — 2026-07-15

- `EX-R48E1-031`, `EX-R51c-018`을 stdlib profile에 맞게 `accept`로 정정했다.
- example outcome을 `accept=363`, `reject=291`, `accept_with_gate=2`로 닫았다.
- candidate 검토 중에는 current pointer를 발행하지 않는 gate-first 절차를 적용했다.
- 언어 의미와 feature status는 변경하지 않았으며 제품 lane은 모두 `NOT_RUN`이다.

## r51f3-migration-m1 — 2026-07-15

- `0.1.2-baseline.r51f3`의 언어 의미를 변경하지 않고 안정 경로 작업공간으로 이관했다.
- 사람용 spec, exact grammar, frontend model, type system, MIR semantics, Prelude, examples를 분리 정본으로 유지했다.
- feature 681, diagnostic 1,251, checker predicate 245, example 656, no-go 150을 source shard로 분해했다.
- R1.1 거버넌스, 역할 prompt, RFC/ADR template, current pointer 및 authority map을 도입했다.
- Rust compiler/xVM/LLVM crate 책임 골격과 workspace validator를 추가했다.
- 제품 lane은 모두 `NOT_RUN`으로 유지했다.
