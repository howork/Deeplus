#!/usr/bin/env python3
"""Build the bounded R57 unified-call and tilde trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json"
CONTRACT = "spec/contracts/unified-call-tilde-trace-closure-r1.json"
FEATURES = sorted([
    "actor_declaration_grammar_closed",
    "actor_protocol_family",
    "data_shaping_callshape_model",
    "unified_call_expression_and_tilde_modes",
])

STRUCTURAL_RULES = {
    ("unified_call_expression_and_tilde_modes", "DYNAMIC_LOWERING"): "UCTC-R011",
    ("actor_protocol_family", "DYNAMIC_LOWERING"): "UCTC-R014",
}

TEST_BINDINGS = [
    ("unified_call_expression_and_tilde_modes", "POSITIVE", "BOUND_DIRECT", None),
    ("unified_call_expression_and_tilde_modes", "BOUNDARY", "BOUND_DIRECT", None),
    ("unified_call_expression_and_tilde_modes", "REJECT", "BOUND_DIRECT", None),
    ("data_shaping_callshape_model", "BOUNDARY", "BOUND_DIRECT", None),
    ("data_shaping_callshape_model", "REJECT", "BOUND_DIRECT", None),
    ("actor_declaration_grammar_closed", "BOUNDARY", "BOUND_DIRECT", None),
    ("actor_declaration_grammar_closed", "REJECT", "BOUND_DELEGATED", "actor_mailbox_capacity"),
]


def evidence_key(feature: str, stage: str, outcome: str | None = None) -> str:
    return f"R57:{feature}:{stage}:{outcome or 'STRUCTURAL'}"


def entry(key: str, evidence_class: str, locator_kind: str, locator: str, stage_role: str) -> dict[str, str]:
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
    disposition: str,
    delegate_feature_id: str | None,
) -> dict[str, object]:
    return {
        "feature_id": feature,
        "stage": stage,
        "outcome": outcome,
        "disposition": disposition,
        "evidence_keys": [key],
        "delegate_feature_id": delegate_feature_id,
        "not_applicable": None,
    }


def main() -> None:
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    acceptance_bindings = contract["acceptance_bindings"]
    case_by_id = {case["case_id"]: case for case in contract["acceptance_cases"]}
    entries: list[dict[str, str]] = []
    bindings: list[dict[str, object]] = []
    trace_cases: list[dict[str, object]] = []

    for (feature, stage), rule_id in sorted(STRUCTURAL_RULES.items()):
        key = evidence_key(feature, stage)
        entries.append(entry(key, "CONTRACT_RULE_ID", "REGISTRY_ID", rule_id, stage))
        bindings.append(binding(feature, stage, None, key, "BOUND_DIRECT", None))

    for ordinal, (feature, outcome, disposition, delegate) in enumerate(TEST_BINDINGS, start=1):
        ids = acceptance_bindings[feature][outcome]
        if not ids or any(case_by_id[case_id]["class"] != outcome for case_id in ids):
            raise ValueError(f"ACCEPTANCE_BINDING_CLASS_MISMATCH:{feature}:{outcome}")
        key = evidence_key(feature, "CONFORMANCE_TESTS", outcome)
        pointer = f"/acceptance_bindings/{feature}/{outcome}"
        entries.append(entry(key, "ACCEPTANCE_CASE_SET", "JSON_POINTER", pointer, f"CONFORMANCE_TESTS:{outcome}"))
        bindings.append(binding(feature, "CONFORMANCE_TESTS", outcome, key, disposition, delegate))
        trace_cases.append({
            "case_id": f"R57-TRACE-{ordinal:03d}",
            "feature_id": feature,
            "outcome": outcome,
            "contract_pointer": pointer,
            "acceptance_case_ids": ids,
            "disposition": disposition,
            "delegate_feature_id": delegate,
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })

    entries.sort(key=lambda item: item["evidence_key"])
    bindings.sort(key=lambda item: (str(item["feature_id"]), str(item["stage"]), str(item["outcome"])))
    value = {
        "$schema": "../../../schemas/language/unified-call-tilde-evidence-r1.schema.json",
        "schema": "deeplus.unified-call-tilde-evidence/r1",
        "revision": "r57-local-unified-call-tilde-trace-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "808bf7cd1d28bba737e0744a6f120c71297d7ddd",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": FEATURES,
        "evidence_entries": entries,
        "bindings": bindings,
        "acceptance_cases": trace_cases,
        "counts": {
            "feature_count": 4,
            "evidence_entry_count": 9,
            "binding_count": 9,
            "predecessor_blocked_cell_count": 10,
            "catalog_direct_transition_count": 1,
            "overlay_bound_direct_transition_count": 8,
            "overlay_bound_delegated_transition_count": 1,
            "predecessor_total_blocked_cell_count": 1291,
            "post_overlay_total_blocked_cell_count": 1281,
            "acceptance_binding_count": 7,
            "acceptance_case_count": 15,
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
    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
