#!/usr/bin/env python3
"""Verify that the current workspace validator rejects closure mutations."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools/validators/validate_workspace.py"
BUILDER = ROOT / "tools/release/build_source_archive.py"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def alias_duplicate(root: Path) -> None:
    path = root / "migration/path-aliases.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["aliases"][1]["legacy_name"] = value["aliases"][0]["legacy_name"]
    write_json(path, value)


def oversize_shard(root: Path) -> None:
    path = root / "library/prelude/signatures/chunks/part-0001.json"
    path.write_text(path.read_text(encoding="utf-8") + (" " * 70000), encoding="utf-8")


def broken_schema_ref(root: Path) -> None:
    path = root / "schemas/language/checker-predicate-fixture-row.schema.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.setdefault("$defs", {})["mutation_descriptor"] = {
        "$ref": "./missing-descriptor.schema.json"
    }
    write_json(path, value)


def authority_drift(root: Path) -> None:
    path = root / "spec/language.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nmutation\n", encoding="utf-8")


def post_pr16_unit_hash(root: Path) -> None:
    path = root / "spec/language.md"
    text = path.read_text(encoding="utf-8")
    marker = "<!-- POST_PR16_UNIT_BEGIN:TC-R001 -->\n"
    if text.count(marker) != 1:
        raise RuntimeError("TC-R001 wrapper unavailable")
    path.write_text(text.replace(marker, marker + "mutation\n", 1), encoding="utf-8")


def invalid_gate(root: Path) -> None:
    reassembly = json.loads((root / "migration/catalog-reassembly.json").read_text(encoding="utf-8"))
    contract = next(
        row for row in reassembly["contracts"]
        if row["shard_root"] == "examples/manifests/by-outcome"
    )
    for rel in contract["ordered_shard_paths"]:
        path = root / rel
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            if row.get("expected_outcome") == "accept_with_gate":
                row["source_activation"] = "stdlib"
                write_json(path, rows)
                return


def missing_release_state(root: Path) -> None:
    candidate = root / "release/candidate-state.json"
    pointer = root / "current/current-pointer.json"
    active = candidate if candidate.is_file() else pointer
    active.unlink()


def both_release_states(root: Path) -> None:
    write_json(root / "release/candidate-state.json", {
        "schema": "deeplus.release-candidate-state/v1",
        "candidate_revision": "r51f3-current-publication-m1.3",
        "authority_digest": "mutation",
        "current_pointer_published": False,
    })


def pointer_required_key_missing(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop("language_version")
    write_json(path, value)


def pointer_lane_missing(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["product_lanes"].pop("rust_frontend_parser")
    write_json(path, value)


def pointer_lane_extra(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["product_lanes"]["imaginary_product_lane"] = "NOT_RUN"
    write_json(path, value)


def implementation_status_mismatch(root: Path) -> None:
    path = root / "current/implementation-status.yaml"
    value = path.read_text(encoding="utf-8").replace(
        "  rust_frontend_parser: NOT_RUN", "  rust_frontend_parser: PASSED_FOCUSED"
    )
    path.write_text(value, encoding="utf-8")


def pointer_publication_target_reverted_to_historical(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["publication_authority_source"]["commit"] = (
        "b6ff1f6e53ea8a21cfb706864478baa02545d3dd"
    )
    write_json(path, value)


def pointer_publication_target_reverted_to_authority_transition(
    root: Path,
) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["publication_authority_source"]["commit"] = (
        "cfd5946c52571119564b9c8beb430f8dd0356750"
    )
    write_json(path, value)


def pointer_publication_role_conflated_with_audited_baseline(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["publication_authority_source"]["role"] = (
        "document_consistency_repair_base"
    )
    write_json(path, value)


def pointer_audited_baseline_rebound_to_publication(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["audited_implementation_baseline"]["commit"] = (
        "8d81d6747488055cb76da8bda1350b96e576b7b1"
    )
    write_json(path, value)


def pointer_audited_baseline_role_conflated_with_publication(
    root: Path,
) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["audited_implementation_baseline"]["role"] = (
        "publication_authority_source"
    )
    write_json(path, value)


def pointer_tracking_ref_external(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"][0]["tracking_ref"] = "https://github.com/howork/Deeplus/issues/6"
    write_json(path, value)


def expr_consumer_digest_wrong(root: Path) -> None:
    path = root / "roles/prompts/Deeplus_Shared_Work_Role_Charter_Prompt.txt"
    value = path.read_text(encoding="utf-8").replace(
        "42250c554d2d5f9cfb29bbd3668bed40ec1390fce658ac1804f7c6de29b1ac39",
        "0" * 64,
    )
    path.write_text(value, encoding="utf-8")


def historical_binding_claims_current(root: Path) -> None:
    path = root / "release/evidence/current-publication-m1.3-git-binding-receipt.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["current_binding"] = True
    write_json(path, value)


def historical_snapshot_id_empty(root: Path) -> None:
    path = (
        root
        / "release/evidence/current-publication-m1.3-source-snapshot-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["object"]["library_file_id"] = ""
    write_json(path, value)


def historical_snapshot_sha_wrong(root: Path) -> None:
    path = (
        root
        / "release/evidence/current-publication-m1.3-source-snapshot-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["object"]["sha256"] = "0" * 64
    write_json(path, value)


def pointer_snapshot_reintroduced(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["source_snapshot"] = {
        "library_file_id": "libfile_fc490a0ba3348191af7ef847b2558cd3",
        "sha256": (
            "1a330f7a519ef6e823b62310568000586"
            "b6ab155ad2a1fbb65f95a954f0b646f"
        ),
    }
    write_json(path, value)


def pointer_predecessor_wrong(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["previous_pointer"] = "r51f3-nonexistent"
    write_json(path, value)


def pointer_action_binding_missing(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"][0].pop("acceptance_test")
    write_json(path, value)


def pointer_action_id_substitution(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"][0]["id"] = "M13-A001"
    write_json(path, value)


def pointer_review_route_mismatch(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["required_next_reviews"][0] = "M13-A999: Impl_ + Spec_ + Test_"
    write_json(path, value)


def stale_role_memory(root: Path) -> None:
    path = root / "roles/current-memory/Design_Deeplus_Current_Memory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["source_revision"] = "r51f3-post-pr16-preview-design-r4"
    write_json(path, value)


def design_authority_fact_removed(root: Path) -> None:
    path = root / "roles/current-memory/Design_Deeplus_Current_Memory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["current_facts"] = [
        row for row in value["current_facts"] if row.get("id") != "AUTH-001"
    ]
    write_json(path, value)


def sfd_execution_owner_conflated_with_closure_authority(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    sfd = next(
        row for row in value["open_actions"] if row.get("id") == "SFD-P1-009"
    )
    sfd["owner"] = "Codex Design_"
    write_json(path, value)


def sfd_closure_authority_reverted(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    sfd = next(
        row for row in value["open_actions"] if row.get("id") == "SFD-P1-009"
    )
    sfd["target"] = sfd["target"].replace(
        "closure authority: Codex Design_",
        "closure authority: ChatGPT Design_",
    )
    write_json(path, value)


def current_decision_index_missing(root: Path) -> None:
    path = root / "current/decision-index.yaml"
    value = path.read_text(encoding="utf-8")
    entry = (
        "  - path: "
        "decisions/language/Design_Deeplus_Cranelift_Backend_Adoption_R1.md\n"
        "    authority: current_user_delegated_design_adoption\n"
    )
    if value.count(entry) != 1:
        raise RuntimeError("Cranelift decision-index entry unavailable")
    path.write_text(value.replace(entry, "", 1), encoding="utf-8")


def current_decision_index_authority_class_wrong(root: Path) -> None:
    path = root / "current/decision-index.yaml"
    value = path.read_text(encoding="utf-8")
    old = "    authority: current_user_delegated_design_adoption"
    if value.count(old) < 1:
        raise RuntimeError("decision-index authority unavailable")
    path.write_text(
        value.replace(old, "    authority: imported_current_decisions", 1),
        encoding="utf-8",
    )


def current_decision_index_authority_transition_report_missing(
    root: Path,
) -> None:
    path = root / "current/decision-index.yaml"
    value = path.read_text(encoding="utf-8")
    entry = (
        "  - governance/reports/"
        "Design_Deeplus_Codex_Design_Authority_Transition_R1.md\n"
    )
    if value.count(entry) != 1:
        raise RuntimeError("authority-transition report entry unavailable")
    path.write_text(value.replace(entry, "", 1), encoding="utf-8")


def current_decision_index_r4_closure_report_missing(root: Path) -> None:
    path = root / "current/decision-index.yaml"
    value = path.read_text(encoding="utf-8")
    entry = (
        "  - governance/reports/"
        "Design_Deeplus_R4_Name_Resolution_Module_"
        "Publication_Closure_R1.md\n"
    )
    if value.count(entry) != 1:
        raise RuntimeError("R4 closure report entry unavailable")
    path.write_text(value.replace(entry, "", 1), encoding="utf-8")


def r4_closure_receipt_gap_drift(root: Path) -> None:
    path = (
        root
        / "release/evidence/"
        "r4-name-resolution-modules-publication-closure-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["gap_transition"]["rows"][0]["id"] = "IR-RES-P0-MUTATED"
    write_json(path, value)


def r4_closure_receipt_ci_job_drift(root: Path) -> None:
    path = (
        root
        / "release/evidence/"
        "r4-name-resolution-modules-publication-closure-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["semantic_pr_github_ci"][0]["job_id"] = 1
    write_json(path, value)


def r4_closure_receipt_premature_closed(root: Path) -> None:
    path = (
        root
        / "release/evidence/"
        "r4-name-resolution-modules-publication-closure-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["gap_transition"]["closed_count_before_closure_readback"] = 12
    write_json(path, value)


def r4_closure_receipt_feature_p1_closed(root: Path) -> None:
    path = (
        root
        / "release/evidence/"
        "r4-name-resolution-modules-publication-closure-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["action_ledger"]["closed_by_candidate"] = 1
    write_json(path, value)


def r4_closure_receipt_product_overclaim(root: Path) -> None:
    path = (
        root
        / "release/evidence/"
        "r4-name-resolution-modules-publication-closure-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["governance"]["product_lanes"] = "14_OF_15_NOT_RUN"
    write_json(path, value)


def r4_closure_decision_removed(root: Path) -> None:
    path = root / "decisions/language/current-decisions.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    decision_id = (
        "DSGN-CURRENT-R4-NAME-RESOLUTION-MODULES-PUBLICATION-CLOSURE"
    )
    value["laws"] = [
        row for row in value["laws"] if row.get("id") != decision_id
    ]
    value["law_count"] = len(value["laws"])
    write_json(path, value)


def r4_closure_memory_reverted(root: Path) -> None:
    path = root / "roles/current-memory/Design_Deeplus_Current_Memory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    pub = next(
        row for row in value["current_facts"] if row.get("id") == "PUB-001"
    )
    pub["statement"] = "The historical R4 checkpoint is current."
    write_json(path, value)


def r4_independent_test_verdict_drift(root: Path) -> None:
    path = (
        root
        / "release/evidence/"
        "r4-name-resolution-modules-independent-test-verification.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["verdict"] = "NOT_AUDITABLE"
    write_json(path, value)


def authority_transition_report_content_drift(root: Path) -> None:
    path = (
        root
        / "governance/reports/"
        "Design_Deeplus_Codex_Design_Authority_Transition_R1.md"
    )
    path.write_text(
        path.read_text(encoding="utf-8") + "\nmutation\n",
        encoding="utf-8",
    )


def historical_predecessor_receipt_identity_drift(root: Path) -> None:
    path = (
        root
        / "release/evidence/current-publication-m1.3-predecessor-receipt.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    value["pointer_object"]["file_id"] = "file_mutated_but_well_formed"
    write_json(path, value)


def match_guard_annotation_fixit(root: Path) -> None:
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("part-*.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            if row.get("diagnostic_id") == "MATCH_ARM_SINGLE_GUARD_ONLY":
                row["fixit_policy"] = "place the annotation immediately before its target declaration"
                write_json(path, rows)
                return
    raise RuntimeError("MATCH_ARM_SINGLE_GUARD_ONLY not found")


def current_integrity_delta_hash(root: Path) -> None:
    path = root / "migration/current-document-consistency-repair-r2.3-manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["transitions"][0]["approved_current_sha256"] = "0" * 64
    write_json(path, value)


def current_integrity_missing_transition(root: Path) -> None:
    path = root / "tools/generators/current-integrity.contract.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["historical_transitions"].pop()
    write_json(path, value)


def current_integrity_nonowned_reassembly(root: Path) -> None:
    path = root / "migration/catalog-reassembly.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["contracts"][2]["partition_key"] = "mutation"
    write_json(path, value)


def refresh_manifest(root: Path, name: str) -> tuple[bool, str]:
    output = root.parent / f"{name}.zip"
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--root",
            str(root),
            "--output",
            str(output),
            "--allow-dirty-source",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if output.exists():
        output.unlink()
    return result.returncode == 0, result.stderr or result.stdout


def legacy_current_pointer(root: Path) -> None:
    path = root / "spec/frontend/frontend-model.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["authority_bundle"]["exact_syntax"] = (
        "Deeplus_Grammar_0_1_2_R51f3_Current_Canonical.ebnf"
    )
    write_json(path, value)


def run(write_receipt: bool) -> int:
    revision = tomllib.loads(
        (ROOT / "current/language-version.toml").read_text(encoding="utf-8")
    )["spec_revision"]
    candidate_mode = (
        (ROOT / "release/candidate-state.json").is_file()
        and not (ROOT / "current/current-pointer.json").exists()
    )
    mutations: list[tuple[str, Callable[[Path], None], str]] = [
        ("same_count_alias_duplicate", alias_duplicate, "ALIAS_UNIQUENESS"),
        ("unlisted_root_oversize_shard", oversize_shard, "SOURCE_SHARD_SIZE"),
        ("broken_local_schema_ref", broken_schema_ref, "LOCAL_JSON_REF_FILE"),
        ("authority_file_drift", authority_drift, "AUTHORITY_DOMAIN_IDENTITY"),
        ("invalid_gate_activation", invalid_gate, "GATED_EXAMPLE_LAW"),
        ("missing_release_state", missing_release_state, "REQUIRED_PATH"),
        ("both_release_states", both_release_states, "RELEASE_STATE_EXCLUSIVE"),
        ("legacy_basename_in_current_owner", legacy_current_pointer, "CURRENT_LEGACY_BASENAME_CLOSURE"),
        ("pointer_required_key_missing", pointer_required_key_missing, "POINTER_REQUIRED_KEYS"),
        ("pointer_lane_missing", pointer_lane_missing, "POINTER_LANE_PARITY"),
        ("pointer_lane_extra", pointer_lane_extra, "POINTER_LANE_PARITY"),
        ("implementation_status_mismatch", implementation_status_mismatch, "IMPLEMENTATION_STATUS_PARITY"),
        (
            "pointer_publication_target_reverted_to_historical",
            pointer_publication_target_reverted_to_historical,
            "POINTER_PUBLICATION_SOURCE",
        ),
        (
            "pointer_publication_target_reverted_to_authority_transition",
            pointer_publication_target_reverted_to_authority_transition,
            "POINTER_PUBLICATION_SOURCE",
        ),
        (
            "pointer_publication_role_conflated_with_audited_baseline",
            pointer_publication_role_conflated_with_audited_baseline,
            "POINTER_PUBLICATION_SOURCE",
        ),
        (
            "pointer_audited_baseline_rebound_to_publication",
            pointer_audited_baseline_rebound_to_publication,
            "POINTER_AUDITED_BASELINE",
        ),
        (
            "pointer_audited_baseline_role_conflated_with_publication",
            pointer_audited_baseline_role_conflated_with_publication,
            "POINTER_AUDITED_BASELINE",
        ),
        ("pointer_tracking_ref_external", pointer_tracking_ref_external, "POINTER_INTERNAL_TRACKING"),
        ("expr_consumer_digest_wrong", expr_consumer_digest_wrong, "EXPR_CONSUMER_BINDING"),
        ("historical_binding_claims_current", historical_binding_claims_current, "HISTORICAL_PUBLICATION_RECEIPT"),
        ("historical_snapshot_id_empty", historical_snapshot_id_empty, "HISTORICAL_SOURCE_SNAPSHOT_RECEIPT"),
        ("historical_snapshot_sha_wrong", historical_snapshot_sha_wrong, "HISTORICAL_SOURCE_SNAPSHOT_RECEIPT"),
        ("pointer_snapshot_reintroduced", pointer_snapshot_reintroduced, "POINTER_SOURCE_SNAPSHOT"),
        (
            "historical_predecessor_receipt_identity_drift",
            historical_predecessor_receipt_identity_drift,
            "HISTORICAL_PREDECESSOR_RECEIPT",
        ),
        ("pointer_predecessor_wrong", pointer_predecessor_wrong, "POINTER_PREDECESSOR_BINDING"),
        ("pointer_action_binding_missing", pointer_action_binding_missing, "POINTER_ACTION_BINDING"),
        ("pointer_action_id_substitution", pointer_action_id_substitution, "POINTER_ACTION_BINDING"),
        ("pointer_review_route_mismatch", pointer_review_route_mismatch, "POINTER_ACTION_BINDING"),
        ("stale_role_memory", stale_role_memory, "ROLE_MEMORY_CURRENT"),
        ("design_authority_fact_removed", design_authority_fact_removed, "CMA_ROLE_MEMORY_ROTATION"),
        (
            "sfd_execution_owner_conflated_with_closure_authority",
            sfd_execution_owner_conflated_with_closure_authority,
            "SFD_P1_009_AUTHORITY_TRANSITION",
        ),
        ("sfd_closure_authority_reverted", sfd_closure_authority_reverted, "SFD_P1_009_AUTHORITY_TRANSITION"),
        ("current_decision_index_missing", current_decision_index_missing, "CURRENT_DECISION_INDEX_BINDING"),
        (
            "current_decision_index_authority_class_wrong",
            current_decision_index_authority_class_wrong,
            "CURRENT_DECISION_INDEX_BINDING",
        ),
        (
            "current_decision_index_authority_transition_report_missing",
            current_decision_index_authority_transition_report_missing,
            "CURRENT_DECISION_INDEX_BINDING",
        ),
        (
            "current_decision_index_r4_closure_report_missing",
            current_decision_index_r4_closure_report_missing,
            "CURRENT_DECISION_INDEX_BINDING",
        ),
        (
            "r4_closure_receipt_gap_drift",
            r4_closure_receipt_gap_drift,
            "R4_PUBLICATION_CLOSURE_GOVERNANCE",
        ),
        (
            "r4_closure_receipt_ci_job_drift",
            r4_closure_receipt_ci_job_drift,
            "R4_PUBLICATION_CLOSURE_IDENTITY",
        ),
        (
            "r4_closure_receipt_premature_closed",
            r4_closure_receipt_premature_closed,
            "R4_PUBLICATION_CLOSURE_GOVERNANCE",
        ),
        (
            "r4_closure_receipt_feature_p1_closed",
            r4_closure_receipt_feature_p1_closed,
            "R4_PUBLICATION_CLOSURE_GOVERNANCE",
        ),
        (
            "r4_closure_receipt_product_overclaim",
            r4_closure_receipt_product_overclaim,
            "R4_PUBLICATION_CLOSURE_GOVERNANCE",
        ),
        (
            "r4_closure_decision_removed",
            r4_closure_decision_removed,
            "R4_PUBLICATION_CLOSURE_DECISION",
        ),
        (
            "r4_closure_memory_reverted",
            r4_closure_memory_reverted,
            "R4_PUBLICATION_CLOSURE_MEMORY",
        ),
        (
            "r4_independent_test_verdict_drift",
            r4_independent_test_verdict_drift,
            "R4_INDEPENDENT_TEST_VERIFICATION",
        ),
        (
            "authority_transition_report_content_drift",
            authority_transition_report_content_drift,
            "CURRENT_INTEGRITY_GENERATOR_CHECK",
        ),
        ("match_guard_annotation_fixit", match_guard_annotation_fixit, "MATCH_GUARD_FIXIT"),
        ("current_integrity_delta_hash", current_integrity_delta_hash, "CURRENT_DELTA_TRANSITION_EXACT"),
        ("current_integrity_missing_transition", current_integrity_missing_transition, "CURRENT_INTEGRITY_GENERATOR_CHECK"),
        ("current_integrity_nonowned_reassembly", current_integrity_nonowned_reassembly, "CURRENT_INTEGRITY_GENERATOR_CHECK"),
    ]
    if revision.startswith("r51f3-post-pr16-preview-design-r4"):
        mutations.append(
            (
                "post_pr16_normalized_unit_hash",
                post_pr16_unit_hash,
                "CURRENT_INTEGRITY_GENERATOR_CHECK",
            )
        )
    results = []
    with tempfile.TemporaryDirectory(prefix="dw-") as temp:
        base = Path(temp)
        for index, (name, mutate, expected_code) in enumerate(mutations):
            # Keep Windows copies below MAX_PATH even when a tracked authority
            # artifact already has a deliberately descriptive deep path.
            target = base / f"m{index:02d}"
            shutil.copytree(
                ROOT,
                target,
                ignore=shutil.ignore_patterns(
                    ".git",
                    "candidate",
                    "dist",
                    "target",
                    "__pycache__",
                ),
            )
            mutate(target)
            refreshed, refresh_output = refresh_manifest(target, name)
            if not refreshed:
                results.append({
                    "mutation": name,
                    "expected_code": expected_code,
                    "rejected": False,
                    "returncode": -1,
                    "observed_codes": [],
                    "harness_error": refresh_output,
                })
                continue
            command = [sys.executable, str(VALIDATOR), "--root", str(target), "--no-receipt"]
            if candidate_mode:
                command.append("--candidate")
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
            )
            observed_codes: list[str] = []
            try:
                receipt = json.loads(result.stdout)
                observed_codes = [row.split(":", 1)[0] for row in receipt.get("errors", [])]
            except json.JSONDecodeError:
                pass
            results.append({
                "mutation": name,
                "expected_code": expected_code,
                "rejected": result.returncode != 0 and expected_code in observed_codes,
                "returncode": result.returncode,
                "observed_codes": observed_codes,
            })
    rejected = sum(row["rejected"] for row in results)
    receipt = {
        "schema": "deeplus.validator-mutation-receipt/v1",
        "revision": revision,
        "result": "PASS" if rejected == len(results) else "FAIL",
        "mutations": len(results),
        "rejected": rejected,
        "harness_contract": "Each mutation refreshes the source manifest and passes only when the validator rejects with the designated diagnostic code.",
        "product_execution": "NOT_RUN",
        "cases": results,
    }
    if write_receipt:
        receipt_name = (
            "repository-bootstrap-m1.2-validator-mutation-receipt.json"
            if candidate_mode
            else "current-publication-m1.3-validator-mutation-receipt.json"
        )
        write_json(
            ROOT / "release/evidence" / receipt_name,
            receipt,
        )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    return run(args.write_receipt)


if __name__ == "__main__":
    raise SystemExit(main())
