#!/usr/bin/env python3
"""Validate the closed SourceItemCommitmentV1 design contract."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/source-item-commitment-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/source-item-commitment-v1.schema.json"
DECISION_SCHEMA_REL = "schemas/language/source-item-commitment-decision-v1.schema.json"
FIXTURE_SCHEMA_REL = "schemas/language/source-item-commitment-fixtures-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/source-item-commitment-v1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Source_Item_Commitment_Closure_R1.md"

COMMITTED_DIAGNOSTIC = "SOURCE_ITEM_CONTEXTUAL_DECLARATION_INCOMPLETE"
ANNOTATION_DIAGNOSTIC = "ANNOTATION_TARGET_REQUIRED"
ROLE_DIAGNOSTIC = "TOP_LEVEL_STATEMENT_REQUIRES_SCRIPT_ROOT"
EXPECTED_COUNTS = {"normal": 5, "boundary": 4, "reject": 5}
EXPECTED_ROW_OWNERS = {
    "SIC-R01": "Class",
    "SIC-R02": "Actor",
    "SIC-R03": "ActorProtocol",
    "SIC-R04": "Typestate",
    "SIC-R05": "Bitfield",
    "SIC-R06": "ExtensionSet",
    "SIC-R07": "ExtensionPack",
    "SIC-R08": "Capability",
    "SIC-R09": "Schema",
    "SIC-R10": "UnitCatalog",
    "SIC-R11": "ModuleInterface",
    "SIC-R12": "PreviewFFI.Function",
    "SIC-R13": "PreviewFFI.Block",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def reject(owner: str | None, diagnostic: str) -> dict[str, Any]:
    return {"outcome": "REJECT", "owner_or_null": owner, "diagnostic_or_null": diagnostic}


def decide(descriptor: dict[str, Any]) -> dict[str, Any]:
    family_owner = {
        "CONTEXTUAL_CLASS": "Class", "ACTOR": "Actor",
        "ACTOR_PROTOCOL": "ActorProtocol", "TYPESTATE": "Typestate",
        "BITFIELD": "Bitfield", "EXTENSION_SET": "ExtensionSet",
        "EXTENSION_PACK": "ExtensionPack", "CAPABILITY": "Capability",
        "SCHEMA": "Schema", "UNIT_CATALOG": "UnitCatalog",
        "OPAQUE_MODULE": "ModuleInterface",
        "PREVIEW_EXTERN_FUNCTION": "PreviewFFI.Function",
        "PREVIEW_EXTERN_BLOCK": "PreviewFFI.Block",
    }
    if descriptor.get("semantic_lookup_count") != 0:
        return reject(None, COMMITTED_DIAGNOSTIC)
    if descriptor.get("committed_token_count_before_marker") != 0:
        return reject(None, COMMITTED_DIAGNOSTIC)

    marker = descriptor.get("commit_marker_reached")
    family = descriptor.get("declaration_family_or_null")
    owner = family_owner.get(family)
    if marker:
        if owner is None:
            return reject(None, COMMITTED_DIAGNOSTIC)
        if descriptor.get("declaration_parse_succeeds"):
            return {"outcome": "COMMIT_DECLARATION", "owner_or_null": owner, "diagnostic_or_null": None}
        return reject(owner, COMMITTED_DIAGNOSTIC)

    if family is not None:
        return reject(None, COMMITTED_DIAGNOSTIC)
    if descriptor.get("annotation_prefix"):
        return reject(None, ANNOTATION_DIAGNOSTIC)
    if descriptor.get("statement_parse_succeeds"):
        if descriptor.get("source_role") == "script":
            return {"outcome": "ROLLBACK_AND_PARSE_STATEMENT", "owner_or_null": "Statement", "diagnostic_or_null": None}
        return reject("Statement", ROLE_DIAGNOSTIC)
    return reject(None, COMMITTED_DIAGNOSTIC)


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
            store = {
                "https://deeplus-lang.org/schema/r88/source-item-commitment-decision-v1.schema.json": load(root / DECISION_SCHEMA_REL)
            }
            resolver = jsonschema.RefResolver.from_schema(load(root / FIXTURE_SCHEMA_REL), store=store)
            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(load(root / FIXTURE_SCHEMA_REL), resolver=resolver).validate(fixture)
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover
            errors.append(f"SCHEMA_VALIDATION:{exc}")

    if contract.get("audit_gap_binding") != {
        "id": "IR-PARSE-P1-058", "severity": "P1", "feature_p1_created": 0
    }:
        errors.append("AUDIT_GAP_BINDING_DRIFT")
    boundary = contract.get("source_boundary", {})
    if (
        boundary.get("role_selected_before_parse") is not True
        or boundary.get("activation_profile_selected_before_parse") is not True
        or boundary.get("member_item_scope_added") is not False
        or boundary.get("grammar_production_change_count") != 0
    ):
        errors.append("SOURCE_BOUNDARY_SCOPE_DRIFT")

    law = contract.get("commitment_law", {})
    expected_zeroes = ["semantic_lookup_count", "type_lookup_count", "overload_lookup_count", "source_order_winner_count"]
    if any(law.get(key) != 0 for key in expected_zeroes):
        errors.append("SEMANTIC_OR_ORDER_LOOKUP_ADMITTED")
    if (
        law.get("pre_marker_failure") != "ROLLBACK_ZERO_TOKENS"
        or law.get("post_marker_failure") != "COMMITTED_DECLARATION_DIAGNOSTIC_NO_FALLBACK"
        or law.get("declaration_precedence_after_marker") is not True
        or law.get("contextual_name_call_escape") != "PARENTHESIZE_FIRST_ARGUMENT"
        or law.get("annotation_selects_annotated_item_without_statement_fallback") is not True
    ):
        errors.append("COMMITMENT_LAW_DRIFT")

    rows = contract.get("rows", [])
    observed = {row.get("row_id"): row.get("production_owner") for row in rows}
    if observed != EXPECTED_ROW_OWNERS or len(rows) != 13:
        errors.append("CONTEXTUAL_ROW_SET_OR_OWNER_DRIFT")
    for row in rows:
        if row.get("fallback_before_marker") != "ROLLBACK_ZERO_TOKENS" or row.get("fallback_after_marker") != "FORBIDDEN":
            errors.append(f"ROW_FALLBACK_DRIFT:{row.get('row_id')}")
    for row_id in ("SIC-R12", "SIC-R13"):
        row = next((item for item in rows if item.get("row_id") == row_id), {})
        if row.get("profiles") != ["preview"]:
            errors.append(f"PREVIEW_FFI_PROFILE_DRIFT:{row_id}")

    cst = contract.get("cst_ast_tooling", {})
    if (
        cst.get("lossless_cst_node") != "SourceItemCommitmentCst"
        or cst.get("normalized_ast_commitment_node_count") != 0
        or cst.get("formatter_uses_symbol_lookup") is not False
        or cst.get("lsp_recovery_crosses_commit_marker") is not False
        or cst.get("product_execution") != "NOT_RUN"
    ):
        errors.append("CST_AST_TOOLING_DRIFT")
    if contract.get("governance") != {
        "semantic_p0": 0, "global_open_feature_p1": 22,
        "new_feature_p1_count": 0, "product_lanes": "15/15_NOT_RUN",
        "github_mutation": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE_OVERCLAIM_OR_DRIFT")

    cases = fixture.get("cases", [])
    counts = Counter(case.get("class") for case in cases)
    if dict(counts) != EXPECTED_COUNTS:
        errors.append(f"FIXTURE_CLASS_COUNTS:{dict(counts)}")
    if len({case.get("case_id") for case in cases}) != len(cases):
        errors.append("FIXTURE_CASE_ID_DUPLICATE")
    for case in cases:
        result = decide(case.get("descriptor", {}))
        if result != case.get("expected"):
            errors.append(f"FIXTURE_ORACLE:{case.get('case_id')}:{result}")

    diagnostics = {row.get("diagnostic_id") for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    for diagnostic in (COMMITTED_DIAGNOSTIC, ANNOTATION_DIAGNOSTIC, ROLE_DIAGNOSTIC):
        if diagnostic not in diagnostics:
            errors.append(f"DIAGNOSTIC_MISSING:{diagnostic}")
    predicates = {row.get("predicate_id"): row for row in all_rows(root, "spec/types/predicates/chunks")}
    predicate = predicates.get("SourceItemOwnerCommitted", {})
    if predicate.get("input_descriptor_schema") != DECISION_SCHEMA_REL:
        errors.append("PREDICATE_DESCRIPTOR_BINDING_MISSING")
    if set(predicate.get("diagnostic_refs", [])) != {COMMITTED_DIAGNOSTIC, ANNOTATION_DIAGNOSTIC, ROLE_DIAGNOSTIC}:
        errors.append("PREDICATE_DIAGNOSTIC_BINDING_DRIFT")

    features = {row.get("feature_id"): row for row in all_rows(root, "spec/features/catalog/chunks")}
    feature = features.get("source_role_contract", {})
    refs = feature.get("normative_trace_refs", {})
    if "SourceItemOwnerCommitted" not in refs.get("predicates", []):
        errors.append("FEATURE_PREDICATE_TRACE_MISSING")
    if COMMITTED_DIAGNOSTIC not in refs.get("diagnostics", []):
        errors.append("FEATURE_DIAGNOSTIC_TRACE_MISSING")
    for artifact in (CONTRACT_REL, FIXTURE_REL, DECISION_SCHEMA_REL):
        if artifact not in feature.get("artifact_trace_refs", []):
            errors.append(f"FEATURE_ARTIFACT_TRACE_MISSING:{artifact}")

    contexts = load(root / "spec/grammar/deeplus.parser-contexts.json")
    source_commitment = contexts.get("commitment_policy", {}).get("source_item")
    if source_commitment != {
        "registry": "SourceItemCommitmentV1",
        "contract": CONTRACT_REL,
        "row_count": 13,
        "pre_marker_failure": "ROLLBACK_ZERO_TOKENS",
        "post_marker_failure": "COMMITTED_DECLARATION_DIAGNOSTIC_NO_FALLBACK",
        "semantic_lookup_count": 0,
    }:
        errors.append("PARSER_CONTEXT_BINDING_DRIFT")

    frontend = load(root / "spec/frontend/frontend-model.json")
    commitments = {row.get("id"): row for row in frontend.get("parser_commitments", [])}
    source_frontend = commitments.get("SOURCE_ITEM_CONTEXTUAL_DECLARATION", {})
    if source_frontend.get("registry") != "SourceItemCommitmentV1" or source_frontend.get("row_count") != 13:
        errors.append("FRONTEND_COMMITMENT_BINDING_DRIFT")
    source_roles = load(root / "spec/contracts/source-roles.json")
    if source_roles.get("source_item_commitment", {}).get("contract") != CONTRACT_REL:
        errors.append("SOURCE_ROLE_CONTRACT_BINDING_MISSING")

    joined = "\n".join([
        (root / DECISION_REL).read_text(encoding="utf-8"),
        (root / "spec/language.md").read_text(encoding="utf-8"),
        (root / "docs/grammar-reference/16-contextual-syntax-and-production-guide.md").read_text(encoding="utf-8"),
    ])
    for token in ("SourceItemCommitmentV1", "IR-PARSE-P1-058", "15/15 NOT_RUN"):
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
        "schema": "deeplus.source-item-commitment-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "gap": "IR-PARSE-P1-058",
        "rows": 13,
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
