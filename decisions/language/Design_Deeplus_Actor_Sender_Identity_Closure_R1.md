# Deeplus Actor Sender Identity Closure R1

Status: `LOCAL_STABLE_DESIGN_CANDIDATE_NOT_INTEGRATED`

Gap: `IR-ACTOR-P1-061`

## Decision

`SenderId` is a non-forgeable, runtime-internal tagged identity with exactly two
variants:

- `Actor(ActorInstanceId)` while an actor turn authority is active; and
- `Execution(ExecutionId)` otherwise.

The actor variant has precedence only while the current execution context owns
the actor turn token. A structured child execution does not inherit that token
and therefore uses its own `ExecutionId`. An inline awaited async invocation
continues in the caller's execution/actor-turn context.

Suspend/resume preserves the selected origin identity. Actor restart creates a
new `ActorInstanceId` and therefore a new `SenderId`; child spawn creates a new
`ExecutionId` and therefore a new execution sender. A queued message retains the
immutable sender value even after the originating actor incarnation or execution
terminates. The value grants no actor, task or mailbox authority.

`SenderId` is not a source type, `ActorId`, `ActorTurnId`, thread ID, address,
timestamp, hash truncation, serialization tag, ABI identity or debugger-created
surrogate. The send operation performs no identity allocation or lookup. It
projects the already installed current actor-instance or execution identity
through one statically sealed `ActorSenderIdentityPlanV1`.

## Ordering consequence

`ChannelId` remains an injective derivation of the exact tagged
`(SenderId, ReceiverActorId, MailboxProfileId)` tuple. Actor sends across turns
of one incarnation share a sender key; restart starts a distinct key. Execution
suspension preserves a key; a structured child has a distinct key. FIFO remains
per exact channel only and does not imply cross-sender order or fairness.

## Evidence boundary

This decision closes design identity and lifetime only. Parser, checker, MIR,
xVM, runtime, Cranelift and tooling execution remain `NOT_RUN`. Semantic P0 is
0, the exact 22 feature P1 set is unchanged, and no GitHub mutation is performed.
