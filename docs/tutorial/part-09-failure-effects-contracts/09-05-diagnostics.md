# 09-05 — 진단 우선순위와 오류 경계

## 1. 좋은 진단의 목표
> 상태: `CURRENT_DESIGN_PRODUCT_NOT_RUN`

진단은 단순히 오류 문자열을 출력하는 기능이 아니다. 같은 source에는
여러 문제가 동시에 보일 수 있으므로 Deeplus는 가장 이른 owner가
가장 구체적인 원인을 먼저 보고한다. 뒤 단계는 앞 단계가 실패한
구조를 임의로 보완하거나 별도의 의미 node로 바꾸지 않는다.

## 2. 단계별 owner

진단 owner는 대체로 다음 순서를 따른다.

1. lexer: 토큰과 literal 형식
2. parser: delimiter, token ownership, 문법 구조
3. name resolver: 이름과 가시성
4. type/checker: 타입, 리파인먼트, exhaustiveness
5. ownership/effect checker: 이동, 대여, 격리, 책임
6. lowering verifier: HIR/MIR invariant

한 단계가 정확한 오류를 확정하면 뒤 단계는 그 오류를 가리는 추측성
진단을 primary로 올리지 않는다.

## 3. 문법 오류와 의미 오류를 분리한다

문법에 없는 source는 AST 의미를 갖지 않는다. parser가 잘못된 구조를
발견했으면 타입 checker가 가상의 표현식을 만들어 타입 오류를
보고해서는 안 된다. 반대로 문법은 맞지만 이름이나 타입이 잘못된
경우에는 해당 의미 owner가 진단한다.

```deeplus
private def select(values: List<Int>, index: Int) -> Int = {
    return values[index]
}
```

이 예시에서 bracket 구조와 1-based logical index가 문법적으로
성립한 뒤에야 index 타입과 범위 계약을 검사한다.

## 4. primary와 suppressed 진단

하나의 root cause에서 여러 오류가 파생될 수 있다. Deeplus는
deterministic precedence로 primary 하나를 선택하고, 도움이 되는
후속 정보만 suppressed 또는 note로 결합한다. source 순서만으로
후보의 의미 우선순위를 정하거나 formatter가 오류를 자동 수정한 뒤
다른 결과를 내서는 안 된다.

```deeplus
private def describe(value: Int | String) -> String = {
    return @match value {
        number: Int => "number ${number}"
        text: String => text
    }
}
```

exhaustiveness, unreachable arm, binding 타입은 모두 match owner가
일관된 순서로 판정한다.

## 5. 진단 필드

도구가 안정적으로 소비할 수 있도록 논리 진단 family에는 최소한 다음
필드가 필요하다.

- diagnostic family 또는 정식 registry code
- severity와 primary span
- semantic owner
- 관련 이름·타입·case·effect identity
- deterministic note와 fix 제안
- admission 뒤 남은 AST/HIR/MIR residue 여부

정식 code가 아직 승인되지 않은 Preview Design은 임의 번호를 만들지
않고 logical family와 필드 schema만 설명한다.

### 5.1 effect row의 “해석 실패”와 “관계 실패”

effect/error row 진단은 두 문제를 분리한다. 먼저 row variable과 alias를
canonical identity로 해석할 수 있는지 검사한다. 그 다음에야 호출
문맥이 요구한 부분집합 또는 동등 관계를 검사한다.

- required row variable을 찾지 못한 경우는
  `EFFECT_ROW_SUBSUMPTION_NOT_ADMITTED`가 primary이고,
  `EFFECT_ROW_VARIABLE_UNBOUND`가 required 쪽을 설명하는 secondary다.
- implementation row variable을 찾지 못한 경우도 같은 primary를
  사용하되 secondary가 implementation 쪽을 가리킨다.
- alias가 missing, wrong-kind, ambiguous 또는 cyclic이면 row를
  비교할 수 없으므로 normalization 실패다.
- 두 row가 정상적으로 해석됐지만 trait witness 또는 function value의
  부분집합 조건, 혹은 class override의 동등 조건을 만족하지 않으면
  relation 실패다.

