#!/usr/bin/env python3
"""Validate and bind the Korean Deeplus tutorial projection.

The tutorial is educational documentation, not an independent semantic
authority. This tool derives its exact curriculum from SUMMARY.md, enforces a
minimum depth and status fence, validates local links, and writes deterministic
coverage artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


CONTRACT_REL = "spec/contracts/tutorial-r1.json"
SCHEMA_REL = "schemas/language/tutorial-coverage.schema.json"
MANIFEST_REL = "docs/tutorial/coverage-manifest.json"
REPORT_REL = "docs/tutorial/coverage-report.md"
MANIFEST_SCHEMA = "deeplus.tutorial-coverage/r1"
REVISION = "r51f3-current-frontend-readiness-r11-r19-r1"
POINTER_REL = "current/current-pointer.json"
SOURCE_BINDING_RELS = (
    "spec/language.md",
    "spec/grammar/deeplus.ebnf",
    "spec/frontend/frontend-model.json",
    "spec/types/type-system.md",
    "docs/grammar-reference/coverage-manifest.json",
    "library/prelude/signatures/catalog-metadata.json",
    "examples/guide/review-corpus.md",
    "docs/guide/example-host-adapters.md",
)
FEATURE_P1_IDS = (
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
)
SEPARATE_ACTION_IDS = (
    "M13-A002",
    "M13-A003",
    "M13-A004",
    "M13-A005",
)
PRODUCT_LANE_COUNT = 15
PRODUCT_LANE_STATUS = "NOT_RUN"
SUMMARY_LINK_RE = re.compile(
    r"(?<!!)\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)"
)
LOCAL_LINK_RE = re.compile(
    r"!?\[[^\]]*\]\(([^)#]+)(?:#[^)]+)?\)"
)
DEEPLUS_BLOCK_RE = re.compile(
    r"(?ms)^```deeplus[ \t]*\n.*?^```[ \t]*$"
)
FENCED_BLOCK_RE = re.compile(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$")
KOREAN_RE = re.compile(r"[가-힣]")
LEVEL2_RE = re.compile(r"(?m)^##[ \t]+")
EXERCISE_RE = re.compile(
    r"(?m)^[ \t]*\d+\.[ \t]+\*\*[^*\r\n]+:\*\*"
)
STATUS_RE = re.compile(
    r"(?m)^>[ \t]*(?:\*\*)?"
    r"(?:(?:문서|과정|부)[ \t]+)?상태:"
    r"(?:\*\*)?[ \t]*`([A-Z][A-Z0-9_]*)`"
)
PRODUCT_NOT_RUN_RE = re.compile(
    r"(?is)(?:product|제품).{0,160}\bNOT_RUN\b|"
    r"\bNOT_RUN\b.{0,160}(?:product|제품)"
)
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
PART_DIR_RE = re.compile(rf"part-(\d{{2}})-{SLUG}")
CONCEPT_FILE_RE = re.compile(rf"(\d{{2}})-(\d{{2}})-{SLUG}\.md")
LAB_FILE_RE = re.compile(rf"lab-(\d{{2}})-{SLUG}\.md")
CAPSTONE_FILE_RE = re.compile(rf"([a-d])-{SLUG}\.md")
APPENDIX_FILE_RE = re.compile(rf"([a-h])-{SLUG}\.md")


class TutorialError(RuntimeError):
    """A stable validation failure."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        Path(raw_temp).replace(path)
    finally:
        temp = Path(raw_temp)
        if temp.exists():
            temp.unlink()


def safe_relative(path_text: str) -> PurePosixPath:
    if not path_text or "\x00" in path_text:
        raise TutorialError(f"unsafe tutorial path: {path_text}")
    path = PurePosixPath(path_text.replace("\\", "/"))
    if (
        path.is_absolute()
        or ".." in path.parts
        or not path.parts
        or re.match(r"^[A-Za-z]:", path.parts[0])
        or any(ord(character) < 32 for character in path_text)
    ):
        raise TutorialError(f"unsafe tutorial path: {path_text}")
    return path


