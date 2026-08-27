# ProfiliTable / DataFlow-Table 项目完整交接说明

**日期：** 2026-08-26  
**用途：** 让振鹏在不依赖此前聊天记录的情况下，从上次组内交流开始，完整理解项目缘起、研究问题如何演化、当前仓库状态、文献边界、尚未解决的问题，以及接下来应该按什么顺序推进。  
**当前 canonical 工作仓库：** `alex051107/ProfiliTable`  
**当前 canonical 研究分支：** `research/benchmark-first-plan-v0.2`  
**该快照对应分支 head：** `309b12a`
**上游固定基线：** `Eularioal/ProfiliTable@f023ec4b754555000a659b93fd514645c55e3cec`

> **Phase 1 completion update:** This document preserves the project history and the pre-Phase-1 handoff state. Phase 1 has since selected **A — Table-Agent Capability Benchmark** as the primary formulation and **C — Method-First State-Grounded Evaluator** as the fallback. Sections that say the formulation is unselected or that the four Phase 1 deliverables remain to be written are historical snapshots. For the current reviewed status, canonical reading order, resolved review findings, and next authorised gate, read [`research/PHASE1_HANDOFF_REVIEW.md`](research/PHASE1_HANDOFF_REVIEW.md) first, then [`research/RESEARCH_DECISION_MEMO.md`](research/RESEARCH_DECISION_MEMO.md). The evidence-based decision path is recorded in [`research/PHASE1_DECISION_RATIONALE.md`](research/PHASE1_DECISION_RATIONALE.md).

---

# 0. 先给结论：我们现在到底在做什么

目前还没有正式开始构建新的 benchmark，也没有开始跑模型实验，更没有确认 novelty。

Phase 1 的研究问题选择与 novelty 审计已经完成。当前项目处于：

> **进入实现前的 bounded Phase 2 ProfiliTable task / evaluator / provenance audit。**

我们最初想研究的是：

> **Table Agent 在用户要求会补充、修订或撤回时，能不能真正把当前任务做对；如果没有做对，它能不能知道自己错了、指出错在哪里，并最终修复。**

在查阅 ProfiliTable、CITBench、DataSpace、UserIntentBench、AgentRx、FALAT、TELBench/DRIFT、DataTrace 等工作后，我们发现：

- 多轮表格任务已经有人做；
- evolving/shifting intent 已经有人做；
- first error / first unrecovered error 已经有人做；
- source error 与 downstream propagation 已经有人做；
- evidence-grounded root-cause diagnosis 也已有相邻工作。

因此，当前不能直接声称：

- “第一个多轮表格 benchmark”；
- “第一个 evolving-intent benchmark”；
- “第一个 first-error localization benchmark”；
- “第一个 semantic verifier”；
- “第一个 evidence-grounded data-workflow diagnosis”。

Phase 1 的 primary 方向是 Table-Agent Capability Benchmark。当前需要先确认公开 ProfiliTable tasks、evaluator coverage、provenance/license 与 checkpoint feasibility 是否足以承载这个问题。

State-grounded evaluator 被保留为 fallback，核心问题仍是：

> **在 reference-output-withheld 条件下，真实 intermediate table state 是否为错误定位或修复提供 final-output scorer 和 dialogue/code trajectory diagnosis 没有的增量信息？**

这仍是待实验推翻的候选方法方向，不是已成立 contribution。

---

# 1. 上次组内交流到底说了什么

以下内容来自 2026-08-21 组内 PhD 交流的用户整理，不是逐字录音稿。

## 1.1 会议中明确表达的方向

DataFlow-Table 的长期范围计划覆盖：

1. 数据发现 / 获取；
2. 数据处理；
3. 数据分析；
4. 将这些能力整合进自然语言驱动的数据系统。

对方给出的研究推进建议是：

```text
先从难任务和评测定义出发
→ 用当前强 Agent 跑这些任务
→ 暴露真实能力缺口
→ 再决定做 evaluator、harness 还是 post-training
```

这句话非常关键。它意味着组内并没有要求你立即发明一个模型，也没有要求你先做大量系统工程；更合理的入口是：

> **先确认现在的 Agent 到底做不好什么，而且这个“做不好”能够被严谨、重复地评测。**

## 1.2 会议没有确认的事项

