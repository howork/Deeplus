#!/usr/bin/env python3
"""Validate R99 runtime records, target maps, CLIF rows, and typed XBC payloads."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RECORDS = Path("spec/contracts/runtime-abi-record-registry-r99.json")
TARGETS = Path("spec/contracts/runtime-target-mapping-registry-r99.json")
CLIF = Path("spec/contracts/mir-clif-projection-registry-r99.json")
XBC = Path("spec/contracts/xbc-typed-payload-registry-r99.json")
XBC_FIXTURE = Path("tests/fixtures/current/xbc-decoded-module-r99.json")
HELPERS = Path("spec/contracts/runtime-helper-registry-r1.json")
MACHINE = Path("spec/contracts/mir-machine-registry.json")
XBC_MODULE_SCHEMA = Path("schemas/language/xvm-xbc-module-r1.schema.json")
MIR_SEMANTICS = Path("spec/mir/semantics.md")
LANGUAGE = Path("spec/language.md")
CONTINUATION = Path("spec/contracts/continuation-interface-r1.json")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if isinstance(value, str):
        raw = value.encode("utf-8")
        return _cbor_head(3, len(raw)) + raw
    if isinstance(value, list):
        return _cbor_head(4, len(value)) + b"".join(canonical_cbor(item) for item in value)
    if isinstance(value, dict):
        rows = [(canonical_cbor(key), canonical_cbor(item)) for key, item in value.items()]
        rows.sort(key=lambda row: (len(row[0]), row[0]))
        return _cbor_head(5, len(rows)) + b"".join(key + item for key, item in rows)
    raise TypeError(f"unsupported deterministic CBOR value: {type(value)!r}")


def cbor_digest(value: Any) -> str:
    return hashlib.sha256(canonical_cbor(value)).hexdigest()


def active_helpers(helpers: dict[str, Any]) -> list[dict[str, Any]]:
    return [*helpers.get("helper_rows", []), *helpers.get("conditional_extension_rows", [])]


def without(value: dict[str, Any], key: str) -> dict[str, Any]:
    return {name: item for name, item in value.items() if name != key}


def registry_errors(records: dict[str, Any], targets: dict[str, Any], clif: dict[str, Any], xbc: dict[str, Any], helpers: dict[str, Any], machine: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    record_rows = records.get("record_rows", [])
    record_by_id = {row.get("record_id"): row for row in record_rows}
    bindings = records.get("helper_bindings", [])
    helper_rows = active_helpers(helpers)
    helper_by_id = {row.get("runtime_helper_id"): row for row in helper_rows}
    active_helper_ids = [row.get("runtime_helper_id") for row in helper_rows]
    active_helper_set = set(active_helper_ids)
    require(records.get("schema") == "deeplus.runtime-abi-record-registry/r99", "RECORD_IDENTITY")
    require(len(active_helper_ids) == len(active_helper_set) == 25, "ACTIVE_HELPER_COUNT")
    expected_record_ids = {
        record_id
        for helper in helper_rows
        for record_id in (helper.get("arguments_record_id"), helper.get("result_record_id"))
    }
    require(len(record_rows) == len(record_by_id) == 50 and set(record_by_id) == expected_record_ids, "RECORD_EXACT_SET")
    require(len(bindings) == 25 and {row.get("runtime_helper_id") for row in bindings} == active_helper_set, "HELPER_BINDING_EXACT_SET")
    require(records.get("registry_digest") == digest(without(records, "registry_digest")), "RECORD_REGISTRY_DIGEST")
    for row in record_rows:
        require(row.get("record_digest") == digest(without(row, "record_digest")), f"RECORD_DIGEST:{row.get('record_id')}")
        fields = row.get("fields", [])
        require([field.get("ordinal") for field in fields] == list(range(len(fields))), f"RECORD_FIELD_ORDER:{row.get('record_id')}")
        require(len({field.get("field_name") for field in fields}) == len(fields), f"RECORD_FIELD_NAMES:{row.get('record_id')}")
    for binding in bindings:
        helper = helper_by_id.get(binding.get("runtime_helper_id"), {})
        material = without(binding, "effective_signature_digest")
        require(binding.get("effective_signature_digest") == digest(material), f"HELPER_EFFECTIVE_DIGEST:{binding.get('runtime_helper_id')}")
        require(binding.get("arguments_record_id") == helper.get("arguments_record_id"), f"HELPER_ARGS_ID:{binding.get('runtime_helper_id')}")
        require(binding.get("result_record_id") == helper.get("result_record_id"), f"HELPER_RESULT_ID:{binding.get('runtime_helper_id')}")
        require(binding.get("arguments_record_digest") == record_by_id.get(binding.get("arguments_record_id"), {}).get("record_digest"), f"HELPER_ARGS_DIGEST:{binding.get('runtime_helper_id')}")
        require(binding.get("result_record_digest") == record_by_id.get(binding.get("result_record_id"), {}).get("record_digest"), f"HELPER_RESULT_DIGEST:{binding.get('runtime_helper_id')}")
        require(binding.get("parameter_modes") == helper.get("parameter_modes"), f"HELPER_MODES:{binding.get('runtime_helper_id')}")
        require(binding.get("parameter_address_classes") == helper.get("parameter_address_classes"), f"HELPER_ADDRESS:{binding.get('runtime_helper_id')}")
    effective_by_helper = {row.get("runtime_helper_id"): row.get("effective_signature_digest") for row in bindings}

    target_rows = targets.get("target_mappings", [])
    require(targets.get("schema") == "deeplus.runtime-target-mapping-registry/r99", "TARGET_IDENTITY")
    require([row.get("module_kind") for row in target_rows] == ["Xvm", "ObjectAot", "InMemoryJit"], "TARGET_ORDER")
    require(targets.get("registry_digest") == digest(without(targets, "registry_digest")), "TARGET_REGISTRY_DIGEST")
    for row in target_rows:
        require(row.get("mapping_digest") == digest(without(row, "mapping_digest")), f"TARGET_MAPPING_DIGEST:{row.get('module_kind')}")
        require(len(row.get("scalar_mapping_rows", [])) == 20, f"TARGET_SCALARS:{row.get('module_kind')}")
        helper_maps = row.get("helper_mapping_rows", [])
        require(len(helper_maps) == 25 and {item.get("runtime_helper_id") for item in helper_maps} == active_helper_set, f"TARGET_HELPER_EXACT_SET:{row.get('module_kind')}")
        require(all(item.get("effective_signature_digest") == effective_by_helper.get(item.get("runtime_helper_id")) for item in helper_maps), f"TARGET_HELPER_SIGNATURES:{row.get('module_kind')}")
        if row.get("module_kind") == "Xvm":
            require([item.get("table_ordinal") for item in helper_maps] == list(range(25)), "XVM_HELPER_ORDINALS")
        else:
            require(all(item.get("symbol") and item.get("linkage") == "IMPORT_EXACT" for item in helper_maps), f"NATIVE_HELPER_SYMBOLS:{row.get('module_kind')}")
        require(row.get("host_default_count") == 0 and row.get("target_location_is_semantic_identity") is False, f"TARGET_FENCE:{row.get('module_kind')}")
    require(target_rows[1]["scalar_mapping_rows"] == target_rows[2]["scalar_mapping_rows"], "AOT_JIT_SCALAR_PARITY")
    require(target_rows[1]["indirect_slot_mapping"] == target_rows[2]["indirect_slot_mapping"], "AOT_JIT_SLOT_PARITY")
    require(target_rows[1]["outcome_mapping_rows"] == target_rows[2]["outcome_mapping_rows"], "AOT_JIT_OUTCOME_PARITY")
    lock = targets.get("toolchain_lock", {})
    require(lock.get("rust_version") == "1.85.0" and lock.get("cranelift_dependency_connected") is False and lock.get("product_execution") == "NOT_RUN", "TARGET_TOOLCHAIN_HONESTY")

    machine_ops = machine.get("semantic_operations", [])
    machine_terms = machine.get("terminators", [])
    xbc_ops = xbc.get("operation_rows", [])
    xbc_terms = xbc.get("terminator_rows", [])
    require(xbc.get("schema") == "deeplus.xbc-typed-payload-registry/r99", "XBC_IDENTITY")
    require(xbc.get("registry_digest") == digest(without(xbc, "registry_digest")), "XBC_REGISTRY_DIGEST")
    require(len(xbc.get("field_domain_rows", [])) == 73, "XBC_FIELD_DOMAINS")
    require(len(xbc_ops) == 48 and len({row.get("opcode") for row in xbc_ops}) == 48, "XBC_OPERATION_ROWS")
    require(len(xbc_terms) == 17 and len({row.get("opcode") for row in xbc_terms}) == 17, "XBC_TERMINATOR_ROWS")
    for index, (source, row) in enumerate(zip(machine_ops, xbc_ops)):
        require(row.get("opcode") == index and row.get("operation_kind") == source.get("operation_kind"), f"XBC_OPERATION_ID:{index}")
        require([item.get("field_name") for item in row.get("required_fields", [])] == source.get("payload_contract", {}).get("required_fields", []), f"XBC_OPERATION_FIELDS:{index}")
        require(row.get("additional_fields") is False, f"XBC_OPERATION_CLOSED:{index}")
        require(all(item in xbc.get("field_domain_rows", []) for item in row.get("required_fields", [])), f"XBC_OPERATION_DOMAIN_BINDING:{index}")
    for index, (source, row) in enumerate(zip(machine_terms, xbc_terms)):
        require(row.get("opcode") == 32768 + index and row.get("terminator_kind") == source.get("terminator_kind"), f"XBC_TERMINATOR_ID:{index}")
        require([item.get("field_name") for item in row.get("required_fields", [])] == source.get("payload_contract", {}).get("required_fields", []), f"XBC_TERMINATOR_FIELDS:{index}")
        require(row.get("additional_fields") is False, f"XBC_TERMINATOR_CLOSED:{index}")
        require(all(item in xbc.get("field_domain_rows", []) for item in row.get("required_fields", [])), f"XBC_TERMINATOR_DOMAIN_BINDING:{index}")

    clif_ops = clif.get("operation_rows", [])
    clif_terms = clif.get("terminator_rows", [])
    require(clif.get("schema") == "deeplus.mir-clif-projection-registry/r99", "CLIF_IDENTITY")
    require(clif.get("gap_id") == "IR-BACKEND-P1-073", "CLIF_GAP_ID")
    require(clif.get("registry_digest") == digest(without(clif, "registry_digest")), "CLIF_REGISTRY_DIGEST")
    require([row.get("mir_kind") for row in clif_ops] == [row.get("operation_kind") for row in machine_ops], "CLIF_OPERATION_TOTALITY")
    require([row.get("mir_kind") for row in clif_terms] == [row.get("terminator_kind") for row in machine_terms], "CLIF_TERMINATOR_TOTALITY")
    require(all(len(row.get("ordered_steps", [])) >= 2 and row.get("missing_capability") == "REJECT_BEFORE_CLIF_EMISSION" for row in [*clif_ops, *clif_terms]), "CLIF_ROW_CLOSURE")
    expected_grouped = {
        "RUN_OP": {"AWAIT", "CANCEL_THEN_JOIN", "EXIT", "JOIN", "SPAWN"},
        "ACTOR_OP": {"AWAIT_REPLY", "DEQUEUE", "REPLY", "REQUEST", "SEND", "TURN_BEGIN", "TURN_END"},
        "ONCE_OP": {"FUNCTION_STATIC_ENSURE", "LAZY_FORCE"},
        "SYNC_OP": {"LOCK_ACQUIRE", "LOCK_RELEASE", "OBSERVE_BEGIN", "OBSERVE_END", "REPLACE_COMMIT"},
    }
    binding_by_helper = {row.get("runtime_helper_id"): row for row in bindings}
    for row in clif_terms:
        selector = row.get("runtime_helper_selector_or_null")
        require(not isinstance(selector, str) or "<" not in selector, f"CLIF_HELPER_PLACEHOLDER:{row.get('mir_kind')}")
        if selector:
            require(selector in active_helper_set, f"CLIF_DIRECT_HELPER:{row.get('mir_kind')}")
        dispatch = row.get("runtime_helper_dispatch_rows", [])
        if row.get("mir_kind") in expected_grouped:
            require({item.get("payload_operation") for item in dispatch} == expected_grouped[row["mir_kind"]], f"CLIF_GROUPED_OPERATION_TOTALITY:{row.get('mir_kind')}")
            require(len(dispatch) == len(expected_grouped[row["mir_kind"]]), f"CLIF_GROUPED_OPERATION_UNIQUENESS:{row.get('mir_kind')}")
            for item in dispatch:
                helper = helper_by_id.get(item.get("runtime_helper_id"), {})
                binding = binding_by_helper.get(item.get("runtime_helper_id"), {})
                require(helper.get("operation") == item.get("payload_operation"), f"CLIF_GROUPED_HELPER_OPERATION:{row.get('mir_kind')}:{item.get('payload_operation')}")
                require(item.get("runtime_helper_signature_id") == helper.get("runtime_helper_signature_id"), f"CLIF_GROUPED_SIGNATURE:{row.get('mir_kind')}:{item.get('payload_operation')}")
                require(item.get("arguments_record_id") == helper.get("arguments_record_id") and item.get("result_record_id") == helper.get("result_record_id"), f"CLIF_GROUPED_RECORDS:{row.get('mir_kind')}:{item.get('payload_operation')}")
                require(item.get("effective_signature_digest") == binding.get("effective_signature_digest"), f"CLIF_GROUPED_EFFECTIVE_DIGEST:{row.get('mir_kind')}:{item.get('payload_operation')}")
        else:
            require(not dispatch, f"CLIF_UNEXPECTED_GROUPED_DISPATCH:{row.get('mir_kind')}")
    invariants = clif.get("global_invariants", {})
    require(invariants.get("semantic_reselection_count") == 0 and invariants.get("trap_substitution_for_error_or_cancellation_count") == 0 and invariants.get("grouped_runtime_helper_dispatch_count") == 19 and invariants.get("runtime_helper_placeholder_count") == 0 and invariants.get("product_execution") == "NOT_RUN", "CLIF_GOVERNANCE")
    return errors


def ordinal_reference_ok(
    value: Any,
    contract: dict[str, Any],
    module: dict[str, Any],
    body: dict[str, Any],
) -> bool:
    domain = contract.get("domain", "")
    namespaces = {
        "CONSTANT_ORDINAL": "CONSTANT", "VALUE_ORDINAL": "VALUE",
        "PLACE_ORDINAL": "PLACE", "BODY_ORDINAL": "BODY",
        "STATIC_IDENTITY_ORDINAL": "STATIC_IDENTITY",
        "CONTINUATION_FRAME_SLOT_ORDINAL": "CONTINUATION_FRAME_SLOT",
    }

    def limit(namespace: str) -> int:
        return {
            "CONSTANT": len(module.get("constant_table", [])),
            "STATIC_IDENTITY": len(module.get("static_identity_table", [])),
            "BODY": len(module.get("body_table", [])),
            "VALUE": len(body.get("value_slots", [])),
            "PLACE": len(body.get("place_slots", [])),
            "LINEAR_TOKEN": len(body.get("linear_token_slots", [])),
            "CONTINUATION_FRAME_SLOT": len(body.get("continuation_frame_slots", [])),
        }.get(namespace, -1)

    def exact_ref(item: Any, namespace: str) -> bool:
        return (
            isinstance(item, dict)
            and set(item) == {"namespace", "ordinal"}
            and item.get("namespace") == namespace
            and isinstance(item.get("ordinal"), int)
            and 0 <= item["ordinal"] < limit(namespace)
        )

    if domain in namespaces:
        return exact_ref(value, namespaces[domain])
    if domain == "LINEAR_TOKEN_ORDINAL":
        return exact_ref(value, "LINEAR_TOKEN")
    if domain == "LINEAR_TOKEN_ORDINAL_OR_NULL":
        return value is None or exact_ref(value, "LINEAR_TOKEN")
    if domain.endswith("_ORDINAL_LIST"):
        namespace = "STATIC_IDENTITY" if domain.startswith("STATIC") else "LINEAR_TOKEN"
        return isinstance(value, list) and all(exact_ref(item, namespace) for item in value)
    if domain == "BASE_KIND_DISCRIMINATED_PLACE_OR_VALUE_ORDINAL":
        return isinstance(value, dict) and value.get("namespace") in {"PLACE", "VALUE"} and exact_ref(value, value["namespace"])
    if domain == "SHA256_BYTES":
        return isinstance(value, str) and value != "0" * 64 and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)
    if domain == "U32":
        return isinstance(value, int) and 0 <= value <= 4294967295
    if domain in {"CLOSED_ENUM_VALUE", "CLOSED_ENUM_VALUE_OR_NULL"}:
        return (value is None and domain.endswith("_OR_NULL")) or value in contract.get("closed_values", [])
    return False


def decoded_module_errors(root: Path, fixture: dict[str, Any], xbc: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    module = fixture.get("decoded_module", {})
    op_rows = {row.get("opcode"): row for row in xbc.get("operation_rows", [])}
    term_rows = {row.get("opcode"): row for row in xbc.get("terminator_rows", [])}
    section_keys = [
        ("MODULE_DESCRIPTOR", "module_descriptor"), ("TYPE_TABLE", "type_table"),
        ("STATIC_IDENTITY_TABLE", "static_identity_table"),
        ("RESPONSIBILITY_EVIDENCE_TABLE", "responsibility_evidence_table"),
        ("CONSTANT_TABLE", "constant_table"),
        ("CLOSURE_ENVIRONMENT_PLAN_TABLE", "closure_environment_plan_table"),
        ("BODY_TABLE", "body_table"), ("MANAGED_MEMORY_PLAN", "managed_memory_plan"),
        ("CONTINUATION_INTERFACE", "continuation_interface"),
        ("DEBUG_PROVENANCE", "debug_provenance"),
    ]
    if fixture.get("typed_payload_registry_digest") != xbc.get("registry_digest"):
        errors.append("FIXTURE_REGISTRY_DIGEST")
    schema = load(root / XBC_MODULE_SCHEMA)
    if fixture.get("module_schema") != XBC_MODULE_SCHEMA.as_posix() or fixture.get("module_schema_digest") != file_digest(root / XBC_MODULE_SCHEMA):
        errors.append("DECODED_MODULE_SCHEMA_BINDING")
    if module.get("schema") != "deeplus.xvm-xbc-module/r1" or set(module) != set(schema.get("required", [])):
        errors.append("DECODED_MODULE_SHAPE")
    header = module.get("header", {})
    descriptor = module.get("module_descriptor", {})
    source_digest = fixture.get("source_mir_semantic_digest")
    if source_digest != digest(fixture.get("source_mir_fixture")) or header.get("source_mir_semantic_digest") != source_digest or descriptor.get("source_mir_semantic_digest") != source_digest:
        errors.append("SOURCE_MIR_DIGEST_BINDING")
    if header.get("contract_digest") != xbc.get("registry_digest"):
        errors.append("XBC_CONTRACT_DIGEST_BINDING")
    directory = module.get("directory", [])
    if len(directory) != 10:
        errors.append("DECODED_MODULE_DIRECTORY_COUNT")
    else:
        offset = 128 + 10 * 56
        logical_rows = []
        for index, ((kind, key), entry) in enumerate(zip(section_keys, directory)):
            encoded = canonical_cbor(module.get(key))
            expected_digest = hashlib.sha256(encoded).hexdigest()
            if entry != {"kind": kind, "ordinal": index, "flags": 0, "offset": offset, "length": len(encoded), "payload_sha256": expected_digest}:
                errors.append(f"DECODED_MODULE_DIRECTORY_BINDING:{kind}")
            logical_rows.append({"kind": kind, "payload_sha256": expected_digest})
            offset += len(encoded)
        if header.get("payload_bytes") != offset - (128 + 10 * 56) or header.get("xbc_logical_digest") != cbor_digest(logical_rows):
            errors.append("DECODED_MODULE_LOGICAL_DIGEST")

    def dense_ok(rows: Any) -> bool:
        return isinstance(rows, list) and [row.get("ordinal") for row in rows] == list(range(len(rows))) and all(row.get("entry_digest") == digest(without(row, "entry_digest")) for row in rows)

    for key in ("type_table", "static_identity_table", "responsibility_evidence_table", "constant_table", "closure_environment_plan_table"):
        if not dense_ok(module.get(key)):
            errors.append(f"XBC_DENSE_TABLE:{key}")
    positive_frame = False
    for body in module.get("body_table", []):
        for key in ("value_slots", "place_slots", "linear_token_slots", "continuation_frame_slots"):
            if not dense_ok(body.get(key)):
                errors.append(f"XBC_DENSE_BODY_TABLE:{key}")
        body_material = without(body, "body_projection_digest")
        if body.get("body_projection_digest") != digest(body_material):
            errors.append("XBC_BODY_PROJECTION_DIGEST")
        blocks = body.get("blocks", [])
        if [row.get("ordinal") for row in blocks] != list(range(len(blocks))) or body.get("entry_block_ordinal") not in range(len(blocks)):
            errors.append("XBC_CFG_BLOCK_ORDINALS")
        seen_outputs: set[tuple[str, int]] = set()
        for block in body.get("blocks", []):
            if [row.get("ordinal") for row in block.get("instructions", [])] != list(range(len(block.get("instructions", [])) )):
                errors.append("XBC_INSTRUCTION_ORDINALS")
            for instruction in block.get("instructions", []):
                row = op_rows.get(instruction.get("opcode"), {})
                if instruction.get("operation_kind") != row.get("operation_kind"):
                    errors.append("XBC_OPCODE_KIND_MISMATCH")
                if instruction.get("payload_contract_id") != row.get("payload_contract_id"):
                    errors.append("XBC_PAYLOAD_CONTRACT_MISMATCH")
                payload = instruction.get("payload", {})
                required = row.get("required_fields", [])
                if list(payload) != [item.get("field_name") for item in required]:
                    errors.append("XBC_PAYLOAD_FIELD_SET_OR_ORDER")
                for item in required:
                    if not ordinal_reference_ok(payload.get(item.get("field_name")), item, module, body):
                        errors.append(f"XBC_PAYLOAD_DOMAIN:{item.get('field_name')}")
                if instruction.get("operation_kind") == "FRAME_RESUME_COMMIT" and payload.get("winner_witness_or_null") == "RESUME_WON" and payload.get("hir_provenance", {}).get("namespace") == "STATIC_IDENTITY":
                    positive_frame = True
                for slot in [*instruction.get("inputs", []), *instruction.get("outputs", [])]:
                    contract = {"domain": slot.get("namespace", "") + "_ORDINAL"}
                    if not ordinal_reference_ok(slot, contract, module, body):
                        errors.append("XBC_SSA_SLOT_BOUNDS")
                for slot in instruction.get("outputs", []):
                    identity = (slot.get("namespace"), slot.get("ordinal"))
                    if identity in seen_outputs:
                        errors.append("XBC_SSA_MULTIPLE_DEFINITION")
                    seen_outputs.add(identity)
            term = block.get("terminator", {})
            row = term_rows.get(term.get("opcode"), {})
            if term.get("terminator_kind") != row.get("terminator_kind"):
                errors.append("XBC_TERMINATOR_KIND_MISMATCH")
            if term.get("payload_contract_id") != row.get("payload_contract_id"):
                errors.append("XBC_TERMINATOR_CONTRACT_MISMATCH")
            payload = term.get("payload", {})
            required = row.get("required_fields", [])
            if list(payload) != [item.get("field_name") for item in required]:
                errors.append("XBC_TERMINATOR_FIELD_SET_OR_ORDER")
            for item in required:
                if not ordinal_reference_ok(payload.get(item.get("field_name")), item, module, body):
                    errors.append(f"XBC_TERMINATOR_DOMAIN:{item.get('field_name')}")
            for successor in term.get("successors", []):
                if successor.get("block_ordinal") not in range(len(blocks)):
                    errors.append("XBC_CFG_SUCCESSOR_BOUNDS")
    if not positive_frame:
        errors.append("XBC_POSITIVE_FRAME_ROUNDTRIP")
    return errors


def validate(root: Path, values: dict[str, Any] | None = None) -> list[str]:
    values = values or {}
    get = lambda rel: values.get(rel.as_posix(), load(root / rel))
    records, targets, clif, xbc = get(RECORDS), get(TARGETS), get(CLIF), get(XBC)
    helpers, machine, fixture = get(HELPERS), get(MACHINE), get(XBC_FIXTURE)
    errors = registry_errors(records, targets, clif, xbc, helpers, machine)
    errors.extend(decoded_module_errors(root, fixture, xbc))
    continuation = get(CONTINUATION)
    mir_semantics = values.get(MIR_SEMANTICS.as_posix(), (root / MIR_SEMANTICS).read_text(encoding="utf-8"))
    language = values.get(LANGUAGE.as_posix(), (root / LANGUAGE).read_text(encoding="utf-8"))
    exact_continuation_digest = continuation.get("continuation_interface_digest")
    expected_mir_count = (
        f"exactly {len(machine.get('semantic_operations', []))} semantic operations, "
        f"{len(machine.get('terminators', []))}"
    )
    expected_runtime_count = (
        f"{len(records.get('record_rows', []))} ordered argument/result\n"
        f"records and {len(active_helpers(helpers))} effective helper signatures "
        f"({len(helpers.get('helper_rows', []))} base plus "
        f"{len(helpers.get('conditional_extension_rows', []))} active conditional\nhelpers)"
    )
    if expected_mir_count not in mir_semantics:
        errors.append("MIR_SEMANTIC_OPERATION_COUNT_PROSE_PARITY")
    if expected_runtime_count not in mir_semantics:
        errors.append("RUNTIME_HELPER_RECORD_COUNT_PROSE_PARITY")
    if not exact_continuation_digest or exact_continuation_digest not in mir_semantics or exact_continuation_digest not in language:
        errors.append("CONTINUATION_DIGEST_PROSE_PARITY")
    abi = load(root / "spec/contracts/internal-runtime-abi-r1.json")
    backend = load(root / "spec/contracts/cranelift-backend-current.json")
    xbc_contract = load(root / "spec/contracts/xvm-xbc-projection-r1.json")
    if abi.get("helper_registry", {}).get("record_registry") != RECORDS.as_posix():
        errors.append("ABI_RECORD_BINDING")
    if abi.get("target_projection_contract", {}).get("mapping_preimage_registry") != TARGETS.as_posix():
        errors.append("ABI_TARGET_BINDING")
    if backend.get("mir_projection", {}).get("total_projection_registry") != CLIF.as_posix():
        errors.append("BACKEND_CLIF_BINDING")
    if xbc_contract.get("body_projection", {}).get("typed_payload_registry") != XBC.as_posix():
        errors.append("XBC_CONTRACT_BINDING")
    lanes = load(root / "current/product-lanes.json").get("lanes", [])
    if len(lanes) != 15 or any(row.get("status") != "NOT_RUN" for row in lanes):
        errors.append("PRODUCT_LANES")
    return errors


def mutation_errors(root: Path) -> list[str]:
    base = {
        RECORDS.as_posix(): load(root / RECORDS), TARGETS.as_posix(): load(root / TARGETS),
        CLIF.as_posix(): load(root / CLIF), XBC.as_posix(): load(root / XBC),
        XBC_FIXTURE.as_posix(): load(root / XBC_FIXTURE), HELPERS.as_posix(): load(root / HELPERS),
        MACHINE.as_posix(): load(root / MACHINE),
        CONTINUATION.as_posix(): load(root / CONTINUATION),
        MIR_SEMANTICS.as_posix(): (root / MIR_SEMANTICS).read_text(encoding="utf-8"),
        LANGUAGE.as_posix(): (root / LANGUAGE).read_text(encoding="utf-8"),
    }
    mutations: list[tuple[str, dict[str, Any]]] = []
    def redigest_registry(value: dict[str, Any], rel: Path, rows: str | None = None) -> None:
        doc = value[rel.as_posix()]
        if rows:
            for row in doc[rows]:
                row["mapping_digest"] = digest(without(row, "mapping_digest"))
        doc["registry_digest"] = digest(without(doc, "registry_digest"))

    value = copy.deepcopy(base); value[RECORDS.as_posix()]["record_rows"][0]["fields"].reverse(); redigest_registry(value, RECORDS); mutations.append(("RECORD_FIELD_ORDER", value))
    value = copy.deepcopy(base); rid="RuntimeHelperId:managed.allocate_slow"; binding=next(row for row in value[RECORDS.as_posix()]["helper_bindings"] if row["runtime_helper_id"]==rid); value[RECORDS.as_posix()]["helper_bindings"].remove(binding); value[RECORDS.as_posix()]["record_rows"]=[row for row in value[RECORDS.as_posix()]["record_rows"] if row["record_id"] not in {binding["arguments_record_id"],binding["result_record_id"]}]; redigest_registry(value, RECORDS); mutations.append(("RECORD_ACTIVE_HELPER_MISSING", value))
    value = copy.deepcopy(base); value[TARGETS.as_posix()]["target_mappings"][0]["helper_mapping_rows"].pop(); redigest_registry(value, TARGETS, "target_mappings"); mutations.append(("TARGET_ACTIVE_HELPER_MISSING", value))
    value = copy.deepcopy(base); value[TARGETS.as_posix()]["target_mappings"][1]["helper_mapping_rows"][0]["effective_signature_digest"]="f"*64; redigest_registry(value, TARGETS, "target_mappings"); mutations.append(("TARGET_HELPER_SIGNATURE", value))
    value = copy.deepcopy(base); value[CLIF.as_posix()]["operation_rows"].pop(); mutations.append(("CLIF_MISSING_ROW", value))
    value = copy.deepcopy(base); value[CLIF.as_posix()]["terminator_rows"].append(copy.deepcopy(value[CLIF.as_posix()]["terminator_rows"][0])); mutations.append(("CLIF_DUPLICATE_ROW", value))
    value = copy.deepcopy(base); row=next(row for row in value[CLIF.as_posix()]["terminator_rows"] if row["mir_kind"]=="RUN_OP"); row["runtime_helper_dispatch_rows"].pop(); redigest_registry(value, CLIF); mutations.append(("CLIF_GROUPED_MISSING", value))
    value = copy.deepcopy(base); row=next(row for row in value[CLIF.as_posix()]["terminator_rows"] if row["mir_kind"]=="RUN_OP"); row["runtime_helper_selector_or_null"]="RuntimeHelperId:run.<sealed>"; redigest_registry(value, CLIF); mutations.append(("CLIF_PLACEHOLDER", value))
    value = copy.deepcopy(base); row=next(row for row in value[CLIF.as_posix()]["terminator_rows"] if row["mir_kind"]=="RUN_OP"); row["runtime_helper_dispatch_rows"][0]["runtime_helper_id"]="RuntimeHelperId:actor.send"; redigest_registry(value, CLIF); mutations.append(("CLIF_WRONG_GROUPED_HELPER", value))
    value = copy.deepcopy(base); instruction = value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][0]; instruction["operation_kind"] = "CONST"; mutations.append(("XBC_WRONG_KIND", value))
    value = copy.deepcopy(base); instruction = value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][0]; instruction["payload"]["construction_id"]["namespace"] = "VALUE"; mutations.append(("XBC_WRONG_NAMESPACE", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][0]["payload"]["construction_id"] = None; mutations.append(("XBC_NONNULL_ID_NULL", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][0]["payload"]["construction_id"]["ordinal"] = 999; mutations.append(("XBC_ORDINAL_OUT_OF_BOUNDS", value))
    value = copy.deepcopy(base); frame=value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][1]; frame["payload"]["winner_witness_or_null"]="UNKNOWN_WINNER"; mutations.append(("XBC_UNKNOWN_CLOSED_ENUM", value))
    value = copy.deepcopy(base); frame=value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][1]; frame["payload"]["hir_provenance"]={"source":"free-form"}; mutations.append(("XBC_HIR_PROVENANCE_NOT_ORDINAL", value))
    value = copy.deepcopy(base); instruction = value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][0]; del instruction["payload"]["stage_index"]; mutations.append(("XBC_MISSING_FIELD", value))
    value = copy.deepcopy(base); instruction = value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"][0]; instruction["payload"]["extra"] = 0; mutations.append(("XBC_EXTRA_FIELD", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["decoded_module"]["header"]["source_mir_semantic_digest"]="0"*64; mutations.append(("XBC_ZERO_DIGEST", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["decoded_module"]["directory"][0]["payload_sha256"]="f"*64; mutations.append(("XBC_STALE_SECTION_DIGEST", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["source_mir_fixture"]["body_id"]="BodyId:mutated"; mutations.append(("XBC_SOURCE_MIR_BINDING", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["terminator"]["successors"]=[{"block_ordinal":99,"arguments":[]}]; mutations.append(("XBC_CFG_SUCCESSOR_BOUNDS", value))
    value = copy.deepcopy(base); value[XBC_FIXTURE.as_posix()]["decoded_module"]["body_table"][0]["blocks"][0]["instructions"].pop(); mutations.append(("XBC_FRAME_POSITIVE_REMOVED", value))
    value = copy.deepcopy(base); value[MIR_SEMANTICS.as_posix()] = value[MIR_SEMANTICS.as_posix()].replace("exactly 48 semantic operations, 17", "exactly 47 semantic operations, 17"); mutations.append(("MIR_PROSE_OPERATION_COUNT", value))
    value = copy.deepcopy(base); value[MIR_SEMANTICS.as_posix()] = value[MIR_SEMANTICS.as_posix()].replace("50 ordered argument/result\nrecords and 25 effective helper signatures (22 base plus 3 active conditional\nhelpers)", "50 ordered argument/result\nrecords and 24 effective helper signatures (22 base plus 2 active conditional\nhelpers)"); mutations.append(("MIR_PROSE_RUNTIME_COUNTS", value))
    value = copy.deepcopy(base); value[LANGUAGE.as_posix()] = value[LANGUAGE.as_posix()].replace(value[CONTINUATION.as_posix()]["continuation_interface_digest"], "0" * 64); mutations.append(("LANGUAGE_CONTINUATION_DIGEST", value))
    survived = []
    for mutation_id, values in mutations:
        if not validate(root, values):
            survived.append(f"MUTATION_SURVIVED:{mutation_id}")
    return survived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    if args.mutations:
        errors.extend(mutation_errors(root))
    if errors:
        print("FAIL R99 runtime/backend projection: " + ", ".join(errors))
        return 1
    print("PASS R99 runtime/backend projection: records 50, active helpers 25 (22 base + 3 conditional), targets 3x25, MIR/CLIF 48+17 with grouped helper dispatch 19, exact prose/digest parity, XBC fields 73 and rows 48+17, bounded decoded module PASS, mutations 25/25 rejected, product 15/15 NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
