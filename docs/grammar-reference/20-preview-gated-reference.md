<!-- deeplus-reference: narrative; authority: documentation-projection -->
<!-- deeplus-grammar-reference-status: CURRENT_CANONICAL_DOCUMENTATION_PROJECTION -->

# 명시적으로 활성화하는 Preview 참조

<!-- deeplus-status-fence: PREVIEW_GATED -->

이 장은 현행 feature registry에서 `status_enum = PREVIEW`이고
`source_activation = explicit_feature_gate`인 기능만 설명한다. 여기에
등재된 예시는 정적 설계 예시이며 제품 실행 증거가 아니다. lexer, parser,
checker, MIR, xVM, LLVM, formatter/LSP를 포함한 15개 제품 lane은 모두
`NOT_RUN`이다. gate는 해당 source root와 구문 또는 의미 route를 선택할
뿐이며, ABI·타입·소유권·효과·오류·provenance 검사를 면제하지 않는다.
gate ID는 왼쪽에서 오른쪽으로 검사되고, 의존성은 암시적으로 켜지지
않는다.

<!-- deeplus-preview-feature-example: ffi_minimum_sound_profile; registry-status: PREVIEW -->
<a id="preview-feature-ffi_minimum_sound_profile"></a>

## 안전한 FFI 최소 sound profile

> **Feature metadata**
> - Feature ID: `ffi_minimum_sound_profile`
> - Registry status: `PREVIEW`; activation: `explicit_feature_gate`
> - Authority: `LANGUAGE / TYPE_SYSTEM / OFFICIAL_TOOLING`; dependencies:
>   `raw_pointer_provenance`, `unsafe_boundary_surface`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
C ABI를 호출한다는 한 줄의 선언이 곧 메모리 안전성을 뜻하는 것처럼
오해하지 않도록, 외부 호출에 필요한 최소 정적 계약을 하나의 명시적
profile로 묶는다. 이 profile은 ABI 이름, 표현 가능한 parameter/result,
`unsafe` 경계, raw pointer provenance, 소유권 이전, unwind와 cleanup을
각각 독립된 책임으로 남긴다. `Plain`이라는 일반 Deeplus 성질만으로 C
layout-safe를 추론하지 않으며, LLVM backend가 있다는 사실도 FFI
soundness의 증거가 아니다.

**제안 표면**
source의 첫 위치에서 gate를 선택한 뒤 `PreviewFfiFunctionDecl` 형태의
`extern#C def#unsafe` 선언을 사용한다. script에서는 shebang 다음 첫
비-shebang token이어야 하고 library/executable에서는 첫 token이어야
한다. 최소 profile ID만 적은 gate는 알려진 Preview ID로서 root 선택에는
유효하지만, 실제 C extern unsafe surface가 함께 필요한 선언은 아래
두 번째 기능과 그 명시적 dependency closure를 함께 적어야 한다.

**정적 판정과 상호작용**
gate admission, FFI signature representability, ABI/provenance, unsafe
authority 검사는 서로 다른 단계다. `throws`와 `effects`는 외부 함수의
관측 가능한 Deeplus 계약을 보존해야 하며 `unsafe`를 EffectRow 원자로
넣지 않는다. C aggregate, variadic, stored callback은 이 최소 profile에
포함되지 않고 별도 비활성 설계다. 동일 선언이 xVM과 LLVM에서 서로 다른
Deeplus 의미를 갖거나 pointer provenance를 backend 관습에 맡기는
구성은 허용 후보가 아니다.

**평가·소유권·오류**
인수는 왼쪽에서 오른쪽으로 한 번 평가되고, 호출 전에 representability와
소유권 경계가 정적으로 확정되어야 한다. borrowed pointer의 유효 기간,
owned handle의 반환 또는 cleanup owner, nullability와 foreign failure
mapping은 선언에 없는 채 추정되지 않는다. gate가 맞아도
`FFI_SIGNATURE_UNREPRESENTABLE`, `PLAIN_IS_NOT_LAYOUT_SAFE` 같은
feature-local 판정으로 거부될 수 있다. 현재 parser/checker/runtime
실행은 `NOT_RUN`이므로 아래 양성은 `accept_with_gate` 설계 oracle이지
제품 성공 사례가 아니다.

