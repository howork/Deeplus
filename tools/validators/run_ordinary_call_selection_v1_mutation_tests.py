#!/usr/bin/env python3
"""Mutation controls for OrdinaryCallSelectionV1."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_ordinary_call_selection_v1 as focused


Mutation = tuple[str, str, Callable[[dict[str, Any], dict[str, Any]], None]]


def contract_value(path: tuple[str, ...], value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        target: Any = contract
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return mutate


def fixture_value(case_id: str, key: str, value: Any):
    def mutate(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
        row = next(item for item in fixture["cases"] if item["id"] == case_id)
        row[key] = value
    return mutate


def swap_diagnostic_ranks(contract: dict[str, Any], fixture: dict[str, Any]) -> None:
    contract["diagnostic_precedence"][2], contract["diagnostic_precedence"][7] = contract["diagnostic_precedence"][7], contract["diagnostic_precedence"][2]


MUTATIONS: list[Mutation] = [
    ("OCS-MUT-01", "G03", contract_value(("candidate_local_inference", "cross_candidate_constraint_flow"), True)),
    ("OCS-MUT-02", "G03", contract_value(("candidate_local_inference", "expected_result_filters_candidates"), True)),
    ("OCS-MUT-03", "G04", contract_value(("specificity", "channel_generality"), ["FIXED", "NAMED_REST", "REPEATED", "REPEATED_AND_NAMED"])),
    ("OCS-MUT-04", "G04", contract_value(("specificity", "unknown_proof_result"), "PREFER_FIRST")),
    ("OCS-MUT-05", "G06", contract_value(("canonical_output", "selected_count"), 2)),
    ("OCS-MUT-06", "G06", contract_value(("runtime_and_lowering", "operand_runtime_evaluation_before_seal_count"), 1)),
    ("OCS-MUT-07", "G05", swap_diagnostic_ranks),
    ("OCS-MUT-08", "G11", fixture_value("OCS-N-003", "selected_count", 1)),
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
    print(json.dumps({"schema": "deeplus.ordinary-call-selection-v1-mutation-receipt/r1", "result": "PASS" if passed else "FAIL", "declared_mutation_count": 8, "executed_mutation_count": len(results), "rejected_mutation_count": sum(item["rejected"] for item in results), "results": results, "product_execution": "NOT_RUN"}, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
