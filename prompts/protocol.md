# Shared Protocol — roundtable

Both **lead** (Claude Code) and **impl** (Codex) follow this file. Your role file
(`prompts/lead.md` or `prompts/impl.md`) adds your role-specific duties. Read this first.

## The communication channel (this is how you avoid copy-paste)
- Hand off by **writing your full message to your outbox** (overwrite it; it is a mailbox holding
  only your latest message). Then **end your turn and wait**.
  - lead: outbox `.roundtable/to-impl.md`, inbox `.roundtable/to-lead.md`
  - impl: outbox `.roundtable/to-lead.md`, inbox `.roundtable/to-impl.md`
- A relay delivers it and wakes the other agent. When they reply, the relay wakes you with a nudge
  to read your inbox. Read it and continue.
- **Never poll, never run watch/tail/sleep loops.** Write your message, then stop.
- The durable transcript lives in `.roundtable/channel.md` (relay-owned; never hand-edited) — read
  it for history, but communicate only by writing your outbox.
- Address the arbiter only via your own pane output, never via the mailbox.
- On a relay nudge, read your inbox and infer phase from its header plus `.roundtable/requirements.md`;
  if the message is empty, malformed, stale, or has the wrong `FROM`, reply `STATUS: blocked` asking
  for a resend rather than guessing.

## Message format (always)
Start every mailbox message with this header, then `---`, then the body:
```
PHASE: 0-roundtable | 1-requirements | 2-build
FROM: <lead|impl>          # your own role
STATUS: needs-reply | agreed | blocked | escalate
---
<body>
```
Status values:
- `needs-reply`: normal handoff; the recipient should act or reply.
- `agreed`: sender has no open objection on the current artifact/task.
- `blocked`: sender cannot proceed until an external/tooling/arbiter condition changes.
- `escalate`: disagreement cap or arbiter-level scope call; halt for the arbiter.

## Artifacts & commits
- lead owns the content of `.roundtable/requirements.md` and `.roundtable/decisions.md` across all
  phases. impl edits `.roundtable/requirements.md` only to tick its own sign-off box; if
  `.roundtable/decisions.md` looks wrong, impl flags it by mailbox and lead corrects it.
- lead commits only `.roundtable/requirements.md` and `.roundtable/decisions.md` (whole files,
  including impl's sign-off tick), never `.roundtable/channel.md` or any other path.
- impl commits implementation/source work (`prompts/*.md`, `README.md`, `templates/`, source code,
  etc.) plus the relay-appended `.roundtable/channel.md` on each commit to sweep transcript history.
- Neither party commits `.roundtable/to-*.md`, `.roundtable/panes.env`, or `.roundtable/prompts/`.
- Commits must capture a real diff; never `--allow-empty`. `channel.md` commit cadence is not
  load-bearing: recovery reads the on-disk working-tree transcript, even if the committed one lags.

## Guardrails (shared)
- **Disagreement cap:** one round = one lead↔impl back-and-forth on the same unresolved point. If
  more than 3 rounds pass on an unresolved disagreement or repeated rejection of the same proposed
  fix/rationale, both set `STATUS: escalate` and **HALT for the arbiter**; ordinary debugging
  escalates only when it becomes a real blocker.
- **Escalate to the arbiter only for:** unresolved disagreement (>3 rounds), a real blocker (failing
  build you can't resolve, missing access), genuinely arbiter-level scope calls, or a
  rate-limit/tooling failure. Otherwise proceed autonomously; do not ask permission on routine steps.
- **Restart recovery:** if your pane was restarted and you lack context, re-read
  `.roundtable/requirements.md`, `.roundtable/decisions.md`, and `.roundtable/channel.md`. Treat
  `requirements.md` as the authority for phase, version, sign-off/Gate A, and item status;
  `decisions.md` for settled rationale; `channel.md` as history.
