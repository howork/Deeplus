#!/usr/bin/env python3
"""Run bounded in-memory mutations against the R58 focused validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_member_visibility_trace import CONTRACT_REL, OVERLAY_REL, load, validate


ROOT = Path(__file__).resolve().parents[2]
Mutation = tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]]


def main() -> int:
    overlay = load(ROOT / OVERLAY_REL)
    contract = load(ROOT / CONTRACT_REL)
    normal_errors = validate(ROOT, overlay, contract, validate_schema=True)
    if normal_errors:
        print(json.dumps({"result": "FAIL", "phase": "NORMAL_PATH", "errors": normal_errors}, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("FEATURE_OMISSION", lambda o, c: o["feature_ids"].pop()),
        ("EVIDENCE_OMISSION", lambda o, c: o["evidence_entries"].pop()),
        ("BINDING_OMISSION", lambda o, c: o["bindings"].pop()),
        ("PREDECESSOR_DRIFT", lambda o, c: o["bindings"][0].__setitem__("predecessor_disposition", "NOT_APPLICABLE")),
        ("DISPOSITION_DRIFT", lambda o, c: o["bindings"][0].__setitem__("disposition", "BOUND_DELEGATED")),
        ("DELEGATE_REMOVED", lambda o, c: next(item for item in o["bindings"] if item["disposition"] == "BOUND_DELEGATED").__setitem__("delegate_feature_id", None)),
        ("LOCATOR_DRIFT", lambda o, c: o["evidence_entries"][0].__setitem__("locator", "/missing")),
        ("SIGIL_ADDED", lambda o, c: c["surface_contract"]["member_visibility_sigils"].append("~")),
        ("OMITTED_DEFAULTED", lambda o, c: c["surface_contract"]["omitted"].__setitem__("semantic_value", "PRIVATE")),
        ("LATTICE_REVERSED", lambda o, c: c["static_semantics"].__setitem__("strict_order", "+ < # < -")),
        ("CONFORMER_ADMITTED", lambda o, c: c["static_semantics"]["hierarchy_protected_access_domain"].append("NOMINAL_CONFORMER_NOT_SUBCLASS")),
        ("ANCHOR_REWRITTEN", lambda o, c: c["override_contract"].__setitem__("anchor_rewrite_count", 1)),
        ("NARROWING_ALLOWED", lambda o, c: c["override_contract"].__setitem__("cannot_narrow", False)),
        ("RUNTIME_CHECK_ADDED", lambda o, c: c["lowering_contract"].__setitem__("runtime_visibility_check_count", 1)),
        ("RUNTIME_INSTRUCTION_ADDED", lambda o, c: c["lowering_contract"].__setitem__("runtime_visibility_instruction_count", 1)),
        ("ACCEPTANCE_OMISSION", lambda o, c: c["acceptance_cases"].pop()),
        ("ACCEPTANCE_OVERCLAIM", lambda o, c: c["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
        ("P1_DRIFT", lambda o, c: c["authority_fence"].__setitem__("feature_p1", "21_OPEN")),
        ("M13_DRIFT", lambda o, c: o["guards"].__setitem__("m13_actions", "3_OPEN")),
        ("PRODUCT_OVERCLAIM", lambda o, c: o["guards"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_ENABLED", lambda o, c: o["guards"].__setitem__("github_publication", "ENABLED")),
    ]
    results = []
    for mutation_id, mutate in mutations:
        candidate_overlay = copy.deepcopy(overlay)
        candidate_contract = copy.deepcopy(contract)
        mutate(candidate_overlay, candidate_contract)
        errors = validate(ROOT, candidate_overlay, candidate_contract, validate_schema=False)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "first_error": errors[0] if errors else None})
    rejected = sum(item["rejected"] for item in results)
    passed = rejected == len(results)
    print(json.dumps({
        "schema": "deeplus.member-visibility-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": len(results),
        "rejected_count": rejected,
        "results": results,
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
