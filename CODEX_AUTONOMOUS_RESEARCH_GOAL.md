# Codex Autonomous Research Goal — ProfiliTable / DataFlow-Table

**Status:** executable research charter  
**Branch:** `research/phase2-autonomous-audit`  
**Parent decision branch:** `research/benchmark-first-plan-v0.2`  
**Frozen runtime baseline:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`  
**Primary formulation:** A — Table-Agent Capability Benchmark  
**Fallback formulation:** C — Reference-Output-Withheld State-Information-Gain Evaluator

---

## 1. Mission

Autonomously advance this project from the completed Phase 0/1 research decision into a reproducible Phase 2 audit and, only when the predeclared gate passes, a bounded empirical pilot.

The north star is not to create another benchmark for its own sake. The project aims to determine whether a Table Agent can:

1. execute the latest active user requirements correctly;
2. track additions, revisions, and retractions;
3. recognize its own semantic failure despite runnable code;
4. localize the violated requirement and first source step;
5. recover or repair without introducing new failures.

Intermediate table state is not assumed to be the contribution. It may serve as:

- hidden scoring evidence for the capability benchmark;
- an input treatment in the fallback evaluator study;
- later, agent-visible feedback in a self-monitoring integration.

Do not silently switch among these roles.

---

## 2. Operating mode

Work proactively. Do not pause for routine user review after each subtask.

You may:

- inspect public papers, official project pages, and fixed public repository revisions;
- create bounded research branches and worktrees;
- write audit scripts, tests, compact manifests, reviewed summaries, and reproducible reports;
- run local deterministic tests and public-source audits;
- commit and push non-destructive changes to research branches;
- open and update draft pull requests;
- perform a self-review of each PR, fix findings, and continue to the next authorised phase;
- update progress, decision, and risk logs when evidence changes a decision.

You must not:

- merge into `master`;
- force-push or rewrite remote history;
- change repository visibility, collaborators, permissions, or ownership;
- access internal lab repositories, data, trajectories, or labels without explicit credentials and authorisation;
- publish or redistribute raw ProfiliTable data or derived benchmark instances before licence/provenance approval;
- commit API keys, `.env`, raw data, large snapshots, model dumps, logs, caches, or unreviewed derived artifacts;
- incur paid API cost unless an explicit machine-readable budget is present in the repository or environment;
- claim novelty, authorship, venue, acceptance, ownership, or lab commitment;
- treat a model-generated label as scientific ground truth without independent adjudication.

When a human-dependent boundary blocks one path, continue all other authorised work and record the blocker in the PR and progress log. Stop only when every remaining path is blocked or a formal kill condition is met.

---

## 3. Canonical reading order

Before changing anything, read in this order:

1. `research/PHASE1_HANDOFF_REVIEW.md`
2. `research/RESEARCH_DECISION_MEMO.md`
3. `research/PHASE1_DECISION_RATIONALE.md`
4. `research/ALTERNATIVE_FORMULATIONS.md`
5. `research/DIRECT_TRANSFER_BASELINE_PLAN.md`
6. `research/NOVELTY_MATRIX.tsv`
7. `CODEX_RESEARCH_START_HERE.md`
8. `PROJECT_HANDOFF_2026-08-26.md`
9. `research/PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`
10. `research/CODEX_EXECUTION_AND_REPO_HYGIENE.md`

Then produce a short internal context reconstruction in the active PR description. Do not create another long handoff document unless a decision materially changes.

---

## 4. Current scientific decision

### Primary route A

Evaluate the Table Agent itself. The main capability ladder is:

- final execution correctness;
- latest-intent tracking;
- calibrated self-detection and abstention;
- violated-clause and source-step localization;
- recovery and later local repair.

The main agent track must not receive benchmark-injected intermediate state. Checkpoints may be retained as hidden scoring evidence.

### Fallback route C

Only promote state-grounded evaluation to a method direction if, under the same reference-output-withheld cases and matched budget, state or lineage:

- solves cases missed by strong dialogue/code/trajectory baselines;
- supplies replayable row/cell/statistic/file evidence that cannot be reconstructed from the no-state trace;
- changes a decision such as exact localization, accept/retry, repair success, false acceptance, or cost.

### Routes not currently primary

- B remains the diagnostic scoring layer and direct-transfer baseline suite, not the paper identity.
- D remains deferred until a reliable evaluator exists and local repair beats matched retry or full regeneration.

---

## 5. Phase 2 — mandatory upstream audit

### Goal

Establish whether the fixed public ProfiliTable package can support a lawful, independently adjudicated, process-aware pilot.

### Required outputs

Create:

```text
research/audit_results/package_manifest.tsv
research/audit_results/upstream_inventory.tsv
research/audit_results/oracle_coverage.DRAFT.tsv
research/audit_results/base_task_candidates.md
research/audit_results/licence_and_provenance.md
scripts/audit_upstream_package.py
tests/test_audit_upstream_package.py
research/PHASE2_PROGRESS.md
```

### Audit requirements

1. Fix and record the exact upstream source and retrieval date.
2. Compute and record the `data.zip` SHA-256 without committing the archive or extracted data.
3. Recompute all `NL2Op` and `NL2Dag` counts from the fixed package.
4. Enumerate every task's:
   - task id and path;
   - metadata fields;
   - user instruction(s);
   - raw input presence and shape summary;
   - expected output presence;
   - `eval.py` presence and exact path;
   - `score_rule` presence;
   - candidate task family.
5. Mechanically inspect each `eval.py` and draft clause-to-check coverage with exact code locations.
6. Distinguish:
   - what the evaluator actually checks;
   - what the natural-language task requires;
   - what remains untested;
   - whether an independent semantic property oracle is feasible.
7. Assess whether a semantics-preserving step/checkpoint boundary can be introduced.
8. Record upstream licence, source provenance, and redistribution uncertainty. Code MIT does not establish data redistribution rights.
9. Recommend four real tasks only when all four have:
   - traceable provenance;
   - a usable independent semantic-oracle plan;
   - a feasible checkpoint boundary;
   - enough construct diversity;
   - no unresolved blocking licence issue for the intended local pilot.

### Phase 2 pass condition

Phase 2 passes only if four tasks defensibly cover:

- filter or requirement revision;
- aggregation grain;
- deduplication with latest-record semantics;
- input preservation or irreversible side effect.

If fewer than four qualify, reduce the pilot or pivot before implementation. Do not manufacture weak tasks to fill the quota.

---

## 6. Phase 2 review loop

After generating the audit outputs:

1. run all new and existing deterministic tests;
2. verify every reported count from the script output;
3. verify every evaluator-coverage row points to an exact file and line/range or a clearly marked `DATA_INSUFFICIENT`;
4. inspect the Git diff for raw data, generated junk, secrets, and unsupported claims;
5. perform one independent-style self-review with severity labels:
   - `CRITICAL`
   - `IMPORTANT`
   - `MINOR`
6. fix all `CRITICAL` and `IMPORTANT` findings;
7. update the draft PR with:
   - findings;
   - fixes;
   - remaining risks;
   - Phase 2 pass/pivot/stop status.

Do not call the phase complete merely because tests pass. Tests establish repository consistency, not semantic-oracle validity or novelty.

---

## 7. Phase 3 — conditional empirical pilot

Proceed only if Phase 2 passes.

Create a new child branch from the reviewed Phase 2 head. Do not implement Phase 3 directly on the Phase 2 audit branch.

### Task design

Use four reviewed real base tasks. For each, construct:

1. `clean` — fully correct;
2. `persistent` — one runnable, schema-valid semantic error remains through submission;
3. `recovered` — the same early error occurs but is explicitly repaired before submission and causes no irreversible side effect;
4. `benign_equivalent` — implementation differs but task semantics remain correct.

Total calibration slice: `4 × 4 = 16` cases.

These are construct-validation cases, not natural-agent-performance evidence.

### Required safeguards

- One semantic variable per controlled mutation.
- Persistent and recovered cases share the same mutation source.
- Benign controls are verified by an independent property oracle, not code similarity.
- Full snapshots remain outside Git; track only compact metrics, digests, manifests, and small synthetic/reviewed fixtures where lawful.
- Hidden mutation ledgers and gold labels are inaccessible to evaluated systems.
- Step boundaries require human-style justification and a segmentation-sensitivity note.

### Capability conditions

Evaluate at least:

- final task execution;
- latest-intent reconstruction;
- self-detection and abstention;
- violated-requirement localization;
- source-step localization;
- recovered-versus-persistent discrimination.

Repair remains optional until the preceding labels are stable.

---

## 8. Required baseline families

On the same cases, visibility, model budget, and hidden-gold boundary, compare:

1. native ProfiliTable final evaluator;
2. final-output-only property checker;
3. dialogue + code/ordinary trajectory judge without intermediate state;
4. UserIntentBench/evolving-intent-style intent tracker;
5. DataSpace-style process audit;
6. AgentRx-style constraint/evidence diagnosis;
7. FALAT-style dependency/counterfactual attribution where faithfully implementable;
8. DRIFT-style claim/evidence/dependency diagnosis;
9. DataTrace-style artifact/dependency/evidence-path baseline where public artifacts permit;
10. state-aware ablation only as a treatment, not an assumed winner.

For every transferred baseline, record:

- exact source version or fixed commit;
- whether official code exists;
- faithful input transformation;
- visible and hidden gold;
- output-label mapping;
- any specification-level reimplementation;
- unsupported assumptions;
- matched token/time/tool budget.

If a direct-transfer baseline reaches the annotation ceiling, stop the overlapping novelty claim.

---

## 9. Empirical reporting rules

For the 16-case pilot, report per-case counts and all disagreements. Do not claim statistical significance or population-level generalization.

Report:

- runnable and schema-valid count;
- native outcome result;
- clean/benign false rejection;
- persistent detection;
- recovered specificity;
- active-intent exactness;
- violated-clause exactness;
- source-step exact and `±1`;
- executable witness replay success;
- abstention and unresolved reasons;
- annotator raw agreement and adjudication;
- runtime, tokens, and cost when available.

Keep controlled mutations separate from natural failures.

---

## 10. Natural-failure gate

Do not claim real-agent relevance until natural failures are collected from multiple frozen systems or provided by authorised internal sources.

Natural failures must be stored and reported separately from controlled variants. Compare whether the planned failure families actually occur:

- stale or superseded requirement;
- wrong comparator/boundary;
- omitted exclusion;
- wrong aggregation grain;
- latest-record error;
- join/cardinality error;
- forbidden side effect;
- execution succeeds but self-report is overconfident.

If controlled labels do not transfer to natural failures, retain the artifact as a controlled diagnostic suite and drop representativeness claims.

---

## 11. GO / PIVOT / STOP

### GO A

Advance the Table-Agent capability benchmark only if at least one capability beyond final success has:

- stable independent gold;
- nontrivial headroom after strongest direct-transfer baseline;
- a decision consequence for acceptance, retry, repair, ranking, time, or cost;
- lawful and reproducible task provenance.

### PIVOT C

Promote state-grounded evaluation only if state creates unique replayable wins across multiple semantic families with acceptable clean/recovered/benign false rejection and matched input budget.

### PIVOT to intent reconstruction

If gold-contract diagnosis works but predicted-contract diagnosis fails, focus on evolving-intent reconstruction or contract induction.

### PIVOT to detection only

If violated requirements are stable but exact source steps are not, drop exact localization and build a violation-detection benchmark.

### STOP novelty

Stop the benchmark/method novelty framing if:

- an existing fixed benchmark matches the evaluated subject, inputs, gold, and output labels;
- transferred methods reach the annotation ceiling;
- intermediate state adds no decision-relevant information;
- labels are unstable;
- independent semantic oracles cannot be built;
- data provenance or licence blocks reproducible release;
- new labels do not change any operational decision.

### D later

Attempt harness/self-monitoring integration only after the evaluator is reliable and a local repair policy outperforms matched retry/full regeneration without increasing side effects.

---

## 12. Repository and PR discipline

Use one bounded branch per phase:

```text
research/phase2-autonomous-audit
research/phase3-capability-pilot
research/phase3-state-ablation
research/natural-failure-collection
research/harness-integration
```

For each branch:

1. keep a draft PR open;
2. update the PR body after each milestone;
3. use small commits with one purpose;
4. run tests before every push;
5. inspect `git status --short` and `git diff --check`;
6. keep full raw/generated artifacts outside Git;
7. never merge to `master` automatically;
8. target the current research decision branch or the reviewed parent phase branch.

Commit examples:

```text
audit: add reproducible task package inventory
audit: draft evaluator clause coverage
test: validate package audit outputs
docs: record phase 2 pass and residual risks
feat: instrument reviewed workflow checkpoints
eval: add reference-hidden dialogue-code baseline
```

Avoid catch-all commits.

---

## 13. Progress log contract

Maintain `research/PHASE2_PROGRESS.md` as a concise current-state ledger. Each update must contain:

```text
Date / commit
Question answered
Evidence produced
Files changed
Tests run
Decision impact
New blockers
Next autonomous action
```

Do not duplicate long historical context. Link to the canonical handoff and decision memo.

---

## 14. Human-science boundary

Codex may propose draft gold, interpretations, task decomposition, mutation classification, and novelty analysis. It may not silently finalize them.

The following require explicit adjudication in the artifact, even when Codex performs the first pass:

- faithful interpretation of a user requirement;
- clause-level evaluator coverage;
- semantic step boundaries;
- one-variable mutation validity;
- source versus propagation;
- recovered versus persistent;
- data licence and redistribution;
- novelty and paper claims;
- final GO/PIVOT/STOP.

When no human adjudicator is available, mark the item `PENDING_ADJUDICATION` or `DATA_INSUFFICIENT`; continue all independent work.

---

## 15. Completion definition

This autonomous goal is complete when one of the following occurs:

### Outcome 1 — Phase 2 pass

A reviewed Phase 2 PR contains reproducible task inventory, evaluator coverage, provenance/licence analysis, independent-oracle feasibility, and four defensible real task candidates. It also contains an explicit Phase 3 branch plan.

### Outcome 2 — Evidence-based pivot

The audit demonstrates ProfiliTable cannot support four defensible tasks, but a narrower construct or different carrier is justified with evidence and a new bounded branch/plan.

### Outcome 3 — Evidence-based stop

The audit demonstrates the research framing is duplicated, unsupported, unreleasable, or lacks independent semantic oracles. The PR records the stop rationale and recommends the next research problem.

Do not stop because the work is tedious. Stop only on a documented scientific, legal, or resource boundary.
