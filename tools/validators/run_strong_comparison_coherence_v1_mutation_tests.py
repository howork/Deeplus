#!/usr/bin/env python3
"""Reject bounded semantic drift in StrongComparisonCoherenceV1."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from validate_strong_comparison_coherence_v1 import CONTRACT_REL, FIXTURE_REL, load, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)
    mutations: list[tuple[str, dict, dict]] = []

    changed = copy.deepcopy(contract)
    changed["admission"]["user_defined"] = "ANY_RHS"
    mutations.append(("USER_HETEROGENEOUS_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["sealed_bilateral_family_contract"]["oriented_witness_count"] = 1
    mutations.append(("REVERSE_WITNESS_REQUIREMENT_REMOVED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["sealed_bilateral_family_contract"]["normalization_domain_required"] = False
    mutations.append(("NORMALIZATION_DOMAIN_OPTIONAL", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["sealed_bilateral_family_contract"]["eq_symmetry_required"] = False
    mutations.append(("EQ_SYMMETRY_DISABLED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["sealed_bilateral_family_contract"]["ord_sign_reversal_required"] = False
    mutations.append(("ORD_SIGN_REVERSAL_DISABLED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["sealed_bilateral_family_contract"]["ord_zero_agreement_required"] = False
    mutations.append(("ORD_ZERO_AGREEMENT_DISABLED", changed, fixture))

    changed_fixture = copy.deepcopy(fixture)
    target = next(case for case in changed_fixture["cases"] if case["case_id"] == "SCC-R-001")
    target["expected"] = {"outcome": "ADMIT_SELF_DOMAIN", "diagnostic_or_null": None}
    mutations.append(("USER_HETERO_FIXTURE_FALSE_PASS", contract, changed_fixture))

    changed = copy.deepcopy(contract)
    changed["governance"]["product_lanes"] = "15_OF_15_PASS"
    mutations.append(("PRODUCT_PASS_OVERCLAIM", changed, fixture))

    results = []
    for name, candidate_contract, candidate_fixture in mutations:
        errors = validate(
            root,
            contract_override=candidate_contract,
            fixture_override=candidate_fixture,
            validate_schema=False,
        )
        results.append({"mutation": name, "result": "REJECTED" if errors else "MISSED", "error_count": len(errors)})
    missed = [row["mutation"] for row in results if row["result"] == "MISSED"]
    print(json.dumps({
        "schema": "deeplus.strong-comparison-coherence-mutation-receipt/r1",
        "result": "PASS" if not missed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": len(results) - len(missed),
        "results": results,
        "missed": missed,
    }, indent=2))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
