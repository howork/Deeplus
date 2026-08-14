#!/usr/bin/env python3
"""Validate the exact R101 feature-P1 first-target disposition."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_REL = Path("spec/contracts/implementation-target-feature-p1-disposition-r101.json")
SCHEMA_REL = Path("schemas/language/implementation-target-feature-p1-disposition-r101.schema.json")
POINTER_REL = Path("current/current-pointer.json")
R99_REL = Path("spec/contracts/implementation-readiness-r99-audit-closure.json")
TARGET_METADATA_REL = Path("spec/traceability/implementation-target-profile-r1/catalog-metadata.json")
TARGET_ROWS_REL = Path("spec/traceability/implementation-target-profile-r1/rows.json")

EXPECTED_ACTION_IDS = [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
EXPECTED_SUMMARY = {
    "exact_action_count": 22,
    "class_action_count": 6,
    "enum_action_count": 8,
    "trait_action_count": 7,
    "sfd_action_count": 1,
    "first_target_design_open_action_count": 0,
    "open_execution_receipt_count": 22,
    "excluded_successor_action_count": 14,
    "included_implementation_acceptance_count": 8,
}
EXPECTED_GOVERNANCE = {
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "open_feature_p1_count": 22,
    "product_lanes": "15_OF_15_NOT_RUN",
    "production_implementation": "NOT_RUN",
    "github_mutation": 0,
    "canonical_publication": "NOT_PERFORMED",
}
EXPECTED_EXCLUDED_MAPPING = {
    "enum_case_display_mapping_preview_design": ["CE-E-P1-007", "CE-E-P1-008"],
    "enum_declaration_order_ord_preview_design": ["CE-E-P1-007", "CE-E-P1-008"],
    "enum_exact_variant_subset_alias_preview_design": ["CE-E-P1-004", "CE-E-P1-008"],
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_ids(ids: list[str]) -> str:
    return hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()


def feature_catalog_ids(root: Path) -> tuple[set[str], dict[str, str]]:
    ids: set[str] = set()
    statuses: dict[str, str] = {}
    for path in sorted((root / "spec/features/catalog/chunks").glob("part-*.json")):
        rows = load(path)
        for row in rows:
            feature_id = row.get("feature_id")
            if isinstance(feature_id, str):
                ids.add(feature_id)
                statuses[feature_id] = row.get("status_enum")
    return ids, statuses


def action_domain(action_id: str) -> str:
    if action_id.startswith("CE-C-"):
        return "CLASS"
    if action_id.startswith("CE-E-"):
        return "ENUMERATION"
    if action_id.startswith("TCC-"):
        return "TRAIT_CONFORMANCE"
    return "STATIC_FIRST_DYNAMIC"


def has_dependency_cycle(actions: list[dict[str, Any]]) -> bool:
    graph = {
        row.get("id"): row.get("dependencies", [])
        for row in actions
        if isinstance(row.get("id"), str)
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(action_id: str) -> bool:
        if action_id in visiting:
            return True
        if action_id in visited:
            return False
        visiting.add(action_id)
        for dependency in graph.get(action_id, []):
            if dependency in graph and visit(dependency):
                return True
        visiting.remove(action_id)
        visited.add(action_id)
        return False

    return any(visit(action_id) for action_id in graph)


def model_errors(
    root: Path,
    contract: dict[str, Any],
    pointer: dict[str, Any],
    r99: dict[str, Any],
    metadata: dict[str, Any],
    target_rows: list[dict[str, Any]],
    catalog_ids: set[str],
    catalog_statuses: dict[str, str],
) -> list[str]:
    errors: list[str] = []

    if contract.get("schema") != "deeplus.implementation-target-feature-p1-disposition/r101":
        errors.append("CONTRACT_IDENTITY")
    if contract.get("revision") != "r101-implementation-target-feature-p1-disposition":
        errors.append("CONTRACT_REVISION")
    if contract.get("status") != "LOCAL_DESIGN_STATIC_TARGET_DISPOSITION":
        errors.append("CONTRACT_STATUS")
    if contract.get("baseline") != {
        "repository": "howork/Deeplus",
        "branch": "main",
        "observed_commit": "10e64f492f0529610673846139afcf0d95175663",
        "local_predecessor_commit": "9c5f25e9d1e518c75e594f46b2158c510008c379",
        "current_binding": False,
    }:
        errors.append("BASELINE_IDENTITY")
    if contract.get("authority_model") != {
        "successor_to": R99_REL.as_posix(),
        "design_disposition_authority": "Codex Design_",
        "execution_closure_authority": "TARGET_BOUND_EXECUTION_RECEIPT_PLUS_CODEX_DESIGN",
        "evidence_separation": "DESIGN_STATIC_IS_NOT_PRODUCT_EXECUTION",
    }:
        errors.append("AUTHORITY_MODEL")
    if contract.get("summary") != EXPECTED_SUMMARY:
        errors.append("SUMMARY_EXACT_COUNTS")
    if contract.get("governance") != EXPECTED_GOVERNANCE:
        errors.append("GOVERNANCE_FENCE")

    actions = contract.get("actions", [])
    action_ids = [row.get("id") for row in actions if isinstance(row, dict)]
    if action_ids != EXPECTED_ACTION_IDS or len(set(action_ids)) != 22:
        errors.append("ACTION_ID_EXACT_ORDER_UNIQUE")
    action_set = set(action_ids)
    excluded_mapping: dict[str, list[str]] = {}
    retained_ids: set[str] = set()
    included_retained_ids: set[str] = set()
    for index, row in enumerate(actions):
        action_id = row.get("id")
        if action_id not in action_set:
            continue
        expected_included = action_id.startswith("TCC-") or action_id == "SFD-P1-009"
        expected_design = (
            "CLOSED_DESIGN_STATIC"
            if expected_included
            else "EXPLICITLY_DEFERRED_OUTSIDE_FIRST_TARGET"
        )
        expected_disposition = (
            "INCLUDED_IMPLEMENTATION_ACCEPTANCE"
            if expected_included
            else "EXCLUDED_SUCCESSOR_SCOPE_RETAIN_CLOSED_BASE"
        )
        if row.get("domain") != action_domain(action_id):
            errors.append(f"ACTION_DOMAIN:{action_id}")
        if row.get("action_status") != "OPEN":
            errors.append(f"ACTION_STATUS:{action_id}")
        if row.get("design_handoff_gate") != expected_design:
            errors.append(f"ACTION_DESIGN_GATE:{action_id}")
        if row.get("disposition") != expected_disposition:
            errors.append(f"ACTION_DISPOSITION:{action_id}")
        if row.get("execution_receipt_gate") != "OPEN_NOT_RUN":
            errors.append(f"ACTION_EXECUTION_GATE:{action_id}")
        if row.get("product_execution") != "NOT_RUN":
            errors.append(f"ACTION_PRODUCT_EXECUTION:{action_id}")

        retained = row.get("retained_feature_ids", [])
        excluded = row.get("excluded_target_feature_ids", [])
        dependencies = row.get("dependencies", [])
        anchors = row.get("authority_anchors", [])
        if not retained or len(retained) != len(set(retained)):
            errors.append(f"RETAINED_FEATURE_IDS_NONEMPTY_UNIQUE:{action_id}")
        if any(feature_id not in catalog_ids for feature_id in retained):
            errors.append(f"RETAINED_FEATURE_UNKNOWN:{action_id}")
        retained_ids.update(retained)
        if expected_included:
            included_retained_ids.update(retained)
        if len(excluded) != len(set(excluded)) or set(retained) & set(excluded):
            errors.append(f"EXCLUDED_FEATURE_IDS_DISJOINT_UNIQUE:{action_id}")
        if expected_included and excluded:
            errors.append(f"INCLUDED_ACTION_HAS_EXCLUSION:{action_id}")
        for feature_id in excluded:
            excluded_mapping.setdefault(feature_id, []).append(action_id)
        if len(dependencies) != len(set(dependencies)):
            errors.append(f"DEPENDENCY_UNIQUE:{action_id}")
        if any(dependency not in action_set for dependency in dependencies):
            errors.append(f"DEPENDENCY_TARGET:{action_id}")
        if action_id in dependencies:
            errors.append(f"DEPENDENCY_SELF:{action_id}")
        expected_anchors = {
            f"current/current-pointer.json#/open_actions/{index + 5}",
            f"spec/contracts/implementation-readiness-r99-audit-closure.json#/feature_p1_lanes/{index}",
        }
        if not expected_anchors <= set(anchors) or len(anchors) != len(set(anchors)):
            errors.append(f"AUTHORITY_ANCHORS:{action_id}")
        if not isinstance(row.get("acceptance_summary"), str) or not row["acceptance_summary"].strip():
            errors.append(f"ACCEPTANCE_SUMMARY:{action_id}")
    excluded_mapping = {
        feature_id: sorted(action_ids)
        for feature_id, action_ids in sorted(excluded_mapping.items())
    }
    if excluded_mapping != EXPECTED_EXCLUDED_MAPPING:
        errors.append("EXCLUDED_FEATURE_EXACT_MAPPING")
    if has_dependency_cycle(actions):
        errors.append("DEPENDENCY_DAG_CYCLE")

    pointer_actions = [
        row
        for row in pointer.get("open_actions", [])
        if row.get("id") in set(EXPECTED_ACTION_IDS)
    ]
    if [row.get("id") for row in pointer_actions] != EXPECTED_ACTION_IDS:
        errors.append("POINTER_ACTION_EXACT_PARITY")
    for row in pointer_actions:
        if (
            row.get("priority") != "P1"
            or row.get("tracking_ref") != f"deeplus-action:{row.get('id')}"
            or not row.get("acceptance_test")
        ):
            errors.append(f"POINTER_ACTION_CONTRACT:{row.get('id')}")
    pointer_lanes = pointer.get("product_lanes", {})
    if len(pointer_lanes) != 15 or set(pointer_lanes.values()) != {"NOT_RUN"}:
        errors.append("POINTER_PRODUCT_LANES")
    if pointer.get("candidate_binding", {}).get("current_binding") is not False:
        errors.append("POINTER_CURRENT_BINDING")

    r99_lanes = r99.get("feature_p1_lanes", [])
    if [row.get("id") for row in r99_lanes] != EXPECTED_ACTION_IDS:
        errors.append("R99_ACTION_EXACT_PARITY")
    for row in r99_lanes[:14]:
        if (
            row.get("design_contract_gate") != "OPEN_EXCLUSION_TOTALITY_NOT_PROVEN"
            or row.get("execution_receipt_gate") != "OPEN_NOT_RUN"
            or row.get("readiness_effect") != "BLOCKS_FIRST_TARGET_UNTIL_EXACT_EXCLUSION_TOTALITY"
        ):
            errors.append(f"R99_PREDECESSOR_LANE:{row.get('id')}")
    for row in r99_lanes[14:21]:
        if (
            row.get("design_contract_gate") != "PARTIAL_STATIC_ACCEPTANCE_R102_NOT_ACTION_COMPLETE"
            or row.get("execution_receipt_gate") != "OPEN_NOT_RUN"
            or row.get("readiness_effect") != "BLOCKS_FIRST_TARGET_HANDOFF"
        ):
            errors.append(f"R99_PREDECESSOR_LANE:{row.get('id')}")
    if not r99_lanes or (
        r99_lanes[-1].get("design_contract_gate") != "CLOSED_DESIGN_STATIC"
        or r99_lanes[-1].get("execution_receipt_gate") != "OPEN_NOT_RUN"
        or r99_lanes[-1].get("readiness_effect")
        != "RETAINED_IMPLEMENTATION_ACCEPTANCE_BLOCKS_SFD_EXECUTION_CLAIM_ONLY"
    ):
        errors.append("R99_PREDECESSOR_SFD_LANE")

    target_ids = [row.get("feature_id") for row in target_rows]
    target_set = set(target_ids)
    if len(target_ids) != len(target_set):
        errors.append("TARGET_FEATURE_ID_UNIQUE")
    if metadata.get("target_count") != len(target_rows):
        errors.append("TARGET_METADATA_COUNT")
    if retained_ids - target_set:
        errors.append("RETAINED_CLOSED_BASE_NOT_IN_TARGET")
    if included_retained_ids - target_set:
        errors.append("INCLUDED_ACCEPTANCE_NOT_IN_TARGET")
    if set(EXPECTED_EXCLUDED_MAPPING) & target_set:
        errors.append("EXCLUDED_FEATURE_REINSERTED")
    if any(catalog_statuses.get(feature_id) != "STABLE_DESIGN" for feature_id in EXPECTED_EXCLUDED_MAPPING):
        errors.append("EXCLUDED_FEATURE_NOT_STABLE_DESIGN")

    reasons = metadata.get("excluded_current_feature_reasons", {})
    r101_reason_ids = {
        feature_id
        for feature_id, value in reasons.items()
        if value.get("status") == "EXCLUDED_BY_R101_FEATURE_P1_DISPOSITION"
    }
    if r101_reason_ids != set(EXPECTED_EXCLUDED_MAPPING):
        errors.append("TARGET_EXCLUSION_REASON_EXACT_THREE")
    for feature_id, expected_action_ids in EXPECTED_EXCLUDED_MAPPING.items():
        reason = reasons.get(feature_id, {})
        if sorted(reason.get("action_ids", [])) != expected_action_ids:
            errors.append(f"TARGET_EXCLUSION_ACTION_MAPPING:{feature_id}")

    metadata_governance = metadata.get("governance", {})
    if (
        metadata_governance.get("semantic_p0") != 0
        or metadata_governance.get("feature_p1") != "22_OPEN_UNCHANGED"
        or metadata_governance.get("product_lanes") != "15_OF_15_NOT_RUN"
    ):
        errors.append("TARGET_GOVERNANCE_FENCE")
    expected_projection = {
        "contract_path": CONTRACT_REL.as_posix(),
        "contract_sha256": sha256_file(root / CONTRACT_REL),
        "exact_action_ids": EXPECTED_ACTION_IDS,
        "action_count": 22,
        "design_open_in_target_count": 0,
        "execution_open_action_count": 22,
        "excluded_target_feature_mapping": EXPECTED_EXCLUDED_MAPPING,
        "retained_feature_ids": sorted(retained_ids),
        "retained_feature_id_list_sha256": digest_ids(sorted(retained_ids)),
        "tcc_sfd_retained_feature_ids": sorted(included_retained_ids),
        "tcc_sfd_retained_feature_id_list_sha256": digest_ids(
            sorted(included_retained_ids)
        ),
    }
    if metadata_governance.get("r101_feature_p1_disposition") != expected_projection:
        errors.append("TARGET_R101_PROJECTION_BINDING")
    return errors


def mutation_rejections(
    root: Path,
    documents: dict[str, Any],
    catalog_ids: set[str],
    catalog_statuses: dict[str, str],
) -> tuple[int, list[str]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate(name: str) -> dict[str, Any]:
        value = copy.deepcopy(documents)
        mutations.append((name, value))
        return value

    value = mutate("MISSING_ACTION")
    value["contract"]["actions"].pop()
    value = mutate("DUPLICATE_ACTION")
    value["contract"]["actions"][-1] = copy.deepcopy(value["contract"]["actions"][0])
    value = mutate("WRONG_FAMILY")
    value["contract"]["actions"][0]["domain"] = "ENUMERATION"
    value = mutate("WRONG_DESIGN_GATE")
    value["contract"]["actions"][0]["design_handoff_gate"] = "CLOSED_DESIGN_STATIC"
    value = mutate("WRONG_DISPOSITION")
    value["contract"]["actions"][0]["disposition"] = "INCLUDED_IMPLEMENTATION_ACCEPTANCE"
    value = mutate("CLOSED_EXECUTION_GATE")
    value["contract"]["actions"][0]["execution_receipt_gate"] = "CLOSED"
    value = mutate("STALE_TARGET_FEATURE_ID")
    value["contract"]["actions"][14]["retained_feature_ids"][0] = "stale_target_feature_r101"
    value = mutate("EXCLUDED_FEATURE_REINSERTION")
    value["target_rows"].append({"feature_id": "enum_case_display_mapping_preview_design"})
    value = mutate("DEPENDENCY_CYCLE")
    value["contract"]["actions"][0]["dependencies"] = ["CE-C-P1-002"]
    value = mutate("PRODUCT_PASS")
    value["contract"]["actions"][0]["product_execution"] = "PASS"
    value = mutate("EXCLUDED_MAPPING_DRIFT")
    value["contract"]["actions"][12]["excluded_target_feature_ids"].pop()

    survived: list[str] = []
    for mutation_id, value in mutations:
        errors = model_errors(
            root,
            value["contract"],
            value["pointer"],
            value["r99"],
            value["metadata"],
            value["target_rows"],
            catalog_ids,
            catalog_statuses,
        )
        if not errors:
            survived.append(mutation_id)
    return len(mutations) - len(survived), survived


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = load(root / CONTRACT_REL)
    schema = load(root / SCHEMA_REL)
    pointer = load(root / POINTER_REL)
    r99 = load(root / R99_REL)
    metadata = load(root / TARGET_METADATA_REL)
    target_rows = load(root / TARGET_ROWS_REL)
    catalog_ids, catalog_statuses = feature_catalog_ids(root)
    errors: list[str] = []
    schema_properties = schema.get("properties", {})
    action_properties = schema.get("$defs", {}).get("action", {}).get("properties", {})
    summary_properties = schema_properties.get("summary", {}).get("properties", {})
    governance_properties = schema_properties.get("governance", {}).get("properties", {})
    if (
        schema.get("$id")
        != "https://howork.github.io/Deeplus/schemas/language/implementation-target-feature-p1-disposition-r101.schema.json"
        or schema_properties.get("schema", {}).get("const")
        != "deeplus.implementation-target-feature-p1-disposition/r101"
        or schema_properties.get("actions", {}).get("minItems") != 22
        or schema_properties.get("actions", {}).get("maxItems") != 22
        or {
            key: value.get("const")
            for key, value in summary_properties.items()
        }
        != EXPECTED_SUMMARY
        or set(action_properties.get("design_handoff_gate", {}).get("enum", []))
        != {"EXPLICITLY_DEFERRED_OUTSIDE_FIRST_TARGET", "CLOSED_DESIGN_STATIC"}
        or set(action_properties.get("disposition", {}).get("enum", []))
        != {
            "EXCLUDED_SUCCESSOR_SCOPE_RETAIN_CLOSED_BASE",
            "INCLUDED_IMPLEMENTATION_ACCEPTANCE",
        }
        or action_properties.get("execution_receipt_gate", {}).get("const")
        != "OPEN_NOT_RUN"
        or action_properties.get("product_execution", {}).get("const") != "NOT_RUN"
        or {
            key: value.get("const")
            for key, value in governance_properties.items()
        }
        != EXPECTED_GOVERNANCE
    ):
        errors.append("SCHEMA_EXACT_CONTRACT")
    schema_validation = "JSONSCHEMA_DRAFT_2020_12"
    try:
        import jsonschema

        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
    except ImportError:
        schema_validation = "STRICT_STRUCTURAL_FALLBACK"
    except Exception as error:
        errors.append(f"JSON_SCHEMA_VALIDATION:{error}")
    errors.extend(
        model_errors(
            root,
            contract,
            pointer,
            r99,
            metadata,
            target_rows,
            catalog_ids,
            catalog_statuses,
        )
    )
    rejected = 0
    survived: list[str] = []
    if args.mutations and not errors:
        rejected, survived = mutation_rejections(
            root,
            {
                "contract": contract,
                "pointer": pointer,
                "r99": r99,
                "metadata": metadata,
                "target_rows": target_rows,
            },
            catalog_ids,
            catalog_statuses,
        )
        if survived:
            errors.append("MUTATION_SURVIVED:" + ",".join(survived))
    receipt = {
        "schema": "deeplus.implementation-target-feature-p1-disposition-validation/r101",
        "result": "PASS" if not errors else "FAIL",
        "exact_action_count": 22,
        "excluded_successor_action_count": 14,
        "included_implementation_acceptance_count": 8,
        "execution_open_not_run_count": 22,
        "excluded_target_feature_count": 3,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "schema_validation": schema_validation,
        "mutation_rejections": rejected,
        "mutation_total": 11 if args.mutations else 0,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
