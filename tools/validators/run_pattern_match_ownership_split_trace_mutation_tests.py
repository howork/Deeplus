#!/usr/bin/env python3
"""Run exact in-memory mutations against the R60 focused validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_pattern_match_ownership_split_trace import (
    CONTRACT_REL,
    HM_REL,
    OVERLAY_REL,
    TRACE_REL,
    load,
    validate,
)


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[
    str,
    Callable[[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]], None],
]


def find_trace_cell(rows: list[dict[str, Any]], feature: str, stage: str) -> dict[str, Any]:
    row = next(item for item in rows if item["feature_id"] == feature)
    return next(item for item in row["stages"] if item["stage"] == stage)


def add_duplicate_binding(
    overlay: dict[str, Any], contract: dict[str, Any], trace: list[dict[str, Any]], hm: dict[str, Any]
) -> None:
    overlay["bindings"].append(copy.deepcopy(overlay["bindings"][0]))


def transition_excluded(
    overlay: dict[str, Any], contract: dict[str, Any], trace: list[dict[str, Any]], hm: dict[str, Any]
) -> None:
    cell = find_trace_cell(trace, "clause_pattern_heads", "STATIC_SEMANTICS")
    cell["disposition"] = (
        "BOUND_DIRECT"
        if cell.get("disposition") != "BOUND_DIRECT"
        else "APPLICABLE_BLOCKED_BY_GAP"
    )


def main() -> int:
    overlay = load(ROOT / OVERLAY_REL)
    contract = load(ROOT / CONTRACT_REL)
    trace = load(ROOT / TRACE_REL)
    hm = load(ROOT / HM_REL)

    normal_errors = validate(ROOT, overlay, contract, validate_schema=True)
    if normal_errors:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors}, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("MISSING_FEATURE", lambda o, c, t, h: o["feature_ids"].pop()),
        ("EXTRA_FEATURE", lambda o, c, t, h: o["feature_ids"].append("clause_pattern_heads")),
        ("MISSING_EVIDENCE", lambda o, c, t, h: o["evidence_entries"].pop()),
        ("EXTRA_EVIDENCE", lambda o, c, t, h: o["evidence_entries"].append(copy.deepcopy(o["evidence_entries"][0]))),
        ("MISSING_BINDING", lambda o, c, t, h: o["bindings"].pop()),
        ("EXTRA_BINDING", add_duplicate_binding),
        ("WRONG_BINDING_CELL", lambda o, c, t, h: o["bindings"][0].__setitem__("stage", "DIAGNOSTICS")),
        ("WRONG_PREDECESSOR", lambda o, c, t, h: o["bindings"][0].__setitem__("predecessor_disposition", "NOT_APPLICABLE")),
        ("WRONG_DISPOSITION", lambda o, c, t, h: o["bindings"][0].__setitem__("disposition", "BOUND_DELEGATED")),
        ("LOCATOR_DRIFT", lambda o, c, t, h: o["evidence_entries"][0].__setitem__("locator", "PMOSTC-R014")),
        ("RULE_ID_DRIFT", lambda o, c, t, h: c["rules"][0].__setitem__("rule_id", "PMOSTC-R099")),
        ("CASE_CLASS_DRIFT", lambda o, c, t, h: c["acceptance_cases"][0].__setitem__("class", "BOUNDARY")),
        ("CASE_EXPECTATION_DRIFT", lambda o, c, t, h: c["acceptance_cases"][5].__setitem__("expected", "UNION")),
        ("CASE_POINTER_DRIFT", lambda o, c, t, h: o["acceptance_cases"][0].__setitem__("contract_pointer", "/acceptance_cases/1")),
        ("SCHEMA_ID_DRIFT", lambda o, c, t, h: o.__setitem__("schema", "deeplus.pattern-match-ownership-split-evidence/r2")),
        ("NORMALIZED_INTERFACE_DRIFT", lambda o, c, t, h: c["ownership_interface"]["normalized_binder_interface_fields"].append("projection_path")),
        ("OWNED_COMMIT_EFFECT_DRIFT", lambda o, c, t, h: c["ownership_interface"]["owned_binding"].__setitem__("final_commit_effect", "MOVE_COMMIT")),
        ("OR_RETRY_DRIFT", lambda o, c, t, h: c["or_alias_ownership_law"]["or_pattern"].__setitem__("retry_count", 1)),
        ("ALIAS_CLONE_DRIFT", lambda o, c, t, h: c["or_alias_ownership_law"]["alias_pattern"].__setitem__("clone_count", 1)),
        ("SUBJECT_EVALUATION_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"].__setitem__("subject_evaluation_count", 2)),
        ("GUARD_CONSUMPTION_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"]["guard"].__setitem__("consumption", "CONSUMING")),
        ("GUARD_ACQUISITION_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"]["guard"].__setitem__("acquisition_count", 1)),
        ("COMMIT_COUNT_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"]["final_commit"].__setitem__("logical_commit_count_on_success", 2)),
        ("COMMIT_ORDER_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"]["final_commit"]["operation_order"].reverse()),
        ("ABORT_OPERATION_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"]["preparation_abort"].__setitem__("operation", "PLACE_MOVE")),
        ("FAILURE_RESIDUE_DRIFT", lambda o, c, t, h: c["probe_guard_commit_law"]["failure_residue"].__setitem__("loan_count", 1)),
        ("LOAN_FRONTIER_DRIFT", lambda o, c, t, h: c["loan_lifetime_and_arm_join_law"].__setitem__("loan_end_frontier", "FUNCTION_EXIT")),
        ("RETURN_JOIN_DRIFT", lambda o, c, t, h: c["loan_lifetime_and_arm_join_law"]["returning_arm_join"].__setitem__("result_capabilities", "UNION")),
        ("EXCLUDED_FEATURE_TRANSITION", transition_excluded),
        ("TARGET_TRACE_DISPOSITION_DRIFT", lambda o, c, t, h: find_trace_cell(t, "pattern_match_ownership_split", "STATIC_SEMANTICS").__setitem__("disposition", "NOT_APPLICABLE")),
        ("PRODUCT_EXECUTION_OVERCLAIM", lambda o, c, t, h: c["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
        ("P1_DRIFT", lambda o, c, t, h: c["authority_fence"].__setitem__("feature_p1", "21_OPEN")),
        ("M13_DRIFT", lambda o, c, t, h: o["guards"].__setitem__("m13_actions", "3_OPEN")),
        ("PRODUCT_LANE_OVERCLAIM", lambda o, c, t, h: c["authority_fence"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_OVERCLAIM", lambda o, c, t, h: o["guards"].__setitem__("github_publication", "ENABLED")),
        ("IMPLEMENTATION_OVERCLAIM", lambda o, c, t, h: o["guards"].__setitem__("implementation_claim", "COMPLETE")),
    ]

    results = []
    for mutation_id, mutate in mutations:
        candidate_overlay = copy.deepcopy(overlay)
        candidate_contract = copy.deepcopy(contract)
        candidate_trace = copy.deepcopy(trace)
        candidate_hm = copy.deepcopy(hm)
        mutate(candidate_overlay, candidate_contract, candidate_trace, candidate_hm)
        errors = validate(
            ROOT,
            candidate_overlay,
            candidate_contract,
            validate_schema=False,
            trace_rows_override=candidate_trace,
            hm_registry_override=candidate_hm,
        )
        results.append(
            {
                "mutation_id": mutation_id,
                "rejected": bool(errors),
                "first_error": errors[0] if errors else None,
            }
        )

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == len(results)
    print(
        json.dumps(
            {
                "schema": "deeplus.pattern-match-ownership-split-trace-mutation-receipt/r1",
                "result": "PASS" if passed else "FAIL",
                "normal_path": "PASS",
                "mutation_count": len(results),
                "rejected_count": rejected,
                "results": results,
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
