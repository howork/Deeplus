#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any,Optional
PRODUCT_EXECUTION="NOT_RUN"
def fail(code,detail): raise ValueError(f"{code}: {detail}")
def sha256(x): return hashlib.sha256(x).hexdigest()
def canonical_digest(x): return sha256(json.dumps(x,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(",",":")).encode())
def has_cycle(edges):
 g=defaultdict(list);nodes=set()
 for a,b in edges:g[a].append(b);nodes.update((a,b))
 visiting=set();visited=set()
 def visit(n):
  if n in visiting:return n
  if n in visited:return None
  visiting.add(n)
  for x in sorted(g[n]):
   y=visit(x)
   if y is not None:return y
  visiting.remove(n);visited.add(n)
 for n in sorted(nodes):
  y=visit(n)
  if y is not None:return True,y
 return False,None
REASONS = {
    "AssociatedRequirementAdmitted": [
        (
            "1_requirement_identity_or_kind_conflict",
            "ASSOCIATED_REQUIREMENT_UNRESOLVED",
        ),
        (
            "2_requirement_bounds_or_default_not_admitted",
            "ASSOCIATED_REQUIREMENT_UNRESOLVED",
        ),
        (
            "3_implementation_binding_unresolved_or_ambiguous",
            "ASSOCIATED_REQUIREMENT_UNRESOLVED",
        ),
        (
            "4_recursive_requirement_obligation_cycle",
            "ASSOCIATED_REQUIREMENT_UNRESOLVED",
        ),
    ],
    "EffectErrorRowPolymorphismAdmitted": [
        (
            "1_row_parameter_unbound_or_wrong_kind",
            "EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED",
        ),
        (
            "2_finite_constraints_unsatisfied_or_nonprincipal",
            "EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED",
        ),
        (
            "3_substitution_escapes_or_leaks_private_error",
            "EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED",
        ),
        (
            "4_substitution_cycle",
            "EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED",
        ),
    ],
    "EffectRowSubsumes": [
        (
            "1_required_row_variable_unbound",
            "EFFECT_ROW_VARIABLE_UNBOUND",
        ),
        (
            "2_implementation_row_variable_unbound",
            "EFFECT_ROW_VARIABLE_UNBOUND",
        ),
        (
            "3_effect_term_or_parameter_not_normalizable",
            "EFFECT_ROW_SUBSUMPTION_NOT_ADMITTED",
        ),
        (
            "4_context_row_relation_not_satisfied",
            "EFFECT_ROW_SUBSUMPTION_NOT_ADMITTED",
        ),
    ],
}

EXPECTED_INPUT_DESCRIPTOR_OVERRIDE_IDS = [
    "BorrowEscapeAdmitted",
    "BoxOwnershipAdmitted",
    "OwnershipModeAdmitted",
    *REASONS,
    "ActorProtocolGateAdmitted",
]

PRIMARY_DIAGNOSTICS = {
    "AssociatedRequirementAdmitted": "ASSOCIATED_REQUIREMENT_UNRESOLVED",
    "EffectErrorRowPolymorphismAdmitted":
        "EFFECT_ERROR_ROW_POLYMORPHISM_NOT_ADMITTED",
    "EffectRowSubsumes": "EFFECT_ROW_SUBSUMPTION_NOT_ADMITTED",
}

SECONDARY_DIAGNOSTICS = {
    "AssociatedRequirementAdmitted": [],
    "EffectErrorRowPolymorphismAdmitted": [],
    "EffectRowSubsumes": ["EFFECT_ROW_VARIABLE_UNBOUND"],
}
def expected(
    predicate: str,
    reason_index: Optional[int] = None,
    culprit: Optional[str] = None,
) -> dict[str, Any]:
    if reason_index is None:
        return {
            "variant": "ADMIT",
            "reason_key_or_null": None,
            "diagnostic_id_or_null": None,
            "canonical_culprit_id_or_null": None,
            "emitted_primary_count": 0,
            "later_candidate_status": "NOT_APPLICABLE",
        }
    reason, diagnostic = REASONS[predicate][reason_index - 1]
    return {
        "variant": "REJECT",
        "reason_key_or_null": reason,
        "diagnostic_id_or_null": diagnostic,
        "canonical_culprit_id_or_null": culprit,
        "emitted_primary_count": 1,
        "later_candidate_status": "NOT_EVALUATED",
    }


