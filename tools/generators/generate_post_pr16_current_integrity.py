#!/usr/bin/env python3
"""Check and render the bounded Post-PR16 R4+CMA-R1 current-integrity fields.

This is deterministic NON_PRODUCT repository tooling.  It owns only the
authority-domain hashes/aggregate and the current-pointer authority digest.
It never runs a Deeplus product lane and it deliberately leaves the immutable
R2.3 generator, contract, tests, and receipt untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.9 local fallback; CI uses 3.12.
    tomllib = None  # type: ignore[assignment]
from pathlib import Path
from typing import Any


CONTRACT_REL = "tools/generators/post-pr16-current-integrity.contract.json"
GENERATOR_REL = "tools/generators/generate_post_pr16_current_integrity.py"
EXPECTED_SCHEMA = "deeplus.post-pr16-current-integrity-contract/r5"
AUTHORITY_REL = "current/authority-map.yaml"
POINTER_REL = "current/current-pointer.json"
OUTPUTS = (AUTHORITY_REL, POINTER_REL)
DOMAIN_RE = re.compile(
    r'^  ([a-z_]+):\n'
    r'    path: (\S+)\n'
    r'    owner: "([^"]+)"\n'
    r'    sha256: ([0-9a-f]{64})$',
    re.MULTILINE,
)
AUTHORITY_DIGEST_RE = re.compile(
    r"^authority_digest: ([0-9a-f]{64})$", re.MULTILINE
)


class GeneratorError(RuntimeError):
    """A bounded R4+CMA-R1 integrity stop condition."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    material = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(material)


def read_json(path: Path, code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratorError(code, f"{path}: {exc}") from exc


def safe_path(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise GeneratorError("POST_PR16_OUTPUT_ESCAPE", rel.as_posix())
    root = root.resolve()
    lexical = root / rel
    current = root
    for part in rel.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise GeneratorError("POST_PR16_OUTPUT_ESCAPE", rel.as_posix())
    try:
        lexical.resolve(strict=must_exist).relative_to(root)
    except (OSError, ValueError) as exc:
        raise GeneratorError("POST_PR16_OUTPUT_ESCAPE", rel.as_posix()) from exc
    return lexical


def load_contract(root: Path) -> dict[str, Any]:
    contract = read_json(
        safe_path(root, CONTRACT_REL, must_exist=True),
        "POST_PR16_CONTRACT_DRIFT",
    )
    if not isinstance(contract, dict) or contract.get("schema") != EXPECTED_SCHEMA:
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "contract schema")
    if contract.get("revision") != "r51f3-post-pr16-preview-design-r4-cma-r1":
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "revision")
    if contract.get("materialization_timestamp") != "2026-07-23T02:40:25+09:00":
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "timestamp")
    ownership = tuple(
        row.get("path") for row in contract.get("output_ownership", [])
    )
    if ownership != OUTPUTS or len(set(ownership)) != len(OUTPUTS):
        raise GeneratorError("POST_PR16_OUTPUT_OWNERSHIP", repr(ownership))
    for rel in ownership:
        safe_path(root, rel)

    units = contract.get("normalized_units", [])
    unit_ids = [row.get("id") for row in units if isinstance(row, dict)]
    paths = [row.get("target") for row in units if isinstance(row, dict)]
    if (
        len(units) != 69
        or len(set(unit_ids)) != 69
        or paths.count("spec/language.md") != 63
        or paths.count("spec/types/type-system.md") != 4
        or paths.count("spec/mir/semantics.md") != 1
        or paths.count("decisions/language/current-decisions.json") != 1
    ):
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "normalized unit set")
    for row in units:
        if set(row) != {
            "id",
            "target",
            "order",
            "authority_raw_sha256",
            "lf_sha256",
            "kind",
        }:
            raise GeneratorError(
                "POST_PR16_CONTRACT_DRIFT", f"unit shape: {row.get('id')}"
            )
        safe_path(root, row["target"], must_exist=True)
        if not all(
            re.fullmatch(r"[0-9a-f]{64}", row[field])
            for field in ("authority_raw_sha256", "lf_sha256")
        ):
            raise GeneratorError(
                "POST_PR16_CONTRACT_DRIFT", f"unit digest: {row['id']}"
            )
    correction = contract.get("historical_sha_role_correction", {})
    corrected = next(
        (row for row in units if row.get("id") == correction.get("unit")), None
    )
    if (
        corrected is None
        or corrected["authority_raw_sha256"]
        != correction.get("authority_artifact_raw_sha256")
        or corrected["lf_sha256"] != correction.get("canonical_lf_sha256")
        or correction.get("correction_kind") != "HISTORICAL_SHA_ROLE_SWAP"
        or correction.get("semantic_effect") != "NONE"
        or correction.get("authority_artifact_immutable") is not True
        or len(
            [
                row
                for row in units
                if row["authority_raw_sha256"] != row["lf_sha256"]
            ]
        )
        != 20
    ):
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "raw/LF provenance")
    canonical_targets = contract.get("canonical_targets", [])
    expected_target_paths = {
        "decisions/language/current-decisions.json",
        "spec/language.md",
        "spec/mir/semantics.md",
        "spec/types/type-system.md",
    }
    if (
        len(canonical_targets) != len(expected_target_paths)
        or {row.get("path") for row in canonical_targets if isinstance(row, dict)}
        != expected_target_paths
        or any(
            set(row) != {"path", "bytes", "sha256"}
            or not isinstance(row["bytes"], int)
            or row["bytes"] < 0
            or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
            for row in canonical_targets
        )
        or not re.fullmatch(
            r"[0-9a-f]{64}",
            contract.get("pointer_non_owned_canonical_sha256", ""),
        )
    ):
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "canonical target pins")
    for row in canonical_targets:
        safe_path(root, row["path"], must_exist=True)
    return contract


