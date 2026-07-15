#!/usr/bin/env python3
"""Initialize bounded R1.1 memory capsules for the five mandatory Work roles."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROLES = {
    "Design_": ("design_release_steward", "Complete five-role migration review and publish the first current snapshot."),
    "Spec_": ("language_type_architect", "Verify stable-path authority, grammar, type, MIR, and source-shard parity."),
    "Impl_": ("compiler_runtime_lead", "Review crate boundaries and implement the first Rust lexer/parser vertical slice."),
    "Test_": ("conformance_quality_lead", "Independently verify migration closure and define executable M2 gates."),
    "Devel_": ("developer_experience_ecosystem_lead", "Review human navigation, examples, diagnostics, and Prelude usability."),
}


for prefix, (role_id, action) in ROLES.items():
    capsule = {
        "schema": "deeplus.role-memory-capsule/v1",
        "role": {"id": role_id, "prefix": prefix},
        "updated_at": "2026-07-15T00:00:00+09:00",
        "source_revision": "r51f3-migration-m1",
        "current_facts": [
            {
                "id": "ARCH-001",
                "statement": "Rust implements the frontend, HIR, MIR and xVM; Deeplus MIR is semantic authority; LLVM AOT precedes ORC JIT.",
                "authority": "current architecture decision",
                "source": "current/authority-map.yaml",
                "introduced": "r51f3-migration-m1",
                "review_after": None,
                "status": "current",
            },
            {
                "id": "EVID-001",
                "statement": "All product lanes remain NOT_RUN; scaffold and static validation are not product evidence.",
                "authority": "current implementation status",
                "source": "current/implementation-status.yaml",
                "introduced": "r51f3-migration-m1",
                "review_after": None,
                "status": "current",
            },
        ],
        "open_actions": [
            {
                "id": f"MIG-M1-{prefix.rstrip('_').upper()}-001",
                "priority": "P1",
                "summary": action,
                "owner": prefix,
                "acceptance_test": "Role report contains lane verdicts, evidence, an alternative, executable acceptance tests, and handoff.",
                "target": "migration M1 review window",
            }
        ],
        "watch_items": [
            {
                "id": "RISK-001",
                "statement": "Legacy filenames inside imported row provenance must resolve through migration/path-aliases.json and must not become new edit authorities.",
                "authority": "migration contract",
                "source": "migration/README.md",
                "introduced": "r51f3-migration-m1",
                "review_after": "first post-migration release",
                "status": "watch",
            }
        ],
        "recent_releases": [
            {
                "release": "r51f3-migration-m1",
                "verdict": "identity/path/configuration migration; product lanes NOT_RUN",
                "report": "Design_Deeplus_R51f3_to_Canonical_Workspace_Migration_Report_M1.md",
            }
        ],
    }
    path = ROOT / "roles/current-memory" / f"{prefix}Deeplus_Current_Memory.json"
    path.write_text(json.dumps(capsule, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"created {len(ROLES)} role memory capsules")

