# Requirements — Harden the lead/impl role prompts

> Produced in Phase 1 by lead + impl, signed off by both, approved by the arbiter at Gate A.
> Version bumps whenever the arbiter requests changes. Item statuses drive the Phase 2 loop.

**Version:** v2
**Sign-off:** lead: ☑  impl: ☑   |   **Arbiter approval (Gate A):** ☑ (approved v2)

> **v2 change (arbiter):** relax the commit model — lead MAY commit doc-only artifact changes
> (`requirements.md` / `decisions.md`, channel-free); impl remains the sole implementer AND sole
> committer of CODE. The v1 "impl persists lead's edits on its next turn" machinery (checkpoint-
> commit handoffs, artifact-only checkpoint commits) is collapsed accordingly. Everything else
> from v1 is unchanged.

## 1. Problem & goal
The two source role contracts — `prompts/lead.md` and `prompts/impl.md` — drive an autonomous
two-agent loop, so any ambiguity or internal contradiction in them is amplified: an agent can
stall, deadlock, or act against the design. A read of the current prompts (plus `bin/relay.py`
and the three `templates/`) surfaced one self-contradiction that breaks the review loop, several
gaps that let workflow state drift, and undefined protocol terms. **Goal:** sharpen wording,
remove ambiguity, and close loop-stalling gaps in the two source prompts (with surgical touch-ups
to directly-dependent files), **without bloating them and without changing the core design.**

## 2. Scope
- **In scope:**
  - Primary edits to `prompts/lead.md` and `prompts/impl.md`.
  - Surgical (~1-line) touch-ups to `README.md` and/or `templates/` ONLY where a prompt-only fix
    would leave a real cross-file contradiction. Each such edit is enumerated in item 7.
