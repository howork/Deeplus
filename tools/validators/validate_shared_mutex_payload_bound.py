#!/usr/bin/env python3
"""Validate the R35 SharedMutex payload-bound design contract.

This is a design-static reference validator.  It does not execute the Deeplus
parser, integrated checker, MIR lowering, xVM, runtime, formatter, or LSP.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE = "87115776365fcbe8870d2f631050db3e23194c9b"
PREDICATE_ID = "SharedMutexPayloadAdmitted"
CONSTRAINT_ID = "SharedMutexPayload"
FEATURE_ID = "shared_mutex_no_drop_minimum_profile"
DIAGNOSTIC_ID = "SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD"
DESCRIPTOR_SCHEMA = (
    "schemas/language/shared-mutex-payload-bound-fixtures-r1.schema.json"
    "#/$defs/payloadDescriptor"
)
PUBLIC_SIGNATURE = (
    "prelude intrinsic SharedMutex<T: SharedMutexPayload> { new(move T) -> "
    "SharedMutex<T>; withLock(#scoped (inout T) -> R throws E effects ε) -> "
    "R throws E effects ε effects state }"
)
CONTRACT_PATH = "spec/contracts/shared-mutex-payload-bound-r1.json"
SCHEMA_PATH = "schemas/language/shared-mutex-payload-bound-fixtures-r1.schema.json"
FIXTURE_PATH = "tests/fixtures/current/shared-mutex-payload-bound-r1.json"

EXPECTED_MUTATIONS = [
    "R35-SMP-MUT-001-REMOVE-PUBLIC-BOUND",
    "R35-SMP-MUT-002-RENAME-PUBLIC-BOUND",
    "R35-SMP-MUT-003-CLEAR-FEATURE-PREDICATE",
    "R35-SMP-MUT-004-REMOVE-PRIMARY-RELATION",
    "R35-SMP-MUT-005-SUBSTITUTE-PRIMARY-DIAGNOSTIC",
    "R35-SMP-MUT-006-ADMIT-DIRECT-LIFECYCLE",
    "R35-SMP-MUT-007-ADMIT-TRANSITIVE-LIFECYCLE",
    "R35-SMP-MUT-008-ADMIT-CLEANUP-KIND",
    "R35-SMP-MUT-009-ADMIT-CLEANUP-EFFECT",
    "R35-SMP-MUT-010-ADMIT-CLEANUP-ERROR",
    "R35-SMP-MUT-011-ADMIT-UNPROVEN-GENERIC",
    "R35-SMP-MUT-012-ACCEPT-USER-CONFORMANCE",
    "R35-SMP-MUT-013-ERASE-MODULE-API-BOUND",
    "R35-SMP-MUT-014-CONFUSE-WRAPPER-UNLOCK",
]

EXPECTED_REASON_ORDER = [
    "PAYLOAD_PROOF_NOT_CLOSED",
    "PAYLOAD_EVIDENCE_ROUTE_NOT_ADMITTED",
    "LIFECYCLE_OWNER_PRESENT",
    "CLEANUP_KIND_NOT_NONE",
    "CLEANUP_EFFECT_ROW_NONEMPTY",
    "CLEANUP_ERROR_SET_NONEMPTY",
    "CLEANUP_AUTHORITY_NONEMPTY",
    "CLEANUP_SUSPENSION_OR_CANCELLATION",
]


class ValidationFailure(RuntimeError):
    pass


def read_json(root: Path, relative: str) -> Any:
    path = root / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser error is evidence
        raise ValidationFailure(f"JSON_PARSE:{relative}:{exc}") from exc


def rows(root: Path, pattern: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(root.glob(pattern), key=lambda item: item.as_posix()):
        value = read_json(root, path.relative_to(root).as_posix())
        if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
            raise ValidationFailure(f"ROW_CATALOG_SHAPE:{path.relative_to(root)}")
        result.extend(value)
    return result


def unique_row(
    catalog: list[dict[str, Any]], key: str, value: str, failure: str
) -> dict[str, Any]:
    matches = [row for row in catalog if row.get(key) == value]
    if len(matches) != 1:
        raise ValidationFailure(f"{failure}:observed={len(matches)}")
    return matches[0]


def expected_admit() -> dict[str, Any]:
    return {
        "verdict": "ADMIT",
        "reason_or_null": None,
        "diagnostic_id_or_null": None,
        "culprit_path_or_null": None,
        "emitted_primary_count": 0,
        "later_candidate_status": "NOT_APPLICABLE",
    }


def expected_reject(reason: str, path: str = "$") -> dict[str, Any]:
    return {
        "verdict": "REJECT",
        "reason_or_null": reason,
        "diagnostic_id_or_null": DIAGNOSTIC_ID,
        "culprit_path_or_null": path,
        "emitted_primary_count": 1,
        "later_candidate_status": "NOT_EVALUATED",
    }


def evaluate(descriptor: dict[str, Any]) -> dict[str, Any]:
    """Closed design-reference decision procedure for one normalized summary."""

    nodes = descriptor.get("payload_nodes")
    proof_closed = (
        descriptor.get("normalized") is True
        and descriptor.get("proof_complete") is True
        and isinstance(nodes, list)
        and bool(nodes)
        and any(node.get("path") == "$" for node in nodes if isinstance(node, dict))
    )
    if descriptor.get("proof_origin") == "generic_bound":
        proof_closed = proof_closed and descriptor.get("bound_predicate_ids") == [
            PREDICATE_ID
        ]
    elif descriptor.get("bound_predicate_ids") not in ([], None):
        proof_closed = False
    if not proof_closed:
        return expected_reject("PAYLOAD_PROOF_NOT_CLOSED")

    if descriptor.get("user_conformance_evidence") is not False:
        return expected_reject("PAYLOAD_EVIDENCE_ROUTE_NOT_ADMITTED")

    ordered_nodes = sorted(nodes, key=lambda row: (row.get("path", ""), row.get("type_id", "")))
    for node in ordered_nodes:
        path = node.get("path", "$")
        checks = [
            (node.get("lifecycle_owner") is True, "LIFECYCLE_OWNER_PRESENT"),
            (node.get("cleanup_kind") != "none", "CLEANUP_KIND_NOT_NONE"),
            (bool(node.get("cleanup_effects")), "CLEANUP_EFFECT_ROW_NONEMPTY"),
            (bool(node.get("cleanup_errors")), "CLEANUP_ERROR_SET_NONEMPTY"),
            (bool(node.get("cleanup_authorities")), "CLEANUP_AUTHORITY_NONEMPTY"),
            (
                node.get("cleanup_suspends") is True
                or node.get("cleanup_cancellation") is True,
                "CLEANUP_SUSPENSION_OR_CANCELLATION",
            ),
        ]
        for detected, reason in checks:
            if detected:
                return expected_reject(reason, path)
    return expected_admit()


def check_fixture_schema(schema: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if schema.get("$defs", {}).get("payloadDescriptor") is None:
        errors.append("DESCRIPTOR_SCHEMA_MISSING")
    properties = schema.get("properties", {})
    for name, size in (("semantic_cases", 12), ("mutation_matrix", 14)):
        prop = properties.get(name, {})
        if prop.get("minItems") != size or prop.get("maxItems") != size:
            errors.append(f"SCHEMA_{name.upper()}_CARDINALITY")

    try:
        from jsonschema import Draft202012Validator

        schema_errors = sorted(
            Draft202012Validator(schema).iter_errors(fixture),
            key=lambda error: list(error.absolute_path),
        )
        errors.extend(
            "JSON_SCHEMA:"
            + "/".join(str(part) for part in error.absolute_path)
            + ":"
            + error.message
            for error in schema_errors
        )
    except ImportError:
        required = {"schema", "baseline", "product_execution", "semantic_cases", "mutation_matrix"}
        if set(fixture) != required:
            errors.append("FIXTURE_TOP_LEVEL_SHAPE")
    return errors


def check_semantic_cases(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = fixture.get("semantic_cases", [])
    ids = [case.get("case_id") for case in cases]
    if len(cases) != 12 or len(set(ids)) != 12:
        errors.append("SEMANTIC_CASE_CARDINALITY_OR_DUPLICATE")
    if Counter(case.get("class") for case in cases) != {
        "positive": 3,
        "boundary": 3,
        "negative": 6,
    }:
        errors.append("SEMANTIC_CLASS_CARDINALITY")

    for case in cases:
        descriptor = case.get("descriptor", {})
        nodes = descriptor.get("payload_nodes", [])
        node_keys = [(node.get("path"), node.get("type_id")) for node in nodes]
        if node_keys != sorted(node_keys):
            errors.append(f"PAYLOAD_NODE_ORDER:{case.get('case_id')}")
        if len({node.get("path") for node in nodes}) != len(nodes):
            errors.append(f"PAYLOAD_NODE_PATH_DUPLICATE:{case.get('case_id')}")
        observed = evaluate(descriptor)
        if observed != case.get("expected"):
            errors.append(
                f"SEMANTIC_EXPECTATION_MISMATCH:{case.get('case_id')}:"
                f"observed={observed}:expected={case.get('expected')}"
            )
    return errors


def canonical_projection(root: Path) -> dict[str, Any]:
    prelude = unique_row(
        rows(root, "library/prelude/signatures/chunks/*.json"),
        "entry_id",
        "sharedmutex_t",
        "SHAREDMUTEX_PRELUDE_ROW",
    )
    feature = unique_row(
        rows(root, "spec/features/catalog/chunks/*.json"),
        "feature_id",
        FEATURE_ID,
        "SHAREDMUTEX_FEATURE_ROW",
    )
    predicate = unique_row(
        rows(root, "spec/types/predicates/chunks/*.json"),
        "predicate_id",
        PREDICATE_ID,
        "SHAREDMUTEX_PREDICATE_ROW",
    )
    relations = [
        row
        for row in rows(root, "spec/diagnostics/relations/chunks/*.json")
        if row.get("predicate_id") == PREDICATE_ID and row.get("relation") == "primary"
    ]
    diagnostic = unique_row(
        rows(root, "spec/diagnostics/catalog/chunks/*.json"),
        "diagnostic_id",
        DIAGNOSTIC_ID,
        "SHAREDMUTEX_DIAGNOSTIC_ROW",
    )
    module_schema = read_json(root, "schemas/language/module-api-digest.schema.json")
    module_symbol_properties = (
        module_schema.get("properties", {})
        .get("symbols", {})
        .get("items", {})
        .get("properties", {})
    )
    shared_state = read_json(root, "spec/contracts/shared-state-coherence.json")
    rules = {row.get("rule_id"): row for row in shared_state.get("rules", [])}
    pointer = read_json(root, "current/current-pointer.json")
    return {
        "prelude": prelude,
        "feature": feature,
        "predicate": predicate,
        "primary_relations": relations,
        "diagnostic": diagnostic,
        "module_schema": module_schema,
        "module_bound_property": module_symbol_properties.get(
            "type_parameter_predicate_bounds"
        ),
        "module_bound_definition": module_schema.get("$defs", {}).get(
            "typeParameterPredicateBoundResidue"
        ),
        "ssc_r006": rules.get("SSC-R006", {}).get("contract"),
        "ssc_r008": rules.get("SSC-R008", {}).get("contract"),
        "pointer": pointer,
    }


def artifact_errors(projection: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prelude = projection["prelude"]
    if prelude.get("signatures") != [PUBLIC_SIGNATURE] or prelude.get(
        "signature_records"
    ) != [
        {
            "text": PUBLIC_SIGNATURE,
            "dialect": "prelude_intrinsic",
            "grammar_root": None,
            "schema": "deeplus.prelude-intrinsic-signature/r51f3",
        }
    ]:
        errors.append("PUBLIC_SIGNATURE_BOUND_MISMATCH")

    predicates = projection["feature"].get("normative_trace_refs", {}).get(
        "predicates"
    )
    if predicates != [PREDICATE_ID]:
        errors.append("FEATURE_PREDICATE_BINDING_MISMATCH")

    predicate = projection["predicate"]
    predicate_ok = (
        predicate.get("source_name") == CONSTRAINT_ID
        and predicate.get("input_descriptor") == "SharedMutexPayloadDescriptorR1"
        and predicate.get("input_descriptor_schema") == DESCRIPTOR_SCHEMA
        and predicate.get("feature_refs") == [FEATURE_ID]
        and predicate.get("diagnostic_refs") == [DIAGNOSTIC_ID]
        and predicate.get("active_primary_diagnostic") == DIAGNOSTIC_ID
        and predicate.get("predicate_maturity") == "design_algorithm"
        and predicate.get("emission_eligible") is True
        and predicate.get("product_support") == "NOT_RUN"
    )
    if not predicate_ok:
        errors.append("PREDICATE_CONTRACT_MISMATCH")

    relations = projection["primary_relations"]
    if relations != [
        {
            "violation_id": f"{PREDICATE_ID}:default",
            "predicate_id": PREDICATE_ID,
            "diagnostic_id": DIAGNOSTIC_ID,
            "relation": "primary",
        }
    ]:
        errors.append("PRIMARY_DIAGNOSTIC_RELATION_MISMATCH")

    diagnostic = projection["diagnostic"]
    if not (
        diagnostic.get("diagnostic_status") == "active"
        and diagnostic.get("diagnostic_maturity") == "active"
        and diagnostic.get("stage") == "checker"
        and diagnostic.get("fixit_kind") == "manual_review"
        and diagnostic.get("product_support") == "NOT_RUN"
    ):
        errors.append("EXISTING_DIAGNOSTIC_CONTRACT_MISMATCH")

    bound_property = projection.get("module_bound_property")
    required_fields = [
        "parameter_id",
        "predicate_id",
        "predicate_contract_sha256",
    ]
    bound_item = bound_property.get("items", {}) if isinstance(bound_property, dict) else {}
    if bound_item.get("$ref") == "#/$defs/typeParameterPredicateBoundResidue":
        bound_item = projection.get("module_bound_definition") or {}
    if bound_item.get("$ref") == "#/$defs/typeParameterPredicateBoundResidue":
        bound_item = (
            projection["module_schema"]
            .get("$defs", {})
            .get("typeParameterPredicateBoundResidue", {})
        )
    bound_properties = bound_item.get("properties", {})
    digest_pattern = bound_properties.get("predicate_contract_sha256", {}).get("pattern")
    if not (
        isinstance(bound_property, dict)
        and bound_property.get("type") == "array"
        and bound_property.get("uniqueItems") is True
        and bound_item.get("type") == "object"
        and bound_item.get("additionalProperties") is False
        and bound_item.get("required") == required_fields
        and set(bound_properties) == set(required_fields)
        and digest_pattern == "^[0-9a-f]{64}$"
    ):
        errors.append("MODULE_API_BOUND_PROPERTY_MISSING")

    r006 = projection.get("ssc_r006") or {}
    if not (
        r006.get("public_constraint") == CONSTRAINT_ID
        and r006.get("internal_predicate") == PREDICATE_ID
        and "not Trait" in str(r006.get("constraint_kind"))
        and "no user conformance" in str(r006.get("constraint_kind"))
        and r006.get("generic_bound_required") is True
        and r006.get("public_api_identity_retains_bound") is True
        and r006.get("admission_precedes_move_commit") is True
        and r006.get("primary_diagnostic") == DIAGNOSTIC_ID
    ):
        errors.append("SHARED_STATE_PAYLOAD_BOUND_FENCE")

    expected_unlock = {
        "cleanup_owner": "withLock call",
        "unlock_count": 1,
        "terminal_paths": ["return", "Error", "Defect", "Cancellation"],
        "unlock_failure": "not admitted",
        "body_failure_remains_primary": True,
    }
    if projection.get("ssc_r008") != expected_unlock:
        errors.append("SHARED_STATE_UNLOCK_FENCE")

    pointer = projection["pointer"]
    lanes = pointer.get("product_lanes", {})
    open_actions = pointer.get("open_actions", [])
    feature_p1 = [
        row
        for row in open_actions
        if str(row.get("id", "")).startswith(("CE-C-P1-", "CE-E-P1-", "TCC-P1-", "SFD-P1-"))
    ]
    m13 = [row for row in open_actions if str(row.get("id", "")).startswith("M13-A")]
    if not (
        len(feature_p1) == 22
        and len(m13) == 4
        and len(lanes) == 15
        and set(lanes.values()) == {"NOT_RUN"}
    ):
        errors.append("GLOBAL_STATUS_FENCE")
    return errors


def mutation_reason(
    mutation: dict[str, Any], projection: dict[str, Any], case_map: dict[str, dict[str, Any]]
) -> str | None:
    operation = mutation["operation"]
    if operation in {
        "REMOVE_PUBLIC_BOUND",
        "RENAME_PUBLIC_BOUND",
        "CLEAR_FEATURE_PREDICATE_REF",
        "REMOVE_PRIMARY_RELATION",
        "SUBSTITUTE_PRIMARY_DIAGNOSTIC",
        "ERASE_MODULE_API_BOUND",
    }:
        mutant = copy.deepcopy(projection)
        if operation == "REMOVE_PUBLIC_BOUND":
            text = PUBLIC_SIGNATURE.replace("T: SharedMutexPayload", "T")
            mutant["prelude"]["signatures"] = [text]
            mutant["prelude"]["signature_records"][0]["text"] = text
        elif operation == "RENAME_PUBLIC_BOUND":
            text = PUBLIC_SIGNATURE.replace("SharedMutexPayload", "Plain")
            mutant["prelude"]["signatures"] = [text]
            mutant["prelude"]["signature_records"][0]["text"] = text
        elif operation == "CLEAR_FEATURE_PREDICATE_REF":
            mutant["feature"]["normative_trace_refs"]["predicates"] = []
        elif operation == "REMOVE_PRIMARY_RELATION":
            mutant["primary_relations"] = []
        elif operation == "SUBSTITUTE_PRIMARY_DIAGNOSTIC":
            mutant["primary_relations"][0]["diagnostic_id"] = (
                "SHARED_CELL_REQUIRES_PLAIN_PAYLOAD"
            )
        elif operation == "ERASE_MODULE_API_BOUND":
            mutant["module_bound_property"] = None
        observed = artifact_errors(mutant)
        return observed[0] if observed else None

    base = copy.deepcopy(case_map[mutation["base_case_id_or_null"]])
    if operation == "FORGE_USER_CONFORMANCE_AND_EXPECT_ADMIT":
        base["descriptor"]["user_conformance_evidence"] = True
        base["expected"] = expected_admit()
    elif operation == "FORCE_WRAPPER_UNLOCK_REJECTION":
        base["expected"] = expected_reject("CLEANUP_KIND_NOT_NONE")
    elif operation == "FORCE_EXPECTED_ADMIT":
        base["expected"] = expected_admit()
    else:
        return "UNKNOWN_MUTATION_OPERATION"
    return None if evaluate(base["descriptor"]) == base["expected"] else "SEMANTIC_EXPECTATION_MISMATCH"


def check_mutations(
    fixture: dict[str, Any], projection: dict[str, Any]
) -> tuple[list[str], list[dict[str, str]]]:
    errors: list[str] = []
    mutations = fixture.get("mutation_matrix", [])
    observed_ids = [row.get("mutation_id") for row in mutations]
    if observed_ids != EXPECTED_MUTATIONS:
        errors.append("MUTATION_IDENTITY_OR_ORDER")
    case_map = {row["case_id"]: row for row in fixture.get("semantic_cases", [])}
    receipts: list[dict[str, str]] = []
    for mutation in mutations:
        try:
            observed = mutation_reason(mutation, projection, case_map)
        except Exception as exc:  # pragma: no cover - captured as failed mutation
            observed = f"MUTATION_EXECUTION:{exc}"
        expected = mutation.get("expected_validator_reason")
        status = "PASS" if observed == expected else "FAIL"
        receipts.append(
            {
                "mutation_id": mutation.get("mutation_id", "UNKNOWN"),
                "status": status,
                "observed_reason": str(observed),
            }
        )
        if status != "PASS":
            errors.append(
                f"MUTATION_SURVIVED:{mutation.get('mutation_id')}:"
                f"expected={expected}:observed={observed}"
            )
    return errors, receipts


def check_contract(contract: dict[str, Any], fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("baseline", {}).get("commit") != BASELINE:
        errors.append("CONTRACT_BASELINE")
    surface = contract.get("public_surface", {})
    if not (
        surface.get("constraint_id") == CONSTRAINT_ID
        and surface.get("checker_predicate_id") == PREDICATE_ID
        and surface.get("canonical_signature") == PUBLIC_SIGNATURE
        and surface.get("source_trait") is False
        and surface.get("user_conformable") is False
    ):
        errors.append("CONTRACT_PUBLIC_SURFACE")
    algorithm = contract.get("admission_algorithm", {})
    if algorithm.get("preflight_order", []) + algorithm.get("per_node_order", []) != EXPECTED_REASON_ORDER:
        errors.append("CONTRACT_REASON_ORDER")
    if contract.get("diagnostic_binding", {}).get("primary_diagnostic") != DIAGNOSTIC_ID:
        errors.append("CONTRACT_DIAGNOSTIC")
    module_api = contract.get("module_api_residue", {})
    if not (
        module_api.get("property") == "type_parameter_predicate_bounds"
        and module_api.get("row_fields")
        == ["parameter_id", "predicate_id", "predicate_contract_sha256"]
        and module_api.get("required_row", {}).get("parameter_id") == "T"
        and module_api.get("required_row", {}).get("predicate_id") == PREDICATE_ID
    ):
        errors.append("CONTRACT_MODULE_API_RESIDUE")
    fixture_contract = contract.get("fixture_contract", {})
    if not (
        fixture_contract.get("semantic_case_count") == 12
        and fixture_contract.get("semantic_class_counts")
        == {"positive": 3, "boundary": 3, "negative": 6}
        and fixture_contract.get("mutation_count") == 14
        and len(fixture.get("semantic_cases", [])) == 12
        and len(fixture.get("mutation_matrix", [])) == 14
    ):
        errors.append("CONTRACT_FIXTURE_BINDING")
    status = contract.get("status_fences", {})
    if not (
        status.get("semantic_p0") == 0
        and status.get("open_feature_p1") == 22
        and status.get("open_action_count") == 4
        and status.get("product_lanes") == "15_OF_15_NOT_RUN"
        and all(
            status.get(key) == "NOT_RUN"
            for key in (
                "production_parser",
                "production_checker",
                "production_hir_mir",
                "runtime_xvm",
                "formatter_lsp",
            )
        )
    ):
        errors.append("CONTRACT_STATUS_FENCE")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        contract = read_json(root, CONTRACT_PATH)
        schema = read_json(root, SCHEMA_PATH)
        fixture = read_json(root, FIXTURE_PATH)
        projection = canonical_projection(root)
        errors = []
        errors.extend(check_fixture_schema(schema, fixture))
        errors.extend(check_contract(contract, fixture))
        errors.extend(check_semantic_cases(fixture))
        errors.extend(artifact_errors(projection))
        mutation_errors, mutation_receipts = check_mutations(fixture, projection)
        errors.extend(mutation_errors)
    except ValidationFailure as exc:
        errors = [str(exc)]
        mutation_receipts = []
    except Exception as exc:  # pragma: no cover - one deterministic failure receipt
        errors = [f"VALIDATOR_INTERNAL:{type(exc).__name__}:{exc}"]
        mutation_receipts = []

    result = {
        "schema": "deeplus.shared-mutex-payload-bound-validation-receipt/r1",
        "baseline": BASELINE,
        "verdict": "PASS" if not errors else "FAIL",
        "semantic_case_count": 12,
        "semantic_class_counts": {"positive": 3, "boundary": 3, "negative": 6},
        "mutation_count": 14,
        "mutation_pass_count": sum(
            receipt.get("status") == "PASS" for receipt in mutation_receipts
        ),
        "semantic_p0": 0,
        "open_feature_p1": 22,
        "open_action_count": 4,
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
        "errors": errors,
        "mutation_receipts": mutation_receipts,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