会议没有确认：

- 正式加入实验室；
- 你拥有某个任务或模块的 ownership；
- 内部仓库、内部数据或失败 trajectory 的访问权限；
- 投稿 venue；
- 论文作者顺序；
- 经费；
- GPU；
- 固定 day-to-day mentor；
- benchmark 数据能否公开再分发。

因此，所有后续计划都必须把这些事项标为 `DATA_INSUFFICIENT`，不能根据聊天气氛推断已经获得。

---

# 2. 最初研究目的是什么

最初目的不是：

- 造一个新题库；
- 写一个 JSON Schema；
- 做一个 state checker；
- 给 ProfiliTable 加几个 Operator；
- 单纯定位 first error。

最初的北极星是：

> **围绕 ProfiliTable / DataFlow-Table 找到一个既贴合真实 Table Agent 系统、又能训练 Agent Engineer 能力，并有机会长成 A 会论文的研究问题。**

这个研究问题最自然地分成五层能力：

1. **Execution**：Agent 能不能把当前表格任务做对？
2. **Intent tracking**：用户补充、修订、撤回要求后，Agent 能不能保持最新要求？
3. **Self-detection**：代码能运行时，Agent 能不能知道自己语义上做错？
4. **Localization**：Agent 能不能指出违反了哪条要求、从哪一步开始错，而不是只看到最终症状？
5. **Recovery**：Agent 能不能修复错误，而且不引入新的错误？

一个 benchmark 可以只测其中几层，但必须明确：

> 被评对象是谁，输入是什么，gold 是什么，输出标签是什么。

---

# 3. ProfiliTable 本身做什么

ProfiliTable 是一个自动表格处理 Agent 系统。

它的基本循环是：

```text
用户自然语言任务
→ Interpreter 理解任务
→ Profiler 主动查看原始表格
→ Decomposer 拆分复杂任务
→ RAG 检索已有 Operator 模板
→ Generator 生成 Python
→ 执行代码
→ Evaluator 用隐藏 GT / eval.py 评分
→ Summarizer 查看处理结果并给反馈
→ 再次 profiling / generation
```

其核心贡献是 dynamic profiling：Agent 不是固定读取所有统计，而是根据任务决定下一步需要查看哪一列、哪些值、哪些分布。

但其公开实验中，Evaluator 主要依赖：

```text
task-specific eval.py
+ hidden ground-truth output
```

所以 ProfiliTable 很适合回答：

- 代码能不能跑；
- 最终输出和标准答案有多接近；
- feedback loop 能不能改善最终分数。

它不天然提供：

- 每轮 active / obsolete requirements；
- 每个 subtask 的独立 intermediate table；
- first semantic divergence gold；
- source-vs-propagation label；
- recovered-vs-persistent label；
- deployment-time self-monitoring protocol。

---

# 4. 为什么研究方向反复变化

## 4.1 第一版：Semantic Verifier

最初想法是：

> ProfiliTable 或 DataFlow-Harness 代码能运行，但可能语义错误，因此做 semantic verifier。

问题是：

- contract verification 已有大量工作；
- first-error localization 已有大量工作；
- local repair 已有工作；
- 如果只加一个 LLM Judge，容易退化成 prompt engineering。

## 4.2 第二版：First Error / Persistent Divergence Benchmark

随后想做：

> 多轮需求下，定位第一次持续未修复的语义错误。

问题是：

- DataSpace 已有 earliest observable unrecovered divergence audit；
- AgentRx 已有 constraint + evidence + critical step；
- FALAT 已有 source vs propagation 与 counterfactual sufficiency；
- TELBench/DRIFT 已有 earliest harmful commitment / evidence localization。

因此 first error 可以作为 benchmark 维度，但不能单独作为 novelty。

## 4.3 第三版：Table-State Evidence

为了寻找 residual gap，问题被收缩成：

> intermediate table state 是否比 text/code trajectory 多提供可执行的数据证据？

这个收缩有合理性，因为复杂表格错误往往必须看真实 rows、cardinality、grain、file event 才能确认。

但后来执行过度收缩：

> 从“benchmark Table Agent 的能力”逐渐变成“benchmark 一个外部诊断器会不会读 snapshots”。

这就是最近产生上下文混乱的来源。

## 4.4 当前修正：四种 formulation 并行比较

