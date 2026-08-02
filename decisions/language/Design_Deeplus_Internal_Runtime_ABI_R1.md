# Deeplus Internal Runtime ABI R1

Status: **Stable design candidate; local, noncanonical, product NOT_RUN**

## Decision

Deeplus uses one versioned backend-neutral logical ABI for calls that cross a
generated-code/runtime boundary. xVM, Cranelift Object AOT, and Cranelift JIT
use target projections of that same logical contract. A target projection is
representation evidence, not language semantics.

The R1 profile is intentionally uniform and conservative:

- fixed primitive scalars use direct channels;
- every aggregate, nominal value, closure, collection, `Option`, `Result`,
  `Rational`, and `Complex` value uses an indirect typed slot;
- an aggregate normal result uses the caller-provided normal slot as sret;
- no aggregate is split into target registers at an internal ABI boundary;
- `Unit` has no normal payload and `Never` cannot materialize a return;
- a managed reference uses an opaque `MANAGED_HANDLE` channel only after the
  exact managed-handle dependency is bound;
- borrow and `inout` channels are call-bounded target addresses and never
  become semantic identities or escaping values.

## Outcome channel

The dispatcher returns the closed union `COMPLETE(OutcomeTag) |
PARKED(ContinuationReceiptId)`. A completed call carries one direct
`OutcomeTag` with exactly four values in this order: `NORMAL = 0`, `ERROR = 1`,
`DEFECT = 2`, and `CANCELLATION = 3`. The caller supplies four disjoint typed
slots. Exactly the slot selected by a completed call may commit; the other
slots remain uninitialized. Error is never a Defect, Cancellation is never an
Error, and no host exception or unwind is admitted as a Deeplus outcome.

Suspension is not a fifth inferred result tag. `PARKED` commits no outcome tag,
no outcome slot, and no MIR successor. It instead transfers the exact committed
owners, active loans, cleanup tokens, and roots to one continuation receipt,
with zero source residual. Those loans end only on the resumed or cancelled
terminal edge. A suspending runtime entry must bind the separately approved
continuation interface before this ABI can admit it; until then it remains
dependency-unbound and excluded from the active helper allowlist.

## Ownership boundary

Argument evaluation, acquisition, conversion, slot preparation, ABI/signature
verification, root publication, and reservation all finish before entry. One
atomic `ownership_commit` immediately precedes callee entry. Failure before
that point cancels reservations, reverse-cleans staged temporaries, and retains
the caller owner. Once entry occurs, a later Normal, Error, Defect, or
Cancellation outcome never restores transferred inputs to the caller. Borrow
and `inout` loans end on every explicit completed outcome edge. A parked call
transfers their exact state once to its continuation receipt instead. An output
owner transfers only when its matching completed-call output slot commits.

The ABI introduces no new source-observable event and does not replace MIR
cleanup or outcome ordering.

## Identity and compatibility

`RuntimeAbiId`, `RuntimeHelperId`, `RuntimeHelperSignatureId`,
`RuntimeAbiTargetProjectionId`, and `RuntimeAbiReceiptId` are distinct typed
identity domains. A native symbol spelling, table index, address, link order,
or load order cannot substitute for any of them.

R1 compatibility is exact. Caller, callee/runtime, helper allowlist, and target
projection must bind the same ABI ID, full canonical digest, and helper
signature digest. There is no inferred minor-version, subset, prefix, or host
default compatibility. The canonical preimage uses
`DEEPLUS_CANONICAL_JSON_UTF8_SHA256_V1`; self-digest fields and target-private
addresses are excluded.

## Target projections

Every projection binds the exact target triple, pointer width, endianness,
stack alignment, calling convention, module kind, Cranelift/toolchain identity
where applicable, scalar mapping, indirect-slot mapping, outcome-tag mapping,
helper symbol/import mapping, and dependency digests.

xVM uses logical slots and typed helper-table entries. Object AOT uses an exact
symbol sidecar and linker receipt. JIT uses an exact import allowlist, resolved
map, immutable image-generation identity, and retirement receipt. Runtime to
generated-code callbacks are outside R1; missing or mismatched imports fail
before execution.

## Dependency guards

The logical contract is independently materialized from canonical `main`.
Canonical promotion is not ready until both of these exact dependencies are
integrated and rebound:

1. `IR-OWN-P1-025`: managed-reference Phase-1 handle/root ABI;
2. `IR-OWN-P0-017`: suspending continuation-root interface, for any suspending
   runtime entry.

Their digest fields are deliberately null in this local candidate. Six
suspending helper rows and three managed-memory helper rows are therefore
dependency-unbound and excluded from the active allowlist. The two function-
static/lazy helpers and scoped mutex acquire are synchronous COMPLETE-only
operations: host-thread blocking does not create semantic suspension. No digest
is guessed from another local branch.

## Rejected alternatives

- Per-backend ABIs were rejected because they would make differential outcome
  and ownership parity optional.
- Aggregate register splitting was rejected for R1 because it multiplies
  target-dependent classification and verifier state.
- Host unwind as an error channel was rejected because it would bypass MIR
  outcome and cleanup authority.
- Compatibility by ABI version prefix, symbol spelling, or helper subset was
  rejected because matching-looking artifacts could still disagree.
- Runtime callbacks and external FFI were deferred; neither is silently
  authorized by this internal ABI.

## Evidence boundary

This decision creates a design-static contract, schemas, fixtures, and a
validator. It performs no production parser, checker, MIR, xVM, runtime,
Cranelift, linker, formatter, LSP, or debugger execution. Semantic P0 remains
zero, the exact 22 feature P1 remain OPEN, the four M13 actions remain OPEN,
and all 15 product lanes remain `NOT_RUN`.
