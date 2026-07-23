# Deeplus Grammar 0.1.2 R51f3 구현 계약

정확한 문법 정본은 `spec/grammar/deeplus.ebnf`, 문맥별 owner 모델은
`spec/frontend/frontend-model.json`이다. 독자를 위한 한국어 설명과
역색인은 `docs/grammar-reference/README.md`에서 시작한다. 이 문서는
구현 handoff 요약이며 두 번째 문법 정본이 아니다.

- Rust 구현은 scanner, handwritten recursive-descent owner, Pratt entry,
  lossless CST, AST/HIR, checker를 담당한다.
- Stable source root는 반드시 EOF까지 소비한다.
- named-rest parameter/type residue는 붙여 쓴 `***`, named unfold는
  prefix `**`를 사용한다.
- `**`는 Pratt 표가 허용하는 위치에서 별도의 linear-product
  operator이기도 하다.
- Recovery는 진단만 만들며 current AST/HIR/MIR node를 만들지 않는다.
- 정확한 production 수는 LEXICAL 89, STABLE 443, PREVIEW 13, RECOVERY
  15로 총 560개이며 generator가 frontend model과의 일치를 검사한다.
- Deeplus MIR가 의미 정본이고 xVM과 LLVM은 그 projection이다.
- target-bound receipt가 없으면 모든 product lane은 `NOT_RUN`이다.

R51f closure에서 scanner는 regex-literal token이나 REGEX mode를 내보내지
않고, callable context table에는 tailrec role이 없다. Map key와 List
Union 규칙은 의미 규칙이므로 parser가 임의로 발명해서는 안 된다.
