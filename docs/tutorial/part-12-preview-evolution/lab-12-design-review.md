# Lab 12 — 비활성 설계 제안 검토 카드 만들기

> 상태: `MIXED_STATUS`
>
> 미니 범례: `CURRENT`는 proposal 문제를 오늘 해결하는 explicit 대안,
> `PREVIEW_DESIGN_NONACTIVATABLE`은 candidate expected-reject probe다.
> 검토 카드는 두 상태를 비교하지만 activation·product PASS를 만들지 않는다.

이 실습은 proposal을 구현하거나 활성화하지 않는다. 선택한 exact feature
ID의 문제, current alternative, 정적 의미, 관찰 가능성, diagnostic과
activation evidence를 한 장의 검토 카드로 닫는 연습이다. 결과물은
source authority, P1 또는 product lane을 바꾸지 않는다.

## 목표

- exact registry identity에서 시작한다.
- candidate surface와 current alternative를 다른 코드 블록에 둔다.
- positive, negative, boundary scenario를 기계적으로 비교 가능하게 쓴다.
- HIR/MIR/tooling/target evidence가 무엇인지 구체적으로 기록한다.
- 마지막에 `KEEP_NONACTIVATABLE`, `REVISE_PROPOSAL`, `REJECT_DESIGN`
  중 하나를 근거와 함께 선택한다.

## 준비

1. `spec/features/gates.json`에서 `PREVIEW_DESIGN` feature 하나를 고른다.
2. 해당 feature가 설명된 grammar reference의 metadata, dependency,
   current alternative와 activation 조건을 읽는다.
3. `current/current-pointer.json`과 관련 contract를 확인한다.
4. product lane `15/15 NOT_RUN`, semantic P0 `0`, exact OPEN P1 `22`,
   별도 OPEN action `M13-A002..005`를 메모한다.

이 실습은 예시로
`option_let_question_binding_preview_design`을 사용한다.

### 누적 프로젝트 연결

| 연결 | 이 실습에서 이어 받거나 넘기는 것 |
|---|---|
| input | Lab 11의 current Module/API/codec/adapter와 HIR evidence 경계를 비교 기준으로 받는다. |
| output | exact ID, current 대안, candidate probe, guard·evidence·판정을 가진 비활성 검토 카드를 만든다. |
| next | 후속 Design 검토에는 카드와 미해결 질문만 넘기며 implementation/GitHub 작업은 자동 활성화하지 않는다. |

## 단계별 구현

### 1단계 — identity와 상태를 복사한다

검토 카드 첫머리를 다음처럼 만든다.

```text
feature_id: option_let_question_binding_preview_design
registry_status: PREVIEW_DESIGN
source_activation: nonactivatable
candidate_status: PREVIEW_DESIGN_NONACTIVATABLE
product_lanes: 15/15_NOT_RUN
p1_delta: 0
implementation_authority: NONE
```

feature 이름을 줄이거나 비슷한 별칭을 만들지 않는다. artifact digest와
Git commit SHA도 같은 hash domain처럼 비교하지 않는다.

### 2단계 — 해결할 문제와 비목표를 쓴다

문제는 “Option을 편하게 푼다”보다 정확해야 한다.

- `Option<T>` 한 겹의 `::some` pattern을 얼마나 줄이는가?
- subject 단일 평가와 atomic binding commit을 어떻게 보존하는가?
- `if`/`while`/guarded local `let`의 mismatch disposition은 무엇인가?
- `let`과 `?` 사이 trivia를 허용할 것인가?
- Result·arbitrary Enum·force unwrap·propagation으로 확대하지 않는가?

비목표에는 nullability, general truthiness, bare local `let?` without
`else`, condition chain, automatic migration과 product support를 적는다.

### 3단계 — candidate probe와 current alternative를 분리한다

candidate probe는 expected reject다.

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
// feature: option_let_question_binding_preview_design
if let? value = maybeValue {
    consume(value)
}
```

current alternative는 explicit `::some` pattern이다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
if let ::some(value) = maybeValue {
    consume(value)
}
```

두 블록을 한 declaration에 섞지 않는다. current function은 proposal
implementation이 아니라 오늘 사용할 수 있는 explicit design이다.

### 4단계 — 정적 판정 표를 채운다

다음 열을 가진 표를 만든다.

| scenario | expected | 이유 | required diagnostic/receipt |
|---|---|---|---|
| `Option<T>`과 irrefutable child pattern | proposal-positive | 한 겹 some binding | activation 이후에만 admission |
| `Result<T,E>` subject | proposal-negative | Option-only profile | deterministic subject-type diagnostic |
| `Option<Option<T>>` subject | boundary | 한 번에 한 겹만 open | inner Option 유지 evidence |
| stored/moved subject | boundary | single evaluation·commit 필요 | ownership trace |
| bare local `let?` without `else` | reject | mismatch disposition 없음 | missing-else diagnostic |

positive는 “현재 컴파일 성공”이 아니다. ratification에 필요한 의미가
일관되는지 보여 주는 proposal scenario다.

