#!/usr/bin/env python3
"""Validate the bounded R65 associated-requirement AST/diagnostic parity repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "f2e7353b1c44fc066eba47f6d013cbe0a20e9239"
REVISION = "r65-local-associated-requirement-ast-diagnostic-parity-r1"
FEATURE = "associated_requirement_phase_a"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/associated-requirement-ast-diagnostic-parity-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/associated-requirement-ast-diagnostic-parity-evidence-r1.schema.json"
ROWS_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
GRAMMAR_REGISTRY_REL = "spec/contracts/grammar-production-disposition-registry-r1.json"
DIAGNOSTIC_CATALOG_REL = "spec/diagnostics/catalog/chunks/part-0001.json"
DIAGNOSTIC_RELATION_REL = "spec/diagnostics/relations/chunks/part-0001.json"
R64_CONTRACT_REL = "spec/contracts/associated-requirement-phase-a-trace-closure-r1.json"
DECISION_REL = "decisions/language/Design_Deeplus_R65_Associated_Requirement_AST_Diagnostic_Parity_R1.md"
TARGETS = {
    (FEATURE, "AST_FRONTEND", None),
    (FEATURE, "DIAGNOSTICS", None),
}
BYTE_FENCES = {
    "spec/features/catalog/chunks/part-0001.json": "abbdaf8e3e3115b9e1a6c005b0641a72c1d432d0d0b2025a3519a762e4c91c86",
    "spec/grammar/deeplus.ebnf": "303e90004386609777013bb6f15d139277e39ab0bf71301ace990a1f0092fb2a",
    "spec/frontend/frontend-model.json": "7a871f1b565eccc3ff6b7d081dc76cbc6ff7282f1aeea5e68237f64b854f7c9f",
    GRAMMAR_REGISTRY_REL: "0744e9353a24a016c279ceb91c3585cf5094608e59f676515b7e254f4223f03c",
    DIAGNOSTIC_CATALOG_REL: "18dca15178f6e9290a73e759921c65aa1e7edb94adc075a898ccf96668cdabb5",
    DIAGNOSTIC_RELATION_REL: "fe2f779eba81025ec008b69deb40dadc0a982349a66d9564f69d699fa8ff053a",
    R64_CONTRACT_REL: "c087220df930a8fec18b08c55aeee17ba0538debcfe2e4a6e612052c866ebad4",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace_cells(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str | None], dict[str, Any]]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for row in rows:
        feature_id = row.get("feature_id")
        for stage in row.get("stages", []):
            stage_name = stage.get("stage")
            values = stage.get("outcomes", [stage])
            for cell in values:
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                key = (feature_id, stage_name, outcome)
                if key in cells:
                    raise ValueError(f"duplicate trace cell: {key}")
                cells[key] = copy.deepcopy(cell)
    return cells


def predecessor_rows(root: Path) -> list[dict[str, Any]]:
    raw = subprocess.check_output(
        ["git", "-c", f"safe.directory={root.as_posix()}", "show", f"{PREDECESSOR}:{ROWS_REL}"],
        cwd=root,
        text=True,
        encoding="utf-8",
    )
    value = json.loads(raw)
    return value.get("rows", value) if isinstance(value, dict) else value


def validate(
    root: Path,
    overlay: dict[str, Any],
    *,
    validate_schema: bool = True,
    grammar_registry_override: dict[str, Any] | None = None,
    diagnostic_catalog_override: list[dict[str, Any]] | None = None,
    relation_override: list[dict[str, Any]] | None = None,
    r64_contract_override: dict[str, Any] | None = None,
    rows_override: list[dict[str, Any]] | None = None,
    metadata_override: dict[str, Any] | None = None,
    predecessor_rows_override: list[dict[str, Any]] | None = None,
    decision_text_override: str | None = None,
) -> dict[str, Any]:
    failures: dict[str, list[str]] = {f"G{i:02d}": [] for i in range(1, 11)}

    def require(gate: int, condition: bool, code: str) -> None:
        if not condition:
            failures[f"G{gate:02d}"].append(code)

    if validate_schema:
        try:
            import jsonschema

            jsonschema.Draft202012Validator(load(root / OVERLAY_SCHEMA_REL)).validate(overlay)
        except ImportError:
            pass
        except Exception as exc:
            failures["G10"].append(f"JSON_SCHEMA:{exc}")

    grammar = grammar_registry_override or load(root / GRAMMAR_REGISTRY_REL)
    diagnostic_catalog = diagnostic_catalog_override or load(root / DIAGNOSTIC_CATALOG_REL)
    relations = relation_override or load(root / DIAGNOSTIC_RELATION_REL)
    r64 = r64_contract_override or load(root / R64_CONTRACT_REL)
    rows_value = rows_override or load(root / ROWS_REL)
    rows = rows_value.get("rows", rows_value) if isinstance(rows_value, dict) else rows_value
    metadata = metadata_override or load(root / METADATA_REL)
    before_rows = predecessor_rows_override or predecessor_rows(root)
    decision_text = decision_text_override if decision_text_override is not None else (root / DECISION_REL).read_text(encoding="utf-8")

    # G01: exact noncanonical identity and bounded scope.
    require(1, overlay.get("revision") == REVISION, "REVISION")
    require(1, overlay.get("canonical_baseline_commit") == BASELINE, "BASELINE")
    require(1, overlay.get("local_predecessor_commit") == PREDECESSOR, "PREDECESSOR")
    require(1, overlay.get("feature_ids") == [FEATURE], "FEATURE_SCOPE")
    require(1, "IR-TRACE-P1-056" in decision_text and "LOCAL_APPROVED_CANDIDATE" in decision_text, "DECISION_IDENTITY")

    before = trace_cells(before_rows)
    after = trace_cells(rows)

    # G02: predecessor facts are the two stale N/A cells.
    require(2, len(before) == 4221 and set(before) == set(after), "ATOMIC_CELL_DOMAIN")
    for target in sorted(TARGETS):
        cell = before.get(target, {})
        require(2, cell.get("disposition") == "NOT_APPLICABLE", f"PREDECESSOR_NA:{target[1]}")
        require(2, cell.get("not_applicable") is not None, f"PREDECESSOR_NA_DETAIL:{target[1]}")

    # G03: the declaration already has one exact stable AST owner.
    declaration = resolve_pointer(grammar, "/production_rows/237")
    require(3, declaration.get("production_id") == "AssociatedRequirementDecl", "DECL_PRODUCTION")
    require(3, declaration.get("profile") == "STABLE" and declaration.get("reachability_owner") == "CURRENT_SOURCE_GRAPH", "DECL_CURRENT_STABLE")
    require(3, declaration.get("disposition") == "ast_node", "DECL_AST_DISPOSITION")
    require(3, declaration.get("ast_target") == "AST/AssociatedRequirementDecl" and declaration.get("ast_output_cardinality") == "EXACTLY_ONE", "DECL_AST_OWNER")

    # G04: the binding remains inline CST owned by the existing Conformance AST.
    binding = resolve_pointer(grammar, "/production_rows/251")
    conformance = resolve_pointer(grammar, "/production_rows/241")
    require(4, binding.get("production_id") == "AssociatedRequirementBinding", "BINDING_PRODUCTION")
    require(4, binding.get("disposition") == "cst_only" and binding.get("ast_target") is None, "BINDING_CST_ONLY")
    require(4, binding.get("ast_output_cardinality") == "ZERO" and binding.get("cst_shape") == "INLINE_IN_PARENT_PRODUCTION_NODE", "BINDING_INLINE_ZERO_AST")
    require(4, conformance.get("ast_target") == "AST/ConformanceDecl", "BINDING_PARENT_OWNER")

    # G05: an active primary diagnostic and exact R64 emission rule already exist.
    diagnostic = resolve_pointer(diagnostic_catalog, "/39")
    relation = resolve_pointer(relations, "/8")
    rules = {item.get("rule_id"): item.get("text", "") for item in r64.get("rules", [])}
    require(5, diagnostic.get("diagnostic_id") == "ASSOCIATED_REQUIREMENT_UNRESOLVED", "DIAGNOSTIC_ID")
    require(5, diagnostic.get("diagnostic_status") == "active" and diagnostic.get("stage") == "checker", "DIAGNOSTIC_ACTIVE")
    require(5, FEATURE in diagnostic.get("feature_refs", []) and diagnostic.get("product_support") == "NOT_RUN", "DIAGNOSTIC_FEATURE_PRODUCT")
    require(5, relation == {"violation_id": "AssociatedRequirementAdmitted:default", "predicate_id": "AssociatedRequirementAdmitted", "diagnostic_id": "ASSOCIATED_REQUIREMENT_UNRESOLVED", "relation": "primary"}, "PRIMARY_RELATION")
    require(5, "exactly one ASSOCIATED_REQUIREMENT_UNRESOLVED" in rules.get("ARPTC-R006", "") and "NOT_EVALUATED" in rules.get("ARPTC-R006", ""), "R64_PRIMARY_RULE")

    # G06: exact two-entry/two-binding overlay, no delegate or N/A residue.
    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    require(6, len(entries) == 2 and len({item.get("evidence_key") for item in entries}) == 2, "EVIDENCE_EXACT_2")
    require(6, len(bindings) == 2, "BINDING_EXACT_2")
    expected_targets = {(item.get("feature_id"), item.get("stage"), item.get("outcome")) for item in bindings}
    require(6, expected_targets == TARGETS, "BINDING_TARGETS")
    for item in bindings:
        require(6, item.get("predecessor_disposition") == "NOT_APPLICABLE" and item.get("disposition") == "BOUND_DIRECT", f"BINDING_TRANSITION:{item.get('stage')}")
        require(6, item.get("delegate_feature_id") is None and item.get("not_applicable") is None, f"BINDING_RESIDUE:{item.get('stage')}")
    try:
        ast_entry = next(item for item in entries if item.get("stage_role") == "AST_FRONTEND")
        diag_entry = next(item for item in entries if item.get("stage_role") == "DIAGNOSTICS")
        require(6, ast_entry.get("path") == GRAMMAR_REGISTRY_REL and ast_entry.get("locator") == "/production_rows/237", "AST_EVIDENCE")
        require(6, diag_entry.get("path") == R64_CONTRACT_REL and diag_entry.get("locator") == "ARPTC-R006", "DIAGNOSTIC_EVIDENCE")
    except StopIteration:
        require(6, False, "EVIDENCE_STAGE_ROLES")

    # G07: exact global reconstruction and overlay binding counts.
    counts = metadata.get("derived_counts", {})
    require(7, (counts.get("bound_direct_cells"), counts.get("bound_delegated_cells"), counts.get("not_applicable_cells"), counts.get("applicable_blocked_cells")) == (2463, 3, 501, 1254), "TRACE_COUNTS")
    applied = metadata.get("applied_evidence_overlays", [])
    require(7, len(applied) == 11 and sum(item.get("binding_count", 0) for item in applied) == 127, "OVERLAY_BINDING_COUNTS")
    require(7, len(metadata.get("evidence_registry", [])) == 3140, "EVIDENCE_REGISTRY_3140")
    require(7, counts.get("missing_cells") == 0 and counts.get("conflict_cells") == 0, "NO_MISSING_CONFLICT")

    # G08: only the two target cells differ byte-for-byte.
    changed = {key for key in before if before[key] != after[key]}
    require(8, changed == TARGETS, f"EXACT_TARGET_DIFF:{sorted(changed)}")
    for target in TARGETS:
        cell = after.get(target, {})
        require(8, cell.get("disposition") == "BOUND_DIRECT", f"TARGET_DIRECT:{target[1]}")
        require(8, cell.get("delegate_feature_id") is None and cell.get("not_applicable") is None and cell.get("blocked_gap_ids") == [], f"TARGET_CLEAN:{target[1]}")
    require(8, len(before) - len(changed) == 4219, "OTHER_4219_UNCHANGED")

    # G09: no source, registry, frontend, diagnostic, or R64 authority bytes drift.
    for rel, expected in BYTE_FENCES.items():
        require(9, sha256(root / rel) == expected, f"BYTE_FENCE:{rel}")

    # G10: schema/path/governance and evidence-honesty fence.
    require(10, (root / OVERLAY_SCHEMA_REL).is_file() and (root / DECISION_REL).is_file(), "REQUIRED_PATHS")
    require(10, all((root / item.get("path", "")).is_file() for item in entries), "EVIDENCE_PATHS")
    guards = overlay.get("guards", {})
    require(10, guards.get("transitioned_cell_count") == 2 and guards.get("other_atomic_cell_count") == 4219, "GUARD_CELL_COUNTS")
    require(10, guards.get("semantic_p0") == 0 and guards.get("feature_p1") == "22_OPEN_UNCHANGED" and guards.get("m13_actions") == "4_OPEN_UNCHANGED", "GOVERNANCE_COUNTS")
    require(10, guards.get("product_lanes") == "15_OF_15_NOT_RUN" and guards.get("github_publication") == "SUSPENDED", "PRODUCT_GITHUB_FENCE")
    require(10, all(row.get("product_execution") == "NOT_RUN" for row in rows), "ALL_PRODUCT_ROWS_NOT_RUN")

    passed = sum(not values for values in failures.values())
    errors = [f"{gate}:{code}" for gate, values in failures.items() for code in values]
    return {
        "schema": "deeplus.associated-requirement-ast-diagnostic-parity-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "checks": 10,
        "passed": passed,
        "failed": 10 - passed,
        "errors": errors,
        "transitioned_cells": 2,
        "unchanged_other_cells": 4219,
        "trace_counts": {"direct": 2463, "delegated": 3, "not_applicable": 501, "blocked": 1254},
        "overlay_count": 11,
        "overlay_binding_count": 127,
        "evidence_registry_count": 3140,
        "product_lanes": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    receipt = validate(root, load(root / OVERLAY_REL))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
