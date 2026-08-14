#!/usr/bin/env python3
"""Run bounded mutations for Actor Sender Identity V1."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from validate_actor_sender_identity_v1 import (
    CONTRACT, FIXTURE, MIR_SCHEMA, load, validate,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    baseline = validate(root)
    if baseline:
        print(json.dumps({"result": "BLOCKED_BASELINE", "errors": baseline}, separators=(",", ":")))
        return 1

    contract = load(root / CONTRACT)
    fixture = load(root / FIXTURE)
    mir = load(root / MIR_SCHEMA)
    mutations: list[tuple[str, dict[str, object]]] = []

    def mutate_contract(name: str, fn) -> None:
        value = copy.deepcopy(contract)
        fn(value)
        mutations.append((name, {CONTRACT: value}))

    mutate_contract("DROP_EXECUTION_VARIANT", lambda x: x["identity_domain"].update(variants=["Actor(ActorInstanceId)"]))
    mutate_contract("REVERSE_PRECEDENCE", lambda x: x["selection"].update(precedence=["OTHERWISE_CURRENT_EXECUTION", "ACTIVE_ACTOR_TURN_USES_ACTOR_INSTANCE"]))
    mutate_contract("CHILD_INHERITS_ACTOR", lambda x: x["selection"].update(structured_child_inherits_actor_turn=True))
    mutate_contract("SEND_TIME_ALLOCATION", lambda x: x["identity_domain"].update(send_time_identity_allocation_count=1))
    mutate_contract("SERIALIZATION_IDENTITY", lambda x: x["identity_domain"].update(serialization_or_abi_identity=True))
    mutate_contract("SUSPEND_REPLACES", lambda x: x["lifetime"].update(actor_suspend_resume="NEW_SENDER"))
    mutate_contract("RESTART_REUSES", lambda x: x["lifetime"].update(actor_restart="REUSE_SENDER"))
    mutate_contract("CHANNEL_NON_INJECTIVE", lambda x: x["channel_binding"].update(channel_id_derivation="HASH_TRUNCATED"))

    wrong_fixture = copy.deepcopy(fixture)
    wrong_fixture["cases"][0]["descriptor"]["proposed_sender_kind"] = "EXECUTION"
    mutations.append(("ACTOR_CASE_EXECUTION_SENDER", {FIXTURE: wrong_fixture}))

    wrong_mir = copy.deepcopy(mir)
    def clear_annotations(value):
        if isinstance(value, dict):
            value.pop("x-deeplus-semantic-domain", None)
            for child in value.values():
                clear_annotations(child)
        elif isinstance(value, list):
            for child in value:
                clear_annotations(child)
    clear_annotations(wrong_mir)
    mutations.append(("DROP_MIR_DOMAIN", {MIR_SCHEMA: wrong_mir}))

    results = []
    for mutation_id, overrides in mutations:
        errors = validate(root, overrides)
        results.append({"mutation_id": mutation_id, "rejected": bool(errors), "errors": errors[:4]})
    passed = all(row["rejected"] for row in results)
    print(json.dumps({
        "schema": "deeplus.actor-sender-identity-mutation-receipt/r1",
        "result": "PASS" if passed else "FAIL",
        "declared": len(mutations),
        "rejected": sum(row["rejected"] for row in results),
        "results": results,
        "product_execution": "NOT_RUN",
    }, ensure_ascii=False, separators=(",", ":")))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
