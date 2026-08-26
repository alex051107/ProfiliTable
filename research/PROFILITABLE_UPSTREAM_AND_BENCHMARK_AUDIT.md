# ProfiliTable Upstream / Benchmark Audit Protocol

**Goal:** turn the current benchmark idea into a reproducible audit before generating any new benchmark instances.

**Fixed upstream:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`

---

## 1. Audit principles

1. Do not infer task counts from the paper when the package can be counted directly.
2. Do not assume `eval.py` covers the full natural-language requirement.
3. Do not treat a runnable script as a correct solution.
4. Do not commit upstream raw/derived benchmark data until redistribution rights are confirmed.
5. Every reported count must be recomputable by script and tied to a package SHA-256.
6. Stage-0 audit outputs are evidence about the upstream package, not benchmark results.

---

# 2. Local acquisition protocol

Clone/fetch the fork, then fetch the original upstream and pin the commit.

```bash
git clone git@github.com:alex051107/ProfiliTable.git
cd ProfiliTable
git remote add upstream https://github.com/Eularioal/ProfiliTable.git
git fetch upstream --tags
git switch research/benchmark-first-plan-v0.2
```

Verify the expected upstream commit exists:

```bash
git cat-file -t f023ec4b754555000a659b93fd514645c55e3cec
```

Create a detached audit worktree instead of contaminating the research branch:

```bash
mkdir -p ../_worktrees
git worktree add ../_worktrees/profilitable-upstream-audit \
  f023ec4b754555000a659b93fd514645c55e3cec
