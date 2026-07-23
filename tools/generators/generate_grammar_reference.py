#!/usr/bin/env python3
"""Render and verify the deterministic Deeplus Grammar Reference projection.

The reference is a documentation projection, not a second semantic authority.
This generator binds its manual chapters and generated indexes to the exact
grammar, frontend model, registries, Prelude, and example corpus.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/grammar-reference-r1.json"
MANIFEST_REL = "docs/grammar-reference/coverage-manifest.json"
EXPECTED_COVERAGE_SCHEMA_PATH = (
    "schemas/language/grammar-reference-coverage.schema.json"
)
SCHEMA = "deeplus.grammar-reference-contract/r1"
MANIFEST_SCHEMA = "deeplus.grammar-reference-coverage/r1"
GENERATED_BANNER = (
    "<!-- tools/generators/generate_grammar_reference.py가 생성함; "
    "직접 수정하지 마십시오. -->\n"
)
DOCUMENT_STATUS_RE = re.compile(
    r"<!--\s*deeplus-grammar-reference-status:\s*([A-Z0-9_]+)\s*-->"
)
STATUS_FENCE_RE = re.compile(
    r"<!--\s*deeplus-status-fence:\s*([A-Z0-9_]+)\s*-->"
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
EXAMPLE_REF_RE = re.compile(r"`(EX-[A-Za-z0-9-]+)`")
DEEPLUS_BLOCK_RE = re.compile(
    r"(?m)^```deeplus[ \t]*\n(.*?)^```[ \t]*$", re.DOTALL
)
HEADING_RE = re.compile(r"(?m)^#{1,6}[ \t]+.+$")
ILLUSTRATIVE_EXAMPLE_RE = re.compile(
    r"<!--\s*deeplus-example:\s*illustrative;\s*"
    r"status:\s*([A-Z0-9_]+);\s*"
    r"authority-source:\s*([^\s]+)\s*-->"
)
PROFILE_MARKER_RE = re.compile(
    r"(?m)^[ \t]*PROFILE:[ \t]*(LEXICAL|STABLE|PREVIEW|RECOVERY)[ \t]*$"
)
PRODUCTION_RE = re.compile(r"(?m)^([A-Za-z][A-Za-z0-9_]*)[ \t]*::=")
EXPECTED_COUNTS = {
    "grammar_productions": 560,
    "features": 688,
    "diagnostics": 1281,
    "predicates": 247,
    "prelude_entries": 56,
    "examples": 703,
    "hard_keywords": 30,
    "contextual_words": 101,
}
EXPECTED_PROFILES = {
    "LEXICAL": 89,
    "STABLE": 443,
    "PREVIEW": 13,
    "RECOVERY": 15,
}
EXPECTED_FENCES = {
    "CURRENT",
    "PREVIEW_GATED",
    "PREVIEW_NONACTIVATABLE",
    "RECOVERY_ONLY",
    "REMOVED",
}
EXPECTED_PREVIEW_POLICY = {
    "chapter_path": (
        "docs/grammar-reference/15-preview-recovery-and-removed-surfaces.md"
    ),
    "status_fence_scope": "UNTIL_NEXT_FENCE_OR_EOF",
    "required_status_fences": [
        "PREVIEW_GATED",
        "PREVIEW_NONACTIVATABLE",
        "RECOVERY_ONLY",
        "REMOVED",
    ],
    "activation_disclaimer": (
        "이 장의 Preview 설계 문서화는 구문, 구현, 제품 지원 또는 "
        "활성화 권위를 부여하지 않는다."
    ),
    "required_registry_status_counts": {
        "PREVIEW": 3,
        "PREVIEW_DESIGN": 47,
    },
    "review_card_begin_marker": (
        "<!-- deeplus-preview-design-review-cards: begin -->"
    ),
    "review_card_end_marker": (
        "<!-- deeplus-preview-design-review-cards: end -->"
    ),
    "review_card_fields": [
        "motivation",
        "surface_or_api",
        "static_semantics_and_interactions",
        "diagnostics_migration_tooling",
        "open_alternatives",
        "activation_prerequisites",
    ],
    "required_review_card_count": 47,
}
EXPECTED_MANUAL_QUALITY_POLICY = {
    "forbidden_path_tokens": ["candidate/", "candidate\\"],
    "illustrative_example_marker": "deeplus-example: illustrative",
    "allowed_illustrative_statuses": [
        "CURRENT_EXPLANATORY",
        "PREVIEW_GATED",
        "PREVIEW_NONACTIVATABLE",
        "RECOVERY_ONLY",
        "REJECTED_EXPLANATORY",
    ],
    "generated_link_targets_are_planned_valid": True,
}
ILLUSTRATIVE_STATUS_FENCES = {
    "CURRENT_EXPLANATORY": "CURRENT",
    "PREVIEW_GATED": "PREVIEW_GATED",
    "PREVIEW_NONACTIVATABLE": "PREVIEW_NONACTIVATABLE",
    "RECOVERY_ONLY": "RECOVERY_ONLY",
    "REJECTED_EXPLANATORY": "CURRENT",
}
EXPECTED_FEATURE_P1_IDS = [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
EXPECTED_M13_ACTION_IDS = [
    "M13-A002",
    "M13-A003",
    "M13-A004",
    "M13-A005",
]
EXPECTED_PRODUCT_LANE_IDS = [
    "rust_frontend_lexer",
    "rust_frontend_parser",
    "rust_hir_lowering",
    "rust_integrated_checker",
    "deeplus_mir_lowering",
    "xvm_bytecode_emitter",
    "xvm_interpreter",
    "llvm_aot_backend",
    "llvm_orc_jit_backend",
    "formatter_lsp",
    "stdlib_provider_runner",
    "official_tooling",
    "independent_conformance",
    "cross_backend_conformance",
    "actual_user_team_study",
]
EXPECTED_GOVERNANCE = {
    "source_path": "current/current-pointer.json",
    "chapter_path": (
        "docs/grammar-reference/15-preview-recovery-and-removed-surfaces.md"
    ),
    "semantic_p0": 0,
    "feature_p1_status": "OPEN",
    "feature_p1_ids": EXPECTED_FEATURE_P1_IDS,
    "separate_action_status": "OPEN",
    "separate_open_action_ids": EXPECTED_M13_ACTION_IDS,
    "product_lane_status": "NOT_RUN",
    "product_lane_ids": EXPECTED_PRODUCT_LANE_IDS,
    "chapter_begin_marker": "<!-- deeplus-governance-invariants: begin -->",
    "chapter_end_marker": "<!-- deeplus-governance-invariants: end -->",
}


class GeneratorError(RuntimeError):
    """A stable generator failure code and detail."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def safe_path(root: Path, relative: str, *, must_exist: bool = True) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise GeneratorError("GRAMMAR_REFERENCE_PATH_ESCAPE", relative)
    root = root.resolve()
    current = root
    for part in rel.parts:
        current /= part
        if current.exists() and current.is_symlink():
            raise GeneratorError("GRAMMAR_REFERENCE_PATH_SYMLINK", relative)
    path = root / rel
    if must_exist and not path.exists():
        raise GeneratorError("GRAMMAR_REFERENCE_MISSING_PATH", relative)
    try:
        path.resolve(strict=must_exist).relative_to(root)
    except (OSError, ValueError) as exc:
        raise GeneratorError("GRAMMAR_REFERENCE_PATH_ESCAPE", relative) from exc
    if must_exist and not path.is_file() and not path.is_dir():
        raise GeneratorError("GRAMMAR_REFERENCE_MISSING_PATH", relative)
    return path


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: Path, code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratorError(code, f"{path}: {exc}") from exc