> **Phase 1 update:** The comparison below has been completed. A is now the primary formulation and C is the fallback; see `research/RESEARCH_DECISION_MEMO.md`. The descriptions remain useful as the alternatives that were evaluated.

当前不再默认 state-grounded diagnosis 就是最终答案，而是要求比较四种项目形状：

### A. Table-Agent Capability Benchmark

被评对象：Table Agent。  
测量：execution、intent tracking、self-detection、localization、可选 repair。  
最贴近最初目标。

### B. Process-Diagnostic Benchmark

被评对象：外部 evaluator / diagnoser。  
测量：violated requirement、source step、propagation、recovery、evidence。

### C. Method-First State-Grounded Evaluator

被评对象：新的诊断方法。  
核心比较：是否比 text/trajectory-only diagnosis 更强。

### D. Harness / Self-Monitoring Integration

被评对象：ProfiliTable / DataFlow-Table runtime。  
核心比较：process-aware checking 是否提高真实 task success、减少错误提交与无效 debugging。

Phase 1 已选定 A 为 primary、C 为 fallback；B 保留为诊断与 direct-transfer baseline 层，D 延后。

---

# 5. 当前文献审查的结论

## 5.1 已经覆盖、不能单独声称新的部分

### ProfiliTable — `arXiv:2605.12376v2`

已覆盖：

- dynamic profiling；
- operator retrieval；
- feedback refinement；
- 18 类 table-processing tasks；
- runnable 与 task correctness 的区分。

### DataGovBench / DataGovAgent — `arXiv:2512.04416`

已覆盖：

- operator-level 与 DAG-level data-governance tasks；
- task-specific evaluator；
- Planner–Executor–Evaluator；
- feedback debugging。

### CITBench — `arXiv:2608.00018v1`

已覆盖：

- interactive tabular processing；
- 4 类、18 种任务、1,296 个实例；
- multi-turn；
- evolving requirements / interaction noise。

它阻断“first interactive/evolving table benchmark”的 claim。

### UserIntentBench — public repo `d294828...`

已覆盖：

- hidden intent graph；
- latent/shifting intent；
- belief graph；
- post-shift alignment；
- obsolete-constraint suppression；
- stale evidence diagnostics。

它阻断“first active intent representation”的 claim。

### DataSpace — `arXiv:2608.03451v1`

已覆盖：

- heterogeneous workspace；
- deterministic complete-table evaluation；
- process-level failure audit；
- earliest unrecovered observable divergence 的相邻定义。

### AgentRx — `arXiv:2602.02475v1`

已覆盖：

- constraint synthesis；
- stepwise checking；
- evidence log；
- critical failure localization。

### FALAT — `arXiv:2606.00765v1`

已覆盖：

- dependency-guided failure attribution；
- source-vs-propagation；
- counterfactual sufficiency。

### TELBench / DRIFT — `arXiv:2606.02060v2`

已覆盖：

- span-level error localization；
- earliest harmful commitments；
- claim/evidence/dependency auditing。

### DataTrace — `HKUSTDial/datatrace`

公开仓库已显示：

- database pipeline fault object；
- dependency graph；
- evidence path；
- root-cause localization；
- repair framing。

正式论文状态仍需继续核实。

## 5.2 当前仍可能存在、但尚未成立的 candidate gap

候选 gap 不是 first error 本身，而是下列组合是否产生增量价值：

```text
versioned table intent
+ executable table-state transition
+ machine-checkable row/cell/statistic/file witness
+ reference-output-withheld evaluation
```

必须通过 direct-transfer baseline 和真实 pilot 才能确认。

## 5.3 当前必须补齐的知识

1. CITBench 在线评测到底暴露哪些 intermediate state；
2. DataSpace process audit 的完整操作化细节；
3. AgentRx / FALAT / DRIFT 能否直接迁移到 ProfiliTable trace；
4. DataTrace 的正式数据和论文状态；
5. ProfiliTable 公开 task inventory 与 `eval.py` coverage；
6. ProfiliTable 内部是否已保存 intermediate states / root-cause labels；
7. benchmark construct validity、annotation reliability、difficulty calibration 与 leakage；
8. proposed mutant 是否真会在自然 Agent failure 中出现；
9. step boundary 是否稳定；
10. 数据再分发许可。

