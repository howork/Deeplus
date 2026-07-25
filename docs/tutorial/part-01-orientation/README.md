# Part 1. Deeplus를 읽는 첫 관점

> **부 상태:** `MIXED_STATUS`  
> **제품 실행:** `15/15 NOT_RUN`

이 부는 Deeplus 코드를 처음 보는 독자가 “무엇을 입력할 수 있는가”보다
먼저 “어떤 자료가 정본이고, 예제를 어느 수준까지 믿어야 하는가”를
판단하도록 돕는다. Deeplus 저장소에는 현행 설계, gate가 필요한 Preview,
활성화할 수 없는 Preview Design, 정밀 진단만을 위한 Recovery 표면이 함께
기록되어 있다. 이 차이를 모르면 문서에 보이는 철자를 곧바로 실행 가능한
기능으로 오해하기 쉽다.

이 부의 모든 예제는 설계 정적 설명이다. 현재 제품 lane은
`15/15 NOT_RUN`이며, 예제의 예상값과 예상 진단은 실제 compiler/runtime
실행 영수증이 아니다.

## 학습 순서

1. [Deeplus와 상태](01-01-language-status.md) — 정본, Preview, Recovery,
   제품 증거를 구분한다.
2. [소스와 진단 읽기](01-02-source-diagnostics.md) — source에서
   CST/AST/HIR로 가는 책임과 첫 진단을 읽는다.
3. [첫 설계 정적 프로그램](01-03-first-design-static-program.md) —
   출력 장치에 기대지 않고 타입이 있는 작은 함수를 만든다.
4. [Package, Module, source role](01-04-package-module-source.md) —
   배포 단위와 이름 공간을 분리하고 세 Stable source root를 배운다.
5. [이름, 바인딩, 블록](01-05-names-bindings-blocks.md) — `let`, `var`,
   lexical scope와 atomic binding을 배운다.
6. [실습: 타입이 있는 인사말](lab-01-typed-greeting.md) — 앞의 내용을
   한 개의 작은 library source로 합친다.

## 이 부의 학습 판정 trace

초보자는 예제를 볼 때 세 질문을 같은 순서로 적용한다. 첫째, 이 표면은
현행·Preview·Recovery 중 어디에 속하는가. 둘째, scanner와 parser가
구조를 만들 수 있는가. 셋째, 구조가 만들어져도 type과 responsibility
검사를 통과하는가. 예를 들어 `private type Count = 1..10`은 현행
type-producing declaration이므로 visibility와 범위를 함께 검사하지만,
옛 철자 하나를 Recovery scanner가 알아본다는 사실은 정상 AST를 만든다는
뜻이 아니다. 이 trace를 종이에 세 칸으로 적는 습관을 들이면 이후 장의
복잡한 진단도 “문법 오류인가, 의미 오류인가, 실행 실패인가”로 나누어
볼 수 있다.

## 흔한 오해와 미니 사례

가장 흔한 오해는 첫 예제를 곧바로 실행 가능한 “Hello World”로 읽는
것이다. 이 부의 미니 사례는 출력 대신 `String` 값을 반환한다. 따라서
배울 대상은 terminal 사용법이 아니라 이름, 타입, 함수 경계와 상태
판정이다. 또 `tutorial::greeting`이라는 ModulePath가 보인다고
`tutorial/greeting.dp`라는 파일 배치를 강제하지 않는다. Package는
배포·의존성·빌드 단위이고 Module은 이름 공간·가시성·소스 구성
단위라는 구분을 끝까지 유지한다.

## 이 부를 마치면

- `CURRENT`가 “제품에서 실행됨”을 뜻하지 않는다고 설명할 수 있다.
- 오류를 runtime failure로 미루지 않고 어느 정적 단계가 거부하는지
  찾아볼 수 있다.
- 함수, 명시적 타입, 보간 문자열로 순수한 값 변환을 작성할 수 있다.
- Package와 Module, 파일 경로와 ModulePath를 구분할 수 있다.
- 블록 안 이름의 수명과 `let`/`var`의 차이를 설명할 수 있다.

## 상태 불변 조건

- semantic P0: `0`
- OPEN feature P1: 정확히 `22`
- 별도 OPEN action: `M13-A002..005`
- product lanes: `15/15 NOT_RUN`

## 정본 찾아가기

- [현재 포인터](../../../current/current-pointer.json)
- [언어 정본](../../../spec/language.md)
- [통합 EBNF](../../../spec/grammar/deeplus.ebnf)
- [상태·권위 참고서](../../grammar-reference/00-status-authority-and-notation.md)
- [프로그램과 Module 참고서](../../grammar-reference/02-programs-modules-and-imports.md)