def checked_file_identity(root: Path, rel: str) -> dict[str, Any]:
    relative = safe_relative(rel)
    root = root.resolve()
    path = root.joinpath(*relative.parts)
    cursor = root
    for component in relative.parts:
        cursor /= component
        if cursor.is_symlink():
            raise TutorialError(
                f"tutorial source path must not contain a symlink: {rel}"
            )
    if not path.is_file():
        raise TutorialError(f"missing tutorial source binding: {rel}")
    data = path.read_bytes()
    return {
        "path": rel,
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def validate_authority_and_pointer(
    root: Path, contract: dict[str, Any]
) -> list[dict[str, Any]]:
    if contract.get("revision") != REVISION:
        raise TutorialError("tutorial revision does not match current revision")
    authority = contract.get("authority", {})
    if (
        authority.get("kind") != "CANONICAL_EDUCATIONAL_PROJECTION"
        or authority.get("semantic_authority") is not False
        or authority.get("product_support") != PRODUCT_LANE_STATUS
    ):
        raise TutorialError("tutorial authority boundary drift")

    governance = contract.get("governance", {})
    expected_governance_keys = {
        "semantic_p0",
        "feature_p1_status",
        "feature_p1_ids",
        "separate_open_action_ids",
        "product_lane_status",
        "product_lane_count",
    }
    if set(governance) != expected_governance_keys:
        raise TutorialError("tutorial governance shape drift")
    if (
        governance.get("semantic_p0") != 0
        or governance.get("feature_p1_status") != "OPEN"
        or governance.get("feature_p1_ids") != list(FEATURE_P1_IDS)
        or governance.get("separate_open_action_ids")
        != list(SEPARATE_ACTION_IDS)
        or governance.get("product_lane_status") != PRODUCT_LANE_STATUS
        or governance.get("product_lane_count") != PRODUCT_LANE_COUNT
    ):
        raise TutorialError("tutorial governance does not match exact current set")

    expected_bindings = contract.get("source_bindings")
    if (
        not isinstance(expected_bindings, list)
        or [row.get("path") for row in expected_bindings if isinstance(row, dict)]
        != list(SOURCE_BINDING_RELS)
        or any(
            not isinstance(row, dict)
            or set(row) != {"path", "sha256"}
            or not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))
            for row in expected_bindings
        )
    ):
        raise TutorialError("tutorial source binding contract shape drift")
    source_bindings = [
        checked_file_identity(root, relative)
        for relative in SOURCE_BINDING_RELS
    ]
    # Length equality is established by the contract-shape check above. Keep the
    # loop compatible with the repository's supported Python 3.9 validator host.
    for expected, actual in zip(expected_bindings, source_bindings):
        if expected["sha256"] != actual["sha256"]:
            raise TutorialError(
                f"tutorial source binding drift: {actual['path']}"
            )

    pointer_contract = contract.get("current_pointer_validation")
    if pointer_contract != {"path": POINTER_REL, "hash_binding": False}:
        raise TutorialError("current pointer must remain validation-only")
    pointer = read_json(root / POINTER_REL)
    if pointer.get("spec_revision") != REVISION:
        raise TutorialError("current pointer revision drift")
    actions = pointer.get("open_actions")
    if not isinstance(actions, list) or any(
        not isinstance(row, dict) for row in actions
    ):
        raise TutorialError("current pointer open action shape drift")
    action_ids = [row.get("id") for row in actions]
    expected_action_ids = [*SEPARATE_ACTION_IDS, *FEATURE_P1_IDS]
    if (
        len(action_ids) != len(set(action_ids))
        or set(action_ids) != set(expected_action_ids)
        or len(action_ids) != len(expected_action_ids)
        or any(row.get("priority") == "P0" for row in actions)
        or any(
            row.get("priority") != "P1"
            for row in actions
            if row.get("id") in FEATURE_P1_IDS
        )
    ):
        raise TutorialError("current pointer P0/P1/action set drift")
    lanes = pointer.get("product_lanes")
    if (
        not isinstance(lanes, dict)
        or len(lanes) != PRODUCT_LANE_COUNT
        or set(lanes.values()) != {PRODUCT_LANE_STATUS}
    ):
        raise TutorialError("current pointer product lane drift")
    return source_bindings


