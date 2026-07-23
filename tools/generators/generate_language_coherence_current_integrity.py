#!/usr/bin/env python3
"""Check/render the bounded language-coherence current integrity projection.

The generator owns only the revision/digest fields of ``authority-map.yaml``
and the materialization timestamp/authority digest of ``current-pointer.json``.
All other state is pinned by a reviewed contract.  ``--refresh-contract`` is an
explicit authority operation used before final staging; ordinary validation
never refreshes or learns new hashes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
from pathlib import Path
from typing import Any


REVISION = "r51f3-current-literal-shaped-collection-design-r1"
PREVIOUS_REVISION = "r51f3-current-enum-derived-capabilities-r1"
CONTRACT_REL = "spec/contracts/language-coherence-current-integrity-r1.json"
AUTHORITY_REL = "current/authority-map.yaml"
POINTER_REL = "current/current-pointer.json"
OUTPUTS = (AUTHORITY_REL, POINTER_REL)
EXCLUDED_PARTS = {".git", "__pycache__", "target", "dist"}
DOMAIN_RE = re.compile(
    r'^  ([a-z_]+):\n'
    r'    path: (\S+)\n'
    r'    owner: "([^"]+)"\n'
    r'    sha256: ([0-9a-f]{64})$',
    re.MULTILINE,
)
REVISION_RE = re.compile(r"^revision: (\S+)$", re.MULTILINE)
AUTHORITY_DIGEST_RE = re.compile(
    r"^authority_digest: ([0-9a-f]{64})$", re.MULTILINE
)
ACTION_IDS = [
    "M13-A002",
    "M13-A003",
    "M13-A004",
    "M13-A005",
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
FEATURE_P1_IDS = ACTION_IDS[4:]
SEPARATE_ACTION_IDS = ACTION_IDS[:4]


class GeneratorError(RuntimeError):
    """A bounded integrity stop condition with a stable diagnostic code."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(data)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_path(root: Path, relative: str, *, must_exist: bool = True) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise GeneratorError("LANGUAGE_COHERENCE_PATH_ESCAPE", relative)
    root = root.resolve()
    path = root / rel
    current = root
    for part in rel.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise GeneratorError("LANGUAGE_COHERENCE_PATH_SYMLINK", relative)
    try:
        path.resolve(strict=must_exist).relative_to(root)
    except (OSError, ValueError) as exc:
        raise GeneratorError("LANGUAGE_COHERENCE_PATH_ESCAPE", relative) from exc
    return path


