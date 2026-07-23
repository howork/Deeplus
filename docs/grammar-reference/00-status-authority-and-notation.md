<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# 상태, 권위 및 표기법

## 상태

이 문서는 현행 Deeplus `0.1.2-internal` 설계를 투영한 문서다. 아래에
연결된 정확한 권위 원천을 충실하게 투영하는 범위에서만 규범적이다.
제품 실행 상태는 `NOT_RUN`, 현행 Git 자기 결합은 `false`, 의미론적 P0는
`0`이며, 이 참조서는 기존 기능 P1 집합을 변경하지 않는다.

## 범위

이 참조서는 다음을 다룬다.

- Unicode 소스 텍스트, 토큰, 비의미 토큰(trivia) 및 어휘 목표
- 안정, Preview, 복구 전용 및 제거된 구문 프로필
- 소스 루트, 선언, 식, 문, 타입 및 패턴
- 이름, 가시성, 타입, 소유권, 효과, 오류 및 격리의 허용 규칙
- 평가와 MIR에서 관찰 가능한 동작
- Prelude와 구현 경계
- 현행 진단, 검사기 술어 및 설계 정적 예제

언어에 필요한 시그니처를 넘어 표준 라이브러리를 정의하거나, 구현을
보장하거나, 활성화할 수 없는 설계 자료를 현행으로 만들지는 않는다.

## 규범 용어

**MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY**는 표준 문서에서
통상 사용하는 의미를 갖는다. “거부됨(rejected)”은 명시된 단계에서 해당
프로그램이 현행 허용 언어에 들어갈 수 없다는 뜻이다. “복구
전용(recovery-only)”은 프런트엔드가 진단에 필요한 형태까지는 인식할 수
있지만, 허용된 의미 노드를 방출해서는 안 된다는 뜻이다.

정확한 권위 추적이 달리 명시하지 않는 한 설명, 예제, 설계 근거 및 다른
언어와의 비교는 정보 제공 목적이다.

## 문법 표기법

정확 문법은 EBNF를 사용한다.

| 형식 | 의미 |
|---|---|
| `Name ::= body ;` | 생성 규칙 정의 |
| `"text"` | 정확한 소스 철자 |
| `A B` | A 다음에 B가 옴. 비의미 토큰 정책은 별도 권위가 소유함 |
| `A \| B` | A 또는 B |
| `A?` | A가 없거나 한 번 나타남 |
| `A*` | A가 0회 이상 나타남 |
| `A+` | A가 1회 이상 나타남 |
| `( ... )` | 그룹화 |

`UPPER_SNAKE_CASE` 이름은 스캐너가 방출하는 범주를 나타낸다. 해당
프로필 절의 정의에 따라 `CamelCase` 이름은 어휘 보조 요소 또는 구조
생성 규칙을 나타낸다. 따라서 대소문자는 정확히 구별해야 하며,
`IDENTIFIER`와 `Identifier`는 서로 다른 생성 규칙이다.

EBNF는 다음 책임을 의도적으로 프런트엔드 모델에 위임한다.

- maximal-munch와 스캐너 모드 확정
- 문맥 단어 및 sigil 역할 허용
- 문과 줄바꿈 경계
- Pratt 결합 우선순위와 parselet 등록
- 소스 역할 및 부모 소유자 허용
- CST에서 AST/HIR/MIR로 이어지는 책임
- 복구 소유권과 포매터 정책

따라서 하나의 EBNF 대안에 일치하는 것은 허용의 필요조건이지만
충분조건은 아니다.

## 네 가지 문법 프로필

현행 생성 규칙의 정확한 개수는 다음과 같다.

| 프로필 | 생성 규칙 수 | 역할 |
|---|---:|---|
| `LEXICAL` | 89 | 소스 문자, 토큰, 스캐너 결과 및 비의미 토큰 |
| `STABLE` | 443 | 현행 구조 구문 |
| `PREVIEW` | 13 | 명시적 gate를 거쳐 활성화할 수 있는 Preview 루트 |
| `RECOVERY` | 15 | 진단을 위한 인식에만 사용 |
| **합계** | **560** | 대소문자를 구별하는 정확한 생성 규칙 정의 |

생성기는 EBNF에서 이 값을 산출하며 `frontend-model.json`과 정확히
일치할 것을 요구한다. 숨겨진 제외 목록은 없다.

문법 프로필과 문서 상태 fence는 서로 다른 분류다. 특히 EBNF의
`PREVIEW` 프로필 안에서도 명시적 기능 gate로 도달 가능한 표면은
`PREVIEW_GATED`, 소스 경로와 활성화 권위가 없는 설계는
`PREVIEW_NONACTIVATABLE`로 나뉜다.

`<!-- deeplus-status-fence: <STATUS> -->` 형식의 표지는 그 다음
문자부터 다음
상태 fence 직전까지 적용되며, 뒤에 다른 fence가 없으면 파일 끝까지
적용된다. 즉 fence의 범위는 `UNTIL_NEXT_FENCE_OR_EOF`다. 일반 설명으로
돌아올 때도 `CURRENT` fence를 명시한다. 이 규칙은 gated Preview,
비활성 Preview, 복구 전용 및 제거 표면이 같은 절에 섞여 현행처럼
보이는 것을 막는다.

