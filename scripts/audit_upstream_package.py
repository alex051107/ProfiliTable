#!/usr/bin/env python3
"""Reproducible, static audit for a fixed ProfiliTable benchmark package.

This script never executes task generators, evaluators, or candidate code. It
records package identity, inventories task bundles, and creates a conservative
machine-generated draft that maps instruction clauses to static evaluator
signals. The draft is evidence for human review, not semantic ground truth.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import platform
import re
import stat
import sys
import unicodedata
import zipfile
import zlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence


AUDIT_SCHEMA_VERSION = "1.0"
DEFAULT_SOURCE_REPO = "https://github.com/Eularioal/ProfiliTable"
DEFAULT_SOURCE_COMMIT = "f023ec4b754555000a659b93fd514645c55e3cec"
DEFAULT_ARCHIVE_BLOB = "7c1e8be2cffe34386d94f7d5e5849b2ba096b4fd"

INVENTORY_COLUMNS = (
    "source_commit",
    "split_or_mode",
    "task_id",
    "task_key",
    "relative_task_path",
    "task_meta_present",
    "task_meta_parse_status",
    "task_meta_duplicate_keys",
    "task_meta_field_paths",
    "task_meta_type_map",
    "target_en_present",
    "target_en_char_count",
    "target_zh_present",
    "target_zh_char_count",
    "score_rule_present",
    "task_type_declared",
    "raw_dir_present",
    "raw_file_count",
    "raw_file_types",
    "raw_paths",
    "expected_dir_present",
    "expected_file_count",
    "expected_file_types",
    "expected_paths",
    "eval_py_present",
    "eval_ast_parse_status",
    "eval_line_count",
    "generator_present",
    "multi_input",
    "multi_output",
    "task_id_occurrences_all_modes",
    "duplicate_id_scope",
    "raw_expected_byte_equal_pairs",
    "raw_expected_parsed_equal_pairs",
    "derived_raw_filename_hints",
    "notes",
)

COVERAGE_COLUMNS = (
    "source_commit",
    "split_or_mode",
    "task_id",
    "task_path",
    "eval_path",
    "ast_parse_status",
    "requirement_id",
    "requirement_source",
    "requirement_text",
    "requirement_type",
    "eval_py_checks",
    "coverage",
    "static_signal",
    "check_mechanism",
    "known_false_positive_risk",
    "known_false_negative_risk",
    "independent_oracle_possible",
    "checkpoint_feasible",
    "pilot_eligible",
    "execution_trace_check",
    "intermediate_state_check",
    "reviewer",
    "notes",
)

REQUIREMENT_TO_EVIDENCE = {
    "aggregation_grouping": {"row_content", "numeric_tolerance", "exact_value", "row_count"},
    "dedup_latest": {"row_content", "exact_value", "row_count", "ordering"},
    "file_side_effect": {"file_set", "file_presence", "raw_preservation"},
    "filter": {"row_content", "row_count", "exact_value"},
    "imputation": {"exact_value", "numeric_tolerance", "raw_preservation"},
    "join_merge": {"row_content", "row_count", "schema"},
    "ordering": {"ordering", "exact_value", "row_content"},
    "output_format_encoding": {"format", "schema", "file_presence"},
    "preservation_schema": {"schema", "row_count", "raw_preservation", "exact_value"},
    "transformation": {"exact_value", "numeric_tolerance", "row_content"},
    "other": {"exact_value", "row_content", "task_predicate"},
}

DERIVED_NAME_HINTS = (
    "cleaned",
    "formatted",
    "generated",
    "interpolated",
    "normalized",
    "output",
    "processed",
    "result",
    "transformed",
    "gt",
)


@dataclass(frozen=True)
class Evidence:
    kind: str
    line: int
    symbol: str
    snippet: str

    def render(self, relative_eval_path: str, *, include_snippet: bool = False) -> str:
        symbol = safe_cell(self.symbol)
        rendered = f"{relative_eval_path}:{self.line}|{self.kind}|{symbol}"
        if include_snippet:
            rendered += f"|{safe_cell(self.snippet)}"
        return rendered


@dataclass
class EvaluatorAudit:
    parse_status: str
    line_count: int
    evidence: dict[str, list[Evidence]] = field(default_factory=dict)
    error: str = ""


@dataclass
class TaskAudit:
    mode: str
    task_id: str
    task_dir: Path
    relative_task_path: str
    metadata: dict[str, Any] | None
    metadata_status: str
    duplicate_keys: list[str]
    evaluator: EvaluatorAudit
    inventory_row: dict[str, str]


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def safe_cell(value: Any) -> str:
    """Convert arbitrary values to one physical TSV line without hiding content."""
    if value is None:
        return ""
    return str(value).replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def crc32_file(path: Path) -> int:
    checksum = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum = zlib.crc32(chunk, checksum)
    return checksum & 0xFFFFFFFF


def flatten_types(value: Any, path: str = "$") -> list[tuple[str, str]]:
    """Return every observed JSON field/container path and its value type."""
    if isinstance(value, dict):
        rows = [(path, "object")]
        for key in sorted(value):
            child = f"{path}.{key}" if path != "$" else f"$.{key}"
            rows.extend(flatten_types(value[key], child))
        return rows
    if isinstance(value, list):
        rows = [(path, "array")]
        for item_type in sorted({json_type_name(item) for item in value}):
            rows.append((f"{path}[]", item_type))
        return rows
    return [(path, json_type_name(value))]


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def load_json_object(path: Path) -> tuple[dict[str, Any] | None, str, list[str]]:
    duplicate_keys: list[str] = []

    def keep_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                duplicate_keys.append(key)
            result[key] = value
        return result

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=keep_pairs)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"ERROR:{type(exc).__name__}:{safe_cell(exc)}", sorted(set(duplicate_keys))
    if not isinstance(value, dict):
        return None, f"ERROR:root_type={json_type_name(value)}", sorted(set(duplicate_keys))
    status = "OK" if not duplicate_keys else "OK_WITH_DUPLICATE_KEYS"
    return value, status, sorted(set(duplicate_keys))


def relative_files(directory: Path, task_dir: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        (path for path in directory.rglob("*") if path.is_file() and not path.is_symlink()),
        key=lambda path: path.relative_to(task_dir).as_posix(),
    )


def suffixes(paths: Sequence[Path]) -> str:
    values = sorted({path.suffix.lower() or "[no_suffix]" for path in paths})
    return "|".join(values)


def render_paths(paths: Sequence[Path], task_dir: Path) -> str:
    return "|".join(path.relative_to(task_dir).as_posix() for path in paths)


def parsed_tabular_value(path: Path) -> Any:
    """Read only simple CSV/JSONL structures for equality checks; never emit values."""
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                return tuple(tuple(row) for row in csv.reader(handle) if any(cell != "" for cell in row))
        if suffix == ".jsonl":
            rows = []
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(json.loads(line))
            return rows
    except (OSError, UnicodeError, csv.Error, json.JSONDecodeError):
        return None
    return None


def raw_expected_equal_pairs(
    raw_files: Sequence[Path], expected_files: Sequence[Path], task_dir: Path
) -> tuple[str, str]:
    byte_pairs: list[str] = []
    parsed_pairs: list[str] = []
    parsed_cache: dict[Path, Any] = {}
    for raw_path in raw_files:
        for expected_path in expected_files:
            if raw_path.suffix.lower() != expected_path.suffix.lower():
                continue
            label = (
                f"{raw_path.relative_to(task_dir).as_posix()}="
                f"{expected_path.relative_to(task_dir).as_posix()}"
            )
            try:
                if raw_path.read_bytes() == expected_path.read_bytes():
                    byte_pairs.append(label)
            except OSError:
                pass
            for path in (raw_path, expected_path):
                if path not in parsed_cache:
                    parsed_cache[path] = parsed_tabular_value(path)
            raw_value = parsed_cache[raw_path]
            expected_value = parsed_cache[expected_path]
            if raw_value is not None and raw_value == expected_value:
                parsed_pairs.append(label)
    return "|".join(byte_pairs), "|".join(parsed_pairs)


def callee_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = callee_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def assigned_names(node: ast.AST) -> list[str]:
    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in node.elts:
            names.extend(assigned_names(element))
        return names
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, ast.Attribute):
        return [callee_name(node)]
    return []


def source_snippet(lines: Sequence[str], node: ast.AST, limit: int = 180) -> str:
    line_no = getattr(node, "lineno", 0)
    if not line_no or line_no > len(lines):
        return ""
    text = lines[line_no - 1].strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def classify_static_evidence(node: ast.AST, symbol: str, snippet: str) -> set[str]:
    raw_text = f"{symbol} {snippet}"
    text = raw_text.lower()
    identifier_text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", raw_text)
    identifier_text = re.sub(r"[^A-Za-z0-9]+", " ", identifier_text).lower()
    kinds: set[str] = set()

    if any(token in text for token in ("expected", "gt_path", "ground_truth", "gold")):
        kinds.add("reference_load")
    if any(token in text for token in ("read_csv", "read_json", "dictreader", ".open", "json.load")):
        kinds.add("data_load")
    if any(token in text for token in (".columns", "fieldnames", "schema", "header", "dtypes")):
        kinds.add("schema")
    if any(token in text for token in ("len(", ".shape", "row_count", "n_rows", "nunique")):
        kinds.add("row_count")
    if any(token in text for token in ("sort_values", "sorted(", "argsort", "reset_index", "row_order")):
        kinds.add("ordering")
    if any(token in text for token in ("counter(", "multiset", "value_counts", "merge(", ".isin(", "set(")):
        kinds.add("row_content")
    if any(token in text for token in (".equals(", "assert_frame_equal", "==", "!=", "compare(")):
        kinds.add("exact_value")
    if any(token in text for token in ("isclose", "allclose", "tolerance", "atol", "rtol", "epsilon")):
        kinds.add("numeric_tolerance")
    if any(token in text for token in ("is_file", ".exists(", "filenotfounderror")):
        kinds.add("file_presence")
    if any(token in text for token in ("glob(", "iterdir(", "listdir(", "multiple output", "output_files")):
        kinds.add("file_set")
    if any(token in text for token in ("encoding=", "utf-8", "csv.dictreader", "csv.reader", "json.loads")):
        kinds.add("format")
    if any(token in text for token in ("raw/", '"raw"', "'raw'", "raw_path", "original_df")):
        kinds.add("raw_preservation")
    if any(token in text for token in ("check_", "validate_", "is_valid_")):
        kinds.add("task_predicate")
    if any(token in text for token in ("eval_score", "precision", "recall", "accuracy", "compute_f1", "score")):
        kinds.add("score_reporting")
    if re.search(r"\b(?:trace|trajectory|lineage)\b", identifier_text):
        kinds.add("execution_trace")
    if re.search(r"\b(?:checkpoint|snapshot)\b", identifier_text) or re.search(
        r"\bintermediate\s+state\b", identifier_text
    ):
        kinds.add("intermediate_state")

    if isinstance(node, ast.Compare):
        kinds.add("exact_value")
    if isinstance(node, ast.Assert):
        kinds.add("task_predicate")
    return kinds


def analyze_evaluator(path: Path) -> EvaluatorAudit:
    if not path.is_file():
        return EvaluatorAudit(parse_status="MISSING", line_count=0)
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return EvaluatorAudit(
            parse_status=f"ERROR:{type(exc).__name__}", line_count=0, error=safe_cell(exc)
        )
    lines = source.splitlines()
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return EvaluatorAudit(
            parse_status="ERROR:SyntaxError",
            line_count=len(lines),
            error=f"line={exc.lineno}:{safe_cell(exc.msg)}",
        )

    grouped: dict[str, list[Evidence]] = defaultdict(list)
    seen: set[tuple[str, int, str, str]] = set()
    for node in ast.walk(tree):
        symbol = ""
        include = False
        if isinstance(node, ast.Call):
            symbol = callee_name(node.func)
            include = True
        elif isinstance(node, ast.Compare):
            symbol = "compare"
            include = True
        elif isinstance(node, ast.Assert):
            symbol = "assert"
            include = True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            symbol = ",".join(name for target in targets for name in assigned_names(target))
            lowered = symbol.lower()
            include = any(token in lowered for token in ("gt", "expected", "gold", "raw", "score"))
        if not include:
            continue
        snippet = source_snippet(lines, node)
        for kind in classify_static_evidence(node, symbol, snippet):
            key = (kind, getattr(node, "lineno", 0), symbol, snippet)
            if key in seen:
                continue
            seen.add(key)
            grouped[kind].append(
                Evidence(kind=kind, line=getattr(node, "lineno", 0), symbol=symbol, snippet=snippet)
            )
    for kind in grouped:
        grouped[kind].sort(key=lambda item: (item.line, item.symbol, item.snippet))
    return EvaluatorAudit(parse_status="OK", line_count=len(lines), evidence=dict(grouped))


def metadata_text(metadata: Mapping[str, Any] | None, key: str) -> str:
    value = metadata.get(key) if metadata else None
    return value if isinstance(value, str) else ""


def split_requirement_clauses(text: str) -> list[str]:
    """Create deterministic review units; these are explicitly not gold clauses."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"(?:^|[\n;；])\s*(?:\d+[.)]|[①②③④⑤⑥⑦⑧⑨⑩])\s*", "\n", normalized)
    pieces: list[str] = []
    for block in re.split(r"[\n;；]+", normalized):
        block = re.sub(r"\s+", " ", block).strip(" -•")
        if not block:
            continue
        if len(block) > 420:
            sentences = re.split(r"(?<=[.!?。！？])\s+", block)
        else:
            sentences = [block]
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                pieces.append(sentence)
    return pieces or ([re.sub(r"\s+", " ", text).strip()] if text.strip() else [])


