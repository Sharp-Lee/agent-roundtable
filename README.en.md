# agent-roundtable

[English](README.en.md) · [中文](README.md)

[![Repo](https://img.shields.io/badge/GitHub-agent--roundtable-181717?logo=github&logoColor=white)](https://github.com/Sharp-Lee/agent-roundtable)
![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=white)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Requires tmux](https://img.shields.io/badge/requires-tmux-1BB91F?logo=tmux&logoColor=white)
![Zero deps](https://img.shields.io/badge/deps-stdlib%20only-success)
![Agents](https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-8A2BE2)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **Repo:** https://github.com/Sharp-Lee/agent-roundtable

A tiny relay that removes the **copy-paste between two interactive agent CLIs**.

Three parties collaborate on one project:

- **arbiter** — you. You shape the idea, approve the three gates (direction, final form, detailed
  requirements), and arbitrate deadlocks. Otherwise you stay out of the way.
- **玄** — Claude Code. Holds the document pen: synthesizes direction, designs final form, expands
  requirements, assigns tasks, and reviews. **Never edits code.**
- **素** — Codex. Challenges first throughout the process; once the build loop starts, is the
  **only** implementer.

The compatibility layer still uses `lead` / `impl` as wire labels: mailbox file names, `FROM:`
values, environment variables, and legacy CLI aliases keep those tokens; user-facing roles,
operating contracts, and pane titles use **玄/素**.

It does exactly one thing: relays handoff messages between the two CLI panes so you never copy
text between them again. It does **not** touch the agents' model loop or native abilities — the
real Claude Code and real Codex clients run unchanged in real terminals.

## Design principle

**Files are the memory; panes are disposable; a file-write is the completion signal.**

- Agents hand off by *writing a message to a mailbox file*. That write is an explicit,
  unambiguous "my turn is done" event — we never scrape terminal output to guess completion
  (the fragile part of heavier tools).
- Durable design artifacts live under `docs/design/roundtable/`; runtime handoff state lives under
  `.roundtable/`. If a pane dies, start a fresh one and tell it to re-read those files — no
  session-resume machinery needed.

## The workflow

```
Phase 0  Idea roundtable       raw idea -> three-party shaping -> direction statement  (you + 玄 + 素)
                               ╔═ Gate 0: direction lock ═╗
Phase 1  Final-form design     玄 drafts architecture/flow -> 素 adversarial review
                               -> one-shot panel -> ╔═ Gate 1: final-form confirmation ═╗
Phase 2  Detailed requirements expand flow nodes into atomic requirements -> 素 challenges / 玄+素 converge
                               -> arbiter confirms WHY/WHAT -> pending=0
                               -> ╔═ Gate 2: detailed requirements approval ═╗
Phase 3  Build loop            per requirement: assign -> challenge -> 素 implements+commits
                               -> 玄 reviews -> both agree -> 玄 commits status -> next
                         deadlock >3 rounds / real blocker / rate limit -> escalate to you
                         all items done -> halt and report
```

The panel is not a resident agent: it is mandatory in Phase 1, optional in Phase 2 for risky or
complex requirements, one-shot, internal to the document holder's tooling, and adds no relay route
or tmux pane.

The shared rules (channel, message format, commit ownership, guardrails) live in
`prompts/protocol.md`; the role-specific duties are in `prompts/xuan.md` and `prompts/su.md`.
All three are copied into each project so the agents read them as their operating contract.

## Requirements

- `tmux`, `python3` (3.8+, stdlib only), and the two CLIs on PATH (`claude`, `codex`).

## Usage

```bash
# one-time: put bin/ on your PATH (or call bin/roundtable directly)
export PATH="$PWD/bin:$PATH"

cd /path/to/your/dev/project
roundtable init            # scaffolds docs/design/roundtable/ + .roundtable/ runtime state
roundtable start           # opens tmux workbench: top 玄|素, bottom command|relay
```

`rt` is a built-in shorthand for `roundtable` (e.g. `rt start`, `rt list`, `rt stop`).

| Command | Purpose |
|---|---|
| `roundtable new <name>` | create a sibling git worktree for a new idea and initialize roundtable there |
| `roundtable init [name\|dir]` | initialize the current directory, an existing named worktree, or a directory path |
| `roundtable start [name\|dir]` | start the 玄/素/command/relay workbench for the current directory, named worktree, or directory path |
| `roundtable kickoff [name] [xuan\|su]` | re-send kickoff for the current or named worktree; `lead\|impl` are legacy wire aliases only |
| `roundtable stop [name\|dir]` | stop the tmux session for the current directory, named worktree, or directory path |
| `roundtable list` | list running roundtable sessions |

## Workbench, Mouse, And Popups

By default, `roundtable start` creates a 4-pane workbench:

```text
top:    玄 (Claude Code) | 素 (Codex)
bottom: command shell      | relay watcher
```

The bottom-left pane is a normal shell in the project directory. The bottom-right pane is the visible relay
watcher. `RT_LAYOUT=classic` restores the old layout: 玄 on the left, 素 on the right, and a separate
`relay` window. If the terminal is below roughly `100x30`, start warns but proceeds best-effort.

**tmux mouse is off by default** (`RT_MOUSE=0`), so text selection and copy behave exactly as usual. When you
want the wheel to scroll pane history, click to select panes, or drag to resize, **press `prefix+v` to turn it
on** (press again to turn it off). To start with the mouse already on, use `RT_MOUSE=1 roundtable start`; to
change the toggle key, set `RT_MOUSE_KEY=<key>`.

**Why off-by-default + a toggle:** with the mouse on, the wheel drops the pane into tmux **copy-mode**, where
keys become copy-mode commands instead of input — e.g. `f` pops up `(jump to forward)` and typing seems to do
nothing. Off-by-default avoids stumbling into that; when you do want to scroll, `prefix+v` on, then **press `q`
or `Esc` to leave copy-mode**, and `prefix+v` off again if you like. The `prefix+g` tips popup carries this
reminder too.

roundtable installs a few global, context-aware prefix keys (the popup keys require the current tmux to support
`display-popup`):

- `prefix+g`: tips/cheatsheet popup with commands, the actual configured keys, and recovery reminders.
- `prefix+e`: project file-view popup; uses the first available of `yazi`, `lf`, `ranger`, or `tree`, else
  `ls -R` (paged with `less` when present, otherwise printed with Enter-to-close).
- `prefix+v`: toggle tmux mouse on/off (does not require `display-popup`).

The bindings are tmux-server-global, but they read the current session's `@roundtable_dir` and
`@roundtable_keys` at invocation time, so multiple project sessions can share the same keys. If the target
key is already bound to a non-roundtable command, roundtable preserves it and warns; set `RT_TIPS_KEY` /
`RT_FILE_KEY` / `RT_MOUSE_KEY` to choose different keys, or `RT_KEYS=0` to make these keys a hard no-op for
that session and install no new bindings. `roundtable stop` never unbinds these global keys because another active roundtable
session may still need them. The file popup does not implement a picker or file actions; external file
managers run with your own config and may allow navigation or mutation.

On first start, the **kickoff is automatic**: once each pane's CLI output looks settled,
`roundtable start` sends it the matching operating contract (`protocol.md` + `xuan.md`/`su.md`).
You only need to give your raw idea to the **left (玄)** pane — the relay takes over from there.

Automatic kickoff assumes both CLIs are already authenticated and configured, and that they land on
their normal main input prompt. First-run login, model-selection, trust-folder, update notices, or
other setup prompts can also look visually "settled"; complete those flows first, or run
`AUTO_KICKOFF=0 roundtable start` and paste the kickoff manually.

If auto-send mis-fires (e.g. it lands in a pane that wasn't fully ready), there are two fallbacks:

- once the CLI is fully up, run `roundtable kickoff` to **re-send** to both panes (or
  `roundtable kickoff xuan|su` for just one; `lead|impl` remain legacy wire aliases) — easier
  than re-pasting;
- or **copy/paste** from the files `start` writes: `.roundtable/kickoff-lead.txt` /
  `kickoff-impl.txt` (`cat` them from inside tmux — readable even after you've attached).

The kickoff is also **state-aware**: it tells each pane to re-read `.roundtable/_idea.md`,
`docs/design/roundtable/{architecture,flow,requirements,decisions}.md`, `.roundtable/channel.md`,
and its inbox, so re-starting a project mid-flight resumes from the last handoff (on a fresh
project those artifacts are empty templates, so it just waits for your idea). If you only detached
from a still-running session, no kickoff is needed — just `tmux attach` back.

Set `AUTO_KICKOFF=0` to do it manually instead (paste these once each pane is up):

1. Left pane (Claude Code): run `roundtable kickoff xuan`, or paste `.roundtable/kickoff-lead.txt`.
2. Right pane (Codex): run `roundtable kickoff su`, or paste `.roundtable/kickoff-impl.txt`.
3. Give your raw idea to the **left (玄)** pane.

Approve or reject Gate 0/1/2 in the **玄** pane; 玄 records the verdict in
`docs/design/roundtable/decisions.md`.

## Lifecycle: stop, restart, resume

The guiding idea — **files are the memory, panes are disposable** — means you can kill and
recreate panes freely; nothing is lost as long as the on-disk artifacts survive.

**Detach (keep it running).** `Ctrl-b d` leaves the session alive in the background. The two CLIs
keep their full context. Reconnect any time with `tmux attach -t <session>` (find the name via
`roundtable list`) — **no kickoff needed**, the panes never died.

**Stop.** From the project dir:

```bash
roundtable stop      # kills this project's tmux session (玄, 素, command, relay)
```

This ends the CLI processes. The design artifacts under `docs/design/roundtable/` and the runtime
handoff state under `.roundtable/` are untouched, so the work is fully recoverable on the next
start.

**Relay pane killed.** If the bottom-right relay pane in the workbench is manually killed, 玄/素 can still
look healthy, but handoffs will no longer be relayed. Recovery is still:

```bash
roundtable stop && roundtable start
```

**Restart / resume the same project.** Just start again — **do not clean anything**:

```bash
roundtable start
```

Each pane gets a brand-new CLI process (no memory of the old one), so the auto-kickoff re-sends the
operating contract *and* tells each side to re-read the docs design artifacts,
`.roundtable/channel.md`, and its inbox. A project that was mid-build resumes from the last
handoff; a fresh project just waits for your idea. This is the normal path after a `stop`, a crash,
a machine reboot, or a CLI update — the artifacts are the resume point, so you essentially never
re-paste anything.

**Run several at once.** Each project gets its own session (`roundtable-<name>-<hash>`), so
multiple roundtables coexist. `roundtable list` shows the running ones.

**Update the CLIs (Claude Code / Codex).** Nothing special — `roundtable stop` then
`roundtable start`. The new binaries launch in fresh panes and resume via the artifacts.

**Update this tool itself.** A running session holds the old `relay.py` in memory, so after
pulling new code you must restart the session to pick it up:

```bash
git -C /path/to/agent-roundtable pull   # update the tool
roundtable stop && roundtable start      # in your project dir
```

If `prompts/` changed, re-run `roundtable init` in the project to refresh the copies under
`.roundtable/prompts/` (init refreshes prompts and mailboxes but never clobbers your
existing docs design artifacts or channel).

**Start a new idea in its own worktree.** Each idea should have its own git worktree instead of
manually clearing old artifacts in the same directory:

```bash
roundtable new my-idea
roundtable start my-idea
```

By default, this creates branch `codex/my-idea` from the current `HEAD` and a sibling worktree such
as `../agent-roundtable.my-idea`. Code changes, Roundtable memory, and the tmux session for that
idea all live in that worktree.

`roundtable start` without a name still resumes the current directory's state.

## What lives where

| Path (in your project) | Purpose | Commit? |
|---|---|---|
| `docs/design/roundtable/architecture.md` | Gate 1 locked overall architecture | yes |
| `docs/design/roundtable/flow.md` | Gate 1 locked runtime business flow | yes |
| `docs/design/roundtable/requirements.md` | Gate 2 locked detailed requirements + work list | yes |
| `docs/design/roundtable/decisions.md` | gate verdicts, resolved disagreements + rationale | yes |
| `.roundtable/_idea.md` | Gate 0 direction statement | no (runtime state) |
| `.roundtable/channel.md` | relay transcript of every handoff | no (runtime state) |
| `.roundtable/prompts/` | copied role contracts the agents read | no (runtime state) |
| `.roundtable/to-lead.md`, `to-impl.md` | wire-named transient mailboxes | no (gitignored) |
| `.roundtable/kickoff-lead.txt`, `kickoff-impl.txt` | wire-named kickoff text saved at start (manual fallback) | no (gitignored) |

## Env overrides

| Var | Default | Meaning |
|---|---|---|
| `CLAUDE_CMD` | `claude` | command to start the 玄 CLI |
| `CODEX_CMD` | `codex` | command to start the 素 CLI |
| `SESSION` | per-project `roundtable-<name>-<hash>` | override the tmux session name |
| `RT_LAYOUT` | `workbench` | `workbench` = 4-pane layout; `classic` = old 2 panes + relay window |
| `RT_MOUSE` | `0` | `1` = start with tmux mouse on; off by default, toggle at runtime with `prefix+v` |
| `RT_KEYS` | `1` | install/use roundtable keys; `0` = these keys no-op for this session and install no new keys |
| `RT_TIPS_KEY` | `g` | tmux prefix key for the tips popup |
| `RT_FILE_KEY` | `e` | tmux prefix key for the project file-view popup |
| `RT_MOUSE_KEY` | `v` | tmux prefix key that toggles tmux mouse on/off |
| `POLL_SECONDS` | `1.0` | relay poll interval |
| `AUTO_KICKOFF` | `1` | auto-send each pane its operating contract once its CLI output looks settled (`0` = manual paste) |
| `KICKOFF_TIMEOUT` | `30` | max seconds to wait for a pane to settle before falling back to manual |

## Limitations (known, by design)

- The relay nudges the *other* pane via `tmux send-keys`; it assumes a turn-based flow (only one
  side acting at a time), which this workflow guarantees. If you type into a pane while it is
  mid-turn, keystrokes can interleave — let each turn finish.
- It does not auto-resume the models' internal conversation across a full restart. Recovery is by
  re-reading the on-disk artifacts (which is more robust than fragile session resume).
- Automatic kickoff uses `tmux capture-pane` output stability as a startup convenience, not a
  protocol completion signal. Animated idle screens may time out and fall back to manual kickoff;
  static first-run setup prompts may require `AUTO_KICKOFF=0`.