def classify(relative_to_tutorial: PurePosixPath) -> str:
    parts = relative_to_tutorial.parts
    if len(parts) != 2:
        raise TutorialError(
            "curriculum documents must be one level below tutorial root: "
            f"{relative_to_tutorial}"
        )
    name = relative_to_tutorial.name
    part_match = PART_DIR_RE.fullmatch(parts[0])
    if part_match:
        part_number = part_match.group(1)
        if name == "README.md":
            return "part_guide"
        lab_match = LAB_FILE_RE.fullmatch(name)
        if lab_match:
            if lab_match.group(1) != part_number:
                raise TutorialError(
                    f"lab number does not match Part: {relative_to_tutorial}"
                )
            return "guided_lab"
        chapter_match = CONCEPT_FILE_RE.fullmatch(name)
        if not chapter_match:
            raise TutorialError(
                f"invalid concept chapter filename: {relative_to_tutorial}"
            )
        if chapter_match.group(1) != part_number:
            raise TutorialError(
                f"chapter number does not match Part: {relative_to_tutorial}"
            )
        chapter_number = int(chapter_match.group(2))
        if chapter_number not in range(1, 6):
            raise TutorialError(
                f"concept chapter must be numbered 01..05: "
                f"{relative_to_tutorial}"
            )
        return "concept_chapter"
    if parts[0] == "capstones":
        if not CAPSTONE_FILE_RE.fullmatch(name):
            raise TutorialError(
                f"invalid capstone filename: {relative_to_tutorial}"
            )
        return "capstone"
    if parts[0] == "appendices":
        if not APPENDIX_FILE_RE.fullmatch(name):
            raise TutorialError(
                f"invalid appendix filename: {relative_to_tutorial}"
            )
        return "appendix"
    raise TutorialError(
        f"SUMMARY target has no curriculum kind: {relative_to_tutorial}"
    )


def inspect_document(root: Path, rel: str, kind: str) -> dict[str, Any]:
    relative = safe_relative(rel)
    root = root.resolve()
    path = root.joinpath(*relative.parts)
    cursor = root
    for component in relative.parts:
        cursor /= component
        if cursor.is_symlink():
            raise TutorialError(
                f"tutorial path must not contain a symlink: {rel}"
            )
    if not path.is_file():
        raise TutorialError(f"missing tutorial document: {rel}")
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TutorialError(f"tutorial document is not UTF-8: {rel}") from exc
    prose = FENCED_BLOCK_RE.sub("", text)
    return {
        "path": rel,
        "kind": kind,
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "korean_characters": len(KOREAN_RE.findall(prose)),
        "deeplus_blocks": len(DEEPLUS_BLOCK_RE.findall(text)),
        "exercise_prompts": len(EXERCISE_RE.findall(prose)),
        "level2_headings": len(LEVEL2_RE.findall(prose)),
        "_text": text,
    }


def validate_local_links(root: Path, member: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source = root / member["path"]
    root = root.resolve()
    for target_text in LOCAL_LINK_RE.findall(member["_text"]):
        target_text = target_text.strip()
        if target_text.startswith("<") and target_text.endswith(">"):
            target_text = target_text[1:-1]
        if "://" in target_text or target_text.startswith("mailto:"):
            continue
        if (
            "\x00" in target_text
            or re.match(r"^[A-Za-z]:", target_text)
            or any(ord(character) < 32 for character in target_text)
        ):
            errors.append(
                f"{member['path']}: unsafe local link: {target_text}"
            )
            continue
        target = PurePosixPath(target_text.replace("\\", "/"))
        if target.is_absolute():
            errors.append(
                f"{member['path']}: absolute local link: {target_text}"
            )
            continue
        resolved = (source.parent / Path(*target.parts)).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"{member['path']}: link escapes repository: {target_text}")
            continue
        if not resolved.exists():
            errors.append(f"{member['path']}: missing link target: {target_text}")
    return errors


