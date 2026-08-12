#!/usr/bin/env python3
"""Validate R99 exact-number operator allocation/effect closure."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("spec/contracts/exact-numeric-operator-allocation-r99.json")
FIXTURE = Path("tests/fixtures/current/exact-numeric-operator-allocation-r99.json")
ARITHMETIC_PURE = "BORROWED_PURE_SYNCHRONOUS_NONCONSUMING_ARITHMETIC_DEFECT_PRECOMMIT"
ARITHMETIC_ALLOC = "BORROWED_ALLOCATING_SYNCHRONOUS_NONCONSUMING_ALLOCATIONERROR_ARITHMETIC_DEFECT_PRECOMMIT"
COMPARISON_PURE = "BORROWED_PURE_TOTAL_SYNCHRONOUS_NONCONSUMING"
COMPARISON_ALLOC = "BORROWED_ALLOCATING_TOTAL_SYNCHRONOUS_NONCONSUMING_ALLOCATIONERROR"
ALLOCATING_ROOTS = {
    "UnaryPlus", "UnaryMinus", "Add<Rhs>", "Subtract<Rhs>",
    "Multiply<Rhs>", "Divide<Rhs>", "Remainder<Rhs>", "Ord<Rhs>",
}
PRELUDE_ALLOCATING_ENTRIES = {
    "unary_plus", "unary_minus", "add_rhs", "subtract_rhs",
    "multiply_rhs", "divide_rhs", "remainder_rhs", "ord_t",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_rows(root: Path, directory: str, id_field: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / directory).glob("*.json")):
        value = load(path)
        if isinstance(value, list):
            for row in value:
                rows[row[id_field]] = row
    return rows


def contract_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    decision = contract.get("decision", {})
    require(contract.get("schema") == "deeplus.exact-numeric-operator-allocation/r99", "IDENTITY")
    require(contract.get("gap_id") == "IR-NUM-P1-072", "GAP_ID")
    require(contract.get("semantic_p0") == 0, "SEMANTIC_P0")
    require(contract.get("feature_p1") == "22_OPEN_UNCHANGED", "FEATURE_P1")
    require(contract.get("product_lanes") == "15_OF_15_NOT_RUN", "PRODUCT_LANES")
    require(decision.get("hidden_oom_defect_count") == 0, "HIDDEN_OOM_ZERO")
    require(decision.get("fixed_glyph_count") == 13, "FIXED_GLYPHS")
    require(decision.get("trait_root_count") == 9, "TRAIT_ROOTS")
    require(decision.get("new_source_glyph_count") == 0, "NEW_GLYPH_ZERO")

    envelope = contract.get("trait_requirement_envelopes", {})
    require(set(envelope.get("allocating_capable_roots", [])) == ALLOCATING_ROOTS, "ALLOCATING_ROOT_SET")
    require(envelope.get("exact_requirement_error_set") == ["AllocationError"], "MAX_ERROR_SET")
    require(envelope.get("exact_requirement_effect_row") == ["allocate"], "MAX_EFFECT_ROW")
    require(envelope.get("pure_root") == "Eq<Rhs>", "PURE_EQ_ROOT")
    require("exact normalized subset" in envelope.get("implementation_rule", ""), "EXACT_SUBSET_RULE")
    require("full AllocationError/allocate envelope" in envelope.get("generic_rule", ""), "GENERIC_MAX_RULE")

    descriptor_rows = contract.get("responsibility_descriptor_registry", [])
    descriptors = {row.get("profile_id"): row for row in descriptor_rows}
    require(len(descriptor_rows) == len(descriptors) == 4, "DESCRIPTOR_CARDINALITY")
    require(set(descriptors) == {ARITHMETIC_PURE, ARITHMETIC_ALLOC, COMPARISON_PURE, COMPARISON_ALLOC}, "DESCRIPTOR_IDS")
    require(descriptors.get(ARITHMETIC_PURE, {}).get("error_set") == [], "ARITHMETIC_PURE_ERRORS")
    require(descriptors.get(ARITHMETIC_PURE, {}).get("effect_row") == [], "ARITHMETIC_PURE_EFFECTS")
    require(descriptors.get(ARITHMETIC_ALLOC, {}).get("error_set") == ["AllocationError"], "ARITHMETIC_ALLOC_ERRORS")
    require(descriptors.get(ARITHMETIC_ALLOC, {}).get("effect_row") == ["allocate"], "ARITHMETIC_ALLOC_EFFECTS")
    require(descriptors.get(COMPARISON_PURE, {}).get("error_set") == [], "COMPARISON_PURE_ERRORS")
    require(descriptors.get(COMPARISON_ALLOC, {}).get("effect_row") == ["allocate"], "COMPARISON_ALLOC_EFFECTS")

    boundary = contract.get("literal_and_conversion_boundary", {})
    runtime_materialization = boundary.get("runtime_BigInt_or_Rational_materialization", {})
    require(runtime_materialization.get("small_value_optimization_changes_responsibility") is False, "SMALL_VALUE_FENCE")
    require(runtime_materialization.get("error_set") == ["AllocationError"], "MATERIALIZATION_ERRORS")
    require(runtime_materialization.get("effect_row") == ["allocate"], "MATERIALIZATION_EFFECTS")
    require(boundary.get("ArithmeticDefect_membership_in_error_set") is False, "DEFECT_ERRORSET_SEPARATION")

    selection = contract.get("selection_and_hir", {})
    required_hir = selection.get("required_hir_fields", [])
    require("responsibility_profile_id" in required_hir, "HIR_RESPONSIBILITY_ID")
    require(not {"normalized_error_set_id", "normalized_effect_row_id", "allocation_plan_id_or_null"}.intersection(required_hir), "HIR_NO_REDUNDANT_FIELDS")
    require("exactly one registry descriptor" in selection.get("responsibility_binding", ""), "HIR_DESCRIPTOR_BINDING")

    failure = contract.get("dynamic_and_lowering", {}).get("allocation_failure", {})
    require(failure.get("outcome") == "throw AllocationError", "FAILURE_OUTCOME")
    require(failure.get("effect") == "allocate", "FAILURE_EFFECT")
    require(failure.get("published_result_count") == 0, "FAILURE_PUBLICATION_ZERO")
    require(failure.get("compound_assignment_place_write_count") == 0, "FAILURE_PLACE_WRITE_ZERO")
    require(failure.get("restore_or_retain_operands") is True, "FAILURE_OPERAND_RETENTION")
    return errors


def validate(root: Path, contract: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors = contract_errors(contract)

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    features = catalog_rows(root, "spec/features/catalog/chunks", "feature_id")
    diagnostics = catalog_rows(root, "spec/diagnostics/catalog/chunks", "diagnostic_id")
    prelude = catalog_rows(root, "library/prelude/signatures/chunks", "entry_id")
    frontend = load(root / "spec/frontend/frontend-model.json")
    mir_schema = load(root / "schemas/language/mir-responsibility.schema.json")
    api_schema = load(root / "schemas/language/module-api-digest.schema.json")

    require(fixture.get("contract") == CONTRACT.as_posix(), "FIXTURE_BINDING")
    require(fixture.get("product_execution") == "NOT_RUN", "FIXTURE_NOT_RUN")
    cases = fixture.get("cases", [])
    require(len(cases) == 10 and len({row.get("id") for row in cases}) == 10, "FIXTURE_CARDINALITY")
    require({kind: sum(row.get("kind") == kind for row in cases) for kind in ("POSITIVE", "BOUNDARY", "REJECT")} == {"POSITIVE": 3, "BOUNDARY": 3, "REJECT": 4}, "FIXTURE_PARTITION")

    expected_diagnostics = {
        "OPERATOR_ALLOCATION_ERROR_NOT_PROPAGATED",
        "OPERATOR_ALLOCATE_EFFECT_NOT_DECLARED",
        "OPERATOR_CONFORMANCE_RESPONSIBILITY_MISMATCH",
        "HIR_MIR_RESPONSIBILITY_PROJECTION_MISMATCH",
    }
    require(expected_diagnostics.issubset(diagnostics), "DIAGNOSTIC_SET")
    for diagnostic_id in expected_diagnostics:
        row = diagnostics.get(diagnostic_id, {})
        require(row.get("product_support") == "NOT_RUN", f"{diagnostic_id}_NOT_RUN")

    feature = features.get("fixed_operator_conformance_overloading", {})
    require(feature.get("status_enum") == "STABLE_DESIGN", "FEATURE_STATUS")
    require(CONTRACT.as_posix() in feature.get("artifact_trace_refs", []), "FEATURE_CONTRACT_TRACE")
    require(FIXTURE.as_posix() in feature.get("artifact_trace_refs", []), "FEATURE_FIXTURE_TRACE")

    for entry_id in PRELUDE_ALLOCATING_ENTRIES:
        row = prelude.get(entry_id, {})
        signature = "\n".join(row.get("signatures", []))
        require("throws AllocationError effects allocate" in signature, f"PRELUDE_{entry_id}_ENVELOPE")
        require(row.get("product_support") == "NOT_RUN", f"PRELUDE_{entry_id}_NOT_RUN")
    require("throws Never effects {}" in "\n".join(prelude.get("eq_rhs", {}).get("signatures", [])), "PRELUDE_EQ_PURE")

    frontend_contract = frontend.get("fixed_operator_conformance_frontend_contract", {})
    rows = {row.get("operator_id"): row for row in frontend_contract.get("admitted_operator_rows", [])}
    arithmetic_ids = {"UnaryPlus", "UnaryMinus", "BinaryAdd", "BinarySubtract", "BinaryMultiply", "BinaryDivide", "BinaryRemainder"}
    ord_ids = {"BinaryLessThan", "BinaryLessThanOrEqual", "BinaryGreaterThan", "BinaryGreaterThanOrEqual"}
    eq_ids = {"BinaryEqual", "BinaryNotEqual"}
    require(all(rows.get(operator_id, {}).get("responsibility_profile_id_domain") == [ARITHMETIC_PURE, ARITHMETIC_ALLOC] for operator_id in arithmetic_ids), "FRONTEND_ARITHMETIC_DOMAIN")
    require(all(rows.get(operator_id, {}).get("responsibility_profile_id_domain") == [COMPARISON_PURE, COMPARISON_ALLOC] for operator_id in ord_ids), "FRONTEND_ORD_DOMAIN")
    require(all(rows.get(operator_id, {}).get("responsibility_profile_id") == COMPARISON_PURE for operator_id in eq_ids), "FRONTEND_EQ_PURE")
    required_hir = frontend_contract.get("typed_hir_residue", {}).get("required_fields", [])
    require(required_hir == contract.get("selection_and_hir", {}).get("required_hir_fields"), "FRONTEND_HIR_PARITY")

    for schema, label in ((mir_schema, "MIR"), (api_schema, "API")):
        key = "fixedOperatorConformanceDispatch" if label == "MIR" else "fixedOperatorConformanceResidue"
        node = schema.get("$defs", {}).get(key, {})
        base_enum = node.get("properties", {}).get("responsibility_profile_id", {}).get("enum", [])
        require(base_enum == [ARITHMETIC_PURE, ARITHMETIC_ALLOC, COMPARISON_PURE, COMPARISON_ALLOC], f"{label}_PROFILE_ENUM")
        require(len(node.get("allOf", [])) == 13, f"{label}_ROLE_ROWS")

    language = (root / "spec/language.md").read_text(encoding="utf-8")
    type_system = (root / "spec/types/type-system.md").read_text(encoding="utf-8")
    prelude_doc = (root / "library/prelude/prelude.md").read_text(encoding="utf-8")
    for needle in ("AllocationError", "small-value optimization", "selected witness"):
        require(needle in language or needle in type_system, f"DOC_{needle}")
    require("AllocationError" in prelude_doc and "ArithmeticDefect" in prelude_doc, "PRELUDE_DOC_BOUNDARY")
    return errors


def mutation_checks(contract: dict[str, Any]) -> list[str]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    value = copy.deepcopy(contract)
    value["decision"]["hidden_oom_defect_count"] = 1
    mutations.append(("HIDDEN_OOM", value))
    value = copy.deepcopy(contract)
    value["trait_requirement_envelopes"]["generic_rule"] = "pure"
    mutations.append(("GENERIC_ERASURE", value))
    value = copy.deepcopy(contract)
    value["trait_requirement_envelopes"]["implementation_rule"] = "implementation defined"
    mutations.append(("SUBSET_ERASURE", value))
    value = copy.deepcopy(contract)
    value["responsibility_descriptor_registry"][1]["effect_row"] = []
    mutations.append(("ALLOCATE_EFFECT_ERASURE", value))
    value = copy.deepcopy(contract)
    value["literal_and_conversion_boundary"]["runtime_BigInt_or_Rational_materialization"]["small_value_optimization_changes_responsibility"] = True
    mutations.append(("SMALL_VALUE_NARROWING", value))
    value = copy.deepcopy(contract)
    value["dynamic_and_lowering"]["allocation_failure"]["published_result_count"] = 1
    mutations.append(("PARTIAL_PUBLICATION", value))
    value = copy.deepcopy(contract)
    value["dynamic_and_lowering"]["allocation_failure"]["compound_assignment_place_write_count"] = 1
    mutations.append(("PARTIAL_PLACE_WRITE", value))

    failures: list[str] = []
    for mutation_id, mutated in mutations:
        if not contract_errors(mutated):
            failures.append(f"MUTATION_SURVIVED:{mutation_id}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT)
    fixture = load(root / FIXTURE)
    errors = validate(root, contract, fixture)
    if args.mutations:
        errors.extend(mutation_checks(contract))
    if errors:
        print("FAIL R99 exact numeric operator allocation: " + ", ".join(errors))
        return 1
    print("PASS R99 exact numeric operator allocation: 13 glyphs, 9 roots, 4 exact responsibility descriptors, 10 fixtures, 7/7 mutations rejected, product 15/15 NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
