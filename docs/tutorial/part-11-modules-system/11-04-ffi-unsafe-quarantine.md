# 11-04 — FFI, `unsafe`와 quarantine 경계

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`

Stable unsafe block과 static type projection은 current design이다. C FFI는
`PREVIEW_GATED_PRODUCT_NOT_RUN`, quarantine spelling은
`PREVIEW_DESIGN_NONACTIVATABLE`이자 recovery probe다.

## 2. 학습 목표

- unsafe authority와 effect row를 분리한다.
- exact Preview gate가 FFI source root를 선택하는 방식을 이해한다.
- FFI representability와 Deeplus semantic identity를 분리한다.
- quarantine probe를 current syntax로 사용하지 않는다.

## 3. 선수 지식

status model, source root, capability/effects, ownership과 API/ABI identity를
알고 있어야 한다.

## 4. 문제에서 출발하기

foreign function은 Deeplus type과 C ABI가 우연히 비슷하다고 호출할 수
있는 것이 아니다. target triple, representation, lifetime, error,
ownership을 모두 경계 계약에 묶어야 한다. unsafe라는 단어도 I/O나 network
effect를 숨겨 주지 않는다.

## 5. 핵심 모델

- `unsafe { ... }`: current authority boundary; effect row와 별도.
- gated FFI: preview root 첫머리의 exact `#preview(...)`가 필요.
- FFI lowering: target/ABI manifest와 representability proof 필요.
- quarantine: dynamic/unsafe legacy operation을 격리하려는 nonactivatable
  design; current AST/HIR/MIR source surface가 아님.

## 6. 단계별 예제

Stable unsafe block은 operation의 unsafe authority를 source에 드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def inspectRaw(handle: RawHandle) -> Int
    throws ForeignError
    effects {}
= {
    return unsafe {
        handle ~ checkedValue()
    }
}
```

FFI Preview는 두 exact feature를 gate한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

이 문서 조각은 ABI 실행 PASS를 뜻하지 않는다.

## 7. 허용·거부·경계 사례

gate 없는 FFI는 Stable root에서 거부된다.

<!-- deeplus-example: illustrative; surface: PREVIEW_GATED; product: NOT_RUN; expected: REJECT -->
```deeplus
extern#C def#unsafe c_abs(x: Int) -> Int
// FFI_MINIMUM_SOUND_PROFILE_REQUIRES_FEATURE_GATE
```

quarantine probe는 current source가 아니다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
@scope#dynamic {
    legacyCall()
} -> $result: PlainResult
// QUARANTINE_SCOPE_NOT_ACTIVATABLE
```

typed immutable export, escape/alias/cleanup, backend equivalence, security
review와 activation authority가 닫히기 전에는 gate로도 켤 수 없다.

## 8. 다른 기능과의 연결

- unsafe authority는 effects `{io}`나 `{network}`를 대체하지 않는다.
- FFI ABI는 serialization format 및 Deeplus semantic identity와 다르다.
- foreign callback/task/actor crossing에는 별도 lifetime/isolation proof가
  필요하다.
- HIR/MIR은 rejected quarantine probe의 residue를 만들지 않는다.

### 판정 추적

FFI source는 먼저 source root의 exact gate 집합과 dependency closure를
검사한다. 그 뒤 foreign declaration의 ABI spelling, parameter/result
representability, pointer provenance와 ownership, unsafe authority,
effect/error 책임을 닫는다. 마지막으로 target manifest가 선택한
triple·ABI에서 lowering 가능하다는 evidence를 요구한다. gate와 source
type check만 통과해도 target execution은 아직 `NOT_RUN`이다.

safe wrapper는 foreign handle을 받았다는 이유로 lifetime을 추측하지
않는다. 누가 allocation과 release를 소유하는지, nullability와 length가
어디서 증명되는지, partial failure 때 어느 cleanup이 실행되는지를
Deeplus type과 ErrorSet으로 다시 표현한다. callback이나 actor crossing은
이 기본 wrapper 위에 별도 isolation proof를 더한다.

### 흔한 오해와 미니 사례

