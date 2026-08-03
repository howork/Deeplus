#!/usr/bin/env python3
"""Validate the bounded R58 member-visibility contract and trace projection."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/member-visibility-trace-closure-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/member-visibility-trace-closure-r1.schema.json"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/member-visibility-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/member-visibility-evidence-r1.schema.json"
TRACE_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "6a0eb950fb46fc061c260445bb0d25dc766117ea"
FEATURES = sorted([
    "member_visibility_hierarchy_protected",
    "member_visibility_sigil_surface_phase_a",
    "member_visibility_sigils_only",
])
EXPECTED_CELLS = {
    ("member_visibility_hierarchy_protected", "DYNAMIC_LOWERING", None): ("APPLICABLE_BLOCKED_BY_GAP", "NOT_APPLICABLE", None),
    ("member_visibility_hierarchy_protected", "DIAGNOSTICS", None): ("NOT_APPLICABLE", "BOUND_DIRECT", None),
    **{
        ("member_visibility_hierarchy_protected", "CONFORMANCE_TESTS", outcome): ("APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT", None)
        for outcome in ("POSITIVE", "BOUNDARY", "REJECT")
    },
    ("member_visibility_sigil_surface_phase_a", "STATIC_SEMANTICS", None): ("APPLICABLE_BLOCKED_BY_GAP", "NOT_APPLICABLE", None),
    ("member_visibility_sigil_surface_phase_a", "CONFORMANCE_TESTS", "POSITIVE"): ("APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT", None),
    ("member_visibility_sigil_surface_phase_a", "CONFORMANCE_TESTS", "BOUNDARY"): ("APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT", None),
    ("member_visibility_sigil_surface_phase_a", "CONFORMANCE_TESTS", "REJECT"): ("APPLICABLE_BLOCKED_BY_GAP", "BOUND_DELEGATED", "member_visibility_sigils_only"),
    ("member_visibility_sigils_only", "DYNAMIC_LOWERING", None): ("APPLICABLE_BLOCKED_BY_GAP", "NOT_APPLICABLE", None),
    **{
        ("member_visibility_sigils_only", "CONFORMANCE_TESTS", outcome): ("APPLICABLE_BLOCKED_BY_GAP", "BOUND_DIRECT", None)
        for outcome in ("POSITIVE", "BOUNDARY", "REJECT")
    },
}
EXPECTED_ACCEPTANCE = {
    ("member_visibility_hierarchy_protected", "POSITIVE"): ["MVTC-AC-001"],
    ("member_visibility_hierarchy_protected", "BOUNDARY"): ["MVTC-AC-002"],
    ("member_visibility_hierarchy_protected", "REJECT"): ["MVTC-AC-003"],
    ("member_visibility_sigil_surface_phase_a", "POSITIVE"): ["MVTC-AC-004"],
    ("member_visibility_sigil_surface_phase_a", "BOUNDARY"): ["MVTC-AC-005"],
    ("member_visibility_sigil_surface_phase_a", "REJECT"): ["MVTC-AC-006"],
    ("member_visibility_sigils_only", "POSITIVE"): ["MVTC-AC-007", "MVTC-AC-008"],
    ("member_visibility_sigils_only", "BOUNDARY"): ["MVTC-AC-009"],
    ("member_visibility_sigils_only", "REJECT"): ["MVTC-AC-010"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative).glob("part-*.json")):
        rows.extend(load(path))
    return rows


def resolve_pointer(value: Any, pointer: str) -> Any:
    current = value
    for raw in pointer.split("/")[1:]:
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


def trace_cell(row: dict[str, Any], stage_name: str, outcome: str | None) -> dict[str, Any]:
    stage = next(item for item in row["stages"] if item["stage"] == stage_name)
    if outcome is None:
        return stage
    return next(item for item in stage["outcomes"] if item["outcome"] == outcome)


def trace_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        for stage in row["stages"]:
            for cell in stage.get("outcomes", [stage]):
                counts[cell["disposition"]] += 1
    return counts


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any],
    validate_schema: bool = True,
    trace_rows_override: list[dict[str, Any]] | None = None,
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

    surface = contract.get("surface_contract", {})
    require(surface.get("member_visibility_sigils") == ["+", "-", "#"], "SIGILS_EXACT")
    require(surface.get("exact_normalization") == {"+": "PUBLIC", "-": "PRIVATE", "#": "HIERARCHY_PROTECTED"}, "SIGIL_NORMALIZATION_EXACT")
    require(surface.get("omitted") == {"syntax_state": "OMITTED", "semantic_value": None, "r58_global_default": None, "default_application_count": 0}, "OMITTED_EXPLICIT_NO_DEFAULT")
    static = contract.get("static_semantics", {})
    require(static.get("strict_order") == "- < # < +", "ACCESS_LATTICE_EXACT")
    require(static.get("hierarchy_protected_access_domain") == ["DECLARING_NOMINAL", "NOMINAL_SUBCLASS"], "PROTECTED_DOMAIN_EXACT")
    require(static.get("hierarchy_protected_rejected_consumers") == ["MODULE_PEER", "NOMINAL_CONFORMER_NOT_SUBCLASS", "STRUCTURAL_PEER"], "PROTECTED_REJECTORS_EXACT")
    override = contract.get("override_contract", {})
    require(override.get("slot_anchor") == "ORIGINAL_DECLARING_NOMINAL_SLOT" and override.get("anchor_rewrite_count") == 0, "OVERRIDE_ANCHOR_EXACT")
    require(override.get("cannot_narrow") is True and override.get("comparison_order") == "- < # < +", "OVERRIDE_NO_NARROW")
    lowering = contract.get("lowering_contract", {})
    require(lowering.get("classification") == "STATIC_ONLY_NO_RUNTIME_BEHAVIOR", "STATIC_ONLY")
    require(lowering.get("runtime_visibility_check_count") == 0 and lowering.get("runtime_visibility_instruction_count") == 0, "NO_RUNTIME_VISIBILITY")
    require(lowering.get("new_hir_identity_count") == 0 and lowering.get("new_mir_operation_kind_count") == 0, "NO_NEW_LOWERING_IDENTITY")

    rules = contract.get("rules", [])
    require([item.get("rule_id") for item in rules] == [f"MVTC-R{index:03d}" for index in range(1, 13)], "RULE_IDS_EXACT_12")
    cases = contract.get("acceptance_cases", [])
    case_by_id = {case.get("case_id"): case for case in cases}
    require(len(cases) == 10 and len(case_by_id) == 10, "ACCEPTANCE_EXACT_UNIQUE_10")
    require((sum(case.get("class") == "POSITIVE" for case in cases), sum(case.get("class") == "BOUNDARY" for case in cases), sum(case.get("class") == "REJECT" for case in cases)) == (4, 3, 3), "ACCEPTANCE_CLASS_COUNTS")
    require(all(case.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for case in cases), "ACCEPTANCE_DESIGN_STATIC_NOT_RUN")
    for (feature, outcome), expected_ids in EXPECTED_ACCEPTANCE.items():
        observed = contract.get("acceptance_bindings", {}).get(feature, {}).get(outcome)
        require(observed == expected_ids, f"ACCEPTANCE_BINDING:{feature}:{outcome}")
        require(all(case_by_id.get(case_id, {}).get("feature_id") == feature and case_by_id.get(case_id, {}).get("class") == outcome for case_id in expected_ids), f"ACCEPTANCE_CLASS:{feature}:{outcome}")

    entries = overlay.get("evidence_entries", [])
    by_key = {item.get("evidence_key"): item for item in entries}
    require(len(entries) == 13 and len(by_key) == 13, "EVIDENCE_EXACT_UNIQUE_13")
    for key, item in by_key.items():
        require(isinstance(key, str) and key.startswith("R58:"), f"EVIDENCE_KEY:{key}")
        require(item.get("path") == CONTRACT_REL, f"EVIDENCE_PATH:{key}")
        if item.get("locator_kind") == "JSON_POINTER":
            try:
                resolve_pointer(contract, item.get("locator", ""))
            except (KeyError, IndexError, TypeError, ValueError):
                require(False, f"EVIDENCE_POINTER:{key}")
        else:
            require(contains_scalar(contract, item.get("locator", "")), f"EVIDENCE_RULE:{key}")

    bindings = overlay.get("bindings", [])
    by_cell = {(item.get("feature_id"), item.get("stage"), item.get("outcome")): item for item in bindings}
    require(len(bindings) == 13 and len(by_cell) == 13 and set(by_cell) == set(EXPECTED_CELLS), "BINDING_CELLS_EXACT_13")
    for cell, (predecessor, disposition, delegate) in EXPECTED_CELLS.items():
        item = by_cell.get(cell, {})
        require(item.get("predecessor_disposition") == predecessor, f"BINDING_PREDECESSOR:{cell}")
        require(item.get("disposition") == disposition, f"BINDING_DISPOSITION:{cell}")
        require(item.get("delegate_feature_id") == delegate, f"BINDING_DELEGATE:{cell}")
        refs = item.get("evidence_keys", [])
        require(len(refs) == 1 and refs[0] in by_key, f"BINDING_EVIDENCE:{cell}")
        if disposition == "NOT_APPLICABLE":
            detail = item.get("not_applicable") or {}
            require(detail.get("justification_evidence_keys") == refs, f"BINDING_NA_EVIDENCE:{cell}")
        else:
            require(item.get("not_applicable") is None, f"BINDING_NOT_NA:{cell}")

    trace_rows = trace_rows_override if trace_rows_override is not None else load(root / TRACE_REL)
    trace_by_id = {row["feature_id"]: row for row in trace_rows}
    require(len(trace_rows) == 469 and len(trace_by_id) == 469, "TRACE_FEATURES_469")
    predecessor_counts = trace_counts(trace_rows)
    require(tuple(predecessor_counts[key] for key in ("BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE", "APPLICABLE_BLOCKED_BY_GAP")) == (2438, 2, 500, 1281), "PREDECESSOR_COUNTS_EXACT")
    projected = predecessor_counts.copy()
    for cell, item in by_cell.items():
        observed = trace_cell(trace_by_id[cell[0]], cell[1], cell[2])
        require(observed.get("disposition") == item.get("predecessor_disposition"), f"TRACE_PREDECESSOR:{cell}")
        projected[item["predecessor_disposition"]] -= 1
        projected[item["disposition"]] += 1
    require(tuple(projected[key] for key in ("BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE", "APPLICABLE_BLOCKED_BY_GAP")) == (2447, 3, 502, 1269), "POST_COUNTS_EXACT")

    predicate_rows = {row["predicate_id"]: row for row in all_rows(root, "spec/types/predicates/chunks")}
    visibility = predicate_rows.get("ReferenceVisibilityActivationAdmitted", {})
    require("member_visibility_hierarchy_protected" in visibility.get("feature_refs", []), "HIERARCHY_PREDICATE_BOUND")
    require(visibility.get("active_primary_diagnostic") == "REFERENCE_VISIBILITY_OR_ACTIVATION_VIOLATION", "HIERARCHY_DIAGNOSTIC_BOUND")
    require(visibility.get("product_support") == "NOT_RUN" and visibility.get("execution_receipt") is None, "PREDICATE_NOT_RUN")

    machine = contract.get("machine_acceptance", {})
    require((machine.get("post_overlay_total_bound_direct_cell_count"), machine.get("post_overlay_total_bound_delegated_cell_count"), machine.get("post_overlay_total_not_applicable_cell_count"), machine.get("post_overlay_total_blocked_cell_count")) == (2447, 3, 502, 1269), "MACHINE_POST_COUNTS")
    guards = overlay.get("guards", {})
    fence = contract.get("authority_fence", {})
    for value, prefix in ((guards, "GUARD"), (fence, "FENCE")):
        require(value.get("semantic_p0") == 0 and value.get("feature_p1") == "22_OPEN_UNCHANGED", f"{prefix}_P0_P1")
        require(value.get("m13_actions") == "4_OPEN_UNCHANGED", f"{prefix}_M13")
        require(value.get("product_lanes") == "15_OF_15_NOT_RUN", f"{prefix}_PRODUCT")
        require(value.get("github_publication") == "SUSPENDED", f"{prefix}_GITHUB")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    overlay = load(root / OVERLAY_REL)
    contract = load(root / CONTRACT_REL)
    errors = validate(root, overlay, contract)
    print(json.dumps({
        "schema": "deeplus.member-visibility-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_count": len(overlay.get("feature_ids", [])),
        "binding_count": len(overlay.get("bindings", [])),
        "contract_acceptance_case_count": len(contract.get("acceptance_cases", [])),
        "projected_counts": {"bound_direct": 2447, "bound_delegated": 3, "not_applicable": 502, "applicable_blocked": 1269, "missing": 0, "conflict": 0},
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
