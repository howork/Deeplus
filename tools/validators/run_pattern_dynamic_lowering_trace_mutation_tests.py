#!/usr/bin/env python3
"""Run bounded in-memory mutations against the R59 focused validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_pattern_dynamic_lowering_trace import (
    CONTEXT_REL,
    CONTRACT_REL,
    HM_REL,
    OVERLAY_REL,
    PK_REL,
    PL_REL,
    TRACE_REL,
    load,
    validate,
)


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[
    str,
    Callable[
        [
            dict[str, Any],
            dict[str, Any],
            list[dict[str, Any]],
            dict[str, Any],
            dict[str, Any],
            dict[str, Any],
            dict[str, Any],
        ],
        None,
    ],
]


def find_trace_cell(
    rows: list[dict[str, Any]], feature_id: str, stage_name: str
) -> dict[str, Any]:
    row = next(item for item in rows if item["feature_id"] == feature_id)
    return next(item for item in row["stages"] if item["stage"] == stage_name)


def swap_or_alias(
    overlay: dict[str, Any],
    contract: dict[str, Any],
    trace: list[dict[str, Any]],
    pl: dict[str, Any],
    pk: dict[str, Any],
    hm: dict[str, Any],
    contexts: dict[str, Any],
) -> None:
    or_row = next(row for row in pl["rows"] if row["lowering_id"] == "PL-OR")
    alias_row = next(row for row in pl["rows"] if row["lowering_id"] == "PL-ALIAS")
    or_row["pattern_kind_id"], alias_row["pattern_kind_id"] = (
        alias_row["pattern_kind_id"],
        or_row["pattern_kind_id"],
    )


def transition_excluded_row(
    overlay: dict[str, Any],
    contract: dict[str, Any],
    trace: list[dict[str, Any]],
    pl: dict[str, Any],
    pk: dict[str, Any],
    hm: dict[str, Any],
    contexts: dict[str, Any],
) -> None:
    cell = find_trace_cell(trace, "pattern_match_ownership_split", "DYNAMIC_LOWERING")
    mutated_disposition = (
        "APPLICABLE_BLOCKED_BY_GAP"
        if cell.get("disposition") == "BOUND_DIRECT"
        else "BOUND_DIRECT"
    )
    cell.update(
        {
            "disposition": mutated_disposition,
            "blocked_gap_ids": ["IR-XCUT-P1-054"] if mutated_disposition == "APPLICABLE_BLOCKED_BY_GAP" else [],
            "not_applicable": None,
        }
    )


def main() -> int:
    overlay = load(ROOT / OVERLAY_REL)
    contract = load(ROOT / CONTRACT_REL)
    trace = load(ROOT / TRACE_REL)
    pl = load(ROOT / PL_REL)
    pk = load(ROOT / PK_REL)
    hm = load(ROOT / HM_REL)
    contexts = load(ROOT / CONTEXT_REL)

    normal_errors = validate(ROOT, overlay, contract, validate_schema=True)
    if normal_errors:
        print(
            json.dumps(
                {"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors},
                indent=2,
            )
        )
        return 1

    mutations: list[Mutation] = [
        ("MISSING_FEATURE", lambda o, c, t, pl, pk, hm, cx: o["feature_ids"].pop()),
        ("EXTRA_FEATURE", lambda o, c, t, pl, pk, hm, cx: o["feature_ids"].append("pattern_match_ownership_split")),
        ("MISSING_EVIDENCE", lambda o, c, t, pl, pk, hm, cx: o["evidence_entries"].pop()),
        ("EXTRA_EVIDENCE", lambda o, c, t, pl, pk, hm, cx: o["evidence_entries"].append(copy.deepcopy(o["evidence_entries"][0]))),
        ("MISSING_BINDING", lambda o, c, t, pl, pk, hm, cx: o["bindings"].pop()),
        ("EXTRA_BINDING", lambda o, c, t, pl, pk, hm, cx: o["bindings"].append(copy.deepcopy(o["bindings"][0]))),
        ("WRONG_CELL", lambda o, c, t, pl, pk, hm, cx: o["bindings"][0].__setitem__("stage", "STATIC_SEMANTICS")),
        ("WRONG_DISPOSITION", lambda o, c, t, pl, pk, hm, cx: o["bindings"][0].__setitem__("disposition", "BOUND_DELEGATED")),
        ("LOCATOR_DRIFT", lambda o, c, t, pl, pk, hm, cx: o["evidence_entries"][0].__setitem__("locator", "PDLTC-R013")),
        ("RULE_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["rules"][8].__setitem__("rule_id", "PDLTC-R099")),
        ("CASE_BINDING_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["acceptance_cases"][0].__setitem__("feature_id", "pattern_decomposition")),
        ("CASE_POINTER_DRIFT", lambda o, c, t, pl, pk, hm, cx: o["acceptance_cases"][0].__setitem__("contract_pointer", "/acceptance_cases/1")),
        ("SCHEMA_BINDING_DRIFT", lambda o, c, t, pl, pk, hm, cx: o.__setitem__("schema", "deeplus.pattern-dynamic-lowering-evidence/r2")),
        ("CURRENT_29_ROW_OMISSION", lambda o, c, t, pl, pk, hm, cx: pl["rows"].pop(0)),
        ("CURRENT_BIJECTION_DRIFT", lambda o, c, t, pl, pk, hm, cx: next(row for row in pl["rows"] if row["lowering_id"] == "PL-BINDER").__setitem__("pattern_kind_id", "PK-ALIAS")),
        ("OR_ALIAS_SWAP", swap_or_alias),
        ("CURRENT_PROFILE_DRIFT", lambda o, c, t, pl, pk, hm, cx: next(row for row in hm["rows"] if row["row_id"] == "HM-LR-PAT-027").__setitem__("profile_gate", "PREVIEW")),
        ("CONTEXT_MAPPING_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["context_lowering_alignment"]["contexts"][0]["hir_mir_row_ids"].__setitem__(1, "HM-LR-TOP-011")),
        ("TOP_ROW_IDENTITY_DRIFT", lambda o, c, t, pl, pk, hm, cx: next(row for row in hm["rows"] if row["row_id"] == "HM-LR-TOP-008")["lowering_dispatch_key"].__setitem__("identity_id", "LOOP")),
        ("GUARD_ORDER_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["dynamic_semantics"]["optional_guard"].__setitem__("evaluation_count_on_structural_failure", 1)),
        ("SINGLE_COMMIT_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["dynamic_semantics"]["final_commit"].__setitem__("logical_commit_count_on_final_guarded_success", 2)),
        ("NESTED_COMMIT_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["dynamic_semantics"]["final_commit"].__setitem__("subpattern_executable_commit_count", 1)),
        ("FAILURE_PUBLICATION_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["dynamic_semantics"]["failure_or_false_guard"].__setitem__("binding_publication_count", 1)),
        ("FOR_LET_SKIP_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["context_lowering_alignment"]["contexts"][4].__setitem__("failure_disposition", "LOOP_EXIT")),
        ("FOR_LET_DISCHARGE_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["acceptance_cases"][6]["assertions"].__setitem__("candidate_discharge_count", 0)),
        ("EXCLUDED_ROW_TRANSITION", transition_excluded_row),
        ("PRODUCT_EXECUTION_OVERCLAIM", lambda o, c, t, pl, pk, hm, cx: c["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
        ("P1_DRIFT", lambda o, c, t, pl, pk, hm, cx: c["authority_fence"].__setitem__("feature_p1", "21_OPEN")),
        ("M13_DRIFT", lambda o, c, t, pl, pk, hm, cx: o["guards"].__setitem__("m13_actions", "3_OPEN")),
        ("PRODUCT_LANE_OVERCLAIM", lambda o, c, t, pl, pk, hm, cx: c["machine_acceptance"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_OVERCLAIM", lambda o, c, t, pl, pk, hm, cx: o["guards"].__setitem__("github_publication", "ENABLED")),
        ("IMPLEMENTATION_OVERCLAIM", lambda o, c, t, pl, pk, hm, cx: o["guards"].__setitem__("implementation_claim", "COMPLETE")),
    ]

    results = []
    for mutation_id, mutate in mutations:
        candidate_overlay = copy.deepcopy(overlay)
        candidate_contract = copy.deepcopy(contract)
        candidate_trace = copy.deepcopy(trace)
        candidate_pl = copy.deepcopy(pl)
        candidate_pk = copy.deepcopy(pk)
        candidate_hm = copy.deepcopy(hm)
        candidate_contexts = copy.deepcopy(contexts)
        mutate(
            candidate_overlay,
            candidate_contract,
            candidate_trace,
            candidate_pl,
            candidate_pk,
            candidate_hm,
            candidate_contexts,
        )
        errors = validate(
            ROOT,
            candidate_overlay,
            candidate_contract,
            validate_schema=False,
            trace_rows_override=candidate_trace,
            pattern_lowering_override=candidate_pl,
            pattern_kinds_override=candidate_pk,
            hm_registry_override=candidate_hm,
            context_registry_override=candidate_contexts,
        )
        results.append(
            {
                "mutation_id": mutation_id,
                "rejected": bool(errors),
                "first_error": errors[0] if errors else None,
            }
        )

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == len(results)
    print(
        json.dumps(
            {
                "schema": "deeplus.pattern-dynamic-lowering-trace-mutation-receipt/r1",
                "result": "PASS" if passed else "FAIL",
                "normal_path": "PASS",
                "mutation_count": len(results),
                "rejected_count": rejected,
                "results": results,
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
