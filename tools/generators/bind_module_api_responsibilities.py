#!/usr/bin/env python3
"""Bind complete responsibility axes into the module API digest fixtures."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "tests/fixtures/imported/module-api-digest-fixtures.json"
CALLABLE_AXIS_NEGATIVE_ID = "MODULE-API-NEG-CALLABLE-AXES-001"
CALLABLE_CHANNEL_DUPLICATE_NEGATIVE_ID = "MODULE-API-NEG-CALLABLE-CHANNEL-ID-001"


def channel(channel_id: str, type_identity: str, ownership: str, cleanup: str) -> dict[str, str]:
    return {
        "channel_id": channel_id,
        "type_identity": type_identity,
        "ownership": ownership,
        "cleanup": cleanup,
    }


def responsibility_profile(symbol: dict[str, Any]) -> dict[str, Any]:
    kind = symbol["kind"]
    if kind == "type":
        return {"profile_kind": "type", "declaration_ownership": "not_applicable"}
    if kind == "conformance":
        return {
            "profile_kind": "conformance",
            "evidence_ownership": "reusable",
            "evidence_cleanup": "none",
        }
    if kind == "static_binding":
        return {
            "profile_kind": "static_binding",
            "value": channel("value", "Int", "reusable", "none"),
        }
    if kind == "function":
        parameter_type = "Record***" if "Record***" in symbol["normalized_signature"] else "Int"
        parameter_id = "named_rest" if parameter_type == "Record***" else "value"
        return {
            "profile_kind": "callable",
            "receiver": None,
            "parameters": [channel(parameter_id, parameter_type, "move", "drop_exactly_once")],
            "result": channel("result", "Unit", "reusable", "none"),
            "captures": [],
        }
    if kind == "method":
        return {
            "profile_kind": "callable",
            "receiver": channel("self", "gamma::Type", "inout", "none"),
            "parameters": [],
            "result": channel("result", "Bool", "reusable", "none"),
            "captures": [],
        }
    raise ValueError(f"unsupported module API symbol kind: {kind}")


def complete_symbol(symbol: dict[str, Any]) -> dict[str, Any]:
    output = dict(symbol)
    output["responsibility_profile"] = responsibility_profile(output)
    output["ownership"] = "not_applicable"
    output["cleanup"] = "not_applicable"
    if output["kind"] not in {"function", "method"}:
        output["cancellation"] = "not_applicable"
        output["suspends"] = "not_applicable"
        output["isolation"] = "not_applicable"
    elif output.get("isolation") == "shared":
        output["isolation"] = "global"
    return output


def canonical_bytes(payload: dict[str, Any]) -> str:
    digest_input = {key: value for key, value in payload.items() if key != "canonical_sha256"}
    return json.dumps(
        digest_input,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def ensure_callable_contract_negative_fixtures(document: dict[str, Any]) -> None:
    """Materialize deterministic negatives from the one complete positive payload."""
    positive_payload = document["positive_fixtures"][0]["payload"]
    by_id = {row["fixture_id"]: row for row in document["negative_fixtures"]}
    required = {
        CALLABLE_AXIS_NEGATIVE_ID: [
            "MODULE_API_CALLABLE_RESPONSIBILITY_AXIS_NOT_APPLICABLE"
        ],
        CALLABLE_CHANNEL_DUPLICATE_NEGATIVE_ID: [
            "MODULE_API_CALLABLE_CHANNEL_ID_DUPLICATE"
        ],
    }
    for fixture_id, expected_errors in required.items():
        if fixture_id not in by_id:
            document["negative_fixtures"].append(
                {
                    "fixture_id": fixture_id,
                    "payload": copy.deepcopy(positive_payload),
                    "expected_errors": expected_errors,
                }
            )
    document["negative_fixture_count"] = len(document["negative_fixtures"])


def apply_intentional_negative(fixture: dict[str, Any]) -> None:
    """Apply the one invalid condition owned by each generated negative."""
    fixture_id = fixture["fixture_id"]
    symbols = fixture["payload"]["symbols"]
    if fixture_id == CALLABLE_AXIS_NEGATIVE_ID:
        function = next(row for row in symbols if row["kind"] == "function")
        function["cancellation"] = "not_applicable"
        function["suspends"] = "not_applicable"
        function["isolation"] = "not_applicable"
    elif fixture_id == CALLABLE_CHANNEL_DUPLICATE_NEGATIVE_ID:
        method = next(row for row in symbols if row["kind"] == "method")
        method["responsibility_profile"]["captures"] = [
            channel("self", "gamma::Type", "borrow", "view_release")
        ]


def bind_fixture(fixture: dict[str, Any]) -> int:
    payload = fixture["payload"]
    changed = 0
    updated_symbols = []
    for symbol in payload["symbols"]:
        updated = complete_symbol(symbol)
        if updated != symbol:
            changed += 1
        updated_symbols.append(updated)
    payload["symbols"] = updated_symbols
    apply_intentional_negative(fixture)

    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    fixture["canonical_bytes_utf8"] = encoded
    fixture["expected_canonical_sha256"] = digest
    if fixture["fixture_id"] != "MODULE-API-NEG-HASH-001":
        payload["canonical_sha256"] = digest
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    document = json.loads(TARGET.read_text(encoding="utf-8"))
    ensure_callable_contract_negative_fixtures(document)
    fixtures = [*document["positive_fixtures"], *document["negative_fixtures"]]
    changed = sum(bind_fixture(fixture) for fixture in fixtures)
    rendered = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    rendered_bytes = rendered.encode("utf-8")
    pending = rendered_bytes != TARGET.read_bytes()
    if args.write and pending:
        TARGET.write_bytes(rendered_bytes)
    mode = "WRITE" if args.write else "CHECK"
    print(f"MODULE_API_RESPONSIBILITY_BIND_{mode}: symbols={changed} pending={pending}")
    return 1 if (pending and not args.write) else 0


if __name__ == "__main__":
    raise SystemExit(main())
