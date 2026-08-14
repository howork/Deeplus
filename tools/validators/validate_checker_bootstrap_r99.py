#!/usr/bin/env python3
"""Validate R99 private ErrorSet inference and exact Callable facade closure."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


class ValidationError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, code: str, detail: Any = None) -> None:
    if not condition:
        suffix = "" if detail is None else f": {detail}"
        raise ValidationError(f"{code}{suffix}")


def rows(root: Path, relative: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        value = read_json(path)
        require(isinstance(value, list), "R99_CATALOG_CHUNK_NOT_ARRAY", path)
        result.extend(value)
    return result


def by_id(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item.get(key)
        require(isinstance(value, str), "R99_CATALOG_ID_MISSING", key)
        require(value not in result, "R99_CATALOG_ID_DUPLICATE", value)
        result[value] = item
    return result


def validate_contract_core(private: dict[str, Any], callable_: dict[str, Any]) -> None:
    require(private.get("schema") == "deeplus.private-error-set-inference/v1", "R99_PRIVATE_SCHEMA")
    require(private.get("gap_id") == "IR-ERR-P1-067", "R99_PRIVATE_GAP")
    owners = private.get("admitted_omission_owners")
    require(isinstance(owners, list) and len(owners) == 4, "R99_PRIVATE_OWNER_COUNT")
    require(
        [(row.get("owner"), row.get("effective_visibility")) for row in owners]
        == [
            ("NestedLocalFunction", "LEXICAL"),
            ("TopLevelCallable", "private"),
            ("NominalMemberCallable", "-"),
            ("ExtensionMemberCallable", "-"),
        ],
        "R99_PRIVATE_OWNER_ROWS",
    )
    sealed = private.get("sealed_input", {})
    require(
        sealed.get("required_predecessors")
        == [
            "name_resolution_complete",
            "ordinary_call_selection_complete",
            "generic_substitution_complete",
            "callable_visibility_normalized",
        ],
        "R99_PRIVATE_PREDECESSORS",
    )
    require(sealed.get("unresolved_or_ambiguous_call_admitted") is False, "R99_PRIVATE_UNSEALED_CALL")
    require(sealed.get("effect_inference_performed") is False, "R99_PRIVATE_EFFECT_INFERENCE")
    recursive = sealed.get("recursive_substitution_law", {})
    require(
        recursive.get("inferred_scc_edge_admitted")
        == "caller and callee have exactly the same normalized substitution vector",
        "R99_PRIVATE_RECURSIVE_SAME_VECTOR",
    )
    require(recursive.get("different_or_expansive_vector_admitted") is False, "R99_PRIVATE_EXPANSIVE_VECTOR")
    require(
        recursive.get("rejection_diagnostic")
        == "ERROR_ROW_PRIVATE_INFERENCE_NONFINITE_INSTANCE_GRAPH",
        "R99_PRIVATE_NONFINITE_DIAGNOSTIC",
    )
    algorithm = private.get("algorithm", {})
    require(algorithm.get("name") == "PrivateErrorInferenceV1", "R99_PRIVATE_ALGORITHM")
    require(algorithm.get("source_order_affects_result") is False, "R99_PRIVATE_SOURCE_ORDER")
    require(algorithm.get("expected_result_type_affects_result") is False, "R99_PRIVATE_EXPECTED_RESULT")
    require("least fixed point" in " ".join(algorithm.get("steps", [])), "R99_PRIVATE_FIXED_POINT")
    require(private.get("normalization", {}).get("row") == "sorted unique ErrorId set", "R99_PRIVATE_NORMALIZATION")
    require(
        private.get("diagnostic_precedence")
        == [
            "existing resolver or ordinary-call-selection diagnostic",
            "ERROR_ROW_PRIVATE_INFERENCE_NOT_ADMITTED",
            "ERROR_ROW_PRIVATE_INFERENCE_UNSEALED_CALL",
            "ERROR_ROW_PRIVATE_INFERENCE_NONFINITE_INSTANCE_GRAPH",
            "ERROR_ROW_PRIVATE_TYPE_LEAK",
        ],
        "R99_PRIVATE_DIAGNOSTIC_ORDER",
    )

    require(callable_.get("schema") == "deeplus.callable-exact-signature-facade/v1", "R99_CALLABLE_SCHEMA")
    require(callable_.get("gap_id") == "IR-CALL-P1-068", "R99_CALLABLE_GAP")
    surface = callable_.get("surface", {})
    require(surface.get("canonical_shape") == "Callable<Sig>", "R99_CALLABLE_SURFACE")
    require(surface.get("type_argument_count") == 1, "R99_CALLABLE_TYPE_ARG_COUNT")
    require(surface.get("new_grammar_production_count") == 0, "R99_CALLABLE_GRAMMAR_DELTA")
    require(surface.get("bare_callable_admitted") is False, "R99_CALLABLE_BARE")
    identity = callable_.get("exact_signature_identity_fields")
    require(isinstance(identity, list) and len(identity) == 11, "R99_CALLABLE_IDENTITY_FIELD_COUNT")
    normalization = callable_.get("normalization", {})
    for field in (
        "distinct_nominal_type_id",
        "distinct_runtime_representation",
        "dynamic_erasure",
        "existential_packaging",
        "hidden_allocation",
    ):
        require(normalization.get(field) is False, "R99_CALLABLE_FALSE_FENCE", field)
    require(normalization.get("rule") == "Callable<Sig> normalizes exactly to Sig", "R99_CALLABLE_NORMALIZATION")
    compat = callable_.get("compatibility_and_invocation", {})
    require(compat.get("overload_discriminator") is False, "R99_CALLABLE_OVERLOAD")
    require(compat.get("runtime_lookup") is False, "R99_CALLABLE_RUNTIME_LOOKUP")


def validate_all(root: Path, private: dict[str, Any], callable_: dict[str, Any], fixture: dict[str, Any]) -> dict[str, int]:
    validate_contract_core(private, callable_)
    feature_map = by_id(rows(root, "spec/features/catalog/chunks"), "feature_id")
    diagnostic_map = by_id(rows(root, "spec/diagnostics/catalog/chunks"), "diagnostic_id")
    for feature_id, contract_path, diagnostics in (
        (
            "private_error_set_inference",
            "spec/contracts/private-error-set-inference-v1.json",
            [
                "ERROR_ROW_PRIVATE_INFERENCE_NOT_ADMITTED",
                "ERROR_ROW_PRIVATE_INFERENCE_UNSEALED_CALL",
                "ERROR_ROW_PRIVATE_INFERENCE_NONFINITE_INSTANCE_GRAPH",
                "ERROR_ROW_PRIVATE_TYPE_LEAK",
            ],
        ),
        (
            "callable_facade_preview",
            "spec/contracts/callable-exact-signature-facade-v1.json",
            ["CALLABLE_EXACT_SIGNATURE_FACADE_REQUIRED", "BARE_FUNCTION_TYPE_REMOVED"],
        ),
    ):
        feature = feature_map.get(feature_id, {})
        require(feature.get("status_enum") == "STABLE_DESIGN", "R99_FEATURE_STATUS", feature_id)
        require(feature.get("product_support") == "NOT_RUN", "R99_FEATURE_PRODUCT", feature_id)
        require(contract_path in feature.get("artifact_trace_refs", []), "R99_FEATURE_CONTRACT_TRACE", feature_id)
        require(feature.get("normative_trace_refs", {}).get("diagnostics") == diagnostics, "R99_FEATURE_DIAGNOSTICS", feature_id)
        for diagnostic_id in diagnostics:
            diagnostic = diagnostic_map.get(diagnostic_id, {})
            require(diagnostic.get("diagnostic_status") == "active", "R99_DIAGNOSTIC_STATUS", diagnostic_id)
            require(diagnostic.get("diagnostic_class") == "current_source", "R99_DIAGNOSTIC_CLASS", diagnostic_id)
            require(diagnostic.get("product_support") == "NOT_RUN", "R99_DIAGNOSTIC_PRODUCT", diagnostic_id)

    cases = fixture.get("cases")
    require(isinstance(cases, list) and len(cases) == 13, "R99_FIXTURE_CASE_COUNT")
    ids = [case.get("id") for case in cases]
    require(len(ids) == len(set(ids)), "R99_FIXTURE_DUPLICATE_ID")
    counts = {
        category: sum(case.get("category") == category for case in cases)
        for category in ("positive", "boundary", "reject")
    }
    require(counts == {"positive": 3, "boundary": 3, "reject": 7}, "R99_FIXTURE_CATEGORY_COUNTS", counts)
    case_map = {case.get("id"): case for case in cases}
    require(
        case_map.get("R99-ERR-POS-002", {}).get("expected") == "ADMIT_FINITE_SAME_SUBSTITUTION_SCC",
        "R99_PRIVATE_SAME_VECTOR_POSITIVE",
    )
    require(
        case_map.get("R99-ERR-BOUND-002", {}).get("expected") == "NORMALIZE_THEN_ADMIT_SAME_VECTOR",
        "R99_PRIVATE_ALIAS_BOUNDARY",
    )
    require(
        case_map.get("R99-ERR-REJECT-004", {}).get("expected")
        == "ERROR_ROW_PRIVATE_INFERENCE_NONFINITE_INSTANCE_GRAPH",
        "R99_PRIVATE_EXPANSIVE_REJECT",
    )
    require(
        fixture.get("governance")
        == {
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "product_execution": "NOT_RUN",
        },
        "R99_GOVERNANCE",
    )
    language = (root / "spec/language.md").read_text(encoding="utf-8")
    type_system = (root / "spec/types/type-system.md").read_text(encoding="utf-8")
    frontend = read_json(root / "spec/frontend/frontend-model.json")
    for needle in ("PrivateErrorInferenceV1", "Callable<Sig>"):
        require(needle in language, "R99_LANGUAGE_BINDING", needle)
        require(needle in type_system, "R99_TYPE_BINDING", needle)
    require(frontend.get("private_error_set_inference_frontend_contract", {}).get("eligible_omission_owner_count") == 4, "R99_FRONTEND_PRIVATE")
    require(frontend.get("callable_exact_signature_facade_frontend_contract", {}).get("normalization") == "Callable<Sig> == Sig", "R99_FRONTEND_CALLABLE")
    return counts


def run_mutations(private: dict[str, Any], callable_: dict[str, Any]) -> int:
    mutations: list[tuple[dict[str, Any], dict[str, Any]]] = []
    value = copy.deepcopy(private); value["admitted_omission_owners"].pop(); mutations.append((value, callable_))
    value = copy.deepcopy(private); value["algorithm"]["source_order_affects_result"] = True; mutations.append((value, callable_))
    value = copy.deepcopy(private); value["sealed_input"]["effect_inference_performed"] = True; mutations.append((value, callable_))
    value = copy.deepcopy(private); value["sealed_input"]["recursive_substitution_law"]["different_or_expansive_vector_admitted"] = True; mutations.append((value, callable_))
    value = copy.deepcopy(callable_); value["surface"]["type_argument_count"] = 0; mutations.append((private, value))
    value = copy.deepcopy(callable_); value["normalization"]["dynamic_erasure"] = True; mutations.append((private, value))
    value = copy.deepcopy(callable_); value["compatibility_and_invocation"]["overload_discriminator"] = True; mutations.append((private, value))
    rejected = 0
    for mutated_private, mutated_callable in mutations:
        try:
            validate_contract_core(mutated_private, mutated_callable)
        except ValidationError:
            rejected += 1
    require(rejected == len(mutations) == 7, "R99_MUTATION_COUNT", rejected)
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        private = read_json(root / "spec/contracts/private-error-set-inference-v1.json")
        callable_ = read_json(root / "spec/contracts/callable-exact-signature-facade-v1.json")
        fixture = read_json(root / "tests/fixtures/current/checker-bootstrap-r99.json")
        counts = validate_all(root, private, callable_, fixture)
        mutation_count = run_mutations(private, callable_) if args.mutations else 0
    except (OSError, ValueError, KeyError, ValidationError) as exc:
        print(f"R99_CHECKER_BOOTSTRAP_VALIDATION_FAILED: {exc}")
        return 1
    print(
        json.dumps(
            {
                "schema": "deeplus.checker-bootstrap-r99-validation/r1",
                "result": "PASS",
                "gaps_closed": ["IR-ERR-P1-067", "IR-CALL-P1-068"],
                "case_counts": counts,
                "mutation_count": mutation_count,
                "evidence_level": "E2_STATIC_MUTATION_BACKED",
                "product_execution": "NOT_RUN",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
