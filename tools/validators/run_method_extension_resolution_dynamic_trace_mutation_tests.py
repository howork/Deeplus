#!/usr/bin/env python3
"""Run exactly 14 bounded in-memory mutations against the R71 validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_method_extension_resolution_dynamic_trace as focused  # noqa: E402


Mutation = Tuple[str, str, Callable[[Dict[str, Any]], None]]


def contract(values: Dict[str, Any]) -> Dict[str, Any]:
    item = copy.deepcopy(values[focused.CONTRACT])
    values[focused.CONTRACT] = item
    return item


def m01_direct(values: Dict[str, Any]) -> None:
    contract(values)["target_cell"]["disposition"] = "BOUND_DIRECT"


def m02_delegate(values: Dict[str, Any]) -> None:
    contract(values)["target_cell"]["delegate_feature_id"] = None


def m03_extension_set(values: Dict[str, Any]) -> None:
    contract(values)["selected_identity_seal"]["required_identity_domains"].remove(
        "ExtensionSetId"
    )


def m04_extension_member(values: Dict[str, Any]) -> None:
    contract(values)["selected_identity_seal"]["required_identity_domains"].remove(
        "ExtensionMemberId"
    )


def m05_callable(values: Dict[str, Any]) -> None:
    contract(values)["selected_identity_seal"]["required_identity_domains"][2] = (
        "ExtensionMemberId"
    )


def m06_ordinary_row(values: Dict[str, Any]) -> None:
    contract(values)["dynamic_delegate"]["ordinary"]["lowering_row"] = "HM-LR-CALL-001"


def m07_message_row(values: Dict[str, Any]) -> None:
    contract(values)["dynamic_delegate"]["message"]["lowering_row"] = "HM-LR-CALL-005"


def m08_reorder(values: Dict[str, Any]) -> None:
    contract(values)["dynamic_delegate"]["ordinary"]["operation_sequence"] = [
        "INVOKE",
        "CONTEXT_ADAPT",
    ]


def m09_receiver_twice(values: Dict[str, Any]) -> None:
    contract(values)["dynamic_delegate"]["ordinary"]["receiver_evaluation_count"] = 2


def m10_cross_domain_rank(values: Dict[str, Any]) -> None:
    item = contract(values)["static_resolution_owner"]
    item["ordinary_both_domains_nonempty"] = "RANK_TOGETHER"
    item["selected_count_on_collision"] = 1


def m11_order_winner(values: Dict[str, Any]) -> None:
    contract(values)["static_resolution_owner"]["source_import_use_order_winner_count"] = 1


def m12_runtime_search(values: Dict[str, Any]) -> None:
    item = contract(values)
    item["static_resolution_owner"]["runtime_candidate_search_count"] = 1
    item["runtime_backend_residue_fence"]["runtime_selector_string_lookup_count"] = 1


def m13_trait_witness(values: Dict[str, Any]) -> None:
    contract(values)["static_resolution_owner"]["trait_witness_synthesis_count"] = 1


def m14_product_claim(values: Dict[str, Any]) -> None:
    item = contract(values)["authority_fence"]
    item["open_feature_p1"] = 21
    item["product_lanes"]["executed"] = 1
    item["product_lanes"]["state"] = "PASS"


MUTATIONS: List[Mutation] = [
    ("M01", "G06", m01_direct),
    ("M02", "G06", m02_delegate),
    ("M03", "G06", m03_extension_set),
    ("M04", "G06", m04_extension_member),
    ("M05", "G06", m05_callable),
    ("M06", "G06", m06_ordinary_row),
    ("M07", "G06", m07_message_row),
    ("M08", "G06", m08_reorder),
    ("M09", "G06", m09_receiver_twice),
    ("M10", "G06", m10_cross_domain_rank),
    ("M11", "G06", m11_order_winner),
    ("M12", "G06", m12_runtime_search),
    ("M13", "G06", m13_trait_witness),
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
                    "schema": "deeplus.r71-method-extension-resolution-dynamic-trace-mutation-receipt/r1",
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
                "schema": "deeplus.r71-method-extension-resolution-dynamic-trace-mutation-receipt/r1",
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
