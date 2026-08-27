# Conditional Base-Task Candidates

**Status:** Phase 2 shortlist; no task is approved for mutation or pilot construction
**Fixed source:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`
**Package SHA-256:** `a5c46f5c0d71a4886ed7c6cebb737814dff0587038f45bed58a40d9d96fafcb6`
**Audit date:** 2026-08-27

This document records a four-family conditional shortlist. It does not finalize semantic ground truth, license permission, checkpoint boundaries, mutations, or Stage-0 admission.

## 1. Selection rule

A candidate was retained only when the public package supplies all four structural components—`task_meta.json`, nonempty `raw/`, nonempty `expected/`, and an AST-parseable `eval.py`—and the task exposes a mechanically testable operation related to one planned pilot family.

Final eligibility still requires a human reviewer to approve:

1. the English/Chinese requirement interpretation;
2. an independent property oracle rather than reliance on `expected/` alone;
3. evaluator coverage for every active clause;
4. semantically justified checkpoint boundaries;
5. data-use and redistribution permission;
6. a later single-variable mutation/control design.

## 2. Shortlist

| Planned family | Conditional candidate | Why it is useful | Native evaluator boundary | Current disposition |
|---|---|---|---|---|
| Filter / revision | `NL2Op/T0114_filter_muti` | Three independently revisable predicates over four input tables plus an explicit master-schema preservation clause | Exact column comparison, then row accuracy only over the shorter GT/prediction prefix | retain for human clause review; not pilot-approved |
| Aggregation grain | `NL2Op/T0074_wide_table_construction` | Explicit per-user grain, 30-day window, three aggregates, and a left join | Exact multiset over GT columns; ignores row order and allows extra columns | strongest current aggregation candidate; not pilot-approved |
| Dedup / latest record | `NL2Op/T0011_incremental_deduplication` | Two-source incremental merge with key, latest timestamp, winning-row preservation, and output-order requirement | Penalizes duplicate/extra/missing IDs and wrong full rows; does not enforce ascending output order | retain with independent timestamp/tie oracle; not pilot-approved |
| Output preservation; side-effect role unresolved | `NL2Op/T0047_multi_csv_union` | Requires file/row order, duplicates, field values, and schema to remain intact in the union output | Strict parsed row-and-column equality of final output only | hold for package-drift resolution; the source task does not state input immutability |

The source tasks are static. Any evolving requirement or revision sequence would be a later reviewed benchmark design, not an observed upstream feature.

## 3. Candidate-specific coverage review

### 3.1 Filter / revision — `NL2Op/T0114_filter_muti`

Observed instruction:

- `task_meta.json:1` describes whitelist membership, category membership, a channel-specific minimum amount, conjunction of all predicates, and exact preservation of the master table's columns/order.

Observed evaluator:

- `eval.py:54-59` requires exact column names and order;
- `eval.py:61-64` truncates GT and prediction to `min(len(gt), len(pred))`;
- `eval.py:78-84` scores equality only within that truncated prefix.

Consequence: a short output can avoid direct penalty for omitted tail rows. The evaluator also does not express the three filter predicates independently, so a score does not localize which requirement failed.

Independent-oracle design proposal:

- compute each predicate from its relevant auxiliary table;
- require their conjunction per master-table row;
- compare the exact retained-row multiset and exact master schema;
- reject both missing and extra rows;
- use input-identity comparison only as an experiment-safety control unless a human adds and approves an explicit input-immutability contract atom.

Human gate: define a natural revision sequence and boundary cases for whitelist/category/threshold changes. The upstream task itself contains no revisions.

### 3.2 Aggregation grain — `NL2Op/T0074_wide_table_construction`

Observed instruction:

- `task_meta.json:1` specifies user grain, a 30-day window relative to `2024-08-31`, `orders_cnt`, `orders_gmv`, `clicks_cnt`, left join, and zero filling.

Observed evaluator:

- `eval.py:15-18` declares a GT-column row-multiset comparison;
- `eval.py:56-59` rejects missing GT columns but permits extra columns;
- `eval.py:61-64` compares exact multisets over GT columns and therefore checks missing/extra rows within that projection;
- `eval.py:65-70` may print sample missing or extra reference rows to stderr.

Consequence: the final GT projection is comparatively strong for row/value agreement, but it does not independently expose window, grouping-grain, aggregation, or join clauses. If evaluator diagnostics enter an iterative agent loop, the printed reference rows could also violate a reference-hidden condition.

Independent-oracle design proposal:

- recompute the time-window membership with explicit open/closed boundaries;
- recompute the three aggregates per `user_id`;
- assert one output row per source user;
- validate the exact required schema and zero-fill policy;
- keep oracle diagnostics hidden from the evaluated agent.

Human gate: choose one grain-changing revision that is not confounded with a simultaneous window or join change.

### 3.3 Dedup / latest record — `NL2Op/T0011_incremental_deduplication`

Observed instruction:

- `task_meta.json:1` specifies historical JSONL plus incremental CSV, deduplication by `id`, latest `updated_at`, full winning-row preservation, original timestamp formatting, and ascending `id` order.

Observed evaluator:

- `eval.py:51-59` strips every CSV field before comparison;
- `eval.py:84-104` penalizes empty IDs, duplicate IDs, extra IDs, and full-row mismatch;
- `eval.py:106-111` accounts for missing IDs in F1;
- it never checks the required ascending output order.

Consequence: the evaluator covers final record identity and content more strongly than an ID-set-only scorer, but not output order. CSV whitespace normalization also weakens exact preservation.

Independent-oracle design proposal:

- compare the original ISO-form timestamp strings lexicographically and fail closed on divergent equal maxima until a tie policy is approved;
- choose the latest record per ID directly from both inputs;
- require exact winning-row values and no duplicate/extra/missing IDs;
- evaluate ascending output order separately;
- compare input bytes before/after only in a later isolated pilot.

Human gate: freeze equal-timestamp behavior, lexical identifier ordering, and whether format preservation is semantic or representational. The source contract explicitly says not to parse timestamps into datetime objects.

### 3.4 Output preservation; side-effect role unresolved — `NL2Op/T0047_multi_csv_union`

Observed instruction:

- `task_meta.json:1` requires vertical union in input-file order and in-file row order, with no deduplication or field modification and with `NA` treated as text.

Observed evaluator:

- `eval.py:43-54` parses every CSV row without stripping field values;
- `eval.py:65-72` checks output existence and `.csv` suffix;
- `eval.py:75-82` requires the parsed output rows, including header and order, to equal GT exactly.

Observed package drift:

- packaged inputs are `raw/customer1.csv` and `raw/customer2.csv`, while `gen_data.py:20-22` writes `customers1.csv` and `customers2.csv`;
- the packaged first raw CSV contains a blank record that the current generator does not emit;
- the evaluator receives only the final output path and cannot detect input overwrites or extra filesystem side effects.

Independent-oracle design proposal:

- first resolve whether the blank record is an intended row and refreeze the package contract;
- compare the exact parsed concatenation with explicit blank-row policy;
- run any later code against copied read-only inputs;
- compare before/after input identities and sandbox file inventories as experiment-safety controls, not as this source task's semantic oracle.

Human gate: resolve package/generator drift and decide whether output preservation is an acceptable fourth family. The upstream task cannot ground an input-overwrite violation unless a new, separately authored immutability requirement is approved.

## 4. Hard exclusions and holds

### Exclude: `NL2Op/T0010_normalize_numbers`

The inventory found `raw/formatted_20251202144816.csv` parsed-row-for-row equivalent to `expected/gt.csv`, even though the instruction describes one input CSV. This is direct answer leakage. Do not use the task until the input package is corrected and refrozen.

### Exclude: `NL2Op/T0113_data_imputation_muti`

`eval.py:36` hardcodes `expected/gt.csv`, while its mask logic at `eval.py:105-121` looks for `**` markers. Only the second expected file contains those markers. The chosen GT therefore yields zero evaluated cells, and `eval.py:142-150` returns zero for every parseable candidate. Do not use this evaluator without a separately authorized upstream-compatible repair and regression test.

### Hold: `NL2Op/T0087_linear_interpolation_for_missing_columns`

The raw directory contains both `customers.csv` and the derived-looking `interpolated_dataframe.csv`, while the task text describes one input. It is not equivalent to GT, but input visibility is ambiguous. Resolve the intended input set before use.

### Hold: path/content mismatches

Five NL2Dag directory names say `jsonl` while packaged raw and expected files are CSV. The strongest mismatch is `NL2Dag/T0002_jsonl_trim_spaces_dedupe_by_id_latest_updatetime`: its instruction is actually CSV URL/language/grammar filtering. Do not select tasks from directory names alone.

## 5. Decision

The four tasks remain the best current structural shortlist for the planned families, but **Phase 2 does not authorize Stage 0**. The immediate blockers are data-license/redistribution evidence, manual clause-to-evaluator review, independent-oracle approval, and checkpoint-boundary approval.

No mutants, reference solutions, checkpoints, model runs, or benchmark instances were produced in this phase.