def validate_target_matrix(
    tutorial_root: PurePosixPath, targets: list[str]
) -> None:
    parts: dict[str, dict[str, Any]] = {}
    capstones: set[str] = set()
    appendices: set[str] = set()
    for rel in targets:
        relative = PurePosixPath(rel).relative_to(tutorial_root)
        kind = classify(relative)
        if kind in {"part_guide", "concept_chapter", "guided_lab"}:
            part_number = PART_DIR_RE.fullmatch(relative.parts[0]).group(1)
            row = parts.setdefault(
                part_number,
                {"guides": 0, "labs": 0, "chapters": set()},
            )
            if kind == "part_guide":
                row["guides"] += 1
            elif kind == "guided_lab":
                row["labs"] += 1
            else:
                chapter = CONCEPT_FILE_RE.fullmatch(
                    relative.name
                ).group(2)
                row["chapters"].add(chapter)
        elif kind == "capstone":
            capstones.add(
                CAPSTONE_FILE_RE.fullmatch(relative.name).group(1)
            )
        elif kind == "appendix":
            appendices.add(
                APPENDIX_FILE_RE.fullmatch(relative.name).group(1)
            )

    expected_parts = {f"{number:02d}" for number in range(1, 13)}
    if set(parts) != expected_parts:
        raise TutorialError(
            f"SUMMARY Part set {sorted(parts)} != {sorted(expected_parts)}"
        )
    expected_chapters = {f"{number:02d}" for number in range(1, 6)}
    for part_number, row in sorted(parts.items()):
        if (
            row["guides"] != 1
            or row["labs"] != 1
            or row["chapters"] != expected_chapters
        ):
            raise TutorialError(
                f"Part {part_number} matrix is not "
                "one guide + chapters 01..05 + one lab"
            )
    if capstones != set("abcd"):
        raise TutorialError(
            f"SUMMARY capstone labels {sorted(capstones)} != a..d"
        )
    if appendices != set("abcdefgh"):
        raise TutorialError(
            f"SUMMARY appendix labels {sorted(appendices)} != a..h"
        )


def validate_schema_contract(
    schema: dict[str, Any],
    expected: dict[str, int],
    expected_member_count: int,
) -> None:
    if (
        schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("properties", {})
        .get("schema", {})
        .get("const")
        != MANIFEST_SCHEMA
    ):
        raise TutorialError("unexpected tutorial coverage schema identity")
    properties = schema["properties"]
    if properties.get("revision", {}).get("const") != REVISION:
        raise TutorialError("coverage schema revision is stale")
    if properties["contract"]["properties"]["path"].get("const") != CONTRACT_REL:
        raise TutorialError("coverage schema contract path is stale")
    if (
        properties["coverage_schema"]["properties"]["path"].get("const")
        != SCHEMA_REL
    ):
        raise TutorialError("coverage schema self-binding path is stale")
    curriculum_properties = properties["curriculum"]["properties"]
    for key, expected_value in expected.items():
        if curriculum_properties.get(key, {}).get("const") != expected_value:
            raise TutorialError(
                f"coverage schema curriculum {key} is not bound to "
                f"{expected_value}"
            )
    members = properties["members"]
    if (
        members.get("minItems") != expected_member_count
        or members.get("maxItems") != expected_member_count
    ):
        raise TutorialError(
            "coverage schema member cardinality is not exactly "
            f"{expected_member_count}"
        )
    source_bindings = properties.get("source_bindings", {})
    source_items = source_bindings.get("items", {})
    if (
        source_bindings.get("minItems") != len(SOURCE_BINDING_RELS)
        or source_bindings.get("maxItems") != len(SOURCE_BINDING_RELS)
        or set(source_items.get("required", []))
        != {"path", "bytes", "sha256"}
        or set(source_items.get("properties", {}))
        != {"path", "bytes", "sha256"}
        or source_items.get("properties", {})
        .get("path", {})
        .get("enum")
        != list(SOURCE_BINDING_RELS)
        or source_items.get("additionalProperties") is not False
    ):
        raise TutorialError("coverage schema source binding shape is stale")
    governance = properties.get("governance", {}).get("properties", {})
    if (
        governance.get("semantic_p0", {}).get("const") != 0
        or governance.get("feature_p1_status", {}).get("const") != "OPEN"
        or governance.get("open_feature_p1", {}).get("const")
        != len(FEATURE_P1_IDS)
        or governance.get("feature_p1_ids", {}).get("minItems")
        != len(FEATURE_P1_IDS)
        or governance.get("feature_p1_ids", {}).get("maxItems")
        != len(FEATURE_P1_IDS)
        or governance.get("separate_open_actions", {}).get("const")
        != len(SEPARATE_ACTION_IDS)
        or governance.get("separate_open_action_ids", {}).get("minItems")
        != len(SEPARATE_ACTION_IDS)
        or governance.get("separate_open_action_ids", {}).get("maxItems")
        != len(SEPARATE_ACTION_IDS)
        or governance.get("product_lanes", {}).get("const")
        != PRODUCT_LANE_COUNT
        or governance.get("product_lane_status", {}).get("const")
        != PRODUCT_LANE_STATUS
    ):
        raise TutorialError("coverage schema governance binding is stale")