**현행 대안과 이행**
Stable code는 typed wrapper, 명시적인 byte buffer 또는 검증된 provider를
사용한다. gate가 없는 외부 선언을 formatter가 자동으로 Preview source로
바꾸거나, `Plain` 값을 C-safe aggregate로 자동 승격해서는 안 된다.
migration 도구는 필요한 gate와 미결 ABI/ownership 항목을 보고할 수
있지만 사용자를 대신해 ABI, nullable policy, cleanup 함수를 선택할 수
없다. LSP는 source root, gate closure와 foreign boundary를 hover와
diagnostic에 분리해 보여야 한다.

**활성화 선행 조건**
정확한 ABI별 representability 표, raw pointer provenance와 lifetime
법칙, ownership/unwind/cleanup mapping, 결정적 diagnostic와 recovery,
formatter/LSP round-trip, MIR foreign-call identity, xVM/LLVM 동등성
corpus, 다중 target의 artifact-bound receipt와 별도 Design_ 판정이
필요하다. 문서·schema·정적 fixture는 이 조건을 대체하지 않고 어떤 P1도
닫지 않는다.

양성 검토 예시 `EX-R48-026`은 의존 surface까지 명시한 완전한 gate를
사용한다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

음성 예시는 Stable root에서 gate 없이 같은 표면을 사용한다. 첫 진단은
`FFI_MINIMUM_SOUND_PROFILE_REQUIRES_FEATURE_GATE`이며, parser가 이를
ordinary Stable declaration으로 받아들여서는 안 된다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
// 검토용 음성 조각: gate가 없으므로 Stable source에서는 거부된다.
extern#C def#unsafe c_abs(x: Int) -> Int
```

경계 예시는 gate가 source item 뒤에 놓인 경우다. 알려진 ID라도 root를
뒤늦게 바꿀 수 없으므로 `PREVIEW_GATE_PLACEMENT_INVALID`가 우선한다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
let ready = true
#preview(ffi_minimum_sound_profile)
```

<!-- deeplus-preview-feature-example: ffi_c_extern_unsafe_surface_msp; registry-status: PREVIEW -->
<a id="preview-feature-ffi_c_extern_unsafe_surface_msp"></a>

## C extern unsafe 선언 표면

> **Feature metadata**
> - Feature ID: `ffi_c_extern_unsafe_surface_msp`
> - Registry status: `PREVIEW`; activation: `explicit_feature_gate`
> - Authority: `LANGUAGE / TYPE_SYSTEM`; dependencies:
>   `ffi_minimum_sound_profile`, `raw_pointer_provenance`,
>   `unsafe_boundary_surface`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
단일 C 함수와 이름 있는 C library block을 같은 외부 경계 모델 안에서
표현하되, 단지 철자를 인식했다는 이유로 safety, layout 또는 product
support를 주장하지 않게 한다. 이 기능은 `extern#C def#unsafe`와
`extern c("library") { unsafe def ... }`라는 구문 route의 owner다.
surface 선택과 최소 sound profile을 분리함으로써, 이후 ABI profile이
확장되더라도 syntax gate 하나가 모든 외부 책임을 암시하지 않게 한다.

**제안 표면**
function route는 `PreviewFfiFunctionDecl`, block route는
`PreviewFfiBlockDecl`과 그 member다. 이 기능의 gate closure는 자기
자신과 `ffi_minimum_sound_profile`을 정확히 함께 요구한다. 순서는 gate
목록에서 의미 우선순위를 만들지 않지만, registry에 기록된 두 ID가 모두
명시되어야 한다. unknown, duplicate, nonactivatable ID 또는 누락된
dependency가 있으면 구문 body를 의미 분석하기 전에 결정적 gate 진단을
낸다.

