#!/usr/bin/env python3
"""Reject bounded mutations of the R4 name-resolution/module contract."""

from __future__ import annotations

import json
import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from validate_workspace import (
    R4_NRM_ACCEPTANCE_ARTIFACT_REFS,
    R4_NRM_ACCEPTANCE_ORACLE_SHA256,
    R4_NRM_INTEGRATED_PATHS,
    R4_NRM_TARGET_FILES,
    r4_nrm_contract_results,
    r4_nrm_integrated_contract_results,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_RELATIVE = "spec/contracts/name-resolution-modules-current.json"
FIXTURE_RELATIVE = (
    "tests/fixtures/current/name-resolution-modules-current-r1.json"
)
SCHEMA_RELATIVE = (
    "schemas/language/name-resolution-modules-current-fixtures.schema.json"
)
EXPECTED_GAP_IDS = (
    "IR-RES-P0-040",
    "IR-RES-P0-041",
    "IR-MOD-P1-042",
    "IR-MOD-P1-043",
    "IR-MOD-P1-044",
    "IR-MOD-P1-045",
    "IR-MOD-P1-046",
    "IR-MOD-P1-047",
    "IR-RES-P1-048",
    "IR-RES-P1-049",
    "IR-TRACE-P1-050",
    "IR-TRACE-P2-051",
)
EXPECTED_TEST_CLASSES = ("positive", "boundary", "negative")
EXPECTED_TEST_SUFFIXES = ("P", "B", "N")
EXPECTED_TEST_IDS = tuple(
    f"IR-R4-GAP-{gap_number:02d}-{suffix}"
    for gap_number in range(1, 13)
    for suffix in EXPECTED_TEST_SUFFIXES
)
ORACLE_REFERENCE_FILES = (
    "schemas/language/method-extension-resolution-trace-schema.json",
    "schemas/language/module-api-digest.schema.json",
    "schemas/language/module-compilation-dependency-receipt.schema.json",
    "schemas/language/module-implementation-digest.schema.json",
    "schemas/language/module-initialization-plan.schema.json",
    "schemas/language/module-visibility-closure.schema.json",
    "schemas/language/package-module-source-graph.schema.json",
    "schemas/language/resolver-graph.schema.json",
    "schemas/language/resolver-trace.schema.json",
    "schemas/language/source-role-carrier.schema.json",
    "schemas/language/top-level-type-visibility-descriptor.schema.json",
    "spec/contracts/hir-h1-current-mir-bridge.json",
)
ORACLE_COPY_ONLY_FILES = (
    "schemas/language/module-source-contribution-projection.schema.json",
    "schemas/language/module-compilation-receipt.schema.json",
    "tests/fixtures/current/module-compilation-artifact-relations-r1.json",
)
MODULE_ARTIFACT_FIXTURE_RELATIVE = (
    "tests/fixtures/current/module-compilation-artifact-relations-r1.json"
)
R4_ORACLE_TARGET_FILES = (
    CONTRACT_RELATIVE,
    FIXTURE_RELATIVE,
    SCHEMA_RELATIVE,
    *ORACLE_REFERENCE_FILES,
    *ORACLE_COPY_ONLY_FILES,
)


def read_json(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def write_json(
    root: Path, relative: str, value: Any
) -> None:
    path = root / relative
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def reseal_json_self_hash(value: dict[str, Any], field: str) -> None:
    payload = json.loads(json.dumps(value))
    payload.pop(field, None)
    value[field] = canonical_sha256(payload)


def r4_oracle_contract_results(
    root: Path,
) -> list[tuple[bool, str, str]]:
    contract = read_json(root, CONTRACT_RELATIVE)
    fixture = read_json(root, FIXTURE_RELATIVE)
    schema = read_json(root, SCHEMA_RELATIVE)

    oracles = contract.get("acceptance_oracles", [])
    cases = fixture.get("cases", [])
    expected_outcomes = [
        row.get("expected_outcome") for row in oracles
    ]
    expected_diagnostics = {
        row.get("primary_diagnostic_or_null")
        for row in oracles
        if row.get("primary_diagnostic_or_null") is not None
    }
    expected_reasons = {
        row.get("primary_reason_or_null")
        for row in oracles
        if row.get("primary_reason_or_null") is not None
    }
    expected_suppressed_diagnostics = {
        diagnostic
        for row in oracles
        for diagnostic in row.get("suppressed_diagnostics", [])
    }

    oracle_contract_ok = (
        len(oracles) == 36
        and canonical_sha256(oracles)
        == R4_NRM_ACCEPTANCE_ORACLE_SHA256
        and [row.get("test_id") for row in oracles]
        == list(EXPECTED_TEST_IDS)
    )

    fixture_ids = [row.get("acceptance_test_id") for row in cases]
    case_set_ok = (
        len(cases) == 36
        and fixture_ids == list(EXPECTED_TEST_IDS)
        and len(set(fixture_ids)) == 36
    )

    expected_gap_kind_pairs = {
        (gap_id, test_class)
        for gap_id in EXPECTED_GAP_IDS
        for test_class in EXPECTED_TEST_CLASSES
    }
    observed_gap_kind_pairs = {
        (row.get("gap_id"), row.get("kind")) for row in cases
    }
    gap_kind_ok = (
        len(cases) == 36
        and observed_gap_kind_pairs == expected_gap_kind_pairs
        and len(observed_gap_kind_pairs) == 36
    )

    binding_ok = len(oracles) == len(cases) == 36
    for oracle, case in zip(oracles, cases):
        expected = case.get("expected", {})
        invariant = expected.get("invariants", {})
        expected_verdict = (
            "REJECT"
            if str(oracle.get("expected_outcome", "")).startswith(
                "REJECT"
            )
            else "ACCEPT"
        )
        binding_ok = binding_ok and all(
            (
                case.get("acceptance_test_id")
                == oracle.get("test_id"),
                oracle.get("gap_ids") == [case.get("gap_id")],
                case.get("kind") == oracle.get("test_class"),
                case.get("scenario") == oracle.get("scenario"),
                case.get("input", {}).get("description")
                == oracle.get("scenario"),
                expected.get("verdict") == expected_verdict,
                expected.get("outcome")
                == oracle.get("expected_outcome"),
                expected.get("primary_diagnostic_or_null")
                == oracle.get("primary_diagnostic_or_null"),
                expected.get("primary_reason_or_null")
                == oracle.get("primary_reason_or_null"),
                expected.get("suppressed_diagnostics")
                == oracle.get("suppressed_diagnostics"),
                oracle.get("execution") == "PROPOSED_OUTLINE_NOT_RUN",
                oracle.get("product_lanes") == "15/15_NOT_RUN",
                oracle.get("candidate_oracle_status")
                == "EXACT_DESIGN_ORACLE_NOT_RUN",
                invariant.get("product_execution_count") == 0,
            )
        )
    binding_ok = binding_ok and all(
        (
            fixture.get("semantic_p0") == 0,
            fixture.get("open_feature_p1") == 22,
            fixture.get("product_lanes") == "15/15_NOT_RUN",
            fixture.get("status")
            == "DESIGN_STATIC_FIXTURES_NOT_EXECUTED",
        )
    )

    cases_schema = schema.get("properties", {}).get("cases", {})
    case_schema = schema.get("$defs", {}).get("case", {})
    expected_schema = schema.get("$defs", {}).get("expected", {})
    primary_diagnostic_schema = (
        expected_schema.get("properties", {})
        .get("primary_diagnostic_or_null", {})
        .get("oneOf", [{}])[0]
    )
    primary_reason_schema = (
        expected_schema.get("properties", {})
        .get("primary_reason_or_null", {})
        .get("oneOf", [{}])[0]
    )
    suppressed_schema = (
        expected_schema.get("properties", {})
        .get("suppressed_diagnostics", {})
        .get("items", {})
    )
    primary_diagnostic_domain = set(
        primary_diagnostic_schema.get("enum", [])
    )
    suppressed_diagnostic_domain = set(
        suppressed_schema.get("enum", [])
    )
    schema_ok = all(
        (
            cases_schema.get("minItems") == 36,
            cases_schema.get("maxItems") == 36,
            set(case_schema.get("required", []))
            == {
                "id",
                "acceptance_test_id",
                "gap_id",
                "kind",
                "category",
                "scenario",
                "input",
                "expected",
            },
            case_schema.get("properties", {})
            .get("acceptance_test_id", {})
            .get("enum")
            == list(EXPECTED_TEST_IDS),
            case_schema.get("properties", {})
            .get("kind", {})
            .get("enum")
            == list(EXPECTED_TEST_CLASSES),
            case_schema.get("properties", {})
            .get("expected", {})
            .get("$ref")
            == "#/$defs/expected",
            set(expected_schema.get("required", []))
            == {
                "verdict",
                "outcome",
                "primary_diagnostic_or_null",
                "primary_reason_or_null",
                "suppressed_diagnostics",
                "selected_count_or_null",
                "invariants",
            },
            expected_schema.get("properties", {})
            .get("outcome", {})
            .get("enum")
            == expected_outcomes,
            expected_diagnostics <= primary_diagnostic_domain,
            set(primary_reason_schema.get("enum", []))
            == expected_reasons,
            suppressed_diagnostic_domain == primary_diagnostic_domain,
            expected_suppressed_diagnostics
            <= suppressed_diagnostic_domain,
        )
    )

    referenced_paths = {
        reference
        for case in cases
        for reference in case.get("input", {}).get(
            "artifact_refs", []
        )
    }
    expected_reference_paths = {
        reference
        for references in R4_NRM_ACCEPTANCE_ARTIFACT_REFS.values()
        for reference in references
    } | {CONTRACT_RELATIVE}
    artifact_refs_ok = (
        referenced_paths == expected_reference_paths
        and all((root / reference).is_file() for reference in referenced_paths)
    )

    return [
        (
            oracle_contract_ok,
            "R4_NRM_ORACLE_CONTRACT",
            "frozen 36-row acceptance oracle identity and order",
        ),
        (
            case_set_ok,
            "R4_NRM_ORACLE_CASE_SET",
            "exact ordered 36-case acceptance-test identity set",
        ),
        (
            gap_kind_ok,
            "R4_NRM_ORACLE_GAP_KIND",
            "one positive, boundary, and negative case per frozen gap",
        ),
        (
            binding_ok,
            "R4_NRM_ORACLE_BINDING",
            "fixture scenarios and expected results bind to frozen oracles",
        ),
        (
            schema_ok,
            "R4_NRM_ORACLE_SCHEMA",
            "fixture schema freezes cardinality and oracle value domains",
        ),
        (
            artifact_refs_ok,
            "R4_NRM_ORACLE_ARTIFACT_REFS",
            "all and only frozen artifact references resolve",
        ),
    ]


def copy_contract_tree(target: Path) -> None:
    for relative in dict.fromkeys(
        (
            *R4_NRM_TARGET_FILES,
            *R4_ORACLE_TARGET_FILES,
            *R4_NRM_INTEGRATED_PATHS,
        )
    ):
        source = ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def delete_new_diagnostic(root: Path) -> None:
    relative = "spec/diagnostics/catalog/chunks/part-0027.json"
    rows = read_json(root, relative)
    del rows[0]
    write_json(root, relative, rows)


def add_new_diagnostic(root: Path) -> None:
    relative = "spec/diagnostics/catalog/chunks/part-0027.json"
    rows = read_json(root, relative)
    rows.append(dict(rows[-1]))
    write_json(root, relative, rows)


def claim_product_support(root: Path) -> None:
    relative = "spec/diagnostics/catalog/chunks/part-0027.json"
    rows = read_json(root, relative)
    rows[0]["product_support"] = "PASS"
    write_json(root, relative, rows)


def delete_primary_relation(root: Path) -> None:
    relative = "spec/diagnostics/relations/chunks/part-0007.json"
    rows = read_json(root, relative)
    del rows[0]
    write_json(root, relative, rows)


def swap_predicate_precedence(root: Path) -> None:
    relative = "spec/types/predicates/chunks/part-0018.json"
    rows = read_json(root, relative)
    rows[0], rows[1] = rows[1], rows[0]
    write_json(root, relative, rows)


def delete_reason_dispatch(root: Path) -> None:
    relative = "spec/types/predicates/chunks/part-0018.json"
    rows = read_json(root, relative)
    del rows[0]["diagnostic_dispatch"]["PACKAGE_TARGET_MISSING"]
    write_json(root, relative, rows)


def change_dependency_prefix(root: Path) -> None:
    relative = "spec/types/predicates/chunks/part-0018.json"
    rows = read_json(root, relative)
    rows[1]["dependency_predicates"] = []
    write_json(root, relative, rows)


def delete_fixture(root: Path) -> None:
    relative = (
        "tests/conformance/checker-predicates/chunks/part-0028.json"
    )
    rows = read_json(root, relative)
    del rows[0]
    write_json(root, relative, rows)


def change_negative_fixture_binding(root: Path) -> None:
    relative = (
        "tests/conformance/checker-predicates/chunks/part-0028.json"
    )
    rows = read_json(root, relative)
    row = next(
        item
        for item in rows
        if item["fixture_id"]
        == "PF-PackageModuleSourceGraphAdmitted-NEG"
    )
    row["expected_primary_diagnostic"] = "MODULE_ITEM_SKELETON_CONFLICT"
    write_json(root, relative, rows)


def drift_predicate_fixture_tuple(root: Path) -> None:
    relative = (
        "tests/conformance/checker-predicates/chunks/part-0028.json"
    )
    rows = read_json(root, relative)
    rows[0]["descriptor"]["scenario"] += " [mutated]"
    write_json(root, relative, rows)


def retire_member_collision_primary(root: Path) -> None:
    relative = "spec/diagnostics/catalog/chunks/part-0011.json"
    rows = read_json(root, relative)
    row = next(
        item
        for item in rows
        if item["diagnostic_id"] == "MEMBER_EXTENSION_COLLISION"
    )
    row["diagnostic_status"] = "retired"
    write_json(root, relative, rows)


def break_stable_collision_alias(root: Path) -> None:
    relative = "spec/diagnostics/relations/chunks/part-0001.json"
    rows = read_json(root, relative)
    row = next(
        item
        for item in rows
        if item["diagnostic_id"] == "STABLE_MEMBER_EXTENSION_COLLISION"
    )
    row["replacement"] = "EXTENSION_SHADOWED_BY_MEMBER_COMPAT"
    write_json(root, relative, rows)


def absorb_callable_overload_cluster(root: Path) -> None:
    relative = "spec/types/predicates/chunks/part-0018.json"
    rows = read_json(root, relative)
    row = next(
        item
        for item in rows
        if item["predicate_id"] == "ResolvedNoncallReferenceSelected"
    )
    row["summary"] = "Select one deterministic reference."
    row["output"] = "admit(ResolvedRef) | reject(reason)"
    row["requires"] = [
        "only noncall reference namespaces are eligible for winner selection",
        "source enumeration order is not a tie-breaker",
    ]
    row["decision_procedure"] = [
        "filter to the exact namespace and lowest reachable lookup tier",
        "reject zero or multiple candidates after filtering",
        "otherwise commit one existing typed ResolvedRef",
    ]
    row["success_result"] = "ResolvedRef"
    write_json(root, relative, rows)


def absorb_method_extension_winner(root: Path) -> None:
    relative = "spec/types/predicates/chunks/part-0008.json"
    rows = read_json(root, relative)
    row = next(
        item
        for item in rows
        if item["predicate_id"] == "MethodExtensionResolutionAdmitted"
    )
    row["decision_procedure"].append(
        "commit one statically selected method or extension identity"
    )
    row["success_result"] = (
        "admit(one static method or extension identity)"
    )
    write_json(root, relative, rows)


def break_closed_collision_selected_count(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    row = next(
        case
        for case in fixture["cases"]
        if case["id"] == "IR-R4-RES041-POS"
    )
    row["expected"]["selected_count_or_null"] = 2
    write_json(root, FIXTURE_RELATIVE, fixture)


def replace_common_visibility_with_package(root: Path) -> None:
    relative = "schemas/language/module-visibility-closure.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["visibility"]["enum"] = [
        "private",
        "package",
        "public",
    ]
    write_json(root, relative, schema)


def add_module_visibility_domain(root: Path) -> None:
    relative = "schemas/language/module-visibility-closure.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["visibility"]["enum"].insert(1, "module")
    write_json(root, relative, schema)


def delete_acceptance_oracle(root: Path) -> None:
    contract = read_json(root, CONTRACT_RELATIVE)
    del contract["acceptance_oracles"][-1]
    write_json(root, CONTRACT_RELATIVE, contract)


def duplicate_acceptance_test_id(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    fixture["cases"][1]["acceptance_test_id"] = fixture["cases"][0][
        "acceptance_test_id"
    ]
    write_json(root, FIXTURE_RELATIVE, fixture)


def change_oracle_scenario_binding(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    fixture["cases"][0]["scenario"] = "mutated scenario"
    write_json(root, FIXTURE_RELATIVE, fixture)


def change_oracle_outcome_binding(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    fixture["cases"][0]["expected"]["outcome"] = (
        "ACCEPT_DISTINCT_HIR_LOCAL_IDS_AND_RESTORE"
    )
    write_json(root, FIXTURE_RELATIVE, fixture)


def change_oracle_diagnostic_binding(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    row = next(
        case
        for case in fixture["cases"]
        if case["expected"]["primary_diagnostic_or_null"] is not None
    )
    row["expected"]["primary_diagnostic_or_null"] = (
        "MODULE_ITEM_SKELETON_CONFLICT"
    )
    write_json(root, FIXTURE_RELATIVE, fixture)


def change_oracle_reason_binding(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    row = next(
        case
        for case in fixture["cases"]
        if case["expected"]["primary_reason_or_null"] is not None
    )
    row["expected"]["primary_reason_or_null"] = "IMPORT_TARGET_NOT_FOUND"
    write_json(root, FIXTURE_RELATIVE, fixture)


def change_oracle_suppression_binding(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    row = next(
        case
        for case in fixture["cases"]
        if case["expected"]["suppressed_diagnostics"]
    )
    row["expected"]["suppressed_diagnostics"] = []
    write_json(root, FIXTURE_RELATIVE, fixture)


def weaken_oracle_schema_cardinality(root: Path) -> None:
    schema = read_json(root, SCHEMA_RELATIVE)
    schema["properties"]["cases"]["maxItems"] = 37
    write_json(root, SCHEMA_RELATIVE, schema)


def drift_per_test_artifact_refs(root: Path) -> None:
    fixture = read_json(root, FIXTURE_RELATIVE)
    fixture["cases"][0]["input"]["artifact_refs"].append(
        CONTRACT_RELATIVE
    )
    write_json(root, FIXTURE_RELATIVE, fixture)


def genericize_package_identity(root: Path) -> None:
    relative = (
        "schemas/language/package-module-source-graph.schema.json"
    )
    schema = read_json(root, relative)
    schema["$defs"]["packageId"]["pattern"] = (
        r"^[A-Za-z][A-Za-z0-9]*:[^\s]+$"
    )
    write_json(root, relative, schema)


def allow_empty_package_owner_set(root: Path) -> None:
    relative = (
        "schemas/language/package-module-source-graph.schema.json"
    )
    schema = read_json(root, relative)
    schema["properties"]["packages"]["minItems"] = 0
    write_json(root, relative, schema)


def mutate_first_property_const(
    value: Any,
    property_name: str,
    replacement: Any,
) -> bool:
    if isinstance(value, dict):
        properties = value.get("properties")
        if (
            isinstance(properties, dict)
            and isinstance(properties.get(property_name), dict)
            and "const" in properties[property_name]
        ):
            properties[property_name]["const"] = replacement
            return True
        return any(
            mutate_first_property_const(
                child, property_name, replacement
            )
            for child in value.values()
        )
    if isinstance(value, list):
        return any(
            mutate_first_property_const(
                child, property_name, replacement
            )
            for child in value
        )
    return False


def drift_first_resolver_trace_stage(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    first_stage = (
        schema["$defs"]["referenceTrace"]["properties"]["stages"][
            "prefixItems"
        ][0]
    )
    if not mutate_first_property_const(
        first_stage,
        "predicate",
        "ModuleInterfaceDigestVerified",
    ):
        raise ValueError("resolver trace predicate const not found")
    write_json(root, relative, schema)


def drift_module_initialization_decl_id_refs(root: Path) -> None:
    relative = "schemas/language/module-initialization-plan.schema.json"
    schema = read_json(root, relative)
    binding = schema["$defs"]["binding"]["properties"]
    binding["binding_decl_id"]["$ref"] = "#/$defs/moduleId"
    binding["dependency_decl_ids"]["items"]["$ref"] = "#/$defs/moduleId"
    write_json(root, relative, schema)


def drift_trace_diagnostic_order(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    schema["properties"]["diagnostic_order"]["const"] = (
        "SOURCE_ORIGIN_ORDER"
    )
    write_json(root, relative, schema)


def unbind_trace_diagnostic_selection(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    del schema["$defs"]["diagnosticSelection"]["oneOf"]
    write_json(root, relative, schema)


def drift_trace_zero_seal_counter(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["zeroSealCounters"]["allOf"][1]["properties"][
        "unresolved_count"
    ]["const"] = 1
    write_json(root, relative, schema)


def drift_hir_r4_exact_bridge_row(root: Path) -> None:
    relative = (
        "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json"
    )
    fixture = read_json(root, relative)
    row = next(
        item
        for item in fixture["r4_name_resolution_module_bridge_cases"]
        if item["fixture_id"] == "H1MB-R4-NRM-POS-002"
    )
    row["canonical_hir_projection"] = "ResolvedRef::DirectDecl(DeclId)"
    write_json(root, relative, fixture)


def drop_module_api_r4_envelope_requirement(root: Path) -> None:
    relative = "schemas/language/module-api-digest.schema.json"
    schema = read_json(root, relative)
    removed = False
    for clause in schema.get("allOf", []):
        required = clause.get("then", {}).get("required", [])
        if "r4_interface_envelope" in required:
            required.remove("r4_interface_envelope")
            removed = True
            break
    if not removed:
        raise ValueError("R4 module API envelope requirement not found")
    write_json(root, relative, schema)


def drop_receipt_interface_digest_binding(root: Path) -> None:
    relative = (
        "schemas/language/"
        "module-compilation-dependency-receipt.schema.json"
    )
    schema = read_json(root, relative)
    required = schema["$defs"]["requiredInterface"]["required"]
    required.remove("interface_sha256")
    write_json(root, relative, schema)


def allow_envelope_without_r4_profile(root: Path) -> None:
    relative = "schemas/language/module-api-digest.schema.json"
    schema = read_json(root, relative)
    clause = next(
        row
        for row in schema["allOf"]
        if "r4_interface_envelope"
        in row.get("then", {}).get("required", [])
    )
    del clause["else"]
    write_json(root, relative, schema)


def genericize_public_export_identity(root: Path) -> None:
    relative = "schemas/language/module-api-digest.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["r4PublicExportRow"]["properties"][
        "referenced_identity_id"
    ]["pattern"] = r"^[A-Za-z][A-Za-z0-9]*:[^\s]+$"
    write_json(root, relative, schema)


def leak_provenance_into_public_interface(root: Path) -> None:
    relative = "schemas/language/module-api-digest.schema.json"
    schema = read_json(root, relative)
    excluded = schema[
        "x-deeplus-r4-module-interface-contract"
    ]["excluded_identity_inputs"]
    excluded.remove("visibility_closure_sha256")
    write_json(root, relative, schema)


def add_source_projection_extra_row(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    projection = fixture["cases"][0][
        "module_source_contribution_projection"
    ]
    extra = json.loads(
        json.dumps(projection["source_contributions"][0])
    )
    extra.update(
        {
            "source_file_id": "SourceFileId:acme/src/extra.dp",
            "normalized_project_relative_path": "src/extra.dp",
            "source_bytes_sha256": "e" * 64,
        }
    )
    projection["source_contributions"].append(extra)
    projection["source_contributions"].sort(
        key=lambda row: row["source_file_id"]
    )
    reseal_json_self_hash(projection, "projection_sha256")
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_source_projection_owner(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    projection = fixture["cases"][0][
        "module_source_contribution_projection"
    ]
    projection["module_id"] = "ModuleId:acme.other"
    reseal_json_self_hash(projection, "projection_sha256")
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_implementation_interface(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    implementation = fixture["cases"][0]["implementation_digest"]
    implementation["interface_sha256"] = "9" * 64
    reseal_json_self_hash(implementation, "implementation_sha256")
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_compilation_artifact_binding(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    compilation = fixture["cases"][0]["compilation_receipt"]
    compilation["module_source_contribution_sha256"] = "a" * 64
    reseal_json_self_hash(
        compilation, "compilation_receipt_sha256"
    )
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def break_compilation_receipt_self_hash(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    fixture["cases"][0]["compilation_receipt"][
        "compilation_receipt_sha256"
    ] = "0" * 64
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def false_private_change_matrix_claim(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    fixture["expected_relations"][
        "interface_sha256_equal_across_cases"
    ] = False
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def reseal_compilation_receipt(case: dict[str, Any]) -> None:
    reseal_json_self_hash(
        case["compilation_receipt"],
        "compilation_receipt_sha256",
    )


def rebind_trace_chain(case: dict[str, Any]) -> None:
    trace = case["resolver_trace"]
    reseal_json_self_hash(trace, "trace_sha256")
    case["compilation_receipt"]["resolver_trace_sha256"] = trace[
        "trace_sha256"
    ]
    reseal_compilation_receipt(case)


def rebind_dependency_chain(case: dict[str, Any]) -> None:
    receipt = case["dependency_receipt"]
    reseal_json_self_hash(receipt, "dependency_receipt_sha256")
    case["compilation_receipt"]["dependency_receipt_sha256"] = (
        receipt["dependency_receipt_sha256"]
    )
    reseal_compilation_receipt(case)


def rebind_resolver_chain(case: dict[str, Any]) -> None:
    resolver = case["resolver_graph"]
    reseal_json_self_hash(resolver, "resolver_graph_sha256")
    resolver_sha256 = resolver["resolver_graph_sha256"]
    case["resolver_trace"]["resolver_graph_sha256"] = resolver_sha256
    reseal_json_self_hash(case["resolver_trace"], "trace_sha256")
    case["dependency_receipt"][
        "resolver_graph_sha256"
    ] = resolver_sha256
    reseal_json_self_hash(
        case["dependency_receipt"],
        "dependency_receipt_sha256",
    )
    compilation = case["compilation_receipt"]
    compilation["resolver_trace_sha256"] = case["resolver_trace"][
        "trace_sha256"
    ]
    compilation["dependency_receipt_sha256"] = case[
        "dependency_receipt"
    ]["dependency_receipt_sha256"]
    reseal_compilation_receipt(case)


def rebind_package_chain(case: dict[str, Any]) -> None:
    package_graph = case["package_graph"]
    reseal_json_self_hash(
        package_graph, "canonical_graph_sha256"
    )
    package_sha256 = package_graph["canonical_graph_sha256"]
    case["resolver_graph"]["package_graph_sha256"] = package_sha256
    case["dependency_receipt"][
        "package_graph_sha256"
    ] = package_sha256
    case["compilation_receipt"][
        "package_graph_sha256"
    ] = package_sha256
    rebind_resolver_chain(case)


def rebind_source_projection(case: dict[str, Any]) -> None:
    projection = case["module_source_contribution_projection"]
    reseal_json_self_hash(projection, "projection_sha256")
    case["compilation_receipt"][
        "module_source_contribution_sha256"
    ] = projection["projection_sha256"]
    reseal_compilation_receipt(case)


def insert_lone_surrogate_escape(root: Path) -> None:
    path = root / MODULE_ARTIFACT_FIXTURE_RELATIVE
    source = '"product_compiler_execution": "NOT_RUN"'
    replacement = (
        '"product_compiler_execution": "NOT_RUN\\ud800"'
    )
    text = path.read_text(encoding="utf-8")
    if text.count(source) != 1:
        raise ValueError("product execution marker is not unique")
    path.write_text(
        text.replace(source, replacement, 1),
        encoding="utf-8",
    )


def inject_float_canonical_value(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    fixture["cases"][0]["resolver_trace"]["references"][0][
        "source_span"
    ]["start"] = 96.5
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def add_closed_package_graph_field(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    case["package_graph"]["unexpected_relation_field"] = (
        "NOT_SCHEMA_ADMITTED"
    )
    rebind_package_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def reverse_resolver_scope_order(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    case["resolver_graph"]["scopes"].reverse()
    rebind_resolver_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def remove_provider_api_symbols(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    provider_module_id = "ModuleId:acme.display"
    provider = fixture["provider_interfaces"][provider_module_id]
    del provider["symbols"]
    reseal_json_self_hash(provider, "canonical_sha256")
    for case in fixture["cases"]:
        for row in case["dependency_receipt"][
            "required_interfaces"
        ]:
            if row["provider_module_id"] == provider_module_id:
                row["interface_sha256"] = provider[
                    "canonical_sha256"
                ]
        rebind_dependency_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_manifest_from_package_graph(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    shared = fixture["shared_inputs"]
    shared["manifest_bytes_utf8"] += "# relation drift\n"
    shared["manifest_sha256"] = hashlib.sha256(
        shared["manifest_bytes_utf8"].encode("utf-8")
    ).hexdigest()
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_consumer_source_from_graph(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    source_file_id = case["source_file_id"]
    drift_sha256 = "1" * 64
    source_row = next(
        row
        for row in case["package_graph"][
            "source_contributions"
        ]
        if row["source_file_id"] == source_file_id
    )
    source_row["source_bytes_sha256"] = drift_sha256
    projection_row = next(
        row
        for row in case[
            "module_source_contribution_projection"
        ]["source_contributions"]
        if row["source_file_id"] == source_file_id
    )
    projection_row["source_bytes_sha256"] = drift_sha256
    rebind_source_projection(case)
    rebind_package_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_provider_source_from_graph(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    provider_source_file_id = fixture["shared_inputs"][
        "provider_source_file_id"
    ]
    source_row = next(
        row
        for row in case["package_graph"][
            "source_contributions"
        ]
        if row["source_file_id"] == provider_source_file_id
    )
    source_row["source_bytes_sha256"] = "2" * 64
    rebind_package_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_resolver_module_owner(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    module_scope = next(
        row
        for row in case["resolver_graph"]["scopes"]
        if row["kind"] == "ModuleScope"
    )
    module_scope["module_id"] = "ModuleId:acme.display"
    rebind_resolver_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_trace_visibility_proof(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    case["resolver_trace"]["references"][0][
        "visibility_proof_ids"
    ] = ["VisibilityProofId:acme.api.missing"]
    rebind_trace_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_public_reexport_origin(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    closure = fixture["shared_inputs"]["visibility_closure"]
    closure["reexport_edges"][0]["activation_origin_id"] = (
        "ActivationOriginId:acme.api.other-reexport"
    )
    reseal_json_self_hash(closure, "closure_sha256")
    for case in fixture["cases"]:
        case["compilation_receipt"][
            "visibility_closure_sha256"
        ] = closure["closure_sha256"]
        reseal_compilation_receipt(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_initialization_binding_owner(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    plan = fixture["shared_inputs"]["initialization_plan"]
    drift_decl_id = "DeclId:acme.api.unrelated"
    plan["bindings"][0]["binding_decl_id"] = drift_decl_id
    plan["topological_evaluation_order"] = [drift_decl_id]
    reseal_json_self_hash(plan, "plan_sha256")
    for case in fixture["cases"]:
        case["compilation_receipt"][
            "initialization_plan_sha256"
        ] = plan["plan_sha256"]
        reseal_compilation_receipt(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_trace_source_span(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    source_span = case["resolver_trace"]["references"][0][
        "source_span"
    ]
    source_span["start"] = 0
    source_span["end"] = 3
    rebind_trace_chain(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_canonicalization_contract(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    fixture["canonicalization"]["json_algorithm_contract"][
        "terminal_newline"
    ] = True
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def drift_hir_source_contract(root: Path) -> None:
    fixture = read_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE)
    case = fixture["cases"][0]
    hir_preimage = case["hir_semantic_digest_preimage"]
    hir_preimage["private_bodies"][0]["return_int"] = 3
    hir_bytes = json.dumps(
        hir_preimage,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    case["hir_semantic_bytes_utf8"] = hir_bytes.decode("utf-8")
    hir_domain = fixture["canonicalization"][
        "hir_semantic_domain_utf8"
    ].encode("utf-8")
    hir_payload = (
        hir_domain
        + len(hir_bytes).to_bytes(8, "big")
        + hir_bytes
    )
    case["hir_semantic_sha256"] = hashlib.sha256(
        hir_payload
    ).hexdigest()
    implementation = case["implementation_digest"]
    implementation["hir_semantic_sha256"] = case[
        "hir_semantic_sha256"
    ]
    reseal_json_self_hash(
        implementation, "implementation_sha256"
    )
    case["compilation_receipt"]["implementation_sha256"] = (
        implementation["implementation_sha256"]
    )
    reseal_compilation_receipt(case)
    write_json(root, MODULE_ARTIFACT_FIXTURE_RELATIVE, fixture)


def broaden_activation_identity_domain(root: Path) -> None:
    relative = (
        "schemas/language/"
        "module-compilation-dependency-receipt.schema.json"
    )
    schema = read_json(root, relative)
    schema["$defs"]["activatedIdentity"]["pattern"] = (
        r"^(?:ExtensionSetId|TraitWitnessId):[^\s]+$"
    )
    write_json(root, relative, schema)


def drift_receipt_activation_kind(root: Path) -> None:
    relative = (
        "schemas/language/"
        "module-compilation-dependency-receipt.schema.json"
    )
    schema = read_json(root, relative)
    schema["$defs"]["activationBinding"]["properties"][
        "activation_kind"
    ]["const"] = "activate"
    write_json(root, relative, schema)


def drift_resolver_activation_kind(root: Path) -> None:
    relative = "schemas/language/resolver-graph.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["activationEntry"]["properties"][
        "activation_kind"
    ]["const"] = "activate"
    write_json(root, relative, schema)


def omit_local_candidate_origin(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["candidateOriginId"]["pattern"] = (
        schema["$defs"]["candidateOriginId"]["pattern"].replace(
            "HirLocalId|", ""
        )
    )
    write_json(root, relative, schema)


def unbind_trace_status_from_result(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    del schema["$defs"]["referenceTrace"]["oneOf"]
    write_json(root, relative, schema)


def misprofile_r4_interface_fixture(root: Path) -> None:
    relative = "tests/fixtures/imported/module-api-digest-fixtures.json"
    fixture = read_json(root, relative)
    fixture["r4_interface_envelope_fixtures"][0][
        "interface_profile"
    ] = "LEGACY_R51F3"
    write_json(root, relative, fixture)


def add_unauthorized_interface_profile(root: Path) -> None:
    relative = "schemas/language/module-api-digest.schema.json"
    schema = read_json(root, relative)
    schema["properties"]["interface_profile"]["enum"].append(
        "EXPERIMENTAL"
    )
    write_json(root, relative, schema)


def broaden_receipt_import_target_identity(root: Path) -> None:
    relative = (
        "schemas/language/"
        "module-compilation-dependency-receipt.schema.json"
    )
    schema = read_json(root, relative)
    schema["$defs"]["importTargetIdentity"]["pattern"] = (
        r"^(?:HirLocalId|DeclId|ModuleId):[^\s]+$"
    )
    write_json(root, relative, schema)


def broaden_trace_resolved_identity(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["resolvedIdentity"]["pattern"] = (
        r"^(?:HirLocalId|DeclId|ModuleId|ImportBindingId):[^\s]+$"
    )
    write_json(root, relative, schema)


def broaden_deferred_overload_ref(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["analysisHirOverloadSetRef"]["pattern"] = (
        r"^(?:ResolvedOverloadSetRef|DeclId):[^\s]+$"
    )
    write_json(root, relative, schema)


def broaden_witness_identity(root: Path) -> None:
    relative = "schemas/language/resolver-graph.schema.json"
    schema = read_json(root, relative)
    schema["$defs"]["traitWitnessId"]["pattern"] = (
        r"^(?:TraitWitnessId|ExtensionSetId):[^\s]+$"
    )
    write_json(root, relative, schema)


def broaden_first_stage_rejection_reason(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    first_failure_branch = schema["$defs"]["referenceTrace"]["oneOf"][1]
    first_failure_branch["properties"]["result"]["allOf"][1][
        "properties"
    ]["rejection_reason"]["enum"].append("DUPLICATE_DECLARATION")
    write_json(root, relative, schema)


def unbind_success_namespace_from_result(root: Path) -> None:
    relative = "schemas/language/resolver-trace.schema.json"
    schema = read_json(root, relative)
    success_branch = schema["$defs"]["referenceTrace"]["oneOf"][0]
    del success_branch["oneOf"]
    success_branch["properties"]["result"] = {
        "oneOf": [
            {"$ref": "#/$defs/acceptedResult"},
            {"$ref": "#/$defs/deferredOverloadResult"},
        ]
    }
    write_json(root, relative, schema)


def run() -> int:
    mutations: list[
        tuple[str, str, Callable[[Path], None]]
    ] = [
        (
            "missing_diagnostic",
            "R4_NRM_DIAGNOSTIC_SET",
            delete_new_diagnostic,
        ),
        (
            "extra_diagnostic",
            "R4_NRM_DIAGNOSTIC_SET",
            add_new_diagnostic,
        ),
        (
            "product_support_overclaim",
            "R4_NRM_PRODUCT_NOT_RUN",
            claim_product_support,
        ),
        (
            "missing_primary_relation",
            "R4_NRM_PRIMARY_RELATIONS",
            delete_primary_relation,
        ),
        (
            "predicate_precedence_swap",
            "R4_NRM_PRECEDENCE",
            swap_predicate_precedence,
        ),
        (
            "missing_reason_dispatch",
            "R4_NRM_REASON_BINDING",
            delete_reason_dispatch,
        ),
        (
            "dependency_prefix_drift",
            "R4_NRM_PRECEDENCE",
            change_dependency_prefix,
        ),
        (
            "missing_fixture",
            "R4_NRM_FIXTURE_SET",
            delete_fixture,
        ),
        (
            "negative_fixture_misbound",
            "R4_NRM_FIXTURE_BINDING",
            change_negative_fixture_binding,
        ),
        (
            "predicate_fixture_tuple_drift",
            "R4_NRM_FIXTURE_BINDING",
            drift_predicate_fixture_tuple,
        ),
        (
            "retired_collision_primary",
            "R4_NRM_COLLISION_CATALOG",
            retire_member_collision_primary,
        ),
        (
            "collision_alias_drift",
            "R4_NRM_COLLISION_RELATIONS",
            break_stable_collision_alias,
        ),
        (
            "ordinary_call_route_removed",
            "R4_NRM_ORDINARY_CALL_SELECTION_BINDING",
            absorb_callable_overload_cluster,
        ),
        (
            "method_extension_selection_contract_drift",
            "R4_NRM_COLLISION_SELECTION_CLOSED",
            absorb_method_extension_winner,
        ),
        (
            "closed_collision_selected_count_drift",
            "R4_NRM_COLLISION_SELECTION_CLOSED",
            break_closed_collision_selected_count,
        ),
        (
            "common_visibility_replaced_by_package",
            "R4_NRM_VISIBILITY_VOCABULARY",
            replace_common_visibility_with_package,
        ),
        (
            "module_visibility_domain_added",
            "R4_NRM_VISIBILITY_VOCABULARY",
            add_module_visibility_domain,
        ),
        (
            "missing_acceptance_oracle",
            "R4_NRM_ORACLE_CONTRACT",
            delete_acceptance_oracle,
        ),
        (
            "duplicate_acceptance_test_id",
            "R4_NRM_ORACLE_CASE_SET",
            duplicate_acceptance_test_id,
        ),
        (
            "acceptance_scenario_drift",
            "R4_NRM_ORACLE_BINDING",
            change_oracle_scenario_binding,
        ),
        (
            "acceptance_outcome_drift",
            "R4_NRM_ORACLE_BINDING",
            change_oracle_outcome_binding,
        ),
        (
            "acceptance_diagnostic_drift",
            "R4_NRM_ORACLE_BINDING",
            change_oracle_diagnostic_binding,
        ),
        (
            "acceptance_reason_drift",
            "R4_NRM_ORACLE_BINDING",
            change_oracle_reason_binding,
        ),
        (
            "acceptance_suppression_drift",
            "R4_NRM_ORACLE_BINDING",
            change_oracle_suppression_binding,
        ),
        (
            "acceptance_schema_cardinality_drift",
            "R4_NRM_ORACLE_SCHEMA",
            weaken_oracle_schema_cardinality,
        ),
        (
            "per_test_artifact_refs_drift",
            "R4_NRM_ORACLE_ARTIFACT_REFS",
            drift_per_test_artifact_refs,
        ),
        (
            "generic_package_identity_domain",
            "R4_NRM_TYPED_ID_DOMAINS",
            genericize_package_identity,
        ),
        (
            "empty_package_owner_set",
            "R4_NRM_GRAPH_SCHEMA_CLOSURE",
            allow_empty_package_owner_set,
        ),
        (
            "resolver_trace_stage_order_drift",
            "R4_NRM_TRACE_STAGE_SCHEMA",
            drift_first_resolver_trace_stage,
        ),
        (
            "module_initialization_decl_id_refs_drift",
            "R4_NRM_INITIALIZATION_SCHEMA_CLOSURE",
            drift_module_initialization_decl_id_refs,
        ),
        (
            "trace_diagnostic_order_drift",
            "R4_NRM_TRACE_SEAL_DIAGNOSTIC_SCHEMA",
            drift_trace_diagnostic_order,
        ),
        (
            "trace_diagnostic_selection_unbound",
            "R4_NRM_TRACE_SEAL_DIAGNOSTIC_SCHEMA",
            unbind_trace_diagnostic_selection,
        ),
        (
            "trace_zero_seal_counter_drift",
            "R4_NRM_TRACE_SEAL_DIAGNOSTIC_SCHEMA",
            drift_trace_zero_seal_counter,
        ),
        (
            "hir_r4_exact_bridge_row_drift",
            "R4_NRM_HIR_BRIDGE_EXACT_STATIC_BINDING",
            drift_hir_r4_exact_bridge_row,
        ),
        (
            "module_api_r4_envelope_optional",
            "R4_NRM_INTERFACE_ENVELOPE",
            drop_module_api_r4_envelope_requirement,
        ),
        (
            "dependency_receipt_interface_digest_unbound",
            "R4_NRM_INTERFACE_ENVELOPE",
            drop_receipt_interface_digest_binding,
        ),
        (
            "module_api_profile_envelope_not_exclusive",
            "R4_NRM_INTERFACE_PROFILE_EXCLUSIVITY",
            allow_envelope_without_r4_profile,
        ),
        (
            "generic_public_export_identity",
            "R4_NRM_EXPORT_ID_DOMAINS",
            genericize_public_export_identity,
        ),
        (
            "public_interface_provenance_leak",
            "R4_NRM_MODULE_ARTIFACT_HASH_DOMAINS",
            leak_provenance_into_public_interface,
        ),
        (
            "source_projection_extra_row",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            add_source_projection_extra_row,
        ),
        (
            "source_projection_owner_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_source_projection_owner,
        ),
        (
            "implementation_interface_mismatch",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_implementation_interface,
        ),
        (
            "compilation_artifact_binding_mismatch",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_compilation_artifact_binding,
        ),
        (
            "compilation_receipt_self_hash_mismatch",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            break_compilation_receipt_self_hash,
        ),
        (
            "private_change_matrix_false_claim",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            false_private_change_matrix_claim,
        ),
        (
            "relation_lone_surrogate",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            insert_lone_surrogate_escape,
        ),
        (
            "relation_float_value_domain",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            inject_float_canonical_value,
        ),
        (
            "relation_closed_package_shape",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            add_closed_package_graph_field,
        ),
        (
            "relation_resolver_order_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            reverse_resolver_scope_order,
        ),
        (
            "relation_incomplete_provider_api",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            remove_provider_api_symbols,
        ),
        (
            "relation_manifest_graph_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_manifest_from_package_graph,
        ),
        (
            "relation_consumer_source_graph_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_consumer_source_from_graph,
        ),
        (
            "relation_provider_source_graph_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_provider_source_from_graph,
        ),
        (
            "relation_package_resolver_owner_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_resolver_module_owner,
        ),
        (
            "relation_trace_visibility_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_trace_visibility_proof,
        ),
        (
            "relation_public_residue_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_public_reexport_origin,
        ),
        (
            "relation_initialization_owner_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_initialization_binding_owner,
        ),
        (
            "relation_source_span_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_trace_source_span,
        ),
        (
            "relation_canonical_contract_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_canonicalization_contract,
        ),
        (
            "relation_hir_source_drift",
            "R4_NRM_MODULE_ARTIFACT_RELATION_FIXTURE",
            drift_hir_source_contract,
        ),
        (
            "activation_environment_absorbs_witness",
            "R4_NRM_ACTIVATION_DOMAIN_SEPARATION",
            broaden_activation_identity_domain,
        ),
        (
            "receipt_activation_kind_drift",
            "R4_NRM_ACTIVATION_DOMAIN_SEPARATION",
            drift_receipt_activation_kind,
        ),
        (
            "resolver_activation_kind_drift",
            "R4_NRM_ACTIVATION_DOMAIN_SEPARATION",
            drift_resolver_activation_kind,
        ),
        (
            "local_candidate_origin_unrepresentable",
            "R4_NRM_TRACE_CANDIDATE_DOMAINS",
            omit_local_candidate_origin,
        ),
        (
            "trace_status_result_unbound",
            "R4_NRM_TRACE_STATUS_RESULT_SCHEMA",
            unbind_trace_status_from_result,
        ),
        (
            "r4_interface_fixture_misprofiled",
            "R4_NRM_INTERFACE_FIXTURES",
            misprofile_r4_interface_fixture,
        ),
        (
            "unauthorized_interface_profile",
            "R4_NRM_INTERFACE_PROFILE_DOMAIN",
            add_unauthorized_interface_profile,
        ),
        (
            "receipt_import_target_identity_domain_broadened",
            "R4_NRM_RESOLVED_IDENTITY_DOMAINS",
            broaden_receipt_import_target_identity,
        ),
        (
            "trace_resolved_identity_domain_broadened",
            "R4_NRM_RESOLVED_IDENTITY_DOMAINS",
            broaden_trace_resolved_identity,
        ),
        (
            "deferred_overload_ref_domain_broadened",
            "R4_NRM_RESOLVED_IDENTITY_DOMAINS",
            broaden_deferred_overload_ref,
        ),
        (
            "witness_identity_absorbs_activation",
            "R4_NRM_WITNESS_DOMAIN_SEPARATION",
            broaden_witness_identity,
        ),
        (
            "wrong_stage_rejection_reason_admitted",
            "R4_NRM_TRACE_STATUS_RESULT_SCHEMA",
            broaden_first_stage_rejection_reason,
        ),
        (
            "success_namespace_result_unbound",
            "R4_NRM_TRACE_STATUS_RESULT_SCHEMA",
            unbind_success_namespace_from_result,
        ),
    ]

    baseline_failures = [
        code
        for condition, code, _detail in (
            *r4_nrm_contract_results(ROOT),
            *r4_oracle_contract_results(ROOT),
            *r4_nrm_integrated_contract_results(ROOT),
        )
        if not condition
    ]
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(
        prefix="deeplus-r4-nrm-mutations-"
    ) as temporary:
        base = Path(temporary)
        for name, expected_code, mutate in mutations:
            target = base / name
            copy_contract_tree(target)
            mutate(target)
            failed_codes = [
                code
                for condition, code, _detail in (
                    *r4_nrm_contract_results(target),
                    *r4_oracle_contract_results(target),
                    *r4_nrm_integrated_contract_results(target),
                )
                if not condition
            ]
            results.append(
                {
                    "mutation": name,
                    "expected_rejection_code": expected_code,
                    "observed_failure_codes": failed_codes,
                    "rejected": expected_code in failed_codes,
                }
            )

    rejected = sum(bool(row["rejected"]) for row in results)
    passed = not baseline_failures and rejected == len(results)
    receipt = {
        "schema": "deeplus.r4-name-resolution-module-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "baseline_contract": (
            "PASS" if not baseline_failures else "FAIL"
        ),
        "baseline_failure_codes": baseline_failures,
        "mutations": len(results),
        "rejected": rejected,
        "product_execution": "NOT_RUN",
        "cases": results,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run())
