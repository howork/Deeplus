## Change identity

- Change/RFC/ADR ID:
- Related issue:
- Target revision:

## What changed

Describe the bounded change set and the canonical authorities it touches.

## Why

Explain the problem, accepted decision, and alternatives considered.

## Evidence and validation

- [ ] `python3 tools/validators/validate_workspace.py`
- [ ] `cargo fmt --all -- --check`
- [ ] `cargo check --workspace --locked`
- [ ] `cargo test --workspace --locked`
- [ ] Generated projections were regenerated and checked for drift.

List commands actually run. Leave any unexecuted product lane as `NOT_RUN`.

## Review routing

- Required primary roles: Design_, Spec_, Impl_, Test_, Devel_
- Extra auditors:
- Role review request pack:
- Evidence/report location:

## Evidence boundary

State separately whether this PR establishes design direction, publication
integrity, implementation handoff, conformance evidence, or product support.
