# Codex Execution Packet and Repository Hygiene

**Purpose:** keep the ProfiliTable fork usable as both a faithful upstream replication and a clean research workbench.

---

# 1. Repository strategy

Do not turn `master` into a research scratchpad.

Use:

```text
master
  = upstream replication baseline

research/benchmark-first-plan-v0.2
  = documentation + audit + pilot integration branch

future branches
  = one bounded experimental change each
```

Recommended future branches:

```text
research/upstream-audit
research/pilot-checkpoints
research/pilot-mutants
research/baseline-evaluators
research/natural-failure-collection
```

Merge only reviewable changes. Do not commit raw upstream benchmark data, model dumps, large trajectories, API responses, or temporary notebooks by default.

---

# 2. Local directory layout

Keep the tracked repository small. Store heavy/generated artifacts beside the repo, not inside Git history.

Recommended local layout:

```text
ProfiliTable/
  tracked source + research docs

../_worktrees/
  profilitable-upstream-audit/

../_research_cache/
  upstream_archives/
  extracted_data/
  model_cache/

../_research_runs/
  stage0/
  baselines/
  natural_failures/

../_research_exports/
  reviewed_small_tables/
  figures/
  paper_artifacts/
```

A worktree is preferable to repeatedly copying repositories.

Useful commands:

```bash
git worktree list
git status --short
git clean -ndX        # preview ignored generated files only
git clean -fdX        # remove ignored generated files only; use only after preview
```

Never use `git clean -fdx` casually because it also removes untracked non-ignored files.

---

# 3. What belongs in Git

Track:

- source code changes;
- research protocols;
- compact schemas;
- audit scripts;
- package hashes/manifests;
- reviewed TSV/Markdown summaries;
- small synthetic fixtures needed by tests;
- deterministic unit tests;
- benchmark cards and annotation guides.

Do not track by default:

- `.env`, API keys;
- virtual environments;
- extracted upstream `data/`;
- raw model outputs;
- giant table snapshots;
- logs;
- cached embeddings/models;
- local notebooks/checkpoints;
- generated benchmark packages before licensing review;
- unreviewed derived copies of upstream data.

---

# 4. Commit discipline

Every experimental commit should answer one question.

Good examples:

```text
docs: freeze benchmark-first research contract
audit: add reproducible upstream task inventory
feat: add semantic checkpoint instrumentation for four pilot tasks
test: add recovered-vs-persistent controls
eval: add dialogue-code baseline runner
```

Avoid:

```text
update stuff
research changes
fix all
new benchmark
```

Each PR/branch summary should state:

```text
Goal
Inputs
Outputs
Acceptance criteria
What is intentionally out of scope
Data/license impact
Research claim impact
```

---

# 5. Codex operating rule

Codex is allowed to automate reproducible engineering work, but it should not be allowed to silently define the scientific ground truth.

## Codex can do

- enumerate tasks;
- compute hashes;
- parse `task_meta.json`;
- inspect `eval.py` mechanically;
- create draft oracle-coverage rows;
- generate checkpoint instrumentation;
- construct mutations from an approved mutation grammar;
- run tests and evaluators;
- package track-specific inputs;
- run leakage checks;
- replay machine-checkable witnesses;
- summarize raw results without changing labels.

## Human review required

- whether a user requirement has been interpreted faithfully;
- whether `eval.py` fully/partially/not at all covers a requirement;
- whether a step boundary is semantically justified;
- whether a mutation changes only one semantic variable;
- source-vs-propagation adjudication;
- recovered-vs-persistent adjudication;
- data licensing / redistribution;
- novelty and paper claims;
- GO/PIVOT/STOP decision.

---

# 6. Codex Task 1 — Upstream audit

Give Codex this bounded task first.

