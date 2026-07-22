#!/usr/bin/env python3
"""Bind the explicit cancellation axis into every canonical RCTS-V5 projection.

Existing generated fixtures predate the required axis.  The default is
``forbidden`` as a structurally closed migration projection; predicates that
exercise cancellation must override it in their own discriminating fixture.
The default does not override predicate-specific semantic fixture authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TARGETS = [
    *sorted((ROOT / "tests/conformance/checker-predicates/chunks").glob("part-*.json")),
    ROOT / "tests/fixtures/imported/rcts-v5-fixtures.json",
    ROOT / "tests/fixtures/imported/rcts-v5-adversarial-fixtures.json",
]


def bind(node: Any, preserve_missing_cancellation: bool = False) -> tuple[Any, int]:
    changed = 0
    if isinstance(node, list):
        output = []
        for item in node:
            bound, count = bind(item, preserve_missing_cancellation)
            output.append(bound)
            changed += count
        return output, changed
    if not isinstance(node, dict):
        return node, 0

    output: dict[str, Any] = {}
    is_descriptor = node.get("schema") == "deeplus.rcts-v5/descriptor"
    child_preserves_missing = preserve_missing_cancellation or (
        node.get("fixture_id") == "RCTS5-NEG-CANCELLATION-MISSING"
    )
    for key, value in node.items():
        bound, count = bind(value, child_preserves_missing)
        output[key] = bound
        changed += count
        if key == "responsibility" and is_descriptor and isinstance(bound, dict):
            if "cancellation" not in bound and not child_preserves_missing:
                responsibility: dict[str, Any] = {}
                for responsibility_key, responsibility_value in bound.items():
                    responsibility[responsibility_key] = responsibility_value
                    if responsibility_key == "errors":
                        responsibility["cancellation"] = "forbidden"
                output[key] = responsibility
                changed += 1
    return output, changed


def validate_axis_coverage(document: dict[str, Any], path: Path) -> None:
    if path.name != "rcts-v5-fixtures.json":
        return
    positives = document.get("positive", [])
    observed = {
        fixture.get("descriptor", {}).get("responsibility", {}).get("cancellation")
        for fixture in positives
    }
    expected = {"forbidden", "propagate", "observe", "shielded_cleanup"}
    if observed != expected:
        raise ValueError(f"RCTS cancellation coverage mismatch: {sorted(observed)}")
    negative_by_id = {
        fixture.get("fixture_id"): fixture for fixture in document.get("negative", [])
    }
    missing = negative_by_id.get("RCTS5-NEG-CANCELLATION-MISSING", {})
    invalid = negative_by_id.get("RCTS5-NEG-CANCELLATION-INVALID", {})
    if "cancellation" in missing.get("descriptor", {}).get("responsibility", {}):
        raise ValueError("RCTS missing-cancellation negative was normalized away")
    if invalid.get("descriptor", {}).get("responsibility", {}).get("cancellation") != "catch_as_error":
        raise ValueError("RCTS invalid-cancellation negative is not discriminating")
    coverage = document.get("coverage", {})
    if coverage.get("cancellation_axis_complete") is not True:
        raise ValueError("RCTS cancellation coverage marker is not closed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    pending_total = 0
    for path in TARGETS:
        original = json.loads(path.read_text(encoding="utf-8"))
        bound, changed = bind(original)
        validate_axis_coverage(bound, path)
        rendered = (json.dumps(bound, ensure_ascii=False, indent=2) + "\n").encode(
            "utf-8"
        )
        pending = bool(changed) or rendered != path.read_bytes()
        pending_total += int(pending)
        if args.write and pending:
            path.write_bytes(rendered)

    mode = "WRITE" if args.write else "CHECK"
    print(f"RCTS_V5_CANCELLATION_BIND_{mode}: pending_or_applied={pending_total}")
    if not args.write and pending_total:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
