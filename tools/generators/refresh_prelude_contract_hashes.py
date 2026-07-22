#!/usr/bin/env python3
"""Refresh or verify normalized Prelude row contract identities."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CHUNK_ROOT = "library/prelude/signatures/chunks"


def normalized_hash(row: dict[str, Any]) -> str:
    contract = {key: value for key, value in row.items() if key != "normalized_contract_sha256"}
    material = json.dumps(
        contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    chunk_root = (root / CHUNK_ROOT).resolve()
    if root not in chunk_root.parents:
        raise ValueError("Prelude chunk root escapes workspace")

    pending = 0
    rows = 0
    for path in sorted(chunk_root.glob("part-*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        for row in document:
            rows += 1
            expected = normalized_hash(row)
            if row.get("normalized_contract_sha256") != expected:
                pending += 1
                row["normalized_contract_sha256"] = expected
        if args.write:
            path.write_bytes(
                (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            )
    mode_name = "WRITE" if args.write else "CHECK"
    print(f"PRELUDE_CONTRACT_HASH_{mode_name}: rows={rows} pending={pending}")
    return 1 if args.check and pending else 0


if __name__ == "__main__":
    raise SystemExit(main())
