# Deeplus Runtime and Managed Projection Implementation Handoff R108

Status: `LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF_COMPLETE_PRODUCT_NOT_RUN`

Baseline: local commit `94bb739bc8d541c90ef88526f86075d1c9ef4e9f`, tree `9462517520544476b3d72f998c66dda50f70aa4a`.

## Decision

R108 closes the remaining design-handoff ambiguity between the logical internal runtime ABI, the R99 target mapping preimages, managed stable handles, explicit shadow-root frames, xVM, Cranelift Object AOT, and Cranelift in-memory JIT. It does not connect Cranelift dependencies, build native artifacts, execute a runtime, or claim product support.

The machine contract is `spec/contracts/runtime-managed-projection-handoff-r108.json`. Its generator derives three full target projections from the exact R99 mapping rows and binds all 25 active helper signatures, all 20 logical value kinds, MIR identities, toolchain input, managed-reference profile, continuation interface, managed handle layout, shadow-root layout, and runtime-root registry.

## Managed handle and root profile

The first implementation uses a 40-byte, 8-byte-aligned stable handle slot with generation, state, referent, trace descriptor, and cleanup state fields. Generation advances before reuse; overflow permanently retires the slot. A raw address is never semantic identity.

Native execution uses explicit shadow-root frames. Root frames are strict LIFO while active, transfer to a continuation receipt before suspension, and are popped exactly once during ordinary return, error, defect, cancellation, or unwind cleanup. Root scanning admits only `LIVE` handles whose observed generation equals the receipt-bound expected generation. Missing, duplicate, unsorted, or stale roots reject the projection.

Cranelift may not add implicit safepoints. `managed.safepoint_enter` and `managed.safepoint_leave` are explicit target-projection steps. A finalized JIT image remains live while any call, suspended continuation, or root receipt references it.

## Target projections

- xVM uses 8-byte stack alignment and logical typed slots.
- Object AOT and in-memory JIT use 16-byte stack alignment on `x86_64-pc-windows-msvc`.
- AOT and JIT share the same logical scalar, indirect-slot, outcome, and helper allowlist mappings. Their symbol/import maps and image lifetimes remain distinct.
- Host defaults, opaque mapping digests, implicit roots, raw-address identity, and backend reinterpretation are forbidden.

## Acceptance and evidence honesty

The R108 validator checks three projections, three managed ABI records, sixteen positive/boundary/reject cases, and twelve bounded mutations. Static validation is E2 design evidence only. Semantic P0 remains zero, the exact 22 feature P1 actions remain OPEN, and all 15 product lanes remain `NOT_RUN`.

GitHub publication is not performed by this handoff.
