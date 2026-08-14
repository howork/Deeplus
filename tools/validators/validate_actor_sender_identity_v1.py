#!/usr/bin/env python3
"""Validate the R91 Actor Sender Identity V1 design closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT = "spec/contracts/actor-sender-identity-v1.json"
CONTRACT_SCHEMA = "schemas/language/actor-sender-identity-v1.schema.json"
DECISION_SCHEMA = "schemas/language/actor-sender-identity-decision-v1.schema.json"
FIXTURE_SCHEMA = "schemas/language/actor-sender-identity-fixtures-v1.schema.json"
FIXTURE = "tests/fixtures/current/actor-sender-identity-v1.json"
ACTOR = "spec/contracts/actor-concurrency-coherence.json"
UNIFIED = "spec/contracts/unified-call-actor-transport.json"
FRONTEND = "spec/frontend/frontend-model.json"
HIR = "schemas/language/canonical-hir-h1.schema.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
LOWERING = "spec/contracts/hir-mir-lowering-registry.json"
MIR_SCHEMA = "schemas/language/mir-responsibility.schema.json"
CRANELIFT = "spec/contracts/cranelift-backend-current.json"
DIAGNOSTICS = "spec/diagnostics/catalog/chunks/part-0039.json"
PREDICATE = "spec/types/predicates/chunks/part-0030.json"
RELATIONS = "spec/diagnostics/relations/chunks/part-0020.json"
CHECKER_FIXTURES = "tests/conformance/checker-predicates/chunks/part-0042.json"
PRODUCT = "current/product-lanes.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path, overrides: dict[str, Any] | None = None) -> list[str]:
    overrides = overrides or {}
    errors: list[str] = []

    def value(relative: str) -> Any:
        return overrides.get(relative, load(root / relative))

    contract = value(CONTRACT)
    fixture = value(FIXTURE)
    actor = value(ACTOR)
    unified = value(UNIFIED)
    frontend = value(FRONTEND)
    hir = value(HIR)
    bridge = value(BRIDGE)
    lowering = value(LOWERING)
    mir_schema = value(MIR_SCHEMA)
    cranelift = value(CRANELIFT)
    diagnostics = value(DIAGNOSTICS)
    predicates = value(PREDICATE)
    relations = value(RELATIONS)
    checker_fixtures = value(CHECKER_FIXTURES)

    try:
        from jsonschema import Draft202012Validator

        contract_schema = value(CONTRACT_SCHEMA)
        decision_schema = value(DECISION_SCHEMA)
        fixture_schema = value(FIXTURE_SCHEMA)
        for schema in (contract_schema, decision_schema, fixture_schema):
            Draft202012Validator.check_schema(schema)
        Draft202012Validator(contract_schema).validate(contract)
        Draft202012Validator(fixture_schema).validate(fixture)
        for row in fixture.get("cases", []):
            Draft202012Validator(decision_schema).validate(row.get("descriptor"))
    except ImportError:
        pass
    except Exception as exc:
        errors.append(f"SCHEMA:{type(exc).__name__}")

    domain = contract.get("identity_domain", {})
    selection = contract.get("selection", {})
    lifetime = contract.get("lifetime", {})
    channel = contract.get("channel_binding", {})
    if domain != {
        "name": "SenderId",
        "variants": ["Actor(ActorInstanceId)", "Execution(ExecutionId)"],
        "tagged_disjoint": True,
        "source_constructor_count": 0,
        "send_time_identity_allocation_count": 0,
        "serialization_or_abi_identity": False,
        "authority_grant": False,
    }:
        errors.append("IDENTITY_DOMAIN")
    if selection != {
        "plan": "ActorSenderIdentityPlanV1",
        "precedence": ["ACTIVE_ACTOR_TURN_USES_ACTOR_INSTANCE", "OTHERWISE_CURRENT_EXECUTION"],
        "actor_turn_required_for_actor_variant": True,
        "structured_child_inherits_actor_turn": False,
        "runtime_search_count": 0,
        "source_order_winner_count": 0,
    }:
        errors.append("SELECTION")
    if lifetime != {
        "actor_suspend_resume": "PRESERVE_ACTOR_INSTANCE_SENDER",
        "execution_suspend_resume": "PRESERVE_EXECUTION_SENDER",
        "actor_restart": "NEW_ACTOR_INSTANCE_NEW_SENDER",
        "structured_child": "NEW_EXECUTION_NEW_SENDER",
        "queued_message_after_origin_termination": "PRESERVE_IMMUTABLE_SENDER_VALUE",
        "identity_reuse_while_observable": False,
    }:
        errors.append("LIFETIME")
    if channel.get("key") != ["SenderId", "ReceiverActorId", "MailboxProfileId"] or channel.get("channel_id_derivation") != "INJECTIVE_FROM_EXACT_TAGGED_KEY" or channel.get("fifo_scope") != "ONE_EXACT_CHANNEL_KEY" or channel.get("global_order") is not False or channel.get("fairness") is not False:
        errors.append("CHANNEL_BINDING")

    cases = fixture.get("cases", [])
    expected_ids = (
        [f"R91-ASI-POS-{i:03d}" for i in range(1, 6)]
        + [f"R91-ASI-BND-{i:03d}" for i in range(1, 6)]
        + [f"R91-ASI-NEG-{i:03d}" for i in range(1, 7)]
    )
    if [row.get("case_id") for row in cases] != expected_ids:
        errors.append("CASE_IDS")
    if [sum(row.get("class") == kind for row in cases) for kind in ("normal", "boundary", "reject")] != [5, 5, 6]:
        errors.append("CASE_COUNTS")

    for row in cases:
        d = row.get("descriptor", {})
        expected = row.get("expected")
        context = d.get("context")
        proposed = d.get("proposed_sender_kind")
        phase = d.get("phase")
        relation = d.get("relation")
        derived: str
        diagnostic: str | None = None
        if d.get("send_time_identity_allocation_count") != 0:
            derived, diagnostic = "REJECT_MIR", "MIR_ACTOR_SENDER_IDENTITY_INVALID"
        elif context == "NO_EXECUTION_CONTEXT":
            derived, diagnostic = "REJECT_STATIC", "ACTOR_SENDER_CONTEXT_UNAVAILABLE"
        elif proposed in {"PER_SEND", "UNTAGGED"}:
            derived, diagnostic = "REJECT_MIR", "MIR_ACTOR_SENDER_IDENTITY_INVALID"
        elif proposed in {"STATIC_ACTOR_DECLARATION", "ACTOR_TURN", "NONE"}:
            derived, diagnostic = "REJECT_STATIC", "ACTOR_SENDER_CONTEXT_UNAVAILABLE"
        elif phase == "RESTARTED" and relation != "DISTINCT_FROM_PRE_RESTART":
            derived, diagnostic = "REJECT_MIR", "MIR_ACTOR_SENDER_IDENTITY_INVALID"
        elif phase == "ORIGIN_TERMINATED_MESSAGE_QUEUED" and relation == "PRESERVED_IN_QUEUED_MESSAGE":
            derived = "PRESERVE_QUEUED"
        elif d.get("actor_turn_authority") is True and d.get("actor_instance_available") is True and proposed == "ACTOR_INSTANCE" and context != "STRUCTURED_CHILD_EXECUTION":
            derived = "ADMIT_ACTOR"
        elif d.get("actor_turn_authority") is False and d.get("execution_id_available") is True and proposed == "EXECUTION":
            derived = "ADMIT_EXECUTION"
        else:
            derived, diagnostic = "REJECT_STATIC", "ACTOR_SENDER_CONTEXT_UNAVAILABLE"
        if derived != expected or d.get("decision") != expected:
            errors.append(f"CASE_DECISION:{row.get('case_id')}")
        if diagnostic != d.get("diagnostic_or_null"):
            errors.append(f"CASE_DIAGNOSTIC:{row.get('case_id')}")

    rules = actor.get("rules", [])
    if [row.get("rule_id") for row in rules] != [f"ACC-R{i:03d}" for i in range(1, 23)]:
        errors.append("ACTOR_RULE_IDS")
    r91 = next((row for row in rules if row.get("rule_id") == "ACC-R022"), {}).get("contract", {})
    if r91.get("contract") != CONTRACT or r91.get("sender_domain") != domain.get("variants") or r91.get("send_time_identity_allocation_count") != 0 or r91.get("runtime_sender_search_count") != 0:
        errors.append("ACTOR_CONTRACT_BINDING")
    if actor.get("machine_acceptance", {}).get("rule_count") != 22:
        errors.append("ACTOR_RULE_COUNT")

    if unified.get("machine_acceptance", {}).get("actor_sender_identity_plan_count") != 1 or unified.get("canonical_hir_projection", {}).get("actor_sender_identity", {}).get("plan_id_field") != "sender_identity_plan_id":
        errors.append("UNIFIED_CALL_BINDING")
    identity = frontend.get("concurrency_frontend_contract", {})
    if "ActorSenderIdentityPlanId" not in identity.get("typed_hir_identities", []) or "SenderId" not in identity.get("mir_runtime_only_identities", []) or identity.get("sender_identity_contract", {}).get("runtime_search_count") != 0:
        errors.append("FRONTEND_BINDING")

    call_plan = hir.get("$defs", {}).get("CallPlan", {})
    properties = call_plan.get("properties", {})
    if "sender_identity_plan_id" not in properties:
        errors.append("HIR_FIELD")
    bridge_fields = bridge.get("call_plan_contract", {}).get("actor_transport_required_fields", [])
    if "sender_identity_plan_id" not in bridge_fields:
        errors.append("BRIDGE_FIELD")
    lower = lowering.get("actor_sender_identity_contract", {})
    if lower.get("contract") != CONTRACT or lower.get("send_time_identity_allocation_count") != 0 or lower.get("runtime_search_count") != 0:
        errors.append("LOWERING_BINDING")

    sender_annotations = 0
    stack = [mir_schema]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            if item.get("x-deeplus-semantic-domain") == "SenderIdV1":
                sender_annotations += 1
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    if sender_annotations != 3 or "actor_sender_identity" not in mir_schema.get("x-deeplus-semantic-contract", {}):
        errors.append("MIR_DOMAIN_BINDING")
    backend = cranelift.get("actor_projection_guard", {})
    if backend.get("sender_identity_contract") != CONTRACT or backend.get("sender_identity_reselection_count") != 0 or backend.get("sender_identity_address_or_thread_derivation_count") != 0 or backend.get("sender_identity_tag_erasure_count") != 0:
        errors.append("CRANELIFT_BINDING")

    diagnostic_ids = [row.get("diagnostic_id") for row in diagnostics]
    if diagnostic_ids != ["ACTOR_SENDER_CONTEXT_UNAVAILABLE", "MIR_ACTOR_SENDER_IDENTITY_INVALID"]:
        errors.append("DIAGNOSTICS")
    predicate = predicates[0] if len(predicates) == 1 else {}
    if predicate.get("predicate_id") != "ActorSenderIdentityAdmitted" or predicate.get("input_descriptor_schema") != DECISION_SCHEMA or predicate.get("runtime_dispatch_count") != 0 or predicate.get("send_time_identity_allocation_count") != 0:
        errors.append("PREDICATE")
    if {(row.get("predicate_id"), row.get("diagnostic_id")) for row in relations} != {("ActorSenderIdentityAdmitted", "ACTOR_SENDER_CONTEXT_UNAVAILABLE"), ("ActorSenderIdentityAdmitted", "MIR_ACTOR_SENDER_IDENTITY_INVALID")}:
        errors.append("RELATIONS")
    if len(checker_fixtures) != 4 or {row.get("fixture_id") for row in checker_fixtures} != set(predicate.get("positive_fixture_ids", []) + predicate.get("negative_fixture_ids", [])):
        errors.append("CHECKER_FIXTURES")

    governance = contract.get("governance", {})
    if governance != {"semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "github_mutation": "NOT_PERFORMED"}:
        errors.append("GOVERNANCE")
    product = value(PRODUCT)
    lanes = product.get("lanes", [])
    if len(lanes) != 15 or any(row.get("status") != "NOT_RUN" for row in lanes):
        errors.append("PRODUCT_LANES")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    receipt = {
        "schema": "deeplus.actor-sender-identity-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "normal": "5_OF_5_PASS" if not errors else "BLOCKED",
        "boundary": "5_OF_5_PASS" if not errors else "BLOCKED",
        "reject": "6_OF_6_PASS" if not errors else "BLOCKED",
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
