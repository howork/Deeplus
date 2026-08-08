# 01-01. Deeplus와 상태를 먼저 읽기

## 1. 상태와 읽는 법

> **상태:** `MIXED_STATUS`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 여러 상태를 비교한다. `CURRENT_DESIGN_PRODUCT_NOT_RUN`은 현행
정본 설계, `PREVIEW_GATED_PRODUCT_NOT_RUN`은 명시적 gate가 필요한
Preview, `PREVIEW_DESIGN_NONACTIVATABLE`은 아직 source로 활성화할 수 없는
설계 검토면이다. 어느 상태도 그 자체로 compiler나 runtime의 실행 PASS를
뜻하지 않는다.

## 2. 학습 목표

- 언어 설계 상태와 제품 실행 상태를 서로 다른 축으로 설명한다.
- 문서가 충돌할 때 어떤 정본을 먼저 확인할지 안다.
- Preview Design이 current HIR/MIR을 만들지 않는 이유를 이해한다.
- 예제의 예상 결과를 실행 영수증으로 오해하지 않는다.

## 3. 선수 지식

특별한 프로그래밍 경험은 필요 없다. 파일과 폴더가 무엇인지, 코드의
한 줄이 위에서 아래로 읽힌다는 정도만 알면 된다.

## 4. 문제에서 출발하기

저장소에서 다음 두 문장을 보았다고 하자.

- “이 기능은 Stable이다.”
- “제품 lane은 NOT_RUN이다.”

두 문장은 모순이 아니다. 첫 문장은 언어 설계가 현재 정본에 들어왔다는
뜻이고, 둘째 문장은 특정 compiler, checker, backend에서 실제 실행한
target-bound receipt가 없다는 뜻이다. Deeplus는 이 둘을 일부러 분리해,
문서가 구현보다 앞서가거나 구현 실험이 정본 의미를 바꾸는 일을 막는다.

## 5. 핵심 모델

정본 우선순위는 다음과 같다.

1. `current/current-pointer.json`
2. `spec/language.md`
3. `spec/grammar/deeplus.dpg`
4. `spec/contracts/**`, `spec/types/**`, `spec/patterns/**`
5. canonical registry와 schema
6. `docs/grammar-reference/**`
7. 이 튜토리얼

튜토리얼은 이해를 돕는 2차 문서다. 예제가 정본과 다르면 예제가 아니라
정본을 따른다. 또한 정적으로 거부된 source는 진단 provenance는 남길 수
있지만 admitted AST/HIR/MIR이나 runtime event를 만들지 않는다.

## 6. 단계별 예제

다음은 현재 문법으로 설명할 수 있는 순수 함수다. 실행했다는 주장이
아니라, 문법·타입·효과 계약상 허용되는 설계 정적 예다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private def#pure double(value: Int) -> Int
= {
    return value * 2
}

let answer: Int = double(21)
```

`def#pure`는 recoverable error가 없고 관찰 가능한 effect가 없는 callable
profile이다. `answer`의 설계상 값은 `42`지만, 이 문서는 xVM이나 Cranelift에서
그 결과를 실행했다는 영수증이 아니다.

다음은 Preview Design 문서가 current source admission을 만들지 않는
대표적인 경우다.

<!-- deeplus-example: illustrative; surface: PREVIEW_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
private type UserRow = ${id: Int, name: String}
```

이 후보는 Preview Design 설명용이며 현행 source route가 없다.

### 판정 trace, 미니 사례와 흔한 오해

새 코드 조각을 만났다고 가정하자. 먼저 현재 포인터가 가리키는 revision을
확인하고, 해당 spelling이 정본 문법과 feature registry 중 어디에
소속되는지 찾는다. 다음으로 source gate가 실제로 존재하는지 확인한다.
마지막으로 static 설명과 제품 실행 영수증을 분리한다. 문서에
`PREVIEW_DESIGN_NONACTIVATABLE` 예제가 자세히 적혀 있어도 두 번째
단계에서 activation route가 없으므로 정상 입력 후보가 아니다. 반대로
CURRENT 예제도 세 번째 단계의 compiler/runtime receipt가 없으면 제품
PASS라고 말할 수 없다.

미니 사례로 새 표면을 본 독자는 “편리해 보인다”보다 먼저
상태 토큰을 찾는다. Preview Design이면 current 대안과 비교하는 설계
자료다. 가장 흔한 오해는
`Stable`을 “모든 target에서 이미 구현됨”으로 번역하거나, `Preview`라는
한 단어로 gated 기능과 nonactivatable 설계를 합치는 것이다. 상태는
language admission을 말하고 `NOT_RUN`은 제품 증거를 말한다.

## 7. 허용·거부·경계 사례

- **허용:** 현행 DPG와 checker 계약에 모두 들어 있는 source.
- **거부:** Current 또는 gated Preview route에 속하지 않는 source.
- **경계:** Preview-gated FFI처럼 gate가 있어야 parse 후보가 되지만,
  target ABI 실행은 여전히 `NOT_RUN`인 기능.
- **비활성:** Preview Design은 gate를 추가해도 켤 수 없다.

문서에 schema, fixture, HIR 이름이 있다는 사실만으로 해당 기능이
활성화되거나 OPEN P1이 닫히지 않는다.

## 8. 다른 기능과의 연결

상태는 모든 장에 영향을 준다. 타입 표면이 CURRENT여도 runtime layout은
정해지지 않을 수 있고, HIR-H1 verifier 경계가 Stable Design이어도
구체 MIR-X1 제안은 noncanonical/nonactivatable일 수 있다. 앞으로 각
예제는 surface 상태와 product `NOT_RUN`을 함께 표시한다.

## 9. Deeplus다운 작성 관례

- 실행되지 않은 것을 “작동한다”라고 쓰지 않고 “정본상 허용된다”라고
  표현한다.
- Preview를 Stable 예제와 한 코드 블록에 섞지 않는다.
- 잘못된 철자는 학습의 중심으로 반복하지 않고, 실제 실패를 설명할 때만
  제시한다.
- 제약을 설명할 때는 같은 의도를 표현할 현행 대안도 함께 제시한다.

## 10. 연습 문제

1. **따라 하기:** 위 `double` 함수에서 입력을 `7`로 바꾸고 정본상 결과를
   종이에 계산하라. 실행 PASS라고 쓰지 말아야 하는 이유도 한 문장으로
   적는다.
2. **빈칸 완성:** `CURRENT`, `PREVIEW_GATED`,
   `PREVIEW_DESIGN_NONACTIVATABLE` 중 “설계는 보존하지만 current 의미
   node는 만들지 않는 상태”를 고른다.
3. **스스로 설계하기:** 새 문서 예제를 하나 가정하고 surface 상태,
   product 상태, 근거 파일 세 항목을 포함한 머리말을 작성하라.

## 11. 빠른 복습

- Stable/Current는 설계 권위이고 product PASS가 아니다.
- Preview Design은 feature gate로 활성화할 수 없다.
- 튜토리얼보다 current pointer와 spec이 우선한다.
- 현행 불변값은 semantic P0 `0`, feature P1 `22 OPEN`,
  product lane `15/15 NOT_RUN`이다.

## 12. 정본 근거와 다음 장

- [현재 포인터](../../../current/current-pointer.json)
- [언어 정본](../../../spec/language.md)
- [상태·권위 및 표기](../../grammar-reference/00-status-authority-and-notation.md)
- [평가·HIR·MIR 경계](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)

다음은 [소스와 진단 읽기](01-02-source-diagnostics.md)에서 잘못된 source가
어느 단계에서 어떻게 멈추는지 살펴본다.
