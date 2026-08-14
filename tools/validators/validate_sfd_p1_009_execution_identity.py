#!/usr/bin/env python3
"""Validate the bounded R79 SFD-P1-009 execution-identity route repair."""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
from pathlib import Path
from typing import Any


CONTRACT_REL = "spec/contracts/sfd-p1-009-execution-identity-r1.json"
SCHEMA_REL = "schemas/language/sfd-p1-009-execution-identity-r1.schema.json"
SOURCE_REL = "crates/deeplus-source/src/sfd_p1_009.rs"
CLI_REL = "crates/deeplusc/src/sfd_cli.rs"
TESTKIT_REL = "crates/deeplus-testkit/src/sfd_p1_009.rs"
POINTER_REL = "current/current-pointer.json"
HISTORICAL = "f509fce5df6c16b77d3accdccde4c640b093da0a"
FIRST_ROUTE_COMMIT = "585d083c6515a78ca327e542a439584f8773a2aa"
REQUIRED_AT_TARGET = (
    SOURCE_REL,
    "crates/deeplus-testkit/fixtures/sfd_p1_009/"
    "Test_Deeplus_SFD_P1_009_Executable_Fixture_Manifest_R3.json",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-c", "safe.directory=" + root.as_posix(), "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def validate(
    root: Path,
    *,
    contract_override: dict[str, Any] | None = None,
    source_override: str | None = None,
    cli_override: str | None = None,
    testkit_override: str | None = None,
) -> list[str]:
    errors: list[str] = []
    contract = copy.deepcopy(contract_override) if contract_override is not None else load(root / CONTRACT_REL)
    schema = load(root / SCHEMA_REL)
    source = source_override if source_override is not None else (root / SOURCE_REL).read_text(encoding="utf-8")
    cli = cli_override if cli_override is not None else (root / CLI_REL).read_text(encoding="utf-8")
    testkit = testkit_override if testkit_override is not None else (root / TESTKIT_REL).read_text(encoding="utf-8")
    pointer = load(root / POINTER_REL)

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
        except Exception as exc:
            errors.append("G01:SCHEMA_BINDING:" + type(exc).__name__)

    require(
        contract.get("revision") == "r79-sfd-p1-009-execution-identity-route-repair-r1"
        and contract.get("candidate_status") == "LOCAL_EXECUTABLE_ROUTE_REPAIRED_SFD_P1_OPEN",
        "G01",
        "CONTRACT_IDENTITY",
    )
    domains = contract.get("identity_domains", {})
    historical = domains.get("historical_provenance", {})
    target = domains.get("execution_target", {})
    require(
        historical
        == {
            "commit": HISTORICAL,
            "role": "IMMUTABLE_DESIGN_PROVENANCE_ONLY",
            "executable_route_present": False,
        }
        and target
        == {
            "binding": "OBSERVED_CLEAN_CHECKOUT_HEAD",
            "approval_binding": "EXTERNAL_POST_COMMIT_EXECUTION_RECEIPT",
            "self_reference": False,
        },
        "G02",
        "IDENTITY_DOMAIN_SEPARATION",
    )

    absent = [git(root, "cat-file", "-e", f"{HISTORICAL}:{path}").returncode != 0 for path in REQUIRED_AT_TARGET]
    introduced = git(root, "log", "--diff-filter=A", "--format=%H", "--", SOURCE_REL)
    first = introduced.stdout.decode("utf-8", errors="replace").splitlines()
    require(all(absent), "G02", "HISTORICAL_ROUTE_ABSENCE")
    require(bool(first) and first[-1] == FIRST_ROUTE_COMMIT, "G02", "ROUTE_INTRODUCTION_PROVENANCE")

    require(
        f'pub const HISTORICAL_PROVENANCE_BASELINE: &str = "{HISTORICAL}";' in source
        and 'pub const EXECUTION_TARGET_BINDING: &str = "OBSERVED_CLEAN_CHECKOUT_HEAD";' in source
        and "REQUIRED_BASELINE" not in source,
        "G03",
        "SOURCE_IDENTITY_CONSTANTS",
    )
    require(
        "fn execution_target_gate(repository: &Path) -> Result<String, ContractError>" in cli
        and '.args(["rev-parse", "--verify", "HEAD"])' in cli
        and '.args(["diff-index", "--quiet", "HEAD", "--"])' in cli
        and '.args(["cat-file", "-e", &object])' in cli
        and "baseline_gate" not in cli
        and "REQUIRED_BASELINE" not in cli,
        "G03",
        "CLEAN_TARGET_GATE",
    )
    require(
        '"baseline_commit": bindings.execution_target_commit' in testkit
        and 'json!(bindings.execution_target_commit)' in testkit
        and "Some(HISTORICAL_PROVENANCE_BASELINE)" in testkit
        and "REQUIRED_BASELINE" not in testkit,
        "G03",
        "RECEIPT_TARGET_AND_TEMPLATE_PROVENANCE",
    )

    gate = contract.get("execution_gate", {})
    receipt = contract.get("receipt_binding", {})
    require(
        gate
        == {
            "full_commit_sha": True,
            "tracked_tree_clean": True,
            "required_paths_owned_by_head": True,
            "untracked_output_allowed": True,
            "historical_commit_as_target_rejected": True,
        },
        "G04",
        "EXECUTION_GATE_EXACT",
    )
    require(
        receipt.get("baseline_commit") == "OBSERVED_EXECUTION_TARGET_COMMIT"
        and receipt.get("historical_provenance_commit") == "RUN_SUMMARY_ONLY"
        and all(
            receipt.get(key) == "BOUND_AT_EXECUTION"
            for key in (
                "current_pointer_digest",
                "implementation_digest",
                "compiler_binary_digest",
                "environment_digest",
            )
        ),
        "G04",
        "RECEIPT_BINDING_EXACT",
    )

    action = next((row for row in pointer.get("open_actions", []) if row.get("id") == "SFD-P1-009"), {})
    closure = contract.get("closure_fence", {})
    governance = contract.get("governance", {})
    require(
        action.get("id") == "SFD-P1-009"
        and action.get("priority") == "P1"
        and action.get("tracking_ref") == "deeplus-action:SFD-P1-009"
        and closure.get("action") == "SFD-P1-009"
        and closure.get("status") == "OPEN"
        and closure.get("route_blocker") == "RESOLVED_BY_IDENTITY_DOMAIN_SEPARATION"
        and closure.get("execution_receipt_count") == 0,
        "G05",
        "SFD_ACTION_REMAINS_OPEN",
    )
    require(
        governance
        == {
            "semantic_p0": 0,
            "feature_p1": "22_OPEN_UNCHANGED",
            "product_lanes": "15_OF_15_NOT_RUN",
            "github_publication": "NOT_PERFORMED_FOR_R79",
            "production_implementation": "NOT_AUTHORIZED_OR_PERFORMED",
        },
        "G05",
        "GOVERNANCE_FENCE",
    )
    ids = [row.get("id") for row in contract.get("acceptance_cases", [])]
    require(ids == [f"R79-AT-{index:03d}" for index in range(1, 8)], "G05", "ACCEPTANCE_CASES_EXACT_7")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root)
    print(
        json.dumps(
            {
                "schema": "deeplus.r79-sfd-p1-009-execution-identity-validation-receipt/r1",
                "result": "PASS" if not errors else "FAIL",
                "checks": 7,
                "failed": errors,
                "feature_p1": "22_OPEN_UNCHANGED",
                "sfd_p1_009": "OPEN",
                "product_execution": "NOT_RUN",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
