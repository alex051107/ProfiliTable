# Phase 1 Handoff Review

**Documentation type:** Reference — current state, reviewed artifacts, acceptance evidence, unresolved boundaries, and next executor entry point
**Date:** 2026-08-26
**Repository:** `https://github.com/alex051107/ProfiliTable`
**Branch:** `research/benchmark-first-plan-v0.2`
**Remote base integrated before this batch:** `309b12a`
**Runtime baseline:** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`
**Upload state at authoring:** pending final review and non-force push

## 1. Current authoritative status

The Phase 0/1 content is complete in the working tree. It becomes the canonical remote-branch package only after final review, commit, non-force push, and GitHub readback.

| Decision | Current status |
|---|---|
| Primary formulation | **A — Table-Agent Capability Benchmark** |
| Fallback formulation | **C — Method-First State-Grounded Evaluator** |
| B — Process-Diagnostic Benchmark | not selected as primary; retained as the scoring layer and direct-transfer baseline suite |
| D — Harness / Self-Monitoring Integration | deferred until an evaluator produces stable, decision-relevant signal |
| Next authorised work | bounded Phase 2 ProfiliTable task/evaluator/provenance audit |
| Runtime implementation | not started |
| Controlled variants or mutants | not created |
| Model experiments | not run |
| Novelty | not established |

The word **GO** in this package means GO to Phase 2 audit only. It does not authorise benchmark implementation, schema expansion, mutation generation, model runs, or a paper claim.

## 2. Canonical reading order

A new researcher or Codex task should read:

1. this file — current reviewed state and next gate;
2. [`RESEARCH_DECISION_MEMO.md`](RESEARCH_DECISION_MEMO.md) — decision and kill rules;
3. [`PHASE1_DECISION_RATIONALE.md`](PHASE1_DECISION_RATIONALE.md) — evidence-based reasoning and alternatives;
4. [`ALTERNATIVE_FORMULATIONS.md`](ALTERNATIVE_FORMULATIONS.md) — full A–D comparison;
5. [`DIRECT_TRANSFER_BASELINE_PLAN.md`](DIRECT_TRANSFER_BASELINE_PLAN.md) — reference-hidden transfer protocol;
6. [`NOVELTY_MATRIX.tsv`](NOVELTY_MATRIX.tsv) — source-by-source claim boundary;
7. [`../CODEX_RESEARCH_START_HERE.md`](../CODEX_RESEARCH_START_HERE.md) — execution charter and phase order;
8. [`../PROJECT_HANDOFF_2026-08-26.md`](../PROJECT_HANDOFF_2026-08-26.md) — project history and pre-Phase-1 snapshot;
9. [`PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`](PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md) — Phase 2 audit specification;
10. [`CODEX_EXECUTION_AND_REPO_HYGIENE.md`](CODEX_EXECUTION_AND_REPO_HYGIENE.md) — repository and data boundaries.

When an older section says the formulation remains unselected or the four deliverables are unwritten, this file and `RESEARCH_DECISION_MEMO.md` supersede that status.

## 3. Phase 1 artifact inventory

| Artifact | Purpose | Completion boundary |
|---|---|---|
| [`NOVELTY_MATRIX.tsv`](NOVELTY_MATRIX.tsv) | 37-work, 18-field comparison across six search axes, including a batch retrieval date | literature/code audit; not a proof of novelty or completeness |
| [`ALTERNATIVE_FORMULATIONS.md`](ALTERNATIVE_FORMULATIONS.md) | A–D scientific question, overlap, resources, baseline, kill test, six-week plan, and fallback | route comparison; no experiment |
| [`DIRECT_TRANSFER_BASELINE_PLAN.md`](DIRECT_TRANSFER_BASELINE_PLAN.md) | common cases, visibility V0–V7, expected-output boundary, five transfers, metrics, and falsification rules | protocol design; no implementation |
| [`RESEARCH_DECISION_MEMO.md`](RESEARCH_DECISION_MEMO.md) | context reconstruction, primary/fallback selection, allowed/forbidden claims, next gate | decision record; GO only to Phase 2 audit |
| [`PHASE1_DECISION_RATIONALE.md`](PHASE1_DECISION_RATIONALE.md) | reconstructable evidence and decision path | explanation; not private chain-of-thought or empirical evidence |
| [`../PROJECT_HANDOFF_2026-08-26.md`](../PROJECT_HANDOFF_2026-08-26.md) | project history from meeting context to the pre-Phase-1 plan | historical snapshot; current status is superseded where noted |
| [`../CODEX_RESEARCH_START_HERE.md`](../CODEX_RESEARCH_START_HERE.md) | discoverable current entry point | updated to point to this package and Phase 2 |

## 4. Claim boundary

### Allowed now

- The project plans to test the Table Agent capability ladder under changing requirements and hidden reference outputs.
- Adjacent work covers individual ingredients including evolving intent, persistent/critical failure, state-aware judging, executable lineage, and local/counterfactual repair.
- The residual combination is a candidate hypothesis that requires direct transfer and empirical falsification.
- A is the selected primary route and C is the selected fallback.
- The branch remains documentation-only relative to the frozen ProfiliTable runtime.

### Forbidden now

- first evolving-intent table benchmark;
- first spreadsheet debugging, state-aware judge, or state-grounded self-reflection;
- first persistent, first-unrecoverable, decisive-step, or root-cause process audit;
- first row/cell lineage, witness, replay, or data-pipeline root-cause-and-repair benchmark;
- first executable contract, semantic verifier, runtime evidence enforcement, or local repair;
- state improves diagnosis or repair;
- the 16-case design represents natural agent performance;
- task data can be redistributed;
- the project has established novelty, ownership, authorship, venue, or publication outcome.

## 5. Review history and resolved findings

The original four-artifact batch received one combined independent research review. Its accepted findings were resolved as follows:

| Finding | Resolution |
|---|---|
| Eight novelty-matrix rows had 16 rather than 17 substantive fields | inserted the missing evidence/overlap field, then added a uniform `retrieved_on` field; all 37 data rows now parse to 18 fields |
| B and D lacked the same resource and six-week-plan detail as A and C | added minimum resources, bounded six-week plans, direct-transfer controls, and early-stop rules |
| DataTrace conditions conflated V4 and V6 notation | rewrote them as explicit composites: V6 plus gold contract versus V6 plus predicted contract |
| Datasheets source was not version-pinned | pinned the arXiv record to `1803.09010v8` |

No accepted finding changed the A-primary/C-fallback decision.

## 6. Acceptance criteria for this handoff batch

| Criterion | Evidence expected before push | Status |
|---|---|---|
| Phase 1 files are structurally readable | TSV field-count check; required headings and baseline names present | passed |
| Current decision is consistent | A primary, C fallback, B not primary, D deferred in the entry point, memo, rationale, and review | passed after replacing the stale Start Here task |
| Oracle visibility is explicit | reference output, evaluator internals, gold contract, state, and lineage separated in V0–V7 | passed |
| Historical handoff is not mistaken for current status | snapshot banner and section-level updates link to this review and the decision memo | passed |
| New executor can find the package | README, start page, and this file provide a canonical reading order | passed |
| No runtime or data scope expansion | Git diff contains documentation only; no data, mutants, schema, runs, or runtime edits | passed |
| Source/claim boundaries remain conservative | `PAPER CLAIM`, `CODE OBSERVATION`, inference, and `DATA_INSUFFICIENT` remain separated | passed by combined review |
| GitHub delivery is non-destructive | remote base fetched and fast-forwarded; upload uses a normal non-force push | pending push/readback |
| Source identity is traceable | an unambiguous `canonical_work_identifier`, versioned official URL/fixed commit or `DATA_INSUFFICIENT`, and batch retrieval date are recorded; exact titles are used where needed to prevent conflation | passed after field clarification |

## 7. Final combined review record

One independent combined review returned `FIX` with two Important findings and no Critical findings. Both findings were accepted and corrected. The `PASS` below is the implementing agent's post-fix delivery disposition based on targeted self-verification; a second independent review was not run.

```json
{
  "mode": "task",
  "target": "Phase 0/1 research decision package, handoff review, and decision rationale",
  "review": "performed",
  "reviewReason": "final delivery to the public GitHub research branch",
  "verdict": "PASS",
  "findings": [
    {
      "severity": "Important",
      "issue": "The bottom of CODEX_RESEARCH_START_HERE.md still assigned the completed Phase 1 work.",
      "action": "Replaced it with the bounded Phase 2 public-source audit and the mentor-gated internal/pilot boundary.",
      "status": "resolved"
    },
    {
      "severity": "Important",
      "issue": "The handoff acceptance row implied that every matrix work label was a full official title.",
      "action": "Renamed the field to canonical_work_identifier and defined traceability through an unambiguous identifier, versioned official URL/fixed commit or DATA_INSUFFICIENT, and retrieved_on date.",
      "status": "resolved"
    }
  ],
  "evidence": [
    "one read-only combined review of the nine-file documentation diff",
    "targeted post-fix checks for the current immediate task and matrix identity fields",
    "documentation-only Git diff and status review",
    "no runtime tests, builds, E2E checks, or hashes were run"
  ],
  "remainingRisks": [
    "ProfiliTable task inventory and evaluator coverage are not audited",
    "data licensing and redistribution are not resolved",
    "no baseline, annotation, state-ablation, natural-failure, or repair result exists"
  ]
}
```

## 8. Known unverified boundaries

The next executor must not infer completion for:

- exact public task-package identity and counts;
- case-level license and redistribution rights;
- clause-level `eval.py` coverage;
- independent semantic-oracle feasibility;
- checkpoint boundary fidelity;
- natural failure prevalence;
- annotation reliability;
- direct-transfer baseline performance;
- state information gain;
- local repair benefit;
- integration benefit.

## 9. Next executor task

Execute only Phase 2 from [`PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`](PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md):

1. identify the exact fixed task package and record source/provenance/license metadata;
2. enumerate task metadata, raw input, expected output, and `eval.py` presence;
3. produce a clause-to-evaluator coverage draft with exact code locations;
4. test independent semantic-oracle and checkpoint feasibility;
5. recommend four real tasks only if filter/revision, aggregation grain, dedup/latest record, and preservation/side effects are defensible.

Do not create variants or run LLM baselines during this audit.

### Authorisation boundary

The following work is authorised now by this handoff:

- read the fixed public source and repository;
- create local, reproducible inventory and evaluator-coverage summaries;
- record public-source provenance, licence/terms, and redistribution questions;
- recommend candidate tasks without modifying or redistributing raw source data.

The following work remains gated by human/mentor alignment or a separate explicit instruction:

- access to internal repositories, data, trajectories, or labels;
- claims of project ownership, authorship, or lab commitment;
- redistribution of public or internal task data;
- controlled mutation generation;
- pilot implementation, LLM runs, or integration changes;
- GO/PIVOT/STOP decisions after empirical evidence.

### Phase 2 pass condition

Four tasks have:

- traceable provenance;
- a documented redistribution decision;
- an independent semantic-oracle plan;
- a feasible, semantics-preserving checkpoint boundary;
- enough task-family diversity for the planned construct gate.

If fewer qualify, reduce the pilot or stop the ProfiliTable benchmark framing before implementation.

## 10. Repository boundary

Track compact protocols, scripts, manifests, reviewed summaries, schemas, and deterministic tests. Keep upstream raw data, extracted packages, model output, trajectories, logs, caches, and unreviewed derived artifacts outside Git.

No force push, history rewrite, merge to `master`, raw-data publication, repository visibility change, or collaborator/permission change is part of this handoff.
