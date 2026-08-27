# Phase 2 Handoff Review

**Status:** mechanical upstream audit complete; pilot gate not passed
**Date:** 2026-08-27
**Branch:** `research/upstream-audit`
**Fixed source:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`

## 1. Current authoritative status

Phase 2 has completed the bounded public-source/local-summary audit authorized by the Phase 1 decision. It did not create benchmark variants, run evaluators or models, modify runtime code, use internal assets, or commit upstream raw data.

The four task families now have conditional candidates, but no task is approved for Stage 0. Data redistribution permission is unresolved, the clause coverage table is still machine-generated `DRAFT`, and independent oracle/checkpoint designs require human approval.

## 2. Canonical reading order

1. [`PHASE2_HANDOFF_REVIEW.md`](PHASE2_HANDOFF_REVIEW.md) — current status, acceptance, blockers, and next gate;
2. [`PHASE2_AUDIT_RATIONALE.md`](PHASE2_AUDIT_RATIONALE.md) — evidence-based audit and decision path;
3. [`audit_results/base_task_candidates.md`](audit_results/base_task_candidates.md) — four conditional candidates, exact evaluator boundaries, exclusions;
4. [`audit_results/package_manifest.tsv`](audit_results/package_manifest.tsv) — fixed archive identity, package and license observations;
5. [`audit_results/upstream_inventory.tsv`](audit_results/upstream_inventory.tsv) — one row per `(mode, task directory)`;
6. [`audit_results/oracle_coverage.DRAFT.tsv`](audit_results/oracle_coverage.DRAFT.tsv) — 516 unreviewed clause/evaluator mappings;
7. [`../scripts/audit_upstream_package.py`](../scripts/audit_upstream_package.py) and [`../tests/test_audit_upstream_package.py`](../tests/test_audit_upstream_package.py) — reproducer and synthetic tests;
8. [`PHASE1_HANDOFF_REVIEW.md`](PHASE1_HANDOFF_REVIEW.md) — prior formulation decision and claim boundaries.

## 3. Output inventory

| Artifact | Role | Status |
|---|---|---|
| `research/audit_results/package_manifest.tsv` | package hash, archive structure, task counts, license boundary | generated and reviewed |
| `research/audit_results/upstream_inventory.tsv` | 127 task-grain inventory | generated and reviewed |
| `research/audit_results/oracle_coverage.DRAFT.tsv` | machine review queue with task/clause locators and exact evaluator line/kind/symbol evidence; requirement text and evaluator snippets withheld | DRAFT; must not be renamed/finalized without authorized human clause review |
| `research/audit_results/base_task_candidates.md` | conditional four-family shortlist and hard exclusions | reviewed recommendation, not Stage-0 approval |
| `scripts/audit_upstream_package.py` | standard-library static audit | implemented |
| `tests/test_audit_upstream_package.py` | synthetic field, withholding, path-safety, archive-binding, inventory, and coverage tests | implemented |
| `research/PHASE2_AUDIT_RATIONALE.md` | auditable reasoning and overturn conditions | complete |

## 4. Acceptance record

| Phase 2 acceptance criterion | Evidence | Status |
|---|---|---|
| package SHA-256 recorded | `package_manifest.tsv:data_zip_sha256` = `a5c46f5…fafcb6` | PASS |
| task counts recomputable | 127 inventory rows; NL2Dag 37, NL2Op 90 | PASS |
| all `task_meta.json` fields enumerated | root/target fields plus optional `task_type` and `score_rule` paths/types recorded per task | PASS |
| raw/expected/eval presence recorded | per-task counts, paths, suffixes, and parse status | PASS |
| draft evaluator coverage points to exact code locations | 516 DRAFT rows with task/clause locators and archive-relative `eval.py:line|kind|symbol` evidence; clause text and source snippets withheld | PASS as mechanical draft |
| no upstream raw data added to Git | changed paths contain only Python, Markdown, and TSV; requirement text and evaluator snippets are withheld from the DRAFT | PASS |
| existing ProfiliTable behavior unchanged | no `main/`, `table_agent/`, dependency, or runtime-configuration path edited | PASS |

Passing this table does not establish semantic-oracle completeness or data permission.

## 5. Key observed results

- Package identity: `data.zip` blob `7c1e8be…`, 1,851,954 bytes, SHA-256 `a5c46f5…fafcb6`.
- Archive: 1,033 entries; all 648 extracted regular files match ZIP CRC; no static path-traversal, duplicate-path, symlink, special-file, normalization-collision, or encryption finding.
- Tasks: 127 total; NL2Op 90 and NL2Dag 37; 23 bare IDs overlap across modes.
- Structural completeness: 127/127 have valid metadata, nonempty raw/expected directories, and AST-parseable evaluators.
- Evaluator scope: final-output evidence; no trace/checkpoint/intermediate-state reader detected.
- Direct leakage exclusion: `NL2Op/T0010_normalize_numbers`.
- Non-discriminating evaluator exclusion: `NL2Op/T0113_data_imputation_muti`.
- Data license: repository MIT text observed; benchmark-data license and redistribution permission remain `DATA_INSUFFICIENT`.

## 6. Conditional candidates

1. filter/revision — `NL2Op/T0114_filter_muti`;
2. aggregation grain — `NL2Op/T0074_wide_table_construction`;
3. dedup/latest record — `NL2Op/T0011_incremental_deduplication`;
4. preservation/side effects — `NL2Op/T0047_multi_csv_union`.

These are the strongest current structural candidates, not approved benchmark instances. See [`base_task_candidates.md`](audit_results/base_task_candidates.md) for exact evaluator limitations and human gates.

## 7. Allowed claims

- The fixed archive has a reproducible SHA-256 and contains 127 task bundles under the observed structure.
- The public package has complete task/evaluator file presence at that fixed commit.
- Static inspection found material leakage, evaluator, naming, and packaging issues.
- The four named tasks are conditional candidates for further human review.
- Existing evaluators adjudicate final artifacts and do not provide process-localization or intermediate-state evidence.

## 8. Forbidden claims

- the benchmark data are MIT-licensed or approved for redistribution;
- Phase 2 has selected four valid pilot tasks;
- the DRAFT table is semantic ground truth;
- all evaluator clauses are full/partial/none covered;
- any model or ProfiliTable method passed or failed these tasks;
- intermediate state is useful, causal, or novel;
- the archive or Python code is safe to execute;
- the benchmark is ready for publication.

## 9. Next gate

The next action requires human/mentor decisions, not more autonomous implementation:

1. obtain or document data-use/redistribution permission;
2. manually review every clause for the four candidates and finalize a non-DRAFT coverage table;
3. approve one independent property oracle per candidate;
4. approve semantic step/checkpoint boundaries;
5. decide GO/PIVOT/STOP for Stage 0.

Until those decisions are recorded, do not create mutants, reference workflows, checkpoints, LLM runs, or runtime integration changes.

## 10. Validation and review record

Original validation budget:

- one focused standard-library unit-test invocation;
- one real-package audit invocation;
- affected reruns only when a new material risk changes generated evidence;
- one final structural consistency check;
- one combined final review;
- source archive SHA-256 during audit generation; no routine Markdown/source hashes.

Checks actually completed:

- focused unit test command ran once on the initial implementation and once after each distinct repair batch; final state: 6 tests passed;
- real audit generation ran on the initial implementation and after each distinct evidence-affecting repair; final state: 127 tasks, 516 DRAFT rows, 127 AST-parseable evaluators, and 648/648 extracted-file CRC matches;
- each generation recomputed the mandatory archive SHA-256; four identical observations were produced because the classifier, public-content boundary, and final fail-closed review fixes each changed generated evidence. No additional archive hash was run;
- one final structural consistency check verified TSV schemas/counts, exact evaluator locations, withholding, changed-path scope, and whitespace;
- one combined independent milestone review was performed;
- source evaluators, generators, raw task data, model code, and LLMs were not executed.

Intentionally skipped: full build, full lint, E2E, runtime tests, evaluator execution, model runs, and source/runtime hashes. None covers a changed runtime risk in this audit-only branch.

### Combined review disposition

The sole combined review found 0 Critical, 3 Important, and 4 minor findings.

Important findings and fixes:

1. snake_case trace/checkpoint identifiers were missed — identifier tokenization and positive/negative fixtures added;
2. archive SHA was not fail-closed against same-size extraction changes — every extracted regular file is now CRC-bound, benchmark roots must stay inside the verified extraction, and mismatches abort before output generation;
3. public DRAFT rows copied evaluator snippets — default output now keeps only `eval.py:line|kind|symbol`; snippets require a separate opt-in.

Minor findings fixed: test-scope wording, pending handoff statuses, two trailing-space lines, and obsolete branch-example wording.

Final review disposition after focused repairs and self-verification: **PASS for Phase 2 mechanical delivery**. Human scientific/licensing gates remain open.

## 11. Environment note

The host health check reported a Google Chrome Gatekeeper/code-signing canary failure. This phase did not install/update software or launch GUI applications. Git/Python CLI operations continued, and the environment warning must not be interpreted as a benchmark failure.
