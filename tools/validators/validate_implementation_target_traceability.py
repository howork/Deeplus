#!/usr/bin/env python3
"""Validate exact target-profile traceability totality without product overclaim."""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
SCHEMA_REL = "schemas/language/implementation-target-traceability-r1.schema.json"
PARSER_AUTHORITY_CONTRACT_REL = "spec/contracts/parser-authority-traceability-r1.json"
PARSER_AUTHORITY_SCHEMA_REL = "schemas/language/parser-authority-traceability-r1.schema.json"
R101_FEATURE_P1_CONTRACT_REL = "spec/contracts/implementation-target-feature-p1-disposition-r101.json"
OVERLAY_SPECS = [
    (
        "spec/traceability/implementation-target-profile-r1/scalar-numeric-fixed-operator-evidence-r1.json",
        "schemas/language/scalar-numeric-fixed-operator-evidence-r1.schema.json",
        40,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json",
        "schemas/language/lexical-trivia-source-root-evidence-r1.schema.json",
        38,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json",
        "schemas/language/numeric-array-shape-inferred-evidence-r1.schema.json",
        10,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json",
        "schemas/language/unified-call-tilde-evidence-r1.schema.json",
        9,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json",
        "schemas/language/member-visibility-evidence-r1.schema.json",
        13,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/pattern-dynamic-lowering-evidence-r1.json",
        "schemas/language/pattern-dynamic-lowering-evidence-r1.schema.json",
        3,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/pattern-match-ownership-split-evidence-r1.json",
        "schemas/language/pattern-match-ownership-split-evidence-r1.schema.json",
        2,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/pattern-clause-exhaustiveness-evidence-r1.json",
        "schemas/language/pattern-clause-exhaustiveness-evidence-r1.schema.json",
        5,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/trait-qualified-associated-static-selection-evidence-r1.json",
        "schemas/language/trait-qualified-associated-static-selection-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/associated-requirement-phase-a-evidence-r1.json",
        "schemas/language/associated-requirement-phase-a-evidence-r1.schema.json",
        4,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/associated-requirement-ast-diagnostic-parity-evidence-r1.json",
        "schemas/language/associated-requirement-ast-diagnostic-parity-evidence-r1.schema.json",
        2,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/responsibility-identity-dynamic-trace-evidence-r1.json",
        "schemas/language/responsibility-identity-dynamic-trace-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/closure-capture-dynamic-trace-evidence-r1.json",
        "schemas/language/closure-capture-dynamic-trace-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/region-lifetime-dynamic-trace-evidence-r1.json",
        "schemas/language/region-lifetime-dynamic-trace-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/managed-reference-dynamic-trace-evidence-r1.json",
        "schemas/language/managed-reference-dynamic-trace-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/static-runtime-member-boundary-evidence-r1.json",
        "schemas/language/static-runtime-member-boundary-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/method-extension-resolution-dynamic-evidence-r1.json",
        "schemas/language/method-extension-resolution-dynamic-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/member-extension-collision-dynamic-evidence-r1.json",
        "schemas/language/member-extension-collision-dynamic-evidence-r1.schema.json",
        1,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/member-extension-collision-conformance-evidence-r1.json",
        "schemas/language/member-extension-collision-conformance-evidence-r1.schema.json",
        2,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/actor-cranelift-projection-dynamic-evidence-r1.json",
        "schemas/language/actor-cranelift-projection-dynamic-evidence-r1.schema.json",
        3,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/global-trace-closure-evidence-r1.json",
        "schemas/language/implementation-target-global-trace-evidence-r1.schema.json",
        1242,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/accessor-property-forwarding-evidence-r100.json",
        "schemas/language/accessor-property-forwarding-evidence-r100.schema.json",
        35,
    ),
]
FEATURE_DIR = "spec/features/catalog/chunks"
STAGES = ["SOURCE_GRAMMAR", "AST_FRONTEND", "STATIC_SEMANTICS", "DYNAMIC_LOWERING", "DIAGNOSTICS", "TOOLING_OBLIGATIONS", "CONFORMANCE_TESTS"]
OUTCOMES = ["POSITIVE", "BOUNDARY", "REJECT"]
BASE_STATUSES = {"STABLE_DESIGN", "STDLIB_PROFILE"}
ADDITIONS = {"callable_responsibility_profile_core", "data_shaping_callshape_model", "nominal_prototype_derivation", "numeric_literal_lexical_contract", "source_role_contract", "typed_labeled_materialization_family"}
NEGATIVE_COMPATIBILITY_ADDITIONS = {
    "numeric_literal_suffix",
    "static_exact_unit_conversion_msp",
}
TARGET_ADDITIONS = ADDITIONS | NEGATIVE_COMPATIBILITY_ADDITIONS
EXCLUDED_CURRENT_FEATURE_REASONS = {
    "affine_unit_profile_msp": {
        "status": "EXPLICITLY_DEFERRED_TARGET_EXCLUDED",
        "action_id": "IR-MEASURE-P1-069",
    },
    "arbitrary_generator_stdlib_profile": {
        "status": "EXPLICITLY_DEFERRED_TARGET_EXCLUDED_OPTIONAL_PROVIDER",
        "action_id": "IR-COLL-P1-070",
    },
    "trait_binding_failable_v1": {
        "status": "EXCLUDED_PENDING_BOUNDARY_CLOSURE",
        "action_id": "R77-A006",
    },
    "enum_declaration_order_ord_preview_design": {
        "status": "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION",
        "action_id": "CE-E-P1-007",
        "action_ids": ["CE-E-P1-007", "CE-E-P1-008"],
    },
    "enum_case_display_mapping_preview_design": {
        "status": "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION",
        "action_id": "CE-E-P1-007",
        "action_ids": ["CE-E-P1-007", "CE-E-P1-008"],
    },
    "enum_exact_variant_subset_alias_preview_design": {
        "status": "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION",
        "action_id": "CE-E-P1-004",
        "action_ids": ["CE-E-P1-004", "CE-E-P1-008"],
    },
}
R101_EXCLUDED_FEATURE_MAPPING = {
    feature_id: sorted(reason["action_ids"])
    for feature_id, reason in EXCLUDED_CURRENT_FEATURE_REASONS.items()
    if reason.get("status") == "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION"
}
R101_ACTION_IDS = [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
DISPOSITIONS = {"BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE", "APPLICABLE_BLOCKED_BY_GAP"}
NA_REASONS = {
    "SOURCE_GRAMMAR": {"NA_SOURCE_INTERNAL_NO_PROGRAMMER_FORM", "NA_SOURCE_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "AST_FRONTEND": {"NA_AST_LEXICAL_TRIVIA_ONLY", "NA_AST_NO_PROGRAMMER_VISIBLE_FORM", "NA_AST_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "STATIC_SEMANTICS": {"NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY", "NA_STATIC_STDLIB_PROVIDER_ONLY", "NA_STATIC_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "DYNAMIC_LOWERING": {"NA_DYNAMIC_ALIAS_NORMALIZES_NO_DISTINCT_RUNTIME_IDENTITY", "NA_DYNAMIC_REJECTED_BEFORE_LOWERING", "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR", "NA_DYNAMIC_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "DIAGNOSTICS": {"NA_DIAGNOSTIC_NO_REJECTION_WARNING_OR_INFO_CONDITION", "NA_DIAGNOSTIC_INTERNAL_VERIFIER_ONLY"},
    "TOOLING_OBLIGATIONS": {"NA_TOOLING_NO_NEW_SOURCE_OR_OBSERVATION_OBLIGATION", "NA_TOOLING_RUNTIME_ONLY_NO_DEVELOPER_TOOLING_CONTRACT"},
    "CONFORMANCE_TESTS": {"NA_TEST_NO_DISTINCT_REJECTION_CLASS"},
}
BOUNDARIES = {"GRAMMAR_AUTHORITY", "FRONTEND_AUTHORITY", "TYPE_CHECKER_AUTHORITY", "MIR_RUNTIME_AUTHORITY", "DIAGNOSTIC_AUTHORITY", "TOOLING_AUTHORITY", "CONFORMANCE_AUTHORITY", "PRELUDE_PROVIDER_AUTHORITY", "PUBLICATION_AUTHORITY"}
SOURCE_AUTHORITY_CLASSES = {
    "DPG_RULE_FAMILY_ID",
    "PARSER_CONTEXT_REGISTRY",
    "PRATT_PARSE_GOAL_CONTRACT",
    "SCANNER_LEXICAL_GOAL_CONTRACT",
}
GRAMMAR_LOCATOR_CLASSES = SOURCE_AUTHORITY_CLASSES | {
    "GRAMMAR_SURFACE_CENSUS_ID"
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest_ids(ids: list[str]) -> str:
    return hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_id(item: dict[str, Any]) -> str:
    material = "\0".join([
        item["class"], item["path"], item["locator_kind"],
        item["locator"], item["stage_role"],
    ])
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def powershell_ordinal_key(value: str) -> str:
    return value.replace("_", "\0")


def safe_rel(path: str) -> bool:
    value = Path(path)
    return bool(path) and not value.is_absolute() and ".." not in value.parts and "*" not in path and "?" not in path


def resolve_json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def collect_strings(value: Any, output: set[str]) -> None:
    if isinstance(value, dict):
        output.update(str(key) for key in value)
        for item in value.values():
            collect_strings(item, output)
    elif isinstance(value, list):
        for item in value:
            collect_strings(item, output)
    elif isinstance(value, str):
        output.add(value)


@functools.lru_cache(maxsize=None)
def registry_strings(path_text: str) -> frozenset[str]:
    path = Path(path_text)
    output: set[str] = set()
    candidates = [path] if path.is_file() else sorted(path.rglob("*.json"))
    for candidate in candidates:
        if candidate.suffix.lower() == ".json":
            try:
                collect_strings(load(candidate), output)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        else:
            try:
                output.add(candidate.read_text(encoding="utf-8"))
            except (OSError, UnicodeError):
                continue
    return frozenset(output)


@functools.lru_cache(maxsize=None)
def cached_json_document(path_text: str) -> Any:
    """Parse a locator target once per validator process.

    R76 adds 1,242 pointers into one immutable contract.  Re-reading and
    reparsing that same document for every pointer has no evidentiary value and
    made the bounded mutation suite quadratic in artifact size.
    """

    return load(Path(path_text))


def evidence_locator_resolves(root: Path, item: dict[str, Any]) -> bool:
    path = root / item.get("path", "")
    kind = item.get("locator_kind")
    locator = item.get("locator", "")
    evidence_class = item.get("class")
    if not path.exists():
        return False
    if kind == "FILE":
        return path.is_file() and locator in {item.get("path"), path.name}
    if kind == "JSON_POINTER":
        if not path.is_file():
            return False
        try:
            resolve_json_pointer(cached_json_document(str(path.resolve())), locator)
            return True
        except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
            return False
    if kind != "REGISTRY_ID" or not locator:
        return False
    if evidence_class == "GRAMMAR_SURFACE_CENSUS_ID":
        if not path.is_file():
            return False
        return bool(
            re.search(
                rf"(?m)^\s*{re.escape(locator)}\s*::=",
                path.read_text(encoding="utf-8"),
            )
        )
    if evidence_class == "DPG_RULE_FAMILY_ID":
        if not path.is_file():
            return False
        return bool(
            re.search(
                rf"(?m)^\s*{re.escape(locator)}(?:<[^>\r\n]+>)?\s*"
                rf"(?::=|\r?\n\s*:=)",
                path.read_text(encoding="utf-8"),
            )
        )
    if locator in registry_strings(str(path.resolve())):
        return True
    if path.is_file() and path.suffix.lower() != ".json":
        try:
            return locator in path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return False
    return False


def validate(root: Path, metadata: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    parser_authority = load(root / PARSER_AUTHORITY_CONTRACT_REL)
    require(
        parser_authority.get("schema")
        == "deeplus.parser-authority-traceability/r1"
        and parser_authority.get("revision")
        == "r78-dpg-implementation-target-traceability-closure-r1",
        "PARSER_AUTHORITY_CONTRACT_IDENTITY",
    )
    require(
        metadata.get("source_grammar_authority")
        == {
            "contract": PARSER_AUTHORITY_CONTRACT_REL,
            "authority_axes": [
                "structural_grammar",
                "parser_context",
                "pratt",
                "scanner",
            ],
            "surface_census_path": "spec/grammar/deeplus.ebnf",
            "surface_census_semantic_authority": False,
            "direct_cell_requires_all_authority_axes": True,
            "ebnf_only_binding_rejected": True,
        },
        "SOURCE_GRAMMAR_AUTHORITY_METADATA",
    )

    overlays = [(rel, load(root / rel), expected) for rel, _, expected in OVERLAY_SPECS]
    overlay_entries: dict[str, dict[str, Any]] = {}
    overlay_bindings: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    overlay_binding_sources: dict[tuple[Any, Any, Any], str] = {}
    overlay_evidence_ids: set[str] = set()
    for rel, overlay, expected in overlays:
        supersession = overlay.get("supersedes_binding_cells")
        predecessor_overlay_path = None
        declared_superseded: set[tuple[Any, Any, Any]] = set()
        if supersession is not None:
            predecessor_overlay_path = supersession.get("predecessor_overlay_path")
            declared_superseded = {
                (item.get("feature_id"), item.get("stage"), item.get("outcome"))
                for item in supersession.get("cells", [])
            }
        observed_superseded: set[tuple[Any, Any, Any]] = set()
        entries = overlay.get("evidence_entries", [])
        bindings = overlay.get("bindings", [])
        require(len(bindings) == expected, f"OVERLAY_BINDING_EXACT:{rel}:{expected}")
        for item in entries:
            key = item.get("evidence_key")
            require(key not in overlay_entries, f"OVERLAY_EVIDENCE_UNIQUE:{rel}:{key}")
            overlay_entries[key] = item
            overlay_evidence_ids.add(evidence_id(item))
        for item in bindings:
            cell = (item.get("feature_id"), item.get("stage"), item.get("outcome"))
            duplicate_allowed = (
                cell in overlay_bindings
                and cell in declared_superseded
                and overlay_binding_sources.get(cell) == predecessor_overlay_path
            )
            require(
                cell not in overlay_bindings or duplicate_allowed,
                f"OVERLAY_BINDING_UNIQUE:{rel}:{cell}",
            )
            if duplicate_allowed:
                observed_superseded.add(cell)
            overlay_bindings[cell] = item
            overlay_binding_sources[cell] = rel
        require(
            observed_superseded == declared_superseded,
            f"OVERLAY_SUPERSESSION_EXACT:{rel}",
        )
    require(len(overlay_bindings) == 1384, "OVERLAY_BINDING_EXACT_TOTAL_1384")

    feature_rows: list[dict[str, Any]] = []
    for path in sorted((root / FEATURE_DIR).glob("part-*.json")):
        feature_rows.extend(load(path))
    by_id = {row["feature_id"]: row for row in feature_rows}
    target = sorted(
        row["feature_id"]
        for row in feature_rows
        if (row.get("status_enum") in BASE_STATUSES or row["feature_id"] in TARGET_ADDITIONS)
        and row["feature_id"] not in EXCLUDED_CURRENT_FEATURE_REASONS
    )
    excluded = sorted(set(by_id) - set(target), key=powershell_ordinal_key)
    ids = [row.get("feature_id") for row in rows]

    require(len(feature_rows) == 723, "CATALOG_COUNT")
    require(
        len(target) == 464
        and digest_ids(target) == "6f7bf3a7f632d452d04d3a59f222f7353568e466f64507ee2418d233a1d50182",
        "TARGET_IDENTITY",
    )
    # The exclusion set is derived from the current catalog and the explicit
    # profile additions above.  Unlike the target set, its historical digest
    # changes whenever a removed spelling moves from a stale Stable row to an
    # explicit negative-compatibility obligation.
    require(
        len(excluded) == 259
        and digest_ids(excluded) == "df88d5ba0733d78a0c3d327236b6e26c94624ea4a6f5c3e2386560e7f44595ae",
        "EXCLUDED_IDENTITY",
    )
    require(metadata.get("target_count") == len(target) and metadata.get("target_feature_id_list_sha256") == digest_ids(target), "METADATA_TARGET_IDENTITY")
    require(metadata.get("excluded_count") == len(excluded) and metadata.get("excluded_feature_id_list_sha256") == digest_ids(excluded), "METADATA_EXCLUDED_IDENTITY")
    require(metadata.get("negative_compatibility_additions") == sorted(NEGATIVE_COMPATIBILITY_ADDITIONS), "NEGATIVE_COMPATIBILITY_ADDITIONS")
    require(metadata.get("negative_compatibility_addition_count") == len(NEGATIVE_COMPATIBILITY_ADDITIONS), "NEGATIVE_COMPATIBILITY_COUNT")
    metadata_exclusions = metadata.get("excluded_current_feature_reasons", {})
    require(set(metadata_exclusions) == set(EXCLUDED_CURRENT_FEATURE_REASONS), "EXCLUSION_KEY_SET")
    for feature_id, expected in EXCLUDED_CURRENT_FEATURE_REASONS.items():
        observed = metadata_exclusions.get(feature_id, {})
        require(feature_id in excluded and feature_id not in target, f"EXCLUSION_TARGET_ABSENCE:{feature_id}")
        require(observed.get("status") == expected["status"], f"EXCLUSION_STATUS:{feature_id}")
        require(observed.get("action_id") == expected["action_id"], f"EXCLUSION_ACTION:{feature_id}")
        if "action_ids" in expected:
            require(
                observed.get("action_ids") == expected["action_ids"],
                f"EXCLUSION_ACTION_SET:{feature_id}",
            )

    r101_projection = metadata.get("governance", {}).get(
        "r101_feature_p1_disposition", {}
    )
    require(
        r101_projection.get("contract_path") == R101_FEATURE_P1_CONTRACT_REL,
        "R101_CONTRACT_PATH",
    )
    r101_path = root / R101_FEATURE_P1_CONTRACT_REL
    require(r101_path.is_file(), "R101_CONTRACT_EXISTS")
    r101_contract = load(r101_path) if r101_path.is_file() else {}
    require(
        r101_projection.get("contract_sha256")
        == (file_sha256(r101_path) if r101_path.is_file() else None),
        "R101_CONTRACT_DIGEST",
    )
    r101_actions = r101_contract.get("actions", [])
    require(isinstance(r101_actions, list), "R101_ACTIONS_ARRAY")
    r101_actions = r101_actions if isinstance(r101_actions, list) else []
    r101_action_ids = [
        row.get("id") for row in r101_actions if isinstance(row, dict)
    ]
    require(
        len(r101_actions) == 22
        and len(r101_action_ids) == 22
        and len(set(r101_action_ids)) == 22
        and sorted(r101_action_ids) == sorted(R101_ACTION_IDS),
        "R101_ACTION_IDENTITY_EXACT_22",
    )
    action_partition_exact = True
    for row in r101_actions:
        if not isinstance(row, dict):
            action_partition_exact = False
            continue
        action_id = str(row.get("id", ""))
        if action_id.startswith("CE-C-"):
            expected_domain = "CLASS"
        elif action_id.startswith("CE-E-"):
            expected_domain = "ENUMERATION"
        elif action_id.startswith("TCC-"):
            expected_domain = "TRAIT_CONFORMANCE"
        else:
            expected_domain = "STATIC_FIRST_DYNAMIC"
        excluded_scope = action_id.startswith("CE-")
        action_partition_exact = action_partition_exact and (
            row.get("domain") == expected_domain
            and row.get("action_status") == "OPEN"
            and row.get("design_handoff_gate")
            == (
                "EXPLICITLY_DEFERRED_OUTSIDE_FIRST_TARGET"
                if excluded_scope
                else "CLOSED_DESIGN_STATIC"
            )
            and row.get("disposition")
            == (
                "EXCLUDED_SUCCESSOR_SCOPE_RETAIN_CLOSED_BASE"
                if excluded_scope
                else "INCLUDED_IMPLEMENTATION_ACCEPTANCE"
            )
        )
    require(action_partition_exact, "R101_ACTION_PARTITION_EXACT")
    design_open = sum(
        str(row.get("design_handoff_gate", "")).startswith("OPEN")
        for row in r101_actions
        if isinstance(row, dict)
    )
    execution_open = sum(
        str(row.get("execution_receipt_gate", "")).startswith("OPEN")
        for row in r101_actions
        if isinstance(row, dict)
    )
    require(design_open == 0, "R101_DESIGN_OPEN_IN_TARGET_ZERO")
    require(execution_open == 22, "R101_EXECUTION_OPEN_EXACT_22")
    require(
        all(
            isinstance(row, dict) and row.get("product_execution") == "NOT_RUN"
            for row in r101_actions
        ),
        "R101_ACTION_PRODUCT_NOT_RUN",
    )
    r101_excluded_mapping: dict[str, list[str]] = {}
    r101_retained: set[str] = set()
    r101_tcc_sfd_retained: set[str] = set()
    for row in r101_actions:
        if not isinstance(row, dict):
            continue
        action_id = row.get("id")
        retained = row.get("retained_feature_ids", [])
        excluded_features = row.get("excluded_target_feature_ids", [])
        require(
            isinstance(retained, list)
            and bool(retained)
            and isinstance(excluded_features, list),
            f"R101_ACTION_FEATURE_ARRAYS:{action_id}",
        )
        if not isinstance(retained, list) or not isinstance(excluded_features, list):
            continue
        r101_retained.update(str(feature_id) for feature_id in retained)
        if str(action_id).startswith("TCC-") or action_id == "SFD-P1-009":
            require(bool(retained), f"R101_TCC_SFD_RETAINED_NONEMPTY:{action_id}")
            r101_tcc_sfd_retained.update(str(feature_id) for feature_id in retained)
        for feature_id in excluded_features:
            r101_excluded_mapping.setdefault(str(feature_id), []).append(str(action_id))
    r101_excluded_mapping = {
        feature_id: sorted(action_ids)
        for feature_id, action_ids in sorted(r101_excluded_mapping.items())
    }
    require(
        r101_excluded_mapping == R101_EXCLUDED_FEATURE_MAPPING,
        "R101_EXCLUDED_FEATURE_MAPPING_EXACT",
    )
    require(not (r101_retained - set(by_id)), "R101_RETAINED_FEATURES_EXIST")
    require(
        not (r101_tcc_sfd_retained - set(target)),
        "R101_TCC_SFD_RETAINED_FEATURES_IN_TARGET",
    )
    require(
        r101_projection.get("exact_action_ids") == R101_ACTION_IDS
        and r101_projection.get("action_count") == 22
        and r101_projection.get("design_open_in_target_count") == design_open
        and r101_projection.get("execution_open_action_count") == execution_open,
        "R101_METADATA_ACTION_COUNTS",
    )
    require(
        r101_projection.get("excluded_target_feature_mapping")
        == r101_excluded_mapping,
        "R101_METADATA_EXCLUDED_MAPPING",
    )
    require(
        r101_projection.get("retained_feature_ids") == sorted(r101_retained)
        and r101_projection.get("retained_feature_id_list_sha256")
        == digest_ids(sorted(r101_retained)),
        "R101_METADATA_RETAINED_BINDING",
    )
    require(
        r101_projection.get("tcc_sfd_retained_feature_ids")
        == sorted(r101_tcc_sfd_retained)
        and r101_projection.get("tcc_sfd_retained_feature_id_list_sha256")
        == digest_ids(sorted(r101_tcc_sfd_retained)),
        "R101_METADATA_TCC_SFD_BINDING",
    )
    # Bounded reinsertion mutant: the old base-status rule would put exactly the
    # excluded Stable/stdlib rows back into the target.  Prove that every such
    # row is caught by the current explicit exclusion fence.
    old_rule_target = {
        row["feature_id"]
        for row in feature_rows
        if row.get("status_enum") in BASE_STATUSES or row["feature_id"] in TARGET_ADDITIONS
    }
    require(
        old_rule_target.intersection(EXCLUDED_CURRENT_FEATURE_REASONS)
        == {
            "affine_unit_profile_msp",
            "arbitrary_generator_stdlib_profile",
            "enum_case_display_mapping_preview_design",
            "enum_declaration_order_ord_preview_design",
            "enum_exact_variant_subset_alias_preview_design",
        },
        "EXCLUSION_REINSERTION_MUTANT_NOT_DISCRIMINATING",
    )
    require(len(rows) == 464, "ROW_COUNT")
    require(ids == target, "ROW_EXACT_SORTED_TARGET_SET")
    require(len(set(ids)) == len(ids) and len({str(value).casefold() for value in ids}) == len(ids), "ROW_UNIQUE")

    evidence_rows = metadata.get("evidence_registry", [])
    evidence = {row.get("evidence_id"): row for row in evidence_rows}
    require(len(evidence) == len(evidence_rows), "EVIDENCE_UNIQUE")
    # R59-R73 are bounded pending-generation overlays. Make their exact E2 entries
    # available to the in-memory projection without rewriting generated rows.
    for item in overlay_entries.values():
        ev_id = evidence_id(item)
        evidence.setdefault(ev_id, {**item, "evidence_id": ev_id, "evidence_level": "E2_STRUCTURED_STATIC"})
    for ev_id, item in evidence.items():
        path = item.get("path", "")
        require(safe_rel(path), f"EVIDENCE_PATH_SAFE:{ev_id}")
        require((root / path).exists(), f"EVIDENCE_PATH_EXISTS:{ev_id}")
        # Parser-authority evidence is current only when its exact locator
        # resolves. Other legacy rows retain their bounded overlay policy.
        if ev_id in overlay_evidence_ids or item.get("class") in GRAMMAR_LOCATOR_CLASSES:
            require(evidence_locator_resolves(root, item), f"EVIDENCE_LOCATOR_RESOLVES:{ev_id}")
        if item.get("class") == "GRAMMAR_SURFACE_CENSUS_ID":
            require(
                item.get("path") == "spec/grammar/deeplus.ebnf"
                and item.get("stage_role")
                == "SOURCE_GRAMMAR:SURFACE_CENSUS_NONAUTHORITY",
                f"SURFACE_CENSUS_NONAUTHORITY:{ev_id}",
            )
        if item.get("class") in SOURCE_AUTHORITY_CLASSES:
            require(
                item.get("path") != "spec/grammar/deeplus.ebnf",
                f"EBNF_CANNOT_BE_PARSER_AUTHORITY:{ev_id}",
            )
        require(item.get("evidence_level") == "E2_STRUCTURED_STATIC", f"EVIDENCE_LEVEL:{ev_id}")

    direct = delegated = na = blocked = 0
    for row in rows:
        feature_id = row.get("feature_id")
        catalog = by_id.get(feature_id, {})
        binding = row.get("catalog_binding", {})
        require(binding.get("status_enum") == catalog.get("status_enum"), f"CATALOG_STATUS:{feature_id}")
        require(binding.get("feature_kind") == catalog.get("feature_kind"), f"CATALOG_KIND:{feature_id}")
        require(binding.get("source_activation") == catalog.get("source_activation"), f"CATALOG_ACTIVATION:{feature_id}")
        require(row.get("product_execution") == "NOT_RUN", f"PRODUCT_EXECUTION:{feature_id}")
        stages = row.get("stages", [])
        require([stage.get("stage") for stage in stages] == STAGES, f"STAGE_ORDER:{feature_id}")
        for stage in stages:
            stage_name = stage.get("stage")
            cells = stage.get("outcomes", [stage])
            if stage_name == "CONFORMANCE_TESTS":
                require([cell.get("outcome") for cell in cells] == OUTCOMES, f"TEST_OUTCOME_ORDER:{feature_id}")
                require(stage.get("product_execution") == "NOT_RUN", f"TEST_PRODUCT:{feature_id}")
            for cell in cells:
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                overlay_binding = overlay_bindings.get((feature_id, stage_name, outcome))
                disposition = cell.get("disposition")
                pending_projection = (
                    overlay_binding is not None
                    and "predecessor_disposition" in overlay_binding
                )
                if overlay_binding is not None:
                    expected_disposition = overlay_binding.get("disposition")
                    if pending_projection:
                        predecessor_disposition = overlay_binding.get(
                            "predecessor_disposition"
                        )
                        require(
                            disposition
                            in {expected_disposition, predecessor_disposition},
                            f"OVERLAY_PREDECESSOR:{feature_id}:{stage_name}:{outcome}",
                        )
                        disposition = expected_disposition
                    else:
                        require(
                            disposition == expected_disposition,
                            f"OVERLAY_DISPOSITION:{feature_id}:{stage_name}:{outcome}",
                        )
                require(disposition in DISPOSITIONS, f"DISPOSITION:{feature_id}:{stage_name}")
                refs = cell.get("evidence_refs", [])
                if pending_projection:
                    refs = sorted(
                        evidence_id(overlay_entries[key])
                        for key in overlay_binding.get("evidence_keys", [])
                    )
                require(all(ref in evidence for ref in refs), f"EVIDENCE_REF:{feature_id}:{stage_name}")
                if disposition == "BOUND_DIRECT":
                    direct += 1
                    require(bool(refs), f"DIRECT_WITHOUT_EVIDENCE:{feature_id}:{stage_name}")
                    require(
                        pending_projection or not cell.get("blocked_gap_ids"),
                        f"DIRECT_BLOCKED:{feature_id}:{stage_name}",
                    )
                    if stage_name == "SOURCE_GRAMMAR":
                        ref_items = [evidence[ref] for ref in refs if ref in evidence]
                        ref_classes = {item.get("class") for item in ref_items}
                        require(
                            SOURCE_AUTHORITY_CLASSES <= ref_classes,
                            f"SOURCE_AUTHORITY_AXES:{feature_id}",
                        )
                        require(
                            not any(
                                item.get("class") == "GRAMMAR_PRODUCTION_ID"
                                or (
                                    item.get("path") == "spec/grammar/deeplus.ebnf"
                                    and item.get("class")
                                    != "GRAMMAR_SURFACE_CENSUS_ID"
                                )
                                for item in ref_items
                            ),
                            f"SOURCE_EBNF_AUTHORITY_FORBIDDEN:{feature_id}",
                        )
                        trace = catalog.get("normative_trace_refs", {})
                        needs_census = bool(
                            trace.get("productions")
                            or trace.get("semantic_reference_productions")
                        )
                        require(
                            not needs_census
                            or "GRAMMAR_SURFACE_CENSUS_ID" in ref_classes,
                            f"SOURCE_CENSUS_LOCATOR_REQUIRED:{feature_id}",
                        )
                elif disposition == "NOT_APPLICABLE":
                    na += 1
                    detail = (
                        overlay_binding.get("not_applicable")
                        if pending_projection
                        else cell.get("not_applicable")
                    ) or {}
                    require(detail.get("reason_code") in NA_REASONS.get(stage_name, set()), f"NA_REASON:{feature_id}:{stage_name}")
                    require(detail.get("authority_boundary") in BOUNDARIES, f"NA_BOUNDARY:{feature_id}:{stage_name}")
                    just = detail.get("justification_evidence_refs", [])
                    if pending_projection:
                        just = [
                            evidence_id(overlay_entries[key])
                            for key in detail.get("justification_evidence_keys", [])
                        ]
                    require(bool(just) and all(ref in evidence for ref in just), f"NA_JUSTIFICATION:{feature_id}:{stage_name}")
                    require(bool(detail.get("rationale")), f"NA_RATIONALE:{feature_id}:{stage_name}")
                elif disposition == "APPLICABLE_BLOCKED_BY_GAP":
                    blocked += 1
                    require(cell.get("blocked_gap_ids") == ["IR-XCUT-P1-054"], f"BLOCKED_GAP:{feature_id}:{stage_name}")
                    require(bool(refs), f"BLOCKED_WITHOUT_CONTEXT:{feature_id}:{stage_name}")
                elif disposition == "BOUND_DELEGATED":
                    delegated += 1
                    delegate = (
                        overlay_binding.get("delegate_feature_id")
                        if pending_projection
                        else cell.get("delegate_feature_id")
                    )
                    require(delegate in set(target), f"DELEGATE_TARGET:{feature_id}:{stage_name}")
                if overlay_binding is not None:
                    expected_refs = sorted(
                        evidence_id(overlay_entries[key])
                        for key in overlay_binding.get("evidence_keys", [])
                    )
                    require(disposition == overlay_binding.get("disposition"), f"OVERLAY_DISPOSITION:{feature_id}:{stage_name}:{outcome}")
                    if disposition == "NOT_APPLICABLE":
                        actual_refs = (
                            sorted(refs)
                            if pending_projection
                            else sorted(
                                (cell.get("not_applicable") or {}).get(
                                    "justification_evidence_refs", []
                                )
                            )
                        )
                    else:
                        actual_refs = sorted(refs)
                    require(actual_refs == expected_refs, f"OVERLAY_EVIDENCE_REFS:{feature_id}:{stage_name}:{outcome}")
                    require(
                        pending_projection or not cell.get("blocked_gap_ids"),
                        f"OVERLAY_STILL_BLOCKED:{feature_id}:{stage_name}:{outcome}",
                    )
                    if disposition == "BOUND_DELEGATED":
                        actual_delegate = (
                            overlay_binding.get("delegate_feature_id")
                            if pending_projection
                            else cell.get("delegate_feature_id")
                        )
                        require(actual_delegate == overlay_binding.get("delegate_feature_id"), f"OVERLAY_DELEGATE:{feature_id}:{stage_name}:{outcome}")

    counts = metadata.get("derived_counts", {})
    require(counts.get("feature_rows") == 464, "DERIVED_FEATURE_ROWS")
    require(counts.get("stage_cells") == 3248, "DERIVED_STAGE_CELLS")
    require(counts.get("test_outcome_cells") == 1392, "DERIVED_TEST_CELLS")
    metadata_counts = (
        counts.get("bound_direct_cells"),
        counts.get("bound_delegated_cells"),
        counts.get("not_applicable_cells"),
        counts.get("applicable_blocked_cells"),
    )
    require(
        metadata_counts
        in {
            (2438, 2, 500, 1281),
            (2450, 3, 502, 1266),
            (2452, 3, 502, 1264),
            (2457, 3, 502, 1259),
            (2458, 3, 502, 1258),
            (2461, 3, 503, 1254),
            (2463, 3, 501, 1254),
            (2464, 3, 501, 1253),
            (2466, 3, 501, 1251),
            (3713, 4, 504, 0),
            (3714, 4, 503, 0),
            (direct, delegated, na, blocked),
        },
        "DERIVED_LEGACY_OR_CURRENT_COUNTS",
    )
    require(counts.get("missing_cells") == 0 and counts.get("conflict_cells") == 0, "DERIVED_NO_MISSING_CONFLICT")
    require(counts.get("product_not_run_rows") == 464, "DERIVED_PRODUCT")
    require(
        (direct, delegated, na, blocked) == (3676, 4, 496, 0),
        "R101_CURRENT_TARGET_REBIND_COUNTS",
    )
    governance = metadata.get("governance", {})
    require(governance.get("gap_id") == "IR-XCUT-P1-054", "GOVERNANCE_GAP")
    require(governance.get("gap_status") == "LOCAL_VERIFIED_CANDIDATE_NOT_INTEGRATED", "GOVERNANCE_STATUS")
    require(governance.get("semantic_p0") == 0 and governance.get("feature_p1") == "22_OPEN_UNCHANGED", "GOVERNANCE_SEMANTIC")
    require(governance.get("product_lanes") == "15_OF_15_NOT_RUN" and governance.get("e4_e5_evidence_count") == 0, "GOVERNANCE_PRODUCT")
    require(governance.get("github_publication") == "NOT_PERFORMED_FOR_DPG_TRACE_REPAIR", "GOVERNANCE_GITHUB")
    return errors


def load_registry(root: Path, metadata_path: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata = load(metadata_path or root / META_REL)
    rows: list[dict[str, Any]] = []
    for chunk in metadata.get("chunks", []):
        rows.extend(load(root / chunk["path"]))
    return metadata, rows


def run_mutations(
    root: Path, metadata: dict[str, Any], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Prove that each R101 binding fence rejects a bounded in-memory mutant."""

    def projection(value: dict[str, Any]) -> dict[str, Any]:
        return value["governance"]["r101_feature_p1_disposition"]

    plans: list[tuple[str, str, Any]] = [
        (
            "R101_CONTRACT_DIGEST_MUTATION",
            "R101_CONTRACT_DIGEST",
            lambda meta, _rows: projection(meta).__setitem__(
                "contract_sha256", "0" * 64
            ),
        ),
        (
            "R101_ACTION_IDENTITY_MUTATION",
            "R101_METADATA_ACTION_COUNTS",
            lambda meta, _rows: projection(meta).__setitem__(
                "exact_action_ids", projection(meta)["exact_action_ids"][:-1]
            ),
        ),
        (
            "R101_DESIGN_OPEN_COUNT_MUTATION",
            "R101_METADATA_ACTION_COUNTS",
            lambda meta, _rows: projection(meta).__setitem__(
                "design_open_in_target_count", 1
            ),
        ),
        (
            "R101_EXECUTION_OPEN_COUNT_MUTATION",
            "R101_METADATA_ACTION_COUNTS",
            lambda meta, _rows: projection(meta).__setitem__(
                "execution_open_action_count", 21
            ),
        ),
        (
            "R101_EXCLUDED_MAPPING_MUTATION",
            "R101_METADATA_EXCLUDED_MAPPING",
            lambda meta, _rows: projection(meta).__setitem__(
                "excluded_target_feature_mapping", {}
            ),
        ),
        (
            "R101_RETAINED_BINDING_MUTATION",
            "R101_METADATA_RETAINED_BINDING",
            lambda meta, _rows: projection(meta).__setitem__(
                "retained_feature_ids",
                projection(meta)["retained_feature_ids"] + ["missing_feature"],
            ),
        ),
        (
            "R101_TCC_SFD_TARGET_BINDING_MUTATION",
            "R101_METADATA_TCC_SFD_BINDING",
            lambda meta, _rows: projection(meta).__setitem__(
                "tcc_sfd_retained_feature_ids", []
            ),
        ),
        (
            "R101_PRODUCT_OVERCLAIM_MUTATION",
            "PRODUCT_EXECUTION:",
            lambda _meta, row_values: row_values[0].__setitem__(
                "product_execution", "PASS"
            ),
        ),
        (
            "R101_EXCLUDED_FEATURE_REINSERTION_MUTATION",
            "ROW_EXACT_SORTED_TARGET_SET",
            lambda _meta, row_values: row_values[0].__setitem__(
                "feature_id", "enum_declaration_order_ord_preview_design"
            ),
        ),
    ]
    results: list[dict[str, Any]] = []
    for mutation_id, expected_gate, mutate in plans:
        mutated_metadata = copy.deepcopy(metadata)
        mutated_rows = copy.deepcopy(rows)
        mutate(mutated_metadata, mutated_rows)
        errors = validate(root, mutated_metadata, mutated_rows)
        rejected = any(error.startswith(expected_gate) for error in errors)
        results.append(
            {
                "mutation_id": mutation_id,
                "expected_gate": expected_gate,
                "result": "REJECTED" if rejected else "NOT_REJECTED",
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    metadata, rows = load_registry(root)
    try:
        import jsonschema
        jsonschema.Draft202012Validator(load(root / SCHEMA_REL)).validate(metadata)
        jsonschema.Draft202012Validator(
            load(root / PARSER_AUTHORITY_SCHEMA_REL)
        ).validate(load(root / PARSER_AUTHORITY_CONTRACT_REL))
        for overlay_rel, overlay_schema_rel, _ in OVERLAY_SPECS:
            jsonschema.Draft202012Validator(load(root / overlay_schema_rel)).validate(
                load(root / overlay_rel)
            )
        schema_error = None
    except ImportError:
        schema_error = None
    except Exception as exc:  # pragma: no cover
        schema_error = f"JSON_SCHEMA:{exc}"
    errors = ([schema_error] if schema_error else []) + validate(root, metadata, rows)
    mutation_results: list[dict[str, Any]] = []
    if args.mutations and not errors:
        mutation_results = run_mutations(root, metadata, rows)
        if any(row["result"] != "REJECTED" for row in mutation_results):
            errors.append("R101_MUTATION_SUITE")
    print(json.dumps({
        "schema": "deeplus.implementation-target-traceability-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "target_rows": len(rows),
        "stage_cells": len(rows) * 7,
        "test_outcome_cells": len(rows) * 3,
        "derived_counts": metadata.get("derived_counts", {}),
        "product_execution": "15_OF_15_NOT_RUN",
        "errors": errors,
        "mutation_count": len(mutation_results),
        "mutations": mutation_results,
        "evidence_honesty": "APPLICABLE_BLOCKED_BY_GAP is trace totality, not implementation readiness or product support.",
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
