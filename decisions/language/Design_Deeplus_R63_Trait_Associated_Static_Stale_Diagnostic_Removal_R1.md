# R63 Trait-Associated Static Stale Diagnostic Removal

Status: `LOCAL_APPROVED_CANDIDATE`

Gap: `IR-DIAG-P2-055`

Canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`

Local predecessor: `eec3b840176e8b401cabac1fc32ab61e7d0ace49`

Scope: diagnostic-registry parity for Trait-qualified associated static
selection. This decision authorizes a later bounded removal/rebind candidate; it
does not itself modify the companion contract, fixture corpus, diagnostic
catalog, predicate registry, relation registry, implementation trace, canonical
source, or GitHub.

## Decision

`TRAIT_ASSOCIATED_STATIC_AMBIGUOUS` is stale and unreachable under the current
lookup contract. It must not be registered as a diagnostic.

`<T as Trait>::item` fixes one explicitly named Trait domain. Nominal type-side,
named-extension, Trait-associated-static, and explicit-runtime-value lookup
domains never form a shared candidate list. Consequently, the simultaneous
visibility of names in different domains cannot create Trait-associated-static
ambiguity.

An unqualified `T::item` that attempts Trait-associated selection is rejected by
the existing `TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION` diagnostic.
For an explicitly qualified `<T as Trait>::item`, witness resolution occurs
before associated-item lookup. More than one normalized visible witness is
therefore rejected by `WitnessResolution` with the existing
`TRAIT_AMBIGUOUS_IMPORTED_WITNESS` diagnostic. Overlapping conformance
declarations remain governed by the existing witness-coherence diagnostics.
There is no later, distinct ambiguity condition for
`TraitAssociatedStaticSelectionAdmitted`.

## Bounded repair disposition

The later repair is limited to these three active-artifact changes:

1. Remove `TRAIT_ASSOCIATED_STATIC_AMBIGUOUS` from
   `spec/contracts/companion-capability-coherence.json` `diagnostic_families`.
2. Rebind `CCC-R1-NEG-009` to an explicit `<T as Factory>::default` selection
   with two normalized visible witness candidates. Its expected diagnostic is
   `TRAIT_AMBIGUOUS_IMPORTED_WITNESS`, selected by `WitnessResolution` before
   associated-item lookup or lowering.
3. Retain the merged-domain structural mutation `CCC-R1-MUT-022`, but set its
   `diagnostic_family_or_null` to `null`. Killing an invalid merged-domain model
   is a structural fixture oracle and does not emit a source diagnostic.

The repair introduces no source surface or alias. It adds no diagnostic row,
checker predicate, diagnostic relation, grammar production, AST/HIR identity,
MIR operation, runtime mechanism, activation, feature status, implementation
trace transition, or product-support claim.

## Diagnostic selection order

1. An unqualified Trait-associated intent stops with
   `TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION`; no witness search
   occurs.
2. Explicit `<T as Trait>::item` runs `WitnessResolution`. Zero candidates use
   the existing missing-witness diagnostic, more than one use
   `TRAIT_AMBIGUOUS_IMPORTED_WITNESS`, and exactly one yields sealed evidence.
3. With exactly one witness, associated-item lookup may select the existing
   item-not-found, item-kind, value-profile, runtime-lookup, or identity-residue
   diagnostic according to the existing deterministic checker/verifier phases.

## Exact acceptance criteria

1. **R63-AC-001 — companion family removal:** the active companion contract has
   zero `TRAIT_ASSOCIATED_STATIC_AMBIGUOUS` diagnostic-family entries and gains
   no replacement diagnostic ID.
2. **R63-AC-002 — NEG-009 rebind:** `CCC-R1-NEG-009` uses the existing explicit
   `<T as Factory>::default` surface, records two normalized witness candidates,
   expects `TRAIT_AMBIGUOUS_IMPORTED_WITNESS`, and records zero associated-item
   lookup and lowering after witness rejection.
3. **R63-AC-003 — MUT-022 structural oracle:** `CCC-R1-MUT-022` retains the
   four-domain-merger mutation and `MUTANT_KILLED` result while
   `diagnostic_family_or_null` is exactly `null`.
4. **R63-AC-004 — catalog uniqueness:** the active diagnostic catalog contains
   zero rows for `TRAIT_ASSOCIATED_STATIC_AMBIGUOUS` and exactly one active row
   each for `TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION` and
   `TRAIT_AMBIGUOUS_IMPORTED_WITNESS`.
5. **R63-AC-005 — predicate/relation uniqueness:** active predicate and relation
   registries contain zero references to `TRAIT_ASSOCIATED_STATIC_AMBIGUOUS`;
   `WitnessResolution` remains the unique owner of
   `TRAIT_AMBIGUOUS_IMPORTED_WITNESS`, and
   `TraitAssociatedStaticSelectionAdmitted` retains its existing six diagnostic
   families without a new branch.
6. **R63-AC-006 — fixture cardinality:** the companion fixture remains exactly
   28 cases partitioned as 7 positive, 7 negative, 7 boundary, and 7 mutation
   cases; fixture IDs and all unrelated cases remain unchanged.
7. **R63-AC-007 — language and machine fence:** new source spellings, grammar
   productions, AST identities, HIR identities, MIR operations or terminators,
   runtime mechanisms, activation triggers, fallback paths, and provider or
   order winners are all zero.
8. **R63-AC-008 — trace fence:** no implementation-target feature, stage, or
   outcome cell changes disposition; the R62 dynamic-lowering binding remains
   direct, and R63 creates zero implementation-trace transitions.
9. **R63-AC-009 — governance and evidence honesty:** semantic P0 remains `0`,
   feature P1 remains exactly `22 OPEN`, M13 remains `4 OPEN`, product lanes
   remain `15/15 NOT_RUN`, product execution receipts remain absent, canonical
   source mutation is `0`, and GitHub mutation is `0`.
10. **R63-AC-010 — historical evidence preservation:** R62 decision and closure
    evidence remain immutable provenance describing the then-open follow-up;
    R63 supersedes only the active interpretation of the stale spelling, and no
    historical artifact is deleted, rewritten, or treated as an active
    diagnostic registry entry.

## Governance fence

- semantic P0: `0`
- feature P1: `22 OPEN`, unchanged
- M13 actions: `4 OPEN`, unchanged
- product lanes: `15/15_NOT_RUN`
- implementation-target trace transitions: `0`
- canonical source mutation: `0`
- GitHub mutation: `0`
- production implementation: `NOT_AUTHORIZED`