def classify_requirement(text: str) -> list[str]:
    lowered = text.lower()
    labels: list[str] = []
    rules = (
        ("file_side_effect", ("overwrite", "side effect", "multiple files", "one file per", "input file", "output file naming")),
        ("dedup_latest", ("dedup", "duplicate", "latest", "newest", "keep the first", "去重", "最新")),
        ("aggregation_grouping", ("aggregate", "group by", "grouping", "average", "mean", "sum", "count", "聚合", "分组", "平均")),
        ("filter", ("filter", "remove record", "retain record", "keep only", "筛", "过滤", "删除记录")),
        ("ordering", ("sort", "order", "ascending", "descending", "rank", "排序", "顺序")),
        ("join_merge", ("join", "merge", "union", "upsert", "连接", "合并")),
        ("imputation", ("imput", "fill missing", "missing value", "填补", "缺失")),
        ("preservation_schema", ("retain the original", "remain unchanged", "keep the original", "column order", "row count", "schema", "结构", "列顺序", "保持")),
        ("output_format_encoding", ("utf-8", "bom", "output", "csv", "jsonl", "encoding", "编码", "输出")),
        ("transformation", ("normalize", "standardize", "convert", "map", "replace", "transform", "转换", "标准化", "替换")),
    )
    for label, keywords in rules:
        if any(keyword in lowered for keyword in keywords):
            labels.append(label)
    return labels or ["other"]


