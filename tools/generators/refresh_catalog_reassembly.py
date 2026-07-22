#!/usr/bin/env python3
"""Deterministically rechunk current checker fixtures and refresh catalog identities."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REASSEMBLY = "migration/catalog-reassembly.json"
CHECKER_ROOT = "tests/conformance/checker-predicates"
MAX_SHARD_BYTES = 61440


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def canonical_sha(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes root: {relative}")
    return candidate


def shard_rows(rows: list[Any]) -> list[list[Any]]:
    chunks: list[list[Any]] = []
    current: list[Any] = []
    for row in rows:
        candidate = [*current, row]
        if current and len(json_bytes(candidate)) > MAX_SHARD_BYTES:
            chunks.append(current)
            current = [row]
        else:
            current = candidate
    if current:
        chunks.append(current)
    if any(len(json_bytes(chunk)) > MAX_SHARD_BYTES for chunk in chunks):
        raise ValueError("one catalog row exceeds the shard byte limit")
    return chunks


def desired_checker_shards(root: Path) -> dict[Path, bytes]:
    chunk_root = safe(root, f"{CHECKER_ROOT}/chunks")
    rows: list[Any] = []
    for path in sorted(chunk_root.glob("part-*.json")):
        value = read_json(path)
        if not isinstance(value, list):
            raise ValueError(f"not an array shard: {path}")
        rows.extend(value)
    return {
        chunk_root / f"part-{index:04d}.json": json_bytes(chunk)
        for index, chunk in enumerate(shard_rows(rows), start=1)
    }


def rendered_reassembly(root: Path, checker_shards: dict[Path, bytes]) -> bytes:
    document = read_json(safe(root, REASSEMBLY))
    for contract in document["contracts"]:
        shard_root = safe(root, f"{contract['shard_root']}/chunks")
        paths = sorted(shard_root.glob("part-*.json"))
        if contract["shard_root"] == CHECKER_ROOT:
            paths = sorted(checker_shards)
        rows: list[Any] = []
        for path in paths:
            value = (
                json.loads(checker_shards[path].decode("utf-8"))
                if path in checker_shards
                else read_json(path)
            )
            if not isinstance(value, list):
                raise ValueError(f"not an array shard: {path}")
            rows.extend(value)
        metadata = read_json(safe(root, contract["metadata_path"]))
        reconstructed = dict(metadata)
        reconstructed[contract["array_key"]] = rows
        contract["row_count"] = len(rows)
        contract["ordered_shard_paths"] = [
            path.relative_to(root).as_posix() for path in paths
        ]
        contract["canonical_object_sha256"] = canonical_sha(reconstructed)
    return json_bytes(document)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    desired = desired_checker_shards(root)
    checker_root = safe(root, f"{CHECKER_ROOT}/chunks")
    actual = set(checker_root.glob("part-*.json"))
    pending = actual != set(desired)
    pending = pending or any(path.read_bytes() != data for path, data in desired.items() if path.is_file())

    if args.write:
        for path, data in desired.items():
            if not path.is_file() or path.read_bytes() != data:
                path.write_bytes(data)
        for stale in sorted(actual - set(desired)):
            if stale.resolve().parent != checker_root:
                raise ValueError(f"refuse stale path outside checker chunks: {stale}")
            stale.unlink()

    reassembly = rendered_reassembly(root, desired)
    reassembly_path = safe(root, REASSEMBLY)
    reassembly_pending = reassembly_path.read_bytes() != reassembly
    if args.write and reassembly_pending:
        reassembly_path.write_bytes(reassembly)

    mode_name = "WRITE" if args.write else "CHECK"
    total_pending = pending or reassembly_pending
    print(
        f"CATALOG_REASSEMBLY_{mode_name}: checker_shards={len(desired)} "
        f"pending={total_pending}"
    )
    return 1 if args.check and total_pending else 0


if __name__ == "__main__":
    raise SystemExit(main())
