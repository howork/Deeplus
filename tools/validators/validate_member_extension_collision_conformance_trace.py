#!/usr/bin/env python3
"""Validate the bounded R73 member/extension-collision conformance trace.

The evidence is a design-static acceptance contract, not parser/checker/runtime
execution.  BOUND_DIRECT here means direct machine-readable specification
evidence while every product lane remains NOT_RUN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "ab1ffd86db91d2b3b93e7c15e43829a7aa4704d3"
REVISION = "r73-local-member-extension-collision-conformance-trace-closure-r1"
R74_REVISION = "r74-local-member-extension-collision-diagnostic-trace-closure-r1"
R74_PREDECESSOR = "f6581b6fba8f0f48e8b3ac2ea893298e7713d51d"
FEATURE = "member_extension_collision_error_policy"
BOUNDARY_TARGET = (FEATURE, "CONFORMANCE_TESTS", "BOUNDARY")
REJECT_TARGET = (FEATURE, "CONFORMANCE_TESTS", "REJECT")
TARGETS = {BOUNDARY_TARGET, REJECT_TARGET}
BOUNDARY_EVIDENCE_ID = "EV-7af9345ab4c98882b2af77fc1814fc0352298f5d5f4dd9d4df357abc824c0c3f"
REJECT_EVIDENCE_ID = "EV-ee837f7a965f93d9d84ad03a394d443692b235c6715b00ab2e748d5dbaf7850e"
NON_TARGET_COUNT = 4219
NON_TARGET_SHA256 = "7448ce347ec8ebf432af540973ec6e56bf9ddbd04049c57d4eca7a23ba544cf7"
R74_TARGET = (FEATURE, "DIAGNOSTICS", None)
R74_EVIDENCE_REFS = [
    "EV-55d02c2cea739b77d7d95070b34e6b350f4aa3b3c0b838597263a576b85115fa",
    "EV-c3f43ca9fc5692e6da578ae1a0701cc340951ff85144c9263e69c60a0d358bb4",
]
R74_TRIPLE_EXCLUSION_COUNT = 4218
R74_TRIPLE_EXCLUSION_SHA256 = "aa4a204990a660ffcef3477ac2f0d1405182c813276349f9934f7cab6b5fb968"
R75_REVISION = "r75-local-actor-cranelift-projection-trace-closure-r1"
R75_PREDECESSOR = "c016871d5aa1c7515fd8a8df181744916f1e1849"
R75_OVERLAY = "spec/traceability/implementation-target-profile-r1/actor-cranelift-projection-dynamic-evidence-r1.json"
R75_TARGETS = {
    ("actor_mailbox_capacity", "DYNAMIC_LOWERING", None),
    ("actor_minimum_lifecycle_r1", "DYNAMIC_LOWERING", None),
    ("actor_request_reply", "DYNAMIC_LOWERING", None),
}
R75_NON_TARGET_COUNT = 4215
R75_NON_TARGET_SHA256 = "fb2e67e12bb3b6fd1c29f15d9c49ae2de6d84ba260070e606d19938afa265c2a"

OVERLAY = "spec/traceability/implementation-target-profile-r1/member-extension-collision-conformance-evidence-r1.json"
OVERLAY_SCHEMA = "schemas/language/member-extension-collision-conformance-evidence-r1.schema.json"
DECISION = "decisions/language/Design_Deeplus_R73_Member_Extension_Collision_Conformance_Trace_Closure_R1.md"
ROWS = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
TRACE_SCHEMA = "schemas/language/implementation-target-traceability-r1.schema.json"
R72_CONTRACT = "spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json"
R72_FIXTURE = "tests/fixtures/current/member-extension-collision-dynamic-trace-closure-r1.json"
FRONTEND = "spec/frontend/frontend-model.json"
PREDICATES = "spec/types/predicates/chunks/part-0008.json"
DIAGNOSTICS = "spec/diagnostics/catalog/chunks/part-0011.json"
MIR_SEMANTICS = "spec/mir/semantics.md"

JSON_PATHS = (
    OVERLAY,
    OVERLAY_SCHEMA,
    ROWS,
    METADATA,
    TRACE_SCHEMA,
    R72_CONTRACT,
    R72_FIXTURE,
    FRONTEND,
    PREDICATES,
    DIAGNOSTICS,
)

GATES = {
    "G01": "overlay_identity_two_evidence_entries_and_bindings",
    "G02": "predecessor_and_4219_non_target_immutability_fence",
    "G03": "generated_projection_counts_and_metadata",
    "G04": "r72_acceptance_partition_and_fixture_parity",
    "G05": "collision_boundary_rejection_and_zero_residue_semantics",
    "G06": "design_static_evidence_honesty_and_governance",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_inputs(root: Path) -> Dict[str, Any]:
    return {relative: load(root / relative) for relative in JSON_PATHS}


def evidence_id(item: Mapping[str, Any]) -> str:
    material = "\0".join(
        str(item.get(key, ""))
        for key in ("class", "path", "locator_kind", "locator", "stage_role")
    )
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def predecessor_rows(root: Path) -> List[Dict[str, Any]]:
    process = subprocess.run(
        [
            "git",
            "-c",
            "safe.directory=" + root.as_posix(),
            "-C",
            str(root),
            "show",
            PREDECESSOR + ":" + ROWS,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(process.stdout.decode("utf-8"))


def trace_cells(
    rows: List[Dict[str, Any]],
) -> Tuple[Dict[Tuple[str, str, Optional[str]], Dict[str, Any]], int]:
    cells: Dict[Tuple[str, str, Optional[str]], Dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        for stage in row.get("stages", []):
            for cell in stage.get("outcomes", [stage]):
                outcome = (
                    cell.get("outcome")
                    if stage.get("stage") == "CONFORMANCE_TESTS"
                    else None
                )
                key = (row.get("feature_id"), stage.get("stage"), outcome)
                duplicates += key in cells
                cells[key] = cell
    return cells, duplicates


def non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    material = [[*key, value] for key, value in cells.items() if key not in TARGETS]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def r74_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R73 and R74 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key not in TARGETS | {R74_TARGET}
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def r75_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R73-R75 targets."""
    excluded = TARGETS | {R74_TARGET} | R75_TARGETS
    material = [[*key, value] for key, value in cells.items() if key not in excluded]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def find_by(rows: List[Dict[str, Any]], key: str, value: str) -> Dict[str, Any]:
    return next((row for row in rows if row.get(key) == value), {})