---

# 6. 当前仓库状态

## 6.1 Canonical 仓库

```text
alex051107/ProfiliTable
```

该仓库是 ProfiliTable 的 fork。

### `master`

用途：保持上游 replication baseline。  
当前基线：`f023ec4b754555000a659b93fd514645c55e3cec`。  
没有加入本项目研究代码。

### `research/benchmark-first-plan-v0.2`

用途：研究计划、novelty audit、upstream audit protocol、Codex execution protocol。  
本节原始快照 head 为 `9c37cf6dc13fb1931ec328cee3266423c4352cce`；远端交接提交 `309b12a` 已在本轮开始前 fast-forward 整合。最终上传后的 head 应以 `git rev-parse HEAD` 和 GitHub branch readback 为准。
没有修改 ProfiliTable runtime。

新增文件：

1. `CODEX_RESEARCH_START_HERE.md`  
   给 Codex 的上下文重建和广泛探索入口。

2. `TP2_BENCHMARK_FIRST_MASTER_PLAN.md`  
   当前 benchmark-first 设计的完整 master plan。

3. `research/PAPER_GAP_AUDIT.md`  
   文献覆盖、blocked claims、candidate gaps 和 missing knowledge。

4. `research/PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`  
   ProfiliTable fixed package、tasks、metadata、`eval.py` 和许可 audit 方案。

5. `research/CODEX_EXECUTION_AND_REPO_HYGIENE.md`  
   分支、worktree、数据、缓存、commit、Codex/人工职责规则。

6. `.gitignore` 强化  
   忽略 venv、cache、logs、data、artifacts、runs、research-derived 等。

Phase 1 completion package 另增加：

7. `research/NOVELTY_MATRIX.tsv`；
8. `research/ALTERNATIVE_FORMULATIONS.md`；
9. `research/DIRECT_TRANSFER_BASELINE_PLAN.md`；
10. `research/RESEARCH_DECISION_MEMO.md`；
11. `research/PHASE1_DECISION_RATIONALE.md`；
12. `research/PHASE1_HANDOFF_REVIEW.md`。

## 6.2 Legacy / 侧向仓库

```text
alex051107/table-intent-trace
```

状态：private。  
当前已知 head：`f175ac07078a2b227292ec6a199583fff9947d8c`。  
用途：早期 process-diagnosis contract prototype；包含 T0001 synthetic fixtures、schemas、validator 和 tests。

它现在不应继续作为 canonical 主仓。

原因：

- 与 ProfiliTable runtime 割裂；
- 研究对象过早收缩成外部 diagnosis；
- 容易继续优化 schema/fixture，而没有确认正确 scientific question。

建议：

> 暂时冻结，不删除；作为历史设计和 fixture 参考。后续只有在明确选择 Formulation B/C 后，才挑选可复用内容迁回 ProfiliTable fork。

---

# 7. 当前已经完成的事情

## 7.1 已完成

- 读过并解释 ProfiliTable、DataFlow-Harness、One-Eval、DataGovBench 等核心工作；
- 明确 runnable、structural validity、final correctness、intent fidelity 的区别；
- 做过多轮外部 novelty 审查；
- 识别到 first error / active intent / root cause 等已有高度重叠；
- 创建并审查过 TableIntentTrace 早期 scaffold；
- 将 canonical 工作迁到 ProfiliTable fork；
- 固定上游 commit；
- 创建 research branch；
- 写入 master plan、paper gap audit、upstream audit、repo hygiene、Codex exploration charter；
- 保持 master/runtime 未改；
- 强化 `.gitignore`。

## 7.2 尚未完成

- 尚未正式复跑 ProfiliTable 完整公开 package inventory；
- 尚未生成可复现的 `package_manifest.tsv`；
- 尚未生成 `upstream_inventory.tsv`；
- 尚未完成逐任务 `oracle_coverage.tsv`；
- 尚未选定 4 个真实 ProfiliTable base tasks；
- 尚未构建 4×4 正式 pilot；
- 尚未运行任何 LLM baseline；
- 尚未运行 AgentRx / FALAT / DRIFT direct-transfer baseline；
- 尚未收集自然 Agent failures；
- 已选 A 为 primary、C 为 fallback，但尚未用实验验证该选择；
- 尚未证明 novelty；
- 尚未决定数据公开许可；
- 尚未创建 PR；
- 尚未获得内部 repo/data/mentor/ownership 确认；
- 尚未得到任何论文实验结果。

