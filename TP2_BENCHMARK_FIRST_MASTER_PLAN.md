# TP2 — DataFlow-Table / ProfiliTable Benchmark-First Master Plan

**Status:** research design v0.2  
**Date:** 2026-08-26  
**Branch:** `research/benchmark-first-plan-v0.2`  
**Upstream code baseline:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`  
**Purpose:** define a falsifiable benchmark-first entry point that can later support an A-conference-quality evaluation/method paper, without claiming novelty before the residual gap is empirically established.

---

## 0. North Star

The long-term goal is **not** to create another table benchmark for its own sake.

The target problem is:

> How can an evaluator diagnose whether a table-processing agent remains faithful to the user's current requirements when requirements evolve, code remains runnable, and a complete reference-output table is unavailable at evaluation time?

The candidate residual gap is narrower:

> **Do versioned user requirements + executable intermediate table states provide measurable diagnostic value beyond final-output scoring and text/code trajectory diagnosis?**

If the answer is **no**, the benchmark-novelty path should stop or pivot. If the answer is **yes**, the project can expand toward a process-level benchmark, a state-grounded diagnostic method, and eventually adaptive evidence acquisition / harness integration.

---

# 1. What the current literature already covers

The following claims are **not safe novelty claims**.

## 1.1 Multi-turn / evolving table tasks are already covered

- **CITBench** (`arXiv:2608.00018v1`) already evaluates interactive tabular processing with multi-turn evolving requirements, four high-level categories, 18 task types, and 1,296 instances.
- **LLMs Get Lost in Evolving User Intent** (`arXiv:2607.20734v1`) converts static tasks into reveal/revision/task-switch interactions while preserving original evaluation protocols.

Therefore we should not claim:

> “first multi-turn table benchmark” or “first evolving-intent benchmark”.

## 1.2 Active/shifting intent tracking is already covered

- **UserIntentBench** publicly represents latent/shifting intent with an intent graph, tracks belief-vs-oracle alignment over time, and reports post-shift alignment and stale/obsolete intent diagnostics.

Therefore we should not claim:

> “first active intent representation” or “first stale requirement tracking”.

## 1.3 Earliest unrecovered failure / root-cause localization is already covered

- **DataSpace** includes process-level failure auditing in addition to deterministic final-table evaluation.
- **AgentRx** synthesizes constraints, evaluates trajectories step-by-step, records evidence, and localizes a critical failure step.
- **FALAT** explicitly separates error source from downstream propagation using dependency-guided search and counterfactual sufficiency.
- **TELBench/DRIFT** studies span-level error localization and earliest harmful commitments with evidence/dependency reasoning.

Therefore we should not claim:

> “first first-error localization”, “first source-vs-propagation diagnosis”, or “first evidence-grounded root-cause framework”.

## 1.4 Complex spreadsheet/workspace tasks are already covered

- **SpreadsheetBench 2** evaluates realistic end-to-end business workbooks and reports inspection / target-selection failure modes.
- **DataSpace** evaluates complete tabular answers over heterogeneous workspaces with deterministic evaluation.

Therefore we should not claim that realistic workbooks, heterogeneous files, or deterministic final-table scoring are new by themselves.

---

# 2. Candidate residual gap

The still-plausible research space is the following combination:

1. **Versioned table intent** — the evaluator knows which user requirements are currently active, superseded, or newly introduced.
2. **Executable table-state transitions** — each workflow step has observable before/after table state, not only a textual trace.
3. **Machine-checkable witness** — a diagnosis points to a row/cell/statistic/file event that can be replayed by code.
4. **Reference-output-withheld diagnosis** — diagnostic tracks do not read the complete expected output table or original task-specific evaluator at evaluation time.
5. **Incremental-value requirement** — the benchmark is only justified if intermediate table state solves cases that strong final-only and trajectory-only baselines do not.

This is a **candidate gap**, not established novelty.

---

# 3. Running example

Input tables:

```text
patients(patient_id, age)
visits(patient_id, encounter_id, date, status, cost)
```

User turn 1:

> Keep patients strictly older than 65, exclude canceled visits, aggregate the cost of the latest visit per patient, and do not modify the source sheets.

User turn 2:

> Only consider visits after 2025-01-01.

The final active requirements can be represented as:

```yaml
A1: age > 65
A2: status != canceled
A3: date > 2025-01-01
A4: latest visit per patient_id
A5: aggregate cost at patient grain
A6: preserve original inputs
```

A runnable but semantically wrong workflow may use:

```python
df = df[df["age"] >= 65]  # wrong boundary
```

The desired diagnosis is not merely `wrong final table`.

It should be able to return:

```text
violated requirement: A1
source step: S1 AgeFilter
code evidence: age >= 65
state witness: a row with age=65 remains after S1
propagation status: later steps consume the wrong state
recovery status: not repaired before commit
```

If a later step correctly removes `age == 65`, the earlier error is a recovered transient, not a persistent final failure.

---

# 4. Benchmark target: what we measure and what we do not

## 4.1 Track A — Native Outcome

**Visible to evaluator:** final artifact; hidden GT and original `eval.py` are used by the benchmark harness.  
**Measures:** final task correctness.  
**Purpose:** retain comparability with ProfiliTable-style scoring.  
**Not a novelty claim.**

## 4.2 Track B — Intent Reconstruction

**Visible:** multi-turn dialogue only.  
**Hidden:** gold atoms, workflow, snapshots, complete output GT.  
**Measures:** whether the evaluator reconstructs the current active/superseded requirements.  
**Direct baselines:** UserIntentBench-style intent tracking; evolving-intent prompting baselines.

## 4.3 Track C — Given-Contract Diagnosis

**Visible:** gold versioned intent atoms + workflow/code + intermediate snapshots.  
**Hidden:** complete output GT, original `eval.py`, mutation ledger, gold source-step/witness labels.  
**Measures:** execution diagnosis when the correct requirement interpretation is already known.

This isolates the table-state diagnosis problem from intent reconstruction.

## 4.4 Track D — End-to-End Diagnosis

**Visible:** dialogue + workflow/code + intermediate snapshots.  
**Hidden:** gold atoms, complete output GT, original `eval.py`, mutation ledger, gold diagnosis.  
**Measures:** joint intent reconstruction + execution diagnosis.

**Terminology:** use `reference-output-withheld at evaluation time`, not `oracle-free`.

---

# 5. Benchmark task taxonomy

The first pilot should emphasize error families where code can run and schemas can remain valid.

## Family 1 — Boundary and filter semantics

**Example requirement:** `age > 65`.  
**Mutant:** `age >= 65`.  
**Why runnable:** both are valid pandas predicates.  
**Intermediate evidence:** minimum retained age, or a specific retained row with `age=65`.  
**Gold diagnosis:** violated atom `A1`, source at AgeFilter.  
**Why final-only is insufficient:** it may detect a different result but does not identify the boundary error or provide a local witness.

## Family 2 — Requirement revision / stale rule

**Turn 1:** visits on or after `2025-01-01`.  
**Turn 2:** revise to strictly after `2025-01-01`.  
**Mutant:** workflow continues using `>=`.  
**Intermediate evidence:** minimum retained date equals `2025-01-01`.  
**Gold diagnosis:** current atom violated; old atom is lineage/context, not the current violated requirement.

## Family 3 — Aggregation grain

**Requirement:** one result per patient.  
**Mutant:** group by `encounter_id`.  
**Intermediate evidence:** rows per patient, unique patient count vs unique encounter count.  
**Gold diagnosis:** wrong grain at aggregation step.  
**Why text-only can fail:** both identifiers are valid fields and code is syntactically/structurally plausible.

## Family 4 — Latest-record semantics

**Requirement:** keep the most recent visit per patient.  
**Mutant:** sort ascending and keep first; or deduplicate before the required sort.  
**Intermediate evidence:** selected visit date per patient vs local maximum date.  
**Gold diagnosis:** latest-selection step.

## Family 5 — Required exclusion / omitted operation

**Requirement:** exclude canceled visits.  
**Mutant:** omit the filter entirely.  
**Intermediate evidence:** count of `status == canceled` after the obligation boundary.  
**Gold diagnosis:** missing operation at the semantic commit point, not at an invented nonexistent step.

## Family 6 — Join/cardinality semantics (Stage 1, not first-week core)

**Requirement:** one-to-one patient merge.  
**Mutant:** join through a non-unique key.  
**Intermediate evidence:** duplicate amplification, unmatched ratio, key uniqueness.  
**Risk:** harder gold because multiple valid implementations may exist.

## Family 7 — Input preservation / irreversible side effect

**Requirement:** do not modify source sheets/files.  
**Mutant:** write in place, then later produce a correct final output.  
**Intermediate evidence:** before/after file digest or workbook state.  
**Gold diagnosis:** write/materialization step.  
**Why final-table scoring can miss it:** final prediction may be correct while the environment contract was violated.

## Family 8 — Benign equivalent control

**Requirement:** same semantics as a clean case.  
**Variant:** `df.query("age > 65")` vs `df[df.age.gt(65)]`.  
**Purpose:** detect false rejection from superficial implementation matching.

---

# 6. Pilot design: Stage 0

The first pilot remains **4 base tasks × 4 variants = 16 instances** because the goal is construct validity, not statistical estimation.

Choose four real ProfiliTable tasks, ideally covering:

1. filter/revision;
2. aggregation grain;
3. dedup/latest-record selection;
4. input preservation / side effect.

For each base task construct:

| Variant | Purpose |
|---|---|
| clean | fully correct reference workflow |
| persistent mutant | one runnable semantic error remains to final commit |
| recovered mutant | same early error appears, but is explicitly repaired before final commit |
| benign equivalent | different implementation, same semantics |

The persistent and recovered variants must share the same mutation source; the only essential difference is whether the violation is repaired.

### Why 16 is enough for Stage 0

It is enough to test:

- whether the definitions can be annotated consistently;
- whether checkpoint instrumentation works;
- whether a state-aware checker gains anything over a text-only checker;
- whether recovered vs persistent errors can be distinguished;
- whether benign controls expose false-positive behavior.

It is **not** enough to claim generalization, AUC improvement, or publication-level benchmark quality.

---

# 7. ProfiliTable reuse strategy

## 7.1 What can be reused directly

From the fixed upstream version:

- natural-language task descriptions;
- raw task inputs;
- reference outputs (`expected/gt.*`) where present;
- task-specific `eval.py`;
- the existing Agent workflow as a system-under-test;
- task family metadata where available.

## 7.2 What must be rebuilt for this project

ProfiliTable does not natively provide the process annotations required here. We must add:

- versioned multi-turn requirements;
- explicit step boundaries for the pilot;
- intermediate input/output snapshots;
- mutation ledger;
- source-vs-propagation labels;
- persistent-vs-recovered labels;
- executable row/cell/stat/file witnesses;
- explicit oracle-coverage records.

## 7.3 Do not assume the original evaluator covers the entire user instruction

Each candidate base task requires `oracle_coverage.tsv` with:

```text
task_id
requirement_atom
source_text
eval_py_checks_it (yes/no/partial)
check_mechanism
known_gap
independent_oracle_possible
checkpoint_feasible
pilot_eligible
```

The original `eval.py` is an adjudication aid, not automatically a complete semantic oracle.

## 7.4 Step-boundary bias

The first controlled pilot may manually rewrite passing solutions into explicit step functions.

However, that can bias `first step` labels. Therefore the formal benchmark must later include at least one of:

1. natural agent traces with instrumented data-state checkpoints;
2. a stable transformation-boundary extraction rule;
3. multiple reasonable segmentations with label-stability analysis.

A publication cannot rely solely on researcher-chosen step boundaries without sensitivity analysis.

---

# 8. Strong baselines required before novelty claims

At minimum:

1. **Native final evaluator** — hidden GT + original `eval.py`; outcome reference only.
2. **Final-output-only property checker** — no complete GT; check only properties derivable from the task.
3. **Dialogue + code/trajectory judge** — no intermediate states.
4. **AgentRx-style constraint/evidence diagnosis** — direct transfer baseline.
5. **FALAT/DRIFT-style dependency-aware diagnosis** — direct conceptual baseline.
6. **Gold-contract + state checker** — isolates execution diagnosis.
7. **Predicted-contract + state checker** — end-to-end.

The key result is not “our model has higher accuracy.” The key test is:

> **Does explicit intermediate table state solve instances that strong dialogue/code/trajectory baselines still misdiagnose, while preserving low false rejection on clean/benign/recovered cases?**

If not, benchmark novelty should stop.

---

# 9. Metrics

Stage-0 metrics are reported per instance, not with significance claims:

- runnable + schema-valid count;
- native outcome pass/fail;
- violated-atom exact match;
- source-divergence exact / ±1 step;
- persistent-vs-recovered correctness;
- clean/benign false rejection count;
- executable-witness replay success;
- abstention / unresolved count;
- raw annotator agreement and all disagreements;
- evaluator latency/token/cost.

Stage-1/full benchmark can add:

- macro/micro F1 over violation classes;
- localization metrics;
- selective risk vs coverage;
- cross-task / cross-mutation / cross-model generalization;
- annotation reliability with confidence intervals;
- incremental diagnostic utility (e.g., reduced human diagnosis time or improved repair selection).

---

# 10. GO / PIVOT / STOP

## GO

Continue benchmark + method development if:

- state snapshots produce clear additional evidence in at least three distinct semantic error families;
- persistent and recovered cases are reliably separated;
- benign/clean false rejection remains low;
- witnesses replay successfully;
- strong trajectory-diagnosis transfer baselines still leave interpretable errors;
- instrumentation cost is manageable.

## PIVOT

- violated atom is stable but source step is not → focus on violation detection, not localization;
- gold-contract diagnosis works but end-to-end fails → focus on intent reconstruction / contract induction;
- state is useful but full inspection is expensive → develop adaptive evidence acquisition;
- synthetic mutants work but natural failures differ → position as a controlled diagnostic suite, not a real-failure benchmark.

## STOP

Stop benchmark-novelty framing if:

- AgentRx/FALAT/DRIFT/DataTrace transfer directly solves the target;
- snapshots do not add measurable value over dialogue+code;
- recovered vs persistent cannot be labeled reliably;
- independent oracle coverage cannot be established;
- data licensing prevents the intended release;
- new labels do not change any practical comparison, diagnosis, or method decision.

---

# 11. Stage-1 benchmark expansion if Stage 0 succeeds

Do **not** simply scale synthetic mutants.

A stronger benchmark must contain two separately reported distributions:

### Controlled mutations

Purpose: clean causal labels.

- one semantic variable changed;
- mutation ledger known;
- reproducible source step;
- reversible where possible.

### Natural agent failures

Purpose: ecological validity.

Generate runs from multiple agents/backbones and manually audit naturally occurring failures.

Do not merge the two distributions into one headline number.

### Required split discipline

Group by base workflow. Never split variants from the same base task across train/test.

Later add:

- held-out task family;
- held-out mutation family;
- held-out operator pattern;
- held-out agent/backbone;
- paraphrase/revision style holdout.

---

# 12. A-conference paper shapes

## Benchmark-only

**Shape:** new task set + process labels.  
**Risk:** high overlap with CITBench, UserIntentBench, DataSpace, DataTrace, AgentRx.  
**Current recommendation:** insufficient alone unless the process target proves strongly distinct and large-scale.

## Benchmark + evaluation protocol

**Shape:** versioned intent + snapshots + executable witness evaluation.  
**Risk:** may still look like a domain-specific recombination of existing ideas.  
**Potential:** moderate if annotation reliability and diagnostic utility are strong.

## Benchmark + method

**Shape:** process benchmark + state-grounded diagnostic method.  
**Potential:** strongest near-term target.

## Benchmark + method + system integration

**Shape:** process benchmark + state-grounded diagnosis + integration into ProfiliTable/DataFlow-Table, demonstrating lower semantic false acceptance / fewer debugging iterations / better task success under reference-output-withheld conditions.  
**Potential:** strongest overall paper shape, but only after Stage-0/Stage-1 evidence.

No venue acceptance is implied.

---

# 13. Method directions after a successful pilot

## 13.1 State-grounded diagnosis

Build an explicit mapping:

```text
intent atom
↕
workflow operation
↕
observable table-state effect
```

Diagnoses should be grounded in executable data witnesses rather than free-form rationales.

## 13.2 Dependency-aware diagnosis

Use data/control dependencies to separate source divergence from propagation.

Novelty risk: FALAT/DRIFT/DataTrace already occupy adjacent space. Table-specific semantics and executable state witnesses must show measurable incremental value.

## 13.3 Adaptive / minimal evidence acquisition

Instead of reading all intermediate tables, choose the next probe based on expected information gain and cost.

Example candidate probes for `one row per patient`:

```text
check group key
check patient_id uniqueness
check rows-per-patient
check duplicate amplification
inspect full lineage
```

Possible objective:

```text
probe* = argmax(expected ambiguity reduction / probe cost)
```

This becomes method-worthy only if state access is materially expensive and selective probes retain reliability.

## 13.4 Selective abstention / repair

If evidence is insufficient, output `unresolved` rather than fabricate a diagnosis. Repair should be a later extension, not a Stage-0 gate.

---

# 14. Immediate execution sequence

The project should proceed in this order:

```text
1. Upstream audit
2. Oracle-coverage audit
3. Select four real ProfiliTable base tasks
4. Build clean step-wise references + checkpoints
5. Construct 4×4 controlled pilot
6. Run strong baselines
7. Blind annotation + witness replay
8. GO / PIVOT / STOP
9. Only then scale benchmark
10. Only after headroom is established, develop new method
```

Detailed audit and repository procedures live under `research/`.

---

# 15. Current factual gaps that must remain DATA_INSUFFICIENT

Until directly confirmed, do not assume:

- internal ProfiliTable/DataFlow-Table has process labels or intermediate states;
- the public package contains exactly the same task count as the paper;
- all `eval.py` scripts cover all user semantics;
- ProfiliTable benchmark data can be redistributed in a derivative benchmark;
- project ownership, authorship, target venue, GPU access, mentor availability, or internal repository access;
- DataTrace has a stable peer-reviewed/preprint paper matching the current public repository.

---

# 16. Three-sentence group update

> I am not trying to claim another multi-turn table benchmark or another generic first-error benchmark; those settings are already substantially covered.  
> I am testing a narrower hypothesis: whether versioned user requirements aligned with real intermediate table states provide executable diagnostic evidence that final-output and text-only trajectory evaluators miss.  
> If the pilot shows clear incremental value, I will scale it into a process benchmark and then develop a state-grounded / cost-aware evaluator that can plug back into ProfiliTable or DataFlow-Table.
