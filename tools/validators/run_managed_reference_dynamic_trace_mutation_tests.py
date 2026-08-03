#!/usr/bin/env python3
"""Run exactly 14 in-memory mutations against the focused R69 validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Tuple


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_managed_reference_dynamic_trace as focused  # noqa: E402


Mutation = Tuple[str, str, Callable[[Dict[str, Any]], None]]


def mutate_managed_dependency(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.MANAGED])
    row["dependency_guard"]["continuation_root_interface_digest"] = "0" * 64
    values[focused.MANAGED] = row


def mutate_managed_suspension(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.MANAGED])
    row["suspension_root_transfer"]["continuation_root_interface_digest"] = "0" * 64
    values[focused.MANAGED] = row


def mutate_runtime_dispatch(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.INTERNAL])
    row["dispatcher_contract"]["bounded_continuation_dispatch"]["continuation_interface_digest"] = "0" * 64
    values[focused.INTERNAL] = row


def mutate_root_domain(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    row["runtime_root_receipt"]["root_entries"][0]["root_id"] = "RegionId:r69-not-a-root"
    values[focused.FIXTURE] = row


def mutate_drop_live_root(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    row["runtime_root_receipt"]["root_entries"] = []
    values[focused.FIXTURE] = row


def mutate_stale_generation(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    row["runtime_root_receipt"]["suspension_rebind_receipts"][0]["destination_handle_generation"] += 1
    row["static_plan"]["bodies"][0]["root_map_table"][0]["entries"][0]["handle_generation"] = 7
    values[focused.FIXTURE] = row


def mutate_root_map_binding(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    row["runtime_root_receipt"]["root_map_id"] = "RootMapId:r69-missing"
    row["runtime_root_receipt"]["root_entry_order"] = "UNSORTED"
    values[focused.FIXTURE] = row


def mutate_late_publish(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    row["runtime_root_receipt"]["lifecycle"]["published_before_operation_entry"] = False
    values[focused.FIXTURE] = row


def mutate_reused_root(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    receipt = row["runtime_root_receipt"]["suspension_rebind_receipts"][0]
    receipt["destination_root_id"] = receipt["source_root_id"]
    values[focused.FIXTURE] = row


def mutate_forbidden_loan_root(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.CONTRACT])
    fence = row["projection_contract"]["region_loan_fence"]
    fence["borrowed_or_inout_view_creates_independent_root"] = True
    values[focused.CONTRACT] = row


def mutate_post_transfer_source_map(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.FIXTURE])
    body = row["static_plan"]["bodies"][0]
    body["safepoint_table"][0]["root_map_id"] = "RootMapId:r69-source"
    values[focused.FIXTURE] = row


def mutate_helper_phase(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.HELPERS])
    helper = next(
        item for item in row["conditional_extension_rows"]
        if item.get("operation") == "MANAGED_SAFEPOINT_ENTER"
    )
    helper["terminator_kind"] = "SYNC_OP"
    helper["projection_phase_or_null"] = None
    values[focused.HELPERS] = row


def mutate_backend_implicit(values: Dict[str, Any]) -> None:
    row = copy.deepcopy(values[focused.CRANELIFT])
    guard = row["managed_reference_guard"]
    guard["implicit_backend_safepoint_count"] = 1
    guard["raw_pointer_fallback"] = True
    values[focused.CRANELIFT] = row


def mutate_parity_product_and_trace(values: Dict[str, Any]) -> None:
    fixture = copy.deepcopy(values[focused.FIXTURE])
    fixture["native_projection_receipts"][1]["semantic_parity_trace_digest"] = "0" * 64
    fixture["evidence_state"]["product_execution"] = "PASS"
    values[focused.FIXTURE] = fixture

    rows = copy.deepcopy(values[focused.ROWS])
    target_changed = False
    for row in rows:
        if row.get("feature_id") == focused.FEATURE:
            for stage in row.get("stages", []):
                if stage.get("stage") == "DYNAMIC_LOWERING":
                    stage["disposition"] = "APPLICABLE_BLOCKED_BY_GAP"
                    stage["blocked_gap_ids"] = ["IR-XCUT-P1-054"]
                    target_changed = True
                    break
        if target_changed:
            break
    rows[0]["stages"][0]["disposition"] = "CONFLICT"
    values[focused.ROWS] = rows


MUTATIONS: List[Mutation] = [
    ("R69-MRM-MUT-001_STALE_MANAGED_DEPENDENCY_CONTINUATION_DIGEST", "G02", mutate_managed_dependency),
    ("R69-MRM-MUT-002_STALE_SUSPENSION_CONTINUATION_DIGEST", "G02", mutate_managed_suspension),
    ("R69-MRM-MUT-003_RUNTIME_DISPATCH_CONTINUATION_DIGEST_DRIFT", "G02", mutate_runtime_dispatch),
    ("R69-MRM-MUT-004_ROOT_ID_DOMAIN_ALIAS", "G04", mutate_root_domain),
    ("R69-MRM-MUT-005_DROP_LIVE_ROOT", "G04", mutate_drop_live_root),
    ("R69-MRM-MUT-006_STALE_HANDLE_GENERATION", "G03", mutate_stale_generation),
    ("R69-MRM-MUT-007_SAFEPOINT_ROOT_MAP_BINDING_DRIFT", "G04", mutate_root_map_binding),
    ("R69-MRM-MUT-008_RECEIPT_PUBLISHED_AFTER_ENTRY", "G04", mutate_late_publish),
    ("R69-MRM-MUT-009_REUSE_SOURCE_ROOT_ID_AT_DESTINATION", "G04", mutate_reused_root),
    ("R69-MRM-MUT-010_FORBIDDEN_LOAN_CROSSES_SUSPENSION", "G05", mutate_forbidden_loan_root),
    ("R69-MRM-MUT-011_POST_TRANSFER_SAFEPOINT_USES_SOURCE_MAP", "G04", mutate_post_transfer_source_map),
    ("R69-MRM-MUT-012_MANAGED_HELPER_COLLECTION_BINDING_DRIFT", "G06", mutate_helper_phase),
    ("R69-MRM-MUT-013_NATIVE_RAW_POINTER_OR_RECEIPT_DRIFT", "G06", mutate_backend_implicit),
    ("R69-MRM-MUT-014_TARGET_PARITY_OR_PRODUCT_OVERCLAIM", "G09", mutate_parity_product_and_trace),
]


def predecessor_hashes(root: Path) -> Mapping[str, str]:
    return {
        focused.MANAGED: focused.git_blob_sha256(root, focused.BASELINE, focused.MANAGED),
        focused.INTERNAL: focused.git_blob_sha256(root, focused.BASELINE, focused.INTERNAL),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base = focused.load_inputs(root)
    declared = [row.get("mutation_id") for row in base[focused.FIXTURE].get("declared_mutations", [])]
    expected = [row[0] for row in MUTATIONS]
    blobs = predecessor_hashes(root)
    normal_errors = focused.validate(root, overrides=base, predecessor_hashes_override=blobs)
    if normal_errors:
        print(json.dumps({
            "schema": "deeplus.r69-managed-reference-dynamic-trace-mutation-receipt/r1",
            "result": "BLOCKED_BASELINE",
            "declared_mutation_count": len(MUTATIONS),
            "executed_mutation_count": 0,
            "declared_id_parity": declared == expected,
            "normal_errors": normal_errors,
            "product_execution": "NOT_RUN",
        }, separators=(",", ":")))
        return 1

    results = []
    for mutation_id, expected_gate, mutate in MUTATIONS:
        values = dict(base)
        mutate(values)
        errors = focused.validate(root, overrides=values, predecessor_hashes_override=blobs)
        expected_rejection = any(item.startswith(expected_gate + ":") for item in errors)
        results.append({
            "mutation_id": mutation_id,
            "expected_gate": expected_gate,
            "rejected": bool(errors),
            "expected_rejection": expected_rejection,
            "first_error": errors[0] if errors else None,
        })
    passed = (
        declared == expected
        and len(results) == 14
        and all(row["rejected"] and row["expected_rejection"] for row in results)
    )
    print(json.dumps({
        "schema": "deeplus.r69-managed-reference-dynamic-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "declared_mutation_count": 14,
        "executed_mutation_count": len(results),
        "rejected_mutation_count": sum(row["rejected"] for row in results),
        "expected_gate_rejection_count": sum(row["expected_rejection"] for row in results),
        "declared_id_parity": declared == expected,
        "results": results,
        "product_execution": "NOT_RUN",
    }, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
