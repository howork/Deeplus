#!/usr/bin/env python3
"""Generate deterministic example and surface projections from the review corpus.

This is repository tooling only. It parses static authority text and never runs
the Deeplus parser, checker, MIR, xVM, LLVM, formatter, or LSP product lanes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = Path("tools/generators/example-projections.contract.json")
EXPECTED_SCHEMA = "deeplus.example-projections-generator-contract/v1"
EXPECTED_REASSEMBLY_FIELDS = {
    "row_count",
    "ordered_shard_paths",
    "canonical_object_sha256",
}
HEADING_RE = re.compile(r"^## ([A-Za-z0-9._-]+) — (.+)$")
METADATA_RE = re.compile(r"^- \*\*(.+?):\*\* (.+)$")
SCALAR_RE = re.compile(r"^`([^`]+)`$")
STATUS_PAIR_RE = re.compile(r"^`([^`]+)` / `([^`]+)`$")
LIST_RE = re.compile(r"^`[^`]+`(?:,\s*`[^`]+`)*$")
ALLOWED_METADATA = {
    "source_feature_ids",
    "checker_trace_ids",
    "expected_outcome",
    "source_activation",
    "certification_status",
    "source_role",
    "source_root",
    "primary_diagnostic",
    "expected_warnings",
    "parser_status / checker_status",
}
REQUIRED_METADATA = ALLOWED_METADATA - {"primary_diagnostic", "expected_warnings"}
VALID_OUTCOMES = {"accept", "accept_with_gate", "reject"}


class GeneratorError(RuntimeError):
    """Bounded failure with a contract-defined machine code."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def canonical_sha(value: Any) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_output_path(root: Path, relative: str | Path) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise GeneratorError("GENERATOR_OUTPUT_ESCAPE", rel.as_posix())
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise GeneratorError("GENERATOR_OUTPUT_ESCAPE", rel.as_posix()) from exc
    return target


