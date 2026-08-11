#!/usr/bin/env python3
"""Validate the G4 independent Implementation Target Profile readiness audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/implementation-readiness-g4-audit-r1.json"
REVALIDATION_REL = (
    "spec/contracts/implementation-readiness-g4-dpg-revalidation-r1.json"
)
REVALIDATION_SCHEMA_REL = (
    "schemas/language/implementation-readiness-g4-dpg-revalidation-r1.schema.json"
)
METADATA_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
ROWS_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
POINTER_REL = "current/current-pointer.json"
R76_RECEIPT_REL = (
    "release/evidence/"
    "r76-global-implementation-target-trace-publication-closure-receipt.json"
)
BASELINE = "6782bcb576b7685a706b410620db8ea495aab901"
BASELINE_TREE = "117d667d1014eb32d03e6723d9ce211a1fe798c7"
FEATURE_P1_PREFIXES = ("CE-C-P1-", "CE-E-P1-", "TCC-P1-", "SFD-P1-")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    historical = load(root / CONTRACT_REL)
    contract = load(root / REVALIDATION_REL)
    metadata = load(root / METADATA_REL)
    rows = load(root / ROWS_REL)
    pointer = load(root / POINTER_REL)
    r76_receipt = load(root / R76_RECEIPT_REL)

    require(historical.get("canonical_baseline_commit") == BASELINE, "HISTORICAL_BASELINE_COMMIT")
    require(historical.get("canonical_baseline_tree") == BASELINE_TREE, "HISTORICAL_BASELINE_TREE")
    require(
        contract.get("historical_audit")
        == {
            "path": CONTRACT_REL,
            "preserved_immutable": True,
            "interpretation": "HISTORICAL_SNAPSHOT_NOT_CURRENT_GRAMMAR_AUTHORITY",
        },
        "HISTORICAL_AUDIT_FENCE",
    )
    require(
        contract.get("baseline", {}).get("canonical_commit")
        == "10e64f492f0529610673846139afcf0d95175663",
        "CURRENT_BASELINE_COMMIT",
    )
    require(
        contract.get("verdict")
        == "IMPLEMENTATION_TARGET_PROFILE_SPECIFICATION_READY_LOCAL_REVALIDATION",
        "VERDICT",
    )
    require(contract.get("evidence_level") == "E2_STRUCTURED_STATIC", "EVIDENCE_LEVEL")
    require(contract.get("external_post_commit_receipt_required") is True, "RECEIPT_FENCE")

    derived = metadata.get("derived_counts", {})
    expected_trace = {
        "feature_rows": 469,
        "stage_cells": 3283,
        "conformance_outcome_cells": 1407,
        "atomic_cells": 4221,
        "bound_direct": 3709,
        "bound_delegated": 4,
        "not_applicable": 508,
        "applicable_blocked": 0,
        "missing": 0,
        "conflicting": 0,
    }
    require(len(rows) == 469, "ROW_COUNT")
    require(len({row.get("feature_id") for row in rows}) == 469, "ROW_IDS_UNIQUE")
    require(metadata.get("catalog_feature_count") == 723, "CATALOG_COUNT")
    require(metadata.get("target_count") == 469, "TARGET_COUNT")
    require(metadata.get("excluded_count") == 254, "EXCLUDED_COUNT")
    require(metadata.get("base_count") == 462, "BASE_STATUS_COUNT")
    require(metadata.get("dependency_addition_count") == 6, "DEPENDENCY_COUNT")
    require(metadata.get("negative_compatibility_addition_count") == 1, "NEGATIVE_COMPATIBILITY_COUNT")
    expected_trace.update({"bound_direct": 3713, "not_applicable": 504})
    require(contract.get("traceability") == expected_trace, "CONTRACT_TRACE_COUNTS")
    require(derived.get("feature_rows") == 469, "DERIVED_FEATURE_ROWS")
    require(derived.get("stage_cells") == 3283, "DERIVED_STAGE_CELLS")
    require(derived.get("test_outcome_cells") == 1407, "DERIVED_OUTCOME_CELLS")
    require(derived.get("bound_direct_cells") == 3713, "DERIVED_DIRECT")
    require(derived.get("bound_delegated_cells") == 4, "DERIVED_DELEGATED")
    require(derived.get("not_applicable_cells") == 504, "DERIVED_NA")
    require(derived.get("applicable_blocked_cells") == 0, "DERIVED_BLOCKED")
    require(derived.get("missing_cells") == 0, "DERIVED_MISSING")
    require(derived.get("conflict_cells") == 0, "DERIVED_CONFLICT")
    require(derived.get("product_not_run_rows") == 469, "DERIVED_PRODUCT_NOT_RUN")

    parser = contract.get("parser_authority", {})
    require(parser.get("structural_grammar") == "spec/grammar/deeplus.dpg", "DPG_AUTHORITY")
    require(parser.get("parser_context") == "spec/grammar/deeplus.parser-contexts.json", "PARSER_CONTEXT_AUTHORITY")
    require(parser.get("surface_census_semantic_authority") is False, "EBNF_NONAUTHORITY")
    require(parser.get("legacy_ebnf_authority_evidence_count") == 0, "EBNF_AUTHORITY_ZERO")
    require(parser.get("surface_census_locator_count") == 297, "CENSUS_LOCATOR_COUNT")
    require(parser.get("direct_source_cell_count") == 438, "DIRECT_SOURCE_CELL_COUNT")

    gates = contract.get("gates", [])
    require([gate.get("id") for gate in gates] == ["G0", "G1", "G2", "G3", "G4"], "GATE_IDS")
    require(all(gate.get("verdict") == "PASS_E2" for gate in gates), "GATE_VERDICTS")

    fence = contract.get("authority_fence", {})
    require(fence.get("semantic_p0") == 0, "SEMANTIC_P0")
    require(fence.get("target_profile_unresolved_p0") == 0, "TARGET_P0")
    require(fence.get("target_profile_unresolved_p1") == 0, "TARGET_P1")
    require(fence.get("feature_p1") == "22_OPEN_OUTSIDE_TARGET_PROFILE", "FEATURE_P1_FENCE")
    require(fence.get("m13_actions") == "4_OPEN_SEPARATE", "M13_FENCE")
    require(fence.get("product_lanes") == "15_OF_15_NOT_RUN", "PRODUCT_LANE_FENCE")
    require(fence.get("production_implementation") == "NOT_PERFORMED", "IMPLEMENTATION_FENCE")
    require(fence.get("e4_e5_evidence_count") == 0, "E4_E5_FENCE")

    actions = pointer.get("open_actions", [])
    feature_p1 = [
        action.get("id", "")
        for action in actions
        if action.get("id", "").startswith(FEATURE_P1_PREFIXES)
    ]
    m13 = [action.get("id", "") for action in actions if action.get("id", "").startswith("M13-A")]
    require(len(feature_p1) == 22 and len(set(feature_p1)) == 22, "POINTER_FEATURE_P1")
    require(m13 == ["M13-A002", "M13-A003", "M13-A004", "M13-A005"], "POINTER_M13")
    product_lanes = pointer.get("product_lanes", {})
    require(len(product_lanes) == 15, "POINTER_PRODUCT_LANE_COUNT")
    require(set(product_lanes.values()) == {"NOT_RUN"}, "POINTER_PRODUCT_NOT_RUN")

    governance = metadata.get("governance", {})
    require(governance.get("gap_id") == "IR-XCUT-P1-054", "R76_GAP_ID")
    require(governance.get("e4_e5_evidence_count") == 0, "METADATA_E4_E5")
    require(
        r76_receipt.get("gap_state", {}).get("closed_gap") == "IR-XCUT-P1-054"
        or "IR-XCUT-P1-054" in json.dumps(r76_receipt, sort_keys=True),
        "R76_CLOSURE_EVIDENCE",
    )
    require(
        contract.get("next_blocking_cluster")
        == {
            "gap_id": "PREIMPL-P0-003",
            "name": "SFD-P1-009 impossible target-bound route",
            "activated": False,
        },
        "NEXT_BLOCKING_CLUSTER",
    )
    require(
        contract.get("conflict_register")
        == [
            {
                "id": "G4-CONFLICT-001",
                "disposition": "EXPLAINED_TYPED_HISTORICAL_PROMOTION_STATE",
                "source_repair": "NOT_REQUIRED",
            },
            {
                "id": "G4-CONFLICT-002",
                "disposition": "CLOSED_IN_LOCAL_R78_BY_DPG_AUTHORITY_REBIND",
                "source_repair": "PARSER_AUTHORITY_ENSEMBLE_AND_LOCATOR_ENFORCEMENT",
            },
        ],
        "CONFLICT_REGISTER",
    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    try:
        import jsonschema

        jsonschema.Draft202012Validator(load(root / REVALIDATION_SCHEMA_REL)).validate(
            load(root / REVALIDATION_REL)
        )
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover - reported as a stable receipt code
        errors.append(f"JSON_SCHEMA:{exc}")
    if errors:
        print("G4 IMPLEMENTATION READINESS AUDIT: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("G4 HISTORICAL AUDIT + R78 DPG AUTHORITY REVALIDATION: PASS")
    print("- readiness gates: 5/5 PASS_E2")
    print("- target rows: 469 (including one explicit negative-compatibility obligation)")
    print("- atomic trace cells: 4221")
    print("- missing/conflicting/blocked: 0/0/0")
    print("- target-profile unresolved P0/P1: 0/0")
    print("- feature P1: 22 OPEN outside target profile")
    print("- product lanes: 15/15 NOT_RUN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
