#!/usr/bin/env python3
"""Validate the closed TraitAutoPolicyRegistryV1 design contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/trait-auto-policy-registry-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/trait-auto-policy-registry-v1.schema.json"
DECISION_SCHEMA_REL = "schemas/language/trait-auto-policy-decision-v1.schema.json"
FIXTURE_SCHEMA_REL = "schemas/language/trait-auto-policy-fixtures-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/trait-auto-policy-registry-v1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Trait_Auto_Policy_Registry_Closure_R1.md"

OWNER_DIAGNOSTIC = "CONFORMANCE_AUTO_POLICY_OWNER_FORBIDDEN"
REGISTRY_DIAGNOSTIC = "CONFORMANCE_AUTO_POLICY_NOT_REGISTERED"
INPUT_DIAGNOSTIC = "CONFORMANCE_AUTO_POLICY_INPUT_EVIDENCE_UNSATISFIED"
EXPECTED_COUNTS = {"normal": 4, "boundary": 3, "reject": 6}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def reject(diagnostic: str) -> dict[str, Any]:
    return {"outcome": "REJECT", "diagnostic_or_null": diagnostic}


def policy_rows(contract: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (row["trait_id"], row["policy_version"]): row
        for row in contract.get("registry", {}).get("rows", [])
    }


def decide(contract: dict[str, Any], descriptor: dict[str, Any]) -> dict[str, Any]:
    if descriptor.get("declaration_owner") == "USER":
        return reject(OWNER_DIAGNOSTIC)

    version = descriptor.get("policy_version_or_null")
    row = policy_rows(contract).get((descriptor.get("trait_id"), version)) if version else None
    if not row:
        return reject(REGISTRY_DIAGNOSTIC)
    if any([
        descriptor.get("policy_id_or_null") != row.get("policy_id"),
        descriptor.get("policy_digest_or_null") != row.get("policy_digest"),
        descriptor.get("input_predicate_id_or_null") != row.get("input_predicate_id"),
    ]):
        return reject(REGISTRY_DIAGNOSTIC)

    if descriptor.get("action") == "TRAIT_OPT_IN":
        if descriptor.get("target_type_id_or_null") is not None or descriptor.get("target_kind_or_null") is not None:
            return reject(REGISTRY_DIAGNOSTIC)
        return {"outcome": "ADMIT_POLICY_BINDING", "diagnostic_or_null": None}

    evidence = descriptor.get("component_evidence_ids", [])
    inputs_ok = all([
        descriptor.get("target_type_id_or_null") is not None,
        descriptor.get("target_kind_or_null") in row.get("source_request_target_kinds", []),
        descriptor.get("input_graph_finite") is True,
        descriptor.get("policy_input_satisfied") is True,
        descriptor.get("direct_user_witness_count") == 0,
        descriptor.get("extension_evidence_count") == 0,
        descriptor.get("provider_search_count") == 0,
        descriptor.get("runtime_lookup_count") == 0,
        evidence == sorted(set(evidence)),
    ])
    if not inputs_ok:
        return reject(INPUT_DIAGNOSTIC)
    return {"outcome": "SYNTHESIZE_STATIC_WITNESS", "diagnostic_or_null": None}


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
            registry = jsonschema.RefResolver.from_schema(load(root / FIXTURE_SCHEMA_REL), store={
                "https://deeplus-lang.org/schema/r87/trait-auto-policy-decision-v1.schema.json": load(root / DECISION_SCHEMA_REL)
            })
            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(load(root / FIXTURE_SCHEMA_REL), resolver=registry).validate(fixture)
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover
            errors.append(f"SCHEMA_VALIDATION:{exc}")

    binding = contract.get("feature_p1_binding", {})
    if binding != {"id": "TCC-P1-005", "status": "OPEN", "new_feature_p1_count": 0}:
        errors.append("FEATURE_P1_BINDING_DRIFT")
    source = contract.get("source_surface", {})
    expected_source = {
        "trait_opt_in": "supports auto", "use": "by auto", "by_auto_body_allowed": False,
        "trait_declaration_creates_policy": False, "user_owned_trait_opt_in": "REJECT",
        "core_or_prelude_trait_requires_exact_registry_row": True,
        "unregistered_candidate_count": 0, "grammar_change_count": 0,
    }
    if source != expected_source:
        errors.append("SOURCE_SURFACE_POLICY_DRIFT")

    registry = contract.get("registry", {})
    rows = registry.get("rows", [])
    if registry.get("registry_revision") != "TraitAutoPolicyRegistryV1" or registry.get("owner") != "CORE_OR_PRELUDE_ONLY":
        errors.append("REGISTRY_IDENTITY_OR_OWNER_DRIFT")
    if registry.get("policy_count") != 2 or len(rows) != 2:
        errors.append("POLICY_COUNT_DRIFT")
    expected_traits = ["TraitId:core::Shareable", "TraitId:core::Transferable"]
    if [row.get("trait_id") for row in rows] != expected_traits:
        errors.append("POLICY_TRAIT_SET_OR_ORDER_DRIFT")
    for row in rows:
        observed_digest = hashlib.sha256(row.get("digest_recipe", "").encode("utf-8")).hexdigest()
        if row.get("policy_digest") != observed_digest:
            errors.append(f"POLICY_DIGEST_DRIFT:{row.get('trait_id')}")
        if row.get("excluded_evidence_sources") != [
            "USER_POLICY_DECLARATION", "EXTENSION_SHAPE", "PROVIDER", "SOURCE_ORDER", "IMPORT_ORDER", "RUNTIME_STATE"
        ]:
            errors.append(f"POLICY_EXCLUSION_DRIFT:{row.get('trait_id')}")
        termination = row.get("termination", {})
        if termination != {
            "finite_nominal_graph": True,
            "memoized_identity_subject_pairs": True,
            "cycle_detection": True,
            "metric": "UNVISITED_TYPE_ID_RESPONSIBILITY_RULE_ID_PAIRS",
        }:
            errors.append(f"POLICY_TERMINATION_DRIFT:{row.get('trait_id')}")

    residue = contract.get("hir_and_api_residue", {})
    if residue.get("mir_new_operation_count") != 0 or residue.get("mir_runtime_relookup_count") != 0:
        errors.append("RUNTIME_LOOKUP_OR_MIR_OPERATION_DRIFT")
    expected_fields = {
        "TraitAutoPolicyId", "PolicyVersion", "PolicyDigest", "TraitId", "TargetTypeId",
        "InputPredicateId", "InputEvidenceIds", "ConformanceId", "TraitWitnessIds", "DerivationDigest",
    }
    if set(residue.get("exact_fields", [])) != expected_fields:
        errors.append("HIR_API_RESIDUE_FIELD_DRIFT")
    if contract.get("governance") != {
        "semantic_p0": 0, "global_open_feature_p1": 22, "tcc_p1_005": "OPEN",
        "current_policy_count": 2, "user_defined_policy_count": 0,
        "product_lanes": "15/15_NOT_RUN", "github_mutation": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE_OVERCLAIM_OR_DRIFT")

    cases = fixture.get("cases", [])
    counts = Counter(case.get("class") for case in cases)
    if dict(counts) != EXPECTED_COUNTS:
        errors.append(f"FIXTURE_CLASS_COUNTS:{dict(counts)}")
    if len({case.get("case_id") for case in cases}) != len(cases):
        errors.append("FIXTURE_CASE_ID_DUPLICATE")
    for case in cases:
        observed = decide(contract, case.get("descriptor", {}))
        if observed != case.get("expected"):
            errors.append(f"FIXTURE_ORACLE:{case.get('case_id')}:{observed}")

    diagnostics = {row.get("diagnostic_id") for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    for diagnostic in (OWNER_DIAGNOSTIC, REGISTRY_DIAGNOSTIC, INPUT_DIAGNOSTIC):
        if diagnostic not in diagnostics:
            errors.append(f"DIAGNOSTIC_MISSING:{diagnostic}")
    predicates = {row.get("predicate_id"): row for row in all_rows(root, "spec/types/predicates/chunks")}
    predicate = predicates.get("TraitAutoPolicyAdmitted", {})
    if predicate.get("input_descriptor_schema") != DECISION_SCHEMA_REL:
        errors.append("PREDICATE_DESCRIPTOR_BINDING_MISSING")
    if set(predicate.get("diagnostic_refs", [])) != {OWNER_DIAGNOSTIC, REGISTRY_DIAGNOSTIC, INPUT_DIAGNOSTIC}:
        errors.append("PREDICATE_DIAGNOSTIC_BINDING_DRIFT")
    features = {row.get("feature_id"): row for row in all_rows(root, "spec/features/catalog/chunks")}
    feature = features.get("trait_witness_coherence_phase_a", {})
    refs = feature.get("normative_trace_refs", {})
    if "TraitAutoPolicyAdmitted" not in refs.get("predicates", []):
        errors.append("FEATURE_PREDICATE_TRACE_MISSING")
    if CONTRACT_REL not in feature.get("artifact_trace_refs", []):
        errors.append("FEATURE_ARTIFACT_TRACE_MISSING")

    frontend = load(root / "spec/frontend/frontend-model.json")
    automatic = frontend.get("trait_conformance_surface_contract", {}).get(
        "automatic_synthesis", {}
    )
    if automatic != {
        "trait_opt_in_surface": "supports auto",
        "use_surface": "by auto",
        "registry_identity": "TraitAutoPolicyRegistryV1",
        "registry_owner": "CORE_OR_PRELUDE_ONLY",
        "registry_key": ["TraitId", "PolicyVersion"],
        "current_policy_trait_ids": [
            "TraitId:core::Shareable", "TraitId:core::Transferable"
        ],
        "user_trait_declaration_creates_policy": False,
        "closed_registered_policy_required": True,
        "unregistered_policy_candidate_count": 0,
        "extension_shape_creates_policy": False,
        "provider_search_count": 0,
        "runtime_search_count": 0,
        "hir_exact_fields": [
            "TraitAutoPolicyId", "PolicyVersion", "PolicyDigest", "TraitId",
            "TargetTypeId", "InputPredicateId", "InputEvidenceIds",
            "ConformanceId", "TraitWitnessIds", "DerivationDigest",
        ],
    }:
        errors.append("FRONTEND_AUTOMATIC_SYNTHESIS_BINDING_DRIFT")

    api_schema = load(root / "schemas/language/module-api-digest.schema.json")
    api_contract = api_schema.get("x-deeplus-trait-auto-policy-contract", {})
    api_residue = api_schema.get("$defs", {}).get("traitAutoPolicyResidue", {})
    required_api_fields = {
        "mode", "policy_id", "policy_version", "policy_digest", "trait_id",
        "target_type_id_or_null", "input_predicate_id", "input_evidence_ids",
        "conformance_id_or_null", "trait_witness_ids",
        "derivation_digest_or_null",
    }
    if (
        set(api_residue.get("required", [])) != required_api_fields
        or api_contract.get("registry") != "TraitAutoPolicyRegistryV1"
        or api_contract.get("registry_owner") != "CORE_OR_PRELUDE_ONLY"
        or api_contract.get("current_policy_count") != 2
        or api_contract.get("runtime_lookup_count") != 0
        or api_contract.get("product_support") != "NOT_RUN"
    ):
        errors.append("MODULE_API_AUTO_POLICY_RESIDUE_DRIFT")

    mir_schema = load(root / "schemas/language/mir-responsibility.schema.json")
    mir_contract = mir_schema.get("x-deeplus-trait-auto-policy-contract", {})
    if mir_contract != {
        "registry": "TraitAutoPolicyRegistryV1",
        "current_policy_trait_ids": [
            "TraitId:core::Shareable", "TraitId:core::Transferable"
        ],
        "hir_sealed_fields": [
            "TraitAutoPolicyId", "PolicyVersion", "PolicyDigest", "TraitId",
            "TargetTypeId", "InputPredicateId", "InputEvidenceIds",
            "ConformanceId", "TraitWitnessIds", "DerivationDigest",
        ],
        "mir_new_operation_count": 0,
        "mir_registry_lookup_count": 0,
        "mir_provider_search_count": 0,
        "runtime_relookup_count": 0,
        "existing_residue_reused": [
            "ConformanceId", "TraitWitnessId", "ResponsibilityEvidenceId",
            "RegistryRevision", "DerivationDigest",
        ],
        "product_support": "NOT_RUN",
    }:
        errors.append("MIR_AUTO_POLICY_ZERO_LOOKUP_FENCE_DRIFT")

    responsibility = load(
        root / "spec/contracts/responsibility-identity-registry-r1.json"
    )
    responsibility_binding = responsibility.get("trait_auto_policy_binding", {})
    expected_binding_rows = [
        {
            "identity_id": row["trait_id"].removeprefix("TraitId:core::"),
            "trait_id": row["trait_id"],
            "policy_id": row["policy_id"],
            "policy_version": row["policy_version"],
            "policy_digest": row["policy_digest"],
            "input_predicate_id": row["input_predicate_id"],
        }
        for row in rows
    ]
    if responsibility_binding != {
        "registry": "TraitAutoPolicyRegistryV1",
        "policy_count": 2,
        "rows": expected_binding_rows,
        "source_declaration_creates_policy": False,
        "user_owned_policy_count": 0,
    }:
        errors.append("RESPONSIBILITY_AUTO_POLICY_BINDING_DRIFT")

    joined = "\n".join([
        (root / DECISION_REL).read_text(encoding="utf-8"),
        (root / "spec/language.md").read_text(encoding="utf-8"),
        (root / "spec/types/type-system.md").read_text(encoding="utf-8"),
        (root / "spec/mir/semantics.md").read_text(encoding="utf-8"),
        (root / "docs/grammar-reference/06-classes-traits-conformance-and-extensions.md").read_text(encoding="utf-8"),
    ])
    for token in ("TraitAutoPolicyRegistryV1", "CORE_OR_PRELUDE_ONLY", "TCC-P1-005", "15/15 NOT_RUN"):
        if token not in joined:
            errors.append(f"NORMATIVE_TEXT_BINDING_MISSING:{token}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    counts = Counter(case["class"] for case in load(root / FIXTURE_REL)["cases"])
    print(json.dumps({
        "schema": "deeplus.trait-auto-policy-registry-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_p1": "TCC-P1-005_OPEN_UNCHANGED",
        "current_policy_count": 2,
        "cases": dict(counts),
        "semantic_p0": 0,
        "global_feature_p1": "22_OPEN_UNCHANGED",
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "NOT_PERFORMED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
