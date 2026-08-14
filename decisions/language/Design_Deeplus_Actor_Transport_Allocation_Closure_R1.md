# Design Decision: Actor Transport Allocation Closure R1

Status: `LOCAL_STABLE_DESIGN_CANDIDATE_NOT_INTEGRATED`

Gap: `IR-ACTOR-P1-060`

## Decision

Actor transport keeps its normal value carriers unchanged:
`Result<Unit, error ActorMessageError>` for one-way send and
`Result<Reply<T>, error ActorMessageError>` for request. `ActorMessageError`
continues to describe transport admission and receiver-lifecycle outcomes only.

The `:~` operation also has the independent dynamic responsibility
`throws AllocationError effects allocate`. This responsibility covers the
compiler/runtime-owned envelope, required mailbox storage, and request-only
Reply/correlation responsibility storage. It is not converted to `mailboxFull`,
Cancellation, or Defect.

Receiver closure and bounded capacity rejection are decided before allocation.
If admission remains possible, every required allocation is staged before the
enqueue commit. Failure restores sender ownership, reverse-cleans staged
resources, publishes no message, sequence, ReplyId, CorrelationId, or Result,
and propagates `AllocationError`. One atomic enqueue commit then publishes the
already prepared resources and transferred owners. Postcommit allocation count
is exactly zero.

`logical_unbounded_v1` means only that there is no language-level capacity
rejection. It does not promise infinite storage and does not hide managed
allocation failure.

## Non-goals

- No new source syntax.
- No new `ActorMessageError` case.
- No retry, block, suspension, drop, OOM Defect, or postcommit repair path.
- No product parser/checker/MIR/xVM/runtime/tooling support claim.

The existing feature P1 set remains exactly 22 OPEN and all product lanes remain
`NOT_RUN`.
