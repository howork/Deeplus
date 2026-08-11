# Deeplus Publication and Current-Pointer Binding Closure R1

## Decision

`ACCEPT_TWO_PHASE_EXTERNAL_READBACK_BINDING`

Audit gap `IR-GOV-P0-064` is closed in this local candidate against read-only
main `10e64f492f0529610673846139afcf0d95175663`.

The live-main pointer claimed `current_binding: true` while its receipt location
was still `PENDING_POST_MERGE_READBACK_RECEIPT`. The repository already contains
an immutable external receipt that records the R77 semantic merge, later
publication-closure merge, exact trees, required GitHub Actions and live-main
readback. The pointer is therefore rebound to that receipt while artifact
self-binding remains false.

## Identity roles

- `da734c608c0d583a671c0da9e14da00bff42affd` is the semantic publication
  target from PR #76.
- `10e64f492f0529610673846139afcf0d95175663` is the publication-closure and
  post-merge readback commit from PR #77.
- file SHA-256 values identify artifact bytes and are never compared directly
  with Git commit SHA values.

`semantic_authority_active: true` does not imply artifact self-binding.
`current_binding: false` is the explicit self-reference fence; the external
receipt proves publication without requiring a file to predict the commit that
contains it.

## Required state law

Pending or absent receipt plus `current_binding: true` is invalid. Before the
receipt exists, the state is HOLD with false current binding. After exact
readback, semantic authority is active, the receipt is immutable, and current
binding remains false. If main later advances, a new cluster rebases its
baseline; it does not rewrite the historical receipt.

## Evidence boundary

This closure changes no Deeplus syntax or semantics. Semantic P0 remains 0,
the exact 22 feature P1 remain OPEN, and all 15 product lanes remain `NOT_RUN`.
No production compiler/runtime/tooling execution or GitHub mutation is claimed.
