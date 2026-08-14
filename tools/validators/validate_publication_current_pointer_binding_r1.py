#!/usr/bin/env python3
"""Validate the R94 two-phase publication and current-pointer binding."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE_MAIN = "10e64f492f0529610673846139afcf0d95175663"
SEMANTIC_COMMIT = "da734c608c0d583a671c0da9e14da00bff42affd"
SEMANTIC_TREE = "ab37f3a91745c3b90e87eeaf15868007ef08ef69"
CLOSURE_TREE = "8e08d498795c1054e392f82802f54d92cf2c215a"
RECEIPT_REL = "release/evidence/r77-integrated-surface-publication-closure-readback.json"
CONTRACT_REL = "spec/contracts/publication-current-pointer-binding-r1.json"
SCHEMA_REL = "schemas/language/publication-current-pointer-binding-r1.schema.json"
FIXTURE_REL = "tests/fixtures/current/publication-current-pointer-binding-r1.json"
POINTER_REL = "current/current-pointer.json"
INTEGRITY_REL = "spec/contracts/language-coherence-current-integrity-r1.json"
DECISION_REL = "decisions/language/Design_Deeplus_Publication_Current_Pointer_Binding_Closure_R1.md"
GENERATOR_REL = "tools/generators/generate_language_coherence_current_integrity.py"

EXPECTED_BINDING = {
    "mode": "semantic_publication_target_bound_by_external_post_merge_receipt",
    "receipt_location": RECEIPT_REL,
    "current_binding": False,
    "self_binding_forbidden": True,
}
EXPECTED_CASE_IDS = [
    "R94-P-01-EXTERNAL-RECEIPT",
    "R94-P-02-ACTIVE-NONSELF",
    "R94-P-03-ROLE-SEPARATION",
    "R94-B-01-AWAITING-RECEIPT",
    "R94-B-02-MAIN-ADVANCED",
    "R94-B-03-CI-PENDING",
    "R94-B-04-SEMANTIC-ANCESTOR",
    "R94-N-01-PENDING-TRUE",
    "R94-N-02-ABSENT-TRUE",
    "R94-N-03-SELF-COMMIT",
    "R94-N-04-ROLE-CONFLATION",
    "R94-N-05-HASH-DOMAIN-CONFLATION",
    "R94-N-06-CI-FAILURE",
    "R94-N-07-PRODUCT-OVERCLAIM",
]
EXPECTED_MUTATION_IDS = [
    "R94-M-01-CURRENT-BINDING-TRUE",
    "R94-M-02-PENDING-RECEIPT",
    "R94-M-03-SEMANTIC-COMMIT-DRIFT",
    "R94-M-04-CLOSURE-COMMIT-DRIFT",
    "R94-M-05-CLOSURE-TREE-DRIFT",
    "R94-M-06-RECEIPT-BINDING-TRUE",
    "R94-M-07-CI-FAILURE",
    "R94-M-08-PRODUCT-PASS",
]
CHECK_IDS = [
    "R94_CONTRACT_SCHEMA_BINDING",
    "R94_GIT_IDENTITY_ROLES",
    "R94_POINTER_EXTERNAL_RECEIPT_BINDING",
    "R94_RECEIPT_EXACT_READBACK",
    "R94_REQUIRED_CI_SUCCESS",
    "R94_SELF_BINDING_FENCE",
    "R94_STATE_MACHINE",
    "R94_ACCEPTANCE_CASES_14",
    "R94_MUTATIONS_DECLARED_8",
    "R94_GENERATOR_OWNERSHIP_PATH",
    "R94_GOVERNANCE_FENCE",
    "R94_DECISION_TRACE",
]


def strict_load(path: Path) -> Any:
    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        keys = [key for key, _ in pairs]
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate JSON key in {path}")
        if len(keys) != len({key.casefold() for key in keys}):
            raise ValueError(f"case-fold duplicate JSON key in {path}")
        return dict(pairs)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def load_documents(root: Path) -> tuple[Any, ...]:
    return (
        strict_load(root / CONTRACT_REL),
        strict_load(root / SCHEMA_REL),
        strict_load(root / FIXTURE_REL),
        strict_load(root / POINTER_REL),
        strict_load(root / INTEGRITY_REL),
        strict_load(root / RECEIPT_REL),
    )


def validate_documents(
    root: Path,
    contract: dict[str, Any],
    schema: dict[str, Any],
    fixtures: dict[str, Any],
    pointer: dict[str, Any],
    integrity: dict[str, Any],
    receipt: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if (
        contract.get("schema") != "deeplus.publication-current-pointer-binding/r1"
        or contract.get("status") != "LOCAL_VERIFIED_CANDIDATE_NOT_INTEGRATED"
        or contract.get("gap_id") != "IR-GOV-P0-064"
        or contract.get("baseline_main") != BASELINE_MAIN
        or schema.get("properties", {}).get("gap_id", {}).get("const") != "IR-GOV-P0-064"
        or schema.get("properties", {}).get("pointer_binding", {}).get("properties", {}).get("current_binding", {}).get("const") is not False
    ):
        errors.append("R94 contract/schema identity drift")

    identities = contract.get("identity_roles", {})
    semantic = identities.get("semantic_publication", {})
    closure = identities.get("publication_closure_readback", {})
    try:
        observed_semantic_tree = git(root, "rev-parse", f"{SEMANTIC_COMMIT}^{{tree}}")
        observed_closure_tree = git(root, "rev-parse", f"{BASELINE_MAIN}^{{tree}}")
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", SEMANTIC_COMMIT, BASELINE_MAIN],
            cwd=root,
            check=False,
        ).returncode == 0
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Git identity probe failed: {exc}")
        observed_semantic_tree = ""
        observed_closure_tree = ""
        ancestor = False
    if (
        semantic != {"role": "R77_SEMANTIC_PUBLICATION_TARGET", "pull_request": 76, "commit": SEMANTIC_COMMIT, "tree": SEMANTIC_TREE}
        or closure != {"role": "R77_PUBLICATION_CLOSURE_READBACK", "pull_request": 77, "commit": BASELINE_MAIN, "tree": CLOSURE_TREE, "parent": SEMANTIC_COMMIT}
        or observed_semantic_tree != SEMANTIC_TREE
        or observed_closure_tree != CLOSURE_TREE
        or not ancestor
    ):
        errors.append("semantic/closure Git identity role drift")

    contract_binding = contract.get("pointer_binding", {})
    if (
        pointer.get("publication_authority_source", {}).get("commit") != SEMANTIC_COMMIT
        or pointer.get("audited_implementation_baseline", {}).get("commit") != BASELINE_MAIN
        or pointer.get("candidate_binding") != EXPECTED_BINDING
        or integrity.get("current_binding") is not False
        or contract_binding.get("current_binding") is not False
        or contract_binding.get("semantic_authority_active") is not True
        or contract_binding.get("artifact_self_binding") is not False
        or contract_binding.get("receipt_location") != RECEIPT_REL
    ):
        errors.append("pointer or integrity external receipt binding drift")

    receipt_semantic = receipt.get("semantic_publication", {})
    receipt_closure = receipt.get("publication_closure", {})
    receipt_binding = receipt.get("binding", {})
    if (
        receipt.get("result") != "VERIFIED_CLOSED"
        or receipt.get("verdict") != "VERIFIED_CLOSED_BY_POST_MERGE_READBACK"
        or receipt_semantic.get("merge_commit") != SEMANTIC_COMMIT
        or receipt_semantic.get("tree") != SEMANTIC_TREE
        or receipt_closure.get("merge_commit") != BASELINE_MAIN
        or receipt_closure.get("tree") != CLOSURE_TREE
        or receipt_closure.get("parent") != SEMANTIC_COMMIT
        or receipt_closure.get("live_main_exact_match_at_audit_start") is not True
        or receipt_binding != {
            "semantic_authority_active": True,
            "artifact_self_binding": False,
            "pointer_current_binding": False,
            "binding_mechanism": "EXTERNAL_POST_MERGE_READBACK_RECEIPT",
        }
    ):
        errors.append("external post-merge receipt identity drift")

    expected_workflows = {"Canonical integrity", "Rust workspace"}
    for phase in ("semantic_merge", "closure_merge"):
        rows = receipt.get("github_actions", {}).get(phase, [])
        if (
            {row.get("workflow") for row in rows} != expected_workflows
            or any(row.get("conclusion") != "SUCCESS" for row in rows)
        ):
            errors.append(f"required GitHub Actions drift: {phase}")

    state_machine = contract.get("state_machine", {})
    states = state_machine.get("states", [])
    forbidden = set(state_machine.get("forbidden_states", []))
    if (
        len(states) != 3
        or any(row.get("current_binding") is not False for row in states)
        or forbidden != {
            "PENDING_RECEIPT_AND_CURRENT_BINDING_TRUE",
            "ABSENT_RECEIPT_AND_CURRENT_BINDING_TRUE",
            "PREDICTED_FUTURE_COMMIT_IN_SELF_CONTAINING_ARTIFACT",
            "SEMANTIC_AND_CLOSURE_COMMIT_ROLE_CONFLATION",
            "ARTIFACT_SHA256_AND_GIT_COMMIT_SHA_COMPARISON",
        }
        or contract.get("acceptance", {}).get("pending_receipt_current_binding_true_count") != 0
        or contract.get("acceptance", {}).get("self_referential_commit_count") != 0
    ):
        errors.append("publication state machine or self-binding fence drift")

    cases = fixtures.get("cases", [])
    if (
        [row.get("test_id") for row in cases] != EXPECTED_CASE_IDS
        or Counter(row.get("class") for row in cases) != {"positive": 3, "boundary": 4, "negative": 7}
        or any(not row.get("scenario") or not row.get("expected") for row in cases)
    ):
        errors.append("R94 acceptance case drift")
    mutations = fixtures.get("mutations", [])
    if (
        [row.get("mutation_id") for row in mutations] != EXPECTED_MUTATION_IDS
        or any(row.get("expected") != "REJECT" for row in mutations)
    ):
        errors.append("R94 mutation declaration drift")

    generator_text = (root / GENERATOR_REL).read_text(encoding="utf-8")
    if (
        "LANGUAGE_COHERENCE_PUBLICATION_RECEIPT" not in generator_text
        or '"current_binding": False' not in generator_text
        or "EXTERNAL_POST_MERGE_READBACK_RECEIPT" not in generator_text
        or "self_binding_forbidden" not in generator_text
    ):
        errors.append("generator-owned two-phase binding path drift")

    execution = fixtures.get("execution", {})
    governance = contract.get("governance", {})
    if (
        execution.get("production_implementation") != "NOT_RUN"
        or execution.get("product_lanes") != "15_OF_15_NOT_RUN"
        or execution.get("open_feature_p1_count") != 22
        or governance.get("semantic_p0") != 0
        or governance.get("feature_p1") != "22_OPEN_UNCHANGED"
        or governance.get("product_lanes") != "15_OF_15_NOT_RUN"
        or governance.get("github_mutation") is not False
    ):
        errors.append("R94 governance or evidence honesty drift")

    decision = (root / DECISION_REL).read_text(encoding="utf-8") if (root / DECISION_REL).is_file() else ""
    for token in ("IR-GOV-P0-064", SEMANTIC_COMMIT, BASELINE_MAIN, "current_binding: false", "22 feature P1", "15 product lanes"):
        if token not in decision:
            errors.append(f"R94 decision trace missing: {token}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = validate_documents(root, *load_documents(root))
    except Exception as exc:  # noqa: BLE001
        errors = [str(exc)]
    checks = [{"check_id": check_id, "pass": not errors} for check_id in CHECK_IDS]
    receipt = {
        "schema": "deeplus.r94-publication-current-pointer-binding-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "evidence_level": "E3_GIT_OBJECT_AND_REPOSITORY_STATIC",
        "baseline_main": BASELINE_MAIN,
        "gap_id": "IR-GOV-P0-064",
        "check_count": len(CHECK_IDS),
        "passed_check_count": sum(row["pass"] for row in checks),
        "checks": checks,
        "acceptance_case_count": 14,
        "mutation_declaration_count": 8,
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
