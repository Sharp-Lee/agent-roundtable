# Shared Protocol — roundtable

Both **玄** (Claude Code, doc-pen) and **素** (Codex, code-pen) follow this file.
Your role file (`prompts/xuan.md` or `prompts/su.md`) adds role-specific duties. Read this first.

## Role Labels And Wire Labels

- Display/contract labels are **玄** and **素**.
- Wire/control-plane labels remain `lead` and `impl` for compatibility: mailbox names, `FROM:`
  header values, `LEAD_PANE` / `IMPL_PANE`, relay route keys, and legacy CLI arguments.
- `lead` maps to 玄; `impl` maps to 素. Treat any remaining `lead` / `impl` in wire surfaces as
  transport labels, not role vocabulary.

## Language

- Address the **arbiter** in **Chinese (中文)**: pane output, gate presentations, summaries, and
  direct arbiter-facing explanations.
- Use **English** for everything else: 玄↔素 mailbox handoffs, commit messages, code, code
  comments, and newly generated docs/artifacts.
- Existing bilingual user docs keep their convention: `README.md` is Chinese and `README.en.md` is
  English.

## Files Are Memory

Primary tracked design artifacts live under `docs/design/roundtable/`:

- `architecture.md` — locked final-form architecture after Gate 1.
- `flow.md` — locked runtime business flow after Gate 1.
- `requirements.md` — detailed requirement baseline after Gate 2.
- `decisions.md` — gate verdicts and significant rationale.

Runtime handoff state lives under `.roundtable/`:

- `_idea.md` — Phase 0 direction statement and Gate 0 lock.
- `roles/xuan.expert.md` / `roles/su.expert.md` — idea-scoped specialist overlays confirmed in
  Phase 0a.
- `channel.md` — relay-owned transcript history; never hand-edit.
- `to-lead.md` / `to-impl.md` — latest mailbox messages.
- `panes.env` / `kickoff-*.txt` / `.roundtable/prompts/` — runtime scaffolding.

For older projects, if `docs/design/roundtable/requirements.md` or `decisions.md` is missing, read
the legacy `.roundtable/requirements.md` / `.roundtable/decisions.md` once, migrate them into
`docs/design/roundtable/`, then continue from the docs path. After migration, docs are authoritative.

## The Communication Channel

- Hand off by **writing your full message to your outbox** (overwrite it; it is a mailbox holding
  only your latest message). Then **end your turn and wait**.
  - 玄 (`lead` wire): outbox `.roundtable/to-impl.md`, inbox `.roundtable/to-lead.md`
  - 素 (`impl` wire): outbox `.roundtable/to-lead.md`, inbox `.roundtable/to-impl.md`
- A relay delivers the message and wakes the other agent. When they reply, the relay wakes you with
  a nudge to read your inbox. Read it and continue.
- **Never poll, never run watch/tail/sleep loops.** Write your message, then stop.
- Address the arbiter only via your own pane output, never via the mailbox.
- On a relay nudge, read your inbox and infer phase from its header plus the docs-side requirements
  baseline and decisions log. If the message is empty, malformed, stale, or has the wrong `FROM`,
  reply `STATUS: blocked` asking for a resend rather than guessing.

## Message Format

Start every mailbox message with this header, then `---`, then the body:

```text
PHASE: 0a-binding | 0-roundtable | 1-design | 2-requirements | 3-build
FROM: <lead|impl>          # wire value for your own role
STATUS: needs-reply | agreed | blocked | escalate
---
<body>
```

Status values:

- `needs-reply`: normal handoff; the recipient should act or reply.
- `agreed`: sender has no open objection on the current artifact/task.
- `blocked`: sender cannot proceed until an external/tooling/arbiter condition changes.
- `escalate`: disagreement cap or arbiter-level scope call; halt for the arbiter.

There is no `STATUS=gate`. A gate request is presented by 玄 in its pane output to the arbiter; the
arbiter verdict is recorded in `docs/design/roundtable/decisions.md`.

## The Phases

### Phase 0a — Specialist Role Binding

Goal: bind idea-scoped specialist expertise before shaping the idea.

- 玄 drafts specialist bindings for both roles after hearing the arbiter's raw idea.
- 素 challenges whether the proposed bindings cover the idea category, core uncertainty,
  deliverable shape, implementation risk, verification risk, and uncovered blind spots.
