# Deeplus R68 Region Lifetime Dynamic Trace Closure R1

## Decision

R68 repairs the bounded RegionId/LoanId ownership and projection seam, then
closes exactly `region_lifetime_model_phase_a / DYNAMIC_LOWERING` from
`APPLICABLE_BLOCKED_BY_GAP` to `BOUND_DIRECT`. The local predecessor is
`11d9df3e1ce148be5c73f227376470fff114723d`; the canonical publication baseline
remains `39a5d50cc770341c4b9776d00d84520b780d0c62`.

The checker selects static RegionId and LoanId identities before typed-HIR
sealing. Typed HIR preserves a finite region forest, place storage-region
bindings, and the exact concrete region/loan tuple for each admitted borrow
plan. MIR preserves those identities exactly. Dynamic loop activations remain
the responsibility of the existing ACCESS-token state machine.

Type identity and value identity are separate. A normalized type descriptor
contains only `region_profile_id_or_null`; it never contains a concrete
per-value RegionId. Concrete RegionId and LoanId values occur only in the
body/plan and MIR value/loan domains and are never exported through a module
API.

The body-wide projection pass runs after ordinary node-row lowering and before
release verification. It validates a reference-closed acyclic region forest,
exact entry/end extents, place storage regions, constraint membership,
shared/exclusive dispatch, strict child reborrow containment, suspension and
isolation fences, and canonical projection identity. R34 remains the sole owner
of LOAN_END placement and dynamic path balance.

The direct trace evidence is
`spec/contracts/region-lifetime-mir-projection-r1.json#/projection_contract`.
It is direct because this feature owns the checker-to-HIR-to-MIR region/loan
projection; R34 supplies a downstream close-frontier proof without absorbing
that ownership.

## Exact postcondition

Exactly one of 4,221 trace cells changes; the other 4,220 retain digest
`24bd4668d31d583d421bd5b124e902ac1d7d1271ed263e40afc9660022e8dee3`.
Post-overlay counts are 2,466 direct, 3 delegated, 501 not applicable, and
1,251 blocked cells, with 14 overlays, 130 bindings, and 3,143 evidence rows.

No source syntax, public diagnostic, MIR operation, linear token, runtime
service, ABI field, or backend identity is added. Region and loan identities
are compiler-local verifier identities and may be erased after verification;
runtime/backend relookup or inference is forbidden. Semantic P0 stays zero,
feature P1 stays `22_OPEN_UNCHANGED`, M13 stays `4_OPEN_UNCHANGED`, product
lanes stay `15_OF_15_NOT_RUN`, and GitHub publication stays `SUSPENDED`.
