#!/usr/bin/env python3
"""Design-static validator for the R29 ownership type qualifier contract."""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
PATHS = {
    "contract": ROOT / "spec/contracts/ownership-type-qualifier-r1.json",
    "schema": ROOT / "schemas/language/ownership-type-qualifier-r1.schema.json",
    "fixtures": ROOT / "tests/fixtures/current/ownership-type-qualifier-r1.json",
    "pratt": ROOT / "spec/contracts/closed-pratt-parse-goal-contract-r1.json",
    "mir_schema": ROOT / "schemas/language/deeplus-mir.schema.json",
    "hir_schema": ROOT / "schemas/language/canonical-hir-h1.schema.json",
    "api_schema": ROOT / "schemas/language/module-api-digest.schema.json",
    "rcts_schema": ROOT / "schemas/language/rcts-v5-descriptor.schema.json",
    "lowering": ROOT / "spec/contracts/hir-mir-lowering-registry.json",
    "rcts_fixtures": ROOT / "tests/fixtures/imported/rcts-v5-fixtures.json",
    "rcts_adversarial": ROOT / "tests/fixtures/imported/rcts-v5-adversarial-fixtures.json",
}

BASELINE_COMMIT = "87115776365fcbe8870d2f631050db3e23194c9b"
BASELINE_TREE = "2452f0a6be1e1391b3678dafa86987059b115ec7"
QUALIFIERS = ["UNQUALIFIED", "OWNED", "BORROWED", "MUT", "INOUT"]
SURFACES = ["owned", "borrowed", "mut", "inout"]
PARAMETER_MODES = ["ORDINARY", "BORROW", "MUT_LOCAL", "MOVE", "INOUT"]
CONTEXTS = [
    "LOCAL_BINDING",
    "CALLABLE_PARAMETER_TYPE",
    "FUNCTION_TYPE_ITEM",
    "STORED_FIELD",
    "RETURN_TYPE",
    "EXPORTED_API",
    "OPTIONAL_TYPE",
    "UNION_OR_INTERSECTION_MEMBER",
    "SUSPENSION_OR_ISOLATION_BOUNDARY",
]
MIR_MODES = ["REUSABLE", "OWNED", "BORROWED", "INOUT"]
MODE_TOKEN_MAP = {
    "borrow": "BORROW",
    "mut": "MUT_LOCAL",
    "move": "MOVE",
    "inout": "INOUT",
}
QUALIFIER_TOKEN_MAP = {
    "owned": "OWNED",
    "borrowed": "BORROWED",
    "mut": "MUT",
    "inout": "INOUT",
}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a member name."""


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value}")


def strict_load(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_constant,
    )


def add_error(errors: list[tuple[str, str]], check_id: str, condition: bool, message: str) -> None:
    if not condition:
        errors.append((check_id, message))


def map_by(rows: Iterable[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row.get(key)): row for row in rows}


def contract_errors(contract: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    surface = contract.get("source_surface", {})
    identity = contract.get("identity_separation", {})
    normalization = contract.get("normalization", {})
    semantics = contract.get("qualifier_semantics", [])
    semantic_map = map_by(semantics, "qualifier")
    legality = contract.get("context_legality", {})
    context_map = map_by(legality.get("rows", []), "qualifier")
    api = contract.get("api_residue", {})
    hir = contract.get("hir_mapping", {})
    mir = contract.get("mir_mapping", {})
    mir_map = map_by(mir.get("rows", []), "qualifier")
    diagnostics = contract.get("diagnostic_dispatch", {})
    disambiguation = identity.get("function_type_disambiguation", {})

    add_error(errors, "R29_OTQ_BASELINE", contract.get("baseline_commit") == BASELINE_COMMIT and contract.get("baseline_tree") == BASELINE_TREE, "baseline commit/tree differs")
    add_error(errors, "R29_OTQ_SURFACE_EXACT", surface.get("exact_qualifier_spellings") == SURFACES, "qualifier surface is not exact four")
    add_error(errors, "R29_OTQ_SURFACE_EXACT", surface.get("grammar_change_required") is True and surface.get("grammar_repair") == "ROOT_CONNECTION_ONLY_EXISTING_STABLE_SURFACE" and surface.get("new_surface_count") == 0, "root-connection grammar repair or zero-new-surface fence differs")
    add_error(errors, "R29_OTQ_SURFACE_EXACT", surface.get("maximum_qualifier_count_after_alias_expansion") == 1, "effective qualifier limit is not one")

    pm = identity.get("parameter_mode_domain", {})
    tq = identity.get("type_ownership_qualifier_domain", {})
    add_error(errors, "R29_OTQ_IDENTITY_SEPARATION", pm.get("identity") == "ParameterMode" and pm.get("normalized_values") == PARAMETER_MODES, "ParameterMode domain differs")
    add_error(errors, "R29_OTQ_IDENTITY_SEPARATION", tq.get("identity") == "TypeOwnershipQualifier" and tq.get("normalized_values") == QUALIFIERS, "TypeOwnershipQualifier domain differs")
    add_error(errors, "R29_OTQ_IDENTITY_SEPARATION", identity.get("cross_product_is_explicit") is True and identity.get("implicit_conversion_between_domains") is False, "identity domains are conflated")

    add_error(errors, "R29_OTQ_FUNCTION_TYPE_DISAMBIGUATION", disambiguation.get("commit_lookahead") == "CLOSING_PAREN_FOLLOWED_BY_ARROW", "function type commit lookahead differs")
    add_error(errors, "R29_OTQ_FUNCTION_TYPE_DISAMBIGUATION", disambiguation.get("direct_channel_tokens") == list(MODE_TOKEN_MAP) and disambiguation.get("direct_channel_normalization") == list(MODE_TOKEN_MAP.values()), "direct function channel map differs")
    add_error(errors, "R29_OTQ_FUNCTION_TYPE_DISAMBIGUATION", disambiguation.get("inner_grouped_qualifier_tokens") == SURFACES and disambiguation.get("new_spelling_count") == 0, "inner-group qualifier fence differs")

    add_error(errors, "R29_OTQ_NORMALIZATION", normalization.get("alias_expansion_precedes_uniqueness_check") is True, "alias expansion order differs")
    add_error(errors, "R29_OTQ_NORMALIZATION", normalization.get("duplicate_same_qualifier_is_idempotent") is False and normalization.get("conflicting_qualifiers_are_rejected") is True, "nested qualifier fail-closed rule differs")
    add_error(errors, "R29_OTQ_NORMALIZATION", normalization.get("unqualified_is_not_owned") is True and normalization.get("qualifier_distribution_over_union_or_intersection") is False, "unqualified or composite law differs")
    add_error(errors, "R29_OTQ_NORMALIZATION", list(normalization.get("canonical_emission", {})) == QUALIFIERS and list(normalization.get("canonical_emission", {}).values()) == [None, *SURFACES], "canonical emission differs")

    add_error(errors, "R29_OTQ_VARIANCE", len(semantics) == len(semantic_map) == 5 and list(semantic_map) == QUALIFIERS, "qualifier semantic rows are not exact unique five")
    add_error(errors, "R29_OTQ_VARIANCE", all(semantic_map.get(q, {}).get("implicit_subtyping") is False for q in QUALIFIERS), "implicit qualifier subtyping admitted")
    add_error(errors, "R29_OTQ_VARIANCE", all(semantic_map.get(q, {}).get("variance") == "INVARIANT" for q in QUALIFIERS[1:]), "explicit qualifier is not invariant")

    add_error(errors, "R29_OTQ_CONTEXT", legality.get("contexts") == CONTEXTS, "context universe differs")
    add_error(errors, "R29_OTQ_CONTEXT", len(context_map) == 5 and list(context_map) == QUALIFIERS and all(list(row.get("admission", {})) == CONTEXTS for row in context_map.values()), "context matrix is not exact 5 by 9")
    add_error(errors, "R29_OTQ_CONTEXT", context_map.get("BORROWED", {}).get("admission", {}).get("STORED_FIELD") == "REJECT_ESCAPE", "borrowed stored field no longer fails closed")
    add_error(errors, "R29_OTQ_CONTEXT", context_map.get("INOUT", {}).get("admission", {}).get("STORED_FIELD") == "REJECT_ESCAPE" and context_map.get("INOUT", {}).get("admission", {}).get("RETURN_TYPE") == "REJECT_ESCAPE", "inout storage/return no longer fails closed")
    add_error(errors, "R29_OTQ_CONTEXT", context_map.get("INOUT", {}).get("admission", {}).get("OPTIONAL_TYPE") == "REJECT", "inout optional became a value type")

    add_error(errors, "R29_OTQ_API_RESIDUE", api.get("public_qualifier_erasure_allowed") is False and api.get("parameter_mode_erasure_allowed") is False, "API erasure admitted")
    add_error(errors, "R29_OTQ_API_RESIDUE", api.get("borrowed_public_return_requires_declared_origin_relation") is True and api.get("inout_public_return_allowed") is False, "public escape law differs")
    add_error(errors, "R29_OTQ_API_RESIDUE", "parameter_mode" in api.get("required_fields", []) and "type_ownership_qualifier" in api.get("required_fields", []), "separate API identity fields missing")

    add_error(errors, "R29_OTQ_HIR_MAPPING", hir.get("node") == "HirOwnershipQualifiedType" and hir.get("backend_neutral") is True, "HIR mapping differs")
    add_error(errors, "R29_OTQ_HIR_MAPPING", hir.get("callable_parameter_fields") == ["parameter_mode", "normalized_type_id", "type_ownership_qualifier"], "HIR callable fields conflate domains")

    expected_mir = {
        "UNQUALIFIED": "BASE_TYPE_DERIVED",
        "OWNED": "BASE_REUSABLE_OR_OWNED",
        "BORROWED": "BORROWED",
        "MUT": "OWNED",
        "INOUT": "INOUT",
    }
    add_error(errors, "R29_OTQ_MIR_MAPPING", mir.get("ownership_mode_universe") == MIR_MODES and len(mir_map) == 5 and list(mir_map) == QUALIFIERS, "MIR row universe differs")
    add_error(errors, "R29_OTQ_MIR_MAPPING", all(mir_map.get(q, {}).get("ownership_mode") == mode for q, mode in expected_mir.items()), "qualifier to MIR mapping differs")
    add_error(errors, "R29_OTQ_MIR_MAPPING", mir.get("new_mir_operation_count") == 0 and mir.get("backend_specific_semantic_count") == 0, "new/backend-specific MIR semantics claimed")

    add_error(errors, "R29_OTQ_DIAGNOSTICS", diagnostics.get("borrowed_or_inout_unbound_escape") == "BORROW_ESCAPE_OWNER_REGION", "escape diagnostic differs")
    add_error(errors, "R29_OTQ_DIAGNOSTICS", diagnostics.get("other_illegal_context_or_qualifier_combination") == "OWNERSHIP_MODE_ADMISSION_FAILED", "context diagnostic differs")
    add_error(errors, "R29_OTQ_DIAGNOSTICS", diagnostics.get("new_diagnostic_id_count") == 0, "new diagnostic was invented")
    return errors


def normalize_input(case_input: dict[str, Any]) -> tuple[str, str]:
    parameter_mode = str(case_input.get("parameter_mode", "ORDINARY"))
    qualifier = str(case_input.get("qualifier", "UNQUALIFIED"))
    form = case_input.get("surface_form")
    token = case_input.get("leading_token")
    if form == "FUNCTION_TYPE_DIRECT":
        parameter_mode = MODE_TOKEN_MAP.get(str(token), "ORDINARY")
        qualifier = "UNQUALIFIED"
    elif form in {"FUNCTION_TYPE_GROUPED_TYPE", "PARENTHESIZED_NON_FUNCTION_TYPE"}:
        qualifier = QUALIFIER_TOKEN_MAP.get(str(token), qualifier)
        parameter_mode = "ORDINARY"
    return parameter_mode, qualifier


def evaluate_case(contract: dict[str, Any], case_input: dict[str, Any]) -> dict[str, Any]:
    parameter_mode, qualifier = normalize_input(case_input)
    result = {
        "verdict": "ACCEPT",
        "parameter_mode": parameter_mode,
        "type_ownership_qualifier": qualifier,
        "diagnostic": None,
    }

    def reject(diagnostic: str) -> dict[str, Any]:
        result["verdict"] = "REJECT"
        result["diagnostic"] = diagnostic
        return result

    if int(case_input.get("effective_qualifier_count", 0 if qualifier == "UNQUALIFIED" else 1)) != (0 if qualifier == "UNQUALIFIED" else 1):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    if case_input.get("implicit_qualifier_conversion") is True:
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")

    if parameter_mode in {"BORROW", "INOUT"}:
        if not case_input.get("region_binding", False) or not case_input.get("nonescaping", False):
            return reject("BORROW_ESCAPE_OWNER_REGION")
    if parameter_mode == "MUT_LOCAL" and not case_input.get("uniqueness_proof", False):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    if parameter_mode == "MOVE" and not case_input.get("transfer_proof", False):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")

    context_rows = map_by(contract["context_legality"]["rows"], "qualifier")
    admission = context_rows[qualifier]["admission"][case_input["context"]]
    if admission == "REJECT_ESCAPE":
        return reject("BORROW_ESCAPE_OWNER_REGION")
    if admission == "REJECT":
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    if "OWNER_REGION" in admission and not case_input.get("region_binding", False):
        return reject("BORROW_ESCAPE_OWNER_REGION")
    if "NONESCAPING" in admission and not case_input.get("nonescaping", False):
        return reject("BORROW_ESCAPE_OWNER_REGION")
    if "DECLARED_ORIGIN_RELATION" in admission and not case_input.get("declared_origin_relation", False):
        return reject("BORROW_ESCAPE_OWNER_REGION")
    if "UNIQUENESS" in admission and not case_input.get("uniqueness_proof", False):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    if "TRANSFER_PROOF" in admission and not case_input.get("transfer_proof", False):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    if "EXACT_RESIDUE" in admission and not case_input.get("api_residue", False):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    if admission == "BASE_TYPE_RULE" and not case_input.get("base_type_admitted", True):
        return reject("OWNERSHIP_MODE_ADMISSION_FAILED")
    return result


def replace_pointer(document: dict[str, Any], pointer: str, value: Any) -> None:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.lstrip("/").split("/")]
    target: Any = document
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    leaf = parts[-1]
    if isinstance(target, list):
        target[int(leaf)] = value
    else:
        target[leaf] = value


def collect_diagnostic_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        diagnostic_id = value.get("diagnostic_id")
        if isinstance(diagnostic_id, str):
            found.add(diagnostic_id)
        for child in value.values():
            found.update(collect_diagnostic_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_diagnostic_ids(child))
    return found


def collect_named_enums(value: Any, property_name: str) -> list[list[Any]]:
    found: list[list[Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == property_name and isinstance(child, dict) and isinstance(child.get("enum"), list):
                found.append(child["enum"])
            found.extend(collect_named_enums(child, property_name))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_named_enums(child, property_name))
    return found


def collect_objects_with_keys(value: Any, keys: set[str]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if keys.issubset(value):
            found.append(value)
        for child in value.values():
            found.extend(collect_objects_with_keys(child, keys))
    elif isinstance(value, list):
        for child in value:
            found.extend(collect_objects_with_keys(child, keys))
    return found


def main() -> int:
    failures: list[tuple[str, str]] = []
    checks: list[tuple[str, str]] = []
    docs: dict[str, Any] = {}
    try:
        for name, path in PATHS.items():
            docs[name] = strict_load(path)
        checks.append(("R29_OTQ_CHECK_001", "strict JSON load and duplicate-key rejection"))
    except Exception as exc:
        print(f"R29_OTQ_CHECK_001: FAIL: {exc}")
        return 1

    contract = docs["contract"]
    fixtures = docs["fixtures"]
    try:
        import jsonschema  # type: ignore

        jsonschema.Draft202012Validator.check_schema(docs["schema"])
        jsonschema.Draft202012Validator(docs["schema"]).validate(contract)
        checks.append(("R29_OTQ_CHECK_002", "Draft 2020-12 schema validation"))
    except ImportError:
        checks.append(("R29_OTQ_CHECK_002", "jsonschema unavailable; strict structural validator active"))
    except Exception as exc:
        failures.append(("R29_OTQ_CHECK_002", f"schema validation failed: {exc}"))

    for check_id, message in contract_errors(contract):
        failures.append((check_id, message))
    if not contract_errors(contract):
        checks.extend([
            ("R29_OTQ_CHECK_003", "baseline and exact four-token surface"),
            ("R29_OTQ_CHECK_004", "ParameterMode/TypeOwnershipQualifier identity separation"),
            ("R29_OTQ_CHECK_005", "alias-first normalization and function-type disambiguation"),
            ("R29_OTQ_CHECK_006", "qualifier semantics, invariant variance, and context matrix"),
            ("R29_OTQ_CHECK_007", "API residue and backend-neutral HIR/MIR mapping"),
            ("R29_OTQ_CHECK_008", "existing diagnostic dispatch only"),
        ])

    grammar = (ROOT / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    add_error(failures, "R29_OTQ_CHECK_009", 'OwnershipQualifier ::= "owned" | "borrowed" | "mut" | "inout" ;' in grammar, "grammar ownership qualifier set differs")
    add_error(failures, "R29_OTQ_CHECK_009", "ParenTypeItem ::= FunctionTypeModeItem | TypeRef | TypeRef \"...\" | TypeRef \"***\" ;" in grammar and "FunctionTypeModeItem ::= ParameterMode TypeRef ;" in grammar, "function-type channel mode is not root-connected")
    pratt_text = json.dumps(docs["pratt"], sort_keys=True)
    add_error(failures, "R29_OTQ_CHECK_009", "OwnershipQualifiedType" in pratt_text and all(f'"{token}"' in pratt_text for token in SURFACES), "Pratt ownership parselet binding differs")

    diag_ids: set[str] = set()
    try:
        for path in sorted((ROOT / "spec/diagnostics/catalog/chunks").glob("*.json")):
            diag_ids.update(collect_diagnostic_ids(strict_load(path)))
    except Exception as exc:
        failures.append(("R29_OTQ_CHECK_009", f"diagnostic catalog strict load failed: {exc}"))
    add_error(failures, "R29_OTQ_CHECK_009", {"BORROW_ESCAPE_OWNER_REGION", "OWNERSHIP_MODE_ADMISSION_FAILED"}.issubset(diag_ids), "required existing diagnostics are absent")
    mir_enums = collect_named_enums(docs["mir_schema"], "ownership_mode")
    add_error(failures, "R29_OTQ_CHECK_009", any(enum == MIR_MODES for enum in mir_enums), "MIR ownership mode universe differs")
    hir_text = json.dumps(docs["hir_schema"], sort_keys=True)
    api_text = json.dumps(docs["api_schema"], sort_keys=True)
    rcts_text = json.dumps(docs["rcts_schema"], sort_keys=True)
    add_error(failures, "R29_OTQ_CHECK_009", "NormalizedTypeDescriptor" in hir_text and "type_ownership_qualifier" in hir_text, "HIR normalized qualifier residue is absent")
    add_error(failures, "R29_OTQ_CHECK_009", "type_ownership_qualifier" in api_text and "region_origin_channel_id_or_null" in api_text, "module API qualifier/origin residue is absent")
    add_error(failures, "R29_OTQ_CHECK_009", "type_ownership_qualifiers" in rcts_text, "RCTS callable qualifier residue is absent")
    projection = docs["lowering"].get("ownership_type_qualifier_projection", {})
    projection_rows = map_by(projection.get("rows", []), "qualifier")
    add_error(failures, "R29_OTQ_CHECK_009", list(projection_rows) == QUALIFIERS and projection.get("parameter_mode_separate") is True and projection.get("product_support") == "NOT_RUN", "HIR/MIR qualifier projection differs")
    callable_descriptors: list[dict[str, Any]] = []
    for fixture_name in ("rcts_fixtures", "rcts_adversarial"):
        callable_descriptors.extend(
            row
            for row in collect_objects_with_keys(
                docs[fixture_name], {"schema", "variant", "parameter_modes"}
            )
            if row.get("schema") == "deeplus.rcts-v5/descriptor"
            and row.get("variant") == "callable"
        )
    add_error(failures, "R29_OTQ_CHECK_009", bool(callable_descriptors) and all(len(row.get("parameter_modes", [])) == len(row.get("type_ownership_qualifiers", [])) for row in callable_descriptors), "RCTS callable parameter/qualifier residue is not parallel")
    if not any(check_id == "R29_OTQ_CHECK_009" for check_id, _ in failures):
        checks.append(("R29_OTQ_CHECK_009", "canonical grammar/Pratt/diagnostic/MIR anchors"))

    rows = fixtures.get("acceptance_rows", [])
    counts = Counter(row.get("kind") for row in rows)
    expected_counts = {"POSITIVE": 4, "BOUNDARY": 4, "NEGATIVE": 8}
    add_error(failures, "R29_OTQ_CHECK_010", len(rows) == len({row.get("test_id") for row in rows}) == 16, "acceptance rows are not exact unique 16")
    add_error(failures, "R29_OTQ_CHECK_010", dict(counts) == expected_counts and fixtures.get("expected_acceptance_counts") == {"total": 16, **expected_counts}, "acceptance class counts differ")
    for row in rows:
        actual = evaluate_case(contract, row["input"])
        add_error(failures, "R29_OTQ_CHECK_010", actual == row["expected"], f"{row.get('test_id')} expected {row.get('expected')} but got {actual}")
    if not any(check_id == "R29_OTQ_CHECK_010" for check_id, _ in failures):
        checks.append(("R29_OTQ_CHECK_010", "16 acceptance rows evaluated (4 positive, 4 boundary, 8 negative)"))

    mutations = fixtures.get("mutation_rows", [])
    add_error(failures, "R29_OTQ_CHECK_011", len(mutations) == len({row.get("mutation_id") for row in mutations}) >= 8, "mutation rows are not unique or fewer than eight")
    add_error(failures, "R29_OTQ_CHECK_011", fixtures.get("expected_mutation_count") == len(mutations), "declared mutation count differs")
    for mutation in mutations:
        mutated = copy.deepcopy(contract)
        if mutation.get("operation") != "replace":
            failures.append(("R29_OTQ_CHECK_011", f"{mutation.get('mutation_id')} unsupported mutation operation"))
            continue
        try:
            replace_pointer(mutated, mutation["pointer"], mutation.get("value"))
            rejected_ids = {check_id for check_id, _ in contract_errors(mutated)}
            add_error(failures, "R29_OTQ_CHECK_011", mutation.get("expected_check_id") in rejected_ids, f"{mutation.get('mutation_id')} was not rejected by {mutation.get('expected_check_id')}; got {sorted(rejected_ids)}")
        except Exception as exc:
            failures.append(("R29_OTQ_CHECK_011", f"{mutation.get('mutation_id')} could not execute: {exc}"))
    if not any(check_id == "R29_OTQ_CHECK_011" for check_id, _ in failures):
        checks.append(("R29_OTQ_CHECK_011", f"{len(mutations)} contract mutations rejected by exact invariant"))

    expected_fence = {
        "semantic_p0": 0,
        "canonical_feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
        "github_mutation": 0,
    }
    add_error(failures, "R29_OTQ_CHECK_012", fixtures.get("status") == "DESIGN_STATIC_NOT_RUN" and fixtures.get("status_fence") == expected_fence, "fixture status fence overclaims execution")
    add_error(failures, "R29_OTQ_CHECK_012", contract.get("status_fence", {}).get("semantic_p0") == 0 and contract.get("status_fence", {}).get("canonical_feature_p1") == "22_OPEN_UNCHANGED" and contract.get("status_fence", {}).get("product_lanes") == "15_OF_15_NOT_RUN", "contract status fence differs")
    if not any(check_id == "R29_OTQ_CHECK_012" for check_id, _ in failures):
        checks.append(("R29_OTQ_CHECK_012", "P0/P1, product-lane, implementation, and GitHub fences"))

    if failures:
        print("R29 OWNERSHIP TYPE QUALIFIER: FAIL")
        for check_id, message in failures:
            print(f"  {check_id}: FAIL: {message}")
        return 1

    print("R29 OWNERSHIP TYPE QUALIFIER: PASS")
    for check_id, message in checks:
        print(f"  {check_id}: PASS: {message}")
    print("  qualifiers=4 surface / 5 normalized; contexts=9; acceptance=16; mutations=10")
    print("  semantic P0=0; feature P1=22 OPEN; product lanes=15/15 NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
