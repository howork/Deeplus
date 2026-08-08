#!/usr/bin/env python3
"""Validate the canonical DPG against the R77 EBNF surface census.

This is a design/static differential validator for the handwritten-parser
contract.  It does not claim that a production Deeplus parser has executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


DPG_REL = "spec/grammar/deeplus.dpg"
CONTEXT_REL = "spec/grammar/deeplus.parser-contexts.json"
LEGACY_REL = "spec/grammar/deeplus.ebnf"
VOCAB_REL = "spec/grammar/keyword-vocabulary.json"
FRONTEND_REL = "spec/frontend/frontend-model.json"
DISPOSITION_REL = "spec/contracts/grammar-production-disposition-registry-r1.json"
CONTRACT_REL = "spec/contracts/parser-grammar-differential-r1.json"
FIXTURE_REL = "tests/fixtures/current/parser-grammar-differential-r1.json"

RULE_RE = re.compile(
    r"(?m)^([A-Za-z_][A-Za-z0-9_]*)(<[^>\r\n]+>)?\s*(?::=|\r?\n\s*:=)"
)
LEGACY_PRODUCTION_RE = re.compile(
    r"(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*::="
)


class ValidationError(RuntimeError):
    pass


def require(condition: bool, code: str, detail: object = "") -> None:
    if not condition:
        raise ValidationError(f"{code}: {detail}")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "DPG_JSON_ROOT", path)
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_dpg_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"(?m)^\s*#.*$", "", text)


def rule_clauses(text: str) -> list[dict[str, str]]:
    clean = strip_dpg_comments(text)
    matches = list(RULE_RE.finditer(clean))
    rows: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(clean)
        tail = clean[match.end() : stop]
        quote = False
        escaped = False
        end = None
        for offset, char in enumerate(tail):
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "'":
                    quote = False
                continue
            if char == "'":
                quote = True
            elif char == ";":
                end = offset
                break
        require(end is not None, "DPG_RULE_TERMINATOR", match.group(1))
        rows.append(
            {
                "key": match.group(1) + (match.group(2) or ""),
                "family": match.group(1),
                "rhs": tail[:end].strip(),
            }
        )
    keys = [row["key"] for row in rows]
    require(len(keys) == len(set(keys)), "DPG_DUPLICATE_RULE_CLAUSE", keys)
    return rows


def json_pointer(document: Any, pointer: str) -> Any:
    require(pointer.startswith("#/"), "DPG_JSON_POINTER", pointer)
    value = document
    for encoded in pointer[2:].split("/"):
        key = encoded.replace("~1", "/").replace("~0", "~")
        require(isinstance(value, dict) and key in value, "DPG_JSON_POINTER", pointer)
        value = value[key]
    return value


def resolve_binding(root: Path, contexts: dict[str, Any], binding: str) -> Any:
    if binding.startswith("#/"):
        return json_pointer(contexts, binding)
    require("#/" in binding, "DPG_EXTERNAL_BINDING", binding)
    path_text, pointer_tail = binding.split("#/", 1)
    path = (root / path_text).resolve()
    require(path.is_file(), "DPG_EXTERNAL_BINDING_PATH", path_text)
    return json_pointer(read_json(path), "#/" + pointer_tail)


def nested_strings(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        result: set[str] = set()
        for item in value:
            result.update(nested_strings(item))
        return result
    return set()


def frontend_pratt_spellings(frontend: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for domain in ("expression", "type", "unit"):
        for row in frontend["pratt"][domain].get("operators", []):
            result.update(nested_strings(row.get("tokens", [])))
    return result


def validate_model(
    root: Path,
    dpg_text: str,
    contexts: dict[str, Any],
    frontend: dict[str, Any],
    disposition: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    rows = rule_clauses(dpg_text)
    families = {row["family"] for row in rows}
    clean = strip_dpg_comments(dpg_text)

    at_sets = set(re.findall(r"(?<!')@([A-Za-z_][A-Za-z0-9_]*)", clean))
    dispatches = set(re.findall(r"dispatch<([A-Za-z_][A-Za-z0-9_]*)", clean))
    admits = set(re.findall(r"admit<([A-Za-z_][A-Za-z0-9_]*)", clean))
    admits.discard("P")
    pratt = set(re.findall(r"pratt<([^>]+)>", clean))
    pratt.discard("D,M")

    bindings = contexts["closed_external_bindings"]
    require(at_sets <= set(contexts["surface_sets"]), "DPG_UNKNOWN_SURFACE_SET", sorted(at_sets - set(contexts["surface_sets"])))
    require(dispatches == set(bindings["dispatch_tables"]), "DPG_DISPATCH_TABLE_CLOSURE", sorted(dispatches ^ set(bindings["dispatch_tables"])))
    require(admits == set(bindings["admission_predicates"]), "DPG_ADMISSION_PREDICATE_CLOSURE", sorted(admits ^ set(bindings["admission_predicates"])))
    require(pratt == set(bindings["pratt_entries"]), "DPG_PRATT_ENTRY_CLOSURE", sorted(pratt ^ set(bindings["pratt_entries"])))

    for group in ("metanodes", "external_parser_slots", "admission_predicates", "pratt_entries"):
        for binding in bindings[group].values():
            resolve_binding(root, contexts, binding)
    for refs in bindings["dispatch_tables"].values():
        for binding in refs:
            resolve_binding(root, contexts, binding)

    member_parsers = contexts["parser_dispatch"]["member_parser_map"]
    member_items = set().union(*(set(v) for v in contexts["owner_member_sets"].values()))
    require(member_items == set(member_parsers), "DPG_MEMBER_DISPATCH_CLOSURE", sorted(member_items ^ set(member_parsers)))

    known_upper = (
        families
        | set(bindings["scanner_outcomes"])
        | set(bindings["external_parser_slots"])
        | set(bindings["metanodes"])
        | at_sets
        | dispatches
        | admits
        | {entry.split(",", 1)[0] for entry in pratt}
        | {"C", "M", "P", "R", "Role", "D"}
    )
    rhs_text = "\n".join(row["rhs"] for row in rows)
    rhs_unquoted = re.sub(r"'(?:\\.|[^'\\])*'", " ", rhs_text)
    unknown_upper = {
        name
        for name in re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", rhs_unquoted)
        if name not in known_upper
    }
    require(not unknown_upper, "DPG_UNBOUND_UPPER_SYMBOL", sorted(unknown_upper))

    legacy_text = (root / LEGACY_REL).read_text(encoding="utf-8")
    legacy_nonlex = legacy_text.split("COMMON STRUCTURAL SYNTAX", 1)[1]
    old_terminals = set(re.findall(r'"([^"\n]*)"', legacy_nonlex))
    dpg_literals = set(re.findall(r"'([^'\n]*)'", clean))
    dpg_contextual = set(re.findall(r"~([A-Za-z_][A-Za-z0-9_]*)", clean))
    represented = dpg_literals | dpg_contextual
    for values in contexts["surface_sets"].values():
        represented.update(nested_strings(values))
    represented.update(nested_strings(contexts["pratt_external_surface_words"]))
    represented.update(contexts["pratt_external_surface_operators_audit_only"])
    represented.update(frontend_pratt_spellings(frontend))
    missing_terminals = sorted(old_terminals - represented)
    require(not missing_terminals, "DPG_SURFACE_TERMINAL_LOSS", missing_terminals)

    legacy_names = LEGACY_PRODUCTION_RE.findall(legacy_text)
    require(len(legacy_names) == len(set(legacy_names)) == 656, "DPG_LEGACY_PRODUCTION_CENSUS", len(legacy_names))
    registry_rows = disposition.get("production_rows", [])
    registry_names = [row.get("production_id") for row in registry_rows]
    require(registry_names == legacy_names, "DPG_LEGACY_DISPOSITION_ORDER", len(registry_names))
    ast_domain = set(disposition["ast_schema"]["kind_domain"])
    ast_targets = {row["ast_target"] for row in registry_rows if row.get("ast_target") is not None}
    require(ast_targets <= ast_domain, "DPG_AST_TARGET_DOMAIN", sorted(ast_targets - ast_domain))

    require("Source<Role,preview>\n            := SourcePreamble<Role> PreviewGate" in dpg_text, "DPG_PREVIEW_GATE")
    require("DeferredReceiver '~' MessageSelector" in dpg_text and "DeferredReceiver ':~'" not in dpg_text, "DPG_DEFERRED_MESSAGE_FENCE")
    require("TildeCall   := ('~' | ':~') MessageSelector" in dpg_text, "DPG_TILDE_CALL_MODES")
    require("[list<Argument,1,no>]" in dpg_text, "DPG_TILDE_TRAILING_COMMA_FENCE")
    require(contexts["call_argument_policy"]["parenthesized_comma"]["trailing_comma"] is True, "DPG_ORDINARY_TRAILING_COMMA")
    require(contexts["call_argument_policy"]["tilde"]["trailing_comma"] is False, "DPG_TILDE_TRAILING_COMMA")
    require(contexts["scanner_attachment_policy"]["actor_message"] == {
        "surface": ":~",
        "scanner_outcome": "COLON_TILDE",
        "longest_match_before_single_character_tokens": True,
        "trivia_between_colon_and_tilde": False,
        "spaced_colon_tilde_is_actor_message": False,
    }, "DPG_COLON_TILDE_ATTACHMENT")
    require(len(contexts["surface_sets"]["MutableListInsertSuffix"]) == 4, "DPG_MUTLIST_INSERT_SUFFIX_COUNT")
    require(len(contexts["surface_sets"]["MutableListRemoveSuffix"]) == 5, "DPG_MUTLIST_REMOVE_SUFFIX_COUNT")
    require("ParameterPolicy<C>" in dpg_text and "Parameters<entry>" in dpg_text and "Parameters<primary_constructor>" in dpg_text, "DPG_PARAMETER_OWNER_CONTEXT")

    expected = contract["metrics"]
    require(len(rows) == expected["dpg_rule_clause_count"], "DPG_RULE_CLAUSE_COUNT", len(rows))
    require(len(families) == expected["dpg_rule_family_count"], "DPG_RULE_FAMILY_COUNT", len(families))
    require(len(legacy_names) == expected["legacy_production_count"], "DPG_LEGACY_PRODUCTION_COUNT", len(legacy_names))
    require(len(registry_rows) == expected["legacy_disposition_row_count"], "DPG_LEGACY_DISPOSITION_COUNT", len(registry_rows))
    require(len(old_terminals) == expected["legacy_nonlex_terminal_count"], "DPG_LEGACY_TERMINAL_COUNT", len(old_terminals))

    return {
        "dpg_rule_clause_count": len(rows),
        "dpg_rule_family_count": len(families),
        "legacy_production_count": len(legacy_names),
        "legacy_disposition_row_count": len(registry_rows),
        "legacy_nonlex_terminal_count": len(old_terminals),
        "missing_terminal_count": 0,
        "unbound_external_count": 0,
        "ast_target_domain_miss_count": 0,
    }


def load_documents(root: Path) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        (root / DPG_REL).read_text(encoding="utf-8"),
        read_json(root / CONTEXT_REL),
        read_json(root / FRONTEND_REL),
        read_json(root / DISPOSITION_REL),
        read_json(root / CONTRACT_REL),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--mutations", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    dpg, contexts, frontend, disposition, contract = load_documents(root)
    fixture = read_json(root / FIXTURE_REL)

    for rel, key in ((DPG_REL, "dpg"), (CONTEXT_REL, "contexts"), (LEGACY_REL, "legacy_surface_census")):
        expected = contract["artifacts"][key]
        path = root / rel
        require(path.stat().st_size == expected["bytes"], "DPG_ARTIFACT_BYTES", rel)
        require(sha256(path) == expected["sha256"], "DPG_ARTIFACT_SHA256", rel)
    require(sha256(root / LEGACY_REL) == contexts["source"]["deeplus_ebnf_sha256"], "DPG_CONTEXT_BASELINE_EBNF")
    require(sha256(root / VOCAB_REL) == contexts["source"]["keyword_vocabulary_sha256"], "DPG_CONTEXT_BASELINE_VOCAB")

    metrics = validate_model(root, dpg, contexts, frontend, disposition, contract)
    killed: list[str] = []
    if args.mutations:
        cases: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []
        bad_context = json.loads(json.dumps(contexts))
        del bad_context["surface_sets"]["OrderedComparison"]
        cases.append(("MUT-UNKNOWN-SET", dpg, bad_context, disposition))
        bad_context = json.loads(json.dumps(contexts))
        bad_context["call_argument_policy"]["tilde"]["trailing_comma"] = True
        cases.append(("MUT-TILDE-TRAILING-COMMA", dpg, bad_context, disposition))
        bad_context = json.loads(json.dumps(contexts))
        bad_context["scanner_attachment_policy"]["actor_message"]["trivia_between_colon_and_tilde"] = True
        cases.append(("MUT-COLON-TILDE-ATTACHMENT", dpg, bad_context, disposition))
        bad_disposition = json.loads(json.dumps(disposition))
        bad_disposition["ast_schema"]["kind_domain"].remove("AST/CallExpr")
        cases.append(("MUT-AST-CALL-DOMAIN", dpg, contexts, bad_disposition))
        cases.append(("MUT-PREVIEW-GATE", dpg.replace("SourcePreamble<Role> PreviewGate", "SourcePreamble<Role>"), contexts, disposition))
        cases.append(("MUT-PARAMETER-OWNER-CONTEXT", dpg.replace("Parameters<entry>", "Parameters<function>"), contexts, disposition))
        for mutation_id, changed_dpg, changed_context, changed_disposition in cases:
            try:
                validate_model(root, changed_dpg, changed_context, frontend, changed_disposition, contract)
            except ValidationError:
                killed.append(mutation_id)
            else:
                raise ValidationError(f"DPG_MUTATION_SURVIVED: {mutation_id}")
        require(
            fixture.get("mutation_specs") == killed,
            "DPG_MUTATION_FIXTURE_BINDING",
            fixture.get("mutation_specs"),
        )

    receipt = {
        "schema": "deeplus.parser-grammar-differential-validation-receipt/r1",
        "result": "PASS",
        "evidence_boundary": "design/static DPG differential; production parser execution NOT_RUN",
        "metrics": metrics,
        "mutation_kill_count": len(killed),
        "killed_mutations": killed,
        "governance": contract["governance"],
    }
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