## Preview 설계 문서화 원칙

Preview 설계는 도입 여부를 실질적으로 검토할 수 있을 만큼 구체적으로
기술해야 한다. 비활성 상태라는 이유만으로 설계의 이름이나 결론만
기록해서는 안 되며, 각 항목은 적용 가능한 범위에서 다음을 포함한다.

- 제안 동기와 해결하려는 현행 제약
- 현행 대안과 구별되는 정확한 구문 후보 또는 API 형태
- 소스 역할, gate, 수용 단계 및 정적 의미 규칙
- 타입, 소유권, 효과, 패턴, 동시성 및 MIR과의 상호작용
- 진단, 복구, 호환성, 이행 및 도구 영향
- 미결정 사항, 거부 대안, 근거 및 활성화 선행 조건

소스 경로가 없는 Preview 설계에는 `PREVIEW_NONACTIVATABLE` 상태 경계를
적용한다. 참조서에 설계를 자세히 수록했다는 사실만으로 해당 설계가
`CURRENT`가 되거나 문법·구현·제품 지원이 활성화되지는 않는다. 활성화는
별도의 승인된 설계 권위, 정확한 소스 루트와 gate, 문법·프런트엔드 모델
결합 및 요구된 구현·검증 증거를 모두 필요로 한다.

## 어휘 문법, 구조 문법 및 의미론

소스 후보는 책임이 구분된 다음 단계를 거친다.

1. **lexical** — Unicode scalar를 손실 없는 토큰과 비의미 토큰으로
   변환한다.
2. **parse** — 하나의 소스 역할 루트가 전체 토큰 스트림을 소비한다.
3. **admission** — 부모 소유자가 문맥 단어, 수식자 및 프로필을
   허용한다.
4. **resolution/type** — 이름, 식별자, 호출 형태, 패턴, 타입 및
   리파인먼트를 검증한다.
5. **ownership/effect** — move, borrow, 정리, 실패, 중단 및 권위를
   검사한다.
6. **link** — 내보낸 식별자, 일관성 및 분리 컴파일 제약을
   검증한다.
7. **runtime** — 구현되고 허용된 프로그램만 관찰 가능한 결과를 낼 수
   있다.

각 진단은 하나의 주된 단계에 속한다. 판정 가능한 앞 단계의 거부를
실행 시간 실패로 대체해서는 안 된다.

## 예제 증거

이 참조서의 모든 Deeplus 예제는 다음 중 하나에 해당한다.

- 검토된 예제 모음에서 `EX-*` 식별자와 함께 복사된 예제
- 해당 예제 모음에서 부록으로 생성된 예제
- 설명만을 위한 예제라고 명시적으로 표시된 예제

`accept` 행은 **현행 정적 설계가 허용함**을 뜻한다. 예제 모음 자체에는
`design_static_product_not_run`이 기록되어 있으며, 이는 파서나
검사기의 실행 증거가 아니다. 거부 예제는 유용한 진단 oracle로
남지만, 이 참조서에 실렸다는 이유로 현행 구문이 되지는 않는다.

## 구성에 참고한 언어 문서

이 참조서의 구성에는 다음과 같은 주요 언어 참조 문서가 참고되었다.

- [Rust Reference](https://doc.rust-lang.org/reference/)는 정확 표기법,
  어휘 구조, 주제별 장 및 통합 문법을 분리한다.
- [Python Language Reference](https://docs.python.org/3/reference/)는
  참조 자료를 자습서와 분리하고 파서에서 산출한 완전한 문법을
  제공한다.
- [Kotlin specification](https://kotlinlang.org/spec/kotlin-spec.html)은
  문법을 타입, 오버로드 해석 및 데이터 흐름 분석과 연결한다.
- [Swift language reference](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/)는
  설명, 예제 및 주제별 문법을 결합한다.
- [Java Language Specification](https://docs.oracle.com/javase/specs/jls/se25/html/index.html)은
  어휘, 구문, 정적, 실행 시간 및 Preview 규칙을 구별한다.
- [Go specification](https://go.dev/ref/spec)은 표기법, 문법, 의미 규칙
  및 예제를 하나의 버전별 참조서에 담는다.

이 문서들은 제시 방식을 정하는 데만 영향을 주며, Deeplus 구문이나
의미론의 원천은 아니다.

## 권위 추적

- 자연어 명세: [`spec/language.md`](../../spec/language.md)
- 정확 EBNF: [`spec/grammar/deeplus.ebnf`](../../spec/grammar/deeplus.ebnf)
- 프런트엔드 모델:
  [`spec/frontend/frontend-model.json`](../../spec/frontend/frontend-model.json)
- 타입 시스템:
  [`spec/types/type-system.md`](../../spec/types/type-system.md)
- MIR 의미론: [`spec/mir/semantics.md`](../../spec/mir/semantics.md)
- 용어:
  [`spec/contracts/normative-terminology.json`](../../spec/contracts/normative-terminology.json)
