# Research Decision Memo

**Decision:** GO to a bounded Phase 2 audit under formulation A; do not begin benchmark implementation
**Primary formulation:** A — table-agent capability benchmark
**Fallback:** C — reference-hidden state-information-gain evaluator
**Not selected:** B — external process-diagnostic benchmark; D — self-monitoring harness
**Date:** 2026-08-26
**Evidence status:** literature/code audit and design inference only; no experiment or novelty claim

## Executive decision

Return the project to its original subject: the **Table Agent**. The primary study should measure execution, latest-intent tracking, calibrated self-detection, localization, recovery, and eventually repair. Intermediate table state remains hidden scoring evidence in the main capability track. It becomes the fallback method question only if a controlled, reference-hidden ablation shows that checkpoints or lineage solve cases that strong dialogue/code/trajectory baselines cannot and that this improvement changes acceptance or repair.

Proceed only to Phase 2: audit real ProfiliTable tasks, evaluator coverage, provenance/license, and checkpoint feasibility. The planned `4 tasks × 4 variants` experiment is the next empirical gate, but it is not authorized or executed by this memo.

## Phase 0 context reconstruction

### Original objective

Benchmark and improve whether a table agent can:

1. execute the user's current requirements correctly;
2. track additions, revisions, and retractions;
3. recognize its own semantic error;
4. identify the violated requirement and where the error began;
5. recover or repair before submission.

This objective concerns the agent's capability ladder, not a state checker in isolation.

### Current candidate gap

The only candidate space that survived the six-axis audit is the conjunction of:

```text
evolving/versioned table intent
+ executed table checkpoints
+ independently labeled source, propagation, recovery, and consequence
+ executable row/cell/statistic witness
+ evaluated localized recovery or repair
```

No audited source in `NOVELTY_MATRIX.tsv` was found to cover the whole conjunction. Each ingredient, and several large subsets, already have strong precedents. The conjunction is therefore a **hypothesis to falsify**, not a novelty statement.

### Known overlapping work

