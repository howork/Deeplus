#!/usr/bin/env python3
"""Validate the bounded R105 generic and higher-order responsibility handoff."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("spec/contracts/generic-applicability-variance-responsibility-r105.json")
FIXTURE = Path("tests/fixtures/current/generic-applicability-variance-responsibility-r105.json")
PREDICATE_DIR = Path("spec/types/predicates/chunks")
FEATURE_DIR = Path("spec/features/catalog/chunks")

ALGORITHMS = [
    "GenericApplicabilityV1",
    "GenericVarianceV1",
    "FunctionResponsibilityCompatibilityV1",
]
PARAMETER_KINDS = ["TYPE", "STATIC_INT", "EFFECT_ROW", "ERROR_SET"]
PREDICATE_IDS = [
    "GenericConstraintSatisfied",
    "GenericConstructorVariance",
    "GenericInvarianceAdmitted",
    "GenericVarianceDescriptorAdmitted",
    "TraitVariancePositionAdmitted",
    "ResponsibilitySubsumes",
    "EffectRowForwardingAdmitted",
    "ErrorRowForwardingAdmitted",
]
PROMOTED_PREDICATES = {
    "GenericConstraintSatisfied": "GenericApplicabilityV1",
    "GenericConstructorVariance": "GenericVarianceV1",
    "GenericInvarianceAdmitted": "GenericVarianceV1",
    "GenericVarianceDescriptorAdmitted": "GenericVarianceV1",
    "EffectRowForwardingAdmitted": "FunctionResponsibilityCompatibilityV1",
    "ErrorRowForwardingAdmitted": "FunctionResponsibilityCompatibilityV1",
}
FEATURE_IDS = {
    "generic_parameter_model_phase_a",
    "generic_invariance_default_law",
    "generic_responsibility_quantification_law",
    "generic_type_constructor_subtyping_law",
    "generic_variance_descriptor_phase_a",
    "generic_variance_phase_b_trait_only",
    "function_type_variance_law_phase_a",
    "effect_error_row_polymorphism_phase_a",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog(root: Path, relative: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / relative).glob("part-*.json")):
        for row in load(path):
            identity = row.get(key)
            if identity:
                rows[identity] = row
    return rows


def model_errors(root: Path, docs: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = docs["contract"]
    fixture = docs["fixture"]
    predicates = docs["predicates"]
    features = docs["features"]

    if (
        contract.get("schema") != "deeplus.generic-applicability-variance-responsibility/r105"
        or contract.get("revision") != "r105-closed-generic-and-higher-order-responsibility"
        or contract.get("status") != "LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF"
        or contract.get("baseline", {}).get("predecessor_commit")
        != "615f7822b6a81f3e7869bb596d1d4fe09388ea02"
        or contract.get("baseline", {}).get("current_binding") is not False
    ):
        errors.append("CONTRACT_IDENTITY")

    scope = contract.get("scope", {})
    if (
        scope.get("existing_surface_only") is not True
        or scope.get("new_syntax_count") != 0
        or scope.get("generic_parameter_kinds") != PARAMETER_KINDS
        or scope.get("algorithms") != ALGORITHMS
        or scope.get("predicate_ids") != PREDICATE_IDS
    ):
        errors.append("SCOPE_EXACT")

    generic = contract.get("generic_applicability", {})
    if (
        generic.get("algorithm_id") != ALGORITHMS[0]
        or len(generic.get("ordered_steps", [])) != 7
        or set(generic.get("where_predicates", {}))
        != {"type_equality", "trait_conformance", "effect_row_relation", "visibility"}
        or set(generic.get("forbidden_solver_inputs", []))
        != {
            "expected result type", "return type preference",
            "source, declaration, import or provider order", "runtime values",
            "anonymous Union synthesis", "failed sibling-candidate bindings",
            "implicit responsibility evidence",
        }
        or "failed candidate" not in generic.get("failure_atomicity", "")
    ):
        errors.append("GENERIC_ALGORITHM")

    variance = contract.get("generic_variance", {})
    owners = variance.get("owner_matrix", [])
    kinds = variance.get("kind_matrix", [])
    if (
        variance.get("algorithm_id") != ALGORITHMS[1]
        or [row.get("owner") for row in owners]
        != ["CLASS", "ENUM", "RECORD_OR_OTHER_NOMINAL", "TRAIT", "FUNCTION_TYPE"]
        or [row.get("kind") for row in kinds] != PARAMETER_KINDS
        or owners[0].get("declared_variance") != "FORBIDDEN"
        or owners[1].get("declared_variance") != "FORBIDDEN"
        or kinds[2].get("declared_in_out") != "FORBIDDEN"
        or variance.get("position_calculus", {}).get("mutable_or_inout_storage") != "INVARIANT"
        or variance.get("position_calculus", {}).get("owned_borrowed_mut_inout_qualified_type") != "INVARIANT"
        or "use-site variance" not in variance.get("forbidden", [])
    ):
        errors.append("VARIANCE_ALGORITHM")

    higher = contract.get("higher_order_responsibility", {})
    compatibility = higher.get("compatibility", {})
    forwarding = higher.get("forwarding", {})
    if (
        higher.get("algorithm_id") != ALGORITHMS[2]
        or compatibility.get("channel_shape") != "exact"
        or compatibility.get("parameter_mode_and_ownership") != "exact"
        or "contravariant" not in compatibility.get("parameter_type", "")
        or "covariant" not in compatibility.get("result_type", "")
        or "subset" not in compatibility.get("source_error_set", "")
        or "subset" not in compatibility.get("source_effect_row", "")
        or compatibility.get("cancellation_suspension_isolation") != "exact"
        or "never dropped" not in compatibility.get("authority_call_right_capture_cleanup", "")
        or "includes" not in forwarding.get("callback_errors", "")
        or "includes" not in forwarding.get("callback_effects", "")
        or len(higher.get("no_hidden_adaptation", [])) != 6
    ):
        errors.append("FUNCTION_RESPONSIBILITY_ALGORITHM")

    precedence = contract.get("diagnostic_precedence", [])
    if (
        len(precedence) != 13
        or len(set(precedence)) != 13
        or precedence[:3] != [
            "GENERIC_PARAM_KIND_MISMATCH",
            "ORDINARY_CALL_NO_APPLICABLE_CANDIDATE",
            "GENERIC_CONSTRAINT_UNSATISFIED",
        ]
    ):
        errors.append("DIAGNOSTIC_PRECEDENCE")
    residue = contract.get("hir_residue", {})
    if residue.get("unresolved_variable_count") != 0 or residue.get("runtime_generic_or_variance_lookup_count") != 0:
        errors.append("HIR_ZERO_RESIDUE")

    if (
        fixture.get("schema") != "deeplus.generic-applicability-variance-responsibility-fixtures/r105"
        or fixture.get("contract") != CONTRACT.as_posix()
    ):
        errors.append("FIXTURE_IDENTITY")
    cases = fixture.get("cases", [])
    classes = {name: sum(row.get("class") == name for row in cases) for name in ("positive", "boundary", "reject")}
    axes = {name: sum(row.get("axis") == name for row in cases) for name in ("generic", "variance", "function")}
    if (
        len(cases) != 22
        or len({row.get("id") for row in cases}) != 22
        or classes != {"positive": 8, "boundary": 5, "reject": 9}
        or axes != {"generic": 8, "variance": 8, "function": 6}
    ):
        errors.append("FIXTURE_PARTITION")
    if [row.get("id") for row in cases] != [
        f"R105-{('GEN' if index <= 8 else 'VAR' if index <= 16 else 'FUN')}-"
        f"{('P' if row.get('class') == 'positive' else 'B' if row.get('class') == 'boundary' else 'N')}-{index:03d}"
        for index, row in enumerate(cases, start=1)
    ]:
        errors.append("FIXTURE_ID_ORDER")

    contract_rel = CONTRACT.as_posix()
    for predicate_id, algorithm in PROMOTED_PREDICATES.items():
        row = predicates.get(predicate_id, {})
        if (
            row.get("predicate_maturity") != "design_algorithm"
            or row.get("emission_eligible") is not True
            or row.get("diagnostic_disposition") != "active_primary"
            or row.get("predecessor_contract") != contract_rel
            or not any(algorithm in step for step in row.get("decision_procedure", []))
        ):
            errors.append(f"PREDICATE_PROMOTION:{predicate_id}")
    for predicate_id in ("TraitVariancePositionAdmitted", "ResponsibilitySubsumes"):
        row = predicates.get(predicate_id, {})
        if row.get("predicate_maturity") != "design_algorithm" or row.get("emission_eligible") is not True:
            errors.append(f"PREDICATE_DEPENDENCY:{predicate_id}")

    for feature_id in FEATURE_IDS:
        row = features.get(feature_id, {})
        trace = row.get("normative_trace_refs", {})
        if row.get("status_enum") != "STABLE_DESIGN" or "R105" not in row.get("notes", "") or not trace.get("predicates"):
            errors.append(f"FEATURE_BINDING:{feature_id}")

    acceptance = contract.get("acceptance", {})
    if acceptance != {
        "fixture_path": FIXTURE.as_posix(),
        "case_count": 22,
        "positive_count": 8,
        "boundary_count": 5,
        "reject_count": 9,
        "required_mutation_count": 12,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_checker": "NOT_RUN",
        "github_mutation": 0,
    }:
        errors.append("GOVERNANCE_ACCEPTANCE")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    docs = {
        "contract": load(root / CONTRACT),
        "fixture": load(root / FIXTURE),
        "predicates": catalog(root, PREDICATE_DIR, "predicate_id"),
        "features": catalog(root, FEATURE_DIR, "feature_id"),
    }
    errors = model_errors(root, docs)
    rejected = 0
    mutation_total = 0
    if args.mutations and not errors:
        mutations: list[dict[str, Any]] = []
        for index in range(12):
            candidate = copy.deepcopy(docs)
            if index == 0:
                candidate["contract"]["scope"]["generic_parameter_kinds"].pop()
            elif index == 1:
                candidate["contract"]["generic_applicability"]["forbidden_solver_inputs"].remove("expected result type")
            elif index == 2:
                candidate["contract"]["generic_applicability"]["failure_atomicity"] = "commit failed bindings"
            elif index == 3:
                candidate["contract"]["generic_variance"]["owner_matrix"][0]["declared_variance"] = "IN_OR_OUT"
            elif index == 4:
                candidate["contract"]["generic_variance"]["kind_matrix"][2]["declared_in_out"] = "TRAIT_ONLY"
            elif index == 5:
                candidate["contract"]["generic_variance"]["position_calculus"]["mutable_or_inout_storage"] = "COVARIANT"
            elif index == 6:
                candidate["contract"]["higher_order_responsibility"]["compatibility"]["source_error_set"] = "exact"
            elif index == 7:
                candidate["contract"]["higher_order_responsibility"]["compatibility"]["authority_call_right_capture_cleanup"] = "ignored"
            elif index == 8:
                candidate["fixture"]["cases"].pop()
            elif index == 9:
                candidate["predicates"]["GenericConstraintSatisfied"]["emission_eligible"] = False
            elif index == 10:
                candidate["features"]["function_type_variance_law_phase_a"]["normative_trace_refs"]["predicates"] = []
            else:
                candidate["contract"]["acceptance"]["product_lanes"] = "PASS"
            mutations.append(candidate)
        mutation_total = len(mutations)
        rejected = sum(bool(model_errors(root, candidate)) for candidate in mutations)
        if rejected != mutation_total:
            errors.append("MUTATION_SURVIVED")

    receipt = {
        "schema": "deeplus.generic-applicability-variance-responsibility-validation/r105",
        "result": "PASS" if not errors else "FAIL",
        "algorithm_count": 3,
        "fixture_count": 22,
        "predicate_count": 8,
        "feature_count": 8,
        "mutation_rejections": rejected,
        "mutation_total": mutation_total,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_checker": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
