#!/usr/bin/env python3
"""Validate the bounded R64 associated-requirement Phase A trace closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DECISION_REL = "decisions/language/Design_Deeplus_R64_Associated_Requirement_Phase_A_Trace_Closure_R1.md"
CONTRACT_REL = "spec/contracts/associated-requirement-phase-a-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/associated-requirement-phase-a-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/associated-requirement-phase-a-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/associated-requirement-phase-a-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
FIXTURE_REL = "tests/fixtures/current/diagnostic-dispatch-closure-r1.json"
CONFORMANCE_REL = "tests/conformance/diagnostic-dispatch-closure/chunks/part-0001.json"
PREDICATE_DIR_REL = "spec/types/predicates/chunks"
R62_CONTRACT_REL = "spec/contracts/trait-qualified-associated-static-selection-trace-closure-r1.json"
R62_OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/trait-qualified-associated-static-selection-evidence-r1.json"
HIR_BRIDGE_REL = "spec/contracts/hir-h1-current-mir-bridge.json"
HIR_FIXTURE_REL = "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json"
HM_REGISTRY_REL = "spec/contracts/hir-mir-lowering-registry.json"
MIR_SEMANTICS_REL = "spec/mir/semantics.md"
WORKSPACE_VALIDATOR_REL = "tools/validators/validate_workspace.py"
VALIDATOR_REL = "tools/validators/validate_associated_requirement_phase_a_trace_closure.py"

CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "19d8ea962a884f57e45d16883a128405d419bbe6"
FEATURE = "associated_requirement_phase_a"
OWNER_PREDICATE = "AssociatedRequirementAdmitted"
SUPPORTING_PREDICATES = ["AssociatedRequirementWitnessAdmitted", "WherePredicateAdmitted"]
REVISION = "r64-local-associated-requirement-phase-a-trace-closure-r1"
CONTRACT_REVISION = "r64-local-associated-requirement-phase-a-conformance-trace-closure-r1"
OVERLAY_REVISION = "r64-local-associated-requirement-phase-a-dynamic-conformance-trace-closure-r1"
NON_TARGET_CELL_COUNT = 4217
NON_TARGET_DISPOSITION_SHA256 = "8209ca93f4a5b0bf357c3d164c1b4433ef119356e724953d41338f08a530b15d"

TARGETS = {
    (FEATURE, "DYNAMIC_LOWERING", None): "NOT_APPLICABLE",
    (FEATURE, "CONFORMANCE_TESTS", "POSITIVE"): "BOUND_DIRECT",
    (FEATURE, "CONFORMANCE_TESTS", "BOUNDARY"): "BOUND_DIRECT",
    (FEATURE, "CONFORMANCE_TESTS", "REJECT"): "BOUND_DIRECT",
}

REASON_RANKS = [
    "1_requirement_identity_or_kind_conflict",
    "2_requirement_bounds_or_default_not_admitted",
    "3_implementation_binding_unresolved_or_ambiguous",
    "4_recursive_requirement_obligation_cycle",
]

ADMIT = {
    "variant": "ADMIT",
    "reason_key_or_null": None,
    "diagnostic_id_or_null": None,
    "canonical_culprit_id_or_null": None,
    "emitted_primary_count": 0,
    "later_candidate_status": "NOT_APPLICABLE",
}


def reject(reason: str, culprit: str) -> dict[str, Any]:
    return {
        "variant": "REJECT",
        "reason_key_or_null": reason,
        "diagnostic_id_or_null": "ASSOCIATED_REQUIREMENT_UNRESOLVED",
        "canonical_culprit_id_or_null": culprit,
        "emitted_primary_count": 1,
        "later_candidate_status": "NOT_EVALUATED",
    }


CASE_SPECS = [
    ("ARPTC-AC-001", "POSITIVE", "R9-AR-POS-001", "/cases/0", "/0", ADMIT),
    ("ARPTC-AC-002", "POSITIVE", "R9-ADV-AR-VALUE-ADMIT", "/adversarial_cases/0", "/18", ADMIT),
    ("ARPTC-AC-003", "BOUNDARY", "R9-AR-BOUNDARY-001", "/cases/1", "/1", ADMIT),
    ("ARPTC-AC-004", "REJECT", "R9-AR-NEG-001", "/cases/2", "/2", reject(REASON_RANKS[0], "REQ-Item-V")),
    ("ARPTC-AC-005", "REJECT", "R9-AR-NEG-002", "/cases/3", "/3", reject(REASON_RANKS[1], "REQ-Output")),
    ("ARPTC-AC-006", "REJECT", "R9-AR-NEG-003", "/cases/4", "/4", reject(REASON_RANKS[2], "REQ-Output")),
    ("ARPTC-AC-007", "REJECT", "R9-AR-NEG-004", "/cases/5", "/5", reject(REASON_RANKS[3], "REQ-Output")),
    ("ARPTC-AC-008", "REJECT", "R9-ADV-MULTI-ASSOCIATED", "/adversarial_cases/5", "/23", reject(REASON_RANKS[0], "REQ-Item-V")),
]

EXPECTED_BINDINGS = {
    "POSITIVE": ["ARPTC-AC-001", "ARPTC-AC-002"],
    "BOUNDARY": ["ARPTC-AC-003"],
    "REJECT": ["ARPTC-AC-004", "ARPTC-AC-005", "ARPTC-AC-006", "ARPTC-AC-007", "ARPTC-AC-008"],
}

PROTECTED_HEAD_SHA256 = {
    FIXTURE_REL: "23ebd8844ab951d5ad06a02a61544fa57754cc88ce39a241ca2d800849c6ddb9",
    "tests/conformance/diagnostic-dispatch-closure/catalog-metadata.json": "3d05dfd379ea11556fc5cdfdf2988216d67d7164cb465ada57b9aec3ac05e431",
    CONFORMANCE_REL: "a22d090260573d3826010a624ca828acd9ca8289fbd5d61abc14dc5dee25369d",
    "spec/types/predicates/chunks/part-0001.json": "b1e2f54dd391eefa1db139e080fd1f91cabbfa930d7611317e148c7c247e338f",
    "tools/validators/run_diagnostic_dispatch_closure_tests.py": "03fddf9674df0c12bcb1c944b1835358c918ad642df233dce8533d8fe43b6389",
    R62_CONTRACT_REL: "3547a75ac7d4a2bae8305272d29b6612e957de5d7dd3a432e6da15fa564d531b",
    R62_OVERLAY_REL: "ca607deaf9dac62e4020046078bdf9c48ffb5d21e98032d40972d4be12a29fc2",
    "tools/validators/validate_trait_qualified_associated_static_selection_trace.py": "591fbe3c18edcacb6329bd9b8ef704d4ffc2b2d8faaaac75342db8c6dd22cb91",
    HIR_BRIDGE_REL: "a0e63833b94de2bf39b5a9f4a974091903b7fab9cc515062a81656f573c73d2b",
    HIR_FIXTURE_REL: "4b4d0ec6d996c086cd411a0fdb370494b3f7dd9c9bd2dfa1b13e25ec1f5017aa",
    HM_REGISTRY_REL: "5f03bd3bdd1cf00649bd9c99ba6e2ec1c199103d1e81c2546787c485cde99bfe",
    MIR_SEMANTICS_REL: "31f1fd2ca2c3099a4a5930ca7b75791197e3219a904a7a08cc0f64d37c2eec2d",
}

WORKSPACE_REGISTRATION_PATHS = [
    DECISION_REL,
    CONTRACT_REL,
    CONTRACT_SCHEMA_REL,
    OVERLAY_REL,
    OVERLAY_SCHEMA_REL,
    VALIDATOR_REL,
]

GATE_NAMES = {
    "G01": "identity_and_schema_fence",
    "G02": "exact_case_pointer_oracle_parity",
    "G03": "owner_algorithm_and_supporting_predicate_fence",
    "G04": "static_only_and_r62_later_use_fence",
    "G05": "overlay_cardinality_and_trace_records",
    "G06": "dynamic_not_applicable_contract",
    "G07": "direct_conformance_acceptance_sets",
    "G08": "exact_four_cell_transition_and_4217_cell_fence",
    "G09": "registry_overlay_and_disposition_counts",
    "G10": "protected_head_byte_fences",
    "G11": "governance_and_product_honesty",
    "G12": "follow_up_and_workspace_registration_readiness",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_shards(root: Path, relative_dir: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative_dir).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def trace_cells(rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, str, str | None], dict[str, Any]], int]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        feature_id = row.get("feature_id")
        for stage in row.get("stages", []):
            stage_name = stage.get("stage")
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                identity = (feature_id, stage_name, outcome)
                duplicates += identity in cells
                cells[identity] = cell
    return cells, duplicates


def non_target_disposition_digest(cells: dict[tuple[str, str, str | None], dict[str, Any]]) -> tuple[int, str]:
    material = [
        [feature_id, stage, outcome, cell.get("disposition")]
        for (feature_id, stage, outcome), cell in cells.items()
        if (feature_id, stage, outcome) not in TARGETS
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    encoded = json.dumps(material, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return len(material), hashlib.sha256(encoded).hexdigest()


def evidence_id(item: dict[str, Any]) -> str:
    material = "\0".join([item["class"], item["path"], item["locator_kind"], item["locator"], item["stage_role"]])
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(
    root: Path,
    overlay: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
    *,
    validate_schema: bool = True,
    fixture_override: dict[str, Any] | None = None,
    conformance_override: list[dict[str, Any]] | None = None,
    predicates_override: list[dict[str, Any]] | None = None,
    r62_contract_override: dict[str, Any] | None = None,
    r62_overlay_override: dict[str, Any] | None = None,
    hir_bridge_override: dict[str, Any] | None = None,
    hir_fixture_override: dict[str, Any] | None = None,
    hm_registry_override: dict[str, Any] | None = None,
    trace_rows_override: list[dict[str, Any]] | None = None,
    metadata_override: dict[str, Any] | None = None,
    decision_text_override: str | None = None,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    overlay = overlay if overlay is not None else load(root / OVERLAY_REL)
    contract = contract if contract is not None else load(root / CONTRACT_REL)
    fixture = fixture_override if fixture_override is not None else load(root / FIXTURE_REL)
    conformance = conformance_override if conformance_override is not None else load(root / CONFORMANCE_REL)
    predicates = predicates_override if predicates_override is not None else load_shards(root, PREDICATE_DIR_REL)
    r62_contract = r62_contract_override if r62_contract_override is not None else load(root / R62_CONTRACT_REL)
    r62_overlay = r62_overlay_override if r62_overlay_override is not None else load(root / R62_OVERLAY_REL)
    hir_bridge = hir_bridge_override if hir_bridge_override is not None else load(root / HIR_BRIDGE_REL)
    _hir_fixture = hir_fixture_override if hir_fixture_override is not None else load(root / HIR_FIXTURE_REL)
    _hm_registry = hm_registry_override if hm_registry_override is not None else load(root / HM_REGISTRY_REL)
    rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    metadata = metadata_override if metadata_override is not None else load(root / META_REL)
    decision_text = decision_text_override if decision_text_override is not None else (root / DECISION_REL).read_text(encoding="utf-8")
    contract_schema = load(root / CONTRACT_SCHEMA_REL)
    overlay_schema = load(root / OVERLAY_SCHEMA_REL)

    if validate_schema:
        try:
            import jsonschema

            jsonschema.Draft202012Validator(contract_schema).validate(contract)
            jsonschema.Draft202012Validator(overlay_schema).validate(overlay)
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"G01:JSON_SCHEMA:{exc}")

    # G01 — exact R64 identities and the canonical/local split.
    require(f"Canonical baseline: `{CANONICAL}`" in decision_text, "G01", "DECISION_CANONICAL")
    require(f"Local predecessor: `{PREDECESSOR}`" in decision_text, "G01", "DECISION_PREDECESSOR")
    for value, prefix, revision in (
        (contract, "CONTRACT", CONTRACT_REVISION),
        (overlay, "OVERLAY", OVERLAY_REVISION),
    ):
        require(value.get("canonical_baseline_commit") == CANONICAL, "G01", f"{prefix}_CANONICAL")
        require(value.get("local_predecessor_commit") == PREDECESSOR, "G01", f"{prefix}_PREDECESSOR")
        require(value.get("revision") == revision, "G01", f"{prefix}_REVISION")
    require(contract.get("schema") == "deeplus.associated-requirement-phase-a-trace-closure/r1", "G01", "CONTRACT_SCHEMA_ID")
    require(overlay.get("schema") == "deeplus.associated-requirement-phase-a-evidence/r1", "G01", "OVERLAY_SCHEMA_ID")
    require(contract_schema.get("properties", {}).get("canonical_baseline_commit", {}).get("const") == CANONICAL, "G01", "CONTRACT_SCHEMA_CANONICAL")
    require(contract_schema.get("properties", {}).get("local_predecessor_commit", {}).get("const") == PREDECESSOR, "G01", "CONTRACT_SCHEMA_PREDECESSOR")
    require(overlay_schema.get("properties", {}).get("canonical_baseline_commit", {}).get("const") == CANONICAL, "G01", "OVERLAY_SCHEMA_CANONICAL")
    require(overlay_schema.get("properties", {}).get("local_predecessor_commit", {}).get("const") == PREDECESSOR, "G01", "OVERLAY_SCHEMA_PREDECESSOR")

    # G02 — exact existing R9 cases, pointers and expected/observed oracle parity.
    cases = contract.get("acceptance_cases", [])
    require(len(cases) == 8, "G02", "CASE_COUNT_EXACT_8")
    require(Counter(row.get("outcome") for row in cases) == Counter({"POSITIVE": 2, "BOUNDARY": 1, "REJECT": 5}), "G02", "CASE_CLASSES_EXACT_2_1_5")
    for index, spec in enumerate(CASE_SPECS):
        case = cases[index] if index < len(cases) else {}
        case_id, outcome, test_id, fixture_pointer, conformance_pointer, expected = spec
        require((case.get("case_id"), case.get("outcome"), case.get("test_id"), case.get("fixture_pointer"), case.get("conformance_pointer")) == spec[:5], "G02", f"CASE_IDENTITY:{case_id}")
        require(case.get("expected_decision") == expected, "G02", f"CASE_EXPECTED:{case_id}")
        try:
            fixture_case = resolve_pointer(fixture, fixture_pointer)
            conformance_case = resolve_pointer(conformance, conformance_pointer)
        except (KeyError, IndexError, TypeError, ValueError):
            fixture_case = {}
            conformance_case = {}
        require(fixture_case.get("test_id") == test_id and fixture_case.get("expected") == expected, "G02", f"FIXTURE_PARITY:{case_id}")
        require(conformance_case.get("test_id") == test_id and conformance_case.get("expected_decision") == expected, "G02", f"CONFORMANCE_EXPECTED_PARITY:{case_id}")
        observed = conformance_case.get("static_reference_result", conformance_case.get("observed"))
        require(observed == expected, "G02", f"CONFORMANCE_OBSERVED_PARITY:{case_id}")
        require(case.get("execution_status") == conformance_case.get("execution_status") == "STATIC_REFERENCE_VALIDATOR_PASS", "G02", f"EXECUTION_STATUS:{case_id}")
        require(case.get("product_support") == conformance_case.get("product_support") == "NOT_RUN", "G02", f"PRODUCT_STATUS:{case_id}")
    require(contract.get("acceptance_bindings") == EXPECTED_BINDINGS, "G02", "ACCEPTANCE_BINDINGS_EXACT")

    # G03 — one controlling algorithm, four exact ranks and unchanged supporters.
    by_predicate: dict[str, list[dict[str, Any]]] = {}
    for row in predicates:
        by_predicate.setdefault(row.get("predicate_id"), []).append(row)
    require(len(by_predicate.get(OWNER_PREDICATE, [])) == 1, "G03", "OWNER_UNIQUE")
    owner = by_predicate.get(OWNER_PREDICATE, [{}])[0]
    expected_procedure = [
        "validate closed AssociatedRequirementDecisionInputR1",
        "rank 1: selected identity missing, duplicate, or kind-conflicting",
        "rank 2: bounds not admitted or default present under TC-R010",
        "rank 3: binding missing/ambiguous/wrong-kind; type=bounds subset, value=exact type, function=exact signature",
        "rank 4: cycle derived from normalized_dependency_requirement_ids",
        "select lowest rank then canonical culprit; otherwise admit",
    ]
    require(owner.get("input_descriptor") == "DiagnosticDispatchClosureInputR1", "G03", "OWNER_INPUT")
    require(owner.get("requires") == ["kind in {type,value,function}", "default_state=absent under TC-R010", "canonical binding/obligation identities"], "G03", "OWNER_REQUIREMENTS")
    require(owner.get("decision_procedure") == expected_procedure, "G03", "OWNER_ALGORITHM")
    require(owner.get("diagnostic_dispatch") == {reason: "ASSOCIATED_REQUIREMENT_UNRESOLVED" for reason in REASON_RANKS}, "G03", "OWNER_RANK_DIAGNOSTICS")
    require(owner.get("active_primary_diagnostic") == "ASSOCIATED_REQUIREMENT_UNRESOLVED" and owner.get("secondary_diagnostics") == [], "G03", "OWNER_PRIMARY_ONLY")
    require(owner.get("evidence_status") == "STATIC_REFERENCE_VALIDATOR_PASS" and owner.get("product_support") == "NOT_RUN", "G03", "OWNER_EVIDENCE_BOUNDARY")
    require(all(len(by_predicate.get(item, [])) == 1 for item in SUPPORTING_PREDICATES), "G03", "SUPPORTERS_EXIST_UNIQUELY")
    scope = contract.get("evidence_scope", {})
    require(scope.get("owner_predicate") == OWNER_PREDICATE and scope.get("supporting_predicates") == SUPPORTING_PREDICATES and scope.get("supporting_predicate_role") == "UNCHANGED_NONCONTROLLING", "G03", "SUPPORTERS_NONCONTROLLING")
    require(all(item not in json.dumps(overlay, sort_keys=True) for item in SUPPORTING_PREDICATES), "G03", "SUPPORTERS_NOT_OVERLAY_OWNERS")

    # G04 — R64 stops before HIR/MIR/runtime and leaves all selected-item use to R62.
    rules = {row.get("rule_id"): row.get("text") for row in contract.get("rules", [])}
    require(list(rules) == [f"ARPTC-R{index:03d}" for index in range(1, 9)], "G04", "RULE_IDS_EXACT_8")
    require("no source, AST, HIR, MIR, runtime operation" in rules.get("ARPTC-R007", ""), "G04", "STATIC_ONLY_RULE_R007")
    fence = contract.get("authority_fence", {})
    require(fence == {"classification": "STATIC_ADMISSION_ONLY", "admission_terminates_before_hir": True, "new_source_surface_count": 0, "new_ast_identity_count": 0, "new_hir_identity_count": 0, "new_mir_operation_kind_count": 0, "runtime_operation_count": 0, "later_use_owner_feature": "trait_qualified_associated_static_selection", "later_use_owner_revision": "R62", "later_use_scope": "PROJECTION_SELECTION_AND_EXISTING_STATIC_REFERENCE_OR_INVOKE_LOWERING", "later_use_imported_into_this_contract": False}, "G04", "AUTHORITY_FENCE_EXACT")
    require(r62_contract.get("feature_ids") == ["trait_qualified_associated_static_selection"], "G04", "R62_CONTRACT_OWNER")
    descriptor = r62_contract.get("descriptor_repair", {})
    require(descriptor.get("identity_kind") == "TraitAssociatedStaticSelectionId" and descriptor.get("required_field_count") == 7 and descriptor.get("runtime_reconstruction_count") == 0, "G04", "R62_DESCRIPTOR_FENCE")
    require(r62_overlay.get("feature_ids") == ["trait_qualified_associated_static_selection"] and len(r62_overlay.get("bindings", [])) == 1, "G04", "R62_OVERLAY_OWNER")
    bridge = hir_bridge.get("trait_associated_static_selection_bridge", {})
    require(bridge.get("descriptor") == "TraitAssociatedStaticSelection" and bridge.get("new_hir_node_identity_count") == 0 and bridge.get("new_mir_operation_kind_count") == 0 and bridge.get("runtime_reconstruction_count") == 0, "G04", "HIR_BRIDGE_EXISTING_OWNER")
    require(isinstance(_hir_fixture, dict) and isinstance(_hm_registry, dict), "G04", "EXISTING_MACHINE_ARTIFACTS_PARSE")

    # G05 — exact overlay and trace-record cardinalities.
    expected_evidence = [
        ("R64:associated_requirement_phase_a:DYNAMIC_LOWERING:STATIC_ONLY", "CONTRACT_RULE_ID", "REGISTRY_ID", "ARPTC-R007", "DYNAMIC_LOWERING"),
        ("R64:associated_requirement_phase_a:CONFORMANCE_TESTS:POSITIVE", "ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/POSITIVE", "CONFORMANCE_TESTS:POSITIVE"),
        ("R64:associated_requirement_phase_a:CONFORMANCE_TESTS:BOUNDARY", "ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/BOUNDARY", "CONFORMANCE_TESTS:BOUNDARY"),
        ("R64:associated_requirement_phase_a:CONFORMANCE_TESTS:REJECT", "ACCEPTANCE_CASE_SET", "JSON_POINTER", "/acceptance_bindings/REJECT", "CONFORMANCE_TESTS:REJECT"),
    ]
    require(overlay.get("feature_ids") == [FEATURE], "G05", "FEATURE_EXACT_ONE")
    entries = overlay.get("evidence_entries", [])
    require(len(entries) == 4, "G05", "EVIDENCE_ENTRY_COUNT_4")
    require([(row.get("evidence_key"), row.get("class"), row.get("locator_kind"), row.get("locator"), row.get("stage_role")) for row in entries] == expected_evidence, "G05", "EVIDENCE_ENTRIES_EXACT")
    require(all(row.get("path") == CONTRACT_REL for row in entries), "G05", "EVIDENCE_CONTRACT_PATH")
    require(len(overlay.get("bindings", [])) == 4, "G05", "BINDING_COUNT_4")
    trace_records = overlay.get("acceptance_cases", [])
    require([row.get("case_id") for row in trace_records] == [f"R64-TRACE-{index:03d}" for index in range(1, 5)], "G05", "TRACE_RECORDS_EXACT_4")
    require(overlay.get("counts", {}).get("feature_count") == 1 and overlay.get("counts", {}).get("evidence_entry_count") == 4 and overlay.get("counts", {}).get("binding_count") == 4, "G05", "OVERLAY_COUNTS_1_4_4")

    # G06 — exact static-only NOT_APPLICABLE reason and authority.
    bindings = overlay.get("bindings", [])
    dynamic = next((row for row in bindings if row.get("stage") == "DYNAMIC_LOWERING"), {})
    dynamic_key = "R64:associated_requirement_phase_a:DYNAMIC_LOWERING:STATIC_ONLY"
    expected_na = {
        "reason_code": "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR",
        "authority_boundary": "MIR_RUNTIME_AUTHORITY",
        "rationale": "Associated-requirement admission terminates before MIR and creates no runtime artifact; admitted value and function use-site selection remains owned by trait_qualified_associated_static_selection.",
        "justification_evidence_keys": [dynamic_key],
    }
    require(dynamic == {"feature_id": FEATURE, "stage": "DYNAMIC_LOWERING", "outcome": None, "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "NOT_APPLICABLE", "evidence_keys": [dynamic_key], "delegate_feature_id": None, "not_applicable": expected_na}, "G06", "DYNAMIC_NOT_APPLICABLE_EXACT")

    # G07 — every conformance outcome is directly bound to its exact case set.
    test_bindings = [row for row in bindings if row.get("stage") == "CONFORMANCE_TESTS"]
    require([row.get("outcome") for row in test_bindings] == ["POSITIVE", "BOUNDARY", "REJECT"], "G07", "TEST_OUTCOMES_EXACT")
    require(all(row.get("disposition") == "BOUND_DIRECT" and row.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP" and row.get("delegate_feature_id") is None and row.get("not_applicable") is None for row in test_bindings), "G07", "TEST_BINDINGS_DIRECT")
    trace_by_outcome = {row.get("outcome"): row for row in trace_records if row.get("outcome") is not None}
    for outcome, case_ids in EXPECTED_BINDINGS.items():
        row = trace_by_outcome.get(outcome, {})
        require(row.get("contract_pointer") == f"/acceptance_bindings/{outcome}" and row.get("acceptance_case_ids") == case_ids and row.get("disposition") == "BOUND_DIRECT" and row.get("execution_state") == "STATIC_REFERENCE_VALIDATOR_PASS", "G07", f"TEST_CASE_SET:{outcome}")

    # G08 — four exact target cells; all other 4,217 ledger dispositions match HEAD.
    cells, duplicate_count = trace_cells(rows)
    require(len(rows) == 469 and len(cells) == 4221 and duplicate_count == 0, "G08", "TRACE_LEDGER_EXACT_469_4221")
    for identity, disposition in TARGETS.items():
        require(cells.get(identity, {}).get("disposition") == disposition, "G08", f"TARGET:{identity[1]}:{identity[2]}")
    non_target_count, non_target_digest = non_target_disposition_digest(cells)
    require(non_target_count == NON_TARGET_CELL_COUNT, "G08", "NON_TARGET_COUNT_4217")
    require(non_target_digest == NON_TARGET_DISPOSITION_SHA256, "G08", "NON_TARGET_HEAD_SEMANTIC_MAP")

    # G09 — exact projected totals and evidence-registry pre+4 accounting.
    derived = metadata.get("derived_counts", {})
    require((derived.get("bound_direct_cells"), derived.get("bound_delegated_cells"), derived.get("not_applicable_cells"), derived.get("applicable_blocked_cells")) == (2461, 3, 503, 1254), "G09", "DISPOSITION_COUNTS_EXACT")
    applied = metadata.get("applied_evidence_overlays", [])
    require(len(applied) == 10 and sum(row.get("binding_count", 0) for row in applied) == 125, "G09", "OVERLAYS_10_BINDINGS_125")
    require(applied[-1] == {"path": OVERLAY_REL, "feature_count": 1, "binding_count": 4}, "G09", "R64_OVERLAY_METADATA_LAST")
    registry = metadata.get("evidence_registry", [])
    registry_ids = {row.get("evidence_id") for row in registry}
    expected_ids = {evidence_id(row) for row in entries}
    require(len(registry) == 3138 and 3138 == 3134 + 4, "G09", "EVIDENCE_REGISTRY_PRE_PLUS_4")
    require(expected_ids <= registry_ids and len(expected_ids) == 4, "G09", "R64_EVIDENCE_IDS_REGISTERED")
    counts = overlay.get("counts", {})
    require((counts.get("post_overlay_total_bound_direct_cell_count"), counts.get("post_overlay_total_bound_delegated_cell_count"), counts.get("post_overlay_total_not_applicable_cell_count"), counts.get("post_overlay_total_blocked_cell_count")) == (2461, 3, 503, 1254), "G09", "OVERLAY_POST_COUNTS")
    require(counts.get("predecessor_cumulative_overlay_binding_count") == 121 and counts.get("post_overlay_cumulative_binding_count") == 125, "G09", "OVERLAY_BINDING_DELTA_121_TO_125")

    # G10 — protected R9, R62 and HIR/MIR bytes remain exactly at the fixed HEAD map.
    for relative, expected_hash in PROTECTED_HEAD_SHA256.items():
        path = root / relative
        require(path.is_file(), "G10", f"PROTECTED_PATH:{relative}")
        if path.is_file():
            require(file_sha256(path) == expected_hash, "G10", f"PROTECTED_HASH:{relative}")

    # G11 — design evidence remains honest about P0/P1/actions/product/GitHub.
    machine = contract.get("machine_acceptance", {})
    governance = contract.get("governance", {})
    guards = overlay.get("guards", {})
    metadata_governance = metadata.get("governance", {})
    require(machine.get("semantic_p0") == governance.get("semantic_p0") == guards.get("semantic_p0") == metadata_governance.get("semantic_p0") == 0, "G11", "SEMANTIC_P0_ZERO")
    require(machine.get("feature_p1") == governance.get("feature_p1") == guards.get("feature_p1") == metadata_governance.get("feature_p1") == "22_OPEN_UNCHANGED", "G11", "FEATURE_P1_22_OPEN")
    require(machine.get("m13_actions") == governance.get("m13_actions") == guards.get("m13_actions") == metadata_governance.get("m13_actions") == "4_OPEN_UNCHANGED", "G11", "M13_4_OPEN")
    require(machine.get("product_lanes") == governance.get("product_lanes") == guards.get("product_lanes") == metadata_governance.get("product_lanes") == "15_OF_15_NOT_RUN", "G11", "PRODUCT_15_NOT_RUN")
    require(machine.get("github_publication") == governance.get("github_publication") == guards.get("github_publication") == metadata_governance.get("github_publication") == "SUSPENDED", "G11", "GITHUB_SUSPENDED")
    require(guards.get("product_execution_receipt_count") == 0 and guards.get("implementation_claim") == "NONE" and governance.get("implementation_claim") == "NONE", "G11", "NO_EXECUTION_OR_IMPLEMENTATION_CLAIM")
    require(derived.get("product_not_run_rows") == 469, "G11", "ALL_TARGET_ROWS_NOT_RUN")

    # G12 — bounded follow-up is recorded and all files are ready for workspace registration.
    require("IR-TRACE-P1-056" in decision_text, "G12", "FOLLOW_UP_ID")
    require("AST_FRONTEND" in decision_text and "DIAGNOSTICS" in decision_text and "explicitly outside R64" in decision_text, "G12", "FOLLOW_UP_BOUNDARY")
    require(all((root / relative).is_file() for relative in WORKSPACE_REGISTRATION_PATHS), "G12", "REGISTRATION_PATHS_EXIST")
    require((root / WORKSPACE_VALIDATOR_REL).is_file(), "G12", "WORKSPACE_VALIDATOR_EXISTS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    gate_receipts = []
    for gate_id, name in GATE_NAMES.items():
        gate_errors = [item for item in errors if item.startswith(f"{gate_id}:")]
        gate_receipts.append({"gate_id": gate_id, "name": name, "result": "PASS" if not gate_errors else "FAIL", "errors": gate_errors})
    passed = sum(row["result"] == "PASS" for row in gate_receipts)
    receipt = {
        "schema": "deeplus.associated-requirement-phase-a-trace-validation-receipt/r1",
        "revision": REVISION,
        "canonical_baseline_commit": CANONICAL,
        "local_predecessor_commit": PREDECESSOR,
        "result": "PASS" if not errors else "FAIL",
        "gate_count": 12,
        "passed_gate_count": passed,
        "gate_summary": f"{passed}/12",
        "feature_id": FEATURE,
        "transitioned_cell_count": 4,
        "unchanged_non_target_cell_count": NON_TARGET_CELL_COUNT,
        "acceptance_case_count": 8,
        "acceptance_case_classes": {"POSITIVE": 2, "BOUNDARY": 1, "REJECT": 5},
        "projected_counts": {"bound_direct": 2461, "bound_delegated": 3, "not_applicable": 503, "applicable_blocked": 1254},
        "evidence_overlay_count": 10,
        "evidence_overlay_binding_count": 125,
        "evidence_registry_count": 3138,
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "workspace_registration_ready_paths": WORKSPACE_REGISTRATION_PATHS,
        "gates": gate_receipts,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
