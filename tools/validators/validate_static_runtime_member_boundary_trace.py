#!/usr/bin/env python3
"""Validate the bounded R70 static/runtime member-boundary trace closure.

This is a design-static validator.  It proves that the target law is closed
before MIR lowering; it does not execute a parser, runtime, backend, formatter,
or LSP.  In-memory overrides are exposed only for the focused mutation runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


PREDECESSOR = "29059c1b23de7d32398f582d2a37d5ce24d31341"
CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
REVISION = "r70-local-static-runtime-member-boundary-trace-closure-r1"
FEATURE = "static_runtime_member_boundary_law"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
NON_TARGET_COUNT = 4220
NON_TARGET_SHA256 = "a6a56943d6b8b51c177b4ff282ef3db50dcc3f85a950495d80553d4c552bec35"
EVIDENCE_ID = "EV-8ab19e684aca7aeae5d3a2c0f9418ff5db42f41bb9f061af7e580d51d3a7c3aa"
OVERLAY = "spec/traceability/implementation-target-profile-r1/static-runtime-member-boundary-evidence-r1.json"
OVERLAY_SCHEMA = "schemas/language/static-runtime-member-boundary-evidence-r1.schema.json"
ROWS = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
TRACE_SCHEMA = "schemas/language/implementation-target-traceability-r1.schema.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
FRONTEND = "spec/frontend/frontend-model.json"
FEATURE_CHUNK = "spec/features/catalog/chunks/part-0016.json"
CONTRACT = "spec/contracts/static-runtime-member-boundary-trace-closure-r1.json"
CONTRACT_SCHEMA = "schemas/language/static-runtime-member-boundary-trace-closure-r1.schema.json"
FIXTURE = "tests/fixtures/current/static-runtime-member-boundary-trace-closure-r1.json"
FIXTURE_SCHEMA = "schemas/language/static-runtime-member-boundary-trace-closure-fixtures-r1.schema.json"

JSON_PATHS = (
    OVERLAY,
    OVERLAY_SCHEMA,
    ROWS,
    METADATA,
    TRACE_SCHEMA,
    BRIDGE,
    FRONTEND,
    FEATURE_CHUNK,
    CONTRACT,
    CONTRACT_SCHEMA,
    FIXTURE,
    FIXTURE_SCHEMA,
)

GATES = {
    "G01": "overlay_identity_and_not_applicable_reason",
    "G02": "static_boundary_bridge_and_ordinary_dot_separation",
    "G03": "predecessor_target_and_non_target_fence",
    "G04": "generated_registry_projection",
    "G05": "governance_tooling_and_product_fence",
    "G06": "semantic_contract_acceptance_and_mutation_binding",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_inputs(root: Path) -> Dict[str, Any]:
    return {relative: load(root / relative) for relative in JSON_PATHS}


def evidence_id(item: Mapping[str, Any]) -> str:
    material = "\0".join(
        str(item.get(key, ""))
        for key in ("class", "path", "locator_kind", "locator", "stage_role")
    )
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def predecessor_rows(root: Path) -> List[Dict[str, Any]]:
    proc = subprocess.run(
        [
            "git",
            "-c",
            "safe.directory=" + root.as_posix(),
            "-C",
            str(root),
            "show",
            PREDECESSOR + ":" + ROWS,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(proc.stdout.decode("utf-8"))


def trace_cells(
    rows: List[Dict[str, Any]],
) -> Tuple[Dict[Tuple[str, str, Optional[str]], Dict[str, Any]], int]:
    cells: Dict[Tuple[str, str, Optional[str]], Dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        for stage in row.get("stages", []):
            for cell in stage.get("outcomes", [stage]):
                outcome = (
                    cell.get("outcome")
                    if stage.get("stage") == "CONFORMANCE_TESTS"
                    else None
                )
                key = (row.get("feature_id"), stage.get("stage"), outcome)
                if key in cells:
                    duplicates += 1
                cells[key] = cell
    return cells, duplicates


def non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    material = [[*key, value] for key, value in cells.items() if key != TARGET]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def validate(
    root: Path,
    *,
    overrides: Optional[Mapping[str, Any]] = None,
    predecessor_rows_override: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    errors: List[str] = []
    values = load_inputs(root)
    if overrides:
        values.update(overrides)

    def value(relative: str) -> Any:
        return values[relative]

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(gate + ":" + code)

    overlay = value(OVERLAY)
    overlay_schema = value(OVERLAY_SCHEMA)
    rows = value(ROWS)
    metadata = value(METADATA)
    trace_schema = value(TRACE_SCHEMA)
    bridge = value(BRIDGE)
    frontend = value(FRONTEND)
    feature_chunk = value(FEATURE_CHUNK)
    contract = value(CONTRACT)
    contract_schema = value(CONTRACT_SCHEMA)
    fixture = value(FIXTURE)
    fixture_schema = value(FIXTURE_SCHEMA)
    before_rows = predecessor_rows_override or predecessor_rows(root)

    require(
        overlay_schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema"
        and trace_schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema",
        "G01",
        "SCHEMA_DIALECT",
    )
    require(
        contract_schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema"
        and fixture_schema.get("$schema")
        == "https://json-schema.org/draft/2020-12/schema",
        "G06",
        "SCHEMA_DIALECT",
    )
    try:
        import jsonschema
    except ModuleNotFoundError:
        # The repository's bundled validator profile permits jsonschema to be
        # absent; the exact structural gates below remain authoritative.
        pass
    else:
        try:
            jsonschema.Draft202012Validator.check_schema(overlay_schema)
            jsonschema.Draft202012Validator(overlay_schema).validate(overlay)
            jsonschema.Draft202012Validator.check_schema(trace_schema)
            jsonschema.Draft202012Validator(trace_schema).validate(metadata)
        except Exception as exc:
            errors.append("G01:JSON_SCHEMA:" + type(exc).__name__)
        try:
            jsonschema.Draft202012Validator.check_schema(contract_schema)
            jsonschema.Draft202012Validator(contract_schema).validate(contract)
            jsonschema.Draft202012Validator.check_schema(fixture_schema)
            jsonschema.Draft202012Validator(fixture_schema).validate(fixture)
        except Exception as exc:
            errors.append("G06:JSON_SCHEMA:" + type(exc).__name__)

    # G01: one exact overlay binding converts only the target cell to static NA.
    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    entry = entries[0] if len(entries) == 1 else {}
    binding = bindings[0] if len(bindings) == 1 else {}
    evidence_key = entry.get("evidence_key")
    detail = binding.get("not_applicable") or {}
    require(
        overlay.get("schema")
        == "deeplus.static-runtime-member-boundary-evidence/r1"
        and overlay.get("revision") == REVISION
        and overlay.get("canonical_baseline_commit") == CANONICAL
        and overlay.get("local_predecessor_commit") == PREDECESSOR
        and overlay.get("feature_ids") == [FEATURE],
        "G01",
        "OVERLAY_IDENTITY",
    )
    require(
        len(entries) == 1
        and entry.get("class") == "ARTIFACT_POINTER"
        and entry.get("path") == BRIDGE
        and entry.get("locator_kind") == "JSON_POINTER"
        and entry.get("locator") == "/name_resolution_module_bridge"
        and entry.get("stage_role") == "DYNAMIC_LOWERING"
        and evidence_id(entry) == EVIDENCE_ID,
        "G01",
        "EXACT_BRIDGE_EVIDENCE",
    )
    require(
        len(bindings) == 1
        and binding.get("feature_id") == FEATURE
        and binding.get("stage") == "DYNAMIC_LOWERING"
        and binding.get("outcome") is None
        and binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP"
        and binding.get("disposition") == "NOT_APPLICABLE"
        and binding.get("evidence_keys") == [evidence_key]
        and binding.get("delegate_feature_id") is None,
        "G01",
        "ONE_NOT_APPLICABLE_BINDING",
    )
    require(
        detail.get("reason_code") == "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR"
        and detail.get("authority_boundary") == "MIR_RUNTIME_AUTHORITY"
        and detail.get("justification_evidence_keys") == [evidence_key]
        and bool(detail.get("rationale")),
        "G01",
        "EXACT_NOT_APPLICABLE_REASON",
    )
    counts = overlay.get("counts", {})
    require(
        counts.get("feature_count") == 1
        and counts.get("evidence_entry_count") == 1
        and counts.get("binding_count") == 1
        and counts.get("predecessor_blocked_cell_count") == 1
        and counts.get("overlay_bound_direct_transition_count") == 0
        and counts.get("overlay_bound_delegated_transition_count") == 0
        and counts.get("overlay_not_applicable_transition_count") == 1
        and counts.get("predecessor_cumulative_overlay_count") == 15
        and counts.get("post_overlay_cumulative_overlay_count") == 16
        and counts.get("predecessor_cumulative_overlay_binding_count") == 131
        and counts.get("post_overlay_cumulative_binding_count") == 132
        and counts.get("predecessor_evidence_registry_count") == 3144
        and counts.get("post_overlay_evidence_registry_count") == 3145,
        "G01",
        "OVERLAY_COUNTS",
    )

    # G02: the static identity is eliminated before lowering; dot remains a
    # separate frontend MemberAccess role and is not claimed by this cell.
    module_bridge = bridge.get("name_resolution_module_bridge", {})
    name_binding = module_bridge.get("name_binding_to_hir", {})
    module_receipts = module_bridge.get("module_receipts", {})
    seal = module_bridge.get("seal", {})
    canonical_hir = bridge.get("canonical_hir_contract", {})
    import_rule = str(name_binding.get("import_binding", ""))
    require(
        name_binding.get("static_declaration") == "ResolvedRef::DirectDecl(DeclId)"
        and "MODULE_NAMESPACE_TARGET_IS_ModuleId" in import_rule
        and "ONLY_EXPRESSION_REFERENCES_PROJECT_ResolvedRef::DirectDecl" in import_rule,
        "G02",
        "MODULE_AND_STATIC_HIR_BOUNDARY",
    )
    require(
        module_receipts.get("runtime_module_initializer_count") == 0
        and seal.get("runtime_relookup_count") == 0
        and canonical_hir.get("runtime_string_to_static_identity_conversion_count") == 0
        and "name_or_selector_lookup"
        in canonical_hir.get("mir_lowerer_forbidden_decisions", []),
        "G02",
        "ZERO_RUNTIME_RECONSTRUCTION",
    )
    dot_rows = [row for row in frontend.get("stage_names", []) if row.get("surface") == "."]
    require(
        len(dot_rows) == 1
        and "MemberAccess" in dot_rows[0].get("ast_roles", [])
        and dot_rows[0].get("lexer") == "DOT",
        "G02",
        "ORDINARY_DOT_FRONTEND_SEPARATE",
    )

    # G03: exact predecessor and a 4,220-cell non-target immutability fence.
    before_cells, before_duplicates = trace_cells(before_rows)
    current_cells, current_duplicates = trace_cells(rows)
    before_target = before_cells.get(TARGET, {})
    current_target = current_cells.get(TARGET, {})
    require(
        before_target.get("disposition") == "APPLICABLE_BLOCKED_BY_GAP"
        and before_target.get("blocked_gap_ids") == ["IR-XCUT-P1-054"],
        "G03",
        "PREDECESSOR_TARGET_BLOCKED",
    )
    target_detail = current_target.get("not_applicable") or {}
    require(
        current_target.get("disposition") == "NOT_APPLICABLE"
        and current_target.get("evidence_refs") == []
        and current_target.get("delegate_feature_id") is None
        and current_target.get("blocked_gap_ids") == []
        and target_detail.get("reason_code")
        == "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR"
        and target_detail.get("authority_boundary") == "MIR_RUNTIME_AUTHORITY"
        and target_detail.get("justification_evidence_refs") == [EVIDENCE_ID],
        "G03",
        "GENERATED_TARGET_EXACT",
    )
    before_count, before_digest = non_target_digest(before_cells)
    current_count, current_digest = non_target_digest(current_cells)
    require(
        before_duplicates == current_duplicates == 0
        and len(before_cells) == len(current_cells) == 4221
        and before_count == current_count == NON_TARGET_COUNT
        and before_digest == current_digest == NON_TARGET_SHA256,
        "G03",
        "NON_TARGET_4220_EXACT",
    )

    # G04: generated metadata and registry bind the sixteenth overlay.
    applied = metadata.get("applied_evidence_overlays", [])
    registry = metadata.get("evidence_registry", [])
    registered = [row for row in registry if row.get("evidence_id") == EVIDENCE_ID]
    derived = metadata.get("derived_counts", {})
    require(
        metadata.get("revision") == REVISION
        and metadata.get("canonical_baseline_commit") == CANONICAL
        and metadata.get("local_predecessor_commit") == PREDECESSOR,
        "G04",
        "METADATA_IDENTITY",
    )
    require(
        len(applied) == 16
        and sum(row.get("binding_count", 0) for row in applied) == 132
        and applied[-1]
        == {"path": OVERLAY, "feature_count": 1, "binding_count": 1},
        "G04",
        "OVERLAY_REGISTRATION",
    )
    require(
        len(registry) == 3145
        and len(registered) == 1
        and registered[0].get("path") == BRIDGE
        and registered[0].get("locator") == "/name_resolution_module_bridge",
        "G04",
        "EVIDENCE_REGISTRATION",
    )
    require(
        derived.get("bound_direct_cells") == 2467
        and derived.get("bound_delegated_cells") == 3
        and derived.get("not_applicable_cells") == 502
        and derived.get("applicable_blocked_cells") == 1249
        and derived.get("missing_cells") == 0
        and derived.get("conflict_cells") == 0,
        "G04",
        "PROJECTED_COUNTS",
    )

    # G05: no semantic/product expansion and tooling remains obligation-only.
    guards = overlay.get("guards", {})
    governance = metadata.get("governance", {})
    target_row = next((row for row in rows if row.get("feature_id") == FEATURE), {})
    tooling = next(
        (stage for stage in target_row.get("stages", []) if stage.get("stage") == "TOOLING_OBLIGATIONS"),
        {},
    )
    catalog_row = next(
        (row for row in feature_chunk if row.get("feature_id") == FEATURE), {}
    )
    require(
        guards.get("transitioned_cell_count") == 1
        and guards.get("other_cell_transition_count") == 0
        and guards.get("other_atomic_cell_count") == NON_TARGET_COUNT
        and guards.get("other_atomic_cell_sha256") == NON_TARGET_SHA256
        and guards.get("ordinary_dot_member_cell_transition_count") == 0
        and guards.get("double_colon_cell_transition_count") == 0
        and guards.get("method_extension_cell_transition_count") == 0
        and guards.get("runtime_module_object_count") == 0
        and guards.get("new_source_surface_count") == 0
        and guards.get("new_identity_count") == 0
        and guards.get("new_p1_count") == 0
        and guards.get("runtime_or_backend_relookup_count") == 0,
        "G05",
        "BOUNDED_SCOPE",
    )
    require(
        guards.get("semantic_p0") == 0
        and guards.get("feature_p1") == "22_OPEN_UNCHANGED"
        and guards.get("m13_actions") == "4_OPEN_UNCHANGED"
        and guards.get("product_lanes") == "15_OF_15_NOT_RUN"
        and guards.get("github_publication") == "SUSPENDED"
        and guards.get("product_execution_receipt_count") == 0
        and guards.get("implementation_claim") == "NONE",
        "G05",
        "OVERLAY_GOVERNANCE",
    )
    require(
        governance.get("semantic_p0") == 0
        and governance.get("feature_p1") == "22_OPEN_UNCHANGED"
        and governance.get("m13_actions") == "4_OPEN_UNCHANGED"
        and governance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and governance.get("github_publication") == "SUSPENDED"
        and governance.get("e4_e5_evidence_count") == 0,
        "G05",
        "REGISTRY_GOVERNANCE",
    )
    require(
        tooling.get("disposition") == "BOUND_DIRECT"
        and tooling.get("blocked_gap_ids") == []
        and "EV-fe6fa6caa4aa7982ab89770477848501c02e68c5c246c2d4e2cea5f58dbd7c6d"
        in tooling.get("evidence_refs", [])
        and target_row.get("product_execution") == "NOT_RUN"
        and catalog_row.get("formatter_lsp") == "NOT_RUN"
        and catalog_row.get("runtime_xvm") == "NOT_RUN"
        and current_target.get("delegate_feature_id") is None,
        "G05",
        "TOOLING_PRODUCT_AND_DELEGATION_FENCE",
    )

    # G06: the semantic closure carries nine exact design-static acceptance
    # cases and the fixture binds the fourteen bounded mutation obligations.
    contract_target = contract.get("target_cell", {})
    authority = contract.get("authority_fence", {})
    boundary = contract.get("boundary_definition", {})
    resolver = contract.get("resolver_hir_fence", {})
    handoff = contract.get("terminal_selection_handoff", {})
    runtime_fence = contract.get("runtime_backend_residue_fence", {})
    diagnostics = contract.get("diagnostic_ownership", {})
    machine = contract.get("machine_acceptance", {})
    require(
        contract.get("schema")
        == "deeplus.static-runtime-member-boundary-trace-closure/r1"
        and contract.get("revision") == REVISION
        and contract.get("canonical_baseline_commit") == CANONICAL
        and contract.get("local_predecessor_commit") == PREDECESSOR
        and contract.get("feature_id") == FEATURE
        and contract.get("source_activation") == "none"
        and contract.get("current_binding") is False,
        "G06",
        "CONTRACT_IDENTITY",
    )
    require(
        contract_target.get("stage") == "DYNAMIC_LOWERING"
        and contract_target.get("predecessor_disposition")
        == "APPLICABLE_BLOCKED_BY_GAP"
        and contract_target.get("predecessor_gap_id") == "IR-XCUT-P1-054"
        and contract_target.get("disposition") == "NOT_APPLICABLE"
        and contract_target.get("reason_code")
        == "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR"
        and contract_target.get("authority_boundary") == "MIR_RUNTIME_AUTHORITY",
        "G06",
        "CONTRACT_TARGET_CELL",
    )
    require(
        all(
            authority.get(key) == 0
            for key in (
                "new_source_surface_count",
                "new_grammar_production_count",
                "new_ast_identity_count",
                "new_hir_identity_count",
                "new_mir_operation_kind_count",
                "new_mir_terminator_kind_count",
                "new_xvm_capability_count",
                "new_internal_runtime_abi_field_count",
                "new_runtime_helper_count",
                "new_cranelift_mapping_count",
                "semantic_p0",
            )
        )
        and authority.get("open_feature_p1") == 22
        and authority.get("open_m13_actions") == 4
        and authority.get("product_lanes")
        == {"total": 15, "executed": 0, "state": "15_OF_15_NOT_RUN"}
        and authority.get("github_publication") == "SUSPENDED"
        and authority.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
        and authority.get("evidence_level") == "E2_STRUCTURED_STATIC",
        "G06",
        "CONTRACT_AUTHORITY_FENCE",
    )
    require(
        boundary.get("module_identity_is_runtime_value") is False
        and boundary.get("static_qualifier_identity_is_runtime_value") is False
        and boundary.get("qualifier_lookup_erased_before_expression_hir") is True
        and boundary.get("runtime_member_surface") == "."
        and boundary.get("static_qualification_surface") == "::"
        and boundary.get("ordinary_dot_execution_owner")
        == "SEPARATE_EXISTING_PLACEPLAN_OR_CALLPLAN_CONTRACT"
        and boundary.get("ordinary_dot_execution_absorbed_by_r70") is False
        and boundary.get("companion_or_metatype_value_created") is False,
        "G06",
        "STATIC_RUNTIME_DOMAIN_FENCE",
    )
    require(
        resolver.get("module_resolver_identity") == "ModuleId"
        and resolver.get("module_expression_hir_projection") is None
        and resolver.get("static_terminal_expression_hir_projection")
        == "ResolvedRef::DirectDecl(DeclId)"
        and resolver.get("ordinary_dot_field_hir_projection")
        == "PlacePlan.root+StaticProjection::FIELD(field_symbol_key)"
        and resolver.get("ordinary_dot_call_hir_projection")
        == "CallPlan(mode_target_pair,call_head_id)"
        and resolver.get("unresolved_count") == 0
        and resolver.get("candidate_set_count") == 0
        and resolver.get("runtime_relookup_count") == 0
        and resolver.get("recovery_admitted_hir_count") == 0,
        "G06",
        "RESOLVER_HIR_FENCE",
    )
    require(
        handoff.get("static_value", {}).get("lowering_rows")
        == ["HM-LR-REF-002", "HM-LR-TOP-002"]
        and handoff.get("ordinary_dot_field_read", {}).get("lowering_rows")
        == ["HM-LR-TOP-006"]
        and handoff.get("ordinary_direct_call", {}).get("hir_mode_target_pair")
        == "ORDINARY::DIRECT_IMPLEMENTATION"
        and handoff.get("ordinary_direct_call", {}).get("lowering_rows")
        == ["HM-LR-CALL-001"]
        and handoff.get("ordinary_virtual_call", {}).get("hir_mode_target_pair")
        == "ORDINARY::VIRTUAL_SLOT"
        and handoff.get("ordinary_virtual_call", {}).get("lowering_rows")
        == ["HM-LR-CALL-002"]
        and handoff.get("ordinary_extension_static_call", {}).get(
            "hir_mode_target_pair"
        )
        == "ORDINARY::EXTENSION_STATIC"
        and handoff.get("ordinary_extension_static_call", {}).get("lowering_rows")
        == ["HM-LR-CALL-004"],
        "G06",
        "EXISTING_HANDOFF_ROWS_EXACT",
    )
    require(
        all(
            runtime_fence.get(key) == 0
            for key in (
                "qualifier_hir_residue_count",
                "qualifier_mir_residue_count",
                "runtime_selector_lookup_count",
                "runtime_member_name_lookup_count",
                "xvm_new_opcode_count",
                "xvm_new_capability_count",
                "internal_runtime_selector_payload_count",
                "internal_runtime_selector_helper_count",
                "cranelift_selector_reselection_count",
                "cranelift_new_mapping_count",
                "target_identity_leak_count",
            )
        )
        and runtime_fence.get("xvm_authority") == "Verified<DeeplusMirR1>"
        and runtime_fence.get("internal_runtime_abi_role")
        == "TYPED_CALL_TRANSPORT_ONLY"
        and runtime_fence.get("cranelift_input") == "Verified<DeeplusMir>"
        and runtime_fence.get("cranelift_lowering")
        == "DETERMINISTIC_MIR_TO_BACKEND_PRIVATE_CLIF",
        "G06",
        "RUNTIME_BACKEND_ZERO_RESIDUE",
    )
    owned_ids = [row.get("diagnostic_id") for row in diagnostics.get("owned", [])]
    delegated_ids = [
        row.get("diagnostic_id") for row in diagnostics.get("delegated", [])
    ]
    require(
        owned_ids
        == ["MODULE_IS_NOT_A_VALUE", "STATIC_ALIAS_CONFLICTS_WITH_LOCAL_BINDING"]
        and delegated_ids
        == [
            "DOTTED_STATIC_PATH_NOT_CURRENT",
            "DOT_NOT_ALLOWED_FOR_TYPE_SIDE_SELECTOR",
            "STATIC_SELECTOR_RESOLUTION_FAILED",
            "MEMBER_EXTENSION_COLLISION",
            "MEMBER_NOT_FOUND",
        ]
        and [row.get("ordinal") for row in diagnostics.get("precedence", [])]
        == [1, 2, 3, 4, 5, 6]
        and diagnostics.get("new_diagnostic_count") == 0
        and diagnostics.get("r70_reselection_count") == 0,
        "G06",
        "DIAGNOSTIC_OWNERSHIP_EXACT",
    )
    acceptance = contract.get("acceptance_cases", [])
    acceptance_ids = [row.get("case_id") for row in acceptance]
    expected_acceptance_ids = [f"R70-SRMB-ACC-{index:03d}" for index in range(1, 10)]
    expected_assertions = [
        [
            "QUALIFIER_ERASED_BEFORE_EXPRESSION_HIR",
            "DIRECT_DECL_ID_EXACT",
            "HM_LR_REF_002_THEN_TOP_002",
            "RUNTIME_RELOOKUP_ZERO",
        ],
        [
            "QUALIFIER_ERASED_BEFORE_EXPRESSION_HIR",
            "ORDINARY_DIRECT_IMPLEMENTATION",
            "HM_LR_CALL_001",
            "RUNTIME_SELECTOR_LOOKUP_ZERO",
        ],
        [
            "MEMBER_ACCESS_AST_ROLE",
            "PLACEPLAN_FIELD_OR_CALLPLAN",
            "NO_STATIC_DOMAIN_ENTRY",
            "R70_ABSORPTION_ZERO",
        ],
        [
            "ASSOCIATED_TYPE_RUNTIME_OPERATION_ZERO",
            "NORMALIZE_BEFORE_SECOND_SELECTION",
            "SECOND_DOMAIN_NOMINAL_TYPE_SIDE",
            "TRAIT_EXTENSION_FALLBACK_ZERO",
        ],
        [
            "CALLPLAN_SELECTED_BEFORE_MIR",
            "HM_LR_CALL_001_002_004_EXACT",
            "RECEIVER_EVALUATED_ONCE",
            "RUNTIME_SELECTOR_LOOKUP_ZERO",
        ],
        [
            "MODULE_EXPRESSION_HIR_PROJECTION_ZERO",
            "MIR_NODE_COUNT_ZERO",
            "RUNTIME_RELOOKUP_ZERO",
        ],
        [
            "R70_DIAGNOSTIC_RESELECTION_ZERO",
            "EXPRESSION_HIR_COUNT_ZERO",
            "STATIC_QUALIFICATION_REWRITE_IS_DOUBLE_COLON",
        ],
        [
            "UNRESOLVED_HIR_COUNT_ZERO",
            "CANDIDATE_SET_HIR_COUNT_ZERO",
            "RUNTIME_FALLBACK_ZERO",
        ],
        [
            "LOCAL_BINDING_IDENTITY_PRESERVED",
            "STATIC_ALIAS_BINDING_NOT_CREATED",
            "RUNTIME_RELOOKUP_ZERO",
        ],
    ]
    require(
        acceptance_ids == expected_acceptance_ids
        and [row.get("class") for row in acceptance]
        == ["POSITIVE"] * 3 + ["BOUNDARY"] * 2 + ["REJECT"] * 4
        and [row.get("assertion_ids") for row in acceptance] == expected_assertions
        and all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in acceptance)
        and contract.get("acceptance_bindings", {}).get("POSITIVE")
        == expected_acceptance_ids[:3]
        and contract.get("acceptance_bindings", {}).get("BOUNDARY")
        == expected_acceptance_ids[3:5]
        and contract.get("acceptance_bindings", {}).get("REJECT")
        == expected_acceptance_ids[5:],
        "G06",
        "ACCEPTANCE_9_EXACT",
    )
    mutation_ids = [
        row.get("mutation_id") for row in contract.get("mutation_obligations", [])
    ]
    expected_mutation_ids = [f"M{index:02d}" for index in range(1, 15)]
    require(
        mutation_ids == expected_mutation_ids
        and all(
            row.get("expected") == "MUTANT_KILLED"
            for row in contract.get("mutation_obligations", [])
        ),
        "G06",
        "MUTATION_OBLIGATIONS_M01_M14",
    )
    require(
        machine.get("feature_count") == 1
        and machine.get("transitioned_cell_count") == 1
        and machine.get("not_applicable_transition_count") == 1
        and machine.get("other_feature_transition_count") == 0
        and machine.get("rule_count") == 14
        and machine.get("lookup_domain_count") == 4
        and machine.get("acceptance_case_count") == 9
        and machine.get("positive_case_count") == 3
        and machine.get("boundary_case_count") == 2
        and machine.get("reject_case_count") == 4
        and machine.get("acceptance_bound_case_count") == 9
        and machine.get("mutation_obligation_count") == 14
        and machine.get("new_hir_identity_count") == 0
        and machine.get("new_mir_operation_kind_count") == 0
        and machine.get("new_mir_terminator_kind_count") == 0
        and machine.get("runtime_relookup_count") == 0
        and machine.get("xvm_new_opcode_count") == 0
        and machine.get("internal_runtime_selector_payload_count") == 0
        and machine.get("cranelift_selector_reselection_count") == 0
        and machine.get("other_target_cell_transition_count") == 0
        and machine.get("product_executed_count") == 0,
        "G06",
        "MACHINE_ACCEPTANCE_EXACT",
    )
    fixture_acceptance = fixture.get("acceptance_oracles", [])
    fixture_mutations = fixture.get("mutation_oracles", [])
    require(
        fixture.get("schema")
        == "deeplus.static-runtime-member-boundary-trace-closure-fixtures/r1"
        and fixture.get("revision") == REVISION
        and fixture.get("contract") == CONTRACT
        and fixture.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
        and [row.get("case_id") for row in fixture_acceptance]
        == expected_acceptance_ids
        and [row.get("mutation_id") for row in fixture_mutations]
        == expected_mutation_ids,
        "G06",
        "FIXTURE_9_AND_M01_M14_BINDING",
    )
    require(
        [row.get("class") for row in fixture_acceptance]
        == ["POSITIVE"] * 3 + ["BOUNDARY"] * 2 + ["REJECT"] * 4
        and all(row.get("expected_gate") == "G06" for row in fixture_mutations)
        and all(row.get("expected") == "MUTANT_KILLED" for row in fixture_mutations),
        "G06",
        "FIXTURE_ORACLE_EXPECTATIONS_EXACT",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = validate(root)
    except Exception as exc:
        errors = ["EXCEPTION:" + type(exc).__name__ + ":" + str(exc)]
    receipt = {
        "schema": "deeplus.r70-static-runtime-member-boundary-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_id": FEATURE,
        "transitioned_cell_count": 1,
        "projected_counts": {
            "bound_direct": 2467,
            "bound_delegated": 3,
            "not_applicable": 502,
            "applicable_blocked": 1249,
        },
        "non_target_cell_count": NON_TARGET_COUNT,
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
