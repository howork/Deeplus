# Deeplus 튜토리얼 집필 계약

이 파일은 `docs/tutorial/**`의 편집 계약이다. 독자가 읽는 진입점은
`README.md`와 `SUMMARY.md`이며, 이 파일은 작성자와 검증 도구를 위한
규칙이다.

## 1. 목적과 독자

튜토리얼은 프로그래밍을 처음 배우는 독자부터 언어 구현 경계를 검토하는
독자까지 한 경로로 안내한다. 문법 항목을 나열하는 대신, 작은 문제를
해결하고 실패 사례를 읽은 뒤 정확한 언어 모델로 되돌아오는 나선형
구성을 사용한다.

모든 설명과 본문은 한국어로 쓴다. 코드의 이름은 의미가 분명한 영어를
기본으로 하되, 설명에서 이름의 역할을 풀어 쓴다.

## 2. authority와 상태

튜토리얼은 이해를 돕는 2차 문서다. 충돌 시 다음 자료가 우선한다.

1. `current/current-pointer.json`
2. `spec/language.md`
3. `spec/contracts/**`, `spec/types/**`, `spec/patterns/**`와 canonical
   registry·schema
4. `spec/grammar/deeplus.dpg`
5. `docs/grammar-reference/**`

각 장 첫머리에는 아래 중 하나의 정확한 상태 표식을 둔다. 표식은 제목
바로 다음에 두거나 첫 `## 상태와 읽는 법` 절 안에 둘 수 있지만, 두
번째 `##` 절보다 뒤로 미루지 않는다.

- `CURRENT_DESIGN_PRODUCT_NOT_RUN`: 현행 정본 설계. 제품 실행 증거는 없음.
- `PREVIEW_GATED_PRODUCT_NOT_RUN`: 명시적 gate가 필요한 Preview.
- `PREVIEW_DESIGN_NONACTIVATABLE`: 비활성 설계 검토면.
- `MIXED_STATUS`: 장 안에서 표면별 상태를 다시 구분함.

`CURRENT` 또는 `Stable`은 제품 구현·실행·지원 PASS를 뜻하지 않는다.
저장소의 product lane은 계속 `15/15 NOT_RUN`이다. 예제의 “예상 결과”는
정본 설계에 따른 정적·의미적 설명이지 실행 영수증이 아니다.

## 3. 각 장의 고정 구조

학습 장은 다음 절을 이 순서로 포함한다.

1. 상태와 읽는 법
2. 학습 목표
3. 선수 지식
4. 문제에서 출발하기
5. 핵심 모델
6. 단계별 예제
7. 허용·거부·경계 사례
8. 다른 기능과의 연결
9. Deeplus다운 작성 관례
10. 연습 문제
11. 빠른 복습
12. 정본 근거와 다음 장

실습 장은 목표, 준비, 단계별 구현, 중간 점검, 실패 실험, 확장 과제,
완료 체크리스트를 포함한다. 모든 장은 최소 두 개의 `deeplus` 코드
블록과 세 개의 연습 문제를 제공한다. 단순 복사, 빈칸 완성, 스스로
설계하기의 세 단계를 한 개 이상씩 둔다.

## 4. 예제 표기

코드 블록 바로 앞에 필요할 때 다음 주석을 둔다.

```text
<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```

거부 예제에는 `expected: REJECT`와 관련 diagnostic family를 설명한다.
Preview gated 예제는 `surface: PREVIEW_GATED`로
표시하고 exact gate를 함께 설명한다.
Preview Design 예제는 반드시 `surface: PREVIEW_DESIGN_NONACTIVATABLE`로
표시하고 현행 프로그램처럼 복사해 쓰라고 안내하지 않는다.

예제는 다음 울타리를 보존한다.

- 인덱스의 첫 유효 위치는 `1`이다.
- `array`와 `case`는 일반 식별자다.
- raw 문자열은 `#raw"..."`이다.
- 한정 이름은 식별자를 `::`로 잇는다.
- Package는 배포·의존성·빌드 단위이고 Module은 이름 공간·가시성·소스
  구성 단위다. Module 경로와 파일 시스템 경로는 동일할 필요가 없다.
- 임의 custom operator는 Current와 Preview Design 모두에서 수용하지
  않으며 positive 예제에 쓰지 않는다.
- fixed-glyph conformance는 정본 Stable 설계 범위만 설명한다.
- 현재 lowercase `via`와 비활성 successor `VIA`/`AUTO` route를 섞지 않는다.
- 현재 Enum과 Preview successor Enum 표면을 섞지 않는다.

## 5. 설명의 깊이

용어를 처음 쓸 때는 “무엇인지, 왜 필요한지, 언제 쓰는지, 무엇과
혼동하기 쉬운지”를 모두 설명한다. 문법만 보여 주지 않고 다음 네 층을
연결한다.

- surface syntax
- 정적 의미와 조기 오류
- runtime/ownership/effect 관찰 가능성
- HIR-H1/MIR/backend 경계

초급 장에서는 내부 표현을 직관으로만 소개하고, 고급 장에서 정확한
경계를 다시 설명한다.

## 6. 과정 전체의 불변 조건

- semantic P0: `0`
- OPEN feature P1: 정확히 `22`
- 별도 OPEN action: `M13-A002..005`
- product lanes: `15/15 NOT_RUN`
- 임의 P1 폐쇄·신규 생성 금지
- Preview Design 활성화 주장 금지
- compiler/runtime/tooling PASS 주장 금지

## 7. 파일 배치

각 부는 `part-NN-*` 디렉터리에 `README.md`, 다섯 개 학습 장, 한 개
실습을 둔다. 종합 프로젝트는 `capstones/`, 참조 부록은 `appendices/`에
둔다. 파일명은 정렬 가능한 두 자리 장 번호를 사용한다.
