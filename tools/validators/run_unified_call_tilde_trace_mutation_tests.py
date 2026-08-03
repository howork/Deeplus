#!/usr/bin/env python3
"""Run bounded in-memory mutations against the R57 focused validator."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

from validate_unified_call_tilde_trace import CONTRACT_REL, OVERLAY_REL, load, validate


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    overlay = load(ROOT / OVERLAY_REL)
    contract = load(ROOT / CONTRACT_REL)
    trace_rows = load(ROOT / "spec/traceability/implementation-target-profile-r1/rows.json")
    lowering = load(ROOT / "spec/contracts/hir-mir-lowering-registry.json")
    hm_row = next(row for row in lowering["rows"] if row["row_id"] == "HM-LR-CALL-010")
    mutations = []

    def add(name, change):
        mutations.append((name, change))

    add("feature omission", lambda o, c, t, h: o["feature_ids"].pop())
    add("extra feature", lambda o, c, t, h: o["feature_ids"].append("actor_mailbox_capacity"))
    add("binding omission", lambda o, c, t, h: o["bindings"].pop())
    add("binding stage drift", lambda o, c, t, h: o["bindings"][0].__setitem__("stage", "STATIC_SEMANTICS"))
    add("delegate removed", lambda o, c, t, h: next(item for item in o["bindings"] if item["disposition"] == "BOUND_DELEGATED").__setitem__("delegate_feature_id", None))
    add("delegate disposition drift", lambda o, c, t, h: next(item for item in o["bindings"] if item["disposition"] == "BOUND_DELEGATED").__setitem__("disposition", "BOUND_DIRECT"))
    add("evidence locator drift", lambda o, c, t, h: o["evidence_entries"][0].__setitem__("locator", "/missing"))
    add("call mode drift", lambda o, c, t, h: c["surface_and_ast"]["call_modes"].pop())
    add("ast argument kind drift", lambda o, c, t, h: c["surface_and_ast"]["ast_argument_kinds"].append("TRAILING_CLOSURE"))
    add("hir argument kind drift", lambda o, c, t, h: c["surface_and_ast"]["hir_argument_kinds"].pop())
    add("payload aggregate enabled", lambda o, c, t, h: c["surface_and_ast"].__setitem__("message_payload_node_count", 1))
    add("pratt rank drift", lambda o, c, t, h: c["pratt_contract"].__setitem__("rank", 16))
    add("actor associativity drift", lambda o, c, t, h: c["pratt_contract"].__setitem__("actor_message_associativity", "LEFT"))
    add("actor fallback enabled", lambda o, c, t, h: c["static_semantics"].__setitem__("actor_to_ordinary_fallback_count", 1))
    add("mode target pair omission", lambda o, c, t, h: c["hir_lowering"]["valid_mode_target_pairs"].pop())
    add("implicit actor suspension", lambda o, c, t, h: c["actor_transport"].__setitem__("implicit_suspend_count", 1))
    add("unconditional reply token", lambda o, c, t, h: c["actor_transport"].__setitem__("lowering_row_reply_token_count", 1))
    add("acceptance execution overclaim", lambda o, c, t, h: c["acceptance_cases"][0].__setitem__("execution_state", "PASS"))
    add("p1 drift", lambda o, c, t, h: c["authority_fence"].__setitem__("feature_p1", "21_OPEN"))
    add("github drift", lambda o, c, t, h: c["authority_fence"].__setitem__("github_publication", "AUTHORIZED"))
    add("trace delegation drift", lambda o, c, t, h: next(row for row in t if row["feature_id"] == "actor_declaration_grammar_closed")["stages"][-1]["outcomes"][2].__setitem__("delegate_feature_id", None))
    add("hm010 suspend drift", lambda o, c, t, h: h.__setitem__("suspension_effect", "MAY_SUSPEND"))
    add("hm010 reply drift", lambda o, c, t, h: h["token_outputs"].append({"token_kind": "REPLY", "token_role": "actor_reply_correlation", "cardinality": 1}))

    rejected = 0
    for name, change in mutations:
        o = copy.deepcopy(overlay)
        c = copy.deepcopy(contract)
        t = copy.deepcopy(trace_rows)
        h = copy.deepcopy(hm_row)
        change(o, c, t, h)
        errors = validate(ROOT, o, c, validate_schema=False, trace_rows_override=t, hm_row_override=h)
        if errors:
            rejected += 1
        else:
            print(f"MUTATION_NOT_REJECTED:{name}")
    if rejected != len(mutations):
        print(f"R57_UNIFIED_CALL_TILDE_MUTATIONS: FAIL ({rejected}/{len(mutations)})")
        return 1
    print(f"R57_UNIFIED_CALL_TILDE_MUTATIONS: PASS ({rejected}/{len(mutations)} rejected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
