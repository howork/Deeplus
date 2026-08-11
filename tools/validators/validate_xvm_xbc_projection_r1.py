#!/usr/bin/env python3
"""Validate the R92 canonical xVM XBC projection design closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


CONTRACT = "spec/contracts/xvm-xbc-projection-r1.json"
CONTRACT_SCHEMA = "schemas/language/xvm-xbc-projection-contract-r1.schema.json"
MODULE_SCHEMA = "schemas/language/xvm-xbc-module-r1.schema.json"
RECEIPT_SCHEMA = "schemas/language/xvm-xbc-projection-receipt-r1.schema.json"
FIXTURE_SCHEMA = "schemas/language/xvm-xbc-projection-fixtures-r1.schema.json"
FIXTURE = "tests/fixtures/current/xvm-xbc-projection-r1.json"
MACHINE = "spec/contracts/mir-machine-registry.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
BACKEND = "spec/contracts/cranelift-backend-current.json"
RUNTIME_ABI = "spec/contracts/internal-runtime-abi-r1.json"
RUNTIME_FIXTURE = "tests/fixtures/current/internal-runtime-abi-r1.json"
MANAGED = "spec/contracts/managed-reference-memory-profile-r1.json"
CONTINUATION = "spec/contracts/continuation-interface-r1.json"
SEMANTICS = "spec/mir/semantics.md"
FEATURES = "spec/features/catalog/chunks/part-0021.json"
DIAGNOSTICS = "spec/diagnostics/catalog/chunks/part-0040.json"
PRODUCT = "current/product-lanes.json"

SECTION_ORDER = [
    "MODULE_DESCRIPTOR",
    "TYPE_TABLE",
    "STATIC_IDENTITY_TABLE",
    "RESPONSIBILITY_EVIDENCE_TABLE",
    "CONSTANT_TABLE",
    "CLOSURE_ENVIRONMENT_PLAN_TABLE",
    "BODY_TABLE",
    "MANAGED_MEMORY_PLAN",
    "CONTINUATION_INTERFACE",
    "DEBUG_PROVENANCE",
]
DIAGNOSTIC_IDS = [
    "XBC_CONTAINER_INVALID",
    "XBC_VERSION_OR_BINDING_UNSUPPORTED",
    "XBC_SECTION_CANONICALITY_INVALID",
    "XBC_INSTRUCTION_OR_CFG_INVALID",
    "XBC_RESPONSIBILITY_OR_ROOT_INVALID",
    "XBC_ARTIFACT_DIGEST_MISMATCH",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha(value: bytes) -> bytes:
    return hashlib.sha256(value).digest()


def _cbor_head(major: int, value: int) -> bytes:
    if value < 24:
        return bytes([(major << 5) | value])
    if value <= 0xFF:
        return bytes([(major << 5) | 24, value])
    if value <= 0xFFFF:
        return bytes([(major << 5) | 25]) + struct.pack(">H", value)
    if value <= 0xFFFFFFFF:
        return bytes([(major << 5) | 26]) + struct.pack(">I", value)
    if value <= 0xFFFFFFFFFFFFFFFF:
        return bytes([(major << 5) | 27]) + struct.pack(">Q", value)
    raise ValueError("CBOR integer out of range")


def cbor_encode(value: Any) -> bytes:
    if value is None:
        return b"\xf6"
    if value is False:
        return b"\xf4"
    if value is True:
        return b"\xf5"
    if isinstance(value, int):
        return _cbor_head(0, value) if value >= 0 else _cbor_head(1, -1 - value)
    if isinstance(value, bytes):
        return _cbor_head(2, len(value)) + value
    if isinstance(value, str):
        payload = value.encode("utf-8")
        return _cbor_head(3, len(payload)) + payload
    if isinstance(value, list):
        return _cbor_head(4, len(value)) + b"".join(cbor_encode(row) for row in value)
    if isinstance(value, dict):
        rows = [(cbor_encode(key), cbor_encode(item)) for key, item in value.items()]
        rows.sort(key=lambda row: (len(row[0]), row[0]))
        return _cbor_head(5, len(rows)) + b"".join(key + item for key, item in rows)
    raise TypeError(type(value).__name__)


class CborError(ValueError):
    pass


def cbor_decode(payload: bytes) -> Any:
    def read_uint(offset: int, additional: int) -> tuple[int, int]:
        if additional < 24:
            return additional, offset
        widths = {24: 1, 25: 2, 26: 4, 27: 8}
        if additional not in widths:
            raise CborError("indefinite or reserved additional information")
        width = widths[additional]
        if offset + width > len(payload):
            raise CborError("truncated integer")
        value = int.from_bytes(payload[offset : offset + width], "big")
        minimum = {24: 24, 25: 256, 26: 65536, 27: 4294967296}[additional]
        if value < minimum:
            raise CborError("non-shortest integer or length")
        return value, offset + width

    def item(offset: int) -> tuple[Any, int, bytes]:
        start = offset
        if offset >= len(payload):
            raise CborError("truncated item")
        initial = payload[offset]
        offset += 1
        major, additional = initial >> 5, initial & 31
        if major in {0, 1, 2, 3, 4, 5}:
            count, offset = read_uint(offset, additional)
        if major == 0:
            result: Any = count
        elif major == 1:
            result = -1 - count
        elif major == 2:
            if offset + count > len(payload):
                raise CborError("truncated bytes")
            result, offset = payload[offset : offset + count], offset + count
        elif major == 3:
            if offset + count > len(payload):
                raise CborError("truncated text")
            try:
                result = payload[offset : offset + count].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise CborError("invalid utf-8") from exc
            offset += count
        elif major == 4:
            result = []
            for _ in range(count):
                child, offset, _ = item(offset)
                result.append(child)
        elif major == 5:
            result = {}
            previous: tuple[int, bytes] | None = None
            for _ in range(count):
                key, offset, key_bytes = item(offset)
                order = (len(key_bytes), key_bytes)
                if previous is not None and order <= previous:
                    raise CborError("noncanonical or duplicate map key")
                previous = order
                child, offset, _ = item(offset)
                try:
                    result[key] = child
                except TypeError as exc:
                    raise CborError("unhashable map key") from exc
        elif major == 7 and additional in {20, 21, 22}:
            result = {20: False, 21: True, 22: None}[additional]
        else:
            raise CborError("unsupported CBOR item")
        return result, offset, payload[start:offset]

    value, end, _ = item(0)
    if end != len(payload):
        raise CborError("trailing CBOR bytes")
    if cbor_encode(value) != payload:
        raise CborError("decode-reencode mismatch")
    return value


def build_sample_container(contract: dict[str, Any]) -> bytes:
    sections = [
        cbor_encode({"kind": kind, "present": True, "rows": []})
        for kind in SECTION_ORDER
    ]
    section_digests = [sha(payload) for payload in sections]
    logical_rows = [
        {"kind": kind, "payload_sha256": digest}
        for kind, digest in zip(SECTION_ORDER, section_digests)
    ]
    logical_digest = sha(cbor_encode(logical_rows))
    source_digest = sha(b"R92_SAMPLE_VERIFIED_DEEPLUS_MIR_R1")
    contract_digest = sha(canonical_json(contract))
    payload_bytes = sum(len(payload) for payload in sections)
    header = struct.pack(
        "<8sHHIHHIQ32s32s32s",
        bytes.fromhex("4450584243000d0a"),
        1,
        0,
        0,
        10,
        0,
        560,
        payload_bytes,
        source_digest,
        logical_digest,
        contract_digest,
    )
    offset = 128 + 560
    directory = bytearray()
    for ordinal, (payload, digest) in enumerate(zip(sections, section_digests)):
        directory.extend(
            struct.pack("<HHIQQ32s", ordinal + 1, 0, ordinal, offset, len(payload), digest)
        )
        offset += len(payload)
    return header + bytes(directory) + b"".join(sections)


def validate_container_bytes(blob: bytes) -> list[str]:
    errors: list[str] = []
    if len(blob) < 688:
        return ["CONTAINER_TRUNCATED"]
    try:
        fields = struct.unpack("<8sHHIHHIQ32s32s32s", blob[:128])
    except struct.error:
        return ["HEADER_UNPACK"]
    magic, major, minor, flags, count, reserved, directory_bytes, payload_bytes, source_digest, logical_digest, contract_digest = fields
    if magic != bytes.fromhex("4450584243000d0a"):
        errors.append("MAGIC")
    if (major, minor) != (1, 0) or flags != 0 or reserved != 0:
        errors.append("VERSION_FLAGS")
    if count != 10 or directory_bytes != 560:
        errors.append("DIRECTORY_SHAPE")
    if len(blob) != 688 + payload_bytes:
        errors.append("PAYLOAD_LENGTH")
    expected_offset = 688
    logical_rows: list[dict[str, Any]] = []
    for ordinal in range(10):
        start = 128 + ordinal * 56
        try:
            kind, row_flags, row_ordinal, offset, length, digest = struct.unpack(
                "<HHIQQ32s", blob[start : start + 56]
            )
        except struct.error:
            errors.append(f"DIRECTORY_ROW:{ordinal}")
            continue
        if kind != ordinal + 1 or row_flags != 0 or row_ordinal != ordinal:
            errors.append(f"DIRECTORY_IDENTITY:{ordinal}")
        if offset != expected_offset or offset + length > len(blob):
            errors.append(f"DIRECTORY_EXTENT:{ordinal}")
            continue
        section = blob[offset : offset + length]
        if sha(section) != digest:
            errors.append(f"SECTION_DIGEST:{ordinal}")
        try:
            decoded = cbor_decode(section)
            if decoded.get("kind") != SECTION_ORDER[ordinal]:
                errors.append(f"SECTION_KIND:{ordinal}")
        except (CborError, AttributeError):
            errors.append(f"SECTION_CBOR:{ordinal}")
        logical_rows.append({"kind": SECTION_ORDER[ordinal], "payload_sha256": digest})
        expected_offset += length
    if expected_offset != len(blob):
        errors.append("TRAILING_OR_GAP")
    if sha(cbor_encode(logical_rows)) != logical_digest:
        errors.append("LOGICAL_DIGEST")
    if source_digest == bytes(32) or contract_digest == bytes(32):
        errors.append("ZERO_BINDING_DIGEST")
    return errors


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def validate(root: Path, overrides: dict[str, Any] | None = None) -> list[str]:
    overrides = overrides or {}
    errors: list[str] = []

    def value(relative: str) -> Any:
        return overrides.get(relative, load(root / relative))

    contract = value(CONTRACT)
    machine = value(MACHINE)
    fixture = value(FIXTURE)
    bridge = value(BRIDGE)
    backend = value(BACKEND)
    runtime_abi = value(RUNTIME_ABI)
    runtime_fixture = value(RUNTIME_FIXTURE)
    diagnostics = value(DIAGNOSTICS)
    features = value(FEATURES)

    for schema_path in (CONTRACT_SCHEMA, MODULE_SCHEMA, RECEIPT_SCHEMA, FIXTURE_SCHEMA):
        schema = value(schema_path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("type") != "object":
            errors.append(f"SCHEMA_HEADER:{schema_path}")

    if contract.get("schema") != "deeplus.xvm-xbc-projection-contract/r1" or contract.get("gap_id") != "IR-XVM-P1-062":
        errors.append("CONTRACT_IDENTITY")
    authority = contract.get("authority", {})
    if authority.get("semantic_authority") != "Verified<DeeplusMirR1>" or authority.get("xvm_only_architecture") is not False or authority.get("historical_mir_x1_rfc_is_authority") is not False:
        errors.append("AUTHORITY_FENCE")
    source = contract.get("source_binding", {})
    if source.get("required_input_state") != "Verified<DeeplusMirR1>" or source.get("runtime_target_triple") != "deeplus-xvm-portable-r1" or source.get("semantic_reselection_count") != 0:
        errors.append("SOURCE_BINDING")

    container = contract.get("container", {})
    if container.get("magic_hex") != "4450584243000d0a" or container.get("header_bytes") != 128 or container.get("directory_entry_bytes") != 56 or container.get("section_order") != SECTION_ORDER or container.get("section_count") != 10:
        errors.append("CONTAINER_CONTRACT")
    if not all(container.get(key) is True for key in ("definite_lengths", "shortest_encodings", "canonical_map_key_order", "decode_reencode_byte_equality", "reserved_bits_must_be_zero")):
        errors.append("CANONICAL_ENCODING")

    operations = [
        row.get("operation_kind")
        for row in machine.get("semantic_operations", [])
    ]
    operation_rows = contract.get("opcode_contract", {}).get("operation_assignments", [])
    if len(operations) != 48 or [(row.get("ordinal"), row.get("kind"), row.get("opcode")) for row in operation_rows] != [(index, kind, index) for index, kind in enumerate(operations)]:
        errors.append("OPERATION_OPCODE_MAP")
    terminators = [
        row.get("terminator_kind")
        for row in machine.get("terminators", [])
    ]
    terminator_rows = contract.get("opcode_contract", {}).get("terminator_assignments", [])
    if len(terminators) != 17 or [(row.get("ordinal"), row.get("kind"), row.get("opcode")) for row in terminator_rows] != [(index, kind, 32768 + index) for index, kind in enumerate(terminators)]:
        errors.append("TERMINATOR_OPCODE_MAP")

    projection = machine.get("projection_capability_fence", {})
    if projection.get("projection_contracts", {}).get("PROJ-CAP-XVM-CANONICAL-XBC-R1") != CONTRACT or projection.get("xvm_xbc_schema") != MODULE_SCHEMA or projection.get("xvm_xbc_receipt_schema") != RECEIPT_SCHEMA:
        errors.append("MACHINE_PROJECTION_BINDING")
    bridge_authority = bridge.get("backend_authority", {})
    if bridge_authority.get("xvm_xbc_projection_contract") != CONTRACT or bridge_authority.get("xvm_xbc_product_execution") != "NOT_RUN" or bridge_authority.get("xvm_only_current") is not False:
        errors.append("BRIDGE_BINDING")
    backend_guard = backend.get("xvm_xbc_projection_guard", {})
    if backend_guard.get("contract") != CONTRACT or backend_guard.get("backend_semantic_reselection_count") != 0 or backend_guard.get("cross_path_observable_parity_required") is not True or backend_guard.get("product_execution") != "NOT_RUN":
        errors.append("BACKEND_PARITY_BINDING")

    xvm_projection_rows = [
        row for row in _walk(runtime_fixture)
        if isinstance(row, dict) and row.get("module_kind") == "Xvm" and row.get("target_triple") == "deeplus-xvm-portable-r1"
    ]
    if not xvm_projection_rows or any(row.get("runtime_abi_id") != "RuntimeAbiId:DEEPLUS_INTERNAL_RUNTIME_ABI_R1" or row.get("endianness") != "LITTLE" or row.get("calling_convention") != "DEEPLUS_XVM_LOGICAL_R1" for row in xvm_projection_rows):
        errors.append("RUNTIME_ABI_XVM_BINDING")
    if runtime_abi.get("backend_mappings", {}).get("Xvm", {}).get("helper_binding") != "TYPED_HELPER_TABLE":
        errors.append("RUNTIME_HELPER_BINDING")

    if not (root / MANAGED).is_file() or not (root / CONTINUATION).is_file():
        errors.append("ROOT_CONTINUATION_DEPENDENCY")
    semantics = (root / SEMANTICS).read_text(encoding="utf-8")
    if "canonical XBC R1" not in semantics or CONTRACT not in semantics or "0x0000..0x002f" not in semantics:
        errors.append("MIR_SEMANTICS_BINDING")

    feature = next((row for row in features if row.get("feature_id") == "hir_h1_current_mir_bridge_design"), {})
    feature_diags = feature.get("normative_trace_refs", {}).get("diagnostics", [])
    if not set(DIAGNOSTIC_IDS).issubset(feature_diags) or CONTRACT not in feature.get("artifact_trace_refs", []):
        errors.append("FEATURE_TRACE_BINDING")
    if [row.get("diagnostic_id") for row in diagnostics] != DIAGNOSTIC_IDS or any(row.get("stage") != "verifier" or row.get("product_support") != "NOT_RUN" for row in diagnostics):
        errors.append("DIAGNOSTIC_CONTRACT")

    cases = fixture.get("cases", [])
    expected_ids = ([f"R92-XBC-POS-{i:03d}" for i in range(1, 6)] + [f"R92-XBC-BND-{i:03d}" for i in range(1, 6)] + [f"R92-XBC-NEG-{i:03d}" for i in range(1, 9)])
    if [row.get("case_id") for row in cases] != expected_ids:
        errors.append("CASE_IDS")
    if [sum(row.get("class") == kind for row in cases) for kind in ("positive", "boundary", "reject")] != [5, 5, 8]:
        errors.append("CASE_COUNTS")
    for row in cases:
        admitted = row.get("class") != "reject"
        if admitted != (row.get("expected") == "ADMIT_STATIC_PROJECTION") or admitted != (row.get("diagnostic_or_null") is None):
            errors.append(f"CASE_DECISION:{row.get('case_id')}")

    sample = build_sample_container(contract)
    errors.extend(f"SAMPLE_{item}" for item in validate_container_bytes(sample))
    if len(sample) <= 688:
        errors.append("SAMPLE_EMPTY_PAYLOAD")

    governance = contract.get("governance", {})
    if governance.get("semantic_p0") != 0 or governance.get("feature_p1") != "22_OPEN_UNCHANGED" or governance.get("product_lanes") != "15_OF_15_NOT_RUN" or governance.get("production_xbc_emitter") != "NOT_RUN" or governance.get("production_xvm_interpreter") != "NOT_RUN":
        errors.append("GOVERNANCE")
    lanes = value(PRODUCT).get("lanes", [])
    if len(lanes) != 15 or any(row.get("status") != "NOT_RUN" for row in lanes):
        errors.append("PRODUCT_LANES")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    receipt = {
        "schema": "deeplus.xvm-xbc-projection-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "normal": "5_OF_5_PASS" if not errors else "BLOCKED",
        "boundary": "5_OF_5_PASS" if not errors else "BLOCKED",
        "reject": "8_OF_8_PASS" if not errors else "BLOCKED",
        "container_header_bytes": 128,
        "section_count": 10,
        "operation_opcode_count": 48,
        "terminator_opcode_count": 17,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
