#!/usr/bin/env python3
"""One-time, deterministic R51f3 import into stable Deeplus workspace paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any


BASELINE = "0.1.2-baseline.r51f3"
REVISION = "r51f3-migration-m1"
PREFIX = "deeplus-0.1.2-baseline-r51f3-"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_object_sha(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(encoded)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_id(value: Any, row: Any) -> str:
    raw = str(value or "row").strip()
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip(".-") or "row"
    if len(cleaned) > 140:
        cleaned = cleaned[:120] + "-" + canonical_object_sha(row)[:12]
    return cleaned


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--management", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()

    legacy = args.legacy.resolve()
    management = args.management.resolve()
    dst = args.destination.resolve()
    if not legacy.is_dir() or not management.is_dir() or not dst.is_dir():
        raise SystemExit("legacy, management, and destination must be existing directories")

    dispositions: dict[str, dict[str, Any]] = {}
    for source in sorted(legacy.iterdir()):
        if source.is_file():
            data = source.read_bytes()
            dispositions[source.name] = {
                "legacy_path": source.name,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
                "disposition": "ARCHIVE_ONLY_IMPORT_PROVENANCE",
                "current_paths": [],
            }

    def mark(old: str, disposition: str, target: Path) -> None:
        entry = dispositions[old]
        entry["disposition"] = disposition
        path = relative(target, dst)
        if path not in entry["current_paths"]:
            entry["current_paths"].append(path)

    def copy(old: str, new: str, disposition: str = "MIGRATED_STABLE_PATH") -> Path:
        source = legacy / old
        target = dst / new
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        mark(old, disposition, target)
        return target

    authority_map = {
        "Deeplus_0_1_2_Baseline_R51f3_Fully_Merged_Current_Canonical.md": "spec/language.md",
        "Deeplus_0_1_2_R51f3_Design_Gallery.md": "docs/guide/design-gallery.md",
        "Deeplus_0_1_2_R51f3_Example_Review_Corpus.md": "examples/guide/review-corpus.md",
        "Deeplus_Frontend_Model_0_1_2_R51f3_Current_Canonical.json": "spec/frontend/frontend-model.json",
        "Deeplus_Grammar_0_1_2_R51f3_Current_Canonical.ebnf": "spec/grammar/deeplus.ebnf",
        "Deeplus_Grammar_0_1_2_R51f3_Implementation_Contract.md": "docs/internals/grammar-implementation-contract.md",
        "Deeplus_Operational_Semantics_0_1_2_R51f3_Fully_Merged.md": "spec/mir/semantics.md",
        "Deeplus_Prelude_0_1_2_R51f3_Fully_Merged.md": "library/prelude/prelude.md",
        "Deeplus_TypeSystem_0_1_2_RCTS_V5_TS_R45_R51f3_Fully_Merged.md": "spec/types/type-system.md",
    }
    for old, new in authority_map.items():
        copy(old, new)

    split_contracts: list[dict[str, Any]] = []

    def split_object(
        old: str,
        array_key: str,
        id_key: str,
        root: str,
        partition_key: str | None = None,
    ) -> None:
        doc = json.loads((legacy / old).read_text(encoding="utf-8"))
        rows = doc[array_key]
        metadata = {key: value for key, value in doc.items() if key != array_key}
        target_root = dst / root
        if target_root.exists():
            for stale in target_root.rglob("*.json"):
                stale.unlink()
        write_json(target_root / "catalog-metadata.json", metadata)
        mark(old, "MIGRATED_SOURCE_SHARDS", target_root / "catalog-metadata.json")
        ordered_shard_paths: list[str] = []
        chunks: list[list[Any]] = []
        current_chunk: list[Any] = []
        for row in rows:
            candidate = current_chunk + [row]
            encoded = (json.dumps(candidate, ensure_ascii=False, indent=2) + "\n").encode()
            if current_chunk and len(encoded) > 61440:
                chunks.append(current_chunk)
                current_chunk = [row]
            else:
                current_chunk = candidate
        if current_chunk:
            chunks.append(current_chunk)
        for index, chunk in enumerate(chunks, start=1):
            shard_path = target_root / "chunks" / f"part-{index:04d}.json"
            write_json(shard_path, chunk)
            ordered_shard_paths.append(relative(shard_path, dst))
        split_contracts.append(
            {
                "legacy_file": old,
                "array_key": array_key,
                "id_key": id_key,
                "partition_key": partition_key,
                "shard_encoding": "ordered_json_arrays_max_61440_bytes",
                "shard_root": root,
                "metadata_path": f"{root}/catalog-metadata.json",
                "row_count": len(rows),
                "ordered_shard_paths": ordered_shard_paths,
                "canonical_object_sha256": canonical_object_sha(doc),
            }
        )

    split_object(
        f"{PREFIX}feature-registry.json", "features", "feature_id",
        "spec/features/catalog", "status_enum"
    )
    split_object(
        f"{PREFIX}diagnostic-registry.json", "diagnostics", "diagnostic_id",
        "spec/diagnostics/catalog", "stage"
    )
    split_object(
        f"{PREFIX}checker-predicate-catalog.json", "predicates", "predicate_id",
        "spec/types/predicates", "predicate_maturity"
    )
    split_object(
        f"{PREFIX}checker-predicate-fixtures.json", "fixtures", "fixture_id",
        "tests/conformance/checker-predicates", "expected"
    )
    split_object(
        f"{PREFIX}current-no-go-registry.json", "entries", "rejection_id",
        "spec/compatibility/no-go", "recognition_stage"
    )
    split_object(
        f"{PREFIX}examples-active-profile-manifest.json", "examples", "example_id",
        "examples/manifests/by-outcome", "expected_outcome"
    )
    split_object(
        f"{PREFIX}surface-smoke-corpus-positive.json", "cases", "example_id",
        "tests/conformance/surface/positive"
    )
    split_object(
        f"{PREFIX}surface-smoke-corpus-rejected.json", "cases", "example_id",
        "tests/conformance/surface/rejected"
    )
    split_object(
        f"{PREFIX}surface-smoke-corpus-gated.json", "cases", "example_id",
        "tests/conformance/surface/gated"
    )
    split_object(
        f"{PREFIX}feature-dependency-edge-registry.json", "edges", "edge_id",
        "spec/features/dependencies"
    )
    split_object(
        f"{PREFIX}diagnostic-relation-registry.json", "relations", "relation_id",
        "spec/diagnostics/relations"
    )
    split_object(
        f"{PREFIX}prelude-signature-catalog.json", "entries", "entry_id",
        "library/prelude/signatures"
    )

    direct_json = {
        f"{PREFIX}keyword-vocabulary.json": "spec/grammar/keyword-vocabulary.json",
        f"{PREFIX}feature-gate-map.json": "spec/features/gates.json",
        f"{PREFIX}ratified-decision-ledger.json": "decisions/language/current-decisions.json",
        f"{PREFIX}product-lane-registry.json": "current/product-lanes.json",
        f"{PREFIX}normative-terminology-contract.json": "spec/contracts/normative-terminology.json",
        f"{PREFIX}source-role-contract.json": "spec/contracts/source-roles.json",
        f"{PREFIX}tooling-and-profile-contracts.json": "spec/contracts/tooling-and-profiles.json",
        f"{PREFIX}proof-r2-tooling-contract.json": "spec/contracts/proof-r2-tooling.json",
        f"{PREFIX}provider-derive-via-contract.json": "spec/contracts/provider-derive-via.json",
        f"{PREFIX}quarantine-scope-design-contract.json": "spec/contracts/quarantine-scope.json",
        f"{PREFIX}constitutional-law-catalog.json": "spec/contracts/constitutional-laws.json",
        f"{PREFIX}rcts-v5-nominal-relation-registry.json": "spec/types/rcts-v5-nominal-relations.json",
        f"{PREFIX}design-gallery-manifest.json": "examples/manifests/design-gallery.json",
    }
    for old, new in direct_json.items():
        copy(old, new)

    handled = set(authority_map) | set(direct_json)
    handled |= {contract["legacy_file"] for contract in split_contracts}
    for source in sorted(legacy.glob("*.schema.json")):
        if source.name in handled:
            continue
        short = source.name[len(PREFIX):] if source.name.startswith(PREFIX) else source.name
        copy(source.name, f"schemas/language/{short}", "MIGRATED_SCHEMA")
        handled.add(source.name)
    for source in sorted(legacy.glob("*-schema.json")):
        if source.name in handled:
            continue
        short = source.name[len(PREFIX):] if source.name.startswith(PREFIX) else source.name
        copy(source.name, f"schemas/language/{short}", "MIGRATED_SCHEMA")
        handled.add(source.name)
    for source in sorted(legacy.glob("*fixtures.json")):
        if source.name in handled:
            continue
        short = source.name[len(PREFIX):] if source.name.startswith(PREFIX) else source.name
        copy(source.name, f"tests/fixtures/imported/{short}", "MIGRATED_TEST_FIXTURE")
        handled.add(source.name)

    for name, entry in dispositions.items():
        if name.endswith(".py"):
            entry["disposition"] = "SUPERSEDED_BY_WORKSPACE_VALIDATORS"
        elif name in handled:
            pass
        elif any(token in name for token in ("matrix", "crosswalk", "stage-map", "normalization-map", "disposition-registry", "block-manifest", "coverage")):
            entry["disposition"] = "ARCHIVE_ONLY_GENERATED_PROJECTION"

    management_copies = {
        "Deeplus_Project_Instructions_R1_1.txt": "governance/project-instructions.txt",
        "Design_Deeplus_Development_and_Governance_System_R1.md": "governance/reports/development-and-governance.md",
        "Design_Deeplus_Configuration_Management_and_Artifact_Lifecycle_R1.md": "governance/reports/configuration-management.md",
        "Design_Deeplus_Role_Operating_Model_R1.md": "governance/reports/role-operating-model.md",
        "Design_Deeplus_Management_R1_1_Prompt_and_Project_Settings_Amendment.md": "governance/reports/project-settings-amendment.md",
        "config/Design_Deeplus_Management_Policy_R1.yaml": "governance/policies/management-policy.yaml",
    }
    for old, new in management_copies.items():
        target = dst / new
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(management / old, target)
    for folder, target_folder in (("prompts", "roles/prompts"), ("templates", "governance/templates"), ("schemas", "schemas/governance")):
        for source in sorted((management / folder).glob("*")):
            if source.is_file():
                target = dst / target_folder / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    source_index = {
        "schema": "deeplus.r51f3-import-manifest/v1",
        "source_baseline": BASELINE,
        "target_revision": REVISION,
        "semantic_delta": "NONE; identity/path/configuration migration only",
        "legacy_file_count": len(dispositions),
        "legacy_files": [dispositions[name] for name in sorted(dispositions)],
    }
    write_json(dst / "migration/import-manifest.json", source_index)
    write_json(
        dst / "migration/catalog-reassembly.json",
        {
            "schema": "deeplus.catalog-reassembly/v1",
            "source_baseline": BASELINE,
            "contracts": split_contracts,
        },
    )
    aliases = []
    for name in sorted(dispositions):
        entry = dispositions[name]
        aliases.append(
            {
                "legacy_name": name,
                "resolution": "stable_path" if entry["current_paths"] else "immutable_import_provenance",
                "current_paths": entry["current_paths"],
                "legacy_sha256": entry["sha256"],
            }
        )
    write_json(
        dst / "migration/path-aliases.json",
        {"schema": "deeplus.import-path-aliases/v1", "source_baseline": BASELINE, "aliases": aliases},
    )

    authority_specs = [
        ("human_language", "spec/language.md", "Spec_"),
        ("exact_grammar", "spec/grammar/deeplus.ebnf", "Spec_"),
        ("frontend_admission", "spec/frontend/frontend-model.json", "Spec_ + Impl_"),
        ("type_system", "spec/types/type-system.md", "Spec_"),
        ("mir_observable_semantics", "spec/mir/semantics.md", "Spec_ + Impl_"),
        ("prelude", "library/prelude/prelude.md", "Devel_ + Spec_"),
        ("examples", "examples/guide/review-corpus.md", "Devel_ + Test_"),
        ("current_decisions", "decisions/language/current-decisions.json", "Design_ + Spec_"),
        ("features", "spec/features/catalog", "Spec_"),
        ("diagnostics", "spec/diagnostics/catalog", "Test_ + Spec_"),
        ("checker_predicates", "spec/types/predicates", "Spec_ + Impl_"),
    ]
    digest_rows = []
    yaml_lines = ["schema: deeplus.authority-map/v1", f"revision: {REVISION}", "domains:"]
    for domain, path, owner in authority_specs:
        target = dst / path
        if target.is_file():
            digest = sha256_bytes(target.read_bytes())
        else:
            parts = []
            for file in sorted(target.rglob("*.json")):
                parts.append(relative(file, dst) + "\0" + sha256_bytes(file.read_bytes()))
            digest = sha256_bytes("\n".join(parts).encode())
        digest_rows.append({"domain": domain, "path": path, "sha256": digest, "owner": owner})
        yaml_lines.extend([
            f"  {domain}:", f"    path: {path}", f"    owner: \"{owner}\"", f"    sha256: {digest}"
        ])
    authority_digest = canonical_object_sha(digest_rows)
    yaml_lines.extend([
        "conflict_resolution:",
        "  - approved_current_decision",
        "  - domain_edit_authority",
        "  - generated_projection",
        "  - execution_receipt_for_implementation_claim_only",
        f"authority_digest: {authority_digest}",
    ])
    (dst / "current/authority-map.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")
    (dst / "current/decision-index.yaml").write_text(
        "schema: deeplus.decision-index/v1\nrevision: r51f3-migration-m1\ncurrent:\n"
        "  - path: decisions/language/current-decisions.json\n"
        "    authority: imported_current_decisions\n"
        "implementation: []\ngovernance:\n  - governance/policies/management-policy.yaml\n",
        encoding="utf-8",
    )
    lane_doc = json.loads((dst / "current/product-lanes.json").read_text(encoding="utf-8"))
    lanes = {row["lane_id"]: row["status"] for row in lane_doc["lanes"]}
    write_json(
        dst / "current/current-pointer.json",
        {
            "schema": "deeplus.current-pointer/v1",
            "updated_at": "2026-07-15T00:00:00+09:00",
            "language_version": "0.1.2-internal",
            "spec_revision": REVISION,
            "source_revision": {"kind": "migration", "value": BASELINE, "repository": "Deeplus_Canonical_Workspace"},
            "authority_digest": authority_digest,
            "source_snapshot": "Deeplus_Canonical_Workspace_0_1_2_R51f3_Migration_M1_Source.zip",
            "product_lanes": lanes,
            "open_actions": [
                {"id": "MIG-M1-A001", "priority": "P1", "summary": "Obtain five mandatory role reviews for the migrated workspace", "owner": "Design_"},
                {"id": "MIG-M1-A002", "priority": "P1", "summary": "Implement and receipt the first Rust lexer/parser vertical slice", "owner": "Impl_"},
            ],
            "required_next_reviews": [
                "Design_ integrated migration and release review",
                "Spec_ authority-map and source-shard review",
                "Impl_ crate boundary and vertical-slice review",
                "Test_ import closure and gate review",
                "Devel_ human documentation and example navigation review",
                "Archive_ configuration-integrity auxiliary review",
            ],
            "previous_pointer": {"kind": "legacy-release", "value": BASELINE},
        },
    )
    print(json.dumps({
        "status": "PASS",
        "legacy_files": len(dispositions),
        "split_catalogs": len(split_contracts),
        "authority_digest": authority_digest,
        "semantic_delta": "NONE",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
