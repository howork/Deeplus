#!/usr/bin/env python3
"""Validate the R39 ownership-tooling design projection and mutation fence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

FILES = {
    "contract": "spec/contracts/ownership-tooling-obligations-r1.json",
    "schema": "schemas/language/ownership-tooling-obligations-r1.schema.json",
    "fixture_schema": "schemas/language/ownership-tooling-obligations-fixtures-r1.schema.json",
    "fixtures": "tests/fixtures/current/ownership-tooling-obligations-r1.json",
    "feature": "spec/features/catalog/chunks/part-0006.json",
    "diagnostic": "spec/diagnostics/catalog/chunks/part-0033.json",
    "decision": "decisions/language/Design_Deeplus_Ownership_Tooling_Projection_R1.md",
}

SPAN_ROLES = [
    "PRIMARY_OPERATION",
    "OWNER_DECLARATION",
    "PRIOR_TRANSFER",
    "LOAN_ORIGIN",
    "CONFLICTING_ACCESS",
    "REGION_BOUNDARY",
    "CAPTURE_SITE",
    "ESCAPE_BOUNDARY",
    "CLEANUP_REGISTRATION",
    "SUSPENSION_POINT",
    "JOIN_PREDECESSOR",
    "PAYLOAD_CAUSE",
]

FAMILY_IDS = [
    "OWN_USE_OR_TRANSFER",
    "OWN_ALIAS_OR_INOUT_CONFLICT",
    "OWN_BORROW_ESCAPE_OR_SUSPENSION",
    "OWN_PLACE_STATE_JOIN",
    "OWN_CAPTURE_RESPONSIBILITY",
    "OWN_CLEANUP_OR_DEFER",
    "OWN_SHARED_PAYLOAD",
    "OWN_MIR_RESPONSIBILITY_VERIFIER",
]

INACTIVE_SEEDS = [
    "CLOSURE_BORROW_CAPTURE_ESCAPES",
    "CLOSURE_CAPTURE_ESCAPES_REGION",
    "ITERATOR_CLEANUP_EFFECT_NOT_ACCOUNTED",
]

CANONICAL_UNPROFILED = [
    {"diagnostic_id": "RESPONSIBILITY_IDENTITY_UNRESOLVED", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R48"},
    {"diagnostic_id": "RESPONSIBILITY_EVIDENCE_NOT_ADMISSIBLE", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R48"},
    {"diagnostic_id": "CLEANUP_BUDGET_DUPLICATE", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R48"},
    {"diagnostic_id": "CLEANUP_BUDGET_ERRORS_REQUIRES_ERROR_SET", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R48"},
    {"diagnostic_id": "RESOURCE_INHERITANCE_REQUIRES_SAME_MODULE_SEALED_ROOT", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R48"},
    {"diagnostic_id": "CLEANUP_BUDGET_EXCEEDED", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R48"},
    {"diagnostic_id": "PATTERN_BORROWED_MATCH_CANNOT_MOVE_PAYLOAD", "tooling_projection_status": "CANONICAL_ACTIVE_UNPROFILED_R60"},
    {"diagnostic_id": "MIR_LOAN_UNBALANCED", "tooling_projection_status": "INTERNAL_RELEASE_VERIFIER_NO_SOURCE_SPAN"},
]

FIX_CLASSES = [
    "PRESENTATION_ONLY",
    "RESPONSIBILITY_NEUTRAL_SOURCE",
    "MANUAL_RESPONSIBILITY_CHANGE",
    "PROHIBITED_AUTHORITY_MANUFACTURING",
]

FORBIDDEN_TRANSFORMS = [
    "INSERT_MOVE",
    "INSERT_CLONE",
    "INSERT_SHARE_OR_TRANSFER",
    "CHANGE_CAPTURE_MODE",
    "WIDEN_REGION_OR_LIFETIME",
    "REORDER_OR_REMOVE_CLEANUP",
    "SUPPRESS_OWNERSHIP_DIAGNOSTIC",
    "MATERIALIZE_OWNER_LOAN_TOKEN_ROOT_OR_WITNESS",
]

REASON_CODES = [
    "TOOLING_SNAPSHOT_STALE_OR_MIXED",
    "TOOLING_REQUIRED_RELATED_SPAN_MISSING",
    "TOOLING_RELATED_SPAN_ORDER_DRIFT",
    "TOOLING_FIXIT_MANUFACTURES_AUTHORITY",
    "TOOLING_FORMATTER_RESPONSIBILITY_DRIFT",
    "TOOLING_RENAME_RESPONSIBILITY_DRIFT",
    "TOOLING_DEBUGGER_IDENTITY_CONFLATION",
    "TOOLING_DEBUGGER_STATE_FABRICATED",
]

EXPECTED_FAMILIES = {
    "OWN_USE_OR_TRANSFER": (["OWNERSHIP_MODE_ADMISSION_FAILED", "FACET_MOVE_REQUIRES_OWNER"], ["PRIMARY_OPERATION", "OWNER_DECLARATION", "PRIOR_TRANSFER", "LOAN_ORIGIN", "CONFLICTING_ACCESS", "REGION_BOUNDARY", "ESCAPE_BOUNDARY", "SUSPENSION_POINT", "PAYLOAD_CAUSE"]),
    "OWN_ALIAS_OR_INOUT_CONFLICT": (["INOUT_ALIAS_CONFLICT", "ALIAS_PATTERN_OWNERSHIP_CONFLICT"], ["PRIMARY_OPERATION", "PRIOR_TRANSFER", "LOAN_ORIGIN", "CONFLICTING_ACCESS"]),
    "OWN_BORROW_ESCAPE_OR_SUSPENSION": (["BORROW_ESCAPE_OWNER_REGION", "FACET_BORROW_CROSSES_SUSPENSION", "SCOPED_CALLBACK_BORROW_ESCAPE_FORBIDDEN"], ["LOAN_ORIGIN", "REGION_BOUNDARY", "ESCAPE_BOUNDARY", "SUSPENSION_POINT"]),
    "OWN_PLACE_STATE_JOIN": (["PLACE_STATE_JOIN_MISMATCH", "PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH"], ["PRIMARY_OPERATION", "JOIN_PREDECESSOR"]),
    "OWN_CAPTURE_RESPONSIBILITY": (["OUTER_MUTATION_REQUIRES_INOUT_CAPTURE", "OUTER_MOVE_REQUIRES_EXPLICIT_CAPTURE"], ["PRIMARY_OPERATION", "OWNER_DECLARATION", "CAPTURE_SITE"]),
    "OWN_CLEANUP_OR_DEFER": (["DEFER_CLEANUP_RESERVED_PLACE_MOVED", "CLEANUP_DECLARATION_DIRECT_CALL_FORBIDDEN"], ["PRIMARY_OPERATION", "CLEANUP_REGISTRATION"]),
    "OWN_SHARED_PAYLOAD": (["SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD"], ["PRIMARY_OPERATION", "PAYLOAD_CAUSE"]),
    "OWN_MIR_RESPONSIBILITY_VERIFIER": (["HIR_MIR_RESPONSIBILITY_PROJECTION_MISMATCH"], ["PRIMARY_OPERATION", "PAYLOAD_CAUSE"]),
}

EXPECTED_PROFILE_PRIMARY = {
    "OWNERSHIP_MODE_ADMISSION_FAILED": "PRIMARY_OPERATION",
    "FACET_MOVE_REQUIRES_OWNER": "PRIMARY_OPERATION",
    "INOUT_ALIAS_CONFLICT": "PRIMARY_OPERATION",
    "ALIAS_PATTERN_OWNERSHIP_CONFLICT": "PRIMARY_OPERATION",
    "BORROW_ESCAPE_OWNER_REGION": "ESCAPE_BOUNDARY",
    "FACET_BORROW_CROSSES_SUSPENSION": "SUSPENSION_POINT",
    "SCOPED_CALLBACK_BORROW_ESCAPE_FORBIDDEN": "ESCAPE_BOUNDARY",
    "PLACE_STATE_JOIN_MISMATCH": "PRIMARY_OPERATION",
    "PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH": "PRIMARY_OPERATION",
    "OUTER_MUTATION_REQUIRES_INOUT_CAPTURE": "PRIMARY_OPERATION",
    "OUTER_MOVE_REQUIRES_EXPLICIT_CAPTURE": "PRIMARY_OPERATION",
    "DEFER_CLEANUP_RESERVED_PLACE_MOVED": "PRIMARY_OPERATION",
    "CLEANUP_DECLARATION_DIRECT_CALL_FORBIDDEN": "PRIMARY_OPERATION",
    "SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD": "PRIMARY_OPERATION",
    "HIR_MIR_RESPONSIBILITY_PROJECTION_MISMATCH": "PRIMARY_OPERATION",
}

EXPECTED_PROFILE_RELATED_ROLES = {
    "OWNERSHIP_MODE_ADMISSION_FAILED": ["OWNER_DECLARATION"],
    "FACET_MOVE_REQUIRES_OWNER": ["PAYLOAD_CAUSE", "OWNER_DECLARATION"],
    "INOUT_ALIAS_CONFLICT": ["CONFLICTING_ACCESS", "LOAN_ORIGIN"],
    "ALIAS_PATTERN_OWNERSHIP_CONFLICT": ["PRIOR_TRANSFER", "LOAN_ORIGIN"],
    "BORROW_ESCAPE_OWNER_REGION": ["LOAN_ORIGIN", "REGION_BOUNDARY"],
    "FACET_BORROW_CROSSES_SUSPENSION": ["LOAN_ORIGIN"],
    "SCOPED_CALLBACK_BORROW_ESCAPE_FORBIDDEN": ["LOAN_ORIGIN", "REGION_BOUNDARY"],
    "PLACE_STATE_JOIN_MISMATCH": ["JOIN_PREDECESSOR"],
    "PATTERN_CROSS_ARM_PLACE_STATE_MISMATCH": ["JOIN_PREDECESSOR"],
    "OUTER_MUTATION_REQUIRES_INOUT_CAPTURE": ["OWNER_DECLARATION", "CAPTURE_SITE"],
    "OUTER_MOVE_REQUIRES_EXPLICIT_CAPTURE": ["OWNER_DECLARATION", "CAPTURE_SITE"],
    "DEFER_CLEANUP_RESERVED_PLACE_MOVED": ["CLEANUP_REGISTRATION"],
    "CLEANUP_DECLARATION_DIRECT_CALL_FORBIDDEN": ["CLEANUP_REGISTRATION"],
    "SHARED_MUTEX_REJECTS_LIFECYCLE_PAYLOAD": ["PAYLOAD_CAUSE"],
    "HIR_MIR_RESPONSIBILITY_PROJECTION_MISMATCH": ["PAYLOAD_CAUSE"],
}

EXPECTED_REASON_KEYS = ["EXCLUSIVITY", "LIFETIME", "ESCAPE", "SUSPENSION", "TRANSFER_OR_USE_AFTER_MOVE"]

EXPECTED_CASE_IDS = ["OWN-GAP-P-027", "OWN-GAP-B-027", "OWN-GAP-N-027", "OWN-TOOL-M-065"]
EXPECTED_MUTATION_IDS = [f"R39-M-{index:02d}" for index in range(1, 11)]
MUTATION_EXPECTED_CHECKS = {
    "R39-M-01": "R39_RELATED_SPAN_COMPLETENESS",
    "R39-M-02": "R39_RELATED_SPAN_COMPLETENESS",
    "R39-M-03": "R39_PRIMARY_RELATED_ORDER",
    "R39-M-04": "R39_CODE_ACTION_FENCE",
    "R39-M-05": "R39_FORMATTER_FENCE",
    "R39-M-06": "R39_SNAPSHOT_REVISION_FENCE",
    "R39-M-07": "R39_RENAME_FENCE",
    "R39-M-08": "R39_HOVER_FENCE",
    "R39-M-09": "R39_DEPENDENCY_FENCE",
    "R39-M-10": "R39_ACTOR_TRANSFER_PROJECTION",
}


def load_json(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def all_diagnostics(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("part-*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")):
            rows[row["diagnostic_id"]] = row
    return rows


def check(errors: list[dict[str, str]], checks: list[str], condition: bool, check_id: str, message: str) -> None:
    checks.append(check_id)
    if not condition:
        errors.append({"check_id": check_id, "message": message})


def requirement_tuple(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row.get("role"), row.get("min_count"), row.get("max_count_or_null"), row.get("exact_count_source_or_null"), row.get("omit_when_zero"))


def valid_requirement(row: dict[str, Any]) -> bool:
    minimum = row.get("min_count")
    maximum = row.get("max_count_or_null")
    exact_source = row.get("exact_count_source_or_null")
    return (
        set(row) == {"role", "min_count", "max_count_or_null", "exact_count_source_or_null", "omit_when_zero"}
        and row.get("role") in SPAN_ROLES
        and isinstance(minimum, int)
        and minimum >= 0
        and (maximum is None or isinstance(maximum, int) and maximum >= max(1, minimum))
        and isinstance(row.get("omit_when_zero"), bool)
        and (minimum != 0 or row.get("omit_when_zero") is True and isinstance(exact_source, str) and bool(exact_source))
    )


def validate_documents(root: Path, docs: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[dict[str, str]] = []
    checks: list[str] = []
    contract = docs["contract"]
    schema = docs["schema"]
    fixture_schema = docs["fixture_schema"]
    fixtures = docs["fixtures"]
    feature_rows = docs["feature"]
    diagnostics = all_diagnostics(root)

    check(errors, checks, all((root / relative).is_file() for relative in FILES.values()), "R39_FILES_PRESENT", "one or more R39 artifacts are missing")
    check(errors, checks, contract.get("schema") == "deeplus.ownership-tooling-obligations/r1" and contract.get("gap_id") == "IR-OWN-P2-027", "R39_CONTRACT_IDENTITY", "contract identity drift")
    check(errors, checks, contract.get("baseline") == {"repository": "howork/Deeplus", "branch": "main", "commit": "39a5d50cc770341c4b9776d00d84520b780d0c62", "tree": "b19b2a86c0f29c1f73763c8526a3a7bde23d530a"}, "R39_BASELINE_BINDINGS", "baseline binding drift")
    check(errors, checks, contract.get("sibling_dependencies") == [
        {"identity": "R28_FORMATTER_LSP_INCREMENTAL_CONTRACT_R1", "status": "LOCAL_FUSION_INCLUDED", "future_action": "NONE_SAME_CANDIDATE"},
        {"identity": "R38_CONTINUATION_INTERFACE_REBASE_R1", "status": "CANONICAL_CURRENT", "future_action": "NONE"},
    ], "R39_SIBLING_DEPENDENCY_BINDINGS", "R28/R38 dependency status drift")
    expected_tooling_recipe = ["ParseSnapshotId", "checker_snapshot_digest", "ownership_contract_digest_set"]
    expected_request_binding = ["ToolingSnapshotId", *expected_tooling_recipe]
    schema_identity = schema.get("properties", {}).get("identity_domains", {}).get("properties", {}).get("ToolingSnapshotId", {}).get("const", {})
    schema_request_binding = schema.get("properties", {}).get("snapshot_fence", {}).get("properties", {}).get("request_binding", {}).get("const")
    check(errors, checks, contract.get("snapshot_fence", {}).get("cross_revision_merge_count") == 0 and contract.get("identity_domains", {}).get("ToolingSnapshotId", {}).get("recipe") == expected_tooling_recipe and contract.get("snapshot_fence", {}).get("request_binding") == expected_request_binding and schema_identity.get("recipe") == expected_tooling_recipe and schema_request_binding == expected_request_binding, "R39_SNAPSHOT_REVISION_FENCE", "tooling snapshot/schema is not an exact ParseSnapshotId extension or cross-revision facts may be merged")
    input_bindings_ok = len(contract.get("inputs", {})) == 12
    for binding in contract.get("inputs", {}).values():
        path = root / binding.get("path", "")
        input_bindings_ok &= path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == binding.get("sha256")
    check(errors, checks, input_bindings_ok, "R39_INPUT_DIGEST_BINDINGS", "one or more canonical input path/digest bindings drift")

    schema_defs = schema.get("$defs", {})
    check(errors, checks, schema_defs.get("ownershipSpanRole", {}).get("enum") == SPAN_ROLES and schema.get("properties", {}).get("span_roles", {}).get("const") == SPAN_ROLES, "R39_SCHEMA_SPAN_DOMAIN", "schema does not close the exact span-role domain")
    check(errors, checks, schema_defs.get("familyId", {}).get("enum") == FAMILY_IDS, "R39_SCHEMA_FAMILY_DOMAIN", "schema does not close the exact family domain")
    check(errors, checks, schema_defs.get("diagnosticId", {}).get("enum") == list(EXPECTED_PROFILE_PRIMARY), "R39_SCHEMA_DIAGNOSTIC_DOMAIN", "schema does not close the exact diagnostic profile domain")
    check(errors, checks, schema.get("properties", {}).get("reason_codes", {}).get("const") == REASON_CODES, "R39_SCHEMA_REASON_DOMAIN", "schema does not close reason codes")
    profile_schema = schema.get("properties", {}).get("diagnostic_span_profiles", {})
    family_schema = schema.get("properties", {}).get("diagnostic_family_projections", {}).get("items", {})
    check(errors, checks, profile_schema.get("minItems") == 15 and profile_schema.get("maxItems") == 15 and set(family_schema.get("required", [])) == {"family_id", "diagnostic_ids", "allowed_role_union", "normative_cardinality_source"} and "omit_when_zero" in schema_defs.get("relatedSpanRequirement", {}).get("required", []), "R39_SCHEMA_PROFILE_SHAPE", "schema profile/family/cardinality shape drift")
    check(errors, checks, fixture_schema.get("properties", {}).get("expected_counts", {}).get("const") == {"positive": 1, "boundary": 1, "negative": 1, "mutation_suite": 1, "total": 4, "mutations": 10}, "R39_FIXTURE_SCHEMA_COUNTS", "fixture schema count fence drift")

    dependencies = contract.get("dependency_status", [])
    dependency_core = [{key: row.get(key) for key in ("dependency_id", "status", "panel", "required_digest_or_null")} for row in dependencies]
    dependency_shapes = [row.get("bound_shape") for row in dependencies]
    check(errors, checks, dependency_core == [
        {"dependency_id": "MANAGED_REFERENCE_MEMORY_PROFILE", "status": "CANONICALLY_BOUND_DESIGN_STATIC", "panel": "root_rows", "required_digest_or_null": "feff3c021d4b77e64e4e9f00f797b0ce2c465a5b60709d86d0baf7bded72c7f7"},
        {"dependency_id": "CONTINUATION_INTERFACE", "status": "CANONICALLY_BOUND_DESIGN_STATIC", "panel": "continuation_rows", "required_digest_or_null": "42b925ea39769f9eb85310d333e0c43f866c72d0541dcdd6b7966c4bd1ed8562"},
    ] and dependency_shapes == [
        {"semantic_references": ["RootId"], "required_receipt": "exact runtime/debug receipt additionally bound to the canonical managed-reference profile digest", "current_rows": "EMPTY_UNAVAILABLE_RUNTIME_NOT_RUN"},
        {"semantic_references": ["ContinuationReceiptId"], "fields": ["frame state", "winner"], "required_receipt": "exact runtime/debug receipt additionally bound to the canonical continuation-interface digest", "current_rows": "EMPTY_UNAVAILABLE_RUNTIME_NOT_RUN"},
    ], "R39_DEPENDENCY_FENCE", "root/continuation dependency digests or runtime-evidence fence drift")

    sidecar = contract.get("ownership_sidecar_projection", {})
    identity = contract.get("identity_domains", {})
    observation_recipe = identity.get("OwnershipObservationId", {}).get("recipe", [])
    check(errors, checks, sidecar.get("owner_binding_states") == ["UNISSUED", "LIVE", "JOIN_CONDITIONAL", "RETIRED"] and sidecar.get("projection_availability") == {"STATIC_PROGRAM_POINT": "DESIGN_STATIC_AVAILABLE", "PAUSED_RUNTIME_SNAPSHOT": "NOT_RUN_REQUIRES_EXACT_RUNTIME_DEBUG_RECEIPT"} and sidecar.get("tool_to_semantic_feedback_edge_count") == 0 and sidecar.get("tool_created_semantic_identity_count") == 0 and observation_recipe == ["CompilationReceiptId", "RuntimeInstanceId", "ExecutionId", "ActivationFrameId", "FunctionId", "MirProgramPointId", "pause_epoch", "exact runtime/debug receipt digest"] and "ContinuationReceiptId" not in identity.get("semantic_references", []), "R39_SIDECAR_READ_ONLY", "ownership sidecar can fabricate identity, mix activations, or import an unbound dependency")
    check(errors, checks, contract.get("span_roles") == SPAN_ROLES, "R39_SPAN_ROLE_DOMAIN", "contract span roles drift")
    span_ordering = contract.get("span_ordering", {})
    order = span_ordering.get("related_order", "")
    check(errors, checks, span_ordering.get("primary_selection") == "semantic diagnostic row primary_role, then least stable SourceOriginId, then typed semantic-reference tie-break" and order == "stable SourceOriginId then typed semantic-reference tie-break; role is data only; source, fixture, catalog and CFG iteration order never wins", "R39_PRIMARY_RELATED_ORDER", "primary/related span ordering is not SourceOriginId-bound")
    check(errors, checks, contract.get("span_ordering", {}).get("primary_count") == 1 and contract.get("span_ordering", {}).get("duplicate_span_role_pair_count") == 0, "R39_SPAN_CARDINALITY", "primary/related span cardinality drift")

    families = contract.get("diagnostic_family_projections", [])
    family_ids = [row.get("family_id") for row in families]
    family_shapes_ok = family_ids == FAMILY_IDS and len(set(family_ids)) == 8
    active_ids: list[str] = []
    for row in families:
        active_ids.extend(row.get("diagnostic_ids", []))
        expected_members, expected_roles = EXPECTED_FAMILIES.get(row.get("family_id"), (None, None))
        family_shapes_ok &= row.get("diagnostic_ids") == expected_members and row.get("allowed_role_union") == expected_roles and row.get("normative_cardinality_source") == "diagnostic_span_profiles" and set(row) == {"family_id", "diagnostic_ids", "allowed_role_union", "normative_cardinality_source"}
    check(errors, checks, family_shapes_ok, "R39_FAMILY_SET", "diagnostic family grouping set/order drift")
    profiles = contract.get("diagnostic_span_profiles", [])
    profile_ids = [row.get("diagnostic_id") for row in profiles]
    profiles_ok = profile_ids == list(EXPECTED_PROFILE_PRIMARY) and len(set(profile_ids)) == 15 and profile_ids == active_ids
    for row in profiles:
        diagnostic_id = row.get("diagnostic_id")
        family_id = row.get("family_id")
        family_members, family_roles = EXPECTED_FAMILIES.get(family_id, ([], []))
        requirements = row.get("related_span_requirements", [])
        profiles_ok &= diagnostic_id in family_members and row.get("primary_role") == EXPECTED_PROFILE_PRIMARY.get(diagnostic_id)
        profiles_ok &= [item.get("role") for item in requirements] == EXPECTED_PROFILE_RELATED_ROLES.get(diagnostic_id)
        profiles_ok &= row.get("primary_role") in family_roles and all(valid_requirement(item) and item.get("role") in family_roles for item in requirements)
        variants = row.get("reason_variants", [])
        if diagnostic_id == "OWNERSHIP_MODE_ADMISSION_FAILED":
            profiles_ok &= [item.get("reason_key") for item in variants] == EXPECTED_REASON_KEYS
            profiles_ok &= all(item.get("requirements") and all(valid_requirement(req) and req.get("role") in family_roles for req in item.get("requirements", [])) for item in variants)
        else:
            profiles_ok &= not variants
    check(errors, checks, profiles_ok, "R39_RELATED_SPAN_COMPLETENESS", "per-diagnostic span roles/cardinalities drift")
    check(errors, checks, all(diagnostics.get(item, {}).get("diagnostic_status") == "active" for item in active_ids), "R39_ACTIVE_DIAGNOSTIC_FENCE", "inactive or missing diagnostic entered active tooling projection")
    inactive = contract.get("inactive_seed_references", [])
    unprofiled = contract.get("canonical_unprofiled_diagnostics", [])
    check(errors, checks, [row.get("diagnostic_id") for row in inactive] == INACTIVE_SEEDS and all(row.get("tooling_projection_status") == "INACTIVE_NOT_PROJECTED" for row in inactive) and all(diagnostics.get(item, {}).get("diagnostic_status") == "seed" for item in INACTIVE_SEEDS) and unprofiled == CANONICAL_UNPROFILED and all(diagnostics.get(row["diagnostic_id"], {}).get("diagnostic_status") == "active" for row in CANONICAL_UNPROFILED) and diagnostics.get("MIR_LOAN_UNBALANCED", {}).get("diagnostic_class") == "release_verifier", "R39_SEED_DIAGNOSTIC_FENCE", "seed or canonical unprofiled diagnostic disposition drift")

    hover = contract.get("hover_projection", {})
    check(errors, checks, hover.get("initialization_states") == ["Uninitialized", "Live", "Moved", "MaybeMoved"] and hover.get("loan_states") == ["Active", "Suspended", "Ended"] and hover.get("cleanup_token_states") == ["Unbound", "Available", "Consumed"] and hover.get("hidden_identity_invention_count") == 0, "R39_HOVER_FENCE", "hover state domain or identity fence drift")
    formatter = contract.get("formatter_projection", {})
    check(errors, checks, formatter.get("protected_spellings") == ["move", "borrow", "inout", "owned", "borrowed", "mut", "capture", "defer"] and formatter.get("parse_format_parse_normalized_hir_equal") is True and formatter.get("responsibility_digest_equal") is True and formatter.get("second_pass_edit_count") == 0 and formatter.get("ownership_semantic_rewrite_count") == 0, "R39_FORMATTER_FENCE", "formatter ownership/idempotence fence drift")
    rename = contract.get("rename_projection", {})
    check(errors, checks, rename.get("binding") == ["ToolingSnapshotId", "target DeclId", "exact reference graph digest"] and "isomorphic" in rename.get("cross_snapshot_proof", "") and rename.get("implicit_ownership_change_count") == 0, "R39_RENAME_FENCE", "rename snapshot/isomorphism fence drift")
    actions = contract.get("code_action_policy", {})
    check(errors, checks, actions.get("classes") == FIX_CLASSES and actions.get("automatic_classes") == FIX_CLASSES[:2] and actions.get("forbidden_transformations") == FORBIDDEN_TRANSFORMS and actions.get("automatic_authority_manufacturing_count") == 0, "R39_CODE_ACTION_FENCE", "code-action authority fence drift")
    debugger = contract.get("debugger_projection", {})
    location = debugger.get("backend_location_sidecar", {})
    check(errors, checks, location.get("display_only") is True and location.get("semantic_identity") is False and location.get("equality_authority") is False and location.get("persistent") is False and location.get("included_in_projection_digest") is False and location.get("expires_at_resume") is True and location.get("instance_status") == "NOT_RUN_UNAVAILABLE_WITHOUT_EXACT_RUNTIME_DEBUG_RECEIPT" and debugger.get("paused_runtime_rows") == "NOT_RUN and UNAVAILABLE until an exact runtime/debug receipt digest is supplied" and debugger.get("root_rows") == "canonical managed-reference digest bound; runtime rows remain empty and UNAVAILABLE_RUNTIME_NOT_RUN until an exact runtime/debug receipt is supplied" and debugger.get("continuation_rows") == "canonical continuation-interface digest bound; runtime rows remain empty and UNAVAILABLE_RUNTIME_NOT_RUN until an exact runtime/debug receipt is supplied" and "continuation_fields" not in debugger and debugger.get("invented_owner_loan_token_or_continuation_count") == 0, "R39_DEBUGGER_PROJECTION", "debugger/backend identity or runtime-receipt fence drift")
    actor = contract.get("actor_transfer_projection", {})
    check(errors, checks, actor.get("dual_owner_count") == 0 and "enqueue_committed" in actor.get("commit_event", "") and "sender_retained" in actor.get("precommit_or_rejected", "") and "no cross-channel or global order" in actor.get("channel_sequence_rule", "") and actor.get("runtime_debugger_execution") == "NOT_RUN", "R39_ACTOR_TRANSFER_PROJECTION", "actor transfer ownership/ordering projection drift")

    fixture_ids = [row.get("test_id") for row in fixtures.get("cases", [])]
    mutation_ids = [row.get("mutation_id") for row in fixtures.get("mutations", [])]
    check(errors, checks, fixture_ids == EXPECTED_CASE_IDS and fixtures.get("expected_counts") == {"positive": 1, "boundary": 1, "negative": 1, "mutation_suite": 1, "total": 4, "mutations": 10}, "R39_EXACT_ACCEPTANCE_IDS", "acceptance ID/count fence drift")
    check(errors, checks, mutation_ids == EXPECTED_MUTATION_IDS and all(row.get("expected") == "REJECT" for row in fixtures.get("mutations", [])), "R39_MUTATION_SET", "mutation suite drift")
    case_by_id = {row.get("test_id"): row for row in fixtures.get("cases", [])}
    positive = case_by_id.get("OWN-GAP-P-027", {})
    boundary = case_by_id.get("OWN-GAP-B-027", {})
    negative = case_by_id.get("OWN-GAP-N-027", {})
    positive_input = positive.get("input", {})
    actor_fixture = positive_input.get("actor_transfer_projection", {})
    rename_fixture = positive_input.get("rename_projection", {})
    boundary_input = boundary.get("input", {})
    boundary_rows = boundary_input.get("related_spans", [])
    check(errors, checks, positive.get("operation") == "MOVE_BORROW_CLEANUP_TOOLING_PROJECTION" and positive.get("expected") == {"result": "ACCEPT_EXACT_READ_ONLY_PROJECTION", "diagnostic_or_null": None, "semantic_mutation_count": 0} and rename_fixture == {"target_decl_id_bound": True, "reference_graph_isomorphic": True, "ownership_responsibility_digest_equal": True} and actor_fixture.get("dual_owner_count") == 0 and actor_fixture.get("ownership_commit_count") == 1 and actor_fixture.get("runtime_debugger_execution") == "NOT_RUN", "R39_POSITIVE_CASE_BODY", "positive rename/actor projection fixture drift")
    check(errors, checks, boundary.get("operation") == "OVERLAPPING_INOUT_MULTI_SPAN" and boundary.get("expected", {}).get("diagnostic_or_null") == "INOUT_ALIAS_CONFLICT" and boundary_input.get("related_span_counts") == {"CONFLICTING_ACCESS": 2, "LOAN_ORIGIN": 0} and [row.get("role") for row in boundary_rows] == ["CONFLICTING_ACCESS", "CONFLICTING_ACCESS"] and len({row.get("source_origin_id") for row in boundary_rows}) == 2, "R39_BOUNDARY_CASE_BODY", "boundary fixture does not prove two distinct conflicting accesses")
    check(errors, checks, negative.get("operation") == "AUTO_INSERT_CLONE_WITHOUT_WITNESS" and negative.get("expected") == {"result": "REJECT", "diagnostic_or_null": "OWNERSHIP_TOOLING_PROJECTION_DRIFT", "semantic_mutation_count": 0} and negative.get("input", {}).get("transformation") == "INSERT_CLONE", "R39_NEGATIVE_CASE_BODY", "negative authority-manufacturing fixture drift")

    final_row = diagnostics.get("OWNERSHIP_TOOLING_PROJECTION_DRIFT", {})
    check(errors, checks, final_row.get("diagnostic_status") == "active" and final_row.get("diagnostic_class") == "release_verifier" and final_row.get("emission_domain") == "release_verifier" and final_row.get("product_support") == "NOT_RUN", "R39_DIAGNOSTIC_BINDING", "release-verifier diagnostic binding drift")
    feature = next((row for row in feature_rows if row.get("feature_id") == "formatter_lsp_responsibility_card"), {})
    required_artifacts = {FILES["contract"], FILES["schema"], FILES["fixture_schema"], FILES["fixtures"], FILES["decision"]}
    check(errors, checks, "hir_h1_current_mir_bridge_design" in feature.get("depends_on", []) and "OWNERSHIP_TOOLING_PROJECTION_DRIFT" in feature.get("normative_trace_refs", {}).get("diagnostics", []) and required_artifacts.issubset(set(feature.get("artifact_trace_refs", []))), "R39_FEATURE_TRACE", "feature trace binding drift")

    docs_text = "\n".join([
        (root / "spec/language.md").read_text(encoding="utf-8"),
        (root / "docs/grammar-reference/12-ownership-borrowing-and-responsibility.md").read_text(encoding="utf-8"),
        (root / "docs/grammar-reference/18-evaluation-ownership-mir-and-backends.md").read_text(encoding="utf-8"),
        (root / "docs/tutorial/part-11-modules-system/11-05-hir-mir-backends-tooling.md").read_text(encoding="utf-8"),
    ])
    check(errors, checks, "OWNERSHIP_TOOLING_PROJECTION_DRIFT" in docs_text and "SourceOriginId" in docs_text and "OPTIMIZED_OUT" in docs_text, "R39_DOCUMENTATION_TRACE", "normative/teaching documentation trace missing")

    governance = contract.get("governance", {})
    execution = fixtures.get("execution", {})
    check(errors, checks, governance == {"semantic_p0": 0, "canonical_feature_p1": "22_OPEN_UNCHANGED", "separate_m13_actions": "4_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "source_syntax_change_count": 0, "grammar_production_change_count": 0, "language_semantic_change_count": 0, "production_formatter_lsp_debugger": "NOT_RUN", "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION"} and execution == {"design_static_projection": "PASS", "production_formatter": "NOT_RUN", "production_lsp": "NOT_RUN", "production_debugger": "NOT_RUN", "product_lanes": "15_OF_15_NOT_RUN"}, "R39_GOVERNANCE_NOT_RUN", "governance/evidence-honesty fence drift")
    return errors, checks


def mutation_documents(docs: dict[str, Any], index: int) -> dict[str, Any]:
    mutant = copy.deepcopy(docs)
    contract = mutant["contract"]
    if index == 1:
        contract["diagnostic_span_profiles"][0]["primary_role"] = "ARBITRARY_ROLE"
    elif index == 2:
        contract["diagnostic_span_profiles"][2]["related_span_requirements"].pop(0)
    elif index == 3:
        contract["span_ordering"]["related_order"] = "CFG predecessor iteration order"
    elif index == 4:
        contract["code_action_policy"]["automatic_authority_manufacturing_count"] = 1
    elif index == 5:
        contract["formatter_projection"]["protected_spellings"].remove("move")
    elif index == 6:
        contract["snapshot_fence"]["cross_revision_merge_count"] = 1
    elif index == 7:
        contract["rename_projection"]["implicit_ownership_change_count"] = 1
    elif index == 8:
        contract["hover_projection"]["loan_states"] = ["Active", "Ended"]
    elif index == 9:
        contract["dependency_status"][1]["bound_shape"]["current_rows"] = "AVAILABLE_WITHOUT_RUNTIME_RECEIPT"
        contract["debugger_projection"]["backend_location_sidecar"]["semantic_identity"] = True
    elif index == 10:
        contract["actor_transfer_projection"]["dual_owner_count"] = 1
        contract["ownership_sidecar_projection"]["tool_to_semantic_feedback_edge_count"] = 1
        contract["governance"]["production_formatter_lsp_debugger"] = "PASS"
    return mutant


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    docs = {name: load_json(root, relative) for name, relative in FILES.items() if relative.endswith(".json")}
    errors, checks = validate_documents(root, docs)
    mutation_results = []
    if not errors:
        for index in range(1, 11):
            mutation_id = f"R39-M-{index:02d}"
            mutation_errors, _ = validate_documents(root, mutation_documents(docs, index))
            failed_ids = {row.get("check_id") for row in mutation_errors}
            expected_check = MUTATION_EXPECTED_CHECKS[mutation_id]
            rejected = expected_check in failed_ids
            mutation_results.append({"mutation_id": mutation_id, "result": "REJECTED" if rejected else "SURVIVED", "target_check": expected_check})
            if not rejected:
                errors.append({"check_id": "R39_MUTATION_REJECTION_10", "message": f"{mutation_id} did not fail targeted check {expected_check}"})
    else:
        errors.append({"check_id": "R39_MUTATION_CONTROL_PASS", "message": "control contract must pass before mutation credit"})
    checks.append("R39_MUTATION_REJECTION_10")
    result = {
        "schema": "deeplus.r39-ownership-tooling-validation/r1",
        "result": "PASS" if not errors else "FAIL",
        "evidence_level": "E2_STATIC_CLOSURE",
        "check_scope": "R39_OWNERSHIP_TOOLING_OBLIGATIONS_EXACT",
        "checks": len(checks),
        "check_count": len(checks),
        "passed_check_count": len(checks) - len(errors),
        "passed": len(checks) - len(errors),
        "failed": len(errors),
        "mutation_count": 10,
        "rejected_mutation_count": sum(row.get("result") == "REJECTED" for row in mutation_results),
        "semantic_change_count": 0,
        "product_execution": "NOT_RUN",
        "mutation_results": mutation_results,
        "errors": errors,
        "governance": {"semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN"},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
