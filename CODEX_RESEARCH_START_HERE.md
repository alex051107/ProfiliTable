# Codex Research Start Here — ProfiliTable / DataFlow-Table

**Status:** Phase 3 Stage-0 design proposal prepared; human gate not passed
**Date:** 2026-08-27
**Working branch:** `research/pilot-task-selection`
**Upstream baseline:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`

---

## 0. Why this file exists

The research discussion has repeatedly narrowed because adjacent work already covers parts of the original idea. That created a risk of local optimization: polishing a diagnostic schema before confirming that the project is asking the right scientific question.

This file gives Codex the complete decision context and requires broad exploration before further implementation.

**Do not assume the current state-grounded diagnosis idea is correct.** Treat it as one candidate among several.

## 0.1 Phase 1 decision, Phase 2 audit, and Phase 3 design update

Phase 1 is complete. The current decision is:

- **Primary:** A — Table-Agent Capability Benchmark;
- **Fallback:** C — Method-First State-Grounded Evaluator;
- **Not selected as primary:** B — Process-Diagnostic Benchmark;
- **Deferred:** D — Harness / Self-Monitoring Integration.

The bounded Phase 2 public-package audit is complete. It reproduced the 127-task inventory, fixed the package SHA-256, generated an exact-line DRAFT evaluator-coverage queue, found material leakage/evaluator defects, and produced four conditional candidates.

Phase 3 has now prepared a data-free `DESIGN_PROPOSAL` with independent-oracle, checkpoint, control, and approval specifications. Three tasks remain provisional; the union task is on hold because its upstream contract supports output preservation but not input immutability. The approval queue is an unsigned template: its validator requires every decision and provenance field to remain unresolved and cannot authorize GO/PIVOT/STOP. No human approval, benchmark instance, reference workflow, mutation, checkpoint value, evaluator run, model run, or experimental result exists.

Read the current handoff package in this order:

1. `research/PHASE3_STAGE0_DESIGN_REVIEW.md` — current verdict, semantic corrections, experimental design, approval gate, and allowed actions;
2. `research/stage0/STAGE0_TASK_CONTRACTS.PROPOSED.json` — data-free proposed clauses, oracles, steps, checkpoints, ambiguities, and mutation concepts;
3. `research/stage0/STAGE0_APPROVAL_QUEUE.PROPOSED.tsv` — 18 human decisions required before Stage 0;
4. `research/PHASE2_HANDOFF_REVIEW.md` — completed mechanical audit, acceptance record, and remaining evidence boundaries;
5. `research/PHASE2_AUDIT_RATIONALE.md` — evidence-based audit and decision path;
6. `research/audit_results/base_task_candidates.md` — conditional shortlist, evaluator boundaries, and exclusions;
7. `research/audit_results/package_manifest.tsv` — fixed package identity and license boundary;
8. `research/audit_results/upstream_inventory.tsv` — one row per task bundle;
9. `research/audit_results/oracle_coverage.DRAFT.tsv` — machine-generated queue that remains unreviewed;
10. `research/PHASE1_HANDOFF_REVIEW.md` — primary/fallback formulation decision;
11. `research/RESEARCH_DECISION_MEMO.md` — GO/PIVOT/STOP rules;
12. `PROJECT_HANDOFF_2026-08-26.md` — project history and pre-Phase-1 context.

---

# 1. Original objective — preserve this north star

The original goal was not to build a state checker or another table benchmark for its own sake.

The intended research program is:

> Benchmark and improve whether a table agent can execute evolving user requirements correctly, recognize when it has made a semantic error, localize where the error began, and eventually repair it — in a way that can grow into an A-conference-quality benchmark/method/system contribution.

The evaluated subject should ultimately be the **table agent and/or its evaluator**, not merely a hand-authored mutant trajectory.

The capability ladder is:

1. **Execution:** Can the agent complete the current table task correctly?
2. **Intent tracking:** Can it maintain the latest active requirements after additions, revisions, or retractions?
3. **Self-detection:** Can it recognize that its own runnable workflow violates a requirement?
4. **Localization:** Can it identify the violated requirement and first source step rather than only the final symptom?
5. **Recovery:** Can it revise the workflow without introducing new failures?

A benchmark may cover only a subset, but it must state clearly which capability is being measured.

---

# 2. What has already been done in this fork

The branch `research/benchmark-first-plan-v0.2` currently adds research planning only. ProfiliTable runtime code on `master` has not been modified.

Existing documents:

- `PROJECT_HANDOFF_2026-08-26.md`
- `TP2_BENCHMARK_FIRST_MASTER_PLAN.md`
- `research/PAPER_GAP_AUDIT.md`
- `research/PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`
- `research/CODEX_EXECUTION_AND_REPO_HYGIENE.md`
- `research/NOVELTY_MATRIX.tsv`
- `research/ALTERNATIVE_FORMULATIONS.md`
- `research/DIRECT_TRANSFER_BASELINE_PLAN.md`
- `research/RESEARCH_DECISION_MEMO.md`
- `research/PHASE1_DECISION_RATIONALE.md`
- `research/PHASE1_HANDOFF_REVIEW.md`
- `research/PHASE2_AUDIT_RATIONALE.md`
- `research/PHASE2_HANDOFF_REVIEW.md`
- `research/audit_results/package_manifest.tsv`
- `research/audit_results/upstream_inventory.tsv`
- `research/audit_results/oracle_coverage.DRAFT.tsv`
- `research/audit_results/base_task_candidates.md`
- `scripts/audit_upstream_package.py`
- `tests/test_audit_upstream_package.py`
- an expanded `.gitignore`

These documents currently establish:

- multi-turn table tasks, evolving intent, first-error localization, source-vs-propagation analysis, and evidence-grounded root-cause diagnosis are **not safe standalone novelty claims**;
- ProfiliTable remains useful as a base-task pool and system under test;
- the currently hypothesized residual gap is whether executable intermediate table state adds diagnostic value beyond final-output and dialogue/code-only baselines;
- no benchmark contribution, model result, or novelty has been established;
- no raw benchmark data or generated experiment artifacts should be committed.

Do not duplicate these documents. Extend or correct them only when new evidence changes a decision.

---

# 3. The key conceptual correction

Intermediate table state is **not automatically the research goal**.

It can play three different roles:

1. **Hidden scoring evidence** used by benchmark authors to label a first semantic error;
2. **Evaluator input** for an external diagnosis track;
3. **Agent-observable feedback** used for self-monitoring or repair.

These are different experimental settings. Codex must not silently move between them.

The benchmark-first project should therefore compare several formulations, not assume formulation B below is the winner.

---

# 4. Required alternative formulations

Before coding, produce a side-by-side analysis of at least these four research formulations.

## Formulation A — Table-agent capability benchmark

**Subject:** the table agent.  
**Measures:** task execution, intent tracking, self-detection, localization, optional repair.  
**Input:** tables + multi-turn user interaction + tools.  
**Main question:** Can the agent do the task and know when it did not?

Potential strength: closest to the original goal.  
Main risk: overlap with CITBench, ProfiliTable, evolving-intent benchmarks, and agent self-correction work.

## Formulation B — Process-diagnostic benchmark

**Subject:** an external evaluator/diagnoser.  
**Measures:** violated requirement, source step, propagation, recovery, evidence.  
**Input:** dialogue/code/trajectory, optionally intermediate table states.  
**Main question:** Can a diagnostic system explain a failed table workflow?

Potential strength: controlled gold and detailed failure analysis.  
Main risk: overlap with DataSpace, AgentRx, FALAT, TELBench/DRIFT, DataTrace.

## Formulation C — Method-first state-grounded evaluator

**Subject:** a new diagnosis method.  
**Measures:** improvement over strong text/trajectory diagnosis, false rejection, evidence replayability, cost.  
**Main question:** Does table-state access produce measurable additional value?

Potential strength: clear technical comparison.  
Main risk: domain adaptation rather than general method novelty.

## Formulation D — Harness/self-monitoring integration

**Subject:** ProfiliTable/DataFlow-Table runtime.  
**Measures:** task success, semantic false acceptance, debugging iterations, cost, recovery.  
**Main question:** Does process-aware checking improve the actual table agent loop?

Potential strength: strongest systems relevance.  
Main risk: requires reliable benchmark/evaluator first and may become engineering-only.

Codex must recommend one primary formulation and one fallback only after the overlap audit and direct-transfer tests.

---

# 5. Novelty search method — do not search by one project name

Use a decomposition-based search. A candidate contribution is novel only if its **combination of task, supervision, output, and deployment setting** is not already covered.

For every relevant paper/repository, record the following fields in a structured matrix:

| Field | Required question |
|---|---|
| Evaluated subject | Agent, external evaluator, verifier, planner, repair system, or benchmark? |
| Domain | Table, spreadsheet, database, general tools, web, coding, mixed workspace? |
| Interaction | Single-turn, multi-turn, evolving requirement, interruption, task switch? |
| Agent input | What data/state/tools does the agent see? |
| Evaluator input | Final output, code, textual trajectory, environment state, intermediate tables, lineage? |
| Gold supervision | Full reference output, property checks, constraints, annotations, counterfactuals? |
| Main labels | Task success, active intent, violated constraint, source step, propagation, recovery, witness? |
| Error timing | Final only, first error, first unrecovered, decisive step, earliest observable? |
| Evidence | Natural-language rationale, trace span, row/cell/statistic, dependency path, executable check? |
| Repair | None, regenerate, local patch, counterfactual intervention? |
| Public artifacts | Paper version, code commit, task data, trajectories, evaluator? |
| Direct-transfer feasibility | Can its released method be run on ProfiliTable-style traces? |
| Claim blocked | Which novelty statement would this work invalidate? |
| Residual gap | What remains after this work is included? |

The matrix must distinguish:

- **paper claims**;
- **code/repository behavior**;
- **our inference**;
- **unverified assumptions**.

---

# 6. Search axes and required source groups

Search each axis separately. Do not stop after finding one adjacent paper.

## Axis 1 — Table/spreadsheet ability benchmarks

Required starting set:

- ProfiliTable
- DataGovBench / DataGovAgent
- CITBench
- SpreadsheetBench and SpreadsheetBench 2
- DataSpace
- BIRD-INTERACT
- SheetMind and other end-to-end spreadsheet agents

Questions:

- Is the agent evaluated only on final output, or also on process/self-monitoring?
- Are requirement revisions real or synthetic?
- Are intermediate states exposed, logged, or scored?
- Is first error or repair part of the benchmark?

## Axis 2 — Evolving/latent user intent

Required starting set:

- UserIntentBench
- LLMs Get Lost in Evolving User Intent
- AgentChangeBench
- InterruptBench
- related long-horizon goal-shift or stale-constraint benchmarks

Questions:

- How is current intent represented?
- Who sees the gold intent graph?
- Are actions/data states aligned to intent, or only textual beliefs/final outcomes?
- Can the method transfer to deterministic table semantics?

## Axis 3 — Failure localization and trajectory diagnosis

Required starting set:

- DataSpace process audit
- AgentRx
- FALAT
- TELBench/DRIFT
- HINTBench
- TrajDebug or newer trajectory-debugging work

Questions:

- How is first/source/critical error defined?
- Does the method require expected final output?
- How are recovered errors treated?
- Is evidence executable or only textual?
- What would a direct transfer to ProfiliTable require?

## Axis 4 — Data/database provenance and root-cause evidence

Required starting set:

- DataTrace
- mlinspect
- BigDebug
- database provenance / lineage debugging
- data pipeline root-cause benchmarks

Questions:

- How are state transitions and dependency paths represented?
- Is the witness row/cell/statistic executable?
- Is user intent dynamic or fixed?
- Is the task to diagnose a known failure, or to benchmark an agent's own ability?

## Axis 5 — Agent verification, contracts, and repair

Required starting set:

- Lean4Agent
- AgentSpec / VIGIL-like policy enforcement
- RunAgent
- Task Shield
- ContractSkill
- CausalFlow
- metamorphic testing and selective evidence acquisition work

Questions:

- Is the contract human-authored, model-generated, or inferred?
- What does the verifier guarantee?
- What remains unverified if the contract is wrong?
- Is repair local, minimal, or only token-small?

## Axis 6 — Benchmark methodology

Search benchmark-design literature for:

- construct validity;
- evaluator coverage;
- annotation/adjudication reliability;
- controlled mutants versus natural failures;
- contamination and near-duplicate leakage;
- difficulty calibration;
- benchmark saturation;
- data provenance and licensing.

This axis is necessary before scaling a pilot into a publishable benchmark.

---

# 7. Query design

Use multiple query families rather than one broad search.

Examples:

```text
"interactive table agent benchmark" evolving requirements
"spreadsheet agent" process evaluation intermediate state
"table workflow" semantic error localization benchmark
"data pipeline" first failure root cause benchmark executable evidence
"agent trajectory diagnosis" recovered error propagation
"LLM agent" self-monitoring semantic failure table
"database pipeline" row-level witness root cause localization
"benchmark design" controlled mutation natural failure agent
```

For each core work, also search:

```text
<paper name> code github
<paper name> appendix evaluator
<paper name> dataset schema
<paper name> failure taxonomy
<paper name> intermediate state
<paper name> first error recovered
```

Prioritize official arXiv pages, conference pages, project sites, and fixed GitHub commits. Record versions and retrieval dates.

---

# 8. Direct-transfer tests — novelty cannot be literature-only

Before claiming a residual gap, test the strongest adjacent methods on a small shared slice.

At minimum compare:

1. final-output/property checker;
2. dialogue + code/trajectory judge;
3. an AgentRx-style constraint/evidence diagnosis;
4. a FALAT/DRIFT-style source-vs-propagation diagnosis;
5. a state-aware table diagnosis, only if intermediate state is available.

The central empirical comparison is:

```text
Does table-state access solve any cases that the strongest text/trajectory baselines cannot solve,
without creating unacceptable clean/benign false rejections?
```

If no, stop the state-grounded novelty path.

If yes, determine whether the gain comes from:

- better intent reconstruction;
- deterministic table properties;
- direct observation of data effects;
- easier synthetic cases;
- leakage from gold contracts or mutation labels.

---

# 9. Required Codex deliverables before implementation

Create or update only the following research outputs. Do not add miscellaneous notes.

## Deliverable 1 — `research/NOVELTY_MATRIX.tsv`

One row per work, using the fields in Section 5.

## Deliverable 2 — `research/ALTERNATIVE_FORMULATIONS.md`

Compare Formulations A–D using:

- scientific question;
- evaluated subject;
- required assets;
- closest overlaps;
- potential novelty;
- falsifying evidence;
- six-week feasibility;
- A-conference upside;
- fallback path.

## Deliverable 3 — `research/DIRECT_TRANSFER_BASELINE_PLAN.md`

Specify exactly how DataSpace/AgentRx/FALAT/DRIFT/DataTrace-style baselines would be represented and tested on the same ProfiliTable slice.

## Deliverable 4 — `research/RESEARCH_DECISION_MEMO.md`

Select:

- one primary formulation;
- one fallback;
- explicit claims allowed/forbidden;
- the next empirical gate;
- GO/PIVOT/STOP conditions.

No runtime implementation should begin until these four outputs are internally consistent with `TP2_BENCHMARK_FIRST_MASTER_PLAN.md` and `research/PAPER_GAP_AUDIT.md`.

---

# 10. Explore-first execution protocol

Codex must follow this order.

## Phase 0 — Reconstruct context

Read:

1. this file;
2. `TP2_BENCHMARK_FIRST_MASTER_PLAN.md`;
3. `research/PAPER_GAP_AUDIT.md`;
4. `research/PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`;
5. `research/CODEX_EXECUTION_AND_REPO_HYGIENE.md`;
6. ProfiliTable paper and fixed upstream code.

Then write a short context reconstruction before making changes:

```text
Original objective
Current candidate gap
Known overlap
What has been implemented
What remains unverified
```

If its reconstruction contradicts the files, stop and resolve the contradiction first.

## Phase 1 — Broad exploration

- Complete the novelty matrix.
- Produce at least three plausible research directions, including one that does **not** rely on intermediate table states.
- Identify the strongest work that could invalidate each direction.
- Search for disconfirming evidence, not only supporting evidence.

## Phase 2 — ProfiliTable audit

**Completed mechanically on 2026-08-27:**

- reproduce task inventory and package hash;
- audit `task_meta.json`, raw data, GT, and `eval.py` coverage;
- identify candidate real tasks;
- do not commit raw/derived data.

Scientific completion remains gated by data-rights confirmation, manual clause coverage, independent-oracle approval, and checkpoint-boundary approval.

## Phase 3 — Empirical gate design

Design the smallest experiment that distinguishes the surviving formulations.

Examples:

- agent execution/self-monitoring track;
- external diagnosis track;
- state-vs-no-state ablation;
- gold-contract-vs-predicted-contract separation.

## Phase 4 — Implementation

Implement only after a research decision memo identifies the primary formulation and its falsifying test.

---

# 11. Local-minimum prevention rules

Codex must not:

- assume the current repository title or plan is the final paper framing;
- improve a schema simply because it exists;
- keep adding synthetic fixtures before real-task and overlap audits;
- treat intermediate state as automatically useful;
- treat first-error localization as standalone novelty;
- interpret a lower model score as proof of benchmark quality;
- compare only against ProfiliTable final scoring;
- use the same model to generate tasks, infer gold, and judge results without independent checks;
- create a new document when an existing living document should be updated;
- commit raw tables, unpacked archives, model outputs, cache, logs, or secrets.

Every proposed direction must include a **kill test**:

> What result would make us stop claiming this direction is novel or useful?

---

# 12. Repository and branch discipline

- Keep `master` aligned with the upstream replication baseline.
- Preserve `research/benchmark-first-plan-v0.2` as the Phase 1 decision baseline.
- Use `research/upstream-audit` for the completed Phase 2 audit.
- Use short-lived implementation branches only after Phase 3, e.g.:
  - `research/pilot-task-selection`
  - `research/baseline-transfer`
  - `research/agent-capability-pilot`
- Store generated outputs under ignored local directories such as `artifacts/`, `runs/`, `logs/`, or `research/local/`.
- Commit scripts, schemas, small manifests, and summarized results — not source archives or full run dumps.
- Every result must record source commit, model version, prompt/config, random seed where applicable, and artifact hash.

---

# 13. Decision standard for novelty

A safe novelty statement must pass all three tests:

## Test 1 — Coverage

No directly adjacent work already provides the same evaluated subject, inputs, labels, and outputs.

## Test 2 — Incremental evidence

The proposed information or method solves cases that the strongest direct-transfer baseline does not.

## Test 3 — Consequence

The new measurement changes at least one real decision:

- model ranking;
- failure taxonomy;
- debugging time;
- repair choice;
- acceptance/rejection of a workflow;
- ProfiliTable/DataFlow-Table task success or cost.

If the new labels only produce a more detailed narrative but do not change a decision, the contribution is weak.

---

# 14. Current recommended immediate task

Do **not** expand the state checker, create mutants, or run models yet.

Phase 3 has converted the conditional shortlist into a data-free proposal and an explicit approval queue. The immediate task remains a human/mentor gate:

1. confirm data-use and redistribution permission;
2. review or correct the four candidates' proposed atomic contracts;
3. approve or revise the independent property oracles;
4. approve or revise checkpoint boundaries;
5. resolve whether the fourth task measures output preservation or must be replaced for input-side-effect semantics;
6. approve mutation semantics only after the preceding decisions;
7. record GO/PIVOT/STOP for Stage 0.

The DRAFT coverage table and the `DESIGN_PROPOSAL` must not be renamed or treated as ground truth before that review. A formal decision must be recorded in a separately reviewed successor artifact or protected human-approval workflow; editing the proposed queue is not approval. Internal assets, ownership, redistribution, reference workflow construction, mutation generation, pilot implementation, model runs, and integration changes remain gated.

State becomes the method direction only if a later reference-hidden ablation demonstrates replayable, decision-relevant value over strong text/trajectory baselines.
