# Deeplus R59 Pattern Dynamic-Lowering Trace Closure R1

## Decision

`APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE`

R59 is a local-only normative and documentation clarification at baseline
`fb3e98888f947d0e7b45f713efe3b017a55c976a`. It closes exactly three
`DYNAMIC_LOWERING` trace cells without changing Grammar, source syntax,
feature status, dependency edges, source activation, or product support.

## Exact transition scope

Only these cells transition from `APPLICABLE_BLOCKED_BY_GAP` to
`BOUND_DIRECT`:

1. `or_alias_pattern/DYNAMIC_LOWERING`;
2. `pattern_binding_control_family/DYNAMIC_LOWERING`;
3. `pattern_decomposition/DYNAMIC_LOWERING`.

No other stage cell in those rows transitions. The ledger counts therefore
change exactly as follows:

| disposition | predecessor | R59 |
|---|---:|---:|
| direct | 2,447 | 2,450 |
| delegated | 3 | 3 |
| not applicable | 502 | 502 |
| blocked | 1,269 | 1,266 |

## PatternAttempt contract

Each refutable Pattern owner lowers as one logical `PatternAttempt`. Its subject
is evaluated once. Structural decomposition is a pure nonconsuming probe, and
its provisional binders are read-only and nonescaping. After structural
success, zero or one pure Bool guard is evaluated exactly once. Only final
guarded success performs exactly one final logical commit.

A child pattern-row `BINDING_COMMIT` entry is a compositional commit
requirement. Every such requirement collapses into the single top-level
`PatternAttempt` commit; child rows do not authorize nested or multiple
executable commits.

An Or probe tries branches in source order and selects the first structural
success. Every branch must expose the exact same binder interface. There is no
retry or backtracking, including after a false owner guard. An Alias probe
preserves the same subject identity, performs no clone, and stages a borrow
requirement; the actual loan is acquired only by the final commit.

A structural failure or false guard publishes no bindings, moves, loans,
views, or authority. For `if let`, `while let`, and `for let`, the respective
dispositions are the false branch, loop exit, and current-candidate skip.

## Delegation and exact exclusions

`OR_PATTERN_BINDINGS_INCONSISTENT` and Alias ownership conflict remain
delegated to `pattern_match_ownership_split`. Its trace row remains unchanged.
R59 also does not transition any cell for the following ten Stable-design
reverse dependents of `pattern_decomposition`:

1. `assertive_pattern_binding`;
2. `irrefutable_parameter_entry_pattern`;
3. `local_group_tuple_assignment`;
4. `pattern_condition_chain`;
5. `pin_range_relational_pattern`;
6. `refutable_catch_pattern`;
7. `sequence_positional_rest_pattern`;
8. `structured_record_map_pattern`;
9. `transparent_nominal_named_enum_pattern`;
10. `tuple_bare_product_surface`.

These exclusions prevent inference-based closure of ownership analysis,
diagnostics, reverse-dependent features, tests, or product behavior.

## Preserved governance

- semantic P0: `0`;
- feature P1: exactly `22 OPEN`;
- M13 actions: exactly `4 OPEN`;
- product execution: `NOT_RUN`;
- source activation: none;
- Grammar or source-syntax change: none;
- product implementation or conformance claim: none;
- GitHub publication: `SUSPENDED`.

No generator execution, HIR/MIR registry edit, catalog expansion, source
activation, product claim, staging, commit, or GitHub mutation is authorized by
this decision.