def read_json(path: Path, code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratorError(code, f"{path}: {exc}") from exc


def iter_bound_files(root: Path, target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if not target.is_dir():
        raise GeneratorError("LANGUAGE_COHERENCE_BOUND_PATH", str(target))
    result: list[Path] = []
    # Path ordering follows the host filesystem flavour by default.  In
    # particular, Windows compares case-insensitively while POSIX compares
    # case-sensitively, which made mixed-case trees hash differently in CI.
    # Bind the portable repository spelling instead.
    for path in sorted(
        target.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        if any(part in EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            raise GeneratorError(
                "LANGUAGE_COHERENCE_PATH_SYMLINK",
                path.relative_to(root).as_posix(),
            )
        if not path.is_file():
            continue
        if path.relative_to(root).as_posix() == CONTRACT_REL:
            continue
        result.append(path)
    return result


def bound_identity(root: Path, relative: str) -> dict[str, Any]:
    target = safe_path(root, relative)
    if target.is_file():
        data = target.read_bytes()
        return {
            "path": relative,
            "kind": "file",
            "file_count": 1,
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        }
    rows = []
    total = 0
    for path in iter_bound_files(root, target):
        data = path.read_bytes()
        total += len(data)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    return {
        "path": relative,
        "kind": "directory",
        "file_count": len(rows),
        "bytes": total,
        "sha256": canonical_sha(rows),
    }


def domain_digest(root: Path, relative: str) -> str:
    target = safe_path(root, relative)
    if target.is_file():
        return sha256_bytes(target.read_bytes())
    rows = []
    for path in iter_bound_files(root, target):
        rows.append(
            path.relative_to(root).as_posix()
            + "\0"
            + sha256_bytes(path.read_bytes())
        )
    return sha256_bytes("\n".join(rows).encode("utf-8"))


def normalize_authority(text: str) -> str:
    if len(REVISION_RE.findall(text)) != 1:
        raise GeneratorError("LANGUAGE_COHERENCE_AUTHORITY_SHAPE", "revision")
    if len(AUTHORITY_DIGEST_RE.findall(text)) != 1:
        raise GeneratorError("LANGUAGE_COHERENCE_AUTHORITY_SHAPE", "aggregate")
    normalized = REVISION_RE.sub("revision: <OWNED>", text, count=1)
    normalized = DOMAIN_RE.sub(
        lambda match: (
            f"  {match.group(1)}:\n"
            f"    path: {match.group(2)}\n"
            f'    owner: "{match.group(3)}"\n'
            "    sha256: <OWNED>"
        ),
        normalized,
    )
    return AUTHORITY_DIGEST_RE.sub(
        "authority_digest: <OWNED>", normalized, count=1
    )


def normalized_pointer_sha(pointer: dict[str, Any]) -> str:
    normalized = copy.deepcopy(pointer)
    normalized["updated_at"] = "<OWNED>"
    normalized["authority_digest"] = "<OWNED>"
    return canonical_sha(normalized)


def collect_counts(root: Path) -> dict[str, int]:
    def value(relative: str, key: str) -> int:
        parsed = read_json(
            safe_path(root, relative), "LANGUAGE_COHERENCE_COUNT_METADATA"
        )
        result = parsed.get(key) if isinstance(parsed, dict) else None
        if not isinstance(result, int) or result < 0:
            raise GeneratorError(
                "LANGUAGE_COHERENCE_COUNT_METADATA", f"{relative}:{key}"
            )
        return result

    vocabulary = read_json(
        safe_path(root, "spec/grammar/keyword-vocabulary.json"),
        "LANGUAGE_COHERENCE_COUNT_METADATA",
    )
    return {
        "features": value("spec/features/catalog/catalog-metadata.json", "feature_count"),
        "diagnostics": value(
            "spec/diagnostics/catalog/catalog-metadata.json", "diagnostic_count"
        ),
        "predicates": value(
            "spec/types/predicates/catalog-metadata.json", "predicate_count"
        ),
        "predicate_fixtures": value(
            "tests/conformance/checker-predicates/catalog-metadata.json",
            "fixture_count",
        ),
        "no_go": value(
            "spec/compatibility/no-go/catalog-metadata.json", "entry_count"
        ),
        "hard_keywords": len(vocabulary.get("hard_keywords", [])),
        "contextual_words": len(vocabulary.get("contextual_words", [])),
        "prelude_entries": value(
            "library/prelude/signatures/catalog-metadata.json", "entry_count"
        ),
    }


def collect_migration_exemptions(root: Path) -> list[dict[str, str]]:
    repair = read_json(
        safe_path(root, "migration/m1.1-repair-manifest.json"),
        "LANGUAGE_COHERENCE_MIGRATION_EXEMPTION",
    )
    transformations = repair.get("reference_normalization", {}).get(
        "transformations", []
    )
    changed_paths = {
        repair.get("human_corpus", {}).get("path"),
        *(row.get("path") for row in transformations if isinstance(row, dict)),
    }
    changed_paths.discard(None)
    exemptions: dict[str, str] = {}
    for row in transformations:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            continue
        path = safe_path(root, row["path"])
        if path.is_file() and sha256_bytes(path.read_bytes()) != row.get("output_sha256"):
            exemptions[row["path"]] = sha256_bytes(path.read_bytes())

    imported = read_json(
        safe_path(root, "migration/import-manifest.json"),
        "LANGUAGE_COHERENCE_MIGRATION_EXEMPTION",
    )
    for entry in imported.get("legacy_files", []):
        if not isinstance(entry, dict) or entry.get("disposition") == "MIGRATED_SOURCE_SHARDS":
            continue
        for relative in entry.get("current_paths", []):
            if relative in changed_paths:
                continue
            path = safe_path(root, relative)
            if path.is_file() and sha256_bytes(path.read_bytes()) != entry.get("sha256"):
                exemptions[relative] = sha256_bytes(path.read_bytes())
    return [
        {"path": path, "sha256": digest}
        for path, digest in sorted(exemptions.items())
    ]


def load_contract(root: Path, *, relaxed: bool = False) -> dict[str, Any]:
    contract = read_json(
        safe_path(root, CONTRACT_REL), "LANGUAGE_COHERENCE_CONTRACT"
    )
    if (
        not isinstance(contract, dict)
        or contract.get("schema")
        != "deeplus.language-coherence-current-integrity-contract/r1"
        or contract.get("revision") != REVISION
        or contract.get("previous_revision") != PREVIOUS_REVISION
    ):
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "identity")
    roots = contract.get("bound_roots", [])
    paths = [row.get("path") for row in roots if isinstance(row, dict)]
    if not roots or len(paths) != len(set(paths)) or any(not path for path in paths):
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "bound roots")
    for path in paths:
        safe_path(root, path)
    if relaxed:
        return contract
    expected_keys = {"path", "kind", "file_count", "bytes", "sha256"}
    if any(set(row) != expected_keys for row in roots):
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "bound root shape")
    if contract.get("open_action_ids") != ACTION_IDS:
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "open actions")
    if contract.get("feature_p1_ids") != FEATURE_P1_IDS:
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "feature P1")
    if contract.get("separate_action_ids") != SEPARATE_ACTION_IDS:
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "separate actions")
    if len(contract.get("product_lanes", [])) != 15:
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "product lanes")
    counts = contract.get("canonical_counts", {})
    fixed_counts = {
        "features": 688,
        "predicates": 247,
        "predicate_fixtures": 771,
        "no_go": 150,
        "hard_keywords": 30,
        "contextual_words": 101,
    }
    if (
        set(counts) != {*fixed_counts, "diagnostics", "prelude_entries"}
        or any(counts.get(key) != value for key, value in fixed_counts.items())
        or not isinstance(counts.get("diagnostics"), int)
        or counts.get("diagnostics", 0) < 1250
        or not isinstance(counts.get("prelude_entries"), int)
        or counts.get("prelude_entries", 0) < 49
    ):
        raise GeneratorError("LANGUAGE_COHERENCE_CONTRACT", "canonical counts")
    return contract


