#!/usr/bin/env python3
"""Prove current validator and integrity-generator isolation in parallel."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "release/source-tree-manifest.json"
VALIDATOR_REL = Path("tools/validators/validate_workspace.py")
INTEGRITY_GENERATOR_REL = Path(
    "tools/generators/generate_language_coherence_current_integrity.py"
)
REPOSITORY_TEMP_PREFIXES = (
    ".post-pr16-integrity-test-",
    "deeplus-post-pr16-integrity-test-",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_inside(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    repository = root.resolve()
    return resolved == repository or repository in resolved.parents


def tracked_snapshot() -> dict[str, str] | None:
    if not (ROOT / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "--cached"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", "replace"))
    snapshot: dict[str, str] = {}
    for name in result.stdout.decode("utf-8").split("\0"):
        if not name:
            continue
        path = ROOT / name
        snapshot[name] = sha(path) if path.is_file() else "MISSING"
    return snapshot


def copy_manifest_workspace(target: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    relatives = [Path("release/source-tree-manifest.json")]
    relatives.extend(Path(row["path"]) for row in manifest["files"])
    for relative in relatives:
        if relative.is_absolute() or not relative.parts or ".." in relative.parts:
            raise RuntimeError(f"PARALLEL_TEST_UNSAFE_MEMBER: {relative.as_posix()}")
        source = ROOT / relative
        if source.is_symlink() or not source.is_file():
            raise RuntimeError(f"PARALLEL_TEST_UNSAFE_MEMBER: {relative.as_posix()}")
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def external_temp_directory(
    prefix: str,
) -> tempfile.TemporaryDirectory[str]:
    """Allocate held peer state outside both the repository and clean export."""
    temporary = tempfile.TemporaryDirectory(prefix=prefix)
    temporary_path = Path(temporary.name).resolve()
    if is_inside(temporary_path, ROOT):
        temporary.cleanup()
        raise RuntimeError(
            f"PARALLEL_TEST_TEMP_INSIDE_REPOSITORY: {temporary_path.as_posix()}"
        )
    return temporary


def poison(root: Path) -> None:
    (root / "invalid-peer-state.json").write_text("{not-json", encoding="utf-8")
    (root / "nested-peer-archive.zip").write_bytes(b"not-a-zip-but-still-an-archive-path")


def local_residue(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    return sorted(
        path.name
        for path in root.iterdir()
        if any(path.name.startswith(prefix) for prefix in REPOSITORY_TEMP_PREFIXES)
    )


def parse_receipt(output: str) -> dict[str, object]:
    try:
        value = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"PARALLEL_TEST_NONJSON_RECEIPT: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("PARALLEL_TEST_NONOBJECT_RECEIPT")
    return value


def run_parallel(workspace: Path, peer_roots: tuple[Path, Path]) -> list[dict[str, object]]:
    commands = [
        (
            "validator_a",
            "validator",
            [
                sys.executable,
                str(workspace / VALIDATOR_REL),
                "--root",
                str(workspace),
                "--no-receipt",
            ],
        ),
        (
            "validator_b",
            "validator",
            [
                sys.executable,
                str(workspace / VALIDATOR_REL),
                "--root",
                str(workspace),
                "--no-receipt",
            ],
        ),
        (
            "integrity_check",
            "integrity_check",
            [
                sys.executable,
                str(workspace / INTEGRITY_GENERATOR_REL),
                "--root",
                str(workspace),
                "--check",
            ],
        ),
        (
            "integrity_self_test",
            "integrity_self_test",
            [
                sys.executable,
                str(workspace / INTEGRITY_GENERATOR_REL),
                "--root",
                str(workspace),
                "--self-test",
            ],
        ),
    ]
    processes = [
        (
            name,
            kind,
            subprocess.Popen(
                command,
                cwd=workspace,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ),
        )
        for name, kind, command in commands
    ]
    observed_residue: set[str] = set()
    deadline = time.monotonic() + 300
    while any(process.poll() is None for _, _, process in processes):
        observed_residue.update(f"root/{name}" for name in local_residue(ROOT))
        observed_residue.update(f"workspace/{name}" for name in local_residue(workspace))
        if time.monotonic() >= deadline:
            for _, _, process in processes:
                process.kill()
            raise RuntimeError("PARALLEL_TEST_TIMEOUT")
        time.sleep(0.02)

    peer_spellings = {
        spelling
        for peer in peer_roots
        for spelling in (str(peer.resolve()), peer.resolve().as_posix(), peer.name)
    }
    results: list[dict[str, object]] = []
    for name, kind, process in processes:
        stdout, stderr = process.communicate()
        receipt = parse_receipt(stdout)
        peer_absent = all(
            spelling not in stdout and spelling not in stderr
            for spelling in peer_spellings
        )
        if kind == "validator":
            passed = (
                process.returncode == 0
                and receipt.get("result") == "PASS"
                and receipt.get("errors") == []
                and peer_absent
            )
        elif kind == "integrity_check":
            passed = (
                process.returncode == 0
                and receipt.get("result") == "PASS"
                and receipt.get("mode") == "CHECK"
                and receipt.get("product_execution") == "NOT_RUN"
                and peer_absent
            )
        else:
            passed = (
                process.returncode == 0
                and receipt.get("result") == "PASS"
                and receipt.get("tests") == 3
                and receipt.get("passed") == 3
                and receipt.get("product_execution") == "NOT_RUN"
                and peer_absent
            )
        results.append({
            "test": name,
            "pass": passed,
            "returncode": process.returncode,
            "receipt_result": receipt.get("result"),
            "tests": receipt.get("tests"),
            "passed": receipt.get("passed"),
            "errors": receipt.get("errors"),
            "peer_paths_absent": peer_absent,
            "stderr_tail": stderr[-500:],
        })
    results.append({
        "test": "no_repository_local_harness_residue",
        "pass": not observed_residue and not local_residue(ROOT) and not local_residue(workspace),
        "observed": sorted(observed_residue),
        "root_final": local_residue(ROOT),
        "workspace_final": local_residue(workspace),
    })
    return results


def main() -> int:
    before = tracked_snapshot()
    results: list[dict[str, object]] = []
    try:
        with tempfile.TemporaryDirectory(prefix="deeplus-parallel-isolation-") as outer_name:
            outer = Path(outer_name).resolve()
            if is_inside(outer, ROOT):
                raise RuntimeError(f"PARALLEL_TEST_TEMP_INSIDE_REPOSITORY: {outer.as_posix()}")
            workspace = outer / "workspace"
            copy_manifest_workspace(workspace)
            with ExitStack() as stack:
                peer_a = Path(stack.enter_context(
                    external_temp_directory("deeplus-parallel-peer-a-")
                )).resolve()
                peer_b = Path(stack.enter_context(
                    external_temp_directory("deeplus-parallel-peer-b-")
                )).resolve()
                poison(peer_a)
                poison(peer_b)
                roots_valid = (
                    peer_a != peer_b
                    and not is_inside(peer_a, workspace)
                    and not is_inside(peer_b, workspace)
                    and not is_inside(peer_a, ROOT)
                    and not is_inside(peer_b, ROOT)
                )
                results.append({
                    "test": "external_peer_roots_distinct_and_held",
                    "pass": roots_valid,
                    "peer_a": peer_a.as_posix(),
                    "peer_b": peer_b.as_posix(),
                    "poison_files_per_root": 2,
                })
                results.extend(run_parallel(workspace, (peer_a, peer_b)))
    except Exception as exc:  # Emit one machine-readable failure receipt.
        results.append({
            "test": "harness_execution",
            "pass": False,
            "detail": f"{type(exc).__name__}: {exc}",
        })

    after = tracked_snapshot()
    results.append({
        "test": "repository_tracked_files_unchanged",
        "pass": before == after,
        "git_snapshot_available": before is not None,
    })
    passed = sum(bool(row.get("pass")) for row in results)
    receipt = {
        "schema": "deeplus.parallel-validator-isolation-test-receipt/v1",
        "result": "PASS" if passed == len(results) else "FAIL",
        "tests": len(results),
        "passed": passed,
        "parallel_processes": 4,
        "product_execution": "NOT_RUN",
        "claim_boundary": "TOOLING_VALIDATION_ONLY_NO_PRODUCT_EXECUTION",
        "cases": results,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
