#!/usr/bin/env python3
"""Validate the bounded strong Eq/Ord coherence contract."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/strong-comparison-coherence-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/strong-comparison-coherence-v1.schema.json"
DESCRIPTOR_SCHEMA_REL = "schemas/language/strong-comparison-decision-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/strong-comparison-coherence-v1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Strong_Comparison_Coherence_Closure_R1.md"

RHS_DIAGNOSTIC = "STRONG_COMPARISON_RHS_NOT_ADMITTED"
FAMILY_DIAGNOSTIC = "STRONG_COMPARISON_BILATERAL_FAMILY_INVALID"
EXPECTED_COUNTS = {"normal": 3, "boundary": 4, "reject": 5}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def reject(diagnostic: str) -> dict[str, Any]:
    return {"outcome": "REJECT", "diagnostic_or_null": diagnostic}


def decide(descriptor: dict[str, Any]) -> dict[str, Any]:
    origin = descriptor.get("evidence_origin")
    left = descriptor.get("left_type_id")
    right = descriptor.get("right_type_id")
    role = descriptor.get("trait_role")
    laws = descriptor.get("laws", {})

    if origin == "INTRINSIC_RESERVED":
        return {"outcome": "BYPASS_CONFORMANCE", "diagnostic_or_null": None}

    if not descriptor.get("strong_profile_eligible"):
        return reject(RHS_DIAGNOSTIC)

    eq_laws = all(laws.get(name) is True for name in ("reflexive", "symmetric", "transitive", "total"))
    ord_laws = eq_laws and all(laws.get(name) is True for name in ("reverse_sign", "zero_iff_eq"))
    laws_ok = eq_laws if role == "EQ" else ord_laws

    if origin in {"USER_LEFT_OWNER", "LANGUAGE_DERIVED_SELF"}:
        if left != right:
            return reject(RHS_DIAGNOSTIC)
        if origin == "USER_LEFT_OWNER" and descriptor.get("declaring_owner_type_id_or_null") != left:
            return reject(RHS_DIAGNOSTIC)
        if not laws_ok:
            return reject(FAMILY_DIAGNOSTIC)
        return {"outcome": "ADMIT_SELF_DOMAIN", "diagnostic_or_null": None}

    if origin == "PRELUDE_SEALED_FAMILY":
        complete = (
            left != right
            and descriptor.get("declaring_owner_type_id_or_null") is None
            and bool(descriptor.get("family_id_or_null"))
            and bool(descriptor.get("reverse_witness_id_or_null"))
            and bool(descriptor.get("normalization_domain_id_or_null"))
            and laws_ok
        )
        if not complete:
            return reject(FAMILY_DIAGNOSTIC)
        return {"outcome": "ADMIT_SEALED_BILATERAL_FAMILY", "diagnostic_or_null": None}

    return reject(RHS_DIAGNOSTIC)


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
    validate_schema: bool = True,
) -> list[str]:
    errors: list[str] = []
    contract = contract_override or load(root / CONTRACT_REL)
    fixture = fixture_override or load(root / FIXTURE_REL)

    if validate_schema:
        try:
            import jsonschema  # type: ignore

            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            descriptor_schema = load(root / DESCRIPTOR_SCHEMA_REL)
            descriptor_validator = jsonschema.Draft202012Validator(descriptor_schema)
            for case in fixture.get("cases", []):
                descriptor_validator.validate(case.get("descriptor"))
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover - exact message depends on jsonschema
            errors.append(f"SCHEMA_VALIDATION:{exc}")

    if contract.get("feature_p1_binding") != "TCC-P1-003_REMAINS_OPEN":
        errors.append("FEATURE_P1_BINDING_DRIFT")
    if contract.get("admission") != {
        "intrinsic_reserved": "BYPASS_CONFORMANCE",
        "user_defined": "NORMALIZED_RHS_MUST_EQUAL_SELF",
        "heterogeneous": "SEALED_BILATERAL_FAMILY_ONLY",
    }:
        errors.append("ADMISSION_DOMAIN_DRIFT")
    family = contract.get("sealed_bilateral_family_contract", {})
    expected_family = {
        "authority": "COMPILER_OR_PRELUDE_SEALED",
        "unordered_pair_key": "sort(NormalizedTypeId(A),NormalizedTypeId(B))",
        "oriented_witness_count": 2,
        "normalization_domain_required": True,
        "eq_symmetry_required": True,
        "ord_sign_reversal_required": True,
        "ord_zero_agreement_required": True,
        "runtime_lookup_count": 0,
    }
    if family != expected_family:
        errors.append("BILATERAL_FAMILY_CONTRACT_DRIFT")
    if contract.get("current_sealed_bilateral_families") != []:
        errors.append("UNAUTHORIZED_CURRENT_BILATERAL_FAMILY")
    if contract.get("law_domain") != {
        "eq": ["reflexive", "symmetric", "transitive", "total_bool"],
        "ord": ["total", "trichotomy", "transitive", "antisymmetric", "reverse_sign", "zero_iff_eq"],
    }:
        errors.append("STRONG_COMPARISON_LAW_DOMAIN_DRIFT")
    identity = contract.get("canonical_identity", {})
    if identity != {
        "self_domain_family_id": None,
        "heterogeneous_family_id_required": True,
        "reverse_witness_id_required": True,
        "hir_runtime_relookup_count": 0,
    }:
        errors.append("CANONICAL_IDENTITY_FENCE_DRIFT")
    if contract.get("acceptance") != {"normal": 3, "boundary": 4, "reject": 5, "mutations": 8}:
        errors.append("ACCEPTANCE_COUNT_DRIFT")
    if contract.get("governance") != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE_OVERCLAIM_OR_DRIFT")

    cases = fixture.get("cases", [])
    counts = Counter(case.get("class") for case in cases)
    if dict(counts) != EXPECTED_COUNTS:
        errors.append(f"FIXTURE_CLASS_COUNTS:{dict(counts)}")
    if len({case.get("case_id") for case in cases}) != len(cases):
        errors.append("FIXTURE_CASE_ID_DUPLICATE")
    for case in cases:
        observed = decide(case.get("descriptor", {}))
        if observed != case.get("expected"):
            errors.append(f"FIXTURE_ORACLE:{case.get('case_id')}:{observed}")

    diagnostics = {row.get("diagnostic_id") for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    for diagnostic in (RHS_DIAGNOSTIC, FAMILY_DIAGNOSTIC):
        if diagnostic not in diagnostics:
            errors.append(f"DIAGNOSTIC_MISSING:{diagnostic}")
    predicates = {row.get("predicate_id"): row for row in all_rows(root, "spec/types/predicates/chunks")}
    predicate = predicates.get("StrongComparisonConformanceAdmitted", {})
    if predicate.get("input_descriptor_schema") != DESCRIPTOR_SCHEMA_REL:
        errors.append("PREDICATE_DESCRIPTOR_BINDING_MISSING")
    if set(predicate.get("diagnostic_refs", [])) != {RHS_DIAGNOSTIC, FAMILY_DIAGNOSTIC}:
        errors.append("PREDICATE_DIAGNOSTIC_BINDING_DRIFT")
    features = {row.get("feature_id"): row for row in all_rows(root, "spec/features/catalog/chunks")}
    fixed = features.get("fixed_operator_conformance_overloading", {})
    refs = fixed.get("normative_trace_refs", {})
    if "StrongComparisonConformanceAdmitted" not in refs.get("predicates", []):
        errors.append("FEATURE_PREDICATE_TRACE_MISSING")
    if CONTRACT_REL not in fixed.get("artifact_trace_refs", []):
        errors.append("FEATURE_ARTIFACT_TRACE_MISSING")

    decision = (root / DECISION_REL).read_text(encoding="utf-8")
    required_text = [
        "NORMALIZED_RHS_MUST_EQUAL_SELF",
        "SEALED_BILATERAL_FAMILY_ONLY",
        "TCC-P1-003",
        "15_OF_15_NOT_RUN",
    ]
    joined = "\n".join([
        decision,
        (root / "spec/language.md").read_text(encoding="utf-8"),
        (root / "spec/types/type-system.md").read_text(encoding="utf-8"),
        (root / "spec/mir/semantics.md").read_text(encoding="utf-8"),
        (root / "library/prelude/prelude.md").read_text(encoding="utf-8"),
    ])
    for token in required_text:
        if token not in joined:
            errors.append(f"NORMATIVE_TEXT_BINDING_MISSING:{token}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    fixture = load(root / FIXTURE_REL)
    counts = Counter(case["class"] for case in fixture["cases"])
    print(json.dumps({
        "schema": "deeplus.strong-comparison-coherence-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_p1": "TCC-P1-003_OPEN_UNCHANGED",
        "cases": dict(counts),
        "current_sealed_bilateral_families": 0,
        "semantic_p0": 0,
        "global_feature_p1": "22_OPEN_UNCHANGED",
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "NOT_PERFORMED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