- **Out of scope (explicit non-goals):**
  - Any change to the core design (hard constraints in §4).
  - Editing `bin/relay.py` or `bin/roundtable` (the relay already behaves correctly; the
    contradictions are in prompt/README wording, not code).
  - Editing the `.roundtable/prompts/` working copies (this session's runtime contracts).
  - Adding new phases, statuses, files, or Codex-specific tooling instructions.

## 3. Requirements (the Phase 2 work list)
Each item is testable by inspecting the resulting files. Status ∈ todo / doing / done.

| # | Requirement | Acceptance criteria | Depends on | Status |
|---|-------------|---------------------|------------|--------|
| 1 | **Narrow lead's action prohibition** so it stops contradicting the review/verify loop. | `lead.md` no longer says lead may "never run build/commit commands." It states lead **never edits implementation code and is not the code committer**, but **may** (a) run **read-only inspection, verification, and review commands** (e.g. `/verify`, `/code-review`, `/security-review`, `/ce-test-browser`) and (b) **commit doc-only artifact changes** to `requirements.md` / `decisions.md`. No remaining sentence in `lead.md` forbids running verification or committing doc-only changes. | — | done |
| 2 | **Put agreement, version & Gate-A handling on the artifact; keep `channel.md` relay-owned.** | `lead.md` no longer instructs lead to append `AGREED` (or anything) to `channel.md`; both prompts state `channel.md` is relay-owned and never hand-edited. Both prompts state: **in Phase 1**, when an agent sets `STATUS: agreed` on the requirements it ticks **its own** sign-off box in `requirements.md` (these boxes are the Phase-1/Gate-A sign-off, not a per-Phase-2-item action); **lead owns the Version field** (v1 initially) and **commits the agreed `requirements.md` + `decisions.md`** itself (doc-only). `lead.md` states that on an arbiter change-request lead **bumps the version and resets both sign-off boxes + the Gate A box in one edit**; after explicit arbiter approval lead **ticks the Gate A box, commits it (doc-only)**, and its **first Phase 2 action — the item-1 assignment written to the mailbox — re-engages impl via the relay**, so neither agent waits idle at Gate A. | — | done |
| 3 | **Define artifact-content & commit ownership** (relaxed: lead commits its docs, impl commits everything else). | Both prompts state: **lead owns the content of `requirements.md` and `decisions.md` across all phases**; the only edit impl makes to `requirements.md` is ticking its own sign-off box; if impl finds `decisions.md` inaccurate it **flags via the mailbox and lead corrects it** (impl never edits content). **Commit model (split by file path, not "doc vs code"):** **lead commits only `requirements.md` and `decisions.md`** (its own artifact edits, when it makes them) — never `channel.md` (**channel-free**) and never any other file. **impl is the sole implementer and commits everything else in the work tree** — source code, `prompts/*.md`, `README.md`, `templates/`, etc. — **plus** the relay-appended `channel.md` (transcript history), restaged on each commit so it sweeps the transcript to date. Neither party commits the mailboxes (`to-*.md`), `panes.env`, or the `.roundtable/prompts/` working copies; commits capture a **real diff** (never `--allow-empty`). **`channel.md`'s commit cadence is not load-bearing** — recovery always reads the on-disk working tree, where the transcript is complete regardless of when it was last committed. The rule appears once, crisply, in both prompts. *(No checkpoint-commit handoffs or artifact-only checkpoint commits — lead persists its own doc edits directly.)* | 1 | done |
| 4 | **Canonical Phase 2 loop + assignment contract** (clean split: impl commits code, lead commits the status update). | `lead.md` and `impl.md` describe **one** ordering: assign → impl challenges → converge → impl implements **and commits code** → impl hands back **committed (no uncommitted impl changes for the item)** → lead reviews (`/code-review` + `/verify`) → on issues, **the same point** loops back to impl (fix + commit) → both `agreed` → **lead marks the item `done` and commits that doc update** (`requirements.md`, doc-only). The commit instruction is stated **once per event** (today `lead.md` redundantly names "impl commits" in both step 3 and step 5 — collapse to one). `lead.md` states a Phase 2 assignment handoff **must include**: requirement version + ID, acceptance criteria, constraints/non-goals, dependencies, and proposed verification. | 1, 3 | done |
| 5 | **Define the protocol terms** referenced but never defined, kept parallel in both prompts, and **fix the restart-recovery text**. | Both prompts define the four STATUS values (`needs-reply`, `agreed`, `blocked`, `escalate`); define **one round** = one lead↔impl back-and-forth on the **same unresolved point**, and clarify the >3-round cap fires on **unresolved disagreement or repeated rejection of the same proposed fix/rationale** — a stubborn bug escalates only when it becomes a real blocker, not merely because debugging took several rounds; state that **agents address the arbiter only via pane output, never via the mailbox**; give an inbox-recovery rule (on a nudge, read the inbox and infer phase from its header + `requirements.md`; if the message is empty/malformed/stale/wrong-`FROM`, reply `STATUS: blocked` asking for a resend rather than guessing); and **update the existing "re-read requirements.md, channel.md, decisions.md" sentence** so it names `requirements.md` as the authority for sign-off/version/Gate-A and frames `channel.md` as history. All four definitions appear in **both** prompts. | — | done |
| 6 | **Sharpen the skill-trigger guidance** in `lead.md` (keep it lean & trigger-based). | `lead.md` states: `/understand` runs **once per existing-codebase session** (or after a context-losing restart), not per phase/item; `/ce-doc-review` before the **first** Phase 1 handoff and after any change to **scope, a requirement's acceptance criteria, constraints, or the work-list set** (not wording/formatting-only edits); `/ce-plan` per Phase 2 requirement; `/code-review` + `/verify` after impl's **committed** handback. `/simplify` (and any fix-applying skill) is reframed as a **review/suggestion pass for lead — impl performs all code changes.** Conditional skills remain trigger-based. | 1 | doing |
| 7 | **Leanness, symmetry & adjacent-file consistency.** | Protocol sections (channel, message header, STATUS, phase gates, disagreement cap, recovery) are **inspectably parallel** — shared sections use the **same headings/order and equivalent definitions** across both prompts; role sections stay role-specific (lead: synthesis/review/artifact ownership/doc commits/tool triggers; impl: challenge-first/implement/code commits). `impl.md` stays **tool-agnostic** — at most one sentence that impl may use its native tools/skills but they never override the mailbox / Gate A / role contract. No duplicated first-wake instructions (the prompts say only: lead initiates after the arbiter's idea; impl waits for a handoff). **Adjacent edits (enumerated):** (a) `README.md` Phase 2 line is adjusted so it matches the canonical ordering in item 4 (impl commits code during implement; lead commits the status update); (b) any path reference uses `bin/relay.py` (no root `relay.py`). **Neither prompt grows by more than ~10 net lines, except where lines are needed to remove a listed contradiction.** | 2, 3, 4, 5 | todo |

## 4. Constraints & assumptions
- **Hard constraints (core design — do NOT change):** file-relay + mailbox protocol (write to
  `to-impl.md`/`to-lead.md`, then stop; never poll); the `PHASE / FROM / STATUS` message format;
  three phases + Gate A (arbiter approval of requirements) + autonomous Phase 2 with the >3-round
  disagreement cap; **lead never edits implementation code; impl is the only implementer.** (Commit
  split is a v2 detail, not a locked invariant: lead commits only `requirements.md`/`decisions.md`;
  impl commits every other file plus `channel.md` — see item 3.) Prompts stay in English and concise.
- **Assumption:** `bin/relay.py` already correctly owns `channel.md`, fires only on mailbox
  writes, and ignores empty mailbox bodies, so no relay change is needed.
- **Verification approach:** items are markdown-edit items, so acceptance is checked by `/verify`
  reading both prompts (and the touched adjacent files) for the required **presence/absence of
  text** AND **semantic cross-file consistency** (the Phase 2 ordering matches `README.md`; the
  protocol sections read parallel; no sentence reintroduces a fixed contradiction or the collapsed
  v1 checkpoint-commit machinery). As a regression guard, `roundtable selftest` still passes.

## 5. Open questions
- None blocking. v2 simplifies the commit model per the arbiter: the committer split is **by file**
  — lead commits only `requirements.md`/`decisions.md` (channel-free); impl commits every other file
  (code, `prompts/*.md`, README, templates) plus `channel.md`. No checkpoint-commit handoffs remain.
- **Known minor limitation (accepted, not blocking):** because lead's commits are channel-free and
  Phase 1 has no code commit, the Phase-1 transcript in `channel.md` is not committed until impl's
  first Phase-2 commit; likewise the final item's trailing transcript lands only if a later commit
  sweeps it. This never loses data for recovery (the working tree always holds the full transcript),
  but a *fresh clone* taken in those windows would lag the live transcript. Judged acceptable vs.
  reintroducing the removed flush machinery. Confirm at sign-off.
