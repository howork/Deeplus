#!/usr/bin/env python3
"""Run exactly 14 in-memory mutations against the focused R68 validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_region_lifetime_dynamic_trace as focused


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def identity_drift(b: dict[str, Any]) -> None:
    b["contract"]["local_predecessor_commit"] = "0" * 40


def region_kind_map_swap(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["region_graph"]["mir_kind_map"]["Lexical"] = "INVOCATION"


def drop_hir_region_table(b: dict[str, Any]) -> None:
    b["hir"]["$defs"]["HirBodyBase"]["required"].remove("region_table")


def region_parent_cycle_admitted(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["region_graph"]["parent_rule"] = "ALLOW_CYCLE"


def unbound_hir_region_constraint(b: dict[str, Any]) -> None:
    plan = b["hir"]["$defs"]["PlacePlan"]["allOf"][1]
    plan["required"].remove("result_region_id_or_null")


def shared_dispatch_wrong(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["place_access_dispatch"]["BORROW_SHARED"] = "ONE_LOAN_BEGIN_EXCLUSIVE"


def loan_id_created_in_mir(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["loan_projection"]["loan_id_selection_stage"] = "MIR_LOWERING"
    b["lowering"]["loan_close_projection_contract"]["loan_id_creation_stage"] = "MIR_LOWERING"


def reborrow_not_contained(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["loan_projection"]["reborrow_rule"] = "PARENT_OPTIONAL_CHILD_REGION_EQUAL_ALLOWED"


def type_value_identity_conflated(b: dict[str, Any]) -> None:
    normalized = b["hir"]["$defs"]["NormalizedTypeDescriptor"]
    normalized["required"] = ["region_id_or_null" if item == "region_profile_id_or_null" else item for item in normalized["required"]]
    normalized["properties"]["region_id_or_null"] = normalized["properties"].pop("region_profile_id_or_null")


def region_exit_live_loan(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["close_delegation"]["frontier"] = "AFTER_REGION_EXIT"


def suspension_widened(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["suspension_and_isolation"]["ordinary_or_exclusive_cross_suspension"] = "ACCEPT"


def source_diagnostic_replaced(b: dict[str, Any]) -> None:
    b["contract"]["projection_contract"]["diagnostic_bindings"]["escape_or_unresolved_region_relation"] = "MIR_LOAN_UNBALANCED"


def target_overlay_drift(b: dict[str, Any]) -> None:
    b["overlay"]["bindings"][0]["disposition"] = "BOUND_DELEGATED"
    b["overlay"]["bindings"][0]["delegate_feature_id"] = "closure_capture_descriptor_msp"
    feature = next(row for row in b["rows"] if row["feature_id"] == focused.FEATURE)
    target = next(stage for stage in feature["stages"] if stage["stage"] == "DYNAMIC_LOWERING")
    target["evidence_refs"] = ["EV-" + "0" * 64]


def unrelated_or_governance_or_protected_drift(b: dict[str, Any]) -> None:
    feature = next(row for row in b["rows"] if row["feature_id"] != focused.FEATURE)
    feature["stages"][0]["disposition"] = "APPLICABLE_BLOCKED_BY_GAP"
    b["metadata"]["governance"]["github_publication"] = "ENABLED"
    b["overlay"]["guards"]["product_lanes"] = "15_OF_15_PASS"
    b["protected_drift"] = True


def errors_for(b: dict[str, Any]) -> list[str]:
    return focused.validate(
        ROOT,
        contract_override=b["contract"],
        overlay_override=b["overlay"],
        hir_override=b["hir"],
        mir_override=b["mir"],
        lowering_override=b["lowering"],
        bridge_override=b["bridge"],
        machine_override=b["machine"],
        loan_fixture_override=b["loan_fixture"],
        ownership_fixture_override=b["ownership_fixture"],
        borrow_context_fixture_override=b["borrow_context_fixture"],
        escape_override=b["escape"],
        rows_override=b["rows"],
        metadata_override=b["metadata"],
        protected_drift=b.get("protected_drift", False),
    )


def main() -> int:
    normal = focused.validate(ROOT)
    if normal:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal}, indent=2))
        return 1
    base = {
        "contract": focused.load(ROOT / focused.CONTRACT_REL),
        "overlay": focused.load(ROOT / focused.OVERLAY_REL),
        "hir": focused.load(ROOT / focused.HIR_REL),
        "mir": focused.load(ROOT / focused.MIR_REL),
        "lowering": focused.load(ROOT / focused.LOWERING_REL),
        "bridge": focused.load(ROOT / focused.BRIDGE_REL),
        "machine": focused.load(ROOT / focused.MACHINE_REL),
        "loan_fixture": focused.load(ROOT / focused.LOAN_FIXTURE_REL),
        "ownership_fixture": focused.load(ROOT / focused.OWNERSHIP_FIXTURE_REL),
        "borrow_context_fixture": focused.load(ROOT / focused.BORROW_CONTEXT_FIXTURE_REL),
        "escape": focused.load(ROOT / focused.ESCAPE_REL),
        "rows": focused.load(ROOT / focused.ROWS_REL),
        "metadata": focused.load(ROOT / focused.META_REL),
        "protected_drift": False,
    }
    mutations: list[Mutation] = [
        ("IDENTITY_OR_PREDECESSOR_DRIFT", identity_drift),
        ("REGION_KIND_MAP_SWAP", region_kind_map_swap),
        ("DROP_HIR_REGION_TABLE", drop_hir_region_table),
        ("REGION_PARENT_CYCLE", region_parent_cycle_admitted),
        ("HIR_CONSTRAINT_REGION_UNBOUND", unbound_hir_region_constraint),
        ("BORROW_SHARED_DISPATCH_WRONG", shared_dispatch_wrong),
        ("LOAN_ID_CREATED_IN_MIR", loan_id_created_in_mir),
        ("REBORROW_CONTAINMENT_MISMATCH", reborrow_not_contained),
        ("TYPE_VALUE_REGION_CONFLATED", type_value_identity_conflated),
        ("REGION_EXIT_WITH_LIVE_LOAN", region_exit_live_loan),
        ("SUSPENSION_EXCEPTION_WIDENED", suspension_widened),
        ("SOURCE_DIAGNOSTIC_REPLACED", source_diagnostic_replaced),
        ("TARGET_OVERLAY_OR_REF_DRIFT", target_overlay_drift),
        ("UNRELATED_GOVERNANCE_OR_PROTECTED_DRIFT", unrelated_or_governance_or_protected_drift),
    ]
    results = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        errors = errors_for(candidate)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})
    rejected = sum(row["rejected"] for row in results)
    passed = rejected == 14
    print(json.dumps({
        "schema": "deeplus.region-lifetime-dynamic-trace-mutation-receipt/r1",
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
