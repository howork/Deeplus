#!/usr/bin/env python3
"""Compatibility entry point for the R38 continuation-interface validator.

The predecessor R20 checks remain below as immutable implementation evidence;
the executable entry point delegates to the R38 successor, which also preserves
the exact 24-case suspension acceptance set.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE_COMMIT = "3f0077dd8f021718dc87b3b239f417e5d3f770a6"
GRAMMAR_SHA256 = "055ed7010ad8b78345d0414ffe696988abb52d13fa6f86e3dd1dae4610a4c962"
STATIC_IDS = ["ContinuationFramePlanId", "SuspensionPointId", "FrameSlotId"]
DYNAMIC_IDS = ["ContinuationFrameId", "SuspensionEpochId"]
FRAME_STATES = [
    "RUNNING",
    "SUSPENDED",
    "CLEANING",
    "TERMINAL_COMPLETED",
    "TERMINAL_FAILED",
    "TERMINAL_CANCELLED",
]
EPOCH_STATES = ["PREPARING", "COMMITTED", "RESUME_WON", "CANCEL_WON", "DISCHARGED"]
OPERATIONS = [
    "FRAME_CREATE",
    "FRAME_SUSPEND_COMMIT",
    "FRAME_RESUME_COMMIT",
    "FRAME_CANCEL_COMMIT",
    "FRAME_CLEANUP_STEP",
    "FRAME_TERMINATE",
]
SLOT_DISPOSITIONS = [
    "NOT_LIVE_AFTER_SUSPEND",
    "REUSABLE_COPY",
    "OWNED_TRANSFER",
    "STATIC_SHARED_BORROW",
]
DIAGNOSTICS = [
    "BORROW_CROSSES_SUSPENSION",
    "CONTINUATION_FRAME_OWNER_PARTITION_INVALID",
    "CONTINUATION_FRAME_TRANSITION_INVALID",
    "CONTINUATION_FRAME_CLEANUP_BALANCE_INVALID",
    "CONTINUATION_FRAME_ROOT_SET_INVALID",
]
EXPECTED_CLASSES = Counter({"positive": 6, "boundary": 7, "negative": 6, "mutation": 5})


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog_rows(root: Path, relative_root: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative_root / "chunks").glob("part-*.json")):
        value = load_json(path)
        if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
            raise ValueError(f"invalid catalog shard: {path}")
        rows.extend(value)
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def contract_errors(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if contract.get("schema") != "deeplus.suspension-frame-responsibility/r1":
        errors.append("schema identity")
    if contract.get("status") != "LOCAL_CANONICAL_PROJECTION_NOT_PUBLISHED":
        errors.append("projection status")
    if contract.get("gap_id") != "IR-OWN-P0-017":
        errors.append("gap identity")

    surface = contract.get("source_surface", {})
    if surface.get("new_spelling_count") != 0 or surface.get("grammar_change_required") is not False:
        errors.append("source surface fence")

    identities = contract.get("identity_domains", {})
    if identities.get("static") != STATIC_IDS or identities.get("dynamic") != DYNAMIC_IDS:
        errors.append("identity domains")
    if contract.get("frame_states") != FRAME_STATES:
        errors.append("frame states")
    if contract.get("epoch_states") != EPOCH_STATES:
        errors.append("epoch states")

    transitions = contract.get("transitions", [])
    if [row.get("operation") for row in transitions] != OPERATIONS:
        errors.append("transition operation family")
    if len({row.get("operation") for row in transitions}) != len(OPERATIONS):
        errors.append("transition operation uniqueness")

    slots = contract.get("frame_slot_contract", {})
    if slots.get("dispositions") != SLOT_DISPOSITIONS:
        errors.append("slot disposition family")
    if slots.get("runtime_address_identity_count") != 0:
        errors.append("backend identity fence")

    loan = contract.get("loan_fence", {})
    if loan.get("admitted_across_suspension") != ["NONE", "STATIC_IMMUTABLE_SHARED"]:
        errors.append("admitted loan fence")
    forbidden = set(loan.get("must_end_before_suspension", []))
    if forbidden != {"STACK_SHARED", "REGION_SHARED", "INOUT", "EXCLUSIVE", "TEMPORARY_VIEW", "CALLBACK_BORROW", "BORROW_FACET"}:
        errors.append("forbidden loan fence")

    partition = contract.get("partition_law", {})
    if any(partition.get(key) != 0 for key in ("partial_transfer_count", "duplicate_identity_count", "lost_identity_count")):
        errors.append("partition conservation")
    commit = contract.get("suspend_commit", {})
    if commit.get("preparing_ownership_mutation_count") != 0 or commit.get("atomic") is not True:
        errors.append("atomic suspension commit")
    if commit.get("epoch_allocation") != "FRESH_MONOTONIC_PER_FRAME":
        errors.append("epoch freshness")

    race = contract.get("resume_cancel_race", {})
    if race.get("winner_count") != 1 or race.get("loser_effect_count") != 0 or race.get("terminal_resume_count") != 0:
        errors.append("resume/cancel single-winner law")

    cleanup = contract.get("cleanup", {})
    if cleanup.get("token_discharge_count_per_token") != 1:
        errors.append("cleanup exactly once")
    if cleanup.get("order") != "REVERSE_REGISTRATION_WITHIN_REVERSE_NESTED_CLEANUP_REGION":
        errors.append("cleanup order")
    if any(cleanup.get(key) != 0 for key in ("publication_count", "owner_resurrection_count", "terminal_owner_balance", "terminal_cleanup_token_balance")):
        errors.append("terminal cleanup balance")

    mir = contract.get("mir_projection", {})
    if mir.get("operations") != OPERATIONS:
        errors.append("MIR operation projection")
    if mir.get("backend_owner_inference") != "FORBIDDEN" or mir.get("xvm_cranelift_partition_equivalence") != "REQUIRED":
        errors.append("backend-neutral projection")

    diagnostic_ids = [row.get("id") for row in contract.get("diagnostics", [])]
    if diagnostic_ids != DIAGNOSTICS:
        errors.append("diagnostic family")
    if contract.get("diagnostic_precedence") != ["FACET_BORROW_CROSSES_SUSPENSION", *DIAGNOSTICS]:
        errors.append("diagnostic precedence")

    fence = contract.get("status_fence", {})
    if fence != {
        "semantic_p0_delta": 0,
        "canonical_feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
        "github_publication": "SUSPENDED",
    }:
        errors.append("status fence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()

    paths = {
        "contract": root / "spec/contracts/suspension-frame-responsibility-r1.json",
        "language": root / "spec/language.md",
        "bridge_contract": root / "spec/contracts/hir-h1-current-mir-bridge.json",
        "machine_diagnostics": root / "spec/contracts/hir-mir-machine-diagnostic-contract.json",
        "feature_chunk": root / "spec/features/catalog/chunks/part-0021.json",
        "schema": root / "schemas/language/suspension-frame-responsibility.schema.json",
        "fixtures": root / "tests/fixtures/current/suspension-frame-responsibility-r1.json",
        "machine_fixtures": root / "tests/fixtures/current/hir-mir-machine-contract-r1.json",
        "types": root / "spec/types/type-system.md",
        "mir": root / "spec/mir/semantics.md",
        "grammar": root / "spec/grammar/deeplus.ebnf",
        "hir_schema": root / "schemas/language/canonical-hir-h1.schema.json",
        "hir_catalog": root / "spec/contracts/hir-h1-identity-catalog.json",
        "mir_schema": root / "schemas/language/deeplus-mir.schema.json",
        "mir_registry": root / "spec/contracts/mir-machine-registry.json",
        "lowering_registry": root / "spec/contracts/hir-mir-lowering-registry.json",
        "row_schema": root / "schemas/language/hir-mir-lowering-row.schema.json",
        "diagnostic_metadata": root / "spec/diagnostics/catalog/catalog-metadata.json",
        "predicate_metadata": root / "spec/types/predicates/catalog-metadata.json",
        "predicate_fixture_metadata": root / "tests/conformance/checker-predicates/catalog-metadata.json",
        "relation_metadata": root / "spec/diagnostics/relations/catalog-metadata.json",
    }
    missing = [str(path.relative_to(root)) for path in paths.values() if not path.is_file()]
    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "pass": bool(passed), "detail": detail})

    check("R20_FILES_PRESENT", not missing, missing)
    if missing:
        print(json.dumps({"result": "FAIL", "checks": checks}, separators=(",", ":")))
        return 1

    contract = load_json(paths["contract"])
    schema = load_json(paths["schema"])
    fixtures = load_json(paths["fixtures"])

    schema_status = "NOT_RUN_JSONSCHEMA_UNAVAILABLE"
    try:
        import jsonschema  # type: ignore

        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(contract, schema)
        schema_status = "PASS"
    except ModuleNotFoundError:
        pass
    except Exception as exc:  # pragma: no cover - surfaced as receipt detail
        schema_status = f"FAIL:{exc}"
    check("R20_JSON_SCHEMA", not schema_status.startswith("FAIL"), schema_status)

    contract_failures = contract_errors(contract)
    check("R20_EXACT_CONTRACT", not contract_failures, contract_failures)

    tests = fixtures.get("tests", [])
    ids = [row.get("test_id") for row in tests]
    classes = Counter(row.get("class") for row in tests)
    counts_ok = (
        len(tests) == 24
        and len(ids) == len(set(ids))
        and classes == EXPECTED_CLASSES
        and fixtures.get("expected_counts") == {"total": 24, **EXPECTED_CLASSES}
    )
    check("R20_ACCEPTANCE_EXACT_24", counts_ok, {"total": len(tests), "classes": dict(classes)})
    diagnostic_ids = {row["id"] for row in contract["diagnostics"]} | {"FACET_BORROW_CROSSES_SUSPENSION"}
    fixture_diagnostics = {row["diagnostic_or_null"] for row in tests if row["diagnostic_or_null"] is not None}
    check("R20_ACCEPTANCE_DIAGNOSTICS_BOUND", fixture_diagnostics <= diagnostic_ids, sorted(fixture_diagnostics))

    catalog_diagnostics = load_catalog_rows(root, "spec/diagnostics/catalog")
    matching_diagnostics = {
        diagnostic_id: [row for row in catalog_diagnostics if row.get("diagnostic_id") == diagnostic_id]
        for diagnostic_id in DIAGNOSTICS
    }
    diagnostic_binding_ok = all(len(rows) == 1 for rows in matching_diagnostics.values())
    diagnostic_binding_ok = diagnostic_binding_ok and matching_diagnostics[DIAGNOSTICS[0]][0].get("diagnostic_class") == "current_source"
    diagnostic_binding_ok = diagnostic_binding_ok and all(
        matching_diagnostics[diagnostic_id][0].get("diagnostic_class") == "release_verifier"
        for diagnostic_id in DIAGNOSTICS[1:]
    )
    check(
        "R20_DIAGNOSTIC_CATALOG_BOUND",
        diagnostic_binding_ok,
        {diagnostic_id: len(rows) for diagnostic_id, rows in matching_diagnostics.items()},
    )

    predicate_rows = load_catalog_rows(root, "spec/types/predicates")
    predicate_matches = [row for row in predicate_rows if row.get("predicate_id") == "BorrowAcrossSuspensionAdmitted"]
    predicate_fixture_rows = load_catalog_rows(root, "tests/conformance/checker-predicates")
    predicate_fixture_ids = {
        row.get("fixture_id")
        for row in predicate_fixture_rows
        if row.get("predicate_id") == "BorrowAcrossSuspensionAdmitted"
    }
    expected_predicate_fixture_ids = {
        "PF-BorrowAcrossSuspensionAdmitted-POS",
        "PF-BorrowAcrossSuspensionAdmitted-BOUNDARY",
        "PF-BorrowAcrossSuspensionAdmitted-NEG",
    }
    relation_rows = load_catalog_rows(root, "spec/diagnostics/relations")
    suspension_relations = [
        row for row in relation_rows
        if row.get("predicate_id") == "BorrowAcrossSuspensionAdmitted"
    ]
    check(
        "R20_CHECKER_PREDICATE_DISPATCH_BOUND",
        len(predicate_matches) == 1
        and predicate_matches[0].get("active_primary_diagnostic") == "BORROW_CROSSES_SUSPENSION"
        and predicate_matches[0].get("positive_fixture_ids")
        == ["PF-BorrowAcrossSuspensionAdmitted-POS", "PF-BorrowAcrossSuspensionAdmitted-BOUNDARY"]
        and predicate_matches[0].get("negative_fixture_ids")
        == ["PF-BorrowAcrossSuspensionAdmitted-NEG"]
        and predicate_fixture_ids == expected_predicate_fixture_ids
        and suspension_relations == [
            {
                "violation_id": "BorrowAcrossSuspensionAdmitted:default",
                "predicate_id": "BorrowAcrossSuspensionAdmitted",
                "diagnostic_id": "BORROW_CROSSES_SUSPENSION",
                "relation": "primary",
            },
            {
                "violation_id": None,
                "predicate_id": "BorrowAcrossSuspensionAdmitted",
                "diagnostic_id": "FACET_BORROW_CROSSES_SUSPENSION",
                "relation": "secondary",
            },
        ],
        {
            "predicate_rows": len(predicate_matches),
            "fixture_ids": sorted(predicate_fixture_ids),
            "relations": suspension_relations,
        },
    )

    metadata_counts = {
        "diagnostics": load_json(paths["diagnostic_metadata"]).get("diagnostic_count"),
        "predicates": load_json(paths["predicate_metadata"]).get("predicate_count"),
        "predicate_fixtures": load_json(paths["predicate_fixture_metadata"]).get("fixture_count"),
        "relations": load_json(paths["relation_metadata"]).get("relation_count"),
    }
    actual_catalog_counts = {
        "diagnostics": len(catalog_diagnostics),
        "predicates": len(predicate_rows),
        "predicate_fixtures": len(predicate_fixture_rows),
        "relations": len(relation_rows),
    }
    expected_catalog_counts = {
        "diagnostics": 1446,
        "predicates": 278,
        "predicate_fixtures": 849,
        "relations": 562,
    }
    check(
        "R20_CATALOG_METADATA_COUNTS",
        metadata_counts == expected_catalog_counts
        and actual_catalog_counts == expected_catalog_counts,
        {"metadata": metadata_counts, "actual": actual_catalog_counts},
    )

    types_text = paths["types"].read_text(encoding="utf-8")
    mir_text = paths["mir"].read_text(encoding="utf-8")
    language_text = paths["language"].read_text(encoding="utf-8")
    check(
        "R20_TYPE_SYSTEM_TRACE",
        all(term in types_text for term in ("ContinuationFramePlanId", "SuspensionEpochId", "BORROW_CROSSES_SUSPENSION", "exactly once")),
        "type-system suspension-frame section",
    )
    check(
        "R20_MIR_TRACE",
        all(term in mir_text for term in OPERATIONS + ["CONTINUATION_FRAME_TRANSITION_INVALID"]),
        "MIR continuation-frame section",
    )
    check(
        "R20_LANGUAGE_TRACE",
        all(
            term in language_text
            for term in (
                "exactly 130 identities",
                "ContinuationFramePlanId",
                "BorrowAcrossSuspensionAdmitted",
                "exactly one wins",
            )
        ),
        "language HIR/MIR suspension-frame bridge",
    )
    check("R20_GRAMMAR_UNCHANGED", sha256(paths["grammar"]) == GRAMMAR_SHA256, sha256(paths["grammar"]))
    check("R20_BASELINE_ANCESTRY", git(root, "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD") == "", git(root, "rev-parse", "HEAD"))

    hir_schema = load_json(paths["hir_schema"])
    hir_defs = hir_schema.get("$defs", {})
    structural_refs = [row.get("$ref") for row in hir_defs.get("StructuralPlan", {}).get("oneOf", [])]
    suspend_required = set(
        hir_defs.get("SuspendPlan", {}).get("allOf", [{}, {}])[1].get("required", [])
    )
    check(
        "R20_HIR_FRAME_PLAN_REACHABLE",
        "HIR-H1/STRUCT/CONTINUATION_FRAME_PLAN" in hir_defs.get("PlanStructuralKind", {}).get("enum", [])
        and "ContinuationFramePlan" in hir_defs
        and structural_refs.count("#/$defs/ContinuationFramePlan") == 1
        and "continuation_frame_plan_id" in suspend_required,
        {"structural_ref_count": structural_refs.count("#/$defs/ContinuationFramePlan"), "suspend_required": sorted(suspend_required)},
    )

    hir_catalog = load_json(paths["hir_catalog"])
    continuation_rows = [
        row for row in hir_catalog.get("identity_rows", [])
        if row.get("identity_id") == "HIR-H1/STRUCT/CONTINUATION_FRAME_PLAN"
    ]
    continuation_contracts = [
        row for row in hir_catalog.get("structural_plan_contracts", [])
        if row.get("structural_identity_id") == "HIR-H1/STRUCT/CONTINUATION_FRAME_PLAN"
    ]
    check(
        "R20_HIR_IDENTITY_CATALOG_BOUND",
        hir_catalog.get("identity_count") == 130
        and hir_catalog.get("structural_plan_contract_count") == 14
        and len(continuation_rows) == len(continuation_contracts) == 1,
        {"identities": hir_catalog.get("identity_count"), "structural_plans": hir_catalog.get("structural_plan_contract_count")},
    )

    mir_schema = load_json(paths["mir_schema"])
    mir_defs = mir_schema.get("$defs", {})
    mir_ops = mir_defs.get("operationKind", {}).get("enum", [])
    mir_semops = mir_defs.get("semanticOperationId", {}).get("enum", [])
    body_required = mir_defs.get("mirBody", {}).get("required", [])
    check(
        "R20_MIR_FRAME_SCHEMA_BOUND",
        all(name in mir_defs for name in ("continuationFrameSlotDecl", "continuationFramePlanDecl", "frameOperationPayload"))
        and "continuation_frame_plan_table" in body_required
        and all(operation in mir_ops for operation in OPERATIONS)
        and all(f"DM-SEMOP-{operation.replace('_', '-')}-R1" in mir_semops for operation in OPERATIONS)
        and mir_schema.get("x-deeplus-closed-universe", {}).get("operation_kind_count") == 48,
        {"operation_count": len(mir_ops), "body_has_frame_table": "continuation_frame_plan_table" in body_required},
    )

    mir_registry = load_json(paths["mir_registry"])
    registry_map = {
        row.get("operation_kind"): row.get("semantic_operation_id")
        for row in mir_registry.get("semantic_operations", [])
    }
    suspend_capability = next(
        (row for row in mir_registry.get("capabilities", []) if row.get("capability_id") == "DM-CAP-SUSPEND-CANCEL-R1"),
        {},
    )
    check(
        "R20_MIR_REGISTRY_BOUND",
        len(registry_map) == 48
        and all(registry_map.get(operation) == f"DM-SEMOP-{operation.replace('_', '-')}-R1" for operation in OPERATIONS)
        and suspend_capability.get("operation_kinds") == OPERATIONS,
        {"operation_count": len(registry_map), "suspend_operations": suspend_capability.get("operation_kinds")},
    )

    lowering = load_json(paths["lowering_registry"])
    frame_mapping = lowering.get("continuation_frame_mapping", {})
    await_yield = {
        row.get("lowering_dispatch_key", {}).get("identity_id"): [step.get("operation_kind") for step in row.get("operation_plan", [])]
        for row in lowering.get("rows", [])
        if row.get("lowering_dispatch_key", {}).get("identity_id") in {"AWAIT", "YIELD"}
    }
    check(
        "R20_LOWERING_REGISTRY_BOUND",
        frame_mapping.get("exact_operation_family_count") == 6
        and frame_mapping.get("body_entry_operation") == "FRAME_CREATE"
        and frame_mapping.get("body_terminal_operation") == "FRAME_TERMINATE"
        and await_yield == {
            "AWAIT": ["FRAME_SUSPEND_COMMIT", "FRAME_RESUME_COMMIT", "FRAME_CANCEL_COMMIT"],
            "YIELD": ["FRAME_SUSPEND_COMMIT", "FRAME_RESUME_COMMIT", "FRAME_CANCEL_COMMIT"],
        },
        {"frame_mapping": frame_mapping, "site_plans": await_yield},
    )

    bridge = load_json(paths["bridge_contract"])
    bridge_acceptance = bridge.get("machine_acceptance", {})
    bridge_frame = bridge.get("suspension_frame_responsibility_bridge", {})
    feature_rows = load_json(paths["feature_chunk"])
    feature = next(
        (row for row in feature_rows if row.get("feature_id") == "hir_h1_current_mir_bridge_design"),
        {},
    )
    check(
        "R20_CURRENT_BRIDGE_BOUND",
        bridge_acceptance.get("hir_identity_count") == 130
        and bridge_acceptance.get("mir_operation_count") == 48
        and bridge_acceptance.get("new_release_verifier_diagnostic_count") == 9
        and bridge_acceptance.get("new_source_diagnostic_count") == 1
        and bridge_frame.get("checker_predicate") == "BorrowAcrossSuspensionAdmitted"
        and bridge_frame.get("source_spelling_delta") == 0
        and bridge_frame.get("product_support") == "NOT_RUN"
        and set(feature.get("normative_trace_refs", {}).get("diagnostics", [])) >= set(DIAGNOSTICS)
        and feature.get("normative_trace_refs", {}).get("predicates") == ["BorrowAcrossSuspensionAdmitted"],
        {
            "acceptance": bridge_acceptance,
            "frame_bridge": bridge_frame,
            "feature_predicates": feature.get("normative_trace_refs", {}).get("predicates"),
        },
    )

    machine_diagnostics = load_json(paths["machine_diagnostics"])
    machine_fixture_text = paths["machine_fixtures"].read_text(encoding="utf-8")
    check(
        "R20_PREDECESSOR_MACHINE_COUNT_REBOUND",
        machine_diagnostics.get("semantic_operation_mapping", {}).get("operation_count") == 48
        and "structural_schema_identity_count=18" in machine_fixture_text
        and "structural_schema_identity_count=17" not in machine_fixture_text,
        {
            "operation_count": machine_diagnostics.get("semantic_operation_mapping", {}).get("operation_count"),
            "structural_identity_assertion": 18,
        },
    )

    bindings = lowering.get("contract_bindings", {})
    binding_paths = {
        "hir_schema": "hir_schema",
        "hir_identity_catalog": "hir_catalog",
        "mir_schema": "mir_schema",
        "mir_machine_registry": "mir_registry",
        "lowering_row_schema": "row_schema",
        "fixture_binding_table": "machine_fixtures",
        "diagnostic_contract": "machine_diagnostics",
    }
    digest_results = {
        binding: bindings.get(binding, {}).get("sha256") == sha256(paths[path_key])
        for binding, path_key in binding_paths.items()
    }
    check("R20_MACHINE_DIGEST_BINDINGS", all(digest_results.values()), digest_results)

    mutations: list[tuple[str, dict[str, Any]]] = []
    mutant = copy.deepcopy(contract); mutant["source_surface"]["new_spelling_count"] = 1; mutations.append(("NEW_SPELLING", mutant))
    mutant = copy.deepcopy(contract); mutant["resume_cancel_race"]["winner_count"] = 2; mutations.append(("TWO_WINNERS", mutant))
    mutant = copy.deepcopy(contract); mutant["loan_fence"]["admitted_across_suspension"].append("INOUT"); mutations.append(("INOUT_CROSSES", mutant))
    mutant = copy.deepcopy(contract); mutant["cleanup"]["token_discharge_count_per_token"] = 2; mutations.append(("DOUBLE_CLEANUP", mutant))
    mutant = copy.deepcopy(contract); mutant["transitions"][1]["operation"] = "FRAME_CREATE"; mutations.append(("DUPLICATE_TRANSITION", mutant))
    mutation_results = {name: bool(contract_errors(value)) for name, value in mutations}
    check("R20_MUTATION_REJECTION_5_OF_5", all(mutation_results.values()), mutation_results)

    failed = [row for row in checks if not row["pass"]]
    receipt = {
        "schema": "deeplus.suspension-frame-responsibility-validation/r1",
        "result": "PASS" if not failed else "FAIL",
        "baseline_commit": BASELINE_COMMIT,
        "head": git(root, "rev-parse", "HEAD"),
        "check_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "checks": checks,
        "product_execution": "NOT_RUN",
        "github_mutation": 0,
    }
    print(json.dumps(receipt, separators=(",", ":")))
    return 0 if not failed else 1


if __name__ == "__main__":
    from validate_continuation_interface import main as r38_main

    raise SystemExit(r38_main())