**정적 판정과 상호작용**
library string은 compile-time plain string이어야 하고 동적 library
선택을 뜻하지 않는다. block member의 `unsafe`는 foreign call boundary의
정적 authority이며 `effects {unsafe}`로 치환되지 않는다. 함수와 block
형태 모두 parameter/result의 FFI representability, pointer provenance,
foreign resource owner와 effect/error mapping을 통과해야 한다. C
aggregate, variadic, stored callback, implicit layout derivation은 이
surface를 열었다고 함께 활성화되지 않는다.

**평가·소유권·오류**
외부 호출의 인수 평가 순서는 일반 Deeplus 호출 순서를 보존한다. ABI
호출 직전까지의 실패는 전달되지 않은 owner를 소비하지 않아야 하고,
전달 이후의 cleanup 책임은 선언된 mapping에만 따른다. foreign integer
status를 자동 `Error`로 바꾸거나 null pointer를 자동 `Option`으로
바꾸지 않는다. 잘못된 gate에서는
`FFI_C_EXTERN_UNSAFE_SURFACE_MSP_REQUIRES_FEATURE_GATE`,
의존성 누락에서는 `PREVIEW_GATE_DEPENDENCY_MISSING`가 우선하며, 이후
signature 진단으로 fallback하지 않는다.

**현행 대안과 이행**
현행 Stable 대안은 명시적으로 검증된 wrapper/provider 또는 외부에서
생성된 typed binding을 ordinary named API 뒤에 두는 것이다. 기존 C
header나 오래된 pseudo-extern 선언을 자동 변환하면 ownership과 nullable
정책을 임의 선택하게 되므로 자동 rewrite는 금지한다. migration report는
library identity, 각 parameter의 representation, owner direction과
cleanup 공백을 항목별로 보여야 한다. formatter는 gate를 source 첫
위치에서 보존하고 LSP는 block/member와 sound profile 의존성을 각각
탐색 가능하게 해야 한다.

**활성화 선행 조건**
exact EBNF/root와 lossless CST, ABI별 type mapping, provenance와
unsafe-authority calculus, resource/unwind/cleanup 법칙, gate 및
feature-local diagnostic 순서, formatter/LSP, header projection 검증,
MIR/xVM bytecode identity, native target의 양성·음성·경계·mutation corpus와
artifact-bound 실행 receipt가 모두 필요하다. 현재 모든 제품 lane은
`NOT_RUN`이며 이 문서의 예시는 activation이나 P1 closure가 아니다.

양성 block 예시는 두 Preview dependency를 모두 적고 library identity를
정적으로 고정한다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile)
extern c("sqlite3") {
    unsafe def sqlite3_close(db: RawPtr<sqlite3>) -> CInt
        effects {io}
}
```

음성 예시는 정확한 surface ID만 적어 최소 sound profile을 누락한다.
누락된 기능을 암시적으로 켜지 않고 `PREVIEW_GATE_DEPENDENCY_MISSING`를
낸다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp)
extern c("libc") {
    unsafe def puts(text: CString) -> Int
}
```

경계 예시는 같은 ID의 첫 중복이다. 중복을 집합처럼 조용히 합치지 않고
`PREVIEW_GATE_DUPLICATE_FEATURE`를 낸다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(ffi_c_extern_unsafe_surface_msp,ffi_minimum_sound_profile,ffi_minimum_sound_profile)
extern#C def#unsafe c_abs(x: Int) -> Int
```

<!-- deeplus-preview-feature-example: numeric_array_elementwise_power_msp; registry-status: PREVIEW -->
<a id="preview-feature-numeric_array_elementwise_power_msp"></a>

## NumericArray 원소별 infix 거듭제곱

> **Feature metadata**
> - Feature ID: `numeric_array_elementwise_power_msp`
> - Registry status: `PREVIEW`; activation: `explicit_feature_gate`
> - Authority: `LANGUAGE / TYPE_SYSTEM`; dependencies:
>   `caret_power_operator_msp`, `numeric_array_elementwise_arithmetic_msp`
> - P1 영향: 없음. 정확한 OPEN P1 집합을 추가·폐쇄하지 않는다.

**검토 목적**
NumericArray의 각 원소에 같은 지수를 적용하는 의도를 닫힌 연산자
규칙으로 표현하면서, 붙은 postfix transpose와 spaced infix power를
혼동하지 않게 한다. 이 기능은 새 CFG production을 추가하는 대신 기존
`PrattExpr` 의미 route에서 gate와 operand domain을 검사한다. Stable
`values^`는 transpose이고 Preview `values ^ 2`는 원소별 power이므로
공백/attachment 경계가 semantic owner를 결정한다.

**제안 표면**
source 첫 위치의
`#preview(numeric_array_elementwise_power_msp)`가 Preview root를 고른다.
이 기능의 gate closure에는 다른 Preview ID가 없고, registry의
`caret_power_operator_msp`와
`numeric_array_elementwise_arithmetic_msp` 의존성은 이미 Stable
설계이므로 gate 목록에 적지 않는다. gate가 없으면 infix 형태는
`NUMARR_INFIX_POWER_REQUIRES_PREVIEW_GATE` 또는 현재 gate-map의
`NUMARR_INFIX_POWER_NOT_ADMITTED`로 거부된다.