两个 Deep Research 请求已启动，但其最终报告尚未合并进 canonical 文档。因此当前 canonical 事实以 GitHub 分支中的已审计文档为准。

---

# 8. 现在的正确执行顺序

当前不要立即生成 benchmark，也不要修改 ProfiliTable runtime。

> **Current execution update:** Phase 0 and Phase 1 are complete. The next step is the bounded public-source/local-summary Phase 2 audit. Mentor/PM alignment still gates internal assets, ownership, redistribution, mutation generation, pilot implementation, and model experiments.

## Phase 0 — Context Reconstruction

Codex 先读取：

1. `PROJECT_HANDOFF_2026-08-26.md`
2. `CODEX_RESEARCH_START_HERE.md`
3. `TP2_BENCHMARK_FIRST_MASTER_PLAN.md`
4. `research/PAPER_GAP_AUDIT.md`
5. `research/PROFILITABLE_UPSTREAM_AND_BENCHMARK_AUDIT.md`
6. `research/CODEX_EXECUTION_AND_REPO_HYGIENE.md`

然后输出一份 context reconstruction，包含：

- original objective；
- 当前四种 formulation；
- 已覆盖 claims；
- candidate gaps；
- 已完成工作；
- 未验证问题；
- 当前 kill tests。

## Phase 1 — Novelty / Alternative Formulation Audit

**Status: complete.** The four file descriptions below are retained as the finished deliverable contract.

Codex 只创建以下四个文件：

```text
research/NOVELTY_MATRIX.tsv
research/ALTERNATIVE_FORMULATIONS.md
research/DIRECT_TRANSFER_BASELINE_PLAN.md
research/RESEARCH_DECISION_MEMO.md
```

### `NOVELTY_MATRIX.tsv`

每篇工作必须记录：

- 被评对象；
- domain；
- interaction；
- Agent input；
- evaluator input；
- gold supervision；
- labels；
- error timing；
- evidence；
- repair；
- public artifacts；
- direct-transfer feasibility；
- blocked claim；
- residual gap。

### `ALTERNATIVE_FORMULATIONS.md`

比较 A/B/C/D 四条路线：

- 科学问题；
- 与最初目标的匹配度；
- strongest overlap；
- resources；
- 六周可行性；
- A 会潜力；
- reviewer risk；
- kill test；
- fallback。

### `DIRECT_TRANSFER_BASELINE_PLAN.md`

写清楚如何把 DataSpace / AgentRx / FALAT / DRIFT / DataTrace 的方法迁移到同一组 ProfiliTable cases。

不能只写“会比较”，必须说明：

- 输入格式如何转换；
- 哪些 gold 可见；
- 输出 label 如何对齐；
- 需要哪些代码；
- 没有代码时如何构造 faithful baseline；
- 什么表现意味着我们的 candidate gap 不成立。

### `RESEARCH_DECISION_MEMO.md`

只选择：

- 一个 primary formulation；
- 一个 fallback；
- allowed claims；
- forbidden claims；
- 下一次 empirical gate；
- GO / PIVOT / STOP。

## Phase 2 — ProfiliTable Upstream Audit

只有在 Phase 1 仍认为 ProfiliTable 是合适 carrier 时才做。

输出：

```text
research/audit_results/package_manifest.tsv
research/audit_results/upstream_inventory.tsv
research/audit_results/oracle_coverage.DRAFT.tsv
research/audit_results/base_task_candidates.md
scripts/audit_upstream_package.py
tests/test_audit_upstream_package.py
```

必须：

- 记录 `data.zip` SHA-256；
- 可重算 NL2Op / NL2Dag 数量；
- 枚举 task metadata；
- 记录 raw / expected / eval.py；
- 指出每个 `eval.py` 检查与漏检；
- 推荐候选真实任务；
- 不提交 raw data。

## Phase 3 — Empirical Pilot

具体形状取决于 Phase 1 选择。

### 若选 A：Table-Agent Capability Benchmark

优先测：

- final execution；
- intent tracking；
- self-detection；
- localization；
- 可选 repair。

