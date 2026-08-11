#!/usr/bin/env python3
"""Validate the closed ActorTransportAllocationPlanV1 design candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/actor-transport-allocation-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/actor-transport-allocation-v1.schema.json"
DECISION_SCHEMA_REL = "schemas/language/actor-transport-allocation-decision-v1.schema.json"
FIXTURE_SCHEMA_REL = "schemas/language/actor-transport-allocation-fixtures-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/actor-transport-allocation-v1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Actor_Transport_Allocation_Closure_R1.md"

EXPECTED_RELATIONS = {
    ("ActorTransportAllocationAdmitted:RESPONSIBILITY_DROPPED", "ACTOR_TRANSPORT_ALLOCATION_RESPONSIBILITY_DROPPED", "primary"),
    ("ActorTransportAllocationAdmitted:POSTCOMMIT_ALLOCATION", "ACTOR_TRANSPORT_POSTCOMMIT_ALLOCATION_FORBIDDEN", "secondary"),
}
EXPECTED_CHECKER_FIXTURES = {
    "PF-ActorTransportAllocationAdmitted-POS",
    "PF-ActorTransportAllocationAdmitted-BOUNDARY",
    "PF-ActorTransportAllocationAdmitted-NEG-DROPPED",
    "PF-ActorTransportAllocationAdmitted-NEG-POSTCOMMIT",
}
EXPECTED_ORDER = [
    "STATIC_SELECT", "EVALUATE_OPERANDS", "LOCK_ADMISSION",
    "CHECK_RECEIVER_OPEN", "CHECK_BOUNDED_CAPACITY",
    "STAGE_ALL_ALLOCATIONS", "ENQUEUE_COMMIT",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
    validate_schema: bool = True,
) -> list[str]:
    errors: list[str] = []
    contract = contract_override or load(root / CONTRACT_REL)
    fixture = fixture_override or load(root / FIXTURE_REL)

    if validate_schema:
        try:
            import jsonschema  # type: ignore

            decision_schema = load(root / DECISION_SCHEMA_REL)
            fixture_schema = load(root / FIXTURE_SCHEMA_REL)
            store = {decision_schema["$id"]: decision_schema}
            resolver = jsonschema.RefResolver.from_schema(fixture_schema, store=store)
            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(fixture_schema, resolver=resolver).validate(fixture)
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover
            errors.append(f"SCHEMA_VALIDATION:{exc}")

    if contract.get("schema") != "deeplus.actor-transport-allocation/r1":
        errors.append("CONTRACT_SCHEMA_DRIFT")
    if contract.get("status") != "LOCAL_STABLE_DESIGN_CANDIDATE_NOT_INTEGRATED":
        errors.append("STATUS_DRIFT")
    if contract.get("gap_id") != "IR-ACTOR-P1-060":
        errors.append("GAP_ID_DRIFT")

    surface = contract.get("surface_responsibility", {})
    if surface != {
        "one_way_value_type": "Result<Unit, error ActorMessageError>",
        "request_value_type": "Result<Reply<T>, error ActorMessageError>",
        "throws": ["AllocationError"],
        "effects": ["allocate"],
        "actor_message_error_cases": ["mailboxFull", "receiverClosedBeforeAdmission", "receiverClosedBeforeReply"],
    }:
        errors.append("SURFACE_RESPONSIBILITY_DRIFT")

    profiles = contract.get("profiles", {})
    if profiles != {
        "logical_unbounded_v1": "NO_LANGUAGE_CAPACITY_REJECTION_FINITE_STORAGE_ALLOCATION_ERROR_VISIBLE",
        "bounded_reject_v1": "RECEIVER_CLOSED_THEN_CAPACITY_CHECK_THEN_PRECOMMIT_ALLOCATION",
    }:
        errors.append("MAILBOX_PROFILE_DRIFT")

    transaction = contract.get("transaction", {})
    if transaction.get("order") != EXPECTED_ORDER:
        errors.append("TRANSACTION_ORDER_DRIFT")
    if transaction.get("allocation_stages") != [
        "ENVELOPE_STORAGE", "MAILBOX_STORAGE_IF_REQUIRED",
        "REQUEST_RESPONSIBILITY_STORAGE_IF_REQUEST",
    ]:
        errors.append("ALLOCATION_STAGE_DRIFT")
    if transaction.get("failure") != {
        "outcome": "THROW_ALLOCATION_ERROR",
        "owner": "SENDER",
        "reverse_cleanup": True,
        "message_publish_count": 0,
        "channel_sequence_count": 0,
        "reply_id_publish_count": 0,
        "correlation_id_publish_count": 0,
        "ownership_commit_count": 0,
    }:
        errors.append("ALLOCATION_FAILURE_ATOMICITY_DRIFT")
    if transaction.get("commit") != {
        "atomic": True,
        "message_publish_count": 1,
        "channel_sequence_count": 1,
        "ownership_commit_count": 1,
        "request_identity_publish_count_if_request": 2,
        "postcommit_allocation_count": 0,
    }:
        errors.append("ENQUEUE_COMMIT_DRIFT")
    if contract.get("hir_contract") != {
        "plan": "ActorTransportAllocationPlanV1",
        "error_set": ["AllocationError"],
        "effect_row": ["allocate"],
        "publish_phase": "ENQUEUE_COMMIT",
        "postcommit_allocation_count": 0,
    }:
        errors.append("HIR_CONTRACT_DRIFT")
    if contract.get("mir_contract") != {
        "allocation_reject_phase": "allocation_rejected",
        "error_successor": "ERROR",
        "allocation_error": "AllocationError",
        "allocation_effect": "allocate",
        "postcommit_allocation_count": 0,
    }:
        errors.append("MIR_CONTRACT_DRIFT")
    if contract.get("governance") != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_mutation": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE_DRIFT")

    cases = fixture.get("cases", [])
    counts = {kind: sum(row.get("class") == kind for row in cases) for kind in ("normal", "boundary", "reject")}
    if len(cases) != 14 or counts != {"normal": 4, "boundary": 4, "reject": 6}:
        errors.append(f"FIXTURE_COUNTS:{len(cases)}:{counts}")
    if len({row.get("case_id") for row in cases}) != len(cases):
        errors.append("FIXTURE_ID_DUPLICATE")
    for row in cases:
        descriptor = row.get("descriptor", {})
        if row.get("class") != "reject" and descriptor.get("decision") != row.get("expected"):
            errors.append(f"FIXTURE_ORACLE:{row.get('case_id')}")
        if row.get("class") == "reject" and row.get("expected") not in {"REJECT_STATIC", "REJECT_MIR"}:
            errors.append(f"FIXTURE_REJECT_ORACLE:{row.get('case_id')}")
        if descriptor.get("published_residue_count") and descriptor.get("decision") != "ADMIT" and descriptor.get("allocation_stage") != "POSTCOMMIT":
            errors.append(f"FIXTURE_FAILURE_PUBLISHED:{row.get('case_id')}")

    actor = load(root / "spec/contracts/actor-concurrency-coherence.json")
    actor_rules = {row.get("rule_id"): row.get("contract", {}) for row in actor.get("rules", [])}
    r4 = actor_rules.get("ACC-R004", {})
    r7 = actor_rules.get("ACC-R007", {})
    r8 = actor_rules.get("ACC-R008", {})
    r21 = actor_rules.get("ACC-R021", {})
    if r4.get("allocation_contract") != CONTRACT_REL or r4.get("postcommit_allocation_count") != 0:
        errors.append("ACTOR_MAILBOX_BINDING_DRIFT")
    if "throws AllocationError effects allocate" not in r7.get("message_expression_type", ""):
        errors.append("ACTOR_SEND_RESPONSIBILITY_DRIFT")
    if "throws AllocationError effects allocate" not in r8.get("message_expression_type", ""):
        errors.append("ACTOR_REQUEST_RESPONSIBILITY_DRIFT")
    if r21.get("postcommit_allocation_count") != 0 or r21.get("dynamic_error_axis") != ["AllocationError"]:
        errors.append("ACTOR_R021_DRIFT")

    managed = load(root / "spec/contracts/managed-reference-memory-profile-r1.json")
    if managed.get("allocation_contract", {}).get("recoverable_error_id") != "AllocationError" or managed.get("allocation_contract", {}).get("effect_id") != "allocate":
        errors.append("MANAGED_ALLOCATION_AXIS_DRIFT")

    frontend = load(root / "spec/frontend/frontend-model.json").get("concurrency_frontend_contract", {})
    enqueue = frontend.get("enqueue_commit_contract", {})
    if enqueue.get("transport_error_set") != ["AllocationError"] or enqueue.get("transport_effect_row") != ["allocate"] or enqueue.get("postcommit_allocation_count") != 0:
        errors.append("FRONTEND_ALLOCATION_BINDING_DRIFT")

    hir = load(root / "schemas/language/canonical-hir-h1.schema.json")
    call_plan = hir.get("$defs", {}).get("CallPlan", {})
    hir_fields = {"transport_allocation_plan_id", "transport_error_set", "transport_effect_row", "allocation_publish_phase", "postcommit_allocation_count"}
    if not hir_fields <= set(call_plan.get("properties", {})):
        errors.append("HIR_FIELDS_MISSING")
    actor_branch = next((row for row in call_plan.get("allOf", []) if row.get("if", {}).get("properties", {}).get("mode_target_pair", {}).get("const") == "ACTOR_MESSAGE::ACTOR_TRANSPORT"), {})
    if not hir_fields <= set(actor_branch.get("then", {}).get("required", [])):
        errors.append("HIR_ACTOR_REQUIRED_FIELDS_MISSING")

    bridge = load(root / "spec/contracts/hir-h1-current-mir-bridge.json")
    if not hir_fields <= set(bridge.get("call_plan_contract", {}).get("actor_transport_required_fields", [])):
        errors.append("HIR_BRIDGE_FIELDS_MISSING")

    mir = load(root / "schemas/language/mir-responsibility.schema.json")
    event = mir.get("$defs", {}).get("actor_lifecycleEvent", {})
    mir_fields = {"transport_attempt_id", "allocation_stage", "allocation_error", "allocation_effect", "allocation_reservation_count", "postcommit_allocation_count"}
    if not mir_fields <= set(event.get("required", [])) or not mir_fields <= set(event.get("properties", {})):
        errors.append("MIR_ALLOCATION_FIELDS_MISSING")
    if "allocation_rejected" not in event.get("properties", {}).get("phase", {}).get("enum", []):
        errors.append("MIR_ALLOCATION_REJECT_PHASE_MISSING")

    lowering = load(root / "spec/contracts/hir-mir-lowering-registry.json")
    row = next((item for item in lowering.get("rows", []) if item.get("row_id") == "HM-LR-CALL-010"), {})
    if row.get("successor_roles") != ["NORMAL", "ERROR", "DEFECT", "CANCELLATION"]:
        errors.append("LOWERING_ERROR_SUCCESSOR_MISSING")
    if lowering.get("actor_transport_allocation_contract", {}).get("postcommit_allocation_count") != 0:
        errors.append("LOWERING_ALLOCATION_BINDING_MISSING")

    unified = load(root / "spec/contracts/unified-call-tilde-trace-closure-r1.json").get("actor_transport", {})
    if unified.get("transport_error_set") != ["AllocationError"] or unified.get("transport_effect_row") != ["allocate"] or unified.get("postcommit_allocation_count") != 0:
        errors.append("UNIFIED_CALL_ALLOCATION_DRIFT")

    diagnostics = {row.get("diagnostic_id") for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    expected_diagnostics = {"ACTOR_TRANSPORT_ALLOCATION_RESPONSIBILITY_DROPPED", "ACTOR_TRANSPORT_POSTCOMMIT_ALLOCATION_FORBIDDEN"}
    if not expected_diagnostics <= diagnostics:
        errors.append("DIAGNOSTIC_SET_MISSING")
    predicates = {row.get("predicate_id"): row for row in all_rows(root, "spec/types/predicates/chunks")}
    predicate = predicates.get("ActorTransportAllocationAdmitted", {})
    if predicate.get("input_descriptor_schema") != DECISION_SCHEMA_REL or predicate.get("product_support") != "NOT_RUN":
        errors.append("PREDICATE_BINDING_DRIFT")
    observed_relations = {
        (row.get("violation_id"), row.get("diagnostic_id"), row.get("relation"))
        for row in all_rows(root, "spec/diagnostics/relations/chunks")
        if row.get("predicate_id") == "ActorTransportAllocationAdmitted"
    }
    if observed_relations != EXPECTED_RELATIONS:
        errors.append("RELATION_SET_DRIFT")
    observed_checker = {
        row.get("fixture_id") for row in all_rows(root, "tests/conformance/checker-predicates/chunks")
        if row.get("predicate_id") == "ActorTransportAllocationAdmitted"
    }
    if observed_checker != EXPECTED_CHECKER_FIXTURES:
        errors.append("CHECKER_FIXTURE_SET_DRIFT")

    features = {row.get("feature_id"): row for row in all_rows(root, "spec/features/catalog/chunks")}
    for feature_id in ("actor_mailbox_capacity", "actor_request_reply"):
        feature = features.get(feature_id, {})
        refs = feature.get("normative_trace_refs", {})
        if "ActorTransportAllocationAdmitted" not in refs.get("predicates", []):
            errors.append(f"FEATURE_PREDICATE_TRACE:{feature_id}")
        if not expected_diagnostics <= set(refs.get("diagnostics", [])):
            errors.append(f"FEATURE_DIAGNOSTIC_TRACE:{feature_id}")
        for artifact in (CONTRACT_REL, CONTRACT_SCHEMA_REL, FIXTURE_REL):
            if artifact not in feature.get("artifact_trace_refs", []):
                errors.append(f"FEATURE_ARTIFACT_TRACE:{feature_id}:{artifact}")
        if feature.get("product_support") != "NOT_RUN":
            errors.append(f"FEATURE_PRODUCT_OVERCLAIM:{feature_id}")

    for relative in (CONTRACT_REL, CONTRACT_SCHEMA_REL, DECISION_SCHEMA_REL, FIXTURE_SCHEMA_REL, FIXTURE_REL, DECISION_REL):
        if not (root / relative).is_file():
            errors.append(f"ARTIFACT_MISSING:{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    fixture = load(args.root.resolve() / FIXTURE_REL)
    counts = {kind: sum(row.get("class") == kind for row in fixture.get("cases", [])) for kind in ("normal", "boundary", "reject")}
    print(json.dumps({
        "schema": "deeplus.actor-transport-allocation-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "gap": "IR-ACTOR-P1-060",
        "cases": counts,
        "semantic_p0": 0,
        "global_feature_p1": "22_OPEN_UNCHANGED",
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "NOT_PERFORMED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
