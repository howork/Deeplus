#!/usr/bin/env python3
"""Validate the R37 Deeplus internal runtime ABI design-static closure."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any

from validate_hir_mir_machine_contract import schema_errors


CONTRACT = "spec/contracts/internal-runtime-abi-r1.json"
REGISTRY = "spec/contracts/runtime-helper-registry-r1.json"
FIXTURES = "tests/fixtures/current/internal-runtime-abi-r1.json"

SCHEMAS = [
    "schemas/language/internal-runtime-abi-r1.schema.json",
    "schemas/language/runtime-helper-registry-r1.schema.json",
    "schemas/language/internal-runtime-target-projection-r1.schema.json",
    "schemas/language/internal-runtime-artifact-binding-receipt-r1.schema.json",
    "schemas/language/internal-runtime-abi-fixtures-r1.schema.json",
]

FEATURE_ROW_SCHEMA = "schemas/language/feature-row.schema.json"
DIAGNOSTIC_ROW_SCHEMA = "schemas/language/diagnostic-row.schema.json"
FEATURE_CHUNK = "spec/features/catalog/chunks/part-0027.json"
DIAGNOSTIC_CHUNK = "spec/diagnostics/catalog/chunks/part-0032.json"

EXPECTED_RECEIPT_INPUTS = [
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
    "continuation_root_interface_digest",
    "target_root_projection_digest",
    "runtime_root_registry_digest",
    "object_linker_or_jit_import_map_identity",
]

EXPECTED_MODULE_KINDS = ["Xvm", "ObjectAot", "InMemoryJit"]
TYPED_ABI_ID = "RuntimeAbiId:DEEPLUS_INTERNAL_RUNTIME_ABI_R1"

DIAGNOSTICS = [
    "RUNTIME_ABI_DIGEST_MISMATCH",
    "RUNTIME_ABI_HELPER_SET_INVALID",
    "RUNTIME_ABI_HELPER_SIGNATURE_MISMATCH",
    "RUNTIME_ABI_CHANNEL_PROJECTION_INVALID",
    "RUNTIME_ABI_OUTCOME_TRANSPORT_INVALID",
    "RUNTIME_ABI_OWNERSHIP_COMMIT_INVALID",
    "RUNTIME_ABI_HOST_UNWIND_FORBIDDEN",
    "RUNTIME_ABI_TARGET_PROJECTION_MISMATCH",
    "RUNTIME_ABI_JIT_IMPORT_INVALID",
    "RUNTIME_ABI_JIT_RETIREMENT_LEASE_VIOLATION",
    "RUNTIME_ABI_CROSS_PATH_PARITY_MISMATCH",
    "RUNTIME_ABI_ARTIFACT_BINDING_MISMATCH",
]

BASE_OPERATIONS = {
    "CANCEL_CHECK": {"CHECK"},
    "SUSPEND": {"PARK"},
    "RUN_OP": {"SPAWN", "AWAIT", "JOIN", "CANCEL_THEN_JOIN", "EXIT"},
    "ACTOR_OP": {
        "SEND",
        "REQUEST",
        "AWAIT_REPLY",
        "DEQUEUE",
        "TURN_BEGIN",
        "TURN_END",
        "REPLY",
    },
    "PROVIDER_OP": {"DISPATCH"},
    "ONCE_OP": {"FUNCTION_STATIC_ENSURE", "LAZY_FORCE"},
    "SYNC_OP": {
        "OBSERVE_BEGIN",
        "OBSERVE_END",
        "REPLACE_COMMIT",
        "LOCK_ACQUIRE",
        "LOCK_RELEASE",
    },
}

CONDITIONAL_OPERATIONS = {
    "MANAGED_ALLOCATE_SLOW",
    "MANAGED_SAFEPOINT_ENTER",
    "MANAGED_SAFEPOINT_LEAVE",
}

EXPECTED_MUTATIONS = {
    "CORRUPT_RUNTIME_ABI_DIGEST": "RUNTIME_ABI_DIGEST_MISMATCH",
    "ADD_UNLISTED_HELPER": "RUNTIME_ABI_HELPER_SET_INVALID",
    "DUPLICATE_HELPER_ID": "RUNTIME_ABI_HELPER_SET_INVALID",
    "DROP_REQUIRED_HELPER": "RUNTIME_ABI_HELPER_SET_INVALID",
    "CHANGE_HELPER_SIGNATURE": "RUNTIME_ABI_HELPER_SIGNATURE_MISMATCH",
    "CHANGE_HELPER_VERSION": "RUNTIME_ABI_HELPER_SIGNATURE_MISMATCH",
    "CHANGE_ARGUMENT_CHANNEL_CLASS": "RUNTIME_ABI_CHANNEL_PROJECTION_INVALID",
    "RETURN_AGGREGATE_WITHOUT_SRET": "RUNTIME_ABI_CHANNEL_PROJECTION_INVALID",
    "ALIAS_SRET_WITH_INPUT": "RUNTIME_ABI_CHANNEL_PROJECTION_INVALID",
    "MISMATCH_OUTCOME_TAG_AND_PAYLOAD": "RUNTIME_ABI_OUTCOME_TRANSPORT_INVALID",
    "REPLACE_EXPLICIT_OUTCOME_WITH_HOST_UNWIND": "RUNTIME_ABI_HOST_UNWIND_FORBIDDEN",
    "COMMIT_ARGUMENT_BEFORE_PREFLIGHT": "RUNTIME_ABI_OWNERSHIP_COMMIT_INVALID",
    "ROLLBACK_AFTER_OWNERSHIP_COMMIT": "RUNTIME_ABI_OWNERSHIP_COMMIT_INVALID",
    "INHERIT_HOST_TARGET_DEFAULT": "RUNTIME_ABI_TARGET_PROJECTION_MISMATCH",
    "CHANGE_TARGET_PROJECTION_WITHOUT_DIGEST": "RUNTIME_ABI_TARGET_PROJECTION_MISMATCH",
    "RESOLVE_UNLISTED_JIT_IMPORT": "RUNTIME_ABI_JIT_IMPORT_INVALID",
    "CHANGE_JIT_IMPORT_SIGNATURE": "RUNTIME_ABI_JIT_IMPORT_INVALID",
    "RETIRE_JIT_WITH_NONZERO_LEASE": "RUNTIME_ABI_JIT_RETIREMENT_LEASE_VIOLATION",
    "DIVERGE_XVM_AOT_JIT_LOGICAL_TRACE": "RUNTIME_ABI_CROSS_PATH_PARITY_MISMATCH",
    "CORRUPT_FINAL_ARTIFACT_BINDING": "RUNTIME_ABI_ARTIFACT_BINDING_MISMATCH",
}


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def normalized(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(value[key]) for key in sorted(value)}
    if isinstance(value, float):
        raise ValueError("floats are forbidden in canonical ABI material")
    return value


def digest(value: Any) -> str:
    payload = json.dumps(
        normalized(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def material_without(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in keys}


def check(condition: bool, check_id: str, detail: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {check_id}: {detail}")
    else:
        failures.append(f"{check_id}: {detail}")
        print(f"FAIL {check_id}: {detail}")


def mutation_oracle(operator: str) -> str | None:
    state = {
        "abi_digest": True,
        "helper_set": True,
        "helper_signature": True,
        "channel": True,
        "outcome": True,
        "ownership": True,
        "no_unwind": True,
        "target": True,
        "jit_import": True,
        "jit_retirement": True,
        "parity": True,
        "artifact": True,
    }
    mutations = {
        "CORRUPT_RUNTIME_ABI_DIGEST": "abi_digest",
        "ADD_UNLISTED_HELPER": "helper_set",
        "DUPLICATE_HELPER_ID": "helper_set",
        "DROP_REQUIRED_HELPER": "helper_set",
        "CHANGE_HELPER_SIGNATURE": "helper_signature",
        "CHANGE_HELPER_VERSION": "helper_signature",
        "CHANGE_ARGUMENT_CHANNEL_CLASS": "channel",
        "RETURN_AGGREGATE_WITHOUT_SRET": "channel",
        "ALIAS_SRET_WITH_INPUT": "channel",
        "MISMATCH_OUTCOME_TAG_AND_PAYLOAD": "outcome",
        "REPLACE_EXPLICIT_OUTCOME_WITH_HOST_UNWIND": "no_unwind",
        "COMMIT_ARGUMENT_BEFORE_PREFLIGHT": "ownership",
        "ROLLBACK_AFTER_OWNERSHIP_COMMIT": "ownership",
        "INHERIT_HOST_TARGET_DEFAULT": "target",
        "CHANGE_TARGET_PROJECTION_WITHOUT_DIGEST": "target",
        "RESOLVE_UNLISTED_JIT_IMPORT": "jit_import",
        "CHANGE_JIT_IMPORT_SIGNATURE": "jit_import",
        "RETIRE_JIT_WITH_NONZERO_LEASE": "jit_retirement",
        "DIVERGE_XVM_AOT_JIT_LOGICAL_TRACE": "parity",
        "CORRUPT_FINAL_ARTIFACT_BINDING": "artifact",
    }
    field = mutations.get(operator)
    if field is None:
        return None
    state[field] = False
    priority = [
        ("abi_digest", DIAGNOSTICS[0]),
        ("helper_set", DIAGNOSTICS[1]),
        ("helper_signature", DIAGNOSTICS[2]),
        ("channel", DIAGNOSTICS[3]),
        ("outcome", DIAGNOSTICS[4]),
        ("ownership", DIAGNOSTICS[5]),
        ("no_unwind", DIAGNOSTICS[6]),
        ("target", DIAGNOSTICS[7]),
        ("jit_import", DIAGNOSTICS[8]),
        ("jit_retirement", DIAGNOSTICS[9]),
        ("parity", DIAGNOSTICS[10]),
        ("artifact", DIAGNOSTICS[11]),
    ]
    return next((diag for key, diag in priority if not state[key]), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    failures: list[str] = []

    required = [
        CONTRACT,
        REGISTRY,
        FIXTURES,
        *SCHEMAS,
        FEATURE_ROW_SCHEMA,
        DIAGNOSTIC_ROW_SCHEMA,
        FEATURE_CHUNK,
        DIAGNOSTIC_CHUNK,
    ]
    check(
        all((root / rel).is_file() for rel in required),
        "R37_SCHEMA_INSTANCE_CLOSURE",
        f"required_files={len(required)}",
        failures,
    )
    if failures:
        return 1

    contract = load_json(root, CONTRACT)
    registry = load_json(root, REGISTRY)
    fixtures = load_json(root, FIXTURES)
    schema_documents = {rel: load_json(root, rel) for rel in SCHEMAS}
    for rel in SCHEMAS:
        schema = schema_documents[rel]
        check(
            schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
            and schema.get("type") == "object",
            "R37_SCHEMA_INSTANCE_CLOSURE",
            rel,
            failures,
        )

    schema_instance_pairs = [
        (
            fixtures.get("runtime_abi_instance"),
            "schemas/language/internal-runtime-abi-r1.schema.json",
            "runtime ABI manifest",
        ),
        (
            registry,
            "schemas/language/runtime-helper-registry-r1.schema.json",
            "runtime helper registry",
        ),
        *[
            (
                row,
                "schemas/language/internal-runtime-target-projection-r1.schema.json",
                f"target projection {index}",
            )
            for index, row in enumerate(
                fixtures.get("target_projection_instances", [])
            )
        ],
        *[
            (
                row,
                "schemas/language/internal-runtime-artifact-binding-receipt-r1.schema.json",
                f"artifact receipt {index}",
            )
            for index, row in enumerate(
                fixtures.get("artifact_binding_receipts", [])
            )
        ],
        (
            fixtures,
            "schemas/language/internal-runtime-abi-fixtures-r1.schema.json",
            "fixture container",
        ),
    ]
    instance_errors = [
        f"{label}: {error}"
        for instance, schema_rel, label in schema_instance_pairs
        for error in schema_errors(
            instance, schema_documents[schema_rel], schema_documents[schema_rel]
        )
    ]
    check(
        not instance_errors,
        "R37_SCHEMA_INSTANCE_CLOSURE",
        "instances=9 errors=" + str(instance_errors[:3]),
        failures,
    )

    helper_rows = registry.get("helper_rows", [])
    conditional = registry.get("conditional_extension_rows", [])
    continuation_rows = [
        row
        for row in helper_rows
        if row.get("may_suspend") is True
    ]
    active_helper_rows = [*helper_rows, *conditional]
    helper_ids = [row.get("runtime_helper_id") for row in helper_rows]
    operations: dict[str, set[str]] = {}
    signature_ok = True
    ownership_digest_ok = True
    address_fence_ok = True
    for row in helper_rows:
        operations.setdefault(row.get("terminator_kind"), set()).add(row.get("operation"))
    for row in [*helper_rows, *conditional]:
        signature_ok &= row.get("signature_digest") == digest(
            material_without(row, "signature_digest")
        )
        expected_address_classes = [
            "OPAQUE_MANAGED_HANDLE" if mode == "OPAQUE_HANDLE" else
            "CALL_BOUNDED_ADDRESS" if mode in {
                "BORROW_READ_CALL_BOUND", "INOUT_EXCLUSIVE_CALL_BOUND"
            } else "NON_ADDRESS_VALUE"
            for mode in row.get("parameter_modes", [])
        ]
        ownership_material = {
            key: row.get(key)
            for key in (
                "runtime_helper_id", "parameter_modes", "parameter_address_classes",
                "normal_result_kind", "admitted_outcomes", "completion_modes",
                "may_collect", "may_suspend", "observes_cancellation",
                "managed_referent_or_interior_address_cross_boundary",
            )
        }
        ownership_digest_ok &= row.get("ownership_profile_digest") == digest(
            ownership_material
        )
        address_fence_ok &= (
            row.get("parameter_address_classes") == expected_address_classes
            and row.get("managed_referent_or_interior_address_cross_boundary") is False
        )
    expected_ops = {key: set(value) for key, value in BASE_OPERATIONS.items()}
    check(
        len(helper_rows) == 22
        and helper_ids == sorted(helper_ids)
        and len(helper_ids) == len(set(helper_ids))
        and operations == expected_ops
        and {row.get("operation") for row in conditional} == CONDITIONAL_OPERATIONS
        and len(active_helper_rows) == 25
        and len(continuation_rows) == 6
        and all(
            row.get("activation_status") is None
            and row.get("dependency_gap_id") is None
            and row.get("continuation_interface_digest_or_null")
            == registry.get("continuation_interface_digest_or_null")
            and "PARKED" in row.get("completion_modes", [])
            for row in continuation_rows
        )
        and all(
            "activation_status" not in row and "dependency_gap_id" not in row
            for row in helper_rows
        )
        and all(
            row.get("activation_status") is None
            and row.get("dependency_gap_id") is None
            and row.get("managed_reference_profile_digest_or_null")
            == registry.get("managed_reference_profile_digest_or_null")
            for row in conditional
        ),
        "R37_HELPER_ALLOWLIST",
        (
            f"declared={len(helper_rows)} active={len(active_helper_rows)} "
            f"continuation={len(continuation_rows)} managed={len(conditional)}"
        ),
        failures,
    )
    check(
        signature_ok and ownership_digest_ok and address_fence_ok,
        "R37_HELPER_ALLOWLIST",
        "all helper signature/ownership digests and address classes recompute",
        failures,
    )
    helper_rows_digest = digest(helper_rows)
    conditional_digest = digest(conditional)
    allowlist_digest = digest(
        [
            {
                "runtime_helper_id": row["runtime_helper_id"],
                "runtime_helper_signature_id": row["runtime_helper_signature_id"],
                "helper_version": row["helper_version"],
                "signature_digest": row["signature_digest"],
            }
            for row in active_helper_rows
        ]
    )
    registry_material = registry.get("digest_material", {})
    check(
        registry_material.get("helper_rows_digest") == helper_rows_digest
        and registry_material.get("conditional_extension_rows_digest") == conditional_digest
        and registry.get("helper_allowlist_digest") == allowlist_digest
        and registry.get("registry_digest") == digest(registry_material),
        "R37_CANONICAL_DIGEST",
        "registry rows, allowlist and registry digests bind",
        failures,
    )
    by_helper_id = {
        row.get("runtime_helper_id"): row for row in [*helper_rows, *conditional]
    }
    synchronous_blocking_ids = {
        "RuntimeHelperId:once.function_static_ensure",
        "RuntimeHelperId:once.lazy_force",
        "RuntimeHelperId:sync.lock_acquire",
    }
    synchronous_blocking_ok = all(
        by_helper_id[helper_id].get("completion_modes") == ["COMPLETE"]
        and by_helper_id[helper_id].get("may_suspend") is False
        and by_helper_id[helper_id].get("observes_cancellation") is False
        and "CANCELLATION"
        not in by_helper_id[helper_id].get("admitted_outcomes", [])
        for helper_id in synchronous_blocking_ids
    )
    safepoint_enter = by_helper_id.get(
        "RuntimeHelperId:managed.safepoint_enter", {}
    )
    check(
        synchronous_blocking_ok
        and safepoint_enter.get("observes_cancellation") is False
        and "CANCELLATION"
        not in safepoint_enter.get("admitted_outcomes", []),
        "R37_SUSPENSION_AND_SAFEPOINT_FENCE",
        "host blocking is COMPLETE-only; safepoint never delivers cancellation",
        failures,
    )

    expected_kinds = contract.get("expected_counts", {}).get("logical_value_kinds")
    kind_rows = contract.get("logical_value_kinds", [])
    type_profile = contract.get("type_classification", {})
    outcome = contract.get("outcome_channel", {})
    check(
        len(kind_rows) == expected_kinds == 20
        and len({row.get("kind") for row in kind_rows}) == 20
        and type_profile.get("aggregate_register_split_admitted") is False
        and type_profile.get("one_field_aggregate_scalar_collapse") is False
        and type_profile.get("zero_sized_nominal_erases_identity") is False
        and outcome.get("aggregate_normal_uses_sret_slot") is True,
        "R37_ARGUMENT_RESULT_SRET",
        f"value_kinds={len(kind_rows)} indirect_aggregate=true",
        failures,
    )
    tags = outcome.get("tags", [])
    dispatcher = contract.get("dispatcher_contract", {})
    check(
        [(row.get("ordinal"), row.get("name")) for row in tags]
        == [(0, "NORMAL"), (1, "ERROR"), (2, "DEFECT"), (3, "CANCELLATION")]
        and outcome.get("exactly_one_tag_commits") is True
        and outcome.get("nonselected_slots_remain_uninitialized") is True
        and outcome.get("suspension_is_outcome_tag") is False
        and outcome.get("host_unwind_is_outcome") is False
        and contract.get("calling_model", {}).get("host_unwind_across_boundary") is False
        and dispatcher.get("logical_signature")
        == "RuntimeDispatchCompletion dispatch(RuntimeContextHandle, RuntimeCallPacketSlot)"
        and dispatcher.get("completion_union")
        == {"COMPLETE": "OutcomeTag", "PARKED": "ContinuationReceiptId"}
        and dispatcher.get("complete_requires_one_outcome_tag") is True
        and dispatcher.get("parked_requires_continuation_interface_digest") is True
        and dispatcher.get("parked_requires_continuation_ownership_receipt") is True
        and dispatcher.get("parked_commits_outcome_tag") is False
        and dispatcher.get("parked_commits_outcome_slot") is False
        and dispatcher.get("parked_commits_mir_successor") is False
        and dispatcher.get("bounded_continuation_dispatch", {}).get("profile_count") == 1
        and dispatcher.get("bounded_continuation_dispatch", {}).get("operation_allowlist")
        == ["RESUME", "CANCEL"]
        and dispatcher.get("arbitrary_callback_entry_count") == 0,
        "R37_OUTCOME_NO_UNWIND",
        "COMPLETE carries one of four outcomes; PARKED carries a continuation receipt",
        failures,
    )
    ownership = contract.get("ownership_boundary", {})
    parked_transfer = ownership.get("parked_transfer_receipt", {})
    check(
        ownership.get("pre_entry_order", [])[-2:] == ["OWNERSHIP_COMMIT", "CALLEE_ENTRY"]
        and ownership.get("ownership_commit_count") == 1
        and ownership.get("pre_entry_failure_restores_caller") is True
        and ownership.get("post_entry_outcome_restores_transferred_input") is False
        and ownership.get("complete_loan_end_on_every_outcome") is True
        and parked_transfer.get("receipt_id_type") == "ContinuationReceiptId"
        and parked_transfer.get("committed_owners_transfer_count") == "EXACT"
        and parked_transfer.get("active_loans_transfer_count") == "EXACT"
        and parked_transfer.get("admitted_loan_classes")
        == ["NONE", "STATIC_IMMUTABLE_SHARED"]
        and parked_transfer.get("forbidden_loan_classes")
        == ["STACK", "REGION", "INOUT", "EXCLUSIVE", "TEMPORARY_VIEW", "CALLBACK", "FACET"]
        and parked_transfer.get("cleanup_tokens_transfer_count") == "EXACT"
        and parked_transfer.get("root_ownership_transfer_count") == "EXACT"
        and parked_transfer.get("source_residual_count") == 0
        and parked_transfer.get("transfer_commit_count") == 1
        and parked_transfer.get("loan_end") == "RESUME_OR_CANCEL_TERMINAL_EDGE"
        and ownership.get("cleanup_owned_by_mir") is True,
        "R37_OWNERSHIP_TRANSACTION",
        "one pre-entry commit; PARKED transfers exact state to one receipt",
        failures,
    )

    abi = fixtures.get("runtime_abi_instance", {})
    check(
        abi.get("runtime_abi_id") == TYPED_ABI_ID
        and contract.get("calling_model", {}).get("abi_id") == TYPED_ABI_ID
        and registry.get("runtime_abi_id") == TYPED_ABI_ID
        and abi.get("mir_schema_digest") == file_digest(root / "schemas/language/deeplus-mir.schema.json")
        and abi.get("mir_machine_registry_digest") == file_digest(root / "spec/contracts/mir-machine-registry.json")
        and abi.get("helper_registry_digest") == registry.get("registry_digest")
        and abi.get("helper_allowlist_digest") == allowlist_digest
        and abi.get("runtime_abi_digest") == digest(abi.get("digest_material")),
        "R37_CANONICAL_DIGEST",
        "ABI instance binds exact MIR, registry, helper and canonical material",
        failures,
    )

    projections = fixtures.get("target_projection_instances", [])
    module_kinds = [row.get("module_kind") for row in projections]
    projection_ok = True
    for row in projections:
        projection_ok &= (
            row.get("runtime_abi_id") == TYPED_ABI_ID
            and row.get("runtime_abi_digest") == abi.get("runtime_abi_digest")
            and row.get("mir_schema_digest") == abi.get("mir_schema_digest")
            and row.get("mir_machine_registry_digest")
            == abi.get("mir_machine_registry_digest")
            and row.get("helper_allowlist_digest") == allowlist_digest
            and row.get("target_location_is_semantic_identity") is False
            and row.get("digest_material")
            == material_without(row, "digest_material", "projection_digest")
            and row.get("projection_digest") == digest(row.get("digest_material"))
            and row.get("stack_alignment_bytes") in {8, 16, 32, 64}
            and bool(row.get("target_triple"))
            and bool(row.get("calling_convention"))
        )
    check(
        module_kinds == EXPECTED_MODULE_KINDS
        and len(module_kinds) == len(set(module_kinds))
        and projection_ok,
        "R37_TARGET_PROJECTIONS",
        f"module_kinds={module_kinds}",
        failures,
    )

    receipts = fixtures.get("artifact_binding_receipts", [])
    receipt_module_kinds = [row.get("module_kind") for row in receipts]
    by_kind = {row["module_kind"]: row for row in projections}
    receipt_ok = True
    for row in receipts:
        projection = by_kind.get(row.get("module_kind"), {})
        receipt_ok &= (
            row.get("runtime_abi_digest") == abi.get("runtime_abi_digest")
            and row.get("target_projection_digest") == projection.get("projection_digest")
            and row.get("helper_allowlist_digest") == allowlist_digest
            and row.get("helper_symbol_or_table_map_digest")
            == projection.get("helper_symbol_or_table_map_digest")
            and row.get("digest_material")
            == material_without(row, "digest_material", "receipt_digest")
            and row.get("receipt_digest") == digest(row.get("digest_material"))
        )
        if row.get("module_kind") == "InMemoryJit":
            receipt_ok &= bool(row.get("resolved_import_map_digest_or_null"))
            receipt_ok &= bool(row.get("image_generation_id_or_null"))
            if row.get("retirement_admitted"):
                receipt_ok &= row.get("retirement_requested") is True
                receipt_ok &= row.get("active_call_lease_count") == 0
                receipt_ok &= row.get("suspended_continuation_lease_count") == 0
                receipt_ok &= row.get("outstanding_root_receipt_count") == 0
        else:
            receipt_ok &= row.get("image_generation_id_or_null") is None
    check(
        receipt_module_kinds == EXPECTED_MODULE_KINDS
        and len(receipt_module_kinds) == len(set(receipt_module_kinds))
        and receipt_ok,
        "R37_JIT_IMPORT_RETIREMENT",
        "three artifact receipts bind ABI/projection/helper and zero-lease JIT retirement",
        failures,
    )
    check(
        receipt_ok,
        "R37_ARTIFACT_BINDING",
        "artifact binding digest recomputation exact",
        failures,
    )
    check(
        projections[1].get("scalar_mapping_digest") == projections[2].get("scalar_mapping_digest")
        and projections[1].get("indirect_slot_mapping_digest")
        == projections[2].get("indirect_slot_mapping_digest")
        and projections[1].get("outcome_mapping_digest")
        == projections[2].get("outcome_mapping_digest")
        and contract.get("calling_model", {}).get("symbol_or_link_order_selects_identity") is False,
        "R37_CROSS_PATH_PARITY",
        "AOT/JIT logical maps equal; xVM binds same ABI and helper allowlist",
        failures,
    )

    cranelift = load_json(root, "spec/contracts/cranelift-backend-current.json")
    hir = load_json(root, "spec/contracts/hir-h1-current-mir-bridge.json")
    cranelift_guard = cranelift.get("internal_runtime_abi_guard", {})
    hir_guard = hir.get("internal_runtime_abi_contract", {})
    check(
        cranelift.get("required_receipt_inputs") == EXPECTED_RECEIPT_INPUTS
        and hir.get("native_projection_contract", {}).get(
            "required_receipt_inputs"
        )
        == EXPECTED_RECEIPT_INPUTS
        and len(EXPECTED_RECEIPT_INPUTS) == len(set(EXPECTED_RECEIPT_INPUTS)) == 22
        and cranelift_guard.get("contract") == CONTRACT
        and cranelift_guard.get("helper_registry") == REGISTRY
        and cranelift_guard.get("manifest_schema")
        == "deeplus.internal-runtime-abi-manifest/r1"
        and cranelift_guard.get("target_projection_schema")
        == "deeplus.internal-runtime-abi-target-projection/r1"
        and cranelift_guard.get("artifact_binding_receipt_schema")
        == "deeplus.internal-runtime-abi-artifact-binding-receipt/r1"
        and cranelift_guard.get("logical_abi_id") == TYPED_ABI_ID
        and cranelift_guard.get("dispatcher_completion_union")
        == ["COMPLETE(OutcomeTag)", "PARKED(ContinuationReceiptId)"]
        and cranelift_guard.get("active_base_runtime_helper_count") == 22
        and cranelift_guard.get("conditional_continuation_helper_count") == 6
        and cranelift_guard.get("conditional_managed_helper_count") == 3
        and cranelift_guard.get("parked_commits_outcome_or_successor") is False
        and cranelift_guard.get("parked_requires_exact_continuation_receipt")
        is True
        and cranelift_guard.get("active_conditional_managed_helper_count") == 3
        and cranelift_guard.get("managed_reference_profile_digest_or_null")
        == registry.get("managed_reference_profile_digest_or_null")
        and cranelift_guard.get("continuation_interface_digest_or_null")
        == registry.get("continuation_interface_digest_or_null")
        and cranelift_guard.get("dependency_binding_status") == "EXACT_LOCAL_FUSION_BOUND"
        and cranelift_guard.get("canonical_promotion_ready") is True
        and hir_guard.get("feature_id") == "internal_runtime_abi_r1"
        and hir_guard.get("contract") == CONTRACT
        and hir_guard.get("helper_registry") == REGISTRY
        and hir_guard.get("runtime_abi_id") == TYPED_ABI_ID
        and hir_guard.get("declared_base_runtime_helper_count") == 22
        and hir_guard.get("active_base_runtime_helper_count") == 22
        and hir_guard.get("conditional_continuation_helper_count") == 6
        and hir_guard.get("conditional_managed_helper_count") == 3
        and hir_guard.get("active_conditional_managed_helper_count") == 3
        and hir_guard.get("managed_reference_profile_digest_or_null")
        == registry.get("managed_reference_profile_digest_or_null")
        and hir_guard.get("continuation_interface_digest_or_null")
        == registry.get("continuation_interface_digest_or_null")
        and hir_guard.get("dependency_binding_status") == "EXACT_LOCAL_FUSION_BOUND"
        and hir_guard.get("canonical_promotion_ready") is True
        and hir_guard.get("product_support") == "NOT_RUN",
        "R37_HIR_CRANELIFT_BINDING",
        "exact ordered 22-input fused receipts and typed ABI guard parity",
        failures,
    )

    cases = fixtures.get("semantic_cases", [])
    classes = {name: sum(row.get("class") == name for row in cases) for name in ("positive", "boundary", "negative")}
    check(
        len(cases) == 31
        and len({row.get("case_id") for row in cases}) == 31
        and classes == {"positive": 8, "boundary": 8, "negative": 15}
        and all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in cases)
        and all(
            (row.get("class") == "negative")
            == (row.get("expected", {}).get("verdict") == "REJECT_STATIC")
            for row in cases
        ),
        "R37_SEMANTIC_31",
        f"cases={len(cases)} classes={classes}",
        failures,
    )

    mutations = fixtures.get("mutations", [])
    mutation_results = {
        row.get("operator"): mutation_oracle(row.get("operator", ""))
        for row in mutations
    }
    check(
        len(mutations) == 20
        and len({row.get("mutation_id") for row in mutations}) == 20
        and set(mutation_results) == set(EXPECTED_MUTATIONS)
        and all(
            mutation_results[row["operator"]]
            == row.get("expected_diagnostic")
            == EXPECTED_MUTATIONS[row["operator"]]
            for row in mutations
        ),
        "R37_MUTATION_20",
        f"rejected={sum(mutation_results[k] is not None for k in mutation_results)}/20",
        failures,
    )

    feature_rows = load_json(root, FEATURE_CHUNK)
    diagnostic_rows = load_json(root, DIAGNOSTIC_CHUNK)
    feature_row_schema = load_json(root, FEATURE_ROW_SCHEMA)
    diagnostic_row_schema = load_json(root, DIAGNOSTIC_ROW_SCHEMA)
    catalog_schema_errors = [
        *[
            f"feature[{index}]: {error}"
            for index, row in enumerate(feature_rows)
            for error in schema_errors(row, feature_row_schema, feature_row_schema)
        ],
        *[
            f"diagnostic[{index}]: {error}"
            for index, row in enumerate(diagnostic_rows)
            for error in schema_errors(
                row, diagnostic_row_schema, diagnostic_row_schema
            )
        ],
    ]
    internal_feature_rows = [
        row for row in feature_rows
        if row.get("feature_id") == "internal_runtime_abi_r1"
    ]
    check(
        contract.get("diagnostics") == DIAGNOSTICS
        and fixtures.get("expected_counts", {}).get("diagnostics")
        == len(DIAGNOSTICS)
        and len(internal_feature_rows) == 1
        and internal_feature_rows[0].get("authority_set")
        == ["LANGUAGE", "RUNTIME", "VERIFIER"]
        and "consumes the exact continuation and managed-reference digests"
        in internal_feature_rows[0].get("notes", "")
        and "does not canonically close IR-OWN-P0-017"
        in internal_feature_rows[0].get("notes", "")
        and [row.get("diagnostic_id") for row in diagnostic_rows]
        == DIAGNOSTICS
        and all(
            row.get("authority_set") == ["LANGUAGE", "VERIFIER"]
            and row.get("primary_source") == "spec/language.md"
            for row in diagnostic_rows
        )
        and not catalog_schema_errors,
        "R37_CATALOG_PRIORITY",
        (
            f"feature_rows={len(feature_rows)} internal_features={len(internal_feature_rows)} "
            f"diagnostics={len(diagnostic_rows)} "
            f"schema_errors={catalog_schema_errors[:3]}"
        ),
        failures,
    )
    deps = contract.get("dependencies", {})
    counts = contract.get("expected_counts", {})
    check(
        deps.get("managed_reference_profile_digest_or_null")
        == registry.get("managed_reference_profile_digest_or_null")
        and deps.get("continuation_interface_digest_or_null")
        == registry.get("continuation_interface_digest_or_null")
        and deps.get("dependency_binding_status") == "EXACT_LOCAL_FUSION_BOUND"
        and deps.get("canonical_promotion_ready") is True
        and counts.get("declared_base_helpers") == 22
        and counts.get("active_base_helpers") == 22
        and counts.get("conditional_continuation_helpers") == 6
        and counts.get("conditional_managed_helpers") == 3
        and counts.get("active_conditional_helpers") == 3
        and counts.get("semantic_p0") == 0
        and counts.get("open_feature_p1") == 22
        and counts.get("separate_actions_open") == 4
        and counts.get("product_lanes") == 15
        and counts.get("product_executed") == 0
        and fixtures.get("evidence_state", {}).get("product_execution") == "NOT_RUN",
        "R37_GOVERNANCE",
        "P0=0 P1=22 M13=4 product=15/15 NOT_RUN dependencies exact-bound",
        failures,
    )

    bound_artifacts = [
        "decisions/language/Design_Deeplus_Internal_Runtime_ABI_R1.md",
        "spec/mir/semantics.md",
        "spec/language.md",
        "spec/contracts/cranelift-backend-current.json",
        "spec/contracts/hir-h1-current-mir-bridge.json",
        "docs/grammar-reference/18-evaluation-ownership-mir-and-backends.md",
        "docs/tutorial/part-11-modules-system/11-05-hir-mir-backends-tooling.md",
    ]
    combined = "\n".join((root / rel).read_text(encoding="utf-8") for rel in bound_artifacts)
    check(
        all((root / rel).is_file() for rel in bound_artifacts)
        and "DEEPLUS_INTERNAL_RUNTIME_ABI_R1" in combined
        and "RUNTIME_ABI_HOST_UNWIND_FORBIDDEN" in combined,
        "R37_BOUND_ARTIFACTS",
        f"bound_artifacts={len(bound_artifacts)}",
        failures,
    )

    if failures:
        print("R37 INTERNAL RUNTIME ABI: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("R37 INTERNAL RUNTIME ABI: PASS")
    print(
        "checks=19 semantic_cases=31 mutations=20 declared_helpers=22 "
        "active_helpers=25 continuation_bound=6 managed_bound=3"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
