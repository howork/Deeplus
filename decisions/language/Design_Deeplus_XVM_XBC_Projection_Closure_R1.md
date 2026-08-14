# Deeplus xVM XBC Projection Closure R1

## Verdict

`APPROVED_NOT_INTEGRATED` for the design-static closure of
`IR-XVM-P1-062`. This decision defines the first canonical XBC projection and
verifier contract. It does not implement the emitter or interpreter and does
not change any product lane from `NOT_RUN`.

## Authority boundary

Deeplus MIR remains the sole execution-semantic authority. XBC is a
deterministic, target-bound execution projection of one already verified
`deeplus.mir/r1` module. It cannot add an operation, repair malformed MIR,
reselect a witness or helper, infer ownership, choose a cleanup path, invent a
safepoint, or turn a target slot or address into semantic identity.

The noncanonical MIR-X1/xVM-only RFC is retained only as historical design
evidence. This closure preserves the current architecture: the xVM XBC path,
Cranelift ObjectModule AOT, and Cranelift JITModule all project the same
verified MIR and must preserve the same observable trace.

## Container

XBC R1 uses a fixed 128-byte little-endian header followed by ten fixed-order
directory entries and ten contiguous section payloads. The magic is
`DPXBC\0\r\n` (`4450584243000d0a`), the version is `1.0`, and every flag and
reserved field is zero. Each 56-byte directory row binds the section kind,
ordinal, offset, length, and SHA-256 of its raw payload.

Every section payload is RFC 8949 deterministic CBOR with definite lengths,
shortest integer and length encodings, canonical map-key order, and exact
decode/re-encode byte equality. The ten sections are:

1. `MODULE_DESCRIPTOR`
2. `TYPE_TABLE`
3. `STATIC_IDENTITY_TABLE`
4. `RESPONSIBILITY_EVIDENCE_TABLE`
5. `CONSTANT_TABLE`
6. `CLOSURE_ENVIRONMENT_PLAN_TABLE`
7. `BODY_TABLE`
8. `MANAGED_MEMORY_PLAN`
9. `CONTINUATION_INTERFACE`
10. `DEBUG_PROVENANCE`

An absent optional capability is represented by a present section carrying a
closed `present=false` record. Unknown, duplicate, omitted, reordered,
overlapping, gapped, or trailing sections are rejected.

## Instruction and frame model

The 48 MIR operation kinds receive opcodes `0x0000` through `0x002f` in the
exact machine-registry order. The 17 terminators receive `0x8000` through
`0x8010`. All other opcode values are invalid in XBC R1. A changed machine
registry digest is unsupported until a decoder explicitly advertises the new
binding; it is never interpreted by ordinal coincidence.

Each body keeps disjoint dense namespaces for values, places, linear tokens,
continuation-frame slots, blocks, types, constants, static identities, and
responsibility evidence. Ordinals are derived from the corresponding exact
verified-MIR table order. They are not byte offsets, addresses, ABI identities,
or serialization tags. Every block contains its operations followed by exactly
one terminator. Branches name block ordinals rather than byte offsets.

The instruction payload is the exact machine-registry payload after every MIR
identity reference is replaced by its typed ordinal reference. The verifier
reconstructs the logical MIR projection, checks the exact source MIR semantic
digest, and reruns the applicable MIR validity obligations before execution.

## Roots, suspension, and runtime ABI

Managed roots bind exact `RootId` values to typed xVM locations. The mapping is
bijective for the active root map; a static XBC artifact contains no handle
generation, raw referent address, native stack offset, or collector timing.
Runtime root receipts supply the exact generation at a may-collect entry.

Continuation slots preserve the exact continuation-interface identity and
digest, owner/loan/cleanup/authority partition, root-rebind law, and
resume-or-cancel single-winner law. XBC cannot synthesize a slot absent from the
verified continuation plan or merge distinct semantic slots.

The module descriptor binds the exact internal runtime ABI and the explicit
`deeplus-xvm-portable-r1` projection. Host defaults cannot fill any missing
field. A helper is callable only through the already sealed typed helper-table
binding.

## Verification and evidence

The xVM must decode and fully verify the artifact before the first operation is
executed or any runtime resource is acquired. Failure preserves the source MIR
and emits one deterministic verifier diagnostic. No source fix-it exists.

The artifact receipt binds the contract, XBC schema, source MIR semantic
digest, MIR schema and machine-registry digests, runtime-ABI projection digest,
managed-memory and continuation digests where applicable, logical XBC digest,
and full encoded-byte SHA-256.

Static schema, fixture, and mutation validation establishes only a design
handoff. The xVM emitter, interpreter, Cranelift paths, cross-backend
conformance, and all other product lanes remain `NOT_RUN`.
