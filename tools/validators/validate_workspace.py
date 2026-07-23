#!/usr/bin/env python3
"""Static closure validator for the Deeplus current or candidate workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 and earlier
    import tomli as tomllib
from collections import Counter
from pathlib import Path
from typing import Any


LEGACY_REVISION = "r51f3-current-publication-m1.3"
POST_PR16_REVISION = "r51f3-post-pr16-preview-design-r4-cma-r1"
LANGUAGE_COHERENCE_REVISION = "r51f3-current-enum-derived-capabilities-r1"
PREVIOUS_LANGUAGE_COHERENCE_REVISION = "r51f3-current-type-refinement-narrowing-coherence-r1"
LANGUAGE_COHERENCE_CONTRACT_REL = (
    "spec/contracts/language-coherence-current-integrity-r1.json"
)
EXCLUDED_TREE_PARTS = {".git", "target", "dist", "__pycache__"}
EXPECTED = {
    "features": 681, "diagnostics": 1250, "predicates": 245,
    "predicate_fixtures": 763, "no_go": 150,
    "hard_keywords": 30, "contextual_words": 101,
}
REQUIRED_FEATURE_IDS = (
    "named_rest_parameter_record_msp",
    "schema_named_unfolding",
    "unicode_char_literal_single_quote_msp",
    "char_unicode_scalar_value_model",
    "strict_boolean_word_operators_msp",
    "sequential_boolean_control_words_msp",
    "standalone_bang_not_current_not_word_law",
    "rightward_flow_dollar_local_binding_msp",
    "optional_chaining_not_current_law",
    "ternary_conditional_expression",
    "ternary_short_expression_stable_profile",
    "at_control_expression_family",
    "local_value_body_msp",
    "match_exhaustiveness_phase_a",
    "match_arm_guard_msp",
    "bytes_literal_hash_bytes_msp",
    "string_interpolation_braced_expr_core",
    "string_interpolation_format_spec_core",
    "string_interpolation_shorthand_factor_msp",
    "numeric_array_postfix_transpose_caret_msp",
)
MIR_DISPOSITIONS = {
    "named_rest_parameter_record_msp": "LAW_PRESENT",
    "schema_named_unfolding": "GENERIC_LAW_PRESENT",
    "unicode_char_literal_single_quote_msp": "LAW_PRESENT",
    "char_unicode_scalar_value_model": "LAW_PRESENT",
    "strict_boolean_word_operators_msp": "LAW_PRESENT",
    "sequential_boolean_control_words_msp": "LAW_PRESENT",
    "standalone_bang_not_current_not_word_law": "NO_DISTINCT_MIR_OP",
    "rightward_flow_dollar_local_binding_msp": "LAW_PRESENT",
    "optional_chaining_not_current_law": "NOT_APPLICABLE(rejected current surface)",
    "ternary_conditional_expression": "DEFERRED_PRODUCT_HANDOFF",
    "ternary_short_expression_stable_profile": "DEFERRED_PRODUCT_HANDOFF",
    "at_control_expression_family": "GENERIC_LAW_PRESENT",
    "local_value_body_msp": "NO_DISTINCT_MIR_OP",
    "match_exhaustiveness_phase_a": "NOT_APPLICABLE(checker-only rejection before MIR)",
    "match_arm_guard_msp": "GENERIC_LAW_PRESENT",
    "bytes_literal_hash_bytes_msp": "LAW_PRESENT",
    "string_interpolation_braced_expr_core": "DEFERRED_PRODUCT_HANDOFF",
    "string_interpolation_format_spec_core": "DEFERRED_PRODUCT_HANDOFF",
    "string_interpolation_shorthand_factor_msp": "DEFERRED_PRODUCT_HANDOFF",
    "numeric_array_postfix_transpose_caret_msp": "DEFERRED_PRODUCT_HANDOFF",
}
SUPPLEMENTAL_MIR_FEATURE_IDS = (
    "no_string_char_bytes_implicit_conversion_law",
    "text_model_char_grapheme_current_law",
)
MATCH_GUARD_FIXIT = "combine predicates into one Bool guard or remove the extra guard"
FROZEN_UNCHANGED_SEMANTIC_HASHES = {
    "spec/grammar/deeplus.ebnf": "c844f1422b17001d279e7eeb897ad320dd780513de0b93297c986cec69916c72",
    "spec/frontend/frontend-model.json": "8dc54dca8bc16b22fe07824260c193d5da43b449cc408535290dd420f1bf53bb",
    "spec/types/type-system.md": "17ac6b139b0ffc422b091ef97ba900fe9f028400034f3e73534bb5d6c1fdae4a",
    "library/prelude/prelude.md": "41d4bdefb110dd4c648b986cca2a4b3ef26760d1f0ced321d4e6d0ce05249a8f",
}
EXPECTED_POINTER_KEYS = {
    "schema", "updated_at", "language_version", "spec_revision",
    "publication_authority_source", "audited_implementation_baseline",
    "candidate_binding", "authority_digest", "source_snapshot",
    "product_lanes", "open_actions", "required_next_reviews",
    "previous_pointer",
}
EXPECTED_NEXT_REVIEWS = [
    "M13-A002: Impl_ + Spec_ + Test_",
    "M13-A003: Design_ + Legal_",
    "M13-A004: Build_",
    "M13-A005: Design_ + Spec_ + Devel_",
]
EXPECTED_ACTION_IDS = ["M13-A002", "M13-A003", "M13-A004", "M13-A005"]
SUCCESSOR_ACTION_IDS = EXPECTED_ACTION_IDS + [
    *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
    *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
    *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
    "SFD-P1-009",
]
POST_PR16_CANONICAL_DELTA_PATHS = {
    "spec/language.md",
    "spec/frontend/frontend-model.json",
    "spec/types/type-system.md",
    "spec/mir/semantics.md",
    "decisions/language/current-decisions.json",
    "library/prelude/prelude.md",
    "examples/guide/review-corpus.md",
    "examples/manifests/by-outcome/catalog-metadata.json",
    *(f"examples/manifests/by-outcome/chunks/part-{index:04d}.json" for index in range(5, 15)),
    "tests/conformance/surface/rejected/catalog-metadata.json",
    "tests/conformance/surface/rejected/chunks/part-0001.json",
    "tests/conformance/surface/rejected/chunks/part-0002.json",
    "library/prelude/signatures/catalog-metadata.json",
    "library/prelude/signatures/chunks/part-0001.json",
    "spec/diagnostics/catalog/catalog-metadata.json",
    "spec/diagnostics/catalog/chunks/part-0011.json",
    "spec/diagnostics/relations/catalog-metadata.json",
    "spec/diagnostics/relations/chunks/part-0001.json",
    "spec/features/catalog/chunks/part-0002.json",
    "spec/features/catalog/chunks/part-0004.json",
    "spec/features/catalog/chunks/part-0018.json",
    "spec/types/predicates/chunks/part-0004.json",
}
EXPR_AUTHORITY = "governance/policies/management-policy.yaml#EXPR-001"
EXPR_DIGEST = "42250c554d2d5f9cfb29bbd3668bed40ec1390fce658ac1804f7c6de29b1ac39"
EXPR_FIELDS = {
    "clause_id": "EXPR-001",
    "statement": "Expressiveness means translating programmer intent easily, consistently, and responsibly.",
    "restriction_rule": "A restriction must provide an expression-preserving alternative or state an explicit impossibility case.",
    "visibility_rule": "Responsibility, ownership, effects, failure, cleanup, suspension, authority, provider lookup, call domain, and public API residue remain visible.",
}
EXPR_TEXT_CONSUMERS = [
    "roles/prompts/Deeplus_Shared_Work_Role_Charter_Prompt.txt",
    "roles/prompts/Design_Deeplus_Design_and_Release_Steward_Prompt.txt",
    "roles/prompts/Spec_Deeplus_Language_and_Type_System_Architect_Prompt.txt",
    "roles/prompts/Impl_Deeplus_Compiler_and_Runtime_Lead_Prompt.txt",
    "roles/prompts/Test_Deeplus_Conformance_and_Quality_Lead_Prompt.txt",
    "roles/prompts/Devel_Deeplus_Developer_Experience_and_Ecosystem_Lead_Prompt.txt",
    "governance/templates/Design_Deeplus_RFC_Template.md",
    "governance/templates/Design_Deeplus_ADR_Template.md",
]


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


def scalar_occurrences(value: Any, needle: str) -> int:
    if isinstance(value, dict):
        return sum(scalar_occurrences(child, needle) for child in value.values())
    if isinstance(value, list):
        return sum(scalar_occurrences(child, needle) for child in value)
    return int(value == needle)


def longest_exact_indent_prefix(lines: list[str]) -> str:
    prefixes: list[str] = []
    for line in lines:
        if not isinstance(line, str):
            return "\0INVALID"
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        if line[len(prefix):]:
            prefixes.append(prefix)
    if not prefixes:
        return ""
    common = prefixes[0]
    for prefix in prefixes[1:]:
        limit = min(len(common), len(prefix))
        index = 0
        while index < limit and common[index] == prefix[index]:
            index += 1
        common = common[:index]
    return common


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

    try:
        revision = tomllib.loads(
            (root / "current/language-version.toml").read_text(encoding="utf-8")
        )["spec_revision"]
    except Exception as exc:  # noqa: BLE001
        revision = ""
        check(False, "REVISION_PARITY", str(exc))
    check(
        revision
        in {LEGACY_REVISION, POST_PR16_REVISION, LANGUAGE_COHERENCE_REVISION},
        "REVISION_PARITY",
        revision,
    )

    language_coherence_contract: dict[str, Any] = {}
    if revision == LANGUAGE_COHERENCE_REVISION:
        try:
            language_coherence_contract = json.loads(
                (root / LANGUAGE_COHERENCE_CONTRACT_REL).read_text(
                    encoding="utf-8"
                )
            )
            fixed_counts = language_coherence_contract.get("canonical_counts", {})
            check(
                language_coherence_contract.get("schema")
                == "deeplus.language-coherence-current-integrity-contract/r1"
                and language_coherence_contract.get("revision") == revision
                and fixed_counts.get("features") == 684
                and fixed_counts.get("predicates") == 245
                and fixed_counts.get("predicate_fixtures") == 764
                and fixed_counts.get("no_go") == 150
                and fixed_counts.get("hard_keywords") == 30
                and fixed_counts.get("contextual_words") == 101,
                "LANGUAGE_COHERENCE_CONTRACT",
                str(fixed_counts),
            )
        except Exception as exc:  # noqa: BLE001
            check(False, "LANGUAGE_COHERENCE_CONTRACT", str(exc))

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
        "tools/generators/generate_example_projections.py",
        "tools/generators/example-projections.contract.json",
        "tools/validators/run_example_projection_generator_tests.py",
        "tools/generators/generate_current_integrity.py",
        "tools/generators/current-integrity.contract.json",
        "tools/validators/run_current_integrity_generator_tests.py",
        "migration/current-document-consistency-repair-r2.3-manifest.json",
        "governance/policies/management-policy.yaml",
        "release/evidence/current-publication-m1.3-source-snapshot-receipt.json",
        "release/evidence/current-publication-m1.3-predecessor-receipt.json",
        "release/evidence/current-publication-m1.3-git-binding-receipt.json",
        "release/evidence/current-publication-m1.3-role-review-index.json",
    ]
    if revision == POST_PR16_REVISION:
        required.extend([
            "tools/generators/generate_post_pr16_current_integrity.py",
            "tools/generators/post-pr16-current-integrity.contract.json",
            "tools/validators/run_post_pr16_current_integrity_tests.py",
        ])
    elif revision == LANGUAGE_COHERENCE_REVISION:
        required.extend([
            "tools/generators/generate_language_coherence_current_integrity.py",
            LANGUAGE_COHERENCE_CONTRACT_REL,
        ])
    required.append("release/candidate-state.json" if args.candidate else "current/current-pointer.json")
    for rel in required:
        check((root / rel).is_file(), "REQUIRED_PATH", rel)
    check(not (root / ("current/current-pointer.json" if args.candidate else "release/candidate-state.json")).exists(),
          "RELEASE_STATE_EXCLUSIVE", "candidate and published current states are mutually exclusive")

    generator = root / "tools/generators/generate_example_projections.py"
    if generator.is_file():
        process = subprocess.run(
            [sys.executable, str(generator), "--root", str(root), "--check"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        detail = process.stdout.strip() if process.returncode == 0 else process.stderr.strip()
        check(
            process.returncode == 0,
            "EXAMPLE_PROJECTION_GENERATOR_CHECK",
            detail[-2000:],
        )

    if revision == LANGUAGE_COHERENCE_REVISION:
        current_integrity_generator_rel = (
            "tools/generators/generate_language_coherence_current_integrity.py"
        )
    elif revision == POST_PR16_REVISION:
        current_integrity_generator_rel = (
            "tools/generators/generate_post_pr16_current_integrity.py"
        )
    else:
        current_integrity_generator_rel = (
            "tools/generators/generate_current_integrity.py"
        )
    current_integrity_generator = root / current_integrity_generator_rel
    if current_integrity_generator.is_file():
        process = subprocess.run(
            [
                sys.executable,
                str(current_integrity_generator),
                "--root",
                str(root),
                "--check",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        detail = process.stdout.strip() if process.returncode == 0 else (
            process.stderr.strip() or process.stdout.strip()
        )
        check(
            process.returncode == 0,
            "CURRENT_INTEGRITY_GENERATOR_CHECK",
            detail[-4000:],
        )
        if revision == LANGUAGE_COHERENCE_REVISION:
            mutation_process = subprocess.run(
                [
                    sys.executable,
                    str(current_integrity_generator),
                    "--root",
                    str(root),
                    "--self-test",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            mutation_detail = (
                mutation_process.stdout.strip()
                if mutation_process.returncode == 0
                else mutation_process.stderr.strip()
                or mutation_process.stdout.strip()
            )
            check(
                mutation_process.returncode == 0,
                "CURRENT_INTEGRITY_GENERATOR_MUTATION_CHECK",
                mutation_detail[-4000:],
            )

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

    integrity_contract = parsed.get(
        root / "tools/generators/current-integrity.contract.json", {}
    )
    current_delta = parsed.get(
        root / "migration/current-document-consistency-repair-r2.3-manifest.json", {}
    )
    contract_transitions = integrity_contract.get("historical_transitions", [])
    delta_transitions = current_delta.get("transitions", [])
    transition_keys = {
        "path",
        "historical_receipt",
        "classification",
        "frozen_sha256",
        "approved_current_sha256",
        "decision_ids",
    }
    transition_shape = (
        isinstance(contract_transitions, list)
        and isinstance(delta_transitions, list)
        and len(contract_transitions) == len(delta_transitions) == 26
        and len({row.get("path") for row in contract_transitions}) == 26
        and all(set(row) == transition_keys for row in contract_transitions)
        and delta_transitions == contract_transitions
        and current_delta.get("transition_count") == 26
        and "migration/current-document-consistency-repair-r2.3-manifest.json"
        not in {row.get("path") for row in delta_transitions}
        and "release/source-tree-manifest.json"
        not in {row.get("path") for row in delta_transitions}
    )
    check(
        transition_shape,
        "CURRENT_DELTA_TRANSITION_EXACT",
        f"contract={len(contract_transitions)} delta={len(delta_transitions)}",
    )
    transitions_by_path = {
        row["path"]: row
        for row in contract_transitions
        if isinstance(row, dict) and set(row) == transition_keys
    }

    def exact_transition(
        rel: str,
        receipt: str,
        frozen_sha256: str,
        approved_current_sha256: str,
    ) -> bool:
        row = transitions_by_path.get(rel)
        return bool(
            transition_shape
            and row
            and row["historical_receipt"] == receipt
            and row["frozen_sha256"] == frozen_sha256
            and row["approved_current_sha256"] == approved_current_sha256
            and bool(row["classification"])
            and bool(row["decision_ids"])
            and (root / rel).is_file()
            and file_sha(root / rel) == approved_current_sha256
        )

    language_identity_exemptions = {
        row.get("path"): row.get("sha256")
        for row in language_coherence_contract.get(
            "migration_identity_exemptions", []
        )
        if isinstance(row, dict)
        and set(row) == {"path", "sha256"}
        and isinstance(row.get("path"), str)
        and isinstance(row.get("sha256"), str)
    }

    def revision_identity_exempt(relative: str, current_sha256: str) -> bool:
        if revision == POST_PR16_REVISION:
            return relative in POST_PR16_CANONICAL_DELTA_PATHS
        if revision == LANGUAGE_COHERENCE_REVISION:
            return language_identity_exemptions.get(relative) == current_sha256
        return False

    repair = parsed.get(root / "migration/m1.1-repair-manifest.json", {})
    changed_paths = {repair.get("human_corpus", {}).get("path")}
    transformations = repair.get("reference_normalization", {}).get("transformations", [])
    changed_paths.update(row.get("path") for row in transformations)
    changed_paths.discard(None)
    for row in transformations:
        path = root / row["path"]
        current_hash = file_sha(path) if path.is_file() else ""
        check(
            path.is_file()
            and (
                current_hash == row["output_sha256"]
                or revision_identity_exempt(row["path"], current_hash)
                or exact_transition(
                    row["path"],
                    "migration/m1.1-repair-manifest.json",
                    row["output_sha256"],
                    current_hash,
                )
            ),
            "REPAIR_OUTPUT_IDENTITY",
            row["path"],
        )

    imported = parsed.get(root / "migration/import-manifest.json", {})
    legacy = imported.get("legacy_files", [])
    check(imported.get("legacy_file_count") == len(legacy) == 86, "IMPORT_FILE_COUNT", str(len(legacy)))
    check(imported.get("semantic_delta") == "NONE; identity/path/configuration migration only", "IMPORT_SEMANTIC_DELTA", str(imported.get("semantic_delta")))
    for entry in legacy:
        for rel in entry.get("current_paths", []):
            target = root / rel
            check(target.exists(), "MIGRATED_PATH_EXISTS", f"{entry['legacy_path']} -> {rel}")
            if target.is_file() and entry["disposition"] != "MIGRATED_SOURCE_SHARDS" and rel not in changed_paths:
                current_hash = file_sha(target)
                check(
                    current_hash == entry["sha256"]
                    or revision_identity_exempt(rel, current_hash)
                    or exact_transition(
                        rel,
                        "migration/import-manifest.json",
                        entry["sha256"],
                        current_hash,
                    ),
                    "IMPORT_BYTE_IDENTITY",
                    rel,
                )

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
    check(
        sum(counts.values()) == len(active)
        and set(counts) <= {"accept", "accept_with_gate", "reject"}
        and counts["accept"] == len(positive)
        and counts["accept_with_gate"] == len(gated)
        and counts["reject"] == len(rejected),
        "EXAMPLE_OUTCOME_COUNTS",
        str(dict(counts)),
    )
    active_ids = {row["example_id"] for row in active}
    partitions = [positive, rejected, gated]
    partition_ids = [row["example_id"] for group in partitions for row in group]
    check(len(partition_ids) == len(set(partition_ids)) and set(partition_ids) == active_ids, "EXAMPLE_PARTITION_EXACT", str([len(group) for group in partitions]))
    active_by_id = {row["example_id"]: row for row in active}
    for row in gated:
        owner = active_by_id.get(row["example_id"], {})
        check(owner.get("expected_outcome") == "accept_with_gate" and owner.get("source_activation") == "explicit_feature_gate" and bool(owner.get("feature_ids")), "GATED_EXAMPLE_LAW", row["example_id"])

    feature_rows = rows("deeplus-0.1.2-baseline-r51f3-feature-registry.json", "features")
    diagnostic_rows = rows("deeplus-0.1.2-baseline-r51f3-diagnostic-registry.json", "diagnostics")
    predicate_rows = rows("deeplus-0.1.2-baseline-r51f3-checker-predicate-catalog.json", "predicates")
    actual = {
        "features": len(feature_rows),
        "diagnostics": len(diagnostic_rows),
        "predicates": len(predicate_rows),
        "predicate_fixtures": len(rows("deeplus-0.1.2-baseline-r51f3-checker-predicate-fixtures.json", "fixtures")),
        "examples": len(active),
        "no_go": len(rows("deeplus-0.1.2-baseline-r51f3-current-no-go-registry.json", "entries")),
    }
    vocabulary = parsed.get(root / "spec/grammar/keyword-vocabulary.json", {})
    actual["hard_keywords"] = len(vocabulary.get("hard_keywords", []))
    actual["contextual_words"] = len(vocabulary.get("contextual_words", []))
    expected_counts = (
        {
            key: value
            for key, value in language_coherence_contract.get(
                "canonical_counts", {}
            ).items()
            if key != "prelude_entries"
        }
        if revision == LANGUAGE_COHERENCE_REVISION
        else EXPECTED
    )
    for key, expected in expected_counts.items():
        check(actual[key] == expected, "CANONICAL_COUNT", f"{key}={actual[key]} expected={expected}")

    feature_by_id = {row.get("feature_id"): row for row in feature_rows}
    diagnostic_by_id = {row.get("diagnostic_id"): row for row in diagnostic_rows}
    predicate_by_id = {row.get("predicate_id"): row for row in predicate_rows}
    predicate_relation_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-diagnostic-relation-registry.json",
        "relations",
    )
    for predicate_id, predicate in predicate_by_id.items():
        if not predicate.get("emission_eligible"):
            continue
        primary_relations = [
            row.get("diagnostic_id")
            for row in predicate_relation_rows
            if row.get("predicate_id") == predicate_id
            and row.get("relation") == "primary"
        ]
        secondary_relations = {
            row.get("diagnostic_id")
            for row in predicate_relation_rows
            if row.get("predicate_id") == predicate_id
            and row.get("relation") == "secondary"
        }
        declared_secondaries = set(predicate.get("secondary_diagnostics", []))
        check(
            primary_relations == [predicate.get("active_primary_diagnostic")],
            "DIAGNOSTIC_RELATION_PRIMARY_BINDING",
            f"{predicate_id}: declared={predicate.get('active_primary_diagnostic')} relations={primary_relations}",
        )
        check(
            declared_secondaries == secondary_relations,
            "DIAGNOSTIC_RELATION_SECONDARY_BINDING",
            f"{predicate_id}: missing={sorted(declared_secondaries - secondary_relations)} extra={sorted(secondary_relations - declared_secondaries)}",
        )
    empty_char = active_by_id.get("EX-R49B-CHAR-005", {})
    empty_char_surface = next(
        (row for row in rejected if row.get("example_id") == "EX-R49B-CHAR-005"),
        {},
    )
    empty_char_features = {
        "char_unicode_scalar_value_model",
        "unicode_char_literal_single_quote_msp",
    }
    empty_char_sha = "57f7a0556e0351b914052e202e272fbf8c801a26dbc3e34179cf1b886c817399"
    check(
        empty_char.get("expected_outcome") == "reject"
        and empty_char.get("primary_diagnostic") == "CHAR_LITERAL_EMPTY"
        and set(empty_char.get("feature_ids", [])) == empty_char_features
        and empty_char.get("code_sha256") == empty_char_sha
        and empty_char.get("parser_status") == "not_run"
        and empty_char.get("checker_status") == "not_run"
        and empty_char_surface.get("primary_diagnostic") == "CHAR_LITERAL_EMPTY"
        and set(empty_char_surface.get("feature_ids", [])) == empty_char_features
        and empty_char_surface.get("code_sha256") == empty_char_sha,
        "CMA_EMPTY_CHAR_EXAMPLE",
        str(empty_char.get("example_id")),
    )
    required_set = set(REQUIRED_FEATURE_IDS)
    check(
        len(REQUIRED_FEATURE_IDS) == 20
        and len(required_set) == 20
        and required_set <= set(feature_by_id),
        "REQUIRED_FEATURE_SET",
        f"count={len(required_set)} missing={sorted(required_set - set(feature_by_id))}",
    )
    for feature_id in REQUIRED_FEATURE_IDS:
        feature = feature_by_id.get(feature_id, {})
        trace = feature.get("normative_trace_refs", {})
        forward_diagnostics = set(trace.get("diagnostics", []))
        reverse_diagnostics = {
            row.get("diagnostic_id")
            for row in diagnostic_rows
            if row.get("diagnostic_status") == "active"
            and feature_id in row.get("feature_refs", [])
        }
        check(
            forward_diagnostics == reverse_diagnostics,
            "DIRECT_DIAGNOSTIC_TRACE_EQUALITY",
            f"{feature_id}: forward={sorted(forward_diagnostics)} reverse={sorted(reverse_diagnostics)}",
        )
        forward_predicates = {
            predicate_id
            for predicate_id in trace.get("predicates", [])
            if predicate_by_id.get(predicate_id, {}).get("predicate_maturity") == "active"
        }
        reverse_predicates = {
            row.get("predicate_id")
            for row in predicate_rows
            if row.get("predicate_maturity") == "active"
            and feature_id in row.get("feature_refs", [])
        }
        design_seed_predicates = {
            row.get("predicate_id")
            for row in predicate_rows
            if row.get("predicate_maturity") == "design_seed"
            and feature_id in row.get("feature_refs", [])
        }
        check(
            forward_predicates == reverse_predicates,
            "DIRECT_PREDICATE_TRACE_EQUALITY",
            f"{feature_id}: forward={sorted(forward_predicates)} reverse={sorted(reverse_predicates)} design_seed={sorted(design_seed_predicates)}",
        )
        forward_examples = set(trace.get("examples", []))
        reverse_examples = {
            row.get("example_id")
            for row in active
            if feature_id in row.get("source_feature_ids", row.get("feature_ids", []))
        }
        check(
            forward_examples == reverse_examples,
            "DIRECT_EXAMPLE_TRACE_EQUALITY",
            f"{feature_id}: forward={sorted(forward_examples)} reverse={sorted(reverse_examples)}",
        )
        check(
            feature.get("status_enum") == "STABLE_DESIGN"
            and feature.get("source_activation") == "none",
            "REQUIRED_FEATURE_STATUS_ACTIVATION",
            feature_id,
        )

    rightward_id = "rightward_flow_dollar_local_binding_msp"
    rightward_feature = feature_by_id.get(rightward_id, {})
    rightward_owned = sum(
        rightward_id in row.get("source_feature_ids", row.get("feature_ids", []))
        for row in active
        if row.get("example_id") == "EX-R51d-008"
    )
    check(
        "EX-R51d-008" not in rightward_feature.get("normative_trace_refs", {}).get("examples", [])
        and rightward_owned == 0,
        "RIGHTWARD_UNRELATED_EXAMPLE_ZERO",
        str(rightward_owned),
    )
    numeric_diagnostics = feature_by_id.get(
        "numeric_array_postfix_transpose_caret_msp", {}
    ).get("normative_trace_refs", {}).get("diagnostics", [])
    check(
        numeric_diagnostics.count("CARET_ATTACHMENT_AMBIGUOUS") == 0,
        "NUMERIC_TRANSPOSE_CARET_DIAGNOSTIC_ZERO",
        str(numeric_diagnostics),
    )
    set_feature = feature_by_id.get("set_prefixed_literal", {})
    check(
        set_feature.get("normative_trace_refs", {}).get("examples", []) == ["EX-R51f-008"],
        "SUPPLEMENTAL_SET_PREFIX_EDGE",
        str(set_feature.get("normative_trace_refs", {}).get("examples", [])),
    )
    unknown_prefixed = diagnostic_by_id.get("UNKNOWN_PREFIXED_LITERAL", {})
    check(
        unknown_prefixed.get("feature_refs") == [
            "set_prefixed_literal",
            "r51f_removed_surface_boundary_law",
        ]
        and unknown_prefixed.get("message") == "Unknown #prefix literal; current prefixed literal families are #map, #set, #mut, and #bytes."
        and unknown_prefixed.get("stage") == "checker"
        and unknown_prefixed.get("severity") == "error"
        and unknown_prefixed.get("diagnostic_status") == "active"
        and unknown_prefixed.get("product_support") == "NOT_RUN",
        "SUPPLEMENTAL_UNKNOWN_PREFIXED_LITERAL_ZERO_DELTA",
        str(unknown_prefixed),
    )

    coverage_rows = {
        row.get("feature_id"): row.get("evidence_coverage")
        for row in feature_rows
        if row.get("evidence_coverage") is not None
    }
    expected_coverage = {
        "optional_chaining_not_current_law": ("N/A_REJECTION_ONLY_LAW", "accept"),
        "at_control_expression_family": ("N/A_DELEGATED_UMBRELLA", "reject"),
        "ternary_short_expression_stable_profile": ("N/A_WARNING_PROFILE", "reject"),
    }
    check(
        set(coverage_rows) == set(expected_coverage),
        "FEATURE_EVIDENCE_COVERAGE_SET",
        str(sorted(coverage_rows)),
    )
    for feature_id, (kind, missing_outcome) in expected_coverage.items():
        entries = coverage_rows.get(feature_id, [])
        entry = entries[0] if len(entries) == 1 and isinstance(entries[0], dict) else {}
        common_keys = {"feature_id", "coverage_kind", "missing_outcome", "reason", "owner"}
        evidence = entry.get("substitute_evidence", [])
        delegated = kind == "N/A_DELEGATED_UMBRELLA"
        check(
            entry.get("feature_id") == feature_id
            and entry.get("coverage_kind") == kind
            and entry.get("missing_outcome") == missing_outcome
            and all(entry.get(key) for key in common_keys)
            and bool(evidence)
            and all(example_id in active_by_id for example_id in evidence)
            and (
                bool(entry.get("delegated_feature_id"))
                and entry.get("delegated_feature_id") in feature_by_id
                and entry.get("delegated_rule") in diagnostic_by_id
                if delegated
                else entry.get("substitute_boundary_diagnostic") in diagnostic_by_id
            ),
            "FEATURE_EVIDENCE_COVERAGE_SCHEMA",
            f"{feature_id}: {entry}",
        )
    for feature_id in REQUIRED_FEATURE_IDS:
        direct_outcomes = {
            "accept" if row.get("expected_outcome") in {"accept", "accept_with_gate"} else "reject"
            for row in active
            if feature_id in row.get("source_feature_ids", row.get("feature_ids", []))
        }
        missing = {"accept", "reject"} - direct_outcomes
        coverage = coverage_rows.get(feature_id, [])
        declared_missing = {entry.get("missing_outcome") for entry in coverage}
        check(
            not missing or missing == declared_missing,
            "FEATURE_EVIDENCE_OUTCOME_CLOSURE",
            f"{feature_id}: direct={sorted(direct_outcomes)} missing={sorted(missing)} declared={sorted(str(item) for item in declared_missing)}",
        )

    bytes_feature = feature_by_id.get("bytes_literal_hash_bytes_msp", {})
    check(
        bytes_feature.get("notes") == '#bytes"..." raw byte sequence literal; no implicit String/Bytes conversion.'
        and '.." raw byte sequence literal' not in json.dumps(feature_rows, ensure_ascii=False),
        "BYTES_NOTE_CURRENT_SPELLING",
        str(bytes_feature.get("notes")),
    )
    match_guard = diagnostic_by_id.get("MATCH_ARM_SINGLE_GUARD_ONLY", {})
    match_fixture = active_by_id.get("EX-R51b-GRAM-NG-009", {})
    check(
        match_guard.get("message") == "A match arm admits at most one `if` or attached `!if` guard."
        and match_guard.get("severity") == "error"
        and match_guard.get("stage") == "parser"
        and match_guard.get("diagnostic_status") == "active"
        and match_guard.get("feature_refs") == ["match_arm_guard_msp"]
        and match_guard.get("fixit_hint") == MATCH_GUARD_FIXIT
        and match_guard.get("fixit_policy") == MATCH_GUARD_FIXIT
        and "annotation" not in (match_guard.get("fixit_hint", "") + match_guard.get("fixit_policy", "")).lower()
        and match_fixture.get("primary_diagnostic") == "MATCH_ARM_SINGLE_GUARD_ONLY"
        and "match_arm_guard_msp" in match_fixture.get("source_feature_ids", match_fixture.get("feature_ids", [])),
        "MATCH_GUARD_FIXIT",
        str(match_guard),
    )

    mir_text = (root / "spec/mir/semantics.md").read_text(encoding="utf-8")
    mir_section = mir_text.split(
        "## 14. Normative document-consistency product-handoff dispositions", 1
    )
    mir_rows = {}
    if len(mir_section) == 2:
        for feature_id, disposition in re.findall(
            r"^\| `([^`]+)` \| `([^`]+(?:\([^`]+\))?)` \|", mir_section[1], re.MULTILINE
        ):
            mir_rows[feature_id] = disposition
    check(
        mir_rows == MIR_DISPOSITIONS,
        "MIR_REQUIRED_DISPOSITION_CLOSURE",
        f"rows={len(mir_rows)} missing={sorted(required_set - set(mir_rows))} extra={sorted(set(mir_rows) - required_set)}",
    )
    deferred_required = {
        feature_id for feature_id, disposition in MIR_DISPOSITIONS.items()
        if disposition == "DEFERRED_PRODUCT_HANDOFF"
    }
    check(
        len(deferred_required) == 6
        and all(
            f"`{feature_id}`" in mir_section[-1]
            for feature_id in SUPPLEMENTAL_MIR_FEATURE_IDS
        )
        and mir_section[-1].count("are `LAW_PRESENT`") == 1
        and "All product lanes remain `NOT_RUN`" in mir_section[-1]
        and "not a product execution receipt" in mir_section[-1],
        "MIR_DEFERRED_PRODUCT_HANDOFF",
        f"required={len(deferred_required)} supplemental={SUPPLEMENTAL_MIR_FEATURE_IDS}",
    )

    successor_semantic_files = {
        row.get("path"): row.get("sha256")
        for row in language_coherence_contract.get(
            "semantic_authority_files", []
        )
        if isinstance(row, dict) and set(row) == {"path", "sha256"}
    }
    for rel, expected_sha in FROZEN_UNCHANGED_SEMANTIC_HASHES.items():
        if revision == LANGUAGE_COHERENCE_REVISION:
            check(
                successor_semantic_files.get(rel) == file_sha(root / rel),
                "SUCCESSOR_SEMANTIC_FILE_IDENTITY",
                rel,
            )
            continue
        if revision == POST_PR16_REVISION and rel == "spec/types/type-system.md":
            continue
        check(file_sha(root / rel) == expected_sha, "FROZEN_SEMANTIC_FILE_IDENTITY", rel)
    r42 = feature_by_id.get("type_system_rcts_v5_ts_r42_current_canonical_companion", {})
    active_navigation_text = "\n".join(
        (root / rel).read_text(encoding="utf-8", errors="replace")
        for rel in ("README.md", "GOVERNANCE.md", "CONTRIBUTING.md", "current/current-pointer.json")
        if (root / rel).is_file()
    )
    check("EP1" not in active_navigation_text, "EP1_CURRENT_NAVIGATION_ZERO", "README/GOVERNANCE/CONTRIBUTING/pointer")
    check(
        r42.get("status_enum") == "SUPERSEDED"
        and r42.get("source_activation") == "nonactivatable",
        "R42_SUPERSEDED_NONACTIVATABLE",
        str(r42.get("status_enum")),
    )

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
        "tests/fixtures/current/type-flow-callable-coherence-r1.json": ("fixture_schema", "schemas/language/type-flow-callable-coherence-fixtures.schema.json"),
        "tests/fixtures/current/destructuring-pattern-matching-r1.json": ("fixture_schema", "schemas/language/destructuring-pattern-matching-static-fixtures.schema.json"),
        "tests/fixtures/current/value-operator-indexing-coherence-r1.json": ("fixture_schema", "schemas/language/value-operator-indexing-coherence-fixtures.schema.json"),
        "tests/fixtures/current/type-refinement-narrowing-coherence-r1.json": ("fixture_schema", "schemas/language/type-refinement-narrowing-coherence-fixtures.schema.json"),
        "tests/fixtures/current/enum-derived-capabilities-r1.json": ("fixture_schema", "schemas/language/enum-derived-capabilities-fixtures.schema.json"),
    }
    for rel, (field, expected) in operational.items():
        value = parsed.get(root / rel, {})
        check(value.get(field) == expected and (root / expected).exists(), "OPERATIONAL_POINTER", f"{rel}:{field}")

    tfc_rel = "tests/fixtures/current/type-flow-callable-coherence-r1.json"
    tfc = parsed.get(root / tfc_rel, {})
    tfc_top_keys = {
        "schema", "fixture_schema", "revision", "contract", "evidence_status",
        "product_support", "product_lanes", "fixture_policy", "positive",
        "negative", "boundary", "expected_counts",
    }
    check(set(tfc) == tfc_top_keys, "TFC_FIXTURE_CLOSED_SHAPE", str(sorted(set(tfc) ^ tfc_top_keys)))
    tfc_groups = {
        "positive": tfc.get("positive", []),
        "negative": tfc.get("negative", []),
        "boundary": tfc.get("boundary", []),
    }
    tfc_rows = [row for rows in tfc_groups.values() for row in rows if isinstance(row, dict)]
    tfc_ids = [row.get("fixture_id") for row in tfc_rows]
    tfc_counts = tfc.get("expected_counts", {})
    check(
        len(tfc_rows) == len(tfc_ids) == len(set(tfc_ids))
        and all(tfc_counts.get(group) == len(rows) for group, rows in tfc_groups.items())
        and tfc_counts.get("total") == len(tfc_rows)
        and tfc_counts.get("product_executed") == 0,
        "TFC_FIXTURE_COUNT_AND_ID_CLOSURE",
        f"rows={len(tfc_rows)} ids={len(set(tfc_ids))} counts={tfc_counts}",
    )
    tfc_contract = parsed.get(root / "spec/contracts/type-flow-callable-coherence.json", {})
    tfc_rule_ids = [row.get("rule_id") for row in tfc_contract.get("rules", []) if isinstance(row, dict)]
    check(
        len(tfc_rule_ids) == 20
        and len(set(tfc_rule_ids)) == 20
        and all(
            isinstance(row.get("rule_ids"), list)
            and row["rule_ids"]
            and set(row["rule_ids"]).issubset(set(tfc_rule_ids))
            for row in tfc_rows
        ),
        "TFC_RULE_BINDING_CLOSURE",
        f"rules={len(tfc_rule_ids)} rows={len(tfc_rows)}",
    )
    cleanup_skip = next(
        (row for row in tfc_groups["negative"] if row.get("fixture_id") == "TFC-N-025-CLEANUP-SKIP"),
        {},
    )
    cleanup_descriptor = cleanup_skip.get("responsibility_descriptor", {})
    check(
        cleanup_skip.get("expected_existing_diagnostic") == "DEFER_CLEANUP_RESERVED_PLACE_MOVED"
        and cleanup_descriptor.get("normalized_type") == "File"
        and cleanup_descriptor.get("ownership") == "resource"
        and cleanup_descriptor.get("cleanup") == "drop_exactly_once"
        and cleanup_descriptor.get("bound_place") == "resource",
        "TFC_CLEANUP_OBLIGATION_EXPLICIT",
        str(cleanup_descriptor),
    )

    dpm_rel = "tests/fixtures/current/destructuring-pattern-matching-r1.json"
    dpm = parsed.get(root / dpm_rel, {})
    dpm_top_keys = {
        "schema", "fixture_schema", "revision", "authority", "evidence_level",
        "product_execution", "phase_profile", "failure_profile",
        "lifecycle_identities", "counts", "fixtures",
    }
    dpm_row_keys = {
        "fixture_id", "fixture_class", "context_id", "pattern_kind_id", "source",
        "subject_profile", "expected", "primary_diagnostic_family_or_null",
        "assertions", "execution_state",
    }
    dpm_rows = [row for row in dpm.get("fixtures", []) if isinstance(row, dict)]
    dpm_ids = [row.get("fixture_id") for row in dpm_rows]
    dpm_class_counts = Counter(row.get("fixture_class") for row in dpm_rows)
    dpm_counts = dpm.get("counts", {})
    check(
        set(dpm) == dpm_top_keys
        and all(set(row) == dpm_row_keys for row in dpm_rows),
        "DPM_FIXTURE_CLOSED_SHAPE",
        f"top_delta={sorted(set(dpm) ^ dpm_top_keys)} rows={len(dpm_rows)}",
    )
    check(
        len(dpm_rows) == len(dpm_ids) == len(set(dpm_ids)) == dpm_counts.get("fixtures")
        and all(dpm_counts.get(group) == dpm_class_counts.get(group, 0) for group in ("positive", "negative", "boundary"))
        and dpm_counts.get("product_executed") == 0
        and all(row.get("execution_state") == "DESIGN_STATIC_NOT_RUN" for row in dpm_rows),
        "DPM_FIXTURE_COUNT_AND_ID_CLOSURE",
        f"rows={len(dpm_rows)} ids={len(set(dpm_ids))} classes={dict(dpm_class_counts)}",
    )

    voi_rel = "tests/fixtures/current/value-operator-indexing-coherence-r1.json"
    voi = parsed.get(root / voi_rel, {})
    voi_top_keys = {
        "schema", "fixture_schema", "revision", "contract", "authority",
        "evidence_level", "semantic_p0", "current_binding", "open_feature_p1",
        "separate_open_actions", "product_lanes", "positive", "negative",
        "boundary", "expected_counts",
    }
    voi_row_keys = {
        "fixture_id", "fixture_class", "rule_ids", "domain", "source",
        "subject_profile", "expected", "diagnostic_or_null", "assertions",
        "execution_state",
    }
    voi_groups = {
        group: voi.get(group, []) for group in ("positive", "negative", "boundary")
    }
    voi_rows = [
        row for group in voi_groups.values() for row in group if isinstance(row, dict)
    ]
    voi_ids = [row.get("fixture_id") for row in voi_rows]
    voi_counts = voi.get("expected_counts", {})
    check(
        set(voi) == voi_top_keys
        and all(set(row) == voi_row_keys for row in voi_rows)
        and len(voi_rows) == len(voi_ids) == len(set(voi_ids)) == 50
        and all(voi_counts.get(group) == len(rows) for group, rows in voi_groups.items())
        and voi_counts.get("total") == 50
        and voi_counts.get("semantic_p0") == 0
        and voi_counts.get("open_feature_p1") == 22
        and voi_counts.get("closed_feature_p1") == 0
        and voi_counts.get("new_feature_p1") == 0
        and voi_counts.get("product_executed") == 0,
        "VOI_FIXTURE_SHAPE_COUNT_AND_ID_CLOSURE",
        f"rows={len(voi_rows)} ids={len(set(voi_ids))} counts={voi_counts}",
    )
    voi_contract = parsed.get(root / "spec/contracts/value-operator-indexing-coherence.json", {})
    voi_rule_ids = [
        row.get("rule_id") for row in voi_contract.get("rules", []) if isinstance(row, dict)
    ]
    expected_voi_rules = [f"VOI-R{index:03d}" for index in range(1, 13)]
    expected_feature_p1 = SUCCESSOR_ACTION_IDS[4:]
    expected_product_lanes = {row: "NOT_RUN" for row in (
        "rust_frontend_lexer", "rust_frontend_parser", "rust_hir_lowering",
        "rust_integrated_checker", "deeplus_mir_lowering", "xvm_bytecode_emitter",
        "xvm_interpreter", "llvm_aot_backend", "llvm_orc_jit_backend",
        "formatter_lsp", "stdlib_provider_runner", "official_tooling",
        "independent_conformance", "cross_backend_conformance",
        "actual_user_team_study",
    )}
    check(
        voi_rule_ids == expected_voi_rules
        and {
            rule_id
            for row in voi_rows
            for rule_id in row.get("rule_ids", [])
        } == set(expected_voi_rules)
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(expected_voi_rules))
            and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in voi_rows
        )
        and voi.get("open_feature_p1") == expected_feature_p1
        and voi.get("separate_open_actions") == EXPECTED_ACTION_IDS
        and voi.get("product_lanes") == expected_product_lanes,
        "VOI_RULE_GUARD_AND_PRODUCT_CLOSURE",
        f"rules={voi_rule_ids} p1={len(voi.get('open_feature_p1', []))} lanes={len(voi.get('product_lanes', {}))}",
    )
    voi_machine = voi_contract.get("machine_acceptance", {})
    voi_new_diagnostics = [
        row.get("diagnostic_id")
        for row in voi_contract.get("new_rejection_diagnostic_matrix", [])
        if isinstance(row, dict)
    ]
    expected_voi_diagnostics = [
        "NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE",
        "CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT",
        "FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT",
        "RANGE_OPERATOR_SPELLING_NOT_CURRENT",
        "INDEX_SUFFIX_REQUIRES_AXIS",
        "BITWISE_OPERATOR_MIXED_DOMAIN_REQUIRES_EXPLICIT_CONVERSION",
    ]
    check(
        voi_contract.get("revision") == revision
        and voi_contract.get("semantic_p0") == 0
        and voi_contract.get("current_binding") is False
        and voi_contract.get("product_lanes") == "15/15_NOT_RUN"
        and voi_contract.get("open_feature_p1", {}).get("total") == 22
        and voi_machine.get("rule_count") == 12
        and voi_machine.get("literal_domain_row_count")
        == len(voi_contract.get("literal_domain_matrix", [])) == 11
        and voi_machine.get("expression_precedence_row_count")
        == len(voi_contract.get("expression_operator_precedence_matrix", [])) == 19
        and voi_machine.get("index_carrier_row_count")
        == len(voi_contract.get("index_carrier_matrix", [])) == 10
        and voi_machine.get("slice_form_row_count")
        == len(voi_contract.get("slice_form_matrix", [])) == 8
        and voi_machine.get("operator_dispatch_mode") == "INTRINSIC_ONLY"
        and voi_machine.get("custom_operator_current_count") == 0
        and voi_machine.get("fixed_operator_conformance_overloading_current_count") == 0
        and voi_machine.get("trait_operator_lookup_count") == 0
        and voi_machine.get("structural_bracket_activation_count") == 0
        and voi_machine.get("ordinary_sequence_first_index") == 1
        and voi_machine.get("negative_from_end_rewrite_count") == 0
        and voi_machine.get("implicit_rebase_count") == 0
        and voi_machine.get("product_execution_receipt_count") == 0
        and voi_machine.get("new_rejection_diagnostic_count")
        == len(voi_new_diagnostics) == 6
        and voi_new_diagnostics == expected_voi_diagnostics
        and set(voi_new_diagnostics).issubset(set(diagnostic_by_id)),
        "VOI_CONTRACT_MACHINE_ACCEPTANCE",
        f"machine={voi_machine} diagnostics={voi_new_diagnostics}",
    )
    voi_example_ids = {
        *(f"EX-R51VOI-{index:03d}" for index in range(1, 10)),
        *(f"EX-R51VOI-NG-{index:03d}" for index in range(1, 10)),
    }
    warning_example = active_by_id.get("EX-R51VOI-009", {})
    check(
        voi_example_ids.issubset(active_ids)
        and warning_example.get("expected_outcome") == "accept"
        and warning_example.get("expected_warnings")
        == ["SLICE_HALF_OPEN_RANGE_NONCANONICAL"],
        "VOI_EXAMPLE_AND_WARNING_BINDING",
        f"missing={sorted(voi_example_ids - active_ids)} warning={warning_example.get('expected_warnings')}",
    )

    trn_rel = "tests/fixtures/current/type-refinement-narrowing-coherence-r1.json"
    trn = parsed.get(root / trn_rel, {})
    trn_contract = parsed.get(root / "spec/contracts/type-refinement-narrowing-coherence.json", {})
    trn_rows = [row for row in trn.get("cases", []) if isinstance(row, dict)]
    trn_ids = [row.get("fixture_id") for row in trn_rows]
    trn_rule_ids = [
        row.get("rule_id") for row in trn_contract.get("rules", []) if isinstance(row, dict)
    ]
    trn_counts = trn.get("expected_counts", {})
    trn_admit = sum(row.get("expected") == "ADMIT" for row in trn_rows)
    trn_reject = sum(row.get("expected") == "REJECT" for row in trn_rows)
    check(
        trn.get("revision") == revision
        and trn_contract.get("revision") == revision
        and trn_contract.get("semantic_p0") == 0
        and trn_contract.get("current_binding") is False
        and trn_contract.get("product_lanes") == "15/15_NOT_RUN"
        and trn_contract.get("open_feature_p1", {}).get("total") == 22
        and trn_rule_ids == [f"TRN-R{index:03d}" for index in range(1, 14)]
        and len(trn_rows) == len(trn_ids) == len(set(trn_ids)) == trn_counts.get("cases") == 35
        and trn_admit == trn_counts.get("admit") == 10
        and trn_reject == trn_counts.get("reject") == 25
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(trn_rule_ids))
            and row.get("commit_count") in {0, 1}
            and (row.get("expected") == "ADMIT") == (row.get("diagnostic_or_null") is None)
            for row in trn_rows
        )
        and len(trn.get("open_feature_p1", [])) == 22
        and len(trn.get("product_lanes", {})) == 15
        and set(trn.get("product_lanes", {}).values()) == {"NOT_RUN"}
        and trn_counts.get("runtime_union_tests") == 2
        and trn_counts.get("open_runtime_type_tests") == 0
        and trn_counts.get("def_guard_narrowing_facts") == 0
        and trn_counts.get("p1_closed") == 0
        and trn_counts.get("p1_created") == 0,
        "TRN_CONTRACT_FIXTURE_CLOSURE",
        f"rules={trn_rule_ids} rows={len(trn_rows)} admit={trn_admit} reject={trn_reject} counts={trn_counts}",
    )

    edc_rel = "tests/fixtures/current/enum-derived-capabilities-r1.json"
    edc = parsed.get(root / edc_rel, {})
    edc_contract = parsed.get(
        root / "spec/contracts/enum-derived-capabilities.json", {}
    )
    edc_rows = [row for row in edc.get("cases", []) if isinstance(row, dict)]
    edc_ids = [row.get("fixture_id") for row in edc_rows]
    edc_rule_ids = [
        row.get("rule_id")
        for row in edc_contract.get("rules", [])
        if isinstance(row, dict)
    ]
    edc_counts = edc.get("expected_counts", {})
    edc_expected_p1 = [
        *(f"CE-C-P1-{index:03d}" for index in range(1, 7)),
        *(f"CE-E-P1-{index:03d}" for index in range(1, 9)),
        *(f"TCC-P1-{index:03d}" for index in range(2, 9)),
        "SFD-P1-009",
    ]
    edc_feature_ids = {
        "enum_declaration_order_ord_preview_design",
        "enum_case_display_mapping_preview_design",
        "enum_exact_variant_subset_alias_preview_design",
    }
    edc_features = [feature_by_id.get(feature_id, {}) for feature_id in edc_feature_ids]
    edc_frontend = parsed.get(root / "spec/frontend/frontend-model.json", {}).get(
        "preview_design_nonactivatable", {}
    )
    edc_frontend_ids = {
        "enum_declaration_order_ord_derivation",
        "enum_case_display_mapping",
        "enum_exact_variant_subset_alias",
    }
    edc_pc10_lanes = [
        "source", "resolution", "behavior", "serialization",
        "runtime_layout", "foreign_ABI", "tooling_reflection", "product",
    ]
    edc_serialized = json.dumps(edc_contract, ensure_ascii=False)
    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    check(
        edc.get("revision") == revision
        and edc_contract.get("revision") == revision
        and edc_contract.get("semantic_p0") == 0
        and edc_contract.get("current_binding") is False
        and edc_contract.get("source_activation") == "nonactivatable"
        and edc_contract.get("product_lanes") == "15/15_NOT_RUN"
        and edc_contract.get("open_feature_p1", {}).get("total") == 22
        and edc_contract.get("compatibility_lanes") == edc_pc10_lanes
        and edc_contract.get("compatibility_lane_subrecords") == {
            "resolution": ["subset_membership", "variant_owner_widening"],
            "behavior": ["order_behavior", "display_behavior"],
            "serialization": ["raw_identity"],
        }
        and "overall_pass" not in edc_serialized
        and "sibling_status_propagation" not in edc_serialized
        and edc_contract.get("trait_contracts", {}).get("Ord<T>", {}).get(
            "canonical_signature"
        ) == "public trait Ord<T> { +def compare.(borrow lhs: T, borrow rhs: T) -> Int throws Never effects {}; }"
        and edc_contract.get("trait_contracts", {}).get("Display", {}).get(
            "canonical_signature"
        ) == "public trait Display { +def display.() -> String throws Never effects {}; }"
        and edc.get("open_feature_p1") == edc_expected_p1
        and edc_rule_ids == [f"EDC-R{index:03d}" for index in range(1, 19)]
        and len(edc_rows) == len(edc_ids) == len(set(edc_ids)) == 35
        and sum(row.get("expected_design") == "ADMIT" for row in edc_rows)
        == edc_counts.get("design_admit") == 15
        and sum(row.get("expected_design") == "REJECT" for row in edc_rows)
        == edc_counts.get("design_reject") == 15
        and sum(row.get("expected_design") == "BOUNDARY" for row in edc_rows)
        == edc_counts.get("boundary") == 5
        and all(
            row.get("rule_ids")
            and set(row["rule_ids"]).issubset(set(edc_rule_ids))
            and row.get("current_source_outcome") == "NONACTIVATABLE_NOT_CURRENT"
            and row.get("execution_state") == "DESIGN_STATIC_NOT_RUN"
            for row in edc_rows
        )
        and set(edc_rule_ids)
        == {rule_id for row in edc_rows for rule_id in row.get("rule_ids", [])}
        and len(edc.get("product_lanes", {})) == 15
        and set(edc.get("product_lanes", {}).values()) == {"NOT_RUN"}
        and edc_counts.get("current_source_activated") == 0
        and edc_counts.get("p1_closed") == 0
        and edc_counts.get("p1_created") == 0
        and edc_counts.get("product_executed") == 0,
        "EDC_CONTRACT_FIXTURE_CLOSURE",
        f"rules={edc_rule_ids} rows={len(edc_rows)} counts={edc_counts}",
    )
    check(
        all(
            feature.get("status_enum") == "PREVIEW_DESIGN"
            and feature.get("source_activation") == "nonactivatable"
            and feature.get("product_support") == "NOT_RUN"
            and feature.get("production_lexer") == "NOT_RUN"
            and feature.get("production_parser") == "NOT_RUN"
            and feature.get("integrated_checker") == "NOT_RUN"
            and feature.get("runtime_xvm") == "NOT_RUN"
            and feature.get("artifact_trace_refs")
            == ["spec/contracts/enum-derived-capabilities.json"]
            and feature.get("normative_trace_refs", {}).get("productions") == []
            for feature in edc_features
        )
        and all(
            edc_frontend.get(feature_id, {}).get("parser_cover_grammar") is False
            and edc_frontend.get(feature_id, {}).get("source_activation")
            == "nonactivatable"
            for feature_id in edc_frontend_ids
        )
        and "enum#increasing" not in grammar
        and "enum#decreasing" not in grammar
        and "~>" not in grammar,
        "EDC_NONACTIVATABLE_FEATURE_FENCE",
        f"features={sorted(edc_feature_ids)} frontend={sorted(edc_frontend_ids)}",
    )
    trn_case_by_id = {row.get("fixture_id"): row for row in trn_rows}
    trn_required_axes = {f"TRN-R1-{kind}-{index:03d}" for kind, index in (
        [("NEG", value) for value in range(19, 30)] + [("POS", 30), ("POS", 31)]
    )}
    check(
        trn_required_axes <= set(trn_case_by_id)
        and all(trn_case_by_id[fixture_id].get("commit_count") == 0 for fixture_id in trn_required_axes)
        and all(
            trn_case_by_id[f"TRN-R1-NEG-{index:03d}"].get("diagnostic_or_null")
            == "ENUM_PATTERN_CASE_OR_PAYLOAD_MISMATCH"
            for index in range(19, 24)
        )
        and all(
            trn_case_by_id[f"TRN-R1-NEG-{index:03d}"].get("diagnostic_or_null")
            == "OR_PATTERN_BINDINGS_INCONSISTENT"
            for index in range(24, 30)
        ),
        "TRN_ENUM_OR_PATTERN_AND_TRANSACTION_AXES",
        f"required={len(trn_required_axes & set(trn_case_by_id))}/13",
    )
    pattern_kinds = parsed.get(root / "spec/patterns/pattern-kinds.json", {})
    pattern_lowering = parsed.get(root / "spec/patterns/pattern-lowering.json", {})
    union_kind = next(
        (row for row in pattern_kinds.get("rows", []) if row.get("pattern_kind_id") == "PK-UNION-ALTERNATIVE-BINDER"),
        {},
    )
    union_lowering = next(
        (row for row in pattern_lowering.get("rows", []) if row.get("lowering_id") == "PL-UNION-ALTERNATIVE-BINDER"),
        {},
    )
    pattern_policies = parsed.get(root / "spec/patterns/pattern-context-policies.json", {})
    expected_union_contexts = {
        "PCTX-GUARDED-LET", "PCTX-IF-LET", "PCTX-WHILE-LET", "PCTX-FOR-LET",
        "PCTX-ASYNC-FOR-LET", "PCTX-STATEMENT-MATCH", "PCTX-VALUE-MATCH",
        "PCTX-DECLARATIVE-CLAUSE", "PCTX-COMPREHENSION-IF-LET",
    }
    policy_union_contexts = {
        row.get("context_id")
        for row in pattern_policies.get("rows", [])
        if "PK-UNION-ALTERNATIVE-BINDER" in row.get("allowed_pattern_kind_ids", [])
    }
    check(
        pattern_kinds.get("counts", {}).get("rows") == len(pattern_kinds.get("rows", [])) == 19
        and pattern_lowering.get("counts", {}).get("rows") == len(pattern_lowering.get("rows", [])) == 19
        and pattern_kinds.get("revision") == PREVIOUS_LANGUAGE_COHERENCE_REVISION
        and pattern_lowering.get("revision") == PREVIOUS_LANGUAGE_COHERENCE_REVISION
        and pattern_policies.get("revision") == PREVIOUS_LANGUAGE_COHERENCE_REVISION
        and all(
            row.get("revision") == PREVIOUS_LANGUAGE_COHERENCE_REVISION
            for row in pattern_kinds.get("rows", [])
            + pattern_lowering.get("rows", [])
            + pattern_policies.get("rows", [])
        )
        and union_kind.get("normalized_variant") == "UnionAlternativeBindPattern"
        and union_kind.get("coverage_contribution") == "SUBJECT_CONSTRUCTOR_CELL"
        and set(union_kind.get("allowed_context_ids", [])) == expected_union_contexts
        and "PK-UNION-ALTERNATIVE-BINDER" in pattern_policies.get("current_pattern_kind_ids", [])
        and policy_union_contexts == expected_union_contexts
        and union_lowering.get("test_kind") == "UNION_INJECTION_TAG_TEST"
        and union_lowering.get("mir_disposition") == "TEST_PROBE_COMMIT_TRACE",
        "TRN_UNION_PATTERN_LOWERING_BINDING",
        f"kind={union_kind.get('normalized_variant')} contexts={sorted(policy_union_contexts)} lowering={union_lowering.get('test_kind')}",
    )
    trn_predicate_ids = {
        "NarrowUnionByPattern", "NormalizeUnion", "MatchExhaustive",
        "GuardPredicateAdmitted", "R0GuardSafe", "RefinementCheckBoundaryAdmitted",
    }
    trn_inputs = [
        row for row in trn_contract.get("predicate_inputs", [])
        if isinstance(row, dict) and row.get("predicate_id") in trn_predicate_ids
    ]
    trn_input_ids = [row.get("fixture_id") for row in trn_inputs]
    trn_input_groups = {
        predicate_id: [row for row in trn_inputs if row.get("predicate_id") == predicate_id]
        for predicate_id in trn_predicate_ids
    }
    trn_predicate_rows = {
        row.get("predicate_id"): row
        for row in predicate_rows
        if row.get("predicate_id") in trn_predicate_ids
    }
    trn_schema_rel = "schemas/language/type-refinement-narrowing-coherence-descriptor.schema.json"
    descriptor_binding_ok = (
        len(trn_inputs) == len(trn_input_ids) == len(set(trn_input_ids)) == 12
        and all(
            len(rows) == 2
            and {row.get("expected") for row in rows} == {"admitted", "rejected"}
            for rows in trn_input_groups.values()
        )
        and set(trn_predicate_rows) == trn_predicate_ids
        and all(
            row.get("input_descriptor") == "TRNCoherenceDescriptor"
            and row.get("input_descriptor_schema") == trn_schema_rel
            for row in trn_predicate_rows.values()
        )
    )
    match_descriptors = [
        row.get("descriptor", {}) for row in trn_input_groups["MatchExhaustive"]
    ]
    union_descriptors = [
        row.get("descriptor", {}) for row in trn_input_groups["NormalizeUnion"]
    ]
    match_binding_ok = all(
        descriptor.get("arms")
        and len(descriptor.get("arms", [])) == len(descriptor.get("arm_order", []))
        and all(
            {"arm_id", "kind", "coverage_cells", "guard_origin", "binder_contract", "entry_place_state", "exit_place_state"}
            <= set(arm)
            for arm in descriptor.get("arms", [])
        )
        for descriptor in match_descriptors
    )
    union_pair_binding_ok = all(
        len(descriptor.get("union_pairs", []))
        == len(descriptor.get("current_alternatives", [])) * (len(descriptor.get("current_alternatives", [])) - 1) // 2
        for descriptor in union_descriptors
    )
    check(
        descriptor_binding_ok and match_binding_ok and union_pair_binding_ok,
        "TRN_PREDICATE_DESCRIPTOR_BINDING",
        f"inputs={len(trn_inputs)} predicates={sorted(trn_predicate_rows)} match={match_binding_ok} pairs={union_pair_binding_ok}",
    )
    opaque_guard = next(
        (row for row in trn_inputs if row.get("fixture_id") == "TRN-DESC-REFINE-NEG"), {}
    ).get("descriptor", {})
    as_option_case = next(
        (row for row in trn_rows if row.get("fixture_id") == "TRN-R1-POS-009"), {}
    )
    check(
        opaque_guard.get("guard_origin") == "DEF_GUARD_OPAQUE"
        and opaque_guard.get("proof_state") == "UNKNOWN"
        and opaque_guard.get("commit_count") == 0
        and as_option_case.get("flow_in") == as_option_case.get("flow_join"),
        "TRN_OPAQUE_GUARD_AND_AS_OPTION_FLOW",
        f"guard={opaque_guard.get('proof_state')} phi={as_option_case.get('flow_in')}->{as_option_case.get('flow_join')}",
    )

    module_fixtures = parsed.get(root / "tests/fixtures/imported/module-api-digest-fixtures.json", {})
    module_positive = module_fixtures.get("positive_fixtures", [])
    callable_rows = [
        symbol
        for fixture in module_positive
        for symbol in fixture.get("payload", {}).get("symbols", [])
        if symbol.get("kind") in {"function", "method"}
    ]
    callable_axis_ok = all(
        row.get("cancellation") in {"forbidden", "propagate", "observe", "shielded_cleanup"}
        and isinstance(row.get("suspends"), bool)
        and row.get("isolation") in {"local", "task", "actor", "global"}
        for row in callable_rows
    )
    callable_channel_ok = True
    for row in callable_rows:
        profile = row.get("responsibility_profile", {})
        channels = []
        if isinstance(profile.get("receiver"), dict):
            channels.append(profile["receiver"])
        channels.extend(profile.get("parameters", []))
        if isinstance(profile.get("result"), dict):
            channels.append(profile["result"])
        channels.extend(profile.get("captures", []))
        channel_ids = [channel.get("channel_id") for channel in channels]
        callable_channel_ok = callable_channel_ok and len(channel_ids) == len(set(channel_ids))
    module_negative_by_id = {
        row.get("fixture_id"): row for row in module_fixtures.get("negative_fixtures", [])
    }
    axis_negative = module_negative_by_id.get("MODULE-API-NEG-CALLABLE-AXES-001", {})
    axis_negative_function = next(
        (
            row for row in axis_negative.get("payload", {}).get("symbols", [])
            if row.get("kind") == "function"
        ),
        {},
    )
    channel_negative = module_negative_by_id.get("MODULE-API-NEG-CALLABLE-CHANNEL-ID-001", {})
    channel_negative_method = next(
        (
            row for row in channel_negative.get("payload", {}).get("symbols", [])
            if row.get("kind") == "method"
        ),
        {},
    )
    channel_negative_profile = channel_negative_method.get("responsibility_profile", {})
    channel_negative_rows = []
    if isinstance(channel_negative_profile.get("receiver"), dict):
        channel_negative_rows.append(channel_negative_profile["receiver"])
    channel_negative_rows.extend(channel_negative_profile.get("parameters", []))
    if isinstance(channel_negative_profile.get("result"), dict):
        channel_negative_rows.append(channel_negative_profile["result"])
    channel_negative_rows.extend(channel_negative_profile.get("captures", []))
    channel_negative_ids = [row.get("channel_id") for row in channel_negative_rows]
    check(callable_axis_ok, "MODULE_API_CALLABLE_AXES_CONCRETE", f"callables={len(callable_rows)}")
    check(callable_channel_ok, "MODULE_API_CALLABLE_CHANNEL_IDS_UNIQUE", f"callables={len(callable_rows)}")
    check(
        "MODULE_API_CALLABLE_RESPONSIBILITY_AXIS_NOT_APPLICABLE"
        in axis_negative.get("expected_errors", [])
        and all(
            axis_negative_function.get(axis) == "not_applicable"
            for axis in ("cancellation", "suspends", "isolation")
        )
        and "MODULE_API_CALLABLE_CHANNEL_ID_DUPLICATE"
        in channel_negative.get("expected_errors", [])
        and len(channel_negative_ids) > len(set(channel_negative_ids))
        and module_fixtures.get("negative_fixture_count")
        == len(module_fixtures.get("negative_fixtures", [])),
        "MODULE_API_CALLABLE_NEGATIVE_COVERAGE",
        f"negative={module_fixtures.get('negative_fixture_count')}",
    )

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
    lane_ids = [row.get("lane_id") for row in lanes]
    lane_status = {row.get("lane_id"): row.get("status") for row in lanes}
    check(len(lanes) == 15 and len(set(lane_ids)) == 15 and all(lane_status.get(lane_id) == "NOT_RUN" for lane_id in lane_ids), "PRODUCT_EVIDENCE_HONESTY", str(len(lanes)))
    implementation_text = (root / "current/implementation-status.yaml").read_text(encoding="utf-8")
    implementation_rows = dict(re.findall(r"^  ([a-z0-9_]+): (NOT_RUN|BLOCKED|FAILED|PASSED_FOCUSED|PASSED_INTEGRATED|PASSED_INDEPENDENT)$", implementation_text, re.MULTILINE))
    check(set(implementation_rows) == set(lane_ids) and implementation_rows == lane_status, "IMPLEMENTATION_STATUS_PARITY", f"registry={len(lane_ids)} yaml={len(implementation_rows)}")

    management_text = (root / "governance/policies/management-policy.yaml").read_text(encoding="utf-8")
    policy_values: dict[str, str] = {}
    clause_match = re.search(r"^  clause_id: (\S+)$", management_text, re.MULTILINE)
    if clause_match:
        policy_values["clause_id"] = clause_match.group(1)
    for key in ("statement", "restriction_rule", "visibility_rule"):
        match = re.search(rf'^  {key}: "([^"]+)"$', management_text, re.MULTILINE)
        if match:
            policy_values[key] = match.group(1)
    digest_match = re.search(r"^  clause_digest: ([0-9a-f]{64})$", management_text, re.MULTILINE)
    computed_expr_digest = canonical_sha(policy_values) if set(policy_values) == set(EXPR_FIELDS) else ""
    check(
        management_text.count("clause_id: EXPR-001") == 1
        and policy_values == EXPR_FIELDS
        and bool(digest_match)
        and digest_match.group(1) == computed_expr_digest == EXPR_DIGEST,
        "EXPR_NORMATIVE_AUTHORITY",
        f"count={management_text.count('clause_id: EXPR-001')} digest={computed_expr_digest}",
    )
    binding = (
        "[EXPR-001_BINDING]\n"
        "clause_id: EXPR-001\n"
        f"authority: {EXPR_AUTHORITY}\n"
        f"clause_digest: {EXPR_DIGEST}\n"
        "classification: non-authoritative projection"
    )
    review_consumers = sorted(
        path for path in (root / "governance/templates").glob("*Review*")
        if path.is_file()
    )
    text_consumers = [root / rel for rel in EXPR_TEXT_CONSUMERS] + review_consumers
    for path in text_consumers:
        text = path.read_text(encoding="utf-8")
        duplicate_normative = any(value in text for key, value in EXPR_FIELDS.items() if key != "clause_id")
        check(
            text.count(binding) == 1 and not duplicate_normative,
            "EXPR_CONSUMER_BINDING",
            path.relative_to(root).as_posix(),
        )
    check(len(review_consumers) == 7, "EXPR_REVIEW_TEMPLATE_DISCOVERY", str(len(review_consumers)))
    if args.candidate:
        state = parsed.get(root / "release/candidate-state.json", {})
        check(state.get("candidate_revision") == revision and state.get("authority_digest") == computed_authority and state.get("current_pointer_published") is False, "CANDIDATE_STATE", str(state.get("candidate_revision")))
    else:
        pointer = parsed.get(root / "current/current-pointer.json", {})
        check(set(pointer) == EXPECTED_POINTER_KEYS, "POINTER_REQUIRED_KEYS", f"missing={sorted(EXPECTED_POINTER_KEYS - set(pointer))} extra={sorted(set(pointer) - EXPECTED_POINTER_KEYS)}")
        check(pointer.get("schema") == "deeplus.current-pointer/v2", "POINTER_CLOSED_SHAPE", str(pointer.get("schema")))
        publication_source = pointer.get("publication_authority_source", {})
        audited_baseline = pointer.get("audited_implementation_baseline", {})
        candidate_binding = pointer.get("candidate_binding", {})
        check(
            publication_source == {
                "kind": "git-commit",
                "commit": "b6ff1f6e53ea8a21cfb706864478baa02545d3dd",
                "role": "publication_authority_source",
                "repository": "https://github.com/howork/Deeplus.git",
            },
            "POINTER_PUBLICATION_SOURCE",
            str(publication_source),
        )
        check(
            audited_baseline == {
                "kind": "git-commit",
                "commit": "4c85d5b923ee0a58ec6993bb0552e4d0aa7e24d9",
                "repository": "https://github.com/howork/Deeplus.git",
                "branch": "main",
                "role": "document_consistency_repair_base",
            },
            "POINTER_AUDITED_BASELINE",
            str(audited_baseline),
        )
        check(
            candidate_binding == {
                "mode": "external_post_commit_receipt_required",
                "receipt_location": "external_result_pack",
                "current_binding": False,
                "self_binding_forbidden": True,
            },
            "POINTER_EXTERNAL_BINDING",
            str(candidate_binding),
        )
        snapshot = pointer.get("source_snapshot")
        check(snapshot is None or (set(snapshot) == {"library_file_id", "sha256"} and bool(re.fullmatch(r"[0-9a-f]{64}", snapshot.get("sha256", "")))), "POINTER_SOURCE_SNAPSHOT", str(snapshot))
        git_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-git-binding-receipt.json", {})
        check(
            git_receipt.get("result") == "PASS_REVIEWED_HEAD"
            and git_receipt.get("scope") == "historical_reviewed_head"
            and git_receipt.get("current_binding") is False
            and git_receipt.get("reviewed_head") == "989bef9da472348971e56fafb2c9abc550100226"
            and git_receipt.get("pull_request") == 7
            and publication_source.get("repository") == git_receipt.get("repository")
            and publication_source.get("commit") == git_receipt.get("source_authority_commit"),
            "POINTER_SOURCE_BINDING", str(publication_source),
        )
        snapshot_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-source-snapshot-receipt.json", {})
        snapshot_object = snapshot_receipt.get("object", {})
        check(bool(snapshot and snapshot.get("library_file_id")), "POINTER_SNAPSHOT_ID", str(snapshot))
        check(
            snapshot_receipt.get("result") == "PASS_DIRECT_BYTES"
            and snapshot == {"library_file_id": snapshot_object.get("library_file_id"), "sha256": snapshot_object.get("sha256")},
            "POINTER_SNAPSHOT_BINDING", str(snapshot),
        )
        predecessor_receipt = parsed.get(root / "release/evidence/current-publication-m1.3-predecessor-receipt.json", {})
        if revision == LANGUAGE_COHERENCE_REVISION:
            expected_predecessor = PREVIOUS_LANGUAGE_COHERENCE_REVISION
        elif revision == POST_PR16_REVISION:
            expected_predecessor = "r51f3-post-pr16-preview-design-r4"
        else:
            expected_predecessor = predecessor_receipt.get(
                "predecessor_revision"
            )
        check(
            predecessor_receipt.get("result") == "PASS_DIRECT_BYTES"
            and pointer.get("previous_pointer") == expected_predecessor
            and bool(re.fullmatch(r"[0-9a-f]{64}", predecessor_receipt.get("pointer_object", {}).get("sha256", ""))),
            "POINTER_PREDECESSOR_BINDING", str(pointer.get("previous_pointer")),
        )
        check(pointer.get("spec_revision") == revision and pointer.get("authority_digest") == computed_authority, "POINTER_AUTHORITY", str(pointer.get("spec_revision")))
        check(pointer.get("product_lanes") == lane_status, "POINTER_LANE_PARITY", f"pointer={len(pointer.get('product_lanes', {}))} registry={len(lane_status)}")
        actions = pointer.get("open_actions", [])
        action_keys = {"id", "priority", "summary", "owner", "tracking_ref", "acceptance_test", "target"}
        action_ids = [row.get("id") for row in actions]
        next_review_ids = [row.split(":", 1)[0] for row in pointer.get("required_next_reviews", [])]
        expected_action_ids = (
            SUCCESSOR_ACTION_IDS
            if revision in {POST_PR16_REVISION, LANGUAGE_COHERENCE_REVISION}
            else EXPECTED_ACTION_IDS
        )
        check(
            action_ids == expected_action_ids
            and (
                next_review_ids == action_ids
                if revision == LEGACY_REVISION
                else pointer.get("required_next_reviews") == EXPECTED_NEXT_REVIEWS
            )
            and len(action_ids) == len(set(action_ids))
            and all(set(row) == action_keys and all(bool(row.get(key)) for key in action_keys) for row in actions),
            "POINTER_ACTION_BINDING", str(action_ids),
        )
        check(
            all(row.get("tracking_ref") == f"deeplus-action:{row.get('id')}" for row in actions)
            and all("issues/6" not in row.get("tracking_ref", "") for row in actions),
            "POINTER_INTERNAL_TRACKING",
            str([row.get("tracking_ref") for row in actions]),
        )
        check(pointer.get("required_next_reviews") == EXPECTED_NEXT_REVIEWS, "POINTER_NEXT_REVIEW_BINDING", str(pointer.get("required_next_reviews")))
        review_index = parsed.get(root / "release/evidence/current-publication-m1.3-role-review-index.json", {})
        review_roles = [row.get("role") for row in review_index.get("reports", [])]
        check(
            review_roles == ["Design_", "Spec_", "Impl_", "Test_", "Devel_", "Archive_", "Build_"]
            and all(bool(re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))) for row in review_index.get("reports", []))
            and review_index.get("reviewed_head") == git_receipt.get("reviewed_head")
            and review_index.get("integrated_gate") == "HOLD",
            "ROLE_REVIEW_INDEX", str(review_roles),
        )
        check(
            review_index.get("static_corpus", {}).get("status") == "PASS_STATIC_ONLY"
            and review_index.get("executable_conformance", {}).get("status") == "NOT_RUN"
            and review_index.get("product_execution") == "NOT_RUN",
            "STATIC_EXECUTABLE_EVIDENCE_SPLIT", str(review_index.get("executable_conformance")),
        )

    language = (root / "spec/language.md").read_text(encoding="utf-8")
    grammar = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    frontend = parsed.get(root / "spec/frontend/frontend-model.json", {})
    check(
        scalar_occurrences(frontend, "FlowBindingArrow") == 1
        and scalar_occurrences(frontend, "FlowBinding") == 0,
        "CMA_FLOW_BINDING_PROJECTION",
        "CST FlowBindingArrow=1; semantic FlowBinding=0",
    )
    expression_operators = frontend.get("pratt", {}).get("expression", {}).get(
        "operators", []
    )
    range_operator = next(
        (row for row in expression_operators if row.get("id") == "range"), {}
    )
    assignment_operator = next(
        (row for row in expression_operators if row.get("id") == "assignment"), {}
    )
    slice_index_owner = frontend.get("pratt", {}).get("slice_index", {})
    ellipsis_stage = next(
        (row for row in frontend.get("stage_names", []) if row.get("surface") == "..."),
        {},
    )
    ellipsis_token = next(
        (
            row
            for row in frontend.get("boundary_policies", [])
            if row.get("id") == "POSITIONAL_REPEAT"
        ),
        {},
    )
    literal_rule = re.search(r"^Literal ::= (.+)$", grammar, re.MULTILINE)
    vocabulary = parsed.get(root / "spec/grammar/keyword-vocabulary.json", {})
    check(
        literal_rule is not None
        and "NullLiteral" not in literal_rule.group(1)
        and 'RecoveryNullLiteral ::= "null" ;' in grammar
        and 'UnfoldClause ::= "for" "..." Pattern "in" Expr ;' in grammar
        and 'IndexSuffix ::= "[" SliceAxisList "]" ;' in grammar
        and 'BoundedListLiteral ::= "[" StaticIntLiteral ".." StaticIntLiteral'
        in grammar
        and range_operator.get("tokens") == [[".."], ["..<"]]
        and range_operator.get("rejected_reserved_spellings")
        == {
            "..>": "RANGE_OPERATOR_SPELLING_NOT_CURRENT",
            "...": "RANGE_OPERATOR_SPELLING_NOT_CURRENT",
        }
        and assignment_operator.get("tokens")
        == [["="], ["+="], ["-="], ["*="], ["/="], ["%="]]
        and slice_index_owner.get("entry") == "SLICE_INDEX_PRATT_ENTRY"
        and slice_index_owner.get("bounds_required") is True
        and slice_index_owner.get("full_axis") == "* (NumericArray axis only)"
        and slice_index_owner.get("empty_axis") == "INDEX_SUFFIX_REQUIRES_AXIS"
        and slice_index_owner.get("anchor_outside_slice_bound_recovery")
        == {
            "diagnostic": "SLICE_ANCHOR_OUTSIDE_SLICE",
            "stage": "parser",
            "semantic_anchor_node_count": 0,
        }
        and ellipsis_stage.get("cst_roles")
        == ["RepeatedPositionalMarker", "UnfoldClause"]
        and ellipsis_stage.get("ast_roles")
        == ["RepeatedPositional", "ComprehensionUnfold"]
        and ellipsis_token.get("contexts")
        == ["parameter", "function_type", "comprehension_unfold_clause"]
        and vocabulary.get("recovery_reserved_words", {}).get("null", {}).get(
            "admitted_as_literal"
        )
        is False,
        "VOI_GRAMMAR_FRONTEND_OWNER_CLOSURE",
        f"literal={literal_rule.group(1) if literal_rule else None} range={range_operator.get('tokens')} assignment={assignment_operator.get('tokens')}",
    )
    basic_index_predicate = predicate_by_id.get("BasicIndexOperatorAdmitted", {})
    index_suffix_diagnostic = diagnostic_by_id.get("INDEX_SUFFIX_REQUIRES_AXIS", {})
    check(
        index_suffix_diagnostic.get("stage") == "parser"
        and slice_index_owner.get("empty_axis_recovery_production")
        == "RecoveryEmptyIndexSuffix"
        and basic_index_predicate.get("active_primary_diagnostic")
        == "LOGICAL_INDEX_DOMAIN_MISMATCH"
        and basic_index_predicate.get("diagnostic_refs")
        == ["LOGICAL_INDEX_DOMAIN_MISMATCH"]
        and basic_index_predicate.get("secondary_diagnostics") == []
        and not any(
            row.get("predicate_id") == "BasicIndexOperatorAdmitted"
            and row.get("diagnostic_id") == "INDEX_SUFFIX_REQUIRES_AXIS"
            for row in predicate_relation_rows
        ),
        "VOI_EMPTY_INDEX_SINGLE_OWNER",
        f"parser={index_suffix_diagnostic.get('stage')} primary={basic_index_predicate.get('active_primary_diagnostic')}",
    )
    prelude_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-prelude-signature-catalog.json", "entries"
    )
    forbidden_public_trees = {"RawAst", "ResolvedAst", "TypedAst<T,R>"}
    expected_prelude_entries = (
        language_coherence_contract.get("canonical_counts", {}).get(
            "prelude_entries"
        )
        if revision == LANGUAGE_COHERENCE_REVISION
        else 49
    )
    check(
        len(prelude_rows) == expected_prelude_entries
        and not forbidden_public_trees.intersection(
            {row.get("symbol") for row in prelude_rows}
        )
        and all(symbol not in (root / "library/prelude/prelude.md").read_text(encoding="utf-8") for symbol in forbidden_public_trees),
        "CMA_COMPILER_TREE_BOUNDARY",
        f"prelude_entries={len(prelude_rows)}",
    )
    prelude_by_id = {row.get("entry_id"): row for row in prelude_rows}
    arithmetic_defect = prelude_by_id.get("arithmetic_defect", {})
    index_error = prelude_by_id.get("index_error", {})
    indexable = prelude_by_id.get("indexable", {})
    display_entry = prelude_by_id.get("display", {})
    ord_entry = prelude_by_id.get("ord_t", {})
    check(
        arithmetic_defect.get("symbol") == "ArithmeticDefect"
        and arithmetic_defect.get("kind") == "language_intrinsic_defect"
        and arithmetic_defect.get("signatures")
        == ["prelude intrinsic ArithmeticDefect { overflow; divisionByZero; }"]
        and arithmetic_defect.get("product_support") == "NOT_RUN"
        and index_error.get("symbol") == "IndexError"
        and index_error.get("status") == "stable_design"
        and index_error.get("signatures")
        == ["public enum IndexError { outOfLogicalDomain; keyNotFound; }"]
        and index_error.get("product_support") == "NOT_RUN"
        and "conformance does not activate []" in indexable.get("notes", "")
        and display_entry.get("signatures")
        == ["public trait Display { +def display.() -> String throws Never effects {}; }"]
        and ord_entry.get("signatures")
        == ["public trait Ord<T> { +def compare.(borrow lhs: T, borrow rhs: T) -> Int throws Never effects {}; }"]
        and all(
            diagnostic_by_id.get(diagnostic_id, {}).get("diagnostic_status")
            == "active"
            for diagnostic_id in (
                "NULL_LITERAL_NOT_CURRENT_USE_OPTION_NONE",
                "CUSTOM_OPERATOR_DECLARATION_NOT_CURRENT",
                "FIXED_OPERATOR_TRAIT_DISPATCH_NOT_CURRENT",
                "RANGE_OPERATOR_SPELLING_NOT_CURRENT",
                "INDEX_SUFFIX_REQUIRES_AXIS",
            )
        ),
        "VOI_PRELUDE_AND_DIAGNOSTIC_CLOSURE",
        f"arithmetic_defect={arithmetic_defect.get('entry_id')} index_error={index_error.get('entry_id')} indexable={indexable.get('entry_id')}",
    )
    retired_multiline_diagnostic = "MULTILINE_STRING_INDENT_PREFIX_MISMATCH"
    diagnostic_relation_rows = rows(
        "deeplus-0.1.2-baseline-r51f3-diagnostic-relation-registry.json",
        "relations",
    )
    check(
        retired_multiline_diagnostic not in language
        and all(row.get("diagnostic_id") != retired_multiline_diagnostic for row in diagnostic_rows)
        and all(row.get("diagnostic_id") != retired_multiline_diagnostic for row in diagnostic_relation_rows)
        and all(retired_multiline_diagnostic not in json.dumps(row, ensure_ascii=False) for row in feature_rows)
        and all(retired_multiline_diagnostic not in json.dumps(row, ensure_ascii=False) for row in predicate_rows),
        "CMA_MULTILINE_DIAGNOSTIC_RETIRED",
        retired_multiline_diagnostic,
    )
    lcp_fixtures = parsed.get(
        root / "tests/fixtures/current/multiline-string-lcp-r1.json", {}
    )
    lcp_cases = lcp_fixtures.get("cases", [])
    lcp_ids = [row.get("fixture_id") for row in lcp_cases if isinstance(row, dict)]
    lcp_valid = (
        lcp_fixtures.get("schema") == "deeplus.multiline-string-lcp-fixtures/r1"
        and lcp_fixtures.get("authority") == "CMA-R1-A003"
        and lcp_fixtures.get("evidence_status") == "DESIGN_STATIC_NOT_RUN"
        and lcp_fixtures.get("product_support") == "NOT_RUN"
        and len(lcp_cases) == len(set(lcp_ids)) == 6
    )
    for row in lcp_cases:
        if not isinstance(row, dict):
            lcp_valid = False
            continue
        lines = row.get("content_lines", [])
        expected_prefix = longest_exact_indent_prefix(lines) if isinstance(lines, list) else "\0INVALID"
        dedented = [
            "" if not line.lstrip(" \t") else line[len(expected_prefix):]
            for line in lines
        ] if isinstance(lines, list) and expected_prefix != "\0INVALID" else []
        lcp_valid = lcp_valid and (
            row.get("line_ending") in {"LF", "CRLF"}
            and isinstance(row.get("terminal_content_line_break"), bool)
            and row.get("expected_common_prefix") == expected_prefix
            and row.get("expected_dedented_lines") == dedented
            and row.get("expected_outcome") == "accept"
            and row.get("expected_primary_diagnostic") is None
        )
    lcp_by_id = {row.get("fixture_id"): row for row in lcp_cases if isinstance(row, dict)}
    for left, right in (
        ("LCP-LF-PARITY", "LCP-CRLF-PARITY"),
        ("LCP-NO-TRAILING-CONTENT-NEWLINE", "LCP-TRAILING-CONTENT-NEWLINE"),
    ):
        a, b = lcp_by_id.get(left, {}), lcp_by_id.get(right, {})
        lcp_valid = lcp_valid and all(
            a.get(field) == b.get(field)
            for field in ("content_lines", "expected_common_prefix", "expected_dedented_lines")
        )
    check(lcp_valid, "CMA_MULTILINE_LCP_FIXTURES", f"cases={len(lcp_cases)}")
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
        check(capsule.get("source_revision") == revision and all(not row.get("id", "").startswith("MIG-M1-") for row in capsule.get("open_actions", [])), "ROLE_MEMORY_CURRENT", path.name)
        facts_by_id = {
            row.get("id"): row
            for row in capsule.get("current_facts", [])
            if isinstance(row, dict)
        }
        memory_action_ids = {
            row.get("id")
            for row in capsule.get("open_actions", [])
            if isinstance(row, dict)
        }
        check(
            set(facts_by_id) == {
                "ARCH-001", "EVID-001", "PUB-001", "P1-001",
                "CMA-001", "MIRX1-001", "EXPR-001",
            }
            and "22 total" in facts_by_id.get("P1-001", {}).get("statement", "")
            and "15 product lanes remain NOT_RUN" in facts_by_id.get("EVID-001", {}).get("statement", "")
            and facts_by_id.get("CMA-001", {}).get("introduced")
            == (
                POST_PR16_REVISION
                if revision == LANGUAGE_COHERENCE_REVISION
                else revision
            )
            and "Issue #24 remains open" in facts_by_id.get("MIRX1-001", {}).get("statement", "")
            and memory_action_ids <= {"M13-A002", "M13-A005", "M13-TEST-001"}
            and not {"M13-IMPL-A004", "M13-DEVEL-001"}.intersection(memory_action_ids),
            "CMA_ROLE_MEMORY_ROTATION",
            path.name,
        )
        expr_rows = [row for row in capsule.get("current_facts", []) if row.get("id") == "EXPR-001"]
        check(
            len(expr_rows) == 1
            and expr_rows[0].get("statement") == "Non-authoritative projection; resolve the normative clause by authority path and digest."
            and expr_rows[0].get("authority") == EXPR_AUTHORITY
            and expr_rows[0].get("source") == EXPR_AUTHORITY
            and expr_rows[0].get("clause_digest") == EXPR_DIGEST
            and "github.com/howork/Deeplus/issues/8" not in json.dumps(capsule, ensure_ascii=False),
            "EXPR_MEMORY_BINDING",
            path.name,
        )
    design_memory = parsed.get(root / "roles/current-memory/Design_Deeplus_Current_Memory.json", {})
    design_actions = design_memory.get("open_actions", [])
    design_history = design_memory.get("recent_releases", [])
    pr7_history = [row for row in design_history if row.get("release") == "github-pr-7-historical-merge"]
    check(
        all(row.get("id") != "M13-DESIGN-001" for row in design_actions)
        and all("PR #7" not in json.dumps(row, ensure_ascii=False) and "Draft" not in json.dumps(row, ensure_ascii=False) for row in design_actions)
        and len(pr7_history) == 1
        and "merged=true" in pr7_history[0].get("verdict", "")
        and "draft=false" in pr7_history[0].get("verdict", "")
        and "cec72e38d3de716344b64f049fb7a6fc9c1dd01e" in pr7_history[0].get("verdict", "")
        and all(term in pr7_history[0].get("verdict", "") for term in ("tag", "GitHub Release", "Issue closure", "public license", "product promotion", "not inferred")),
        "DESIGN_PR7_HISTORICAL",
        str(pr7_history),
    )

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
    check(manifest.get("revision") == revision and manifest.get("tree_sha256") == hashlib.sha256(tree_material).hexdigest(), "SOURCE_TREE_AGGREGATE", str(manifest.get("tree_sha256")))

    result = "PASS" if not errors else "FAIL"
    receipt = {
        "schema": "deeplus.canonical-workspace-validation-receipt/v1.1",
        "revision": revision, "mode": "candidate" if args.candidate else "published-current",
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
