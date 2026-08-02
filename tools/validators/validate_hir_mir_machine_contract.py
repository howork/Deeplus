#!/usr/bin/env python3
"""Focused static validator for the canonical-candidate R10 HIR/MIR machine contract.

Scope is deliberately bounded to the canonical HIR schema/catalog, MIR
schema/registry, lowering row schema/registry, diagnostic delta, and the 43
fixture bindings.  This script does not execute a compiler, mutate a corpus,
claim a product lane, or validate target projection capabilities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def canonical_paths(root: Path) -> dict[str, Path]:
    return {
        "registry": root / "spec/contracts/hir-mir-lowering-registry.json",
        "hir_schema": root / "schemas/language/canonical-hir-h1.schema.json",
        "hir_catalog": root / "spec/contracts/hir-h1-identity-catalog.json",
        "mir_schema": root / "schemas/language/deeplus-mir.schema.json",
        "mir_registry": root / "spec/contracts/mir-machine-registry.json",
        "row_schema": (
            root / "schemas/language/hir-mir-lowering-row.schema.json"
        ),
        "fixture_schema": (
            root
            / "schemas/language/"
            "hir-mir-machine-contract-fixtures.schema.json"
        ),
        "fixtures": (
            root / "tests/fixtures/current/hir-mir-machine-contract-r1.json"
        ),
        "diagnostics": (
            root
            / "spec/contracts/hir-mir-machine-diagnostic-contract.json"
        ),
    }


PATHS = canonical_paths(ROOT)
AXES = [
    "value_mode",
    "resource",
    "place_access",
    "effects",
    "recoverable_errors",
    "defects",
    "cancellation",
    "suspension",
    "isolation",
    "authority",
    "cleanup",
]

VALID_CALL_PAIRS = [
    "ORDINARY::DIRECT_IMPLEMENTATION",
    "ORDINARY::VIRTUAL_SLOT",
    "ORDINARY::TRAIT_WITNESS",
    "ORDINARY::EXTENSION_STATIC",
    "MESSAGE::DIRECT_IMPLEMENTATION",
    "MESSAGE::VIRTUAL_SLOT",
    "MESSAGE::TRAIT_WITNESS",
    "MESSAGE::EXTENSION_STATIC",
    "MESSAGE::RESERVED_OPERATION",
    "ACTOR_MESSAGE::ACTOR_TRANSPORT",
]

EXPECTED_FAMILY_COUNTS = {
    "TOP_LEVEL_EXPRESSION_OR_STATEMENT": 35,
    "RESOLVED_REF": 2,
    "VALID_CALL_MODE_TARGET_PAIR": 10,
    "CALL_ARGUMENT": 7,
    "FIXED_OPERATOR_OR_POWER": 19,
    "PATTERN_CURRENT": 29,
    "PATTERN_PREVIEW_ADDITIONAL": 9,
}

EXPECTED_STATUS_FENCE = {
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "m13_actions": "4_OPEN_UNCHANGED",
    "product_lanes": "15_OF_15_NOT_RUN",
    "canonical_source_mutation": 0,
    "github_mutation": 0,
}
R31_LOWERING_REVISION = "R31-CLOSURE-CAPTURE-PLAN-R1"

PREVIEW_PATTERNS = {
    "PK-AND",
    "PK-NOT",
    "PK-SET",
    "PK-NUMERIC-ARRAY",
    "PK-PATTERN-SYNONYM",
    "PK-PATTERN-VIEW",
    "PK-FIND",
    "PK-GENERIC-SEQUENCE-REST",
    "PK-TUPLE-REST",
}

AGGREGATE_PATTERNS = {
    "PK-PARENTHESIZED",
    "PK-TUPLE",
    "PK-LIST-EXACT",
    "PK-LIST-IGNORED-TAIL",
    "PK-LIST-SUFFIX-REST",
    "PK-LIST-PREFIX-REST",
    "PK-LIST-MIDDLE-REST",
    "PK-RECORD-EXACT",
    "PK-RECORD-OPEN-IGNORED",
    "PK-RECORD-OPEN-CAPTURED",
    "PK-MAP-EXACT",
    "PK-MAP-OPEN-IGNORED",
    "PK-MAP-OPEN-CAPTURED",
    "PK-NOMINAL-TRANSPARENT",
    "PK-VARIANT",
    "PK-VARIANT-NAMED",
    "PK-SET",
    "PK-NUMERIC-ARRAY",
    "PK-GENERIC-SEQUENCE-REST",
    "PK-TUPLE-REST",
}

BINDING_PATTERNS = {
    "PK-BINDER",
    "PK-UNION-ALTERNATIVE-BINDER",
    "PK-TYPED-BINDER",
    "PK-LIST-SUFFIX-REST",
    "PK-LIST-PREFIX-REST",
    "PK-LIST-MIDDLE-REST",
    "PK-RECORD-OPEN-CAPTURED",
    "PK-MAP-OPEN-CAPTURED",
    "PK-BOUNDED-BINDER",
    "PK-ALIAS",
    "PK-MOVE",
    "PK-GENERIC-SEQUENCE-REST",
    "PK-TUPLE-REST",
}


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[int, str, str]] = []

    def require(
        self, condition: bool, stage: int, code: str, message: str
    ) -> None:
        if not condition:
            self.errors.append((stage, code, message))

    def extend_schema(self, label: str, errors: list[str]) -> None:
        for message in errors[:100]:
            self.errors.append(
                (1, "JSON_SCHEMA_VALIDATION_FAILURE", f"{label}: {message}")
            )
        if len(errors) > 100:
            self.errors.append(
                (
                    1,
                    "JSON_SCHEMA_VALIDATION_FAILURE",
                    f"{label}: {len(errors) - 100} additional schema errors",
                )
            )


def canonical(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_documents(report: Report) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for label, path in PATHS.items():
        report.require(
            path.is_file(),
            1,
            "JSON_SCHEMA_VALIDATION_FAILURE",
            f"missing required integrated input {path}",
        )
        if not path.is_file():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            report.errors.append(
                (
                    1,
                    "JSON_SCHEMA_VALIDATION_FAILURE",
                    f"{label} cannot be parsed as UTF-8 JSON: {exc}",
                )
            )
            continue
        if not isinstance(value, dict):
            report.errors.append(
                (
                    1,
                    "JSON_SCHEMA_VALIDATION_FAILURE",
                    f"{label} root must be an object",
                )
            )
            continue
        documents[label] = value
    return documents


def json_equal(left: Any, right: Any) -> bool:
    return canonical(left) == canonical(right)


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def resolve_local_ref(root: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise ValueError(f"only local JSON Pointer references are supported: {reference}")
    value: Any = root
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        value = value[part]
    return value


def schema_errors(
    instance: Any,
    schema: Any,
    root: dict[str, Any],
    path: str = "$",
) -> list[str]:
    errors: list[str] = []
    if isinstance(schema, bool):
        if not schema:
            errors.append(f"{path}: value is forbidden")
        return errors
    if not isinstance(schema, dict):
        return [f"{path}: invalid schema node"]

    if "$ref" in schema:
        try:
            target = resolve_local_ref(root, schema["$ref"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{path}: unresolved schema reference {schema['$ref']}: {exc}")
        else:
            errors.extend(schema_errors(instance, target, root, path))

    if "allOf" in schema:
        for branch in schema["allOf"]:
            errors.extend(schema_errors(instance, branch, root, path))

    if "oneOf" in schema:
        branch_errors = [
            schema_errors(instance, branch, root, path)
            for branch in schema["oneOf"]
        ]
        matching = sum(not branch for branch in branch_errors)
        if matching != 1:
            errors.append(
                f"{path}: oneOf matched {matching} branches instead of exactly one"
            )

    if "if" in schema:
        condition_matches = not schema_errors(instance, schema["if"], root, path)
        selected = schema.get("then") if condition_matches else schema.get("else")
        if selected is not None:
            errors.extend(schema_errors(instance, selected, root, path))

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not type_matches(instance, expected_type):
        return errors + [
            f"{path}: expected type {expected_type}, got {type(instance).__name__}"
        ]
    if isinstance(expected_type, list) and not any(
        type_matches(instance, candidate) for candidate in expected_type
    ):
        return errors + [
            f"{path}: expected one of types {expected_type}, got {type(instance).__name__}"
        ]

    if "const" in schema and not json_equal(instance, schema["const"]):
        errors.append(f"{path}: value differs from const {schema['const']!r}")
    if "enum" in schema and not any(
        json_equal(instance, option) for option in schema["enum"]
    ):
        errors.append(f"{path}: value is outside closed enum")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string is shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: string does not match pattern {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: number is below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: number is above maximum")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array is shorter than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array is longer than maxItems")
        if schema.get("uniqueItems"):
            encoded = [canonical(item) for item in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: array items are not unique")
        prefix = schema.get("prefixItems", [])
        for index, subschema in enumerate(prefix):
            if index < len(instance):
                errors.extend(
                    schema_errors(
                        instance[index], subschema, root, f"{path}[{index}]"
                    )
                )
        items = schema.get("items")
        if items is False and len(instance) > len(prefix):
            errors.append(f"{path}: array has items beyond closed prefixItems")
        elif isinstance(items, dict):
            start = len(prefix)
            for index in range(start, len(instance)):
                errors.extend(
                    schema_errors(
                        instance[index], items, root, f"{path}[{index}]"
                    )
                )

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(
                    schema_errors(
                        instance[key], subschema, root, f"{path}.{key}"
                    )
                )
        if schema.get("additionalProperties") is False:
            extra = sorted(set(instance) - set(properties))
            if extra:
                errors.append(
                    f"{path}: additional properties are forbidden: {extra}"
                )
    return errors


def collect_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            strings.extend(collect_strings(item))
    elif isinstance(value, list):
        for item in value:
            strings.extend(collect_strings(item))
    return strings


def collect_hir_identity_literals(value: Any) -> set[str]:
    identity_pattern = re.compile(
        r"^HIR-H1/(?:EXPR|STMT|STRUCT|RESOLVED_REF|CALL_MODE|"
        r"CALL_ARGUMENT|CALL_TARGET|INTRINSIC_FAMILY|FIXED_OPERATOR|"
        r"POWER|PATTERN)/"
    )
    return {
        item
        for item in collect_strings(value)
        if identity_pattern.match(item) is not None
    }


def derive_hir_identity_set(schema: dict[str, Any]) -> set[str]:
    """Project the schema's closed discriminators into catalog identity IDs.

    The JSON representation intentionally uses compact per-family
    discriminators such as ``ExprKind = "CALL"``.  Requiring the schema to
    duplicate all 130 fully qualified catalog strings would create a second
    registry.  This projection instead proves that the executable schema
    discriminators and the catalog use the same closed universe.
    """

    defs = schema.get("$defs", {})
    identities = collect_hir_identity_literals(schema)

    def enum_values(definition: str) -> list[str]:
        value = defs.get(definition, {}).get("enum", [])
        return [item for item in value if isinstance(item, str)]

    identities.update(
        f"HIR-H1/EXPR/{item}" for item in enum_values("ExprKind")
    )
    identities.update(
        f"HIR-H1/STMT/{item}"
        for item in (
            defs.get("StmtBase", {})
            .get("properties", {})
            .get("kind", {})
            .get("enum", [])
        )
        if isinstance(item, str)
    )

    for branch in defs.get("ResolvedRef", {}).get("oneOf", []):
        kind = branch.get("properties", {}).get("kind", {}).get("const")
        if isinstance(kind, str):
            identities.add(f"HIR-H1/RESOLVED_REF/{kind}")

    call_modes: set[str] = set()
    call_targets: set[str] = set()
    for pair in enum_values("CallModeTargetPair"):
        mode, separator, target = pair.partition("::")
        if separator:
            call_modes.add(mode)
            call_targets.add(target)
    identities.update(f"HIR-H1/CALL_MODE/{item}" for item in call_modes)
    identities.update(f"HIR-H1/CALL_TARGET/{item}" for item in call_targets)

    for branch in defs.get("CallArgument", {}).get("oneOf", []):
        for component in branch.get("allOf", []):
            kind = component.get("properties", {}).get("kind", {}).get("const")
            if isinstance(kind, str):
                identities.add(f"HIR-H1/CALL_ARGUMENT/{kind}")

    intrinsic_families = {
        item
        for item in collect_strings(defs.get("IntrinsicPlan", {}))
        if item in {"FIXED_OPERATOR_CONFORMANCE", "POWER"}
    }
    identities.update(
        f"HIR-H1/INTRINSIC_FAMILY/{item}"
        for item in intrinsic_families
    )
    identities.update(
        f"HIR-H1/FIXED_OPERATOR/{item}"
        for item in (
            enum_values("UnaryFixedOperatorId")
            + enum_values("BinaryFixedOperatorId")
        )
    )
    identities.update(
        f"HIR-H1/POWER/{item}" for item in enum_values("PowerOperationId")
    )
    identities.update(
        f"HIR-H1/PATTERN/{item}"
        for item in (
            enum_values("CurrentPatternKindId")
            + enum_values("PreviewPatternKindId")
        )
    )
    return identities


def check_schema_and_bindings(
    report: Report, docs: dict[str, dict[str, Any]]
) -> None:
    needed = set(PATHS)
    if set(docs) != needed:
        return
    registry = docs["registry"]
    row_schema = docs["row_schema"]
    fixture_schema = docs["fixture_schema"]
    fixtures = docs["fixtures"]

    rows = registry.get("rows")
    if isinstance(rows, list):
        for index, row in enumerate(rows):
            report.extend_schema(
                f"rows[{index}]",
                schema_errors(row, row_schema, row_schema, f"$.rows[{index}]"),
            )
    else:
        report.errors.append(
            (
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                "lowering registry rows must be an array",
            )
        )

    report.extend_schema(
        "fixture binding table",
        schema_errors(fixtures, fixture_schema, fixture_schema),
    )

    expected_top_keys = {
        "schema",
        "draft_revision",
        "status",
        "artifact_context",
        "contract_bindings",
        "lowering_rules_revision",
        "profile_contract",
        "coverage_contract",
        "loan_close_projection_contract",
        "semantic_operation_mapping",
        "nominal_construction_lifecycle_mapping",
        "continuation_frame_mapping",
        "capability_gate_contract",
        "ownership_type_qualifier_projection",
        "rows",
        "status_fence",
        "actor_protocol_binding_contract",
        "closure_capture_plan_lowering_contract",
        "deferred_call_plan_projection_contract",
        "type_header_cleanup_budget_projection_contract",
        "shared_mutex_with_lock_projection_contract",
    }
    report.require(
        set(registry) == expected_top_keys,
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering registry wrapper fields differ from the closed canonical shape",
    )
    report.require(
        registry.get("schema") == "deeplus.hir-mir-lowering-registry/r1",
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering registry schema ID is not r1",
    )
    report.require(
        registry.get("draft_revision") == R31_LOWERING_REVISION
        and registry.get("lowering_rules_revision") == R31_LOWERING_REVISION,
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering registry revisions are not the R31 bounded extension",
    )

    expected_bindings = {
        "hir_schema": (
            "../../schemas/language/canonical-hir-h1.schema.json",
            "deeplus.canonical-hir-h1/r1",
            "hir_schema",
        ),
        "hir_identity_catalog": (
            "hir-h1-identity-catalog.json",
            "deeplus.hir-h1-identity-catalog/r1",
            "hir_catalog",
        ),
        "mir_schema": (
            "../../schemas/language/deeplus-mir.schema.json",
            "deeplus.mir/r1",
            "mir_schema",
        ),
        "mir_machine_registry": (
            "mir-machine-registry.json",
            "deeplus.mir-machine-registry/r1",
            "mir_registry",
        ),
        "lowering_row_schema": (
            "../../schemas/language/hir-mir-lowering-row.schema.json",
            "deeplus.hir-mir-lowering-row/r1",
            "row_schema",
        ),
        "fixture_binding_table": (
            "../../tests/fixtures/current/hir-mir-machine-contract-r1.json",
            "deeplus.hir-mir-machine-contract-fixtures/r1",
            "fixtures",
        ),
        "diagnostic_contract": (
            "hir-mir-machine-diagnostic-contract.json",
            "deeplus.hir-mir-machine-diagnostic-contract/r1",
            "diagnostics",
        ),
    }
    bindings = registry.get("contract_bindings", {})
    report.require(
        isinstance(bindings, dict) and set(bindings) == set(expected_bindings),
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "contract_bindings do not name the exact seven canonical artifacts",
    )
    if isinstance(bindings, dict):
        for name, (relative, schema_id, document_label) in expected_bindings.items():
            binding = bindings.get(name)
            if not isinstance(binding, dict):
                continue
            report.require(
                binding.get("relative_path") == relative,
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                f"{name} relative path differs from the locked binding",
            )
            report.require(
                binding.get("schema_id") == schema_id,
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                f"{name} schema ID differs from the locked identity",
            )
            report.require(
                binding.get("sha256") == sha256_file(PATHS[document_label]),
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                f"{name} SHA-256 does not bind the current canonical bytes",
            )
            allowed = {"schema_id", "relative_path", "sha256"}
            if name == "fixture_binding_table":
                allowed.add("case_count")
                report.require(
                    binding.get("case_count") == 43,
                    1,
                    "JSON_SCHEMA_VALIDATION_FAILURE",
                    "fixture binding declares a count other than 43",
                )
            report.require(
                set(binding) == allowed,
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                f"{name} binding has missing or additional fields",
            )

    report.require(
        docs["diagnostics"].get("schema")
        == "deeplus.hir-mir-machine-diagnostic-contract/r1",
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "diagnostic contract schema ID is not canonical r1",
    )

    for schema_label in ("hir_schema", "mir_schema", "row_schema", "fixture_schema"):
        schema = docs[schema_label]
        report.require(
            schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            1,
            "JSON_SCHEMA_VALIDATION_FAILURE",
            f"{schema_label} is not a JSON Schema Draft 2020-12 document",
        )


def check_hir_catalog(
    report: Report, docs: dict[str, dict[str, Any]]
) -> tuple[set[str], dict[str, tuple[str, str, list[str]]]]:
    if "hir_catalog" not in docs or "hir_schema" not in docs:
        return set(), {}
    catalog = docs["hir_catalog"]
    hir_schema = docs["hir_schema"]
    identity_rows = catalog.get("identity_rows")
    if not isinstance(identity_rows, list):
        report.errors.append(
            (
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                "HIR identity_rows is not an array",
            )
        )
        return set(), {}

    identity_ids = [
        row.get("identity_id")
        for row in identity_rows
        if isinstance(row, dict) and isinstance(row.get("identity_id"), str)
    ]
    identity_set = set(identity_ids)
    report.require(
        catalog.get("schema") == "deeplus.hir-h1-identity-catalog/r1",
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR identity catalog schema ID differs from r1",
    )
    report.require(
        catalog.get("identity_count") == 130
        and len(identity_rows) == 130
        and len(identity_ids) == 130
        and len(identity_set) == 130,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR identity catalog is not an exact unique 130-row closed set",
    )

    family_counts = Counter(
        row.get("family") for row in identity_rows if isinstance(row, dict)
    )
    role_counts = Counter(
        row.get("role") for row in identity_rows if isinstance(row, dict)
    )
    report.require(
        dict(family_counts) == catalog.get("family_counts"),
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR family_counts do not equal identity_rows",
    )
    report.require(
        dict(role_counts) == catalog.get("role_counts"),
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR role_counts do not equal identity_rows",
    )
    current_profile_count = sum(
        "CURRENT" in row.get("source_profiles", [])
        for row in identity_rows
        if isinstance(row, dict)
    )
    preview_profile_count = sum(
        "EXPLICIT_PREVIEW" in row.get("source_profiles", [])
        for row in identity_rows
        if isinstance(row, dict)
    )
    report.require(
        catalog.get("profile_catalog_counts")
        == {
            "CURRENT": current_profile_count,
            "EXPLICIT_PREVIEW": preview_profile_count,
        }
        == {"CURRENT": 121, "EXPLICIT_PREVIEW": 130},
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR catalog profile counts are not exact 121/130",
    )
    for row in identity_rows:
        if not isinstance(row, dict):
            continue
        parent = row.get("parent_identity_id")
        report.require(
            parent is None or parent in identity_set,
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"HIR identity {row.get('identity_id')} has an unknown parent {parent}",
        )

    excluded = set(catalog.get("excluded_pre_hir_pattern_ids", []))
    report.require(
        excluded == {"PK-EFFECTFUL-EXTRACTOR", "PK-BACKTRACKING"},
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "pre-HIR rejected pattern set is not the exact two-entry set",
    )
    report.require(
        all(f"HIR-H1/PATTERN/{pattern}" not in identity_set for pattern in excluded),
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "a pre-HIR rejected pattern was admitted to the 130-row catalog",
    )
    schema_identity_set = derive_hir_identity_set(hir_schema)
    report.require(
        schema_identity_set == identity_set,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR schema identity literals and the exact 130-row catalog differ",
    )

    expected_gate = {
        "lowering_row_dispositions": ["LOWER", "NO_RUNTIME_EMISSION"],
        "capability_insufficiency_is_lowering_row": False,
        "verified_hir_digest_on_insufficiency": "EXACTLY_PRESERVED",
        "executable_hir_h1_on_insufficiency": "NOT_CREATED",
    }
    report.require(
        catalog.get("capability_gate_contract") == expected_gate,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR catalog does not place capability insufficiency only at the executable gate",
    )
    report.require(
        hir_schema.get("x-deeplus-machine-contract", {}).get(
            "capability_gate_contract"
        )
        == expected_gate,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR schema and catalog capability-gate contracts differ",
    )
    report.require(
        catalog.get("structural_plan_contract_count") == 14,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR structural_plan_contract_count is not exactly 14",
    )
    receipt_validation_results = (
        catalog.get("verification_receipt_contract", {})
        .get("receipt_shape", {})
        .get("properties", {})
        .get("validation_results", {})
    )
    report.require(
        "structural_plan"
        in receipt_validation_results.get("required", [])
        and receipt_validation_results.get("properties", {})
        .get("structural_plan", {})
        .get("const")
        == "PASS",
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "HIR verification receipt does not require validation_results.structural_plan=PASS",
    )

    expected_dispatch: dict[str, tuple[str, str, list[str]]] = {}

    def add(
        key: dict[str, str],
        family: str,
        profile: str,
        identities: list[str],
    ) -> None:
        token_key = canonical(key)
        if token_key in expected_dispatch:
            report.errors.append(
                (
                    2,
                    "R10_HM_VARIANT_REGISTRY_MISMATCH",
                    f"derived HIR dispatch key is duplicated: {token_key}",
                )
            )
        expected_dispatch[token_key] = (family, profile, identities)

    for row in identity_rows:
        if not isinstance(row, dict):
            continue
        identity_id = row.get("identity_id")
        family = row.get("family")
        if family in {"EXPR_KIND", "STMT_KIND"}:
            identity = identity_id.rsplit("/", 1)[-1]
            category = "EXPRESSION" if family == "EXPR_KIND" else "STATEMENT"
            add(
                {
                    "kind": "TOP_LEVEL",
                    "node_category": category,
                    "identity_id": identity,
                },
                "TOP_LEVEL_EXPRESSION_OR_STATEMENT",
                "CURRENT",
                [identity_id],
            )
        elif family == "RESOLVED_REF_KIND":
            identity = identity_id.rsplit("/", 1)[-1]
            add(
                {"kind": "RESOLVED_REF", "identity_id": identity},
                "RESOLVED_REF",
                "CURRENT",
                ["HIR-H1/EXPR/RESOLVED_REF", identity_id],
            )
        elif family == "CALL_ARGUMENT_KIND":
            identity = identity_id.rsplit("/", 1)[-1]
            add(
                {"kind": "CALL_ARGUMENT", "identity_id": identity},
                "CALL_ARGUMENT",
                "CURRENT",
                ["HIR-H1/EXPR/CALL", identity_id],
            )
        elif family in {"FIXED_OPERATOR_KIND", "POWER_OPERATION_KIND"}:
            identity = identity_id.rsplit("/", 1)[-1]
            intrinsic_family = (
                "FIXED_OPERATOR_CONFORMANCE"
                if family == "FIXED_OPERATOR_KIND"
                else "POWER"
            )
            add(
                {
                    "kind": "INTRINSIC_OPERATION",
                    "intrinsic_family": intrinsic_family,
                    "identity_id": identity,
                },
                "FIXED_OPERATOR_OR_POWER",
                "CURRENT",
                [
                    "HIR-H1/EXPR/INTRINSIC",
                    f"HIR-H1/INTRINSIC_FAMILY/{intrinsic_family}",
                    identity_id,
                ],
            )
        elif family == "PATTERN_KIND":
            identity = identity_id.rsplit("/", 1)[-1]
            profile = (
                "EXPLICIT_PREVIEW"
                if row.get("source_profiles") == ["EXPLICIT_PREVIEW"]
                else "CURRENT"
            )
            add(
                {
                    "kind": "PATTERN",
                    "pattern_profile": profile,
                    "identity_id": identity,
                },
                "PATTERN",
                profile,
                ["HIR-H1/EXPR/PATTERN_ATTEMPT", identity_id],
            )

    for pair in VALID_CALL_PAIRS:
        mode, target = pair.split("::")
        identities = [
            "HIR-H1/EXPR/CALL",
            f"HIR-H1/CALL_MODE/{mode}",
            f"HIR-H1/CALL_TARGET/{target}",
        ]
        report.require(
            all(identity in identity_set for identity in identities),
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"valid call pair {pair} does not resolve to exact catalog identities",
        )
        add(
            {"kind": "CALL_MODE_TARGET_PAIR", "pair_id": pair},
            "VALID_CALL_MODE_TARGET_PAIR",
            "CURRENT",
            identities,
        )

    report.require(
        len(expected_dispatch) == 111,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        f"derived reachable lowering-key set has {len(expected_dispatch)} entries, expected 111",
    )
    return identity_set, expected_dispatch


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, int] = {node: 0 for node in graph}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for dependency in graph.get(node, []):
            if dependency not in graph:
                continue
            if state[dependency] == 0:
                cycle = visit(dependency)
                if cycle:
                    return cycle
            elif state[dependency] == 1:
                start = stack.index(dependency)
                return stack[start:] + [dependency]
        stack.pop()
        state[node] = 2
        return None

    for node in graph:
        if state[node] == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def check_mir_registry(
    report: Report, docs: dict[str, dict[str, Any]]
) -> tuple[
    dict[str, str],
    set[str],
    set[str],
    set[str],
    dict[str, set[str]],
    dict[str, dict[str, set[str]]],
]:
    if "mir_registry" not in docs:
        return {}, set(), set(), set(), {}, {}
    registry = docs["mir_registry"]
    operations = registry.get("semantic_operations", [])
    terminators = registry.get("terminators", [])
    tokens = registry.get("linear_tokens", [])
    capabilities = registry.get("capabilities", [])

    operation_map: dict[str, str] = {}
    for entry in operations if isinstance(operations, list) else []:
        if not isinstance(entry, dict):
            continue
        kind = entry.get("operation_kind")
        semantic_id = entry.get("semantic_operation_id")
        if isinstance(kind, str) and isinstance(semantic_id, str):
            report.require(
                kind not in operation_map,
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                f"duplicate MIR operation kind {kind}",
            )
            operation_map[kind] = semantic_id
            report.require(
                semantic_id == f"DM-SEMOP-{kind.replace('_', '-')}-R1",
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                f"MIR semantic operation ID for {kind} violates the total-map formula",
            )
    report.require(
        len(operation_map) == 48 and len(set(operation_map.values())) == 48,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "MIR semantic-operation map is not a total one-to-one 48-entry map",
    )

    terminator_set = {
        entry.get("terminator_kind")
        for entry in terminators
        if isinstance(entry, dict) and isinstance(entry.get("terminator_kind"), str)
    }
    token_set = {
        entry.get("token_kind")
        for entry in tokens
        if isinstance(entry, dict) and isinstance(entry.get("token_kind"), str)
    }
    report.require(
        len(terminators) == 17 and len(terminator_set) == 17,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "MIR terminator registry is not the exact unique 17-entry set",
    )
    report.require(
        len(tokens) == 12 and len(token_set) == 12,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "MIR linear-token registry is not the exact unique 12-entry set",
    )

    capability_rows: dict[str, dict[str, set[str]]] = {}
    graph: dict[str, list[str]] = {}
    for entry in capabilities if isinstance(capabilities, list) else []:
        if not isinstance(entry, dict) or not isinstance(
            entry.get("capability_id"), str
        ):
            continue
        capability_id = entry["capability_id"]
        report.require(
            capability_id not in graph,
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"duplicate MIR capability {capability_id}",
        )
        graph[capability_id] = list(entry.get("requires", []))
        capability_rows[capability_id] = {
            "operation_kinds": set(entry.get("operation_kinds", [])),
            "terminator_kinds": set(entry.get("terminator_kinds", [])),
            "token_kinds": set(entry.get("token_kinds", [])),
        }
    capability_set = set(graph)
    report.require(
        len(capability_set) == 26
        and set(registry.get("capability_ids", [])) == capability_set
        and len(registry.get("capability_ids", [])) == 26,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "MIR capability registry is not the exact unique 26-entry set",
    )
    for capability_id, dependencies in graph.items():
        for dependency in dependencies:
            report.require(
                dependency in capability_set,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{capability_id} has unknown capability dependency {dependency}",
            )
        row = capability_rows[capability_id]
        for operation_kind in row["operation_kinds"]:
            report.require(
                operation_kind in operation_map,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{capability_id} references unknown operation {operation_kind}",
            )
        for terminator_kind in row["terminator_kinds"]:
            report.require(
                terminator_kind in terminator_set,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{capability_id} references unknown terminator {terminator_kind}",
            )
        for token_kind in row["token_kinds"]:
            report.require(
                token_kind in token_set,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{capability_id} references unknown token {token_kind}",
            )

    cycle = find_cycle(graph)
    report.require(
        cycle is None,
        5,
        "R10_HM_LOWERING_TARGET_UNKNOWN",
        (
            "capability dependency graph has DEPENDENCY_CYCLE "
            + " -> ".join(cycle or [])
        ),
    )

    closures: dict[str, set[str]] = {}
    if cycle is None and all(
        dependency in capability_set
        for dependencies in graph.values()
        for dependency in dependencies
    ):
        def closure(capability_id: str) -> set[str]:
            if capability_id in closures:
                return closures[capability_id]
            result = {capability_id}
            for dependency in graph[capability_id]:
                result.update(closure(dependency))
            closures[capability_id] = result
            return result

        for capability_id in graph:
            closure(capability_id)

    shared_mutex = registry.get("shared_mutex_with_lock_contract", {})
    report.require(
        isinstance(shared_mutex, dict)
        and shared_mutex.get("plan_schema") == "SharedMutexWithLockPlan"
        and shared_mutex.get("payload_predicate_id")
        == "SharedMutexPayloadAdmitted"
        and shared_mutex.get("ordered_machine_steps")
        == [
            "SYNC_OP:LOCK_ACQUIRE",
            "LOAN_BEGIN_EXCLUSIVE",
            "INVOKE:CALLBACK",
            "LOAN_END",
            "SYNC_OP:LOCK_RELEASE",
        ]
        and shared_mutex.get("wrapper_unlock_excluded_from_payload_predicate")
        is True
        and shared_mutex.get("product_execution") == "NOT_RUN",
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "SharedMutexWithLockPlan is not bound to the exact existing MIR machine sequence",
    )
    return (
        operation_map,
        terminator_set,
        token_set,
        capability_set,
        closures,
        capability_rows,
    )


TOP_SEMANTIC_PLANS: dict[str, tuple[list[str], list[str], str]] = {
    "LITERAL": (["CONST"], [], "LOWER"),
    "RESOLVED_REF": (["TOTAL_PROJECTION"], [], "LOWER"),
    "BLOCK": ([], ["BR"], "LOWER"),
    "CALL": (["CONTEXT_ADAPT"], [], "LOWER"),
    "INTRINSIC": (["TOTAL_PROJECTION"], [], "LOWER"),
    "PLACE_ACCESS": (["PLACE_LOAD"], [], "LOWER"),
    "REPLACE": (["MOVE_RESERVE", "MOVE_CANCEL"], ["PLACE_REPLACE"], "LOWER"),
    "IF": ([], ["COND_BR"], "LOWER"),
    "TERNARY": ([], ["COND_BR"], "LOWER"),
    "MATCH": (["PATTERN_PROBE"], ["SWITCH_ENUM"], "LOWER"),
    "LOOP": ([], ["COND_BR", "BR"], "LOWER"),
    "TRY": (["CLEANUP_REGION_ENTER"], ["LEAVE"], "LOWER"),
    "STRICT_BOOL": (["PURE_INTRINSIC"], [], "LOWER"),
    "SEQUENTIAL_BOOL": ([], ["COND_BR"], "LOWER"),
    "OPTION_COALESCE": (["TOTAL_PROJECTION"], ["SWITCH_ENUM"], "LOWER"),
    "PATTERN_ATTEMPT": (
        ["PATTERN_PROBE", "BINDING_COMMIT"],
        ["COND_BR"],
        "LOWER",
    ),
    "CONSTRUCTION": (
        ["BUILDER_BEGIN", "BUILDER_STAGE", "BUILDER_COMMIT", "AGGREGATE_INJECT"],
        ["CHECKED"],
        "LOWER",
    ),
    "MAP_LITERAL": (
        ["BUILDER_BEGIN", "BUILDER_STAGE", "BUILDER_COMMIT"],
        ["CHECKED"],
        "LOWER",
    ),
    "INTERPOLATION": (
        ["BUILDER_BEGIN", "BUILDER_STAGE", "BUILDER_COMMIT"],
        ["CHECKED"],
        "LOWER",
    ),
    "CLOSURE": (
        ["BUILDER_BEGIN", "BUILDER_STAGE", "BUILDER_COMMIT", "CLOSURE_MAKE"],
        ["CHECKED", "LEAVE"],
        "LOWER",
    ),
    "CLEANUP_SCOPE": (["CLEANUP_REGION_ENTER"], ["LEAVE"], "LOWER"),
    "AWAIT": (["FRAME_SUSPEND_COMMIT", "FRAME_RESUME_COMMIT", "FRAME_CANCEL_COMMIT"], ["SUSPEND"], "LOWER"),
    "YIELD": (["FRAME_SUSPEND_COMMIT", "FRAME_RESUME_COMMIT", "FRAME_CANCEL_COMMIT"], ["SUSPEND"], "LOWER"),
    "CONCUR": (["CONCUR_ENTER"], ["RUN_OP"], "LOWER"),
    "PROVIDER_OPERATION": ([], ["PROVIDER_OP"], "LOWER"),
    "RETURN_TO": ([], ["LEAVE"], "LOWER"),
    "RET_TO": ([], ["LEAVE"], "LOWER"),
    "BREAK_TO": ([], ["LEAVE"], "LOWER"),
    "CONTINUE_TO": ([], ["LEAVE"], "LOWER"),
    "THROW": ([], ["LEAVE"], "LOWER"),
    "CANCEL_PROPAGATE": ([], ["LEAVE"], "LOWER"),
    "EVALUATE": ([], [], "NO_RUNTIME_EMISSION"),
    "LOCAL_INIT": (["PLACE_STORE_INIT"], [], "LOWER"),
    "REGISTER_CLEANUP": (
        [
            "CLEANUP_REGISTER",
            "CLEANUP_PIN",
            "CLEANUP_SEAL",
            "CLEANUP_DISARM",
            "LOAN_END",
            "MOVE_CANCEL",
        ],
        [],
        "LOWER",
    ),
    "NESTED_ITEM": ([], [], "NO_RUNTIME_EMISSION"),
}

CALL_OPERATION = {
    "DIRECT_IMPLEMENTATION": "STATIC_REF",
    "VIRTUAL_SLOT": "TOTAL_PROJECTION",
    "TRAIT_WITNESS": "STATIC_REF",
    "EXTENSION_STATIC": "CONTEXT_ADAPT",
    "RESERVED_OPERATION": "STATIC_REF",
    "ACTOR_TRANSPORT": "ACTOR_ENVELOPE_PREPARE",
}

ARGUMENT_OPERATION = {
    "POSITIONAL": "CONTEXT_ADAPT",
    "NAMED": "CONTEXT_ADAPT",
    "POSITIONAL_UNFOLD": "TOTAL_PROJECTION",
    "NAMED_UNFOLD": "TOTAL_PROJECTION",
    "CONTEXT": "CONTEXT_ADAPT",
    "WITNESS": "STATIC_REF",
    "TRAILING_CLOSURE": "CLOSURE_MAKE",
}

CHECKED_INTRINSICS = {
    "UNARY_MINUS",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "DIVIDE",
    "REMAINDER",
    "CHECKED_INT_POW",
}


def expected_semantic_plan(
    dispatch: dict[str, Any],
) -> tuple[list[str], list[str], str]:
    kind = dispatch["kind"]
    if kind == "TOP_LEVEL":
        return TOP_SEMANTIC_PLANS[dispatch["identity_id"]]
    if kind == "RESOLVED_REF":
        operation_kind = (
            "PLACE_LOAD" if dispatch["identity_id"] == "LOCAL" else "STATIC_REF"
        )
        return [operation_kind], [], "LOWER"
    if kind == "CALL_MODE_TARGET_PAIR":
        mode, target = dispatch["pair_id"].split("::")
        return (
            [CALL_OPERATION[target]],
            ["ACTOR_OP" if mode == "ACTOR_MESSAGE" else "INVOKE"],
            "LOWER",
        )
    if kind == "CALL_ARGUMENT":
        if dispatch["identity_id"] == "TRAILING_CLOSURE":
            return (
                [
                    "BUILDER_BEGIN",
                    "BUILDER_STAGE",
                    "BUILDER_COMMIT",
                    "CLOSURE_MAKE",
                ],
                ["CHECKED", "LEAVE"],
                "LOWER",
            )
        return [ARGUMENT_OPERATION[dispatch["identity_id"]]], [], "LOWER"
    if kind == "INTRINSIC_OPERATION":
        terminators = (
            ["CHECKED"] if dispatch["identity_id"] in CHECKED_INTRINSICS else []
        )
        return ["PURE_INTRINSIC"], terminators, "LOWER"
    if kind == "PATTERN":
        identity = dispatch["identity_id"]
        operations = ["PATTERN_PROBE"]
        if identity in AGGREGATE_PATTERNS:
            operations.append("TOTAL_PROJECTION")
        if identity in BINDING_PATTERNS:
            operations.append("BINDING_COMMIT")
        if identity == "PK-PIN":
            operations.insert(0, "PLACE_LOAD")
        elif identity == "PK-MOVE":
            operations.insert(0, "MOVE_RESERVE")
            operations.append("PLACE_MOVE")
        return operations, [], "LOWER"
    raise KeyError(canonical(dispatch))


def check_rows(
    report: Report,
    docs: dict[str, dict[str, Any]],
    identity_set: set[str],
    expected_dispatch: dict[str, tuple[str, str, list[str]]],
    mir_contract: tuple[
        dict[str, str],
        set[str],
        set[str],
        set[str],
        dict[str, set[str]],
        dict[str, dict[str, set[str]]],
    ],
) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    if "registry" not in docs:
        return facts
    registry = docs["registry"]
    rows = registry.get("rows")
    if not isinstance(rows, list):
        return facts
    (
        operation_map,
        terminator_set,
        token_set,
        capability_set,
        capability_closures,
        capability_rows,
    ) = mir_contract

    hir_schema_digest = (
        sha256_file(PATHS["hir_schema"]) if PATHS["hir_schema"].is_file() else None
    )
    mir_schema_digest = (
        sha256_file(PATHS["mir_schema"]) if PATHS["mir_schema"].is_file() else None
    )
    row_ids: list[str] = []
    rule_ids: list[str] = []
    dispatch_tokens: list[str] = []
    lookup_tokens: list[str] = []
    actual_dispatch: dict[str, dict[str, Any]] = {}
    structural_row_count = 0
    pre_hir_row_count = 0
    placeholder_pattern = re.compile(
        r"(?:\bTODO\b|\bTBD\b|PLACEHOLDER|FILL[_ -]?ME[_ -]?IN|EXAMPLE[_ -]?ONLY)",
        re.IGNORECASE,
    )

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        label = row.get("row_id", f"rows[{index}]")
        row_ids.append(str(row.get("row_id")))
        rule_ids.append(str(row.get("lowering_rule_id")))
        dispatch = row.get("lowering_dispatch_key", {})
        dispatch_token = canonical(dispatch)
        dispatch_tokens.append(dispatch_token)
        actual_dispatch[dispatch_token] = row
        lookup_tokens.append(
            canonical(
                [
                    row.get("hir_schema_digest"),
                    row.get("mir_schema_digest"),
                    row.get("lowering_rules_revision"),
                    dispatch,
                ]
            )
        )
        report.require(
            row.get("hir_schema_digest") == hir_schema_digest
            and row.get("mir_schema_digest") == mir_schema_digest,
            1,
            "JSON_SCHEMA_VALIDATION_FAILURE",
            f"{label} schema digest tuple does not bind current HIR/MIR bytes",
        )
        report.require(
            row.get("lowering_rules_revision") == R31_LOWERING_REVISION,
            1,
            "JSON_SCHEMA_VALIDATION_FAILURE",
            f"{label} lowering revision is not the R31 bounded extension",
        )
        identities = row.get("hir_identity_ids", [])
        unknown_identities = [
            identity for identity in identities if identity not in identity_set
        ]
        report.require(
            not unknown_identities,
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"{label} references unknown HIR identities {unknown_identities}",
        )
        structural_row_count += any(
            identity.startswith("HIR-H1/STRUCT/") for identity in identities
        )
        pre_hir_row_count += any(
            identity
            in {
                "HIR-H1/PATTERN/PK-EFFECTFUL-EXTRACTOR",
                "HIR-H1/PATTERN/PK-BACKTRACKING",
            }
            for identity in identities
        )
        expected = expected_dispatch.get(dispatch_token)
        if expected is not None:
            expected_family, expected_profile, expected_identities = expected
            report.require(
                row.get("row_family") == expected_family
                and row.get("profile_gate") == expected_profile
                and identities == expected_identities,
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                f"{label} family/profile/HIR identity tuple differs from its dispatch key",
            )

        operation_kinds: list[str] = []
        for ordinal, step in enumerate(row.get("operation_plan", []), 1):
            operation_kind = step.get("operation_kind")
            operation_kinds.append(operation_kind)
            report.require(
                step.get("ordinal") == ordinal,
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                f"{label} operation ordinals are not contiguous from one",
            )
            report.require(
                operation_kind in operation_map
                and step.get("semantic_operation_id")
                == operation_map.get(operation_kind),
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{label} operation/semantic-operation pair does not resolve",
            )
        terminator_kinds: list[str] = []
        for ordinal, step in enumerate(row.get("terminator_plan", []), 1):
            terminator_kind = step.get("terminator_kind")
            terminator_kinds.append(terminator_kind)
            report.require(
                step.get("ordinal") == ordinal,
                1,
                "JSON_SCHEMA_VALIDATION_FAILURE",
                f"{label} terminator ordinals are not contiguous from one",
            )
            report.require(
                terminator_kind in terminator_set,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{label} references unknown terminator {terminator_kind}",
            )
        referenced_tokens: set[str] = set()
        for field in ("token_inputs", "token_outputs", "token_discharges"):
            for entry in row.get(field, []):
                token_kind = entry.get("token_kind")
                referenced_tokens.add(token_kind)
                report.require(
                    token_kind in token_set,
                    5,
                    "R10_HM_LOWERING_TARGET_UNKNOWN",
                    f"{label} references unknown token {token_kind}",
                )
        required_capabilities = row.get("required_capability_ids", [])
        for capability_id in required_capabilities:
            report.require(
                capability_id in capability_set,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{label} references unknown capability {capability_id}",
            )

        if (
            capability_closures
            and all(capability in capability_set for capability in required_capabilities)
        ):
            available_caps: set[str] = set()
            for capability in required_capabilities:
                available_caps.update(capability_closures[capability])
            supported_operations = set().union(
                *(
                    capability_rows[capability]["operation_kinds"]
                    for capability in available_caps
                ),
                set(),
            )
            supported_terminators = set().union(
                *(
                    capability_rows[capability]["terminator_kinds"]
                    for capability in available_caps
                ),
                set(),
            )
            supported_tokens = set().union(
                *(
                    capability_rows[capability]["token_kinds"]
                    for capability in available_caps
                ),
                set(),
            )
            report.require(
                set(operation_kinds) <= supported_operations,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{label} operations are not covered by required capability closure",
            )
            report.require(
                set(terminator_kinds) <= supported_terminators,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{label} terminators are not covered by required capability closure",
            )
            report.require(
                referenced_tokens <= supported_tokens,
                5,
                "R10_HM_LOWERING_TARGET_UNKNOWN",
                f"{label} tokens are not covered by required capability closure",
            )

        disposition = row.get("disposition")
        if disposition == "NO_RUNTIME_EMISSION":
            empty_fields = [
                "required_capability_ids",
                "operation_plan",
                "terminator_plan",
                "successor_roles",
                "token_inputs",
                "token_outputs",
                "token_discharges",
                "outcome_families",
            ]
            report.require(
                all(row.get(field) == [] for field in empty_fields),
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                f"{label} NO_RUNTIME_EMISSION row has runtime/capability residue",
            )
        elif disposition == "LOWER":
            report.require(
                bool(required_capabilities)
                and bool(operation_kinds or terminator_kinds),
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                f"{label} LOWER row lacks a concrete plan or required capability",
            )

        try:
            expected_ops, expected_terms, expected_disposition = (
                expected_semantic_plan(dispatch)
            )
        except (KeyError, TypeError):
            pass
        else:
            report.require(
                operation_kinds == expected_ops
                and terminator_kinds == expected_terms
                and disposition == expected_disposition,
                2,
                "R10_HM_VARIANT_REGISTRY_MISMATCH",
                f"{label} plan is not the concrete semantic plan for {dispatch_token}",
            )

        axis_projection = row.get("responsibility_projection", {})
        report.require(
            axis_projection.get("axis_order") == AXES
            and [
                entry.get("axis")
                for entry in axis_projection.get("axis_projections", [])
            ]
            == AXES
            and axis_projection.get("dropped_axis_count") == 0
            and axis_projection.get("changed_axis_count") == 0,
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"{label} does not preserve all eleven ordered responsibility axes",
        )
        report.require(
            row.get("provenance_projection", {}).get("key_shape")
            == "(HirBodyId,HirNodeId,LoweringRuleId)",
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"{label} provenance key shape differs from the locked triple",
        )
        placeholder_hits = [
            value for value in collect_strings(row) if placeholder_pattern.search(value)
        ]
        report.require(
            not placeholder_hits,
            2,
            "R10_HM_VARIANT_REGISTRY_MISMATCH",
            f"{label} contains placeholder text {placeholder_hits[:3]}",
        )

    report.require(
        len(row_ids) == len(set(row_ids)),
        3,
        "R10_HM_LOWERING_ROW_DUPLICATE",
        "lowering registry has duplicate row_id values",
    )
    report.require(
        len(rule_ids) == len(set(rule_ids)),
        3,
        "R10_HM_LOWERING_ROW_DUPLICATE",
        "lowering registry has duplicate lowering_rule_id values",
    )
    report.require(
        len(dispatch_tokens) == len(set(dispatch_tokens)),
        3,
        "R10_HM_LOWERING_ROW_DUPLICATE",
        "two lowering rows claim the same dispatch key",
    )
    report.require(
        len(lookup_tokens) == len(set(lookup_tokens)),
        3,
        "R10_HM_LOWERING_ROW_DUPLICATE",
        "two lowering rows claim the same exact four-field lookup key",
    )

    missing = sorted(set(expected_dispatch) - set(actual_dispatch))
    extra = sorted(set(actual_dispatch) - set(expected_dispatch))
    report.require(
        not missing,
        4,
        "R10_HM_LOWERING_ROW_MISSING",
        f"registry is missing {len(missing)} reachable lowering keys",
    )
    report.require(
        not extra,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        f"registry has {len(extra)} extra or unknown lowering keys",
    )
    report.require(
        structural_row_count == 0 and pre_hir_row_count == 0,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "structural or pre-HIR rejection identity received an independent row",
    )

    current_rows = [row for row in rows if row.get("profile_gate") == "CURRENT"]
    preview_rows = [
        row for row in rows if row.get("profile_gate") == "EXPLICIT_PREVIEW"
    ]
    report.require(
        len(rows) == 111 and len(current_rows) == 102 and len(preview_rows) == 9,
        4,
        "R10_HM_LOWERING_ROW_MISSING",
        "row totals are not exact 111 total / 102 CURRENT / 9 Preview additional",
    )
    report.require(
        all(
            row.get("counts_toward_current_102")
            == (row.get("profile_gate") == "CURRENT")
            and row.get("counts_toward_preview_111") is True
            for row in rows
        ),
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "profile count flags do not equal CURRENT/Preview reachability",
    )
    report.require(
        all(
            row.get("row_family") == "PATTERN"
            and row.get("lowering_dispatch_key", {}).get("identity_id")
            in PREVIEW_PATTERNS
            for row in preview_rows
        ),
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "Preview rows are not exactly the nine additional pattern rows",
    )

    family_counts = Counter(row.get("row_family") for row in current_rows)
    actual_family_counts = {
        "TOP_LEVEL_EXPRESSION_OR_STATEMENT": family_counts[
            "TOP_LEVEL_EXPRESSION_OR_STATEMENT"
        ],
        "RESOLVED_REF": family_counts["RESOLVED_REF"],
        "VALID_CALL_MODE_TARGET_PAIR": family_counts[
            "VALID_CALL_MODE_TARGET_PAIR"
        ],
        "CALL_ARGUMENT": family_counts["CALL_ARGUMENT"],
        "FIXED_OPERATOR_OR_POWER": family_counts["FIXED_OPERATOR_OR_POWER"],
        "PATTERN_CURRENT": family_counts["PATTERN"],
        "PATTERN_PREVIEW_ADDITIONAL": len(preview_rows),
    }
    report.require(
        actual_family_counts == EXPECTED_FAMILY_COUNTS,
        4,
        "R10_HM_LOWERING_ROW_MISSING",
        f"row-family counts differ: {actual_family_counts}",
    )
    report.require(
        registry.get("coverage_contract", {}).get("row_family_counts")
        == EXPECTED_FAMILY_COUNTS
        and registry.get("coverage_contract", {}).get(
            "valid_call_mode_target_pairs"
        )
        == VALID_CALL_PAIRS
        and registry.get("coverage_contract", {}).get(
            "structural_schema_independent_row_count"
        )
        == 0
        and registry.get("coverage_contract", {}).get(
            "pre_hir_rejection_row_count"
        )
        == 0,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "registry coverage contract differs from computed closed coverage",
    )

    expected_order = sorted(
        rows,
        key=lambda row: (
            row.get("composition_rank"),
            row.get("row_schema_version"),
            row.get("hir_identity_ids"),
            row.get("row_id"),
        ),
    )
    report.require(
        rows == expected_order,
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "registry rows are not in the locked deterministic sort order",
    )

    semantic_mapping = registry.get("semantic_operation_mapping", [])
    expected_mapping = [
        {
            "operation_kind": kind,
            "semantic_operation_id": semantic_id,
        }
        for kind, semantic_id in operation_map.items()
    ]
    report.require(
        semantic_mapping == expected_mapping and len(semantic_mapping) == 48,
        5,
        "R10_HM_LOWERING_TARGET_UNKNOWN",
        "lowering registry does not bind the exact ordered total 48-operation map",
    )
    report.require(
        registry.get("capability_gate_contract")
        == {
            "boundary": "EXECUTABLE_HIR_GATE",
            "lowering_row_disposition_on_missing_capability": "LOWER",
            "failure_diagnostic": "HIR_MIR_CAPABILITY_RECEIPT_MISMATCH",
            "verified_canonical_hir_effect": "PRESERVE",
            "executable_hir_created": False,
            "required_and_provided_capability_relation": "EXACT_SORTED_UNIQUE_EQUAL",
            "unsupported_reachable_key_count": 0,
        },
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "capability insufficiency is not fenced exclusively at ExecutableHirH1",
    )

    shared_mutex_projection = registry.get(
        "shared_mutex_with_lock_projection_contract", {}
    )
    report.require(
        isinstance(shared_mutex_projection, dict)
        and shared_mutex_projection.get("refines_row_id") == "HM-LR-CALL-009"
        and shared_mutex_projection.get("selected_reserved_operation_identity")
        == "SharedMutex::withLock"
        and shared_mutex_projection.get("evaluation_order")
        == [
            "EVALUATE_RECEIVER_ONCE",
            "EVALUATE_CALLBACK_ONCE",
            "SYNC_OP:LOCK_ACQUIRE",
            "LOAN_BEGIN_EXCLUSIVE",
            "INVOKE:CALLBACK",
            "LOAN_END",
            "SYNC_OP:LOCK_RELEASE",
        ]
        and shared_mutex_projection.get("wrapper_unlock_excluded_from_payload_predicate")
        is True
        and shared_mutex_projection.get("product_support") == "NOT_RUN",
        2,
        "R10_HM_VARIANT_REGISTRY_MISMATCH",
        "SharedMutex::withLock projection does not refine HM-LR-CALL-009 exactly",
    )

    template_groups: defaultdict[str, list[str]] = defaultdict(list)
    for row in rows:
        template = canonical(
            {
                field: row.get(field)
                for field in (
                    "operation_plan",
                    "terminator_plan",
                    "successor_roles",
                    "token_inputs",
                    "token_outputs",
                    "token_discharges",
                    "outcome_families",
                    "cleanup_effect",
                    "suspension_effect",
                    "ownership_effect",
                )
            }
        )
        template_groups[template].append(row["row_id"])
    shared_template_count = sum(
        len(row_group) > 1 for row_group in template_groups.values()
    )
    call_pairs = {
        row["lowering_dispatch_key"]["pair_id"]
        for row in rows
        if row.get("row_family") == "VALID_CALL_MODE_TARGET_PAIR"
    }
    facts.update(
        {
            "identity_catalog_count": len(identity_set),
            "row_count": len(rows),
            "current_row_count": len(current_rows),
            "preview_row_count": len(preview_rows),
            "family_counts": actual_family_counts,
            "structural_row_count": structural_row_count,
            "pre_hir_row_count": pre_hir_row_count,
            "duplicate_dispatch_key_count": len(dispatch_tokens)
            - len(set(dispatch_tokens)),
            "duplicate_row_id_count": len(row_ids) - len(set(row_ids)),
            "missing_key_count": len(missing),
            "extra_key_count": len(extra),
            "shared_template_count": shared_template_count,
            "call_pairs": call_pairs,
            "argument_row_count": family_counts["CALL_ARGUMENT"],
            "provenance_key_shapes": {
                row.get("provenance_projection", {}).get("key_shape")
                for row in rows
            },
            "capability_gate": registry.get("capability_gate_contract"),
        }
    )
    return facts


def check_fixture_bindings(
    report: Report,
    docs: dict[str, dict[str, Any]],
    facts: dict[str, Any],
) -> int:
    if "fixtures" not in docs or "diagnostics" not in docs:
        return 0
    fixtures = docs["fixtures"]
    diagnostics = docs["diagnostics"]
    cases = fixtures.get("cases")
    if not isinstance(cases, list):
        return 0

    case_ids = [
        case.get("case_id")
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("case_id"), str)
    ]
    expected_case_ids = (
        [f"R10-HM-POS-{index:03d}" for index in range(1, 9)]
        + [f"R10-HM-BOUND-{index:03d}" for index in range(1, 9)]
        + [f"R10-HM-NEG-{index:03d}" for index in range(1, 20)]
        + [f"R10-HM-MUT-{index:03d}" for index in range(1, 9)]
    )
    report.require(
        len(cases) == 43
        and len(case_ids) == 43
        and len(set(case_ids)) == 43
        and case_ids == expected_case_ids,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "fixture binding table is not the exact ordered 43-case set",
    )
    expected_result_by_class = {
        "positive": "PASS",
        "boundary": "BOUNDARY",
        "negative": "REJECT",
        "mutation": "MUTANT_KILLED",
    }
    class_counts = Counter(
        case.get("case_class") for case in cases if isinstance(case, dict)
    )
    report.require(
        class_counts
        == {"positive": 8, "boundary": 8, "negative": 19, "mutation": 8},
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        f"fixture class counts differ: {dict(class_counts)}",
    )

    priority_rows = diagnostics.get("deterministic_internal_priority", [])
    priority_by_id = {
        row["diagnostic_id"]: row["rank"]
        for row in priority_rows
        if isinstance(row, dict)
    }
    priority_ids = [
        row.get("diagnostic_id") for row in priority_rows if isinstance(row, dict)
    ]
    report.require(
        fixtures.get("deterministic_diagnostic_priority") == priority_ids,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "fixture internal diagnostic priority differs from diagnostic delta",
    )
    capability_rows = diagnostics.get("capability_mismatch_subpriority", [])
    expected_capability_labels = [
        "HIR_SCHEMA_DIGEST",
        "MIR_SCHEMA_DIGEST",
        "LOWERING_REGISTRY_DIGEST",
        "REQUIRED_REACHABILITY_SET",
        "PROVIDED_CAPABILITY_SET",
        "UNSUPPORTED_REACHABLE_KEY_COUNT",
    ]
    report.require(
        [row.get("rank") for row in capability_rows] == list(range(1, 7))
        and fixtures.get("capability_mismatch_subpriority")
        == expected_capability_labels,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "capability mismatch subpriority is not the locked six-rank relation",
    )
    report.require(
        diagnostics.get("responsibility_axis_priority") == AXES
        and fixtures.get("responsibility_axis_priority") == AXES,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "fixture/diagnostic responsibility axis order differs from the eleven axes",
    )
    preflight_rows = diagnostics.get("repository_preflight_stages", [])
    preflight_ids = [
        row.get("stage_id") for row in preflight_rows if isinstance(row, dict)
    ]
    failure_rank = {
        row["repository_failure_id_or_null"]: row["rank"]
        for row in preflight_rows
        if isinstance(row, dict)
        and row.get("repository_failure_id_or_null") is not None
    }
    report.require(
        fixtures.get("repository_preflight_priority") == preflight_ids,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "fixture repository preflight order differs from diagnostic delta",
    )
    repository_failures = {
        row.get("failure_id")
        for row in diagnostics.get("repository_only_failures", [])
        if isinstance(row, dict)
    }
    report.require(
        len(repository_failures) == 6
        and all(
            row.get("public_compiler_diagnostic") is False
            for row in diagnostics.get("repository_only_failures", [])
            if isinstance(row, dict)
        ),
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "repository failure catalog is not six non-public validator IDs",
    )
    existing_diagnostics = {
        row.get("diagnostic_id")
        for row in diagnostics.get("existing_diagnostic_reuse", [])
        if isinstance(row, dict)
    }
    new_internal = {
        row.get("diagnostic_id")
        for row in diagnostics.get("new_internal_diagnostics", [])
        if isinstance(row, dict)
    }
    report.require(
        len(new_internal) == 5
        and new_internal
        == set(priority_ids) - {"RCTS_RESPONSIBILITY_AXIS_DROPPED"},
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "new internal diagnostics do not bind exactly five priority identities",
    )
    report.require(
        {
            "RCTS_RESPONSIBILITY_AXIS_DROPPED",
            "RESOLVER_HIR_SEAL_INCOMPLETE",
            "RECEIVER_MODE_MISMATCH",
        }
        <= existing_diagnostics,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "existing diagnostic reuse set is incomplete",
    )

    allowed_oracles = {
        "HIR_CANONICAL_RECOVERY_NODE_FORBIDDEN": {"CANONICAL_HIR_SEAL"},
        "HIR_VARIANT_UNMAPPED": {"CANONICAL_HIR_SEAL"},
        "HIR_MIR_CAPABILITY_RECEIPT_MISMATCH": {"EXECUTABLE_HIR_GATE"},
        "RCTS_RESPONSIBILITY_AXIS_DROPPED": {"RESPONSIBILITY_VERIFIER"},
        "HIR_MIR_RESPONSIBILITY_PROJECTION_MISMATCH": {
            "RESPONSIBILITY_VERIFIER"
        },
        "HIR_MIR_PAIR_RELOWERING_MISMATCH": {
            "PAIR_VERIFIER",
            "SERIALIZATION_VERIFIER",
        },
    }
    case_by_id: dict[str, dict[str, Any]] = {}
    for case in cases:
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id", "<unknown>")
        case_by_id[case_id] = case
        report.require(
            case.get("expected_result")
            == expected_result_by_class.get(case.get("case_class")),
            6,
            "R10_HM_DIAGNOSTIC_BINDING_INVALID",
            f"{case_id} class/result binding is invalid",
        )
        internal = case.get("expected_internal_diagnostic_or_null")
        diagnostic_rank = case.get("diagnostic_priority_rank_or_null")
        if internal is None:
            report.require(
                diagnostic_rank is None,
                6,
                "R10_HM_DIAGNOSTIC_BINDING_INVALID",
                f"{case_id} has a diagnostic rank without an internal diagnostic",
            )
        else:
            report.require(
                priority_by_id.get(internal) == diagnostic_rank,
                6,
                "R10_HM_DIAGNOSTIC_BINDING_INVALID",
                f"{case_id} internal diagnostic priority binding is invalid",
            )
            report.require(
                case.get("oracle_layer") in allowed_oracles.get(internal, set()),
                6,
                "R10_HM_DIAGNOSTIC_BINDING_INVALID",
                f"{case_id} binds {internal} to the wrong oracle layer",
            )
        capability_rank = case.get("capability_subpriority_rank_or_null")
        report.require(
            (
                internal == "HIR_MIR_CAPABILITY_RECEIPT_MISMATCH"
                and capability_rank in range(1, 7)
            )
            or (
                internal != "HIR_MIR_CAPABILITY_RECEIPT_MISMATCH"
                and capability_rank is None
            ),
            6,
            "R10_HM_DIAGNOSTIC_BINDING_INVALID",
            f"{case_id} capability subpriority relation is invalid",
        )
        repository_failure = case.get("expected_repository_failure_or_null")
        repository_rank = case.get("repository_preflight_rank_or_null")
        if repository_failure is None:
            report.require(
                repository_rank is None,
                6,
                "R10_HM_DIAGNOSTIC_BINDING_INVALID",
                f"{case_id} has a repository rank without a repository failure",
            )
        else:
            report.require(
                repository_failure in repository_failures
                and failure_rank.get(repository_failure) == repository_rank,
                6,
                "R10_HM_DIAGNOSTIC_BINDING_INVALID",
                f"{case_id} repository failure/preflight binding is invalid",
            )
        source_disposition = case.get("source_diagnostic_disposition")
        source_diagnostic = case.get("expected_source_diagnostic_or_null")
        report.require(
            (
                source_disposition == "EXISTING_SOURCE_CHECKER_DIAGNOSTIC_REQUIRED"
                and source_diagnostic == "RECEIVER_MODE_MISMATCH"
                and source_diagnostic in existing_diagnostics
            )
            or (
                source_disposition
                in {"NONE", "ORIGINAL_SOURCE_DIAGNOSTIC_PRESERVED"}
                and source_diagnostic is None
            ),
            6,
            "R10_HM_DIAGNOSTIC_BINDING_INVALID",
            f"{case_id} source diagnostic relation is invalid",
        )
        report.require(
            case.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            and case.get("product_support") == "NOT_RUN",
            7,
            "R10_HM_PRODUCT_STATUS_OVERCLAIM",
            f"{case_id} overclaims execution or product support",
        )

    def assertions(case_id: str) -> set[str]:
        return set(case_by_id.get(case_id, {}).get("assertions", []))

    registry_backed_assertions = {
        "R10-HM-POS-001": {
            "35+2+10+7+19+29=102",
            "structural_schema_independent_row_count=0",
            "pre_hir_rejection_row_count=0",
        },
        "R10-HM-POS-002": {
            "102+9=111",
            "preview_additional_pattern_count=9",
            "rejected_pattern_row_count=0",
        },
        "R10-HM-POS-003": {
            "valid_call_pair_count=10",
            "actor_message_pair_set={ACTOR_MESSAGE::ACTOR_TRANSPORT}",
            "reserved_operation_pair_set={MESSAGE::RESERVED_OPERATION}",
        },
        "R10-HM-POS-006": {
            "shared_template_count>=1",
            "duplicate_dispatch_key_count=0",
            "duplicate_row_id_count=0",
        },
        "R10-HM-BOUND-005": {
            "preview_row_delta=9",
            "PK-EFFECTFUL-EXTRACTOR_reachable=false",
            "PK-BACKTRACKING_reachable=false",
        },
        "R10-HM-BOUND-006": {
            "argument_kind_row_reused=true",
            "projection_key_shape=(HirBodyId,HirNodeId,LoweringRuleId)",
            "duplicate_projection_key_count=0",
        },
        "R10-HM-BOUND-007": {
            "row_disposition=LOWER",
            "capability_gate_result=REJECT",
            "input_hir_semantic_digest=preserved_hir_semantic_digest",
            "canonical_hir_retained=true",
            "executable_hir_created=false",
        },
        "R10-HM-BOUND-008": {
            "structural_schema_identity_count=18",
            "structural_schema_independent_row_count=0",
            "identity_catalog_count=130",
        },
        "R10-HM-NEG-013": {
            "pair=ACTOR_MESSAGE::VIRTUAL_SLOT",
            "rejected_before_canonical_hir=true",
            "source_diagnostic_id=RECEIVER_MODE_MISMATCH",
            "new_r10_source_diagnostic_created=false",
        },
    }
    for case_id, expected_assertions in registry_backed_assertions.items():
        report.require(
            expected_assertions <= assertions(case_id),
            6,
            "R10_HM_DIAGNOSTIC_BINDING_INVALID",
            f"{case_id} registry-backed assertion binding is incomplete",
        )

    report.require(
        facts.get("current_row_count") == 102
        and facts.get("preview_row_count") == 9
        and facts.get("family_counts") == EXPECTED_FAMILY_COUNTS
        and facts.get("structural_row_count") == 0
        and facts.get("pre_hir_row_count") == 0,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "coverage/profile fixture assertions are not supported by registry facts",
    )
    report.require(
        facts.get("call_pairs") == set(VALID_CALL_PAIRS)
        and {
            pair for pair in facts.get("call_pairs", set()) if pair.startswith("ACTOR_MESSAGE")
        }
        == {"ACTOR_MESSAGE::ACTOR_TRANSPORT"}
        and {
            pair
            for pair in facts.get("call_pairs", set())
            if pair.endswith("RESERVED_OPERATION")
        }
        == {"MESSAGE::RESERVED_OPERATION"}
        and "ACTOR_MESSAGE::VIRTUAL_SLOT" not in facts.get("call_pairs", set()),
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "call-matrix fixture assertions are not supported by registry facts",
    )
    report.require(
        facts.get("shared_template_count", 0) >= 1
        and facts.get("duplicate_dispatch_key_count") == 0
        and facts.get("duplicate_row_id_count") == 0,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "shared-template/uniqueness fixture assertions are not supported",
    )
    gate = facts.get("capability_gate", {})
    report.require(
        gate.get("boundary") == "EXECUTABLE_HIR_GATE"
        and gate.get("lowering_row_disposition_on_missing_capability") == "LOWER"
        and gate.get("verified_canonical_hir_effect") == "PRESERVE"
        and gate.get("executable_hir_created") is False,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "capability-boundary fixture assertions are not supported",
    )
    report.require(
        facts.get("argument_row_count") == 7
        and facts.get("provenance_key_shapes")
        == {"(HirBodyId,HirNodeId,LoweringRuleId)"},
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "argument-row/provenance fixture assertions are not supported",
    )

    expected_counts = fixtures.get("expected_counts", {})
    report.require(
        expected_counts.get("cases") == len(cases)
        and expected_counts.get("positive") == class_counts["positive"]
        and expected_counts.get("boundary") == class_counts["boundary"]
        and expected_counts.get("negative") == class_counts["negative"]
        and expected_counts.get("mutation") == class_counts["mutation"]
        and expected_counts.get("internal_diagnostic_ids") == len(new_internal)
        and expected_counts.get("reused_internal_diagnostic_ids")
        == len(existing_diagnostics - {"RECEIVER_MODE_MISMATCH"})
        and expected_counts.get("repository_only_failure_ids")
        == len(repository_failures)
        and expected_counts.get("source_level_new_diagnostic_ids")
        == diagnostics.get("classification_rule", {}).get(
            "new_source_level_diagnostic_count"
        )
        and expected_counts.get("identity_catalog")
        == facts.get("identity_catalog_count")
        and expected_counts.get("current_rows") == facts.get("current_row_count")
        and expected_counts.get("preview_max_rows") == facts.get("row_count")
        and expected_counts.get("product_lanes") == 15
        and expected_counts.get("product_executed") == 0,
        6,
        "R10_HM_DIAGNOSTIC_BINDING_INVALID",
        "fixture expected_counts do not bind the computed contract facts",
    )
    return len(cases)


def check_status_fence(
    report: Report, docs: dict[str, dict[str, Any]]
) -> None:
    if "registry" in docs:
        registry = docs["registry"]
        expected = {
            **EXPECTED_STATUS_FENCE,
            "product_execution": "NOT_RUN",
            "r31_closure_capture_plan_projection": "DESIGN_ONLY_NOT_RUN",
            "r32_deferred_call_plan_projection": "DESIGN_ONLY_NOT_RUN",
            "new_mir_operation_kind_count": 0,
            "module_api_value_level_identity_export_count": 0,
        }
        report.require(
            registry.get("status")
            == "DESIGN_REGISTRY_NOT_IMPLEMENTATION_OR_EXECUTION_EVIDENCE"
            and registry.get("status_fence") == expected
            and all(
                row.get("product_support") == "NOT_RUN"
                for row in registry.get("rows", [])
                if isinstance(row, dict)
            ),
            7,
            "R10_HM_PRODUCT_STATUS_OVERCLAIM",
            "lowering registry status fence overclaims implementation or execution",
        )
    for label in ("fixtures", "diagnostics"):
        if label in docs:
            report.require(
                docs[label].get("status_fence") == EXPECTED_STATUS_FENCE,
                7,
                "R10_HM_PRODUCT_STATUS_OVERCLAIM",
                f"{label} status fence differs from the locked design-only fence",
            )
    if "fixtures" in docs:
        report.require(
            docs["fixtures"].get("status") == "DESIGN_STATIC_NOT_RUN",
            7,
            "R10_HM_PRODUCT_STATUS_OVERCLAIM",
            "fixture status claims execution",
        )
    if "diagnostics" in docs:
        report.require(
            docs["diagnostics"].get("status") == "STABLE_DESIGN",
            7,
            "R10_HM_PRODUCT_STATUS_OVERCLAIM",
            "diagnostic contract status is not STABLE_DESIGN",
        )
    if "hir_catalog" in docs:
        report.require(
            docs["hir_catalog"].get("status")
            == "CURRENT_STABLE_DESIGN_MACHINE_SCHEMA",
            7,
            "R10_HM_PRODUCT_STATUS_OVERCLAIM",
            "HIR catalog status is not the current Stable-design machine schema",
        )
    if "mir_registry" in docs:
        status = docs["mir_registry"].get("status_fence", {})
        report.require(
            docs["mir_registry"].get("status")
            == "DESIGN_REGISTRY_NOT_IMPLEMENTATION_OR_EXECUTION_EVIDENCE"
            and status.get("design_registry_only") is True
            and status.get("provided_capability_receipt_emitted") is False
            and status.get("product_lanes") == "15_OF_15_NOT_RUN"
            and status.get("product_execution") == "NOT_RUN"
            and status.get("canonical_source_mutation") == 0
            and status.get("github_mutation") == 0,
            7,
            "R10_HM_PRODUCT_STATUS_OVERCLAIM",
            "MIR registry status fence overclaims implementation or evidence",
        )


def check_schema_closed_sets(
    report: Report,
    docs: dict[str, dict[str, Any]],
    mir_contract: tuple[
        dict[str, str],
        set[str],
        set[str],
        set[str],
        dict[str, set[str]],
        dict[str, dict[str, set[str]]],
    ],
) -> None:
    if "row_schema" not in docs:
        return
    row_schema = docs["row_schema"]
    (
        operation_map,
        terminator_set,
        token_set,
        capability_set,
        _,
        _,
    ) = mir_contract
    defs = row_schema.get("$defs", {})
    report.require(
        set(defs.get("operationKind", {}).get("enum", [])) == set(operation_map)
        and len(defs.get("operationKind", {}).get("enum", [])) == 48,
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema operation enum differs from MIR registry",
    )
    report.require(
        set(defs.get("operationPlanStep", {}).get("properties", {}).get(
            "semantic_operation_id", {}
        ).get("enum", []))
        == set(operation_map.values()),
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema semantic-operation enum differs from total map",
    )
    report.require(
        set(defs.get("terminatorKind", {}).get("enum", [])) == terminator_set,
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema terminator enum differs from MIR registry",
    )
    report.require(
        set(defs.get("tokenKind", {}).get("enum", [])) == token_set,
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema token enum differs from MIR registry",
    )
    report.require(
        set(defs.get("capabilityId", {}).get("enum", [])) == capability_set,
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema capability enum differs from MIR registry",
    )
    report.require(
        row_schema.get("properties", {}).get("disposition", {}).get("enum")
        == ["LOWER", "NO_RUNTIME_EMISSION"],
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema disposition enum is not the exact two-entry set",
    )
    report.require(
        row_schema.get("properties", {}).get("profile_gate", {}).get("enum")
        == ["CURRENT", "EXPLICIT_PREVIEW"],
        1,
        "JSON_SCHEMA_VALIDATION_FAILURE",
        "lowering-row schema profile enum is not the exact machine vocabulary",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=ROOT,
        help="canonical or applied-candidate workspace root",
    )
    args = parser.parse_args()
    global PATHS
    PATHS = canonical_paths(args.root.resolve())
    report = Report()
    docs = load_documents(report)
    if set(docs) != set(PATHS):
        pass
    else:
        check_schema_and_bindings(report, docs)
        identity_set, expected_dispatch = check_hir_catalog(report, docs)
        mir_contract = check_mir_registry(report, docs)
        check_schema_closed_sets(report, docs, mir_contract)
        facts = check_rows(
            report,
            docs,
            identity_set,
            expected_dispatch,
            mir_contract,
        )
        fixture_binding_count = check_fixture_bindings(report, docs, facts)
        check_status_fence(report, docs)

    if report.errors:
        print("R10 HIR/MIR MACHINE CONTRACT: FAIL")
        for stage, code, message in sorted(report.errors):
            print(f"  preflight[{stage}] {code}: {message}")
        print(
            "LIMITATIONS: design-static focused validation only; no compiler, "
            "product lane, target projection, capability evidence receipt, "
            "canonical source, package, GitHub, or external execution."
        )
        return 1

    registry = docs["registry"]
    rows = registry["rows"]
    current_count = sum(row["profile_gate"] == "CURRENT" for row in rows)
    preview_count = len(rows) - current_count
    print("R10 HIR/MIR MACHINE CONTRACT: PASS")
    print(
        "  HIR identities=130; lowering rows="
        f"{len(rows)} ({current_count} CURRENT + {preview_count} EXPLICIT_PREVIEW)"
    )
    print(
        "  MIR operations=48; terminators=17; tokens=12; "
        "capabilities=26; capability graph=ACYCLIC"
    )
    print(
        f"  fixture bindings={fixture_binding_count}; product executions=0; "
        "canonical/GitHub mutations=0"
    )
    print(
        "LIMITATIONS: design-static focused validation only; no compiler, "
        "product lane, target projection, capability evidence receipt, "
        "canonical source, package, GitHub, or external execution."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
