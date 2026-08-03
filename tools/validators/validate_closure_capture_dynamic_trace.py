#!/usr/bin/env python3
"""Validate the bounded R67 closure-capture semantic repair and trace closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


DECISION_REL = "decisions/language/Design_Deeplus_R67_Closure_Capture_Dynamic_Trace_Closure_R1.md"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/closure-capture-dynamic-trace-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/closure-capture-dynamic-trace-evidence-r1.schema.json"
CONTRACT_REL = "spec/contracts/closure-capture-plan-r1.json"
INPUT_SCHEMA_REL = "schemas/language/closure-capture-plan-input-r1.schema.json"
FIXTURE_REL = "tests/fixtures/current/closure-capture-plan-r1.json"
HIR_REL = "schemas/language/canonical-hir-h1.schema.json"
MIR_REL = "schemas/language/deeplus-mir.schema.json"
IDENTITY_CATALOG_REL = "spec/contracts/hir-h1-identity-catalog.json"
BRIDGE_REL = "spec/contracts/hir-h1-current-mir-bridge.json"
LOWERING_REL = "spec/contracts/hir-mir-lowering-registry.json"
MACHINE_REL = "spec/contracts/mir-machine-registry.json"
MIR_SEMANTICS_REL = "spec/mir/semantics.md"
RESPONSIBILITY_REL = "spec/contracts/responsibility-identity-registry-r1.json"
ROWS_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
VALIDATOR_REL = "tools/validators/validate_closure_capture_dynamic_trace.py"
MUTATION_REL = "tools/validators/run_closure_capture_dynamic_trace_mutation_tests.py"

CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "a1fc8b99db7e7392fa17ea78880d02239ffc5d1e"
REVISION = "r67-local-closure-capture-dynamic-trace-closure-r1"
FEATURE = "closure_capture_descriptor_msp"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
EVIDENCE_KEY = "R67:closure_capture_descriptor_msp:DYNAMIC_LOWERING:TRANSACTION"
NON_TARGET_SHA256 = "cd52a1d81105c67d0033687047f1d819f165aac964fc88b414544474e50c2bcb"
CURRENT_MODES = ["BORROW", "INOUT", "MOVE", "COPY", "CLONE", "ONCE"]

PROTECTED = {
    RESPONSIBILITY_REL: "533767a103487ecd96f62a77cc37173fc80cc18dbb6bd0b98caecbe0a8a2d7cf",
    "schemas/language/responsibility-identity-registry-r1.schema.json": "6ede17e8098bc9d7b5208bcfc74239737536e66ec2162186cf4fa70224d61e45",
    "tests/fixtures/current/responsibility-identity-registry-r1.json": "b630cae0cb1aaa575a830056f8595b42c5b786616f0d0f24d01b1d45a8240f2f",
    "spec/features/catalog/chunks/part-0003.json": "d613c58edf3663b3bb0b6d10b0337edeb778b4184b2d5117b4d25a5f75a3d8ce",
    "spec/traceability/implementation-target-profile-r1/responsibility-identity-dynamic-trace-evidence-r1.json": "efad60cc533c1484f7b11c5635becce869d7fdfa7e42128b0920c4e06723f687",
    "schemas/language/responsibility-identity-dynamic-trace-evidence-r1.schema.json": "675b0e0e3d7425fb1dd9ec45832d4acb0fec63115226b18cc512e75092db8871",
    "decisions/language/Design_Deeplus_R66_Responsibility_Identity_Dynamic_Trace_Closure_R1.md": "af533d947004e2cd369722c20432fcca95e9e3db07995736da3328ad7ecb8a4f",
}

GATES = {
    "G01": "identity_scope_and_predecessor",
    "G02": "move_reservation_and_commit_barrier",
    "G03": "capture_evidence_domain_admission",
    "G04": "canonical_hir_capture_projection",
    "G05": "canonical_mir_capture_projection",
    "G06": "lowering_bridge_machine_and_deep_zero",
    "G07": "acceptance_fixture_and_private_residue",
    "G08": "exact_direct_overlay",
    "G09": "generated_trace_counts_and_non_target_fence",
    "G10": "schema_governance_and_upstream_byte_fences",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_id(entry: dict[str, Any]) -> str:
    material = "\0".join(
        [entry["class"], entry["path"], entry["locator_kind"], entry["locator"], entry["stage_role"]]
    )
    return "EV-" + hashlib.sha256(material.encode()).hexdigest()


def trace_cells(rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, str, str | None], dict[str, Any]], int]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        for stage in row.get("stages", []):
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage.get("stage") == "CONFORMANCE_TESTS" else None
                key = (row.get("feature_id"), stage.get("stage"), outcome)
                duplicates += key in cells
                cells[key] = cell
    return cells, duplicates


def non_target_digest(cells: dict[tuple[str, str, str | None], dict[str, Any]]) -> tuple[int, str]:
    material = [[*key, value] for key, value in cells.items() if key != TARGET]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return len(material), hashlib.sha256(encoded).hexdigest()


def mode_conditional(schema: dict[str, Any], mode: str) -> dict[str, Any]:
    for clause in schema.get("allOf", []):
        condition = clause.get("if", {}).get("properties", {}).get("normalized_mode", {})
        if condition.get("const") == mode:
            return clause.get("then", {}).get("properties", {})
    return {}


def validate(
    root: Path,
    *,
    overlay_override: dict[str, Any] | None = None,
    contract_override: dict[str, Any] | None = None,
    input_schema_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
    hir_override: dict[str, Any] | None = None,
    mir_override: dict[str, Any] | None = None,
    identity_catalog_override: dict[str, Any] | None = None,
    bridge_override: dict[str, Any] | None = None,
    lowering_override: dict[str, Any] | None = None,
    machine_override: dict[str, Any] | None = None,
    responsibility_override: dict[str, Any] | None = None,
    rows_override: list[dict[str, Any]] | None = None,
    metadata_override: dict[str, Any] | None = None,
    decision_text_override: str | None = None,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    overlay = overlay_override if overlay_override is not None else load(root / OVERLAY_REL)
    contract = contract_override if contract_override is not None else load(root / CONTRACT_REL)
    input_schema = input_schema_override if input_schema_override is not None else load(root / INPUT_SCHEMA_REL)
    fixture = fixture_override if fixture_override is not None else load(root / FIXTURE_REL)
    hir = hir_override if hir_override is not None else load(root / HIR_REL)
    mir = mir_override if mir_override is not None else load(root / MIR_REL)
    identity_catalog = identity_catalog_override if identity_catalog_override is not None else load(root / IDENTITY_CATALOG_REL)
    bridge = bridge_override if bridge_override is not None else load(root / BRIDGE_REL)
    lowering = lowering_override if lowering_override is not None else load(root / LOWERING_REL)
    machine = machine_override if machine_override is not None else load(root / MACHINE_REL)
    responsibility = responsibility_override if responsibility_override is not None else load(root / RESPONSIBILITY_REL)
    rows = rows_override if rows_override is not None else load(root / ROWS_REL)
    metadata = metadata_override if metadata_override is not None else load(root / META_REL)
    decision = decision_text_override if decision_text_override is not None else (root / DECISION_REL).read_text(encoding="utf-8")

    # G01: exact local identity and one dependency-local target.
    require(overlay.get("revision") == REVISION, "G01", "REVISION")
    require(overlay.get("canonical_baseline_commit") == CANONICAL, "G01", "CANONICAL")
    require(overlay.get("local_predecessor_commit") == PREDECESSOR, "G01", "PREDECESSOR")
    require(overlay.get("feature_ids") == [FEATURE], "G01", "FEATURE_SCOPE")
    require(all(token in decision for token in (CANONICAL, PREDECESSOR, "IR-XCUT-P1-054", "exactly one")), "G01", "DECISION_IDENTITY")

    # G02: MOVE/ONCE reserve before a closed infallible commit interval.
    algorithm = contract.get("algorithm", {})
    failure = algorithm.get("failure_atomicity", {})
    tail = algorithm.get("infallible_commit_tail", {})
    require("reserve move only" in algorithm.get("mode_preparation", {}).get("MOVE", ""), "G02", "MOVE_RESERVE_ONLY")
    require("reserve move only" in algorithm.get("mode_preparation", {}).get("ONCE", ""), "G02", "ONCE_RESERVE_ONLY")
    require(failure.get("source_owner_consumed_before_commit_tail_count") == 0, "G02", "SOURCE_LIVE_BEFORE_TAIL")
    require(failure.get("place_move_before_all_fallible_preparations_complete_count") == 0, "G02", "NO_EARLY_PLACE_MOVE")
    require(failure.get("move_reservation_cancelled") is True and failure.get("rollback_order") == "strict reverse acquisition order", "G02", "FAILURE_ROLLBACK")
    require(tail.get("starts_after_all_fallible_preparations") is True, "G02", "BARRIER")
    require(tail.get("reserved_modes") == ["MOVE", "ONCE"], "G02", "RESERVED_MODES")
    require(tail.get("per_reserved_capture_in_source_order") == ["PLACE_MOVE", "BUILDER_STAGE"], "G02", "TAIL_MOVE_STAGE_ORDER")
    require(tail.get("fallible_step_count") == 0 and tail.get("then") == ["BUILDER_COMMIT", "CLOSURE_MAKE"], "G02", "INFALLIBLE_TAIL")

    # G03: checker input preserves CopyValue and Clone evidence domains.
    item = input_schema.get("$defs", {}).get("captureItem", {})
    input_modes = item.get("properties", {}).get("normalized_mode", {}).get("enum", [])
    copy_props = mode_conditional(item, "COPY")
    clone_props = mode_conditional(item, "CLONE")
    require("DEEP" in input_modes, "G03", "SOURCE_DEEP_REJECTION_INPUT_RETAINED")
    require(copy_props.get("responsibility_rule_id_or_null", {}).get("const") == "CopyValue", "G03", "COPY_RULE")
    require(copy_props.get("responsibility_evidence_id_or_null", {}).get("type") == "string", "G03", "COPY_EVIDENCE_REQUIRED")
    require(copy_props.get("trait_witness_id_or_null", {}).get("type") == "null", "G03", "COPY_WITNESS_NULL")
    require(clone_props.get("responsibility_rule_id_or_null", {}).get("const") == "Clone", "G03", "CLONE_RULE")
    require(clone_props.get("responsibility_evidence_id_or_null", {}).get("type") == "string", "G03", "CLONE_EVIDENCE_REQUIRED")
    require(clone_props.get("trait_witness_id_or_null", {}).get("type") == "string", "G03", "CLONE_WITNESS_REQUIRED")
    identity_rows = {row.get("identity_id"): row for row in responsibility.get("identities", [])}
    require(identity_rows.get("CopyValue", {}).get("evidence_mode") == "INTRINSIC_PREDICATE_PROOF", "G03", "COPY_DESCRIPTOR_DOMAIN")
    require(identity_rows.get("Clone", {}).get("evidence_mode") == "EXACT_SELECTED_TRAIT_WITNESS" and identity_rows.get("Clone", {}).get("trait_id_required") is True, "G03", "CLONE_DESCRIPTOR_OWNS_WITNESS")
    require(identity_rows.get("DeepClone", {}).get("availability") == "RESERVED_PREVIEW_NONACTIVATABLE", "G03", "DEEP_IDENTITY_RESERVED")

    # G04: canonical HIR admits six current modes and keeps callable/evidence IDs disjoint.
    href = hir.get("$defs", {}).get("ReferenceCapture", {})
    hprops = href.get("properties", {})
    require(hprops.get("mode", {}).get("enum") == CURRENT_MODES, "G04", "HIR_CURRENT_MODES")
    require("responsibility_evidence_id_or_null" in href.get("required", []) and "responsibility_profile_id" in href.get("required", []), "G04", "HIR_REQUIRED_IDS")
    require(hprops.get("responsibility_evidence_id_or_null", {}).get("x-deeplus-identity-domain") == "RESPONSIBILITY_EVIDENCE_ID_OR_NULL", "G04", "HIR_EVIDENCE_DOMAIN")
    require(hprops.get("responsibility_profile_id", {}).get("x-deeplus-identity-domain") == "RESPONSIBILITY_PROFILE_ID", "G04", "HIR_PROFILE_DOMAIN")
    hif = href.get("allOf", [{}])[0]
    require(hif.get("if", {}).get("properties", {}).get("mode", {}).get("enum") == ["COPY", "CLONE"], "G04", "HIR_COPY_CLONE_IFF")
    require("ResponsibilityEvidenceId" in hprops.get("responsibility_evidence_id_or_null", {}).get("description", "") and "ResponsibilityProfileId" in hprops.get("responsibility_evidence_id_or_null", {}).get("description", ""), "G04", "HIR_DOMAIN_TEXT")
    catalog_text = json.dumps(identity_catalog, ensure_ascii=False)
    require("responsibility_evidence_id_or_null" in catalog_text and "N1_IFF_MODE_COPY_OR_CLONE" in catalog_text, "G04", "HIR_IDENTITY_CATALOG")

    # G05: MIR preserves the same exact evidence identity and separation.
    mref = mir.get("$defs", {}).get("closureReferenceCaptureField", {})
    mprops = mref.get("properties", {})
    require(mprops.get("capture_mode", {}).get("enum") == CURRENT_MODES, "G05", "MIR_CURRENT_MODES")
    require("responsibility_evidence_id_or_null" in mref.get("required", []) and "responsibility_profile_id" in mref.get("required", []), "G05", "MIR_REQUIRED_IDS")
    require(mprops.get("responsibility_evidence_id_or_null", {}).get("x-deeplus-identity-domain") == "RESPONSIBILITY_EVIDENCE_ID_OR_NULL", "G05", "MIR_EVIDENCE_DOMAIN")
    require(mprops.get("responsibility_profile_id", {}).get("x-deeplus-identity-domain") == "RESPONSIBILITY_PROFILE_ID", "G05", "MIR_PROFILE_DOMAIN")
    mif = mref.get("allOf", [{}])[0]
    require(mif.get("if", {}).get("properties", {}).get("capture_mode", {}).get("enum") == ["COPY", "CLONE"], "G05", "MIR_COPY_CLONE_IFF")
    descriptor = mir.get("$defs", {}).get("responsibilityEvidenceDescriptor", {})
    require(all(field in descriptor.get("required", []) for field in ("responsibility_rule_id", "responsibility_evidence_id", "evidence_kind", "trait_witness_id_or_null")), "G05", "MIR_DESCRIPTOR_OWNS_RULE_AND_WITNESS")

    # G06: bridge, lowering and machine agree on barrier, evidence and DEEP zero.
    bcontract = bridge.get("closure_capture_plan_contract", {})
    bcapture = bcontract.get("capture_sum", {})
    bprojection = bcontract.get("mir_projection", {})
    btransaction = bcontract.get("transaction", {})
    lcontract = lowering.get("closure_capture_plan_lowering_contract", {})
    lprojection = lcontract.get("capture_projection", {})
    expansion = lcontract.get("source_order_expansion", {})
    publish = lcontract.get("commit_and_publish", {})
    mcontract = machine.get("closure_environment_plan_contract", {})
    mcapture = mcontract.get("capture_sum", {})
    mtransaction = mcontract.get("transactional_lowering", {})
    require("responsibility_evidence_id_or_null" in bcapture.get("reference_required_fields", []), "G06", "BRIDGE_EVIDENCE_FIELD")
    require(bprojection.get("deep_typed_hir_or_mir_row_count") == 0 and lprojection.get("deep_typed_hir_or_mir_row_count") == 0 and mcapture.get("deep_typed_hir_or_mir_row_count") == 0, "G06", "DEEP_ZERO")
    require(bprojection.get("responsibility_evidence_projection") == lprojection.get("responsibility_evidence_id_or_null"), "G06", "BRIDGE_LOWERING_EVIDENCE")
    require("never substitutes" in lprojection.get("callable_profile_separation", "") and "never substitutes" in bprojection.get("callable_profile_separation", ""), "G06", "PROFILE_SEPARATION")
    require(expansion.get("reference_move_or_once_preparation") == ["MOVE_RESERVE", "NO_PLACE_MOVE_OR_BUILDER_STAGE_BEFORE_FINAL_INTERVAL"], "G06", "LOWERING_RESERVE_ONLY")
    require(publish.get("fallible_preparation_boundary") == "ALL_FALLIBLE_PREPARATION_SUCCEEDS_BEFORE_FIRST_PLACE_MOVE", "G06", "LOWERING_BARRIER")
    require(publish.get("final_infallible_commit_interval") == ["SOURCE_ORDER_PLACE_MOVE_THEN_BUILDER_STAGE_FOR_EACH_MOVE_OR_ONCE_RESERVATION", "BUILDER_COMMIT_AFTER_ALL_CAPTURE_FIELDS", "INFALLIBLE_CLOSURE_MAKE"], "G06", "LOWERING_FINAL_INTERVAL")
    require(publish.get("final_interval_failure_edge_count") == publish.get("final_interval_suspend_or_branch_count") == 0, "G06", "LOWERING_INTERVAL_CLOSED")
    require(lcontract.get("new_mir_operation_kind_count") == 0 and mtransaction.get("new_operation_kind_count") == 0, "G06", "NO_NEW_MIR_OP")
    require(machine.get("status_fence", {}).get("closure_capture_deep_typed_hir_or_mir_row_count") == 0, "G06", "MACHINE_DEEP_FENCE")
    require(btransaction.get("final_interval_failure_edge_count") == btransaction.get("final_interval_suspend_or_branch_count") == 0, "G06", "BRIDGE_INTERVAL_CLOSED")
    mir_semantics = (root / MIR_SEMANTICS_REL).read_text(encoding="utf-8")
    require("infallible final interval" in mir_semantics and "ResponsibilityEvidenceId" in mir_semantics, "G06", "MIR_SEMANTICS_BOUND")

    # G07: acceptance rows state the exact boundary and rejection contracts.
    cases = {row.get("case_id"): row for row in fixture.get("cases", [])}
    move_case = cases.get("R31-CCP-BND-002", {}).get("assertions", {})
    copy_case = cases.get("R31-CCP-POS-003", {}).get("assertions", {})
    clone_case = cases.get("R31-CCP-POS-004", {}).get("assertions", {})
    deep_case = cases.get("R31-CCP-NEG-001", {})
    require(move_case.get("source_consumed_before_commit") is False and move_case.get("place_move_before_all_fallible_preparations_complete_count") == 0 and move_case.get("move_reservation_cancelled") is True, "G07", "MOVE_BOUNDARY_CASE")
    require(copy_case.get("responsibility_rule_id") == "CopyValue" and copy_case.get("trait_witness_id_or_null") is None, "G07", "COPY_CASE")
    require(clone_case.get("responsibility_rule_id") == "Clone" and clone_case.get("responsibility_evidence_id_required") is True and clone_case.get("trait_witness_id_required_in_descriptor") is True, "G07", "CLONE_CASE")
    require(deep_case.get("expected_outcome") == "REJECT" and deep_case.get("expected_diagnostic_or_null") == "FEATURE_NOT_ACTIVATABLE_IN_CURRENT_PROFILE" and deep_case.get("assertions", {}).get("typed_hir_residue_count") == deep_case.get("assertions", {}).get("typed_mir_residue_count") == 0, "G07", "DEEP_REJECT_CASE")
    require(bcontract.get("api_fence", {}).get("value_level_identity_export_count") == 0 and "ResponsibilityEvidenceId" in bcontract.get("api_fence", {}).get("forbidden", []), "G07", "PRIVATE_EVIDENCE_RESIDUE")

    # G08: exactly one direct nondelegated overlay binding and one evidence entry.
    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    entry = entries[0] if len(entries) == 1 else {}
    binding = bindings[0] if len(bindings) == 1 else {}
    require(len(entries) == len(bindings) == len(overlay.get("acceptance_cases", [])) == 1, "G08", "ONE_ONE_ONE")
    require(entry == {"evidence_key": EVIDENCE_KEY, "class": "ARTIFACT_POINTER", "path": LOWERING_REL, "locator_kind": "JSON_POINTER", "locator": "/closure_capture_plan_lowering_contract", "stage_role": "DYNAMIC_LOWERING"}, "G08", "ENTRY_EXACT")
    require(binding.get("feature_id") == FEATURE and binding.get("stage") == "DYNAMIC_LOWERING" and binding.get("outcome") is None, "G08", "TARGET_EXACT")
    require(binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP" and binding.get("disposition") == "BOUND_DIRECT", "G08", "BLOCKED_TO_DIRECT")
    require(binding.get("evidence_keys") == [EVIDENCE_KEY] and binding.get("delegate_feature_id") is None and binding.get("not_applicable") is None, "G08", "DIRECT_ONLY")

    # G09: generated ledger changes exactly the target cell.
    cells, duplicates = trace_cells(rows)
    target = cells.get(TARGET, {})
    expected_ref = evidence_id(entry) if entry else ""
    count, digest = non_target_digest(cells)
    derived = metadata.get("derived_counts", {})
    overlays = metadata.get("applied_evidence_overlays", [])
    require(len(rows) == 469 and len(cells) == 4221 and duplicates == 0, "G09", "LEDGER_SHAPE")
    require(target == {"stage": "DYNAMIC_LOWERING", "disposition": "BOUND_DIRECT", "evidence_refs": [expected_ref], "delegate_feature_id": None, "not_applicable": None, "blocked_gap_ids": []}, "G09", "TARGET_GENERATED_EXACT")
    require(count == 4220 and digest == NON_TARGET_SHA256, "G09", "OTHER_4220_EXACT")
    require((derived.get("bound_direct_cells"), derived.get("bound_delegated_cells"), derived.get("not_applicable_cells"), derived.get("applicable_blocked_cells")) == (2465, 3, 501, 1252), "G09", "COUNTS")
    require(len(overlays) == 13 and sum(row.get("binding_count", 0) for row in overlays) == 129 and len(metadata.get("evidence_registry", [])) == 3142, "G09", "OVERLAY_COUNTS")

    # G10: exact schema, governance and unchanged R66 provider authority.
    schema = load(root / OVERLAY_SCHEMA_REL)
    const_keys = ("$schema", "schema", "revision", "canonical_baseline_commit", "local_predecessor_commit", "candidate_status", "feature_ids", "evidence_entries", "bindings", "acceptance_cases", "counts", "guards")
    require(all(schema.get("properties", {}).get(key, {}).get("const") == overlay.get(key) for key in const_keys), "G10", "SCHEMA_EXACT")
    require(all((root / path).is_file() for path in (DECISION_REL, OVERLAY_REL, OVERLAY_SCHEMA_REL, VALIDATOR_REL, MUTATION_REL)), "G10", "PATHS")
    guards = overlay.get("guards", {})
    governance = metadata.get("governance", {})
    require(guards.get("semantic_p0") == governance.get("semantic_p0") == 0 and guards.get("feature_p1") == governance.get("feature_p1") == "22_OPEN_UNCHANGED", "G10", "P0_P1")
    require(guards.get("product_lanes") == governance.get("product_lanes") == "15_OF_15_NOT_RUN" and guards.get("github_publication") == governance.get("github_publication") == "SUSPENDED", "G10", "PRODUCT_GITHUB")
    require(all(guards.get(key) == 0 for key in ("move_source_consumed_before_commit_count", "move_barrier_fallible_operation_count", "move_barrier_suspension_point_count", "capture_responsibility_domain_mismatch_count", "callable_profile_as_capture_evidence_count", "current_deep_hir_mode_count", "current_deep_mir_mode_count", "current_deep_lowering_row_count", "current_deep_lowering_operation_count", "new_mir_operation_kind_count", "runtime_relookup_count", "backend_relookup_count", "product_execution_receipt_count")), "G10", "ZERO_FENCES")
    for relative, expected in PROTECTED.items():
        if not (relative == RESPONSIBILITY_REL and responsibility_override is not None):
            require(sha256(root / relative) == expected, "G10", f"HASH:{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    gates = []
    for gate_id, name in GATES.items():
        gate_errors = [item for item in errors if item.startswith(f"{gate_id}:")]
        gates.append({"gate_id": gate_id, "name": name, "result": "PASS" if not gate_errors else "FAIL", "errors": gate_errors})
    passed = sum(row["result"] == "PASS" for row in gates)
    receipt = {
        "schema": "deeplus.closure-capture-dynamic-trace-validation-receipt/r1",
        "revision": REVISION,
        "canonical_baseline_commit": CANONICAL,
        "local_predecessor_commit": PREDECESSOR,
        "result": "PASS" if not errors else "FAIL",
        "gate_count": len(GATES),
        "passed_gate_count": passed,
        "gate_summary": f"{passed}/{len(GATES)}",
        "feature_id": FEATURE,
        "transitioned_cell_count": 1,
        "unchanged_non_target_cell_count": 4220,
        "projected_counts": {"bound_direct": 2465, "bound_delegated": 3, "not_applicable": 501, "applicable_blocked": 1252},
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "gates": gates,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
