# Phase 2 Audit Rationale

**Purpose:** record the evidence and decision logic behind the fixed-package audit
**Status:** audit complete; scientific and licensing gates remain open
**Date:** 2026-08-27

This is an auditable rationale, not private chain-of-thought. It records inputs, transformations, evidence classes, alternatives, and stop conditions so another researcher can reproduce or overturn the result.

## 1. Question answered

Phase 2 asked whether the fixed public ProfiliTable package is sufficiently identifiable and structurally inspectable to support selection of four real base tasks for the benchmark-first project.

The audit was not designed to establish novelty, run ProfiliTable, validate model performance, create semantic ground truth, or approve data redistribution.

## 2. Evidence order

The audit used the following order because each step constrains the next:

1. **Freeze package identity.** Bind observations to one Git commit, one `data.zip` blob, and one SHA-256.
2. **Keep raw material outside Git.** Extract to a detached temporary worktree and commit only summaries/code.
3. **Fix the inventory grain.** Use `(split_or_mode, task directory)` rather than bare `Txxxx`, because task IDs overlap across modes.
4. **Enumerate before interpreting.** Record all metadata fields and raw/expected/evaluator presence for every task.
5. **Inspect evaluators statically.** Parse code and point draft coverage to exact lines without executing untrusted package code.
6. **Separate machine signals from semantic judgment.** Keep every automatically split clause and coverage value in `oracle_coverage.DRAFT.tsv` as unreviewed.
7. **Shortlist conditionally.** Select one structurally promising task per planned family, then record evaluator gaps and human gates.
8. **Stop at the authorization boundary.** Do not create mutations or run models while license, oracle, and checkpoint decisions remain unresolved.

## 3. Fixed evidence

### Package identity

- claimed upstream: `https://github.com/Eularioal/ProfiliTable`;
- fixed commit: `f023ec4b754555000a659b93fd514645c55e3cec`;
- `data.zip` Git blob: `7c1e8be2cffe34386d94f7d5e5849b2ba096b4fd`;
- archive size: 1,851,954 bytes;
- archive SHA-256: `a5c46f5c0d71a4886ed7c6cebb737814dff0587038f45bed58a40d9d96fafcb6`.

A 2026-08-27 remote readback found both `HEAD` and `refs/heads/master` at the fixed commit. This verifies the current remote ref, not a signed release or immutable tag.

The ZIP central directory contains 1,033 entries: 648 regular files and 385 directories. Static path checks found no absolute paths, traversal paths, duplicate paths, normalization collisions, symlinks, special files, or encrypted entries. Every extracted regular file is bound back to the archive through size and CRC-32 checks; inventory generation fails before writing if path, type, size, or CRC differs. Archive modes mark all entries world-writable; extraction tools may apply a restrictive umask, so this remains a packaging-hygiene observation rather than an exploit claim.

### Inventory

- 127 task directories: 90 NL2Op and 37 NL2Dag;
- 127/127 contain parseable `task_meta.json`, nonempty `raw/`, nonempty `expected/`, and AST-parseable `eval.py`;
- all metadata contain string `target_en` and `target_zh`;
- 13 metadata files contain `task_type`; their arrays contain 17 values in total;
- one task contains `score_rule`;
- 23 bare task IDs occur in both modes, so bare IDs are not globally unique;
- all 37 NL2Dag and 70/90 NL2Op tasks include `gen_data.py`; the remaining 20 NL2Op tasks do not.

### Evaluator boundary

The 127 evaluators are heterogeneous final-output checks. Static inspection found no evaluator that reads an execution trace, lineage, checkpoint, or intermediate state. Ten evaluators also read raw data, usually for preservation checks, but this remains final-artifact adjudication.

This means the upstream evaluator fleet can contribute native-outcome baselines. It cannot by itself label source-step divergence, propagation, recovery, or the incremental value of state evidence.

## 4. Why a draft coverage table was generated for every task

The package contains enough variation that sampling only four evaluators could hide recurring weaknesses. The script therefore:

- deterministically splits `target_en` into 516 review units in memory;
- classifies each unit with lexical requirement categories;
- parses the corresponding `eval.py` into AST signals;
- records exact `data/benchmarks/.../eval.py:line|signal-kind|symbol` evidence;
- withholds the clause text from the tracked TSV while data redistribution is unresolved;
- withholds evaluator source snippets by default so embedded oracle literals cannot be copied into the public review table;
- sets semantic coverage to `DRAFT_UNREVIEWED` and pilot eligibility to `UNASSESSED`.

