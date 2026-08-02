#!/usr/bin/env python3
"""Static validator for the R32 deterministic deferred-call-plan candidate.

The validator checks design artifacts and deterministic projections only.  It
does not execute a Deeplus parser, checker, MIR lowerer, runtime, backend, or
tool and therefore cannot establish product support.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_TERMINAL_PATHS = {
    "FALLTHROUGH",
    "RETURN",
    "EXITING_BREAK",
    "EXITING_CONTINUE",
    "ERROR",
    "DEFECT",
    "CANCELLATION",
}
EXPECTED_MIR_OPERATIONS = {
    "MOVE_RESERVE",
    "MOVE_CANCEL",
    "PLACE_MOVE",
    "LOAN_BEGIN_SHARED",
    "LOAN_BEGIN_EXCLUSIVE",
    "LOAN_END",
    "CLEANUP_REGISTER",
    "CLEANUP_PIN",
    "CLEANUP_SEAL",
    "CLEANUP_DISARM",
}
EXPECTED_DIAGNOSTICS = {
    "DEFER_REQUIRES_SINGLE_INVOCATION",
    "DEFER_BLOCK_REMOVED_USE_SINGLE_CLEANUP_CALL",
    "DEFER_CLEANUP_RESERVED_PLACE_MOVED",
    "ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER",
}
EXPECTED_CASE_COUNTS = {
    "positive": 8,
    "boundary": 6,
    "negative": 8,
    "mutation": 12,
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def rows_from_chunks(root: Path, rel: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / rel).glob("part-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, dict))
            continue
        candidates = [item for item in value.values() if isinstance(item, list)]
        if len(candidates) != 1:
            raise ValueError(f"cannot identify row array in {path}")
        rows.extend(row for row in candidates[0] if isinstance(row, dict))
    return rows


def local_refs_closed(schema: dict[str, Any]) -> bool:
    defs = schema.get("$defs", {})
    refs: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            ref = value.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                refs.append(ref.removeprefix("#/$defs/"))
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(schema)
    return all(ref in defs for ref in refs)


def typed_input_shape_errors(value: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    if value.get("schema") != "deeplus.deferred-call-plan-input/r1":
        errors.add("SCHEMA")
    if value.get("predicate_id") != "SingleActionDeferAdmitted":
        errors.add("PREDICATE")
    if value.get("product_support") != "NOT_RUN":
        errors.add("PRODUCT_SUPPORT")
    variant = value.get("variant")
    if variant == "SOURCE_REJECTION":
        allowed = {
            "schema",
            "predicate_id",
            "variant",
            "surface",
            "expected_parser_diagnostic",
            "product_support",
        }
        if set(value) != allowed:
            errors.add("PHASE_UNION")
        if value.get("expected_parser_diagnostic") not in EXPECTED_DIAGNOSTICS:
            errors.add("DIAGNOSTIC")
        return errors
    if variant != "TYPED_PLAN":
        errors.add("PHASE_UNION")
        return errors
    required = {
        "plan_id",
        "cleanup_scope_id",
        "registration_site_id",
        "source_registration_ordinal",
        "surface",
        "selected_call",
        "dynamic_operands_in_evaluation_order",
        "static_evidence_bindings",
        "registration_transaction",
        "execution_policy",
        "scope_profile",
        "post_registration_place_actions",
    }
    if not required.issubset(value):
        errors.add("TYPED_PLAN_FIELDS")
        return errors
    surface = value["surface"]
    if surface.get("form") not in {"DIRECT_CALL", "MESSAGE_CALL"}:
        errors.add("SURFACE")
    if surface.get("invocation_count") != 1:
        errors.add("SURFACE")
    forbidden_flags = {
        "contains_block",
        "contains_inline_callable",
        "contains_trailing_closure",
        "contains_guard",
        "contains_await",
        "contains_spawn",
        "contains_actor_transport",
    }
    if any(surface.get(flag) is not False for flag in forbidden_flags):
        errors.add("SURFACE")
    call = value["selected_call"]
    if str(call.get("mode_target_pair", "")).startswith("ACTOR_MESSAGE::"):
        errors.add("ACTOR_TRANSPORT")
    if call.get("exit_time_selection_count") != 0:
        errors.add("EXIT_SELECTION")
    if call.get("execution_suspension") != "NONE":
        errors.add("CLEANUP_SUSPENDS")
    if call.get("result_disposition") not in {
        "UNIT_NO_VALUE",
        "DISCARD_CLEANUP_FREE_VALUE",
        "CLEAN_OWNED_TEMPORARY",
    }:
        errors.add("RESULT_DISPOSITION")
    if (
        call.get("result_disposition") == "CLEAN_OWNED_TEMPORARY"
        and call.get("result_cleanup_obligation_id_or_null") is None
    ):
        errors.add("RESULT_CLEANUP")

    operands = value["dynamic_operands_in_evaluation_order"]
    ordinals = [operand.get("evaluation_ordinal") for operand in operands]
    if ordinals != list(range(len(operands))):
        errors.add("OPERAND_ORDINAL")
    if any(operand.get("evaluation_count") != 1 for operand in operands):
        errors.add("EVALUATION_COUNT")
    if any(operand.get("role") == "STATIC_EVIDENCE" for operand in operands):
        errors.add("STATIC_EVIDENCE_IN_DYNAMIC_ORDER")
    roles = [operand.get("role") for operand in operands]
    if not roles or roles[0] != "CALLEE_OR_RECEIVER":
        errors.add("RECEIVER_FIRST")
    default_seen = False
    for operand in operands[1:]:
        if operand.get("role") == "DEFAULT_ARGUMENT":
            default_seen = True
        elif default_seen:
            errors.add("DEFAULT_ORDER")
    if any(
        not binding.get("formal_binding_id")
        or not binding.get("evidence_id")
        for binding in value["static_evidence_bindings"]
    ):
        errors.add("STATIC_EVIDENCE_BINDING")

    transaction = value["registration_transaction"]
    if transaction.get("evaluation_order_ordinals") != ordinals:
        errors.add("OPERAND_ORDER")
    if transaction.get("rollback_order_ordinals") != list(reversed(ordinals)):
        errors.add("ROLLBACK_ORDER")
    if transaction.get("partial_publication_count") != 0:
        errors.add("PARTIAL_PUBLICATION")
    if transaction.get("sealed_state") != "SEALED_IMMUTABLE":
        errors.add("PLAN_SEAL")
    if transaction.get("external_effects_undone") is not False:
        errors.add("EXTERNAL_EFFECT_ROLLBACK")
    if transaction.get("commit_sequence") != [
        "CLEANUP_REGISTER",
        "CLEANUP_PIN",
        "CLEANUP_SEAL",
    ]:
        errors.add("COMMIT_SEQUENCE")

    policy = value["execution_policy"]
    if policy.get("scope_execution_order") != "LIFO":
        errors.add("LIFO_ORDER")
    if policy.get("execution_count") != 1 or policy.get("retry_count") != 0:
        errors.add("EXECUTION_COUNT")
    if policy.get("exit_time_operand_evaluation_count") != 0:
        errors.add("EXIT_TIME_EVALUATION")
    if policy.get("suspension_disposition") != "PRESERVE_REGISTERED_PLAN_NO_EXECUTION":
        errors.add("SUSPENSION_PRESERVATION")
    if set(policy.get("terminal_paths", [])) != EXPECTED_TERMINAL_PATHS:
        errors.add("TERMINAL_PATHS")

    pinned_places = {
        acquisition.get("source_place_id_or_null")
        for acquisition in (operand.get("acquisition", {}) for operand in operands)
        if acquisition.get("kind")
        in {"SHARED_LOAN", "EXCLUSIVE_LOAN", "PINNED_PLACE_RESERVATION"}
    }
    forbidden_actions = {"MOVE", "REBIND", "REPLACE_OWNER"}
    if any(
        action.get("place_id") in pinned_places
        and action.get("action") in forbidden_actions
        for action in value["post_registration_place_actions"]
    ):
        errors.add("PINNED_PLACE_ACTION")
    return errors


def decide_input(value: dict[str, Any]) -> tuple[str, str | None]:
    errors = typed_input_shape_errors(value)
    if value.get("variant") == "SOURCE_REJECTION":
        return "REJECT", value.get("expected_parser_diagnostic")
    if "PINNED_PLACE_ACTION" in errors:
        return "REJECT", "DEFER_CLEANUP_RESERVED_PLACE_MOVED"
    if errors:
        return "REJECT", None
    return "ADMIT", None


def base_projection() -> dict[str, Any]:
    return {
        "plan_id": "dcp:0",
        "bound_registration_id": "cleanup-registration:0",
        "operand_ordinals": [0, 1, 2],
        "evaluation_order": [0, 1, 2],
        "evaluation_counts": [1, 1, 1],
        "exit_time_evaluation_count": 0,
        "rollback_order": [2, 1, 0],
        "partial_publication_count": 0,
        "sealed_state": "SEALED_IMMUTABLE",
        "execution_count": 1,
        "retry_count": 0,
        "scope_order": "LIFO",
        "identity_at_execution": "dcp:0",
        "suspension_disposition": "PRESERVE_REGISTERED_PLAN_NO_EXECUTION",
        "product_support": "NOT_RUN",
    }


def projection_errors(model: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    ordinals = model["operand_ordinals"]
    if ordinals != list(range(len(ordinals))):
        errors.add("OPERAND_ORDINAL")
    if model["evaluation_order"] != ordinals:
        errors.add("OPERAND_ORDER")
    if any(count != 1 for count in model["evaluation_counts"]):
        errors.add("EVALUATION_COUNT")
    if model["exit_time_evaluation_count"] != 0:
        errors.add("EXIT_TIME_EVALUATION")
    if model["rollback_order"] != list(reversed(ordinals)):
        errors.add("ROLLBACK_ORDER")
    if model["partial_publication_count"] != 0:
        errors.add("PARTIAL_PUBLICATION")
    if model["sealed_state"] != "SEALED_IMMUTABLE":
        errors.add("PLAN_SEAL")
    if model["execution_count"] != 1 or model["retry_count"] != 0:
        errors.add("EXECUTION_COUNT")
    if model["scope_order"] != "LIFO":
        errors.add("LIFO_ORDER")
    if model["identity_at_execution"] != model["plan_id"]:
        errors.add("PLAN_IDENTITY")
    if model["suspension_disposition"] != "PRESERVE_REGISTERED_PLAN_NO_EXECUTION":
        errors.add("SUSPENSION_PRESERVATION")
    if model["product_support"] != "NOT_RUN":
        errors.add("PRODUCT_SUPPORT")
    return errors


Mutator = Callable[[dict[str, Any]], None]


def mutations() -> dict[str, tuple[str, Mutator]]:
    return {
        "REORDER_OPERANDS": (
            "OPERAND_ORDER",
            lambda m: m.__setitem__("evaluation_order", [1, 0, 2]),
        ),
        "DELAY_TO_EXIT": (
            "EXIT_TIME_EVALUATION",
            lambda m: m.__setitem__("exit_time_evaluation_count", 1),
        ),
        "EVALUATE_TWICE": (
            "EVALUATION_COUNT",
            lambda m: m.__setitem__("evaluation_counts", [1, 2, 1]),
        ),
        "ORDINAL_GAP": (
            "OPERAND_ORDINAL",
            lambda m: m.__setitem__("operand_ordinals", [0, 1, 3]),
        ),
        "PARTIAL_PUBLICATION": (
            "PARTIAL_PUBLICATION",
            lambda m: m.__setitem__("partial_publication_count", 1),
        ),
        "FORWARD_ROLLBACK": (
            "ROLLBACK_ORDER",
            lambda m: m.__setitem__("rollback_order", [0, 1, 2]),
        ),
        "MUTABLE_PLAN": (
            "PLAN_SEAL",
            lambda m: m.__setitem__("sealed_state", "MUTABLE"),
        ),
        "EXECUTE_TWICE_OR_RETRY": (
            "EXECUTION_COUNT",
            lambda m: m.__setitem__("execution_count", 2),
        ),
        "FIFO_DRAIN": (
            "LIFO_ORDER",
            lambda m: m.__setitem__("scope_order", "FIFO"),
        ),
        "IDENTITY_SUBSTITUTION": (
            "PLAN_IDENTITY",
            lambda m: m.__setitem__("identity_at_execution", "dcp:other"),
        ),
        "SUSPENSION_DRAINS": (
            "SUSPENSION_PRESERVATION",
            lambda m: m.__setitem__("suspension_disposition", "RUN_LIFO"),
        ),
        "PRODUCT_LANE_FLIP": (
            "PRODUCT_SUPPORT",
            lambda m: m.__setitem__("product_support", "PASS"),
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[dict[str, Any]] = []

    def emit(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})

    schema = load_json(root, "schemas/language/deferred-call-plan-input-r1.schema.json")
    contract = load_json(root, "spec/contracts/deferred-call-plan-r1.json")
    fixtures = load_json(root, "tests/fixtures/current/deferred-call-plan-r1.json")

    union_refs = {entry.get("$ref") for entry in schema.get("oneOf", [])}
    typed_results = []
    for row in fixtures.get("typed_inputs", []):
        decision = decide_input(row["input"])
        typed_results.append(
            {
                "case_id": row["case_id"],
                "shape_errors": sorted(typed_input_shape_errors(row["input"])),
                "decision": decision,
                "expected": (row["expected_outcome"], row["expected_diagnostic_or_null"]),
            }
        )
    emit(
        "DCP-V01_SCHEMA_PHASE_UNION_CLOSED",
        local_refs_closed(schema)
        and union_refs
        == {"#/$defs/sourceRejectionInput", "#/$defs/typedPlanInput"}
        and all(not result["shape_errors"] for result in typed_results),
        typed_results,
    )

    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    productions = [
        line.split("::=", 1)[0].strip()
        for line in grammar.splitlines()
        if "::=" in line and not line.lstrip().startswith("(*")
    ]
    grammar_count_authority = load_json(
        root, "spec/contracts/manual-grammar-count-authority-r1.json"
    )["authority"]["production_count"]
    emit(
        "DCP-V02_SURFACE_GRAMMAR_UNCHANGED",
        len(productions) == grammar_count_authority
        and 'DeferStmt ::= "defer" DeferredCleanupInvocation StatementBoundary ;' in grammar
        and "DeferredCleanupInvocation ::= DeferredDirectCall | DeferredMessageCall ;" in grammar
        and ":~" not in grammar.split("DeferredCleanupInvocation ::=", 1)[1].split("RightwardLocalBindingSurface", 1)[0],
        {
            "production_count": len(productions),
            "authoritative_production_count": grammar_count_authority,
            "grammar_change_count": contract["scope_fence"]["grammar_change_count"],
        },
    )

    admitted_pairs = {
        "ORDINARY::DIRECT_IMPLEMENTATION",
        "ORDINARY::VIRTUAL_SLOT",
        "ORDINARY::TRAIT_WITNESS",
        "ORDINARY::EXTENSION_STATIC",
        "MESSAGE::DIRECT_IMPLEMENTATION",
        "MESSAGE::VIRTUAL_SLOT",
        "MESSAGE::TRAIT_WITNESS",
        "MESSAGE::EXTENSION_STATIC",
        "MESSAGE::RESERVED_OPERATION",
    }
    positive_input = next(row["input"] for row in fixtures["typed_inputs"] if row["case_id"] == "R32-DCP-IN-POS-001")
    call = positive_input["selected_call"]
    emit(
        "DCP-V03_CALL_SELECTION_CLOSED",
        call["mode_target_pair"] in admitted_pairs
        and call["exit_time_selection_count"] == 0
        and contract["call_selection"]["exit_time_overload_or_extension_or_witness_selection_count"] == 0,
        call,
    )

    operands = positive_input["dynamic_operands_in_evaluation_order"]
    roles = [operand["role"] for operand in operands]
    emit(
        "DCP-V04_ARGUMENT_CHANNELS_AND_ORDER",
        roles == ["CALLEE_OR_RECEIVER", "EXPLICIT_ARGUMENT", "DEFAULT_ARGUMENT"]
        and operands[1]["argument_kind_or_null"] == "CONTEXT"
        and all(operand["evaluation_count"] == 1 for operand in operands)
        and all(binding["evidence_id"] for binding in positive_input["static_evidence_bindings"])
        and contract["registration_algorithm"]["dynamic_order"]
        == [
            "callee_or_receiver",
            "explicit_runtime_call_arguments_in_source_order_including_context",
            "selected_defaults_under_normal_call_order",
            "static_evidence_identity_bindings_with_zero_evaluation",
            "ownership_and_cleanup_preparation",
        ]
        and contract["registration_algorithm"]["static_evidence_evaluation_count"] == 0,
        {"roles": roles, "static_evidence_count": len(positive_input["static_evidence_bindings"])},
    )

    defaults = call["default_value_refs"]
    emit(
        "DCP-V05_DEFAULT_BINDING_DIGEST",
        len(defaults) == 1
        and len(defaults[0]["body_semantic_digest"]) == 64
        and operands[-1]["default_value_ref_id_or_null"] == defaults[0]["default_value_ref_id"],
        defaults,
    )

    modes = {operand["acquisition"]["kind"] for operand in operands}
    emit(
        "DCP-V06_ACQUISITION_IDENTITY_NO_HIDDEN_CLONE",
        "SHARED_LOAN" in modes
        and "SNAPSHOT_VALUE" in modes
        and "OWNED_TEMPORARY" in modes
        and "CLONE" not in json.dumps(contract["acquisition_modes"], sort_keys=True)
        and contract["acquisition_modes"]["MOVE_INTO_PLAN"].startswith("reserve during preparation"),
        sorted(modes),
    )

    transaction = positive_input["registration_transaction"]
    emit(
        "DCP-V07_REGISTRATION_FAILURE_ATOMIC",
        transaction["rollback_order_ordinals"] == list(reversed(transaction["evaluation_order_ordinals"]))
        and transaction["partial_publication_count"] == 0
        and transaction["external_effects_undone"] is False
        and transaction["commit_sequence"] == ["CLEANUP_REGISTER", "CLEANUP_PIN", "CLEANUP_SEAL"],
        transaction,
    )

    pinned_probe = copy.deepcopy(positive_input)
    pinned_probe["post_registration_place_actions"] = [{"place_id": "place:file", "action": "REBIND"}]
    emit(
        "DCP-V08_PINNED_PLACE_REBIND_REJECTED",
        decide_input(pinned_probe) == ("REJECT", "DEFER_CLEANUP_RESERVED_PLACE_MOVED"),
        decide_input(pinned_probe),
    )

    policy = positive_input["execution_policy"]
    lowering = load_json(root, "spec/contracts/hir-mir-lowering-registry.json")
    lowering_rows = {row["row_id"]: row for row in lowering["rows"]}
    emit(
        "DCP-V09_LIFO_TERMINAL_AND_SUSPENSION",
        policy["scope_execution_order"] == "LIFO"
        and set(policy["terminal_paths"]) == EXPECTED_TERMINAL_PATHS
        and policy["suspension_disposition"] == "PRESERVE_REGISTERED_PLAN_NO_EXECUTION"
        and lowering["deferred_call_plan_projection_contract"]["suspension"]
        == "PRESERVE_ACTIVE_PLAN_NO_EXECUTION"
        and lowering_rows["HM-LR-TOP-022"]["cleanup_effect"] == "NONE"
        and lowering_rows["HM-LR-TOP-023"]["cleanup_effect"] == "NONE"
        and lowering_rows["HM-LR-TOP-021"]["successor_roles"]
        == ["NORMAL", "ERROR", "DEFECT", "CANCELLATION"]
        and contract["machine_projection"]["terminator_successor_roles"]
        == ["SUCCESS", "ERROR", "DEFECT", "CANCEL"],
        policy,
    )

    emit(
        "DCP-V10_FAILURE_AND_RESULT_DISPOSITION",
        policy["body_failure_precedence"] == "BODY_FAILURE_REMAINS_PRIMARY"
        and policy["normal_body_first_cleanup_failure"] == "BECOMES_PRIMARY"
        and policy["later_cleanup_failure_order"] == "SUPPRESSED_IN_ACTUAL_LIFO_ORDER"
        and set(contract["surface"]["result_dispositions"])
        == {"UNIT_NO_VALUE", "DISCARD_CLEANUP_FREE_VALUE", "CLEAN_OWNED_TEMPORARY"}
        and contract["surface"]["untyped_result_drop_count"] == 0,
        contract["surface"],
    )

    diagnostics = rows_from_chunks(root, "spec/diagnostics/catalog/chunks")
    relations = rows_from_chunks(root, "spec/diagnostics/relations/chunks")
    no_go = rows_from_chunks(root, "spec/compatibility/no-go/chunks")
    diagnostic_by_id = {row.get("diagnostic_id"): row for row in diagnostics}
    defer_relations = [row for row in relations if row.get("predicate_id") == "SingleActionDeferAdmitted"]
    actor_no_go = next((row for row in no_go if row.get("rejection_id") == "NG-DEFER-ACTOR-TRANSPORT"), None)
    block_no_go = next((row for row in no_go if row.get("rejection_id") == "NG-DEFER-BLOCK"), None)
    emit(
        "DCP-V11_DIAGNOSTIC_REACHABILITY_AND_PRIORITY",
        EXPECTED_DIAGNOSTICS.issubset(diagnostic_by_id)
        and diagnostic_by_id["ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER"].get("stage") == "parser"
        and actor_no_go is not None
        and actor_no_go.get("current_ast_created") is False
        and block_no_go is not None
        and block_no_go.get("recognition_stage") == "parser"
        and block_no_go.get("current_ast_created") is False
        and any(row.get("diagnostic_id") == "ACTOR_TRANSPORT_FORBIDDEN_IN_DEFER" for row in defer_relations),
        {"relations": len(defer_relations), "actor_no_go": actor_no_go, "block_no_go": block_no_go},
    )

    hir_schema = load_json(root, "schemas/language/canonical-hir-h1.schema.json")
    mir_schema = load_json(root, "schemas/language/deeplus-mir.schema.json")
    mir_registry = load_json(root, "spec/contracts/mir-machine-registry.json")
    hir_text = json.dumps(hir_schema, sort_keys=True)
    mir_text = json.dumps(mir_schema, sort_keys=True)
    registry_text = json.dumps(mir_registry, sort_keys=True)
    op_universe = set(mir_schema.get("$defs", {}).get("operationKind", {}).get("enum", []))
    api_schema = load_json(root, "schemas/language/module-api-digest.schema.json")
    api_fence = api_schema["x-deeplus-deferred-call-plan-api-fence"]
    emit(
        "DCP-V12_HIR_MIR_API_BINDING",
        "DeferredCallPlan" in hir_text
        and "deferred_call_registration_table" in mir_text
        and EXPECTED_MIR_OPERATIONS.issubset(op_universe)
        and contract["machine_projection"]["new_mir_operation_kind_count"] == 0
        and contract["machine_projection"]["cleanup_register_payload_expansion_count"] == 0
        and "cleanup_registration_id" in registry_text
        and api_fence["deferred_call_plan_is_body_local"] is True
        and api_fence["cleanup_registration_is_body_local"] is True
        and api_fence["value_level_deferred_plan_identity_export_count"] == 0
        and api_fence["value_level_registration_operand_eval_place_owner_loan_reservation_export_count"] == 0
        and api_fence["public_signature_error_effect_residue_preserved"] is True,
        {"operation_count": len(op_universe), "required_subset": sorted(EXPECTED_MIR_OPERATIONS)},
    )

    case_counts = Counter(row["class"] for row in fixtures["cases"])
    case_counts["mutation"] = len(fixtures["mutations"])
    mutation_results = []
    for mutation_id, (expected_error, mutator) in mutations().items():
        model = base_projection()
        mutator(model)
        observed = projection_errors(model)
        mutation_results.append(
            {"mutation": mutation_id, "expected": expected_error, "observed": sorted(observed)}
        )
    fixture_mutation_ids = {row["mutation"].replace("_OR_RETRY", "_OR_RETRY") for row in fixtures["mutations"]}
    emit(
        "DCP-V13_FIXTURE_AND_MUTATION_MATRIX",
        dict(case_counts) == EXPECTED_CASE_COUNTS
        and set(mutations()) == fixture_mutation_ids
        and all(result["expected"] in result["observed"] for result in mutation_results)
        and all(result["decision"] == result["expected"] for result in typed_results),
        {"counts": dict(case_counts), "mutations": mutation_results, "typed": typed_results},
    )

    global_fences = fixtures["global_fences"]
    coherence = load_json(root, "spec/contracts/language-coherence-current-integrity-r1.json")
    emit(
        "DCP-V14_GLOBAL_EVIDENCE_FENCES",
        global_fences
        == {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "separate_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION",
        }
        and coherence["semantic_p0"] == 0
        and len(coherence["feature_p1_ids"]) == 22
        and len(coherence["separate_action_ids"]) == 4
        and len(coherence["product_lanes"]) == 15
        and coherence["product_execution"] == "NOT_RUN"
        and contract["global_fences"]["feature_p1"] == "22_OPEN_UNCHANGED"
        and contract["global_fences"]["separate_actions"] == "4_OPEN_UNCHANGED",
        global_fences,
    )

    failed = [row for row in checks if row["result"] != "PASS"]
    receipt = {
        "schema": "deeplus.deferred-call-plan-validation-receipt/r1",
        "revision": "R32-DEFERRED-CALL-PLAN-R1",
        "result": "PASS" if not failed else "FAIL",
        "checks": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "mutation_count": len(mutations()),
        "mutation_rejections": sum(
            1 for result in mutation_results if result["expected"] in result["observed"]
        ),
        "new_mir_operation_kind_count": contract["machine_projection"]["new_mir_operation_kind_count"],
        "new_diagnostic_id_count": contract["scope_fence"]["new_diagnostic_id_count"],
        "feature_p1": "22_OPEN_UNCHANGED",
        "separate_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_mutation": "NOT_PERFORMED",
        "check_results": checks,
    }
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
