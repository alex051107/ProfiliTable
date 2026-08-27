# Phase 3 Stage 0 Design Review

**Status:** `DESIGN_PROPOSAL` prepared; Stage 0 gate not passed
**Date:** 2026-08-27
**Branch:** `research/pilot-task-selection`
**Fixed source:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`

## 1. Decision

Do not start the 4 × 4 pilot yet. Three candidates have feasible independent-oracle and checkpoint proposals, while the fourth remains on hold because its upstream contract supports output preservation but does not state that source files must remain unchanged. Data rights and all scientific approvals are also open.

The current Codex recommendation is **PIVOT BEFORE STAGE 0**:

1. retain the filter, aggregation, and latest-record candidates as provisional;
2. decide whether the fourth family should measure output preservation or use a different task with an explicit input-immutability requirement;
3. resolve the review queue before creating reference workflows, mutations, checkpoints, or runs.

This recommendation is not the human GO/PIVOT/STOP decision.

## 2. What this phase produced

The design package contains no source rows, expected outputs, executable reference workflow, mutation, checkpoint value, model output, or gold annotation.

- `research/stage0/STAGE0_TASK_CONTRACTS.PROPOSED.json` — four data-free, paraphrased task contracts with proposed clauses, independent property oracles, semantic steps, compact checkpoints, ambiguities, and mutation concepts;
- `research/stage0/STAGE0_APPROVAL_QUEUE.PROPOSED.tsv` — 18 explicit human decisions with evidence requirements and blocked downstream actions;
- `scripts/validate_stage0_design.py` — proposal-shape validator for artifact class, fixed source identity, structured oracle-input roles, cross-references, exact approval-subject coverage, and an entirely pending gate;
- `tests/test_validate_stage0_design.py` — focused positive and negative fixtures.

All approval-bearing task, oracle, checkpoint, and mutation review fields remain `CODEX_PROPOSED` or `UNREVIEWED`; candidate dispositions remain three `PROVISIONAL` and one `HOLD`, and the gate remains `NOT_READY`. The Phase 2 `oracle_coverage.DRAFT.tsv` remains unchanged and has not been renamed or promoted to ground truth.

## 3. Candidate disposition

| Candidate | Proposed role | Technical feasibility | Current disposition | Decisive unresolved issue |
|---|---|---|---|---|
| `NL2Op/T0114_filter_muti` | composite filter plus a newly authored revision | independent row-membership and schema properties are feasible | `PROVISIONAL` | the upstream task is static; revision wording and active-atom lineage need approval |
| `NL2Op/T0074_wide_table_construction` | time-windowed aggregation at user grain | independent window, grain, aggregate, join, and fill properties are feasible | `PROVISIONAL` | output schema, duplicate-user, parsing, and numeric-representation policies are unstated |
| `NL2Op/T0011_incremental_deduplication` | lexicographic last-write-wins merge | independent winner, identifier, field, order, and format properties are feasible | `PROVISIONAL` | equal-maximum ties and identifier ordering are unstated |
| `NL2Op/T0047_multi_csv_union` | ordered output preservation | independent header, sequence, duplicate, value, and empty-segment properties are feasible | `HOLD` | no input-immutability clause; packaged inputs and generator also drift |

## 4. Semantic corrections made during review

### 4.1 The filter task does not contain a revision

Its three predicates and schema rule are source facts. Any later threshold change, comparator change, or stale-rule turn would be newly authored benchmark content. The proposal therefore records the revision as a human-gated mutation concept rather than describing it as an upstream feature.

The native evaluator is unsuitable as the primary admission gate. It compares only the shorter output/reference prefix, so omitted or appended tail rows can avoid direct penalty. The proposed oracle instead recomputes all predicates from the rule inputs and checks the full retained row multiset plus master schema.

### 4.2 The aggregation evaluator is a regression check, not an independent oracle

The native evaluator strongly compares the final row multiset on its reference columns, but it permits extra columns and cannot localize window, grain, aggregation, join, or zero-fill errors. Its diagnostics may expose reference rows. The proposed oracle independently derives window membership and per-user aggregates and keeps reference-derived diagnostics outside deployment-like views.

### 4.3 Latest-record comparison is lexical

The source contract explicitly requires lexicographic comparison of the original timestamp strings. The independent oracle must not parse datetimes or invent a timezone policy. It should abstain or fail closed when different records share the same maximum timestamp until a tie rule is approved.

The native evaluator does not enforce ascending identifier order and accepts CSV even though the source contract asks for JSON Lines.

### 4.4 Output preservation is not input immutability

The union task requires ordered concatenation, duplicate retention, unchanged output field values, literal handling of `NA`, and empty-segment handling. It does not say that source files cannot be overwritten. An input digest can still be used as an experiment-safety control, but it cannot become this task's violated requirement or gold diagnosis.

The fixed package contains one zero-field blank record inside a nonempty input. A raw-derived row-preserving union includes it, while the packaged reference omits it. Ignoring that record makes the parsed union agree, but that silently equates an empty row with an empty file segment. The clean contract is therefore not unique until a human resolves the blank-record policy.

The currently proposed unintended-deduplication mutation is outside the frozen mutation grammar. A human must either amend that grammar, redefine the fourth family as output preservation, or replace this task.

## 5. Independent-oracle standard

Each proposed oracle is intended to derive from task inputs and contract properties rather than `expected/gt.*` or the native `eval.py`. Every oracle specifies:

- the minimum input roles it needs;
- the property it recomputes;
- a compact, replayable mismatch witness;
- `uses_expected_output=false`;
- `uses_native_evaluator=false`;
- `approval_status=UNREVIEWED`.

Full output snapshots and actual witness values remain outside Git. Tracked specifications name only metrics, digests, counts, positions, and witness structure.

The static validator checks each oracle against a structured input-role allowlist and rejects direct reference-artifact tokens in the property and witness text. This is a limited shape and leakage check. It cannot prove semantic independence, inspect a future implementation, or substitute for human oracle review.

## 6. Proposed checkpoint rule

A checkpoint is placed only where a task obligation becomes committed or where a later step could hide the original error:

- filter: rule lookup → predicate vector → output commit;
- aggregation: windowed events → user aggregates → joined feature output;
- latest record: unified pool → winner selection → ordered serialized output;
- union: ordered input inventory → per-file row streams → merged output.

These boundaries are deliberately fewer than the implementation steps. They remain proposed because researcher-chosen segmentation can bias first-error labels. Approval should compare at least one reasonable alternative segmentation per task.

## 7. Experimental design if the gate later passes

### Question and unit

The question is whether intermediate table state provides replayable diagnostic information that final-output and dialogue/code evidence miss. The experimental unit is one approved base-task variant, not one clause, checkpoint, row, or witness.

### Blocking and paired comparison

Base task is the block. Every approved evaluator view receives every approved instance under a frozen visibility contract, creating a paired repeated-measures comparison. Task families must remain separate in reporting; 16 controlled cases are a construct audit, not a representative sample.

### Controls

- clean: false-rejection control;
- persistent: positive semantic-violation control;
- recovered: lifecycle control with the same source mutation repaired before commit;
- benign equivalent: implementation-form false-rejection control.

Persistent and recovered cases must share the same source mutation and remain a nested matched pair in any later analysis; they are not independent variants. Checkpoints within one instance are not independent replicates.

### Run order and blinding

No run schedule or seed has been generated. After approval, evaluator-view order should be counterbalanced within task blocks and recorded with one fixed seed. Deployment-like packages must hide expected outputs, native evaluators, variant labels, mutation ledgers, gold diagnoses, witnesses, and corrected workflows.

### Stage 0 stopping logic

Stage 0 is not a significance test. It should stop or pivot when property oracles are unstable, task-role semantics do not match the planned family, recovered/persistent labels depend on arbitrary segmentation, reference-hidden packages leak gold, or data rights do not cover the planned use.

## 8. Human approval queue

The 18-row queue contains:

- one data-rights decision;
- four requirement-interpretation decisions;
- four independent-oracle decisions;
- four checkpoint-boundary decisions;
- four mutation-semantics decisions;
- one final GO/PIVOT/STOP decision.

Every row is assigned to `HUMAN_PM_OR_MENTOR`, remains `PENDING` and `UNDECIDED`, binds to exact contract subject IDs, and provides blank provenance slots for a future decision record. The current proposal validator requires those fields to remain blank and rejects every GO/PIVOT/STOP transition. It does not authenticate a reviewer or validate a signature.

A formal decision therefore needs a separately reviewed successor artifact or protected approval workflow with reviewer identity, timestamp, rationale, evidence reference, and readback. No such approval-bearing mechanism is implemented in this phase.

## 9. Allowed and forbidden next actions

Allowed now:

- review or correct the paraphrased clauses;
- approve, reject, or revise the property-oracle definitions;
- approve or revise checkpoint boundaries;
- resolve the fourth task's role;
- document data-use and redistribution evidence;
- record the human GO/PIVOT/STOP decision.

Still forbidden:

- treating this proposal as gold annotation;
- creating clean reference workflows or 4 × 4 variants;
- executing source generators or native evaluators;
- running models or baseline judges;
- publishing source data, derived task packages, or witness values;
- claiming state benefit, benchmark validity, novelty, or experimental results.

## 10. Validation and review record

Validation budget for this batch:

- one focused unit-test invocation for the proposal validator;
- one static validation of the shipped design package;
- one combined final review because this is a scientific gate milestone;
- no archive rehash, package regeneration, evaluator execution, model run, full build, lint, or E2E.

Completed checks:

- before combined review, `python3 -m unittest tests/test_validate_stage0_design.py` passed 6 tests and `python3 scripts/validate_stage0_design.py` returned `valid: true`;
- the combined milestone review returned `FIX` with 1 Critical, 3 Important, and 2 Minor findings;
- repairs made the JSON contract trackable, converted the validator to proposal-only lifecycle enforcement, introduced structured oracle-input roles and literal dependency checks, bound every queue row to exact contract subjects, corrected the six-clause filter approval, removed input immutability from the union task step, and recorded the nested matched-pair boundary;
- one syntax/import preflight was run after the validator rewrite to catch a partial-patch failure;
- the affected post-repair rerun passed all 6 unit tests, including forged transition, reference-dependency, and subject-binding negatives;
- the affected post-repair static validation returned `valid: true` with 4 tasks, 28 proposed clauses, 14 independent-oracle proposals, 12 checkpoint proposals, and 18/18 pending human decisions;
- no archive hash, package regeneration, evaluator execution, source generator execution, reference workflow, mutation artifact, model run, full build, lint, or E2E was performed.

All review findings were addressed and the affected checks passed. No second independent review was run because the repairs did not introduce a new architecture or scientific decision.
