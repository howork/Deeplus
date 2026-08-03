# Deeplus R44/R22 Actor Lifecycle Exact-Main Rebase R1

## Status

- repository: `howork/Deeplus`
- canonical baseline: `39a5d50cc770341c4b9776d00d84520b780d0c62`
- canonical baseline tree: `b19b2a86c0f29c1f73763c8526a3a7bde23d530a`
- local predecessor: R48 successor `b357ffbae3fb51e63afcd656134643917ee781fe`
  (tree `6a3acfb1fbd5b09461b6c0fe00cd4e79ca2e87aa`)
- gap: `IR-ACTOR-P1-005`
- design verdict: `APPROVED_NOT_INTEGRATED`
- product lanes: `15/15 NOT_RUN`
- GitHub publication: `SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION`

This successor preserves the immutable R42/R22 candidate while rebasing its
lifecycle semantics onto the R47 publication closure and the locally frozen
R48 tooling successor. It is a local semantic candidate, not a production
runtime implementation or product-support receipt.

## Rebase decision

R41 owns `ACC-R019` direct Actor Protocol conformance. R23 owns the stable
binding slot, binding-row digest, binding-table identity and exact typed MIR
selection. The lifecycle rule remains `ACC-R020`, and its target-execution gate
remains `ACC-G006`; the exact combined counts are 20 rules and 6 gates.

R22 consumes an already verified R23 selection and never constructs, looks up,
reselects or mutates a binding. For a protocol-originated transport event the
lifecycle trace retains the same table ID, binding ID, responsibility ID and
row digest. Concrete non-protocol operations carry no binding foreign key.

## Identity domains

R23 `ActorId` remains the static Actor declaration identity serialized in
binding tables. R22 introduces the internal, non-forgeable `ActorInstanceId`
for one runtime incarnation. `ActorRef`, `ActorRuntimeRootOwnerId`, `MailboxId`
and `StateRegionId` bind that runtime instance; the instance identity never
enters module API binding bytes, table digests or executable-origin identity.

`ActorRuntimeRootOwnerId` is unique per instance. `ActorTurnId`, `FailureId`
and `DefectId` retain their current domains. R22 does not introduce any R24
`ActorCodeGenerationId`, native code lease, relocation or JIT lifetime rule.

## Minimum sound lifecycle

Creation first verifies the executable binding set, then follows exactly
`create_prepare -> state_initialized -> mailbox_initialized ->
actor_publish_committed`. Publication records the immutable association between
the static declaration and runtime instance and happens-before external use.
Prepublication failure publishes no `ActorRef` and no Actor termination,
enters `CREATION_ABORTED`, reverse-cleans each initialized resource once, and
emits one root-owner creation-failure observation carrying `FailureId`.

Normal stop uses `DRAIN_ALL_COMMITTED_V1`. Admission closes before the drain;
the drain set is exactly the envelopes committed before that close. Drain
completion requires an empty committed set, no active turn and exactly one
terminal result for every admitted request. Per-channel FIFO remains the only
ordering promise. An indefinitely suspended active turn keeps stop pending and
retains `StateRegionId` authority; no implicit cancellation, cleanup, fabricated
reply, root observation or termination is permitted.

An uncaught Defect uses `STOP_AND_FAIL_PENDING_V1`. The primary `DefectId` is
immutable. No queued handler starts after Defect observation. Cleanup cardinality
is conditional: every queued payload once, the active turn once iff present,
then the Actor state region once. Cleanup Defects are recorded as ordered
suppressed identities in reverse-cleanup execution order and never replace the
primary Defect.

The still-open admitted request set is snapshotted at `defect_observed`. A reply
already terminal before that point is preserved. Each captured request receives
exactly one later `ActorMessageError::receiverClosedBeforeReply`, after cleanup,
with the original R23 request binding, responsibility and row digest. A SEND
selection never produces a Reply terminalization. Root observation is emitted
once before the single published termination, and no event follows termination.

## Subsystem boundary

Typed HIR and module artifacts retain the R41/R23 static identities. Verified
MIR carries the internal instance/root/state/turn identities, lifecycle policy,
transition state, conditional cleanup sets, reply snapshot and binding foreign
key. Runtime/xVM executes those selected barriers. Cranelift may preserve them
but cannot choose policy, reselect a provider or reorder observable barriers.
R24 remains the separate backend code-generation-lifetime cluster.

## Closure gate

Static validation can advance the gap only to `APPROVED_NOT_INTEGRATED`.
`IR-ACTOR-P1-005` becomes `VERIFIED_CLOSED` only after a separately authorized
semantic PR, CI, publication closure and exact post-merge readback. This
candidate closes no feature P1 and leaves all 15 product lanes `NOT_RUN`.
