#!/usr/bin/env python3
"""Build a deterministic Deeplus source snapshot and non-self-referential tree manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import tomllib
import zipfile
from pathlib import Path


EXCLUDED_PARTS = {".git", "target", "dist", "__pycache__"}
MANIFEST = "release/source-tree-manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in rel.parts) or rel.as_posix() == MANIFEST:
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    version = tomllib.loads((root / "current/language-version.toml").read_text(encoding="utf-8"))
    revision = version["spec_revision"]
    rows = []
    for path in source_files(root):
        rel = path.relative_to(root).as_posix()
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha(path)})
    tree_material = "\n".join(f"{row['path']}\0{row['sha256']}" for row in rows).encode()
    manifest = {
        "schema": "deeplus.source-tree-manifest/v1",
        "revision": revision,
        "source_baseline": "0.1.2-baseline.r51f3",
        "file_count_excluding_manifest": len(rows),
        "total_bytes_excluding_manifest": sum(row["bytes"] for row in rows),
        "tree_sha256": hashlib.sha256(tree_material).hexdigest(),
        "self_hash_policy": "manifest is excluded; archive digest is recorded externally",
        "files": rows,
    }
    manifest_path = root / MANIFEST
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    all_files = source_files(root) + [manifest_path]
    all_files.sort(key=lambda path: path.relative_to(root).as_posix())
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in all_files:
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"Deeplus_Canonical_Workspace/{rel}", (2026, 7, 15, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    archive_sha = sha(output)
    print(json.dumps({
        "schema": "deeplus.source-archive-build/v1",
        "result": "PASS",
        "output": output.name,
        "archive_sha256": archive_sha,
        "archive_bytes": output.stat().st_size,
        "file_count": len(all_files),
        "tree_sha256": manifest["tree_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
