#!/usr/bin/env python3
"""Focused mutation oracles for the R55 lexical-trivia/source-root overlay."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_lexical_trivia_source_root_trace import CONTRACT_REL, OVERLAY_REL, load, validate


Mutation = tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]]


def wrong_locator(entry: dict[str, Any]) -> None:
    if entry.get("locator_kind") == "JSON_POINTER":
        entry["locator"] = "/__missing_json_pointer__"
    elif entry.get("locator_kind") == "FILE":
        entry["locator"] = "__missing_file_locator__"
    else:
        entry["locator"] = "__MISSING_REGISTRY_ID__"


def first_binding(overlay: dict[str, Any], disposition: str) -> dict[str, Any]:
    return next(row for row in overlay["bindings"] if row["disposition"] == disposition)


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
        print(
            json.dumps(
                {
                    "schema": "deeplus.lexical-trivia-source-root-trace-mutation-receipt/r1",
                    "result": "FAIL",
                    "phase": "NORMAL_PATH",
                    "errors": normal_errors,
                    "product_execution": "15_OF_15_NOT_RUN",
                    "github_publication": "SUSPENDED",
                },
                indent=2,
            )
        )
        return 1

    mutations: list[Mutation] = [
        ("FEATURE_OMISSION", lambda overlay, contract: overlay["feature_ids"].pop()),
        ("FEATURE_EXTRA", lambda overlay, contract: overlay["feature_ids"].append("invented_lexical_feature")),
        ("BINDING_OMISSION", lambda overlay, contract: overlay["bindings"].pop()),
        ("EVIDENCE_OMISSION", lambda overlay, contract: overlay["evidence_entries"].pop()),
        ("WRONG_EXISTING_LOCATOR", lambda overlay, contract: wrong_locator(overlay["evidence_entries"][0])),
        (
            "WRONG_BINDING_FEATURE",
            lambda overlay, contract: overlay["bindings"][0].__setitem__("feature_id", "invented_lexical_feature"),
        ),
        (
            "WRONG_BINDING_STAGE",
            lambda overlay, contract: overlay["bindings"][0].__setitem__("stage", "TOOLING_OBLIGATIONS"),
        ),
        (
            "UNKNOWN_EVIDENCE_KEY",
            lambda overlay, contract: overlay["bindings"][0].__setitem__("evidence_keys", ["R55:UNKNOWN"]),
        ),
        (
            "DIRECT_TO_DELEGATED",
            lambda overlay, contract: first_binding(overlay, "BOUND_DIRECT").update(
                {"disposition": "BOUND_DELEGATED", "delegate_feature_id": "word_comment_lossless_trivia"}
            ),
        ),
        (
            "NA_TO_DIRECT",
            lambda overlay, contract: first_binding(overlay, "NOT_APPLICABLE").update(
                {"disposition": "BOUND_DIRECT", "not_applicable": None}
            ),
        ),
        (
            "NA_REASON_DRIFT",
            lambda overlay, contract: first_binding(overlay, "NOT_APPLICABLE")["not_applicable"].__setitem__(
                "reason_code", "UNREGISTERED_REASON"
            ),
        ),
        ("COUNT_DRIFT", lambda overlay, contract: overlay["counts"].__setitem__("binding_count", 37)),
        ("ACCEPTANCE_CASE_OMISSION", lambda overlay, contract: overlay["acceptance_cases"].pop()),
        (
            "ACCEPTANCE_PRODUCT_OVERCLAIM",
            lambda overlay, contract: overlay["acceptance_cases"][0].__setitem__("execution_state", "PASS"),
        ),
        ("CANONICAL_BASELINE_DRIFT", lambda overlay, contract: overlay.__setitem__("canonical_baseline_commit", "0" * 40)),
        ("PREDECESSOR_DRIFT", lambda overlay, contract: overlay.__setitem__("local_predecessor_commit", "0" * 40)),
        ("PRODUCT_PASS", lambda overlay, contract: overlay["guards"].__setitem__("product_lanes", "15_OF_15_PASS")),
        ("GITHUB_ENABLED", lambda overlay, contract: overlay["guards"].__setitem__("github_publication", "ENABLED")),
        ("SEMANTIC_P0_DRIFT", lambda overlay, contract: overlay["guards"].__setitem__("semantic_p0", 1)),
        ("CONTRACT_CASE_OMISSION", lambda overlay, contract: contract["new_acceptance_cases"].pop()),
        ("CONTRACT_CASE_COUNT_DRIFT", lambda overlay, contract: contract.__setitem__("new_acceptance_case_count", 9)),
        (
            "CONTRACT_CASE_OUTCOME_DRIFT",
            lambda overlay, contract: contract["new_acceptance_cases"][0].__setitem__("outcome", "REJECT"),
        ),
        (
            "COMMENT_PRIORITY_DRIFT",
            lambda overlay, contract: contract["comment_opener_priority"]["ordered_openers"].reverse(),
        ),
        (
            "WORD_SCALAR_DOMAIN_DRIFT",
            lambda overlay, contract: contract["word_comment"].__setitem__("scanner_primitive_exact_domain", "ANY_UNICODE_SCALAR"),
        ),
        (
            "WORD_SEMANTIC_EFFECT",
            lambda overlay, contract: contract["word_comment"].__setitem__("semantic_effect_count", 1),
        ),
        (
            "SOURCE_ROOT_OMISSION",
            lambda overlay, contract: contract["source_root_consumption"]["direct_roots"].pop(),
        ),
        (
            "SOURCE_ROOT_EOF_DRIFT",
            lambda overlay, contract: contract["source_root_consumption"].__setitem__("required_terminal", "EOF"),
        ),
        (
            "CONTRACT_SURFACE_CHANGE",
            lambda overlay, contract: contract.__setitem__("surface_change_count", 1),
        ),
        (
            "CONTRACT_PRODUCT_PASS",
            lambda overlay, contract: contract["governance"].__setitem__("product_lanes", "15_OF_15_PASS"),
        ),
        (
            "CONTRACT_GITHUB_ENABLED",
            lambda overlay, contract: contract["governance"].__setitem__("github_publication", "ENABLED"),
        ),
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
        results.append(
            {
                "mutation_id": mutation_id,
                "rejected": bool(errors) and not errors[0].startswith("MUTATION_SETUP:"),
                "first_error": errors[0] if errors else None,
            }
        )

    rejected_count = sum(row["rejected"] for row in results)
    passed = rejected_count == len(results)
    print(
        json.dumps(
            {
                "schema": "deeplus.lexical-trivia-source-root-trace-mutation-receipt/r1",
                "result": "PASS" if passed else "FAIL",
                "normal_path": "PASS",
                "mutation_count": len(results),
                "rejected_count": rejected_count,
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
