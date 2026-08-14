#!/usr/bin/env python3
"""Validate the bounded R100 accessor/property/forwarding design-static closure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "spec/contracts/accessor-property-forwarding-r100.json"
FIXTURE = "tests/fixtures/current/accessor-property-forwarding-r100.json"
OVERLAY = "spec/traceability/implementation-target-profile-r1/accessor-property-forwarding-evidence-r100.json"
EXPECTED_FEATURES = {
    "accessor_property_colon_equals_surface",
    "accessor_visibility_restored_law",
    "accessor_visibility_surface_phase_a",
    "instance_extension_property",
    "member_forwarding",
    "property_default_accessor",
    "property_value_admissibility",
    "simplified_class_member_surface",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    contract = load(root / CONTRACT)
    fixture = load(root / FIXTURE)
    overlay = load(root / OVERLAY)
    language = (root / "spec/language.md").read_text(encoding="utf-8")
    types = (root / "spec/types/type-system.md").read_text(encoding="utf-8")
    grammar = (root / "spec/grammar/deeplus.dpg").read_text(encoding="utf-8")
    frontend = load(root / "spec/frontend/frontend-model.json")
    diagnostics: list[dict[str, Any]] = []
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("part-*.json")):
        diagnostics.extend(load(path))
    diagnostic_ids = {row.get("diagnostic_id") for row in diagnostics}

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    features = contract.get("feature_ids", [])
    require(set(features) == EXPECTED_FEATURES and len(features) == 8, "FEATURE_SET")
    rules = contract.get("rules", [])
    rule_ids = [row.get("rule_id") for row in rules]
    require(rule_ids == [f"APMF-R{i:03d}" for i in range(1, 14)], "RULE_ID_ORDER")
    require("Accessor    := ('let'|'var') Name TypeAnn ':='" in grammar, "DPG_ACCESSOR_ROOT")
    require("Forward     := [MemberVis] ~forward" in grammar, "DPG_FORWARD_ROOT")
    require("accessor_property_admission" in json.dumps(frontend), "FRONTEND_ACCESSOR_ADMISSION")
    for token in ("throws Never effects {}", "receiver once", "target expression once", "backing-storage identity", "runtime lookup"):
        require(token.casefold() in json.dumps(contract, ensure_ascii=False).casefold(), f"CONTRACT_TOKEN:{token}")
    for token in ("AccessorPropertyDecl", "ForwardDecl", "MemberVisibilityOmissionV1"):
        require(token in language or token in types, f"CANONICAL_PROSE:{token}")

    cases = fixture.get("cases", [])
    case_ids = [row.get("case_id") for row in cases]
    require(case_ids == [f"APMF-AC-{i:03d}" for i in range(1, 24)], "CASE_ID_ORDER")
    require(len(case_ids) == len(set(case_ids)), "CASE_ID_UNIQUE")
    require({row.get("class") for row in cases} == {"POSITIVE", "BOUNDARY", "REJECT"}, "CASE_CLASSES")
    bound_ids: set[str] = set()
    bindings = contract.get("acceptance_bindings", {})
    require(set(bindings) == EXPECTED_FEATURES, "ACCEPTANCE_FEATURE_SET")
    for feature_id, outcomes in bindings.items():
        require(set(outcomes) == {"POSITIVE", "BOUNDARY", "REJECT"}, f"OUTCOME_SET:{feature_id}")
        for outcome, ids in outcomes.items():
            require(bool(ids), f"OUTCOME_NONEMPTY:{feature_id}:{outcome}")
            bound_ids.update(ids)
            for case_id in ids:
                row = next((item for item in cases if item.get("case_id") == case_id), {})
                require(row.get("class") == outcome, f"CASE_CLASS:{feature_id}:{outcome}:{case_id}")
    require(bound_ids == set(case_ids), "CASE_BINDING_TOTAL")

    required_diags = set(contract.get("diagnostic_order", []))
    require(required_diags <= diagnostic_ids, "DIAGNOSTIC_IDS")
    overlay_bindings = overlay.get("bindings", [])
    cells = {(row.get("feature_id"), row.get("stage"), row.get("outcome")) for row in overlay_bindings}
    superseded = {(row.get("feature_id"), row.get("stage"), row.get("outcome")) for row in overlay.get("supersedes_binding_cells", {}).get("cells", [])}
    require(len(overlay.get("evidence_entries", [])) == 35, "EVIDENCE_COUNT")
    require(len(overlay_bindings) == 35 and len(cells) == 35, "BINDING_COUNT")
    require(len(superseded) == 32 and superseded < cells, "SUPERSESSION_CELL_EXACT")
    require({cell[0] for cell in cells} == EXPECTED_FEATURES, "OVERLAY_FEATURE_SET")
    require(sum(1 for row in overlay_bindings if row.get("disposition") == "NOT_APPLICABLE") == 5, "DYNAMIC_NA_EXACT_5")
    require(sum(1 for row in overlay_bindings if row.get("disposition") == "BOUND_DIRECT") == 30, "DIRECT_EXACT_30")
    require(contract.get("guards") == {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_implementation": "NOT_AUTHORIZED_NOT_PERFORMED",
        "github_mutation": 0,
        "canonical_publication": "NOT_PERFORMED",
    }, "GOVERNANCE_GUARDS")
    require(fixture.get("product_execution") == "NOT_RUN", "FIXTURE_NOT_RUN")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR:{error}")
        return 1
    print("R100 accessor/property/forwarding closure: PASS (8 features, 13 rules, 23 cases, 35 successor cells; product NOT_RUN)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