def read_json(path: Path, code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratorError(code, f"{path}: {exc}") from exc


def load_contract(root: Path) -> dict[str, Any]:
    path = safe_output_path(root, CONTRACT_REL)
    contract = read_json(path, "GENERATOR_AUTHORITY_GAP")
    if not isinstance(contract, dict) or contract.get("schema") != EXPECTED_SCHEMA:
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", "operational contract schema")
    required = {
        "authority_inputs",
        "manifest",
        "surfaces",
        "reassembly",
        "serialization",
        "derived_defaults",
        "required_fail_codes",
    }
    if not required.issubset(contract):
        raise GeneratorError(
            "GENERATOR_AUTHORITY_GAP",
            f"missing contract keys: {sorted(required - set(contract))}",
        )
    generated = contract["reassembly"].get("generated_fields", [])
    if len(generated) != len(set(generated)) or set(generated) != EXPECTED_REASSEMBLY_FIELDS:
        raise GeneratorError(
            "GENERATOR_REASSEMBLY_SCOPE_VIOLATION",
            f"generated_fields={generated}",
        )
    roots = [contract["manifest"].get("root")]
    roots.extend(row.get("root") for row in contract.get("surfaces", []))
    if len(roots) != 4 or len(set(roots)) != 4 or any(not row for row in roots):
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", f"owned roots={roots}")
    for rel in roots + [contract["reassembly"].get("path")]:
        safe_output_path(root, rel)
    return contract


def scalar_value(raw: str, example_id: str, key: str) -> str:
    match = SCALAR_RE.fullmatch(raw)
    if not match:
        raise GeneratorError(
            "GENERATOR_PARSE_ERROR", f"{example_id}: invalid {key} encoding"
        )
    return match.group(1)


def list_value(raw: str, example_id: str, key: str) -> list[str]:
    if raw == "`none`":
        return []
    if not LIST_RE.fullmatch(raw):
        raise GeneratorError(
            "GENERATOR_PARSE_ERROR", f"{example_id}: invalid {key} list"
        )
    values = re.findall(r"`([^`]+)`", raw)
    if not values or any(value == "none" for value in values):
        raise GeneratorError(
            "GENERATOR_PARSE_ERROR", f"{example_id}: invalid {key} values"
        )
    return values


def parse_cards(corpus: bytes, source_file: str) -> list[dict[str, Any]]:
    try:
        text = corpus.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GeneratorError("GENERATOR_PARSE_ERROR", "corpus is not UTF-8") from exc
    if "\r" in text:
        raise GeneratorError("GENERATOR_PARSE_ERROR", "corpus must use LF line endings")
    lines = text.splitlines(keepends=True)
    heading_indexes: list[int] = []
    for index, raw in enumerate(lines):
        line = raw[:-1] if raw.endswith("\n") else raw
        if line.startswith("## "):
            if not HEADING_RE.fullmatch(line):
                raise GeneratorError(
                    "GENERATOR_PARSE_ERROR", f"line {index + 1}: malformed heading"
                )
            heading_indexes.append(index)
    if not heading_indexes:
        raise GeneratorError("GENERATOR_PARSE_ERROR", "no example cards")

    cards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, start in enumerate(heading_indexes):
        end = heading_indexes[position + 1] if position + 1 < len(heading_indexes) else len(lines)
        segment = lines[start:end]
        heading = segment[0][:-1] if segment[0].endswith("\n") else segment[0]
        match = HEADING_RE.fullmatch(heading)
        assert match is not None
        example_id, title = match.groups()
        if example_id in seen:
            raise GeneratorError("GENERATOR_DUPLICATE_ID", example_id)
        seen.add(example_id)
        if not title.strip():
            raise GeneratorError("GENERATOR_PARSE_ERROR", f"{example_id}: empty title")

        fence_indexes = []
        for index, raw in enumerate(segment[1:], start=1):
            line = raw[:-1] if raw.endswith("\n") else raw
            if line.startswith("```"):
                fence_indexes.append(index)
        if len(fence_indexes) != 2:
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR",
                f"{example_id}: expected two fence lines, found {len(fence_indexes)}",
            )
        open_index, close_index = fence_indexes
        open_line = segment[open_index].rstrip("\n")
        close_line = segment[close_index].rstrip("\n")
        if open_line != "```deeplus" or close_line != "```" or close_index <= open_index:
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR", f"{example_id}: malformed Deeplus fence"
            )

        metadata: dict[str, str] = {}
        for raw in segment[1:open_index]:
            line = raw[:-1] if raw.endswith("\n") else raw
            if not line:
                continue
            item = METADATA_RE.fullmatch(line)
            if not item:
                raise GeneratorError(
                    "GENERATOR_PARSE_ERROR",
                    f"{example_id}: unparsed content before fence: {line!r}",
                )
            key, value = item.groups()
            if key not in ALLOWED_METADATA:
                raise GeneratorError(
                    "GENERATOR_PARSE_ERROR", f"{example_id}: unknown metadata {key}"
                )
            if key in metadata:
                raise GeneratorError(
                    "GENERATOR_PARSE_ERROR", f"{example_id}: duplicate metadata {key}"
                )
            metadata[key] = value
        missing = REQUIRED_METADATA - set(metadata)
        if missing:
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR",
                f"{example_id}: missing metadata {sorted(missing)}",
            )
        for raw in segment[close_index + 1 :]:
            line = raw[:-1] if raw.endswith("\n") else raw
            # A level-one section heading separates imported corpus groups and
            # is outside both adjacent cards. No other nonblank interstitial
            # content is accepted.
            if line and not line.startswith("# "):
                raise GeneratorError(
                    "GENERATOR_PARSE_ERROR",
                    f"{example_id}: unparsed content after fence: {line!r}",
                )

        source_feature_ids = list_value(
            metadata["source_feature_ids"], example_id, "source_feature_ids"
        )
        if not source_feature_ids:
            raise GeneratorError(
                "GENERATOR_AUTHORITY_GAP", f"{example_id}: empty source_feature_ids"
            )
        checker_trace_ids = list_value(
            metadata["checker_trace_ids"], example_id, "checker_trace_ids"
        )
        expected_outcome = scalar_value(
            metadata["expected_outcome"], example_id, "expected_outcome"
        )
        if expected_outcome not in VALID_OUTCOMES:
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR",
                f"{example_id}: invalid outcome {expected_outcome}",
            )
        primary = metadata.get("primary_diagnostic")
        primary_diagnostic = (
            scalar_value(primary, example_id, "primary_diagnostic")
            if primary is not None
            else None
        )
        warnings = metadata.get("expected_warnings")
        expected_warnings = (
            list_value(warnings, example_id, "expected_warnings")
            if warnings is not None
            else []
        )
        if len(expected_warnings) != len(set(expected_warnings)):
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR",
                f"{example_id}: duplicate expected_warnings",
            )
        if (expected_outcome == "reject") != bool(primary_diagnostic):
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR",
                f"{example_id}: primary diagnostic/outcome mismatch",
            )
        statuses = STATUS_PAIR_RE.fullmatch(metadata["parser_status / checker_status"])
        if not statuses:
            raise GeneratorError(
                "GENERATOR_PARSE_ERROR", f"{example_id}: invalid parser/checker status"
            )
        parser_status, checker_status = statuses.groups()
        if parser_status != "not_run" or checker_status != "not_run":
            raise GeneratorError(
                "GENERATOR_AUTHORITY_GAP",
                f"{example_id}: product status must remain not_run",
            )

        code_text = "".join(segment[open_index + 1 : close_index])
        if code_text.endswith("\n"):
            code_text = code_text[:-1]
        code = code_text.encode("utf-8")
        if not code:
            raise GeneratorError("GENERATOR_PARSE_ERROR", f"{example_id}: empty code")
        cards.append(
            {
                "example_id": example_id,
                "title": title,
                "source_feature_ids": source_feature_ids,
                "checker_trace_ids": checker_trace_ids,
                "expected_outcome": expected_outcome,
                "source_activation": scalar_value(
                    metadata["source_activation"], example_id, "source_activation"
                ),
                "certification_status": scalar_value(
                    metadata["certification_status"], example_id, "certification_status"
                ),
                "source_role": scalar_value(
                    metadata["source_role"], example_id, "source_role"
                ),
                "source_root": scalar_value(
                    metadata["source_root"], example_id, "source_root"
                ),
                "primary_diagnostic": primary_diagnostic,
                "expected_warnings": expected_warnings,
                "parser_status": parser_status,
                "checker_status": checker_status,
                "code_sha256": sha256_bytes(code),
                "source_file": source_file,
                "card_line_start": start + 1,
                "card_line_end": start + close_index + 1,
            }
        )
    return cards


