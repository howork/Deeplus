#!/usr/bin/env python3
"""Mutation controls for the R80 interpolation format contract."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_string_interpolation_format_spec_core as focused


Mutation = tuple[
    str,
    str,
    Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], None],
]


def contract_value(path: tuple[str, ...], value: Any):
    def mutate(
        contract: dict[str, Any], fixture: dict[str, Any], decisions: dict[str, Any]
    ) -> None:
        target: Any = contract
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def fixture_value(case_id: str, key: str, value: Any):
    def mutate(
        contract: dict[str, Any], fixture: dict[str, Any], decisions: dict[str, Any]
    ) -> None:
        row = next(item for item in fixture["cases"] if item["id"] == case_id)
        row[key] = value
    return mutate


def stale_decision_projection(
    contract: dict[str, Any], fixture: dict[str, Any], decisions: dict[str, Any]
) -> None:
    row = next(
        item
        for item in decisions["laws"]
        if item["id"] == "DSGN-CURRENT-VALUE-OPERATOR-INDEX-COHERENCE"
    )
    row["law"] = row["law"].replace(
        "Its colon format-spec uses the closed Stable `Align? Width` plan: width is a Unicode-scalar minimum from 1 through 1,000,000, U+0020 padding is applied after one direct String or preselected synchronous Display render, center remainder goes right, and truncation never occurs; this design closure claims no product execution.",
        "colon format-spec semantics remain DEFERRED_PRODUCT_HANDOFF.",
    )


MUTATIONS: list[Mutation] = [
    ("R80-M01", "G02", contract_value(("surface_contract", "width_decimal_max"), 999999)),
    ("R80-M02", "G02", contract_value(("surface_contract", "default_alignment"), "RIGHT")),
    ("R80-M03", "G05", contract_value(("dynamic_semantics", "fill_scalar"), "U+0030")),
    ("R80-M04", "G05", contract_value(("dynamic_semantics", "truncation"), "RIGHT_TRUNCATE")),
    ("R80-M05", "G05", contract_value(("dynamic_semantics", "string_hole_display_invocation_count"), 1)),
    ("R80-M06", "G10", contract_value(("governance", "product_lanes"), "1_OF_15_PASS")),
    ("R80-M07", "G04", fixture_value("R80-FMT-REJ-002", "reason", "WIDTH_OUT_OF_RANGE")),
    ("R80-M08", "G04", fixture_value("R80-FMT-POS-003", "format_text", "~12")),
    ("R80-M09", "G09", stale_decision_projection),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base_contract = focused.load(root / focused.CONTRACT_REL)
    base_fixture = focused.load(root / focused.FIXTURE_REL)
    base_decisions = focused.load(root / focused.CURRENT_DECISIONS_REL)
    normal = focused.validate(root)
    results = []
    for mutation_id, expected_gate, mutate in MUTATIONS:
        contract = copy.deepcopy(base_contract)
        fixture = copy.deepcopy(base_fixture)
        decisions = copy.deepcopy(base_decisions)
        mutate(contract, fixture, decisions)
        errors = focused.validate(
            root,
            contract_override=contract,
            fixture_override=fixture,
            decisions_override=decisions,
        )
        expected = any(item.startswith(expected_gate + ":") for item in errors)
        results.append({"mutation_id": mutation_id, "expected_gate": expected_gate, "rejected": bool(errors), "expected_rejection": expected, "first_error": errors[0] if errors else None})
    passed = not normal and all(item["rejected"] and item["expected_rejection"] for item in results)
    print(json.dumps({"schema": "deeplus.r80-string-interpolation-format-mutation-receipt/r1", "result": "PASS" if passed else "FAIL", "declared_mutation_count": 9, "executed_mutation_count": len(results), "rejected_mutation_count": sum(item["rejected"] for item in results), "results": results, "product_execution": "NOT_RUN"}, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