def validate(
    root: Path,
    *,
    overrides: Optional[Mapping[str, Any]] = None,
    predecessor_rows_override: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    values = load_inputs(root)
    if overrides:
        values.update(overrides)
    errors: List[str] = []

    def value(relative: str) -> Any:
        return values[relative]

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(gate + ":" + code)

    overlay = value(OVERLAY)
    rows = value(ROWS)
    metadata = value(METADATA)
    contract = value(R72_CONTRACT)
    fixture = value(R72_FIXTURE)
    frontend = value(FRONTEND)
    predicates = value(PREDICATES)
    diagnostics = value(DIAGNOSTICS)

    require(
        value(OVERLAY_SCHEMA).get("$schema")
        == "https://json-schema.org/draft/2020-12/schema"
        and value(TRACE_SCHEMA).get("$schema")
        == "https://json-schema.org/draft/2020-12/schema",
        "G01",
        "SCHEMA_DIALECT",
    )
    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        for document_path, schema_path in (
            (OVERLAY, OVERLAY_SCHEMA),
            (METADATA, TRACE_SCHEMA),
        ):
            try:
                schema = value(schema_path)
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema.Draft202012Validator(schema).validate(value(document_path))
            except Exception as exc:
                errors.append("G01:JSON_SCHEMA_BINDING:" + type(exc).__name__)

    # G01: two exact acceptance-set evidence entries bind the two target cells.
    entries = overlay.get("evidence_entries", [])
    bindings = overlay.get("bindings", [])
    entry_by_role = {row.get("stage_role"): row for row in entries}
    binding_by_outcome = {row.get("outcome"): row for row in bindings}
    boundary_entry = entry_by_role.get("CONFORMANCE_TESTS:BOUNDARY", {})
    reject_entry = entry_by_role.get("CONFORMANCE_TESTS:REJECT", {})
    boundary_binding = binding_by_outcome.get("BOUNDARY", {})
    reject_binding = binding_by_outcome.get("REJECT", {})
    require(
        overlay.get("revision") == REVISION
        and overlay.get("canonical_baseline_commit") == CANONICAL
        and overlay.get("local_predecessor_commit") == PREDECESSOR
        and overlay.get("feature_ids") == [FEATURE]
        and len(entries) == len(bindings) == 2,
        "G01",
        "OVERLAY_IDENTITY_AND_CARDINALITY",
    )
    for outcome, entry, expected_id in (
        ("BOUNDARY", boundary_entry, BOUNDARY_EVIDENCE_ID),
        ("REJECT", reject_entry, REJECT_EVIDENCE_ID),
    ):
        require(
            entry.get("class") == "ACCEPTANCE_CASE_SET"
            and entry.get("path") == R72_CONTRACT
            and entry.get("locator_kind") == "JSON_POINTER"
            and entry.get("locator") == "/acceptance_bindings/" + outcome
            and entry.get("stage_role") == "CONFORMANCE_TESTS:" + outcome
            and evidence_id(entry) == expected_id,
            "G01",
            "EXACT_" + outcome + "_EVIDENCE",
        )
        binding = boundary_binding if outcome == "BOUNDARY" else reject_binding
        require(
            binding.get("feature_id") == FEATURE
            and binding.get("stage") == "CONFORMANCE_TESTS"
            and binding.get("outcome") == outcome
            and binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP"
            and binding.get("disposition") == "BOUND_DIRECT"
            and binding.get("evidence_keys") == [entry.get("evidence_key")]
            and binding.get("delegate_feature_id") is None
            and binding.get("not_applicable") is None,
            "G01",
            "EXACT_" + outcome + "_BINDING",
        )

    # G02: the predecessor has two blocked targets and 4,219 exact non-targets.
    before_rows = predecessor_rows_override or predecessor_rows(root)
    before_cells, before_duplicates = trace_cells(before_rows)
    before_count, before_digest = non_target_digest(before_cells)
    require(
        before_duplicates == 0
        and all(
            before_cells.get(target, {}).get("disposition")
            == "APPLICABLE_BLOCKED_BY_GAP"
            and before_cells.get(target, {}).get("blocked_gap_ids")
            == ["IR-XCUT-P1-054"]
            for target in TARGETS
        ),
        "G02",
        "PREDECESSOR_TARGETS_EXACT",
    )
    require(
        before_count == NON_TARGET_COUNT and before_digest == NON_TARGET_SHA256,
        "G02",
        "NON_TARGET_4219_EXACT",
    )

    # G03: generated rows and metadata contain exactly the two transitions.
    current_cells, current_duplicates = trace_cells(rows)
    current_count, current_digest = non_target_digest(current_cells)
    for target, expected_id in (
        (BOUNDARY_TARGET, BOUNDARY_EVIDENCE_ID),
        (REJECT_TARGET, REJECT_EVIDENCE_ID),
    ):
        cell = current_cells.get(target, {})
        require(
            cell.get("disposition") == "BOUND_DIRECT"
            and cell.get("evidence_refs") == [expected_id]
            and cell.get("delegate_feature_id") is None
            and cell.get("not_applicable") is None
            and cell.get("blocked_gap_ids") == [],
            "G03",
            "GENERATED_" + str(target[2]) + "_TARGET_EXACT",
        )
    applied = metadata.get("applied_evidence_overlays", [])
    registry = metadata.get("evidence_registry", [])
    derived = metadata.get("derived_counts", {})
    r74_successor = (
        metadata.get("revision") == R74_REVISION
        and metadata.get("local_predecessor_commit") == R74_PREDECESSOR
    )
    r75_successor = (
        metadata.get("revision") == R75_REVISION
        and metadata.get("local_predecessor_commit") == R75_PREDECESSOR
        and applied[-1]
        == {"path": R75_OVERLAY, "feature_count": 3, "binding_count": 3}
    )
    r74_target = current_cells.get(R74_TARGET, {})
    require(
        current_duplicates == 0
        and (
            (
                r75_successor
                and r75_successor_non_target_digest(current_cells)
                == (R75_NON_TARGET_COUNT, R75_NON_TARGET_SHA256)
            )
            or (
                r74_successor
                and r74_successor_non_target_digest(current_cells)
                == (R74_TRIPLE_EXCLUSION_COUNT, R74_TRIPLE_EXCLUSION_SHA256)
            )
            or (
                not (r74_successor or r75_successor)
                and current_count == NON_TARGET_COUNT
                and current_digest == NON_TARGET_SHA256
            )
        )
        and (metadata.get("revision") == REVISION or r74_successor or r75_successor)
        and metadata.get("canonical_baseline_commit")
        == (R75_PREDECESSOR if r75_successor else CANONICAL)
        and (
            metadata.get("local_predecessor_commit") == PREDECESSOR
            or r74_successor
            or r75_successor
        )
        and len(applied) == (20 if r75_successor else 19)
        and applied[-2 if r75_successor else -1]
        == {"path": OVERLAY, "feature_count": 1, "binding_count": 2}
        and sum(row.get("binding_count", 0) for row in applied)
        == (139 if r75_successor else 136)
        and len(registry) == (3151 if r75_successor else 3148)
        and {BOUNDARY_EVIDENCE_ID, REJECT_EVIDENCE_ID}
        <= {row.get("evidence_id") for row in registry},
        "G03",
        "GENERATED_METADATA_EXACT",
    )
    if r74_successor or r75_successor:
        require(
            r74_target.get("disposition") == "BOUND_DIRECT"
            and r74_target.get("evidence_refs") == R74_EVIDENCE_REFS
            and r74_target.get("delegate_feature_id") is None
            and r74_target.get("not_applicable") is None
            and r74_target.get("blocked_gap_ids") == [],
            "G03",
            "R74_SUCCESSOR_TARGET_EXACT",
        )
    require(
        (
            derived.get("bound_direct_cells"),
            derived.get("bound_delegated_cells"),
            derived.get("not_applicable_cells"),
            derived.get("applicable_blocked_cells"),
        )
        == (
            (2473, 4, 502, 1242)
            if r75_successor
            else (2470, 4, 502, 1245)
            if r74_successor
            else (2469, 4, 503, 1245)
        )
        and derived.get("missing_cells") == 0
        and derived.get("conflict_cells") == 0,
        "G03",
        "GENERATED_COUNTS_EXACT",
    )

    # G04: reuse the exact R72 partition and fixture; do not duplicate it.
    acceptance = contract.get("acceptance_cases", [])
    by_id = {row.get("case_id"): row for row in acceptance}
    fixture_rows = fixture.get("acceptance_oracles", [])
    fixture_by_id = {row.get("case_id"): row for row in fixture_rows}
    all_ids = [f"R72-MECD-ACC-{index:03d}" for index in range(1, 10)]
    boundary_ids = all_ids[2:5]
    reject_ids = all_ids[5:]
    require(
        [row.get("case_id") for row in acceptance] == all_ids
        and [row.get("class") for row in acceptance]
        == ["POSITIVE"] * 2 + ["BOUNDARY"] * 3 + ["REJECT"] * 4
        and contract.get("acceptance_bindings", {}).get("BOUNDARY") == boundary_ids
        and contract.get("acceptance_bindings", {}).get("REJECT") == reject_ids
        and [row.get("case_id") for row in fixture_rows] == all_ids
        and all(fixture_by_id[case_id].get("class") == by_id[case_id].get("class") for case_id in all_ids)
        and all(fixture_by_id[case_id].get("expected") == by_id[case_id].get("expected") for case_id in all_ids),
        "G04",
        "R72_ACCEPTANCE_AND_FIXTURE_PARITY",
    )
    exact_cases = {
        "R72-MECD-ACC-003": (
            "EXACT_DOMAIN_RESTRICTION_BYPASSES_ONLY_CROSS_DOMAIN_COLLISION",
            ["QUALIFIED_DOMAIN_EXACT", "WITHIN_DOMAIN_OWNER_UNCHANGED", "RUNTIME_LOOKUP_ZERO"],
        ),
        "R72-MECD-ACC-004": (
            "NO_ORDER_WINNER_OR_SEMANTIC_DRIFT",
            ["SOURCE_IMPORT_USE_ORDER_WINNER_ZERO", "ADDRESS_LINK_ORDER_WINNER_ZERO"],
        ),
        "R72-MECD-ACC-005": (
            "EXACT_COLLISION_PRIMARY_WINS",
            ["SOLE_ACTIVE_PRIMARY", "GENERIC_FALLBACK_WINNER_ZERO", "SECONDARY_DIAGNOSTICS_EMPTY"],
        ),
        "R72-MECD-ACC-006": (
            "REJECT_SELECTED_COUNT_ZERO_BEFORE_HIR",
            ["BOTH_DOMAINS_NONEMPTY", "SELECTED_COUNT_ZERO", "HIR_RESIDUE_ZERO"],
        ),
        "R72-MECD-ACC-007": (
            "CROSS_DOMAIN_COLLISION_PRECEDES_WITHIN_DOMAIN_RANKING",
            ["WITHIN_DOMAIN_RANKING_BEFORE_COLLISION_FALSE", "SELECTED_COUNT_ZERO"],
        ),
        "R72-MECD-ACC-008": (
            "RECOVERY_HIR_AND_RUNTIME_FALLBACK_ZERO",
            ["RECOVERY_HIR_ZERO", "RUNTIME_FALLBACK_ZERO"],
        ),
        "R72-MECD-ACC-009": (
            "NO_DYNAMIC_OR_BACKEND_RESIDUE",
            ["MIR_RESIDUE_ZERO", "XVM_RESIDUE_ZERO", "RUNTIME_RESIDUE_ZERO", "CRANELIFT_RESIDUE_ZERO"],
        ),
    }
    require(
        all(
            by_id.get(case_id, {}).get("expected") == expected
            and by_id.get(case_id, {}).get("assertion_ids") == assertions
            and by_id.get(case_id, {}).get("execution_state")
            == "DESIGN_STATIC_NOT_RUN"
            for case_id, (expected, assertions) in exact_cases.items()
        ),
        "G04",
        "BOUNDARY_AND_REJECT_CASES_EXACT",
    )

    # G05: bind the checker terminal, qualified boundary, ranking and zero residue.
    static = contract.get("static_collision_owner", {})
    noncollision = contract.get("noncollision_boundary", {})
    diagnostic_fence = contract.get("diagnostic_fence", {})
    pre_hir = contract.get("pre_hir_rejection_boundary", {})
    residue = contract.get("runtime_backend_residue_fence", {})
    collision = frontend.get("r4_name_resolution_module_contract", {}).get(
        "member_extension_collision", {}
    )
    predicate = find_by(predicates, "predicate_id", "MemberExtensionCollisionRejected")
    diagnostic = find_by(diagnostics, "diagnostic_id", "MEMBER_EXTENSION_COLLISION")
    mir_text = (root / MIR_SEMANTICS).read_text(encoding="utf-8")
    require(
        static.get("both_domains_nonempty") == "REJECT_MEMBER_EXTENSION_COLLISION"
        and static.get("within_domain_ranking_before_collision") is False
        and static.get("selected_count_on_collision") == 0
        and static.get("source_import_use_or_activation_order_winner_count") == 0
        and noncollision.get("qualified_extension_selector")
        == "RESTRICT_TO_EXACT_EXTENSION_DOMAIN_AND_BYPASS_ONLY_CROSS_DOMAIN_COLLISION"
        and noncollision.get("qualified_selector_within_domain_winner_owned_by_this_contract")
        is False
        and collision.get("selected_count") == 0
        and collision.get("source_import_or_activation_order_winner") is False,
        "G05",
        "COLLISION_AND_QUALIFIED_BOUNDARY_EXACT",
    )
    require(
        diagnostic_fence.get("sole_active_primary") == "MEMBER_EXTENSION_COLLISION"
        and diagnostic_fence.get("secondary_diagnostics") == []
        and diagnostic_fence.get("same_stage_generic_fallback_winner_count") == 0
        and predicate.get("active_primary_diagnostic") == "MEMBER_EXTENSION_COLLISION"
        and predicate.get("secondary_diagnostics") == []
        and "selected_count = 0" in predicate.get("success_result", "")
        and diagnostic.get("diagnostic_status") == "active"
        and diagnostic.get("stage") == "checker",
        "G05",
        "SOLE_PRIMARY_DIAGNOSTIC_EXACT",
    )
    require(
        all(value == 0 for value in pre_hir.values())
        and all(value == 0 for value in residue.values())
        and "produces no\nselected reference or MIR" in mir_text,
        "G05",
        "PRE_HIR_AND_DOWNSTREAM_RESIDUE_ZERO",
    )

    # G06: BOUND_DIRECT does not upgrade design-static evidence to execution.
    guards = overlay.get("guards", {})
    counts = overlay.get("counts", {})
    governance = metadata.get("governance", {})
    require(
        overlay.get("candidate_status")
        == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY"
        and all(
            row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in acceptance
        )
        and fixture.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
        and all(
            row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in overlay.get("acceptance_cases", [])
        ),
        "G06",
        "DESIGN_STATIC_NOT_RUN_EXACT",
    )
    require(
        counts.get("feature_count") == 1
        and counts.get("evidence_entry_count") == 2
        and counts.get("binding_count") == 2
        and counts.get("overlay_bound_direct_transition_count") == 2
        and counts.get("post_overlay_total_bound_direct_cell_count") == 2469
        and counts.get("post_overlay_total_bound_delegated_cell_count") == 4
        and counts.get("post_overlay_total_not_applicable_cell_count") == 503
        and counts.get("post_overlay_total_blocked_cell_count") == 1245
        and counts.get("post_overlay_missing_cell_count") == 0
        and counts.get("post_overlay_conflict_cell_count") == 0,
        "G06",
        "OVERLAY_COUNTS_EXACT",
    )
    require(
        guards.get("transitioned_cell_count") == 2
        and guards.get("other_cell_transition_count") == 0
        and guards.get("other_atomic_cell_count") == NON_TARGET_COUNT
        and guards.get("other_atomic_cell_sha256") == NON_TARGET_SHA256
        and guards.get("semantic_p0") == 0
        and guards.get("feature_p1") == "22_OPEN_UNCHANGED"
        and guards.get("m13_actions") == "4_OPEN_UNCHANGED"
        and guards.get("product_lanes") == "15_OF_15_NOT_RUN"
        and guards.get("github_publication") == "SUSPENDED"
        and guards.get("product_execution_receipt_count") == 0
        and guards.get("implementation_claim") == "NONE"
        and governance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and governance.get("github_publication") == "SUSPENDED",
        "G06",
        "GOVERNANCE_AND_PRODUCT_FENCE",
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = validate(root)
    except (FileNotFoundError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        errors = ["INPUT:" + str(exc)]
    receipt = {
        "schema": "deeplus.r73-member-extension-collision-conformance-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "feature_id": FEATURE,
        "transitioned_cell_count": 2,
        "outcomes": ["BOUNDARY", "REJECT"],
        "disposition": "BOUND_DIRECT",
        "projected_counts": {
            "bound_direct": load(root / METADATA).get("derived_counts", {}).get("bound_direct_cells"),
            "bound_delegated": load(root / METADATA).get("derived_counts", {}).get("bound_delegated_cells"),
            "not_applicable": load(root / METADATA).get("derived_counts", {}).get("not_applicable_cells"),
            "applicable_blocked": load(root / METADATA).get("derived_counts", {}).get("applicable_blocked_cells"),
        },
        "non_target_cell_count": (
            R75_NON_TARGET_COUNT
            if load(root / METADATA).get("revision") == R75_REVISION
            else R74_TRIPLE_EXCLUSION_COUNT
            if load(root / METADATA).get("revision") == R74_REVISION
            else NON_TARGET_COUNT
        ),
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "gates": GATES,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
