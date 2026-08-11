#!/usr/bin/env python3
"""Reject bounded semantic drift in MemberVisibilityOmissionV1."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from validate_member_visibility_omission_v1 import CONTRACT_REL, FIXTURE_REL, load, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)

    mutations: list[tuple[str, dict, dict]] = []

    changed = copy.deepcopy(contract)
    changed["owner_rows"].pop()
    mutations.append(("OWNER_ROW_REMOVED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["owner_rows"][2]["omitted_resolution"] = "PUBLIC"
    mutations.append(("DEFAULT_PUBLIC_WIDENING", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["owner_rows"][9]["omitted_resolution"] = "PRIVATE"
    mutations.append(("CONFORMANCE_PRIVATE_DEFAULT", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["owner_rows"][0]["omitted_resolution"] = "PRIVATE"
    mutations.append(("OVERRIDE_PRIVATE_DEFAULT", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["hir_seal"]["actor_protocol_transport_rule"] = "ActorDecl.visibility"
    mutations.append(("ACTOR_PROTOCOL_VISIBILITY_NOT_MET", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["hir_seal"]["omitted_or_null_effective_domain_count"] = 1
    mutations.append(("UNRESOLVED_NULL_HIR", changed, fixture))

    changed_fixture = copy.deepcopy(fixture)
    missing_anchor = next(case for case in changed_fixture["cases"] if case["case_id"] == "MVO-R-001")
    missing_anchor["expected"] = {
        "outcome": "ADMIT",
        "resolution_kind": "DEFAULT_PRIVATE",
        "effective_domain": "PRIVATE",
        "resolution_anchor_id_or_null": None,
        "diagnostic_or_null": None,
    }
    mutations.append(("MISSING_ANCHOR_ADMITTED", contract, changed_fixture))

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

    missed = [result["mutation"] for result in results if result["result"] == "MISSED"]
    print(json.dumps({
        "schema": "deeplus.member-visibility-omission-mutation-receipt/r1",
        "result": "PASS" if not missed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": len(results) - len(missed),
        "results": results,
        "missed": missed,
    }, indent=2))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
