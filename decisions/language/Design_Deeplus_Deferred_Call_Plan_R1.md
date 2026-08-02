# Deeplus Deferred Call Plan R1

Status: `STABLE_DESIGN_STATIC_CANDIDATE`
Gap: `IR-OWN-P1-020`
Baseline: `howork/Deeplus main` at
`4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`
Product support: `15/15 NOT_RUN`
GitHub publication: `SUSPENDED`

## Decision

`defer` keeps its existing single-invocation surface. It does not accept a
block, an inline callable, a trailing closure, a guard, `await`, `spawn`, or
actor transport. This decision adds no token or grammar production.

A valid `defer` statement creates one immutable `DeferredCallPlan`. The plan
fixes the semantic call target and ordinary dispatch route, evaluates and
prepares its receiver and arguments at the registration statement, and then
publishes exactly one cleanup registration. Scope exit consumes the sealed
plan once. It does not resolve the call or reevaluate an operand at exit.

For a virtual call, the selected declaration, normalized call shape, and
virtual slot are fixed at registration. The ordinary runtime slot lookup on
the stored receiver remains part of that selected dispatch route; it is not a
second overload, extension, witness, or fallback selection.

## Registration-time call preparation

Static preflight first selects one admitted ordinary direct or `~` message
call and binds every formal channel, default provider, context argument, and
static evidence identity. Actor `:~` transport remains rejected. Preflight
does not evaluate a source expression.

Dynamic preparation then follows the ordinary call order:

1. evaluate the callee or receiver once;
2. evaluate every runtime-valued explicit `CallArgument`, including `context`,
   in written order, once each;
3. evaluate every selected default under the normal default-argument order;
4. preserve static witness/evidence bindings out of band with evaluation count
   zero;
5. validate and stage ownership, loans, move reservations, temporaries,
   ErrorSet, EffectRow, and cleanup obligations;
6. atomically publish one sealed cleanup registration.

Static evidence selection is preserved by identity and has evaluation count
zero. Every dynamic operand has one `EvalId` and evaluation count one. A
default is evaluated at registration even though its expression belongs to
the selected callable declaration. No operand, default, provider, or dynamic
dispatch candidate is delayed until scope exit.

## Ownership and value identity

Preparation preserves the ordinary parameter responsibility rather than
silently cloning:

- a reusable plain value is snapshotted into the plan;
- a shared or exclusive borrow creates the exact loan required through plan
  discharge;
- a consuming input creates an exact move reservation during preparation and
  atomically moves the owner into the sealed plan when registration commits;
- a registration-time temporary becomes plan-owned immediately;
- static evidence contributes an identity but no runtime value evaluation.

A source moved into the plan is dead immediately after successful registration.
A borrowed or otherwise pinned place cannot be moved, rebound, or replaced
before discharge. Reading
or operating through an independently admitted borrow does not change the
place identity; mutation still obeys the exact loan and callable contract.
The checker never substitutes a hidden copy or clone to make a plan fit.

The plan identity is
`DeferredCallPlanId(CleanupScopeId, source_registration_ordinal)`. Prepared
operands use contiguous zero-based evaluation ordinals. Cleanup registration,
plan, operand, value, place, owner, region, loan, reservation, ErrorSet, and
EffectRow identities are value-level implementation residue and are not public
module API identities.

## Registration transaction

All potentially failing preparation occurs before publication. If target
selection or static admission fails, no operand is evaluated. If dynamic
preparation fails after a prefix has succeeded, only that prepared prefix is
cleaned in strict reverse acquisition order: loans end, move reservations are
cancelled, and plan-owned temporaries are cleaned exactly once. No cleanup
registration is published and no source owner is consumed. External effects
already observed while evaluating an operand or default are not claimed to be
undone.

After all preparations succeed, `CLEANUP_REGISTER`, the required
`CLEANUP_PIN` operations, and `CLEANUP_SEAL` publish the immutable plan in one
nonbranching, nonsuspending interval. Partial registration count is zero.

