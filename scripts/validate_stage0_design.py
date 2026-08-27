#!/usr/bin/env python3
"""Validate the data-free Stage 0 design proposal and its human approval queue."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


UPSTREAM_COMMIT = "f023ec4b754555000a659b93fd514645c55e3cec"
PACKAGE_SHA256 = "a5c46f5c0d71a4886ed7c6cebb737814dff0587038f45bed58a40d9d96fafcb6"
EXPECTED_TASKS = {
    "NL2Op/T0114_filter_muti": "filter_revision",
    "NL2Op/T0074_wide_table_construction": "aggregation_grain",
    "NL2Op/T0011_incremental_deduplication": "latest_record",
    "NL2Op/T0047_multi_csv_union": "output_preservation",
}
EXPECTED_QUALIFICATIONS = {
    "NL2Op/T0114_filter_muti": "PROVISIONAL",
    "NL2Op/T0074_wide_table_construction": "PROVISIONAL",
    "NL2Op/T0011_incremental_deduplication": "PROVISIONAL",
    "NL2Op/T0047_multi_csv_union": "HOLD",
}
EXPECTED_APPROVAL_TYPES = {
    "DATA_RIGHTS": 1,
    "REQUIREMENT_INTERPRETATION": 4,
    "PROPERTY_ORACLE": 4,
    "CHECKPOINT_BOUNDARIES": 4,
    "MUTATION_SEMANTICS": 4,
    "STAGE0_GO_PIVOT_STOP": 1,
}
QUEUE_FIELDS = [
    "approval_id",
    "approval_type",
    "task_key",
    "subject_ids",
    "decision_prompt",
    "codex_recommendation",
    "status",
    "decision",
    "owner",
    "decided_by",
    "decided_at",
    "rationale",
    "evidence_ref",
    "evidence_required",
    "blocked_action",
]
ALLOWED_COVERAGE = {"FULL", "PARTIAL", "NONE", "UNCERTAIN"}
ROLE_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
FORBIDDEN_ROLE_FRAGMENTS = (
    "EXPECTED",
    "GROUND_TRUTH",
    "NATIVE_EVALUATOR",
    "MUTATION_LEDGER",
    "GOLD",
)
FORBIDDEN_ORACLE_TEXT_TOKENS = (
    "expected/",
    "ground truth",
    "gt.csv",
    "gt.jsonl",
    "eval.py",
    "native evaluator",
    "mutation ledger",
    "gold diagnosis",
)


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_contracts(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError("contracts root must be a JSON object")
    return value


def load_queue(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    return fields, rows


def require_nonempty_string(
    value: Any, location: str, errors: list[str], *, max_length: int | None = None
) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{location}: expected a nonempty string")
        return
    if max_length is not None and len(value) > max_length:
        errors.append(f"{location}: exceeds {max_length} characters")
    if "\n" in value or "\r" in value:
        errors.append(f"{location}: embedded line break is not allowed")


def duplicate_values(values: Iterable[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def validate_contracts(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "0.1":
        errors.append("schema_version: expected 0.1")
    if data.get("artifact_class") != "DESIGN_PROPOSAL":
        errors.append("artifact_class: must remain DESIGN_PROPOSAL")
    if data.get("status") != "CODEX_PROPOSED":
        errors.append("status: must remain CODEX_PROPOSED until human review")
    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source: expected an object")
        source = {}
    if source.get("upstream_commit") != UPSTREAM_COMMIT:
        errors.append("source.upstream_commit: fixed source changed")
    if source.get("package_sha256") != PACKAGE_SHA256:
        errors.append("source.package_sha256: fixed package changed")
    if data.get("data_rights_status") != "DATA_INSUFFICIENT":
        errors.append("data_rights_status: proposed artifact must remain DATA_INSUFFICIENT")

    gate = data.get("stage0_gate")
    if not isinstance(gate, dict):
        errors.append("stage0_gate: expected an object")
        gate = {}
    if gate.get("status") != "NOT_READY":
        errors.append("stage0_gate.status: proposed artifact cannot authorize GO, PIVOT, or STOP")
    reasons = gate.get("blocking_reasons")
    if not isinstance(reasons, list) or not reasons:
        errors.append("stage0_gate.blocking_reasons: NOT_READY requires a nonempty list")

    design = data.get("experiment_design")
    if not isinstance(design, dict):
        errors.append("experiment_design: expected an object")
        design = {}
    if design.get("blocking_factor") != "base task":
        errors.append("experiment_design.blocking_factor: expected base task")
    run_order = design.get("run_order")
    if not isinstance(run_order, dict):
        errors.append("experiment_design.run_order: expected an object")
    else:
        if run_order.get("status") != "NOT_GENERATED":
            errors.append("experiment_design.run_order: proposed artifact cannot contain a generated schedule")
        if run_order.get("seed") is not None:
            errors.append("experiment_design.run_order: seed must be null before generation")
    if design.get("replication_claim") != "NONE_STAGE0_CONSTRUCT_VALIDITY":
        errors.append("experiment_design.replication_claim: statistical replication is not established")

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks: expected a list")
        tasks = []
    task_keys = [task.get("task_key", "") for task in tasks if isinstance(task, dict)]
    if set(task_keys) != set(EXPECTED_TASKS) or len(task_keys) != len(EXPECTED_TASKS):
        errors.append("tasks: expected exactly the four Phase 2 candidate task keys")
    duplicates = duplicate_values(task_keys)
    if duplicates:
        errors.append(f"tasks: duplicate task keys {duplicates}")

    for index, task in enumerate(tasks):
        location = f"tasks[{index}]"
        if not isinstance(task, dict):
            errors.append(f"{location}: expected an object")
            continue
        task_key = task.get("task_key")
        if task_key in EXPECTED_TASKS and task.get("family") != EXPECTED_TASKS[task_key]:
            errors.append(f"{location}.family: does not match the frozen task role")
        if task_key in EXPECTED_QUALIFICATIONS and task.get("qualification") != EXPECTED_QUALIFICATIONS[task_key]:
            errors.append(f"{location}.qualification: proposed disposition changed")
        if task.get("design_status") != "CODEX_PROPOSED":
            errors.append(f"{location}.design_status: must remain CODEX_PROPOSED")
        if task.get("human_requirement_review") != "UNREVIEWED":
            errors.append(f"{location}.human_requirement_review: proposal cannot self-approve")
        source_path = task.get("source_task_path")
        require_nonempty_string(source_path, f"{location}.source_task_path", errors)
        if isinstance(source_path, str):
            pure = PurePosixPath(source_path)
            if pure.is_absolute() or ".." in pure.parts:
                errors.append(f"{location}.source_task_path: must be a confined relative path")
            if not source_path.startswith("data/benchmarks/NL2Op/"):
                errors.append(f"{location}.source_task_path: unexpected source namespace")

        steps = task.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{location}.steps: expected a nonempty list")
            steps = []
        step_ids = [step.get("step_id", "") for step in steps if isinstance(step, dict)]
        if duplicate_values(step_ids):
            errors.append(f"{location}.steps: duplicate step IDs")
        for step_index, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"{location}.steps[{step_index}]: expected an object")
                continue
            require_nonempty_string(step.get("step_id"), f"{location}.steps[{step_index}].step_id", errors)
            require_nonempty_string(
                step.get("action_summary"),
                f"{location}.steps[{step_index}].action_summary",
                errors,
                max_length=240,
            )

        input_roles = task.get("oracle_input_roles")
        if not isinstance(input_roles, list) or not input_roles:
            errors.append(f"{location}.oracle_input_roles: expected a nonempty list")
            input_roles = []
        if duplicate_values(str(role) for role in input_roles):
            errors.append(f"{location}.oracle_input_roles: duplicate role IDs")
        for role in input_roles:
            if not isinstance(role, str) or not ROLE_ID_PATTERN.fullmatch(role):
                errors.append(f"{location}.oracle_input_roles: invalid role ID {role!r}")
                continue
            if any(fragment in role for fragment in FORBIDDEN_ROLE_FRAGMENTS):
                errors.append(f"{location}.oracle_input_roles: forbidden role ID {role!r}")

        oracles = task.get("oracles")
        if not isinstance(oracles, list) or not oracles:
            errors.append(f"{location}.oracles: expected a nonempty list")
            oracles = []
        oracle_ids = [oracle.get("oracle_id", "") for oracle in oracles if isinstance(oracle, dict)]
        if duplicate_values(oracle_ids):
            errors.append(f"{location}.oracles: duplicate oracle IDs")
        for oracle_index, oracle in enumerate(oracles):
            oracle_location = f"{location}.oracles[{oracle_index}]"
            if not isinstance(oracle, dict):
                errors.append(f"{oracle_location}: expected an object")
                continue
            require_nonempty_string(oracle.get("oracle_id"), f"{oracle_location}.oracle_id", errors)
            if oracle.get("uses_expected_output") is not False:
                errors.append(f"{oracle_location}.uses_expected_output: must be false")
            if oracle.get("uses_native_evaluator") is not False:
                errors.append(f"{oracle_location}.uses_native_evaluator: must be false")
            if oracle.get("approval_status") != "UNREVIEWED":
                errors.append(f"{oracle_location}.approval_status: proposal cannot self-approve")
            role_ids = oracle.get("input_role_ids")
            if not isinstance(role_ids, list) or not role_ids:
                errors.append(f"{oracle_location}.input_role_ids: expected a nonempty list")
                role_ids = []
            unknown_roles = sorted(set(role_ids) - set(input_roles))
            if unknown_roles:
                errors.append(f"{oracle_location}.input_role_ids: unapproved roles {unknown_roles}")
            require_nonempty_string(
                oracle.get("property"), f"{oracle_location}.property", errors, max_length=420
            )
            require_nonempty_string(
                oracle.get("witness"), f"{oracle_location}.witness", errors, max_length=320
            )
            oracle_text = f"{oracle.get('property', '')} | {oracle.get('witness', '')}".lower()
            for token in FORBIDDEN_ORACLE_TEXT_TOKENS:
                if token in oracle_text:
                    errors.append(f"{oracle_location}: forbidden reference dependency token {token!r}")

        clauses = task.get("clauses")
        if not isinstance(clauses, list) or not clauses:
            errors.append(f"{location}.clauses: expected a nonempty list")
            clauses = []
        clause_ids = [clause.get("clause_id", "") for clause in clauses if isinstance(clause, dict)]
        if duplicate_values(clause_ids):
            errors.append(f"{location}.clauses: duplicate clause IDs")
        for clause_index, clause in enumerate(clauses):
            clause_location = f"{location}.clauses[{clause_index}]"
            if not isinstance(clause, dict):
                errors.append(f"{clause_location}: expected an object")
                continue
            require_nonempty_string(clause.get("clause_id"), f"{clause_location}.clause_id", errors)
            require_nonempty_string(
                clause.get("summary"), f"{clause_location}.summary", errors, max_length=260
            )
            if clause.get("native_evaluator_coverage") not in ALLOWED_COVERAGE:
                errors.append(f"{clause_location}.native_evaluator_coverage: unsupported value")
            if clause.get("human_review_status") != "UNREVIEWED":
                errors.append(f"{clause_location}.human_review_status: proposal cannot self-approve")
            references = clause.get("oracle_ids")
            if not isinstance(references, list) or not references:
                errors.append(f"{clause_location}.oracle_ids: expected a nonempty list")
            else:
                unknown = sorted(set(references) - set(oracle_ids))
                if unknown:
                    errors.append(f"{clause_location}.oracle_ids: unknown IDs {unknown}")

        checkpoints = task.get("checkpoints")
        if not isinstance(checkpoints, list) or not checkpoints:
            errors.append(f"{location}.checkpoints: expected a nonempty list")
            checkpoints = []
        checkpoint_ids = [
            checkpoint.get("checkpoint_id", "")
            for checkpoint in checkpoints
            if isinstance(checkpoint, dict)
        ]
        if duplicate_values(checkpoint_ids):
            errors.append(f"{location}.checkpoints: duplicate checkpoint IDs")
        for checkpoint_index, checkpoint in enumerate(checkpoints):
            checkpoint_location = f"{location}.checkpoints[{checkpoint_index}]"
            if not isinstance(checkpoint, dict):
                errors.append(f"{checkpoint_location}: expected an object")
                continue
            require_nonempty_string(
                checkpoint.get("checkpoint_id"), f"{checkpoint_location}.checkpoint_id", errors
            )
            if checkpoint.get("after_step") not in step_ids:
                errors.append(f"{checkpoint_location}.after_step: unknown step")
            if checkpoint.get("approval_status") != "UNREVIEWED":
                errors.append(f"{checkpoint_location}.approval_status: proposal cannot self-approve")
            observations = checkpoint.get("compact_observations")
            if not isinstance(observations, list) or not observations:
                errors.append(f"{checkpoint_location}.compact_observations: expected a nonempty list")
            references = checkpoint.get("oracle_ids")
            if not isinstance(references, list) or not references:
                errors.append(f"{checkpoint_location}.oracle_ids: expected a nonempty list")
            else:
                unknown = sorted(set(references) - set(oracle_ids))
                if unknown:
                    errors.append(f"{checkpoint_location}.oracle_ids: unknown IDs {unknown}")

        mutation = task.get("mutation_proposal")
        if not isinstance(mutation, dict):
            errors.append(f"{location}.mutation_proposal: expected an object")
        else:
            if mutation.get("status") not in {"CODEX_PROPOSED", "BLOCKED"}:
                errors.append(f"{location}.mutation_proposal.status: unsupported proposal status")
            if mutation.get("human_approval") != "UNREVIEWED":
                errors.append(f"{location}.mutation_proposal.human_approval: proposal cannot self-approve")
        ambiguities = task.get("ambiguities")
        if not isinstance(ambiguities, list) or not ambiguities:
            errors.append(f"{location}.ambiguities: at least one human decision is required")

    for text in iter_strings(data):
        if text.startswith("/Users/") or text.startswith("/private/tmp/") or ":\\" in text:
            errors.append("contracts: local absolute path detected")
            break

    return errors


def validate_queue(fields: list[str], rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if fields != QUEUE_FIELDS:
        errors.append(f"approval queue header: expected {QUEUE_FIELDS}, observed {fields}")
    if len(rows) != sum(EXPECTED_APPROVAL_TYPES.values()):
        errors.append("approval queue: expected exactly 18 gate decisions")
    ids = [row.get("approval_id", "") for row in rows]
    if duplicate_values(ids):
        errors.append("approval queue: duplicate approval IDs")
    counts = Counter(row.get("approval_type", "") for row in rows)
    if counts != Counter(EXPECTED_APPROVAL_TYPES):
        errors.append(f"approval queue: unexpected approval-type counts {dict(counts)}")
    task_scoped_types = {
        "REQUIREMENT_INTERPRETATION",
        "PROPERTY_ORACLE",
        "CHECKPOINT_BOUNDARIES",
        "MUTATION_SEMANTICS",
    }
    observed_pairs: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, 2):
        location = f"approval queue line {index}"
        if None in row:
            errors.append(f"{location}: extra TSV fields")
        for field in QUEUE_FIELDS:
            require_nonempty_string(row.get(field), f"{location}.{field}", errors)
        if row.get("status") != "PENDING":
            errors.append(f"{location}.status: proposed queue must remain PENDING")
        if row.get("decision") != "UNDECIDED":
            errors.append(f"{location}.decision: proposed queue must remain UNDECIDED")
        if row.get("owner") != "HUMAN_PM_OR_MENTOR":
            errors.append(f"{location}.owner: scientific gates require a human owner")
        for field in ("decided_by", "decided_at", "rationale", "evidence_ref"):
            if row.get(field) != "UNSET":
                errors.append(f"{location}.{field}: proposed queue must remain UNSET")
        approval_type = row.get("approval_type")
        task_key = row.get("task_key")
        if approval_type in task_scoped_types:
            if task_key not in EXPECTED_TASKS:
                errors.append(f"{location}.task_key: unknown task-scoped key")
            observed_pairs.add((approval_type, task_key))
        elif task_key != "GLOBAL":
            errors.append(f"{location}.task_key: global gate must use GLOBAL")
        for field, value in row.items():
            if field is None or value is None:
                continue
            if value[:1] in {"=", "+", "-", "@"}:
                errors.append(f"{location}.{field}: spreadsheet-formula-leading cell")
    expected_pairs = {
        (approval_type, task_key)
        for approval_type in task_scoped_types
        for task_key in EXPECTED_TASKS
    }
    if observed_pairs != expected_pairs:
        errors.append("approval queue: each task needs all four task-scoped decisions")
    return errors


def expected_approval_subjects(data: dict[str, Any]) -> dict[tuple[str, str], set[str]]:
    expected: dict[tuple[str, str], set[str]] = {
        ("DATA_RIGHTS", "GLOBAL"): {"DATA_RIGHTS_STATUS"},
        ("STAGE0_GO_PIVOT_STOP", "GLOBAL"): {"STAGE0_GATE"},
    }
    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return expected
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_key = task.get("task_key")
        if task_key not in EXPECTED_TASKS:
            continue

        def collect_ids(collection_name: str, id_field: str) -> set[str]:
            collection = task.get(collection_name)
            if not isinstance(collection, list):
                return set()
            return {
                item[id_field]
                for item in collection
                if isinstance(item, dict)
                and isinstance(item.get(id_field), str)
                and item[id_field]
            }

        expected[("REQUIREMENT_INTERPRETATION", task_key)] = collect_ids(
            "clauses", "clause_id"
        )
        expected[("PROPERTY_ORACLE", task_key)] = collect_ids("oracles", "oracle_id")
        expected[("CHECKPOINT_BOUNDARIES", task_key)] = collect_ids(
            "checkpoints", "checkpoint_id"
        )
        mutation = task.get("mutation_proposal")
        mutation_name = mutation.get("name") if isinstance(mutation, dict) else None
        expected[("MUTATION_SEMANTICS", task_key)] = (
            {mutation_name} if isinstance(mutation_name, str) and mutation_name else set()
        )
    return expected


def validate_queue_bindings(
    data: dict[str, Any], rows: list[dict[str, str]]
) -> list[str]:
    """Bind every proposed human decision to the exact contract objects it covers."""

    errors: list[str] = []
    expected = expected_approval_subjects(data)
    for index, row in enumerate(rows, 2):
        location = f"approval queue line {index}.subject_ids"
        approval_type = row.get("approval_type", "")
        task_key = row.get("task_key", "")
        value = row.get("subject_ids")
        if not isinstance(value, str) or not value:
            continue
        parts = value.split("|")
        if any(not part or any(character.isspace() for character in part) for part in parts):
            errors.append(f"{location}: IDs must be nonempty and contain no whitespace")
            continue
        if len(parts) != len(set(parts)):
            errors.append(f"{location}: duplicate subject IDs")
        key = (approval_type, task_key)
        if key not in expected:
            continue
        observed = set(parts)
        if observed != expected[key]:
            missing = sorted(expected[key] - observed)
            extra = sorted(observed - expected[key])
            errors.append(
                f"{location}: subjects do not exactly match the contract; "
                f"missing={missing}, extra={extra}"
            )
    return errors


def validate_gate_consistency(
    data: dict[str, Any], queue_rows: list[dict[str, str]]
) -> list[str]:
    """Ensure this proposal cannot be edited into an approval-bearing artifact."""

    errors: list[str] = []
    gate_status = (data.get("stage0_gate") or {}).get("status")
    transitioned_rows = [
        row.get("approval_id", "")
        for row in queue_rows
        if row.get("status") != "PENDING" or row.get("decision") != "UNDECIDED"
    ]
    if gate_status != "NOT_READY" or data.get("data_rights_status") != "DATA_INSUFFICIENT" or transitioned_rows:
        errors.append(
            "proposal lifecycle: this artifact cannot record or authorize a human gate transition"
        )
    return errors


def summarize(data: dict[str, Any], queue_rows: list[dict[str, str]]) -> dict[str, Any]:
    tasks = [task for task in data.get("tasks", []) if isinstance(task, dict)]
    return {
        "artifact_class": data.get("artifact_class"),
        "gate_status": (data.get("stage0_gate") or {}).get("status"),
        "data_rights_status": data.get("data_rights_status"),
        "task_count": len(tasks),
        "qualification_counts": dict(sorted(Counter(task.get("qualification") for task in tasks).items())),
        "clause_count": sum(len(task.get("clauses", [])) for task in tasks),
        "oracle_count": sum(len(task.get("oracles", [])) for task in tasks),
        "checkpoint_count": sum(len(task.get("checkpoints", [])) for task in tasks),
        "approval_count": len(queue_rows),
        "pending_approval_count": sum(row.get("status") == "PENDING" for row in queue_rows),
    }


def validate_files(contracts_path: Path, queue_path: Path) -> tuple[dict[str, Any], list[str]]:
    data = load_contracts(contracts_path)
    fields, rows = load_queue(queue_path)
    errors = validate_contracts(data)
    errors.extend(validate_queue(fields, rows))
    errors.extend(validate_queue_bindings(data, rows))
    errors.extend(validate_gate_consistency(data, rows))
    return summarize(data, rows), errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contracts",
        type=Path,
        default=Path("research/stage0/STAGE0_TASK_CONTRACTS.PROPOSED.json"),
    )
    parser.add_argument(
        "--approval-queue",
        type=Path,
        default=Path("research/stage0/STAGE0_APPROVAL_QUEUE.PROPOSED.tsv"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary, errors = validate_files(args.contracts, args.approval_queue)
    except (OSError, ValueError, json.JSONDecodeError, DuplicateKeyError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    payload = {"valid": not errors, "summary": summary, "errors": errors}
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
