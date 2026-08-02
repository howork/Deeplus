#!/usr/bin/env python3
"""Focused mutation oracles for current-contract authority status R1."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from validate_current_contract_authority_status import REGISTRY_REL, load, validate


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    source = load(root / REGISTRY_REL)
    mutants = []

    value = copy.deepcopy(source)
    value["rows"][0]["current_authority"]["gap_status"] = "APPROVED_NOT_INTEGRATED"
    mutants.append(("STALE_GAP_STATUS", value))

    value = copy.deepcopy(source)
    value["rows"][2]["current_authority"]["publication_closure_commit"] = value["rows"][3]["current_authority"]["publication_closure_commit"]
    mutants.append(("CROSS_BOUND_CLOSURE", value))

    value = copy.deepcopy(source)
    del value["rows"][3]["historical_provenance"]
    mutants.append(("MISSING_HISTORY", value))

    value = copy.deepcopy(source)
    value["rows"][4]["contract_sha256"] = "0" * 64
    mutants.append(("CONTRACT_DIGEST_DRIFT", value))

    value = copy.deepcopy(source)
    value["rows"].append(copy.deepcopy(value["rows"][0]))
    mutants.append(("DUPLICATE_ROW", value))

    value = copy.deepcopy(source)
    value["rows"][0]["product_execution"] = "PASS"
    mutants.append(("PRODUCT_OVERCLAIM", value))

    results = []
    for mutation_id, mutant in mutants:
        errors = validate(root, mutant)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})

    passed = all(row["rejected"] for row in results)
    print(json.dumps({
        "schema": "deeplus.current-contract-authority-status-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": sum(row["rejected"] for row in results),
        "results": results,
        "product_execution": "NOT_RUN",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
