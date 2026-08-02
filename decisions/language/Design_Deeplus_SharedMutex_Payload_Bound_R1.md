# Deeplus SharedMutex Payload Bound Decision R1

Status: `CURRENT_STABLE_DESIGN_LOCAL_CANDIDATE`

Gap: `IR-OWN-P1-024`
Baseline: `howork/Deeplus main@4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`

## Decision

The public Prelude identity is
`SharedMutex<T: SharedMutexPayload>`. `SharedMutexPayload` is a sealed,
compiler-known, context-specific responsibility constraint. It is not a Trait,
does not admit `conform`, and cannot be manufactured by an annotation, wrapper,
import, source order, link order, or runtime lookup. The checker operation is
the single predicate `SharedMutexPayloadAdmitted`.

The predicate uses a dedicated `SharedMutexPayloadDescriptorR1`, because the
general RCTS descriptor does not contain a complete transitive stored-field
projection. It expands transparent aliases, requires one closed normalized
root and generic substitution, canonical-sorts stored component paths, and
walks the finite owner-closed graph with memoized strongly connected
components. Opaque or incomplete components fail closed.

An admitted component may be Reusable or Affine, including mutable nominal
state, when it owns no resource lifecycle, cleanup token or hook, cleanup
ErrorSet or EffectRow, cleanup authority, cleanup suspension or cancellation,
or borrowed/`inout` view region. This rule deliberately does not require
`Plain`: it creates no copy, clone, sharing, transfer, representation, ABI,
serialization, or actor-isolation evidence. A generic component passes only
through the exact explicit `SharedMutexPayload` bound.

`SharedMutex::new(move value)` checks the predicate before move commit. A
rejection therefore retains the source owner and emits exactly the existing
`SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD` diagnostic. No automatic fix can
choose a new ownership or cleanup design, so the diagnostic is manual-review
only.

## Public and machine residue

The normalized Prelude signature and module API digest both retain the bound.
The structured API row contains the parameter ID, predicate ID, and canonical
predicate-contract SHA-256; text alone is insufficient. Compiler-local mutex,
loan, region, cleanup-registration, and runtime identities remain outside the
module API.

The existing `SYNC_OP`, `LOAN_BEGIN_EXCLUSIVE`, `LOAN_END`, `LOCK_ACQUIRE`, and
`LOCK_RELEASE` machine identities are sufficient. A body-local
`SharedMutexWithLockPlan` resolves every referenced `sync_plan_id`. Receiver and
callback evaluate once, acquire precedes the exclusive loan and callback,
`LOAN_END` precedes `LOCK_RELEASE`, and release executes exactly once on normal,
Error, Defect, and Cancellation outcomes. Unlock is infallible and never
changes the callback's primary failure. The wrapper-owned unlock obligation is
not payload cleanup and is excluded from `SharedMutexPayloadAdmitted`.

## Examples

```deeplus
public value class CounterState {
    public var count: Int
}

let counter = SharedMutex::new(move CounterState!(count: 0))
counter ~ withLock { inout state =>
    state.count += 1
}
```

The mutable payload is admitted when its complete stored graph has no cleanup
responsibility. This does not make `CounterState` Plain or Transferable.

```deeplus
public def makeBox<T: SharedMutexPayload>(move value: T) -> SharedMutex<T> = {
    return SharedMutex::new(move value)
}
```

The exact public generic bound is required and survives separate compilation.

```deeplus
public resource class OpenFileState {
    private let handle: FileHandle
}

public def rejectResource(move state: OpenFileState) -> Unit = {
    let invalid = SharedMutex::new(move state)
    // SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD
}
```

The rejection occurs before the constructor consumes `invalid`'s argument.

## Evidence boundary

The R35 schema, fixtures, reference predicate evaluator, mutation matrix, and
workspace validators are design-static evidence. They do not execute a
production parser, checker, HIR/MIR lowerer, xVM, Cranelift backend, formatter,
or LSP. Semantic P0 remains `0`; the exact 22 feature P1 items and four separate
actions remain OPEN; all 15 product lanes remain `NOT_RUN`. GitHub publication
remains suspended by user instruction.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
