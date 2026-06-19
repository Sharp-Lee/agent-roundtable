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

- **arbiter** — you. You shape the idea, approve the requirements (one gate), and arbitrate
  deadlocks. Otherwise you stay out of the way.
- **lead** — Claude Code. Plans, drafts requirements, assigns tasks, reviews. **Never edits code.**
- **impl** — Codex. Challenges first, then is the **only** implementer.

It does exactly one thing: relays handoff messages between the two CLI panes so you never copy
text between them again. It does **not** touch the agents' model loop or native abilities — the
real Claude Code and real Codex clients run unchanged in real terminals.

## Design principle

**Files are the memory; panes are disposable; a file-write is the completion signal.**

- Agents hand off by *writing a message to a mailbox file*. That write is an explicit,
  unambiguous "my turn is done" event — we never scrape terminal output to guess completion
  (the fragile part of heavier tools).
- The durable state (`requirements.md`, `channel.md`, `decisions.md`) lives on disk. If a pane
  dies, start a fresh one and tell it to re-read those files — no session-resume machinery needed.

## The workflow

```
Phase 0  Roundtable      idea -> sharp questions -> shaped problem        (you + lead + impl)
Phase 1  Requirements    lead drafts -> impl reviews adversarially -> iterate
                         both sign off  ->  ╔═ Gate A: you approve requirements ═╗
Phase 2  Build loop      per requirement: assign -> challenge -> impl implements+commits
                         -> lead reviews -> both agree -> lead commits status -> next
                         (no gate; autonomous)
                         deadlock >3 rounds / real blocker / rate limit -> escalate to you
                         all items done -> halt and report
```

The shared rules (channel, message format, commit ownership, guardrails) live in
`prompts/protocol.md`; the role-specific duties are in `prompts/lead.md` and `prompts/impl.md`.
All three are copied into each project so the agents read them as their operating contract.

## Requirements

- `tmux`, `python3` (3.8+, stdlib only), and the two CLIs on PATH (`claude`, `codex`).

## Usage

```bash
# one-time: put bin/ on your PATH (or call bin/roundtable directly)
export PATH="$PWD/bin:$PATH"

cd /path/to/your/dev/project
roundtable init            # scaffolds .roundtable/ (requirements, channel, decisions, prompts)
roundtable start           # opens tmux workbench: top lead|impl, bottom command|relay
```

`rt` is a built-in shorthand for `roundtable` (e.g. `rt start`, `rt list`, `rt stop`).

## Workbench, Mouse, And Popups

By default, `roundtable start` creates a 4-pane workbench:

```text
top:    lead (Claude Code) | impl (Codex)
bottom: command shell      | relay watcher
```

The bottom-left pane is a normal shell in the project directory. The bottom-right pane is the visible relay
watcher. `RT_LAYOUT=classic` restores the old layout: lead on the left, impl on the right, and a separate
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
`roundtable start` sends it the matching operating contract (`protocol.md` + `lead.md`/`impl.md`).
You only need to give your raw idea to the **left (lead)** pane — the relay takes over from there.

Automatic kickoff assumes both CLIs are already authenticated and configured, and that they land on
their normal main input prompt. First-run login, model-selection, trust-folder, update notices, or
other setup prompts can also look visually "settled"; complete those flows first, or run
`AUTO_KICKOFF=0 roundtable start` and paste the kickoff manually.