A detected AST signal is not proof that a clause is covered. A missing signal is not proof that it is uncovered. The table is a review queue, not an oracle. A reviewer with authorized access can resolve each `(task_path, requirement_source, requirement_id)` against the fixed local package; the script exposes separate opt-in flags for requirement text and evaluator snippets only in an authorized environment.

## 5. Findings that changed the decision

### 5.1 Package counts are stable, but identifiers are not globally unique

The expected 90 NL2Op count is present; NL2Dag contains 37, not 39, in this exact package. Non-contiguous suffixes and 23 cross-mode ID overlaps make directory enumeration necessary. Paper-level counts or maximum IDs are not sufficient provenance.

### 5.2 Presence is complete; semantic metadata is thin

Every task has the expected four structural components, but metadata does not contain task ID, input/output path declarations, schemas, source attribution, data license, evaluator contract, or version. These properties must be reconstructed from paths/code and then reviewed.

### 5.3 Two defects block naive task reuse

- `NL2Op/T0010_normalize_numbers` contains a raw file equivalent to its GT, creating direct answer leakage.
- `NL2Op/T0113_data_imputation_muti` selects the wrong expected file for its marker-based metric and therefore scores every parseable candidate as zero.

These are not model failures. They are benchmark-package/evaluator defects and must be excluded from model comparisons.

### 5.4 Native scores are not sufficient semantic oracles

Twenty-five evaluator files belong to six byte-identical cross-task groups. At least 17 scoring bodies rely mainly on identifier membership. Several custom evaluators have concrete loopholes, such as prefix truncation, ignored order, allowed extra columns, or diagnostics that print reference values.

The relevant conclusion is narrow: upstream native evaluators are useful baseline evidence but require per-task clause coverage review and independent property checks before Stage 0.

### 5.5 Data permission remains unresolved

The fixed commit contains a standard MIT `LICENSE` whose defined subject is software and associated documentation. No separate data license, attribution, citation, or terms file was found in `data.zip`, the task metadata, README, or project metadata.

The audit therefore records:

```text
software_license = MIT text observed
data_license_status = DATA_INSUFFICIENT
redistribution_permission = DATA_INSUFFICIENT
```

No claim is made that the archive is prohibited from reuse. The evidence simply does not establish the intended redistribution right.

## 6. Candidate logic

The four conditional candidates were chosen to maximize semantic contrast while staying close to deterministic table operations:

- `T0114_filter_muti` exposes three separable filter constraints that could later support a reviewed revision;
- `T0074_wide_table_construction` exposes grouping grain, window boundaries, aggregation, and left-join completeness;
- `T0011_incremental_deduplication` exposes latest-record selection and winning-row preservation;
- `T0047_multi_csv_union` exposes order/value preservation and motivates a separate filesystem side-effect oracle.

Each candidate has a documented native-evaluator gap. That is acceptable for a shortlist because Stage 0 is supposed to compare native scoring with stronger property/state conditions. It is not acceptable for final gold without human review.

## 7. Alternatives rejected in this phase

- Selecting tasks only from directory names was rejected because five NL2Dag `jsonl` names package CSV and one name describes the wrong operation entirely.
- Selecting the strongest native evaluator regardless of research family was rejected because it would optimize final-output exactness rather than the planned capability contrast.
- Executing all 127 evaluators was rejected for this audit because candidate outputs were not in scope and code execution would not answer clause coverage, licensing, or provenance questions.
- Creating a new clean package was rejected because mutation, upstream repair, and redistribution were not authorized.
- Proceeding directly to the 4×4 pilot was rejected because human semantic and data-rights gates remain open.

## 8. Conditions that overturn this result

Revise the Phase 2 conclusion if any of the following occurs:

1. a different official fixed package produces different task/archive counts or task contents;
2. the rights holder supplies explicit data terms that change reuse or redistribution status;
3. manual clause review shows one or more candidates lack an independent semantic oracle;
4. candidate checkpoint boundaries cannot be defined without changing clean semantics;
5. an upstream evaluator repair or refrozen package removes the recorded leakage/zero-score defects;
6. a better real task covers the same planned family with fewer confounds.

## 9. Result

The mechanical Phase 2 audit is complete and reproducible. It resolves package identity and task inventory, exposes material data/evaluator defects, and narrows the real-task pool to four conditional candidates.

The next gate is human/mentor review of data rights, clause coverage, independent oracles, and checkpoint boundaries. Until that gate passes, do not create mutants, run LLM baselines, modify ProfiliTable runtime, or claim that Phase 2 selected a valid benchmark.
