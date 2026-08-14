# Deeplus String Interpolation Format Spec Core R1

Status: `LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED`
Baseline: `10e64f492f0529610673846139afcf0d95175663`
Feature: `string_interpolation_format_spec_core`

## Decision

The Stable format core is deliberately small: `${expr:format}` accepts
`Align? Width`, where `Align` is `<`, `>` or `^` and `Width` is a canonical
decimal integer from 1 through 1,000,000. An omitted alignment means left
alignment. The only fill scalar is U+0020 SPACE.

Width counts Unicode scalar values. This is deterministic under Deeplus's
existing String value model and does not import a Unicode-version-dependent
grapheme or terminal-column algorithm. Width is a minimum, never a truncation
request. For center alignment, the left pad receives `floor(deficit / 2)` and
the right pad receives the remainder.

The scanner continues to emit one opaque `INTERPOLATION_FORMAT_TEXT` token.
The DPG therefore remains a structural grammar; the checker parses the bounded
inner format language. Invalid text is rejected before canonical HIR with
`INTERPOLATION_FORMAT_SPEC_INVALID`.

## Evaluation and lowering

The hole expression is evaluated once. A String hole is used directly; a
non-String hole invokes its already-selected `Display` witness exactly once.
Interpolation-owned padding is then applied to the resulting String segment.
The format plan is not passed to `Display`. It grants
no locale, provider, serialization, reflection, redaction or ABI authority.
The padded segment participates in the existing transactional String builder,
including final publication and reverse cleanup on an earlier failure.

## Alternatives rejected

- Arbitrary fill, precision, sign, radix and type codes would create a second
  formatting protocol before its responsibilities exist.
- Grapheme or display-column width would require a versioned segmentation or
  terminal-width authority that current Deeplus does not expose.
- Truncation is lossy and is left to explicit String APIs.
- Delegating the format string to `Display` would make behavior witness-specific
  and defeat deterministic HIR/MIR lowering.

## Evidence fence

This closes a design/static handoff gap only. Production parser, checker, xVM,
Cranelift, formatter and LSP execution remain `NOT_RUN`; all 22 feature P1s and
all 15 product lanes retain their current states.
