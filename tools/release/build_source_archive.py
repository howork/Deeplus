#!/usr/bin/env python3
"""Build a deterministic Deeplus source snapshot and non-self-referential tree manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import stat
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
import zipfile
import zlib
from pathlib import Path


EXCLUDED_PARTS = {
    ".git",
    "target",
    "dist",
    "candidate",
    "__pycache__",
}
MANIFEST = "release/source-tree-manifest.json"
ARCHIVE_ROOT = "Deeplus_Canonical_Workspace/"
ARCHIVE_COMPRESSION = zipfile.ZIP_DEFLATED
ARCHIVE_COMPRESSION_NAME = "ZIP_DEFLATED"
ARCHIVE_COMPRESSLEVEL = 9
ARCHIVE_ENTRY_TIMESTAMP = (2026, 7, 15, 0, 0, 0)
ARCHIVE_ENTRY_MODE = 0o644


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fail(code: str, detail: str) -> None:
    raise SystemExit(f"{code}: {detail}")


def checked_member(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        fail("SOURCE_ARCHIVE_UNSAFE_MEMBER", relative.as_posix())
    path = root / relative
    if path.is_symlink() or not path.is_file():
        fail("SOURCE_ARCHIVE_UNSAFE_MEMBER", relative.as_posix())
    try:
        path.resolve(strict=True).relative_to(root)
    except (OSError, ValueError):
        fail("SOURCE_ARCHIVE_UNSAFE_MEMBER", relative.as_posix())
    return path


def repository_output(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        fail("SOURCE_ARCHIVE_OUTPUT_COLLISION", relative.as_posix())
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            fail("SOURCE_ARCHIVE_OUTPUT_COLLISION", relative.as_posix())
    try:
        current.resolve(strict=False).relative_to(root)
    except (OSError, ValueError):
        fail("SOURCE_ARCHIVE_OUTPUT_COLLISION", relative.as_posix())
    if current.exists() and not current.is_file():
        fail("SOURCE_ARCHIVE_OUTPUT_COLLISION", relative.as_posix())
    return current


def git_source_files(root: Path, *, allow_dirty: bool) -> list[Path] | None:
    if not (root / ".git").exists():
        return None
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        fail("SOURCE_ARCHIVE_GIT_STATE", status.stderr.decode("utf-8", "replace"))
    if status.stdout and not allow_dirty:
        fail("SOURCE_ARCHIVE_DIRTY_SOURCE_SET", "tracked or untracked workspace changes")
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached"],
        capture_output=True,
        check=False,
    )
    if listed.returncode != 0:
        fail("SOURCE_ARCHIVE_GIT_STATE", listed.stderr.decode("utf-8", "replace"))
    try:
        names = listed.stdout.decode("utf-8").split("\0")
    except UnicodeDecodeError as exc:
        fail("SOURCE_ARCHIVE_UNSAFE_MEMBER", str(exc))
    if allow_dirty:
        untracked = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "-z",
                "--others",
                "--exclude-standard",
            ],
            capture_output=True,
            check=False,
        )
        if untracked.returncode != 0:
            fail(
                "SOURCE_ARCHIVE_GIT_STATE",
                untracked.stderr.decode("utf-8", "replace"),
            )
        try:
            names.extend(untracked.stdout.decode("utf-8").split("\0"))
        except UnicodeDecodeError as exc:
            fail("SOURCE_ARCHIVE_UNSAFE_MEMBER", str(exc))
    files = []
    seen: set[str] = set()
    for name in names:
        if not name or name == MANIFEST or name in seen:
            continue
        seen.add(name)
        relative = Path(name)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if allow_dirty and not (root / relative).exists():
            # Explicit dirty-mode callers may be validating an intentional
            # tracked deletion.  The deleted path is absent from that snapshot.
            continue
        files.append(checked_member(root, relative))
    return files


def exported_source_files(root: Path) -> list[Path]:
    files = []
    for current, directories, names in os.walk(root, topdown=True, followlinks=False):
        base = Path(current)
        retained = []
        for name in directories:
            path = base / name
            if name in EXCLUDED_PARTS:
                continue
            if path.is_symlink():
                fail("SOURCE_ARCHIVE_UNSAFE_MEMBER", path.relative_to(root).as_posix())
            retained.append(name)
        directories[:] = retained
        for name in names:
            relative = (base / name).relative_to(root)
            if (
                any(part in EXCLUDED_PARTS for part in relative.parts)
                or relative.as_posix() == MANIFEST
            ):
                continue
            files.append(checked_member(root, relative))
    return files


def source_files(root: Path, *, allow_dirty: bool) -> list[Path]:
    files = git_source_files(root, allow_dirty=allow_dirty)
    if files is None:
        files = exported_source_files(root)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def lexical_output_path(value: Path) -> Path:
    path = Path(os.path.abspath(value))
    current = Path(path.parts[0])
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            fail("SOURCE_ARCHIVE_OUTPUT_COLLISION", str(current))
    return path


def git_text(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail("SOURCE_ARCHIVE_GIT_STATE", result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def git_binding(root: Path, *, allow_dirty: bool) -> dict[str, object]:
    if not (root / ".git").exists():
        return {
            "repository_state": "EXPORTED_TREE_NO_GIT_METADATA",
            "object_format": None,
            "commit_oid": None,
            "tree_oid": None,
            "worktree_state": "NOT_AUDITABLE_NO_GIT_METADATA",
            "status_porcelain_sha256": None,
            "status_entry_count": None,
            "allow_dirty_source_requested": allow_dirty,
            "archive_to_git_binding": "UNBOUND_EXPORTED_SOURCE_TREE",
        }
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        fail("SOURCE_ARCHIVE_GIT_STATE", status.stderr.decode("utf-8", "replace"))
    dirty = bool(status.stdout)
    return {
        "repository_state": "GIT_WORKTREE",
        "object_format": git_text(root, "rev-parse", "--show-object-format"),
        "commit_oid": git_text(root, "rev-parse", "HEAD"),
        "tree_oid": git_text(root, "rev-parse", "HEAD^{tree}"),
        "worktree_state": "DIRTY_ALLOWED_NONRELEASE" if dirty else "CLEAN",
        "status_porcelain_sha256": hashlib.sha256(status.stdout).hexdigest(),
        "status_entry_count": status.stdout.count(b"\0"),
        "allow_dirty_source_requested": allow_dirty,
        "archive_to_git_binding": (
            "NOT_EXACT_DIRTY_SOURCE_TREE" if dirty else "EXACT_CLEAN_WORKTREE_HEAD"
        ),
    }


def environment_fingerprint() -> dict[str, object]:
    zipfile_path = Path(zipfile.__file__).resolve()
    if not zipfile_path.is_file():
        fail("SOURCE_ARCHIVE_ENVIRONMENT_FINGERPRINT", str(zipfile_path))
    return {
        "os": {
            "name": os.name,
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "cache_tag": sys.implementation.cache_tag,
        },
        "zlib": {
            "compile_version": zlib.ZLIB_VERSION,
            "runtime_version": zlib.ZLIB_RUNTIME_VERSION,
        },
        "zipfile": {
            "module_sha256": sha(zipfile_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-dirty-source", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = lexical_output_path(args.output).resolve()
    try:
        output_relative = output.relative_to(root)
    except ValueError:
        output_relative = None
    if output_relative is not None and not any(
        part in EXCLUDED_PARTS for part in output_relative.parts
    ):
        fail("SOURCE_ARCHIVE_OUTPUT_COLLISION", output_relative.as_posix())
    version = tomllib.loads((root / "current/language-version.toml").read_text(encoding="utf-8"))
    revision = version["spec_revision"]
    rows = []
    for path in source_files(root, allow_dirty=args.allow_dirty_source):
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
    manifest_path = repository_output(root, Path(MANIFEST))
    manifest_path.write_bytes(
        (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    all_files = source_files(root, allow_dirty=True) + [manifest_path]
    all_files.sort(key=lambda path: path.relative_to(root).as_posix())
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output,
        "w",
        compression=ARCHIVE_COMPRESSION,
        compresslevel=ARCHIVE_COMPRESSLEVEL,
    ) as archive:
        for path in all_files:
            rel = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}{rel}", ARCHIVE_ENTRY_TIMESTAMP)
            info.compress_type = ARCHIVE_COMPRESSION
            info.external_attr = (stat.S_IFREG | ARCHIVE_ENTRY_MODE) << 16
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=ARCHIVE_COMPRESSION,
                compresslevel=ARCHIVE_COMPRESSLEVEL,
            )
    archive_sha = sha(output)
    environment = environment_fingerprint()
    environment_sha = canonical_sha(environment)
    source = {
        "git": git_binding(root, allow_dirty=args.allow_dirty_source),
        "manifest_path": MANIFEST,
        "manifest_revision": revision,
        "manifest_sha256": sha(manifest_path),
        "content_tree_sha256": manifest["tree_sha256"],
    }
    builder = {
        "path": "tools/release/build_source_archive.py",
        "sha256": sha(Path(__file__).resolve()),
    }
    archive_policy = {
        "format": "ZIP",
        "archive_root": ARCHIVE_ROOT,
        "compression_method": ARCHIVE_COMPRESSION_NAME,
        "compression_level": ARCHIVE_COMPRESSLEVEL,
        "entry_timestamp": list(ARCHIVE_ENTRY_TIMESTAMP),
        "entry_mode": format(stat.S_IFREG | ARCHIVE_ENTRY_MODE, "07o"),
    }
    build_context_sha = canonical_sha({
        "source": source,
        "builder": builder,
        "archive_policy": archive_policy,
        "environment_fingerprint_sha256": environment_sha,
    })
    receipt = {
        "schema": "deeplus.source-archive-build-receipt/v2",
        "result": "PASS_ENVIRONMENT_SCOPED",
        "claim_boundary": {
            "source_content_tree_identity": "PORTABLE_SHA256",
            "archive_byte_identity": "ENVIRONMENT_SCOPED",
            "same_environment_repeat": "NOT_EVALUATED_BY_SINGLE_BUILD",
            "cross_environment_byte_identity": "NOT_ESTABLISHED",
            "product_execution": "NOT_RUN",
        },
        "source": source,
        "builder": builder,
        "archive_policy": archive_policy,
        "environment": environment,
        "environment_fingerprint_sha256": environment_sha,
        "build_context_sha256": build_context_sha,
        "environment_scoped_archive_digest": {
            "algorithm": "SHA-256",
            "value": archive_sha,
            "scope_environment_fingerprint_sha256": environment_sha,
        },
        "archive": {
            "output": output.name,
            "sha256": archive_sha,
            "bytes": output.stat().st_size,
            "file_count": len(all_files),
        },
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
