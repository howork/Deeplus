#!/usr/bin/env python3
"""Build the bounded R58 member-visibility trace overlay."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json"
CONTRACT = "spec/contracts/member-visibility-trace-closure-r1.json"
FEATURES = sorted([
    "member_visibility_hierarchy_protected",
    "member_visibility_sigil_surface_phase_a",
    "member_visibility_sigils_only",
])

STRUCTURAL_BINDINGS = [
    (
        "member_visibility_hierarchy_protected",
        "DYNAMIC_LOWERING",
        "APPLICABLE_BLOCKED_BY_GAP",
        "NOT_APPLICABLE",
        "MVTC-R009",
        {
            "reason_code": "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
            "authority_boundary": "MIR_RUNTIME_AUTHORITY",
            "rationale": "Hierarchy-protected access is decided statically and emits no runtime visibility behavior.",
        },
    ),
    (
        "member_visibility_hierarchy_protected",
        "DIAGNOSTICS",
        "NOT_APPLICABLE",
        "BOUND_DIRECT",
        "MVTC-R006",
        None,
    ),
    (
        "member_visibility_sigil_surface_phase_a",
        "STATIC_SEMANTICS",
        "APPLICABLE_BLOCKED_BY_GAP",
        "NOT_APPLICABLE",
        "MVTC-R003",
        {
            "reason_code": "NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY",
            "authority_boundary": "TYPE_CHECKER_AUTHORITY",
            "rationale": "The phase-a surface cell preserves exact sigil or OMITTED syntax and supplies no separate type-checking rule.",
        },
    ),
    (
        "member_visibility_sigils_only",
        "DYNAMIC_LOWERING",
        "APPLICABLE_BLOCKED_BY_GAP",
        "NOT_APPLICABLE",
        "MVTC-R009",
        {
            "reason_code": "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
            "authority_boundary": "MIR_RUNTIME_AUTHORITY",
            "rationale": "The sigil-only rule is closed before lowering and emits no runtime visibility behavior.",
        },
    ),
]

TEST_BINDINGS = [
    ("member_visibility_hierarchy_protected", "POSITIVE", "BOUND_DIRECT", None),
    ("member_visibility_hierarchy_protected", "BOUNDARY", "BOUND_DIRECT", None),
    ("member_visibility_hierarchy_protected", "REJECT", "BOUND_DIRECT", None),
    ("member_visibility_sigil_surface_phase_a", "POSITIVE", "BOUND_DIRECT", None),
    ("member_visibility_sigil_surface_phase_a", "BOUNDARY", "BOUND_DIRECT", None),
    ("member_visibility_sigil_surface_phase_a", "REJECT", "BOUND_DELEGATED", "member_visibility_sigils_only"),
    ("member_visibility_sigils_only", "POSITIVE", "BOUND_DIRECT", None),
    ("member_visibility_sigils_only", "BOUNDARY", "BOUND_DIRECT", None),
    ("member_visibility_sigils_only", "REJECT", "BOUND_DIRECT", None),
]


def evidence_key(feature: str, stage: str, outcome: str | None = None) -> str:
    return f"R58:{feature}:{stage}:{outcome or 'STRUCTURAL'}"


def evidence_entry(
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
    predecessor: str,
    disposition: str,
    key: str,
    delegate: str | None,
    not_applicable: dict[str, str] | None,
) -> dict[str, object]:
    detail = None
    if not_applicable is not None:
        detail = {
            **not_applicable,
            "justification_evidence_keys": [key],
        }
    return {
        "feature_id": feature,
        "stage": stage,
        "outcome": outcome,
        "predecessor_disposition": predecessor,
        "disposition": disposition,
        "evidence_keys": [key],
        "delegate_feature_id": delegate,
        "not_applicable": detail,
    }


def main() -> None:
    contract = json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))
    acceptance_bindings = contract["acceptance_bindings"]
    case_by_id = {case["case_id"]: case for case in contract["acceptance_cases"]}
    entries: list[dict[str, str]] = []
    bindings: list[dict[str, object]] = []
    trace_cases: list[dict[str, object]] = []

    for feature, stage, predecessor, disposition, rule_id, detail in STRUCTURAL_BINDINGS:
        key = evidence_key(feature, stage)
        entries.append(evidence_entry(key, "CONTRACT_RULE_ID", "REGISTRY_ID", rule_id, stage))
        bindings.append(binding(feature, stage, None, predecessor, disposition, key, None, detail))

    for ordinal, (feature, outcome, disposition, delegate) in enumerate(TEST_BINDINGS, start=1):
        case_ids = acceptance_bindings[feature][outcome]
        if not case_ids or any(
            case_by_id[case_id]["feature_id"] != feature
            or case_by_id[case_id]["class"] != outcome
            for case_id in case_ids
        ):
            raise ValueError(f"ACCEPTANCE_BINDING_CLASS_MISMATCH:{feature}:{outcome}")
        key = evidence_key(feature, "CONFORMANCE_TESTS", outcome)
        pointer = f"/acceptance_bindings/{feature}/{outcome}"
        entries.append(evidence_entry(
            key,
            "ACCEPTANCE_CASE_SET",
            "JSON_POINTER",
            pointer,
            f"CONFORMANCE_TESTS:{outcome}",
        ))
        bindings.append(binding(
            feature,
            "CONFORMANCE_TESTS",
            outcome,
            "APPLICABLE_BLOCKED_BY_GAP",
            disposition,
            key,
            delegate,
            None,
        ))
        trace_cases.append({
            "case_id": f"R58-TRACE-{ordinal:03d}",
            "feature_id": feature,
            "outcome": outcome,
            "contract_pointer": pointer,
            "acceptance_case_ids": case_ids,
            "disposition": disposition,
            "delegate_feature_id": delegate,
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })

    entries.sort(key=lambda item: item["evidence_key"])
    bindings.sort(key=lambda item: (
        str(item["feature_id"]),
        str(item["stage"]),
        str(item["outcome"]),
    ))
    value = {
        "$schema": "../../../schemas/language/member-visibility-evidence-r1.schema.json",
        "schema": "deeplus.member-visibility-evidence/r1",
        "revision": "r58-local-member-visibility-trace-closure-r1",
        "canonical_baseline_commit": "39a5d50cc770341c4b9776d00d84520b780d0c62",
        "local_predecessor_commit": "6a0eb950fb46fc061c260445bb0d25dc766117ea",
        "candidate_status": "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": FEATURES,
        "evidence_entries": entries,
        "bindings": bindings,
        "acceptance_cases": trace_cases,
        "counts": {
            "feature_count": 3,
            "evidence_entry_count": 13,
            "binding_count": 13,
            "predecessor_blocked_cell_count": 12,
            "predecessor_not_applicable_to_direct_count": 1,
            "overlay_bound_direct_transition_count": 9,
            "overlay_bound_delegated_transition_count": 1,
            "overlay_not_applicable_transition_count": 3,
            "predecessor_total_bound_direct_cell_count": 2438,
            "predecessor_total_bound_delegated_cell_count": 2,
            "predecessor_total_not_applicable_cell_count": 500,
            "predecessor_total_blocked_cell_count": 1281,
            "post_overlay_total_bound_direct_cell_count": 2447,
            "post_overlay_total_bound_delegated_cell_count": 3,
            "post_overlay_total_not_applicable_cell_count": 502,
            "post_overlay_total_blocked_cell_count": 1269,
            "post_overlay_missing_cell_count": 0,
            "post_overlay_conflict_cell_count": 0,
            "acceptance_binding_count": 9,
            "acceptance_case_count": 10,
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
