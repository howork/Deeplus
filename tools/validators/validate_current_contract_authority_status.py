#!/usr/bin/env python3
"""Validate the byte-bound current-contract authority status registry.

The registry resolves candidate-era metadata without rewriting digest-bound
semantic contracts. It is design-static evidence only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REGISTRY_REL = "spec/contracts/current-contract-authority-status-r1.json"
SCHEMA_REL = "schemas/language/current-contract-authority-status-r1.schema.json"
CURRENT_MAIN = "39a5d50cc770341c4b9776d00d84520b780d0c62"
EXPECTED = {
    "spec/contracts/continuation-interface-r1.json": {
        "sha256": "07e0ab81e3a29286f65b04bb0e1c49752cda674ceeda19231b7e8744b3a9218f",
        "gap": "IR-OWN-P0-017",
        "semantic": "82cdf6aa6b1527af3b5b06157a3fd745ee33e5b0",
        "closure": "ab7fb2fd356262eeaf0b0bbdeb4d81e4d63d84e5",
        "receipt": "release/evidence/r46-managed-root-runtime-fusion-publication-closure-receipt.json",
    },
    "spec/contracts/suspension-frame-responsibility-r1.json": {
        "sha256": "8f5b8e5d106de8edf9517929d9f34cff9550a10fa35b0e10df094fbd4d356f11",
        "gap": "IR-OWN-P0-017",
        "semantic": "82cdf6aa6b1527af3b5b06157a3fd745ee33e5b0",
        "closure": "ab7fb2fd356262eeaf0b0bbdeb4d81e4d63d84e5",
        "receipt": "release/evidence/r46-managed-root-runtime-fusion-publication-closure-receipt.json",
    },
    "spec/contracts/managed-reference-memory-profile-r1.json": {
        "sha256": "2274caed9a6fefb3f2169d6136617b7971efa0e2bf5aeacef861cab4a956ce73",
        "gap": "IR-OWN-P1-025",
        "semantic": "82cdf6aa6b1527af3b5b06157a3fd745ee33e5b0",
        "closure": "ab7fb2fd356262eeaf0b0bbdeb4d81e4d63d84e5",
        "receipt": "release/evidence/r46-managed-root-runtime-fusion-publication-closure-receipt.json",
    },
    "spec/contracts/ownership-type-qualifier-r1.json": {
        "sha256": "0e459e087cdc481f8d098ea737fd97816d25347385e50c1c53afb6bbc378fca8",
        "gap": "IR-OWN-P1-018",
        "semantic": "ee7d1833dcc9156070c1071f96fc55b3e19ae967",
        "closure": CURRENT_MAIN,
        "receipt": "release/evidence/r47-ownership-contract-fusion-publication-closure-receipt.json",
    },
    "spec/contracts/frontend-primary-diagnostic-identity-r1.json": {
        "sha256": "fd8605532a4678eedf0eff3a4343028308ae8217d6561dfb91ea26e1fb0e0ec9",
        "gap": "IR-FE-P1-035",
        "semantic": "2feba9e077ffdf35403c3b8467c17ddcfcf142f6",
        "closure": "4a38cdfaee6bb76b6e21fba59eef4b4b870a5a44",
        "receipt": "release/evidence/r25-r27-frontend-trace-diagnostic-grammar-topology-publication-closure-receipt.json",
    },
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_pointer(value: Any, pointer: str) -> Any:
    current = value
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def validate(root: Path, registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    try:
        import jsonschema

        jsonschema.Draft202012Validator(load(root / SCHEMA_REL)).validate(registry)
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover - exact text is environment-specific
        errors.append(f"JSON_SCHEMA:{exc}")

    rows = registry.get("rows", [])
    row_paths = [row.get("contract_path") for row in rows]
    require(len(rows) == 5, "ROW_COUNT")
    require(len(set(row_paths)) == len(row_paths), "ROW_PATH_UNIQUE")
    require(set(row_paths) == set(EXPECTED), "ROW_PATH_EXACT_SET")

    for row in rows:
        rel = row.get("contract_path", "")
        expected = EXPECTED.get(rel)
        if expected is None:
            continue
        contract_path = root / rel
        require(contract_path.is_file(), f"CONTRACT_EXISTS:{rel}")
        if not contract_path.is_file():
            continue
        contract = load(contract_path)
        require(sha256(contract_path) == expected["sha256"], f"CONTRACT_SHA:{rel}")
        require(row.get("contract_sha256") == expected["sha256"], f"ROW_SHA:{rel}")

        authority = row.get("current_authority", {})
        require(authority.get("artifact_status") == "CANONICAL_CURRENT", f"CURRENT_STATUS:{rel}")
        require(authority.get("gap_id") == expected["gap"], f"GAP_ID:{rel}")
        require(authority.get("gap_status") == "VERIFIED_CLOSED", f"GAP_STATUS:{rel}")
        require(authority.get("semantic_publication_commit") == expected["semantic"], f"SEMANTIC_COMMIT:{rel}")
        require(authority.get("publication_closure_commit") == expected["closure"], f"CLOSURE_COMMIT:{rel}")
        require(authority.get("closure_receipt") == expected["receipt"], f"RECEIPT_PATH:{rel}")
        require(authority.get("republished_current_commit") == CURRENT_MAIN, f"REPUBLISHED_CURRENT:{rel}")

        history = row.get("historical_provenance", {})
        require(history.get("interpretation") == "HISTORICAL_CANDIDATE_ORIGIN_NOT_CURRENT_AUTHORITY", f"HISTORY_ROLE:{rel}")
        for pointer, expected_value in history.get("field_values", {}).items():
            try:
                actual_value = json_pointer(contract, pointer)
            except (KeyError, IndexError, TypeError, ValueError):
                errors.append(f"HISTORY_POINTER:{rel}:{pointer}")
                continue
            require(actual_value == expected_value, f"HISTORY_VALUE:{rel}:{pointer}")

        receipt_path = root / expected["receipt"]
        require(receipt_path.is_file(), f"RECEIPT_EXISTS:{rel}")
        if receipt_path.is_file():
            receipt = load(receipt_path)
            transition = receipt.get("gap_transition", {})
            require(receipt.get("semantic_publication", {}).get("merge_commit") == expected["semantic"], f"RECEIPT_SEMANTIC:{rel}")
            require(expected["gap"] in transition.get("gap_ids", []), f"RECEIPT_GAP:{rel}")
            require(transition.get("closure_state_after_closure_merge_readback") == "VERIFIED_CLOSED", f"RECEIPT_CLOSURE_STATE:{rel}")

        require(row.get("semantic_delta") == 0, f"SEMANTIC_DELTA:{rel}")
        require(row.get("source_syntax_delta") == 0, f"SOURCE_DELTA:{rel}")
        require(row.get("product_execution") == "NOT_RUN", f"PRODUCT_EXECUTION:{rel}")

    counts = registry.get("expected_counts", {})
    require(counts == {
        "contract_rows": 5,
        "unique_contract_paths": 5,
        "verified_closed_gaps": 5,
        "historical_provenance_rows": 5,
        "semantic_delta": 0,
        "source_syntax_delta": 0,
        "product_not_run_rows": 5,
    }, "EXPECTED_COUNTS")
    governance = registry.get("governance", {})
    require(governance.get("semantic_p0") == 0, "GOVERNANCE_P0")
    require(governance.get("feature_p1") == "22_OPEN_UNCHANGED", "GOVERNANCE_P1")
    require(governance.get("m13_actions") == "4_OPEN_UNCHANGED", "GOVERNANCE_M13")
    require(governance.get("product_lanes") == "15_OF_15_NOT_RUN", "GOVERNANCE_PRODUCT")
    require(governance.get("github_publication") == "SUSPENDED", "GOVERNANCE_GITHUB")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--registry", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    registry_path = args.registry or root / REGISTRY_REL
    registry = load(registry_path)
    errors = validate(root, registry)
    receipt = {
        "schema": "deeplus.current-contract-authority-status-validation-receipt/r1",
        "result": "PASS" if not errors else "FAIL",
        "contract_rows": len(registry.get("rows", [])),
        "semantic_delta": 0,
        "source_syntax_delta": 0,
        "product_execution": "NOT_RUN",
        "errors": errors,
        "evidence_honesty": "Design-static authority reconciliation does not establish production implementation or product support.",
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
