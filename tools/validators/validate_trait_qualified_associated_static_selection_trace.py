#!/usr/bin/env python3
"""Validate the bounded R62 trait-qualified associated-static trace closure."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/trait-qualified-associated-static-selection-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/trait-qualified-associated-static-selection-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/trait-qualified-associated-static-selection-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/trait-qualified-associated-static-selection-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
HM_REL = "spec/contracts/hir-mir-lowering-registry.json"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "0346f2cdd417618ffa0af144a1c37569da63a4c4"
REVISION = "r62-local-trait-qualified-associated-static-selection-dynamic-trace-closure-r1"
FEATURE = "trait_qualified_associated_static_selection"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
RELATED_EXCLUSIONS = [
    "companion_capability_decomposition",
    "hir_h1_current_mir_bridge_design",
    "function_static_activation",
]
PRIOR_OVERLAYS = [
    "scalar-numeric-fixed-operator-evidence-r1.json",
    "lexical-trivia-source-root-evidence-r1.json",
    "numeric-array-shape-inferred-evidence-r1.json",
    "unified-call-tilde-evidence-r1.json",
    "member-visibility-evidence-r1.json",
    "pattern-dynamic-lowering-evidence-r1.json",
    "pattern-match-ownership-split-evidence-r1.json",
    "pattern-clause-exhaustiveness-evidence-r1.json",
]
RULE_IDS = [f"TQASSTC-R{index:03d}" for index in range(1, 15)]
CASE_IDS = [f"TQASSTC-AC-{index:03d}" for index in range(1, 14)]
AUDIT_IDS = ["TYPE1", "VALUE1", "FUNCTION1", "SUBSTITUTION1", "INHERITED1", "CALLABLE1", "LINK1", "EXPLICIT1", "NOTFOUND1", "KIND1", "RESIDUE1", "RUNTIME1", "VALUEPROFILE1"]
CASE_EXPECTATIONS = [
    ("POSITIVE", "SELECT_EXACT_ASSOCIATED_TYPE_THEN_NOMINAL_TYPE_SIDE_MEMBER", None),
    ("POSITIVE", "DIRECT_DECL_STATIC_REF_TOTAL_PROJECTION", None),
    ("POSITIVE", "ORDINARY_TRAIT_WITNESS_STATIC_REF_DIRECT_SYMBOL_INVOKE", None),
    ("BOUNDARY", "DISTINCT_SELECTION_IDS_WITH_EXACT_SUBSTITUTION_RESIDUE", None),
    ("BOUNDARY", "PRESERVE_PARENT_CONFORMANCE_AND_WITNESS_IDENTITY", None),
    ("BOUNDARY", "ONE_TO_ONE_IMPLEMENTATION_TO_CALLABLE_IMPLEMENTATION_MAPPING", None),
    ("BOUNDARY", "UNCHANGED_SEMANTIC_SELECTION_AND_DIRECT_SYMBOL_TARGET", None),
    ("REJECT", "REJECT_BEFORE_HIR_REQUIRING_EXPLICIT_TRAIT_QUALIFICATION", "TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION"),
    ("REJECT", "REJECT_MISSING_ITEM_BEFORE_HIR", "TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND"),
    ("REJECT", "REJECT_TERMINAL_ITEM_KIND_MISMATCH_BEFORE_HIR", "TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH"),
    ("REJECT", "REJECT_INCOMPLETE_RESIDUE_BEFORE_MIR", "TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE"),
    ("REJECT", "REJECT_RUNTIME_DISCOVERY_OR_RECONSTRUCTION", "TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN"),
    ("REJECT", "REJECT_VALUE_PROFILE_BEFORE_STATIC_REF", "ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED"),
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def disposition_counts(values: dict[tuple[str, str, str | None], str]) -> tuple[int, int, int, int]:
    counts = Counter(values.values())
    return tuple(counts[key] for key in ("BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE", "APPLICABLE_BLOCKED_BY_GAP"))


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    *,
    validate_schema: bool = True,
    trace_rows_override: list[dict[str, Any]] | None = None,
    hm_override: dict[str, Any] | None = None,
    metadata_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    if validate_schema:
        try:
            import jsonschema

            jsonschema.Draft202012Validator(load(root / CONTRACT_SCHEMA_REL)).validate(contract)
            jsonschema.Draft202012Validator(load(root / OVERLAY_SCHEMA_REL)).validate(overlay)
        except ImportError:
            pass
        except Exception as exc:
            errors.append(f"JSON_SCHEMA:{exc}")

    for value, prefix in ((contract, "CONTRACT"), (overlay, "OVERLAY")):
        require(value.get("canonical_baseline_commit") == BASELINE, f"{prefix}_BASELINE")
        require(value.get("local_predecessor_commit") == PREDECESSOR, f"{prefix}_PREDECESSOR")
        require(value.get("revision") == REVISION, f"{prefix}_REVISION")
        require(value.get("feature_ids") == [FEATURE], f"{prefix}_FEATURE")
    require(contract.get("schema") == "deeplus.trait-qualified-associated-static-selection-trace-closure/r1", "CONTRACT_SCHEMA_ID")
    require(contract.get("candidate_status") == "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE", "CONTRACT_STATUS")
    require(contract.get("language_status") == "STABLE_DESIGN", "CONTRACT_LANGUAGE_STATUS")
    require(contract.get("source_activation") == "none" and contract.get("current_binding") is False, "CONTRACT_NONACTIVATING")
    require(overlay.get("schema") == "deeplus.trait-qualified-associated-static-selection-evidence/r1", "OVERLAY_SCHEMA_ID")
    require(overlay.get("candidate_status") == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY", "OVERLAY_STATUS")

    expected_scope = {
        "transitioned_cells": [{
            "feature_id": FEATURE,
            "stage": "DYNAMIC_LOWERING",
            "outcome": None,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "predecessor_gap_id": "IR-XCUT-P1-054",
            "disposition": "BOUND_DIRECT",
        }],
        "transitioned_cell_count": 1,
        "other_feature_transition_count": 0,
        "other_target_cell_transition_count": 0,
    }
    require(contract.get("scope_fence") == expected_scope, "SCOPE_EXACT_ONE_CELL")

    descriptor = contract.get("descriptor_repair", {})
    require(descriptor.get("identity_kind") == "TraitAssociatedStaticSelectionId", "DESCRIPTOR_IDENTITY_KIND")
    require(descriptor.get("identity_role") == "CLOSED_STATIC_SELECTION_DESCRIPTOR_ID", "DESCRIPTOR_IDENTITY_ROLE")
    require(descriptor.get("required_fields") == ["TraitId", "RequirementId", "ConformanceId", "TraitWitnessId", "ImplementationId", "SubstitutionId", "ResponsibilityId"] and descriptor.get("required_field_count") == 7, "DESCRIPTOR_EXACT_SEVEN_FIELDS")
    require(descriptor.get("item_kinds") == ["associated_type", "associated_value", "associated_function"], "DESCRIPTOR_ITEM_KINDS")
    require(descriptor.get("hir_binding") == "decl_id_or_call_head_id_REFERENCES_TraitAssociatedStaticSelectionId", "DESCRIPTOR_HIR_BINDING")
    require(descriptor.get("mir_binding") == "STATIC_REF.static_identity_id_REFERENCES_TraitAssociatedStaticSelectionId", "DESCRIPTOR_MIR_BINDING")
    require(descriptor.get("selected_identity_erased_before_mir") is False and descriptor.get("runtime_reconstruction_count") == 0 and descriptor.get("machine_address_identity_input_count") == 0, "DESCRIPTOR_NO_ERASURE_OR_RECONSTRUCTION")
    mapping = descriptor.get("implementation_callable_mapping", {})
    require(mapping == {"source_field": "ImplementationId", "hir_projection": "CallableImplementationId", "cardinality": "ONE_TO_ONE", "complete_before_hir_emission": True, "injective_within_compilation_identity_domain": True, "independent_candidate_selection_count": 0}, "DESCRIPTOR_CALLABLE_MAPPING_EXACT")

    kinds = contract.get("associated_item_kind_lowering", {})
    require(kinds.get("associated_type") == {"runtime_operation_count": 0, "composition_order": ["EXACT_ASSOCIATED_TYPE_SELECTION", "NORMALIZE_SELECTED_TYPE", "NOMINAL_TYPE_SIDE_SELECTION"], "trait_or_extension_fallback_count": 0}, "LOWERING_ASSOCIATED_TYPE_EXACT")
    require(kinds.get("associated_value") == {"hir_form": "ResolvedRef::DirectDecl(TraitAssociatedStaticSelectionId)", "lowering_rows": ["HM-LR-REF-002", "HM-LR-TOP-002"], "operation_sequence": ["STATIC_REF", "TOTAL_PROJECTION"], "invoke_count": 0, "static_material_profile": ["IMMUTABLE", "SHAREABLE", "NO_DROP", "AUTHORITY_FREE", "ACYCLIC", "STATICALLY_MATERIALIZABLE"]}, "LOWERING_ASSOCIATED_VALUE_EXACT")
    require(kinds.get("associated_function") == {"hir_mode_target_pair": "ORDINARY::TRAIT_WITNESS", "hir_call_head": "TraitAssociatedStaticSelectionId", "lowering_rows": ["HM-LR-CALL-003"], "operation_sequence": ["STATIC_REF", "INVOKE"], "direct_symbol_input": ["CallableImplementationId", "SubstitutionId", "ResponsibilityId"], "semantic_target_rewrite_count": 0}, "LOWERING_ASSOCIATED_FUNCTION_EXACT")

    alignment = contract.get("existing_operation_alignment", {})
    require(alignment == {"reused_rows": ["HM-LR-REF-002", "HM-LR-TOP-002", "HM-LR-CALL-003"], "reused_operations": ["STATIC_REF", "TOTAL_PROJECTION"], "reused_terminators": ["INVOKE"], "static_ref_semantic_operation_id": "DM-SEMOP-STATIC-REF-R1", "new_hir_node_count": 0, "new_mir_operation_kind_count": 0, "new_mir_terminator_kind_count": 0, "new_runtime_service_count": 0}, "OPERATION_ALIGNMENT_EXACT")
    hm = hm_override or load(root / HM_REL)
    hm_rows = {row.get("row_id"): row for row in hm.get("rows", []) if row.get("row_id") in set(alignment.get("reused_rows", []))}
    require(set(hm_rows) == {"HM-LR-REF-002", "HM-LR-TOP-002", "HM-LR-CALL-003"}, "HM_REUSED_ROWS_EXIST")
    require(all(row.get("profile_gate") == "CURRENT" for row in hm_rows.values()), "HM_REUSED_ROWS_CURRENT")
    require([item.get("operation_kind") for item in hm_rows.get("HM-LR-REF-002", {}).get("operation_plan", [])] == ["STATIC_REF"], "HM_REF_STATIC_REF")
    require([item.get("operation_kind") for item in hm_rows.get("HM-LR-TOP-002", {}).get("operation_plan", [])] == ["TOTAL_PROJECTION"], "HM_PROJECTION_EXACT")
    require([item.get("operation_kind") for item in hm_rows.get("HM-LR-CALL-003", {}).get("operation_plan", [])] == ["STATIC_REF"] and [item.get("terminator_kind") for item in hm_rows.get("HM-LR-CALL-003", {}).get("terminator_plan", [])] == ["INVOKE"], "HM_CALL_STATIC_REF_INVOKE")

    zero = contract.get("zero_runtime_contract", {})
    zero_keys = ["runtime_witness_lookup_count", "candidate_enumeration_count", "candidate_ranking_count", "provider_search_count", "fallback_count", "source_import_use_link_order_winner_count", "expected_result_selection_count", "implicit_conversion_selection_count", "specialization_count", "child_local_witness_replacement_count", "activation_trigger_count", "new_commit_event_count", "runtime_identity_reconstruction_count", "machine_address_identity_input_count"]
    require(set(zero) == set(zero_keys) and all(zero.get(key) == 0 for key in zero_keys), "ZERO_RUNTIME_CONTRACT_EXACT")
    require(contract.get("diagnostic_fence") == {"active_diagnostics": ["TRAIT_ASSOCIATED_STATIC_REQUIRES_EXPLICIT_QUALIFICATION", "TRAIT_ASSOCIATED_STATIC_ITEM_NOT_FOUND", "TRAIT_ASSOCIATED_STATIC_ITEM_KIND_MISMATCH", "TRAIT_ASSOCIATED_STATIC_IDENTITY_RESIDUE_INCOMPLETE", "TRAIT_ASSOCIATED_STATIC_RUNTIME_LOOKUP_FORBIDDEN", "ASSOCIATED_STATIC_VALUE_PROFILE_NOT_ADMITTED"], "active_diagnostic_count": 6, "new_diagnostic_count": 0}, "DIAGNOSTIC_FENCE_EXACT")
    require(contract.get("out_of_scope_follow_up") == {"catalog_spelling": "TRAIT_ASSOCIATED_STATIC_AMBIGUOUS", "used_as_r62_evidence": False, "disposition": "OUT_OF_SCOPE_CATALOG_COHERENCE_FOLLOW_UP", "blocks_dynamic_trace_closure": False}, "AMBIGUOUS_DIAGNOSTIC_EXCLUDED")

    rules = contract.get("rules", [])
    require([row.get("rule_id") for row in rules] == RULE_IDS, "RULE_IDS_EXACT_14")
    require(all(isinstance(row.get("text"), str) and row.get("text") for row in rules), "RULE_TEXTS_NONEMPTY")
    cases = contract.get("acceptance_cases", [])
    require([row.get("case_id") for row in cases] == CASE_IDS, "CASE_IDS_EXACT_13")
    require([row.get("audit_case_id") for row in cases] == AUDIT_IDS, "CASE_AUDIT_IDS_EXACT_13")
    require([(row.get("class"), row.get("expected"), row.get("diagnostic_or_null")) for row in cases] == CASE_EXPECTATIONS, "CASE_SEMANTICS_EXACT_13")
    require(all(row.get("feature_id") == FEATURE and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in cases), "CASE_FEATURE_AND_NOT_RUN")
    require(contract.get("acceptance_bindings") == {FEATURE: {"POSITIVE": CASE_IDS[:3], "BOUNDARY": CASE_IDS[3:7], "REJECT": CASE_IDS[7:]}}, "CASE_BINDINGS_EXACT_3_4_6")

    expected_key = f"R62:{FEATURE}:DYNAMIC_LOWERING:STRUCTURAL"
    require(overlay.get("evidence_entries") == [{"evidence_key": expected_key, "class": "CONTRACT_RULE_ID", "path": CONTRACT_REL, "locator_kind": "REGISTRY_ID", "locator": "TQASSTC-R006", "stage_role": "DYNAMIC_LOWERING"}], "OVERLAY_EVIDENCE_EXACT_ONE")
    require(overlay.get("bindings") == [{"feature_id": FEATURE, "stage": "DYNAMIC_LOWERING", "outcome": None, "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP", "disposition": "BOUND_DIRECT", "evidence_keys": [expected_key], "delegate_feature_id": None, "not_applicable": None}], "OVERLAY_BINDING_EXACT_ONE")
    overlay_cases = overlay.get("acceptance_cases", [])
    require(len(overlay_cases) == 13, "OVERLAY_CASES_EXACT_13")
    for index in range(13):
        row = overlay_cases[index] if index < len(overlay_cases) else {}
        expected = cases[index] if index < len(cases) else {}
        pointer = f"/acceptance_cases/{index}"
        require((row.get("case_id"), row.get("audit_case_id"), row.get("feature_id"), row.get("class"), row.get("contract_pointer")) == (expected.get("case_id"), expected.get("audit_case_id"), FEATURE, expected.get("class"), pointer), f"OVERLAY_CASE_IDENTITY:{index}")
        try:
            resolved = resolve_pointer(contract, pointer)
        except (KeyError, IndexError, TypeError, ValueError):
            resolved = None
        require(resolved == expected, f"OVERLAY_CASE_POINTER:{index}")
        require(row.get("trace_role") == "SUPPORTING_DESIGN_STATIC_NOT_STAGE_TRANSITION" and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"OVERLAY_CASE_NOT_RUN:{index}")

    expected_counts = {"feature_count": 1, "evidence_entry_count": 1, "binding_count": 1, "acceptance_case_count": 13, "acceptance_stage_transition_count": 0, "predecessor_blocked_cell_count": 1, "overlay_bound_direct_transition_count": 1, "overlay_bound_delegated_transition_count": 0, "overlay_not_applicable_transition_count": 0, "predecessor_cumulative_overlay_binding_count": 120, "post_overlay_cumulative_binding_count": 121, "predecessor_total_bound_direct_cell_count": 2457, "predecessor_total_bound_delegated_cell_count": 3, "predecessor_total_not_applicable_cell_count": 502, "predecessor_total_blocked_cell_count": 1259, "post_overlay_total_bound_direct_cell_count": 2458, "post_overlay_total_bound_delegated_cell_count": 3, "post_overlay_total_not_applicable_cell_count": 502, "post_overlay_total_blocked_cell_count": 1258, "post_overlay_missing_cell_count": 0, "post_overlay_conflict_cell_count": 0}
    require(overlay.get("counts") == expected_counts, "OVERLAY_COUNTS_EXACT")
    prior_dir = root / "spec/traceability/implementation-target-profile-r1"
    require(sum(len(load(prior_dir / rel).get("bindings", [])) for rel in PRIOR_OVERLAYS) == 120, "PRIOR_OVERLAY_BINDINGS_EXACT_120")

    rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    cells, duplicate_count = trace_cells(rows)
    require(len(rows) == 469 and len({row.get("feature_id") for row in rows}) == 469, "TRACE_ROWS_EXACT_469")
    require(len(cells) == 4221 and duplicate_count == 0, "TRACE_CELLS_EXACT_4221")
    raw = {identity: cell.get("disposition") for identity, cell in cells.items()}
    raw_counts = disposition_counts(raw)
    installed_cells, installed_duplicate_count = trace_cells(load(root / TRACE_REL))
    installed_raw = {identity: cell.get("disposition") for identity, cell in installed_cells.items()}
    require(len(installed_cells) == 4221 and installed_duplicate_count == 0, "TRACE_INSTALLED_CELLS_EXACT_4221")
    pre = dict(raw)
    require(raw.get(TARGET) in {"APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT"}, "TRACE_TARGET_PRE_OR_POST")
    pre[TARGET] = "APPLICABLE_BLOCKED_BY_GAP"
    post = dict(pre)
    post[TARGET] = "BOUND_DIRECT"
    require({identity for identity in pre if pre[identity] != post[identity]} == {TARGET}, "TRACE_ONLY_ONE_TARGET_CHANGED")
    require(all(pre[identity] == post[identity] for identity in pre if identity != TARGET), "TRACE_ALL_OTHER_CELLS_UNCHANGED")
    for feature_id in RELATED_EXCLUSIONS:
        feature_cells = [identity for identity in pre if identity[0] == feature_id]
        require(len(feature_cells) == 9 and all(pre[identity] == post[identity] for identity in feature_cells), f"TRACE_RELATED_EXCLUSION:{feature_id}")
        require(all(raw[identity] == installed_raw.get(identity) for identity in feature_cells), f"TRACE_RELATED_EXCLUSION_INSTALLED:{feature_id}")
    baseline_installed = raw_counts in {(2457, 3, 502, 1259), (2458, 3, 502, 1258)}
    metadata = metadata_override or load(root / META_REL)
    applied_paths = [row.get("path") for row in metadata.get("applied_evidence_overlays", [])]
    later_overlay_installed = OVERLAY_REL in applied_paths and raw.get(TARGET) == "BOUND_DIRECT"
    require(baseline_installed or later_overlay_installed, "TRACE_INSTALLED_BASELINE_OR_FORWARD_COMPATIBLE")
    if baseline_installed:
        require(disposition_counts(pre) == (2457, 3, 502, 1259), "TRACE_PREDECESSOR_COUNTS_EXACT")
        require(disposition_counts(post) == (2458, 3, 502, 1258), "TRACE_POST_COUNTS_EXACT")

    authority = contract.get("authority_fence", {})
    require(authority == {"new_source_surface_count": 0, "new_grammar_production_count": 0, "new_ast_identity_count": 0, "new_hir_identity_count": 0, "new_mir_operation_kind_count": 0, "new_runtime_mechanism_count": 0, "semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "m13_actions": "4_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "github_publication": "SUSPENDED", "evidence_level": "E2_STRUCTURED_STATIC"}, "AUTHORITY_FENCE_EXACT")
    guards = overlay.get("guards", {})
    require(guards == {"target_feature_count": 469, "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435", "excluded_feature_count": 254, "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7", "transitioned_cell_count": 1, "related_feature_transition_count": 0, "other_cell_transition_count": 0, "source_activation": "none", "surface_change_count": 0, "ast_identity_change_count": 0, "hir_identity_change_count": 0, "mir_operation_kind_change_count": 0, "semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "m13_actions": "4_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "github_publication": "SUSPENDED", "product_execution_receipt_count": 0, "implementation_claim": "NONE"}, "OVERLAY_GUARDS_EXACT")
    machine = contract.get("machine_acceptance", {})
    require(machine.get("feature_count") == 1 and machine.get("rule_count") == 14 and machine.get("acceptance_case_count") == 13, "MACHINE_CARDINALITIES")
    require(machine.get("positive_case_count") == 3 and machine.get("boundary_case_count") == 4 and machine.get("reject_case_count") == 6, "MACHINE_CASE_CLASSES")
    require(machine.get("overlay_binding_count") == 1 and machine.get("identity_residue_field_count") == 7 and machine.get("reused_lowering_row_count") == 3, "MACHINE_BINDING_IDENTITY_ROWS")
    require(all(machine.get(key) == 0 for key in ("new_hir_identity_count", "new_mir_operation_kind_count", "runtime_lookup_count", "fallback_count", "provider_search_count", "order_winner_count", "specialization_count", "child_replacement_count", "activation_trigger_count", "other_feature_transition_count", "other_target_cell_transition_count", "product_executed_count")), "MACHINE_ZERO_GUARDS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    overlay = load(root / OVERLAY_REL)
    errors = validate(root, overlay, contract)
    print(json.dumps({"schema": "deeplus.trait-qualified-associated-static-selection-trace-validation-receipt/r1", "result": "PASS" if not errors else "FAIL", "feature_count": 1, "binding_count": 1, "acceptance_case_count": 13, "projected_counts": {"bound_direct": 2458, "bound_delegated": 3, "not_applicable": 502, "applicable_blocked": 1258, "missing": 0, "conflict": 0}, "product_execution": "15_OF_15_NOT_RUN", "github_publication": "SUSPENDED", "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
