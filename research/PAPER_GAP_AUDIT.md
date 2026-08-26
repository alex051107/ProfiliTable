# Paper / Gap Audit for Benchmark-First DataFlow-Table Research

**Status:** living evidence map  
**Date:** 2026-08-26  
**Rule:** separate `Observed`, `Inference`, and `Design decision`. Do not promote a residual gap to novelty until direct-transfer baselines and pilot evidence support it.

---

## 1. Why this audit exists

The research question has repeatedly narrowed because adjacent work already covers substantial parts of:

- multi-turn table processing;
- evolving/shifting user intent;
- final-output evaluation;
- process-level error localization;
- source-vs-propagation diagnosis;
- evidence-grounded root cause analysis.

The goal of this file is to prevent accidental reinvention and to define what must still be learned before a benchmark or method claim is safe.

---

# 2. Core source matrix

| Source | Directly observed contribution | What it blocks us from claiming | What still needs checking |
|---|---|---|---|
| ProfiliTable, arXiv:2605.12376v2 | Dynamic profiling; operator retrieval; feedback refinement; 18 table task types; hidden GT/task-specific evaluator for final outputs | runnable-vs-correct is not new; table-specific generation/refinement already exists | exact public task inventory; `eval.py` semantic coverage; internal intermediate-state support; data redistribution rights |
| DataGovBench/GovBench, arXiv:2512.04416 | 150 data-governance tasks; operator + DAG tasks; reversed-objective noise; task-specific evaluators; Planner-Executor-Evaluator | multi-step data-governance evaluation is not new | exact overlap of mutation families with our controlled errors; whether current release exposes intermediate artifacts |
| CITBench, arXiv:2608.00018v1 | interactive tabular processing; 4 categories/18 task types/1,296 instances; offline+online; evolving requirements/noise | first interactive/evolving table benchmark is not safe | exact online evaluator visibility; whether any process/intermediate-state gold exists; whether full-result matrix remains the scoring oracle in all tracks |
| LLMs Get Lost in Evolving User Intent, arXiv:2607.20734v1 | static-to-evolving conversion via reveal/revision/redirection while preserving native verifier | converting static tasks into evolving intent is not new | exact transformation operators and whether the framework can be directly applied to ProfiliTable |
| UserIntentBench, public repo `d294828...` | hidden intent graph; shifting/latent intent; belief graph; post-shift alignment; obsolete-constraint/stale-evidence diagnostics | active intent graph, intent shift recovery, stale requirement tracking are not new | formal paper status; whether its graph-scoring machinery transfers cleanly to deterministic table requirements |
| DataSpace, arXiv:2608.03451v1 | 410 heterogeneous-workspace tasks; deterministic complete-table evaluation; process audit/failure taxonomy | heterogeneous workspace, deterministic final table evaluation, generic process auditing not new | Appendix process-audit operational details; exact earliest-unrecovered definition; direct-transfer feasibility to table-state traces |
| SpreadsheetBench 2, arXiv:2606.29955v1 | 321 realistic business workbook tasks; generation/debugging/visualization; failure taxonomy | realistic multi-sheet workbook workflow benchmark is not new | whether intermediate cell-state trajectories are available; how debugging ground truth is represented |
| AgentRx, arXiv:2602.02475v1 | 115 failed trajectories; constraint synthesis; stepwise evidence validation; critical-step localization | constraint+evidence+critical-step diagnosis is not new | code availability; how much domain adaptation is needed for table-state semantics |
| FALAT, arXiv:2606.00765v1 | dependency-guided failure attribution; source-vs-propagation; counterfactual sufficiency | source-vs-propagation and decisive-step localization are not new | whether final expected output is required; transfer to data-state checkpoints |
| TELBench/DRIFT, arXiv:2606.02060v2 | span-level error localization; earliest harmful commitments; claim/evidence/dependency auditing | evidence-aware first-error analysis is not new | applicability to executable table-state evidence rather than text claims |
| DataTrace, HKUSTDial/datatrace | public database root-cause benchmark/evaluator; dependency graph/evidence path/root-cause framing | database evidence-grounded root-cause localization is not new | formal paper version; exact data format; whether evolving intent is absent; direct-transfer baseline implementation |
| Toolathlon, arXiv:2510.25726v2 | long-horizon real tool use with real initial state and deterministic task evaluators | real-state, cross-app long-horizon evaluation is not new | process diagnostic availability; state reset/replay protocol relevance |
| DataFlow-Harness, arXiv:2607.16617v2 | typed pipeline mutation; live state; schema/DAG validation; commit boundary | structural platform-native workflow validation is already explicit | whether current internal DataFlow-Table integrates Harness semantics |

---

# 3. Claims ledger

## 3.1 Already covered — do not claim novelty

- `runnable != semantically correct`;
- multi-step table workflow evaluation;
- multi-turn/evolving user requirements;
- active/obsolete requirement tracking;
- first/critical unrecovered error localization in generic trajectories;
- source error vs propagated symptom distinction;
- evidence-grounded root-cause analysis in generic agent or database settings;
- realistic multi-sheet spreadsheet workflows;
- deterministic final-output table evaluation.

## 3.2 Candidate residual claims — pilot required

