# Deeplus 프로그래밍 튜토리얼

> 문서 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> 이 튜토리얼은 현행 Deeplus 정본 설계를 학습하기 위한 한국어 안내서다.
> `Stable` 또는 `Current`라는 말은 언어 설계상 수용되었다는 뜻이며,
> compiler·runtime·tooling·product support가 실행 검증되었다는 뜻이
> 아니다. 현재 product lane은 모두 `NOT_RUN`이다.

Deeplus는 타입 리파인먼트와 narrowing, Union, `def#guard`, Enum,
패턴 매칭, 명시적 Trait conformance, 소유권, actor를 서로 연결해 가능한
오류를 이른 단계에 드러내려는 언어다. 따라서 이 튜토리얼은 기능을
사전처럼 한 번씩 소개하는 데 그치지 않는다. 같은 개념을 세 번 만난다.

1. 먼저 작은 문제를 해결하며 표면을 사용한다.
2. 다음에는 허용·거부·경계 사례로 정확한 정적 의미를 배운다.
3. 마지막에는 ownership·effect·concurrency·HIR-H1/MIR 경계와 함께
   설계 이유를 검토한다.

## 추천 학습 경로

- **처음 프로그래밍하는 독자**: Part 01부터 차례로 읽고 모든 실습의
  “따라 하기”와 “빈칸 완성”을 수행한다.
- **다른 언어 경험이 있는 독자**: 각 Part의 README와 빠른 복습을 먼저
  읽고, 낯선 개념인 1-based indexing, narrowing, conformance,
  ownership, actor 장을 깊게 읽는다.
- **언어 설계 검토자**: Part 12와 상태 부록을 먼저 읽은 뒤 각 장의
  “정본 근거”를 따라간다.
- **구현 기여자**: Part 11의 HIR-H1/MIR 경계를 읽되, 이 문서만으로
  implementation authority가 생기지 않는다는 점을 지킨다.

## 전체 규모

이 과정은 12개 부, 60개 개념 장, 12개 안내 실습, 4개 종합 프로젝트,
8개 참조 부록으로 구성된다. Part 안내 12개까지 포함해 `SUMMARY.md`가
가리키는 문서는 정확히 96개다. 이 중 60개 개념 장과 12개 안내 실습을
합친 핵심 학습 단위는 정확히 72개이며, 짧은 문법 순회보다
상호작용·오류 읽기·설계 경계를 충분히 반복하도록 의도했다.

목차와 진행 순서는 [SUMMARY.md](SUMMARY.md)에서 확인한다.

## 예제를 읽는 법

`deeplus` 코드 블록은 정본 설계를 설명한다. “예상 결과”는 정적 의미의
설명이며 실제 compiler 실행 영수증이 아니다. 거부 예제는 오류를
가르치기 위해 의도적으로 잘못 작성했다. Preview와 Preview Design
예제는 눈에 띄는 상태 상자로 분리한다.

첫 인덱스는 `1`이고, `array`와 `case`는 일반 식별자이며, raw 문자열은
`#raw"..."`로 쓴다. Package와 Module은 서로 다른 단위다. 이런 핵심
차이는 첫 번째 부에서 천천히 익힌다.

## 정본과의 관계

튜토리얼은 학습용 2차 문서다. 정확한 규칙을 확인할 때는
[문법 명세 및 언어 참조서](../grammar-reference/README.md)와
`spec/language.md`, `spec/grammar/deeplus.ebnf`를 함께 본다. 상태나
규칙이 충돌하면 이들 정본 자료가 우선한다.
