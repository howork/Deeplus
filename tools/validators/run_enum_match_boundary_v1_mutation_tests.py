#!/usr/bin/env python3
"""Reject bounded EnumBodyCommitmentV1 and MatchFallbackBoundaryV1 drift."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from validate_enum_match_boundary_v1 import CONTRACT_REL, FIXTURE_REL, load, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)
    mutations: list[tuple[str, dict, dict]] = []

    changed = copy.deepcopy(contract)
    changed["enum_body"]["minimum_case_count"] = 0
    mutations.append(("EMPTY_ENUM_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["enum_body"]["modes"]["COMMA_CASES"]["minimum_case_count"] = 1
    mutations.append(("ONE_CASE_COMMA_MODE_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["enum_body"]["modes"]["COMMA_CASES"]["member_count"] = 1
    mutations.append(("COMMA_MODE_MEMBER_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["enum_body"]["mixed_separator_count"] = 1
    mutations.append(("MIXED_ENUM_SEPARATOR_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["enum_body"]["empty_enum_profile"] = "CURRENT"
    mutations.append(("EMPTY_ENUM_CURRENT", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["match_fallback"]["fallback_guard_field"] = "OPTIONAL"
    mutations.append(("FALLBACK_GUARD_FIELD_ADDED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["match_fallback"]["maximum_fallback_count"] = 2
    mutations.append(("DUPLICATE_FALLBACK_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["match_fallback"]["fallback_must_be_final"] = False
    mutations.append(("NONFINAL_FALLBACK_ADMITTED", changed, fixture))

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
        "schema": "deeplus.enum-match-boundary-mutation-receipt/r1",
        "result": "PASS" if not missed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": len(results) - len(missed),
        "results": results,
        "missed": missed,
    }, indent=2))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
