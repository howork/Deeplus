#!/usr/bin/env python3
"""Validate the R93 formatter/LSP rebase to the parser authority ensemble."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE_MAIN = "10e64f492f0529610673846139afcf0d95175663"
CONTRACT_REL = "spec/contracts/formatter-lsp-incremental-parsing-contract-r1.json"
SCHEMA_REL = "schemas/language/formatter-lsp-incremental-parsing.schema.json"
FIXTURE_REL = "tests/fixtures/current/formatter-lsp-incremental-parsing-r1.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
AUTHORITY_REL = "spec/contracts/parser-authority-traceability-r1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Formatter_LSP_DPG_Authority_Rebase_R1.md"
FORMATTER_FEATURE_REL = "spec/features/catalog/chunks/part-0006.json"
LSP_FEATURE_REL = "spec/features/catalog/chunks/part-0008.json"
VALIDATOR_REL = "tools/validators/validate_formatter_lsp_dpg_authority_rebase.py"
MUTATION_REL = "tools/validators/run_formatter_lsp_dpg_authority_rebase_mutation_tests.py"

AUTHORITY_SHA256 = "9f8b60146298a930f7fe3f63408a8e89c8ac57e540595902e954d66852792133"
SURFACE_CENSUS = {
    "path": "spec/grammar/deeplus.ebnf",
    "sha256": "f69b2e438df00e62afe805a1bcef2d1b7e069bda988862fa35d58942828d7be2",
    "semantic_authority": False,
    "role": "FORMATTER_CST_AST_DISPOSITION_CROSSWALK_ONLY",
}
AUTHORITY_DIGEST_SET = [
    {
        "axis": "STRUCTURAL_DPG",
        "path": "spec/grammar/deeplus.dpg",
        "sha256": "fefec3a3c8425d4911c8a162fd7f51ee4a63c946f32bcbba0face055a1c9863f",
    },
    {
        "axis": "PARSER_CONTEXT",
        "path": "spec/grammar/deeplus.parser-contexts.json",
        "sha256": "9464f078bfac5429bc71339ed9ea52c68e18dc588fd65ddfb541ed0a8efbefaf",
    },
    {
        "axis": "PRATT",
        "path": "spec/contracts/closed-pratt-parse-goal-contract-r1.json",
        "sha256": "143bfc0248ee473d7d6855cf1145a401ef931fa71a6037049c1e48b5189ccd4b",
    },
    {
        "axis": "SCANNER",
        "path": "spec/contracts/complete-token-lexical-goal-contract-r1.json",
        "sha256": "ad75bdc19e4dcdeed68c77a3db046cf7d1fa57480696a9d60e15b769ef801d46",
    },
]
EXPECTED_INPUTS = {
    "parser_authority": AUTHORITY_REL,
    "structural_grammar": "spec/grammar/deeplus.dpg",
    "parser_contexts": "spec/grammar/deeplus.parser-contexts.json",
    "pratt_contract": "spec/contracts/closed-pratt-parse-goal-contract-r1.json",
    "surface_census": "spec/grammar/deeplus.ebnf",
    "grammar_disposition_registry": "spec/contracts/grammar-production-disposition-registry-r1.json",
    "grammar_topology": "spec/contracts/grammar-topology-closure-r1.json",
    "frontend_model": FRONTEND_REL,
    "recovery_contract": "spec/contracts/frontend-recovery-invalid-tree-contract-r1.json",
    "parser_boundary_contract": "spec/contracts/parser-boundary-match-arm-contract-r1.json",
    "scanner_contract": "spec/contracts/complete-token-lexical-goal-contract-r1.json",
}
EXPECTED_REBASE = {
    "gap_id": "IR-FE-P1-063",
    "baseline_main": BASELINE_MAIN,
    "decision": DECISION_REL,
    "authority_contract": {"path": AUTHORITY_REL, "sha256": AUTHORITY_SHA256},
    "authority_digest_set": AUTHORITY_DIGEST_SET,
    "snapshot_component": "ParserAuthorityDigestSetR1",
    "surface_census": SURFACE_CENSUS,
    "full_parse_reference": "SCANNER_PLUS_DPG_PLUS_PARSER_CONTEXT_PLUS_PRATT_PLUS_LOSSLESS_CST_RECOVERY_PLUS_AST_CHECKER",
    "ebnf_only_admission_count": 0,
    "incremental_source_language_widening_count": 0,
    "tooling_parser_semantic_reselection_count": 0,
}
EXPECTED_FRONTEND_REBASE = {
    "gap_id": "IR-FE-P1-063",
    "baseline_main": BASELINE_MAIN,
    "authority_contract": AUTHORITY_REL,
    "authority_axes": ["STRUCTURAL_DPG", "PARSER_CONTEXT", "PRATT", "SCANNER"],
    "snapshot_component": "ParserAuthorityDigestSetR1",
    "surface_census_semantic_authority": False,
    "structural_cst_owner_identity": "CstStructuralOwnerId",
    "source_root_reparse_on_authority_change": True,
    "old_handle_reuse_on_authority_change": 0,
    "ebnf_only_admission_count": 0,
    "tooling_parser_semantic_reselection_count": 0,
}
EXPECTED_CASE_IDS = [
    "R93-P-01-EXACT-ENSEMBLE",
    "R93-P-02-UNCHANGED-REUSE",
    "R93-P-03-CENSUS-ONLY-REFORMAT",
    "R93-P-04-FULL-PARSE-PARITY",
    "R93-B-01-DPG-DRIFT",
    "R93-B-02-CONTEXT-DRIFT",
    "R93-B-03-PRATT-DRIFT",
    "R93-B-04-SCANNER-DRIFT",
    "R93-N-01-EBNF-ONLY-AUTHORITY",
    "R93-N-02-MISSING-AXIS",
    "R93-N-03-GRAMMAR-SHA-IDENTITY",
    "R93-N-04-CENSUS-PRODUCTION-OWNER",
    "R93-N-05-DIGEST-MISMATCH",
    "R93-N-06-TOOLING-RESELECTION",
    "R93-N-07-SOURCE-WIDENING",
    "R93-N-08-PRODUCT-OVERCLAIM",
]
EXPECTED_MUTATION_IDS = [f"R93-M-{ordinal:02d}-{suffix}" for ordinal, suffix in (
    (1, "PROMOTE-EBNF"),
    (2, "DROP-DPG"),
    (3, "DROP-PARSER-CONTEXT"),
    (4, "DROP-PRATT"),
    (5, "DROP-SCANNER"),
    (6, "RESTORE-GRAMMAR-SHA256"),
    (7, "RESTORE-PRODUCTION-ID"),
    (8, "ALLOW-OLD-HANDLE-REUSE"),
    (9, "ALLOW-TOOLING-RESELECTION"),
    (10, "CLAIM-PRODUCT-PASS"),
)]
CHECK_IDS = [
    "R93_EXACT_AUTHORITY_BYTES",
    "R93_AUTHORITY_ENSEMBLE_LAW",
    "R93_CONTRACT_AND_SCHEMA_BINDING",
    "R93_SNAPSHOT_IDENTITY_BINDING",
    "R93_STRUCTURAL_CST_OWNER_BINDING",
    "R93_REPARSE_AND_LSP_FENCE",
    "R93_FRONTEND_MODEL_BINDING",
    "R93_ACCEPTANCE_CASES_16",
    "R93_MUTATION_DECLARATIONS_10",
    "R93_FEATURE_TRACE_BINDING",
    "R93_GOVERNANCE_FENCE",
    "R93_DECISION_TRACE",
]


def strict_load(path: Path) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        keys = [key for key, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate JSON key in {path}")
        if len(keys) != len({key.casefold() for key in keys}):
            raise ValueError(f"case-fold duplicate JSON key in {path}")
        return dict(pairs)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_row(rows: list[dict[str, Any]], feature_id: str) -> dict[str, Any]:
    matches = [row for row in rows if row.get("feature_id") == feature_id]
    return matches[0] if len(matches) == 1 else {}


def validate_documents(
    root: Path,
    contract: dict[str, Any],
    schema: dict[str, Any],
    fixtures: dict[str, Any],
    frontend: dict[str, Any],
    authority: dict[str, Any],
    formatter_features: list[dict[str, Any]],
    lsp_features: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []

    for row in [{"path": AUTHORITY_REL, "sha256": AUTHORITY_SHA256}, *AUTHORITY_DIGEST_SET, SURFACE_CENSUS]:
        path = root / row["path"]
        if not path.is_file() or sha256(path) != row["sha256"]:
            errors.append(f"authority byte digest drift: {row['path']}")

    ensemble = authority.get("authority_ensemble", {})
    expected_ensemble_paths = {
        "structural_grammar": "spec/grammar/deeplus.dpg",
        "parser_context": "spec/grammar/deeplus.parser-contexts.json",
        "pratt": "spec/contracts/closed-pratt-parse-goal-contract-r1.json",
        "scanner": "spec/contracts/complete-token-lexical-goal-contract-r1.json",
    }
    if (
        {key: ensemble.get(key, {}).get("path") for key in expected_ensemble_paths}
        != expected_ensemble_paths
        or authority.get("surface_census", {}).get("semantic_authority") is not False
        or authority.get("surface_census", {}).get("path") != "spec/grammar/deeplus.ebnf"
        or authority.get("binding_law", {}).get("direct_source_cell_requires_all_authority_axes") is not True
        or authority.get("binding_law", {}).get("ebnf_only_binding_rejected") is not True
        or authority.get("binding_law", {}).get("all_grammar_locators_resolve") is not True
    ):
        errors.append("parser authority ensemble law drift")

    rebase = contract.get("parser_authority_rebase", {})
    schema_rebase = schema.get("properties", {}).get("parser_authority_rebase", {})
    if (
        contract.get("inputs") != EXPECTED_INPUTS
        or rebase != EXPECTED_REBASE
        or "parser_authority_rebase" not in schema.get("required", [])
        or schema_rebase.get("properties", {}).get("snapshot_component", {}).get("const")
        != "ParserAuthorityDigestSetR1"
        or schema_rebase.get("properties", {}).get("surface_census", {}).get("properties", {}).get("semantic_authority", {}).get("const") is not False
    ):
        errors.append("R93 contract/schema authority binding drift")

    identities = contract.get("identity_domains", {})
    snapshot_recipe = identities.get("ParseSnapshotId", {}).get("recipe", [])
    content_recipe = identities.get("CstContentId", {}).get("recipe", [])
    reuse_equalities = identities.get("NodeReuseReceipt", {}).get("required_equalities", [])
    if (
        "parser_authority_digest_set" not in snapshot_recipe
        or "grammar_sha256" in snapshot_recipe
        or "structural_cst_owner_id" not in content_recipe
        or "production_id" in content_recipe
        or "parser_authority_digest_set" not in reuse_equalities
        or "structural_cst_owner_id" not in reuse_equalities
        or "grammar_sha256" in reuse_equalities
        or "production_id" in reuse_equalities
    ):
        errors.append("snapshot or structural CST owner identity drift")

    reparse = contract.get("incremental_reparse", {})
    lsp_binding = contract.get("lsp_snapshot_fence", {}).get("request_binding", [])
    reparse_text = json.dumps(reparse, sort_keys=True)
    if (
        "parser authority digest set" not in reparse_text
        or "structural CST owner" not in reparse_text
        or "production owner" in reparse_text
        or "parser authority digest set" not in lsp_binding
        or "grammar sha256" in lsp_binding
        or rebase.get("incremental_source_language_widening_count") != 0
        or rebase.get("tooling_parser_semantic_reselection_count") != 0
    ):
        errors.append("incremental reparse or LSP authority fence drift")

    frontend_rebase = frontend.get("formatter_lsp_incremental_parsing_contract", {}).get("parser_authority_rebase", {})
    if frontend_rebase != EXPECTED_FRONTEND_REBASE:
        errors.append("frontend parser-authority rebase drift")

    fixture_domain = fixtures.get("parser_authority_domain", {})
    expected_fixture_domain = {
        "authority_contract": {"path": AUTHORITY_REL, "sha256": AUTHORITY_SHA256},
        "snapshot_component": "ParserAuthorityDigestSetR1",
        "authority_digest_set": AUTHORITY_DIGEST_SET,
        "surface_census": {
            "path": "spec/grammar/deeplus.ebnf",
            "sha256": SURFACE_CENSUS["sha256"],
            "semantic_authority": False,
            "production_count": 656,
        },
    }
    cases = fixtures.get("authority_rebase_cases", [])
    if (
        fixture_domain != expected_fixture_domain
        or [row.get("test_id") for row in cases] != EXPECTED_CASE_IDS
        or Counter(row.get("class") for row in cases)
        != {"positive": 4, "boundary": 4, "negative": 8}
        or any(not row.get("scenario") or not row.get("expected") for row in cases)
    ):
        errors.append("R93 acceptance fixture drift")

    mutations = fixtures.get("authority_mutations", [])
    if (
        [row.get("mutation_id") for row in mutations] != EXPECTED_MUTATION_IDS
        or any(row.get("expected") != "REJECT" for row in mutations)
    ):
        errors.append("R93 mutation declaration drift")

    required_trace = [
        CONTRACT_REL,
        SCHEMA_REL,
        FIXTURE_REL,
        DECISION_REL,
        VALIDATOR_REL,
        MUTATION_REL,
    ]
    for row in (
        feature_row(formatter_features, "formatter_lsp_responsibility_card"),
        feature_row(lsp_features, "lsp_responsibility_card"),
    ):
        refs = row.get("artifact_trace_refs", [])
        if (
            any(path not in refs for path in required_trace)
            or row.get("formatter_lsp") != "NOT_RUN"
            or row.get("product_support") != "NOT_RUN"
            or row.get("production_parser") != "NOT_RUN"
            or "ParserContext" not in row.get("notes", "")
        ):
            errors.append(f"R93 feature trace drift: {row.get('feature_id')}")

    execution = fixtures.get("execution", {})
    governance = authority.get("governance", {})
    if (
        execution.get("production_formatter") != "NOT_RUN"
        or execution.get("production_lsp") != "NOT_RUN"
        or execution.get("production_incremental_parser") != "NOT_RUN"
        or execution.get("product_lanes") != "15_OF_15_NOT_RUN"
        or execution.get("semantic_p0") != 0
        or execution.get("open_feature_p1_count") != 22
        or governance.get("semantic_p0") != 0
        or governance.get("feature_p1") != "22_OPEN_UNCHANGED"
        or governance.get("product_lanes") != "15_OF_15_NOT_RUN"
    ):
        errors.append("R93 governance or product evidence drift")

    decision_path = root / DECISION_REL
    decision_text = decision_path.read_text(encoding="utf-8") if decision_path.is_file() else ""
    for token in (
        "IR-FE-P1-063",
        "ParserAuthorityDigestSetR1",
        "STRUCTURAL_DPG",
        "PARSER_CONTEXT",
        "PRATT",
        "SCANNER",
        "22 OPEN",
        "15 product lanes remain",
    ):
        if token not in decision_text:
            errors.append(f"R93 decision trace missing: {token}")

    return errors


def load_documents(root: Path) -> tuple[Any, ...]:
    return (
        strict_load(root / CONTRACT_REL),
        strict_load(root / SCHEMA_REL),
        strict_load(root / FIXTURE_REL),
        strict_load(root / FRONTEND_REL),
        strict_load(root / AUTHORITY_REL),
        strict_load(root / FORMATTER_FEATURE_REL),
        strict_load(root / LSP_FEATURE_REL),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    try:
        documents = load_documents(root)
        errors = validate_documents(root, *documents)
    except Exception as exc:  # noqa: BLE001
        errors = [str(exc)]

    checks = [{"check_id": check_id, "pass": not errors} for check_id in CHECK_IDS]
    receipt = {
        "schema": "deeplus.r93-formatter-lsp-dpg-authority-rebase-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "evidence_level": "E2_STATIC_CLOSURE",
        "baseline_main": BASELINE_MAIN,
        "gap_id": "IR-FE-P1-063",
        "check_count": len(CHECK_IDS),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "parser_authority_axis_count": 4,
        "surface_census_semantic_authority": False,
        "acceptance_case_count": 16,
        "acceptance_class_counts": {"positive": 4, "boundary": 4, "negative": 8},
        "mutation_declaration_count": 10,
        "ebnf_only_admission_count": 0,
        "source_syntax_change_count": 0,
        "language_semantic_change_count": 0,
        "new_final_diagnostic_id_count": 0,
        "semantic_p0": 0,
        "open_feature_p1_count": 22,
        "product_lanes": "15_OF_15_NOT_RUN",
        "product_execution": "NOT_RUN",
        "github_mutation": False,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
