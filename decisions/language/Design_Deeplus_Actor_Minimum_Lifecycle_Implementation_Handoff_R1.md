# Deeplus Actor Minimum Lifecycle Implementation Handoff R1

## Authority and scope

This handoff binds the already frozen `ACC-R020` Actor lifecycle semantics to
implementation responsibilities. It adds no source syntax and changes no R49
lifecycle rule. Production implementation is not authorized by this document.
`IR-ACTOR-P1-005` remains `APPROVED_NOT_INTEGRATED` until canonical promotion
and post-merge readback.

## Exact implementation order

1. **Frontend identity preservation** — retain distinct `ActorId`,
   `ActorInstanceId`, `ActorRuntimeRootOwnerId`, `StateRegionId`, protocol
   binding identities and responsibility digest fields. Parser work is not
   required because R51 adds no source surface.
2. **Checker lifecycle plan** — construct one closed lifecycle plan only after
   protocol binding verification. Reject an identity collision or foreign
   binding before create preparation. Do not infer supervision or restart.
3. **MIR lowering** — emit the existing typed lifecycle-event family in the
   exact creation, normal-stop or Defect-stop order. Preserve state-before,
   state-after, cleanup cardinality, reply terminalization and root-owner
   observation fields.
4. **xVM runtime** — commit publication only after state and mailbox
   initialization; drain normal stops; keep an indefinitely suspended turn
   pending; on uncaught Defect close admission, clean queued payloads, clean the
   active turn and actor state, terminalize the reply snapshot, notify the root
   owner, then publish termination.
5. **Debugger projection** — show the four identity domains separately, display
   only committed events in event order, and distinguish the primary Defect
   from suppressed cleanup defects.
6. **Conformance execution** — bind a target/toolchain/build identity and run
   all direct and mutation cases in
   `tests/conformance/actor-lifecycle-guards-r1.json`. Design-static execution
   alone is not a product receipt.

## Failure and diagnostic boundary

The twelve `ACTOR_LIFECYCLE_*` codes in the guard matrix are internal
design-static verifier guards. They are not public compiler diagnostic registry
IDs. A compiler-facing diagnostic lane is therefore explicitly not applicable
to R51 unless a future source-admission rule exposes one of these conditions to
program text.

## Acceptance

- all five existing direct rejection fixtures return their exact first guard;
- seven deep-copy mutations return the seven previously uncovered exact first
  guards;
- the declared, direct and mutation guard sets form an exact 12-of-12 partition;
- the admitted base fixtures remain unchanged and continue to admit;
- formatter/LSP work is N/A because no source spelling changes;
- runtime, backend, debugger and product execution remain `NOT_RUN` until a
  target-bound receipt exists;
- R24 remains held until R22 is canonically `VERIFIED_CLOSED`.

## Validation commands

```text
py -3.9 -B tools/validators/validate_actor_minimum_lifecycle.py
py -3.9 -B tools/validators/run_actor_lifecycle_guard_mutation_tests.py --root .
py -3.9 -B tools/validators/validate_workspace.py --root .
```
