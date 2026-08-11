#!/usr/bin/env python3
"""Reject bounded SourceItemCommitmentV1 drift."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from validate_source_item_commitment_v1 import CONTRACT_REL, FIXTURE_REL, load, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)
    mutations: list[tuple[str, dict, dict]] = []

    changed = copy.deepcopy(contract)
    changed["rows"].pop()
    mutations.append(("CONTEXTUAL_ROW_REMOVED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["commitment_law"]["semantic_lookup_count"] = 1
    mutations.append(("SEMANTIC_LOOKUP_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["commitment_law"]["pre_marker_failure"] = "KEEP_PREFIX_TOKENS"
    mutations.append(("ROLLBACK_CONSUMES_TOKENS", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["commitment_law"]["post_marker_failure"] = "FALLBACK_TO_STATEMENT"
    mutations.append(("POST_MARKER_FALLBACK_ADMITTED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["rows"][1]["fallback_after_marker"] = "ROLLBACK_ZERO_TOKENS"
    mutations.append(("ACTOR_CALL_WINS_AFTER_MARKER", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["commitment_law"]["annotation_selects_annotated_item_without_statement_fallback"] = False
    mutations.append(("ANNOTATION_STATEMENT_FALLBACK", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["rows"][11]["profiles"] = ["stable", "preview"]
    mutations.append(("PREVIEW_EXTERN_STABLE", changed, fixture))

    changed_fixture = copy.deepcopy(fixture)
    target = next(case for case in changed_fixture["cases"] if case["case_id"] == "R88-SIC-R-001")
    target["expected"] = {"outcome": "ROLLBACK_AND_PARSE_STATEMENT", "owner_or_null": "Statement", "diagnostic_or_null": None}
    mutations.append(("COMMITTED_DECLARATION_FALSE_FALLBACK", contract, changed_fixture))

    changed = copy.deepcopy(contract)
    changed["governance"]["product_lanes"] = "15/15_PASS"
    mutations.append(("PRODUCT_PASS_OVERCLAIM", changed, fixture))

    results = []
    for name, candidate_contract, candidate_fixture in mutations:
        errors = validate(root, contract_override=candidate_contract, fixture_override=candidate_fixture, validate_schema=False)
        results.append({"mutation": name, "result": "REJECTED" if errors else "MISSED", "error_count": len(errors)})
    missed = [row["mutation"] for row in results if row["result"] == "MISSED"]
    print(json.dumps({
        "schema": "deeplus.source-item-commitment-mutation-receipt/r1",
        "result": "PASS" if not missed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": len(results) - len(missed),
        "results": results,
        "missed": missed,
    }, indent=2))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
