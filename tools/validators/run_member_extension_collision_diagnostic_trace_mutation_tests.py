#!/usr/bin/env python3
"""Run exactly 14 bounded in-memory mutations against the R74 validator."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_member_extension_collision_diagnostic_trace as focused  # noqa: E402

Mutation = Tuple[str, str, Callable[[Dict[str, Any]], None]]
MUTATION_PLAN_SOURCE = "R74_VALIDATION_HARNESS"


def change(values: Dict[str, Any], path: str) -> Any:
    value = copy.deepcopy(values[path])
    values[path] = value
    return value


def feature(values: Dict[str, Any]) -> Dict[str, Any]:
    rows = change(values, focused.FEATURE_CATALOG)
    return next(row for row in rows if row.get("feature_id") == focused.FEATURE)


def target_cell(values: Dict[str, Any]) -> Dict[str, Any]:
    rows = change(values, focused.ROWS)
    row = next(row for row in rows if row.get("feature_id") == focused.FEATURE)
    return next(stage for stage in row["stages"] if stage.get("stage") == "DIAGNOSTICS")


def predicate(values: Dict[str, Any]) -> Dict[str, Any]:
    rows = change(values, focused.PREDICATES)
    return next(row for row in rows if row.get("predicate_id") == "MemberExtensionCollisionRejected")


def diagnostic(values: Dict[str, Any]) -> Dict[str, Any]:
    rows = change(values, focused.DIAGNOSTICS)
    return next(row for row in rows if row.get("diagnostic_id") == "MEMBER_EXTENSION_COLLISION")


def m01_missing_feature_ref(values: Dict[str, Any]) -> None:
    feature(values)["normative_trace_refs"]["diagnostics"] = []


def m02_extra_feature_ref(values: Dict[str, Any]) -> None:
    feature(values)["normative_trace_refs"]["diagnostics"].append("AMBIGUOUS_EXTENSION_CANDIDATE")


def m03_target_disposition(values: Dict[str, Any]) -> None:
    target_cell(values)["disposition"] = "NOT_APPLICABLE"


def m04_target_evidence(values: Dict[str, Any]) -> None:
    target_cell(values)["evidence_refs"] = [focused.FEATURE_REF_ID]


def m05_target_na_payload(values: Dict[str, Any]) -> None:
    target_cell(values)["not_applicable"] = {
        "reason_code": "NA_DIAGNOSTIC_NO_REJECTION_WARNING_OR_INFO_CONDITION",
        "authority_boundary": "DIAGNOSTIC_AUTHORITY",
        "justification_evidence_refs": [focused.FEATURE_REF_ID],
        "rationale": "stale",
    }


def m06_diagnostic_status(values: Dict[str, Any]) -> None:
    diagnostic(values)["diagnostic_status"] = "retired"


def m07_diagnostic_severity(values: Dict[str, Any]) -> None:
    diagnostic(values)["severity"] = "warning"


def m08_diagnostic_stage(values: Dict[str, Any]) -> None:
    diagnostic(values)["stage"] = "parser"


def m09_diagnostic_emission(values: Dict[str, Any]) -> None:
    diagnostic(values)["emission_domain"] = "historical"


def m10_predicate_primary(values: Dict[str, Any]) -> None:
    predicate(values)["active_primary_diagnostic"] = "AMBIGUOUS_EXTENSION_CANDIDATE"


def m11_predicate_secondary(values: Dict[str, Any]) -> None:
    predicate(values)["secondary_diagnostics"] = ["STABLE_MEMBER_EXTENSION_COLLISION"]


def m12_r72_fence(values: Dict[str, Any]) -> None:
    change(values, focused.R72_CONTRACT)["diagnostic_fence"]["sole_active_primary"] = "OTHER"


def m13_non_target(values: Dict[str, Any]) -> None:
    rows = change(values, focused.ROWS)
    row = next(row for row in rows if row.get("feature_id") != focused.FEATURE)
    row["stages"][0]["disposition"] = "BOUND_DELEGATED"


def m14_product_claim(values: Dict[str, Any]) -> None:
    metadata = change(values, focused.METADATA)
    metadata["governance"]["product_lanes"] = "1_OF_15_PASS"
    metadata["governance"]["github_publication"] = "PUBLISHED"


MUTATION_PLAN: List[Mutation] = [
    ("M01", "G01", m01_missing_feature_ref),
    ("M02", "G01", m02_extra_feature_ref),
    ("M03", "G03", m03_target_disposition),
    ("M04", "G03", m04_target_evidence),
    ("M05", "G03", m05_target_na_payload),
    ("M06", "G04", m06_diagnostic_status),
    ("M07", "G04", m07_diagnostic_severity),
    ("M08", "G04", m08_diagnostic_stage),
    ("M09", "G04", m09_diagnostic_emission),
    ("M10", "G04", m10_predicate_primary),
    ("M11", "G04", m11_predicate_secondary),
    ("M12", "G05", m12_r72_fence),
    ("M13", "G03", m13_non_target),
    ("M14", "G06", m14_product_claim),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    base = focused.load_inputs(root)
    before = focused.predecessor_rows(root)
    planned_ids = [row[0] for row in MUTATION_PLAN]
    exact_ids = [f"M{index:02d}" for index in range(1, 15)]
    normal_errors = focused.validate(root, overrides=base, predecessor_rows_override=before)
    if normal_errors:
        print(json.dumps({
            "schema": "deeplus.r74-member-extension-collision-diagnostic-trace-mutation-receipt/r1",
            "result": "BLOCKED_BASELINE", "plan_source": MUTATION_PLAN_SOURCE,
            "declared_mutation_count": 14, "executed_mutation_count": 0,
            "plan_id_sequence_exact": planned_ids == exact_ids,
            "normal_errors": normal_errors, "product_execution": "NOT_RUN",
        }, separators=(",", ":")))
        return 1

    results = []
    for mutation_id, expected_gate, mutate in MUTATION_PLAN:
        values = copy.deepcopy(base)
        mutate(values)
        errors = focused.validate(root, overrides=values, predecessor_rows_override=before)
        expected_rejection = any(item.startswith(expected_gate + ":") for item in errors)
        results.append({"mutation_id": mutation_id, "expected_gate": expected_gate,
                        "rejected": bool(errors), "expected_rejection": expected_rejection,
                        "first_error": errors[0] if errors else None})

    passed = planned_ids == exact_ids and len(results) == 14 and all(
        row["rejected"] and row["expected_rejection"] for row in results)
    print(json.dumps({
        "schema": "deeplus.r74-member-extension-collision-diagnostic-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL", "plan_source": MUTATION_PLAN_SOURCE,
        "declared_mutation_count": 14, "executed_mutation_count": len(results),
        "rejected_mutation_count": sum(row["rejected"] for row in results),
        "expected_gate_rejection_count": sum(row["expected_rejection"] for row in results),
        "plan_id_sequence_exact": planned_ids == exact_ids, "results": results,
        "product_execution": "NOT_RUN",
    }, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
