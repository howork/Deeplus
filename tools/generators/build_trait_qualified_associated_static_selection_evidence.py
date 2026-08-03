#!/usr/bin/env python3
"""Build the bounded R62 trait-qualified associated-static trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/trait-qualified-associated-static-selection-evidence-r1.json"
CONTRACT = "spec/contracts/trait-qualified-associated-static-selection-trace-closure-r1.json"
FEATURE = "trait_qualified_associated_static_selection"
EVIDENCE_KEY = f"R62:{FEATURE}:DYNAMIC_LOWERING:STRUCTURAL"


def main() -> None:
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    rule_ids = {rule["rule_id"] for rule in contract["rules"]}
    if "TQASSTC-R006" not in rule_ids:
        raise ValueError("R62_RULE_NOT_FOUND:TQASSTC-R006")
    target_cells = contract["scope_fence"]["transitioned_cells"]
    expected_cell = {
        "feature_id": FEATURE,
        "stage": "DYNAMIC_LOWERING",
        "outcome": None,
        "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
        "predecessor_gap_id": "IR-XCUT-P1-054",
        "disposition": "BOUND_DIRECT",
    }
    if target_cells != [expected_cell]:
        raise ValueError("R62_TARGET_CELL_FENCE_MISMATCH")

    acceptance_cases = []
    for index, case in enumerate(contract["acceptance_cases"]):
        if case["execution_state"] != "DESIGN_STATIC_NOT_RUN":
            raise ValueError(f"R62_ACCEPTANCE_EXECUTION_STATE_MISMATCH:{case['case_id']}")
        acceptance_cases.append({
            "case_id": case["case_id"],
            "audit_case_id": case["audit_case_id"],
            "feature_id": case["feature_id"],
            "class": case["class"],
            "contract_pointer": f"/acceptance_cases/{index}",
            "trace_role": "SUPPORTING_DESIGN_STATIC_NOT_STAGE_TRANSITION",
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })
    if len(acceptance_cases) != 13:
        raise ValueError("R62_ACCEPTANCE_CASE_COUNT")

    value = {
        "$schema": "../../../schemas/language/trait-qualified-associated-static-selection-evidence-r1.schema.json",
        "schema": "deeplus.trait-qualified-associated-static-selection-evidence/r1",
        "revision": "r62-local-trait-qualified-associated-static-selection-dynamic-trace-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "0346f2cdd417618ffa0af144a1c37569da63a4c4",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": [FEATURE],
        "evidence_entries": [{
            "evidence_key": EVIDENCE_KEY,
            "class": "CONTRACT_RULE_ID",
            "path": CONTRACT,
            "locator_kind": "REGISTRY_ID",
            "locator": "TQASSTC-R006",
            "stage_role": "DYNAMIC_LOWERING",
        }],
        "bindings": [{
            "feature_id": FEATURE,
            "stage": "DYNAMIC_LOWERING",
            "outcome": None,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": "BOUND_DIRECT",
            "evidence_keys": [EVIDENCE_KEY],
            "delegate_feature_id": None,
            "not_applicable": None,
        }],
        "acceptance_cases": acceptance_cases,
        "counts": {
            "feature_count": 1,
            "evidence_entry_count": 1,
            "binding_count": 1,
            "acceptance_case_count": 13,
            "acceptance_stage_transition_count": 0,
            "predecessor_blocked_cell_count": 1,
            "overlay_bound_direct_transition_count": 1,
            "overlay_bound_delegated_transition_count": 0,
            "overlay_not_applicable_transition_count": 0,
            "predecessor_cumulative_overlay_binding_count": 120,
            "post_overlay_cumulative_binding_count": 121,
            "predecessor_total_bound_direct_cell_count": 2457,
            "predecessor_total_bound_delegated_cell_count": 3,
            "predecessor_total_not_applicable_cell_count": 502,
            "predecessor_total_blocked_cell_count": 1259,
            "post_overlay_total_bound_direct_cell_count": 2458,
            "post_overlay_total_bound_delegated_cell_count": 3,
            "post_overlay_total_not_applicable_cell_count": 502,
            "post_overlay_total_blocked_cell_count": 1258,
            "post_overlay_missing_cell_count": 0,
            "post_overlay_conflict_cell_count": 0,
        },
        "guards": {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "transitioned_cell_count": 1,
            "related_feature_transition_count": 0,
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
    }
    OUT.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
