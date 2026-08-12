#!/usr/bin/env python3
"""Validate the closed EnumBodyCommitmentV1 and MatchFallbackBoundaryV1 design."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/enum-match-boundary-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/enum-match-boundary-v1.schema.json"
DECISION_SCHEMA_REL = "schemas/language/enum-match-boundary-decision-v1.schema.json"
FIXTURE_SCHEMA_REL = "schemas/language/enum-match-boundary-fixtures-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/enum-match-boundary-v1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Enum_Match_Boundary_Closure_R1.md"

DIAGNOSTIC_PRECEDENCE = [
    "ENUM_BODY_REQUIRES_CASE",
    "ENUM_COMMA_MODE_REQUIRES_TWO_CASES",
    "ENUM_CASE_SEPARATOR_MIXED",
    "OTHERWISE_GUARD_FORBIDDEN",
    "OTHERWISE_DUPLICATE_CLAUSE",
    "OTHERWISE_MUST_BE_LAST",
    "OTHERWISE_UNREACHABLE",
    "MATCH_NOT_EXHAUSTIVE",
]
EXPECTED_PREDICATES = {"EnumBodyCommitted", "MatchFallbackAdmitted"}
EXPECTED_FIXTURE_IDS = {
    "PF-EnumBodyCommitted-POS",
    "PF-EnumBodyCommitted-BOUNDARY",
    "PF-EnumBodyCommitted-NEG-EMPTY",
    "PF-EnumBodyCommitted-NEG-COMMA",
    "PF-MatchFallbackAdmitted-POS",
    "PF-MatchFallbackAdmitted-BOUNDARY",
    "PF-MatchFallbackAdmitted-NEG-GUARD",
    "PF-MatchFallbackAdmitted-NEG-ORDER",
}
EXPECTED_RELATIONS = {
    ("EnumBodyCommitted:NO_FIRST_CASE", "EnumBodyCommitted", "ENUM_BODY_REQUIRES_CASE", "primary"),
    ("EnumBodyCommitted:COMMA_WITHOUT_SECOND_CASE", "EnumBodyCommitted", "ENUM_COMMA_MODE_REQUIRES_TWO_CASES", "secondary"),
    ("EnumBodyCommitted:MIXED_SEPARATOR", "EnumBodyCommitted", "ENUM_CASE_SEPARATOR_MIXED", "secondary"),
    ("MatchFallbackAdmitted:GUARDED_OTHERWISE", "MatchFallbackAdmitted", "OTHERWISE_GUARD_FORBIDDEN", "primary"),
    ("MatchFallbackAdmitted:DUPLICATE_OTHERWISE", "MatchFallbackAdmitted", "OTHERWISE_DUPLICATE_CLAUSE", "secondary"),
    ("MatchFallbackAdmitted:NONFINAL_OTHERWISE", "MatchFallbackAdmitted", "OTHERWISE_MUST_BE_LAST", "secondary"),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def expected_fixture_result(source: str) -> tuple[str, str | None, int]:
    if source in {"enum Empty {}", "enum MemberOnly { +def value(self) -> Int }"}:
        return ("REJECT", "ENUM_BODY_REQUIRES_CASE", 0)
    if source == "enum Bad { only, }":
        return ("REJECT", "ENUM_COMMA_MODE_REQUIRES_TWO_CASES", 0)
    if source == "@match x { otherwise if ready => 1 }":
        return ("REJECT", "OTHERWISE_GUARD_FORBIDDEN", 0)
    if source == "@match x { otherwise => 0; otherwise => 1 }":
        return ("REJECT", "OTHERWISE_DUPLICATE_CLAUSE", 0)
    if source == "@match x { otherwise => 0; ::some(v) => v }":
        return ("REJECT", "OTHERWISE_MUST_BE_LAST", 0)
    return ("ADMIT", None, 1)


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

            decision_schema = load(root / DECISION_SCHEMA_REL)
            fixture_schema = load(root / FIXTURE_SCHEMA_REL)
            store = {decision_schema["$id"]: decision_schema}
            resolver = jsonschema.RefResolver.from_schema(fixture_schema, store=store)
            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(fixture_schema, resolver=resolver).validate(fixture)
        except ModuleNotFoundError:
            pass
        except Exception as exc:  # pragma: no cover
            errors.append(f"SCHEMA_VALIDATION:{exc}")

    if contract.get("gap_id") != "IR-PARSE-P1-059":
        errors.append("GAP_ID_DRIFT")
    if contract.get("status") != "CURRENT_STABLE_DESIGN_MACHINE_CONTRACT":
        errors.append("CURRENT_STATUS_DRIFT")
    if contract.get("baseline") != {
        "repository": "howork/Deeplus",
        "branch": "main",
        "commit": "10e64f492f0529610673846139afcf0d95175663",
    }:
        errors.append("BASELINE_IDENTITY_DRIFT")

    enum = contract.get("enum_body", {})
    comma = enum.get("modes", {}).get("COMMA_CASES", {})
    layout = enum.get("modes", {}).get("LAYOUT_CASES_THEN_MEMBERS", {})
    if (
        enum.get("identity") != "EnumBodyCommitmentV1"
        or enum.get("minimum_case_count") != 1
        or enum.get("first_item") != "EnumCase"
        or enum.get("empty_body") != "REJECT_ENUM_BODY_REQUIRES_CASE"
        or enum.get("member_first_body") != "REJECT_ENUM_BODY_REQUIRES_CASE"
        or enum.get("mixed_separator_count") != 0
        or enum.get("empty_enum_profile") != "NOT_CURRENT"
        or enum.get("uninhabited_nominal_inference") is not False
    ):
        errors.append("ENUM_BODY_CORE_DRIFT")
    if comma != {
        "commit_marker": "COMMA_AFTER_FIRST_CASE",
        "minimum_case_count": 2,
        "same_physical_line": True,
        "optional_trailing_comma_count": 1,
        "member_count": 0,
    }:
        errors.append("ENUM_COMMA_MODE_DRIFT")
    if layout != {
        "commit_markers": ["END_AFTER_CASE", "CLOSE_AFTER_SINGLE_CASE"],
        "minimum_case_count": 1,
        "case_member_order": "ALL_CASES_BEFORE_MEMBERS",
        "admitted_member_set": "MemberSeq<enum>",
    }:
        errors.append("ENUM_LAYOUT_MODE_DRIFT")

    fallback = contract.get("match_fallback", {})
    if fallback != {
        "identity": "MatchFallbackBoundaryV1",
        "pattern_arm": "(BoundedBinder | Pattern) [Guard] => MatchArmBody",
        "fallback_arm": "otherwise => MatchArmBody",
        "fallback_guard_field": "ABSENT",
        "maximum_fallback_count": 1,
        "fallback_must_be_final": True,
        "wildcard_fallback_alias_count": 0,
        "guarded_fallback_ast_count": 0,
        "guarded_pattern_arm_subtracts_coverage": False,
        "unguarded_pattern_arm_subtracts_coverage": True,
        "otherwise_covers": "EXACT_NONEMPTY_RESIDUAL",
        "implicit_fallback_count": 0,
    }:
        errors.append("MATCH_FALLBACK_CORE_DRIFT")
    if contract.get("diagnostic_precedence") != DIAGNOSTIC_PRECEDENCE:
        errors.append("DIAGNOSTIC_PRECEDENCE_DRIFT")

    fence = contract.get("frontend_fence", {})
    if (
        fence.get("normalized_enum_ast") != "EnumDecl(cases: NonEmptyVector<EnumCase>, members)"
        or fence.get("normalized_match_ast") != "PatternMatchArm(pattern, optional_guard, body) | OtherwiseMatchArm(body)"
        or fence.get("otherwise_guard_slot_count") != 0
        or any(fence.get(key) != 0 for key in (
            "rejected_ast_count", "rejected_hir_count", "rejected_mir_count", "runtime_commitment_operation_count"
        ))
    ):
        errors.append("FRONTEND_OR_RUNTIME_FENCE_DRIFT")
    if contract.get("validation") != {
        "fixture": FIXTURE_REL,
        "fixture_schema": FIXTURE_SCHEMA_REL,
        "normal_count": 5,
        "boundary_count": 5,
        "reject_count": 6,
        "mutation_count": 9,
    }:
        errors.append("VALIDATION_COUNT_DRIFT")
    if contract.get("governance") != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "new_feature_p1": 0,
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_parser_checker_tooling": "NOT_RUN",
        "github_mutation": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE_OVERCLAIM_OR_DRIFT")

    cases = fixture.get("cases", [])
    if len(cases) != 16:
        errors.append(f"FIXTURE_COUNT:{len(cases)}")
    if [case.get("decision") for case in cases[:10]] != ["ADMIT"] * 10:
        errors.append("NORMAL_OR_BOUNDARY_CLASS_DRIFT")
    if [case.get("decision") for case in cases[10:]] != ["REJECT"] * 6:
        errors.append("REJECT_CLASS_DRIFT")
    if len({case.get("input") for case in cases}) != len(cases):
        errors.append("FIXTURE_INPUT_DUPLICATE")
    for case in cases:
        observed = (case.get("decision"), case.get("diagnostic_or_null"), case.get("ast_residue_count"))
        expected = expected_fixture_result(case.get("input", ""))
        if observed != expected:
            errors.append(f"FIXTURE_ORACLE:{case.get('input')}:{observed}")

    diagnostics = {row.get("diagnostic_id") for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    for diagnostic in DIAGNOSTIC_PRECEDENCE:
        if diagnostic not in diagnostics:
            errors.append(f"DIAGNOSTIC_MISSING:{diagnostic}")
    predicates = {row.get("predicate_id"): row for row in all_rows(root, "spec/types/predicates/chunks")}
    for predicate_id in EXPECTED_PREDICATES:
        predicate = predicates.get(predicate_id, {})
        if predicate.get("input_descriptor_schema") != DECISION_SCHEMA_REL:
            errors.append(f"PREDICATE_DESCRIPTOR_BINDING_MISSING:{predicate_id}")
        if predicate.get("product_support") != "NOT_RUN":
            errors.append(f"PREDICATE_PRODUCT_OVERCLAIM:{predicate_id}")

    relation_rows = all_rows(root, "spec/diagnostics/relations/chunks")
    observed_relations = {
        (row.get("violation_id"), row.get("predicate_id"), row.get("diagnostic_id"), row.get("relation"))
        for row in relation_rows if row.get("predicate_id") in EXPECTED_PREDICATES
    }
    if observed_relations != EXPECTED_RELATIONS:
        errors.append("PREDICATE_DIAGNOSTIC_RELATION_DRIFT")
    fixture_rows = all_rows(root, "tests/conformance/checker-predicates/chunks")
    observed_fixture_ids = {
        row.get("fixture_id") for row in fixture_rows if row.get("predicate_id") in EXPECTED_PREDICATES
    }
    if observed_fixture_ids != EXPECTED_FIXTURE_IDS:
        errors.append("CHECKER_FIXTURE_SET_DRIFT")

    features = {row.get("feature_id"): row for row in all_rows(root, "spec/features/catalog/chunks")}
    feature_expectations = {
        "enum_bare_case_declaration_canonical": ("EnumBodyCommitted", "ENUM_BODY_REQUIRES_CASE"),
        "match_otherwise_default_arm": ("MatchFallbackAdmitted", "OTHERWISE_GUARD_FORBIDDEN"),
        "match_exhaustiveness_phase_a": ("MatchFallbackAdmitted", None),
    }
    for feature_id, (predicate_id, diagnostic_id) in feature_expectations.items():
        feature = features.get(feature_id, {})
        refs = feature.get("normative_trace_refs", {})
        if predicate_id not in refs.get("predicates", []):
            errors.append(f"FEATURE_PREDICATE_TRACE_MISSING:{feature_id}")
        if diagnostic_id is not None and diagnostic_id not in refs.get("diagnostics", []):
            errors.append(f"FEATURE_DIAGNOSTIC_TRACE_MISSING:{feature_id}")
        for artifact in (CONTRACT_REL, FIXTURE_REL, DECISION_SCHEMA_REL):
            if artifact not in feature.get("artifact_trace_refs", []):
                errors.append(f"FEATURE_ARTIFACT_TRACE_MISSING:{feature_id}:{artifact}")

    dpg = (root / "spec/grammar/deeplus.dpg").read_text(encoding="utf-8")
    for rule in (
        "EnumBody    := '{' admit<EnumBodyCommit>(EnumCommaCases | EnumLayout) '}' ;",
        "EnumLayout  := EnumCase [END] (EnumCase [END])* MemberSeq<enum> ;",
        "MatchArm    := PatternMatchArm | OtherwiseMatchArm ;",
        ":= (BoundedBinder | Pattern) [Guard] '=>' MatchArmBody ;",
        ":= ~otherwise '=>' MatchArmBody ;",
    ):
        if rule not in dpg:
            errors.append(f"DPG_RULE_DRIFT:{rule}")
    contexts = load(root / "spec/grammar/deeplus.parser-contexts.json")
    if contexts.get("closed_external_bindings", {}).get("admission_predicates", {}).get("EnumBodyCommit") != "#/commitment_policy/enum_body":
        errors.append("ENUM_COMMIT_REFERENCE_DRIFT")
    if contexts.get("commitment_policy", {}).get("enum_body") != {
        "registry": "EnumBodyCommitmentV1",
        "contract": CONTRACT_REL,
        "minimum_case_count": 1,
        "comma_mode_marker": "COMMA_AFTER_FIRST_CASE",
        "layout_mode_markers": ["END_AFTER_CASE", "CLOSE_AFTER_SINGLE_CASE"],
        "mixed_separator_count": 0,
        "empty_enum_profile": "NOT_CURRENT",
    }:
        errors.append("ENUM_COMMIT_CONTEXT_DRIFT")
    frontend = load(root / "spec/frontend/frontend-model.json")
    commitment = next((row for row in frontend.get("parser_commitments", []) if row.get("id") == "ENUM_BODY_AND_MATCH_FALLBACK_BOUNDARY"), {})
    if (
        commitment.get("contract") != CONTRACT_REL
        or commitment.get("enum_case_vector") != "NonEmptyVector<EnumCase>"
        or commitment.get("otherwise_guard_slot_count") != 0
        or commitment.get("otherwise_maximum_count") != 1
        or commitment.get("otherwise_must_be_final") is not True
        or commitment.get("product_support") != "NOT_RUN"
    ):
        errors.append("FRONTEND_COMMITMENT_DRIFT")

    joined = "\n".join([
        (root / DECISION_REL).read_text(encoding="utf-8"),
        (root / "spec/language.md").read_text(encoding="utf-8"),
        (root / "spec/types/type-system.md").read_text(encoding="utf-8"),
        (root / "spec/mir/semantics.md").read_text(encoding="utf-8"),
        (root / "docs/grammar-reference/07-enums-records-schemas-bitfields-and-units.md").read_text(encoding="utf-8"),
        (root / "docs/grammar-reference/10-patterns-destructuring-and-matching.md").read_text(encoding="utf-8"),
    ])
    for token in ("IR-PARSE-P1-059", "EnumBodyCommitmentV1", "MatchFallbackBoundaryV1", "15/15 NOT_RUN"):
        if token not in joined:
            errors.append(f"NORMATIVE_TEXT_BINDING_MISSING:{token}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    print(json.dumps({
        "schema": "deeplus.enum-match-boundary-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "gap": "IR-PARSE-P1-059",
        "cases": {"normal": 5, "boundary": 5, "reject": 6},
        "semantic_p0": 0,
        "global_feature_p1": "22_OPEN_UNCHANGED",
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "NOT_PERFORMED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