```

Run all raw-package inspection inside that worktree or a dedicated local cache directory.

---

# 3. Package manifest

Record at minimum:

```text
upstream_repo
upstream_commit
data_zip_path
data_zip_sha256
archive_size_bytes
audit_timestamp
python_version
platform
```

Command:

```bash
sha256sum data.zip
```

Store only the metadata in Git. Do not copy extracted upstream data into the research branch.

Recommended tracked output:

```text
research/audit_results/package_manifest.tsv
```

If project policy prefers no generated evidence committed yet, keep generated outputs under ignored `artifacts/` and commit only a reviewed summary later.

---

# 4. Task inventory audit

Recursively inspect the extracted package and produce one row per task.

Required columns:

```text
task_id
split_or_mode          # NL2Op / NL2Dag / other
relative_task_path
task_meta_present
raw_file_count
raw_file_types
expected_present
eval_py_present
target_en_present
target_zh_present
score_rule_present
task_type_declared
multi_input
notes
```

Questions this audit must answer:

- Does the fixed package contain 90 NL2Op tasks?
- Does it contain 39 or 37 NL2Dag tasks?
- Which paper-reported tasks are absent from the fixed package?
- Are there duplicate task IDs or incomplete task directories?
- Which tasks have missing/partial metadata?

Do not publish the 127-vs-129 discrepancy as a new factual claim until the inventory script and package hash are preserved.

---

# 5. Oracle coverage audit

For each candidate base task, manually and programmatically compare the natural-language instruction with the evaluator.

Create `oracle_coverage.tsv` with:

```text
task_id
requirement_id
requirement_text
requirement_type
eval_py_checks
coverage              # full / partial / none
check_mechanism
known_false_positive_risk
known_false_negative_risk
independent_oracle_possible
checkpoint_feasible
pilot_eligible
reviewer
notes
```

### Example

User requirement:

> Keep the latest row per patient.

Possible `eval.py` behavior:

```text
checks final patient IDs only
```

Coverage:

```text
partial
```

Reason:

```text
The evaluator can accept the correct ID set while retaining the wrong visit row for a patient.
```

This task can still be used, but the project must create an independent oracle for latest-record semantics.

---

# 6. First real base-task selection

Select four tasks only after oracle coverage is reviewed.

Preferred families:

1. filter/revision;
2. aggregation/grouping grain;
3. deduplication/latest-record semantics;
4. input preservation / side effect.

A task is eligible only if:

- the intended semantics can be stated unambiguously;
- a clean reference solution can be verified independently;
- a single-variable wrong-but-runnable mutation is possible;
- a recovered version can be constructed;
- a benign equivalent implementation is possible;
- step-level state can be checkpointed without altering semantics;
- the evaluator gap, if any, is documented rather than silently ignored.

Avoid in Stage 0:

- subjective entity resolution;
- free-text generation;
- external real-time knowledge;
- tasks with multiple equally valid but hard-to-enumerate output semantics;
- tasks where the correct intermediate semantics cannot be independently adjudicated.

---

# 7. Step/checkpoint instrumentation protocol

The fixed public workflow mainly generates and executes a complete Python script. Stage 0 therefore needs controlled instrumentation.

## Stage-0 approach

Rewrite a verified passing solution into explicit semantic functions:

```python
def step_1_filter(...): ...
def step_2_group(...): ...
def step_3_select_latest(...): ...
def step_4_write(...): ...
```

After each step, record a compact checkpoint:

```text
row_count
column_names
selected key statistics
semantic metrics required by active requirements
input/output digest
file events when relevant
```

Do not save giant full snapshots to Git.

Raw snapshot artifacts should live under an ignored local run directory; tracked benchmark instances should contain compact evidence summaries and reproducible checks.

## Stage-1 requirement

Before publication, test whether `first divergence` labels are stable under different reasonable segmentations.

At least one of the following is required:

- natural agent traces with event/checkpoint instrumentation;
- an automatic transformation-boundary extractor;
- segmentation sensitivity analysis.

Otherwise `first-step` gold risks reflecting researcher-chosen function boundaries rather than real workflow causality.

---

# 8. Stage-0 4×4 construction protocol

For each selected base task build:

### Clean

A reference workflow satisfying every final active requirement.

### Persistent mutant

Inject exactly one semantic mutation that:

- remains runnable;
- preserves output schema when possible;
- violates one targeted requirement;
- is not repaired before final submission.

### Recovered mutant

Start from the same mutation as the persistent case, then explicitly repair it later without irreversible side effects.

### Benign equivalent

Change implementation form without changing semantics.

Each variant needs a mutation/control ledger with:

```text
base_task_id
variant
changed_step
mutation_family
changed_expression
expected_violated_requirement
expected_recovery_step
allowed_side_effects
final_native_outcome
```

The ledger is construction-only and must never be visible to evaluated systems.

---

# 9. Required blind annotation

A second reviewer must not see:

- mutation ledger;
- variant name;
- gold source step;
- corrected workflow.

They receive dialogue, workflow, allowed snapshots, and must annotate:

```text
valid / invalid / unresolved
active requirements
violated requirement
source divergence
propagated symptoms
recovered transient
persistent/recovered status
evidence witness
```

Preserve both raw annotations and the adjudication log.

---

# 10. Baseline audit order

Run baselines from weakest to strongest:

1. Native final evaluator.
2. Final-output-only property checker.
3. Dialogue+code judge.
4. Direct-transfer trajectory diagnostic baseline (AgentRx/FALAT/DRIFT-style).
5. Gold-contract + state checker.
6. Predicted-contract + state checker.

The direct-transfer baseline is mandatory before novelty claims.

If a generic trajectory diagnostic method already solves the pilot without table states, the benchmark should pivot or stop.

---

# 11. Pilot decision table

## GO

Continue if state-aware diagnosis:

- uniquely solves several cases missed by text-only/trajectory baselines;
- produces replayable witnesses;
- separates persistent from recovered;
- keeps benign false rejection low;
- has stable annotation and manageable checkpoint cost.

## PIVOT

- stable violation, unstable source step → violation-only benchmark;
- gold contract works, predicted contract fails → intent reconstruction project;
- state helps but is expensive → adaptive evidence acquisition;
- controlled mutants diverge from natural failures → controlled diagnostic suite only.

## STOP

- direct-transfer baselines solve the task;
- snapshots add no value;
- oracle coverage is too weak;
- source-step labels depend strongly on segmentation;
- licensing prevents the intended release.

---

# 12. Audit outputs

Tracked reviewable outputs should be compact:

```text
research/audit_results/upstream_inventory.tsv
research/audit_results/oracle_coverage.tsv
research/audit_results/package_manifest.tsv
research/audit_results/base_task_selection.md
research/audit_results/pilot_decision.md
```

Large/generated files remain local under ignored paths.
