#!/usr/bin/env python3
"""Reject bounded mutations of the RefinementR0V1 closure contract."""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_refinement_r0_v1 as focused  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[2], type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    contract = focused.load(root / focused.CONTRACT_REL)
    fixture = focused.load(root / focused.FIXTURE_REL)
    mutations = []

    mutant = copy.deepcopy(contract)
    mutant["formula_normal_form"]["float_comparison_complement_rewrite_count"] = 1
    mutations.append(("FLOAT_COMPLEMENT_REWRITE", mutant, fixture))

    mutant = copy.deepcopy(contract)
    mutant["closed_term_vocabulary"]["user_operator_or_method_dispatch_count"] = 1
    mutations.append(("USER_OPERATOR_DISPATCH", mutant, fixture))

    mutant = copy.deepcopy(contract)
    mutant["totality"]["required_before_formula_admission"] = False
    mutations.append(("TOTALITY_BYPASS", mutant, fixture))

    mutant = copy.deepcopy(contract)
    mutant["relation_procedure"]["proof_budget_exhaustion"] = "PROVED"
    mutations.append(("PROOF_BUDGET_PASS", mutant, fixture))

    mutant = copy.deepcopy(contract)
    mutant["resource_limits"]["formula_node_count_max"] = 0
    mutations.append(("UNBOUNDED_OR_INVALID_FORMULA_LIMIT", mutant, fixture))

    fixture_mutant = copy.deepcopy(fixture)
    fixture_mutant["formula_cases"][0]["document"]["formula"]["terms"].reverse()
    mutations.append(("NONCANONICAL_CHILD_ORDER", contract, fixture_mutant))

    fixture_mutant = copy.deepcopy(fixture)
    fixture_mutant["formula_cases"][1]["document"]["formula_digest"] = "0" * 64
    mutations.append(("STALE_FORMULA_DIGEST", contract, fixture_mutant))

    mutant = copy.deepcopy(contract)
    mutant["governance"]["product_lanes"] = "15_OF_15_PASS"
    mutations.append(("PRODUCT_PASS_OVERCLAIM", mutant, fixture))

    failures = []
    for name, contract_candidate, fixture_candidate in mutations:
        errors = focused.validate(root, contract_override=contract_candidate, fixture_override=fixture_candidate)
        if not errors:
            failures.append(name)
    if failures:
        print("UNREJECTED_MUTATIONS: " + ", ".join(failures))
        return 1
    print(f"REFINEMENT_R0_V1_MUTATIONS: PASS {len(mutations)}/{len(mutations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
