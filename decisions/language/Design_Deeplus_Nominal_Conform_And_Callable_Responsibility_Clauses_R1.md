# Deeplus nominal conform and callable responsibility clauses R1

Status: `CURRENT_DESIGN_STATIC`

Revision: `r51f3-current-trait-operator-refinement-r1`

Product execution: `15/15 NOT_RUN`

## Decision

Two related surface inconsistencies are resolved without changing the existing
Trait identity, ErrorSet, or EffectRow semantics.

### Nominal conformance group

`conform Trait { ... }` is a lexical witness group owned by an enclosing Class
or Enum:

```deeplus
public class User
conforms Display {
    +let name: String

    conform Display {
        def display.() -> String = {
            return self.name
        }
    }
}
```

The enclosing nominal declaration is the target. Its header must already carry
the matching `conforms Trait` relation. Consequently:

- no `for Type` clause exists;
- a top-level `conform` block is rejected;
- a block whose Trait does not match a header relation is rejected;
- requirement names inside the block are unqualified;
- external evidence remains the separate
  `type Target conforms Trait { ... }` form.

Lexical grouping changes no `ConformanceId`, `TraitWitnessId`, coherence,
visibility, overlap, or runtime-search rule.

### Callable responsibility clauses

Callable declarations use one repeated clause per declared responsibility,
matching the repeated-clause style of nominal `conforms` relations:

```deeplus
public def loadReport(path: Path) -> Report
    throws IOError
    throws DecodeError
    effects io
    effects decode
= {
    return decodeReport(read(path))
}
```

All `throws` clauses precede all `effects` clauses. `throws Never` and
`effects {}` remain the explicit empty spellings. A bar-composed callable
throws list and a nonempty effect-set callable list are rejected. Type-level
ErrorSet and EffectRow algebra remain unchanged, so `E1 | E2` and
`Eff | {state, io}` are still admitted in their type-level owners.

Lossless CST retains clause order and spans. AST, HIR, API identity, and MIR
receive duplicate-free normalized ErrorSet and EffectRow identities. Source
order is diagnostic and formatting information only; a repeated normalized
term is rejected.

## Guards

- Existing concise omission remains `PREVIEW_DESIGN_NONACTIVATABLE`; this
  decision does not promote it.
- No local/runtime conformance, specialization, alternate provider route, or
  child-local witness replacement is introduced.
- Semantic P0 remains `0`.
- The exact existing feature-P1 set remains `22 OPEN`.
- Product lanes remain `15/15 NOT_RUN`.
- This design-static materialization claims no parser, checker, runtime,
  formatter, LSP, or product execution.
