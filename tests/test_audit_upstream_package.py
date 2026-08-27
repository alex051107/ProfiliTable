from __future__ import annotations

import ast
import csv
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import audit_upstream_package as audit  # noqa: E402


class AuditUpstreamPackageTests(unittest.TestCase):
    def test_flatten_types_enumerates_nested_fields_and_list_elements(self) -> None:
        observed = audit.flatten_types(
            {"target_en": "task", "task_type": ["Filtering", "Join"], "nested": {"enabled": True}}
        )
        self.assertIn(("$", "object"), observed)
        self.assertIn(("$.target_en", "string"), observed)
        self.assertIn(("$.task_type", "array"), observed)
        self.assertIn(("$.task_type[]", "string"), observed)
        self.assertIn(("$.nested.enabled", "boolean"), observed)

    def test_duplicate_metadata_keys_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "task_meta.json"
            path.write_text('{"target_en":"one","target_en":"two","target_zh":"二"}', encoding="utf-8")
            metadata, status, duplicate_keys = audit.load_json_object(path)
        self.assertEqual("two", metadata["target_en"])
        self.assertEqual("OK_WITH_DUPLICATE_KEYS", status)
        self.assertEqual(["target_en"], duplicate_keys)

    def test_archive_path_audit_flags_traversal_without_extracting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "unsafe.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("data/ok.txt", "ok")
                archive.writestr("../escape.txt", "blocked")
            result = audit.audit_archive(archive_path, None)
        self.assertEqual(["../escape.txt"], result["traversal_paths"])
        self.assertEqual(2, result["file_count"])
        self.assertEqual(64, len(result["sha256"]))

    def test_trace_and_checkpoint_identifier_tokens_without_traceback_false_positive(self) -> None:
        node = ast.parse("import traceback\ntraceback.print_exc()\n").body[1].value
        kinds = audit.classify_static_evidence(node, "traceback.print_exc", "traceback.print_exc()")
        self.assertNotIn("execution_trace", kinds)
        for symbol in ("execution_trace", "trace_path", "executionTrace", "lineage_reader"):
            node = ast.parse(f"{symbol}()\n").body[0].value
            kinds = audit.classify_static_evidence(node, symbol, f"{symbol}()")
            self.assertIn("execution_trace", kinds)
        for symbol in ("checkpoint_path", "snapshot_dir", "intermediate_state"):
            node = ast.parse(f"{symbol}()\n").body[0].value
            kinds = audit.classify_static_evidence(node, symbol, f"{symbol}()")
            self.assertIn("intermediate_state", kinds)

    def test_run_audit_fails_closed_on_same_size_extraction_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            extracted_root = root / "extracted"
            benchmarks_root = extracted_root / "data" / "benchmarks"
            output_dir = root / "audit-output"
            source_root.mkdir()
            (source_root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
            task_dir = benchmarks_root / "NL2Op" / "T0001_filter"
            self._write_task(
                task_dir,
                target_en="Filter rows and output CSV.",
                target_zh="过滤并输出 CSV。",
                raw_name="input.csv",
                raw_value="id,amount\n1,9\n",
                expected_value="id,amount\n1,9\n",
            )
            archive_path = source_root / "data.zip"
            self._zip_tree(extracted_root, archive_path)
            (task_dir / "raw" / "input.csv").write_text("id,amount\n1,8\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "extraction_crc_mismatches"):
                audit.run_audit(
                    archive_path=archive_path,
                    extracted_root=extracted_root,
                    benchmarks_root=benchmarks_root,
                    output_dir=output_dir,
                    source_repo="https://example.invalid/repo",
                    source_commit="a" * 40,
                    archive_git_blob="b" * 40,
                    source_root=source_root,
                    audit_timestamp="2026-08-27T12:00:00+00:00",
                )
            self.assertFalse(output_dir.exists())

    def test_run_audit_writes_recomputable_inventory_and_draft_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            extracted_root = root / "extracted"
            benchmarks_root = extracted_root / "data" / "benchmarks"
            output_dir = root / "audit-output"
            source_root.mkdir()
            (source_root / "LICENSE").write_text("MIT License\n", encoding="utf-8")

            self._write_task(
                benchmarks_root / "NL2Op" / "T0001_filter",
                target_en=(
                    "Filter rows whose amount is below 10; retain the original column order; "
                    "output UTF-8 CSV."
                ),
                target_zh="过滤并保留列顺序。",
                raw_name="formatted_input.csv",
                raw_value="id,amount\n1,9\n",
                expected_value="id,amount\n1,9\n",
                extra_metadata={"task_type": ["Filtering"], "score_rule": "exact"},
            )
            self._write_task(
                benchmarks_root / "NL2Dag" / "T0001_pipeline",
                target_en="Keep only valid rows and output CSV.",
                target_zh="仅保留有效行并输出 CSV。",
                raw_name="input.csv",
                raw_value="id,amount\n2,20\n",
                expected_value="id,amount\n2,20\n",
            )

            archive_path = source_root / "data.zip"
            self._zip_tree(extracted_root, archive_path)
            result = audit.run_audit(
                archive_path=archive_path,
                extracted_root=extracted_root,
                benchmarks_root=benchmarks_root,
                output_dir=output_dir,
                source_repo="https://example.invalid/repo",
                source_commit="a" * 40,
                archive_git_blob="b" * 40,
                source_root=source_root,
                audit_timestamp="2026-08-27T12:00:00+00:00",
            )

            self.assertEqual(2, result["task_count"])
            self.assertEqual({"NL2Dag": 1, "NL2Op": 1}, result["mode_counts"])
            inventory = self._read_tsv(output_dir / "upstream_inventory.tsv")
            self.assertEqual(2, len(inventory))
            self.assertTrue(all(row["task_id_occurrences_all_modes"] == "2" for row in inventory))
            self.assertTrue(all(row["duplicate_id_scope"] == "across_modes" for row in inventory))
            op_row = next(row for row in inventory if row["split_or_mode"] == "NL2Op")
            self.assertEqual("true", op_row["raw_dir_present"])
            self.assertEqual("1", op_row["raw_file_count"])
            self.assertEqual("true", op_row["expected_dir_present"])
            self.assertEqual("OK", op_row["eval_ast_parse_status"])
            self.assertIn("$.score_rule:string", op_row["task_meta_type_map"])
            self.assertIn("raw/formatted_input.csv=expected/gt.csv", op_row["raw_expected_parsed_equal_pairs"])
            self.assertEqual("raw/formatted_input.csv", op_row["derived_raw_filename_hints"])

            coverage = self._read_tsv(output_dir / "oracle_coverage.DRAFT.tsv")
            self.assertGreaterEqual(len(coverage), 2)
            self.assertTrue(all(row["coverage"] == "DRAFT_UNREVIEWED" for row in coverage))
            self.assertTrue(
                all(
                    row["requirement_text"] == "[WITHHELD_PENDING_DATA_LICENSE_REVIEW]"
                    for row in coverage
                )
            )
            self.assertTrue(any("eval.py:" in row["eval_py_checks"] for row in coverage))
            self.assertTrue(all(row["pilot_eligible"] == "UNASSESSED" for row in coverage))

            manifest = {row["field"]: row for row in self._read_tsv(output_dir / "package_manifest.tsv")}
            self.assertEqual("2", manifest["task_count_total"]["value"])
            self.assertEqual("NL2Dag:1|NL2Op:1", manifest["task_count_by_mode"]["value"])
            self.assertEqual("DATA_INSUFFICIENT", manifest["data_license_status"]["value"])
            self.assertEqual("withheld", manifest["requirement_text_in_tracked_draft"]["value"])
            self.assertEqual("withheld", manifest["evaluator_source_snippets_in_tracked_draft"]["value"])
            self.assertEqual("true", manifest["extracted_crc_match"]["value"])
            self.assertEqual(64, len(manifest["data_zip_sha256"]["value"]))

            rendered = "\n".join(path.read_text(encoding="utf-8") for path in output_dir.iterdir())
            self.assertNotIn("1,9", rendered)
            self.assertNotIn("2,20", rendered)
            self.assertNotIn("Filter rows whose amount is below 10", rendered)
            self.assertNotIn("oracle-secret-42", rendered)

            outside_benchmarks = root / "unverified-benchmarks"
            outside_benchmarks.mkdir()
            with self.assertRaisesRegex(ValueError, "verified extracted_root"):
                audit.run_audit(
                    archive_path=archive_path,
                    extracted_root=extracted_root,
                    benchmarks_root=outside_benchmarks,
                    output_dir=root / "other-output",
                    source_repo="https://example.invalid/repo",
                    source_commit="a" * 40,
                    archive_git_blob="b" * 40,
                    source_root=source_root,
                    audit_timestamp="2026-08-27T12:00:00+00:00",
                )

    @staticmethod
    def _write_task(
        task_dir: Path,
        *,
        target_en: str,
        target_zh: str,
        raw_name: str,
        raw_value: str,
        expected_value: str,
        extra_metadata: dict[str, object] | None = None,
    ) -> None:
        (task_dir / "raw").mkdir(parents=True)
        (task_dir / "expected").mkdir()
        metadata: dict[str, object] = {"target_en": target_en, "target_zh": target_zh}
        metadata.update(extra_metadata or {})
        (task_dir / "task_meta.json").write_text(
            json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
        )
        (task_dir / "raw" / raw_name).write_text(raw_value, encoding="utf-8")
        (task_dir / "expected" / "gt.csv").write_text(expected_value, encoding="utf-8")
        (task_dir / "gen_data.py").write_text("# synthetic generator fixture\n", encoding="utf-8")
        (task_dir / "eval.py").write_text(
            "from pathlib import Path\n"
            "import csv\n"
            "GT_PATH = Path(__file__).parent / 'expected' / 'gt.csv'\n"
            "RAW_PATH = Path(__file__).parent / 'raw' / 'input.csv'\n"
            "GOLD_LITERAL = 'oracle-secret-42'\n"
            "def score(output):\n"
            "    with GT_PATH.open(encoding='utf-8') as handle:\n"
            "        expected = list(csv.reader(handle))\n"
            "    with Path(output).open(encoding='utf-8') as handle:\n"
            "        predicted = list(csv.reader(handle))\n"
            "    if len(predicted) != len(expected):\n"
            "        return 0.0\n"
            "    if predicted[0] != expected[0]:\n"
            "        return 0.0\n"
            "    return float(predicted == expected)\n",
            encoding="utf-8",
        )

    @staticmethod
    def _zip_tree(root: Path, archive_path: Path) -> None:
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob("*")):
                name = path.relative_to(root).as_posix()
                if path.is_dir():
                    archive.writestr(name + "/", "")
                else:
                    archive.write(path, name)

    @staticmethod
    def _read_tsv(path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle, dialect="excel-tab"))


if __name__ == "__main__":
    unittest.main()