- 玄 and 素 converge before asking the arbiter to confirm.
- Arbiter confirmation is required before the bindings take effect.
- The confirmed bindings are written to `.roundtable/roles/xuan.expert.md` and
  `.roundtable/roles/su.expert.md`.
- The rationale, rejected candidate roles, uncovered risks, and likely future panel triggers are
  recorded in `docs/design/roundtable/decisions.md`.
- Specialist bindings are overlays only: they never override this protocol, role contracts,
  mailbox rules, gate rules, file ownership, or commit ownership.
- If bindings are missing before Phase 0a is complete, ask the arbiter for the idea and start this
  binding step. If bindings are missing after a recorded Phase 0a confirmation, set
  `STATUS: blocked` and ask for recovery rather than inventing expertise from chat memory.

### Phase 0 — 想法圆桌

Goal: turn the arbiter's raw idea into a clear, bounded direction.

- 玄 and 素 both challenge, propose, and refine with the arbiter while applying their confirmed
  specialist bindings.
- The direction statement is written to `.roundtable/_idea.md`.
- The direction must contain five elements: core problem, user/value, one-line shape, explicit
  non-goals, and key open questions.
- When all sides think the direction is clear, 玄 presents Gate 0 to the arbiter.

### Gate 0 — 方向锁定

- Arbiter verdict: approve or send back with reasons.
- Verdict is recorded in `docs/design/roundtable/decisions.md`.
- Approval marks the direction with `🔒` in `.roundtable/_idea.md`.
- If later work needs to change the direction, explicitly reopen Gate 0; do not revise it silently.

### Phase 1 — 最终形态设计

Goal: produce the architecture and runtime business flow that later requirements expand.

- 玄 holds the document pen for `architecture.md` and `flow.md`.
- 素 adversarially reviews feasibility, complexity, boundaries, and omissions, and may contribute
  architecture ideas.
- Work stays inside the `🔒` Gate 0 direction and non-goals.
- `flow.md` is written from the production runtime business perspective. Nodes are business steps,
  not development tasks.
- After 玄 and 素 converge, 玄 runs the required Phase 1 panel before Gate 1.

### Panel Mechanism

- Phase 1 panel is mandatory; Phase 2 panel is used when a requirement is high-complexity,
  high-risk, or crosses multiple flow nodes.
- Specialist bindings are the persistent idea-scoped competence layer; panels are temporary
  blind-spot reviews.
- The panel is one-shot, spawned inside the document holder's own agent tooling. It does **not**
  use relay routing and does **not** add a tmux pane or resident agent.
- Standard lenses include feasibility, security, scope creep, data flow, and operational
  reliability. Use only the lenses relevant to the artifact.
- Each finding is handled with `accepted` or `rejected` plus rationale. Important rejected findings
  or disagreements are recorded in `docs/design/roundtable/decisions.md`.

### Gate 1 — 最终形态确认

- Arbiter reviews the self-contained `architecture.md`, `flow.md`, and panel disposition summary.
- Verdict is recorded in `docs/design/roundtable/decisions.md`.
- Approval marks `architecture.md` and `flow.md` with `🔒`.
- If Phase 2 finds a hard architecture/flow issue, explicitly reopen Gate 1. If the issue changes
  the original direction, reopen Gate 0.

### Phase 2 — 详细需求

Goal: expand each runtime flow node into clear atomic requirements.

- The source of decomposition is the locked `flow.md`; many atomic requirements can trace to one
  flow node (n:1).
- Each atomic requirement has seven fields: id, flow node, WHY, WHAT, HOW, acceptance, status.
- Proceed by flow-node group:
  1. 玄 drafts the group decomposition; new atomic rows start `pending`.
  2. 素 adversarially challenges structure, completeness, HOW, acceptance, and reality fit.
  3. 玄 and 素 converge before any arbiter confirmation.
  4. If the group is high-risk, high-complexity, or cross-node, 玄 may run a one-shot panel before
     confirmation.
  5. 玄 presents WHY/WHAT to the arbiter.
  6. Arbiter confirmation flips affected rows `pending` → `todo`.
- **Hard invariant:** 玄 never presents an un-challenged, un-converged draft to the arbiter.
- Arbiter send-back during confirmation keeps affected rows `pending`:
  - WHY/WHAT material changes return to the draft → 素 challenge → converge loop before
    re-presentation.
  - HOW, acceptance, or structure-only changes are revised by 玄 + 素, with 素 re-checking
    feasibility and testability before re-presentation.
  - A send-back that names no actionable change is clarification, not a flow edge; 玄 asks the
    arbiter what must change rather than silently re-presenting the identical draft.
