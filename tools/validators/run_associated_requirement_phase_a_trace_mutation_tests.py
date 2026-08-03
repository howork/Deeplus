#!/usr/bin/env python3
"""Run exactly 24 in-memory mutations against the R64 focused validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_associated_requirement_phase_a_trace_closure as focused


ROOT = Path(__file__).resolve().parents[2]
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/associated-requirement-phase-a-evidence-r1.json"
CONTRACT_REL = "spec/contracts/associated-requirement-phase-a-trace-closure-r1.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
FIXTURE_REL = "tests/fixtures/current/diagnostic-dispatch-closure-r1.json"
CONFORMANCE_REL = "tests/conformance/diagnostic-dispatch-closure/chunks/part-0001.json"
R62_OWNER_REL = "spec/contracts/trait-qualified-associated-static-selection-trace-closure-r1.json"
HIR_REL = "spec/contracts/hir-h1-current-mir-bridge.json"
MIR_REL = "spec/contracts/hir-mir-lowering-registry.json"
DECISION_REL = "decisions/language/Design_Deeplus_R64_Associated_Requirement_Phase_A_Trace_Closure_R1.md"
FEATURE = "associated_requirement_phase_a"

Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def load_json(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def trace_cell(rows: list[dict[str, Any]], feature: str, stage: str, outcome: str | None = None) -> dict[str, Any]:
    row = next(item for item in rows if item["feature_id"] == feature)
    stage_row = next(item for item in row["stages"] if item["stage"] == stage)
    if stage == "CONFORMANCE_TESTS":
        return next(item for item in stage_row["outcomes"] if item["outcome"] == outcome)
    return stage_row


def unrelated_transition(bundle: dict[str, Any]) -> None:
    cell = trace_cell(bundle["trace"], "accessor_property_colon_equals_surface", "STATIC_SEMANTICS")
    cell["disposition"] = (
        "BOUND_DIRECT"
        if cell.get("disposition") != "BOUND_DIRECT"
        else "APPLICABLE_BLOCKED_BY_GAP"
    )


def corrupt_evidence_set(bundle: dict[str, Any]) -> None:
    values = bundle["overlay"]["evidence_entries"]
    values.pop(0)
    values.append(copy.deepcopy(values[0]))
    extra = copy.deepcopy(values[-1])
    extra["evidence_key"] = "R64:associated_requirement_phase_a:EXTRA"
    values.append(extra)


def corrupt_binding_set(bundle: dict[str, Any]) -> None:
    values = bundle["overlay"]["bindings"]
    values.pop(0)
    values.append(copy.deepcopy(values[0]))
    extra = copy.deepcopy(values[-1])
    extra["outcome"] = "EXTRA"
    values.append(extra)


def dynamic_disposition_drift(bundle: dict[str, Any]) -> None:
    row = bundle["overlay"]["bindings"][0]
    row["disposition"] = "BOUND_DIRECT"
    row["not_applicable"] = None


def dynamic_delegate_or_owner_duplication(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["bindings"][0]["delegate_feature_id"] = "trait_qualified_associated_static_selection"
    bundle["contract"]["authority_fence"]["later_use_imported_into_this_contract"] = True


def reject_set_or_rank_drift(bundle: dict[str, Any]) -> None:
    bundle["contract"]["acceptance_bindings"]["REJECT"].pop()
    bundle["overlay"]["acceptance_cases"][3]["acceptance_case_ids"].pop()
    bundle["contract"]["semantic_contract"]["rejection_rank_order"].reverse()


def fixture_execution_or_product_overclaim(bundle: dict[str, Any]) -> None:
    bundle["fixture"]["cases"][0]["execution_status"] = "PASS"
    bundle["fixture"]["product_execution"] = "PASS"
    bundle["conformance"][0]["execution_status"] = "PASS"
    bundle["conformance"][0]["product_support"] = "PASS"


def diagnostic_tuple_drift(bundle: dict[str, Any]) -> None:
    expected = bundle["contract"]["acceptance_cases"][3]["expected_decision"]
    expected["diagnostic_id_or_null"] = "TRAIT_MISSING_WITNESS"
    expected["canonical_culprit_id_or_null"] = "REQ-WRONG"
    expected["emitted_primary_count"] = 2
    expected["later_candidate_status"] = "EVALUATED"


def r62_owner_byte_drift(bundle: dict[str, Any]) -> None:
    bundle["r62_owner"]["descriptor_repair"]["runtime_reconstruction_count"] = 1


def hir_mir_byte_drift(bundle: dict[str, Any]) -> None:
    bundle["hir"]["trait_associated_static_selection_bridge"]["runtime_reconstruction_count"] = 1
    projection = bundle["mir"]["profile_contract"]["trait_associated_static_selection_projection_contract"]
    projection["runtime_reconstruction_or_search_count"] = 1


def derived_count_overlay_binding_drift(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["counts"]["post_overlay_total_bound_direct_cell_count"] = 2462
    bundle["overlay"]["counts"]["post_overlay_cumulative_binding_count"] = 126
    bundle["metadata"]["derived_counts"]["bound_direct_cells"] = 2462
    applied = bundle["metadata"]["applied_evidence_overlays"]
    target = next(row for row in applied if row.get("path") == OVERLAY_REL)
    target["binding_count"] = 5


def p0_p1_m13_drift(bundle: dict[str, Any]) -> None:
    bundle["contract"]["machine_acceptance"]["semantic_p0"] = 1
    bundle["contract"]["governance"]["feature_p1"] = "21_OPEN"
    bundle["overlay"]["guards"]["m13_actions"] = "3_OPEN"


def product_github_overclaim(bundle: dict[str, Any]) -> None:
    bundle["contract"]["governance"]["product_execution"] = "PASS"
    bundle["contract"]["governance"]["github_publication"] = "ENABLED"
    bundle["overlay"]["guards"]["product_lanes"] = "15_OF_15_PASS"
    bundle["overlay"]["guards"]["implementation_claim"] = "COMPLETE"


def validation_errors(bundle: dict[str, Any], *, validate_schema: bool) -> list[str]:
    """Call the R64 validator with every mutable dependency injected in memory."""
    return focused.validate(
        ROOT,
        bundle["overlay"],
        bundle["contract"],
        validate_schema=validate_schema,
        fixture_override=bundle["fixture"],
        conformance_override=bundle["conformance"],
        predicates_override=bundle["predicates"],
        r62_contract_override=bundle["r62_owner"],
        r62_overlay_override=bundle["r62_overlay"],
        hir_bridge_override=bundle["hir"],
        hir_fixture_override=bundle["hir_fixture"],
        hm_registry_override=bundle["mir"],
        trace_rows_override=bundle["trace"],
        metadata_override=bundle["metadata"],
        decision_text_override=bundle["decision_text"],
    )


def main() -> int:
    base = {
        "overlay": load_json(OVERLAY_REL),
        "contract": load_json(CONTRACT_REL),
        "trace": load_json(TRACE_REL),
        "metadata": load_json(META_REL),
        "fixture": load_json(FIXTURE_REL),
        "conformance": load_json(CONFORMANCE_REL),
        "predicates": focused.load_shards(ROOT, focused.PREDICATE_DIR_REL),
        "r62_owner": load_json(R62_OWNER_REL),
        "r62_overlay": load_json(focused.R62_OVERLAY_REL),
        "hir": load_json(HIR_REL),
        "hir_fixture": load_json(focused.HIR_FIXTURE_REL),
        "mir": load_json(MIR_REL),
        "decision_text": (ROOT / DECISION_REL).read_text(encoding="utf-8"),
    }

    normal_errors = validation_errors(base, validate_schema=True)
    if normal_errors:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors}, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("WRONG_CANONICAL_IDENTITY", lambda b: b["overlay"].__setitem__("canonical_baseline_commit", "0" * 40)),
        ("WRONG_LOCAL_IDENTITY", lambda b: b["contract"].__setitem__("local_predecessor_commit", "0" * 40)),
        ("FEATURE_OR_SCOPE_DRIFT", lambda b: (b["overlay"]["feature_ids"].append("trait_witness_coherence_phase_a"), b["contract"].__setitem__("feature_id", "trait_witness_coherence_phase_a"))),
        ("MISSING_EXTRA_OR_DUPLICATE_EVIDENCE", corrupt_evidence_set),
        ("MISSING_EXTRA_OR_DUPLICATE_BINDING", corrupt_binding_set),
        ("DYNAMIC_WRONG_DISPOSITION", dynamic_disposition_drift),
        ("DYNAMIC_WRONG_REASON", lambda b: b["overlay"]["bindings"][0]["not_applicable"].__setitem__("reason_code", "NA_DYNAMIC_REJECTED_BEFORE_LOWERING")),
        ("DYNAMIC_WRONG_AUTHORITY", lambda b: b["overlay"]["bindings"][0]["not_applicable"].__setitem__("authority_boundary", "FRONTEND_AUTHORITY")),
        ("DYNAMIC_DELEGATE_OR_USE_OWNER_DUPLICATION", dynamic_delegate_or_owner_duplication),
        ("POSITIVE_SET_DRIFT", lambda b: (b["contract"]["acceptance_bindings"]["POSITIVE"].pop(), b["overlay"]["acceptance_cases"][1]["acceptance_case_ids"].pop())),
        ("BOUNDARY_SET_DRIFT", lambda b: (b["contract"]["acceptance_bindings"]["BOUNDARY"].append("ARPTC-AC-004"), b["overlay"]["acceptance_cases"][2]["acceptance_case_ids"].append("ARPTC-AC-004"))),
        ("REJECT_SET_OR_RANK_DRIFT", reject_set_or_rank_drift),
        ("FIXTURE_POINTER_DRIFT", lambda b: b["contract"]["acceptance_cases"][0].__setitem__("fixture_pointer", "/cases/1")),
        ("FIXTURE_EXECUTION_STATUS_OR_PRODUCT_OVERCLAIM", fixture_execution_or_product_overclaim),
        ("DIAGNOSTIC_CULPRIT_EMITTED_OR_LATER_DRIFT", diagnostic_tuple_drift),
        ("OWNER_PREDICATE_DRIFT", lambda b: b["contract"]["evidence_scope"].__setitem__("owner_predicate", "AssociatedRequirementWitnessAdmitted")),
        ("SUPPORTING_PREDICATE_PROMOTED_OR_CHANGED", lambda b: (b["contract"]["evidence_scope"].__setitem__("supporting_predicate_role", "CONTROLLING"), b["contract"]["evidence_scope"]["supporting_predicates"].pop())),
        ("R62_OWNER_BYTE_DRIFT", r62_owner_byte_drift),
        ("HIR_OR_MIR_BYTE_DRIFT", hir_mir_byte_drift),
        ("UNRELATED_TRACE_CELL_TRANSITION", unrelated_transition),
        ("DERIVED_COUNT_OVERLAY_OR_BINDING_DRIFT", derived_count_overlay_binding_drift),
        ("P0_P1_OR_M13_DRIFT", p0_p1_m13_drift),
        ("PRODUCT_OR_GITHUB_OVERCLAIM", product_github_overclaim),
        ("DECISION_OR_FOLLOWUP_ABSENCE", lambda b: b.__setitem__("decision_text", b["decision_text"].replace("IR-TRACE-P1-056", ""))),
    ]
    if len(mutations) != 24:
        raise AssertionError(f"R64_MUTATION_COUNT:{len(mutations)}")

    results = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        errors = validation_errors(candidate, validate_schema=False)
        results.append({
            "mutation_id": mutation_id,
            "rejected": bool(errors),
            "first_error": errors[0] if errors else None,
        })

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == 24
    print(json.dumps({
        "schema": "deeplus.associated-requirement-phase-a-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": 24,
        "rejected_count": rejected,
        "results": results,
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