def validate_bound_roots(root: Path, contract: dict[str, Any]) -> None:
    for expected in contract["bound_roots"]:
        actual = bound_identity(root, expected["path"])
        if actual != expected:
            raise GeneratorError(
                "LANGUAGE_COHERENCE_BOUND_STATE_DRIFT", expected["path"]
            )


def validate_state(root: Path, pointer: dict[str, Any], contract: dict[str, Any]) -> None:
    version = tomllib.loads(
        safe_path(root, "current/language-version.toml").read_text(encoding="utf-8")
    )
    implementation = safe_path(
        root, "current/implementation-status.yaml"
    ).read_text(encoding="utf-8")
    implementation_revision = REVISION_RE.search(implementation)
    if (
        version.get("language") != "0.1.2-internal"
        or version.get("spec_revision") != REVISION
        or pointer.get("spec_revision") != REVISION
        or pointer.get("previous_pointer") != PREVIOUS_REVISION
        or not implementation_revision
        or implementation_revision.group(1) != REVISION
    ):
        raise GeneratorError("LANGUAGE_COHERENCE_REVISION_PARITY", REVISION)
    if pointer.get("candidate_binding", {}).get("current_binding") is not False:
        raise GeneratorError("LANGUAGE_COHERENCE_CURRENT_BINDING", "must be false")

    lane_ids = contract["product_lanes"]
    expected_lanes = {lane: "NOT_RUN" for lane in lane_ids}
    registry = read_json(
        safe_path(root, "current/product-lanes.json"),
        "LANGUAGE_COHERENCE_PRODUCT_LANES",
    )
    registry_map = {
        row.get("lane_id"): row.get("status") for row in registry.get("lanes", [])
    }
    implementation_map = dict(
        re.findall(
            r"^  ([a-z0-9_]+): (NOT_RUN|BLOCKED|FAILED|PASSED_FOCUSED|PASSED_INTEGRATED|PASSED_INDEPENDENT)$",
            implementation,
            re.MULTILINE,
        )
    )
    if (
        pointer.get("product_lanes") != expected_lanes
        or registry_map != expected_lanes
        or implementation_map != expected_lanes
    ):
        raise GeneratorError(
            "LANGUAGE_COHERENCE_PRODUCT_LANES", "15/15 NOT_RUN parity"
        )

    actions = pointer.get("open_actions", [])
    action_ids = [row.get("id") for row in actions if isinstance(row, dict)]
    if (
        action_ids != ACTION_IDS
        or len(action_ids) != 26
        or len(set(action_ids)) != 26
        or any(row.get("tracking_ref") != f"deeplus-action:{row.get('id')}" for row in actions)
        or any(row.get("priority") != "P1" for row in actions[4:])
        or pointer.get("required_next_reviews") != contract["required_next_reviews"]
    ):
        raise GeneratorError("LANGUAGE_COHERENCE_ACTION_SET", repr(action_ids))

    memory_paths = sorted((root / "roles/current-memory").glob("*.json"))
    if len(memory_paths) != 5:
        raise GeneratorError(
            "LANGUAGE_COHERENCE_ROLE_MEMORY", f"count={len(memory_paths)}"
        )
    for path in memory_paths:
        capsule = read_json(path, "LANGUAGE_COHERENCE_ROLE_MEMORY")
        if capsule.get("source_revision") != REVISION:
            raise GeneratorError("LANGUAGE_COHERENCE_ROLE_MEMORY", path.name)

    if collect_counts(root) != contract["canonical_counts"]:
        raise GeneratorError(
            "LANGUAGE_COHERENCE_CANONICAL_COUNTS", repr(collect_counts(root))
        )


