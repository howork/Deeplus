# Source-Item Contextual Declaration Commitment Closure R1

Status: `LOCAL_VERIFIED_DESIGN_CANDIDATE`
Audit gap: `IR-PARSE-P1-058`
Product support: `15/15 NOT_RUN`

## Decision

The source role and activation profile are selected before parsing. At every
source-item boundary the parser takes one lossless checkpoint and runs the
closed `SourceItemCommitmentV1` table. Contextual words remain ordinary
identifiers until one row reaches its structural commitment marker. The probe
uses tokens, attachment, balanced delimiters and the DPG type parser only; name
resolution, symbol lookup, type lookup and overload selection are forbidden.

Before a marker, failure consumes zero tokens and a script root may parse the
same input as a statement. Library and executable roots retain their existing
top-level statement rejection. After a marker, the declaration owner is final:
a later header or body error cannot fall back to an expression or to a
parenless trailing-closure call.

This gives declarations precedence for intentionally declaration-shaped text.
For example, source-initial `actor Worker { ... }` is an actor declaration.
Calling a value named `actor` at the same boundary uses the unambiguous
parenthesized form `actor(Worker) { ... }`. The parser never consults whether a
binding named `actor` exists.

An optional top-level visibility word participates in the same transaction and
commits only with a declaration row. A parsed annotation is different: it
already selects `AnnotatedItem`, so failure to find an annotatable declaration
emits `ANNOTATION_TARGET_REQUIRED` and never becomes a statement.

The table covers every current contextual source-declaration family, including
the two Preview FFI families. Hard-keyword declaration starters continue to
commit immediately and are not duplicated as contextual rows. Member bodies
remain governed by their closed owner member sets; this cluster does not invent
a member-item ambiguity or change the DPG surface.

The lossless CST records the selected row and commitment span for recovery and
tooling. The normalized AST contains only the selected declaration or statement
owner. No HIR, MIR, xVM, runtime or backend operation is added.

This closes the parser-owner ambiguity as a local design candidate. It creates
no feature P1, changes none of the existing 22 OPEN feature P1 items, and does
not claim production parser, formatter or LSP execution.
