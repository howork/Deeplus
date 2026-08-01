# Design_ Deeplus R19 Source Role, Activation Profile, and Gate Decision R1

## Status

`APPROVED_CANONICAL_TARGET_PENDING_PUBLICATION`

This bounded R19 decision closes the design ambiguity tracked as
`IR-FE-P1-036`. The repository projection is prepared locally against commit
`88bbc4fe6217fc1b0e8d5db05379ef046eb07abe`; publication and product execution
are separate gates.

## Closed carrier domains

- `source_role` is exactly `library | executable | script`.
- `activation_profile` is exactly lowercase `stable | preview`.
- The carrier supplies both axes before parsing. A parser must not try several
  roots to infer either value.
- The Cartesian product selects exactly six roots:
  `LibrarySourceFile`, `ExecutableSourceFile`, `ScriptSourceFile`,
  `PreviewLibrarySourceFile`, `PreviewExecutableSourceFile`, and
  `PreviewScriptSourceFile`.
- HIR normalizes `stable` to `CURRENT` and `preview` to
  `EXPLICIT_PREVIEW`. Values such as `preview_library` are not source roles.

## Gate contract

`spec/features/gates.json` is the exhaustive feature-ID-keyed gate projection.
It contains exactly the two FFI routes and the checker-owned NumericArray
elementwise-power route. A gate verifies an already selected Preview profile;
it cannot change the source role or activation profile.

Validation is ordered as follows: carrier/root agreement, placement, left-to-
right unknown/nonactivatable/duplicate ID checks, dependency closure, atomic
commit, HIR-profile normalization, and route ownership. Every failure leaves
zero activated features and zero canonical source-unit AST.

Grammar routes and checker semantic routes remain distinct. NumericArray power
continues to parse through `PrattExpr`; its feature gate controls checker
admission rather than introducing a separate parser production.

## Diagnostics and compatibility

The existing Preview-gate diagnostics are reused. Invalid carrier profile
values or stable/preview target disagreement use
`PACKAGE_MODULE_SOURCE_GRAPH_INVALID`. No new final diagnostic ID or syntax is
introduced. Existing role-specific top-level and entry-count rules retain their
ordered diagnostics after carrier validation.

The active gate projection is exactly `3/3`. Its separate `nonactivatable`
projection is repaired to the exact 115 catalog entries: obsolete
`custom_operator` is removed and the twelve missing Preview Design IDs are
added.

## Frozen acceptance oracles

- `IR-R3-GAP-09-P` →
  `ACCEPT_SAME_ROLE_PREVIEW_PROFILE_AND_GATE_CLOSURE`
- `IR-R3-GAP-09-B` → `REJECT_ATOMIC_GATE_DEPENDENCY`
- `IR-R3-GAP-09-N` → `REJECT_GATE_PROJECTION_DRIFT`

## Evidence boundary

- design-static canonical projection: `PREPARED`
- production parser/checker, formatter/LSP, runtime, and backend execution:
  `NOT_RUN`
- product lanes: `15/15 NOT_RUN`
- semantic P0: `0`
- existing feature P1 set: unchanged
- new syntax, diagnostic ID, or product-support claim: `0`
