#!/usr/bin/env python3
"""Reassemble deterministic R51f3 compatibility projections from source shards."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def canonical_sha(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.mkdir(parents=True, exist_ok=True)
    contract_doc = json.loads((root / "migration/catalog-reassembly.json").read_text(encoding="utf-8"))
    receipts = []
    for contract in contract_doc["contracts"]:
        metadata = json.loads((root / contract["metadata_path"]).read_text(encoding="utf-8"))
        rows = []
        for path in contract["ordered_shard_paths"]:
            value = json.loads((root / path).read_text(encoding="utf-8"))
            rows.extend(value if isinstance(value, list) else [value])
        document = dict(metadata)
        document[contract["array_key"]] = rows
        digest = canonical_sha(document)
        if digest != contract["canonical_object_sha256"]:
            raise SystemExit(f"reassembly digest mismatch: {contract['legacy_file']}")
        target = output / contract["legacy_file"]
        target.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        receipts.append({"file": target.name, "rows": len(rows), "canonical_object_sha256": digest})
    receipt = {"schema": "deeplus.generated-catalog-export/v1", "result": "PASS", "projections": receipts}
    (output / "catalog-export-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
