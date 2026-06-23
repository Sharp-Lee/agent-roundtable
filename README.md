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

- **arbiter（仲裁者）** — 你本人。你提出并打磨想法，批准三道关卡（方向、最终形态、详细需求），
  并在僵局时仲裁。其余时间你不必插手。
- **玄** — Claude Code。持文档笔：综合方向、设计最终形态、展开需求、分配任务、评审。**从不改代码。**
- **素** — Codex。全程先质疑；进入构建循环后是**唯一**的实现者。

兼容层仍保留 `lead` / `impl` 作为 wire 标签：mailbox 文件名、`FROM:` 值、环境变量和 legacy CLI
别名仍用它们；用户可见角色、操作契约和 pane 标题使用 **玄/素**。

它只做一件事：在两个 CLI pane 之间中继交接消息，让你再也不用在它们之间复制文本。它**不**触碰
agent 的模型循环或原生能力——真正的 Claude Code 和真正的 Codex 客户端在真实终端里原样运行。

## 设计原则

**文件是记忆；pane 是一次性的；一次文件写入就是完成信号。**

- agent 通过*向 mailbox 文件写一条消息*来交接。这次写入是一个明确、无歧义的"我这轮做完了"事件——
  我们从不去抓取终端输出来猜测是否完成（那是重型工具最脆弱的部分）。
- 持久设计产物存在 `docs/design/roundtable/`；运行时交接态存在 `.roundtable/`。如果某个 pane
  挂了，起一个新的、让它重读这些文件即可——无需任何会话恢复机制。

## 工作流

```
Phase 0  想法圆桌        原始想法 -> 三方打磨 -> 方向陈述              (你 + 玄 + 素)
                         ╔═ Gate 0：方向锁定 ═╗
Phase 1  最终形态设计    玄起草 architecture/flow -> 素对抗式评审
                         -> panel 一次性评审 -> ╔═ Gate 1：最终形态确认 ═╗
Phase 2  详细需求        从 flow 节点展开原子需求 -> 素质疑/玄素收敛
                         -> 你确认 WHY/WHAT -> pending 清零
                         -> ╔═ Gate 2：详细需求批准 ═╗
Phase 3  构建循环        逐条需求：分配 -> 质疑 -> 素实现+提交
                         -> 玄评审 -> 双方一致 -> 玄提交状态 -> 下一条
                         僵局 >3 轮 / 真实阻塞 / 触发限流 -> 升级给你
                         全部完成 -> 停机并汇报
```

panel 不是常驻 agent：Phase 1 强制、Phase 2 按高风险/复杂度触发；它是一次性内部评审，不碰 relay
路由，也不增加 tmux pane。

共享规则（channel、消息格式、提交归属、护栏）在 `prompts/protocol.md`；各角色职责在
`prompts/xuan.md` 和 `prompts/su.md`。三者都会复制进每个项目，作为 agent 读取的操作契约。

## 依赖

- `tmux`、`python3`（3.8+，仅标准库），以及 PATH 上的两个 CLI（`claude`、`codex`）。

## 使用

```bash
# 一次性：把 bin/ 加入 PATH（或直接调用 bin/roundtable）
export PATH="$PWD/bin:$PATH"

cd /path/to/your/dev/project
roundtable init            # 生成 docs/design/roundtable/ + .roundtable/ 运行时态
roundtable start           # 打开 tmux workbench：上 玄|素，下 command|relay
```

`rt` 是 `roundtable` 的内置简写（例如 `rt start`、`rt list`、`rt stop`）。

| 命令 | 用途 |
|---|---|
| `roundtable init [dir]` | 生成 docs 设计产物和 `.roundtable/` 运行时态 |
| `roundtable start [dir]` | 启动 玄/素/command/relay workbench |
| `roundtable kickoff [xuan|su]` | 重发 kickoff；`lead|impl` 仅作 legacy wire 别名 |
| `roundtable stop [dir]` | 停止当前项目的 tmux 会话 |
| `roundtable list` | 列出正在运行的 roundtable 会话 |

## Workbench、鼠标与弹窗

默认的 `roundtable start` 会创建一个 4-pane workbench：

```text
上排：玄（Claude Code） | 素（Codex）
下排：command shell       | relay watcher
```

左下角是项目目录里的普通 shell，右下角是可见的 relay watcher。`RT_LAYOUT=classic` 会恢复旧布局：
左侧玄、右侧素，另开一个 `relay` 窗口。终端小于约 `100x30` 时会警告但仍尽量启动。

**tmux mouse 默认关闭**（`RT_MOUSE=0`），这样拖选/复制和平时一模一样。需要滚轮滚 pane 历史、
点击选 pane、拖边框调大小时，**按 `prefix+v` 临时开启**（再按一次关闭）。想一启动就开着鼠标，用
`RT_MOUSE=1 roundtable start`；想改开关键，用 `RT_MOUSE_KEY=<key>`。

