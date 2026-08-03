#!/usr/bin/env python3
"""Run exactly 14 bounded in-memory mutations against the R70 validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_static_runtime_member_boundary_trace as focused  # noqa: E402


Mutation = Tuple[str, str, Callable[[Dict[str, Any]], None]]


def change(values: Dict[str, Any], path: str) -> Any:
    value = copy.deepcopy(values[path])
    values[path] = value
    return value


def m01_colon_colon_member(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["boundary_definition"][
        "static_qualification_surface"
    ] = "."


def m02_dot_static(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["boundary_definition"][
        "runtime_member_surface"
    ] = "::"


def m03_module_expression_ref(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["resolver_hir_fence"][
        "module_expression_hir_projection"
    ] = "ResolvedRef::Module(ModuleId)"


def m04_companion_value(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["boundary_definition"][
        "companion_or_metatype_value_created"
    ] = True


def m05_runtime_relookup(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["resolver_hir_fence"][
        "runtime_relookup_count"
    ] = 1


def m06_wrong_static_identity(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["resolver_hir_fence"][
        "static_terminal_expression_hir_projection"
    ] = "ResolvedRef::Module(ModuleId)"


def m07_runtime_field_lookup(values: Dict[str, Any]) -> None:
    contract = change(values, focused.CONTRACT)
    contract["resolver_hir_fence"]["ordinary_dot_field_hir_projection"] = (
        "RuntimeMemberLookup(name)"
    )
    contract["runtime_backend_residue_fence"]["runtime_member_name_lookup_count"] = 1


def m08_receiver_twice(values: Dict[str, Any]) -> None:
    contract = change(values, focused.CONTRACT)
    case = next(
        row
        for row in contract["acceptance_cases"]
        if row.get("case_id") == "R70-SRMB-ACC-005"
    )
    case["assertion_ids"].remove("RECEIVER_EVALUATED_ONCE")


def m09_wrong_direct_row(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["terminal_selection_handoff"][
        "ordinary_direct_call"
    ]["lowering_rows"] = ["HM-LR-CALL-002"]


def m10_virtual_as_direct(values: Dict[str, Any]) -> None:
    contract = change(values, focused.CONTRACT)
    virtual = contract["terminal_selection_handoff"]["ordinary_virtual_call"]
    virtual["hir_mode_target_pair"] = "ORDINARY::DIRECT_IMPLEMENTATION"
    virtual["lowering_rows"] = ["HM-LR-CALL-001"]


def m11_extension_runtime_search(values: Dict[str, Any]) -> None:
    contract = change(values, focused.CONTRACT)
    extension = contract["terminal_selection_handoff"][
        "ordinary_extension_static_call"
    ]
    extension["lowering_rows"] = ["HM-LR-CALL-003"]
    contract["runtime_backend_residue_fence"]["runtime_selector_lookup_count"] = 1


def m12_runtime_selector_payload(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["runtime_backend_residue_fence"][
        "internal_runtime_selector_payload_count"
    ] = 1


def m13_xvm_selector_search(values: Dict[str, Any]) -> None:
    contract = change(values, focused.CONTRACT)
    fence = contract["runtime_backend_residue_fence"]
    fence["xvm_new_opcode_count"] = 1
    fence["xvm_new_capability_count"] = 1


def m14_cranelift_reselection(values: Dict[str, Any]) -> None:
    change(values, focused.CONTRACT)["runtime_backend_residue_fence"][
        "cranelift_selector_reselection_count"
    ] = 1


MUTATIONS: List[Mutation] = [
    ("M01", "G06", m01_colon_colon_member),
    ("M02", "G06", m02_dot_static),
    ("M03", "G06", m03_module_expression_ref),
    ("M04", "G06", m04_companion_value),
    ("M05", "G06", m05_runtime_relookup),
    ("M06", "G06", m06_wrong_static_identity),
    ("M07", "G06", m07_runtime_field_lookup),
    ("M08", "G06", m08_receiver_twice),
    ("M09", "G06", m09_wrong_direct_row),
    ("M10", "G06", m10_virtual_as_direct),
    ("M11", "G06", m11_extension_runtime_search),
    ("M12", "G06", m12_runtime_selector_payload),
    ("M13", "G06", m13_xvm_selector_search),
    ("M14", "G06", m14_cranelift_reselection),
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
        print(json.dumps({
            "schema": "deeplus.r70-static-runtime-member-boundary-trace-mutation-receipt/r1",
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
        values = copy.deepcopy(base)
        mutate(values)
        errors = focused.validate(
            root, overrides=values, predecessor_rows_override=before
        )
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
        "schema": "deeplus.r70-static-runtime-member-boundary-trace-mutation-receipt/r1",
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