def file_binding(path: Path, root: Path, *, binding_id: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    row: dict[str, Any] = {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }
    if binding_id is not None:
        row = {"id": binding_id, **row}
    return row


def markdown(value: Any) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("`", "\\`")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def validate_contract(root: Path) -> dict[str, Any]:
    contract = read_json(
        safe_path(root, CONTRACT_REL), "GRAMMAR_REFERENCE_CONTRACT_JSON"
    )
    if not isinstance(contract, dict) or contract.get("schema") != SCHEMA:
        raise GeneratorError("GRAMMAR_REFERENCE_CONTRACT", "schema")
    if contract.get("reference_root") != "docs/grammar-reference":
        raise GeneratorError("GRAMMAR_REFERENCE_CONTRACT", "reference root")
    authority = contract.get("authority", {})
    if (
        authority.get("kind") != "CANONICAL_DOCUMENTATION_PROJECTION"
        or authority.get("semantic_authority") is not False
        or authority.get("product_support") != "NOT_RUN"
    ):
        raise GeneratorError("GRAMMAR_REFERENCE_AUTHORITY_FENCE", repr(authority))
    if (
        contract.get("manual_status_marker")
        != "CURRENT_CANONICAL_DOCUMENTATION_PROJECTION"
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_DOCUMENT_STATUS",
            repr(contract.get("manual_status_marker")),
        )
    if set(contract.get("allowed_status_fences", [])) != EXPECTED_FENCES:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_STATUS_FENCE",
            repr(contract.get("allowed_status_fences")),
        )
    if contract.get("preview_documentation_policy") != EXPECTED_PREVIEW_POLICY:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_POLICY",
            repr(contract.get("preview_documentation_policy")),
        )
    if contract.get("manual_quality_policy") != EXPECTED_MANUAL_QUALITY_POLICY:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_MANUAL_QUALITY_POLICY",
            repr(contract.get("manual_quality_policy")),
        )
    if contract.get("governance") != EXPECTED_GOVERNANCE:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_CONTRACT",
            repr(contract.get("governance")),
        )
    safe_path(root, contract["governance"]["source_path"])
    if contract.get("coverage_targets") != EXPECTED_COUNTS:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_TARGET",
            repr(contract.get("coverage_targets")),
        )
    grammar = contract.get("grammar", {})
    if (
        grammar.get("expected_total") != EXPECTED_COUNTS["grammar_productions"]
        or grammar.get("expected_profile_counts") != EXPECTED_PROFILES
    ):
        raise GeneratorError("GRAMMAR_REFERENCE_GRAMMAR_TARGET", repr(grammar))

    documents = contract.get("manual_documents", [])
    expected_ids = ["landing", *(f"{index:02d}" for index in range(16))]
    if (
        not isinstance(documents, list)
        or [row.get("id") for row in documents if isinstance(row, dict)]
        != expected_ids
    ):
        raise GeneratorError("GRAMMAR_REFERENCE_CHAPTER_ORDER", repr(documents))
    paths = [row.get("path") for row in documents]
    if (
        any(not isinstance(path, str) for path in paths)
        or len(paths) != len(set(paths))
        or len(paths) != len({path.casefold() for path in paths})
    ):
        raise GeneratorError("GRAMMAR_REFERENCE_CHAPTER_PATHS", repr(paths))
    for path in paths:
        if not path.startswith("docs/grammar-reference/") or not path.endswith(".md"):
            raise GeneratorError("GRAMMAR_REFERENCE_CHAPTER_PATHS", path)
    if EXPECTED_PREVIEW_POLICY["chapter_path"] not in paths:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_POLICY",
            EXPECTED_PREVIEW_POLICY["chapter_path"],
        )

    bindings = contract.get("source_bindings", [])
    binding_ids = [row.get("id") for row in bindings if isinstance(row, dict)]
    binding_paths = [row.get("path") for row in bindings if isinstance(row, dict)]
    if (
        not binding_ids
        or len(binding_ids) != len(set(binding_ids))
        or len(binding_paths) != len(set(binding_paths))
    ):
        raise GeneratorError("GRAMMAR_REFERENCE_SOURCE_BINDINGS", repr(bindings))
    for path in binding_paths:
        safe_path(root, path)
    coverage_schema_rows = [
        row
        for row in bindings
        if isinstance(row, dict) and row.get("id") == "coverage_schema"
    ]
    if coverage_schema_rows != [
        {
            "id": "coverage_schema",
            "path": EXPECTED_COVERAGE_SCHEMA_PATH,
        }
    ]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_BINDING",
            repr(coverage_schema_rows),
        )
    validate_coverage_schema(root, contract)

    output_paths = contract.get("generated_outputs", [])
    if (
        not isinstance(output_paths, list)
        or MANIFEST_REL not in output_paths
        or len(output_paths) != 8
        or len(output_paths) != len(set(output_paths))
        or len(output_paths) != len({path.casefold() for path in output_paths})
    ):
        raise GeneratorError("GRAMMAR_REFERENCE_OUTPUT_SET", repr(output_paths))
    for path in output_paths:
        if not isinstance(path, str) or not path.startswith(
            "docs/grammar-reference/"
        ):
            raise GeneratorError("GRAMMAR_REFERENCE_OUTPUT_SET", repr(path))
        safe_path(root, path, must_exist=False)
    reference_root = safe_path(root, contract["reference_root"])
    stale_generated = []
    banner = GENERATED_BANNER.rstrip("\n")
    for candidate in sorted(reference_root.rglob("*")):
        relative = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            raise GeneratorError(
                "GRAMMAR_REFERENCE_PATH_SYMLINK",
                relative,
            )
        if (
            candidate.is_file()
            and candidate.read_text(encoding="utf-8").startswith(banner)
            and relative not in output_paths
        ):
            stale_generated.append(relative)
    if stale_generated:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_STALE_GENERATED_OUTPUT",
            repr(stale_generated),
        )
    return contract


def validate_coverage_schema(
    root: Path, contract: dict[str, Any]
) -> None:
    schema = read_json(
        safe_path(root, EXPECTED_COVERAGE_SCHEMA_PATH),
        "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_JSON",
    )
    if (
        not isinstance(schema, dict)
        or schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("type") != "object"
        or schema.get("additionalProperties") is not False
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
            "root",
        )
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
            "properties",
        )
    if properties.get("schema", {}).get("const") != MANIFEST_SCHEMA:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
            "manifest schema",
        )
    if properties.get("revision", {}).get("const") != contract["revision"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
            "revision",
        )
    registry_properties = (
        properties.get("registries", {}).get("properties", {})
    )
    if not isinstance(registry_properties, dict):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
            "registries",
        )
    for name, definition in contract["registries"].items():
        expected = definition["expected_count"]
        row_schema = registry_properties.get(name)
        try:
            exact = row_schema["allOf"][1]["properties"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
                f"{name}:exact binding",
            ) from exc
        if (
            exact.get("row_count", {}).get("const") != expected
            or exact.get("unique_id_count", {}).get("const") != expected
        ):
            raise GeneratorError(
                "GRAMMAR_REFERENCE_COVERAGE_SCHEMA_CONTRACT",
                f"{name}:expected={expected}",
            )


