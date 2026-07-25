# 부록 H — 튜토리얼 조사 방법과 참고 자료

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 이 조사와 문서 구성은 교육 projection이며 모든 product 실행 상태는
> `NOT_RUN`이다.

이 튜토리얼의 구성은 한 언어의 책을 그대로 모방하지 않았다. 서로 다른
교육 장치를 비교하고 Deeplus의 복잡도와 authority 모델에 맞게 다시
조합했다. 참고 자료의 언어 규칙은 Deeplus의 의미 authority가 아니다.

## 1. 책 네 권에서 얻은 구성 원칙

### C# 4.0 — 낮은 진입 경사

*C# 4.0: The Complete Reference*는 짧은 프로그램, 줄별 설명, 실행
결과, 작은 변형을 반복해 처음 배우는 독자가 빠르게 성공하도록 한다.
Deeplus 튜토리얼은 이 장점을 받아들여 Part 01과 02에서 한 번에 한
개념만 추가한다. 다만 특정 IDE나 실제 compiler 성공을 전제하지 않고
design-static 결과로 경계를 표시한다.

### The D Programming Language — 설계 이유와 빠른 참조

이 책은 기능 목록보다 “왜 필요한가”를 먼저 묻고, 빠른 순회 뒤 같은
기능을 심층 재방문한다. 함수와 테스트, 오류와 계약, 메시지 전달과
공유 상태처럼 구별해야 할 개념도 의도적으로 나눈다. Deeplus 과정의
나선형 구조, 각 장의 “문제에서 출발하기”, 빠른 복습표는 이 장점을
반영한다.

### Kotlin in Action 2e — 개념 중심의 나선형 심화

Kotlin 자료는 nullability, generic, lambda, DSL, structured
concurrency처럼 연결된 개념을 의존 순서에 따라 반복해 심화한다.
Deeplus에서는 refinement·narrowing·Union·Enum·pattern을 하나의
조기 오류 검출 축으로, actor·cancellation·effect를 하나의 책임 축으로
재구성했다.

### Programming Rust 3e Early Release — 문제와 실패에서 출발

Rust 자료는 완성 프로그램을 먼저 만들고 ownership·move·reference의
필요를 실제 충돌에서 끌어낸다. Deeplus Part 07도 문법 정의보다
“누가 값을 소유하고, 실패하면 누가 정리하는가”를 먼저 묻는다. 참고한
판본은 Early Release였으므로 전체 목차의 완성본이 아니라 프로젝트
투어와 오류 중심 설명 방식의 참고로만 사용했다.

## 2. 공식 온라인 튜토리얼에서 얻은 원칙

- [The Rust Programming Language](https://doc.rust-lang.org/stable/book/)는
  작은 프로젝트와 compiler feedback을 통해 개념을 단계적으로 결합한다.
- [Kotlin Tour](https://kotlinlang.org/docs/kotlin-tour-welcome.html)는
  짧은 학습 단위와 즉시 확인 가능한 예제를 제공하고,
  [Kotlin documentation](https://kotlinlang.org/docs/home.html)은
  학습 경로와 참조 경로를 분리한다.
- [A Swift Tour](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/guidedtour/)는
  먼저 언어 전체를 얕게 순회한 뒤 전체 책의 심층 장으로 연결한다.
- [A Tour of Go](https://go.dev/tour/list)는 짧은 상호작용 단위로
  언어·메서드·generic·concurrency를 나눈다.
- [Go Tutorials](https://go.dev/doc/tutorial/)는 기능별 설명과 별도로
  실제 과업 중심의 안내 프로젝트를 둔다.
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)은
  학습용 handbook과 기계적인 reference의 역할 차이를 명시한다.
- [The Python Tutorial](https://docs.python.org/3/tutorial/)은
  이미 프로그래밍을 아는 독자에게 언어의 고유 표현을 빠르게 보여 준다.

## 3. Deeplus에 맞춘 재구성

Deeplus는 다음 이유로 단순한 “문법 한 번 훑기”보다 긴 과정이 필요하다.

1. 기능 상태가 Current, Preview gated, Preview Design, Recovery,
   Removed로 나뉜다.
2. 타입, pattern, ownership, effect, actor가 독립 기능이 아니라 서로
   증거를 주고받는다.
3. 설계 authority와 제품 실행 증거를 분리해야 한다.
4. 1-based indexing, exact numeric, explicit conformance처럼 익숙한
   언어와 다른 선택의 이유를 충분히 설명해야 한다.

그래서 12개 Part 안에서 **사용 → 정확한 의미 → 시스템 경계**의 세
순회를 만들고, 72개 학습 단위와 4개 독립 종합 프로젝트를 배치했다.
각 장은 허용 사례만이 아니라 거부와 경계 사례를 함께 보여 준다.

## 4. 저작권과 사용 범위

참고 도서의 문장이나 예제를 복제하지 않았다. 목차, 교수법, 설명
순서라는 일반적인 구성 아이디어를 분석하고 Deeplus 규칙과 자체 예제로
새로 작성했다. 이 부록의 링크는 연구 근거이며 Deeplus 의미 규칙의
authority가 아니다. 도서명과 언어·프로젝트 이름은 출처를 식별하기 위한
것이며 각 권리자에게 귀속된다. 온라인 자료는 2026-07-25에 공식 문서
주소를 확인했다.
