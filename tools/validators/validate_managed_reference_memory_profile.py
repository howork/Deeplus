#!/usr/bin/env python3
"""Validate the R36 managed-reference Phase-1 memory design contract.

This validator is design-static. It does not execute a Deeplus frontend,
collector, xVM, Cranelift backend, FFI boundary, formatter or LSP.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE = "e680568057ec9c6b02218dbe153758471734cf44"
BASELINE_TREE = "4d91b75d244f0c6adb5980cee19fec756c337053"
CONTINUATION_INTERFACE_ID = "ContinuationInterfaceId:DEEPLUS_CONTINUATION_INTERFACE_R1"
CONTINUATION_INTERFACE_DIGEST = "0dc4891d1d23da397012f1ec1956ba1a3b52e884dbec604d27c8561a09941271"
PROFILE_ID = "STW_NONMOVING_TRACING_WITH_OPAQUE_STABLE_HANDLES_R1"
FEATURE_ID = "managed_reference_memory_profile_phase1"
CONTRACT_PATH = "spec/contracts/managed-reference-memory-profile-r1.json"
PLAN_SCHEMA_PATH = "schemas/language/managed-reference-memory-profile-r1.schema.json"
NATIVE_RECEIPT_SCHEMA_PATH = (
    "schemas/language/managed-reference-native-projection-receipt-r1.schema.json"
)
FIXTURE_SCHEMA_PATH = (
    "schemas/language/managed-reference-memory-profile-fixtures-r1.schema.json"
)
FIXTURE_PATH = "tests/fixtures/current/managed-reference-memory-profile-r1.json"

CLOSED_SITE_KINDS = [
    "NONTAIL_INVOKE",
    "MANAGED_ALLOCATION_SLOW_PATH",
    "SUSPENSION_AFTER_ROOT_TRANSFER",
    "CANCELLATION_OBSERVATION",
    "RUN_RUNTIME_ENTRY",
    "ACTOR_RUNTIME_ENTRY",
    "PROVIDER_RUNTIME_ENTRY",
    "ONCE_RUNTIME_ENTRY",
    "SYNC_RUNTIME_ENTRY",
    "CFG_BACKEDGE",
    "FFI_TRANSITION",
]
SITE_TERMINATORS = {
    "NONTAIL_INVOKE": "INVOKE",
    "MANAGED_ALLOCATION_SLOW_PATH": "CHECKED",
    "SUSPENSION_AFTER_ROOT_TRANSFER": "SUSPEND",
    "CANCELLATION_OBSERVATION": "CANCEL_CHECK",
    "RUN_RUNTIME_ENTRY": "RUN_OP",
    "ACTOR_RUNTIME_ENTRY": "ACTOR_OP",
    "PROVIDER_RUNTIME_ENTRY": "PROVIDER_OP",
    "ONCE_RUNTIME_ENTRY": "ONCE_OP",
    "SYNC_RUNTIME_ENTRY": "SYNC_OP",
    "CFG_BACKEDGE": "BR_OR_COND_BR_BACKEDGE",
    "FFI_TRANSITION": "INVOKE_WITH_FOREIGN_CONTRACT",
}
PROJECTION_DIAGNOSTICS = [
    "RAW_POINTER_PROVENANCE_ACROSS_SAFEPOINT",
    "MANAGED_REFERENCE_SAFEPOINT_SET_INVALID",
    "MANAGED_REFERENCE_ROOT_SET_INVALID",
    "MANAGED_REFERENCE_ROOT_RECEIPT_DIGEST_MISMATCH",
    "MANAGED_REFERENCE_SAFEPOINT_ORDER_INVALID",
    "MANAGED_REFERENCE_JIT_RETIREMENT_LEASE_VIOLATION",
    "MANAGED_REFERENCE_PROJECTION_PARITY_MISMATCH",
]
REQUIRED_NATIVE_RECEIPT_FIELDS = [
    "managed_memory_profile_digest",
    "managed_memory_plan_digest",
    "continuation_root_interface_digest",
    "handle_abi_digest",
    "shadow_root_frame_abi_digest",
    "safepoint_projection_digest",
    "target_root_projection_digest",
    "runtime_root_registry_digest",
    "runtime_abi_digest",
    "image_metadata_lifetime_receipt_digest",
    "semantic_parity_trace_digest",
    "receipt_semantic_digest",
]
EXPECTED_MUTATIONS = [
    "DROP_ROOT",
    "ADD_STALE_ROOT",
    "DUPLICATE_ROOT",
    "REVERSE_ROOT_ORDER",
    "CORRUPT_ROOT_DIGEST",
    "CHANGE_SAFEPOINT_ID_WITHOUT_DIGEST",
    "REMOVE_SAFEPOINT_DECLARATION",
    "ENABLE_COLLECTING_FAST_PATH",
    "EXTEND_INTERIOR_POINTER_ACROSS_SAFEPOINT",
    "PUBLISH_RECEIPT_AFTER_ENTRY",
    "ENABLE_RELOCATION",
    "ENABLE_CONCURRENT_OR_GENERATIONAL_COLLECTION",
    "ENABLE_WEAK_REFERENCE",
    "ENABLE_USER_FINALIZER",
    "RETIRE_JIT_WITH_SUSPENDED_LEASE",
    "CHANGE_TARGET_SEMANTIC_TRACE_OR_CLAIM_PRODUCT_PASS",
    "EXTEND_INTERIOR_POINTER_ACROSS_CALL",
    "EXTEND_INTERIOR_POINTER_ACROSS_SUSPENSION",
    "EXTEND_INTERIOR_POINTER_ACROSS_ACTOR_BOUNDARY",
    "DROP_CONTINUATION_INTERFACE_BINDING",
]


class ValidationFailure(RuntimeError):
    pass


def read_json(root: Path, relative: str) -> Any:
    path = root / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationFailure(f"JSON_PARSE:{relative}:{exc}") from exc


def catalog_rows(root: Path, pattern: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(root.glob(pattern), key=lambda item: item.as_posix()):
        value = read_json(root, path.relative_to(root).as_posix())
        if not isinstance(value, list):
            raise ValidationFailure(f"CATALOG_SHAPE:{path.relative_to(root)}")
        result.extend(row for row in value if isinstance(row, dict))
    return result


def unique_row(
    rows: list[dict[str, Any]], key: str, value: str, failure: str
) -> dict[str, Any]:
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise ValidationFailure(f"{failure}:{value}:count={len(matches)}")
    return matches[0]


def reject(diagnostic: str) -> dict[str, Any]:
    return {"verdict": "REJECT_STATIC", "diagnostic_id_or_null": diagnostic}


def admit() -> dict[str, Any]:
    return {"verdict": "ADMIT_STATIC", "diagnostic_id_or_null": None}


def evaluate(facts: dict[str, Any]) -> dict[str, Any]:
    if (
        facts.get("moving_collector", False)
        or facts.get("concurrent_collector", False)
        or facts.get("generational_collector", False)
        or facts.get("weak_reference_count", 0) != 0
        or facts.get("user_finalizer_count", 0) != 0
    ):
        return reject("HIR_MIR_CAPABILITY_RECEIPT_MISMATCH")

    site_kind = facts.get("site_kind")
    if site_kind is not None:
        if site_kind not in CLOSED_SITE_KINDS:
            return reject("MANAGED_REFERENCE_SAFEPOINT_SET_INVALID")
        if facts.get("safepoint_declared", True) is not True:
            return reject("MANAGED_REFERENCE_SAFEPOINT_SET_INVALID")
        terminator = facts.get("terminator_kind")
        expected = SITE_TERMINATORS[site_kind]
        valid = (
            terminator == expected
            or (site_kind == "CFG_BACKEDGE" and terminator in {"BR", "COND_BR"})
            or (site_kind == "FFI_TRANSITION" and terminator == "INVOKE")
        )
        if not valid:
            return reject("MANAGED_REFERENCE_SAFEPOINT_SET_INVALID")
    if facts.get("allocation_fast_path_may_collect", False):
        return reject("MANAGED_REFERENCE_SAFEPOINT_SET_INVALID")

    root_fields_present = any(
        name in facts
        for name in (
            "running_root_ids",
            "frame_root_ids",
            "runtime_root_ids",
            "declared_root_ids",
            "entry_root_ids",
        )
    )
    if root_fields_present:
        partitions = [
            list(facts.get("running_root_ids", [])),
            list(facts.get("frame_root_ids", [])),
            list(facts.get("runtime_root_ids", [])),
        ]
        flattened = [root for part in partitions for root in part]
        declared = list(facts.get("declared_root_ids", []))
        entries = list(facts.get("entry_root_ids", []))
        exact = sorted(set(flattened))
        if (
            len(flattened) != len(set(flattened))
            or declared != exact
            or len(declared) != len(set(declared))
            or entries != declared
            or len(entries) != len(set(entries))
        ):
            return reject("MANAGED_REFERENCE_ROOT_SET_INVALID")
        if facts.get("root_set_digest_valid", True) is not True:
            return reject("MANAGED_REFERENCE_ROOT_RECEIPT_DIGEST_MISMATCH")

    if facts.get("root_set_digest_valid", True) is not True:
        return reject("MANAGED_REFERENCE_ROOT_RECEIPT_DIGEST_MISMATCH")
    if (
        facts.get("receipt_published_before_entry", True) is not True
        or facts.get("receipt_live_through_outcome", True) is not True
    ):
        return reject("MANAGED_REFERENCE_SAFEPOINT_ORDER_INVALID")
    if facts.get("transfer_count", 1) != 1 or facts.get(
        "source_residual_count", 0
    ) != 0:
        return reject("MANAGED_REFERENCE_SAFEPOINT_ORDER_INVALID")
    transfer_fields = (
        "source_root_id",
        "destination_root_id",
        "source_handle_generation",
        "destination_handle_generation",
    )
    if any(name in facts for name in transfer_fields):
        if not all(name in facts for name in transfer_fields):
            return reject("MANAGED_REFERENCE_ROOT_SET_INVALID")
        if facts["source_root_id"] == facts["destination_root_id"]:
            return reject("MANAGED_REFERENCE_ROOT_SET_INVALID")
        if facts["source_handle_generation"] != facts["destination_handle_generation"]:
            return reject("MANAGED_REFERENCE_ROOT_SET_INVALID")
    if any(
        facts.get(name, False)
        for name in (
            "raw_interior_crosses_safepoint",
            "raw_interior_crosses_call",
            "raw_interior_crosses_suspension",
            "raw_interior_crosses_actor_boundary",
            "raw_interior_crosses_ffi",
        )
    ):
        return reject("RAW_POINTER_PROVENANCE_ACROSS_SAFEPOINT")
    if facts.get("continuation_interface_bound", True) is not True:
        return reject("HIR_MIR_CAPABILITY_RECEIPT_MISMATCH")

    if facts.get("retirement_requested", False):
        counters = (
            facts.get("active_native_activation_count", 0),
            facts.get("suspended_continuation_count", 0),
            facts.get("outstanding_root_receipt_count", 0),
        )
        if facts.get("jit_state") != "UNPUBLISHED" or any(counters):
            return reject("MANAGED_REFERENCE_JIT_RETIREMENT_LEASE_VIOLATION")
    if facts.get("cross_path_parity", True) is not True:
        return reject("MANAGED_REFERENCE_PROJECTION_PARITY_MISMATCH")
    if facts.get("product_execution", "NOT_RUN") != "NOT_RUN":
        return reject("PRODUCT_SUPPORT_OVERCLAIM")
    return admit()


def validate_schema(
    plan_schema: dict[str, Any],
    native_receipt_schema: dict[str, Any],
    fixture_schema: dict[str, Any],
    fixture: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    try:
        from jsonschema import Draft202012Validator

        Draft202012Validator.check_schema(plan_schema)
        Draft202012Validator.check_schema(native_receipt_schema)
        Draft202012Validator.check_schema(fixture_schema)
        root_entry_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": plan_schema["$defs"],
            "$ref": "#/$defs/rootEntry",
        }
        root_entry_validator = Draft202012Validator(root_entry_schema)
        base_root_entry = {
            "root_id": "RootId:r",
            "partition": "RUNNING",
            "owner_kind": "ACTIVE_FRAME",
            "owner_id": "ActiveFrameId:f",
            "storage_kind": "VALUE",
            "storage_id": "ValueId:v",
            "trace_descriptor_id": "ManagedTraceDescriptorId:t",
            "handle_generation": 7,
        }
        if list(root_entry_validator.iter_errors(base_root_entry)):
            errors.append("ROOT_ENTRY_TYPED_DOMAIN_POSITIVE")
        owner_mutants = {
            "ACTIVE_FRAME": "ContinuationFrameId:f",
            "SUSPENDED_FRAME": "ActiveFrameId:f",
            "CLEANUP_CAPTURE": "RuntimeOwnerId:f",
            "PENDING_OUTCOME": "RunStateId:f",
            "CLOSURE_ENVIRONMENT": "ActorEnvelopeId:f",
            "ACTOR_ENVELOPE": "ClosureEnvironmentId:f",
            "RUN_STATE": "ReplyStateId:f",
            "REPLY_STATE": "RunStateId:f",
            "RUNTIME_OWNER": "PendingOutcomeId:f",
        }
        for owner_kind, wrong_owner_id in owner_mutants.items():
            mutant = copy.deepcopy(base_root_entry)
            mutant["owner_kind"] = owner_kind
            mutant["owner_id"] = wrong_owner_id
            if not list(root_entry_validator.iter_errors(mutant)):
                errors.append(f"ROOT_ENTRY_OWNER_DOMAIN_MUTANT:{owner_kind}")
        storage_mutants = {
            "VALUE": "PlaceId:s",
            "PLACE": "ValueId:s",
            "FRAME_SLOT": "RuntimeRootSlotId:s",
            "RUNTIME_SLOT": "FrameSlotId:s",
        }
        for storage_kind, wrong_storage_id in storage_mutants.items():
            mutant = copy.deepcopy(base_root_entry)
            mutant["storage_kind"] = storage_kind
            mutant["storage_id"] = wrong_storage_id
            if not list(root_entry_validator.iter_errors(mutant)):
                errors.append(f"ROOT_ENTRY_STORAGE_DOMAIN_MUTANT:{storage_kind}")
        for error in sorted(
            Draft202012Validator(fixture_schema).iter_errors(fixture),
            key=lambda item: list(item.absolute_path),
        ):
            locator = "/".join(str(part) for part in error.absolute_path)
            errors.append(f"JSON_SCHEMA:{locator}:{error.message}")
    except ImportError:
        if set(fixture) != {
            "schema",
            "fixture_schema",
            "revision",
            "contract",
            "baseline",
            "evidence_state",
            "semantic_cases",
            "mutation_matrix",
            "expected_counts",
        }:
            errors.append("FIXTURE_TOP_LEVEL_SHAPE")
    return errors


def validate_contract(
    contract: dict[str, Any],
    plan_schema: dict[str, Any],
    native_receipt_schema: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    profile = contract.get("profile", {})
    if contract.get("baseline_commit") != BASELINE or contract.get(
        "baseline_tree"
    ) != BASELINE_TREE:
        errors.append("BASELINE_BINDING")
    if contract.get("gap_id") != "IR-OWN-P1-025":
        errors.append("GAP_BINDING")
    dependency = contract.get("dependency_guard", {})
    if not (
        dependency.get("gap_id") == "IR-OWN-P0-017"
        and dependency.get("status_at_baseline") == "APPROVED_NOT_INTEGRATED"
        and dependency.get("gap_role") == "GOVERNANCE_TRACKING_ONLY"
        and dependency.get("successor_binding_status") == "EXACT_LOCAL_FUSION_BOUND"
        and dependency.get("continuation_root_interface_id") == CONTINUATION_INTERFACE_ID
        and dependency.get("continuation_root_interface_digest") == CONTINUATION_INTERFACE_DIGEST
        and dependency.get("canonical_promotion_ready") is True
        and dependency.get("r36_replaces_dependency_state_machine") is False
    ):
        errors.append("DEPENDENCY_GUARD")
    if not (
        contract.get("source_syntax_change_count") == 0
        and contract.get("semantic_p0") == 0
        and contract.get("feature_p1") == "22_OPEN_UNCHANGED"
        and contract.get("m13_actions") == "4_OPEN_UNCHANGED"
        and contract.get("product_lanes") == "15_OF_15_NOT_RUN"
    ):
        errors.append("EVIDENCE_STATE")
    expected_profile = {
        "profile_id": PROFILE_ID,
        "collector_kind": "STOP_THE_WORLD_FULL_HEAP_MARK_SWEEP",
        "relocation_policy": "NONMOVING",
        "concurrency_policy": "NONCONCURRENT",
        "generation_policy": "NONGENERATIONAL",
        "handle_model": "OPAQUE_STABLE_HANDLE",
        "root_strategy": "EXPLICIT_SHADOW_ROOT_FRAMES",
    }
    for key, expected in expected_profile.items():
        if profile.get(key) != expected:
            errors.append(f"PROFILE:{key}")
    zero_fields = [
        "read_barrier_count",
        "write_barrier_count",
        "weak_reference_surface_count",
        "ephemeron_surface_count",
        "user_finalizer_surface_count",
        "resurrection_surface_count",
        "pinning_surface_count",
        "managed_ffi_export_count",
    ]
    if any(profile.get(field) != 0 for field in zero_fields):
        errors.append("PROFILE_ZERO_FENCE")
    safepoints = contract.get("safepoint_contract", {})
    if safepoints.get("closed_site_kinds") != CLOSED_SITE_KINDS:
        errors.append("SAFEPOINT_CLOSED_SET")
    if safepoints.get("terminator_binding") != SITE_TERMINATORS:
        errors.append("SAFEPOINT_TERMINATOR_BINDING")
    if len(contract.get("rules", [])) != 20 or len(
        {row.get("rule_id") for row in contract.get("rules", [])}
    ) != 20:
        errors.append("RULE_CARDINALITY")
    diagnostics = contract.get("diagnostic_contract", {})
    if diagnostics.get("projection_diagnostics") != PROJECTION_DIAGNOSTICS:
        errors.append("DIAGNOSTIC_CLOSED_SET")
    if plan_schema.get("properties", {}).get("memory_profile_id", {}).get(
        "const"
    ) != PROFILE_ID:
        errors.append("PLAN_SCHEMA_PROFILE_BINDING")
    plan_required = set(plan_schema.get("required", []))
    if not {
        "continuation_root_interface_id",
        "continuation_root_interface_digest",
    }.issubset(plan_required):
        errors.append("PLAN_CONTINUATION_DEPENDENCY_BINDING")
    if plan_schema.get("properties", {}).get(
        "continuation_root_interface_id", {}
    ).get("const") != CONTINUATION_INTERFACE_ID:
        errors.append("PLAN_CONTINUATION_TYPED_IDENTITY")
    defs = plan_schema.get("$defs", {})
    typed_domains = {
        "managedMemoryPlanId",
        "bodyId",
        "mirNodeId",
        "typeId",
        "managedTraceDescriptorId",
        "projectionId",
        "rootId",
        "rootMapId",
        "safepointId",
        "activeFrameId",
        "continuationFrameId",
        "cleanupCaptureId",
        "pendingOutcomeId",
        "closureEnvironmentId",
        "actorEnvelopeId",
        "runStateId",
        "replyStateId",
        "runtimeOwnerId",
        "valueId",
        "placeId",
        "frameSlotId",
        "runtimeRootSlotId",
        "noCollectRegionId",
        "suspensionPointId",
    }
    patterns = [defs.get(name, {}).get("pattern") for name in typed_domains]
    if any(not isinstance(pattern, str) for pattern in patterns) or len(
        set(patterns)
    ) != len(patterns):
        errors.append("PLAN_TYPED_IDENTITY_DOMAIN_CLOSURE")
    if len(defs.get("rootEntry", {}).get("allOf", [])) != 13:
        errors.append("PLAN_ROOT_ENTRY_DISCRIMINATOR_CLOSURE")
    root_entry = defs.get("rootEntry", {})
    if (
        "handle_generation" not in set(root_entry.get("required", []))
        or "generation_checked" in root_entry.get("properties", {})
    ):
        errors.append("PLAN_ROOT_ENTRY_EXACT_GENERATION")
    transfer = defs.get("suspensionTransfer", {})
    if (
        "root_rebind_pairs" not in set(transfer.get("required", []))
        or "rootRebindPair" not in defs
    ):
        errors.append("PLAN_ROOT_REBIND_PAIR_CLOSURE")
    native_required = set(native_receipt_schema.get("required", []))
    if not set(REQUIRED_NATIVE_RECEIPT_FIELDS).issubset(native_required):
        errors.append("NATIVE_RECEIPT_REQUIRED_FIELD_BINDING")
    native_properties = native_receipt_schema.get("properties", {})
    if (
        "root_map_projection_digest" in native_properties
        or "jit_generation_identity_or_null" in native_properties
        or "target_root_projection_digest" not in native_properties
        or "finalized_image_identity_or_null" not in native_properties
    ):
        errors.append("NATIVE_RECEIPT_VOCABULARY_CLOSURE")
    return errors


def validate_semantic_cases(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = fixture.get("semantic_cases", [])
    ids = [row.get("case_id") for row in cases]
    if len(cases) != 24 or len(set(ids)) != 24:
        errors.append("SEMANTIC_CASE_CARDINALITY")
    if Counter(row.get("class") for row in cases) != {
        "positive": 6,
        "boundary": 7,
        "negative": 11,
    }:
        errors.append("SEMANTIC_CLASS_CARDINALITY")
    for row in cases:
        observed = evaluate(row.get("facts", {}))
        if observed != row.get("expected"):
            errors.append(
                f"SEMANTIC_EXPECTATION:{row.get('case_id')}:"
                f"observed={observed}:expected={row.get('expected')}"
            )
    return errors


def mutated_facts(operator: str) -> dict[str, Any]:
    facts: dict[str, Any] = {
        "site_kind": "NONTAIL_INVOKE",
        "terminator_kind": "INVOKE",
        "safepoint_declared": True,
        "running_root_ids": ["Root.a", "Root.b"],
        "frame_root_ids": [],
        "runtime_root_ids": [],
        "declared_root_ids": ["Root.a", "Root.b"],
        "entry_root_ids": ["Root.a", "Root.b"],
        "root_set_digest_valid": True,
        "receipt_published_before_entry": True,
        "receipt_live_through_outcome": True,
        "allocation_fast_path_may_collect": False,
        "raw_interior_crosses_safepoint": False,
        "raw_interior_crosses_call": False,
        "raw_interior_crosses_suspension": False,
        "raw_interior_crosses_actor_boundary": False,
        "raw_interior_crosses_ffi": False,
        "continuation_interface_bound": True,
        "cross_path_parity": True,
        "product_execution": "NOT_RUN",
    }
    if operator == "DROP_ROOT":
        facts["declared_root_ids"] = ["Root.a"]
        facts["entry_root_ids"] = ["Root.a"]
    elif operator == "ADD_STALE_ROOT":
        facts["declared_root_ids"] = ["Root.a", "Root.b", "Root.stale"]
        facts["entry_root_ids"] = ["Root.a", "Root.b", "Root.stale"]
    elif operator == "DUPLICATE_ROOT":
        facts["declared_root_ids"] = ["Root.a", "Root.a", "Root.b"]
    elif operator == "REVERSE_ROOT_ORDER":
        facts["declared_root_ids"] = ["Root.b", "Root.a"]
        facts["entry_root_ids"] = ["Root.b", "Root.a"]
    elif operator in {"CORRUPT_ROOT_DIGEST", "CHANGE_SAFEPOINT_ID_WITHOUT_DIGEST"}:
        facts["root_set_digest_valid"] = False
    elif operator == "REMOVE_SAFEPOINT_DECLARATION":
        facts["safepoint_declared"] = False
    elif operator == "ENABLE_COLLECTING_FAST_PATH":
        facts["allocation_fast_path_may_collect"] = True
    elif operator == "EXTEND_INTERIOR_POINTER_ACROSS_SAFEPOINT":
        facts["raw_interior_crosses_safepoint"] = True
    elif operator == "EXTEND_INTERIOR_POINTER_ACROSS_CALL":
        facts["raw_interior_crosses_call"] = True
    elif operator == "EXTEND_INTERIOR_POINTER_ACROSS_SUSPENSION":
        facts["raw_interior_crosses_suspension"] = True
    elif operator == "EXTEND_INTERIOR_POINTER_ACROSS_ACTOR_BOUNDARY":
        facts["raw_interior_crosses_actor_boundary"] = True
    elif operator == "DROP_CONTINUATION_INTERFACE_BINDING":
        facts["continuation_interface_bound"] = False
    elif operator == "PUBLISH_RECEIPT_AFTER_ENTRY":
        facts["receipt_published_before_entry"] = False
    elif operator == "ENABLE_RELOCATION":
        facts["moving_collector"] = True
    elif operator == "ENABLE_CONCURRENT_OR_GENERATIONAL_COLLECTION":
        facts["concurrent_collector"] = True
        facts["generational_collector"] = True
    elif operator == "ENABLE_WEAK_REFERENCE":
        facts["weak_reference_count"] = 1
    elif operator == "ENABLE_USER_FINALIZER":
        facts["user_finalizer_count"] = 1
    elif operator == "RETIRE_JIT_WITH_SUSPENDED_LEASE":
        facts.update(
            {
                "jit_state": "UNPUBLISHED",
                "active_native_activation_count": 0,
                "suspended_continuation_count": 1,
                "outstanding_root_receipt_count": 0,
                "retirement_requested": True,
            }
        )
    elif operator == "CHANGE_TARGET_SEMANTIC_TRACE_OR_CLAIM_PRODUCT_PASS":
        facts["cross_path_parity"] = False
        facts["product_execution"] = "PASS"
    else:
        raise ValidationFailure(f"UNKNOWN_MUTATION:{operator}")
    return facts


def validate_mutations(fixture: dict[str, Any]) -> tuple[list[str], int]:
    errors: list[str] = []
    rows = fixture.get("mutation_matrix", [])
    operators = [row.get("operator") for row in rows]
    if operators != EXPECTED_MUTATIONS or len({row.get("mutation_id") for row in rows}) != 20:
        errors.append("MUTATION_CLOSED_SET")
    killed = 0
    for row in rows:
        operator = row.get("operator")
        observed = evaluate(mutated_facts(operator))
        expected = row.get("expected_failure")
        observed_diagnostic = observed.get("diagnostic_id_or_null")
        if operator == "CHANGE_TARGET_SEMANTIC_TRACE_OR_CLAIM_PRODUCT_PASS":
            parity_killed = observed_diagnostic == "MANAGED_REFERENCE_PROJECTION_PARITY_MISMATCH"
            overclaim_killed = (
                evaluate({"product_execution": "PASS"}).get("diagnostic_id_or_null")
                == "PRODUCT_SUPPORT_OVERCLAIM"
            )
            ok = expected == "MANAGED_REFERENCE_PROJECTION_PARITY_MISMATCH_OR_PRODUCT_OVERCLAIM" and parity_killed and overclaim_killed
        else:
            ok = observed.get("verdict") == "REJECT_STATIC" and observed_diagnostic == expected
        if ok:
            killed += 1
        else:
            errors.append(
                f"MUTATION_SURVIVED:{row.get('mutation_id')}:"
                f"observed={observed}:expected={expected}"
            )
    return errors, killed


def validate_catalog_bindings(root: Path) -> list[str]:
    errors: list[str] = []
    features = catalog_rows(root, "spec/features/catalog/chunks/*.json")
    diagnostics = catalog_rows(root, "spec/diagnostics/catalog/chunks/*.json")
    try:
        feature = unique_row(features, "feature_id", FEATURE_ID, "FEATURE_BINDING")
        if not (
            feature.get("status_enum") == "STABLE_DESIGN"
            and feature.get("source_activation") == "none"
            and feature.get("product_support") == "NOT_RUN"
            and feature.get("primary_source") == CONTRACT_PATH
        ):
            errors.append("FEATURE_STATUS_FENCE")
        trace_diagnostics = feature.get("normative_trace_refs", {}).get(
            "diagnostics", []
        )
        if trace_diagnostics != [
            "HIR_MIR_CAPABILITY_RECEIPT_MISMATCH",
            *PROJECTION_DIAGNOSTICS,
        ]:
            errors.append("FEATURE_DIAGNOSTIC_BINDING")
    except ValidationFailure as exc:
        errors.append(str(exc))
    for diagnostic_id in PROJECTION_DIAGNOSTICS:
        try:
            row = unique_row(
                diagnostics,
                "diagnostic_id",
                diagnostic_id,
                "DIAGNOSTIC_BINDING",
            )
            if not (
                row.get("diagnostic_class") == "release_verifier"
                and row.get("product_support") == "NOT_RUN"
                and row.get("fixit_kind") == "none"
            ):
                errors.append(f"DIAGNOSTIC_STATUS:{diagnostic_id}")
        except ValidationFailure as exc:
            errors.append(str(exc))
    return errors


def validate_bound_artifacts(root: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cranelift = read_json(root, "spec/contracts/cranelift-backend-current.json")
    bridge = read_json(root, "spec/contracts/hir-h1-current-mir-bridge.json")
    registry = read_json(root, "spec/contracts/mir-machine-registry.json")
    guard = cranelift.get("managed_reference_guard", {})
    if not (
        guard.get("memory_profile_id") == PROFILE_ID
        and guard.get("managed_memory_plan_schema")
        == "deeplus.managed-memory-plan/r1"
        and guard.get("missing_or_invalid_plan") == "BLOCK_NATIVE_LOWERING"
        and guard.get("raw_pointer_fallback") is False
    ):
        errors.append("CRANELIFT_PROFILE_BINDING")
    if guard.get("required_native_projection_receipt_fields") != REQUIRED_NATIVE_RECEIPT_FIELDS:
        errors.append("CRANELIFT_NATIVE_RECEIPT_FIELD_BINDING")
    native = bridge.get("native_projection_contract", {})
    bridge_guard = native.get("managed_reference_guard", {})
    if bridge_guard.get("memory_profile_id") != PROFILE_ID:
        errors.append("HIR_BRIDGE_PROFILE_BINDING")
    if bridge_guard.get("required_native_projection_receipt_fields") != REQUIRED_NATIVE_RECEIPT_FIELDS:
        errors.append("HIR_BRIDGE_NATIVE_RECEIPT_FIELD_BINDING")
    capabilities = {
        row.get("capability_id"): row for row in registry.get("capabilities", [])
    }
    safepoint = capabilities.get("DM-CAP-SAFEPOINT-ROOTMAP-R1", {})
    expected_terms = [
        "BR",
        "COND_BR",
        "INVOKE",
        "CHECKED",
        "SUSPEND",
        "CANCEL_CHECK",
        "RUN_OP",
        "ACTOR_OP",
        "PROVIDER_OP",
        "ONCE_OP",
        "SYNC_OP",
    ]
    if safepoint.get("terminator_kinds") != expected_terms:
        errors.append("MIR_CAPABILITY_SAFEPOINT_TERMINATORS")
    if safepoint.get("managed_memory_plan_schema") != "deeplus.managed-memory-plan/r1":
        errors.append("MIR_CAPABILITY_PLAN_SCHEMA")
    mir_schema = read_json(root, "schemas/language/deeplus-mir.schema.json")
    verifier = mir_schema.get("x-deeplus-verifier-contract", {})
    if verifier.get("managed_memory_plan") != (
        "RECOMPUTE_AND_BIND_DEEPLUS_MANAGED_MEMORY_PLAN_R1_WHEN_"
        "DM_CAP_SAFEPOINT_ROOTMAP_R1_IS_REQUIRED"
    ):
        errors.append("MIR_SCHEMA_PLAN_BINDING")
    text_bindings = [
        "decisions/language/Design_Deeplus_Managed_Reference_Memory_Profile_R1.md",
        "spec/mir/semantics.md",
        "spec/language.md",
    ]
    for relative in text_bindings:
        text = (root / relative).read_text(encoding="utf-8")
        if PROFILE_ID not in text:
            errors.append(f"TEXT_PROFILE_BINDING:{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[dict[str, Any]] = []

    def record(check_id: str, errors: list[str]) -> None:
        checks.append(
            {
                "check_id": check_id,
                "pass": not errors,
                "errors": errors,
            }
        )

    try:
        contract = read_json(root, CONTRACT_PATH)
        plan_schema = read_json(root, PLAN_SCHEMA_PATH)
        native_receipt_schema = read_json(root, NATIVE_RECEIPT_SCHEMA_PATH)
        fixture_schema = read_json(root, FIXTURE_SCHEMA_PATH)
        fixture = read_json(root, FIXTURE_PATH)
        record(
            "R36_SCHEMA_AND_FIXTURE_PARSE",
            validate_schema(
                plan_schema, native_receipt_schema, fixture_schema, fixture
            ),
        )
        record(
            "R36_PROFILE_AND_DEPENDENCY_CONTRACT",
            validate_contract(contract, plan_schema, native_receipt_schema),
        )
        record("R36_SEMANTIC_MATRIX", validate_semantic_cases(fixture))
        mutation_errors, killed = validate_mutations(fixture)
        record("R36_MUTATION_MATRIX", mutation_errors)
        record("R36_CATALOG_BINDING", validate_catalog_bindings(root))
        record("R36_BOUND_ARTIFACTS", validate_bound_artifacts(root, contract))
    except ValidationFailure as exc:
        record("R36_PRECONDITION", [str(exc)])
        killed = 0

    failures = [error for row in checks for error in row["errors"]]
    receipt = {
        "schema": "deeplus.r36-managed-reference-memory-profile-validation-receipt/r1",
        "baseline_commit": BASELINE,
        "baseline_tree": BASELINE_TREE,
        "result": "PASS" if not failures else "FAIL",
        "evidence_level": "E2_DESIGN_STATIC",
        "checks": len(checks),
        "passed": sum(row["pass"] for row in checks),
        "failed": sum(not row["pass"] for row in checks),
        "semantic_cases": "24_OF_24_PASS" if not next(
            (row["errors"] for row in checks if row["check_id"] == "R36_SEMANTIC_MATRIX"),
            ["missing"],
        ) else "FAIL",
        "mutations_rejected": f"{killed}_OF_20",
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
        "github_mutation": 0,
        "check_results": checks,
        "errors": failures,
        "evidence_honesty": "Static closure is not parser, checker, collector, xVM, Cranelift, FFI, tooling or product execution evidence.",
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
