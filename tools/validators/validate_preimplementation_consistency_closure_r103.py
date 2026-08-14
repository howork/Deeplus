#!/usr/bin/env python3
"""Validate the R103 readiness-evidence and parser-authority closure.

This is design/static validation only.  It never claims that a production
lexer, parser, checker, runtime, backend, formatter, or LSP has executed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/preimplementation-consistency-closure-r103.json"
SCHEMA_REL = "schemas/language/preimplementation-consistency-closure-r103.schema.json"
FIXTURE_REL = "tests/fixtures/current/preimplementation-consistency-closure-r103.json"
GLOBAL_TRACE_REL = "spec/contracts/implementation-target-global-trace-closure-r1.json"
RULE_RE = re.compile(
    r"(?m)^([A-Za-z_][A-Za-z0-9_]*)(<[^>\r\n]+>)?\s*(?::=|\r?\n\s*:=)"
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def canonical_sha(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def strip_dpg_comments(text: str) -> str:
    text = re.sub(
        r"/\*.*?\*/",
        lambda match: "\n" * match.group(0).count("\n"),
        text,
        flags=re.S,
    )
    return re.sub(r"(?m)^\s*#.*$", "", text)


def dpg_metrics(text: str) -> tuple[int, int]:
    clean = strip_dpg_comments(text)
    matches = list(RULE_RE.finditer(clean))
    keys: list[str] = []
    families: set[str] = set()
    for index, match in enumerate(matches):
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(clean)
        tail = clean[match.end() : stop]
        quoted = False
        escaped = False
        terminated = False
        for char in tail:
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "'":
                    quoted = False
            elif char == "'":
                quoted = True
            elif char == ";":
                terminated = True
                break
        if not terminated:
            raise ValueError(f"DPG_RULE_TERMINATOR:{match.group(1)}")
        keys.append(match.group(1) + (match.group(2) or ""))
        families.add(match.group(1))
    if len(keys) != len(set(keys)):
        raise ValueError("DPG_DUPLICATE_RULE_CLAUSE")
    return len(keys), len(families)


def global_evidence_metrics(
    metadata: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, Any]:
    ids = {
        row["evidence_id"]
        for row in metadata.get("evidence_registry", [])
        if row.get("path") == GLOBAL_TRACE_REL
    }
    feature_ids: set[str] = set()
    reference_count = 0
    stage_counts: Counter[str] = Counter()
    for feature in rows:
        hit = False
        for stage in feature.get("stages", []):
            if stage.get("stage") == "CONFORMANCE_TESTS":
                for outcome in stage.get("outcomes", []):
                    count = sum(
                        reference in ids
                        for reference in outcome.get("evidence_refs", [])
                    )
                    reference_count += count
                    if count:
                        hit = True
                        stage_counts[f"CONFORMANCE_TESTS_{outcome.get('outcome')}"] += count
            else:
                count = sum(
                    reference in ids for reference in stage.get("evidence_refs", [])
                )
                reference_count += count
                if count:
                    hit = True
                    stage_counts[str(stage.get("stage"))] += count
        if hit:
            feature_ids.add(str(feature.get("feature_id")))
    return {
        "target_rows": len(rows),
        "rows_using_generic_global_evidence": len(feature_ids),
        "generic_global_evidence_refs": reference_count,
        "generic_global_registry_ids": len(ids),
        "reference_stage_counts": dict(stage_counts),
    }


def model_errors(
    root: Path,
    contract: dict[str, Any],
    fixture: dict[str, Any],
    readiness: dict[str, Any],
    frontend: dict[str, Any],
    contexts: dict[str, Any],
    pratt: dict[str, Any],
    vocabulary: dict[str, Any],
    metadata: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "deeplus.preimplementation-consistency-closure/r103":
        errors.append("CONTRACT_IDENTITY")
    items = contract.get("closure_items", [])
    expected_ids = [
        "R103-READY-P0-001",
        "R103-PARSER-P0-002",
        "R103-PARSER-P0-003",
        "R103-PARSER-P0-004",
    ]
    if [item.get("id") for item in items] != expected_ids or any(
        item.get("status") != "CLOSED_LOCAL_DESIGN_STATIC" for item in items
    ):
        errors.append("CLOSURE_ITEM_SET")
        return errors

    readiness_acceptance = items[0].get("acceptance", {})
    if global_evidence_metrics(metadata, rows) != {
        key: readiness_acceptance.get(key)
        for key in (
            "target_rows",
            "rows_using_generic_global_evidence",
            "generic_global_evidence_refs",
            "generic_global_registry_ids",
            "reference_stage_counts",
        )
    }:
        errors.append("GENERIC_EVIDENCE_OVERCLAIM_METRICS")
    if (
        readiness.get("readiness_verdict")
        != "LOCAL_IMPLEMENTATION_HANDOFF_BLOCKED_BY_TWO_READINESS_GATES"
        or readiness.get("governance", {}).get("bootstrap_readiness_blocker_count")
        != 2
        or [row.get("status") for row in readiness.get("readiness_blockers", [])]
        != [
            "OPEN",
            "OPEN_PARTIAL_R102_EIGHT_ACTIONS_ONLY",
            "CLOSED_BY_R104_EXACT_TARGET_PARTITION",
        ]
    ):
        errors.append("READINESS_TRUTH_STATE")

    dpg_text = (root / "spec/grammar/deeplus.dpg").read_text(encoding="utf-8")
    clause_count, family_count = dpg_metrics(dpg_text)
    parser_acceptance = items[1].get("acceptance", {})
    differential = read_json(root / "spec/contracts/parser-grammar-differential-r1.json")
    frontend_parser = frontend.get("parser_grammar_contract", {})
    if (
        (clause_count, family_count) != (303, 282)
        or parser_acceptance.get("dpg_rule_clause_count") != clause_count
        or parser_acceptance.get("dpg_rule_family_count") != family_count
        or differential.get("metrics", {}).get("dpg_rule_clause_count") != clause_count
        or differential.get("metrics", {}).get("dpg_rule_family_count") != family_count
        or frontend_parser.get("context_specialized_clause_count") != clause_count
        or frontend_parser.get("rule_family_count") != family_count
        or "282개 rule family와 303개 context-specialized clause"
        not in (root / "docs/internals/grammar-implementation-contract.md").read_text(
            encoding="utf-8"
        )
    ):
        errors.append("DPG_COUNT_AUTHORITY_PARITY")

    bracket = contexts.get("commitment_policy", {}).get("bracket_primary", {})
    bracket_acceptance = items[2].get("acceptance", {})
    frontend_bracket = (
        frontend.get("pratt", {})
        .get("closed_parse_goal_contract", {})
        .get("bracket_primary_commitment", {})
    )
    if (
        bracket.get("probe") != bracket_acceptance.get("probe")
        or bracket.get("closure_post_markers")
        != bracket_acceptance.get("closure_markers")
        or bracket.get("generator_post_markers")
        != bracket_acceptance.get("generator_markers")
        or bracket.get("fallback") != bracket_acceptance.get("fallback")
        or bracket.get("semantic_lookup_count") != 0
        or frontend_bracket.get("semantic_lookup_count") != 0
        or bracket_acceptance.get("post_commit_fallback_count") != 0
    ):
        errors.append("BRACKET_PRIMARY_COMMITMENT")

    primary_rows = {row.get("id"): row for row in pratt.get("primary_dispatch", [])}
    bounded = items[3].get("acceptance", {})
    language = (root / "spec/language.md").read_text(encoding="utf-8")
    ebnf = (root / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    diagnostics = []
    for path in sorted((root / "spec/diagnostics/catalog/chunks").glob("part-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        diagnostics.extend(value if isinstance(value, list) else value.get("diagnostics", []))
    if (
        bounded.get("bounded_list_surface") != "#list[L..U: elements]"
        or bounded.get("ordinary_list_range_surface") != "[(L..U:step)]"
        or bounded.get("compatibility_alias_count") != 0
        or "BoundedList := '#' ~list '['" not in dpg_text
        or 'BoundedListLiteral ::= "#" "list" "["' not in ebnf
        or "#list[L..U: elements]" not in language
        or primary_rows.get("bounded_list", {}).get("trigger") != "# list ["
        or primary_rows.get("list_or_comprehension", {}).get("grammar_owner")
        != "ListLiteral | ComprehensionExpr"
        or any(row.get("id") == "list_bounded_or_comprehension" for row in primary_rows.values())
        or not any(
            row.get("diagnostic_id") == "BOUNDED_LIST_EXPLICIT_SIGIL_REQUIRED"
            and row.get("diagnostic_status") == "active"
            for row in diagnostics
        )
    ):
        errors.append("BOUNDED_LIST_RANGE_SURFACE_SEPARATION")

    keyword_projection = {
        "hard_keywords": frontend.get("keyword_model", {}).get("hard_reserved", []),
        "contextual_words": frontend.get("keyword_model", {}).get("contextual", []),
        "sigil_role_subset": frontend.get("keyword_model", {}).get(
            "sigil_role_subset", []
        ),
    }
    if (
        "list" not in keyword_projection["contextual_words"]
        or "list" not in keyword_projection["sigil_role_subset"]
        or vocabulary.get("contextual_word_count") != 106
        or vocabulary.get("hard_keywords") != keyword_projection["hard_keywords"]
        or vocabulary.get("contextual_words") != keyword_projection["contextual_words"]
        or vocabulary.get("sigil_role_subset")
        != keyword_projection["sigil_role_subset"]
        or vocabulary.get("projection_sha256") != canonical_sha(keyword_projection)
    ):
        errors.append("LIST_CONTEXTUAL_SIGIL_ROLE")

    expected_cases = {
        "R103-BRACKET-P-001": ("ClosureExpr", None, 1),
        "R103-BRACKET-P-002": ("GeneratorExpr", None, 1),
        "R103-BRACKET-P-003": ("ListExpr", None, 1),
        "R103-BRACKET-B-001": ("ComprehensionExpr", None, 1),
        "R103-BRACKET-R-001": ("ClosureExpr", "CLOSURE_LAMBDA_BODY_REQUIRED", 0),
        "R103-BRACKET-R-002": ("GeneratorExpr", "GENERATOR_SOURCE_EXPRESSION_REQUIRED", 0),
        "R103-BOUNDED-P-001": ("BoundedListExpr", None, 1),
        "R103-BOUNDED-B-001": ("ListExpr", None, 1),
        "R103-BOUNDED-R-001": ("RemovedBoundedListSurface", "BOUNDED_LIST_EXPLICIT_SIGIL_REQUIRED", 0),
        "R103-BOUNDED-R-002": ("BoundedListExpr", "BOUND_LITERAL_LENGTH_MISMATCH", 0),
    }
    cases = fixture.get("cases", [])
    observed_cases = {
        row.get("id"): (
            row.get("owner"),
            row.get("diagnostic"),
            row.get("canonical_ast_count"),
        )
        for row in cases
    }
    if observed_cases != expected_cases or fixture.get("product_execution") != "NOT_RUN":
        errors.append("ACCEPTANCE_FIXTURE_EXACT_SET")

    pointer = read_json(root / "current/current-pointer.json")
    governance = contract.get("governance", {})
    if (
        governance.get("semantic_p0") != 0
        or governance.get("artifact_parser_p0_after_closure") != 0
        or governance.get("feature_p1") != "22_OPEN_EXACT_TYPED_LANES"
        or governance.get("product_lanes") != "15_OF_15_NOT_RUN"
        or len(pointer.get("product_lanes", {})) != 15
        or set(pointer.get("product_lanes", {}).values()) != {"NOT_RUN"}
    ):
        errors.append("GOVERNANCE_FENCE")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract = read_json(root / CONTRACT_REL)
    fixture = read_json(root / FIXTURE_REL)
    readiness = read_json(root / "spec/contracts/implementation-readiness-r99-audit-closure.json")
    frontend = read_json(root / "spec/frontend/frontend-model.json")
    contexts = read_json(root / "spec/grammar/deeplus.parser-contexts.json")
    pratt = read_json(root / "spec/contracts/closed-pratt-parse-goal-contract-r1.json")
    vocabulary = read_json(root / "spec/grammar/keyword-vocabulary.json")
    metadata = read_json(root / "spec/traceability/implementation-target-profile-r1/catalog-metadata.json")
    rows_value = json.loads(
        (root / "spec/traceability/implementation-target-profile-r1/rows.json").read_text(
            encoding="utf-8"
        )
    )
    if not isinstance(rows_value, list):
        raise ValueError("TARGET_ROWS_ARRAY_REQUIRED")
    errors = model_errors(
        root,
        contract,
        fixture,
        readiness,
        frontend,
        contexts,
        pratt,
        vocabulary,
        metadata,
        rows_value,
    )
    mutation_count = 0
    if args.mutations and not errors:
        mutants: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]] = []
        changed = copy.deepcopy(contract)
        changed["closure_items"][0]["acceptance"]["rows_using_generic_global_evidence"] -= 1
        mutants.append((changed, fixture, readiness, contexts, pratt))
        changed_readiness = copy.deepcopy(readiness)
        changed_readiness["readiness_verdict"] = "LOCAL_IMPLEMENTATION_HANDOFF_READY_PENDING_CANONICAL_PUBLICATION"
        mutants.append((contract, fixture, changed_readiness, contexts, pratt))
        changed_contexts = copy.deepcopy(contexts)
        changed_contexts["commitment_policy"]["bracket_primary"]["semantic_lookup_count"] = 1
        mutants.append((contract, fixture, readiness, changed_contexts, pratt))
        changed_pratt = copy.deepcopy(pratt)
        for row in changed_pratt["primary_dispatch"]:
            if row.get("id") == "bounded_list":
                row["trigger"] = "["
        mutants.append((contract, fixture, readiness, contexts, changed_pratt))
        changed_fixture = copy.deepcopy(fixture)
        changed_fixture["cases"][0]["owner"] = "ListExpr"
        mutants.append((contract, changed_fixture, readiness, contexts, pratt))
        for current_contract, current_fixture, current_readiness, current_contexts, current_pratt in mutants:
            if model_errors(
                root,
                current_contract,
                current_fixture,
                current_readiness,
                frontend,
                current_contexts,
                current_pratt,
                vocabulary,
                metadata,
                rows_value,
            ):
                mutation_count += 1
        if mutation_count != len(mutants):
            errors.append(f"MUTATION_SURVIVED:{mutation_count}/{len(mutants)}")

    schema_result = "STRICT_STRUCTURAL_FALLBACK"
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(contract, read_json(root / SCHEMA_REL))
        schema_result = "PASS"
    except ModuleNotFoundError:
        pass
    except Exception as exc:  # pragma: no cover - dependency-specific detail
        errors.append(f"SCHEMA_VALIDATION:{exc}")

    receipt = {
        "schema": "deeplus.preimplementation-consistency-closure-r103-validation/r1",
        "result": "PASS" if not errors else "FAIL",
        "schema_validation": schema_result,
        "closure_items": 4,
        "mutation_count": mutation_count,
        "semantic_p0": 0,
        "artifact_parser_p0_after_closure": 0 if not errors else 4,
        "feature_p1": "22_OPEN_EXACT_TYPED_LANES",
        "product_lanes": "15_OF_15_NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
