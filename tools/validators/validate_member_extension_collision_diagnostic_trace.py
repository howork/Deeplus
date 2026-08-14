#!/usr/bin/env python3
"""Validate the bounded R74 member/extension-collision diagnostic trace."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from r78_dpg_trace_successor import (
    CANONICAL_BASELINE as R78_BASELINE,
    COUNTS as R78_COUNTS,
    EVIDENCE_COUNT as R78_EVIDENCE_COUNT,
    GITHUB_PUBLICATION as R78_GITHUB_PUBLICATION,
    is_successor as is_r78_successor,
)


CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "f6581b6fba8f0f48e8b3ac2ea893298e7713d51d"
REVISION = "r74-local-member-extension-collision-diagnostic-trace-closure-r1"
FEATURE = "member_extension_collision_error_policy"
TARGET = (FEATURE, "DIAGNOSTICS", None)
EVIDENCE_ID = "EV-55d02c2cea739b77d7d95070b34e6b350f4aa3b3c0b838597263a576b85115fa"
FEATURE_REF_ID = "EV-c3f43ca9fc5692e6da578ae1a0701cc340951ff85144c9263e69c60a0d358bb4"
NON_TARGET_COUNT = 4220
NON_TARGET_SHA256 = "0f134da58b8045ad157b08b5a3eb7ce32509716eb7ab95fd67ce3e551299d827"
R75_REVISION = "r75-local-actor-cranelift-projection-trace-closure-r1"
R75_PREDECESSOR = "c016871d5aa1c7515fd8a8df181744916f1e1849"
R75_OVERLAY = "spec/traceability/implementation-target-profile-r1/actor-cranelift-projection-dynamic-evidence-r1.json"
R75_TARGETS = {
    ("actor_mailbox_capacity", "DYNAMIC_LOWERING", None),
    ("actor_minimum_lifecycle_r1", "DYNAMIC_LOWERING", None),
    ("actor_request_reply", "DYNAMIC_LOWERING", None),
}
R75_NON_TARGET_COUNT = 4217
R75_NON_TARGET_SHA256 = "d8b2b490eae91d1926c0a30a70951325638c6545c327e2f1d911d1d1e3104417"
R76_REVISION = "r76-global-implementation-target-trace-closure-r1"
R76_PREDECESSOR = "40a826af29410af1a14c6a7dec3193cd59ba9b12"
R76_OVERLAY = "spec/traceability/implementation-target-profile-r1/global-trace-closure-evidence-r1.json"
R76_COUNTS = (3709, 4, 508, 0)
R76_NON_TARGET_SHA256 = "6a81d15917d1b2dc882cd66311ef66d5a9dd07d443e083fc963f34f08db16549"
R77_REVISION = "r77-current-implementation-target-rebind-r1"
R77_BASELINE = "da734c608c0d583a671c0da9e14da00bff42affd"
R77_COUNTS = (3711, 4, 506, 0)
R77_NON_TARGET_SHA256 = "03cbce04ca0b3a06e01972d186ad4b0c5a6987b814463a5d9f9dc53c1b27e34d"

FEATURE_CATALOG = "spec/features/catalog/chunks/part-0009.json"
ROWS = "spec/traceability/implementation-target-profile-r1/rows.json"
METADATA = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
TRACE_SCHEMA = "schemas/language/implementation-target-traceability-r1.schema.json"
R72_CONTRACT = "spec/contracts/member-extension-collision-dynamic-trace-closure-r1.json"
R73_OVERLAY = "spec/traceability/implementation-target-profile-r1/member-extension-collision-conformance-evidence-r1.json"
PREDICATES = "spec/types/predicates/chunks/part-0008.json"
DIAGNOSTICS = "spec/diagnostics/catalog/chunks/part-0011.json"
RELATIONS_A = "spec/diagnostics/relations/chunks/part-0001.json"
RELATIONS_B = "spec/diagnostics/relations/chunks/part-0002.json"

JSON_PATHS = (
    FEATURE_CATALOG, ROWS, METADATA, TRACE_SCHEMA, R72_CONTRACT,
    R73_OVERLAY, PREDICATES, DIAGNOSTICS, RELATIONS_A, RELATIONS_B,
)

GATES = {
    "G01": "canonical_feature_catalog_diagnostic_correction",
    "G02": "predecessor_and_4220_non_target_immutability_fence",
    "G03": "generated_projection_counts_and_metadata",
    "G04": "active_diagnostic_predicate_and_relation_authority",
    "G05": "r72_r73_semantic_and_acceptance_preservation",
    "G06": "design_static_evidence_honesty_and_governance",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_inputs(root: Path) -> Dict[str, Any]:
    return {relative: load(root / relative) for relative in JSON_PATHS}


def evidence_id(item: Mapping[str, Any]) -> str:
    material = "\0".join(str(item.get(key, "")) for key in
        ("class", "path", "locator_kind", "locator", "stage_role"))
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def predecessor_rows(root: Path) -> List[Dict[str, Any]]:
    process = subprocess.run(
        ["git", "-c", "safe.directory=" + root.as_posix(), "-C", str(root),
         "show", PREDECESSOR + ":" + ROWS],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return json.loads(process.stdout.decode("utf-8"))


def trace_cells(rows: List[Dict[str, Any]]) -> Tuple[Dict[Tuple[str, str, Optional[str]], Dict[str, Any]], int]:
    cells: Dict[Tuple[str, str, Optional[str]], Dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        for stage in row.get("stages", []):
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage.get("stage") == "CONFORMANCE_TESTS" else None
                key = (row.get("feature_id"), stage.get("stage"), outcome)
                duplicates += key in cells
                cells[key] = cell
    return cells, duplicates


def non_target_digest(cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]]) -> Tuple[int, str]:
    material = [[*key, value] for key, value in cells.items() if key != TARGET]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def r75_successor_non_target_digest(
    cells: Mapping[Tuple[str, str, Optional[str]], Dict[str, Any]],
) -> Tuple[int, str]:
    """Fence every atomic cell except the exact R74 and R75 targets."""
    material = [
        [*key, value]
        for key, value in cells.items()
        if key not in ({TARGET} | R75_TARGETS)
    ]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return len(material), hashlib.sha256(raw).hexdigest()


def find_by(rows: List[Dict[str, Any]], key: str, value: str) -> Dict[str, Any]:
    return next((row for row in rows if row.get(key) == value), {})


def validate(root: Path, *, overrides: Optional[Mapping[str, Any]] = None,
             predecessor_rows_override: Optional[List[Dict[str, Any]]] = None) -> List[str]:
    values = load_inputs(root)
    if overrides:
        values.update(overrides)
    errors: List[str] = []
    value = lambda relative: values[relative]

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(gate + ":" + code)

    feature_rows = value(FEATURE_CATALOG)
    rows = value(ROWS)
    metadata = value(METADATA)
    contract = value(R72_CONTRACT)
    r73 = value(R73_OVERLAY)
    predicates = value(PREDICATES)
    diagnostics = value(DIAGNOSTICS)
    relations = value(RELATIONS_A) + value(RELATIONS_B)

    require(value(TRACE_SCHEMA).get("$schema") == "https://json-schema.org/draft/2020-12/schema",
            "G01", "SCHEMA_DIALECT")
    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        for document_path, schema_path in ((METADATA, TRACE_SCHEMA),):
            try:
                schema = value(schema_path)
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema.Draft202012Validator(schema).validate(value(document_path))
            except Exception as exc:
                errors.append("G01:JSON_SCHEMA_BINDING:" + type(exc).__name__)

    feature = find_by(feature_rows, "feature_id", FEATURE)
    require(
        feature.get("normative_trace_refs", {}).get("diagnostics")
        == ["MEMBER_EXTENSION_COLLISION"]
        and feature.get("normative_trace_refs", {}).get("predicates")
        == ["MemberExtensionCollisionPolicyAdmitted", "MemberExtensionCollisionRejected"]
        and feature.get("product_support") == "NOT_RUN"
        and feature.get("feature_id") == FEATURE,
        "G01", "FEATURE_CATALOG_DIAGNOSTIC_REF_EXACT",
    )

    before_rows = predecessor_rows_override or predecessor_rows(root)
    before_cells, before_duplicates = trace_cells(before_rows)
    before_count, before_digest = non_target_digest(before_cells)
    before_target = before_cells.get(TARGET, {})
    require(
        before_duplicates == 0
        and before_target.get("disposition") == "NOT_APPLICABLE"
        and before_target.get("not_applicable", {}).get("reason_code")
        == "NA_DIAGNOSTIC_NO_REJECTION_WARNING_OR_INFO_CONDITION",
        "G02", "PREDECESSOR_TARGET_EXACT",
    )
    require(before_count == NON_TARGET_COUNT and before_digest == NON_TARGET_SHA256,
            "G02", "NON_TARGET_4220_EXACT")

    current_cells, current_duplicates = trace_cells(rows)
    current_count, current_digest = non_target_digest(current_cells)
    current = current_cells.get(TARGET, {})
    require(
        current.get("disposition") == "BOUND_DIRECT"
        and current.get("evidence_refs") == [EVIDENCE_ID, FEATURE_REF_ID]
        and current.get("delegate_feature_id") is None
        and current.get("not_applicable") is None
        and current.get("blocked_gap_ids") == [],
        "G03", "GENERATED_TARGET_EXACT",
    )
    applied = metadata.get("applied_evidence_overlays", [])
    registry = metadata.get("evidence_registry", [])
    derived = metadata.get("derived_counts", {})
    r75_successor = (
        metadata.get("revision") == R75_REVISION
        and metadata.get("local_predecessor_commit") == R75_PREDECESSOR
        and applied[-1]
        == {"path": R75_OVERLAY, "feature_count": 3, "binding_count": 3}
    )
    r76_successor = (
        metadata.get("revision") == R76_REVISION
        and metadata.get("local_predecessor_commit") == R76_PREDECESSOR
        and applied[-1]
        == {"path": R76_OVERLAY, "feature_count": 409, "binding_count": 1242}
    )
    r77_successor = (
        metadata.get("revision") == R77_REVISION
        and metadata.get("canonical_baseline_commit") == R77_BASELINE
        and metadata.get("local_predecessor_commit") == R77_BASELINE
        and applied[-1]
        == {"path": R76_OVERLAY, "feature_count": 409, "binding_count": 1242}
    )
    r78_successor = is_r78_successor(metadata, root=root, rows=rows)
    global_successor = r76_successor or r77_successor or r78_successor
    require(
        current_duplicates == 0
        and (
            (
                global_successor
                and (
                    r78_successor
                    or (
                        current_count == NON_TARGET_COUNT
                        and current_digest == (R77_NON_TARGET_SHA256 if r77_successor else R76_NON_TARGET_SHA256)
                    )
                )
            )
            or (
                r75_successor
                and r75_successor_non_target_digest(current_cells)
                == (R75_NON_TARGET_COUNT, R75_NON_TARGET_SHA256)
            )
            or (
                not (r75_successor or global_successor)
                and current_count == NON_TARGET_COUNT
                and current_digest == NON_TARGET_SHA256
            )
        )
        and (metadata.get("revision") == REVISION or r75_successor or global_successor)
        and metadata.get("canonical_baseline_commit")
        == (R78_BASELINE if r78_successor else R77_BASELINE if r77_successor else R76_PREDECESSOR if r76_successor else R75_PREDECESSOR if r75_successor else CANONICAL)
        and (metadata.get("local_predecessor_commit") == PREDECESSOR or r75_successor or global_successor)
        and len(applied) == (22 if global_successor else 20 if r75_successor else 19)
        and {"path": R73_OVERLAY, "feature_count": 1, "binding_count": 2}
        in applied
        and sum(row.get("binding_count", 0) for row in applied)
        == (1416 if global_successor else 139 if r75_successor else 136)
        and len(registry) == (R78_EVIDENCE_COUNT if r78_successor else 4392 if r77_successor else 4393 if r76_successor else 3151 if r75_successor else 3148)
        and sum(row.get("evidence_id") == EVIDENCE_ID for row in registry) == 1,
        "G03", "GENERATED_METADATA_EXACT",
    )
    require(
        (derived.get("bound_direct_cells"), derived.get("bound_delegated_cells"),
         derived.get("not_applicable_cells"), derived.get("applicable_blocked_cells"))
        == (R78_COUNTS if r78_successor else R77_COUNTS if r77_successor else R76_COUNTS if r76_successor else (2473, 4, 502, 1242) if r75_successor else (2470, 4, 502, 1245))
        and derived.get("missing_cells") == 0 and derived.get("conflict_cells") == 0,
        "G03", "GENERATED_COUNTS_EXACT",
    )

    predicate = find_by(predicates, "predicate_id", "MemberExtensionCollisionRejected")
    diagnostic = find_by(diagnostics, "diagnostic_id", "MEMBER_EXTENSION_COLLISION")
    primary = [row for row in relations if row.get("diagnostic_id") == "MEMBER_EXTENSION_COLLISION"
               and row.get("predicate_id") == "MemberExtensionCollisionRejected"]
    require(
        predicate.get("active_primary_diagnostic") == "MEMBER_EXTENSION_COLLISION"
        and predicate.get("diagnostic_refs") == ["MEMBER_EXTENSION_COLLISION"]
        and predicate.get("secondary_diagnostics") == []
        and predicate.get("emission_eligible") is True
        and predicate.get("product_support") == "NOT_RUN",
        "G04", "PREDICATE_PRIMARY_EXACT",
    )
    require(
        diagnostic.get("diagnostic_status") == "active"
        and diagnostic.get("diagnostic_maturity") == "active"
        and diagnostic.get("severity") == "error"
        and diagnostic.get("stage") == "checker"
        and diagnostic.get("diagnostic_class") == "current_source"
        and diagnostic.get("emission_domain") == "source"
        and diagnostic.get("product_support") == "NOT_RUN"
        and primary == [{"violation_id": "MemberExtensionCollisionRejected:default",
                         "predicate_id": "MemberExtensionCollisionRejected",
                         "diagnostic_id": "MEMBER_EXTENSION_COLLISION", "relation": "primary"}],
        "G04", "DIAGNOSTIC_AND_RELATION_EXACT",
    )

    fence = contract.get("diagnostic_fence", {})
    require(
        fence.get("sole_active_primary") == "MEMBER_EXTENSION_COLLISION"
        and fence.get("secondary_diagnostics") == []
        and fence.get("same_stage_generic_fallback_winner_count") == 0
        and r73.get("revision") == "r73-local-member-extension-collision-conformance-trace-closure-r1"
        and len(r73.get("bindings", [])) == 2
        and {row.get("outcome") for row in r73.get("bindings", [])} == {"BOUNDARY", "REJECT"},
        "G05", "R72_R73_CONTRACT_PRESERVATION",
    )

    governance = metadata.get("governance", {})
    require(
        governance.get("semantic_p0") == 0
        and governance.get("feature_p1") == "22_OPEN_UNCHANGED"
        and governance.get("m13_actions") == "4_OPEN_UNCHANGED"
        and governance.get("product_lanes") == "15_OF_15_NOT_RUN"
        and governance.get("github_publication")
        == (R78_GITHUB_PUBLICATION if r78_successor else "R77_SEMANTIC_SURFACE_INTEGRATED_ON_MAIN" if r77_successor else "NOT_YET_PUBLISHED" if r76_successor else "SUSPENDED"),
        "G06", "GOVERNANCE_AND_PRODUCT_FENCE",
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
    metadata = load(root / METADATA)
    rows = load(root / ROWS)
    current_cells, _duplicates = trace_cells(rows)
    current_successor = is_r78_successor(metadata, root=root, rows=rows)
    derived = metadata.get("derived_counts", {})
    r75_successor = metadata.get("revision") == R75_REVISION
    receipt = {
        "schema": "deeplus.r74-member-extension-collision-diagnostic-trace-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL", "feature_id": FEATURE,
        "transitioned_cell_count": 1, "stage": "DIAGNOSTICS",
        "disposition": "BOUND_DIRECT", "projected_counts": {
            "bound_direct": derived.get("bound_direct_cells"),
            "bound_delegated": derived.get("bound_delegated_cells"),
            "not_applicable": derived.get("not_applicable_cells"),
            "applicable_blocked": derived.get("applicable_blocked_cells"),
        }, "non_target_cell_count": (
            sum(1 for key in current_cells if key != TARGET)
            if current_successor
            else R75_NON_TARGET_COUNT
            if r75_successor
            else NON_TARGET_COUNT
        ),
        "product_execution": "15_OF_15_NOT_RUN", "github_publication": "SUSPENDED",
        "gates": GATES, "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
