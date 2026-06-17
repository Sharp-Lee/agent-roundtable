# agent-roundtable

[English](README.en.md) · [中文](README.md)

[![Repo](https://img.shields.io/badge/GitHub-agent--roundtable-181717?logo=github&logoColor=white)](https://github.com/Sharp-Lee/agent-roundtable)
![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=white)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Requires tmux](https://img.shields.io/badge/requires-tmux-1BB91F?logo=tmux&logoColor=white)
![Zero deps](https://img.shields.io/badge/deps-stdlib%20only-success)
![Agents](https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-8A2BE2)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **仓库：** https://github.com/Sharp-Lee/agent-roundtable

一个极小的中继，消除**两个交互式 agent CLI 之间的复制粘贴**。

三方在同一个项目上协作：

- **arbiter（仲裁者）** — 你本人。你提出并打磨想法、批准需求（唯一的一道关卡）、并在僵局时仲裁。
  其余时间你不必插手。
- **lead（主导）** — Claude Code。负责规划、起草需求、分配任务、评审。**从不改代码。**
- **impl（实现）** — Codex。先质疑，然后是**唯一**的实现者。

它只做一件事：在两个 CLI pane 之间中继交接消息，让你再也不用在它们之间复制文本。它**不**触碰
agent 的模型循环或原生能力——真正的 Claude Code 和真正的 Codex 客户端在真实终端里原样运行。

## 设计原则

**文件是记忆；pane 是一次性的；一次文件写入就是完成信号。**

- agent 通过*向 mailbox 文件写一条消息*来交接。这次写入是一个明确、无歧义的"我这轮做完了"事件——
  我们从不去抓取终端输出来猜测是否完成（那是重型工具最脆弱的部分）。
- 持久状态（`requirements.md`、`channel.md`、`decisions.md`）存在磁盘上。如果某个 pane 挂了，
  起一个新的、让它重读这些文件即可——无需任何会话恢复机制。

## 工作流

```
Phase 0  Roundtable      想法 -> 尖锐提问 -> 打磨成形的问题            (你 + lead + impl)
Phase 1  Requirements    lead 起草 -> impl 对抗式评审 -> 迭代
                         双方签字  ->  ╔═ Gate A：你批准需求 ═╗
Phase 2  Build loop      逐条需求：分配 -> 质疑 -> impl 实现+提交
                         -> lead 评审 -> 双方一致 -> lead 提交状态 -> 下一条
                         （无关卡；自治运行）
                         僵局 >3 轮 / 真实阻塞 / 触发限流 -> 升级给你
                         全部完成 -> 停机并汇报
```

共享规则（channel、消息格式、提交归属、护栏）在 `prompts/protocol.md`；各角色职责在
`prompts/lead.md` 和 `prompts/impl.md`。三者都会复制进每个项目，作为 agent 读取的操作契约。

## 依赖

- `tmux`、`python3`（3.8+，仅标准库），以及 PATH 上的两个 CLI（`claude`、`codex`）。

## 使用

```bash
# 一次性：把 bin/ 加入 PATH（或直接调用 bin/roundtable）
export PATH="$PWD/bin:$PATH"

cd /path/to/your/dev/project
roundtable init            # 生成 .roundtable/（requirements、channel、decisions、prompts）
roundtable start           # 打开 tmux：左=lead | 右=impl | 窗口 'relay'
```

`rt` 是 `roundtable` 的内置简写（例如 `rt start`、`rt list`、`rt stop`）。

首次启动时，**kickoff 是自动的**：一旦某个 pane 的 CLI 输出看起来稳定下来，`roundtable start`
就会把对应的操作契约（`protocol.md` + `lead.md`/`impl.md`）发给它。你只需把原始想法发给
**左侧（lead）** pane——之后中继就接管了。

自动 kickoff 假设两个 CLI 都已完成认证与配置、并停在正常的主输入提示符上。首次登录、选模型、
信任目录、更新提示等设置界面也可能在视觉上"看起来稳定"；请先处理完这些流程，或用
`AUTO_KICKOFF=0 roundtable start` 然后手动粘贴 kickoff。

如果自动发送没落干净（例如发进了尚未完全就绪的 pane），有两层兜底：

- 等 CLI 完全起来后运行 `roundtable kickoff` **重发**到两个 pane（或 `roundtable kickoff lead|impl`
  只发其中一个）——比手动粘贴更省事；
- 或直接从 start 时落盘的 `.roundtable/kickoff-lead.txt` / `kickoff-impl.txt` **复制粘贴**（在 tmux
  里 `cat` 这两个文件即可，attach 之后也读得到）。

kickoff 同时是**状态自适应**的：它会让每个 pane 重读 `requirements.md`、`channel.md` 和
`decisions.md`，因此中途重启一个项目时会从上次交接处续上（全新项目里这些产物是空模板，于是它
只会等你给想法）。如果你只是从一个仍在运行的会话 detach 了，则**无需 kickoff**——直接
`tmux attach` 回去即可。

设 `AUTO_KICKOFF=0` 可改为手动（每个 pane 起来后各粘一次）：

1. 左侧 pane（Claude Code）：`Read .roundtable/prompts/protocol.md then .roundtable/prompts/lead.md — that is your operating contract. Then read .roundtable/requirements.md, .roundtable/channel.md and .roundtable/decisions.md to restore any prior state. If work is in progress, continue from the last handoff; otherwise acknowledge and wait for my idea.`
2. 右侧 pane（Codex）：`Read .roundtable/prompts/protocol.md then .roundtable/prompts/impl.md — that is your operating contract. Then read .roundtable/requirements.md, .roundtable/channel.md and .roundtable/decisions.md to restore any prior state. If work is in progress, continue from the last handoff; otherwise acknowledge and wait.`
3. 把你的原始想法发给**左侧（lead）** pane。

在 Gate A 批准需求：在 lead pane 中输入
`ARBITER: approved requirements v1`

## 生命周期：停止、重启、恢复

核心思想——**文件是记忆，pane 是一次性的**——意味着你可以随意杀掉并重建 pane；只要磁盘上的产物
还在，就什么都不会丢。

**Detach（保持运行）。** `Ctrl-b d` 让会话在后台继续存活。两个 CLI 保留完整上下文。随时用
`tmux attach -t <session>` 重新连回（用 `roundtable list` 查会话名）——**无需 kickoff**，pane
从未死过。

**停止。** 在项目目录下：

```bash
roundtable stop      # 杀掉本项目的 tmux 会话（lead、impl、relay）
```

这会结束 CLI 进程。`.roundtable/` 下的持久产物原封不动，所以下次启动时工作完全可恢复。

**重启 / 恢复同一个项目。** 直接再启动一次——**什么都别清**：

```bash
roundtable start
```

每个 pane 都会拿到一个全新的 CLI 进程（不记得旧的），所以 auto-kickoff 会重发操作契约，*并*让
两边重读 `requirements.md`、`channel.md`、`decisions.md`。做到一半的项目会从上次交接处续上；
全新项目则只是等你给想法。这是 `stop`、崩溃、机器重启、或 CLI 更新之后的常规路径——产物就是
恢复点，所以你基本永远不用重新粘贴任何东西。

**同时跑多个。** 每个项目有自己的会话（`roundtable-<name>-<hash>`），因此多个 roundtable 可以
共存。`roundtable list` 列出正在运行的那些。

**更新 CLI（Claude Code / Codex）。** 没有特殊操作——`roundtable stop` 然后 `roundtable start`。
新的二进制会在全新 pane 里启动，并通过产物恢复。

**更新本工具自身。** 正在运行的会话在内存里抱着旧的 `relay.py`，所以拉取新代码后必须重启会话才能
生效：

```bash
git -C /path/to/agent-roundtable pull   # 更新工具
roundtable stop && roundtable start      # 在你的项目目录下
```

如果 `prompts/` 有变化，在项目里重新跑 `roundtable init` 以刷新 `.roundtable/prompts/` 下的副本
（init 会刷新 prompts 和 mailbox，但绝不覆盖你的 requirements/channel/decisions）。

**在同一目录里开一个*不同的*、无关的任务（罕见）。** `start` 总是恢复已有产物，所以若要在一个
已经存有"已完成项目"产物的目录里开一轮干净、无关的 roundtable，需自己重置这三个持久文件——
**先备份**，因为它们不会被自动保存：

```bash
mkdir -p .roundtable/_backup && cp .roundtable/{requirements,channel,decisions}.md .roundtable/_backup/
cp templates/{requirements,channel,decisions}.md .roundtable/
```

在正常的"一目录一项目"用法里你永远用不到这个；不同项目请用不同目录。

## 各文件的归属

| 路径（在你的项目里） | 用途 | 提交？ |
|---|---|---|
| `.roundtable/requirements.md` | 商定的规格 + 工作清单 | 是 |
| `.roundtable/channel.md` | 每次交接的持久记录 | 是 |
| `.roundtable/decisions.md` | 已解决的分歧 + 理由 | 是 |
| `.roundtable/prompts/` | agent 读取的角色契约 | 是 |
| `.roundtable/to-lead.md`、`to-impl.md` | 临时 mailbox | 否（已 gitignore） |
| `.roundtable/kickoff-lead.txt`、`kickoff-impl.txt` | start 落盘的 kickoff 文本（手动兜底） | 否（已 gitignore） |

## 环境变量覆盖

| 变量 | 默认 | 含义 |
|---|---|---|
| `CLAUDE_CMD` | `claude` | 启动 lead CLI 的命令 |
| `CODEX_CMD` | `codex` | 启动 impl CLI 的命令 |
| `SESSION` | 按项目 `roundtable-<name>-<hash>` | 覆盖 tmux 会话名 |
| `POLL_SECONDS` | `1.0` | 中继轮询间隔 |
| `AUTO_KICKOFF` | `1` | 一旦 CLI 输出看起来稳定就自动发送操作契约（`0` = 手动粘贴） |
| `KICKOFF_TIMEOUT` | `30` | 在回退到手动前，每个 pane 等待稳定的最大秒数 |

## 已知局限（出于设计）

- 中继通过 `tmux send-keys` 提示*另一个* pane；它假设回合制流程（同一时刻只有一方在行动），
  本工作流保证了这一点。如果你在某个 pane 处于回合中时往里打字，按键可能交错——请让每一轮先结束。
- 它不会跨完整重启自动恢复模型的内部对话。恢复靠的是重读磁盘上的产物（这比脆弱的会话恢复更稳健）。
- 自动 kickoff 把 `tmux capture-pane` 的输出稳定性当作启动便利，而非协议完成信号。带动画的空闲
  界面可能超时并回退到手动 kickoff；静态的首次设置界面可能需要 `AUTO_KICKOFF=0`。
