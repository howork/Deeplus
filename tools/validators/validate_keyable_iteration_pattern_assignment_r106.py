#!/usr/bin/env python3
"""Validate the bounded R106 Keyable, iteration and assignment handoff."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("spec/contracts/keyable-iteration-pattern-assignment-r106.json")
CONTRACT_SCHEMA = Path("schemas/language/keyable-iteration-pattern-assignment-r106.schema.json")
FIXTURE = Path("tests/fixtures/current/keyable-iteration-pattern-assignment-r106.json")
FIXTURE_SCHEMA = Path("schemas/language/keyable-iteration-pattern-assignment-fixtures-r106.schema.json")
PATTERN_CONTRACT = Path("spec/contracts/pattern-sequence-multivalue-r1.json")
PREDICATE_DIR = Path("spec/types/predicates/chunks")
FEATURE_DIR = Path("spec/features/catalog/chunks")
DIAGNOSTIC_DIR = Path("spec/diagnostics/catalog/chunks")

ALGORITHMS = ["KeyableSelectionV1", "ForIteratorPlanV1", "LocalPatternAssignmentV1"]
PREDICATE_IDS = ["KeyableAdmissible", "ForSourceIterableAdmitted", "LocalGroupAssignmentAdmitted"]
FEATURE_IDS = ["keyable_key_admissibility_v2", "iterator_protocol_core", "local_group_tuple_assignment"]
DIAGNOSTIC_IDS = {
    "TYPE_KEY_REQUIRES_KEYABLE",
    "KEYABLE_REQUIRES_PLAIN_STABLE_HASH",
    "FOR_SOURCE_NOT_ITERABLE",
    "ITERATOR_CLEANUP_EFFECT_NOT_ACCOUNTED",
    "REFUTABLE_PATTERN_IN_IRREFUTABLE_CONTEXT",
    "FOR_LET_FILTER_GUARD_NOT_BOOL",
    "PATTERN_ASSIGNMENT_REQUIRES_EXISTING_VAR",
    "PATTERN_ASSIGNMENT_REFUTABLE",
    "PARALLEL_ASSIGNMENT_ARITY_MISMATCH",
    "PATTERN_ASSIGNMENT_TARGET_OVERLAP",
    "PATTERN_ASSIGNMENT_SHARED_TARGET",
    "PATTERN_ASSIGNMENT_COMMIT_MAY_FAIL",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog(root: Path, relative: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / relative).glob("part-*.json")):
        for row in load(path):
            identity = row.get(key)
            if identity:
                rows[identity] = row
    return rows


def schema_errors(instance: Any, schema: Any, label: str) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []
    try:
        jsonschema.Draft202012Validator(schema).validate(instance)
    except jsonschema.ValidationError:
        return [f"SCHEMA:{label}"]
    return []


def model_errors(root: Path, docs: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = docs["contract"]
    fixture = docs["fixture"]
    pattern = docs["pattern"]
    predicates = docs["predicates"]
    features = docs["features"]
    diagnostics = docs["diagnostics"]

    errors.extend(schema_errors(contract, docs["contract_schema"], "CONTRACT"))
    errors.extend(schema_errors(fixture, docs["fixture_schema"], "FIXTURE"))
    if (
        contract.get("schema") != "deeplus.keyable-iteration-pattern-assignment/r106"
        or contract.get("revision") != "r106-closed-keyable-iteration-pattern-assignment"
        or contract.get("status") != "LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF"
        or contract.get("decision_report")
        != "decisions/language/Design_Deeplus_Keyable_Iteration_Pattern_Assignment_R106.md"
        or not (root / contract.get("decision_report", "__missing__")).is_file()
        or contract.get("baseline", {}).get("predecessor_commit")
        != "cc16fdd33112394861adea38846b40ae3373fb4b"
        or contract.get("baseline", {}).get("current_binding") is not False
    ):
        errors.append("CONTRACT_IDENTITY")

    scope = contract.get("scope", {})
    if (
        scope.get("new_syntax_count") != 0
        or scope.get("algorithms") != ALGORITHMS
        or scope.get("predicate_ids") != PREDICATE_IDS
        or scope.get("feature_ids") != FEATURE_IDS
    ):
        errors.append("SCOPE_EXACT")

    keyable = contract.get("keyable", {})
    if (
        keyable.get("algorithm_id") != ALGORITHMS[0]
        or len(keyable.get("ordered_steps", [])) != 6
        or len(keyable.get("diagnostic_precedence", [])) != 2
        or len(keyable.get("rejected_domains", [])) != 4
        or not any("Float64" in item for item in keyable.get("rejected_domains", []))
        or not any("lifecycle" in item for item in keyable.get("rejected_domains", []))
        or "no witness" not in keyable.get("failure_atomicity", "")
    ):
        errors.append("KEYABLE_ALGORITHM")

    iteration = contract.get("iteration", {})
    if (
        iteration.get("algorithm_id") != ALGORITHMS[1]
        or iteration.get("route_order") != [
            "DIRECT_ITERATOR when the source has one exact Iterator conformance",
            "SEQUENCE_ACQUIRE otherwise when the source has one exact Sequence conformance whose iterator result has one exact Iterator conformance",
            "REJECT otherwise",
        ]
        or len(iteration.get("ordered_steps", [])) != 7
        or iteration.get("current_profile", {}).get("next_result") != "Option<Item>"
        or iteration.get("current_profile", {}).get("suspension") is not False
        or len(iteration.get("hir_residue", [])) != 8
    ):
        errors.append("ITERATION_ALGORITHM")

    assignment = contract.get("pattern_assignment", {})
    if (
        assignment.get("algorithm_id") != ALGORITHMS[2]
        or assignment.get("surface_owners") != ["PatternAssignmentStmt", "ParallelAssignmentStmt"]
        or assignment.get("admitted_shapes")[:3] != [
            "Tuple",
            "List when irrefutability is statically proven for the exact RHS type",
            "Record",
        ]
        or len(assignment.get("ordered_steps", [])) != 7
        or "target_write_count is zero" not in assignment.get("failure_atomicity", "")
        or len(assignment.get("hir_residue", [])) != 7
    ):
        errors.append("ASSIGNMENT_ALGORITHM")

    migration = contract.get("surface_migration", {})
    pattern_text = json.dumps(pattern, ensure_ascii=False, sort_keys=True)
    if (
        migration != {
            "map_literal_unfold": "*expr",
            "map_pattern_open_ignore": "*_",
            "map_pattern_open_capture": "*name",
            "record_static_named_rest": "_** or name**",
            "removed_map_pattern_rest_spellings": [".._", "..name"],
        }
        or pattern.get("pattern_algebra", {}).get("map_open_ignore") != "*_"
        or pattern.get("pattern_algebra", {}).get("map_open_capture") != "*name"
        or pattern.get("record_map_nominal", {}).get("map_open_ignore") != "*_"
        or pattern.get("record_map_nominal", {}).get("map_open_capture") != "*name"
        or '"map_open_ignore": ".._"' in pattern_text
        or '"map_open_capture": "..name"' in pattern_text
    ):
        errors.append("MAP_REST_MIGRATION")

    if (
        fixture.get("schema") != "deeplus.keyable-iteration-pattern-assignment-fixtures/r106"
        or fixture.get("contract") != CONTRACT.as_posix()
    ):
        errors.append("FIXTURE_IDENTITY")
    cases = fixture.get("cases", [])
    classes = {name: sum(row.get("class") == name for row in cases) for name in ("positive", "boundary", "reject")}
    algorithms = {name: sum(row.get("algorithm") == name for row in cases) for name in ALGORITHMS}
    if (
        len(cases) != 24
        or len({row.get("id") for row in cases}) != 24
        or classes != {"positive": 8, "boundary": 7, "reject": 9}
        or algorithms != {"KeyableSelectionV1": 8, "ForIteratorPlanV1": 9, "LocalPatternAssignmentV1": 7}
        or any(not row.get("oracle") for row in cases)
    ):
        errors.append("FIXTURE_PARTITION")

    contract_rel = CONTRACT.as_posix()
    predicate_algorithms = {
        "KeyableAdmissible": "HashPolicyId",
        "ForSourceIterableAdmitted": "ForIteratorPlanId",
        "LocalGroupAssignmentAdmitted": "PatternAssignmentCommitId",
    }
    for predicate_id, exact_residue in predicate_algorithms.items():
        row = predicates.get(predicate_id, {})
        if (
            row.get("predicate_maturity") != "design_algorithm"
            or row.get("emission_eligible") is not True
            or row.get("predecessor_contract") != contract_rel
            or "R106" not in row.get("summary", "")
            or not row.get("decision_procedure")
            or exact_residue not in json.dumps(row, ensure_ascii=False)
        ):
            errors.append(f"PREDICATE_BINDING:{predicate_id}")
    for predicate_id in ("KeyableAdmissible", "ForSourceIterableAdmitted"):
        if predicates.get(predicate_id, {}).get("diagnostic_disposition") != "active_primary":
            errors.append(f"PREDICATE_DIAGNOSTIC:{predicate_id}")

    expected_productions = {
        "iterator_protocol_core": {"ForLoop"},
        "keyable_key_admissibility_v2": set(),
        "local_group_tuple_assignment": {"PatternAssignmentStmt", "ParallelAssignmentStmt"},
    }
    for feature_id in FEATURE_IDS:
        row = features.get(feature_id, {})
        trace = row.get("normative_trace_refs", {})
        if (
            row.get("status_enum") != "STABLE_DESIGN"
            or "R106" not in row.get("notes", "")
            or not trace.get("predicates")
            or set(trace.get("productions", [])) != expected_productions[feature_id]
        ):
            errors.append(f"FEATURE_BINDING:{feature_id}")

    if DIAGNOSTIC_IDS - set(diagnostics):
        errors.append("DIAGNOSTIC_SET")
    for diagnostic_id in ("FOR_SOURCE_NOT_ITERABLE", "ITERATOR_CLEANUP_EFFECT_NOT_ACCOUNTED"):
        row = diagnostics.get(diagnostic_id, {})
        if "R106" not in row.get("notes", "") or "Design-time diagnostic seed" in row.get("notes", ""):
            errors.append(f"DIAGNOSTIC_ACTIVATION:{diagnostic_id}")

    acceptance = contract.get("acceptance", {})
    if acceptance != {
        "fixture_path": FIXTURE.as_posix(),
        "case_count": 24,
        "positive_count": 8,
        "boundary_count": 7,
        "reject_count": 9,
        "required_mutation_count": 12,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_checker_runtime": "NOT_RUN",
        "github_mutation": 0,
    }:
        errors.append("GOVERNANCE_ACCEPTANCE")
    if fixture.get("governance") != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_execution": "NOT_RUN",
    }:
        errors.append("FIXTURE_GOVERNANCE")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    docs = {
        "contract": load(root / CONTRACT),
        "contract_schema": load(root / CONTRACT_SCHEMA),
        "fixture": load(root / FIXTURE),
        "fixture_schema": load(root / FIXTURE_SCHEMA),
        "pattern": load(root / PATTERN_CONTRACT),
        "predicates": catalog(root, PREDICATE_DIR, "predicate_id"),
        "features": catalog(root, FEATURE_DIR, "feature_id"),
        "diagnostics": catalog(root, DIAGNOSTIC_DIR, "diagnostic_id"),
    }
    errors = model_errors(root, docs)
    rejected = 0
    mutation_total = 0
    if args.mutations and not errors:
        mutations: list[dict[str, Any]] = []
        for index in range(12):
            candidate = copy.deepcopy(docs)
            if index == 0:
                candidate["contract"]["scope"]["algorithms"][0] = "RuntimeKeyableLookup"
            elif index == 1:
                candidate["contract"]["keyable"]["rejected_domains"].pop(0)
            elif index == 2:
                candidate["contract"]["iteration"]["route_order"].reverse()
            elif index == 3:
                candidate["contract"]["iteration"]["current_profile"]["suspension"] = True
            elif index == 4:
                candidate["contract"]["pattern_assignment"]["surface_owners"].pop()
            elif index == 5:
                candidate["contract"]["surface_migration"]["map_pattern_open_capture"] = "..name"
            elif index == 6:
                candidate["fixture"]["cases"].pop()
            elif index == 7:
                candidate["fixture"]["cases"][0]["id"] = candidate["fixture"]["cases"][1]["id"]
            elif index == 8:
                candidate["predicates"]["KeyableAdmissible"]["emission_eligible"] = False
            elif index == 9:
                candidate["features"]["iterator_protocol_core"]["normative_trace_refs"]["productions"] = []
            elif index == 10:
                candidate["pattern"]["pattern_algebra"]["map_open_ignore"] = ".._"
            else:
                candidate["contract"]["acceptance"]["product_lanes"] = "15_OF_15_PASS"
            mutations.append(candidate)
        mutation_total = len(mutations)
        rejected = sum(bool(model_errors(root, candidate)) for candidate in mutations)
        if rejected != mutation_total:
            errors.append("MUTATION_SURVIVED")

    receipt = {
        "schema": "deeplus.keyable-iteration-pattern-assignment-validation/r106",
        "result": "PASS" if not errors else "FAIL",
        "algorithm_count": 3,
        "fixture_count": 24,
        "predicate_count": 3,
        "feature_count": 3,
        "mutation_rejections": rejected,
        "mutation_total": mutation_total,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_checker_runtime": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
