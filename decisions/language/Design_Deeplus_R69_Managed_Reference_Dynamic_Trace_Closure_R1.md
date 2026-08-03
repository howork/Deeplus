# Deeplus R69 Managed-Reference Dynamic Trace Closure R1

## Decision

R69 defines the bounded successor seam for
`managed_reference_memory_profile_phase1 / DYNAMIC_LOWERING`. It preserves the
R36 Phase-1 collector choice and the R37 backend-neutral runtime ABI, but binds
them to the current continuation-interface digest
`56ae21c7e0b18fc30ef753a6a38e7b849783f550ca8e4b253b72344b38369cbb`,
recomputed after the R69 HIR/MIR descriptor and verifier bindings were added.
Three active predecessor pointers still containing the former `0dc489...`
digest are historical inputs at this seam and are not accepted as successor
authority.

The historical predecessor digest remains immutable evidence. The active R36
successor seam is bound by
`spec/contracts/managed-reference-memory-profile-r1.json` at SHA-256
`feff3c021d4b77e64e4e9f00f797b0ce2c465a5b60709d86d0baf7bded72c7f7`;
R37 is bound by `spec/contracts/internal-runtime-abi-r1.json` at SHA-256
`fa905282037bdda3d3eb122d74f467ae611ea1ca7d355b0efb49c02fb6f93ba0`.

## Static plan and runtime receipt

The managed-memory plan is a deterministic, backend-neutral companion to
verified MIR. It contains trace descriptors, semantic safepoints, logical root
map templates, allocation plans, interior projections and suspension transfer
templates. A static root entry identifies a storage location and trace
descriptor. It does not contain a runtime handle generation or a publish,
commit or release state.

At each execution of a safepoint, the runtime constructs one root receipt from
the verified static template and target projection. That receipt binds the
execution epoch and exact handle generation for every logical RootId. It is
verified and published before the may-collect entry, remains live through the
selected MIR outcome commit, and is released afterward. A missing, extra,
duplicate, unsorted, stale-digest or generation-mismatched entry fails before
collection.

The continuation receipt remains the specialized authority for suspension
rebind: it already binds source and destination RootIds, exact checked handle
generation, root-map identities and digests, bijection and zero source
residual. It does not cover ordinary invoke, allocation, runtime-entry,
backedge or FFI safepoints; those executions require the general managed-root
receipt. At suspension their common root-map and generation facts must agree.

## Deterministic lowering boundary

The order is fixed:

1. verify MIR and RegionId/LoanId balance;
2. recompute and verify the static managed-memory plan;
3. project logical roots to xVM slots or native target storage;
4. verify and publish the runtime root receipt;
5. enter the exact may-collect operation;
6. commit the selected MIR outcome; and
7. release the root receipt.

RegionId and LoanId remain compiler-local verifier identities and never become
RootId. A borrowed or `inout` view creates no independent managed root, and
root liveness never extends a region or loan. Nonmoving managed storage is not
proof that a loan may cross suspension. Only the already admitted
process-static immutable shared proof can cross, with the existing R38 frame
root projection; ordinary and exclusive loans still end first.

xVM, Object AOT and in-memory JIT preserve identical ordered safepoints,
logical roots, owner transfers, cleanup results and terminal outcomes. Target
addresses, registers, stack offsets, heap layout and collection timing remain
projection-private. The backend may not infer a new root or safepoint.

## Evidence boundary

This contract adds no source surface, HIR identity, MIR operation kind,
backend semantic identity or product implementation. Managed safepoint
enter/leave is a target/runtime projection around an existing verified MIR
safepoint, not a new MIR terminator. Semantic P0 remains zero, feature P1
remains exactly 22 OPEN, M13 actions remain four OPEN, and all 15 product lanes
remain `NOT_RUN`.

The machine-readable authority is
`spec/contracts/managed-reference-dynamic-projection-r1.json`. Product support,
runtime execution and GitHub publication are not claimed by this local
contract.
