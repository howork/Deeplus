#!/usr/bin/env python3
"""Validate the bounded R60 pattern-match ownership-split trace closure."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/pattern-match-ownership-split-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/pattern-match-ownership-split-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/pattern-match-ownership-split-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/pattern-match-ownership-split-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
HM_REL = "spec/contracts/hir-mir-lowering-registry.json"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "e120f83db380ee182f0117713a67e97886bfcd11"
FEATURE = "pattern_match_ownership_split"
TARGET_CELLS = {
    (FEATURE, "STATIC_SEMANTICS", None),
    (FEATURE, "DYNAMIC_LOWERING", None),
}
EXCLUDED_FEATURES = ["clause_pattern_heads", "match_exhaustiveness_phase_a"]
PRIOR_OVERLAYS = [
    "spec/traceability/implementation-target-profile-r1/scalar-numeric-fixed-operator-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/pattern-dynamic-lowering-evidence-r1.json",
]
RULE_IDS = [f"PMOSTC-R{index:03d}" for index in range(1, 15)]
CASE_IDS = [f"PMOSTC-AC-{index:03d}" for index in range(1, 13)]
CASE_EXPECTATIONS = [
    ("POSITIVE", "ADMIT_ONE_FINAL_PLACE_MOVE", None),
    ("POSITIVE", "ADMIT_SHARED_LOAN_AT_FINAL_COMMIT", None),
    ("POSITIVE", "ADMIT_SAME_SUBJECT_SHARED_ALIAS", None),
    ("BOUNDARY", "MISMATCH_WITH_ZERO_RESIDUE", None),
    ("BOUNDARY", "FALSE_GUARD_WITH_ZERO_RESIDUE", None),
    ("BOUNDARY", "JOIN_BY_CAPABILITY_INTERSECTION", None),
    ("BOUNDARY", "PREPARATION_ABORT_REVERSE_MOVE_CANCEL_WITH_ZERO_RESIDUE", None),
    ("REJECT", "REJECT_BEFORE_COMMIT", "PATTERN_BORROWED_MATCH_CANNOT_MOVE_PAYLOAD"),
    ("REJECT", "REJECT_BEFORE_COMMIT", "ALIAS_PATTERN_OWNERSHIP_CONFLICT"),
    ("REJECT", "REJECT_OR_INTERFACE_BEFORE_BRANCH_SELECTION", "OR_PATTERN_BINDINGS_INCONSISTENT"),
    ("REJECT", "REJECT_RETURNING_PLACE_JOIN", "PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH"),
    ("REJECT", "REJECT_GUARD_BEFORE_LOWERING", "MATCH_GUARD_CONSUME_NOT_ALLOWED"),
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def collect_operation_kinds(value: Any, output: set[str]) -> None:
    if isinstance(value, dict):
        kind = value.get("operation_kind")
        if isinstance(kind, str):
            output.add(kind)
        for child in value.values():
            collect_operation_kinds(child, output)
    elif isinstance(value, list):
        for child in value:
            collect_operation_kinds(child, output)


def trace_cells(
    rows: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str, str | None], dict[str, Any]], int]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        feature = row.get("feature_id")
        for stage in row.get("stages", []):
            stage_name = stage.get("stage")
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                key = (feature, stage_name, outcome)
                duplicates += key in cells
                cells[key] = cell
    return cells, duplicates


def disposition_counts(values: dict[tuple[str, str, str | None], str]) -> tuple[int, int, int, int]:
    counts = Counter(values.values())
    return tuple(
        counts[key]
        for key in (
            "BOUND_DIRECT",
            "BOUND_DELEGATED",
            "NOT_APPLICABLE",
            "APPLICABLE_BLOCKED_BY_GAP",
        )
    )


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    *,
    validate_schema: bool = True,
    trace_rows_override: list[dict[str, Any]] | None = None,
    hm_registry_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    if validate_schema:
        try:
            import jsonschema

            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(load(root / OVERLAY_SCHEMA_REL)).validate(overlay)
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"JSON_SCHEMA:{exc}")

    for value, prefix in ((contract, "CONTRACT"), (overlay, "OVERLAY")):
        require(value.get("canonical_baseline_commit") == BASELINE, f"{prefix}_BASELINE")
        require(value.get("local_predecessor_commit") == PREDECESSOR, f"{prefix}_PREDECESSOR")
        require(value.get("feature_ids") == [FEATURE], f"{prefix}_FEATURE_EXACT")
        require(value.get("revision") == "r60-local-pattern-match-ownership-split-trace-closure-r1", f"{prefix}_REVISION")

    require(contract.get("schema") == "deeplus.pattern-match-ownership-split-trace-closure/r1", "CONTRACT_SCHEMA_ID")
    require(contract.get("candidate_status") == "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE", "CONTRACT_STATUS")
    require(contract.get("language_status") == "STABLE_DESIGN", "CONTRACT_LANGUAGE_STATUS")
    require(contract.get("source_activation") == "none" and contract.get("current_binding") is False, "CONTRACT_NONACTIVATING")
    require(overlay.get("schema") == "deeplus.pattern-match-ownership-split-evidence/r1", "OVERLAY_SCHEMA_ID")
    require(overlay.get("candidate_status") == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY", "OVERLAY_STATUS")

    expected_transitions = [
        {
            "feature_id": FEATURE,
            "stage": stage,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": "BOUND_DIRECT",
        }
        for stage in ("STATIC_SEMANTICS", "DYNAMIC_LOWERING")
    ]
    scope = contract.get("scope_fence", {})
    require(scope.get("transitioned_cells") == expected_transitions, "SCOPE_EXACT_TWO_CELLS")
    require(scope.get("excluded_reverse_dependents") == EXCLUDED_FEATURES, "SCOPE_EXACT_REVERSE_DEPENDENTS")
    require(
        all(
            scope.get(key) == 0
            for key in (
                "excluded_reverse_dependent_transition_count",
                "preview_pattern_row_transition_count",
                "other_target_cell_transition_count",
            )
        ),
        "SCOPE_ZERO_OTHER_TRANSITIONS",
    )

    operation_alignment = contract.get("existing_operation_alignment", {})
    admitted_operations = [
        "MOVE_RESERVE",
        "MOVE_CANCEL",
        "PLACE_MOVE",
        "LOAN_BEGIN_SHARED",
        "LOAN_BEGIN_EXCLUSIVE",
        "LOAN_BEGIN_REBORROW",
        "LOAN_END",
        "BINDING_COMMIT",
    ]
    require(operation_alignment.get("new_operation_count") == 0, "OPERATIONS_ZERO_NEW")
    require(operation_alignment.get("admitted_operations") == admitted_operations, "OPERATIONS_EXACT_EXISTING_SET")
    require(
        [operation_alignment.get(key) for key in ("pattern_attempt_row_id", "move_pattern_row_id", "or_pattern_row_id", "alias_pattern_row_id")]
        == ["HM-LR-TOP-016", "HM-LR-PAT-029", "HM-LR-PAT-027", "HM-LR-PAT-028"],
        "OPERATIONS_EXACT_PATTERN_ROWS",
    )
    hm = hm_registry_override or load(root / HM_REL)
    operation_kinds: set[str] = set()
    collect_operation_kinds(hm, operation_kinds)
    require(set(admitted_operations) <= operation_kinds, "OPERATIONS_EXIST_IN_HM_REGISTRY")
    hm_ids = {row.get("row_id") for row in hm.get("rows", [])}
    require(
        {"HM-LR-TOP-016", "HM-LR-PAT-029", "HM-LR-PAT-027", "HM-LR-PAT-028"} <= hm_ids,
        "OPERATIONS_PATTERN_ROWS_EXIST",
    )

    ownership = contract.get("ownership_interface", {})
    require(ownership.get("binding_modes") == ["BORROWED", "OWNED"], "OWNERSHIP_BINDING_MODES")
    require(
        ownership.get("normalized_binder_interface_fields")
        == ["binder_name", "binder_type", "ownership_mode", "mutability", "usable_region", "capability_set"],
        "OWNERSHIP_NORMALIZED_INTERFACE",
    )
    require(ownership.get("excluded_interface_fields") == ["projection_path", "source_order"], "OWNERSHIP_EXCLUDED_INTERFACE_FIELDS")
    require(
        ownership.get("borrowed_binding")
        == {"probe_consumption": "NONE", "final_commit_effect": "ACQUIRE_SHARED_LOAN", "move_count": 0},
        "OWNERSHIP_BORROWED_EXACT",
    )
    require(
        ownership.get("owned_binding")
        == {"probe_consumption": "NONE", "preparation": "MOVE_RESERVE", "final_commit_effect": "PLACE_MOVE", "move_count_on_success": 1},
        "OWNERSHIP_OWNED_EXACT",
    )

    law = contract.get("probe_guard_commit_law", {})
    require(law.get("subject_evaluation_count") == 1, "LAW_SUBJECT_ONCE")
    require(
        law.get("structural_probe")
        == {"purity": "PURE", "consumption": "NONCONSUMING", "suspension": "NONE", "acquisition_count": 0, "publication_count": 0},
        "LAW_PROBE_ZERO_ACQUISITION_PUBLICATION",
    )
    require(
        law.get("guard")
        == {
            "required_result_type": "Bool",
            "purity": "PURE",
            "consumption": "NONCONSUMING",
            "suspension": "NONE",
            "mutation_count": 0,
            "acquisition_count": 0,
            "evaluation_count_on_structural_success": 1,
            "evaluation_count_on_structural_failure": 0,
            "ownership_publication_count": 0,
        },
        "LAW_GUARD_READ_ONLY_NONESCAPING_ZERO_ACQUISITION",
    )
    require(
        law.get("final_commit")
        == {
            "logical_commit_count_on_success": 1,
            "atomic": True,
            "fallibility": "INFALLIBLE_AFTER_PREPARATION",
            "timing": "AFTER_STRUCTURAL_AND_GUARD_SUCCESS",
            "pending_acquisition_order": "SOURCE_PATTERN_PREORDER",
            "operation_order": [
                "MOVE_RESERVE",
                "PLACE_MOVE_OR_LOAN_BEGIN_SHARED_OR_LOAN_BEGIN_EXCLUSIVE",
                "BINDING_COMMIT",
            ],
        },
        "LAW_ONE_INFALLIBLE_ORDERED_GROUP_COMMIT",
    )
    require(
        law.get("preparation_abort")
        == {
            "operation": "MOVE_CANCEL",
            "required_on_structural_mismatch_or_false_guard": False,
            "required_on_preparation_failure": True,
            "reverse_acquisition_order": True,
        },
        "LAW_REVERSE_MOVE_CANCEL",
    )
    require(
        law.get("failure_residue")
        == {"binding_count": 0, "move_count": 0, "loan_count": 0, "view_count": 0, "authority_count": 0, "reservation_count": 0},
        "LAW_ZERO_FAILURE_RESIDUE",
    )

    or_alias = contract.get("or_alias_ownership_law", {})
    require(
        or_alias.get("or_pattern")
        == {
            "required_branch_contract": "EXACT_EQUAL_NORMALIZED_BINDER_INTERFACE",
            "selection": "FIRST_SOURCE_ORDERED_SUCCESSFUL_BRANCH",
            "backtracking_count": 0,
            "retry_count": 0,
            "later_branch_probe_after_success_count": 0,
        },
        "LAW_OR_EXACT_INTERFACE_SOURCE_FIRST_NO_RETRY",
    )
    require(
        or_alias.get("alias_pattern")
        == {
            "alias_mode": "SHARED_LOAN_OF_SAME_SUBJECT",
            "clone_count": 0,
            "conflicts_with_moved_descendant": True,
            "conflicts_with_exclusive_borrow_descendant": True,
            "loan_acquisition": "FINAL_ATOMIC_COMMIT_ONLY",
        },
        "LAW_ALIAS_SAME_SUBJECT_NO_CLONE_CONFLICTS",
    )
    require(
        contract.get("loan_lifetime_and_arm_join_law")
        == {
            "loan_end_frontier": "EARLIEST_OWNER_MUTATION_MOVE_REPLACEMENT_CLEANUP_OR_REGION_FRONTIER",
            "returning_arm_join": {
                "required_place_identity": "COMPATIBLE",
                "required_place_state": "COMPATIBLE",
                "result_capabilities": "INTERSECTION",
                "divergent_place_contract": "EXCLUDED_FROM_R60",
            },
        },
        "LAW_LOAN_END_AND_RETURN_JOIN_EXACT",
    )

    rules = contract.get("rules", [])
    require([row.get("rule_id") for row in rules] == RULE_IDS, "RULE_IDS_EXACT_14")
    require(all(isinstance(row.get("text"), str) and row.get("text") for row in rules), "RULE_TEXTS_NONEMPTY")
    cases = contract.get("acceptance_cases", [])
    require([row.get("case_id") for row in cases] == CASE_IDS, "CASE_IDS_EXACT_12")
    require(
        [(row.get("class"), row.get("expected"), row.get("diagnostic_or_null")) for row in cases] == CASE_EXPECTATIONS,
        "CASE_SEMANTICS_EXACT_12",
    )
    require(all(row.get("feature_id") == FEATURE for row in cases), "CASE_FEATURE_EXACT")
    require(all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in cases), "CASE_NOT_RUN")
    require(
        contract.get("acceptance_bindings")
        == {
            FEATURE: {
                "POSITIVE": CASE_IDS[:3],
                "BOUNDARY": CASE_IDS[3:7],
                "REJECT": CASE_IDS[7:],
            }
        },
        "CASE_BINDINGS_EXACT_3_4_5",
    )

    entries = overlay.get("evidence_entries", [])
    entry_by_key = {row.get("evidence_key"): row for row in entries}
    expected_entries = {
        "R60:pattern_match_ownership_split:STATIC_SEMANTICS:STRUCTURAL": ("PMOSTC-R002", "STATIC_SEMANTICS"),
        "R60:pattern_match_ownership_split:DYNAMIC_LOWERING:STRUCTURAL": ("PMOSTC-R006", "DYNAMIC_LOWERING"),
    }
    require(len(entries) == 2 and len(entry_by_key) == 2 and set(entry_by_key) == set(expected_entries), "OVERLAY_EVIDENCE_EXACT_2")
    for key, (locator, role) in expected_entries.items():
        row = entry_by_key.get(key, {})
        require(row.get("class") == "CONTRACT_RULE_ID", f"OVERLAY_EVIDENCE_CLASS:{role}")
        require(row.get("path") == CONTRACT_REL, f"OVERLAY_EVIDENCE_PATH:{role}")
        require(row.get("locator_kind") == "REGISTRY_ID" and row.get("locator") == locator, f"OVERLAY_EVIDENCE_LOCATOR:{role}")
        require(row.get("stage_role") == role, f"OVERLAY_EVIDENCE_ROLE:{role}")

    bindings = overlay.get("bindings", [])
    binding_by_cell = {(row.get("feature_id"), row.get("stage"), row.get("outcome")): row for row in bindings}
    require(len(bindings) == 2 and len(binding_by_cell) == 2 and set(binding_by_cell) == TARGET_CELLS, "OVERLAY_BINDINGS_EXACT_2")
    for cell in TARGET_CELLS:
        row = binding_by_cell.get(cell, {})
        key = f"R60:{FEATURE}:{cell[1]}:STRUCTURAL"
        require(row.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP", f"OVERLAY_PREDECESSOR:{cell[1]}")
        require(row.get("disposition") == "BOUND_DIRECT", f"OVERLAY_DISPOSITION:{cell[1]}")
        require(row.get("evidence_keys") == [key], f"OVERLAY_EVIDENCE_BINDING:{cell[1]}")
        require(row.get("delegate_feature_id") is None and row.get("not_applicable") is None, f"OVERLAY_DIRECT_SHAPE:{cell[1]}")

    overlay_cases = overlay.get("acceptance_cases", [])
    require(len(overlay_cases) == 12, "OVERLAY_CASES_EXACT_12")
    for index, row in enumerate(overlay_cases):
        pointer = f"/acceptance_cases/{index}"
        require(row.get("contract_pointer") == pointer, f"OVERLAY_CASE_POINTER:{index}")
        try:
            resolved = resolve_pointer(contract, pointer)
        except (KeyError, IndexError, TypeError, ValueError):
            resolved = {}
        expected = cases[index] if index < len(cases) else {}
        require(resolved == expected, f"OVERLAY_CASE_POINTER_RESOLVES:{index}")
        require(
            (row.get("case_id"), row.get("audit_case_id"), row.get("feature_id"), row.get("class"))
            == (expected.get("case_id"), expected.get("audit_case_id"), expected.get("feature_id"), expected.get("class")),
            f"OVERLAY_CASE_BINDING:{index}",
        )
        require(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"OVERLAY_CASE_NOT_RUN:{index}")

    expected_counts = {
        "feature_count": 1,
        "evidence_entry_count": 2,
        "binding_count": 2,
        "acceptance_case_count": 12,
        "acceptance_stage_transition_count": 0,
        "predecessor_blocked_cell_count": 2,
        "overlay_bound_direct_transition_count": 2,
        "overlay_bound_delegated_transition_count": 0,
        "overlay_not_applicable_transition_count": 0,
        "predecessor_cumulative_overlay_binding_count": 113,
        "post_overlay_cumulative_binding_count": 115,
        "predecessor_total_bound_direct_cell_count": 2450,
        "predecessor_total_bound_delegated_cell_count": 3,
        "predecessor_total_not_applicable_cell_count": 502,
        "predecessor_total_blocked_cell_count": 1266,
        "post_overlay_total_bound_direct_cell_count": 2452,
        "post_overlay_total_bound_delegated_cell_count": 3,
        "post_overlay_total_not_applicable_cell_count": 502,
        "post_overlay_total_blocked_cell_count": 1264,
        "post_overlay_missing_cell_count": 0,
        "post_overlay_conflict_cell_count": 0,
    }
    require(overlay.get("counts") == expected_counts, "OVERLAY_COUNTS_EXACT")

    prior_binding_count = sum(len(load(root / rel).get("bindings", [])) for rel in PRIOR_OVERLAYS)
    require(prior_binding_count == 113, "PRIOR_OVERLAY_BINDINGS_EXACT_113")
    trace_rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    trace, duplicate_count = trace_cells(trace_rows)
    require(len(trace_rows) == 469 and len({row.get("feature_id") for row in trace_rows}) == 469, "TRACE_FEATURES_EXACT_469")
    require(len(trace) == 4221 and duplicate_count == 0, "TRACE_CELLS_EXACT_UNIQUE_4221")
    raw = {cell: row.get("disposition") for cell, row in trace.items()}
    installed_counts = disposition_counts(raw)
    require(
        installed_counts
        in {
            (2450, 3, 502, 1266),  # R60 pre-state
            (2452, 3, 502, 1264),  # R60 post-state
            (2457, 3, 502, 1259),  # R61 post-state
        },
        "TRACE_INSTALLED_PRE_OR_POST_COUNTS",
    )
    pre = dict(raw)
    for cell in TARGET_CELLS:
        require(raw.get(cell) in {"APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT"}, f"TRACE_TARGET_PRE_OR_POST:{cell[1]}")
        pre[cell] = "APPLICABLE_BLOCKED_BY_GAP"
    pre_counts = disposition_counts(pre)
    target_direct_count = sum(raw.get(cell) == "BOUND_DIRECT" for cell in TARGET_CELLS)
    require(
        pre_counts
        == (installed_counts[0] - target_direct_count, installed_counts[1], installed_counts[2], installed_counts[3] + target_direct_count),
        "TRACE_PREDECESSOR_COUNTS_EXACT",
    )
    post = dict(pre)
    for cell in TARGET_CELLS:
        post[cell] = "BOUND_DIRECT"
    require(
        disposition_counts(post)
        == (pre_counts[0] + len(TARGET_CELLS), pre_counts[1], pre_counts[2], pre_counts[3] - len(TARGET_CELLS)),
        "TRACE_POST_COUNTS_EXACT",
    )
    require({cell for cell in pre if pre[cell] != post[cell]} == TARGET_CELLS, "TRACE_ONLY_TWO_TARGET_CELLS_CHANGED")
    require(all(pre[cell] == post[cell] for cell in pre if cell not in TARGET_CELLS), "TRACE_ALL_OTHER_CELLS_UNCHANGED")
    for feature in EXCLUDED_FEATURES:
        feature_cells = [cell for cell in pre if cell[0] == feature]
        require(len(feature_cells) == 9, f"TRACE_EXCLUDED_FEATURE_CELLS_EXACT_9:{feature}")
        require(all(pre[cell] == post[cell] for cell in feature_cells), f"TRACE_EXCLUDED_FEATURE_UNCHANGED:{feature}")
    if disposition_counts(raw) == (2452, 3, 502, 1264):
        require(raw == post, "TRACE_INSTALLED_POST_EXACT")

    expected_machine = {
        "feature_count": 1,
        "rule_count": 14,
        "acceptance_case_count": 12,
        "positive_case_count": 3,
        "boundary_case_count": 4,
        "reject_case_count": 5,
        "overlay_binding_count": 2,
        "predecessor_blocked_cell_count": 2,
        "overlay_bound_direct_transition_count": 2,
        "overlay_bound_delegated_transition_count": 0,
        "overlay_not_applicable_transition_count": 0,
        "predecessor_cumulative_overlay_binding_count": 113,
        "post_overlay_cumulative_binding_count": 115,
        "predecessor_total_bound_direct_cell_count": 2450,
        "predecessor_total_bound_delegated_cell_count": 3,
        "predecessor_total_not_applicable_cell_count": 502,
        "predecessor_total_blocked_cell_count": 1266,
        "post_overlay_total_bound_direct_cell_count": 2452,
        "post_overlay_total_bound_delegated_cell_count": 3,
        "post_overlay_total_not_applicable_cell_count": 502,
        "post_overlay_total_blocked_cell_count": 1264,
        "post_overlay_missing_cell_count": 0,
        "post_overlay_conflict_cell_count": 0,
        "new_operation_count": 0,
        "logical_final_commit_count_on_success": 1,
        "failure_residue_count": 0,
        "or_retry_count": 0,
        "excluded_reverse_dependent_transition_count": 0,
        "other_target_cell_transition_count": 0,
    }
    require(contract.get("machine_acceptance") == expected_machine, "MACHINE_ACCEPTANCE_EXACT")
    authority = contract.get("authority_fence", {})
    require(
        authority
        == {
            "new_source_surface_count": 0,
            "new_ast_identity_count": 0,
            "new_hir_identity_count": 0,
            "new_mir_operation_kind_count": 0,
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
            "evidence_level": "E2_STRUCTURED_STATIC",
        },
        "AUTHORITY_FENCE_EXACT",
    )
    guards = overlay.get("guards", {})
    require(
        guards
        == {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "transitioned_cell_count": 2,
            "excluded_reverse_dependent_transition_count": 0,
            "preview_transition_count": 0,
            "other_cell_transition_count": 0,
            "source_activation": "none",
            "surface_change_count": 0,
            "ast_identity_change_count": 0,
            "hir_identity_change_count": 0,
            "mir_operation_kind_change_count": 0,
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
            "product_execution_receipt_count": 0,
            "implementation_claim": "NONE",
        },
        "GUARDS_EXACT",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    overlay = load(root / OVERLAY_REL)
    contract = load(root / CONTRACT_REL)
    errors = validate(root, overlay, contract)
    print(
        json.dumps(
            {
                "schema": "deeplus.pattern-match-ownership-split-trace-validation-receipt/r1",
                "result": "PASS" if not errors else "FAIL",
                "feature_count": 1,
                "binding_count": 2,
                "rule_count": len(contract.get("rules", [])),
                "acceptance_case_count": len(contract.get("acceptance_cases", [])),
                "projected_counts": {
                    "bound_direct": 2452,
                    "bound_delegated": 3,
                    "not_applicable": 502,
                    "applicable_blocked": 1264,
                    "missing": 0,
                    "conflict": 0,
                },
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
