"""Shared identity fence for the bounded R78 parser-authority trace successor."""

from __future__ import annotations

from pathlib import Path
from typing import Any


REVISION = "r78-dpg-implementation-target-traceability-closure-r1"
CANONICAL_BASELINE = "10e64f492f0529610673846139afcf0d95175663"
LOCAL_PREDECESSOR = "7d4e6c48b9374bec34a60b970530174dd9b4e145"
COUNTS = (3712, 4, 505, 0)
# R83 adds the exact OrdinaryCallSelectionV1 evidence locators.  The R84
# RefinementR0V1 closure, R85 member-visibility omission closure, R86
# strong-comparison coherence closure, R87 Trait auto-policy registry closure,
# and R88 SourceItemCommitmentV1 then add their canonical artifact, feature,
# predicate, diagnostic, and acceptance locators without changing the R78
# target-cell partition. Historical validators
# import this successor count only after first validating the complete current
# trace through is_successor().
EVIDENCE_COUNT = 4504
GITHUB_PUBLICATION = "NOT_PERFORMED_FOR_DPG_TRACE_REPAIR"


def is_successor(
    metadata: dict[str, Any],
    *,
    root: Path | None = None,
    rows: list[dict[str, Any]] | None = None,
) -> bool:
    source = metadata.get("source_grammar_authority", {})
    governance = metadata.get("governance", {})
    identity_matches = (
        metadata.get("revision") == REVISION
        and metadata.get("canonical_baseline_commit") == CANONICAL_BASELINE
        and metadata.get("local_predecessor_commit") == LOCAL_PREDECESSOR
        and source.get("contract")
        == "spec/contracts/parser-authority-traceability-r1.json"
        and source.get("authority_axes")
        == ["structural_grammar", "parser_context", "pratt", "scanner"]
        and source.get("surface_census_semantic_authority") is False
        and source.get("direct_cell_requires_all_authority_axes") is True
        and source.get("ebnf_only_binding_rejected") is True
        and governance.get("semantic_p0") == 0
        and governance.get("feature_p1") == "22_OPEN_UNCHANGED"
        and governance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and governance.get("github_publication") == GITHUB_PUBLICATION
    )
    if not identity_matches:
        return False
    if root is None or rows is None:
        return True

    # Historical closure validators may accept the bounded R78 successor, but
    # they must not turn that exception into a blanket non-target-row bypass.
    # Reuse the current trace validator against the in-memory rows so mutation
    # suites still reject every change outside R78's exact parser-authority
    # rebind.
    from validate_implementation_target_traceability import validate

    return not validate(root, metadata, rows)
