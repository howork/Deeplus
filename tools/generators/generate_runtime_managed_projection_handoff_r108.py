#!/usr/bin/env python3
"""Generate the R108 runtime/managed-reference implementation handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CONTRACT_REL = Path("spec/contracts/runtime-managed-projection-handoff-r108.json")
FIXTURE_REL = Path("tests/fixtures/current/runtime-managed-projection-handoff-r108.json")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def managed_abi() -> dict[str, Any]:
    handle = {
        "abi_id": "ManagedHandleAbiId:STABLE_HANDLE_R108",
        "size_bytes": 40,
        "alignment_bytes": 8,
        "fields": [
            {"name": "generation", "offset": 0, "carrier": "U64", "atomic_order": "ACQUIRE_RELEASE"},
            {"name": "state", "offset": 8, "carrier": "U8", "atomic_order": "ACQUIRE_RELEASE"},
            {"name": "referent", "offset": 16, "carrier": "NONNULL_OR_NULL_POINTER64", "atomic_order": "ACQUIRE_RELEASE"},
            {"name": "trace_descriptor_id", "offset": 24, "carrier": "U64", "atomic_order": "IMMUTABLE_WHILE_LIVE"},
            {"name": "cleanup_state", "offset": 32, "carrier": "U8", "atomic_order": "ACQUIRE_RELEASE"},
        ],
        "state_order": ["FREE", "RESERVED", "INITIALIZING", "LIVE", "RETIRED", "FREE"],
        "generation_rule": "increment before FREE slot reuse; U64 overflow permanently retires the slot",
        "raw_address_is_semantic_identity": False,
    }
    root_slot = {
        "abi_id": "ManagedRootSlotAbiId:R108",
        "size_bytes": 24,
        "alignment_bytes": 8,
        "fields": [
            {"name": "root_id", "offset": 0, "carrier": "U64"},
            {"name": "handle_slot_address", "offset": 8, "carrier": "POINTER64"},
            {"name": "expected_generation", "offset": 16, "carrier": "U64"},
        ],
    }
    frame = {
        "abi_id": "ShadowRootFrameAbiId:R108",
        "header_size_bytes": 24,
        "alignment_bytes": 8,
        "fields": [
            {"name": "previous_frame", "offset": 0, "carrier": "NULLABLE_POINTER64"},
            {"name": "slot_count", "offset": 8, "carrier": "U32"},
            {"name": "frame_state", "offset": 12, "carrier": "U8"},
            {"name": "activation_epoch", "offset": 16, "carrier": "U64"},
        ],
        "trailing_slot_abi_id": root_slot["abi_id"],
        "frame_state_order": ["DETACHED", "ACTIVE", "SUSPENDED", "RETIRED"],
        "push_pop_rule": "strict LIFO per runtime thread; unwind and cancellation pop exactly once",
        "suspension_rule": "ACTIVE frame becomes SUSPENDED and transfers to the continuation receipt before thread detachment",
    }
    registry = {
        "registry_id": "RuntimeRootRegistryId:R108",
        "partitions": ["RUNNING", "FRAME", "RUNTIME"],
        "equation": "sorted_unique(running_root_ids | frame_root_ids | runtime_root_ids)",
        "duplicate_missing_unsorted_or_stale_generation": "REJECT_PROJECTION",
        "scan_rule": "load state and generation with acquire semantics; trace only LIVE handles whose generation equals expected_generation",
        "jit_lifetime_rule": "a finalized image remains live while any active call, suspended continuation, or root receipt references it",
        "implicit_backend_root_count": 0,
    }
    for item in (handle, root_slot, frame, registry):
        item["digest"] = digest(item)
    return {
        "managed_handle_abi": handle,
        "managed_root_slot_abi": root_slot,
        "shadow_root_frame_abi": frame,
        "runtime_root_registry": registry,
        "safepoint_helpers": [
            "RuntimeHelperId:managed.safepoint_enter",
            "RuntimeHelperId:managed.safepoint_leave",
        ],
        "implicit_backend_safepoint_count": 0,
    }


def projection(root: Path, mapping: dict[str, Any], managed: dict[str, Any], runtime_abi_digest: str) -> dict[str, Any]:
    module = mapping["module_kind"]
    stack_alignment = 8 if module == "Xvm" else 16
    toolchain = {
        "rust_version": "1.85.0",
        "cargo_lock_sha256": file_digest(root / "Cargo.lock"),
        "module_kind": module,
        "target_triple": mapping["target_triple"],
        "cranelift_version_or_null": None if module == "Xvm" else "0.121.2",
        "dependency_connected": False,
        "product_execution": "NOT_RUN",
    }
    material = {
        "schema": "deeplus.internal-runtime-abi-target-projection/r108",
        "projection_id": mapping["projection_id"].replace("/r99", "/r108"),
        "runtime_abi_id": "RuntimeAbiId:DEEPLUS_INTERNAL_RUNTIME_ABI_R1",
        "runtime_abi_digest": runtime_abi_digest,
        "mir_schema_digest": file_digest(root / "schemas/language/deeplus-mir.schema.json"),
        "mir_machine_registry_digest": file_digest(root / "spec/contracts/mir-machine-registry.json"),
        "target_triple": mapping["target_triple"],
        "pointer_width": mapping["pointer_width"],
        "endianness": mapping["endianness"],
        "stack_alignment_bytes": stack_alignment,
        "calling_convention": mapping["calling_convention"],
        "module_kind": module,
        "scalar_mapping_digest": digest(mapping["scalar_mapping_rows"]),
        "indirect_slot_mapping_digest": digest(mapping["indirect_slot_mapping"]),
        "outcome_mapping_digest": digest(mapping["outcome_mapping_rows"]),
        "helper_allowlist_digest": digest(sorted(row["runtime_helper_id"] for row in mapping["helper_mapping_rows"])),
        "helper_symbol_or_table_map_digest": digest(mapping["helper_mapping_rows"]),
        "toolchain_digest": digest(toolchain),
        "managed_reference_profile_digest": file_digest(root / "spec/contracts/managed-reference-memory-profile-r1.json"),
        "continuation_interface_digest": file_digest(root / "spec/contracts/continuation-interface-r1.json"),
        "managed_handle_abi_digest": managed["managed_handle_abi"]["digest"],
        "shadow_root_frame_abi_digest": managed["shadow_root_frame_abi"]["digest"],
        "runtime_root_registry_digest": managed["runtime_root_registry"]["digest"],
        "mapping_preimage_digest": mapping["mapping_digest"],
        "target_location_is_semantic_identity": False,
    }
    return {
        **material,
        "toolchain_preimage": toolchain,
        "helper_mapping_count": len(mapping["helper_mapping_rows"]),
        "logical_value_kind_count": len(mapping["scalar_mapping_rows"]),
        "projection_digest": digest(material),
        "product_execution": "NOT_RUN",
    }


def build(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    mappings = load(root / "spec/contracts/runtime-target-mapping-registry-r99.json")
    managed = managed_abi()
    runtime_fixture = load(root / "tests/fixtures/current/internal-runtime-abi-r1.json")
    runtime_abi_digest = runtime_fixture["runtime_abi_instance"]["runtime_abi_digest"]
    projections = [projection(root, row, managed, runtime_abi_digest) for row in mappings["target_mappings"]]
    contract = {
        "$schema": "../../schemas/language/runtime-managed-projection-handoff-r108.schema.json",
        "schema": "deeplus.runtime-managed-projection-handoff/r108",
        "revision": "r108-runtime-managed-projection-implementation-handoff",
        "status": "LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF_COMPLETE_PRODUCT_NOT_RUN",
        "baseline": {
            "repository": "howork/Deeplus",
            "branch": "codex/preimpl-p0-r80-authority-projection-parity",
            "commit": "94bb739bc8d541c90ef88526f86075d1c9ef4e9f",
            "tree": "9462517520544476b3d72f998c66dda50f70aa4a",
        },
        "source_bindings": {
            "runtime_target_mapping_registry": "spec/contracts/runtime-target-mapping-registry-r99.json",
            "runtime_helper_registry": "spec/contracts/runtime-helper-registry-r1.json",
            "runtime_record_registry": "spec/contracts/runtime-abi-record-registry-r99.json",
            "managed_reference_profile": "spec/contracts/managed-reference-memory-profile-r1.json",
            "continuation_interface": "spec/contracts/continuation-interface-r1.json",
            "mir_machine_registry": "spec/contracts/mir-machine-registry.json",
        },
        "managed_native_abi": managed,
        "target_projections": projections,
        "implementation_invariants": {
            "target_projection_count": 3,
            "module_kinds": ["Xvm", "ObjectAot", "InMemoryJit"],
            "logical_value_kind_count_per_projection": 20,
            "helper_mapping_count_per_projection": 25,
            "host_default_count": 0,
            "aot_jit_logical_mapping_equal": all(
                projections[1][field] == projections[2][field]
                for field in (
                    "scalar_mapping_digest",
                    "indirect_slot_mapping_digest",
                    "outcome_mapping_digest",
                    "helper_allowlist_digest",
                )
            ),
            "implicit_backend_safepoint_count": 0,
            "raw_address_semantic_identity_count": 0,
        },
        "acceptance": {
            "positive": 4,
            "boundary": 4,
            "reject": 8,
            "mutation_count": 12,
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        },
        "governance": {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_execution": "NOT_RUN",
            "current_binding": False,
            "github_mutation": 0,
        },
    }
    cases = []
    scenarios = [
        ("P", "positive", "all three target projections bind exact local preimages", "ADMIT_STATIC"),
        ("P", "positive", "managed handle generation advances before reuse", "ADMIT_STATIC"),
        ("P", "positive", "shadow-root frame push and pop are balanced", "ADMIT_STATIC"),
        ("P", "positive", "suspended continuation retains its finalized JIT image", "ADMIT_STATIC"),
        ("B", "boundary", "generation overflow retires rather than reuses a handle slot", "ADMIT_WITH_PERMANENT_RETIREMENT"),
        ("B", "boundary", "empty shadow-root frame is represented with slot_count zero", "ADMIT_STATIC"),
        ("B", "boundary", "cancellation pops an active root frame exactly once", "ADMIT_STATIC"),
        ("B", "boundary", "Xvm uses logical slots while native targets use shadow roots", "ADMIT_STATIC"),
        ("R", "reject", "one helper signature digest is stale", "REJECT_TARGET_PROJECTION"),
        ("R", "reject", "stack alignment is inherited from the host", "REJECT_TARGET_PROJECTION"),
        ("R", "reject", "AOT and JIT mapping preimages diverge", "REJECT_TARGET_PROJECTION"),
        ("R", "reject", "managed handle generation mismatches a root receipt", "REJECT_ROOT_PROJECTION"),
        ("R", "reject", "a root frame is missing or popped twice", "REJECT_ROOT_PROJECTION"),
        ("R", "reject", "an implicit Cranelift safepoint is inserted", "REJECT_TARGET_PROJECTION"),
        ("R", "reject", "a finalized JIT image is retired with an active lease", "REJECT_JIT_RETIREMENT"),
        ("R", "reject", "a runtime address is used as semantic identity", "REJECT_IDENTITY_CONFLATION"),
    ]
    for index, (prefix, kind, scenario, expected) in enumerate(scenarios, 1):
        cases.append({
            "case_id": f"R108-{prefix}-{index:03d}",
            "class": kind,
            "scenario": scenario,
            "expected": expected,
            "execution_state": "DESIGN_STATIC_NOT_RUN",
        })
    fixture = {
        "schema": "deeplus.runtime-managed-projection-handoff-fixtures/r108",
        "revision": contract["revision"],
        "contract_path": CONTRACT_REL.as_posix(),
        "cases": cases,
        "product_execution": "NOT_RUN",
    }
    return contract, fixture


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract, fixture = build(root)
    expected = {CONTRACT_REL: contract, FIXTURE_REL: fixture}
    stale = []
    for rel, value in expected.items():
        path = root / rel
        encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded.encode("utf-8"))
        elif not path.is_file() or path.read_text(encoding="utf-8") != encoded:
            stale.append(rel.as_posix())
    print(json.dumps({"schema": "deeplus.r108-generator-receipt/v1", "result": "PASS" if not stale or args.write else "FAIL", "mode": "WRITE" if args.write else "CHECK", "stale": stale, "target_projections": 3, "product_execution": "NOT_RUN"}, sort_keys=True))
    return 0 if not stale or args.write else 1


if __name__ == "__main__":
    raise SystemExit(main())
