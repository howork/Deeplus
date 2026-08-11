#!/usr/bin/env python3
"""Reject bounded TraitAutoPolicyRegistryV1 drift."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from validate_trait_auto_policy_registry_v1 import CONTRACT_REL, FIXTURE_REL, load, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)
    mutations: list[tuple[str, dict, dict]] = []

    changed = copy.deepcopy(contract)
    changed["source_surface"]["trait_declaration_creates_policy"] = True
    mutations.append(("SOURCE_CREATES_POLICY", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["source_surface"]["user_owned_trait_opt_in"] = "ADMIT"
    mutations.append(("USER_POLICY_OWNER_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["registry"]["policy_count"] = 3
    mutations.append(("POLICY_COUNT_WIDENED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["registry"]["rows"][0]["policy_digest"] = "0" * 64
    mutations.append(("POLICY_DIGEST_MUTATED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["registry"]["rows"][0]["termination"]["finite_nominal_graph"] = False
    mutations.append(("FINITE_GRAPH_DISABLED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["registry"]["rows"][0]["excluded_evidence_sources"].remove("PROVIDER")
    mutations.append(("PROVIDER_EVIDENCE_ADMITTED", changed, fixture))

    changed_fixture = copy.deepcopy(fixture)
    target = next(case for case in changed_fixture["cases"] if case["case_id"] == "R87-AUTO-R-001")
    target["expected"] = {"outcome": "ADMIT_POLICY_BINDING", "diagnostic_or_null": None}
    mutations.append(("USER_OPT_IN_FALSE_PASS", contract, changed_fixture))

    changed = copy.deepcopy(contract)
    changed["governance"]["product_lanes"] = "15/15_PASS"
    mutations.append(("PRODUCT_PASS_OVERCLAIM", changed, fixture))

    results = []
    for name, candidate_contract, candidate_fixture in mutations:
        errors = validate(root, contract_override=candidate_contract, fixture_override=candidate_fixture, validate_schema=False)
        results.append({"mutation": name, "result": "REJECTED" if errors else "MISSED", "error_count": len(errors)})
    missed = [row["mutation"] for row in results if row["result"] == "MISSED"]
    print(json.dumps({
        "schema": "deeplus.trait-auto-policy-registry-mutation-receipt/r1",
        "result": "PASS" if not missed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": len(results) - len(missed),
        "results": results,
        "missed": missed,
    }, indent=2))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