### 5단계 — ownership, effect와 IR residue를 쓴다

subject는 한 번 평가하고 `::some` structural test 성공 전에는 move,
borrow와 binding을 commit하지 않아야 한다. AST/HIR은 기존 Option
pattern으로 정규화하고 새 unwrap runtime node를 만들지 않는다.

다음 skeleton을 완성한다.

```text
surface_owner:
semantic_identity:
serialization_identity:
payload_access:
ownership_rule:
effect_rule:
hir_residue:
mir_observation:
formatter_rule:
lsp_rule:
migration_rule:
```

### 6단계 — activation evidence와 판정을 쓴다

최소 evidence는 exact grammar/recovery, Option-only checker, one-layer
normalization, evaluation/ownership/guard/exhaustiveness law, deterministic
diagnostics, formatter/LSP, positive/negative/boundary corpus, HIR/MIR
preservation과 target-bound receipt다.

현재 판정은 다음 중 하나여야 한다.

- `KEEP_NONACTIVATABLE`: 질문은 유효하지만 activation evidence가 없다.
- `REVISE_PROPOSAL`: identity나 법칙의 모순을 고쳐 다시 검토해야 한다.
- `REJECT_DESIGN`: current alternative가 충분하거나 Deeplus의 명시성/
  coherence 원칙과 충돌한다.

이 예시의 기본 판정은 `KEEP_NONACTIVATABLE`이다.

## 중간 점검

- exact feature ID와 registry status가 일치하는가?
- candidate code에 `PREVIEW_DESIGN_NONACTIVATABLE`과 expected reject가
  붙었는가?
- current alternative가 별도 block에 있는가?
- Option identity와 binding sugar를 분리했는가?
- positive, negative, boundary scenario가 각각 하나 이상 있는가?
- static evidence와 execution receipt를 구분했는가?
- P1 delta와 product state를 바꾸지 않았는가?

하나라도 “아니오”라면 activation 판정을 쓰지 말고 해당 단계로 돌아간다.

## 실패 실험

### 실험 1 — nonactivatable feature를 gate에 넣기

<!-- deeplus-example: illustrative; surface: PREVIEW_DESIGN_NONACTIVATABLE; product: NOT_RUN; expected: REJECT -->
```deeplus
#preview(option_let_question_binding_preview_design)
if let? value = maybeValue {
    consume(value)
}
```

예상 결과는 gate activation이 아니라 nonactivatable feature 진단이다.

### 실험 2 — Option과 Result를 같은 unwrap으로 합치기

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
// current explicit form: carrier마다 exact pattern을 사용한다.
let optionValue = @match maybeValue {
    ::some(value) => value
    ::none => fallback
}
```

검토 카드에서 Option absence와 Result error를 한 failure identity로
합쳤다면 실패다. carrier와 mismatch disposition을 분리한다.

## 연습 문제

1. **그대로 따라 하기:** 위 identity/status header와 두 코드 블록을
   그대로 옮기고 각 블록의 admission 상태를 표시하라.
2. **빈칸 채우기:** IR skeleton에서 `semantic_identity`를
   `Option::some`, `ownership_rule`을 `성공 전 ____ commit`으로 완성하라.
3. **스스로 설계하기:** Part 12의 다른 Preview Design feature 하나를
   골라 문제/비목표, current alternative, candidate probe,
   allow/reject/boundary, ownership/effect, HIR/MIR residue, diagnostic,
   activation evidence와 최종 판정을 갖춘 검토 카드를 작성하라.

## 확장 과제

- 두 proposal이 같은 token을 원할 때 lexical owner와 priority를 비교하는
  conflict register를 만든다.
- Preview Gated 기능 하나를 골라 dependency closure와 source-root
  placement를 추가한 별도 카드를 만든다.
- MIR-X1 draft를 대상으로 “유용한 설계 원칙”과 “아직 authority가 없는
  schema/backend 결정”을 두 열로 분리한다.
- diagnostic family가 recovery AST/HIR residue를 만들지 않는지 negative
  matrix를 보강한다.

## 완료 체크리스트

- [ ] exact feature ID와 authority source를 기록했다.
- [ ] 상태는 `PREVIEW_DESIGN_NONACTIVATABLE`이다.
- [ ] current alternative와 candidate probe를 분리했다.
- [ ] candidate probe는 expected reject다.
- [ ] allow/reject/boundary를 모두 기록했다.
- [ ] identity/type/ownership/effect/error를 검토했다.
- [ ] HIR/MIR/tooling/target evidence를 구분했다.
- [ ] semantic P0 `0`, OPEN P1 `22`, P1 delta `0`을 보존했다.
- [ ] `M13-A002..005`를 별도 OPEN action으로 보존했다.
- [ ] product lane은 `15/15 NOT_RUN`이다.
- [ ] implementation/activation/publication authority를 주장하지 않았다.

완성한 카드는 proposal을 켜는 파일이 아니라 다음 formal Design 검토가
같은 질문과 evidence domain을 재현하도록 돕는 비활성 자료다.
