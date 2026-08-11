#!/usr/bin/env python3
"""Validate the R76 global implementation-target trace closure contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/implementation-target-global-trace-closure-r1.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/global-trace-closure-evidence-r1.json"
ROWS_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
BASELINE = "40a826af29410af1a14c6a7dec3193cd59ba9b12"
STAGE_COUNTS = {
    "AST_FRONTEND": 11,
    "CONFORMANCE_TESTS": 961,
    "DYNAMIC_LOWERING": 206,
    "STATIC_SEMANTICS": 64,
}
OUTCOME_COUNTS = {"BOUNDARY": 408, "POSITIVE": 145, "REJECT": 408}
R77_CURRENT_TARGET_TRACE_COUNTS = {
    "BOUND_DIRECT": 3712,
    "BOUND_DELEGATED": 4,
    "NOT_APPLICABLE": 505,
    "APPLICABLE_BLOCKED_BY_GAP": 0,
}
R88_CATALOG_REASSEMBLY_RELOCATIONS = {
    (
        "static_evidence_selector_msp",
        "spec/features/catalog/chunks/part-0015.json",
        "/36",
    ): ("spec/features/catalog/chunks/part-0034.json", "/0"),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(value: Any, pointer: str) -> Any:
    current = value
    for raw in pointer.removeprefix("/").split("/") if pointer else []:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def feature_catalog(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, tuple[str, str]]]:
    rows: dict[str, dict[str, Any]] = {}
    locations: dict[str, tuple[str, str]] = {}
    for path in sorted((root / "spec/features/catalog/chunks").glob("part-*.json")):
        rel = path.relative_to(root).as_posix()
        for index, row in enumerate(load(path)):
            rows[row["feature_id"]] = row
            locations[row["feature_id"]] = (rel, f"/{index}")
    return rows, locations


def corpus_ids(root: Path) -> set[str]:
    text = (root / "examples/guide/review-corpus.md").read_text(encoding="utf-8")
    return set(re.findall(r"(?m)^## (EX-[A-Za-z0-9_-]+)\b", text))


def validate_data(root: Path, contract: dict[str, Any], overlay: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    catalog, locations = feature_catalog(root)
    examples = corpus_ids(root)
    cells = contract.get("cells", [])
    bindings = overlay.get("bindings", [])
    evidence = overlay.get("evidence_entries", [])

    require(contract.get("canonical_baseline_commit") == BASELINE, "CONTRACT_BASELINE")
    require(overlay.get("canonical_baseline_commit") == BASELINE, "OVERLAY_BASELINE")
    require(len(cells) == len(bindings) == len(evidence) == 1242, "EXACT_CELL_COUNT")
    require(len(overlay.get("feature_ids", [])) == 409, "EXACT_FEATURE_COUNT")
    require(len(set(overlay.get("feature_ids", []))) == 409, "FEATURE_IDS_UNIQUE")
    require(contract.get("scope", {}).get("stage_counts") == STAGE_COUNTS, "STAGE_COUNTS")
    require(contract.get("scope", {}).get("outcome_counts") == OUTCOME_COUNTS, "OUTCOME_COUNTS")
    require(contract.get("scope", {}).get("remaining_blocked_cells") == 0, "CONTRACT_ZERO_BLOCKED")
    require(overlay.get("counts", {}).get("remaining_blocked_count") == 0, "OVERLAY_ZERO_BLOCKED")

    fence = contract.get("authority_fence", {})
    require(fence.get("semantic_p0") == 0, "SEMANTIC_P0")
    require(fence.get("feature_p1") == "22_OPEN_UNCHANGED", "FEATURE_P1")
    require(fence.get("m13_actions") == "4_OPEN_UNCHANGED", "M13_ACTIONS")
    require(fence.get("product_lanes") == "15_OF_15_NOT_RUN", "PRODUCT_LANES")
    require(fence.get("production_implementation") == "NOT_RUN", "PRODUCTION_NOT_RUN")
    require(fence.get("new_language_semantics") == 0, "NO_NEW_LANGUAGE_SEMANTICS")
    require(fence.get("e4_e5_evidence_count") == 0, "NO_E4_E5")

    seen_cells: set[tuple[str, str, str | None]] = set()
    seen_evidence: set[str] = set()
    for index, (cell, binding, item) in enumerate(zip(cells, bindings, evidence)):
        prefix = f"CELL_{index:04d}"
        feature_id = cell.get("feature_id")
        stage = cell.get("stage")
        outcome = cell.get("outcome")
        identity = (feature_id, stage, outcome)
        require(identity not in seen_cells, f"{prefix}_DUPLICATE")
        seen_cells.add(identity)
        require(cell.get("cell_id") == f"R76-CELL-{index + 1:04d}", f"{prefix}_ID")
        require(feature_id in catalog, f"{prefix}_FEATURE")
        require(cell.get("predecessor") == {"disposition": "APPLICABLE_BLOCKED_BY_GAP", "gap_ids": ["IR-XCUT-P1-054"]}, f"{prefix}_PREDECESSOR")
        require(cell.get("evidence_level") == "E2_STRUCTURED_STATIC", f"{prefix}_EVIDENCE_LEVEL")
        require(cell.get("product_execution") == "NOT_RUN", f"{prefix}_PRODUCT")
        require(cell.get("final_disposition") in {"BOUND_DIRECT", "NOT_APPLICABLE"}, f"{prefix}_DISPOSITION")

        if feature_id in catalog:
            row = catalog[feature_id]
            location = locations[feature_id]
            snapshot = cell.get("feature_contract", {})
            historical_location = (snapshot.get("path"), snapshot.get("json_pointer"))
            accepted_location = R88_CATALOG_REASSEMBLY_RELOCATIONS.get(
                (feature_id, *historical_location), historical_location
            )
            require(accepted_location == location, f"{prefix}_LOCATION")
            require(snapshot.get("status_enum") == row.get("status_enum"), f"{prefix}_STATUS")
            require(snapshot.get("feature_kind") == row.get("feature_kind"), f"{prefix}_KIND")
            require(snapshot.get("trace_class") == row.get("trace_class"), f"{prefix}_CLASS")
            require(snapshot.get("notes") == row.get("notes") and bool(snapshot.get("notes")), f"{prefix}_NOTES")

        require(binding.get("feature_id") == feature_id, f"{prefix}_BIND_FEATURE")
        require(binding.get("stage") == stage and binding.get("outcome") == outcome, f"{prefix}_BIND_CELL")
        require(binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP", f"{prefix}_BIND_PREDECESSOR")
        require(binding.get("disposition") == cell.get("final_disposition"), f"{prefix}_BIND_DISPOSITION")
        require(len(binding.get("evidence_keys", [])) == 1, f"{prefix}_BIND_EVIDENCE")
        key = binding.get("evidence_keys", [None])[0]
        require(key == item.get("evidence_key"), f"{prefix}_EVIDENCE_KEY")
        require(key not in seen_evidence, f"{prefix}_EVIDENCE_DUPLICATE")
        seen_evidence.add(key)
        require(item.get("class") == "IMPLEMENTATION_TARGET_CELL_CONTRACT", f"{prefix}_EVIDENCE_CLASS")
        require(item.get("path") == CONTRACT_REL, f"{prefix}_EVIDENCE_PATH")
        require(item.get("locator_kind") == "JSON_POINTER", f"{prefix}_LOCATOR_KIND")
        require(item.get("locator") == f"/cells/{index}", f"{prefix}_LOCATOR")
        require(resolve(contract, item.get("locator")) == cell, f"{prefix}_LOCATOR_RESOLUTION")

        obligation = cell.get("obligation", {})
        if stage == "AST_FRONTEND":
            require(obligation.get("frontend_contract") == "spec/frontend/frontend-model.json", f"{prefix}_FRONTEND")
        elif stage == "STATIC_SEMANTICS":
            require(obligation.get("obligation_kind") == "EXACT_FEATURE_STATIC_ADMISSION", f"{prefix}_STATIC_KIND")
        elif stage == "DYNAMIC_LOWERING":
            require(obligation.get("hir_bridge") == "spec/contracts/hir-h1-current-mir-bridge.json", f"{prefix}_HIR")
            require(obligation.get("mir_registry") == "spec/contracts/hir-mir-lowering-registry.json", f"{prefix}_MIR")
            require(obligation.get("backend_contract") == "spec/contracts/cranelift-backend-current.json", f"{prefix}_BACKEND")
            require(obligation.get("obligation_kind") in {"ZERO_DYNAMIC_RESIDUE", "CANONICAL_HIR_H1_MIR_PROJECTION"}, f"{prefix}_DYNAMIC_KIND")
        elif stage == "CONFORMANCE_TESTS":
            require(outcome in {"POSITIVE", "BOUNDARY", "REJECT"}, f"{prefix}_OUTCOME")
            require(obligation.get("execution_state") == "DESIGN_STATIC_SPECIFIED_PRODUCT_NOT_RUN", f"{prefix}_TEST_EXECUTION")
            referenced = set()
            for field in ("example_ids", "admitted_example_ids", "rejected_example_ids"):
                referenced.update(obligation.get(field, []))
            require(referenced <= examples, f"{prefix}_EXAMPLE_ID")
            require(bool(obligation.get("expected")) and bool(obligation.get("oracle")), f"{prefix}_TEST_ORACLE")

    require(sum(1 for cell in cells if cell["final_disposition"] == "BOUND_DIRECT") == 1236, "DIRECT_COUNT")
    require(sum(1 for cell in cells if cell["final_disposition"] == "NOT_APPLICABLE") == 6, "NA_COUNT")

    trace_counts = {"BOUND_DIRECT": 0, "BOUND_DELEGATED": 0, "NOT_APPLICABLE": 0, "APPLICABLE_BLOCKED_BY_GAP": 0}
    for row in rows:
        require(row.get("product_execution") == "NOT_RUN", f"ROW_PRODUCT:{row.get('feature_id')}")
        for stage in row.get("stages", []):
            for item in stage.get("outcomes", [stage]):
                trace_counts[item.get("disposition")] = trace_counts.get(item.get("disposition"), 0) + 1
    # R76 is an immutable closure record.  Its contract contains no
    # numeric_literal_suffix cell; R77 reclassifies the same target row as an
    # explicit negative-compatibility obligation, which moves two generated
    # cells from N/A to direct without changing target membership or semantics.
    require(trace_counts == R77_CURRENT_TARGET_TRACE_COUNTS, "TRACE_COUNTS")

    for rel in (
        "spec/frontend/frontend-model.json",
        "spec/contracts/hir-h1-current-mir-bridge.json",
        "spec/contracts/hir-mir-lowering-registry.json",
        "spec/contracts/cranelift-backend-current.json",
    ):
        require((root / rel).is_file(), f"REQUIRED_CONTRACT:{rel}")
    return errors


def validate(root: Path, contract_path: Path, overlay_path: Path, rows_path: Path) -> list[str]:
    return validate_data(root, load(contract_path), load(overlay_path), load(rows_path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--rows", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(
        root,
        args.contract or root / CONTRACT_REL,
        args.overlay or root / OVERLAY_REL,
        args.rows or root / ROWS_REL,
    )
    receipt = {
        "schema": "deeplus.global-implementation-target-trace-closure-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "baseline": BASELINE,
        "feature_rows": 469,
        "affected_features": 409,
        "contract_cells": 1242,
        "final_trace_counts": R77_CURRENT_TARGET_TRACE_COUNTS,
        "historical_contract": "R76 closure contract retained; current rows revalidated under R77 negative-compatibility policy",
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
