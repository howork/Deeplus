#!/usr/bin/env python3
"""Validate the bounded OrdinaryCallSelectionV1 design closure."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/ordinary-call-selection-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/ordinary-call-selection-v1.schema.json"
INPUT_SCHEMA_REL = "schemas/language/ordinary-call-selection-input-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/ordinary-call-selection-v1.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
HIR_REL = "schemas/language/canonical-hir-h1.schema.json"
LANGUAGE_REL = "spec/language.md"
TYPE_REL = "spec/types/type-system.md"
MIR_REL = "spec/mir/semantics.md"
DECISION_REL = "decisions/language/Design_Deeplus_Ordinary_Call_Selection_Closure_R1.md"
REFERENCE_REL = "docs/grammar-reference/17-name-resolution-type-inference-and-calls.md"
GENERIC_REFERENCE_REL = "docs/grammar-reference/04-types-generics-and-refinement.md"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def chunk_rows(root: Path, pattern: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob(pattern)):
        value = load(path)
        if isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))
    return rows


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = copy.deepcopy(contract_override) if contract_override is not None else load(root / CONTRACT_REL)
    fixture = copy.deepcopy(fixture_override) if fixture_override is not None else load(root / FIXTURE_REL)
    contract_schema = load(root / CONTRACT_SCHEMA_REL)
    input_schema = load(root / INPUT_SCHEMA_REL)
    frontend = load(root / FRONTEND_REL)
    hir = load(root / HIR_REL)
    language = (root / LANGUAGE_REL).read_text(encoding="utf-8")
    types = (root / TYPE_REL).read_text(encoding="utf-8")
    mir = (root / MIR_REL).read_text(encoding="utf-8")
    decision = (root / DECISION_REL).read_text(encoding="utf-8")
    reference = (root / REFERENCE_REL).read_text(encoding="utf-8")
    generic_reference = (root / GENERIC_REFERENCE_REL).read_text(encoding="utf-8")
    diagnostics = {row.get("diagnostic_id"): row for row in chunk_rows(root, "spec/diagnostics/catalog/chunks/*.json")}
    predicates = {row.get("predicate_id"): row for row in chunk_rows(root, "spec/types/predicates/chunks/*.json")}
    predicate_fixtures = {row.get("fixture_id"): row for row in chunk_rows(root, "tests/conformance/checker-predicates/chunks/*.json")}
    features = {row.get("feature_id"): row for row in chunk_rows(root, "spec/features/catalog/chunks/*.json")}
    relations = chunk_rows(root, "spec/diagnostics/relations/chunks/*.json")

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        try:
            jsonschema.Draft202012Validator.check_schema(contract_schema)
            jsonschema.Draft202012Validator(contract_schema).validate(contract)
            jsonschema.Draft202012Validator.check_schema(input_schema)
            jsonschema.Draft202012Validator.check_schema(hir)
        except Exception as exc:  # noqa: BLE001
            errors.append("G01:SCHEMA_BINDING:" + type(exc).__name__)

    require(contract.get("gap_id") == "IR-CALL-P1-055", "G02", "GAP_ID")
    require(contract.get("input_descriptor_schema") == INPUT_SCHEMA_REL, "G02", "INPUT_SCHEMA_BINDING")
    scope = contract.get("scope", {})
    require(scope.get("included_call_modes") == ["ORDINARY", "MESSAGE"], "G02", "CALL_MODES")
    require(scope.get("new_surface_count") == 0, "G02", "NO_NEW_SURFACE")
    fence = contract.get("domain_fence", {})
    require(fence.get("both_nominal_and_extension_applicable") == "MEMBER_EXTENSION_COLLISION", "G02", "DOMAIN_COLLISION")
    require(fence.get("cross_domain_specificity_count") == 0, "G02", "NO_CROSS_DOMAIN_RANK")

    inference = contract.get("candidate_local_inference", {})
    require(inference.get("fresh_variable_owner") == "EXACT_CANDIDATE_GENERIC_OWNER", "G03", "FRESH_OWNER")
    require(inference.get("cross_candidate_constraint_flow") is False, "G03", "NO_CROSS_CANDIDATE_FLOW")
    require(inference.get("default_argument_contributes_constraints") is False, "G03", "DEFAULT_NOT_CONSTRAINT")
    require(inference.get("expected_result_contributes_constraints") is False, "G03", "RESULT_NOT_CONSTRAINT")
    require(inference.get("expected_result_filters_candidates") is False, "G03", "RESULT_NOT_FILTER")
    staging = contract.get("context_dependent_argument_staging", {})
    require(staging.get("candidate_local_body_probe_count") == 0 and staging.get("body_check_count_after_unique_winner") == 1, "G03", "LAMBDA_STAGING")

    specificity = contract.get("specificity", {})
    require(specificity.get("relation") == "STRICT_PARTIAL_ORDER", "G04", "PARTIAL_ORDER")
    require(specificity.get("channel_generality") == ["FIXED", "REPEATED", "NAMED_REST", "REPEATED_AND_NAMED"], "G04", "CHANNEL_ORDER")
    require(specificity.get("same_rank_input_domain_proofs") == ["EXACT_NOMINAL_SUBTYPE", "CONCRETE_OR_CONSTRUCTED_OVER_BARE_TYPE_PARAMETER", "STRICT_TRAIT_BOUND_SUPERSET"], "G04", "PROOF_SET")
    require(specificity.get("unknown_proof_result") == "INCOMPARABLE", "G04", "UNKNOWN_INCOMPARABLE")
    forbidden = set(specificity.get("preference_forbidden_axes", []))
    require({"EXPECTED_RESULT_TYPE", "RETURN_TYPE", "SOURCE_ORDER", "DECLARATION_ORDER", "IMPORT_ORDER", "PROVIDER_ORDER", "RUNTIME_VALUE"} <= forbidden, "G04", "FORBIDDEN_PREFERENCES")
    require(specificity.get("winner_rule") == "EXACTLY_ONE_MAXIMAL_APPLICABLE_CANDIDATE", "G04", "UNIQUE_MAXIMAL")

    expected_diagnostics = [
        "STATIC_CALL_SHAPE_NOT_ADMITTED",
        "MEMBER_EXTENSION_COLLISION",
        "ORDINARY_CALL_NO_APPLICABLE_CANDIDATE",
        "IMPLICIT_LAMBDA_EXPECTED_CALLABLE_AMBIGUOUS",
        "TRAILING_CLOSURE_OVERLOAD_AMBIGUOUS",
        "AMBIGUOUS_NAMED_REST_OVERLOAD",
        "AMBIGUOUS_REST_PARAMETER_OVERLOAD",
        "ORDINARY_CALL_OVERLOAD_AMBIGUOUS",
        "ORDINARY_CALL_RESULT_CONTEXT_MISMATCH",
    ]
    precedence = contract.get("diagnostic_precedence", [])
    require([row.get("rank") for row in precedence] == list(range(1, 10)), "G05", "DIAGNOSTIC_RANKS")
    require([row.get("diagnostic") for row in precedence] == expected_diagnostics, "G05", "DIAGNOSTIC_ORDER")
    require(all(item in diagnostics for item in expected_diagnostics), "G05", "DIAGNOSTIC_CATALOG_BINDING")
    relation_ids = {(row.get("predicate_id"), row.get("diagnostic_id")) for row in relations}
    require(all(("OrdinaryCallSelectionClosed", item) in relation_ids for item in expected_diagnostics[1:]), "G05", "DIAGNOSTIC_RELATIONS")

    output = contract.get("canonical_output", {})
    require(output.get("identity") == "OrdinaryCallSelectionV1", "G06", "OUTPUT_IDENTITY")
    require(output.get("selected_count") == 1 and output.get("unresolved_count") == 0, "G06", "OUTPUT_CARDINALITY")
    require(output.get("analysis_overload_set_residue_count") == 0, "G06", "NO_ANALYSIS_RESIDUE")
    runtime = contract.get("runtime_and_lowering", {})
    require(runtime.get("operand_runtime_evaluation_before_seal_count") == 0, "G06", "NO_EVAL_BEFORE_SEAL")
    require(runtime.get("runtime_selection_count") == 0 and runtime.get("mir_specificity_ranking_count") == 0 and runtime.get("backend_relookup_count") == 0, "G06", "NO_RUNTIME_SELECTION")

    frontend_contract = frontend.get("ordinary_call_selection_contract", {})
    require(frontend_contract.get("contract") == CONTRACT_REL and frontend_contract.get("canonical_output") == "OrdinaryCallSelectionV1", "G07", "FRONTEND_CONTRACT")
    require(frontend_contract.get("candidate_local_phase_a", {}).get("cross_candidate_constraint_flow") is False, "G07", "FRONTEND_LOCALITY")
    require(frontend_contract.get("runtime_or_mir_ranking_count") == 0, "G07", "FRONTEND_RUNTIME_FENCE")
    handoff = frontend.get("lowering_and_semantic_responsibility", {}).get("r4_resolver_handoff", {})
    require("closed_by_ordinary_call_selection_v1" in handoff and "deferred_to_generic_and_ordinary_overload_cluster" not in handoff, "G07", "R4_HANDOFF_CLOSED")

    defs = hir.get("$defs", {})
    selection_def = defs.get("OrdinaryCallSelectionV1", {})
    call_plan = defs.get("CallPlan", {})
    require(set(output.get("required_fields", [])) <= set(selection_def.get("required", [])), "G08", "HIR_REQUIRED_FIELDS")
    require(call_plan.get("properties", {}).get("ordinary_call_selection", {}).get("$ref") == "#/$defs/OrdinaryCallSelectionV1", "G08", "HIR_CALLPLAN_BINDING")
    require(any("ordinary_call_selection" in row.get("then", {}).get("required", []) for row in call_plan.get("allOf", [])), "G08", "HIR_CONDITIONAL_REQUIRED")

    predicate = predicates.get("OrdinaryCallSelectionClosed", {})
    require(predicate.get("input_descriptor_schema") == INPUT_SCHEMA_REL, "G09", "PREDICATE_SCHEMA")
    require(predicate.get("success_result") == "OrdinaryCallSelectionV1(selected_count=1, unresolved_count=0)", "G09", "PREDICATE_RESULT")
    fixture_ids = predicate.get("positive_fixture_ids", []) + predicate.get("negative_fixture_ids", [])
    require(all(item in predicate_fixtures for item in fixture_ids), "G09", "PREDICATE_FIXTURES")
    require(all(predicate_fixtures[item].get("predicate_id") == "OrdinaryCallSelectionClosed" for item in fixture_ids if item in predicate_fixtures), "G09", "PREDICATE_FIXTURE_OWNER")

    for feature_id in ("exact_function_signature_callshape_law", "generic_parameter_model_phase_a", "rest_parameter_overload_specificity_law"):
        row = features.get(feature_id, {})
        refs = row.get("normative_trace_refs", {})
        require("OrdinaryCallSelectionClosed" in refs.get("predicates", []), "G10", "FEATURE_PREDICATE:" + feature_id)
        require(row.get("product_support") == "NOT_RUN", "G10", "FEATURE_PRODUCT:" + feature_id)

    counts = Counter(row.get("class") for row in fixture.get("cases", []))
    expected = fixture.get("expected_counts", {})
    require(len(fixture.get("cases", [])) == expected.get("cases") == 15, "G11", "CASE_COUNT")
    require(counts == Counter({"positive": 5, "boundary": 5, "reject": 5}), "G11", "CASE_CLASSES")
    require(len(fixture.get("metamorphic_cases", [])) == expected.get("metamorphic") == 4, "G11", "METAMORPHIC_COUNT")
    require(all(row.get("selected_count") == 0 for row in fixture.get("cases", []) if row.get("class") == "reject"), "G11", "REJECT_SELECTED_ZERO")
    require(expected.get("semantic_p0") == 0 and expected.get("feature_p1") == 22 and expected.get("product_lanes") == 15 and expected.get("product_executed") == 0, "G11", "FIXTURE_GOVERNANCE")

    require("OrdinaryCallSelectionV1" in language and "result-only overloads remain ambiguous" in language, "G12", "LANGUAGE_BINDING")
    require("exactly one maximal candidate" in types and "nonexecuting static descriptor" in types, "G12", "TYPE_BINDING")
    require("Call selection is a static, nonexecuting proof" in mir, "G12", "MIR_BINDING")
    require("strict partial order" in reference and "candidate-local" in reference, "G12", "REFERENCE_BINDING")
    require("후보마다" in generic_reference and "expected result" in generic_reference, "G12", "GENERIC_REFERENCE_BINDING")
    for stale in ("generic/ordinary-overload cluster가 닫는다", "generic and\nordinary-overload cluster", "subsequent generic and\nordinary-overload cluster"):
        require(stale not in language + types + mir + reference, "G12", "STALE_DEFER:" + stale.replace("\n", "_"))

    governance = contract.get("governance", {})
    require(governance == {"semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "production_implementation": "NOT_RUN", "github_publication": "NOT_PERFORMED"}, "G13", "GOVERNANCE_EXACT")
    for fragment in ("gap_id: IR-CALL-P1-055", "semantic_p0: 0", "feature_p1: 22_OPEN_UNCHANGED", "product_lanes: 15/15_NOT_RUN", "LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED"):
        require(fragment in decision, "G13", "DECISION_FENCE:" + fragment)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    print(json.dumps({
        "schema": "deeplus.ordinary-call-selection-v1-validation-receipt/r1",
        "result": "FAIL" if errors else "PASS",
        "error_count": len(errors),
        "errors": errors,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN"
    }, ensure_ascii=False, separators=(",", ":")))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
