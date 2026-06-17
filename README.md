# agent-roundtable

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
roundtable start           # opens tmux: left=lead | right=impl | window 'relay'
```

`rt` is a built-in shorthand for `roundtable` (e.g. `rt start`, `rt list`, `rt stop`).

On first start, the **kickoff is automatic**: once each pane's CLI output looks settled,
`roundtable start` sends it the matching operating contract (`protocol.md` + `lead.md`/`impl.md`).
You only need to give your raw idea to the **left (lead)** pane — the relay takes over from there.

Automatic kickoff assumes both CLIs are already authenticated and configured, and that they land on
their normal main input prompt. First-run login, model-selection, trust-folder, update notices, or
other setup prompts can also look visually "settled"; complete those flows first, or run
`AUTO_KICKOFF=0 roundtable start` and paste the kickoff manually.

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

Stop this project's session: `roundtable stop` (run from the project dir).

Each project gets its own tmux session (`roundtable-<name>-<hash>`), so you can run several
roundtables at once. `roundtable list` shows the running ones.

## What lives where

| Path (in your project) | Purpose | Commit? |
|---|---|---|
| `.roundtable/requirements.md` | the agreed spec + work list | yes |
| `.roundtable/channel.md` | durable transcript of every handoff | yes |
| `.roundtable/decisions.md` | resolved disagreements + rationale | yes |
| `.roundtable/prompts/` | the role contracts the agents read | yes |
| `.roundtable/to-lead.md`, `to-impl.md` | transient mailboxes | no (gitignored) |

## Env overrides

| Var | Default | Meaning |
|---|---|---|
| `CLAUDE_CMD` | `claude` | command to start the lead CLI |
| `CODEX_CMD` | `codex` | command to start the impl CLI |
| `SESSION` | per-project `roundtable-<name>-<hash>` | override the tmux session name |
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
