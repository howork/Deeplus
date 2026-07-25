# 12-02 — Preview Gated: exact feature closure와 source root

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`
>
> 미니 범례: `PREVIEW_GATED`는 exact source-root gate가 필요한 예제,
> `CURRENT`는 gate와 무관하게 현행인 대안·인접 표면이다. 두 상태 모두
> product는 `NOT_RUN`이다.

현재 gate registry에서 source route가 있는 Preview 기능은 정확히 세
개다. `ffi_minimum_sound_profile`,
`ffi_c_extern_unsafe_surface_msp`,
`numeric_array_elementwise_power_msp`만 이 장의 activatable Preview다.
명시적 gate로 정적 검토 route를 고를 수 있다는 뜻이며 제품 구현·실행
PASS를 뜻하지 않는다.

## 2. 학습 목표

- `#preview(...)`의 source-root placement와 exact ID 규칙을 설명한다.
- FFI surface와 minimum sound profile의 dependency를 닫는다.
- NumericArray의 postfix transpose와 spaced infix power를 구분한다.
- unknown, duplicate, missing dependency와 nonactivatable ID를 진단한다.

## 3. 선수 지식

qualified name, effect/error set, unsafe boundary, NumericArray shape와
postfix/infix attachment 규칙을 알고 있어야 한다.

## 4. 문제에서 출발하기

Preview gate는 전역 “실험 모드” 스위치가 아니다. source file이 exact
기능 집합과 dependency closure를 선언하고 parser/checker가 그 root의
제한된 surface만 연다. gate가 item 사이에 나타나거나, ID가 중복되거나,
dependency가 빠지면 구현이 적당히 추측해서는 안 된다.

## 5. 핵심 모델

gate 검사는 source body보다 먼저 다음 순서로 이루어진다.

1. `#preview(...)`가 source root의 허용 위치에 있는지 확인한다.
2. ID가 registry의 `PREVIEW`이면서 `explicit_feature_gate`인지 확인한다.
3. unknown·duplicate·nonactivatable ID를 거부한다.
4. 선택한 feature의 transitive dependency closure를 확인한다.
5. 통과한 root에만 feature-local grammar/semantic admission을 적용한다.

정확한 세 기능의 관계는 다음과 같다.

| Feature ID | 역할 | gate dependency |
|---|---|---|
| `ffi_minimum_sound_profile` | representability, pointer provenance, unsafe/resource 경계의 최소 프로필 | 없음 |
| `ffi_c_extern_unsafe_surface_msp` | C extern unsafe 선언 표면 | `ffi_minimum_sound_profile` |
| `numeric_array_elementwise_power_msp` | NumericArray spaced infix `^`의 요소별 power | Stable operator/array 계약에 의존하나 gate 목록에는 자기 ID만 둠 |

## 6. 단계별 예제

FFI function route는 surface와 sound profile을 함께 선택한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

이 선언은 C ABI나 native target이 제품으로 검증되었다는 주장이 아니다.
checker는 parameter/result representability, unsafe authority, raw pointer
provenance와 foreign resource cleanup을 feature profile에 따라 점검해야
한다.

block route에서도 library identity와 member별 unsafe/effect가 드러난다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern c("sqlite3") {
    unsafe def sqlite3_close(db: RawPtr<sqlite3>) -> CInt
        effects {io}
}
```

NumericArray power는 공백이 있는 infix route다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN -->
```deeplus
#preview(numeric_array_elementwise_power_msp)
let squared = values ^ 2
```

`values^`는 별개의 Stable postfix transpose owner다. 같은 파일에 power
gate가 있어도 attachment가 바뀌지 않는다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let transposed = values^
```

## 7. 허용·거부·경계 사례

허용: exact FFI feature와 dependency를 한 번씩 root에 나열한다.

