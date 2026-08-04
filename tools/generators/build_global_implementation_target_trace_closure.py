#!/usr/bin/env python3
"""Build the R76 global implementation-target trace closure evidence.

This generator does not claim product execution.  It closes the design/static
handoff locator gap by giving every predecessor blocked cell an exact contract
row.  Existing example-corpus cases are reused when present; otherwise the
cell records a model-level acceptance obligation against the immutable feature
row, its authority/dependency fence, and the canonical frontend/HIR-MIR
contracts.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TRACE_ROOT = ROOT / "spec/traceability/implementation-target-profile-r1"
ROWS = TRACE_ROOT / "rows.json"
CONTRACT = ROOT / "spec/contracts/implementation-target-global-trace-closure-r1.json"
OVERLAY = TRACE_ROOT / "global-trace-closure-evidence-r1.json"
BASELINE = "40a826af29410af1a14c6a7dec3193cd59ba9b12"

AST_ZERO_RESIDUE = {
    "bare_parenless_ordinary_call_not_current",
    "legacy_logical_and_or_operator_removed",
    "old_dotted_bitwise_operator_removed",
    "optional_callable_invocation_not_current_law",
    "optional_chaining_not_current_law",
    "standalone_bang_not_current_not_word_law",
}

ZERO_DYNAMIC_TOKENS = (
    "not current",
    "removed",
    "forbidden",
    "excluded",
    "no admitted ast",
    "no admitted hir",
    "no admitted mir",
    "zero runtime",
    "no runtime",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def feature_catalog() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    rows: dict[str, dict[str, Any]] = {}
    locations: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "spec/features/catalog/chunks").glob("part-*.json")):
        rel = path.relative_to(ROOT).as_posix()
        for index, row in enumerate(read_json(path)):
            feature_id = row["feature_id"]
            rows[feature_id] = row
            locations[feature_id] = {"path": rel, "json_pointer": f"/{index}"}
    return rows, locations


def corpus_index() -> dict[str, dict[str, list[str]]]:
    text = (ROOT / "examples/guide/review-corpus.md").read_text(encoding="utf-8")
    result: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: {"accept": [], "accept_with_gate": [], "reject": []}
    )
    quote = "`"
    for section in text.split("\n## ")[1:]:
        lines = section.splitlines()
        example_id = lines[0].split()[0]
        if not example_id.startswith("EX-"):
            continue
        feature_line = next((line for line in lines if "source_feature_ids:" in line), None)
        outcome_line = next((line for line in lines if "expected_outcome:" in line), None)
        if feature_line is None or outcome_line is None:
            continue
        feature_ids = feature_line.split(quote)[1::2]
        values = outcome_line.split(quote)[1::2]
        outcome = values[0] if values else outcome_line.split(":", 1)[1].replace("*", "").strip()
        if outcome not in {"accept", "accept_with_gate", "reject"}:
            continue
        for feature_id in feature_ids:
            if feature_id != "none":
                result[feature_id][outcome].append(example_id)
    return result


def blocked_cells(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in rows:
        for stage in row["stages"]:
            for cell in stage.get("outcomes", [stage]):
                if cell.get("disposition") != "APPLICABLE_BLOCKED_BY_GAP":
                    continue
                result.append(
                    {
                        "feature_id": row["feature_id"],
                        "stage": stage["stage"],
                        "outcome": cell.get("outcome"),
                        "predecessor_disposition": cell["disposition"],
                        "predecessor_gap_ids": cell["blocked_gap_ids"],
                    }
                )
    return result


def test_obligation(
    feature_id: str,
    outcome: str,
    examples: dict[str, list[str]],
    row: dict[str, Any],
) -> dict[str, Any]:
    accepted = sorted(set(examples["accept"] + examples["accept_with_gate"]))
    rejected = sorted(set(examples["reject"]))
    common = {
        "execution_state": "DESIGN_STATIC_SPECIFIED_PRODUCT_NOT_RUN",
        "feature_row_contract": "EXACT_NOT_WIDENED",
        "authority_set": row.get("authority_set", [row.get("authority")]),
        "dependency_ids": row.get("depends_on", []),
        "source_activation": row.get("source_activation", "none"),
    }
    if outcome == "POSITIVE":
        return {
            **common,
            "case_kind": "EXISTING_ADMITTED_CORPUS" if accepted else "CANONICAL_CONTRACT_MODEL",
            "example_ids": accepted,
            "expected": "ADMIT_EXACT_CANONICAL_FEATURE_CONTRACT",
            "oracle": "feature row notes, existing predicates/diagnostics, and canonical authority agree",
        }
    if outcome == "BOUNDARY":
        if accepted and rejected:
            kind = "EXACT_ACCEPT_REJECT_PARTITION"
        elif len(accepted) > 1:
            kind = "MULTIPLE_ADMITTED_SHAPES_FENCE"
        else:
            kind = "AUTHORITY_DEPENDENCY_AND_ACTIVATION_FENCE"
        return {
            **common,
            "case_kind": kind,
            "admitted_example_ids": accepted,
            "rejected_example_ids": rejected,
            "expected": "PRESERVE_EXACT_FEATURE_AUTHORITY_DEPENDENCY_AND_SOURCE_PROFILE_BOUNDARY",
            "oracle": "no implicit dependency, authority, activation, surface, or runtime-residue widening",
        }
    return {
        **common,
        "case_kind": "EXISTING_REJECTED_CORPUS" if rejected else "UNAUTHORIZED_CONTRACT_WIDENING_MUTATION",
        "example_ids": rejected,
        "expected": "REJECT_BEFORE_UNAUTHORIZED_CANONICAL_RESIDUE",
        "primary_diagnostic_ids": row.get("normative_trace_refs", {}).get("diagnostics", []),
        "oracle": "no AST/HIR/MIR/API residue outside the exact feature contract",
    }


def main() -> None:
    predecessor_rows = read_json(ROWS)
    catalog, locations = feature_catalog()
    examples = corpus_index()
    cells = blocked_cells(predecessor_rows)
    if not cells and OVERLAY.is_file():
        cells = [
            {
                "feature_id": item["feature_id"],
                "stage": item["stage"],
                "outcome": item["outcome"],
                "predecessor_disposition": item["predecessor_disposition"],
                "predecessor_gap_ids": ["IR-XCUT-P1-054"],
            }
            for item in read_json(OVERLAY).get("bindings", [])
        ]
    if len(cells) != 1242:
        raise ValueError(f"R76_PREDECESSOR_BLOCKED_COUNT:{len(cells)}")

    contract_cells: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    feature_ids: set[str] = set()
    outcome_counts = defaultdict(int)
    stage_counts = defaultdict(int)
    existing_example_reuse: set[str] = set()

    for index, cell in enumerate(cells):
        feature_id = cell["feature_id"]
        stage = cell["stage"]
        outcome = cell["outcome"]
        row = catalog[feature_id]
        feature_ids.add(feature_id)
        stage_counts[stage] += 1
        if outcome is not None:
            outcome_counts[outcome] += 1

        if stage == "AST_FRONTEND" and feature_id in AST_ZERO_RESIDUE:
            disposition = "NOT_APPLICABLE"
            obligation = {
                "obligation_kind": "REJECTED_SURFACE_ZERO_AST_RESIDUE",
                "expected": "REJECT_BEFORE_ADMITTED_AST",
                "frontend_contract": "spec/frontend/frontend-model.json",
            }
        elif stage == "AST_FRONTEND":
            disposition = "BOUND_DIRECT"
            obligation = {
                "obligation_kind": "EXISTING_FRONTEND_NORMALIZATION",
                "expected": "ONE_CANONICAL_CST_AST_INTERPRETATION",
                "frontend_contract": "spec/frontend/frontend-model.json",
            }
        elif stage == "STATIC_SEMANTICS":
            disposition = "BOUND_DIRECT"
            obligation = {
                "obligation_kind": "EXACT_FEATURE_STATIC_ADMISSION",
                "expected": "ENFORCE_FEATURE_NOTES_DEPENDENCIES_PREDICATES_AND_DIAGNOSTIC_FENCE",
                "predicate_ids": row.get("normative_trace_refs", {}).get("predicates", []),
                "diagnostic_ids": row.get("normative_trace_refs", {}).get("diagnostics", []),
            }
        elif stage == "DYNAMIC_LOWERING":
            disposition = "BOUND_DIRECT"
            notes = row.get("notes", "").lower()
            zero_residue = row.get("trace_class") == "rejection" or any(
                token in notes for token in ZERO_DYNAMIC_TOKENS
            )
            obligation = {
                "obligation_kind": "ZERO_DYNAMIC_RESIDUE" if zero_residue else "CANONICAL_HIR_H1_MIR_PROJECTION",
                "expected": "NO_RUNTIME_RESIDUE" if zero_residue else "PRESERVE_EXACT_LANGUAGE_SEMANTICS_WITHOUT_BACKEND_REINTERPRETATION",
                "hir_bridge": "spec/contracts/hir-h1-current-mir-bridge.json",
                "mir_registry": "spec/contracts/hir-mir-lowering-registry.json",
                "backend_contract": "spec/contracts/cranelift-backend-current.json",
            }
        elif stage == "CONFORMANCE_TESTS":
            disposition = "BOUND_DIRECT"
            obligation = test_obligation(feature_id, outcome, examples[feature_id], row)
            for key in ("example_ids", "admitted_example_ids", "rejected_example_ids"):
                existing_example_reuse.update(obligation.get(key, []))
        else:
            raise ValueError(f"R76_UNEXPECTED_BLOCKED_STAGE:{feature_id}:{stage}:{outcome}")

        cell_id = f"R76-CELL-{index + 1:04d}"
        contract_cells.append(
            {
                "cell_id": cell_id,
                "feature_id": feature_id,
                "stage": stage,
                "outcome": outcome,
                "predecessor": {
                    "disposition": cell["predecessor_disposition"],
                    "gap_ids": cell["predecessor_gap_ids"],
                },
                "final_disposition": disposition,
                "feature_contract": {
                    **locations[feature_id],
                    "status_enum": row.get("status_enum"),
                    "feature_kind": row.get("feature_kind"),
                    "trace_class": row.get("trace_class"),
                    "display_name": row.get("display_name"),
                    "notes": row.get("notes"),
                    "primary_source": row.get("primary_source"),
                },
                "obligation": obligation,
                "evidence_level": "E2_STRUCTURED_STATIC",
                "product_execution": "NOT_RUN",
            }
        )
        evidence_key = f"R76:{feature_id}:{stage}:{outcome or 'NONE'}"
        evidence_entries.append(
            {
                "evidence_key": evidence_key,
                "class": "IMPLEMENTATION_TARGET_CELL_CONTRACT",
                "path": "spec/contracts/implementation-target-global-trace-closure-r1.json",
                "locator_kind": "JSON_POINTER",
                "locator": f"/cells/{index}",
                "stage_role": stage if outcome is None else f"{stage}:{outcome}",
            }
        )
        binding: dict[str, Any] = {
            "feature_id": feature_id,
            "stage": stage,
            "outcome": outcome,
            "predecessor_disposition": "APPLICABLE_BLOCKED_BY_GAP",
            "disposition": disposition,
            "evidence_keys": [evidence_key],
            "delegate_feature_id": None,
            "not_applicable": None,
        }
        if disposition == "NOT_APPLICABLE":
            binding["not_applicable"] = {
                "reason_code": "NA_AST_NO_PROGRAMMER_VISIBLE_FORM",
                "authority_boundary": "FRONTEND_AUTHORITY",
                "rationale": "The prohibited predecessor surface is rejected before admitted AST construction and has zero canonical AST/HIR/MIR residue.",
                "justification_evidence_keys": [evidence_key],
            }
        bindings.append(binding)

    contract = {
        "$schema": "../../schemas/language/implementation-target-global-trace-closure-r1.schema.json",
        "schema": "deeplus.implementation-target-global-trace-closure/r1",
        "revision": "r76-global-implementation-target-trace-closure-r1",
        "canonical_baseline_commit": BASELINE,
        "candidate_status": "LOCAL_CANDIDATE_NOT_PRODUCT_EXECUTION",
        "scope": {
            "feature_rows": 469,
            "predecessor_blocked_cells": 1242,
            "closed_by_contract_cells": 1242,
            "remaining_blocked_cells": 0,
            "affected_feature_count": len(feature_ids),
            "stage_counts": dict(sorted(stage_counts.items())),
            "outcome_counts": dict(sorted(outcome_counts.items())),
            "reused_existing_example_count": len(existing_example_reuse),
        },
        "authority_fence": {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_implementation": "NOT_RUN",
            "new_language_semantics": 0,
            "feature_status_change_count": 0,
            "source_activation_change_count": 0,
            "e4_e5_evidence_count": 0,
        },
        "policy": {
            "evidence_domain": "DESIGN_STATIC_HANDOFF_ONLY",
            "direct_binding_meaning": "an exact canonical contract locator exists; it is not parser, checker, runtime, backend, tooling, or product execution evidence",
            "test_specification_meaning": "an implementation acceptance obligation is specified; execution remains NOT_RUN",
            "existing_examples_first": True,
            "missing_example_policy": "bind an exact model-level feature-contract mutation oracle without inventing source syntax or semantic widening",
            "backend_boundary": "Deeplus MIR semantics are backend-neutral; Cranelift projects them and may not reinterpret language behavior",
        },
        "cells": contract_cells,
    }
    overlay = {
        "$schema": "../../../schemas/language/implementation-target-global-trace-evidence-r1.schema.json",
        "schema": "deeplus.implementation-target-global-trace-evidence/r1",
        "revision": "r76-global-implementation-target-trace-closure-r1",
        "canonical_baseline_commit": BASELINE,
        "local_predecessor_commit": BASELINE,
        "candidate_status": "LOCAL_CANDIDATE_NOT_PRODUCT_EXECUTION",
        "feature_ids": sorted(feature_ids),
        "evidence_entries": evidence_entries,
        "bindings": bindings,
        "counts": {
            "feature_count": len(feature_ids),
            "evidence_entry_count": len(evidence_entries),
            "binding_count": len(bindings),
            "bound_direct_count": sum(item["disposition"] == "BOUND_DIRECT" for item in bindings),
            "not_applicable_count": sum(item["disposition"] == "NOT_APPLICABLE" for item in bindings),
            "remaining_blocked_count": 0,
        },
        "guards": contract["authority_fence"],
    }
    write_json(CONTRACT, contract)
    write_json(OVERLAY, overlay)
    print(
        "R76_GLOBAL_TRACE_CLOSURE_BUILT "
        f"features={len(feature_ids)} bindings={len(bindings)} "
        f"direct={overlay['counts']['bound_direct_count']} "
        f"na={overlay['counts']['not_applicable_count']} "
        f"examples={len(existing_example_reuse)}"
    )


if __name__ == "__main__":
    main()
