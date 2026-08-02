# Deeplus Closure Capture Plan R1

Status: `STABLE_DESIGN_STATIC_CANDIDATE`
Gap: `IR-OWN-P1-019`
Baseline: `howork/Deeplus main` at
`4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`
Dependency: R30 local evidence commit
`50ad91fddc8111104fb2adc1f1ae74b21ddef3c2` (`IR-OWN-P1-023`)
Product support: `15/15 NOT_RUN`
GitHub publication: `SUSPENDED`

## Decision

An explicit capture list denotes one sealed, source-ordered environment
construction plan. It is not an unordered set of names and it is not a hint
that a backend may reinterpret. The existing capture surface is sufficient;
R1 adds no capture mode and no grammar production.

The capture modes are:

- reference captures: `borrow`, `inout`, `move`, `copy`, `clone`, `deep`, and
  `once`;
- initializer captures: `let name = expression` and
  `var name = expression`;
- a bare capture item is exactly `borrow`, never an inferred `copy`;
- `deep` remains Preview Design and nonactivatable;
- a capture-level `once` requires an independently explicit callable `#once`.

The capture list remains physically attached to its closure owner. A line break
between the closing `]` and the owned closure surface is rejected. This is a
lexical attachment rule, not a new token or production.

## Identity and scope

The plan identity is `CapturePlanId(ClosureOwnerId, CreationPointId)`. Every
field has the stable body-local identity
`CaptureFieldId(CapturePlanId, source_ordinal, canonical_name)`. Source
ordinals are zero-based, contiguous, and preserve exact written order.

Reference captures bind one resolved reference and normalized source place.
Initializer captures own one initializer expression and one result evaluation.
All initializers are resolved and evaluated in the enclosing scope; no capture
binder is visible to its own initializer or to a later initializer. The
binders become visible together only in the closure body. Duplicate field
names and duplicate normalized source-place acquisition are rejected before
any capture expression is evaluated.

An explicit capture of a place removes the same-place lexical residue. A
proven read-only dependency on a different ancestor place may coexist. A
lexical dependency is not a capture event and does not create a snapshot,
owner transfer, loan, or cleanup entry.

## Static admission

Admission is applied before environment construction:

| Mode | Minimum current obligation |
|---|---|
| `borrow` | nonescaping; exact shared loan bounded by the owner region |
| `inout` | `#scoped#mut`, nonescaping, nonsuspending, exact exclusive loan |
| `move` | one live owned place and one move reservation |
| `copy` | exact R30 `CopyValue` responsibility evidence; null Trait witness |
| `clone` | one exact selected `Clone` witness and visible normalized error/effect residue |
| `deep` | reject `FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE` |
| `once` | one live owned place plus explicit callable `#once` |
| initializer `let` | evaluate one enclosing-scope expression into an immutable field |
| initializer `var` | initializer `let` obligations plus callable `#mut` |

The bounded concur-local async profile admits only an empty environment or an
explicit reusable `copy`-only plan. Generator borrow/inout capture and mutable
capture in a pure callable remain rejected by their existing active
diagnostics. R1 invents no new diagnostic ID.

## Construction transaction

The checker and lowering apply this deterministic algorithm:

1. Resolve every binder, source place, type, owner, region, evidence, witness,
   error/effect row, and cleanup disposition without evaluating a capture
   item.
2. Apply duplicate, scope, owner, callable-profile, escape, suspension, and
   isolation gates.
3. Begin one environment builder.
4. Prepare fields from source ordinal zero upward, evaluating each source or
   initializer exactly once. Borrow/inout begin exact loans; move/once reserve
   a move; copy binds exact responsibility evidence; clone invokes the selected
   witness; initializer captures stage their single result.
5. If preparation fails, clean only the prepared prefix in strict reverse
   acquisition order: end live loans, cancel uncommitted move reservations,
   and clean staged owned values exactly once. External effects already
   observed during an initializer or clone call are not claimed to be undone.
6. After all failure-prone work succeeds, commit the complete environment once.
   In the same nonbranching and nonsuspending interval, perform infallible
   closure creation. No partial environment or closure is published.

Normal destruction cleans the remaining live owned fields in reverse field
order exactly once.

## HIR, MIR, runtime, and API boundary

HIR represents `ReferenceCapture` and `InitializerCapture` as a closed tagged
sum and preserves field identity, source ordinal, normalized type, residence,
capture-list state, closed-ancestor assertion, and lexical dependencies. The
R30 promotion dependency supplies the final canonical `ResponsibilityRuleId`
and `ResponsibilityEvidenceId` domains; R31 does not import or duplicate R30
candidate bytes.

MIR binds one `closure_environment_plan_table` row to the exact HIR plan. No
new MIR operation kind is needed. Lowering reuses builder, move, loan, cleanup,
`CHECKED`/`LEAVE`, and `CLOSURE_MAKE` machinery. xVM and Cranelift receive the
sealed plan and may choose representation or layout, but may not reselect a
capture mode, owner, evidence, witness, or cleanup responsibility.

An exported callable API exposes its normalized signature/type and public
responsibility channels only. Capture plan, field, evaluation, place, owner,
region, loan, reservation, cleanup, construction, environment, and closure
identities are value-level implementation residue and are forbidden from the
module API digest.

## Diagnostics

The active dispatch order is:

1. invalid binder/source-place/initializer graph:
   `RESOLVER_SCOPE_TREE_INVALID`;
2. nonactivatable current profile, including `deep`:
   `FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE`;
3. overlapping exclusive capture: `INOUT_ALIAS_CONFLICT`;
4. missing `#scoped#mut` inout profile:
   `CLOSURE_INOUT_CAPTURE_REQUIRES_SCOPED_MUT`;
5. escaping borrow: `BORROW_ESCAPE_OWNER_REGION`;
6. ownership mode, owner state, evidence, witness, or callable-right failure:
   `OWNERSHIP_MODE_ADMISSION_FAILED`.

The existing concur, generator, and pure-callable diagnostics keep their more
specific branches. Historical closure-capture diagnostic seeds remain
nonemitting.

## Acceptance and evidence boundary

The R31 static fixture set contains 9 positive, 3 boundary, 12 negative, and
11 mutation cases. The focused validator checks schema closure, ordinal and
place identity, exactly-once evaluation, responsibility binding, profile
gates, owner/loan disposition, reverse rollback, zero partial publication,
lexical separation, HIR/MIR binding, and the product fence.

This candidate closes the design-static projection only. It neither closes
`IR-OWN-P1-019` in canonical main nor proves a production parser, checker,
HIR/MIR lowerer, xVM, Cranelift backend, formatter, LSP, or conformance runner.
The exact 22 global feature P1 items and four M13 actions remain open and
unchanged. All 15 product lanes remain `NOT_RUN`.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
