#!/usr/bin/env python3
"""Static closure validator for the Deeplus current or candidate workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


REVISION = "r51f3-repository-bootstrap-m1.2"
EXCLUDED_TREE_PARTS = {".git", "target", "dist", "__pycache__"}
EXPECTED = {
    "features": 681, "diagnostics": 1251, "predicates": 245,
    "predicate_fixtures": 763, "examples": 656, "no_go": 150,
    "hard_keywords": 30, "contextual_words": 101,
}


def canonical_sha(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_pointer(value: Any, fragment: str) -> bool:
    if not fragment or fragment == "#":
        return True
    if not fragment.startswith("#/"):
        return False
    current = value
    for raw in fragment[2:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            return False
    return True


def walk_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                refs.append(child)
            refs.extend(walk_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(walk_refs(child))
    return refs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--write-receipt", action="store_true", help="write migration receipt; rebuild source-tree manifest afterward")
    parser.add_argument("--no-receipt", action="store_true", help="deprecated compatibility no-op; validation is read-only by default")
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.candidate and (root / "release/candidate-state.json").is_file() and not (root / "current/current-pointer.json").exists():
        args.candidate = True
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(condition: bool, code: str, detail: str) -> None:
        checks.append({"code": code, "pass": bool(condition), "detail": detail})
        if not condition:
            errors.append(f"{code}: {detail}")

    required = [
        "README.md", "GOVERNANCE.md", "CONTRIBUTING.md", "Cargo.toml",
        "current/authority-map.yaml", "current/implementation-status.yaml",
        "current/language-version.toml", "current/product-lanes.json",
        "spec/language.md", "spec/grammar/deeplus.ebnf",
        "spec/frontend/frontend-model.json", "spec/types/type-system.md",
        "spec/mir/semantics.md", "library/prelude/prelude.md",
        "examples/guide/review-corpus.md", "migration/import-manifest.json",
        "migration/catalog-reassembly.json", "migration/path-aliases.json",
        "migration/m1.1-repair-manifest.json", "release/source-tree-manifest.json",
        "governance/policies/management-policy.yaml",
    ]
    required.append("release/candidate-state.json" if args.candidate else "current/current-pointer.json")
    for rel in required:
        check((root / rel).is_file(), "REQUIRED_PATH", rel)
    check(not (root / ("current/current-pointer.json" if args.candidate else "release/candidate-state.json")).exists(),
          "RELEASE_STATE_EXCLUSIVE", "candidate and published current states are mutually exclusive")

    parsed: dict[Path, Any] = {}
    json_files = sorted(root.rglob("*.json"))
    for path in json_files:
        try:
            parsed[path] = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"JSON_PARSE: {path.relative_to(root)}: {exc}")
    check(len(parsed) == len(json_files), "JSON_CLOSURE", f"{len(parsed)}/{len(json_files)}")
    try:
        tomllib.loads((root / "current/language-version.toml").read_text(encoding="utf-8"))
        tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
        check(True, "TOML_PARSE", "language version and workspace")
    except Exception as exc:  # noqa: BLE001
        check(False, "TOML_PARSE", str(exc))

    archives = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".zip", ".tar", ".gz", ".zst"}]
    check(not archives, "NO_NESTED_ARCHIVES", str(archives))

    repair = parsed.get(root / "migration/m1.1-repair-manifest.json", {})
    changed_paths = {repair.get("human_corpus", {}).get("path")}
    transformations = repair.get("reference_normalization", {}).get("transformations", [])
    changed_paths.update(row.get("path") for row in transformations)
    changed_paths.discard(None)
    for row in transformations:
        path = root / row["path"]
        check(path.is_file() and file_sha(path) == row["output_sha256"], "REPAIR_OUTPUT_IDENTITY", row["path"])

    imported = parsed.get(root / "migration/import-manifest.json", {})
    legacy = imported.get("legacy_files", [])
    check(imported.get("legacy_file_count") == len(legacy) == 86, "IMPORT_FILE_COUNT", str(len(legacy)))
    check(imported.get("semantic_delta") == "NONE; identity/path/configuration migration only", "IMPORT_SEMANTIC_DELTA", str(imported.get("semantic_delta")))
    for entry in legacy:
        for rel in entry.get("current_paths", []):
            target = root / rel
            check(target.exists(), "MIGRATED_PATH_EXISTS", f"{entry['legacy_path']} -> {rel}")
            if target.is_file() and entry["disposition"] != "MIGRATED_SOURCE_SHARDS" and rel not in changed_paths:
                check(file_sha(target) == entry["sha256"], "IMPORT_BYTE_IDENTITY", rel)

    aliases = parsed.get(root / "migration/path-aliases.json", {}).get("aliases", [])
    by_legacy = {row["legacy_path"]: row for row in legacy}
    by_alias = {row["legacy_name"]: row for row in aliases}
    check(len(by_legacy) == len(legacy) and len(by_alias) == len(aliases), "ALIAS_UNIQUENESS", f"legacy={len(by_legacy)} alias={len(by_alias)}")
    check(set(by_legacy) == set(by_alias), "ALIAS_BIJECTION", f"legacy={len(by_legacy)} alias={len(by_alias)}")
    for name in set(by_legacy) & set(by_alias):
        entry, alias = by_legacy[name], by_alias[name]
        check(entry["sha256"] == alias.get("legacy_sha256") and entry.get("current_paths", []) == alias.get("current_paths", []), "ALIAS_IDENTITY", name)
    current_projection_files = [
        path for top in ("spec", "schemas", "tests", "examples", "library", "docs")
        for path in (root / top).rglob("*") if path.is_file()
    ]
    current_projection_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in current_projection_files)
    for alias in aliases:
        if alias.get("resolution") == "stable_path":
            check(alias["legacy_name"] not in current_projection_text, "CURRENT_LEGACY_BASENAME_CLOSURE", alias["legacy_name"])

    reassembly = parsed.get(root / "migration/catalog-reassembly.json", {})
    reconstructed: dict[str, Any] = {}
    all_shards: list[Path] = []
    for contract in reassembly.get("contracts", []):
        metadata = parsed.get(root / contract["metadata_path"])
        rows: list[Any] = []
        for rel in contract.get("ordered_shard_paths", []):
            path = root / rel
            all_shards.append(path)
            check(path.is_file(), "SHARD_PATH_CLOSURE", rel)
            check(path.is_file() and path.stat().st_size <= 61440, "SOURCE_SHARD_SIZE", rel)
            value = parsed.get(path)
            if isinstance(value, list):
                rows.extend(value)
        check(len(rows) == contract.get("row_count"), "SHARD_ROW_COUNT", contract.get("legacy_file", "?"))
        if not isinstance(metadata, dict):
            check(False, "CATALOG_METADATA", contract["metadata_path"])
            continue
        doc = dict(metadata)
        doc[contract["array_key"]] = rows
        check(canonical_sha(doc) == contract.get("canonical_object_sha256"), "CATALOG_OBJECT_IDENTITY", contract["legacy_file"])
        ids = [row.get(contract["id_key"]) for row in rows if isinstance(row, dict) and row.get(contract["id_key"])]
        check(len(ids) == len(set(ids)), "CATALOG_ID_UNIQUENESS", contract["legacy_file"])
        reconstructed[contract["legacy_file"]] = doc
    chunk_files = sorted(root.glob("**/chunks/part-*.json"))
    check(set(chunk_files) == set(all_shards), "SHARD_CONTRACT_COVERAGE", f"actual={len(chunk_files)} declared={len(all_shards)}")
    check(len(reconstructed) == 12, "CATALOG_COUNT", str(len(reconstructed)))

    def rows(name: str, key: str) -> list[dict[str, Any]]:
        return reconstructed.get(name, {}).get(key, [])
    active = rows("deeplus-0.1.2-baseline-r51f3-examples-active-profile-manifest.json", "examples")
    positive = rows("deeplus-0.1.2-baseline-r51f3-surface-smoke-corpus-positive.json", "cases")
    rejected = rows("deeplus-0.1.2-baseline-r51f3-surface-smoke-corpus-rejected.json", "cases")
    gated = rows("deeplus-0.1.2-baseline-r51f3-surface-smoke-corpus-gated.json", "cases")
    counts = Counter(row.get("expected_outcome") for row in active)
    check(counts == Counter({"accept": 363, "reject": 291, "accept_with_gate": 2}), "EXAMPLE_OUTCOME_COUNTS", str(dict(counts)))
    active_ids = {row["example_id"] for row in active}
    partitions = [positive, rejected, gated]
    partition_ids = [row["example_id"] for group in partitions for row in group]
    check(len(partition_ids) == len(set(partition_ids)) and set(partition_ids) == active_ids, "EXAMPLE_PARTITION_EXACT", str([len(group) for group in partitions]))
    active_by_id = {row["example_id"]: row for row in active}
    for row in gated:
        owner = active_by_id.get(row["example_id"], {})
        check(owner.get("expected_outcome") == "accept_with_gate" and owner.get("source_activation") == "explicit_feature_gate" and bool(owner.get("feature_ids")), "GATED_EXAMPLE_LAW", row["example_id"])

    actual = {
        "features": len(rows("deeplus-0.1.2-baseline-r51f3-feature-registry.json", "features")),
        "diagnostics": len(rows("deeplus-0.1.2-baseline-r51f3-diagnostic-registry.json", "diagnostics")),
        "predicates": len(rows("deeplus-0.1.2-baseline-r51f3-checker-predicate-catalog.json", "predicates")),
        "predicate_fixtures": len(rows("deeplus-0.1.2-baseline-r51f3-checker-predicate-fixtures.json", "fixtures")),
        "examples": len(active),
        "no_go": len(rows("deeplus-0.1.2-baseline-r51f3-current-no-go-registry.json", "entries")),
    }
    vocabulary = parsed.get(root / "spec/grammar/keyword-vocabulary.json", {})
    actual["hard_keywords"] = len(vocabulary.get("hard_keywords", []))
    actual["contextual_words"] = len(vocabulary.get("contextual_words", []))
    for key, expected in EXPECTED.items():
        check(actual[key] == expected, "CANONICAL_COUNT", f"{key}={actual[key]} expected={expected}")

    for path, value in parsed.items():
        if not path.is_relative_to(root / "schemas"):
            continue
        for ref in walk_refs(value):
            if ref.startswith(("http://", "https://", "urn:")):
                continue
            file_part, marker, fragment = ref.partition("#")
            target = path if not file_part else (path.parent / file_part).resolve()
            ok = target.is_file() and target in parsed
            check(ok, "LOCAL_JSON_REF_FILE", f"{path.relative_to(root)} -> {ref}")
            if ok and marker:
                check(resolve_pointer(parsed[target], "#" + fragment), "LOCAL_JSON_REF_FRAGMENT", f"{path.relative_to(root)} -> {ref}")

    operational = {
        "examples/manifests/by-outcome/catalog-metadata.json": ("source_file", "examples/guide/review-corpus.md"),
        "examples/manifests/design-gallery.json": ("source_file", "docs/guide/design-gallery.md"),
        "tests/conformance/checker-predicates/catalog-metadata.json": ("fixture_schema", "schemas/language/checker-predicate-fixture-row.schema.json"),
        "tests/fixtures/imported/uml-export-fixtures.json": ("profile_schema", "schemas/language/uml-export-profile.schema.json"),
        "tests/fixtures/imported/deterministic-suite-fixtures.json": ("profile_schema", "schemas/language/deterministic-suite-profile.schema.json"),
    }
    for rel, (field, expected) in operational.items():
        value = parsed.get(root / rel, {})
        check(value.get(field) == expected and (root / expected).exists(), "OPERATIONAL_POINTER", f"{rel}:{field}")

    authority_path = root / "current/authority-map.yaml"
    authority_text = authority_path.read_text(encoding="utf-8")
    domains = re.findall(r'^  ([a-z_]+):\n    path: (\S+)\n    owner: "([^"]+)"\n    sha256: ([0-9a-f]{64})$', authority_text, re.MULTILINE)
    digest_rows = []
    for domain, rel, owner, digest in domains:
        target = root / rel
        check(target.exists(), "AUTHORITY_PATH", rel)
        if target.is_file():
            actual_digest = file_sha(target)
        else:
            material = "\n".join(p.relative_to(root).as_posix() + "\0" + file_sha(p) for p in sorted(target.rglob("*.json"))).encode()
            actual_digest = hashlib.sha256(material).hexdigest()
        check(digest == actual_digest, "AUTHORITY_DOMAIN_IDENTITY", domain)
        digest_rows.append({"domain": domain, "path": rel, "sha256": actual_digest, "owner": owner})
    declared_match = re.search(r"^authority_digest: ([0-9a-f]{64})$", authority_text, re.MULTILINE)
    computed_authority = canonical_sha(digest_rows)
    check(len(domains) == 11 and bool(declared_match) and declared_match.group(1) == computed_authority, "AUTHORITY_AGGREGATE", computed_authority)

    lanes = parsed.get(root / "current/product-lanes.json", {}).get("lanes", [])
    check(len(lanes) == 15 and all(row.get("status") == "NOT_RUN" for row in lanes), "PRODUCT_EVIDENCE_HONESTY", str(len(lanes)))
    if args.candidate:
        state = parsed.get(root / "release/candidate-state.json", {})
        check(state.get("candidate_revision") == REVISION and state.get("authority_digest") == computed_authority and state.get("current_pointer_published") is False, "CANDIDATE_STATE", str(state.get("candidate_revision")))
    else:
        pointer = parsed.get(root / "current/current-pointer.json", {})
        allowed = {"schema", "updated_at", "language_version", "spec_revision", "source_revision", "authority_digest", "source_snapshot", "product_lanes", "open_actions", "required_next_reviews", "previous_pointer"}
        check(set(pointer) <= allowed and pointer.get("schema") == "deeplus.current-pointer/v1", "POINTER_CLOSED_SHAPE", str(sorted(set(pointer) - allowed)))
        source_revision = pointer.get("source_revision", {})
        check(source_revision.get("kind") in {"git-commit", "git-tag", "legacy-import"} and bool(source_revision.get("value")), "POINTER_SOURCE_REVISION", str(source_revision))
        snapshot = pointer.get("source_snapshot")
        check(snapshot is None or (set(snapshot) == {"library_file_id", "sha256"} and bool(re.fullmatch(r"[0-9a-f]{64}", snapshot.get("sha256", "")))), "POINTER_SOURCE_SNAPSHOT", str(snapshot))
        check(pointer.get("previous_pointer") is None or isinstance(pointer.get("previous_pointer"), str), "POINTER_PREVIOUS", str(pointer.get("previous_pointer")))
        check(pointer.get("spec_revision") == REVISION and pointer.get("authority_digest") == computed_authority, "POINTER_AUTHORITY", str(pointer.get("spec_revision")))
        check(all(value == "NOT_RUN" for value in pointer.get("product_lanes", {}).values()), "POINTER_PRODUCT_EVIDENCE", str(pointer.get("product_lanes")))

    language = (root / "spec/language.md").read_text(encoding="utf-8")
    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    check("| `*` | call-side positional unfold" in language and 'PositionalUnfoldArgument ::= "*" Expr ;' in grammar, "POSITIONAL_UNFOLD_OWNER", "* in spec and grammar")
    check("repeated positional parameter/type residue and positional unfold" not in language, "POSITIONAL_UNFOLD_NO_ELLIPSIS", "... is not call-side unfold")
    probes = ["options***: Record", "Record***", "**options", "let#lazy", "sealed class"]
    for probe in probes:
        check(probe in language, "CURRENT_SURFACE_PROBE", probe)
    check('Identifier "***" TypeAnnotation' in grammar, "NAMED_REST_GRAMMAR", "***")

    instruction_chars = len((root / "governance/project-instructions.txt").read_text(encoding="utf-8"))
    check(instruction_chars <= 8000, "PROJECT_INSTRUCTION_LIMIT", str(instruction_chars))
    memories = sorted((root / "roles/current-memory").glob("*.json"))
    check(len(memories) == 5, "ROLE_MEMORY_COUNT", str(len(memories)))
    for path in memories:
        capsule = parsed.get(path, {})
        check(len(capsule.get("current_facts", [])) <= 50 and len(capsule.get("open_actions", [])) <= 30 and len(capsule.get("watch_items", [])) <= 20 and path.stat().st_size <= 102400, "ROLE_MEMORY_CAP", path.name)

    crates = sorted(path for path in (root / "crates").iterdir() if path.is_dir())
    check(len(crates) == 15, "CRATE_BOUNDARY_COUNT", str(len(crates)))
    for crate in crates:
        check((crate / "Cargo.toml").is_file() and bool(list((crate / "src").glob("*.rs"))), "CRATE_SCAFFOLD", crate.name)
    manifest = parsed.get(root / "release/source-tree-manifest.json", {})
    listed = manifest.get("files", [])
    actual_files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and not any(part in EXCLUDED_TREE_PARTS for part in p.relative_to(root).parts)
        and p.relative_to(root).as_posix() != "release/source-tree-manifest.json"
    )
    listed_map = {row["path"]: row for row in listed}
    check(set(listed_map) == {p.relative_to(root).as_posix() for p in actual_files}, "SOURCE_TREE_MEMBERSHIP", f"listed={len(listed_map)} actual={len(actual_files)}")
    for path in actual_files:
        rel = path.relative_to(root).as_posix()
        row = listed_map.get(rel, {})
        check(row.get("sha256") == file_sha(path) and row.get("bytes") == path.stat().st_size, "SOURCE_TREE_FILE_IDENTITY", rel)
    tree_material = "\n".join(f"{row['path']}\0{row['sha256']}" for row in sorted(listed, key=lambda x: x["path"])).encode()
    check(manifest.get("revision") == REVISION and manifest.get("tree_sha256") == hashlib.sha256(tree_material).hexdigest(), "SOURCE_TREE_AGGREGATE", str(manifest.get("tree_sha256")))

    result = "PASS" if not errors else "FAIL"
    receipt = {
        "schema": "deeplus.canonical-workspace-validation-receipt/v1.1",
        "revision": REVISION, "mode": "candidate" if args.candidate else "published-current",
        "result": result, "evidence_level": "E2_STATIC_CLOSURE",
        "checks": len(checks), "passed": sum(row["pass"] for row in checks),
        "failed": sum(not row["pass"] for row in checks), "canonical_counts": actual,
        "json_files_parsed": len(parsed), "legacy_files_accounted": len(legacy),
        "catalogs_reassembled": len(reconstructed), "rust_scaffold_crates": len(crates),
        "product_execution": "NOT_RUN", "warnings": warnings, "errors": errors,
        "evidence_honesty": "Static closure does not establish lexer, parser, checker, MIR, xVM, LLVM, tooling, conformance, or user-study product support.",
    }
    if args.write_receipt:
        write_json(root / "migration/migration-receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
