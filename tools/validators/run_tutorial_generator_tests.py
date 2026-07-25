#!/usr/bin/env python3
"""Mutation checks for the deterministic Korean tutorial generator."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(root / "tools/generators/generate_tutorial.py"),
            "--root",
            str(root),
            *args,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def require_rejected(
    result: subprocess.CompletedProcess[str], label: str
) -> bool:
    if result.returncode != 0:
        return True
    print(f"TUTORIAL_MUTATION_TEST_FAILED: {label} was accepted")
    return False


def copy_fixture(source: Path, target: Path) -> None:
    """Copy only the canonical inputs reachable from tutorial links.

    Copying the whole repository makes an otherwise small mutation test depend
    on historical export ACLs and can exceed the legacy Windows path limit.
    Keep this list aligned with the local-link surface validated by the
    tutorial generator.
    """

    fixture_members = (
        "docs/tutorial",
        "docs/grammar-reference",
        "docs/guide/example-host-adapters.md",
        "current",
        "examples/guide",
        "library/prelude",
        "rfcs",
        "schemas/language",
        "spec",
        "tools/generators/generate_tutorial.py",
    )
    for relative_text in fixture_members:
        relative = Path(relative_text)
        source_member = source / relative
        target_member = target / relative
        if source_member.is_dir():
            shutil.copytree(source_member, target_member)
        else:
            target_member.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_member, target_member)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    source = parser.parse_args().root.resolve()
    baseline = run(source, "--check")
    if baseline.returncode:
        print(baseline.stdout, end="")
        print(baseline.stderr, end="", file=sys.stderr)
        return baseline.returncode

    # Some managed Windows environments redirect the system temporary
    # directory to a location that can be listed but not populated by a child
    # process.  Keep the isolated copy under the already ignored build tree;
    # the copy operation excludes ``target`` so it cannot recurse into itself.
    isolated_root = source / "target" / "tutorial-generator-tests"
    isolated_root.mkdir(parents=True, exist_ok=True)
    raw = isolated_root / uuid.uuid4().hex[:8]
    raw.mkdir()
    try:
        target = raw / "r"
        target.mkdir()
        copy_fixture(source, target)

        first_write = run(target, "--write")
        if first_write.returncode:
            print(first_write.stdout, end="")
            print(first_write.stderr, end="", file=sys.stderr)
            return first_write.returncode
        manifest = target / "docs/tutorial/coverage-manifest.json"
        report = target / "docs/tutorial/coverage-report.md"
        first_bytes = (manifest.read_bytes(), report.read_bytes())
        second_write = run(target, "--write")
        if second_write.returncode:
            print(second_write.stdout, end="")
            print(second_write.stderr, end="", file=sys.stderr)
            return second_write.returncode
        if first_bytes != (manifest.read_bytes(), report.read_bytes()):
            print(
                "TUTORIAL_MUTATION_TEST_FAILED: repeated generation "
                "changed output bytes"
            )
            return 1

        source = target / "spec/language.md"
        original_source = source.read_bytes()
        source.write_bytes(original_source + b"\n")
        mutated = run(target, "--write")
        if not require_rejected(mutated, "bound source identity drift"):
            return 1
        source.write_bytes(original_source)

        contract_path = target / "spec/contracts/tutorial-r1.json"
        original_contract = contract_path.read_bytes()
        contract = json.loads(original_contract.decode("utf-8"))
        contract["governance"]["semantic_p0"] = 1
        contract_path.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "semantic P0 drift"):
            return 1
        contract_path.write_bytes(original_contract)

        contract = json.loads(original_contract.decode("utf-8"))
        contract["governance"]["feature_p1_ids"][0] = "UNKNOWN-P1"
        contract_path.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "exact feature P1 set drift"):
            return 1
        contract_path.write_bytes(original_contract)

        contract = json.loads(original_contract.decode("utf-8"))
        contract["governance"]["product_lane_status"] = "PASS"
        contract_path.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "product lane status drift"):
            return 1
        contract_path.write_bytes(original_contract)

        pointer_path = target / "current/current-pointer.json"
        original_pointer = pointer_path.read_bytes()
        pointer = json.loads(original_pointer.decode("utf-8"))
        pointer["open_actions"][0]["priority"] = "P0"
        pointer_path.write_text(
            json.dumps(pointer, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "pointer semantic P0 drift"):
            return 1
        pointer_path.write_bytes(original_pointer)

        pointer = json.loads(original_pointer.decode("utf-8"))
        feature_row = next(
            row
            for row in pointer["open_actions"]
            if row["id"] == "CE-C-P1-001"
        )
        feature_row["id"] = "UNKNOWN-P1"
        pointer_path.write_text(
            json.dumps(pointer, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "pointer feature P1 set drift"):
            return 1
        pointer_path.write_bytes(original_pointer)

        pointer = json.loads(original_pointer.decode("utf-8"))
        first_lane = next(iter(pointer["product_lanes"]))
        pointer["product_lanes"][first_lane] = "PASS"
        pointer_path.write_text(
            json.dumps(pointer, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "pointer product lane drift"):
            return 1
        pointer_path.write_bytes(original_pointer)

        mixed_chapter = (
            target
            / "docs/tutorial/part-01-orientation/01-01-language-status.md"
        )
        original = mixed_chapter.read_text(encoding="utf-8")
        mixed_chapter.write_text(
            original.replace("NOT_RUN", "UNSPECIFIED"),
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "missing product NOT_RUN fence"):
            return 1
        mixed_chapter.write_text(original, encoding="utf-8")

        status_chapter = (
            target
            / "docs/tutorial/part-01-orientation/01-02-source-diagnostics.md"
        )
        original = status_chapter.read_text(encoding="utf-8")
        status_chapter.write_text(
            original.replace(
                "CURRENT_DESIGN_PRODUCT_NOT_RUN", "UNSPECIFIED", 1
            ),
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "unapproved leading status token"):
            return 1
        status_chapter.write_text(original, encoding="utf-8")

        summary = target / "docs/tutorial/SUMMARY.md"
        original = summary.read_text(encoding="utf-8")
        first_target = (
            "part-01-orientation/01-01-language-status.md"
        )
        summary.write_text(
            original.replace(first_target, "../README.md", 1),
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "unsafe SUMMARY traversal"):
            return 1
        summary.write_text(original, encoding="utf-8")

        wrong_target = (
            target
            / "docs/tutorial/part-01-orientation/"
            "02-01-language-status.md"
        )
        shutil.copyfile(
            target
            / "docs/tutorial/part-01-orientation/"
            "01-01-language-status.md",
            wrong_target,
        )
        summary.write_text(
            original.replace(
                first_target,
                "part-01-orientation/02-01-language-status.md",
                1,
            ),
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "cross-Part chapter numbering"):
            return 1
        summary.write_text(original, encoding="utf-8")
        wrong_target.unlink()

        schema_path = (
            target / "schemas/language/tutorial-coverage.schema.json"
        )
        original_schema = schema_path.read_bytes()
        schema = json.loads(original_schema.decode("utf-8"))
        schema["properties"]["members"]["maxItems"] = 100
        schema_path.write_text(
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        mutated = run(target, "--write")
        if not require_rejected(mutated, "schema/member cardinality drift"):
            return 1
        schema_path.write_bytes(original_schema)
    finally:
        shutil.rmtree(raw)

    print("TUTORIAL_MUTATION_TEST_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
