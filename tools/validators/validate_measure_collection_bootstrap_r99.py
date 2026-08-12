#!/usr/bin/env python3
"""Validate the R99 measure/collection bootstrap design closure."""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("spec/contracts/measure-collection-bootstrap-r99.json")
FIXTURES = Path("tests/fixtures/current/measure-collection-bootstrap-r99.json")
TARGET_METADATA = Path("spec/traceability/implementation-target-profile-r1/catalog-metadata.json")
TARGET_ROWS = Path("spec/traceability/implementation-target-profile-r1/rows.json")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def feature_rows(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "spec/features/catalog/chunks").glob("*.json")):
        for row in load(path):
            rows[row["feature_id"]] = row
    return rows


def predicate_rows(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "spec/types/predicates/chunks").glob("*.json")):
        for row in load(path):
            rows[row["predicate_id"]] = row
    return rows


def diagnostic_ids(root: Path) -> set[str]:
    ids: set[str] = set()
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("*.json")):
        ids.update(row["diagnostic_id"] for row in load(path))
    return ids


def diagnostic_relations(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "spec/diagnostics/relations/chunks").glob("*.json")):
        rows.extend(load(path))
    return rows


def reduced_positive(pair: list[int]) -> bool:
    return (
        isinstance(pair, list)
        and len(pair) == 2
        and all(isinstance(value, int) for value in pair)
        and pair[0] > 0
        and pair[1] > 0
        and math.gcd(pair[0], pair[1]) == 1
    )


