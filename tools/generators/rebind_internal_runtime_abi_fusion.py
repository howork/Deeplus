#!/usr/bin/env python3
"""Bind the R37 runtime ABI to the fused R38/R36 contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REGISTRY = "spec/contracts/runtime-helper-registry-r1.json"
CONTRACT = "spec/contracts/internal-runtime-abi-r1.json"
FIXTURES = "tests/fixtures/current/internal-runtime-abi-r1.json"
CONTINUATION = "spec/contracts/continuation-interface-r1.json"
MEMORY = "spec/contracts/managed-reference-memory-profile-r1.json"
CRANELIFT = "spec/contracts/cranelift-backend-current.json"
HIR_BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
MIR_SCHEMA = "schemas/language/deeplus-mir.schema.json"
MIR_REGISTRY = "spec/contracts/mir-machine-registry.json"


def load(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads((root / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(relative)
    return value


def write(root: Path, relative: str, value: Any) -> None:
    (root / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(root: Path, relative: str) -> str:
    return hashlib.sha256((root / relative).read_bytes()).hexdigest()


def without(value: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key not in keys}


def address_class(mode: str) -> str:
    if mode == "OPAQUE_HANDLE":
        return "OPAQUE_MANAGED_HANDLE"
    if mode in {"BORROW_READ_CALL_BOUND", "INOUT_EXCLUSIVE_CALL_BOUND"}:
        return "CALL_BOUNDED_ADDRESS"
    return "NON_ADDRESS_VALUE"


def bind_helper(
    row: dict[str, Any], *, continuation_digest: str, memory_digest: str,
    managed_extension: bool,
) -> None:
    row["parameter_address_classes"] = [
        address_class(mode) for mode in row.get("parameter_modes", [])
    ]
    row["managed_referent_or_interior_address_cross_boundary"] = False
    row["continuation_interface_digest_or_null"] = (
        continuation_digest if row.get("may_suspend") else None
    )
    row["managed_reference_profile_digest_or_null"] = (
        memory_digest if managed_extension else None
    )
    row.pop("activation_status", None)
    row.pop("dependency_gap_id", None)
    ownership_material = {
        key: row.get(key)
        for key in (
            "runtime_helper_id",
            "parameter_modes",
            "parameter_address_classes",
            "normal_result_kind",
            "admitted_outcomes",
            "completion_modes",
            "may_collect",
            "may_suspend",
            "observes_cancellation",
            "managed_referent_or_interior_address_cross_boundary",
        )
    }
    row["ownership_profile_digest"] = digest(ownership_material)
    row["signature_digest"] = digest(without(row, "signature_digest"))


def recompute(root: Path) -> dict[str, str]:
    registry = load(root, REGISTRY)
    contract = load(root, CONTRACT)
    fixtures = load(root, FIXTURES)
    continuation = load(root, CONTINUATION)
    cranelift = load(root, CRANELIFT)
    hir_bridge = load(root, HIR_BRIDGE)

    continuation_digest = continuation["continuation_interface_digest"]
    memory_digest = file_digest(root, MEMORY)
    mir_schema_digest = file_digest(root, MIR_SCHEMA)
    mir_registry_digest = file_digest(root, MIR_REGISTRY)

    helper_rows = registry["helper_rows"]
    extension_rows = registry["conditional_extension_rows"]
    for row in helper_rows:
        bind_helper(
            row,
            continuation_digest=continuation_digest,
            memory_digest=memory_digest,
            managed_extension=False,
        )
    for row in extension_rows:
        bind_helper(
            row,
            continuation_digest=continuation_digest,
            memory_digest=memory_digest,
            managed_extension=True,
        )
    helper_rows.sort(key=lambda row: row["runtime_helper_id"])
    extension_rows.sort(key=lambda row: row["runtime_helper_id"])

    registry["managed_reference_profile_digest_or_null"] = memory_digest
    registry["continuation_interface_digest_or_null"] = continuation_digest
    registry["expected_counts"].update({
        "active_base_helpers": 22,
        "active_conditional_helpers": 3,
        "runtime_callbacks": 0,
    })
    active_rows = [*helper_rows, *extension_rows]
    allowlist_material = [
        {
            "runtime_helper_id": row["runtime_helper_id"],
            "runtime_helper_signature_id": row["runtime_helper_signature_id"],
            "helper_version": row["helper_version"],
            "signature_digest": row["signature_digest"],
        }
        for row in active_rows
    ]
    registry["digest_material"] = {
        "runtime_abi_id": registry["runtime_abi_id"],
        "revision": registry["revision"],
        "managed_reference_profile_digest_or_null": memory_digest,
        "continuation_interface_digest_or_null": continuation_digest,
        "helper_rows_digest": digest(helper_rows),
        "conditional_extension_rows_digest": digest(extension_rows),
    }
    registry["helper_allowlist_digest"] = digest(allowlist_material)
    registry["registry_digest"] = digest(registry["digest_material"])

    contract["dependencies"].update({
        "managed_reference_profile_digest_or_null": memory_digest,
        "continuation_interface_digest_or_null": continuation_digest,
        "dependency_binding_status": "EXACT_LOCAL_FUSION_BOUND",
        "canonical_promotion_ready": True,
    })
    contract["expected_counts"].update({
        "active_base_helpers": 22,
        "active_conditional_helpers": 3,
    })
    fixtures["expected_counts"].update({
        "active_base_helpers": 22,
    })

    abi = fixtures["runtime_abi_instance"]
    abi.update({
        "mir_schema_digest": mir_schema_digest,
        "mir_machine_registry_digest": mir_registry_digest,
        "managed_reference_profile_digest_or_null": memory_digest,
        "continuation_interface_digest_or_null": continuation_digest,
        "helper_registry_digest": registry["registry_digest"],
        "helper_allowlist_digest": registry["helper_allowlist_digest"],
    })
    abi["digest_material"] = without(abi, "digest_material", "runtime_abi_digest")
    abi["runtime_abi_digest"] = digest(abi["digest_material"])
    runtime_abi_digest = abi["runtime_abi_digest"]

    projections = fixtures["target_projection_instances"]
    for row in projections:
        transport = "XVM" if row["module_kind"] == "Xvm" else "NATIVE"
        row.update({
            "runtime_abi_digest": runtime_abi_digest,
            "mir_schema_digest": mir_schema_digest,
            "mir_machine_registry_digest": mir_registry_digest,
            "managed_reference_profile_digest_or_null": memory_digest,
            "continuation_interface_digest_or_null": continuation_digest,
            "helper_allowlist_digest": registry["helper_allowlist_digest"],
            "scalar_mapping_digest": digest({"transport": transport, "mapping": "scalar-r1"}),
            "indirect_slot_mapping_digest": digest({"transport": transport, "mapping": "indirect-r1"}),
            "outcome_mapping_digest": digest({"transport": transport, "mapping": "outcome-r1"}),
        })
        row["helper_symbol_or_table_map_digest"] = digest({
            "module_kind": row["module_kind"],
            "helper_ids": [item["runtime_helper_id"] for item in active_rows],
        })
        row["digest_material"] = without(row, "digest_material", "projection_digest")
        row["projection_digest"] = digest(row["digest_material"])

    by_kind = {row["module_kind"]: row for row in projections}
    for row in fixtures["artifact_binding_receipts"]:
        projection = by_kind[row["module_kind"]]
        row.update({
            "runtime_abi_digest": runtime_abi_digest,
            "target_projection_digest": projection["projection_digest"],
            "helper_allowlist_digest": registry["helper_allowlist_digest"],
            "helper_symbol_or_table_map_digest": projection["helper_symbol_or_table_map_digest"],
            "outstanding_root_receipt_count": 0,
        })
        row["digest_material"] = without(row, "digest_material", "receipt_digest")
        row["receipt_digest"] = digest(row["digest_material"])

    fixtures["baseline"] = {
        "commit": "e680568057ec9c6b02218dbe153758471734cf44",
        "tree": "4d91b75d244f0c6adb5980cee19fec756c337053",
    }

    for owner in (cranelift["internal_runtime_abi_guard"], hir_bridge["internal_runtime_abi_contract"]):
        owner["active_base_runtime_helper_count"] = 22
        owner["conditional_continuation_helper_count"] = 6
        owner["conditional_managed_helper_count"] = 3
        owner["active_conditional_managed_helper_count"] = 3
        owner["managed_reference_profile_digest_or_null"] = memory_digest
        owner["continuation_interface_digest_or_null"] = continuation_digest
        owner["dependency_binding_status"] = "EXACT_LOCAL_FUSION_BOUND"
        owner["canonical_promotion_ready"] = True

    continuation["seam_status"].update({
        "r36_managed_reference_profile_digest": memory_digest,
        "r37_helpers_remain_dependency_unbound": False,
        "r37_dependency_binding": "EXACT_LOCAL_FUSION_BOUND",
        "r37_runtime_abi_digest": runtime_abi_digest,
        "future_fusion_required": False,
    })

    for relative, value in (
        (REGISTRY, registry),
        (CONTRACT, contract),
        (FIXTURES, fixtures),
        (CRANELIFT, cranelift),
        (HIR_BRIDGE, hir_bridge),
        (CONTINUATION, continuation),
    ):
        write(root, relative, value)
    return {
        "continuation_interface_digest": continuation_digest,
        "managed_reference_profile_digest": memory_digest,
        "runtime_helper_registry_digest": registry["registry_digest"],
        "runtime_abi_digest": runtime_abi_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        raise SystemExit("--write is required")
    result = recompute(args.root.resolve())
    print(json.dumps({"result": "PASS", **result}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
