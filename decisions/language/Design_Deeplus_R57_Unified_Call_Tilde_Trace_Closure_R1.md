# Deeplus R57 Unified Call and Tilde Trace Closure

## Decision

`APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE`

R57 closes the implementation-readiness trace cells for the dependency-closed
unified-call slice without activating source, running a product implementation,
or publishing to GitHub. The baseline GitHub main remains
`39a5d50cc770341c4b9776d00d84520b780d0c62`; the local predecessor is
`808bf7cd1d28bba737e0744a6f120c71297d7ddd`.

## Exact scope

The exact transitive feature closure is:

1. `unified_call_expression_and_tilde_modes`;
2. `data_shaping_callshape_model`;
3. `actor_protocol_family`;
4. `actor_declaration_grammar_closed`.

The unified-call catalog dependency edges to the call-shape and actor-protocol
features are now represented in the normalized dependency registry. Actor
Protocol retains its existing dependency on the closed Actor declaration
grammar.

The predecessor had exactly ten `IR-XCUT-P1-054` cells in this closure. R57
transitions one static-semantics cell through the new catalog-bound
`UnifiedCallModeAdmitted` predicate, eight cells through direct structured
evidence, and the Actor declaration rejection cell by delegation to the already
bound `actor_mailbox_capacity` rejection owner. The post-R57 totals are:

- direct: 2,438;
- delegated: 2;
- not applicable: 500;
- blocked: 1,281;
- missing/conflict: 0/0.

## Unified static contract

All invocation surfaces normalize to one `CallExpr`. `CallMode` is exactly
`Ordinary`, `Message`, or `ActorMessage`. AST preserves six explicit argument
kinds and a source-structure trailing-closure array; canonical HIR carries the
same runtime order in one seven-kind argument array by appending
`TRAILING_CLOSURE` entries. No message payload aggregate or Tuple/Record
payload-to-formal projection exists.

`~` remains rank-15 left associative. `:~` remains rank-15 terminal and
nonassociative. Static resolution selects a finite mode-owned candidate domain,
rejects structural shape defects, binds channels, ranks fixed arity before
repeated positional before named rest, requires exactly one winner, and closes
type, ownership, effect, error, isolation, authority and cleanup responsibility
before sealing `CallPlan`. Expected result type, source/import order, runtime
strings, MIR and backend lookup do not choose the winner.

## Evaluation and lowering

After static preflight, evaluation is:

1. callee or receiver;
2. explicit runtime arguments left-to-right once;
3. trailing-closure environments left-to-right once;
4. omitted defaults in formal declaration order;
5. zero-evaluation witness bindings;
6. ownership/admission commit.

Preparation failure invokes and publishes nothing, retains uncommitted owners,
and cleans the prepared prefix in reverse acquisition order exactly once.

The ten existing `HM-LR-CALL-001..010` rows remain the complete current call
lowering table. R57 corrects `HM-LR-CALL-010`: actor `:~` is immediate admission,
not a suspension point. Admission rejection is a `Result::err` on normal
expression flow. The row therefore has `NORMAL`, `DEFECT`, and `CANCELLATION`
successors, `suspension_effect = NONE`, and no unconditional reply token. A
one-way send creates no reply identity; a request creates reply/correlation
identity only on successful admission commit, and waiting is the existing
separate one-shot explicit `await` path.

## Diagnostics and acceptance

`UnifiedCallModeAdmitted` owns one deterministic primary diagnostic,
`TILDE_CALL_COMMA_REQUIRES_GROUPING`, and three secondary diagnostics:
terminal ActorMessage chaining, actor operation reached through `~`, and
same-shape `on`/`request` collision. `ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER`
remains owned by `SingleActionDeferAdmitted`; it is not duplicated here.

The R57 contract freezes fifteen normal, boundary, and rejection examples. The
focused validator passes, and all 23 bounded mutations are rejected. These are
E2 structured-static receipts only. Parser, checker, MIR, runtime, formatter,
LSP and independent product execution remain `NOT_RUN`.

## Preserved governance

- semantic P0: 0;
- feature P1: exactly 22 OPEN;
- M13 actions: exactly 4 OPEN;
- product lanes: 15/15 `NOT_RUN`;
- source activation: none;
- new AST/HIR/MIR identities: 0/0/0;
- GitHub publication: `SUSPENDED`.

`RCTS_RESPONSIBILITY_COMBINATION_INVALID` remains a separate catalog-quality
observation and is not expanded into this bounded cluster. Actor mailbox,
request/reply, cancellation and delivery contracts are referenced but not
redefined or claimed closed by R57.
