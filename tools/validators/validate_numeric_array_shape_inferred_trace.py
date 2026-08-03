#!/usr/bin/env python3
"""Validate the bounded R56 shape-inferred NumericArray contract and trace overlay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/numeric-array-shape-inferred-evidence-r1.schema.json"
CONTRACT_REL = "spec/contracts/numeric-array-shape-inferred-literal-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/numeric-array-shape-inferred-literal-r1.schema.json"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "f4e194d414a024b1fbf93549cdbe3d0cc59fb810"
FEATURES = sorted([
    "numeric_array_shape_inferred_column_vector_semicolon_msp",
    "numeric_array_shape_inferred_value_literal",
    "numeric_array_vector_orientation_witness_msp",
])
EXPECTED_CELLS = {
    (feature, "DYNAMIC_LOWERING", None) for feature in FEATURES
} | {
    ("numeric_array_shape_inferred_value_literal", "CONFORMANCE_TESTS", outcome)
    for outcome in ("POSITIVE", "BOUNDARY", "REJECT")
} | {
    (feature, "CONFORMANCE_TESTS", outcome)
    for feature in (
        "numeric_array_shape_inferred_column_vector_semicolon_msp",
        "numeric_array_vector_orientation_witness_msp",
    )
    for outcome in ("BOUNDARY", "REJECT")
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def contains_scalar(value: Any, expected: str) -> bool:
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(contains_scalar(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(contains_scalar(item, expected) for item in value)
    return False


def locator_resolves(root: Path, contract: dict[str, Any], entry: dict[str, Any]) -> bool:
    path = root / entry["path"]
    if not path.is_file():
        return False
    if entry["path"] == CONTRACT_REL:
        value = contract
    else:
        value = load(path) if path.suffix == ".json" else path.read_text(encoding="utf-8")
    if entry["locator_kind"] == "JSON_POINTER":
        try:
            resolve_pointer(value, entry["locator"])
            return True
        except (KeyError, IndexError, TypeError, ValueError):
            return False
    if entry["locator_kind"] == "REGISTRY_ID":
        return contains_scalar(value, entry["locator"])
    return False


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    validate_schema: bool,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    if validate_schema:
        try:
            import jsonschema
            jsonschema.Draft202012Validator(load(root / OVERLAY_SCHEMA_REL)).validate(overlay)
            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"JSON_SCHEMA:{exc}")

    require(overlay.get("canonical_baseline_commit") == BASELINE, "OVERLAY_BASELINE")
    require(overlay.get("local_predecessor_commit") == PREDECESSOR, "OVERLAY_PREDECESSOR")
    require(contract.get("canonical_baseline_commit") == BASELINE, "CONTRACT_BASELINE")
    require(contract.get("local_predecessor_commit") == PREDECESSOR, "CONTRACT_PREDECESSOR")
    require(overlay.get("feature_ids") == FEATURES, "OVERLAY_FEATURES_EXACT")
    require(contract.get("feature_ids") == FEATURES, "CONTRACT_FEATURES_EXACT")
    require(contract.get("language_status") == "STABLE_DESIGN", "CONTRACT_STABLE_DESIGN")
    require(contract.get("source_activation") == "none", "CONTRACT_ACTIVATION_NONE")
    require(contract.get("current_binding") is False, "CONTRACT_CURRENT_BINDING_FALSE")
    forms = contract.get("syntax_contract", {}).get("forms", [])
    require(
        forms == [
            {
                "form_id": "ROW_COMMA",
                "production_id": "ShapeInferredArrayLiteral",
                "surface": "#[e1, e2, ..., eN]",
                "separator": ",",
                "minimum_element_count": 1,
                "rank": 1,
                "shape_expression": "[N]",
                "orientation": "ROW",
            },
            {
                "form_id": "COLUMN_SEMICOLON",
                "production_id": "ShapeInferredColumnVectorLiteral",
                "surface": "#[e1; e2; ...; eN]",
                "separator": ";",
                "minimum_element_count": 2,
                "rank": 1,
                "shape_expression": "[N]",
                "orientation": "COLUMN",
            },
        ],
        "CONTRACT_FORMS_EXACT",
    )
    static_semantics = contract.get("static_semantics", {})
    require(static_semantics.get("row_result") == "NumericArray<Element, rank=1, shape=[N], orientation=ROW>", "CONTRACT_ROW_RESULT")
    require(static_semantics.get("column_result") == "NumericArray<Element, rank=1, shape=[N], orientation=COLUMN>", "CONTRACT_COLUMN_RESULT")
    require(static_semantics.get("exact_rank_two_nonidentity") is True, "CONTRACT_RANK2_DISTINCT")
    require(static_semantics.get("implicit_broadcast_count") == 0, "CONTRACT_NO_BROADCAST")
    require(static_semantics.get("runtime_shape_inference_count") == 0, "CONTRACT_NO_RUNTIME_INFERENCE")

    entries = overlay.get("evidence_entries", [])
    by_key = {entry.get("evidence_key"): entry for entry in entries}
    require(len(entries) == 10 and len(by_key) == 10, "EVIDENCE_EXACT_UNIQUE_10")
    for key, entry in by_key.items():
        require(isinstance(key, str) and key.startswith("R56:"), f"EVIDENCE_KEY:{key}")
        require(locator_resolves(root, contract, entry), f"EVIDENCE_LOCATOR:{key}")

    bindings = overlay.get("bindings", [])
    by_cell = {
        (item.get("feature_id"), item.get("stage"), item.get("outcome")): item
        for item in bindings
    }
    require(len(bindings) == 10 and len(by_cell) == 10, "BINDINGS_EXACT_UNIQUE_10")
    require(set(by_cell) == EXPECTED_CELLS, "BINDING_CELLS_EXACT")
    for cell, item in by_cell.items():
        require(item.get("disposition") == "BOUND_DIRECT", f"BINDING_DIRECT:{cell}")
        require(item.get("delegate_feature_id") is None, f"BINDING_NO_DELEGATE:{cell}")
        require(item.get("not_applicable") is None, f"BINDING_NO_NA:{cell}")
        refs = item.get("evidence_keys", [])
        require(len(refs) == 1 and refs[0] in by_key, f"BINDING_ONE_EVIDENCE:{cell}")

    cases = overlay.get("acceptance_cases", [])
    require(len(cases) == 7, "TRACE_CASE_COUNT_7")
    for case in cases:
        require(case.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"TRACE_CASE_NOT_RUN:{case.get('case_id')}")
        pointer = case.get("contract_pointer", "")
        try:
            target = resolve_pointer(contract, pointer)
        except (KeyError, IndexError, TypeError, ValueError):
            require(False, f"TRACE_CASE_POINTER:{case.get('case_id')}")
            continue
        require(target.get("feature_id") == case.get("feature_id"), f"TRACE_CASE_FEATURE:{case.get('case_id')}")
        require(target.get("class") == case.get("outcome"), f"TRACE_CASE_OUTCOME:{case.get('case_id')}")

    catalog_rows = all_rows(root, "spec/features/catalog/chunks")
    catalog = {row["feature_id"]: row for row in catalog_rows}
    target = catalog["numeric_array_shape_inferred_value_literal"]
    column = catalog["numeric_array_shape_inferred_column_vector_semicolon_msp"]
    require(target.get("depends_on") == ["numeric_array_sharp_shape_literal_msp", "numeric_array_vector_orientation_witness_msp"], "TARGET_DEPENDENCIES_EXACT")
    require(column.get("depends_on") == ["numeric_array_shape_inferred_value_literal", "numeric_array_vector_orientation_witness_msp"], "COLUMN_DEPENDENCIES_EXACT")
    require("NumericArrayShapeInferredLiteral" not in target.get("notes", ""), "TARGET_OWNER_TYPO_REMOVED")
    require("ShapeInferredArrayLiteral" in target.get("notes", ""), "TARGET_OWNER_CANONICAL")
    trace = target.get("normative_trace_refs", {})
    require(trace.get("productions") == ["ShapeInferredArrayLiteral"], "TARGET_PRODUCTION_EXACT")
    require(trace.get("predicates") == ["NumericArrayElementAdmitted"], "TARGET_PREDICATE_EXACT")
    require("NUMARR_ELEMENT_TYPE_MISMATCH" in trace.get("diagnostics", []), "TARGET_DIAGNOSTIC_NEW_BOUND")

    dependency_rows = all_rows(root, "spec/features/dependencies/chunks")
    edges = {
        (row["source_feature_id"], row["target_feature_id"])
        for row in dependency_rows
    }
    expected_edges = {
        ("numeric_array_shape_inferred_value_literal", "numeric_array_sharp_shape_literal_msp"),
        ("numeric_array_shape_inferred_value_literal", "numeric_array_vector_orientation_witness_msp"),
        ("numeric_array_shape_inferred_column_vector_semicolon_msp", "numeric_array_shape_inferred_value_literal"),
        ("numeric_array_shape_inferred_column_vector_semicolon_msp", "numeric_array_vector_orientation_witness_msp"),
    }
    require(expected_edges <= edges, "DEPENDENCY_EDGES_PRESENT")
    require(("numeric_array_shape_inferred_column_vector_semicolon_msp", "shaped_literal_separator_rank_law") not in edges, "COLUMN_EXACT_SHAPE_EDGE_REMOVED")

    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    require('ShapeInferredArrayLiteral ::= "#" "[" Expr ("," Expr)* ","? "]" ;' in grammar, "GRAMMAR_NONEMPTY_ROW")
    require('ShapeInferredArrayLiteral ::= "#" "[" ExpressionList? "]" ;' not in grammar, "GRAMMAR_EMPTY_REMOVED")
    frontend = load(root / "spec/frontend/frontend-model.json")
    require(not contains_scalar(frontend, "#dims["), "FRONTEND_DIMS_ALIAS_REMOVED")
    require(contains_scalar(frontend, "#StaticDimensionList["), "FRONTEND_EXACT_SHAPE_OWNER")

    diagnostics = {row["diagnostic_id"]: row for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    mismatch = diagnostics.get("NUMARR_ELEMENT_TYPE_MISMATCH")
    require(mismatch is not None, "DIAGNOSTIC_MISMATCH_EXISTS")
    if mismatch:
        require(mismatch.get("diagnostic_status") == "active", "DIAGNOSTIC_MISMATCH_ACTIVE")
        require(mismatch.get("product_support") == "NOT_RUN", "DIAGNOSTIC_MISMATCH_NOT_RUN")
        require("numeric_array_shape_inferred_value_literal" in mismatch.get("feature_refs", []), "DIAGNOSTIC_MISMATCH_TARGET")
    orientation_diag = diagnostics.get("COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED", {})
    require("rank-1" in orientation_diag.get("message", "") and "COLUMN" in orientation_diag.get("message", ""), "COLUMN_DIAGNOSTIC_RANK1")

    predicate_rows = {row["predicate_id"]: row for row in all_rows(root, "spec/types/predicates/chunks")}
    for predicate_id in (
        "ColumnVectorSemicolonGateAdmitted",
        "ColumnVectorSemicolonOrientationAdmitted",
        "NumericArrayElementAdmitted",
    ):
        row = predicate_rows[predicate_id]
        require(row.get("predicate_maturity") == "design_algorithm", f"PREDICATE_ALGORITHM:{predicate_id}")
        require(row.get("emission_eligible") is True, f"PREDICATE_EMISSION:{predicate_id}")
        require(row.get("product_support") == "NOT_RUN", f"PREDICATE_NOT_RUN:{predicate_id}")
        require(row.get("execution_receipt") is None, f"PREDICATE_NO_RECEIPT:{predicate_id}")
        require(row.get("predicate_maturity") != "design_seed", f"PREDICATE_NO_SEED_MATURITY:{predicate_id}")
        require("design seed" not in row.get("summary", "").lower(), f"PREDICATE_NO_SEED_SUMMARY:{predicate_id}")
        require(row.get("design_seed_diagnostic_refs") == [], f"PREDICATE_NO_SEED_DIAGNOSTICS:{predicate_id}")

    relation_rows = all_rows(root, "spec/diagnostics/relations/chunks")
    relations_by_predicate = {
        predicate_id: [row for row in relation_rows if row.get("predicate_id") == predicate_id]
        for predicate_id in (
            "ColumnVectorSemicolonGateAdmitted",
            "ColumnVectorSemicolonOrientationAdmitted",
            "NumericArrayElementAdmitted",
        )
    }
    expected_relation_sets = {
        "ColumnVectorSemicolonGateAdmitted": {
            "SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN",
            "NUMARR_EXPECTED_SHAPE_MISMATCH",
            "COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED",
            "NUMARR_ELEMENT_NOT_NUMERIC",
            "NUMARR_ELEMENT_NOT_PLAIN_NUMERIC",
            "NUMARR_ELEMENT_TYPE_MISMATCH",
            "NUMARR_LITERAL_ELEMENT_OUT_OF_RANGE",
        },
        "ColumnVectorSemicolonOrientationAdmitted": {
            "COLUMN_VECTOR_SEMICOLON_ORIENTATION_LAW_REQUIRED",
            "SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN",
            "NUMARR_EXPECTED_SHAPE_MISMATCH",
        },
        "NumericArrayElementAdmitted": {
            "SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN",
            "NUMARR_ELEMENT_NOT_NUMERIC",
            "NUMARR_ELEMENT_NOT_PLAIN_NUMERIC",
            "NUMARR_ELEMENT_TYPE_MISMATCH",
            "NUMARR_LITERAL_ELEMENT_OUT_OF_RANGE",
        },
    }
    for predicate_id, expected_ids in expected_relation_sets.items():
        rows = relations_by_predicate[predicate_id]
        observed_ids = {row.get("diagnostic_id") for row in rows}
        require(observed_ids == expected_ids and len(rows) == len(expected_ids), f"RELATION_SET_EXACT:{predicate_id}")
        primary_ids = {row.get("diagnostic_id") for row in rows if row.get("relation") == "primary"}
        require(primary_ids == {predicate_rows[predicate_id]["active_primary_diagnostic"]}, f"RELATION_PRIMARY_EXACT:{predicate_id}")

    rules = {row["rule_id"]: row for row in contract.get("rules", [])}
    require(len(rules) == 14, "CONTRACT_RULES_EXACT_14")
    require(contract.get("lowering_contract", {}).get("element_evaluation_order") == "SOURCE_LEFT_TO_RIGHT", "LOWERING_LEFT_TO_RIGHT")
    require(contract.get("lowering_contract", {}).get("element_evaluation_count_each") == 1, "LOWERING_ONCE")
    assembly = contract.get("lowering_contract", {}).get("assembly", {})
    require(assembly.get("operation_kind") == "AGGREGATE_ASSEMBLE", "LOWERING_AGGREGATE_ASSEMBLE")
    require(assembly.get("semantic_operation_id") == "DM-SEMOP-AGGREGATE-ASSEMBLE-R1", "LOWERING_SEMANTIC_OPERATION")
    require(contract.get("lowering_contract", {}).get("new_mir_operation_kind_count") == 0, "LOWERING_NO_NEW_MIR_OP")
    require(contract.get("lowering_contract", {}).get("publication", {}).get("partial_publish_count") == 0, "LOWERING_NO_PARTIAL_PUBLISH")
    require(contract.get("machine_acceptance", {}).get("feature_count") == 3, "CONTRACT_FEATURE_COUNT_3")
    require(contract.get("machine_acceptance", {}).get("semantic_p0") == 0, "CONTRACT_P0_ZERO")
    require(contract.get("machine_acceptance", {}).get("feature_p1") == "22_OPEN_UNCHANGED", "CONTRACT_P1_UNCHANGED")
    require(contract.get("machine_acceptance", {}).get("m13_actions") == "4_OPEN_UNCHANGED", "CONTRACT_M13_UNCHANGED")
    require(contract.get("machine_acceptance", {}).get("product_lanes") == "15_OF_15_NOT_RUN", "CONTRACT_PRODUCT_NOT_RUN")
    require(contract.get("machine_acceptance", {}).get("github_publication") == "SUSPENDED", "CONTRACT_GITHUB_SUSPENDED")
    contract_cases = {case.get("case_id"): case for case in contract.get("acceptance_cases", [])}
    require(len(contract_cases) == 11, "CONTRACT_ACCEPTANCE_CASES_EXACT_11")
    empty_case = contract_cases.get("NASIL-AC-TARGET-REJECT-001", {})
    require(empty_case.get("source_or_subject") == "let empty = #[]", "CONTRACT_EMPTY_CASE_SOURCE")
    require(empty_case.get("diagnostic_or_null") == "SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN", "CONTRACT_EMPTY_CASE_DIAGNOSTIC")
    mismatch_case = contract_cases.get("NASIL-AC-TARGET-REJECT-002", {})
    require(mismatch_case.get("source_or_subject") == "let mixed = #[1, 2.0]", "CONTRACT_MISMATCH_CASE_SOURCE")
    require(mismatch_case.get("diagnostic_or_null") == "NUMARR_ELEMENT_TYPE_MISMATCH", "CONTRACT_MISMATCH_CASE_DIAGNOSTIC")

    fixtures = {row["fixture_id"]: row for row in all_rows(root, "tests/conformance/checker-predicates/chunks")}
    gate_negative = fixtures["PF-ColumnVectorSemicolonGateAdmitted-NEG"]
    require(gate_negative.get("expected_primary_diagnostic") == "SHARP_SHAPE_LITERAL_EMPTY_FORBIDDEN", "FIXTURE_EMPTY_DIAGNOSTIC")
    element_negative = fixtures["PF-NumericArrayElementAdmitted-NEG"]
    require(element_negative.get("expected_primary_diagnostic") == "NUMARR_ELEMENT_TYPE_MISMATCH", "FIXTURE_MISMATCH_DIAGNOSTIC")
    require(element_negative.get("descriptor", {}).get("call_shape", {}).get("surface") == "#[1, 2.0]", "FIXTURE_MISMATCH_SOURCE")
    for fixture_id in (
        "PF-ColumnVectorSemicolonGateAdmitted-POS",
        "PF-ColumnVectorSemicolonOrientationAdmitted-NEG",
        "PF-ColumnVectorSemicolonOrientationAdmitted-POS",
        "PF-NumericArrayElementAdmitted-NEG",
        "PF-NumericArrayElementAdmitted-POS",
    ):
        orientation = fixtures[fixture_id].get("descriptor", {}).get("orientation")
        require(orientation in {"ROW", "COLUMN"}, f"FIXTURE_ORIENTATION:{fixture_id}")

    counts = overlay.get("counts", {})
    require(counts.get("predecessor_total_blocked_cell_count") == 1303, "COUNT_PRE_BLOCKED_1303")
    require(counts.get("post_overlay_total_blocked_cell_count") == 1291, "COUNT_POST_BLOCKED_1291")
    require(counts.get("catalog_direct_transition_count") == 2, "COUNT_CATALOG_DIRECT_2")
    guards = overlay.get("guards", {})
    require(guards.get("semantic_p0") == 0, "GUARD_P0_ZERO")
    require(guards.get("feature_p1") == "22_OPEN_UNCHANGED", "GUARD_P1_UNCHANGED")
    require(guards.get("m13_actions") == "4_OPEN_UNCHANGED", "GUARD_M13_UNCHANGED")
    require(guards.get("product_lanes") == "15_OF_15_NOT_RUN", "GUARD_PRODUCT_NOT_RUN")
    require(guards.get("github_publication") == "SUSPENDED", "GUARD_GITHUB_SUSPENDED")
    text = json.dumps({"overlay": overlay, "contract": contract})
    require("BOUND_DELEGATED" not in text, "NO_DELEGATED_BINDING")
    require("APPLICABLE_BLOCKED_BY_GAP" not in text, "NO_BLOCKED_DISPOSITION")
    require("15_OF_15_PASS" not in text, "NO_PRODUCT_OVERCLAIM")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overlay_path = args.overlay.resolve() if args.overlay else root / OVERLAY_REL
    contract_path = args.contract.resolve() if args.contract else root / CONTRACT_REL
    try:
        overlay = load(overlay_path)
        contract = load(contract_path)
        errors = validate(root, overlay, contract, args.overlay is None and args.contract is None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        overlay = {}
        contract = {}
        errors = [f"LOAD:{type(exc).__name__}:{exc}"]
    print(json.dumps({
        "schema": "deeplus.numeric-array-shape-inferred-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_count": len(overlay.get("feature_ids", [])),
        "binding_count": len(overlay.get("bindings", [])),
        "acceptance_case_count": len(overlay.get("acceptance_cases", [])),
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
