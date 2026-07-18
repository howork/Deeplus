#!/usr/bin/env python3
"""Static and mutation tests for the R2.2 example projection generator."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "tools/generators/generate_example_projections.py"
KNOWN_DRIFT_FIXTURE = (
    ROOT
    / "tools/validators/fixtures/example-projection-known-baseline-drift-r2_2.json"
)
FIXTURE_FILES = [
    "examples/guide/review-corpus.md",
    "current/language-version.toml",
    "tools/generators/example-projections.contract.json",
    "migration/catalog-reassembly.json",
]
FIXTURE_ROOTS = [
    "examples/manifests/by-outcome",
    "tests/conformance/surface/positive",
    "tests/conformance/surface/rejected",
    "tests/conformance/surface/gated",
]


def load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("deeplus_example_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(source: Path, target: Path) -> None:
    for relative in FIXTURE_FILES:
        src = source / relative
        dst = target / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    for relative in FIXTURE_ROOTS:
        shutil.copytree(source / relative, target / relative)


def git_output(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True
    )
    return result.stdout


def copy_frozen_fixture(target: Path, fixture: dict[str, Any]) -> None:
    """Materialize only the declared generator inputs/targets from frozen Git."""
    commit = fixture["frozen_base"]["commit"]
    tree = git_output("rev-parse", f"{commit}^{{tree}}").decode().strip()
    assert tree == fixture["frozen_base"]["tree"], (tree, fixture["frozen_base"]["tree"])
    frozen_paths = [
        "examples/guide/review-corpus.md",
        "current/language-version.toml",
        "migration/catalog-reassembly.json",
    ]
    listed = git_output(
        "ls-tree", "-r", "--name-only", commit, "--", *FIXTURE_ROOTS
    ).decode("utf-8").splitlines()
    for relative in [*frozen_paths, *listed]:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(git_output("show", f"{commit}:{relative}"))
    contract_target = target / "tools/generators/example-projections.contract.json"
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "tools/generators/example-projections.contract.json", contract_target)


def actual_manifest_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "examples/manifests/by-outcome/chunks").glob("part-*.json")):
        rows.extend(json.loads(path.read_text(encoding="utf-8")))
    return rows


def actual_manifest_shard_rows(root: Path) -> list[int]:
    return [
        len(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((root / "examples/manifests/by-outcome/chunks").glob("part-*.json"))
    ]


def rendered_manifest_shard_rows(rendered: dict[str, Any]) -> list[int]:
    return [
        len(json.loads(data))
        for relative, data in sorted(rendered["output"].items())
        if relative.startswith("examples/manifests/by-outcome/chunks/part-")
    ]


def authority_row_diffs(root: Path, rendered: dict[str, Any]) -> list[dict[str, Any]]:
    frozen_rows = actual_manifest_rows(root)
    expected_rows = rendered["documents"]["examples/manifests/by-outcome"][1]
    assert len(frozen_rows) == len(expected_rows)
    differences: list[dict[str, Any]] = []
    for frozen, expected in zip(frozen_rows, expected_rows):
        assert frozen["example_id"] == expected["example_id"]
        for field in sorted(set(frozen) | set(expected)):
            if frozen.get(field) != expected.get(field):
                differences.append(
                    {
                        "example_id": expected["example_id"],
                        "field": field,
                        "frozen": frozen.get(field),
                        "rendered": expected.get(field),
                    }
                )
    return differences


def run_known_drift_gate(
    generator: ModuleType,
    frozen_root: Path,
    fixture: dict[str, Any],
    exercised: set[str],
) -> dict[str, Any]:
    before = snapshot(frozen_root)
    first = generator.render_projection(frozen_root)
    second = generator.render_projection(frozen_root)
    generator.assert_deterministic(first, second)
    try:
        generator.check_projection(frozen_root, first)
    except generator.GeneratorError as exc:  # type: ignore[attr-defined]
        assert exc.code == "GENERATOR_BASELINE_MISMATCH", (exc.code, exc.detail)
        mismatches = json.loads(exc.detail)
        exercised.add(exc.code)
    else:
        raise AssertionError("frozen strict check unexpectedly passed")
    after = snapshot(frozen_root)
    assert before == after, "known-drift gate wrote frozen fixture files"

    gate = fixture["gate"]
    mismatch_paths = sorted(row["path"] for row in mismatches)
    assert mismatch_paths == sorted(gate["allowed_projection_paths"]), mismatch_paths
    differences = authority_row_diffs(frozen_root, first)
    expected_differences = [
        {key: row[key] for key in ("example_id", "field", "frozen", "rendered")}
        for row in fixture["row_dispositions"]
    ]
    assert differences == expected_differences, differences
    assert len(mismatches) == gate["projection_mismatch_count"]
    assert len(differences) == gate["authority_row_diff_count"]
    assert len({row["example_id"] for row in differences}) == gate["authority_row_count"]
    assert first["counts"] == gate["counts"]
    assert first["shards"] == gate["rendered_shard_counts"]
    frozen_shard_counts = {
        "examples/manifests/by-outcome": len(
            list((frozen_root / "examples/manifests/by-outcome/chunks").glob("part-*.json"))
        ),
        "tests/conformance/surface/positive": len(
            list((frozen_root / "tests/conformance/surface/positive/chunks").glob("part-*.json"))
        ),
        "tests/conformance/surface/rejected": len(
            list((frozen_root / "tests/conformance/surface/rejected/chunks").glob("part-*.json"))
        ),
        "tests/conformance/surface/gated": len(
            list((frozen_root / "tests/conformance/surface/gated/chunks").glob("part-*.json"))
        ),
    }
    assert frozen_shard_counts == gate["frozen_shard_counts"]
    assert actual_manifest_shard_rows(frozen_root) == gate["frozen_manifest_shard_rows"]
    assert rendered_manifest_shard_rows(first) == gate["rendered_manifest_shard_rows"]
    assert first["corpus_sha256"] == fixture["frozen_base"]["corpus_sha256"]
    assert gate["unknown_path_diffs"] == 0 and gate["unknown_row_diffs"] == 0
    assert gate["generated_write_during_gate"] is False
    return {
        "result": "PASS_KNOWN_BASELINE_DRIFT",
        "projection_mismatch_count": len(mismatches),
        "authority_row_diff_count": len(differences),
        "authority_row_count": len({row["example_id"] for row in differences}),
        "unknown_path_diffs": 0,
        "unknown_row_diffs": 0,
        "counts": first["counts"],
        "frozen_shards": frozen_shard_counts,
        "rendered_shards": first["shards"],
        "generated_write": False,
        "before_after_hashes_equal": True,
        "product_execution": "NOT_RUN",
    }


def snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def mutate_text(root: Path, relative: str, transform: Callable[[str], str]) -> None:
    path = root / relative
    before = path.read_text(encoding="utf-8")
    after = transform(before)
    if before == after:
        raise AssertionError(f"mutation made no change: {relative}")
    write_text(path, after)


def expect_code(
    generator: ModuleType,
    code: str,
    action: Callable[[], Any],
    exercised: set[str],
) -> None:
    try:
        action()
    except generator.GeneratorError as exc:  # type: ignore[attr-defined]
        if exc.code != code:
            raise AssertionError(f"expected {code}, received {exc.code}: {exc.detail}") from exc
        exercised.add(code)
        return
    raise AssertionError(f"expected {code}")


def first_match_remove(pattern: str, text: str) -> str:
    changed, count = re.subn(pattern, "", text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise AssertionError(f"pattern not found: {pattern}")
    return changed


def load_json_bytes(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"))


def main() -> int:
    generator = load_generator()
    tests: list[str] = []
    exercised: set[str] = set()
    try:
        with tempfile.TemporaryDirectory(prefix="deeplus-example-generator-") as temp:
            fixture = json.loads(KNOWN_DRIFT_FIXTURE.read_text(encoding="utf-8"))
            assert fixture["revision"] == "R2.2"
            assert fixture["evidence_classification"] == (
                "FROZEN_HISTORICAL_REPAIR_EVIDENCE_NOT_SOURCE_OR_PROJECTION_AUTHORITY"
            )
            frozen_root = Path(temp) / "frozen-known-drift"
            copy_frozen_fixture(frozen_root, fixture)
            known_drift = run_known_drift_gate(
                generator, frozen_root, fixture, exercised
            )
            tests.extend(
                [
                    "known_frozen_drift_exact_set",
                    "known_frozen_drift_read_only",
                    "deterministic_double_render",
                ]
            )

            temp_root = Path(temp) / "normal-write-check"
            copy_fixture(ROOT, temp_root)
            baseline = generator.render_projection(temp_root)
            second = generator.render_projection(temp_root)
            generator.assert_deterministic(baseline, second)
            generator.write_projection(temp_root, baseline)
            before = snapshot(temp_root)
            generator.check_projection(temp_root, baseline)
            after = snapshot(temp_root)
            assert before == after, "ordinary --check modified the normalized fixture"
            tests.extend(["normal_write_check_in_temporary_copy", "strict_check_read_only"])

            generator_text = GENERATOR.read_text(encoding="utf-8")
            assert KNOWN_DRIFT_FIXTURE.name not in generator_text
            tests.append("normal_modes_do_not_read_known_drift_fixture")

            contract = json.loads(
                (temp_root / "tools/generators/example-projections.contract.json").read_text(
                    encoding="utf-8"
                )
            )
            baseline_gate = contract["baseline_gate"]
            baseline_gate_active = known_drift["result"] == "PASS_KNOWN_BASELINE_DRIFT"
            if baseline["corpus_sha256"] == baseline_gate["corpus_sha256"]:
                assert baseline["counts"] == baseline_gate["counts"]
                assert baseline["shards"] == baseline_gate["shards"]
            tests.append("unchanged_baseline_counts_and_shards")

            def case(name: str) -> Path:
                target = Path(temp) / name
                copy_fixture(ROOT, target)
                return target

            duplicate = case("duplicate")
            mutate_text(
                duplicate,
                "examples/guide/review-corpus.md",
                lambda text: text.replace("## EX-R48-002 —", "## EX-R48-001 —", 1),
            )
            expect_code(
                generator,
                "GENERATOR_DUPLICATE_ID",
                lambda: generator.render_projection(duplicate),
                exercised,
            )
            tests.append("duplicate_id_rejected")

            for name, transform in [
                (
                    "missing_metadata",
                    lambda text: first_match_remove(r"^- \*\*source_root:\*\* `[^`]+`\n", text),
                ),
                (
                    "duplicate_metadata",
                    lambda text: text.replace(
                        "- **source_root:** `ScriptSourceFile`\n",
                        "- **source_root:** `ScriptSourceFile`\n- **source_root:** `ScriptSourceFile`\n",
                        1,
                    ),
                ),
                (
                    "unknown_metadata",
                    lambda text: text.replace(
                        "- **source_root:** `ScriptSourceFile`\n",
                        "- **source_root:** `ScriptSourceFile`\n- **unknown_key:** `forbidden`\n",
                        1,
                    ),
                ),
            ]:
                target = case(name)
                mutate_text(target, "examples/guide/review-corpus.md", transform)
                expect_code(
                    generator,
                    "GENERATOR_PARSE_ERROR",
                    lambda target=target: generator.render_projection(target),
                    exercised,
                )
            tests.append("missing_duplicate_unknown_metadata_rejected")

            for name, transform in [
                ("missing_fence", lambda text: text.replace("```deeplus\n", "", 1)),
                ("malformed_fence", lambda text: text.replace("```deeplus\n", "```Deeplus\n", 1)),
                (
                    "multiple_fence",
                    lambda text: text.replace(
                        "```deeplus\n", "```deeplus\n```\n```deeplus\n", 1
                    ),
                ),
            ]:
                target = case(name)
                mutate_text(target, "examples/guide/review-corpus.md", transform)
                expect_code(
                    generator,
                    "GENERATOR_PARSE_ERROR",
                    lambda target=target: generator.render_projection(target),
                    exercised,
                )
            tests.append("malformed_multiple_missing_fences_rejected")

            reject_without_primary = case("reject_without_primary")
            mutate_text(
                reject_without_primary,
                "examples/guide/review-corpus.md",
                lambda text: first_match_remove(r"^- \*\*primary_diagnostic:\*\* `[^`]+`\n", text),
            )
            expect_code(
                generator,
                "GENERATOR_PARSE_ERROR",
                lambda: generator.render_projection(reject_without_primary),
                exercised,
            )
            accept_with_primary = case("accept_with_primary")
            mutate_text(
                accept_with_primary,
                "examples/guide/review-corpus.md",
                lambda text: text.replace(
                    "- **source_root:** `ScriptSourceFile`\n",
                    "- **source_root:** `ScriptSourceFile`\n- **primary_diagnostic:** `FORBIDDEN_ON_ACCEPT`\n",
                    1,
                ),
            )
            expect_code(
                generator,
                "GENERATOR_PARSE_ERROR",
                lambda: generator.render_projection(accept_with_primary),
                exercised,
            )
            tests.append("primary_diagnostic_outcome_law")

            authority_gap = case("authority_gap")
            mutate_text(
                authority_gap,
                "current/language-version.toml",
                lambda text: first_match_remove(r"^source_import = .+\n", text),
            )
            expect_code(
                generator,
                "GENERATOR_AUTHORITY_GAP",
                lambda: generator.render_projection(authority_gap),
                exercised,
            )
            tests.append("authority_gap_rejected")

            code_mutation = case("code_mutation")
            mutate_text(
                code_mutation,
                "examples/guide/review-corpus.md",
                lambda text: text.replace("let row = #[1, 2, 3]", "let row_x = #[1, 2, 3]", 1),
            )
            changed = generator.render_projection(code_mutation)
            changed_paths = {
                path
                for path in set(baseline["output"]) | set(changed["output"])
                if baseline["output"].get(path) != changed["output"].get(path)
            }
            assert changed_paths == {
                "examples/manifests/by-outcome/chunks/part-0001.json",
                "tests/conformance/surface/positive/chunks/part-0001.json",
                "migration/catalog-reassembly.json",
            }, changed_paths
            baseline_manifest = load_json_bytes(
                baseline["output"]["examples/manifests/by-outcome/chunks/part-0001.json"]
            )[0]
            changed_manifest = load_json_bytes(
                changed["output"]["examples/manifests/by-outcome/chunks/part-0001.json"]
            )[0]
            assert {
                key: value for key, value in baseline_manifest.items() if key != "code_sha256"
            } == {key: value for key, value in changed_manifest.items() if key != "code_sha256"}
            assert baseline_manifest["code_sha256"] != changed_manifest["code_sha256"]
            generator.verify_reassembly_scope(
                changed["reassembly_before"],
                changed["reassembly_after"],
                set(contract["reassembly"]["owned_contracts"]),
            )
            tests.append("controlled_code_hash_dependency")

            stale = case("stale")
            stale_render = generator.render_projection(stale)
            generator.write_projection(stale, stale_render)
            stale_path = stale / "tests/conformance/surface/gated/chunks/part-9999.json"
            stale_path.write_text("[]\n", encoding="utf-8", newline="\n")
            stale_render = generator.render_projection(stale)
            expect_code(
                generator,
                "GENERATOR_BASELINE_MISMATCH",
                lambda: generator.check_projection(stale, stale_render),
                exercised,
            )
            write_receipt = generator.write_projection(stale, stale_render)
            assert write_receipt["stale_removed"] == [
                "tests/conformance/surface/gated/chunks/part-9999.json"
            ]
            assert not stale_path.exists()
            generator.check_projection(stale)
            tests.append("stale_shard_detected_and_bounded_write_removed")

            escape = case("escape")
            escape_contract_path = escape / "tools/generators/example-projections.contract.json"
            escape_contract = json.loads(escape_contract_path.read_text(encoding="utf-8"))
            escape_contract["manifest"]["root"] = "../escape"
            write_text(escape_contract_path, json.dumps(escape_contract, ensure_ascii=False, indent=2) + "\n")
            expect_code(
                generator,
                "GENERATOR_OUTPUT_ESCAPE",
                lambda: generator.render_projection(escape),
                exercised,
            )
            tests.append("output_escape_rejected")

            bad_scope = case("bad_scope")
            bad_contract_path = bad_scope / "tools/generators/example-projections.contract.json"
            bad_contract = json.loads(bad_contract_path.read_text(encoding="utf-8"))
            bad_contract["reassembly"]["generated_fields"].append("legacy_file")
            write_text(bad_contract_path, json.dumps(bad_contract, ensure_ascii=False, indent=2) + "\n")
            expect_code(
                generator,
                "GENERATOR_REASSEMBLY_SCOPE_VIOLATION",
                lambda: generator.render_projection(bad_scope),
                exercised,
            )
            tests.append("reassembly_scope_violation_rejected")

            nondeterministic = copy.deepcopy(baseline)
            arbitrary_path = sorted(nondeterministic["output"])[0]
            nondeterministic["output"][arbitrary_path] += b" "
            expect_code(
                generator,
                "GENERATOR_NONDETERMINISTIC",
                lambda: generator.assert_deterministic(baseline, nondeterministic),
                exercised,
            )
            tests.append("nondeterminism_fail_code_exercised")

            manifest_meta = load_json_bytes(
                baseline["output"]["examples/manifests/by-outcome/catalog-metadata.json"]
            )
            assert manifest_meta["product_parser"] == "NOT_RUN"
            assert manifest_meta["integrated_checker"] == "NOT_RUN"
            for relative, data in baseline["output"].items():
                if relative.endswith("catalog-metadata.json") and relative.startswith(
                    "tests/conformance/surface/"
                ):
                    assert load_json_bytes(data)["result"] == "NOT_RUN"
            manifest_rows = baseline["documents"]["examples/manifests/by-outcome"][1]
            assert all(
                row["parser_status"] == "not_run" and row["checker_status"] == "not_run"
                for row in manifest_rows
            )
            tests.append("product_not_run_preserved")

            required_codes = set(contract["required_fail_codes"])
            assert exercised == required_codes, (exercised, required_codes)
            receipt = {
                "schema": "deeplus.example-projection-generator-test-receipt/v1",
                "result": "PASS",
                "tests": tests,
                "test_count": len(tests),
                "required_fail_codes_exercised": sorted(exercised),
                "baseline_gate_active": baseline_gate_active,
                "known_baseline_drift": known_drift,
                "counts": baseline["counts"],
                "shards": baseline["shards"],
                "product_execution": "NOT_RUN",
            }
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
            return 0
    except Exception as exc:  # bounded test runner receipt
        print(
            json.dumps(
                {
                    "schema": "deeplus.example-projection-generator-test-receipt/v1",
                    "result": "FAIL",
                    "error": f"{type(exc).__name__}: {exc}",
                    "tests_completed": tests,
                    "required_fail_codes_exercised": sorted(exercised),
                    "product_execution": "NOT_RUN",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