If auto-send mis-fires (e.g. it lands in a pane that wasn't fully ready), there are two fallbacks:

- once the CLI is fully up, run `roundtable kickoff` to **re-send** to both panes (or
  `roundtable kickoff lead|impl` for just one) — easier than re-pasting;
- or **copy/paste** from the files `start` writes: `.roundtable/kickoff-lead.txt` /
  `kickoff-impl.txt` (`cat` them from inside tmux — readable even after you've attached).

The kickoff is also **state-aware**: it tells each pane to re-read `requirements.md`, `channel.md`
and `decisions.md`, so re-starting a project mid-flight resumes from the last handoff (on a fresh
project those artifacts are empty templates, so it just waits for your idea). If you only detached
from a still-running session, no kickoff is needed — just `tmux attach` back.

Set `AUTO_KICKOFF=0` to do it manually instead (paste these once each pane is up):

1. Left pane (Claude Code): `Read .roundtable/prompts/protocol.md then .roundtable/prompts/lead.md — that is your operating contract. Then read .roundtable/requirements.md, .roundtable/channel.md and .roundtable/decisions.md to restore any prior state. If work is in progress, continue from the last handoff; otherwise acknowledge and wait for my idea.`
2. Right pane (Codex): `Read .roundtable/prompts/protocol.md then .roundtable/prompts/impl.md — that is your operating contract. Then read .roundtable/requirements.md, .roundtable/channel.md and .roundtable/decisions.md to restore any prior state. If work is in progress, continue from the last handoff; otherwise acknowledge and wait.`
3. Give your raw idea to the **left (lead)** pane.

Approve requirements at Gate A by typing into the lead pane:
`ARBITER: approved requirements v1`

## Lifecycle: stop, restart, resume

The guiding idea — **files are the memory, panes are disposable** — means you can kill and
recreate panes freely; nothing is lost as long as the on-disk artifacts survive.

**Detach (keep it running).** `Ctrl-b d` leaves the session alive in the background. The two CLIs
keep their full context. Reconnect any time with `tmux attach -t <session>` (find the name via
`roundtable list`) — **no kickoff needed**, the panes never died.

**Stop.** From the project dir:

```bash
roundtable stop      # kills this project's tmux session (lead, impl, command, relay)
```

This ends the CLI processes. The durable artifacts under `.roundtable/` are untouched, so the
work is fully recoverable on the next start.

**Relay pane killed.** If the bottom-right relay pane in the workbench is manually killed, lead/impl can still
look healthy, but handoffs will no longer be relayed. Recovery is still:

```bash
roundtable stop && roundtable start
```

**Restart / resume the same project.** Just start again — **do not clean anything**:

```bash
roundtable start
```

Each pane gets a brand-new CLI process (no memory of the old one), so the auto-kickoff re-sends the
operating contract *and* tells each side to re-read `requirements.md`, `channel.md`, and
`decisions.md`. A project that was mid-build resumes from the last handoff; a fresh project just
waits for your idea. This is the normal path after a `stop`, a crash, a machine reboot, or a CLI
update — the artifacts are the resume point, so you essentially never re-paste anything.

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
requirements/channel/decisions).

**Starting a *different*, unrelated task in the same directory (rare).** `start` always resumes the
existing artifacts, so to begin a clean, unrelated roundtable in a directory that already holds a
finished project's artifacts, reset the three durable files yourself — **back them up first**, since
they are not auto-saved:

```bash
mkdir -p .roundtable/_backup && cp .roundtable/{requirements,channel,decisions}.md .roundtable/_backup/
cp templates/{requirements,channel,decisions}.md .roundtable/
```

In normal one-directory-per-project use you never need this; prefer a separate directory for a
separate project.

## What lives where

| Path (in your project) | Purpose | Commit? |
|---|---|---|
| `.roundtable/requirements.md` | the agreed spec + work list | yes |
| `.roundtable/channel.md` | durable transcript of every handoff | yes |
| `.roundtable/decisions.md` | resolved disagreements + rationale | yes |
| `.roundtable/prompts/` | the role contracts the agents read | yes |
| `.roundtable/to-lead.md`, `to-impl.md` | transient mailboxes | no (gitignored) |
| `.roundtable/kickoff-lead.txt`, `kickoff-impl.txt` | kickoff text saved at start (manual fallback) | no (gitignored) |

## Env overrides

| Var | Default | Meaning |
|---|---|---|
| `CLAUDE_CMD` | `claude` | command to start the lead CLI |
| `CODEX_CMD` | `codex` | command to start the impl CLI |
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