Table-state snapshots 主要作为 benchmark hidden scoring evidence，不一定给 Agent。

### 若选 B：Process-Diagnostic Benchmark

优先测：

- violated requirement；
- source step；
- propagation；
- recovery；
- witness。

### 若选 C：State-Grounded Method

优先比较：

```text
final-output-only
vs dialogue+code
vs trajectory-diagnosis direct transfer
vs dialogue+code+table state
```

### 若选 D：Harness Integration

需要先有可靠 evaluator，然后接回 ProfiliTable loop，测：

- semantic false acceptance；
- task success；
- debugging iterations；
- token / latency；
- repair side effects。

---

# 9. 4×4 Pilot 到底是什么

此前设计的 4×4 pilot 是一个候选 calibration experiment，不是最终 benchmark。

四个 base task family：

1. filter / revision；
2. aggregation grain；
3. dedup + latest-record selection；
4. input preservation / side effect。

每个 task 四个版本：

- `clean`：正确；
- `persistent mutant`：错误一直存在；
- `recovered mutant`：中间错误后来恢复；
- `benign equivalent`：代码不同但语义等价。

它的目的只是测试：

- 标签能不能稳定定义；
- recovered 与 persistent 能不能区分；
- benign 是否会被误判；
- intermediate state 是否提供增量；
- direct-transfer baseline 是否已经解决。

16 个实例不能用于：

- AUC；
- 显著性检验；
- 泛化结论；
- 宣称 benchmark 优于现有工作；
- 宣称论文 contribution 已成立。

---

# 10. 当前允许和禁止的研究 claim

## 10.1 当前允许

- ProfiliTable 能生成 runnable 但 semantically flawed 的代码；
- 多轮/evolving table task、intent tracking、first error、root cause 已有相邻工作；
- intermediate table state 可能提供额外诊断信息；
- 该问题值得用 pilot 检验；
- ProfiliTable 可作为 task pool / system under test 候选。

## 10.2 当前禁止

- 这是第一个 evolving-intent table benchmark；
- 这是第一个 semantic verifier；
- 这是第一个 first-error benchmark；
- 这是第一个 evidence-grounded database/table diagnosis；
- state-grounded diagnosis 已经优于 existing methods；
- 新 benchmark 已经成立；
- 16 个 fixtures 是模型结果；
- reference-output-withheld 等于 oracle-free；
- 数据许可允许公开；
- 已经获得组内 ownership；
- 已经确定 A 会 venue；
- 可以保证发表。

---

# 11. Codex 与人工的职责边界

## 11.1 Codex 可以自动执行

- 搜索与整理论文和 repo；
- 生成 novelty matrix draft；
- 固定 commit；
- 计算 archive hash；
- 枚举 tasks；
- 解析 `task_meta.json`；
- 静态检查 `eval.py`；
- 生成 oracle coverage draft；
- 写 audit scripts/tests；
- 插 checkpoint；
- 根据已批准 mutation grammar 生成 variants；
- 运行测试和 evaluator；
- 做 leakage check；
- 重放 executable witness；
- 整理 raw results。

## 11.2 必须人工判断

- 用户要求是否被忠实解释；
- `eval.py` 是否完整覆盖 requirement；
- step boundary 是否语义合理；
- mutation 是否只改一个语义变量；
- source 与 propagation；
- recovered 与 persistent；
- data license；
- novelty；
- paper claim；
- GO / PIVOT / STOP；
- 是否公开；
- 是否向组内提出 ownership。

---

# 12. 本地接手与仓库卫生

## 12.1 推荐本地目录

```text
ProfiliTable/
  tracked source + research docs

../_worktrees/
  profilitable-novelty-audit/
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

## 12.2 推荐 Git 设置

```bash
git clone https://github.com/alex051107/ProfiliTable.git
cd ProfiliTable

git remote add upstream https://github.com/Eularioal/ProfiliTable.git
git fetch --all --prune

git checkout research/benchmark-first-plan-v0.2

git worktree add ../_worktrees/profilitable-novelty-audit \
  -b research/novelty-audit-v0.1 \
  research/benchmark-first-plan-v0.2
