#!/usr/bin/env python3
"""Validate the bounded R82 Map unfold/rest owner closure."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/map-unfold-rest-owner-closure-r1.json"
SCHEMA_REL = "schemas/language/map-unfold-rest-owner-closure-r1.schema.json"
FIXTURE_REL = "tests/fixtures/current/map-unfold-rest-owner-closure-r1.json"
DPG_REL = "spec/grammar/deeplus.dpg"
EBNF_REL = "spec/grammar/deeplus.ebnf"
FRONTEND_REL = "spec/frontend/frontend-model.json"
PARSER_CONTEXT_REL = "spec/grammar/deeplus.parser-contexts.json"
LANGUAGE_REL = "spec/language.md"
TYPE_REL = "spec/types/type-system.md"
PATTERN_KINDS_REL = "spec/patterns/pattern-kinds.json"
PATTERN_LOWERING_REL = "spec/patterns/pattern-lowering.json"
HIR_REL = "schemas/language/canonical-hir-h1.schema.json"
MIR_REL = "spec/mir/semantics.md"
DECISION_REL = "decisions/language/Design_Deeplus_Map_Unfold_Rest_Owner_Closure_R1.md"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def chunk_rows(root: Path, pattern: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob(pattern)):
        value = load(path)
        if isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))
    return rows


def normalized_ebnf_productions(text: str) -> dict[str, str]:
    stripped = re.sub(r"\(\*.*?\*\)", "", text, flags=re.S)
    return {
        match.group(1): re.sub(r"\s+", " ", match.group(2)).strip()
        for match in re.finditer(
            r"(?m)^([A-Za-z][A-Za-z0-9_]*)\s*::=\s*(.*?);",
            stripped,
            flags=re.S,
        )
    }


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    fixture_override: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = copy.deepcopy(contract_override) if contract_override is not None else load(root / CONTRACT_REL)
    fixture = copy.deepcopy(fixture_override) if fixture_override is not None else load(root / FIXTURE_REL)
    schema = load(root / SCHEMA_REL)
    frontend = load(root / FRONTEND_REL)
    parser_context = load(root / PARSER_CONTEXT_REL)
    pattern_kinds = load(root / PATTERN_KINDS_REL)
    pattern_lowering = load(root / PATTERN_LOWERING_REL)
    hir = load(root / HIR_REL)
    dpg = (root / DPG_REL).read_text(encoding="utf-8")
    ebnf = (root / EBNF_REL).read_text(encoding="utf-8")
    language = (root / LANGUAGE_REL).read_text(encoding="utf-8")
    types = (root / TYPE_REL).read_text(encoding="utf-8")
    mir = (root / MIR_REL).read_text(encoding="utf-8")
    decision = (root / DECISION_REL).read_text(encoding="utf-8")
    diagnostics = {row.get("diagnostic_id"): row for row in chunk_rows(root, "spec/diagnostics/catalog/chunks/*.json")}
    features = {row.get("feature_id"): row for row in chunk_rows(root, "spec/features/catalog/chunks/*.json")}

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    try:
        import jsonschema
    except ModuleNotFoundError:
        pass
    else:
        try:
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(contract)
        except Exception as exc:  # noqa: BLE001
            errors.append("G01:SCHEMA_BINDING:" + type(exc).__name__)

    matrix = contract.get("owner_matrix", [])
    require(
        matrix
        == [
            {"channel": "POSITIONAL_RUNTIME", "surface": "*Expr", "owners": ["call_argument", "list_entry", "mutable_list_insertion_payload", "comprehension_source"], "ast_kind": "PositionalUnfold", "source_domain": "FINITE_RUNTIME_POSITIONAL_SEQUENCE"},
            {"channel": "MAP_RUNTIME", "surface": "*Expr", "owners": ["map_literal_entry"], "ast_kind": "MapUnfold", "source_domain": "EXACT_IMMUTABLE_MAP_K_V"},
            {"channel": "MAP_PATTERN_RESIDUAL", "surface": "*RestBinder", "owners": ["map_pattern_entry"], "ast_kind": "MapRestPattern", "source_domain": "EXACT_DYNAMIC_KEYED_RESIDUAL_MAP_K_V"},
            {"channel": "STATIC_NAMED", "surface": "**Expr", "owners": ["call_argument", "record_materialization_entry"], "ast_kind": "NamedUnfold", "source_domain": "FINITE_STATIC_RECORD_OR_NAMED_PACK_ROW"},
        ],
        "G02",
        "OWNER_MATRIX_EXACT",
    )
    parser = contract.get("parser_contract", {})
    require(
        parser
        == {
            "map_literal_entry": "Expr ':' Expr | '*' Expr",
            "map_pattern_entry": "Pattern ':' (Literal | '^' StablePatternValue) | '*' (Name | '_')",
            "map_comprehension_head": "Expr ':' Expr",
            "general_star_prefix_parselet": False,
            "expected_type_selects_channel": False,
            "overload_selects_channel": False,
            "runtime_shape_selects_channel": False,
            "legacy_alias_count": 0,
        },
        "G02",
        "PARSER_CONTRACT_EXACT",
    )

    require("| '*' (Name | '_')>]" in dpg and "MapEntry    := Expr ':' Expr | '*' Expr ;" in dpg, "G03", "DPG_MAP_STAR_SURFACES")
    require("'#' ~map '{' Expr ':' Expr CompClause+ '}'" in dpg, "G03", "DPG_MAP_COMPREHENSION_PAIR_ONLY")
    require("MapEntry    := Expr ':' Expr | '**' Expr" not in dpg and "| '..' (Name | '_')>]" not in dpg, "G03", "DPG_LEGACY_MAP_SURFACE_ZERO")
    productions = normalized_ebnf_productions(ebnf)
    require(productions.get("MapRestPattern") == '"*" RestBinder', "G03", "EBNF_MAP_REST_STAR")
    require(productions.get("MapEntry") == 'Expr ":" Expr | "*" Expr', "G03", "EBNF_MAP_UNFOLD_STAR")
    require(productions.get("MapComprehensionExpr") == '"#" "map" "{" Expr ":" Expr ComprehensionClause+ "}"', "G03", "EBNF_MAP_COMPREHENSION_PAIR_ONLY")
    require("Status: NONAUTHORITATIVE_DIFFERENTIAL_SURFACE_CENSUS" in ebnf and "spec/grammar/deeplus.dpg" in ebnf, "G03", "EBNF_AUTHORITY_HEADER")
    require(parser_context.get("externalized_registries", {}).get("hard_and_contextual_words") == "spec/grammar/keyword-vocabulary.json", "G03", "PARSER_CONTEXT_VOCAB_PATH")
    require(parser_context.get("map_structural_owner_policy") == {"map_literal_entry": {"surface": "*Expr", "cst_kind": "MapUnfoldEntry", "ast_kind": "MapUnfold", "source_domain": "EXACT_IMMUTABLE_MAP_K_V"}, "map_pattern_remainder": {"surface": "*RestBinder", "cst_kind": "MapRestPattern", "ast_kind": "MapRestPattern", "source_domain": "EXACT_DYNAMIC_KEYED_RESIDUAL_MAP_K_V"}, "map_comprehension_head": {"surface": "Expr ':' Expr", "unfold_head_allowed": False}, "legacy_alias_count": 0, "general_star_prefix_parselet": False, "commit_before_type_or_overload_selection": True}, "G03", "PARSER_CONTEXT_MAP_OWNER_POLICY")

    owner = next((row for row in frontend.get("boundary_policies", []) if row.get("id") == "STRUCTURAL_UNFOLD_BY_OWNER"), {})
    require(owner.get("surfaces") == {"positional": "*Expr", "static_named": "**Expr", "runtime_map": "*Expr", "map_pattern_remainder": "*RestBinder"}, "G04", "FRONTEND_SURFACE_MATRIX")
    require(owner.get("owners") == {"positional": ["call_argument", "list_entry", "mutable_list_insertion_payload", "comprehension_source"], "static_named": ["call_argument", "record_materialization_entry"], "runtime_map": ["map_literal_entry"], "map_pattern_remainder": ["map_pattern_entry"]}, "G04", "FRONTEND_OWNER_MATRIX")
    require(owner.get("general_expression_prefix_parselet") is False and owner.get("runtime_shape_selection") is False, "G04", "FRONTEND_NO_DEFERRED_CHANNEL")
    double_star = next((row for row in frontend.get("stage_names", []) if row.get("surface") == "**"), {})
    require("MapUnfoldPrefixMarker" not in double_star.get("cst_roles", []) and "MapUnfold" not in double_star.get("ast_roles", []), "G04", "DOUBLE_STAR_NOT_MAP_OWNER")
    patterns = frontend.get("pattern_frontend_contract", {})
    require("*_ or *name" in patterns.get("map_entry_direction_current", ""), "G04", "FRONTEND_MAP_PATTERN_STAR")

    require("owner-bounded `*base` unfolds" in language and "`*rest`/`*_`" in language, "G05", "LANGUAGE_CURRENT_SURFACES")
    require("#map{*base for ...}` is\nrejected" in language, "G05", "LANGUAGE_COMPREHENSION_FENCE")
    require("`*_` ignores and `*name` captures" in types, "G05", "TYPE_MAP_RESIDUAL")
    require(pattern_lowering.get("r77_pattern_surface_direction", {}).get("map_remainder_preserved") == "*name/*_", "G05", "PATTERN_LOWERING_SURFACE")
    kind_text = json.dumps(pattern_kinds, ensure_ascii=False)
    require("`*_` permits additional keys" in kind_text and "`*rest` captures the exact residual Map" in kind_text, "G05", "PATTERN_KIND_SURFACE")

    map_entry = hir.get("$defs", {}).get("MapLiteralEntry", {})
    map_plan = hir.get("$defs", {}).get("MapLiteralPlan", {})
    require('"const": "UNFOLD"' in json.dumps(map_entry, sort_keys=True) and '"const": "DIRECT"' in json.dumps(map_entry, sort_keys=True), "G06", "HIR_MAP_ENTRY_VARIANTS")
    require("LATER_OCCURRENCE_REPLACES" in json.dumps(map_plan) and "COMMIT_AFTER_COMPLETE_SUCCESS" in json.dumps(map_plan), "G06", "HIR_MAP_PLAN_SEALED")
    require("Runtime Map unfold remains\ndistinct from static-label call unfold" in mir, "G06", "MIR_CHANNEL_FENCE")

    diag = contract.get("diagnostics", {})
    for diagnostic_id in diag.values():
        require(diagnostic_id in diagnostics, "G07", "DIAGNOSTIC_PRESENT:" + str(diagnostic_id))
    require("owner-bounded `*`" in diagnostics.get("MAP_UNFOLD_SPELLING_AMBIGUOUS", {}).get("message", ""), "G07", "DIAGNOSTIC_CANONICAL_SPELLING")
    require("map_runtime_unfold_star_current" in features and "map_unfold_double_star_current" not in features, "G07", "FEATURE_ID_MIGRATED")
    require("`*base`" in features.get("map_literal_unfold", {}).get("notes", ""), "G07", "FEATURE_LITERAL_NOTES")
    require("*name" in features.get("structured_record_map_pattern", {}).get("notes", ""), "G07", "FEATURE_PATTERN_NOTES")

    counts = Counter(case.get("class") for case in fixture.get("cases", []))
    expected = fixture.get("expected_counts", {})
    require(len(fixture.get("cases", [])) == expected.get("cases") == 12 and counts == Counter({"positive": 4, "boundary": 4, "reject": 4}), "G08", "FIXTURE_CARDINALITY")
    require(all(case.get("expected_residue_count") == 0 for case in fixture.get("cases", []) if case.get("class") == "reject"), "G08", "REJECT_RESIDUE_ZERO")
    require(expected.get("semantic_p0") == 0 and expected.get("feature_p1") == 22 and expected.get("product_lanes") == 15 and expected.get("product_executed") == 0, "G08", "FIXTURE_GOVERNANCE")

    governance = contract.get("governance", {})
    require(governance == {"semantic_p0": 0, "feature_p1": "22_OPEN_UNCHANGED", "product_lanes": "15_OF_15_NOT_RUN", "production_implementation": "NOT_RUN", "github_publication": "NOT_PERFORMED_FOR_R82"}, "G09", "GOVERNANCE_EXACT")
    for fragment in ("gap_id: PREIMPL-P0-004C", "semantic_p0_after_closure: 0", "feature_p1: 22_OPEN_UNCHANGED", "product_lanes: 15/15_NOT_RUN", "LOCAL_STABLE_DESIGN_CLOSURE_NOT_PUBLISHED"):
        require(fragment in decision, "G09", "DECISION_FENCE:" + fragment)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    receipt = {
        "schema": "deeplus.map-unfold-rest-owner-closure-validation-receipt/r1",
        "result": "FAIL" if errors else "PASS",
        "error_count": len(errors),
        "errors": errors,
        "semantic_p0": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
    }
    print(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
