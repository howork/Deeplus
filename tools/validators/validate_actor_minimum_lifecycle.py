#!/usr/bin/env python3
"""Focused static validator for the rebased Actor minimum lifecycle contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def rows_from_chunks(relative: str) -> list[dict]:
    rows: list[dict] = []
    for path in sorted((ROOT / relative).glob("part-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            fail(f"catalog chunk is not an array: {path}")
        rows.extend(payload)
    return rows


def fail(message: str) -> None:
    raise SystemExit(f"ACTOR_MINIMUM_LIFECYCLE_FAIL: {message}")


def valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and set(value) <= set("0123456789abcdef")
    )


def binding_failure(row: dict) -> str | None:
    selection = row.get("binding_selection")
    events = row.get("events", [])
    if selection is None:
        if any(event.get("binding_id") is not None for event in events):
            return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
        return None
    required = {
        "table_id",
        "binding_id",
        "implementation_kind",
        "actor_handler_id",
        "actor_request_id",
        "responsibility_id",
        "binding_row_sha256",
    }
    if set(selection) != required or not valid_digest(selection.get("binding_row_sha256")):
        return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
    kind = selection.get("implementation_kind")
    if kind == "SEND_TO_ON":
        if not isinstance(selection.get("actor_handler_id"), str) or selection.get("actor_request_id") is not None:
            return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
    elif kind == "REQUEST_TO_REQUEST":
        if selection.get("actor_handler_id") is not None or not isinstance(selection.get("actor_request_id"), str):
            return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
    else:
        return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
    if not all(isinstance(selection.get(key), str) and selection[key] for key in ("table_id", "binding_id", "responsibility_id")):
        return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
    for event in events:
        if event.get("binding_id") is not None and event.get("binding_id") != selection["binding_id"]:
            return "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID"
        if event.get("phase") in {"reply_terminal", "pending_reply_terminalized"}:
            if (
                kind != "REQUEST_TO_REQUEST"
                or event.get("responsibility_id") != selection["responsibility_id"]
                or event.get("binding_row_sha256") != selection["binding_row_sha256"]
            ):
                return "ACTOR_LIFECYCLE_REPLY_BINDING_INVALID"
    if kind == "SEND_TO_ON" and any(
        event.get("phase") in {"reply_terminal", "pending_reply_terminalized"}
        for event in events
    ):
        return "ACTOR_LIFECYCLE_REPLY_BINDING_INVALID"
    return None


def first_failure(row: dict) -> str | None:
    root_owner = row.get("root_owner_id")
    events = row.get("events", [])
    identity_fields = (
        row.get("static_actor_id"),
        row.get("actor_instance_id"),
        row.get("state_region_id"),
        root_owner,
    )
    if (
        any(not isinstance(value, str) or not value for value in identity_fields)
        or len(set(identity_fields)) != len(identity_fields)
        or row.get("binding_set_verified_before_prepare") is not True
        or not isinstance(events, list)
    ):
        return "ACTOR_LIFECYCLE_IDENTITY_INVALID"
    foreign_key_failure = binding_failure(row)
    if foreign_key_failure is not None:
        return foreign_key_failure
    phases = [event.get("phase") for event in events if isinstance(event, dict)]
    if len(phases) != len(events):
        return "ACTOR_LIFECYCLE_IDENTITY_INVALID"

    if "actor_publish_committed" in phases:
        publish = phases.index("actor_publish_committed")
        if (
            "state_initialized" not in phases[:publish]
            or "mailbox_initialized" not in phases[:publish]
            or "create_failed" in phases[:publish]
        ):
            return "ACTOR_LIFECYCLE_PUBLICATION_BEFORE_COMMIT"
        if phases[: publish + 1] != [
            "create_prepare",
            "state_initialized",
            "mailbox_initialized",
            "actor_publish_committed",
        ]:
            return "ACTOR_LIFECYCLE_PUBLICATION_BEFORE_COMMIT"
    if "create_failed" in phases:
        failed = events[phases.index("create_failed")]
        if failed.get("failure_id") is None or failed.get("state_after") != "CREATION_ABORTED":
            return "ACTOR_LIFECYCLE_IDENTITY_INVALID"
        initialized = [
            event.get("resource_id")
            for event in events[: phases.index("create_failed")]
            if event.get("phase") in {"state_initialized", "mailbox_initialized"}
        ]
        cleaned = [
            event.get("resource_id")
            for event in events[phases.index("create_failed") + 1 :]
            if event.get("phase") == "initialized_resource_cleaned"
        ]
        if cleaned != list(reversed(initialized)) or "termination_published" in phases:
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"

    normal_order = [
        "stop_requested",
        "admission_closed",
        "drain_started",
        "drain_completed",
        "actor_state_cleanup_completed",
        "root_owner_observed",
        "termination_published",
    ]
    if all(phase in phases for phase in normal_order):
        positions = [phases.index(phase) for phase in normal_order]
        if positions != sorted(positions):
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"
    if "actor_state_cleanup_completed" in phases and "drain_completed" in phases:
        if phases.index("actor_state_cleanup_completed") < phases.index("drain_completed"):
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"
    if row.get("active_turn_state") == "SUSPENDED_INDEFINITELY" and any(
        phase in phases
        for phase in ("actor_state_cleanup_completed", "root_owner_observed", "termination_published")
    ):
        return "ACTOR_LIFECYCLE_TRANSITION_INVALID"
    if row.get("active_turn_state") == "SUSPENDED_INDEFINITELY":
        suspended = [event for event in events if event.get("phase") == "turn_suspend"]
        if (
            len(suspended) != 1
            or suspended[0].get("turn_id") != row.get("active_turn_id")
            or suspended[0].get("state_region_id") != row.get("state_region_id")
            or suspended[0].get("state_region_authority") != "held"
        ):
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"

    if "admission_closed" in phases:
        close = phases.index("admission_closed")
        if "enqueue_committed" in phases[close + 1 :]:
            return "ACTOR_LIFECYCLE_ADMISSION_AFTER_CLOSE"
    if "defect_observed" in phases:
        defect = phases.index("defect_observed")
        if "turn_start" in phases[defect + 1 :]:
            return "ACTOR_LIFECYCLE_HANDLER_AFTER_DEFECT"
        if "pending_reply_terminalized" in phases:
            terminal = phases.index("pending_reply_terminalized")
            required_cleanup = {
                "queued_payload_cleaned",
                "active_turn_cleanup_completed",
                "actor_state_cleanup_completed",
            }
            if not required_cleanup.issubset(phases[defect + 1 : terminal]):
                return "ACTOR_LIFECYCLE_TRANSITION_INVALID"
        if len(set(row.get("suppressed_cleanup_defect_ids", []))) != len(
            row.get("suppressed_cleanup_defect_ids", [])
        ):
            return "ACTOR_LIFECYCLE_IDENTITY_INVALID"
        snapshot = row.get("open_reply_ids_at_defect", [])
        terminalized = [
            event.get("reply_id")
            for event in events[defect + 1 :]
            if event.get("phase") == "pending_reply_terminalized"
        ]
        if terminalized and terminalized != snapshot:
            return "ACTOR_LIFECYCLE_REPLY_TERMINAL_CARDINALITY"

    for reply_id in row.get("pending_request_ids", []):
        count = sum(
            event.get("reply_id") == reply_id
            and event.get("phase") in {"reply_terminal", "pending_reply_terminalized"}
            for event in events
            if isinstance(event, dict)
        )
        if count != 1:
            return "ACTOR_LIFECYCLE_REPLY_TERMINAL_CARDINALITY"
    for message_id in row.get("queued_message_ids", []):
        count = sum(
            event.get("message_id") == message_id
            and event.get("phase") == "queued_payload_cleaned"
            for event in events
            if isinstance(event, dict)
        )
        if count != 1:
            return "ACTOR_LIFECYCLE_PAYLOAD_CLEANUP_CARDINALITY"

    if "defect_observed" in phases and "turn_start" not in phases[phases.index("defect_observed") + 1 :]:
        active_turn_id = row.get("active_turn_id")
        turn_cleanups = [
            event for event in events if event.get("phase") == "active_turn_cleanup_completed"
        ]
        if active_turn_id is not None and (
            len(turn_cleanups) != 1 or turn_cleanups[0].get("turn_id") != active_turn_id
        ):
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"
        state_cleanups = [
            event for event in events if event.get("phase") == "actor_state_cleanup_completed"
        ]
        if "termination_published" in phases and (
            len(state_cleanups) != 1
            or state_cleanups[0].get("resource_id") != row.get("state_region_id")
        ):
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"

    if "termination_published" in phases:
        termination = phases.index("termination_published")
        if "root_owner_observed" not in phases[:termination]:
            return "ACTOR_LIFECYCLE_ROOT_OBSERVATION_INVALID"
        if "actor_state_cleanup_completed" not in phases[:termination]:
            return "ACTOR_LIFECYCLE_TERMINATION_BEFORE_CLEANUP"
        if termination != len(phases) - 1 or phases.count("termination_published") != 1:
            return "ACTOR_LIFECYCLE_TRANSITION_INVALID"
        if phases[:termination].count("root_owner_observed") != 1:
            return "ACTOR_LIFECYCLE_ROOT_OBSERVATION_INVALID"
    if row.get("supervisor_id") is not None or "restart_requested" in phases:
        return "ACTOR_LIFECYCLE_DEFERRED_POLICY_ACTIVATED"
    return None


def main() -> int:
    contract = load("spec/contracts/actor-concurrency-coherence.json")
    binding_contract = load("spec/contracts/actor-protocol-binding-descriptor.json")
    schema = load("schemas/language/mir-responsibility.schema.json")
    fixtures = load("tests/fixtures/current/actor-concurrency-coherence-r1.json")
    frontend = load("spec/frontend/frontend-model.json")
    trace_contract = load("spec/contracts/actor-minimum-lifecycle-trace-r1.json")
    guard_matrix = load("tests/conformance/actor-lifecycle-guards-r1.json")
    feature_rows = rows_from_chunks("spec/features/catalog/chunks")
    handoff = (ROOT / "decisions/language/Design_Deeplus_Actor_Minimum_Lifecycle_Implementation_Handoff_R1.md").read_text(encoding="utf-8")
    language = (ROOT / "spec/language.md").read_text(encoding="utf-8")
    mir = (ROOT / "spec/mir/semantics.md").read_text(encoding="utf-8")

    rules = {row["rule_id"]: row["contract"] for row in contract["rules"]}
    if list(rules) != [f"ACC-R{i:03d}" for i in range(1, 23)]:
        fail("rule IDs are not the exact contiguous ACC-R001..022 set")
    r41 = rules["ACC-R019"]
    if (
        r41.get("binding_identity")
        != "ActorProtocolBindingId(ActorProtocolConformanceId, ActorProtocolRequirementId)"
        or r41.get("candidate_cardinality") != "EXACTLY_ONE"
        or r41.get("runtime_lookup_count") != 0
    ):
        fail("R41 direct-conformance prefix drift")
    if (
        binding_contract["identity"].get("actor_id_domain")
        != "STATIC_ACTOR_DECLARATION_ID"
        or binding_contract["identity"].get("binding_key")
        != ["ActorProtocolConformanceId", "ActorProtocolRequirementId"]
        or binding_contract["identity"].get(
            "runtime_actor_instance_identity_in_serialized_bytes_count"
        )
        != 0
    ):
        fail("R23 binding identity drift")

    lifecycle = rules["ACC-R020"]
    if lifecycle.get("normal_stop_policy") != "DRAIN_ALL_COMMITTED_V1":
        fail("normal stop policy drift")
    if lifecycle.get("defect_policy") != "STOP_AND_FAIL_PENDING_V1":
        fail("Defect policy drift")
    if lifecycle.get("current_supervisor_id") is not None:
        fail("supervisor_id must remain null")
    if (
        lifecycle.get("runtime_instance_in_module_binding_bytes_count") != 0
        or lifecycle.get("lifecycle_binding_creation_count") != 0
        or lifecycle.get("lifecycle_binding_reselection_count") != 0
        or lifecycle.get("r24_codegen_lifetime_absorbed_count") != 0
    ):
        fail("R22/R23/R24 boundary drift")
    if lifecycle.get("restart_event_count") != 0 or lifecycle.get("interleaving_event_count") != 0:
        fail("deferred lifecycle surface activated")
    if (
        lifecycle.get("feature_id") != "actor_minimum_lifecycle_r1"
        or lifecycle.get("trace_contract")
        != "spec/contracts/actor-minimum-lifecycle-trace-r1.json"
        or lifecycle.get("compiler_source_diagnostic_lane")
        != "NOT_APPLICABLE_INTERNAL_LIFECYCLE_EVIDENCE_INVARIANT"
        or lifecycle.get("acceptance_matrix")
        != "tests/conformance/actor-lifecycle-guards-r1.json"
        or lifecycle.get("acceptance_guard_coverage") != "12_OF_12"
        or lifecycle.get("debugger_projection")
        != "RECEIPT_BOUND_READ_ONLY_IDENTITY_STATE_AND_COMMITTED_EVENT_ORDER_PRODUCT_NOT_RUN"
    ):
        fail("R51 lifecycle trace binding drift")
    defect_order = lifecycle.get("defect_order", [])
    if not (
        defect_order.index("actor_state_cleanup_completed")
        < defect_order.index("pending Reply terminalization")
        < defect_order.index("root_owner_observed")
    ):
        fail("Defect cleanup/reply/root observation order drift")

    machine = contract["machine_acceptance"]
    if machine.get("rule_count") != 22 or machine.get("gate_count") != 6:
        fail("contract count closure drift")
    if machine.get("product_execution_receipt_count") != 0:
        fail("product execution overclaim")

    event = schema["$defs"]["actor_lifecycleEvent"]
    required = set(event["required"])
    fields = {
        "root_owner_id",
        "supervisor_id",
        "lifecycle_policy",
        "lifecycle_state_before",
        "lifecycle_state_after",
        "resource_cleanup_count",
        "reply_terminal_count",
        "defect_id",
    }
    if not fields.issubset(required):
        fail("MIR lifecycle required fields incomplete")
    if event["properties"]["supervisor_id"].get("type") != "null":
        fail("MIR supervisor compatibility field is not fixed to null")
    phases = set(event["properties"]["phase"]["enum"])
    states = set(event["properties"]["lifecycle_state_after"]["enum"])
    if "supervisor_disposition" in phases or "CREATION_ABORTED" not in states:
        fail("MIR lifecycle phase/state set drift")
    ordering = schema.get("x-deeplus-actor-lifecycle-ordering", {})
    if (
        ordering.get("state_region_identity") != "StateRegionId"
        or ordering.get("defect_order", []).index("actor_state_cleanup_completed")
        > ordering.get("defect_order", []).index("pending_reply_terminalized")
        or ordering.get("r41_binding_runtime_reselection_count") != 0
        or ordering.get("r23_binding_runtime_reselection_count") != 0
        or ordering.get("r23_binding_creation_count") != 0
        or ordering.get("runtime_instance_in_binding_bytes_count") != 0
        or ordering.get("r24_codegen_lifetime_absorbed_count") != 0
    ):
        fail("MIR lifecycle ordering metadata drift")

    rows = fixtures.get("actor_lifecycle_binding_cases", [])
    if len(rows) != 10 or len({row.get("fixture_id") for row in rows}) != 10:
        fail("lifecycle fixture identity/count drift")
    mismatches = [
        (row.get("fixture_id"), row.get("expected_failed_guard"), first_failure(row))
        for row in rows
        if row.get("expected_failed_guard") != first_failure(row)
    ]
    if mismatches:
        fail(f"fixture guard mismatch: {mismatches}")
    counts = fixtures["expected_counts"]
    if (
        counts.get("actor_lifecycle_binding") != 10
        or counts.get("actor_lifecycle_binding_admit") != 5
        or counts.get("actor_lifecycle_binding_reject") != 5
    ):
        fail("lifecycle fixture count closure drift")

    frontend_lifecycle = frontend["concurrency_frontend_contract"].get(
        "actor_minimum_lifecycle_contract", {}
    )
    if frontend_lifecycle.get("normal_stop_policy") != "DRAIN_ALL_COMMITTED_V1":
        fail("frontend normal stop policy drift")
    if frontend_lifecycle.get("defect_policy") != "STOP_AND_FAIL_PENDING_V1":
        fail("frontend Defect policy drift")
    if frontend_lifecycle.get("product_execution") != "NOT_RUN":
        fail("frontend product execution overclaim")

    trace = trace_contract.get("trace", {})
    diagnostic = trace.get("diagnostic", {})
    tooling = trace.get("tooling_and_debugger", {})
    acceptance = trace.get("acceptance_tests", {})
    exact_guards = {
        "ACTOR_LIFECYCLE_ADMISSION_AFTER_CLOSE",
        "ACTOR_LIFECYCLE_BINDING_FOREIGN_KEY_INVALID",
        "ACTOR_LIFECYCLE_DEFERRED_POLICY_ACTIVATED",
        "ACTOR_LIFECYCLE_HANDLER_AFTER_DEFECT",
        "ACTOR_LIFECYCLE_IDENTITY_INVALID",
        "ACTOR_LIFECYCLE_PAYLOAD_CLEANUP_CARDINALITY",
        "ACTOR_LIFECYCLE_PUBLICATION_BEFORE_COMMIT",
        "ACTOR_LIFECYCLE_REPLY_BINDING_INVALID",
        "ACTOR_LIFECYCLE_REPLY_TERMINAL_CARDINALITY",
        "ACTOR_LIFECYCLE_ROOT_OBSERVATION_INVALID",
        "ACTOR_LIFECYCLE_TERMINATION_BEFORE_CLEANUP",
        "ACTOR_LIFECYCLE_TRANSITION_INVALID",
    }
    if (
        trace_contract.get("feature_id") != "actor_minimum_lifecycle_r1"
        or trace_contract.get("gap_id") != "IR-ACTOR-P1-005"
        or trace_contract.get("semantic_change_from_r49") is not False
        or diagnostic.get("compiler_user_diagnostic_lane")
        != "NOT_APPLICABLE_INTERNAL_LIFECYCLE_EVIDENCE_INVARIANT"
        or diagnostic.get("canonical_diagnostic_registry_id_count") != 0
        or set(diagnostic.get("internal_verifier_guards", [])) != exact_guards
        or tooling.get("formatter_lsp")
        != "NOT_APPLICABLE_NO_NEW_SOURCE_SURFACE"
        or len(tooling.get("debugger_obligations", [])) != 3
        or tooling.get("product_execution") != "NOT_RUN"
        or acceptance.get("guard_coverage") != "12_OF_12"
        or acceptance.get("direct_fixture_count") != 5
        or acceptance.get("mutation_test_count") != 7
        or trace_contract.get("evidence_boundary", {}).get("product_lanes")
        != "15/15_NOT_RUN"
    ):
        fail("R51 end-to-end trace contract drift")

    direct = guard_matrix.get("direct_guards", [])
    mutations = guard_matrix.get("mutation_guards", [])
    matrix_acceptance = guard_matrix.get("machine_acceptance", {})
    matrix_guards = {
        row.get("expected_first_failure") for row in [*direct, *mutations]
    }
    if (
        guard_matrix.get("feature_id") != "actor_minimum_lifecycle_r1"
        or guard_matrix.get("gap_id") != "IR-ACTOR-P1-005"
        or len(direct) != 5
        or len(mutations) != 7
        or matrix_guards != exact_guards
        or len({row.get("test_id") for row in [*direct, *mutations]}) != 12
        or matrix_acceptance.get("uncovered_guard_count") != 0
        or matrix_acceptance.get("product_execution") != "NOT_RUN"
    ):
        fail("R51 lifecycle guard matrix drift")

    lifecycle_features = [
        row for row in feature_rows
        if row.get("feature_id") == "actor_minimum_lifecycle_r1"
    ]
    if len(lifecycle_features) != 1:
        fail("R51 lifecycle feature identity is not unique")
    feature = lifecycle_features[0]
    if (
        feature.get("status_enum") != "STABLE_DESIGN"
        or feature.get("depends_on")
        != [
            "actor_request_reply",
            "managed_reference_memory_profile_phase1",
            "internal_runtime_abi_r1",
        ]
        or feature.get("normative_trace_refs", {}).get("diagnostics")
        != ["ACTOR_SENDER_CONTEXT_UNAVAILABLE", "MIR_ACTOR_SENDER_IDENTITY_INVALID"]
        or feature.get("product_support") != "NOT_RUN"
        or "spec/contracts/actor-minimum-lifecycle-trace-r1.json"
        not in feature.get("artifact_trace_refs", [])
    ):
        fail("R51 lifecycle feature row drift")

    for marker in (
        "Frontend identity preservation",
        "Checker lifecycle plan",
        "MIR lowering",
        "xVM runtime",
        "Debugger projection",
        "Conformance execution",
        "R24 dependency hold is discharged",
    ):
        if marker not in handoff:
            fail(f"R51 implementation handoff missing {marker}")

    for text, label in ((language, "language"), (mir, "MIR")):
        for marker in (
            "ActorRuntimeRootOwnerId",
            "CREATION_ABORTED",
            "DRAIN_ALL_COMMITTED_V1",
            "STOP_AND_FAIL_PENDING_V1",
            "ActorMessageError::receiverClosedBeforeReply",
        ):
            if marker not in text:
                fail(f"{label} contract missing {marker}")

    print(
        "ACTOR_MINIMUM_LIFECYCLE_PASS: "
        "rules=22 fixtures=10 admit=5 reject=5 guards=12 trace=complete "
        "restart=0 interleaving=0 product=NOT_RUN"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
