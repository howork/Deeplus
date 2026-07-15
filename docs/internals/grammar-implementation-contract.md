# Deeplus Grammar 0.1.2 R51f3 — Implementation Contract

The exact Grammar is `spec/grammar/deeplus.ebnf` and the contextual owner model is `spec/frontend/frontend-model.json`. This document is a concise handoff, not a second grammar.

- Rust implements the scanner, handwritten recursive-descent owners, Pratt entries, lossless CST, AST/HIR, and checker.
- Stable roots consume EOF.
- Named-rest parameter/type residue uses attached `***`; named unfold uses prefix `**`.
- `**` remains an independent linear-product operator where the Pratt table admits it.
- Recovery produces diagnostics and never a current AST/MIR node.
- Deeplus MIR is the semantic authority; xVM and LLVM are projections.
- Every product lane remains `NOT_RUN` without a target-baseline receipt.

R51f closure: the scanner exports no regex-literal token or REGEX mode; the contextual callable table contains no tailrec role. Map-key and List-union rules are semantic and must not be invented by the parser.
