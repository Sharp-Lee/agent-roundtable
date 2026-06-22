# Requirements — roundtable「前置设计流程」(玄/素 v2)

> Phase 0/1 已在 dry-run roundtable 走完;此清单即 Gate A 已批准的 Phase 2 工作清单。
> **完整 WHY/WHAT/HOW/验收** 见 [`front-end-pipeline-requirements.md`](../front-end-pipeline-requirements.md)(48 条原子需求)
> 与最终形态 [`front-end-pipeline-final-form.md`](../front-end-pipeline-final-form.md)。
> 本文件已 copy-forward 到 `docs/design/roundtable/requirements.md`;后续以 docs/ 为权威,`.roundtable/` 仅保留 legacy mirror。

**Version:** v1
**Sign-off:** lead: ☑  impl: ☑   |   **Arbiter approval (Gate A):** ☑（dry-run 2026-06-22）

## 1. Problem & goal
为 roundtable 增加一条**前置设计流水线**:想法圆桌 → 最终形态设计 → 详细需求 → 构建循环,
人类在三处把关(方向锁定 / 最终形态确认 / 详细需求批准),其余自治。核心:在 idea 与构建之间,
产出**整体架构文档**与**运行时业务流程文档(含 Mermaid 图)**,再把每个业务步骤展开成清晰、可追溯的原子需求。

## 2. Scope
- **In scope:** 改 `prompts/protocol.md`、角色契约(改名 玄/素)、`templates/`(新增 architecture/flow、升级 requirements)、README 中/英、kickoff;落点 B(设计产物入 tracked `docs/`)。
- **Out of scope(非目标):** 不改 `bin/relay.py`(阶段无关);不重做已验证的构建循环;不引入第三方依赖;不增加常驻 agent(多视角靠一次性 panel)。

## 3. Requirements (the Phase 2 work list)
> 每个工作项对应一组原子需求(R-编号);构建时 commit 回指对应 R-编号。Status ∈ todo / doing / done。

| # | Requirement(覆盖的 R-编号) | Acceptance criteria | Depends on | Status |
|---|------------------------------|---------------------|------------|--------|
| G1 | Phase 0 想法圆桌契约（R-P0-1..4）| 三方打磨;方向落 `_idea.md`;方向陈述含 5 要素(含 scope 非目标);可触发关卡 0 | — | done |
| G2 | 关卡 0 方向锁定（R-G0-1..3）| 自包含呈现;通过/打回落 `decisions.md`;通过即"🔒方向",改方向须回关卡 0 | G1 | done |
| G3 | Phase 1 最终形态设计（R-P1-1..6）| 玄持笔产 `architecture.md`+`flow.md`(Mermaid,节点=业务步骤);在冻结边界内;玄×素对抗回合;收敛信号 | G2,G9 | done |
| G4 | 专项评审 panel 机制（R-P4-1..4）| ②强制/③按需触发;一次性、不碰 relay、不增 pane;lens 按需选;发现回流归并 | — | done |
| G5 | 关卡 1 最终形态确认（R-G1-1..3）| 只读可判;通过/打回(可退关卡 0)落 `decisions.md`;通过即"🔒最终形态" | G3,G4 | done |
| G6 | Phase 2 详细需求（R-P2-1..6）| 拆解源=flow 节点(n:1);7 字段完备;按字段分工;覆盖 100%(pending 门);按组推进 | G5 | done |
| G7 | 关卡 2 详细需求批准（R-G2-1..3）| pending=0 前提;批准/精确打回落 `decisions.md`;批准即"🔒基线" | G6 | done |
| G8 | Phase 3 构建循环（R-P3-1..4）| 沿用现循环+重编号;输入=已锁基线(commit 回指 R-编号);玄/素改名;自治/升级/完成 | G7 | done |
| G9 | 产物与文件模型（R-F-1..5）| 新增 `templates/architecture.md`、`flow.md`;升级 `templates/requirements.md`;沿用 decisions/channel;落点 B | — | done |
| G10 | 重启恢复（R-RR-1..3）| 从文件重建阶段位置;🔒 为权威;pending/状态驱动续做 | G9 | done |
| G11 | 角色契约改名 玄/素（R-RC-1..4）| `lead.md→xuan.md`、`impl.md→su.md`;阶段职责表;protocol 增补共享规则;challenge-first 全程 | G1-G10 | done |
| G12 | 对外更新 README/kickoff（R-EX-1..3）| README 中/英同步四阶段三关卡;kickoff 引导新流程;术语一致性自检 | G11 | done |

## 4. Constraints & assumptions
- 零第三方依赖(tmux + python3 stdlib);引擎(relay + orchestrator)保持极小、几乎不改。
- "文件即记忆":设计产物入 tracked `docs/`,交接态(channel/_idea/mailbox)留 `.roundtable/`。
- 命名 玄=Claude(原 lead)/ 素=Codex(原 impl),仅为标签、不编码角色。

## 5. Open questions
（无;Gate A 已通过。构建中若发现最终形态/需求硬伤,按 R-G1-3 / R-G2-3 显式升级回对应关卡。）

## 6. 构建排序指引(供自治循环规划用,非强制)
> 目的:让 lead+impl 的 `/ce-plan` 自己排好顺序,**不必由 arbiter 供给**。impl 应**对抗、修正**本节,而非照抄。

- **自治授权:** Gate A 已批准 = 已授权自治运行。**不必为"先开哪项 / 派活给 impl"请示 arbiter**;仅在真实僵局(>3 轮)/ 真实阻塞 / 触发限流时升级。
- **无依赖、可先开:** G9、G1、G4(其余均有 Depends on)。
- **物理 sink 警告(关键):** 12 组是按"关注点"切的,但写入**高度集中在 `prompts/protocol.md` + 两份角色契约**。R-RC-3(G11)明确就是"把四阶段 / 三关卡 / panel / 锁 / 落点 / 重启**写进 protocol.md**"——即 **G1–G10 多为"定规则",G11 才是"落笔到 protocol.md"**。逐组各改一遍 protocol.md 再到 G11 重写,会反复打架。
- **建议顺序:**
  1. **G9** —— 隔离的新模板(architecture / flow + requirements 升级),打底、解开 G3 依赖。
  2. **protocol.md + 角色契约 玄/素 整体一次写成** —— 吸收 G1/G2/G4/G5/G7/G10 的规则 + G11 的改名与阶段表,而非对同一文件改 11 次。
  3. **G12** —— README 中/英 + kickoff + 一致性自检,收尾。
