#!/usr/bin/env python3
"""Validate the bounded R71 method/extension dynamic trace delegation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "7babf6b0d6a3c806784ef052308cf7026f3fecb2"
REVISION = "r71-local-method-extension-resolution-dynamic-trace-closure-r1"
FEATURE = "method_extension_resolution_policy"
DELEGATE = "unified_call_expression_and_tilde_modes"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
EVIDENCE_ID = "EV-8612c9785d1ec77315d24c4f6700d39e07b38f8c115155f519c698e406770b5b"
NON_TARGET_COUNT = 4220
NON_TARGET_SHA256 = "79510a1255de566d0dffe331717e2833b426ebc8ef871e07bce0d9a85e7a798a"
R72_REVISION = "r72-local-member-extension-collision-dynamic-trace-closure-r1"
R72_PREDECESSOR = "d54633b10c1b92bcd2445afc9906ecf9bafec5c9"
R72_TARGET = ("member_extension_collision_error_policy", "DYNAMIC_LOWERING", None)
R72_EVIDENCE_ID = "EV-879fcccb6c75f3f07a0d69202e8a77ab9cff9054049dfae8b7796d3865ea0374"
R72_OVERLAY = "spec/traceability/implementation-target-profile-r1/member-extension-collision-dynamic-evidence-r1.json"
R72_DUAL_EXCLUSION_COUNT = 4219
R72_DUAL_EXCLUSION_SHA256 = "75ccf47df040801cb0b75c34c47f85fb5ef0ef36d0d3a72ed3cf64099126f9ab"
R73_REVISION = "r73-local-member-extension-collision-conformance-trace-closure-r1"
R73_PREDECESSOR = "ab1ffd86db91d2b3b93e7c15e43829a7aa4704d3"
R73_BOUNDARY_TARGET = ("member_extension_collision_error_policy", "CONFORMANCE_TESTS", "BOUNDARY")
R73_REJECT_TARGET = ("member_extension_collision_error_policy", "CONFORMANCE_TESTS", "REJECT")
R73_BOUNDARY_EVIDENCE_ID = "EV-7af9345ab4c98882b2af77fc1814fc0352298f5d5f4dd9d4df357abc824c0c3f"
R73_REJECT_EVIDENCE_ID = "EV-ee837f7a965f93d9d84ad03a394d443692b235c6715b00ab2e748d5dbaf7850e"
R73_OVERLAY = "spec/traceability/implementation-target-profile-r1/member-extension-collision-conformance-evidence-r1.json"
R73_QUAD_EXCLUSION_COUNT = 4217
R73_QUAD_EXCLUSION_SHA256 = "74f224cc61633e22f72c0c4f480afbdbe0aab42ffa905d85496620d8740a6296"
R74_REVISION = "r74-local-member-extension-collision-diagnostic-trace-closure-r1"
R74_PREDECESSOR = "f6581b6fba8f0f48e8b3ac2ea893298e7713d51d"
R74_TARGET = ("member_extension_collision_error_policy", "DIAGNOSTICS", None)
R74_EVIDENCE_REFS = [
    "EV-55d02c2cea739b77d7d95070b34e6b350f4aa3b3c0b838597263a576b85115fa",
    "EV-c3f43ca9fc5692e6da578ae1a0701cc340951ff85144c9263e69c60a0d358bb4",
]
R74_QUINT_EXCLUSION_COUNT = 4216
R74_QUINT_EXCLUSION_SHA256 = "a474ca31b207ea5f45e7606e99ec1afe4ababc7850224788922a31faa2dd1f22"

CONTRACT = "spec/contracts/method-extension-resolution-dynamic-trace-closure-r1.json"
CONTRACT_SCHEMA = "schemas/language/method-extension-resolution-dynamic-trace-closure-r1.schema.json"
FIXTURE = "tests/fixtures/current/method-extension-resolution-dynamic-trace-closure-r1.json"
FIXTURE_SCHEMA = "schemas/language/method-extension-resolution-dynamic-trace-closure-fixtures-r1.schema.json"
OVERLAY = "spec/traceability/implementation-target-profile-r1/method-extension-resolution-dynamic-evidence-r1.json"
OVERLAY_SCHEMA = "schemas/language/method-extension-resolution-dynamic-evidence-r1.schema.json"
ROWS = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
TRACE_SCHEMA = "schemas/language/implementation-target-traceability-r1.schema.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
LOWERING = "spec/contracts/hir-mir-lowering-registry.json"
MACHINE = "spec/contracts/mir-machine-registry.json"
UNIFIED = "spec/contracts/unified-call-tilde-trace-closure-r1.json"
R70_CONTRACT = "spec/contracts/static-runtime-member-boundary-trace-closure-r1.json"
RUNTIME_ABI = "spec/contracts/internal-runtime-abi-r1.json"
CRANELIFT = "spec/contracts/cranelift-backend-current.json"

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
    BRIDGE,
    LOWERING,
    MACHINE,
    UNIFIED,
    R70_CONTRACT,
    RUNTIME_ABI,
    CRANELIFT,
)

GATES = {
    "G01": "overlay_identity_and_delegate",
    "G02": "predecessor_and_non_target_fence",
    "G03": "generated_projection_and_counts",
    "G04": "unified_call_and_hir_mir_lowering",
    "G05": "runtime_backend_and_product_fence",
    "G06": "semantic_contract_fixtures_and_mutations",
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


def r72_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R71 and R72 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key not in {TARGET, R72_TARGET}
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def r73_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R71-R73 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key
        not in {TARGET, R72_TARGET, R73_BOUNDARY_TARGET, R73_REJECT_TARGET}
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def r74_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R71-R74 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key
        not in {
            TARGET,
            R72_TARGET,
            R73_BOUNDARY_TARGET,
            R73_REJECT_TARGET,
            R74_TARGET,
        }
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def lowering_row(registry: Mapping[str, Any], row_id: str) -> Mapping[str, Any]:
    return next(
        (row for row in registry.get("rows", []) if row.get("row_id") == row_id),
        {},
    )


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
    contract_schema = value(CONTRACT_SCHEMA)
    fixture = value(FIXTURE)
    fixture_schema = value(FIXTURE_SCHEMA)
    overlay = value(OVERLAY)
    overlay_schema = value(OVERLAY_SCHEMA)
    rows = value(ROWS)
    metadata = value(METADATA)
    trace_schema = value(TRACE_SCHEMA)
    bridge = value(BRIDGE)
    lowering = value(LOWERING)
    machine = value(MACHINE)
    unified = value(UNIFIED)
    r70_contract = value(R70_CONTRACT)
    runtime_abi = value(RUNTIME_ABI)
    cranelift = value(CRANELIFT)

    for schema in (contract_schema, fixture_schema, overlay_schema, trace_schema):
        require(
            schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            "G01",
            "SCHEMA_DIALECT",
        )
    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        for document, schema in (
            (contract, contract_schema),
            (fixture, fixture_schema),
            (overlay, overlay_schema),
            (metadata, trace_schema),
        ):
            try:
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema.Draft202012Validator(schema).validate(document)
            except jsonschema.exceptions.ValidationError:
                require(False, "G01", "JSON_SCHEMA_BINDING")

    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    entry = entries[0] if len(entries) == 1 else {}
    binding = bindings[0] if len(bindings) == 1 else {}
    require(
        overlay.get("revision") == REVISION
        and overlay.get("canonical_baseline_commit") == CANONICAL
        and overlay.get("local_predecessor_commit") == PREDECESSOR
        and overlay.get("feature_ids") == [FEATURE],
        "G01",
        "OVERLAY_IDENTITY",
    )
    require(
        entry.get("class") == "CONTRACT_RULE_ID"
        and entry.get("path") == UNIFIED
        and entry.get("locator_kind") == "REGISTRY_ID"
        and entry.get("locator") == "UCTC-R011"
        and entry.get("stage_role") == "DYNAMIC_LOWERING"
        and evidence_id(entry) == EVIDENCE_ID,
        "G01",
        "DELEGATE_EVIDENCE_EXACT",
    )
    require(
        binding.get("feature_id") == FEATURE
        and binding.get("stage") == "DYNAMIC_LOWERING"
        and binding.get("outcome") is None
        and binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP"
        and binding.get("disposition") == "BOUND_DELEGATED"
        and binding.get("delegate_feature_id") == DELEGATE
        and binding.get("not_applicable") is None,
        "G01",
        "BOUND_DELEGATED_EXACT",
    )

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
        "OTHER_4220_EXACT",
    )

    cells, duplicates = trace_cells(rows)
    target = cells.get(TARGET, {})
    applied = [row.get("path") for row in metadata.get("applied_evidence_overlays", [])]
    evidence_registry = {
        row.get("evidence_id"): row for row in metadata.get("evidence_registry", [])
    }
    counts = metadata.get("derived_counts", {})
    r72_successor = (
        metadata.get("revision") == R72_REVISION
        and metadata.get("local_predecessor_commit") == R72_PREDECESSOR
        and applied[-2:] == [OVERLAY, R72_OVERLAY]
    )
    r73_successor = (
        metadata.get("revision") == R73_REVISION
        and metadata.get("local_predecessor_commit") == R73_PREDECESSOR
        and applied[-3:] == [OVERLAY, R72_OVERLAY, R73_OVERLAY]
    )
    r74_successor = (
        metadata.get("revision") == R74_REVISION
        and metadata.get("local_predecessor_commit") == R74_PREDECESSOR
        and applied[-3:] == [OVERLAY, R72_OVERLAY, R73_OVERLAY]
    )
    require(
        duplicates == 0
        and target.get("disposition") == "BOUND_DELEGATED"
        and target.get("evidence_refs") == [EVIDENCE_ID]
        and target.get("delegate_feature_id") == DELEGATE
        and target.get("not_applicable") is None
        and target.get("blocked_gap_ids") == [],
        "G03",
        "GENERATED_TARGET_EXACT",
    )
    require(
        (
            (
                metadata.get("revision") == REVISION
                and metadata.get("local_predecessor_commit") == PREDECESSOR
                and applied[-1:] == [OVERLAY]
                and len(applied) == 17
                and len(evidence_registry) == 3145
            )
            or (
                r72_successor
                and len(applied) == 18
                and len(evidence_registry) == 3146
            )
            or (
                (r73_successor or r74_successor)
                and len(applied) == 19
                and len(evidence_registry) == 3148
            )
        )
        and EVIDENCE_ID in evidence_registry,
        "G03",
        "GENERATED_METADATA_EXACT",
    )
    if r72_successor or r73_successor or r74_successor:
        r72_target = cells.get(R72_TARGET, {})
        r72_detail = r72_target.get("not_applicable") or {}
        successor_count, successor_digest = (
            r74_successor_non_target_digest(cells)
            if r74_successor
            else r73_successor_non_target_digest(cells)
            if r73_successor
            else r72_successor_non_target_digest(cells)
        )
        require(
            r72_target.get("disposition") == "NOT_APPLICABLE"
            and r72_target.get("evidence_refs") == []
            and r72_target.get("delegate_feature_id") is None
            and r72_target.get("blocked_gap_ids") == []
            and r72_detail.get("reason_code")
            == "NA_DYNAMIC_REJECTED_BEFORE_LOWERING"
            and r72_detail.get("authority_boundary") == "MIR_RUNTIME_AUTHORITY"
            and r72_detail.get("justification_evidence_refs") == [R72_EVIDENCE_ID],
            "G03",
            "R72_SUCCESSOR_TARGET_EXACT",
        )
        require(
            (
                r74_successor
                and successor_count == R74_QUINT_EXCLUSION_COUNT
                and successor_digest == R74_QUINT_EXCLUSION_SHA256
            )
            or (
                r73_successor
                and successor_count == R73_QUAD_EXCLUSION_COUNT
                and successor_digest == R73_QUAD_EXCLUSION_SHA256
            )
            or (
                r72_successor
                and successor_count == R72_DUAL_EXCLUSION_COUNT
                and successor_digest == R72_DUAL_EXCLUSION_SHA256
            ),
            "G03",
            "R72_R73_SUCCESSOR_OTHER_EXACT",
        )
    if r73_successor or r74_successor:
        boundary = cells.get(R73_BOUNDARY_TARGET, {})
        reject = cells.get(R73_REJECT_TARGET, {})
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
        r74_target = cells.get(R74_TARGET, {})
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
        counts.get("bound_direct_cells")
        == (2470 if r74_successor else 2469 if r73_successor else 2467)
        and counts.get("bound_delegated_cells") == 4
        and counts.get("not_applicable_cells")
        == (502 if r74_successor else 503 if (r72_successor or r73_successor) else 502)
        and counts.get("applicable_blocked_cells")
        == (1245 if (r73_successor or r74_successor) else (1247 if r72_successor else 1248))
        and counts.get("missing_cells") == 0
        and counts.get("conflict_cells") == 0,
        "G03",
        "GENERATED_COUNTS_EXACT",
    )

    call = bridge.get("call_plan_contract", {})
    canonical = bridge.get("canonical_hir_contract", {})
    forbidden = set(canonical.get("mir_lowerer_forbidden_decisions", []))
    required_domains = {"ExtensionSetId", "ExtensionMemberId", "CallableImplementationId"}
    require(
        required_domains <= set(canonical.get("selected_identity_domains", []))
        and {
            "name_or_selector_lookup",
            "overload_ranking",
            "witness_or_extension_or_provider_search",
        }
        <= forbidden
        and "ExtensionStatic" in call.get("resolved_plan_enum", [])
        and call.get("invariants", {}).get("runtime_selector_search_count") == 0
        and "exactly once" in call.get("source_evaluation_law", ""),
        "G04",
        "HIR_CALLPLAN_STATIC_SEAL",
    )
    ordinary = lowering_row(lowering, "HM-LR-CALL-004")
    message = lowering_row(lowering, "HM-LR-CALL-008")
    require(
        ordinary.get("lowering_dispatch_key", {}).get("pair_id")
        == "ORDINARY::EXTENSION_STATIC"
        and ordinary.get("required_capability_ids")
        == ["DM-CAP-CALL-EXTENSION-STATIC-R1"]
        and [row.get("operation_kind") for row in ordinary.get("operation_plan", [])]
        == ["CONTEXT_ADAPT"]
        and [row.get("terminator_kind") for row in ordinary.get("terminator_plan", [])]
        == ["INVOKE"],
        "G04",
        "HM_LR_CALL_004_EXACT",
    )
    require(
        message.get("lowering_dispatch_key", {}).get("pair_id")
        == "MESSAGE::EXTENSION_STATIC"
        and message.get("required_capability_ids")
        == ["DM-CAP-CALL-EXTENSION-STATIC-R1", "DM-CAP-MESSAGE-MODE-R1"]
        and [row.get("operation_kind") for row in message.get("operation_plan", [])]
        == ["CONTEXT_ADAPT"]
        and [row.get("terminator_kind") for row in message.get("terminator_plan", [])]
        == ["INVOKE"],
        "G04",
        "HM_LR_CALL_008_BOUNDARY_EXACT",
    )
    unified_rule = next(
        (row for row in unified.get("rules", []) if row.get("rule_id") == "UCTC-R011"),
        {},
    )
    r70_handoff = r70_contract.get("terminal_selection_handoff", {}).get(
        "ordinary_extension_static_call", {}
    )
    require(
        bool(unified_rule)
        and unified.get("static_semantics", {}).get("runtime_selector_lookup_count") == 0
        and r70_handoff.get("owner") == FEATURE
        and r70_handoff.get("lowering_rows") == ["HM-LR-CALL-004"]
        and r70_handoff.get("operation_sequence") == ["CONTEXT_ADAPT", "INVOKE"],
        "G04",
        "UNIFIED_DELEGATE_AND_R70_HANDOFF",
    )
    capabilities = machine.get("capability_registry", machine.get("capabilities", []))
    capability = next(
        (
            row
            for row in capabilities
            if row.get("capability_id") == "DM-CAP-CALL-EXTENSION-STATIC-R1"
        ),
        {},
    )
    require(
        bool(capability)
        and capability.get("requires") == ["DM-CAP-CALL-CHANNELS-R1"]
        and capability.get("operation_kinds") == ["CONTEXT_ADAPT"],
        "G04",
        "MIR_CAPABILITY_EXACT",
    )

    residue = contract.get("runtime_backend_residue_fence", {})
    require(
        all(
            residue.get(key) == 0
            for key in (
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
        and runtime_abi.get("current_binding") is False,
        "G05",
        "RUNTIME_BACKEND_ZERO_RELOOKUP",
    )

    target_contract = contract.get("target_cell", {})
    static_owner = contract.get("static_resolution_owner", {})
    identities = contract.get("selected_identity_seal", {})
    dynamic = contract.get("dynamic_delegate", {})
    authority = contract.get("authority_fence", {})
    machine_acceptance = contract.get("machine_acceptance", {})
    require(
        contract.get("revision") == REVISION
        and contract.get("canonical_baseline_commit") == CANONICAL
        and contract.get("local_predecessor_commit") == PREDECESSOR
        and contract.get("feature_id") == FEATURE
        and target_contract.get("disposition") == "BOUND_DELEGATED"
        and target_contract.get("delegate_feature_id") == DELEGATE,
        "G06",
        "CONTRACT_IDENTITY_AND_TRANSITION",
    )
    require(
        static_owner.get("ordinary_both_domains_nonempty")
        == "REJECT_MEMBER_EXTENSION_COLLISION"
        and static_owner.get("selected_count_on_collision") == 0
        and static_owner.get("source_import_use_order_winner_count") == 0
        and static_owner.get("runtime_candidate_search_count") == 0
        and static_owner.get("dynamic_extension_dispatch_admitted") is False
        and static_owner.get("trait_witness_synthesis_count") == 0,
        "G06",
        "STATIC_OWNER_FENCE",
    )
    require(
        identities.get("required_identity_domains")
        == ["ExtensionSetId", "ExtensionMemberId", "CallableImplementationId"]
        and identities.get("identity_closed_before_mir") is True
        and identities.get("unresolved_identity_count") == 0
        and identities.get("candidate_set_residue_count") == 0
        and identities.get("selector_string_runtime_payload_count") == 0
        and identities.get("provider_name_runtime_payload_count") == 0,
        "G06",
        "EXACT_IDENTITY_SEAL",
    )
    require(
        dynamic.get("delegate_feature_id") == DELEGATE
        and dynamic.get("ordinary", {}).get("lowering_row") == "HM-LR-CALL-004"
        and dynamic.get("message", {}).get("lowering_row") == "HM-LR-CALL-008"
        and dynamic.get("ordinary", {}).get("operation_sequence")
        == ["CONTEXT_ADAPT", "INVOKE"]
        and dynamic.get("message", {}).get("operation_sequence")
        == ["CONTEXT_ADAPT", "INVOKE"]
        and dynamic.get("ordinary", {}).get("receiver_evaluation_count") == 1
        and dynamic.get("message", {}).get("receiver_evaluation_count") == 1
        and dynamic.get("context_adapt_precedes_invoke") is True
        and dynamic.get("dynamic_owner_reselection_count") == 0,
        "G06",
        "DYNAMIC_DELEGATE_EXACT",
    )
    case_ids = [row.get("case_id") for row in contract.get("acceptance_cases", [])]
    fixture_case_ids = [row.get("case_id") for row in fixture.get("acceptance_oracles", [])]
    mutation_ids = [row.get("mutation_id") for row in contract.get("mutation_obligations", [])]
    fixture_mutation_ids = [row.get("mutation_id") for row in fixture.get("mutation_oracles", [])]
    require(
        case_ids == [f"R71-MER-ACC-{index:03d}" for index in range(1, 11)]
        and fixture_case_ids == case_ids
        and mutation_ids == [f"M{index:02d}" for index in range(1, 15)]
        and fixture_mutation_ids == mutation_ids,
        "G06",
        "ACCEPTANCE_AND_MUTATION_BINDING",
    )
    require(
        machine_acceptance.get("transitioned_cell_count") == 1
        and machine_acceptance.get("bound_delegated_transition_count") == 1
        and machine_acceptance.get("other_target_cell_transition_count") == 0
        and machine_acceptance.get("rule_count") == 15
        and machine_acceptance.get("acceptance_case_count") == 10
        and machine_acceptance.get("mutation_obligation_count") == 14
        and authority.get("semantic_p0") == 0
        and authority.get("open_feature_p1") == 22
        and authority.get("open_m13_actions") == 4
        and authority.get("product_lanes", {}).get("state") == "15_OF_15_NOT_RUN"
        and authority.get("github_publication") == "SUSPENDED"
        and authority.get("execution_state") == "DESIGN_STATIC_NOT_RUN",
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
    r72_successor = metadata.get("revision") == R72_REVISION
    r74_successor = metadata.get("revision") == R74_REVISION
    receipt = {
        "schema": "deeplus.r71-method-extension-resolution-dynamic-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_id": FEATURE,
        "transitioned_cell_count": 1,
        "disposition": "BOUND_DELEGATED",
        "delegate_feature_id": DELEGATE,
        "projected_counts": {
            "bound_direct": 2470 if r74_successor else 2469 if r73_successor else 2467,
            "bound_delegated": 4,
            "not_applicable": 502 if r74_successor else 503 if (r72_successor or r73_successor) else 502,
            "applicable_blocked": (
                1245 if (r73_successor or r74_successor) else (1247 if r72_successor else 1248)
            ),
        },
        "non_target_cell_count": (
            R74_QUINT_EXCLUSION_COUNT
            if r74_successor
            else R73_QUAD_EXCLUSION_COUNT
            if r73_successor
            else (R72_DUAL_EXCLUSION_COUNT if r72_successor else NON_TARGET_COUNT)
        ),
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "gates": GATES,
        "errors": errors,
    }
    print(json.dumps(receipt, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
