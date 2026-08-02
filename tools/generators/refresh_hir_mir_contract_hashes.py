#!/usr/bin/env python3
"""Refresh only byte-identity bindings in the HIR/MIR lowering registry.

Semantic rows remain reviewer-owned.  This helper removes repetitive digest
editing after a reviewed HIR or MIR schema/catalog change and is fail-closed:
the default mode reports drift, while ``--write`` applies the deterministic
projection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REGISTRY_REL = Path("spec/contracts/hir-mir-lowering-registry.json")
BINDING_PATHS = {
    "hir_schema": Path("schemas/language/canonical-hir-h1.schema.json"),
    "hir_identity_catalog": Path("spec/contracts/hir-h1-identity-catalog.json"),
    "mir_schema": Path("schemas/language/deeplus-mir.schema.json"),
    "mir_machine_registry": Path("spec/contracts/mir-machine-registry.json"),
    "lowering_row_schema": Path("schemas/language/hir-mir-lowering-row.schema.json"),
    "fixture_binding_table": Path("tests/fixtures/current/hir-mir-machine-contract-r1.json"),
    "diagnostic_contract": Path("spec/contracts/hir-mir-machine-diagnostic-contract.json"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_load(path: Path) -> dict[str, Any]:
    pairs_seen: list[str] = []

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            result[key] = value
            pairs_seen.append(key)
        return result

    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON number {token!r} in {path}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError(f"registry root is not an object: {path}")
    return value


def projected(root: Path) -> tuple[dict[str, Any], int]:
    registry_path = root / REGISTRY_REL
    registry = strict_load(registry_path)
    bindings = registry.get("contract_bindings")
    rows = registry.get("rows")
    if not isinstance(bindings, dict) or set(bindings) != set(BINDING_PATHS):
        raise ValueError("closed contract binding key set differs")
    if not isinstance(rows, list) or not rows:
        raise ValueError("lowering rows are missing")

    digests = {key: sha256(root / path) for key, path in BINDING_PATHS.items()}
    for key, digest in digests.items():
        row = bindings.get(key)
        if not isinstance(row, dict) or "sha256" not in row:
            raise ValueError(f"binding {key!r} has no sha256 field")
        row["sha256"] = digest

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"lowering row {index} is not an object")
        row["hir_schema_digest"] = digests["hir_schema"]
        row["mir_schema_digest"] = digests["mir_schema"]
    return registry, len(rows)


def render(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    registry_path = root / REGISTRY_REL
    try:
        registry, row_count = projected(root)
        expected = render(registry)
        pending = registry_path.read_bytes() != expected
        if args.write and pending:
            registry_path.write_bytes(expected)
            pending = False
        print(
            "HIR_MIR_BINDING_REFRESH: "
            f"rows={row_count} pending={str(pending).lower()} "
            f"mode={'write' if args.write else 'check'}"
        )
        return 1 if pending else 0
    except Exception as exc:  # noqa: BLE001
        print(f"HIR_MIR_BINDING_REFRESH_ERROR: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
