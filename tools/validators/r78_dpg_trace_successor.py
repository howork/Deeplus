"""Shared identity fence for the bounded R78 parser-authority trace successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


REVISION = "r78-dpg-implementation-target-traceability-closure-r1"
CANONICAL_BASELINE = "10e64f492f0529610673846139afcf0d95175663"
LOCAL_PREDECESSOR = "7d4e6c48b9374bec34a60b970530174dd9b4e145"
COUNTS = (3679, 4, 493, 0)
FEATURE_ROWS = 464
STAGE_CELLS = 3248
TEST_OUTCOME_CELLS = 1392
ATOMIC_CELLS = sum(COUNTS)
R101_CONTRACT_REL = (
    "spec/contracts/implementation-target-feature-p1-disposition-r101.json"
)
R101_ACTION_IDS = (
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
)
R101_EXCLUDED_TARGET_FEATURE_IDS = {
    "enum_case_display_mapping_preview_design",
    "enum_declaration_order_ord_preview_design",
    "enum_exact_variant_subset_alias_preview_design",
}
# R83 adds the exact OrdinaryCallSelectionV1 evidence locators.  The R84
# RefinementR0V1 closure, R85 member-visibility omission closure, R86
# strong-comparison coherence closure, R87 Trait auto-policy registry closure,
# R88 SourceItemCommitmentV1, R89 EnumBodyCommitmentV1 /
# MatchFallbackBoundaryV1, R90 actor transport allocation closure, R91
# SenderId identity closure, and R92 XBC projection closure then add their
# canonical artifact, feature, predicate, diagnostic, and acceptance locators.
# R92 deliberately changes one XBC DYNAMIC_LOWERING cell from NOT_APPLICABLE
# to BOUND_DIRECT; all other target-cell dispositions remain unchanged. R99
# adds exact parser/checker/numeric/runtime projection locators. R100 then
# replaces 32 generic historical cells with feature-local property/forwarding
# evidence and classifies two dynamic cells as static-only. R101 then projects
# the exact 22 still-open feature actions onto the first implementation target:
# three unexecuted Enum successor slices are excluded while every retained
# TCC/SFD implementation-acceptance feature remains present.
# Rebuilding the global trace after R103 registers the bounded-list diagnostic
# evidence while preserving the R101/R104 row and cell cardinalities.
# Historical validators
# import this successor count only after first validating the complete current
# trace through is_successor().
EVIDENCE_COUNT = 4627
GITHUB_PUBLICATION = "NOT_PERFORMED_FOR_DPG_TRACE_REPAIR"


def _digest_ids(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode("utf-8")).hexdigest()


def _r101_projection_matches(
    root: Path,
    metadata: dict[str, Any],
    rows: list[dict[str, Any]],
) -> bool:
    contract_path = root / R101_CONTRACT_REL
    if not contract_path.is_file():
        return False
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    actions = contract.get("actions", [])
    action_ids = [row.get("id") for row in actions]
    if action_ids != list(R101_ACTION_IDS):
        return False
    if any(
        row.get("action_status") != "OPEN"
        or row.get("execution_receipt_gate") != "OPEN_NOT_RUN"
        or row.get("product_execution") != "NOT_RUN"
        for row in actions
    ):
        return False

    excluded_mapping: dict[str, list[str]] = {}
    retained_ids: set[str] = set()
    tcc_sfd_retained_ids: set[str] = set()
    for row in actions:
        action_id = row["id"]
        retained = row.get("retained_feature_ids", [])
        retained_ids.update(retained)
        if action_id.startswith(("TCC-P1-", "SFD-P1-")):
            tcc_sfd_retained_ids.update(retained)
        for feature_id in row.get("excluded_target_feature_ids", []):
            excluded_mapping.setdefault(feature_id, []).append(action_id)

    target_ids = {row.get("feature_id") for row in rows}
    if set(excluded_mapping) != R101_EXCLUDED_TARGET_FEATURE_IDS:
        return False
    if R101_EXCLUDED_TARGET_FEATURE_IDS & target_ids:
        return False
    if not retained_ids <= target_ids:
        return False

    retained_list = sorted(retained_ids)
    tcc_sfd_list = sorted(tcc_sfd_retained_ids)
    expected_projection = {
        "contract_path": R101_CONTRACT_REL,
        "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        "exact_action_ids": list(R101_ACTION_IDS),
        "action_count": 22,
        "design_open_in_target_count": 0,
        "execution_open_action_count": 22,
        "excluded_target_feature_mapping": excluded_mapping,
        "retained_feature_ids": retained_list,
        "retained_feature_id_list_sha256": _digest_ids(retained_list),
        "tcc_sfd_retained_feature_ids": tcc_sfd_list,
        "tcc_sfd_retained_feature_id_list_sha256": _digest_ids(tcc_sfd_list),
    }
    summary = contract.get("summary", {})
    governance = contract.get("governance", {})
    return (
        metadata.get("governance", {}).get("r101_feature_p1_disposition")
        == expected_projection
        and summary.get("exact_action_count") == 22
        and summary.get("first_target_design_open_action_count") == 0
        and summary.get("open_execution_receipt_count") == 22
        and governance.get("semantic_p0") == 0
        and governance.get("feature_p1") == "22_OPEN_UNCHANGED"
        and governance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and governance.get("production_implementation") == "NOT_RUN"
    )


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
        and metadata.get("target_count") == FEATURE_ROWS
        and metadata.get("excluded_count") == 259
        and metadata.get("derived_counts", {}).get("feature_rows") == FEATURE_ROWS
        and metadata.get("derived_counts", {}).get("stage_cells") == STAGE_CELLS
        and metadata.get("derived_counts", {}).get("test_outcome_cells")
        == TEST_OUTCOME_CELLS
        and (
            metadata.get("derived_counts", {}).get("bound_direct_cells"),
            metadata.get("derived_counts", {}).get("bound_delegated_cells"),
            metadata.get("derived_counts", {}).get("not_applicable_cells"),
            metadata.get("derived_counts", {}).get("applicable_blocked_cells"),
        ) == COUNTS
        and metadata.get("derived_counts", {}).get("product_not_run_rows")
        == FEATURE_ROWS
        and set(metadata.get("excluded_current_feature_reasons", {}))
        == {
            "affine_unit_profile_msp",
            "arbitrary_generator_stdlib_profile",
            "trait_binding_failable_v1",
            *R101_EXCLUDED_TARGET_FEATURE_IDS,
        }
    )
    if not identity_matches:
        return False
    if root is None or rows is None:
        return True

    if not _r101_projection_matches(root, metadata, rows):
        return False

    # Historical closure validators may accept the bounded current successor,
    # but they must not turn that exception into a blanket non-target-row bypass.
    # Reuse the current trace validator against the in-memory rows so mutation
    # suites still reject every change outside R78's exact parser-authority
    # rebind.
    from validate_implementation_target_traceability import validate

    return not validate(root, metadata, rows)
