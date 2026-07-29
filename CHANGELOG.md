# Changelog

## r51f3-current-cranelift-backend-r1 — 2026-07-29

- xVM을 초기 개발·검증·REPL 경로로 유지하면서 LLVM native backend
  authority를 Cranelift ObjectModule AOT와 Cranelift in-memory JIT로 교체했다.
- Deeplus MIR의 의미 정본 지위와 backend-neutral HIR-H1 경계를 유지하고,
  CLIF·native layout·register·relocation은 검증된 MIR 이후의 비정본
  projection으로 한정했다.
- native projection receipt에 target, ISA settings, module kind, runtime ABI,
  optimization, object/linker 또는 JIT import identity를 결합하도록 했다.
- product lane은 두 native lane의 identity만 교체해 정확히 15개를
  유지했으며, 모든 lane은 `NOT_RUN`이다.
- 기존 OPEN feature P1 22건은 추가·폐쇄·재번호화하지 않았다.

## r51f3-current-trait-operator-refinement-r1 — 2026-07-28

- Adopt the guarded Trait Conformance successor surface: `type ... conforms`,
  repeated nominal `conforms`, `derives`, registered `by auto`, grouped
  `conform` witnesses, and qualified `Trait::member`.
- Expand Stable fixed-glyph conformance to the exact thirteen unary,
  arithmetic, equality, and ordering roles while keeping arbitrary custom
  operators and range hooks closed.
- Complete Rational arithmetic including division and truncation remainder;
  keep Complex unordered and without remainder.
- Enable ordered payload-free nongeneric Enum comparison and semantic-order
  ranges.
- Add explicit-boundary refinement shorthand and monotone chained binder
  Patterns, then update the Korean Grammar Reference, tutorial, and example
  corpus.
- Preserve semantic P0 = 0, the exact 22 OPEN feature P1 set, and product
  lanes 15/15 NOT_RUN.

## r51f3-current-publication-m1.3 — 2026-07-15

- 병합된 M1.2 source revision과 불변 Library snapshot을 `deeplus.current-pointer/v1`로 결속했다.
- `release/candidate-state.json`을 제거하여 candidate/current XOR을 published-current 상태로 전환했다.
- 언어 의미, feature status, grammar, type system 및 MIR observable semantics는 변경하지 않았다.
- 15개 제품 lane은 실제 target-baseline 실행 receipt가 없으므로 모두 `NOT_RUN`으로 유지했다.
- archive-only provenance, 첫 Rust lexer/parser E3 slice, 공개 라이선스와 Actions SHA pinning을 open action으로 승계했다.
- 7개 역할 검토 후 pointer 필수 키·source/snapshot/predecessor receipt·15-lane exact-set·YAML parity·action tracking·role-memory continuity를 보강하고 mutation suite를 expected-diagnostic 18/18로 강화했다.

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
