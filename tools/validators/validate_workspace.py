#!/usr/bin/env python3
"""Static closure validator for the Deeplus current or candidate workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


LEGACY_REVISION = "r51f3-current-publication-m1.3"
SUCCESSOR_REVISION = "r51f3-post-pr16-preview-design-r4"
EXCLUDED_TREE_PARTS = {".git", "target", "dist", "__pycache__"}
EXPECTED = {
    "features": 681, "diagnostics": 1251, "predicates": 245,
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
    "unicode_char_literal_single_quote_msp": "DEFERRED_PRODUCT_HANDOFF",
    "char_unicode_scalar_value_model": "DEFERRED_PRODUCT_HANDOFF",
    "strict_boolean_word_operators_msp": "DEFERRED_PRODUCT_HANDOFF",
    "sequential_boolean_control_words_msp": "DEFERRED_PRODUCT_HANDOFF",
    "standalone_bang_not_current_not_word_law": "NO_DISTINCT_MIR_OP",
    "rightward_flow_dollar_local_binding_msp": "LAW_PRESENT",
    "optional_chaining_not_current_law": "NOT_APPLICABLE(rejected current surface)",
    "ternary_conditional_expression": "DEFERRED_PRODUCT_HANDOFF",
    "ternary_short_expression_stable_profile": "DEFERRED_PRODUCT_HANDOFF",
    "at_control_expression_family": "GENERIC_LAW_PRESENT",
    "local_value_body_msp": "NO_DISTINCT_MIR_OP",
    "match_exhaustiveness_phase_a": "NOT_APPLICABLE(checker-only rejection before MIR)",
    "match_arm_guard_msp": "GENERIC_LAW_PRESENT",
    "bytes_literal_hash_bytes_msp": "DEFERRED_PRODUCT_HANDOFF",
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
    "spec/frontend/frontend-model.json": "2932c1a7c6f1f933ad1a51d8043f4c583833484a8123c6e0e71782a15d0ce1a9",
    "spec/types/type-system.md": "17ac6b139b0ffc422b091ef97ba900fe9f028400034f3e73534bb5d6c1fdae4a",
    "library/prelude/prelude.md": "71182fc438f64dcae39570824ee479a3f2b402a207f12712593cda108bb63cba",
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
SUCCESSOR_CANONICAL_DELTA_PATHS = {
    "spec/language.md",
    "spec/types/type-system.md",
    "spec/mir/semantics.md",
    "decisions/language/current-decisions.json",
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
        revision in {LEGACY_REVISION, SUCCESSOR_REVISION},
        "REVISION_PARITY",
        revision,
    )

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
    if revision == SUCCESSOR_REVISION:
        required.extend([
            "tools/generators/generate_post_pr16_current_integrity.py",
            "tools/generators/post-pr16-current-integrity.contract.json",
            "tools/validators/run_post_pr16_current_integrity_tests.py",
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

    current_integrity_generator = root / (
        "tools/generators/generate_post_pr16_current_integrity.py"
        if revision == SUCCESSOR_REVISION
        else "tools/generators/generate_current_integrity.py"
    )
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
                or (
                    revision == SUCCESSOR_REVISION
                    and row["path"] in SUCCESSOR_CANONICAL_DELTA_PATHS
                )
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
                    or (
                        revision == SUCCESSOR_REVISION
                        and rel in SUCCESSOR_CANONICAL_DELTA_PATHS
                    )
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
    for key, expected in EXPECTED.items():
        check(actual[key] == expected, "CANONICAL_COUNT", f"{key}={actual[key]} expected={expected}")

    feature_by_id = {row.get("feature_id"): row for row in feature_rows}
    diagnostic_by_id = {row.get("diagnostic_id"): row for row in diagnostic_rows}
    predicate_by_id = {row.get("predicate_id"): row for row in predicate_rows}
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
        len(deferred_required) == 11
        and all(
            f"`{feature_id}`" in mir_section[-1]
            for feature_id in SUPPLEMENTAL_MIR_FEATURE_IDS
        )
        and mir_section[-1].count("also `DEFERRED_PRODUCT_HANDOFF`") == 1
        and "All product lanes remain `NOT_RUN`" in mir_section[-1]
        and "approved future MIR law and a target-bound execution receipt" in mir_section[-1],
        "MIR_DEFERRED_PRODUCT_HANDOFF",
        f"required={len(deferred_required)} supplemental={SUPPLEMENTAL_MIR_FEATURE_IDS}",
    )

    for rel, expected_sha in FROZEN_UNCHANGED_SEMANTIC_HASHES.items():
        if revision == SUCCESSOR_REVISION and rel == "spec/types/type-system.md":
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
        check(
            predecessor_receipt.get("result") == "PASS_DIRECT_BYTES"
            and pointer.get("previous_pointer") == predecessor_receipt.get("predecessor_revision")
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
            SUCCESSOR_ACTION_IDS if revision == SUCCESSOR_REVISION else EXPECTED_ACTION_IDS
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
        check(capsule.get("source_revision") == LEGACY_REVISION and all(not row.get("id", "").startswith("MIG-M1-") for row in capsule.get("open_actions", [])), "ROLE_MEMORY_CURRENT", path.name)
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
