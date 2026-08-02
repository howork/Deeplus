# Deeplus Loan-Close Operation Decision R1

Status: `CURRENT_DESIGN_STATIC_CONTRACT_LOCAL_CANDIDATE`

Gap: `IR-OWN-P1-022`
Baseline: `howork/Deeplus main@4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44`

## Decision

Deeplus keeps loan closing implicit in source and explicit in MIR. The existing
`LOAN_BEGIN_SHARED`, `LOAN_BEGIN_EXCLUSIVE`, `LOAN_BEGIN_REBORROW`, `LOAN_END`,
and linear `ACCESS(LoanId)` identities are sufficient. No source spelling,
HIR expression kind, MIR opcode, runtime-observable event, or token kind is
added.

Each MIR loan-table row now identifies its optional parent, its unique static
begin operation, and its nonempty canonical set of static end operations. The
lowerer derives the earliest legal close frontier from verified uses, region
constraints, child loans, and CFG exits. Every dynamic begin crosses exactly
one end on every reachable normal, Error, Defect, Cancellation, and early-exit
path. Multiple static end sites are legal only on mutually exclusive paths.

`LOAN_END` is infallible and nonsuspending. It consumes only the matching
ACCESS token, invalidates the activation's borrowed/inout views, and discharges
ViewRelease. It performs no user cleanup and cannot change primary/suppressed
failure order. Child loans close leaf-first; owner mutation, move, replacement,
cleanup, region exit, or an unadmitted suspension cannot occur with an
overlapping live loan.

The same static loan site may execute repeatedly in a loop. Each iteration is
a distinct dynamic activation, and every backedge must see the site inactive.
No dynamic activation identity becomes source or module-API residue.

## Examples

```deeplus
public def first(values: List<Int>) -> Int = {
    let view = borrow values
    let value = view[1]
    return value
}
```

The shared loan ends after the final `view` use and before the return leaves
the region.

```deeplus
public def#async firstThenWait(values: List<Int>) -> Int = {
    let view = borrow values
    let value = view[1]
    await tick()
    return value
}
```

The ordinary loan ends before `await`; the copied `value` remains live.

```deeplus
public def#async invalid(values: List<Int>) -> Int = {
    let view = borrow values
    await tick()
    return view[1]
}
```

This is rejected by the existing source-level borrow/suspension rule. It does
not reach MIR as an unbalanced loan.

```deeplus
public def nested(values: List<Int>) -> Int = {
    let outer = borrow values
    let inner = borrow outer
    let value = inner[1]
    return value
}
```

The inner loan ends first, resumes the outer loan, and the outer loan then
ends. Reversing or omitting either close fails with the internal verifier
identity `MIR_LOAN_UNBALANCED`.

## Evidence boundary

The R34 fixtures and validator execute design-static path and mutation checks.
They do not execute a Deeplus parser, checker, MIR lowerer, xVM, Cranelift,
formatter, or LSP. Semantic P0 stays `0`, the exact 22 feature P1 items and
four separate actions stay OPEN, and all 15 product lanes stay `NOT_RUN`.
GitHub publication is outside this local candidate.

## R47 exact-order local fusion

The predecessor baseline recorded above remains immutable provenance. R47
replayed this contract onto local R46 base
`87115776365fcbe8870d2f631050db3e23194c9b` in the exact dependency order
R29 → R30 → R31 → R32 → R33 → R34 → R35, then rebound R46 as
R38 → R36 → R37. Its local state is `APPROVED_NOT_INTEGRATED`; canonical and
GitHub mutation counts are zero, and product support remains `15/15 NOT_RUN`.
