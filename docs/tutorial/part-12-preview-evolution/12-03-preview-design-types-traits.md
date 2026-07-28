# 12-03 — Preview Design: 타입, 객체와 Trait

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`
>
> 미니 범례: `CURRENT`는 오늘 사용할 수 있는 explicit 대안,
> `PREVIEW_DESIGN_NONACTIVATABLE`은 검토용 expected-reject probe다.
> proposal은 gate로 켤 수 없고 product는 `NOT_RUN`이다.

이 장의 모든 제안은 `source_activation = nonactivatable`이다. 선택된
후보 철자를 보여 주는 블록도 current/Preview Gated source가 아니라
expected reject probe다. 이 장은 새 syntax, P1 closure, 구현 authority
또는 product support를 만들지 않는다.

## 2. 학습 목표

- 타입·객체·Trait Preview Design을 문제군별로 분류한다.
- current explicit alternative와 candidate surface를 구분한다.
- coherence, witness, identity와 ownership 검토 질문을 세운다.
- Option optional-binding 후보가 current pattern authority를 재사용하는
  경계를 설명한다.

## 3. 선수 지식

Class/Record/Enum/Union, Trait conformance, witness selection, refinement,
ownership facet와 qualified path를 알고 있어야 한다.

## 4. 문제에서 출발하기

짧은 sugar를 먼저 고르면 중요한 질문이 가려진다. 예를 들어 “Class에
static을 넣자”는 말만으로는 storage identity, initialization effect,
generic instantiation별 cell 수, unload/drop owner가 결정되지 않는다.
“local witness를 허용하자”는 말도 같은 pair에 여러 witness가 보일 때
coherence와 link identity를 닫지 못한다.

따라서 Preview Design은 syntax 선호 투표가 아니라, 정적 의미와 관찰
가능성이 닫히는지를 검토하는 exact probe다.

## 5. 핵심 모델

이 문서군의 19개 exact feature ID를 네 문제군으로 읽을 수 있다.

1. **활성화·공유 상태**
   - `class_static_activation`
   - `effectful_static_activation`
2. **Trait evidence와 coherence**
   - `conformance_law_proof_block_preview_design`
   - `first_class_witness_value_not_current`
   - `local_witness_preview_design`
   - `negative_impl_preview_design`
   - `specialization_preview_design`
   - `sealed_multimethod_family`
3. **refinement·dynamic type boundary**
   - `dependent_refinement_value_capture`
   - `solver_backed_general_refinement`
   - `dyn_rcts_family`
   - `dynamic_trait_attach_detach_stateless_preview_design`
   - `option_let_question_binding_preview_design`
4. **extension·facet·projection**
   - `extension_dot_call_sugar`
   - `generic_named_extension_set_target`
   - `structural_prototype_extension`
   - `facet_inout_pack_preview_design`
   - `facet_owned_pack_preview_design`
   - `use_site_projection_dmad`

이 목록은 activation 목록이 아니다. 각 feature는 exact source surface,
owner identity, type rule, witness/admission order, ownership/effect
responsibility, deterministic diagnostic, HIR residue와 activation evidence가
별도 authority로 닫히기 전까지 현행 프로그램에 들어갈 수 없다.

## 6. 단계별 예제

### 1단계: static 요구를 explicit owner로 풀어 쓴다

Class-level activation의 successor 철자는 미선정이다. 현행 대안은
module binding과 named entry point로 storage/effect owner를 드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private let cache = Cache!()

public def warmCache() -> Unit = {
    cache ~ warm
}
```

이 대안은 Class identity와 storage identity가 같다고 주장하지 않는다.
import만으로 effectful initialization이 일어나는 hidden rule도 만들지
않는다.

### 2단계: conformance와 법칙 증거를 구분한다

fixed-glyph conformance는 current Stable 계약이지만 source의 test 함수가
formal proof block은 아니다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public type UserId conforms Display {
    +def display+() -> String = { return self.raw ~ toString }
}

def displayIsStable(id: UserId) -> Bool = {
    return id ~ display == id ~ display
}
```

`conformance_law_proof_block_preview_design`은 proof calculus, trusted base,
termination, artifact binding을 검토하는 이름이다. 위 test의 존재만으로
proposal이 활성화되거나 법칙이 기계 증명되었다고 말하지 않는다.

### 3단계: Option optional binding을 기존 pattern과 비교한다

`let?`는 `Option<T>` 한 겹의 `::some` pattern을 짧게 쓰려는
nonactivatable 후보다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: option_let_question_binding_preview_design
if let? user = findUser(id) {
    show(user)
}

let? config = loadConfig() else {
    return defaultConfig()
}
```

정규화는 각각 현행 `if let ::some(user) = ...`와 mismatch disposition을
가진 guarded `let`을 재사용한다. `Option<T>` 한 겹만 열고 subject를 한
번 평가하며 성공 전에는 binding/move를 commit하지 않는다. Result,
arbitrary Enum, nullability, force unwrap, propagation, bare local
`let?` without `else`, `for`/comprehension/match/condition-chain으로
확대하지 않는다.

