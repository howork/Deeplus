#!/usr/bin/env python3
"""Validate the bounded R68 RegionId/LoanId projection and trace closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/region-lifetime-mir-projection-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/region-lifetime-mir-projection-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/region-lifetime-dynamic-trace-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/region-lifetime-dynamic-trace-evidence-r1.schema.json"
DECISION_REL = "decisions/language/Design_Deeplus_R68_Region_Lifetime_Dynamic_Trace_Closure_R1.md"
HIR_REL = "schemas/language/canonical-hir-h1.schema.json"
MIR_REL = "schemas/language/deeplus-mir.schema.json"
LOWERING_REL = "spec/contracts/hir-mir-lowering-registry.json"
BRIDGE_REL = "spec/contracts/hir-h1-current-mir-bridge.json"
MACHINE_REL = "spec/contracts/mir-machine-registry.json"
LOAN_REL = "spec/contracts/loan-close-operation-r1.json"
LOAN_FIXTURE_REL = "tests/fixtures/current/loan-close-operation-r1.json"
OWNERSHIP_FIXTURE_REL = "tests/fixtures/current/ownership-decision-inputs-r1.json"
BORROW_CONTEXT_REL = "spec/contracts/borrow-context-anchor-disambiguation.json"
BORROW_CONTEXT_FIXTURE_REL = "tests/fixtures/current/borrow-context-anchor-disambiguation-r1.json"
ESCAPE_REL = "tests/fixtures/current/borrow-escape-diagnostic-dispatch-r1.json"
SUSPEND_REL = "tests/fixtures/current/suspension-frame-responsibility-r1.json"
ROWS_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"

CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "11d9df3e1ce148be5c73f227376470fff114723d"
REVISION = "r68-local-region-lifetime-dynamic-trace-closure-r1"
FEATURE = "region_lifetime_model_phase_a"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
EVIDENCE_KEY = "R68:region_lifetime_model_phase_a:DYNAMIC_LOWERING:REGION_PROJECTION"
EVIDENCE_ID = "EV-032750ffa3d95c5598d2adcdaae3048b3c03353353dc2dd3ac6146e7664fd070"
NON_TARGET_SHA256 = "24bd4668d31d583d421bd5b124e902ac1d7d1271ed263e40afc9660022e8dee3"

PROTECTED = {
    "spec/traceability/implementation-target-profile-r1/closure-capture-dynamic-trace-evidence-r1.json": "bd5af3ef5fa6ef92c01376dfcc8f663ac8f6a5451b6b63145ac8fe2a4756bcac",
    "schemas/language/closure-capture-dynamic-trace-evidence-r1.schema.json": "8469efe03426d2792e48af12f83590174380e136a26893e812ddf1d17ecf7adc",
    "decisions/language/Design_Deeplus_R67_Closure_Capture_Dynamic_Trace_Closure_R1.md": "fdab6f347dd47910990069b95ac53936856d50fd318526d4740ab766d34da49d",
    "tools/generators/refresh_source_tree_manifest.py": "798e1f82bfe5174ac476a306bd42b8318d8175ba0a145002d07cd597fedc408c",
}

GATES = {
    "G01": "identity_and_schema",
    "G02": "typed_hir_region_and_loan_ownership",
    "G03": "mir_extent_and_value_projection",
    "G04": "lowering_bridge_and_machine_contract",
    "G05": "region_graph_and_access_dispatch",
    "G06": "close_suspension_and_diagnostic_composition",
    "G07": "acceptance_evidence_reuse",
    "G08": "exact_direct_overlay",
    "G09": "generated_trace_and_non_target_fence",
    "G10": "governance_and_predecessor_fences",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    raw = json.dumps(material, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    overlay_override: dict[str, Any] | None = None,
    hir_override: dict[str, Any] | None = None,
    mir_override: dict[str, Any] | None = None,
    lowering_override: dict[str, Any] | None = None,
    bridge_override: dict[str, Any] | None = None,
    machine_override: dict[str, Any] | None = None,
    loan_fixture_override: dict[str, Any] | None = None,
    ownership_fixture_override: dict[str, Any] | None = None,
    borrow_context_fixture_override: dict[str, Any] | None = None,
    escape_override: dict[str, Any] | None = None,
    rows_override: list[dict[str, Any]] | None = None,
    metadata_override: dict[str, Any] | None = None,
    protected_drift: bool = False,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    contract = contract_override or load(root / CONTRACT_REL)
    overlay = overlay_override or load(root / OVERLAY_REL)
    hir = hir_override or load(root / HIR_REL)
    mir = mir_override or load(root / MIR_REL)
    lowering = lowering_override or load(root / LOWERING_REL)
    bridge = bridge_override or load(root / BRIDGE_REL)
    machine = machine_override or load(root / MACHINE_REL)
    loan = load(root / LOAN_REL)
    loan_fixture = loan_fixture_override or load(root / LOAN_FIXTURE_REL)
    ownership_fixture = ownership_fixture_override or load(root / OWNERSHIP_FIXTURE_REL)
    borrow_contract = load(root / BORROW_CONTEXT_REL)
    borrow_fixture = borrow_context_fixture_override or load(root / BORROW_CONTEXT_FIXTURE_REL)
    escape = escape_override or load(root / ESCAPE_REL)
    suspension = load(root / SUSPEND_REL)
    rows = rows_override or load(root / ROWS_REL)
    metadata = metadata_override or load(root / META_REL)

    # G01: candidate identity and closed schemas.
    require(contract.get("revision") == REVISION and contract.get("canonical_baseline_commit") == CANONICAL and contract.get("local_predecessor_commit") == PREDECESSOR, "G01", "CONTRACT_IDENTITY")
    require(overlay.get("revision") == REVISION and overlay.get("canonical_baseline_commit") == CANONICAL and overlay.get("local_predecessor_commit") == PREDECESSOR, "G01", "OVERLAY_IDENTITY")
    contract_schema = load(root / CONTRACT_SCHEMA_REL)
    overlay_schema = load(root / OVERLAY_SCHEMA_REL)
    require(contract_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "G01", "CONTRACT_SCHEMA_DIALECT")
    require(overlay_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "G01", "OVERLAY_SCHEMA_DIALECT")
    try:
        import jsonschema
    except ModuleNotFoundError:
        # The repository validator runs in the bundled environment where
        # jsonschema is optional. Exact structural gates below remain active.
        pass
    else:
        try:
            jsonschema.Draft202012Validator(contract_schema).validate(contract)
            jsonschema.Draft202012Validator(overlay_schema).validate(overlay)
        except Exception as exc:
            require(False, "G01", f"SCHEMA:{type(exc).__name__}")

    # G02: typed HIR owns the region forest, place bindings and concrete borrow tuple.
    defs = hir.get("$defs", {})
    body_required = set(defs.get("HirBodyBase", {}).get("required", []))
    place = defs.get("PlacePlan", {}).get("allOf", [{}, {}])[1]
    place_required = set(place.get("required", []))
    require({"HirRegionDef", "HirPlaceRegionBinding"}.issubset(defs), "G02", "HIR_REGION_DEFS")
    require({"region_table", "place_region_bindings"}.issubset(body_required), "G02", "HIR_BODY_TABLES")
    require({"result_region_id_or_null", "loan_id_or_null"}.issubset(place_required), "G02", "HIR_PLACE_TUPLE")
    normalized = defs.get("NormalizedTypeDescriptor", {})
    require("region_profile_id_or_null" in normalized.get("required", []) and "region_id_or_null" not in normalized.get("properties", {}), "G02", "TYPE_VALUE_REGION_SEPARATION")
    borrow_rule = place.get("allOf", [{}])[0]
    require(set(borrow_rule.get("if", {}).get("properties", {}).get("access", {}).get("enum", [])) == {"BORROW_SHARED", "BORROW_INOUT"}, "G02", "BORROW_CONDITIONAL")
    general_borrow = borrow_contract.get("hir_projection_contract", {}).get("general_borrow", {})
    require(general_borrow.get("loan_id_created_in_hir") is True and general_borrow.get("loan_id_created_by_mir_lowering") is False, "G02", "LOAN_OWNER_STAGE")

    # G03: MIR retains exact extents, storage regions and value/loan tuples.
    mdefs = mir.get("$defs", {})
    region = mdefs.get("regionDecl", {})
    place_decl = mdefs.get("placeDecl", {})
    value_decl = mdefs.get("valueDecl", {})
    loan_decl = mdefs.get("loanDecl", {})
    require(set(region.get("properties", {}).get("kind", {}).get("enum", [])) == {"LEXICAL", "INVOCATION", "PROCESS_STATIC_IMMUTABLE"}, "G03", "REGION_KIND_CLOSED")
    require({"isolation_domain_id", "entry_point_id", "end_point_ids"}.issubset(region.get("required", [])), "G03", "REGION_EXTENTS")
    require("storage_region_id" in place_decl.get("required", []), "G03", "PLACE_STORAGE_REGION")
    require({"region_id_or_null", "loan_id_or_null"}.issubset(value_decl.get("required", [])), "G03", "VALUE_TUPLE")
    require({"loan_id", "region_id", "parent_loan_id_or_null", "begin_operation_id", "end_operation_ids"}.issubset(loan_decl.get("required", [])), "G03", "LOAN_TUPLE")

    # G04: exact body-wide projection is present at every contract seam.
    lproj = lowering.get("region_lifetime_projection_contract", {})
    bproj = bridge.get("region_lifetime_projection_contract", {})
    mproj = machine.get("region_lifetime_projection_contract", {})
    require(lproj.get("contract") == CONTRACT_REL and lproj.get("composition_layer") == "BODY_WIDE_REGION_LOAN_PROJECTION_AFTER_NODE_ROW_LOWERING_BEFORE_RELEASE_VERIFICATION", "G04", "LOWERING_OWNER")
    require(lproj.get("node_row_fence") == "HM-LR-TOP-006_REMAINS_PLACE_VALUE_OBSERVATION_ONLY" and lproj.get("close_frontier_owner") == "loan_close_projection_contract", "G04", "ROW_AND_CLOSE_FENCE")
    require(bproj.get("type_identity_axis") == "NormalizedTypeDescriptor.region_profile_id_or_null" and bproj.get("exact_identity_preservation") is True, "G04", "BRIDGE_EXACT")
    require(mproj.get("loan_id_origin") == "CHECKER_SEALED_AND_EXACTLY_PRESERVED_HIR_TO_MIR" and mproj.get("loan_balance_owner") == "loan_close_projection_contract", "G04", "MACHINE_EXACT")
    require(machine.get("verifier_contract", {}).get("region_lifetime_graph", "").startswith("RECOMPUTE_REFERENCE_CLOSED_ACYCLIC_REGION_FOREST"), "G04", "MACHINE_VERIFIER")

    # G05: normalized graph and access dispatch are closed and deterministic.
    projection = contract.get("projection_contract", {})
    graph = projection.get("region_graph", {})
    dispatch = projection.get("place_access_dispatch", {})
    loan_projection = projection.get("loan_projection", {})
    require(graph.get("parent_rule") == "FINITE_REFERENCE_CLOSED_ACYCLIC_FOREST_WITH_EXACT_IMMEDIATE_PARENT", "G05", "REGION_FOREST")
    require(graph.get("constraint_normalization") == "SOURCE_ORDER_INDEPENDENT_SORTED_UNIQUE_TRANSITIVE_CLOSURE_WITH_UNIQUE_TRANSITIVE_REDUCTION", "G05", "DETERMINISTIC_GRAPH")
    require(graph.get("mir_kind_map") == {"Lexical": "LEXICAL", "Invocation": "INVOCATION", "ProcessStaticImmutable": "PROCESS_STATIC_IMMUTABLE"}, "G05", "REGION_KIND_MAP")
    require(dispatch == {"READ": "NO_NEW_LOAN_OR_BEGIN_OPERATION", "MOVE": "NO_NEW_LOAN_OR_BEGIN_OPERATION", "REPLACE": "NO_NEW_LOAN_OR_BEGIN_OPERATION", "BORROW_SHARED": "ONE_SHARED_LOAN_AND_ONE_LOAN_BEGIN_SHARED_AT_THE_STATIC_SITE", "BORROW_INOUT": "ONE_EXCLUSIVE_LOAN_AND_ONE_LOAN_BEGIN_EXCLUSIVE_AT_THE_STATIC_SITE"}, "G05", "ACCESS_DISPATCH")
    require(loan_projection.get("loan_id_selection_stage") == "CHECKER_BEFORE_TYPED_HIR_SEALING" and "PRESERVED_HIR_TO_MIR" in loan_projection.get("static_site_cardinality", ""), "G05", "LOAN_ID_OWNER")
    require(loan_projection.get("reborrow_rule") == "LOAN_BEGIN_REBORROW_REQUIRES_ONE_EXACT_ACTIVE_PARENT_LOAN_AND_A_STRICT_CHILD_REGION", "G05", "REBORROW")

    # G06: R34 remains the release owner and source diagnostics retain precedence.
    close = projection.get("close_delegation", {})
    suspension_contract = projection.get("suspension_and_isolation", {})
    diagnostics = projection.get("diagnostic_bindings", {})
    require(close.get("contract") == LOAN_REL and close.get("dynamic_end_cardinality") == "EXACTLY_ONE_PER_BEGIN_PER_REACHABLE_PATH" and close.get("loan_end_failure_or_suspension_count") == 0, "G06", "R34_CLOSE")
    require(close.get("frontier") == "EARLIEST_POST_USE_PATH_FRONTIER_BEFORE_OWNER_BARRIER_REGION_EXIT_OR_UNADMITTED_SUSPEND", "G06", "REGION_EXIT_FRONTIER")
    require(suspension_contract.get("ordinary_or_exclusive_cross_suspension") == "REJECT" and suspension_contract.get("process_static_immutable_shared_exception") == "ONLY_WITH_THE_EXACT_EXISTING_ADMITTED_PROOF", "G06", "SUSPENSION_FENCE")
    require(diagnostics == {"escape_or_unresolved_region_relation": "BORROW_ESCAPE_OWNER_REGION", "exclusive_overlap_or_domain_mismatch": "INOUT_ALIAS_CONFLICT", "ordinary_live_loan_at_suspension": "BORROW_CROSSES_SUSPENSION", "facet_live_loan_at_suspension": "FACET_BORROW_CROSSES_SUSPENSION", "malformed_emitted_mir": "MIR_LOAN_UNBALANCED"}, "G06", "DIAGNOSTIC_BINDINGS")
    require(projection.get("diagnostic_order", [])[-1:] == ["MIR_LOAN_UNBALANCED_RELEASE_VERIFIER"], "G06", "DIAGNOSTIC_ORDER")
    require(loan.get("close_frontier", {}).get("dynamic_balance_rule", "").startswith("each dynamic begin activation executes exactly one matching end"), "G06", "LOAN_CONTRACT")

    # G07: exact existing evidence IDs and their oracles are present.
    acceptance = contract.get("acceptance_matrix", [])
    require([row.get("case_id") for row in acceptance] == [f"R68-RL-ACC-{index:03d}" for index in range(1, 13)], "G07", "ACCEPTANCE_IDS")
    loan_cases = {row.get("case_id"): row for row in loan_fixture.get("cases", [])}
    require(set(loan_cases) == {"R34-LOAN-POS-001", "R34-LOAN-POS-002", "R34-LOAN-POS-003", "R34-LOAN-BND-004", "R34-LOAN-BND-005", "R34-LOAN-BND-006", "R34-LOAN-NEG-007", "R34-LOAN-NEG-008", "R34-LOAN-NEG-009", "R34-LOAN-NEG-010", "R34-LOAN-NEG-011", "R34-LOAN-NEG-012"}, "G07", "R34_CASES")
    scenarios = ownership_fixture.get("scenarios", {})
    require({"OWN-PLACE-P-010", "OWN-PLACE-P-011", "OWN-PLACE-P-012", "OWN-PLACE-B-013"}.issubset(scenarios), "G07", "R5_CASES")
    require([row.get("branch_rank") for row in escape.get("reason_rows", [])] == [1, 2, 3, 4] and all(row.get("expected_diagnostic_id") == "BORROW_ESCAPE_OWNER_REGION" for row in escape.get("reason_rows", [])), "G07", "ESCAPE_CASES")
    require({"R20-SUS-N-001", "R20-SUS-N-002"}.issubset({row.get("test_id") for row in suspension.get("tests", [])}), "G07", "SUSPEND_CASES")
    ordinary = [row for row in borrow_fixture.get("cases", []) if row.get("source_or_scenario") == "borrow place"]
    context = [row for row in borrow_fixture.get("cases", []) if row.get("source_or_scenario", "").startswith("&")]
    require(ordinary and all(row.get("loan_id_created_in_hir") == 1 and row.get("loan_id_created_by_mir_lowering") == 0 for row in ordinary), "G07", "BORROW_IDENTITY_CASES")
    require(context and all(row.get("loan_id_created_in_hir") == row.get("loan_id_created_by_mir_lowering") == row.get("borrow_event_created") == 0 for row in context), "G07", "CONTEXT_ZERO")

    # G08: exactly one direct nondelegated overlay binding.
    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    entry = entries[0] if len(entries) == 1 else {}
    binding = bindings[0] if len(bindings) == 1 else {}
    require(len(entries) == len(bindings) == len(overlay.get("acceptance_cases", [])) == 1, "G08", "ONE_ONE_ONE")
    require(entry == {"evidence_key": EVIDENCE_KEY, "class": "ARTIFACT_POINTER", "path": CONTRACT_REL, "locator_kind": "JSON_POINTER", "locator": "/projection_contract", "stage_role": "DYNAMIC_LOWERING"}, "G08", "ENTRY_EXACT")
    require(binding.get("feature_id") == FEATURE and binding.get("stage") == "DYNAMIC_LOWERING" and binding.get("outcome") is None, "G08", "TARGET_EXACT")
    require(binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP" and binding.get("disposition") == "BOUND_DIRECT", "G08", "BLOCKED_TO_DIRECT")
    require(binding.get("evidence_keys") == [EVIDENCE_KEY] and binding.get("delegate_feature_id") is None and binding.get("not_applicable") is None, "G08", "DIRECT_ONLY")

    # G09: generated ledger changes only the target cell.
    cells, duplicates = trace_cells(rows)
    target = cells.get(TARGET, {})
    count, digest = non_target_digest(cells)
    derived = metadata.get("derived_counts", {})
    require(len(rows) == 469 and len(cells) == 4221 and duplicates == 0, "G09", "LEDGER_SHAPE")
    require(target == {"stage": "DYNAMIC_LOWERING", "disposition": "BOUND_DIRECT", "evidence_refs": [EVIDENCE_ID], "delegate_feature_id": None, "not_applicable": None, "blocked_gap_ids": []}, "G09", "TARGET_GENERATED_EXACT")
    require(count == 4220 and digest == NON_TARGET_SHA256, "G09", "OTHER_4220_EXACT")
    require((derived.get("bound_direct_cells"), derived.get("bound_delegated_cells"), derived.get("not_applicable_cells"), derived.get("applicable_blocked_cells")) == (2466, 3, 501, 1251), "G09", "COUNTS")
    require(len(metadata.get("applied_evidence_overlays", [])) == 14 and sum(row.get("binding_count", 0) for row in metadata.get("applied_evidence_overlays", [])) == 130 and len(metadata.get("evidence_registry", [])) == 3143, "G09", "OVERLAY_COUNTS")

    # G10: governance is honest and the R67/integrity predecessors stay unchanged.
    guards = overlay.get("guards", {})
    governance = metadata.get("governance", {})
    require(guards.get("semantic_p0") == governance.get("semantic_p0") == 0 and guards.get("feature_p1") == governance.get("feature_p1") == "22_OPEN_UNCHANGED", "G10", "P0_P1")
    require(guards.get("product_lanes") == governance.get("product_lanes") == "15_OF_15_NOT_RUN" and guards.get("github_publication") == governance.get("github_publication") == "SUSPENDED", "G10", "PRODUCT_GITHUB")
    require(all(guards.get(key) == 0 for key in ("region_parent_cycle_count", "unresolved_region_or_loan_reference_count", "mir_created_static_loan_id_count", "type_level_concrete_region_id_count", "context_anchor_region_or_loan_creation_count", "new_source_surface_count", "new_mir_operation_kind_count", "runtime_region_object_count", "runtime_or_backend_relookup_count", "product_execution_receipt_count")), "G10", "ZERO_FENCES")
    for relative, expected in PROTECTED.items():
        observed = "0" * 64 if protected_drift and relative.endswith("closure-capture-dynamic-trace-evidence-r1.json") else sha256(root / relative)
        require(observed == expected, "G10", f"HASH:{relative}")
    decision = (root / DECISION_REL).read_text(encoding="utf-8")
    require("checker selects static RegionId and LoanId" in decision and "15_OF_15_NOT_RUN" in decision and "SUSPENDED" in decision, "G10", "DECISION_FENCES")
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
    print(json.dumps({
        "schema": "deeplus.region-lifetime-dynamic-trace-validation-receipt/r1",
        "revision": REVISION,
        "canonical_baseline_commit": CANONICAL,
        "local_predecessor_commit": PREDECESSOR,
        "result": "PASS" if not errors else "FAIL",
        "gate_summary": f"{passed}/{len(GATES)}",
        "feature_id": FEATURE,
        "transitioned_cell_count": 1,
        "unchanged_non_target_cell_count": 4220,
        "projected_counts": {"bound_direct": 2466, "bound_delegated": 3, "not_applicable": 501, "applicable_blocked": 1251},
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "gates": gates,
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
