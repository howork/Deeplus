# Deeplus Grammar 0.1.2 R51f3 구현 계약

정확한 구조 문법 정본은 `spec/grammar/deeplus.dpg`, 닫힌 parser context
정본은 `spec/grammar/deeplus.parser-contexts.json`이다. scanner, Pratt,
CST/AST 계약은 `spec/frontend/frontend-model.json`이 소유한다. 이 문서는
구현자가 이 책임 경계를 임의로 다시 설계하지 않도록 하는 구현 요약이다.
`spec/grammar/deeplus.ebnf`는 R77 표면을 빠짐없이 대조하기 위한
비권위 surface census이며 새 parser의 생성 문법이 아니다.

## 1. 닫힌 입력 계약

- source carrier는 parse 전에 `library | executable | script` 역할과
  `stable | preview` activation profile을 각각 하나씩 고정한다.
- 이 두 축은 여섯 source root 중 하나를 선택한다. root를 차례로 parse해
  성공하는 것을 선택하는 방식은 금지한다.
- Preview gate는 이미 선택된 Preview profile을 검증할 뿐 역할·profile·
  root를 바꾸지 않는다. 실패는 feature와 canonical AST를 하나도
  commit하지 않는다.
- source root는 EOF까지 소비하며 receipt는 input, Grammar, role, profile,
  root와 boundary 결정의 identity를 기록한다.

## 2. Grammar와 lossless CST

DPG는 282개 rule family와 303개 context-specialized clause로 구조를
기술한다. 기존 EBNF의 656개 surface-census production은
`spec/contracts/grammar-production-disposition-registry-r1.json`에 정확히 한
번씩 남아 CST/AST 책임 crosswalk로 쓰인다. 이 656이라는 수는 새 DPG를
다시 팽창시키라는 요구가 아니다. disposition은 CST-only, AST-node,
normalization, external parser entry 중 하나이며 recovery residue는 별도의
reject-before-AST 종류다.

Lossless CST는 token, trivia, delimiter, recovery residue와 source bytes를
순서대로 정확히 한 번 보존한다. AST normalization은 선언된 rule과
receipt에 의해서만 수행한다. recovery/missing/unexpected/skipped/error
node는 canonical AST 또는 HIR로 나갈 수 없다.

## 3. parser와 Pratt 경계

Handwritten recursive descent parser는 declaration, statement, delimiter와
contextual boundary를 소유한다. Pratt goal은 정확히 `EXPRESSION`,
`PREDICATE`, `SLICE_INDEX`, `TYPE`, `NON_FUNCTION_TYPE`, `UNIT`이다. 각
goal은 닫힌 parselet registry와 stop set을 사용한다. `~`와 `:~`는 rank
15의 structured message-call led parselet이며 generic postfix가 아니다.

Statement boundary와 match-arm separator의 newline 판정은 transaction으로
probe한다. 실패한 probe는 token을 소비하지 않고 diagnostic을 만들지
않는다. 열린 delimiter나 필수 child는 newline보다 먼저 계속한다.

## 4. scanner와 String

Scanner는 complete-token/lexical-goal registry와 명시된 priority를 따른다.
실패한 speculative token probe는 byte와 diagnostic을 commit하지 않는다.
Shorthand interpolation은 닫힌 scanner state machine으로 token boundary만
결정하며 이름과 타입 의미는 parser/checker가 소유한다.

Multiline String은 하나의 atomic scanner-stream envelope다. payload leaf는
source bytes를 정확히 한 번 partition한다. dedent는 비어 있지 않은
content line indentation의 byte longest common prefix이며 tab과 space는
다르다. closer indentation은 metadata일 뿐 dedent 입력이 아니다.

## 5. recovery와 canonical seal

`STRICT_CANONICAL`과 `ANALYSIS_RECOVERY`는 같은 lossless recovery CST와
bounded progress law를 사용한다. recovery taint는 containing owner로
전파된다. 변경된 입력을 새로 parse할 때만 제거할 수 있으며 formatter나
checker가 지울 수 없다. analysis-only tree는 editor API에만 쓰고 API
digest, canonical HIR, MIR, 실행 또는 conformance evidence에 포함하지
않는다.

## 6. 증거 경계

이 계약과 fixture의 정적 검증은 설계 정합성 증거다. production Rust
scanner/parser/checker, formatter/LSP, MIR/xVM/Cranelift의 target-bound 실행
receipt가 없으면 해당 product lane은 `NOT_RUN`이다. R12–R19 정본 투영은
새 source spelling이나 final diagnostic ID를 만들지 않는다.