`unsafe`는 모든 검사를 끄는 표식이 아니다. programmer가 특정 operation의
unsafe obligation을 명시적으로 맡는 boundary이며 I/O effect, network
authority, pointer lifetime, target representability를 지우지 않는다.
exact Preview gate 역시 “실험 기능 전부 켜기”나 ABI 제품 PASS가 아니다.

미니 사례로 C가 `(pointer, length)` buffer를 돌려주면 wrapper는 length를
검증하고 owned `Bytes`로 복사한 뒤 foreign release를 수행할 수 있다.
pointer를 borrowed Deeplus slice처럼 그대로 반환하면 lifetime owner가
사라진다. copy와 release가 모두 실패할 수 있다면 body/cleanup의
primary·suppressed 순서도 Part 09 법칙을 따른다.

quarantine recovery probe를 보았을 때는 migration diagnostic만 만들고
admitted AST/HIR/MIR residue count를 0으로 유지한다. 비슷한 문제를
해결한다는 이유로 gated FFI profile에 끼워 넣거나 current `unsafe`
block으로 자동 재작성하지 않는다.

경계 검토는 positive, negative, target 세 묶음으로 만든다. positive에는
exact gate closure, representable scalar와 명시적 safe wrapper를 둔다.
negative에는 gate 누락, 비표현 type, escaping foreign borrow, cleanup
owner 누락을 둔다. target 묶음에는 지원 triple별 call convention,
size/alignment, symbol binding과 failure receipt를 둔다. static positive가
있어도 target 묶음이 비어 있으면 execution은 계속 `NOT_RUN`이다.

foreign error도 숫자 하나로 던져 두지 않는다. C return code, platform
last-error, null pointer, partial write 중 어떤 관찰이 source operation의
primary failure인지 wrapper가 결정하고 versioned application Error로
mapping한다. mapping 도중 cleanup이 실패하면 Part 09의 suppressed
ordering을 보존한다. raw code를 Enum declaration order나 Defect
identity로 추측해서는 안 된다.

callback 미니 사례에서는 foreign side가 callback을 저장하는지, 호출
thread와 lifetime이 무엇인지, Deeplus task/actor isolation을 건너는지를
먼저 묻는다. 호출 중에만 유효한 nonescaping callback과 장기 저장되는
callback은 같은 function pointer shape라도 ownership contract가 다르다.
별도 proof가 없으면 후자를 safe wrapper로 수용하지 않는다.

review receipt에는 gate identity, target identity, wrapper owner와 아직
실행하지 않은 lane을 함께 적는다. source가 존재한다는 사실, manifest가
parse된다는 사실, 한 target에서 symbol을 찾았다는 사실을 서로 다른
evidence로 유지한다. 그래야 다른 ABI나 actor callback으로 범위를
부당하게 확대하지 않는다.

## 9. Deeplus다운 작성 관례

foreign boundary를 작게 유지하고 safe wrapper가 representability,
ownership, error를 다시 Deeplus type으로 닫게 한다. gate와 unsafe를
“모든 검사를 끄는 스위치”처럼 사용하지 않는다.

## 10. 연습 문제

1. **따라 하기:** exact 두 FFI gate ID를 source root 첫머리에 적어라.
2. **빈칸 완성:** unsafe authority와 effect row가 각각 답하는 질문을
   채워라.
3. **스스로 설계하기:** C buffer를 Deeplus `Bytes`로 복사하는 wrapper의
   lifetime/error/cleanup 경계를 설계하라.

## 11. 빠른 복습

- unsafe와 effects는 독립 축이다.
- FFI는 exact gated Preview다.
- gate는 target ABI proof가 아니다.
- quarantine은 nonactivatable recovery probe다.

## 12. 정본 근거와 다음 장

- [FFI/unsafe reference](../../grammar-reference/14-ffi-unsafe-metaprogramming-and-profiles.md)
- [Preview gated reference](../../grammar-reference/20-preview-gated-reference.md)
- [feature gates](../../../spec/features/gates.json)

다음 장은 source identity가 HIR-H1과 MIR을 거치며 무엇을 보존하는지
설명한다.
