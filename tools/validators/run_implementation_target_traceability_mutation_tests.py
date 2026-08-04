#!/usr/bin/env python3
"""Focused mutation oracles for the current target traceability ledger."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from validate_implementation_target_traceability import load_registry, validate


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    metadata, rows = load_registry(root)
    mutants = []

    value = copy.deepcopy(rows); del value[0]
    mutants.append(("ROW_DELETE", metadata, value))
    value = copy.deepcopy(rows); value.insert(1, copy.deepcopy(value[0]))
    mutants.append(("ROW_DUPLICATE", metadata, value))
    meta = copy.deepcopy(metadata); meta["target_feature_id_list_sha256"] = "0" * 64
    mutants.append(("TARGET_DIGEST", meta, rows))
    value = copy.deepcopy(rows); del value[0]["stages"][0]
    mutants.append(("STAGE_DELETE", metadata, value))
    value = copy.deepcopy(rows); value[0]["stages"][0], value[0]["stages"][1] = value[0]["stages"][1], value[0]["stages"][0]
    mutants.append(("STAGE_ORDER", metadata, value))
    value = copy.deepcopy(rows)
    direct = next(cell for row in value for stage in row["stages"] for cell in stage.get("outcomes", [stage]) if cell.get("disposition") == "BOUND_DIRECT")
    direct["evidence_refs"] = []
    mutants.append(("DIRECT_EVIDENCE_EMPTY", metadata, value))
    value = copy.deepcopy(rows)
    na = next(cell for row in value for stage in row["stages"] for cell in stage.get("outcomes", [stage]) if cell.get("disposition") == "NOT_APPLICABLE")
    na["not_applicable"]["reason_code"] = "UNREGISTERED_REASON"
    mutants.append(("NA_REASON", metadata, value))
    value = copy.deepcopy(rows)
    rebound = next(cell for row in value for stage in row["stages"] for cell in stage.get("outcomes", [stage]) if cell.get("disposition") == "BOUND_DIRECT")
    rebound.update({
        "disposition": "APPLICABLE_BLOCKED_BY_GAP",
        "blocked_gap_ids": ["IR-XCUT-P1-054"],
        "not_applicable": None,
    })
    mutants.append(("R76_ZERO_BLOCKED_INVARIANT", metadata, value))
    value = copy.deepcopy(rows); value[0]["stages"][-1]["outcomes"].pop()
    mutants.append(("TEST_OUTCOME_DELETE", metadata, value))
    value = copy.deepcopy(rows); value[0]["product_execution"] = "PASS"
    mutants.append(("PRODUCT_OVERCLAIM", metadata, value))
    meta = copy.deepcopy(metadata)
    pointer = next(
        item for item in meta["evidence_registry"]
        if item.get("locator_kind") == "JSON_POINTER"
        and item.get("path", "").endswith(
            "scalar-numeric-fixed-operator-evidence-r1.json"
        )
    )
    pointer["locator"] = "/__missing_r54_pointer__"
    mutants.append(("EVIDENCE_LOCATOR_MISSING", meta, rows))
    value = copy.deepcopy(rows)
    overlay_row = next(
        row for row in value
        if row["feature_id"] == "numeric_operator_core"
    )
    overlay_cell = next(
        stage for stage in overlay_row["stages"]
        if stage["stage"] == "AST_FRONTEND"
    )
    overlay_cell.update({
        "disposition": "APPLICABLE_BLOCKED_BY_GAP",
        "blocked_gap_ids": ["IR-XCUT-P1-054"],
        "not_applicable": None,
    })
    mutants.append(("R54_OVERLAY_CELL_REBLOCKED", metadata, value))
    meta = copy.deepcopy(metadata)
    pointer = next(
        item for item in meta["evidence_registry"]
        if item.get("locator_kind") == "JSON_POINTER"
        and item.get("path", "").endswith(
            "lexical-trivia-source-root-attachment-r1.json"
        )
    )
    pointer["locator"] = "/__missing_r55_pointer__"
    mutants.append(("R55_EVIDENCE_LOCATOR_MISSING", meta, rows))
    value = copy.deepcopy(rows)
    overlay_row = next(
        row for row in value
        if row["feature_id"] == "comment_trivia_lexical_priority_law"
    )
    test_stage = next(
        stage for stage in overlay_row["stages"]
        if stage["stage"] == "CONFORMANCE_TESTS"
    )
    overlay_cell = next(
        cell for cell in test_stage["outcomes"]
        if cell["outcome"] == "POSITIVE"
    )
    overlay_cell.update({
        "disposition": "APPLICABLE_BLOCKED_BY_GAP",
        "evidence_refs": [],
        "blocked_gap_ids": ["IR-XCUT-P1-054"],
        "not_applicable": None,
    })
    mutants.append(("R55_OVERLAY_CELL_REBLOCKED", metadata, value))

    results = []
    for mutation_id, meta, candidate_rows in mutants:
        errors = validate(root, meta, candidate_rows)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})
    passed = all(row["rejected"] for row in results)
    print(json.dumps({
        "schema": "deeplus.implementation-target-traceability-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": sum(row["rejected"] for row in results),
        "results": results,
        "product_execution": "15_OF_15_NOT_RUN",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
