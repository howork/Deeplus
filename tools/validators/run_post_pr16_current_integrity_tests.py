#!/usr/bin/env python3
"""Isolated tests for the bounded Post-PR16 R4 current-integrity generator."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_REL = Path("tools/generators/generate_post_pr16_current_integrity.py")
EXCLUDES = {".git", "target", "dist", "candidate", "rfcs", "__pycache__"}
TEST_TEMP_PREFIX = ".post-pr16-integrity-test-"


def write_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run_generator(root: Path, mode: str = "--check") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / GENERATOR_REL), "--root", str(root), mode],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def copy_workspace(target: Path) -> None:
    def ignore(_path: str, names: list[str]) -> set[str]:
        return {
            name
            for name in names
            if name in EXCLUDES or name.startswith(TEST_TEMP_PREFIX)
        }

    shutil.copytree(ROOT, target, ignore=ignore)


def mutate_unit(root: Path) -> None:
    path = root / "spec/language.md"
    data = path.read_bytes()
    marker = b"<!-- POST_PR16_UNIT_BEGIN:TC-R001 -->\n"
    if data.count(marker) != 1:
        raise RuntimeError("TC-R001 wrapper unavailable")
    path.write_bytes(data.replace(marker, marker + b"mutation\n", 1))


def mutate_interstitial_bytes(root: Path) -> None:
    path = root / "spec/language.md"
    data = path.read_bytes()
    marker = b"<!-- POST_PR16_UNIT_BEGIN:TC-R001 -->\n"
    if data.count(marker) != 1:
        raise RuntimeError("TC-R001 wrapper unavailable")
    path.write_bytes(data.replace(marker, b"unbound interstitial mutation\n" + marker, 1))


def mutate_baseline_document(root: Path) -> None:
    path = root / "spec/language.md"
    data = path.read_bytes()
    needle = b"R51f is a **fully merged package-level current-canonical artifact**"
    if data.count(needle) != 1:
        raise RuntimeError("baseline language probe unavailable")
    path.write_bytes(data.replace(needle, needle.replace(b"fully", b"partly"), 1))


def mutate_preexisting_law(root: Path) -> None:
    path = root / "decisions/language/current-decisions.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["laws"][0]["law"] += " mutation"
    write_json(path, value)


def mutate_added_law_body(root: Path) -> None:
    path = root / "decisions/language/current-decisions.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["laws"][-6]["law"] += " mutation"
    write_json(path, value)


def mutate_action(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"][4]["id"] = "CE-C-P1-999"
    value["open_actions"][4]["tracking_ref"] = "deeplus-action:CE-C-P1-999"
    write_json(path, value)


def mutate_action_content(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"][4]["summary"] += " mutation"
    write_json(path, value)


def mutate_lane(root: Path) -> None:
    path = root / "current/current-pointer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["product_lanes"]["rust_frontend_parser"] = "PASSED_FOCUSED"
    write_json(path, value)


def mutate_law(root: Path) -> None:
    path = root / "decisions/language/current-decisions.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["law_count"] = 19
    write_json(path, value)


def mutate_feature_count(root: Path) -> None:
    path = root / "spec/features/catalog/catalog-metadata.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["feature_count"] = 682
    write_json(path, value)


def mutate_historical_r2_3(root: Path) -> None:
    path = root / "migration/current-document-consistency-repair-r2.3-manifest.json"
    path.write_bytes(path.read_bytes() + b" ")


def zero_owned_digests(root: Path) -> None:
    authority = root / "current/authority-map.yaml"
    authority_text = authority.read_text(encoding="utf-8")
    authority_text = re.sub(
        r"^(    sha256: )[0-9a-f]{64}$",
        r"\g<1>" + ("0" * 64),
        authority_text,
        flags=re.MULTILINE,
    )
    authority_text = re.sub(
        r"^(authority_digest: )[0-9a-f]{64}$",
        r"\g<1>" + ("0" * 64),
        authority_text,
        flags=re.MULTILINE,
    )
    with authority.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(authority_text)
    pointer = root / "current/current-pointer.json"
    pointer_value = json.loads(pointer.read_text(encoding="utf-8"))
    pointer_value["authority_digest"] = "0" * 64
    write_json(pointer, pointer_value)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cases: list[tuple[str, Callable[[Path], None], str]] = [
        ("baseline_document_byte", mutate_baseline_document, "POST_PR16_BASELINE_DRIFT"),
        ("preexisting_law_field", mutate_preexisting_law, "POST_PR16_BASELINE_DRIFT"),
        ("normalized_unit_byte", mutate_unit, "POST_PR16_UNIT_HASH"),
        ("interstitial_document_byte", mutate_interstitial_bytes, "POST_PR16_CANONICAL_TARGET_DRIFT"),
        ("added_law_body", mutate_added_law_body, "POST_PR16_CANONICAL_TARGET_DRIFT"),
        ("open_action_identity", mutate_action, "POST_PR16_POINTER_NONOWNED_DRIFT"),
        ("open_action_content", mutate_action_content, "POST_PR16_POINTER_NONOWNED_DRIFT"),
        ("product_lane_transition", mutate_lane, "POST_PR16_POINTER_NONOWNED_DRIFT"),
        ("decision_law_count", mutate_law, "POST_PR16_LAW_SET"),
        ("feature_count", mutate_feature_count, "POST_PR16_FEATURE_DRIFT"),
        ("immutable_r2_3", mutate_historical_r2_3, "POST_PR16_HISTORICAL_R2_3_DRIFT"),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix=TEST_TEMP_PREFIX, dir=ROOT) as temp:
        base = Path(temp) / "base"
        copy_workspace(base)
        initial = run_generator(base)
        results.append(
            {
                "test": "clean_check",
                "pass": initial.returncode == 0,
                "detail": (initial.stderr or initial.stdout)[-1000:],
            }
        )
        for name, mutate, expected in cases:
            target = Path(temp) / name
            shutil.copytree(base, target)
            mutate(target)
            result = run_generator(target)
            results.append(
                {
                    "test": name,
                    "pass": result.returncode != 0 and expected in result.stderr,
                    "detail": (result.stderr or result.stdout)[-1000:],
                }
            )

        write_target = Path(temp) / "deterministic_write"
        shutil.copytree(base, write_target)
        before = {
            path.relative_to(write_target).as_posix(): sha(path)
            for path in write_target.rglob("*")
            if path.is_file()
        }
        zero_owned_digests(write_target)
        mutated = {
            path.relative_to(write_target).as_posix(): sha(path)
            for path in write_target.rglob("*")
            if path.is_file()
        }
        first = run_generator(write_target, "--write")
        first_bytes = {
            rel: (write_target / rel).read_bytes()
            for rel in (
                "current/authority-map.yaml",
                "current/current-pointer.json",
            )
        }
        second = run_generator(write_target, "--write")
        check = run_generator(write_target, "--check")
        second_bytes = {
            rel: (write_target / rel).read_bytes() for rel in first_bytes
        }
        after = {
            path.relative_to(write_target).as_posix(): sha(path)
            for path in write_target.rglob("*")
            if path.is_file()
        }
        allowed = {"current/authority-map.yaml", "current/current-pointer.json"}
        changed = {
            rel
            for rel in set(mutated) | set(after)
            if mutated.get(rel) != after.get(rel)
        }
        results.append(
            {
                "test": "deterministic_bounded_write",
                "pass": (
                    first.returncode == 0
                    and second.returncode == 0
                    and check.returncode == 0
                    and first_bytes == second_bytes
                    and changed == allowed
                    and all(
                        before.get(rel) == after.get(rel)
                        for rel in set(before) | set(after)
                        if rel not in allowed
                    )
                ),
                "detail": (
                    f"changed={sorted(changed)} first={first.returncode} "
                    f"second={second.returncode} check={check.returncode} "
                    f"byte_stable={first_bytes == second_bytes}"
                ),
            }
        )

    passed = sum(bool(row["pass"]) for row in results)
    receipt = {
        "schema": "deeplus.post-pr16-current-integrity-test-receipt/r4",
        "revision": "r51f3-post-pr16-preview-design-r4",
        "result": "PASS" if passed == len(results) else "FAIL",
        "tests": len(results),
        "passed": passed,
        "product_execution": "NOT_RUN",
        "cases": results,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
