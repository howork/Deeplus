# 문서 예제의 host adapter 경계

이 문서는 오래된 조각 예제에 등장하는 `print`, `readLine`, `assert`의
범위를 명확히 한다. 세 이름은 현재 63개 Prelude signature에 포함되지
않으며, 언어 내재 함수나 hard keyword도 아니다.

## 규칙

- `docs/grammar-reference/**`와 `examples/guide/review-corpus.md`의 일부
  조각이 `print` 또는 `readLine`을 선언 없이 쓰는 경우, 그 이름은
  해당 예제 fixture가 공급하는 **문서 host adapter**다.
- 같은 범위에서 선언 없이 쓰는 `assert`는 예제의 기대값을 기록하는
  **test-oracle adapter**다. Deeplus source API나 contract/law 문법이
  아니며, 프로그램이 호출할 수 있는 canonical Prelude 함수를
  정본화하지 않는다.
- 조각 예제의 검토 목적은 주변 문법·타입·흐름 규칙이다. host adapter의
  존재만으로 console API, effect signature, EOF/error policy 또는
  product support를 정본화하지 않는다.
- 완결된 Package나 Module 예제는 console provider를 명시적으로
  선언·import하고 I/O effect와 error policy를 signature에 드러내야 한다.
- 한국어 튜토리얼의 핵심 예제는 가능한 한 순수한 반환값을 사용한다.
  console adapter가 필요한 장은 adapter를 먼저 선언하고, Prelude
  identity라고 설명하지 않는다.

## 왜 즉시 Prelude에 넣지 않는가

`print`는 rendering witness, locale, redaction, buffering, newline,
failure와 I/O effect를 결정해야 한다. `readLine`은 EOF, decoding,
allocation, cancellation과 recoverable error 정책을 결정해야 한다.
이 정책을 생략한 채 이름만 Prelude에 넣으면 초급 예제는 짧아지지만
Deeplus의 책임 가시성 원칙을 훼손한다.

`assert` 역시 failure kind, diagnostic ownership, evaluation policy와
test-runner 결합을 정해야 한다. 따라서 조각 예제의 `assert`는 fixture가
비교를 수행한다는 표기일 뿐, 현행 언어의 assertion 문이나 표준 함수가
아니다.

따라서 현재 해법은 문서 fixture의 placeholder와 정본 API를 분리하는
것이다. 향후 실제 console library profile은 별도 설계·signature·fixture
및 target-bound 실행 증거를 갖춰야 한다. 현재 모든 관련 product lane은
`NOT_RUN`이다.