def strip_ebnf_comments(text: str) -> str:
    """Blank nested EBNF comments while preserving offsets and newlines."""

    output = list(text)
    depth = 0
    quote = False
    escaped = False
    index = 0
    while index < len(text):
        pair = text[index : index + 2]
        char = text[index]
        if depth:
            if pair == "(*":
                output[index] = output[index + 1] = " "
                depth += 1
                index += 2
                continue
            if pair == "*)":
                output[index] = output[index + 1] = " "
                depth -= 1
                index += 2
                continue
            if char not in "\r\n":
                output[index] = " "
            index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
            index += 1
            continue
        if char == '"':
            quote = True
            index += 1
            continue
        if pair == "(*":
            output[index] = output[index + 1] = " "
            depth = 1
            index += 2
            continue
        if pair == "*)":
            raise GeneratorError(
                "GRAMMAR_REFERENCE_EBNF_COMMENT", f"unmatched closer at {index}"
            )
        index += 1
    if depth:
        raise GeneratorError("GRAMMAR_REFERENCE_EBNF_COMMENT", "unterminated comment")
    if quote:
        raise GeneratorError("GRAMMAR_REFERENCE_EBNF_STRING", "unterminated string")
    return "".join(output)


def has_unquoted_terminator(text: str) -> bool:
    quote = False
    escaped = False
    for char in text:
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = False
            continue
        if char == '"':
            quote = True
        elif char == ";":
            return True
    return False


def parse_grammar(
    grammar_text: str, frontend: dict[str, Any], contract: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    markers = [
        (match.start(), match.group(1))
        for match in PROFILE_MARKER_RE.finditer(grammar_text)
    ]
    if not markers:
        raise GeneratorError("GRAMMAR_REFERENCE_PROFILE_MARKERS", "none")
    marker_offsets = [row[0] for row in markers]
    stripped = strip_ebnf_comments(grammar_text)
    productions: list[dict[str, Any]] = []
    names: list[str] = []
    unknown_profiles = 0
    matches = list(PRODUCTION_RE.finditer(stripped))
    for match_index, match in enumerate(matches):
        next_start = (
            matches[match_index + 1].start()
            if match_index + 1 < len(matches)
            else len(stripped)
        )
        if not has_unquoted_terminator(stripped[match.end() : next_start]):
            raise GeneratorError(
                "GRAMMAR_REFERENCE_EBNF_TERMINATOR",
                f"{match.group(1)} at line "
                f"{grammar_text.count(chr(10), 0, match.start()) + 1}",
            )
        marker_index = bisect.bisect_right(marker_offsets, match.start()) - 1
        if marker_index < 0:
            profile = "UNKNOWN"
            unknown_profiles += 1
        else:
            profile = markers[marker_index][1]
        name = match.group(1)
        names.append(name)
        productions.append(
            {
                "name": name,
                "profile": profile,
                "line": grammar_text.count("\n", 0, match.start()) + 1,
            }
        )
    duplicate_names = sorted(
        name for name, count in Counter(names).items() if count != 1
    )
    if duplicate_names:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_DUPLICATE_PRODUCTION", repr(duplicate_names)
        )
    if unknown_profiles:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_UNKNOWN_PROFILE", str(unknown_profiles)
        )
    counts = dict(Counter(row["profile"] for row in productions))
    expected = contract["grammar"]["expected_profile_counts"]
    if counts != expected or len(productions) != contract["grammar"]["expected_total"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GRAMMAR_COUNT",
            f"profiles={counts} total={len(productions)}",
        )
    declared = frontend.get("grammar_profile_counts")
    if declared != counts:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_FRONTEND_PROFILE_PARITY",
            f"declared={declared} observed={counts}",
        )
    return productions, counts


def validate_manual_documents(
    root: Path, contract: dict[str, Any]
) -> list[dict[str, Any]]:
    expected_marker = contract["manual_status_marker"]
    allowed_fences = set(contract["allowed_status_fences"])
    preview_policy = contract["preview_documentation_policy"]
    rows: list[dict[str, Any]] = []
    for document in contract["manual_documents"]:
        path = safe_path(root, document["path"])
        if not path.is_file():
            raise GeneratorError(
                "GRAMMAR_REFERENCE_MISSING_CHAPTER", document["path"]
            )
        text = path.read_text(encoding="utf-8")
        markers = DOCUMENT_STATUS_RE.findall(text)
        if markers != [expected_marker]:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_DOCUMENT_STATUS",
                f"{document['path']}:{markers}",
            )
        fences = STATUS_FENCE_RE.findall(text)
        unknown = sorted(set(fences) - allowed_fences)
        if unknown:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_UNKNOWN_STATUS_FENCE",
                f"{document['path']}:{unknown}",
            )
        if document["path"] == preview_policy["chapter_path"]:
            missing_fences = sorted(
                set(preview_policy["required_status_fences"]) - set(fences)
            )
            if missing_fences:
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_PREVIEW_STATUS_FENCE",
                    f"{document['path']}:{missing_fences}",
                )
            disclaimer = preview_policy["activation_disclaimer"]
            if text.count(disclaimer) != 1:
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_PREVIEW_ACTIVATION_DISCLAIMER",
                    f"{document['path']}:count={text.count(disclaimer)}",
                )
        rows.append(
            {
                **document,
                "status_marker": expected_marker,
                **{
                    key: value
                    for key, value in file_binding(path, root).items()
                    if key in {"bytes", "sha256"}
                },
            }
        )
    return rows


def extract_marked_json(
    text: str,
    begin_marker: str,
    end_marker: str,
    code: str,
) -> tuple[Any, int, int]:
    if text.count(begin_marker) != 1 or text.count(end_marker) != 1:
        raise GeneratorError(
            code,
            f"begin={text.count(begin_marker)} end={text.count(end_marker)}",
        )
    begin = text.index(begin_marker)
    end = text.index(end_marker)
    if begin >= end:
        raise GeneratorError(code, "marker order")
    payload_start = begin + len(begin_marker)
    payload = text[payload_start:end].strip()
    match = re.fullmatch(r"```json[ \t]*\n(.*)\n```", payload, re.DOTALL)
    if match is None:
        raise GeneratorError(code, "expected one fenced JSON value")
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise GeneratorError(code, str(exc)) from exc
    return value, begin, end + len(end_marker)


def status_fence_segments(text: str) -> list[dict[str, Any]]:
    matches = list(STATUS_FENCE_RE.finditer(text))
    return [
        {
            "status": match.group(1),
            "marker_start": match.start(),
            "start": match.end(),
            "end": (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            ),
        }
        for index, match in enumerate(matches)
    ]


def status_at_offset(text: str, offset: int) -> str | None:
    status: str | None = None
    for match in STATUS_FENCE_RE.finditer(text):
        if match.start() > offset:
            break
        status = match.group(1)
    return status