| Component | Strongest observed overlap | Decision consequence |
|---|---|---|
| table execution and final evaluation | [ProfiliTable v2](https://arxiv.org/abs/2605.12376v2), [SpreadsheetBench v2](https://arxiv.org/abs/2406.14991v2) | final correctness is a control, not a new construct |
| evolving table/user intent | [CITBench v1](https://arxiv.org/abs/2608.00018v1), [Evolving User Intent v1](https://arxiv.org/abs/2607.20734v1), [InterruptBench v1](https://arxiv.org/abs/2604.00892v1) | additions/revisions/retractions alone cannot support novelty |
| spreadsheet debugging and state reflection | [SpreadsheetBench 2 v1](https://arxiv.org/abs/2606.29955v1), [SheetMind v2](https://arxiv.org/abs/2506.12339v2) | debugging or state-grounded reflection alone is already covered |
| persistent/critical/source error | [DataSpace v1](https://arxiv.org/abs/2608.03451v1), [AgentRx v1](https://arxiv.org/abs/2602.02475v1), [FALAT v1](https://arxiv.org/abs/2606.00765v1), [TrajDebug v1](https://arxiv.org/abs/2608.06346v1) | generic first/root-cause framing is blocked |
| harmful spans and claim dependencies | [DRIFT v2](https://arxiv.org/abs/2606.02060v2) | text/trace-only diagnosis is a required strong baseline |
| executable provenance and repair | [mlinspect](https://doi.org/10.1007/s00778-021-00726-w), [BigDebug](https://doi.org/10.1145/2884781.2884813), [BigSift](https://doi.org/10.1145/3127479.3131624), [DataTrace code](https://github.com/HKUSTDial/datatrace/commit/48a89e59b4aeef5a01d5ed68c1a1b4d4dc84a411) | row/lineage/replay/root-cause-and-fix cannot be claimed as first |
| contracts, state verification, evidence acquisition, and local repair | [Lean4Agent v2](https://arxiv.org/abs/2606.06523v2), [AgentSpec v3](https://arxiv.org/abs/2503.18666v3), [AJ-Bench](https://aclanthology.org/2026.findings-acl.1269/), [ContractSkill v3](https://arxiv.org/abs/2603.20340v3), [CausalFlow v1](https://arxiv.org/abs/2605.25338v1) | contract/verifier/state-evidence/minimal-repair claims require narrower evidence |

### What is already implemented or observed

**Repository observation:** on `research/benchmark-first-plan-v0.2`, the changes relative to the frozen upstream baseline are research plans/protocols and `.gitignore` hardening. No ProfiliTable runtime file has been changed on this branch.

**Code observation:** the frozen baseline is [`Eularioal/ProfiliTable@f023ec4`](https://github.com/Eularioal/ProfiliTable/commit/f023ec4b754555000a659b93fd514645c55e3cec). The paper now links [`PKU-DAIR/ProfiliTable`](https://github.com/PKU-DAIR/ProfiliTable), inspected at fixed commit [`f495062`](https://github.com/PKU-DAIR/ProfiliTable/commit/f495062699e1364978f5032bfbd7b6dac22144e9). A local recursive comparison found the `main/` and `table_agent/` runtime trees equal between those two checked revisions. This does not establish data-package identity or evaluator coverage.

**Paper/code observation:** ProfiliTable executes a candidate program, runs a task-specific `eval.py` against the processed output and ground truth, returns a scalar result to the agent loop, and lets a summarizer inspect the processed table ([paper v2](https://arxiv.org/abs/2605.12376v2); [fixed official code](https://github.com/PKU-DAIR/ProfiliTable/commit/f495062699e1364978f5032bfbd7b6dac22144e9)). The audited runtime does not provide a checked-in gold contract for versioned intent, first/source/propagation/recovery labels, or executable witness scoring.

### What remains unverified

- exact ProfiliTable task inventory and package identity at the frozen revision;
- source-data and derived-artifact licenses/redistribution terms;
- clause-level coverage and blind spots of every selected task's `eval.py`;
- feasibility and semantic fidelity of transformation boundaries and table checkpoints;
- prevalence and taxonomy of natural Table Agent failures;
- label stability for first local error, first intent violation, source, persistence, propagation, recovery, and final consequence;
- actual performance of DataSpace, AgentRx, FALAT, DRIFT, and DataTrace transfers;
- incremental value, cost, and false-rejection risk of state or lineage;
- whether localized repair beats matched whole-program regeneration.

These items prevent implementation claims, benchmark claims, and novelty claims.

## Phase 1 formulation decision

### Primary: A — table-agent capability benchmark

**Scientific question:** can a Table Agent execute the latest intent and detect, localize, and recover from its own semantic failures under hidden reference outputs?

**Why this is primary:** it matches the original objective, retains a no-agent-visible-state condition, and makes the process diagnosis and state evaluator serve a measurable agent capability rather than become the project identity. The benchmark can separate execution, active-intent tracking, self-detection, localization, recovery, and repair instead of presenting one aggregate score.

**Research burden:** the contribution survives only if the constructs are reliable, direct-transfer baselines leave headroom, and the new labels alter an operational decision.

### Fallback: C — state-information-gain evaluator

**Scientific question:** with gold/reference outputs withheld, does executed table state or lineage improve diagnosis or repair beyond dialogue, code, and ordinary trace?

**Why this is fallback:** it is sharply falsifiable through V2/V3 versus V5/V6 comparisons in `DIRECT_TRANSFER_BASELINE_PLAN.md`. It also prevents the project from assuming state value. A positive result must contain a replayable cell/row/statistic witness unavailable in the no-state input and must change exact localization, repair, false acceptance, or cost.

### Why B is not selected

B's generic core is already densely occupied:

- DataSpace: earliest observable, uncorrected, outcome-determining divergence;
- AgentRx: first unrecovered failure under generated constraints;
- FALAT: typed dependencies and counterfactual decisive steps;
- DRIFT: earliest harmful span and claim-support ledger;
- TrajDebug: resolved/active lifecycle and terminal footprint;
- DataTrace: artifact graph, reference evidence path, root-cause scoring, and executable fix tests at the code-artifact level.

A table-only relabeling would not justify a standalone direction. B remains necessary as the evaluation layer and source of direct-transfer baselines.

### Why D is not selected

D depends on a reliable evaluator, calibrated accept/retry behavior, a safe localized patch interface, and end-to-end comparisons against simple regeneration. [SheetMind](https://arxiv.org/abs/2506.12339v2), [AgentSpec](https://arxiv.org/abs/2503.18666v3), [ContractSkill](https://arxiv.org/abs/2603.20340v3), and [CausalFlow](https://arxiv.org/abs/2605.25338v1) already make a generic reflection/enforcement/repair story insufficient. Building the harness now would recreate the local-minimum problem.

## Allowed claims

The following statements are allowed at the end of Phase 1:

- The project **plans to test** the Table Agent capability ladder under evolving requirements and hidden reference outputs.
- The audited literature/code covers individual components including evolving intent, first/persistent failure, state-aware judging, executable lineage, and localized/counterfactual repair.
- The candidate residual is the conjunction of evolving table intent, executed state, lifecycle labels, executable witness, and evaluated repair.
- A direct-transfer and ablation plan has been specified for DataSpace, AgentRx, FALAT, DRIFT, and DataTrace.
- The current ProfiliTable branch contains research design changes and no runtime implementation change.
- State is a treatment to test, not the assumed core contribution.

All future-facing statements must use `plan`, `candidate`, `hypothesis`, or `design proposal` until empirical evidence exists.

## Forbidden claims

Do not claim:

- first evolving-intent table or spreadsheet benchmark;
- first spreadsheet debugging, self-reflection, or state-aware judging benchmark;
- first state-grounded agent diagnosis;
- first persistent, first-unrecoverable, decisive-step, or root-cause process audit;
- first recovered-versus-persistent error lifecycle;
- first dependency-guided source-versus-propagation diagnosis;
- first row/cell lineage, minimal row witness, provenance, or replay debugger;
- first evidence-grounded database/table root-cause-and-repair benchmark;
- first executable contract, workflow verifier, runtime state-evidence enforcement, or localized/counterfactual repair;
- benchmark coverage, annotation reliability, natural-failure validity, repair benefit, state benefit, or system improvement before those results exist;
- novelty from the absence of a shared name or from no single audited source matching the full conjunction.

## Next gate

### Gate 1 — Phase 2 audit; GO now

Run only read-only or locally summarized audits:

1. record the exact task package, source commit, retrieval date, license/terms, and local redistribution decision;
2. enumerate `task_meta.json`, raw input shape, ground truth, and `eval.py` for the frozen baseline;
3. build a clause-to-check coverage table for candidate tasks;
4. test whether independent property oracles and checkpoint boundaries are feasible without changing task semantics;
5. select four real tasks only if they cover filter/revision, aggregation grain, dedup/latest record, and preservation/side effects.

**Pass condition:** four tasks have traceable provenance, usable rights for the planned artifact, independent semantic-oracle plans, and feasible checkpoint boundaries.
**Pivot:** fewer than four tasks qualify but a smaller construct audit remains possible.
**Stop:** task data or evaluation cannot support independent semantic adjudication or lawful reproducible release.

### Gate 2 — Phase 3/Stage 0 design; planned, not executed

Construct four variants per qualified task:

```text
clean
persistent semantic error
recovered version of the same early error
benign-equivalent implementation
```

Run the fixed reference-hidden views and direct transfers in `DIRECT_TRANSFER_BASELINE_PLAN.md`. The diagnostic slice is `4 × 4 = 16` instances. A capability slice should separately ask the agent to execute and self-report under ordinary visibility; controlled variants remain a diagnostic construct test rather than employment of synthetic failures as natural agent behavior.

**C advancement proposal:** at least three state-unique wins across at least three semantic families, replay success for every claimed unique witness, and no more than one new false rejection among clean/recovered/benign controls. These are predeclared design thresholds, not statistical effect claims.

**A advancement condition:** at least one capability beyond final success has stable gold, nontrivial headroom after direct transfer, and a demonstrated decision consequence.

## GO / PIVOT / STOP table

| Evidence after the future gate | Decision |
|---|---|
| A has stable labels and decision-relevant headroom; state adds little | **GO A:** scale capability benchmark carefully; keep state hidden for scoring |
| State adds unique replayable reference-hidden wins | **PIVOT C:** develop state/cost-aware evaluator; retain A as evaluation setting |
| Gold active contract works but predicted contract fails | **PIVOT:** intent reconstruction/contract induction, not state diagnosis |
| Violated clause is stable but source step is not | **PIVOT:** detection benchmark; drop exact localization claim |
| Synthetic lifecycle works but natural failures do not match | **PIVOT:** controlled diagnostic suite; do not claim natural-failure representativeness |
| Transferred no-state methods reach annotation ceiling | **STOP B/C novelty:** retain domain integration only |
| New labels do not change accept/retry/repair/ranking/time/cost | **STOP benchmark contribution:** explanations alone are insufficient |
| Oracles, provenance, licensing, or annotation are unstable | **STOP scaling:** repair the evidence foundation first |
| Reliable evaluator exists and local patch beats matched regeneration | **GO D later:** test integrated self-monitoring as a separate milestone |

## Conditions that overturn this memo

The primary/fallback choice must be reopened if:

1. a fixed, official work is found with the same evaluated subject, main input visibility, gold, output labels, and evolving-table lifecycle/witness/repair conjunction;
2. Phase 2 shows that ProfiliTable tasks cannot expose independent semantic oracles or stable checkpoints;
3. direct transfers solve the planned labels at the human ceiling;
4. capability annotations are unstable even after unit/boundary rules and adjudication are frozen;
5. state access provides no replayable unique information or produces unacceptable false rejection;
6. an integrated agent-visible feedback track is substantially easier to validate than the external evaluator assumption—this would require new evidence, not architectural preference.

## Final status

**GO means:** perform the bounded Phase 2 audit for A and preserve C as the falsifiable fallback.
**GO does not mean:** implement the benchmark, generate mutants, expand the schema, claim novelty, or build the self-monitoring harness.
