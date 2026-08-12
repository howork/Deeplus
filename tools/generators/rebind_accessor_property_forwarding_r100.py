#!/usr/bin/env python3
"""Build the exact R100 accessor/property/forwarding successor trace overlay."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "spec/traceability/implementation-target-profile-r1/accessor-property-forwarding-evidence-r100.json"
CONTRACT_PATH = "spec/contracts/accessor-property-forwarding-r100.json"
PREDECESSOR = "spec/traceability/implementation-target-profile-r1/global-trace-closure-evidence-r1.json"

FEATURE_RULES: dict[str, tuple[str, str, bool]] = {
    "accessor_property_colon_equals_surface": ("STATIC_SEMANTICS", "APMF-R001", False),
    "accessor_visibility_restored_law": ("DYNAMIC_LOWERING", "APMF-R002", True),
    "accessor_visibility_surface_phase_a": ("STATIC_SEMANTICS", "APMF-R002", False),
    "instance_extension_property": ("DYNAMIC_LOWERING", "APMF-R009", False),
    "member_forwarding": ("DYNAMIC_LOWERING", "APMF-R011", False),
    "property_default_accessor": ("DYNAMIC_LOWERING", "APMF-R008", False),
    "property_value_admissibility": ("DYNAMIC_LOWERING", "APMF-R006", True),
    "simplified_class_member_surface": ("STATIC_SEMANTICS", "APMF-R007", False),
}
OUTCOMES = ("POSITIVE", "BOUNDARY", "REJECT")
STATIC_SURFACE_DYNAMIC_NA = {
    "accessor_property_colon_equals_surface": "APMF-R007",
    "accessor_visibility_surface_phase_a": "APMF-R002",
    "simplified_class_member_surface": "APMF-R007",
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> None:
    contract = json.loads((ROOT / CONTRACT_PATH).read_text(encoding="utf-8"))
    features = sorted(FEATURE_RULES)
    if contract.get("feature_ids") != features:
        raise SystemExit("R100_FEATURE_SET_DRIFT")

    entries: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    for feature_id in features:
        stage, rule_id, dynamic_is_na = FEATURE_RULES[feature_id]
        structural_key = f"R100:{feature_id}:{stage}:STRUCTURAL"
        entries.append({
            "evidence_key": structural_key,
            "class": "CONTRACT_RULE_ID",
            "path": CONTRACT_PATH,
            "locator_kind": "REGISTRY_ID",
            "locator": rule_id,
            "stage_role": stage,
        })
        na = None
        disposition = "BOUND_DIRECT"
        if dynamic_is_na:
            disposition = "NOT_APPLICABLE"
            na = {
                "reason_code": "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
                "authority_boundary": "MIR_RUNTIME_AUTHORITY",
                "rationale": "This admission law is completely sealed before lowering and introduces no distinct runtime behavior.",
                "justification_evidence_keys": [structural_key],
            }
        bindings.append({
            "feature_id": feature_id,
            "stage": stage,
            "outcome": None,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": disposition,
            "evidence_keys": [structural_key],
            "delegate_feature_id": None,
            "not_applicable": na,
        })
        for outcome in OUTCOMES:
            key = f"R100:{feature_id}:CONFORMANCE_TESTS:{outcome}"
            entries.append({
                "evidence_key": key,
                "class": "ACCEPTANCE_CASE_SET",
                "path": CONTRACT_PATH,
                "locator_kind": "JSON_POINTER",
                "locator": f"/acceptance_bindings/{feature_id}/{outcome}",
                "stage_role": f"CONFORMANCE_TESTS:{outcome}",
            })
            bindings.append({
                "feature_id": feature_id,
                "stage": "CONFORMANCE_TESTS",
                "outcome": outcome,
                "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
                "disposition": "BOUND_DIRECT",
                "evidence_keys": [key],
                "delegate_feature_id": None,
                "not_applicable": None,
            })

    superseded_cells = [
        {"feature_id": row["feature_id"], "stage": row["stage"], "outcome": row["outcome"]}
        for row in bindings
    ]
    for feature_id, rule_id in sorted(STATIC_SURFACE_DYNAMIC_NA.items()):
        key = f"R100:{feature_id}:DYNAMIC_LOWERING:STATIC_ONLY"
        entries.append({
            "evidence_key": key,
            "class": "CONTRACT_RULE_ID",
            "path": CONTRACT_PATH,
            "locator_kind": "REGISTRY_ID",
            "locator": rule_id,
            "stage_role": "DYNAMIC_LOWERING",
        })
        bindings.append({
            "feature_id": feature_id,
            "stage": "DYNAMIC_LOWERING",
            "outcome": None,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": "NOT_APPLICABLE",
            "evidence_keys": [key],
            "delegate_feature_id": None,
            "not_applicable": {
                "reason_code": "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
                "authority_boundary": "MIR_RUNTIME_AUTHORITY",
                "rationale": "This surface or identity distinction is completely normalized before lowering and introduces no separate runtime behavior.",
                "justification_evidence_keys": [key],
            },
        })
    overlay = {
        "schema": "deeplus.accessor-property-forwarding-evidence/r100",
        "revision": "r100-accessor-property-forwarding-trace-r1",
        "status": "LOCAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "feature_ids": features,
        "evidence_entries": entries,
        "bindings": bindings,
        "supersedes_binding_cells": {
            "predecessor_overlay_path": PREDECESSOR,
            "cells": superseded_cells,
        },
        "guards": {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "NOT_PERFORMED",
            "product_execution_receipt_count": 0,
        },
    }
    if len(entries) != 35 or len(bindings) != 35 or len({(r["feature_id"], r["stage"], r["outcome"]) for r in bindings}) != 35 or len(superseded_cells) != 32:
        raise SystemExit("R100_TRACE_CARDINALITY")
    write_json(OUT, overlay)
    print("R100 accessor/property/forwarding trace overlay: PASS (8 features, 32 superseded + 3 completed cells)")


if __name__ == "__main__":
    main()
