#!/usr/bin/env python3
"""Bind current Pattern, task, Actor, and synchronization MIR evidence."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "tests/fixtures/imported/mir-responsibility-fixtures.json"


def source_span(index: int) -> dict[str, object]:
    return {"file": "fixture.dp", "start": index, "end": index + 1}


PATTERN_PROFILES = {
    "MATCH_BODY_COMPLETED": {
        "dpm_fixture_id": "DPM-R1-POS-007",
        "context_id": "PCTX-STATEMENT-MATCH",
        "failure_disposition": "NEXT_MATCH_ARM",
        "pattern_id": "move-resource-ready",
        "final_binder_ids": ["binder-value"],
        "committed_move_count": 1,
        "phases": [
            ("subject_evaluate", "entered"),
            ("subject_acquire", "entered"),
            ("test_plan_build", "completed"),
            ("structural_test", "matched"),
            ("probe_bind", "completed"),
            ("guard_evaluate", "true"),
            ("atomic_commit", "committed"),
            ("final_bind", "completed"),
            ("body", "completed"),
            ("exit_or_join", "completed"),
        ],
    },
    "PATTERN_MISMATCH_PRECOMMIT": {
        "dpm_fixture_id": "DPM-R1-BND-005",
        "context_id": "PCTX-IF-LET",
        "failure_disposition": "DISPOSE_TEMPORARY_EXACTLY_ONCE",
        "pattern_id": "result-ok-temporary",
        "final_binder_ids": [],
        "committed_move_count": 0,
        "phases": [
            ("subject_evaluate", "entered"),
            ("subject_acquire", "entered"),
            ("test_plan_build", "completed"),
            ("structural_test", "mismatched"),
            ("exit_or_join", "completed"),
        ],
    },
    "GUARD_FALSE_PRECOMMIT": {
        "dpm_fixture_id": "DPM-R1-BND-004",
        "context_id": "PCTX-STATEMENT-MATCH",
        "failure_disposition": "NEXT_MATCH_ARM",
        "pattern_id": "move-item-ready-false-guard",
        "final_binder_ids": [],
        "committed_move_count": 0,
        "phases": [
            ("subject_evaluate", "entered"),
            ("subject_acquire", "entered"),
            ("test_plan_build", "completed"),
            ("structural_test", "matched"),
            ("probe_bind", "completed"),
            ("guard_evaluate", "false"),
            ("exit_or_join", "completed"),
        ],
    },
    "GUARDED_LET_ELSE_TRANSFER": {
        "dpm_fixture_id": "DPM-R1-POS-006",
        "context_id": "PCTX-GUARDED-LET",
        "failure_disposition": "TRANSFER_TO_GUARDED_LET_ELSE",
        "pattern_id": "guarded-let-result-ok",
        "final_binder_ids": [],
        "committed_move_count": 0,
        "phases": [
            ("subject_evaluate", "entered"),
            ("subject_acquire", "entered"),
            ("test_plan_build", "completed"),
            ("structural_test", "mismatched"),
            ("exit_or_join", "completed"),
        ],
    },
    "FOR_LET_CANDIDATE_FILTERED": {
        "dpm_fixture_id": "DPM-R1-BND-006",
        "context_id": "PCTX-FOR-LET",
        "failure_disposition": "ITERATOR_CANDIDATE_SKIP_OR_DISCHARGE_ONCE",
        "pattern_id": "for-let-result-ok-false-guard",
        "final_binder_ids": [],
        "committed_move_count": 0,
        "phases": [
            ("subject_evaluate", "entered"),
            ("subject_acquire", "entered"),
            ("test_plan_build", "completed"),
            ("structural_test", "matched"),
            ("probe_bind", "completed"),
            ("guard_evaluate", "false"),
            ("exit_or_join", "completed"),
        ],
    },
    "DESTRUCTURING_BODY_COMPLETED": {
        "dpm_fixture_id": "DPM-R1-POS-001",
        "context_id": "PCTX-PLAIN-LET",
        "failure_disposition": "STATICALLY_ADMITTED_NO_RUNTIME_FAILURE_EDGE",
        "pattern_id": "record-name-age",
        "final_binder_ids": ["binder-name", "binder-age"],
        "committed_move_count": 0,
        "phases": [
            ("subject_evaluate", "entered"),
            ("subject_acquire", "entered"),
            ("test_plan_build", "completed"),
            ("structural_test", "matched"),
            ("probe_bind", "completed"),
            ("atomic_commit", "committed"),
            ("final_bind", "completed"),
            ("body", "completed"),
            ("exit_or_join", "completed"),
        ],
    },
}

PATTERN_PROFILE_BY_FIXTURE = {
    "MIR-POS-ALL-KINDS-001": "MATCH_BODY_COMPLETED",
    "MIR-POS-ACTOR-REJECTED-ADMISSION-001": "PATTERN_MISMATCH_PRECOMMIT",
    "MIR-POS-TASK-SPAWN-ORDER-001": "DESTRUCTURING_BODY_COMPLETED",
    "MIR-NEG-STACK-KIND-001": "GUARD_FALSE_PRECOMMIT",
    "MIR-NEG-LAW-IDENTITY-001": "GUARDED_LET_ELSE_TRANSFER",
    "MIR-NEG-SOURCE-ORDER-001": "FOR_LET_CANDIDATE_FILTERED",
    "MIR-NEG-COMMIT-POINT-001": "MATCH_BODY_COMPLETED",
    "MIR-NEG-PAYLOAD-SHAPE-001": "PATTERN_MISMATCH_PRECOMMIT",
    "MIR-NEG-SYNC-RELEASE-001": "DESTRUCTURING_BODY_COMPLETED",
    "MIR-NEG-SYNC-SUSPEND-001": "GUARD_FALSE_PRECOMMIT",
    "MIR-NEG-ACTOR-TURN-OVERLAP-001": "GUARDED_LET_ELSE_TRANSFER",
    "MIR-NEG-TASK-COMPLETION-PRIMARY-001": "FOR_LET_CANDIDATE_FILTERED",
}

EVENT_STACKS = (
    "evaluation_events",
    "temporary_stack",
    "ownership_events",
    "cleanup_stack",
    "rollback_stack",
    "primary_failure",
    "suppressed_failures",
    "cancellation_state",
    "task_scope",
    "actor_isolation",
    "pattern_trace",
    "synchronization_events",
    "control_events",
    "callable_events",
    "evidence_events",
)

GENERATED_POSITIVE_IDS = {
    "MIR-POS-ACTOR-REJECTED-ADMISSION-001",
    "MIR-POS-TASK-SPAWN-ORDER-001",
}

GENERATED_NEGATIVE_IDS = {
    "MIR-NEG-ACTOR-TURN-OVERLAP-001",
    "MIR-NEG-TASK-COMPLETION-PRIMARY-001",
    "MIR-NEG-SYNC-RELEASE-001",
    "MIR-NEG-SYNC-SUSPEND-001",
}


def pattern_event(
    index: int,
    law_id: str,
    profile_name: str,
    phase: str,
    outcome: str,
) -> dict[str, object]:
    profile = PATTERN_PROFILES[profile_name]
    sequence = 19 + index
    committed = phase in {"final_bind", "body", "exit_or_join"} and outcome != "mismatched"
    atomic_commit_seen = phase in {"atomic_commit", "final_bind", "body", "exit_or_join"}
    final_binder_ids = list(profile["final_binder_ids"]) if committed else []
    move_count = int(profile["committed_move_count"]) if atomic_commit_seen else 0
    return {
        "kind": "pattern_phase",
        "event_id": f"ev-{sequence:02d}",
        "sequence": sequence,
        "law_id": law_id,
        "source_span": source_span(sequence),
        "trace_id": "pattern-trace-0",
        "dpm_fixture_id": profile["dpm_fixture_id"],
        "attempt_disposition": profile_name,
        "context_id": profile["context_id"],
        "subject_id": "subject-0",
        "pattern_id": profile["pattern_id"],
        "test_plan_id": "test-plan-0",
        "probe_binder_set_id": "probe-binders-0",
        "probe_binder_ids": ["probe-binder-0"] if phase in {"probe_bind", "guard_evaluate"} else [],
        "final_binder_set_id": "final-binders-0",
        "final_binder_ids": final_binder_ids,
        "commit_plan_id": "commit-plan-0" if profile_name in {"MATCH_BODY_COMPLETED", "DESTRUCTURING_BODY_COMPLETED"} else None,
        "failure_disposition": profile["failure_disposition"],
        "pattern_move_count": move_count,
        "lifecycle_ids": {
            "payload_drop_plan_id": "payload-drop-0",
            "user_cleanup_plan_id": "user-cleanup-0",
            "storage_disposition_plan_id": "storage-disposition-0",
            "allocator_or_domain_id": "allocator-domain-0",
            "foreign_release_plan_id": "foreign-release-0",
            "failure_disposition_plan_id": "failure-disposition-0",
        },
        "precommit_zero_counts": {
            "ownership_commit": 0,
            "irreversible_borrow": 0,
            "authority_acquisition": 0,
            "escape": 0,
            "suspension": 0,
            "partial_binding": 0,
        },
        "phase": phase,
        "outcome": outcome,
        "consuming": phase == "atomic_commit" and move_count > 0,
    }


def iter_events(record: dict[str, object]):
    """Yield every event-bearing object from one MIR record."""
    for field in EVENT_STACKS:
        value = record.get(field)
        if value is None:
            continue
        if isinstance(value, list):
            yield from value
        else:
            yield value


def normalize_source_order(record: dict[str, object]) -> None:
    events = sorted(iter_events(record), key=lambda event: int(event["sequence"]))
    record["source_order"] = [str(event["event_id"]) for event in events]
    record["source_span"]["end"] = max(
        int(record["source_span"]["end"]),
        max(int(event["sequence"]) for event in events) + 1,
    )


def actor_lifecycle_event(
    *,
    sequence: int,
    law_id: str,
    phase: str,
    turn_id: str | None,
    turn_index: int | None,
    message_id: str,
    channel_sequence: int | None,
    transfer_id: str | None = None,
    outcome: str = "success",
    capacity_outcome: str = "admitted",
    ownership_commit_state: str = "committed",
    ownership_commit_count: int = 1,
    transfer_disposition: str = "receiver_owned",
    state_region_authority: str = "held",
) -> dict[str, object]:
    return {
        "kind": "actor_lifecycle",
        "event_id": f"ev-{sequence:02d}",
        "sequence": sequence,
        "law_id": law_id,
        "source_span": source_span(sequence),
        "actor_id": "actor-0",
        "receiver_id": "actor-0",
        "sender_id": "sender-0",
        "mailbox_id": "mailbox-0",
        "channel_id": "channel-0",
        "channel_sequence": channel_sequence,
        "mailbox_profile_id": "mailbox-profile-0",
        "state_region_id": "actor-state-region-0",
        "state_region_authority": state_region_authority,
        "turn_id": turn_id,
        "turn_index": turn_index,
        "handler_id": "handler-0" if turn_id is not None else None,
        "supervisor_id": None,
        "message_id": message_id,
        "phase": phase,
        "outcome": outcome,
        "correlation_id": None,
        "reply_id": None,
        "transfer_id": transfer_id or f"transfer-{message_id.rsplit('-', 1)[-1]}",
        "failure_id": None,
        "capacity_outcome": capacity_outcome,
        "ownership_commit_state": ownership_commit_state,
        "ownership_commit_count": ownership_commit_count,
        "transfer_disposition": transfer_disposition,
    }


def bind_record(record: dict[str, object]) -> bool:
    law_id = str(record["law_id"])
    record["pattern_trace"] = []

    for event in record["task_scope"]:
        if event["kind"] == "task_spawn":
            event.update(
                scope_id="scope-0",
                parent_task_id=None,
                cancellation_id="cancellation-0",
                cleanup_barrier_id="cleanup-barrier-0",
            )
        elif event["kind"] == "task_join":
            event.update(
                scope_id="scope-0",
                parent_task_id=None,
                spawn_index=0,
                cancellation_id="cancellation-0",
                cleanup_barrier_id="cleanup-barrier-0",
                failure_id=None,
                failure_role="none",
                suppression_index=None,
            )
    record["task_scope"] = [event for event in record["task_scope"] if event["kind"] != "task_lifecycle"]
    record["task_scope"].append(
        {
            "kind": "task_lifecycle",
            "event_id": "ev-29",
            "sequence": 29,
            "law_id": law_id,
            "source_span": source_span(29),
            "task_id": "task-0",
            "scope_id": "scope-0",
            "parent_task_id": None,
            "spawn_index": 0,
            "aggregation_scope_id": "scope-0",
            "cancellation_id": "cancellation-0",
            "cleanup_barrier_id": "cleanup-barrier-0",
            "phase": "scope_terminal",
            "outcome": "success",
            "failure_id": None,
            "child_failure_id": None,
            "primary_failure_id": None,
            "failure_role": "none",
            "suppression_index": None,
        }
    )

    record["actor_isolation"] = [
        event
        for event in record["actor_isolation"]
        if event["kind"] != "actor_lifecycle" and event["event_id"] not in {"ev-34", "ev-35"}
    ]
    for event in record["actor_isolation"]:
        if event["kind"] in {"actor_enqueue", "actor_dequeue"}:
            event.update(
                receiver_id="actor-0",
                channel_id="channel-0",
                mailbox_id="mailbox-0",
                mailbox_profile_id="mailbox-profile-0",
                transfer_id="transfer-0",
                channel_sequence=0,
            )
        if event["kind"] == "actor_enqueue":
            event.update(
                capacity_outcome="admitted",
                ownership_commit_count=1,
                transfer_disposition="receiver_owned",
            )
    actor_turns = [
        (30, "turn_start", "turn-0", 0, "held", "message-0", 0),
        (31, "turn_suspend", "turn-0", 0, "held", "message-0", 0),
        (32, "turn_resume", "turn-0", 0, "held", "message-0", 0),
        (33, "turn_finish", "turn-0", 0, "released", "message-0", 0),
        (36, "turn_start", "turn-1", 1, "held", "message-1", 1),
        (37, "turn_finish", "turn-1", 1, "released", "message-1", 1),
    ]
    record["actor_isolation"].extend(
        actor_lifecycle_event(
            sequence=sequence,
            law_id=law_id,
            phase=phase,
            turn_id=turn_id,
            turn_index=turn_index,
            state_region_authority=authority,
            message_id=message_id,
            channel_sequence=channel_sequence,
        )
        for sequence, phase, turn_id, turn_index, authority, message_id, channel_sequence in actor_turns
    )
    record["actor_isolation"].extend(
        [
            {
                "kind": "actor_enqueue",
                "event_id": "ev-34",
                "sequence": 34,
                "law_id": law_id,
                "source_span": source_span(34),
                "actor_id": "actor-0",
                "receiver_id": "actor-0",
                "sender_id": "sender-0",
                "channel_id": "channel-0",
                "mailbox_id": "mailbox-0",
                "mailbox_profile_id": "mailbox-profile-0",
                "message_id": "message-1",
                "transfer_id": "transfer-1",
                "channel_sequence": 1,
                "enqueue_index": 1,
                "capacity_outcome": "admitted",
                "ownership_commit_count": 1,
                "transfer_disposition": "receiver_owned",
            },
            {
                "kind": "actor_dequeue",
                "event_id": "ev-35",
                "sequence": 35,
                "law_id": law_id,
                "source_span": source_span(35),
                "actor_id": "actor-0",
                "receiver_id": "actor-0",
                "sender_id": "sender-0",
                "channel_id": "channel-0",
                "mailbox_id": "mailbox-0",
                "mailbox_profile_id": "mailbox-profile-0",
                "message_id": "message-1",
                "transfer_id": "transfer-1",
                "channel_sequence": 1,
                "dequeue_index": 1,
            },
        ]
    )
    record["actor_isolation"].sort(key=lambda event: int(event["sequence"]))
    synchronization_operations = [
        ("shared_cell", "observe_begin", "entered", "sequentially_consistent", False),
        ("shared_cell", "observe_end", "completed", "sequentially_consistent", False),
        ("shared_cell", "replace_commit", "committed", "sequentially_consistent", True),
        ("shared_mutex", "lock_acquire", "acquired", "mutex_handoff", False),
        ("shared_mutex", "lock_release", "released", "mutex_handoff", False),
    ]
    record["synchronization_events"] = []
    for offset, (profile, operation, outcome, ordering, consuming) in enumerate(synchronization_operations):
        sequence = 38 + offset
        sync_id = "shared-cell-0" if profile == "shared_cell" else "shared-mutex-0"
        record["synchronization_events"].append(
            {
                "kind": "synchronization",
                "event_id": f"ev-{sequence:02d}",
                "sequence": sequence,
                "law_id": law_id,
                "source_span": source_span(sequence),
                "sync_id": sync_id,
                "operation_id": f"{operation}-0",
                "profile": profile,
                "operation": operation,
                "owner_id": "task-0",
                "value_id": "value-0",
                "outcome": outcome,
                "ordering": ordering,
                "cleanup_region_id": "sync-cleanup-0" if profile == "shared_mutex" else None,
                "handoff_index": offset - 3 if profile == "shared_mutex" else offset,
                "cancellation_id": None,
                "consuming": consuming,
            }
        )
    record["source_span"]["end"] = max(int(record["source_span"]["end"]), 43)
    return True


def bind_pattern_evidence(document: dict[str, object]) -> None:
    fixtures = [*document["positive_fixtures"], *document["negative_fixtures"]]
    observed_ids = {str(fixture["fixture_id"]) for fixture in fixtures}
    if observed_ids != set(PATTERN_PROFILE_BY_FIXTURE):
        missing = sorted(set(PATTERN_PROFILE_BY_FIXTURE) - observed_ids)
        extra = sorted(observed_ids - set(PATTERN_PROFILE_BY_FIXTURE))
        raise ValueError(f"Pattern evidence fixture-set drift: missing={missing} extra={extra}")
    for fixture in fixtures:
        fixture_id = str(fixture["fixture_id"])
        profile_name = PATTERN_PROFILE_BY_FIXTURE[fixture_id]
        profile = PATTERN_PROFILES[profile_name]
        record = fixture["record"]
        law_id = str(record["law_id"])
        record["pattern_trace"] = [
            pattern_event(index, law_id, profile_name, phase, outcome)
            for index, (phase, outcome) in enumerate(profile["phases"])
        ]
        normalize_source_order(record)
        if fixture_id == "MIR-NEG-SOURCE-ORDER-001":
            record["source_order"][0], record["source_order"][1] = (
                record["source_order"][1],
                record["source_order"][0],
            )


def bind_actor_rejection_positive(document: dict[str, object]) -> None:
    fixture = copy.deepcopy(document["positive_fixtures"][0])
    fixture["fixture_id"] = "MIR-POS-ACTOR-REJECTED-ADMISSION-001"
    record = fixture["record"]
    law_id = str(record["law_id"])
    record["actor_isolation"] = [
        actor_lifecycle_event(
            sequence=12,
            law_id=law_id,
            phase="admission_rejected",
            turn_id=None,
            turn_index=None,
            message_id="message-rejected-0",
            channel_sequence=None,
            transfer_id="transfer-rejected-0",
            outcome="capacity_rejected",
            capacity_outcome="capacity_rejected",
            ownership_commit_state="precommit",
            ownership_commit_count=0,
            transfer_disposition="sender_retained",
            state_region_authority="not_applicable",
        )
    ]
    normalize_source_order(record)
    fixture["expected"] = "admission_rejected"
    document["positive_fixtures"].append(fixture)


def task_spawn_event(sequence: int, law_id: str, task_id: str, spawn_index: int) -> dict[str, object]:
    return {
        "kind": "task_spawn",
        "event_id": f"ev-{sequence:02d}",
        "sequence": sequence,
        "law_id": law_id,
        "source_span": source_span(sequence),
        "task_id": task_id,
        "owner_id": "task-scope-0",
        "scope_id": "scope-order-0",
        "parent_task_id": "task-parent-0",
        "cancellation_id": "cancellation-order-0",
        "cleanup_barrier_id": "cleanup-barrier-order-0",
        "spawn_index": spawn_index,
    }


def task_lifecycle_failure_event(
    *,
    sequence: int,
    law_id: str,
    task_id: str,
    spawn_index: int,
    failure_id: str,
    primary_failure_id: str,
    failure_role: str,
    suppression_index: int | None,
) -> dict[str, object]:
    return {
        "kind": "task_lifecycle",
        "event_id": f"ev-{sequence:02d}",
        "sequence": sequence,
        "law_id": law_id,
        "source_span": source_span(sequence),
        "task_id": task_id,
        "scope_id": "scope-order-0",
        "parent_task_id": "task-parent-0",
        "spawn_index": spawn_index,
        "aggregation_scope_id": "scope-order-0",
        "cancellation_id": "cancellation-order-0",
        "cleanup_barrier_id": "cleanup-barrier-order-0",
        "phase": "scope_terminal",
        "outcome": "error",
        "failure_id": failure_id,
        "child_failure_id": failure_id,
        "primary_failure_id": primary_failure_id,
        "failure_role": failure_role,
        "suppression_index": suppression_index,
    }


def task_join_failure_event(
    *,
    sequence: int,
    law_id: str,
    task_id: str,
    spawn_index: int,
    join_index: int,
    failure_id: str,
    failure_role: str,
    suppression_index: int | None,
) -> dict[str, object]:
    return {
        "kind": "task_join",
        "event_id": f"ev-{sequence:02d}",
        "sequence": sequence,
        "law_id": law_id,
        "source_span": source_span(sequence),
        "task_id": task_id,
        "scope_id": "scope-order-0",
        "parent_task_id": "task-parent-0",
        "spawn_index": spawn_index,
        "cancellation_id": "cancellation-order-0",
        "cleanup_barrier_id": "cleanup-barrier-order-0",
        "join_index": join_index,
        "outcome": "failed",
        "failure_id": failure_id,
        "failure_role": failure_role,
        "suppression_index": suppression_index,
    }


def bind_task_order_positive(document: dict[str, object]) -> None:
    fixture = copy.deepcopy(document["positive_fixtures"][0])
    fixture["fixture_id"] = "MIR-POS-TASK-SPAWN-ORDER-001"
    record = fixture["record"]
    law_id = str(record["law_id"])
    # Child 1 completes first, but child 0 remains primary because lexical
    # spawn_index, not scheduler completion order, controls aggregation.
    record["task_scope"] = [
        task_spawn_event(10, law_id, "task-child-0", 0),
        task_spawn_event(11, law_id, "task-child-1", 1),
        task_lifecycle_failure_event(
            sequence=29,
            law_id=law_id,
            task_id="task-child-1",
            spawn_index=1,
            failure_id="child-failure-1",
            primary_failure_id="child-failure-0",
            failure_role="child_suppressed",
            suppression_index=0,
        ),
        task_lifecycle_failure_event(
            sequence=43,
            law_id=law_id,
            task_id="task-child-0",
            spawn_index=0,
            failure_id="child-failure-0",
            primary_failure_id="child-failure-0",
            failure_role="child_primary",
            suppression_index=None,
        ),
        task_join_failure_event(
            sequence=44,
            law_id=law_id,
            task_id="task-child-1",
            spawn_index=1,
            join_index=0,
            failure_id="child-failure-1",
            failure_role="child_suppressed",
            suppression_index=0,
        ),
        task_join_failure_event(
            sequence=45,
            law_id=law_id,
            task_id="task-child-0",
            spawn_index=0,
            join_index=1,
            failure_id="child-failure-0",
            failure_role="child_primary",
            suppression_index=None,
        ),
    ]
    normalize_source_order(record)
    fixture["expected"] = "admitted"
    document["positive_fixtures"].append(fixture)


def bind_actor_and_task_negatives(document: dict[str, object]) -> None:
    actor_positive = document["positive_fixtures"][0]
    overlap = copy.deepcopy(actor_positive)
    overlap["fixture_id"] = "MIR-NEG-ACTOR-TURN-OVERLAP-001"
    overlap.pop("expected", None)
    overlap["expected_errors"] = ["MIR_ACTOR_TURN_OVERLAP"]
    overlap["record"]["actor_isolation"] = [
        event
        for event in overlap["record"]["actor_isolation"]
        if not (event["kind"] == "actor_lifecycle" and event["sequence"] == 33)
    ]
    lifecycle = {
        int(event["sequence"]): event
        for event in overlap["record"]["actor_isolation"]
        if event["kind"] == "actor_lifecycle"
    }
    # Turn 1 starts after its dequeue but before turn 0 releases the same
    # state-region authority. Both admissions remain otherwise well ordered.
    lifecycle[37].update(
        phase="turn_finish",
        turn_id="turn-0",
        turn_index=0,
        message_id="message-0",
        transfer_id="transfer-0",
        channel_sequence=0,
        state_region_authority="released",
    )
    overlap["record"]["actor_isolation"].append(
        actor_lifecycle_event(
            sequence=43,
            law_id=str(overlap["record"]["law_id"]),
            phase="turn_finish",
            turn_id="turn-1",
            turn_index=1,
            message_id="message-1",
            channel_sequence=1,
            transfer_id="transfer-1",
            state_region_authority="released",
        )
    )
    overlap["record"]["actor_isolation"].sort(key=lambda event: int(event["sequence"]))
    normalize_source_order(overlap["record"])

    task_positive = next(
        fixture
        for fixture in document["positive_fixtures"]
        if fixture["fixture_id"] == "MIR-POS-TASK-SPAWN-ORDER-001"
    )
    wrong_primary = copy.deepcopy(task_positive)
    wrong_primary["fixture_id"] = "MIR-NEG-TASK-COMPLETION-PRIMARY-001"
    wrong_primary.pop("expected", None)
    wrong_primary["expected_errors"] = ["MIR_TASK_PRIMARY_NOT_MIN_SPAWN_INDEX"]
    for event in wrong_primary["record"]["task_scope"]:
        if event["kind"] == "task_lifecycle":
            event["primary_failure_id"] = "child-failure-1"
        if event.get("task_id") == "task-child-1" and event["kind"] in {"task_lifecycle", "task_join"}:
            event["failure_role"] = "child_primary"
            event["suppression_index"] = None
        if event.get("task_id") == "task-child-0" and event["kind"] in {"task_lifecycle", "task_join"}:
            event["failure_role"] = "child_suppressed"
            event["suppression_index"] = 0
    normalize_source_order(wrong_primary["record"])
    document["negative_fixtures"].extend([overlap, wrong_primary])


def bind_synchronization_negatives(document: dict[str, object]) -> None:
    positive = document["positive_fixtures"][0]
    retained = [
        fixture
        for fixture in document["negative_fixtures"]
        if fixture["fixture_id"]
        not in {"MIR-NEG-SYNC-RELEASE-001", "MIR-NEG-SYNC-SUSPEND-001"}
    ]

    missing_release = copy.deepcopy(positive)
    missing_release["fixture_id"] = "MIR-NEG-SYNC-RELEASE-001"
    removed_release_ids = {
        event["event_id"]
        for event in missing_release["record"]["synchronization_events"]
        if event["operation"] == "lock_release"
    }
    missing_release["record"]["synchronization_events"] = [
        event
        for event in missing_release["record"]["synchronization_events"]
        if event["event_id"] not in removed_release_ids
    ]
    missing_release["record"]["source_order"] = [
        event_id
        for event_id in missing_release["record"]["source_order"]
        if event_id not in removed_release_ids
    ]
    missing_release.pop("expected", None)
    missing_release["expected_errors"] = ["MIR_SYNCHRONIZATION_RELEASE_REQUIRED"]

    suspending_lock = copy.deepcopy(positive)
    suspending_lock["fixture_id"] = "MIR-NEG-SYNC-SUSPEND-001"
    lock_event = next(
        event
        for event in suspending_lock["record"]["synchronization_events"]
        if event["operation"] == "lock_acquire"
    )
    lock_event["operation"] = "lock_suspend"
    suspending_lock.pop("expected", None)
    suspending_lock["expected_errors"] = ["MIR_SYNC_SCOPED_SUSPENSION_FORBIDDEN"]

    document["negative_fixtures"] = [*retained, missing_release, suspending_lock]
    document["negative_fixture_count"] = len(document["negative_fixtures"])


def validate_document(document: dict[str, object]) -> None:
    fixtures = [*document["positive_fixtures"], *document["negative_fixtures"]]
    fixture_ids = [str(fixture["fixture_id"]) for fixture in fixtures]
    if len(fixture_ids) != len(set(fixture_ids)):
        raise ValueError("fixture_id values must be unique")
    if document.get("product_runtime_execution") != "NOT_RUN":
        raise ValueError("product runtime execution must remain NOT_RUN")

    profile_counts = {profile_name: 0 for profile_name in PATTERN_PROFILES}

    for fixture in fixtures:
        record = fixture["record"]
        fixture_id = str(fixture["fixture_id"])
        profile_name = PATTERN_PROFILE_BY_FIXTURE[fixture_id]
        profile = PATTERN_PROFILES[profile_name]
        profile_counts[profile_name] += 1
        trace = record["pattern_trace"]
        if [event["phase"] for event in trace] != [phase for phase, _ in profile["phases"]]:
            raise ValueError(f"{fixture_id}: Pattern phase profile is not exact")
        if [event["outcome"] for event in trace] != [outcome for _, outcome in profile["phases"]]:
            raise ValueError(f"{fixture_id}: Pattern outcome profile is not exact")
        if not all(
            event["attempt_disposition"] == profile_name
            and event["dpm_fixture_id"] == profile["dpm_fixture_id"]
            and event["context_id"] == profile["context_id"]
            for event in trace
        ):
            raise ValueError(f"{fixture_id}: Pattern authority binding is not exact")
        if profile_name in {
            "PATTERN_MISMATCH_PRECOMMIT",
            "GUARD_FALSE_PRECOMMIT",
            "GUARDED_LET_ELSE_TRANSFER",
            "FOR_LET_CANDIDATE_FILTERED",
        } and not all(
            event["pattern_move_count"] == 0
            and event["final_binder_ids"] == []
            and event["consuming"] is False
            and all(count == 0 for count in event["precommit_zero_counts"].values())
            for event in trace
        ):
            raise ValueError(f"{fixture_id}: failed Pattern attempt is not precommit-zero")
        if profile_name in {"PATTERN_MISMATCH_PRECOMMIT", "GUARDED_LET_ELSE_TRANSFER"} and any(
            event["phase"] in {"probe_bind", "guard_evaluate", "atomic_commit", "final_bind", "body"}
            for event in trace
        ):
            raise ValueError(f"{fixture_id}: structural mismatch advanced past its terminal edge")
        if profile_name in {"GUARD_FALSE_PRECOMMIT", "FOR_LET_CANDIDATE_FILTERED"} and any(
            event["phase"] in {"atomic_commit", "final_bind", "body"}
            for event in trace
        ):
            raise ValueError(f"{fixture_id}: false guard advanced past its terminal edge")
        events = list(iter_events(record))
        event_ids = [str(event["event_id"]) for event in events]
        sequences = [int(event["sequence"]) for event in events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError(f"{fixture['fixture_id']}: duplicate event_id")
        if len(sequences) != len(set(sequences)):
            raise ValueError(f"{fixture['fixture_id']}: duplicate sequence")
        expected_order = [
            str(event["event_id"])
            for event in sorted(events, key=lambda event: int(event["sequence"]))
        ]
        if (
            fixture["fixture_id"] != "MIR-NEG-SOURCE-ORDER-001"
            and record["source_order"] != expected_order
        ):
            raise ValueError(f"{fixture['fixture_id']}: source_order is not exact")
        for event in record["actor_isolation"]:
            if event["kind"] == "actor_enqueue" and not (
                event["capacity_outcome"] == "admitted"
                and event["ownership_commit_count"] == 1
                and event["channel_sequence"] is not None
                and event["transfer_disposition"] in {"receiver_owned", "shared_evidence"}
            ):
                raise ValueError(f"{fixture['fixture_id']}: actor_enqueue is not an admitted commit")
            if event["kind"] == "actor_lifecycle" and event["phase"] == "admission_rejected":
                if not (
                    event["channel_sequence"] is None
                    and event["ownership_commit_state"] == "precommit"
                    and event["ownership_commit_count"] == 0
                    and event["transfer_disposition"] == "sender_retained"
                ):
                    raise ValueError(f"{fixture['fixture_id']}: rejected admission committed ownership")

    if set(profile_counts.values()) != {2}:
        raise ValueError(f"Pattern evidence must bind exactly two fixtures per profile: {profile_counts}")

    actor_positive = document["positive_fixtures"][0]["record"]["actor_isolation"]
    actor_phases = [event["phase"] for event in actor_positive if event["kind"] == "actor_lifecycle"]
    if actor_phases != [
        "turn_start",
        "turn_suspend",
        "turn_resume",
        "turn_finish",
        "turn_start",
        "turn_finish",
    ]:
        raise ValueError("positive Actor lifecycle sequence is not exact")
    task_fixture = next(
        fixture
        for fixture in document["positive_fixtures"]
        if fixture["fixture_id"] == "MIR-POS-TASK-SPAWN-ORDER-001"
    )
    completions = [
        event
        for event in task_fixture["record"]["task_scope"]
        if event["kind"] == "task_lifecycle" and event["phase"] == "scope_terminal"
    ]
    if not (
        [event["task_id"] for event in completions] == ["task-child-1", "task-child-0"]
        and all(event["primary_failure_id"] == "child-failure-0" for event in completions)
    ):
        raise ValueError("task completion-order evidence does not preserve spawn-index primary")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    document = json.loads(TARGET.read_text(encoding="utf-8"))
    document["positive_fixtures"] = [
        fixture
        for fixture in document["positive_fixtures"]
        if fixture["fixture_id"] not in GENERATED_POSITIVE_IDS
    ]
    document["negative_fixtures"] = [
        fixture
        for fixture in document["negative_fixtures"]
        if fixture["fixture_id"] not in GENERATED_NEGATIVE_IDS
    ]
    document["event_kind_count"] = 23
    stacks = document["stack_kind_contracts"]
    stacks["task_scope"] = ["task_spawn", "task_join", "task_lifecycle"]
    stacks["actor_isolation"] = ["actor_enqueue", "actor_dequeue", "actor_lifecycle"]
    stacks["pattern_trace"] = ["pattern_phase"]
    stacks["synchronization_events"] = ["synchronization"]
    records = [*document["positive_fixtures"], *document["negative_fixtures"]]
    changed = sum(bind_record(fixture["record"]) for fixture in records)
    bind_actor_rejection_positive(document)
    bind_task_order_positive(document)
    bind_synchronization_negatives(document)
    bind_actor_and_task_negatives(document)
    bind_pattern_evidence(document)
    document["positive_fixture_count"] = len(document["positive_fixtures"])
    document["negative_fixture_count"] = len(document["negative_fixtures"])
    validate_document(document)
    rendered = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    rendered_bytes = rendered.encode("utf-8")
    pending = rendered_bytes != TARGET.read_bytes()
    if args.write and pending:
        TARGET.write_bytes(rendered_bytes)
    mode = "WRITE" if args.write else "CHECK"
    print(f"MIR_COHERENCE_EVENT_BIND_{mode}: records={changed} pending={pending}")
    return 1 if (pending and not args.write) else 0


if __name__ == "__main__":
    raise SystemExit(main())