def collect_relevant_evidence(
    evaluator: EvaluatorAudit, requirement_types: Sequence[str]
) -> tuple[list[str], list[Evidence]]:
    categories: set[str] = set()
    for requirement_type in requirement_types:
        categories.update(REQUIREMENT_TO_EVIDENCE.get(requirement_type, set()))
    evidence: list[Evidence] = []
    for category in sorted(categories):
        evidence.extend(evaluator.evidence.get(category, []))
    evidence.sort(key=lambda item: (item.line, item.kind, item.symbol))
    return sorted(categories), evidence


def task_directories(benchmarks_root: Path) -> list[tuple[str, Path]]:
    tasks: list[tuple[str, Path]] = []
    if not benchmarks_root.is_dir():
        raise FileNotFoundError(f"benchmark root not found: {benchmarks_root}")
    for mode_dir in sorted((path for path in benchmarks_root.iterdir() if path.is_dir()), key=lambda p: p.name):
        for task_dir in sorted((path for path in mode_dir.iterdir() if path.is_dir()), key=lambda p: p.name):
            has_task_shape = any(
                (task_dir / name).exists() for name in ("task_meta.json", "raw", "expected", "eval.py")
            )
            if has_task_shape:
                tasks.append((mode_dir.name, task_dir))
    return tasks


