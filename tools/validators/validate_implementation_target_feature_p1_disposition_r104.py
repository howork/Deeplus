#!/usr/bin/env python3
"""Validate the exact R104 first-target partition for all 22 feature-P1 actions."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path("spec/contracts/implementation-target-feature-p1-disposition-r104.json")
SCHEMA = Path("schemas/language/implementation-target-feature-p1-disposition-r104.schema.json")
R101 = Path("spec/contracts/implementation-target-feature-p1-disposition-r101.json")
R102 = Path("spec/contracts/implementation-target-feature-local-acceptance-r102.json")
R99 = Path("spec/contracts/implementation-readiness-r99-audit-closure.json")
POINTER = Path("current/current-pointer.json")
METADATA = Path("spec/traceability/implementation-target-profile-r1/catalog-metadata.json")
ROWS = Path("spec/traceability/implementation-target-profile-r1/rows.json")

ACTION_IDS = [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]


def load(root: Path, relative: Path) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_ids(values: list[str]) -> str:
    return hashlib.sha256(("\n".join(values) + "\n").encode("utf-8")).hexdigest()


def model_errors(root: Path, docs: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    contract = docs["contract"]
    r101 = docs["r101"]
    r102 = docs["r102"]
    r99 = docs["r99"]
    pointer = docs["pointer"]
    metadata = docs["metadata"]
    rows = docs["rows"]

    if (
        contract.get("schema") != "deeplus.implementation-target-feature-p1-disposition/r104"
        or contract.get("revision") != "r104-exact-first-target-obligation-partition"
        or contract.get("status") != "LOCAL_DESIGN_STATIC_EXACT_TARGET_PARTITION"
        or contract.get("baseline", {}).get("current_binding") is not False
    ):
        errors.append("CONTRACT_IDENTITY")
    for key, relative in (("r101", R101), ("r102", R102)):
        binding = contract.get("predecessors", {}).get(key, {})
        if (
            binding.get("path") != relative.as_posix()
            or binding.get("sha256") != sha256(root / relative)
        ):
            errors.append(f"PREDECESSOR_BINDING:{key}")

    obligations = contract.get("obligations", [])
    if [row.get("action_id") for row in obligations] != ACTION_IDS:
        errors.append("ACTION_COVERAGE_OR_ORDER")
        return errors
    if len({row.get("obligation_id") for row in obligations}) != 22:
        errors.append("OBLIGATION_ID_UNIQUE")
    r101_actions = r101.get("actions", [])
    r102_by_id = {row.get("action_id"): row for row in r102.get("actions", [])}
    pointer_by_id = {
        row.get("id"): row for row in pointer.get("open_actions", [])
        if row.get("id") in ACTION_IDS
    }
    if set(pointer_by_id) != set(ACTION_IDS):
        errors.append("POINTER_OPEN_ACTION_COVERAGE")
    target_ids = {row.get("feature_id") for row in rows}
    retained_ids: set[str] = set()
    excluded_catalog_ids: set[str] = set()
    for index, (row, predecessor) in enumerate(zip(obligations, r101_actions)):
        action_id = ACTION_IDS[index]
        excluded = index < 14
        expected_disposition = (
            "EXCLUDE_SUCCESSOR_OBLIGATION_RETAIN_CURRENT_BASE"
            if excluded else "INCLUDE_FEATURE_LOCAL_ACCEPTANCE"
        )
        if (
            predecessor.get("id") != action_id
            or row.get("obligation_id") != f"ImplementationObligationId:{action_id}/r104"
            or row.get("predecessor_pointer") != f"/actions/{index}"
            or row.get("first_target_disposition") != expected_disposition
            or row.get("closure_source_pointer")
            != f"current/current-pointer.json#/open_actions/{index + 5}"
            or row.get("execution_receipt_gate") != "OPEN_NOT_RUN"
            or not pointer_by_id.get(action_id, {}).get("acceptance_test")
        ):
            errors.append(f"OBLIGATION_ROW:{action_id}")
        retained = set(predecessor.get("retained_feature_ids", []))
        excluded_features = set(predecessor.get("excluded_target_feature_ids", []))
        retained_ids.update(retained)
        excluded_catalog_ids.update(excluded_features)
        if not retained or retained - target_ids or excluded_features & target_ids:
            errors.append(f"TARGET_FEATURE_PARTITION:{action_id}")
        if excluded:
            if row.get("acceptance_pointer_or_null") is not None:
                errors.append(f"EXCLUDED_ACCEPTANCE_POINTER:{action_id}")
        else:
            acceptance = r102_by_id.get(action_id, {})
            if (
                row.get("acceptance_pointer_or_null")
                != "spec/contracts/implementation-target-feature-local-acceptance-r102.json"
                f"#/actions/{index - 14}"
                or set(acceptance.get("retained_target_feature_ids", [])) != retained
                or acceptance.get("handoff_specification_gate")
                != "CLOSED_FEATURE_LOCAL_SPECIFICATION"
                or acceptance.get("execution_receipt_gate") != "OPEN_NOT_RUN"
            ):
                errors.append(f"INCLUDED_ACCEPTANCE_POINTER:{action_id}")

    expected_summary = {
        "exact_action_count": 22,
        "excluded_successor_obligation_count": 14,
        "included_acceptance_obligation_count": 8,
        "design_partition_open_count": 0,
        "execution_open_not_run_count": 22,
        "closed_feature_p1_count": 0,
        "new_feature_p1_count": 0,
    }
    if contract.get("summary") != expected_summary:
        errors.append("SUMMARY")
    if contract.get("acceptance") != {
        "exact_action_identity_coverage": 22,
        "duplicate_or_unmapped_action_count": 0,
        "empty_target_partition_count": 0,
        "retained_current_feature_reinvention_count": 0,
        "excluded_obligation_catalog_alias_count": 0,
        "dependency_cycle_count": 0,
        "execution_receipt_claim_count": 0,
    }:
        errors.append("ACCEPTANCE_FENCE")
    if contract.get("governance") != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_implementation": "NOT_RUN",
        "github_mutation": 0,
        "canonical_publication": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE")

    projection = metadata.get("governance", {}).get("r104_feature_p1_disposition", {})
    expected_projection = {
        "contract_path": CONTRACT.as_posix(),
        "contract_sha256": sha256(root / CONTRACT),
        "exact_action_ids": ACTION_IDS,
        "implementation_obligation_ids": [row["obligation_id"] for row in obligations],
        "action_count": 22,
        "excluded_successor_obligation_count": 14,
        "included_acceptance_obligation_count": 8,
        "design_partition_open_count": 0,
        "execution_open_action_count": 22,
        "retained_target_feature_ids": sorted(retained_ids),
        "retained_target_feature_id_list_sha256": digest_ids(sorted(retained_ids)),
        "excluded_catalog_feature_ids": sorted(excluded_catalog_ids),
        "excluded_catalog_feature_id_list_sha256": digest_ids(sorted(excluded_catalog_ids)),
    }
    if projection != expected_projection:
        errors.append("METADATA_PROJECTION")

    lanes = r99.get("feature_p1_lanes", [])
    if [row.get("id") for row in lanes] != ACTION_IDS:
        errors.append("R99_ACTION_SET")
    for row in lanes[:14]:
        if (
            row.get("design_contract_gate") != "CLOSED_BY_R104_EXACT_FIRST_TARGET_EXCLUSION"
            or row.get("execution_receipt_gate") != "OPEN_NOT_RUN"
            or row.get("readiness_effect")
            != "EXCLUDED_SUCCESSOR_OBLIGATION_DOES_NOT_BLOCK_RETAINED_FIRST_TARGET_BASE"
        ):
            errors.append(f"R99_CE_LANE:{row.get('id')}")
    blockers = {row.get("id"): row for row in r99.get("readiness_blockers", [])}
    if (
        r99.get("readiness_verdict")
        != "LOCAL_IMPLEMENTATION_HANDOFF_COMPLETE_PUBLICATION_PENDING"
        or r99.get("governance", {}).get("bootstrap_readiness_blocker_count") != 1
        or blockers.get("R99-READY-BLOCK-003", {}).get("status")
        != "CLOSED_BY_R104_EXACT_TARGET_PARTITION"
    ):
        errors.append("R99_SUCCESSOR_STATE")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    docs = {
        "contract": load(root, CONTRACT),
        "r101": load(root, R101),
        "r102": load(root, R102),
        "r99": load(root, R99),
        "pointer": load(root, POINTER),
        "metadata": load(root, METADATA),
        "rows": load(root, ROWS),
    }
    errors = model_errors(root, docs)
    rejected = 0
    mutation_total = 0
    if args.mutations and not errors:
        mutations: list[dict[str, Any]] = []
        for mutate in range(10):
            candidate = copy.deepcopy(docs)
            if mutate == 0:
                candidate["contract"]["obligations"].pop()
            elif mutate == 1:
                candidate["contract"]["obligations"][1]["obligation_id"] = candidate["contract"]["obligations"][0]["obligation_id"]
            elif mutate == 2:
                candidate["contract"]["obligations"][0]["first_target_disposition"] = "INCLUDE_FEATURE_LOCAL_ACCEPTANCE"
            elif mutate == 3:
                candidate["contract"]["obligations"][14]["acceptance_pointer_or_null"] = None
            elif mutate == 4:
                candidate["contract"]["obligations"][0]["execution_receipt_gate"] = "CLOSED"
            elif mutate == 5:
                candidate["rows"].append({"feature_id": "enum_exact_variant_subset_alias_preview_design"})
            elif mutate == 6:
                candidate["r102"]["actions"][0]["retained_target_feature_ids"] = []
            elif mutate == 7:
                candidate["pointer"]["open_actions"].pop(5)
            elif mutate == 8:
                candidate["r99"]["readiness_blockers"][2]["status"] = "OPEN"
            else:
                candidate["contract"]["governance"]["product_lanes"] = "PASS"
            mutations.append(candidate)
        mutation_total = len(mutations)
        rejected = sum(bool(model_errors(root, value)) for value in mutations)
        if rejected != mutation_total:
            errors.append("MUTATION_SURVIVED")
    receipt = {
        "schema": "deeplus.implementation-target-feature-p1-disposition-validation/r104",
        "result": "PASS" if not errors else "FAIL",
        "exact_action_count": 22,
        "excluded_successor_obligation_count": 14,
        "included_acceptance_obligation_count": 8,
        "execution_open_not_run_count": 22,
        "mutation_rejections": rejected,
        "mutation_total": mutation_total,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
