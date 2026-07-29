# Part 5 — 데이터를 모양과 의미로 모델링하기

> 과정 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> semantic P0: `0` · OPEN feature P1: `22` · product lanes: `15/15 NOT_RUN`

이 부에서는 “값 몇 개를 어디에 담을까?”보다 한 단계 더 중요한 질문을
다룬다. 어떤 값들이 하나의 의미 단위를 이루는지, 가능한 상태가 유한한지,
외부에 공개할 필드가 무엇인지, 실패한 분해가 소유권을 바꾸어도 되는지를
타입과 패턴으로 표현한다.

Deeplus의 데이터 모델링 표면은 비슷해 보이는 문법을 의도적으로 나눈다.

- Tuple은 위치가 의미인 고정 길이 값이다.
- Record는 정적 label이 의미인 구조적 값이다.
- Map은 실행 중 key로 찾는 동적 연관 값이다.
- schema는 허용된 label·타입·기본값·제약을 선언하는 materialization
  authority다.
- Class는 명목 identity와 생성·가시성·책임을 소유한다.
- Enum은 하나의 `EnumId`가 유한한 `VariantId` 우주를 소유한다.
- Pattern은 값을 시험하고 성공했을 때만 binding과 ownership을 commit한다.

## 학습 경로

1. [Record, Tuple, Map, schema](05-01-record-tuple-map-schema.md)
2. [Class, data class, constructor](05-02-class-data-class-constructors.md)
3. [현행 Enum 표면](05-03-enum-current-surface.md)
4. [패턴과 구조 분해](05-04-patterns-destructuring.md)
5. [완전성, guard, transaction](05-05-exhaustiveness-guards-transactions.md)
6. [실습: 주문 승인 workflow](lab-05-domain-workflow.md)

## 이 부의 불변선

- `case`는 keyword가 아니라 일반 식별자다. Enum case는 bare name으로
  선언한다.
- 현재 Enum의 named/positional/mixed payload와 `.`, `+`, `*.`, `*+`
  member reachability를 유지한다.
- successor Enum의 uniform payload나 final-dot-only member는
  `PREVIEW_DESIGN_NONACTIVATABLE`이며 현행 예제에 섞지 않는다.
- Record label과 Map key를 서로 바꾸지 않는다.
- Tuple과 bare comma product는 하나의 Tuple 의미로 정규화된다.
- Record/Map Pattern은 exact-by-default이며 subset 의도는 `.._`로
  명시한다.
- List rest는 tail `..tail`, prefix `leadings..`, middle
  `..middle..`의 방향을 구분한다.
- pattern 실패나 false guard는 partial binding, partial move 또는
  exclusive borrow를 남기지 않는다.

## 읽을 때 사용할 질문

각 예제를 볼 때 다음 네 질문을 반복한다.

1. 이 값의 identity는 위치, 정적 label, runtime key, nominal owner 중
   무엇인가?
2. 어떤 검사가 실행 전에 끝나는가?
3. 평가가 실패하면 무엇이 아직 publish되지 않아야 하는가?
4. HIR-H1/MIR에 남겨야 할 owner, variant, label, commit 정보는 무엇인가?

이 부의 예시는 정본 설계에 따른 설명용 코드다. 실제 parser/checker,
MIR, xVM 또는 Cranelift 실행을 증명하지 않는다.
