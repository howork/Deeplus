#!/usr/bin/env python3
"""Build the bounded R59 pattern dynamic-lowering trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/pattern-dynamic-lowering-evidence-r1.json"
CONTRACT = "spec/contracts/pattern-dynamic-lowering-trace-closure-r1.json"
FEATURES = [
    "or_alias_pattern",
    "pattern_binding_control_family",
    "pattern_decomposition",
]
STRUCTURAL_BINDINGS = [
    ("or_alias_pattern", "PDLTC-R009"),
    ("pattern_binding_control_family", "PDLTC-R003"),
    ("pattern_decomposition", "PDLTC-R002"),
]


def evidence_key(feature: str) -> str:
    return f"R59:{feature}:DYNAMIC_LOWERING:STRUCTURAL"


def main() -> None:
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    rule_ids = {rule["rule_id"] for rule in contract["rules"]}
    target_cells = {
        (cell["feature_id"], cell["stage"]): cell
        for cell in contract["scope_fence"]["transitioned_cells"]
    }
    if set(target_cells) != {(feature, "DYNAMIC_LOWERING") for feature in FEATURES}:
        raise ValueError("R59_TARGET_CELL_FENCE_MISMATCH")

    entries: list[dict[str, str]] = []
    bindings: list[dict[str, object]] = []
    for feature, rule_id in STRUCTURAL_BINDINGS:
        if rule_id not in rule_ids:
            raise ValueError(f"R59_RULE_NOT_FOUND:{rule_id}")
        cell = target_cells[(feature, "DYNAMIC_LOWERING")]
        if (
            cell["predecessor_disposition"] != "APPLICABLE_BLOCKED_BY_GAP"
            or cell["disposition"] != "BOUND_DIRECT"
        ):
            raise ValueError(f"R59_TARGET_DISPOSITION_MISMATCH:{feature}")
        key = evidence_key(feature)
        entries.append({
            "evidence_key": key,
            "class": "CONTRACT_RULE_ID",
            "path": CONTRACT,
            "locator_kind": "REGISTRY_ID",
            "locator": rule_id,
            "stage_role": "DYNAMIC_LOWERING",
        })
        bindings.append({
            "feature_id": feature,
            "stage": "DYNAMIC_LOWERING",
            "outcome": None,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": "BOUND_DIRECT",
            "evidence_keys": [key],
            "delegate_feature_id": None,
            "not_applicable": None,
        })

    acceptance_cases = []
    for case in contract["acceptance_cases"]:
        if case["execution_state"] != "DESIGN_STATIC_NOT_RUN":
            raise ValueError(f"R59_ACCEPTANCE_EXECUTION_STATE_MISMATCH:{case['case_id']}")
        acceptance_cases.append({
            "case_id": case["case_id"],
            "audit_case_id": case["audit_case_id"],
            "feature_id": case["feature_id"],
            "class": case["class"],
            "contract_pointer": f"/acceptance_cases/{len(acceptance_cases)}",
            "trace_role": "SUPPORTING_DESIGN_STATIC_NOT_STAGE_TRANSITION",
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })

    entries.sort(key=lambda item: item["evidence_key"])
    bindings.sort(key=lambda item: str(item["feature_id"]))
    value = {
        "$schema": "../../../schemas/language/pattern-dynamic-lowering-evidence-r1.schema.json",
        "schema": "deeplus.pattern-dynamic-lowering-evidence/r1",
        "revision": "r59-local-pattern-dynamic-lowering-trace-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "fb3e98888f947d0e7b45f713efe3b017a55c976a",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": FEATURES,
        "evidence_entries": entries,
        "bindings": bindings,
        "acceptance_cases": acceptance_cases,
        "counts": {
            "feature_count": 3,
            "evidence_entry_count": 3,
            "binding_count": 3,
            "acceptance_case_count": 12,
            "acceptance_stage_transition_count": 0,
            "predecessor_blocked_cell_count": 3,
            "overlay_bound_direct_transition_count": 3,
            "overlay_bound_delegated_transition_count": 0,
            "overlay_not_applicable_transition_count": 0,
            "predecessor_cumulative_overlay_binding_count": 110,
            "post_overlay_cumulative_binding_count": 113,
            "predecessor_total_bound_direct_cell_count": 2447,
            "predecessor_total_bound_delegated_cell_count": 3,
            "predecessor_total_not_applicable_cell_count": 502,
            "predecessor_total_blocked_cell_count": 1269,
            "post_overlay_total_bound_direct_cell_count": 2450,
            "post_overlay_total_bound_delegated_cell_count": 3,
            "post_overlay_total_not_applicable_cell_count": 502,
            "post_overlay_total_blocked_cell_count": 1266,
            "post_overlay_missing_cell_count": 0,
            "post_overlay_conflict_cell_count": 0,
        },
        "guards": {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "transitioned_cell_count": 3,
            "ownership_split_transition_count": 0,
            "reverse_dependent_transition_count": 0,
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
    }
    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