```text
Goal:
Perform a reproducible audit of the fixed ProfiliTable public package and select candidate real base tasks for the benchmark-first pilot.

Fixed source:
Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec

Do not:
- create mutants
- run LLM benchmark baselines
- modify original task data
- commit extracted raw data
- claim novelty

Required outputs:
1. research/audit_results/package_manifest.tsv
2. research/audit_results/upstream_inventory.tsv
3. research/audit_results/oracle_coverage.DRAFT.tsv
4. research/audit_results/base_task_candidates.md
5. scripts/audit_upstream_package.py
6. tests/test_audit_upstream_package.py

Acceptance:
- package SHA-256 recorded
- all task counts recomputable
- all task_meta fields enumerated
- raw/expected/eval presence recorded
- draft evaluator coverage points to exact code locations
- no upstream raw data added to Git
- existing ProfiliTable behavior unchanged
```

The `oracle_coverage.DRAFT.tsv` is explicitly a machine-generated draft. A researcher must review and rename/finalize it.

---

# 7. Codex Task 2 — Controlled checkpoint pilot

Run only after Task 1 selects four tasks.

```text
Goal:
Create explicit semantic step functions and compact checkpoints for four reviewed base tasks without changing final clean semantics.

Requirements:
- preserve original raw inputs
- run original hidden evaluator for clean adjudication
- checkpoint only semantics required by the task contract
- keep full snapshots outside Git
- store compact metrics/digests in tracked fixtures
- add deterministic tests for each clean reference workflow
```

Human must approve step boundaries before mutation work begins.

---

# 8. Codex Task 3 — 4×4 variant generation

Use an approved mutation grammar only.

Allowed Stage-0 mutation forms:

```text
comparator boundary change
required-filter omission
stale revised constraint
aggregation-key/grain substitution
latest-record order reversal
input-overwrite side effect
```

For each base task:

```text
clean
persistent
recovered
benign equivalent
```

Codex may generate candidate variants, but a human must confirm single-variable semantics and the gold diagnosis.

---

# 9. Codex Task 4 — Evaluation packages and leakage checks

Produce separate input packages for:

```text
Native Outcome
Intent Reconstruction
Dialogue + Code
Given-Contract + State
End-to-End + State
```

Automated checks must fail if a deployment-like track includes:

```text
expected/gt.*
original eval.py
mutation ledger
variant label
gold violated atom
gold source step
gold witness
corrected workflow
```

---

# 10. Codex Task 5 — Result ledger

Do not optimize prompts against the 16 pilot cases repeatedly.

For every run store:

```text
instance_id
baseline_name
model/provider/version
prompt_hash
allowed_inputs_manifest
temperature/reasoning settings
retry policy
raw prediction
parsed prediction
latency
token usage
cost estimate
witness replay result
```

The research report must include every pilot run under the frozen configuration, not only the best attempt.

---

# 11. Git hygiene checklist before each push

```bash
git status --short
git diff --stat
git diff --check
```

Confirm:

- no API keys;
- no raw upstream data;
- no large generated outputs;
- no `.DS_Store`;
- no temporary notebooks;
- no local absolute paths;
- no speculative claim promoted from docs to README;
- source URLs/commit hashes are fixed where reproducibility matters.

---

# 12. Research cleanliness rule

Maintain three distinct artifact classes:

```text
SOURCE FACT
  paper / fixed repository / reproducible audit

GOLD ANNOTATION
  independently reviewed benchmark label

MODEL PREDICTION
  output of the evaluated system
```

Never let a model prediction silently become a gold annotation.

Never let a hidden GT artifact enter a reference-output-withheld evaluation package.

Never let an internal conversation be written as a public experimental result.

---

# 13. When to update upstream

Keep the fork's `master` close to upstream.

Before rebasing research work:

```bash
git fetch upstream
git log --oneline --decorate --graph --all -n 30
```

Do not blindly merge upstream during a frozen experiment. Record the source commit first. After an experiment finishes, update in a separate maintenance change and rerun the audit.

---

# 14. Minimum README policy

Do not rewrite the upstream README into a research manifesto yet.

Until Stage 0 is complete, keep the research plan in `TP2_BENCHMARK_FIRST_MASTER_PLAN.md` and `research/`.

Only add a short README pointer after the pilot is stable and if the fork becomes the long-term project home.
