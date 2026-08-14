#!/usr/bin/env python3
"""Validate the R102 feature-local handoff specification for R101's eight included actions."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_REL = Path("spec/contracts/implementation-target-feature-local-acceptance-r102.json")
SCHEMA_REL = Path("schemas/language/implementation-target-feature-local-acceptance-r102.schema.json")
INDEX_REL = Path("tests/fixtures/current/implementation-target-feature-local-acceptance-r102.json")
R101_REL = Path("spec/contracts/implementation-target-feature-p1-disposition-r101.json")
TARGET_ROWS_REL = Path("spec/traceability/implementation-target-profile-r1/rows.json")
GLOBAL_ONLY_REL = "spec/contracts/implementation-target-global-trace-closure-r1.json"
SELF_EVIDENCE_PATHS = {CONTRACT_REL.as_posix(), SCHEMA_REL.as_posix(), INDEX_REL.as_posix()}

EXPECTED_ACTION_IDS = [*(f"TCC-P1-{index:03d}" for index in range(2, 9)), "SFD-P1-009"]
EXPECTED_STAGES = [
    "SOURCE_OR_NON_GRAMMAR_AUTHORITY",
    "AST_FRONTEND",
    "STATIC_SEMANTICS",
    "DYNAMIC_MIR",
    "PRIMARY_DIAGNOSTIC",
    "TOOLING_OBLIGATION",
]
EXPECTED_OUTCOMES = ["POSITIVE", "BOUNDARY", "REJECT"]
EXPECTED_RETAINED = {
    "TCC-P1-002": ["conformance_declaration_surface", "explicit_conformance"],
    "TCC-P1-003": ["trait_witness_coherence_phase_a", "trait_witness_resolution_phase_a"],
    "TCC-P1-004": ["trait_witness_coherence_phase_a", "trait_witness_formal_judgment_core"],
    "TCC-P1-005": ["conformance_evidence_origin_bridge_msp", "named_conformance_selector_msp"],
    "TCC-P1-006": ["trait_source_internal_descriptor_split_law", "trait_witness_resolution_phase_a"],
    "TCC-P1-007": ["trait_witness_formal_judgment_core", "trait_witness_resolution_phase_a"],
    "TCC-P1-008": ["conformance_law_documentation_contract", "trait_witness_visibility_export_law"],
    "SFD-P1-009": ["function_static_activation", "static_runtime_member_boundary_law"],
}
EXPECTED_DEPENDENCIES = {
    "TCC-P1-002": [],
    "TCC-P1-003": ["TCC-P1-002"],
    "TCC-P1-004": ["TCC-P1-002", "TCC-P1-003"],
    "TCC-P1-005": ["TCC-P1-002"],
    "TCC-P1-006": ["TCC-P1-003", "TCC-P1-004", "TCC-P1-005"],
    "TCC-P1-007": ["TCC-P1-002", "TCC-P1-003", "TCC-P1-004", "TCC-P1-005", "TCC-P1-006"],
    "TCC-P1-008": ["TCC-P1-002", "TCC-P1-004", "TCC-P1-006", "TCC-P1-007"],
    "SFD-P1-009": [],
}
EXPECTED_PROFILE_BINDINGS = {
    "TCC-P1-002": [
        "R102-TCC-SOURCE-SURFACE", "R102-TCC-AST", "R102-TCC-STATIC-SURFACE",
        "R102-TCC-DYNAMIC-STATIC-ONLY", "R102-TCC-DIAGNOSTIC-SURFACE", "R102-TCC-TOOLING",
    ],
    "TCC-P1-003": [
        "R102-TCC-SOURCE-COHERENCE", "R102-TCC-AST", "R102-TCC-STATIC-COHERENCE",
        "R102-TCC-DYNAMIC-STATIC-ONLY", "R102-TCC-DIAGNOSTIC-COHERENCE", "R102-TCC-TOOLING",
    ],
    "TCC-P1-004": [
        "R102-TCC-SOURCE-COHERENCE", "R102-TCC-AST", "R102-TCC-STATIC-COHERENCE",
        "R102-TCC-DYNAMIC-STATIC-ONLY", "R102-TCC-DIAGNOSTIC-COHERENCE", "R102-TCC-TOOLING",
    ],
    "TCC-P1-005": [
        "R102-TCC-SOURCE-ROUTES", "R102-TCC-AST", "R102-TCC-STATIC-ROUTES",
        "R102-TCC-DYNAMIC-STATIC-ONLY", "R102-TCC-DIAGNOSTIC-SURFACE", "R102-TCC-TOOLING",
    ],
    "TCC-P1-006": [
        "R102-TCC-SOURCE-IDENTITY", "R102-TCC-AST", "R102-TCC-STATIC-IDENTITY",
        "R102-TCC-DYNAMIC-ZERO-RELOOK", "R102-TCC-DIAGNOSTIC-IDENTITY", "R102-TCC-TOOLING",
    ],
    "TCC-P1-007": [
        "R102-TCC-SOURCE-COHERENCE", "R102-TCC-AST", "R102-TCC-STATIC-COHERENCE",
        "R102-TCC-DYNAMIC-STATIC-ONLY", "R102-TCC-DIAGNOSTIC-COHERENCE", "R102-TCC-TOOLING",
    ],
    "TCC-P1-008": [
        "R102-TCC-SOURCE-IDENTITY", "R102-TCC-AST", "R102-TCC-STATIC-IDENTITY",
        "R102-TCC-DYNAMIC-ZERO-RELOOK", "R102-TCC-DIAGNOSTIC-IDENTITY", "R102-TCC-TOOLING",
    ],
    "SFD-P1-009": [
        "R102-SFD-SOURCE", "R102-SFD-AST", "R102-SFD-STATIC",
        "R102-SFD-DYNAMIC", "R102-SFD-DIAGNOSTIC", "R102-SFD-TOOLING",
    ],
}
EXPECTED_SUMMARY = {
    "exact_action_count": 8,
    "trait_action_count": 7,
    "sfd_action_count": 1,
    "exact_stage_count_per_action": 6,
    "exact_outcome_count_per_action": 3,
    "handoff_specification_closed_count": 8,
    "execution_open_not_run_count": 8,
    "product_lanes": "15_OF_15_NOT_RUN",
}
EXPECTED_GOVERNANCE = {
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "tcc_execution": "OPEN_NOT_RUN",
    "sfd_execution": "OPEN_NOT_RUN",
    "product_lanes": "15_OF_15_NOT_RUN",
    "product_support": "NOT_RUN",
    "closure_scope": "HANDOFF_SPECIFICATION_ONLY_NOT_EXECUTION_OR_PRODUCT",
}
EXPECTED_INDEX_GOVERNANCE = {
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "tcc_execution": "OPEN_NOT_RUN",
    "sfd_execution": "OPEN_NOT_RUN",
    "product_lanes": "15_OF_15_NOT_RUN",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    value = document
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def path_text(path: Path) -> str:
    if path.is_dir():
        return "\n".join(
            child.read_text(encoding="utf-8", errors="replace")
            for child in sorted(path.rglob("*"))
            if child.is_file() and child.suffix.lower() in {".json", ".md", ".dpg", ".ebnf", ".yaml", ".yml"}
        )
    return path.read_text(encoding="utf-8", errors="replace")


def resolve_locator(root: Path, locator: dict[str, Any]) -> tuple[bool, Any]:
    rel = locator.get("path")
    kind = locator.get("locator_kind")
    needle = locator.get("locator")
    if not isinstance(rel, str) or not isinstance(needle, str):
        return False, None
    path = root / rel
    if not path.exists():
        return False, None
    try:
        if kind == "JSON_POINTER":
            if not path.is_file():
                return False, None
            return True, json_pointer(load(path), needle)
        text = path_text(path)
        if kind in {"TEXT_ANCHOR", "REGISTRY_ID"}:
            return needle in text, None
        if kind == "GRAMMAR_RULE":
            found = re.search(rf"(?m)^\s*{re.escape(needle)}\s*::=", text) is not None
            return found, None
        if kind == "DPG_RULE":
            found = re.search(rf"(?m)^\s*{re.escape(needle)}\s*:=", text) is not None
            return found, None
    except (KeyError, IndexError, TypeError, ValueError, OSError, json.JSONDecodeError):
        return False, None
    return False, None


def identity_of(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    for field in ("fixture_id", "case_id", "id"):
        if isinstance(value.get(field), str):
            return value[field]
    return None


def command_validator_path(command: str) -> str | None:
    match = re.search(r"(?:^|\s)(tools/validators/[A-Za-z0-9_.-]+\.py)(?:\s|$)", command)
    return match.group(1) if match else None


def has_cycle(actions: list[dict[str, Any]]) -> bool:
    graph = {row.get("action_id"): row.get("dependencies", []) for row in actions}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, []) if child in graph):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def model_errors(
    root: Path,
    contract: dict[str, Any],
    index: dict[str, Any],
    r101: dict[str, Any],
    target_rows: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "deeplus.implementation-target-feature-local-acceptance/r102":
        errors.append("CONTRACT_IDENTITY")
    if contract.get("revision") != "r102-feature-local-implementation-acceptance-handoff":
        errors.append("CONTRACT_REVISION")
    if contract.get("status") != "LOCAL_DESIGN_STATIC_HANDOFF_SPECIFICATION":
        errors.append("CONTRACT_STATUS")
    controlling = contract.get("controlling_r101", {})
    if controlling != {
        "path": R101_REL.as_posix(),
        "sha256": sha256(root / R101_REL),
        "included_action_count": 8,
    }:
        errors.append("R101_DIGEST_BINDING")
    if contract.get("summary") != EXPECTED_SUMMARY:
        errors.append("SUMMARY_EXACT")
    if contract.get("governance") != EXPECTED_GOVERNANCE:
        errors.append("GOVERNANCE_FENCE")

    r101_included = [
        row for row in r101.get("actions", [])
        if row.get("disposition") == "INCLUDED_IMPLEMENTATION_ACCEPTANCE"
    ]
    if [row.get("id") for row in r101_included] != EXPECTED_ACTION_IDS:
        errors.append("R101_INCLUDED_ACTION_PARITY")
    r101_by_id = {row.get("id"): row for row in r101_included}
    target_ids = {row.get("feature_id") for row in target_rows}

    profiles = contract.get("evidence_profiles", [])
    profile_ids = [row.get("profile_id") for row in profiles if isinstance(row, dict)]
    if len(profile_ids) != len(set(profile_ids)) or any(not value for value in profile_ids):
        errors.append("EVIDENCE_PROFILE_ID_UNIQUE")
    profiles_by_id = {row.get("profile_id"): row for row in profiles if isinstance(row, dict)}
    for profile_id, profile in profiles_by_id.items():
        disposition = profile.get("disposition")
        not_applicable = profile.get("not_applicable")
        locators = profile.get("locators", [])
        if not locators:
            errors.append(f"PROFILE_LOCATORS_NONEMPTY:{profile_id}")
        if disposition == "EXACT_NOT_APPLICABLE":
            if not isinstance(not_applicable, dict) or profile.get("stage") != "DYNAMIC_MIR":
                errors.append(f"PROFILE_EXACT_NA_CONTRACT:{profile_id}")
        elif disposition == "CONCRETE_FEATURE_LOCAL_EVIDENCE":
            if not_applicable is not None:
                errors.append(f"PROFILE_CONCRETE_NA_NULL:{profile_id}")
        else:
            errors.append(f"PROFILE_DISPOSITION:{profile_id}")
        for locator in locators:
            rel = locator.get("path")
            if rel == GLOBAL_ONLY_REL:
                errors.append(f"GLOBAL_ONLY_EVIDENCE_FORBIDDEN:{profile_id}")
            if rel in SELF_EVIDENCE_PATHS:
                errors.append(f"SELF_REFERENCE_FORBIDDEN:{profile_id}")
            resolved, _ = resolve_locator(root, locator)
            if not resolved:
                errors.append(f"STALE_PROFILE_LOCATOR:{profile_id}:{rel}:{locator.get('locator')}")
        if profile.get("stage") == "SOURCE_OR_NON_GRAMMAR_AUTHORITY":
            paths = {row.get("path") for row in locators}
            if "spec/grammar/deeplus.ebnf" in paths and not {
                "spec/grammar/deeplus.dpg",
                "spec/grammar/deeplus.parser-contexts.json",
            } <= paths:
                errors.append(f"EBNF_ONLY_SOURCE_AUTHORITY_FORBIDDEN:{profile_id}")

    actions = contract.get("actions", [])
    action_ids = [row.get("action_id") for row in actions if isinstance(row, dict)]
    if action_ids != EXPECTED_ACTION_IDS or len(set(action_ids)) != 8:
        errors.append("ACTION_EXACT_ORDER_UNIQUE")
    if has_cycle(actions):
        errors.append("ACTION_DEPENDENCY_CYCLE")
    for action in actions:
        action_id = action.get("action_id")
        if action_id not in EXPECTED_RETAINED:
            continue
        retained = action.get("retained_target_feature_ids")
        if retained != EXPECTED_RETAINED[action_id]:
            errors.append(f"ACTION_RETAINED_FEATURE_EXACT:{action_id}")
        if any(feature_id not in target_ids for feature_id in retained or []):
            errors.append(f"ACTION_TARGET_MEMBERSHIP:{action_id}")
        r101_row = r101_by_id.get(action_id, {})
        if retained != r101_row.get("retained_feature_ids"):
            errors.append(f"ACTION_R101_FEATURE_PARITY:{action_id}")
        if action.get("dependencies") != EXPECTED_DEPENDENCIES[action_id]:
            errors.append(f"ACTION_DEPENDENCIES:{action_id}")
        if action.get("dependencies") != r101_row.get("dependencies"):
            errors.append(f"ACTION_R101_DEPENDENCY_PARITY:{action_id}")
        bindings = action.get("stage_bindings", [])
        if [row.get("stage") for row in bindings] != EXPECTED_STAGES:
            errors.append(f"ACTION_STAGE_EXACT:{action_id}")
        bound_profile_ids = [row.get("evidence_profile_id") for row in bindings]
        if bound_profile_ids != EXPECTED_PROFILE_BINDINGS[action_id]:
            errors.append(f"ACTION_PROFILE_BINDING_EXACT:{action_id}")
        for stage, profile_id in zip(EXPECTED_STAGES, bound_profile_ids):
            if profiles_by_id.get(profile_id, {}).get("stage") != stage:
                errors.append(f"ACTION_PROFILE_STAGE:{action_id}:{stage}")
        if action.get("acceptance_profile_id") != f"R102-{action_id}":
            errors.append(f"ACTION_ACCEPTANCE_PROFILE:{action_id}")
        commands = action.get("validator_commands", [])
        if not commands or len(commands) != len(set(commands)):
            errors.append(f"ACTION_VALIDATOR_COMMANDS:{action_id}")
        for command in commands:
            validator_path = command_validator_path(command) if isinstance(command, str) else None
            if validator_path is None or not (root / validator_path).is_file():
                errors.append(f"STALE_VALIDATOR_COMMAND:{action_id}:{command}")
        if action.get("handoff_specification_gate") != "CLOSED_FEATURE_LOCAL_SPECIFICATION":
            errors.append(f"ACTION_HANDOFF_GATE:{action_id}")
        if action.get("execution_receipt_gate") != "OPEN_NOT_RUN":
            errors.append(f"ACTION_EXECUTION_GATE:{action_id}")
        if action.get("product_execution") != "NOT_RUN":
            errors.append(f"ACTION_PRODUCT_EXECUTION:{action_id}")

    if contract.get("acceptance_locator_index") != {
        "path": INDEX_REL.as_posix(),
        "schema": "deeplus.implementation-target-feature-local-acceptance-index/r102",
        "exact_action_count": 8,
    }:
        errors.append("ACCEPTANCE_INDEX_BINDING")
    if index.get("schema") != "deeplus.implementation-target-feature-local-acceptance-index/r102":
        errors.append("INDEX_IDENTITY")
    if index.get("revision") != contract.get("revision") or index.get("contract") != CONTRACT_REL.as_posix():
        errors.append("INDEX_CONTRACT_BINDING")
    if index.get("execution_state") != "OPEN_NOT_RUN" or index.get("product_execution") != "NOT_RUN":
        errors.append("INDEX_EXECUTION_FENCE")
    if index.get("governance") != EXPECTED_INDEX_GOVERNANCE:
        errors.append("INDEX_GOVERNANCE_FENCE")
    oracle_rows = index.get("action_oracles", [])
    if [row.get("action_id") for row in oracle_rows] != EXPECTED_ACTION_IDS:
        errors.append("INDEX_ACTION_EXACT_ORDER")
    for row in oracle_rows:
        action_id = row.get("action_id")
        outcomes = row.get("outcomes", [])
        if [outcome.get("outcome") for outcome in outcomes] != EXPECTED_OUTCOMES:
            errors.append(f"INDEX_OUTCOME_EXACT:{action_id}")
        for outcome in outcomes:
            locators = outcome.get("locators", [])
            if not locators:
                errors.append(f"INDEX_OUTCOME_LOCATOR_NONEMPTY:{action_id}:{outcome.get('outcome')}")
            for locator in locators:
                rel = locator.get("path")
                if rel == GLOBAL_ONLY_REL or rel in SELF_EVIDENCE_PATHS:
                    errors.append(f"INDEX_ORACLE_NOT_FEATURE_LOCAL:{action_id}:{rel}")
                resolved, value = resolve_locator(root, locator)
                if not resolved:
                    errors.append(f"STALE_ORACLE_LOCATOR:{action_id}:{rel}:{locator.get('locator')}")
                elif identity_of(value) != locator.get("expected_identity"):
                    errors.append(f"ORACLE_IDENTITY:{action_id}:{locator.get('expected_identity')}")
    return errors


def mutation_rejections(
    root: Path,
    documents: dict[str, Any],
) -> tuple[int, list[str]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str) -> dict[str, Any]:
        value = copy.deepcopy(documents)
        mutations.append((name, value))
        return value

    value = mutate("MISSING_ACTION")
    value["contract"]["actions"].pop()
    value = mutate("MISSING_STAGE")
    value["contract"]["actions"][0]["stage_bindings"].pop()
    value = mutate("MISSING_OUTCOME")
    value["index"]["action_oracles"][0]["outcomes"].pop()
    value = mutate("GLOBAL_ONLY_EVIDENCE")
    value["contract"]["evidence_profiles"][0]["locators"] = [{
        "path": GLOBAL_ONLY_REL,
        "locator_kind": "JSON_POINTER",
        "locator": "/cells/0",
    }]
    value = mutate("STALE_LOCATOR")
    value["contract"]["evidence_profiles"][0]["locators"][0]["locator"] = "/missing_r102"
    value = mutate("PRODUCT_PASS")
    value["contract"]["actions"][0]["product_execution"] = "PASS"
    value = mutate("EXECUTION_CLOSED")
    value["contract"]["actions"][0]["execution_receipt_gate"] = "CLOSED"
    value = mutate("WRONG_TARGET_FEATURE")
    value["contract"]["actions"][0]["retained_target_feature_ids"][0] = "stale_r102_feature"
    value = mutate("SELF_REFERENCE_ORACLE")
    value["index"]["action_oracles"][0]["outcomes"][0]["locators"][0]["path"] = CONTRACT_REL.as_posix()
    value = mutate("WRONG_ORACLE_IDENTITY")
    value["index"]["action_oracles"][0]["outcomes"][0]["locators"][0]["expected_identity"] = "STALE-R102"
    value = mutate("EBNF_ONLY_SOURCE_AUTHORITY")
    value["contract"]["evidence_profiles"][0]["locators"] = [{
        "path": "spec/grammar/deeplus.ebnf",
        "locator_kind": "GRAMMAR_RULE",
        "locator": "ConformanceDecl",
    }]

    survived: list[str] = []
    for mutation_id, value in mutations:
        if not model_errors(root, value["contract"], value["index"], value["r101"], value["target_rows"]):
            survived.append(mutation_id)
    return len(mutations) - len(survived), survived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    schema = load(root / SCHEMA_REL)
    index = load(root / INDEX_REL)
    r101 = load(root / R101_REL)
    target_rows = load(root / TARGET_ROWS_REL)
    errors: list[str] = []
    schema_validation = "JSONSCHEMA_DRAFT_2020_12"
    try:
        import jsonschema

        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
    except ImportError:
        schema_validation = "STRICT_STRUCTURAL_FALLBACK"
    except Exception as error:
        errors.append(f"JSON_SCHEMA_VALIDATION:{error}")
    errors.extend(model_errors(root, contract, index, r101, target_rows))
    rejected = 0
    survived: list[str] = []
    if args.mutations and not errors:
        rejected, survived = mutation_rejections(
            root,
            {"contract": contract, "index": index, "r101": r101, "target_rows": target_rows},
        )
        if survived:
            errors.append("MUTATION_SURVIVED:" + ",".join(survived))
    receipt = {
        "schema": "deeplus.implementation-target-feature-local-acceptance-validation/r102",
        "result": "PASS" if not errors else "FAIL",
        "exact_action_count": 8,
        "trait_action_count": 7,
        "sfd_action_count": 1,
        "handoff_specification_closed_count": 8,
        "execution_open_not_run_count": 8,
        "product_lanes": "15_OF_15_NOT_RUN",
        "schema_validation": schema_validation,
        "mutation_rejections": rejected,
        "mutation_total": 11 if args.mutations else 0,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
