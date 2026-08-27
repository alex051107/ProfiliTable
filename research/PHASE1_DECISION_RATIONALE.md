# Phase 1 Decision Rationale

**Documentation type:** Explanation — why the project selected formulation A and retained formulation C as its fallback
**Date:** 2026-08-26
**Status:** evidence-based rationale; no novelty or experimental claim
**Branch:** `research/benchmark-first-plan-v0.2`
**Upstream runtime baseline:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`

## Purpose

This document records the reconstructable decision path behind Phase 1: the starting objective, evidence inspected, alternatives considered, decision rules, conclusions, and conditions that would overturn them. It complements the concise [`RESEARCH_DECISION_MEMO.md`](RESEARCH_DECISION_MEMO.md) and the operational [`PHASE1_HANDOFF_REVIEW.md`](PHASE1_HANDOFF_REVIEW.md).

It does not present private chain-of-thought or treat intermediate deliberation as evidence. Every material conclusion should be traceable to a source, a repository observation, or an explicitly labelled design inference.

## Outcome

Phase 1 selected:

- **Primary:** A — Table-Agent Capability Benchmark;
- **Fallback:** C — Method-First State-Grounded Evaluator;
- **Not selected as primary:** B — Process-Diagnostic Benchmark;
- **Deferred:** D — Harness / Self-Monitoring Integration.

The decision is **GO to a bounded Phase 2 audit**, not GO to benchmark implementation. Phase 2 must establish task provenance, evaluator coverage, independent semantic-oracle feasibility, and checkpoint feasibility before any controlled variants or model runs are created.

## 1. Starting objective

The original research objective was broader than state evidence:

> Can a table agent execute evolving user requirements correctly, recognise when it has made a semantic error, localise where that error began, recover, and eventually repair its workflow?

That objective contains five separable capabilities:

1. final execution correctness;
2. latest-intent tracking after additions, revisions, or retractions;
3. calibrated self-detection;
4. violated-clause and source-step localisation;
5. recovery or repair without new failures.

The research subject therefore began as the **Table Agent**, not an external state checker.

## 2. Why the project narrowed too early

The initial literature search found strong overlap for several broad framings:

- table-agent execution and final evaluation in [ProfiliTable](https://arxiv.org/abs/2605.12376v2) and spreadsheet benchmarks;
- evolving interaction and intent changes in [CITBench](https://arxiv.org/abs/2608.00018v1) and [Evolving User Intent](https://arxiv.org/abs/2607.20734v1);
- first, critical, or persistent failure diagnosis in [DataSpace](https://arxiv.org/abs/2608.03451v1), [AgentRx](https://arxiv.org/abs/2602.02475v1), [FALAT](https://arxiv.org/abs/2606.00765v1), [DRIFT](https://arxiv.org/abs/2606.02060v2), and [TrajDebug](https://arxiv.org/abs/2608.06346v1);
- executable lineage and evidence paths in [mlinspect](https://doi.org/10.1007/s00778-021-00726-w), [BigDebug](https://doi.org/10.1145/2884781.2884813), and the code-first [DataTrace artifact](https://github.com/HKUSTDial/datatrace/commit/48a89e59b4aeef5a01d5ed68c1a1b4d4dc84a411);
- executable contracts and local or counterfactual repair in [Lean4Agent](https://arxiv.org/abs/2606.06523v2), [ContractSkill](https://arxiv.org/abs/2603.20340v3), and [CausalFlow](https://arxiv.org/abs/2605.25338v1).

Those overlaps made “first semantic verifier”, “first evolving table benchmark”, and “first-error diagnosis” unsafe. The work then narrowed to the question of whether intermediate table state adds evidence unavailable in dialogue or code.

That narrowing was useful as a hypothesis but harmful as a default project identity. It changed the evaluated subject from the Table Agent to an external diagnostic model before proving that state information had incremental value.

## 3. Decision framework

Four research shapes were compared using the same criteria.

| Criterion | Decision question |
|---|---|
| Objective alignment | Does the formulation still test the original Table Agent capability ladder? |
| Coverage | Does an existing work already match the evaluated subject, input visibility, gold, and output labels? |
| Incremental evidence | Does the new information solve cases that a strong transferred baseline cannot? |
| Consequence | Does the new label or method change acceptance, retry, repair, ranking, time, or cost? |
| Falsifiability | Is there a small experiment that can disconfirm the formulation? |
| Six-week feasibility | Can task audit, annotation, baselines, and a meaningful gate be completed without premature platform work? |
| Evidence and release risk | Can the task, gold, provenance, licensing, and evaluator coverage be defended? |

The complete comparison appears in [`ALTERNATIVE_FORMULATIONS.md`](ALTERNATIVE_FORMULATIONS.md).

## 4. Investigation sequence

### 4.1 Reconstruct the repository and claim boundary

The branch was first checked against the frozen upstream runtime. The branch contained research plans and protocols rather than a native ProfiliTable implementation of versioned intent, source-error labels, or state witnesses. The paper-linked official runtime was inspected at [`PKU-DAIR/ProfiliTable@f495062`](https://github.com/PKU-DAIR/ProfiliTable/commit/f495062699e1364978f5032bfbd7b6dac22144e9).

This established an important boundary:

- the current branch is a research-design branch;
- the original ProfiliTable evaluator is an outcome control;
- proposed process labels and witnesses remain unimplemented in this repository;
- a separate controlled prototype is not evidence of ProfiliTable-native capability or real-agent performance.

### 4.2 Search by dimensions, not project names

The literature audit was divided into six axes:

1. table and spreadsheet capability benchmarks;
2. evolving or latent intent;
3. failure localisation;
4. data/database provenance;
5. contract, verification, and repair;
6. benchmark methodology.

Each work was decomposed by evaluated subject, domain, interaction, agent-visible information, evaluator-visible information, gold, output labels, error definition, evidence, repair, public assets, blocked claims, and residual gap. The result is the 37-row [`NOVELTY_MATRIX.tsv`](NOVELTY_MATRIX.tsv).

This decomposition prevented a superficial conclusion such as “another paper also mentions first error”. Two methods can share that phrase while differing in oracle visibility, error persistence, state access, or repair semantics.

### 4.3 Search for disconfirmation

The audit prioritised sources that could invalidate each formulation:

- A was challenged by ProfiliTable, CITBench, SpreadsheetBench 2, SheetMind, and evolving-intent benchmarks;
- B was challenged by DataSpace, AgentRx, FALAT, DRIFT, TrajDebug, and DataTrace;
- C was challenged by SheetMind, AJ-Bench, HINTBench, mlinspect, and DataTrace;
- D was challenged by SheetMind, AgentSpec, ContractSkill, and CausalFlow.

The audit found that most individual ingredients were already covered. The only surviving space was a conjunction:

```text
evolving/versioned table intent
+ executed table checkpoints
+ independently labelled source, propagation, recovery, and consequence
+ executable row/cell/statistic witness
+ evaluated local recovery or repair
```

No audited source was found to cover the full conjunction. That absence is a **candidate gap**, not novelty.

### 4.4 Convert related work into executable baselines

The project then asked whether the strongest neighbouring approaches could be transferred to the same ProfiliTable cases. [`DIRECT_TRANSFER_BASELINE_PLAN.md`](DIRECT_TRANSFER_BASELINE_PLAN.md) specifies:

- a shared case representation and lifecycle labels;
- reference-hidden and oracle visibility conditions V0–V7;
- DataSpace-style final and process controls;
- AgentRx-style guarded constraints;
- a specification-level FALAT adaptation where official code is unavailable;
- DRIFT-style trace and claim ledgers;
- DataTrace-style artifact graphs and executable repair checks.

This step changed the research question from “does our idea sound different?” to “what remains after strong direct transfer under the same visibility contract?”

### 4.5 Apply benchmark methodology before scaling

The design added explicit requirements for:

- construct-to-observation-to-label-to-metric mapping;
- evaluator coverage rather than one aggregate score;
- independent annotation and adjudication;
- separate controlled and natural-failure tracks;
- grouped leakage controls;
- difficulty and saturation checks;
- case-level provenance and redistribution decisions.

These requirements mean that a clean schema or a difficult-looking task is insufficient. The score interpretation, gold stability, evaluator coverage, and intended decision must all be defensible.

## 5. Why A became primary

A best preserves the original subject and can absorb the other work as measurement layers.

### 5.1 It evaluates the Table Agent

The main track asks whether the agent can execute, track intent, detect, localise, and recover. The agent sees ordinary dialogue, source tables, its own code/actions, and normal runtime feedback. Benchmark-injected checkpoints and gold labels remain hidden.

### 5.2 It retains a no-state direction

Intermediate state can be hidden scoring evidence without becoming agent input. This avoids assuming that state access is necessary or deployable.

### 5.3 It turns B into a baseline rather than a competing identity

Process diagnosis remains valuable for scoring detection, localisation, and recovery. DataSpace-, AgentRx-, FALAT-, DRIFT-, and DataTrace-style methods become direct-transfer controls for A.

### 5.4 It is falsifiable

A stops as a benchmark contribution if:

- existing benchmarks match its subject, inputs, gold, and labels;
- violated-clause or source labels are unstable;
- transferred methods reach the annotation ceiling;
- the new capabilities do not change acceptance, retry, repair, ranking, time, or cost;
- real ProfiliTable tasks lack independent semantic oracles.

### 5.5 It fits a bounded six-week path

The first week is an upstream task/evaluator/provenance audit. Only qualified tasks proceed to construct definition, controlled calibration, direct transfers, blind annotation, and a GO/PIVOT/STOP review. A broad benchmark release is not a six-week promise.

## 6. Why C remains the fallback

C asks a narrower method question:

> Under the same reference-hidden task and trajectory, does executed table state or lineage improve diagnosis or repair beyond dialogue, code, and ordinary observations?

C survives only when state produces a **state-unique win**:

1. the strongest no-state baseline is wrong or unresolved;
2. the state condition identifies the correct clause/source or creates a hidden-check-passing repair;
3. the cited witness replays;
4. the evidence was not already present in the ordinary trace;
5. no gold, reference output, evaluator internals, or witness ledger leaked into prediction.

If gold contract access helps but predicted contract access fails, the correct pivot is intent or contract induction—not a state method. If state adds only longer explanations, C stops.

## 7. Why B and D were not selected

### B — not selected as primary

B has the cleanest labels but the highest direct overlap. Generic persistent error, critical step, propagation, recovery, evidence paths, and repair tests are already represented in neighbouring work. A table-domain relabelling would be weak unless the full evolving-intent and executable-witness conjunction changes outcomes.

B remains necessary as A's diagnosis layer and baseline suite.

### D — deferred

D has strong systems value but depends on a reliable evaluator, calibrated abstention, an isolated patch mechanism, and matched retry/regeneration controls. Building the harness first would optimise an unvalidated signal.

D becomes eligible only if A or C yields a stable decision signal and a local patch beats whole-program regeneration at matched cost.

## 8. Evidence-status ledger

| Status | What Phase 1 supports |
|---|---|
| Observed | The branch is documentation-only relative to the frozen runtime; the four Phase 1 artifacts exist; the official ProfiliTable loop uses task-specific final evaluation; neighbouring work covers the listed components. |
| Inference | The conjunction may remain under-covered; A better matches the original objective; C is the cleanest falsifiable fallback. |
| Design proposal | Shared lifecycle labels, visibility views V0–V7, a 4×4 controlled gate, state-unique-win thresholds, and six-week execution plans. |
| Data insufficient | Real task inventory, evaluator coverage, task licensing, checkpoint fidelity, natural-failure prevalence, annotation reliability, baseline performance, state benefit, and repair benefit. |

## 9. What Phase 1 did not do

Phase 1 did not:

- change ProfiliTable runtime code;
- download or redistribute benchmark data;
- generate controlled variants;
- add or expand a runtime schema;
- run LLM baselines;
- validate natural failures;
- establish state benefit;
- establish annotation reliability;
- establish novelty or publication potential;
- create a pull request or merge to `master`.

## 10. Next decision point

Phase 2 must answer whether ProfiliTable is a viable carrier for A:

1. Are four real tasks available with traceable provenance and suitable rights?
2. Does each task have an independent semantic-oracle plan beyond assuming `eval.py` is complete?
3. Can transformation/checkpoint boundaries be exposed without changing task semantics?
4. Can the selected tasks cover filter/revision, aggregation grain, dedup/latest record, and preservation/side effects?

If these conditions pass, design the 16-instance construct gate. If they fail, reduce the scope or stop the ProfiliTable benchmark framing before implementing mutants.

## 11. Traceability map

| Need | Canonical artifact |
|---|---|
| source-by-source claim boundary | [`NOVELTY_MATRIX.tsv`](NOVELTY_MATRIX.tsv) |
| A–D comparison and six-week plans | [`ALTERNATIVE_FORMULATIONS.md`](ALTERNATIVE_FORMULATIONS.md) |
| baseline inputs, oracle boundaries, and metrics | [`DIRECT_TRANSFER_BASELINE_PLAN.md`](DIRECT_TRANSFER_BASELINE_PLAN.md) |
| primary/fallback decision and GO/PIVOT/STOP | [`RESEARCH_DECISION_MEMO.md`](RESEARCH_DECISION_MEMO.md) |
| current handoff, review evidence, and next executor | [`PHASE1_HANDOFF_REVIEW.md`](PHASE1_HANDOFF_REVIEW.md) |
| pre-Phase-1 history and meeting context | [`../PROJECT_HANDOFF_2026-08-26.md`](../PROJECT_HANDOFF_2026-08-26.md) |
