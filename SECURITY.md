# Security Policy

현재 Deeplus는 공개 전 설계·구현 준비 단계다. security 또는 soundness 문제는 일반 기능 요청보다 우선하며 P0으로 분류할 수 있다.

- `unsafe`, FFI, authority, resource cleanup, actor isolation, JIT executable memory 변경은 보조 보안 감사자를 지정한다.
- 증거 없는 지원 주장을 security signal로 취급한다.
- 의존성, unsafe block, LLVM/JIT boundary, bytecode verifier 변경은 위협 모델과 negative test를 요구한다.
- 민감한 취약점 세부사항은 공개 RFC가 아니라 제한된 보안 기록으로 시작하고, 수정 후 필요한 범위만 공개한다.

