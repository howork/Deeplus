#!/usr/bin/env python3
"""Validate the bounded R54 scalar numeric/fixed-operator evidence overlay.

This validator checks design-static evidence bindings.  It deliberately does
not interpret a passing result as parser, checker, runtime, or product support.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


OVERLAY_REL = (
    "spec/traceability/implementation-target-profile-r1/"
    "scalar-numeric-fixed-operator-evidence-r1.json"
)
SCHEMA_REL = "schemas/language/scalar-numeric-fixed-operator-evidence-r1.schema.json"
FEATURE_DIR = "spec/features/catalog/chunks"

TOP_KEYS = {
    "$schema",
    "schema",
    "revision",
    "canonical_baseline_commit",
    "local_predecessor_commit",
    "candidate_status",
    "feature_ids",
    "evidence_entries",
    "bindings",
    "acceptance_cases",
    "counts",
    "guards",
}
EVIDENCE_KEYS = {
    "evidence_key",
    "class",
    "path",
    "locator_kind",
    "locator",
    "stage_role",
}
BINDING_KEYS = {
    "feature_id",
    "stage",
    "outcome",
    "disposition",
    "evidence_keys",
    "delegate_feature_id",
    "not_applicable",
}
CASE_KEYS = {
    "case_id",
    "feature_id",
    "outcome",
    "source_or_subject",
    "expected",
    "diagnostic_or_null",
    "assertions",
    "execution_state",
}

FEATURE_IDS = sorted(
    [
        "numeric_literal_suffix",
        "numeric_literal_lexical_contract",
        "numeric_operator_core",
        "rational_exact_numeric_value",
        "complex_core_numeric_value",
        "scalar_real_complex_power",
        "float_alias_float64",
        "uint_default_unsigned_integer_domain",
        "fixed_operator_conformance_overloading",
        "linear_algebra_complex_inner_product_law",
        "caret_power_operator_msp",
        "caret_power_right_associative_math_law",
        "closed_operator_symbols_open_named_extensions",
        "operator_precedence_table_phase_a",
    ]
)
OUTCOMES = {"POSITIVE", "BOUNDARY", "REJECT"}
STAGES = {"AST_FRONTEND", "STATIC_SEMANTICS", "DYNAMIC_LOWERING", "CONFORMANCE_TESTS"}
DISPOSITIONS = {"BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE"}
LOCATOR_KINDS = {"FILE", "JSON_POINTER", "REGISTRY_ID"}
STAGE_ROLES = {
    "AST_FRONTEND",
    "STATIC_SEMANTICS",
    "DYNAMIC_LOWERING",
    "CONFORMANCE_TESTS:POSITIVE",
    "CONFORMANCE_TESTS:BOUNDARY",
    "CONFORMANCE_TESTS:REJECT",
}

STRUCTURAL_CELLS = {
    ("numeric_literal_suffix", "STATIC_SEMANTICS", None),
    ("numeric_operator_core", "AST_FRONTEND", None),
    ("rational_exact_numeric_value", "DYNAMIC_LOWERING", None),
    ("complex_core_numeric_value", "DYNAMIC_LOWERING", None),
    ("scalar_real_complex_power", "DYNAMIC_LOWERING", None),
    ("float_alias_float64", "DYNAMIC_LOWERING", None),
    ("uint_default_unsigned_integer_domain", "DYNAMIC_LOWERING", None),
    ("fixed_operator_conformance_overloading", "DYNAMIC_LOWERING", None),
    ("linear_algebra_complex_inner_product_law", "DYNAMIC_LOWERING", None),
    ("closed_operator_symbols_open_named_extensions", "DYNAMIC_LOWERING", None),
    ("operator_precedence_table_phase_a", "AST_FRONTEND", None),
}
TWO_OUTCOME_FEATURES = {
    "numeric_literal_suffix",
    "numeric_literal_lexical_contract",
    "scalar_real_complex_power",
    "fixed_operator_conformance_overloading",
    "linear_algebra_complex_inner_product_law",
    "caret_power_operator_msp",
    "caret_power_right_associative_math_law",
}
THREE_OUTCOME_FEATURES = {
    "numeric_operator_core",
    "float_alias_float64",
    "uint_default_unsigned_integer_domain",
    "closed_operator_symbols_open_named_extensions",
    "operator_precedence_table_phase_a",
}
TEST_CELLS = {
    (feature_id, "CONFORMANCE_TESTS", outcome)
    for feature_id in TWO_OUTCOME_FEATURES
    for outcome in ("BOUNDARY", "REJECT")
} | {
    (feature_id, "CONFORMANCE_TESTS", outcome)
    for feature_id in THREE_OUTCOME_FEATURES
    for outcome in ("POSITIVE", "BOUNDARY", "REJECT")
}
EXPECTED_CELLS = STRUCTURAL_CELLS | TEST_CELLS

NA_CELLS = {
    ("float_alias_float64", "DYNAMIC_LOWERING", None): (
        "NA_DYNAMIC_ALIAS_NORMALIZES_NO_DISTINCT_RUNTIME_IDENTITY",
        "MIR_RUNTIME_AUTHORITY",
    ),
    ("float_alias_float64", "CONFORMANCE_TESTS", "REJECT"): (
        "NA_TEST_NO_DISTINCT_REJECTION_CLASS",
        "CONFORMANCE_AUTHORITY",
    ),
    ("caret_power_right_associative_math_law", "CONFORMANCE_TESTS", "REJECT"): (
        "NA_TEST_NO_DISTINCT_REJECTION_CLASS",
        "CONFORMANCE_AUTHORITY",
    ),
}
DELEGATED_CELL = (
    "closed_operator_symbols_open_named_extensions",
    "DYNAMIC_LOWERING",
    None,
)
DELEGATE_FEATURE = "fixed_operator_conformance_overloading"

TARGET_COUNT = 469
TARGET_DIGEST = "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435"
EXCLUDED_COUNT = 254
EXCLUDED_DIGEST = "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7"
CANONICAL_BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
LOCAL_PREDECESSOR = "7f540c2c593911ec19003b43ff48652615becfc6"
COUNT_KEYS = {
    "feature_count",
    "evidence_entry_count",
    "binding_count",
    "predecessor_blocked_cell_count",
    "bound_direct_transition_count",
    "bound_delegated_transition_count",
    "not_applicable_transition_count",
    "predecessor_total_blocked_cell_count",
    "post_overlay_total_blocked_cell_count",
    "acceptance_case_count",
}
GUARD_VALUES = {
    "target_feature_count": TARGET_COUNT,
    "target_feature_id_list_sha256": TARGET_DIGEST,
    "excluded_feature_count": EXCLUDED_COUNT,
    "excluded_feature_id_list_sha256": EXCLUDED_DIGEST,
    "feature_statuses": "UNCHANGED",
    "source_activation": "UNCHANGED",
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "m13_actions": "4_OPEN_UNCHANGED",
    "product_lanes": "15_OF_15_NOT_RUN",
    "github_publication": "SUSPENDED",
    "fixed_glyph_operator_count": 13,
    "arbitrary_custom_operator_count": 0,
    "runtime_operator_lookup_count": 0,
    "float_normalizes_to": "Float64",
    "float_distinct_identity_count": 0,
    "uint_mathematical_domain": "0..2^64-1",
    "uint_alias_of_uint64": False,
    "uint_storage_or_abi_identity_selected": False,
    "evidence_level": "E2_STRUCTURED_STATIC",
    "product_execution_receipt_count": 0,
    "implementation_claim": "NOT_RUN",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def contains_registry_id(value: Any, locator: str) -> bool:
    if isinstance(value, dict):
        if locator in value:
            return True
        return any(
            child == locator if isinstance(child, str) else contains_registry_id(child, locator)
            for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_registry_id(child, locator) for child in value)
    return False


def safe_relative(path: str) -> bool:
    candidate = Path(path)
    return (
        bool(path)
        and not candidate.is_absolute()
        and ".." not in candidate.parts
        and "*" not in path
        and "?" not in path
    )


def locator_resolves(root: Path, entry: dict[str, Any]) -> bool:
    relative = entry.get("path", "")
    path = root / relative
    kind = entry.get("locator_kind")
    locator = entry.get("locator", "")
    if not path.exists() or not locator:
        return False
    if kind == "FILE":
        return path.is_file() and locator in {relative, path.name}
    if kind == "JSON_POINTER":
        if not path.is_file():
            return False
        try:
            resolve_json_pointer(load(path), locator)
            return True
        except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
            return False
    if kind != "REGISTRY_ID":
        return False
    candidates = [path] if path.is_file() else sorted(path.rglob("*"))
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            if candidate.suffix.lower() == ".json":
                if contains_registry_id(load(candidate), locator):
                    return True
            else:
                text = candidate.read_text(encoding="utf-8")
                if locator in text:
                    return True
                if re.search(rf"(?m)^\s*{re.escape(locator)}\s*::?=", text):
                    return True
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            continue
    return False


def feature_catalog(root: Path) -> dict[str, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / FEATURE_DIR).glob("part-*.json")):
        rows.extend(load(path))
    return {row["feature_id"]: row for row in rows}


def validate(root: Path, overlay: dict[str, Any], *, validate_schema: bool = False) -> list[str]:
    """Return stable error codes for an overlay candidate."""

    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(set(overlay) == TOP_KEYS, "TOP_LEVEL_EXACT_KEYS")
    require(
        overlay.get("$schema") == "../../../schemas/language/scalar-numeric-fixed-operator-evidence-r1.schema.json",
        "SCHEMA_POINTER",
    )
    require(overlay.get("schema") == "deeplus.scalar-numeric-fixed-operator-evidence/r1", "SCHEMA_ID")
    require(overlay.get("revision") == "r54-local-scalar-numeric-fixed-operator-trace-closure-r1", "REVISION")
    require(overlay.get("canonical_baseline_commit") == CANONICAL_BASELINE, "CANONICAL_BASELINE")
    require(overlay.get("local_predecessor_commit") == LOCAL_PREDECESSOR, "LOCAL_PREDECESSOR")

    if validate_schema:
        schema_path = root / SCHEMA_REL
        require(schema_path.is_file(), "SCHEMA_PATH_EXISTS")
        if schema_path.is_file():
            try:
                import jsonschema  # type: ignore

                jsonschema.Draft202012Validator(load(schema_path)).validate(overlay)
            except ImportError:
                pass
            except Exception:
                require(False, "JSON_SCHEMA")

    require(overlay.get("feature_ids") == FEATURE_IDS, "FEATURE_IDS_EXACT_SORTED_14")
    require(len(set(overlay.get("feature_ids", []))) == 14, "FEATURE_IDS_UNIQUE")
    require(overlay.get("candidate_status") == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY", "CANDIDATE_STATUS")

    catalog = feature_catalog(root)
    for feature_id in FEATURE_IDS:
        row = catalog.get(feature_id)
        require(row is not None, f"CATALOG_FEATURE_EXISTS:{feature_id}")
        if row is not None:
            expected_status = (
                "STABLE_GROUP"
                if feature_id == "numeric_literal_lexical_contract"
                else "STABLE_DESIGN"
            )
            require(row.get("status_enum") == expected_status, f"CATALOG_STATUS_UNCHANGED:{feature_id}")
            require(row.get("source_activation") == "none", f"CATALOG_ACTIVATION_UNCHANGED:{feature_id}")

    entries = overlay.get("evidence_entries", [])
    require(isinstance(entries, list), "EVIDENCE_ENTRIES_ARRAY")
    evidence: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries if isinstance(entries, list) else []):
        require(isinstance(entry, dict) and set(entry) == EVIDENCE_KEYS, f"EVIDENCE_ENTRY_SHAPE:{index}")
        if not isinstance(entry, dict):
            continue
        key = entry.get("evidence_key")
        require(isinstance(key, str) and bool(key), f"EVIDENCE_KEY:{index}")
        if isinstance(key, str):
            require(key not in evidence, f"EVIDENCE_KEY_UNIQUE:{key}")
            evidence[key] = entry
        require(entry.get("locator_kind") in LOCATOR_KINDS, f"EVIDENCE_LOCATOR_KIND:{key}")
        require(isinstance(entry.get("class"), str) and bool(entry.get("class")), f"EVIDENCE_CLASS:{key}")
        require(entry.get("stage_role") in STAGE_ROLES, f"EVIDENCE_STAGE_ROLE:{key}")
        path = entry.get("path", "")
        require(isinstance(path, str) and safe_relative(path), f"EVIDENCE_PATH_SAFE:{key}")
        if isinstance(path, str) and safe_relative(path):
            require(locator_resolves(root, entry), f"EVIDENCE_LOCATOR_RESOLVES:{key}")

    bindings = overlay.get("bindings", [])
    require(isinstance(bindings, list), "BINDINGS_ARRAY")
    by_cell: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for index, binding in enumerate(bindings if isinstance(bindings, list) else []):
        require(isinstance(binding, dict) and set(binding) == BINDING_KEYS, f"BINDING_SHAPE:{index}")
        if not isinstance(binding, dict):
            continue
        cell = (binding.get("feature_id"), binding.get("stage"), binding.get("outcome"))
        require(cell not in by_cell, f"BINDING_CELL_UNIQUE:{cell}")
        by_cell[cell] = binding
        require(binding.get("feature_id") in FEATURE_IDS, f"BINDING_FEATURE:{index}")
        require(binding.get("stage") in STAGES, f"BINDING_STAGE:{index}")
        if binding.get("stage") == "CONFORMANCE_TESTS":
            require(binding.get("outcome") in OUTCOMES, f"BINDING_OUTCOME:{index}")
        else:
            require(binding.get("outcome") is None, f"BINDING_STRUCTURAL_OUTCOME_NULL:{index}")
        disposition = binding.get("disposition")
        require(disposition in DISPOSITIONS, f"BINDING_DISPOSITION:{index}")
        refs = binding.get("evidence_keys")
        require(isinstance(refs, list) and bool(refs), f"BINDING_EVIDENCE_NONEMPTY:{index}")
        if isinstance(refs, list):
            require(len(refs) == len(set(refs)), f"BINDING_EVIDENCE_UNIQUE:{index}")
            require(all(ref in evidence for ref in refs), f"BINDING_EVIDENCE_EXISTS:{index}")
            expected_role = (
                f"CONFORMANCE_TESTS:{binding.get('outcome')}"
                if binding.get("stage") == "CONFORMANCE_TESTS"
                else binding.get("stage")
            )
            require(
                all(evidence.get(ref, {}).get("stage_role") == expected_role for ref in refs),
                f"BINDING_EVIDENCE_STAGE_ROLE:{index}",
            )
        if disposition == "BOUND_DELEGATED":
            require(cell == DELEGATED_CELL, f"DELEGATED_EXACT_CELL:{index}")
            require(binding.get("delegate_feature_id") == DELEGATE_FEATURE, f"DELEGATED_EXACT_TARGET:{index}")
            require(binding.get("not_applicable") is None, f"DELEGATED_NO_NA:{index}")
        elif disposition == "NOT_APPLICABLE":
            require(cell in NA_CELLS, f"NA_EXACT_CELL:{index}")
            detail = binding.get("not_applicable")
            require(isinstance(detail, dict), f"NA_DETAIL:{index}")
            if isinstance(detail, dict):
                require(
                    set(detail) == {
                        "reason_code",
                        "authority_boundary",
                        "rationale",
                        "justification_evidence_keys",
                    },
                    f"NA_DETAIL_SHAPE:{index}",
                )
                expected = NA_CELLS.get(cell)
                if expected is not None:
                    require(detail.get("reason_code") == expected[0], f"NA_REASON:{index}")
                    require(detail.get("authority_boundary") == expected[1], f"NA_AUTHORITY:{index}")
                require(isinstance(detail.get("rationale"), str) and bool(detail.get("rationale")), f"NA_RATIONALE:{index}")
                just = detail.get("justification_evidence_keys")
                require(isinstance(just, list) and bool(just), f"NA_JUSTIFICATION:{index}")
                if isinstance(just, list):
                    require(set(just) == set(refs or []), f"NA_JUSTIFICATION_MATCH:{index}")
            require(binding.get("delegate_feature_id") is None, f"NA_NO_DELEGATE:{index}")
        else:
            require(binding.get("delegate_feature_id") is None, f"DIRECT_NO_DELEGATE:{index}")
            require(binding.get("not_applicable") is None, f"DIRECT_NO_NA:{index}")

    require(set(by_cell) == EXPECTED_CELLS, "BINDINGS_EXACT_40_CELLS")
    require(len(bindings) == 40, "BINDING_COUNT_40")
    require(sum(row.get("disposition") == "BOUND_DIRECT" for row in bindings) == 36, "DIRECT_TRANSITION_COUNT_36")
    require(sum(row.get("disposition") == "BOUND_DELEGATED" for row in bindings) == 1, "DELEGATED_TRANSITION_COUNT_1")
    require(sum(row.get("disposition") == "NOT_APPLICABLE" for row in bindings) == 3, "NA_TRANSITION_COUNT_3")

    cases = overlay.get("acceptance_cases", [])
    require(isinstance(cases, list), "ACCEPTANCE_CASES_ARRAY")
    case_ids: set[str] = set()
    case_cells: set[tuple[str, str]] = set()
    for index, case in enumerate(cases if isinstance(cases, list) else []):
        require(isinstance(case, dict) and set(case) == CASE_KEYS, f"ACCEPTANCE_CASE_SHAPE:{index}")
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id")
        require(isinstance(case_id, str) and bool(case_id), f"ACCEPTANCE_CASE_ID:{index}")
        if isinstance(case_id, str):
            require(case_id not in case_ids, f"ACCEPTANCE_CASE_ID_UNIQUE:{case_id}")
            case_ids.add(case_id)
        feature_id = case.get("feature_id")
        outcome = case.get("outcome")
        require(feature_id in FEATURE_IDS, f"ACCEPTANCE_CASE_FEATURE:{index}")
        require(outcome in OUTCOMES, f"ACCEPTANCE_CASE_OUTCOME:{index}")
        if feature_id in FEATURE_IDS and outcome in OUTCOMES:
            case_cells.add((feature_id, outcome))
        require(isinstance(case.get("source_or_subject"), str) and bool(case.get("source_or_subject")), f"ACCEPTANCE_CASE_SUBJECT:{index}")
        require(isinstance(case.get("expected"), str) and bool(case.get("expected")), f"ACCEPTANCE_CASE_EXPECTED:{index}")
        require(isinstance(case.get("assertions"), dict) and bool(case.get("assertions")), f"ACCEPTANCE_CASE_ASSERTIONS:{index}")
        require(case.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"ACCEPTANCE_CASE_NOT_RUN:{index}")
        if outcome == "REJECT":
            require(case.get("diagnostic_or_null") is not None, f"ACCEPTANCE_CASE_REJECT_DIAGNOSTIC:{index}")

    direct_test_cells = {
        (binding["feature_id"], binding["outcome"])
        for binding in bindings
        if binding.get("stage") == "CONFORMANCE_TESTS"
        and binding.get("disposition") == "BOUND_DIRECT"
    }
    require(direct_test_cells <= case_cells, "ACCEPTANCE_CASE_EXACT_DIRECT_OUTCOME_COVERAGE")

    counts = overlay.get("counts", {})
    require(isinstance(counts, dict), "COUNTS_OBJECT")
    require(isinstance(counts, dict) and set(counts) == COUNT_KEYS, "COUNTS_EXACT_KEYS")
    expected_counts = {
        "feature_count": 14,
        "evidence_entry_count": len(entries),
        "binding_count": 40,
        "predecessor_blocked_cell_count": 40,
        "bound_direct_transition_count": 36,
        "bound_delegated_transition_count": 1,
        "not_applicable_transition_count": 3,
        "predecessor_total_blocked_cell_count": 1381,
        "post_overlay_total_blocked_cell_count": 1341,
        "acceptance_case_count": len(cases),
    }
    for key, expected in expected_counts.items():
        require(counts.get(key) == expected, f"COUNT:{key}")

    guards = overlay.get("guards", {})
    require(isinstance(guards, dict), "GUARDS_OBJECT")
    if isinstance(guards, dict):
        require(set(guards) == set(GUARD_VALUES), "GUARDS_EXACT_KEYS")
        for key, expected in GUARD_VALUES.items():
            require(guards.get(key) == expected, f"GUARD:{key}")

    text = json.dumps(overlay, sort_keys=True)
    require("APPLICABLE_BLOCKED_BY_GAP" not in text, "NO_BLOCKED_DISPOSITION_IN_OVERLAY")
    require("VERIFIED_CLOSED" not in text and "IR-XCUT-P1-054_CLOSED" not in text, "NO_IR_XCUT_CLOSURE_OVERCLAIM")
    require("product_execution\": \"PASS" not in text and "15_OF_15_PASS" not in text, "NO_PRODUCT_PASS_OVERCLAIM")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--overlay", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overlay_path = args.overlay.resolve() if args.overlay else root / OVERLAY_REL
    try:
        overlay = load(overlay_path)
        errors = validate(root, overlay, validate_schema=args.overlay is None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [f"LOAD:{type(exc).__name__}:{exc}"]
        overlay = {}
    print(
        json.dumps(
            {
                "schema": "deeplus.scalar-numeric-fixed-operator-trace-validation-receipt/r1",
                "result": "PASS" if not errors else "FAIL",
                "feature_count": len(overlay.get("feature_ids", [])),
                "binding_count": len(overlay.get("bindings", [])),
                "acceptance_case_count": len(overlay.get("acceptance_cases", [])),
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
