#!/usr/bin/env python3
"""Focused mutation oracles for the R54 scalar numeric trace overlay."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from validate_scalar_numeric_fixed_operator_trace import OVERLAY_REL, load, validate


Mutation = tuple[str, Callable[[dict[str, Any]], None]]


def guard_key(guards: dict[str, Any], *candidates: str) -> str:
    for candidate in candidates:
        if candidate in guards:
            return candidate
    raise KeyError(candidates[0])


def wrong_locator(entry: dict[str, Any]) -> None:
    kind = entry.get("locator_kind")
    if kind == "FILE":
        entry["locator"] = "__missing_file_locator__"
    elif kind == "JSON_POINTER":
        entry["locator"] = "/__missing_json_pointer__"
    else:
        entry["locator"] = "__MISSING_REGISTRY_ID__"


def set_guard(candidate: dict[str, Any], value: Any, *names: str) -> None:
    guards = candidate["guards"]
    guards[guard_key(guards, *names)] = value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--overlay", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overlay_path = args.overlay.resolve() if args.overlay else root / OVERLAY_REL
    try:
        baseline = load(overlay_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"result": "FAIL", "errors": [f"LOAD:{type(exc).__name__}:{exc}"]}, indent=2))
        return 1

    normal_errors = validate(root, baseline, validate_schema=args.overlay is None)
    if normal_errors:
        print(
            json.dumps(
                {
                    "schema": "deeplus.scalar-numeric-fixed-operator-trace-mutation-receipt/r1",
                    "result": "FAIL",
                    "phase": "NORMAL_PATH",
                    "errors": normal_errors,
                    "product_execution": "15_OF_15_NOT_RUN",
                },
                indent=2,
            )
        )
        return 1

    mutations: list[Mutation] = [
        ("FEATURE_OMISSION", lambda value: value["feature_ids"].pop()),
        ("FEATURE_EXTRA", lambda value: value["feature_ids"].append("invented_numeric_feature")),
        ("BINDING_OMISSION", lambda value: value["bindings"].pop()),
        ("WRONG_EXISTING_LOCATOR", lambda value: wrong_locator(value["evidence_entries"][0])),
        ("WRONG_BINDING_FEATURE", lambda value: value["bindings"][0].__setitem__("feature_id", "invented_numeric_feature")),
        ("WRONG_BINDING_OUTCOME", lambda value: value["bindings"][0].__setitem__("outcome", "REJECT" if value["bindings"][0]["outcome"] is None else None)),
        ("WRONG_BINDING_STAGE", lambda value: value["bindings"][0].__setitem__("stage", "TOOLING_OBLIGATIONS")),
        ("UNKNOWN_EVIDENCE_KEY", lambda value: value["bindings"][0]["evidence_keys"].append("EVK-UNKNOWN")),
        ("COUNT_DRIFT", lambda value: value["counts"].__setitem__("binding_count", 39)),
        ("STATUS_DRIFT", lambda value: set_guard(value, "CHANGED", "feature_statuses")),
        ("ACTIVATION_DRIFT", lambda value: set_guard(value, "CHANGED", "source_activation")),
        ("FLOAT_IDENTITY", lambda value: set_guard(value, 1, "float_distinct_identity_count")),
        ("UINT_CONFLATION", lambda value: set_guard(value, True, "uint_alias_of_uint64")),
        ("UINT_STORAGE_IDENTITY", lambda value: set_guard(value, True, "uint_storage_or_abi_identity_selected")),
        ("CUSTOM_OPERATOR", lambda value: set_guard(value, 1, "arbitrary_custom_operator_count")),
        ("RUNTIME_LOOKUP", lambda value: set_guard(value, 1, "runtime_operator_lookup_count")),
        ("PRODUCT_PASS", lambda value: set_guard(value, "15_OF_15_PASS", "product_lanes")),
        ("GITHUB_ENABLED", lambda value: set_guard(value, "ENABLED", "github_publication")),
        ("IR_XCUT_CLOSURE_OVERCLAIM", lambda value: value.__setitem__("candidate_status", "IR-XCUT-P1-054_CLOSED")),
        (
            "DELEGATE_TARGET_DRIFT",
            lambda value: next(
                row for row in value["bindings"] if row["disposition"] == "BOUND_DELEGATED"
            ).__setitem__("delegate_feature_id", "numeric_operator_core"),
        ),
        (
            "NA_REASON_DRIFT",
            lambda value: next(
                row for row in value["bindings"] if row["disposition"] == "NOT_APPLICABLE"
            )["not_applicable"].__setitem__("reason_code", "UNREGISTERED_REASON"),
        ),
        (
            "ACCEPTANCE_COVERAGE_OMISSION",
            lambda value: value["acceptance_cases"].__setitem__(
                slice(None),
                [
                    row
                    for row in value["acceptance_cases"]
                    if not (
                        row["feature_id"] == value["acceptance_cases"][0]["feature_id"]
                        and row["outcome"] == value["acceptance_cases"][0]["outcome"]
                    )
                ],
            ),
        ),
        ("ACCEPTANCE_PRODUCT_OVERCLAIM", lambda value: value["acceptance_cases"][0].__setitem__("execution_state", "PASS")),
    ]

    results: list[dict[str, Any]] = []
    for mutation_id, mutate in mutations:
        candidate = copy.deepcopy(baseline)
        try:
            mutate(candidate)
            errors = validate(root, candidate, validate_schema=False)
        except (KeyError, IndexError, StopIteration, TypeError) as exc:
            errors = [f"MUTATION_SETUP:{type(exc).__name__}:{exc}"]
        results.append(
            {
                "mutation_id": mutation_id,
                "rejected": bool(errors) and not errors[0].startswith("MUTATION_SETUP:"),
                "first_error": errors[0] if errors else None,
            }
        )

    rejected = sum(row["rejected"] for row in results)
    passed = rejected == len(results)
    print(
        json.dumps(
            {
                "schema": "deeplus.scalar-numeric-fixed-operator-trace-mutation-receipt/r1",
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
