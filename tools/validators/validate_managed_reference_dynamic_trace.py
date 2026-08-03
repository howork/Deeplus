#!/usr/bin/env python3
"""Validate the bounded R69 managed-reference dynamic trace closure.

This validator is design-static.  It does not execute a collector, xVM,
Cranelift, or any product lane.  In-memory overrides are intentionally exposed
for the focused mutation runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


BASELINE = "a84fd17137b8e2f8f620be8c7f0f96afd627a9e1"
CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
REVISION = "r69-local-managed-reference-dynamic-trace-closure-r1"
FEATURE = "managed_reference_memory_profile_phase1"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
CONTINUATION_ID = "ContinuationInterfaceId:DEEPLUS_CONTINUATION_INTERFACE_R1"
R36_SHA256 = "feff3c021d4b77e64e4e9f00f797b0ce2c465a5b60709d86d0baf7bded72c7f7"
R37_SHA256 = "fa905282037bdda3d3eb122d74f467ae611ea1ca7d355b0efb49c02fb6f93ba0"
NON_TARGET_SHA256 = "d29120dc5d88c5381ba1ca09ed927720deba9f20a05ba6f9cca325049f777165"

CONTRACT = "spec/contracts/managed-reference-dynamic-projection-r1.json"
CONTRACT_SCHEMA = "schemas/language/managed-reference-dynamic-projection-r1.schema.json"
MANAGED = "spec/contracts/managed-reference-memory-profile-r1.json"
PLAN_SCHEMA = "schemas/language/managed-reference-memory-profile-r1.schema.json"
RUNTIME_RECEIPT_SCHEMA = "schemas/language/managed-reference-runtime-root-receipt-r1.schema.json"
NATIVE_RECEIPT_SCHEMA = "schemas/language/managed-reference-native-projection-receipt-r1.schema.json"
FIXTURE = "tests/fixtures/current/managed-reference-dynamic-projection-r1.json"
FIXTURE_SCHEMA = "schemas/language/managed-reference-dynamic-projection-fixtures-r1.schema.json"
CONTINUATION = "spec/contracts/continuation-interface-r1.json"
INTERNAL = "spec/contracts/internal-runtime-abi-r1.json"
HELPERS = "spec/contracts/runtime-helper-registry-r1.json"
HIR = "schemas/language/canonical-hir-h1.schema.json"
MIR = "schemas/language/deeplus-mir.schema.json"
LOWERING = "spec/contracts/hir-mir-lowering-registry.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
MACHINE = "spec/contracts/mir-machine-registry.json"
CRANELIFT = "spec/contracts/cranelift-backend-current.json"
REGION = "spec/contracts/region-lifetime-mir-projection-r1.json"
OVERLAY = "spec/traceability/implementation-target-profile-r1/managed-reference-dynamic-trace-evidence-r1.json"
OVERLAY_SCHEMA = "schemas/language/managed-reference-dynamic-trace-evidence-r1.schema.json"
ROWS = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
DECISION = "decisions/language/Design_Deeplus_R69_Managed_Reference_Dynamic_Trace_Closure_R1.md"

JSON_PATHS = (
    CONTRACT, CONTRACT_SCHEMA, MANAGED, PLAN_SCHEMA, RUNTIME_RECEIPT_SCHEMA,
    NATIVE_RECEIPT_SCHEMA, FIXTURE, FIXTURE_SCHEMA, CONTINUATION, INTERNAL,
    HELPERS, HIR, MIR, LOWERING, BRIDGE, MACHINE, CRANELIFT, REGION, OVERLAY,
    OVERLAY_SCHEMA, ROWS, METADATA,
)

PROTECTED_R68 = {
    "spec/contracts/region-lifetime-mir-projection-r1.json": "8807046bb7d9164b8d9c8aaf209a5f3064c051ade9219576ef8a546a3642ca77",
    "schemas/language/region-lifetime-mir-projection-r1.schema.json": "a98df665f7bd20a8d7e079b72852f113c2ebd4f5e89a7d8c42f2423e03d62b9f",
    "spec/traceability/implementation-target-profile-r1/region-lifetime-dynamic-trace-evidence-r1.json": "fa7c36221c90c0524504ea8a2b8df9ab574cd2e791a80073ecb15affef28d389",
    "schemas/language/region-lifetime-dynamic-trace-evidence-r1.schema.json": "6068e688032a00ac25ba9197c93257b0f762a5bdb33b017fe8ae80475eb23df6",
    "decisions/language/Design_Deeplus_R68_Region_Lifetime_Dynamic_Trace_Closure_R1.md": "b643b85394b23204715c2e0cb0cd428e8399c046c4327d6b29ed5a85310696bf",
    "tools/validators/validate_region_lifetime_dynamic_trace.py": "3d0a40b79dbd1ea7bb4b8e5b9afb28204dbf3b235d22dac6a5491e3e737040fe",
    "tools/validators/run_region_lifetime_dynamic_trace_mutation_tests.py": "9bab831f61909af072cda60577464d677cdf9458adfd1a317bd1a491cb192926",
}

GATES = {
    "G01": "identity_schema_and_predecessor",
    "G02": "current_continuation_seam",
    "G03": "static_plan_runtime_receipt_split",
    "G04": "full_fixture_and_projection_examples",
    "G05": "hir_mir_trace_and_typed_identity",
    "G06": "runtime_helper_projection_mapping",
    "G07": "bridge_machine_and_cranelift_binding",
    "G08": "exact_r69_overlay",
    "G09": "generated_target_and_non_target_fence",
    "G10": "governance_and_r68_protection",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_inputs(root: Path) -> Dict[str, Any]:
    return {relative: load(root / relative) for relative in JSON_PATHS}


def git_blob_sha256(root: Path, commit: str, relative: str) -> str:
    proc = subprocess.run(
        [
            "git", "-c", "safe.directory=" + root.as_posix(), "-C", str(root),
            "show", commit + ":" + relative,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return sha256_bytes(proc.stdout)


def trace_cells(rows: List[Dict[str, Any]]) -> Tuple[Dict[Tuple[str, str, Optional[str]], Dict[str, Any]], int]:
    cells: Dict[Tuple[str, str, Optional[str]], Dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        for stage in row.get("stages", []):
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage.get("stage") == "CONFORMANCE_TESTS" else None
                key = (row.get("feature_id"), stage.get("stage"), outcome)
                if key in cells:
                    duplicates += 1
                cells[key] = cell
    return cells, duplicates


def non_target_digest(cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]]) -> Tuple[int, str]:
    material = [[*key, value] for key, value in cells.items() if key != TARGET]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), sha256_bytes(raw)


def contains_key(value: Any, forbidden: set) -> bool:
    if isinstance(value, dict):
        return bool(forbidden & set(value)) or any(
            contains_key(item, forbidden) for item in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(item, forbidden) for item in value)
    return False


def validate(
    root: Path,
    *,
    overrides: Optional[Mapping[str, Any]] = None,
    predecessor_hashes_override: Optional[Mapping[str, str]] = None,
    protected_drift: bool = False,
) -> List[str]:
    errors: List[str] = []
    values = load_inputs(root)
    if overrides:
        values.update(overrides)

    def value(relative: str) -> Any:
        return values[relative]

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(gate + ":" + code)

    contract = value(CONTRACT)
    managed = value(MANAGED)
    continuation = value(CONTINUATION)
    internal = value(INTERNAL)
    helpers = value(HELPERS)
    plan_schema = value(PLAN_SCHEMA)
    runtime_schema = value(RUNTIME_RECEIPT_SCHEMA)
    fixture = value(FIXTURE)
    hir = value(HIR)
    mir = value(MIR)
    lowering = value(LOWERING)
    bridge = value(BRIDGE)
    machine = value(MACHINE)
    cranelift = value(CRANELIFT)
    region = value(REGION)
    overlay = value(OVERLAY)
    rows = value(ROWS)
    metadata = value(METADATA)

    # G01: identities, schemas, and exact predecessor bytes.
    require(
        contract.get("schema") == "deeplus.managed-reference-dynamic-projection/r1"
        and contract.get("revision") == REVISION
        and contract.get("canonical_baseline_commit") == BASELINE
        and contract.get("feature_id") == FEATURE
        and contract.get("gap_id") == "IR-XCUT-P1-054",
        "G01", "R69_IDENTITY",
    )
    expected_predecessors = {
        MANAGED: R36_SHA256,
        INTERNAL: R37_SHA256,
    }
    declared_predecessors = {
        row.get("path"): row.get("file_sha256")
        for row in contract.get("predecessors", [])
    }
    require(declared_predecessors == expected_predecessors, "G01", "PREDECESSOR_DECLARATION")
    if predecessor_hashes_override is None:
        try:
            predecessor_hashes = {
                relative: git_blob_sha256(root, BASELINE, relative)
                for relative in expected_predecessors
            }
        except (OSError, subprocess.CalledProcessError):
            predecessor_hashes = {}
    else:
        predecessor_hashes = dict(predecessor_hashes_override)
    require(predecessor_hashes == expected_predecessors, "G01", "PREDECESSOR_BLOB_BYTES")
    try:
        from jsonschema import Draft202012Validator
        schema_pairs = (
            (value(CONTRACT_SCHEMA), contract),
            (value(FIXTURE_SCHEMA), fixture),
            (plan_schema, fixture.get("static_plan")),
            (runtime_schema, fixture.get("runtime_root_receipt")),
            (value(OVERLAY_SCHEMA), overlay),
        )
        for schema, instance in schema_pairs:
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(instance)
        native_schema = value(NATIVE_RECEIPT_SCHEMA)
        Draft202012Validator.check_schema(native_schema)
        for instance in fixture.get("native_projection_receipts", []):
            Draft202012Validator(native_schema).validate(instance)
    except ImportError:
        pass
    except Exception:
        require(False, "G01", "DRAFT202012_VALIDATION")

    # G02: derive one current continuation digest and bind every active seam.
    current_digest = continuation.get("continuation_interface_digest")
    require(
        isinstance(current_digest, str)
        and len(current_digest) == 64
        and all(char in "0123456789abcdef" for char in current_digest),
        "G02", "CONTINUATION_CURRENT_DIGEST",
    )
    authority = contract.get("authority_binding", {})
    require(
        authority.get("continuation_interface_id") == CONTINUATION_ID
        and authority.get("continuation_interface_digest") == current_digest
        and authority.get("continuation_contract_path") == CONTINUATION,
        "G02", "SUCCESSOR_AUTHORITY_BINDING",
    )
    active_seams = [
        managed.get("dependency_guard", {}).get("continuation_root_interface_digest"),
        managed.get("suspension_root_transfer", {}).get("continuation_root_interface_digest"),
        internal.get("dependencies", {}).get("continuation_interface_digest_or_null"),
        internal.get("dispatcher_contract", {}).get("bounded_continuation_dispatch", {}).get("continuation_interface_digest"),
        helpers.get("continuation_interface_digest_or_null"),
        lowering.get("continuation_frame_mapping", {}).get("continuation_interface_digest"),
        bridge.get("suspension_frame_responsibility_bridge", {}).get("continuation_interface_digest"),
        bridge.get("internal_runtime_abi_contract", {}).get("continuation_interface_digest_or_null"),
        cranelift.get("internal_runtime_abi_guard", {}).get("continuation_interface_digest_or_null"),
    ]
    require(all(item == current_digest for item in active_seams), "G02", "ACTIVE_SEAM_EXACT")
    stale = contract.get("stale_pointer_supersession", {})
    require(
        stale.get("stale_digest") == "0dc4891d1d23da397012f1ec1956ba1a3b52e884dbec604d27c8561a09941271"
        and stale.get("successor_digest") == current_digest
        and stale.get("pointer_count") == len(stale.get("pointers", [])) == 3,
        "G02", "STALE_POINTER_SUPERSESSION",
    )

    # G03: static plans contain templates only; runtime receipts own generations.
    plan_defs = plan_schema.get("$defs", {})
    root_entry = plan_defs.get("rootEntry", {})
    root_map = plan_defs.get("rootMap", {})
    rebind = plan_defs.get("rootRebindPair", {})
    static_forbidden = {
        "handle_generation", "receipt_lifecycle", "source_handle_generation",
        "destination_handle_generation",
    }
    require(
        not (static_forbidden & set(root_entry.get("properties", {})))
        and not (static_forbidden & set(root_entry.get("required", [])))
        and "receipt_lifecycle" not in root_map.get("properties", {})
        and "receipt_lifecycle" not in root_map.get("required", [])
        and "receiptLifecycle" not in plan_defs
        and not (static_forbidden & set(rebind.get("properties", {})))
        and set(rebind.get("required", [])) == {"source_root_id", "destination_root_id"}
        and not contains_key(fixture.get("static_plan", {}), static_forbidden),
        "G03", "STATIC_PLAN_RUNTIME_FIELD_FENCE",
    )
    runtime_required = set(runtime_schema.get("required", []))
    runtime_entry = runtime_schema.get("$defs", {}).get("runtimeRootEntry", {})
    runtime_rebind = runtime_schema.get("$defs", {}).get("suspensionRebindReceipt", {})
    lifecycle = runtime_schema.get("$defs", {}).get("receiptLifecycle", {})
    require(
        {"managed_memory_plan_id", "managed_memory_plan_digest", "body_id", "safepoint_id", "root_map_id", "root_entries", "lifecycle"}.issubset(runtime_required)
        and "handle_generation" in runtime_entry.get("required", [])
        and runtime_entry.get("properties", {}).get("handle_generation", {}).get("minimum") == 0
        and {"source_handle_generation", "destination_handle_generation", "distinct_root_ids", "same_handle_generation"}.issubset(runtime_rebind.get("required", []))
        and set(lifecycle.get("required", [])) == {"verified_before_publish", "published_before_operation_entry", "live_through_outcome_commit", "released_after_outcome_commit"}
        and all(row.get("const") is True for row in lifecycle.get("properties", {}).values()),
        "G03", "RUNTIME_RECEIPT_GENERATION_LIFECYCLE",
    )

    # G04: one complete static plan, one runtime receipt, two native examples.
    counts = fixture.get("expected_counts", {})
    mutations = fixture.get("declared_mutations", [])
    natives = fixture.get("native_projection_receipts", [])
    require(
        counts == {
            "static_plans": 1, "runtime_root_receipts": 1,
            "native_projection_receipts": 2, "declared_mutations": 14,
            "semantic_p0": 0, "open_feature_p1": 22,
            "open_m13_actions": 4, "product_lanes": 15,
            "product_executed": 0,
        }
        and len(mutations) == len({row.get("mutation_id") for row in mutations}) == 14
        and all(row.get("execution_state") == "DECLARED_NOT_RUN" for row in mutations)
        and [row.get("module_kind") for row in natives] == ["ObjectAot", "InMemoryJit"],
        "G04", "FIXTURE_CARDINALITY_AND_NOT_RUN",
    )
    plan = fixture.get("static_plan", {})
    receipt = fixture.get("runtime_root_receipt", {})
    bodies = {row.get("body_id"): row for row in plan.get("bodies", [])}
    body = bodies.get(receipt.get("body_id"), {})
    safepoints = {row.get("safepoint_id"): row for row in body.get("safepoint_table", [])}
    root_maps = {row.get("root_map_id"): row for row in body.get("root_map_table", [])}
    safepoint = safepoints.get(receipt.get("safepoint_id"), {})
    root_map_value = root_maps.get(receipt.get("root_map_id"), {})
    static_entries = root_map_value.get("entries", [])
    runtime_entries = receipt.get("root_entries", [])
    runtime_static_projection = [
        {key: item for key, item in row.items() if key != "handle_generation"}
        for row in runtime_entries
    ]
    root_ids = [row.get("root_id") for row in runtime_entries]
    require(
        receipt.get("managed_memory_plan_id") == plan.get("plan_id")
        and receipt.get("managed_memory_plan_digest") == plan.get("plan_semantic_digest")
        and safepoint.get("root_map_id") == receipt.get("root_map_id")
        and receipt.get("canonical_root_set_digest") == root_map_value.get("canonical_root_set_digest")
        and runtime_static_projection == static_entries
        and root_ids == sorted(root_ids) and len(root_ids) == len(set(root_ids))
        and receipt.get("root_entry_order") == "ROOT_ID_ASCENDING_UNIQUE"
        and all(isinstance(row.get("handle_generation"), int) and row.get("handle_generation") >= 0 for row in runtime_entries)
        and all(receipt.get("lifecycle", {}).values()),
        "G04", "FULL_PLAN_RUNTIME_RECEIPT_BINDING",
    )
    static_pairs = {
        (row.get("source_root_id"), row.get("destination_root_id"))
        for transfer in body.get("suspension_transfer_table", [])
        for row in transfer.get("root_rebind_pairs", [])
    }
    runtime_pairs = receipt.get("suspension_rebind_receipts", [])
    require(
        all((row.get("source_root_id"), row.get("destination_root_id")) in static_pairs for row in runtime_pairs)
        and all(row.get("source_root_id") != row.get("destination_root_id") for row in runtime_pairs)
        and all(row.get("source_handle_generation") == row.get("destination_handle_generation") for row in runtime_pairs)
        and all(row.get("distinct_root_ids") is True and row.get("same_handle_generation") is True for row in runtime_pairs),
        "G04", "SUSPENSION_RUNTIME_REBIND",
    )
    if len(natives) == 2:
        parity_fields = (
            "mir_semantic_digest", "managed_memory_profile_digest",
            "managed_memory_plan_digest", "managed_root_receipt_schema_digest",
            "continuation_root_interface_digest", "handle_abi_digest",
            "shadow_root_frame_abi_digest", "safepoint_projection_digest",
            "runtime_abi_digest", "semantic_parity_trace_digest",
        )
        require(
            all(natives[0].get(key) is not None for key in parity_fields)
            and all(natives[0].get(key) == natives[1].get(key) for key in parity_fields)
            and all(row.get("managed_root_receipt_schema_digest") == sha256_file(root / RUNTIME_RECEIPT_SCHEMA) for row in natives)
            and all(row.get("managed_memory_plan_digest") == plan.get("plan_semantic_digest") for row in natives)
            and all(row.get("continuation_root_interface_digest") == current_digest for row in natives)
            and all(row.get("target_location_is_semantic_identity") is False for row in natives),
            "G04", "NATIVE_PROJECTION_PARITY",
        )

    # G05: exact HIR -> MIR trace mapping; RootId is not a region/loan identity.
    hir_defs = hir.get("$defs", {})
    mir_defs = mir.get("$defs", {})
    hir_type = hir_defs.get("NormalizedTypeDescriptor", {})
    hir_descriptor = hir_defs.get("ManagedTraceDescriptor", {})
    hir_module = hir_defs.get("CanonicalModuleBase", {})
    mir_type = mir_defs.get("typeEntry", {})
    mir_descriptor = mir_defs.get("managedTraceDescriptor", {})
    hir_descriptor_table = hir_module.get("properties", {}).get("managed_trace_descriptors", {})
    mir_descriptor_table = mir.get("properties", {}).get("managed_trace_descriptor_table", {})
    require(
        "managed_trace_descriptor_id_or_null" not in hir_type.get("required", [])
        and "managed_trace_descriptor_id_or_null" not in hir_type.get("properties", {})
        and "managed_trace_descriptors" in hir_module.get("required", [])
        and set(hir_descriptor.get("required", [])) == {"normalized_type_id", "trace_kind", "ordered_managed_projection_ids"}
        and hir_descriptor_table.get("x-deeplus-unique-key") == "normalized_type_id"
        and "managed_trace_descriptor_id_or_null" not in mir_type.get("required", [])
        and "managed_trace_descriptor_id_or_null" not in mir_type.get("properties", {})
        and set(mir_descriptor.get("required", [])) == {"type_id", "trace_kind", "ordered_managed_projection_ids"}
        and mir_descriptor_table.get("x-deeplus-unique-by") == "type_id",
        "G05", "HIR_MIR_TRACE_DESCRIPTOR_SHAPE",
    )
    mapping = lowering.get("managed_reference_dynamic_projection", {})
    bridge_contract = bridge.get("managed_reference_dynamic_projection_contract", {})
    region_fence = contract.get("projection_contract", {}).get("region_loan_fence", {})
    require(
        mapping.get("hir_type_binding") == "CanonicalModuleBase.managed_trace_descriptors is keyed exactly by existing NormalizedTypeId"
        and mapping.get("mir_type_binding") == "managed_trace_descriptor_table is keyed exactly by existing TypeId"
        and mapping.get("identity_preservation") == "EXACT_HIR_TO_MIR"
        and bridge_contract.get("hir_descriptor_table") == "CanonicalModuleBase.managed_trace_descriptors keyed by existing NormalizedTypeId"
        and bridge_contract.get("mir_descriptor_table") == "managed_trace_descriptor_table keyed by existing TypeId"
        and bridge_contract.get("static_plan_descriptor_identity") == "ManagedTraceDescriptorId derived deterministically from TypeId"
        and contract.get("counts", {}).get("new_hir_identity_kind_count") == 0
        and mapping.get("root_id_equals_region_id_or_loan_id_count") == 0
        and mapping.get("borrowed_or_inout_view_creates_root_count") == 0
        and region_fence.get("region_id_or_loan_id_is_root_id") is False
        and region_fence.get("borrowed_or_inout_view_creates_independent_root") is False
        and region_fence.get("root_liveness_extends_region_or_loan") is False
        and region.get("projection_contract", {}).get("suspension_and_isolation", {}).get("ordinary_or_exclusive_cross_suspension") == "REJECT",
        "G05", "ROOT_REGION_LOAN_FENCE",
    )

    # G06: allocate is MIR INVOKE; enter/leave are target projection phases.
    managed_rows = {
        row.get("operation"): row
        for row in helpers.get("conditional_extension_rows", [])
        if str(row.get("runtime_helper_id", "")).startswith("RuntimeHelperId:managed.")
    }
    allocate = managed_rows.get("MANAGED_ALLOCATE_SLOW", {})
    enter = managed_rows.get("MANAGED_SAFEPOINT_ENTER", {})
    leave = managed_rows.get("MANAGED_SAFEPOINT_LEAVE", {})
    require(
        set(managed_rows) == {"MANAGED_ALLOCATE_SLOW", "MANAGED_SAFEPOINT_ENTER", "MANAGED_SAFEPOINT_LEAVE"}
        and allocate.get("terminator_kind") == "INVOKE"
        and allocate.get("projection_phase_or_null") is None
        and allocate.get("may_collect") is True
        and enter.get("terminator_kind") == "TARGET_PROJECTION_STEP"
        and enter.get("projection_phase_or_null") == "BEFORE_MAY_COLLECT_ENTRY"
        and enter.get("may_collect") is True
        and leave.get("terminator_kind") == "TARGET_PROJECTION_STEP"
        and leave.get("projection_phase_or_null") == "AFTER_OUTCOME_COMMIT"
        and leave.get("may_collect") is False,
        "G06", "MANAGED_HELPER_EXACT_MAPPING",
    )
    require(
        contract.get("projection_contract", {}).get("cross_path_parity", {}).get("backend_root_or_safepoint_inference_count") == 0
        and cranelift.get("managed_reference_guard", {}).get("implicit_backend_safepoint_count") == 0,
        "G06", "NO_IMPLICIT_BACKEND_SAFEPOINT",
    )

    # G07: bridge, MIR capability, and Cranelift consume the successor contract.
    expected_contract = CONTRACT
    expected_plan = "deeplus.managed-memory-plan/r1"
    expected_receipt = "deeplus.managed-reference-runtime-root-receipt/r1"
    bridge_contract = bridge.get("managed_reference_dynamic_projection_contract", {})
    native_guard = bridge.get("native_projection_contract", {}).get("managed_reference_guard", {})
    capabilities = {row.get("capability_id"): row for row in machine.get("capabilities", [])}
    capability = capabilities.get("DM-CAP-SAFEPOINT-ROOTMAP-R1", {})
    cranelift_guard = cranelift.get("managed_reference_guard", {})
    require(
        bridge_contract.get("contract") == expected_contract
        and bridge_contract.get("static_plan_schema") == expected_plan
        and bridge_contract.get("runtime_root_receipt_schema") == expected_receipt
        and bridge_contract.get("exact_descriptor_identity_preservation") is True
        and native_guard.get("dynamic_projection_contract") == expected_contract
        and native_guard.get("managed_memory_plan_schema") == expected_plan
        and native_guard.get("managed_root_receipt_schema") == expected_receipt
        and native_guard.get("static_plan_contains_runtime_generation_or_receipt_lifecycle") is False
        and capability.get("managed_dynamic_projection_contract") == expected_contract
        and capability.get("managed_memory_plan_schema") == expected_plan
        and capability.get("managed_root_receipt_schema") == expected_receipt
        and capability.get("static_plan_runtime_generation_field_count") == 0
        and cranelift_guard.get("dynamic_projection_contract") == expected_contract
        and cranelift_guard.get("managed_memory_plan_schema") == expected_plan
        and cranelift_guard.get("managed_root_receipt_schema") == expected_receipt
        and cranelift_guard.get("static_plan_contains_runtime_generation_or_receipt_lifecycle") is False
        and cranelift_guard.get("managed_safepoint_enter_leave_are_target_projection_steps") is True
        and cranelift_guard.get("managed_allocate_slow_mir_terminator") == "INVOKE"
        and cranelift_guard.get("raw_pointer_fallback") is False,
        "G07", "SUCCESSOR_CROSS_BINDING",
    )
    native_required = set(value(NATIVE_RECEIPT_SCHEMA).get("required", []))
    require("managed_root_receipt_schema_digest" in native_required, "G07", "NATIVE_RECEIPT_ROOT_SCHEMA_DIGEST")

    # G08: overlay changes exactly one target cell and binds all 14 cases.
    acceptance_ids = [row.get("case_id") for row in contract.get("acceptance_matrix", [])]
    require(
        overlay.get("schema") == "deeplus.managed-reference-dynamic-trace-evidence/r1"
        and overlay.get("revision") == REVISION
        and overlay.get("canonical_baseline_commit") == CANONICAL
        and overlay.get("local_predecessor_commit") == BASELINE
        and overlay.get("feature_ids") == [FEATURE]
        and len(overlay.get("evidence_entries", [])) == 1
        and overlay.get("evidence_entries", [{}])[0].get("path") == CONTRACT
        and overlay.get("evidence_entries", [{}])[0].get("locator") == "/projection_contract"
        and overlay.get("bindings") == [{
            "feature_id": FEATURE, "stage": "DYNAMIC_LOWERING", "outcome": None,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": "BOUND_DIRECT",
            "evidence_keys": ["R69:managed_reference_memory_profile_phase1:DYNAMIC_LOWERING:PROJECTION_CONTRACT"],
            "delegate_feature_id": None, "not_applicable": None,
        }]
        and len(acceptance_ids) == len(set(acceptance_ids)) == 14
        and overlay.get("acceptance_cases", [{}])[0].get("acceptance_case_ids") == acceptance_ids,
        "G08", "OVERLAY_EXACT",
    )

    # G09: generated target is direct and every other atomic cell is byte-stable.
    cells, duplicates = trace_cells(rows)
    target = cells.get(TARGET, {})
    count, digest = non_target_digest(cells)
    registrations = [
        row for row in metadata.get("evidence_registry", [])
        if row.get("path") == CONTRACT
        and row.get("locator_kind") == "JSON_POINTER"
        and row.get("locator") == "/projection_contract"
        and row.get("stage_role") == "DYNAMIC_LOWERING"
    ]
    evidence_id = registrations[0].get("evidence_id") if len(registrations) == 1 else None
    applied_paths = [row.get("path") for row in metadata.get("applied_evidence_overlays", [])]
    require(duplicates == 0, "G09", "TRACE_CELL_UNIQUE")
    require(
        target.get("disposition") == "BOUND_DIRECT"
        and target.get("blocked_gap_ids") == []
        and evidence_id in target.get("evidence_refs", []),
        "G09", "TARGET_BOUND_DIRECT",
    )
    require(count == 4220 and digest == NON_TARGET_SHA256, "G09", "OTHER_4220_EXACT")
    require(
        metadata.get("revision") == REVISION
        and metadata.get("local_predecessor_commit") == BASELINE
        and OVERLAY in applied_paths,
        "G09", "GENERATED_METADATA",
    )

    # G10: governance remains static/NOT_RUN and R68 evidence remains immutable.
    expected_governance = {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
    }
    contract_guards = contract.get("guards", {})
    fixture_state = fixture.get("evidence_state", {})
    overlay_guards = overlay.get("guards", {})
    metadata_governance = metadata.get("governance", {})
    require(
        all(contract_guards.get(key) == item for key, item in expected_governance.items())
        and all(fixture_state.get(key) == item for key, item in expected_governance.items())
        and all(overlay_guards.get(key) == item for key, item in expected_governance.items())
        and all(metadata_governance.get(key) == item for key, item in expected_governance.items())
        and contract_guards.get("github_publication") == "SUSPENDED"
        and overlay_guards.get("github_publication") == "SUSPENDED"
        and metadata_governance.get("github_publication") == "SUSPENDED"
        and fixture_state.get("product_execution") == "NOT_RUN"
        and contract.get("counts", {}).get("product_execution_receipt_count") == 0
        and overlay_guards.get("product_execution_receipt_count") == 0,
        "G10", "GOVERNANCE_NOT_RUN",
    )
    protected_ok = not protected_drift and all(
        (root / relative).is_file() and sha256_file(root / relative) == expected
        for relative, expected in PROTECTED_R68.items()
    )
    require(protected_ok, "G10", "R68_PROTECTED_HASHES")
    decision_text = (root / DECISION).read_text(encoding="utf-8") if (root / DECISION).is_file() else ""
    require(
        all(token in decision_text for token in (
            FEATURE, R36_SHA256, R37_SHA256, "all 15 product lanes", "NOT_RUN", str(current_digest),
        )),
        "G10", "DECISION_GOVERNANCE",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    by_gate = {
        gate: [item for item in errors if item.startswith(gate + ":")]
        for gate in GATES
    }
    receipt = {
        "schema": "deeplus.r69-managed-reference-dynamic-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "baseline_commit": BASELINE,
        "feature_id": FEATURE,
        "target_stage": "DYNAMIC_LOWERING",
        "gate_count": len(GATES),
        "passed_gate_count": sum(not rows for rows in by_gate.values()),
        "gates": [
            {"gate": gate, "name": GATES[gate], "pass": not by_gate[gate], "errors": by_gate[gate]}
            for gate in GATES
        ],
        "errors": errors,
        "product_execution": "NOT_RUN",
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
