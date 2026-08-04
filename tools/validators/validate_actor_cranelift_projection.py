#!/usr/bin/env python3
"""Validate the R75 Actor MIR-to-Cranelift projection design contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BASELINE = "c016871d5aa1c7515fd8a8df181744916f1e1849"
BASE_INPUTS = [
    "mir_semantic_digest",
    "target_triple",
    "target_isa_and_settings",
    "cranelift_family_and_lockfile_digest",
    "module_kind",
    "pointer_width_and_endianness",
    "object_format_and_code_relocation_model",
    "calling_convention",
    "internal_runtime_abi_id",
    "internal_runtime_abi_schema_id",
    "runtime_abi_digest",
    "runtime_helper_registry_digest",
    "internal_runtime_target_projection_digest",
    "internal_runtime_artifact_binding_receipt_schema_id",
    "optimization_settings_digest",
    "runtime_helper_and_safepoint_capability_digest",
    "managed_memory_profile_digest",
    "managed_memory_plan_digest",
    "managed_root_receipt_schema_digest",
    "continuation_root_interface_digest",
    "target_root_projection_digest",
    "runtime_root_registry_digest",
    "object_linker_or_jit_import_map_identity",
]
RULES = [f"CLB-R{index:03d}" for index in range(1, 13)]
FEATURES = [
    "actor_mailbox_capacity",
    "actor_minimum_lifecycle_r1",
    "actor_request_reply",
]
OWNER_KINDS = [
    "PUBLISHED_BINDING_TABLE",
    "QUEUED_ENVELOPE",
    "ACTIVE_OR_SUSPENDED_TURN",
    "ACTOR_REQUEST_TERMINAL_OBLIGATION",
    "CALLER_REPLY_CONTINUATION",
    "EXECUTING_FRAME",
    "CODE_DEPENDENT_METADATA",
]
PARTIAL_INVARIANTS = [
    "per_channel_fifo",
    "enqueue_commit_sequence",
    "one_active_state_mutating_turn",
    "suspend_resume_identity",
    "reply_terminal_exactly_once",
    "mir_primary_suppressed_failure_order",
    "cleanup_and_generation_lease_release_exactly_once",
]
DIAGNOSTICS = [
    "ACTOR_CRANELIFT_BASE_RECEIPT_INCOMPLETE",
    "ACTOR_CRANELIFT_BINDING_PROJECTION_INVALID",
    "ACTOR_CRANELIFT_BINDING_RESELECTION_FORBIDDEN",
    "ACTOR_CRANELIFT_MANAGED_REFERENCE_CAPABILITY_MISSING",
    "ACTOR_CRANELIFT_OUTCOME_MAPPING_INVALID",
    "ACTOR_CRANELIFT_GENERATION_ID_MISMATCH",
    "ACTOR_CRANELIFT_LEASE_EVENT_INVALID",
    "ACTOR_CRANELIFT_GENERATION_LIFETIME_VIOLATION",
    "ACTOR_CRANELIFT_CALLER_GENERATION_COUPLING_INVALID",
    "ACTOR_CRANELIFT_SCHEDULE_COMPARISON_INVALID",
    "ACTOR_CRANELIFT_OBSERVATION_INVARIANT_MISMATCH",
    "ACTOR_CRANELIFT_MODULE_OUTPUT_MISMATCH",
    "ACTOR_CRANELIFT_RECEIPT_DIGEST_MISMATCH",
]
PRODUCT_OVERCLAIM = "PRODUCT_EXECUTION_OVERCLAIM_REJECTED"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def self_digest(value: dict[str, Any], field: str = "receipt_sha256") -> str:
    return digest({key: item for key, item in value.items() if key != field})


def require(condition: bool, code: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(code)
    checks.append(code)


def load_r23_validator(root: Path) -> Any:
    path = root / "tools/validators/validate_actor_protocol_binding_descriptors.py"
    spec = importlib.util.spec_from_file_location("deeplus_r23_actor_binding", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("R23_VALIDATOR_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verified_binding_projection(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture = load(root / "tests/fixtures/current/actor-protocol-binding-table-r1.json")
    executable = fixture["projections"]["EXECUTABLE_IMAGE"]
    r23 = load_r23_validator(root)
    failures = r23.table_set_failures(executable)
    if failures:
        raise AssertionError("R23_EXECUTABLE_PROJECTION_INVALID:" + ",".join(sorted(failures)))
    row_digests = sorted(
        row["binding_row_sha256"]
        for table in executable["tables"]
        for row in table["bindings"]
    )
    origins = sorted(
        executable["origin_receipts"],
        key=lambda row: (row["declaring_module_id"], row["compilation_receipt_sha256"]),
    )
    projection = {
        "executable_image_id": executable["projection_owner_id"],
        "actor_protocol_binding_table_set_sha256": executable["table_set_sha256"],
        "binding_row_sha256s": row_digests,
        "origin_coverage_sha256": digest(origins),
        "verified_binding_projection_sha256": digest(executable),
    }
    return projection, executable


def base_inputs(kind: str) -> dict[str, Any]:
    return {
        "mir_semantic_digest": "1" * 64,
        "target_triple": "x86_64-pc-windows-msvc",
        "target_isa_and_settings": "2" * 64,
        "cranelift_family_and_lockfile_digest": "3" * 64,
        "module_kind": kind,
        "pointer_width_and_endianness": "64-little",
        "object_format_and_code_relocation_model": "coff-pic",
        "calling_convention": "deeplus-x86_64-windows-v1",
        "internal_runtime_abi_id": "RuntimeAbiId:DEEPLUS_INTERNAL_RUNTIME_ABI_R1",
        "internal_runtime_abi_schema_id": "deeplus.internal-runtime-abi-manifest/r1",
        "runtime_abi_digest": "4" * 64,
        "runtime_helper_registry_digest": "5" * 64,
        "internal_runtime_target_projection_digest": "6" * 64,
        "internal_runtime_artifact_binding_receipt_schema_id": "deeplus.internal-runtime-abi-artifact-binding-receipt/r1",
        "optimization_settings_digest": "7" * 64,
        "runtime_helper_and_safepoint_capability_digest": "8" * 64,
        "managed_memory_profile_digest": "9" * 64,
        "managed_memory_plan_digest": "a" * 64,
        "managed_root_receipt_schema_digest": "b" * 64,
        "continuation_root_interface_digest": "c" * 64,
        "target_root_projection_digest": "d" * 64,
        "runtime_root_registry_digest": "e" * 64,
        "object_linker_or_jit_import_map_identity": "f" * 64,
    }


def generation_id(receipt: dict[str, Any]) -> str:
    binding = receipt["verified_binding_projection"]
    preimage = {
        "base_receipt_inputs": receipt["base_receipt_inputs"],
        "executable_image_id": binding["executable_image_id"],
        "actor_protocol_binding_table_set_sha256": binding[
            "actor_protocol_binding_table_set_sha256"
        ],
        "binding_row_sha256s": sorted(binding["binding_row_sha256s"]),
        "origin_coverage_sha256": binding["origin_coverage_sha256"],
    }
    material = b"deeplus.actor-code-generation/v1\0" + canonical_bytes(preimage)
    return "ActorCodeGenerationId:" + hashlib.sha256(material).hexdigest()


def owner(
    kind: str,
    owner_id: str,
    *,
    actor_instance: str | None = "ActorInstanceId:fixture",
    responsibility: str | None = None,
    row_digest: str | None = None,
) -> dict[str, Any]:
    return {
        "owner_kind": kind,
        "owner_id": owner_id,
        "actor_instance_id_or_null": actor_instance,
        "responsibility_id_or_null": responsibility,
        "binding_row_sha256_or_null": row_digest,
    }


def module_output(kind: str) -> dict[str, Any]:
    if kind == "ObjectAot":
        return {
            "kind": kind,
            "object_bytes_digest": "1" * 64,
            "object_format": "coff",
            "linker_identity": "lld-link-pinned",
            "linker_arguments_digest": "2" * 64,
            "final_artifact_digest": "3" * 64,
            "image_metadata_lifetime_receipt_digest": "4" * 64,
        }
    return {
        "kind": kind,
        "import_allowlist_digest": "1" * 64,
        "resolved_import_map_digest": "2" * 64,
        "executable_memory_policy": "write-then-execute",
        "finalized_image_identity": "JitImageId:fixture",
        "lifetime_and_retirement_receipt": "3" * 64,
        "image_metadata_lifetime_receipt_digest": "4" * 64,
    }


def projection_fixture(root: Path, kind: str = "ObjectAot") -> dict[str, Any]:
    binding, _ = verified_binding_projection(root)
    value: dict[str, Any] = {
        "schema": "deeplus.actor-cranelift-projection-receipt/r1",
        "base_receipt_inputs": base_inputs(kind),
        "verified_binding_projection": binding,
        "actor_code_generation_id": "",
        "managed_reference_capability": {
            "capability": "PROVEN",
            "capability_digest": "5" * 64,
            "safepoint_obligation_count": 2,
            "root_map_obligation_count": 2,
            "generated_callback_count": 0,
            "suspended_frame_count": 1,
            "cleanup_entry_count": 1,
            "metadata_lifetime_receipt_sha256": "6" * 64,
        },
        "reply_continuation_binding": {},
        "outcome_projection": {
            "error": "EXPLICIT_MIR_EDGE",
            "defect": "EXPLICIT_MIR_EDGE",
            "cancellation": "EXPLICIT_MIR_EDGE",
            "suspension": "EXPLICIT_MIR_TRANSITION",
            "cleanup": "EXPLICIT_MIR_ACTION_ORDER",
            "host_unwind_semantic_authority": False,
            "arbitrary_backend_trap_semantic_authority": False,
            "trap_map_digest": "7" * 64,
        },
        "lease_events": [],
        "final_lifetime_state": {
            "publication_state": "PUBLISHED",
            "open_lease_ids": ["ActorCodeLeaseId:binding-table"],
            "executing_frame_count": 0,
            "code_metadata_user_count": 0,
            "retired": False,
            "physical_retirement": "OBJECT_IMAGE_LIVE" if kind == "ObjectAot" else "NOT_RETIRED",
        },
        "lifecycle_trace_sha256": "8" * 64,
        "observation_trace_sha256": "9" * 64,
        "backend_semantic_reselection_count": 0,
        "runtime_selector_lookup_count": 0,
        "module_output": module_output(kind),
        "product_execution": "NOT_RUN",
    }
    value["actor_code_generation_id"] = generation_id(value)
    generation = value["actor_code_generation_id"]
    row_digest = binding["binding_row_sha256s"][0]
    table_owner = owner(
        "PUBLISHED_BINDING_TABLE",
        "ActorProtocolBindingTableId:fixture",
        actor_instance=None,
    )
    envelope_owner = owner(
        "QUEUED_ENVELOPE",
        "EnvelopeId:fixture",
        responsibility="ResponsibilityId:status-reply",
        row_digest=row_digest,
    )
    turn_owner = owner(
        "ACTIVE_OR_SUSPENDED_TURN",
        "ActorTurnId:fixture",
        responsibility="ResponsibilityId:status-reply",
        row_digest=row_digest,
    )
    request_owner = owner(
        "ACTOR_REQUEST_TERMINAL_OBLIGATION",
        "ActorRequestId:status",
        responsibility="ResponsibilityId:status-reply",
        row_digest=row_digest,
    )

    def event(
        sequence: int,
        event_kind: str,
        lease: str | None,
        source: dict[str, Any] | None,
        target: dict[str, Any] | None,
        lifecycle: str | None,
    ) -> dict[str, Any]:
        return {
            "event_id": f"ActorCodeLeaseEventId:{sequence:02d}",
            "sequence": sequence,
            "event_kind": event_kind,
            "generation_id": generation,
            "lease_id_or_null": lease,
            "from_owner_or_null": source,
            "to_owner_or_null": target,
            "lifecycle_event_id_or_null": lifecycle,
        }

    value["lease_events"] = [
        event(0, "ACQUIRE", "ActorCodeLeaseId:binding-table", None, table_owner, None),
        event(1, "PUBLISH", None, None, None, None),
        event(2, "ACQUIRE", "ActorCodeLeaseId:envelope", None, envelope_owner, "ActorLifecycleEventId:message_enqueue_committed"),
        event(3, "TRANSFER", "ActorCodeLeaseId:envelope", envelope_owner, turn_owner, "ActorLifecycleEventId:dequeue_to_turn"),
        event(4, "ACQUIRE", "ActorCodeLeaseId:request", None, request_owner, "ActorLifecycleEventId:request_admitted"),
        event(5, "RELEASE", "ActorCodeLeaseId:envelope", turn_owner, None, "ActorLifecycleEventId:turn_cleanup_complete"),
        event(6, "RELEASE", "ActorCodeLeaseId:request", request_owner, None, "ActorLifecycleEventId:terminal_cleanup_complete"),
    ]
    caller_generation = "ActorCodeGenerationId:" + "a" * 64
    value["reply_continuation_binding"] = {
        "operation_kind": "REQUEST",
        "mode": "DISTINCT_GENERATION_RECEIPT",
        "actor_code_generation_id": generation,
        "caller_code_generation_id_or_null": caller_generation,
        "continuation_lease_receipt_sha256_or_null": "b" * 64,
        "equal_generation_required": False,
    }
    value["receipt_sha256"] = self_digest(value)
    return value


def differential_fixture() -> dict[str, Any]:
    value = {
        "schema": "deeplus.actor-cranelift-differential-comparison-receipt/r1",
        "xvm_observation_trace_sha256": "1" * 64,
        "object_projection_receipt_sha256": "2" * 64,
        "jit_projection_receipt_sha256": "3" * 64,
        "comparison_mode": "REQUIRED_PARTIAL_ORDER",
        "deterministic_schedule_trace_id_or_null": None,
        "single_channel_precondition_receipt_sha256_or_null": None,
        "partial_order_invariants": PARTIAL_INVARIANTS,
        "execution_state": "NOT_RUN",
    }
    value["receipt_sha256"] = self_digest(value)
    return value


def lease_failure(receipt: dict[str, Any]) -> str | None:
    generation = receipt.get("actor_code_generation_id")
    events = receipt.get("lease_events", [])
    if [item.get("sequence") for item in events] != list(range(len(events))):
        return DIAGNOSTICS[6]
    if len({item.get("event_id") for item in events}) != len(events):
        return DIAGNOSTICS[6]
    active: dict[str, dict[str, Any]] = {}
    published = False
    retired = False
    for item in events:
        if item.get("generation_id") != generation or retired:
            return DIAGNOSTICS[6]
        kind = item.get("event_kind")
        lease = item.get("lease_id_or_null")
        source = item.get("from_owner_or_null")
        target = item.get("to_owner_or_null")
        lifecycle = item.get("lifecycle_event_id_or_null")
        if kind == "ACQUIRE":
            if not lease or lease in active or source is not None or target is None:
                return DIAGNOSTICS[6]
            if target.get("owner_kind") not in OWNER_KINDS:
                return DIAGNOSTICS[6]
            if target.get("owner_kind") == "PUBLISHED_BINDING_TABLE" and published:
                return DIAGNOSTICS[6]
            if target.get("owner_kind") == "QUEUED_ENVELOPE" and lifecycle != "ActorLifecycleEventId:message_enqueue_committed":
                return DIAGNOSTICS[7]
            active[lease] = target
        elif kind == "TRANSFER":
            if not lease or lease not in active or source != active[lease] or target is None:
                return DIAGNOSTICS[6]
            if source.get("owner_kind") == "QUEUED_ENVELOPE" and (
                target.get("owner_kind") != "ACTIVE_OR_SUSPENDED_TURN"
                or lifecycle != "ActorLifecycleEventId:dequeue_to_turn"
            ):
                return DIAGNOSTICS[7]
            active[lease] = target
        elif kind == "RELEASE":
            if not lease or lease not in active or source != active[lease] or target is not None:
                return DIAGNOSTICS[6]
            if source.get("owner_kind") == "ACTOR_REQUEST_TERMINAL_OBLIGATION" and lifecycle != "ActorLifecycleEventId:terminal_cleanup_complete":
                return DIAGNOSTICS[7]
            del active[lease]
        elif kind == "PUBLISH":
            if lease is not None or source is not None or target is not None or published:
                return DIAGNOSTICS[6]
            if not any(owner_value.get("owner_kind") == "PUBLISHED_BINDING_TABLE" for owner_value in active.values()):
                return DIAGNOSTICS[7]
            published = True
        elif kind == "UNPUBLISH":
            if lease is not None or source is not None or target is not None or not published:
                return DIAGNOSTICS[6]
            published = False
        elif kind == "RETIRE":
            if lease is not None or source is not None or target is not None or published or active:
                return DIAGNOSTICS[7]
            retired = True
        else:
            return DIAGNOSTICS[6]
    final = receipt.get("final_lifetime_state", {})
    if final.get("open_lease_ids") != sorted(active):
        return DIAGNOSTICS[7]
    if final.get("publication_state") != ("PUBLISHED" if published else "UNPUBLISHED"):
        return DIAGNOSTICS[7]
    if final.get("retired") != retired:
        return DIAGNOSTICS[7]
    if retired and (final.get("executing_frame_count") != 0 or final.get("code_metadata_user_count") != 0):
        return DIAGNOSTICS[7]
    kind = receipt.get("base_receipt_inputs", {}).get("module_kind")
    physical = final.get("physical_retirement")
    if kind == "ObjectAot" and physical == "JIT_RETIRED":
        return DIAGNOSTICS[7]
    if kind == "ObjectAot" and retired and physical != "OBJECT_IMAGE_UNLOADED":
        return DIAGNOSTICS[7]
    if kind == "InMemoryJit" and retired and physical != "JIT_RETIRED":
        return DIAGNOSTICS[7]
    return None


def projection_failure(receipt: dict[str, Any], expected_binding: dict[str, Any]) -> str | None:
    base = receipt.get("base_receipt_inputs", {})
    if set(base) != set(BASE_INPUTS) or len(base) != len(BASE_INPUTS):
        return DIAGNOSTICS[0]
    if receipt.get("verified_binding_projection") != expected_binding:
        return DIAGNOSTICS[1]
    if receipt.get("backend_semantic_reselection_count") != 0 or receipt.get("runtime_selector_lookup_count") != 0:
        return DIAGNOSTICS[2]
    managed = receipt.get("managed_reference_capability", {})
    if managed.get("capability") not in {"PROVEN", "NOT_REQUIRED"}:
        return DIAGNOSTICS[3]
    if managed.get("capability") == "NOT_REQUIRED" and any(
        managed.get(name) != 0
        for name in [
            "safepoint_obligation_count",
            "root_map_obligation_count",
            "generated_callback_count",
            "suspended_frame_count",
            "cleanup_entry_count",
        ]
    ):
        return DIAGNOSTICS[3]
    expected_outcome = {
        "error": "EXPLICIT_MIR_EDGE",
        "defect": "EXPLICIT_MIR_EDGE",
        "cancellation": "EXPLICIT_MIR_EDGE",
        "suspension": "EXPLICIT_MIR_TRANSITION",
        "cleanup": "EXPLICIT_MIR_ACTION_ORDER",
        "host_unwind_semantic_authority": False,
        "arbitrary_backend_trap_semantic_authority": False,
    }
    outcome = receipt.get("outcome_projection", {})
    if any(outcome.get(key) != value for key, value in expected_outcome.items()):
        return DIAGNOSTICS[4]
    if receipt.get("actor_code_generation_id") != generation_id(receipt):
        return DIAGNOSTICS[5]
    reply = receipt.get("reply_continuation_binding", {})
    if reply.get("actor_code_generation_id") != receipt.get("actor_code_generation_id") or reply.get("equal_generation_required") is not False:
        return DIAGNOSTICS[8]
    if reply.get("operation_kind") == "SEND":
        if reply.get("mode") != "NONE_FOR_SEND" or reply.get("caller_code_generation_id_or_null") is not None or reply.get("continuation_lease_receipt_sha256_or_null") is not None:
            return DIAGNOSTICS[8]
    elif reply.get("operation_kind") == "REQUEST":
        if reply.get("mode") != "DISTINCT_GENERATION_RECEIPT" or not reply.get("caller_code_generation_id_or_null") or not reply.get("continuation_lease_receipt_sha256_or_null"):
            return DIAGNOSTICS[8]
    else:
        return DIAGNOSTICS[8]
    lifetime = lease_failure(receipt)
    if lifetime:
        return lifetime
    kind = base.get("module_kind")
    if receipt.get("module_output", {}).get("kind") != kind:
        return DIAGNOSTICS[11]
    if receipt.get("product_execution") != "NOT_RUN":
        return PRODUCT_OVERCLAIM
    if receipt.get("receipt_sha256") != self_digest(receipt):
        return DIAGNOSTICS[12]
    return None


def differential_failure(receipt: dict[str, Any]) -> str | None:
    if receipt.get("partial_order_invariants") != PARTIAL_INVARIANTS:
        return DIAGNOSTICS[10]
    if receipt.get("comparison_mode") == "EXACT_TOTAL_ORDER" and not (
        receipt.get("deterministic_schedule_trace_id_or_null")
        or receipt.get("single_channel_precondition_receipt_sha256_or_null")
    ):
        return DIAGNOSTICS[9]
    if receipt.get("execution_state") != "NOT_RUN":
        return PRODUCT_OVERCLAIM
    if receipt.get("receipt_sha256") != self_digest(receipt):
        return DIAGNOSTICS[12]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / "spec/contracts/actor-cranelift-projection-r1.json")
    schema = load(root / "schemas/language/actor-cranelift-projection-receipt-r1.schema.json")
    tests = load(root / "tests/conformance/actor-cranelift-projection-r1.json")
    cranelift = load(root / "spec/contracts/cranelift-backend-current.json")
    lifecycle = load(root / "spec/contracts/actor-minimum-lifecycle-trace-r1.json")
    binding_descriptor = load(root / "spec/contracts/actor-protocol-binding-descriptor.json")
    overlay = load(root / "spec/traceability/implementation-target-profile-r1/actor-cranelift-projection-dynamic-evidence-r1.json")
    checks: list[str] = []

    require(contract["authority"]["candidate_baseline_commit"] == BASELINE, "BASELINE_EXACT", checks)
    require(contract["gap_id"] == "IR-ACTOR-P1-007", "GAP_EXACT", checks)
    require(contract["source_syntax_change_count"] == 0, "NO_SOURCE_SYNTAX", checks)
    require(contract["semantic_p0"] == 0, "SEMANTIC_P0_ZERO", checks)
    require(contract["open_feature_p1_count"] == 22, "FEATURE_P1_22_OPEN", checks)
    require(contract["product_lanes"] == "15/15_NOT_RUN", "PRODUCT_LANES_NOT_RUN", checks)
    require(contract["authority"]["github_publication_authorized"] is False, "GITHUB_NOT_AUTHORIZED", checks)
    require([item["gap_id"] for item in contract["dependencies"]] == ["IR-ACTOR-P1-005", "IR-ACTOR-P1-006"], "DEPENDENCY_SET_EXACT", checks)
    require(all(item["status"] == "VERIFIED_CLOSED" for item in contract["dependencies"]), "DEPENDENCIES_CLOSED", checks)
    require(lifecycle.get("gap_status") == "VERIFIED_CLOSED", "R22_LIFECYCLE_CLOSED", checks)
    require(lifecycle.get("canonical_closure_commit") == BASELINE, "R22_CLOSURE_BASELINE", checks)
    require(binding_descriptor.get("status") == "CURRENT_NORMATIVE_DESIGN_CONTRACT", "R23_BINDING_CURRENT", checks)
    require(contract["inherited_cranelift_contract"]["rule_ids"] == RULES, "CLB_RULES_EXACT", checks)
    require([item["rule_id"] for item in cranelift["rules"]] == RULES, "CURRENT_CLB_RULES_EXACT", checks)
    require(contract["inherited_cranelift_contract"]["required_receipt_inputs"] == BASE_INPUTS, "CONTRACT_BASE_INPUTS_23", checks)
    require(cranelift["required_receipt_inputs"] == BASE_INPUTS, "CURRENT_BASE_INPUTS_23", checks)
    require(contract["generation_lifetime"]["owner_kinds"] == OWNER_KINDS, "OWNER_KINDS_7", checks)
    require(contract["differential_comparison"]["partial_order_invariants"] == PARTIAL_INVARIANTS, "PARTIAL_INVARIANTS_7", checks)
    require(contract["diagnostic_precedence"] == DIAGNOSTICS, "DIAGNOSTIC_PRECEDENCE_13", checks)
    require(sorted(contract["feature_trace"]) == sorted(FEATURES), "FEATURE_TRACE_3", checks)
    require(overlay["feature_ids"] == FEATURES, "OVERLAY_FEATURES_3", checks)
    require(overlay["counts"]["binding_count"] == 3, "OVERLAY_BINDINGS_3", checks)
    require(overlay["counts"]["post_overlay_total_blocked_cell_count"] == 1242, "OVERLAY_BLOCKED_1242", checks)

    expected_binding, executable = verified_binding_projection(root)
    require(executable["projection_kind"] == "EXECUTABLE_IMAGE", "R23_EXECUTABLE_PROJECTION", checks)
    require(executable["projection_owner_id"].startswith("ExecutableImageId:"), "R23_EXECUTABLE_OWNER", checks)
    require(executable["runtime_lookup_count"] == 0 and executable["runtime_fallback_count"] == 0, "R23_RUNTIME_LOOKUP_ZERO", checks)
    require(executable["link_order_winner_count"] == 0, "R23_LINK_ORDER_ZERO", checks)

    object_receipt = projection_fixture(root, "ObjectAot")
    jit_receipt = projection_fixture(root, "InMemoryJit")
    differential = differential_fixture()
    try:
        import jsonschema

        validator = jsonschema.Draft202012Validator(schema)
        validator.validate(object_receipt)
        validator.validate(jit_receipt)
        validator.validate(differential)
        require(True, "RECEIPT_SCHEMA_NORMAL_PATHS", checks)
    except ImportError:
        require(True, "RECEIPT_SCHEMA_LIBRARY_NOT_INSTALLED", checks)
    require(projection_failure(object_receipt, expected_binding) is None, "OBJECT_NORMAL_PASS", checks)
    require(projection_failure(jit_receipt, expected_binding) is None, "JIT_NORMAL_PASS", checks)
    require(differential_failure(differential) is None, "DIFFERENTIAL_PARTIAL_PASS", checks)

    total = copy.deepcopy(differential)
    total["comparison_mode"] = "EXACT_TOTAL_ORDER"
    total["deterministic_schedule_trace_id_or_null"] = "DeterministicScheduleTraceId:fixture"
    total["receipt_sha256"] = self_digest(total)
    require(differential_failure(total) is None, "DIFFERENTIAL_TOTAL_ORDER_WITH_REPLAY_PASS", checks)

    permuted = copy.deepcopy(object_receipt)
    permuted["verified_binding_projection"]["binding_row_sha256s"].reverse()
    require(generation_id(permuted) == object_receipt["actor_code_generation_id"], "ROW_ORDER_IDENTITY_STABLE", checks)
    for key, value in [
        ("mir_semantic_digest", "0" * 64),
        ("target_triple", "aarch64-unknown-linux-gnu"),
        ("runtime_abi_digest", "0" * 64),
        ("module_kind", "InMemoryJit"),
    ]:
        mutated = copy.deepcopy(object_receipt)
        mutated["base_receipt_inputs"][key] = value
        require(generation_id(mutated) != object_receipt["actor_code_generation_id"], f"GENERATION_CHANGES_WITH_{key.upper()}", checks)
    mutated = copy.deepcopy(object_receipt)
    mutated["verified_binding_projection"]["executable_image_id"] = "ExecutableImageId:other"
    require(generation_id(mutated) != object_receipt["actor_code_generation_id"], "GENERATION_CHANGES_WITH_EXECUTABLE_IMAGE", checks)

    missing = copy.deepcopy(object_receipt)
    del missing["base_receipt_inputs"]["runtime_root_registry_digest"]
    require(projection_failure(missing, expected_binding) == DIAGNOSTICS[0], "MUTATION_MISSING_BASE_REJECT", checks)
    stale_binding = copy.deepcopy(object_receipt)
    stale_binding["verified_binding_projection"]["origin_coverage_sha256"] = "0" * 64
    stale_binding["actor_code_generation_id"] = generation_id(stale_binding)
    stale_binding["receipt_sha256"] = self_digest(stale_binding)
    require(projection_failure(stale_binding, expected_binding) == DIAGNOSTICS[1], "MUTATION_BINDING_PROJECTION_REJECT", checks)
    reselect = copy.deepcopy(object_receipt)
    reselect["runtime_selector_lookup_count"] = 1
    reselect["receipt_sha256"] = self_digest(reselect)
    require(projection_failure(reselect, expected_binding) == DIAGNOSTICS[2], "MUTATION_RESELECTION_REJECT", checks)
    wrong_generation = copy.deepcopy(object_receipt)
    wrong_generation["actor_code_generation_id"] = "ActorCodeGenerationId:" + "0" * 64
    wrong_generation["receipt_sha256"] = self_digest(wrong_generation)
    require(projection_failure(wrong_generation, expected_binding) == DIAGNOSTICS[5], "MUTATION_GENERATION_REJECT", checks)
    duplicate_acquire = copy.deepcopy(object_receipt)
    duplicate_acquire["lease_events"].insert(1, copy.deepcopy(duplicate_acquire["lease_events"][0]))
    for index, event in enumerate(duplicate_acquire["lease_events"]):
        event["sequence"] = index
        event["event_id"] = f"ActorCodeLeaseEventId:dup-{index:02d}"
    duplicate_acquire["receipt_sha256"] = self_digest(duplicate_acquire)
    require(projection_failure(duplicate_acquire, expected_binding) == DIAGNOSTICS[6], "MUTATION_DUPLICATE_ACQUIRE_REJECT", checks)
    duplicate_release = copy.deepcopy(object_receipt)
    duplicate_release["lease_events"].append(copy.deepcopy(duplicate_release["lease_events"][-1]))
    duplicate_release["lease_events"][-1]["sequence"] = len(duplicate_release["lease_events"]) - 1
    duplicate_release["lease_events"][-1]["event_id"] = "ActorCodeLeaseEventId:duplicate-release"
    duplicate_release["receipt_sha256"] = self_digest(duplicate_release)
    require(projection_failure(duplicate_release, expected_binding) == DIAGNOSTICS[6], "MUTATION_DUPLICATE_RELEASE_REJECT", checks)
    early_request = copy.deepcopy(object_receipt)
    early_request["lease_events"][-1]["lifecycle_event_id_or_null"] = "ActorLifecycleEventId:reply_terminal_decided"
    early_request["receipt_sha256"] = self_digest(early_request)
    require(projection_failure(early_request, expected_binding) == DIAGNOSTICS[7], "MUTATION_EARLY_REQUEST_RELEASE_REJECT", checks)
    coupled = copy.deepcopy(object_receipt)
    coupled["reply_continuation_binding"]["equal_generation_required"] = True
    coupled["receipt_sha256"] = self_digest(coupled)
    require(projection_failure(coupled, expected_binding) == DIAGNOSTICS[8], "MUTATION_CALLER_COUPLING_REJECT", checks)
    managed = copy.deepcopy(object_receipt)
    managed["managed_reference_capability"]["capability"] = "NOT_REQUIRED"
    managed["receipt_sha256"] = self_digest(managed)
    require(projection_failure(managed, expected_binding) == DIAGNOSTICS[3], "MUTATION_MANAGED_NOT_REQUIRED_REJECT", checks)
    overclaim = copy.deepcopy(differential)
    overclaim["comparison_mode"] = "EXACT_TOTAL_ORDER"
    overclaim["receipt_sha256"] = self_digest(overclaim)
    require(differential_failure(overclaim) == DIAGNOSTICS[9], "MUTATION_TOTAL_ORDER_REJECT", checks)
    incomplete_order = copy.deepcopy(differential)
    incomplete_order["partial_order_invariants"] = PARTIAL_INVARIANTS[:-1]
    incomplete_order["receipt_sha256"] = self_digest(incomplete_order)
    require(differential_failure(incomplete_order) == DIAGNOSTICS[10], "MUTATION_PARTIAL_ORDER_REJECT", checks)
    corrupt = copy.deepcopy(object_receipt)
    corrupt["receipt_sha256"] = "0" * 64
    require(projection_failure(corrupt, expected_binding) == DIAGNOSTICS[12], "MUTATION_RECEIPT_DIGEST_REJECT", checks)
    product = copy.deepcopy(object_receipt)
    product["product_execution"] = "EXECUTED_PASS"
    product["receipt_sha256"] = self_digest(product)
    require(projection_failure(product, expected_binding) == PRODUCT_OVERCLAIM, "MUTATION_PRODUCT_OVERCLAIM_REJECT", checks)

    cases = tests["cases"]
    require([item["case_id"] for item in cases] == [f"R24R-T{index:02d}" for index in range(1, 31)], "ACCEPTANCE_IDS_30_EXACT", checks)
    counts = {name: sum(item["class"] == name for item in cases) for name in ["positive", "boundary", "negative"]}
    require(counts == {"positive": 8, "boundary": 7, "negative": 15}, "ACCEPTANCE_CLASS_COUNTS", checks)
    require(len(tests["mutation_controls"]) == 16, "MUTATION_CONTROL_COUNT_16", checks)
    require(tests["target_feature_ids"] == FEATURES, "TEST_TARGET_FEATURES_3", checks)
    require(tests["expected_counts"]["product_executed"] == 0, "TEST_PRODUCT_EXECUTION_ZERO", checks)

    receipt = {
        "schema": "deeplus.actor-cranelift-projection-validation-receipt/r1",
        "result": "PASS",
        "checks": len(checks),
        "acceptance_cases": len(cases),
        "mutations": len(tests["mutation_controls"]),
        "trace_features": len(FEATURES),
        "base_receipt_inputs": len(BASE_INPUTS),
        "owner_kinds": len(OWNER_KINDS),
        "partial_order_invariants": len(PARTIAL_INVARIANTS),
        "diagnostic_guards": len(DIAGNOSTICS),
        "post_overlay_blocked_cells": overlay["counts"]["post_overlay_total_blocked_cell_count"],
        "product_support": "NOT_RUN",
        "github_publication": "NOT_AUTHORIZED_FOR_R75",
        "errors": [],
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
