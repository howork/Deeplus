#!/usr/bin/env python3
"""Run exact in-memory mutations against the R61 focused validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_pattern_clause_exhaustiveness_trace import (
    CONTRACT_REL,
    CONTEXT_REL,
    FRONTEND_REL,
    HM_REL,
    OVERLAY_REL,
    TRACE_REL,
    load,
    load_predicates,
    validate,
)


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[..., None]]


def find_trace_cell(rows: list[dict[str, Any]], feature: str, stage: str, outcome: str | None = None) -> dict[str, Any]:
    row = next(item for item in rows if item["feature_id"] == feature)
    stage_row = next(item for item in row["stages"] if item["stage"] == stage)
    if stage == "CONFORMANCE_TESTS":
        return next(item for item in stage_row["outcomes"] if item["outcome"] == outcome)
    return stage_row


def find_nested(value: Any, key: str, expected: str) -> dict[str, Any]:
    if isinstance(value, dict):
        if value.get(key) == expected:
            return value
        for child in value.values():
            try:
                return find_nested(child, key, expected)
            except LookupError:
                pass
    elif isinstance(value, list):
        for child in value:
            try:
                return find_nested(child, key, expected)
            except LookupError:
                pass
    raise LookupError(expected)


def main() -> int:
    overlay = load(ROOT / OVERLAY_REL)
    contract = load(ROOT / CONTRACT_REL)
    trace = load(ROOT / TRACE_REL)
    frontend = load(ROOT / FRONTEND_REL)
    context = load(ROOT / CONTEXT_REL)
    hm = load(ROOT / HM_REL)
    predicates = load_predicates(ROOT)

    normal_errors = validate(ROOT, overlay, contract, validate_schema=True)
    if normal_errors:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors}, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("OVERLAY_BASELINE_DRIFT", lambda o, c, t, f, x, h, p: o.__setitem__("canonical_baseline_commit", "0" * 40)),
        ("CONTRACT_PREDECESSOR_DRIFT", lambda o, c, t, f, x, h, p: c.__setitem__("local_predecessor_commit", "0" * 40)),
        ("OVERLAY_REVISION_DRIFT", lambda o, c, t, f, x, h, p: o.__setitem__("revision", "r62")),
        ("CONTRACT_SCHEMA_ID_DRIFT", lambda o, c, t, f, x, h, p: c.__setitem__("schema", "deeplus.pattern-clause-exhaustiveness-trace-closure/r2")),
        ("OVERLAY_SCHEMA_ID_DRIFT", lambda o, c, t, f, x, h, p: o.__setitem__("schema", "deeplus.pattern-clause-exhaustiveness-evidence/r2")),
        ("FEATURE_ORDER_DRIFT", lambda o, c, t, f, x, h, p: o["feature_ids"].reverse()),
        ("MISSING_FEATURE", lambda o, c, t, f, x, h, p: c["feature_ids"].pop()),
        ("SOURCE_ACTIVATION_DRIFT", lambda o, c, t, f, x, h, p: c.__setitem__("source_activation", "current")),
        ("CURRENT_BINDING_DRIFT", lambda o, c, t, f, x, h, p: c.__setitem__("current_binding", True)),
        ("SCOPE_MISSING_TARGET", lambda o, c, t, f, x, h, p: c["scope_fence"]["transitioned_cells"].pop()),
        ("SCOPE_EXTRA_TARGET", lambda o, c, t, f, x, h, p: c["scope_fence"]["transitioned_cells"].append(copy.deepcopy(c["scope_fence"]["transitioned_cells"][0]))),
        ("SCOPE_EXCLUDED_DRIFT", lambda o, c, t, f, x, h, p: c["scope_fence"]["excluded_related_features"].pop()),
        ("NEW_OPERATION_DRIFT", lambda o, c, t, f, x, h, p: c["existing_operation_alignment"].__setitem__("new_operation_count", 1)),
        ("OPERATION_SET_DRIFT", lambda o, c, t, f, x, h, p: c["existing_operation_alignment"]["admitted_operations"].append("CLAUSE_RETRY")),
        ("TERMINATOR_SET_DRIFT", lambda o, c, t, f, x, h, p: c["existing_operation_alignment"]["admitted_terminators"].append("THROW")),
        ("SUBJECT_EVALUATION_DRIFT", lambda o, c, t, f, x, h, p: c["clause_dispatch_and_failure_law"].__setitem__("subject_evaluation_count", 2)),
        ("SOURCE_ORDER_WINNER_DRIFT", lambda o, c, t, f, x, h, p: c["clause_dispatch_and_failure_law"].__setitem__("source_order_role", "FIRST_MATCH_WINS_OVERLAP")),
        ("CLAUSE_ORDER_DRIFT", lambda o, c, t, f, x, h, p: c["clause_dispatch_and_failure_law"]["per_clause_order"].reverse()),
        ("CLAUSE_RETRY_DRIFT", lambda o, c, t, f, x, h, p: c["clause_dispatch_and_failure_law"].__setitem__("selected_clause_retry_count", 1)),
        ("IMPLICIT_FALLBACK_DRIFT", lambda o, c, t, f, x, h, p: c["clause_dispatch_and_failure_law"].__setitem__("implicit_fallback_count", 1)),
        ("CONTROLLING_PREDICATE_DRIFT", lambda o, c, t, f, x, h, p: c["declarative_partition_admission_law"].__setitem__("controlling_predicate_id", "DeclarativeClauseExhaustive")),
        ("PARTITION_ORDER_DRIFT", lambda o, c, t, f, x, h, p: c["declarative_partition_admission_law"]["admission_order"].reverse()),
        ("GUARD_COVERAGE_DRIFT", lambda o, c, t, f, x, h, p: c["declarative_partition_admission_law"].__setitem__("guard_unconditional_coverage_count", 1)),
        ("MATCH_GUARD_SUBTRACTION_DRIFT", lambda o, c, t, f, x, h, p: c["match_exhaustiveness_law"].__setitem__("guarded_arm_coverage_effect", "SUBTRACT")),
        ("MATCH_DIAGNOSTIC_DRIFT", lambda o, c, t, f, x, h, p: c["match_exhaustiveness_law"].__setitem__("any_residual_cell_never_mentioned_diagnostic", "MATCH_NONEXHAUSTIVE_AFTER_GUARDS")),
        ("FOREIGN_CASE_PRECEDENCE_DRIFT", lambda o, c, t, f, x, h, p: c["diagnostic_selection_law"].__setitem__("foreign_case_or_payload_precedence", "COVERAGE_FIRST")),
        ("MULTIPLE_PRIMARY_DRIFT", lambda o, c, t, f, x, h, p: c["diagnostic_selection_law"].__setitem__("single_primary_diagnostic", False)),
        ("FAILURE_RESIDUE_DRIFT", lambda o, c, t, f, x, h, p: c["failure_residue_law"].__setitem__("loan_count", 1)),
        ("MOVE_CANCEL_ORDER_DRIFT", lambda o, c, t, f, x, h, p: c["failure_residue_law"].__setitem__("prepared_move_abort_order", "SOURCE_ORDER")),
        ("RULE_ID_DRIFT", lambda o, c, t, f, x, h, p: c["rules"][0].__setitem__("rule_id", "PCETC-R099")),
        ("RULE_TEXT_EMPTY", lambda o, c, t, f, x, h, p: c["rules"][5].__setitem__("text", "")),
        ("CASE_ID_DRIFT", lambda o, c, t, f, x, h, p: c["acceptance_cases"][0].__setitem__("case_id", "PCETC-AC-099")),
        ("CASE_CLASS_DRIFT", lambda o, c, t, f, x, h, p: c["acceptance_cases"][3].__setitem__("class", "POSITIVE")),
        ("CASE_DIAGNOSTIC_DRIFT", lambda o, c, t, f, x, h, p: c["acceptance_cases"][17].__setitem__("diagnostic_or_null", "MATCH_NOT_EXHAUSTIVE")),
        ("CASE_EXECUTION_OVERCLAIM", lambda o, c, t, f, x, h, p: c["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
        ("CASE_BINDING_DRIFT", lambda o, c, t, f, x, h, p: c["acceptance_bindings"]["clause_pattern_heads"]["BOUNDARY"].pop()),
        ("MISSING_EVIDENCE", lambda o, c, t, f, x, h, p: o["evidence_entries"].pop()),
        ("DUPLICATE_EVIDENCE", lambda o, c, t, f, x, h, p: o["evidence_entries"].append(copy.deepcopy(o["evidence_entries"][0]))),
        ("EVIDENCE_LOCATOR_DRIFT", lambda o, c, t, f, x, h, p: o["evidence_entries"][0].__setitem__("locator", "/acceptance_bindings/clause_pattern_heads/REJECT")),
        ("EVIDENCE_CLASS_DRIFT", lambda o, c, t, f, x, h, p: o["evidence_entries"][0].__setitem__("class", "FILE")),
        ("MISSING_BINDING", lambda o, c, t, f, x, h, p: o["bindings"].pop()),
        ("DUPLICATE_BINDING", lambda o, c, t, f, x, h, p: o["bindings"].append(copy.deepcopy(o["bindings"][0]))),
        ("BINDING_CELL_DRIFT", lambda o, c, t, f, x, h, p: o["bindings"][0].__setitem__("outcome", "POSITIVE")),
        ("BINDING_DISPOSITION_DRIFT", lambda o, c, t, f, x, h, p: o["bindings"][0].__setitem__("disposition", "BOUND_DELEGATED")),
        ("BINDING_EVIDENCE_DRIFT", lambda o, c, t, f, x, h, p: o["bindings"][0].__setitem__("evidence_keys", ["missing"])),
        ("OVERLAY_CASE_POINTER_DRIFT", lambda o, c, t, f, x, h, p: o["acceptance_cases"][0].__setitem__("contract_pointer", "/acceptance_bindings/clause_pattern_heads/REJECT")),
        ("OVERLAY_COUNTS_DRIFT", lambda o, c, t, f, x, h, p: o["counts"].__setitem__("post_overlay_total_bound_direct_cell_count", 2458)),
        ("TARGET_TRACE_DISPOSITION_DRIFT", lambda o, c, t, f, x, h, p: find_trace_cell(t, "clause_pattern_heads", "DYNAMIC_LOWERING").__setitem__("disposition", "NOT_APPLICABLE")),
        ("MATCH_DYNAMIC_TRANSITION", lambda o, c, t, f, x, h, p: find_trace_cell(t, "match_exhaustiveness_phase_a", "DYNAMIC_LOWERING").__setitem__("disposition", "BOUND_DIRECT")),
        ("EXCLUDED_FEATURE_TRANSITION", lambda o, c, t, f, x, h, p: find_trace_cell(t, "clause_pattern_head_semantic_partition_core", "DYNAMIC_LOWERING").__setitem__("disposition", "BOUND_DIRECT")),
        ("FRONTEND_SUBJECT_OWNER_DRIFT", lambda o, c, t, f, x, h, p: find_nested(f, "id", "CLAUSE_FUNCTION_SUBJECT").__setitem__("owner", "ClauseFunction")),
        ("FRONTEND_CLAUSE_LINK_DRIFT", lambda o, c, t, f, x, h, p: find_nested(f, "id", "CLAUSE_FUNCTION").__setitem__("subject", "EXPLICIT_SUBJECT")),
        ("CONTEXT_POLICY_DRIFT", lambda o, c, t, f, x, h, p: find_nested(x, "context_id", "PCTX-DECLARATIVE-CLAUSE").__setitem__("policy_state", "PREVIEW")),
        ("CONTEXT_PATTERN_FAILURE_DRIFT", lambda o, c, t, f, x, h, p: find_nested(x, "context_id", "PCTX-DECLARATIVE-CLAUSE").__setitem__("pattern_failure_disposition", "DECLARATIVE_PARTITION_REJECTION")),
        ("CONTEXT_GUARD_FAILURE_DRIFT", lambda o, c, t, f, x, h, p: find_nested(x, "context_id", "PCTX-DECLARATIVE-CLAUSE").__setitem__("guard_false_disposition", "DECLARATIVE_PARTITION_REJECTION")),
        ("HM_PROFILE_DRIFT", lambda o, c, t, f, x, h, p: find_nested(h, "row_id", "HM-LR-TOP-016").__setitem__("profile_gate", "PREVIEW")),
        ("CLAUSE_PREDICATE_MATURITY_DRIFT", lambda o, c, t, f, x, h, p: find_nested(p, "predicate_id", "DeclarativeClausePartitionAdmitted").__setitem__("predicate_maturity", "placeholder")),
        ("MATCH_PREDICATE_RECEIPT_OVERCLAIM", lambda o, c, t, f, x, h, p: find_nested(p, "predicate_id", "MatchExhaustive").__setitem__("execution_receipt", "PASS")),
        ("P0_DRIFT", lambda o, c, t, f, x, h, p: c["authority_fence"].__setitem__("semantic_p0", 1)),
        ("P1_DRIFT", lambda o, c, t, f, x, h, p: c["authority_fence"].__setitem__("feature_p1", "21_OPEN")),
        ("M13_DRIFT", lambda o, c, t, f, x, h, p: o["guards"].__setitem__("m13_actions", "3_OPEN")),
        ("PRODUCT_LANE_OVERCLAIM", lambda o, c, t, f, x, h, p: c["authority_fence"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_OVERCLAIM", lambda o, c, t, f, x, h, p: o["guards"].__setitem__("github_publication", "ENABLED")),
        ("IMPLEMENTATION_OVERCLAIM", lambda o, c, t, f, x, h, p: o["guards"].__setitem__("implementation_claim", "COMPLETE")),
    ]

    results = []
    for mutation_id, mutate in mutations:
        candidate_overlay = copy.deepcopy(overlay)
        candidate_contract = copy.deepcopy(contract)
        candidate_trace = copy.deepcopy(trace)
        candidate_frontend = copy.deepcopy(frontend)
        candidate_context = copy.deepcopy(context)
        candidate_hm = copy.deepcopy(hm)
        candidate_predicates = copy.deepcopy(predicates)
        mutate(candidate_overlay, candidate_contract, candidate_trace, candidate_frontend, candidate_context, candidate_hm, candidate_predicates)
        errors = validate(
            ROOT,
            candidate_overlay,
            candidate_contract,
            validate_schema=False,
            trace_rows_override=candidate_trace,
            frontend_override=candidate_frontend,
            context_override=candidate_context,
            hm_override=candidate_hm,
            predicates_override=candidate_predicates,
        )
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == len(results)
    print(json.dumps({
        "schema": "deeplus.pattern-clause-exhaustiveness-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": len(results),
        "rejected_count": rejected,
        "results": results,
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
