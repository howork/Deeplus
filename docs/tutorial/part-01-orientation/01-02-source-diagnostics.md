# 01-02. 소스와 진단을 읽는 법

## 1. 상태와 읽는 법

> **상태:** `CURRENT_DESIGN_PRODUCT_NOT_RUN`  
> **제품 증거:** `15/15 NOT_RUN`

이 장은 현행 source role, lossless CST, AST, typed HIR 경계와 진단
우선순위를 설명한다. 실제 Rust lexer/parser/checker 실행은 주장하지
않는다.

## 2. 학습 목표

- source가 scanner, CST, AST, HIR을 거치는 목적을 설명한다.
- parse 오류와 type/checker 오류를 구분한다.
- 첫 실패 단계가 뒤 단계의 추측으로 가려지면 안 되는 이유를 이해한다.
- diagnostic ID와 source span, 대안을 함께 읽는다.

## 3. 선수 지식

[01-01](01-01-language-status.md)의 상태 구분을 이해해야 한다. 타입과
함수의 세부 문법은 아직 몰라도 된다.

## 4. 문제에서 출발하기

컴파일러가 오류를 여러 개 한꺼번에 추측하면 초보자는 무엇부터
고쳐야 할지 알기 어렵다. 예를 들어 타입 선언의 가시성이 빠졌는데,
그 뒤의 이름 해석이나 생성자 오류부터 보여 주면 원인을 거꾸로
찾게 된다. Deeplus 진단은 가장 먼저 닫혀야 할 owner와 조건을 우선한다.

## 5. 핵심 모델

source 처리의 직관적인 단계는 다음과 같다.

```text
Unicode source
  -> scanner token + trivia
  -> lossless CST
  -> normalized AST
  -> name/type/ownership/effect checking
  -> Verified<CanonicalHirH1>
  -> MIR capability receipt가 있을 때만 ExecutableHirH1
```

lossless CST는 원래 철자와 주석, 줄바꿈을 보존한다.
AST는 구조 owner를 정하지만 아직 모든 identity를 닫지 않는다. HIR
경계는 이름, 타입, callable, witness, ownership, effect, error,
cancellation, cleanup 결정을 모두 닫아야 한다. unresolved 후보는
canonical HIR에 들어갈 수 없다.

## 6. 단계별 예제

다음 타입 alias는 명시적 가시성과 닫힌 범위를 가진다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN -->
```deeplus
private type Port = 0..65_535

private def#pure isDefault(port: Port) -> Bool
= {
    return port == 80
}
```

scanner는 단어와 숫자를 나누고, parser는 `TypeAliasDecl`과 함수 구조를
만든다. checker는 `Port`가 정적 범위 alias인지, `port == 80`이 exact
domain 비교인지 확인한다. 허용된다면 HIR은 alias identity와 함수
책임을 보존한다.

다음 선언은 parser가 declaration 구조를 만들 수 있지만 checker
admission 전에 멈춘다.

<!-- deeplus-example: illustrative; surface: CURRENT; product: NOT_RUN; expected: REJECT; diagnostic-family: TYPE_DECL_VISIBILITY_* -->
```deeplus
class Session {
}
```

Class는 명시적 `public`, `common`, `private` 중 하나가 필요한 아홉 type
owner에 속한다. primary 진단은 `TYPE_DECL_VISIBILITY_REQUIRED`이며,
admitted HIR type node와 API digest entry는 모두 0이다. 뒤 단계가
임의로 `private`를 붙여 생성자나 멤버 검사를 계속해서는 안 된다.

### 판정 trace, 미니 사례와 흔한 오해

진단을 읽을 때는 source span에서 거꾸로 추측하지 말고 순방향 trace를
적는다. token attachment가 유효한지, production owner가 완성되는지,
이름이 resolve되는지, type과 responsibility가 닫히는지 차례로 본다.
visibility가 빠진 top-level type은 scanner가 모든 token을 읽고 parser도
declaration 구조를 만들 수 있다. 거부 지점은 type-producing owner
admission이므로 “문법을 전혀 읽지 못했다”라고 설명하면 고칠 위치를
잘못 안내한다.

