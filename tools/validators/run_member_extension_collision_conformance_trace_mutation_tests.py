#!/usr/bin/env python3
"""Run exactly 14 bounded in-memory mutations against the R73 validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_member_extension_collision_conformance_trace as focused  # noqa: E402


Mutation = Tuple[str, str, Callable[[Dict[str, Any]], None]]
MUTATION_PLAN_SOURCE = "R73_VALIDATION_HARNESS"


def change(values: Dict[str, Any], path: str) -> Any:
    value = copy.deepcopy(values[path])
    values[path] = value
    return value


def overlay_binding(values: Dict[str, Any], outcome: str) -> Dict[str, Any]:
    overlay = change(values, focused.OVERLAY)
    return next(row for row in overlay["bindings"] if row.get("outcome") == outcome)


def overlay_entry(values: Dict[str, Any], outcome: str) -> Dict[str, Any]:
    overlay = change(values, focused.OVERLAY)
    return next(
        row
        for row in overlay["evidence_entries"]
        if row.get("stage_role") == "CONFORMANCE_TESTS:" + outcome
    )


def m01_boundary_disposition(values: Dict[str, Any]) -> None:
    overlay_binding(values, "BOUNDARY")["disposition"] = "BOUND_DELEGATED"


def m02_reject_disposition(values: Dict[str, Any]) -> None:
    overlay_binding(values, "REJECT")["disposition"] = "NOT_APPLICABLE"


def m03_boundary_pointer(values: Dict[str, Any]) -> None:
    overlay_entry(values, "BOUNDARY")["locator"] = "/acceptance_bindings/POSITIVE"


def m04_reject_pointer(values: Dict[str, Any]) -> None:
    overlay_entry(values, "REJECT")["locator"] = "/acceptance_bindings/BOUNDARY"


def m05_acceptance_binding(values: Dict[str, Any]) -> None:
    change(values, focused.R72_CONTRACT)["acceptance_bindings"]["BOUNDARY"].pop()


def m06_qualified_bypass(values: Dict[str, Any]) -> None:
    contract = change(values, focused.R72_CONTRACT)
    contract["noncollision_boundary"]["qualified_extension_selector"] = (
        "BYPASS_ALL_EXTENSION_CHECKS"
    )
    contract["noncollision_boundary"][
        "qualified_selector_within_domain_winner_owned_by_this_contract"
    ] = True


def m07_order_winner(values: Dict[str, Any]) -> None:
    change(values, focused.R72_CONTRACT)["static_collision_owner"][
        "source_import_use_or_activation_order_winner_count"
    ] = 1


def m08_diagnostic(values: Dict[str, Any]) -> None:
    fence = change(values, focused.R72_CONTRACT)["diagnostic_fence"]
    fence["sole_active_primary"] = "AMBIGUOUS_EXTENSION_CANDIDATE"
    fence["secondary_diagnostics"] = ["STABLE_MEMBER_EXTENSION_COLLISION"]


def m09_selected(values: Dict[str, Any]) -> None:
    contract = change(values, focused.R72_CONTRACT)
    contract["static_collision_owner"]["selected_count_on_collision"] = 1
    contract["pre_hir_rejection_boundary"]["selected_extension_count"] = 1


def m10_ranking(values: Dict[str, Any]) -> None:
    change(values, focused.R72_CONTRACT)["static_collision_owner"][
        "within_domain_ranking_before_collision"
    ] = True


def m11_hir_residue(values: Dict[str, Any]) -> None:
    pre_hir = change(values, focused.R72_CONTRACT)["pre_hir_rejection_boundary"]
    pre_hir["hir_call_plan_count"] = 1
    pre_hir["recovery_hir_count"] = 1


def m12_runtime_residue(values: Dict[str, Any]) -> None:
    residue = change(values, focused.R72_CONTRACT)["runtime_backend_residue_fence"]
    residue["mir_operation_count"] = 1
    residue["xvm_instruction_count"] = 1
    residue["runtime_helper_call_count"] = 1
    residue["cranelift_instruction_count"] = 1


def m13_fixture_drift(values: Dict[str, Any]) -> None:
    fixture = change(values, focused.R72_FIXTURE)
    row = next(
        row
        for row in fixture["acceptance_oracles"]
        if row.get("case_id") == "R72-MECD-ACC-006"
    )
    row["class"] = "BOUNDARY"
    row["expected"] = "ADMIT"


def m14_product_claim(values: Dict[str, Any]) -> None:
    overlay = change(values, focused.OVERLAY)
    overlay["acceptance_cases"][0]["execution_state"] = "PASS"
    overlay["guards"]["product_lanes"] = "1_OF_15_PASS"
    overlay["guards"]["product_execution_receipt_count"] = 1


MUTATION_PLAN: List[Mutation] = [
    ("M01", "G01", m01_boundary_disposition),
    ("M02", "G01", m02_reject_disposition),
    ("M03", "G01", m03_boundary_pointer),
    ("M04", "G01", m04_reject_pointer),
    ("M05", "G04", m05_acceptance_binding),
    ("M06", "G05", m06_qualified_bypass),
    ("M07", "G05", m07_order_winner),
    ("M08", "G05", m08_diagnostic),
    ("M09", "G05", m09_selected),
    ("M10", "G05", m10_ranking),
    ("M11", "G05", m11_hir_residue),
    ("M12", "G05", m12_runtime_residue),
    ("M13", "G04", m13_fixture_drift),
    ("M14", "G06", m14_product_claim),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base = focused.load_inputs(root)
    before = focused.predecessor_rows(root)
    planned_ids = [row[0] for row in MUTATION_PLAN]
    exact_ids = [f"M{index:02d}" for index in range(1, 15)]
    normal_errors = focused.validate(
        root, overrides=base, predecessor_rows_override=before
    )
    if normal_errors:
        print(
            json.dumps(
                {
                    "schema": "deeplus.r73-member-extension-collision-conformance-trace-mutation-receipt/r1",
                    "result": "BLOCKED_BASELINE",
                    "plan_source": MUTATION_PLAN_SOURCE,
                    "declared_mutation_count": 14,
                    "executed_mutation_count": 0,
                    "plan_id_sequence_exact": planned_ids == exact_ids,
                    "normal_errors": normal_errors,
                    "product_execution": "NOT_RUN",
                },
                separators=(",", ":"),
            )
        )
        return 1

    results = []
    for mutation_id, expected_gate, mutate in MUTATION_PLAN:
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
        planned_ids == exact_ids
        and len(results) == 14
        and all(row["rejected"] and row["expected_rejection"] for row in results)
    )
    print(
        json.dumps(
            {
                "schema": "deeplus.r73-member-extension-collision-conformance-trace-mutation-receipt/r1",
                "result": "PASS" if passed else "FAIL",
                "plan_source": MUTATION_PLAN_SOURCE,
                "declared_mutation_count": 14,
                "executed_mutation_count": len(results),
                "rejected_mutation_count": sum(row["rejected"] for row in results),
                "expected_gate_rejection_count": sum(
                    row["expected_rejection"] for row in results
                ),
                "plan_id_sequence_exact": planned_ids == exact_ids,
                "results": results,
                "product_execution": "NOT_RUN",
            },
            separators=(",", ":"),
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
