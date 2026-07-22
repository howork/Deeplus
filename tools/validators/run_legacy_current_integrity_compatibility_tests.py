#!/usr/bin/env python3
"""Run the immutable R2.3 integrity suite against its exact frozen baseline."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
BASELINE_COMMIT = "ffa3bfb7da9e0d19bdd2cc5e4ea713a5e652ee72"
BASELINE_TREE = "5dac7561fa32dd509f2415608cdb0b67c50eef32"
LEGACY_TEST = Path("tools/validators/run_current_integrity_generator_tests.py")


def git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=not binary,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr if not binary else result.stderr.decode("utf-8", "replace")
        raise RuntimeError(f"R2_3_LEGACY_BASELINE_UNAVAILABLE: {detail.strip()}")
    return result.stdout


def extract_regular_tree(archive_bytes: bytes, target: Path) -> int:
    count = 0
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or not relative.parts or ".." in relative.parts:
                raise RuntimeError(f"R2_3_LEGACY_ARCHIVE_ESCAPE: {member.name}")
            destination = target.joinpath(*relative.parts)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise RuntimeError(f"R2_3_LEGACY_UNSAFE_MEMBER: {member.name}")
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"R2_3_LEGACY_UNREADABLE_MEMBER: {member.name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read())
            count += 1
    return count


def run() -> int:
    observed_tree = str(git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}")).strip()
    if observed_tree != BASELINE_TREE:
        raise RuntimeError(
            f"R2_3_LEGACY_BASELINE_TREE_DRIFT: {observed_tree} != {BASELINE_TREE}"
        )
    archive_bytes = git("archive", "--format=tar", BASELINE_COMMIT, binary=True)
    assert isinstance(archive_bytes, bytes)
    with tempfile.TemporaryDirectory(prefix="deeplus-r2-3-legacy-") as temp:
        baseline = Path(temp)
        file_count = extract_regular_tree(archive_bytes, baseline)
        legacy = baseline / LEGACY_TEST
        result = subprocess.run([sys.executable, str(legacy)], cwd=baseline, check=False)
    receipt = {
        "schema": "deeplus.r2-3-legacy-compatibility-receipt/v1",
        "result": "PASS" if result.returncode == 0 else "FAIL",
        "baseline_commit": BASELINE_COMMIT,
        "baseline_tree": BASELINE_TREE,
        "extracted_regular_files": file_count,
        "legacy_test": LEGACY_TEST.as_posix(),
        "legacy_returncode": result.returncode,
        "successor_workspace_mutated": False,
        "product_execution": "NOT_RUN",
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


def main() -> int:
    try:
        return run()
    except (OSError, RuntimeError, tarfile.TarError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
