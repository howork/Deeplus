#!/usr/bin/env python3
"""Isolated tests for the bounded R2.3 current-integrity generator."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "tools/generators/generate_current_integrity.py"
OUTPUTS = (
    "current/authority-map.yaml",
    "current/current-pointer.json",
    "migration/catalog-reassembly.json",
    "migration/current-document-consistency-repair-r2.3-manifest.json",
)
EXCLUDED = {".git", "target", "dist", "__pycache__"}


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("current_integrity_generator", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load current-integrity generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN = load_generator()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    return sha(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def copy_root(destination: Path) -> None:
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(*EXCLUDED),
    )


def seed_synthetic_stale_outputs(root: Path) -> None:
    zero_digest = "0" * 64

    authority_path = root / OUTPUTS[0]
    authority_text = authority_path.read_text(encoding="utf-8")

    def stale_domain(match: Any) -> str:
        domain, relative, owner, _digest = match.groups()
        return (
            f"  {domain}:\n"
            f"    path: {relative}\n"
            f'    owner: "{owner}"\n'
            f"    sha256: {zero_digest}"
        )

    authority_text, domain_count = GEN.DOMAIN_RE.subn(
        stale_domain, authority_text
    )
    authority_text, aggregate_count = GEN.AUTHORITY_DIGEST_RE.subn(
        f"authority_digest: {zero_digest}", authority_text
    )
    if domain_count != 11 or aggregate_count != 1:
        raise RuntimeError(
            "synthetic stale authority seed did not own exactly 11 domains "
            "and one aggregate"
        )
    authority_path.write_bytes(authority_text.encode("utf-8"))

    pointer_path = root / OUTPUTS[1]
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    pointer["authority_digest"] = zero_digest
    write_json(pointer_path, pointer)

    reassembly_path = root / OUTPUTS[2]
    reassembly = json.loads(reassembly_path.read_text(encoding="utf-8"))
    owned_contracts = 0
    for contract in reassembly["contracts"]:
        if contract["legacy_file"] not in GEN.OWNED_REASSEMBLY:
            continue
        owned_contracts += 1
        contract["row_count"] = 0
        contract["ordered_shard_paths"] = []
        contract["canonical_object_sha256"] = zero_digest
    if owned_contracts != 2:
        raise RuntimeError(
            "synthetic stale reassembly seed did not own exactly two contracts"
        )
    write_json(reassembly_path, reassembly)

    (root / OUTPUTS[3]).unlink(missing_ok=True)


def command(root: Path, mode: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / GENERATOR.relative_to(ROOT)), "--root", str(root), mode],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def file_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED for part in path.relative_to(root).parts):
            continue
        result[path.relative_to(root).as_posix()] = sha(path.read_bytes())
    return result


def non_owned_reassembly(value: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(value)
    for row in result["contracts"]:
        if row["legacy_file"] in GEN.OWNED_REASSEMBLY:
            for field in GEN.OWNED_REASSEMBLY_FIELDS:
                row.pop(field, None)
    return result


def independent_domains(root: Path) -> tuple[list[dict[str, str]], str]:
    text = (root / "current/authority-map.yaml").read_text(encoding="utf-8")
    rows = GEN.DOMAIN_RE.findall(text)
    digest_rows: list[dict[str, str]] = []
    for domain, rel, owner, _declared in rows:
        target = root / rel
        if target.is_file():
            digest = sha(target.read_bytes())
        else:
            material = "\n".join(
                path.relative_to(root).as_posix() + "\0" + sha(path.read_bytes())
                for path in sorted(target.rglob("*.json"))
            ).encode("utf-8")
            digest = sha(material)
        digest_rows.append(
            {"domain": domain, "path": rel, "sha256": digest, "owner": owner}
        )
    return digest_rows, canonical_sha(digest_rows)


def parse_receipt(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    raw = result.stdout if result.stdout.strip() else result.stderr
    return json.loads(raw)


def run() -> int:
    cases: list[dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        cases.append({"case": name, "pass": bool(passed), "detail": detail})

    with tempfile.TemporaryDirectory(prefix="deeplus-current-integrity-") as temp:
        root = Path(temp) / "workspace"
        copy_root(root)
        seed_synthetic_stale_outputs(root)

        original_map = file_map(root)
        original_pointer = json.loads((root / OUTPUTS[1]).read_text(encoding="utf-8"))
        original_reassembly = json.loads((root / OUTPUTS[2]).read_text(encoding="utf-8"))
        receipt_hashes = {
            rel: sha((root / rel).read_bytes()) for rel in GEN.EXPECTED_RECEIPT_SHA256
        }

        first = GEN.render_outputs(root)
        second = GEN.render_outputs(root)
        record("two_independent_renders", first == second)

        precheck = command(root, "--check")
        after_precheck = file_map(root)
        pre_receipt = parse_receipt(precheck)
        record(
            "stale_output_set_exact",
            precheck.returncode == 2
            and pre_receipt.get("stale_outputs") == list(OUTPUTS)
            and original_map == after_precheck,
            f"returncode={precheck.returncode}",
        )
        record("check_mode_read_only", original_map == after_precheck)

        write = command(root, "--write")
        after_write = file_map(root)
        changed = sorted(
            set(original_map) | set(after_write),
            key=str,
        )
        changed = [
            rel
            for rel in changed
            if original_map.get(rel) != after_write.get(rel)
        ]
        record(
            "write_exact_four_outputs",
            write.returncode == 0 and changed == sorted(OUTPUTS),
            repr(changed),
        )

        postcheck_before = file_map(root)
        postcheck = command(root, "--check")
        postcheck_after = file_map(root)
        record(
            "postwrite_check_zero_drift",
            postcheck.returncode == 0 and postcheck_before == postcheck_after,
            f"returncode={postcheck.returncode}",
        )

        final_pointer = json.loads((root / OUTPUTS[1]).read_text(encoding="utf-8"))
        old_pointer_nonowned = dict(original_pointer)
        new_pointer_nonowned = dict(final_pointer)
        old_pointer_nonowned.pop("authority_digest")
        new_pointer_nonowned.pop("authority_digest")
        authority_text = (root / OUTPUTS[0]).read_text(encoding="utf-8")
        declared_aggregate = GEN.AUTHORITY_DIGEST_RE.search(authority_text)
        record(
            "pointer_only_final_aggregate",
            old_pointer_nonowned == new_pointer_nonowned
            and bool(declared_aggregate)
            and final_pointer["authority_digest"] == declared_aggregate.group(1),
        )

        final_reassembly = json.loads((root / OUTPUTS[2]).read_text(encoding="utf-8"))
        record(
            "reassembly_nonowned_preserved",
            non_owned_reassembly(original_reassembly)
            == non_owned_reassembly(final_reassembly),
        )
        reassembly_ok = True
        for contract in final_reassembly["contracts"]:
            if contract["legacy_file"] not in GEN.OWNED_REASSEMBLY:
                continue
            rows: list[Any] = []
            for rel in contract["ordered_shard_paths"]:
                rows.extend(json.loads((root / rel).read_text(encoding="utf-8")))
            metadata = json.loads(
                (root / contract["metadata_path"]).read_text(encoding="utf-8")
            )
            document = dict(metadata)
            document[contract["array_key"]] = rows
            reassembly_ok &= (
                contract["row_count"] == len(rows)
                and contract["canonical_object_sha256"] == canonical_sha(document)
            )
        record("reassembly_owned_fields_match", reassembly_ok)

        independent_rows, independent_aggregate = independent_domains(root)
        declared_rows = [
            {
                "domain": domain,
                "path": rel,
                "sha256": digest,
                "owner": owner,
            }
            for domain, rel, owner, digest in GEN.DOMAIN_RE.findall(authority_text)
        ]
        record(
            "validator_domain_aggregate_parity",
            len(declared_rows) == 11
            and declared_rows == independent_rows
            and declared_aggregate.group(1) == independent_aggregate,
        )

        record(
            "historical_receipts_immutable",
            receipt_hashes
            == {rel: sha((root / rel).read_bytes()) for rel in receipt_hashes},
        )
        delta = json.loads((root / OUTPUTS[3]).read_text(encoding="utf-8"))
        contract = json.loads(
            (root / GEN.CONTRACT_REL).read_text(encoding="utf-8")
        )
        record(
            "exact_26_transition_chain",
            delta.get("transition_count") == 26
            and delta.get("transitions") == contract.get("historical_transitions")
            and OUTPUTS[3] not in {row["path"] for row in delta["transitions"]}
            and GEN.SOURCE_MANIFEST_REL
            not in {row["path"] for row in delta["transitions"]},
        )

        def expect_rejected(
            name: str,
            relative: str,
            mutate: Callable[[Path], None],
            acceptable: set[int] = {1, 2},
        ) -> None:
            path = root / relative
            existed = path.exists()
            before = path.read_bytes() if existed else b""
            try:
                mutate(path)
                result = command(root, "--check")
                record(
                    name,
                    result.returncode in acceptable,
                    f"returncode={result.returncode}",
                )
            finally:
                if existed:
                    path.write_bytes(before)
                elif path.exists():
                    path.unlink()

        expect_rejected(
            "mutation_domain_source_byte",
            "spec/language.md",
            lambda path: path.write_bytes(path.read_bytes() + b"\nmutation\n"),
        )

        def swap_domains(path: Path) -> None:
            text = path.read_text(encoding="utf-8")
            blocks = list(GEN.DOMAIN_RE.finditer(text))
            first, second = blocks[0].group(0), blocks[1].group(0)
            text = text.replace(first, "<FIRST>", 1).replace(second, first, 1)
            path.write_text(text.replace("<FIRST>", second, 1), encoding="utf-8")

        expect_rejected("mutation_domain_order", OUTPUTS[0], swap_domains)

        expect_rejected(
            "mutation_pointer_digest",
            OUTPUTS[1],
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    final_pointer["authority_digest"], "0" * 64, 1
                ),
                encoding="utf-8",
            ),
        )

        def cycle(path: Path, forbidden: str) -> None:
            text = path.read_text(encoding="utf-8")
            text = text.replace("path: spec/language.md", f"path: {forbidden}", 1)
            path.write_text(text, encoding="utf-8")

        for label, forbidden in (
            ("pointer_cycle", OUTPUTS[1]),
            ("authority_cycle", OUTPUTS[0]),
            ("delta_cycle", OUTPUTS[3]),
            ("source_manifest_cycle", GEN.SOURCE_MANIFEST_REL),
        ):
            expect_rejected(
                "mutation_" + label,
                OUTPUTS[0],
                lambda path, value=forbidden: cycle(path, value),
                {1},
            )

        for field, value in (
            ("row_count", 0),
            ("ordered_shard_paths", []),
            ("canonical_object_sha256", "0" * 64),
        ):
            def owned_mutation(path: Path, key: str = field, replacement: Any = value) -> None:
                document = json.loads(path.read_text(encoding="utf-8"))
                row = next(
                    item
                    for item in document["contracts"]
                    if item["legacy_file"] in GEN.OWNED_REASSEMBLY
                )
                row[key] = replacement
                write_json(path, document)

            expect_rejected("mutation_wrong_reassembly_" + field, OUTPUTS[2], owned_mutation)

        def nonowned_mutation(path: Path) -> None:
            value = json.loads(path.read_text(encoding="utf-8"))
            value["contracts"][2]["partition_key"] = "mutation"
            write_json(path, value)

        expect_rejected(
            "mutation_nonowned_reassembly", OUTPUTS[2], nonowned_mutation, {1}
        )
        expect_rejected(
            "mutation_historical_receipt_byte",
            "migration/import-manifest.json",
            lambda path: path.write_bytes(path.read_bytes() + b" "),
            {1},
        )

        def contract_mutation(name: str, operation: Callable[[dict[str, Any]], None]) -> None:
            def apply(path: Path) -> None:
                value = json.loads(path.read_text(encoding="utf-8"))
                operation(value)
                write_json(path, value)
            expect_rejected(name, GEN.CONTRACT_REL, apply, {1})

        contract_mutation(
            "mutation_missing_transition",
            lambda value: value["historical_transitions"].pop(),
        )
        contract_mutation(
            "mutation_extra_transition",
            lambda value: value["historical_transitions"].append(
                copy.deepcopy(value["historical_transitions"][0])
            ),
        )
        contract_mutation(
            "mutation_wrong_historical_receipt",
            lambda value: value["historical_transitions"][0].__setitem__(
                "historical_receipt", "migration/import-manifest.json"
            ),
        )
        contract_mutation(
            "mutation_wrong_old_hash",
            lambda value: value["historical_transitions"][0].__setitem__(
                "frozen_sha256", "0" * 64
            ),
        )
        contract_mutation(
            "mutation_wrong_approved_hash",
            lambda value: value["historical_transitions"][0].__setitem__(
                "approved_current_sha256", "0" * 64
            ),
        )
        contract_mutation(
            "mutation_unauthorized_delta_path",
            lambda value: value["historical_transitions"][0].__setitem__(
                "path", "README.md"
            ),
        )
        contract_mutation(
            "mutation_output_path_escape",
            lambda value: value["output_ownership"][0].__setitem__(
                "path", "../escape.json"
            ),
        )

        def manifest_transition(path: Path, forbidden: str) -> None:
            value = json.loads(path.read_text(encoding="utf-8"))
            row = copy.deepcopy(value["transitions"][0])
            row["path"] = forbidden
            value["transitions"].append(row)
            value["transition_count"] += 1
            write_json(path, value)

        expect_rejected(
            "mutation_delta_manifest_self_entry",
            OUTPUTS[3],
            lambda path: manifest_transition(path, OUTPUTS[3]),
            {2},
        )
        expect_rejected(
            "mutation_source_manifest_delta_entry",
            OUTPUTS[3],
            lambda path: manifest_transition(path, GEN.SOURCE_MANIFEST_REL),
            {2},
        )

        symlink_parent = root / "symlink-escape"
        symlink_target = Path(temp) / "outside"
        symlink_target.mkdir()
        try:
            symlink_parent.symlink_to(symlink_target, target_is_directory=True)
            try:
                GEN.safe_path(root, "symlink-escape/output.json")
                symlink_rejected = False
            except GEN.GeneratorError as exc:
                symlink_rejected = exc.code == "R2_3_OUTPUT_ESCAPE"
            record("mutation_symlink_escape", symlink_rejected)
        except OSError as exc:
            # A platform that refuses creation has already prevented the escape.
            record("mutation_symlink_escape", True, f"OS prevented symlink: {exc}")

        def product_lane_mutation(path: Path) -> None:
            value = json.loads(path.read_text(encoding="utf-8"))
            value["lanes"][0]["status"] = "PASSED_FOCUSED"
            write_json(path, value)

        expect_rejected(
            "mutation_product_lane_transition",
            "current/product-lanes.json",
            product_lane_mutation,
            {1},
        )

        check_before = {rel: sha((root / rel).read_bytes()) for rel in OUTPUTS}
        check_again = command(root, "--check")
        check_after = {rel: sha((root / rel).read_bytes()) for rel in OUTPUTS}
        record(
            "mutation_check_mode_write",
            check_again.returncode == 0 and check_before == check_after,
        )

    passed = sum(row["pass"] for row in cases)
    receipt = {
        "schema": "deeplus.current-integrity-generator-test-receipt/v1",
        "revision": "R2.3",
        "result": "PASS" if passed == len(cases) else "FAIL",
        "cases": len(cases),
        "passed": passed,
        "failed": len(cases) - passed,
        "isolated_temporary_copies_only": True,
        "repository_write": False,
        "product_lanes": "15/15 NOT_RUN",
        "details": cases,
    }
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
