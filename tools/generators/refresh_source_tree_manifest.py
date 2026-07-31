#!/usr/bin/env python3
"""Refresh or check the canonical source-tree manifest from the Git index.

The Git index is the only source-content input.  This keeps a candidate freeze
independent from unrelated worktree files and avoids building an archive merely
to refresh ``release/source-tree-manifest.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib


MANIFEST_REL = "release/source-tree-manifest.json"
VERSION_REL = "current/language-version.toml"
EXCLUDED_PARTS = {
    ".git",
    "target",
    "dist",
    "candidate",
    "tmp",
    "__pycache__",
}
ALLOWED_MODES = {"100644", "100755"}
SCHEMA = "deeplus.source-tree-manifest/v1"
SOURCE_BASELINE = "0.1.2-baseline.r51f3"
SELF_HASH_POLICY = "manifest is excluded; archive digest is recorded externally"


class ManifestError(RuntimeError):
    """A deterministic source-manifest validation failure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class IndexEntry:
    mode: str
    oid: str
    path: str


def fail(code: str, detail: str) -> None:
    raise ManifestError(code, detail)


def git_command(root: Path, *arguments: str) -> list[str]:
    return [
        "git",
        "-c",
        f"safe.directory={root.as_posix()}",
        "-C",
        str(root),
        *arguments,
    ]


def run_git(root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            git_command(root, *arguments),
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        fail("SOURCE_MANIFEST_GIT_UNAVAILABLE", str(exc))
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        fail("SOURCE_MANIFEST_GIT_FAILURE", detail or "git command failed")
    return result.stdout


def normalized_path(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path.resolve())))


def verify_repository_root(root: Path) -> None:
    observed_bytes = run_git(root, "rev-parse", "--show-toplevel")
    try:
        observed = Path(observed_bytes.decode("utf-8").strip()).resolve()
    except (UnicodeDecodeError, OSError) as exc:
        fail("SOURCE_MANIFEST_REPOSITORY_ROOT", str(exc))
    if normalized_path(observed) != normalized_path(root):
        fail(
            "SOURCE_MANIFEST_REPOSITORY_ROOT",
            f"expected={root} observed={observed}",
        )


def decode_nul_paths(payload: bytes, code: str) -> list[str]:
    try:
        values = payload.decode("utf-8").split("\0")
    except UnicodeDecodeError as exc:
        fail(code, str(exc))
    return [value for value in values if value]


def validate_index_path(path: str) -> None:
    pure = PurePosixPath(path)
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or any(part in {"", ".", ".."} for part in path.split("/"))
        or pure.as_posix() != path
    ):
        fail("SOURCE_MANIFEST_UNSAFE_INDEX_PATH", repr(path))


def index_entries(root: Path) -> list[IndexEntry]:
    payload = run_git(root, "ls-files", "--stage", "-z")
    entries: list[IndexEntry] = []
    seen: set[str] = set()
    for record in payload.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode_bytes, oid_bytes, stage_bytes = metadata.split(b" ", 2)
            mode = mode_bytes.decode("ascii")
            oid = oid_bytes.decode("ascii")
            stage = stage_bytes.decode("ascii")
            path = raw_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            fail("SOURCE_MANIFEST_INDEX_RECORD", str(exc))
        validate_index_path(path)
        if stage != "0":
            fail("SOURCE_MANIFEST_UNMERGED_INDEX", path)
        if mode not in ALLOWED_MODES:
            fail(
                "SOURCE_MANIFEST_NONREGULAR_INDEX_ENTRY",
                f"path={path} mode={mode}",
            )
        if path in seen:
            fail("SOURCE_MANIFEST_DUPLICATE_INDEX_PATH", path)
        seen.add(path)
        entries.append(IndexEntry(mode=mode, oid=oid, path=path))
    return entries


