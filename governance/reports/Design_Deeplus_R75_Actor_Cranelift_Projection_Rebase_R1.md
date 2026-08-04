# Deeplus R75 Actor–Cranelift Projection Exact-Main Rebase R1

## 1. Verdict and authority fence

- repository: `howork/Deeplus`
- branch: `main`
- exact candidate baseline: `c016871d5aa1c7515fd8a8df181744916f1e1849`
- exact baseline tree: `46df9b097b3010768932ad88617d24b6a7b5e933`
- gap: `IR-ACTOR-P1-007`
- verdict: `APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE`
- source syntax change: `0`
- production implementation: `NOT_AUTHORIZED`
- GitHub publication: `NOT_AUTHORIZED_FOR_R75`
- product lanes: `15/15 NOT_RUN`

R75 rebinds the backend-neutral residue of the historical R24 candidate to
the current Actor lifecycle, Actor Protocol binding and Cranelift contracts.
It neither revives LLVM/ORC assumptions nor treats static receipt validation as
native execution. Deeplus MIR remains the sole execution semantic authority.

## 2. Dependency discharge and bounded stale repair

`IR-ACTOR-P1-005` and `IR-ACTOR-P1-006` are now canonically
`VERIFIED_CLOSED`. The R74 publication closure records the lifecycle closure at
`c016871d5aa1c7515fd8a8df181744916f1e1849`; R23 binding publication already
provided the executable-image binding identity. R75 therefore removes only the
two stale R24 HOLD statements in the lifecycle trace contract and its
implementation handoff. It does not alter lifecycle semantics.

The Actor native projection consumes, but never creates or reselects:

- `ExecutableImageId` and the loader-verified executable binding table set;
- `ActorProtocolBindingTableId`, `ActorProtocolBindingId`,
  `ResponsibilityId` and `binding_row_sha256`;
- `ActorInstanceId`, `ActorTurnId`, request terminal state, cleanup order and
  primary/suppressed Defect order; and
- all twenty-three current Cranelift base receipt inputs and `CLB-R001..012`.

## 3. Selected projection identity

`ActorCodeGenerationId` is a target projection identity derived under
`deeplus.actor-code-generation/v1` from exactly:

1. the complete current Cranelift base receipt input object;
2. `ExecutableImageId`;
3. the executable Actor binding table-set SHA-256;
4. the sorted exact binding-row SHA-256 set; and
5. the origin-coverage SHA-256.

`module_kind` occurs only inside the base receipt input object. Source order,
import order, object enumeration, link order, runtime address and symbol order
are excluded. `ActorId`, `ActorInstanceId`, `ExecutableImageId`,
`ActorCodeGenerationId`, `ActorCodeLeaseId`, backend code object, entry handle,
symbol and machine address remain different identity domains.

## 4. Exact generation lifetime

Aggregate owner counts are insufficient because a balanced total can hide a
duplicate release or missing transfer. R75 therefore requires a unique,
ordered `ActorCodeLeaseEventId` stream over unique `ActorCodeLeaseId` values.
The validator replays `ACQUIRE`, `TRANSFER`, `RELEASE`, `PUBLISH`, `UNPUBLISH`
and `RETIRE`, and requires the final open-lease set to equal the replay result.

The admitted owner kinds are published binding table, queued envelope, active
or suspended turn, Actor request terminal obligation, caller Reply
continuation, executing frame and code-dependent metadata. Dequeue transfers
one existing lease rather than releasing and reacquiring it. An Actor request
retains its Actor generation through terminal cleanup and suppressed-failure
observation. A caller continuation owns a separate lease whose generation need
not equal the Actor generation; one-way SEND creates no such continuation.

JIT retirement requires unpublished state, zero exact leases, zero executing
frames and zero code-metadata users. Object AOT uses image-unload or process
lifetime and cannot claim per-generation physical retirement from a logical
zero-lease state alone. Replacement publishes the new generation before
unpublishing the old and never rewrites an existing owner.

## 5. Managed references and outcomes

The current managed-reference profile remains fail-closed. `NOT_REQUIRED` is
valid only when safepoint, root-map, generated-callback, suspended-frame and
cleanup-entry obligation counts are all zero and digest-bound. Missing or
invalid evidence yields `BLOCK_NATIVE_LOWERING`; raw-pointer fallback is
forbidden.

Trap, stack-map, unwind and cleanup metadata remain alive through the last
Defect cleanup and suppressed-failure observation. Error, Defect,
Cancellation, suspension and cleanup remain explicit MIR outcomes or
transitions. Host unwind and arbitrary Cranelift traps do not become Deeplus
semantics.

## 6. Cross-path observation

A projection receipt proves one target projection only. Cross-path comparison
uses a separate differential receipt. Exact total-order comparison requires a
shared non-null `DeterministicScheduleTraceId` or an independently sealed
single-channel precondition. Otherwise only the seven required partial-order
invariants are compared. Scheduler completion, worker identity and unrelated
cross-sender order are never synthesized as authority.

## 7. Trace and test binding

The bounded trace overlay changes exactly three target cells from
`APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`:

| Feature | Stage | Authority |
|---|---|---|
| `actor_mailbox_capacity` | `DYNAMIC_LOWERING` | projection contract feature trace |
| `actor_minimum_lifecycle_r1` | `DYNAMIC_LOWERING` | projection contract feature trace |
| `actor_request_reply` | `DYNAMIC_LOWERING` | projection contract feature trace |

No other target cell changes. The cumulative counts become direct/delegated/
N/A/blocked `2473/4/502/1242`; the umbrella gap `IR-XCUT-P1-054` remains OPEN.

The exact acceptance matrix is `R24R-T01..R24R-T30`, with normal, boundary and
rejection coverage plus sixteen deterministic mutation controls. These are
design-static checks. Target-bound xVM, ObjectModule, JITModule, loader,
runtime and debugger execution remain `NOT_RUN`.

## 8. Closure gate

Local schema, focused validator, trace registry, mutation and workspace checks
can freeze the R75 semantic candidate. `IR-ACTOR-P1-007` becomes
`VERIFIED_CLOSED` only after a separately authorized semantic PR, CI,
publication closure and exact GitHub main readback. The future promotion must
not predict a merge SHA, close any of the twenty-two feature P1 items or claim
product support.
