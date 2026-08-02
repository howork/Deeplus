# Deeplus Managed-Reference Memory Profile R1

## Verdict

`ACCEPT_OPTION_A_WITH_DEPENDENCY_GUARD`

Deeplus Phase 1 uses stop-the-world, nonmoving, full-heap tracing with opaque
stable handles and explicit shadow-root frames. This closes the design gap in
`IR-OWN-P1-025` without adding source syntax or making a product-support claim.
The exact profile identity is
`STW_NONMOVING_TRACING_WITH_OPAQUE_STABLE_HANDLES_R1`.
This exact-main fusion binds the typed
`ContinuationInterfaceId:DEEPLUS_CONTINUATION_INTERFACE_R1` and its exact R38
digest. `IR-OWN-P0-017` remains the governance gap identifier, not an interface
identity. Canonical promotion remains pending publication of the fused
candidate; an unbound/null dependency cannot pass promotion.

## Why this profile

The profile keeps language identity, ownership, cleanup and cancellation out of
the backend. A handle remains stable while the collector traces referents, and
Cranelift receives an explicit root-frame ABI instead of being asked to infer
Deeplus roots from target registers. Nonmoving collection avoids relocation and
write-barrier laws in the first implementation milestone.

Rejected or deferred alternatives:

- precise moving stack-map collection is deferred until the locked Cranelift
  family and target matrix have a target-bound stack-map receipt;
- ARC/RC is rejected for Phase 1 because cycle behavior and retain/release
  ordering would add observable responsibilities;
- excluding managed references from native paths remains the fail-closed
  fallback if shadow-root feasibility fails.

Cranelift user stack maps are producer supplied; they do not discover managed
roots for the frontend. See the official Cranelift sources:

- <https://docs.rs/cranelift-codegen/latest/src/cranelift_codegen/ir/user_stack_maps.rs.html>
- <https://docs.rs/cranelift-frontend/latest/cranelift_frontend/struct.FunctionBuilder.html>

## Runtime identity and collector

`ManagedHandle` is runtime-owned and opaque. Its slot contains a generation,
state, referent, trace descriptor and cleanup-state summary. The state machine
is `FREE -> RESERVED -> INITIALIZING -> LIVE -> RETIRED -> FREE`; generation
advances before reuse. A handle, object address, page, size class or mark order
is never a source, module-API, serialization or ABI identity.

The collector is stop-the-world, nonmoving, nongenerational and nonconcurrent.
Phase 1 has no relocation, read barrier, write barrier, weak reference,
ephemeron, resurrection, user finalizer, semantic pinning or conservative scan.
The collector never invokes `def#cleanup`, consumes a cleanup token, delivers
cancellation or selects a Deeplus outcome.

## Trace and root model

Every managed type binds one semantic `TraceDescriptorId` whose ordered
projections are logical fields, not byte offsets or masks. A body carries
trace-descriptor, safepoint, root-map, allocation-plan, interior-projection and
suspension-transfer tables.

At each declared safepoint:

```text
declared_root_ids = sorted_unique(
    running_root_ids union frame_root_ids union runtime_root_ids
)
```

The three partitions are pairwise disjoint. A root identifies a live storage
location, so two locations containing the same handle remain two roots. Every
entry binds owner, storage, trace descriptor and an exact nonnegative handle
generation value.
Missing, extra, duplicate, unordered, unknown-generation or unknown-descriptor
entries reject the projection.

The root receipt is verified and published before the may-collect operation is
entered and remains live through outcome commit. Native paths synchronize
logical roots into an explicit shadow-root frame; xVM uses fixed frame slots.
Both consume the same logical `RootMapId`.

## Closed safepoint set

There are no implicit backend safepoints or standalone Phase-1 GC polls.
Safepoints are attached only to these semantic sites:

- non-tail `INVOKE`;
- a managed-allocation slow path represented by `CHECKED`;
- `SUSPEND`, after continuation roots are installed;
- `CANCEL_CHECK`, before either successor observes the cancellation state;
- runtime entries represented by `RUN_OP`, `ACTOR_OP`, `PROVIDER_OP`,
  `ONCE_OP` and `SYNC_OP`;
- a `BR` or `COND_BR` CFG backedge, so a compute-only loop cannot prevent
  cooperative stop-the-world progress;
- an `INVOKE` that crosses an FFI boundary, after managed roots are published
  and after the managed-derived-pointer fence is verified.

An allocation fast path never collects. A safepoint is not a
`CancellationPoint`; collection and cancellation remain orthogonal.

## Allocation and cleanup

Managed allocation is transactional: reserve handle and object, root every
input and staged owner, initialize, and publish once. Existing
`AllocationError effects allocate` is the recoverable failure. Precommit
failure cancels reservations, restores the input owner, reverse-cleans staged
resources and publishes nothing. No new OOM Defect is invented.

Object reachability does not own Resource cleanup. An active cleanup token is a
root; an unreachable live object that still owns an active cleanup obligation
is an invariant failure, never an invitation for the collector to run cleanup.

## Suspension, interior access and FFI

Suspension transfers roots from the active frame to the continuation frame
exactly once. Each handover pairs a source RootId with a distinct destination
RootId and requires the two entries to carry the same exact handle-generation
value. The source entry is removed only after destination installation. This
profile consumes the typed R38 continuation interface; it does not replace that
cluster's continuation state machine.

Interior access is represented as `ManagedHandle + ProjectionId`. A raw native
address may exist only inside a proven `NO_COLLECT` region and dies before a
call, safepoint, suspension, actor boundary or FFI entry. Phase 1 exports no
runtime managed handle, referent address or interior pointer through FFI. An
application-owned foreign opaque handle is a different identity.

## JIT lifetime

An unpublished JIT image may retire only when all of the following are zero:

```text
active_native_activation_count
suspended_continuation_count
outstanding_root_receipt_count
```

Code, safepoint metadata and shadow-root ABI live until that gate passes.
Retirement is exactly once. Managed handles outlive code images independently,
and an old activation or frame is never rebound to a new image generation.

## Cross-path parity

xVM, Object AOT and JIT preserve the same ordered `SafepointId`, logical root
set, root-owner transfer, ownership transition, cleanup outcome and terminal
result. Handle addresses, heap layout, collection timing, mark order, registers
and stack offsets are excluded from parity identity.

## Diagnostics and evidence boundary

Missing executable-HIR capability closure continues to use
`HIR_MIR_CAPABILITY_RECEIPT_MISMATCH`. R36 adds exact projection-verifier
diagnostics for invalid safepoint/root sets, digest/order, raw-pointer lifetime,
JIT lease and cross-path parity. None is a new source spelling or a claim that a
compiler/runtime exists.

Semantic P0 remains 0. The exact 22 feature P1 items and four separate M13
actions remain OPEN. All 15 product lanes remain `NOT_RUN`.