def read_index_blobs(root: Path, oids: list[str]) -> dict[str, bytes]:
    unique_oids = list(dict.fromkeys(oids))
    if not unique_oids:
        return {}
    command = git_command(root, "cat-file", "--batch")
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload, stderr = process.communicate(
            "".join(f"{oid}\n" for oid in unique_oids).encode("ascii")
        )
    except OSError as exc:
        fail("SOURCE_MANIFEST_GIT_UNAVAILABLE", str(exc))
    if process.returncode != 0:
        detail = stderr.decode("utf-8", "replace").strip()
        fail("SOURCE_MANIFEST_GIT_FAILURE", detail or "git cat-file failed")

    blobs: dict[str, bytes] = {}
    cursor = 0
    for requested_oid in unique_oids:
        newline = payload.find(b"\n", cursor)
        if newline < 0:
            fail("SOURCE_MANIFEST_BLOB_PROTOCOL", requested_oid)
        header = payload[cursor:newline].split()
        cursor = newline + 1
        if len(header) == 2 and header[1] == b"missing":
            fail("SOURCE_MANIFEST_MISSING_BLOB", requested_oid)
        if len(header) != 3:
            fail(
                "SOURCE_MANIFEST_BLOB_PROTOCOL",
                payload[cursor:newline].decode("ascii", "replace"),
            )
        returned_oid, object_type, raw_size = header
        try:
            size = int(raw_size)
        except ValueError:
            fail("SOURCE_MANIFEST_BLOB_PROTOCOL", requested_oid)
        if returned_oid.decode("ascii") != requested_oid or object_type != b"blob":
            fail(
                "SOURCE_MANIFEST_NONBLOB_INDEX_ENTRY",
                f"requested={requested_oid} returned={returned_oid!r} "
                f"type={object_type!r}",
            )
        end = cursor + size
        if end >= len(payload) or payload[end : end + 1] != b"\n":
            fail("SOURCE_MANIFEST_BLOB_PROTOCOL", requested_oid)
        blobs[requested_oid] = payload[cursor:end]
        cursor = end + 1
    if cursor != len(payload):
        fail("SOURCE_MANIFEST_BLOB_PROTOCOL", "unexpected trailing bytes")
    return blobs


def is_source_member(path: str) -> bool:
    return (
        path != MANIFEST_REL
        and not any(part in EXCLUDED_PARTS for part in path.split("/"))
    )


def assert_write_worktree_isolated(root: Path) -> None:
    unstaged = decode_nul_paths(
        run_git(root, "diff", "--name-only", "-z", "--"),
        "SOURCE_MANIFEST_UNSTAGED_PATH",
    )
    untracked = decode_nul_paths(
        run_git(root, "ls-files", "--others", "--exclude-standard", "-z"),
        "SOURCE_MANIFEST_UNTRACKED_PATH",
    )
    disallowed = sorted(
        {
            path
            for path in [*unstaged, *untracked]
            if path != MANIFEST_REL
        }
    )
    if disallowed:
        sample = ", ".join(disallowed[:8])
        suffix = "" if len(disallowed) <= 8 else f" (+{len(disallowed) - 8})"
        fail(
            "SOURCE_MANIFEST_DIRTY_OUTSIDE_MANIFEST",
            f"{sample}{suffix}",
        )


