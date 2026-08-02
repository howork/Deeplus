#!/usr/bin/env python3
"""Generate the deterministic R41/R23 Actor Protocol binding fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "tests/fixtures/current/actor-protocol-binding-table-r1.json"
VISIBILITY_RANK = {"private": 0, "common": 1, "public": 2}
PROFILE = "R41_DIRECT_CONFORMANCE_R23_BINDING"
EMPTY_SUBSTITUTION_ID = "SubstitutionId:empty"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def self_digest(value: dict[str, Any], field: str) -> str:
    return sha256({key: item for key, item in value.items() if key != field})


def identity(kind: str, domain: str, value: Any) -> str:
    digest = hashlib.sha256(
        domain.encode("utf-8") + b"\0" + canonical_bytes(value)
    ).hexdigest()
    return f"{kind}:{digest}"


def visibility_meet(left: str, right: str) -> str:
    return min((left, right), key=lambda value: VISIBILITY_RANK[value])


def binding_id(conformance_id: str, requirement_id: str) -> str:
    return identity(
        "ActorProtocolBindingId",
        "deeplus.actor-protocol-binding/v1",
        {
            "conformance_id": conformance_id,
            "requirement_id": requirement_id,
        },
    )


def build_table(
    *,
    package_id: str,
    module_id: str,
    actor_name: str,
    actor_visibility: str,
    protocol_visibility: str,
    operations: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    actor_id = f"ActorId:{actor_name}"
    protocol_id = "ActorProtocolId:CounterProtocol"
    authority_id = "AuthorityId:r41-direct-conformance-fixture"
    owner = {
        "actor_id": actor_id,
        "actor_protocol_id": protocol_id,
        "substitution_id": EMPTY_SUBSTITUTION_ID,
        "authority_id": authority_id,
    }
    conformance_id = identity(
        "ActorProtocolConformanceId",
        "deeplus.actor-protocol-conformance/v1",
        owner,
    )
    effective = visibility_meet(actor_visibility, protocol_visibility)
    rows: list[dict[str, Any]] = []
    proofs: list[dict[str, Any]] = []
    for operation in operations:
        requirement_id = operation["requirement_id"]
        stable_binding_id = binding_id(conformance_id, requirement_id)
        row: dict[str, Any] = {
            "binding_id": stable_binding_id,
            "requirement_id": requirement_id,
            "requirement_origin_protocol_id": protocol_id,
            "implementation_id": operation["implementation_id"],
            "implementation_kind": operation["implementation_kind"],
            "normalized_selector": operation["normalized_selector"],
            "requirement_contract_sha256": operation[
                "requirement_contract_sha256"
            ],
            "implementation_contract_sha256": operation[
                "implementation_contract_sha256"
            ],
            "compatibility_proof_sha256": operation[
                "compatibility_proof_sha256"
            ],
            "normalized_implementation_error_set": sorted(
                set(operation["normalized_implementation_error_set"])
            ),
            "normalized_implementation_effect_row": sorted(
                set(operation["normalized_implementation_effect_row"])
            ),
            "responsibility_id": operation["responsibility_id"],
            "reply_responsibility_sha256_or_null": operation[
                "reply_responsibility_sha256_or_null"
            ],
            "effective_transport_visibility": effective,
        }
        row["binding_row_sha256"] = self_digest(row, "binding_row_sha256")
        rows.append(row)
        proofs.append(
            {
                "table_actor_id": actor_id,
                "actor_protocol_conformance_id": conformance_id,
                "actor_protocol_requirement_id": requirement_id,
                "actor_protocol_binding_id": stable_binding_id,
                "implementation_kind": row["implementation_kind"],
                "actor_handler_id_or_null": (
                    row["implementation_id"]
                    if row["implementation_kind"] == "SEND_TO_ON"
                    else None
                ),
                "actor_request_id_or_null": (
                    row["implementation_id"]
                    if row["implementation_kind"] == "REQUEST_TO_REQUEST"
                    else None
                ),
                "responsibility_id": row["responsibility_id"],
                "requirement_contract_sha256": row[
                    "requirement_contract_sha256"
                ],
                "implementation_contract_sha256": row[
                    "implementation_contract_sha256"
                ],
                "compatibility_proof_sha256": row[
                    "compatibility_proof_sha256"
                ],
            }
        )
    rows.sort(key=lambda row: (row["requirement_id"], row["binding_id"]))
    proofs.sort(
        key=lambda proof: (
            proof["actor_protocol_requirement_id"],
            proof["actor_protocol_binding_id"],
        )
    )
    table: dict[str, Any] = {
        "table_id": identity(
            "ActorProtocolBindingTableId",
            "deeplus.actor-protocol-binding-table/v1",
            owner,
        ),
        "declaring_package_id": package_id,
        "declaring_module_id": module_id,
        **owner,
        "actor_identity_domain": "STATIC_ACTOR_DECLARATION_ID",
        "conformance_id": conformance_id,
        "actor_visibility": actor_visibility,
        "actor_protocol_visibility": protocol_visibility,
        "effective_transport_visibility": effective,
        "requirement_ids": sorted(row["requirement_id"] for row in rows),
        "bindings": rows,
    }
    table["table_sha256"] = self_digest(table, "table_sha256")
    return table, proofs


def table_set(
    *,
    projection_kind: str,
    projection_owner_id: str,
    tables: list[dict[str, Any]],
    origin_receipts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if projection_kind == "MODULE_API":
        tables = [
            table
            for table in tables
            if table["effective_transport_visibility"] in {"common", "public"}
        ]
    payload: dict[str, Any] = {
        "schema": "deeplus.actor-protocol-binding-table-set/r1",
        "profile": PROFILE,
        "projection_kind": projection_kind,
        "projection_owner_id": projection_owner_id,
        "tables": sorted(tables, key=lambda table: table["table_id"]),
        "origin_receipts": sorted(
            origin_receipts or [],
            key=lambda receipt: (
                receipt["declaring_module_id"],
                receipt["compilation_receipt_sha256"],
            ),
        ),
        "runtime_lookup_count": 0,
        "runtime_fallback_count": 0,
        "link_order_winner_count": 0,
    }
    payload["table_set_sha256"] = self_digest(payload, "table_set_sha256")
    return payload


def build_fixture() -> dict[str, Any]:
    package_id = "PackageId:fixture"
    module_id = "ModuleId:fixture.actor"
    operations = [
        {
            "requirement_id": "ActorProtocolRequirementId:ping",
            "implementation_id": "ActorHandlerId:ping",
            "implementation_kind": "SEND_TO_ON",
            "normalized_selector": "ping",
            "requirement_contract_sha256": "1" * 64,
            "implementation_contract_sha256": "2" * 64,
            "compatibility_proof_sha256": "3" * 64,
            "normalized_implementation_error_set": [],
            "normalized_implementation_effect_row": [],
            "responsibility_id": "ResponsibilityId:send-unit-no-reply",
            "reply_responsibility_sha256_or_null": None,
        },
        {
            "requirement_id": "ActorProtocolRequirementId:status",
            "implementation_id": "ActorRequestId:status",
            "implementation_kind": "REQUEST_TO_REQUEST",
            "normalized_selector": "status",
            "requirement_contract_sha256": "4" * 64,
            "implementation_contract_sha256": "5" * 64,
            "compatibility_proof_sha256": "6" * 64,
            "normalized_implementation_error_set": ["LookupError"],
            "normalized_implementation_effect_row": ["state"],
            "responsibility_id": "ResponsibilityId:status-reply",
            "reply_responsibility_sha256_or_null": "7" * 64,
        },
    ]
    public, public_proofs = build_table(
        package_id=package_id,
        module_id=module_id,
        actor_name="Counter",
        actor_visibility="public",
        protocol_visibility="public",
        operations=operations,
    )
    private, private_proofs = build_table(
        package_id=package_id,
        module_id=module_id,
        actor_name="PrivateCounter",
        actor_visibility="private",
        protocol_visibility="public",
        operations=operations[:1],
    )
    tables = [private, public]
    receipt = {
        "declaring_package_id": package_id,
        "declaring_module_id": module_id,
        "interface_sha256": "8" * 64,
        "implementation_sha256": "9" * 64,
        "compilation_receipt_sha256": "a" * 64,
        "visibility_closure_sha256": "b" * 64,
        "table_ids": sorted(table["table_id"] for table in tables),
    }
    projections = {
        "MODULE_API": table_set(
            projection_kind="MODULE_API",
            projection_owner_id=module_id,
            tables=tables,
        ),
        "MODULE_IMPLEMENTATION": table_set(
            projection_kind="MODULE_IMPLEMENTATION",
            projection_owner_id=module_id,
            tables=tables,
        ),
        "EXECUTABLE_IMAGE": table_set(
            projection_kind="EXECUTABLE_IMAGE",
            projection_owner_id="ExecutableImageId:fixture",
            tables=tables,
            origin_receipts=[receipt],
        ),
    }
    proof_rows = sorted(
        public_proofs + private_proofs,
        key=lambda proof: (
            proof["table_actor_id"],
            proof["actor_protocol_requirement_id"],
        ),
    )
    mir_selections = []
    table_by_actor = {table["actor_id"]: table for table in tables}
    row_by_key = {
        (table["actor_id"], row["requirement_id"]): row
        for table in tables
        for row in table["bindings"]
    }
    for proof in proof_rows:
        table = table_by_actor[proof["table_actor_id"]]
        row = row_by_key[
            (
                proof["table_actor_id"],
                proof["actor_protocol_requirement_id"],
            )
        ]
        mir_selections.append(
            {
                "actor_protocol_binding_table_id": table["table_id"],
                "actor_protocol_conformance_id": proof[
                    "actor_protocol_conformance_id"
                ],
                "actor_protocol_requirement_id": proof[
                    "actor_protocol_requirement_id"
                ],
                "actor_protocol_binding_id": proof[
                    "actor_protocol_binding_id"
                ],
                "implementation_kind": proof["implementation_kind"],
                "actor_handler_id_or_null": proof[
                    "actor_handler_id_or_null"
                ],
                "actor_request_id_or_null": proof[
                    "actor_request_id_or_null"
                ],
                "responsibility_id": proof["responsibility_id"],
                "binding_row_sha256": row["binding_row_sha256"],
                "runtime_lookup_count": 0,
            }
        )
    return {
        "schema": "deeplus.actor-protocol-binding-table-fixtures/r1",
        "profile": PROFILE,
        "baseline_commit": "53bbc11cf4b4b5980ae07c04f97a41d7bdd12012",
        "canonical_byte_algorithm": "DEEPLUS_CANONICAL_JSON_UTF8_SHA256_V1",
        "typed_hir_binding_proofs": proof_rows,
        "mir_selections": mir_selections,
        "projections": projections,
        "expected": {
            "projection_count": 3,
            "api_table_count": 1,
            "implementation_table_count": 2,
            "executable_table_count": 2,
            "typed_hir_proof_count": 3,
            "mir_selection_count": 3,
            "private_api_export_count": 0,
            "runtime_lookup_count": 0,
            "runtime_fallback_count": 0,
            "link_order_winner_count": 0,
            "product_execution_count": 0,
        },
        "governance": {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "m13_actions": "4_OPEN_UNCHANGED",
            "product_lanes": "15/15_NOT_RUN",
        },
    }


def encoded_fixture() -> bytes:
    return (
        json.dumps(build_fixture(), ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = encoded_fixture()
    if args.check:
        actual = TARGET.read_bytes() if TARGET.exists() else b""
        if actual != expected:
            print(
                json.dumps(
                    {
                        "result": "FAIL_STALE",
                        "target": TARGET.relative_to(ROOT).as_posix(),
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        print(
            json.dumps(
                {
                    "result": "PASS_CURRENT",
                    "target": TARGET.relative_to(ROOT).as_posix(),
                },
                ensure_ascii=False,
            )
        )
        return 0
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(expected)
    print(
        json.dumps(
            {
                "result": "PASS_GENERATED",
                "target": TARGET.relative_to(ROOT).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
