# 12-01 — 언어 상태 모델: Current와 Preview

## 1. 상태를 먼저 읽는 이유
> 상태: `MIXED_STATUS`

Deeplus 문서에는 현재 언어로 채택된 표면과 앞으로의 도입을 검토하는
표면이 함께 실린다. 코드 조각이 문서에 있다는 사실만으로 사용할 수
있다고 판단하면 안 된다. 먼저 그 조각이 `CURRENT`,
`PREVIEW_GATED`, `PREVIEW_DESIGN_NONACTIVATABLE` 중 어디에 속하는지
확인해야 한다. 제품 구현 여부는 언어 상태와 별개의 축이며 현재 제품
lane은 `15/15 NOT_RUN`이다.

## 2. Current

Current는 현행 문법·정적 의미·타입·소유권·책임 계약이 선택한 언어다.
별도 feature gate 없이 정본 source root에서 사용할 수 있다. 다만
Current라는 말은 컴파일러와 런타임 구현이 완료되었다는 뜻이 아니다.

```deeplus
private enum LoadState {
    Idle
    Loading
    Failed(message: String)
}

private def label(state: LoadState) -> String = {
    return @match state {
        ::Idle => "idle"
        ::Loading => "loading"
        ::Failed(message) => message
    }
}
```

위 코드는 현행 Enum 선언, payload pattern, exhaustive match를 함께
보여 준다. 이 의미 계약은 Current이지만 실제 parser/checker 실행
receipt가 생기기 전에는 제품 PASS를 주장하지 않는다.

## 3. Preview Gated

Preview Gated는 registry가 허용한 정확한 기능 ID를 source 첫머리의
`#preview(...)`에 적었을 때만 admission 후보가 된다. 알려진 ID를
자유롭게 적는 범용 switch가 아니며, 현재 activatable 집합에 없는 ID는
gate에 적어도 활성화되지 않는다.

```deeplus
#preview(numeric_array_elementwise_power_msp)

private def square(values: NumericArray<Int>) -> NumericArray<Int> = {
    return values ^ 2
}
```

이 예시는 gate가 source 의미의 일부라는 점을 보여 준다. gate가 없으면
같은 철자를 같은 기능으로 해석할 권위가 없다.

## 4. Preview Design

Preview Design은 본격 도입 여부를 검토할 수 있도록 동기, 후보 표면,
정적 의미, 상호작용, 진단, 이행 및 활성화 조건을 구체적으로 기록한
설계다. `NONACTIVATABLE`이므로 현재 source route가 없으며
`#preview(...)`에 ID를 적는 것만으로 사용할 수 없다. 그렇다고 문서에서
삭제할 대상도 아니다. Deeplus는 Preview Design과 예시를 보존하여
장단점과 언어 전체의 일관성을 검토한다.

```deeplus
// Preview Design 설명용이며 현재 source로는 사용할 수 없다.
private type UserRow = ${id: Int, name: String}
```

## 5. 상태와 제품 증거는 독립이다

언어 admission은 “어떤 source가 어떤 의미를 갖는가”를 답한다. 제품
증거는 “그 계약이 어느 compiler·runtime·tooling·target에서 실제로
검증되었는가”를 답한다. 문서, schema, registry row, static validator가
존재해도 target-bound 실행 receipt가 없으면 제품 상태는 `NOT_RUN`이다.

| 언어 상태 | source admission | 제품 실행 주장 |
|---|---|---|
| `CURRENT` | 정본 root에서 허용 | 별도 evidence 필요 |
| `PREVIEW_GATED` | 정확한 gate와 dependency가 있을 때만 후보 | 별도 evidence 필요 |
| `PREVIEW_DESIGN_NONACTIVATABLE` | source route 없음 | 주장 불가 |

## 6. Preview 예시를 읽는 순서

Preview 예시는 다음 순서로 읽는다.

1. exact feature ID와 registry status를 확인한다.
2. `source_activation`이 `explicit_feature_gate`인지
   `nonactivatable`인지 확인한다.
3. current 대안과 충돌하지 않는지 확인한다.
4. 타입·소유권·책임·effect·coherence owner를 확인한다.
5. activation 전에 필요한 grammar, frontend, diagnostic, tooling,
   MIR 및 실행 evidence를 확인한다.

## 7. 자주 생기는 오해

첫째, `PREVIEW_DESIGN`을 `#preview`로 켤 수 있다고 생각하는 오류다.
둘째, Current를 구현 완료와 같은 뜻으로 읽는 오류다. 셋째, 정적 문서
검증을 conformance PASS로 확대하는 오류다. 상태 표시는 이 세 오류를
막기 위해 예제 바로 앞이나 장의 첫머리에 둔다.

## 8. 문서 작성 규칙

- Current 예제와 Preview 예제를 한 코드 블록에 섞지 않는다.
- Preview에는 exact feature ID와 activation 상태를 적는다.
- Preview Design 예시는 설명용이라는 사실과 current 대안을 함께 쓴다.
- 문서 생성이나 예제 추가만으로 P1을 닫지 않는다.
- 제품 lane은 target-bound receipt가 생길 때까지 `NOT_RUN`으로 둔다.

## 9. 연습 문제

1. **상태 판정:** 위 `LoadState` 예제의 언어 상태와 제품 상태를 각각
   한 문장으로 설명하라.
2. **gate 검사:** 임의의 Preview ID가 왜 `#preview(...)`에 적었다는
   이유만으로 활성화되지 않는지 registry 조건을 사용해 설명하라.
3. **설계 카드 작성:** 가상의 Preview Design 하나에 대해 동기, 후보
   표면, current 대안, activation 선행 조건을 작성하라.

## 10. 빠른 복습

- Current, Preview Gated, Preview Design은 서로 다른 admission 상태다.
- Preview Design은 보존하지만 현재 source에서는 활성화하지 않는다.
- 언어 상태와 제품 실행 evidence는 별개의 축이다.
- exact feature ID, source activation, dependency와 current 대안을 함께
  확인해야 한다.

## 11. 정본 근거와 다음 단계

- [Preview 표면](../../grammar-reference/15-preview-surfaces.md)
- [current pointer](../../../current/current-pointer.json)
- [implementation status](../../../current/implementation-status.yaml)
- [feature gate registry](../../../spec/features/gates.json)

다음 장에서는 실제 source gate가 있는 기능만 따로 읽는다.