def registry_example_status(
    row: dict[str, Any],
    feature_status_by_id: dict[str, str],
) -> str:
    source_root = row.get("source_root")
    if (
        row.get("source_activation") == "explicit_feature_gate"
        or row.get("expected_outcome") == "accept_with_gate"
        or (
            isinstance(source_root, str)
            and source_root.startswith("Preview")
        )
    ):
        return "PREVIEW_GATED"
    feature_ids = row.get("feature_ids")
    if not isinstance(feature_ids, list) or any(
        not isinstance(identifier, str) for identifier in feature_ids
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_EXAMPLE_FEATURE_REFERENCE",
            str(row.get("example_id")),
        )
    unknown = sorted(set(feature_ids) - set(feature_status_by_id))
    if unknown:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_EXAMPLE_FEATURE_REFERENCE",
            f"{row.get('example_id')}:{unknown}",
        )
    noncurrent_statuses = {
        {
            "PREVIEW": "PREVIEW_GATED",
            "PREVIEW_DESIGN": "PREVIEW_NONACTIVATABLE",
            "RECOVERY": "RECOVERY_ONLY",
            "RECOVERY_ONLY": "RECOVERY_ONLY",
            "REMOVED": "REMOVED",
        }[feature_status_by_id[identifier]]
        for identifier in feature_ids
        if feature_status_by_id[identifier]
        in {
            "PREVIEW",
            "PREVIEW_DESIGN",
            "RECOVERY",
            "RECOVERY_ONLY",
            "REMOVED",
        }
    }
    if len(noncurrent_statuses) > 1:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_EXAMPLE_STATUS_CONFLICT",
            f"{row.get('example_id')}:{sorted(noncurrent_statuses)}",
        )
    if noncurrent_statuses:
        return next(iter(noncurrent_statuses))
    return "CURRENT"


def validate_preview_registry_documentation(
    root: Path,
    contract: dict[str, Any],
    features: list[dict[str, Any]],
) -> dict[str, Any]:
    policy = contract["preview_documentation_policy"]
    text = safe_path(root, policy["chapter_path"]).read_text(encoding="utf-8")
    segments = status_fence_segments(text)
    if not segments or segments[0]["status"] != "CURRENT":
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_STATUS_FENCE",
            "chapter must begin its classified content with CURRENT",
        )

    feature_ids_by_status: dict[str, list[str]] = {}
    for status, expected_count in policy[
        "required_registry_status_counts"
    ].items():
        feature_ids = sorted(
            row["feature_id"]
            for row in features
            if row.get("status_enum") == status
        )
        feature_ids_by_status[status] = feature_ids
        if len(feature_ids) != expected_count:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_PREVIEW_REGISTRY_COUNT",
                f"{status}:expected={expected_count}:observed={len(feature_ids)}",
            )

    status_projection = {
        status: "\n".join(
            text[segment["start"] : segment["end"]]
            for segment in segments
            if segment["status"] == status
        )
        for status in ("PREVIEW_GATED", "PREVIEW_NONACTIVATABLE")
    }
    for registry_status, fence_status in (
        ("PREVIEW", "PREVIEW_GATED"),
        ("PREVIEW_DESIGN", "PREVIEW_NONACTIVATABLE"),
    ):
        missing = [
            feature_id
            for feature_id in feature_ids_by_status[registry_status]
            if f"`{feature_id}`" not in status_projection[fence_status]
        ]
        if missing:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_PREVIEW_REGISTRY_COVERAGE",
                f"{registry_status}:{fence_status}:{','.join(missing)}",
            )

    cards, cards_begin, cards_end = extract_marked_json(
        text,
        policy["review_card_begin_marker"],
        policy["review_card_end_marker"],
        "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARDS",
    )
    if status_at_offset(text, cards_begin) != "PREVIEW_NONACTIVATABLE":
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_FENCE",
            repr(status_at_offset(text, cards_begin)),
        )
    if (
        not isinstance(cards, list)
        or len(cards) != policy["required_review_card_count"]
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_COUNT",
            f"expected={policy['required_review_card_count']} "
            f"observed={len(cards) if isinstance(cards, list) else None}",
        )
    expected_keys = {"feature_id", *policy["review_card_fields"]}
    identifiers: list[str] = []
    for index, card in enumerate(cards):
        if not isinstance(card, dict) or set(card) != expected_keys:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_FIELDS",
                f"index={index}:keys={sorted(card) if isinstance(card, dict) else None}",
            )
        for field in expected_keys:
            value = card.get(field)
            if not isinstance(value, str) or not value.strip():
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_FIELDS",
                    f"index={index}:field={field}",
                )
        identifiers.append(card["feature_id"])
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count != 1
    )
    expected_identifiers = feature_ids_by_status["PREVIEW_DESIGN"]
    if duplicates or sorted(identifiers) != expected_identifiers:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_IDS",
            f"duplicates={duplicates} "
            f"missing={sorted(set(expected_identifiers) - set(identifiers))} "
            f"extra={sorted(set(identifiers) - set(expected_identifiers))}",
        )
    if cards_end > next(
        segment["end"]
        for segment in segments
        if segment["start"] <= cards_begin < segment["end"]
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_PREVIEW_REVIEW_CARD_FENCE",
            "review card block crosses a status fence",
        )
    return {
        "preview_gated_feature_count": len(feature_ids_by_status["PREVIEW"]),
        "preview_design_feature_count": len(
            feature_ids_by_status["PREVIEW_DESIGN"]
        ),
        "preview_review_card_count": len(cards),
        "preview_review_card_field_violation_count": 0,
        "status_fence_scope": policy["status_fence_scope"],
        "status_fence_violation_count": 0,
    }