def revision_from_index(
    entries_by_path: dict[str, IndexEntry],
    blobs: dict[str, bytes],
) -> str:
    entry = entries_by_path.get(VERSION_REL)
    if entry is None:
        fail("SOURCE_MANIFEST_VERSION_MISSING", VERSION_REL)
    try:
        version = tomllib.loads(blobs[entry.oid].decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        fail("SOURCE_MANIFEST_VERSION_INVALID", str(exc))
    revision = version.get("spec_revision")
    if not isinstance(revision, str) or not revision:
        fail("SOURCE_MANIFEST_VERSION_INVALID", "spec_revision")
    return revision


def expected_manifest(
    entries: list[IndexEntry],
    blobs: dict[str, bytes],
) -> tuple[dict[str, object], bytes]:
    entries_by_path = {entry.path: entry for entry in entries}
    revision = revision_from_index(entries_by_path, blobs)
    rows: list[dict[str, object]] = []
    for entry in sorted(entries, key=lambda item: item.path):
        if not is_source_member(entry.path):
            continue
        content = blobs[entry.oid]
        rows.append(
            {
                "path": entry.path,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    tree_material = "\n".join(
        f"{row['path']}\0{row['sha256']}" for row in rows
    ).encode("utf-8")
    manifest: dict[str, object] = {
        "schema": SCHEMA,
        "revision": revision,
        "source_baseline": SOURCE_BASELINE,
        "file_count_excluding_manifest": len(rows),
        "total_bytes_excluding_manifest": sum(
            int(row["bytes"]) for row in rows
        ),
        "tree_sha256": hashlib.sha256(tree_material).hexdigest(),
        "self_hash_policy": SELF_HASH_POLICY,
        "files": rows,
    }
    encoded = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    return manifest, encoded


def checked_manifest_path(root: Path) -> Path:
    path = root / MANIFEST_REL
    if path.is_symlink():
        fail("SOURCE_MANIFEST_UNSAFE_OUTPUT", MANIFEST_REL)
    try:
        path.resolve(strict=False).relative_to(root)
    except (OSError, ValueError):
        fail("SOURCE_MANIFEST_UNSAFE_OUTPUT", MANIFEST_REL)
    if not path.parent.is_dir():
        fail("SOURCE_MANIFEST_UNSAFE_OUTPUT", str(path.parent))
    if path.exists() and not path.is_file():
        fail("SOURCE_MANIFEST_UNSAFE_OUTPUT", MANIFEST_REL)
    return path


def emit_receipt(
    *,
    mode: str,
    result: str,
    manifest: dict[str, object] | None = None,
    disposition: str | None = None,
    error_code: str | None = None,
    detail: str | None = None,
) -> None:
    receipt: dict[str, object] = {
        "schema": "deeplus.source-tree-manifest-refresh-receipt/v1",
        "mode": mode,
        "result": result,
        "manifest": MANIFEST_REL,
        "product_execution": "NOT_RUN",
    }
    if manifest is not None:
        receipt.update(
            {
                "revision": manifest["revision"],
                "file_count": manifest["file_count_excluding_manifest"],
                "total_bytes": manifest["total_bytes_excluding_manifest"],
                "tree_sha256": manifest["tree_sha256"],
            }
        )
    if disposition is not None:
        receipt["disposition"] = disposition
    if error_code is not None:
        receipt["error_code"] = error_code
    if detail is not None:
        receipt["detail"] = detail
    print(
        json.dumps(receipt, ensure_ascii=False, separators=(",", ":")),
        file=sys.stderr if result == "FAIL" else sys.stdout,
    )


def execute(mode: str, root: Path) -> int:
    root = root.resolve()
    verify_repository_root(root)
    if mode == "write":
        assert_write_worktree_isolated(root)

    entries = index_entries(root)
    selected_oids = [
        entry.oid
        for entry in entries
        if is_source_member(entry.path) or entry.path == MANIFEST_REL
    ]
    blobs = read_index_blobs(root, selected_oids)
    manifest, expected = expected_manifest(entries, blobs)
    manifest_path = checked_manifest_path(root)

    if mode == "write":
        previous = manifest_path.read_bytes() if manifest_path.exists() else None
        if previous != expected:
            manifest_path.write_bytes(expected)
            if manifest_path.read_bytes() != expected:
                fail("SOURCE_MANIFEST_WRITE_READBACK", MANIFEST_REL)
            disposition = "WRITTEN_STAGE_MANIFEST_BEFORE_CHECK"
        else:
            disposition = "UNCHANGED"
        emit_receipt(
            mode=mode,
            result="PASS",
            manifest=manifest,
            disposition=disposition,
        )
        return 0

    if not manifest_path.is_file():
        fail("SOURCE_MANIFEST_MISSING", MANIFEST_REL)
    worktree_bytes = manifest_path.read_bytes()
    if worktree_bytes != expected:
        fail(
            "SOURCE_MANIFEST_EXPECTED_MISMATCH",
            "worktree manifest differs from the staged source-tree projection",
        )
    index_manifest = next(
        (entry for entry in entries if entry.path == MANIFEST_REL),
        None,
    )
    if index_manifest is None:
        fail("SOURCE_MANIFEST_INDEX_BINDING", "manifest is not staged/tracked")
    if blobs[index_manifest.oid] != worktree_bytes:
        fail(
            "SOURCE_MANIFEST_INDEX_BINDING",
            "stage release/source-tree-manifest.json before --check",
        )
    emit_receipt(
        mode=mode,
        result="PASS",
        manifest=manifest,
        disposition="WORKTREE_AND_INDEX_BOUND",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh or check the source-tree manifest from staged blobs."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    args = parser.parse_args()
    selected_mode = "write" if args.write else "check"
    try:
        return execute(selected_mode, args.root)
    except ManifestError as exc:
        emit_receipt(
            mode=selected_mode,
            result="FAIL",
            error_code=exc.code,
            detail=exc.detail,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
