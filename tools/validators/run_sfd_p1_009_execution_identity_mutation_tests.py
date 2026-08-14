#!/usr/bin/env python3
"""Mutation controls for the R79 SFD execution-identity route."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

import validate_sfd_p1_009_execution_identity as focused


Mutation = tuple[str, str, Callable[[dict[str, Any], str, str, str], tuple[dict[str, Any], str, str, str]]]


def mutate_contract(path: tuple[str, ...], value: Any):
    def mutation(contract: dict[str, Any], source: str, cli: str, testkit: str):
        target: Any = contract
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return contract, source, cli, testkit
    return mutation


def mutate_text(which: str, old: str, new: str):
    def mutation(contract: dict[str, Any], source: str, cli: str, testkit: str):
        values = {"source": source, "cli": cli, "testkit": testkit}
        values[which] = values[which].replace(old, new, 1)
        return contract, values["source"], values["cli"], values["testkit"]
    return mutation


MUTATIONS: list[Mutation] = [
    ("R79-M01", "G02", mutate_contract(("identity_domains", "historical_provenance", "commit"), "0" * 40)),
    ("R79-M02", "G02", mutate_contract(("identity_domains", "execution_target", "binding"), "HARDCODED_SELF_SHA")),
    ("R79-M03", "G04", mutate_contract(("execution_gate", "tracked_tree_clean"), False)),
    ("R79-M04", "G04", mutate_contract(("receipt_binding", "baseline_commit"), "HISTORICAL_PROVENANCE_COMMIT")),
    ("R79-M05", "G05", mutate_contract(("closure_fence", "status"), "CLOSED")),
    ("R79-M06", "G05", mutate_contract(("governance", "product_lanes"), "1_OF_15_PASS")),
    ("R79-M07", "G03", mutate_text("source", "HISTORICAL_PROVENANCE_BASELINE", "REQUIRED_BASELINE")),
    ("R79-M08", "G03", mutate_text("cli", '"diff-index", "--quiet"', '"status", "--short"')),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base_contract = focused.load(root / focused.CONTRACT_REL)
    base_source = (root / focused.SOURCE_REL).read_text(encoding="utf-8")
    base_cli = (root / focused.CLI_REL).read_text(encoding="utf-8")
    base_testkit = (root / focused.TESTKIT_REL).read_text(encoding="utf-8")
    normal = focused.validate(root)
    results = []
    for mutation_id, expected_gate, mutate in MUTATIONS:
        contract = copy.deepcopy(base_contract)
        contract, source, cli, testkit = mutate(contract, base_source, base_cli, base_testkit)
        errors = focused.validate(
            root,
            contract_override=contract,
            source_override=source,
            cli_override=cli,
            testkit_override=testkit,
        )
        expected = any(error.startswith(expected_gate + ":") for error in errors)
        results.append({"mutation_id": mutation_id, "expected_gate": expected_gate, "rejected": bool(errors), "expected_rejection": expected, "first_error": errors[0] if errors else None})
    passed = not normal and all(row["rejected"] and row["expected_rejection"] for row in results)
    print(json.dumps({"schema": "deeplus.r79-sfd-p1-009-execution-identity-mutation-receipt/r1", "result": "PASS" if passed else "FAIL", "declared_mutation_count": 8, "executed_mutation_count": len(results), "rejected_mutation_count": sum(row["rejected"] for row in results), "results": results, "product_execution": "NOT_RUN"}, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