def validate_governance(
    root: Path, contract: dict[str, Any]
) -> dict[str, Any]:
    governance = contract["governance"]
    pointer = read_json(
        safe_path(root, governance["source_path"]),
        "GRAMMAR_REFERENCE_GOVERNANCE_SOURCE",
    )
    if not isinstance(pointer, dict):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_SOURCE", "expected object"
        )
    open_actions = pointer.get("open_actions")
    if not isinstance(open_actions, list) or any(
        not isinstance(row, dict) for row in open_actions
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_SOURCE", "open_actions"
        )
    action_ids = [row.get("id") for row in open_actions]
    expected_action_ids = [
        *governance["separate_open_action_ids"],
        *governance["feature_p1_ids"],
    ]
    if any(not isinstance(identifier, str) for identifier in action_ids):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_ACTION_SET",
            f"observed={action_ids}",
        )
    duplicate_action_ids = sorted(
        identifier
        for identifier, count in Counter(action_ids).items()
        if count != 1
    )
    if (
        duplicate_action_ids
        or action_ids != expected_action_ids
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_ACTION_SET",
            f"observed={action_ids}:duplicates={duplicate_action_ids}",
        )
    if pointer.get("spec_revision") != contract["revision"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_REVISION_PARITY",
            f"contract={contract['revision']}:"
            f"pointer={pointer.get('spec_revision')}",
        )
    observed_semantic_p0 = sum(
        row.get("priority") == "P0" for row in open_actions
    )
    if observed_semantic_p0 != governance["semantic_p0"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_P0_SOURCE",
            f"observed={observed_semantic_p0}",
        )
    observed_feature_p1 = [
        identifier
        for identifier in action_ids
        if isinstance(identifier, str)
        and re.fullmatch(r"(?:CE-C|CE-E|TCC|SFD)-P1-[0-9]{3}", identifier)
    ]
    observed_m13 = [
        identifier
        for identifier in action_ids
        if isinstance(identifier, str) and identifier.startswith("M13-A")
    ]
    if observed_feature_p1 != governance["feature_p1_ids"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_P1_SOURCE",
            f"observed={observed_feature_p1}",
        )
    feature_p1_ids = set(governance["feature_p1_ids"])
    non_p1 = sorted(
        row["id"]
        for row in open_actions
        if row["id"] in feature_p1_ids and row.get("priority") != "P1"
    )
    if non_p1:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_P1_PRIORITY",
            repr(non_p1),
        )
    if observed_m13 != governance["separate_open_action_ids"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_M13_SOURCE",
            f"observed={observed_m13}",
        )
    expected_lanes = {
        lane: governance["product_lane_status"]
        for lane in governance["product_lane_ids"]
    }
    if pointer.get("product_lanes") != expected_lanes:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_PRODUCT_LANES_SOURCE",
            repr(pointer.get("product_lanes")),
        )

    chapter_path = safe_path(root, governance["chapter_path"])
    chapter_text = chapter_path.read_text(encoding="utf-8")
    chapter_value, _begin, _end = extract_marked_json(
        chapter_text,
        governance["chapter_begin_marker"],
        governance["chapter_end_marker"],
        "GRAMMAR_REFERENCE_GOVERNANCE_CHAPTER_BLOCK",
    )
    expected_chapter_value = {
        "semantic_p0": governance["semantic_p0"],
        "feature_p1_status": governance["feature_p1_status"],
        "feature_p1_ids": governance["feature_p1_ids"],
        "separate_action_status": governance["separate_action_status"],
        "separate_open_action_ids": governance["separate_open_action_ids"],
        "product_lanes": expected_lanes,
    }
    if chapter_value != expected_chapter_value:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_CHAPTER_BLOCK",
            repr(chapter_value),
        )

    p1_rows = re.findall(
        r"(?m)^\|\s*`((?:CE-C|CE-E|TCC|SFD)-P1-[0-9]{3})`\s*"
        r"\|\s*`OPEN`\s*\|",
        chapter_text,
    )
    m13_rows = re.findall(
        r"(?m)^\|\s*`(M13-A[0-9]{3})`\s*\|\s*`OPEN`\s*\|",
        chapter_text,
    )
    if p1_rows != governance["feature_p1_ids"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_P1_LEDGER",
            repr(p1_rows),
        )
    if m13_rows != governance["separate_open_action_ids"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_GOVERNANCE_M13_LEDGER",
            repr(m13_rows),
        )
    return {
        "source_path": governance["source_path"],
        "semantic_p0": observed_semantic_p0,
        "feature_p1_status": governance["feature_p1_status"],
        "feature_p1_ids": governance["feature_p1_ids"],
        "separate_action_status": governance["separate_action_status"],
        "separate_open_action_ids": governance["separate_open_action_ids"],
        "product_lanes": expected_lanes,
    }


def validate_manual_quality(
    root: Path,
    contract: dict[str, Any],
    examples: list[dict[str, Any]],
    features: list[dict[str, Any]],
) -> dict[str, Any]:
    documents = contract["manual_documents"]
    policy = contract["manual_quality_policy"]
    texts = {
        document["path"]: safe_path(root, document["path"]).read_text(
            encoding="utf-8"
        )
        for document in documents
    }

    forbidden_count = 0
    for text in texts.values():
        folded = text.casefold()
        forbidden_count += sum(
            folded.count(token.casefold())
            for token in policy["forbidden_path_tokens"]
        )
    if forbidden_count:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_FORBIDDEN_PATH_TOKEN",
            f"count={forbidden_count}",
        )

    planned_outputs = set(contract["generated_outputs"])
    manual_link_count = 0
    generated_link_count = 0
    invalid_links: list[str] = []
    for document_path, text in texts.items():
        document_parent = Path(document_path).parent
        for match in MARKDOWN_LINK_RE.finditer(text):
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
            manual_link_count += 1
            candidate = (root / document_parent / target).resolve()
            try:
                candidate_rel = candidate.relative_to(root).as_posix()
            except ValueError:
                invalid_links.append(f"{document_path}:{target}:escape")
                continue
            if candidate_rel in planned_outputs or any(
                output.startswith(candidate_rel.rstrip("/") + "/")
                for output in planned_outputs
            ):
                generated_link_count += 1
                continue
            if candidate.exists():
                continue
            invalid_links.append(f"{document_path}:{target}")
    if invalid_links:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_MANUAL_LINK",
            ",".join(invalid_links),
        )

    example_by_id = {row["example_id"]: row for row in examples}
    feature_status_by_id = {
        row["feature_id"]: row["status_enum"] for row in features
    }
    hash_to_ids: dict[str, list[str]] = {}
    for row in examples:
        code_hash = row.get("code_sha256")
        if isinstance(code_hash, str):
            hash_to_ids.setdefault(code_hash, []).append(row["example_id"])
    all_references: list[str] = []
    registry_bound_blocks = 0
    illustrative_blocks = 0
    deeplus_blocks = 0
    allowed_illustrative = set(policy["allowed_illustrative_statuses"])
    for document_path, text in texts.items():
        references = EXAMPLE_REF_RE.findall(text)
        all_references.extend(references)
        unknown = sorted(set(references) - set(example_by_id))
        if unknown:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_UNKNOWN_EXAMPLE_REFERENCE",
                f"{document_path}:{','.join(unknown)}",
            )
        headings = list(HEADING_RE.finditer(text))
        for block in DEEPLUS_BLOCK_RE.finditer(text):
            deeplus_blocks += 1
            code = block.group(1)
            if code.endswith("\n"):
                code = code[:-1]
            if re.search(r"(?m)^type[ \t]+[A-Za-z_]", code):
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_EXAMPLE_TOP_LEVEL_VISIBILITY",
                    f"{document_path}:line="
                    f"{text.count(chr(10), 0, block.start()) + 1}",
                )
            code_hash = sha256_bytes(code.encode("utf-8"))
            matching_ids = set(hash_to_ids.get(code_hash, []))
            if matching_ids:
                section_start = 0
                for heading in headings:
                    if heading.start() >= block.start():
                        break
                    section_start = heading.start()
                section_ids = set(
                    EXAMPLE_REF_RE.findall(text[section_start : block.start()])
                )
                bound_ids = sorted(matching_ids & section_ids)
                if not bound_ids:
                    raise GeneratorError(
                        "GRAMMAR_REFERENCE_EXAMPLE_PROVENANCE",
                        f"{document_path}:line="
                        f"{text.count(chr(10), 0, block.start()) + 1}:"
                        f"hash_ids={sorted(matching_ids)}:"
                        f"section_ids={sorted(section_ids)}",
                    )
                active_status = (
                    status_at_offset(text, block.start()) or "CURRENT"
                )
                expected_statuses = {
                    registry_example_status(
                        example_by_id[identifier],
                        feature_status_by_id,
                    )
                    for identifier in bound_ids
                }
                if (
                    len(expected_statuses) != 1
                    or active_status not in expected_statuses
                ):
                    raise GeneratorError(
                        "GRAMMAR_REFERENCE_EXAMPLE_STATUS_FENCE",
                        f"{document_path}:registry_ids={bound_ids}:"
                        f"expected={sorted(expected_statuses)}:"
                        f"active={active_status}",
                    )
                registry_bound_blocks += 1
                continue

            lookback = text[max(0, block.start() - 700) : block.start()]
            illustrative = list(ILLUSTRATIVE_EXAMPLE_RE.finditer(lookback))
            if (
                not illustrative
                or lookback[illustrative[-1].end() :].strip()
            ):
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_EXAMPLE_BINDING",
                    f"{document_path}:line="
                    f"{text.count(chr(10), 0, block.start()) + 1}",
                )
            status, authority_source = illustrative[-1].groups()
            if status not in allowed_illustrative:
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_EXAMPLE_MARKER",
                    f"{document_path}:{status}",
                )
            safe_path(root, authority_source)
            active_status = status_at_offset(text, block.start()) or "CURRENT"
            expected_status = ILLUSTRATIVE_STATUS_FENCES[status]
            if active_status != expected_status:
                raise GeneratorError(
                    "GRAMMAR_REFERENCE_EXAMPLE_STATUS_FENCE",
                    f"{document_path}:{status}:"
                    f"expected={expected_status}:active={active_status}",
                )
            illustrative_blocks += 1

    return {
        "forbidden_path_token_count": forbidden_count,
        "manual_internal_link_count": manual_link_count,
        "planned_generated_internal_link_count": generated_link_count,
        "invalid_internal_link_count": 0,
        "referenced_example_id_count": len(set(all_references)),
        "unknown_example_reference_count": 0,
        "deeplus_example_block_count": deeplus_blocks,
        "registry_bound_example_block_count": registry_bound_blocks,
        "illustrative_example_block_count": illustrative_blocks,
        "example_binding_violation_count": 0,
    }


