#!/usr/bin/env python3
"""Run exactly 14 bounded in-memory mutations against the R72 validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_member_extension_collision_dynamic_trace as focused  # noqa: E402


Mutation = Tuple[str, str, Callable[[Dict[str, Any]], None]]


def change(values: Dict[str, Any], path: str) -> Any:
    value = copy.deepcopy(values[path])
    values[path] = value
    return value


def m01_disposition(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["target_cell"]["disposition"] = "BOUND_DIRECT"


def m02_reason(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["target_cell"]["not_applicable"][
        "reason_code"
    ] = "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR"


def m03_authority(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["target_cell"]["not_applicable"][
        "authority_boundary"
    ] = "TYPE_CHECKER_AUTHORITY"


def m04_selected(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["static_collision_owner"][
        "selected_count_on_collision"
    ] = 1


def m05_rank_first(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["static_collision_owner"][
        "within_domain_ranking_before_collision"
    ] = True


def m06_primary(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["diagnostic_fence"]["sole_active_primary"] = (
        "AMBIGUOUS_EXTENSION_CANDIDATE"
    )


def m07_retired_emits(values: Dict[str, Any]) -> None:
    item = change(values, focused.CONTRACT)["diagnostic_fence"]
    item["secondary_diagnostics"] = ["STABLE_MEMBER_EXTENSION_COLLISION"]


def m08_recovery_hir(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["pre_hir_rejection_boundary"][
        "recovery_hir_count"
    ] = 1


def m09_mir_residue(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["runtime_backend_residue_fence"][
        "mir_operation_count"
    ] = 1


def m10_runtime_fallback(values: Dict[str, Any]) -> None:
    item = change(values, focused.CONTRACT)
    item["pre_hir_rejection_boundary"]["runtime_fallback_count"] = 1
    item["runtime_backend_residue_fence"]["runtime_provider_lookup_count"] = 1


def m11_link_winner(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["runtime_backend_residue_fence"][
        "address_or_link_order_winner_count"
    ] = 1


def m12_r71_owner(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["r71_preservation"][
        "method_extension_resolution_dynamic_disposition"
    ] = "BOUND_DIRECT"


def m13_non_target(values: Dict[str, Any]) -> None:
    rows = change(values, focused.ROWS)
    row = next(
        row for row in rows if row.get("feature_id") == "method_extension_resolution_policy"
    )
    cell = next(
        stage for stage in row.get("stages", []) if stage.get("stage") == "DYNAMIC_LOWERING"
    )
    cell["disposition"] = "BOUND_DIRECT"
    cell["evidence_refs"] = []
    cell["delegate_feature_id"] = None


def m14_product_claim(values: Dict[str, Any]) -> None:
    item = change(values, focused.CONTRACT)["machine_acceptance"]
    item["product_lanes"] = "1_OF_15_PASS"
    item["product_execution_receipt_count"] = 1


MUTATIONS: List[Mutation] = [
    ("M01", "G06", m01_disposition),
    ("M02", "G06", m02_reason),
    ("M03", "G06", m03_authority),
    ("M04", "G06", m04_selected),
    ("M05", "G06", m05_rank_first),
    ("M06", "G06", m06_primary),
    ("M07", "G06", m07_retired_emits),
    ("M08", "G06", m08_recovery_hir),
    ("M09", "G06", m09_mir_residue),
    ("M10", "G06", m10_runtime_fallback),
    ("M11", "G06", m11_link_winner),
    ("M12", "G06", m12_r71_owner),
    ("M13", "G06", m13_non_target),
    ("M14", "G06", m14_product_claim),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base = focused.load_inputs(root)
    before = focused.predecessor_rows(root)
    declared = [
        row.get("mutation_id")
        for row in base[focused.FIXTURE].get("mutation_oracles", [])
    ]
    expected = [row[0] for row in MUTATIONS]
    normal_errors = focused.validate(
        root, overrides=base, predecessor_rows_override=before
    )
    if normal_errors:
        print(
            json.dumps(
                {
                    "schema": "deeplus.r72-member-extension-collision-dynamic-trace-mutation-receipt/r1",
                    "result": "BLOCKED_BASELINE",
                    "declared_mutation_count": 14,
                    "executed_mutation_count": 0,
                    "declared_id_parity": declared == expected,
                    "normal_errors": normal_errors,
                    "product_execution": "NOT_RUN",
                },
                separators=(",", ":"),
            )
        )
        return 1

    results = []
    for mutation_id, expected_gate, mutate in MUTATIONS:
        values = copy.deepcopy(base)
        mutate(values)
        errors = focused.validate(
            root, overrides=values, predecessor_rows_override=before
        )
        expected_rejection = any(
            item.startswith(expected_gate + ":") for item in errors
        )
        results.append(
            {
                "mutation_id": mutation_id,
                "expected_gate": expected_gate,
                "rejected": bool(errors),
                "expected_rejection": expected_rejection,
                "first_error": errors[0] if errors else None,
            }
        )

    passed = (
        declared == expected
        and len(results) == 14
        and all(row["rejected"] and row["expected_rejection"] for row in results)
    )
    print(
        json.dumps(
            {
                "schema": "deeplus.r72-member-extension-collision-dynamic-trace-mutation-receipt/r1",
                "result": "PASS" if passed else "FAIL",
                "declared_mutation_count": 14,
                "executed_mutation_count": len(results),
                "rejected_mutation_count": sum(row["rejected"] for row in results),
                "expected_gate_rejection_count": sum(
                    row["expected_rejection"] for row in results
                ),
                "declared_id_parity": declared == expected,
                "results": results,
                "product_execution": "NOT_RUN",
            },
            separators=(",", ":"),
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
