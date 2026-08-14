#!/usr/bin/env python3
"""Validate the R99 independent-audit closure and evidence-honesty fence."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_FEATURE_P1 = [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]

REPAIR_VALIDATORS = [
    "validate_parser_scanner_pratt_authority_r99.py",
    "validate_checker_bootstrap_r99.py",
    "validate_measure_collection_bootstrap_r99.py",
    "validate_exact_numeric_operator_allocation_r99.py",
    "validate_runtime_backend_projection_r99.py",
    "validate_implementation_target_feature_p1_disposition_r101.py",
    "validate_implementation_target_feature_local_acceptance_r102.py",
    "validate_implementation_target_feature_p1_disposition_r104.py",
    "validate_trait_conformance_implementation_handoff_r107.py",
    "validate_runtime_managed_projection_handoff_r108.py",
    "validate_preimplementation_readiness_integrated_handoff_r109.py",
    "validate_implementation_target_traceability.py",
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def model_errors(
    root: Path,
    contract: dict[str, Any],
    pointer: dict[str, Any],
    metadata: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "deeplus.implementation-readiness-r99-audit-closure/r1":
        errors.append("CONTRACT_IDENTITY")
    baseline = contract.get("baseline", {})
    if baseline != {
        "repository": "howork/Deeplus",
        "branch": "main",
        "observed_commit": "10e64f492f0529610673846139afcf0d95175663",
        "local_predecessor_commit": "9c5f25e9d1e518c75e594f46b2158c510008c379",
        "current_binding": False,
    }:
        errors.append("BASELINE_IDENTITY")
    if contract.get("readiness_verdict") != (
        "LOCAL_IMPLEMENTATION_HANDOFF_COMPLETE_PUBLICATION_PENDING"
    ):
        errors.append("READINESS_OVERCLAIM")

    historical = contract.get("historical_g4_supersession", {})
    if (
        historical.get("current_interpretation")
        != "SUPERSEDED_BY_R109_LOCAL_HANDOFF_PUBLICATION_PENDING"
        or historical.get("preservation") != "IMMUTABLE_HISTORICAL_EVIDENCE"
        or set(historical.get("prohibited_claims", []))
        != {
            "BOOTSTRAP_UNRESOLVED_P1_ZERO",
            "G4_IMPLEMENTATION_START_PASS",
            "STATIC_E2_EQUALS_PRODUCT_SUPPORT",
        }
        or any(not (root / path).is_file() for path in historical.get("artifacts", []))
    ):
        errors.append("HISTORICAL_G4_SUPERSESSION")

    pointer_binding = pointer.get("candidate_binding", {})
    if pointer_binding.get("current_binding") is not False:
        errors.append("CURRENT_BINDING_MUST_REMAIN_FALSE")
    product_lanes = pointer.get("product_lanes", {})
    if len(product_lanes) != 15 or set(product_lanes.values()) != {"NOT_RUN"}:
        errors.append("PRODUCT_LANES_NOT_RUN")

    pointer_p1 = [
        row.get("id")
        for row in pointer.get("open_actions", [])
        if isinstance(row.get("id"), str)
        and (
            row["id"].startswith("CE-C-P1-")
            or row["id"].startswith("CE-E-P1-")
            or row["id"].startswith("TCC-P1-")
            or row["id"] == "SFD-P1-009"
        )
    ]
    lanes = contract.get("feature_p1_lanes", [])
    lane_ids = [row.get("id") for row in lanes]
    if lane_ids != EXPECTED_FEATURE_P1 or pointer_p1 != EXPECTED_FEATURE_P1:
        errors.append("FEATURE_P1_EXACT_SET")
    for row in lanes[:14]:
        if row != {
            "id": row.get("id"),
            "design_contract_gate": "CLOSED_BY_R104_EXACT_FIRST_TARGET_EXCLUSION",
            "execution_receipt_gate": "OPEN_NOT_RUN",
            "readiness_effect": "EXCLUDED_SUCCESSOR_OBLIGATION_DOES_NOT_BLOCK_RETAINED_FIRST_TARGET_BASE",
        }:
            errors.append(f"FEATURE_P1_LANE:{row.get('id')}")
    for row in lanes[14:21]:
        if row != {
            "id": row.get("id"),
            "design_contract_gate": "CLOSED_BY_R107_ACTION_COMPLETE_IMPLEMENTATION_HANDOFF",
            "execution_receipt_gate": "OPEN_NOT_RUN",
            "readiness_effect": "IMPLEMENTATION_HANDOFF_READY_EXECUTION_REMAINS_OPEN",
        }:
            errors.append(f"FEATURE_P1_LANE:{row.get('id')}")
    if not lanes or lanes[-1] != {
        "id": "SFD-P1-009",
        "design_contract_gate": "CLOSED_DESIGN_STATIC",
        "execution_receipt_gate": "OPEN_NOT_RUN",
        "readiness_effect": "RETAINED_IMPLEMENTATION_ACCEPTANCE_BLOCKS_SFD_EXECUTION_CLAIM_ONLY",
    }:
        errors.append("SFD_P1_LANE")

    blockers = contract.get("readiness_blockers", [])
    if (
        [row.get("id") for row in blockers]
        != ["R99-READY-BLOCK-001", "R99-READY-BLOCK-002", "R99-READY-BLOCK-003"]
        or [row.get("status") for row in blockers]
        != [
            "OPEN",
            "CLOSED_BY_R109_INTEGRATED_LOCAL_HANDOFF",
            "CLOSED_BY_R104_EXACT_TARGET_PARTITION",
        ]
    ):
        errors.append("READINESS_BLOCKER_SET")

    governance = contract.get("governance", {})
    if governance != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_EXACT_TYPED_LANES",
        "bootstrap_readiness_blocker_count": 1,
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_implementation": "NOT_RUN",
        "github_mutation": 0,
        "canonical_publication": "NOT_PERFORMED",
    }:
        errors.append("GOVERNANCE_FENCE")

    local_repairs = contract.get("local_semantic_repairs", [])
    repair_ids = [row.get("id") for row in local_repairs]
    if len(repair_ids) != 20 or len(set(repair_ids)) != 20:
        errors.append("LOCAL_REPAIR_IDENTITY_SET")
    for row in local_repairs:
        if row.get("status") not in {
            "CLOSED_LOCAL_DESIGN_STATIC",
            "EXPLICITLY_DEFERRED_TARGET_EXCLUDED",
            "PARTIAL_STATIC_DISPOSITION_REQUIRES_EXACT_TARGET_TOTALITY",
            "PARTIAL_ACTION_COMPLETE_TCC_R107",
            "CLOSED_BY_R109_INTEGRATED_LOCAL_HANDOFF",
            "CLOSED_BY_R104_EXACT_TARGET_PARTITION",
        } or not (root / row.get("contract", "")).is_file():
            errors.append(f"LOCAL_REPAIR_BINDING:{row.get('id')}")

    if (
        metadata.get("target_count") != 464
        or metadata.get("base_count") != 461
        or metadata.get("negative_compatibility_addition_count") != 2
        or metadata.get("derived_counts", {}).get("applicable_blocked_cells") != 0
        or metadata.get("derived_counts", {}).get("product_not_run_rows") != 464
    ):
        errors.append("TARGET_METADATA_CURRENT_COUNTS")
    return errors


def mutation_count(
    root: Path,
    contract: dict[str, Any],
    pointer: dict[str, Any],
    metadata: dict[str, Any],
) -> int:
    mutants: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    candidate = copy.deepcopy(contract)
    candidate["feature_p1_lanes"].pop()
    mutants.append((candidate, pointer, metadata))
    candidate = copy.deepcopy(contract)
    candidate["feature_p1_lanes"][0]["design_contract_gate"] = "OPEN"
    mutants.append((candidate, pointer, metadata))
    candidate = copy.deepcopy(contract)
    candidate["feature_p1_lanes"][-1]["execution_receipt_gate"] = "CLOSED"
    mutants.append((candidate, pointer, metadata))
    candidate = copy.deepcopy(contract)
    candidate["readiness_verdict"] = "IMPLEMENTATION_READY"
    mutants.append((candidate, pointer, metadata))
    changed_pointer = copy.deepcopy(pointer)
    changed_pointer["candidate_binding"]["current_binding"] = True
    mutants.append((contract, changed_pointer, metadata))
    changed_pointer = copy.deepcopy(pointer)
    first_lane = next(iter(changed_pointer["product_lanes"]))
    changed_pointer["product_lanes"][first_lane] = "PASS"
    mutants.append((contract, changed_pointer, metadata))
    rejected = sum(
        bool(model_errors(root, current, current_pointer, current_metadata))
        for current, current_pointer, current_metadata in mutants
    )
    if rejected != len(mutants):
        raise ValueError(f"MUTATION_SURVIVED:{rejected}/{len(mutants)}")
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = read_json(root / "spec/contracts/implementation-readiness-r99-audit-closure.json")
    pointer = read_json(root / "current/current-pointer.json")
    metadata = read_json(root / "spec/traceability/implementation-target-profile-r1/catalog-metadata.json")
    errors = model_errors(root, contract, pointer, metadata)
    validator_receipts: list[dict[str, Any]] = []
    if not errors:
        for name in REPAIR_VALIDATORS:
            process = subprocess.run(
                [sys.executable, "-B", str(root / "tools/validators" / name), "--root", str(root), "--mutations"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            validator_receipts.append({"validator": name, "result": "PASS" if process.returncode == 0 else "FAIL"})
            if process.returncode != 0:
                errors.append(f"REPAIR_VALIDATOR:{name}:{process.stdout[-1000:]}")
    rejected = mutation_count(root, contract, pointer, metadata) if args.mutations and not errors else 0
    receipt = {
        "schema": "deeplus.implementation-readiness-r99-audit-closure-validation/r1",
        "result": "PASS" if not errors else "FAIL",
        "readiness_verdict": contract.get("readiness_verdict"),
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_EXACT_TYPED_LANES",
        "readiness_blockers": 1,
        "repair_validator_receipts": validator_receipts,
        "mutation_count": rejected,
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