def directory_binding(root: Path, relative: str) -> str:
    directory = safe_path(root, relative)
    if not directory.is_dir():
        raise GeneratorError("GRAMMAR_REFERENCE_REGISTRY_ROOT", relative)
    rows = []
    for path in sorted(directory.glob("*.json")):
        if path.is_symlink() or not path.is_file():
            raise GeneratorError(
                "GRAMMAR_REFERENCE_REGISTRY_MEMBER", str(path)
            )
        data = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    if not rows:
        raise GeneratorError("GRAMMAR_REFERENCE_REGISTRY_ROOT", relative)
    return canonical_sha(rows)


def load_registry(
    root: Path, name: str, definition: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata_path = safe_path(root, definition["metadata_path"])
    metadata = read_json(metadata_path, "GRAMMAR_REFERENCE_REGISTRY_METADATA")
    chunks_root = safe_path(root, definition["chunks_root"])
    if not chunks_root.is_dir():
        raise GeneratorError(
            "GRAMMAR_REFERENCE_REGISTRY_ROOT", definition["chunks_root"]
        )
    rows: list[dict[str, Any]] = []
    for candidate in sorted(chunks_root.glob("*.json")):
        relative = candidate.relative_to(root).as_posix()
        path = safe_path(root, relative)
        if path.is_symlink() or not path.is_file():
            raise GeneratorError(
                "GRAMMAR_REFERENCE_REGISTRY_MEMBER",
                relative,
            )
        value = read_json(path, "GRAMMAR_REFERENCE_REGISTRY_CHUNK")
        if not isinstance(value, list) or any(
            not isinstance(row, dict) for row in value
        ):
            raise GeneratorError(
                "GRAMMAR_REFERENCE_REGISTRY_CHUNK", str(path)
            )
        rows.extend(value)
    count = definition["expected_count"]
    declared = metadata.get(definition["count_field"])
    if declared != count or len(rows) != count:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_REGISTRY_COUNT",
            f"{name}: declared={declared} observed={len(rows)} expected={count}",
        )
    id_field = definition["id_field"]
    identifiers = [row.get(id_field) for row in rows]
    if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
        raise GeneratorError("GRAMMAR_REFERENCE_REGISTRY_ID", name)
    duplicate = sorted(
        identifier
        for identifier, item_count in Counter(identifiers).items()
        if item_count != 1
    )
    casefold_duplicate = sorted(
        identifier
        for identifier, item_count in Counter(
            identifier.casefold() for identifier in identifiers
        ).items()
        if item_count != 1
    )
    if duplicate or casefold_duplicate:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_REGISTRY_DUPLICATE",
            f"{name}: exact={duplicate} casefold={casefold_duplicate}",
        )
    rows.sort(key=lambda row: row[id_field])
    digest_material = [
        file_binding(metadata_path, root),
        {
            "path": definition["chunks_root"],
            "bytes": sum(
                path.stat().st_size for path in sorted(chunks_root.glob("*.json"))
            ),
            "sha256": directory_binding(root, definition["chunks_root"]),
        },
    ]
    binding = {
        "metadata_path": definition["metadata_path"],
        "chunks_root": definition["chunks_root"],
        "row_count": len(rows),
        "unique_id_count": len(set(identifiers)),
        "duplicate_id_count": 0,
        "sha256": canonical_sha(digest_material),
    }
    return rows, binding


def render_summary(contract: dict[str, Any]) -> bytes:
    lines = [
        GENERATED_BANNER.rstrip(),
        "# Deeplus 문법 명세 및 참조서",
        "",
        "이 탐색 문서는 검토된 문법 참조서 계약에서 결정론적으로 생성됩니다.",
        "",
        "## 본문 참조서",
        "",
    ]
    for document in contract["manual_documents"]:
        relative = Path(document["path"]).relative_to(contract["reference_root"])
        lines.append(f"- [{document['id']} — {document['title']}]({relative.as_posix()})")
    lines.extend(
        [
            "",
            "## 생성된 부록",
            "",
            "- [A — 정확한 production 색인](appendices/a-production-index.md)",
            "- [B — 토큰, 키워드 및 연산자](appendices/b-token-keyword-operator-index.md)",
            "- [C — 기능 및 상태 색인](appendices/c-feature-status-index.md)",
            "- [D — 진단 및 술어](appendices/d-diagnostic-predicate-index.md)",
            "- [E — Prelude 및 예제](appendices/e-prelude-example-index.md)",
            "- [F — 커버리지 보고서](appendices/f-coverage-report.md)",
            "- [기계 판독형 커버리지 manifest](coverage-manifest.json)",
            "",
        ]
    )
    return ("\n".join(lines)).encode("utf-8")


def render_productions(productions: list[dict[str, Any]], grammar_path: str) -> bytes:
    lines = [
        GENERATED_BANNER.rstrip(),
        "# 부록 A — 정확한 문법 production 색인",
        "",
        f"권위 원천은 `{grammar_path}`입니다. 모든 production을 정확히 한 번씩 나열합니다.",
        "",
        "| 문법 production | 프로파일 | 원천 줄 |",
        "|---|---|---:|",
    ]
    lines.extend(
        f"| `{row['name']}` | `{row['profile']}` | {row['line']} |"
        for row in productions
    )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def token_spelling(value: Any) -> str:
    if isinstance(value, list):
        if value and all(isinstance(item, list) for item in value):
            return " / ".join(" ".join(map(str, item)) for item in value)
        return " ".join(map(str, value))
    return str(value or "")


