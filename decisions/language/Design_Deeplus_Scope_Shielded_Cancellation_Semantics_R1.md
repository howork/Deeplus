# Deeplus `@scope shielded` Cancellation Semantics — R1

## Decision

Status: `LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED`
Cluster: `P0-4B / PREIMPL-P0-004B`
Canonical audit baseline: `10e64f492f0529610673846139afcf0d95175663`
Local predecessor: `878f3f4c4bf44586cebb836176c6b58af8da42e5`

`@scope shielded` is a lexical cancellation-observation fence. It does not
clear, catch, discard, convert, or acknowledge a cancellation request. A
request that is already pending at entry, arrives in the body, or arrives
during scope-local cleanup remains pending until the outermost active shield
has completed its own cleanup. Only then may the execution observe and
acknowledge the request at the scope-exit cooperative boundary.

This closes the previous positive-semantics gap without claiming parser,
checker, xVM, Cranelift, formatter/LSP, or runtime execution.

## Surface and admission

The source surface remains:

```deeplus
@scope shielded {
    ret await finishCriticalWrite()
}
```

The lossless CST preserves source order and trivia. The normalized AST uses a
set with one independent isolation bit and exactly one cancellation mode:

- no cancellation modifier: `INHERIT`;
- `cancellable`: `OBSERVE`;
- `shielded`: `DEFER_TO_OUTERMOST_SHIELD_EXIT`.

`isolated` is orthogonal and may accompany either cancellation mode. Repeating
any modifier is rejected. `cancellable` and `shielded` together are rejected.
An explicit nested `cancellable` scope inside an active `shielded` scope is also
rejected because a child cannot pierce its parent's cancellation-observation fence.
Either cancellation modifier requires an enclosing execution with a
Cancellation axis. The formatter emits `isolated` first and then the selected
cancellation modifier; this normalization changes neither meaning nor source
profile.

## Dynamic law

One dynamic `ScopeId` increments the shield depth of its exact `ExecutionId`
on entry and decrements it only after its cleanup region has completed. A
pending request encountered at an admitted cooperative boundary while depth is
nonzero records at most one `observation_deferred` transition for the exact
`(CancellationId, ScopeId)` pair. It does not record `observed` or
`acknowledged`.

For nested shields, an inner exit completes only the inner cleanup and leaves
the request pending. The request becomes observable only after the outermost
shield cleanup and depth transition to zero. On a normal fallthrough, `ret`,
`return`, `break`, or `continue`, cancellation observation occurs before the
staged transfer is published. The staged value or target is cleaned according
to its ordinary responsibility plan.

An Error or Defect already selected by the body or cleanup remains primary.
Pending cancellation never replaces it, becomes a recoverable Error, or enters
the suppressed-Error list. An Error path retains the request for the next
admitted cooperative boundary after recovery. A terminal Defect records the
unobserved pending request as terminal evidence and does not fabricate a
`terminal_cancelled` event.

The global cancellation order is:

```text
requested -> observed -> acknowledged -> cancellation cleanup barrier
          -> terminal_cancelled
```

Shield-local cleanup that precedes `observed` is ordinary scope-exit cleanup,
not the later cancellation cleanup barrier. This distinction removes the
previous apparent ordering conflict.

## HIR, MIR, and tooling handoff

Canonical HIR carries one `ScopeCancellationPlan` inside the existing
`CleanupScopePlan`. The plan fixes normalized modifiers, exact cancellation
mode, execution context, static parent shield, exit observation policy,
cleanup fence, and failure precedence. Runtime identities and request presence
are not HIR constants.

The existing cleanup-scope lowering row consumes and reproduces one
Cancellation token. MIR responsibility evidence records shield entry,
observation deferral, scope cleanup completion, shield exit, observation, and
acknowledgement without adding a backend-specific semantic choice. xVM and
Cranelift must preserve this order and may not infer a different cancellation
policy.

Formatter/LSP obligations are exact modifier-set diagnostics, canonical
modifier order, and source-preserving CST round trip. Product support remains
`NOT_RUN`.

## Acceptance boundary

The design-static acceptance corpus covers:

- a request already pending at entry;
- a request arriving in the body;
- a request arriving during cleanup;
- nested shield exit;
- a no-request normal path;
- Error/Defect precedence;
- duplicate and conflicting modifiers;
- a cancellation modifier outside a cancellation-aware execution.

Static validation is not a runtime execution receipt. Semantic P0 is zero for
this closed cluster, the existing 22 feature P1 actions remain OPEN and
unchanged, and all 15 product lanes remain `NOT_RUN`.