## Scope exit and failure ordering

Registrations execute in strict reverse registration order. Each plan is
attempted exactly once when its cleanup scope is exited by fallthrough,
`return`, an exiting `break` or `continue`, recoverable Error, Defect, or
Cancellation. A suspension does not exit the cleanup scope and therefore does
not execute the plan; the registration remains pinned to the active cleanup
scope. The separate suspension-frame cluster owns physical frame residence and
cancellation state-machine details.

Execution uses only stored operands and the sealed dispatch route. It performs
the remaining ordinary callable input admission, invokes once, applies the
ordinary expression-statement result responsibility, records its cleanup
outcome, and discharges all loans, reservations, plan-owned inputs, and any
owned result temporary exactly once. The result disposition is sealed as one
of `UNIT_NO_VALUE`, `DISCARD_CLEANUP_FREE_VALUE`, or
`CLEAN_OWNED_TEMPORARY`; actor admission results remain forbidden. There is no
retry and no untyped result drop.

Existing cleanup outcome law remains authoritative. A pre-existing body
failure stays primary and cleanup failures are appended in actual LIFO
execution order. If the body completed normally, the first failing cleanup is
primary and later cleanup failures are suppressed in LIFO order. Defect and
Cancellation remain distinct terminal axes and are never rewritten as an
Error merely because cleanup runs.

## HIR, MIR, runtime, and API boundary

HIR binds one `DeferredCallPlan` to each `CleanupRegistration`. It preserves
the source registration ordinal, exact `HirCallPlan`, prepared operands,
registration and execution responsibility rows, cleanup scope, terminal-edge
policy, and sealed state. The backend receives no unresolved overload,
extension, witness, default, ownership, or cleanup decision.

No new MIR operation kind is required. Lowering reuses move, loan, cleanup,
`CHECKED`, `INVOKE`, and `LEAVE` machinery. The existing
`CLEANUP_REGISTER(cleanup_registration_id, cleanup_region_id)` payload is not
expanded; its registration identity indexes an exact typed deferred-call row
in the MIR body table. xVM and Cranelift may choose plan storage and calling
representation but cannot change evaluation time, call selection, operand
identity, LIFO order, result disposition, or outcome aggregation.

The public API exposes the callable signatures and their normalized public
error/effect responsibilities. It never exports a value-level deferred plan,
registration, prepared operand, evaluation, place, owner, loan, reservation,
or cleanup token.

## Diagnostics

R32 invents no diagnostic ID. Surface-shape rejection continues to use
`DEFER_REQUIRES_SINGLE_INVOCATION` or
`DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL`. Actor transport uses
`ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER`. Moving or rebinding a pinned place uses
`DEFER_CLEANUP_RESERVED_PLACE_MOVED`. Ordinary resolution, argument binding,
ownership, borrow, effect, and error failures retain their already-selected
ordinary call diagnostics. The cleanup-budget seed diagnostics remain
nonemitting because `IR-OWN-P1-021` is outside this cluster.

## Acceptance and evidence boundary

The R32 fixture set covers direct and message calls, defaults, context,
snapshots, loans, deferred move reservations, registration failure, LIFO
execution, body/cleanup failure ordering, suspension persistence, invalid
surface shapes, actor transport, and reservation misuse. Mutation tests reject
reordering, delayed evaluation, duplicate evaluation, ordinal gaps, partial
publication, forward rollback, mutable plans, multiple execution, non-LIFO
execution, identity substitution, and product-support overclaim.

This candidate closes the design-static projection only. It does not close
`IR-OWN-P1-020` in canonical main or prove a production parser, checker,
HIR/MIR lowerer, xVM, Cranelift backend, formatter, LSP, or conformance runner.
The exact 22 global feature P1 items and four separate actions remain open and
unchanged. All 15 product lanes remain `NOT_RUN`.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
