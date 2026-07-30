#!/usr/bin/env python3
"""Exercise the parallel isolation harness's stream and failure boundaries."""

from __future__ import annotations

import json
import sys
import tempfile
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Callable


sys.dont_write_bytecode = True
import run_parallel_validator_isolation_tests as harness  # noqa: E402


LARGE_STREAM_BYTES = 1024 * 1024


def synthetic_command(source: str) -> list[str]:
    return [sys.executable, "-c", source]


def run_one(
    name: str,
    source: str,
    *,
    timeout_seconds: float = 10.0,
) -> list[dict[str, object]]:
    with tempfile.TemporaryDirectory(
        prefix="deeplus-parallel-mutation-workspace-"
    ) as workspace_name:
        workspace = Path(workspace_name).resolve()
        with ExitStack() as stack:
            peer_a = Path(
                stack.enter_context(
                    harness.external_temp_directory(
                        "deeplus-parallel-mutation-peer-a-"
                    )
                )
            ).resolve()
            peer_b = Path(
                stack.enter_context(
                    harness.external_temp_directory(
                        "deeplus-parallel-mutation-peer-b-"
                    )
                )
            ).resolve()
            return harness.run_parallel(
                workspace,
                (peer_a, peer_b),
                commands_override=[
                    (
                        name,
                        "synthetic_pass",
                        synthetic_command(source),
                    )
                ],
                timeout_seconds=timeout_seconds,
            )


def capture_over_pipe_capacity_completes() -> dict[str, object]:
    source = (
        "import json; "
        "print(json.dumps({'result':'PASS','padding':'x'*"
        f"{LARGE_STREAM_BYTES + 4096}"
        "}))"
    )
    started = time.monotonic()
    rows = run_one("large_stream", source)
    elapsed_ms = round((time.monotonic() - started) * 1000)
    row = rows[0]
    passed = (
        row.get("test") == "large_stream"
        and row.get("pass") is True
        and row.get("returncode") == 0
        and isinstance(row.get("stdout_bytes"), int)
        and row["stdout_bytes"] > LARGE_STREAM_BYTES
        and elapsed_ms < 10_000
        and rows[-1].get("test") == "no_repository_local_harness_residue"
        and rows[-1].get("pass") is True
    )
    return {
        "test": "capture_over_pipe_capacity_completes",
        "pass": passed,
        "elapsed_ms": elapsed_ms,
        "stdout_bytes": row.get("stdout_bytes"),
    }


def nonzero_valid_receipt_fails_closed() -> dict[str, object]:
    source = (
        "import json,sys; "
        "print(json.dumps({'result':'PASS'})); "
        "sys.stderr.write('NONZERO_MARKER\\n'); "
        "raise SystemExit(23)"
    )
    rows = run_one("nonzero_receipt", source)
    row = rows[0]
    return {
        "test": "nonzero_valid_receipt_fails_closed",
        "pass": (
            row.get("test") == "nonzero_receipt"
            and row.get("pass") is False
            and row.get("returncode") == 23
            and "NONZERO_MARKER" in str(row.get("stderr_tail"))
        ),
        "returncode": row.get("returncode"),
        "stderr_tail": row.get("stderr_tail"),
    }


def invalid_receipt_preserves_diagnostic() -> dict[str, object]:
    source = (
        "import sys; "
        "sys.stdout.write('not-json'); "
        "sys.stderr.write('INVALID_JSON_MARKER\\n')"
    )
    observed = ""
    try:
        run_one("invalid_receipt", source)
    except RuntimeError as exc:
        observed = str(exc)
    return {
        "test": "invalid_receipt_preserves_diagnostic",
        "pass": (
            "PARALLEL_TEST_NONJSON_RECEIPT" in observed
            and "process=invalid_receipt" in observed
            and "returncode=0" in observed
            and "INVALID_JSON_MARKER" in observed
        ),
        "observed": observed,
    }


def timeout_kills_reaps_and_fails_closed() -> dict[str, object]:
    source = (
        "import sys,time; "
        "sys.stderr.write('TIMEOUT_MARKER\\n'); "
        "sys.stderr.flush(); "
        "time.sleep(30)"
    )
    observed = ""
    try:
        run_one("timeout_probe", source, timeout_seconds=1.0)
    except RuntimeError as exc:
        observed = str(exc)
    return {
        "test": "timeout_kills_reaps_and_fails_closed",
        "pass": (
            "PARALLEL_TEST_TIMEOUT" in observed
            and "timeout_probe" in observed
            and "unreaped=[]" in observed
            and "TIMEOUT_MARKER" in observed
        ),
        "observed": observed,
    }


def main() -> int:
    before = harness.tracked_snapshot()
    case_functions: tuple[Callable[[], dict[str, object]], ...] = (
        capture_over_pipe_capacity_completes,
        nonzero_valid_receipt_fails_closed,
        invalid_receipt_preserves_diagnostic,
        timeout_kills_reaps_and_fails_closed,
    )
    cases: list[dict[str, object]] = []
    for case_function in case_functions:
        try:
            cases.append(case_function())
        except Exception as exc:
            cases.append(
                {
                    "test": case_function.__name__,
                    "pass": False,
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            )
    after = harness.tracked_snapshot()
    cases.append(
        {
            "test": "repository_tracked_files_unchanged",
            "pass": before == after,
            "git_snapshot_available": before is not None,
        }
    )
    passed = sum(row.get("pass") is True for row in cases)
    receipt = {
        "schema": (
            "deeplus.parallel-validator-isolation-mutation-test-receipt/v1"
        ),
        "result": "PASS" if passed == len(cases) else "FAIL",
        "tests": len(cases),
        "passed": passed,
        "large_stream_threshold_bytes": LARGE_STREAM_BYTES,
        "product_execution": "NOT_RUN",
        "claim_boundary": "TOOLING_VALIDATION_ONLY_NO_PRODUCT_EXECUTION",
        "cases": cases,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
