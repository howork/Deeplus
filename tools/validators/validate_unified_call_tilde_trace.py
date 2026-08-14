#!/usr/bin/env python3
"""Validate the bounded R57 unified-call, tilde and dependency trace closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/unified-call-tilde-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/unified-call-tilde-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/unified-call-tilde-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "808bf7cd1d28bba737e0744a6f120c71297d7ddd"
FEATURES = sorted([
    "actor_declaration_grammar_closed",
    "actor_protocol_family",
    "data_shaping_callshape_model",
    "unified_call_expression_and_tilde_modes",
])
EXPECTED_OVERLAY_CELLS = {
    ("unified_call_expression_and_tilde_modes", "DYNAMIC_LOWERING", None): ("BOUND_DIRECT", None),
    ("actor_protocol_family", "DYNAMIC_LOWERING", None): ("BOUND_DIRECT", None),
    ("unified_call_expression_and_tilde_modes", "CONFORMANCE_TESTS", "POSITIVE"): ("BOUND_DIRECT", None),
    ("unified_call_expression_and_tilde_modes", "CONFORMANCE_TESTS", "BOUNDARY"): ("BOUND_DIRECT", None),
    ("unified_call_expression_and_tilde_modes", "CONFORMANCE_TESTS", "REJECT"): ("BOUND_DIRECT", None),
    ("data_shaping_callshape_model", "CONFORMANCE_TESTS", "BOUNDARY"): ("BOUND_DIRECT", None),
    ("data_shaping_callshape_model", "CONFORMANCE_TESTS", "REJECT"): ("BOUND_DIRECT", None),
    ("actor_declaration_grammar_closed", "CONFORMANCE_TESTS", "BOUNDARY"): ("BOUND_DIRECT", None),
    ("actor_declaration_grammar_closed", "CONFORMANCE_TESTS", "REJECT"): ("BOUND_DELEGATED", "actor_mailbox_capacity"),
}
EXPECTED_ACCEPTANCE_BINDINGS = {
    ("unified_call_expression_and_tilde_modes", "POSITIVE"): ["UCTC-AC-001", "UCTC-AC-002", "UCTC-AC-003"],
    ("unified_call_expression_and_tilde_modes", "BOUNDARY"): ["UCTC-AC-004", "UCTC-AC-005", "UCTC-AC-006"],
    ("unified_call_expression_and_tilde_modes", "REJECT"): ["UCTC-AC-007", "UCTC-AC-008", "UCTC-AC-009", "UCTC-AC-010", "UCTC-AC-011"],
    ("data_shaping_callshape_model", "BOUNDARY"): ["UCTC-AC-012"],
    ("data_shaping_callshape_model", "REJECT"): ["UCTC-AC-013"],
    ("actor_declaration_grammar_closed", "BOUNDARY"): ["UCTC-AC-014"],
    ("actor_declaration_grammar_closed", "REJECT"): ["UCTC-AC-015"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def contains_scalar(value: Any, expected: str) -> bool:
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(contains_scalar(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(contains_scalar(item, expected) for item in value)
    return False


def trace_cell(row: dict[str, Any], stage_name: str, outcome: str | None) -> dict[str, Any]:
    stage = next(item for item in row["stages"] if item["stage"] == stage_name)
    if outcome is None:
        return stage
    return next(item for item in stage["outcomes"] if item["outcome"] == outcome)


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    validate_schema: bool = True,
    trace_rows_override: list[dict[str, Any]] | None = None,
    hm_row_override: dict[str, Any] | None = None,
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

    require(contract.get("canonical_baseline_commit") == BASELINE, "CONTRACT_BASELINE")
    require(contract.get("local_predecessor_commit") == PREDECESSOR, "CONTRACT_PREDECESSOR")
    require(overlay.get("canonical_baseline_commit") == BASELINE, "OVERLAY_BASELINE")
    require(overlay.get("local_predecessor_commit") == PREDECESSOR, "OVERLAY_PREDECESSOR")
    require(contract.get("feature_ids") == FEATURES, "CONTRACT_FEATURES_EXACT")
    require(overlay.get("feature_ids") == FEATURES, "OVERLAY_FEATURES_EXACT")

    surface = contract.get("surface_and_ast", {})
    require(surface.get("ast_node") == "CallExpr", "CALL_EXPR_EXACT")
    require(surface.get("call_modes") == ["Ordinary", "Message", "ActorMessage"], "CALL_MODES_EXACT")
    require(surface.get("ast_argument_kinds") == ["Positional", "Named", "PositionalUnfold", "NamedUnfold", "Context", "Witness"], "AST_ARGUMENT_KINDS_EXACT")
    require(surface.get("hir_argument_kinds") == ["POSITIONAL", "NAMED", "POSITIONAL_UNFOLD", "NAMED_UNFOLD", "CONTEXT", "WITNESS", "TRAILING_CLOSURE"], "HIR_ARGUMENT_KINDS_EXACT")
    require(surface.get("message_payload_node_count") == 0 and surface.get("tuple_or_record_payload_projection_count") == 0, "NO_PAYLOAD_PROJECTION")
    require(surface.get("trailing_closure_hir_array_count") == 0, "ONE_HIR_ARGUMENT_ARRAY")

    pratt = contract.get("pratt_contract", {})
    require(pratt.get("rank") == 15, "PRATT_RANK_15")
    require(pratt.get("message_associativity") == "LEFT", "MESSAGE_LEFT")
    require(pratt.get("actor_message_associativity") == "TERMINAL_NONASSOCIATIVE", "ACTOR_TERMINAL")
    require(pratt.get("outer_comma_requires_grouping") is True, "COMMA_GROUPING")

    static = contract.get("static_semantics", {})
    require(static.get("predicate_id") == "UnifiedCallModeAdmitted", "STATIC_PREDICATE")
    require(static.get("actor_to_ordinary_fallback_count") == 0, "NO_ACTOR_FALLBACK")
    require(static.get("runtime_selector_lookup_count") == 0, "NO_RUNTIME_LOOKUP")
    require(static.get("context_or_witness_synthesis_count") == 0, "NO_IMPLICIT_CONTEXT_WITNESS")
    require(len(static.get("phase_order", [])) == 8, "STATIC_PHASE_COUNT_8")

    evaluation = contract.get("evaluation_and_failure", {})
    require(len(evaluation.get("evaluation_order", [])) == 6, "EVALUATION_ORDER_COUNT_6")
    failure = evaluation.get("preparation_failure", {})
    require(failure.get("callee_invocation_count") == 0, "PREP_NO_INVOKE")
    require(failure.get("actor_envelope_publish_count") == 0, "PREP_NO_PUBLISH")
    require(failure.get("uncommitted_owner_retained") is True, "PREP_OWNER_RETAINED")
    require(evaluation.get("borrow_or_inout_cross_actor_isolation") is False, "NO_BORROW_ACTOR_CROSSING")

    lowering = contract.get("hir_lowering", {})
    require(lowering.get("call_expr_identity") == "HIR-H1/EXPR/CALL", "HIR_CALL_ID")
    require(lowering.get("call_plan_schema_identity") == "CallPlan", "CALL_PLAN_SCHEMA_ID")
    require(len(lowering.get("valid_mode_target_pairs", [])) == 10 and len(set(lowering.get("valid_mode_target_pairs", []))) == 10, "MODE_TARGET_EXACT_10")
    require(lowering.get("lowering_rows") == [f"HM-LR-CALL-{index:03d}" for index in range(1, 11)], "LOWERING_ROWS_EXACT_10")
    require(lowering.get("new_call_input_commit_operation_count") == 0, "NO_CALL_INPUT_COMMIT")

    actor = contract.get("actor_transport", {})
    require(actor.get("admission") == "IMMEDIATE_NONBLOCKING", "ACTOR_IMMEDIATE")
    require(actor.get("implicit_suspend_count") == 0 and actor.get("implicit_retry_count") == 0, "ACTOR_NO_SUSPEND_RETRY")
    require(actor.get("lowering_row_successor_roles") == ["NORMAL", "ERROR", "DEFECT", "CANCELLATION"], "ACTOR_ROW_SUCCESSORS")
    require(actor.get("lowering_row_suspension_effect") == "NONE", "ACTOR_ROW_NO_SUSPEND")
    require(actor.get("lowering_row_reply_token_count") == 0 and actor.get("one_way_reply_identity_count") == 0, "ACTOR_NO_UNCONDITIONAL_REPLY")
    require(actor.get("successful_envelope_publish_count") == 1 and actor.get("successful_moved_owner_transfer_count_each") == 1, "ACTOR_ONE_COMMIT")
    require(actor.get("transport_error_set") == ["AllocationError"] and actor.get("transport_effect_row") == ["allocate"], "ACTOR_ALLOCATION_RESPONSIBILITY")
    require(actor.get("postcommit_allocation_count") == 0, "ACTOR_NO_POSTCOMMIT_ALLOCATION")

    rules = contract.get("rules", [])
    require([item.get("rule_id") for item in rules] == [f"UCTC-R{index:03d}" for index in range(1, 18)], "RULE_IDS_EXACT_17")
    cases = contract.get("acceptance_cases", [])
    case_by_id = {item.get("case_id"): item for item in cases}
    require(len(cases) == 15 and len(case_by_id) == 15, "ACCEPTANCE_EXACT_UNIQUE_15")
    require(sum(item.get("class") == "POSITIVE" for item in cases) == 3, "ACCEPTANCE_POSITIVE_3")
    require(sum(item.get("class") == "BOUNDARY" for item in cases) == 5, "ACCEPTANCE_BOUNDARY_5")
    require(sum(item.get("class") == "REJECT" for item in cases) == 7, "ACCEPTANCE_REJECT_7")
    require(all(item.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for item in cases), "ACCEPTANCE_NOT_RUN")
    bindings_doc = contract.get("acceptance_bindings", {})
    for (feature, outcome), expected_ids in EXPECTED_ACCEPTANCE_BINDINGS.items():
        observed_ids = bindings_doc.get(feature, {}).get(outcome)
        require(observed_ids == expected_ids, f"ACCEPTANCE_BINDING:{feature}:{outcome}")
        require(all(case_by_id.get(case_id, {}).get("feature_id") == feature and case_by_id.get(case_id, {}).get("class") == outcome for case_id in expected_ids), f"ACCEPTANCE_BINDING_CLASS:{feature}:{outcome}")

    entries = overlay.get("evidence_entries", [])
    by_key = {item.get("evidence_key"): item for item in entries}
    require(len(entries) == 9 and len(by_key) == 9, "EVIDENCE_EXACT_UNIQUE_9")
    for key, item in by_key.items():
        require(isinstance(key, str) and key.startswith("R57:"), f"EVIDENCE_KEY:{key}")
        require(item.get("path") == CONTRACT_REL, f"EVIDENCE_PATH:{key}")
        locator = item.get("locator", "")
        if item.get("locator_kind") == "JSON_POINTER":
            try:
                resolve_pointer(contract, locator)
            except (KeyError, IndexError, TypeError, ValueError):
                require(False, f"EVIDENCE_POINTER:{key}")
        else:
            require(contains_scalar(contract, locator), f"EVIDENCE_REGISTRY_ID:{key}")

    overlay_bindings = overlay.get("bindings", [])
    by_cell = {(item.get("feature_id"), item.get("stage"), item.get("outcome")): item for item in overlay_bindings}
    require(len(overlay_bindings) == 9 and len(by_cell) == 9, "OVERLAY_BINDING_EXACT_UNIQUE_9")
    require(set(by_cell) == set(EXPECTED_OVERLAY_CELLS), "OVERLAY_CELLS_EXACT")
    for cell, (disposition, delegate) in EXPECTED_OVERLAY_CELLS.items():
        item = by_cell.get(cell, {})
        require(item.get("disposition") == disposition, f"OVERLAY_DISPOSITION:{cell}")
        require(item.get("delegate_feature_id") == delegate, f"OVERLAY_DELEGATE:{cell}")
        refs = item.get("evidence_keys", [])
        require(len(refs) == 1 and refs[0] in by_key, f"OVERLAY_ONE_EVIDENCE:{cell}")

    trace_rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    trace_by_id = {item["feature_id"]: item for item in trace_rows}
    require(len(trace_rows) == 469 and len(trace_by_id) == 469, "TRACE_FEATURE_COUNT_469")
    static_cell = trace_cell(trace_by_id["unified_call_expression_and_tilde_modes"], "STATIC_SEMANTICS", None)
    require(static_cell.get("disposition") == "BOUND_DIRECT" and not static_cell.get("blocked_gap_ids"), "CATALOG_DIRECT_STATIC_TRANSITION")
    for cell, (disposition, delegate) in EXPECTED_OVERLAY_CELLS.items():
        observed = trace_cell(trace_by_id[cell[0]], cell[1], cell[2])
        require(observed.get("disposition") == disposition, f"TRACE_DISPOSITION:{cell}")
        require(observed.get("delegate_feature_id") == delegate, f"TRACE_DELEGATE:{cell}")
        require(not observed.get("blocked_gap_ids"), f"TRACE_STILL_BLOCKED:{cell}")
    mailbox_reject = trace_cell(trace_by_id["actor_mailbox_capacity"], "CONFORMANCE_TESTS", "REJECT")
    require(mailbox_reject.get("disposition") == "BOUND_DIRECT", "MAILBOX_DELEGATE_TARGET_BOUND")

    feature_rows = {row["feature_id"]: row for row in all_rows(root, "spec/features/catalog/chunks")}
    unified_feature = feature_rows["unified_call_expression_and_tilde_modes"]
    require(unified_feature.get("depends_on") == ["data_shaping_callshape_model", "actor_protocol_family"], "UNIFIED_CATALOG_DEPENDENCIES")
    require(unified_feature.get("normative_trace_refs", {}).get("predicates") == ["UnifiedCallModeAdmitted"], "UNIFIED_PREDICATE_BOUND")
    require(feature_rows["actor_protocol_family"].get("depends_on") == ["actor_declaration_grammar_closed"], "ACTOR_TRANSITIVE_DEPENDENCY")
    dependency_rows = all_rows(root, "spec/features/dependencies/chunks")
    dependency_edges = {(row["source_feature_id"], row["target_feature_id"]) for row in dependency_rows}
    require(("unified_call_expression_and_tilde_modes", "data_shaping_callshape_model") in dependency_edges, "DEPENDENCY_EDGE_CALLSHAPE")
    require(("unified_call_expression_and_tilde_modes", "actor_protocol_family") in dependency_edges, "DEPENDENCY_EDGE_ACTOR")
    require(("actor_protocol_family", "actor_declaration_grammar_closed") in dependency_edges, "DEPENDENCY_EDGE_ACTOR_DECL")

    predicates = {row["predicate_id"]: row for row in all_rows(root, "spec/types/predicates/chunks")}
    predicate = predicates.get("UnifiedCallModeAdmitted", {})
    require(predicate.get("predicate_maturity") == "design_algorithm", "PREDICATE_ALGORITHM")
    require(predicate.get("emission_eligible") is True, "PREDICATE_EMISSION")
    require(predicate.get("product_support") == "NOT_RUN" and predicate.get("execution_receipt") is None, "PREDICATE_NOT_RUN")
    require(predicate.get("active_primary_diagnostic") == "TILDE_CALL_COMMA_REQUIRES_GROUPING", "PREDICATE_PRIMARY")
    require(predicate.get("secondary_diagnostics") == ["TILDE_CALL_TERMINAL_CHAIN_FORBIDDEN", "ACTOR_TILDE_CALL_REQUIRES_COLON_TILDE", "ACTOR_OPERATION_KIND_COLLISION"], "PREDICATE_SECONDARY")

    fixture_rows = [row for row in all_rows(root, "tests/conformance/checker-predicates/chunks") if row.get("predicate_id") == "UnifiedCallModeAdmitted"]
    require(len(fixture_rows) == 6 and len({row["fixture_id"] for row in fixture_rows}) == 6, "PREDICATE_FIXTURES_6")
    require(sum(row.get("expected") == "admitted" for row in fixture_rows) == 2, "PREDICATE_FIXTURES_POS_2")
    require(sum(row.get("expected") == "rejected" for row in fixture_rows) == 4, "PREDICATE_FIXTURES_NEG_4")
    require(all(row.get("execution_status") == "DESIGN_STATIC_NOT_RUN" for row in fixture_rows), "PREDICATE_FIXTURES_NOT_RUN")

    relations = [row for row in all_rows(root, "spec/diagnostics/relations/chunks") if row.get("predicate_id") == "UnifiedCallModeAdmitted"]
    require(len(relations) == 4, "DIAGNOSTIC_RELATIONS_4")
    require(sum(row.get("relation") == "primary" for row in relations) == 1, "DIAGNOSTIC_PRIMARY_1")
    require({row.get("diagnostic_id") for row in relations} == set(contract.get("diagnostic_priority", [])), "DIAGNOSTIC_RELATION_IDS")

    lowering_registry = load(root / "spec/contracts/hir-mir-lowering-registry.json")
    hm_row = hm_row_override or next(row for row in lowering_registry["rows"] if row["row_id"] == "HM-LR-CALL-010")
    require(hm_row.get("successor_roles") == ["NORMAL", "ERROR", "DEFECT", "CANCELLATION"], "HM010_SUCCESSORS")
    require(hm_row.get("terminator_plan", [{}])[0].get("successor_roles") == ["NORMAL", "ERROR", "DEFECT", "CANCELLATION"], "HM010_TERMINATOR_SUCCESSORS")
    require(hm_row.get("outcome_families") == ["NORMAL", "DEFECT", "CANCELLATION"], "HM010_OUTCOMES")
    require(hm_row.get("suspension_effect") == "NONE", "HM010_NO_SUSPEND")
    require(hm_row.get("token_outputs") == [{"token_kind": "AUTHORITY", "token_role": "actor_transport_authority", "cardinality": 1}], "HM010_TOKEN_OUTPUTS")
    require(hm_row.get("token_discharges") == [], "HM010_NO_REPLY_DISCHARGE")

    reference = (root / "docs/grammar-reference/05-functions-methods-closures-and-calls.md").read_text(encoding="utf-8")
    require("0/1 aggregate" not in reference, "REFERENCE_STALE_PAYLOAD_REMOVED")
    require("message 전용 payload aggregate를\n  만들지 않는다" in reference, "REFERENCE_NO_PAYLOAD_RULE")

    machine = contract.get("machine_acceptance", {})
    require(machine.get("predecessor_blocked_cell_count") == 10, "MACHINE_PREDECESSOR_10")
    require(machine.get("catalog_direct_transition_count") == 1, "MACHINE_CATALOG_DIRECT_1")
    require(machine.get("overlay_bound_direct_transition_count") == 8, "MACHINE_OVERLAY_DIRECT_8")
    require(machine.get("overlay_bound_delegated_transition_count") == 1, "MACHINE_OVERLAY_DELEGATED_1")
    require(machine.get("post_overlay_total_blocked_cell_count") == 1281, "MACHINE_POST_BLOCKED_1281")
    fences = contract.get("authority_fence", {})
    require(fences.get("semantic_p0") == 0 and fences.get("feature_p1") == "22_OPEN_UNCHANGED", "FENCE_P0_P1")
    require(fences.get("m13_actions") == "4_OPEN_UNCHANGED", "FENCE_M13")
    require(fences.get("product_lanes") == "15_OF_15_NOT_RUN", "FENCE_PRODUCT_NOT_RUN")
    require(fences.get("github_publication") == "SUSPENDED", "FENCE_GITHUB_SUSPENDED")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    overlay = load(root / OVERLAY_REL)
    contract = load(root / CONTRACT_REL)
    errors = validate(root, overlay, contract)
    if errors:
        print(f"R57_UNIFIED_CALL_TILDE_TRACE: FAIL ({len(errors)})")
        for error in errors:
            print(f"- {error}")
        return 1
    print("R57_UNIFIED_CALL_TILDE_TRACE: PASS")
    print("features=4 predecessor_blocked=10 catalog_direct=1 overlay_direct=8 overlay_delegated=1 post_blocked=1281")
    print("semantic_p0=0 feature_p1=22_OPEN m13=4_OPEN product_lanes=15/15_NOT_RUN github=SUSPENDED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
