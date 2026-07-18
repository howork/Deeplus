#!/usr/bin/env python3
"""Render the bounded Deeplus R2.3 current-integrity closure.

This is static repository tooling. It never runs a Deeplus product lane.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


CONTRACT_REL = "tools/generators/current-integrity.contract.json"
GENERATOR_REL = "tools/generators/generate_current_integrity.py"
EXPECTED_SCHEMA = "deeplus.design-current-integrity-generator-contract/v1"
OUTPUTS = (
    "current/authority-map.yaml",
    "current/current-pointer.json",
    "migration/catalog-reassembly.json",
    "migration/current-document-consistency-repair-r2.3-manifest.json",
)
MANIFEST_REL = OUTPUTS[-1]
SOURCE_MANIFEST_REL = "release/source-tree-manifest.json"
OWNED_REASSEMBLY = {
    "deeplus-0.1.2-baseline-r51f3-feature-registry.json",
    "deeplus-0.1.2-baseline-r51f3-diagnostic-registry.json",
}
OWNED_REASSEMBLY_FIELDS = {
    "row_count",
    "ordered_shard_paths",
    "canonical_object_sha256",
}
EXPECTED_DOMAIN_ORDER = (
    "human_language",
    "exact_grammar",
    "frontend_admission",
    "type_system",
    "mir_observable_semantics",
    "prelude",
    "examples",
    "current_decisions",
    "features",
    "diagnostics",
    "checker_predicates",
)
EXPECTED_RECEIPT_SHA256 = {
    "migration/import-manifest.json": "bbd95f215797a602b17e34888d6c6f90241ed36625fec104708c96f3feee8903",
    "migration/m1.1-repair-manifest.json": "dab1aa035a1839e359365661b8d1fc3ea0f3faafcea6735a7354b0ff6d28b165",
}
EXPECTED_NON_OWNED_SHA256 = {
    "authority_map": "e71114f1b7a53dce712c24db38ed5b7d5c707a35dd437335fdb393a2e6911bb0",
    "pointer": "b15495db761bb8dde9d0ba68dfdb63336997adcea7e3a3b6edfa8ebd16f3647c",
    "reassembly": "e73b4ae7d0a5f2e89b0a808628414ab289cabfbc0332f601d8c7fb84827e5f33",
}
DOMAIN_RE = re.compile(
    r'^  ([a-z_]+):\n'
    r'    path: (\S+)\n'
    r'    owner: "([^"]+)"\n'
    r'    sha256: ([0-9a-f]{64})$',
    re.MULTILINE,
)
AUTHORITY_DIGEST_RE = re.compile(
    r"^authority_digest: ([0-9a-f]{64})$", re.MULTILINE
)


class GeneratorError(RuntimeError):
    """A bounded R2.3 stop condition."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def canonical_sha(value: Any) -> str:
    material = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(material)


