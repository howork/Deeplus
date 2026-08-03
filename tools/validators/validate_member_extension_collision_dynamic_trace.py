#!/usr/bin/env python3
"""Validate the bounded R72 member/extension-collision dynamic non-emission.

This validator is design-static.  The target is a checker rejection, so the
dynamic stage is closed only when no selected reference, HIR call plan, MIR
row, xVM opcode, runtime-ABI payload/helper, or Cranelift projection exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "d54633b10c1b92bcd2445afc9906ecf9bafec5c9"
REVISION = "r72-local-member-extension-collision-dynamic-trace-closure-r1"
FEATURE = "member_extension_collision_error_policy"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
REASON = "NA_DYNAMIC_REJECTED_BEFORE_LOWERING"
AUTHORITY = "MIR_RUNTIME_AUTHORITY"
EVIDENCE_ID = "EV-879fcccb6c75f3f07a0d69202e8a77ab9cff9054049dfae8b7796d3865ea0374"
NON_TARGET_COUNT = 4220
NON_TARGET_SHA256 = "3cdbe4a509df453151f7e4900610acf2acbb6dfe0a8734f52e375a86082299e2"
R73_REVISION = "r73-local-member-extension-collision-conformance-trace-closure-r1"
R73_PREDECESSOR = "ab1ffd86db91d2b3b93e7c15e43829a7aa4704d3"
R73_BOUNDARY_TARGET = (FEATURE, "CONFORMANCE_TESTS", "BOUNDARY")
R73_REJECT_TARGET = (FEATURE, "CONFORMANCE_TESTS", "REJECT")
R73_BOUNDARY_EVIDENCE_ID = "EV-7af9345ab4c98882b2af77fc1814fc0352298f5d5f4dd9d4df357abc824c0c3f"
R73_REJECT_EVIDENCE_ID = "EV-ee837f7a965f93d9d84ad03a394d443692b235c6715b00ab2e748d5dbaf7850e"
R73_OVERLAY = "spec/traceability/implementation-target-profile-r1/member-extension-collision-conformance-evidence-r1.json"
R73_TRIPLE_EXCLUSION_COUNT = 4218
R73_TRIPLE_EXCLUSION_SHA256 = "b7992b83d769cbaa0f2123afbe012732483101411e24fc4f5d924c7db3410a30"
R74_REVISION = "r74-local-member-extension-collision-diagnostic-trace-closure-r1"
R74_PREDECESSOR = "f6581b6fba8f0f48e8b3ac2ea893298e7713d51d"
R74_TARGET = (FEATURE, "DIAGNOSTICS", None)
R74_EVIDENCE_REFS = [
    "EV-55d02c2cea739b77d7d95070b34e6b350f4aa3b3c0b838597263a576b85115fa",
    "EV-c3f43ca9fc5692e6da578ae1a0701cc340951ff85144c9263e69c60a0d358bb4",
]
R74_QUAD_EXCLUSION_COUNT = 4217
R74_QUAD_EXCLUSION_SHA256 = "478376c682a3556f09b3b26aec31390e760fa6196f4cb78ec44e43c56c96d93e"

CONTRACT = "spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json"
CONTRACT_SCHEMA = "schemas/language/member-extension-collision-dynamic-trace-closure-r1.schema.json"
FIXTURE = "tests/fixtures/current/member-extension-collision-dynamic-trace-closure-r1.json"
FIXTURE_SCHEMA = "schemas/language/member-extension-collision-dynamic-trace-closure-fixtures-r1.schema.json"
OVERLAY = "spec/traceability/implementation-target-profile-r1/member-extension-collision-dynamic-evidence-r1.json"
OVERLAY_SCHEMA = "schemas/language/member-extension-collision-dynamic-evidence-r1.schema.json"
ROWS = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
TRACE_SCHEMA = "schemas/language/implementation-target-traceability-r1.schema.json"
R71_CONTRACT = "spec/contracts/method-extension-resolution-dynamic-trace-closure-r1.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
LOWERING = "spec/contracts/hir-mir-lowering-registry.json"
MACHINE = "spec/contracts/mir-machine-registry.json"
RUNTIME_ABI = "spec/contracts/internal-runtime-abi-r1.json"
CRANELIFT = "spec/contracts/cranelift-backend-current.json"
FRONTEND = "spec/frontend/frontend-model.json"
PREDICATES = "spec/types/predicates/chunks/part-0008.json"
DIAGNOSTICS = "spec/diagnostics/catalog/chunks/part-0011.json"
MIR_SEMANTICS = "spec/mir/semantics.md"

JSON_PATHS = (
    CONTRACT,
    CONTRACT_SCHEMA,
    FIXTURE,
    FIXTURE_SCHEMA,
    OVERLAY,
    OVERLAY_SCHEMA,
    ROWS,
    METADATA,
    TRACE_SCHEMA,
    R71_CONTRACT,
    BRIDGE,
    LOWERING,
    MACHINE,
    RUNTIME_ABI,
    CRANELIFT,
    FRONTEND,
    PREDICATES,
    DIAGNOSTICS,
)

GATES = {
    "G01": "overlay_identity_and_exact_not_applicable_reason",
    "G02": "predecessor_and_non_target_immutability_fence",
    "G03": "generated_projection_counts_and_adjacent_preservation",
    "G04": "checker_collision_terminal_and_diagnostic",
    "G05": "hir_mir_xvm_runtime_cranelift_zero_residue",
    "G06": "contract_fixture_mutation_and_governance_binding",
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
    process = subprocess.run(
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
    return json.loads(process.stdout.decode("utf-8"))


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
                duplicates += key in cells
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


def r73_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R72 and R73 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key not in {TARGET, R73_BOUNDARY_TARGET, R73_REJECT_TARGET}
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def r74_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R72-R74 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key not in {TARGET, R73_BOUNDARY_TARGET, R73_REJECT_TARGET, R74_TARGET}
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def find_by(rows: List[Dict[str, Any]], key: str, value: str) -> Dict[str, Any]:
    return next((row for row in rows if row.get(key) == value), {})


def validate(
    root: Path,
    *,
    overrides: Optional[Mapping[str, Any]] = None,
    predecessor_rows_override: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    values = load_inputs(root)
    if overrides:
        values.update(overrides)
    errors: List[str] = []

    def value(relative: str) -> Any:
        return values[relative]

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(gate + ":" + code)

    contract = value(CONTRACT)
    fixture = value(FIXTURE)
    overlay = value(OVERLAY)
    rows = value(ROWS)
    metadata = value(METADATA)
    r71 = value(R71_CONTRACT)
    bridge = value(BRIDGE)
    lowering = value(LOWERING)
    machine = value(MACHINE)
    runtime_abi = value(RUNTIME_ABI)
    cranelift = value(CRANELIFT)
    frontend = value(FRONTEND)
    predicates = value(PREDICATES)
    diagnostics = value(DIAGNOSTICS)

    for schema_path in (
        CONTRACT_SCHEMA,
        FIXTURE_SCHEMA,
        OVERLAY_SCHEMA,
        TRACE_SCHEMA,
    ):
        require(
            value(schema_path).get("$schema")
            == "https://json-schema.org/draft/2020-12/schema",
            "G01",
            "SCHEMA_DIALECT",
        )
    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        for document_path, schema_path in (
            (CONTRACT, CONTRACT_SCHEMA),
            (FIXTURE, FIXTURE_SCHEMA),
            (OVERLAY, OVERLAY_SCHEMA),
            (METADATA, TRACE_SCHEMA),
        ):
            try:
                schema = value(schema_path)
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema.Draft202012Validator(schema).validate(value(document_path))
            except Exception as exc:
                errors.append("G01:JSON_SCHEMA_BINDING:" + type(exc).__name__)

    # G01: one exact structured-static rule binds one exact static rejection NA.
    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    entry = entries[0] if len(entries) == 1 else {}
    binding = bindings[0] if len(bindings) == 1 else {}
    key = entry.get("evidence_key")
    detail = binding.get("not_applicable") or {}
    require(
        overlay.get("revision") == REVISION
        and overlay.get("canonical_baseline_commit") == CANONICAL
        and overlay.get("local_predecessor_commit") == PREDECESSOR
        and overlay.get("feature_ids") == [FEATURE],
        "G01",
        "OVERLAY_IDENTITY",
    )
    require(
        len(entries) == 1
        and entry.get("class") == "CONTRACT_RULE_ID"
        and entry.get("path") == R71_CONTRACT
        and entry.get("locator_kind") == "REGISTRY_ID"
        and entry.get("locator") == "MERTC-R003"
        and entry.get("stage_role") == "DYNAMIC_LOWERING"
        and evidence_id(entry) == EVIDENCE_ID,
        "G01",
        "EXACT_PRE_HIR_REJECTION_EVIDENCE",
    )
    require(
        len(bindings) == 1
        and binding.get("feature_id") == FEATURE
        and binding.get("stage") == "DYNAMIC_LOWERING"
        and binding.get("outcome") is None
        and binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP"
        and binding.get("disposition") == "NOT_APPLICABLE"
        and binding.get("evidence_keys") == [key]
        and binding.get("delegate_feature_id") is None,
        "G01",
        "ONE_NOT_APPLICABLE_BINDING",
    )
    require(
        detail.get("reason_code") == REASON
        and detail.get("authority_boundary") == AUTHORITY
        and detail.get("justification_evidence_keys") == [key]
        and bool(detail.get("rationale")),
        "G01",
        "EXACT_REASON_AND_AUTHORITY",
    )

    # G02: exactly one predecessor cell changes; the other 4,220 are byte-semantic exact.
    before_rows = predecessor_rows_override or predecessor_rows(root)
    before_cells, before_duplicates = trace_cells(before_rows)
    before_target = before_cells.get(TARGET, {})
    count, digest = non_target_digest(before_cells)
    require(
        before_duplicates == 0
        and before_target.get("disposition") == "APPLICABLE_BLOCKED_BY_GAP"
        and before_target.get("blocked_gap_ids") == ["IR-XCUT-P1-054"],
        "G02",
        "PREDECESSOR_TARGET_EXACT",
    )
    require(
        count == NON_TARGET_COUNT and digest == NON_TARGET_SHA256,
        "G02",
        "NON_TARGET_4220_EXACT",
    )

    # G03: generated trace projection and all adjacent cells are preserved.
    current_cells, current_duplicates = trace_cells(rows)
    target = current_cells.get(TARGET, {})
    current_count, current_digest = non_target_digest(current_cells)
    generated_detail = target.get("not_applicable") or {}
    require(
        current_duplicates == 0
        and target.get("disposition") == "NOT_APPLICABLE"
        and target.get("evidence_refs") == []
        and target.get("delegate_feature_id") is None
        and target.get("blocked_gap_ids") == []
        and generated_detail.get("reason_code") == REASON
        and generated_detail.get("authority_boundary") == AUTHORITY
        and generated_detail.get("justification_evidence_refs") == [EVIDENCE_ID],
        "G03",
        "GENERATED_TARGET_EXACT",
    )
    applied = metadata.get("applied_evidence_overlays", [])
    applied_paths = [row.get("path") for row in applied]
    registry = metadata.get("evidence_registry", [])
    derived = metadata.get("derived_counts", {})
    registered = [row for row in registry if row.get("evidence_id") == EVIDENCE_ID]
    r73_successor = (
        metadata.get("revision") == R73_REVISION
        and metadata.get("local_predecessor_commit") == R73_PREDECESSOR
        and applied_paths[-2:] == [OVERLAY, R73_OVERLAY]
    )
    r74_successor = (
        metadata.get("revision") == R74_REVISION
        and metadata.get("local_predecessor_commit") == R74_PREDECESSOR
        and applied_paths[-2:] == [OVERLAY, R73_OVERLAY]
    )
    require(
        (
            r74_successor
            and r74_successor_non_target_digest(current_cells)
            == (R74_QUAD_EXCLUSION_COUNT, R74_QUAD_EXCLUSION_SHA256)
        )
        or (
            r73_successor
            and r73_successor_non_target_digest(current_cells)
            == (R73_TRIPLE_EXCLUSION_COUNT, R73_TRIPLE_EXCLUSION_SHA256)
        )
        or (
            not (r73_successor or r74_successor)
            and current_count == NON_TARGET_COUNT
            and current_digest == NON_TARGET_SHA256
        ),
        "G03",
        "GENERATED_NON_TARGET_SUCCESSOR_EXACT",
    )
    require(
        metadata.get("canonical_baseline_commit") == CANONICAL
        and (
            (
                metadata.get("revision") == REVISION
                and metadata.get("local_predecessor_commit") == PREDECESSOR
                and len(applied) == 18
                and applied_paths[-1:] == [OVERLAY]
                and sum(row.get("binding_count", 0) for row in applied) == 134
                and len(registry) == 3146
            )
            or (
                (r73_successor or r74_successor)
                and len(applied) == 19
                and sum(row.get("binding_count", 0) for row in applied) == 136
                and len(registry) == 3148
            )
        )
        and len(registered) == 1,
        "G03",
        "GENERATED_METADATA_EXACT",
    )
    if r73_successor or r74_successor:
        boundary = current_cells.get(R73_BOUNDARY_TARGET, {})
        reject = current_cells.get(R73_REJECT_TARGET, {})
        successor_count, successor_digest = r73_successor_non_target_digest(
            current_cells
        )
        require(
            boundary.get("disposition") == "BOUND_DIRECT"
            and boundary.get("evidence_refs") == [R73_BOUNDARY_EVIDENCE_ID]
            and boundary.get("delegate_feature_id") is None
            and boundary.get("not_applicable") is None
            and boundary.get("blocked_gap_ids") == []
            and reject.get("disposition") == "BOUND_DIRECT"
            and reject.get("evidence_refs") == [R73_REJECT_EVIDENCE_ID]
            and reject.get("delegate_feature_id") is None
            and reject.get("not_applicable") is None
            and reject.get("blocked_gap_ids") == [],
            "G03",
            "R73_SUCCESSOR_TARGETS_EXACT",
        )
    if r74_successor:
        r74_target = current_cells.get(R74_TARGET, {})
        require(
            r74_target.get("disposition") == "BOUND_DIRECT"
            and r74_target.get("evidence_refs") == R74_EVIDENCE_REFS
            and r74_target.get("delegate_feature_id") is None
            and r74_target.get("not_applicable") is None
            and r74_target.get("blocked_gap_ids") == [],
            "G03",
            "R74_SUCCESSOR_TARGET_EXACT",
        )
        require(
            (
                r74_successor
                and r74_successor_non_target_digest(current_cells)
                == (R74_QUAD_EXCLUSION_COUNT, R74_QUAD_EXCLUSION_SHA256)
            )
            or (
                r73_successor
                and successor_count == R73_TRIPLE_EXCLUSION_COUNT
                and successor_digest == R73_TRIPLE_EXCLUSION_SHA256
            ),
            "G03",
            "R73_R74_SUCCESSOR_OTHER_EXACT",
        )
    require(
        (
            derived.get("bound_direct_cells"),
            derived.get("bound_delegated_cells"),
            derived.get("not_applicable_cells"),
            derived.get("applicable_blocked_cells"),
        )
        == (
            (2470, 4, 502, 1245)
            if r74_successor
            else (2469, 4, 503, 1245)
            if r73_successor
            else (2467, 4, 503, 1247)
        )
        and derived.get("missing_cells") == 0
        and derived.get("conflict_cells") == 0,
        "G03",
        "GENERATED_COUNTS_EXACT",
    )

    # G04: the integrated checker owns the terminal collision and sole primary.
    collision = frontend.get("r4_name_resolution_module_contract", {}).get(
        "member_extension_collision", {}
    )
    predicate = find_by(predicates, "predicate_id", "MemberExtensionCollisionRejected")
    diagnostic = find_by(diagnostics, "diagnostic_id", "MEMBER_EXTENSION_COLLISION")
    r71_owner = r71.get("static_resolution_owner", {})
    r71_diag = r71.get("diagnostic_fence", {})
    require(
        collision.get("ordinary_selector_both_domains_nonempty") == "REJECT"
        and collision.get("selected_count") == 0
        and collision.get("primary_diagnostic") == "MEMBER_EXTENSION_COLLISION"
        and collision.get("source_import_or_activation_order_winner") is False,
        "G04",
        "FRONTEND_COLLISION_TERMINAL",
    )
    require(
        predicate.get("algorithm_owner") == "integrated_checker"
        and predicate.get("active_primary_diagnostic") == "MEMBER_EXTENSION_COLLISION"
        and predicate.get("secondary_diagnostics") == []
        and "selected_count = 0" in predicate.get("success_result", "")
        and predicate.get("emission_eligible") is True
        and predicate.get("product_support") == "NOT_RUN",
        "G04",
        "CHECKER_PREDICATE_EXACT",
    )
    require(
        diagnostic.get("diagnostic_status") == "active"
        and diagnostic.get("severity") == "error"
        and diagnostic.get("stage") == "checker"
        and diagnostic.get("emission_domain") == "source"
        and diagnostic.get("product_support") == "NOT_RUN"
        and r71_owner.get("ordinary_both_domains_nonempty")
        == "REJECT_MEMBER_EXTENSION_COLLISION"
        and r71_owner.get("selected_count_on_collision") == 0
        and "MEMBER_EXTENSION_COLLISION"
        in r71_diag.get("static_owner_diagnostics", []),
        "G04",
        "SOLE_ACTIVE_PRIMARY_AND_R71_OWNER",
    )

    # G05: a rejected selection has no executable residue in any downstream lane.
    canonical_hir = bridge.get("canonical_hir_contract", {})
    coverage = lowering.get("coverage_contract", {})
    mir_text = (root / MIR_SEMANTICS).read_text(encoding="utf-8")
    r71_residue = r71.get("runtime_backend_residue_fence", {})
    require(
        canonical_hir.get("unresolved_variant_count") == 0
        and canonical_hir.get("candidate_set_variant_count") == 0
        and canonical_hir.get("invalid_node_count") == 0
        and canonical_hir.get("runtime_string_to_static_identity_conversion_count") == 0
        and coverage.get("pre_hir_rejection_row_count") == 0
        and "produces no\nselected reference or MIR" in mir_text,
        "G05",
        "NO_SELECTED_REF_HIR_OR_LOWERING_ROW",
    )
    require(
        all(
            r71_residue.get(field) == 0
            for field in (
                "runtime_extension_set_lookup_count",
                "runtime_extension_member_lookup_count",
                "runtime_provider_lookup_count",
                "runtime_selector_string_lookup_count",
                "xvm_new_opcode_count",
                "internal_runtime_new_selector_payload_count",
                "internal_runtime_new_helper_count",
                "cranelift_reselection_count",
                "address_or_link_order_winner_count",
                "target_identity_leak_count",
            )
        )
        and cranelift.get("mir_projection", {}).get("input") == "Verified<DeeplusMir>"
        and cranelift.get("mir_projection", {}).get("clif_is_semantic_authority") is False
        and cranelift.get("mir_projection", {}).get("symbol_or_link_order_selects_semantics") is False
        and runtime_abi.get("helper_registry", {}).get("unlisted_helper_fallback")
        is False
        and machine.get("semantic_operation_contract", {}).get("closed_set") is True,
        "G05",
        "DOWNSTREAM_ZERO_RESIDUE_AUTHORITY",
    )

    # G06: bind the R72 contract, nine cases, fourteen mutations, and governance.
    target_contract = contract.get("target_cell", {})
    static = contract.get("static_collision_owner", {})
    noncollision = contract.get("noncollision_boundary", {})
    diagnostic_fence = contract.get("diagnostic_fence", {})
    pre_hir = contract.get("pre_hir_rejection_boundary", {})
    residue = contract.get("runtime_backend_residue_fence", {})
    r71_preservation = contract.get("r71_preservation", {})
    authority = contract.get("authority_fence", {})
    machine_acceptance = contract.get("machine_acceptance", {})
    require(
        contract.get("revision") == REVISION
        and contract.get("canonical_baseline_commit") == CANONICAL
        and contract.get("local_predecessor_commit") == PREDECESSOR
        and contract.get("feature_id") == FEATURE
        and target_contract.get("stage") == "DYNAMIC_LOWERING"
        and target_contract.get("predecessor_disposition")
        == "APPLICABLE_BLOCKED_BY_GAP"
        and target_contract.get("predecessor_gap_id") == "IR-XCUT-P1-054"
        and target_contract.get("disposition") == "NOT_APPLICABLE"
        and target_contract.get("delegate_feature_id") is None
        and (target_contract.get("not_applicable") or {}).get("reason_code") == REASON
        and (target_contract.get("not_applicable") or {}).get("authority_boundary")
        == AUTHORITY,
        "G06",
        "CONTRACT_IDENTITY_AND_TARGET",
    )
    require(
        static.get("owner") == "integrated_checker"
        and static.get("selector_kind") == "ORDINARY"
        and static.get("nominal_and_active_extension_sets_collected_independently")
        is True
        and static.get("both_domains_nonempty")
        == "REJECT_MEMBER_EXTENSION_COLLISION"
        and static.get("within_domain_ranking_before_collision") is False
        and static.get("selected_count_on_collision") == 0
        and static.get("source_import_use_or_activation_order_winner_count") == 0
        and static.get("generic_or_overload_winner_selected_by_this_contract_count")
        == 0
        and noncollision.get("one_domain_empty")
        == "ADMIT_AND_DEFER_TO_EXISTING_DOMAIN_OWNER"
        and noncollision.get("qualified_selector_within_domain_winner_owned_by_this_contract")
        is False
        and noncollision.get("runtime_behavior_owned_by_this_feature") is False,
        "G06",
        "CONTRACT_STATIC_REJECTION_EXACT",
    )
    require(
        all(
            pre_hir.get(field) == 0
            for field in (
                "selected_member_count",
                "selected_extension_count",
                "hir_call_plan_count",
                "canonical_hir_node_count",
                "recovery_hir_count",
                "runtime_fallback_count",
            )
        )
        and all(
            residue.get(field) == 0
            for field in (
                "mir_operation_count",
                "mir_terminator_count",
                "xvm_instruction_count",
                "runtime_selector_payload_count",
                "runtime_provider_lookup_count",
                "runtime_helper_call_count",
                "cranelift_instruction_count",
                "cranelift_reselection_count",
                "address_or_link_order_winner_count",
            )
        )
        and diagnostic_fence.get("sole_active_primary")
        == "MEMBER_EXTENSION_COLLISION"
        and diagnostic_fence.get("secondary_diagnostics") == []
        and diagnostic_fence.get("same_stage_generic_fallback_winner_count") == 0
        and diagnostic_fence.get("recovery_admitted_hir_count") == 0
        and diagnostic_fence.get("new_diagnostic_count") == 0,
        "G06",
        "CONTRACT_ZERO_RESIDUE_EXACT",
    )
    require(
        r71_preservation.get("contract") == R71_CONTRACT
        and r71_preservation.get("preserved_rule") == "MERTC-R003"
        and r71_preservation.get("method_extension_resolution_dynamic_disposition")
        == "BOUND_DELEGATED"
        and r71_preservation.get("method_extension_resolution_delegate_feature_id")
        == "unified_call_expression_and_tilde_modes"
        and r71_preservation.get("selected_call_lowering_change_count") == 0
        and r71_preservation.get("r71_transition_count") == 0
        and all(
            row.get("r72_transition_count") == 0
            for row in contract.get("preserved_adjacent_ownership", [])
        )
        and len(contract.get("preserved_adjacent_ownership", [])) == 4,
        "G06",
        "R71_AND_ADJACENT_OWNERSHIP_PRESERVED",
    )
    case_ids = [row.get("case_id") for row in contract.get("acceptance_cases", [])]
    fixture_case_ids = [row.get("case_id") for row in fixture.get("acceptance_oracles", [])]
    mutation_ids = [row.get("mutation_id") for row in contract.get("mutation_obligations", [])]
    fixture_mutation_ids = [row.get("mutation_id") for row in fixture.get("mutation_oracles", [])]
    expected_cases = [f"R72-MECD-ACC-{index:03d}" for index in range(1, 10)]
    expected_mutations = [f"M{index:02d}" for index in range(1, 15)]
    require(
        case_ids == fixture_case_ids == expected_cases
        and [row.get("class") for row in contract.get("acceptance_cases", [])]
        == ["POSITIVE"] * 2 + ["BOUNDARY"] * 3 + ["REJECT"] * 4
        and mutation_ids == fixture_mutation_ids == expected_mutations
        and all(
            row.get("expected") == "MUTANT_KILLED"
            for row in contract.get("mutation_obligations", [])
        ),
        "G06",
        "ACCEPTANCE_9_AND_MUTATION_14_BINDING",
    )
    require(
        machine_acceptance.get("transitioned_cell_count") == 1
        and machine_acceptance.get("other_cell_transition_count") == 0
        and machine_acceptance.get("other_atomic_cell_count") == NON_TARGET_COUNT
        and machine_acceptance.get("other_atomic_cell_sha256")
        == NON_TARGET_SHA256
        and machine_acceptance.get("selected_count_on_collision") == 0
        and machine_acceptance.get("admitted_hir_residue_count") == 0
        and machine_acceptance.get("mir_runtime_backend_residue_count") == 0
        and machine_acceptance.get("semantic_p0") == 0
        and machine_acceptance.get("feature_p1") == "22_OPEN_UNCHANGED"
        and machine_acceptance.get("m13_actions") == "4_OPEN_UNCHANGED"
        and machine_acceptance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and machine_acceptance.get("github_publication") == "SUSPENDED"
        and machine_acceptance.get("product_execution_receipt_count") == 0
        and machine_acceptance.get("implementation_claim") == "NONE"
        and all(
            authority.get(field) == 0
            for field in (
                "new_source_surface_count",
                "new_grammar_production_count",
                "new_ast_identity_count",
                "new_hir_identity_count",
                "new_mir_operation_kind_count",
                "new_mir_terminator_kind_count",
                "new_xvm_opcode_count",
                "new_runtime_helper_count",
                "new_backend_rule_count",
                "new_diagnostic_count",
                "new_p1_count",
                "closed_p1_count",
            )
        )
        and len(contract.get("rules", [])) == 13
        and [row.get("rule_id") for row in contract.get("rules", [])]
        == [f"MECDTC-R{index:03d}" for index in range(1, 14)]
        and (
            (
                r74_successor
                and r74_successor_non_target_digest(current_cells)
                == (R74_QUAD_EXCLUSION_COUNT, R74_QUAD_EXCLUSION_SHA256)
            )
            or (
                r73_successor
                and r73_successor_non_target_digest(current_cells)
                == (R73_TRIPLE_EXCLUSION_COUNT, R73_TRIPLE_EXCLUSION_SHA256)
            )
            or (
                not (r73_successor or r74_successor)
                and current_count == NON_TARGET_COUNT
                and current_digest == NON_TARGET_SHA256
            )
        ),
        "G06",
        "MACHINE_AND_GOVERNANCE_FENCE",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = validate(root)
    except (FileNotFoundError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        errors = ["INPUT:" + str(exc)]
    metadata = load(root / METADATA)
    r73_successor = metadata.get("revision") == R73_REVISION
    r74_successor = metadata.get("revision") == R74_REVISION
    receipt = {
        "schema": "deeplus.r72-member-extension-collision-dynamic-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_id": FEATURE,
        "transitioned_cell_count": 1,
        "disposition": "NOT_APPLICABLE",
        "reason_code": REASON,
        "authority_boundary": AUTHORITY,
        "projected_counts": {
            "bound_direct": 2470 if r74_successor else 2469 if r73_successor else 2467,
            "bound_delegated": 4,
            "not_applicable": 502 if r74_successor else 503,
            "applicable_blocked": 1245 if (r73_successor or r74_successor) else 1247,
        },
        "non_target_cell_count": (
            R74_QUAD_EXCLUSION_COUNT
            if r74_successor
            else R73_TRIPLE_EXCLUSION_COUNT
            if r73_successor
            else NON_TARGET_COUNT
        ),
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "gates": GATES,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
