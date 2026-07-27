# 부록 B — 상태와 feature 지도

> 상태: `MIXED_STATUS`
>
> 아래 분류는 학습용 projection이다. product lane은 `15/15 NOT_RUN`이다.

## 1. 세 상태를 구분하는 질문

| 상태 | source admission | semantic authority | product PASS | positive 예제 |
|---|---:|---:|---:|---:|
| Current/Stable design | 예 | 예 | 아니오 | 예 |
| Preview gated | gate 조건부 | 제한됨 | 아니오 | gate 표식 필수 |
| Preview Design | 아니오 | 설계 후보 | 아니오 | 검토용으로만 |

“문서에 자세히 쓰였다”와 “활성화됐다”는 같은 말이 아니다. 특히
Preview Design 문서가 풍부해도 parser, checker, HIR, MIR, backend,
formatter, LSP 또는 product support authority를 만들지 않는다.

## 2. Current에서 먼저 배울 축

- `#raw` String과 현행 text/bytes 구분
- Rational `<p/q>`와 Complex `3.0 + 4.0i`
- ordinary identifier `array`, `case`
- Package/Module 구분과 `::` qualified path
- 1-based indexing
- closed Union, refinement, flow narrowing
- 현행 mixed-payload Enum과 marker reachability
- explicit Trait conformance와 fixed-glyph operator
- 함수 `static { ... }` activation
- named `def#async`, structured task, actor
- HIR-H1 verifier boundary와 current xVM/LLVM backend authority

이 목록은 registry 전체를 대체하지 않는다. 정확한 708 feature row는
feature catalog와 문법 참조 부록을 사용한다.

## 3. Preview gated

Preview gated feature는 정확히 세 개다. 이름과 gate 조건은
[Preview gated 장](../part-12-preview-evolution/12-02-preview-gated.md)과
[문법 참조](../../grammar-reference/20-preview-gated-reference.md)가
정본 projection을 제공한다. 이 부록은 숫자를 임의로 늘리거나 새
gate를 발명하지 않는다.

## 4. Preview Design

현재 registry의 Preview Design surface는 49개이며 모두
`PREVIEW_DESIGN_NONACTIVATABLE`이다. 대표적인 주제는 다음과 같다.

- successor Trait/Enum route, `VIA`/`AUTO`, specialization
- child-local 또는 case-local parent witness replacement
- Class type-static scope
- successor collection/context/control surface
- 일부 async callable literal과 concurrency 확장
- raw/ABI, external residual, A3, empty Enum 검토면
- MIR-X1 xVM-only proposal

각 surface의 동기, static semantics, diagnostic, migration, activation
prerequisite를 따로 검토해야 한다. “좋아 보인다”는 이유로 Tutorial
positive Current 예제로 옮기지 않는다.

## 5. governance 불변식

- semantic P0: `0`
- OPEN feature P1: `22`
  - `CE-C-P1-001..006`: 6
  - `CE-E-P1-001..008`: 8
  - `TCC-P1-002..008`: 7
  - `SFD-P1-009`: 1
- 별도 OPEN action: `M13-A002..005`
- product lanes: `15/15 NOT_RUN`

튜토리얼 파일의 존재, 링크 검증, JSON parse, static fixture만으로 이
항목을 닫지 않는다.

## 6. 상태를 잘못 읽는 대표 사례

1. Stable design을 “compiler에서 실행 PASS”로 읽는다.
2. Preview Design example을 복사해 Current source로 쓴다.
3. artifact SHA-256과 Git commit SHA를 비교해 충돌을 만든다.

각 경우에는 먼저 identity domain과 authority source를 확인한다.

## 7. 정본 근거

- `spec/features/gates.json`
- `spec/features/catalog/**`
- [상태·authority·표기법](../../grammar-reference/00-status-authority-and-notation.md)
- [Preview 표면](../../grammar-reference/15-preview-surfaces.md)

상태 판단을 리뷰할 때는 “문서 존재”, “정적 fixture”, “제품 실행”을
각각 별도 열로 기록한다. 이 세 열을 하나의 PASS로 합치지 않는 습관이
Preview와 Current를 안전하게 함께 문서화하는 핵심이다.
따라서 독자는 각 기능의 언어 상태와 실제 제품 지원 상태를 반드시
따로 확인해야 한다.
