# Deeplus Trait Conformance implementation handoff R107

Status: `LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF`

Baseline predecessor: `750885a2e0b552d7efdd58ef4ee996ad3d02bc48`

## Decision

R107 turns the already accepted TC-R001..R016 design into one deterministic
compiler handoff. It does not add syntax, activate a successor route, close any
feature P1, or claim a parser/checker/MIR/runtime/tooling execution receipt.

The checker performs one closed sequence:

1. commit one admitted source route and normalized AST owner;
2. normalize target, Trait, binders, substitutions and requirement slots;
3. intern the ground conformance and enforce locality, overlap and termination;
4. resolve parent evidence, requirements, associated bindings and visibility;
5. admit only direct, current lowercase `via`, or a registered bodyless
   `by auto` policy;
6. seal the complete identity vector and responsibility residue in typed HIR;
7. lower only already selected evidence. MIR, xVM and runtime perform no
   provider, registry, source-order, specialization, fallback or witness search.

The exact machine contract is
`spec/contracts/trait-conformance-implementation-handoff-r107.json`. Its
fixture index gives one positive, boundary and reject oracle for every
`TCC-P1-002..008`. Static validation proves the completeness and consistency of
the handoff only. The seven actions remain `OPEN`, execution remains
`OPEN_NOT_RUN`, and all product lanes remain `NOT_RUN`.

## Deliberate fences

- no local, structural or runtime conformance;
- no uppercase `VIA` or `AUTO` route;
- no specialization, source/import priority or child-local parent witness;
- no user-defined auto-policy language;
- no runtime witness value or runtime conformance lookup;
- no formatter/LSP/product support claim without a target-bound receipt.

## Implementation order

`TCC-P1-002 -> {TCC-P1-003, TCC-P1-005} -> TCC-P1-004 -> TCC-P1-006 -> TCC-P1-007 -> TCC-P1-008`

The production implementation must execute the bound corpus and attach the
resulting receipt before any action can be closed. R107 is therefore sufficient
to start implementation, but not evidence that implementation exists.
