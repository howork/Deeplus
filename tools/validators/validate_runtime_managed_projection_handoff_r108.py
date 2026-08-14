#!/usr/bin/env python3
"""Validate the R108 runtime/managed-reference implementation handoff."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable


CONTRACT_REL = Path("spec/contracts/runtime-managed-projection-handoff-r108.json")
FIXTURE_REL = Path("tests/fixtures/current/runtime-managed-projection-handoff-r108.json")
SCHEMA_REL = Path("schemas/language/runtime-managed-projection-handoff-r108.schema.json")
GENERATOR_REL = Path("tools/generators/generate_runtime_managed_projection_handoff_r108.py")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_generator(root: Path) -> Any:
    spec = importlib.util.spec_from_file_location("r108_generator", root / GENERATOR_REL)
    if spec is None or spec.loader is None:
        raise RuntimeError("R108_GENERATOR_IMPORT")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_documents(contract: dict[str, Any], fixture: dict[str, Any], expected_contract: dict[str, Any], expected_fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(contract.get("schema") == "deeplus.runtime-managed-projection-handoff/r108", "CONTRACT_IDENTITY")
    require(contract.get("revision") == "r108-runtime-managed-projection-implementation-handoff", "CONTRACT_REVISION")
    require(contract.get("baseline") == expected_contract.get("baseline"), "BASELINE_BINDING")
    require(contract.get("source_bindings") == expected_contract.get("source_bindings"), "SOURCE_BINDINGS")

    managed = contract.get("managed_native_abi", {})
    handle = managed.get("managed_handle_abi", {})
    root_slot = managed.get("managed_root_slot_abi", {})
    frame = managed.get("shadow_root_frame_abi", {})
    registry = managed.get("runtime_root_registry", {})
    require(
        handle.get("size_bytes") == 40
        and handle.get("alignment_bytes") == 8
        and [row.get("offset") for row in handle.get("fields", [])] == [0, 8, 16, 24, 32]
        and [row.get("name") for row in handle.get("fields", [])] == ["generation", "state", "referent", "trace_descriptor_id", "cleanup_state"],
        "MANAGED_HANDLE_LAYOUT",
    )
    require(
        handle.get("generation_rule") == "increment before FREE slot reuse; U64 overflow permanently retires the slot",
        "GENERATION_RULE",
    )
    require(
        root_slot.get("size_bytes") == 24
        and [row.get("offset") for row in root_slot.get("fields", [])] == [0, 8, 16]
        and frame.get("header_size_bytes") == 24
        and frame.get("trailing_slot_abi_id") == root_slot.get("abi_id"),
        "SHADOW_ROOT_LAYOUT",
    )
    require(
        registry.get("partitions") == ["RUNNING", "FRAME", "RUNTIME"]
        and registry.get("implicit_backend_root_count") == 0
        and "generation equals expected_generation" in registry.get("scan_rule", ""),
        "ROOT_REGISTRY",
    )
    require(
        managed.get("safepoint_helpers") == ["RuntimeHelperId:managed.safepoint_enter", "RuntimeHelperId:managed.safepoint_leave"]
        and managed.get("implicit_backend_safepoint_count") == 0,
        "SAFEPOINT_FENCE",
    )

    projections = contract.get("target_projections", [])
    require(len(projections) == 3 and [row.get("module_kind") for row in projections] == ["Xvm", "ObjectAot", "InMemoryJit"], "TARGET_CARDINALITY")
    require(
        len(projections) == 3
        and [row.get("stack_alignment_bytes") for row in projections] == [8, 16, 16]
        and all(row.get("pointer_width") == 64 and row.get("endianness") == "LITTLE" for row in projections),
        "TARGET_LAYOUT",
    )
    require(
        len(projections) == 3
        and all(row.get("helper_mapping_count") == 25 and row.get("logical_value_kind_count") == 20 for row in projections),
        "TARGET_HELPER_AND_VALUE_TOTALITY",
    )
    require(
        len(projections) == 3
        and projections[1].get("scalar_mapping_digest") == projections[2].get("scalar_mapping_digest")
        and projections[1].get("indirect_slot_mapping_digest") == projections[2].get("indirect_slot_mapping_digest")
        and projections[1].get("outcome_mapping_digest") == projections[2].get("outcome_mapping_digest")
        and projections[1].get("helper_allowlist_digest") == projections[2].get("helper_allowlist_digest"),
        "AOT_JIT_PARITY",
    )
    require(
        all(row.get("target_location_is_semantic_identity") is False for row in projections)
        and handle.get("raw_address_is_semantic_identity") is False,
        "IDENTITY_FENCE",
    )
    require(
        len(projections) == 3
        and all(
            row.get("projection_digest") == expected_contract["target_projections"][index]["projection_digest"]
            and row.get("toolchain_digest") == expected_contract["target_projections"][index]["toolchain_digest"]
            and row.get("managed_handle_abi_digest") == handle.get("digest")
            and row.get("shadow_root_frame_abi_digest") == frame.get("digest")
            and row.get("runtime_root_registry_digest") == registry.get("digest")
            for index, row in enumerate(projections)
        ),
        "DIGEST_BINDING",
    )

    invariants = contract.get("implementation_invariants", {})
    require(invariants == expected_contract.get("implementation_invariants"), "IMPLEMENTATION_INVARIANTS")
    governance = contract.get("governance", {})
    require(
        governance == {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "production_execution": "NOT_RUN",
            "current_binding": False,
            "github_mutation": 0,
        }
        and all(row.get("product_execution") == "NOT_RUN" for row in projections),
        "GOVERNANCE",
    )

    cases = fixture.get("cases", [])
    classes = Counter(row.get("class") for row in cases)
    require(
        fixture.get("schema") == "deeplus.runtime-managed-projection-handoff-fixtures/r108"
        and fixture.get("revision") == contract.get("revision")
        and fixture.get("contract_path") == CONTRACT_REL.as_posix()
        and fixture.get("product_execution") == "NOT_RUN",
        "FIXTURE_IDENTITY",
    )
    require(
        len(cases) == 16
        and classes == {"positive": 4, "boundary": 4, "reject": 8}
        and len({row.get("case_id") for row in cases}) == 16
        and all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in cases),
        "FIXTURE_COUNTS",
    )
    require(contract == expected_contract and fixture == expected_fixture, "GENERATED_PROJECTION_BINDING")
    return errors


def run_mutations(contract: dict[str, Any], fixture: dict[str, Any], expected_contract: dict[str, Any], expected_fixture: dict[str, Any]) -> list[dict[str, str]]:
    plans: list[tuple[str, str, Callable[[dict[str, Any], dict[str, Any]], None]]] = [
        ("R108-M-01", "TARGET_CARDINALITY", lambda c, f: c["target_projections"].pop()),
        ("R108-M-02", "TARGET_LAYOUT", lambda c, f: c["target_projections"][1].__setitem__("stack_alignment_bytes", 8)),
        ("R108-M-03", "AOT_JIT_PARITY", lambda c, f: c["target_projections"][2].__setitem__("scalar_mapping_digest", "0" * 64)),
        ("R108-M-04", "MANAGED_HANDLE_LAYOUT", lambda c, f: c["managed_native_abi"]["managed_handle_abi"]["fields"][2].__setitem__("offset", 12)),
        ("R108-M-05", "GENERATION_RULE", lambda c, f: c["managed_native_abi"]["managed_handle_abi"].__setitem__("generation_rule", "wrap and reuse")),
        ("R108-M-06", "ROOT_REGISTRY", lambda c, f: c["managed_native_abi"]["runtime_root_registry"]["partitions"].append("FRAME")),
        ("R108-M-07", "SAFEPOINT_FENCE", lambda c, f: c["managed_native_abi"].__setitem__("implicit_backend_safepoint_count", 1)),
        ("R108-M-08", "IDENTITY_FENCE", lambda c, f: c["target_projections"][0].__setitem__("target_location_is_semantic_identity", True)),
        ("R108-M-09", "GOVERNANCE", lambda c, f: c["governance"].__setitem__("production_execution", "PASS")),
        ("R108-M-10", "FIXTURE_COUNTS", lambda c, f: f["cases"].pop()),
        ("R108-M-11", "DIGEST_BINDING", lambda c, f: c["target_projections"][0].__setitem__("projection_digest", "0" * 64)),
        ("R108-M-12", "DIGEST_BINDING", lambda c, f: c["target_projections"][2].__setitem__("toolchain_digest", "f" * 64)),
    ]
    results = []
    for mutation_id, expected_code, mutate in plans:
        candidate_contract = copy.deepcopy(contract)
        candidate_fixture = copy.deepcopy(fixture)
        mutate(candidate_contract, candidate_fixture)
        errors = validate_documents(candidate_contract, candidate_fixture, expected_contract, expected_fixture)
        results.append({"mutation_id": mutation_id, "result": "REJECTED" if expected_code in errors else "FAILED_TO_REJECT", "target_check": expected_code})
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    required = [CONTRACT_REL, FIXTURE_REL, SCHEMA_REL, GENERATOR_REL]
    missing = [path.as_posix() for path in required if not (root / path).is_file()]
    if missing:
        print(json.dumps({"result": "FAIL", "errors": [f"MISSING:{path}" for path in missing]}, sort_keys=True))
        return 1
    generator = load_generator(root)
    expected_contract, expected_fixture = generator.build(root)
    contract = load(root / CONTRACT_REL)
    fixture = load(root / FIXTURE_REL)
    errors = validate_documents(contract, fixture, expected_contract, expected_fixture)
    schema_mode = "STRICT_STRUCTURAL_FALLBACK"
    try:
        import jsonschema  # type: ignore
        jsonschema.Draft202012Validator(load(root / SCHEMA_REL)).validate(contract)
        schema_mode = "JSONSCHEMA_DRAFT_2020_12"
    except ImportError:
        pass
    except Exception as exc:
        errors.append(f"JSON_SCHEMA:{exc}")
    mutations = run_mutations(contract, fixture, expected_contract, expected_fixture) if args.mutations else []
    failed_mutations = [row for row in mutations if row["result"] != "REJECTED"]
    if failed_mutations:
        errors.extend(f"MUTATION:{row['mutation_id']}" for row in failed_mutations)
    receipt = {
        "schema": "deeplus.runtime-managed-projection-handoff-validation/r108",
        "result": "PASS" if not errors else "FAIL",
        "schema_mode": schema_mode,
        "target_projection_count": len(contract.get("target_projections", [])),
        "managed_abi_record_count": 3,
        "fixture_count": len(fixture.get("cases", [])),
        "mutation_count": len(mutations),
        "rejected_mutation_count": sum(row["result"] == "REJECTED" for row in mutations),
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_execution": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