def load_language_version(root: Path, relative: str) -> dict[str, Any]:
    path = safe_output_path(root, relative)
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", f"{path}: {exc}") from exc
    required = {"source_import", "grammar_schema"}
    if not required.issubset(value):
        raise GeneratorError(
            "GENERATOR_AUTHORITY_GAP",
            f"language-version missing {sorted(required - set(value))}",
        )
    return value


def shard_rows(rows: list[dict[str, Any]], max_bytes: int) -> list[list[dict[str, Any]]]:
    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for row in rows:
        candidate = current + [row]
        if current and len(json_bytes(candidate)) > max_bytes:
            chunks.append(current)
            current = [row]
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def manifest_row(card: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    defaults = contract["derived_defaults"]
    source_ids = list(card["source_feature_ids"])
    row = {
        "example_id": card["example_id"],
        "title": card["title"],
        "feature_ids": source_ids,
        "source_feature_ids": source_ids,
        "checker_trace_ids": list(card["checker_trace_ids"]),
        "provenance_ids": [card["example_id"]],
        "expected_outcome": card["expected_outcome"],
        "corpus_partition": defaults["corpus_partition"],
        "source_activation": card["source_activation"],
        "certification_status": card["certification_status"],
        "primary_diagnostic": card["primary_diagnostic"],
        "expected_warnings": list(card["expected_warnings"]),
        "source_role": card["source_role"],
        "source_root": card["source_root"],
        "parser_status": card["parser_status"],
        "checker_status": card["checker_status"],
        "code_block_id": f"{card['example_id']}-B001",
        "code_language": defaults["code_language"],
        "code_sha256": card["code_sha256"],
        "source_file": card["source_file"],
        "line_range_scope": defaults["line_range_scope"],
        "code_hash_policy": defaults["code_hash_policy"],
        "card_line_start": card["card_line_start"],
        "card_line_end": card["card_line_end"],
    }
    expected_order = contract["manifest"]["row_field_order"]
    if list(row) != expected_order:
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", "manifest field order")
    return row


def surface_row(row: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    value = {
        "example_id": row["example_id"],
        "code_sha256": row["code_sha256"],
        "feature_ids": list(row["feature_ids"]),
        "primary_diagnostic": row["primary_diagnostic"],
    }
    if list(value) != contract["surface_row_field_order"]:
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", "surface field order")
    return value


def verify_reassembly_scope(
    before: dict[str, Any], after: dict[str, Any], owned_keys: set[str]
) -> None:
    before_copy = copy.deepcopy(before)
    after_copy = copy.deepcopy(after)
    for document in (before_copy, after_copy):
        contracts = document.get("contracts", [])
        for row in contracts:
            if row.get("legacy_file") in owned_keys:
                for field in EXPECTED_REASSEMBLY_FIELDS:
                    row.pop(field, None)
    if before_copy != after_copy:
        raise GeneratorError(
            "GENERATOR_REASSEMBLY_SCOPE_VIOLATION",
            "non-owned reassembly content changed",
        )


def render_projection(root: Path) -> dict[str, Any]:
    root = root.resolve()
    contract = load_contract(root)
    inputs = contract["authority_inputs"]
    corpus_path = safe_output_path(root, inputs["corpus"])
    try:
        corpus_bytes = corpus_path.read_bytes()
    except OSError as exc:
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", f"{corpus_path}: {exc}") from exc
    cards = parse_cards(corpus_bytes, contract["manifest"]["source_file"])
    version = load_language_version(root, inputs["language_version"])
    schema_suffix = version["grammar_schema"]
    baseline = version["source_import"]
    manifest_rows = [manifest_row(card, contract) for card in cards]
    counts = Counter(row["expected_outcome"] for row in manifest_rows)
    expected_outcomes = contract["manifest"]["outcomes"]
    if set(counts) - set(expected_outcomes):
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", f"outcomes={sorted(counts)}")

    manifest_meta = {
        "schema": contract["manifest"]["schema_prefix"] + schema_suffix,
        "baseline": baseline,
        "registry_kind": contract["manifest"]["registry_kind"],
        "source_file": contract["manifest"]["source_file"],
        "example_count": len(manifest_rows),
        "outcome_counts": {name: counts.get(name, 0) for name in expected_outcomes},
        "product_parser": "NOT_RUN",
        "integrated_checker": "NOT_RUN",
    }

    documents: dict[str, tuple[dict[str, Any], list[dict[str, Any]], str]] = {}
    manifest_root = contract["manifest"]["root"]
    documents[manifest_root] = (
        manifest_meta,
        manifest_rows,
        contract["manifest"]["array_key"],
    )
    for surface in contract["surfaces"]:
        selected = [
            surface_row(row, contract)
            for row in manifest_rows
            if row["expected_outcome"] == surface["outcome"]
        ]
        metadata = {
            "schema": surface["schema_prefix"] + schema_suffix,
            "baseline": baseline,
            "result": contract["derived_defaults"]["surface_result"],
            "case_count": len(selected),
        }
        documents[surface["root"]] = (metadata, selected, surface["array_key"])

    output: dict[str, bytes] = {}
    shard_paths: dict[str, list[str]] = {}
    max_bytes = int(contract["serialization"]["max_shard_bytes"])
    for owned_root, (metadata, rows, _array_key) in documents.items():
        metadata_name = (
            contract["manifest"]["metadata"]
            if owned_root == manifest_root
            else next(
                row["metadata"]
                for row in contract["surfaces"]
                if row["root"] == owned_root
            )
        )
        metadata_rel = f"{owned_root}/{metadata_name}"
        safe_output_path(root, metadata_rel)
        output[metadata_rel] = json_bytes(metadata)
        chunks = shard_rows(rows, max_bytes)
        paths: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            rel = f"{owned_root}/chunks/part-{index:04d}.json"
            safe_output_path(root, rel)
            encoded = json_bytes(chunk)
            if len(encoded) > max_bytes:
                raise GeneratorError(
                    "GENERATOR_AUTHORITY_GAP", f"single shard exceeds {max_bytes}: {rel}"
                )
            output[rel] = encoded
            paths.append(rel)
        shard_paths[owned_root] = paths

    reassembly_rel = contract["reassembly"]["path"]
    reassembly_path = safe_output_path(root, reassembly_rel)
    reassembly = read_json(reassembly_path, "GENERATOR_AUTHORITY_GAP")
    if not isinstance(reassembly, dict) or not isinstance(reassembly.get("contracts"), list):
        raise GeneratorError("GENERATOR_AUTHORITY_GAP", "reassembly contract shape")
    updated = copy.deepcopy(reassembly)
    owned_map = contract["reassembly"]["owned_contracts"]
    by_key: dict[str, list[dict[str, Any]]] = {}
    for row in updated["contracts"]:
        by_key.setdefault(row.get("legacy_file"), []).append(row)
    if set(owned_map) != {
        key for key in owned_map if len(by_key.get(key, [])) == 1
    }:
        raise GeneratorError(
            "GENERATOR_REASSEMBLY_SCOPE_VIOLATION",
            "owned reassembly contract key missing or duplicated",
        )
    for legacy_file, owned_root in owned_map.items():
        if owned_root not in documents:
            raise GeneratorError(
                "GENERATOR_REASSEMBLY_SCOPE_VIOLATION", f"unknown root {owned_root}"
            )
        metadata, rows, array_key = documents[owned_root]
        document = dict(metadata)
        document[array_key] = rows
        row = by_key[legacy_file][0]
        row["row_count"] = len(rows)
        row["ordered_shard_paths"] = shard_paths[owned_root]
        row["canonical_object_sha256"] = canonical_sha(document)
    verify_reassembly_scope(reassembly, updated, set(owned_map))
    output[reassembly_rel] = json_bytes(updated)

    return {
        "output": output,
        "counts": {
            "all": len(manifest_rows),
            **{name: counts.get(name, 0) for name in expected_outcomes},
        },
        "shards": {root_name: len(paths) for root_name, paths in shard_paths.items()},
        "corpus_sha256": sha256_bytes(corpus_bytes),
        "documents": documents,
        "reassembly_before": reassembly,
        "reassembly_after": updated,
    }


def assert_deterministic(first: dict[str, Any], second: dict[str, Any]) -> None:
    if first["output"] != second["output"]:
        left = first["output"]
        right = second["output"]
        paths = sorted(
            path
            for path in set(left) | set(right)
            if left.get(path) != right.get(path)
        )
        raise GeneratorError("GENERATOR_NONDETERMINISTIC", ",".join(paths))


def actual_owned_paths(root: Path, contract: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    definitions = [contract["manifest"], *contract["surfaces"]]
    for row in definitions:
        owned_root = row["root"]
        metadata_rel = f"{owned_root}/{row['metadata']}"
        metadata_path = safe_output_path(root, metadata_rel)
        if metadata_path.is_file():
            paths.add(metadata_rel)
        chunks = safe_output_path(root, f"{owned_root}/chunks")
        if chunks.is_dir():
            for path in sorted(chunks.glob("part-*.json")):
                if path.is_file():
                    resolved = path.resolve()
                    try:
                        rel = resolved.relative_to(root).as_posix()
                    except ValueError as exc:
                        raise GeneratorError(
                            "GENERATOR_OUTPUT_ESCAPE", str(path)
                        ) from exc
                    paths.add(rel)
    reassembly_rel = contract["reassembly"]["path"]
    if safe_output_path(root, reassembly_rel).is_file():
        paths.add(reassembly_rel)
    return paths


def check_projection(root: Path, rendered: dict[str, Any] | None = None) -> dict[str, Any]:
    root = root.resolve()
    result = rendered or render_projection(root)
    contract = load_contract(root)
    expected = result["output"]
    actual_paths = actual_owned_paths(root, contract)
    expected_paths = set(expected)
    mismatches: list[dict[str, Any]] = []
    for rel in sorted(expected_paths | actual_paths):
        path = safe_output_path(root, rel)
        actual = path.read_bytes() if path.is_file() else None
        wanted = expected.get(rel)
        if actual != wanted:
            mismatches.append(
                {
                    "path": rel,
                    "expected_sha256": sha256_bytes(wanted) if wanted is not None else None,
                    "actual_sha256": sha256_bytes(actual) if actual is not None else None,
                }
            )
    if mismatches:
        raise GeneratorError(
            "GENERATOR_BASELINE_MISMATCH",
            json.dumps(mismatches, ensure_ascii=False, separators=(",", ":")),
        )
    return {
        "schema": "deeplus.example-projection-generator-receipt/v1",
        "mode": "check",
        "result": "PASS",
        "path_count": len(expected),
        "counts": result["counts"],
        "shards": result["shards"],
        "corpus_sha256": result["corpus_sha256"],
        "product_execution": "NOT_RUN",
    }


def write_projection(root: Path, rendered: dict[str, Any] | None = None) -> dict[str, Any]:
    root = root.resolve()
    result = rendered or render_projection(root)
    contract = load_contract(root)
    expected = result["output"]
    existing = actual_owned_paths(root, contract)
    snapshots: dict[str, bytes] = {}
    for rel in existing:
        path = safe_output_path(root, rel)
        snapshots[rel] = path.read_bytes()
    try:
        for rel, data in sorted(expected.items()):
            path = safe_output_path(root, rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        stale = sorted(existing - set(expected))
        for rel in stale:
            safe_output_path(root, rel).unlink()
    except OSError:
        for rel, data in snapshots.items():
            path = safe_output_path(root, rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for rel in set(expected) - set(snapshots):
            path = safe_output_path(root, rel)
            if path.is_file():
                path.unlink()
        raise
    return {
        "schema": "deeplus.example-projection-generator-receipt/v1",
        "mode": "write",
        "result": "PASS",
        "path_count": len(expected),
        "counts": result["counts"],
        "shards": result["shards"],
        "corpus_sha256": result["corpus_sha256"],
        "stale_removed": sorted(existing - set(expected)),
        "product_execution": "NOT_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        first = render_projection(root)
        second = render_projection(root)
        assert_deterministic(first, second)
        receipt = (
            check_projection(root, first)
            if args.check
            else write_projection(root, first)
        )
    except GeneratorError as exc:
        print(
            json.dumps(
                {"result": "FAIL", "code": exc.code, "detail": exc.detail},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