def build_task_audits(benchmarks_root: Path, source_commit: str) -> list[TaskAudit]:
    discovered = task_directories(benchmarks_root)
    id_counts = Counter(
        (match.group(1) if (match := re.match(r"^(T\d+)", task_dir.name)) else "UNKNOWN")
        for _, task_dir in discovered
    )
    audits: list[TaskAudit] = []
    for mode, task_dir in discovered:
        match = re.match(r"^(T\d+)", task_dir.name)
        task_id = match.group(1) if match else "UNKNOWN"
        relative_path = task_dir.relative_to(benchmarks_root).as_posix()
        meta_path = task_dir / "task_meta.json"
        if meta_path.is_file():
            metadata, metadata_status, duplicate_keys = load_json_object(meta_path)
        else:
            metadata, metadata_status, duplicate_keys = None, "MISSING", []

        raw_dir = task_dir / "raw"
        expected_dir = task_dir / "expected"
        raw_files = relative_files(raw_dir, task_dir)
        expected_files = relative_files(expected_dir, task_dir)
        eval_path = task_dir / "eval.py"
        evaluator = analyze_evaluator(eval_path)
        field_types = flatten_types(metadata) if metadata is not None else []
        field_paths = "|".join(path for path, _ in field_types)
        type_map = "|".join(f"{path}:{value_type}" for path, value_type in field_types)
        task_type = metadata.get("task_type") if metadata else None
        if isinstance(task_type, list):
            task_type_text = "|".join(safe_cell(item) for item in task_type)
        elif task_type is None:
            task_type_text = ""
        else:
            task_type_text = safe_cell(task_type)
        byte_equal, parsed_equal = raw_expected_equal_pairs(raw_files, expected_files, task_dir)
        derived_hints = sorted(
            path.relative_to(task_dir).as_posix()
            for path in raw_files
            if any(hint in path.stem.lower() for hint in DERIVED_NAME_HINTS)
        )

        notes: list[str] = []
        if task_id == "UNKNOWN":
            notes.append("task_id_not_parseable_from_directory")
        if metadata_status != "OK":
            notes.append(f"task_meta_status={metadata_status}")
        if not raw_files:
            notes.append("raw_files_missing")
        if not expected_files:
            notes.append("expected_files_missing")
        if evaluator.parse_status != "OK":
            notes.append(f"eval_ast_status={evaluator.parse_status}")
        name_lower = task_dir.name.lower()
        raw_suffix_set = {path.suffix.lower() for path in raw_files}
        expected_suffix_set = {path.suffix.lower() for path in expected_files}
        if "jsonl" in name_lower and raw_suffix_set == {".csv"} and expected_suffix_set == {".csv"}:
            notes.append("directory_name_jsonl_but_raw_expected_csv")
        if parsed_equal:
            notes.append("raw_expected_parsed_equivalence_requires_leakage_review")
        if derived_hints:
            notes.append("derived_looking_raw_filename_requires_input_contract_review")

        target_en = metadata_text(metadata, "target_en")
        target_zh = metadata_text(metadata, "target_zh")
        occurrence_count = id_counts[task_id]
        inventory_row = {
            "source_commit": source_commit,
            "split_or_mode": mode,
            "task_id": task_id,
            "task_key": f"{mode}/{task_dir.name}",
            "relative_task_path": relative_path,
            "task_meta_present": bool_text(meta_path.is_file()),
            "task_meta_parse_status": metadata_status,
            "task_meta_duplicate_keys": "|".join(duplicate_keys),
            "task_meta_field_paths": field_paths,
            "task_meta_type_map": type_map,
            "target_en_present": bool_text(bool(target_en.strip())),
            "target_en_char_count": str(len(target_en)),
            "target_zh_present": bool_text(bool(target_zh.strip())),
            "target_zh_char_count": str(len(target_zh)),
            "score_rule_present": bool_text(bool(metadata and "score_rule" in metadata)),
            "task_type_declared": task_type_text,
            "raw_dir_present": bool_text(raw_dir.is_dir()),
            "raw_file_count": str(len(raw_files)),
            "raw_file_types": suffixes(raw_files),
            "raw_paths": render_paths(raw_files, task_dir),
            "expected_dir_present": bool_text(expected_dir.is_dir()),
            "expected_file_count": str(len(expected_files)),
            "expected_file_types": suffixes(expected_files),
            "expected_paths": render_paths(expected_files, task_dir),
            "eval_py_present": bool_text(eval_path.is_file()),
            "eval_ast_parse_status": evaluator.parse_status,
            "eval_line_count": str(evaluator.line_count),
            "generator_present": bool_text((task_dir / "gen_data.py").is_file()),
            "multi_input": bool_text(len(raw_files) > 1),
            "multi_output": bool_text(len(expected_files) > 1),
            "task_id_occurrences_all_modes": str(occurrence_count),
            "duplicate_id_scope": "across_modes" if occurrence_count > 1 else "none",
            "raw_expected_byte_equal_pairs": byte_equal,
            "raw_expected_parsed_equal_pairs": parsed_equal,
            "derived_raw_filename_hints": "|".join(derived_hints),
            "notes": ";".join(notes),
        }
        audits.append(
            TaskAudit(
                mode=mode,
                task_id=task_id,
                task_dir=task_dir,
                relative_task_path=relative_path,
                metadata=metadata,
                metadata_status=metadata_status,
                duplicate_keys=duplicate_keys,
                evaluator=evaluator,
                inventory_row=inventory_row,
            )
        )
    return sorted(audits, key=lambda item: (item.mode, item.task_id, item.relative_task_path))


