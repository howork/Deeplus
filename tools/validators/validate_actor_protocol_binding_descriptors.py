#!/usr/bin/env python3
"""Validate the rebased R41/R23 closed Actor Protocol binding projection."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


VISIBILITY_RANK = {"private": 0, "common": 1, "public": 2}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PROFILE = "R41_DIRECT_CONFORMANCE_R23_BINDING"
EMPTY_SUBSTITUTION_ID = "SubstitutionId:empty"
ROW_FIELDS = {
    "binding_id",
    "binding_row_sha256",
    "requirement_id",
    "requirement_origin_protocol_id",
    "implementation_id",
    "implementation_kind",
    "normalized_selector",
    "requirement_contract_sha256",
    "implementation_contract_sha256",
    "compatibility_proof_sha256",
    "normalized_implementation_error_set",
    "normalized_implementation_effect_row",
    "responsibility_id",
    "reply_responsibility_sha256_or_null",
    "effective_transport_visibility",
}
TABLE_SET_FIELDS = {
    "schema",
    "profile",
    "projection_kind",
    "projection_owner_id",
    "tables",
    "origin_receipts",
    "table_set_sha256",
    "runtime_lookup_count",
    "runtime_fallback_count",
    "link_order_winner_count",
}


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


def expected_binding_id(conformance_id: str, requirement_id: str) -> str:
    return identity(
        "ActorProtocolBindingId",
        "deeplus.actor-protocol-binding/v1",
        {
            "conformance_id": conformance_id,
            "requirement_id": requirement_id,
        },
    )


def table_failures(table: dict[str, Any], projection_kind: str) -> set[str]:
    failures: set[str] = set()
    owner = {
        "actor_id": table.get("actor_id"),
        "actor_protocol_id": table.get("actor_protocol_id"),
        "substitution_id": table.get("substitution_id"),
        "authority_id": table.get("authority_id"),
    }
    expected_table_id = identity(
        "ActorProtocolBindingTableId",
        "deeplus.actor-protocol-binding-table/v1",
        owner,
    )
    expected_conformance = identity(
        "ActorProtocolConformanceId",
        "deeplus.actor-protocol-conformance/v1",
        owner,
    )
    if table.get("table_id") != expected_table_id:
        failures.add("ACTOR_PROTOCOL_BINDING_IDENTITY_MISMATCH")
    if table.get("conformance_id") != expected_conformance:
        failures.add("ACTOR_PROTOCOL_BINDING_IDENTITY_MISMATCH")
    if table.get("substitution_id") != EMPTY_SUBSTITUTION_ID:
        failures.add("ACTOR_PROTOCOL_BINDING_PROFILE_INVALID")
    if table.get("actor_identity_domain") != "STATIC_ACTOR_DECLARATION_ID":
        failures.add("ACTOR_PROTOCOL_BINDING_IDENTITY_MISMATCH")
    if not str(table.get("declaring_package_id", "")).startswith("PackageId:"):
        failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
    if not str(table.get("declaring_module_id", "")).startswith("ModuleId:"):
        failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")

    actor_visibility = table.get("actor_visibility")
    protocol_visibility = table.get("actor_protocol_visibility")
    if actor_visibility not in VISIBILITY_RANK or protocol_visibility not in VISIBILITY_RANK:
        failures.add("ACTOR_PROTOCOL_BINDING_VISIBILITY_INVALID")
        effective = None
    else:
        effective = min(
            (actor_visibility, protocol_visibility),
            key=lambda value: VISIBILITY_RANK[value],
        )
    if table.get("effective_transport_visibility") != effective:
        failures.add("ACTOR_PROTOCOL_BINDING_VISIBILITY_INVALID")
    if projection_kind == "MODULE_API" and effective == "private":
        failures.add("ACTOR_PROTOCOL_BINDING_VISIBILITY_INVALID")

    rows = table.get("bindings", [])
    requirement_ids = table.get("requirement_ids", [])
    row_keys = [
        (row.get("requirement_id"), row.get("binding_id"))
        for row in rows
        if isinstance(row, dict)
    ]
    if row_keys != sorted(row_keys):
        failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")
    row_requirement_ids = [key[0] for key in row_keys]
    if len(row_requirement_ids) != len(set(row_requirement_ids)):
        failures.add("ACTOR_PROTOCOL_BINDING_REQUIREMENT_DUPLICATE")
    if set(requirement_ids) - set(row_requirement_ids):
        failures.add("ACTOR_PROTOCOL_BINDING_REQUIREMENT_MISSING")
    if set(row_requirement_ids) - set(requirement_ids):
        failures.add("ACTOR_PROTOCOL_BINDING_REQUIREMENT_DUPLICATE")
    if requirement_ids != sorted(requirement_ids):
        failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")

    for row in rows:
        if set(row) != ROW_FIELDS:
            failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")
        if row.get("requirement_origin_protocol_id") != table.get(
            "actor_protocol_id"
        ):
            failures.add("ACTOR_PROTOCOL_BINDING_IDENTITY_MISMATCH")
        if row.get("effective_transport_visibility") != effective:
            failures.add("ACTOR_PROTOCOL_BINDING_VISIBILITY_INVALID")
        kind = row.get("implementation_kind")
        implementation = str(row.get("implementation_id", ""))
        reply_digest = row.get("reply_responsibility_sha256_or_null")
        errors = row.get("normalized_implementation_error_set", [])
        if kind == "SEND_TO_ON":
            if not implementation.startswith("ActorHandlerId:"):
                failures.add("ACTOR_PROTOCOL_BINDING_IMPLEMENTATION_KIND_MISMATCH")
            if errors != [] or reply_digest is not None:
                failures.add("ACTOR_PROTOCOL_BINDING_RESPONSIBILITY_INVALID")
        elif kind == "REQUEST_TO_REQUEST":
            if not implementation.startswith("ActorRequestId:"):
                failures.add("ACTOR_PROTOCOL_BINDING_IMPLEMENTATION_KIND_MISMATCH")
            if SHA256.fullmatch(str(reply_digest or "")) is None:
                failures.add("ACTOR_PROTOCOL_BINDING_RESPONSIBILITY_INVALID")
        else:
            failures.add("ACTOR_PROTOCOL_BINDING_IMPLEMENTATION_KIND_MISMATCH")
        if not str(row.get("responsibility_id", "")).startswith(
            "ResponsibilityId:"
        ):
            failures.add("ACTOR_PROTOCOL_BINDING_RESPONSIBILITY_INVALID")
        expected_binding = expected_binding_id(
            table["conformance_id"],
            row["requirement_id"],
        )
        if row.get("binding_id") != expected_binding:
            failures.add("ACTOR_PROTOCOL_BINDING_IDENTITY_MISMATCH")
        for field in (
            "normalized_implementation_error_set",
            "normalized_implementation_effect_row",
        ):
            values = row.get(field, [])
            if values != sorted(values) or len(values) != len(set(values)):
                failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")
            if any(
                item in {
                    "mailboxFull",
                    "receiverClosedBeforeAdmission",
                    "Cancellation",
                    "Defect",
                }
                for item in values
            ):
                failures.add("ACTOR_PROTOCOL_BINDING_FAILURE_AXIS_INVALID")
        for field in (
            "requirement_contract_sha256",
            "implementation_contract_sha256",
            "compatibility_proof_sha256",
        ):
            if SHA256.fullmatch(str(row.get(field, ""))) is None:
                failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")
        if row.get("binding_row_sha256") != self_digest(
            row, "binding_row_sha256"
        ):
            failures.add("ACTOR_PROTOCOL_BINDING_ROW_DIGEST_MISMATCH")
    if table.get("table_sha256") != self_digest(table, "table_sha256"):
        failures.add("ACTOR_PROTOCOL_BINDING_TABLE_DIGEST_MISMATCH")
    return failures


def table_set_failures(payload: dict[str, Any]) -> set[str]:
    failures: set[str] = set()
    kind = payload.get("projection_kind")
    if (
        set(payload) != TABLE_SET_FIELDS
        or payload.get("schema")
        != "deeplus.actor-protocol-binding-table-set/r1"
        or payload.get("profile") != PROFILE
        or kind
        not in {"MODULE_API", "MODULE_IMPLEMENTATION", "EXECUTABLE_IMAGE"}
    ):
        failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")
    owner = str(payload.get("projection_owner_id", ""))
    origins = payload.get("origin_receipts", [])
    if kind in {"MODULE_API", "MODULE_IMPLEMENTATION"}:
        if not owner.startswith("ModuleId:") or origins != []:
            failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
    elif kind == "EXECUTABLE_IMAGE":
        if not owner.startswith("ExecutableImageId:") or not origins:
            failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
    if payload.get("runtime_lookup_count") != 0:
        failures.add("ACTOR_PROTOCOL_BINDING_RUNTIME_LOOKUP_FORBIDDEN")
    if payload.get("runtime_fallback_count") != 0:
        failures.add("ACTOR_PROTOCOL_BINDING_RUNTIME_LOOKUP_FORBIDDEN")
    if payload.get("link_order_winner_count") != 0:
        failures.add("ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID")
    tables = payload.get("tables", [])
    ids = [table.get("table_id") for table in tables if isinstance(table, dict)]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        failures.add("ACTOR_PROTOCOL_BINDING_IDENTITY_MISMATCH")
    for table in tables:
        failures.update(table_failures(table, kind))
    if kind == "EXECUTABLE_IMAGE":
        covered_ids: list[str] = []
        for receipt in origins:
            if not str(receipt.get("declaring_package_id", "")).startswith(
                "PackageId:"
            ):
                failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
            if not str(receipt.get("declaring_module_id", "")).startswith(
                "ModuleId:"
            ):
                failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
            for field in (
                "interface_sha256",
                "implementation_sha256",
                "compilation_receipt_sha256",
                "visibility_closure_sha256",
            ):
                if SHA256.fullmatch(str(receipt.get(field, ""))) is None:
                    failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
            covered_ids.extend(receipt.get("table_ids", []))
        if sorted(covered_ids) != sorted(ids) or len(covered_ids) != len(
            set(covered_ids)
        ):
            failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
        for table in tables:
            matches = [
                receipt
                for receipt in origins
                if table["table_id"] in receipt.get("table_ids", [])
                and table["declaring_module_id"]
                == receipt.get("declaring_module_id")
                and table["declaring_package_id"]
                == receipt.get("declaring_package_id")
            ]
            if len(matches) != 1:
                failures.add("ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID")
    if payload.get("table_set_sha256") != self_digest(
        payload, "table_set_sha256"
    ):
        failures.add("ACTOR_PROTOCOL_BINDING_TABLE_DIGEST_MISMATCH")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    args = parser.parse_args()
    root = args.root.resolve()

    def load(path: str) -> dict[str, Any]:
        return json.loads((root / path).read_text(encoding="utf-8"))

    fixture = load(
        "tests/fixtures/current/actor-protocol-binding-table-r1.json"
    )
    contract = load("spec/contracts/actor-protocol-binding-descriptor.json")
    direct_contract = load(
        "spec/contracts/actor-protocol-direct-conformance-r1.json"
    )
    table_schema = load(
        "schemas/language/actor-protocol-binding-table.schema.json"
    )
    module_api_schema = load("schemas/language/module-api-digest.schema.json")
    implementation_schema = load(
        "schemas/language/module-implementation-digest.schema.json"
    )
    receipt_schema = load(
        "schemas/language/module-compilation-receipt.schema.json"
    )
    mir_schema = load("schemas/language/mir-responsibility.schema.json")
    checks: list[tuple[bool, str]] = []

    def check(condition: bool, code: str) -> None:
        checks.append((bool(condition), code))

    check(
        fixture.get("baseline_commit")
        == "53bbc11cf4b4b5980ae07c04f97a41d7bdd12012",
        "R23_EXACT_BASELINE",
    )
    check(fixture.get("profile") == PROFILE, "R23_PROFILE")
    check(
        direct_contract["identity_contract"]["binding_key"]
        == ["ActorProtocolConformanceId", "ActorProtocolRequirementId"]
        == contract["identity"]["binding_key"]
        == table_schema["x-deeplus-identity-contract"][
            "binding_id_preimage"
        ],
        "R23_R41_BINDING_KEY_PARITY",
    )
    check(
        contract["authority"]["r22_byte_contribution_count"] == 0,
        "R23_R22_NOT_STACKED",
    )
    check(
        contract["authority"]["r24_scope_absorbed_count"] == 0,
        "R23_R24_NOT_ABSORBED",
    )
    check(
        contract.get("product_lanes") == "15/15_NOT_RUN",
        "R23_PRODUCT_NOT_RUN",
    )

    projections = fixture.get("projections", {})
    check(
        set(projections)
        == {"MODULE_API", "MODULE_IMPLEMENTATION", "EXECUTABLE_IMAGE"},
        "R23_PROJECTION_SET",
    )
    for name, payload in projections.items():
        check(payload.get("projection_kind") == name, f"R23_{name}_KIND")
        check(not table_set_failures(payload), f"R23_{name}_VALID")
    api = projections["MODULE_API"]
    implementation = projections["MODULE_IMPLEMENTATION"]
    executable = projections["EXECUTABLE_IMAGE"]
    check(len(api["tables"]) == 1, "R23_API_EXCLUDES_PRIVATE")
    check(
        len(implementation["tables"]) == 2,
        "R23_IMPLEMENTATION_INCLUDES_PRIVATE",
    )
    expected_api = [
        table
        for table in implementation["tables"]
        if table["effective_transport_visibility"] in {"common", "public"}
    ]
    check(api["tables"] == expected_api, "R23_API_EXACT_FILTER")
    check(
        executable["tables"] == implementation["tables"],
        "R23_EXECUTABLE_EXACT_UNION_SINGLE_MODULE_FIXTURE",
    )
    check(
        executable["projection_owner_id"].startswith("ExecutableImageId:"),
        "R23_EXECUTABLE_OWNER_DOMAIN",
    )
    check(
        all(
            table["substitution_id"] == EMPTY_SUBSTITUTION_ID
            for table in implementation["tables"]
        ),
        "R23_CURRENT_EMPTY_SUBSTITUTION",
    )

    table_rows = {
        (
            table["actor_id"],
            table["conformance_id"],
            row["requirement_id"],
            row["binding_id"],
        ): (table, row)
        for table in implementation["tables"]
        for row in table["bindings"]
    }
    proofs = fixture.get("typed_hir_binding_proofs", [])
    proof_rows = {
        (
            proof["table_actor_id"],
            proof["actor_protocol_conformance_id"],
            proof["actor_protocol_requirement_id"],
            proof["actor_protocol_binding_id"],
        ): proof
        for proof in proofs
    }
    check(table_rows.keys() == proof_rows.keys(), "R23_HIR_TABLE_BIJECTION")
    for key, (table, row) in table_rows.items():
        proof = proof_rows[key]
        expected_impl = (
            proof["actor_handler_id_or_null"]
            if proof["implementation_kind"] == "SEND_TO_ON"
            else proof["actor_request_id_or_null"]
        )
        check(row["implementation_id"] == expected_impl, "R23_HIR_IMPLEMENTATION")
        check(
            row["responsibility_id"] == proof["responsibility_id"],
            "R23_HIR_RESPONSIBILITY",
        )
        check(
            row["compatibility_proof_sha256"]
            == proof["compatibility_proof_sha256"],
            "R23_HIR_COMPATIBILITY_PROOF",
        )

    selections = fixture.get("mir_selections", [])
    selection_rows = {
        (
            row["actor_protocol_conformance_id"],
            row["actor_protocol_requirement_id"],
            row["actor_protocol_binding_id"],
        ): row
        for row in selections
    }
    check(
        len(selection_rows) == len(proofs) == len(selections),
        "R23_MIR_SELECTION_CARDINALITY",
    )
    for (_, table, row), proof in [
        ((key, table, row), proof_rows[key])
        for key, (table, row) in table_rows.items()
    ]:
        selection = selection_rows[
            (
                proof["actor_protocol_conformance_id"],
                proof["actor_protocol_requirement_id"],
                proof["actor_protocol_binding_id"],
            )
        ]
        check(
            selection["actor_protocol_binding_table_id"] == table["table_id"],
            "R23_MIR_TABLE_ID",
        )
        check(
            selection["binding_row_sha256"] == row["binding_row_sha256"],
            "R23_MIR_ROW_DIGEST",
        )
        check(selection["runtime_lookup_count"] == 0, "R23_MIR_LOOKUP_ZERO")

    original_table = implementation["tables"][-1]
    original_row = original_table["bindings"][0]
    rebound = copy.deepcopy(original_table)
    rebound_row = rebound["bindings"][0]
    rebound_row["implementation_contract_sha256"] = "f" * 64
    rebound_row["binding_row_sha256"] = self_digest(
        rebound_row, "binding_row_sha256"
    )
    rebound["table_sha256"] = self_digest(rebound, "table_sha256")
    check(
        rebound["table_id"] == original_table["table_id"]
        and rebound_row["binding_id"] == original_row["binding_id"],
        "R23_CONTENT_REBIND_STABLE_IDS",
    )
    check(
        rebound_row["binding_row_sha256"]
        != original_row["binding_row_sha256"]
        and rebound["table_sha256"] != original_table["table_sha256"],
        "R23_CONTENT_REBIND_CHANGES_DIGESTS",
    )

    corrupted = copy.deepcopy(api)
    corrupted["tables"][0]["table_sha256"] = "0" * 64
    check(
        "ACTOR_PROTOCOL_BINDING_TABLE_DIGEST_MISMATCH"
        in table_set_failures(corrupted),
        "R23_MUTATION_DIGEST_REJECTED",
    )
    missing = copy.deepcopy(api)
    missing["tables"][0]["bindings"].pop()
    check(
        "ACTOR_PROTOCOL_BINDING_REQUIREMENT_MISSING"
        in table_set_failures(missing),
        "R23_MUTATION_MISSING_REJECTED",
    )
    runtime_lookup = copy.deepcopy(api)
    runtime_lookup["runtime_lookup_count"] = 1
    check(
        "ACTOR_PROTOCOL_BINDING_RUNTIME_LOOKUP_FORBIDDEN"
        in table_set_failures(runtime_lookup),
        "R23_MUTATION_RUNTIME_LOOKUP_REJECTED",
    )
    wrong_owner = copy.deepcopy(executable)
    wrong_owner["projection_owner_id"] = "ModuleId:not-an-image"
    check(
        "ACTOR_PROTOCOL_BINDING_ORIGIN_INVALID"
        in table_set_failures(wrong_owner),
        "R23_MUTATION_IMAGE_OWNER_REJECTED",
    )
    wrong_axis = copy.deepcopy(api)
    wrong_axis["tables"][0]["bindings"][0][
        "reply_responsibility_sha256_or_null"
    ] = "c" * 64
    check(
        "ACTOR_PROTOCOL_BINDING_RESPONSIBILITY_INVALID"
        in table_set_failures(wrong_axis),
        "R23_MUTATION_WRONG_REPLY_AXIS_REJECTED",
    )
    leaked_reply = copy.deepcopy(api)
    leaked_reply["tables"][0]["bindings"][0]["reply_id"] = "ReplyId:forbidden"
    check(
        "ACTOR_PROTOCOL_BINDING_TABLE_SHAPE_INVALID"
        in table_set_failures(leaked_reply),
        "R23_MUTATION_CONCRETE_REPLY_ID_REJECTED",
    )

    check(
        "R41_ACTOR_PROTOCOL_BINDINGS"
        in module_api_schema["properties"]["interface_profile"]["enum"],
        "R23_MODULE_API_PROFILE",
    )
    check(
        "actor_protocol_binding_tables"
        not in module_api_schema["required"],
        "R23_LEGACY_API_COMPATIBLE",
    )
    check(
        "actor_protocol_binding_tables_sha256"
        not in implementation_schema["required"],
        "R23_LEGACY_IMPLEMENTATION_COMPATIBLE",
    )
    check(
        "actor_protocol_binding_tables_sha256"
        not in receipt_schema["required"],
        "R23_LEGACY_RECEIPT_COMPATIBLE",
    )
    check(
        implementation_schema["x-deeplus-actor-protocol-binding-profile"][
            "binding_profile_requires_present_field"
        ],
        "R23_IMPLEMENTATION_PROFILE_REQUIRED",
    )
    check(
        receipt_schema["x-deeplus-actor-protocol-binding-profile"][
            "binding_profile_requires_present_field"
        ],
        "R23_RECEIPT_PROFILE_REQUIRED",
    )
    mir_fields = set(
        mir_schema["$defs"]["actorProtocolBindingSelection"]["required"]
    )
    check(
        mir_fields
        == set(contract["projections"]["MIR"]["required_fields"])
        | {"runtime_lookup_count"},
        "R23_MIR_EXACT_FIELDS",
    )
    check(
        table_schema["properties"]["runtime_lookup_count"]["const"] == 0
        and table_schema["properties"]["runtime_fallback_count"]["const"] == 0,
        "R23_SCHEMA_RUNTIME_SELECTION_ZERO",
    )

    failed = [code for passed, code in checks if not passed]
    result = {
        "schema": "deeplus.r23-actor-protocol-binding-validation-receipt/r2",
        "result": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failed": failed,
        "product_execution": "NOT_RUN",
        "canonical_source_status": "LOCAL_REBASED_PROJECTION",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
