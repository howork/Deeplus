# 부록 C — 진단을 읽고 고치는 법

> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`
>
> diagnostic catalog는 정본 설계지만 실제 frontend·formatter·LSP
> 출력과 product acceptance는 `NOT_RUN`이다.

## 1. 오류 메시지를 네 질문으로 나누기

진단을 보면 코드를 무작정 바꾸기 전에 다음을 적는다.

1. **어느 phase의 소유인가?** scanner, parser, resolver, checker,
   ownership/effect, admission, lowering 중 어디인가?
2. **무엇이 primary span인가?** 원인 token과 파생 오류 위치를 구분한다.
3. **어떤 identity가 필요한가?** type, Enum case, Trait witness,
   actor protocol, Module path 중 무엇인가?
4. **고친 뒤 무엇이 보존되어야 하는가?** ownership, effect, evaluation
   order, source spelling, status fence를 확인한다.

## 2. syntax와 semantic 오류

syntax 오류는 token이 해당 grammar goal에서 production을 만들지 못한
경우다. semantic 오류는 AST가 형성됐지만 name/type/effect/ownership
규칙을 만족하지 못한 경우다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
let values = [10, 20, 30]
let first = values[0]         // 일반 sequence의 첫 index라고 가정
```

index expression 자체는 parse되지만 1-based bounds semantics에서
실패한다. parse 성공과 semantic admission을 같은 것으로 보면 수정
지점이 흐려진다.

## 3. 타입·refinement·pattern 진단

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT -->
```deeplus
type Positive = Int where > 0

def assume(value: Int) -> Positive = {
    return value
}
```

기반 타입이 `Int`로 같아도 refinement proof가 없다. 해결은 unchecked
cast가 아니라 입력을 checked conversion으로 바꾸거나, 반환을
`Option<Positive>`/`Result`로 바꾸거나, 호출 계약에서 proof를 받는
것이다.

pattern 진단에서는 structural test, type test, binding transaction,
guard, exhaustiveness를 따로 본다. 앞 arm에서 실패한 binding을 뒤
arm에서 읽을 수는 없다.

## 4. effect와 ownership 진단

signature에 없는 I/O, actor send, `await`, FFI, error를 body에서
발생시키면 callable identity와 구현이 맞지 않는다. effect를 숨기려고
catch-all이나 wrapper를 넣기 전에 실제 책임 owner를 정한다.

borrow가 escape·suspension·actor crossing을 넘는 오류는 “lifetime을
길게 쓰면” 자동 해결되지 않는다. 복사, move, owned snapshot, 작업
분해 중 의미에 맞는 선택을 해야 한다.

## 5. 연쇄 오류 줄이기

가장 앞선 phase의 primary 진단부터 고친다. 예를 들어 Module path가
해결되지 않아 type과 witness가 모두 사라졌다면, 뒤쪽 “conformance
없음”을 먼저 고치지 않는다. compiler가 문법에 없는 source를 의미
node로 만들지 않았는지도 확인한다.

좋은 진단 보고서는 다음을 포함한다.

- source snippet과 primary/secondary span
- stable diagnostic family
- phase와 owner
- 기대 type/effect/identity
- 실제로 관찰된 값
- 안전한 수정 방향
- Preview 상태

## 6. 연습 문제

1. **따라 하기:** 위 `Positive` 예제를 parser/checker 단계로 나눠
   어디까지 성공하는지 적어라.
2. **빈칸 완성:** actor boundary를 넘는 borrow 오류의 owner timeline을
   작성하라.
3. **직접 설계:** non-exhaustive Enum match 진단에 필요한 primary
   span, missing case list, fix-it 조건을 정하라.
4. **경계 과제:** 문법에 없는 source가 AST를 남기면 안 되는 이유를
   HIR-H1 관점에서 설명하라.

## 7. 교육용 rule label과 registry ID

이 튜토리얼은 diagnostic catalog에 실제로 존재하는 이름만
`diagnostic-family` 또는 exact ID라고 부른다. 일반적인 block-scope
name-not-found처럼 한 상황만을 전담하는 stable exact catalog ID가 없는
실패를 설명하는 장은 `expected-rule` 또는 `teaching-label`이라고 표기한다.
Message와 actor-message는 ordinary call과 같은 ordered argument
진단 family를 사용하며 별도의 “payload-row” 진단을 발명하지 않는다.
이는 새 diagnostic, 새 P1, 구현 지원을 발명하는 표식이 아니다.

향후 exact ID를 정본화하려면 resolver/checker owner, primary span,
precedence, admission, fix-it, example fixture와 catalog row를 하나의 변경
집합으로 검토해야 한다. 비슷한 이름의 기존 진단을 단지 문구가
가깝다는 이유로 재사용하지 않는다.

### 7.1 R9 typed dispatch exact ID

다음 세 family는 현재 diagnostic catalog의 exact ID다.

| 판정 | exact primary | 읽는 법 |
|---|---|---|
| associated type/value/function requirement admission | `ASSOCIATED_REQUIREMENT_UNRESOLVED` | requirement kind·bounds/default·binding·dependency cycle 중 첫 rank를 확인한다. |
| quantified effect/error row admission | `EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED` | unbound/wrong-kind, unsat/nonprincipal, scope leak, substitution cycle 순으로 확인한다. |
| context별 effect row 관계 | `EFFECT_ROW_SUBSUMPTION_NOT_ADMITTED` | row normalization 뒤 trait/function subset 또는 override equality가 성립하는지 확인한다. |

`EffectRowSubsumes`의 required 또는 implementation row variable이
unbound이면 `EFFECT_ROW_VARIABLE_UNBOUND`가 secondary로 붙을 수 있다.
secondary는 primary를 대체하지 않는다. associated family는 type에만
한정되지 않고 immutable value와 function requirement까지 포함한다.
`EffectErrorRowPolymorphismAdmitted`는
`RESULT_THROWS_CHANNEL_OVERLAP`을 사용하지 않는다.

이 표는 static registry/dispatch 계약을 설명한다. 실제 frontend,
checker, formatter/LSP가 이 ID를 출력했다는 target-bound receipt는
없으므로 product 상태는 `NOT_RUN`이다.

## 8. 정본 근거

- `spec/diagnostics/catalog/**`
- `spec/diagnostics/relations/**`
- `spec/types/predicates/**`
- `spec/contracts/diagnostic-dispatch-closure-r1.json`
- [진단·predicate 색인](../../grammar-reference/appendices/d-diagnostic-predicate-index.md)