def domain_digest(root: Path, relative: str) -> str:
    target = safe_path(root, relative, must_exist=True)
    if target.is_file():
        return sha256_bytes(target.read_bytes())
    if not target.is_dir():
        raise GeneratorError("POST_PR16_BOUND_STATE_DRIFT", relative)
    rows = []
    for path in sorted(target.rglob("*.json")):
        if path.is_symlink():
            raise GeneratorError("POST_PR16_OUTPUT_ESCAPE", path.as_posix())
        try:
            rel = path.resolve(strict=True).relative_to(root)
        except (OSError, ValueError) as exc:
            raise GeneratorError("POST_PR16_OUTPUT_ESCAPE", path.as_posix()) from exc
        rows.append(rel.as_posix() + "\0" + sha256_bytes(path.read_bytes()))
    return sha256_bytes("\n".join(rows).encode("utf-8"))


def parse_and_render_authority(
    root: Path, contract: dict[str, Any]
) -> tuple[bytes, str, list[dict[str, str]]]:
    path = safe_path(root, AUTHORITY_REL, must_exist=True)
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise GeneratorError("POST_PR16_BOUND_STATE_DRIFT", str(exc)) from exc
    rows = DOMAIN_RE.findall(text)
    expected = contract["authority_domains"]
    declared = [
        {"domain": domain, "path": rel, "owner": owner}
        for domain, rel, owner, _digest in rows
    ]
    if declared != expected:
        raise GeneratorError("POST_PR16_AUTHORITY_SHAPE", repr(declared))
    if not AUTHORITY_DIGEST_RE.search(text):
        raise GeneratorError("POST_PR16_AUTHORITY_SHAPE", "aggregate missing")

    normalized = DOMAIN_RE.sub(
        lambda match: (
            f"  {match.group(1)}:\n"
            f"    path: {match.group(2)}\n"
            f'    owner: "{match.group(3)}"\n'
            "    sha256: <OWNED>"
        ),
        text,
    )
    normalized = AUTHORITY_DIGEST_RE.sub(
        "authority_digest: <OWNED>", normalized, count=1
    )
    if sha256_bytes(normalized.encode("utf-8")) != contract[
        "authority_non_owned_sha256"
    ]:
        raise GeneratorError("POST_PR16_AUTHORITY_SHAPE", "non-owned fields")

    digest_rows = []
    actual = {}
    for row in expected:
        digest = domain_digest(root, row["path"])
        actual[row["domain"]] = digest
        digest_rows.append(
            {
                "domain": row["domain"],
                "path": row["path"],
                "sha256": digest,
                "owner": row["owner"],
            }
        )
    if actual["features"] != contract["feature_catalog"]["domain_sha256"]:
        raise GeneratorError("POST_PR16_FEATURE_DRIFT", actual["features"])
    aggregate = canonical_sha(digest_rows)

    def replace_domain(match: re.Match[str]) -> str:
        domain, rel, owner, _old = match.groups()
        return (
            f"  {domain}:\n"
            f"    path: {rel}\n"
            f'    owner: "{owner}"\n'
            f"    sha256: {actual[domain]}"
        )

    rendered = DOMAIN_RE.sub(replace_domain, text)
    rendered = AUTHORITY_DIGEST_RE.sub(
        f"authority_digest: {aggregate}", rendered, count=1
    )
    return rendered.encode("utf-8"), aggregate, digest_rows


