#!/usr/bin/env python3
"""Run exactly 14 in-memory mutations against the focused R67 validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_closure_capture_dynamic_trace as focused


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def mode_then(schema: dict[str, Any], mode: str) -> dict[str, Any]:
    item = schema["$defs"]["captureItem"]
    for clause in item["allOf"]:
        if clause.get("if", {}).get("properties", {}).get("normalized_mode", {}).get("const") == mode:
            return clause["then"]["properties"]
    raise KeyError(mode)


def target_cell(rows: list[dict[str, Any]]) -> dict[str, Any]:
    feature = next(row for row in rows if row["feature_id"] == focused.FEATURE)
    return next(row for row in feature["stages"] if row["stage"] == "DYNAMIC_LOWERING")


def identity_scope(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["local_predecessor_commit"] = "0" * 40
    bundle["overlay"]["feature_ids"].append("responsibility_identity_registry_r1")


def move_place_move_before_barrier(bundle: dict[str, Any]) -> None:
    expansion = bundle["lowering"]["closure_capture_plan_lowering_contract"]["source_order_expansion"]
    expansion["reference_move_or_once_preparation"] = ["MOVE_RESERVE", "PLACE_MOVE", "BUILDER_STAGE"]


def commit_interval_fallible_or_suspending(bundle: dict[str, Any]) -> None:
    publish = bundle["lowering"]["closure_capture_plan_lowering_contract"]["commit_and_publish"]
    publish["final_interval_failure_edge_count"] = 1
    publish["final_interval_suspend_or_branch_count"] = 1


def move_rollback_or_source_live(bundle: dict[str, Any]) -> None:
    failure = bundle["contract"]["algorithm"]["failure_atomicity"]
    failure["move_reservation_cancelled"] = False
    failure["source_owner_consumed_before_commit_tail_count"] = 1


def copy_rule_or_evidence_domain(bundle: dict[str, Any]) -> None:
    props = mode_then(bundle["input_schema"], "COPY")
    props["responsibility_rule_id_or_null"] = {"const": "Clone"}
    props["responsibility_evidence_id_or_null"] = {"type": "null"}


def copy_witness_nonnull(bundle: dict[str, Any]) -> None:
    mode_then(bundle["input_schema"], "COPY")["trait_witness_id_or_null"] = {
        "type": "string", "minLength": 1
    }


def clone_rule_or_evidence_null(bundle: dict[str, Any]) -> None:
    props = mode_then(bundle["input_schema"], "CLONE")
    props["responsibility_rule_id_or_null"] = {"const": "CopyValue"}
    props["responsibility_evidence_id_or_null"] = {"type": "null"}


def clone_descriptor_witness_not_owned(bundle: dict[str, Any]) -> None:
    clone = next(row for row in bundle["responsibility"]["identities"] if row["identity_id"] == "Clone")
    clone["evidence_mode"] = "RUNTIME_LOOKUP"
    clone["trait_id_required"] = False


def callable_profile_aliases_evidence(bundle: dict[str, Any]) -> None:
    hprops = bundle["hir"]["$defs"]["ReferenceCapture"]["properties"]
    hprops["responsibility_profile_id"]["x-deeplus-identity-domain"] = "RESPONSIBILITY_EVIDENCE_ID_OR_NULL"
    bundle["lowering"]["closure_capture_plan_lowering_contract"]["capture_projection"]["callable_profile_separation"] = "responsibility_profile_id substitutes for ResponsibilityEvidenceId"


def hir_deep_reintroduced(bundle: dict[str, Any]) -> None:
    bundle["hir"]["$defs"]["ReferenceCapture"]["properties"]["mode"]["enum"].append("DEEP")


def mir_deep_reintroduced(bundle: dict[str, Any]) -> None:
    bundle["mir"]["$defs"]["closureReferenceCaptureField"]["properties"]["capture_mode"]["enum"].append("DEEP")


def lowering_deep_nonzero(bundle: dict[str, Any]) -> None:
    contract = bundle["lowering"]["closure_capture_plan_lowering_contract"]
    contract["capture_projection"]["deep_typed_hir_or_mir_row_count"] = 1
    contract["source_order_expansion"]["deep"] = "LOWER_DEEP_CAPTURE"


def target_overlay_counts_or_refs(bundle: dict[str, Any]) -> None:
    binding = bundle["overlay"]["bindings"][0]
    binding["disposition"] = "BOUND_DELEGATED"
    binding["delegate_feature_id"] = "responsibility_identity_registry_r1"
    bundle["overlay"]["counts"]["post_overlay_total_bound_direct_cell_count"] = 2464
    target_cell(bundle["rows"])["evidence_refs"] = ["EV-" + "0" * 64]


def unrelated_governance_or_protected_byte(bundle: dict[str, Any]) -> None:
    row = next(row for row in bundle["rows"] if row["feature_id"] == "accessor_property_colon_equals_surface")
    cell = next(stage for stage in row["stages"] if stage["stage"] == "STATIC_SEMANTICS")
    cell["disposition"] = "APPLICABLE_BLOCKED_BY_GAP" if cell.get("disposition") == "BOUND_DIRECT" else "BOUND_DIRECT"
    bundle["overlay"]["guards"]["product_lanes"] = "15_OF_15_PASS"
    bundle["metadata"]["governance"]["github_publication"] = "ENABLED"
    bundle["force_protected_hash_drift"] = True


def validation_errors(bundle: dict[str, Any]) -> list[str]:
    protected_path = focused.RESPONSIBILITY_REL
    original_digest = focused.PROTECTED[protected_path]
    if bundle.get("force_protected_hash_drift"):
        focused.PROTECTED[protected_path] = "0" * 64
    try:
        return focused.validate(
            ROOT,
            overlay_override=bundle["overlay"],
            contract_override=bundle["contract"],
            input_schema_override=bundle["input_schema"],
            fixture_override=bundle["fixture"],
            hir_override=bundle["hir"],
            mir_override=bundle["mir"],
            identity_catalog_override=bundle["identity_catalog"],
            bridge_override=bundle["bridge"],
            lowering_override=bundle["lowering"],
            machine_override=bundle["machine"],
            responsibility_override=bundle["responsibility"],
            rows_override=bundle["rows"],
            metadata_override=bundle["metadata"],
            decision_text_override=bundle["decision_text"],
        )
    finally:
        focused.PROTECTED[protected_path] = original_digest


def main() -> int:
    normal_errors = focused.validate(ROOT)
    if normal_errors:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors}, indent=2))
        return 1

    base = {
        "overlay": focused.load(ROOT / focused.OVERLAY_REL),
        "contract": focused.load(ROOT / focused.CONTRACT_REL),
        "input_schema": focused.load(ROOT / focused.INPUT_SCHEMA_REL),
        "fixture": focused.load(ROOT / focused.FIXTURE_REL),
        "hir": focused.load(ROOT / focused.HIR_REL),
        "mir": focused.load(ROOT / focused.MIR_REL),
        "identity_catalog": focused.load(ROOT / focused.IDENTITY_CATALOG_REL),
        "bridge": focused.load(ROOT / focused.BRIDGE_REL),
        "lowering": focused.load(ROOT / focused.LOWERING_REL),
        "machine": focused.load(ROOT / focused.MACHINE_REL),
        "responsibility": focused.load(ROOT / focused.RESPONSIBILITY_REL),
        "rows": focused.load(ROOT / focused.ROWS_REL),
        "metadata": focused.load(ROOT / focused.META_REL),
        "decision_text": (ROOT / focused.DECISION_REL).read_text(encoding="utf-8"),
        "force_protected_hash_drift": False,
    }
    mutations: list[Mutation] = [
        ("IDENTITY_SCOPE", identity_scope),
        ("MOVE_PLACE_MOVE_BEFORE_BARRIER", move_place_move_before_barrier),
        ("COMMIT_INTERVAL_FALLIBLE_OR_SUSPENDING", commit_interval_fallible_or_suspending),
        ("MOVE_ROLLBACK_OR_SOURCE_LIVE", move_rollback_or_source_live),
        ("COPY_RULE_OR_EVIDENCE_DOMAIN", copy_rule_or_evidence_domain),
        ("COPY_WITNESS_NONNULL", copy_witness_nonnull),
        ("CLONE_RULE_OR_EVIDENCE_NULL", clone_rule_or_evidence_null),
        ("CLONE_DESCRIPTOR_WITNESS_NOT_OWNED", clone_descriptor_witness_not_owned),
        ("CALLABLE_PROFILE_ALIASES_EVIDENCE", callable_profile_aliases_evidence),
        ("HIR_DEEP_REINTRODUCED", hir_deep_reintroduced),
        ("MIR_DEEP_REINTRODUCED", mir_deep_reintroduced),
        ("LOWERING_DEEP_NONZERO", lowering_deep_nonzero),
        ("TARGET_OVERLAY_COUNTS_OR_REFS", target_overlay_counts_or_refs),
        ("UNRELATED_GOVERNANCE_OR_PROTECTED_BYTE", unrelated_governance_or_protected_byte),
    ]
    if len(mutations) != 14:
        raise AssertionError(f"R67_MUTATION_COUNT:{len(mutations)}")

    results = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        errors = validation_errors(candidate)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == 14
    print(json.dumps({
        "schema": "deeplus.closure-capture-dynamic-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": 14,
        "rejected_count": rejected,
        "mutation_summary": f"{rejected}/14",
        "results": results,
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
