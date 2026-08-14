#!/usr/bin/env python3
"""Mutation controls for the R81 @scope shielded contract."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_scope_shielded_cancellation_semantics as focused


Mutation = tuple[str, str, Callable[[dict[str, Any], dict[str, Any]], None]]


def contract_value(path: tuple[str, ...], value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        target: Any = contract
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def fixture_value(case_id: str, path: tuple[str, ...], value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        target: Any = next(item for item in fixture["cases"] if item["id"] == case_id)
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


MUTATIONS: list[Mutation] = [
    ("R81-M01", "G02", contract_value(("surface_contract", "cancellable_with_shielded_allowed"), True)),
    ("R81-M02", "G03", contract_value(("static_admission", "reason_precedence"), ["CANCELLATION_CONTEXT_REQUIRED", "DUPLICATE_MODIFIER", "CONFLICTING_CANCELLATION_MODE", "CANCELLABLE_INSIDE_SHIELD"])),
    ("R81-M03", "G05", contract_value(("dynamic_semantics", "inside_observed_count"), 1)),
    ("R81-M04", "G05", contract_value(("dynamic_semantics", "cleanup_bypass_count"), 1)),
    ("R81-M05", "G05", contract_value(("dynamic_semantics", "cancellation_to_error_conversion_count"), 1)),
    ("R81-M06", "G04", fixture_value("R81-SHIELD-BOUND-002", ("expected", "observe_count"), 2)),
    ("R81-M07", "G04", fixture_value("R81-SHIELD-BOUND-003", ("expected", "terminal_outcome"), "CANCELLATION")),
    ("R81-M08", "G04", fixture_value("R81-SHIELD-REJ-002", ("expected_reason",), "DUPLICATE_MODIFIER")),
    ("R81-M09", "G10", contract_value(("governance", "product_lanes"), "1_OF_15_PASS")),
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
    print(json.dumps({"schema": "deeplus.r81-scope-shielded-cancellation-mutation-receipt/r1", "result": "PASS" if passed else "FAIL", "declared_mutation_count": 9, "executed_mutation_count": len(results), "rejected_mutation_count": sum(item["rejected"] for item in results), "results": results, "product_execution": "NOT_RUN"}, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
