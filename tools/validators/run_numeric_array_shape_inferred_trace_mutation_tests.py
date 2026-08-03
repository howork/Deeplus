#!/usr/bin/env python3
"""Focused mutation oracles for the R56 shape-inferred NumericArray overlay."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_numeric_array_shape_inferred_trace import CONTRACT_REL, OVERLAY_REL, load, validate


Mutation = tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]]


def wrong_locator(entry: dict[str, Any]) -> None:
    if entry.get("locator_kind") == "JSON_POINTER":
        entry["locator"] = "/__missing_json_pointer__"
    else:
        entry["locator"] = "__MISSING_REGISTRY_ID__"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overlay_path = args.overlay.resolve() if args.overlay else root / OVERLAY_REL
    contract_path = args.contract.resolve() if args.contract else root / CONTRACT_REL
    try:
        baseline_overlay = load(overlay_path)
        baseline_contract = load(contract_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"result": "FAIL", "errors": [f"LOAD:{type(exc).__name__}:{exc}"]}, indent=2))
        return 1

    normal_errors = validate(
        root,
        baseline_overlay,
        baseline_contract,
        validate_schema=args.overlay is None and args.contract is None,
    )
    if normal_errors:
        print(json.dumps({
            "schema": "deeplus.numeric-array-shape-inferred-trace-mutation-receipt/r1",
            "result": "FAIL",
            "phase": "NORMAL_PATH",
            "errors": normal_errors,
            "product_execution": "15_OF_15_NOT_RUN",
            "github_publication": "SUSPENDED",
        }, indent=2))
        return 1

    mutations: list[Mutation] = [
        ("FEATURE_OMISSION", lambda overlay, contract: overlay["feature_ids"].pop()),
        ("EVIDENCE_OMISSION", lambda overlay, contract: overlay["evidence_entries"].pop()),
        ("BINDING_OMISSION", lambda overlay, contract: overlay["bindings"].pop()),
        ("WRONG_LOCATOR", lambda overlay, contract: wrong_locator(overlay["evidence_entries"][0])),
        ("WRONG_BINDING_FEATURE", lambda overlay, contract: overlay["bindings"][0].__setitem__("feature_id", "invented_feature")),
        ("WRONG_BINDING_STAGE", lambda overlay, contract: overlay["bindings"][0].__setitem__("stage", "TOOLING_OBLIGATIONS")),
        ("DIRECT_TO_DELEGATED", lambda overlay, contract: overlay["bindings"][0].update({"disposition": "BOUND_DELEGATED", "delegate_feature_id": overlay["feature_ids"][1]})),
        ("UNKNOWN_EVIDENCE_KEY", lambda overlay, contract: overlay["bindings"][0].__setitem__("evidence_keys", ["R56:UNKNOWN"])),
        ("ACCEPTANCE_CASE_OMISSION", lambda overlay, contract: overlay["acceptance_cases"].pop()),
        ("ACCEPTANCE_PRODUCT_OVERCLAIM", lambda overlay, contract: overlay["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
        ("CONTRACT_FEATURE_OMISSION", lambda overlay, contract: contract["feature_ids"].pop()),
        ("CONTRACT_FORM_ORIENTATION_DRIFT", lambda overlay, contract: contract["syntax_contract"]["forms"][0].__setitem__("orientation", "NEUTRAL")),
        ("CONTRACT_RANK2_CONFLATION", lambda overlay, contract: contract["static_semantics"].__setitem__("exact_rank_two_nonidentity", False)),
        ("CONTRACT_RULE_OMISSION", lambda overlay, contract: contract["rules"].pop()),
        ("EVALUATION_ORDER_DRIFT", lambda overlay, contract: contract["lowering_contract"].__setitem__("element_evaluation_order", "UNSPECIFIED")),
        ("EVALUATION_COUNT_DRIFT", lambda overlay, contract: contract["lowering_contract"].__setitem__("element_evaluation_count_each", 2)),
        ("MIR_OPERATION_INVENTION", lambda overlay, contract: contract["lowering_contract"]["assembly"].__setitem__("operation_kind", "NUMERIC_ARRAY_ASSEMBLE")),
        ("PARTIAL_PUBLISH", lambda overlay, contract: contract["lowering_contract"]["publication"].__setitem__("partial_publish_count", 1)),
        ("EMPTY_DIAGNOSTIC_DRIFT", lambda overlay, contract: contract["acceptance_cases"][2].__setitem__("diagnostic_or_null", "NUMARR_LITERAL_REQUIRES_EXPRESSIONS")),
        ("MISMATCH_SOURCE_DRIFT", lambda overlay, contract: contract["acceptance_cases"][3].__setitem__("source_or_subject", "let mixed = #[1, \"two\"]")),
        ("SEMANTIC_P0_DRIFT", lambda overlay, contract: overlay["guards"].__setitem__("semantic_p0", 1)),
        ("PRODUCT_PASS", lambda overlay, contract: overlay["guards"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_ENABLED", lambda overlay, contract: overlay["guards"].__setitem__("github_publication", "ENABLED")),
    ]

    results: list[dict[str, Any]] = []
    for mutation_id, mutate in mutations:
        candidate_overlay = copy.deepcopy(baseline_overlay)
        candidate_contract = copy.deepcopy(baseline_contract)
        try:
            mutate(candidate_overlay, candidate_contract)
            errors = validate(root, candidate_overlay, candidate_contract, validate_schema=False)
        except (KeyError, IndexError, StopIteration, TypeError) as exc:
            errors = [f"MUTATION_SETUP:{type(exc).__name__}:{exc}"]
        results.append({
            "mutation_id": mutation_id,
            "rejected": bool(errors) and not errors[0].startswith("MUTATION_SETUP:"),
            "first_error": errors[0] if errors else None,
        })

    rejected_count = sum(row["rejected"] for row in results)
    passed = rejected_count == len(results)
    print(json.dumps({
        "schema": "deeplus.numeric-array-shape-inferred-trace-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "normal_path": "PASS",
        "mutation_count": len(results),
        "rejected_count": rejected_count,
        "results": results,
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