**为什么默认关 + 用快捷键开**：鼠标开着时，滚轮一滚就把 pane 切进 tmux **copy-mode**，此时键盘变成
copy-mode 命令而不是输入——比如按 `f` 会在状态栏弹出 `(jump to forward)`，打字也"没反应"。默认关掉
就不会误入；真要滚历史时 `prefix+v` 开、看完 **按 `q` 或 `Esc` 退出 copy-mode**、需要的话再 `prefix+v`
关。`prefix+g` 的 tips 弹窗里也有这条提醒。

roundtable 会安装几组全局、上下文感知的 prefix 快捷键（弹窗键需要当前 tmux 支持 `display-popup`）：

- `prefix+g`：tips/cheatsheet 弹窗，显示命令、当前快捷键和常用恢复提醒。
- `prefix+e`：项目文件视图弹窗；优先使用 `yazi`、`lf`、`ranger`、`tree`，否则 `ls -R`（有 `less`
  就分页，没有就打印后按 Enter 关闭）。
- `prefix+v`：开关 tmux mouse（不依赖 `display-popup`）。

快捷键是 tmux server 全局的，但执行时读取当前 session 的 `@roundtable_dir` 和 `@roundtable_keys`，
所以多个项目会话可以共用同一组键。若目标键已被非 roundtable 绑定占用，roundtable 会保留它并警告；
用 `RT_TIPS_KEY` / `RT_FILE_KEY` / `RT_MOUSE_KEY` 改键，或用 `RT_KEYS=0` 让本 session 的这些键硬 no-op 且不安装新键。
`roundtable stop` 不会解绑这些全局键，以免破坏另一个仍在运行的 roundtable session。文件弹窗本身
不实现选择器或文件操作；外部文件管理器按你的个人配置运行，可能允许导航或修改。

首次启动时，**kickoff 是自动的**：一旦某个 pane 的 CLI 输出看起来稳定下来，`roundtable start`
就会把对应的操作契约（`protocol.md` + `xuan.md`/`su.md`）发给它。你只需把原始想法发给
**左侧（玄）** pane——之后中继就接管了。

自动 kickoff 假设两个 CLI 都已完成认证与配置、并停在正常的主输入提示符上。首次登录、选模型、
信任目录、更新提示等设置界面也可能在视觉上"看起来稳定"；请先处理完这些流程，或用
`AUTO_KICKOFF=0 roundtable start` 然后手动粘贴 kickoff。

如果自动发送没落干净（例如发进了尚未完全就绪的 pane），有两层兜底：

- 等 CLI 完全起来后运行 `roundtable kickoff` **重发**到两个 pane（或 `roundtable kickoff xuan|su`
  只发其中一个；`lead|impl` 仍是 legacy wire 别名）——比手动粘贴更省事；
- 或直接从 start 时落盘的 `.roundtable/kickoff-lead.txt` / `kickoff-impl.txt` **复制粘贴**（在 tmux
  里 `cat` 这两个文件即可，attach 之后也读得到）。

kickoff 同时是**状态自适应**的：它会让每个 pane 重读 `.roundtable/_idea.md`、
`docs/design/roundtable/{architecture,flow,requirements,decisions}.md`、`.roundtable/channel.md`
和自己的 inbox，因此中途重启一个项目时会从上次交接处续上（全新项目里这些产物是空模板，于是它
只会等你给想法）。如果你只是从一个仍在运行的会话 detach 了，则**无需 kickoff**——直接
`tmux attach` 回去即可。

设 `AUTO_KICKOFF=0` 可改为手动（每个 pane 起来后各粘一次）：

1. 左侧 pane（Claude Code）：运行 `roundtable kickoff xuan`，或粘贴 `.roundtable/kickoff-lead.txt`。
2. 右侧 pane（Codex）：运行 `roundtable kickoff su`，或粘贴 `.roundtable/kickoff-impl.txt`。
3. 把你的原始想法发给**左侧（玄）** pane。

Gate 0/1/2 的批准或打回都在**玄** pane 中输入；玄会把裁决记录到
`docs/design/roundtable/decisions.md`。

## 生命周期：停止、重启、恢复

核心思想——**文件是记忆，pane 是一次性的**——意味着你可以随意杀掉并重建 pane；只要磁盘上的产物
还在，就什么都不会丢。

**Detach（保持运行）。** `Ctrl-b d` 让会话在后台继续存活。两个 CLI 保留完整上下文。随时用
`tmux attach -t <session>` 重新连回（用 `roundtable list` 查会话名）——**无需 kickoff**，pane
从未死过。

**停止。** 在项目目录下：

```bash
roundtable stop      # 杀掉本项目的 tmux 会话（玄、素、command、relay）
```

这会结束 CLI 进程。`docs/design/roundtable/` 下的设计产物和 `.roundtable/` 下的运行时交接态
原封不动，所以下次启动时工作完全可恢复。