## 7. 허용·거부·경계 사례

허용: 새 glyph가 필요 없는 named API와 ordinary conformance로 의도를
드러낸다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
public def mergeScores(left: Score, right: Score) -> Score = {
    return Score!(value: left.value + right.value)
}

let total = mergeScores(a, b)
```

거부: Preview Design ID를 gate로 켜려 한다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
#preview(local_witness_preview_design,specialization_preview_design)
let shown = value ~ display
```

expected family는 nonactivatable feature를 gate 목록에 넣었다는 진단이다.
checker가 local witness나 specialization을 “최선의 후보”로 선택해서는 안
된다.

경계: first-class witness value를 제안할 때 witness를 ordinary runtime
object로만 모델링하면 canonical `TraitWitnessId`, parent evidence,
generic substitution과 link coherence가 사라진다. 반대로 모든 witness를
compile-time erased라 하면 dynamic carriage use case를 설명하지 못한다.
이 경계가 닫히기 전에는 syntax를 선택하지 않는다.

## 8. 다른 기능과의 연결

Trait proposal은 fixed-glyph operator, indexing, method dispatch와 이어진다.
하지만 임의 custom operator는 Preview 후보도 아니며 다시 만들지 않는다.
Enum order/display/subset은 이미 Stable이며 Preview proposal로 세지
않는다. Option binding proposal은 기존 pattern의 evaluation/commit과
exhaustiveness 책임을 보존해야 한다. facet/projection proposal은
borrow/move/inout 책임, mutation commit, cleanup을 HIR-H1에 lossless하게
남겨야 한다.

이 proposal들이 executable HIR/MIR로 내려가려면 exact verifier rule과
capability receipt가 필요하다. 현재 parser/checker/MIR/backend/tooling을
포함한 product lane은 `15/15 NOT_RUN`이다.

### 판정 추적과 흔한 오해

proposal은 exact ID, 해결할 문제, current 대안, 비목표를 먼저 적고
syntax는 그 뒤에 둔다. owner identity, witness uniqueness, type/effect/
ownership rule, negative·boundary diagnostic, HIR residue와 activation
evidence를 차례로 채운다. 어느 열이 비어 있으면 candidate probe는
expected reject로 남는다.

흔한 오해는 current explicit 대안이 있다는 사실을 proposal 구현으로
세거나, 문서의 상세한 candidate syntax를 사실상 승인으로 읽는 것이다.
미니 사례에서 module binding으로 cache를 명시한 것은 Class static
activation을 구현한 것이 아니며, local witness probe가 존재해도
child-local parent witness replacement나 specialization을 활성화하지
않는다.

## 9. Deeplus다운 작성 관례

- syntax보다 owner identity와 failure boundary를 먼저 쓴다.
- 같은 type pair의 witness가 하나로 닫히는지 항상 검토한다.
- Stable Enum derived capability를 Preview 목록에 되돌려 넣지 않는다.
- semantic identity, serialization tag, runtime discriminant, ordinal,
  layout/ABI identity를 별도 열로 기록한다.
- 임의 custom operator 대신 named API 또는 admitted fixed-glyph
  conformance를 쓴다.
- current lowercase `via`를 successor `VIA`/`AUTO` route로 재해석하지
  않는다.

## 10. 연습 문제

1. **그대로 따라 하기:** `cache`/`warmCache` 대안을 옮겨 적고 storage
   owner, initialization entry, effect owner를 표시하라.
2. **빈칸 채우기:** Enum identity 표에서 semantic identity는 `____`,
   Trait evidence identity는 `____`로 채우고 serialization tag와 왜
   분리되는지 설명하라.
3. **스스로 설계하기:** `local_witness_preview_design` 검토 카드에
   positive/negative/boundary scenario, coherence invariant, HIR residue,
   required diagnostic, activation evidence를 작성하라. syntax 선택은
   하지 말라.

## 11. 빠른 복습

- 타입·객체·Trait Preview Design은 이 장의 19개 exact ID 검토면이다.
- 모두 `NONACTIVATABLE`이며 current source가 아니다.
- current explicit alternative는 proposal의 문제를 설명하되 proposal을
  몰래 구현하지 않는다.
- Option binding 후보는 Option/pattern identity를 새 runtime node로 바꾸지 않는다.
- static example이나 schema 존재만으로 P1/product 상태는 바뀌지 않는다.

## 12. 정본 근거와 다음 장

- [Preview Design — 타입·객체·Trait](../../grammar-reference/21-preview-design-types-objects-and-traits.md)
- [Trait 정본 의미](../../../spec/language.md)
- [Enum derived capability 계약](../../../spec/contracts/enum-derived-capabilities.json)
- [type-flow-callable coherence](../../../spec/contracts/type-flow-callable-coherence.json)

다음 장에서는 collection shape, context argument, snapshot/view, literal
shape와 null-safe control 제안을 같은 방법으로 검토한다.
