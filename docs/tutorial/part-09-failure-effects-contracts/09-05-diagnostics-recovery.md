# 09-05 — 진단 우선순위와 recovery 경계

## 1. 상태와 읽는 법

> 상태: `MIXED_STATUS`

현행 진단 pipeline은 `CURRENT_DESIGN_PRODUCT_NOT_RUN`이다. 아래
`null`, custom operator 같은 철자는 `RECOVERY_ONLY` 또는 removed
migration probe이며 positive source가 아니다.

## 2. 학습 목표

- lexer, parser, checker, verifier 단계의 역할을 구분한다.
- 첫 실패 조건이 primary diagnostic을 소유하는 이유를 이해한다.
- recovery recognition과 source admission을 분리한다.
- rejected source가 AST/HIR/MIR residue를 만들지 않는 경우를 설명한다.

## 3. 선수 지식

source root, exact grammar, type checking, HIR-H1 pipeline을 알고 있어야 한다.

## 4. 문제에서 출발하기

친절한 compiler는 옛 철자를 알아보고 “무엇을 써야 하는지” 알려 줄 수
있다. 그러나 알아봤다는 이유로 그 철자를 유효 프로그램으로 만들면
언어 경계가 무너진다. Deeplus recovery는 진단을 위한 bounded recognition일
뿐 의미 노드 생성 권위가 아니다.

## 5. 핵심 모델

1. lexer: token과 attachment를 결정한다.
2. parser: 하나의 source root와 structural owner를 결정한다.
3. admission/checker: profile, type, call shape, pattern, ownership을 검사한다.
4. verifier/linker: closed identity와 API coherence를 확인한다.
5. runtime: 앞 단계를 통과하고 구현된 프로그램만 도달할 수 있다.

앞 단계에서 결정적으로 거부되면 뒤 단계의 추측 진단을 쌓지 않는다.
Recovery-only surface는 전용 진단 뒤 admitted AST/HIR/MIR count가 0이다.

## 6. 단계별 예제

현행 absence 값은 `Option::none`이다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
let cached: Option<String> = Option<String>::none
let text = cached ?: "missing"
```

`null`은 parser가 정확한 migration 진단을 내기 위해 예약하지만 값이
아니다.

<!-- deeplus-example: illustrative; surface: RECOVERY_ONLY; product: NOT_RUN; expected: REJECT -->
```deeplus
let cached: Option<String> = null
// NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE
```

## 7. 허용·거부·경계 사례

custom operator 선언은 Preview 후보도 아니다. named API를 쓴다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
def mergeScores(left: Score, right: Score) -> Score = {
    return Score!(value: left.value + right.value)
}
let total = mergeScores(first, second)
```

옛 operator declaration은 diagnostic probe일 뿐이다.

<!-- deeplus-example: illustrative; surface: RECOVERY_ONLY; product: NOT_RUN; expected: REJECT -->
```deeplus
operator <+> precedence 120
// CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT
```

같은 recovery family에는 `[]` empty index, generic entry, old `**`
named-rest, `let @ lazy`, unit middle dot, Facet probe, quarantine probe가
있다. 각각의 대체 경로를 사용하고 positive 예제에 복사하지 않는다.

## 8. 다른 기능과의 연결

- formatter는 recovery source를 current normal form처럼 보존해서는 안 된다.
- LSP quick fix는 semantic identity를 바꾸는 자동 migration을 해서는 안 된다.
- no-go catalog는 removed spelling과 primary diagnostic을 결합한다.
- example manifest의 `accept`도 현재는 design-static이며 compiler PASS가
  아니다.

### 판정 추적

예를 들어 prefix 없는 `raw"..."`를 보면 lexer가 legacy shape를 bounded
recognition하고 `#raw"..."` 대안을 가리키는 전용 진단을 낸다. 그
다음 parser가 편의상 current string node를 만들거나 checker가 type을
붙이지 않는다. admitted AST, HIR-H1, MIR residue가 모두 0인지가 recovery
경계의 핵심 검증이다. 수정된 source는 처음부터 다시 lexer→parser→checker
순으로 판정한다.

미니 사례로 old named-rest `options**: T`가 보이면 triple-star
`options***: T`를 제안할 수 있다. 그러나 quick fix는 call shape와 label,
ownership이 그대로인지 확인해야 하며, 확인 없이 전체 프로젝트를
자동 치환해서는 안 된다.

### 흔한 오해

좋은 오류 메시지를 내므로 “숨겨진 호환 문법”이라고 생각하는 것은
잘못이다. recovery parser는 사용자의 의도를 진단하기 위한 제한된
관찰자이지 source admission owner가 아니다. 여러 후속 오류를 많이
보여 주는 것보다 첫 결정적 실패와 안전한 대안을 정확히 제시하는 것이
우선이다.

진단을 검토할 때는 네 항목을 한 묶음으로 기록한다. 첫째, 실제로
소유한 단계와 primary span. 둘째, stable diagnostic identity. 셋째,
대체 spelling이 의미·ownership·effect를 보존하는 조건. 넷째, 거부된
조각의 residue zero 증거다. 메시지 문구만 자연스럽고 이 결합이 없으면
formatter나 LSP가 서로 다른 수정을 제안할 수 있다. 반대로 이 결합이
있으면 recovery token을 current AST로 승격하지 않고도 친절한 안내가
가능하다.

## 9. Deeplus다운 작성 관례

오류 메시지 수보다 원인 순서를 우선한다. 첫 diagnostic의 stage, source
span, owner, 대체 형식을 읽고 고친 뒤 다시 판정한다. recovery 철자를
“숨은 기능”으로 이용하지 않는다.

## 10. 연습 문제

1. **따라 하기:** `null` 예제를 `Option::none`으로 고치고 의미 차이를
   설명하라.
2. **빈칸 완성:** old named-rest `name**: T`의 current spelling
   `name***: T`를 채워라.
3. **스스로 설계하기:** parse 오류와 checker 오류가 동시에 의심되는
   조각에서 primary diagnostic 선택 순서를 작성하라.

## 11. 빠른 복습

- recovery recognition은 admission이 아니다.
- rejected probe는 admitted AST/HIR/MIR을 만들지 않는다.
- custom operator는 Preview가 아니다.
- primary diagnostic은 첫 결정적 실패 조건이 소유한다.

## 12. 정본 근거와 다음 장

- [Preview, recovery, removed surface](../../grammar-reference/15-preview-recovery-and-removed-surfaces.md)
- [no-go catalog](../../../spec/compatibility/no-go/catalog-metadata.json)
- [diagnostic registry](../../../spec/diagnostics/catalog/catalog-metadata.json)

이제 Part의 축을 하나의 회복 가능한 import workflow에 적용한다.
