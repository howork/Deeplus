#!/usr/bin/env python3
"""Validate the bounded R66 responsibility-identity dynamic trace closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DECISION_REL = "decisions/language/Design_Deeplus_R66_Responsibility_Identity_Dynamic_Trace_Closure_R1.md"
OVERLAY_REL = "spec/traceability/implementation-target-profile-r1/responsibility-identity-dynamic-trace-evidence-r1.json"
OVERLAY_SCHEMA_REL = "schemas/language/responsibility-identity-dynamic-trace-evidence-r1.schema.json"
CONTRACT_REL = "spec/contracts/responsibility-identity-registry-r1.json"
HIR_SCHEMA_REL = "schemas/language/canonical-hir-h1.schema.json"
MIR_SCHEMA_REL = "schemas/language/deeplus-mir.schema.json"
LOWERING_REL = "spec/contracts/hir-mir-lowering-registry.json"
MACHINE_REL = "spec/contracts/mir-machine-registry.json"
ROWS_REL = "spec/traceability/implementation-target-profile-r1/rows.json"
META_REL = "spec/traceability/implementation-target-profile-r1/catalog-metadata.json"
VALIDATOR_REL = "tools/validators/validate_responsibility_identity_dynamic_trace.py"

CANONICAL = "39a5d50cc770341c4b9776d00d84520b780d0c62"
PREDECESSOR = "5c36347f7ed7d2d23e5342f311766cea93b6aa89"
FEATURE = "responsibility_identity_registry_r1"
TARGET = (FEATURE, "DYNAMIC_LOWERING", None)
OVERLAY_REVISION = "r66-local-responsibility-identity-dynamic-trace-closure-r1"
EVIDENCE_KEY = "R66:responsibility_identity_registry_r1:DYNAMIC_LOWERING:PROJECTION"
NON_TARGET_SHA256 = "53c0461b1dfd6252f0886fe075eac6518843a969d446584471280c82a253f26c"

HIR_FIELDS = [
    "responsibility_rule_id", "responsibility_evidence_id", "type_id",
    "evidence_kind", "registry_revision", "derivation_digest",
    "trait_witness_id_or_null", "error_set_id_or_null",
    "effect_row_id_or_null", "result_acquisition_plan_id_or_null",
    "cleanup_plan_id_or_null", "owner_id_or_null", "region_id_or_null",
    "destination_isolation_domain_id_or_null", "source_provenance",
]
MIR_FIELDS = HIR_FIELDS[:-1] + ["source_origin_id"]
R30_HIR_FIELDS = [
    "ResponsibilityRuleId", "ResponsibilityEvidenceId", "TypeId",
    "EvidenceKind", "RegistryRevision", "DerivationDigest",
    "TraitWitnessIdOrNull", "ErrorSetIdOrNull", "EffectRowIdOrNull",
    "ResultAcquisitionPlanIdOrNull", "CleanupPlanIdOrNull", "OwnerIdOrNull",
    "RegionIdOrNull", "DestinationIsolationDomainIdOrNull", "SourceProvenance",
]
R30_MIR_FIELDS = R30_HIR_FIELDS[:-1] + ["SourceOriginId"]
IDENTITIES = ["PlainValue", "Shareable", "Transferable", "CopyValue", "Clone", "DeepClone"]

PROTECTED = {
    CONTRACT_REL: "533767a103487ecd96f62a77cc37173fc80cc18dbb6bd0b98caecbe0a8a2d7cf",
    "schemas/language/responsibility-identity-registry-r1.schema.json": "6ede17e8098bc9d7b5208bcfc74239737536e66ec2162186cf4fa70224d61e45",
    "tests/fixtures/current/responsibility-identity-registry-r1.json": "b630cae0cb1aaa575a830056f8595b42c5b786616f0d0f24d01b1d45a8240f2f",
    HIR_SCHEMA_REL: "399f5a0e8be29e8f544084906b12f796be1bb087f063d9d8a68def56c30cfb5b",
    MIR_SCHEMA_REL: "f57f1ca996f7769fcad10fcfa9823e0198c9cfd0ee3110e1177f60bf1cbf0a55",
    LOWERING_REL: "5f03bd3bdd1cf00649bd9c99ba6e2ec1c199103d1e81c2546787c485cde99bfe",
    MACHINE_REL: "0c02ce9643736cc284b1f89c44c68fc6ce277f24168db160f0660268feaa8405",
}

GATES = {
    "G01": "identity_and_scope",
    "G02": "predecessor_blocked_cell",
    "G03": "r30_identity_and_residue",
    "G04": "canonical_hir_descriptor",
    "G05": "canonical_mir_and_projection",
    "G06": "overlay_exact_direct_binding",
    "G07": "generated_trace_counts_and_fence",
    "G08": "protected_byte_fences",
    "G09": "governance_schema_paths_and_product",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_id(row: dict[str, Any]) -> str:
    material = "\0".join(
        [row["class"], row["path"], row["locator_kind"], row["locator"], row["stage_role"]]
    )
    return "EV-" + hashlib.sha256(material.encode()).hexdigest()


def trace_cells(rows: list[dict[str, Any]]) -> tuple[dict[tuple[str, str, str | None], dict[str, Any]], int]:
    cells: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        for stage in row.get("stages", []):
            for cell in stage.get("outcomes", [stage]):
                outcome = cell.get("outcome") if stage.get("stage") == "CONFORMANCE_TESTS" else None
                key = (row.get("feature_id"), stage.get("stage"), outcome)
                duplicates += key in cells
                cells[key] = cell
    return cells, duplicates


def non_target_digest(cells: dict[tuple[str, str, str | None], dict[str, Any]]) -> tuple[int, str]:
    material = [[*key, value] for key, value in cells.items() if key != TARGET]
    material.sort(key=lambda row: (row[0], row[1], row[2] or ""))
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return len(material), hashlib.sha256(encoded).hexdigest()


def validate(
    root: Path,
    *,
    overlay_override: dict[str, Any] | None = None,
    contract_override: dict[str, Any] | None = None,
    hir_schema_override: dict[str, Any] | None = None,
    mir_schema_override: dict[str, Any] | None = None,
    lowering_registry_override: dict[str, Any] | None = None,
    machine_registry_override: dict[str, Any] | None = None,
    rows_override: list[dict[str, Any]] | None = None,
    metadata_override: dict[str, Any] | None = None,
    decision_text_override: str | None = None,
) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, gate: str, code: str) -> None:
        if not condition:
            errors.append(f"{gate}:{code}")

    overlay = overlay_override if overlay_override is not None else load(root / OVERLAY_REL)
    contract = contract_override if contract_override is not None else load(root / CONTRACT_REL)
    hir = hir_schema_override if hir_schema_override is not None else load(root / HIR_SCHEMA_REL)
    mir = mir_schema_override if mir_schema_override is not None else load(root / MIR_SCHEMA_REL)
    lowering = lowering_registry_override if lowering_registry_override is not None else load(root / LOWERING_REL)
    machine = machine_registry_override if machine_registry_override is not None else load(root / MACHINE_REL)
    rows = rows_override if rows_override is not None else load(root / ROWS_REL)
    metadata = metadata_override if metadata_override is not None else load(root / META_REL)
    decision = decision_text_override if decision_text_override is not None else (root / DECISION_REL).read_text(encoding="utf-8")

    # G01: exact local identity and bounded one-cell scope.
    require(overlay.get("canonical_baseline_commit") == CANONICAL, "G01", "CANONICAL")
    require(overlay.get("local_predecessor_commit") == PREDECESSOR, "G01", "PREDECESSOR")
    require(overlay.get("revision") == OVERLAY_REVISION, "G01", "REVISION")
    require(overlay.get("feature_ids") == [FEATURE], "G01", "FEATURE")
    require(all(value in decision for value in (CANONICAL, PREDECESSOR, "IR-XCUT-P1-054", "exactly one implementation-target trace cell")), "G01", "DECISION_SCOPE")

    # G02: predecessor was exactly one blocked dynamic cell.
    bindings = overlay.get("bindings", [])
    binding = bindings[0] if len(bindings) == 1 else {}
    require(
        binding.get("feature_id") == FEATURE
        and binding.get("stage") == "DYNAMIC_LOWERING"
        and binding.get("outcome") is None
        and binding.get("predecessor_disposition") == "APPLICABLE_BLOCKED_BY_GAP"
        and binding.get("disposition") == "BOUND_DIRECT",
        "G02", "BLOCKED_TO_DIRECT",
    )
    require("IR-XCUT-P1-054" in decision and "APPLICABLE_BLOCKED_BY_GAP" in decision, "G02", "PREDECESSOR_GAP")

    # G03: R30 owns six independent identities and exact 15-field residues.
    residue = contract.get("evidence_residue", {})
    identities = contract.get("identities", [])
    require([row.get("identity_id") for row in identities] == IDENTITIES, "G03", "IDENTITIES_EXACT_6")
    require(residue.get("hir_exact_fields") == R30_HIR_FIELDS, "G03", "HIR_FIELDS_15")
    require(residue.get("mir_exact_fields") == R30_MIR_FIELDS, "G03", "MIR_FIELDS_15")
    require(all(row.get("runtime_relookup_count") == 0 for row in identities), "G03", "IDENTITY_RELOOKUP_ZERO")
    require(residue.get("clone_runtime_relookup_count") == residue.get("deep_clone_runtime_relookup_count") == 0, "G03", "BEHAVIOR_RELOOKUP_ZERO")
    require(contract.get("axis_model", {}).get("identity_count") == contract.get("axis_model", {}).get("axis_count") == 6, "G03", "SIX_INDEPENDENT_AXES")

    # G04: canonical HIR uses one closed non-structural 15-field descriptor.
    hdef = hir.get("$defs", {}).get("ResponsibilityEvidenceDescriptor", {})
    htable = hir.get("$defs", {}).get("CanonicalModuleBase", {}).get("properties", {}).get("responsibility_evidence_descriptors", {})
    require(hdef.get("required") == HIR_FIELDS and hdef.get("additionalProperties") is False, "G04", "HIR_DESCRIPTOR")
    require(set(hdef.get("properties", {})) == set(HIR_FIELDS), "G04", "HIR_PROPERTIES")
    require(htable.get("items", {}).get("$ref") == "#/$defs/ResponsibilityEvidenceDescriptor" and htable.get("uniqueItems") is True, "G04", "HIR_TABLE")
    require("does not add a HIR node identity" in hdef.get("description", ""), "G04", "HIR_NON_STRUCTURAL")

    # G05: MIR and the lowering/machine contracts preserve the same proof directly.
    mdef = mir.get("$defs", {}).get("responsibilityEvidenceDescriptor", {})
    mtable = mir.get("properties", {}).get("responsibility_evidence_table", {})
    projection = lowering.get("profile_contract", {}).get("responsibility_evidence_projection_contract", {})
    machine_projection = machine.get("responsibility_evidence_projection_contract", {})
    identity_rule = machine.get("closed_static_identity_contract", {}).get("responsibility_identity_rule", "")
    require(mdef.get("required") == MIR_FIELDS and mdef.get("additionalProperties") is False, "G05", "MIR_DESCRIPTOR")
    require(mtable.get("items", {}).get("$ref") == "#/$defs/responsibilityEvidenceDescriptor", "G05", "MIR_TABLE")
    require(projection.get("hir_to_mir_field_relation") == "EXACT_EXCEPT_SOURCE_PROVENANCE_PROJECTS_TO_SOURCE_ORIGIN_ID", "G05", "LOWERING_RELATION")
    require(projection.get("runtime_relookup_count") == projection.get("backend_relookup_count") == 0, "G05", "LOWERING_RELOOKUP_ZERO")
    require(machine_projection.get("descriptor_exact_fields") == MIR_FIELDS, "G05", "MACHINE_FIELDS")
    require(machine_projection.get("runtime_relookup_count") == machine_projection.get("backend_relookup_count") == 0, "G05", "MACHINE_RELOOKUP_ZERO")
    require("RESPONSIBILITY_RULE stores canonical ResponsibilityRuleId" in identity_rule and "runtime or backend relookup is forbidden" in identity_rule, "G05", "MACHINE_IDENTITY_RULE")

    # G06: overlay is exactly one direct, nondelegated binding and one record.
    entries = overlay.get("evidence_entries", [])
    entry = entries[0] if len(entries) == 1 else {}
    require(len(entries) == len(bindings) == len(overlay.get("acceptance_cases", [])) == 1, "G06", "ONE_ONE_ONE")
    require(entry == {
        "evidence_key": EVIDENCE_KEY, "class": "ARTIFACT_POINTER", "path": LOWERING_REL,
        "locator_kind": "JSON_POINTER", "locator": "/profile_contract/responsibility_evidence_projection_contract",
        "stage_role": "DYNAMIC_LOWERING",
    }, "G06", "ENTRY_EXACT")
    require(binding.get("evidence_keys") == [EVIDENCE_KEY] and binding.get("delegate_feature_id") is None and binding.get("not_applicable") is None, "G06", "DIRECT_ONLY")

    # G07: generated ledger changes only the target and has exact totals.
    cells, duplicates = trace_cells(rows)
    target = cells.get(TARGET, {})
    expected_ref = evidence_id(entry) if entry else ""
    count, digest = non_target_digest(cells)
    derived = metadata.get("derived_counts", {})
    overlays = metadata.get("applied_evidence_overlays", [])
    require(len(rows) == 469 and len(cells) == 4221 and duplicates == 0, "G07", "LEDGER_SHAPE")
    require(target == {"stage": "DYNAMIC_LOWERING", "disposition": "BOUND_DIRECT", "evidence_refs": [expected_ref], "delegate_feature_id": None, "not_applicable": None, "blocked_gap_ids": []}, "G07", "TARGET_EXACT")
    require(count == 4220 and digest == NON_TARGET_SHA256, "G07", "OTHER_4220_EXACT")
    require((derived.get("bound_direct_cells"), derived.get("bound_delegated_cells"), derived.get("not_applicable_cells"), derived.get("applicable_blocked_cells")) == (2464, 3, 501, 1253), "G07", "COUNTS")
    require(len(overlays) == 12 and sum(row.get("binding_count", 0) for row in overlays) == 128 and len(metadata.get("evidence_registry", [])) == 3141, "G07", "OVERLAY_COUNTS")

    # G08: all controlling canonical inputs remain byte-identical.
    override_paths = {
        CONTRACT_REL: contract_override, HIR_SCHEMA_REL: hir_schema_override,
        MIR_SCHEMA_REL: mir_schema_override, LOWERING_REL: lowering_registry_override,
        MACHINE_REL: machine_registry_override,
    }
    for relative, expected in PROTECTED.items():
        if override_paths.get(relative) is None:
            require(sha256(root / relative) == expected, "G08", f"HASH:{relative}")

    # G09: schema, paths, governance, and evidence honesty remain closed.
    schema = load(root / OVERLAY_SCHEMA_REL)
    require(schema.get("properties", {}).get("revision", {}).get("const") == OVERLAY_REVISION, "G09", "SCHEMA_REVISION")
    require(all((root / path).is_file() for path in (DECISION_REL, OVERLAY_REL, OVERLAY_SCHEMA_REL, VALIDATOR_REL)), "G09", "PATHS")
    guards = overlay.get("guards", {})
    governance = metadata.get("governance", {})
    require(guards.get("semantic_p0") == governance.get("semantic_p0") == 0, "G09", "P0_ZERO")
    require(guards.get("feature_p1") == governance.get("feature_p1") == "22_OPEN_UNCHANGED", "G09", "P1_22")
    require(guards.get("m13_actions") == governance.get("m13_actions") == "4_OPEN_UNCHANGED", "G09", "M13_4")
    require(guards.get("product_lanes") == governance.get("product_lanes") == "15_OF_15_NOT_RUN", "G09", "PRODUCT_NOT_RUN")
    require(guards.get("github_publication") == governance.get("github_publication") == "SUSPENDED", "G09", "GITHUB_SUSPENDED")
    require(all(guards.get(key) == 0 for key in ("surface_change_count", "ast_identity_change_count", "hir_identity_change_count", "mir_operation_kind_change_count", "runtime_relookup_count", "backend_relookup_count", "product_execution_receipt_count")), "G09", "NO_EXPANSION")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    gates = []
    for gate_id, name in GATES.items():
        gate_errors = [item for item in errors if item.startswith(f"{gate_id}:")]
        gates.append({"gate_id": gate_id, "name": name, "result": "PASS" if not gate_errors else "FAIL", "errors": gate_errors})
    passed = sum(row["result"] == "PASS" for row in gates)
    receipt = {
        "schema": "deeplus.responsibility-identity-dynamic-trace-validation-receipt/r1",
        "revision": OVERLAY_REVISION,
        "canonical_baseline_commit": CANONICAL,
        "local_predecessor_commit": PREDECESSOR,
        "result": "PASS" if not errors else "FAIL",
        "gate_count": 9,
        "passed_gate_count": passed,
        "gate_summary": f"{passed}/9",
        "feature_id": FEATURE,
        "transitioned_cell_count": 1,
        "unchanged_non_target_cell_count": 4220,
        "projected_counts": {"bound_direct": 2464, "bound_delegated": 3, "not_applicable": 501, "applicable_blocked": 1253},
        "product_execution": "15_OF_15_NOT_RUN",
        "github_publication": "SUSPENDED",
        "gates": gates,
        "errors": errors,
    }
    print(json.dumps(receipt, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
