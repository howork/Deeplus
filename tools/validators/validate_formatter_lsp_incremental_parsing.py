#!/usr/bin/env python3
"""Validate the R28 formatter/LSP/incremental parsing design contract."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/formatter-lsp-incremental-parsing-contract-r1.json"
SCHEMA_REL = "schemas/language/formatter-lsp-incremental-parsing.schema.json"
FIXTURE_REL = "tests/fixtures/current/formatter-lsp-incremental-parsing-r1.json"
REGISTRY_REL = "spec/contracts/grammar-production-disposition-registry-r1.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
RECOVERY_REL = "spec/contracts/frontend-recovery-invalid-tree-contract-r1.json"
FORMATTER_FEATURE_REL = "spec/features/catalog/chunks/part-0006.json"
LSP_FEATURE_REL = "spec/features/catalog/chunks/part-0008.json"
BASELINE_COMMIT = "39a5d50cc770341c4b9776d00d84520b780d0c62"
BASELINE_TREE = "b19b2a86c0f29c1f73763c8526a3a7bde23d530a"
CHECK_IDS = (
    "R28_CONTRACT_IDENTITY",
    "R28_SCHEMA_BINDING",
    "R77_FORMATTING_TOTAL_656",
    "R28_FORMATTING_DISJOINT_COUNTS",
    "R28_ACTOR_ROWS_EXACT_5",
    "R28_RECOVERY_RANGE_FENCE",
    "R28_IDENTITY_DOMAIN_SEPARATION",
    "R28_EDIT_SNAPSHOT_CONCURRENCY",
    "R28_LSP_COORDINATE_ACTION_FENCE",
    "R28_DIAGNOSTIC_PARITY_PRECEDENCE",
    "R28_ORACLE_CASES_9",
    "R28_ACCEPTANCE_MATRIX_34",
    "R28_MUTATIONS_12",
    "R28_GOVERNANCE_FENCE",
)
EXPECTED_RULE_COUNTS = {
    "FD-01": 54,
    "FD-02": 33,
    "FD-03": 333,
    "FD-04": 205,
    "FD-05": 12,
    "FD-06": 19,
}
EXPECTED_ACTOR_RULES = {
    "ActorProtocolConformanceClause": "FD-04",
    "ActorProtocolConformBlock": "FD-04",
    "ActorMemberDecl": "FD-03",
    "ActorProtocolConformanceBody": "FD-03",
    "ActorProtocolConformanceItem": "FD-03",
}
EXPECTED_CASE_IDS = (
    "IR-R3-GAP-10-P",
    "R28-P-REUSE-001",
    "R28-P-LSP-001",
    "IR-R3-GAP-10-B",
    "R28-B-ASCENT-001",
    "R28-B-RECOVERY-SIBLING-001",
    "IR-R3-GAP-10-N",
    "R28-N-RANGE-001",
    "R28-N-REUSE-001",
)
EXPECTED_MUTATION_IDS = (
    "R28-M-01-DROP-FORMATTING-RULE",
    "R28-M-02-OVERLAP-FORMATTING-RULE",
    "R28-M-03-ALLOW-FORMATTER-TAINT-CLEAR",
    "R28-M-04-ALLOW-OUTSIDE-RANGE-EDIT",
    "R28-M-05-CONFLATE-IDENTITY-DOMAINS",
    "R28-M-06-ACCEPT-STALE-REVISION",
    "R28-M-07-ALLOW-AMBIGUOUS-REUSE",
    "R28-M-08-CLAIM-PRODUCT-PASS",
    "R28-M-09-CONFLATE-AST-OCCURRENCE-SEMANTIC",
    "R28-M-10-OMIT-SNAPSHOT-LEASE",
    "R28-M-11-ALLOW-ACTOR-TOKEN-REWRITE",
    "R28-M-12-ALLOW-R23-ID-FROM-TOOLING-ID",
)
EXPECTED_SUCCESSOR_CASE_IDS = tuple(f"R28R-T{ordinal:02d}" for ordinal in range(1, 35))


def strict_load(path: Path) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        keys = [key for key, _value in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate JSON key in {path}")
        if len(keys) != len({key.casefold() for key in keys}):
            raise ValueError(f"case-fold duplicate JSON key in {path}")
        return dict(pairs)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook)


def matches(row: dict[str, Any], predicate: dict[str, Any]) -> bool:
    for key, expected in predicate.items():
        if key.endswith("_not"):
            if row.get(key[:-4]) == expected:
                return False
        elif row.get(key) != expected:
            return False
    return True


def classify_rows(
    contract: dict[str, Any], registry: dict[str, Any]
) -> tuple[Counter[str], list[str], list[str]]:
    rules = contract.get("formatting_disposition_function", {}).get("rules", [])
    counts: Counter[str] = Counter()
    unclassified: list[str] = []
    multiply: list[str] = []
    for row in registry.get("production_rows", []):
        selected = [
            rule.get("rule_id")
            for rule in rules
            if matches(row, rule.get("when", {}))
        ]
        if len(selected) == 1:
            counts[selected[0]] += 1
        elif not selected:
            unclassified.append(row.get("production_id", "<missing>"))
        else:
            multiply.append(row.get("production_id", "<missing>"))
    return counts, unclassified, multiply


def evaluate_case(row: dict[str, Any]) -> tuple[str, str | None]:
    operation = row.get("operation")
    value = row.get("input", {})
    if operation == "WHOLE_FILE_FORMAT":
        if not value.get("recovery_taint_empty"):
            return "REJECT_RECOVERY_TAINT", "FORMAT_WHOLE_FILE_RECOVERY_TAINTED"
        if not value.get("normalized_ast_equal"):
            return "REJECT_AST_DRIFT", "FORMAT_AST_EQUIVALENCE_FAILED"
        if value.get("second_pass_edit_count") != 0:
            return "REJECT_NONIDEMPOTENT", "FORMAT_IDEMPOTENCE_FAILED"
        return "ACCEPT_AST_EQUIVALENCE", None
    if operation == "RANGE_FORMAT":
        if not value.get("one_smallest_recovery_free_owner"):
            return (
                "REJECT_RANGE_INTERSECTS_RECOVERY_TAINT",
                "FORMAT_RANGE_INTERSECTS_RECOVERY_TAINT",
            )
        if not value.get("outside_interval_bytes_unchanged"):
            return "REJECT_EDIT_ESCAPES_OWNER", "FORMAT_EDIT_ESCAPES_OWNER"
        if not value.get("complete_token_boundary") or not value.get(
            "normalized_ast_equal"
        ):
            return "REJECT_AST_DRIFT", "FORMAT_AST_EQUIVALENCE_FAILED"
        if value.get("second_pass_edit_count") != 0:
            return "REJECT_NONIDEMPOTENT", "FORMAT_IDEMPOTENCE_FAILED"
        return "ACCEPT_BOUNDED_FORMAT", None
    if operation == "INCREMENTAL_NODE_REUSE":
        if not value.get("document_revision_matches"):
            return (
                "REJECT_STALE_INCREMENTAL_NODE",
                "INCREMENTAL_STALE_DOCUMENT_REVISION",
            )
        required = (
            "contract_digests_match",
            "production_and_content_match",
            "token_trivia_partition_match",
            "recovery_taint_identity_match",
            "outside_replaced_interval_or_unchanged_child",
            "parent_reuse_or_selected_root",
        )
        if not all(value.get(key) for key in required):
            return "REJECT_REUSE_PROOF", "INCREMENTAL_SPLICE_GATE_FAILED"
        if value.get("mapping_cardinality") != "ONE_TO_ONE":
            return (
                "REJECT_AMBIGUOUS_NODE_REUSE",
                "INCREMENTAL_NODE_REUSE_AMBIGUOUS",
            )
        return "ACCEPT_REUSE_HANDLE", None
    if operation == "NODE_HANDLE_LOOKUP":
        if not value.get("document_revision_matches"):
            return (
                "REJECT_STALE_INCREMENTAL_NODE",
                "INCREMENTAL_STALE_DOCUMENT_REVISION",
            )
        if value.get("mapping_cardinality") != "ONE_TO_ONE":
            return (
                "REJECT_AMBIGUOUS_NODE_REUSE",
                "INCREMENTAL_NODE_REUSE_AMBIGUOUS",
            )
        return "ACCEPT_NODE_HANDLE", None
    if operation == "INCREMENTAL_REPARSE":
        if not value.get("document_revision_matches"):
            return "REJECT_STALE_EDIT", "INCREMENTAL_STALE_DOCUMENT_REVISION"
        if not value.get("edit_set_valid"):
            return "REJECT_INVALID_EDIT_SET", "INCREMENTAL_INVALID_EDIT_SET"
        if value.get("initial_owner_splice_gate_passes"):
            return "ACCEPT_INITIAL_OWNER_SPLICE", None
        if value.get("eligible_parent_exists") and value.get(
            "parent_splice_gate_passes"
        ):
            return (
                "ACCEPT_AFTER_DETERMINISTIC_ASCENT",
                "INCREMENTAL_REPARSE_ASCENDED",
            )
        return "REJECT_SPLICE", "INCREMENTAL_SPLICE_GATE_FAILED"
    if operation == "LSP_SEMANTIC_TOKENS":
        if not value.get("document_revision_matches"):
            return "REJECT_STALE_RESULT", "INCREMENTAL_STALE_DOCUMENT_REVISION"
        if not value.get("snapshot_binding_matches"):
            return "REJECT_SNAPSHOT_MISMATCH", "INCREMENTAL_SPLICE_GATE_FAILED"
        if not value.get("exact_tokens_or_recovery_free_fragments"):
            return "REJECT_TAINTED_SEMANTICS", "FORMAT_WHOLE_FILE_RECOVERY_TAINTED"
        return "ACCEPT_VERSION_BOUND_RESULT", None
    return "REJECT_UNKNOWN_OPERATION", "INCREMENTAL_SPLICE_GATE_FAILED"


def contract_errors(
    contract: dict[str, Any],
    schema: dict[str, Any],
    fixtures: dict[str, Any],
    registry: dict[str, Any],
    frontend: dict[str, Any],
    recovery: dict[str, Any],
    formatter_features: list[dict[str, Any]],
    lsp_features: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    baseline = contract.get("baseline", {})
    if (
        contract.get("schema")
        != "deeplus.formatter-lsp-incremental-parsing-contract/r1"
        or contract.get("status")
        != "STABLE_DESIGN_IMPLEMENTATION_READINESS_CANDIDATE"
        or contract.get("candidate_class")
        != "LOCAL_NONCANONICAL_NONACTIVATABLE"
        or baseline.get("commit") != BASELINE_COMMIT
        or baseline.get("tree") != BASELINE_TREE
        or contract.get("gap_id") != "IR-FE-P1-037"
        or contract.get("dependencies") != ["IR-FE-P0-028", "IR-FE-P1-034"]
    ):
        errors.append("contract identity drift")

    rows = registry.get("production_rows", [])
    counts, unclassified, multiply = classify_rows(contract, registry)
    function = contract.get("formatting_disposition_function", {})
    declared_rules = function.get("rules", [])
    declared_counts = {
        row.get("rule_id"): row.get("expected_row_count")
        for row in declared_rules
    }
    schema_properties = schema.get("properties", {})
    if (
        schema_properties.get("formatting_disposition_function", {})
        .get("properties", {})
        .get("expected_total_row_count", {})
        .get("const")
        != 656
        or set(
            schema_properties.get("identity_domains", {}).get("required", [])
        )
        != {
            "DocumentSessionId",
            "DocumentRevisionId",
            "ParseSnapshotId",
            "CstContentId",
            "CstOccurrenceId",
            "IncrementalNodeHandleId",
            "NodeReuseReceipt",
            "NormalizedAstSemanticDigest",
            "forbidden_identity_conflations",
        }
        or schema_properties.get("acceptance", {})
        .get("properties", {})
        .get("successor_case_count", {})
        .get("const")
        != 34
        or schema_properties.get("reason_codes", {}).get("minItems") != 14
        or schema_properties.get("reason_codes", {}).get("maxItems") != 14
    ):
        errors.append("schema successor binding drift")

    if len(rows) != 656 or function.get("expected_total_row_count") != 656:
        errors.append("formatting domain is not exact 656")
    if counts != Counter(EXPECTED_RULE_COUNTS):
        errors.append(f"observed formatting counts drift: {dict(counts)}")
    if declared_counts != EXPECTED_RULE_COUNTS:
        errors.append(f"declared formatting counts drift: {declared_counts}")
    if unclassified or function.get("unclassified_row_count") != 0:
        errors.append(f"unclassified formatting rows: {unclassified[:5]}")
    if multiply or function.get("multiply_classified_row_count") != 0:
        errors.append(f"multiply classified formatting rows: {multiply[:5]}")
    row_by_id = {row.get("production_id"): row for row in rows}
    actor_observed: dict[str, str | None] = {}
    for production_id in EXPECTED_ACTOR_RULES:
        row = row_by_id.get(production_id, {})
        selected = [
            rule.get("rule_id")
            for rule in declared_rules
            if matches(row, rule.get("when", {}))
        ]
        actor_observed[production_id] = selected[0] if len(selected) == 1 else None
    if actor_observed != EXPECTED_ACTOR_RULES:
        errors.append(f"Actor Protocol formatting owner drift: {actor_observed}")
    clause_rhs = row_by_id.get("ActorProtocolConformanceClause", {}).get(
        "normalized_rhs", ""
    )
    conform_rhs = row_by_id.get("ActorProtocolConformBlock", {}).get(
        "normalized_rhs", ""
    )
    if (
        'LineBreakBoundary "conforms" QualifiedTypeReference' not in clause_rhs
        or '"conform" QualifiedTypeReference' not in conform_rhs
    ):
        errors.append("Actor Protocol token or line-boundary fence drift")
    if (
        not function.get("total_and_disjoint")
        or not function.get("ordered_first_match")
        or function.get("default_rewrite") != "PRESERVE_EXACT_SOURCE_BYTES"
        or function.get("undeclared_style_preference_count") != 0
    ):
        errors.append("formatting default or totality fence drift")

    malformed = contract.get("recovery_and_malformed_cst", {})
    recovery_fence = recovery.get("formatter_lsp_fence", {})
    if (
        malformed.get("whole_file_format")
        != "REQUIRE_EMPTY_RECOVERY_TAINT"
        or malformed.get("formatter_may_clear_taint") is not False
        or malformed.get("checker_may_clear_taint") is not False
        or malformed.get("taint_clear_owner")
        != "NEW_PARSE_OF_CHANGED_INPUT_ONLY"
        or malformed.get("recovery_nodes_rewritten_or_removed_by_formatter")
        is not False
        or malformed.get("analysis_only_fragments_advertised_as_canonical")
        is not False
        or recovery_fence.get("whole_file_canonical_format_requires_empty_taint")
        is not True
        or "smallest recovery-free CST subtree"
        not in recovery_fence.get("range_format", "")
        or recovery.get("recovery_taint", {}).get("clear_by_reparse")
        != "only a new parse over changed input may remove taint; a checker or formatter cannot clear it"
    ):
        errors.append("recovery/formatter authority fence drift")

    identities = contract.get("identity_domains", {})
    forbidden = identities.get("forbidden_identity_conflations", [])
    if (
        set(identities)
        != {
            "DocumentSessionId",
            "DocumentRevisionId",
            "ParseSnapshotId",
            "CstContentId",
            "CstOccurrenceId",
            "IncrementalNodeHandleId",
            "NodeReuseReceipt",
            "NormalizedAstSemanticDigest",
            "forbidden_identity_conflations",
        }
        or identities.get("NodeReuseReceipt", {}).get("old_to_new_cardinality")
        != "ONE_TO_ONE_ONLY"
        or len(forbidden) != 6
        or "CstContentId == CstOccurrenceId" not in forbidden
        or "CstOccurrenceId == IncrementalNodeHandleId" not in forbidden
        or "AstNodeId == NormalizedAstSemanticDigest" not in forbidden
        or identities.get("CstOccurrenceId", {}).get("cross_revision_stability")
        is not False
        or identities.get("NormalizedAstSemanticDigest", {}).get(
            "parse_format_parse_equality_authority"
        )
        is not True
        or any(
            identities.get(key, {}).get("canonical_residue") is not False
            for key in (
                "DocumentSessionId",
                "DocumentRevisionId",
                "ParseSnapshotId",
                "CstContentId",
                "CstOccurrenceId",
                "IncrementalNodeHandleId",
                "NormalizedAstSemanticDigest",
            )
        )
    ):
        errors.append("tooling identity domain separation drift")

    reparse = contract.get("incremental_reparse", {})
    if (
        len(reparse.get("reparse_owner_eligibility", [])) != 3
        or len(reparse.get("mandatory_ascent_conditions", [])) != 9
        or len(reparse.get("splice_gate", [])) != 7
        or reparse.get("whole_document_mix_of_snapshot_count") != 1
        or reparse.get("edit_input", {}).get("stale_revision")
        != "REJECT_STALE_DOCUMENT_REVISION"
        or "nearest eligible parent" not in reparse.get("ascent", "")
        or "source root" not in reparse.get("root_fallback", "")
        or "compare-and-swap" not in reparse.get("concurrent_edit_publication", "")
        or "ParseSnapshotId" not in reparse.get("snapshot_read_lease", "")
        or "still current" not in reparse.get("late_result_publication", "")
    ):
        errors.append("incremental reparse algorithm drift")

    range_format = contract.get("range_format", {})
    if (
        range_format.get("outside_interval_bytes_unchanged") is not True
        or range_format.get("source_role_profile_unchanged") is not True
        or range_format.get("parse_format_parse_normalized_ast_equivalence")
        != "EQUAL_NORMALIZED_AST_SEMANTIC_DIGEST_AND_TYPED_HIR_SEMANTIC_IDENTITIES"
        or range_format.get("second_pass_edit_count") != 0
        or range_format.get("replacement_count") != 1
        or range_format.get("no_recovery_free_owner")
        != "REJECT_RANGE_INTERSECTS_RECOVERY_TAINT"
    ):
        errors.append("range formatting fence drift")

    lsp = contract.get("lsp_snapshot_fence", {})
    if (
        len(lsp.get("request_binding", [])) != 10
        or lsp.get("stale_request_or_result")
        != "REJECT_STALE_DOCUMENT_REVISION"
        or lsp.get("cross_revision_result_merge_count") != 0
        or "recovery-free" not in lsp.get("semantic_tokens", "")
        or "zero-based half-open byte intervals" not in lsp.get(
            "internal_span_domain", ""
        )
        or lsp.get("invalid_position") != "REJECT_INVALID_POSITION_WITHOUT_CLAMPING"
        or lsp.get("stale_action_application") != "REJECT_STALE_TOOLING_ACTION"
    ):
        errors.append("LSP snapshot fence drift")

    model_binding = frontend.get("frontend_cst_boundary_recovery_contract", {})
    if (
        model_binding.get("grammar_production_count") != 656
        or model_binding.get("canonical_ast_recovery_node_count") != 0
        or model_binding.get("canonical_hir_recovery_node_count") != 0
        or frontend.get("evidence", {}).get("formatter_lsp") != "NOT_RUN"
        or frontend.get("evidence", {}).get("incremental_parser")
        != "NOT_RUN"
    ):
        errors.append("frontend prerequisite binding drift")

    r28_binding = frontend.get("formatter_lsp_incremental_parsing_contract", {})
    if r28_binding != {
        "contract": CONTRACT_REL,
        "schema": SCHEMA_REL,
        "fixtures": FIXTURE_REL,
        "gap_id": "IR-FE-P1-037",
        "baseline": {
            "repository": "howork/Deeplus",
            "branch": "main",
            "commit": BASELINE_COMMIT,
            "tree": BASELINE_TREE,
        },
        "grammar_production_count": 656,
        "formatting_rule_count": 6,
        "formatting_rule_counts": EXPECTED_RULE_COUNTS,
        "identity_domain_count": 8,
        "existing_oracle_case_count": 9,
        "successor_acceptance_case_count": 34,
        "mutation_count": 12,
        "normalized_ast_semantic_identity": "NormalizedAstSemanticDigest",
        "tooling_identity_separation": {
            "content": "CstContentId",
            "occurrence": "CstOccurrenceId",
            "incremental_handle": "IncrementalNodeHandleId",
            "content_occurrence_handle_conflation_count": 0,
        },
        "snapshot_publication_and_lifetime": {
            "snapshot_identity": "ParseSnapshotId",
            "publication": "ATOMIC_COMPARE_AND_SWAP_EXPECTED_DOCUMENT_REVISION_AND_PARSE_SNAPSHOT",
            "read_lease_required": True,
            "reclamation_gate": "ZERO_CURRENT_DOCUMENT_ACTIVE_REQUEST_OR_REUSE_RECEIPT_LEASES",
            "late_result_publication": "REVISION_AND_SNAPSHOT_MUST_STILL_BE_CURRENT",
        },
        "lsp_coordinate_and_action_fence": {
            "internal_span_domain": "ZERO_BASED_HALF_OPEN_BYTE_INTERVAL_IN_EXACT_SNAPSHOT",
            "position_conversion": "NEGOTIATED_POSITION_ENCODING_PLUS_SNAPSHOT_LINE_MAP_DIGEST",
            "invalid_position": "REJECT_INVALID_POSITION_WITHOUT_CLAMPING",
            "action_binding": "EXPECTED_DOCUMENT_REVISION_PARSE_SNAPSHOT_INTERVAL_AND_OLD_INTERVAL_SHA256",
            "stale_action_application": "REJECT_STALE_TOOLING_ACTION",
        },
        "diagnostic_parity_and_precedence": {
            "incremental_equals_full_parse_for_same_snapshot": True,
            "merge_order": "CANONICAL_RECOVERY_ORDER_NOT_WORKER_COMPLETION_ORDER",
            "tooling_failure_precedence": [
                "REQUEST_SCHEMA_AND_DOCUMENT_IDENTITY",
                "STALE_REVISION_OR_SNAPSHOT",
                "EDIT_AND_COORDINATE_VALIDITY",
                "OWNER_AND_RECOVERY_ADMISSION",
                "AST_EQUIVALENCE_IDEMPOTENCE_SPLICE_AND_REUSE_PROOF",
            ],
        },
        "actor_protocol_five_row_preservation": {
            "production_ids": [
                "ActorProtocolConformanceClause",
                "ActorMemberDecl",
                "ActorProtocolConformBlock",
                "ActorProtocolConformanceBody",
                "ActorProtocolConformanceItem",
            ],
            "production_count": 5,
            "formatting_rule_counts": {"FD-03": 3, "FD-04": 2},
            "token_rewrite_count": 0,
            "tooling_identity_in_r23_actor_or_binding_preimage_count": 0,
        },
        "formatting_fallback": "PRESERVE_EXACT_SOURCE_BYTES",
        "recovery_taint_clear_owner": "NEW_PARSE_OF_CHANGED_INPUT_ONLY",
        "incremental_owner_selection": "SMALLEST_ELIGIBLE_OWNER_WITH_DETERMINISTIC_PARENT_ASCENT_AND_SOURCE_ROOT_FALLBACK",
        "range_format_outside_byte_change_count": 0,
        "cross_revision_result_merge_count": 0,
        "source_syntax_change_count": 0,
        "grammar_production_change_count": 0,
        "language_semantic_change_count": 0,
        "new_final_diagnostic_id_count": 0,
        "semantic_p0": 0,
        "canonical_feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "formatter_lsp_execution": "NOT_RUN",
        "incremental_parser_execution": "NOT_RUN",
    }:
        errors.append("frontend R28 contract binding drift")

    expected_artifacts = [CONTRACT_REL, SCHEMA_REL, FIXTURE_REL]
    expected_formatter_artifacts = [
        *expected_artifacts,
        "spec/contracts/ownership-tooling-obligations-r1.json",
        "schemas/language/ownership-tooling-obligations-r1.schema.json",
        "schemas/language/ownership-tooling-obligations-fixtures-r1.schema.json",
        "tests/fixtures/current/ownership-tooling-obligations-r1.json",
        "decisions/language/Design_Deeplus_Ownership_Tooling_Projection_R1.md",
    ]
    feature_rows = {
        row.get("feature_id"): row
        for row in [*formatter_features, *lsp_features]
        if isinstance(row, dict)
    }
    for feature_id in (
        "formatter_lsp_responsibility_card",
        "lsp_responsibility_card",
    ):
        row = feature_rows.get(feature_id, {})
        expected_row_artifacts = (
            expected_formatter_artifacts
            if feature_id == "formatter_lsp_responsibility_card"
            else expected_artifacts
        )
        if (
            row.get("artifact_trace_refs") != expected_row_artifacts
            or row.get("formatter_lsp") != "NOT_RUN"
            or row.get("product_support") != "NOT_RUN"
            or row.get("production_parser") != "NOT_RUN"
        ):
            errors.append(f"R28 tooling feature binding drift: {feature_id}")

    cases = fixtures.get("cases", [])
    case_ids = [row.get("test_id") for row in cases]
    if case_ids != list(EXPECTED_CASE_IDS):
        errors.append(f"acceptance case identity drift: {case_ids}")
    if Counter(row.get("class") for row in cases) != {
        "positive": 3,
        "boundary": 3,
        "negative": 3,
    }:
        errors.append("acceptance class count drift")
    for row in cases:
        observed = evaluate_case(row)
        expected = (row.get("expected_result"), row.get("reason_code_or_null"))
        if observed != expected:
            errors.append(
                f"fixture oracle drift {row.get('test_id')}: {observed} != {expected}"
            )

    successor_cases = fixtures.get("successor_acceptance_matrix", [])
    successor_case_ids = [row.get("test_id") for row in successor_cases]
    if (
        successor_case_ids != list(EXPECTED_SUCCESSOR_CASE_IDS)
        or len(set(successor_case_ids)) != 34
        or any(
            not isinstance(row.get("scenario"), str)
            or not row.get("scenario")
            or not isinstance(row.get("expected"), str)
            or not row.get("expected")
            or row.get("class") not in {"positive", "boundary", "negative"}
            for row in successor_cases
        )
        or contract.get("acceptance", {}).get("successor_case_range")
        != "R28R-T01..R28R-T34"
        or contract.get("acceptance", {}).get("successor_case_count") != 34
    ):
        errors.append("successor acceptance matrix drift")

    mutations = fixtures.get("mutations", [])
    mutation_ids = [row.get("mutation_id") for row in mutations]
    if mutation_ids != list(EXPECTED_MUTATION_IDS) or any(
        row.get("expected") != "REJECT" for row in mutations
    ):
        errors.append("mutation identity or expected disposition drift")
    if contract.get("acceptance", {}).get("mutation_ids") != list(
        EXPECTED_MUTATION_IDS
    ):
        errors.append("contract mutation binding drift")

    governance = contract.get("governance", {})
    if governance != {
        "semantic_p0": 0,
        "canonical_feature_p1": "22_OPEN_UNCHANGED",
        "separate_m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "source_syntax_change_count": 0,
        "grammar_production_change_count": 0,
        "language_semantic_change_count": 0,
        "production_formatter_lsp_incremental_parser": "NOT_RUN",
        "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION",
    }:
        errors.append("governance or evidence fence drift")
    diagnostic = contract.get("diagnostic_policy", {})
    if (
        diagnostic.get("reason_codes_are_final_registry_ids") is not False
        or diagnostic.get("new_final_diagnostic_id_count") != 0
        or diagnostic.get("automatic_semantic_fix_count") != 0
        or len(contract.get("reason_codes", [])) != 14
        or len(set(contract.get("reason_codes", []))) != 14
        or diagnostic.get("incremental_full_parse_diagnostic_order_parity")
        is not True
        or diagnostic.get("tooling_failure_precedence")
        != [
            "request, schema, and document identity",
            "stale revision or snapshot",
            "edit and coordinate validity",
            "owner and recovery admission",
            "AST equivalence, idempotence, splice, and reuse proof",
        ]
    ):
        errors.append("diagnostic reason-code fence drift")
    execution = fixtures.get("execution", {})
    if execution != {
        "design_static_projection": "PASS",
        "production_formatter": "NOT_RUN",
        "production_lsp": "NOT_RUN",
        "production_incremental_parser": "NOT_RUN",
        "product_lanes": "15_OF_15_NOT_RUN",
        "semantic_p0": 0,
        "open_feature_p1_count": 22,
    }:
        errors.append("fixture execution evidence drift")
    return errors


def mutation_results(
    contract: dict[str, Any],
    schema: dict[str, Any],
    fixtures: dict[str, Any],
    registry: dict[str, Any],
    frontend: dict[str, Any],
    recovery: dict[str, Any],
    formatter_features: list[dict[str, Any]],
    lsp_features: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for mutation_id in EXPECTED_MUTATION_IDS:
        candidate = copy.deepcopy(contract)
        if mutation_id == "R28-M-01-DROP-FORMATTING-RULE":
            candidate["formatting_disposition_function"]["rules"].pop()
        elif mutation_id == "R28-M-02-OVERLAP-FORMATTING-RULE":
            candidate["formatting_disposition_function"]["rules"][1]["when"] = (
                copy.deepcopy(
                    candidate["formatting_disposition_function"]["rules"][0]["when"]
                )
            )
        elif mutation_id == "R28-M-03-ALLOW-FORMATTER-TAINT-CLEAR":
            candidate["recovery_and_malformed_cst"]["formatter_may_clear_taint"] = True
        elif mutation_id == "R28-M-04-ALLOW-OUTSIDE-RANGE-EDIT":
            candidate["range_format"]["outside_interval_bytes_unchanged"] = False
        elif mutation_id == "R28-M-05-CONFLATE-IDENTITY-DOMAINS":
            candidate["identity_domains"]["forbidden_identity_conflations"].remove(
                "CstContentId == CstOccurrenceId"
            )
        elif mutation_id == "R28-M-06-ACCEPT-STALE-REVISION":
            candidate["lsp_snapshot_fence"]["stale_request_or_result"] = "ACCEPT"
        elif mutation_id == "R28-M-07-ALLOW-AMBIGUOUS-REUSE":
            candidate["identity_domains"]["NodeReuseReceipt"][
                "old_to_new_cardinality"
            ] = "ONE_OR_MANY"
        elif mutation_id == "R28-M-08-CLAIM-PRODUCT-PASS":
            candidate["governance"]["production_formatter_lsp_incremental_parser"] = (
                "PASS"
            )
        elif mutation_id == "R28-M-09-CONFLATE-AST-OCCURRENCE-SEMANTIC":
            candidate["identity_domains"]["forbidden_identity_conflations"].remove(
                "AstNodeId == NormalizedAstSemanticDigest"
            )
        elif mutation_id == "R28-M-10-OMIT-SNAPSHOT-LEASE":
            candidate["incremental_reparse"]["snapshot_read_lease"] = "OMITTED"
        elif mutation_id == "R28-M-11-ALLOW-ACTOR-TOKEN-REWRITE":
            candidate["formatting_disposition_function"]["default_rewrite"] = (
                "ALLOW_ACTOR_TOKEN_REWRITE"
            )
        elif mutation_id == "R28-M-12-ALLOW-R23-ID-FROM-TOOLING-ID":
            candidate["identity_domains"]["forbidden_identity_conflations"].remove(
                "tooling identity participates in R23 Actor or binding identity preimage"
            )
        rejected = bool(
            contract_errors(
                candidate,
                schema,
                fixtures,
                registry,
                frontend,
                recovery,
                formatter_features,
                lsp_features,
            )
        )
        results.append({"mutation_id": mutation_id, "rejected": rejected})
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        contract = strict_load(root / CONTRACT_REL)
        schema = strict_load(root / SCHEMA_REL)
        fixtures = strict_load(root / FIXTURE_REL)
        registry = strict_load(root / REGISTRY_REL)
        frontend = strict_load(root / FRONTEND_REL)
        recovery = strict_load(root / RECOVERY_REL)
        formatter_features = strict_load(root / FORMATTER_FEATURE_REL)
        lsp_features = strict_load(root / LSP_FEATURE_REL)
        errors = contract_errors(
            contract,
            schema,
            fixtures,
            registry,
            frontend,
            recovery,
            formatter_features,
            lsp_features,
        )
        mutations = mutation_results(
            contract,
            schema,
            fixtures,
            registry,
            frontend,
            recovery,
            formatter_features,
            lsp_features,
        )
        if any(not row["rejected"] for row in mutations):
            errors.append("one or more R28 mutations survived")
        counts, unclassified, multiply = classify_rows(contract, registry)
        cases = fixtures.get("cases", [])
        checks = [
            {"check_id": check_id, "pass": not errors}
            for check_id in CHECK_IDS
        ]
        result = "PASS" if not errors else "FAIL"
        receipt = {
            "schema": "deeplus.r28-formatter-lsp-incremental-validation-receipt/r1",
            "result": result,
            "mode": "SELF_TEST" if args.self_test else "VALIDATE",
            "evidence_level": "E2_STATIC_CLOSURE",
            "check_scope": "R28_FORMATTER_LSP_INCREMENTAL_EXACT",
            "check_count": len(CHECK_IDS),
            "passed_check_count": sum(row["pass"] for row in checks),
            "checks": checks,
            "grammar_production_count": len(registry.get("production_rows", [])),
            "formatting_rule_count": len(
                contract.get("formatting_disposition_function", {}).get("rules", [])
            ),
            "formatting_rule_counts": dict(sorted(counts.items())),
            "unclassified_production_count": len(unclassified),
            "multiply_classified_production_count": len(multiply),
            "identity_domain_count": 8,
            "forbidden_identity_conflation_count": 6,
            "acceptance_case_count": len(cases),
            "acceptance_class_counts": dict(
                sorted(Counter(row.get("class") for row in cases).items())
            ),
            "successor_acceptance_case_count": len(
                fixtures.get("successor_acceptance_matrix", [])
            ),
            "mutation_count": len(mutations),
            "rejected_mutation_count": sum(row["rejected"] for row in mutations),
            "source_syntax_change_count": 0,
            "grammar_production_change_count": 0,
            "language_semantic_change_count": 0,
            "new_final_diagnostic_id_count": 0,
            "product_execution": "NOT_RUN",
            "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION",
            "errors": errors,
        }
    except Exception as exc:  # noqa: BLE001
        receipt = {
            "schema": "deeplus.r28-formatter-lsp-incremental-validation-receipt/r1",
            "result": "FAIL",
            "mode": "SELF_TEST" if args.self_test else "VALIDATE",
            "evidence_level": "E2_STATIC_CLOSURE",
            "check_scope": "R28_FORMATTER_LSP_INCREMENTAL_EXACT",
            "check_count": len(CHECK_IDS),
            "passed_check_count": 0,
            "checks": [
                {"check_id": check_id, "pass": False} for check_id in CHECK_IDS
            ],
            "product_execution": "NOT_RUN",
            "github_publication": "SUSPENDED_UNTIL_FURTHER_USER_INSTRUCTION",
            "errors": [str(exc)],
        }
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=False))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
