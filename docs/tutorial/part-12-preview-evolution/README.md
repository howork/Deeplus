# Part 12 — Preview를 읽고 언어를 진화시키기

> 상태: `MIXED_STATUS`

이 부는 새 문법을 “미리 써 보는 법”보다, 제안과 정본을 섞지 않고
검토하는 법을 가르친다. Deeplus의 상태 축은 단순한 성숙도 순위가
아니다. Current/Stable, Preview Gated와 Preview Design은 서로 다른
admission route와 authority를 가진다. 구현 전 정본은 Current와 보존된
Preview 상태만 설명한다. 어떤 상태에서도 제품 실행
증거가 자동으로 생기지 않으며 현재 product lane은 `15/15 NOT_RUN`이다.

## 이 부에서 답할 질문

- Current와 Stable은 무엇을 보장하고 무엇을 보장하지 않는가?
- 정확히 세 개인 Preview Gated 기능은 어떻게 source root에서 선택되는가?
- Preview Design을 왜 현행 프로그램에 복사하면 안 되는가?
- 제안을 검토할 때 syntax만이 아니라 type, ownership, effect, HIR/MIR,
  diagnostic과 migration을 왜 함께 닫아야 하는가?
- HIR-H1 verifier boundary와 비정규 DP-RFC의 구현 제안을 어떻게 구분하는가?
- MIR-X1 xVM-only draft가 현행 xVM + LLVM backend authority를 왜 바꾸지
  않는가?

## 학습 순서

1. [12-01 상태 모델](12-01-status-model.md)
2. [12-02 Preview Gated](12-02-preview-gated.md)
3. [12-03 Preview Design — 타입·객체·Trait](12-03-preview-design-types-traits.md)
4. [12-04 Preview Design — 컬렉션·context·제어](12-04-preview-design-collections-control.md)
5. [12-05 Preview Design — 동시성·runtime·MIR-X1](12-05-preview-design-concurrency-runtime.md)
6. [Lab 12 — 설계 검토 카드 작성](lab-12-design-review.md)

## 먼저 보는 두 울타리

현행 표면은 별도 Preview 표식 없이 읽는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def square(value: Int) -> Int
= {
    return value * value
}
```

Preview Design 예제는 검토 대상일 뿐 현행 parser/checker가 받아들이는
프로그램이 아니다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: async_callable_literal_profile
let loader = #async{ => await loadProfile() }
```

위 둘을 같은 “지원 예제”로 읽으면 안 된다. 둘 다 product 실행 증거는
없지만, 첫 예제는 current language design이고 둘째는
`PREVIEW_DESIGN_NONACTIVATABLE` probe다.

## 이 부 전체의 불변 조건

- semantic P0는 `0`이다.
- OPEN feature P1은 정확히 `22`이다.
- `M13-A002..005`는 P1과 별도인 OPEN action이다.
- product lane은 정확히 `15/15 NOT_RUN`이다.
- 이 부는 P1을 추가·폐쇄하거나 구현·활성화 authority를 만들지 않는다.
- 비정규 RFC와 예제는 정본 source 또는 backend authority를 바꾸지 않는다.

## 정본 근거

- [Preview 상태 안내](../../grammar-reference/15-preview-surfaces.md)
- [Preview Gated reference](../../grammar-reference/20-preview-gated-reference.md)
- [Preview Design — 타입·객체·Trait](../../grammar-reference/21-preview-design-types-objects-and-traits.md)
- [Preview Design — 컬렉션·context·제어](../../grammar-reference/22-preview-design-collections-context-and-control.md)
- [Preview Design — 동시성·FFI·runtime](../../grammar-reference/23-preview-design-concurrency-ffi-and-runtime.md)
- [Feature gate registry](../../../spec/features/gates.json)