**정적 판정과 상호작용**
base는 admitted NumericArray이고 exponent와 element domain은
feature-local power law를 만족해야 한다. 이 기능은 implicit broadcast,
`matrix .^ n` 같은 과거 철자, arbitrary operator overloading 또는
Trait witness dispatch를 열지 않는다. matrix multiplication `**`,
ordinary scalar infix power와 attached postfix transpose는 각각 별도
owner다. shape/rank/orientation과 result-shape가 정적으로 결정되지 않으면
gate가 있어도 거부해야 한다.

**평가·소유권·오류**
base와 exponent는 왼쪽에서 오른쪽으로 각각 한 번 평가된다. 결과는
새 NumericArray 값이며 입력을 암시적으로 mutable place로 만들지 않는다.
원소 연산의 overflow/failure 정책과 부분 결과 cleanup은 선택된 element
domain 계약을 따르고, 실패 전에 입력 owner를 소비하거나 일부 결과를
publish해서는 안 된다. postfix transpose는 view/representation 법칙을
따르는 별도 평가이며 infix power로 fallback하지 않는다. 제품 checker와
backend 실행은 여전히 `NOT_RUN`이다.

**현행 대안과 이행**
gate를 사용하지 않는 Stable source는 명시적인 named elementwise power
API나 이미 승인된 element transform을 사용한다. formatter는
`values^`와 `values ^ 2` 사이의 공백을 미용상 변경해서는 안 되고,
migration 도구도 transpose를 power로 또는 power를 transpose로 자동
rewrite해서는 안 된다. LSP는 hover에서 postfix/infix owner, gate 상태,
shape와 element result를 함께 보여야 하며 과거 `. ^` 계열 철자를 이
기능의 양성 예시로 제시해서는 안 된다.

**활성화 선행 조건**
정확한 operand/result shape 법칙, exponent domain, overflow/error와
cleanup, Pratt owner 및 spacing 보존, gate-aware formatter/LSP,
양성·음성·attachment 경계·shape mutation corpus, MIR elementwise event와
xVM/LLVM 동등 실행 receipt가 필요하다. 독립 conformance와 실제 사용자
연구를 포함한 제품 lane은 모두 `NOT_RUN`이고, 정적 예시만으로 지원을
주장할 수 없다.

양성 예시는 source 첫 gate와 spaced infix operator를 함께 사용한다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(numeric_array_elementwise_power_msp)
let squared = values ^ 2
```

음성 예시는 같은 spaced infix 형태를 Stable root에서 사용한다. parser가
postfix transpose로 재해석하지 않고 Preview gate 진단을 내야 한다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
// 검토용 음성 조각: gate가 없으므로 원소별 power는 거부된다.
let squared = values ^ 2
```

attachment 경계 예시는 양성 gate 안에서도 `values^`를 사용한다. 이는
오류가 아니라 Stable postfix transpose owner이며, power 결과를 기대한
문맥이라면 그 결과 type/shape 불일치가 별도로 보고된다.

<!-- deeplus-example: illustrative; status: PREVIEW_GATED; authority-source: spec/features/gates.json -->
```deeplus
#preview(numeric_array_elementwise_power_msp)
let transposed = values^
```