미니 사례에서 `value as ? Port`처럼 붙어야 할 token을 띄운 경우에는
checker가 refinement를 검토하기 전에 attachment/parse 단계가 막힌다.
반면 `let port: Port = raw`는 구조가 완성된 뒤 proof가 없어 거부된다.
가장 흔한 오해는 첫 diagnostic이 프로그램의 모든 문제를 설명한다고
생각하는 것이다. 한 항목을 고친 뒤에는 같은 trace를 처음부터 다시
적용해야 다음 단계의 오류를 정확히 찾을 수 있다.

## 7. 허용·거부·경계 사례

- **어휘 거부:** 잘못된 literal delimiter나 token 연쇄.
- **구조 거부:** 닫는 delimiter, owner 또는 source role이 맞지 않음.
- **정적 거부:** 이름 없음, 타입 불일치, ownership/effect 의무 위반.
- **문법 경계:** 문법에 없는 source는 Stable AST/HIR로 바뀌지 않음.
- **runtime 경계:** 정적 거부 source는 runtime failure나 MIR event를
  만들지 않음.

하나의 source에 문제가 여럿이면 보통 lexical/parser owner, source role,
이름, call shape, 타입, ownership/effect 순으로 먼저 적용 가능한
진단을 고른다.

## 8. 다른 기능과의 연결

진단은 문법만의 기능이 아니다. 함수 호출은 label/channel 오류를 generic
추론보다 먼저 보고, closed Union `is`는 comparison-chain 위반을 일반
타입 오류보다 먼저 보고한다. cleanup이나 actor send도 commit 전·후
책임을 구분해야 정확한 진단을 낼 수 있다.

## 9. Deeplus다운 작성 관례

- 오류 메시지의 첫 줄만 보지 말고 source span, owner, 제시된 대안을
  함께 읽는다.
- 한 번에 첫 primary diagnostic 하나를 고친 뒤 다시 검사한다.
- 진단의 제안을 자동 rewrite 권위로 오해하지 않는다.
- “컴파일러가 알아서 추측할 것”이라는 설명 대신 어떤 정적 identity가
  부족한지 적는다.

## 10. 연습 문제

1. **따라 하기:** `private type Count = 0..100`을 적고 scanner, parser,
   checker가 각각 알아야 할 정보를 한 가지씩 적는다.
2. **빈칸 완성:** `class Missing {}`가 거부될 때 canonical HIR type node
   수는 `___`이다.
3. **스스로 설계하기:** 이름 없음과 타입 불일치가 동시에 보이는 호출을
   가정하고 어느 진단이 먼저여야 하는지, 그 이유를 설명하라.

## 11. 빠른 복습

- CST는 원 source, trivia와 delimiter 구조를 보존한다.
- AST는 구조 owner를, HIR은 닫힌 정적 identity와 책임을 보존한다.
- 정적 거부 source는 MIR/runtime event를 만들지 않는다.
- 첫 실패 단계가 뒤 단계의 추측보다 우선한다.
- diagnostic은 제품 실행 영수증이 아니라 정적 설계 계약일 수 있다.

## 12. 정본 근거와 다음 장

- [통합 EBNF](../../../spec/grammar/deeplus.ebnf)
- [진단 catalog](../../../spec/diagnostics/catalog)
- [name/type/call 판정](../../grammar-reference/17-name-resolution-type-inference-and-calls.md)
- [source에서 HIR/MIR로](../../grammar-reference/18-evaluation-ownership-mir-and-backends.md)
- [Prelude와 진단](../../grammar-reference/19-prelude-providers-diagnostics-and-conformance.md)

다음은 [첫 설계 정적 프로그램](01-03-first-design-static-program.md)을
작성하며 이 읽기 순서를 적용한다.