이 구분 덕분에 “이름을 해석할 수 없음”을 “effect가 너무 큼”으로
오진하지 않는다. 여기서 설명하는 registry route는 정본 설계 계약이며
실제 checker emission과 formatter/LSP 지원은 여전히 `NOT_RUN`이다.

### 5.2 quantified effect/error row

`EffectErrorRowPolymorphismAdmitted`는 선언된 generic row parameter의
finite constraint가 모델을 가지며 principal closed substitution 하나를
정하는지 검사한다. constraint가 모순이면
`EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED`를 보고한다. 모델은 있지만
어떤 variable의 membership이 참과 거짓 모두 가능하면 역시
nonprincipal로 거부한다.

scope 검사는 equality의 작성 방향에 영향을 받지 않는다. 예를 들어
`E == Local`과 `Local == E`는 같은 scope reachability를 만든다.
선언된 export root가 solver-local parameter에 닿으면 private row가
공개 signature로 새는 것이므로 같은 primary diagnostic으로 거부한다.
비슷한 이름을 가진 `RESULT_THROWS_CHANNEL_OVERLAP`은 throws/result
channel owner의 진단이므로 이 판정에 대신 사용하지 않는다.

## 6. fix 제안의 경계

fix는 사용자의 의도를 바꾸지 않는 경우에만 제시한다. 여러 의미 선택지가
있는 migration, 소유권 전략 변경, 공개 API 책임 변경은 자동 rewrite
대상이 아니다. 진단은 가능한 선택지를 설명할 수 있지만 최종 의미를
대신 선택하지 않는다.

## 7. Preview 진단

Preview Gated 기능은 gate 누락, 알 수 없는 ID, dependency 누락과 일반
문법 오류를 구분한다. Preview Design은 현재 source route가 없으므로
설명 문서가 후보 진단 family를 제시할 수는 있어도 현재 compiler
registry code나 실행 PASS를 주장하지 않는다.

## 8. 진단을 읽는 절차

먼저 primary span과 owner를 확인한다. 다음으로 source를 그 owner의
계약에 맞게 고친다. 그 뒤 다시 판정하여 suppressed 오류가 독립적으로
남는지 확인한다. 여러 단계를 한꺼번에 추측해 고치면 원래 원인을
숨기거나 다른 책임을 새로 만들 수 있다.

## 9. 작성 규칙

- negative 예제에는 expected diagnostic owner를 적는다.
- 문법 오류 예제에 타입 결과를 부여하지 않는다.
- Preview Design의 logical family와 정식 registry code를 혼동하지 않는다.
- formatter/LSP fix는 의미 보존을 증명할 수 있을 때만 허용한다.
- static validation을 제품 conformance PASS로 표현하지 않는다.
- effect row에서 unbound/normalization/relation 실패를 서로 바꾸어
  설명하지 않는다.
- typed dispatch fixture가 PASS해도 checker 제품 실행을 PASS라고 쓰지
  않는다.

## 10. 연습 문제

1. **owner 판정:** delimiter가 닫히지 않은 call과 타입이 맞지 않는
   call의 primary owner를 각각 적어라.
2. **우선순위 설계:** 하나의 match arm에서 이름 오류와 타입 오류가
   함께 보일 때 어떤 정보를 먼저 확정해야 하는지 설명하라.
3. **fix 경계:** 자동 수정하면 안 되는 소유권 또는 공개 API 변경의
   예를 하나 만들고 이유를 적어라.

## 11. 빠른 복습

- 가장 이른 정확한 owner가 primary 진단을 선택한다.
- 문법 실패는 가상의 의미 node로 보완하지 않는다.
- fix는 의미를 대신 선택하지 않는다.
- Preview 진단과 Current registry code의 권위를 구분한다.
- effect row의 normalization failure와 relation failure를 구분한다.

## 12. 정본 근거

- [제어 흐름, 오류, effect 및 정리](../../grammar-reference/11-control-flow-errors-effects-and-cleanup.md)
- [Preview 표면](../../grammar-reference/15-preview-surfaces.md)
- [R9 typed diagnostic-dispatch 계약](../../../spec/contracts/diagnostic-dispatch-closure-r1.json)
- [진단 catalog 메타데이터](../../../spec/diagnostics/catalog/catalog-metadata.json)
