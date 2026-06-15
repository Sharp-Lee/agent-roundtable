# agent-roundtable

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

The full per-role rules are in `prompts/lead.md` and `prompts/impl.md`. They are copied into each
project so the agents read them as their operating contract.

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

On first start, do the **one-time kickoff** (the only manual paste in the whole flow):

1. Left pane (Claude Code is up): send
   `Read .roundtable/prompts/lead.md — that is your operating contract. Acknowledge, then wait for my idea.`
2. Right pane (Codex is up): send
   `Read .roundtable/prompts/impl.md — that is your operating contract. Acknowledge, then wait.`
3. Give your raw idea to the **left (lead)** pane. The relay takes over.

Approve requirements at Gate A by typing into the lead pane:
`ARBITER: approved requirements v1`

Stop everything: `roundtable stop`.

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
| `SESSION` | `roundtable` | tmux session name |
| `POLL_SECONDS` | `1.0` | relay poll interval |

## Limitations (known, by design)

- The relay nudges the *other* pane via `tmux send-keys`; it assumes a turn-based flow (only one
  side acting at a time), which this workflow guarantees. If you type into a pane while it is
  mid-turn, keystrokes can interleave — let each turn finish.
- It does not auto-resume the models' internal conversation across a full restart. Recovery is by
  re-reading the on-disk artifacts (which is more robust than fragile session resume).