def render_vocabulary(
    vocabulary: dict[str, Any],
    frontend: dict[str, Any],
    productions: list[dict[str, Any]],
) -> bytes:
    lexical_tokens = [
        row
        for row in productions
        if row["profile"] == "LEXICAL"
        and row["name"] == row["name"].upper()
    ]
    lines = [
        GENERATED_BANNER.rstrip(),
        "# 부록 B — 토큰, 키워드 및 연산자",
        "",
        "## 어휘 토큰 범주",
        "",
        "| 토큰/범주 | 문법 줄 |",
        "|---|---:|",
        *[
            f"| `{markdown(row['name'])}` | {row['line']} |"
            for row in lexical_tokens
        ],
        "",
        "## 하드 키워드",
        "",
        "| 단어 |",
        "|---|",
        *[f"| `{markdown(word)}` |" for word in vocabulary["hard_keywords"]],
        "",
        "## 문맥 단어",
        "",
        "| 단어 |",
        "|---|",
        *[f"| `{markdown(word)}` |" for word in vocabulary["contextual_words"]],
        "",
        "## Pratt 연산자 소유자",
        "",
        "| 도메인 | ID | 토큰 | 결합력 | 결합 방향 |",
        "|---|---|---|---|---|",
    ]
    pratt = frontend.get("pratt", {})
    for domain in sorted(pratt):
        value = pratt[domain]
        if not isinstance(value, dict):
            continue
        for row in value.get("operators", []):
            if not isinstance(row, dict):
                continue
            bp = (
                f"{row.get('lbp', '')}/{row.get('rbp', '')}"
                if "lbp" in row or "rbp" in row
                else ""
            )
            lines.append(
                f"| `{markdown(domain)}` | `{markdown(row.get('id'))}` | "
                f"`{markdown(token_spelling(row.get('tokens')))}` | "
                f"{markdown(bp)} | {markdown(row.get('assoc'))} |"
            )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def render_features(rows: list[dict[str, Any]]) -> bytes:
    lines = [
        GENERATED_BANNER.rstrip(),
        "# 부록 C — 기능 및 상태 색인",
        "",
        "| 기능 ID | 표시 이름 | 상태 | 활성화 | 권위 |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{markdown(row.get('feature_id'))}` | "
            f"{markdown(row.get('display_name'))} | "
            f"`{markdown(row.get('status_enum'))}` | "
            f"`{markdown(row.get('source_activation'))}` | "
            f"{markdown(row.get('authority'))} |"
        )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def render_diagnostics_predicates(
    diagnostics: list[dict[str, Any]], predicates: list[dict[str, Any]]
) -> bytes:
    lines = [
        GENERATED_BANNER.rstrip(),
        "# 부록 D — 진단 및 검사기 술어",
        "",
        "## 진단",
        "",
        "| 진단 ID | 단계 | 심각도 | 상태 | 메시지 |",
        "|---|---|---|---|---|",
    ]
    for row in diagnostics:
        lines.append(
            f"| `{markdown(row.get('diagnostic_id'))}` | "
            f"`{markdown(row.get('stage'))}` | "
            f"`{markdown(row.get('severity'))}` | "
            f"`{markdown(row.get('diagnostic_status'))}` | "
            f"{markdown(row.get('message'))} |"
        )
    lines.extend(
        [
            "",
            "## 검사기 술어",
            "",
            "| 술어 ID | 원천 이름 | 요약 | 증거 |",
            "|---|---|---|---|",
        ]
    )
    for row in predicates:
        lines.append(
            f"| `{markdown(row.get('predicate_id'))}` | "
            f"{markdown(row.get('source_name'))} | "
            f"{markdown(row.get('summary'))} | "
            f"`{markdown(row.get('evidence_status'))}` |"
        )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def render_prelude_examples(
    prelude: list[dict[str, Any]], examples: list[dict[str, Any]]
) -> bytes:
    lines = [
        GENERATED_BANNER.rstrip(),
        "# 부록 E — Prelude 및 예제 색인",
        "",
        "## Prelude",
        "",
        "| 항목 ID | 심볼 | 종류 | 상태 | 제품 지원 |",
        "|---|---|---|---|---|",
    ]
    for row in prelude:
        lines.append(
            f"| `{markdown(row.get('entry_id'))}` | "
            f"`{markdown(row.get('symbol'))}` | "
            f"`{markdown(row.get('kind'))}` | "
            f"`{markdown(row.get('status'))}` | "
            f"`{markdown(row.get('product_support'))}` |"
        )
    lines.extend(
        [
            "",
            "## 예제",
            "",
            "| 예제 ID | 제목 | 결과 | 원천 역할 | 증거 |",
            "|---|---|---|---|---|",
        ]
    )
    for row in examples:
        lines.append(
            f"| `{markdown(row.get('example_id'))}` | "
            f"{markdown(row.get('title'))} | "
            f"`{markdown(row.get('expected_outcome'))}` | "
            f"`{markdown(row.get('source_role'))}` | "
            f"`{markdown(row.get('certification_status'))}` |"
        )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def render_coverage_report(
    revision: str,
    targets: dict[str, int],
    observed: dict[str, int],
    profile_counts: dict[str, int],
    bindings: list[dict[str, Any]],
) -> bytes:
    lines = [
        GENERATED_BANNER.rstrip(),
        "# 부록 F — 커버리지 보고서",
        "",
        f"- 리비전: `{revision}`",
        "- 투영 상태: `CURRENT_CANONICAL_DOCUMENTATION_PROJECTION`",
        "- 의미론 권위: `false`",
        "- 제품 지원: `NOT_RUN`",
        "",
        "## 커버리지",
        "",
        "| 도메인 | 목표 | 관측 | 결과 |",
        "|---|---:|---:|---|",
    ]
    for key in targets:
        lines.append(
            f"| `{key}` | {targets[key]} | {observed[key]} | "
            f"`{'통과' if targets[key] == observed[key] else '실패'}` |"
        )
    lines.extend(
        [
            "",
            "## 문법 프로파일",
            "",
            "| 프로파일 | production 수 |",
            "|---|---:|",
            *[
                f"| `{profile}` | {profile_counts[profile]} |"
                for profile in ("LEXICAL", "STABLE", "PREVIEW", "RECOVERY")
            ],
            "",
            "## 결합된 의미론 원천",
            "",
            "| 도메인 | 경로 | SHA-256 |",
            "|---|---|---|",
        ]
    )
    lines.extend(
        f"| `{row['id']}` | `{row['path']}` | `{row['sha256']}` |"
        for row in bindings
    )
    lines.append("")
    return ("\n".join(lines)).encode("utf-8")