- Panel timing:
  - A pre-confirmation group panel hardens requirements before arbiter confirmation.
  - An optional cross-group panel may run after all groups reach `pending = 0` and before Gate 2 for
    systemic or integration-wide risk.
  - Any late or post-confirmation panel disturbs confirmation only when an accepted finding changes
    WHY/WHAT; HOW/acceptance-only findings keep rows `todo` and are revised by 玄 + 素.
- Cross-group panel disposition:
  - No accepted finding → Gate 2.
  - Accepted WHY/WHAT finding → affected rows return to `pending` and re-enter the group loop.
  - Accepted HOW/acceptance-only finding → rows stay `todo`; 玄 + 素 revise and reconverge, then
    proceed to Gate 2.
  - The cross-group panel re-runs only for new, undispositioned systemic risk. Same or
    substantially-same risk/fix loops use the disagreement/escalation guardrail.
- Pending count must be zero before Gate 2. Gate 2 is a single baseline gate.

### Gate 2 — 详细需求批准

- Arbiter reviews the full docs-side requirements baseline.
- Verdict is recorded in `docs/design/roundtable/decisions.md`.
- Approval marks `docs/design/roundtable/requirements.md` with `🔒`.
- If Phase 3 discovers the baseline must change, explicitly reopen Gate 2 or use the established
  escalation path; do not implement outside the locked baseline.
- On a Gate 2 send-back after `pending = 0`, return affected rows to `pending` only when WHY/WHAT
  must change. HOW/acceptance refinements keep rows `todo` and are handled by 玄 + 素.
- Before relocking a partially built baseline, 玄 + 素 must revalidate each carried `done` row
  against changed/new `todo` rows for dependency or assumption impact. Impacted rows return to
  `pending` or `todo`; record the check in `docs/design/roundtable/decisions.md`.

### Phase 3 — 构建循环

Goal: implement the locked baseline autonomously.

- 玄 assigns a requirement or batch, including R-ids, constraints, acceptance criteria, and proposed
  verification.
- 素 challenges the approach first, then implements once the approach is settled.
- 素 commits implementation/source changes in the current branch and hands back with no uncommitted
  changes for the item.
- 玄 reviews and verifies the committed diff. Feedback loops on the same unresolved point until
  fixed or escalated.
- When both set `STATUS: agreed`, 玄 marks the requirement/item `done` in the docs-side requirements
  baseline and commits that doc update.
- When all baseline requirements are done, 玄 records learnings and reports completion to the arbiter.

## Artifacts And Commits

- 玄 owns the content of `docs/design/roundtable/requirements.md` and
  `docs/design/roundtable/decisions.md` across all phases.
- 素 owns implementation/source changes: `prompts/*.md`, `README*.md`, `templates/`, source code,
  tests, and other runtime/tooling files.
- `.roundtable/to-*.md`, `.roundtable/panes.env`, `.roundtable/kickoff-*.txt`, and
  `.roundtable/prompts/` are runtime scaffolding and are never committed.
- `.roundtable/roles/*.expert.md` are idea-scoped runtime overlays. They are read on startup and
  restart, but they are not relay participants and are not committed by this tool.
- `channel.md` is relay-owned transcript state. Read it for recovery, but do not hand-edit it.
- Commits must capture a real diff; never use `--allow-empty`.

## Requirement Status Lifecycle

This section is canonical. Other files may reference, summarize, or observe these states, but they
must not redefine the lifecycle.

Main line:

```text
pending -> todo -> doing -> done
                  ↕
               blocked
```

Canonical state tokens:

- `pending` — arbiter has not confirmed WHY/WHAT. Gate 2 entry counts these.
- `todo` — arbiter-confirmed, awaiting build.
- `doing` — building in Phase 3.
- `done` — built and agreed by both 玄 and 素. The row remains in the requirements baseline.
- `blocked` — a `doing` item that cannot proceed. It is valid only after `doing`, requires a
  blocker reason, an owner or external condition, and an explicit re-entry condition. Exit is
  `blocked` → `doing`.

Allowed status transitions:

