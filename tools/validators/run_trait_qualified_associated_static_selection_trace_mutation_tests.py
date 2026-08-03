#!/usr/bin/env python3
"""Run exactly 42 in-memory mutations against the R62 focused validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_trait_qualified_associated_static_selection_trace import (
    CONTRACT_REL,
    HM_REL,
    META_REL,
    OVERLAY_REL,
    TRACE_REL,
    load,
    validate,
)


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[..., None]]


def trace_cell(rows: list[dict[str, Any]], feature: str, stage: str, outcome: str | None = None) -> dict[str, Any]:
    row = next(item for item in rows if item["feature_id"] == feature)
    stage_row = next(item for item in row["stages"] if item["stage"] == stage)
    if stage == "CONFORMANCE_TESTS":
        return next(item for item in stage_row["outcomes"] if item["outcome"] == outcome)
    return stage_row


def hm_row(value: dict[str, Any], row_id: str) -> dict[str, Any]:
    return next(row for row in value["rows"] if row["row_id"] == row_id)


def change_disposition(cell: dict[str, Any]) -> None:
    cell["disposition"] = (
        "APPLICABLE_BLOCKED_BY_GAP"
        if cell.get("disposition") == "BOUND_DIRECT"
        else "BOUND_DIRECT"
    )


def main() -> int:
    overlay = load(ROOT / OVERLAY_REL)
    contract = load(ROOT / CONTRACT_REL)
    trace = load(ROOT / TRACE_REL)
    hm = load(ROOT / HM_REL)
    metadata = load(ROOT / META_REL)
    normal_errors = validate(ROOT, overlay, contract, validate_schema=True)
    if normal_errors:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors}, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("OVERLAY_BASELINE_DRIFT", lambda o, c, t, h, m: o.__setitem__("canonical_baseline_commit", "0" * 40)),
        ("CONTRACT_PREDECESSOR_DRIFT", lambda o, c, t, h, m: c.__setitem__("local_predecessor_commit", "0" * 40)),
        ("REVISION_DRIFT", lambda o, c, t, h, m: o.__setitem__("revision", "r63")),
        ("FEATURE_DRIFT", lambda o, c, t, h, m: c["feature_ids"].append("companion_capability_decomposition")),
        ("SOURCE_ACTIVATION_DRIFT", lambda o, c, t, h, m: c.__setitem__("source_activation", "current")),
        ("SCOPE_MISSING_TARGET", lambda o, c, t, h, m: c["scope_fence"]["transitioned_cells"].pop()),
        ("SCOPE_GAP_DRIFT", lambda o, c, t, h, m: c["scope_fence"]["transitioned_cells"][0].__setitem__("predecessor_gap_id", "IR-XCUT-P1-999")),
        ("SCOPE_EXTRA_TRANSITION", lambda o, c, t, h, m: c["scope_fence"].__setitem__("other_feature_transition_count", 1)),
        ("EVIDENCE_MISSING", lambda o, c, t, h, m: o["evidence_entries"].pop()),
        ("EVIDENCE_DUPLICATE", lambda o, c, t, h, m: o["evidence_entries"].append(copy.deepcopy(o["evidence_entries"][0]))),
        ("EVIDENCE_CLASS_DRIFT", lambda o, c, t, h, m: o["evidence_entries"][0].__setitem__("class", "FILE")),
        ("EVIDENCE_PATH_DRIFT", lambda o, c, t, h, m: o["evidence_entries"][0].__setitem__("path", "spec/language.md")),
        ("EVIDENCE_LOCATOR_DRIFT", lambda o, c, t, h, m: o["evidence_entries"][0].__setitem__("locator", "TQASSTC-R007")),
        ("BINDING_MISSING", lambda o, c, t, h, m: o["bindings"].pop()),
        ("BINDING_DUPLICATE", lambda o, c, t, h, m: o["bindings"].append(copy.deepcopy(o["bindings"][0]))),
        ("BINDING_STAGE_DRIFT", lambda o, c, t, h, m: o["bindings"][0].__setitem__("stage", "STATIC_SEMANTICS")),
        ("BINDING_DISPOSITION_DRIFT", lambda o, c, t, h, m: o["bindings"][0].__setitem__("disposition", "BOUND_DELEGATED")),
        ("BINDING_EVIDENCE_KEY_DRIFT", lambda o, c, t, h, m: o["bindings"][0].__setitem__("evidence_keys", ["missing"])),
        ("OVERLAY_CASE_POINTER_DRIFT", lambda o, c, t, h, m: o["acceptance_cases"][0].__setitem__("contract_pointer", "/acceptance_cases/1")),
        ("CASE_ID_DRIFT", lambda o, c, t, h, m: c["acceptance_cases"][0].__setitem__("case_id", "TQASSTC-AC-099")),
        ("CASE_CLASS_DRIFT", lambda o, c, t, h, m: c["acceptance_cases"][3].__setitem__("class", "POSITIVE")),
        ("CASE_DIAGNOSTIC_DRIFT", lambda o, c, t, h, m: c["acceptance_cases"][7].__setitem__("diagnostic_or_null", "TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND")),
        ("CASE_EXECUTION_OVERCLAIM", lambda o, c, t, h, m: c["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
        ("DESCRIPTOR_REQUIRED_FIELDS_DRIFT", lambda o, c, t, h, m: c["descriptor_repair"]["required_fields"].pop()),
        ("DESCRIPTOR_FIELD_COUNT_DRIFT", lambda o, c, t, h, m: c["descriptor_repair"].__setitem__("required_field_count", 6)),
        ("CALLABLE_MAPPING_DRIFT", lambda o, c, t, h, m: c["descriptor_repair"]["implementation_callable_mapping"].__setitem__("cardinality", "MANY_TO_ONE")),
        ("DESCRIPTOR_ERASURE_DRIFT", lambda o, c, t, h, m: c["descriptor_repair"].__setitem__("selected_identity_erased_before_mir", True)),
        ("ASSOCIATED_TYPE_RUNTIME_DRIFT", lambda o, c, t, h, m: c["associated_item_kind_lowering"]["associated_type"].__setitem__("runtime_operation_count", 1)),
        ("ASSOCIATED_VALUE_ROW_DRIFT", lambda o, c, t, h, m: c["associated_item_kind_lowering"]["associated_value"]["lowering_rows"].append("HM-LR-REF-001")),
        ("ASSOCIATED_FUNCTION_PAIR_DRIFT", lambda o, c, t, h, m: c["associated_item_kind_lowering"]["associated_function"].__setitem__("hir_mode_target_pair", "ORDINARY::DIRECT_IMPLEMENTATION")),
        ("OPERATION_ALIGNMENT_DRIFT", lambda o, c, t, h, m: c["existing_operation_alignment"]["reused_operations"].append("RUNTIME_LOOKUP")),
        ("HM_PROFILE_DRIFT", lambda o, c, t, h, m: hm_row(h, "HM-LR-CALL-003").__setitem__("profile_gate", "PREVIEW")),
        ("RUNTIME_LOOKUP_DRIFT", lambda o, c, t, h, m: c["zero_runtime_contract"].__setitem__("runtime_witness_lookup_count", 1)),
        ("PROVIDER_SEARCH_DRIFT", lambda o, c, t, h, m: c["zero_runtime_contract"].__setitem__("provider_search_count", 1)),
        ("ACTIVATION_TRIGGER_DRIFT", lambda o, c, t, h, m: c["zero_runtime_contract"].__setitem__("activation_trigger_count", 1)),
        ("TARGET_TRACE_DISPOSITION_DRIFT", lambda o, c, t, h, m: trace_cell(t, "trait_qualified_associated_static_selection", "DYNAMIC_LOWERING").__setitem__("disposition", "NOT_APPLICABLE")),
        ("RELATED_FEATURE_TRANSITION", lambda o, c, t, h, m: change_disposition(trace_cell(t, "companion_capability_decomposition", "DYNAMIC_LOWERING"))),
        ("OVERLAY_COUNT_DRIFT", lambda o, c, t, h, m: o["counts"].__setitem__("post_overlay_total_bound_direct_cell_count", 2459)),
        ("P0_DRIFT", lambda o, c, t, h, m: c["authority_fence"].__setitem__("semantic_p0", 1)),
        ("P1_DRIFT", lambda o, c, t, h, m: c["authority_fence"].__setitem__("feature_p1", "21_OPEN")),
        ("PRODUCT_OVERCLAIM", lambda o, c, t, h, m: c["authority_fence"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_IMPLEMENTATION_OVERCLAIM", lambda o, c, t, h, m: (o["guards"].__setitem__("github_publication", "ENABLED"), o["guards"].__setitem__("implementation_claim", "COMPLETE"))),
    ]
    if len(mutations) != 42:
        raise AssertionError(f"R62_MUTATION_COUNT:{len(mutations)}")

    results = []
    for mutation_id, mutate in mutations:
        candidate_overlay = copy.deepcopy(overlay)
        candidate_contract = copy.deepcopy(contract)
        candidate_trace = copy.deepcopy(trace)
        candidate_hm = copy.deepcopy(hm)
        candidate_metadata = copy.deepcopy(metadata)
        mutate(candidate_overlay, candidate_contract, candidate_trace, candidate_hm, candidate_metadata)
        errors = validate(ROOT, candidate_overlay, candidate_contract, validate_schema=False, trace_rows_override=candidate_trace, hm_override=candidate_hm, metadata_override=candidate_metadata)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == 42
    print(json.dumps({"schema": "deeplus.trait-qualified-associated-static-selection-trace-mutation-receipt/r1", "result": "PASS" if passed else "FAIL", "normal_path": "PASS", "mutation_count": 42, "rejected_count": rejected, "results": results, "product_execution": "15_OF_15_NOT_RUN", "github_publication": "SUSPENDED"}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
