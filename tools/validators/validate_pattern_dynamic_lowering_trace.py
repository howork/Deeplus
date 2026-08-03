#!/usr/bin/env python3
"""Validate the bounded R59 pattern dynamic-lowering trace closure."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/pattern-dynamic-lowering-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/pattern-dynamic-lowering-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/pattern-dynamic-lowering-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/pattern-dynamic-lowering-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
PL_REL = "spec/patterns/pattern-lowering.json"
PK_REL = "spec/patterns/pattern-kinds.json"
CONTEXT_REL = "spec/patterns/pattern-context-policies.json"
HM_REL = "spec/contracts/hir-mir-lowering-registry.json"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "fb3e98888f947d0e7b45f713efe3b017a55c976a"
FEATURES = [
    "or_alias_pattern",
    "pattern_binding_control_family",
    "pattern_decomposition",
]
TARGET_CELLS = {(feature, "DYNAMIC_LOWERING", None) for feature in FEATURES}
PRIOR_OVERLAYS = [
    "spec/traceability/implementation-target-profile-r1/scalar-numeric-fixed-operator-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json",
    "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json",
]
CURRENT_SUFFIXES = [
    "BINDER",
    "UNION-ALTERNATIVE-BINDER",
    "TYPED-BINDER",
    "WILDCARD",
    "UNIT",
    "LITERAL",
    "PARENTHESIZED",
    "TUPLE",
    "LIST-EXACT",
    "LIST-IGNORED-TAIL",
    "LIST-SUFFIX-REST",
    "LIST-PREFIX-REST",
    "LIST-MIDDLE-REST",
    "RECORD-EXACT",
    "RECORD-OPEN-IGNORED",
    "RECORD-OPEN-CAPTURED",
    "MAP-EXACT",
    "MAP-OPEN-IGNORED",
    "MAP-OPEN-CAPTURED",
    "NOMINAL-TRANSPARENT",
    "VARIANT",
    "VARIANT-NAMED",
    "PIN",
    "RANGE",
    "RELATIONAL",
    "BOUNDED-BINDER",
    "OR",
    "ALIAS",
    "MOVE",
]
EXPECTED_MAPPINGS = [
    {
        "pattern_lowering_id": f"PL-{suffix}",
        "pattern_kind_id": f"PK-{suffix}",
        "hir_mir_row_id": f"HM-LR-PAT-{ordinal:03d}",
    }
    for ordinal, suffix in enumerate(CURRENT_SUFFIXES, start=1)
]
EXPECTED_CONTEXTS = [
    {
        "context_id": "PCTX-IF-LET",
        "hir_mir_row_ids": ["HM-LR-TOP-016", "HM-LR-TOP-008"],
        "failure_disposition": "FALSE_BRANCH",
    },
    {
        "context_id": "PCTX-WHILE-LET",
        "hir_mir_row_ids": ["HM-LR-TOP-016", "HM-LR-TOP-011"],
        "failure_disposition": "LOOP_EXIT",
    },
    {
        "context_id": "PCTX-PATTERN-CONDITION-CHAIN",
        "hir_mir_row_ids": ["HM-LR-TOP-016", "HM-LR-TOP-008"],
        "failure_disposition": "CONDITION_FALSE",
    },
    {
        "context_id": "PCTX-BARE-FOR",
        "hir_mir_row_ids": ["HM-LR-TOP-016", "HM-LR-TOP-011"],
        "failure_disposition": "COMPILE_TIME_REJECTION_OR_CANDIDATE_SKIP",
    },
    {
        "context_id": "PCTX-FOR-LET",
        "hir_mir_row_ids": ["HM-LR-TOP-016", "HM-LR-TOP-011"],
        "failure_disposition": "CANDIDATE_SKIP",
    },
]
EXPECTED_ACCEPTANCE_BINDINGS = {
    "or_alias_pattern": {
        "POSITIVE": ["PDLTC-AC-001", "PDLTC-AC-003"],
        "BOUNDARY": ["PDLTC-AC-002"],
        "REJECT": ["PDLTC-AC-004"],
    },
    "pattern_binding_control_family": {
        "BOUNDARY": ["PDLTC-AC-005", "PDLTC-AC-006", "PDLTC-AC-007", "PDLTC-AC-008"],
        "REJECT": ["PDLTC-AC-009"],
    },
    "pattern_decomposition": {
        "POSITIVE": ["PDLTC-AC-010"],
        "BOUNDARY": ["PDLTC-AC-011"],
        "REJECT": ["PDLTC-AC-012"],
    },
}
EXPECTED_LOCATORS = {
    "or_alias_pattern": "PDLTC-R009",
    "pattern_binding_control_family": "PDLTC-R003",
    "pattern_decomposition": "PDLTC-R002",
}
EXPECTED_EXCLUDED_REVERSE_DEPENDENTS = [
    "assertive_pattern_binding",
    "irrefutable_parameter_entry_pattern",
    "pattern_advanced_surface_preview_design",
    "pattern_condition_chain",
    "pin_range_relational_pattern",
    "refutable_catch_pattern",
    "sequence_positional_rest_pattern",
    "structured_record_map_pattern",
    "transparent_nominal_named_enum_pattern",
    "tuple_bare_product_surface",
]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def contains_scalar(value: Any, expected: str) -> bool:
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(contains_scalar(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(contains_scalar(item, expected) for item in value)
    return False


def trace_cells(
    rows: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str, str | None], dict[str, Any]], int]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    duplicate_count = 0
    for row in rows:
        feature = row.get("feature_id")
        for stage in row.get("stages", []):
            stage_name = stage.get("stage")
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                key = (feature, stage_name, outcome)
                duplicate_count += key in cells
                cells[key] = cell
    return cells, duplicate_count


def disposition_counts(cells: dict[tuple[str, str, str | None], str]) -> tuple[int, int, int, int]:
    counts = Counter(cells.values())
    return tuple(
        counts[key]
        for key in (
            "BOUND_DIRECT",
            "BOUND_DELEGATED",
            "NOT_APPLICABLE",
            "APPLICABLE_BLOCKED_BY_GAP",
        )
    )


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    *,
    validate_schema: bool = True,
    trace_rows_override: list[dict[str, Any]] | None = None,
    pattern_lowering_override: dict[str, Any] | None = None,
    pattern_kinds_override: dict[str, Any] | None = None,
    hm_registry_override: dict[str, Any] | None = None,
    context_registry_override: dict[str, Any] | None = None,
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
        require(value.get("feature_ids") == FEATURES, f"{prefix}_FEATURES_EXACT")

    require(contract.get("$schema") == "../../schemas/language/pattern-dynamic-lowering-trace-closure-r1.schema.json", "CONTRACT_SCHEMA_BINDING")
    require(contract.get("schema") == "deeplus.pattern-dynamic-lowering-trace-closure/r1", "CONTRACT_SCHEMA_ID")
    require(contract.get("revision") == "r59-local-pattern-dynamic-lowering-trace-closure-r1", "CONTRACT_REVISION")
    require(contract.get("candidate_status") == "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE", "CONTRACT_CANDIDATE_STATUS")
    require(contract.get("language_status") == "STABLE_DESIGN", "CONTRACT_LANGUAGE_STATUS")
    require(overlay.get("$schema") == "../../../schemas/language/pattern-dynamic-lowering-evidence-r1.schema.json", "OVERLAY_SCHEMA_BINDING")
    require(overlay.get("schema") == "deeplus.pattern-dynamic-lowering-evidence/r1", "OVERLAY_SCHEMA_ID")
    require(overlay.get("revision") == "r59-local-pattern-dynamic-lowering-trace-closure-r1", "OVERLAY_REVISION")
    require(overlay.get("candidate_status") == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY", "OVERLAY_CANDIDATE_STATUS")

    require(contract.get("source_activation") == "none", "CONTRACT_SOURCE_INACTIVE")
    require(contract.get("current_binding") is False, "CONTRACT_NOT_CURRENT")
    scope = contract.get("scope_fence", {})
    expected_transitions = [
        {
            "feature_id": feature,
            "stage": "DYNAMIC_LOWERING",
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": "BOUND_DIRECT",
        }
        for feature in FEATURES
    ]
    require(scope.get("transitioned_cells") == expected_transitions, "SCOPE_TARGET_CELLS_EXACT_3")
    require(
        scope.get("excluded_feature_stage_cells")
        == [
            "pattern_match_ownership_split/STATIC_SEMANTICS",
            "pattern_match_ownership_split/DYNAMIC_LOWERING",
        ],
        "SCOPE_OWNERSHIP_SPLIT_EXCLUDED",
    )
    require(
        scope.get("excluded_reverse_dependents_of_pattern_decomposition")
        == EXPECTED_EXCLUDED_REVERSE_DEPENDENTS,
        "SCOPE_REVERSE_DEPENDENTS_EXACT_10",
    )
    require(
        all(
            scope.get(key) == 0
            for key in (
                "preview_pattern_rows_transition_count",
                "other_target_cell_transition_count",
                "ownership_split_transition_count",
                "reverse_dependent_transition_count",
            )
        ),
        "SCOPE_NO_OTHER_TRANSITIONS",
    )

    pl = pattern_lowering_override or load(root / PL_REL)
    pk = pattern_kinds_override or load(root / PK_REL)
    hm = hm_registry_override or load(root / HM_REL)
    contexts = context_registry_override or load(root / CONTEXT_REL)
    current_pl = [row for row in pl.get("rows", []) if row.get("status") == "CURRENT_LOWERING_CONTRACT"]
    current_pk = [row for row in pk.get("rows", []) if row.get("surface_status") == "CURRENT_REACHABLE"]
    current_hm = [
        row
        for row in hm.get("rows", [])
        if row.get("row_family") == "PATTERN" and row.get("profile_gate") == "CURRENT"
    ]
    require(len(current_pl) == 29, "PL_CURRENT_EXACT_29")
    require(len(current_pk) == 29, "PK_CURRENT_EXACT_29")
    require(len(current_hm) == 29, "HM_PATTERN_CURRENT_EXACT_29")
    require(
        [(row.get("lowering_id"), row.get("pattern_kind_id")) for row in current_pl]
        == [
            (item["pattern_lowering_id"], item["pattern_kind_id"])
            for item in EXPECTED_MAPPINGS
        ],
        "PL_PK_CURRENT_ORDERED_BIJECTION",
    )
    require(
        [row.get("pattern_kind_id") for row in current_pk]
        == [item["pattern_kind_id"] for item in EXPECTED_MAPPINGS],
        "PK_CURRENT_ORDERED_IDENTITY",
    )
    hm_by_id = {row.get("row_id"): row for row in current_hm}
    require(len(hm_by_id) == len(current_hm), "HM_CURRENT_ROW_UNIQUE")
    require(set(hm_by_id) == {item["hir_mir_row_id"] for item in EXPECTED_MAPPINGS}, "HM_CURRENT_ROW_SET")
    for item in EXPECTED_MAPPINGS:
        row = hm_by_id.get(item["hir_mir_row_id"], {})
        dispatch = row.get("lowering_dispatch_key", {})
        require(dispatch.get("kind") == "PATTERN", f"HM_DISPATCH_KIND:{item['hir_mir_row_id']}")
        require(dispatch.get("pattern_profile") == "CURRENT", f"HM_DISPATCH_PROFILE:{item['hir_mir_row_id']}")
        require(dispatch.get("identity_id") == item["pattern_kind_id"], f"HM_DISPATCH_ID:{item['hir_mir_row_id']}")
        require(row.get("counts_toward_current_102") is True, f"HM_CURRENT_COUNT:{item['hir_mir_row_id']}")
        require(row.get("product_support") == "NOT_RUN", f"HM_PRODUCT_NOT_RUN:{item['hir_mir_row_id']}")
    require(all(row.get("product_execution") == "NOT_RUN" for row in current_pl + current_pk), "PL_PK_PRODUCT_NOT_RUN")

    alignment = contract.get("current_registry_alignment", {})
    require(alignment.get("pattern_lowering_registry") == PL_REL, "ALIGN_PL_PATH")
    require(alignment.get("pattern_kind_registry") == PK_REL, "ALIGN_PK_PATH")
    require(alignment.get("hir_mir_lowering_registry") == HM_REL, "ALIGN_HM_PATH")
    require(alignment.get("current_mapping_count") == 29, "ALIGN_MAPPING_COUNT_29")
    require(alignment.get("mappings") == EXPECTED_MAPPINGS, "ALIGN_MAPPINGS_EXACT_29")
    require(alignment.get("exact_or_mapping") == EXPECTED_MAPPINGS[26], "ALIGN_OR_EXACT")
    require(alignment.get("exact_alias_mapping") == EXPECTED_MAPPINGS[27], "ALIGN_ALIAS_EXACT")

    pl_by_id = {row.get("lowering_id"): row for row in current_pl}
    pk_by_id = {row.get("pattern_kind_id"): row for row in current_pk}
    for suffix, ordinal in (("OR", 27), ("ALIAS", 28)):
        pl_row = pl_by_id.get(f"PL-{suffix}", {})
        pk_row = pk_by_id.get(f"PK-{suffix}", {})
        hm_row = hm_by_id.get(f"HM-LR-PAT-{ordinal:03d}", {})
        require(pl_row.get("pattern_kind_id") == f"PK-{suffix}", f"{suffix}_PL_PK_EXACT")
        require(pk_row.get("surface_status") == "CURRENT_REACHABLE", f"{suffix}_PK_CURRENT")
        require(hm_row.get("lowering_rule_id") == f"DM-LR-PAT-PK-{suffix}-R1", f"{suffix}_HM_RULE")
        require(
            hm_row.get("hir_identity_ids")
            == ["HIR-H1/EXPR/PATTERN_ATTEMPT", f"HIR-H1/PATTERN/PK-{suffix}"],
            f"{suffix}_HM_HIR_IDENTITIES",
        )

    context_alignment = contract.get("context_lowering_alignment", {})
    require(context_alignment.get("pattern_context_registry") == CONTEXT_REL, "CONTEXT_REGISTRY_PATH")
    require(context_alignment.get("pattern_attempt_row_id") == "HM-LR-TOP-016", "CONTEXT_PATTERN_ATTEMPT_ROW")
    require(context_alignment.get("if_owner_row_id") == "HM-LR-TOP-008", "CONTEXT_IF_ROW")
    require(context_alignment.get("loop_owner_row_id") == "HM-LR-TOP-011", "CONTEXT_LOOP_ROW")
    require(context_alignment.get("contexts") == EXPECTED_CONTEXTS, "CONTEXT_ALIGNMENT_EXACT_5")
    context_by_id = {row.get("context_id"): row for row in contexts.get("rows", [])}
    expected_context_policies = {
        "PCTX-IF-LET": ("IF_FALSE_BRANCH", "NOT_APPLICABLE"),
        "PCTX-WHILE-LET": ("WHILE_TERMINATE", "NOT_APPLICABLE"),
        "PCTX-PATTERN-CONDITION-CHAIN": ("PATTERN_CONDITION_CHAIN_FALSE", "PATTERN_CONDITION_CHAIN_FALSE"),
        "PCTX-BARE-FOR": ("COMPILE_TIME_REJECTION", "FOR_CANDIDATE_SKIP"),
        "PCTX-FOR-LET": ("FOR_CANDIDATE_SKIP", "FOR_CANDIDATE_SKIP"),
    }
    for context_id, (failure, guard_failure) in expected_context_policies.items():
        row = context_by_id.get(context_id, {})
        require(row.get("policy_state") == "CURRENT", f"CONTEXT_CURRENT:{context_id}")
        require(row.get("pattern_failure_disposition") == failure, f"CONTEXT_FAILURE:{context_id}")
        require(row.get("guard_false_disposition") == guard_failure, f"CONTEXT_GUARD_FAILURE:{context_id}")
        require(row.get("product_execution") == "NOT_RUN", f"CONTEXT_PRODUCT_NOT_RUN:{context_id}")
    for row_id, identity in (
        ("HM-LR-TOP-016", "PATTERN_ATTEMPT"),
        ("HM-LR-TOP-008", "IF"),
        ("HM-LR-TOP-011", "LOOP"),
    ):
        matches = [row for row in hm.get("rows", []) if row.get("row_id") == row_id]
        require(len(matches) == 1, f"TOP_ROW_UNIQUE:{row_id}")
        row = matches[0] if matches else {}
        require(row.get("profile_gate") == "CURRENT", f"TOP_ROW_CURRENT:{row_id}")
        require(row.get("lowering_dispatch_key", {}).get("identity_id") == identity, f"TOP_ROW_IDENTITY:{row_id}")
        require(row.get("product_support") == "NOT_RUN", f"TOP_ROW_PRODUCT_NOT_RUN:{row_id}")

    dynamic = contract.get("dynamic_semantics", {})
    require(dynamic.get("subject_evaluation_count") == 1, "DYNAMIC_SUBJECT_ONCE")
    require(
        dynamic.get("structural_probe")
        == {"purity": "PURE", "consumption": "NONCONSUMING", "determinism": "DETERMINISTIC", "suspension": "NONE"},
        "DYNAMIC_PURE_NONCONSUMING_PROBE",
    )
    require(
        dynamic.get("probe_binders")
        == {"access": "READ_ONLY", "escape": "FORBIDDEN", "ownership_publication_count": 0},
        "DYNAMIC_PROBE_BINDERS",
    )
    require(
        dynamic.get("optional_guard")
        == {
            "required_result_type": "Bool",
            "purity": "PURE",
            "evaluation_count_on_structural_success": 1,
            "evaluation_count_on_structural_failure": 0,
        },
        "DYNAMIC_GUARD_AFTER_PROBE_ONCE",
    )
    require(
        dynamic.get("final_commit")
        == {
            "logical_commit_count_on_final_guarded_success": 1,
            "fallibility": "INFALLIBLE",
            "timing": "AFTER_STRUCTURAL_AND_OPTIONAL_GUARD_SUCCESS",
            "top_level_row_id": "HM-LR-TOP-016",
            "subpattern_binding_commit_interpretation": "COMPOSITIONAL_COMMIT_REQUIREMENT",
            "subpattern_executable_commit_count": 0,
            "multiple_executable_commit_allowed": False,
        },
        "DYNAMIC_SINGLE_COMPOSITIONAL_COMMIT",
    )
    require(
        dynamic.get("failure_or_false_guard")
        == {
            "binding_publication_count": 0,
            "move_publication_count": 0,
            "loan_publication_count": 0,
            "view_publication_count": 0,
            "authority_publication_count": 0,
            "context_dispositions": [
                "FALSE_BRANCH_OR_CONDITION_FALSE",
                "LOOP_EXIT",
                "CANDIDATE_SKIP_OR_DISCHARGE",
            ],
        },
        "DYNAMIC_ZERO_FAILURE_PUBLICATION",
    )
    phases = pl.get("profiles", {}).get("phase_profile", {}).get("ordered_phases", [])
    try:
        guard_index = phases.index("EVALUATE_SINGLE_PURE_BOOL_GUARD")
        commit_index = phases.index("INFALLIBLE_ATOMIC_GROUP_COMMIT")
    except ValueError:
        guard_index = commit_index = -1
    require(guard_index >= 0 and guard_index < commit_index, "PL_GUARD_BEFORE_COMMIT")
    require(pl.get("global_invariants", {}).get("false_guard_component_commit_count") == 0, "PL_FALSE_GUARD_ZERO_COMMIT")
    top016 = next((row for row in hm.get("rows", []) if row.get("row_id") == "HM-LR-TOP-016"), {})
    require(
        [item.get("operation_kind") for item in top016.get("operation_plan", [])]
        == ["PATTERN_PROBE", "BINDING_COMMIT"],
        "HM016_PROBE_THEN_SINGLE_COMMIT",
    )
    require(
        sum(item.get("operation_kind") == "BINDING_COMMIT" for item in top016.get("operation_plan", [])) == 1,
        "HM016_SINGLE_COMMIT",
    )

    require(
        contract.get("or_alias_semantics")
        == {
            "or_pattern": {
                "binder_interface_join": "EXACT_EQUAL_BINDER_INTERFACE",
                "selection": "FIRST_SOURCE_ORDERED_SUCCESSFUL_BRANCH",
                "backtracking_count": 0,
                "retry_count": 0,
            },
            "alias_pattern": {
                "identity": "SAME_SUBJECT_BORROW",
                "clone_count": 0,
                "probe_loan_publication_count": 0,
                "actual_loan_acquisition": "FINAL_TOP_LEVEL_COMMIT_ONLY",
            },
        },
        "OR_ALIAS_SEMANTICS_EXACT",
    )
    require(
        contract.get("ownership_diagnostic_delegation")
        == {
            "delegate_feature_id": "pattern_match_ownership_split",
            "delegated_conditions": [
                "ALIAS_WITH_MOVED_DESCENDANT",
                "ALIAS_WITH_EXCLUSIVELY_BORROWED_DESCENDANT",
                "CROSS_BRANCH_PLACE_STATE_MISMATCH",
                "REST_VIEW_ESCAPE",
            ],
            "delegate_static_semantics_transition_count": 0,
            "delegate_dynamic_lowering_transition_count": 0,
        },
        "OWNERSHIP_DELEGATION_NO_TRANSITION",
    )

    rules = contract.get("rules", [])
    require([row.get("rule_id") for row in rules] == [f"PDLTC-R{index:03d}" for index in range(1, 14)], "RULE_IDS_EXACT_13")
    require(all(isinstance(row.get("text"), str) and row.get("text") for row in rules), "RULE_TEXT_PRESENT")
    cases = contract.get("acceptance_cases", [])
    case_by_id = {row.get("case_id"): row for row in cases}
    require(len(cases) == 12 and len(case_by_id) == 12, "ACCEPTANCE_EXACT_UNIQUE_12")
    require([row.get("case_id") for row in cases] == [f"PDLTC-AC-{index:03d}" for index in range(1, 13)], "ACCEPTANCE_IDS_EXACT")
    require([row.get("audit_case_id") for row in cases] == ["OA1", "OA2", "OA3", "OA4", "PC1", "PC2", "PC3", "PC4", "PC5", "PD1", "PD2", "PD3"], "AUDIT_CASE_IDS_EXACT")
    require(Counter(row.get("class") for row in cases) == Counter({"BOUNDARY": 6, "POSITIVE": 3, "REJECT": 3}), "ACCEPTANCE_CLASS_COUNTS")
    require(all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in cases), "ACCEPTANCE_NOT_RUN")
    require(contract.get("acceptance_bindings") == EXPECTED_ACCEPTANCE_BINDINGS, "ACCEPTANCE_BINDINGS_EXACT")
    for feature, outcomes in EXPECTED_ACCEPTANCE_BINDINGS.items():
        for outcome, case_ids in outcomes.items():
            require(
                all(case_by_id.get(case_id, {}).get("feature_id") == feature and case_by_id.get(case_id, {}).get("class") == outcome for case_id in case_ids),
                f"ACCEPTANCE_BINDING_CLASS:{feature}:{outcome}",
            )
    for case_id, expected in (
        ("PDLTC-AC-007", {"context_id": "PCTX-FOR-LET", "candidate_discharge_count": 1, "logical_commit_count": 0}),
        ("PDLTC-AC-008", {"context_id": "PCTX-PATTERN-CONDITION-CHAIN", "guard_evaluation_count": 1, "logical_commit_count": 0, "publication_count": 0}),
        ("PDLTC-AC-010", {"subject_evaluation_count": 1, "projection_order": "LEFT_TO_RIGHT", "logical_commit_count": 1, "move_commit_count": 1, "subpattern_executable_commit_count": 0}),
        ("PDLTC-AC-011", {"binding_publication_count": 0, "move_publication_count": 0, "loan_publication_count": 0, "view_publication_count": 0, "authority_publication_count": 0}),
    ):
        require(case_by_id.get(case_id, {}).get("assertions") == expected, f"ACCEPTANCE_ASSERTIONS:{case_id}")

    entries = overlay.get("evidence_entries", [])
    entry_by_key = {row.get("evidence_key"): row for row in entries}
    require(len(entries) == 3 and len(entry_by_key) == 3, "EVIDENCE_EXACT_UNIQUE_3")
    for feature, locator in EXPECTED_LOCATORS.items():
        key = f"R59:{feature}:DYNAMIC_LOWERING:STRUCTURAL"
        item = entry_by_key.get(key, {})
        require(item.get("class") == "CONTRACT_RULE_ID", f"EVIDENCE_CLASS:{feature}")
        require(item.get("path") == CONTRACT_REL, f"EVIDENCE_PATH:{feature}")
        require(item.get("locator_kind") == "REGISTRY_ID", f"EVIDENCE_LOCATOR_KIND:{feature}")
        require(item.get("locator") == locator and contains_scalar(contract, locator), f"EVIDENCE_LOCATOR_RULE:{feature}")
        require(item.get("stage_role") == "DYNAMIC_LOWERING", f"EVIDENCE_STAGE_ROLE:{feature}")

    bindings = overlay.get("bindings", [])
    binding_by_cell = {
        (row.get("feature_id"), row.get("stage"), row.get("outcome")): row
        for row in bindings
    }
    require(len(bindings) == 3 and len(binding_by_cell) == 3 and set(binding_by_cell) == TARGET_CELLS, "OVERLAY_CELLS_EXACT_3")
    for cell in TARGET_CELLS:
        item = binding_by_cell.get(cell, {})
        key = f"R59:{cell[0]}:DYNAMIC_LOWERING:STRUCTURAL"
        require(item.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP", f"OVERLAY_PREDECESSOR:{cell[0]}")
        require(item.get("disposition") == "BOUND_DIRECT", f"OVERLAY_DISPOSITION:{cell[0]}")
        require(item.get("evidence_keys") == [key], f"OVERLAY_EVIDENCE:{cell[0]}")
        require(item.get("delegate_feature_id") is None and item.get("not_applicable") is None, f"OVERLAY_DIRECT_SHAPE:{cell[0]}")

    overlay_cases = overlay.get("acceptance_cases", [])
    require(len(overlay_cases) == 12, "OVERLAY_ACCEPTANCE_EXACT_12")
    for index, item in enumerate(overlay_cases):
        contract_case = cases[index] if index < len(cases) else {}
        pointer = f"/acceptance_cases/{index}"
        require(item.get("contract_pointer") == pointer, f"OVERLAY_CASE_POINTER:{index}")
        try:
            resolved = resolve_pointer(contract, pointer)
        except (KeyError, IndexError, TypeError, ValueError):
            resolved = {}
        require(resolved == contract_case, f"OVERLAY_CASE_POINTER_RESOLVES:{index}")
        require(
            (item.get("case_id"), item.get("audit_case_id"), item.get("feature_id"), item.get("class"))
            == (contract_case.get("case_id"), contract_case.get("audit_case_id"), contract_case.get("feature_id"), contract_case.get("class")),
            f"OVERLAY_CASE_BINDING:{index}",
        )
        require(item.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"OVERLAY_CASE_NOT_RUN:{index}")

    expected_counts = {
        "feature_count": 3,
        "evidence_entry_count": 3,
        "binding_count": 3,
        "acceptance_case_count": 12,
        "acceptance_stage_transition_count": 0,
        "predecessor_blocked_cell_count": 3,
        "overlay_bound_direct_transition_count": 3,
        "overlay_bound_delegated_transition_count": 0,
        "overlay_not_applicable_transition_count": 0,
        "predecessor_cumulative_overlay_binding_count": 110,
        "post_overlay_cumulative_binding_count": 113,
        "predecessor_total_bound_direct_cell_count": 2447,
        "predecessor_total_bound_delegated_cell_count": 3,
        "predecessor_total_not_applicable_cell_count": 502,
        "predecessor_total_blocked_cell_count": 1269,
        "post_overlay_total_bound_direct_cell_count": 2450,
        "post_overlay_total_bound_delegated_cell_count": 3,
        "post_overlay_total_not_applicable_cell_count": 502,
        "post_overlay_total_blocked_cell_count": 1266,
        "post_overlay_missing_cell_count": 0,
        "post_overlay_conflict_cell_count": 0,
    }
    require(overlay.get("counts") == expected_counts, "OVERLAY_COUNTS_EXACT")

    trace_rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    authoritative_rows = load(root / TRACE_REL)
    trace, duplicate_count = trace_cells(trace_rows)
    authoritative, authoritative_duplicates = trace_cells(authoritative_rows)
    require(len(trace_rows) == 469 and len({row.get("feature_id") for row in trace_rows}) == 469, "TRACE_FEATURES_EXACT_469")
    require(len(trace) == 4221 and duplicate_count == 0, "TRACE_CELLS_EXACT_UNIQUE_4221")
    require(len(authoritative) == 4221 and authoritative_duplicates == 0, "AUTHORITATIVE_TRACE_CELLS")
    for cell, value in trace.items():
        if cell not in TARGET_CELLS:
            require(value == authoritative.get(cell), f"NON_TARGET_TRACE_CELL_UNCHANGED:{cell}")
    raw_dispositions = {cell: value.get("disposition") for cell, value in trace.items()}
    prior_binding_count = 0
    for relative in PRIOR_OVERLAYS:
        prior = load(root / relative)
        prior_binding_count += len(prior.get("bindings", []))
    require(prior_binding_count == 110, "PREDECESSOR_OVERLAY_BINDINGS_EXACT_110")
    installed_counts = disposition_counts(raw_dispositions)
    require(
        installed_counts in {
            (2450, 3, 502, 1266),  # R59 post-state
            (2452, 3, 502, 1264),  # R60 post-state
            (2457, 3, 502, 1259),  # R61 post-state
        },
        "INSTALLED_POST_COUNTS_EXACT",
    )
    pre = dict(raw_dispositions)
    for item in overlay.get("bindings", []):
        cell = (item.get("feature_id"), item.get("stage"), item.get("outcome"))
        require(
            raw_dispositions.get(cell) == item.get("disposition"),
            f"TRACE_TARGET_INSTALLED:{cell[0]}",
        )
        pre[cell] = item.get("predecessor_disposition")
    pre_counts = disposition_counts(pre)
    require(
        pre_counts
        == (installed_counts[0] - len(TARGET_CELLS), installed_counts[1], installed_counts[2], installed_counts[3] + len(TARGET_CELLS)),
        "PREDECESSOR_COUNTS_EXACT",
    )
    ownership_static = ("pattern_match_ownership_split", "STATIC_SEMANTICS", None)
    ownership_dynamic = ("pattern_match_ownership_split", "DYNAMIC_LOWERING", None)
    require(pre.get(ownership_static) == raw_dispositions.get(ownership_static), "OWNERSHIP_SPLIT_STATIC_UNCHANGED_BLOCKED")
    require(pre.get(ownership_dynamic) == raw_dispositions.get(ownership_dynamic), "OWNERSHIP_SPLIT_DYNAMIC_UNCHANGED_BLOCKED")
    post = dict(pre)
    for item in overlay.get("bindings", []):
        cell = (item.get("feature_id"), item.get("stage"), item.get("outcome"))
        require(pre.get(cell) == "APPLICABLE_BLOCKED_BY_GAP", f"TRACE_TARGET_PREDECESSOR:{cell[0]}")
        post[cell] = item.get("disposition")
    changed = {cell for cell in pre if pre[cell] != post[cell]}
    require(changed == TARGET_CELLS, "TRACE_ONLY_EXACT_TARGET_CELLS_CHANGED")
    require(all(pre[cell] == post[cell] for cell in pre if cell not in TARGET_CELLS), "TRACE_ALL_NON_TARGET_CELLS_UNCHANGED")
    require(post == raw_dispositions, "TRACE_INSTALLED_POST_EXACT")
    require(post.get(ownership_static) == pre.get(ownership_static) and post.get(ownership_dynamic) == pre.get(ownership_dynamic), "OWNERSHIP_SPLIT_ZERO_TRANSITIONS")
    require(disposition_counts(post) == installed_counts, "POST_COUNTS_EXACT")

    machine = contract.get("machine_acceptance", {})
    machine_expected = {
        "feature_count": 3,
        "rule_count": 13,
        "acceptance_case_count": 12,
        "positive_case_count": 3,
        "boundary_case_count": 6,
        "reject_case_count": 3,
        "current_pattern_mapping_count": 29,
        "current_context_count": 5,
        "overlay_binding_count": 3,
        "predecessor_blocked_cell_count": 3,
        "overlay_bound_direct_transition_count": 3,
        "overlay_bound_delegated_transition_count": 0,
        "overlay_not_applicable_transition_count": 0,
        "predecessor_cumulative_overlay_binding_count": 110,
        "post_overlay_cumulative_binding_count": 113,
        "predecessor_total_bound_direct_cell_count": 2447,
        "predecessor_total_bound_delegated_cell_count": 3,
        "predecessor_total_not_applicable_cell_count": 502,
        "predecessor_total_blocked_cell_count": 1269,
        "post_overlay_total_bound_direct_cell_count": 2450,
        "post_overlay_total_bound_delegated_cell_count": 3,
        "post_overlay_total_not_applicable_cell_count": 502,
        "post_overlay_total_blocked_cell_count": 1266,
        "post_overlay_missing_cell_count": 0,
        "post_overlay_conflict_cell_count": 0,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }
    require(machine == machine_expected, "MACHINE_ACCEPTANCE_EXACT")
    authority = contract.get("authority_fence", {})
    guards = overlay.get("guards", {})
    require(
        authority
        == {
            "new_source_surface_count": 0,
            "new_ast_identity_count": 0,
            "new_hir_identity_count": 0,
            "new_mir_operation_kind_count": 0,
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
            "evidence_level": "E2_STRUCTURED_STATIC",
        },
        "AUTHORITY_FENCE_EXACT",
    )
    require(
        guards
        == {
            "target_feature_count": 469,
            "target_feature_id_list_sha256": "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435",
            "excluded_feature_count": 254,
            "excluded_feature_id_list_sha256": "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7",
            "transitioned_cell_count": 3,
            "ownership_split_transition_count": 0,
            "reverse_dependent_transition_count": 0,
            "preview_transition_count": 0,
            "other_cell_transition_count": 0,
            "source_activation": "none",
            "surface_change_count": 0,
            "ast_identity_change_count": 0,
            "hir_identity_change_count": 0,
            "mir_operation_kind_change_count": 0,
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
            "product_execution_receipt_count": 0,
            "implementation_claim": "NONE",
        },
        "GUARDS_EXACT",
    )
    for value, prefix in ((authority, "AUTHORITY"), (guards, "GUARDS"), (machine, "MACHINE")):
        require(value.get("feature_p1") == "22_OPEN_UNCHANGED", f"{prefix}_P1")
        require(value.get("m13_actions") == "4_OPEN_UNCHANGED", f"{prefix}_M13")
        require(value.get("product_lanes") == "15_OF_15_NOT_RUN", f"{prefix}_PRODUCT_LANES")
        require(value.get("github_publication") == "SUSPENDED", f"{prefix}_GITHUB")
    require(guards.get("implementation_claim") == "NONE", "GUARDS_NO_IMPLEMENTATION_CLAIM")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    overlay = load(root / OVERLAY_REL)
    contract = load(root / CONTRACT_REL)
    errors = validate(root, overlay, contract)
    print(
        json.dumps(
            {
                "schema": "deeplus.pattern-dynamic-lowering-trace-validation-receipt/r1",
                "result": "PASS" if not errors else "FAIL",
                "feature_count": len(overlay.get("feature_ids", [])),
                "binding_count": len(overlay.get("bindings", [])),
                "current_pattern_mapping_count": contract.get("current_registry_alignment", {}).get("current_mapping_count"),
                "current_context_count": len(contract.get("context_lowering_alignment", {}).get("contexts", [])),
                "projected_counts": {
                    "bound_direct": 2450,
                    "bound_delegated": 3,
                    "not_applicable": 502,
                    "applicable_blocked": 1266,
                    "missing": 0,
                    "conflict": 0,
                },
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
