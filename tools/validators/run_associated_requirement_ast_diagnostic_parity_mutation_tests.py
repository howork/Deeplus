#!/usr/bin/env python3
"""Run exactly 14 in-memory mutations against the focused R65 validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

import validate_associated_requirement_ast_diagnostic_parity as focused


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def target_cell(rows: list[dict[str, Any]], stage: str) -> dict[str, Any]:
    feature = next(row for row in rows if row["feature_id"] == focused.FEATURE)
    return next(row for row in feature["stages"] if row["stage"] == stage)


def unrelated_cell_drift(bundle: dict[str, Any]) -> None:
    feature = next(
        row for row in bundle["rows"]
        if row["feature_id"] == "accessor_property_colon_equals_surface"
    )
    cell = next(row for row in feature["stages"] if row["stage"] == "STATIC_SEMANTICS")
    cell["disposition"] = (
        "BOUND_DIRECT"
        if cell.get("disposition") != "BOUND_DIRECT"
        else "APPLICABLE_BLOCKED_BY_GAP"
    )


def identity_baseline_drift(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["canonical_baseline_commit"] = "0" * 40
    bundle["overlay"]["local_predecessor_commit"] = "1" * 40


def overlay_scope_drift(bundle: dict[str, Any]) -> None:
    bundle["overlay"]["feature_ids"].append("trait_witness_coherence_phase_a")
    bundle["overlay"]["bindings"][0]["feature_id"] = "trait_witness_coherence_phase_a"


def ast_evidence_locator_drift(bundle: dict[str, Any]) -> None:
    entry = next(
        item for item in bundle["overlay"]["evidence_entries"]
        if item["stage_role"] == "AST_FRONTEND"
    )
    entry["locator"] = "/production_rows/251"


def diagnostic_evidence_locator_drift(bundle: dict[str, Any]) -> None:
    entry = next(
        item for item in bundle["overlay"]["evidence_entries"]
        if item["stage_role"] == "DIAGNOSTICS"
    )
    entry["locator"] = "ARPTC-R005"


def declaration_ast_owner_drift(bundle: dict[str, Any]) -> None:
    row = bundle["grammar"]["production_rows"][237]
    row["ast_target"] = "AST/AssociatedRequirementBinding"
    row["ast_output_cardinality"] = "ZERO"


def binding_cst_child_fence_drift(bundle: dict[str, Any]) -> None:
    row = bundle["grammar"]["production_rows"][251]
    row["disposition"] = "ast_node"
    row["ast_target"] = "AST/AssociatedRequirementBinding"
    row["ast_output_cardinality"] = "EXACTLY_ONE"


def diagnostic_active_id_drift(bundle: dict[str, Any]) -> None:
    row = bundle["diagnostic_catalog"][39]
    row["diagnostic_id"] = "ASSOCIATED_REQUIREMENT_AMBIGUOUS"
    row["diagnostic_status"] = "inactive"


def primary_relation_drift(bundle: dict[str, Any]) -> None:
    row = bundle["relations"][8]
    row["relation"] = "secondary"
    row["diagnostic_id"] = "TRAIT_MISSING_WITNESS"


def r64_primary_rule_drift(bundle: dict[str, Any]) -> None:
    rule = next(row for row in bundle["r64"]["rules"] if row["rule_id"] == "ARPTC-R006")
    rule["text"] = "A rejection may emit multiple diagnostics and evaluate later candidates."


def transition_or_residue_drift(bundle: dict[str, Any]) -> None:
    target_cell(bundle["predecessor_rows"], "AST_FRONTEND")["disposition"] = "BOUND_DIRECT"
    target_cell(bundle["rows"], "DIAGNOSTICS")["delegate_feature_id"] = "trait_witness_coherence_phase_a"
    bundle["overlay"]["bindings"][0]["not_applicable"] = {
        "reason_code": "NA_AST_NO_PROGRAMMER_VISIBLE_FORM"
    }


def aggregate_count_evidence_drift(bundle: dict[str, Any]) -> None:
    metadata = bundle["metadata"]
    metadata["derived_counts"]["bound_direct_cells"] = 2462
    metadata["applied_evidence_overlays"].pop()
    metadata["evidence_registry"].pop()


def target_generated_row_drift(bundle: dict[str, Any]) -> None:
    cell = target_cell(bundle["rows"], "AST_FRONTEND")
    cell["disposition"] = "NOT_APPLICABLE"
    cell["not_applicable"] = {
        "reason_code": "NA_AST_NO_PROGRAMMER_VISIBLE_FORM",
        "authority_boundary": "FRONTEND_AUTHORITY",
        "justification_evidence_refs": [],
        "rationale": "mutated",
    }


def governance_product_decision_drift(bundle: dict[str, Any]) -> None:
    guards = bundle["overlay"]["guards"]
    guards["semantic_p0"] = 1
    guards["feature_p1"] = "21_OPEN"
    guards["m13_actions"] = "3_OPEN"
    guards["product_lanes"] = "15_OF_15_PASS"
    guards["github_publication"] = "ENABLED"
    bundle["rows"][0]["product_execution"] = "PASS"
    bundle["decision_text"] = bundle["decision_text"].replace(
        "IR-TRACE-P1-056", "IR-TRACE-P1-REMOVED"
    )


def validation_receipt(bundle: dict[str, Any], *, validate_schema: bool) -> dict[str, Any]:
    return focused.validate(
        ROOT,
        bundle["overlay"],
        validate_schema=validate_schema,
        grammar_registry_override=bundle["grammar"],
        diagnostic_catalog_override=bundle["diagnostic_catalog"],
        relation_override=bundle["relations"],
        r64_contract_override=bundle["r64"],
        rows_override=bundle["rows"],
        metadata_override=bundle["metadata"],
        predecessor_rows_override=bundle["predecessor_rows"],
        decision_text_override=bundle["decision_text"],
    )


def main() -> int:
    base = {
        "overlay": focused.load(ROOT / focused.OVERLAY_REL),
        "grammar": focused.load(ROOT / focused.GRAMMAR_REGISTRY_REL),
        "diagnostic_catalog": focused.load(ROOT / focused.DIAGNOSTIC_CATALOG_REL),
        "relations": focused.load(ROOT / focused.DIAGNOSTIC_RELATION_REL),
        "r64": focused.load(ROOT / focused.R64_CONTRACT_REL),
        "rows": focused.load(ROOT / focused.ROWS_REL),
        "metadata": focused.load(ROOT / focused.METADATA_REL),
        "predecessor_rows": focused.predecessor_rows(ROOT),
        "decision_text": (ROOT / focused.DECISION_REL).read_text(encoding="utf-8"),
    }

    normal = validation_receipt(base, validate_schema=True)
    if normal["result"] != "PASS":
        print(json.dumps({
            "result": "FAIL",
            "phase": "NORMAL_PATH",
            "errors": normal["errors"],
        }, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("IDENTITY_OR_BASELINE", identity_baseline_drift),
        ("OVERLAY_SCOPE", overlay_scope_drift),
        ("AST_EVIDENCE_LOCATOR", ast_evidence_locator_drift),
        ("DIAGNOSTIC_EVIDENCE_LOCATOR", diagnostic_evidence_locator_drift),
        ("DECLARATION_AST_OWNER", declaration_ast_owner_drift),
        ("BINDING_CST_ONLY_OR_NO_CHILD_FENCE", binding_cst_child_fence_drift),
        ("DIAGNOSTIC_ROW_ACTIVE_OR_ID", diagnostic_active_id_drift),
        ("PRIMARY_RELATION", primary_relation_drift),
        ("R64_ARPTC_R006", r64_primary_rule_drift),
        ("PREDECESSOR_POST_TRANSITION_OR_RESIDUE", transition_or_residue_drift),
        ("AGGREGATE_OVERLAY_COUNT_OR_EVIDENCE", aggregate_count_evidence_drift),
        ("TARGET_GENERATED_ROW", target_generated_row_drift),
        ("UNRELATED_CELL", unrelated_cell_drift),
        ("GOVERNANCE_PRODUCT_GITHUB_OR_DECISION", governance_product_decision_drift),
    ]
    if len(mutations) != 14:
        raise AssertionError(f"R65_MUTATION_COUNT:{len(mutations)}")

    results = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        receipt = validation_receipt(candidate, validate_schema=False)
        results.append({
            "mutation_id": mutation_id,
            "rejected": receipt["result"] == "FAIL" and bool(receipt["errors"]),
            "first_error": receipt["errors"][0] if receipt["errors"] else None,
        })

    rejected = sum(item["rejected"] for item in results)
    passed = rejected == 14
    print(json.dumps({
        "schema": "deeplus.associated-requirement-ast-diagnostic-parity-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": 14,
        "rejected_count": rejected,
        "results": results,
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