def validate_status_fence(
    member: dict[str, Any], allowed_statuses: set[str]
) -> list[str]:
    prose = FENCED_BLOCK_RE.sub("", member["_text"])
    errors: list[str] = []
    status = STATUS_RE.search(prose)
    level2_headings = list(LEVEL2_RE.finditer(prose))
    if status is None:
        errors.append(f"{member['path']}: missing exact leading status fence")
        return errors
    if len(level2_headings) >= 2 and status.start() > level2_headings[1].start():
        errors.append(
            f"{member['path']}: status fence appears after the first section"
        )
    if status.group(1) not in allowed_statuses:
        errors.append(
            f"{member['path']}: unapproved status token {status.group(1)}"
        )
    if (
        not status.group(1).endswith("PRODUCT_NOT_RUN")
        and not PRODUCT_NOT_RUN_RE.search(prose)
    ):
        errors.append(f"{member['path']}: missing explicit product NOT_RUN fence")
    return errors


def validate_manifest_binding(
    manifest: dict[str, Any],
    schema: dict[str, Any],
    expected: dict[str, int],
    expected_member_count: int,
    source_bindings: list[dict[str, Any]],
) -> None:
    required = set(schema["required"])
    if set(manifest) != required:
        raise TutorialError(
            f"manifest fields {sorted(manifest)} != schema fields "
            f"{sorted(required)}"
        )
    if manifest["curriculum"] != expected:
        raise TutorialError("manifest curriculum is not the exact contract set")
    if len(manifest["members"]) != expected_member_count:
        raise TutorialError("manifest member count is not exact")
    paths = [member["path"] for member in manifest["members"]]
    if len(paths) != len(set(paths)):
        raise TutorialError("manifest member paths are not unique")
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise TutorialError("manifest schema identity mismatch")
    if manifest["revision"] != REVISION:
        raise TutorialError("manifest revision mismatch")
    if manifest["source_bindings"] != source_bindings:
        raise TutorialError("manifest source bindings are not exact")
    governance = manifest["governance"]
    if governance != {
        "semantic_p0": 0,
        "feature_p1_status": "OPEN",
        "open_feature_p1": len(FEATURE_P1_IDS),
        "feature_p1_ids": list(FEATURE_P1_IDS),
        "separate_open_actions": len(SEPARATE_ACTION_IDS),
        "separate_open_action_ids": list(SEPARATE_ACTION_IDS),
        "product_lanes": PRODUCT_LANE_COUNT,
        "product_lane_status": PRODUCT_LANE_STATUS,
    }:
        raise TutorialError("manifest governance binding is not exact")


