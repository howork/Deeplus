#!/usr/bin/env python3
"""Validate the R38 continuation-interface rebase.

This is design-static evidence. It does not execute a parser, checker,
runtime, xVM, Cranelift backend, formatter, or LSP.
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


BASELINE_COMMIT = "e680568057ec9c6b02218dbe153758471734cf44"
GRAMMAR_SHA256 = "be302f2b616b61e978d8d889ae3ab3c49bced3df8f1ef60fea66e124bde1d1cc"
INTERFACE_ID = "ContinuationInterfaceId:DEEPLUS_CONTINUATION_INTERFACE_R1"
R36_MANAGED_REFERENCE_DIGEST = "feff3c021d4b77e64e4e9f00f797b0ce2c465a5b60709d86d0baf7bded72c7f7"
R37_RUNTIME_ABI_DIGEST = "e2675436420814e9e4af6c3a7f530321f8c829c7d31d95533f371cbd9ba56146"
FRAME_STATES = ["RUNNING", "SUSPENDED", "CLEANING", "TERMINAL_COMPLETED", "TERMINAL_FAILED", "TERMINAL_CANCELLED"]
EPOCH_STATES = ["PREPARING", "COMMITTED", "RESUME_WON", "CANCEL_WON", "DISCHARGED"]
OPERATIONS = ["FRAME_CREATE", "FRAME_SUSPEND_COMMIT", "FRAME_RESUME_COMMIT", "FRAME_CANCEL_COMMIT", "FRAME_CLEANUP_STEP", "FRAME_TERMINATE"]
TRANSITIONS = [
    ("FRAME_CREATE", ["ABSENT"], "RUNNING", None, None, None),
    ("FRAME_SUSPEND_COMMIT", ["RUNNING"], "SUSPENDED", "PREPARING", "COMMITTED", None),
    ("FRAME_RESUME_COMMIT", ["SUSPENDED"], "RUNNING", "COMMITTED", "DISCHARGED", "RESUME_WON"),
    ("FRAME_CANCEL_COMMIT", ["SUSPENDED"], "CLEANING", "COMMITTED", "CANCEL_WON", "CANCEL_WON"),
    ("FRAME_CLEANUP_STEP", ["CLEANING"], "CLEANING", "CANCEL_WON", "CANCEL_WON", None),
    ("FRAME_TERMINATE", ["RUNNING"], "TERMINAL_COMPLETED", None, None, None),
    ("FRAME_TERMINATE", ["RUNNING"], "TERMINAL_FAILED", None, None, None),
    ("FRAME_TERMINATE", ["CLEANING"], "TERMINAL_CANCELLED", "CANCEL_WON", "DISCHARGED", None),
]
PAYLOAD_FIELDS = [
    "continuation_interface_identity", "continuation_interface_digest",
    "continuation_receipt_id_or_null", "continuation_frame_plan_id", "frame_id",
    "suspension_point_id_or_null", "epoch_id_or_null", "partition_digest",
    "cleanup_token_id_or_null", "terminal_state_or_null", "frame_state_before",
    "frame_state_after", "epoch_state_before_or_null", "epoch_state_after_or_null",
    "winner_witness_or_null", "hir_provenance",
]
DIAGNOSTICS = [
    "BORROW_CROSSES_SUSPENSION",
    "CONTINUATION_FRAME_OWNER_PARTITION_INVALID",
    "CONTINUATION_FRAME_TRANSITION_INVALID",
    "CONTINUATION_FRAME_CLEANUP_BALANCE_INVALID",
    "CONTINUATION_FRAME_ROOT_SET_INVALID",
]
ARTIFACTS = {
    "continuation_receipt_schema": "schemas/language/continuation-receipt-r1.schema.json",
    "suspension_frame_schema": "schemas/language/suspension-frame-responsibility.schema.json",
    "hir_schema": "schemas/language/canonical-hir-h1.schema.json",
    "mir_schema": "schemas/language/deeplus-mir.schema.json",
    "mir_machine_registry": "spec/contracts/mir-machine-registry.json",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def catalog_rows(root: Path, relative: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / relative / "chunks").glob("part-*.json")):
        value = load(path)
        if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
            raise ValueError(f"invalid catalog shard: {path}")
        rows.extend(value)
    return rows


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()


def source_manifest_export_binding(
    root: Path, required_paths: list[Path]
) -> tuple[bool, dict[str, Any]]:
    """Bind a git-less clean export to its staged source-tree manifest."""
    manifest_path = root / "release/source-tree-manifest.json"
    if not manifest_path.is_file():
        return False, {"mode": "SOURCE_TREE_MANIFEST_EXPORT", "error": "manifest_missing"}
    try:
        manifest = load(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return False, {
            "mode": "SOURCE_TREE_MANIFEST_EXPORT",
            "error": f"manifest_invalid:{type(exc).__name__}",
        }
    rows = manifest.get("files")
    if (
        manifest.get("schema") != "deeplus.source-tree-manifest/v1"
        or not isinstance(rows, list)
    ):
        return False, {"mode": "SOURCE_TREE_MANIFEST_EXPORT", "error": "manifest_shape"}
    declared = {
        row.get("path"): row.get("sha256")
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    required = [*required_paths, Path(__file__).resolve()]
    mismatches: list[str] = []
    for path in required:
        try:
            relative = path.resolve().relative_to(root).as_posix()
        except ValueError:
            mismatches.append(f"outside_root:{path}")
            continue
        if not path.is_file() or declared.get(relative) != sha256(path):
            mismatches.append(relative)
    return not mismatches, {
        "mode": "SOURCE_TREE_MANIFEST_EXPORT",
        "source_baseline": manifest.get("source_baseline"),
        "tree_sha256": manifest.get("tree_sha256"),
        "required_binding_count": len(required),
        "mismatches": mismatches,
    }


def interface_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value.get("schema") != "deeplus.continuation-interface/r1":
        errors.append("schema")
    if value.get("interface_identity") != INTERFACE_ID:
        errors.append("identity")
    if value.get("source_surface") != {"new_spelling_count": 0, "grammar_change_required": False}:
        errors.append("source_surface")
    if value.get("frame_states") != FRAME_STATES or value.get("epoch_states") != EPOCH_STATES:
        errors.append("closed_states")
    observed = [
        (row.get("operation"), row.get("frame_from"), row.get("frame_to"), row.get("epoch_from"), row.get("epoch_to"), row.get("winner_witness_or_null"))
        for row in value.get("transitions", [])
    ]
    if observed != TRANSITIONS:
        errors.append("transitions")
    dispositions = value.get("place_dispositions", [])
    if [(row.get("disposition"), row.get("materializes_frame_slot")) for row in dispositions] != [
        ("NOT_LIVE_AFTER_SUSPEND", False), ("REUSABLE_COPY", True),
        ("OWNED_TRANSFER", True), ("STATIC_SHARED_BORROW", True),
    ]:
        errors.append("place_slot_split")
    slot = value.get("frame_slot_contract", {})
    if slot.get("materialized_dispositions") != ["REUSABLE_COPY", "OWNED_TRANSFER", "STATIC_SHARED_BORROW"]:
        errors.append("physical_slot_dispositions")
    if slot.get("runtime_address_identity_count") != 0:
        errors.append("slot_address_identity")
    loan = value.get("loan_fence", {})
    if loan.get("admitted_across_suspension") != ["NONE", "STATIC_IMMUTABLE_SHARED"]:
        errors.append("loan_admission")
    if loan.get("actor_state_live_loan_count_at_commit") != 0:
        errors.append("actor_live_loan")
    partitions = value.get("partition_laws", {})
    if any(partitions.get(key) != 0 for key in ("partial_transfer_count", "duplicate_identity_count", "lost_identity_count")):
        errors.append("partition_conservation")
    if not all(key in partitions for key in ("owner", "loan", "cleanup_token", "opaque_authority", "root")):
        errors.append("partition_axes")
    roots = value.get("root_rebind_law", {})
    if roots.get("source_root_must_differ_from_destination_root") is not True:
        errors.append("root_storage_identity")
    if roots.get("pair_cardinality") != "BIJECTION" or roots.get("collector_entry_during_handover_count") != 0:
        errors.append("root_rebind_atomicity")
    cleanup = value.get("cleanup_law", {})
    if cleanup.get("token_discharge_count") != 1 or cleanup.get("execution_order") != "REVERSE_REGISTRATION_WITHIN_REVERSE_NESTED_CLEANUP_REGION":
        errors.append("cleanup")
    actor = value.get("actor_scope_law", {})
    if actor.get("closed_union") != ["NONE", "ACTOR_TURN"] or actor.get("retained_authority_axes") != ["STATE_REGION_MUTATION", "DEQUEUE"]:
        errors.append("actor_authority")
    race = value.get("race_and_terminal_law", {})
    if race.get("winner_count") != 1 or race.get("loser_effect_count") != 0 or race.get("terminal_resume_count") != 0:
        errors.append("race")
    if race.get("terminal_balances") != {"owners": 0, "loans": 0, "cleanup_tokens": 0, "roots": 0, "frame_slots": 0, "actor_authority": 0}:
        errors.append("terminal_balances")
    projections = value.get("projection_entry_maps", [])
    if [row.get("target_projection") for row in projections] != ["Xvm", "ObjectAot", "InMemoryJit"]:
        errors.append("projection_order")
    if any(row.get("address_as_identity") is not False for row in projections):
        errors.append("projection_address_identity")
    if projections and (projections[-1].get("image_generation_required") is not True or projections[-1].get("continuation_lease_required") is not True):
        errors.append("jit_sidecar")
    dispatch = value.get("dispatch_entry_law", {})
    if dispatch.get("arbitrary_runtime_to_generated_callback_authority") is not False or dispatch.get("host_function_pointer_is_identity") is not False:
        errors.append("dispatch_fence")
    seam = value.get("seam_status", {})
    if not (
        seam.get("r36_digest_binding") == "EXACT_LOCAL_FUSION_BOUND"
        and seam.get("r36_managed_reference_profile_digest") == R36_MANAGED_REFERENCE_DIGEST
        and seam.get("r37_helpers_remain_dependency_unbound") is False
        and seam.get("r37_dependency_binding") == "EXACT_LOCAL_FUSION_BOUND"
        and seam.get("r37_runtime_abi_digest") == R37_RUNTIME_ABI_DIGEST
        and seam.get("silent_candidate_stacking") is False
        and seam.get("future_fusion_required") is False
    ):
        errors.append("sibling_seam")
    governance = value.get("governance", {})
    if governance != {
        "semantic_p0_delta": 0,
        "gap_status": "APPROVED_NOT_INTEGRATED",
        "canonical_feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "production_execution": "NOT_RUN",
        "github_publication": "SUSPENDED",
    }:
        errors.append("governance")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    paths = {
        "interface": root / "spec/contracts/continuation-interface-r1.json",
        "interface_schema": root / "schemas/language/continuation-interface-r1.schema.json",
        "receipt_schema": root / "schemas/language/continuation-receipt-r1.schema.json",
        "suspension": root / "spec/contracts/suspension-frame-responsibility-r1.json",
        "suspension_schema": root / "schemas/language/suspension-frame-responsibility.schema.json",
        "fixtures": root / "tests/fixtures/current/continuation-interface-r1.json",
        "fixture_schema": root / "schemas/language/continuation-interface-fixtures-r1.schema.json",
        "legacy_fixtures": root / "tests/fixtures/current/suspension-frame-responsibility-r1.json",
        "hir_schema": root / "schemas/language/canonical-hir-h1.schema.json",
        "mir_schema": root / "schemas/language/deeplus-mir.schema.json",
        "mir_registry": root / "spec/contracts/mir-machine-registry.json",
        "lowering": root / "spec/contracts/hir-mir-lowering-registry.json",
        "bridge": root / "spec/contracts/hir-h1-current-mir-bridge.json",
        "grammar": root / "spec/grammar/deeplus.ebnf",
    }
    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "pass": bool(passed), "detail": detail})

    missing = [str(path.relative_to(root)) for path in paths.values() if not path.is_file()]
    check("R38_FILES_PRESENT", not missing, missing)
    if missing:
        print(json.dumps({"result": "FAIL", "checks": checks}, separators=(",", ":")))
        return 1

    interface = load(paths["interface"])
    suspension = load(paths["suspension"])
    fixtures = load(paths["fixtures"])
    schema_status: dict[str, str] = {}
    try:
        import jsonschema  # type: ignore
        for name, instance, schema_path in (
            ("interface", interface, paths["interface_schema"]),
            ("suspension", suspension, paths["suspension_schema"]),
            ("fixtures", fixtures, paths["fixture_schema"]),
        ):
            schema = load(schema_path)
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.validate(instance, schema)
            schema_status[name] = "PASS"
    except ModuleNotFoundError:
        schema_status = {"all": "NOT_RUN_JSONSCHEMA_UNAVAILABLE"}
    except Exception as exc:
        schema_status["failure"] = repr(exc)
    check("R38_JSON_SCHEMA", "failure" not in schema_status, schema_status)

    failures = interface_errors(interface)
    check("R38_EXACT_INTERFACE", not failures, failures)

    bound = {name: sha256(root / relative) for name, relative in ARTIFACTS.items()}
    components = {
        "frame_epoch_transition_digest": digest_value({"frame_states": interface["frame_states"], "epoch_states": interface["epoch_states"], "transitions": interface["transitions"]}),
        "place_slot_loan_digest": digest_value({"place_dispositions": interface["place_dispositions"], "frame_slot_contract": interface["frame_slot_contract"], "loan_fence": interface["loan_fence"]}),
        "partition_root_rebind_digest": digest_value({"partition_laws": interface["partition_laws"], "root_rebind_law": interface["root_rebind_law"]}),
        "cleanup_actor_terminal_digest": digest_value({"cleanup_law": interface["cleanup_law"], "actor_scope_law": interface["actor_scope_law"], "race_and_terminal_law": interface["race_and_terminal_law"]}),
        "projection_entry_map_digest": digest_value({"projection_entry_maps": interface["projection_entry_maps"], "dispatch_entry_law": interface["dispatch_entry_law"]}),
    }
    material = {
        "schema": interface["schema"], "interface_identity": interface["interface_identity"],
        "interface_version": interface["interface_version"], "authorities": interface["authorities"],
        "canonical_encoding": interface["canonical_encoding"], "bound_artifact_digests": bound,
        "identity_domains": interface["identity_domains"], "frame_states": interface["frame_states"],
        "epoch_states": interface["epoch_states"], "component_digests": components,
    }
    expected_digest = digest_value(material)
    digest_ok = (
        interface.get("bound_artifact_digests") == bound
        and interface.get("component_digests") == components
        and interface.get("digest_material") == material
        and interface.get("continuation_interface_digest") == expected_digest
    )
    check("R38_INTERFACE_DIGEST_BINDING", digest_ok, {"expected": expected_digest, "actual": interface.get("continuation_interface_digest")})
    suspension_binding = suspension.get("continuation_interface", {})
    check(
        "R38_SUSPENSION_BINDING",
        suspension_binding.get("interface_identity") == INTERFACE_ID
        and suspension_binding.get("interface_digest") == expected_digest
        and suspension_binding.get("bound_artifact_digests") == bound
        and suspension_binding.get("component_digests") == components,
        suspension_binding,
    )

    hir_defs = load(paths["hir_schema"]).get("$defs", {})
    hir_plan = hir_defs.get("ContinuationFramePlan", {}).get("allOf", [{}, {}])[1]
    hir_slot = hir_defs.get("ContinuationFrameSlotPlan", {})
    hir_disposition = hir_defs.get("ContinuationPlaceDisposition", {})
    check(
        "R38_HIR_CONTRACT",
        set(["continuation_interface_identity", "continuation_interface_digest", "place_dispositions", "frame_slots", "authority_token_ids", "cancellation_id_or_null"]) <= set(hir_plan.get("required", []))
        and hir_slot.get("properties", {}).get("disposition", {}).get("enum") == ["REUSABLE_COPY", "OWNED_TRANSFER", "STATIC_SHARED_BORROW"]
        and "cleanup_token_bindings" in hir_slot.get("required", [])
        and "root_projection_ids" in hir_slot.get("required", [])
        and "frame_slot_id_or_null" in hir_disposition.get("required", []),
        {"plan_required": hir_plan.get("required"), "slot_required": hir_slot.get("required")},
    )

    mir_defs = load(paths["mir_schema"]).get("$defs", {})
    plan_required = set(mir_defs.get("continuationFramePlanDecl", {}).get("required", []))
    check(
        "R38_MIR_CLOSED_PAYLOADS",
        set(["continuation_interface_identity", "continuation_interface_digest", "place_dispositions", "authority_token_ids", "cancellation_id_or_null"]) <= plan_required
        and all(name in mir_defs for name in (
            "continuationPlaceDispositionDecl", "frameCreatePayload", "frameSuspendCommitPayload",
            "frameResumeCommitPayload", "frameCancelCommitPayload", "frameCleanupStepPayload", "frameTerminatePayload",
        ))
        and "frameOperationPayload" not in mir_defs,
        {"plan_required": sorted(plan_required)},
    )
    registry = load(paths["mir_registry"])
    rows = {row.get("operation_kind"): row for row in registry.get("semantic_operations", []) if row.get("operation_kind") in OPERATIONS}
    check(
        "R38_MIR_REGISTRY",
        list(rows) == OPERATIONS
        and all(row.get("payload_contract", {}).get("required_fields") == PAYLOAD_FIELDS for row in rows.values())
        and len({canonical_bytes(row.get("payload_contract", {}).get("value_constraints")) for row in rows.values()}) == 6,
        {"operations": list(rows), "constraint_count": len({canonical_bytes(row.get("payload_contract", {}).get("value_constraints")) for row in rows.values()})},
    )
    lowering = load(paths["lowering"]).get("continuation_frame_mapping", {})
    check(
        "R38_LOWERING_BINDING",
        lowering.get("continuation_interface_identity") == INTERFACE_ID
        and lowering.get("continuation_interface_digest") == expected_digest
        and lowering.get("target_projection_order") == ["Xvm", "ObjectAot", "InMemoryJit"]
        and lowering.get("arbitrary_runtime_to_generated_callback_authority") is False,
        lowering,
    )
    bridge = load(paths["bridge"]).get("suspension_frame_responsibility_bridge", {})
    check(
        "R38_BRIDGE_BINDING",
        bridge.get("continuation_interface_identity") == INTERFACE_ID
        and bridge.get("continuation_interface_digest") == expected_digest
        and bridge.get("dynamic_identity_count") == 3
        and bridge.get("target_projection_order") == ["Xvm", "ObjectAot", "InMemoryJit"]
        and bridge.get("root_rebind_policy") == "BIJECTIVE_STORAGE_LOCATION_REBIND",
        bridge,
    )

    tests = fixtures.get("tests", [])
    classes = Counter(row.get("class") for row in tests)
    axes = [row.get("axis") for row in tests if row.get("class") == "mutation"]
    check(
        "R38_FIXTURES_EXACT_18",
        len(tests) == 18 and len({row.get("test_id") for row in tests}) == 18
        and classes == Counter({"positive": 3, "boundary": 3, "mutation": 12})
        and fixtures.get("expected_counts") == {"total": 18, "positive": 3, "boundary": 3, "mutation": 12}
        and len(axes) == len(set(axes)) == 12,
        {"classes": dict(classes), "mutation_axes": axes},
    )
    legacy = load(paths["legacy_fixtures"]).get("tests", [])
    check("R38_R20_ACCEPTANCE_PRESERVED", len(legacy) == 24 and len({row.get("test_id") for row in legacy}) == 24, len(legacy))

    counts: dict[str, tuple[int, int]] = {}
    expected_counts = {"diagnostics": 1483, "predicates": 281, "predicate_fixtures": 864, "relations": 597}
    locations = {
        "diagnostics": ("spec/diagnostics/catalog", "diagnostic_count"),
        "predicates": ("spec/types/predicates", "predicate_count"),
        "predicate_fixtures": ("tests/conformance/checker-predicates", "fixture_count"),
        "relations": ("spec/diagnostics/relations", "relation_count"),
    }
    for key, (relative, metadata_key) in locations.items():
        actual = len(catalog_rows(root, relative))
        declared = load(root / relative / "catalog-metadata.json").get(metadata_key)
        counts[key] = (actual, declared)
    check("R38_CATALOG_COUNTS", all(counts[k] == (v, v) for k, v in expected_counts.items()), counts)
    diagnostics = catalog_rows(root, "spec/diagnostics/catalog")
    diagnostic_counts = Counter(row.get("diagnostic_id") for row in diagnostics)
    check("R38_DIAGNOSTIC_BINDING", all(diagnostic_counts[value] == 1 for value in DIAGNOSTICS), {value: diagnostic_counts[value] for value in DIAGNOSTICS})
    check("R38_GRAMMAR_UNCHANGED", sha256(paths["grammar"]) == GRAMMAR_SHA256, sha256(paths["grammar"]))
    if (root / ".git").exists():
        try:
            ancestry = git(root, "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD")
            head_identity = git(root, "rev-parse", "HEAD")
            baseline_ok = ancestry == ""
            baseline_detail: Any = {
                "mode": "GIT_ANCESTRY",
                "baseline_commit": BASELINE_COMMIT,
                "head": head_identity,
            }
        except subprocess.CalledProcessError as exc:
            head_identity = "GIT_ANCESTRY_UNAVAILABLE"
            baseline_ok = False
            baseline_detail = {
                "mode": "GIT_ANCESTRY",
                "baseline_commit": BASELINE_COMMIT,
                "returncode": exc.returncode,
            }
    else:
        baseline_ok, baseline_detail = source_manifest_export_binding(
            root, list(paths.values())
        )
        head_identity = (
            f"SOURCE_TREE_MANIFEST:{baseline_detail.get('tree_sha256')}"
            if baseline_ok
            else "SOURCE_TREE_MANIFEST_UNBOUND"
        )
    check("R38_BASELINE", baseline_ok, baseline_detail)

    mutants: list[tuple[str, dict[str, Any]]] = []
    mutant = copy.deepcopy(interface); mutant["source_surface"]["new_spelling_count"] = 1; mutants.append(("NEW_SPELLING", mutant))
    mutant = copy.deepcopy(interface); mutant["place_dispositions"][0]["materializes_frame_slot"] = True; mutants.append(("NOT_LIVE_SLOT", mutant))
    mutant = copy.deepcopy(interface); mutant["loan_fence"]["admitted_across_suspension"].append("INOUT"); mutants.append(("LOAN_FENCE", mutant))
    mutant = copy.deepcopy(interface); mutant["partition_laws"]["lost_identity_count"] = 1; mutants.append(("PARTITION_LOSS", mutant))
    mutant = copy.deepcopy(interface); mutant["root_rebind_law"]["source_root_must_differ_from_destination_root"] = False; mutants.append(("ROOT_IDENTITY_TRANSFER", mutant))
    mutant = copy.deepcopy(interface); mutant["cleanup_law"]["token_discharge_count"] = 2; mutants.append(("DOUBLE_CLEANUP", mutant))
    mutant = copy.deepcopy(interface); mutant["actor_scope_law"]["retained_authority_axes"] = ["STATE_REGION_MUTATION"]; mutants.append(("ACTOR_AUTHORITY", mutant))
    mutant = copy.deepcopy(interface); mutant["race_and_terminal_law"]["winner_count"] = 2; mutants.append(("DOUBLE_WINNER", mutant))
    mutant = copy.deepcopy(interface); mutant["projection_entry_maps"].pop(); mutants.append(("PROJECTION_OMISSION", mutant))
    mutant = copy.deepcopy(interface); mutant["projection_entry_maps"][0]["address_as_identity"] = True; mutants.append(("ADDRESS_IDENTITY", mutant))
    mutant = copy.deepcopy(interface); mutant["dispatch_entry_law"]["arbitrary_runtime_to_generated_callback_authority"] = True; mutants.append(("ARBITRARY_CALLBACK", mutant))
    mutant = copy.deepcopy(interface); mutant["seam_status"]["r37_helpers_remain_dependency_unbound"] = True; mutants.append(("SILENT_SIBLING_STACK", mutant))
    mutation_results = {name: bool(interface_errors(value)) for name, value in mutants}
    check("R38_MUTATION_REJECTION_12_OF_12", all(mutation_results.values()), mutation_results)

    failed = [row for row in checks if not row["pass"]]
    receipt = {
        "schema": "deeplus.continuation-interface-validation/r1",
        "result": "PASS" if not failed else "FAIL",
        "baseline_commit": BASELINE_COMMIT,
        "head": head_identity,
        "interface_digest": expected_digest,
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
    raise SystemExit(main())
