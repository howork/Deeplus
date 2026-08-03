#!/usr/bin/env python3
"""Build the bounded R61 pattern-clause/exhaustiveness trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/pattern-clause-exhaustiveness-evidence-r1.json"
CONTRACT = "spec/contracts/pattern-clause-exhaustiveness-trace-closure-r1.json"
FEATURES = ["clause_pattern_heads", "match_exhaustiveness_phase_a"]
STRUCTURAL_BINDINGS = [
    ("clause_pattern_heads", "DYNAMIC_LOWERING", None, "PCETC-R006"),
]
TEST_BINDINGS = [
    ("clause_pattern_heads", "BOUNDARY"),
    ("clause_pattern_heads", "REJECT"),
    ("match_exhaustiveness_phase_a", "BOUNDARY"),
    ("match_exhaustiveness_phase_a", "REJECT"),
]


def evidence_key(feature: str, stage: str, outcome: str | None) -> str:
    return f"R61:{feature}:{stage}:{outcome or 'STRUCTURAL'}"


def entry(
    key: str,
    evidence_class: str,
    locator_kind: str,
    locator: str,
    stage_role: str,
) -> dict[str, str]:
    return {
        "evidence_key": key,
        "class": evidence_class,
        "path": CONTRACT,
        "locator_kind": locator_kind,
        "locator": locator,
        "stage_role": stage_role,
    }


def binding(
    feature: str,
    stage: str,
    outcome: str | None,
    key: str,
) -> dict[str, object]:
    return {
        "feature_id": feature,
        "stage": stage,
        "outcome": outcome,
        "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
        "disposition": "BOUND_DIRECT",
        "evidence_keys": [key],
        "delegate_feature_id": None,
        "not_applicable": None,
    }


def main() -> None:
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    rule_ids = {rule["rule_id"] for rule in contract["rules"]}
    case_by_id = {case["case_id"]: case for case in contract["acceptance_cases"]}
    target_cells = {
        (cell["feature_id"], cell["stage"], cell["outcome"]): cell
        for cell in contract["scope_fence"]["transitioned_cells"]
    }
    expected_cells = {
        (feature, stage, outcome)
        for feature, stage, outcome, _ in STRUCTURAL_BINDINGS
    } | {
        (feature, "CONFORMANCE_TESTS", outcome)
        for feature, outcome in TEST_BINDINGS
    }
    if set(target_cells) != expected_cells:
        raise ValueError("R61_TARGET_CELL_FENCE_MISMATCH")

    entries: list[dict[str, str]] = []
    bindings: list[dict[str, object]] = []
    trace_cases: list[dict[str, object]] = []

    for feature, stage, outcome, rule_id in STRUCTURAL_BINDINGS:
        if rule_id not in rule_ids:
            raise ValueError(f"R61_RULE_NOT_FOUND:{rule_id}")
        cell = target_cells[(feature, stage, outcome)]
        if (
            cell["predecessor_disposition"] != "APPLICABLE_BLOCKED_BY_GAP"
            or cell["disposition"] != "BOUND_DIRECT"
        ):
            raise ValueError(f"R61_TARGET_DISPOSITION_MISMATCH:{feature}:{stage}")
        key = evidence_key(feature, stage, outcome)
        entries.append(entry(key, "CONTRACT_RULE_ID", "REGISTRY_ID", rule_id, stage))
        bindings.append(binding(feature, stage, outcome, key))

    bound_case_count = 0
    for ordinal, (feature, outcome) in enumerate(TEST_BINDINGS, start=1):
        case_ids = contract["acceptance_bindings"][feature][outcome]
        if not case_ids or any(
            case_id not in case_by_id
            or case_by_id[case_id]["feature_id"] != feature
            or case_by_id[case_id]["class"] != outcome
            or case_by_id[case_id]["execution_state"] != "DESIGN_STATIC_NOT_RUN"
            for case_id in case_ids
        ):
            raise ValueError(f"R61_ACCEPTANCE_BINDING_CLASS_MISMATCH:{feature}:{outcome}")
        bound_case_count += len(case_ids)
        cell = target_cells[(feature, "CONFORMANCE_TESTS", outcome)]
        if (
            cell["predecessor_disposition"] != "APPLICABLE_BLOCKED_BY_GAP"
            or cell["disposition"] != "BOUND_DIRECT"
        ):
            raise ValueError(f"R61_TEST_DISPOSITION_MISMATCH:{feature}:{outcome}")
        key = evidence_key(feature, "CONFORMANCE_TESTS", outcome)
        pointer = f"/acceptance_bindings/{feature}/{outcome}"
        entries.append(entry(
            key,
            "ACCEPTANCE_CASE_SET",
            "JSON_POINTER",
            pointer,
            f"CONFORMANCE_TESTS:{outcome}",
        ))
        bindings.append(binding(feature, "CONFORMANCE_TESTS", outcome, key))
        trace_cases.append({
            "case_id": f"R61-TRACE-{ordinal:03d}",
            "feature_id": feature,
            "outcome": outcome,
            "contract_pointer": pointer,
            "acceptance_case_ids": case_ids,
            "disposition": "BOUND_DIRECT",
            "delegate_feature_id": None,
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })

    if len(contract["acceptance_cases"]) != 22 or bound_case_count != 19:
        raise ValueError("R61_ACCEPTANCE_CARDINALITY_MISMATCH")

    entries.sort(key=lambda item: item["evidence_key"])
    bindings.sort(key=lambda item: (
        str(item["feature_id"]),
        str(item["stage"]),
        str(item["outcome"]),
    ))
    value = {
        "$schema": "../../../schemas/language/pattern-clause-exhaustiveness-evidence-r1.schema.json",
        "schema": "deeplus.pattern-clause-exhaustiveness-evidence/r1",
        "revision": "r61-local-pattern-clause-exhaustiveness-trace-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "2db4f483ffdcb281ef765def67e510e63917500c",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": FEATURES,
        "evidence_entries": entries,
        "bindings": bindings,
        "acceptance_cases": trace_cases,
        "counts": {
            "feature_count": 2,
            "evidence_entry_count": 5,
            "binding_count": 5,
            "contract_acceptance_case_count": 22,
            "acceptance_binding_set_count": 4,
            "acceptance_bound_case_count": 19,
            "acceptance_stage_transition_count": 4,
            "predecessor_blocked_cell_count": 5,
            "overlay_bound_direct_transition_count": 5,
            "overlay_bound_delegated_transition_count": 0,
            "overlay_not_applicable_transition_count": 0,
            "predecessor_cumulative_overlay_binding_count": 115,
            "post_overlay_cumulative_binding_count": 120,
            "predecessor_total_bound_direct_cell_count": 2452,
            "predecessor_total_bound_delegated_cell_count": 3,
            "predecessor_total_not_applicable_cell_count": 502,
            "predecessor_total_blocked_cell_count": 1264,
            "post_overlay_total_bound_direct_cell_count": 2457,
            "post_overlay_total_bound_delegated_cell_count": 3,
            "post_overlay_total_not_applicable_cell_count": 502,
            "post_overlay_total_blocked_cell_count": 1259,
            "post_overlay_missing_cell_count": 0,
            "post_overlay_conflict_cell_count": 0,
        },
        "guards": {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "transitioned_cell_count": 5,
            "excluded_related_feature_transition_count": 0,
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