```

## 12.3 清理命令

```bash
git status --short
git worktree list
git clean -ndX   # 只预览 ignored generated files
git clean -fdX   # 确认后才执行
git diff --check
```

不要随意运行：

```bash
git clean -fdx
```

因为它会删除所有未跟踪文件，包括非 ignored 文件。

## 12.4 当前 `.gitignore` 的重要边界

当前分支全局忽略：

```text
*.csv
*.json
```

这对防止 raw/derived junk 很有效，但未来若需要提交 reviewed JSON schema、small JSON fixtures 或 canonical CSV，则必须有意识地修改 ignore policy，不能用 `git add -f` 长期绕过。

建议未来改成更窄的规则，例如只忽略：

```text
data/**
runs/**
artifacts/**
research/derived/**
```

并允许：

```text
schemas/*.json
fixtures/reviewed/*.json
research/audit_results/*.tsv
```

该修改应单独 PR，不要混进实验代码。

## 12.5 Commit 原则

每个 commit 只回答一个问题。

良好例子：

```text
docs: complete novelty matrix draft
audit: add reproducible ProfiliTable task inventory
test: validate evaluator coverage manifest
feat: instrument four reviewed table workflows
eval: add dialogue-code diagnosis baseline
```

避免：

```text
update stuff
research changes
fix all
new benchmark
```

---

# 13. 当前最重要的 kill tests

任何方向都必须能被实验推翻。

## 13.1 A 路线 kill test

如果 CITBench + evolving-intent baseline 已经充分测量 execution、intent tracking、self-detection 和 localization，则不应再做同类 capability benchmark。

## 13.2 B 路线 kill test

如果 DataSpace / AgentRx / FALAT / DRIFT / DataTrace 直接迁移已经能稳定完成 violated-requirement、source-step、propagation、recovery 和 evidence diagnosis，则 process-diagnostic benchmark novelty 不成立。

## 13.3 C 路线 kill test

如果 intermediate table state 没有解决 trajectory-only baseline 解决不了的实例，或只带来更长输入而不带来决策改进，则 state-grounded method 不成立。

## 13.4 D 路线 kill test

如果 process-aware checker 不提高 task success、不降低 semantic false acceptance、不减少 debugging cost，且只增加系统复杂度，则 integration 方向不成立。

---

# 14. 下一次与组内 PhD / 博后必须确认的问题

1. DataFlow-Table 当前主问题到底是 task construction、evaluator、trajectory logging、harness 还是 post-training？
2. 内部 ProfiliTable/DataFlow-Table 是否保存：
   - 多轮 active requirements；
   - intermediate tables；
   - natural failure traces；
   - root-cause labels；
   - evaluator coverage notes？
3. 公开 `data.zip` 与内部 benchmark 有什么差异？
4. 论文 90+39 与公开包先前审计 90+37 的差异是什么？
5. 数据和派生 benchmark 是否允许公开再分发？
6. 你可以独立 own 哪个模块：benchmark schema、evaluator、failure analysis、harness integration 还是 post-training？
7. 谁提供 day-to-day review？
8. 是否有真实用户 logs / Agent runs？
9. 如果做 benchmark，组内希望最后服务哪一个决策：模型比较、系统 debugging、训练数据生成，还是产品 acceptance？
10. 4–6 周后什么 deliverable 算有价值？

---

# 15. 接下来 7 天的推荐计划

Phase 1 research decision 已完成。接下来 7 天应完成公开固定版本的 Phase 2 audit，不立即实现 benchmark。

## Day 1

- 固定公开 ProfiliTable task package 来源、commit、retrieval date 与本地 artifact identity；
- 建立 source/license/redistribution decision ledger；
- 不提交解压后的 raw data。

## Day 2–3

- 枚举公开 task metadata、raw input、expected output 和 `eval.py`；
- 生成可重算 inventory 与 package manifest；
- 区分 paper claim、code observation 与本地 audit observation。

## Day 4

- 生成 clause-to-`eval.py` coverage draft，并指向准确代码位置；
- 标记 independent oracle 和 checkpoint 是否可行；
- 不把 `eval.py` 存在等同于语义覆盖完整。

## Day 5

- 按 filter/revision、aggregation grain、dedup/latest record、preservation/side effect 寻找候选真实任务；
- 只推荐 provenance、oracle 和 checkpoint 边界均可解释的任务。

## Day 6

- 人工复核 task requirement interpretation、evaluator coverage、step boundary 与许可；
- 对不足项使用 `DATA_INSUFFICIENT`，不强行凑满四个任务。

## Day 7

- 与组内 PhD / 博后对齐 internal assets、current bottleneck、ownership、redistribution 与 4–6 周交付；
- 公开固定版本的只读 audit 不依赖内部 access；
- internal data、mutants、pilot implementation 与 model experiments 仍需该次对齐及人工批准。

---

# 16. 4–6 周路线图

以下路线只在 Phase 1 选定方向后生效。

## Week 1

Research formulation + novelty decision。**已完成。**

## Week 2

ProfiliTable upstream audit：

- package hash；
- task inventory；
- evaluator coverage；
- license/provenance；
- base-task selection。

## Week 3

构建最小 empirical pilot：

- 真实 tasks；
- controlled paired cases；
- direct-transfer baselines；
- no model-training。

## Week 4

运行多个 agents / models，收集 natural failures。

## Week 5

分析：

- 现有 baseline 是否已解决；
- 新信息是否改变诊断或模型排名；
- natural vs controlled failure 是否一致；
- annotation/step boundary 是否稳定。

## Week 6

GO / PIVOT / STOP：

- GO：扩 benchmark / method；
- PIVOT：缩到 intent、diagnosis、evidence acquisition 或 harness；
- STOP：终止 novelty 路线，转内部 evaluator engineering 或其他研究问题。

---

# 17. 如何判断 A 会潜力

## Benchmark-only

需要：

- 新且重要的 evaluation target；
- 规模；
- 多模型；
- 自然 failures；
- 高质量 gold；
- 可靠 evaluator；
- 公开数据；
- 明确改变模型比较或研究结论。

风险：容易被认为只是更大或更细的题库。

## Benchmark + Protocol

再增加：

- 新的评分分解；
- process labels；
- self-detection/localization tracks；
- leakage-safe evaluation。

风险：如果协议只是组合已有指标，novelty 仍弱。

## Benchmark + Method

再增加：

- 一个强方法，例如 state-grounded diagnosis、dependency-aware diagnosis 或 adaptive evidence acquisition；
- 显著优于 direct-transfer baselines；
- held-out generalization。

这是当前更可能达到强论文形状的版本。

## Benchmark + Method + System Integration

再证明：

- 接入 ProfiliTable/DataFlow-Table 后提高真实 task success；
- 降低 semantic false acceptance；
- 减少 debugging/repair cost；
- 控制 latency/token/state-inspection cost。

这是最强但工程和资源要求最高的版本。

不能保证录用，也不能在没有实验前选定 venue。

---

# 18. 当前一句话状态

> **Phase 1 已完成并选定 A（Table-Agent Capability Benchmark）为 primary、C（State-Grounded Evaluator information-gain test）为 fallback；没有 runtime、mutant、模型结果或已成立 novelty。下一步是公开固定版本的 bounded Phase 2 task/evaluator/provenance audit，内部资产、再分发、pilot 与实验仍需组内确认。**

---

# 19. 接手完成检查表

读完后，应能够回答：

- [ ] 上次会议明确说了什么、没有承诺什么；
- [ ] 最初北极星是什么；
- [ ] 为什么 research idea 从 semantic verifier 收缩；
- [ ] 为什么不能单独 claim first error；
- [ ] intermediate table state 的三种角色；
- [ ] A/B/C/D 四条路线分别评谁；
- [ ] 当前 canonical repo、branch，以及为何 commit 必须通过 live Git/GitHub readback 确认；
- [ ] `table-intent-trace` 为什么冻结；
- [ ] 当前完成与未完成事项；
- [ ] Phase 1 四个核心 deliverables 的结论与审查状态；
- [ ] 为什么下一步是 bounded Phase 2 ProfiliTable task/evaluator/provenance audit；
- [ ] 哪些 Phase 2 公开审计现在可做，哪些内部资产/pilot/实验仍需组内批准；
- [ ] 哪些事实仍是 DATA_INSUFFICIENT；
- [ ] GO / PIVOT / STOP 的 kill tests；
- [ ] 哪些文件可以进 Git、哪些不能；
- [ ] 下次组内必须问什么。

如果其中任何一项不能回答，应先回到对应章节，而不是继续实现代码。
