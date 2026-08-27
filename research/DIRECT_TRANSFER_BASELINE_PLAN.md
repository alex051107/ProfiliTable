# Direct-Transfer Baseline Plan

**Status:** Phase 1 design only; no baseline has been implemented or run
**Date:** 2026-08-26
**Primary use:** distinguish a table-agent capability benchmark from a state-information-gain method
**Required transfers:** DataSpace, AgentRx, FALAT, DRIFT, DataTrace

## Decision target

The baseline study must answer two questions on the **same ProfiliTable cases**:

1. How much of intent violation, source localization, recovery, and repair can existing reference-hidden dialogue/code/trajectory methods already solve?
2. Does executed table state add unique, replayable information that changes a diagnosis or repair decision?

A method name is not a baseline. Each transfer below fixes its inputs, hidden information, output contract, oracle status, and adaptation limits.

## Scope boundary

This document specifies a future experiment. It does not add a runtime schema, instrument ProfiliTable, create mutants, download benchmark data, or report results. The next authorized action after Phase 1 is the Phase 2 task/evaluator/provenance audit.

## Shared case unit

The following record is a **conceptual comparison contract**, not a request to expand the repository schema in this phase.

```text
case_id
base_task_id
source_commit_and_license
dialogue_turns D = (u_1, ..., u_T)
gold_intent_versions A* = (A*_1, ..., A*_T)         # scorer only in main track
agent_actions/code/ordinary_observations tau
optional executed checkpoints Q = (Q_0, ..., Q_K)   # treatment input only
candidate_final_artifact Y
hidden_final_oracle O*
gold lifecycle L*:
  first_local_error
  first_intent_violation
  source_error_step
  first_persistent_divergence
  propagation_steps
  recovery_step
  final_failure_step
gold violated_clause_id C*
gold executable witness W*
optional localized repair P*
```

