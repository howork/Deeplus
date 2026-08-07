#!/usr/bin/env python3
"""Recompute the R38 continuation-interface digest and suspension binding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


INTERFACE = "spec/contracts/continuation-interface-r1.json"
SUSPENSION = "spec/contracts/suspension-frame-responsibility-r1.json"
LOWERING = "spec/contracts/hir-mir-lowering-registry.json"
BRIDGE = "spec/contracts/hir-h1-current-mir-bridge.json"
ARTIFACTS = {
    "continuation_receipt_schema": "schemas/language/continuation-receipt-r1.schema.json",
    "suspension_frame_schema": "schemas/language/suspension-frame-responsibility.schema.json",
    "hir_schema": "schemas/language/canonical-hir-h1.schema.json",
    "mir_schema": "schemas/language/deeplus-mir.schema.json",
    "mir_machine_registry": "spec/contracts/mir-machine-registry.json",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def write(path: Path, value: Any) -> None:
    # Bound contract identities are byte-level and must not vary with the
    # host default newline convention.  Git's canonical text form is LF.
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def recompute(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    interface = load(root / INTERFACE)
    suspension = load(root / SUSPENSION)
    lowering = load(root / LOWERING)
    bridge = load(root / BRIDGE)
    bound = {name: digest_file(root / relative) for name, relative in ARTIFACTS.items()}
    components = {
        "frame_epoch_transition_digest": digest_value({
            "frame_states": interface["frame_states"],
            "epoch_states": interface["epoch_states"],
            "transitions": interface["transitions"],
        }),
        "place_slot_loan_digest": digest_value({
            "place_dispositions": interface["place_dispositions"],
            "frame_slot_contract": interface["frame_slot_contract"],
            "loan_fence": interface["loan_fence"],
        }),
        "partition_root_rebind_digest": digest_value({
            "partition_laws": interface["partition_laws"],
            "root_rebind_law": interface["root_rebind_law"],
        }),
        "cleanup_actor_terminal_digest": digest_value({
            "cleanup_law": interface["cleanup_law"],
            "actor_scope_law": interface["actor_scope_law"],
            "race_and_terminal_law": interface["race_and_terminal_law"],
        }),
        "projection_entry_map_digest": digest_value({
            "projection_entry_maps": interface["projection_entry_maps"],
            "dispatch_entry_law": interface["dispatch_entry_law"],
        }),
    }
    interface["bound_artifact_digests"] = bound
    interface["component_digests"] = components
    material = {
        "schema": interface["schema"],
        "interface_identity": interface["interface_identity"],
        "interface_version": interface["interface_version"],
        "authorities": interface["authorities"],
        "canonical_encoding": interface["canonical_encoding"],
        "bound_artifact_digests": bound,
        "identity_domains": interface["identity_domains"],
        "frame_states": interface["frame_states"],
        "epoch_states": interface["epoch_states"],
        "component_digests": components,
    }
    interface["digest_material"] = material
    interface["continuation_interface_digest"] = digest_value(material)
    suspension["continuation_interface"] = {
        "authority_contract": INTERFACE,
        "authority_schema": "schemas/language/continuation-interface-r1.schema.json",
        "receipt_schema": ARTIFACTS["continuation_receipt_schema"],
        "interface_identity": interface["interface_identity"],
        "interface_digest": interface["continuation_interface_digest"],
        "canonical_encoding": interface["canonical_encoding"],
        "bound_artifact_digests": bound,
        "component_digests": components,
        "seam_status": interface["seam_status"],
    }
    lowering["continuation_frame_mapping"]["continuation_interface_digest"] = interface["continuation_interface_digest"]
    bridge["suspension_frame_responsibility_bridge"]["continuation_interface_digest"] = interface["continuation_interface_digest"]
    return interface, suspension, lowering, bridge


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        raise SystemExit("choose exactly one of --write or --check")
    root = args.root.resolve()
    expected_interface, expected_suspension, expected_lowering, expected_bridge = recompute(root)
    if args.check:
        actual_interface = load(root / INTERFACE)
        actual_suspension = load(root / SUSPENSION)
        actual_lowering = load(root / LOWERING)
        actual_bridge = load(root / BRIDGE)
        errors = []
        if actual_interface != expected_interface:
            errors.append("INTERFACE_DRIFT")
        if actual_suspension != expected_suspension:
            errors.append("SUSPENSION_BINDING_DRIFT")
        if actual_lowering != expected_lowering:
            errors.append("LOWERING_BINDING_DRIFT")
        if actual_bridge != expected_bridge:
            errors.append("BRIDGE_BINDING_DRIFT")
        print(json.dumps({"result": "PASS" if not errors else "FAIL", "mode": "check", "errors": errors, "interface_digest": expected_interface["continuation_interface_digest"]}, separators=(",", ":")))
        return 1 if errors else 0
    write(root / INTERFACE, expected_interface)
    write(root / SUSPENSION, expected_suspension)
    write(root / LOWERING, expected_lowering)
    write(root / BRIDGE, expected_bridge)
    print(json.dumps({"result": "PASS", "mode": "write", "interface_digest": expected_interface["continuation_interface_digest"]}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
