#!/usr/bin/env python3
"""Validate the owner-bound MemberVisibility omission closure contract."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/member-visibility-omission-v1.json"
CONTRACT_SCHEMA_REL = "schemas/language/member-visibility-omission-v1.schema.json"
DESCRIPTOR_SCHEMA_REL = "schemas/language/member-visibility-resolution-v1.schema.json"
FIXTURE_REL = "tests/fixtures/current/member-visibility-omission-v1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Member_Visibility_Omission_Closure_R1.md"

OWNERS = [
    "MemberFunctionDecl",
    "TypeSideMemberFunctionDecl",
    "ConstructorDecl",
    "StoredParameter",
    "FieldDecl",
    "TypeSideFieldDecl",
    "AccessorDecl",
    "ForwardDecl",
    "TraitMethodDecl",
    "ConformanceMethodDecl",
    "ExtensionSetFunctionDecl",
    "ActorOnDecl",
    "ActorRequestDecl",
    "BitfieldNamedSlot",
    "FlagNamedSlot",
]

EXPECTED_RESOLUTIONS = {
    "MemberFunctionDecl": "INHERIT_ORIGINAL_SLOT_IF_OVERRIDE_ELSE_PRIVATE",
    "TypeSideMemberFunctionDecl": "TRAIT_ASSOCIATED_REQUIREMENT_DOMAIN_IN_CONFORMANCE_ELSE_PRIVATE",
    "ConstructorDecl": "PRIVATE",
    "StoredParameter": "PRIVATE",
    "FieldDecl": "PRIVATE",
    "TypeSideFieldDecl": "PRIVATE",
    "AccessorDecl": "PRIVATE_PER_GET_OR_SET_ACCESSOR",
    "ForwardDecl": "PRIVATE_FOR_EACH_GENERATED_FORWARD_SLOT",
    "TraitMethodDecl": "INHERIT_ORIGINAL_TRAIT_SLOT_IF_OVERRIDE_ELSE_PRIVATE",
    "ConformanceMethodDecl": "INHERIT_EXACT_TRAIT_REQUIREMENT_VISIBILITY",
    "ExtensionSetFunctionDecl": "PRIVATE",
    "ActorOnDecl": "ACTOR_VISIBILITY_OR_ACTOR_PROTOCOL_EFFECTIVE_TRANSPORT_VISIBILITY",
    "ActorRequestDecl": "ACTOR_VISIBILITY_OR_ACTOR_PROTOCOL_EFFECTIVE_TRANSPORT_VISIBILITY",
    "BitfieldNamedSlot": "PRIVATE",
    "FlagNamedSlot": "PRIVATE",
}

DEFAULT_PRIVATE_CONTEXTS = {
    ("MemberFunctionDecl", "NEW_MEMBER"),
    ("TypeSideMemberFunctionDecl", "NOMINAL_TYPE_SIDE"),
    ("TypeSideMemberFunctionDecl", "EXTENSION_SET_TYPE_SIDE"),
    ("ConstructorDecl", "NEW_MEMBER"),
    ("StoredParameter", "NEW_MEMBER"),
    ("FieldDecl", "NEW_MEMBER"),
    ("TypeSideFieldDecl", "NEW_MEMBER"),
    ("AccessorDecl", "NEW_MEMBER"),
    ("ForwardDecl", "NEW_MEMBER"),
    ("TraitMethodDecl", "TRAIT_NEW_MEMBER"),
    ("ExtensionSetFunctionDecl", "NEW_MEMBER"),
    ("BitfieldNamedSlot", "BITFIELD_LAYOUT"),
    ("FlagNamedSlot", "BITFIELD_LAYOUT"),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def reject(diagnostic: str) -> dict[str, Any]:
    return {
        "outcome": "REJECT",
        "resolution_kind": None,
        "effective_domain": None,
        "resolution_anchor_id_or_null": None,
        "diagnostic_or_null": diagnostic,
    }


def admit(kind: str, domain: str, anchor: str | None = None) -> dict[str, Any]:
    return {
        "outcome": "ADMIT",
        "resolution_kind": kind,
        "effective_domain": domain,
        "resolution_anchor_id_or_null": anchor,
        "diagnostic_or_null": None,
    }


def resolve(descriptor: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    """Reference procedure for the exact owner/context omission table."""
    owner = descriptor.get("owner_production")
    context = descriptor.get("parent_context")
    rows = {row.get("owner_production"): row for row in contract.get("owner_rows", [])}
    row = rows.get(owner)
    if row is None or context not in row.get("admitted_parent_contexts", []):
        return reject("MEMBER_VISIBILITY_OMISSION_OWNER_CONTEXT_INVALID")

    if descriptor.get("surface_state") != "OMITTED":
        explicit = descriptor.get("explicit_visibility_or_null")
        if explicit not in {"PRIVATE", "HIERARCHY_PROTECTED", "PUBLIC"}:
            return reject("MEMBER_VISIBILITY_OMISSION_OWNER_CONTEXT_INVALID")
        return admit("EXPLICIT_MEMBER_VISIBILITY", explicit)

    pair = (owner, context)
    if pair in DEFAULT_PRIVATE_CONTEXTS:
        return admit("DEFAULT_PRIVATE", "PRIVATE")

    if pair in {
        ("MemberFunctionDecl", "OVERRIDE_SLOT"),
        ("TraitMethodDecl", "TRAIT_OVERRIDE_SLOT"),
    }:
        anchor = descriptor.get("original_slot_anchor_id_or_null")
        visibility = descriptor.get("original_slot_visibility_or_null")
        if not anchor or visibility not in {"PRIVATE", "HIERARCHY_PROTECTED", "PUBLIC"}:
            return reject("MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING")
        return admit("INHERIT_ORIGINAL_SLOT", visibility, anchor)

    if pair == ("TypeSideMemberFunctionDecl", "CONFORMANCE_ASSOCIATED_FUNCTION"):
        requirement = descriptor.get("requirement_id_or_null")
        visibility = descriptor.get("requirement_visibility_or_null")
        if not requirement or visibility != "TRAIT_ASSOCIATED_REQUIREMENT_DOMAIN":
            return reject("MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING")
        return admit("INHERIT_TRAIT_ASSOCIATED_REQUIREMENT_DOMAIN", visibility, requirement)

    if pair == ("ConformanceMethodDecl", "CONFORMANCE_REQUIREMENT"):
        requirement = descriptor.get("requirement_id_or_null")
        visibility = descriptor.get("requirement_visibility_or_null")
        if not requirement or visibility not in {"PRIVATE", "HIERARCHY_PROTECTED", "PUBLIC"}:
            return reject("MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING")
        return admit("INHERIT_TRAIT_REQUIREMENT", visibility, requirement)

    if owner in {"ActorOnDecl", "ActorRequestDecl"}:
        actor_visibility = descriptor.get("actor_visibility_or_null")
        if actor_visibility not in {"private", "common", "public"}:
            return reject("MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING")
        if context == "ACTOR_STANDALONE_OPERATION":
            return admit(
                "DERIVE_ACTOR_TRANSPORT",
                f"TRANSPORT_{actor_visibility.upper()}",
                "ActorDecl.visibility",
            )
        protocol_visibility = descriptor.get("actor_protocol_visibility_or_null")
        requirement = descriptor.get("requirement_id_or_null")
        if protocol_visibility not in {"private", "common", "public"} or not requirement:
            return reject("MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING")
        rank = {"private": 0, "common": 1, "public": 2}
        effective = min((actor_visibility, protocol_visibility), key=rank.__getitem__)
        return admit(
            "DERIVE_ACTOR_PROTOCOL_TRANSPORT_MEET",
            f"TRANSPORT_{effective.upper()}",
            requirement,
        )

    return reject("MEMBER_VISIBILITY_OMISSION_OWNER_CONTEXT_INVALID")


def validate(
    root: Path,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
    validate_schema: bool = True,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    contract = contract_override if contract_override is not None else load(root / CONTRACT_REL)
    fixture = fixture_override if fixture_override is not None else load(root / FIXTURE_REL)

    if validate_schema:
        try:
            import jsonschema

            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            descriptor_validator = jsonschema.Draft202012Validator(load(root / DESCRIPTOR_SCHEMA_REL))
            for case in fixture.get("cases", []):
                descriptor_validator.validate(case.get("descriptor"))
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"JSON_SCHEMA:{exc}")

    require(contract.get("gap_id") == "IR-VIS-P1-057", "GAP_ID")
    require(contract.get("descriptor_schema") == DESCRIPTOR_SCHEMA_REL, "DESCRIPTOR_SCHEMA_BINDING")
    require(contract.get("predecessor_contract") == "spec/contracts/member-visibility-trace-closure-r1.json", "PREDECESSOR")

    rows = contract.get("owner_rows", [])
    owner_names = [row.get("owner_production") for row in rows]
    require(owner_names == OWNERS, "OWNER_ROWS_EXACT_ORDER_15")
    require(len(set(owner_names)) == 15, "OWNER_ROWS_UNIQUE_15")
    require([row.get("ordinal") for row in rows] == list(range(1, 16)), "OWNER_ORDINALS_EXACT")
    for row in rows:
        owner = row.get("owner_production")
        require(row.get("omitted_resolution") == EXPECTED_RESOLUTIONS.get(owner), f"OWNER_RESOLUTION:{owner}")

    surface = contract.get("surface_contract", {})
    require(surface.get("new_source_surface_count") == 0, "NO_NEW_SURFACE")
    require(surface.get("explicit_spellings") == ["-", "#", "+"], "EXPLICIT_SPELLINGS")
    require(surface.get("ast_preserves_omission") is True and surface.get("omitted_ast_value") is None, "AST_PRESERVES_OMISSION")
    require(surface.get("global_default_count") == 0, "NO_GLOBAL_DEFAULT")
    require(surface.get("unresolved_omission_may_enter_canonical_hir") is False, "NO_UNRESOLVED_HIR")
    require(surface.get("unresolved_omission_may_enter_module_api") is False, "NO_UNRESOLVED_API")

    hir = contract.get("hir_seal", {})
    require(hir.get("omitted_or_null_effective_domain_count") == 0, "HIR_NULL_EFFECTIVE_DOMAIN_ZERO")
    require(hir.get("actor_protocol_transport_rule") == "meet(ActorDecl.visibility, ActorProtocolDecl.visibility)", "ACTOR_PROTOCOL_MEET")
    require(hir.get("actor_standalone_transport_rule") == "ActorDecl.visibility", "ACTOR_STANDALONE_VISIBILITY")
    require(hir.get("runtime_visibility_check_count") == 0, "NO_RUNTIME_VISIBILITY_CHECK")
    require(hir.get("new_mir_operation_kind_count") == 0, "NO_NEW_MIR_OP")
    require(hir.get("backend_reinterpretation_count") == 0, "NO_BACKEND_REINTERPRETATION")

    precedence = contract.get("diagnostic_precedence", [])
    require([item.get("rank") for item in precedence] == list(range(1, 7)), "DIAGNOSTIC_RANKS")
    expected_diagnostics = [
        "CALLABLE_VISIBILITY_KEYWORD_FORBIDDEN",
        "MEMBER_VISIBILITY_OMISSION_OWNER_CONTEXT_INVALID",
        "MEMBER_VISIBILITY_OMISSION_ANCHOR_MISSING",
        "OVERRIDE_VISIBILITY_CANNOT_NARROW",
        "TRAIT_REQUIREMENT_VISIBILITY_MISMATCH",
        "REFERENCE_VISIBILITY_OR_ACTIVATION_VIOLATION",
    ]
    require([item.get("diagnostic") for item in precedence] == expected_diagnostics, "DIAGNOSTIC_PRECEDENCE_EXACT")

    cases = fixture.get("cases", [])
    counts = Counter(case.get("class") for case in cases)
    require(len(cases) == 25 and len({case.get("case_id") for case in cases}) == 25, "FIXTURE_EXACT_UNIQUE_25")
    require((counts["normal"], counts["boundary"], counts["reject"]) == (15, 6, 4), "FIXTURE_CLASS_COUNTS")
    require([case.get("descriptor", {}).get("owner_production") for case in cases[:15]] == OWNERS, "NORMAL_CASE_OWNER_COVERAGE")
    admitted = 0
    for case in cases:
        observed = resolve(case.get("descriptor", {}), contract)
        expected = case.get("expected", {})
        for key in (
            "outcome",
            "resolution_kind",
            "effective_domain",
            "resolution_anchor_id_or_null",
            "diagnostic_or_null",
        ):
            require(observed.get(key) == expected.get(key), f"FIXTURE:{case.get('case_id')}:{key}")
        if observed["outcome"] == "ADMIT":
            admitted += 1
            require(observed["effective_domain"] is not None, f"ADMITTED_DOMAIN:{case.get('case_id')}")
    expected_counts = fixture.get("expected_counts", {})
    require(admitted == expected_counts.get("admitted") == 21, "ADMITTED_COUNT_21")
    require(expected_counts.get("rejected") == 4, "REJECTED_COUNT_4")
    require(expected_counts.get("unresolved_after_admission") == 0, "UNRESOLVED_AFTER_ADMISSION_ZERO")

    diagnostics = {row.get("diagnostic_id"): row for row in all_rows(root, "spec/diagnostics/catalog/chunks")}
    for diagnostic in expected_diagnostics:
        require(diagnostic in diagnostics, f"DIAGNOSTIC_CATALOG:{diagnostic}")
    for diagnostic in expected_diagnostics[1:3]:
        row = diagnostics.get(diagnostic, {})
        require(row.get("primary_source") == CONTRACT_REL, f"DIAGNOSTIC_SOURCE:{diagnostic}")
        require(row.get("product_support") == "NOT_RUN", f"DIAGNOSTIC_NOT_RUN:{diagnostic}")

    predicates = {row.get("predicate_id"): row for row in all_rows(root, "spec/types/predicates/chunks")}
    predicate = predicates.get("MemberVisibilityAdmitted", {})
    require(predicate.get("input_descriptor") == "MemberVisibilityResolutionV1", "PREDICATE_DESCRIPTOR")
    require(predicate.get("input_descriptor_schema") == DESCRIPTOR_SCHEMA_REL, "PREDICATE_DESCRIPTOR_SCHEMA")
    require(predicate.get("predecessor_contract") == CONTRACT_REL, "PREDICATE_CONTRACT")
    require(set(expected_diagnostics[1:3]).issubset(predicate.get("diagnostic_refs", [])), "PREDICATE_DIAGNOSTICS")
    require(predicate.get("product_support") == "NOT_RUN" and predicate.get("execution_receipt") is None, "PREDICATE_NOT_RUN")

    features = {row.get("feature_id"): row for row in all_rows(root, "spec/features/catalog/chunks")}
    for feature_id in (
        "member_visibility_hierarchy_protected",
        "member_visibility_sigil_surface_phase_a",
        "member_visibility_sigils_only",
    ):
        row = features.get(feature_id, {})
        require(CONTRACT_REL in row.get("artifact_trace_refs", []), f"FEATURE_CONTRACT:{feature_id}")
        require(row.get("product_support") == "NOT_RUN", f"FEATURE_NOT_RUN:{feature_id}")

    anchors = {
        "LANGUAGE": ("spec/language.md", "IR-VIS-P1-057"),
        "TYPE_SYSTEM": ("spec/types/type-system.md", "MemberVisibilityOmissionV1"),
        "FRONTEND": ("spec/frontend/frontend-model.json", CONTRACT_REL),
        "MIR": ("spec/mir/semantics.md", "MemberVisibilityOmissionV1"),
        "REFERENCE": ("docs/grammar-reference/03-declarations-bindings-and-names.md", "IR-VIS-P1-057"),
        "TUTORIAL": ("docs/tutorial/part-11-modules-system/11-01-package-module-import-visibility.md", "IR-VIS-P1-057"),
        "DECISION": (DECISION_REL, "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE"),
    }
    for code, (relative, needle) in anchors.items():
        require(needle in (root / relative).read_text(encoding="utf-8"), f"ANCHOR:{code}")

    governance = contract.get("governance", {})
    require(governance.get("semantic_p0") == 0, "SEMANTIC_P0_ZERO")
    require(governance.get("feature_p1") == "22_OPEN_UNCHANGED", "FEATURE_P1_22")
    require(governance.get("product_lanes") == "15_OF_15_NOT_RUN", "PRODUCT_LANES_NOT_RUN")
    require(governance.get("production_implementation") == "NOT_RUN", "IMPLEMENTATION_NOT_RUN")
    require(governance.get("github_publication") == "NOT_PERFORMED", "GITHUB_NOT_PERFORMED")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    fixture = load(root / FIXTURE_REL)
    counts = Counter(case.get("class") for case in fixture.get("cases", []))
    print(json.dumps({
        "schema": "deeplus.member-visibility-omission-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "owner_rows": "15/15",
        "cases": {
            "normal": f"{counts['normal']}/15",
            "boundary": f"{counts['boundary']}/6",
            "reject": f"{counts['reject']}/4",
        },
        "unresolved_after_admission": 0,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "NOT_PERFORMED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
