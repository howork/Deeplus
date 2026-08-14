#!/usr/bin/env python3
"""Generate the R99 runtime ABI, target, CLIF, and typed-XBC closure registries."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HELPERS = Path("spec/contracts/runtime-helper-registry-r1.json")
ABI = Path("spec/contracts/internal-runtime-abi-r1.json")
MACHINE = Path("spec/contracts/mir-machine-registry.json")
OUT_RECORDS = Path("spec/contracts/runtime-abi-record-registry-r99.json")
OUT_TARGETS = Path("spec/contracts/runtime-target-mapping-registry-r99.json")
OUT_CLIF = Path("spec/contracts/mir-clif-projection-registry-r99.json")
OUT_XBC = Path("spec/contracts/xbc-typed-payload-registry-r99.json")
OUT_XBC_FIXTURE = Path("tests/fixtures/current/xbc-decoded-module-r99.json")
XBC_MODULE_SCHEMA = Path("schemas/language/xvm-xbc-module-r1.schema.json")
XBC_PROJECTION = Path("spec/contracts/xvm-xbc-projection-r1.json")


ARGUMENT_SPECS: dict[str, list[tuple[str, str]]] = {
    "AWAIT_REPLY": [("reply_handle", "OPAQUE_RUNTIME_TOKEN"), ("continuation_handle", "MANAGED_HANDLE")],
    "DEQUEUE": [("actor_handle", "MANAGED_HANDLE")],
    "REPLY": [("reply_token", "OPAQUE_RUNTIME_TOKEN"), ("reply_payload", "AGGREGATE_SLOT")],
    "REQUEST": [("actor_handle", "MANAGED_HANDLE"), ("request_payload", "AGGREGATE_SLOT")],
    "SEND": [("actor_handle", "MANAGED_HANDLE"), ("message_payload", "AGGREGATE_SLOT")],
    "TURN_BEGIN": [("actor_handle", "MANAGED_HANDLE")],
    "TURN_END": [("turn_token", "OPAQUE_RUNTIME_TOKEN")],
    "CHECK": [("cancellation_context", "AGGREGATE_SLOT")],
    "FUNCTION_STATIC_ENSURE": [("once_cell_handle", "MANAGED_HANDLE")],
    "LAZY_FORCE": [("lazy_cell_handle", "MANAGED_HANDLE")],
    "DISPATCH": [("provider_slot", "AGGREGATE_SLOT"), ("provider_request", "AGGREGATE_SLOT")],
    "AWAIT": [("run_handle", "OPAQUE_RUNTIME_TOKEN")],
    "CANCEL_THEN_JOIN": [("run_handle", "OPAQUE_RUNTIME_TOKEN")],
    "EXIT": [("run_scope_token", "OPAQUE_RUNTIME_TOKEN")],
    "JOIN": [("run_group_handle", "OPAQUE_RUNTIME_TOKEN")],
    "SPAWN": [("spawn_plan", "AGGREGATE_SLOT")],
    "PARK": [("continuation_receipt", "OPAQUE_RUNTIME_TOKEN")],
    "LOCK_ACQUIRE": [("mutex_slot", "AGGREGATE_SLOT")],
    "LOCK_RELEASE": [("lock_token", "OPAQUE_RUNTIME_TOKEN")],
    "OBSERVE_BEGIN": [("shared_state_slot", "AGGREGATE_SLOT")],
    "OBSERVE_END": [("observation_token", "OPAQUE_RUNTIME_TOKEN")],
    "REPLACE_COMMIT": [("exclusive_place_slot", "AGGREGATE_SLOT"), ("replacement_value", "AGGREGATE_SLOT")],
    "MANAGED_ALLOCATE_SLOW": [("allocation_type_id", "TYPE_ID"), ("allocation_size_bytes", "USIZE")],
    "MANAGED_SAFEPOINT_ENTER": [("runtime_root_receipt", "AGGREGATE_SLOT")],
    "MANAGED_SAFEPOINT_LEAVE": [("safepoint_token", "OPAQUE_RUNTIME_TOKEN")],
}

NORMAL_PAYLOAD_TYPES = {
    "AWAIT_REPLY": "ActorReplyPayload",
    "DEQUEUE": "ActorMessageEnvelope",
    "REQUEST": "ReplyHandle",
    "TURN_BEGIN": "ActorTurnToken",
    "LAZY_FORCE": "LazyValue",
    "DISPATCH": "ProviderResult",
    "AWAIT": "RunOutcomeValue",
    "CANCEL_THEN_JOIN": "RunOutcomeValue",
    "JOIN": "RunOutcomeValue",
    "SPAWN": "RunHandle",
    "LOCK_ACQUIRE": "LockToken",
    "OBSERVE_BEGIN": "ObservationToken",
    "REPLACE_COMMIT": "ReplacedValue",
    "MANAGED_ALLOCATE_SLOW": "ManagedHandle",
    "MANAGED_SAFEPOINT_ENTER": "ManagedSafepointToken",
}

VALUE_FIELDS = {"condition_value_id", "discriminant_value_id", "environment_value_id"}
PLACE_FIELDS = {"place_id", "destination_place_id"}
BODY_FIELDS = {"closure_body_callable_id"}
FRAME_FIELDS = {"frame_id"}
STATIC_FIELDS = {
    "static_identity_id", "intrinsic_identity_id", "projection_identity_id",
    "context_adaptation_plan_id", "aggregate_kind_id", "variant_identity_id",
    "closure_environment_plan_id", "continuation_interface_identity",
    "continuation_frame_plan_id", "call_plan_id",
    "checked_semantic_operation_id", "leave_plan_id", "actor_plan_id",
    "provider_operation_identity_id", "once_identity_id", "run_plan_id",
    "sync_plan_id", "proof_id",
}
TOKEN_FIELDS = {
    "reservation_id", "loan_id", "parent_loan_id", "region_id",
    "cleanup_region_id", "cleanup_registration_id", "construction_id",
    "pattern_attempt_id", "closure_id", "committed_construction_id",
    "concur_id", "actor_envelope_id", "continuation_receipt_id_or_null",
    "epoch_id_or_null", "cleanup_token_id_or_null", "construction_session_id",
    "cancellation_id", "suspend_site_id", "suspension_point_id_or_null",
}
TOKEN_LIST_FIELDS = {
    "consumed_cleanup_token_ids", "produced_cleanup_token_ids",
    "consumed_owner_ids", "produced_owner_ids",
}
DIGEST_FIELDS = {"continuation_interface_digest", "partition_digest", "mask_digest_before", "mask_digest_after"}
ENUM_FIELDS = {
    "base_kind", "discharge_kind", "terminal_state_or_null", "frame_state_before",
    "frame_state_after", "epoch_state_before_or_null", "epoch_state_after_or_null",
    "phase_before", "phase_after", "outcome_edge", "run_operation",
    "actor_operation", "once_operation", "sync_operation", "completion_kind",
}
U32_FIELDS = {"stage_index"}

ENUM_VALUES: dict[str, tuple[str, ...]] = {
    "base_kind": ("PLACE", "VALUE"),
    "discharge_kind": ("ACTION_COMPLETED", "CONSTRUCTION_COMMITTED", "RESPONSIBILITY_REHOMED"),
    "terminal_state_or_null": ("TERMINAL_CANCELLED", "TERMINAL_COMPLETED", "TERMINAL_FAILED"),
    "frame_state_before": ("ABSENT", "CLEANING", "RUNNING", "SUSPENDED"),
    "frame_state_after": ("CLEANING", "RUNNING", "SUSPENDED", "TERMINAL_CANCELLED", "TERMINAL_COMPLETED", "TERMINAL_FAILED"),
    "epoch_state_before_or_null": ("CANCEL_WON", "COMMITTED", "PREPARING"),
    "epoch_state_after_or_null": ("CANCEL_WON", "COMMITTED", "DISCHARGED"),
    "phase_before": ("ALLOCATED", "PRE_DELEGATION", "BASE_INITIALIZING", "BASE_INITIALIZED", "STORAGE_INITIALIZING", "POST_INIT", "COMMIT_READY", "LIVE", "ABORTING", "FAILED_UNPUBLISHED"),
    "phase_after": ("ALLOCATED", "PRE_DELEGATION", "BASE_INITIALIZING", "BASE_INITIALIZED", "STORAGE_INITIALIZING", "POST_INIT", "COMMIT_READY", "LIVE", "ABORTING", "FAILED_UNPUBLISHED"),
    "outcome_edge": ("CANCELLATION", "DEFECT", "ERROR", "NORMAL"),
    "run_operation": ("AWAIT", "CANCEL_THEN_JOIN", "EXIT", "JOIN", "SPAWN"),
    "actor_operation": ("AWAIT_REPLY", "DEQUEUE", "REPLY", "REQUEST", "SEND", "TURN_BEGIN", "TURN_END"),
    "once_operation": ("FUNCTION_STATIC_ENSURE", "LAZY_FORCE"),
    "sync_operation": ("LOCK_ACQUIRE", "LOCK_RELEASE", "OBSERVE_BEGIN", "OBSERVE_END", "REPLACE_COMMIT"),
    "completion_kind": ("CANCELLATION", "DEFECT", "ERROR", "RETURN"),
    "winner_witness_or_null": ("CANCEL_WON", "RESUME_WON"),
}

GROUPED_HELPER_PREFIX = {
    "RUN_OP": "RuntimeHelperId:run.",
    "ACTOR_OP": "RuntimeHelperId:actor.",
    "ONCE_OP": "RuntimeHelperId:once.",
    "SYNC_OP": "RuntimeHelperId:sync.",
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def active_helpers(helper_doc: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [*helper_doc["helper_rows"], *helper_doc.get("conditional_extension_rows", [])]
    ids = [row["runtime_helper_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate active runtime helper identity")
    return rows


def _cbor_head(major: int, value: int) -> bytes:
    if value < 24:
        return bytes([(major << 5) | value])
    if value <= 0xFF:
        return bytes([(major << 5) | 24, value])
    if value <= 0xFFFF:
        return bytes([(major << 5) | 25]) + struct.pack(">H", value)
    if value <= 0xFFFFFFFF:
        return bytes([(major << 5) | 26]) + struct.pack(">I", value)
    return bytes([(major << 5) | 27]) + struct.pack(">Q", value)


def canonical_cbor(value: Any) -> bytes:
    """Encode the JSON value subset with RFC 8949 deterministic map ordering."""
    if value is None:
        return b"\xf6"
    if value is False:
        return b"\xf4"
    if value is True:
        return b"\xf5"
    if isinstance(value, int):
        return _cbor_head(0, value) if value >= 0 else _cbor_head(1, -1 - value)
    if isinstance(value, float):
        return b"\xfb" + struct.pack(">d", value)
    if isinstance(value, bytes):
        return _cbor_head(2, len(value)) + value
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return _cbor_head(3, len(encoded)) + encoded
    if isinstance(value, list):
        return _cbor_head(4, len(value)) + b"".join(canonical_cbor(item) for item in value)
    if isinstance(value, dict):
        rows = [(canonical_cbor(key), canonical_cbor(item)) for key, item in value.items()]
        rows.sort(key=lambda row: (len(row[0]), row[0]))
        return _cbor_head(5, len(rows)) + b"".join(key + item for key, item in rows)
    raise TypeError(f"unsupported deterministic CBOR value: {type(value)!r}")


def cbor_digest(value: Any) -> str:
    return hashlib.sha256(canonical_cbor(value)).hexdigest()


def dense_row(ordinal: int, source_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    material = {"ordinal": ordinal, "source_id": source_id, "payload": payload}
    return {"ordinal": ordinal, "source_id": source_id, "entry_digest": digest(material), "payload": payload}


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def record_registry(root: Path, helper_doc: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    helpers = active_helpers(helper_doc)
    for helper in helpers:
        operation = helper["operation"]
        specs = ARGUMENT_SPECS[operation]
        if len(specs) != len(helper["parameter_modes"]):
            raise ValueError(f"argument arity drift: {operation}")
        argument_fields = [
            {
                "ordinal": index,
                "field_name": name,
                "logical_value_kind": kind,
                "parameter_mode": helper["parameter_modes"][index],
                "address_class": helper["parameter_address_classes"][index],
            }
            for index, (name, kind) in enumerate(specs)
        ]
        argument_record = {
            "record_id": helper["arguments_record_id"],
            "record_role": "ARGUMENTS",
            "fields": argument_fields,
            "layout_policy": "DECLARED_ORDINAL_NO_PADDING_OR_HOST_LAYOUT_IDENTITY",
        }
        argument_record["record_digest"] = digest(argument_record)
        result_fields = [{
            "ordinal": 0,
            "field_name": "outcome_tag",
            "logical_value_kind": "U8",
            "semantic_type_id": "OutcomeTag",
            "initialization": "ALWAYS",
        }]
        next_ordinal = 1
        if helper["normal_result_kind"] != "UNIT":
            result_fields.append({
                "ordinal": next_ordinal,
                "field_name": "normal_payload",
                "logical_value_kind": helper["normal_result_kind"],
                "semantic_type_id": NORMAL_PAYLOAD_TYPES[operation],
                "initialization": "ONLY_WHEN_NORMAL",
            })
            next_ordinal += 1
        for outcome, field_name, type_id in (
            ("ERROR", "error_payload", "ErrorPayload"),
            ("DEFECT", "defect_payload", "DefectPayload"),
            ("CANCELLATION", "cancellation_payload", "CancellationPayload"),
        ):
            if outcome in helper["admitted_outcomes"]:
                result_fields.append({
                    "ordinal": next_ordinal,
                    "field_name": field_name,
                    "logical_value_kind": "AGGREGATE_SLOT",
                    "semantic_type_id": type_id,
                    "initialization": f"ONLY_WHEN_{outcome}",
                })
                next_ordinal += 1
        result_record = {
            "record_id": helper["result_record_id"],
            "record_role": "RESULT",
            "fields": result_fields,
            "layout_policy": "TAG_FIRST_EXACTLY_ONE_SELECTED_PAYLOAD_SLOT_INITIALIZED",
        }
        result_record["record_digest"] = digest(result_record)
        records.extend((argument_record, result_record))
        binding_material = {
            "runtime_helper_id": helper["runtime_helper_id"],
            "runtime_helper_signature_id": helper["runtime_helper_signature_id"],
            "helper_version": helper["helper_version"],
            "arguments_record_id": argument_record["record_id"],
            "arguments_record_digest": argument_record["record_digest"],
            "result_record_id": result_record["record_id"],
            "result_record_digest": result_record["record_digest"],
            "parameter_modes": helper["parameter_modes"],
            "parameter_address_classes": helper["parameter_address_classes"],
            "normal_result_kind": helper["normal_result_kind"],
            "admitted_outcomes": helper["admitted_outcomes"],
            "completion_modes": helper["completion_modes"],
            "may_block": helper["may_block"],
            "may_collect": helper["may_collect"],
            "may_suspend": helper["may_suspend"],
            "observes_cancellation": helper["observes_cancellation"],
        }
        bindings.append({**binding_material, "effective_signature_digest": digest(binding_material)})
    records.sort(key=lambda row: row["record_id"])
    bindings.sort(key=lambda row: row["runtime_helper_id"])
    value = {
        "schema": "deeplus.runtime-abi-record-registry/r99",
        "revision": "r99-runtime-record-and-signature-preimage-closure-r1",
        "status": "STABLE_DESIGN_LOCAL_CANDIDATE_PRODUCT_NOT_RUN",
        "gap_binding": "IR-OWN-P1-026_RUNTIME_RECORD_SUBCONDITION",
        "predecessor_helper_registry": HELPERS.as_posix(),
        "runtime_abi_id": helper_doc["runtime_abi_id"],
        "record_rows": records,
        "helper_bindings": bindings,
        "invariants": {
            "record_count": 50,
            "helper_binding_count": 25,
            "base_helper_count": len(helper_doc["helper_rows"]),
            "conditional_helper_count": len(helper_doc.get("conditional_extension_rows", [])),
            "active_helper_exact_set_bound": True,
            "record_id_unique": True,
            "field_order_is_abi_identity": True,
            "record_digest_in_effective_signature": True,
            "host_layout_is_semantic_identity": False,
            "product_execution": "NOT_RUN",
        },
    }
    value["registry_digest"] = digest(value)
    return value


def target_registry(
    root: Path,
    abi_doc: dict[str, Any],
    helper_doc: dict[str, Any],
    records_doc: dict[str, Any],
) -> dict[str, Any]:
    logical = [row["kind"] for row in abi_doc["logical_value_kinds"]]
    native = {
        "UNIT": "NO_VALUE", "BOOL": "CLIF_I8", "I8": "CLIF_I8", "U8": "CLIF_I8",
        "I16": "CLIF_I16", "U16": "CLIF_I16", "I32": "CLIF_I32", "U32": "CLIF_I32",
        "I64": "CLIF_I64", "U64": "CLIF_I64", "ISIZE": "CLIF_I64", "USIZE": "CLIF_I64",
        "I128": "CLIF_I64_PAIR_LOW_HIGH", "U128": "CLIF_I64_PAIR_LOW_HIGH",
        "F32": "CLIF_F32", "F64": "CLIF_F64", "MANAGED_HANDLE": "CLIF_I64_OPAQUE_HANDLE",
        "AGGREGATE_SLOT": "CLIF_I64_CALL_BOUNDED_ADDRESS", "TYPE_ID": "CLIF_I64_OPAQUE_ID",
        "OPAQUE_RUNTIME_TOKEN": "CLIF_I64_OPAQUE_TOKEN",
    }
    if set(logical) != set(native):
        raise ValueError("logical value kind drift")
    helpers = active_helpers(helper_doc)
    helper_ids = [row["runtime_helper_id"] for row in helpers]
    signature_by_helper = {
        row["runtime_helper_id"]: row["effective_signature_digest"]
        for row in records_doc["helper_bindings"]
    }
    helper_map_native = [
        {
            "runtime_helper_id": helper_id,
            "symbol": "__deeplus_rt_" + helper_id.split(":", 1)[1].replace(".", "_") + "_v1",
            "linkage": "IMPORT_EXACT",
            "effective_signature_digest": signature_by_helper[helper_id],
        }
        for helper_id in helper_ids
    ]
    projections = []
    for module_kind, target_triple, calling_convention in (
        ("Xvm", "deeplus-xvm-portable-r1", "DEEPLUS_XVM_LOGICAL_R1"),
        ("ObjectAot", "x86_64-pc-windows-msvc", "DEEPLUS_INTERNAL_WINDOWS_X64_R1"),
        ("InMemoryJit", "x86_64-pc-windows-msvc", "DEEPLUS_INTERNAL_WINDOWS_X64_R1"),
    ):
        scalar_rows = [
            {"logical_value_kind": kind, "target_carrier": ("XBC_SLOT_" + kind if kind != "UNIT" else "NO_VALUE")}
            for kind in logical
        ] if module_kind == "Xvm" else [
            {"logical_value_kind": kind, "target_carrier": native[kind]} for kind in logical
        ]
        helper_rows = [
            {
                "runtime_helper_id": helper_id,
                "table_ordinal": index,
                "effective_signature_digest": signature_by_helper[helper_id],
            }
            for index, helper_id in enumerate(helper_ids)
        ] if module_kind == "Xvm" else helper_map_native
        mapping = {
            "projection_id": f"RuntimeTargetMappingId:{module_kind}/r99",
            "module_kind": module_kind,
            "target_triple": target_triple,
            "pointer_width": 64,
            "endianness": "LITTLE",
            "calling_convention": calling_convention,
            "scalar_mapping_rows": scalar_rows,
            "indirect_slot_mapping": {
                "argument": "CALL_BOUNDED_ADDRESS_TO_CALLER_STORAGE",
                "result": "CALLER_ALLOCATED_SRET_SLOT",
                "callee_retention": "FORBIDDEN_AFTER_RETURN_OR_PARK_TRANSFER",
            },
            "outcome_mapping_rows": abi_doc["outcome_channel"]["tags"],
            "helper_mapping_rows": helper_rows,
            "host_default_count": 0,
            "target_location_is_semantic_identity": False,
        }
        projections.append({**mapping, "mapping_digest": digest(mapping)})
    value = {
        "schema": "deeplus.runtime-target-mapping-registry/r99",
        "revision": "r99-runtime-target-preimage-closure-r1",
        "status": "STABLE_DESIGN_LOCAL_CANDIDATE_PRODUCT_NOT_RUN",
        "gap_binding": "IR-OWN-P1-026_TARGET_MAPPING_SUBCONDITION",
        "predecessor_projection_schema": "schemas/language/internal-runtime-target-projection-r1.schema.json",
        "target_mappings": projections,
        "toolchain_lock": {
            "rust_version": "1.85.0",
            "cargo_lock_sha256": file_digest(root / "Cargo.lock"),
            "cranelift_dependency_connected": False,
            "required_before_native_product_execution": True,
            "product_execution": "NOT_RUN",
        },
        "invariants": {
            "mapping_count": 3,
            "logical_value_kind_count_per_mapping": 20,
            "helper_mapping_count_per_mapping": 25,
            "active_helper_exact_set_bound": True,
            "aot_jit_logical_mapping_equal": True,
            "mapping_digest_has_local_preimage": True,
            "placeholder_digest_count": 0,
        },
    }
    value["registry_digest"] = digest(value)
    return value


def field_domain(field: str) -> str:
    if field == "constant_id":
        return "CONSTANT_ORDINAL"
    if field in VALUE_FIELDS:
        return "VALUE_ORDINAL"
    if field in PLACE_FIELDS:
        return "PLACE_ORDINAL"
    if field in BODY_FIELDS:
        return "BODY_ORDINAL"
    if field in FRAME_FIELDS:
        return "CONTINUATION_FRAME_SLOT_ORDINAL"
    if field in STATIC_FIELDS or field == "hir_provenance":
        return "STATIC_IDENTITY_ORDINAL"
    if field in TOKEN_FIELDS:
        return "LINEAR_TOKEN_ORDINAL_OR_NULL" if field.endswith("_or_null") else "LINEAR_TOKEN_ORDINAL"
    if field in TOKEN_LIST_FIELDS:
        return "LINEAR_TOKEN_ORDINAL_LIST"
    if field in DIGEST_FIELDS:
        return "SHA256_BYTES"
    if field in ENUM_FIELDS or field == "winner_witness_or_null":
        return "CLOSED_ENUM_VALUE_OR_NULL" if field.endswith("_or_null") else "CLOSED_ENUM_VALUE"
    if field in U32_FIELDS:
        return "U32"
    if field == "capture_field_ids_in_source_order":
        return "STATIC_IDENTITY_ORDINAL_LIST"
    if field == "base_id":
        return "BASE_KIND_DISCRIMINATED_PLACE_OR_VALUE_ORDINAL"
    raise ValueError(f"unclassified MIR payload field: {field}")


def field_contract(field: str) -> dict[str, Any]:
    row: dict[str, Any] = {"field_name": field, "domain": field_domain(field)}
    if field in ENUM_VALUES:
        row["closed_values"] = list(ENUM_VALUES[field])
    return row


def xbc_registry(machine: dict[str, Any]) -> dict[str, Any]:
    fields = sorted({field for row in [*machine["semantic_operations"], *machine["terminators"]] for field in row["payload_contract"]["required_fields"]})
    field_rows = [field_contract(field) for field in fields]
    operations = []
    for ordinal, row in enumerate(machine["semantic_operations"]):
        operations.append({
            "opcode": ordinal,
            "operation_kind": row["operation_kind"],
            "payload_contract_id": f"XbcPayloadContractId:operation.{row['operation_kind']}/r99",
            "required_fields": [
                field_contract(field)
                for field in row["payload_contract"]["required_fields"]
            ],
            "additional_fields": False,
        })
    terminators = []
    for ordinal, row in enumerate(machine["terminators"]):
        terminators.append({
            "opcode": 32768 + ordinal,
            "terminator_kind": row["terminator_kind"],
            "payload_contract_id": f"XbcPayloadContractId:terminator.{row['terminator_kind']}/r99",
            "required_fields": [
                field_contract(field)
                for field in row["payload_contract"]["required_fields"]
            ],
            "additional_fields": False,
        })
    value = {
        "schema": "deeplus.xbc-typed-payload-registry/r99",
        "revision": "r99-xbc-typed-payload-closure-r1",
        "status": "STABLE_DESIGN_LOCAL_CANDIDATE_PRODUCT_NOT_RUN",
        "gap_binding": "IR-XVM-P1-062_TYPED_PAYLOAD_SUBCONDITION",
        "machine_registry": MACHINE.as_posix(),
        "field_domain_rows": field_rows,
        "operation_rows": operations,
        "terminator_rows": terminators,
        "invariants": {
            "field_domain_count": 73,
            "operation_row_count": 48,
            "terminator_row_count": 17,
            "opcode_kind_bijection": True,
            "wrong_kind_same_opcode_rejected": True,
            "wrong_namespace_same_ordinal_rejected": True,
            "ordinal_must_be_in_exact_namespace_bounds": True,
            "closed_enum_membership_required": True,
            "nonnull_mir_id_field_count": len([field for field in fields if field in TOKEN_FIELDS and not field.endswith("_or_null")]),
            "payload_additional_field_count": 0,
            "product_execution": "NOT_RUN",
        },
    }
    value["registry_digest"] = digest(value)
    return value


def clif_registry(
    machine: dict[str, Any],
    helper_doc: dict[str, Any],
    records_doc: dict[str, Any],
) -> dict[str, Any]:
    verifier_only = {"MOVE_RESERVE", "MOVE_CANCEL", "LOAN_BEGIN_SHARED", "LOAN_BEGIN_EXCLUSIVE", "LOAN_BEGIN_REBORROW", "LOAN_END"}
    memory = {"PLACE_LOAD", "PLACE_STORE_INIT", "PLACE_MOVE"}
    control = {"BR", "COND_BR", "SWITCH_ENUM", "SWITCH_INT", "COMPLETE", "UNREACHABLE_PROVEN"}
    helper_selector = {
        "SUSPEND": "RuntimeHelperId:suspension.park",
        "CANCEL_CHECK": "RuntimeHelperId:cancellation.check",
        "PROVIDER_OP": "RuntimeHelperId:provider.dispatch",
    }
    helper_by_operation = {row["operation"]: row for row in active_helpers(helper_doc)}
    effective_by_helper = {
        row["runtime_helper_id"]: row["effective_signature_digest"]
        for row in records_doc["helper_bindings"]
    }
    grouped_dispatch = {
        terminator: [
            {
                "payload_operation": operation,
                "runtime_helper_id": helper_by_operation[operation]["runtime_helper_id"],
                "runtime_helper_signature_id": helper_by_operation[operation]["runtime_helper_signature_id"],
                "arguments_record_id": helper_by_operation[operation]["arguments_record_id"],
                "result_record_id": helper_by_operation[operation]["result_record_id"],
                "effective_signature_digest": effective_by_helper[helper_by_operation[operation]["runtime_helper_id"]],
            }
            for operation in ENUM_VALUES[field]
        ]
        for terminator, field in (
            ("RUN_OP", "run_operation"),
            ("ACTOR_OP", "actor_operation"),
            ("ONCE_OP", "once_operation"),
            ("SYNC_OP", "sync_operation"),
        )
    }
    instruction_families = {
        "CONST": "TYPE_DIRECTED_ICONST_FCONST_OR_VCONST",
        "STATIC_REF": "GLOBAL_VALUE_OR_EXACT_IMPORT_REFERENCE",
        "PURE_INTRINSIC": "SEALED_INTRINSIC_TABLE_SEQUENCE",
        "TOTAL_PROJECTION": "TYPE_DIRECTED_EXTRACT_EXTEND_TRUNCATE_OR_BITCAST",
        "CONTEXT_ADAPT": "VERIFIED_ADAPTATION_PLAN_SEQUENCE",
        "AGGREGATE_INJECT": "ORDERED_AGGREGATE_SLOT_INITIALIZATION",
        "AGGREGATE_ASSEMBLE": "ORDERED_AGGREGATE_SLOT_INITIALIZATION",
        "PLACE_LOAD": "CLIF_LOAD_FROM_VERIFIED_PLACE",
        "PLACE_STORE_INIT": "CLIF_STORE_TO_UNINITIALIZED_VERIFIED_PLACE",
        "PLACE_MOVE": "CLIF_LOAD_THEN_MARK_SOURCE_UNINITIALIZED",
        "CLEANUP_REGION_ENTER": "CLEANUP_LADDER_STATE_ENTER",
        "CLEANUP_REGISTER": "CLEANUP_LADDER_REGISTER_ACTION",
        "CLEANUP_PIN": "CLEANUP_LADDER_PIN_ACTION",
        "CLEANUP_SEAL": "CLEANUP_LADDER_SEAL_ACTION",
        "CLEANUP_DISARM": "CLEANUP_LADDER_DISARM_ACTION",
        "BUILDER_BEGIN": "STAGED_RESULT_STORAGE_BEGIN",
        "BUILDER_STAGE": "STAGED_RESULT_STORAGE_WRITE",
        "BUILDER_COMMIT": "STAGED_RESULT_SINGLE_PUBLICATION",
        "PATTERN_PROBE": "NONCOMMITTING_COMPARE_AND_PROJECTION_SEQUENCE",
        "BINDING_COMMIT": "ORDERED_BINDING_SINGLE_COMMIT",
        "CLOSURE_MAKE": "SEALED_ENVIRONMENT_PLAN_MATERIALIZATION",
        "CONCUR_ENTER": "SEALED_CONCUR_REGION_ENTRY_SEQUENCE",
        "ACTOR_ENVELOPE_PREPARE": "PRECOMMIT_ACTOR_ENVELOPE_MATERIALIZATION",
        "FRAME_CREATE": "CONTINUATION_FRAME_RUNTIME_SEQUENCE",
        "FRAME_SUSPEND_COMMIT": "CONTINUATION_FRAME_RUNTIME_SEQUENCE",
        "FRAME_RESUME_COMMIT": "CONTINUATION_FRAME_RUNTIME_SEQUENCE",
        "FRAME_CANCEL_COMMIT": "CONTINUATION_FRAME_RUNTIME_SEQUENCE",
        "FRAME_CLEANUP_STEP": "CONTINUATION_FRAME_RUNTIME_SEQUENCE",
        "FRAME_TERMINATE": "CONTINUATION_FRAME_RUNTIME_SEQUENCE",
    }
    for kind in verifier_only:
        instruction_families[kind] = "VERIFIER_STATE_ONLY_NO_CLIF_INSTRUCTION"
    for kind in {
        "OBJECT_CONSTRUCTION_BEGIN", "BASE_SEGMENT_BEGIN", "BASE_SEGMENT_COMMIT",
        "FIELD_INIT_COMMIT", "CONSTRUCTION_FIELD_MOVE_TRANSFER",
        "CONSTRUCTION_POST_INIT_GUARD", "OBJECT_CONSTRUCTION_COMMIT",
        "OBJECT_CONSTRUCTION_ABORT", "OBJECT_CLEANUP_BEGIN", "OBJECT_CLEANUP_HOOK",
        "OBJECT_FIELD_CLEANUP", "OBJECT_BASE_CLEANUP", "OBJECT_CLEANUP_END",
    }:
        instruction_families[kind] = "OBJECT_CONSTRUCTION_MASK_AND_CLEANUP_LADDER_SEQUENCE"
    terminator_families = {
        "BR": "CLIF_JUMP", "COND_BR": "CLIF_BRIF",
        "SWITCH_ENUM": "CLIF_BR_TABLE_FROM_SEALED_VARIANT_DISCRIMINANT",
        "SWITCH_INT": "CLIF_BR_TABLE_OR_ORDERED_COMPARE_TREE",
        "INVOKE": "CLIF_CALL_OR_CALL_INDIRECT_THEN_EXPLICIT_OUTCOME_BRANCH",
        "CHECKED": "CHECKED_VALUE_OR_PRESELECTED_DEFECT_BRANCH",
        "PLACE_REPLACE": "STAGED_PLACE_REPLACE_SINGLE_COMMIT_BRANCH",
        "LEAVE": "CLEANUP_LADDER_THEN_JUMP",
        "SUSPEND": "RUNTIME_HELPER_CALL_THEN_PARKED_OR_OUTCOME_BRANCH",
        "CANCEL_CHECK": "RUNTIME_HELPER_CALL_THEN_CANCELLATION_BRANCH",
        "RUN_OP": "SEALED_RUNTIME_HELPER_CALL_THEN_COMPLETION_BRANCH",
        "ACTOR_OP": "SEALED_RUNTIME_HELPER_CALL_THEN_COMPLETION_BRANCH",
        "PROVIDER_OP": "SEALED_RUNTIME_HELPER_CALL_THEN_COMPLETION_BRANCH",
        "ONCE_OP": "SEALED_RUNTIME_HELPER_CALL_THEN_COMPLETION_BRANCH",
        "SYNC_OP": "SEALED_RUNTIME_HELPER_CALL_THEN_COMPLETION_BRANCH",
        "COMPLETE": "RETURN_EXACT_OUTCOME_TAG_AND_SELECTED_PAYLOAD",
        "UNREACHABLE_PROVEN": "TRAP_ONLY_WITH_VERIFIED_PROOF_ID",
    }
    operation_rows = []
    for row in machine["semantic_operations"]:
        kind = row["operation_kind"]
        projection_class = "VERIFIER_ONLY_NO_CLIF_EMISSION" if kind in verifier_only else "CLIF_MEMORY_TEMPLATE" if kind in memory else "CLIF_SEALED_TEMPLATE"
        sequence = ["VERIFY_EXACT_TYPED_PAYLOAD"]
        if projection_class != "VERIFIER_ONLY_NO_CLIF_EMISSION":
            sequence += ["READ_INPUTS_ONCE_IN_MIR_ORDER", f"EMIT_TEMPLATE:{kind}", "BIND_OUTPUTS_ONCE_IN_MIR_ORDER"]
        sequence.append("PRESERVE_EXPLICIT_OUTCOME_CLEANUP_AND_ROOT_EDGES")
        operation_rows.append({
            "mir_kind": kind,
            "projection_class": projection_class,
            "template_id": f"ClifTemplateId:{kind}/r99",
            "clif_instruction_family": instruction_families[kind],
            "ordered_steps": sequence,
            "runtime_helper_selector_or_null": None,
            "missing_capability": "REJECT_BEFORE_CLIF_EMISSION",
        })
    terminator_rows = []
    for row in machine["terminators"]:
        kind = row["terminator_kind"]
        selector = helper_selector.get(kind)
        dispatch_rows = grouped_dispatch.get(kind, [])
        terminator_rows.append({
            "mir_kind": kind,
            "projection_class": "CLIF_CONTROL_TEMPLATE" if kind in control else "CLIF_RUNTIME_OR_CALL_TEMPLATE",
            "template_id": f"ClifTemplateId:terminator.{kind}/r99",
            "clif_instruction_family": terminator_families[kind],
            "ordered_steps": [
                "VERIFY_EXACT_TYPED_PAYLOAD_AND_SUCCESSOR_ARITY",
                "READ_INPUTS_ONCE_IN_MIR_ORDER",
                (
                    f"SELECT_HELPER_FROM_EXACT_{kind}_PAYLOAD_MAP_THEN_CALL"
                    if dispatch_rows else
                    (f"CALL_HELPER:{selector}" if selector else f"EMIT_TERMINATOR_TEMPLATE:{kind}")
                ),
                "COMMIT_EXACTLY_ONE_SEALED_SUCCESSOR_OR_TERMINAL_OUTCOME",
            ],
            "runtime_helper_selector_or_null": selector,
            "runtime_helper_dispatch_rows": dispatch_rows,
            "missing_capability": "REJECT_BEFORE_CLIF_EMISSION",
        })
    value = {
        "schema": "deeplus.mir-clif-projection-registry/r99",
        "revision": "r99-total-mir-clif-projection-closure-r1",
        "status": "STABLE_DESIGN_LOCAL_CANDIDATE_PRODUCT_NOT_RUN",
        "gap_id": "IR-BACKEND-P1-073",
        "semantic_authority": "Verified<DeeplusMirR1>",
        "operation_rows": operation_rows,
        "terminator_rows": terminator_rows,
        "global_invariants": {
            "operation_row_count": 48,
            "terminator_row_count": 17,
            "missing_or_duplicate_row_count": 0,
            "semantic_reselection_count": 0,
            "host_unwind_as_outcome_count": 0,
            "trap_substitution_for_error_or_cancellation_count": 0,
            "object_aot_and_jit_share_registry": True,
            "clif_or_address_is_semantic_identity": False,
            "grouped_runtime_helper_dispatch_count": sum(len(rows) for rows in grouped_dispatch.values()),
            "runtime_helper_placeholder_count": 0,
            "product_execution": "NOT_RUN",
        },
    }
    value["registry_digest"] = digest(value)
    return value


def xbc_decoded_fixture(
    root: Path,
    typed_registry: dict[str, Any],
    target_registry_doc: dict[str, Any],
) -> dict[str, Any]:
    section_kinds = [
        "MODULE_DESCRIPTOR", "TYPE_TABLE", "STATIC_IDENTITY_TABLE",
        "RESPONSIBILITY_EVIDENCE_TABLE", "CONSTANT_TABLE",
        "CLOSURE_ENVIRONMENT_PLAN_TABLE", "BODY_TABLE", "MANAGED_MEMORY_PLAN",
        "CONTINUATION_INTERFACE", "DEBUG_PROVENANCE",
    ]
    token_row = dense_row(0, "ConstructionId:fixture/r99", {"kind": "CONSTRUCTION_TOKEN"})
    static_rows = [
        dense_row(0, "ContinuationInterfaceId:fixture/r99", {"kind": "CONTINUATION_INTERFACE"}),
        dense_row(1, "ContinuationFramePlanId:fixture/r99", {"kind": "FRAME_PLAN"}),
        dense_row(2, "HirOriginId:fixture/r99", {"kind": "HIR_PROVENANCE"}),
    ]
    frame_rows = [dense_row(0, "ContinuationFrameSlotId:fixture/r99", {"kind": "FRAME_SLOT"})]
    source_mir = {
        "schema": "deeplus.mir/r1",
        "body_id": "BodyId:r99-fixture",
        "blocks": [
            {
                "block_id": "BlockId:r99-fixture-entry",
                "operations": [
                    {"kind": "BUILDER_STAGE", "construction_id": "ConstructionId:fixture/r99", "stage_index": 0},
                    {
                        "kind": "FRAME_RESUME_COMMIT",
                        "continuation_interface_identity": "ContinuationInterfaceId:fixture/r99",
                        "continuation_frame_plan_id": "ContinuationFramePlanId:fixture/r99",
                        "frame_id": "ContinuationFrameSlotId:fixture/r99",
                        "winner_witness_or_null": "RESUME_WON",
                        "hir_provenance": "HirOriginId:fixture/r99",
                    },
                ],
                "terminator": {"kind": "COMPLETE", "completion_kind": "RETURN"},
            }
        ],
    }
    source_mir_digest = digest(source_mir)
    module = {
        "schema": "deeplus.xvm-xbc-module/r1",
        "header": {
            "magic_hex": "4450584243000d0a", "major": 1, "minor": 0,
            "flags": 0, "section_count": 10, "directory_bytes": 560,
            "payload_bytes": 0, "source_mir_semantic_digest": source_mir_digest,
            "xbc_logical_digest": "PENDING", "contract_digest": typed_registry["registry_digest"],
        },
        "directory": [
            {"kind": kind, "ordinal": index, "flags": 0, "offset": 0,
             "length": 0, "payload_sha256": "PENDING"}
            for index, kind in enumerate(section_kinds)
        ],
        "module_descriptor": {
            "mir_schema_id": "deeplus.mir/r1", "mir_schema_digest": file_digest(root / "schemas/language/deeplus-mir.schema.json"),
            "mir_machine_registry_id": "deeplus.mir-machine-registry/r1",
            "mir_machine_registry_digest": file_digest(root / MACHINE), "source_mir_semantic_digest": source_mir_digest,
            "feature_profile_id": "FeatureProfileId:r99-fixture",
            "feature_profile_digest": digest({"feature_profile_id": "FeatureProfileId:r99-fixture"}),
            "runtime_abi_id": "RuntimeAbiId:DEEPLUS_INTERNAL_RUNTIME_ABI_R1",
            "runtime_abi_digest": file_digest(root / ABI), "runtime_projection_digest": target_registry_doc["registry_digest"],
            "managed_memory_plan_digest_or_null": None,
            "continuation_interface_digest_or_null": None,
            "projection_capability_id": "PROJ-CAP-XVM-CANONICAL-XBC-R1",
        },
        "type_table": [], "static_identity_table": static_rows,
        "responsibility_evidence_table": [], "constant_table": [],
        "closure_environment_plan_table": [],
        "body_table": [{
            "ordinal": 0, "source_body_id": "BodyId:r99-fixture",
            "entry_block_ordinal": 0, "value_slots": [], "place_slots": [],
            "linear_token_slots": [token_row], "continuation_frame_slots": frame_rows,
            "blocks": [{
                "ordinal": 0, "source_block_id": "BlockId:r99-fixture-entry",
                "parameter_slots": [],
                "instructions": [{
                    "ordinal": 0, "opcode": 22, "operation_kind": "BUILDER_STAGE",
                    "payload_contract_id": "XbcPayloadContractId:operation.BUILDER_STAGE/r99",
                    "inputs": [], "outputs": [],
                    "payload": {"construction_id": {"namespace": "LINEAR_TOKEN", "ordinal": 0}, "stage_index": 0},
                }, {
                    "ordinal": 1, "opcode": 31, "operation_kind": "FRAME_RESUME_COMMIT",
                    "payload_contract_id": "XbcPayloadContractId:operation.FRAME_RESUME_COMMIT/r99",
                    "inputs": [], "outputs": [],
                    "payload": {
                        "continuation_interface_identity": {"namespace": "STATIC_IDENTITY", "ordinal": 0},
                        "continuation_interface_digest": digest({"id": "ContinuationInterfaceId:fixture/r99"}),
                        "continuation_receipt_id_or_null": {"namespace": "LINEAR_TOKEN", "ordinal": 0},
                        "continuation_frame_plan_id": {"namespace": "STATIC_IDENTITY", "ordinal": 1},
                        "frame_id": {"namespace": "CONTINUATION_FRAME_SLOT", "ordinal": 0},
                        "suspension_point_id_or_null": {"namespace": "LINEAR_TOKEN", "ordinal": 0},
                        "epoch_id_or_null": {"namespace": "LINEAR_TOKEN", "ordinal": 0},
                        "partition_digest": digest({"partition": "fixture"}),
                        "cleanup_token_id_or_null": None,
                        "terminal_state_or_null": None,
                        "frame_state_before": "SUSPENDED",
                        "frame_state_after": "RUNNING",
                        "epoch_state_before_or_null": "COMMITTED",
                        "epoch_state_after_or_null": "DISCHARGED",
                        "winner_witness_or_null": "RESUME_WON",
                        "hir_provenance": {"namespace": "STATIC_IDENTITY", "ordinal": 2},
                    },
                }],
                "terminator": {
                    "opcode": 32783, "terminator_kind": "COMPLETE",
                    "payload_contract_id": "XbcPayloadContractId:terminator.COMPLETE/r99",
                    "inputs": [], "successors": [], "payload": {"completion_kind": "RETURN"},
                },
            }],
            "body_projection_digest": "PENDING",
        }],
        "managed_memory_plan": {"present": False, "semantic_digest_or_null": None, "payload": None},
        "continuation_interface": {"present": False, "semantic_digest_or_null": None, "payload": None},
        "debug_provenance": {"source_origin_rows": [], "path_is_semantic_identity": False, "provenance_digest": digest([])},
    }
    section_values = [
        module["module_descriptor"], module["type_table"], module["static_identity_table"],
        module["responsibility_evidence_table"], module["constant_table"],
        module["closure_environment_plan_table"], module["body_table"],
        module["managed_memory_plan"], module["continuation_interface"], module["debug_provenance"],
    ]
    module["body_table"][0]["body_projection_digest"] = digest({
        key: value for key, value in module["body_table"][0].items() if key != "body_projection_digest"
    })
    section_values[6] = module["body_table"]
    offset = 128 + 10 * 56
    logical_rows = []
    for entry, value in zip(module["directory"], section_values):
        encoded = canonical_cbor(value)
        entry.update({"offset": offset, "length": len(encoded), "payload_sha256": hashlib.sha256(encoded).hexdigest()})
        logical_rows.append({"kind": entry["kind"], "payload_sha256": entry["payload_sha256"]})
        offset += len(encoded)
    module["header"]["payload_bytes"] = offset - (128 + 10 * 56)
    module["header"]["xbc_logical_digest"] = cbor_digest(logical_rows)
    return {
        "schema": "deeplus.xbc-decoded-module-fixture/r99",
        "typed_payload_registry": OUT_XBC.as_posix(),
        "typed_payload_registry_digest": typed_registry["registry_digest"],
        "module_schema": XBC_MODULE_SCHEMA.as_posix(),
        "module_schema_digest": file_digest(root / XBC_MODULE_SCHEMA),
        "projection_contract": XBC_PROJECTION.as_posix(),
        "source_mir_fixture": source_mir,
        "source_mir_semantic_digest": source_mir_digest,
        "decoded_module": module,
        "expected": "ADMIT_STATIC_DECODED_MODULE",
        "product_execution": "NOT_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    helper_doc = load(root / HELPERS)
    abi_doc = load(root / ABI)
    machine = load(root / MACHINE)
    typed_registry = xbc_registry(machine)
    records = record_registry(root, helper_doc)
    targets = target_registry(root, abi_doc, helper_doc, records)
    outputs = {
        OUT_RECORDS: records,
        OUT_TARGETS: targets,
        OUT_CLIF: clif_registry(machine, helper_doc, records),
        OUT_XBC: typed_registry,
        OUT_XBC_FIXTURE: xbc_decoded_fixture(root, typed_registry, targets),
    }
    pending = []
    for relative, value in outputs.items():
        path = root / relative
        expected = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            pending.append(relative.as_posix())
            if not args.check:
                write(path, value)
    mode = "CHECK" if args.check else "WRITE"
    print(f"R99_RUNTIME_BACKEND_REBIND_{mode}: outputs={len(outputs)} pending={len(pending)}")
    if args.check and pending:
        for item in pending:
            print(item)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