The lifecycle fields must remain separate. [DataSpace](https://arxiv.org/abs/2608.03451v1) motivates earliest uncorrected outcome-determining divergence; [AgentRx](https://arxiv.org/abs/2602.02475v1) motivates first unrecovered failure; [TrajDebug](https://arxiv.org/abs/2608.06346v1) motivates resolved/active and terminal-footprint distinctions. They are related labels, not synonyms.

## Visibility contract

| Information | Table agent in primary A track | Reference-hidden diagnostic baseline | State-treatment diagnostic baseline | Oracle upper bound | Scorer/adjudicator |
|---|---:|---:|---:|---:|---:|
| User dialogue and source tables | yes | yes | yes | yes | yes |
| Agent code/actions and ordinary runtime/tool output | own execution | yes | yes | yes | yes |
| Candidate final artifact | own artifact | yes | yes | yes | yes |
| Benchmark-injected checkpoints or normalized state deltas | no | no | yes | yes | yes |
| Gold active-intent graph | no | no | no | yes, in a separately named condition | yes |
| Reference output / verified solution | no | no | no | yes, separately named | yes |
| Hidden `eval.py` logic/configuration | no | no | no | only if reproducing a source method that requires it | yes |
| Gold source/lifecycle labels and witness ledger | no | no | no | no during prediction | yes after prediction |
| Binary or scalar failure signal | after submission only, if normal task protocol permits | same frozen signal for every diagnostic method | same | same | generated from hidden oracle |

The main result must be reference-output-withheld. A source method that uses the reference result, evaluation configuration, verified solution, or gold contract becomes an **oracle upper bound**, not a deployable baseline.

## Planned Stage 0 case set

After Phase 2 verifies source, license, evaluator coverage, and checkpoint feasibility, select four real ProfiliTable tasks spanning:

1. filter boundary plus requirement revision;
2. aggregation grain;
3. deduplication/latest-record selection;
4. input preservation or side effects.

For each base task, the planned controlled diagnostic gate uses four variants from `TP2_BENCHMARK_FIRST_MASTER_PLAN.md`:

| Variant | Role in evaluation | Expected diagnosis behavior |
|---|---|---|
| clean | true-negative control | accept; no fabricated source error |
| persistent semantic error | localization positive | detect violated clause, source, persistence, witness, and consequence |
| recovered version of the same early error | lifecycle control | record recovery; do not label the corrected exploration as the final primary cause |
| benign-equivalent implementation | invariance control | accept despite different code or transformation path |

This produces `4 base tasks × 4 variants = 16 instances`. It is a construct/falsification gate, not a ranking dataset or statistical estimate. No variant is created in Phase 1.

## Common output contract

Every diagnostic baseline returns one structured prediction:

```text
final_status: accept | fail | unresolved
active_clause_set_pred
violated_clause_id_pred | null
first_local_error_pred | null
first_intent_violation_pred | null
source_error_step_pred | null
first_persistent_divergence_pred | null
propagation_steps_pred[]
recovery_step_pred | null
lifecycle_pred: clean | costly_resolution | latent_active | manifest_active | unresolved
evidence_pred[]:
  evidence_type
  artifact_or_step_id
  row_column_cell_formula_statistic_selector
  observed_value
  expected_property
  replay_instruction
counterfactual_or_patch_pred | null
confidence
```

`unresolved` is a valid output. An unsupported precise diagnosis is worse than calibrated abstention.

## Shared input views

All methods must be evaluated on compatible information conditions:

| View ID | Inputs | Purpose |
|---|---|---|
| V0 | candidate final artifact only | ProfiliTable-style outcome control |
| V1 | dialogue + final artifact | final artifact with current user intent |
| V2 | dialogue + code/actions + ordinary observations + final artifact | strongest no-injected-state trajectory view |
| V3 | V2 + model-predicted active contract | fair contract-induction pipeline |
| V4 | V2 + gold active contract | contract-oracle upper bound; not a main result |
| V5 | V2 + executed checkpoint deltas | state-information treatment |
| V6 | V5 + row/cell/statistic lineage and replay handles | full executable-evidence treatment |
| V7 | V6 + reference output/verified solution | reference-rich oracle upper bound only |

For C, the decisive comparison is V2/V3 versus V5/V6. V4 isolates intent-reconstruction error. V7 estimates the ceiling created by oracle leakage and must never be merged with reference-hidden results.

## Baseline 1 — DataSpace transfer

**Official source:** [DataSpace v1](https://arxiv.org/abs/2608.03451v1); [official code at `6491caa`](https://github.com/HKUSTDial/DataSpace/commit/6491caa4c70cc06cacb6103ba73cefb00746abfe).

### Source method boundary

The paper's retrospective audit examines 136 failed trajectories with the observable trace, workspace, submitted prediction, reference result, evaluation configuration, and verified solution. It labels one primary stage/subtype using the earliest observable divergence that conflicts with the verified solution, remains uncorrected, and determines or prevents the final submission. Corrected exploratory errors are excluded. The audit proposes a counterfactual correction but does not execute a localized repair.

### Transfer variants

1. **DS-Final (V0):** run the frozen task evaluator on the candidate artifact. Output only final pass/fail. This controls for what process labels add beyond the original result.
2. **DS-Hidden (V2):** give task dialogue, workspace inventory, failed trace, ordinary observations, final artifact, and the common failure signal. Hide reference output, `eval.py` internals, verified solution, lifecycle gold, and witness ledger. Ask for DataSpace's stage taxonomy plus the shared output contract.
3. **DS-State (V5):** add executed checkpoint deltas, while keeping all gold hidden.
4. **DS-Oracle (V7):** reproduce the paper's reference-rich visibility as closely as licensing and assets permit. Report only as an oracle upper bound.

### Table adaptation

Map DataSpace stages to table-agent phenomena without replacing the shared labels:

| DataSpace stage | ProfiliTable examples |
|---|---|
| intent | stale or missing requirement clause |
| discovery | wrong sheet/table/column selected |
| extraction | wrong rows or values read |
| grounding | entity/key/date/column semantics misresolved |
| computation | filter, join, aggregation, grain, or type error |
| materialization | correct computation written to wrong shape/location or source modified |
| termination | false completion, failure to submit, or unnecessary continued edits |

### Transfer limit and kill condition

If DS-Hidden or DS-State reaches the annotation ceiling and its table mapping is stable, there is no standalone B contribution. If only DS-Oracle succeeds, the result demonstrates oracle dependence, not state value.

## Baseline 2 — AgentRx transfer

**Official source:** [AgentRx v1](https://arxiv.org/abs/2602.02475v1); [official code/data at `f228165`](https://github.com/microsoft/AgentRx/commit/f228165bfec60a801fd5fedd9d8ffe0f9de0c69d).

### Source method boundary

AgentRx consumes task/schema/policy context and complete messages, tool calls, tool outputs, and observable environment state. It synthesizes guarded constraints, runs programmatic or semantic checks, and selects the first unrecovered critical failure with evidence. It does not execute a repair.

### Transfer procedure

1. Convert each ProfiliTable trajectory into AgentRx's message/action/observation IR.
2. Compile explicit dialogue clauses, table/tool schemas, and repository policy into candidate constraints. In V3 these constraints are model-predicted; in V4 they come from the hidden gold contract.
3. Implement or prompt two validator classes in the future experiment:
   - programmatic validators for shape, schema, row predicates, aggregation identities, preservation, and file existence;
   - semantic validators only where a deterministic property is unavailable.
4. Preserve the complete validation log with cited step/artifact evidence.
5. Ask the diagnosis stage to emit the shared label contract, including `unresolved`.

### Conditions

- **ARX-Trace:** V2, with constraints derived only from user text/schema/policy and ordinary prefix observations.
- **ARX-PredContract:** V3.
- **ARX-GoldContract:** V4 oracle-intent condition.
- **ARX-State:** V5, adding checkpoint-derived constraint results.

### Transfer limit and kill condition

Generated constraints can inherit the trajectory's misunderstanding. ARX-GoldContract therefore measures contract-induction headroom. If ARX-Trace/PredContract already solves the cases, state is not the differentiator. If GoldContract succeeds and PredContract fails, pivot toward intent/contract induction rather than state-grounded localization.

## Baseline 3 — FALAT transfer

**Official source:** [FALAT v1](https://arxiv.org/abs/2606.00765v1). `DATA_INSUFFICIENT`: no official code/data release or fixed commit was found in this audit.

### Source method boundary

FALAT models typed dependencies among steps, including follow-up, propagation, correction, error-shift, no-influence, and dead-end relations. It searches for the earliest minimal decisive set whose counterfactual correction recovers the expected outcome. The formal definition uses expected output `o*`; the operational diagnosis uses an expected-behavior prior built from task/tool context. Exact oracle visibility is therefore a required audit variable.

### Fair reimplementation contract

Because a stable implementation was not found, this is a **specification-level reimplementation**, labeled as such:

1. Build nodes for dialogue clauses, code/actions, ordinary observations, and final artifact under V2.
2. Add typed edges for data dependence, control dependence, clause dependence, propagation, correction, and recovery.
3. Infer an expected-behavior prior from visible dialogue, schema, and tools only.
4. Search candidate source steps; produce a counterfactual correction proposal.
5. For the main track, evaluate the proposal using hidden property checks after prediction. Do not reveal the full expected table.
6. Under V5/V6, add checkpoint and lineage nodes; under V7, allow reference output only as an explicitly named oracle variant.

### Conditions

- **FALAT-RH:** V2/V3 reference-hidden property-oracle adaptation.
- **FALAT-State:** V5/V6 with executable dependency nodes.
- **FALAT-Oracle:** V7 reference-rich upper bound.

### Transfer limit and kill condition

A property checker can establish that a proposed repair satisfies specified clauses; it cannot silently become the model's input. If FALAT-RH localizes source and propagation without checkpoint nodes, the state claim weakens. If only the oracle variant works, no deployable diagnosis claim follows.

## Baseline 4 — DRIFT transfer

**Official source:** [TELBench/DRIFT v2](https://arxiv.org/abs/2606.02060v2); [official code at `1280b37`](https://github.com/NJU-LINK/DRIFT/commit/1280b373b5af1954bf0577bf6d58b38e1bce341e).

### Source method boundary

DRIFT converts a trajectory into semantic spans and a claim ledger, tracking claim introduction, first consequential use, later reuse, and support. TELBench labels harmful spans and the earliest harmful error while excluding ordinary exploration, failed searches, tentative hypotheses, corrected errors, and tool noise. Diagnosis does not require a gold expected answer.

### Transfer procedure

1. Serialize each user turn, code edit/action, tool result, and explicit agent assertion as an ordered semantic span.
2. Extract claims about the active intent, selected data, transformation semantics, intermediate result, completion, and repair.
3. Link each claim to visible support in V2 and track the first consequential commitment.
4. Emit the shared labels; map earliest harmful commitment to a prediction, not automatically to gold `source_error_step`.
5. In V5, append normalized checkpoint-delta spans.
6. In V6, attach replayable evidence handles to claims rather than replacing claim text with gold labels.

### Conditions

- **DRIFT-Trace:** V2.
- **DRIFT-StateText:** V5, with state deltas serialized into the same span representation.
- **DRIFT-Lineage:** V6.

### Transfer limit and kill condition

DRIFT is the key test of whether state is merely another textual observation. A C contribution survives only when state or lineage supplies evidence unavailable from DRIFT-Trace and the resulting unique win passes replay. More tokens or more detailed prose alone do not count.

## Baseline 5 — DataTrace transfer

**Official source:** [DataTrace official repository at `48a89e5`](https://github.com/HKUSTDial/datatrace/commit/48a89e59b4aeef5a01d5ed68c1a1b4d4dc84a411). `DATA_INSUFFICIENT`: the repository says the paper is forthcoming, so claims are limited to code and artifact observations.

### Source artifact boundary

The fixed repository exposes runnable database environments with a controlled faulty object, remote symptom, artifact dependency graph, reference evidence path, reference repaired outputs, and tests. Typed investigation actions include inspection, profiling, lineage tracing, and SQL execution. The harness evaluates root-cause accuracy, evidence quality, and fixes.

### Transfer graph

| Node type | ProfiliTable instance |
|---|---|
| intent clause | versioned user requirement atom |
| source artifact | input sheet/table/file and schema |
| transformation | code statement or normalized dataframe operation |
| state artifact | table checkpoint or state delta |
| derived value | row set, key set, cell/formula, aggregation statistic, file metadata |
| symptom | failed final property or violated active clause |
| test | hidden clause checker, metamorphic relation, or final evaluator |

Planned edges include `supersedes`, `reads`, `writes`, `filters`, `joins`, `groups`, `aggregates`, `derives`, `propagates_to`, `corrects`, and `violates`.

### Conditions

- **DT-GivenContract:** V6 plus the gold active contract field from V4, while reference output, cause, evidence, fix, and evaluator internals remain hidden. This composite condition measures evidence localization independently of intent induction; it is not an undifferentiated merge of V4 and V6.
- **DT-PredContract:** V6 plus a model-predicted active contract. Compare it directly with DT-GivenContract to isolate contract-induction error under the same state/lineage visibility.
- **DT-NoStateGraph:** V2, containing only dialogue/code/ordinary observations.
- **DT-Repair:** after prediction, apply the proposed localized patch in an isolated copy and run hidden checks. The agent never sees reference repaired output.

### Transfer limit and kill condition

DataTrace's cases use controlled single faults and static intent. ProfiliTable natural failures, recovery, and revisions cannot inherit those claims. If DT-GivenContract succeeds but PredContract fails, study contract induction. If both succeed and no-state graph is equally strong, state/lineage is not a novel method signal. If a real fix cannot be replayed, do not count a natural-language counterfactual as repair.

## Additional required controls

These controls prevent the five transfers from being compared against weak alternatives:

- **ProfiliTable final evaluator:** final-outcome control, with task-level coverage audited rather than assumed.
- **Intent-only control:** Task Shield-style action-to-active-goal relevance, with no table state.
- **Spreadsheet reflection control:** SheetMind-style before/after state reflection, labeled conceptual if no official code becomes available.
- **Deterministic property checker:** clause checks independent of the diagnosis model.
- **Metamorphic checker:** expert-validated relations such as applicable row-order invariance, reversible transforms, or scaling; a pass is partial evidence, not correctness proof ([TSE 2014](https://doi.org/10.1109/TSE.2013.46)).
- **Oracle evidence control:** gold contract and reference-rich inputs, clearly separated.

## Fair-comparison protocol

### Frozen inputs and budgets

- Same 16 instances and artifact bytes for all methods.
- Same backbone/version, decoding settings, attempt count, context budget, and tool budget where architectures permit.
- Frozen prompt/config before scoring; report deviations required by a source implementation.
- Report input tokens/bytes, tool calls, latency, and monetary cost because state conditions receive more information.
- No tuning or method selection on the 16 scored instances. Development examples must be disjoint by base workflow.

### Gold and model independence

- The same model instance must not generate a case, create gold, predict labels, and adjudicate its own output.
- Gold active intent, source/lifecycle labels, witness, repair, reference output, and evaluator internals remain hidden during main-track prediction.
- Programmatic checks are preferred when the clause is executable. Semantic judges must cite evidence and may output `unresolved`.
- Human annotation is independently frozen before method outputs are scored; adjudicators may see method outputs only after independent labels are recorded.

### Leakage and provenance

- Record source URL/commit, retrieval date, task license/terms, transformation identity, annotation version, model/tool version, and release decision.
- Do not commit source archives, extracted data, model traces, or run dumps. Keep them in ignored local storage.
- On expansion, group splits by base workbook/workflow, template, source trace, and task family; variants of one base task never cross splits.
- Record exact/near-duplicate and contamination status; paraphrase is not treated as proof of independence.

## Metrics

| Construct | Primary metric for Stage 0 | Guardrail |
|---|---|---|
| final execution | per-case hidden-oracle pass | audit evaluator clause coverage |
| active intent | exact active-clause set plus clause precision/recall | score revisions/retractions separately |
| self-detection | fail/accept/unresolved confusion and selective risk-coverage | clean and benign-equivalent false rejection |
| violated clause | exact clause accuracy | `unresolved` and ambiguous gold retained |
| localization | exact source step and ±1-step accuracy | report first local, first violation, persistent, and final-failure labels separately |
| lifecycle | four-state accuracy/confusion | recovered errors must not be collapsed into clean or primary failure |
| evidence | witness precision/recall and executable replay rate | unsupported citation counts as failure |
| repair | hidden-check pass after isolated patch | report changed rows/cells/code scope and whole-regeneration control |
| consequence | count of cases where method changes accept/retry/repair correctly | no stable system-ranking claim from 16 instances |
| efficiency | tokens, tool calls, latency, evidence probes, regeneration count | compare at matched retry/attempt policy |

## Incremental state test

A **state-unique win** is counted only when all conditions hold:

1. the strongest frozen V2/V3 no-state baseline is wrong or unresolved;
2. a V5/V6 condition identifies the correct clause and source or produces a hidden-check-passing repair;
3. the cited row/cell/statistic/lineage witness replays successfully;
4. the required evidence is not already present verbatim in ordinary trace input;
5. no reference output, evaluator internals, gold label, or witness ledger leaked into prediction.

The Stage 0 design proposal advances C only if there are at least three state-unique wins across at least three semantic families, every claimed unique witness replays, and state introduces no more than one new false rejection among clean, recovered, and benign-equivalent controls. These are predeclared falsification thresholds for a 16-case construct gate, not estimates of population effect or statistical significance.

## Decision table after the future run

| Observation | Decision |
|---|---|
| A shows separable capability headroom; state adds little | Continue A; keep checkpoints hidden as scoring evidence |
| State adds replayable, reference-hidden wins with controlled false rejection | Pivot method work to C; keep A as the evaluation setting |
| Gold contract helps but predicted contract fails | Pivot to intent/contract induction; do not attribute failure to missing state |
| Direct transfers match annotation ceiling | Stop standalone B and C novelty framing; retain integration/evaluator-audit value |
| Localized patch does not beat matched regeneration | Defer D and repair claims |
| Labels or oracles are unstable | Stop localization/benchmark scaling and repair the construct first |
