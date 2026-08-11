#!/usr/bin/env python3
"""Reject bounded ActorTransportAllocationPlanV1 drift."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from validate_actor_transport_allocation_v1 import CONTRACT_REL, FIXTURE_REL, load, validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)
    mutations: list[tuple[str, dict, dict]] = []

    changed = copy.deepcopy(contract)
    changed["surface_responsibility"]["throws"] = []
    mutations.append(("ALLOCATION_ERROR_DROPPED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["surface_responsibility"]["effects"] = []
    mutations.append(("ALLOCATE_EFFECT_DROPPED", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["profiles"]["logical_unbounded_v1"] = "RESOURCE_EXHAUSTION_IS_MAILBOX_FULL"
    mutations.append(("LOGICAL_UNBOUNDED_CONVERTS_MAILBOX_FULL", changed, fixture))

    changed = copy.deepcopy(contract)
    order = changed["transaction"]["order"]
    order[4], order[5] = order[5], order[4]
    mutations.append(("ALLOCATE_BEFORE_CAPACITY_CHECK", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["transaction"]["failure"]["message_publish_count"] = 1
    mutations.append(("ALLOCATION_FAILURE_PUBLISHES_MESSAGE", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["transaction"]["failure"]["ownership_commit_count"] = 1
    mutations.append(("ALLOCATION_FAILURE_COMMITS_OWNER", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["transaction"]["commit"]["postcommit_allocation_count"] = 1
    mutations.append(("POSTCOMMIT_ALLOCATION", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["mir_contract"]["error_successor"] = "NORMAL"
    mutations.append(("ALLOCATION_ERROR_NORMALIZED_TO_RESULT", changed, fixture))

    changed = copy.deepcopy(contract)
    changed["governance"]["product_lanes"] = "15_OF_15_PASS"
    mutations.append(("PRODUCT_PASS_OVERCLAIM", changed, fixture))

    results = []
    for name, candidate_contract, candidate_fixture in mutations:
        errors = validate(root, contract_override=candidate_contract, fixture_override=candidate_fixture, validate_schema=False)
        results.append({"mutation": name, "result": "REJECTED" if errors else "MISSED", "error_count": len(errors)})
    missed = [row["mutation"] for row in results if row["result"] == "MISSED"]
    print(json.dumps({
        "schema": "deeplus.actor-transport-allocation-mutation-receipt/r1",
        "result": "PASS" if not missed else "FAIL",
        "mutation_count": len(results),
        "rejected_count": len(results) - len(missed),
        "results": results,
        "missed": missed,
    }, indent=2))
    return 0 if not missed else 1


if __name__ == "__main__":
    sys.exit(main())
