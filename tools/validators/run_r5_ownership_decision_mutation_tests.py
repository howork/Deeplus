#!/usr/bin/env python3
"""Static R5 ownership projection and mutation validator.

This is a proposed canonical source file.  It performs deterministic static
validation only.  It does not invoke a Deeplus parser, checker, compiler, or
runtime, and every receipt therefore reports product_execution=NOT_RUN.

The R6 authoring bundle contains four authority payloads that are not among the
six proposed canonical projection paths.  When ``--projection-root`` points at
that immutable bundle, those payloads are loaded and byte-bound.  In canonical
mode their narrowly required values are represented by constants explicitly
labelled NONCANONICAL_ACCEPTANCE_ORACLE_ONLY; those constants are acceptance
oracles, never evidence that a production implementation ran.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


WORKSPACE_SCHEMA = (
    "deeplus.r5-ownership-decision-workspace-validation/v1"
)
FULL_SCHEMA = "deeplus.r5-ownership-decision-mutation-validation/v1"
MUTATION_SCHEMA = "deeplus.r5-ownership-binding-mutation-receipt/v1"
PASSED_CHECK_ID_SCOPE = "R5_OWNERSHIP_EXACT_13"
NONCANONICAL_ORACLE = "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY"
PRODUCT_EXECUTION = "NOT_RUN"

WORKSPACE_CHECK_IDS = (
    "R5_OWN_012_SURFACE_OWNER_PARTITION",
    "R5_OWN_012_CONTEXT_ANCHOR_EXACT_7",
    "R5_OWN_012_HIR_H1_BYTE_FENCE",
    "R5_OWN_013_PREDICATE_UNION_EXACT_2",
    "R5_OWN_013_PREDICATE_OVERRIDE_EXACT_3",
    "R5_OWN_013_SCHEMA_CLOSED_INPUT",
    "R5_OWN_013_FIXTURE_33_AND_CATALOG_19",
    "R5_OWN_013_PROFILE_B_EXACT",
    "R5_OWN_014_REASON_KEY_EXACT_4",
    "R5_OWN_014_PRIMARY_ROUTE_EXACT_1",
    "R5_OWN_014_BINDING_MUTATIONS_EXACT_7",
    "R5_OWN_014_RESIDUAL_DEBT_EXACT_12",
    "R5_OWN_GOVERNANCE_FENCE",
)

EXPECTED_FILE_SHA256 = {
    "borrow_contract": (
        "c30af2580828f3c35b701c915691ec253cb869632e9b080791d7fc4128da9b49"
    ),
    "escape_contract": (
        "a2424dff3fc49ffa96f7906b9185d8df56c32efe163f220b43af8d7c93c09e52"
    ),
    "acceptance_spec": (
        "e9b7587c329ffe4bbcfaab4b56753f54201b7789b31ef9cb1892dc642c8c827b"
    ),
    "authoring_fixture": (
        "1feb1dbb44d28305a718730ca83195724fdb43e550320549a90c05835fcc78af"
    ),
    "ownership_contract": (
        "c6964c39582a37c711bfd32b8d1fda7d71340885f381f20ff518a1de73408c4b"
    ),
    "shape_amendment": (
        "40f41749a18b13c421ecc8703eb9a927770ff3802ace6e3186268e7c4016848d"
    ),
    "input_schema": (
        "36669316d2902deff62987586f2d9090764c834a01ae42b7ecd5a3c51db37234"
    ),
    "union_schema": (
        "658e6ed1ce69c0711c73f034c05738d2f1c1d5596c0635f508fa08d5a255202f"
    ),
    "fixture_schema": (
        "a8ecba527d037fda1f8659867df3b5098c9b7c90184ad8bc0c583edfb2f89186"
    ),
    "row_schema": (
        "5426d87f0c7c5bc38a77b7408c5a79f2206ecda5da730613899437003bc3c46f"
    ),
    "canonical_fixture": (
        "03423fcd0406b9bb267446c3c46cb646b6b3b05a4d66bbb021a58129d3689527"
    ),
    "conformance_rows": (
        "95cbbb6a679a486511daa3359277f185775ac9c42a0cb47991c64fa2c23b47bb"
    ),
}

EXPECTED_CANONICAL_JSON_SHA256 = {
    "authoring_fixture": (
        "65e4b1f95ea16ecdd72633c88e88b9384c425ff7ee9f7ee6f698080251485ca8"
    ),
    "canonical_fixture": (
        "b6e4a47f8d28ee3ba0a015864a151d3be9afd79809034665e2c9759f9a4e47aa"
    ),
    "conformance_rows": (
        "f1145890638f875d5c440a1c66be053bad0f97d774c2baa524cac4d5b112d847"
    ),
}

HIR_H1_FENCE = {
    "spec/contracts/hir-h1-current-mir-bridge.json": (
        "aaa20e2cb7f4135fc6686eeb73d768fe453cab254e0f7be47639a12f92dfcd5e"
    ),
    "schemas/language/hir-h1-current-mir-bridge-fixtures.schema.json": (
        "4ad4bbbd975cbb3cdd7ce31bc693d8bd507fc7c85367996c47d09abc56d15de5"
    ),
    "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json": (
        "ed1c4abd91a0276359511877a783686dfff77851bbffecdeeb4bfca681d7881c"
    ),
}

SURFACE_OWNERS = [
    {
        "parse_goal": "expression",
        "fixity": "prefix",
        "spelling": "borrow",
        "cst": "BorrowExprCst",
        "ast": "BorrowExpr",
        "hir": (
            "HirExprKind::PlaceAccess{plan:HirPlacePlan("
            "access=BorrowShared)}"
        ),
        "semantic_owner": "shared_ownership_borrow",
    },
    {
        "parse_goal": "expression",
        "fixity": "prefix",
        "spelling": "&",
        "cst": "ContextAnchorOperandCst",
        "ast": "ContextAnchorCandidateExpr",
        "hir": (
            "absorbed_into_HirContextAdaptationPlan_owned_by_"
            "enclosing_operation"
        ),
        "semantic_owner": "registered_operation_local_context_anchor",
    },
    {
        "parse_goal": "type",
        "fixity": "infix",
        "spelling": "&",
        "cst": "IntersectionTypeCst",
        "ast": "IntersectionType",
        "hir": "compile_time_type_identity",
        "semantic_owner": "closed_contract_intersection_type_msp",
    },
]

SURFACE_FEATURE_IDS = {
    "borrow_escape_law_phase_a",
    "region_lifetime_model_phase_a",
    "context_evidence_anchor_framework",
    "numeric_array_context_anchor_msp",
    "measure_context_anchor_msp",
    "closed_contract_intersection_type_msp",
}

CONTEXT_ACCEPTANCE_IDS = [
    "OWN-SURF-P-001",
    "OWN-SURF-P-002",
    "OWN-SURF-N-005",
    "OWN-SURF-M-007",
    "OWN-GAP-P-012",
    "OWN-GAP-B-012",
    "OWN-GAP-N-012",
]

BORROW_ZERO_COUNTS = {
    "borrow_to_context_fallback": 0,
    "context_anchor_to_borrow_fallback": 0,
    "type_intersection_to_expression_route": 0,
    "address_of_route": 0,
    "runtime_role_lookup": 0,
    "implicit_provider_search": 0,
    "authority_synthesis": 0,
    "witness_synthesis": 0,
    "context_anchor_first_class_value": 0,
    "context_anchor_ownership_borrow_events": 0,
    "automatic_borrow_ampersand_rewrite": 0,
}

UNION_REFS = [
    {"$ref": "rcts-v5-descriptor.schema.json"},
    {"$ref": "ownership-decision-input-r1.schema.json"},
]
OWNERSHIP_OVERRIDE_IDS = [
    "BorrowEscapeAdmitted",
    "BoxOwnershipAdmitted",
    "OwnershipModeAdmitted",
]
R9_DIAGNOSTIC_OVERRIDE_IDS = [
    "AssociatedRequirementAdmitted",
    "EffectErrorRowPolymorphismAdmitted",
    "EffectRowSubsumes",
]
INSTALLED_OVERRIDE_IDS = [
    *OWNERSHIP_OVERRIDE_IDS,
    *R9_DIAGNOSTIC_OVERRIDE_IDS,
]
R41_ACTOR_PROTOCOL_OVERRIDE_IDS = ["ActorProtocolGateAdmitted"]
R41_INSTALLED_OVERRIDE_IDS = [
    *INSTALLED_OVERRIDE_IDS,
    *R41_ACTOR_PROTOCOL_OVERRIDE_IDS,
]
# Historical authoring-bundle checks still bind the original three ownership
# overrides. Installed-current checks below bind all six exact overrides.
OVERRIDE_IDS = OWNERSHIP_OVERRIDE_IDS
INPUT_FIELDS = [
    "schema",
    "predicate_id",
    "type_descriptors",
    "place_graph",
    "state_graph",
    "loan_region_graph",
    "cfg",
    "operation",
    "escape_context",
    "isolation_context",
    "cleanup_context",
]
OPERATION_NAMES = [
    "Initialize",
    "Read",
    "Write",
    "ReserveMove",
    "CancelReservation",
    "Move",
    "BeginSharedLoan",
    "BeginExclusiveLoan",
    "BeginReborrow",
    "EndLoan",
    "ReplaceInout",
    "Cleanup",
    "Join",
]
OPERATION_DEFS = [
    "opInitialize",
    "opRead",
    "opWrite",
    "opReserveMove",
    "opCancelReservation",
    "opMove",
    "opBeginSharedLoan",
    "opBeginExclusiveLoan",
    "opBeginReborrow",
    "opEndLoan",
    "opReplaceInout",
    "opCleanup",
    "opJoin",
]

ARRAY_SET_FIELDS = [
    "OwnershipDecisionInputR1.type_descriptors",
    "PlaceGraph.places",
    "PlaceGraph.move_paths",
    "PlaceGraph.proofs",
    "MovePathDef.child_move_path_ids",
    "ClosedProof.scope_point_ids",
    "StateGraph.states",
    "StateGraph.operation_prefix_point_ids",
    "OwnershipState.places",
    "OwnershipState.loans",
    "OwnershipState.tokens",
    "OwnershipState.reservations",
    "OwnershipState.join_conflicts",
    "JoinConflict.predecessor_state_ids",
    "JoinConflict.mismatch_axes",
    "JoinConflict.mismatching_places",
    "JoinConflict.covered_places",
    "JoinConflictCoveredPlace.predecessors",
    "LoanRegionGraph.owners",
    "LoanRegionGraph.regions",
    "LoanRegionGraph.loans",
    "LoanRegionGraph.isolation_domains",
    "RegionDef.end_point_ids",
    "LoanDef.view_alias_bindings",
    "LoanDef.end_point_ids",
    "Cfg.point_ids",
    "Cfg.edges",
    "Cfg.accesses",
    "Cfg.predecessor_state_ids",
    "Operation.Initialize.ownership_unit_bindings",
    "Operation.Join.predecessor_state_ids",
    "EscapeContext.proof_ids",
    "IsolationContext.proof_ids",
    "CleanupContext.plans",
    "CleanupContext.tokens",
]
ARRAY_SEQUENCE_FIELDS = [
    "PlaceDef.projections",
    "ClosedProof.subjects",
    "ViewAliasBinding.relative_projection_key",
    "Operation.Cleanup.cleanup_token_ids",
    "CleanupContext.acquisition_order",
    "CleanupPlan.action_keys",
]

FIXTURE_COUNTS = {
    "scenarios": 19,
    "fully_materialized_step_inputs": 27,
    "results": {"ADMIT": 18, "REJECT": 8, "INPUT_INVALID": 1},
    "scenario_classes": {
        "positive": 6,
        "boundary": 5,
        "negative": 7,
        "mutation": 1,
    },
    "supplemental_operation_coverage_steps": 6,
    "supplemental_results": {
        "ADMIT": 5,
        "REJECT": 1,
        "INPUT_INVALID": 0,
    },
    "all_fully_materialized_step_inputs": 33,
    "all_results": {"ADMIT": 23, "REJECT": 9, "INPUT_INVALID": 1},
    "operation_counts_all_inputs": {
        "BeginExclusiveLoan": 5,
        "BeginReborrow": 1,
        "BeginSharedLoan": 2,
        "CancelReservation": 1,
        "Cleanup": 1,
        "EndLoan": 5,
        "Initialize": 1,
        "Join": 3,
        "Move": 5,
        "Read": 4,
        "ReplaceInout": 3,
        "ReserveMove": 1,
        "Write": 1,
    },
}

SUPPLEMENTAL_IDS = [
    "OWN-COVERAGE-INITIALIZE-R5",
    "OWN-COVERAGE-RESERVE-MOVE-R5",
    "OWN-COVERAGE-CANCEL-RESERVATION-R5",
    "OWN-COVERAGE-REPLACE-INOUT-P-R5",
    "OWN-COVERAGE-REPLACE-INOUT-B-R5",
    "OWN-COVERAGE-REPLACE-INOUT-N-R5",
]

REASON_ROUTES = {
    "1_return_outlives_owner_region": "BORROW_ESCAPE_OWNER_REGION",
    "2_store_outlives_owner_region": "BORROW_ESCAPE_OWNER_REGION",
    "3_capture_or_suspension_outlives_owner_region": (
        "BORROW_ESCAPE_OWNER_REGION"
    ),
    "4_isolation_boundary_without_admitted_proof": (
        "BORROW_ESCAPE_OWNER_REGION"
    ),
}
REASON_AXES = {
    "1_return_outlives_owner_region": (
        "escape_context.target_region_id_or_null"
    ),
    "2_store_outlives_owner_region": (
        "escape_context.target_region_id_or_null"
    ),
    "3_capture_or_suspension_outlives_owner_region": (
        "loan_region_graph.loans[*].end_point_ids"
    ),
    "4_isolation_boundary_without_admitted_proof": (
        "isolation_context.proof_ids"
    ),
}
BORROW_DIAGNOSTIC_ID = "BORROW_ESCAPE_OWNER_REGION"
BORROW_RELATION = {
    "violation_id": "BorrowEscapeAdmitted:default",
    "predicate_id": "BorrowEscapeAdmitted",
    "diagnostic_id": BORROW_DIAGNOSTIC_ID,
    "relation": "primary",
}

HISTORICAL_R8_RESIDUAL_DEBT_ROWS = [
    {
        "predicate_id": predicate_id,
        "branch": f"branch_{branch:02d}",
        "target": target,
    }
    for predicate_id, target in (
        (
            "AssociatedRequirementAdmitted",
            "ASSOCIATEDREQUIREMENTADMITTED_NOT_ADMITTED",
        ),
        (
            "EffectErrorRowPolymorphismAdmitted",
            "EFFECTERRORROWPOLYMORPHISMADMITTED_NOT_ADMITTED",
        ),
        ("EffectRowSubsumes", "EFFECTROWSUBSUMES_NOT_ADMITTED"),
    )
    for branch in range(1, 5)
]
INSTALLED_CURRENT_RESIDUAL_DEBT_ROWS: list[dict[str, str]] = []
INSTALLED_CURRENT_RESIDUAL_EXACT_ROWS = {
    "AssociatedRequirementAdmitted": 0,
    "EffectErrorRowPolymorphismAdmitted": 0,
    "EffectRowSubsumes": 0,
}
# Compatibility alias for the immutable R8 authoring/candidate checks in the
# first half of this validator. Current canonical scanning uses the explicit
# installed-current constants above.
RESIDUAL_DEBT_ROWS = HISTORICAL_R8_RESIDUAL_DEBT_ROWS

FEATURE_P1_IDS = {
    "CE-C-P1-001",
    "CE-C-P1-002",
    "CE-C-P1-003",
    "CE-C-P1-004",
    "CE-C-P1-005",
    "CE-C-P1-006",
    "CE-E-P1-001",
    "CE-E-P1-002",
    "CE-E-P1-003",
    "CE-E-P1-004",
    "CE-E-P1-005",
    "CE-E-P1-006",
    "CE-E-P1-007",
    "CE-E-P1-008",
    "TCC-P1-002",
    "TCC-P1-003",
    "TCC-P1-004",
    "TCC-P1-005",
    "TCC-P1-006",
    "TCC-P1-007",
    "TCC-P1-008",
    "SFD-P1-009",
}
M13_IDS = {"M13-A002", "M13-A003", "M13-A004", "M13-A005"}

TYPED_FIXTURE_CHECK_IDS = (
    "exact_19_scenarios",
    "exact_27_inputs",
    "exact_outcome_counts",
    "exact_class_counts",
    "exact_test_identity_set",
    "exact_13_row_operation_access_role_matrix",
    "fixture_simulator_explicitly_bounded_nonproduction",
    "exact_six_supplemental_operation_profiles",
    "declared_counts_exactly_recomputed",
    "closed_top_level_fields",
    "array_field_policy_registry_and_permutation_guards",
    "no_template_or_patch_reference",
    "input_hash_binding",
    "scenario_hash_binding",
    "acceptance_binding_count",
    "acceptance_hash_and_step_binding",
    "all_inputs_have_owner_and_view_place_ids",
    "place_state_type_move_path_loan_reference_integrity",
    "normalized_place_identity_unique_per_input",
    "proof_derivation_digest_recomputed_exactly",
    "fresh_affine_roots_ordered_role_domain_tuple_exact",
    "admit_move_direct_fresh_root_proof_binding",
    "partial_move_nonunion_static_field_identity_exact",
    "current_point_access_roles_exact_bijective",
    "cleanup_complete_owned_closure_access_role_exact",
    "historical_access_facts_excluded_from_current_binding",
    "replace_inout_positive_boundary_reject_exact_call_and_staging",
    "multi_step_semantic_identity_stability",
    "cfg_state_graph_identity_binding",
    "operation_prefix_state_cfg_bijection",
    "operation_context_matrix_exact",
    "escape_context_exact_operation_point_binding",
    "escape_source_region_exact_33_of_33",
    "escape_target_region_exact_33_of_33",
    "escape_source_region_mutants_rejected_33_of_33",
    "escape_target_region_mutants_rejected_33_of_33",
    "escape_boundary_target_origin_recomputable",
    "escape_matrix_schema_fixture_parity",
    "begin_loan_profile_b_valid_contexts_6_of_6",
    "begin_loan_profile_b_forgeries_rejected_18_of_18",
    "begin_loan_profile_b_unlisted_boundaries_input_invalid_8_of_8",
    "begin_loan_profile_b_policy_separation_and_controls",
    "view_alias_and_loan_status_invariants",
    "reborrow_parent_view_transitive_alias_and_active_parent_exact",
    "cleanup_token_per_state_and_holder_invariants",
    "reservation_state_place_bijection",
    "join_mismatch_coverage_and_reference_invariants",
    "join_entry_and_full_entry_predecessor_branch_closure",
    "join_equal_and_mismatch_outputs_independently_simulated",
    "post_join_read_cfg_history_exact",
    "declared_join_predecessor_permutations_executed_identical",
    "structured_evaluator_state_and_conservation_assertions",
    "rejection_and_input_invalid_atomicity_digest_recomputed",
    "all_admit_output_state_digests_independently_recomputed",
    "structured_state_assertions_match_simulated_output",
    "six_multistep_forward_state_digests_independently_recomputed",
    "six_multistep_direct_payload_and_predecessor_step_binding",
    "exact_required_multistep_sequences",
    "state_loan_reservation_join_transition_coverage",
    "exact_rejection_routing",
    "mutation_is_internal_input_invalid",
    "no_duplicate_input_hash",
)


class ValidationError(RuntimeError):
    """The runner could not safely produce ordinary semantic check results."""


@dataclass(frozen=True)
class JsonDocument:
    path: Path
    locator: str
    value: Any
    byte_count: int
    sha256: str


@dataclass
class Environment:
    root: Path
    projection_root: Path | None
    documents: dict[str, JsonDocument | None]
    feature_rows: list[dict[str, Any]]
    predicate_rows: list[dict[str, Any]]
    diagnostic_rows: list[dict[str, Any]]
    relation_rows: list[dict[str, Any]]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _canonical_digest(value: Any) -> str:
    return _sha256(_canonical_bytes(value))


def _detail(value: dict[str, Any]) -> str:
    return _canonical_bytes(value).decode("utf-8")


def _strict_json_bytes(payload: bytes, locator: str) -> Any:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ValidationError(f"{locator}: UTF-8 BOM is forbidden")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        keys = [key for key, _value in pairs]
        if len(keys) != len(set(keys)):
            raise ValidationError(f"{locator}: duplicate JSON key")
        if len(keys) != len({key.casefold() for key in keys}):
            raise ValidationError(f"{locator}: case-fold duplicate JSON key")
        return dict(pairs)

    def reject_noninteger(token: str) -> None:
        raise ValidationError(f"{locator}: noninteger JSON number {token}")

    try:
        return json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=pairs_hook,
            parse_float=reject_noninteger,
            parse_constant=reject_noninteger,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValidationError(f"{locator}: invalid strict JSON: {error}") from error


def _read_json(path: Path, locator: str) -> JsonDocument:
    if not path.is_file() or path.is_symlink():
        raise ValidationError(f"{locator}: missing or nonregular JSON file")
    payload = path.read_bytes()
    return JsonDocument(
        path=path,
        locator=locator,
        value=_strict_json_bytes(payload, locator),
        byte_count=len(payload),
        sha256=_sha256(payload),
    )


def _optional_json(path: Path, locator: str) -> JsonDocument | None:
    if not path.exists():
        return None
    return _read_json(path, locator)


def _first_json(
    candidates: Iterable[tuple[Path, str]],
    logical_name: str,
) -> JsonDocument:
    for path, locator in candidates:
        if path.exists():
            return _read_json(path, locator)
    raise ValidationError(f"{logical_name}: no installed or R6 projection source")


def _chunk_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    chunk_root = root / relative
    if not chunk_root.is_dir() or chunk_root.is_symlink():
        raise ValidationError(f"{relative}: missing canonical chunk directory")
    rows: list[dict[str, Any]] = []
    paths = sorted(chunk_root.glob("*.json"), key=lambda path: path.name)
    if not paths:
        raise ValidationError(f"{relative}: no JSON chunks")
    for path in paths:
        document = _read_json(path, f"{relative}/{path.name}")
        if not isinstance(document.value, list):
            raise ValidationError(f"{document.locator}: chunk root is not array")
        if not all(isinstance(row, dict) for row in document.value):
            raise ValidationError(f"{document.locator}: nonobject chunk row")
        rows.extend(document.value)
    return rows


def _build_environment(
    root_arg: str,
    projection_arg: str | None,
) -> Environment:
    root = Path(root_arg).resolve(strict=True)
    if not root.is_dir():
        raise ValidationError("--root is not a directory")
    projection_root = (
        Path(projection_arg).resolve(strict=True)
        if projection_arg is not None
        else None
    )
    if projection_root is not None and not projection_root.is_dir():
        raise ValidationError("--projection-root is not a directory")

    def projected(relative: str) -> tuple[Path, str]:
        if projection_root is None:
            return root / "__absent_projection__", relative
        return projection_root / relative, (
            f"{projection_root.as_posix()}/{relative}"
        )

    def sources(
        installed: tuple[Path, str],
        projection: tuple[Path, str],
    ) -> list[tuple[Path, str]]:
        # An explicit immutable R6 projection root is the authoring authority.
        # With no projection root, only installed canonical paths are admitted.
        return (
            [projection, installed]
            if projection_root is not None
            else [installed]
        )

    ownership_projected = projected(
        "Codex_Design_Deeplus_R5_Ownership_Decision_Input_Contract_R1.json"
    )
    documents: dict[str, JsonDocument | None] = {
        "ownership_contract": _first_json(
            sources(
                (
                    root / "spec/contracts/ownership-decision-input-r1.json",
                    "spec/contracts/ownership-decision-input-r1.json",
                ),
                ownership_projected,
            ),
            "ownership contract",
        ),
        "input_schema": _first_json(
            sources(
                (
                    root
                    / "schemas/language/"
                    "ownership-decision-input-r1.schema.json",
                    (
                        "schemas/language/"
                        "ownership-decision-input-r1.schema.json"
                    ),
                ),
                projected(
                    "schemas/language/"
                    "ownership-decision-input-r1.schema.json"
                ),
            ),
            "ownership input schema",
        ),
        "union_schema": _first_json(
            sources(
                (
                    root
                    / "schemas/language/"
                    "ownership-predicate-input-r1.schema.json",
                    (
                        "schemas/language/"
                        "ownership-predicate-input-r1.schema.json"
                    ),
                ),
                projected(
                    "schemas/language/"
                    "ownership-predicate-input-r1.schema.json"
                ),
            ),
            "ownership predicate union schema",
        ),
        "fixture_schema": _first_json(
            sources(
                (
                    root
                    / "schemas/language/"
                    "ownership-decision-fixtures-r1.schema.json",
                    (
                        "schemas/language/"
                        "ownership-decision-fixtures-r1.schema.json"
                    ),
                ),
                projected(
                    "schemas/language/"
                    "ownership-decision-fixtures-r1.schema.json"
                ),
            ),
            "ownership fixture schema",
        ),
        "row_schema": _first_json(
            sources(
                (
                    root
                    / "schemas/language/"
                    "ownership-decision-fixture-row-r1.schema.json",
                    (
                        "schemas/language/"
                        "ownership-decision-fixture-row-r1.schema.json"
                    ),
                ),
                projected(
                    "schemas/language/"
                    "ownership-decision-fixture-row-r1.schema.json"
                ),
            ),
            "ownership conformance row schema",
        ),
        "canonical_fixture": _first_json(
            sources(
                (
                    root
                    / "tests/fixtures/current/"
                    "ownership-decision-inputs-r1.json",
                    (
                        "tests/fixtures/current/"
                        "ownership-decision-inputs-r1.json"
                    ),
                ),
                projected(
                    "tests/fixtures/current/"
                    "ownership-decision-inputs-r1.json"
                ),
            ),
            "canonical ownership fixture",
        ),
        "conformance_rows": _first_json(
            sources(
                (
                    root
                    / "tests/conformance/ownership-decisions/chunks/"
                    "part-0001.json",
                    (
                        "tests/conformance/ownership-decisions/chunks/"
                        "part-0001.json"
                    ),
                ),
                projected(
                    "tests/conformance/ownership-decisions/chunks/"
                    "part-0001.json"
                ),
            ),
            "ownership conformance rows",
        ),
        "current_pointer": _read_json(
            root / "current/current-pointer.json",
            "current/current-pointer.json",
        ),
    }
    optional_sources = {
        "borrow_contract": (
            "Codex_Design_Deeplus_R5_Borrow_Context_Anchor_Contract_R1.json"
        ),
        "escape_contract": (
            "Codex_Design_Deeplus_R5_Borrow_Escape_Diagnostic_Contract_R1.json"
        ),
        "acceptance_spec": (
            "Codex_Design_Deeplus_R5_Ownership_Acceptance_Spec_R1.json"
        ),
        "authoring_fixture": (
            "Codex_Design_Deeplus_R5_Ownership_Decision_Fixture_Payloads_R1.json"
        ),
        "shape_amendment": "Canonical_Shape_Amendment_R5.json",
        "r6_receipt": (
            "Codex_Design_Deeplus_R6_Ownership_Handoff_"
            "Reproducibility_Candidate_Receipt_R6.json"
        ),
        "typed_fixture_receipt": (
            "inputs/predecessor-r5/members/"
            "TYPED_FIXTURE_VALIDATION_R1.json"
        ),
    }
    for logical_name, relative in optional_sources.items():
        path, locator = projected(relative)
        documents[logical_name] = (
            _optional_json(path, locator)
            if projection_root is not None
            else None
        )

    return Environment(
        root=root,
        projection_root=projection_root,
        documents=documents,
        feature_rows=_chunk_rows(root, "spec/features/catalog/chunks"),
        predicate_rows=_chunk_rows(root, "spec/types/predicates/chunks"),
        diagnostic_rows=_chunk_rows(root, "spec/diagnostics/catalog/chunks"),
        relation_rows=_chunk_rows(root, "spec/diagnostics/relations/chunks"),
    )


def _doc(environment: Environment, logical_name: str) -> JsonDocument:
    document = environment.documents.get(logical_name)
    if document is None:
        raise ValidationError(f"{logical_name}: required document is absent")
    return document


def _errors(*conditions: tuple[bool, str]) -> list[str]:
    return [message for condition, message in conditions if not condition]


def _authority_detail(
    document: JsonDocument | None,
    embedded_name: str,
) -> dict[str, Any]:
    if document is None:
        return {
            "authority": NONCANONICAL_ORACLE,
            "canonical_implementation_validation": False,
            "source_locator": (
                "tools/validators/"
                "run_r5_ownership_decision_mutation_tests.py"
                f"#{embedded_name}"
            ),
        }
    return {
        "authority": "IMMUTABLE_R6_TOP_LEVEL_R5_PAYLOAD",
        "canonical_implementation_validation": False,
        "source_locator": document.locator,
        "bytes": document.byte_count,
        "sha256": document.sha256,
    }


def _borrow_projection(
    environment: Environment,
) -> tuple[dict[str, Any], dict[str, Any]]:
    document = environment.documents["borrow_contract"]
    if document is None:
        return (
            {
                "surface_owners": copy.deepcopy(SURFACE_OWNERS),
                "zero_counts": copy.deepcopy(BORROW_ZERO_COUNTS),
                "anchor_binding": {
                    "canonical_hir_unresolved_anchor_count": 0,
                    "extra_effect_count": 0,
                    "extra_error_count": 0,
                    "extra_cleanup_count": 0,
                },
                "hir_projection_contract": {
                    "context_anchor": {
                        "loan_id_created": False,
                        "borrow_event_created": False,
                        "runtime_role_lookup_count": 0,
                        "unresolved_role_count": 0,
                    }
                },
            },
            _authority_detail(None, "FROZEN_BORROW_CONTRACT_PROJECTION"),
        )
    return document.value, _authority_detail(
        document, "FROZEN_BORROW_CONTRACT_PROJECTION"
    )


def _acceptance_ids(
    environment: Environment,
) -> tuple[list[str], dict[str, Any]]:
    document = environment.documents["acceptance_spec"]
    if document is None:
        return (
            list(CONTEXT_ACCEPTANCE_IDS),
            _authority_detail(None, "FROZEN_CONTEXT_ACCEPTANCE_IDS"),
        )
    value = document.value["exact_test_ids_by_gap"]["IR-OWN-P0-012"]
    return value, _authority_detail(
        document, "FROZEN_CONTEXT_ACCEPTANCE_IDS"
    )


def _escape_projection(
    environment: Environment,
) -> tuple[dict[str, Any], dict[str, Any]]:
    document = environment.documents["escape_contract"]
    if document is None:
        return (
            {
                "diagnostic_dispatch": copy.deepcopy(REASON_ROUTES),
                "single_mutant_axes": copy.deepcopy(REASON_AXES),
                "public_diagnostic": {
                    "diagnostic_id": BORROW_DIAGNOSTIC_ID,
                    "relation": "BorrowEscapeAdmitted:default",
                    "relation_role": "primary",
                },
                "emitted_primary_count": 1,
                "global_dispatch_debt": {
                    "r5_borrow_escape_unresolved_after_candidate": 0,
                    "outside_r5_gap_id": "IR-DIAG-P0-052",
                    "outside_r5_total": 12,
                    "outside_r5_exact_debt_rows": copy.deepcopy(
                        RESIDUAL_DEBT_ROWS
                    ),
                    "global_zero_totality": "BLOCKED_BY_IR-DIAG-P0-052",
                },
                "product_support": PRODUCT_EXECUTION,
            },
            _authority_detail(None, "FROZEN_ESCAPE_CONTRACT_PROJECTION"),
        )
    return document.value, _authority_detail(
        document, "FROZEN_ESCAPE_CONTRACT_PROJECTION"
    )


def _find_unique(
    rows: list[dict[str, Any]],
    field: str,
    value: str,
    label: str,
) -> dict[str, Any]:
    matches = [row for row in rows if row.get(field) == value]
    if len(matches) != 1:
        raise ValidationError(
            f"{label}: expected one {field}={value}, observed {len(matches)}"
        )
    return matches[0]


def _check_surface_partition(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    borrow, authority = _borrow_projection(environment)
    borrow_document = environment.documents["borrow_contract"]
    feature_ids = {row.get("feature_id") for row in environment.feature_rows}
    errors = _errors(
        (
            borrow_document is None
            or borrow_document.sha256
            == EXPECTED_FILE_SHA256["borrow_contract"],
            "borrow contract byte identity mismatch",
        ),
        (
            borrow.get("surface_owners") == SURFACE_OWNERS,
            "surface owner partition is not the exact ordered three rows",
        ),
        (
            len(
                {
                    (
                        row["parse_goal"],
                        row["fixity"],
                        row["spelling"],
                    )
                    for row in borrow.get("surface_owners", [])
                }
            )
            == 3,
            "surface owner keys are not disjoint",
        ),
        (
            SURFACE_FEATURE_IDS.issubset(feature_ids),
            "installed canonical feature owners are incomplete",
        ),
    )
    return not errors, {
        "source_locators": [
            "spec/features/catalog/chunks/*.json#feature_id",
            authority["source_locator"],
        ],
        "acceptance_oracle": authority,
        "installed_canonical_fields_checked": [
            "feature_id",
        ],
        "expected_owner_count": 3,
        "observed_owner_count": len(borrow.get("surface_owners", [])),
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_context_exact_7(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    borrow, borrow_authority = _borrow_projection(environment)
    acceptance_ids, acceptance_authority = _acceptance_ids(environment)
    acceptance_document = environment.documents["acceptance_spec"]
    context = borrow.get("hir_projection_contract", {}).get(
        "context_anchor", {}
    )
    anchor = borrow.get("anchor_binding", {})
    errors = _errors(
        (
            acceptance_document is None
            or acceptance_document.sha256
            == EXPECTED_FILE_SHA256["acceptance_spec"],
            "acceptance spec byte identity mismatch",
        ),
        (
            acceptance_ids == CONTEXT_ACCEPTANCE_IDS,
            "delegated context-anchor acceptance IDs are not exact seven",
        ),
        (
            borrow.get("zero_counts") == BORROW_ZERO_COUNTS,
            "borrow/context zero-count fence changed",
        ),
        (
            anchor.get("canonical_hir_unresolved_anchor_count") == 0,
            "unresolved standalone context anchor is nonzero",
        ),
        (
            context.get("loan_id_created") is False
            and context.get("borrow_event_created") is False
            and context.get("runtime_role_lookup_count") == 0
            and context.get("unresolved_role_count") == 0,
            "context-anchor HIR zero-fabrication fence changed",
        ),
    )
    return not errors, {
        "source_locators": [
            borrow_authority["source_locator"],
            acceptance_authority["source_locator"],
        ],
        "installed_canonical_path_or_null": None,
        "acceptance_oracle_label": NONCANONICAL_ORACLE,
        "canonical_implementation_validation": False,
        "expected_ids": CONTEXT_ACCEPTANCE_IDS,
        "observed_ids": acceptance_ids,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_hir_h1_fence(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    observed: dict[str, str] = {}
    errors: list[str] = []
    for relative, expected_sha256 in HIR_H1_FENCE.items():
        path = environment.root / relative
        if not path.is_file() or path.is_symlink():
            errors.append(f"{relative}: missing or nonregular")
            continue
        observed[relative] = _sha256(path.read_bytes())
        active_expected_sha256 = (
            R41_HIR_H1_BRIDGE_SHA256
            if relative == "spec/contracts/hir-h1-current-mir-bridge.json"
            else expected_sha256
        )
        if observed[relative] != active_expected_sha256:
            errors.append(f"{relative}: byte fence mismatch")
    fixture_path = (
        environment.root
        / "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json"
    )
    case_count: int | None = None
    if fixture_path.is_file() and not fixture_path.is_symlink():
        fixture = _read_json(
            fixture_path,
            "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json",
        )
        cases = fixture.value.get("cases")
        case_count = len(cases) if isinstance(cases, list) else None
        if case_count != 48:
            errors.append("HIR-H1 fixture case count is not 48")
    shape = environment.documents["shape_amendment"]
    if shape is not None:
        if shape.sha256 != EXPECTED_FILE_SHA256["shape_amendment"]:
            errors.append("shape amendment byte identity mismatch")
        fence = shape.value.get("hir_h1_byte_fence_and_delegation", {})
        shape_hashes = {
            relative: row.get("sha256")
            for relative, row in fence.get("baseline_artifacts", {}).items()
        }
        if shape_hashes != HIR_H1_FENCE:
            errors.append("shape amendment HIR-H1 digest projection mismatch")
        if fence.get("existing_fixture_case_count") != 48:
            errors.append("shape amendment fixture count is not 48")
    return not errors, {
        "source_locators": list(HIR_H1_FENCE),
        "installed_canonical_fields_checked": [
            "exact file bytes",
            "tests/fixtures/current/hir-h1-current-mir-bridge-r1.json#cases",
        ],
        "expected_sha256": HIR_H1_FENCE,
        "observed_sha256": observed,
        "expected_case_count": 48,
        "observed_case_count": case_count,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_union_exact_2(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    union = _doc(environment, "union_schema")
    value = union.value
    errors = _errors(
        (
            union.sha256 == EXPECTED_FILE_SHA256["union_schema"],
            "union schema byte identity mismatch",
        ),
        (
            list(value) == ["$schema", "$id", "title", "oneOf"],
            "union schema root keys/order changed",
        ),
        (
            value.get("oneOf") == UNION_REFS,
            "union schema is not the exact ordered two refs",
        ),
    )
    return not errors, {
        "source_locators": [
            f"{union.locator}#oneOf",
        ],
        "installed_canonical_fields_checked": ["oneOf"],
        "expected_refs": UNION_REFS,
        "observed_refs": value.get("oneOf"),
        "bytes": union.byte_count,
        "sha256": union.sha256,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_overrides_exact_3(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    ownership = _doc(environment, "ownership_contract")
    binding = ownership.value["predicate_input_dispatch"][
        "canonical_union_schema_binding"
    ]
    overrides = binding.get("predicate_row_overrides")
    metadata = binding.get("catalog_metadata_binding")
    expected_row = {
        "input_descriptor": "OwnershipPredicateInputR1",
        "input_descriptor_schema": (
            "schemas/language/ownership-predicate-input-r1.schema.json"
        ),
    }
    errors = _errors(
        (
            ownership.sha256 == EXPECTED_FILE_SHA256["ownership_contract"],
            "ownership contract byte identity mismatch",
        ),
        (
            isinstance(overrides, dict)
            and list(overrides) == OVERRIDE_IDS
            and all(row == expected_row for row in overrides.values()),
            "predicate override set/shape is not exact three",
        ),
        (
            metadata.get("override_count") == 3,
            "catalog metadata override_count is not three",
        ),
        (
            binding.get("checker_predicate_row_schema_effect")
            == "BYTE_IDENTICAL",
            "checker predicate row schema byte fence changed",
        ),
    )
    return not errors, {
        "source_locators": [
            (
                f"{ownership.locator}#predicate_input_dispatch/"
                "canonical_union_schema_binding/predicate_row_overrides"
            ),
        ],
        "installed_canonical_fields_checked": [
            "predicate_row_overrides",
            "catalog_metadata_binding.override_count",
            "checker_predicate_row_schema_effect",
        ],
        "expected_override_ids": OVERRIDE_IDS,
        "observed_override_ids": (
            list(overrides) if isinstance(overrides, dict) else None
        ),
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _explicit_object_shape_violations(
    value: Any,
    path: tuple[str, ...] = (),
) -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        if value.get("type") == "object" and "additionalProperties" not in value:
            violations.append("/".join(path) or "<root>")
        for key, child in value.items():
            violations.extend(
                _explicit_object_shape_violations(child, path + (key,))
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(
                _explicit_object_shape_violations(
                    child, path + (str(index),)
                )
            )
    return violations


def _check_schema_closed(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    ownership = _doc(environment, "ownership_contract")
    input_schema = _doc(environment, "input_schema")
    union_schema = _doc(environment, "union_schema")
    fixture_schema = _doc(environment, "fixture_schema")
    row_schema = _doc(environment, "row_schema")
    fixture = _doc(environment, "canonical_fixture")
    schemas = [
        input_schema,
        union_schema,
        fixture_schema,
        row_schema,
    ]
    expected_digests = {
        "input_schema": EXPECTED_FILE_SHA256["input_schema"],
        "union_schema": EXPECTED_FILE_SHA256["union_schema"],
        "fixture_schema": EXPECTED_FILE_SHA256["fixture_schema"],
        "row_schema": EXPECTED_FILE_SHA256["row_schema"],
    }
    observed_digests = {
        "input_schema": input_schema.sha256,
        "union_schema": union_schema.sha256,
        "fixture_schema": fixture_schema.sha256,
        "row_schema": row_schema.sha256,
    }
    violations = {
        document.locator: _explicit_object_shape_violations(document.value)
        for document in schemas
        if _explicit_object_shape_violations(document.value)
    }
    input_value = input_schema.value
    input_defs = input_value["$defs"]
    operation_refs = input_defs["operation"]["oneOf"]
    operation_shapes_closed = all(
        input_defs[definition].get("type") == "object"
        and input_defs[definition].get("additionalProperties") is False
        and input_defs[definition]["properties"]["kind"].get("const") == name
        for definition, name in zip(OPERATION_DEFS, OPERATION_NAMES)
    )
    contract_registry = ownership.value["input"]["canonicalization"][
        "array_field_policy_registry"
    ]
    fixture_registry = fixture.value["canonicalization"][
        "array_field_policy_registry"
    ]
    schema_registry = input_defs["validatorOwnedLaws"]["properties"][
        "array_canonical_ordering_keys"
    ]["const"]
    canonical_fixture_fields = list(fixture.value)
    errors = _errors(
        (
            observed_digests == expected_digests,
            "one or more exact schema byte identities changed",
        ),
        (not violations, "an explicit object schema lacks additionalProperties"),
        (
            input_value.get("type") == "object"
            and input_value.get("additionalProperties") is False
            and input_value.get("required") == INPUT_FIELDS
            and list(input_value.get("properties", {})) == INPUT_FIELDS,
            "ownership input root is not the exact closed 11-field record",
        ),
        (
            operation_refs
            == [{"$ref": f"#/$defs/{name}"} for name in OPERATION_DEFS]
            and operation_shapes_closed,
            "operation union is not the exact 13 closed variants",
        ),
        (
            contract_registry.get("SET") == ARRAY_SET_FIELDS
            and contract_registry.get("SEQUENCE") == ARRAY_SEQUENCE_FIELDS
            and contract_registry.get("set_field_count") == 35
            and contract_registry.get("sequence_field_count") == 6
            and contract_registry.get("total_registered_array_field_count")
            == 41
            and contract_registry.get("generic_array_sort_count") == 0
            and contract_registry.get("unregistered_array_field_policy")
            == "REJECT",
            "ownership contract array policy registry changed",
        ),
        (
            fixture_registry.get("SET") == ARRAY_SET_FIELDS
            and fixture_registry.get("SEQUENCE") == ARRAY_SEQUENCE_FIELDS
            and fixture_registry.get("generic_array_sort_count") == 0
            and fixture_registry.get("unregistered_array_field_policy")
            == "REJECT",
            "fixture array policy registry changed",
        ),
        (
            list(schema_registry.get("SET", {})) == ARRAY_SET_FIELDS
            and list(schema_registry.get("SEQUENCE", {}))
            == ARRAY_SEQUENCE_FIELDS
            and schema_registry.get("generic_array_sort_count") == 0
            and schema_registry.get("unregistered_array_field_policy")
            == "REJECT",
            "schema validator-owned array registry changed",
        ),
        (
            fixture_schema.value.get("additionalProperties") is False
            and fixture_schema.value.get("required")
            == canonical_fixture_fields
            and list(fixture_schema.value.get("properties", {}))
            == canonical_fixture_fields
            and "acceptance_bindings"
            not in fixture_schema.value.get("properties", {}),
            "canonical fixture schema root is not exact closed projection",
        ),
        (
            row_schema.value.get("additionalProperties") is False
            and len(row_schema.value.get("allOf", [])) == 19,
            "conformance row schema is not closed with 19 conditions",
        ),
    )
    return not errors, {
        "source_locators": [
            ownership.locator
            + "#input/canonicalization/array_field_policy_registry",
            input_schema.locator,
            union_schema.locator,
            fixture_schema.locator,
            row_schema.locator,
            fixture.locator + "#canonicalization/array_field_policy_registry",
        ],
        "installed_canonical_fields_checked": [
            "root required/properties/additionalProperties",
            "$defs.operation.oneOf",
            "$defs.validatorOwnedLaws.array_canonical_ordering_keys",
            "fixture and row closed roots",
        ],
        "expected_sha256": expected_digests,
        "observed_sha256": observed_digests,
        "explicit_object_shape_violations": violations,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _all_steps(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = fixture.get("scenarios")
    if not isinstance(scenarios, dict):
        raise ValidationError("fixture scenarios is not an object")
    steps = [
        step
        for scenario in scenarios.values()
        for step in scenario["steps"]
    ]
    steps.extend(fixture["supplemental_operation_coverage"]["steps"])
    return steps


def _canonical_conformance_rows(
    authoring_fixture: dict[str, Any],
) -> list[dict[str, Any]]:
    scenarios = authoring_fixture["scenarios"]
    bindings = authoring_fixture["acceptance_bindings"]
    if set(scenarios) != set(bindings):
        raise ValidationError("scenario/acceptance binding identity mismatch")
    rows: list[dict[str, Any]] = []
    for test_id in sorted(scenarios):
        scenario = scenarios[test_id]
        binding = bindings[test_id]
        final_expected = scenario["steps"][-1]["expected"]
        if (
            binding["scenario_sha256"] != scenario["scenario_sha256"]
            or binding["step_count"] != len(scenario["steps"])
            or [row["input_sha256"] for row in binding["steps"]]
            != [step["input_sha256"] for step in scenario["steps"]]
        ):
            raise ValidationError(
                f"{test_id}: acceptance binding projection mismatch"
            )
        rows.append(
            {
                "test_id": test_id,
                "class": scenario["class"],
                "scenario_locator": f"#/scenarios/{test_id}",
                "scenario_sha256": scenario["scenario_sha256"],
                "step_count": len(scenario["steps"]),
                "step_input_sha256s": [
                    step["input_sha256"] for step in scenario["steps"]
                ],
                "final_evaluator_result": final_expected["result"],
                "semantic_oracle_key_or_null": final_expected[
                    "semantic_oracle_key_or_null"
                ],
                "primary_diagnostic_id_or_null": final_expected[
                    "primary_diagnostic_id_or_null"
                ],
                "legacy_semantic_side_channel_read_count": 0,
                "execution_status": "SPECIFIED_NOT_RUN",
                "product_support": PRODUCT_EXECUTION,
            }
        )
    return rows


def _fixture_count_observations(
    fixture: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    scenarios = fixture["scenarios"]
    scenario_steps = [
        step for scenario in scenarios.values() for step in scenario["steps"]
    ]
    supplemental = fixture["supplemental_operation_coverage"]["steps"]
    all_steps = scenario_steps + supplemental
    scenario_results = Counter(
        step["expected"]["result"] for step in scenario_steps
    )
    supplemental_results = Counter(
        step["expected"]["result"] for step in supplemental
    )
    all_results = Counter(step["expected"]["result"] for step in all_steps)
    observed = {
        "scenarios": len(scenarios),
        "fully_materialized_step_inputs": len(scenario_steps),
        "results": {
            result: scenario_results[result]
            for result in ("ADMIT", "REJECT", "INPUT_INVALID")
        },
        "scenario_classes": dict(
            sorted(Counter(row["class"] for row in scenarios.values()).items())
        ),
        "supplemental_operation_coverage_steps": len(supplemental),
        "supplemental_results": {
            result: supplemental_results[result]
            for result in ("ADMIT", "REJECT", "INPUT_INVALID")
        },
        "all_fully_materialized_step_inputs": len(all_steps),
        "all_results": {
            result: all_results[result]
            for result in ("ADMIT", "REJECT", "INPUT_INVALID")
        },
        "operation_counts_all_inputs": dict(
            sorted(
                Counter(
                    step["input"]["operation"]["kind"] for step in all_steps
                ).items()
            )
        ),
    }
    input_hash_failures = [
        step["step_id"]
        for step in all_steps
        if _canonical_digest(step["input"]) != step["input_sha256"]
    ]
    scenario_hash_failures = []
    for test_id, scenario in scenarios.items():
        payload = {
            key: value
            for key, value in scenario.items()
            if key != "scenario_sha256"
        }
        if _canonical_digest(payload) != scenario["scenario_sha256"]:
            scenario_hash_failures.append(test_id)
    supplemental_ids = [
        step["step_id"].split("/", 1)[0] for step in supplemental
    ]
    supplemental_shape_failures = [
        step["step_id"]
        for step in supplemental
        if step.get("coverage_only") is not True
        or step.get("acceptance_test_id_or_null") is not None
    ]
    errors = _errors(
        (observed == FIXTURE_COUNTS, "recomputed fixture counts changed"),
        (
            fixture.get("counts") == FIXTURE_COUNTS,
            "declared fixture counts changed",
        ),
        (not input_hash_failures, "one or more typed input hashes changed"),
        (not scenario_hash_failures, "one or more scenario hashes changed"),
        (
            supplemental_ids == SUPPLEMENTAL_IDS,
            "supplemental coverage IDs/order changed",
        ),
        (
            not supplemental_shape_failures,
            "supplemental coverage-only binding shape changed",
        ),
    )
    return (
        {
            "counts": observed,
            "input_hash_failures": input_hash_failures,
            "scenario_hash_failures": scenario_hash_failures,
            "supplemental_ids": supplemental_ids,
            "supplemental_shape_failures": supplemental_shape_failures,
        },
        errors,
    )


def _rows_from_fixture_without_bindings(
    fixture: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for test_id in sorted(fixture["scenarios"]):
        scenario = fixture["scenarios"][test_id]
        final_expected = scenario["steps"][-1]["expected"]
        rows.append(
            {
                "test_id": test_id,
                "class": scenario["class"],
                "scenario_locator": f"#/scenarios/{test_id}",
                "scenario_sha256": scenario["scenario_sha256"],
                "step_count": len(scenario["steps"]),
                "step_input_sha256s": [
                    step["input_sha256"] for step in scenario["steps"]
                ],
                "final_evaluator_result": final_expected["result"],
                "semantic_oracle_key_or_null": final_expected[
                    "semantic_oracle_key_or_null"
                ],
                "primary_diagnostic_id_or_null": final_expected[
                    "primary_diagnostic_id_or_null"
                ],
                "legacy_semantic_side_channel_read_count": 0,
                "execution_status": "SPECIFIED_NOT_RUN",
                "product_support": PRODUCT_EXECUTION,
            }
        )
    return rows


def _check_fixture_catalog(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    ownership = _doc(environment, "ownership_contract")
    fixture_document = _doc(environment, "canonical_fixture")
    rows_document = _doc(environment, "conformance_rows")
    fixture = fixture_document.value
    rows = rows_document.value
    if not isinstance(rows, list):
        raise ValidationError("conformance row projection is not an array")
    observations, errors = _fixture_count_observations(fixture)
    projected_rows = _rows_from_fixture_without_bindings(fixture)
    if projected_rows != rows:
        errors.append("canonical conformance rows do not project from fixture")
    if fixture_document.sha256 != EXPECTED_FILE_SHA256["canonical_fixture"]:
        errors.append("canonical fixture byte identity mismatch")
    if rows_document.sha256 != EXPECTED_FILE_SHA256["conformance_rows"]:
        errors.append("conformance row byte identity mismatch")
    if (
        _canonical_digest(fixture)
        != EXPECTED_CANONICAL_JSON_SHA256["canonical_fixture"]
    ):
        errors.append("canonical fixture object identity mismatch")
    if (
        _canonical_digest(rows)
        != EXPECTED_CANONICAL_JSON_SHA256["conformance_rows"]
    ):
        errors.append("conformance rows object identity mismatch")

    authoring = environment.documents["authoring_fixture"]
    if authoring is not None:
        if authoring.sha256 != EXPECTED_FILE_SHA256["authoring_fixture"]:
            errors.append("authoring fixture byte identity mismatch")
        if (
            _canonical_digest(authoring.value)
            != EXPECTED_CANONICAL_JSON_SHA256["authoring_fixture"]
        ):
            errors.append("authoring fixture object identity mismatch")
        authoring_projection = {
            key: value
            for key, value in authoring.value.items()
            if key != "acceptance_bindings"
        }
        if authoring_projection != fixture:
            errors.append(
                "canonical fixture is not authoring fixture minus bindings"
            )
        if _canonical_conformance_rows(authoring.value) != rows:
            errors.append("authoring bindings do not project canonical rows")

    envelope = ownership.value["canonical_conformance_catalog_envelope"]
    supplemental = ownership.value[
        "supplemental_operation_coverage_contract"
    ]
    if (
        envelope["reassembly_contract"].get("row_count") != 19
        or envelope["catalog_metadata"].get("scenario_count") != 19
        or envelope["catalog_metadata"].get("step_input_count") != 27
        or envelope["row_contract"].get("exact_partition_counts")
        != FIXTURE_COUNTS["scenario_classes"]
    ):
        errors.append("ownership catalog envelope counts changed")
    if (
        supplemental.get("exact_step_count") != 6
        or supplemental.get("exact_step_ids") != SUPPLEMENTAL_IDS
        or supplemental.get("all_fully_materialized_step_inputs") != 33
        or supplemental.get("all_results") != FIXTURE_COUNTS["all_results"]
    ):
        errors.append("ownership supplemental coverage contract changed")
    return not errors, {
        "source_locators": [
            fixture_document.locator,
            rows_document.locator,
            ownership.locator
            + "#canonical_conformance_catalog_envelope",
            (
                authoring.locator
                if authoring is not None
                else (
                    "authoring fixture not installed; canonical fixture and "
                    "rows validated directly"
                )
            ),
        ],
        "installed_canonical_fields_checked": [
            "canonical fixture exact bytes/object/counts/hashes",
            "19 ordered conformance rows",
            "contract catalog envelope",
        ],
        "observed": observations,
        "row_count": len(rows),
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _begin_profile_errors(value: dict[str, Any]) -> list[str]:
    operation = value["operation"]
    escape = value["escape_context"]
    errors: list[str] = []
    if operation["kind"] not in {
        "BeginSharedLoan",
        "BeginExclusiveLoan",
    }:
        return ["operation_not_begin_loan"]
    if escape["boundary"] not in {"Return", "Capture", "Suspension"}:
        errors.append("begin_loan_boundary_not_admitted_r5")
        return errors
    loans = {
        row["loan_id"]: row for row in value["loan_region_graph"]["loans"]
    }
    places = {
        row["place_id"]: row for row in value["place_graph"]["places"]
    }
    operation_loan = loans.get(operation["loan_id"])
    origin = escape["target_region_origin_or_null"]
    if origin != {"kind": "LoanRegion", "loan_id": operation["loan_id"]}:
        errors.append("begin_loan_target_origin_binding")
    expected_kind = (
        "Shared"
        if operation["kind"] == "BeginSharedLoan"
        else "Exclusive"
    )
    view = (
        places.get(operation_loan["view_place_id"])
        if operation_loan is not None
        else None
    )
    if (
        operation_loan is None
        or operation_loan["kind"] != expected_kind
        or operation["owner_place_id"] != operation_loan["owner_place_id"]
        or operation["view_place_id"] != operation_loan["view_place_id"]
        or operation["region_id"] != operation_loan["region_id"]
        or operation["at_point_id"] != operation_loan["start_point_id"]
        or view is None
        or view["storage_region_id"] != operation_loan["region_id"]
    ):
        errors.append("begin_loan_target_operation_loan_binding")
    if (
        operation_loan is None
        or escape["target_region_id_or_null"] != operation_loan["region_id"]
    ):
        errors.append("begin_loan_target_region_binding")
    return errors


def _profile_b_receipt(fixture: dict[str, Any]) -> dict[str, Any]:
    templates: dict[str, dict[str, Any]] = {}
    for operation_kind in ("BeginSharedLoan", "BeginExclusiveLoan"):
        candidates = [
            step["input"]
            for step in _all_steps(fixture)
            if step["input"]["operation"]["kind"] == operation_kind
            and step["input"]["escape_context"]["boundary"] == "None"
            and len(step["input"]["loan_region_graph"]["loans"]) >= 2
        ]
        if candidates:
            templates[operation_kind] = candidates[0]

    valid_rows: list[dict[str, Any]] = []
    forgery_rows: list[dict[str, Any]] = []
    unlisted_rows: list[dict[str, Any]] = []
    for operation_kind in ("BeginSharedLoan", "BeginExclusiveLoan"):
        base = templates.get(operation_kind)
        if base is None:
            continue
        operation = base["operation"]
        loans = {
            row["loan_id"]: row
            for row in base["loan_region_graph"]["loans"]
        }
        operation_loan = loans[operation["loan_id"]]
        alternate_loans = [
            row
            for loan_id, row in loans.items()
            if loan_id != operation["loan_id"]
        ]
        forged_targets = [
            row["region_id"]
            for row in base["loan_region_graph"]["regions"]
            if row["region_id"] != operation_loan["region_id"]
        ]
        for boundary in ("Return", "Capture", "Suspension"):
            valid = copy.deepcopy(base)
            valid["escape_context"]["boundary"] = boundary
            valid["escape_context"]["target_region_origin_or_null"] = {
                "kind": "LoanRegion",
                "loan_id": operation["loan_id"],
            }
            valid["escape_context"]["target_region_id_or_null"] = (
                operation_loan["region_id"]
            )
            valid_rows.append(
                {
                    "operation": operation_kind,
                    "boundary": boundary,
                    "errors": _begin_profile_errors(valid),
                }
            )

            region_ancestor = copy.deepcopy(valid)
            region_ancestor["escape_context"][
                "target_region_origin_or_null"
            ] = {
                "kind": "RegionAncestor",
                "source_region_id": valid["escape_context"][
                    "source_region_id_or_null"
                ],
                "required_ancestor_kind": "Invocation",
            }
            forgery_rows.append(
                {
                    "operation": operation_kind,
                    "boundary": boundary,
                    "forgery": "REGION_ANCESTOR_SUBSTITUTION",
                    "errors": _begin_profile_errors(region_ancestor),
                }
            )

            alternate = copy.deepcopy(valid)
            alternate_available = bool(alternate_loans)
            if alternate_available:
                alternate_loan = alternate_loans[0]
                alternate["escape_context"][
                    "target_region_origin_or_null"
                ] = {
                    "kind": "LoanRegion",
                    "loan_id": alternate_loan["loan_id"],
                }
                alternate["escape_context"]["target_region_id_or_null"] = (
                    alternate_loan["region_id"]
                )
            forgery_rows.append(
                {
                    "operation": operation_kind,
                    "boundary": boundary,
                    "forgery": "COHERENT_ALTERNATE_DECLARED_LOAN_TARGET",
                    "alternate_available": alternate_available,
                    "errors": _begin_profile_errors(alternate),
                }
            )

            forged_target = copy.deepcopy(valid)
            target_available = bool(forged_targets)
            if target_available:
                forged_target["escape_context"][
                    "target_region_id_or_null"
                ] = forged_targets[0]
            forgery_rows.append(
                {
                    "operation": operation_kind,
                    "boundary": boundary,
                    "forgery": "CORRECT_ORIGIN_FORGED_TARGET",
                    "alternate_available": target_available,
                    "errors": _begin_profile_errors(forged_target),
                }
            )

        for boundary in ("Store", "TaskEscape", "ActorTransfer", "Ffi"):
            unlisted = copy.deepcopy(base)
            unlisted["escape_context"]["boundary"] = boundary
            unlisted["escape_context"]["target_region_origin_or_null"] = {
                "kind": "LoanRegion",
                "loan_id": operation["loan_id"],
            }
            unlisted["escape_context"]["target_region_id_or_null"] = (
                operation_loan["region_id"]
            )
            unlisted_rows.append(
                {
                    "operation": operation_kind,
                    "boundary": boundary,
                    "expected": "INPUT_INVALID",
                    "errors": _begin_profile_errors(unlisted),
                }
            )

    valid_pass = len(valid_rows) == 6 and all(
        not row["errors"] for row in valid_rows
    )
    forgery_pass = len(forgery_rows) == 18 and all(
        row["errors"] and row.get("alternate_available", True)
        for row in forgery_rows
    )
    unlisted_pass = len(unlisted_rows) == 8 and all(
        "begin_loan_boundary_not_admitted_r5" in row["errors"]
        for row in unlisted_rows
    )
    result = "PASS" if valid_pass and forgery_pass and unlisted_pass else "FAIL"
    return {
        "schema": "deeplus.r5-ownership-profile-b-static-probes/v1",
        "result": result,
        "static_validation_execution": (
            "EXECUTED_PASS" if result == "PASS" else "EXECUTED_FAIL"
        ),
        "valid": {
            "expected": 6,
            "observed": len(valid_rows),
            "accepted": sum(not row["errors"] for row in valid_rows),
        },
        "forgeries": {
            "expected": 18,
            "observed": len(forgery_rows),
            "rejected": sum(bool(row["errors"]) for row in forgery_rows),
        },
        "unlisted": {
            "expected": 8,
            "observed": len(unlisted_rows),
            "input_invalid": sum(
                "begin_loan_boundary_not_admitted_r5" in row["errors"]
                for row in unlisted_rows
            ),
        },
        "production_evaluator_execution": PRODUCT_EXECUTION,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_profile_b(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    fixture = _doc(environment, "canonical_fixture")
    ownership = _doc(environment, "ownership_contract")
    receipt = _profile_b_receipt(fixture.value)
    matrix = ownership.value["escape_target_origin_compatibility_matrix"]
    errors = _errors(
        (receipt["result"] == "PASS", "Profile-B derived probes failed"),
        (
            matrix.get("admitted_actual_profile_count") == 4
            and matrix.get("admitted_origin_kind_count") == 3
            and matrix.get("unlisted_combination") == "INPUT_INVALID",
            "contract escape target-origin matrix changed",
        ),
    )
    return not errors, {
        "source_locators": [
            fixture.locator + "#scenarios",
            fixture.locator + "#supplemental_operation_coverage/steps",
            ownership.locator + "#escape_target_origin_compatibility_matrix",
        ],
        "installed_canonical_fields_checked": [
            "BeginSharedLoan/BeginExclusiveLoan typed inputs",
            "escape target origin/region binding",
        ],
        "profile_b_receipt": receipt,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_reason_routes(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    escape, authority = _escape_projection(environment)
    document = environment.documents["escape_contract"]
    errors = _errors(
        (
            document is None
            or document.sha256 == EXPECTED_FILE_SHA256["escape_contract"],
            "escape contract byte identity mismatch",
        ),
        (
            escape.get("diagnostic_dispatch") == REASON_ROUTES,
            "reason-key dispatch is not exact four routes",
        ),
        (
            escape.get("single_mutant_axes") == REASON_AXES,
            "reason-key single-mutant axes changed",
        ),
        (
            escape.get("public_diagnostic", {}).get("diagnostic_id")
            == BORROW_DIAGNOSTIC_ID,
            "public diagnostic identity changed",
        ),
    )
    return not errors, {
        "source_locators": [authority["source_locator"]],
        "installed_canonical_path_or_null": None,
        "acceptance_oracle_label": NONCANONICAL_ORACLE,
        "canonical_implementation_validation": False,
        "expected_routes": REASON_ROUTES,
        "observed_routes": escape.get("diagnostic_dispatch"),
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _binding_projection(environment: Environment) -> dict[str, Any]:
    escape, authority = _escape_projection(environment)
    predicate = _find_unique(
        environment.predicate_rows,
        "predicate_id",
        "BorrowEscapeAdmitted",
        "predicate catalog",
    )
    catalog_matches = [
        row
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id") == BORROW_DIAGNOSTIC_ID
    ]
    relation_matches = [
        row
        for row in environment.relation_rows
        if row.get("predicate_id") == "BorrowEscapeAdmitted"
        and row.get("diagnostic_id") == BORROW_DIAGNOSTIC_ID
        and row.get("relation") == "primary"
    ]
    return {
        "reason_routes": copy.deepcopy(escape["diagnostic_dispatch"]),
        "diagnostic_refs": copy.deepcopy(predicate.get("diagnostic_refs", [])),
        "catalog_ids": [
            row["diagnostic_id"] for row in catalog_matches
        ],
        "primary_relations": [
            {
                "violation_id": row.get("violation_id"),
                "predicate_id": row.get("predicate_id"),
                "diagnostic_id": row.get("diagnostic_id"),
                "relation": row.get("relation"),
            }
            for row in relation_matches
        ],
        "reason_authority": authority,
    }


def _binding_errors(projection: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if projection.get("reason_routes") != REASON_ROUTES:
        errors.append("REASON_ROUTE_SET_OR_TARGET_MISMATCH")
    if projection.get("diagnostic_refs") != [BORROW_DIAGNOSTIC_ID]:
        errors.append("PREDICATE_DIAGNOSTIC_REF_MISSING_OR_NONEXACT")
    if projection.get("catalog_ids") != [BORROW_DIAGNOSTIC_ID]:
        errors.append("DIAGNOSTIC_CATALOG_ID_MISSING_OR_NONEXACT")
    if projection.get("primary_relations") != [BORROW_RELATION]:
        errors.append("PRIMARY_RELATION_MISSING_OR_NONEXACT")
    return errors


def _check_primary_route(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    projection = _binding_projection(environment)
    errors = _binding_errors(projection)
    route_errors = [
        error
        for error in errors
        if error
        in {
            "PREDICATE_DIAGNOSTIC_REF_MISSING_OR_NONEXACT",
            "DIAGNOSTIC_CATALOG_ID_MISSING_OR_NONEXACT",
            "PRIMARY_RELATION_MISSING_OR_NONEXACT",
        }
    ]
    return not route_errors, {
        "source_locators": [
            (
                "spec/types/predicates/chunks/*.json"
                "#BorrowEscapeAdmitted.diagnostic_refs"
            ),
            (
                "spec/diagnostics/catalog/chunks/*.json"
                "#BORROW_ESCAPE_OWNER_REGION"
            ),
            (
                "spec/diagnostics/relations/chunks/*.json"
                "#BorrowEscapeAdmitted:default"
            ),
        ],
        "installed_canonical_fields_checked": [
            "predicate diagnostic_refs",
            "active diagnostic catalog identity",
            "one primary relation",
        ],
        "observed": {
            "diagnostic_refs": projection["diagnostic_refs"],
            "catalog_ids": projection["catalog_ids"],
            "primary_relations": projection["primary_relations"],
        },
        "errors": route_errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _mutation_receipt(environment: Environment) -> dict[str, Any]:
    baseline = _binding_projection(environment)
    baseline_errors = _binding_errors(baseline)
    mutations: list[dict[str, Any]] = []
    for index, reason_key in enumerate(REASON_ROUTES, start=1):
        mutant = copy.deepcopy(baseline)
        mutant["reason_routes"][reason_key] = (
            f"R5_MUTATION_ABSENT_DIAGNOSTIC_{index}"
        )
        rejection = _binding_errors(mutant)
        mutations.append(
            {
                "mutation_id": (
                    f"R5_OWN_MUT_{index:02d}_"
                    f"{reason_key.upper()}_ABSENT_TARGET"
                ),
                "axis": f"diagnostic_dispatch.{reason_key}",
                "result": "REJECTED" if rejection else "SURVIVED",
                "rejection_reasons": rejection,
            }
        )
    for index, (mutation_id, axis) in enumerate(
        (
            (
                "R5_OWN_MUT_05_REMOVE_PREDICATE_DIAGNOSTIC_REF",
                "predicate.diagnostic_refs",
            ),
            (
                "R5_OWN_MUT_06_REMOVE_DIAGNOSTIC_CATALOG_ID",
                "diagnostic_catalog",
            ),
            (
                "R5_OWN_MUT_07_REMOVE_PRIMARY_RELATION",
                "diagnostic_relations",
            ),
        ),
        start=5,
    ):
        mutant = copy.deepcopy(baseline)
        if index == 5:
            mutant["diagnostic_refs"] = []
        elif index == 6:
            mutant["catalog_ids"] = []
        else:
            mutant["primary_relations"] = []
        rejection = _binding_errors(mutant)
        mutations.append(
            {
                "mutation_id": mutation_id,
                "axis": axis,
                "result": "REJECTED" if rejection else "SURVIVED",
                "rejection_reasons": rejection,
            }
        )
    rejected = sum(row["result"] == "REJECTED" for row in mutations)
    result = (
        "PASS"
        if not baseline_errors and len(mutations) == 7 and rejected == 7
        else "FAIL"
    )
    return {
        "schema": MUTATION_SCHEMA,
        "result": result,
        "static_validation_execution": (
            "EXECUTED_PASS" if result == "PASS" else "EXECUTED_FAIL"
        ),
        "baseline_errors": baseline_errors,
        "expected_mutation_count": 7,
        "observed_mutation_count": len(mutations),
        "rejected_mutation_count": rejected,
        "mutations": mutations,
        "reason_route_authority": baseline["reason_authority"],
        "canonical_implementation_validation": False,
        "production_evaluator_execution": PRODUCT_EXECUTION,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_binding_mutations(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    receipt = _mutation_receipt(environment)
    errors = _errors(
        (
            receipt["result"] == "PASS",
            "one or more exact binding mutations survived",
        ),
    )
    return not errors, {
        "source_locators": [
            (
                "spec/types/predicates/chunks/*.json"
                "#BorrowEscapeAdmitted.diagnostic_refs"
            ),
            (
                "spec/diagnostics/catalog/chunks/*.json"
                "#BORROW_ESCAPE_OWNER_REGION"
            ),
            (
                "spec/diagnostics/relations/chunks/*.json"
                "#BorrowEscapeAdmitted:default"
            ),
            receipt["reason_route_authority"]["source_locator"],
        ],
        "installed_canonical_fields_checked": [
            "diagnostic_refs binding",
            "catalog identity binding",
            "primary relation binding",
        ],
        "acceptance_oracle_label": NONCANONICAL_ORACLE,
        "mutation_receipt": receipt,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_residual_debt(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    escape, authority = _escape_projection(environment)
    predicate_by_id = {
        row["predicate_id"]: row for row in environment.predicate_rows
    }
    diagnostic_ids = {
        row["diagnostic_id"] for row in environment.diagnostic_rows
    }
    actual_rows: list[dict[str, Any]] = []
    row_failures: list[str] = []
    for expected in RESIDUAL_DEBT_ROWS:
        predicate = predicate_by_id.get(expected["predicate_id"])
        if predicate is None:
            row_failures.append(
                f"{expected['predicate_id']}: predicate missing"
            )
            continue
        target = predicate.get("diagnostic_dispatch", {}).get(
            expected["branch"]
        )
        route_count = sum(
            row.get("predicate_id") == expected["predicate_id"]
            and row.get("diagnostic_id") == expected["target"]
            for row in environment.relation_rows
        )
        actual = {
            "predicate_id": expected["predicate_id"],
            "branch": expected["branch"],
            "target": target,
            "target_absent_from_predicate_refs": (
                target not in predicate.get("diagnostic_refs", [])
            ),
            "target_absent_from_catalog": target not in diagnostic_ids,
            "target_relation_count": route_count,
        }
        actual_rows.append(actual)
        if (
            target != expected["target"]
            or not actual["target_absent_from_predicate_refs"]
            or not actual["target_absent_from_catalog"]
            or route_count != 0
        ):
            row_failures.append(
                f"{expected['predicate_id']}:{expected['branch']}: drift"
            )
    debt = escape.get("global_dispatch_debt", {})
    errors = _errors(
        (
            debt.get("r5_borrow_escape_unresolved_after_candidate") == 0,
            "R5 BorrowEscape residual is not zero",
        ),
        (
            debt.get("outside_r5_gap_id") == "IR-DIAG-P0-052",
            "residual debt gap identity changed",
        ),
        (
            debt.get("outside_r5_total") == 12
            and debt.get("outside_r5_exact_debt_rows")
            == RESIDUAL_DEBT_ROWS,
            "escape contract residual debt is not exact 12",
        ),
        (
            len(actual_rows) == 12 and not row_failures,
            "installed canonical residual debt rows changed",
        ),
    )
    return not errors, {
        "source_locators": [
            (
                "spec/types/predicates/chunks/*.json"
                "#diagnostic_dispatch"
            ),
            "spec/diagnostics/catalog/chunks/*.json#diagnostic_id",
            (
                "spec/diagnostics/relations/chunks/*.json"
                "#predicate_id+diagnostic_id"
            ),
            authority["source_locator"],
        ],
        "installed_canonical_fields_checked": [
            "three predicates x four dispatch branches",
            "target absence from refs/catalog/relations",
        ],
        "acceptance_oracle_label": NONCANONICAL_ORACLE,
        "expected_rows": RESIDUAL_DEBT_ROWS,
        "observed_rows": actual_rows,
        "row_failures": row_failures,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_governance(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    pointer = _doc(environment, "current_pointer")
    open_actions = pointer.value.get("open_actions")
    product_lanes = pointer.value.get("product_lanes")
    if not isinstance(open_actions, list) or not isinstance(
        product_lanes, dict
    ):
        raise ValidationError("current pointer governance shapes are invalid")
    actions_by_id = {row["id"]: row for row in open_actions}
    observed_feature_p1 = {
        action_id
        for action_id, row in actions_by_id.items()
        if action_id in FEATURE_P1_IDS and row.get("priority") == "P1"
    }
    observed_m13 = {action_id for action_id in actions_by_id if action_id in M13_IDS}
    semantic_p0 = [
        row["id"] for row in open_actions if row.get("priority") == "P0"
    ]
    r6 = environment.documents["r6_receipt"]
    r6_errors: list[str] = []
    if r6 is not None:
        if (
            r6.value.get("semantic_delta") != 0
            or r6.value.get("feature_p1")
            != {"count": 22, "status": "OPEN"}
            or r6.value.get("m13_actions")
            != {"count": 4, "status": "OPEN"}
            or r6.value.get("product_lanes")
            != {"count": 15, "status": PRODUCT_EXECUTION}
            or r6.value.get("production_implementation")
            != "NOT_PERFORMED"
        ):
            r6_errors.append("R6 governance receipt changed")
    errors = _errors(
        (semantic_p0 == [], "semantic P0 open-action count is nonzero"),
        (
            observed_feature_p1 == FEATURE_P1_IDS
            and len(observed_feature_p1) == 22,
            "feature P1 OPEN set is not exact 22",
        ),
        (
            observed_m13 == M13_IDS and len(observed_m13) == 4,
            "M13 OPEN action set is not exact four",
        ),
        (
            len(product_lanes) == 15
            and set(product_lanes.values()) == {PRODUCT_EXECUTION},
            "product lanes are not exact 15 NOT_RUN",
        ),
        (not r6_errors, "R6 candidate governance projection changed"),
    )
    return not errors, {
        "source_locators": [
            "current/current-pointer.json#open_actions",
            "current/current-pointer.json#product_lanes",
            (
                r6.locator
                if r6 is not None
                else "R6 candidate receipt not installed"
            ),
        ],
        "installed_canonical_fields_checked": [
            "open_actions priority/id",
            "product_lanes values",
        ],
        "observed": {
            "semantic_p0": len(semantic_p0),
            "feature_p1_open": len(observed_feature_p1),
            "m13_open": len(observed_m13),
            "product_lanes_not_run": sum(
                value == PRODUCT_EXECUTION
                for value in product_lanes.values()
            ),
        },
        "r6_errors": r6_errors,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }



# ---------------------------------------------------------------------------
# R8 canonical-installed semantic binding amendment.
# Frozen candidate values remain comparison constants only.  Canonical mode
# fails closed unless every IR-OWN-P0-012..014 authority input is installed.
# ---------------------------------------------------------------------------

R8_CONTEXT_CONTRACT = "spec/contracts/borrow-context-anchor-disambiguation.json"
R8_CONTEXT_SCHEMA = (
    "schemas/language/"
    "borrow-context-anchor-disambiguation-fixtures.schema.json"
)
R8_CONTEXT_FIXTURE = (
    "tests/fixtures/current/borrow-context-anchor-disambiguation-r1.json"
)
R8_ESCAPE_SCHEMA = (
    "schemas/language/"
    "borrow-escape-diagnostic-dispatch-fixtures.schema.json"
)
R8_ESCAPE_FIXTURE = (
    "tests/fixtures/current/borrow-escape-diagnostic-dispatch-r1.json"
)
R8_PREDICATE_METADATA = "spec/types/predicates/catalog-metadata.json"
R8_OWNERSHIP_METADATA = (
    "tests/conformance/ownership-decisions/catalog-metadata.json"
)
R8_REASSEMBLY = "migration/catalog-reassembly.json"
R8_GRAMMAR_SHA256 = (
    "055ed7010ad8b78345d0414ffe696988abb52d13fa6f86e3dd1dae4610a4c962"
)
R41_GRAMMAR_SHA256 = (
    "a95ce1649e872fa0803300bff4e720e1c1d6a5afa54fa546de584501c8da2276"
)
R41_HIR_H1_BRIDGE_SHA256 = (
    "6823b757662b3b6144a7f360d5e792e2f20647feb1753a3dfe057338b54464f6"
)
R8_CHECKER_ROW_SCHEMA_SHA256 = (
    "d990505e697c8f600f930eddc4bd4c0ac8a7f99474209e5636488f01165c47a8"
)
R8_014_BYTE_FENCE = {
    "schemas/language/checker-predicate-fixture-row.schema.json": (
        6010,
        "13fd8cd1ae06b06d2d490258368244ef13871b1f8c66f1aec7e65e4dd184df8b",
    ),
    "schemas/language/rcts-v5-descriptor.schema.json": (
        23266,
        "d396b44a739da5c71dc3e52ef472e447852759d1353324481bfc822b670c7c75",
    ),
    "spec/diagnostics/catalog/chunks/part-0002.json": (
        60219,
        "c3142bd09a936a0d1f65015e6632789043a2ed30a38b2767d85cadb7a89907b9",
    ),
    "spec/diagnostics/relations/chunks/part-0001.json": (
        61344,
        "3e82a0dcc3cce9b447cd0caa31bb7655c6086bb647ed82c9c6157e0f49411d1a",
    ),
    "tests/conformance/checker-predicates/chunks/part-0003.json": (
        58715,
        "062a32da9dad1f5c6481a83963ad1b1f0b713636b7ed11b283b4312973fa399e",
    ),
}
R41_014_RELATION_PART_0001_FENCE = (
    61154,
    "b017b716e38901919505985a2e293d6ed385cbcf63cef50965bf387dc2d96790",
)
R8_014_EXACT_MUTATION_PROBES = [
    {
        "mutation_id": (
            "R5_OWN_MUT_01_1_RETURN_OUTLIVES_OWNER_REGION_ABSENT_TARGET"
        ),
        "axis": (
            "diagnostic_dispatch.1_return_outlives_owner_region"
        ),
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
    {
        "mutation_id": (
            "R5_OWN_MUT_02_2_STORE_OUTLIVES_OWNER_REGION_ABSENT_TARGET"
        ),
        "axis": (
            "diagnostic_dispatch.2_store_outlives_owner_region"
        ),
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
    {
        "mutation_id": (
            "R5_OWN_MUT_03_3_CAPTURE_OR_SUSPENSION_OUTLIVES_OWNER_REGION_"
            "ABSENT_TARGET"
        ),
        "axis": (
            "diagnostic_dispatch."
            "3_capture_or_suspension_outlives_owner_region"
        ),
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
    {
        "mutation_id": (
            "R5_OWN_MUT_04_4_ISOLATION_BOUNDARY_WITHOUT_ADMITTED_PROOF_"
            "ABSENT_TARGET"
        ),
        "axis": (
            "diagnostic_dispatch."
            "4_isolation_boundary_without_admitted_proof"
        ),
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
    {
        "mutation_id": "R5_OWN_MUT_05_REMOVE_PREDICATE_DIAGNOSTIC_REF",
        "axis": "predicate.diagnostic_refs",
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
    {
        "mutation_id": "R5_OWN_MUT_06_REMOVE_DIAGNOSTIC_CATALOG_ID",
        "axis": "diagnostic_catalog",
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
    {
        "mutation_id": "R5_OWN_MUT_07_REMOVE_PRIMARY_RELATION",
        "axis": "diagnostic_relations",
        "expected_validator_result": "REJECTED",
        "expected_internal_reason": (
            "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
        ),
        "execution_status": "SPECIFIED_NOT_RUN",
    },
]
# The R6 authority shard is an exact input/preimage fence.  Canonical catalog
# reassembly normalizes its CRLF bytes to LF while preserving all 19 rows and
# their canonical JSON-object digest.
EXPECTED_FILE_SHA256["conformance_rows"] = (
    "204fc8e47d952b9d5e2ca625213c526c07ff60bbf485ec98eb158b74804d8278"
)
R8_CONTEXT_CANONICAL_FENCE = {
    R8_CONTEXT_CONTRACT: (
        8444,
        "84919d36fc1843bce749d1341d8364936d42ccc551d7a7c9046291f356326a2c",
    ),
    R8_CONTEXT_SCHEMA: (
        5202,
        "cf6d3e366387436762ca78b5d877751dc8979e5289ad39817c6e2659d0d25232",
    ),
    R8_CONTEXT_FIXTURE: (
        6969,
        "e00b92a7af2676f87d091d580ce5facd6f7a117bcb9d2194cdb6b07d5af2ab82",
    ),
}
R8_ESCAPE_CANONICAL_FENCE = {
    R8_ESCAPE_SCHEMA: (
        6576,
        "9c1ccd5472547a0dfc282c3670430bdfa8143658c29c91b1136bdf2a76e5adc9",
    ),
    R8_ESCAPE_FIXTURE: (
        5017,
        "a23b6670816b7ed7bcaa1f475ebd71eba3621e93140a20e9ce6ca297c2d7b41b",
    ),
}
R8_PREDICATE_PROCEDURES = {
    "ContextAnchorOperandAdmitted": [
        "validate the closed RCTS-V5 input variant",
        "select exactly one of NUMERIC_ARRAY_CONTEXT_PROVIDER or "
        "MEASURE_UNIT_CONTEXT_PROVIDER from the nearest admitted operation",
        "cross only transparent ParenExpr while searching for that owner",
        "stop at call-argument, index, closure, or control-expression boundaries",
        "require one anchor per operation and no standalone value",
        "when the selected role is MEASURE_UNIT_CONTEXT_PROVIDER require one "
        "statically known witness_id after the multiple-anchor check; "
        "otherwise reject UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
        "create no LoanId, borrow event, effect, error, cleanup, authority, "
        "new witness, runtime role lookup, or unresolved role",
        "evaluate the provider and adapted operands once in source order",
        "return admit or the first diagnostic in the canonical priority",
    ],
    "NumericArrayContextAnchorAdmitted": [
        "validate the closed RCTS-V5 input descriptor",
        "evaluate ContextAnchorOperandAdmitted and propagate its selected "
        "diagnostic before the NumericArray-local rule",
        "bind the nearest eligible operation as the sole "
        "NUMERIC_ARRAY_CONTEXT_PROVIDER owner",
        "reject broadcast-marker polarity before context-provider polarity",
        "evaluate provider and adapted operands once in source order",
        "create one HirContextAdaptationPlan and zero LoanId, borrow event, "
        "runtime role lookup, or unresolved provider",
        "return admit or the first exact diagnostic in canonical order",
    ],
    "BorrowEscapeAdmitted": [
        "validate the schema-discriminated OwnershipPredicateInputR1",
        "dispatch by top-level schema identity to the unchanged "
        "RCTSDescriptorV5 branch or to OwnershipDecisionInputR1; the typed "
        "branch requires predicate_id BorrowEscapeAdmitted and reads zero "
        "fixture, legacy side-channel, or fabricated adapter fields",
        "normalize aliases, ownership regions, and identity references",
        "evaluate declared dependency predicates left-to-right and propagate "
        "their selected diagnostic",
        "classify failed escape uses into the exact four predicate-local "
        "reason keys",
        "select the lexicographic minimum of canonical CFG operation order and "
        "numeric reason rank",
        "map each exact reason key to BORROW_ESCAPE_OWNER_REGION",
        "emit exactly one primary diagnostic and mark later branch or use "
        "candidates NOT_EVALUATED",
    ],
    "BoxOwnershipAdmitted": [
        "validate the schema-discriminated OwnershipPredicateInputR1",
        "dispatch by top-level schema identity to the unchanged "
        "RCTSDescriptorV5 branch or to OwnershipDecisionInputR1; the typed "
        "branch requires predicate_id BoxOwnershipAdmitted and reads zero "
        "fixture, legacy side-channel, or fabricated adapter fields",
        "evaluate declared dependency predicates left-to-right in listed order",
        "construct one unique owner under explicit allocation and failure "
        "responsibility",
        "require move to invalidate the source and reject every later source use",
        "require one payload cleanup on every completed owned lifecycle and keep "
        "every borrow nonescaping while the owner is alive",
        "emit only the active primary diagnostic on local-rule failure",
    ],
    "OwnershipModeAdmitted": [
        "validate the schema-discriminated OwnershipPredicateInputR1",
        "dispatch by top-level schema identity to the unchanged "
        "RCTSDescriptorV5 branch or to OwnershipDecisionInputR1; the typed "
        "branch requires predicate_id OwnershipModeAdmitted and reads zero "
        "fixture, legacy side-channel, or fabricated adapter fields",
        "evaluate declared dependency predicates left-to-right in listed order",
        "evaluate ordinary mut, borrow, inout, move, cleanup, suspension, "
        "isolation, and join rules from the selected branch only",
        "select the first exact diagnostic-reason rank and emit exactly one "
        "primary diagnostic; secondary diagnostics are trace alternatives",
    ],
}
R8_MEASURE_SEED_PROCEDURES = {
    "HasKnownUnitWitness": [
        "validate the declared descriptor shape as design documentation only",
        "record HasKnownUnitWitness requires and candidate diagnostic "
        "vocabulary without executing a checker decision",
        "emit no diagnostic and create no product execution receipt while "
        "predicate_maturity is design_seed",
        "promote only after a closed terminating algorithm plus "
        "discriminating positive/negative fixtures is independently reviewed",
    ],
    "MeasureUnitWitnessAdmitted": [
        "validate the declared descriptor shape as design documentation only",
        "record MeasureUnitWitnessAdmitted requires and candidate diagnostic "
        "vocabulary without executing a checker decision",
        "emit no diagnostic and create no product execution receipt while "
        "predicate_maturity is design_seed",
        "promote only after a closed terminating algorithm plus "
        "discriminating positive/negative fixtures is independently reviewed",
    ],
}
R8_OWNERSHIP_MODE_REASON_RANK = [
    {
        "rank": 1,
        "match_kind": "EXACT",
        "semantic_oracle_key": "PLACE_STATE_JOIN_MISMATCH",
        "primary_diagnostic_id": "PLACE_STATE_JOIN_MISMATCH",
    },
    {
        "rank": 2,
        "match_kind": "EXACT",
        "semantic_oracle_key": "USE_AFTER_MOVE",
        "primary_diagnostic_id": "OWNERSHIP_MODE_ADMISSION_FAILED",
    },
    {
        "rank": 3,
        "match_kind": "EXACT",
        "semantic_oracle_key": "INOUT_ALIAS_CONFLICT",
        "primary_diagnostic_id": "INOUT_ALIAS_CONFLICT",
    },
    {
        "rank": 4,
        "match_kind": "EXACT",
        "semantic_oracle_key": "BORROW_CONFLICT_MUTATION",
        "primary_diagnostic_id": "OWNERSHIP_MODE_ADMISSION_FAILED",
    },
    {
        "rank": 5,
        "match_kind": "CATCH_ALL",
        "semantic_oracle_key": "*",
        "primary_diagnostic_id": "OWNERSHIP_MODE_ADMISSION_FAILED",
    },
]


def _r8_installed(
    environment: Environment,
    relative: str,
) -> JsonDocument:
    if environment.projection_root is not None:
        raise ValidationError(
            "R8 canonical-installed checks reject --projection-root"
        )
    return _read_json(environment.root / relative, relative)


def _r8_authority(document: JsonDocument) -> dict[str, Any]:
    return {
        "authority": "INSTALLED_CANONICAL_CURRENT",
        "canonical_implementation_validation": True,
        "source_locator": document.locator,
        "bytes": document.byte_count,
        "sha256": document.sha256,
    }


def _r8_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _r8_schema_errors(
    schema: dict[str, Any],
    value: Any,
    path: str = "$",
) -> list[str]:
    """Validate the closed JSON-Schema subset used by the two R8 fixtures."""
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: const mismatch")
        return errors
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: enum mismatch")
    expected_type = schema.get("type")
    if expected_type is not None:
        domains = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        if not any(_r8_type_matches(value, domain) for domain in domains):
            errors.append(f"{path}: type mismatch")
            return errors
    if isinstance(value, str) and "minLength" in schema:
        if len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                errors.append(
                    f"{path}: additional properties {','.join(extra)}"
                )
        for key, child in properties.items():
            if key in value and isinstance(child, dict):
                errors.extend(
                    _r8_schema_errors(child, value[key], f"{path}.{key}")
                )
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems") is True:
            canonical = [
                json.dumps(item, ensure_ascii=False, sort_keys=True)
                for item in value
            ]
            if len(canonical) != len(set(canonical)):
                errors.append(f"{path}: duplicate array items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(
                    _r8_schema_errors(
                        item_schema, item, f"{path}[{index}]"
                    )
                )
    return errors


def _r8_byte_fence_errors(
    root: Path,
    fence: dict[str, tuple[int, str]],
) -> list[str]:
    errors: list[str] = []
    for relative, (expected_bytes, expected_sha256) in fence.items():
        path = root / relative
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_size != expected_bytes
            or _sha256(path.read_bytes()) != expected_sha256
        ):
            errors.append(relative)
    return errors


def _borrow_projection(
    environment: Environment,
) -> tuple[dict[str, Any], dict[str, Any]]:
    document = _r8_installed(environment, R8_CONTEXT_CONTRACT)
    return document.value, _r8_authority(document)


def _acceptance_ids(
    environment: Environment,
) -> tuple[list[str], dict[str, Any]]:
    document = _r8_installed(environment, R8_CONTEXT_FIXTURE)
    cases = document.value.get("cases")
    if not isinstance(cases, list):
        raise ValidationError("R8 context fixture cases are not an array")
    return [row.get("test_id") for row in cases], _r8_authority(document)


def _escape_projection(
    environment: Environment,
) -> tuple[dict[str, Any], dict[str, Any]]:
    document = _r8_installed(environment, R8_ESCAPE_FIXTURE)
    value = document.value
    rows = value.get("reason_rows")
    if not isinstance(rows, list):
        raise ValidationError("R8 escape fixture reason_rows are not an array")
    predicate = _find_unique(
        environment.predicate_rows,
        "predicate_id",
        "BorrowEscapeAdmitted",
        "predicate catalog",
    )
    diagnostic_dispatch = copy.deepcopy(
        predicate.get("diagnostic_dispatch")
    )
    single_mutant_axes = {
        row.get("reason_key"): row.get("single_mutant_axis") for row in rows
    }
    return {
        "diagnostic_dispatch": diagnostic_dispatch,
        "single_mutant_axes": single_mutant_axes,
        "primary_route": copy.deepcopy(value.get("primary_route")),
        "emitted_primary_count": value.get("emitted_primary_count"),
        "global_dispatch_debt": copy.deepcopy(
            value.get("residual_dispatch_debt")
        ),
        "product_support": PRODUCT_EXECUTION,
    }, _r8_authority(document)


def _r8_class_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    return {
        name: sum(row.get("class") == name for row in cases)
        for name in ("positive", "boundary", "negative", "mutation")
    }


def _r8_context_static_decision(
    row: dict[str, Any],
) -> tuple[str, str | None]:
    if row.get("spelling") == "borrow":
        return "ACCEPT", None
    if row.get("spelling") != "&":
        return "REJECT", "AMPERSAND_POLARITY_UNRESOLVED"
    role_id = row.get("registered_role_id_or_null")
    if role_id not in {
        "NUMERIC_ARRAY_CONTEXT_PROVIDER",
        "MEASURE_UNIT_CONTEXT_PROVIDER",
    }:
        return "REJECT", "CONTEXT_EVIDENCE_ROLE_NOT_REGISTERED"
    if (
        role_id == "MEASURE_UNIT_CONTEXT_PROVIDER"
        and not row.get("unit_witness_id_or_null")
    ):
        return (
            "REJECT",
            "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
        )
    return "ACCEPT", None


def _check_context_exact_7(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    contract_doc = _r8_installed(environment, R8_CONTEXT_CONTRACT)
    schema_doc = _r8_installed(environment, R8_CONTEXT_SCHEMA)
    fixture_doc = _r8_installed(environment, R8_CONTEXT_FIXTURE)
    frontend_doc = _r8_installed(
        environment, "spec/frontend/frontend-model.json"
    )
    contract = contract_doc.value
    fixture = fixture_doc.value
    schema = schema_doc.value
    cases = fixture.get("cases")
    if not isinstance(cases, list):
        raise ValidationError("R8 context fixture cases are not an array")
    case_ids = [row.get("test_id") for row in cases]
    class_counts = _r8_class_counts(cases)
    context_rows = [row for row in cases if row.get("spelling") == "&"]
    borrow_rows = [row for row in cases if row.get("spelling") == "borrow"]
    measure_positive = _find_unique(
        cases,
        "test_id",
        "OWN-GAP-P-012",
        "R8 context fixture",
    )
    unregistered_negative = _find_unique(
        cases,
        "test_id",
        "OWN-GAP-N-012",
        "R8 context fixture",
    )
    measure_witness_mutant = copy.deepcopy(measure_positive)
    measure_witness_mutant["unit_witness_id_or_null"] = None
    measure_witness_mutant_result = _r8_context_static_decision(
        measure_witness_mutant
    )
    fixture_static_results = [
        (
            row.get("test_id"),
            *_r8_context_static_decision(row),
        )
        for row in cases
    ]
    active_diagnostic_counts = Counter(
        row.get("diagnostic_id")
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id")
        and row.get("diagnostic_status") == "active"
        and row.get("diagnostic_maturity") == "active"
        and row.get("diagnostic_class") == "current_source"
    )
    frontend = frontend_doc.value.get(
        "borrow_context_anchor_frontend_contract"
    )
    context_predicate = _find_unique(
        environment.predicate_rows,
        "predicate_id",
        "ContextAnchorOperandAdmitted",
        "predicate catalog",
    )
    numeric_predicate = _find_unique(
        environment.predicate_rows,
        "predicate_id",
        "NumericArrayContextAnchorAdmitted",
        "predicate catalog",
    )
    measure_seed_predicates = {
        predicate_id: _find_unique(
            environment.predicate_rows,
            "predicate_id",
            predicate_id,
            "predicate catalog",
        )
        for predicate_id in R8_MEASURE_SEED_PROCEDURES
    }
    context_feature_expectations = {
        "ampersand_polarity_decision_record": (
            "Tooling only",
            "documentation",
            "Tooling decision record: `&expr` is resolved by closed current "
            "position. The exact current context-provider role set is "
            "NumericArray plus Measure; generalized context/AOP/provider "
            "roles outside that set remain nonactivatable design material.",
        ),
        "borrow_escape_law_phase_a": (
            "Stable design",
            "none",
            "`borrow` is the sole general ownership-borrow spelling; expression "
            "`&` creates no loan or region.",
        ),
        "context_evidence_anchor_framework": (
            "Internal design",
            "checker_internal",
            "The current role registry is exactly NumericArray plus Measure, "
            "owned by the nearest admitted operation.",
        ),
        "contextual_operation_anchor_dmad": (
            "Preview design",
            "nonactivatable",
            "Current law: the closed current `&` context-provider surface "
            "comprises NumericArray and Measure. Generalized "
            "context/AOP/provider roles outside that exact set remain Preview "
            "Design and nonactivatable.",
        ),
        "measure_context_anchor_msp": (
            "Stable design",
            "none",
            "A Measure context anchor requires one statically selected "
            "UnitWitnessId and creates no ownership borrow.",
        ),
        "numeric_array_context_anchor_msp": (
            "Stable design",
            "none",
            "The provider operand binds one operation-owned adaptation plan and "
            "creates no ownership borrow.",
        ),
        "region_lifetime_model_phase_a": (
            "Stable design",
            "none",
            "Expression context-anchor `&` does not create a LoanId, RegionId, "
            "borrow event, or runtime role residue.",
        ),
    }
    context_features = {
        feature_id: _find_unique(
            environment.feature_rows,
            "feature_id",
            feature_id,
            "feature catalog",
        )
        for feature_id in context_feature_expectations
    }
    context_effect_diagnostic = _find_unique(
        environment.diagnostic_rows,
        "diagnostic_id",
        "CONTEXT_ANCHOR_EFFECTFUL_CONTEXT_NOT_ENABLED",
        "diagnostic catalog",
    )
    unit_witness_diagnostic = _find_unique(
        environment.diagnostic_rows,
        "diagnostic_id",
        "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
        "diagnostic catalog",
    )
    context_unit_relations = [
        row
        for row in environment.relation_rows
        if row.get("predicate_id") == "ContextAnchorOperandAdmitted"
        and row.get("diagnostic_id")
        == "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS"
    ]
    diagnostic_ids = {
        row.get("diagnostic_id") for row in environment.diagnostic_rows
    }
    grammar_path = environment.root / "spec/grammar/deeplus.ebnf"
    language_path = environment.root / "spec/language.md"
    language_text = language_path.read_text(encoding="utf-8")
    numbered_language_sections = []
    for line in language_text.splitlines():
        if line.startswith("## "):
            token = line[3:].split(" ", 1)[0].rstrip(".")
            if token.replace(".", "").isdigit():
                numbered_language_sections.append(token)
    schema_errors = _r8_schema_errors(schema, fixture)
    context_fence_errors = _r8_byte_fence_errors(
        environment.root, R8_CONTEXT_CANONICAL_FENCE
    )
    errors = _errors(
        (
            not context_fence_errors,
            "R8 context canonical byte fence changed: "
            + ",".join(context_fence_errors),
        ),
        (
            schema.get("$schema")
            == "https://json-schema.org/draft/2020-12/schema"
            and not schema_errors,
            "context fixture failed its installed Draft 2020-12 schema: "
            + "; ".join(schema_errors),
        ),
        (
            contract.get("schema")
            == "deeplus.borrow-context-anchor-disambiguation-contract/r1",
            "context contract schema identity changed",
        ),
        (
            contract.get("status")
            == "CURRENT_NORMATIVE_STABLE_DESIGN_CONTRACT"
            and contract.get("source_activation") == "none",
            "context contract status/source activation changed",
        ),
        (
            contract.get("surface_owners") == SURFACE_OWNERS,
            "surface owner partition is not exact ordered three",
        ),
        (
            [
                row.get("role_id")
                for row in contract.get("registered_context_roles", [])
            ]
            == [
                "NUMERIC_ARRAY_CONTEXT_PROVIDER",
                "MEASURE_UNIT_CONTEXT_PROVIDER",
            ],
            "registered context role set/order changed",
        ),
        (
            contract.get("diagnostic_priority")
            == [
                "AMPERSAND_POLARITY_UNRESOLVED",
                "BROADCAST_MARKER_POLARITY_IS_CONTEXT_ANCHOR",
                "CONTEXT_EVIDENCE_ROLE_NOT_REGISTERED",
                "CONTEXT_ANCHOR_NOT_A_VALUE",
                "CONTEXT_ANCHOR_REQUIRES_ELIGIBLE_OPERATION",
                "CONTEXT_ANCHOR_MULTIPLE_ANCHORS_UNSUPPORTED",
                "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
                "CONTEXT_ANCHOR_SCOPE_IS_NEAREST_OPERATION",
            ],
            "context diagnostic priority changed",
        ),
        (
            set(contract.get("diagnostic_priority", []))
            .issubset(diagnostic_ids),
            "one or more context diagnostics are absent from catalog",
        ),
        (
            contract.get("zero_counts") == BORROW_ZERO_COUNTS,
            "context zero-count fence changed",
        ),
        (
            fixture.get("schema")
            == "deeplus.borrow-context-anchor-disambiguation-fixtures/r1"
            and fixture.get("execution_status") == "SPECIFIED_NOT_RUN"
            and fixture.get("product_lanes") == "15/15_NOT_RUN",
            "context fixture governance changed",
        ),
        (
            case_ids == CONTEXT_ACCEPTANCE_IDS,
            "context fixture ID set/order is not exact seven",
        ),
        (
            class_counts
            == {
                "positive": 3,
                "boundary": 1,
                "negative": 2,
                "mutation": 1,
            },
            "context fixture class cardinality changed",
        ),
        (
            all(
                row.get("loan_id_created_in_hir") == 0
                and row.get("loan_id_created_by_mir_lowering") == 0
                and row.get("borrow_event_created") == 0
                and row.get("context_adaptation_plan_count")
                in ({1} if row.get("expected_result") == "ACCEPT" else {0})
                for row in context_rows
            ),
            "context case fabricated ownership/MIR residue",
        ),
        (
            all(
                row.get("loan_id_created_in_hir") == 0
                and row.get("loan_id_created_by_mir_lowering") == 1
                and row.get("borrow_event_created") == 1
                for row in borrow_rows
            ),
            "general borrow case did not retain MIR shared-loan lowering",
        ),
        (
            schema.get("properties", {}).get("cases", {}).get("minItems") == 7
            and schema.get("properties", {}).get("cases", {}).get("maxItems")
            == 7,
            "context fixture schema cardinality changed",
        ),
        (
            isinstance(frontend, dict)
            and frontend.get("parse_goal_partition") == SURFACE_OWNERS
            and frontend.get("registered_context_roles")
            == [
                "NUMERIC_ARRAY_CONTEXT_PROVIDER",
                "MEASURE_UNIT_CONTEXT_PROVIDER",
            ],
            "frontend context partition is absent or inconsistent",
        ),
        (
            context_predicate.get("feature_refs")
            == [
                "context_evidence_anchor_framework",
                "numeric_array_context_anchor_msp",
                "measure_context_anchor_msp",
            ]
            and context_predicate.get("descriptor_axes")
            == [
                "source_kind",
                "normalized_type",
                "source_role",
                "shape",
                "rank",
                "orientation",
                "witness_id",
                "element_types",
            ]
            and context_predicate.get("rule_facets")
            == context_predicate.get("descriptor_axes")
            and context_predicate.get("diagnostic_refs")
            == [
                "CONTEXT_ANCHOR_MULTIPLE_ANCHORS_UNSUPPORTED",
                "CONTEXT_ANCHOR_NOT_A_VALUE",
                "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
            ]
            and context_predicate.get("secondary_diagnostics")
            == [
                "CONTEXT_ANCHOR_NOT_A_VALUE",
                "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
            ]
            and context_predicate.get("positive_fixture_ids")
            == ["OWN-SURF-P-002", "OWN-GAP-P-012"]
            and context_predicate.get("negative_fixture_ids")
            == [
                "OWN-SURF-N-005",
                "OWN-SURF-M-007",
                "OWN-GAP-N-012",
            ]
            and context_predicate.get("predicate_maturity")
            == "design_algorithm"
            and context_predicate.get("emission_eligible") is True
            and context_predicate.get("decision_procedure")
            == R8_PREDICATE_PROCEDURES["ContextAnchorOperandAdmitted"],
            "generic context-anchor/witness predicate binding changed",
        ),
        (
            numeric_predicate.get("feature_refs")
            == [
                "context_evidence_anchor_framework",
                "numeric_array_context_anchor_msp",
                "numeric_array_context_anchor_polarity_law",
            ]
            and numeric_predicate.get("dependency_predicates")
            == ["ContextAnchorOperandAdmitted"]
            and numeric_predicate.get("positive_fixture_ids")
            == ["OWN-SURF-P-002"]
            and numeric_predicate.get("negative_fixture_ids")
            == [
                "OWN-SURF-N-005",
                "OWN-SURF-M-007",
            ]
            and numeric_predicate.get("predicate_maturity")
            == "design_algorithm"
            and numeric_predicate.get("emission_eligible") is True
            and numeric_predicate.get("evidence_status")
            == "DESIGN_ALGORITHM_STATIC_NOT_RUN"
            and numeric_predicate.get("product_support")
            == PRODUCT_EXECUTION
            and numeric_predicate.get("decision_procedure")
            == R8_PREDICATE_PROCEDURES[
                "NumericArrayContextAnchorAdmitted"
            ],
            "NumericArray context-anchor closed algorithm binding changed",
        ),
        (
            measure_positive.get("registered_role_id_or_null")
            == "MEASURE_UNIT_CONTEXT_PROVIDER"
            and measure_positive.get("unit_witness_id_or_null")
            == "UnitWitnessId:metre"
            and measure_positive.get("expected_result") == "ACCEPT"
            and measure_positive.get("primary_diagnostic_or_null") is None
            and unregistered_negative.get("registered_role_id_or_null") is None
            and unregistered_negative.get("unit_witness_id_or_null") is None
            and unregistered_negative.get("expected_result") == "REJECT"
            and unregistered_negative.get("primary_diagnostic_or_null")
            == "CONTEXT_EVIDENCE_ROLE_NOT_REGISTERED"
            and measure_witness_mutant_result
            == (
                "REJECT",
                "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
            ),
            "Measure UnitWitness static mutation or immutable R5 negative "
            "oracle changed",
        ),
        (
            all(
                (result, diagnostic)
                == (
                    row.get("expected_result"),
                    row.get("primary_diagnostic_or_null"),
                )
                for row, (_, result, diagnostic) in zip(
                    cases, fixture_static_results
                )
            ),
            "context fixture rows disagree with independent static decision",
        ),
        (
            all(
                row.get("language_status") == expected[0]
                and row.get("source_activation") == expected[1]
                and row.get("product_support") == PRODUCT_EXECUTION
                and row.get("artifact_trace_refs")
                == [R8_CONTEXT_CONTRACT]
                and (
                    row.get("notes") == expected[2]
                    if feature_id
                    in {
                        "ampersand_polarity_decision_record",
                        "contextual_operation_anchor_dmad",
                    }
                    else row.get("notes", "").endswith(expected[2])
                )
                for feature_id, expected in (
                    context_feature_expectations.items()
                )
                for row in [context_features[feature_id]]
            ),
            "context feature status/trace binding changed",
        ),
        (
            context_features["measure_context_anchor_msp"]
            .get("normative_trace_refs", {})
            .get("diagnostics")
            == ["UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS"]
            and context_features["measure_context_anchor_msp"]
            .get("normative_trace_refs", {})
            .get("predicates")
            == ["ContextAnchorOperandAdmitted"],
            "Measure context feature lacks exact witness trace binding",
        ),
        (
            context_unit_relations
            == [
                {
                    "diagnostic_id": (
                        "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS"
                    ),
                    "predicate_id": "ContextAnchorOperandAdmitted",
                    "relation": "secondary",
                    "violation_id": None,
                }
            ]
            and unit_witness_diagnostic.get("feature_refs")
            == [
                "unit_catalog_resolution_msp",
                "measure_context_anchor_msp",
            ]
            and unit_witness_diagnostic.get("diagnostic_status") == "active"
            and unit_witness_diagnostic.get("diagnostic_maturity") == "active"
            and unit_witness_diagnostic.get("diagnostic_class")
            == "current_source"
            and unit_witness_diagnostic.get("product_support")
            == PRODUCT_EXECUTION,
            "Context UnitWitness secondary relation or diagnostic trace "
            "binding changed",
        ),
        (
            all(
                row.get("predicate_maturity") == "design_seed"
                and row.get("emission_eligible") is False
                and row.get("decision_procedure")
                == R8_MEASURE_SEED_PROCEDURES[predicate_id]
                and row.get("execution_receipt") is None
                and row.get("dependency_predicates") == []
                for predicate_id, row in measure_seed_predicates.items()
            ),
            "Measure witness design-seed predicates were implicitly promoted",
        ),
        (
            context_effect_diagnostic.get("feature_refs")
            == [
                "numeric_array_context_anchor_msp",
                "measure_context_anchor_msp",
            ]
            and context_effect_diagnostic.get("message")
            == (
                "Effectful context anchors are outside the closed NumericArray "
                "and Measure context-provider roles."
            )
            and context_effect_diagnostic.get("notes")
            == (
                "Current-source diagnostic for a carrier outside the exact "
                "closed two-role context-anchor profile; product execution "
                "NOT_RUN."
            )
            and context_effect_diagnostic.get("diagnostic_status") == "active"
            and context_effect_diagnostic.get("diagnostic_maturity") == "active"
            and context_effect_diagnostic.get("product_support")
            == PRODUCT_EXECUTION,
            "context effect diagnostic two-role binding changed",
        ),
        (
            grammar_path.is_file()
            and not grammar_path.is_symlink()
            and _sha256(grammar_path.read_bytes()) == R41_GRAMMAR_SHA256,
            "grammar byte fence changed",
        ),
        (
            language_text.count(
                "## 59. Canonical borrow/context ownership and typed decision "
                "inputs"
            )
            == 1
            and len(numbered_language_sections)
            == len(set(numbered_language_sections)),
            "language section numbering is duplicated or R8 section is absent",
        ),
    )
    return not errors, {
        "source_locators": [
            contract_doc.locator,
            schema_doc.locator,
            fixture_doc.locator,
            frontend_doc.locator,
            "spec/grammar/deeplus.ebnf",
            "spec/language.md#59",
            "spec/types/predicates/chunks/*.json"
            "#ContextAnchorOperandAdmitted",
            "spec/types/predicates/chunks/*.json"
            "#NumericArrayContextAnchorAdmitted",
            "spec/features/catalog/chunks/*.json#context-anchor-owners",
            "spec/diagnostics/catalog/chunks/*.json"
            "#CONTEXT_ANCHOR_EFFECTFUL_CONTEXT_NOT_ENABLED",
            "spec/diagnostics/catalog/chunks/*.json"
            "#UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
            "spec/diagnostics/relations/chunks/*.json"
            "#ContextAnchorOperandAdmitted+"
            "UNIT_CONTEXT_ANCHOR_REQUIRES_KNOWN_UNIT_WITNESS",
            "spec/types/predicates/chunks/*.json"
            "#HasKnownUnitWitness+MeasureUnitWitnessAdmitted",
        ],
        "installed_canonical_paths": [
            contract_doc.locator,
            schema_doc.locator,
            fixture_doc.locator,
            frontend_doc.locator,
            *R8_CONTEXT_CANONICAL_FENCE,
        ],
        "canonical_implementation_validation": True,
        "expected_ids": CONTEXT_ACCEPTANCE_IDS,
        "observed_ids": case_ids,
        "class_counts": class_counts,
        "context_byte_fence_errors": context_fence_errors,
        "measure_witness_mutation_receipt": {
            "mutation_axis": "unit_witness_id_or_null",
            "source_test_id": "OWN-GAP-P-012",
            "mutated_value": None,
            "observed_result": measure_witness_mutant_result[0],
            "observed_primary_diagnostic": measure_witness_mutant_result[1],
            "static_validation_execution": "EXECUTED_PASS",
            "product_execution": PRODUCT_EXECUTION,
        },
        "fixture_static_results": fixture_static_results,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_overrides_exact_3(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    ownership = _doc(environment, "ownership_contract")
    metadata_doc = _r8_installed(environment, R8_PREDICATE_METADATA)
    ownership_metadata_doc = _r8_installed(
        environment, R8_OWNERSHIP_METADATA
    )
    reassembly_doc = _r8_installed(environment, R8_REASSEMBLY)
    diagnostic_metadata_doc = _r8_installed(
        environment, "spec/diagnostics/catalog/catalog-metadata.json"
    )
    relation_metadata_doc = _r8_installed(
        environment, "spec/diagnostics/relations/catalog-metadata.json"
    )
    metadata = metadata_doc.value
    ownership_expected_row = {
        "input_descriptor": "OwnershipPredicateInputR1",
        "input_descriptor_schema": (
            "schemas/language/ownership-predicate-input-r1.schema.json"
        ),
    }
    diagnostic_expected_row = {
        "input_descriptor": "DiagnosticDispatchClosureInputR1",
        "input_descriptor_schema": (
            "schemas/language/"
            "diagnostic-dispatch-closure-input-r1.schema.json"
        ),
    }
    actor_protocol_expected_row = {
        "input_descriptor": "ActorProtocolDirectConformanceDescriptorR1",
        "input_descriptor_schema": (
            "schemas/language/"
            "actor-protocol-direct-conformance-descriptor.schema.json"
        ),
    }
    expected_rows = {
        **{
            predicate_id: ownership_expected_row
            for predicate_id in OWNERSHIP_OVERRIDE_IDS
        },
        **{
            predicate_id: diagnostic_expected_row
            for predicate_id in R9_DIAGNOSTIC_OVERRIDE_IDS
        },
        **{
            predicate_id: actor_protocol_expected_row
            for predicate_id in R41_ACTOR_PROTOCOL_OVERRIDE_IDS
        },
    }
    overrides = metadata.get("input_descriptor_overrides")
    actual_rows = {
        predicate_id: _find_unique(
            environment.predicate_rows,
            "predicate_id",
            predicate_id,
            "predicate catalog",
        )
        for predicate_id in R41_INSTALLED_OVERRIDE_IDS
    }
    checker_schema = (
        environment.root
        / "schemas/language/checker-predicate-row.schema.json"
    )
    ownership_metadata = ownership_metadata_doc.value
    reassembly_matches = [
        row
        for row in reassembly_doc.value.get("contracts", [])
        if row.get("legacy_file")
        == "deeplus-0.1.2-r5-ownership-decision-conformance.json"
    ]
    active_diagnostics = {
        row.get("diagnostic_id"): row
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id")
        in {"INOUT_ALIAS_CONFLICT", "PLACE_STATE_JOIN_MISMATCH"}
    }
    feature_rows = {
        feature_id: _find_unique(
            environment.feature_rows,
            "feature_id",
            feature_id,
            "feature catalog",
        )
        for feature_id in ("box_ownership", "inout_borrow_move_modes")
    }
    ownership_artifacts = [
        "spec/contracts/ownership-decision-input-r1.json",
        "tests/fixtures/current/ownership-decision-inputs-r1.json",
        "tests/conformance/ownership-decisions/chunks/part-0001.json",
    ]
    secondary_relations = [
        {
            "violation_id": row.get("violation_id"),
            "predicate_id": row.get("predicate_id"),
            "diagnostic_id": row.get("diagnostic_id"),
            "relation": row.get("relation"),
        }
        for row in environment.relation_rows
        if row.get("predicate_id") == "OwnershipModeAdmitted"
        and row.get("diagnostic_id")
        in {"INOUT_ALIAS_CONFLICT", "PLACE_STATE_JOIN_MISMATCH"}
    ]
    errors = _errors(
        (
            ownership.sha256 == EXPECTED_FILE_SHA256["ownership_contract"],
            "ownership contract byte identity mismatch",
        ),
        (
            metadata.get("input_descriptor") == "RCTSDescriptorV5"
            and metadata.get("input_descriptor_schema")
            == "schemas/language/rcts-v5-descriptor.schema.json",
            "predicate catalog default descriptor changed",
        ),
        (
            isinstance(overrides, dict)
            and list(overrides) == R41_INSTALLED_OVERRIDE_IDS
            and overrides == expected_rows
            and metadata.get("override_count")
            == len(R41_INSTALLED_OVERRIDE_IDS),
            "installed predicate metadata override set is not exact R41",
        ),
        (
            all(
                {
                    "input_descriptor": row.get("input_descriptor"),
                    "input_descriptor_schema": row.get(
                        "input_descriptor_schema"
                    ),
                }
                == expected_rows[predicate_id]
                for predicate_id, row in actual_rows.items()
            ),
            "one or more installed predicate rows lack the exact override",
        ),
        (
            all(
                row.get("decision_procedure")
                == R8_PREDICATE_PROCEDURES[predicate_id]
                for predicate_id, row in actual_rows.items()
                if predicate_id in OWNERSHIP_OVERRIDE_IDS
            ),
            "ownership predicate decision procedures are not branch-aware",
        ),
        (
            actual_rows["BorrowEscapeAdmitted"].get(
                "diagnostic_reason_identity_rule"
            )
            == (
                "reason keys are predicate-local trace identities, never "
                "public diagnostic IDs"
            )
            and actual_rows["OwnershipModeAdmitted"].get(
                "diagnostic_reason_rank"
            )
            == R8_OWNERSHIP_MODE_REASON_RANK,
            "ownership reason identity/rank contract changed",
        ),
        (
            checker_schema.is_file()
            and not checker_schema.is_symlink()
            and _sha256(checker_schema.read_bytes())
            == R8_CHECKER_ROW_SCHEMA_SHA256,
            "checker predicate row schema byte fence changed",
        ),
        (
            ownership_metadata
            == {
                "schema": "deeplus.ownership-decision-conformance/r1",
                "baseline": "0.1.2-baseline.r51f3",
                "scenario_count": 19,
                "step_input_count": 27,
                "row_schema": (
                    "schemas/language/"
                    "ownership-decision-fixture-row-r1.schema.json"
                ),
                "payload_schema": (
                    "schemas/language/"
                    "ownership-decision-fixtures-r1.schema.json"
                ),
                "payload_path": (
                    "tests/fixtures/current/"
                    "ownership-decision-inputs-r1.json"
                ),
                "execution_status": "SPECIFIED_NOT_RUN",
                "product_support": "NOT_RUN",
                "evidence_boundary": (
                    "fully materialized typed semantic inputs and expected "
                    "outputs; production evaluator NOT_RUN"
                ),
            },
            "ownership conformance metadata changed",
        ),
        (
            len(reassembly_matches) == 1
            and reassembly_matches[0].get("array_key") == "scenarios"
            and reassembly_matches[0].get("id_key") == "test_id"
            and reassembly_matches[0].get("partition_key") == "class"
            and reassembly_matches[0].get("row_count") == 19
            and reassembly_matches[0].get("ordered_shard_paths")
            == [
                "tests/conformance/ownership-decisions/chunks/part-0001.json"
            ],
            "ownership conformance reassembly envelope changed",
        ),
        (
            diagnostic_metadata_doc.value.get("diagnostic_count") == 1452
            and relation_metadata_doc.value.get("relation_count") == 568,
            "diagnostic/relation canonical counts are not exact R41",
        ),
        (
            set(active_diagnostics)
            == {"INOUT_ALIAS_CONFLICT", "PLACE_STATE_JOIN_MISMATCH"}
            and all(
                row.get("diagnostic_status") == "active"
                and row.get("diagnostic_maturity") == "active"
                and row.get("product_support") == PRODUCT_EXECUTION
                for row in active_diagnostics.values()
            ),
            "ownership diagnostic rows are absent or not active current",
        ),
        (
            secondary_relations
            == [
                {
                    "violation_id": None,
                    "predicate_id": "OwnershipModeAdmitted",
                    "diagnostic_id": "INOUT_ALIAS_CONFLICT",
                    "relation": "secondary",
                },
                {
                    "violation_id": None,
                    "predicate_id": "OwnershipModeAdmitted",
                    "diagnostic_id": "PLACE_STATE_JOIN_MISMATCH",
                    "relation": "secondary",
                },
            ],
            "ownership secondary diagnostic relations changed",
        ),
        (
            feature_rows["box_ownership"].get("artifact_trace_refs")
            == ownership_artifacts
            and feature_rows["inout_borrow_move_modes"].get(
                "artifact_trace_refs"
            )
            == [
                "spec/contracts/type-flow-callable-coherence.json",
                "spec/mir/semantics.md",
                (
                    "tests/fixtures/current/"
                    "type-flow-callable-coherence-r1.json"
                ),
                *ownership_artifacts,
            ]
            and feature_rows["inout_borrow_move_modes"]
            .get("normative_trace_refs", {})
            .get("diagnostics")
            == [
                "OWNERSHIP_MODE_ADMISSION_FAILED",
                "INOUT_ALIAS_CONFLICT",
                "PLACE_STATE_JOIN_MISMATCH",
            ],
            "ownership feature artifact/diagnostic traces changed",
        ),
    )
    return not errors, {
        "source_locators": [
            ownership.locator,
            metadata_doc.locator,
            ownership_metadata_doc.locator,
            reassembly_doc.locator,
            diagnostic_metadata_doc.locator,
            relation_metadata_doc.locator,
            "spec/types/predicates/chunks/*.json",
            "spec/diagnostics/catalog/chunks/*.json",
            "spec/diagnostics/relations/chunks/*.json",
            "spec/features/catalog/chunks/*.json",
        ],
        "installed_canonical_paths": [
            metadata_doc.locator,
            ownership_metadata_doc.locator,
            reassembly_doc.locator,
        ],
        "canonical_implementation_validation": True,
        "expected_override_ids": R41_INSTALLED_OVERRIDE_IDS,
        "observed_override_ids": (
            list(overrides) if isinstance(overrides, dict) else None
        ),
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _binding_projection(environment: Environment) -> dict[str, Any]:
    escape, authority = _escape_projection(environment)
    predicate = _find_unique(
        environment.predicate_rows,
        "predicate_id",
        "BorrowEscapeAdmitted",
        "predicate catalog",
    )
    active_catalog_counts = Counter(
        row.get("diagnostic_id")
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id")
        and row.get("diagnostic_status") == "active"
        and row.get("diagnostic_maturity") == "active"
        and row.get("diagnostic_class") == "current_source"
    )
    relation_counts = Counter(
        (row.get("predicate_id"), row.get("diagnostic_id"))
        for row in environment.relation_rows
        if row.get("predicate_id") and row.get("diagnostic_id")
    )
    primary_relations = [
        {
            "violation_id": row.get("violation_id"),
            "predicate_id": row.get("predicate_id"),
            "diagnostic_id": row.get("diagnostic_id"),
            "relation": row.get("relation"),
        }
        for row in environment.relation_rows
        if row.get("predicate_id") == "BorrowEscapeAdmitted"
        and row.get("diagnostic_id") == BORROW_DIAGNOSTIC_ID
        and row.get("relation") == "primary"
    ]
    return {
        "predicate_id": "BorrowEscapeAdmitted",
        "reason_routes": copy.deepcopy(escape["diagnostic_dispatch"]),
        "diagnostic_refs": copy.deepcopy(predicate.get("diagnostic_refs", [])),
        "catalog_ids": [
            BORROW_DIAGNOSTIC_ID
            for _ in range(active_catalog_counts[BORROW_DIAGNOSTIC_ID])
        ],
        "active_catalog_counts": dict(active_catalog_counts),
        "primary_relations": primary_relations,
        "relation_counts": {
            f"{predicate_id}\0{diagnostic_id}": count
            for (predicate_id, diagnostic_id), count in relation_counts.items()
        },
        "reason_authority": authority,
    }


def _binding_errors(projection: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if projection.get("reason_routes") != REASON_ROUTES:
        errors.append("REASON_ROUTE_SET_OR_TARGET_MISMATCH")
    if projection.get("diagnostic_refs") != [BORROW_DIAGNOSTIC_ID]:
        errors.append("PREDICATE_DIAGNOSTIC_REF_MISSING_OR_NONEXACT")
    if projection.get("catalog_ids") != [BORROW_DIAGNOSTIC_ID]:
        errors.append("DIAGNOSTIC_CATALOG_ID_MISSING_OR_NONEXACT")
    if projection.get("primary_relations") != [BORROW_RELATION]:
        errors.append("PRIMARY_RELATION_MISSING_OR_NONEXACT")
    routes = projection.get("reason_routes")
    refs = projection.get("diagnostic_refs", [])
    active_counts = projection.get("active_catalog_counts", {})
    relation_counts = projection.get("relation_counts", {})
    unroutable = not isinstance(routes, dict)
    if isinstance(routes, dict):
        for target in routes.values():
            if (
                target not in refs
                or active_counts.get(target, 0) != 1
                or relation_counts.get(
                    f"BorrowEscapeAdmitted\0{target}", 0
                )
                != 1
            ):
                unroutable = True
    if unroutable:
        errors.append("UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET")
    return errors


def _check_reason_routes(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    escape, authority = _escape_projection(environment)
    fixture_doc = _r8_installed(environment, R8_ESCAPE_FIXTURE)
    schema_doc = _r8_installed(environment, R8_ESCAPE_SCHEMA)
    predicate = _find_unique(
        environment.predicate_rows,
        "predicate_id",
        "BorrowEscapeAdmitted",
        "predicate catalog",
    )
    reason_rows = fixture_doc.value.get("reason_rows")
    exact_top_keys = [
        "schema",
        "baseline_commit",
        "gap_id",
        "predicate_id",
        "status",
        "product_lanes",
        "selection_order",
        "pipeline_order",
        "dependency_rejection_precedes_local_dispatch",
        "emitted_primary_count",
        "later_branch_or_use_status",
        "primary_route",
        "reason_rows",
        "mutation_probes",
        "residual_dispatch_debt",
        "expected_counts",
    ]
    expected_rows = [
        {
            "reason_key": reason_key,
            "branch_rank": index,
            "single_mutant_axis": REASON_AXES[reason_key],
            "expected_diagnostic_id": diagnostic_id,
            "execution_status": "SPECIFIED_NOT_RUN",
            "product_support": PRODUCT_EXECUTION,
        }
        for index, (reason_key, diagnostic_id) in enumerate(
            REASON_ROUTES.items(), start=1
        )
    ]
    expected_primary = {
        "violation_id": "BorrowEscapeAdmitted:default",
        "predicate_id": "BorrowEscapeAdmitted",
        "diagnostic_id": BORROW_DIAGNOSTIC_ID,
        "relation": "primary",
    }
    primary_matches = [
        {
            "violation_id": row.get("violation_id"),
            "predicate_id": row.get("predicate_id"),
            "diagnostic_id": row.get("diagnostic_id"),
            "relation": row.get("relation"),
        }
        for row in environment.relation_rows
        if row.get("predicate_id") == "BorrowEscapeAdmitted"
        and row.get("diagnostic_id") == BORROW_DIAGNOSTIC_ID
        and row.get("relation") == "primary"
    ]
    branch_relations = [
        row
        for row in environment.relation_rows
        if row.get("predicate_id") == "BorrowEscapeAdmitted"
        and row.get("violation_id") in REASON_ROUTES
    ]
    public_matches = [
        row
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id") == BORROW_DIAGNOSTIC_ID
    ]
    invented_reason_diagnostics = [
        row.get("diagnostic_id")
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id") in set(REASON_ROUTES)
    ]
    schema_errors = _r8_schema_errors(
        schema_doc.value, fixture_doc.value
    )
    byte_fence_errors = []
    for relative, (expected_bytes, expected_sha256) in (
        R8_014_BYTE_FENCE.items()
    ):
        active_expected = (
            R41_014_RELATION_PART_0001_FENCE
            if relative
            == "spec/diagnostics/relations/chunks/part-0001.json"
            else (expected_bytes, expected_sha256)
        )
        path = environment.root / relative
        if (
            not path.is_file()
            or path.is_symlink()
            or path.stat().st_size != active_expected[0]
            or _sha256(path.read_bytes()) != active_expected[1]
        ):
            byte_fence_errors.append(relative)
    escape_canonical_errors = _r8_byte_fence_errors(
        environment.root, R8_ESCAPE_CANONICAL_FENCE
    )
    errors = _errors(
        (
            not escape_canonical_errors,
            "R8 escape canonical byte fence changed: "
            + ",".join(escape_canonical_errors),
        ),
        (
            list(fixture_doc.value) == exact_top_keys
            and fixture_doc.value.get("schema")
            == "deeplus.borrow-escape-diagnostic-dispatch-fixtures/r1"
            and fixture_doc.value.get("baseline_commit")
            == "1053902449aedccb110cef5bcfe76e5b1af9df01"
            and fixture_doc.value.get("gap_id") == "IR-OWN-P0-014"
            and fixture_doc.value.get("predicate_id")
            == "BorrowEscapeAdmitted"
            and fixture_doc.value.get("selection_order")
            == (
                "(canonical CFG operation order, numeric branch rank) "
                "lexicographic minimum"
            ),
            "borrow-escape fixture identity/envelope changed",
        ),
        (
            schema_doc.value.get("$schema")
            == "https://json-schema.org/draft/2020-12/schema"
            and not schema_errors,
            "borrow-escape fixture failed its installed Draft 2020-12 "
            "schema: " + "; ".join(schema_errors),
        ),
        (
            reason_rows == expected_rows,
            "installed reason rows are not the exact ordered four",
        ),
        (
            fixture_doc.value.get("mutation_probes")
            == R8_014_EXACT_MUTATION_PROBES,
            "installed mutation probes are not the exact ordered seven",
        ),
        (
            escape.get("diagnostic_dispatch") == REASON_ROUTES
            and escape.get("single_mutant_axes") == REASON_AXES,
            "installed reason route/axis projection changed",
        ),
        (
            predicate.get("diagnostic_dispatch") == REASON_ROUTES,
            "BorrowEscapeAdmitted canonical diagnostic dispatch changed",
        ),
        (
            predicate.get("diagnostic_refs") == [BORROW_DIAGNOSTIC_ID]
            and predicate.get("active_primary_diagnostic")
            == BORROW_DIAGNOSTIC_ID,
            "BorrowEscapeAdmitted diagnostic refs/active primary changed",
        ),
        (
            fixture_doc.value.get("primary_route") == expected_primary
            and primary_matches == [expected_primary],
            "borrow-escape primary route is not exact one",
        ),
        (
            len(public_matches) == 1
            and public_matches[0].get("diagnostic_status") == "active"
            and not branch_relations
            and not invented_reason_diagnostics,
            "borrow-escape public identity or branch-relation zero fence changed",
        ),
        (
            fixture_doc.value.get("status")
            == "CURRENT_NORMATIVE_STABLE_DESIGN_CONTRACT"
            and fixture_doc.value.get("product_lanes") == "15/15_NOT_RUN"
            and fixture_doc.value.get("pipeline_order")
            == [
                "schema",
                "normalization",
                "dependency",
                "predicate_local_dispatch",
            ]
            and fixture_doc.value.get(
                "dependency_rejection_precedes_local_dispatch"
            )
            is True
            and fixture_doc.value.get("emitted_primary_count") == 1
            and fixture_doc.value.get("later_branch_or_use_status")
            == "NOT_EVALUATED",
            "borrow-escape fixture ordering/evidence boundary changed",
        ),
        (
            fixture_doc.value.get("expected_counts")
            == {
                "reason_rows": 4,
                "primary_relations": 1,
                "mutation_probes": 7,
                "residual_rows": 0,
                "product_executed": 0,
            },
            "borrow-escape fixture exact counts changed",
        ),
        (
            not byte_fence_errors,
            "IR-OWN-P0-014 legacy byte fence changed: "
            + ",".join(byte_fence_errors),
        ),
    )
    return not errors, {
        "source_locators": [
            fixture_doc.locator,
            schema_doc.locator,
            "spec/types/predicates/chunks/*.json#BorrowEscapeAdmitted",
            *R8_014_BYTE_FENCE,
            *R8_ESCAPE_CANONICAL_FENCE,
        ],
        "installed_canonical_paths": [
            fixture_doc.locator,
            schema_doc.locator,
        ],
        "canonical_implementation_validation": True,
        "expected_routes": REASON_ROUTES,
        "observed_routes": escape.get("diagnostic_dispatch"),
        "schema_errors": schema_errors,
        "primary_route": primary_matches,
        "branch_relation_count": len(branch_relations),
        "invented_reason_diagnostic_count": len(invented_reason_diagnostics),
        "byte_fence_errors": byte_fence_errors,
        "escape_canonical_byte_fence_errors": escape_canonical_errors,
        "reason_authority": authority,
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _mutation_receipt(environment: Environment) -> dict[str, Any]:
    baseline = _binding_projection(environment)
    baseline_errors = _binding_errors(baseline)
    fixture_doc = _r8_installed(environment, R8_ESCAPE_FIXTURE)
    expected_probes = fixture_doc.value.get("mutation_probes")
    if not isinstance(expected_probes, list):
        raise ValidationError("R8 mutation_probes are not an array")
    mutations: list[dict[str, Any]] = []
    for index, reason_key in enumerate(REASON_ROUTES, start=1):
        probe = R8_014_EXACT_MUTATION_PROBES[index - 1]
        mutant = copy.deepcopy(baseline)
        mutant["reason_routes"][reason_key] = (
            f"R5_MUTATION_ABSENT_DIAGNOSTIC_{index}"
        )
        rejection = _binding_errors(mutant)
        mutations.append(
            {
                "mutation_id": probe.get("mutation_id"),
                "axis": probe.get("axis"),
                "expected_validator_result": probe.get(
                    "expected_validator_result"
                ),
                "expected_internal_reason": probe.get(
                    "expected_internal_reason"
                ),
                "execution_status": probe.get("execution_status"),
                "result": "REJECTED" if rejection else "SURVIVED",
                "observed_internal_reason": (
                    "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
                    if "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
                    in rejection
                    else None
                ),
                "rejection_reasons": rejection,
            }
        )
    for index in range(5, 8):
        probe = R8_014_EXACT_MUTATION_PROBES[index - 1]
        mutant = copy.deepcopy(baseline)
        if index == 5:
            mutant["diagnostic_refs"] = []
        elif index == 6:
            mutant["catalog_ids"] = []
            mutant["active_catalog_counts"][BORROW_DIAGNOSTIC_ID] = 0
        else:
            mutant["primary_relations"] = []
            mutant["relation_counts"][
                f"BorrowEscapeAdmitted\0{BORROW_DIAGNOSTIC_ID}"
            ] = 0
        rejection = _binding_errors(mutant)
        mutations.append(
            {
                "mutation_id": probe.get("mutation_id"),
                "axis": probe.get("axis"),
                "expected_validator_result": probe.get(
                    "expected_validator_result"
                ),
                "expected_internal_reason": probe.get(
                    "expected_internal_reason"
                ),
                "execution_status": probe.get("execution_status"),
                "result": "REJECTED" if rejection else "SURVIVED",
                "observed_internal_reason": (
                    "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
                    if "UNDEFINED_OR_UNROUTABLE_DIAGNOSTIC_TARGET"
                    in rejection
                    else None
                ),
                "rejection_reasons": rejection,
            }
        )
    rejected = sum(row["result"] == "REJECTED" for row in mutations)
    exact_probe_binding = (
        expected_probes == R8_014_EXACT_MUTATION_PROBES
        and all(
            {
                "mutation_id": row.get("mutation_id"),
                "axis": row.get("axis"),
                "expected_validator_result": row.get(
                    "expected_validator_result"
                ),
                "expected_internal_reason": row.get(
                    "expected_internal_reason"
                ),
                "execution_status": row.get("execution_status"),
            }
            == probe
            and row.get("result") == probe.get("expected_validator_result")
            and row.get("observed_internal_reason")
            == probe.get("expected_internal_reason")
            for row, probe in zip(
                mutations, R8_014_EXACT_MUTATION_PROBES
            )
        )
    )
    result = (
        "PASS"
        if (
            not baseline_errors
            and len(mutations) == 7
            and rejected == 7
            and exact_probe_binding
        )
        else "FAIL"
    )
    return {
        "schema": MUTATION_SCHEMA,
        "result": result,
        "static_validation_execution": (
            "EXECUTED_PASS" if result == "PASS" else "EXECUTED_FAIL"
        ),
        "baseline_errors": baseline_errors,
        "expected_mutation_count": 7,
        "observed_mutation_count": len(mutations),
        "rejected_mutation_count": rejected,
        "exact_fixture_probe_binding": exact_probe_binding,
        "mutations": mutations,
        "reason_route_authority": baseline["reason_authority"],
        "canonical_implementation_validation": True,
        "installed_canonical_path_or_null": fixture_doc.locator,
        "production_evaluator_execution": PRODUCT_EXECUTION,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_binding_mutations(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    receipt = _mutation_receipt(environment)
    errors = _errors(
        (
            receipt["result"] == "PASS"
            and receipt["canonical_implementation_validation"] is True,
            "one or more canonical-loaded binding mutations survived",
        ),
    )
    return not errors, {
        "source_locators": [
            "spec/types/predicates/chunks/*.json#BorrowEscapeAdmitted",
            "spec/diagnostics/catalog/chunks/*.json",
            "spec/diagnostics/relations/chunks/*.json",
            R8_ESCAPE_FIXTURE,
        ],
        "installed_canonical_paths": [R8_ESCAPE_FIXTURE],
        "canonical_implementation_validation": True,
        "mutation_receipt": receipt,
        "installed_canonical_path_or_null": R8_ESCAPE_FIXTURE,
        "acceptance_oracle_label": "INSTALLED_CANONICAL_STATIC_CONTRACT",
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


def _check_residual_debt(
    environment: Environment,
) -> tuple[bool, dict[str, Any]]:
    fixture_doc = _r8_installed(environment, R8_ESCAPE_FIXTURE)
    debt = fixture_doc.value.get("residual_dispatch_debt")
    if not isinstance(debt, dict):
        raise ValidationError("R8 residual_dispatch_debt is not an object")
    active_diagnostic_counts = Counter(
        row.get("diagnostic_id")
        for row in environment.diagnostic_rows
        if row.get("diagnostic_id")
        and row.get("diagnostic_status") == "active"
        and row.get("diagnostic_maturity") == "active"
        and row.get("diagnostic_class") == "current_source"
    )
    scanned: list[dict[str, Any]] = []
    for predicate in sorted(
        environment.predicate_rows,
        key=lambda row: str(row.get("predicate_id", "")),
    ):
        predicate_id = predicate.get("predicate_id")
        dispatch = predicate.get("diagnostic_dispatch")
        if not isinstance(predicate_id, str) or not isinstance(dispatch, dict):
            continue
        refs = predicate.get("diagnostic_refs", [])
        for branch, target in dispatch.items():
            relation_count = sum(
                row.get("predicate_id") == predicate_id
                and row.get("diagnostic_id") == target
                for row in environment.relation_rows
            )
            catalog_exact_one = active_diagnostic_counts[target] == 1
            listed = target in refs
            if not (catalog_exact_one and listed and relation_count == 1):
                scanned.append(
                    {
                        "predicate_id": predicate_id,
                        "branch": branch,
                        "target": target,
                    }
                )
    expected = debt.get("outside_r5_exact_debt_rows")
    errors = _errors(
        (
            debt.get("r5_borrow_escape_unresolved_after_candidate") == 0,
            "R8 BorrowEscape residual is not zero",
        ),
        (
            debt.get("outside_r5_gap_id") == "IR-DIAG-P0-052"
            and debt.get("outside_r5_exact_rows")
            == INSTALLED_CURRENT_RESIDUAL_EXACT_ROWS
            and debt.get("outside_r5_total") == 0
            and debt.get("global_zero_totality")
            == "CLOSED_BY_IR-DIAG-P0-052_R9"
            and debt.get("new_or_missing_residual") == "VALIDATOR_FAIL",
            "installed current residual-debt envelope is not exact zero",
        ),
        (
            expected == INSTALLED_CURRENT_RESIDUAL_DEBT_ROWS
            and scanned == INSTALLED_CURRENT_RESIDUAL_DEBT_ROWS,
            "installed undefined-dispatch scan is not exact zero",
        ),
    )
    return not errors, {
        "source_locators": [
            "spec/types/predicates/chunks/*.json#diagnostic_dispatch",
            "spec/diagnostics/catalog/chunks/*.json#diagnostic_id",
            "spec/diagnostics/relations/chunks/*.json"
            "#predicate_id+diagnostic_id",
            fixture_doc.locator,
        ],
        "installed_canonical_paths": [fixture_doc.locator],
        "installed_canonical_path_or_null": fixture_doc.locator,
        "acceptance_oracle_label": "INSTALLED_CANONICAL_STATIC_CONTRACT",
        "canonical_implementation_validation": True,
        "historical_r8_candidate_rows": HISTORICAL_R8_RESIDUAL_DEBT_ROWS,
        "expected_rows": INSTALLED_CURRENT_RESIDUAL_DEBT_ROWS,
        "observed_rows": scanned,
        "observed_residual_count": len(scanned),
        "errors": errors,
        "product_execution": PRODUCT_EXECUTION,
    }


CHECK_FUNCTIONS: tuple[
    tuple[str, Callable[[Environment], tuple[bool, dict[str, Any]]]], ...
] = (
    (WORKSPACE_CHECK_IDS[0], _check_surface_partition),
    (WORKSPACE_CHECK_IDS[1], _check_context_exact_7),
    (WORKSPACE_CHECK_IDS[2], _check_hir_h1_fence),
    (WORKSPACE_CHECK_IDS[3], _check_union_exact_2),
    (WORKSPACE_CHECK_IDS[4], _check_overrides_exact_3),
    (WORKSPACE_CHECK_IDS[5], _check_schema_closed),
    (WORKSPACE_CHECK_IDS[6], _check_fixture_catalog),
    (WORKSPACE_CHECK_IDS[7], _check_profile_b),
    (WORKSPACE_CHECK_IDS[8], _check_reason_routes),
    (WORKSPACE_CHECK_IDS[9], _check_primary_route),
    (WORKSPACE_CHECK_IDS[10], _check_binding_mutations),
    (WORKSPACE_CHECK_IDS[11], _check_residual_debt),
    (WORKSPACE_CHECK_IDS[12], _check_governance),
)

INTERNAL_ERROR_LOCATORS = {
    WORKSPACE_CHECK_IDS[0]: [
        "spec/features/catalog/chunks/*.json#feature_id",
        "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY#surface_owners",
    ],
    WORKSPACE_CHECK_IDS[1]: [
        "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY#IR-OWN-P0-012"
    ],
    WORKSPACE_CHECK_IDS[2]: list(HIR_H1_FENCE),
    WORKSPACE_CHECK_IDS[3]: [
        "schemas/language/ownership-predicate-input-r1.schema.json#oneOf"
    ],
    WORKSPACE_CHECK_IDS[4]: [
        (
            "spec/contracts/ownership-decision-input-r1.json"
            "#predicate_input_dispatch"
        )
    ],
    WORKSPACE_CHECK_IDS[5]: [
        "schemas/language/ownership-decision-input-r1.schema.json",
        "schemas/language/ownership-decision-fixtures-r1.schema.json",
        "schemas/language/ownership-decision-fixture-row-r1.schema.json",
    ],
    WORKSPACE_CHECK_IDS[6]: [
        "tests/fixtures/current/ownership-decision-inputs-r1.json",
        "tests/conformance/ownership-decisions/chunks/part-0001.json",
    ],
    WORKSPACE_CHECK_IDS[7]: [
        "tests/fixtures/current/ownership-decision-inputs-r1.json"
    ],
    WORKSPACE_CHECK_IDS[8]: [
        "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY#diagnostic_dispatch"
    ],
    WORKSPACE_CHECK_IDS[9]: [
        "spec/types/predicates/chunks/*.json",
        "spec/diagnostics/catalog/chunks/*.json",
        "spec/diagnostics/relations/chunks/*.json",
    ],
    WORKSPACE_CHECK_IDS[10]: [
        "spec/types/predicates/chunks/*.json",
        "spec/diagnostics/catalog/chunks/*.json",
        "spec/diagnostics/relations/chunks/*.json",
        "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY#diagnostic_dispatch",
    ],
    WORKSPACE_CHECK_IDS[11]: [
        "spec/types/predicates/chunks/*.json#diagnostic_dispatch",
        "NONCANONICAL_ACCEPTANCE_ORACLE_ONLY#global_dispatch_debt",
    ],
    WORKSPACE_CHECK_IDS[12]: [
        "current/current-pointer.json#open_actions",
        "current/current-pointer.json#product_lanes",
    ],
}


def _failed_workspace_receipt(error: str) -> dict[str, Any]:
    checks = [
        {
            "check_id": check_id,
            "pass": False,
            "detail": _detail(
                {
                    "source_locators": INTERNAL_ERROR_LOCATORS[check_id],
                    "internal_error": error,
                    "fail_closed_scope": "ALL_EXACT_13_ROWS",
                    "product_execution": PRODUCT_EXECUTION,
                }
            ),
        }
        for check_id in WORKSPACE_CHECK_IDS
    ]
    return {
        "schema": WORKSPACE_SCHEMA,
        "result": "FAIL",
        "static_validation_execution": "EXECUTED_FAIL",
        "product_execution": PRODUCT_EXECUTION,
        "passed_check_id_scope": PASSED_CHECK_ID_SCOPE,
        "workspace_check_id_count": 13,
        "checks": checks,
        "passed_check_ids": [],
    }


def _run_workspace_checks(environment: Environment) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        for check_id, check_function in CHECK_FUNCTIONS:
            passed, detail = check_function(environment)
            detail = dict(detail)
            detail["canonical_implementation_validation"] = (
                environment.projection_root is None
            )
            detail.setdefault(
                "installed_canonical_paths",
                [
                    locator
                    for locator in detail.get("source_locators", [])
                    if isinstance(locator, str)
                    and not locator.startswith("NONCANONICAL_")
                ],
            )
            checks.append(
                {
                    "check_id": check_id,
                    "pass": bool(passed),
                    "detail": _detail(detail),
                }
            )
    except Exception as error:  # fail closed to an exact 13-row receipt
        return _failed_workspace_receipt(
            f"{type(error).__name__}: {error}"
        )
    if (
        len(checks) != 13
        or [row["check_id"] for row in checks] != list(WORKSPACE_CHECK_IDS)
    ):
        return _failed_workspace_receipt(
            "internal ordered workspace check registry drift"
        )
    passed_check_ids = [
        row["check_id"] for row in checks if row["pass"] is True
    ]
    result = "PASS" if len(passed_check_ids) == 13 else "FAIL"
    return {
        "schema": WORKSPACE_SCHEMA,
        "result": result,
        "static_validation_execution": (
            "EXECUTED_PASS" if result == "PASS" else "EXECUTED_FAIL"
        ),
        "product_execution": PRODUCT_EXECUTION,
        "passed_check_id_scope": PASSED_CHECK_ID_SCOPE,
        "workspace_check_id_count": 13,
        "checks": checks,
        "passed_check_ids": passed_check_ids,
        "canonical_implementation_validation": (
            environment.projection_root is None
        ),
        "installed_canonical_validation_scope": "IR-OWN-P0-012..014",
    }


def _typed_fixture_receipt_binding(
    environment: Environment,
) -> dict[str, Any]:
    document = environment.documents["typed_fixture_receipt"]
    if document is None:
        return {
            "result": "NOT_RUN",
            "binding_status": "IMMUTABLE_PREDECESSOR_RECEIPT_NOT_INSTALLED",
            "expected_check_count": 62,
            "reexecuted_check_count": 0,
            "execution_boundary": (
                "STATIC_PROJECTION_CHECKS_EXECUTED; "
                "62-CHECK PREDECESSOR VALIDATOR NOT_REEXECUTED"
            ),
            "product_execution": PRODUCT_EXECUTION,
        }
    value = document.value
    binding_pass = (
        value.get("verdict") == "PASS"
        and value.get("check_count") == 62
        and value.get("passed") == 62
        and value.get("failed") == []
        and value.get("passed_check_ids") == list(TYPED_FIXTURE_CHECK_IDS)
        and value.get("counts") == FIXTURE_COUNTS
    )
    return {
        "result": "PASS" if binding_pass else "FAIL",
        "binding_status": (
            "IMMUTABLE_R5_PREDECESSOR_RECEIPT_REVALIDATED"
            if binding_pass
            else "IMMUTABLE_R5_PREDECESSOR_RECEIPT_DRIFT"
        ),
        "source_locator": document.locator,
        "expected_check_count": 62,
        "bound_passed_check_count": (
            len(value.get("passed_check_ids", []))
            if isinstance(value.get("passed_check_ids"), list)
            else 0
        ),
        "reexecuted_check_count": 0,
        "execution_boundary": (
            "RECEIPT_AND_STATIC_PROJECTIONS_REVALIDATED; "
            "ORIGINAL_62-CHECK VALIDATOR NOT_REEXECUTED"
        ),
        "product_execution": PRODUCT_EXECUTION,
    }


def _full_receipt(
    environment: Environment,
    workspace_receipt: dict[str, Any],
) -> dict[str, Any]:
    mutation_detail = json.loads(
        next(
            row["detail"]
            for row in workspace_receipt["checks"]
            if row["check_id"]
            == "R5_OWN_014_BINDING_MUTATIONS_EXACT_7"
        )
    )
    profile_detail = json.loads(
        next(
            row["detail"]
            for row in workspace_receipt["checks"]
            if row["check_id"] == "R5_OWN_013_PROFILE_B_EXACT"
        )
    )
    fixture_binding = _typed_fixture_receipt_binding(environment)
    authoring_fixture = environment.documents["authoring_fixture"]
    full_pass = (
        workspace_receipt["result"] == "PASS"
        and mutation_detail.get("mutation_receipt", {}).get("result")
        == "PASS"
        and profile_detail.get("profile_b_receipt", {}).get("result")
        == "PASS"
        and fixture_binding.get("result") in {"PASS", "NOT_RUN"}
    )
    return {
        "schema": FULL_SCHEMA,
        "result": "PASS" if full_pass else "FAIL",
        "static_validation_execution": (
            "EXECUTED_PASS" if full_pass else "EXECUTED_FAIL"
        ),
        "product_execution": PRODUCT_EXECUTION,
        "passed_check_id_scope": PASSED_CHECK_ID_SCOPE,
        "workspace_check_id_count": 13,
        "checks": workspace_receipt["checks"],
        "passed_check_ids": workspace_receipt["passed_check_ids"],
        "payload_sha256_or_null": (
            _canonical_digest(authoring_fixture.value)
            if authoring_fixture is not None
            else None
        ),
        "typed_fixture_receipt_binding": fixture_binding,
        "profile_b_receipt": profile_detail.get("profile_b_receipt"),
        "mutation_receipt": mutation_detail.get("mutation_receipt"),
        "execution_boundary": {
            "static_contract_schema_fixture_conformance": (
                "EXECUTED_PASS" if full_pass else "EXECUTED_FAIL"
            ),
            "production_parser_checker_compiler_runtime": PRODUCT_EXECUTION,
            "noncanonical_oracle_label": NONCANONICAL_ORACLE,
        },
    }


def _parse_arguments(
    argv: list[str],
) -> tuple[str, str | None, bool, bool, bool]:
    root = "."
    projection_root: str | None = None
    workspace_only = False
    pretty = False
    help_requested = False
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--root":
            index += 1
            if index >= len(argv):
                raise ValidationError("--root requires a value")
            root = argv[index]
        elif argument == "--projection-root":
            index += 1
            if index >= len(argv):
                raise ValidationError("--projection-root requires a value")
            projection_root = argv[index]
        elif argument == "--workspace-checks-only":
            workspace_only = True
        elif argument == "--pretty":
            pretty = True
        elif argument in {"--help", "-h"}:
            help_requested = True
        else:
            raise ValidationError(f"unknown argument: {argument}")
        index += 1
    return root, projection_root, workspace_only, pretty, help_requested


def _emit(value: dict[str, Any], pretty: bool) -> None:
    print(
        json.dumps(
            value,
            # ASCII escaping makes the subprocess protocol byte-stable UTF-8
            # even on Windows hosts whose redirected stdout uses a legacy code
            # page and whose OSError text is localized.
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=False,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
        )
    )


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    workspace_requested = "--workspace-checks-only" in arguments
    pretty_requested = "--pretty" in arguments
    try:
        (
            root_arg,
            projection_arg,
            workspace_only,
            pretty,
            help_requested,
        ) = _parse_arguments(arguments)
        if help_requested:
            print(
                "usage: run_r5_ownership_decision_mutation_tests.py "
                "[--root PATH] [--projection-root PATH] "
                "[--workspace-checks-only] [--pretty]"
            )
            return 0
        environment = _build_environment(root_arg, projection_arg)
        workspace_receipt = _run_workspace_checks(environment)
        if workspace_only:
            _emit(workspace_receipt, pretty)
            # The parent workspace validator consumes semantic FAIL as data.
            # Any well-formed exact 13-row workspace receipt exits zero.
            return 0
        receipt = _full_receipt(environment, workspace_receipt)
        _emit(receipt, pretty)
        return 0 if receipt["result"] == "PASS" else 1
    except Exception as error:
        message = f"{type(error).__name__}: {error}"
        if workspace_requested:
            _emit(_failed_workspace_receipt(message), pretty_requested)
            return 0
        receipt = {
            "schema": FULL_SCHEMA,
            "result": "FAIL",
            "static_validation_execution": "EXECUTED_FAIL",
            "product_execution": PRODUCT_EXECUTION,
            "passed_check_id_scope": PASSED_CHECK_ID_SCOPE,
            "workspace_check_id_count": 13,
            "checks": _failed_workspace_receipt(message)["checks"],
            "passed_check_ids": [],
            "execution_boundary": {
                "internal_error": message,
                "production_parser_checker_compiler_runtime": (
                    PRODUCT_EXECUTION
                ),
            },
        }
        _emit(receipt, pretty_requested)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