**relay pane 被杀掉。** workbench 里的右下角 relay pane 如果被手动 `kill-pane`，玄/素看起来仍在，
但 handoff 不会再被中继。恢复方式仍然是：

```bash
roundtable stop && roundtable start
```

**重启 / 恢复同一个项目。** 直接再启动一次——**什么都别清**：

```bash
roundtable start
```

每个 pane 都会拿到一个全新的 CLI 进程（不记得旧的），所以 auto-kickoff 会重发操作契约，*并*让
两边重读 docs 设计产物、`.roundtable/channel.md` 和自己的 inbox。做到一半的项目会从上次交接处续上；
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
（init 会刷新 prompts 和 mailbox，但绝不覆盖已有的 docs 设计产物或 channel）。

**在同一目录里开一个*不同的*、无关的任务（罕见）。** `start` 总是恢复已有产物，所以若要在一个
已经存有"已完成项目"产物的目录里开一轮干净、无关的 roundtable，需自己重置设计产物和运行时态——
**先备份**，因为它们不会被自动保存：

```bash
stamp=$(date +%Y%m%d%H%M%S)
mkdir -p docs/design/_backup .roundtable-backup
cp -R docs/design/roundtable docs/design/_backup/roundtable.$stamp
cp -R .roundtable .roundtable-backup/roundtable.$stamp
rm -rf docs/design/roundtable .roundtable
roundtable init
```

在正常的"一目录一项目"用法里你永远用不到这个；不同项目请用不同目录。

## 各文件的归属

| 路径（在你的项目里） | 用途 | 提交？ |
|---|---|---|
| `docs/design/roundtable/architecture.md` | Gate 1 锁定的整体架构 | 是 |
| `docs/design/roundtable/flow.md` | Gate 1 锁定的运行时业务流程 | 是 |
| `docs/design/roundtable/requirements.md` | Gate 2 锁定的详细需求 + 工作清单 | 是 |
| `docs/design/roundtable/decisions.md` | gate 裁决、已解决的分歧 + 理由 | 是 |
| `.roundtable/_idea.md` | Gate 0 方向陈述 | 否（运行时态） |
| `.roundtable/channel.md` | 每次交接的 relay transcript | 否（运行时态） |
| `.roundtable/prompts/` | agent 读取的角色契约副本 | 否（运行时态） |
| `.roundtable/to-lead.md`、`to-impl.md` | wire 命名的临时 mailbox | 否（已 gitignore） |
| `.roundtable/kickoff-lead.txt`、`kickoff-impl.txt` | wire 命名的 kickoff 文本（手动兜底） | 否（已 gitignore） |

## 环境变量覆盖

| 变量 | 默认 | 含义 |
|---|---|---|
| `CLAUDE_CMD` | `claude` | 启动玄 CLI 的命令 |
| `CODEX_CMD` | `codex` | 启动素 CLI 的命令 |
| `SESSION` | 按项目 `roundtable-<name>-<hash>` | 覆盖 tmux 会话名 |
| `RT_LAYOUT` | `workbench` | `workbench` = 4-pane 布局；`classic` = 旧 2-pane + relay 窗口 |
| `RT_MOUSE` | `0` | `1` = 启动即开 tmux mouse；默认关闭，运行中用 `prefix+v` 临时开关 |
| `RT_KEYS` | `1` | 安装/使用 roundtable 快捷键；`0` = 本 session 这些键 no-op，且不安装新键 |
| `RT_TIPS_KEY` | `g` | tips 弹窗的 tmux prefix 快捷键 |
| `RT_FILE_KEY` | `e` | 项目文件视图弹窗的 tmux prefix 快捷键 |
| `RT_MOUSE_KEY` | `v` | 开关 tmux mouse 的 tmux prefix 快捷键 |
| `POLL_SECONDS` | `1.0` | 中继轮询间隔 |
| `AUTO_KICKOFF` | `1` | 一旦 CLI 输出看起来稳定就自动发送操作契约（`0` = 手动粘贴） |
| `KICKOFF_TIMEOUT` | `30` | 在回退到手动前，每个 pane 等待稳定的最大秒数 |

## 已知局限（出于设计）

- 中继通过 `tmux send-keys` 提示*另一个* pane；它假设回合制流程（同一时刻只有一方在行动），
  本工作流保证了这一点。如果你在某个 pane 处于回合中时往里打字，按键可能交错——请让每一轮先结束。
- 它不会跨完整重启自动恢复模型的内部对话。恢复靠的是重读磁盘上的产物（这比脆弱的会话恢复更稳健）。
- 自动 kickoff 把 `tmux capture-pane` 的输出稳定性当作启动便利，而非协议完成信号。带动画的空闲
  界面可能超时并回退到手动 kickoff；静态的首次设置界面可能需要 `AUTO_KICKOFF=0`。