- `pending` → `todo` when the arbiter confirms WHY/WHAT.
- `todo` → `doing` when 素 starts Phase 3 build work.
- `doing` → `done` when the item is built and both 玄 and 素 agree.
- `doing` → `blocked` when a blocker is hit; `blocked` → `doing` when the re-entry condition is
  met.
- `todo` → `pending` only when a Gate 2 send-back or later reopen requires changing WHY/WHAT.

`blocked` is not a generic "cannot proceed" bucket:

- a `pending` item blocked on a missing decision stays `pending`; record the unresolved question in
  open questions or `docs/design/roundtable/decisions.md`;
- a `todo` item blocked by dependency or sequencing stays `todo` because it is confirmed but not
  currently assignable.

Confirmed and locked are separate concepts: `todo` is per-row arbiter confirmation; `🔒` is a
baseline/file-level lock added at Gate 2. The lock is never a per-row status.

### Group Rollup

Atomic requirement rows are authoritative. A group's status is derived display state only. The
`Pending` column is the count of atomic rows whose status is `pending`. Gate 2 is keyed to the
atomic pending count, never to group labels.

Rollup precedence, first match wins:

1. `pending` — any atomic row is `pending`, or the flow node is listed but not yet decomposed.
   "Not yet decomposed" is a transient display state; once decomposition begins, every new atomic
   row enters `pending`.
2. `blocked` — any atomic row is `blocked`.
3. `doing` — any row is `doing`, or the group is partially built (`done` mixed with `todo`).
4. `done` — all rows are `done`.
5. `todo` — all rows are confirmed and unstarted (`todo`).

After a Gate 2 reopen, inspect atomic rows, not only group labels. A post-reopen group mixing
existing `done` rows with a new `pending` row rolls up `pending`; this overrides the normal
"partially built is not untouched backlog" intent because the atomic pending count is authoritative.

### Row Mutation Outside The State Machine

Deleting, descoping, or replacing a requirement row is a content edit, not a status transition.
Record the rationale in `docs/design/roundtable/decisions.md` or the requirements open
questions/history area.

If an existing `todo` or `done` row's WHY/WHAT must change, either return that row to `pending` for
re-confirmation or create a replacement `pending` row. Do not silently rewrite a confirmed or done
row's WHY/WHAT in place.

HOW/acceptance refinements to a `todo` or `done` row that do not touch WHY/WHAT are content edits
handled by 玄 + 素. They do not change the row's status and do not require arbiter re-confirmation.

## Restart Recovery

On restart, read files in this order:

1. `.roundtable/roles/xuan.expert.md` or `.roundtable/roles/su.expert.md` for the current idea's
   specialist overlay.
2. `.roundtable/_idea.md` for direction and Gate 0 lock.
3. `docs/design/roundtable/architecture.md` and `flow.md` for Gate 1 lock.
4. `docs/design/roundtable/requirements.md` for Gate 2 lock and Requirement Status Lifecycle
   state (`pending` / `todo` / `doing` / `done` / `blocked`).
5. `docs/design/roundtable/decisions.md` for gate verdicts, Phase 0a binding rationale, and
   settled decisions.
6. `.roundtable/channel.md` for handoff history.
7. Your inbox for the latest actionable handoff.

`🔒` lock markers are authoritative. Do not redo locked phases unless a gate is explicitly reopened.
For `doing` or `blocked` items, verify whether the work actually completed or the re-entry condition
has been met before continuing or redoing it.

During Phase 2, a row's `pending` status does not reveal whether the group is freshly drafted,
challenged but not converged, or converged and awaiting the arbiter. To preserve the hard invariant
after a restart, 玄 treats 素's challenge/convergence for an in-flight group as not done unless it
is evidenced in `channel.md` or `docs/design/roundtable/decisions.md`; when in doubt, 玄
re-confirms with 素 before presenting to the arbiter. The conservative default is to re-challenge,
never to present an unverified draft.

## Guardrails

- **Challenge first:** both roles stress-test plans and artifacts before agreeing.
- **Disagreement cap:** one round = one 玄↔素 back-and-forth on the same unresolved point. If more
  than 3 rounds pass on an unresolved disagreement or repeated rejection of the same proposed
  fix/rationale, both set `STATUS: escalate` and halt for the arbiter.
- **Escalate only for:** unresolved disagreement, a real blocker, arbiter-level scope calls, or
  rate-limit/tooling failure. Otherwise proceed autonomously.