def build(root: Path) -> tuple[dict[str, Any], bytes]:
    root = root.resolve()
    contract_path = root / CONTRACT_REL
    schema_path = root / SCHEMA_REL
    if not contract_path.is_file() or not schema_path.is_file():
        raise TutorialError("tutorial contract or schema is missing")
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes.decode("utf-8"))
    if contract.get("schema") != "deeplus.tutorial-contract/r1":
        raise TutorialError("unexpected tutorial contract schema")
    if contract.get("coverage_schema_path") != SCHEMA_REL:
        raise TutorialError("tutorial contract coverage schema path is stale")
    if contract.get("coverage_manifest_path") != MANIFEST_REL:
        raise TutorialError("tutorial contract manifest path is stale")
    if contract.get("coverage_report_path") != REPORT_REL:
        raise TutorialError("tutorial contract report path is stale")
    schema_bytes = schema_path.read_bytes()
    schema = json.loads(schema_bytes.decode("utf-8"))
    source_bindings = validate_authority_and_pointer(root, contract)

    summary_rel = safe_relative(contract["summary_path"]).as_posix()
    summary_path = root.joinpath(*PurePosixPath(summary_rel).parts)
    summary_text = summary_path.read_text(encoding="utf-8")
    tutorial_root = safe_relative(contract["tutorial_root"])
    targets: list[str] = []
    for raw in SUMMARY_LINK_RE.findall(summary_text):
        if "://" in raw or raw.startswith("mailto:"):
            continue
        relative = safe_relative(raw)
        normalized = tutorial_root / relative
        targets.append(normalized.as_posix())
    if len(targets) != len(set(targets)):
        duplicates = sorted(
            path for path in set(targets) if targets.count(path) > 1
        )
        raise TutorialError(f"duplicate SUMMARY targets: {duplicates}")

    expected = contract["expected_curriculum"]
    if len(targets) != expected["summary_linked_documents"]:
        raise TutorialError(
            f"SUMMARY links {len(targets)} != "
            f"{expected['summary_linked_documents']}"
        )
    validate_target_matrix(tutorial_root, targets)

    members: list[dict[str, Any]] = []
    root_guides = [
        "docs/tutorial/README.md",
        "docs/tutorial/AUTHORING_GUIDE.md",
        "docs/tutorial/SUMMARY.md",
    ]
    expected_member_count = (
        len(root_guides) + expected["summary_linked_documents"]
    )
    validate_schema_contract(schema, expected, expected_member_count)
    for rel in root_guides:
        members.append(inspect_document(root, rel, "root_guide"))
    for rel in targets:
        relative = PurePosixPath(rel).relative_to(tutorial_root)
        members.append(inspect_document(root, rel, classify(relative)))

    counts = {
        "part_guides": sum(m["kind"] == "part_guide" for m in members),
        "concept_chapters": sum(
            m["kind"] == "concept_chapter" for m in members
        ),
        "guided_labs": sum(m["kind"] == "guided_lab" for m in members),
        "capstones": sum(m["kind"] == "capstone" for m in members),
        "appendices": sum(m["kind"] == "appendix" for m in members),
        "summary_linked_documents": len(targets),
    }
    counts["learning_units"] = (
        counts["concept_chapters"] + counts["guided_labs"]
    )
    for key, expected_value in expected.items():
        if counts.get(key) != expected_value:
            raise TutorialError(
                f"curriculum count {key}={counts.get(key)} != {expected_value}"
            )

    floors = contract["quality_floor"]
    allowed_statuses = set(contract["allowed_status_tokens"])
    quality_errors: list[str] = []
    link_errors: list[str] = []
    for member in members:
        kind = member["kind"]
        if kind != "root_guide":
            floor = floors[kind]
            for key in (
                "minimum_korean_characters",
                "minimum_deeplus_blocks",
                "minimum_level2_headings",
            ):
                metric = key.removeprefix("minimum_")
                if member[metric] < floor[key]:
                    quality_errors.append(
                        f"{member['path']}: {metric}={member[metric]} "
                        f"< {floor[key]}"
                    )
            required_exercises = floor.get("minimum_exercise_prompts", 0)
            if member["exercise_prompts"] < required_exercises:
                quality_errors.append(
                    f"{member['path']}: exercise_prompts="
                    f"{member['exercise_prompts']} < {required_exercises}"
                )
            quality_errors.extend(
                validate_status_fence(member, allowed_statuses)
            )
        link_errors.extend(validate_local_links(root, member))
    if quality_errors or link_errors:
        raise TutorialError(
            "tutorial quality failure:\n- "
            + "\n- ".join(quality_errors + link_errors)
        )

    for member in members:
        member.pop("_text")
    members.sort(key=lambda item: item["path"])
    governance = contract["governance"]
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "revision": contract["revision"],
        "contract": {
            "path": CONTRACT_REL,
            "sha256": sha256_bytes(contract_bytes),
        },
        "coverage_schema": {
            "path": SCHEMA_REL,
            "sha256": sha256_bytes(schema_bytes),
        },
        "source_bindings": source_bindings,
        "curriculum": counts,
        "quality": {
            "korean_characters": sum(m["korean_characters"] for m in members),
            "deeplus_blocks": sum(m["deeplus_blocks"] for m in members),
            "exercise_prompts": sum(m["exercise_prompts"] for m in members),
            "level2_headings": sum(m["level2_headings"] for m in members),
            "local_link_errors": 0,
        },
        "governance": {
            "semantic_p0": governance["semantic_p0"],
            "feature_p1_status": governance["feature_p1_status"],
            "open_feature_p1": len(governance["feature_p1_ids"]),
            "feature_p1_ids": governance["feature_p1_ids"],
            "separate_open_actions": len(
                governance["separate_open_action_ids"]
            ),
            "separate_open_action_ids": governance[
                "separate_open_action_ids"
            ],
            "product_lanes": governance["product_lane_count"],
            "product_lane_status": governance["product_lane_status"],
        },
        "members": members,
    }
    validate_manifest_binding(
        manifest, schema, expected, expected_member_count, source_bindings
    )
    return manifest, canonical_json(manifest)