def parse_yaml_revision(text: str, code: str) -> str:
    match = re.search(r"^revision: (\S+)$", text, re.MULTILINE)
    if not match:
        raise GeneratorError(code, "revision missing")
    return match.group(1)


def parse_language_version(text: str) -> dict[str, str]:
    if tomllib is not None:
        return tomllib.loads(text)
    values = dict(
        re.findall(r'^([a-z_]+)\s*=\s*"([^"]*)"$', text, re.MULTILINE)
    )
    if not values:
        raise GeneratorError("POST_PR16_REVISION_PARITY", "language-version.toml")
    return values


def validate_revision_and_lanes(
    root: Path, pointer: dict[str, Any], contract: dict[str, Any]
) -> None:
    revision = contract["revision"]
    try:
        language_version = parse_language_version(
            safe_path(root, "current/language-version.toml", must_exist=True)
            .read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise GeneratorError("POST_PR16_REVISION_PARITY", str(exc)) from exc
    implementation_text = safe_path(
        root, "current/implementation-status.yaml", must_exist=True
    ).read_text(encoding="utf-8")
    implementation_revision = parse_yaml_revision(
        implementation_text, "POST_PR16_REVISION_PARITY"
    )
    if (
        pointer.get("spec_revision") != revision
        or language_version.get("spec_revision") != revision
        or language_version.get("language") != "0.1.2-internal"
        or implementation_revision != revision
    ):
        raise GeneratorError(
            "POST_PR16_REVISION_PARITY",
            repr(
                (
                    pointer.get("spec_revision"),
                    language_version.get("spec_revision"),
                    implementation_revision,
                )
            ),
        )

    lane_ids = contract["product_lanes"]
    pointer_lanes = pointer.get("product_lanes")
    registry = read_json(
        safe_path(root, "current/product-lanes.json", must_exist=True),
        "POST_PR16_PRODUCT_LANE_TRANSITION",
    )
    registry_lanes = registry.get("lanes", []) if isinstance(registry, dict) else []
    registry_map = {
        row.get("lane_id"): row.get("status")
        for row in registry_lanes
        if isinstance(row, dict)
    }
    implementation_map = dict(
        re.findall(
            r"^  ([a-z0-9_]+): (NOT_RUN|BLOCKED|FAILED|PASSED_FOCUSED|PASSED_INTEGRATED|PASSED_INDEPENDENT)$",
            implementation_text,
            re.MULTILINE,
        )
    )
    expected = {lane: "NOT_RUN" for lane in lane_ids}
    if (
        pointer_lanes != expected
        or registry_map != expected
        or implementation_map != expected
    ):
        raise GeneratorError(
            "POST_PR16_PRODUCT_LANE_TRANSITION", "15/15 NOT_RUN parity"
        )


def validate_actions(pointer: dict[str, Any], contract: dict[str, Any]) -> None:
    actions = pointer.get("open_actions", [])
    action_ids = [row.get("id") for row in actions if isinstance(row, dict)]
    expected_ids = contract["open_action_ids"]
    action_keys = {
        "id",
        "priority",
        "summary",
        "owner",
        "tracking_ref",
        "acceptance_test",
        "target",
    }
    if (
        action_ids != expected_ids
        or len(action_ids) != 26
        or len(set(action_ids)) != 26
        or any(set(row) != action_keys for row in actions)
        or any(not all(bool(row.get(key)) for key in action_keys) for row in actions)
        or any(
            row.get("tracking_ref") != f"deeplus-action:{row.get('id')}"
            for row in actions
        )
        or any(row.get("priority") != "P1" for row in actions[4:])
    ):
        raise GeneratorError("POST_PR16_ACTION_SET", repr(action_ids))
    if pointer.get("required_next_reviews") != contract["required_next_reviews"]:
        raise GeneratorError(
            "POST_PR16_REVIEW_SET", repr(pointer.get("required_next_reviews"))
        )


def validate_baseline_preservation(root: Path, contract: dict[str, Any]) -> None:
    baseline = contract["baseline_preservation"]
    for row in baseline["markdown_prefixes"]:
        data = safe_path(root, row["path"], must_exist=True).read_bytes()
        prefix = data[: row["bytes"]]
        heading = contract["containers"][row["path"]].encode("utf-8")
        boundary = row["separator_before_container"].encode("utf-8") + heading
        if (
            len(prefix) != row["bytes"]
            or sha256_bytes(prefix) != row["sha256"]
            or data[row["bytes"] : row["bytes"] + len(boundary)] != boundary
        ):
            raise GeneratorError("POST_PR16_BASELINE_DRIFT", row["path"])

    decision_contract = baseline["decision_projection"]
    decision = read_json(
        safe_path(root, decision_contract["path"], must_exist=True),
        "POST_PR16_BASELINE_DRIFT",
    )
    law_count = decision_contract["baseline_law_count"]
    projection = {
        "schema": decision.get("schema"),
        "baseline": decision.get("baseline"),
        "authority": decision.get("authority"),
        "laws": decision.get("laws", [])[:law_count],
        "authority_policy": decision.get("authority_policy"),
    }
    if (
        len(projection["laws"]) != law_count
        or canonical_sha(projection) != decision_contract["canonical_sha256"]
    ):
        raise GeneratorError("POST_PR16_BASELINE_DRIFT", decision_contract["path"])


def validate_canonical_targets(root: Path, contract: dict[str, Any]) -> None:
    for row in contract["canonical_targets"]:
        data = safe_path(root, row["path"], must_exist=True).read_bytes()
        if len(data) != row["bytes"] or sha256_bytes(data) != row["sha256"]:
            raise GeneratorError("POST_PR16_CANONICAL_TARGET_DRIFT", row["path"])


def validate_units(root: Path, contract: dict[str, Any]) -> None:
    markdown_units = [row for row in contract["normalized_units"] if row["kind"] == "markdown"]
    json_units = [row for row in contract["normalized_units"] if row["kind"] == "json-law"]
    if len(markdown_units) != 68 or len(json_units) != 1:
        raise GeneratorError("POST_PR16_CONTRACT_DRIFT", "unit kind counts")
    by_target: dict[str, list[dict[str, Any]]] = {}
    for row in markdown_units:
        by_target.setdefault(row["target"], []).append(row)

    for target, rows in by_target.items():
        data = safe_path(root, target, must_exist=True).read_bytes()
        if b"\r" in data:
            raise GeneratorError("POST_PR16_UNIT_HASH", f"non-LF bytes: {target}")
        ordered_positions = []
        for row in rows:
            ident = row["id"]
            begin = f"<!-- POST_PR16_UNIT_BEGIN:{ident} -->\n".encode("utf-8")
            end = f"<!-- POST_PR16_UNIT_END:{ident} -->".encode("utf-8")
            if data.count(begin) != 1 or data.count(end) != 1:
                raise GeneratorError(
                    "POST_PR16_UNIT_CARDINALITY", f"{target}:{ident}"
                )
            start = data.index(begin) + len(begin)
            stop = data.index(end, start)
            payload = data[start:stop]
            if sha256_bytes(payload) != row["lf_sha256"]:
                raise GeneratorError("POST_PR16_UNIT_HASH", f"{target}:{ident}")
            ordered_positions.append((row["order"], data.index(begin), ident))
        if (
            [row[0] for row in ordered_positions]
            != sorted(row[0] for row in ordered_positions)
            or [row[1] for row in ordered_positions]
            != sorted(row[1] for row in ordered_positions)
        ):
            raise GeneratorError("POST_PR16_UNIT_ORDER", target)
        all_begin = re.findall(
            rb"<!-- POST_PR16_UNIT_BEGIN:([^ >]+) -->", data
        )
        expected_here = {row["id"].encode("utf-8") for row in rows}
        observed_here = set(all_begin)
        if observed_here != expected_here or len(all_begin) != len(expected_here):
            raise GeneratorError("POST_PR16_UNIT_CARDINALITY", target)

    decisions = read_json(
        safe_path(root, "decisions/language/current-decisions.json", must_exist=True),
        "POST_PR16_LAW_SET",
    )
    laws = decisions.get("laws", []) if isinstance(decisions, dict) else []
    law_ids = [row.get("id") for row in laws if isinstance(row, dict)]
    if decisions.get("law_count") != 20 or law_ids != contract["law_ids"]:
        raise GeneratorError("POST_PR16_LAW_SET", repr(law_ids))
    added = laws[-6:]
    fence = contract["added_law_fence"]
    for law in added:
        for key, value in fence.items():
            if law.get(key) != value:
                raise GeneratorError(
                    "POST_PR16_STATUS_FENCE", f"{law.get('id')}:{key}"
                )
    json_unit = json_units[0]
    law = next((row for row in laws if row.get("id") == json_unit["id"]), None)
    if law is None:
        raise GeneratorError("POST_PR16_LAW_SET", json_unit["id"])
    compact = (
        json.dumps(law, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    if sha256_bytes(compact) != json_unit["lf_sha256"]:
        raise GeneratorError("POST_PR16_UNIT_HASH", json_unit["id"])

    for target, heading in contract["containers"].items():
        text = safe_path(root, target, must_exist=True).read_text(encoding="utf-8")
        fence = contract["container_fences"][target]
        exact = f"{heading}\n\n{fence}\n\n"
        if text.count(heading) != 1 or text.count(fence) != 1 or text.count(exact) != 1:
            raise GeneratorError("POST_PR16_STATUS_FENCE", f"container: {target}")


def validate_feature_catalog(root: Path, contract: dict[str, Any]) -> None:
    metadata = read_json(
        safe_path(
            root, "spec/features/catalog/catalog-metadata.json", must_exist=True
        ),
        "POST_PR16_FEATURE_DRIFT",
    )
    if metadata.get("feature_count") != contract["feature_catalog"]["count"]:
        raise GeneratorError(
            "POST_PR16_FEATURE_DRIFT", str(metadata.get("feature_count"))
        )


def validate_immutable_r2_3(root: Path, contract: dict[str, Any]) -> None:
    for row in contract["immutable_r2_3"]:
        path = safe_path(root, row["path"], must_exist=True)
        if sha256_bytes(path.read_bytes()) != row["sha256"]:
            raise GeneratorError("POST_PR16_HISTORICAL_R2_3_DRIFT", row["path"])


def validate_scope_preserved_inputs(root: Path, contract: dict[str, Any]) -> None:
    for row in contract["scope_preserved_inputs"]:
        path = safe_path(root, row["path"], must_exist=True)
        if sha256_bytes(path.read_bytes()) != row["sha256"]:
            raise GeneratorError("POST_PR16_SCOPE_DRIFT", row["path"])


def render_pointer(
    root: Path, aggregate: str, contract: dict[str, Any]
) -> tuple[bytes, dict[str, Any]]:
    path = safe_path(root, POINTER_REL, must_exist=True)
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise GeneratorError("POST_PR16_BOUND_STATE_DRIFT", POINTER_REL) from exc
    pointer = read_json(path, "POST_PR16_BOUND_STATE_DRIFT")
    if not isinstance(pointer, dict) or not re.fullmatch(
        r"[0-9a-f]{64}", pointer.get("authority_digest", "")
    ):
        raise GeneratorError("POST_PR16_BOUND_STATE_DRIFT", POINTER_REL)
    if pointer.get("updated_at") != contract["materialization_timestamp"]:
        raise GeneratorError(
            "POST_PR16_REVISION_PARITY", f"updated_at={pointer.get('updated_at')}"
        )
    non_owned = {key: value for key, value in pointer.items() if key != "authority_digest"}
    if canonical_sha(non_owned) != contract["pointer_non_owned_canonical_sha256"]:
        raise GeneratorError("POST_PR16_POINTER_NONOWNED_DRIFT", POINTER_REL)
    validate_revision_and_lanes(root, pointer, contract)
    validate_actions(pointer, contract)
    old = pointer["authority_digest"]
    needle = f'"authority_digest": "{old}"'
    if text.count(needle) != 1:
        raise GeneratorError("POST_PR16_OUTPUT_OWNERSHIP", POINTER_REL)
    rendered = text.replace(
        needle, f'"authority_digest": "{aggregate}"', 1
    ).encode("utf-8")
    return rendered, pointer


def render_outputs(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = root.resolve()
    contract = load_contract(root)
    validate_immutable_r2_3(root, contract)
    validate_scope_preserved_inputs(root, contract)
    validate_feature_catalog(root, contract)
    validate_baseline_preservation(root, contract)
    validate_units(root, contract)
    validate_canonical_targets(root, contract)
    authority, aggregate, digest_rows = parse_and_render_authority(root, contract)
    pointer, _pointer_value = render_pointer(root, aggregate, contract)
    rendered = {AUTHORITY_REL: authority, POINTER_REL: pointer}
    detail = {
        "revision": contract["revision"],
        "authority_digest": aggregate,
        "authority_domains": len(digest_rows),
        "normalized_units": 69,
        "open_actions": 26,
        "feature_count": 681,
        "law_count": 20,
        "product_lanes": "15/15_NOT_RUN",
    }
    return rendered, detail


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def run(root: Path, mode: str) -> int:
    root = root.resolve()
    rendered, detail = render_outputs(root)
    mismatches = [
        rel
        for rel, data in rendered.items()
        if safe_path(root, rel, must_exist=True).read_bytes() != data
    ]
    if mode == "check" and mismatches:
        raise GeneratorError("POST_PR16_CHECK_MISMATCH", ", ".join(mismatches))
    if mode == "write":
        for rel in OUTPUTS:
            atomic_write(safe_path(root, rel, must_exist=True), rendered[rel])
        second, _ = render_outputs(root)
        if second != rendered:
            raise GeneratorError("POST_PR16_NONDETERMINISTIC", "second render")
    receipt = {
        "schema": "deeplus.post-pr16-current-integrity-receipt/r5",
        "result": "PASS",
        "mode": mode.upper(),
        **detail,
        "owned_outputs": list(OUTPUTS),
        "source_tree_manifest": "GENERATE_LAST_WITH_BUILD_SOURCE_ARCHIVE",
        "product_execution": "NOT_RUN",
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        return run(args.root, "write" if args.write else "check")
    except GeneratorError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