def render_authority(
    root: Path, contract: dict[str, Any]
) -> tuple[bytes, str, list[dict[str, str]]]:
    path = safe_path(root, AUTHORITY_REL)
    text = path.read_text(encoding="utf-8")
    if sha256_bytes(normalize_authority(text).encode("utf-8")) != contract[
        "authority_non_owned_sha256"
    ]:
        raise GeneratorError(
            "LANGUAGE_COHERENCE_AUTHORITY_NONOWNED_DRIFT", AUTHORITY_REL
        )
    observed = [
        {"domain": domain, "path": relative, "owner": owner}
        for domain, relative, owner, _digest in DOMAIN_RE.findall(text)
    ]
    expected = [
        {key: row[key] for key in ("domain", "path", "owner")}
        for row in contract["authority_domains"]
    ]
    if observed != expected:
        raise GeneratorError("LANGUAGE_COHERENCE_AUTHORITY_SHAPE", repr(observed))

    actual: dict[str, str] = {}
    digest_rows = []
    for row in contract["authority_domains"]:
        digest = domain_digest(root, row["path"])
        if digest != row["sha256"]:
            raise GeneratorError(
                "LANGUAGE_COHERENCE_AUTHORITY_DOMAIN_DRIFT", row["domain"]
            )
        actual[row["domain"]] = digest
        digest_rows.append(
            {
                "domain": row["domain"],
                "path": row["path"],
                "sha256": digest,
                "owner": row["owner"],
            }
        )
    aggregate = canonical_sha(digest_rows)

    rendered = REVISION_RE.sub(f"revision: {REVISION}", text, count=1)
    rendered = DOMAIN_RE.sub(
        lambda match: (
            f"  {match.group(1)}:\n"
            f"    path: {match.group(2)}\n"
            f'    owner: "{match.group(3)}"\n'
            f"    sha256: {actual[match.group(1)]}"
        ),
        rendered,
    )
    rendered = AUTHORITY_DIGEST_RE.sub(
        f"authority_digest: {aggregate}", rendered, count=1
    )
    return rendered.encode("utf-8"), aggregate, digest_rows


