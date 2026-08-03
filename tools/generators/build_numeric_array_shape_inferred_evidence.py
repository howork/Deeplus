#!/usr/bin/env python3
"""Build the bounded R56 shape-inferred NumericArray trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json"
CONTRACT = "spec/contracts/numeric-array-shape-inferred-literal-r1.json"
FEATURES = sorted([
    "numeric_array_shape_inferred_column_vector_semicolon_msp",
    "numeric_array_shape_inferred_value_literal",
    "numeric_array_vector_orientation_witness_msp",
])

DYNAMIC_RULES = {
    "numeric_array_shape_inferred_value_literal": "NASIL-R008",
    "numeric_array_shape_inferred_column_vector_semicolon_msp": "NASIL-R009",
    "numeric_array_vector_orientation_witness_msp": "NASIL-R012",
}

TEST_CASES = {
    ("numeric_array_shape_inferred_value_literal", "POSITIVE"): 0,
    ("numeric_array_shape_inferred_value_literal", "BOUNDARY"): 1,
    ("numeric_array_shape_inferred_value_literal", "REJECT"): 2,
    ("numeric_array_shape_inferred_column_vector_semicolon_msp", "BOUNDARY"): 5,
    ("numeric_array_shape_inferred_column_vector_semicolon_msp", "REJECT"): 6,
    ("numeric_array_vector_orientation_witness_msp", "BOUNDARY"): 8,
    ("numeric_array_vector_orientation_witness_msp", "REJECT"): 9,
}


def key(feature: str, stage: str, outcome: str | None = None) -> str:
    return f"R56:{feature}:{stage}:{outcome or 'STRUCTURAL'}"


def entry(
    evidence_key: str,
    evidence_class: str,
    locator_kind: str,
    locator: str,
    stage_role: str,
) -> dict[str, str]:
    return {
        "evidence_key": evidence_key,
        "class": evidence_class,
        "path": CONTRACT,
        "locator_kind": locator_kind,
        "locator": locator,
        "stage_role": stage_role,
    }


def binding(feature: str, stage: str, outcome: str | None, evidence_key: str) -> dict[str, object]:
    return {
        "feature_id": feature,
        "stage": stage,
        "outcome": outcome,
        "disposition": "BOUND_DIRECT",
        "evidence_keys": [evidence_key],
        "delegate_feature_id": None,
        "not_applicable": None,
    }


def main() -> None:
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    cases = contract["acceptance_cases"]
    entries: list[dict[str, str]] = []
    bindings: list[dict[str, object]] = []
    trace_cases: list[dict[str, object]] = []

    for feature in FEATURES:
        evidence_key = key(feature, "DYNAMIC_LOWERING")
        entries.append(entry(evidence_key, "CONTRACT_RULE_ID", "REGISTRY_ID", DYNAMIC_RULES[feature], "DYNAMIC_LOWERING"))
        bindings.append(binding(feature, "DYNAMIC_LOWERING", None, evidence_key))

    for ordinal, ((feature, outcome), index) in enumerate(sorted(TEST_CASES.items()), start=1):
        case = cases[index]
        if case["feature_id"] != feature or case["class"] != outcome:
            raise ValueError(f"CONTRACT_CASE_MISMATCH:{feature}:{outcome}:{index}")
        evidence_key = key(feature, "CONFORMANCE_TESTS", outcome)
        pointer = f"/acceptance_cases/{index}"
        entries.append(entry(evidence_key, "ACCEPTANCE_CASE", "JSON_POINTER", pointer, f"CONFORMANCE_TESTS:{outcome}"))
        bindings.append(binding(feature, "CONFORMANCE_TESTS", outcome, evidence_key))
        trace_cases.append({
            "case_id": f"R56-TRACE-{ordinal:03d}",
            "feature_id": feature,
            "outcome": outcome,
            "contract_pointer": pointer,
            "expected": case["expected"],
            "diagnostic_or_null": case["diagnostic_or_null"],
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })

    entries.sort(key=lambda item: item["evidence_key"])
    bindings.sort(key=lambda item: (str(item["feature_id"]), str(item["stage"]), str(item["outcome"])))
    trace_cases.sort(key=lambda item: item["case_id"])
    value = {
        "$schema": "../../../schemas/language/numeric-array-shape-inferred-evidence-r1.schema.json",
        "schema": "deeplus.numeric-array-shape-inferred-evidence/r1",
        "revision": "r56-local-numeric-array-shape-inferred-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "f4e194d414a024b1fbf93549cdbe3d0cc59fb810",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": FEATURES,
        "evidence_entries": entries,
        "bindings": bindings,
        "acceptance_cases": trace_cases,
        "counts": {
            "feature_count": 3,
            "evidence_entry_count": 10,
            "binding_count": 10,
            "predecessor_blocked_cell_count": 12,
            "catalog_direct_transition_count": 2,
            "bound_direct_transition_count": 10,
            "predecessor_total_blocked_cell_count": 1303,
            "post_overlay_total_blocked_cell_count": 1291,
            "acceptance_case_count": 7,
        },
        "guards": {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "source_activation": "none",
            "surface_change_count": 0,
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