- explicit intermediate **table state** gives measurable diagnostic value beyond dialogue+code/trajectory-only diagnosis;
- row/cell/statistic/file-state witnesses reduce unsupported diagnosis and improve replayability;
- versioned table intent + table-state transitions help separate intent-reconstruction errors from execution errors;
- a table-specific state-grounded evaluator remains useful when the full expected output table is withheld at evaluation time;
- state access is costly enough that adaptive evidence acquisition becomes a meaningful method problem.

## 3.3 Claims to delete unless new evidence appears

- first evolving-intent table benchmark;
- first semantic verifier;
- first first-error/root-cause localization benchmark;
- first evidence-grounded data-workflow diagnosis;
- fully oracle-free evaluation;
- globally minimal repair;
- comprehensive superiority over CITBench/DataSpace/SpreadsheetBench 2.

---

# 4. Missing knowledge that can change the project direction

## K1 — ProfiliTable public task/evaluator reality

Need a reproducible audit of:

- actual `NL2Op` / `NL2Dag` counts at fixed commit;
- task metadata fields;
- which tasks contain full GT;
- what each `eval.py` checks;
- which natural-language requirements are not covered by the evaluator;
- whether checkpoints can be inserted without changing semantics.

**Decision impact:** determines whether ProfiliTable is a usable base-task pool or only a system-under-test.

## K2 — CITBench process visibility

Need to verify from paper + code:

- what the online agent can see;
- whether explicit intermediate tables or cached state snapshots are exposed;
- whether scoring remains tied to final locked result matrices;
- whether root-cause/process labels exist.

**Decision impact:** if CITBench already exposes the same process state and labels, benchmark novelty shrinks sharply.

## K3 — DataSpace process audit transfer

Need exact operationalization of:

- earliest observable/unrecovered divergence;
- failure taxonomy;
- workspace evidence used in adjudication;
- counterfactual or replay logic.

**Decision impact:** defines the strongest process-diagnosis baseline.

## K4 — AgentRx / FALAT / DRIFT transfer cost

Need an implementation-level test, not only conceptual comparison.

Question:

> If we feed these methods versioned requirements + code trace but no intermediate tables, how well do they already solve our pilot?

**Decision impact:** if direct transfer is already strong, the only defensible contribution is the incremental value of executable table-state evidence.

## K5 — DataTrace status

Need to monitor:

- stable dataset release;
- paper/preprint availability;
- exact evidence path representation;
- whether tasks include user-intent evolution.

**Decision impact:** may eliminate broad `data evidence + RCA` novelty claims.

## K6 — Benchmark design methodology

Need a focused review of:

- construct validity;
- annotation reliability;
- contamination / near-duplicate leakage;
- difficulty calibration;
- evaluator coverage;
- benchmark saturation;
- controlled synthetic mutation vs natural failure distribution;
- public data licensing and provenance.

**Decision impact:** required before scaling Stage 0 into a paper-quality benchmark.

## K7 — Natural failure distribution

Need actual ProfiliTable/DataFlow-Table runs from multiple backbones or internal traces.

Questions:

- Do stale-requirement, wrong-grain, side-effect, join-cardinality errors actually occur naturally?
- Or are the proposed mutants mostly researcher-invented?

**Decision impact:** determines whether the benchmark can claim real-agent relevance.

## K8 — State instrumentation semantics

Need to answer:

- what is a stable semantic step boundary?
- how should chained pandas expressions be segmented?
- does segmentation change the `first divergence` label?
- which file/table events are observable and replayable?

**Decision impact:** without stable segmentation, localization labels are fragile.

---

# 5. Search/review queue

Do not keep expanding the bibliography indiscriminately. Search only to answer the following unresolved questions.

## Queue A — benchmark overlap

1. CITBench full paper + construction code: process-state visibility and evaluator details.
2. DataSpace Appendix process audit: exact diagnosis protocol.
3. DataTrace repo/paper: exact evidence-path and RCA representation.
4. SpreadsheetBench 2 appendix/code: debugging and inspection trajectory labels.

## Queue B — evolving intent

1. UserIntentBench current public protocol and evaluation schema.
2. `LLMs Get Lost in Evolving User Intent`: transformation operators and preserved-native-verifier assumptions.
3. Any table/spreadsheet-specific dynamic-requirement benchmark published after 2026-08-01.

## Queue C — process diagnosis

1. AgentRx code and output schema.
2. FALAT candidate pruning/counterfactual requirements.
3. DRIFT claim/evidence/dependency data structures.
4. New post-2026-06 trajectory debugging benchmarks that distinguish recovered vs persistent errors.

## Queue D — state/provenance diagnosis

1. mlinspect / data lineage systems as evidence infrastructure.
2. database RCA / provenance benchmarks with executable witness paths.
3. methods for selective/adaptive evidence retrieval only if Stage 0 shows state evidence is valuable but expensive.

---

# 6. Evidence standard for future paper claims

Every substantive claim in the eventual paper should map to one of:

- official paper section/table;
- fixed repository commit/path;
- reproducible local audit script + package hash;
- pre-registered pilot result;
- independent annotation/adjudication record.

Do not cite a conversation summary as experimental evidence.

---

# 7. Current review verdict

**Benchmark-first remains a reasonable entry point only as a falsifiable measurement study.**

The research should not yet be described as a new benchmark contribution. The next empirical question is:

> Does executable intermediate table state add diagnostic information beyond strong final-only and trajectory-only baselines?

Only if the answer is yes should the project scale into benchmark construction and method development.