def validate(
    root: Path,
    contract: dict[str, Any],
    fixtures: dict[str, Any],
    relation_override: list[dict[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    features = feature_rows(root)
    predicates = predicate_rows(root)
    diagnostics = diagnostic_ids(root)
    relations = (
        diagnostic_relations(root)
        if relation_override is None
        else relation_override
    )
    language = (root / "spec/language.md").read_text(encoding="utf-8")
    type_system = (root / "spec/types/type-system.md").read_text(encoding="utf-8")
    target_builder = (root / "tools/generators/build_implementation_target_traceability.py").read_text(encoding="utf-8")
    target_metadata = load(root / TARGET_METADATA)
    target_rows = load(root / TARGET_ROWS)
    target_ids = {row.get("feature_id") for row in target_rows}

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(contract.get("schema") == "deeplus.measure-collection-bootstrap/r99", "CONTRACT_IDENTITY")
    require(contract.get("gaps") == ["IR-MEASURE-P1-069", "IR-COLL-P1-070", "IR-MEASURE-P1-071"], "GAP_SET")
    require(contract.get("governance") == {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_execution": "NOT_RUN",
        "github_mutation": "NOT_PERFORMED",
    }, "GOVERNANCE_FENCE")

    exact = contract.get("exact_ratio_conversion", {})
    require(exact.get("canonical_feature_id") == "exact_ratio_unit_conversion_msp", "EXACT_CANONICAL_OWNER")
    require(exact.get("absorbed_alias_feature_id") == "static_exact_unit_conversion_msp", "EXACT_ALIAS_ID")
    require(exact.get("independent_semantic_identity_count_for_alias") == 0, "EXACT_ALIAS_ZERO_IDENTITY")
    ratio = exact.get("reduced_positive_rational", {})
    require("positive nonzero" in ratio.get("denominator", ""), "EXACT_DENOMINATOR_POSITIVE")
    require(exact.get("catalog_closure", {}).get("provider_fallback_count") == 0, "EXACT_PROVIDER_FALLBACK_ZERO")
    require(exact.get("catalog_closure", {}).get("source_order_winner_count") == 0, "EXACT_SOURCE_ORDER_WINNER_ZERO")
    require(exact.get("hir", {}).get("unresolved_field_count_before_seal") == 0, "EXACT_HIR_SEALED")
    witness = exact.get("known_unit_witness_selection", {})
    require(len(witness.get("algorithm", [])) == 5, "KNOWN_WITNESS_FINITE_ALGORITHM")
    require(witness.get("source_order_winner_count") == 0, "KNOWN_WITNESS_SOURCE_ORDER_ZERO")
    require(witness.get("provider_fallback_count") == 0, "KNOWN_WITNESS_PROVIDER_ZERO")
    require("KnownUnitWitnessId" in " ".join(witness.get("algorithm", [])), "KNOWN_WITNESS_HIR_IDENTITY")
    require("Measure<Rep, Dim>" in witness.get("function_boundary_law", ""), "KNOWN_WITNESS_BOUNDARY")
    scalar = exact.get("scalar_operation_plan", {})
    require(scalar.get("identity") == "ScaleByReducedRatio<Rep>", "SCALAR_PLAN_IDENTITY")
    require(set(scalar.get("matrix", {})) == {"Rational", "integral", "Float32_or_Float64", "other_Rep"}, "SCALAR_PLAN_MATRIX")
    require(scalar.get("implicit_representation_promotion_count") == 0, "SCALAR_PLAN_PROMOTION_ZERO")
    require(scalar.get("implicit_rounding_policy_count") == 0, "SCALAR_PLAN_ROUNDING_ZERO")
    require(scalar.get("silent_truncation_count") == 0, "SCALAR_PLAN_TRUNCATION_ZERO")

    canonical = features.get("exact_ratio_unit_conversion_msp", {})
    alias = features.get("static_exact_unit_conversion_msp", {})
    require(canonical.get("status_enum") == "STABLE_DESIGN" and canonical.get("feature_kind") == "canonical_feature", "EXACT_FEATURE_STATUS")
    require(CONTRACT.as_posix() in canonical.get("artifact_trace_refs", []), "EXACT_FEATURE_CONTRACT_TRACE")
    require(alias.get("status_enum") == "ABSORBED_ALIAS" and alias.get("feature_kind") == "absorbed_alias", "EXACT_ALIAS_STATUS")
    require(alias.get("source_activation") == "nonactivatable" and alias.get("replaced_by") == ["exact_ratio_unit_conversion_msp"], "EXACT_ALIAS_REPLACEMENT")

    for predicate_id in ("ExactRatioUnitConversionAdmitted", "UnitCatalogExactRatioAdmitted"):
        row = predicates.get(predicate_id, {})
        require(row.get("predicate_maturity") == "design_algorithm", f"{predicate_id}_MATURITY")
        require(row.get("emission_eligible") is True, f"{predicate_id}_EMISSION")
        require(len(row.get("decision_procedure", [])) >= 6, f"{predicate_id}_PROCEDURE")
    known = predicates.get("HasKnownUnitWitness", {})
    require(known.get("predicate_maturity") == "design_algorithm", "KNOWN_WITNESS_PREDICATE_MATURITY")
    require(known.get("emission_eligible") is True, "KNOWN_WITNESS_PREDICATE_EMISSION")
    require(len(known.get("decision_procedure", [])) == 6, "KNOWN_WITNESS_PREDICATE_PROCEDURE")

    affine = contract.get("affine_units", {})
    require(affine.get("implementation_target_disposition") == "EXPLICITLY_DEFERRED_TARGET_EXCLUDED", "AFFINE_EXCLUSION")
    require(affine.get("current_source_admission") == "REJECT", "AFFINE_CURRENT_REJECT")
    require("affine_unit_profile_msp" in target_builder and "EXPLICITLY_DEFERRED_TARGET_EXCLUDED" in target_builder, "AFFINE_TARGET_BUILDER_FENCE")
    require("affine_unit_profile_msp" not in target_ids, "AFFINE_TARGET_ROW_ABSENT")

    generator = contract.get("shaped_generator_boundary", {})
    source = generator.get("source_contract", {})
    require(generator.get("language_dependency_edge_count_from_shaped_initializer_to_profile") == 0, "GENERATOR_DEPENDENCY_ZERO")
    require(generator.get("provider_availability_changes_checker_result_count") == 0, "GENERATOR_PROVIDER_RESULT_ZERO")
    require(source.get("provider_lookup_count") == 0 and source.get("hidden_clone_or_default_count") == 0, "GENERATOR_HIDDEN_ACTION_ZERO")
    require("zero when cardinality == 0" in source.get("generator_expression_evaluation_count", ""), "GENERATOR_ZERO_SHAPE_EVAL")
    require("arbitrary_generator_stdlib_profile" in target_builder and "EXPLICITLY_DEFERRED_TARGET_EXCLUDED_OPTIONAL_PROVIDER" in target_builder, "GENERATOR_TARGET_BUILDER_FENCE")
    require("arbitrary_generator_stdlib_profile" not in target_ids, "GENERATOR_TARGET_ROW_ABSENT")
    require("shaped_generator_initializer_msp" in target_ids, "SHAPED_GENERATOR_TARGET_ROW_PRESENT")
    metadata_exclusions = target_metadata.get("excluded_current_feature_reasons", {})
    require(metadata_exclusions.get("affine_unit_profile_msp", {}).get("action_id") == "IR-MEASURE-P1-069", "AFFINE_EXCLUSION_ACTION")
    require(metadata_exclusions.get("arbitrary_generator_stdlib_profile", {}).get("action_id") == "IR-COLL-P1-070", "GENERATOR_EXCLUSION_ACTION")
    shaped = features.get("shaped_generator_initializer_msp", {})
    require("arbitrary_generator_stdlib_profile" not in shaped.get("depends_on", []), "GENERATOR_FEATURE_DEPENDENCY_ZERO")
    require(CONTRACT.as_posix() in shaped.get("artifact_trace_refs", []), "GENERATOR_FEATURE_CONTRACT_TRACE")

    expected_diagnostics = {
        "AFFINE_UNIT_NOT_IN_PHASE_A",
        "UNIT_CONVERSION_EXACT_RATIO_FORM_REQUIRED",
        "DIMENSION_MISMATCH",
        "MIXED_UNIT_ADDITION_REQUIRES_DISPLAY_UNIT_DECISION",
        "FILL_REPEAT_ADMISSIBILITY_FAILED",
        "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
        "UNIT_CONVERSION_SCALAR_PLAN_REQUIRED",
        "UNIT_CONVERSION_INTEGRAL_RESULT_REQUIRED",
    }
    require(expected_diagnostics <= diagnostics, "DIAGNOSTIC_SET")
    exact_ratio_relations = [
        row
        for row in relations
        if row.get("predicate_id") == "ExactRatioUnitConversionAdmitted"
    ]
    require(
        exact_ratio_relations
        == [
            {
                "violation_id": "ExactRatioUnitConversionAdmitted:default",
                "predicate_id": "ExactRatioUnitConversionAdmitted",
                "diagnostic_id": "UNIT_CONVERSION_EXACT_RATIO_FORM_REQUIRED",
                "relation": "primary",
            },
            {
                "violation_id": None,
                "predicate_id": "ExactRatioUnitConversionAdmitted",
                "diagnostic_id": "UNIT_CONVERSION_INTEGRAL_RESULT_REQUIRED",
                "relation": "secondary",
            },
            {
                "violation_id": None,
                "predicate_id": "ExactRatioUnitConversionAdmitted",
                "diagnostic_id": "UNIT_CONVERSION_SCALAR_PLAN_REQUIRED",
                "relation": "secondary",
            },
        ],
        "EXACT_RATIO_DIAGNOSTIC_RELATION_BINDING",
    )

    cases = fixtures.get("cases", [])
    require(len(cases) == 13 and len({case.get("id") for case in cases}) == 13, "FIXTURE_EXACT_13")
    require({case.get("class") for case in cases} == {"positive", "boundary", "reject"}, "FIXTURE_CLASS_COVERAGE")
    for case in cases:
        if case.get("operation") == "EXACT_RATIO_CONVERSION" and case.get("expected") == "ADMIT":
            source_scale = case.get("source_scale")
            target_scale = case.get("target_scale")
            require(isinstance(source_scale, list) and isinstance(target_scale, list), f"{case.get('id')}_SCALE_SHAPE")
            if isinstance(source_scale, list) and isinstance(target_scale, list):
                n = source_scale[0] * target_scale[1]
                d = source_scale[1] * target_scale[0]
                divisor = math.gcd(n, d)
                require([n // divisor, d // divisor] == case.get("expected_ratio"), f"{case.get('id')}_RATIO")
                require(reduced_positive(case.get("expected_ratio")), f"{case.get('id')}_REDUCED")
        if case.get("operation", "").startswith("SHAPED_GENERATOR"):
            require(case.get("provider_lookups") in (0, 1), f"{case.get('id')}_PROVIDER_COUNT")
    case_map = {case.get("id"): case for case in cases}
    require(case_map.get("R99-MEASURE-POS-009", {}).get("expected_hir") == ["KnownUnitWitnessId", "UnitCatalogId", "UnitId", "DimensionId", "RepTypeId"], "KNOWN_WITNESS_POSITIVE")
    require(case_map.get("R99-MEASURE-BOUNDARY-010", {}).get("preserved_display_unit_id") is None, "KNOWN_WITNESS_BOUNDARY_LOSS")
    require(case_map.get("R99-MEASURE-REJECT-011", {}).get("diagnostic") == "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS", "KNOWN_WITNESS_REJECT")
    require(case_map.get("R99-MEASURE-REJECT-012", {}).get("diagnostic") == "UNIT_CONVERSION_INTEGRAL_RESULT_REQUIRED", "SCALAR_PLAN_INTEGRAL_REJECT")
    require(case_map.get("R99-MEASURE-REJECT-013", {}).get("diagnostic") == "UNIT_CONVERSION_SCALAR_PLAN_REQUIRED", "SCALAR_PLAN_ROUNDING_REJECT")

    for text, code in (
        ("UnitConversionPlanV1", "LANGUAGE_EXACT_PLAN"),
        ("AFFINE_UNIT_NOT_IN_PHASE_A", "LANGUAGE_AFFINE_FENCE"),
        ("provider availability", "LANGUAGE_GENERATOR_PROVIDER_FENCE"),
        ("ScaleByReducedRatio<Rep>", "LANGUAGE_SCALAR_PLAN"),
    ):
        require(text in language, code)
    require("ReducedPositiveRational" in type_system and "zero-cardinality" in type_system and "KnownUnitWitnessId" in type_system, "TYPE_SYSTEM_R99_MEASURE_COLLECTION")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT)
    fixtures = load(root / FIXTURES)
    errors = validate(root, contract, fixtures)
    mutations: list[dict[str, Any]] = []
    if args.mutations and not errors:
        recipes = [
            ("ALIAS_BECOMES_INDEPENDENT", lambda c: c["exact_ratio_conversion"].__setitem__("independent_semantic_identity_count_for_alias", 1)),
            ("PROVIDER_FALLBACK_ENABLED", lambda c: c["exact_ratio_conversion"]["catalog_closure"].__setitem__("provider_fallback_count", 1)),
            ("AFFINE_TARGET_INCLUDED", lambda c: c["affine_units"].__setitem__("implementation_target_disposition", "TARGET_INCLUDED")),
            ("GENERATOR_PROVIDER_DEPENDENCY", lambda c: c["shaped_generator_boundary"].__setitem__("language_dependency_edge_count_from_shaped_initializer_to_profile", 1)),
            ("GENERATOR_ZERO_SHAPE_EVALUATED", lambda c: c["shaped_generator_boundary"]["source_contract"].__setitem__("generator_expression_evaluation_count", "exactly one")),
            ("KNOWN_WITNESS_PROVIDER_FALLBACK", lambda c: c["exact_ratio_conversion"]["known_unit_witness_selection"].__setitem__("provider_fallback_count", 1)),
            ("SCALAR_IMPLICIT_ROUNDING", lambda c: c["exact_ratio_conversion"]["scalar_operation_plan"].__setitem__("implicit_rounding_policy_count", 1)),
        ]
        for mutation_id, mutate in recipes:
            candidate = copy.deepcopy(contract)
            mutate(candidate)
            rejected = bool(validate(root, candidate, fixtures))
            mutations.append({"mutation_id": mutation_id, "rejected": rejected})
            if not rejected:
                errors.append(f"MUTATION_NOT_REJECTED:{mutation_id}")
        relation_candidate = [
            row
            for row in diagnostic_relations(root)
            if not (
                row.get("predicate_id") == "ExactRatioUnitConversionAdmitted"
                and row.get("diagnostic_id")
                == "UNIT_CONVERSION_SCALAR_PLAN_REQUIRED"
            )
        ]
        relation_rejected = bool(
            validate(root, contract, fixtures, relation_candidate)
        )
        mutations.append(
            {
                "mutation_id": "SCALAR_DIAGNOSTIC_RELATION_OMITTED",
                "rejected": relation_rejected,
            }
        )
        if not relation_rejected:
            errors.append(
                "MUTATION_NOT_REJECTED:SCALAR_DIAGNOSTIC_RELATION_OMITTED"
            )

    receipt = {
        "schema": "deeplus.measure-collection-bootstrap-validation/r99",
        "result": "PASS" if not errors else "FAIL",
        "gaps": contract.get("gaps"),
        "fixture_count": len(fixtures.get("cases", [])),
        "mutations": mutations,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
