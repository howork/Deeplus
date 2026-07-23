#!/usr/bin/env python3
"""Baseline and mutation tests for the Grammar Reference generator."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


CONTRACT_REL = Path("spec/contracts/grammar-reference-r1.json")
GENERATOR_REL = Path("tools/generators/generate_grammar_reference.py")


class TestFailure(RuntimeError):
    """A deterministic test-suite failure."""


def safe_test_path(
    root: Path,
    relative: str | Path,
    *,
    must_exist: bool,
) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise TestFailure(f"TEST_PATH_ESCAPE: {rel}")
    root = root.resolve()
    current = root
    for part in rel.parts:
        current /= part
        if current.exists() and current.is_symlink():
            raise TestFailure(f"TEST_PATH_SYMLINK: {rel.as_posix()}")
    path = root / rel
    try:
        path.resolve(strict=must_exist).relative_to(root)
    except (OSError, ValueError) as exc:
        raise TestFailure(f"TEST_PATH_ESCAPE: {rel.as_posix()}") from exc
    return path


def copy_file(source_root: Path, target_root: Path, relative: str | Path) -> None:
    rel = Path(relative)
    source = safe_test_path(source_root, rel, must_exist=True)
    target = safe_test_path(target_root, rel, must_exist=False)
    if not source.is_file():
        raise TestFailure(f"TEST_SOURCE_MISSING: {rel.as_posix()}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def copy_manual_link_targets(
    source_root: Path, target_root: Path, contract: dict
) -> None:
    generated = set(contract["generated_outputs"])
    link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for document in contract["manual_documents"]:
        path = safe_test_path(
            source_root, document["path"], must_exist=True
        )
        text = path.read_text(encoding="utf-8")
        for match in link_re.finditer(text):
            raw_target = match.group(1).strip()
            if raw_target.startswith("<") and ">" in raw_target:
                target = raw_target[1 : raw_target.index(">")]
            else:
                target = raw_target.split(maxsplit=1)[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            candidate = (path.parent / target).resolve()
            try:
                relative = candidate.relative_to(source_root)
            except ValueError:
                continue
            normalized = relative.as_posix()
            if normalized in generated or any(
                output.startswith(normalized.rstrip("/") + "/")
                for output in generated
            ):
                continue
            if candidate.is_file():
                copy_file(source_root, target_root, relative)
            elif candidate.is_dir():
                for member in sorted(candidate.rglob("*")):
                    if member.is_file() and not member.is_symlink():
                        copy_file(
                            source_root,
                            target_root,
                            member.relative_to(source_root),
                        )


def prepare_root(source_root: Path, target_root: Path) -> dict:
    contract_path = safe_test_path(
        source_root, CONTRACT_REL, must_exist=True
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    copy_file(source_root, target_root, CONTRACT_REL)
    copy_file(source_root, target_root, contract["grammar"]["path"])
    copy_file(source_root, target_root, contract["grammar"]["frontend_model_path"])
    copy_file(source_root, target_root, contract["vocabulary"]["path"])
    for row in contract["manual_documents"]:
        copy_file(source_root, target_root, row["path"])
    copy_manual_link_targets(source_root, target_root, contract)
    for row in contract["source_bindings"]:
        copy_file(source_root, target_root, row["path"])
    for definition in contract["registries"].values():
        copy_file(source_root, target_root, definition["metadata_path"])
        chunks = safe_test_path(
            source_root, definition["chunks_root"], must_exist=True
        )
        for path in sorted(chunks.glob("*.json")):
            copy_file(source_root, target_root, path.relative_to(source_root))
    return contract


def invoke(
    generator: Path, root: Path, mode: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(generator), "--root", str(root), mode],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def expect_pass(process: subprocess.CompletedProcess[str], label: str) -> None:
    if process.returncode != 0:
        raise TestFailure(
            f"{label}: expected PASS, got {process.returncode}: "
            f"{process.stderr.strip() or process.stdout.strip()}"
        )


def expect_failure(
    process: subprocess.CompletedProcess[str], label: str, code: str
) -> None:
    combined = process.stderr + process.stdout
    if process.returncode == 0 or code not in combined:
        raise TestFailure(
            f"{label}: expected {code}, got rc={process.returncode}: {combined.strip()}"
        )


def mutate_profile(root: Path, contract: dict) -> None:
    path = root / contract["grammar"]["frontend_model_path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    value["grammar_profile_counts"]["STABLE"] -= 1
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def mutate_production(root: Path, contract: dict) -> None:
    path = root / contract["grammar"]["path"]
    text = path.read_text(encoding="utf-8")
    needle = 'IgnoredListRest ::= ".." "_" ;'
    if text.count(needle) != 1:
        raise TestFailure("PRODUCTION_MUTATION_NEEDLE: expected one IgnoredListRest")
    path.write_text(text.replace(needle, "", 1), encoding="utf-8")


def mutate_generated(root: Path, _contract: dict) -> None:
    path = root / "docs/grammar-reference/SUMMARY.md"
    path.write_text(
        path.read_text(encoding="utf-8") + "\nmanual drift\n", encoding="utf-8"
    )


def mutate_missing_chapter(root: Path, contract: dict) -> None:
    path = root / contract["manual_documents"][-1]["path"]
    path.unlink()


def mutate_unknown_fence(root: Path, contract: dict) -> None:
    path = root / contract["manual_documents"][0]["path"]
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text + "\n<!-- deeplus-status-fence: UNKNOWN_FUTURE_STATUS -->\n",
        encoding="utf-8",
    )


def mutate_missing_preview_fence(root: Path, contract: dict) -> None:
    policy = contract["preview_documentation_policy"]
    path = root / policy["chapter_path"]
    text = path.read_text(encoding="utf-8")
    marker = "<!-- deeplus-status-fence: PREVIEW_NONACTIVATABLE -->"
    if marker not in text:
        raise TestFailure("PREVIEW_FENCE_MUTATION_NEEDLE: marker not found")
    path.write_text(text.replace(marker, ""), encoding="utf-8")


def mutate_missing_preview_gated_fence(root: Path, contract: dict) -> None:
    policy = contract["preview_documentation_policy"]
    path = root / policy["chapter_path"]
    text = path.read_text(encoding="utf-8")
    marker = "<!-- deeplus-status-fence: PREVIEW_GATED -->"
    if marker not in text:
        raise TestFailure("PREVIEW_GATED_MUTATION_NEEDLE: marker not found")
    path.write_text(text.replace(marker, ""), encoding="utf-8")


def mutate_missing_preview_disclaimer(root: Path, contract: dict) -> None:
    policy = contract["preview_documentation_policy"]
    path = root / policy["chapter_path"]
    text = path.read_text(encoding="utf-8")
    disclaimer = policy["activation_disclaimer"]
    if text.count(disclaimer) != 1:
        raise TestFailure(
            "PREVIEW_DISCLAIMER_MUTATION_NEEDLE: expected one disclaimer"
        )
    path.write_text(text.replace(disclaimer, "", 1), encoding="utf-8")


def mutate_missing_preview_registry_feature(root: Path, contract: dict) -> None:
    policy = contract["preview_documentation_policy"]
    path = root / policy["chapter_path"]
    text = path.read_text(encoding="utf-8")
    feature_rows = []
    feature_definition = contract["registries"]["features"]
    for chunk in sorted(
        (root / feature_definition["chunks_root"]).glob("*.json")
    ):
        feature_rows.extend(json.loads(chunk.read_text(encoding="utf-8")))
    for row in feature_rows:
        marker = f"`{row['feature_id']}`"
        if row.get("status_enum") == "PREVIEW_DESIGN" and marker in text:
            path.write_text(
                text.replace(marker, "`omitted_preview_design_feature`"),
                encoding="utf-8",
            )
            return
    raise TestFailure(
        "PREVIEW_REGISTRY_MUTATION_NEEDLE: unique feature marker not found"
    )


def mutate_json_block(
    path: Path,
    begin_marker: str,
    end_marker: str,
    mutation: Callable[[object], None],
) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(begin_marker) != 1 or text.count(end_marker) != 1:
        raise TestFailure("JSON_BLOCK_MUTATION_NEEDLE: markers")
    begin = text.index(begin_marker)
    end = text.index(end_marker)
    payload = text[begin + len(begin_marker) : end].strip()
    match = re.fullmatch(r"```json[ \t]*\n(.*)\n```", payload, re.DOTALL)
    if match is None:
        raise TestFailure("JSON_BLOCK_MUTATION_NEEDLE: fenced JSON")
    value = json.loads(match.group(1))
    mutation(value)
    replacement = (
        begin_marker
        + "\n```json\n"
        + json.dumps(value, ensure_ascii=False, indent=2)
        + "\n```\n"
        + end_marker
    )
    path.write_text(
        text[:begin] + replacement + text[end + len(end_marker) :],
        encoding="utf-8",
    )


def mutate_preview_review_card_empty(root: Path, contract: dict) -> None:
    policy = contract["preview_documentation_policy"]
    path = root / policy["chapter_path"]

    def mutation(value: object) -> None:
        if not isinstance(value, list) or not value:
            raise TestFailure("PREVIEW_CARD_MUTATION_NEEDLE: array")
        value[0]["motivation"] = ""

    mutate_json_block(
        path,
        policy["review_card_begin_marker"],
        policy["review_card_end_marker"],
        mutation,
    )


def mutate_preview_review_card_duplicate(root: Path, contract: dict) -> None:
    policy = contract["preview_documentation_policy"]
    path = root / policy["chapter_path"]

    def mutation(value: object) -> None:
        if not isinstance(value, list) or len(value) < 2:
            raise TestFailure("PREVIEW_CARD_MUTATION_NEEDLE: array")
        value[1]["feature_id"] = value[0]["feature_id"]

    mutate_json_block(
        path,
        policy["review_card_begin_marker"],
        policy["review_card_end_marker"],
        mutation,
    )


def mutate_governance_p1_block(root: Path, contract: dict) -> None:
    governance = contract["governance"]
    path = root / governance["chapter_path"]

    def mutation(value: object) -> None:
        if not isinstance(value, dict):
            raise TestFailure("GOVERNANCE_MUTATION_NEEDLE: object")
        value["feature_p1_ids"][0] = "CE-C-P1-999"

    mutate_json_block(
        path,
        governance["chapter_begin_marker"],
        governance["chapter_end_marker"],
        mutation,
    )


def mutate_governance_m13_ledger(root: Path, contract: dict) -> None:
    path = root / contract["governance"]["chapter_path"]
    text = path.read_text(encoding="utf-8")
    needle = "| `M13-A002` | `OPEN` |"
    if text.count(needle) != 1:
        raise TestFailure("M13_LEDGER_MUTATION_NEEDLE")
    path.write_text(
        text.replace(needle, "| `M13-A002` | `CLOSED` |", 1),
        encoding="utf-8",
    )


def mutate_product_lane_source(root: Path, contract: dict) -> None:
    path = root / contract["governance"]["source_path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    value["product_lanes"]["rust_frontend_lexer"] = "PASS"
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_governance_extra_action(root: Path, contract: dict) -> None:
    path = root / contract["governance"]["source_path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"].append(
        {
            "id": "XYZ-P1-001",
            "priority": "P1",
            "summary": "mutation",
        }
    )
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_governance_semantic_p0(root: Path, contract: dict) -> None:
    path = root / contract["governance"]["source_path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    value["open_actions"][0]["priority"] = "P0"
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_governance_feature_priority(root: Path, contract: dict) -> None:
    path = root / contract["governance"]["source_path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    feature_id = contract["governance"]["feature_p1_ids"][0]
    row = next(
        item for item in value["open_actions"] if item["id"] == feature_id
    )
    row["priority"] = "P2"
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_revision_parity(root: Path, contract: dict) -> None:
    path = root / contract["governance"]["source_path"]
    value = json.loads(path.read_text(encoding="utf-8"))
    value["spec_revision"] = "r-mutated-stale-reference"
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_coverage_schema_registry_count(
    root: Path, _contract: dict
) -> None:
    path = (
        root
        / "schemas/language/grammar-reference-coverage.schema.json"
    )
    value = json.loads(path.read_text(encoding="utf-8"))
    exact = value["properties"]["registries"]["properties"]["features"][
        "allOf"
    ][1]["properties"]
    exact["row_count"]["const"] = 0
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mutate_stale_generated_output(root: Path, _contract: dict) -> None:
    path = (
        root
        / "docs/grammar-reference/appendices/z-stale-generated.md"
    )
    path.write_text(
        "<!-- tools/generators/generate_grammar_reference.py가 생성함; "
        "직접 수정하지 마십시오. -->\n"
        "# 오래된 생성물\n",
        encoding="utf-8",
    )


def mutate_forbidden_candidate_path(root: Path, contract: dict) -> None:
    path = root / contract["manual_documents"][0]["path"]
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n역사 자료 경로: `candidate/legacy`\n",
        encoding="utf-8",
    )


def mutate_broken_manual_link(root: Path, contract: dict) -> None:
    path = root / contract["manual_documents"][0]["path"]
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n[깨진 링크](missing-grammar-reference.md)\n",
        encoding="utf-8",
    )


def mutate_unknown_example_reference(root: Path, contract: dict) -> None:
    path = root / contract["manual_documents"][0]["path"]
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\n알 수 없는 예제 `EX-NOT-IN-REGISTRY`.\n",
        encoding="utf-8",
    )


def mutate_example_bytes(root: Path, contract: dict) -> None:
    path = root / contract["manual_documents"][0]["path"]
    text = path.read_text(encoding="utf-8")
    needle = "    print(args)"
    if text.count(needle) != 1:
        raise TestFailure("EXAMPLE_BYTES_MUTATION_NEEDLE")
    path.write_text(
        text.replace(needle, "    print( args )", 1),
        encoding="utf-8",
    )


def mutate_missing_illustrative_marker(root: Path, contract: dict) -> None:
    path = root / "docs/grammar-reference/05-functions-methods-closures-and-calls.md"
    text = path.read_text(encoding="utf-8")
    marker = (
        "<!-- deeplus-example: illustrative; status: CURRENT_EXPLANATORY; "
        "authority-source: spec/types/type-system.md -->\n"
    )
    if text.count(marker) != 1:
        raise TestFailure("ILLUSTRATIVE_MARKER_MUTATION_NEEDLE")
    path.write_text(text.replace(marker, "", 1), encoding="utf-8")


def mutate_missing_example_visibility(root: Path, _contract: dict) -> None:
    path = root / "docs/grammar-reference/05-functions-methods-closures-and-calls.md"
    text = path.read_text(encoding="utf-8")
    needle = "private type Handler ="
    if text.count(needle) != 1:
        raise TestFailure("EXAMPLE_VISIBILITY_MUTATION_NEEDLE")
    path.write_text(
        text.replace(needle, "type Handler =", 1),
        encoding="utf-8",
    )


def mutate_cross_chapter_example_status_fence(
    root: Path, _contract: dict
) -> None:
    path = (
        root
        / "docs/grammar-reference/11-control-flow-errors-effects-and-cleanup.md"
    )
    text = path.read_text(encoding="utf-8")
    marker = (
        "<!-- deeplus-example: illustrative; "
        "status: RECOVERY_ONLY; "
        "authority-source: spec/contracts/quarantine-scope.json -->"
    )
    if text.count(marker) != 1:
        raise TestFailure("CROSS_CHAPTER_STATUS_FENCE_MUTATION_NEEDLE")
    path.write_text(
        text.replace(
            marker,
            marker.replace(
                "status: RECOVERY_ONLY",
                "status: PREVIEW_NONACTIVATABLE",
            ),
            1,
        ),
        encoding="utf-8",
    )


def mutate_registry_bound_status_fence(root: Path, _contract: dict) -> None:
    path = root / "docs/grammar-reference/08-expressions-and-operators.md"
    text = path.read_text(encoding="utf-8")
    needle = "<!-- deeplus-status-fence: PREVIEW_GATED -->"
    if text.count(needle) != 1:
        raise TestFailure("REGISTRY_BOUND_STATUS_FENCE_MUTATION_NEEDLE")
    path.write_text(
        text.replace(
            needle,
            "<!-- deeplus-status-fence: CURRENT -->",
            1,
        ),
        encoding="utf-8",
    )


def run_case(
    source_root: Path,
    generator: Path,
    label: str,
    mutation: Callable[[Path, dict], None] | None,
    expected_code: str | None,
) -> None:
    with tempfile.TemporaryDirectory(prefix="deeplus-grammar-reference-") as raw:
        root = Path(raw).resolve()
        contract = prepare_root(source_root, root)
        expect_pass(invoke(generator, root, "--write"), f"{label}:write")
        expect_pass(invoke(generator, root, "--check"), f"{label}:initial-check")
        if mutation is None:
            return
        mutation(root, contract)
        process = invoke(generator, root, "--check")
        if expected_code is None:
            raise TestFailure(f"{label}: mutation lacks expected code")
        expect_failure(process, label, expected_code)


def run_harness_path_guard_tests(source_root: Path) -> int:
    with tempfile.TemporaryDirectory(
        prefix="deeplus-grammar-reference-harness-"
    ) as raw:
        target_root = Path(raw).resolve()
        probes = [
            Path("..") / "outside.json",
            source_root.resolve() / CONTRACT_REL,
        ]
        for probe in probes:
            try:
                copy_file(source_root, target_root, probe)
            except TestFailure as exc:
                if "TEST_PATH_ESCAPE" not in str(exc):
                    raise
            else:
                raise TestFailure(
                    f"HARNESS_PATH_GUARD_ACCEPTED: {probe}"
                )
    return len(probes)


def run_determinism_test(source_root: Path, generator: Path) -> int:
    snapshots: list[dict[str, bytes]] = []
    with tempfile.TemporaryDirectory(
        prefix="deeplus-grammar-reference-determinism-"
    ) as raw:
        base = Path(raw).resolve()
        for index in range(2):
            root = base / f"root-{index}"
            root.mkdir()
            contract = prepare_root(source_root, root)
            expect_pass(
                invoke(generator, root, "--write"),
                f"determinism-{index}:write",
            )
            snapshots.append(
                {
                    relative: safe_test_path(
                        root, relative, must_exist=True
                    ).read_bytes()
                    for relative in contract["generated_outputs"]
                }
            )
    if snapshots[0] != snapshots[1]:
        raise TestFailure("GENERATOR_NONDETERMINISTIC_OUTPUT")
    return len(snapshots[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    args = parser.parse_args()
    root = args.root.resolve()
    generator = root / GENERATOR_REL
    cases: list[
        tuple[
            str,
            Callable[[Path, dict], None] | None,
            str | None,
        ]
    ] = [
        ("baseline", None, None),
        (
            "profile-mismatch",
            mutate_profile,
            "GRAMMAR_REFERENCE_FRONTEND_PROFILE_PARITY",
        ),
        (
            "production-change",
            mutate_production,
            "GRAMMAR_REFERENCE_GRAMMAR_COUNT",
        ),
        (
            "generated-drift",
            mutate_generated,
            "GRAMMAR_REFERENCE_GENERATED_DRIFT",
        ),
        (
            "missing-chapter",
            mutate_missing_chapter,
            "GRAMMAR_REFERENCE_MISSING_PATH",
        ),
        (
            "unknown-status-fence",
            mutate_unknown_fence,
            "GRAMMAR_REFERENCE_UNKNOWN_STATUS_FENCE",
        ),
        (
            "missing-preview-fence",
            mutate_missing_preview_fence,
            "GRAMMAR_REFERENCE_PREVIEW_STATUS_FENCE",
        ),
        (
            "missing-preview-gated-fence",
            mutate_missing_preview_gated_fence,
            "GRAMMAR_REFERENCE_PREVIEW_STATUS_FENCE",
        ),
        (
            "missing-preview-activation-disclaimer",
            mutate_missing_preview_disclaimer,
            "GRAMMAR_REFERENCE_PREVIEW_ACTIVATION_DISCLAIMER",
        ),
        (
            "missing-preview-registry-feature",
            mutate_missing_preview_registry_feature,
            "GRAMMAR_REFERENCE_PREVIEW_REGISTRY_COVERAGE",
        ),
        (
            "empty-preview-review-card-field",
            mutate_preview_review_card_empty,
            "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_FIELDS",
        ),
        (
            "duplicate-preview-review-card-id",
            mutate_preview_review_card_duplicate,
            "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_IDS",
        ),
        (
            "governance-p1-block-drift",
            mutate_governance_p1_block,
            "GRAMMAR_REFERENCE_GOVERNANCE_CHAPTER_BLOCK",
        ),
        (
            "governance-m13-ledger-drift",
            mutate_governance_m13_ledger,
            "GRAMMAR_REFERENCE_GOVERNANCE_M13_LEDGER",
        ),
        (
            "product-lane-source-drift",
            mutate_product_lane_source,
            "GRAMMAR_REFERENCE_GOVERNANCE_PRODUCT_LANES_SOURCE",
        ),
        (
            "governance-extra-open-action",
            mutate_governance_extra_action,
            "GRAMMAR_REFERENCE_GOVERNANCE_ACTION_SET",
        ),
        (
            "governance-semantic-p0-source",
            mutate_governance_semantic_p0,
            "GRAMMAR_REFERENCE_GOVERNANCE_P0_SOURCE",
        ),
        (
            "governance-feature-priority",
            mutate_governance_feature_priority,
            "GRAMMAR_REFERENCE_GOVERNANCE_P1_PRIORITY",
        ),
        (
            "revision-parity",
            mutate_revision_parity,
            "GRAMMAR_REFERENCE_REVISION_PARITY",
        ),
        (
            "coverage-schema-registry-count",
            mutate_coverage_schema_registry_count,
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
        ),
        (
            "stale-generated-output",
            mutate_stale_generated_output,
            "GRAMMAR_REFERENCE_STALE_GENERATED_OUTPUT",
        ),
        (
            "forbidden-candidate-path",
            mutate_forbidden_candidate_path,
            "GRAMMAR_REFERENCE_FORBIDDEN_PATH_TOKEN",
        ),
        (
            "broken-manual-link",
            mutate_broken_manual_link,
            "GRAMMAR_REFERENCE_MANUAL_LINK",
        ),
        (
            "unknown-example-reference",
            mutate_unknown_example_reference,
            "GRAMMAR_REFERENCE_UNKNOWN_EXAMPLE_REFERENCE",
        ),
        (
            "example-byte-drift",
            mutate_example_bytes,
            "GRAMMAR_REFERENCE_EXAMPLE_BINDING",
        ),
        (
            "missing-illustrative-example-marker",
            mutate_missing_illustrative_marker,
            "GRAMMAR_REFERENCE_EXAMPLE_BINDING",
        ),
        (
            "missing-example-top-level-visibility",
            mutate_missing_example_visibility,
            "GRAMMAR_REFERENCE_EXAMPLE_TOP_LEVEL_VISIBILITY",
        ),
        (
            "cross-chapter-example-status-fence-mismatch",
            mutate_cross_chapter_example_status_fence,
            "GRAMMAR_REFERENCE_EXAMPLE_STATUS_FENCE",
        ),
        (
            "registry-bound-example-status-fence-mismatch",
            mutate_registry_bound_status_fence,
            "GRAMMAR_REFERENCE_EXAMPLE_STATUS_FENCE",
        ),
    ]
    try:
        if not generator.is_file():
            raise TestFailure(f"GENERATOR_MISSING: {generator}")
        harness_guard_cases = run_harness_path_guard_tests(root)
        deterministic_output_count = run_determinism_test(root, generator)
        for label, mutation, expected_code in cases:
            run_case(root, generator, label, mutation, expected_code)
        receipt = {
            "schema": "deeplus.grammar-reference-generator-tests/r1",
            "result": "PASS",
            "cases": len(cases),
            "mutations": len(cases) - 1,
            "harness_guard_cases": harness_guard_cases,
            "deterministic_roots": 2,
            "deterministic_output_count": deterministic_output_count,
            "repository_write": False,
            "product_support": "NOT_RUN",
        }
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TestFailure) as exc:
        print(f"GRAMMAR_REFERENCE_TEST_FAILURE: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
