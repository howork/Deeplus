from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS = [
    "ACTOR_PROTOCOL_TARGET_KIND_MISMATCH",
    "ACTOR_PROTOCOL_CONFORMANCE_REQUIRED",
    "ACTOR_PROTOCOL_CONFORM_BLOCK_OWNER_MISMATCH",
    "ACTOR_PROTOCOL_SEND_THROWS_FORBIDDEN",
    "ACTOR_PROTOCOL_REQUIREMENT_DUPLICATE",
    "ACTOR_PROTOCOL_REQUIREMENT_UNIMPLEMENTED",
    "ACTOR_PROTOCOL_IMPLEMENTATION_KIND_MISMATCH",
    "ACTOR_PROTOCOL_SIGNATURE_MISMATCH",
    "ACTOR_PROTOCOL_IMPLEMENTATION_AMBIGUOUS",
]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def path_sha256(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def validate_descriptor_shape(descriptor: dict) -> None:
    require(
        set(descriptor)
        == {
            "schema",
            "actor_id",
            "protocol_id",
            "target_kind",
            "route",
            "header_relation_count",
            "matching_block_count",
            "requirements",
            "implementations",
            "selection",
            "order_evidence",
        },
        "descriptor closed top-level shape",
    )
    require(
        descriptor["schema"]
        == "deeplus.actor-protocol-direct-conformance-descriptor/r1",
        "descriptor schema tag",
    )
    require(
        isinstance(descriptor["actor_id"], str)
        and bool(descriptor["actor_id"])
        and isinstance(descriptor["protocol_id"], str)
        and bool(descriptor["protocol_id"]),
        "descriptor owner identities",
    )
    require(
        descriptor["target_kind"] in {"ACTOR_PROTOCOL", "TRAIT", "OTHER"}
        and descriptor["route"] in {"DIRECT", "VIA", "AUTO", "EXTERNAL", "RUNTIME"},
        "descriptor closed enums",
    )
    require(
        isinstance(descriptor["header_relation_count"], int)
        and descriptor["header_relation_count"] >= 0
        and isinstance(descriptor["matching_block_count"], int)
        and descriptor["matching_block_count"] >= 0,
        "descriptor cardinalities",
    )
    parameter_keys = {"ordinal", "label_or_null", "type_id", "transfer_mode"}
    requirement_keys = {
        "requirement_id",
        "origin_protocol_id",
        "kind",
        "selector",
        "parameters",
        "result_type_or_null",
        "normalized_error_set",
        "normalized_effect_row",
    }
    implementation_keys = {
        "implementation_id",
        "block_protocol_id",
        "kind",
        "selector",
        "parameters",
        "result_type_or_null",
        "normalized_error_set",
        "normalized_effect_row",
    }
    for collection, keys, kinds in (
        (descriptor["requirements"], requirement_keys, {"SEND", "REQUEST"}),
        (descriptor["implementations"], implementation_keys, {"ON", "REQUEST"}),
    ):
        require(isinstance(collection, list), "descriptor item collection")
        for item in collection:
            require(isinstance(item, dict) and set(item) == keys, "descriptor item shape")
            require(item["kind"] in kinds, "descriptor item kind")
            require(isinstance(item["parameters"], list), "descriptor parameters")
            for parameter in item["parameters"]:
                require(
                    isinstance(parameter, dict)
                    and set(parameter) == parameter_keys
                    and isinstance(parameter["ordinal"], int)
                    and parameter["ordinal"] >= 0
                    and parameter["transfer_mode"] in {"REUSABLE", "MOVE", "SHARED"},
                    "descriptor parameter shape",
                )
            require(
                isinstance(item["normalized_error_set"], list)
                and len(item["normalized_error_set"])
                == len(set(item["normalized_error_set"]))
                and isinstance(item["normalized_effect_row"], list)
                and len(item["normalized_effect_row"])
                == len(set(item["normalized_effect_row"])),
                "descriptor normalized rows",
            )
    selection = descriptor["selection"]
    require(
        isinstance(selection, dict)
        and set(selection)
        == {"qualification_protocol_id_or_null", "visible_binding_ids"}
        and isinstance(selection["visible_binding_ids"], list)
        and len(selection["visible_binding_ids"])
        == len(set(selection["visible_binding_ids"])),
        "descriptor selection shape",
    )
    require(
        descriptor["order_evidence"]
        == {
            "source_order_winner_count": 0,
            "import_order_winner_count": 0,
            "runtime_lookup_count": 0,
        },
        "descriptor order evidence shape",
    )


def compatible(requirement: dict, implementation: dict) -> bool:
    if requirement["parameters"] != implementation["parameters"]:
        return False
    if requirement["result_type_or_null"] != implementation["result_type_or_null"]:
        return False
    if not set(implementation["normalized_error_set"]) <= set(requirement["normalized_error_set"]):
        return False
    if not set(implementation["normalized_effect_row"]) <= set(requirement["normalized_effect_row"]):
        return False
    return True


def evaluate(descriptor: dict) -> str:
    if descriptor["target_kind"] != "ACTOR_PROTOCOL" or descriptor["route"] != "DIRECT":
        return "ACTOR_PROTOCOL_TARGET_KIND_MISMATCH"
    headers = descriptor["header_relation_count"]
    blocks = descriptor["matching_block_count"]
    if headers == 0 and blocks == 0:
        return "ACTOR_PROTOCOL_CONFORMANCE_REQUIRED"
    if headers == 0 and blocks > 0:
        return "ACTOR_PROTOCOL_CONFORM_BLOCK_OWNER_MISMATCH"
    if headers > 1 or blocks > 1:
        return "ACTOR_PROTOCOL_REQUIREMENT_DUPLICATE"
    if headers != 1 or blocks != 1:
        return "ACTOR_PROTOCOL_REQUIREMENT_UNIMPLEMENTED"

    requirements = descriptor["requirements"]
    implementations = descriptor["implementations"]
    for item in requirements:
        if item["kind"] == "SEND" and item["normalized_error_set"]:
            return "ACTOR_PROTOCOL_SEND_THROWS_FORBIDDEN"
    for item in implementations:
        if item["kind"] == "ON" and item["normalized_error_set"]:
            return "ACTOR_PROTOCOL_SEND_THROWS_FORBIDDEN"

    for req in sorted(requirements, key=lambda row: row["requirement_id"]):
        candidates = [
            impl for impl in implementations
            if impl["block_protocol_id"] == descriptor["protocol_id"]
            and impl["selector"] == req["selector"]
        ]
        if len(candidates) > 1:
            return "ACTOR_PROTOCOL_REQUIREMENT_DUPLICATE"
        if not candidates:
            return "ACTOR_PROTOCOL_REQUIREMENT_UNIMPLEMENTED"
        impl = candidates[0]
        expected_kind = "ON" if req["kind"] == "SEND" else "REQUEST"
        if impl["kind"] != expected_kind:
            return "ACTOR_PROTOCOL_IMPLEMENTATION_KIND_MISMATCH"
        if not compatible(req, impl):
            return "ACTOR_PROTOCOL_SIGNATURE_MISMATCH"

    if len(descriptor["selection"]["visible_binding_ids"]) > 1:
        return "ACTOR_PROTOCOL_IMPLEMENTATION_AMBIGUOUS"
    order = descriptor["order_evidence"]
    require(order == {
        "source_order_winner_count": 0,
        "import_order_winner_count": 0,
        "runtime_lookup_count": 0,
    }, "order evidence must be zero")
    return "ADMIT"


def binding_digest(descriptor: dict) -> str:
    projection = {
        "actor_id": descriptor["actor_id"],
        "protocol_id": descriptor["protocol_id"],
        "requirements": sorted(descriptor["requirements"], key=lambda row: row["requirement_id"]),
        "implementations": sorted(descriptor["implementations"], key=lambda row: row["implementation_id"]),
    }
    data = json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def main(root: Path = ROOT) -> None:
    global ROOT
    ROOT = root.resolve()
    contract = load("spec/contracts/actor-protocol-direct-conformance-r1.json")
    fixture = load("tests/fixtures/current/actor-protocol-direct-conformance-r1.json")
    schema = load("schemas/language/actor-protocol-direct-conformance-descriptor.schema.json")
    frontend = load("spec/frontend/frontend-model.json")
    actor = load("spec/contracts/actor-concurrency-coherence.json")
    predicates = load("spec/types/predicates/chunks/part-0001.json")
    predicate_fixtures = load("tests/conformance/checker-predicates/chunks/part-0001.json")
    predicate_fixtures += load("tests/conformance/checker-predicates/chunks/part-0031.json")
    diagnostic_rows = []
    for path in sorted((ROOT / "spec/diagnostics/catalog/chunks").glob("part-*.json")):
        diagnostic_rows.extend(json.loads(path.read_text(encoding="utf-8")))
    diagnostic_rows = [
        row for row in diagnostic_rows if row.get("diagnostic_id") in DIAGNOSTICS
    ]
    relations = []
    for path in sorted((ROOT / "spec/diagnostics/relations/chunks").glob("part-*.json")):
        relations.extend(json.loads(path.read_text(encoding="utf-8")))
    relations = [
        row for row in relations if row.get("predicate_id") == "ActorProtocolGateAdmitted"
    ]
    feature_rows = load("spec/features/catalog/chunks/part-0001.json")
    bridge = load("spec/contracts/hir-h1-current-mir-bridge.json")
    lowering = load("spec/contracts/hir-mir-lowering-registry.json")
    hir_schema = load("schemas/language/canonical-hir-h1.schema.json")
    lowering_row_schema = load("schemas/language/hir-mir-lowering-row.schema.json")
    grammar = (ROOT / "spec/grammar/deeplus.ebnf").read_text(encoding="utf-8")
    language = (ROOT / "spec/language.md").read_text(encoding="utf-8")
    type_system = (ROOT / "spec/types/type-system.md").read_text(encoding="utf-8")
    mir_semantics = (ROOT / "spec/mir/semantics.md").read_text(encoding="utf-8")
    passed = []

    require(schema["$id"].endswith("actor-protocol-direct-conformance-descriptor-r1.json"), "schema identity")
    require(contract["revision"] == "R41-REBASED-DESIGN-R1", "R41 contract revision")
    require(
        contract["authority"]["baseline_commit"]
        == "b6ff0f80d74e93bc7b25c54cfde08f8b40ca54e3"
        and contract["authority"]["baseline_tree"]
        == "6ffe1dccce5e8557244b316f129f9ddc9634c1c2"
        and contract["authority"]["predecessor_candidate_commit"]
        == "2e511cede2e1bfca4a60aa124fc55b650f68ba30",
        "R41 authority baseline",
    )
    for binding_name, path in (
        ("descriptor_schema", "schemas/language/actor-protocol-direct-conformance-descriptor.schema.json"),
        ("fixture", "tests/fixtures/current/actor-protocol-direct-conformance-r1.json"),
    ):
        binding = contract["artifact_binding"][binding_name]
        require(
            binding["path"] == path
            and binding["bytes"] == (ROOT / path).stat().st_size
            and binding["sha256"] == path_sha256(path),
            f"artifact binding {binding_name}",
        )
    require(contract["status"] == "CURRENT_STABLE_DESIGN_CONTRACT", "contract status")
    require(contract["product_lanes"] == "15/15_NOT_RUN", "contract product lanes")
    require(contract["surface"]["route"] == "DIRECT", "direct-only route")
    require(contract["surface"]["handler_mapping"] == {"SEND": "ON", "REQUEST": "REQUEST"}, "handler mapping")
    require(contract["algorithm"]["candidate_cardinality"] == "EXACTLY_ONE", "candidate cardinality")
    require(contract["algorithm"]["fallback_count"] == 0, "fallback")
    require(contract["algorithm"]["source_order_winner_count"] == 0, "source order")
    require(contract["algorithm"]["runtime_lookup_count"] == 0, "runtime lookup")
    require(contract["diagnostic_precedence"] == DIAGNOSTICS, "diagnostic order")
    passed.append("contract and schema")

    require("ActorProtocolConformanceClause* ActorBody" in grammar, "Actor header grammar")
    require("ActorProtocolConformBlock" in grammar, "Actor block grammar")
    actor_item = grammar.split("ActorItem ::=", 1)[1].split("ActorOnDecl ::=", 1)[0]
    require("| MemberDecl" not in actor_item and "::= MemberDecl" not in actor_item, "generic MemberDecl excluded from ActorItem")
    require("ActorMemberDecl" in actor_item and "ConformBlockDecl" not in actor_item, "Trait block leak closed")
    require("ActorProtocolConformanceItem ::= ActorOnDecl | ActorRequestDecl" in grammar, "block item closure")
    passed.append("root-connected grammar and leak closure")

    concurrency = frontend["concurrency_frontend_contract"]
    for name in ["ActorProtocolConformanceId", "ActorProtocolRequirementId", "ActorProtocolBindingId"]:
        require(name in concurrency["typed_hir_identities"], f"frontend identity {name}")
    require(concurrency["actor_protocol_direct_conformance"]["one_way_normalized_error_set"] == [], "frontend send ErrorSet")
    require(concurrency["actor_protocol_direct_conformance"]["product_support"] == "NOT_RUN", "frontend product fence")
    passed.append("frontend identity residue")

    rule = next(row for row in actor["rules"] if row["rule_id"] == "ACC-R019")
    require(rule["contract"]["candidate_cardinality"] == "EXACTLY_ONE", "actor rule cardinality")
    gate = next(row for row in actor["unclosed_product_gates"] if row["gate_id"] == "ACC-G002")
    require(
        gate["design_contract_status"]
        == "SATISFIED_BY_R41_REBASED_DIRECT_CONFORMANCE",
        "ACC-G002 R41 rebased design status",
    )
    require(gate["status"] == "BLOCKS_PRODUCT_EXECUTION", "ACC-G002 product fence")
    rule_ids = [row["rule_id"] for row in actor["rules"]]
    require(
        actor["machine_acceptance"]["rule_count"] == len(actor["rules"])
        and rule_ids
        in (
            [f"ACC-R{i:03d}" for i in range(1, 20)],
            [f"ACC-R{i:03d}" for i in range(1, 21)],
        ),
        "actor rule set must be exact R41 or R41+R22",
    )
    passed.append("actor coherence binding")

    predicate = next(row for row in predicates if row["predicate_id"] == "ActorProtocolGateAdmitted")
    require(predicate["predicate_maturity"] == "design_algorithm" and predicate["emission_eligible"], "predicate maturity")
    require(predicate["input_descriptor_schema"] == "schemas/language/actor-protocol-direct-conformance-descriptor.schema.json", "predicate schema")
    require(predicate["active_primary_diagnostic"] == DIAGNOSTICS[0], "predicate primary")
    require(predicate["secondary_diagnostics"] == DIAGNOSTICS[1:], "predicate secondary")
    actor_predicate_fixtures = [row for row in predicate_fixtures if row["predicate_id"] == "ActorProtocolGateAdmitted"]
    require(len(actor_predicate_fixtures) == 11, "predicate fixture count")
    for row in actor_predicate_fixtures:
        validate_descriptor_shape(row["descriptor"])
        outcome = evaluate(row["descriptor"])
        expected = "ADMIT" if row["expected"] == "admitted" else row["expected_primary_diagnostic"]
        require(outcome == expected, f"fixture oracle {row['fixture_id']}: {outcome} != {expected}")
    passed.append("11 predicate fixture oracles")

    require([row["diagnostic_id"] for row in diagnostic_rows] == DIAGNOSTICS, "diagnostic catalog rows")
    require(len(relations) == 9 and relations[0]["relation"] == "primary", "diagnostic relations")
    require(all(row["predicate_id"] == "ActorProtocolGateAdmitted" for row in relations), "relation predicate binding")
    feature = next(row for row in feature_rows if row["feature_id"] == "actor_protocol_family")
    require(set(DIAGNOSTICS) <= set(feature["normative_trace_refs"]["diagnostics"]), "feature diagnostic trace")
    require("ActorProtocolConformBlock" in feature["normative_trace_refs"]["productions"], "feature grammar trace")
    passed.append("diagnostic and feature trace")

    actor_identities = [
        "ActorProtocolConformanceId",
        "ActorProtocolRequirementId",
        "ActorProtocolBindingId",
        "ActorHandlerId",
        "ActorRequestId",
    ]
    for identity in actor_identities:
        require(identity in bridge["canonical_hir_contract"]["selected_identity_domains"], f"HIR selected identity {identity}")
    required_fields = bridge["call_plan_contract"]["actor_transport_required_fields"]
    for field in ["actor_protocol_conformance_id", "actor_protocol_requirement_id", "actor_protocol_binding_id", "actor_handler_or_request_id"]:
        require(field in required_fields, f"actor transport field {field}")
    call_plan = hir_schema["$defs"]["CallPlan"]
    actor_fields = set(required_fields)
    require(actor_fields <= set(call_plan["properties"]), "HIR actor transport properties")
    actor_branch = next(
        branch
        for branch in call_plan["allOf"]
        if branch.get("if", {})
        .get("properties", {})
        .get("mode_target_pair", {})
        .get("const")
        == "ACTOR_MESSAGE::ACTOR_TRANSPORT"
    )
    require(
        actor_branch["if"]["properties"]["mode_target_pair"]["const"]
        == "ACTOR_MESSAGE::ACTOR_TRANSPORT",
        "HIR actor transport discriminator",
    )
    require(set(actor_branch["then"]["required"]) == actor_fields, "HIR actor field totality")
    forbidden_non_actor = {
        row["required"][0]
        for row in actor_branch["else"]["not"]["anyOf"]
    }
    require(forbidden_non_actor == actor_fields, "HIR non-actor residue fence")
    row = next(item for item in lowering["rows"] if item["row_id"] == "HM-LR-CALL-010")
    inputs = row["operation_plan"][0]["input_roles"]
    for field in ["actor_protocol_conformance_id", "actor_protocol_requirement_id", "actor_protocol_binding_id", "actor_handler_or_request_id"]:
        require(field in inputs, f"lowering input {field}")
    expected_projection = {
        "binding_cardinality": "EXACTLY_ONE",
        "source_or_import_order_winner_count": 0,
        "mir_selector_lookup_count": 0,
        "runtime_lookup_count": 0,
    }
    require(row["actor_protocol_binding_projection"] == expected_projection, "MIR binding projection")
    identity_by_operation = {"SEND": "ActorHandlerId", "REQUEST": "ActorRequestId"}
    bridge_binding = bridge["actor_protocol_direct_conformance_bridge"]
    lowering_binding = lowering["actor_protocol_binding_contract"]
    contract_sha256 = path_sha256("spec/contracts/actor-protocol-direct-conformance-r1.json")
    for binding in (bridge_binding, lowering_binding):
        require(binding["contract_sha256"] == contract_sha256, "actor contract digest binding")
        require(
            binding["descriptor_schema_sha256"]
            == path_sha256("schemas/language/actor-protocol-direct-conformance-descriptor.schema.json")
            and binding["fixture_sha256"]
            == path_sha256("tests/fixtures/current/actor-protocol-direct-conformance-r1.json"),
            "actor schema/fixture digest binding",
        )
        require(
            binding["implementation_identity_by_operation"] == identity_by_operation
            and binding["union_field_role"] == "actor_handler_or_request_id",
            "handler/request identity mapping",
        )
    require(bridge_binding["typed_hir_residue"] == actor_identities, "bridge typed identity set")
    require(lowering_binding["required_hir_identities"] == actor_identities, "lowering typed identity set")
    require(
        lowering["contract_bindings"]["lowering_row_schema"]["sha256"]
        == path_sha256("schemas/language/hir-mir-lowering-row.schema.json"),
        "lowering row schema digest",
    )
    actor_schema_branch = next(
        branch
        for branch in lowering_row_schema["allOf"]
        if branch.get("if", {}).get("properties", {}).get("row_id", {}).get("const")
        == "HM-LR-CALL-010"
    )
    require(
        actor_schema_branch["then"]["required"] == ["actor_protocol_binding_projection"]
        and actor_schema_branch["else"]["not"]["required"]
        == ["actor_protocol_binding_projection"],
        "lowering actor projection schema fence",
    )
    passed.append("HIR/MIR lowering residue")

    counts = Counter(row["category"] for row in fixture["cases"])
    require(counts == Counter({"negative": 15, "positive": 6, "boundary": 5}), "canonical case counts")
    require(len(fixture["cases"]) == 26 and len(fixture["mutation_controls"]) == 8, "canonical fixture totals")
    require(fixture["expected_counts"]["product_executed"] == 0, "fixture product fence")
    passed.append("26 cases and 8 mutation controls")

    positive = next(row["descriptor"] for row in actor_predicate_fixtures if row["fixture_id"] == "PF-ActorProtocolGateAdmitted-POS")
    mutations = []
    def mutate(label, expected, fn):
        value = copy.deepcopy(positive)
        fn(value)
        actual = evaluate(value)
        require(actual == expected, f"mutation {label}: {actual} != {expected}")
        mutations.append(label)

    mutate("target-kind", DIAGNOSTICS[0], lambda d: d.update(target_kind="TRAIT"))
    mutate("structural", DIAGNOSTICS[1], lambda d: d.update(header_relation_count=0, matching_block_count=0))
    mutate("orphan-block", DIAGNOSTICS[2], lambda d: d.update(header_relation_count=0, matching_block_count=1))
    mutate("send-error", DIAGNOSTICS[3], lambda d: d["requirements"][0]["normalized_error_set"].append("E"))
    mutate("duplicate", DIAGNOSTICS[4], lambda d: d["implementations"].append(copy.deepcopy(d["implementations"][0])))
    mutate("missing", DIAGNOSTICS[5], lambda d: d.update(implementations=[]))
    mutate("kind", DIAGNOSTICS[6], lambda d: d["implementations"][0].update(kind="REQUEST"))
    mutate("signature", DIAGNOSTICS[7], lambda d: d["implementations"][0]["parameters"].append({"ordinal": 0, "label_or_null": None, "type_id": "String", "transfer_mode": "REUSABLE"}))
    mutate("ambiguous", DIAGNOSTICS[8], lambda d: d["selection"].update(visible_binding_ids=["A::P::ping", "A::Q::ping"]))
    shuffled = copy.deepcopy(positive)
    shuffled["requirements"] = list(reversed(shuffled["requirements"]))
    shuffled["implementations"] = list(reversed(shuffled["implementations"]))
    require(binding_digest(positive) == binding_digest(shuffled), "order-invariant binding digest")
    passed.append("9 diagnostic mutations plus order permutation")

    for text, label in [
        (language, "language"),
        (type_system, "type system"),
        (mir_semantics, "MIR semantics"),
    ]:
        require("ActorProtocolBindingId" in text, f"{label} binding identity")
        require("request" in text and "Unit" in text, f"{label} acknowledged command")
    require(contract["authority"]["canonical_feature_p1"] == "22_OPEN_UNCHANGED", "feature P1 fence")
    require(contract["machine_acceptance"]["product_executed"] == 0, "contract product execution")
    passed.append("semantic text and governance fence")

    print(json.dumps({
        "result": "PASS",
        "checks": passed,
        "predicate_fixtures": len(actor_predicate_fixtures),
        "acceptance_cases": len(fixture["cases"]),
        "mutation_oracles": len(mutations) + 1,
        "diagnostics": len(DIAGNOSTICS),
        "product_support": "NOT_RUN",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    main(parser.parse_args().root)
