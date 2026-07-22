#!/usr/bin/env python3
"""Compare two v2 source-archive receipts without overclaiming portability."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BUILD_SCHEMA = "deeplus.source-archive-build-receipt/v2"
COMPARISON_SCHEMA = "deeplus.source-archive-repeat-comparison-receipt/v1"


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


def read_receipt(path: Path, label: str, errors: list[str]) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}_RECEIPT_READ: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}_RECEIPT_OBJECT: expected object")
        return {}
    return value


def validate_build_receipt(
    receipt: dict[str, object],
    archive_path: Path,
    label: str,
    errors: list[str],
) -> dict[str, object]:
    if receipt.get("schema") != BUILD_SCHEMA:
        errors.append(f"{label}_SCHEMA: expected {BUILD_SCHEMA}")
    if receipt.get("result") != "PASS_ENVIRONMENT_SCOPED":
        errors.append(f"{label}_RESULT: expected PASS_ENVIRONMENT_SCOPED")
    claim = receipt.get("claim_boundary")
    if not isinstance(claim, dict):
        errors.append(f"{label}_CLAIM_BOUNDARY: expected object")
        claim = {}
    if claim.get("archive_byte_identity") != "ENVIRONMENT_SCOPED":
        errors.append(f"{label}_ARCHIVE_SCOPE: expected ENVIRONMENT_SCOPED")
    if claim.get("cross_environment_byte_identity") != "NOT_ESTABLISHED":
        errors.append(f"{label}_CROSS_ENVIRONMENT: expected NOT_ESTABLISHED")
    if claim.get("product_execution") != "NOT_RUN":
        errors.append(f"{label}_PRODUCT_EXECUTION: expected NOT_RUN")

    environment = receipt.get("environment")
    environment_sha = receipt.get("environment_fingerprint_sha256")
    if not isinstance(environment, dict) or canonical_sha(environment) != environment_sha:
        errors.append(f"{label}_ENVIRONMENT_FINGERPRINT: binding mismatch")
    source = receipt.get("source")
    builder = receipt.get("builder")
    archive_policy = receipt.get("archive_policy")
    context_material = {
        "source": source,
        "builder": builder,
        "archive_policy": archive_policy,
        "environment_fingerprint_sha256": environment_sha,
    }
    if canonical_sha(context_material) != receipt.get("build_context_sha256"):
        errors.append(f"{label}_BUILD_CONTEXT: binding mismatch")

    if not archive_path.is_file():
        errors.append(f"{label}_ARCHIVE_READ: missing {archive_path}")
        return {"sha256": None, "bytes": None}
    observed_sha = sha(archive_path)
    observed_bytes = archive_path.stat().st_size
    archive = receipt.get("archive")
    scoped = receipt.get("environment_scoped_archive_digest")
    if not isinstance(archive, dict):
        errors.append(f"{label}_ARCHIVE_RECEIPT: expected object")
        archive = {}
    if not isinstance(scoped, dict):
        errors.append(f"{label}_SCOPED_DIGEST: expected object")
        scoped = {}
    if archive.get("output") != archive_path.name:
        errors.append(f"{label}_ARCHIVE_OUTPUT: receipt/path filename mismatch")
    if archive.get("sha256") != observed_sha or archive.get("bytes") != observed_bytes:
        errors.append(f"{label}_ARCHIVE_BINDING: observed bytes/digest mismatch")
    if (
        scoped.get("algorithm") != "SHA-256"
        or scoped.get("value") != observed_sha
        or scoped.get("scope_environment_fingerprint_sha256") != environment_sha
    ):
        errors.append(f"{label}_SCOPED_DIGEST: environment binding mismatch")
    return {"sha256": observed_sha, "bytes": observed_bytes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-a", type=Path, required=True)
    parser.add_argument("--archive-a", type=Path, required=True)
    parser.add_argument("--receipt-b", type=Path, required=True)
    parser.add_argument("--archive-b", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    receipt_a = read_receipt(args.receipt_a, "A", errors)
    receipt_b = read_receipt(args.receipt_b, "B", errors)
    archive_a = validate_build_receipt(receipt_a, args.archive_a, "A", errors)
    archive_b = validate_build_receipt(receipt_b, args.archive_b, "B", errors)

    comparisons = {
        "receipt_paths_distinct": args.receipt_a.resolve() != args.receipt_b.resolve(),
        "archive_paths_distinct": args.archive_a.resolve() != args.archive_b.resolve(),
        "environment_fingerprint_equal": (
            receipt_a.get("environment_fingerprint_sha256")
            == receipt_b.get("environment_fingerprint_sha256")
        ),
        "build_context_equal": (
            receipt_a.get("build_context_sha256") == receipt_b.get("build_context_sha256")
        ),
        "source_content_tree_equal": (
            isinstance(receipt_a.get("source"), dict)
            and isinstance(receipt_b.get("source"), dict)
            and receipt_a["source"].get("content_tree_sha256")
            == receipt_b["source"].get("content_tree_sha256")
        ),
        "builder_equal": receipt_a.get("builder") == receipt_b.get("builder"),
        "archive_policy_equal": (
            receipt_a.get("archive_policy") == receipt_b.get("archive_policy")
        ),
        "archive_digest_equal": archive_a.get("sha256") == archive_b.get("sha256"),
        "archive_size_equal": archive_a.get("bytes") == archive_b.get("bytes"),
        "archive_bytes_equal": (
            args.archive_a.is_file()
            and args.archive_b.is_file()
            and args.archive_a.read_bytes() == args.archive_b.read_bytes()
        ),
    }
    for name, passed in comparisons.items():
        if not passed:
            errors.append(f"COMPARISON_{name.upper()}: mismatch")

    passed = not errors
    receipt = {
        "schema": COMPARISON_SCHEMA,
        "result": "PASS_SAME_ENVIRONMENT_REPEAT" if passed else "FAIL",
        "claim_boundary": {
            "same_environment_repeat": "PASS" if passed else "FAIL",
            "cross_environment_byte_identity": "NOT_ESTABLISHED",
            "product_execution": "NOT_RUN",
        },
        "environment_fingerprint_sha256": (
            receipt_a.get("environment_fingerprint_sha256") if passed else None
        ),
        "build_context_sha256": receipt_a.get("build_context_sha256") if passed else None,
        "source_content_tree_sha256": (
            receipt_a["source"].get("content_tree_sha256")
            if passed and isinstance(receipt_a.get("source"), dict)
            else None
        ),
        "archive_sha256": archive_a.get("sha256") if passed else None,
        "archive_bytes": archive_a.get("bytes") if passed else None,
        "comparisons": comparisons,
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