def read_json(path: Path, code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GeneratorError(code, f"{path}: {exc}") from exc


def safe_path(root: Path, relative: str | Path, *, must_exist: bool = False) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        raise GeneratorError("R2_3_OUTPUT_ESCAPE", rel.as_posix())
    root = root.resolve()
    lexical = root / rel
    current = root
    for part in rel.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise GeneratorError("R2_3_OUTPUT_ESCAPE", rel.as_posix())
    try:
        resolved = lexical.resolve(strict=must_exist)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise GeneratorError("R2_3_OUTPUT_ESCAPE", rel.as_posix()) from exc
    return lexical


def load_contract(root: Path) -> dict[str, Any]:
    path = safe_path(root, CONTRACT_REL, must_exist=True)
    contract = read_json(path, "R2_3_BOUND_STATE_DRIFT")
    if not isinstance(contract, dict) or contract.get("schema") != EXPECTED_SCHEMA:
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", "contract schema")
    implementation = contract.get("repository_implementation", {})
    expected_impl = {
        "generator": GENERATOR_REL,
        "contract": CONTRACT_REL,
        "test_runner": "tools/validators/run_current_integrity_generator_tests.py",
        "workflow": ".github/workflows/canonical-integrity.yml",
        "validator": "tools/validators/validate_workspace.py",
        "mutation_harness": "tools/validators/run_repository_bootstrap_mutation_tests.py",
        "language": "Python",
        "classification": "NON_PRODUCT_REPOSITORY_TOOLING",
    }
    if implementation != expected_impl:
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", "implementation allowlist")
    declared_outputs = tuple(row.get("path") for row in contract.get("output_ownership", []))
    for rel in declared_outputs:
        safe_path(root, rel)
    if declared_outputs != OUTPUTS or len(set(declared_outputs)) != len(OUTPUTS):
        raise GeneratorError(
            "R2_3_OUTPUT_OWNERSHIP_VIOLATION", repr(declared_outputs)
        )
    if tuple(contract.get("input_authorities", {}).get("domain_order", [])) != EXPECTED_DOMAIN_ORDER:
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", "contract domain order")
    transitions = contract.get("historical_transitions", [])
    if (
        contract.get("historical_receipt_policy", {}).get("transition_count") != 26
        or len(transitions) != 26
        or len({row.get("path") for row in transitions}) != 26
    ):
        raise GeneratorError("R2_3_DELTA_PATH_SET_MISMATCH", "transition count/set")
    required_transition_keys = {
        "path",
        "historical_receipt",
        "classification",
        "frozen_sha256",
        "approved_current_sha256",
        "decision_ids",
    }
    for row in transitions:
        if set(row) != required_transition_keys:
            raise GeneratorError(
                "R2_3_DELTA_PATH_SET_MISMATCH", f"transition shape: {row.get('path')}"
            )
        safe_path(root, row["path"], must_exist=True)
        if row["historical_receipt"] not in EXPECTED_RECEIPT_SHA256:
            raise GeneratorError(
                "R2_3_HISTORICAL_CHAIN_MISMATCH", f"receipt: {row['path']}"
            )
        if not row["classification"] or not row["decision_ids"]:
            raise GeneratorError(
                "R2_3_HISTORICAL_CHAIN_MISMATCH", f"authority: {row['path']}"
            )
        for field in ("frozen_sha256", "approved_current_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", row[field]):
                raise GeneratorError(
                    "R2_3_HISTORICAL_CHAIN_MISMATCH",
                    f"{field}: {row['path']}",
                )
    exclusions = tuple(contract.get("cycle_exclusions", []))
    if exclusions != (
        OUTPUTS[0],
        OUTPUTS[1],
        OUTPUTS[3],
        SOURCE_MANIFEST_REL,
    ):
        raise GeneratorError("R2_3_CURRENT_INTEGRITY_CYCLE", repr(exclusions))
    return contract


def parse_authority_map(root: Path) -> tuple[str, list[tuple[str, str, str, str]]]:
    path = safe_path(root, OUTPUTS[0], must_exist=True)
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", str(exc)) from exc
    rows = DOMAIN_RE.findall(text)
    if tuple(row[0] for row in rows) != EXPECTED_DOMAIN_ORDER:
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", "authority domain order")
    if not AUTHORITY_DIGEST_RE.search(text):
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", "authority aggregate")
    cycle_paths = set(OUTPUTS[:2]) | {OUTPUTS[3], SOURCE_MANIFEST_REL}
    for domain, rel, _owner, _digest in rows:
        target = safe_path(root, rel, must_exist=True)
        rel_norm = Path(rel).as_posix()
        if rel_norm in cycle_paths:
            raise GeneratorError("R2_3_CURRENT_INTEGRITY_CYCLE", f"{domain}: {rel}")
        if target.is_dir():
            for forbidden in cycle_paths:
                try:
                    safe_path(root, forbidden).relative_to(target)
                except ValueError:
                    continue
                raise GeneratorError(
                    "R2_3_CURRENT_INTEGRITY_CYCLE", f"{domain}: {forbidden}"
                )
    normalized = re.sub(
        r"^    sha256: [0-9a-f]{64}$",
        "    sha256: <OWNED>",
        text,
        flags=re.MULTILINE,
    )
    normalized = AUTHORITY_DIGEST_RE.sub("authority_digest: <OWNED>", normalized)
    if sha256_bytes(normalized.encode("utf-8")) != EXPECTED_NON_OWNED_SHA256["authority_map"]:
        raise GeneratorError("R2_3_NON_OWNED_FIELD_DRIFT", OUTPUTS[0])
    return text, rows


def domain_digest(root: Path, relative: str) -> str:
    target = safe_path(root, relative, must_exist=True)
    if target.is_file():
        return sha256_bytes(target.read_bytes())
    if not target.is_dir():
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", relative)
    material_rows: list[str] = []
    # This repository-relative spelling deliberately matches validate_workspace.py.
    for path in sorted(target.rglob("*.json")):
        if path.is_symlink():
            raise GeneratorError("R2_3_OUTPUT_ESCAPE", path.as_posix())
        try:
            resolved = path.resolve(strict=True)
            rel = resolved.relative_to(root)
        except (OSError, ValueError) as exc:
            raise GeneratorError("R2_3_OUTPUT_ESCAPE", path.as_posix()) from exc
        material_rows.append(rel.as_posix() + "\0" + sha256_bytes(path.read_bytes()))
    return sha256_bytes("\n".join(material_rows).encode("utf-8"))


def render_authority(
    root: Path,
    text: str,
    rows: list[tuple[str, str, str, str]],
) -> tuple[bytes, str, list[dict[str, str]]]:
    digest_rows: list[dict[str, str]] = []
    actual: dict[str, str] = {}
    for domain, rel, owner, _declared in rows:
        digest = domain_digest(root, rel)
        actual[domain] = digest
        digest_rows.append(
            {"domain": domain, "path": rel, "sha256": digest, "owner": owner}
        )
    aggregate = canonical_sha(digest_rows)

    def replace_domain(match: re.Match[str]) -> str:
        domain, rel, owner, _old = match.groups()
        return (
            f"  {domain}:\n"
            f"    path: {rel}\n"
            f'    owner: "{owner}"\n'
            f"    sha256: {actual[domain]}"
        )

    rendered = DOMAIN_RE.sub(replace_domain, text)
    rendered = AUTHORITY_DIGEST_RE.sub(
        f"authority_digest: {aggregate}", rendered, count=1
    )
    return rendered.encode("utf-8"), aggregate, digest_rows


def validate_pointer(root: Path) -> tuple[str, dict[str, Any]]:
    path = safe_path(root, OUTPUTS[1], must_exist=True)
    raw = path.read_bytes().decode("utf-8")
    pointer = read_json(path, "R2_3_BOUND_STATE_DRIFT")
    if not isinstance(pointer, dict) or "authority_digest" not in pointer:
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", OUTPUTS[1])
    non_owned = copy.deepcopy(pointer)
    non_owned.pop("authority_digest", None)
    if canonical_sha(non_owned) != EXPECTED_NON_OWNED_SHA256["pointer"]:
        raise GeneratorError("R2_3_NON_OWNED_FIELD_DRIFT", OUTPUTS[1])
    lanes = pointer.get("product_lanes", {})
    if (
        not isinstance(lanes, dict)
        or len(lanes) != 15
        or any(value != "NOT_RUN" for value in lanes.values())
    ):
        raise GeneratorError("R2_3_PRODUCT_LANE_TRANSITION", "pointer product_lanes")
    return raw, pointer


def render_pointer(raw: str, old_digest: str, aggregate: str) -> bytes:
    needle = f'"authority_digest": "{old_digest}"'
    if raw.count(needle) != 1:
        raise GeneratorError("R2_3_OUTPUT_OWNERSHIP_VIOLATION", OUTPUTS[1])
    return raw.replace(
        needle, f'"authority_digest": "{aggregate}"', 1
    ).encode("utf-8")


def validate_product_lanes(root: Path) -> None:
    lanes_doc = read_json(
        safe_path(root, "current/product-lanes.json", must_exist=True),
        "R2_3_BOUND_STATE_DRIFT",
    )
    lanes = lanes_doc.get("lanes", []) if isinstance(lanes_doc, dict) else []
    ids = [row.get("lane_id") for row in lanes if isinstance(row, dict)]
    if (
        len(lanes) != 15
        or len(set(ids)) != 15
        or any(row.get("status") != "NOT_RUN" for row in lanes)
    ):
        raise GeneratorError("R2_3_PRODUCT_LANE_TRANSITION", "registry product_lanes")


def render_reassembly(root: Path) -> bytes:
    path = safe_path(root, OUTPUTS[2], must_exist=True)
    original = read_json(path, "R2_3_BOUND_STATE_DRIFT")
    if not isinstance(original, dict) or not isinstance(original.get("contracts"), list):
        raise GeneratorError("R2_3_BOUND_STATE_DRIFT", OUTPUTS[2])
    non_owned = copy.deepcopy(original)
    for row in non_owned["contracts"]:
        if row.get("legacy_file") in OWNED_REASSEMBLY:
            for field in OWNED_REASSEMBLY_FIELDS:
                row.pop(field, None)
    if canonical_sha(non_owned) != EXPECTED_NON_OWNED_SHA256["reassembly"]:
        raise GeneratorError("R2_3_NON_OWNED_FIELD_DRIFT", OUTPUTS[2])
    rendered = copy.deepcopy(original)
    found: set[str] = set()
    for contract in rendered["contracts"]:
        legacy = contract.get("legacy_file")
        if legacy not in OWNED_REASSEMBLY:
            continue
        found.add(legacy)
        shard_root = safe_path(root, contract["shard_root"], must_exist=True)
        shard_paths = sorted(shard_root.glob("chunks/part-*.json"))
        ordered = [path.relative_to(root).as_posix() for path in shard_paths]
        if not ordered:
            raise GeneratorError("R2_3_BOUND_STATE_DRIFT", f"no shards: {legacy}")
        rows: list[Any] = []
        for shard in shard_paths:
            value = read_json(shard, "R2_3_BOUND_STATE_DRIFT")
            if not isinstance(value, list):
                raise GeneratorError("R2_3_BOUND_STATE_DRIFT", shard.as_posix())
            rows.extend(value)
        metadata = read_json(
            safe_path(root, contract["metadata_path"], must_exist=True),
            "R2_3_BOUND_STATE_DRIFT",
        )
        if not isinstance(metadata, dict):
            raise GeneratorError("R2_3_BOUND_STATE_DRIFT", contract["metadata_path"])
        document = dict(metadata)
        document[contract["array_key"]] = rows
        contract["row_count"] = len(rows)
        contract["ordered_shard_paths"] = ordered
        contract["canonical_object_sha256"] = canonical_sha(document)
    if found != OWNED_REASSEMBLY:
        raise GeneratorError("R2_3_OUTPUT_OWNERSHIP_VIOLATION", "reassembly contracts")
    after_non_owned = copy.deepcopy(rendered)
    for row in after_non_owned["contracts"]:
        if row.get("legacy_file") in OWNED_REASSEMBLY:
            for field in OWNED_REASSEMBLY_FIELDS:
                row.pop(field, None)
    if after_non_owned != non_owned:
        raise GeneratorError("R2_3_NON_OWNED_FIELD_DRIFT", OUTPUTS[2])
    return json_bytes(rendered)


def receipt_old_hash(
    receipt: dict[str, Any], receipt_path: str, transition_path: str
) -> str | None:
    if receipt_path == "migration/m1.1-repair-manifest.json":
        rows = receipt.get("reference_normalization", {}).get("transformations", [])
        matches = [
            row.get("output_sha256")
            for row in rows
            if row.get("path") == transition_path
        ]
        return matches[0] if len(matches) == 1 else None
    legacy = receipt.get("legacy_files", [])
    matches = [
        row.get("sha256")
        for row in legacy
        if transition_path in row.get("current_paths", [])
        and row.get("disposition") != "MIGRATED_SOURCE_SHARDS"
    ]
    return matches[0] if len(matches) == 1 else None


def validate_historical_chain(
    root: Path, contract: dict[str, Any]
) -> list[dict[str, str]]:
    receipts: dict[str, dict[str, Any]] = {}
    receipt_rows: list[dict[str, str]] = []
    for rel, expected in EXPECTED_RECEIPT_SHA256.items():
        path = safe_path(root, rel, must_exist=True)
        actual = sha256_bytes(path.read_bytes())
        if actual != expected:
            raise GeneratorError("R2_3_HISTORICAL_RECEIPT_DRIFT", rel)
        receipt = read_json(path, "R2_3_HISTORICAL_RECEIPT_DRIFT")
        if not isinstance(receipt, dict):
            raise GeneratorError("R2_3_HISTORICAL_RECEIPT_DRIFT", rel)
        receipts[rel] = receipt
        receipt_rows.append({"path": rel, "sha256": actual})
    for row in contract["historical_transitions"]:
        rel = row["path"]
        current = sha256_bytes(safe_path(root, rel, must_exist=True).read_bytes())
        if current != row["approved_current_sha256"]:
            raise GeneratorError("R2_3_CANDIDATE_B_PATCH_DRIFT", rel)
        old = receipt_old_hash(
            receipts[row["historical_receipt"]], row["historical_receipt"], rel
        )
        if old != row["frozen_sha256"]:
            raise GeneratorError("R2_3_HISTORICAL_CHAIN_MISMATCH", rel)
    return receipt_rows


def render_manifest(
    root: Path,
    contract: dict[str, Any],
    rendered: dict[str, bytes],
    receipt_rows: list[dict[str, str]],
    digest_rows: list[dict[str, str]],
    authority_digest: str,
) -> bytes:
    transition_paths = {row["path"] for row in contract["historical_transitions"]}
    if MANIFEST_REL in transition_paths or SOURCE_MANIFEST_REL in transition_paths:
        raise GeneratorError("R2_3_DELTA_PATH_SET_MISMATCH", "excluded delta path")
    generated_outputs = [
        {
            "path": rel,
            "sha256": sha256_bytes(rendered[rel]),
            "ownership": (
                "domains[*].sha256 and authority_digest"
                if rel == OUTPUTS[0]
                else "authority_digest only"
                if rel == OUTPUTS[1]
                else "feature/diagnostic reassembly owned fields only"
            ),
        }
        for rel in OUTPUTS[:3]
    ]
    manifest = {
        "schema": "deeplus.current-document-consistency-repair-delta/v1",
        "revision": "R2.3",
        "result": "STATIC_CURRENT_INTEGRITY_CLOSURE",
        "evidence_boundary": contract["evidence_boundary"],
        "authority_decision": contract["authority_decision"],
        "frozen_base": contract["frozen_base"],
        "candidate_chain_input": {
            "candidate_g": contract["stopped_state"]["candidate_g"],
            "candidate_a": contract["stopped_state"]["candidate_a"],
            "candidate_b_state": "APPROVED_CURRENT_BYTES",
        },
        "generator": {
            "path": GENERATOR_REL,
            "sha256": sha256_bytes(safe_path(root, GENERATOR_REL, must_exist=True).read_bytes()),
            "contract": CONTRACT_REL,
            "contract_sha256": sha256_bytes(
                safe_path(root, CONTRACT_REL, must_exist=True).read_bytes()
            ),
        },
        "non_self_reference_policy": {
            "manifest_self_hash": "EXCLUDED",
            "source_tree_manifest": "EXCLUDED_AND_GENERATED_AFTER_CURRENT_INTEGRITY",
            "excluded_paths": [MANIFEST_REL, SOURCE_MANIFEST_REL],
        },
        "immutable_historical_receipts": receipt_rows,
        "transition_count": 26,
        "transitions": contract["historical_transitions"],
        "authority_domains": digest_rows,
        "authority_digest": authority_digest,
        "generated_outputs_excluding_self": generated_outputs,
        "product_lanes": {"count": 15, "required_state": "NOT_RUN"},
        "remote_actions": {
            "push": False,
            "pull_request": False,
            "issue": False,
            "ci": False,
            "merge": False,
            "publication": False,
        },
    }
    return json_bytes(manifest)


def render_outputs(root: Path) -> dict[str, bytes]:
    root = root.resolve()
    contract = load_contract(root)
    validate_product_lanes(root)
    receipt_rows = validate_historical_chain(root, contract)
    authority_text, authority_rows = parse_authority_map(root)
    pointer_raw, pointer = validate_pointer(root)
    reassembly_bytes = render_reassembly(root)
    authority_bytes, aggregate, digest_rows = render_authority(
        root, authority_text, authority_rows
    )
    pointer_bytes = render_pointer(
        pointer_raw, pointer["authority_digest"], aggregate
    )
    rendered = {
        OUTPUTS[0]: authority_bytes,
        OUTPUTS[1]: pointer_bytes,
        OUTPUTS[2]: reassembly_bytes,
    }
    rendered[OUTPUTS[3]] = render_manifest(
        root, contract, rendered, receipt_rows, digest_rows, aggregate
    )
    if tuple(rendered) != OUTPUTS:
        raise GeneratorError(
            "R2_3_OUTPUT_OWNERSHIP_VIOLATION", repr(tuple(rendered))
        )
    return rendered


def stale_outputs(root: Path, rendered: dict[str, bytes]) -> list[str]:
    stale = []
    for rel in OUTPUTS:
        path = safe_path(root, rel)
        if not path.is_file() or path.read_bytes() != rendered[rel]:
            stale.append(rel)
    return stale


def write_outputs(root: Path, rendered: dict[str, bytes]) -> None:
    staged: list[tuple[Path, Path]] = []
    try:
        for rel in OUTPUTS:
            target = safe_path(root, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temp_name = tempfile.mkstemp(
                prefix=f".{target.name}.r2_3.", dir=target.parent
            )
            temp_path = Path(temp_name)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(rendered[rel])
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((temp_path, target))
        for temp_path, target in staged:
            os.replace(temp_path, target)
    finally:
        for temp_path, _target in staged:
            if temp_path.exists():
                temp_path.unlink()


def receipt(mode: str, result: str, rendered: dict[str, bytes], stale: list[str]) -> dict[str, Any]:
    return {
        "schema": "deeplus.current-integrity-generator-receipt/v1",
        "revision": "R2.3",
        "mode": mode,
        "result": result,
        "owned_output_count": len(OUTPUTS),
        "stale_output_count": len(stale),
        "stale_outputs": stale,
        "output_sha256": {
            rel: sha256_bytes(rendered[rel]) for rel in OUTPUTS
        },
        "historical_transition_count": 26,
        "authority_domain_count": 11,
        "product_lanes": "15/15 NOT_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        rendered = render_outputs(root)
        stale = stale_outputs(root, rendered)
        if args.check:
            result = "PASS" if not stale else "CURRENT_INTEGRITY_BASELINE_MISMATCH"
            print(json.dumps(receipt("check", result, rendered, stale), ensure_ascii=False, indent=2))
            return 0 if not stale else 2
        write_outputs(root, rendered)
        remaining = stale_outputs(root, rendered)
        result = "PASS" if not remaining else "R2_3_CURRENT_INTEGRITY_CHECK_MISMATCH"
        print(json.dumps(receipt("write", result, rendered, remaining), ensure_ascii=False, indent=2))
        return 0 if not remaining else 1
    except GeneratorError as exc:
        print(
            json.dumps(
                {
                    "schema": "deeplus.current-integrity-generator-receipt/v1",
                    "revision": "R2.3",
                    "result": "BLOCKED",
                    "stop_code": exc.code,
                    "detail": exc.detail,
                    "product_lanes": "15/15 NOT_RUN",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
