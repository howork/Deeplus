# Governance

Deeplus는 Development Management System R1.1을 따른다. 언어 규칙은 승인된 current decision과 domain authority가 소유하며, 구현 receipt가 규칙을 임의로 바꾸지 않고 spec이 제품 실행을 증명하지도 않는다.

## 주요 역할

| Prefix | 역할 | 필수 릴리스 검토 |
|---|---|---|
| `Design_` | Design and Release Steward | 예 |
| `Spec_` | Language and Type System Architect | 예 |
| `Impl_` | Compiler and Runtime Lead | 예 |
| `Test_` | Conformance and Quality Lead | 예 |
| `Devel_` | Developer Experience and Ecosystem Lead | 예 |

주요 역할은 Work mode를 사용한다. 보안, 성능, FFI, 동시성, 아이디어, 문서 편집 등의 보조 역할은 risk에 따라 Chat mode로 지정한다. Design 역할은 릴리스 시 5개 역할별 review request와 추가 감사자 assignment를 함께 발행한다.

## 변경 문서

- RFC: source/semantic/type/MIR/public contract 또는 lifecycle 변경
- ADR: Rust crate, parser, cache, xVM encoding, LLVM/CI 구현 선택
- Change Request: 의미 불변 문구·링크·test·generated 재생성

P0 soundness, security 또는 authority 충돌은 투표로 무시할 수 없다. 결론이 닫히지 않으면 current rule을 유지하고 GAP으로 기록한다.

상세 운영은 `governance/reports/`와 `governance/policies/management-policy.yaml`을 따른다.

