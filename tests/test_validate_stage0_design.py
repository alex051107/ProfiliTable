from __future__ import annotations

import copy
import csv
import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "validate_stage0_design.py"
CONTRACTS_PATH = REPO_ROOT / "research" / "stage0" / "STAGE0_TASK_CONTRACTS.PROPOSED.json"
QUEUE_PATH = REPO_ROOT / "research" / "stage0" / "STAGE0_APPROVAL_QUEUE.PROPOSED.tsv"

spec = importlib.util.spec_from_file_location("validate_stage0_design", SCRIPT_PATH)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def load_contracts() -> dict:
    return json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))


def load_queue() -> tuple[list[str], list[dict[str, str]]]:
    with QUEUE_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


class Stage0DesignValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contracts = load_contracts()
        self.fields, self.rows = load_queue()

    def errors(self, contracts: dict | None = None, rows: list[dict[str, str]] | None = None) -> list[str]:
        value = contracts if contracts is not None else self.contracts
        queue_rows = rows if rows is not None else self.rows
        issues = validator.validate_contracts(value)
        issues.extend(validator.validate_queue(self.fields, queue_rows))
        issues.extend(validator.validate_queue_bindings(value, queue_rows))
        issues.extend(validator.validate_gate_consistency(value, queue_rows))
        return issues

    def test_shipped_design_is_valid_but_not_ready(self) -> None:
        summary, errors = validator.validate_files(CONTRACTS_PATH, QUEUE_PATH)
        self.assertEqual(errors, [])
        self.assertEqual(summary["artifact_class"], "DESIGN_PROPOSAL")
        self.assertEqual(summary["gate_status"], "NOT_READY")
        self.assertEqual(summary["task_count"], 4)
        self.assertEqual(summary["qualification_counts"], {"HOLD": 1, "PROVISIONAL": 3})
        self.assertEqual(summary["oracle_count"], 14)
        self.assertEqual(summary["checkpoint_count"], 12)
        self.assertEqual(summary["approval_count"], 18)
        self.assertEqual(summary["pending_approval_count"], 18)

    def test_proposal_rejects_gate_transition_and_generated_schedule(self) -> None:
        contracts = copy.deepcopy(self.contracts)
        contracts["stage0_gate"]["status"] = "GO"
        contracts["data_rights_status"] = "APPROVED_FOR_PLANNED_USE"
        contracts["experiment_design"]["run_order"] = {"status": "GENERATED", "seed": True}
        rows = copy.deepcopy(self.rows)
        rows[0]["status"] = "APPROVED"
        rows[0]["decision"] = "APPROVE"
        rows[0]["decided_by"] = "someone"
        rows[0]["decided_at"] = "2026-08-27T00:00:00Z"
        rows[0]["rationale"] = "fake approval"
        rows[0]["evidence_ref"] = "unverified"
        errors = self.errors(contracts, rows)
        self.assertTrue(any("cannot authorize GO" in error for error in errors))
        self.assertTrue(any("must remain DATA_INSUFFICIENT" in error for error in errors))
        self.assertTrue(any("cannot contain a generated schedule" in error for error in errors))
        self.assertTrue(any("seed must be null" in error for error in errors))
        self.assertTrue(any("must remain PENDING" in error for error in errors))
        self.assertTrue(any("cannot record or authorize" in error for error in errors))

    def test_reference_output_rejected_as_property_oracle_dependency(self) -> None:
        contracts = copy.deepcopy(self.contracts)
        contracts["tasks"][0]["oracles"][0]["input_role_ids"].append("EXPECTED_OUTPUT")
        contracts["tasks"][0]["oracles"][0]["witness"] = "Compare against expected/gt.csv"
        errors = self.errors(contracts)
        self.assertTrue(any("unapproved roles" in error for error in errors))
        self.assertTrue(any("forbidden reference dependency token" in error for error in errors))

    def test_gold_artifact_class_and_self_approval_are_rejected(self) -> None:
        contracts = copy.deepcopy(self.contracts)
        contracts["artifact_class"] = "GOLD_ANNOTATION"
        contracts["tasks"][0]["human_requirement_review"] = "APPROVED"
        errors = self.errors(contracts)
        self.assertTrue(any("DESIGN_PROPOSAL" in error for error in errors))
        self.assertTrue(any("cannot self-approve" in error for error in errors))

    def test_duplicate_clause_and_unknown_oracle_are_rejected(self) -> None:
        contracts = copy.deepcopy(self.contracts)
        task = contracts["tasks"][0]
        duplicate = copy.deepcopy(task["clauses"][0])
        duplicate["oracle_ids"] = ["NOT_AN_ORACLE"]
        task["clauses"].append(duplicate)
        errors = self.errors(contracts)
        self.assertTrue(any("duplicate clause IDs" in error for error in errors))
        self.assertTrue(any("unknown IDs" in error for error in errors))

    def test_incomplete_or_formula_like_approval_queue_is_rejected(self) -> None:
        rows = copy.deepcopy(self.rows[:-1])
        rows[0]["decision_prompt"] = "=HYPERLINK(\"https://example.invalid\")"
        requirements = next(row for row in rows if row["approval_id"] == "F_REQUIREMENTS")
        requirements["subject_ids"] = requirements["subject_ids"].replace(
            "|F_C6_RETAINED_VALUES", ""
        )
        errors = self.errors(rows=rows)
        self.assertTrue(any("expected exactly 18" in error for error in errors))
        self.assertTrue(any("spreadsheet-formula-leading" in error for error in errors))
        self.assertTrue(any("subjects do not exactly match" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