def choose_candidate(
    candidates: dict[int, set[str]],
) -> tuple[Optional[int], Optional[str]]:
    for rank in range(1, 5):
        if candidates[rank]:
            return rank, sorted(candidates[rank])[0]
    return None, None


def rank_trace(
    predicate: str,
    candidates: dict[int, set[str]],
    selected_rank: Optional[int],
) -> list[dict[str, Any]]:
    rows = []
    for rank, (reason, _) in enumerate(REASONS[predicate], 1):
        rows.append(
            {
                "rank": rank,
                "reason_key": reason,
                "detected": bool(candidates[rank]),
                "selected": rank == selected_rank,
                "culprits": sorted(candidates[rank]),
            }
        )
    return rows


def evaluate_associated(
    value: dict[str, Any],
) -> tuple[Optional[int], Optional[str], dict[int, set[str]]]:
    candidates: dict[int, set[str]] = defaultdict(set)
    requirements = value["requirements"]
    bindings = value["bindings"]
    selected = value["selected_requirement_id"]

    requirement_ids = Counter(row["requirement_id"] for row in requirements)
    for rid, count in requirement_ids.items():
        if count != 1:
            candidates[1].add(rid)
    names = defaultdict(list)
    for row in requirements:
        names[row["name"]].append(row["requirement_id"])
    for rows in names.values():
        if len(rows) > 1:
            candidates[1].add(sorted(rows)[-1])
    selected_rows = [
        row for row in requirements if row["requirement_id"] == selected
    ]
    if len(selected_rows) != 1:
        candidates[1].add(selected)
        selected_row = None
    else:
        selected_row = selected_rows[0]

    binding_ids = Counter(row["binding_id"] for row in bindings)
    for bid, count in binding_ids.items():
        if count != 1:
            candidates[1].add(bid)
    selected_bindings = [
        row for row in bindings if row["requirement_id"] == selected
    ]
    if selected_row is not None:
        for row in selected_bindings:
            if row["kind"] != selected_row["kind"]:
                candidates[1].add(selected)

        kind = selected_row["kind"]
        if selected_row["default_state"] == "present":
            candidates[2].add(selected)
        if kind == "type":
            if (
                selected_row["normalized_value_type_or_null"] is not None
                or selected_row[
                    "normalized_callable_signature_or_null"
                ] is not None
            ):
                candidates[2].add(selected)
        elif kind == "value":
            if (
                selected_row["normalized_value_type_or_null"] is None
                or selected_row[
                    "normalized_callable_signature_or_null"
                ] is not None
            ):
                candidates[2].add(selected)
        elif kind == "function":
            if (
                selected_row[
                    "normalized_callable_signature_or_null"
                ] is None
                or selected_row["normalized_value_type_or_null"] is not None
            ):
                candidates[2].add(selected)

        for dep in selected_row[
            "normalized_dependency_requirement_ids"
        ]:
            if requirement_ids.get(dep) != 1:
                candidates[2].add(dep)

        for row in selected_bindings:
            if not set(selected_row["normalized_bounds"]).issubset(
                row["satisfied_bounds"]
            ):
                candidates[2].add(selected)

        compatible = []
        for row in selected_bindings:
            if (
                row["kind"] != kind
                or row["witness_id_or_null"] is None
                or row["implementation_id_or_null"] is None
            ):
                continue
            if kind == "type":
                ok = (
                    row["normalized_value_type_or_null"] is None
                    and row[
                        "normalized_callable_signature_or_null"
                    ] is None
                    and set(selected_row["normalized_bounds"]).issubset(
                        row["satisfied_bounds"]
                    )
                )
            elif kind == "value":
                ok = (
                    row["normalized_value_type_or_null"]
                    == selected_row["normalized_value_type_or_null"]
                    and row[
                        "normalized_callable_signature_or_null"
                    ] is None
                )
            else:
                ok = (
                    row["normalized_callable_signature_or_null"]
                    == selected_row[
                        "normalized_callable_signature_or_null"
                    ]
                    and row["normalized_value_type_or_null"] is None
                )
            if ok:
                compatible.append(row)
        if len(compatible) != 1:
            candidates[3].add(selected)

    edges = []
    for row in requirements:
        for dependency in row["normalized_dependency_requirement_ids"]:
            edges.append((row["requirement_id"], dependency))
    cyclic, culprit = has_cycle(edges)
    if cyclic and culprit is not None:
        candidates[4].add(culprit)

    selected_rank, culprit = choose_candidate(candidates)
    return selected_rank, culprit, candidates


