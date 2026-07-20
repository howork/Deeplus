# Conflict and Gap Register

| ID | Class | Evidence | Design_ resolution | Blocking local acceptance | Blocking later lane |
|---|---|---|---|---|---|
| `IFC-CONF-001` | historical authority ledger | immutable SFD R1 reopened `SFD-P1-001..008` | controlling R2 status applied; eight remain statically closed | no | no current conflict |
| `IFC-CONF-002` | baseline identity role | predecessor `f509…` vs live/current `623ac…` | predecessor is provenance only; current review main is `623ac…` | no | future execution must bind separately |
| `IFC-CONF-003` | duplicate projection | Trait P1 appears in multiple parent projections | deduplicate by exact ID; seven remain OPEN | no | closure still requires original gates |
| `IFC-CONF-004` | canonical target gap | `U-07` has no exact target/policy | retain `HOLD_UNBOUND_CANONICAL_TARGET` | no | blocks canonical migration materialization |
| `IFC-CONF-005` | separate execution track | five-path authority has no fusion-owned future execution HEAD | reference identity only; absorb no delta/head | no | blocks execution without separate authority |
| `IFC-GAP-006` | evidence boundary | product lanes not executed | retain `15/15 NOT_RUN` | no | blocks product support/promotion |

Actual unresolved semantic or current-authority conflict: **0**.
