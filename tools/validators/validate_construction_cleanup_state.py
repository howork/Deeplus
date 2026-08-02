#!/usr/bin/env python3
"""Focused design-static validator for the R11 construction lifecycle successor."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

PATHS = {
    "contract": ROOT / "spec/contracts/construction-cleanup-state-r1.json",
    "diagnostics": ROOT / "spec/contracts/construction-cleanup-diagnostic-contract-r1.json",
    "contract_schema": ROOT / "schemas/language/construction-cleanup-state.schema.json",
    "fixture_schema": ROOT / "schemas/language/construction-cleanup-state-fixtures.schema.json",
    "fixtures": ROOT / "tests/fixtures/current/construction-cleanup-state-r1.json",
    "hir_schema": ROOT / "schemas/language/canonical-hir-h1.schema.json",
    "hir_catalog": ROOT / "spec/contracts/hir-h1-identity-catalog.json",
    "mir_schema": ROOT / "schemas/language/deeplus-mir.schema.json",
    "mir_registry": ROOT / "spec/contracts/mir-machine-registry.json",
    "row_schema": ROOT / "schemas/language/hir-mir-lowering-row.schema.json",
    "lowering_registry": ROOT / "spec/contracts/hir-mir-lowering-registry.json",
}

LIFECYCLE_ID = "HIR-H1/STRUCT/CONSTRUCTION_LIFECYCLE_PLAN"
PLAN_FIELDS = [
    "construction_plan_id",
    "constructor_decl_id",
    "most_derived_class_id",
    "base_segment_ids",
    "field_slot_descriptors",
    "initial_mask",
    "selected_delegation_plan",
    "cfg_mask_states",
    "field_init_commits",
    "owner_token_transfers",
    "prepublication_self_uses",
    "post_init_guards",
    "abort_cleanup_order",
    "normal_cleanup_order",
    "commit_predicate",
    "unique_publication_site",
    "source_provenance",
]
OPS = [
    "OBJECT_CONSTRUCTION_BEGIN",
    "BASE_SEGMENT_BEGIN",
    "BASE_SEGMENT_COMMIT",
    "FIELD_INIT_COMMIT",
    "CONSTRUCTION_FIELD_MOVE_TRANSFER",
    "CONSTRUCTION_POST_INIT_GUARD",
    "OBJECT_CONSTRUCTION_COMMIT",
    "OBJECT_CONSTRUCTION_ABORT",
    "OBJECT_CLEANUP_BEGIN",
    "OBJECT_CLEANUP_HOOK",
    "OBJECT_FIELD_CLEANUP",
    "OBJECT_BASE_CLEANUP",
    "OBJECT_CLEANUP_END",
]
TRANSITION_FIELDS = [
    "construction_session_id",
    "phase_before",
    "phase_after",
    "mask_digest_before",
    "mask_digest_after",
    "consumed_owner_ids",
    "produced_owner_ids",
    "consumed_cleanup_token_ids",
    "produced_cleanup_token_ids",
    "outcome_edge",
    "hir_provenance",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_all() -> tuple[dict[str, Any], list[str]]:
    docs: dict[str, Any] = {}
    errors: list[str] = []
    for name, path in PATHS.items():
        try:
            docs[name] = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - preflight report
            errors.append(f"{name}: {exc}")
    return docs, errors


def require(errors: list[str], condition: bool, code: str, message: str) -> None:
    if not condition:
        errors.append(f"{code}: {message}")


def main() -> int:
    docs, errors = load_all()
    if errors:
        for error in errors:
            print(f"R11_JSON_PARSE_FAILURE: {error}")
        return 1

    contract = docs["contract"]
    diagnostics = docs["diagnostics"]
    fixtures = docs["fixtures"]
    hir_schema = docs["hir_schema"]
    hir_catalog = docs["hir_catalog"]
    mir_schema = docs["mir_schema"]
    mir_registry = docs["mir_registry"]
    row_schema = docs["row_schema"]
    lowering = docs["lowering_registry"]

    require(errors, contract.get("schema") == "deeplus.construction-cleanup-state/r1", "R11_CONTRACT_ID", "contract schema ID differs")
    require(errors, contract.get("revision") == "R11-INTEGRATED-R1", "R11_REVISION", "contract revision differs")
    require(errors, contract.get("gap_id") == "IR-OWN-P0-016", "R11_GAP", "gap binding differs")
    require(errors, contract.get("source_surface", {}).get("new_surface_count") == 0, "R11_SURFACE", "new source surface was introduced")
    require(errors, contract.get("source_surface", {}).get("grammar_change_required") is False, "R11_SURFACE", "grammar change was claimed")

    identity_ids = [row.get("id") for row in contract.get("identity_domains", [])]
    require(errors, len(identity_ids) == len(set(identity_ids)) == 9, "R11_IDENTITY", "identity domains are not exact unique nine")
    require(errors, contract.get("session_state_machine", {}).get("commit_transition", {}).get("publication_delta") == 1, "R11_COMMIT", "commit publication delta is not one")
    require(errors, contract.get("session_state_machine", {}).get("abort_transition", {}).get("publication_delta") == 0, "R11_ABORT", "abort publication delta is not zero")
    require(errors, contract.get("field_slot_state", {}).get("states") == ["Uninitialized", "Live", "Moved", "MaybeMoved"], "R11_MASK", "field-state universe differs")
    require(errors, contract.get("construction_abort", {}).get("most_derived_whole_cleanup_hook_count") == 0, "R11_ABORT", "partial abort calls the most-derived whole hook")
    require(errors, contract.get("live_object_cleanup", {}).get("automatic_cleanup_suppressed_by_user_hook") is False, "R11_CLEANUP", "user hook suppresses automatic cleanup")
    require(errors, contract.get("hir_contract", {}).get("required_fields") == PLAN_FIELDS, "R11_HIR_PLAN", "HIR plan fields differ")
    require(errors, contract.get("mir_contract", {}).get("operation_kinds") == OPS, "R11_MIR_OPS", "contract operation order differs")
    require(errors, contract.get("mir_contract", {}).get("transition_required_fields") == TRANSITION_FIELDS, "R11_MIR_PAYLOAD", "transition fields differ")

    rows = hir_catalog.get("identity_rows", [])
    ids = [row.get("identity_id") for row in rows]
    require(errors, hir_catalog.get("schema_revision") == "R11-INTEGRATED-R1", "R11_HIR_CATALOG", "HIR catalog revision differs")
    require(errors, hir_catalog.get("identity_count") == len(rows) == len(set(ids)) == 130, "R11_HIR_CATALOG", "HIR catalog is not exact unique 130")
    require(errors, sum(row.get("family") == "STRUCTURAL_SCHEMA" for row in rows) == 18, "R11_HIR_CATALOG", "structural identity count is not 18")
    require(errors, ids.count(LIFECYCLE_ID) == 1, "R11_HIR_PLAN", "lifecycle structural identity is not unique")
    plan_contracts = hir_catalog.get("structural_plan_contracts", [])
    lifecycle_contracts = [row for row in plan_contracts if row.get("structural_identity_id") == LIFECYCLE_ID]
    require(errors, hir_catalog.get("structural_plan_contract_count") == len(plan_contracts) == 14, "R11_HIR_PLAN", "structural plan count is not 14")
    require(errors, len(lifecycle_contracts) == 1 and lifecycle_contracts[0].get("required_plan_fields") == PLAN_FIELDS, "R11_HIR_PLAN", "lifecycle catalog contract differs")
    hdefs = hir_schema.get("$defs", {})
    require(errors, LIFECYCLE_ID in hdefs.get("PlanStructuralKind", {}).get("enum", []), "R11_HIR_SCHEMA", "lifecycle plan kind missing")
    require(errors, "HirConstructionLifecyclePlan" in hdefs, "R11_HIR_SCHEMA", "lifecycle plan schema missing")
    structural_refs = [entry.get("$ref") for entry in hdefs.get("StructuralPlan", {}).get("oneOf", [])]
    require(errors, structural_refs.count("#/$defs/HirConstructionLifecyclePlan") == 1, "R11_HIR_SCHEMA", "lifecycle plan not uniquely reachable")

    operations = mir_registry.get("semantic_operations", [])
    op_map = {row.get("operation_kind"): row.get("semantic_operation_id") for row in operations}
    require(errors, mir_registry.get("draft_revision") == "R11-INTEGRATED-R1", "R11_MIR_REGISTRY", "MIR registry revision differs")
    require(errors, mir_registry.get("semantic_operation_contract", {}).get("operation_kind_count") == len(operations) == len(op_map) == 48, "R11_MIR_REGISTRY", "MIR operation universe is not exact unique 48")
    require(errors, all(op_map.get(op) == f"DM-SEMOP-{op.replace('_', '-')}-R1" for op in OPS), "R11_MIR_REGISTRY", "lifecycle operation mapping differs")
    require(errors, all(row.get("payload_contract", {}).get("required_fields") == TRANSITION_FIELDS for row in operations if row.get("operation_kind") in OPS), "R11_MIR_PAYLOAD", "registry lifecycle payload differs")
    mdefs = mir_schema.get("$defs", {})
    require(errors, set(mdefs.get("operationKind", {}).get("enum", [])) == set(op_map), "R11_MIR_SCHEMA", "MIR schema operation set differs from registry")
    require(errors, set(mdefs.get("semanticOperationId", {}).get("enum", [])) == set(op_map.values()), "R11_MIR_SCHEMA", "MIR schema semantic IDs differ")
    require(errors, mdefs.get("constructionLifecyclePayload", {}).get("required") == TRANSITION_FIELDS, "R11_MIR_PAYLOAD", "MIR payload schema differs")

    row_ops = row_schema.get("$defs", {}).get("operationKind", {}).get("enum", [])
    row_semops = row_schema.get("$defs", {}).get("operationPlanStep", {}).get("properties", {}).get("semantic_operation_id", {}).get("enum", [])
    require(errors, set(row_ops) == set(op_map) and len(row_ops) == 48, "R11_ROW_SCHEMA", "lowering row operation universe differs")
    require(errors, set(row_semops) == set(op_map.values()), "R11_ROW_SCHEMA", "lowering row semantic IDs differ")
    require(errors, lowering.get("draft_revision") == lowering.get("lowering_rules_revision") == "R11-INTEGRATED-R1", "R11_LOWERING", "lowering revision differs")
    require(errors, lowering.get("semantic_operation_mapping") == [{"operation_kind": kind, "semantic_operation_id": semantic_id} for kind, semantic_id in op_map.items()], "R11_LOWERING", "lowering operation map is not exact ordered registry map")
    lifecycle_mapping = lowering.get("nominal_construction_lifecycle_mapping", {})
    require(errors, lifecycle_mapping.get("hir_structural_identity_id") == LIFECYCLE_ID and lifecycle_mapping.get("ordered_operation_family") == OPS, "R11_LOWERING", "nominal lifecycle lowering binding differs")
    require(errors, lifecycle_mapping.get("construction_token_kind") == "BUILDER" and lifecycle_mapping.get("construction_token_specialization") == "ConstructionTokenId", "R11_TOKEN", "construction token specialization differs")

    bindings = lowering.get("contract_bindings", {})
    binding_paths = {
        "hir_schema": "hir_schema",
        "hir_identity_catalog": "hir_catalog",
        "mir_schema": "mir_schema",
        "mir_machine_registry": "mir_registry",
        "lowering_row_schema": "row_schema",
        "fixture_binding_table": None,
        "diagnostic_contract": None,
    }
    for binding, doc_name in binding_paths.items():
        if doc_name is not None:
            require(errors, bindings.get(binding, {}).get("sha256") == sha256(PATHS[doc_name]), "R11_DIGEST", f"{binding} digest is stale")
    hir_digest = sha256(PATHS["hir_schema"])
    mir_digest = sha256(PATHS["mir_schema"])
    lowering_rows = lowering.get("rows", [])
    require(errors, len(lowering_rows) == 111, "R11_LOWERING", "base lowering row count changed")
    require(errors, all(row.get("hir_schema_digest") == hir_digest and row.get("mir_schema_digest") == mir_digest and row.get("lowering_rules_revision") == "R11-INTEGRATED-R1" for row in lowering_rows), "R11_DIGEST", "one or more lowering rows have stale successor binding")

    source_diags = diagnostics.get("source_diagnostics", [])
    verifier_diags = diagnostics.get("release_verifier_diagnostics", [])
    require(errors, diagnostics.get("ordinary_source_diagnostic_count") == len(source_diags) == 6, "R11_DIAGNOSTICS", "source diagnostic count differs")
    require(errors, diagnostics.get("release_verifier_diagnostic_count") == len(verifier_diags) == 4, "R11_DIAGNOSTICS", "verifier diagnostic count differs")
    require(errors, len({row.get("diagnostic_id") for row in source_diags + verifier_diags}) == 10, "R11_DIAGNOSTICS", "diagnostic IDs are not exact unique ten")

    cases = fixtures.get("cases", [])
    counts = Counter(row.get("kind") for row in cases)
    expected_counts = {"POSITIVE": 6, "BOUNDARY": 8, "NEGATIVE": 6, "MUTATION": 4}
    require(errors, len(cases) == len({row.get("test_id") for row in cases}) == 24, "R11_FIXTURES", "fixture IDs are not exact unique 24")
    require(errors, dict(counts) == expected_counts, "R11_FIXTURES", f"fixture classes differ: {dict(counts)}")
    require(errors, fixtures.get("expected_counts") == {"total": 24, **expected_counts}, "R11_FIXTURES", "declared fixture counts differ")
    require(errors, fixtures.get("status") == "DESIGN_STATIC_NOT_RUN", "R11_STATUS", "fixture claims execution")
    require(errors, contract.get("status_fence") == {"semantic_p0": 0, "canonical_feature_p1": "22_OPEN_UNCHANGED", "m13_actions": "4_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "production_implementation": "NOT_RUN"}, "R11_STATUS", "contract status fence differs")

    if errors:
        print("R11 CONSTRUCTION CLEANUP STATE: FAIL")
        for error in errors:
            print(f"  {error}")
        return 1

    print("R11 CONSTRUCTION CLEANUP STATE: PASS")
    print("  HIR identities=130; structural plans=14; lifecycle plans=1")
    print("  MIR operations=48 (29 predecessor + 13 construction lifecycle + 6 suspension-frame); lowering rows=111")
    print("  diagnostics=10 (6 source + 4 verifier); fixtures=24 (6/8/6/4)")
    print("  semantic P0=0; feature P1=22 OPEN; product lanes=15/15 NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
