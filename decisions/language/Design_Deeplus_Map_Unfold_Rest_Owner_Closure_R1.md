# Deeplus Map Unfold/Rest Owner Closure R1

## 0. Decision identity

```text
decision_id: DSGN-CURRENT-MAP-UNFOLD-REST-OWNER-CLOSURE-R1
repository: howork/Deeplus
baseline_commit: 10e64f492f0529610673846139afcf0d95175663
local_predecessor_commit: 6f91a01791d7e7c9431605b112b3cda282328ed6
authority: Codex Design_ under the user's delegated language-design authority
status: LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED
gap_id: PREIMPL-P0-004C
semantic_p0_after_closure: 0
feature_p1: 22_OPEN_UNCHANGED
product_lanes: 15/15_NOT_RUN
```

## 1. Decision

Deeplus uses `*` for runtime structural expansion and `**` only for a finite,
statically named Record/NamedPack channel. The owning parser context seals the
meaning before type checking:

| Owner | Surface | CST/AST | Meaning |
|---|---|---|---|
| positional call/list/mutable-list/comprehension source | `*expr` | `PositionalUnfold` | finite runtime positional sequence |
| Map literal entry | `*expr` | `MapUnfold` | immutable `Map<K,V>` runtime entry source |
| Map Pattern entry | `*name` / `*_` | `MapRestPattern` | dynamic keyed residual Map |
| call or Record materialization | `**expr` | `NamedUnfold` | finite static label row |

`*` is not a general prefix operator. The owner commits the node; expected
type, overload resolution, and runtime shape do not choose the channel.

The former Map-specific `#map{**base}` and `#map{value:key, ..rest}` spellings
have no compatibility alias because Deeplus has no production implementation
or source-compatibility obligation yet. They are rejected with the existing
Map spelling diagnostic family. Record and NamedPack `**` and List suffix rest
`name..` remain unchanged.

## 2. Map literal and comprehension

`#map{directKey: directValue, *base}` builds one `MapLiteralPlan`. Direct
entries and unfolded Map sources evaluate exactly once from left to right.
Every entry has the same exact normalized `K` and `V`; later equal keys replace
earlier values, displaced owners clean exactly once, and precommit failure
publishes no partial Map and cleans acquired temporaries in reverse order.

A Map comprehension head is exactly `keyExpr: valueExpr`. An unfold-headed
form such as `#map{*base for item in source}` is rejected. This avoids inventing
per-iteration unfold, duplicate-key, evaluation, and cleanup rules.

## 3. Map Pattern

Map Patterns retain destination-first `Pattern: literal-or-pinned-key` entries.
They are exact by default. Exactly one `*_` may ignore additional keys or one
`*name` may capture the exact residual `Map<K,V>`. The residual publishes only
at whole-pattern commit, never on a failed key probe, child Pattern, guard, or
ownership acquisition. It is not a positional rest and not a static NamedPack.

## 4. Responsibility boundary

- scanner: emits the ordinary `STAR` or `DOUBLE_STAR` token and preserves bytes;
- DPG/ParserContext: commits `*`/`**` by the enclosing entry owner;
- CST: preserves the exact marker and source range;
- AST: emits exactly one of `PositionalUnfold`, `MapUnfold`, `MapRestPattern`,
  or `NamedUnfold`;
- checker: verifies exact Map domains, key descriptor, residual legality, and
  owner admission;
- HIR/MIR: receives an already sealed Map literal/pattern plan and performs no
  channel selection;
- formatter/LSP: emits the canonical owner-specific spelling and never rewrites
  between runtime Map and static-named channels.

## 5. Evidence boundary

The local design/static validators prove contract, grammar, frontend model,
diagnostic, fixture, and documentation parity. They do not prove production
scanner, parser, checker, HIR/MIR, formatter, LSP, xVM, runtime, or backend
execution. All product lanes remain `NOT_RUN`; GitHub publication is not part
of this cluster.