거부: surface만 선택하고 sound profile을 빠뜨린다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN; expected: REJECT -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp)
extern c("libc") {
    unsafe def puts(text: CString) -> Int
}
```

예상 diagnostic family는 `PREVIEW_GATE_DEPENDENCY_MISSING`이다. 이후
signature 진단으로 fallback하지 않는다.

거부: 같은 ID를 두 번 나열한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN; expected: REJECT -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

예상 diagnostic family는 `PREVIEW_GATE_DUPLICATE_FEATURE`다.

경계: gate가 없는 `values ^ 2`는 postfix transpose로 재해석되지 않는다.
`NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE` 계열 진단으로 거부해야 한다.

## 8. 다른 기능과의 연결

FFI gate는 `unsafe`와 `effects`를 없애지 않고 오히려 명시적으로 묶는다.
foreign failure를 자동 `Error`로, null pointer를 자동 `Option`으로 바꾸지
않는다. NumericArray power도 arbitrary custom operator나 Trait lookup을
활성화하지 않는다. fixed-glyph `^`의 exact owner와 shape law 안에서만
작동한다.

HIR-H1에는 selected gate closure와 feature-local semantic decision이
lossless하게 남아야 한다. MIR/backend는 빠진 dependency를 보충하거나
postfix/infix owner를 다시 선택해서는 안 된다.

### 판정 추적과 흔한 오해

source root를 읽으면 item보다 먼저 gate 선언의 위치와 중복을 확인하고,
각 ID의 registry status·activation route를 조회한다. 이어 dependency
closure를 닫고 선택된 feature-local grammar와 semantic rule만 연다.
HIR-H1에는 exact feature set과 selected operation을 남기며 MIR/backend가
빠진 dependency나 다른 operator owner를 보충하지 못하게 한다.

미니 사례에서 `values^`는 공백 없는 current postfix transpose이고,
`values ^ 2`는 gated infix power다. power gate가 없다고 후자를
transpose와 숫자 `2`로 재해석하지 않는다. 반대로 power gate가 있다고
모든 `^` attachment가 infix가 되는 것도 아니다.

흔한 오해는 한 FFI gate가 sound profile dependency까지 암묵적으로
켠다고 보거나, `#preview(*)` 같은 wildcard를 기대하는 것이다. exact
dependency 두 개를 source root에 적어야 하며, gate 성공은 ABI target,
foreign lifetime과 runtime execution receipt를 대신하지 않는다.

## 9. Deeplus다운 작성 관례

- gate는 source root에 한 번, exact ID를 중복 없이 적는다.
- 필요한 기능만 선택하며 “모든 Preview” 같은 wildcard를 쓰지 않는다.
- FFI wrapper에서 ownership, error mapping, cleanup을 named API로
  드러낸다.
- `values^`와 `values ^ 2` 사이 공백을 formatter가 바꾸지 못하게 한다.
- Preview Gated 예제에도 product `NOT_RUN` 경계를 명시한다.

## 10. 연습 문제

1. **그대로 따라 하기:** `c_abs` 예제를 옮겨 적고 두 feature ID가 맡는
   책임을 각각 한 문장으로 설명하라.
2. **빈칸 채우기:** `#preview(ffi_c_extern_unsafe_surface_msp, ____ )`를
   완성하고 dependency가 body parsing 전에 검사되어야 하는 이유를
   적어라.
3. **스스로 설계하기:** NumericArray `values^`, `values ^ 2`, gate가
   없는 `values ^ 2`를 포함한 attachment test matrix를 만들고 각 행의
   expected admission 또는 diagnostic을 기록하라.

## 11. 빠른 복습

- Preview Gated feature는 정확히 세 개다.
- FFI surface는 minimum sound profile에 의존한다.
- unknown·duplicate·missing dependency는 추측 없이 거부한다.
- NumericArray postfix transpose와 spaced infix power는 다른 owner다.
- gate admission은 product support PASS가 아니다.

## 12. 정본 근거와 다음 장

- [Preview Gated reference](../../grammar-reference/20-preview-gated-reference.md)
- [gate registry](../../../spec/features/gates.json)
- [value/operator/indexing 계약](../../../spec/contracts/value-operator-indexing-coherence.json)

다음 장에서는 gate route 자체가 없는 타입·객체·Trait Preview Design을
검토한다.
