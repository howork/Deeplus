#!/usr/bin/env python3
"""Validate the bounded R55 lexical-trivia/source-root trace overlay.

This is a design-static validator.  PASS does not claim a production lexer,
parser, formatter, checker, runtime, or product execution receipt.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


OVERLAY_REL = (
    "spec/traceability/implementation-target-profile-r1/"
    "lexical-trivia-source-root-evidence-r1.json"
)
OVERLAY_SCHEMA_REL = "schemas/language/lexical-trivia-source-root-evidence-r1.schema.json"
CONTRACT_REL = "spec/contracts/lexical-trivia-source-root-attachment-r1.json"
CONTRACT_SCHEMA_REL = "schemas/language/lexical-trivia-source-root-attachment-r1.schema.json"
FEATURE_DIR = "spec/features/catalog/chunks"

CANONICAL_BASELINE = "39a5d50cc770341c4b9776d00d84520b780d0c62"
LOCAL_PREDECESSOR = "89ded1ab5c9110476f7043e5f44b71ddd72d19a1"
TARGET_COUNT = 469
TARGET_DIGEST = "86414f1c8690515497a5a4c284cfcc22084b0ff2962b8c38b073ac79a6b40435"
EXCLUDED_COUNT = 254
EXCLUDED_DIGEST = "8bf7368f5a219fc17fca9d7e5c84adc0b5f8975eb1a590a04ab15ce92b8c10b7"

FEATURE_IDS = sorted(
    [
        "comment_trivia_lexical_priority_law",
        "documentation_comment_trivia",
        "line_comment_double_slash_trivia",
        "nested_block_comment_slash_dash_trivia",
        "r51a1_machine_closed_lexical_modes",
        "shebang_comment_first_line_trivia",
        "source_root_full_consumption",
        "word_comment_lossless_trivia",
        "word_comment_tokenization_law",
    ]
)

TOP_KEYS = {
    "$schema",
    "schema",
    "revision",
    "canonical_baseline_commit",
    "local_predecessor_commit",
    "candidate_status",
    "feature_ids",
    "evidence_entries",
    "bindings",
    "acceptance_cases",
    "counts",
    "guards",
}
CONTRACT_TOP_KEYS = {
    "$schema",
    "schema",
    "revision",
    "candidate_status",
    "canonical_baseline_commit",
    "local_predecessor_commit",
    "surface_change_count",
    "comment_opener_priority",
    "documentation_attachment",
    "word_comment",
    "source_root_consumption",
    "stage_fences",
    "new_acceptance_cases",
    "new_acceptance_case_count",
    "governance",
}
EVIDENCE_KEYS = {
    "evidence_key",
    "class",
    "path",
    "locator_kind",
    "locator",
    "stage_role",
}
BINDING_KEYS = {
    "feature_id",
    "stage",
    "outcome",
    "disposition",
    "evidence_keys",
    "delegate_feature_id",
    "not_applicable",
}
CASE_KEYS = {
    "case_id",
    "feature_id",
    "outcome",
    "source_or_subject",
    "expected",
    "diagnostic_or_null",
    "assertions",
    "execution_state",
}
CONTRACT_CASE_KEYS = {
    "case_id",
    "feature_id",
    "outcome",
    "source",
    "expected",
    "diagnostic_or_null",
}
OUTCOMES = {"POSITIVE", "BOUNDARY", "REJECT"}
STAGES = {"AST_FRONTEND", "STATIC_SEMANTICS", "DYNAMIC_LOWERING", "CONFORMANCE_TESTS"}
LOCATOR_KINDS = {"FILE", "JSON_POINTER", "REGISTRY_ID"}
STAGE_ROLES = {
    "AST_FRONTEND",
    "STATIC_SEMANTICS",
    "DYNAMIC_LOWERING",
    "CONFORMANCE_TESTS:POSITIVE",
    "CONFORMANCE_TESTS:BOUNDARY",
    "CONFORMANCE_TESTS:REJECT",
}

TEST_OUTCOMES = {
    "comment_trivia_lexical_priority_law": ("POSITIVE", "BOUNDARY", "REJECT"),
    "documentation_comment_trivia": ("BOUNDARY", "REJECT"),
    "line_comment_double_slash_trivia": ("BOUNDARY", "REJECT"),
    "nested_block_comment_slash_dash_trivia": ("BOUNDARY", "REJECT"),
    "r51a1_machine_closed_lexical_modes": ("BOUNDARY", "REJECT"),
    "shebang_comment_first_line_trivia": ("BOUNDARY", "REJECT"),
    "source_root_full_consumption": ("BOUNDARY", "REJECT"),
    "word_comment_lossless_trivia": ("BOUNDARY", "REJECT"),
    "word_comment_tokenization_law": ("BOUNDARY", "REJECT"),
}
STRUCTURAL_STAGES = {
    "comment_trivia_lexical_priority_law": ("AST_FRONTEND", "STATIC_SEMANTICS", "DYNAMIC_LOWERING"),
    "documentation_comment_trivia": ("AST_FRONTEND", "STATIC_SEMANTICS"),
    "line_comment_double_slash_trivia": ("AST_FRONTEND", "STATIC_SEMANTICS"),
    "nested_block_comment_slash_dash_trivia": ("AST_FRONTEND", "STATIC_SEMANTICS"),
    "r51a1_machine_closed_lexical_modes": ("AST_FRONTEND", "STATIC_SEMANTICS", "DYNAMIC_LOWERING"),
    "shebang_comment_first_line_trivia": ("AST_FRONTEND", "STATIC_SEMANTICS"),
    "source_root_full_consumption": ("STATIC_SEMANTICS",),
    "word_comment_lossless_trivia": ("AST_FRONTEND", "STATIC_SEMANTICS"),
    "word_comment_tokenization_law": ("AST_FRONTEND", "STATIC_SEMANTICS"),
}
EXPECTED_CELLS = {
    (feature_id, stage, None)
    for feature_id, stages in STRUCTURAL_STAGES.items()
    for stage in stages
} | {
    (feature_id, "CONFORMANCE_TESTS", outcome)
    for feature_id, outcomes in TEST_OUTCOMES.items()
    for outcome in outcomes
}

NA_CELLS: dict[tuple[str, str, str | None], tuple[str, str]] = {}
for feature_id, stages in STRUCTURAL_STAGES.items():
    for stage in stages:
        if stage == "AST_FRONTEND":
            reason = (
                "NA_AST_NO_PROGRAMMER_VISIBLE_FORM"
                if feature_id == "r51a1_machine_closed_lexical_modes"
                else "NA_AST_LEXICAL_TRIVIA_ONLY"
            )
            boundary = "FRONTEND_AUTHORITY"
        elif stage == "STATIC_SEMANTICS":
            reason = "NA_STATIC_LEXICAL_OR_SYNTACTIC_ONLY"
            boundary = "TYPE_CHECKER_AUTHORITY"
        else:
            reason = "NA_DYNAMIC_STATIC_ONLY_NO_RUNTIME_BEHAVIOR"
            boundary = "MIR_RUNTIME_AUTHORITY"
        NA_CELLS[(feature_id, stage, None)] = (reason, boundary)
NA_CELLS[("line_comment_double_slash_trivia", "CONFORMANCE_TESTS", "REJECT")] = (
    "NA_TEST_NO_DISTINCT_REJECTION_CLASS",
    "CONFORMANCE_AUTHORITY",
)

EXPECTED_DIRECT_CELLS = EXPECTED_CELLS - set(NA_CELLS)
EXPECTED_CONTRACT_CASES = {
    "R55-LEX-P-001": ("comment_trivia_lexical_priority_law", "POSITIVE"),
    "R55-LEX-B-002": ("comment_trivia_lexical_priority_law", "BOUNDARY"),
    "R55-LEX-N-003": ("comment_trivia_lexical_priority_law", "REJECT"),
    "R55-LEX-B-004": ("documentation_comment_trivia", "BOUNDARY"),
    "R55-LEX-N-005": ("documentation_comment_trivia", "REJECT"),
    "R55-LEX-N-006": ("nested_block_comment_slash_dash_trivia", "REJECT"),
    "R55-LEX-B-007": ("shebang_comment_first_line_trivia", "BOUNDARY"),
    "R55-LEX-N-008": ("shebang_comment_first_line_trivia", "REJECT"),
    "R55-LEX-N-009": ("word_comment_tokenization_law", "REJECT"),
    "R55-LEX-B-010": ("source_root_full_consumption", "BOUNDARY"),
}
EXPECTED_TRACE_CASES = {
    "R55-TRACE-001": ("comment_trivia_lexical_priority_law", "POSITIVE"),
    "R55-TRACE-002": ("comment_trivia_lexical_priority_law", "BOUNDARY"),
    "R55-TRACE-003": ("comment_trivia_lexical_priority_law", "REJECT"),
    "R55-TRACE-004": ("documentation_comment_trivia", "BOUNDARY"),
    "R55-TRACE-005": ("documentation_comment_trivia", "REJECT"),
    "R55-TRACE-006": ("nested_block_comment_slash_dash_trivia", "REJECT"),
    "R55-TRACE-007": ("shebang_comment_first_line_trivia", "BOUNDARY"),
    "R55-TRACE-008": ("shebang_comment_first_line_trivia", "REJECT"),
    "R55-TRACE-009": ("word_comment_tokenization_law", "REJECT"),
    "R55-TRACE-010": ("source_root_full_consumption", "BOUNDARY"),
    "R55-TRACE-EX-006": ("line_comment_double_slash_trivia", "BOUNDARY"),
    "R55-TRACE-EX-007": ("nested_block_comment_slash_dash_trivia", "BOUNDARY"),
    "R55-TRACE-EX-009": ("r51a1_machine_closed_lexical_modes", "BOUNDARY"),
    "R55-TRACE-EX-010": ("r51a1_machine_closed_lexical_modes", "REJECT"),
    "R55-TRACE-EX-014": ("source_root_full_consumption", "REJECT"),
    "R55-TRACE-EX-015": ("word_comment_lossless_trivia", "BOUNDARY"),
    "R55-TRACE-EX-016": ("word_comment_lossless_trivia", "REJECT"),
    "R55-TRACE-EX-017": ("word_comment_tokenization_law", "BOUNDARY"),
}

COUNT_KEYS = {
    "feature_count",
    "evidence_entry_count",
    "binding_count",
    "predecessor_blocked_cell_count",
    "bound_direct_transition_count",
    "bound_delegated_transition_count",
    "not_applicable_transition_count",
    "predecessor_total_blocked_cell_count",
    "post_overlay_total_blocked_cell_count",
    "acceptance_case_count",
}
GUARD_VALUES = {
    "target_feature_count": TARGET_COUNT,
    "target_feature_id_list_sha256": TARGET_DIGEST,
    "excluded_feature_count": EXCLUDED_COUNT,
    "excluded_feature_id_list_sha256": EXCLUDED_DIGEST,
    "feature_statuses": "UNCHANGED",
    "source_activation": "none",
    "surface_change_count": 0,
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "m13_actions": "4_OPEN_UNCHANGED",
    "product_lanes": "15_OF_15_NOT_RUN",
    "github_publication": "SUSPENDED",
    "product_execution_receipt_count": 0,
    "implementation_claim": "NONE",
}
CONTRACT_GOVERNANCE = {
    "semantic_p0": 0,
    "feature_p1": "22_OPEN_UNCHANGED",
    "m13_actions": "4_OPEN_UNCHANGED",
    "product_lanes": "15_OF_15_NOT_RUN",
    "product_execution_receipt_count": 0,
    "github_publication": "SUSPENDED",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def contains_registry_id(value: Any, locator: str) -> bool:
    if isinstance(value, str):
        return value == locator
    if isinstance(value, dict):
        if locator in value:
            return True
        return any(contains_registry_id(child, locator) for child in value.values())
    if isinstance(value, list):
        return any(
            child == locator if isinstance(child, str) else contains_registry_id(child, locator)
            for child in value
        )
    return False


def safe_relative(path: str) -> bool:
    candidate = Path(path)
    return (
        bool(path)
        and not candidate.is_absolute()
        and ".." not in candidate.parts
        and "*" not in path
        and "?" not in path
    )


def locator_resolves(root: Path, entry: dict[str, Any]) -> bool:
    relative = entry.get("path", "")
    path = root / relative
    kind = entry.get("locator_kind")
    locator = entry.get("locator", "")
    if not path.exists() or not locator:
        return False
    if kind == "FILE":
        return path.is_file() and locator in {relative, path.name}
    if kind == "JSON_POINTER":
        if not path.is_file():
            return False
        try:
            resolve_json_pointer(load(path), locator)
            return True
        except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError):
            return False
    if kind != "REGISTRY_ID":
        return False
    candidates = [path] if path.is_file() else sorted(path.rglob("*"))
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            if candidate.suffix.lower() == ".json":
                if contains_registry_id(load(candidate), locator):
                    return True
            else:
                text = candidate.read_text(encoding="utf-8")
                if locator in text or re.search(rf"(?m)^\s*{re.escape(locator)}\s*::?=", text):
                    return True
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            continue
    return False


def feature_catalog(root: Path) -> dict[str, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / FEATURE_DIR).glob("part-*.json")):
        rows.extend(load(path))
    return {row["feature_id"]: row for row in rows}


def validate_schemas(root: Path, overlay: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    pairs = (
        (OVERLAY_SCHEMA_REL, overlay, "OVERLAY"),
        (CONTRACT_SCHEMA_REL, contract, "CONTRACT"),
    )
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return errors
    for relative, instance, label in pairs:
        path = root / relative
        if not path.is_file():
            errors.append(f"{label}_SCHEMA_PATH_EXISTS")
            continue
        try:
            schema = load(path)
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(instance)
        except Exception:
            errors.append(f"{label}_JSON_SCHEMA")
    return errors


def validate(
    root: Path,
    overlay: dict[str, Any],
    contract: dict[str, Any] | None = None,
    *,
    validate_schema: bool = False,
) -> list[str]:
    """Return stable error codes for one R55 overlay/contract candidate."""

    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    if contract is None:
        try:
            contract = load(root / CONTRACT_REL)
        except (OSError, ValueError, json.JSONDecodeError):
            contract = {}
            errors.append("CONTRACT_LOAD")

    require(set(overlay) == TOP_KEYS, "OVERLAY_TOP_LEVEL_EXACT_KEYS")
    require(
        overlay.get("$schema")
        == "../../../schemas/language/lexical-trivia-source-root-evidence-r1.schema.json",
        "OVERLAY_SCHEMA_POINTER",
    )
    require(overlay.get("schema") == "deeplus.lexical-trivia-source-root-evidence/r1", "OVERLAY_SCHEMA_ID")
    require(overlay.get("revision") == "r55-local-lexical-trivia-source-root-closure-r1", "OVERLAY_REVISION")
    require(overlay.get("canonical_baseline_commit") == CANONICAL_BASELINE, "OVERLAY_CANONICAL_BASELINE")
    require(overlay.get("local_predecessor_commit") == LOCAL_PREDECESSOR, "OVERLAY_LOCAL_PREDECESSOR")
    require(
        overlay.get("candidate_status") == "NONCANONICAL_DESIGN_STATIC_EVIDENCE_OVERLAY",
        "OVERLAY_CANDIDATE_STATUS",
    )

    require(set(contract) == CONTRACT_TOP_KEYS, "CONTRACT_TOP_LEVEL_EXACT_KEYS")
    require(
        contract.get("$schema")
        == "../../schemas/language/lexical-trivia-source-root-attachment-r1.schema.json",
        "CONTRACT_SCHEMA_POINTER",
    )
    require(contract.get("schema") == "deeplus.lexical-trivia-source-root-attachment/r1", "CONTRACT_SCHEMA_ID")
    require(contract.get("revision") == "r55-local-lexical-trivia-source-root-attachment-r1", "CONTRACT_REVISION")
    require(contract.get("candidate_status") == "STABLE_DESIGN_CONTRACT_LOCAL_CANDIDATE", "CONTRACT_CANDIDATE_STATUS")
    require(contract.get("canonical_baseline_commit") == CANONICAL_BASELINE, "CONTRACT_CANONICAL_BASELINE")
    require(contract.get("local_predecessor_commit") == LOCAL_PREDECESSOR, "CONTRACT_LOCAL_PREDECESSOR")
    require(contract.get("surface_change_count") == 0, "CONTRACT_SURFACE_CHANGE_COUNT_ZERO")

    if validate_schema:
        errors.extend(validate_schemas(root, overlay, contract))

    require(overlay.get("feature_ids") == FEATURE_IDS, "FEATURE_IDS_EXACT_SORTED_9")
    require(len(set(overlay.get("feature_ids", []))) == 9, "FEATURE_IDS_UNIQUE_9")
    catalog = feature_catalog(root)
    for feature_id in FEATURE_IDS:
        row = catalog.get(feature_id)
        require(row is not None, f"CATALOG_FEATURE_EXISTS:{feature_id}")
        if row is None:
            continue
        require(row.get("status_enum") == "STABLE_DESIGN", f"CATALOG_STATUS_UNCHANGED:{feature_id}")
        require(row.get("source_activation") == "none", f"CATALOG_ACTIVATION_UNCHANGED:{feature_id}")
        expected_deps = ["word_comment_lossless_trivia"] if feature_id == "word_comment_tokenization_law" else []
        require(row.get("depends_on") == expected_deps, f"CATALOG_DEPENDENCY_EXACT:{feature_id}")

    entries = overlay.get("evidence_entries", [])
    require(isinstance(entries, list), "EVIDENCE_ENTRIES_ARRAY")
    evidence: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries if isinstance(entries, list) else []):
        require(isinstance(entry, dict) and set(entry) == EVIDENCE_KEYS, f"EVIDENCE_ENTRY_SHAPE:{index}")
        if not isinstance(entry, dict):
            continue
        key = entry.get("evidence_key")
        require(isinstance(key, str) and bool(key), f"EVIDENCE_KEY:{index}")
        if isinstance(key, str):
            require(key not in evidence, f"EVIDENCE_KEY_UNIQUE:{key}")
            evidence[key] = entry
        require(entry.get("locator_kind") in LOCATOR_KINDS, f"EVIDENCE_LOCATOR_KIND:{key}")
        require(entry.get("stage_role") in STAGE_ROLES, f"EVIDENCE_STAGE_ROLE:{key}")
        require(isinstance(entry.get("class"), str) and bool(entry.get("class")), f"EVIDENCE_CLASS:{key}")
        relative = entry.get("path", "")
        require(isinstance(relative, str) and safe_relative(relative), f"EVIDENCE_PATH_SAFE:{key}")
        if isinstance(relative, str) and safe_relative(relative):
            require(locator_resolves(root, entry), f"EVIDENCE_LOCATOR_RESOLVES:{key}")

    bindings = overlay.get("bindings", [])
    require(isinstance(bindings, list), "BINDINGS_ARRAY")
    by_cell: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    evidence_use: Counter[str] = Counter()
    for index, binding in enumerate(bindings if isinstance(bindings, list) else []):
        require(isinstance(binding, dict) and set(binding) == BINDING_KEYS, f"BINDING_SHAPE:{index}")
        if not isinstance(binding, dict):
            continue
        cell = (binding.get("feature_id"), binding.get("stage"), binding.get("outcome"))
        require(cell not in by_cell, f"BINDING_CELL_UNIQUE:{cell}")
        by_cell[cell] = binding
        require(cell in EXPECTED_CELLS, f"BINDING_EXACT_CELL:{index}")
        stage = binding.get("stage")
        if stage == "CONFORMANCE_TESTS":
            require(binding.get("outcome") in OUTCOMES, f"BINDING_TEST_OUTCOME:{index}")
        else:
            require(binding.get("outcome") is None, f"BINDING_STRUCTURAL_OUTCOME_NULL:{index}")
        refs = binding.get("evidence_keys")
        require(isinstance(refs, list) and len(refs) == 1, f"BINDING_ONE_EVIDENCE_KEY:{index}")
        if isinstance(refs, list):
            for ref in refs:
                evidence_use[ref] += 1
            require(all(ref in evidence for ref in refs), f"BINDING_EVIDENCE_EXISTS:{index}")
            expected_role = (
                f"CONFORMANCE_TESTS:{binding.get('outcome')}"
                if stage == "CONFORMANCE_TESTS"
                else stage
            )
            require(
                all(evidence.get(ref, {}).get("stage_role") == expected_role for ref in refs),
                f"BINDING_EVIDENCE_STAGE_ROLE:{index}",
            )
            expected_suffix = binding.get("outcome") if stage == "CONFORMANCE_TESTS" else "STRUCTURAL"
            expected_key = f"R55:{binding.get('feature_id')}:{stage}:{expected_suffix}"
            require(refs == [expected_key], f"BINDING_EVIDENCE_KEY_EXACT:{index}")
        require(binding.get("delegate_feature_id") is None, f"BINDING_NO_DELEGATE:{index}")
        if cell in NA_CELLS:
            require(binding.get("disposition") == "NOT_APPLICABLE", f"NA_DISPOSITION:{index}")
            detail = binding.get("not_applicable")
            require(isinstance(detail, dict), f"NA_DETAIL:{index}")
            if isinstance(detail, dict):
                require(
                    set(detail)
                    == {"reason_code", "authority_boundary", "rationale", "justification_evidence_keys"},
                    f"NA_DETAIL_SHAPE:{index}",
                )
                reason, authority = NA_CELLS[cell]
                require(detail.get("reason_code") == reason, f"NA_REASON:{index}")
                require(detail.get("authority_boundary") == authority, f"NA_AUTHORITY:{index}")
                require(isinstance(detail.get("rationale"), str) and bool(detail.get("rationale")), f"NA_RATIONALE:{index}")
                require(detail.get("justification_evidence_keys") == refs, f"NA_JUSTIFICATION_EXACT:{index}")
        else:
            require(binding.get("disposition") == "BOUND_DIRECT", f"DIRECT_DISPOSITION:{index}")
            require(binding.get("not_applicable") is None, f"DIRECT_NO_NA:{index}")

    require(set(by_cell) == EXPECTED_CELLS, "BINDINGS_EXACT_38_CELLS")
    require(len(bindings) == 38, "BINDING_COUNT_38")
    require(sum(row.get("disposition") == "BOUND_DIRECT" for row in bindings) == 18, "DIRECT_COUNT_18")
    require(sum(row.get("disposition") == "BOUND_DELEGATED" for row in bindings) == 0, "DELEGATED_COUNT_0")
    require(sum(row.get("disposition") == "NOT_APPLICABLE" for row in bindings) == 20, "NA_COUNT_20")
    require(set(evidence) == set(evidence_use), "EVERY_EVIDENCE_ENTRY_USED")
    require(all(count == 1 for count in evidence_use.values()), "EVIDENCE_ENTRY_USED_EXACTLY_ONCE")
    require(len(entries) == 38, "EVIDENCE_ENTRY_COUNT_38")

    cases = overlay.get("acceptance_cases", [])
    require(isinstance(cases, list), "ACCEPTANCE_CASES_ARRAY")
    by_case_id: dict[str, dict[str, Any]] = {}
    case_cells: Counter[tuple[str, str]] = Counter()
    for index, case in enumerate(cases if isinstance(cases, list) else []):
        require(isinstance(case, dict) and set(case) == CASE_KEYS, f"ACCEPTANCE_CASE_SHAPE:{index}")
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id")
        require(isinstance(case_id, str) and bool(case_id), f"ACCEPTANCE_CASE_ID:{index}")
        if isinstance(case_id, str):
            require(case_id not in by_case_id, f"ACCEPTANCE_CASE_ID_UNIQUE:{case_id}")
            by_case_id[case_id] = case
            require(EXPECTED_TRACE_CASES.get(case_id) == (case.get("feature_id"), case.get("outcome")), f"ACCEPTANCE_CASE_EXACT:{case_id}")
        feature_id = case.get("feature_id")
        outcome = case.get("outcome")
        if feature_id in FEATURE_IDS and outcome in OUTCOMES:
            case_cells[(feature_id, outcome)] += 1
        require(isinstance(case.get("source_or_subject"), str) and bool(case.get("source_or_subject")), f"ACCEPTANCE_CASE_SUBJECT:{index}")
        require(isinstance(case.get("expected"), str) and bool(case.get("expected")), f"ACCEPTANCE_CASE_EXPECTED:{index}")
        assertions = case.get("assertions")
        require(isinstance(assertions, dict) and set(assertions or {}) == {"evidence_key", "source_activation"}, f"ACCEPTANCE_CASE_ASSERTIONS:{index}")
        if isinstance(assertions, dict):
            require(assertions.get("source_activation") == "none", f"ACCEPTANCE_CASE_ACTIVATION:{index}")
            require(assertions.get("evidence_key") in evidence, f"ACCEPTANCE_CASE_EVIDENCE:{index}")
        require(case.get("execution_state") == "DESIGN_STATIC_NOT_RUN", f"ACCEPTANCE_CASE_NOT_RUN:{index}")
        if outcome == "REJECT":
            require(case.get("diagnostic_or_null") is not None, f"ACCEPTANCE_CASE_REJECT_DIAGNOSTIC:{index}")
        else:
            require(case.get("diagnostic_or_null") is None, f"ACCEPTANCE_CASE_NONREJECT_NO_DIAGNOSTIC:{index}")

    require(set(by_case_id) == set(EXPECTED_TRACE_CASES), "ACCEPTANCE_CASE_IDS_EXACT_18")
    require(len(cases) == 18, "ACCEPTANCE_CASE_COUNT_18")
    expected_direct_test_cells = {(feature, outcome) for feature, stage, outcome in EXPECTED_DIRECT_CELLS if stage == "CONFORMANCE_TESTS"}
    require(set(case_cells) == expected_direct_test_cells, "ACCEPTANCE_CASE_EXACT_DIRECT_CELL_COVERAGE")
    require(all(count == 1 for count in case_cells.values()), "ACCEPTANCE_CASE_ONE_PER_DIRECT_CELL")

    contract_cases = contract.get("new_acceptance_cases", [])
    require(isinstance(contract_cases, list), "CONTRACT_CASES_ARRAY")
    contract_by_id: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(contract_cases if isinstance(contract_cases, list) else []):
        require(isinstance(case, dict) and set(case) == CONTRACT_CASE_KEYS, f"CONTRACT_CASE_SHAPE:{index}")
        if not isinstance(case, dict):
            continue
        case_id = case.get("case_id")
        if isinstance(case_id, str):
            require(case_id not in contract_by_id, f"CONTRACT_CASE_ID_UNIQUE:{case_id}")
            contract_by_id[case_id] = case
            require(EXPECTED_CONTRACT_CASES.get(case_id) == (case.get("feature_id"), case.get("outcome")), f"CONTRACT_CASE_EXACT:{case_id}")
        require(isinstance(case.get("source"), str) and bool(case.get("source")), f"CONTRACT_CASE_SOURCE:{index}")
        require(isinstance(case.get("expected"), str) and bool(case.get("expected")), f"CONTRACT_CASE_EXPECTED:{index}")
        if case.get("outcome") == "REJECT":
            require(case.get("diagnostic_or_null") is not None, f"CONTRACT_CASE_REJECT_DIAGNOSTIC:{index}")
        else:
            require(case.get("diagnostic_or_null") is None, f"CONTRACT_CASE_NONREJECT_NO_DIAGNOSTIC:{index}")
    require(set(contract_by_id) == set(EXPECTED_CONTRACT_CASES), "CONTRACT_CASE_IDS_EXACT_10")
    require(len(contract_cases) == 10, "CONTRACT_CASE_COUNT_10")
    require(contract.get("new_acceptance_case_count") == 10, "CONTRACT_DECLARED_CASE_COUNT_10")

    contract_pointer_refs = [
        entry
        for entry in entries
        if entry.get("path") == CONTRACT_REL
        and entry.get("class") == "ACCEPTANCE_CASE"
        and entry.get("locator_kind") == "JSON_POINTER"
    ]
    require(len(contract_pointer_refs) == 10, "CONTRACT_ACCEPTANCE_EVIDENCE_COUNT_10")
    resolved_contract_case_ids: list[str] = []
    for index, entry in enumerate(contract_pointer_refs):
        try:
            resolved = resolve_json_pointer(contract, entry["locator"])
        except (KeyError, IndexError, TypeError):
            require(False, f"CONTRACT_ACCEPTANCE_POINTER:{index}")
            continue
        require(isinstance(resolved, dict), f"CONTRACT_ACCEPTANCE_POINTER_OBJECT:{index}")
        if isinstance(resolved, dict):
            resolved_contract_case_ids.append(resolved.get("case_id"))
            feature_from_key = entry["evidence_key"].split(":", 2)[1]
            outcome_from_role = entry["stage_role"].split(":", 1)[1]
            require(resolved.get("feature_id") == feature_from_key, f"CONTRACT_POINTER_FEATURE:{index}")
            require(resolved.get("outcome") == outcome_from_role, f"CONTRACT_POINTER_OUTCOME:{index}")
    require(set(resolved_contract_case_ids) == set(EXPECTED_CONTRACT_CASES), "CONTRACT_CASES_REFERENCED_EXACTLY")
    require(len(resolved_contract_case_ids) == len(set(resolved_contract_case_ids)), "CONTRACT_CASE_REFERENCE_UNIQUE")

    priority = contract.get("comment_opener_priority", {})
    require(priority.get("rule_id") == "CommentOpenerPriorityDeterministic", "CONTRACT_PRIORITY_RULE_ID")
    require(
        priority.get("ordered_openers")
        == [
            "DOC_BLOCK_COMMENT_//!!",
            "DOC_LINE_COMMENT_//!",
            "NESTED_BLOCK_COMMENT_//-DASH_RUN",
            "LINE_COMMENT_//",
        ],
        "CONTRACT_COMMENT_PRIORITY_EXACT",
    )
    require(priority.get("triple_slash_disposition") == "ORDINARY_LINE_COMMENT", "CONTRACT_TRIPLE_SLASH")
    require(priority.get("literal_modes_recognize_comment_openers") is False, "CONTRACT_LITERAL_MODE_FENCE")

    documentation = contract.get("documentation_attachment", {})
    owners = documentation.get("documentable_owner_productions", [])
    require(documentation.get("rule_id") == "DocumentationCommentAttachmentAdmitted", "CONTRACT_DOC_RULE_ID")
    require(isinstance(owners, list) and len(owners) == 55 and len(set(owners)) == 55, "CONTRACT_DOC_OWNER_COUNT_55")
    require(documentation.get("documentable_owner_count") == 55, "CONTRACT_DOC_DECLARED_OWNER_COUNT_55")
    require(documentation.get("failure_diagnostic") == "DOC_COMMENT_NOT_ATTACHED_TO_DECL", "CONTRACT_DOC_FAILURE_DIAGNOSTIC")

    word = contract.get("word_comment", {})
    require(word.get("rule_id") == "WordCommentAttachmentAdmitted", "CONTRACT_WORD_RULE_ID")
    require(word.get("scanner_primitive_exact_domain") == "UnicodeXIDContinue", "CONTRACT_WORD_SCALAR_DOMAIN")
    require(word.get("body_consumption") == "MAXIMAL_ONE_OR_MORE", "CONTRACT_WORD_MAXIMAL_BODY")
    require(word.get("eligible_left_anchor_node_class_count") == 6, "CONTRACT_WORD_ANCHOR_COUNT_6")
    require(len(set(word.get("eligible_left_anchor_node_classes", []))) == 6, "CONTRACT_WORD_ANCHORS_UNIQUE_6")
    require(word.get("semantic_effect_count") == 0, "CONTRACT_WORD_SEMANTIC_EFFECT_ZERO")
    require(
        word.get("ambiguous_attachment_exact_predicate")
        == "VALID_NONEMPTY_BODY_AND_ELIGIBLE_BYTE_ADJACENT_LEFT_ANCHOR_COUNT_NOT_EQUAL_TO_ONE",
        "CONTRACT_WORD_AMBIGUITY_PREDICATE",
    )

    roots = contract.get("source_root_consumption", {})
    expected_roots = [
        "LibrarySourceFile",
        "ExecutableSourceFile",
        "ScriptSourceFile",
        "PreviewLibrarySourceFile",
        "PreviewExecutableSourceFile",
        "PreviewScriptSourceFile",
    ]
    require(roots.get("rule_id") == "SourceRootFullConsumptionAdmitted", "CONTRACT_ROOT_RULE_ID")
    require(roots.get("direct_roots") == expected_roots, "CONTRACT_ROOTS_EXACT_6")
    require(roots.get("direct_root_count") == 6, "CONTRACT_ROOT_COUNT_6")
    require(roots.get("required_terminal") == "EOF_TOKEN", "CONTRACT_ROOT_EOF_TOKEN")
    require(
        roots.get("failure_projection") == "RECOVERY_CST_ONLY_NO_CANONICAL_SOURCE_AST_COMMIT",
        "CONTRACT_ROOT_FAILURE_PROJECTION",
    )

    fences = contract.get("stage_fences", {})
    require(fences.get("cst_trivia_in_normalized_ast") is False, "CONTRACT_FENCE_NO_TRIVIA_AST")
    require(fences.get("lexical_trivia_static_semantic_effect_count") == 0, "CONTRACT_FENCE_STATIC_ZERO")
    require(fences.get("lexical_trivia_dynamic_lowering_count") == 0, "CONTRACT_FENCE_DYNAMIC_ZERO")
    require(fences.get("line_comment_distinct_reject_class_count") == 0, "CONTRACT_FENCE_LINE_REJECT_ZERO")
    require(
        fences.get("rule_ids")
        == [
            "CstTriviaErasedBeforeNormalizedAst",
            "LexicalTriviaHasNoStaticSemanticEffect",
            "LexicalTriviaHasNoDynamicLowering",
            "LineCommentHasNoDistinctRejectClass",
        ],
        "CONTRACT_FENCE_RULE_IDS_EXACT",
    )

    counts = overlay.get("counts", {})
    require(isinstance(counts, dict) and set(counts) == COUNT_KEYS, "COUNTS_EXACT_KEYS")
    expected_counts = {
        "feature_count": 9,
        "evidence_entry_count": 38,
        "binding_count": 38,
        "predecessor_blocked_cell_count": 38,
        "bound_direct_transition_count": 18,
        "bound_delegated_transition_count": 0,
        "not_applicable_transition_count": 20,
        "predecessor_total_blocked_cell_count": 1341,
        "post_overlay_total_blocked_cell_count": 1303,
        "acceptance_case_count": 18,
    }
    if isinstance(counts, dict):
        for key, expected in expected_counts.items():
            require(counts.get(key) == expected, f"COUNT:{key}")

    guards = overlay.get("guards", {})
    require(isinstance(guards, dict) and set(guards) == set(GUARD_VALUES), "GUARDS_EXACT_KEYS")
    if isinstance(guards, dict):
        for key, expected in GUARD_VALUES.items():
            require(guards.get(key) == expected, f"GUARD:{key}")
    governance = contract.get("governance", {})
    require(
        isinstance(governance, dict) and set(governance) == set(CONTRACT_GOVERNANCE),
        "CONTRACT_GOVERNANCE_EXACT_KEYS",
    )
    if isinstance(governance, dict):
        for key, expected in CONTRACT_GOVERNANCE.items():
            require(governance.get(key) == expected, f"CONTRACT_GOVERNANCE:{key}")

    text = json.dumps({"overlay": overlay, "contract": contract}, sort_keys=True)
    require("BOUND_DELEGATED" not in text, "NO_DELEGATED_BINDING")
    require("APPLICABLE_BLOCKED_BY_GAP" not in text, "NO_BLOCKED_DISPOSITION_IN_OVERLAY")
    require("VERIFIED_CLOSED" not in text and "IR-XCUT-P1-054_CLOSED" not in text, "NO_CLOSURE_OVERCLAIM")
    require("15_OF_15_PASS" not in text and '"github_publication": "ENABLED"' not in text, "NO_PRODUCT_OR_GITHUB_OVERCLAIM")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--overlay", type=Path)
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    overlay_path = args.overlay.resolve() if args.overlay else root / OVERLAY_REL
    contract_path = args.contract.resolve() if args.contract else root / CONTRACT_REL
    try:
        overlay = load(overlay_path)
        contract = load(contract_path)
        errors = validate(
            root,
            overlay,
            contract,
            validate_schema=args.overlay is None and args.contract is None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        overlay = {}
        contract = {}
        errors = [f"LOAD:{type(exc).__name__}:{exc}"]
    print(
        json.dumps(
            {
                "schema": "deeplus.lexical-trivia-source-root-trace-validation-receipt/r1",
                "result": "PASS" if not errors else "FAIL",
                "feature_count": len(overlay.get("feature_ids", [])),
                "binding_count": len(overlay.get("bindings", [])),
                "acceptance_case_count": len(overlay.get("acceptance_cases", [])),
                "new_contract_case_count": len(contract.get("new_acceptance_cases", [])),
                "product_execution": "15_OF_15_NOT_RUN",
                "github_publication": "SUSPENDED",
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