def build_coverage_rows(
    tasks: Sequence[TaskAudit],
    source_commit: str,
    *,
    include_requirement_text: bool = False,
    include_evaluator_snippets: bool = False,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for task in tasks:
        eval_rel = f"data/benchmarks/{task.relative_task_path}/eval.py"
        target_en = metadata_text(task.metadata, "target_en")
        clauses = split_requirement_clauses(target_en)
        if not clauses:
            clauses = ["[target_en missing or unparsable]"]
        for index, clause in enumerate(clauses, start=1):
            requirement_types = classify_requirement(clause)
            relevant_categories, evidence = collect_relevant_evidence(task.evaluator, requirement_types)
            rendered_evidence = " || ".join(
                item.render(eval_rel, include_snippet=include_evaluator_snippets)
                for item in evidence
            )
            detected_mechanisms = sorted({item.kind for item in evidence})
            has_trace = bool(task.evaluator.evidence.get("execution_trace"))
            has_state = bool(task.evaluator.evidence.get("intermediate_state"))
            rows.append(
                {
                    "source_commit": source_commit,
                    "split_or_mode": task.mode,
                    "task_id": task.task_id,
                    "task_path": f"data/benchmarks/{task.relative_task_path}",
                    "eval_path": eval_rel,
                    "ast_parse_status": task.evaluator.parse_status,
                    "requirement_id": f"DRAFT_C{index:03d}",
                    "requirement_source": "task_meta.json:target_en",
                    "requirement_text": (
                        clause
                        if include_requirement_text
                        else "[WITHHELD_PENDING_DATA_LICENSE_REVIEW]"
                    ),
                    "requirement_type": "|".join(requirement_types),
                    "eval_py_checks": rendered_evidence,
                    "coverage": "DRAFT_UNREVIEWED",
                    "static_signal": (
                        "DETECTED_POTENTIAL_SIGNAL"
                        if evidence
                        else "NOT_DETECTED_FOR_HEURISTIC_CATEGORY"
                    ),
                    "check_mechanism": "|".join(detected_mechanisms),
                    "known_false_positive_risk": "HUMAN_REVIEW_REQUIRED",
                    "known_false_negative_risk": "HUMAN_REVIEW_REQUIRED",
                    "independent_oracle_possible": "UNASSESSED",
                    "checkpoint_feasible": "UNASSESSED",
                    "pilot_eligible": "UNASSESSED",
                    "execution_trace_check": "DETECTED_STATIC" if has_trace else "NOT_DETECTED_STATIC",
                    "intermediate_state_check": "DETECTED_STATIC" if has_state else "NOT_DETECTED_STATIC",
                    "reviewer": "UNASSIGNED",
                    "notes": (
                        "Machine-split clause and lexical/AST signal only; expected categories="
                        + "|".join(relevant_categories)
                        + ". Absence is not proof of no coverage; presence is not proof of semantic coverage."
                    ),
                }
            )
    return rows


def audit_archive(archive_path: Path, extracted_root: Path | None) -> dict[str, Any]:
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        file_entries = [entry for entry in entries if not entry.is_dir()]
        directory_entries = [entry for entry in entries if entry.is_dir()]
        absolute = []
        traversal = []
        symlinks = []
        special = []
        encrypted = []
        world_writable = []
        normalized: defaultdict[str, list[str]] = defaultdict(list)
        for entry in entries:
            name = entry.filename
            pure = PurePosixPath(name)
            if pure.is_absolute() or re.match(r"^[A-Za-z]:", name):
                absolute.append(name)
            if ".." in pure.parts:
                traversal.append(name)
            mode = (entry.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                symlinks.append(name)
            elif mode and not entry.is_dir() and not stat.S_ISREG(mode):
                special.append(name)
            if entry.flag_bits & 0x1:
                encrypted.append(name)
            if mode & 0o002:
                world_writable.append(name)
            normalized[unicodedata.normalize("NFC", name).casefold()].append(name)
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        normalization_collisions = sorted(
            "|".join(values) for values in normalized.values() if len(set(values)) > 1
        )

        extraction_path_match = "NOT_CHECKED"
        extraction_type_match = "NOT_CHECKED"
        extraction_size_match = "NOT_CHECKED"
        extraction_crc_match = "NOT_CHECKED"
        extraction_missing: list[str] = []
        extraction_extra: list[str] = []
        extraction_type_mismatches: list[str] = []
        extraction_size_mismatches: list[str] = []
        extraction_crc_mismatches: list[str] = []
        extraction_symlinks: list[str] = []
        extraction_special: list[str] = []
        extraction_crc_checked_count = 0
        if extracted_root is not None:
            if not extracted_root.is_dir():
                raise FileNotFoundError(f"extracted root not found: {extracted_root}")
            extracted_entries = list(extracted_root.rglob("*"))
            archive_paths = {entry.filename.rstrip("/") for entry in entries}
            extracted_paths = {
                path.relative_to(extracted_root).as_posix()
                for path in extracted_entries
            }
            extraction_symlinks = sorted(
                path.relative_to(extracted_root).as_posix()
                for path in extracted_entries
                if path.is_symlink()
            )
            extraction_special = sorted(
                path.relative_to(extracted_root).as_posix()
                for path in extracted_entries
                if not path.is_symlink() and not path.is_dir() and not path.is_file()
            )
            extraction_missing = sorted(archive_paths - extracted_paths)
            extraction_extra = sorted(extracted_paths - archive_paths)
            extraction_path_match = bool_text(not extraction_missing and not extraction_extra)
            for entry in entries:
                extracted_path = extracted_root / entry.filename.rstrip("/")
                if not extracted_path.exists() and not extracted_path.is_symlink():
                    continue
                if extracted_path.is_symlink() or entry.is_dir() != extracted_path.is_dir():
                    extraction_type_mismatches.append(entry.filename)
                    continue
                if not entry.is_dir():
                    if not extracted_path.is_file():
                        extraction_type_mismatches.append(entry.filename)
                        continue
                    if extracted_path.stat().st_size != entry.file_size:
                        extraction_size_mismatches.append(entry.filename)
                    if crc32_file(extracted_path) != entry.CRC:
                        extraction_crc_mismatches.append(entry.filename)
                    extraction_crc_checked_count += 1
            extraction_type_match = bool_text(
                not extraction_type_mismatches and not extraction_symlinks and not extraction_special
            )
            extraction_size_match = bool_text(not extraction_size_mismatches)
            extraction_crc_match = bool_text(
                extraction_crc_checked_count == len(file_entries)
                and not extraction_crc_mismatches
            )

        return {
            "sha256": sha256_file(archive_path),
            "size_bytes": archive_path.stat().st_size,
            "entry_count": len(entries),
            "file_count": len(file_entries),
            "directory_count": len(directory_entries),
            "uncompressed_bytes": sum(entry.file_size for entry in file_entries),
            "top_level_prefixes": sorted({PurePosixPath(name).parts[0] for name in names if name}),
            "absolute_paths": absolute,
            "traversal_paths": traversal,
            "duplicate_paths": duplicates,
            "normalization_collisions": normalization_collisions,
            "symlink_paths": symlinks,
            "special_paths": special,
            "encrypted_paths": encrypted,
            "world_writable_paths": world_writable,
            "license_like_paths": sorted(
                name
                for name in names
                if PurePosixPath(name).name.lower()
                in {"license", "license.txt", "copying", "notice", "readme", "readme.md", "terms", "citation.cff", "attribution"}
            ),
            "extraction_path_match": extraction_path_match,
            "extraction_type_match": extraction_type_match,
            "extraction_size_match": extraction_size_match,
            "extraction_crc_match": extraction_crc_match,
            "extraction_crc_checked_count": extraction_crc_checked_count,
            "extraction_missing": extraction_missing,
            "extraction_extra": extraction_extra,
            "extraction_type_mismatches": extraction_type_mismatches,
            "extraction_size_mismatches": extraction_size_mismatches,
            "extraction_crc_mismatches": extraction_crc_mismatches,
            "extraction_symlinks": extraction_symlinks,
            "extraction_special": extraction_special,
        }


def assert_archive_binding(archive: Mapping[str, Any]) -> None:
    fatal_lists = {
        "archive_absolute_paths": archive["absolute_paths"],
        "archive_traversal_paths": archive["traversal_paths"],
        "archive_duplicate_paths": archive["duplicate_paths"],
        "archive_normalization_collisions": archive["normalization_collisions"],
        "archive_symlink_paths": archive["symlink_paths"],
        "archive_special_paths": archive["special_paths"],
        "archive_encrypted_paths": archive["encrypted_paths"],
        "extraction_missing": archive["extraction_missing"],
        "extraction_extra": archive["extraction_extra"],
        "extraction_type_mismatches": archive["extraction_type_mismatches"],
        "extraction_size_mismatches": archive["extraction_size_mismatches"],
        "extraction_crc_mismatches": archive["extraction_crc_mismatches"],
        "extraction_symlinks": archive["extraction_symlinks"],
        "extraction_special": archive["extraction_special"],
    }
    failures = [name for name, values in fatal_lists.items() if values]
    for field_name in (
        "extraction_path_match",
        "extraction_type_match",
        "extraction_size_match",
        "extraction_crc_match",
    ):
        if archive[field_name] != "true":
            failures.append(field_name)
    if failures:
        raise ValueError(
            "archive/extraction identity check failed before output generation: "
            + ",".join(sorted(set(failures)))
        )


def manifest_rows(
    *,
    source_repo: str,
    source_commit: str,
    archive_git_blob: str,
    archive_path: Path,
    archive: Mapping[str, Any],
    tasks: Sequence[TaskAudit],
    source_root: Path | None,
    audit_timestamp: str,
    include_requirement_text: bool,
    include_evaluator_snippets: bool,
) -> list[dict[str, str]]:
    mode_counts = Counter(task.mode for task in tasks)
    metadata_schema = Counter(
        pair
        for task in tasks
        if task.metadata is not None
        for pair in flatten_types(task.metadata)
    )
    parsed_equal_tasks = sum(
        bool(task.inventory_row["raw_expected_parsed_equal_pairs"]) for task in tasks
    )
    parse_ok = sum(task.evaluator.parse_status == "OK" for task in tasks)
    trace_detected = sum(bool(task.evaluator.evidence.get("execution_trace")) for task in tasks)
    state_detected = sum(bool(task.evaluator.evidence.get("intermediate_state")) for task in tasks)

    license_path = source_root / "LICENSE" if source_root else None
    license_first_line = ""
    if license_path and license_path.is_file():
        try:
            license_first_line = license_path.read_text(encoding="utf-8").splitlines()[0]
        except (OSError, UnicodeError, IndexError):
            license_first_line = "UNREADABLE"

    rows: list[tuple[str, Any, str, str]] = [
        ("audit_schema_version", AUDIT_SCHEMA_VERSION, "scripts/audit_upstream_package.py", "OBSERVED"),
        ("audit_timestamp_utc", audit_timestamp, "CLI argument or UTC clock", "OBSERVED"),
        ("upstream_repo", source_repo, "fixed audit input", "INPUT_PIN"),
        ("upstream_commit", source_commit, "fixed audit input", "INPUT_PIN"),
        ("data_zip_path", archive_path.name, "fixed source worktree", "OBSERVED"),
        ("data_zip_git_blob_oid", archive_git_blob, "git ls-tree at fixed commit", "OBSERVED_EXTERNAL_TO_SCRIPT"),
        ("data_zip_sha256", archive["sha256"], "SHA-256 over fixed archive bytes", "OBSERVED"),
        ("archive_size_bytes", archive["size_bytes"], "filesystem stat", "OBSERVED"),
        ("archive_entry_count", archive["entry_count"], "ZIP central directory", "DERIVED"),
        ("archive_regular_file_count", archive["file_count"], "ZIP central directory", "DERIVED"),
        ("archive_directory_count", archive["directory_count"], "ZIP central directory", "DERIVED"),
        ("archive_uncompressed_bytes", archive["uncompressed_bytes"], "ZIP central directory", "DERIVED"),
        ("archive_top_level_prefixes", "|".join(archive["top_level_prefixes"]), "ZIP central directory", "DERIVED"),
        ("archive_absolute_path_count", len(archive["absolute_paths"]), "ZIP path audit", "DERIVED"),
        ("archive_traversal_path_count", len(archive["traversal_paths"]), "ZIP path audit", "DERIVED"),
        ("archive_duplicate_path_count", len(archive["duplicate_paths"]), "ZIP path audit", "DERIVED"),
        ("archive_normalization_collision_count", len(archive["normalization_collisions"]), "NFC+casefold path audit", "DERIVED"),
        ("archive_symlink_count", len(archive["symlink_paths"]), "ZIP external mode audit", "DERIVED"),
        ("archive_special_file_count", len(archive["special_paths"]), "ZIP external mode audit", "DERIVED"),
        ("archive_encrypted_entry_count", len(archive["encrypted_paths"]), "ZIP flag audit", "DERIVED"),
        ("archive_world_writable_entry_count", len(archive["world_writable_paths"]), "ZIP external mode audit", "DERIVED"),
        ("archive_license_like_paths", "|".join(archive["license_like_paths"]), "ZIP filename audit", "OBSERVED"),
        ("extracted_path_set_match", archive["extraction_path_match"], "archive/extraction relative paths", "DERIVED"),
        ("extracted_type_match", archive["extraction_type_match"], "archive/extraction file types", "DERIVED"),
        ("extracted_size_match", archive["extraction_size_match"], "archive/extraction file sizes", "DERIVED"),
        ("extracted_crc_match", archive["extraction_crc_match"], "CRC-32 of every extracted regular file versus ZIP central directory", "DERIVED"),
        ("extracted_crc_checked_file_count", archive["extraction_crc_checked_count"], "CRC-32 binding check", "DERIVED"),
        ("extracted_symlink_count", len(archive["extraction_symlinks"]), "extraction type audit", "DERIVED"),
        ("extracted_special_file_count", len(archive["extraction_special"]), "extraction type audit", "DERIVED"),
        ("task_count_total", len(tasks), "rows in upstream_inventory.tsv", "DERIVED"),
        ("task_count_by_mode", "|".join(f"{mode}:{mode_counts[mode]}" for mode in sorted(mode_counts)), "rows in upstream_inventory.tsv", "DERIVED"),
        ("task_id_unique_scope", "split_or_mode+task_directory", "duplicate task IDs exist across modes", "DERIVED"),
        ("task_meta_schema_counts", "|".join(f"{path}:{kind}:{count}" for (path, kind), count in sorted(metadata_schema.items())), "all parsed task_meta.json", "DERIVED"),
        ("eval_ast_parse_ok_count", parse_ok, "static ast.parse only", "DERIVED"),
        ("eval_execution_count", 0, "audit contract prohibits evaluator execution", "OBSERVED"),
        ("execution_trace_static_signal_task_count", trace_detected, "AST/lexical scan", "DERIVED"),
        ("intermediate_state_static_signal_task_count", state_detected, "AST/lexical scan", "DERIVED"),
        ("raw_expected_parsed_equivalence_task_count", parsed_equal_tasks, "format-aware equality; values not emitted", "DERIVED"),
        ("software_license_path", "LICENSE" if license_path and license_path.is_file() else "", "fixed source root", "OBSERVED"),
        ("software_license_first_line", license_first_line, "LICENSE line 1", "OBSERVED"),
        ("data_license_status", "DATA_INSUFFICIENT", "no separate license-like path found inside data.zip", "HUMAN_REVIEW_REQUIRED"),
        ("redistribution_permission", "DATA_INSUFFICIENT", "software LICENSE scope is not treated as data permission", "HUMAN_REVIEW_REQUIRED"),
        (
            "requirement_text_in_tracked_draft",
            "included" if include_requirement_text else "withheld",
            "oracle_coverage.DRAFT.tsv generation option",
            "HUMAN_REVIEW_REQUIRED" if include_requirement_text else "OBSERVED",
        ),
        (
            "evaluator_source_snippets_in_tracked_draft",
            "included" if include_evaluator_snippets else "withheld",
            "oracle_coverage.DRAFT.tsv generation option",
            "HUMAN_REVIEW_REQUIRED" if include_evaluator_snippets else "OBSERVED",
        ),
        ("python_version", platform.python_version(), "audit runtime", "OBSERVED"),
        ("platform", platform.platform(), "audit runtime", "OBSERVED"),
    ]
    return [
        {"field": field_name, "value": safe_cell(value), "evidence": evidence, "status": status}
        for field_name, value, evidence, status in rows
    ]


def write_tsv(path: Path, columns: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), dialect="excel-tab", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: safe_cell(row.get(column, "")) for column in columns})


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def validate_audit_paths(
    output_dir: Path,
    source_root: Path | None,
    extracted_root: Path,
    benchmarks_root: Path,
) -> None:
    resolved_output = output_dir.resolve()
    for label, root in (
        ("source_root", source_root),
        ("extracted_root", extracted_root),
        ("benchmarks_root", benchmarks_root),
    ):
        if root is None:
            continue
        resolved_root = root.resolve()
        if resolved_output == resolved_root or resolved_root in resolved_output.parents:
            raise ValueError(f"output_dir must not be inside {label}: {resolved_output}")
    if not path_is_within(benchmarks_root, extracted_root):
        raise ValueError(
            f"benchmarks_root must resolve beneath the verified extracted_root: {benchmarks_root}"
        )


