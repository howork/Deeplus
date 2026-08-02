#!/usr/bin/env python3
"""Rebind R20 HIR/MIR schema digests without reformatting the registry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PATHS = {
    "hir_schema": "schemas/language/canonical-hir-h1.schema.json",
    "hir_catalog": "spec/contracts/hir-h1-identity-catalog.json",
    "mir_schema": "schemas/language/deeplus-mir.schema.json",
    "mir_registry": "spec/contracts/mir-machine-registry.json",
    "row_schema": "schemas/language/hir-mir-lowering-row.schema.json",
    "fixtures": "tests/fixtures/current/hir-mir-machine-contract-r1.json",
    "diagnostics": "spec/contracts/hir-mir-machine-diagnostic-contract.json",
}

BINDINGS = {
    "hir_schema": "hir_schema",
    "hir_catalog": "hir_identity_catalog",
    "mir_schema": "mir_schema",
    "mir_registry": "mir_machine_registry",
    "row_schema": "lowering_row_schema",
    "fixtures": "fixture_binding_table",
    "diagnostics": "diagnostic_contract",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    registry_path = root / "spec/contracts/hir-mir-lowering-registry.json"
    text = registry_path.read_text(encoding="utf-8")
    registry = json.loads(text)
    new = {key: digest(root / value) for key, value in PATHS.items()}
    counts: dict[str, int] = {}
    for key, binding in BINDINGS.items():
        old_value = registry["contract_bindings"][binding]["sha256"]
        if old_value == new[key]:
            counts[key] = 0
            continue
        count = text.count(old_value)
        if count == 0:
            raise SystemExit(f"R20_REBIND_OLD_DIGEST_NOT_FOUND:{key}")
        text = text.replace(old_value, new[key])
        counts[key] = count
    json.loads(text)
    if args.write:
        with registry_path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    print(json.dumps({"result": "PASS", "mode": "write" if args.write else "check", "replacement_counts": counts, "digests": new}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