def report_bytes(manifest: dict[str, Any]) -> bytes:
    curriculum = manifest["curriculum"]
    quality = manifest["quality"]
    governance = manifest["governance"]
    lines = [
        "<!-- tools/generators/generate_tutorial.py가 생성함. 직접 수정하지 마십시오. -->",
        "",
        "# Deeplus 튜토리얼 coverage 보고서",
        "",
        f"- revision: `{manifest['revision']}`",
        f"- Part 안내: {curriculum['part_guides']}",
        f"- 개념 장: {curriculum['concept_chapters']}",
        f"- 안내 실습: {curriculum['guided_labs']}",
        f"- 종합 프로젝트: {curriculum['capstones']}",
        f"- 부록: {curriculum['appendices']}",
        f"- SUMMARY 연결 문서: {curriculum['summary_linked_documents']}",
        f"- 학습 단위: {curriculum['learning_units']}",
        f"- 한국어 문자: {quality['korean_characters']}",
        f"- Deeplus 코드 블록: {quality['deeplus_blocks']}",
        f"- 연습 prompt 표식: {quality['exercise_prompts']}",
        f"- 로컬 링크 오류: {quality['local_link_errors']}",
        f"- contract SHA-256: `{manifest['contract']['sha256']}`",
        f"- coverage schema SHA-256: "
        f"`{manifest['coverage_schema']['sha256']}`",
        "",
        "## authority 울타리",
        "",
        f"- semantic P0: `{governance['semantic_p0']}`",
        f"- feature P1: `{governance['open_feature_p1']} "
        f"{governance['feature_p1_status']}`",
        f"- 별도 action: `{governance['separate_open_actions']} OPEN` "
        f"(`{', '.join(governance['separate_open_action_ids'])}`)",
        f"- product lanes: `{governance['product_lanes']}/"
        f"{governance['product_lanes']} "
        f"{governance['product_lane_status']}`",
        "- 이 projection은 독립 semantic authority가 아니다.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


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
        manifest, manifest_data = build(root)
        report_data = report_bytes(manifest)
        outputs = {
            root / MANIFEST_REL: manifest_data,
            root / REPORT_REL: report_data,
        }
        if args.write:
            for path, data in outputs.items():
                atomic_write(path, data)
        else:
            for path, expected in outputs.items():
                if not path.is_file():
                    raise TutorialError(f"generated output missing: {path}")
                if path.read_bytes() != expected:
                    raise TutorialError(f"generated output stale: {path}")
    except (OSError, ValueError, KeyError, TutorialError) as exc:
        print(f"TUTORIAL_VALIDATION_FAILED: {exc}")
        return 1
    print(
        "TUTORIAL_VALIDATION_PASS: "
        f"{manifest['curriculum']['learning_units']} learning units, "
        f"{manifest['quality']['deeplus_blocks']} Deeplus blocks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