def render_pointer(
    root: Path, aggregate: str, contract: dict[str, Any]
) -> tuple[bytes, dict[str, Any]]:
    path = safe_path(root, POINTER_REL)
    pointer = read_json(path, "LANGUAGE_COHERENCE_POINTER")
    if not isinstance(pointer, dict):
        raise GeneratorError("LANGUAGE_COHERENCE_POINTER", "not object")
    if normalized_pointer_sha(pointer) != contract[
        "pointer_non_owned_canonical_sha256"
    ]:
        raise GeneratorError("LANGUAGE_COHERENCE_POINTER_NONOWNED_DRIFT", POINTER_REL)
    validate_state(root, pointer, contract)
    pointer["updated_at"] = contract["materialization_timestamp"]
    pointer["authority_digest"] = aggregate
    return json_bytes(pointer), pointer


def render_outputs(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = root.resolve()
    contract = load_contract(root)
    validate_bound_roots(root, contract)
    authority, aggregate, domains = render_authority(root, contract)
    pointer, _ = render_pointer(root, aggregate, contract)
    return {
        AUTHORITY_REL: authority,
        POINTER_REL: pointer,
    }, {
        "revision": REVISION,
        "authority_digest": aggregate,
        "authority_domains": len(domains),
        "bound_roots": len(contract["bound_roots"]),
        "open_actions": 26,
        "feature_p1": 22,
        "separate_actions": 4,
        "product_lanes": "15/15_NOT_RUN",
        "canonical_counts": contract["canonical_counts"],
    }


def refresh_contract(root: Path) -> dict[str, Any]:
    root = root.resolve()
    contract = load_contract(root, relaxed=True)
    authority_text = safe_path(root, AUTHORITY_REL).read_text(encoding="utf-8")
    observed = DOMAIN_RE.findall(authority_text)
    if len(observed) != 11:
        raise GeneratorError("LANGUAGE_COHERENCE_AUTHORITY_SHAPE", "domain count")
    contract["authority_domains"] = [
        {
            "domain": domain,
            "path": relative,
            "owner": owner,
            "sha256": domain_digest(root, relative),
        }
        for domain, relative, owner, _digest in observed
    ]
    contract["authority_non_owned_sha256"] = sha256_bytes(
        normalize_authority(authority_text).encode("utf-8")
    )
    pointer = read_json(safe_path(root, POINTER_REL), "LANGUAGE_COHERENCE_POINTER")
    contract["pointer_non_owned_canonical_sha256"] = normalized_pointer_sha(pointer)
    contract["canonical_counts"] = collect_counts(root)
    bound_paths = [row["path"] for row in contract["bound_roots"]]
    if "docs/grammar-reference" not in bound_paths:
        bound_paths.append("docs/grammar-reference")
    contract["bound_roots"] = [
        bound_identity(root, path) for path in bound_paths
    ]
    contract["migration_identity_exemptions"] = collect_migration_exemptions(root)
    frozen = [
        "spec/grammar/deeplus.ebnf",
        "spec/frontend/frontend-model.json",
        "spec/types/type-system.md",
        "library/prelude/prelude.md",
    ]
    contract["semantic_authority_files"] = [
        {
            "path": relative,
            "sha256": sha256_bytes(safe_path(root, relative).read_bytes()),
        }
        for relative in frozen
    ]
    decisions = read_json(
        safe_path(root, "decisions/language/current-decisions.json"),
        "LANGUAGE_COHERENCE_DECISIONS",
    )
    contract["decision_law_ids"] = [
        row.get("id") for row in decisions.get("laws", []) if isinstance(row, dict)
    ]
    atomic_write(safe_path(root, CONTRACT_REL), json_bytes(contract))
    return contract


def self_test(root: Path) -> dict[str, Any]:
    contract = load_contract(root)
    render_outputs(root)
    cases = []

    grammar_reference_paths = [
        path.relative_to(root).as_posix()
        for path in iter_bound_files(root, safe_path(root, "docs/grammar-reference"))
    ]
    cases.append(
        {
            "case": "portable-bound-path-order",
            "pass": grammar_reference_paths == sorted(grammar_reference_paths),
        }
    )

    bad_bound = copy.deepcopy(contract)
    bad_bound["bound_roots"][0]["sha256"] = "0" * 64
    try:
        validate_bound_roots(root, bad_bound)
        cases.append({"case": "bound-root-mutation", "pass": False})
    except GeneratorError as exc:
        cases.append(
            {
                "case": "bound-root-mutation",
                "pass": exc.code == "LANGUAGE_COHERENCE_BOUND_STATE_DRIFT",
            }
        )

    bad_pointer = copy.deepcopy(contract)
    bad_pointer["pointer_non_owned_canonical_sha256"] = "0" * 64
    try:
        render_pointer(root, "0" * 64, bad_pointer)
        cases.append({"case": "pointer-nonowned-mutation", "pass": False})
    except GeneratorError as exc:
        cases.append(
            {
                "case": "pointer-nonowned-mutation",
                "pass": exc.code == "LANGUAGE_COHERENCE_POINTER_NONOWNED_DRIFT",
            }
        )

    bad_authority = copy.deepcopy(contract)
    bad_authority["authority_non_owned_sha256"] = "0" * 64
    try:
        render_authority(root, bad_authority)
        cases.append({"case": "authority-nonowned-mutation", "pass": False})
    except GeneratorError as exc:
        cases.append(
            {
                "case": "authority-nonowned-mutation",
                "pass": exc.code
                == "LANGUAGE_COHERENCE_AUTHORITY_NONOWNED_DRIFT",
            }
        )
    if not all(row["pass"] for row in cases):
        raise GeneratorError("LANGUAGE_COHERENCE_SELF_TEST", repr(cases))
    return {"tests": len(cases), "passed": len(cases), "cases": cases}


def run(root: Path, mode: str) -> int:
    root = root.resolve()
    if mode == "refresh-contract":
        contract = refresh_contract(root)
        print(
            json.dumps(
                {
                    "schema": "deeplus.language-coherence-contract-refresh-receipt/r1",
                    "result": "PASS",
                    "mode": "REFRESH_CONTRACT",
                    "revision": REVISION,
                    "bound_roots": len(contract["bound_roots"]),
                    "migration_identity_exemptions": len(
                        contract["migration_identity_exemptions"]
                    ),
                    "product_execution": "NOT_RUN",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if mode == "self-test":
        receipt = self_test(root)
        print(
            json.dumps(
                {
                    "schema": "deeplus.language-coherence-integrity-self-test/r1",
                    "result": "PASS",
                    "revision": REVISION,
                    **receipt,
                    "product_execution": "NOT_RUN",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    rendered, detail = render_outputs(root)
    mismatches = [
        relative
        for relative, data in rendered.items()
        if safe_path(root, relative).read_bytes() != data
    ]
    if mode == "check" and mismatches:
        raise GeneratorError(
            "LANGUAGE_COHERENCE_OUTPUT_DRIFT", ", ".join(mismatches)
        )
    if mode == "write":
        for relative in OUTPUTS:
            atomic_write(safe_path(root, relative), rendered[relative])
        second, _ = render_outputs(root)
        if second != rendered:
            raise GeneratorError("LANGUAGE_COHERENCE_NONDETERMINISTIC", "second render")
    print(
        json.dumps(
            {
                "schema": "deeplus.language-coherence-current-integrity-receipt/r1",
                "result": "PASS",
                "mode": mode.upper(),
                **detail,
                "owned_outputs": list(OUTPUTS),
                "source_tree_manifest": "GENERATE_LAST_FROM_EXACT_STAGED_CLEAN_EXPORT",
                "current_binding": False,
                "product_execution": "NOT_RUN",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--refresh-contract", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    mode = (
        "write"
        if args.write
        else "refresh-contract"
        if args.refresh_contract
        else "self-test"
        if args.self_test
        else "check"
    )
    try:
        return run(args.root, mode)
    except (GeneratorError, OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
