#!/usr/bin/env python3
"""Validate the R109 integrated local preimplementation handoff."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_P1 = [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
EXPECTED_CLUSTERS = [f"R{index}" for index in range(103, 109)]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_trace_validator(root: Path) -> Any:
    path = root / "tools/validators/validate_implementation_target_traceability.py"
    spec = importlib.util.spec_from_file_location("r109_trace_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("TRACE_VALIDATOR_IMPORT")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pointer_feature_p1(pointer: dict[str, Any]) -> list[str]:
    return [
        row["id"]
        for row in pointer.get("open_actions", [])
        if isinstance(row.get("id"), str)
        and (
            row["id"].startswith("CE-C-P1-")
            or row["id"].startswith("CE-E-P1-")
            or row["id"].startswith("TCC-P1-")
            or row["id"] == "SFD-P1-009"
        )
    ]


def model_errors(
    root: Path,
    contract: dict[str, Any],
    pointer: dict[str, Any],
    r99: dict[str, Any],
    metadata: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    run_trace_validator: bool = True,
) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "deeplus.preimplementation-readiness-integrated-handoff/r109":
        errors.append("CONTRACT_IDENTITY")
    if contract.get("status") != "LOCAL_IMPLEMENTATION_HANDOFF_COMPLETE_PUBLICATION_PENDING_PRODUCT_NOT_RUN":
        errors.append("STATUS_OVERCLAIM")
    if contract.get("baseline") != {
        "repository": "howork/Deeplus",
        "branch": "codex/preimpl-p0-r80-authority-projection-parity",
        "commit": "97ab454afabb38d41db98f8850b14538c50228de",
        "tree": "f788acef944c7c92602db676229858d11a451872",
    }:
        errors.append("BASELINE_IDENTITY")

    bindings = contract.get("cluster_bindings", [])
    if [row.get("cluster") for row in bindings] != EXPECTED_CLUSTERS:
        errors.append("CLUSTER_SET")
    for binding in bindings:
        path = root / binding.get("path", "")
        if not path.is_file() or sha256(path) != binding.get("sha256"):
            errors.append(f"CLUSTER_BINDING:{binding.get('cluster')}")

    target = contract.get("implementation_target", {})
    metadata_path = root / target.get("metadata_path", "")
    rows_path = root / target.get("rows_path", "")
    if sha256(metadata_path) != target.get("metadata_sha256"):
        errors.append("TARGET_METADATA_DIGEST")
    if sha256(rows_path) != target.get("rows_sha256"):
        errors.append("TARGET_ROWS_DIGEST")
    expected_counts = {
        "feature_count": 464,
        "feature_id_list_sha256": "6f7bf3a7f632d452d04d3a59f222f7353568e466f64507ee2418d233a1d50182",
        "stage_cells": 3248,
        "test_outcome_cells": 1392,
        "bound_direct_cells": 3682,
        "bound_delegated_cells": 4,
        "not_applicable_cells": 490,
        "applicable_blocked_cells": 0,
        "missing_cells": 0,
        "conflict_cells": 0,
        "product_not_run_rows": 464,
    }
    if any(target.get(key) != value for key, value in expected_counts.items()):
        errors.append("TARGET_CONTRACT_COUNTS")
    if (
        metadata.get("target_count") != 464
        or metadata.get("target_feature_id_list_sha256") != expected_counts["feature_id_list_sha256"]
        or metadata.get("derived_counts", {}).get("applicable_blocked_cells") != 0
        or metadata.get("derived_counts", {}).get("product_not_run_rows") != 464
        or len(rows) != 464
    ):
        errors.append("TARGET_METADATA_COUNTS")
    if run_trace_validator:
        trace_errors = load_trace_validator(root).validate(root, metadata, rows)
        errors.extend(f"TARGET_TRACE:{item}" for item in trace_errors)

    p1 = contract.get("feature_p1_fence", {})
    if p1.get("exact_open_ids") != EXPECTED_P1 or pointer_feature_p1(pointer) != EXPECTED_P1:
        errors.append("FEATURE_P1_EXACT_SET")
    if p1 != {
        "exact_open_ids": EXPECTED_P1,
        "class_count": 6,
        "enumeration_count": 8,
        "trait_count": 7,
        "sfd_count": 1,
        "closed_by_r109": 0,
        "execution_receipts": "OPEN_NOT_RUN",
    }:
        errors.append("FEATURE_P1_FENCE")

    gates = contract.get("completion_gates", [])
    if [row.get("gate") for row in gates] != [
        "G0_INVENTORY_CLOSURE",
        "G1_SEMANTIC_DESIGN_CLOSURE",
        "G2_IMPLEMENTATION_HANDOFF_CLOSURE",
        "G3_CONFORMANCE_SPECIFICATION_CLOSURE",
        "G4_INDEPENDENT_READINESS_AUDIT",
    ] or [row.get("result") for row in gates] != [
        "PASS_E2_STATIC",
        "PASS_E2_STATIC",
        "PASS_E2_LOCAL",
        "PASS_E2_STATIC",
        "CONDITIONAL_PASS_PUBLICATION_PENDING",
    ]:
        errors.append("COMPLETION_GATES")

    blocker_status = {row.get("id"): row.get("status") for row in contract.get("readiness_blockers", [])}
    if blocker_status != {
        "R99-READY-BLOCK-001": "OPEN_EXTERNAL_PUBLICATION_GATE",
        "R99-READY-BLOCK-002": "CLOSED_BY_R109_INTEGRATED_LOCAL_HANDOFF",
        "R99-READY-BLOCK-003": "CLOSED_BY_R104_EXACT_TARGET_PARTITION",
    }:
        errors.append("CONTRACT_BLOCKER_SET")
    r99_status = {row.get("id"): row.get("status") for row in r99.get("readiness_blockers", [])}
    if r99_status != {
        "R99-READY-BLOCK-001": "OPEN",
        "R99-READY-BLOCK-002": "CLOSED_BY_R109_INTEGRATED_LOCAL_HANDOFF",
        "R99-READY-BLOCK-003": "CLOSED_BY_R104_EXACT_TARGET_PARTITION",
    }:
        errors.append("R99_BLOCKER_SET")

    pointer_lanes = pointer.get("product_lanes", {})
    governance = contract.get("governance", {})
    if len(pointer_lanes) != 15 or set(pointer_lanes.values()) != {"NOT_RUN"}:
        errors.append("PRODUCT_LANES")
    if governance != {
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "bootstrap_readiness_blocker_count": 1,
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_implementation": "NOT_RUN",
        "current_binding": False,
        "github_mutation": 0,
        "canonical_publication": "PENDING_EXPLICIT_USER_AUTHORITY",
    }:
        errors.append("GOVERNANCE_FENCE")
    if pointer.get("candidate_binding", {}).get("current_binding") is not False:
        errors.append("CURRENT_BINDING")
    return errors


def validate_schema(root: Path, contract: dict[str, Any]) -> str:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return "STRICT_STRUCTURAL_FALLBACK"
    schema = read_json(root / "schemas/language/preimplementation-readiness-integrated-handoff-r109.schema.json")
    jsonschema.Draft202012Validator(schema).validate(contract)
    return "JSONSCHEMA_PASS"


def mutation_count(
    root: Path,
    contract: dict[str, Any],
    pointer: dict[str, Any],
    r99: dict[str, Any],
    metadata: dict[str, Any],
    rows: list[dict[str, Any]],
) -> int:
    mutations: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]] = []
    candidate = copy.deepcopy(contract); candidate["cluster_bindings"].pop(); mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["cluster_bindings"][0]["sha256"] = "0" * 64; mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["implementation_target"]["feature_count"] = 463; mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["feature_p1_fence"]["exact_open_ids"].pop(); mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["feature_p1_fence"]["closed_by_r109"] = 1; mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["completion_gates"][-1]["result"] = "PASS_E5_PRODUCT"; mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["governance"]["semantic_p0"] = 1; mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["governance"]["product_lanes"] = "15_OF_15_PASS"; mutations.append((candidate, pointer, metadata, rows))
    candidate = copy.deepcopy(contract); candidate["governance"]["current_binding"] = True; mutations.append((candidate, pointer, metadata, rows))
    changed_metadata = copy.deepcopy(metadata); changed_metadata["derived_counts"]["applicable_blocked_cells"] = 1; mutations.append((contract, pointer, changed_metadata, rows))
    changed_rows = copy.deepcopy(rows); changed_rows.pop(); mutations.append((contract, pointer, metadata, changed_rows))
    changed_pointer = copy.deepcopy(pointer); next(iter(changed_pointer["product_lanes"])); changed_pointer["product_lanes"][next(iter(changed_pointer["product_lanes"]))] = "PASS"; mutations.append((contract, changed_pointer, metadata, rows))
    rejected = sum(bool(model_errors(root, current, current_pointer, r99, current_metadata, current_rows, run_trace_validator=False)) for current, current_pointer, current_metadata, current_rows in mutations)
    if rejected != len(mutations):
        raise ValueError(f"MUTATION_SURVIVED:{rejected}/{len(mutations)}")
    return rejected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = read_json(root / "spec/contracts/preimplementation-readiness-integrated-handoff-r109.json")
    pointer = read_json(root / "current/current-pointer.json")
    r99 = read_json(root / "spec/contracts/implementation-readiness-r99-audit-closure.json")
    metadata = read_json(root / contract["implementation_target"]["metadata_path"])
    rows = read_json(root / contract["implementation_target"]["rows_path"])
    errors: list[str] = []
    schema_result = "NOT_RUN"
    try:
        schema_result = validate_schema(root, contract)
    except Exception as exc:  # schema diagnostics are part of the receipt
        errors.append(f"SCHEMA:{exc}")
    errors.extend(model_errors(root, contract, pointer, r99, metadata, rows))
    rejected = mutation_count(root, contract, pointer, r99, metadata, rows) if args.mutations and not errors else 0
    receipt = {
        "schema": "deeplus.preimplementation-readiness-integrated-handoff-validation/r109",
        "result": "PASS" if not errors else "FAIL",
        "status": contract.get("status"),
        "schema_validation": schema_result,
        "clusters": len(contract.get("cluster_bindings", [])),
        "target_features": len(rows),
        "feature_p1": "22_OPEN_UNCHANGED",
        "readiness_blockers": 1,
        "product_lanes": "15_OF_15_NOT_RUN",
        "mutations_rejected": rejected,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
