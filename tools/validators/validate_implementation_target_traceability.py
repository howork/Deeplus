#!/usr/bin/env python3
"""Validate exact target-profile traceability totality without product overclaim."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
SCHEMA_REL = "schemas/language/implementation-target-traceability-r1.schema.json"
OVERLAY_SPECS = [
    (
        "spec/traceability/implementation-target-profile-r1/scalar-numeric-fixed-operator-evidence-r1.json",
        "schemas/language/scalar-numeric-fixed-operator-evidence-r1.schema.json",
        40,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/lexical-trivia-source-root-evidence-r1.json",
        "schemas/language/lexical-trivia-source-root-evidence-r1.schema.json",
        38,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/numeric-array-shape-inferred-evidence-r1.json",
        "schemas/language/numeric-array-shape-inferred-evidence-r1.schema.json",
        10,
    ),
    (
        "spec/traceability/implementation-target-profile-r1/unified-call-tilde-evidence-r1.json",
        "schemas/language/unified-call-tilde-evidence-r1.schema.json",
        9,
    ),
]
FEATURE_DIR = "spec/features/catalog/chunks"
STAGES = ["SOURCE_GRAMMAR", "AST_FRONTEND", "STATIC_SEMANTICS", "DYNAMIC_LOWERING", "DIAGNOSTICS", "TOOLING_OBLIGATIONS", "CONFORMANCE_TESTS"]
OUTCOMES = ["POSITIVE", "BOUNDARY", "REJECT"]
BASE_STATUSES = {"STABLE_DESIGN", "STDLIB_PROFILE"}
ADDITIONS = {"callable_responsibility_profile_core", "data_shaping_callshape_model", "nominal_prototype_derivation", "numeric_literal_lexical_contract", "source_role_contract", "typed_labeled_materialization_family"}
DISPOSITIONS = {"BOUND_DIRECT", "BOUND_DELEGATED", "NOT_APPLICABLE", "APPLICABLE_BLOCKED_BY_GAP"}
NA_REASONS = {
    "SOURCE_GRAMMAR": {"NA_SOURCE_INTERNAL_NO_PROGRAMMER_FORM", "NA_SOURCE_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "AST_FRONTEND": {"NA_AST_LEXICAL_TRIVIA_ONLY", "NA_AST_NO_PROGRAMMER_VISIBLE_FORM", "NA_AST_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "STATIC_SEMANTICS": {"NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY", "NA_STATIC_STDLIB_PROVIDER_ONLY", "NA_STATIC_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "DYNAMIC_LOWERING": {"NA_DYNAMIC_ALIAS_NORMALIZES_NO_DISTINCT_RUNTIME_IDENTITY", "NA_DYNAMIC_REJECTED_BEFORE_LOWERING", "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR", "NA_DYNAMIC_TOOLING_OR_PUBLICATION_METADATA_ONLY"},
    "DIAGNOSTICS": {"NA_DIAGNOSTIC_NO_REJECTION_WARNING_OR_INFO_CONDITION", "NA_DIAGNOSTIC_INTERNAL_VERIFIER_ONLY"},
    "TOOLING_OBLIGATIONS": {"NA_TOOLING_NO_NEW_SOURCE_OR_OBSERVATION_OBLIGATION", "NA_TOOLING_RUNTIME_ONLY_NO_DEVELOPER_TOOLING_CONTRACT"},
    "CONFORMANCE_TESTS": {"NA_TEST_NO_DISTINCT_REJECTION_CLASS"},
}
BOUNDARIES = {"GRAMMAR_AUTHORITY", "FRONTEND_AUTHORITY", "TYPE_CHECKER_AUTHORITY", "MIR_RUNTIME_AUTHORITY", "DIAGNOSTIC_AUTHORITY", "TOOLING_AUTHORITY", "CONFORMANCE_AUTHORITY", "PRELUDE_PROVIDER_AUTHORITY", "PUBLICATION_AUTHORITY"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest_ids(ids: list[str]) -> str:
    return hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()


def evidence_id(item: dict[str, Any]) -> str:
    material = "\0".join([
        item["class"], item["path"], item["locator_kind"],
        item["locator"], item["stage_role"],
    ])
    return "EV-" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def powershell_ordinal_key(value: str) -> str:
    return value.replace("_", "\0")


def safe_rel(path: str) -> bool:
    value = Path(path)
    return bool(path) and not value.is_absolute() and ".." not in value.parts and "*" not in path and "?" not in path


def resolve_json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    current = value
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def collect_strings(value: Any, output: set[str]) -> None:
    if isinstance(value, dict):
        output.update(str(key) for key in value)
        for item in value.values():
            collect_strings(item, output)
    elif isinstance(value, list):
        for item in value:
            collect_strings(item, output)
    elif isinstance(value, str):
        output.add(value)


@functools.lru_cache(maxsize=None)
def registry_strings(path_text: str) -> frozenset[str]:
    path = Path(path_text)
    output: set[str] = set()
    candidates = [path] if path.is_file() else sorted(path.rglob("*.json"))
    for candidate in candidates:
        if candidate.suffix.lower() == ".json":
            try:
                collect_strings(load(candidate), output)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        else:
            try:
                output.add(candidate.read_text(encoding="utf-8"))
            except (OSError, UnicodeError):
                continue
    return frozenset(output)


def evidence_locator_resolves(root: Path, item: dict[str, Any]) -> bool:
    path = root / item.get("path", "")
    kind = item.get("locator_kind")
    locator = item.get("locator", "")
    evidence_class = item.get("class")
    if not path.exists():
        return False
    if kind == "FILE":
        return path.is_file() and locator in {item.get("path"), path.name}
    if kind == "JSON_POINTER":
        if not path.is_file():
            return False
        try:
            resolve_json_pointer(load(path), locator)
            return True
        except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
            return False
    if kind != "REGISTRY_ID" or not locator:
        return False
    if evidence_class == "GRAMMAR_PRODUCTION_ID":
        if not path.is_file():
            return False
        return bool(re.search(rf"(?m)^\s*{re.escape(locator)}\s*=", path.read_text(encoding="utf-8")))
    if locator in registry_strings(str(path.resolve())):
        return True
    if path.is_file() and path.suffix.lower() != ".json":
        try:
            return locator in path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return False
    return False


def validate(root: Path, metadata: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    overlays = [(rel, load(root / rel), expected) for rel, _, expected in OVERLAY_SPECS]
    overlay_entries: dict[str, dict[str, Any]] = {}
    overlay_bindings: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    overlay_evidence_ids: set[str] = set()
    for rel, overlay, expected in overlays:
        entries = overlay.get("evidence_entries", [])
        bindings = overlay.get("bindings", [])
        require(len(bindings) == expected, f"OVERLAY_BINDING_EXACT:{rel}:{expected}")
        for item in entries:
            key = item.get("evidence_key")
            require(key not in overlay_entries, f"OVERLAY_EVIDENCE_UNIQUE:{rel}:{key}")
            overlay_entries[key] = item
            overlay_evidence_ids.add(evidence_id(item))
        for item in bindings:
            cell = (item.get("feature_id"), item.get("stage"), item.get("outcome"))
            require(cell not in overlay_bindings, f"OVERLAY_BINDING_UNIQUE:{rel}:{cell}")
            overlay_bindings[cell] = item
    require(len(overlay_bindings) == 97, "OVERLAY_BINDING_EXACT_TOTAL_97")

    feature_rows: list[dict[str, Any]] = []
    for path in sorted((root / FEATURE_DIR).glob("part-*.json")):
        feature_rows.extend(load(path))
    by_id = {row["feature_id"]: row for row in feature_rows}
    target = sorted(row["feature_id"] for row in feature_rows if row.get("status_enum") in BASE_STATUSES or row["feature_id"] in ADDITIONS)
    excluded = sorted(set(by_id) - set(target), key=powershell_ordinal_key)
    ids = [row.get("feature_id") for row in rows]

    require(len(feature_rows) == 723, "CATALOG_COUNT")
    require(len(target) == 469 and digest_ids(target) == "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435", "TARGET_IDENTITY")
    require(len(excluded) == 254 and digest_ids(excluded) == "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7", "EXCLUDED_IDENTITY")
    require(metadata.get("target_count") == len(target) and metadata.get("target_feature_id_list_sha256") == digest_ids(target), "METADATA_TARGET_IDENTITY")
    require(metadata.get("excluded_count") == len(excluded) and metadata.get("excluded_feature_id_list_sha256") == digest_ids(excluded), "METADATA_EXCLUDED_IDENTITY")
    require(len(rows) == 469, "ROW_COUNT")
    require(ids == target, "ROW_EXACT_SORTED_TARGET_SET")
    require(len(set(ids)) == len(ids) and len({str(value).casefold() for value in ids}) == len(ids), "ROW_UNIQUE")

    evidence_rows = metadata.get("evidence_registry", [])
    evidence = {row.get("evidence_id"): row for row in evidence_rows}
    require(len(evidence) == len(evidence_rows), "EVIDENCE_UNIQUE")
    for ev_id, item in evidence.items():
        path = item.get("path", "")
        require(safe_rel(path), f"EVIDENCE_PATH_SAFE:{ev_id}")
        require((root / path).exists(), f"EVIDENCE_PATH_EXISTS:{ev_id}")
        # Bounded evidence-closure overlays add locator-resolution enforcement.
        # Legacy registry rows retain their R53 existence-level validation until
        # their own bounded evidence-closure cluster upgrades them.
        if ev_id in overlay_evidence_ids:
            require(evidence_locator_resolves(root, item), f"EVIDENCE_LOCATOR_RESOLVES:{ev_id}")
        require(item.get("evidence_level") == "E2_STRUCTURED_STATIC", f"EVIDENCE_LEVEL:{ev_id}")

    direct = delegated = na = blocked = 0
    for row in rows:
        feature_id = row.get("feature_id")
        catalog = by_id.get(feature_id, {})
        binding = row.get("catalog_binding", {})
        require(binding.get("status_enum") == catalog.get("status_enum"), f"CATALOG_STATUS:{feature_id}")
        require(binding.get("feature_kind") == catalog.get("feature_kind"), f"CATALOG_KIND:{feature_id}")
        require(binding.get("source_activation") == catalog.get("source_activation"), f"CATALOG_ACTIVATION:{feature_id}")
        require(row.get("product_execution") == "NOT_RUN", f"PRODUCT_EXECUTION:{feature_id}")
        stages = row.get("stages", [])
        require([stage.get("stage") for stage in stages] == STAGES, f"STAGE_ORDER:{feature_id}")
        for stage in stages:
            stage_name = stage.get("stage")
            cells = stage.get("outcomes", [stage])
            if stage_name == "CONFORMANCE_TESTS":
                require([cell.get("outcome") for cell in cells] == OUTCOMES, f"TEST_OUTCOME_ORDER:{feature_id}")
                require(stage.get("product_execution") == "NOT_RUN", f"TEST_PRODUCT:{feature_id}")
            for cell in cells:
                outcome = cell.get("outcome") if stage_name == "CONFORMANCE_TESTS" else None
                overlay_binding = overlay_bindings.get((feature_id, stage_name, outcome))
                disposition = cell.get("disposition")
                require(disposition in DISPOSITIONS, f"DISPOSITION:{feature_id}:{stage_name}")
                refs = cell.get("evidence_refs", [])
                require(all(ref in evidence for ref in refs), f"EVIDENCE_REF:{feature_id}:{stage_name}")
                if disposition == "BOUND_DIRECT":
                    direct += 1
                    require(bool(refs), f"DIRECT_WITHOUT_EVIDENCE:{feature_id}:{stage_name}")
                    require(not cell.get("blocked_gap_ids"), f"DIRECT_BLOCKED:{feature_id}:{stage_name}")
                elif disposition == "NOT_APPLICABLE":
                    na += 1
                    detail = cell.get("not_applicable") or {}
                    require(detail.get("reason_code") in NA_REASONS.get(stage_name, set()), f"NA_REASON:{feature_id}:{stage_name}")
                    require(detail.get("authority_boundary") in BOUNDARIES, f"NA_BOUNDARY:{feature_id}:{stage_name}")
                    just = detail.get("justification_evidence_refs", [])
                    require(bool(just) and all(ref in evidence for ref in just), f"NA_JUSTIFICATION:{feature_id}:{stage_name}")
                    require(bool(detail.get("rationale")), f"NA_RATIONALE:{feature_id}:{stage_name}")
                elif disposition == "APPLICABLE_BLOCKED_BY_GAP":
                    blocked += 1
                    require(cell.get("blocked_gap_ids") == ["IR-XCUT-P1-054"], f"BLOCKED_GAP:{feature_id}:{stage_name}")
                    require(bool(refs), f"BLOCKED_WITHOUT_CONTEXT:{feature_id}:{stage_name}")
                elif disposition == "BOUND_DELEGATED":
                    delegated += 1
                    require(cell.get("delegate_feature_id") in set(target), f"DELEGATE_TARGET:{feature_id}:{stage_name}")
                if overlay_binding is not None:
                    expected_refs = sorted(
                        evidence_id(overlay_entries[key])
                        for key in overlay_binding.get("evidence_keys", [])
                    )
                    require(disposition == overlay_binding.get("disposition"), f"OVERLAY_DISPOSITION:{feature_id}:{stage_name}:{outcome}")
                    if disposition == "NOT_APPLICABLE":
                        actual_refs = sorted((cell.get("not_applicable") or {}).get("justification_evidence_refs", []))
                    else:
                        actual_refs = sorted(refs)
                    require(actual_refs == expected_refs, f"OVERLAY_EVIDENCE_REFS:{feature_id}:{stage_name}:{outcome}")
                    require(not cell.get("blocked_gap_ids"), f"OVERLAY_STILL_BLOCKED:{feature_id}:{stage_name}:{outcome}")
                    if disposition == "BOUND_DELEGATED":
                        require(cell.get("delegate_feature_id") == overlay_binding.get("delegate_feature_id"), f"OVERLAY_DELEGATE:{feature_id}:{stage_name}:{outcome}")

    counts = metadata.get("derived_counts", {})
    require(counts.get("feature_rows") == 469, "DERIVED_FEATURE_ROWS")
    require(counts.get("stage_cells") == 3283, "DERIVED_STAGE_CELLS")
    require(counts.get("test_outcome_cells") == 1407, "DERIVED_TEST_CELLS")
    require(counts.get("bound_direct_cells") == direct, "DERIVED_DIRECT")
    require(counts.get("bound_delegated_cells") == delegated, "DERIVED_DELEGATED")
    require(counts.get("not_applicable_cells") == na, "DERIVED_NA")
    require(counts.get("applicable_blocked_cells") == blocked, "DERIVED_BLOCKED")
    require(counts.get("missing_cells") == 0 and counts.get("conflict_cells") == 0, "DERIVED_NO_MISSING_CONFLICT")
    require(counts.get("product_not_run_rows") == 469, "DERIVED_PRODUCT")
    require(
        (direct, delegated, na, blocked) == (2438, 2, 500, 1281),
        "R57_EXACT_POST_OVERLAY_COUNTS",
    )
    governance = metadata.get("governance", {})
    require(governance.get("gap_id") == "IR-XCUT-P1-054", "GOVERNANCE_GAP")
    require(governance.get("gap_status") == "APPROVED_NOT_INTEGRATED_LOCAL_CANDIDATE", "GOVERNANCE_STATUS")
    require(governance.get("semantic_p0") == 0 and governance.get("feature_p1") == "22_OPEN_UNCHANGED", "GOVERNANCE_SEMANTIC")
    require(governance.get("product_lanes") == "15_OF_15_NOT_RUN" and governance.get("e4_e5_evidence_count") == 0, "GOVERNANCE_PRODUCT")
    require(governance.get("github_publication") == "SUSPENDED", "GOVERNANCE_GITHUB")
    return errors


def load_registry(root: Path, metadata_path: Path | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata = load(metadata_path or root / META_REL)
    rows: list[dict[str, Any]] = []
    for chunk in metadata.get("chunks", []):
        rows.extend(load(root / chunk["path"]))
    return metadata, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    metadata, rows = load_registry(root)
    try:
        import jsonschema
        jsonschema.Draft202012Validator(load(root / SCHEMA_REL)).validate(metadata)
        for overlay_rel, overlay_schema_rel, _ in OVERLAY_SPECS:
            jsonschema.Draft202012Validator(load(root / overlay_schema_rel)).validate(
                load(root / overlay_rel)
            )
        schema_error = None
    except ImportError:
        schema_error = None
    except Exception as exc:  # pragma: no cover
        schema_error = f"JSON_SCHEMA:{exc}"
    errors = ([schema_error] if schema_error else []) + validate(root, metadata, rows)
    print(json.dumps({
        "schema": "deeplus.implementation-target-traceability-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "target_rows": len(rows),
        "stage_cells": len(rows) * 7,
        "test_outcome_cells": len(rows) * 3,
        "derived_counts": metadata.get("derived_counts", {}),
        "product_execution": "15_OF_15_NOT_RUN",
        "errors": errors,
        "evidence_honesty": "APPLICABLE_BLOCKED_BY_GAP is trace totality, not implementation readiness or product support.",
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
