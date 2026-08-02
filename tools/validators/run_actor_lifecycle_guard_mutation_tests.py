#!/usr/bin/env python3
"""Exercise the exact Actor lifecycle first-failure guard partition in memory."""

from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import json
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"ACTOR_LIFECYCLE_GUARD_MUTATION_FAIL: {message}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_validator(root: Path):
    path = root / "tools/validators/validate_actor_minimum_lifecycle.py"
    spec = importlib.util.spec_from_file_location("deeplus_actor_lifecycle_validator", path)
    if spec is None or spec.loader is None:
        fail("cannot load lifecycle validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def mutate(row: dict, mutation_id: str) -> None:
    events = row["events"]
    if mutation_id == "orphan_binding_foreign_key":
        events[0]["binding_id"] = "binding-orphan-r51"
    elif mutation_id == "collide_static_and_instance_identity":
        row["actor_instance_id"] = row["static_actor_id"]
    elif mutation_id == "duplicate_queued_payload_cleanup":
        index = next(i for i, event in enumerate(events) if event.get("phase") == "queued_payload_cleaned")
        events.insert(index + 1, copy.deepcopy(events[index]))
    elif mutation_id == "mismatch_reply_responsibility":
        event = next(event for event in events if event.get("phase") == "reply_terminal")
        event["responsibility_id"] = "responsibility-r51-mismatch"
    elif mutation_id == "remove_reply_terminal":
        row["events"] = [event for event in events if event.get("phase") != "reply_terminal"]
    elif mutation_id == "remove_actor_state_cleanup":
        row["events"] = [
            event for event in events if event.get("phase") != "actor_state_cleanup_completed"
        ]
    elif mutation_id == "reverse_required_creation_cleanup_order":
        indexes = [
            i for i, event in enumerate(events) if event.get("phase") == "initialized_resource_cleaned"
        ]
        if len(indexes) != 2:
            fail("creation cleanup mutation requires exactly two cleanup events")
        events[indexes[0]], events[indexes[1]] = events[indexes[1]], events[indexes[0]]
    else:
        fail(f"unknown mutation_id {mutation_id}")


def declared_guards(validator_path: Path) -> set[str]:
    tree = ast.parse(validator_path.read_text(encoding="utf-8"))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("ACTOR_LIFECYCLE_")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    module, validator_path = load_validator(root)
    matrix = load_json(root / "tests/conformance/actor-lifecycle-guards-r1.json")
    fixtures = load_json(root / "tests/fixtures/current/actor-concurrency-coherence-r1.json")
    fixture_rows = {row["fixture_id"]: row for row in fixtures["actor_lifecycle_binding_cases"]}

    observed_rows: list[dict] = []
    direct_guards: set[str] = set()
    mutation_guards: set[str] = set()

    for item in matrix["direct_guards"]:
        row = fixture_rows[item["base_fixture_id"]]
        observed = module.first_failure(row)
        expected = item["expected_first_failure"]
        if observed != expected:
            fail(f"{item['test_id']} expected {expected}, observed {observed}")
        direct_guards.add(expected)
        observed_rows.append({**item, "observed_first_failure": observed, "pass": True})

    for item in matrix["mutation_guards"]:
        base = fixture_rows[item["base_fixture_id"]]
        if module.first_failure(base) is not None:
            fail(f"{item['test_id']} base fixture is not admitted")
        row = copy.deepcopy(base)
        mutate(row, item["mutation_id"])
        observed = module.first_failure(row)
        expected = item["expected_first_failure"]
        if observed != expected:
            fail(f"{item['test_id']} expected {expected}, observed {observed}")
        if module.first_failure(base) is not None:
            fail(f"{item['test_id']} mutated its base fixture")
        mutation_guards.add(expected)
        observed_rows.append({**item, "observed_first_failure": observed, "pass": True})

    declared = declared_guards(validator_path)
    acceptance = matrix["machine_acceptance"]
    if (
        len(declared) != acceptance["declared_guard_count"]
        or len(direct_guards) != acceptance["direct_guard_count"]
        or len(mutation_guards) != acceptance["mutation_guard_count"]
        or direct_guards & mutation_guards
        or direct_guards | mutation_guards != declared
    ):
        fail("declared/direct/mutation guard partition drift")

    receipt = {
        "schema": "deeplus.r51-actor-lifecycle-guard-mutation-receipt/r1",
        "guard_count": len(declared),
        "direct_guard_count": len(direct_guards),
        "mutation_guard_count": len(mutation_guards),
        "uncovered_guard_count": len(declared - direct_guards - mutation_guards),
        "base_immutability": True,
        "runtime_execution": "NOT_RUN",
        "product_execution": "NOT_RUN",
        "rows": observed_rows,
    }
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "ACTOR_LIFECYCLE_GUARD_MUTATION_PASS: "
            "guards=12 direct=5 mutation=7 uncovered=0 product=NOT_RUN"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
