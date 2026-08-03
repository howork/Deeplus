#!/usr/bin/env python3
"""Run exactly 12 in-memory mutations against the focused R66 validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_responsibility_identity_dynamic_trace as focused


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def target_cell(rows: list[dict[str, Any]]) -> dict[str, Any]:
    feature = next(row for row in rows if row["feature_id"] == focused.FEATURE)
    return next(row for row in feature["stages"] if row["stage"] == "DYNAMIC_LOWERING")


def unrelated_cell_drift(bundle: dict[str, Any]) -> None:
    feature = next(
        row for row in bundle["rows"]
        if row["feature_id"] == "accessor_property_colon_equals_surface"
    )
    cell = next(row for row in feature["stages"] if row["stage"] == "STATIC_SEMANTICS")
    cell["disposition"] = (
        "BOUND_DIRECT"
        if cell.get("disposition") != "BOUND_DIRECT"
        else "APPLICABLE_BLOCKED_BY_GAP"
    )


def identity_drift(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["canonical_baseline_commit"] = "0" * 40
    bundle["overlay"]["local_predecessor_commit"] = "1" * 40


def scope_drift(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["feature_ids"].append("closure_capture_descriptor_msp")
    bundle["overlay"]["bindings"][0]["feature_id"] = "closure_capture_descriptor_msp"


def predecessor_or_post_disposition_drift(bundle: dict[str, Any]) -> None:
    binding = bundle["overlay"]["bindings"][0]
    binding["predecessor_disposition"] = "BOUND_DIRECT"
    binding["disposition"] = "BOUND_DELEGATED"
    binding["delegate_feature_id"] = "closure_capture_descriptor_msp"


def evidence_tuple_drift(bundle: dict[str, Any]) -> None:
    entry = bundle["overlay"]["evidence_entries"][0]
    entry["path"] = "spec/contracts/responsibility-identity-registry-r1.json"
    entry["locator"] = "/evidence_residue"
    entry["stage_role"] = "STATIC_SEMANTICS"


def r30_fields_or_six_identities_drift(bundle: dict[str, Any]) -> None:
    bundle["contract"]["identities"].pop()
    bundle["contract"]["evidence_residue"]["hir_exact_fields"].pop()
    bundle["contract"]["evidence_residue"]["mir_exact_fields"].pop()


def hir_descriptor_drift(bundle: dict[str, Any]) -> None:
    descriptor = bundle["hir"]["$defs"]["ResponsibilityEvidenceDescriptor"]
    descriptor["required"].pop()
    descriptor["additionalProperties"] = True
    descriptor["description"] = "mutated structural HIR identity"


def mir_descriptor_or_machine_rule_drift(bundle: dict[str, Any]) -> None:
    descriptor = bundle["mir"]["$defs"]["responsibilityEvidenceDescriptor"]
    descriptor["required"].pop()
    bundle["machine"]["responsibility_evidence_projection_contract"][
        "descriptor_exact_fields"
    ].pop()
    bundle["machine"]["closed_static_identity_contract"][
        "responsibility_identity_rule"
    ] = "runtime lookup may reconstruct responsibility evidence"


def relookup_or_callable_profile_alias_drift(bundle: dict[str, Any]) -> None:
    projection = bundle["lowering"]["profile_contract"][
        "responsibility_evidence_projection_contract"
    ]
    projection["runtime_relookup_count"] = 1
    projection["backend_relookup_count"] = 1
    projection["callable_responsibility_profile_identity_reuse"] = True
    machine = bundle["machine"]["responsibility_evidence_projection_contract"]
    machine["runtime_relookup_count"] = 1
    machine["backend_relookup_count"] = 1


def overlay_or_global_count_drift(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["counts"]["post_overlay_total_bound_direct_cell_count"] = 2465
    bundle["metadata"]["derived_counts"]["bound_direct_cells"] = 2465
    bundle["metadata"]["applied_evidence_overlays"].pop()
    bundle["metadata"]["evidence_registry"].pop()


def target_evidence_refs_drift(bundle: dict[str, Any]) -> None:
    cell = target_cell(bundle["rows"])
    cell["evidence_refs"] = ["EV-" + "0" * 64]
    cell["blocked_gap_ids"] = ["IR-XCUT-P1-054"]


def governance_product_github_decision_or_byte_drift(bundle: dict[str, Any]) -> None:
    guards = bundle["overlay"]["guards"]
    guards["semantic_p0"] = 1
    guards["feature_p1"] = "21_OPEN"
    guards["product_lanes"] = "15_OF_15_PASS"
    guards["github_publication"] = "ENABLED"
    bundle["metadata"]["governance"]["product_lanes"] = "15_OF_15_PASS"
    bundle["decision_text"] = bundle["decision_text"].replace(
        focused.CANONICAL, "f" * 40
    )
    bundle["force_protected_hash_drift"] = True


def validation_errors(bundle: dict[str, Any]) -> list[str]:
    protected_path = "schemas/language/responsibility-identity-registry-r1.schema.json"
    original_digest = focused.PROTECTED[protected_path]
    if bundle.get("force_protected_hash_drift"):
        focused.PROTECTED[protected_path] = "0" * 64
    try:
        return focused.validate(
            ROOT,
            overlay_override=bundle["overlay"],
            contract_override=bundle["contract"],
            hir_schema_override=bundle["hir"],
            mir_schema_override=bundle["mir"],
            lowering_registry_override=bundle["lowering"],
            machine_registry_override=bundle["machine"],
            rows_override=bundle["rows"],
            metadata_override=bundle["metadata"],
            decision_text_override=bundle["decision_text"],
        )
    finally:
        focused.PROTECTED[protected_path] = original_digest


def main() -> int:
    normal_errors = focused.validate(ROOT)
    if normal_errors:
        print(json.dumps({
            "result": "FAIL",
            "phase": "NORMAL_PATH",
            "errors": normal_errors,
        }, indent=2))
        return 1

    base = {
        "overlay": focused.load(ROOT / focused.OVERLAY_REL),
        "contract": focused.load(ROOT / focused.CONTRACT_REL),
        "hir": focused.load(ROOT / focused.HIR_SCHEMA_REL),
        "mir": focused.load(ROOT / focused.MIR_SCHEMA_REL),
        "lowering": focused.load(ROOT / focused.LOWERING_REL),
        "machine": focused.load(ROOT / focused.MACHINE_REL),
        "rows": focused.load(ROOT / focused.ROWS_REL),
        "metadata": focused.load(ROOT / focused.META_REL),
        "decision_text": (ROOT / focused.DECISION_REL).read_text(encoding="utf-8"),
        "force_protected_hash_drift": False,
    }

    mutations: list[Mutation] = [
        ("IDENTITY", identity_drift),
        ("SCOPE", scope_drift),
        ("PREDECESSOR_OR_POST_DISPOSITION", predecessor_or_post_disposition_drift),
        ("EVIDENCE_TUPLE", evidence_tuple_drift),
        ("R30_FIELD_LIST_OR_SIX_IDENTITIES", r30_fields_or_six_identities_drift),
        ("HIR_DESCRIPTOR", hir_descriptor_drift),
        ("MIR_DESCRIPTOR_OR_MACHINE_RULE", mir_descriptor_or_machine_rule_drift),
        ("RUNTIME_BACKEND_RELOOKUP_OR_CALLABLE_PROFILE_ALIAS", relookup_or_callable_profile_alias_drift),
        ("OVERLAY_OR_GLOBAL_COUNTS", overlay_or_global_count_drift),
        ("TARGET_EVIDENCE_REFS", target_evidence_refs_drift),
        ("UNRELATED_4220_CELL", unrelated_cell_drift),
        ("GOVERNANCE_PRODUCT_GITHUB_DECISION_OR_BYTE", governance_product_github_decision_or_byte_drift),
    ]
    if len(mutations) != 12:
        raise AssertionError(f"R66_MUTATION_COUNT:{len(mutations)}")

    results = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        errors = validation_errors(candidate)
        results.append({
            "mutation_id": mutation_id,
            "rejected": bool(errors),
            "first_error": errors[0] if errors else None,
        })

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == 12
    print(json.dumps({
        "schema": "deeplus.responsibility-identity-dynamic-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": 12,
        "rejected_count": rejected,
        "mutation_summary": f"{rejected}/12",
        "results": results,
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