def run_audit(
    *,
    archive_path: Path,
    extracted_root: Path,
    benchmarks_root: Path,
    output_dir: Path,
    source_repo: str,
    source_commit: str,
    archive_git_blob: str,
    source_root: Path | None,
    audit_timestamp: str,
    include_requirement_text: bool = False,
    include_evaluator_snippets: bool = False,
) -> dict[str, Any]:
    validate_audit_paths(output_dir, source_root, extracted_root, benchmarks_root)
    archive = audit_archive(archive_path, extracted_root)
    assert_archive_binding(archive)
    tasks = build_task_audits(benchmarks_root, source_commit)
    inventory_rows = [task.inventory_row for task in tasks]
    coverage_rows = build_coverage_rows(
        tasks,
        source_commit,
        include_requirement_text=include_requirement_text,
        include_evaluator_snippets=include_evaluator_snippets,
    )
    package_rows = manifest_rows(
        source_repo=source_repo,
        source_commit=source_commit,
        archive_git_blob=archive_git_blob,
        archive_path=archive_path,
        archive=archive,
        tasks=tasks,
        source_root=source_root,
        audit_timestamp=audit_timestamp,
        include_requirement_text=include_requirement_text,
        include_evaluator_snippets=include_evaluator_snippets,
    )

    write_tsv(output_dir / "package_manifest.tsv", ("field", "value", "evidence", "status"), package_rows)
    write_tsv(output_dir / "upstream_inventory.tsv", INVENTORY_COLUMNS, inventory_rows)
    write_tsv(output_dir / "oracle_coverage.DRAFT.tsv", COVERAGE_COLUMNS, coverage_rows)
    return {
        "task_count": len(tasks),
        "coverage_row_count": len(coverage_rows),
        "mode_counts": dict(sorted(Counter(task.mode for task in tasks).items())),
        "archive_sha256": archive["sha256"],
        "eval_ast_parse_ok_count": sum(task.evaluator.parse_status == "OK" for task in tasks),
        "output_dir": str(output_dir),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="Path to the fixed data.zip")
    parser.add_argument(
        "--extracted-root",
        required=True,
        type=Path,
        help="Root produced by extracting data.zip; normally contains data/",
    )
    parser.add_argument(
        "--benchmarks-root",
        type=Path,
        help="Override benchmark root; default: <extracted-root>/data/benchmarks",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, help="Fixed source worktree containing LICENSE")
    parser.add_argument("--source-repo", default=DEFAULT_SOURCE_REPO)
    parser.add_argument("--source-commit", default=DEFAULT_SOURCE_COMMIT)
    parser.add_argument("--archive-git-blob", default=DEFAULT_ARCHIVE_BLOB)
    parser.add_argument(
        "--audit-timestamp",
        default=None,
        help="ISO-8601 UTC timestamp. Defaults to the current UTC clock.",
    )
    parser.add_argument(
        "--include-requirement-text",
        action="store_true",
        help=(
            "Copy machine-split target_en clauses into the coverage TSV. "
            "Default is withheld because benchmark-data redistribution is unresolved."
        ),
    )
    parser.add_argument(
        "--include-evaluator-snippets",
        action="store_true",
        help=(
            "Copy evaluator source snippets into the coverage TSV. Default emits only "
            "archive-relative path, line, signal kind, and symbol."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    audit_timestamp = args.audit_timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    benchmarks_root = args.benchmarks_root or args.extracted_root / "data" / "benchmarks"
    result = run_audit(
        archive_path=args.archive,
        extracted_root=args.extracted_root,
        benchmarks_root=benchmarks_root,
        output_dir=args.output_dir,
        source_repo=args.source_repo,
        source_commit=args.source_commit,
        archive_git_blob=args.archive_git_blob,
        source_root=args.source_root,
        audit_timestamp=audit_timestamp,
        include_requirement_text=args.include_requirement_text,
        include_evaluator_snippets=args.include_evaluator_snippets,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
