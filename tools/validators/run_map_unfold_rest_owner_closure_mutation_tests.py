#!/usr/bin/env python3
"""Mutation controls for the R82 Map unfold/rest owner closure."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_map_unfold_rest_owner_closure as focused


Mutation = tuple[str, str, Callable[[dict[str, Any], dict[str, Any]], None]]


def contract_value(path: tuple[str, ...], value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        target: Any = contract
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def matrix_value(channel: str, key: str, value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        row = next(item for item in contract["owner_matrix"] if item["channel"] == channel)
        row[key] = value
    return mutate


def fixture_value(case_id: str, key: str, value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        row = next(item for item in fixture["cases"] if item["id"] == case_id)
        row[key] = value
    return mutate


MUTATIONS: list[Mutation] = [
    ("R82-M01", "G02", matrix_value("MAP_RUNTIME", "surface", "**Expr")),
    ("R82-M02", "G02", matrix_value("MAP_PATTERN_RESIDUAL", "surface", "..RestBinder")),
    ("R82-M03", "G02", contract_value(("parser_contract", "map_comprehension_head"), "MapEntry")),
    ("R82-M04", "G02", contract_value(("parser_contract", "expected_type_selects_channel"), True)),
    ("R82-M05", "G02", contract_value(("parser_contract", "legacy_alias_count"), 2)),
    ("R82-M06", "G08", fixture_value("R82-MAP-REJ-002", "expected_residue_count", 1)),
    ("R82-M07", "G09", contract_value(("governance", "semantic_p0"), 1)),
    ("R82-M08", "G09", contract_value(("governance", "product_lanes"), "1_OF_15_PASS")),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base_contract = focused.load(root / focused.CONTRACT_REL)
    base_fixture = focused.load(root / focused.FIXTURE_REL)
    normal = focused.validate(root)
    results = []
    for mutation_id, expected_gate, mutate in MUTATIONS:
        contract = copy.deepcopy(base_contract)
        fixture = copy.deepcopy(base_fixture)
        mutate(contract, fixture)
        errors = focused.validate(root, contract_override=contract, fixture_override=fixture)
        expected = any(item.startswith(expected_gate + ":") for item in errors)
        results.append({"mutation_id": mutation_id, "expected_gate": expected_gate, "rejected": bool(errors), "expected_rejection": expected, "first_error": errors[0] if errors else None})
    passed = not normal and all(item["rejected"] and item["expected_rejection"] for item in results)
    print(json.dumps({"schema": "deeplus.r82-map-unfold-rest-owner-closure-mutation-receipt/r1", "result": "PASS" if passed else "FAIL", "declared_mutation_count": 8, "executed_mutation_count": len(results), "rejected_mutation_count": sum(item["rejected"] for item in results), "results": results, "product_execution": "NOT_RUN"}, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
