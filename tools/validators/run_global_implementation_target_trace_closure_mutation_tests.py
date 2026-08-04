#!/usr/bin/env python3
"""Bounded mutation suite for the R76 global trace-closure validator."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from validate_global_implementation_target_trace_closure import (
    CONTRACT_REL,
    OVERLAY_REL,
    ROWS_REL,
    load,
    validate_data,
)


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    base_contract = load(ROOT / CONTRACT_REL)
    base_overlay = load(ROOT / OVERLAY_REL)
    base_rows = load(ROOT / ROWS_REL)
    cases = []

    def add(case_id: str, mutate, expected_fragment: str) -> None:
        contract = copy.deepcopy(base_contract)
        overlay = copy.deepcopy(base_overlay)
        rows = copy.deepcopy(base_rows)
        mutate(contract, overlay, rows)
        cases.append((case_id, contract, overlay, rows, expected_fragment))

    add("R76-MUT-001", lambda c, o, r: c["cells"].pop(), "EXACT_CELL_COUNT")
    add("R76-MUT-002", lambda c, o, r: o["bindings"][0].__setitem__("feature_id", "missing_feature"), "CELL_0000_BIND_FEATURE")
    add("R76-MUT-003", lambda c, o, r: c["authority_fence"].__setitem__("product_lanes", "1_OF_15_PASS"), "PRODUCT_LANES")
    add("R76-MUT-004", lambda c, o, r: c.__setitem__("canonical_baseline_commit", "0" * 40), "CONTRACT_BASELINE")
    add("R76-MUT-005", lambda c, o, r: o["evidence_entries"][0].__setitem__("locator", "/cells/1"), "CELL_0000_LOCATOR")
    add("R76-MUT-006", lambda c, o, r: c["cells"][0]["feature_contract"].__setitem__("notes", "widened"), "CELL_0000_NOTES")
    test_index = next(i for i, cell in enumerate(base_contract["cells"]) if cell["stage"] == "CONFORMANCE_TESTS")
    add("R76-MUT-007", lambda c, o, r: c["cells"][test_index]["obligation"].__setitem__("example_ids", ["EX-NOT-REGISTERED"]), f"CELL_{test_index:04d}_EXAMPLE_ID")
    add("R76-MUT-008", lambda c, o, r: r[0]["stages"][2].__setitem__("disposition", "APPLICABLE_BLOCKED_BY_GAP"), "TRACE_COUNTS")

    failures = []
    for case_id, contract, overlay, rows, expected in cases:
        errors = validate_data(ROOT, contract, overlay, rows)
        if not any(expected in error for error in errors):
            failures.append({"case_id": case_id, "expected": expected, "observed": errors[:8]})

    receipt = {
        "schema": "deeplus.global-implementation-target-trace-closure-mutation-receipt/r1",
        "result": "PASS" if not failures else "FAIL",
        "case_count": len(cases),
        "passed": len(cases) - len(failures),
        "failed": len(failures),
        "failures": failures,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