def poly_atom_key(atom: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    return (
        atom["identity"],
        tuple(atom["normalized_parameter_ids"]),
    )


def bare_variable(expression: dict[str, Any]) -> Optional[str]:
    if not expression["atoms"] and len(expression["variable_ids"]) == 1:
        return expression["variable_ids"][0]
    return None


def expression_membership(
    expression: dict[str, Any],
    atom: tuple[str, tuple[str, ...]],
    assignment: dict[str, bool],
) -> bool:
    return (
        atom in {poly_atom_key(row) for row in expression["atoms"]}
        or any(assignment[variable] for variable in expression["variable_ids"])
    )


def constraint_holds(
    row: dict[str, Any],
    atom: tuple[str, tuple[str, ...]],
    assignment: dict[str, bool],
) -> bool:
    left = expression_membership(
        row["left_row_expression"], atom, assignment
    )
    right = expression_membership(
        row["right_row_expression"], atom, assignment
    )
    if row["relation"] == "subset":
        return (not left) or right
    return left == right


def derived_substitution_edges(
    constraints: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    edges = set()
    for row in constraints:
        if row["relation"] != "equal":
            continue
        left = row["left_row_expression"]
        right = row["right_row_expression"]
        target = bare_variable(left)
        source = right
        if target is None:
            target = bare_variable(right)
            source = left
        if target is None:
            continue
        for variable in source["variable_ids"]:
            # `rho = rho` is a tautological equality, not a substitution
            # dependency.  In `rho = rho | sigma`, only sigma is a genuine
            # dependency.
            if variable != target:
                edges.add((target, variable))
    return sorted(edges)


def derived_scope_edges(
    constraints: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    """Build orientation-independent equality reachability for scope checks."""
    edges = set()
    for row in constraints:
        if row["relation"] != "equal":
            continue
        left = set(row["left_row_expression"]["variable_ids"])
        right = set(row["right_row_expression"]["variable_ids"])
        for source in left:
            for target in right:
                if source != target:
                    edges.add((source, target))
                    edges.add((target, source))
    return sorted(edges)


Literal = tuple[str, bool]
Clause = frozenset[Literal]


def implication_clauses(
    left: dict[str, Any],
    right: dict[str, Any],
    atom: tuple[str, tuple[str, ...]],
) -> list[Clause]:
    """Lower membership(left) => membership(right) to deterministic CNF."""
    left_constant = atom in {
        poly_atom_key(row) for row in left["atoms"]
    }
    right_constant = atom in {
        poly_atom_key(row) for row in right["atoms"]
    }
    if right_constant:
        return []
    right_literals = {
        (variable, True) for variable in right["variable_ids"]
    }
    clauses: list[Clause] = []
    if left_constant:
        clauses.append(frozenset(right_literals))
    for variable in left["variable_ids"]:
        clauses.append(
            frozenset({(variable, False), *right_literals})
        )
    return clauses


def cnf_for_atom(
    atom: tuple[str, tuple[str, ...]],
    constraints: list[dict[str, Any]],
) -> list[Clause]:
    clauses: list[Clause] = []
    for row in constraints:
        left = row["left_row_expression"]
        right = row["right_row_expression"]
        clauses.extend(implication_clauses(left, right, atom))
        if row["relation"] == "equal":
            clauses.extend(implication_clauses(right, left, atom))
    normalized = []
    for clause in clauses:
        if any(
            (variable, not polarity) in clause
            for variable, polarity in clause
        ):
            continue
        normalized.append(clause)
    return sorted(
        set(normalized),
        key=lambda clause: sorted(clause),
    )


def cnf_satisfiable(
    variables: list[str],
    clauses: list[Clause],
    forced: dict[str, bool] | None = None,
) -> bool:
    """Deterministic total DPLL over a finite schema-admitted input."""
    initial = dict(forced or {})

    def simplify(
        current: list[Clause],
        assignment: dict[str, bool],
    ) -> list[Clause] | None:
        result = []
        for clause in current:
            if any(
                variable in assignment
                and assignment[variable] == polarity
                for variable, polarity in clause
            ):
                continue
            reduced = frozenset(
                (variable, polarity)
                for variable, polarity in clause
                if variable not in assignment
            )
            if not reduced:
                return None
            result.append(reduced)
        return result

    def solve(
        current: list[Clause],
        assignment: dict[str, bool],
    ) -> bool:
        while True:
            simplified = simplify(current, assignment)
            if simplified is None:
                return False
            if not simplified:
                return True
            units = sorted(
                next(iter(clause))
                for clause in simplified
                if len(clause) == 1
            )
            if not units:
                current = simplified
                break
            changed = False
            for variable, polarity in units:
                if (
                    variable in assignment
                    and assignment[variable] != polarity
                ):
                    return False
                if variable not in assignment:
                    assignment[variable] = polarity
                    changed = True
            current = simplified
            if not changed:
                break
        unassigned = [
            variable for variable in variables if variable not in assignment
        ]
        if not unassigned:
            return simplify(current, assignment) == []
        variable = unassigned[0]
        for value in (False, True):
            branch = dict(assignment)
            branch[variable] = value
            if solve(current, branch):
                return True
        return False

    return solve(clauses, initial)


def evaluate_poly(
    value: dict[str, Any],
) -> tuple[Optional[int], Optional[str], dict[int, set[str]]]:
    candidates: dict[int, set[str]] = defaultdict(set)
    parameters = value["quantified_row_parameters"]
    parameter_ids = Counter(row["parameter_id"] for row in parameters)
    for pid, count in parameter_ids.items():
        if count != 1:
            candidates[1].add(pid)
    parameter_kinds = {
        row["parameter_id"]: row["row_kind"]
        for row in parameters
    }
    scopes = {
        row["parameter_id"]: row["scope"]
        for row in parameters
    }
    for exported in value["exported_parameter_ids"]:
        if parameter_ids.get(exported) != 1:
            candidates[1].add(exported)
    declared_roots = sorted(
        pid
        for pid, scope in scopes.items()
        if scope == "declared_generic"
    )
    if sorted(value["exported_parameter_ids"]) != declared_roots:
        candidates[1].add(
            sorted(
                set(value["exported_parameter_ids"])
                ^ set(declared_roots)
            )[0]
            if set(value["exported_parameter_ids"]) ^ set(declared_roots)
            else "exported_parameter_ids"
        )

    constraints = sorted(
        value["row_constraints"],
        key=lambda row: (
            row["canonical_order_key"],
            row["constraint_id"],
        ),
    )
    constraint_ids = Counter(row["constraint_id"] for row in constraints)
    for cid, count in constraint_ids.items():
        if count != 1:
            candidates[1].add(cid)
    for row in constraints:
        left = row["left_row_expression"]
        right = row["right_row_expression"]
        if left["row_kind"] != right["row_kind"]:
            candidates[1].add(row["constraint_id"])
        for expression in (left, right):
            for variable in expression["variable_ids"]:
                if (
                    parameter_kinds.get(variable)
                    != expression["row_kind"]
                ):
                    candidates[1].add(variable)

    by_kind: dict[str, list[dict[str, Any]]] = {
        "effect": [],
        "error": [],
    }
    for row in constraints:
        left = row["left_row_expression"]
        right = row["right_row_expression"]
        row_kind = left["row_kind"]
        variables_are_well_kinded = all(
            parameter_kinds.get(variable) == expression["row_kind"]
            for expression in (left, right)
            for variable in expression["variable_ids"]
        )
        if row_kind == right["row_kind"] and variables_are_well_kinded:
            by_kind[row_kind].append(row)

    for kind in ("effect", "error"):
        variables = sorted(
            pid
            for pid, parameter_kind in parameter_kinds.items()
            if parameter_kind == kind
        )
        relevant = by_kind[kind]
        atoms = {
            poly_atom_key(atom)
            for row in relevant
            for side in (
                "left_row_expression",
                "right_row_expression",
            )
            for atom in row[side]["atoms"]
        }
        atoms.add((f"$sentinel:{kind}", ()))

        unsat_constraint: Optional[str] = None
        for index, row in enumerate(relevant, 1):
            prefix = relevant[:index]
            if any(
                not cnf_satisfiable(
                    variables,
                    cnf_for_atom(atom, prefix),
                )
                for atom in sorted(atoms)
            ):
                unsat_constraint = row["constraint_id"]
                break
        if unsat_constraint is not None:
            candidates[2].add(unsat_constraint)
            continue

        for atom in sorted(atoms):
            clauses = cnf_for_atom(atom, relevant)
            if not cnf_satisfiable(variables, clauses):
                candidates[2].add(
                    relevant[-1]["constraint_id"]
                    if relevant
                    else kind
                )
                continue
            for variable in variables:
                admits_false = cnf_satisfiable(
                    variables, clauses, {variable: False}
                )
                admits_true = cnf_satisfiable(
                    variables, clauses, {variable: True}
                )
                if admits_false and admits_true:
                    candidates[2].add(variable)
                    break

    visibility_rank = {"private": 0, "common": 1, "public": 2}
    declaration_rank = visibility_rank[value["declaration_visibility"]]
    for row in constraints:
        for side in ("left_row_expression", "right_row_expression"):
            for atom in row[side]["atoms"]:
                if visibility_rank[atom["visibility"]] < declaration_rank:
                    candidates[3].add(atom["identity"])

    edges = derived_substitution_edges(constraints)
    scope_edges = derived_scope_edges(constraints)
    graph: dict[str, list[str]] = defaultdict(list)
    for source, target in scope_edges:
        graph[source].append(target)
    solver_local = {
        pid for pid, scope in scopes.items() if scope == "solver_local"
    }
    for root in declared_roots:
        if root in solver_local:
            candidates[3].add(root)
        pending = [root]
        visited = set()
        while pending:
            node = pending.pop()
            if node in visited:
                continue
            visited.add(node)
            for target in graph[node]:
                if target in solver_local:
                    candidates[3].add(target)
                pending.append(target)

    cyclic, culprit = has_cycle(edges)
    if cyclic and culprit is not None:
        candidates[4].add(culprit)

    selected_rank, culprit = choose_candidate(candidates)
    return selected_rank, culprit, candidates


def effect_atom_key(
    atom: dict[str, Any],
    parameter_map: dict[str, list[dict[str, Any]]],
    candidates: dict[int, set[str]],
) -> tuple[str, tuple[tuple[str, str], ...]]:
    normalized = []

    def resolve(
        parameter_id: str,
        expected_kind: str,
        visiting: tuple[str, ...],
    ) -> tuple[str, str] | None:
        rows = parameter_map.get(parameter_id, [])
        if len(rows) != 1:
            candidates[3].add(parameter_id)
            return None
        row = rows[0]
        if row["parameter_kind"] != expected_kind:
            candidates[3].add(parameter_id)
            return None
        canonical = row["canonical_identity_or_null"]
        alias = row["alias_parameter_id_or_null"]
        if (canonical is None) == (alias is None):
            candidates[3].add(parameter_id)
            return None
        if canonical is not None:
            return expected_kind, canonical
        if parameter_id in visiting or alias in visiting:
            candidates[3].add(sorted((*visiting, parameter_id, alias))[0])
            return None
        return resolve(alias, expected_kind, (*visiting, parameter_id))

    for argument in atom["parameter_arguments"]:
        resolved = resolve(
            argument["parameter_id"],
            argument["expected_kind"],
            (),
        )
        if resolved is not None:
            normalized.append(resolved)
    return atom["effect_id"], tuple(normalized)


def evaluate_subsumption(
    value: dict[str, Any],
) -> tuple[Optional[int], Optional[str], dict[int, set[str]]]:
    candidates: dict[int, set[str]] = defaultdict(set)
    row_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in value["row_environment"]:
        row_map[row["variable_id"]].append(row["bound_row"])
    for variable, rows in row_map.items():
        if len(rows) != 1:
            candidates[3].add(variable)

    parameter_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in value["parameter_environment"]:
        parameter_map[row["parameter_id"]].append(row)
    for parameter, rows in parameter_map.items():
        if len(rows) != 1:
            candidates[3].add(parameter)

    def expand(
        row: dict[str, Any],
        origin: str,
        visiting: tuple[str, ...] = (),
    ) -> set[tuple[str, tuple[tuple[str, str], ...]]]:
        atoms = {
            effect_atom_key(atom, parameter_map, candidates)
            for atom in row["atoms"]
        }
        for variable in sorted(row["variable_ids"]):
            rows = row_map.get(variable, [])
            if not rows:
                candidates[1 if origin == "required" else 2].add(variable)
                continue
            if len(rows) != 1:
                candidates[3].add(variable)
                continue
            if variable in visiting:
                candidates[3].add(sorted((*visiting, variable))[0])
                continue
            atoms |= expand(rows[0], origin, (*visiting, variable))
        return atoms

    required_atoms = expand(value["required_row"], "required")
    implementation_atoms = expand(
        value["implementation_row"], "implementation"
    )

    context = value["context_kind"]
    if context in {"trait_witness", "function_value"}:
        mismatches = [
            ("implementation_only", atom)
            for atom in implementation_atoms - required_atoms
        ]
    else:
        mismatches = [
            ("implementation_only", atom)
            for atom in implementation_atoms - required_atoms
        ] + [
            ("required_only", atom)
            for atom in required_atoms - implementation_atoms
        ]
    if mismatches:
        detail_rank = {"implementation_only": 0, "required_only": 1}
        detail, atom = sorted(
            mismatches,
            key=lambda row: (row[1], detail_rank[row[0]]),
        )[0]
        candidates[4].add(f"{atom[0]}:{detail}")

    selected_rank, culprit = choose_candidate(candidates)
    if selected_rank == 4 and culprit is not None:
        culprit = culprit.split(":", 1)[0]
    return selected_rank, culprit, candidates


def evaluate_with_trace(
    value: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    predicate = value["predicate_id"]
    if predicate == "AssociatedRequirementAdmitted":
        rank, culprit, candidates = evaluate_associated(value)
    elif predicate == "EffectErrorRowPolymorphismAdmitted":
        rank, culprit, candidates = evaluate_poly(value)
    elif predicate == "EffectRowSubsumes":
        rank, culprit, candidates = evaluate_subsumption(value)
    else:
        fail("R9_UNKNOWN_PREDICATE", predicate)
    return expected(predicate, rank, culprit), rank_trace(
        predicate, candidates, rank
    )


def evaluate(value: dict[str, Any]) -> dict[str, Any]:
    return evaluate_with_trace(value)[0]

IDS=("R9_DD_SCHEMA_CLOSED_UNION","R9_DD_CONTRACT_EXACT","R9_DD_BASE_CASES_18","R9_DD_ADVERSARIAL_13","R9_DD_MUTATIONS_12","R9_DD_REASON_KEYS_12","R9_DD_SCOPE_ORIENTATION_INVARIANT","R9_DD_REGISTRY_DISPATCH_EXACT","R9_DD_GOVERNANCE_FENCE")
def main():
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("."));root=p.parse_args().root.resolve()
 load=lambda x:json.loads((root/x).read_text(encoding="utf-8"));s=load("schemas/language/diagnostic-dispatch-closure-input-r1.schema.json");f=load("tests/fixtures/current/diagnostic-dispatch-closure-r1.json");c=load("spec/contracts/diagnostic-dispatch-closure-r1.json");checks=[];errors=[]
 def ck(i,fn):
  try:d=fn();checks.append({"check_id":i,"status":"PASS","detail":d})
  except Exception as e:checks.append({"check_id":i,"status":"FAIL","detail":str(e)});errors.append(f"{i}: {e}")
 def c0():assert len(s["oneOf"])==3 and "rcts-v5" not in json.dumps(s).lower();return "closed union=3; RCTS fallback=0"
 ck(IDS[0],c0)
 def c1():assert c["closed_input_union"]["rcts_fallback"]=="PROHIBITED" and c["expected_registry_counts"]=={"predicates":277,"diagnostics":1436,"relations":559,"dispatch_rows":226,"undefined_or_unlisted_dispatch":0};return "exact semantic contract"
 ck(IDS[1],c1)
 def c2():
  assert len(f["cases"])==18 and len({x["test_id"] for x in f["cases"]})==18
  for x in f["cases"]:assert evaluate(x["input"])==x["expected"],x["test_id"]
  return "18/18 recomputed"
 ck(IDS[2],c2)
 def c3():
  assert len(f["adversarial_cases"])==13
  for x in f["adversarial_cases"]:
   o,tr=evaluate_with_trace(x["input"]);assert o==x["expected"]==x["observed"] and tr==x["rank_trace"] and x["passed"] and canonical_digest(x["input"])==x["input_sha256"] and canonical_digest(o)==x["semantic_digest"],x["test_id"]
  return "13/13 recomputed"
 ck(IDS[3],c3)
 def c4():assert [x["mutation_id"] for x in f["mutation_matrix"]]==[f"R9-MUT-{i:03d}" for i in range(1,13)] and all(x["passed"] for x in f["mutation_matrix"]);return "12/12 bound"
 ck(IDS[4],c4)
 def c5():
  assert sum(map(len,REASONS.values()))==12
  for p,q in c["predicate_contracts"].items():assert [(x["reason_key"],x["diagnostic_id"]) for x in q["reasons"]]==REASONS[p]
  return "12 ordered reasons"
 ck(IDS[5],c5)
 def c6():
  q={x["test_id"]:x for x in f["adversarial_cases"]};a=q["R9-ADV-POLY-DERIVED-SCOPE-ESCAPE"];b=q["R9-ADV-POLY-DERIVED-SCOPE-ESCAPE-REVERSED"];assert a["observed"]==b["observed"] and a["semantic_digest"]==b["semantic_digest"];return "orientation invariant"
 ck(IDS[6],c6)
 def c7():
  rows=[]
  for z in ("spec/types/predicates/chunks/part-0001.json","spec/types/predicates/chunks/part-0004.json"):rows+=load(z)
  q={x["predicate_id"]:x for x in rows};m=load("spec/types/predicates/catalog-metadata.json");overrides=m["input_descriptor_overrides"];assert list(overrides)==EXPECTED_INPUT_DESCRIPTOR_OVERRIDE_IDS and m["override_count"]==len(EXPECTED_INPUT_DESCRIPTOR_OVERRIDE_IDS) and overrides["ActorProtocolGateAdmitted"]=={"input_descriptor":"ActorProtocolDirectConformanceDescriptorR1","input_descriptor_schema":"schemas/language/actor-protocol-direct-conformance-descriptor.schema.json"}
  for p,r in REASONS.items():assert q[p]["input_descriptor"]=="DiagnosticDispatchClosureInputR1" and q[p]["diagnostic_dispatch"]==dict(r) and q[p]["active_primary_diagnostic"]==PRIMARY_DIAGNOSTICS[p] and q[p]["secondary_diagnostics"]==SECONDARY_DIAGNOSTICS[p]
  return "three typed rows; exact seven R41 overrides"
 ck(IDS[7],c7)
 def c8():
  g=c["governance"];assert(g["semantic_p0_after_candidate"],g["canonical_feature_p1_open"],g["separate_m13_actions_open"])==(0,22,4) and g["product_lanes"]["count"]==15 and g["product_lanes"]["status"]=="NOT_RUN" and g["canonical_source_mutation"]==g["github_mutation"]==0;return "P0=0 P1=22 M13=4 product=15/15 NOT_RUN"
 ck(IDS[8],c8)
 n=sum(x["status"]=="PASS" for x in checks);r={"schema":"deeplus.r9-diagnostic-dispatch-closure-test-receipt/v1","result":"PASS" if n==len(IDS) else "FAIL","product_execution":"NOT_RUN","check_scope":"R9_DIAGNOSTIC_DISPATCH_CLOSURE_EXACT","check_count":len(IDS),"passed_check_count":n,"base_case_count":len(f["cases"]),"adversarial_case_count":len(f["adversarial_cases"]),"mutation_count":len(f["mutation_matrix"]),"reason_key_count":sum(map(len,REASONS.values())),"checks":checks,"errors":errors};print(json.dumps(r,indent=2));return 0 if r["result"]=="PASS" else 1
if __name__=="__main__":raise SystemExit(main())
