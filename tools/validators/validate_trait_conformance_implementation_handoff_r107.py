#!/usr/bin/env python3
"""Validate the R107 action-complete Trait Conformance implementation handoff."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("spec/contracts/trait-conformance-implementation-handoff-r107.json")
CONTRACT_SCHEMA = Path("schemas/language/trait-conformance-implementation-handoff-r107.schema.json")
FIXTURE = Path("tests/fixtures/current/trait-conformance-implementation-handoff-r107.json")
FIXTURE_SCHEMA = Path("schemas/language/trait-conformance-implementation-handoff-fixtures-r107.schema.json")
SURFACE = Path("spec/contracts/trait-conformance-surface.json")
R102 = Path("spec/contracts/implementation-target-feature-local-acceptance-r102.json")
READINESS = Path("spec/contracts/implementation-readiness-r99-audit-closure.json")
FRONTEND = Path("spec/frontend/frontend-model.json")
LANGUAGE = Path("spec/language.md")
MIR = Path("spec/mir/semantics.md")
PREDICATE_DIR = Path("spec/types/predicates/chunks")
DIAGNOSTIC_DIR = Path("spec/diagnostics/catalog/chunks")
TARGET_ROWS = Path("spec/traceability/implementation-target-profile-r1/rows.json")

ACTIONS = [f"TCC-P1-{index:03d}" for index in range(2, 9)]
TC_RULES = [f"TC-R{index:03d}" for index in range(1, 17)]
ALGORITHMS = [
    "ConformanceSurfaceCommitV1",
    "ConformanceCoherenceSealV1",
    "ConformanceDiagnosticOrderV1",
    "ConformanceRouteAdmissionV1",
    "ConformanceIdentityProjectionV1",
    "ConformanceCorpusReceiptV1",
    "ConformanceToolingContractV1",
]
DEPENDENCIES = {
    "TCC-P1-002": [],
    "TCC-P1-003": ["TCC-P1-002"],
    "TCC-P1-004": ["TCC-P1-002", "TCC-P1-003"],
    "TCC-P1-005": ["TCC-P1-002"],
    "TCC-P1-006": ["TCC-P1-003", "TCC-P1-004", "TCC-P1-005"],
    "TCC-P1-007": ["TCC-P1-002", "TCC-P1-003", "TCC-P1-004", "TCC-P1-005", "TCC-P1-006"],
    "TCC-P1-008": ["TCC-P1-002", "TCC-P1-004", "TCC-P1-006", "TCC-P1-007"],
}
DIAGNOSTICS = [
    "CONFORMANCE_DECLARATION_REQUIRES_CONFORMS_KEYWORD",
    "TRAIT_METHOD_DUPLICATE_SLOT",
    "WITNESS_ORPHAN_RULE_VIOLATION",
    "TRAIT_OVERLAPPING_WITNESS",
    "TRAIT_CONDITIONAL_PROOF_NOT_WELL_FOUNDED",
    "TRAIT_SUPER_WITNESS_MISSING",
    "TRAIT_REQUIREMENT_VISIBILITY_MISMATCH",
    "TRAIT_MISSING_WITNESS",
    "TRAIT_ASSOCIATED_REQUIREMENT_MISSING",
    "TRAIT_MIR_EVIDENCE_INCOMPLETE",
]
PREDICATES = {
    "ConformanceDeclProducesWitness",
    "ConformanceEvidenceOriginAdmitted",
    "WitnessCoherent",
    "WitnessResolution",
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
    surface = docs["surface"]
    r102 = docs["r102"]
    readiness = docs["readiness"]
    frontend = docs["frontend"]
    language = docs["language"]
    mir = docs["mir"]
    predicates = docs["predicates"]
    diagnostics = docs["diagnostics"]
    target_ids = docs["target_ids"]

    errors.extend(schema_errors(contract, docs["contract_schema"], "CONTRACT"))
    errors.extend(schema_errors(fixture, docs["fixture_schema"], "FIXTURE"))
    if (
        contract.get("schema") != "deeplus.trait-conformance-implementation-handoff/r107"
        or contract.get("revision") != "r107-trait-conformance-action-complete-handoff"
        or contract.get("status") != "LOCAL_DESIGN_STATIC_IMPLEMENTATION_HANDOFF"
        or contract.get("decision_report")
        != "decisions/language/Design_Deeplus_Trait_Conformance_Implementation_Handoff_R107.md"
        or not (root / contract.get("decision_report", "__missing__")).is_file()
        or contract.get("baseline", {}).get("predecessor_commit")
        != "750885a2e0b552d7efdd58ef4ee996ad3d02bc48"
        or contract.get("baseline", {}).get("current_binding") is not False
    ):
        errors.append("CONTRACT_IDENTITY")

    scope = contract.get("scope", {})
    if (
        scope.get("new_syntax_count") != 0
        or scope.get("tc_rule_ids") != TC_RULES
        or scope.get("action_ids") != ACTIONS
        or scope.get("current_routes")
        != ["DIRECT_GLOBAL", "LOWERCASE_VIA", "REGISTERED_BODYLESS_BY_AUTO"]
        or set(scope.get("forbidden_routes", []))
        != {"LOCAL", "STRUCTURAL", "RUNTIME", "UPPERCASE_VIA", "UPPERCASE_AUTO", "SPECIALIZATION", "CHILD_LOCAL_PARENT_REPLACEMENT"}
    ):
        errors.append("SCOPE_EXACT")

    pipeline = contract.get("pipeline", {})
    phases = pipeline.get("ordered_phases", [])
    expected_phase_ids = ["SOURCE_COMMIT", "NORMALIZE_IDENTITY", "COHERENCE", "BIND_REQUIREMENTS", "ADMIT_ROUTE", "SEAL_HIR", "PROJECT_MIR"]
    required_hir = {"ConformanceId", "TraitWitnessId", "RequirementId", "ImplementationId", "SubstitutionId", "ResponsibilityId", "AuthorityId", "SupertraitLinkIds", "AssociatedBindingIds", "DerivationDigest"}
    if (
        pipeline.get("algorithm_id") != "TraitConformanceSealV1"
        or [row.get("phase") for row in phases] != list(range(1, 8))
        or [row.get("id") for row in phases] != expected_phase_ids
        or not required_hir.issubset(set(pipeline.get("hir_residue", [])))
        or pipeline.get("canonical_hir_requires_complete_identity") is not True
        or pipeline.get("mir_runtime_relookup_count") != 0
        or pipeline.get("source_import_order_winner_count") != 0
        or pipeline.get("fallback_count") != 0
    ):
        errors.append("PIPELINE_EXACT")

    diagnostic_rows = contract.get("diagnostic_order", [])
    if (
        [row.get("rank") for row in diagnostic_rows] != list(range(1, 11))
        or [row.get("diagnostic_id") for row in diagnostic_rows] != DIAGNOSTICS
        or any(not row.get("failure") for row in diagnostic_rows)
        or any(diagnostic_id not in diagnostics for diagnostic_id in DIAGNOSTICS)
    ):
        errors.append("DIAGNOSTIC_ORDER")
    for diagnostic_id in DIAGNOSTICS:
        row = diagnostics.get(diagnostic_id, {})
        if row.get("diagnostic_status") != "active" or row.get("product_support") != "NOT_RUN":
            errors.append(f"DIAGNOSTIC_BINDING:{diagnostic_id}")

    actions = contract.get("actions", [])
    if [row.get("action_id") for row in actions] != ACTIONS or [row.get("algorithm") for row in actions] != ALGORITHMS:
        errors.append("ACTION_ORDER")
    for row in actions:
        action_id = row.get("action_id")
        suffix = action_id[-3:] if isinstance(action_id, str) else ""
        expected_acceptance = [f"R107-TCC{suffix}-{kind}" for kind in ("P", "B", "N")]
        if (
            row.get("dependencies") != DEPENDENCIES.get(action_id)
            or not row.get("obligation")
            or not row.get("canonical_output")
            or row.get("acceptance_ids") != expected_acceptance
        ):
            errors.append(f"ACTION_BINDING:{action_id}")

    if fixture.get("schema") != "deeplus.trait-conformance-implementation-handoff-fixtures/r107" or fixture.get("contract") != CONTRACT.as_posix():
        errors.append("FIXTURE_IDENTITY")
    cases = fixture.get("cases", [])
    class_counts = {name: sum(row.get("class") == name for row in cases) for name in ("positive", "boundary", "reject")}
    if (
        len(cases) != 21
        or len({row.get("id") for row in cases}) != 21
        or class_counts != {"positive": 7, "boundary": 7, "reject": 7}
        or {row.get("action_id") for row in cases} != set(ACTIONS)
        or any(sum(item.get("action_id") == action and item.get("class") == klass for item in cases) != 1 for action in ACTIONS for klass in ("positive", "boundary", "reject"))
        or any(not row.get("oracle") or not row.get("expected") for row in cases)
    ):
        errors.append("FIXTURE_PARTITION")

    if surface.get("current_binding") is not False or surface.get("status") != "STABLE_DESIGN":
        errors.append("SURFACE_AUTHORITY_FENCE")
    if set(surface.get("open_feature_p1", [])) != set(ACTIONS):
        errors.append("SURFACE_OPEN_P1_SET")
    frontend_handoff = frontend.get("trait_conformance_surface_contract", {}).get("implementation_handoff", {})
    if (
        frontend_handoff.get("contract") != CONTRACT.as_posix()
        or frontend_handoff.get("algorithm") != "TraitConformanceSealV1"
        or frontend_handoff.get("ordered_phase_count") != 7
        or frontend_handoff.get("diagnostic_rank_count") != 10
        or frontend_handoff.get("canonical_hir_requires_complete_identity") is not True
        or frontend_handoff.get("mir_runtime_relookup_count") != 0
        or frontend_handoff.get("action_ids") != ACTIONS
        or frontend_handoff.get("execution_receipts") != "OPEN_NOT_RUN"
        or frontend_handoff.get("product_support") != "NOT_RUN"
    ):
        errors.append("FRONTEND_HANDOFF")

    if any(f"<!-- POST_PR16_UNIT_BEGIN:{rule} -->" not in language for rule in TC_RULES):
        errors.append("TC_RULE_ANCHORS")
    for token in ("TraitConformanceSealV1", CONTRACT.as_posix(), "TCC-P1-002..008", "NOT_RUN"):
        if token not in language:
            errors.append(f"LANGUAGE_BINDING:{token}")
    for token in ("TRAIT_MIR_EVIDENCE_INCOMPLETE", "never reconstruct a witness", "production lowering"):
        if token not in mir:
            errors.append(f"MIR_BINDING:{token}")

    r102_actions = {row.get("action_id"): row for row in r102.get("actions", [])}
    retained_ids: set[str] = set()
    for action in ACTIONS:
        row = r102_actions.get(action, {})
        retained_ids.update(row.get("retained_target_feature_ids", []))
        if row.get("execution_receipt_gate") != "OPEN_NOT_RUN" or row.get("product_execution") != "NOT_RUN":
            errors.append(f"R102_GOVERNANCE:{action}")
    if retained_ids - target_ids:
        errors.append("TARGET_FEATURE_BINDING")

    readiness_rows = {row.get("id"): row for row in readiness.get("feature_p1_lanes", [])}
    for action in ACTIONS:
        row = readiness_rows.get(action, {})
        if (
            row.get("design_contract_gate") != "CLOSED_BY_R107_ACTION_COMPLETE_IMPLEMENTATION_HANDOFF"
            or row.get("execution_receipt_gate") != "OPEN_NOT_RUN"
            or row.get("readiness_effect") != "IMPLEMENTATION_HANDOFF_READY_EXECUTION_REMAINS_OPEN"
        ):
            errors.append(f"READINESS_ACTION:{action}")
    blocker = next((row for row in readiness.get("readiness_blockers", []) if row.get("id") == "R99-READY-BLOCK-002"), {})
    if blocker.get("status") != "CLOSED_BY_R109_INTEGRATED_LOCAL_HANDOFF" or readiness.get("governance", {}).get("bootstrap_readiness_blocker_count") != 1:
        errors.append("READINESS_BLOCKER_FENCE")

    for predicate_id in PREDICATES:
        row = predicates.get(predicate_id, {})
        if row.get("predicate_maturity") != "design_algorithm" or row.get("emission_eligible") is not True or row.get("diagnostic_disposition") != "active_primary":
            errors.append(f"PREDICATE_BINDING:{predicate_id}")

    acceptance = contract.get("acceptance", {})
    if acceptance != {
        "fixture_path": FIXTURE.as_posix(),
        "case_count": 21,
        "positive_count": 7,
        "boundary_count": 7,
        "reject_count": 7,
        "required_mutation_count": 14,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "trait_feature_p1": "7_OPEN_EXECUTION_NOT_RUN",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_parser_checker_mir_tooling": "NOT_RUN",
        "github_mutation": 0,
    }:
        errors.append("GOVERNANCE_ACCEPTANCE")
    if fixture.get("governance") != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "trait_feature_p1": "7_OPEN_EXECUTION_NOT_RUN",
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
        "surface": load(root / SURFACE),
        "r102": load(root / R102),
        "readiness": load(root / READINESS),
        "frontend": load(root / FRONTEND),
        "language": (root / LANGUAGE).read_text(encoding="utf-8"),
        "mir": (root / MIR).read_text(encoding="utf-8"),
        "predicates": catalog(root, PREDICATE_DIR, "predicate_id"),
        "diagnostics": catalog(root, DIAGNOSTIC_DIR, "diagnostic_id"),
        "target_ids": {row["feature_id"] for row in load(root / TARGET_ROWS)},
    }
    errors = model_errors(root, docs)
    rejected = 0
    mutation_total = 0
    if args.mutations and not errors:
        mutations: list[dict[str, Any]] = []
        for index in range(14):
            candidate = copy.deepcopy(docs)
            if index == 0:
                candidate["contract"]["baseline"]["current_binding"] = True
            elif index == 1:
                candidate["contract"]["scope"]["action_ids"].pop()
            elif index == 2:
                candidate["contract"]["pipeline"]["ordered_phases"].reverse()
            elif index == 3:
                candidate["contract"]["pipeline"]["hir_residue"].remove("ConformanceId")
            elif index == 4:
                candidate["contract"]["diagnostic_order"][4]["rank"] = 4
            elif index == 5:
                candidate["contract"]["scope"]["forbidden_routes"].remove("RUNTIME")
            elif index == 6:
                candidate["contract"]["actions"][3]["dependencies"] = []
            elif index == 7:
                candidate["fixture"]["cases"].pop()
            elif index == 8:
                candidate["fixture"]["cases"][0]["id"] = candidate["fixture"]["cases"][1]["id"]
            elif index == 9:
                candidate["surface"]["current_binding"] = True
            elif index == 10:
                candidate["frontend"]["trait_conformance_surface_contract"]["implementation_handoff"]["mir_runtime_relookup_count"] = 1
            elif index == 11:
                candidate["readiness"]["feature_p1_lanes"][14]["execution_receipt_gate"] = "CLOSED"
            elif index == 12:
                candidate["predicates"]["WitnessCoherent"]["emission_eligible"] = False
            else:
                candidate["diagnostics"].pop("TRAIT_MIR_EVIDENCE_INCOMPLETE")
            mutations.append(candidate)
        mutation_total = len(mutations)
        rejected = sum(bool(model_errors(root, candidate)) for candidate in mutations)
        if rejected != mutation_total:
            errors.append("MUTATION_SURVIVED")

    receipt = {
        "schema": "deeplus.trait-conformance-implementation-handoff-validation/r107",
        "result": "PASS" if not errors else "FAIL",
        "action_count": 7,
        "tc_rule_count": 16,
        "diagnostic_rank_count": 10,
        "fixture_count": 21,
        "mutation_rejections": rejected,
        "mutation_total": mutation_total,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "trait_feature_p1": "7_OPEN_EXECUTION_NOT_RUN",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_execution": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
