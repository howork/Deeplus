#!/usr/bin/env python3
"""Validate the bounded R63 stale Trait-associated-static diagnostic removal."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/companion-capability-coherence.json"
FIXTURE_REL = "tests/fixtures/current/companion-capability-coherence-r1.json"
DECISION_REL = "decisions/language/Design_Deeplus_R63_Trait_Associated_Static_Stale_Diagnostic_Removal_R1.md"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
R62_CONTRACT_REL = "spec/contracts/trait-qualified-associated-static-selection-trace-closure-r1.json"
R62_SCHEMA_REL = "schemas/language/trait-qualified-associated-static-selection-trace-closure-r1.schema.json"
R62_DECISION_REL = "decisions/language/Design_Deeplus_R62_Trait_Qualified_Associated_Static_Selection_Dynamic_Trace_Closure_R1.md"

STALE = "TRAIT_ASSOCIATED_STATIC_AMBIGUOUS"
WITNESS_DIAGNOSTIC = "TRAIT_AMBIGUOUS_IMPORTED_WITNESS"
EXPLICIT_DIAGNOSTIC = "TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION"
TARGET_FEATURE = "trait_qualified_associated_static_selection"
EXPECTED_FAMILIES = [
    EXPLICIT_DIAGNOSTIC,
    "TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND",
    "TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH",
    "TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE",
    "TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN",
    "TYPE_SIDE_PRIVATE_CONSTRUCTION_AUTHORITY_FORBIDDEN",
    "ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED",
    "COMPANION_OBJECT_NOT_CURRENT",
    "TYPE_TOKEN_RUNTIME_AUTHORITY_FORBIDDEN",
    "STATIC_CLASS_DECLARATION_NOT_CURRENT",
]
EXPECTED_TRAIT_DIAGNOSTICS = [
    EXPLICIT_DIAGNOSTIC,
    "TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND",
    "TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH",
    "TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE",
    "TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN",
    "ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED",
]
NEG_SCENARIO = (
    "explicit <T as Factory>::default with exactly two visible normalized "
    "T conforms Factory candidates"
)
NEG_ASSERTIONS = [
    "explicit qualification fixes TraitId before conformance witness resolution",
    "WitnessResolution rejects the two visible normalized T conforms Factory "
    "candidates before associated-item lookup",
    "no requirement, implementation, substitution, responsibility, runtime "
    "lookup, fallback, or activation is selected",
]
MUT_SCENARIO = (
    "mutant merges nominal, named-extension, Trait-associated, and "
    "runtime-value candidates into one lookup list"
)
MUT_ASSERTIONS = [
    "the canonical model retains exactly four disjoint domains",
    "no cross-domain candidate ranking or fallback is admitted",
    "the merged-domain mutant is detected before lowering",
]
TRACE_COUNTS = (2458, 3, 502, 1258)
TRACE_CANONICAL_SHA256 = "ac89d69349e676dd52278515300a5ccea1fc97159ebf269441bdfc530f3b00df"
META_CANONICAL_SHA256 = "697fbe1b628cab4c14bb993901b3e49926459514b6abd66ed56ac44296f3a08a"
TRACE_FILE_SHA256 = "7c3133c47ea6d5d39d4dadb460109335fe517ca4fd7083adb87d674eb69654a5"
META_FILE_SHA256 = "1ad04e14c36f2bb1a3609667526a6655f04f29901771876f034e5717dbd1823a"
UNRELATED_FIXTURES_SHA256 = "eef6d03e9dc2bc6a6f0fa55478ee1bd57e9db9f8b7be9906dd36f097a2454f23"
FIXTURE_IDS_SHA256 = "9d4786644baa5988a507391faf018f0895daf88174140a8bdebfbec48530f4d7"
R62_HASHES = {
    R62_CONTRACT_REL: "3547a75ac7d4a2bae8305272d29b6612e957de5d7dd3a432e6da15fa564d531b",
    R62_SCHEMA_REL: "372ff4d441cc6aee7f2b668a7b2a1c5933fcb849d71fdd3a95acb8bda0508e42",
    R62_DECISION_REL: "0e261b00d9fd79f5c9015fe371b384eeb30d47d82408ff7f6d1f363858cad9f1",
}
ACCEPTANCE_IDS = [f"R63-AC-{index:03d}" for index in range(1, 11)]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_shards(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative / "chunks").glob("part-*.json")):
        rows.extend(load(path))
    return rows


def canonical_sha(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace_dispositions(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str | None], str]:
    result: dict[tuple[str, str, str | None], str] = {}
    for row in rows:
        feature = row.get("feature_id")
        for stage in row.get("stages", []):
            name = stage.get("stage")
            if name == "CONFORMANCE_TESTS":
                for outcome in stage.get("outcomes", []):
                    result[(feature, name, outcome.get("outcome"))] = outcome.get("disposition")
            else:
                result[(feature, name, None)] = stage.get("disposition")
    return result


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
    diagnostics_override: list[dict[str, Any]] | None = None,
    relations_override: list[dict[str, Any]] | None = None,
    predicates_override: list[dict[str, Any]] | None = None,
    features_override: list[dict[str, Any]] | None = None,
    trace_override: list[dict[str, Any]] | None = None,
    metadata_override: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    contract = contract_override or load(root / CONTRACT_REL)
    fixture = fixture_override or load(root / FIXTURE_REL)
    diagnostics = diagnostics_override or load_shards(root, "spec/diagnostics/catalog")
    relations = relations_override or load_shards(root, "spec/diagnostics/relations")
    predicates = predicates_override or load_shards(root, "spec/types/predicates")
    features = features_override or load_shards(root, "spec/features/catalog")
    trace = trace_override or load(root / TRACE_REL)
    metadata = metadata_override or load(root / META_REL)
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def check(check_id: str, condition: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL"})
        if not condition:
            errors.append(f"{check_id}:{detail}")

    families = contract.get("diagnostic_families", [])
    check(
        "R63-AC-001",
        families == EXPECTED_FAMILIES
        and len(families) == len(set(families)) == 10
        and STALE not in json.dumps(contract, ensure_ascii=False),
        families,
    )

    cases = fixture.get("cases", [])
    by_id = {row.get("fixture_id"): row for row in cases}
    neg = by_id.get("CCC-R1-NEG-009", {})
    neg_oracle = neg.get("oracle", {})
    zero_identity_keys = (
        "selected_requirement_id_count",
        "selected_conformance_id_count",
        "selected_trait_witness_id_count",
        "selected_implementation_id_count",
        "selected_substitution_id_count",
        "selected_responsibility_id_count",
        "runtime_lookup_count",
        "fallback_count",
        "activation_trigger_count",
        "product_execution_count",
    )
    check(
        "R63-AC-002",
        neg.get("fixture_class") == "negative"
        and neg.get("source_or_scenario") == NEG_SCENARIO
        and neg.get("expected_design") == "REJECT"
        and neg.get("diagnostic_family_or_null") == WITNESS_DIAGNOSTIC
        and neg.get("assertions") == NEG_ASSERTIONS
        and neg_oracle.get("lookup_domain") == "TRAIT_QUALIFIED_ASSOCIATED_STATIC"
        and neg_oracle.get("lookup_domain_count") == 4
        and neg_oracle.get("associated_item_kind") is None
        and neg_oracle.get("selected_trait_id_count") == 1
        and all(neg_oracle.get(key) == 0 for key in zero_identity_keys)
        and neg.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
        and neg.get("product_support") == "NOT_RUN"
        and neg.get("product_receipt") is None,
        neg,
    )

    mutant = by_id.get("CCC-R1-MUT-022", {})
    check(
        "R63-AC-003",
        mutant.get("fixture_class") == "mutation"
        and mutant.get("source_or_scenario") == MUT_SCENARIO
        and mutant.get("expected_design") == "MUTANT_KILLED"
        and mutant.get("diagnostic_family_or_null") is None
        and mutant.get("assertions") == MUT_ASSERTIONS
        and mutant.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
        and mutant.get("product_support") == "NOT_RUN"
        and mutant.get("product_receipt") is None,
        mutant,
    )

    diag_counts = Counter(row.get("diagnostic_id") for row in diagnostics)
    active_witness = [
        row for row in diagnostics
        if row.get("diagnostic_id") == WITNESS_DIAGNOSTIC
        and row.get("diagnostic_status") == "active"
        and row.get("diagnostic_maturity") == "active"
        and row.get("diagnostic_class") == "current_source"
        and row.get("stage") == "checker"
        and row.get("severity") == "error"
        and row.get("product_support") == "NOT_RUN"
    ]
    active_explicit = [
        row for row in diagnostics
        if row.get("diagnostic_id") == EXPLICIT_DIAGNOSTIC
        and row.get("diagnostic_status") == "active"
    ]
    check(
        "R63-AC-004",
        diag_counts[STALE] == 0
        and diag_counts[WITNESS_DIAGNOSTIC] == len(active_witness) == 1
        and diag_counts[EXPLICIT_DIAGNOSTIC] == len(active_explicit) == 1,
        {"stale": diag_counts[STALE], "witness": active_witness, "explicit": active_explicit},
    )

    witness_predicates = [row for row in predicates if row.get("predicate_id") == "WitnessResolution"]
    selection_predicates = [row for row in predicates if row.get("predicate_id") == "TraitAssociatedStaticSelectionAdmitted"]
    primary_relations = [
        row for row in relations
        if row == {
            "violation_id": "WitnessResolution:default",
            "predicate_id": "WitnessResolution",
            "diagnostic_id": WITNESS_DIAGNOSTIC,
            "relation": "primary",
        }
    ]
    active_documents = [diagnostics, relations, predicates, features, cases]
    check(
        "R63-AC-005",
        all(STALE not in json.dumps(value, ensure_ascii=False) for value in active_documents)
        and len(witness_predicates) == 1
        and witness_predicates[0].get("active_primary_diagnostic") == WITNESS_DIAGNOSTIC
        and WITNESS_DIAGNOSTIC in witness_predicates[0].get("diagnostic_refs", [])
        and any(
            "more than one emits TRAIT_AMBIGUOUS_IMPORTED_WITNESS" in step
            for step in witness_predicates[0].get("decision_procedure", [])
        )
        and len(primary_relations) == 1
        and len(selection_predicates) == 1
        and selection_predicates[0].get("diagnostic_refs") == EXPECTED_TRAIT_DIAGNOSTICS
        and selection_predicates[0].get("active_primary_diagnostic") == EXPLICIT_DIAGNOSTIC,
        {"witness": witness_predicates, "relations": primary_relations, "selection": selection_predicates},
    )

    class_counts = Counter(row.get("fixture_class") for row in cases)
    unrelated = [row for row in cases if row.get("fixture_id") not in {"CCC-R1-NEG-009", "CCC-R1-MUT-022"}]
    fixture_ids = [row.get("fixture_id") for row in cases]
    check(
        "R63-AC-006",
        len(cases) == len(set(fixture_ids)) == 28
        and class_counts == Counter({"positive": 7, "negative": 7, "boundary": 7, "mutation": 7})
        and canonical_sha(unrelated) == UNRELATED_FIXTURES_SHA256
        and canonical_sha(fixture_ids) == FIXTURE_IDS_SHA256,
        {"count": len(cases), "classes": dict(class_counts)},
    )

    machine = contract.get("machine_acceptance", {})
    check(
        "R63-AC-007",
        machine.get("rule_count") == 18
        and machine.get("fixture_count") == 28
        and all(
            machine.get(key) == 0
            for key in (
                "runtime_lookup_count",
                "activation_trigger_count",
                "companion_object_count",
                "type_name_runtime_value_conversion_count",
                "external_private_authority_escalation_count",
                "invalid_associated_value_profile_admitted_count",
                "class_scope_static_current_acceptance_count",
                "new_CALL_INPUT_COMMIT_event_count",
                "product_executed_count",
            )
        )
        and contract.get("source_activation") == "none",
        machine,
    )

    dispositions = trace_dispositions(trace)
    disposition_counts = Counter(dispositions.values())
    target_row = next((row for row in trace if row.get("feature_id") == TARGET_FEATURE), {})
    target_diagnostics = next((stage for stage in target_row.get("stages", []) if stage.get("stage") == "DIAGNOSTICS"), {})
    overlays = metadata.get("applied_evidence_overlays", [])
    derived = metadata.get("derived_counts", {})
    check(
        "R63-AC-008",
        canonical_sha(trace) == TRACE_CANONICAL_SHA256
        and canonical_sha(metadata) == META_CANONICAL_SHA256
        and file_sha(root / TRACE_REL) == TRACE_FILE_SHA256
        and file_sha(root / META_REL) == META_FILE_SHA256
        and target_diagnostics.get("disposition") == "BOUND_DIRECT"
        and disposition_counts["BOUND_DIRECT"] == TRACE_COUNTS[0]
        and disposition_counts["BOUND_DELEGATED"] == TRACE_COUNTS[1]
        and disposition_counts["NOT_APPLICABLE"] == TRACE_COUNTS[2]
        and disposition_counts["APPLICABLE_BLOCKED_BY_GAP"] == TRACE_COUNTS[3]
        and len(overlays) == 9
        and sum(row.get("binding_count", 0) for row in overlays) == 121
        and derived.get("bound_direct_cells") == TRACE_COUNTS[0]
        and derived.get("bound_delegated_cells") == TRACE_COUNTS[1]
        and derived.get("not_applicable_cells") == TRACE_COUNTS[2]
        and derived.get("applicable_blocked_cells") == TRACE_COUNTS[3]
        and derived.get("missing_cells") == derived.get("conflict_cells") == 0,
        {"counts": dict(disposition_counts), "derived": derived},
    )

    open_p1 = contract.get("open_feature_p1", {})
    product_lanes = fixture.get("product_lanes", {})
    governance = metadata.get("governance", {})
    check(
        "R63-AC-009",
        contract.get("semantic_p0") == fixture.get("semantic_p0") == 0
        and open_p1.get("total") == 22
        and open_p1.get("closed_by_this_contract") == open_p1.get("created_by_this_contract") == 0
        and fixture.get("p1_delta") == {"closed": 0, "created": 0}
        and len(fixture.get("open_feature_p1", [])) == 22
        and contract.get("product_lanes") == "15/15_NOT_RUN"
        and len(product_lanes) == 15
        and all(value == "NOT_RUN" for value in product_lanes.values())
        and governance.get("semantic_p0") == 0
        and governance.get("feature_p1") == "22_OPEN_UNCHANGED"
        and governance.get("m13_actions") == "4_OPEN_UNCHANGED"
        and governance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and governance.get("github_publication") == "SUSPENDED",
        {"open_p1": open_p1, "product_lanes": product_lanes, "governance": governance},
    )

    decision_path = root / DECISION_REL
    decision = decision_path.read_text(encoding="utf-8") if decision_path.is_file() else ""
    historical_ok = all(
        (root / path).is_file()
        and file_sha(root / path) == digest
        and STALE in (root / path).read_text(encoding="utf-8")
        for path, digest in R62_HASHES.items()
    )
    check(
        "R63-AC-010",
        historical_ok
        and decision_path.is_file()
        and "IR-DIAG-P2-055" in decision
        and "eec3b840176e8b401cabac1fc32ab61e7d0ace49" in decision
        and all(check_id in decision for check_id in ACCEPTANCE_IDS),
        {"historical_ok": historical_ok, "decision": DECISION_REL},
    )

    if [row["check_id"] for row in checks] != ACCEPTANCE_IDS:
        errors.append("R63_ACCEPTANCE_ID_ORDER")
    return checks, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    checks, errors = validate(root)
    receipt = {
        "schema": "deeplus.trait-associated-static-stale-diagnostic-removal-validation/r1",
        "result": "PASS" if not errors else "FAIL",
        "acceptance_check_count": len(checks),
        "passed_check_count": sum(row["result"] == "PASS" for row in checks),
        "checks": checks,
        "trace_transition_count": 0,
        "trace_evidence_transition_count": 0,
        "fixture_count": 28,
        "fixture_class_counts": {"positive": 7, "negative": 7, "boundary": 7, "mutation": 7},
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
