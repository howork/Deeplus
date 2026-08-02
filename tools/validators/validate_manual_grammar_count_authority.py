#!/usr/bin/env python3
"""Validate R40 exact grammar-count projection into published manual claims."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/manual-grammar-count-authority-r1.json"
FIXTURE_REL = "tests/fixtures/current/manual-grammar-count-authority-r1.json"
GRAMMAR_REL = "spec/grammar/deeplus.ebnf"
FRONTEND_REL = "spec/frontend/frontend-model.json"
REFERENCE_CONTRACT_REL = "spec/contracts/grammar-reference-r1.json"
DISPOSITION_REL = "spec/contracts/grammar-production-disposition-registry-r1.json"
MANIFEST_REL = "docs/grammar-reference/coverage-manifest.json"
COVERAGE_SCHEMA_REL = "schemas/language/grammar-reference-coverage.schema.json"

CHECK_IDS = [
    "R40_CONTRACT_EXACT",
    "R40_AUTHORITATIVE_PROJECTION_EXACT",
    "R40_MACHINE_CONSUMER_PARITY",
    "R40_PUBLISHED_CLAIMS_EXACT_3",
    "R40_ACCEPTANCE_CASES_EXACT_3",
    "R40_STALE_COUNT_MUTATION_REJECTED_1",
    "R40_NO_SOURCE_OR_FEATURE_DRIFT",
    "R40_GOVERNANCE_FENCE",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_generator(root: Path) -> Any:
    path = root / "tools/generators/generate_grammar_reference.py"
    spec = importlib.util.spec_from_file_location("deeplus_grammar_reference", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load grammar-reference generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_documents(root: Path) -> dict[str, Any]:
    contract = load_json(root / CONTRACT_REL)
    return {
        "contract": contract,
        "fixtures": load_json(root / FIXTURE_REL),
        "grammar_text": (root / GRAMMAR_REL).read_text(encoding="utf-8"),
        "frontend": load_json(root / FRONTEND_REL),
        "reference": load_json(root / REFERENCE_CONTRACT_REL),
        "disposition": load_json(root / DISPOSITION_REL),
        "manifest": load_json(root / MANIFEST_REL),
        "coverage_schema": load_json(root / COVERAGE_SCHEMA_REL),
        "claim_texts": {
            row["claim_id"]: (root / row["path"]).read_text(encoding="utf-8")
            for row in contract.get("published_manual_claims", [])
        },
    }


def evaluate(documents: dict[str, Any], generator: Any) -> list[str]:
    errors: list[str] = []
    contract = documents["contract"]
    fixtures = documents["fixtures"]

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    authority = contract.get("authority", {})
    expected_profiles = authority.get("profile_counts")
    expected_total = authority.get("production_count")
    require(
        contract.get("schema") == "deeplus.manual-grammar-count-authority/r1",
        "CONTRACT_SCHEMA",
    )
    require(
        contract.get("status") == "CURRENT_STABLE_DESIGN_MACHINE_CONTRACT",
        "CONTRACT_STATUS",
    )
    require(authority.get("profile_counts") == expected_profiles, "CONTRACT_PROFILE_COUNTS")
    require(authority.get("production_count") == expected_total, "CONTRACT_TOTAL")
    require(
        authority.get("published_projection") == f"{MANIFEST_REL}#/grammar",
        "CONTRACT_PROJECTION",
    )
    require(
        authority.get("recovery_is_production_profile") is False,
        "CONTRACT_RECOVERY_PROFILE_FENCE",
    )

    productions, observed_profiles = generator.parse_grammar(
        documents["grammar_text"],
        documents["frontend"],
        documents["reference"],
    )
    require(observed_profiles == expected_profiles, "AUTHORITY_PROFILE_COUNTS")
    require(len(productions) == expected_total, "AUTHORITY_TOTAL")

    frontend = documents["frontend"]
    reference = documents["reference"]
    disposition = documents["disposition"]
    manifest_grammar = documents["manifest"].get("grammar", {})
    schema_grammar = documents["coverage_schema"].get("properties", {}).get("grammar", {}).get("properties", {})
    schema_counts = documents["coverage_schema"].get("$defs", {}).get("counts", {}).get("properties", {})
    schema_profiles = schema_grammar.get("profile_counts", {}).get("properties", {})
    require(frontend.get("grammar_profile_counts") == expected_profiles, "MACHINE_FRONTEND_PROFILES")
    require(frontend.get("grammar_topology_closure", {}).get("production_count") == expected_total, "MACHINE_FRONTEND_TOTAL")
    require(reference.get("grammar", {}).get("expected_profile_counts") == expected_profiles, "MACHINE_REFERENCE_PROFILES")
    require(reference.get("grammar", {}).get("expected_total") == expected_total, "MACHINE_REFERENCE_TOTAL")
    require(disposition.get("profile_counts") == expected_profiles, "MACHINE_DISPOSITION_PROFILES")
    require(disposition.get("grammar", {}).get("production_count") == expected_total, "MACHINE_DISPOSITION_TOTAL")
    require(manifest_grammar.get("profile_counts") == expected_profiles, "MACHINE_MANIFEST_PROFILES")
    require(manifest_grammar.get("production_count") == expected_total, "MACHINE_MANIFEST_TOTAL")
    require(schema_grammar.get("production_count", {}).get("const") == expected_total, "MACHINE_SCHEMA_TOTAL")
    require(
        {key: schema_profiles.get(key, {}).get("const") for key in expected_profiles} == expected_profiles,
        "MACHINE_SCHEMA_PROFILES",
    )
    require(schema_counts.get("grammar_productions", {}).get("const") == expected_total, "MACHINE_SCHEMA_COVERAGE_TOTAL")

    claims = contract.get("published_manual_claims", [])
    require(
        [row.get("claim_id") for row in claims]
        == ["R40-CLAIM-README", "R40-CLAIM-STATUS", "R40-CLAIM-GUIDE"],
        "MANUAL_GRAMMAR_COUNT_CLAIM_SET",
    )
    for row in claims:
        text = documents["claim_texts"].get(row.get("claim_id"), "")
        if not all(fragment in text for fragment in row.get("required_fragments", [])):
            errors.append(f"MANUAL_GRAMMAR_COUNT_CLAIM_STALE:{row.get('claim_id')}")
    for fragment in contract.get("forbidden_stale_fragments", []):
        if any(fragment in text for text in documents["claim_texts"].values()):
            errors.append(f"MANUAL_GRAMMAR_COUNT_STALE_FRAGMENT:{fragment}")

    expected_cases = [
        (
            "IR-R3-GAP-11-P",
            "positive",
            "ACCEPT_"
            + "_".join(str(expected_profiles[key]) for key in ("LEXICAL", "STABLE", "PREVIEW")),
        ),
        ("IR-R3-GAP-11-B", "boundary", "ACCEPT_GENERATED_COUNT_UPDATE"),
        ("IR-R3-GAP-11-N", "negative", "REJECT_STALE_COUNT"),
    ]
    observed_cases = [
        (row.get("test_id"), row.get("kind"), row.get("expected_outcome"))
        for row in fixtures.get("acceptance_cases", [])
        if isinstance(row, dict)
    ]
    require(observed_cases == expected_cases, "FIXTURE_CASES")
    mutations = fixtures.get("mutation_specs", [])
    require(
        len(mutations) == 1
        and mutations[0].get("mutation_id") == "R40-MUT-001"
        and mutations[0].get("expected_error_prefix") == "MANUAL_GRAMMAR_COUNT_CLAIM_STALE",
        "FIXTURE_MUTATION",
    )
    acceptance = fixtures.get("acceptance", {})
    require(acceptance.get("case_count") == 3, "FIXTURE_ACCEPTANCE_CASE_COUNT")
    require(acceptance.get("mutation_count") == 1, "FIXTURE_ACCEPTANCE_MUTATION_COUNT")
    require(acceptance.get("manual_claim_count") == 3, "FIXTURE_ACCEPTANCE_CLAIM_COUNT")
    require(acceptance.get("profile_counts") == expected_profiles, "FIXTURE_ACCEPTANCE_PROFILES")
    require(acceptance.get("production_count") == expected_total, "FIXTURE_ACCEPTANCE_TOTAL")
    require(acceptance.get("semantic_change_count") == 0, "FIXTURE_ACCEPTANCE_SEMANTIC")
    require(acceptance.get("grammar_production_change_count") == 0, "FIXTURE_ACCEPTANCE_GRAMMAR")
    require(acceptance.get("product_execution") == "NOT_RUN", "FIXTURE_ACCEPTANCE_PRODUCT")

    governance = contract.get("governance", {})
    require(governance.get("gap_id") == "IR-FE-P2-038", "GOVERNANCE_GAP")
    require(governance.get("semantic_change_count") == 0, "GOVERNANCE_SEMANTIC")
    require(governance.get("grammar_production_change_count") == 0, "GOVERNANCE_GRAMMAR")
    require(governance.get("new_source_spelling_count") == 0, "GOVERNANCE_SURFACE")
    require(governance.get("semantic_p0") == 0, "GOVERNANCE_P0")
    require(governance.get("feature_p1") == "22_OPEN_UNCHANGED", "GOVERNANCE_P1")
    require(governance.get("m13_actions") == "4_OPEN_UNCHANGED", "GOVERNANCE_M13")
    require(governance.get("product_lanes") == "15/15_NOT_RUN", "GOVERNANCE_PRODUCT")
    require(contract.get("product_support") == "NOT_RUN", "GOVERNANCE_SUPPORT")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    mutations: list[dict[str, Any]] = []
    try:
        generator = load_generator(root)
        documents = load_documents(root)
        errors = evaluate(documents, generator)
        mutated = copy.deepcopy(documents)
        current_stable = documents["contract"]["authority"]["profile_counts"]["STABLE"]
        mutated["claim_texts"]["R40-CLAIM-STATUS"] = mutated["claim_texts"]["R40-CLAIM-STATUS"].replace(
            f"| `STABLE` | {current_stable} |",
            f"| `STABLE` | {current_stable - 1} |",
            1,
        )
        mutation_errors = evaluate(mutated, generator)
        mutation_rejected = any(
            error.startswith("MANUAL_GRAMMAR_COUNT_CLAIM_STALE")
            for error in mutation_errors
        )
        mutations.append(
            {
                "mutation_id": "R40-MUT-001",
                "result": "REJECTED" if mutation_rejected else "SURVIVED",
                "expected_error_prefix": "MANUAL_GRAMMAR_COUNT_CLAIM_STALE",
                "observed_errors": mutation_errors,
            }
        )
    except Exception as exc:  # noqa: BLE001
        errors = [f"VALIDATOR_EXCEPTION:{type(exc).__name__}:{exc}"]
        mutations = []

    prefix_groups = {
        "R40_CONTRACT_EXACT": ("CONTRACT_",),
        "R40_AUTHORITATIVE_PROJECTION_EXACT": ("AUTHORITY_",),
        "R40_MACHINE_CONSUMER_PARITY": ("MACHINE_",),
        "R40_PUBLISHED_CLAIMS_EXACT_3": ("MANUAL_",),
        "R40_ACCEPTANCE_CASES_EXACT_3": ("FIXTURE_",),
        "R40_NO_SOURCE_OR_FEATURE_DRIFT": ("GOVERNANCE_SEMANTIC", "GOVERNANCE_GRAMMAR", "GOVERNANCE_SURFACE"),
        "R40_GOVERNANCE_FENCE": ("GOVERNANCE_",),
    }
    checks: list[dict[str, Any]] = []
    for check_id in CHECK_IDS:
        if check_id == "R40_STALE_COUNT_MUTATION_REJECTED_1":
            passed = len(mutations) == 1 and mutations[0]["result"] == "REJECTED"
        else:
            prefixes = prefix_groups[check_id]
            passed = not any(
                any(error.startswith(prefix) for prefix in prefixes)
                for error in errors
            )
        checks.append({"check_id": check_id, "pass": passed})

    result = "PASS" if not errors and all(row["pass"] for row in checks) else "FAIL"
    receipt = {
        "schema": "deeplus.r40-manual-grammar-count-validation-receipt/r1",
        "result": result,
        "evidence_level": "E2_STATIC_CLOSURE",
        "check_scope": "R40_MANUAL_GRAMMAR_COUNT_AUTHORITY_EXACT",
        "check_count": len(checks),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "profile_counts": documents["contract"]["authority"]["profile_counts"],
        "production_count": documents["contract"]["authority"]["production_count"],
        "manual_claim_count": 3,
        "acceptance_case_count": 3,
        "mutation_count": len(mutations),
        "rejected_mutation_count": sum(row["result"] == "REJECTED" for row in mutations),
        "mutations": mutations,
        "grammar_production_change_count": 0,
        "new_source_spelling_count": 0,
        "semantic_change_count": 0,
        "feature_p1": "22_OPEN_UNCHANGED",
        "m13_actions": "4_OPEN_UNCHANGED",
        "product_execution": "NOT_RUN",
        "errors": errors,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
