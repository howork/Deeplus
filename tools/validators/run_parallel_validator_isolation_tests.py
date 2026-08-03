#!/usr/bin/env python3
"""Prove current validator and integrity-generator isolation in parallel."""

from __future__ import annotations

import hashlib
import json
import os
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
EXPECTED_INTEGRITY_SELF_TEST_CASES = {
    "portable-bound-path-order",
    "portable-tutorial-bound-path-order",
    "required-tutorial-bound-root",
    "bound-root-mutation",
    "pointer-nonowned-mutation",
    "authority-nonowned-mutation",
}


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


def run_git_checked(root: Path, *arguments: str) -> bytes:
    process = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={root.as_posix()}",
            "-C",
            str(root),
            *arguments,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(
            "PARALLEL_TEST_GIT_PROVISIONING_FAILED: "
            f"arguments={arguments!r}; detail={detail or 'git command failed'}"
        )
    return process.stdout


def copy_manifest_workspace(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    clone = subprocess.run(
        [
            "git",
            "clone",
            "--no-local",
            "--no-checkout",
            "--quiet",
            str(ROOT),
            str(target),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if clone.returncode != 0:
        detail = clone.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(
            "PARALLEL_TEST_GIT_CLONE_FAILED: "
            f"{detail or 'git clone failed'}"
        )

    source_head = run_git_checked(ROOT, "rev-parse", "HEAD").strip()
    isolated_head = run_git_checked(target, "rev-parse", "HEAD").strip()
    if isolated_head != source_head:
        raise RuntimeError(
            "PARALLEL_TEST_HEAD_MISMATCH: "
            f"source={source_head.decode('ascii', 'replace')} "
            f"isolated={isolated_head.decode('ascii', 'replace')}"
        )
    run_git_checked(target, "remote", "remove", "origin")

    common_dir_text = run_git_checked(
        target, "rev-parse", "--git-common-dir"
    ).decode("utf-8", "strict").strip()
    common_dir = Path(common_dir_text)
    if not common_dir.is_absolute():
        common_dir = target / common_dir
    if not is_inside(common_dir, target):
        raise RuntimeError(
            "PARALLEL_TEST_GIT_COMMON_DIR_OUTSIDE_WORKSPACE: "
            f"{common_dir.resolve().as_posix()}"
        )
    alternates = common_dir / "objects" / "info" / "alternates"
    if alternates.exists():
        raise RuntimeError(
            "PARALLEL_TEST_GIT_ALTERNATES_FORBIDDEN: "
            f"{alternates.resolve().as_posix()}"
        )

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
    run_git_checked(target, "add", "--all")
    run_git_checked(target, "diff", "--quiet", "--")


def external_temp_directory(
    prefix: str,
) -> tempfile.TemporaryDirectory[str]:
    """Allocate held peer state outside the repository and isolated workspace."""
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


def run_parallel(
    workspace: Path,
    peer_roots: tuple[Path, Path],
    *,
    commands_override: list[tuple[str, str, list[str]]] | None = None,
    timeout_seconds: float = 300.0,
) -> list[dict[str, object]]:
    commands = commands_override or [
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
    capture = external_temp_directory("deeplus-parallel-capture-")
    capture_root = Path(capture.name).resolve()
    if is_inside(capture_root, workspace):
        capture.cleanup()
        raise RuntimeError(
            f"PARALLEL_TEST_TEMP_INSIDE_WORKSPACE: {capture_root.as_posix()}"
        )
    child_environment = os.environ.copy()
    child_environment["PYTHONIOENCODING"] = "utf-8"
    processes: list[tuple[str, str, subprocess.Popen[bytes]]] = []
    captures: dict[str, tuple[Path, Path]] = {}
    try:
        for index, (name, kind, command) in enumerate(commands):
            stdout_path = capture_root / f"{index:02d}-{name}.stdout"
            stderr_path = capture_root / f"{index:02d}-{name}.stderr"
            with stdout_path.open("wb") as stdout_handle, stderr_path.open(
                "wb"
            ) as stderr_handle:
                process = subprocess.Popen(
                    command,
                    cwd=workspace,
                    stdout=stdout_handle,
                    stderr=stderr_handle,
                    env=child_environment,
                )
            processes.append((name, kind, process))
            captures[name] = (stdout_path, stderr_path)

        observed_residue: set[str] = set()
        deadline = time.monotonic() + timeout_seconds
        while any(process.poll() is None for _, _, process in processes):
            observed_residue.update(
                f"root/{name}" for name in local_residue(ROOT)
            )
            observed_residue.update(
                f"workspace/{name}" for name in local_residue(workspace)
            )
            if time.monotonic() >= deadline:
                running = [
                    name
                    for name, _, process in processes
                    if process.poll() is None
                ]
                for _, _, process in processes:
                    if process.poll() is None:
                        process.kill()
                unreaped: list[str] = []
                for name, _, process in processes:
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        unreaped.append(name)
                returncodes = {
                    name: process.returncode
                    for name, _, process in processes
                }
                stderr_tails = {
                    name: captures[name][1]
                    .read_bytes()
                    .decode("utf-8", "replace")[-500:]
                    for name, _, _ in processes
                }
                raise RuntimeError(
                    "PARALLEL_TEST_TIMEOUT: "
                    f"running={running!r}; unreaped={unreaped!r}; "
                    f"returncodes={returncodes!r}; "
                    f"stderr_tails={stderr_tails!r}"
                )
            time.sleep(0.02)

        peer_spellings = {
            spelling
            for peer in peer_roots
            for spelling in (
                str(peer.resolve()),
                peer.resolve().as_posix(),
                peer.name,
            )
        }
        results: list[dict[str, object]] = []
        for name, kind, process in processes:
            stdout_bytes = captures[name][0].read_bytes()
            stderr_bytes = captures[name][1].read_bytes()
            stdout = stdout_bytes.decode("utf-8", "strict")
            stderr = stderr_bytes.decode("utf-8", "replace")
            try:
                receipt = parse_receipt(stdout)
            except RuntimeError as exc:
                detail = stderr.strip() or "<empty stderr>"
                raise RuntimeError(
                    f"{exc}; process={name}; returncode={process.returncode}; "
                    f"stderr={detail}"
                ) from exc
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
            elif kind == "synthetic_pass":
                passed = (
                    process.returncode == 0
                    and receipt.get("result") == "PASS"
                    and peer_absent
                )
            else:
                self_test_cases = receipt.get("cases", [])
                observed_case_ids = {
                    row.get("case")
                    for row in self_test_cases
                    if isinstance(row, dict)
                    and isinstance(row.get("case"), str)
                }
                passed = (
                    process.returncode == 0
                    and receipt.get("result") == "PASS"
                    and receipt.get("tests")
                    == len(EXPECTED_INTEGRITY_SELF_TEST_CASES)
                    and receipt.get("passed")
                    == len(EXPECTED_INTEGRITY_SELF_TEST_CASES)
                    and observed_case_ids
                    == EXPECTED_INTEGRITY_SELF_TEST_CASES
                    and all(
                        isinstance(row, dict) and row.get("pass") is True
                        for row in self_test_cases
                    )
                    and receipt.get("product_execution") == "NOT_RUN"
                    and peer_absent
                )
            results.append(
                {
                    "test": name,
                    "pass": passed,
                    "returncode": process.returncode,
                    "receipt_result": receipt.get("result"),
                    "tests": receipt.get("tests"),
                    "passed": receipt.get("passed"),
                    "errors": receipt.get("errors"),
                    "peer_paths_absent": peer_absent,
                    "stdout_bytes": len(stdout_bytes),
                    "stderr_bytes": len(stderr_bytes),
                    "stderr_tail": stderr[-500:],
                }
            )
        results.append(
            {
                "test": "no_repository_local_harness_residue",
                "pass": (
                    not observed_residue
                    and not local_residue(ROOT)
                    and not local_residue(workspace)
                ),
                "observed": sorted(observed_residue),
                "root_final": local_residue(ROOT),
                "workspace_final": local_residue(workspace),
            }
        )
        return results
    finally:
        for _, _, process in processes:
            if process.poll() is None:
                process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        capture.cleanup()


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
