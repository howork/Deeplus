#!/usr/bin/env python3
"""Validate the R30 responsibility identity registry design-static closure."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/responsibility-identity-registry-r1.json"
SCHEMA_REL = "schemas/language/responsibility-identity-registry-r1.schema.json"
FIXTURE_REL = "tests/fixtures/current/responsibility-identity-registry-r1.json"
INPUT_SCHEMA_REL = "schemas/language/responsibility-identity-input-r1.schema.json"
INPUT_FIXTURE_REL = "tests/fixtures/current/responsibility-identity-input-r1.json"
PREDICATE_METADATA_REL = "spec/types/predicates/catalog-metadata.json"
FEATURE_REL = "spec/features/catalog/chunks/part-0025.json"
RELATION_REL = "spec/diagnostics/relations/chunks/part-0009.json"

RESPONSIBILITY_PREDICATES = [
    "PlainValueAdmissible",
    "ShareableObservationSafe",
    "TransferableAcrossIsolation",
    "CopyValueAdmissible",
]
PREDICATE_RULE_IDS = {
    "PlainValueAdmissible": "PlainValue",
    "ShareableObservationSafe": "Shareable",
    "TransferableAcrossIsolation": "Transferable",
    "CopyValueAdmissible": "CopyValue",
}

IDENTITY_IDS = [
    "PlainValue",
    "Shareable",
    "Transferable",
    "CopyValue",
    "Clone",
    "DeepClone",
]
IDENTITY_KINDS = {
    "PlainValue": "SEALED_INTRINSIC_PREDICATE",
    "Shareable": "SEALED_COMPILER_GOVERNED_RESPONSIBILITY_TRAIT",
    "Transferable": "SEALED_COMPILER_GOVERNED_RESPONSIBILITY_TRAIT",
    "CopyValue": "INTERNAL_SEALED_COPY_PREDICATE",
    "Clone": "PUBLIC_BEHAVIORAL_TRAIT",
    "DeepClone": "RESERVED_PREVIEW_BEHAVIORAL_TRAIT",
}
EXPECTED_P1 = [
    "CE-C-P1-001",
    "CE-C-P1-002",
    "CE-C-P1-003",
    "CE-C-P1-004",
    "CE-C-P1-005",
    "CE-C-P1-006",
    "CE-E-P1-001",
    "CE-E-P1-002",
    "CE-E-P1-003",
    "CE-E-P1-004",
    "CE-E-P1-005",
    "CE-E-P1-006",
    "CE-E-P1-007",
    "CE-E-P1-008",
    "TCC-P1-002",
    "TCC-P1-003",
    "TCC-P1-004",
    "TCC-P1-005",
    "TCC-P1-006",
    "TCC-P1-007",
    "TCC-P1-008",
    "SFD-P1-009",
]
EXPECTED_M13 = ["M13-A002", "M13-A003", "M13-A004", "M13-A005"]
PRODUCT_LANES = [
    "rust_frontend_lexer",
    "rust_frontend_parser",
    "rust_hir_lowering",
    "rust_integrated_checker",
    "deeplus_mir_lowering",
    "xvm_bytecode_emitter",
    "xvm_interpreter",
    "cranelift_object_aot_backend",
    "cranelift_jit_backend",
    "formatter_lsp",
    "stdlib_provider_runner",
    "official_tooling",
    "independent_conformance",
    "cross_backend_conformance",
    "actual_user_team_study",
]
EXISTING_DIAGNOSTICS = [
    "PLAIN_IS_NOT_LAYOUT_SAFE",
    "PLAIN_IS_NOT_JSONVALUE",
    "PLAIN_IS_NOT_DYNAMIC",
    "PLAIN_IS_PLAINVALUE_ALIAS",
    "SHAREABLE_DOES_NOT_CREATE_ALIAS",
    "SHARED_WRAPPER_DOES_NOT_IMPLY_TRANSFERABLE",
    "COPYABLE_REMOVED_USE_PLAIN_OR_SHARED",
    "DUPLICABLE_REMOVED_USE_EXPLICIT_RESPONSIBILITY",
    "ALIASABLE_REMOVED_USE_SHARED_OR_PLAIN",
    "TYPE_PLAINDATA_REMOVED_USE_PLAIN",
    "PROTOTYPE_DEEP_DERIVATION_REQUIRES_DEEP_CLONE_LAW",
    "CONFORMANCE_AUTO_POLICY_NOT_REGISTERED",
]
NEW_DIAGNOSTICS = [
    "RESPONSIBILITY_IDENTITY_UNRESOLVED",
    "RESPONSIBILITY_EVIDENCE_NOT_ADMISSIBLE",
]
DESCRIPTOR_FIELDS = [
    "ResponsibilityRuleId",
    "TypeId",
    "EvidenceKind",
    "RegistryRevision",
    "DerivationDigest",
    "TraitWitnessIdOrNull",
]
BEHAVIORAL_DESCRIPTOR_FIELDS = [
    "ErrorSetIdOrNull",
    "EffectRowIdOrNull",
    "ResultAcquisitionPlanIdOrNull",
    "CleanupPlanIdOrNull",
]
HIR_FIELDS = [
    "ResponsibilityRuleId",
    "ResponsibilityEvidenceId",
    "TypeId",
    "EvidenceKind",
    "RegistryRevision",
    "DerivationDigest",
    "TraitWitnessIdOrNull",
    "ErrorSetIdOrNull",
    "EffectRowIdOrNull",
    "ResultAcquisitionPlanIdOrNull",
    "CleanupPlanIdOrNull",
    "OwnerIdOrNull",
    "RegionIdOrNull",
    "DestinationIsolationDomainIdOrNull",
    "SourceProvenance",
]
API_FIELDS = [
    "ResponsibilityRuleId",
    "TypeId",
    "EvidenceKind",
    "RegistryRevision",
    "DerivationDigest",
    "TraitWitnessIdOrNull",
    "ErrorSetIdOrNull",
    "EffectRowIdOrNull",
]
MIR_FIELDS = [
    "ResponsibilityRuleId",
    "ResponsibilityEvidenceId",
    "TypeId",
    "EvidenceKind",
    "RegistryRevision",
    "DerivationDigest",
    "TraitWitnessIdOrNull",
    "ErrorSetIdOrNull",
    "EffectRowIdOrNull",
    "ResultAcquisitionPlanIdOrNull",
    "CleanupPlanIdOrNull",
    "OwnerIdOrNull",
    "RegionIdOrNull",
    "DestinationIsolationDomainIdOrNull",
    "SourceOriginId",
]
REJECTED_SPELLINGS = {
    "PlainValue": (["Plain"], "RESPONSIBILITY_IDENTITY_UNRESOLVED"),
    "Sendable": (["Transferable"], "RESPONSIBILITY_IDENTITY_UNRESOLVED"),
    "ShareSafe": (["Shareable"], "RESPONSIBILITY_IDENTITY_UNRESOLVED"),
    "Copyable": (
        ["Plain", "Shared<T>", "clone", "move"],
        "COPYABLE_REMOVED_USE_PLAIN_OR_SHARED",
    ),
    "Duplicable": (
        ["Plain", "Shared<T>", "clone", "move"],
        "DUPLICABLE_REMOVED_USE_EXPLICIT_RESPONSIBILITY",
    ),
    "Aliasable": (
        ["Plain", "Shared<T>", "Shareable", "move", "clone"],
        "ALIASABLE_REMOVED_USE_SHARED_OR_PLAIN",
    ),
    "PlainData": (["Plain"], "TYPE_PLAINDATA_REMOVED_USE_PLAIN"),
}
CHECK_IDS = [
    "R30_SCHEMA_CONTRACT",
    "R30_IDENTITY_SET_EXACT",
    "R30_AXIS_INDEPENDENCE",
    "R30_IMPLICATION_ZEROES",
    "R30_TERMINATING_RESOLUTION",
    "R30_EVIDENCE_RESIDUE",
    "R30_DIAGNOSTIC_IDENTITY",
    "R30_FIXTURE_MATRIX",
    "R30_MUTATION_REJECTION",
    "R30_GOVERNANCE_FENCE",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_diagnostics(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("*.json")):
        value = load_json(path)
        if not isinstance(value, list):
            raise ValueError(f"diagnostic chunk is not an array: {path}")
        rows.extend(row for row in value if isinstance(row, dict))
    return rows


def load_chunk_rows(root: Path, directory: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / directory).glob("*.json")):
        value = load_json(path)
        if not isinstance(value, list):
            raise ValueError(f"catalog chunk is not an array: {path}")
        rows.extend(row for row in value if isinstance(row, dict))
    return rows


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def resolve_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"external schema reference is not admitted: {ref}")
    value: Any = root_schema
    for part in ref[2:].split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    if not isinstance(value, dict):
        raise ValueError(f"schema reference is not an object: {ref}")
    return value


def schema_errors(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str = "$",
) -> list[str]:
    """Validate the dependency-free JSON Schema subset used by this contract."""
    if "$ref" in schema:
        return schema_errors(value, resolve_ref(root_schema, schema["$ref"]), root_schema, path)

    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        admitted = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(json_type_matches(value, item) for item in admitted):
            return [f"SCHEMA_TYPE:{path}:{admitted}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"SCHEMA_CONST:{path}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"SCHEMA_ENUM:{path}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in value:
                errors.append(f"SCHEMA_REQUIRED:{path}.{name}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for name in value:
                if name not in properties:
                    errors.append(f"SCHEMA_ADDITIONAL:{path}.{name}")
        for name, child_schema in properties.items():
            if name in value:
                errors.extend(
                    schema_errors(value[name], child_schema, root_schema, f"{path}.{name}")
                )
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"SCHEMA_MIN_ITEMS:{path}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"SCHEMA_MAX_ITEMS:{path}")
        if schema.get("uniqueItems"):
            keys = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(keys) != len(set(keys)):
                errors.append(f"SCHEMA_UNIQUE_ITEMS:{path}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    schema_errors(item, item_schema, root_schema, f"{path}[{index}]")
                )
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"SCHEMA_MIN_LENGTH:{path}")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            errors.append(f"SCHEMA_PATTERN:{path}")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"SCHEMA_MINIMUM:{path}")
    return errors


def contract_errors(
    contract: dict[str, Any],
    schema: dict[str, Any],
    diagnostic_rows: list[dict[str, Any]],
) -> list[str]:
    errors = schema_errors(contract, schema, schema)

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(
        contract.get("schema") == "deeplus.responsibility-identity-registry/r1",
        "CONTRACT_SCHEMA",
    )
    require(
        contract.get("baseline")
        == {
            "commit": "87115776365fcbe8870d2f631050db3e23194c9b",
            "tree": "2452f0a6be1e1391b3678dafa86987059b115ec7",
        },
        "CONTRACT_BASELINE",
    )
    require(contract.get("gap", {}).get("gap_id") == "IR-OWN-P1-023", "CONTRACT_GAP")
    surface = contract.get("source_surface", {})
    require(
        surface.get("grammar_change_required") is False
        and surface.get("grammar_production_change_count") == 0
        and surface.get("new_source_spelling_count") == 0,
        "CONTRACT_NO_GRAMMAR_CHANGE",
    )

    identities = contract.get("identities", [])
    require(isinstance(identities, list), "IDENTITY_ARRAY")
    if not isinstance(identities, list):
        identities = []
    observed_ids = [row.get("identity_id") for row in identities if isinstance(row, dict)]
    require(observed_ids == IDENTITY_IDS, "IDENTITY_SET_EXACT")
    require(len(observed_ids) == len(set(observed_ids)) == 6, "IDENTITY_SET_UNIQUE")
    by_id = {
        row.get("identity_id"): row
        for row in identities
        if isinstance(row, dict) and isinstance(row.get("identity_id"), str)
    }
    require(
        all(by_id.get(identity_id, {}).get("kind") == kind for identity_id, kind in IDENTITY_KINDS.items()),
        "IDENTITY_KIND_EXACT",
    )
    axes = [row.get("axis_id") for row in identities if isinstance(row, dict)]
    axis_model = contract.get("axis_model", {})
    require(
        len(axes) == len(set(axes)) == 6
        and axis_model.get("axes_are_independent") is True
        and axis_model.get("implicit_cross_axis_derivation_count") == 0,
        "AXIS_INDEPENDENCE",
    )
    plain = by_id.get("PlainValue", {})
    require(
        plain.get("public_spelling_or_null") == "Plain"
        and plain.get("public_aliases") == []
        and plain.get("user_direct_conformance") == "FORBIDDEN",
        "PLAIN_IDENTITY_EXACT",
    )
    for identity_id in ("Shareable", "Transferable"):
        row = by_id.get(identity_id, {})
        require(
            row.get("user_direct_conformance") == "FORBIDDEN"
            and row.get("auto_policy") == "CLOSED_TERMINATING_STRUCTURAL_AUTO"
            and row.get("evidence_mode") == "EXACT_COMPILER_SYNTHESIZED_TRAIT_WITNESS",
            f"{identity_id.upper()}_SEALED_AUTO_POLICY",
        )
    copy_value = by_id.get("CopyValue", {})
    require(
        copy_value.get("public_spelling_or_null") is None
        and copy_value.get("public_aliases") == []
        and copy_value.get("capture_spelling_or_null") == "copy",
        "COPY_PUBLIC_TRAIT",
    )
    clone = by_id.get("Clone", {})
    clone_behavior = clone.get("behavior", {})
    require(
        clone.get("public_spelling_or_null") == "Clone"
        and clone.get("evidence_mode") == "EXACT_SELECTED_TRAIT_WITNESS"
        and clone.get("runtime_relookup_count") == 0
        and clone_behavior.get("source_access_or_null") == "BORROWED"
        and clone_behavior.get("result_contract_or_null") == "SAME_TYPE_INDEPENDENT_RESULT"
        and clone_behavior.get("maximum_throws") == ["AllocationError"]
        and clone_behavior.get("maximum_effects") == ["allocate"]
        and clone_behavior.get("suspension_or_null") == "FORBIDDEN"
        and clone_behavior.get("cancellation_or_null") == "FORBIDDEN"
        and clone_behavior.get("narrower_implementation_allowed") is True,
        "CLONE_BEHAVIOR_EXACT",
    )
    deep_clone = by_id.get("DeepClone", {})
    deep_behavior = deep_clone.get("behavior", {})
    require(
        deep_clone.get("availability") == "RESERVED_PREVIEW_NONACTIVATABLE"
        and deep_clone.get("user_direct_conformance") == "FORBIDDEN"
        and deep_behavior.get("status") == "RESERVED_PREVIEW_BLOCKED"
        and deep_behavior.get("pending_policy_axes") == ["GRAPH", "CYCLE", "ALIAS"],
        "DEEPCLONE_ACTIVATION",
    )

    matrix = contract.get("implication_matrix", {})
    require(list(matrix) == IDENTITY_IDS, "IMPLICATION_MATRIX_KEYS")
    off_diagonal_true = 0
    diagonal_false = 0
    for source in IDENTITY_IDS:
        row = matrix.get(source, {})
        require(list(row) == IDENTITY_IDS, "IMPLICATION_ROW_KEYS")
        for target in IDENTITY_IDS:
            value = row.get(target)
            if source == target:
                diagonal_false += value is not True
            else:
                off_diagonal_true += value is True
    require(diagonal_false == 0, "IMPLICATION_REFLEXIVE")
    require(off_diagonal_true == 0, "IMPLICATION_OFF_DIAGONAL")
    plain_boundary = contract.get("plain_boundary", {})
    require(
        plain_boundary.get("public_spelling") == "Plain"
        and plain_boundary.get("internal_formal_identity") == "PlainValue"
        and plain_boundary.get("sole_public_spelling") is True,
        "PLAIN_SOURCE_SPELLING_EXACT",
    )
    plain_implications = plain_boundary.get("implies", {})
    require(
        list(plain_implications)
        == [
            "CopyValue",
            "Shareable",
            "Transferable",
            "layout_safe",
            "abi_safe",
            "json_value",
            "dyn_value",
        ]
        and all(value is False for value in plain_implications.values()),
        "PLAIN_EXTERNAL_IMPLICATION_ZEROES",
    )

    lifecycle = contract.get("lifecycle_boundary", {})
    require(
        lifecycle.get("internal_lifecycle_classes") == ["Reusable", "Affine", "Resource"]
        and lifecycle.get("public_trait_identity_count") == 0
        and lifecycle.get("cleanup_trait_dispatch_count") == 0,
        "LIFECYCLE_CLASS_BOUNDARY",
    )
    shared = contract.get("shared_handle_boundary", {})
    require(
        shared.get("spelling") == "Shared<T>"
        and shared.get("is_responsibility_identity") is False
        and shared.get("alias_creation_authority") is True
        and shared.get("shareable_observation_proof_is_separate") is True
        and shared.get("transferable_payload_proof_is_synthesized") is False,
        "SHARED_HANDLE_BOUNDARY",
    )

    predicate_input_contract = contract.get("predicate_input_contract", {})
    require(
        predicate_input_contract
        == {
            "descriptor": "ResponsibilityIdentityInputR1",
            "schema_path": INPUT_SCHEMA_REL,
            "fixture_path": INPUT_FIXTURE_REL,
            "closed_object": True,
            "predicate_ids": RESPONSIBILITY_PREDICATES,
            "case_count": 12,
            "classes_per_predicate": ["positive", "boundary", "negative"],
        },
        "INPUT_CONTRACT_EXACT",
    )

    rejected_rows = contract.get("rejected_spellings", [])
    rejected = {
        row.get("spelling"): row for row in rejected_rows if isinstance(row, dict)
    }
    require(list(rejected) == list(REJECTED_SPELLINGS), "REJECTED_SPELLING_SET")
    for spelling, (replacements, diagnostic_id) in REJECTED_SPELLINGS.items():
        row = rejected.get(spelling, {})
        require(
            row.get("accepted") is False
            and row.get("alias_created") is False
            and row.get("canonical_replacements") == replacements
            and row.get("diagnostic_id") == diagnostic_id,
            "REJECTED_SPELLING_EXACT",
        )

    structural = contract.get("structural_resolution", {})
    require(
        structural.get("algorithm_id") == "RESPONSIBILITY_STRUCTURAL_FIXED_POINT_R1"
        and structural.get("candidate_identities")
        == ["PlainValue", "Shareable", "Transferable", "CopyValue"]
        and all(
            structural.get(field) is True
            for field in (
                "terminating",
                "finite_nominal_graph_required",
                "memoized_identity_subject_pairs",
                "cycle_detection_required",
                "import_order_independent",
                "source_declaration_order_independent",
            )
        )
        and structural.get("runtime_or_provider_search_count") == 0
        and structural.get("open_world_structural_search") is False,
        "STRUCTURAL_TERMINATION",
    )

    residue = contract.get("evidence_residue", {})
    require(
        residue.get("descriptor_exact_fields") == DESCRIPTOR_FIELDS
        and residue.get("behavioral_descriptor_exact_fields")
        == BEHAVIORAL_DESCRIPTOR_FIELDS
        and residue.get("hir_exact_fields") == HIR_FIELDS
        and residue.get("api_exact_fields") == API_FIELDS
        and residue.get("mir_exact_fields") == MIR_FIELDS
        and residue.get("exact_identity_preservation") is True
        and residue.get("exact_selected_witness_preservation") is True,
        "EVIDENCE_RESIDUE_EXACT",
    )
    require(
        residue.get("clone_runtime_relookup_count") == 0
        and residue.get("deep_clone_runtime_relookup_count") == 0
        and all(row.get("runtime_relookup_count") == 0 for row in identities),
        "RUNTIME_RELOOKUP",
    )
    operator = contract.get("operator_boundary", {})
    require(
        operator.get("fixed_operator_role_count") == 13
        and operator.get("operator_trait_root_count") == 9
        and operator.get("responsibility_identity_operator_mapping_count") == 0
        and operator.get("responsibility_identity_operator_mappings") == []
        and operator.get("capture_operations_are_operator_dispatch") is False,
        "OPERATOR_BOUNDARY",
    )

    diagnostic_contract = contract.get("diagnostics", {})
    expected_new_rows = diagnostic_contract.get("expected_new_ids", [])
    expected_new_ids = [
        row.get("diagnostic_id") for row in expected_new_rows if isinstance(row, dict)
    ]
    require(
        diagnostic_contract.get("existing_active_ids") == EXISTING_DIAGNOSTICS,
        "DIAGNOSTIC_EXISTING_SET",
    )
    require(
        expected_new_ids == NEW_DIAGNOSTICS
        and len(expected_new_rows) == 2
        and all(
            row.get("stage") == "checker"
            and row.get("severity") == "error"
            and row.get("status") == "EXPECTED_REGISTRY_ADDITION"
            for row in expected_new_rows
            if isinstance(row, dict)
        )
        and diagnostic_contract.get("expected_new_id_count") == 2
        and diagnostic_contract.get("diagnostic_catalog_mutation_count") == 2,
        "DIAGNOSTIC_NEW_SET_EXACT_TWO",
    )
    diagnostic_by_id = {
        row.get("diagnostic_id"): row
        for row in diagnostic_rows
        if isinstance(row.get("diagnostic_id"), str)
    }
    require(
        all(
            diagnostic_by_id.get(diagnostic_id, {}).get("diagnostic_status") == "active"
            and diagnostic_by_id.get(diagnostic_id, {}).get("diagnostic_maturity") == "active"
            for diagnostic_id in EXISTING_DIAGNOSTICS
        ),
        "DIAGNOSTIC_EXISTING_ACTIVE",
    )
    present_new_ids = [
        diagnostic_id
        for diagnostic_id in NEW_DIAGNOSTICS
        if diagnostic_id in diagnostic_by_id
    ]
    require(
        len(present_new_ids) in {0, 2}
        and all(
            diagnostic_by_id[diagnostic_id].get("diagnostic_status") == "active"
            and diagnostic_by_id[diagnostic_id].get("diagnostic_maturity") == "active"
            and diagnostic_by_id[diagnostic_id].get("stage") == "checker"
            and diagnostic_by_id[diagnostic_id].get("severity") == "error"
            for diagnostic_id in present_new_ids
        ),
        "DIAGNOSTIC_NEW_EXPECTED_OR_ACTIVE_EXACT_TWO",
    )

    governance = contract.get("governance", {})
    product_lanes = governance.get("product_lanes", {})
    require(
        list(product_lanes) == PRODUCT_LANES
        and len(product_lanes) == 15
        and set(product_lanes.values()) == {"NOT_RUN"},
        "PRODUCT_LANES",
    )
    require(governance.get("open_feature_p1") == EXPECTED_P1, "GOVERNANCE_FEATURE_P1")
    require(
        governance.get("separate_open_m13_actions") == EXPECTED_M13,
        "GOVERNANCE_M13",
    )
    require(
        governance.get("semantic_p0") == 0
        and governance.get("product_execution") == "NOT_RUN"
        and governance.get("evidence_level") == "E2_DESIGN_STATIC"
        and governance.get("github_mutation") == 0,
        "GOVERNANCE_FENCE",
    )
    return errors


def fixture_errors(fixtures: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(
        fixtures.get("schema") == "deeplus.responsibility-identity-registry-fixtures/r1",
        "FIXTURE_SCHEMA",
    )
    require(fixtures.get("contract") == CONTRACT_REL, "FIXTURE_CONTRACT")
    cases = fixtures.get("cases", [])
    require(isinstance(cases, list), "FIXTURE_CASE_ARRAY")
    if not isinstance(cases, list):
        cases = []
    case_ids = [row.get("case_id") for row in cases if isinstance(row, dict)]
    require(len(cases) >= 18, "FIXTURE_MINIMUM_18")
    require(len(case_ids) == len(set(case_ids)) == len(cases), "FIXTURE_IDS_UNIQUE")
    require(
        all(
            isinstance(case_id, str)
            and re.fullmatch(r"R30-RIR-(POS|BND|NEG|MUT)-[0-9]{3}", case_id)
            for case_id in case_ids
        ),
        "FIXTURE_ID_FORMAT",
    )
    counts = Counter(row.get("class") for row in cases if isinstance(row, dict))
    expected_counts = {
        "positive": 6,
        "boundary": 7,
        "negative": 12,
        "mutation": 6,
    }
    require(dict(counts) == expected_counts, "FIXTURE_CLASS_COUNTS")
    require(
        fixtures.get("expected_counts") == {**expected_counts, "total": 31},
        "FIXTURE_DECLARED_COUNTS",
    )
    admitted_diagnostics = set(EXISTING_DIAGNOSTICS + NEW_DIAGNOSTICS)
    for row in cases:
        if not isinstance(row, dict):
            errors.append("FIXTURE_ROW_OBJECT")
            continue
        fixture_class = row.get("class")
        outcome = row.get("expected_outcome")
        require(isinstance(row.get("scenario"), str) and bool(row["scenario"]), "FIXTURE_SCENARIO")
        require(
            row.get("expected_identity_or_null") in set(IDENTITY_IDS) | {None},
            "FIXTURE_IDENTITY",
        )
        require(
            row.get("expected_diagnostic_or_null") in admitted_diagnostics | {None},
            "FIXTURE_DIAGNOSTIC",
        )
        if fixture_class == "positive":
            require(outcome == "ADMIT", "FIXTURE_POSITIVE_OUTCOME")
        elif fixture_class == "boundary":
            require(outcome in {"ADMIT", "BLOCKED_PREVIEW"}, "FIXTURE_BOUNDARY_OUTCOME")
        elif fixture_class == "negative":
            require(outcome == "REJECT", "FIXTURE_NEGATIVE_OUTCOME")
            require(row.get("expected_diagnostic_or_null") is not None, "FIXTURE_NEGATIVE_DIAGNOSTIC")
        elif fixture_class == "mutation":
            require(outcome == "REJECT_MUTATION", "FIXTURE_MUTATION_OUTCOME")
            require(isinstance(row.get("mutation_path"), list), "FIXTURE_MUTATION_PATH")
            require(
                isinstance(row.get("expected_validator_error"), str),
                "FIXTURE_MUTATION_ERROR",
            )
        else:
            errors.append("FIXTURE_CLASS")
    require(
        fixtures.get("status_fence")
        == {
            "semantic_p0": 0,
            "open_feature_p1": 22,
            "open_m13_actions": 4,
            "product_lanes": "15/15_NOT_RUN",
            "product_execution": "NOT_RUN",
            "github_mutation": 0,
        },
        "FIXTURE_STATUS_FENCE",
    )
    return errors


def input_fixture_errors(
    fixtures: dict[str, Any], input_schema: dict[str, Any]
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(
        fixtures.get("schema")
        == "deeplus.responsibility-identity-input-fixtures/r1",
        "INPUT_FIXTURE_SCHEMA",
    )
    require(fixtures.get("input_schema") == INPUT_SCHEMA_REL, "INPUT_FIXTURE_SCHEMA_PATH")
    require(fixtures.get("contract") == CONTRACT_REL, "INPUT_FIXTURE_CONTRACT")
    require(fixtures.get("evidence_level") == "E2_DESIGN_STATIC", "INPUT_FIXTURE_EVIDENCE")
    cases = fixtures.get("cases", [])
    require(isinstance(cases, list), "INPUT_FIXTURE_CASE_ARRAY")
    if not isinstance(cases, list):
        cases = []
    case_ids = [row.get("case_id") for row in cases if isinstance(row, dict)]
    require(len(case_ids) == len(set(case_ids)) == 12, "INPUT_FIXTURE_IDS_EXACT_12")
    expected_ids = [
        f"PF-{predicate_id}-{suffix}"
        for predicate_id in RESPONSIBILITY_PREDICATES
        for suffix in ("POS", "BOUNDARY", "NEG")
    ]
    require(case_ids == expected_ids, "INPUT_FIXTURE_ID_ORDER")
    counts = Counter(row.get("class") for row in cases if isinstance(row, dict))
    require(
        dict(counts) == {"positive": 4, "boundary": 4, "negative": 4},
        "INPUT_FIXTURE_CLASS_COUNTS",
    )
    require(
        fixtures.get("expected_counts")
        == {
            "predicate_count": 4,
            "positive": 4,
            "boundary": 4,
            "negative": 4,
            "total": 12,
        },
        "INPUT_FIXTURE_DECLARED_COUNTS",
    )
    by_predicate_class: dict[tuple[str, str], dict[str, Any]] = {}
    for row in cases:
        if not isinstance(row, dict):
            errors.append("INPUT_FIXTURE_ROW_OBJECT")
            continue
        predicate_id = row.get("predicate_id")
        fixture_class = row.get("class")
        require(predicate_id in RESPONSIBILITY_PREDICATES, "INPUT_FIXTURE_PREDICATE")
        require(fixture_class in {"positive", "boundary", "negative"}, "INPUT_FIXTURE_CLASS")
        input_value = row.get("input")
        if not isinstance(input_value, dict):
            errors.append("INPUT_FIXTURE_INPUT_OBJECT")
            continue
        errors.extend(schema_errors(input_value, input_schema, input_schema, f"$.cases[{row.get('case_id')}].input"))
        require(input_value.get("predicate_id") == predicate_id, "INPUT_FIXTURE_PREDICATE_BINDING")
        require(
            input_value.get("responsibility_rule_id")
            == PREDICATE_RULE_IDS.get(predicate_id),
            "INPUT_FIXTURE_RULE_BINDING",
        )
        if isinstance(predicate_id, str) and isinstance(fixture_class, str):
            by_predicate_class[(predicate_id, fixture_class)] = row
        if fixture_class == "negative":
            require(row.get("expected_outcome") == "REJECT", "INPUT_FIXTURE_NEGATIVE_OUTCOME")
            require(
                row.get("expected_diagnostic_or_null") in NEW_DIAGNOSTICS
                or row.get("expected_diagnostic_or_null") == "BORROW_ESCAPE_OWNER_REGION",
                "INPUT_FIXTURE_NEGATIVE_DIAGNOSTIC",
            )
        else:
            require(row.get("expected_outcome") == "ADMIT", "INPUT_FIXTURE_ADMIT_OUTCOME")
            require(row.get("expected_diagnostic_or_null") is None, "INPUT_FIXTURE_ADMIT_DIAGNOSTIC")

    for predicate_id in RESPONSIBILITY_PREDICATES:
        require(
            all(
                (predicate_id, fixture_class) in by_predicate_class
                for fixture_class in ("positive", "boundary", "negative")
            ),
            "INPUT_FIXTURE_EXACT_CLASS_PER_PREDICATE",
        )

    plain_negative = by_predicate_class.get(("PlainValueAdmissible", "negative"), {}).get("input", {})
    require(
        plain_negative.get("source_spelling_or_null") == "PlainValue"
        and by_predicate_class.get(("PlainValueAdmissible", "negative"), {}).get("expected_diagnostic_or_null")
        == "RESPONSIBILITY_IDENTITY_UNRESOLVED",
        "INPUT_PLAINVALUE_SOURCE_REJECTED",
    )
    shareable_boundary = by_predicate_class.get(("ShareableObservationSafe", "boundary"), {}).get("input", {})
    shareable_negative = by_predicate_class.get(("ShareableObservationSafe", "negative"), {}).get("input", {})
    require(
        shareable_boundary.get("observation_mutability") == "SYNCHRONIZED_MUTABLE"
        and isinstance(shareable_boundary.get("synchronization_law_id_or_null"), str)
        and shareable_boundary.get("synchronization_law_id_or_null")
        in shareable_boundary.get("registered_law_ids", []),
        "INPUT_SHAREABLE_SYNCHRONIZED_BOUNDARY",
    )
    require(
        shareable_negative.get("observation_mutability") == "UNSYNCHRONIZED_MUTABLE"
        and shareable_negative.get("synchronization_law_id_or_null") is None,
        "INPUT_SHAREABLE_UNSYNCHRONIZED_REJECTED",
    )
    transfer_negative = by_predicate_class.get(("TransferableAcrossIsolation", "negative"), {}).get("input", {})
    require(
        isinstance(transfer_negative.get("borrow_region_id_or_null"), str)
        and transfer_negative.get("storage_kind") == "VIEW",
        "INPUT_TRANSFER_BORROW_REJECTED",
    )
    copy_positive = by_predicate_class.get(("CopyValueAdmissible", "positive"), {}).get("input", {})
    copy_boundary = by_predicate_class.get(("CopyValueAdmissible", "boundary"), {}).get("input", {})
    for copy_input in (copy_positive, copy_boundary):
        require(
            copy_input.get("lifecycle") == "Reusable"
            and copy_input.get("cleanup_token_ids") == []
            and isinstance(copy_input.get("copy_rule_id_or_null"), str)
            and copy_input.get("copy_rule_id_or_null") in copy_input.get("registered_law_ids", [])
            and copy_input.get("copy_source_remains_live") is True
            and copy_input.get("copy_result_same_type") is True
            and copy_input.get("copy_error_set_id_or_null") is None
            and copy_input.get("copy_effect_row_id_or_null") is None
            and copy_input.get("copy_creates_cleanup_obligation") is False
            and copy_input.get("direct_user_conformance") is False,
            "INPUT_COPY_ADMISSIBLE_EXACT",
        )
    copy_negative = by_predicate_class.get(("CopyValueAdmissible", "negative"), {}).get("input", {})
    require(
        copy_negative.get("lifecycle") == "Resource"
        and bool(copy_negative.get("cleanup_token_ids"))
        and copy_negative.get("copy_rule_id_or_null") is None
        and copy_negative.get("copy_creates_cleanup_obligation") is True,
        "INPUT_COPY_RESOURCE_REJECTED",
    )
    require(
        fixtures.get("status_fence")
        == {
            "semantic_p0": 0,
            "open_feature_p1": 22,
            "open_m13_actions": 4,
            "product_lanes": "15/15_NOT_RUN",
            "product_execution": "NOT_RUN",
            "github_mutation": 0,
        },
        "INPUT_FIXTURE_STATUS_FENCE",
    )
    return errors


def projection_errors(root: Path, input_fixtures: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    predicates = load_chunk_rows(root, "spec/types/predicates/chunks")
    predicate_by_id = {
        row.get("predicate_id"): row
        for row in predicates
        if isinstance(row.get("predicate_id"), str)
    }
    require(len(predicates) == len(predicate_by_id), "PREDICATE_CATALOG_IDENTITIES_UNIQUE")
    require(
        all(predicate_id in predicate_by_id for predicate_id in RESPONSIBILITY_PREDICATES),
        "PREDICATE_SET_EXACT",
    )
    fixture_ids = {
        row.get("case_id")
        for row in input_fixtures.get("cases", [])
        if isinstance(row, dict)
    }
    for predicate_id in RESPONSIBILITY_PREDICATES:
        row = predicate_by_id.get(predicate_id, {})
        require(
            row.get("input_descriptor") == "ResponsibilityIdentityInputR1"
            and row.get("input_descriptor_schema") == INPUT_SCHEMA_REL
            and row.get("predicate_maturity") == "design_algorithm"
            and row.get("product_support") == "NOT_RUN"
            and row.get("execution_receipt") is None,
            "PREDICATE_INPUT_BINDING",
        )
        referenced_fixture_ids = set(row.get("positive_fixture_ids", [])) | set(
            row.get("negative_fixture_ids", [])
        )
        require(referenced_fixture_ids <= fixture_ids, "PREDICATE_FIXTURE_BINDING")
        dispatch = row.get("diagnostic_dispatch", {})
        require(
            dispatch
            == {
                "unknown_or_stale_identity": "RESPONSIBILITY_IDENTITY_UNRESOLVED",
                "known_identity_evidence_failure": "RESPONSIBILITY_EVIDENCE_NOT_ADMISSIBLE",
            }
            and set(NEW_DIAGNOSTICS) <= set(row.get("diagnostic_refs", [])),
            "PREDICATE_DIAGNOSTIC_DISPATCH",
        )

    copy_row = predicate_by_id.get("CopyValueAdmissible", {})
    require(
        copy_row.get("source_name") == "internal CopyValue / copy capture"
        and copy_row.get("active_primary_diagnostic")
        == "RESPONSIBILITY_EVIDENCE_NOT_ADMISSIBLE"
        and copy_row.get("dependency_predicates") == []
        and copy_row.get("positive_fixture_ids")
        == ["PF-CopyValueAdmissible-POS", "PF-CopyValueAdmissible-BOUNDARY"]
        and copy_row.get("negative_fixture_ids") == ["PF-CopyValueAdmissible-NEG"],
        "PREDICATE_COPYVALUE_EXACT",
    )

    metadata = load_json(root / PREDICATE_METADATA_REL)
    overrides = metadata.get("input_descriptor_overrides", {})
    require(
        metadata.get("predicate_count") == len(predicates)
        and metadata.get("design_algorithm_count")
        == sum(row.get("predicate_maturity") == "design_algorithm" for row in predicates)
        and metadata.get("design_seed_count")
        == sum(row.get("predicate_maturity") == "design_seed" for row in predicates)
        and metadata.get("override_count") == len(overrides),
        "PREDICATE_METADATA_COUNTS",
    )
    for predicate_id in RESPONSIBILITY_PREDICATES:
        require(
            overrides.get(predicate_id)
            == {
                "input_descriptor": "ResponsibilityIdentityInputR1",
                "input_descriptor_schema": INPUT_SCHEMA_REL,
            },
            "PREDICATE_METADATA_OVERRIDE",
        )

    relations = load_json(root / RELATION_REL)
    require(isinstance(relations, list), "RELATION_ARRAY")
    if not isinstance(relations, list):
        relations = []
    for predicate_id in RESPONSIBILITY_PREDICATES:
        observed = {
            (row.get("violation_id"), row.get("diagnostic_id"), row.get("relation"))
            for row in relations
            if isinstance(row, dict) and row.get("predicate_id") == predicate_id
        }
        required = {
            (
                f"{predicate_id}:unknown_or_stale_identity",
                "RESPONSIBILITY_IDENTITY_UNRESOLVED",
                "secondary",
            ),
            (
                f"{predicate_id}:default",
                "RESPONSIBILITY_EVIDENCE_NOT_ADMISSIBLE",
                "primary",
            ),
        }
        require(required <= observed, "RELATION_PRIMARY_SECONDARY_BINDING")

    feature_rows = load_json(root / FEATURE_REL)
    responsibility_features = [
        row
        for row in feature_rows
        if isinstance(row, dict)
        and row.get("feature_id") == "responsibility_identity_registry_r1"
    ] if isinstance(feature_rows, list) else []
    require(len(responsibility_features) == 1, "FEATURE_ROW_EXACT_ONE")
    feature = responsibility_features[0] if responsibility_features else {}
    trace = feature.get("normative_trace_refs", {})
    artifacts = feature.get("artifact_trace_refs", [])
    require(
        trace.get("predicates") == RESPONSIBILITY_PREDICATES
        and set(NEW_DIAGNOSTICS) == set(trace.get("diagnostics", [])),
        "FEATURE_TRACE_BINDING",
    )
    require(
        INPUT_SCHEMA_REL in artifacts and INPUT_FIXTURE_REL in artifacts,
        "FEATURE_ARTIFACT_BINDING",
    )
    return errors


def replace_path(document: Any, path: list[Any], replacement: Any) -> None:
    target = document
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def mutation_receipts(
    contract: dict[str, Any],
    fixtures: dict[str, Any],
    schema: dict[str, Any],
    diagnostic_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for row in fixtures.get("cases", []):
        if not isinstance(row, dict) or row.get("class") != "mutation":
            continue
        mutated = copy.deepcopy(contract)
        observed: list[str]
        try:
            replace_path(mutated, row["mutation_path"], row.get("replacement"))
            observed = contract_errors(mutated, schema, diagnostic_rows)
        except Exception as exc:  # noqa: BLE001 - mutation receipt captures the failure
            observed = [f"MUTATION_EXCEPTION:{type(exc).__name__}:{exc}"]
        expected = row.get("expected_validator_error")
        rejected = isinstance(expected, str) and any(
            error.startswith(expected) for error in observed
        )
        receipts.append(
            {
                "case_id": row.get("case_id"),
                "result": "REJECTED" if rejected else "SURVIVED",
                "expected_error": expected,
                "observed_errors": observed,
            }
        )
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    try:
        contract = load_json(root / CONTRACT_REL)
        schema = load_json(root / SCHEMA_REL)
        fixtures = load_json(root / FIXTURE_REL)
        input_schema = load_json(root / INPUT_SCHEMA_REL)
        input_fixtures = load_json(root / INPUT_FIXTURE_REL)
        diagnostic_rows = load_diagnostics(root)
        errors.extend(contract_errors(contract, schema, diagnostic_rows))
        errors.extend(fixture_errors(fixtures))
        errors.extend(input_fixture_errors(input_fixtures, input_schema))
        errors.extend(projection_errors(root, input_fixtures))
        mutations = mutation_receipts(contract, fixtures, schema, diagnostic_rows)
    except Exception as exc:  # noqa: BLE001 - emit a bounded receipt
        errors.append(f"VALIDATOR_EXCEPTION:{type(exc).__name__}:{exc}")
        mutations = []

    rejected_mutations = sum(row.get("result") == "REJECTED" for row in mutations)
    if len(mutations) != 6 or rejected_mutations != 6:
        errors.append("MUTATION_REJECTION_EXACT_6")

    error_groups = {
        "R30_SCHEMA_CONTRACT": ("SCHEMA_", "CONTRACT_"),
        "R30_IDENTITY_SET_EXACT": (
            "IDENTITY_",
            "PLAIN_IDENTITY_",
            "SHAREABLE_",
            "TRANSFERABLE_",
            "COPY_PUBLIC_",
            "CLONE_BEHAVIOR_",
            "DEEPCLONE_",
            "LIFECYCLE_",
            "SHARED_HANDLE_",
            "REJECTED_SPELLING_",
            "OPERATOR_",
        ),
        "R30_AXIS_INDEPENDENCE": ("AXIS_",),
        "R30_IMPLICATION_ZEROES": ("IMPLICATION_", "PLAIN_EXTERNAL_"),
        "R30_TERMINATING_RESOLUTION": ("STRUCTURAL_", "PREDICATE_COPYVALUE_"),
        "R30_EVIDENCE_RESIDUE": (
            "EVIDENCE_",
            "RUNTIME_",
            "INPUT_CONTRACT_",
            "PREDICATE_INPUT_",
            "PREDICATE_METADATA_",
        ),
        "R30_DIAGNOSTIC_IDENTITY": (
            "DIAGNOSTIC_",
            "PREDICATE_DIAGNOSTIC_",
            "RELATION_",
        ),
        "R30_FIXTURE_MATRIX": (
            "FIXTURE_",
            "INPUT_FIXTURE_",
            "INPUT_PLAINVALUE_",
            "INPUT_SHAREABLE_",
            "INPUT_TRANSFER_",
            "INPUT_COPY_",
            "PREDICATE_FIXTURE_",
            "FEATURE_",
        ),
        "R30_MUTATION_REJECTION": ("MUTATION_",),
        "R30_GOVERNANCE_FENCE": ("GOVERNANCE_", "PRODUCT_"),
    }
    checks = []
    for check_id in CHECK_IDS:
        prefixes = error_groups[check_id]
        checks.append(
            {
                "check_id": check_id,
                "pass": not any(
                    any(error.startswith(prefix) for prefix in prefixes)
                    for error in errors
                ),
            }
        )
    result = "PASS" if not errors and all(row["pass"] for row in checks) else "FAIL"
    receipt = {
        "schema": "deeplus.r30-responsibility-identity-validation-receipt/r1",
        "result": result,
        "evidence_level": "E2_DESIGN_STATIC",
        "check_scope": "R30_RESPONSIBILITY_IDENTITY_REGISTRY_EXACT",
        "check_count": len(checks),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "identity_count": 6,
        "independent_axis_count": 6,
        "off_diagonal_implication_true_count": 0,
        "existing_diagnostic_count": 12,
        "expected_new_diagnostic_count": 2,
        "fixture_case_count": 31,
        "input_fixture_case_count": 12,
        "responsibility_predicate_count": 4,
        "mutation_count": len(mutations),
        "rejected_mutation_count": rejected_mutations,
        "mutations": mutations,
        "open_feature_p1_count": 22,
        "separate_open_m13_action_count": 4,
        "product_lane_count": 15,
        "product_execution": "NOT_RUN",
        "grammar_production_change_count": 0,
        "new_source_spelling_count": 0,
        "github_mutation": 0,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