def render_outputs(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = root.resolve()
    contract = validate_contract(root)
    manual_documents = validate_manual_documents(root, contract)

    grammar_path = safe_path(root, contract["grammar"]["path"])
    grammar_text = grammar_path.read_text(encoding="utf-8")
    frontend_path = safe_path(root, contract["grammar"]["frontend_model_path"])
    frontend = read_json(frontend_path, "GRAMMAR_REFERENCE_FRONTEND_JSON")
    productions, profile_counts = parse_grammar(grammar_text, frontend, contract)

    vocabulary_path = safe_path(root, contract["vocabulary"]["path"])
    vocabulary = read_json(
        vocabulary_path, "GRAMMAR_REFERENCE_VOCABULARY_JSON"
    )
    hard = vocabulary.get(contract["vocabulary"]["hard_field"])
    contextual = vocabulary.get(contract["vocabulary"]["contextual_field"])
    if (
        not isinstance(hard, list)
        or not isinstance(contextual, list)
        or len(hard) != contract["vocabulary"]["expected_hard_count"]
        or len(contextual) != contract["vocabulary"]["expected_contextual_count"]
        or len(hard) != len(set(hard))
        or len(contextual) != len(set(contextual))
    ):
        raise GeneratorError(
            "GRAMMAR_REFERENCE_VOCABULARY_COUNT",
            f"hard={len(hard) if isinstance(hard, list) else None} "
            f"contextual={len(contextual) if isinstance(contextual, list) else None}",
        )

    registries: dict[str, list[dict[str, Any]]] = {}
    registry_bindings: dict[str, dict[str, Any]] = {}
    for name, definition in contract["registries"].items():
        rows, binding = load_registry(root, name, definition)
        registries[name] = rows
        registry_bindings[name] = binding
    preview_quality = validate_preview_registry_documentation(
        root, contract, registries["features"]
    )
    governance = validate_governance(root, contract)
    manual_quality = validate_manual_quality(
        root,
        contract,
        registries["examples"],
        registries["features"],
    )
    manual_quality.update(preview_quality)

    source_bindings = [
        file_binding(
            safe_path(root, row["path"]), root, binding_id=row["id"]
        )
        for row in contract["source_bindings"]
    ]
    observed = {
        "grammar_productions": len(productions),
        "features": len(registries["features"]),
        "diagnostics": len(registries["diagnostics"]),
        "predicates": len(registries["predicates"]),
        "prelude_entries": len(registries["prelude"]),
        "examples": len(registries["examples"]),
        "hard_keywords": len(hard),
        "contextual_words": len(contextual),
    }
    if observed != contract["coverage_targets"]:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_COVERAGE", f"observed={observed}"
        )

    outputs: dict[str, bytes] = {
        "docs/grammar-reference/SUMMARY.md": render_summary(contract),
        "docs/grammar-reference/appendices/a-production-index.md": render_productions(
            productions, contract["grammar"]["path"]
        ),
        "docs/grammar-reference/appendices/b-token-keyword-operator-index.md": render_vocabulary(
            vocabulary, frontend, productions
        ),
        "docs/grammar-reference/appendices/c-feature-status-index.md": render_features(
            registries["features"]
        ),
        "docs/grammar-reference/appendices/d-diagnostic-predicate-index.md": render_diagnostics_predicates(
            registries["diagnostics"], registries["predicates"]
        ),
        "docs/grammar-reference/appendices/e-prelude-example-index.md": render_prelude_examples(
            registries["prelude"], registries["examples"]
        ),
        "docs/grammar-reference/appendices/f-coverage-report.md": render_coverage_report(
            contract["revision"],
            contract["coverage_targets"],
            observed,
            profile_counts,
            source_bindings,
        ),
    }
    expected_nonmanifest = set(contract["generated_outputs"]) - {MANIFEST_REL}
    if set(outputs) != expected_nonmanifest:
        raise GeneratorError(
            "GRAMMAR_REFERENCE_OUTPUT_SET",
            f"rendered={sorted(outputs)} expected={sorted(expected_nonmanifest)}",
        )
    generated_bindings = []
    for relative in contract["generated_outputs"]:
        if relative == MANIFEST_REL:
            continue
        data = outputs[relative]
        generated_bindings.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "revision": contract["revision"],
        "reference_root": contract["reference_root"],
        "authority": {
            "kind": contract["authority"]["kind"],
            "semantic_authority": False,
            "conflict_order": contract["authority"]["conflict_order"],
        },
        "source_bindings": source_bindings,
        "manual_documents": manual_documents,
        "generated_outputs": generated_bindings,
        "grammar": {
            "path": contract["grammar"]["path"],
            "sha256": sha256_bytes(grammar_path.read_bytes()),
            "production_count": len(productions),
            "profile_counts": profile_counts,
            "duplicate_production_count": 0,
            "unknown_profile_count": 0,
        },
        "registries": registry_bindings,
        "governance": governance,
        "manual_quality": manual_quality,
        "vocabulary": {
            "path": contract["vocabulary"]["path"],
            "sha256": sha256_bytes(vocabulary_path.read_bytes()),
            "hard_keyword_count": len(hard),
            "contextual_word_count": len(contextual),
        },
        "coverage": {
            "targets": contract["coverage_targets"],
            "observed": observed,
            "uncovered_count": sum(
                max(contract["coverage_targets"][key] - observed[key], 0)
                for key in observed
            ),
            "unknown_reference_count": (
                manual_quality["invalid_internal_link_count"]
                + manual_quality["unknown_example_reference_count"]
                + manual_quality["example_binding_violation_count"]
            ),
            "status_fence_violations": manual_quality[
                "status_fence_violation_count"
            ],
        },
        "product_support": "NOT_RUN",
    }
    outputs[MANIFEST_REL] = json_bytes(manifest)
    return outputs, {
        "schema": "deeplus.grammar-reference-generator-receipt/r1",
        "revision": contract["revision"],
        "result": "PASS",
        "generated_outputs": len(outputs),
        "manual_documents": len(manual_documents),
        "grammar_profiles": profile_counts,
        "coverage": observed,
        "manual_quality": {
            "preview_review_cards": manual_quality[
                "preview_review_card_count"
            ],
            "registry_bound_examples": manual_quality[
                "registry_bound_example_block_count"
            ],
            "illustrative_examples": manual_quality[
                "illustrative_example_block_count"
            ],
            "invalid_internal_links": manual_quality[
                "invalid_internal_link_count"
            ],
        },
        "governance": {
            "semantic_p0": governance["semantic_p0"],
            "open_feature_p1": len(governance["feature_p1_ids"]),
            "open_separate_actions": len(
                governance["separate_open_action_ids"]
            ),
            "product_lanes_not_run": len(governance["product_lanes"]),
        },
        "product_support": "NOT_RUN",
    }


def write_outputs(root: Path, outputs: dict[str, bytes]) -> None:
    for relative, data in outputs.items():
        atomic_write(safe_path(root, relative, must_exist=False), data)


def check_outputs(root: Path, outputs: dict[str, bytes]) -> None:
    for relative, expected in outputs.items():
        path = safe_path(root, relative)
        if not path.is_file():
            raise GeneratorError("GRAMMAR_REFERENCE_GENERATED_DRIFT", relative)
        actual = path.read_bytes()
        if actual != expected:
            raise GeneratorError(
                "GRAMMAR_REFERENCE_GENERATED_DRIFT",
                f"{relative}: expected={sha256_bytes(expected)} "
                f"actual={sha256_bytes(actual)}",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        outputs, receipt = render_outputs(root)
        if args.write:
            write_outputs(root, outputs)
            receipt["mode"] = "write"
        else:
            check_outputs(root, outputs)
            receipt["mode"] = "check"
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
        return 0
    except GeneratorError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, UnicodeError, KeyError, TypeError, ValueError) as exc:
        print(f"GRAMMAR_REFERENCE_UNEXPECTED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
