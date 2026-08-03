#!/usr/bin/env python3
"""Validate the bounded R61 pattern-clause/exhaustiveness trace closure."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/pattern-clause-exhaustiveness-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/pattern-clause-exhaustiveness-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/pattern-clause-exhaustiveness-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/pattern-clause-exhaustiveness-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
CONTEXT_REL = "spec/patterns/pattern-context-policies.json"
HM_REL = "spec/contracts/hir-mir-lowering-registry.json"
PREDICATE_DIR_REL = "spec/types/predicates/chunks"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "2db4f483ffdcb281ef765def67e510e63917500c"
FEATURES = ["clause_pattern_heads", "match_exhaustiveness_phase_a"]
TARGET_CELLS = {
    ("clause_pattern_heads", "DYNAMIC_LOWERING", None),
    ("clause_pattern_heads", "CONFORMANCE_TESTS", "BOUNDARY"),
    ("clause_pattern_heads", "CONFORMANCE_TESTS", "REJECT"),
    ("match_exhaustiveness_phase_a", "CONFORMANCE_TESTS", "BOUNDARY"),
    ("match_exhaustiveness_phase_a", "CONFORMANCE_TESTS", "REJECT"),
}
EXCLUDED_FEATURES = [
    "clause_pattern_head_semantic_partition_core",
    "declarative_clause_pattern_head_law",
    "declarative_function_clause_block_msp",
    "match_otherwise_default_arm",
    "pattern_match_ownership_split",
]
PRIOR_OVERLAYS = [
    "spec/traceability/implementation-target-profile-r1/scalar-numeric-fixed-operator-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/pattern-dynamic-lowering-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/pattern-match-ownership-split-evidence-r1.json",
]
RULE_IDS = [f"PCETC-R{index:03d}" for index in range(1, 17)]
CASE_IDS = [f"PCETC-AC-{index:03d}" for index in range(1, 23)]
CASE_EXPECTATIONS = [
    ("POSITIVE", "clause_pattern_heads", "ADMIT_EXACT_EXHAUSTIVE_PARTITION_AND_ONE_SELECTED_RETURN", None),
    ("POSITIVE", "clause_pattern_heads", "ADMIT_CURRENT_FINITE_LIST_LENGTH_PARTITION", None),
    ("POSITIVE", "clause_pattern_heads", "IMPORT_R60_ONE_ATOMIC_COMMIT_THEN_RETURN", None),
    ("BOUNDARY", "clause_pattern_heads", "NEXT_DECLARATIVE_CLAUSE_WITH_ZERO_FIRST_ATTEMPT_RESIDUE", None),
    ("BOUNDARY", "clause_pattern_heads", "NEXT_DECLARATIVE_CLAUSE_AFTER_FALSE_GUARD_WITH_ZERO_RESIDUE", None),
    ("BOUNDARY", "clause_pattern_heads", "OTHERWISE_COVERS_EXACT_NONEMPTY_REMAINDER", None),
    ("BOUNDARY", "clause_pattern_heads", "TERMINATING_BODY_EXCLUDED_FROM_RETURN_VALUE_JOIN", None),
    ("REJECT", "clause_pattern_heads", "REJECT_FIRST_SOURCE_ORDERED_OVERLAP_BEFORE_LOWERING", "DECL_CLAUSE_OVERLAP"),
    ("REJECT", "clause_pattern_heads", "REJECT_UNKNOWN_DISJOINTNESS_BEFORE_LOWERING", "DECL_CLAUSE_DISJOINTNESS_UNPROVEN"),
    ("REJECT", "clause_pattern_heads", "REJECT_NONEMPTY_REMAINDER_BEFORE_LOWERING", "DECL_CLAUSE_NONEXHAUSTIVE"),
    ("REJECT", "clause_pattern_heads", "REJECT_NON_R0_GUARD_BEFORE_PARTITION_LOWERING", "DECL_CLAUSE_GUARD_NOT_GUARD_SAFE"),
    ("REJECT", "clause_pattern_heads", "REJECT_RESULT_TYPE_BEFORE_MIR_EMISSION", "DECL_CLAUSE_RESULT_TYPE_MISMATCH"),
    ("BOUNDARY", "match_exhaustiveness_phase_a", "ADMIT_EXACT_CLOSED_ENUM_COVERAGE", None),
    ("BOUNDARY", "match_exhaustiveness_phase_a", "ADMIT_SUBJECT_RESTRICTED_SUBSET_COVERAGE", None),
    ("BOUNDARY", "match_exhaustiveness_phase_a", "GUARDED_ARM_MENTIONS_WITHOUT_SUBTRACTION_AND_UNGUARDED_ARM_REMAINS_REACHABLE", None),
    ("BOUNDARY", "match_exhaustiveness_phase_a", "ADMIT_OTHERWISE_AS_EXACT_REMAINDER", None),
    ("BOUNDARY", "match_exhaustiveness_phase_a", "ADMIT_FINITE_SYMBOLIC_SPLIT_WITH_COMPLEMENT", None),
    ("REJECT", "match_exhaustiveness_phase_a", "REJECT_UNREACHABLE_ORDINARY_ARM", "MATCH_ARM_UNREACHABLE"),
    ("REJECT", "match_exhaustiveness_phase_a", "REJECT_UNREACHABLE_OTHERWISE", "OTHERWISE_UNREACHABLE"),
    ("REJECT", "match_exhaustiveness_phase_a", "REJECT_GUARD_ONLY_COVERAGE", "MATCH_NONEXHAUSTIVE_AFTER_GUARDS"),
    ("REJECT", "match_exhaustiveness_phase_a", "REJECT_NEVER_MENTIONED_RESIDUAL", "MATCH_NOT_EXHAUSTIVE"),
    ("REJECT", "match_exhaustiveness_phase_a", "REJECT_CASE_OR_PAYLOAD_BEFORE_COVERAGE_DIAGNOSTIC", "ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH"),
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def find_objects(value: Any, key: str, accepted: set[str]) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    if isinstance(value, dict):
        candidate = value.get(key)
        if candidate in accepted:
            found[candidate] = value
        for child in value.values():
            found.update(find_objects(child, key, accepted))
    elif isinstance(value, list):
        for child in value:
            found.update(find_objects(child, key, accepted))
    return found


def trace_cells(rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, str, str | None], dict[str, Any]], int]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        feature = row.get("feature_id")
        for stage in row.get("stages", []):
            stage_name = stage.get("stage")
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                identity = (feature, stage_name, outcome)
                duplicates += identity in cells
                cells[identity] = cell
    return cells, duplicates


def disposition_counts(values: dict[tuple[str, str, str | None], str]) -> tuple[int, int, int, int]:
    counts = Counter(values.values())
    return tuple(counts[key] for key in ("BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE", "APPLICABLE_BLOCKED_BY_GAP"))


def load_predicates(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / PREDICATE_DIR_REL).glob("*.json")):
        value = load(path)
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))
        elif isinstance(value, dict):
            for key in ("predicates", "rows", "items"):
                if isinstance(value.get(key), list):
                    rows.extend(row for row in value[key] if isinstance(row, dict))
                    break
    return rows


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    *,
    validate_schema: bool = True,
    trace_rows_override: list[dict[str, Any]] | None = None,
    frontend_override: dict[str, Any] | None = None,
    context_override: dict[str, Any] | None = None,
    hm_override: dict[str, Any] | None = None,
    predicates_override: list[dict[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    if validate_schema:
        try:
            import jsonschema

            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(load(root / OVERLAY_SCHEMA_REL)).validate(overlay)
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"JSON_SCHEMA:{exc}")

    for value, prefix in ((contract, "CONTRACT"), (overlay, "OVERLAY")):
        require(value.get("canonical_baseline_commit") == BASELINE, f"{prefix}_BASELINE")
        require(value.get("local_predecessor_commit") == PREDECESSOR, f"{prefix}_PREDECESSOR")
        require(value.get("feature_ids") == FEATURES, f"{prefix}_FEATURE_EXACT")
        require(value.get("revision") == "r61-local-pattern-clause-exhaustiveness-trace-closure-r1", f"{prefix}_REVISION")

    require(contract.get("schema") == "deeplus.pattern-clause-exhaustiveness-trace-closure/r1", "CONTRACT_SCHEMA_ID")
    require(contract.get("candidate_status") == "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE", "CONTRACT_STATUS")
    require(contract.get("language_status") == "STABLE_DESIGN", "CONTRACT_LANGUAGE_STATUS")
    require(contract.get("source_activation") == "none" and contract.get("current_binding") is False, "CONTRACT_NONACTIVATING")
    require(overlay.get("schema") == "deeplus.pattern-clause-exhaustiveness-evidence/r1", "OVERLAY_SCHEMA_ID")
    require(overlay.get("candidate_status") == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY", "OVERLAY_STATUS")

    expected_transitions = [
        {"feature_id": "clause_pattern_heads", "stage": "DYNAMIC_LOWERING", "outcome": None, "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "BOUND_DIRECT"},
        {"feature_id": "clause_pattern_heads", "stage": "CONFORMANCE_TESTS", "outcome": "BOUNDARY", "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "BOUND_DIRECT"},
        {"feature_id": "clause_pattern_heads", "stage": "CONFORMANCE_TESTS", "outcome": "REJECT", "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "BOUND_DIRECT"},
        {"feature_id": "match_exhaustiveness_phase_a", "stage": "CONFORMANCE_TESTS", "outcome": "BOUNDARY", "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "BOUND_DIRECT"},
        {"feature_id": "match_exhaustiveness_phase_a", "stage": "CONFORMANCE_TESTS", "outcome": "REJECT", "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "BOUND_DIRECT"},
    ]
    scope = contract.get("scope_fence", {})
    require(scope.get("transitioned_cells") == expected_transitions, "SCOPE_EXACT_FIVE_CELLS")
    require(scope.get("excluded_related_features") == EXCLUDED_FEATURES, "SCOPE_EXACT_EXCLUDED_FEATURES")
    require(scope.get("excluded_related_feature_transition_count") == 0 and scope.get("other_target_cell_transition_count") == 0, "SCOPE_ZERO_OTHER_TRANSITIONS")

    operations = contract.get("existing_operation_alignment", {})
    require(operations.get("new_operation_count") == 0, "OPERATIONS_ZERO_NEW")
    require([operations.get(key) for key in ("match_row_id", "pattern_attempt_row_id", "return_to_row_id")] == ["HM-LR-TOP-010", "HM-LR-TOP-016", "HM-LR-TOP-026"], "OPERATIONS_TOP_ROWS_EXACT")
    require(operations.get("admitted_operations") == ["PATTERN_PROBE", "TOTAL_PROJECTION", "MOVE_RESERVE", "PLACE_MOVE", "MOVE_CANCEL", "LOAN_BEGIN_SHARED", "LOAN_END", "BINDING_COMMIT"], "OPERATIONS_EXACT_SET")
    require(operations.get("admitted_terminators") == ["COND_BR", "SWITCH_ENUM", "LEAVE"], "TERMINATORS_EXACT_SET")

    frontend = frontend_override or load(root / FRONTEND_REL)
    frontend_ids = find_objects(frontend, "id", {"CLAUSE_FUNCTION", "CLAUSE_FUNCTION_SUBJECT"})
    require(set(frontend_ids) == {"CLAUSE_FUNCTION", "CLAUSE_FUNCTION_SUBJECT"}, "FRONTEND_EXISTING_IDENTITIES")
    require(frontend_ids.get("CLAUSE_FUNCTION_SUBJECT", {}).get("owner") == "MatchArmSequence", "FRONTEND_SUBJECT_OWNER")
    require(frontend_ids.get("CLAUSE_FUNCTION", {}).get("subject") == "CLAUSE_FUNCTION_SUBJECT", "FRONTEND_CLAUSE_SUBJECT_LINK")

    context = context_override or load(root / CONTEXT_REL)
    contexts = find_objects(context, "context_id", {"PCTX-DECLARATIVE-CLAUSE"})
    require(set(contexts) == {"PCTX-DECLARATIVE-CLAUSE"}, "CONTEXT_POLICY_EXISTS")
    clause_context = contexts.get("PCTX-DECLARATIVE-CLAUSE", {})
    require(clause_context.get("policy_state") == "CURRENT", "CONTEXT_POLICY_CURRENT")
    require(clause_context.get("pattern_failure_disposition") == "NEXT_DECLARATIVE_CLAUSE", "CONTEXT_PATTERN_FAILURE_NEXT_CLAUSE")
    require(clause_context.get("guard_false_disposition") == "NEXT_DECLARATIVE_CLAUSE", "CONTEXT_GUARD_FALSE_NEXT_CLAUSE")

    hm = hm_override or load(root / HM_REL)
    hm_ids = find_objects(hm, "row_id", {"HM-LR-TOP-010", "HM-LR-TOP-016", "HM-LR-TOP-026"})
    require(set(hm_ids) == {"HM-LR-TOP-010", "HM-LR-TOP-016", "HM-LR-TOP-026"}, "HM_ROWS_EXIST")
    require(all(row.get("profile_gate") == "CURRENT" for row in hm_ids.values()), "HM_ROWS_CURRENT")

    predicates = predicates_override if predicates_override is not None else load_predicates(root)
    predicate_map = {row.get("predicate_id"): row for row in predicates if row.get("predicate_id") in {"DeclarativeClausePartitionAdmitted", "MatchExhaustive"}}
    require(set(predicate_map) == {"DeclarativeClausePartitionAdmitted", "MatchExhaustive"}, "PREDICATES_EXIST")
    require(predicate_map.get("DeclarativeClausePartitionAdmitted", {}).get("predicate_maturity") == "design_algorithm", "CLAUSE_PREDICATE_MATURITY")
    require(predicate_map.get("DeclarativeClausePartitionAdmitted", {}).get("execution_receipt") is None, "CLAUSE_PREDICATE_NOT_RUN")
    require(predicate_map.get("MatchExhaustive", {}).get("predicate_maturity") == "design_algorithm", "MATCH_PREDICATE_MATURITY")
    require(predicate_map.get("MatchExhaustive", {}).get("execution_receipt") is None, "MATCH_PREDICATE_NOT_RUN")

    clause = contract.get("clause_dispatch_and_failure_law", {})
    require(clause.get("input_supply_id") == "CLAUSE_FUNCTION_SUBJECT" and clause.get("input_owner") == "MatchArmSequence", "CLAUSE_INPUT_IDENTITY")
    require(clause.get("subject_evaluation_count") == 1, "CLAUSE_SUBJECT_ONCE")
    require(clause.get("source_order_role") == "DETERMINISTIC_PROBE_ORDER_NOT_SEMANTIC_TIEBREAKER", "CLAUSE_SOURCE_ORDER_NOT_WINNER")
    require(clause.get("per_clause_order") == ["PATTERN_ATTEMPT", "CHILD_PATTERN_PROBE_AND_PROJECTION", "OPTIONAL_PURE_R0_GUARD", "R60_ATOMIC_OWNERSHIP_AND_BINDING_COMMIT", "SELECTED_BODY_ONCE", "DECLARED_RETURN_CHECK", "RETURN_TO_LEAVE"], "CLAUSE_EXACT_LOWERING_ORDER")
    require(clause.get("pattern_mismatch_runtime_edge") == "NEXT_DECLARATIVE_CLAUSE" and clause.get("false_guard_runtime_edge") == "NEXT_DECLARATIVE_CLAUSE", "CLAUSE_FAILURE_NEXT")
    require(clause.get("selected_body_evaluation_count") == 1 and clause.get("selected_clause_retry_count") == 0 and clause.get("backtracking_count") == 0, "CLAUSE_ONCE_NO_RETRY")
    require(clause.get("terminal_all_failed_edge") == "UNREACHABLE_AFTER_STATIC_ADMISSION" and clause.get("implicit_fallback_count") == 0 and clause.get("pattern_match_defect_count") == 0, "CLAUSE_NO_RUNTIME_FALLBACK")

    partition = contract.get("declarative_partition_admission_law", {})
    require(partition.get("controlling_predicate_id") == "DeclarativeClausePartitionAdmitted", "PARTITION_CONTROLLING_PREDICATE")
    require(partition.get("supporting_noncontrolling_predicate_id") == "DeclarativeClauseExhaustive", "PARTITION_SUPPORTING_PREDICATE")
    require(partition.get("context_policy_id") == "PCTX-DECLARATIVE-CLAUSE", "PARTITION_CONTEXT")
    require(partition.get("admission_order") == ["NORMALIZE_FINITE_SUBJECT_PARTITION", "INTERSECT_SOURCE_ORDERED_HEADS_AND_R0_GUARDS", "REJECT_FIRST_NONEMPTY_OVERLAP", "REJECT_UNDECIDABLE_DISJOINTNESS", "SUBTRACT_UNCONDITIONAL_COVERAGE", "FINAL_OTHERWISE_COVERS_EXACT_REMAINDER", "REJECT_NONEMPTY_REMAINDER", "ADMIT"], "PARTITION_ORDER_EXACT")
    require(partition.get("guard_unconditional_coverage_count") == 0 and partition.get("implicit_option_result_throws_arm_count") == 0, "PARTITION_ZERO_IMPLICIT_COVERAGE")

    match = contract.get("match_exhaustiveness_law", {})
    require(match.get("controlling_predicate_id") == "MatchExhaustive", "MATCH_CONTROLLING_PREDICATE")
    require(match.get("unguarded_reachable_arm_coverage_effect") == "SUBTRACT" and match.get("guarded_arm_coverage_effect") == "MENTION_ONLY_NO_SUBTRACTION", "MATCH_GUARDED_NO_SUBTRACTION")
    require([match.get(key) for key in ("ordinary_arm_empty_residual_diagnostic", "otherwise_empty_residual_diagnostic", "all_residual_cells_guard_mentioned_diagnostic", "any_residual_cell_never_mentioned_diagnostic")] == ["MATCH_ARM_UNREACHABLE", "OTHERWISE_UNREACHABLE", "MATCH_NONEXHAUSTIVE_AFTER_GUARDS", "MATCH_NOT_EXHAUSTIVE"], "MATCH_DIAGNOSTIC_DISPATCH_EXACT")
    require(match.get("sealed_class_without_constructor_pattern_cell_count") == 0 and match.get("implicit_default_arm_count") == 0, "MATCH_ZERO_IMPLICIT_CELLS")

    diagnostics = contract.get("diagnostic_selection_law", {})
    require(diagnostics.get("foreign_case_or_payload_precedence") == "ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH_BEFORE_COVERAGE_DIAGNOSTICS", "DIAGNOSTIC_FOREIGN_CASE_PRECEDENCE")
    require(diagnostics.get("single_primary_diagnostic") is True and diagnostics.get("product_checker_execution") == "NOT_RUN", "DIAGNOSTIC_SINGLE_PRIMARY_NOT_RUN")
    require(diagnostics.get("clause_diagnostics") == ["DECL_CLAUSE_GUARD_NOT_GUARD_SAFE", "DECL_CLAUSE_DISJOINTNESS_UNPROVEN", "DECL_CLAUSE_OVERLAP", "DECL_CLAUSE_NONEXHAUSTIVE", "DECL_CLAUSE_RESULT_TYPE_MISMATCH"], "DIAGNOSTICS_CLAUSE_EXACT")
    require(diagnostics.get("match_diagnostics") == ["MATCH_ARM_UNREACHABLE", "OTHERWISE_UNREACHABLE", "MATCH_NONEXHAUSTIVE_AFTER_GUARDS", "MATCH_NOT_EXHAUSTIVE", "ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH"], "DIAGNOSTICS_MATCH_EXACT")

    residue = contract.get("failure_residue_law", {})
    require(all(residue.get(key) == 0 for key in ("binding_count", "move_count", "loan_count", "view_count", "authority_count", "reservation_count")), "FAILURE_ZERO_RESIDUE")
    require(residue.get("prepared_move_abort_operation") == "MOVE_CANCEL" and residue.get("prepared_move_abort_order") == "REVERSE_ACQUISITION_ORDER", "FAILURE_MOVE_CANCEL_REVERSE")
    require(residue.get("loan_acquisition_timing") == "FINAL_COMMIT_ONLY", "FAILURE_LOAN_FINAL_ONLY")

    rules = contract.get("rules", [])
    require([row.get("rule_id") for row in rules] == RULE_IDS, "RULE_IDS_EXACT_16")
    require(all(isinstance(row.get("text"), str) and row.get("text") for row in rules), "RULE_TEXTS_NONEMPTY")
    cases = contract.get("acceptance_cases", [])
    require([row.get("case_id") for row in cases] == CASE_IDS, "CASE_IDS_EXACT_22")
    require([(row.get("class"), row.get("feature_id"), row.get("expected"), row.get("diagnostic_or_null")) for row in cases] == CASE_EXPECTATIONS, "CASE_SEMANTICS_EXACT_22")
    require(all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in cases), "CASE_NOT_RUN")
    expected_case_bindings = {
        "clause_pattern_heads": {"BOUNDARY": CASE_IDS[3:7], "REJECT": CASE_IDS[7:12]},
        "match_exhaustiveness_phase_a": {"BOUNDARY": CASE_IDS[12:17], "REJECT": CASE_IDS[17:22]},
    }
    require(contract.get("acceptance_bindings") == expected_case_bindings, "CASE_BINDINGS_EXACT_4_5_5_5")

    entries = overlay.get("evidence_entries", [])
    entry_by_key = {row.get("evidence_key"): row for row in entries}
    expected_entries = {
        "R61:clause_pattern_heads:CONFORMANCE_TESTS:BOUNDARY": ("ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/clause_pattern_heads/BOUNDARY", "CONFORMANCE_TESTS:BOUNDARY"),
        "R61:clause_pattern_heads:CONFORMANCE_TESTS:REJECT": ("ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/clause_pattern_heads/REJECT", "CONFORMANCE_TESTS:REJECT"),
        "R61:clause_pattern_heads:DYNAMIC_LOWERING:STRUCTURAL": ("CONTRACT_RULE_ID", "REGISTRY_ID", "PCETC-R006", "DYNAMIC_LOWERING"),
        "R61:match_exhaustiveness_phase_a:CONFORMANCE_TESTS:BOUNDARY": ("ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/match_exhaustiveness_phase_a/BOUNDARY", "CONFORMANCE_TESTS:BOUNDARY"),
        "R61:match_exhaustiveness_phase_a:CONFORMANCE_TESTS:REJECT": ("ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/match_exhaustiveness_phase_a/REJECT", "CONFORMANCE_TESTS:REJECT"),
    }
    require(len(entries) == 5 and len(entry_by_key) == 5 and set(entry_by_key) == set(expected_entries), "OVERLAY_EVIDENCE_EXACT_5")
    bindings = overlay.get("bindings", [])
    binding_by_cell = {(row.get("feature_id"), row.get("stage"), row.get("outcome")): row for row in bindings}
    require(len(bindings) == 5 and len(binding_by_cell) == 5 and set(binding_by_cell) == TARGET_CELLS, "OVERLAY_BINDINGS_EXACT_5")
    for cell in TARGET_CELLS:
        row = binding_by_cell.get(cell, {})
        require(row.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP", f"OVERLAY_PREDECESSOR:{cell}")
        require(row.get("disposition") == "BOUND_DIRECT", f"OVERLAY_DISPOSITION:{cell}")
        require(isinstance(row.get("evidence_keys"), list) and len(row.get("evidence_keys", [])) == 1, f"OVERLAY_ONE_EVIDENCE:{cell}")
        require(row.get("delegate_feature_id") is None and row.get("not_applicable") is None, f"OVERLAY_DIRECT_SHAPE:{cell}")
        for key in row.get("evidence_keys", []):
            require(key in entry_by_key, f"OVERLAY_EVIDENCE_RESOLVES:{cell}")
    for key, expected in expected_entries.items():
        row = entry_by_key.get(key, {})
        require(row.get("path") == CONTRACT_REL, f"OVERLAY_EVIDENCE_PATH:{row.get('evidence_key')}")
        require((row.get("class"), row.get("locator_kind"), row.get("locator"), row.get("stage_role")) == expected, f"OVERLAY_EVIDENCE_SHAPE:{key}")
        locator_kind = row.get("locator_kind")
        locator = row.get("locator")
        if locator_kind == "JSON_POINTER":
            try:
                resolved = resolve_pointer(contract, locator)
            except (KeyError, IndexError, TypeError, ValueError):
                resolved = None
            require(resolved is not None, f"OVERLAY_EVIDENCE_POINTER:{row.get('evidence_key')}")
        else:
            require(locator_kind == "REGISTRY_ID" and locator in RULE_IDS, f"OVERLAY_EVIDENCE_LOCATOR:{row.get('evidence_key')}")

    overlay_cases = overlay.get("acceptance_cases", [])
    expected_overlay_cases = [
        ("R61-TRACE-001", "clause_pattern_heads", "BOUNDARY", "/acceptance_bindings/clause_pattern_heads/BOUNDARY", CASE_IDS[3:7]),
        ("R61-TRACE-002", "clause_pattern_heads", "REJECT", "/acceptance_bindings/clause_pattern_heads/REJECT", CASE_IDS[7:12]),
        ("R61-TRACE-003", "match_exhaustiveness_phase_a", "BOUNDARY", "/acceptance_bindings/match_exhaustiveness_phase_a/BOUNDARY", CASE_IDS[12:17]),
        ("R61-TRACE-004", "match_exhaustiveness_phase_a", "REJECT", "/acceptance_bindings/match_exhaustiveness_phase_a/REJECT", CASE_IDS[17:22]),
    ]
    require(len(overlay_cases) == 4, "OVERLAY_CASES_EXACT_4")
    for index, expected in enumerate(expected_overlay_cases):
        row = overlay_cases[index] if index < len(overlay_cases) else {}
        case_id, feature_id, outcome, pointer, acceptance_ids = expected
        require((row.get("case_id"), row.get("feature_id"), row.get("outcome"), row.get("contract_pointer")) == (case_id, feature_id, outcome, pointer), f"OVERLAY_CASE_IDENTITY:{index}")
        try:
            resolved = resolve_pointer(contract, pointer)
        except (KeyError, IndexError, TypeError, ValueError):
            resolved = None
        require(resolved == acceptance_ids and row.get("acceptance_case_ids") == acceptance_ids, f"OVERLAY_CASE_POINTER_RESOLVES:{index}")
        require(row.get("disposition") == "BOUND_DIRECT" and row.get("delegate_feature_id") is None, f"OVERLAY_CASE_DIRECT:{index}")
        require(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"OVERLAY_CASE_NOT_RUN:{index}")

    expected_counts = {
        "feature_count": 2,
        "evidence_entry_count": 5,
        "binding_count": 5,
        "contract_acceptance_case_count": 22,
        "acceptance_binding_set_count": 4,
        "acceptance_bound_case_count": 19,
        "acceptance_stage_transition_count": 4,
        "predecessor_blocked_cell_count": 5,
        "overlay_bound_direct_transition_count": 5,
        "overlay_bound_delegated_transition_count": 0,
        "overlay_not_applicable_transition_count": 0,
        "predecessor_cumulative_overlay_binding_count": 115,
        "post_overlay_cumulative_binding_count": 120,
        "predecessor_total_bound_direct_cell_count": 2452,
        "predecessor_total_bound_delegated_cell_count": 3,
        "predecessor_total_not_applicable_cell_count": 502,
        "predecessor_total_blocked_cell_count": 1264,
        "post_overlay_total_bound_direct_cell_count": 2457,
        "post_overlay_total_bound_delegated_cell_count": 3,
        "post_overlay_total_not_applicable_cell_count": 502,
        "post_overlay_total_blocked_cell_count": 1259,
        "post_overlay_missing_cell_count": 0,
        "post_overlay_conflict_cell_count": 0,
    }
    require(overlay.get("counts") == expected_counts, "OVERLAY_COUNTS_EXACT")

    prior_binding_count = sum(len(load(root / rel).get("bindings", [])) for rel in PRIOR_OVERLAYS)
    require(prior_binding_count == 115, "PRIOR_OVERLAY_BINDINGS_EXACT_115")
    trace_rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    trace, duplicate_count = trace_cells(trace_rows)
    require(len(trace_rows) == 469 and len({row.get("feature_id") for row in trace_rows}) == 469, "TRACE_FEATURES_EXACT_469")
    require(len(trace) == 4221 and duplicate_count == 0, "TRACE_CELLS_EXACT_UNIQUE_4221")
    raw = {cell: row.get("disposition") for cell, row in trace.items()}
    require(disposition_counts(raw) in {(2452, 3, 502, 1264), (2457, 3, 502, 1259)}, "TRACE_INSTALLED_PRE_OR_POST_COUNTS")
    pre = dict(raw)
    for cell in TARGET_CELLS:
        require(raw.get(cell) in {"APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT"}, f"TRACE_TARGET_PRE_OR_POST:{cell}")
        pre[cell] = "APPLICABLE_BLOCKED_BY_GAP"
    require(disposition_counts(pre) == (2452, 3, 502, 1264), "TRACE_PREDECESSOR_COUNTS_EXACT")
    post = dict(pre)
    for cell in TARGET_CELLS:
        post[cell] = "BOUND_DIRECT"
    require(disposition_counts(post) == (2457, 3, 502, 1259), "TRACE_POST_COUNTS_EXACT")
    require({cell for cell in pre if pre[cell] != post[cell]} == TARGET_CELLS, "TRACE_ONLY_FIVE_TARGET_CELLS_CHANGED")
    require(all(pre[cell] == post[cell] for cell in pre if cell not in TARGET_CELLS), "TRACE_ALL_OTHER_CELLS_UNCHANGED")
    match_dynamic = ("match_exhaustiveness_phase_a", "DYNAMIC_LOWERING", None)
    require(pre.get(match_dynamic) == "NOT_APPLICABLE" and post.get(match_dynamic) == "NOT_APPLICABLE", "TRACE_MATCH_DYNAMIC_STAYS_NOT_APPLICABLE")
    for feature in EXCLUDED_FEATURES:
        feature_cells = [cell for cell in pre if cell[0] == feature]
        require(len(feature_cells) == 9, f"TRACE_EXCLUDED_FEATURE_CELLS_EXACT_9:{feature}")
        require(all(pre[cell] == post[cell] for cell in feature_cells), f"TRACE_EXCLUDED_FEATURE_UNCHANGED:{feature}")
    if disposition_counts(raw) == (2457, 3, 502, 1259):
        require(raw == post, "TRACE_INSTALLED_POST_EXACT")

    require(contract.get("machine_acceptance") == {
        "feature_count": 2, "rule_count": 16, "acceptance_case_count": 22, "positive_case_count": 3,
        "boundary_case_count": 9, "reject_case_count": 10, "acceptance_binding_set_count": 4,
        "acceptance_bound_case_count": 19, "overlay_binding_count": 5, "predecessor_blocked_cell_count": 5,
        "overlay_bound_direct_transition_count": 5, "overlay_bound_delegated_transition_count": 0,
        "overlay_not_applicable_transition_count": 0, "predecessor_cumulative_overlay_binding_count": 115,
        "post_overlay_cumulative_binding_count": 120, "predecessor_total_bound_direct_cell_count": 2452,
        "predecessor_total_bound_delegated_cell_count": 3, "predecessor_total_not_applicable_cell_count": 502,
        "predecessor_total_blocked_cell_count": 1264, "post_overlay_total_bound_direct_cell_count": 2457,
        "post_overlay_total_bound_delegated_cell_count": 3, "post_overlay_total_not_applicable_cell_count": 502,
        "post_overlay_total_blocked_cell_count": 1259, "post_overlay_missing_cell_count": 0,
        "post_overlay_conflict_cell_count": 0, "new_operation_count": 0, "subject_evaluation_count": 1,
        "logical_final_commit_count_on_clause_success": 1, "failure_residue_count": 0,
        "source_order_overlap_winner_count": 0, "terminal_no_match_runtime_residue_count": 0,
        "excluded_related_feature_transition_count": 0, "other_target_cell_transition_count": 0,
    }, "MACHINE_ACCEPTANCE_EXACT")
    require(contract.get("authority_fence") == {
        "new_source_surface_count": 0, "new_ast_identity_count": 0, "new_hir_identity_count": 0,
        "new_mir_operation_kind_count": 0, "semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED", "evidence_level": "E2_STRUCTURED_STATIC",
    }, "AUTHORITY_FENCE_EXACT")
    guards = overlay.get("guards", {})
    require(guards.get("transitioned_cell_count") == 5, "GUARDS_TRANSITION_COUNT")
    require(guards.get("excluded_related_feature_transition_count", guards.get("excluded_reverse_dependent_transition_count")) == 0, "GUARDS_EXCLUDED_ZERO")
    require(guards.get("other_cell_transition_count") == 0, "GUARDS_OTHER_ZERO")
    require(guards.get("source_activation") == "none" and guards.get("surface_change_count") == 0, "GUARDS_NO_SURFACE")
    require(guards.get("ast_identity_change_count") == 0 and guards.get("hir_identity_change_count") == 0 and guards.get("mir_operation_kind_change_count") == 0, "GUARDS_NO_IDENTITY_OR_OPERATION")
    require(guards.get("semantic_p0") == 0 and guards.get("feature_p1") == "22_OPEN_UNCHANGED" and guards.get("m13_actions") == "4_OPEN_UNCHANGED", "GUARDS_P0_P1_M13")
    require(guards.get("product_lanes") == "15_OF_15_NOT_RUN" and guards.get("github_publication") == "SUSPENDED", "GUARDS_PRODUCT_GITHUB")
    require(guards.get("product_execution_receipt_count") == 0 and guards.get("implementation_claim") == "NONE", "GUARDS_NO_IMPLEMENTATION_CLAIM")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    overlay = load(root / OVERLAY_REL)
    contract = load(root / CONTRACT_REL)
    errors = validate(root, overlay, contract)
    print(json.dumps({
        "schema": "deeplus.pattern-clause-exhaustiveness-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_count": 2,
        "binding_count": 5,
        "rule_count": len(contract.get("rules", [])),
        "acceptance_case_count": len(contract.get("acceptance_cases", [])),
        "projected_counts": {"bound_direct": 2457, "bound_delegated": 3, "not_applicable": 502, "applicable_blocked": 1259, "missing": 0, "conflict": 0},
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
