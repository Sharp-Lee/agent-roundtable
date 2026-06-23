# Requirements — Phase 2 sequence + requirement status lifecycle

> Produced in Phase 2 from the 🔒 locked `architecture.md` + `flow.md`.
> **🔒 Gate 2 locked 2026-06-23.** All 19 WHY/WHAT arbiter-confirmed → rows `todo`; pending = 0;
> baseline approved. Supersedes the completed v2-pipeline-build worklist previously at this path
> (G1–G12, preserved in git history at commit `37a1727`). Reopen Gate 2 explicitly to change the
> baseline; reopen Gate 1 if a hard architecture/flow issue surfaces during build.

**Version:** v1
**Baseline:** locked 🔒
**Gate 2:** approved
**Pending count:** 0

## 1. Problem & goal

Phase 2 of the roundtable pipeline had no written internal order and a status vocabulary that
had drifted across three files with an undefined post-confirmation state. This baseline encodes
the locked final form: a canonical requirement-status lifecycle and an explicit Phase-2
per-group loop, written once in `protocol.md` and referenced everywhere else, guarded by a
drift selftest. Contract/doc only; Phase 0/1/3 behavior frozen.

## 2. Locked inputs

- **Direction:** `.roundtable/_idea.md` (🔒 Gate 0)
- **Architecture:** `docs/design/roundtable/architecture.md` (🔒 Gate 1)
- **Runtime flow:** `docs/design/roundtable/flow.md` (🔒 Gate 1)
- **Non-goals / frozen boundaries:** no engine refactor; the only code touch is the selftest
  drift guard; no new states/gates/panes/relay routes; no Phase 0/1/3 behavior change; one
  status column only.

If a requirement would change the locked direction, architecture, or flow, stop and reopen the
relevant gate.

## 3. Scope

- **In scope:** `prompts/protocol.md` (canonical lifecycle section + Phase 2 order + Restart
  Recovery), `prompts/xuan.md`, `prompts/su.md`, `templates/requirements.md`, the
  `bin/roundtable` selftest drift guard, `README.md` / `README.en.md` workflow line, and a
  one-line historical annotation on `docs/design/front-end-pipeline-final-form.md`.
- **Out of scope:** `bin/relay.py` behavior, `templates/channel.md`, any retro-edit of completed
  v2-build row statuses, and any new STATUS value / gate / pane / route.

## 4. 拆解清单 (decomposition)

Decomposition source = the 🔒 architecture surfaces (where each locked rule is written). Gate 2
requires `pending = 0`. Group status is derived from atomic rows (see `flow.md` §4).

| Group | Surface (architecture node) | Requirement ids | Pending | Status |
|---|---|---|---:|---|
| G1 | `protocol.md` — canonical Requirement Status Lifecycle | R-LC-1..4 | 0 | done |
| G2 | `protocol.md` — Phase 2 order + invariant + panel + reopen | R-P2-1..4 | 0 | done |
| G3 | `protocol.md` — Restart Recovery update | R-RR-1..2 | 0 | done |
| G4 | `prompts/xuan.md` — 玄 duties | R-XU-1..3 | 0 | todo |
| G5 | `prompts/su.md` — 素 duties | R-SU-1..2 | 0 | todo |
| G6 | `templates/requirements.md` — pointer + sentinels + diagram + note | R-TM-1..2 | 0 | todo |
| G7 | `bin/roundtable` — selftest drift guard | R-ST-1..1 | 0 | todo |
| G8 | `README.md` / `README.en.md` + historical annotation | R-EX-1..1 | 0 | todo |

## 5. Atomic requirement format

Seven fields each: 编号 / 所属节点 / WHY / WHAT / HOW / 验收 / 状态. Status values follow the
canonical lifecycle in `prompts/protocol.md` (`pending → todo → doing → done`, with `blocked`
as a `doing`-only exception). `pending` = arbiter has not confirmed WHY/WHAT.

## 6. Requirements by surface

### G1 · `protocol.md` — canonical Requirement Status Lifecycle

#### R-LC-1 The four-state main line + `blocked` exception
- **编号:** R-LC-1
- **所属节点:** G1 canonical lifecycle
- **WHY:** One authoritative state set, so status means the same thing everywhere.
- **WHAT:** A new "Requirement Status Lifecycle" section defining `pending → todo → doing →
  done` plus `blocked` as a `doing`-only exception (reason + owner/condition + re-entry; exit
  `blocked → doing`), with the narrowing rule (a `pending`/`todo` item blocked by
  decision/dependency stays in its state, not `blocked`).
- **HOW:** New section in `protocol.md` matching `flow.md` §F-2 (state meanings + transitions).
- **验收:** Section exists; lists exactly the five tokens with the four transitions and the
  `blocked` entry/exit/narrowing rules; no other file redefines the set.
- **状态:** done

#### R-LC-2 Confirmed vs locked decoupled
- **编号:** R-LC-2
- **所属节点:** G1
- **WHY:** Avoid conflating per-row confirmation with baseline locking.
- **WHAT:** State that `todo` (per-row, arbiter-confirmed) is independent of `🔒` (baseline-level
  at Gate 2); the lock is a file property, never a per-row state.
- **HOW:** One paragraph in the lifecycle section.
- **验收:** Text present and unambiguous.
- **状态:** done

#### R-LC-3 Group rollup precedence (atomic rows authoritative)
- **编号:** R-LC-3
- **所属节点:** G1
- **WHY:** Deterministic, conservative group display; restart recovery never misreads progress.
- **WHAT:** Atomic rows are the source of truth; group status is derived; `Pending` column =
  count of `pending` atomic rows; precedence `pending > blocked > doing/partially-built > done
  > todo`; "not yet decomposed" → `pending` (transient); Gate 2 keyed to atomic pending count.
- **HOW:** Subsection in the lifecycle section, mirroring `flow.md` §4.
- **验收:** Precedence resolves every mix (incl. `blocked+doing`, `done+todo`, post-reopen
  `done+pending`); states the mixed-rollup caveat (inspect atomic rows after a reopen).
- **状态:** done

#### R-LC-4 Row mutation outside the state machine
- **编号:** R-LC-4
- **所属节点:** G1
- **WHY:** Prevent silent rewrites of confirmed/done rows.
- **WHAT:** Delete/descope/replace is not a status transition; a `todo`/`done` row whose
  WHY/WHAT must change returns to `pending` or gets a replacement `pending` row, never an
  in-place rewrite; `done` rows stay in the baseline (not removed).
- **HOW:** Short rule block in the lifecycle section, mirroring `flow.md` §3 "Row mutation".
- **验收:** Rule present; covers delete/descope/replace + the WHY/WHAT-change handling.
- **状态:** done

### G2 · `protocol.md` — Phase 2 order + invariant + panel + reopen

#### R-P2-1 Explicit per-group loop + hard invariant
- **编号:** R-P2-1
- **所属节点:** G2 Phase 2 order
- **WHY:** Make Phase 2's order deterministic and protect arbiter time.
- **WHAT:** Encode the per-group loop (draft → 素 challenge → converge → [panel] → present
  WHY/WHAT → arbiter confirm → flip `pending→todo`; all groups `pending=0` → Gate 2) and the
  hard invariant: 玄 never presents an un-challenged, un-converged draft to the arbiter.
- **HOW:** Rewrite the Phase 2 section of `protocol.md` to match `flow.md` §F-1.
- **验收:** Loop order + invariant present; "按组推进" explicit; Gate 2 = single baseline gate.
- **状态:** done

#### R-P2-2 Panel timing (before confirmation) + the three positions
- **编号:** R-P2-2
- **所属节点:** G2
- **WHY:** The arbiter should confirm only panel-hardened requirements; panels must be able to
  affect flow.
- **WHAT:** Pre-confirmation group panel (E); optional cross-group panel (K, after confirm /
  before Gate 2, with the disposition branch); any late panel invalidates confirmation **iff**
  an accepted finding changes WHY/WHAT.
- **HOW:** Encode `flow.md` "Panel timing" prose into the Phase 2 section.
- **验收:** All three positions described; "disturbs confirmation iff WHY/WHAT changes" stated.
- **状态:** done

#### R-P2-3 Send-back transitions + cross-group-panel bound
- **编号:** R-P2-3
- **所属节点:** G2
- **WHY:** No 素-bypass, no non-terminating loops, no unbounded panel churn.
- **WHAT:** Send-back keeps the row `pending`, routes WHY/WHAT→redraft and
  HOW/acceptance/structure→revise+reconverge-through-素, and a no-actionable-change send-back is
  arbiter clarification (no silent re-present). Cross-group panel re-runs only for new
  undispositioned risk; same/substantially-same risk uses the disagreement/escalation guardrail.
- **HOW:** Encode `flow.md` §F-1 send-back + bound prose.
- **验收:** No edge bypasses 素; no fixpoint re-present edge; bound tied to same-risk escalation.
- **状态:** done

#### R-P2-4 Gate-2 reopen `done`-row revalidation
- **编号:** R-P2-4
- **所属节点:** G2
- **WHY:** A `done` row invalidated by a sibling `todo` change must not ride a relock stale.
- **WHAT:** Before relocking a partially-built baseline, 玄+素 check each carried `done` row
  against changed/new `todo` rows for dependency/assumption impact; impacted rows return to
  `pending`/`todo`; record the check in `decisions.md`.
- **HOW:** Add the reopen precondition to the Phase 2 / Gate 2 prose.
- **验收:** Precondition present; recovery-inspects-atomic-rows caveat noted.
- **状态:** done

### G3 · `protocol.md` — Restart Recovery update

#### R-RR-1 Recovery references the full lifecycle set
- **编号:** R-RR-1
- **所属节点:** G3 Restart Recovery
- **WHY:** The recovery checklist predates `todo`/`blocked` and names a stale subset.
- **WHAT:** Update the Restart Recovery step that reads `requirements.md` to reference the full
  lifecycle set (`pending/todo/doing/done/blocked`) per the canonical section, not `pending`/
  `doing` only.
- **HOW:** Edit the Restart Recovery section of `protocol.md`.
- **验收:** Step references the canonical set / lifecycle section, no two-state subset remains.
- **状态:** done

#### R-RR-2 In-flight invariant preservation on restart
- **编号:** R-RR-2
- **所属节点:** G3
- **WHY:** In-flight loop position is not a row status (all read `pending`); a restart could
  present an un-challenged draft, violating the hard invariant.
- **WHAT:** On restart, 玄 treats 素's challenge/convergence for a group as not-done unless
  evidenced in `channel.md`/`decisions.md`; when in doubt, re-confirm with 素 (re-run challenge)
  before presenting. This is the **canonical** rule; the 玄-side operational duty is R-XU-3.
- **HOW:** Add the conservative rule to `protocol.md` Restart Recovery.
- **验收:** Canonical rule present in `protocol.md`; conservative default is re-challenge, never
  present-unverified. (The role-duty half is verified by R-XU-3.)
- **状态:** done

### G4 · `prompts/xuan.md` — 玄 duties

#### R-XU-1 Phase 2 duty: draft → 素 before arbiter
- **编号:** R-XU-1
- **所属节点:** G4
- **WHY:** Encode the hard invariant in 玄's own contract.
- **WHAT:** 玄's Phase 2 duty states: draft decomposition → send to 素 for challenge → converge
  → only then present WHY/WHAT to the arbiter.
- **HOW:** Edit the Phase Duties / Phase 2 row in `xuan.md`.
- **验收:** Duty wording present; order explicit.
- **状态:** todo

#### R-XU-2 Status duty references canonical (no enumeration; operational mentions tagged)
- **编号:** R-XU-2
- **所属节点:** G4
- **WHY:** Role prompts must not become a drift surface (mirrors R-SU-2 for `xuan.md`).
- **WHAT:** 玄's status-update duty points to the canonical lifecycle in `protocol.md` by name
  and does not re-enumerate the state set; any state named operationally carries a "per the
  Requirement Status Lifecycle in `protocol.md`" tag; live-row observation is information-only,
  not definitional.
- **HOW:** Edit `xuan.md`.
- **验收:** No local state-set enumeration; any operational state mention carries the canonical
  tag; observation framed as information-only.
- **状态:** todo

#### R-XU-3 Restart duty: verify 素 challenge before presenting
- **编号:** R-XU-3
- **所属节点:** G4
- **WHY:** 玄 is the actor presenting after a restart; the canonical rule (R-RR-2) needs an
  operational duty in 玄's own contract so a restarted 玄 doesn't miss it.
- **WHAT:** After a restart, before presenting an in-flight Phase 2 group's WHY/WHAT to the
  arbiter, 玄 must verify evidence of 素's challenge/convergence (in `channel.md`/`decisions.md`)
  or re-confirm with 素.
- **HOW:** Add the duty to `xuan.md` (Phase 2 / restart duty).
- **验收:** Duty present in `xuan.md`; ties to the canonical R-RR-2 rule; default is re-confirm.
- **状态:** todo

### G5 · `prompts/su.md` — 素 duties

#### R-SU-1 Challenge + restart duties reference canonical
- **编号:** R-SU-1
- **所属节点:** G5
- **WHY:** Same drift-prevention; 素's restart checklist must use the full set.
- **WHAT:** 素's Phase 2 challenge duty and restart checklist reference the canonical lifecycle
  in `protocol.md`.
- **HOW:** Edit `su.md`.
- **验收:** References present.
- **状态:** todo

#### R-SU-2 Operational state mentions are tagged
- **编号:** R-SU-2
- **所属节点:** G5
- **WHY:** A partial operational list (e.g. omitting `done`) is a drift surface.
- **WHAT:** Any state named operationally (e.g. "surface `doing`/`blocked` rows") carries a
  "per the Requirement Status Lifecycle in `protocol.md`" tag, marking it illustration not
  definition.
- **HOW:** Edit `su.md`.
- **验收:** Any operational state mention carries the canonical tag.
- **状态:** todo

### G6 · `templates/requirements.md` — pointer + sentinels + diagram + note

#### R-TM-1 Lifecycle reference block + atomic default (selftest-anchored)
- **编号:** R-TM-1
- **所属节点:** G6
- **WHY:** A copied standalone requirements file must be self-sufficient yet non-authoritative,
  and selftest needs stable anchors. (This is the row R-ST-1 asserts.)
- **WHAT:** Template embeds three HTML sentinels with content: `<!-- rt-lifecycle-pointer -->`
  (one-line pointer to the protocol canonical section by name), `<!-- rt-lifecycle-diagram -->`
  (compact `pending → todo → doing → done`, `blocked` as `doing → blocked → doing`),
  `<!-- rt-lifecycle-note -->` ("group status derived, atomic rows authoritative"); and the
  atomic-requirement default status is `pending`.
- **HOW:** Edit `templates/requirements.md` format section + add the three sentinels with content.
- **验收:** All three sentinels present with the specified content; atomic-requirement default
  status is `pending` at a stable anchor (e.g. `- **状态:** pending`). (Verified by R-ST-1.)
- **状态:** todo

#### R-TM-2 Template table/default consistency (review-verified)
- **编号:** R-TM-2
- **所属节点:** G6
- **WHY:** The template currently defaults groups to `todo` while atomic rows are `pending` — a
  self-contradiction; the legend predates the canonical lifecycle.
- **WHAT:** Reconcile the 拆解清单 group-table defaults and Pending/Status examples to the rollup
  rule (a fresh group with all-`pending` atomic rows rolls up `pending`); update the legend to
  reference the canonical lifecycle; remove the group-vs-atomic contradiction.
- **HOW:** Edit `templates/requirements.md` header legend + group-table example rows.
- **验收:** Group-table defaults consistent with the rollup rule; legend references the canonical
  lifecycle; no contradiction between group and atomic defaults. (Review-verified, not selftest.)
- **状态:** todo

### G7 · `bin/roundtable` — selftest drift guard

#### R-ST-1 Selftest asserts sentinels + default + pointer-target
- **编号:** R-ST-1
- **所属节点:** G7
- **WHY:** Make drift protection selftest-backed, not grep-only (Gate 0 decision #4, stronger
  form).
- **WHAT:** After `cmd_init`, `cmd_selftest` asserts — in the **initialized project paths** —
  the three `rt-lifecycle-*` sentinels and the atomic default in `$design/requirements.md`, and
  the canonical-section heading in `$rt/prompts/protocol.md` (the copied runtime protocol, not an
  ambiguous repo-root path). All checks use exact stable strings.
- **HOW:** Add `grep -q` assertions reusing the existing init-output grep pattern: each of the
  three exact HTML sentinels and the exact protocol heading string; the atomic default via an
  exact anchor (e.g. `- **状态:** pending`), not a loose `pending` match.
- **验收:** `bin/roundtable selftest` fails if any of the three sentinels, the atomic-default
  anchor (in `$design/requirements.md`), or the canonical heading (in `$rt/prompts/protocol.md`)
  is missing/renamed; passes on the correct tree; `bash -n` clean. (Proves anchors-present +
  pointer-target-exists; does not prove cross-surface semantic agreement.)
- **状态:** todo

### G8 · `README.md` / `README.en.md` + historical annotation

#### R-EX-1 README workflow line + historical annotation
- **编号:** R-EX-1
- **所属节点:** G8
- **WHY:** README teaches the workflow; the stale final-form diagram should point forward.
- **WHAT:** Update the Phase-2 workflow line in `README.md` + `README.en.md` to mention
  "challenged/converged before arbiter confirmation"; add a one-line note on
  `docs/design/front-end-pipeline-final-form.md` marking its `状态:todo→doing→done` diagram as
  historical v2-build evidence superseded by the canonical lifecycle in `protocol.md`.
- **HOW:** Edit the two READMEs and add the annotation line.
- **验收:** Both READMEs updated consistently (zh/en convention preserved); annotation present;
  the historical diagram itself not retro-edited.
- **状态:** todo

## 7. Constraints & assumptions

- Zero third-party dependency; engine stays minimal (only the selftest assertion changes code).
- Single source of truth: canonical lifecycle in `protocol.md`; all else references/derives.
- Build-sequencing note (non-binding, for Phase 3 `/ce-plan`; refined with 素):
  1. `prompts/protocol.md`: R-LC-*, R-P2-*, R-RR-* in one coherent edit (canonical section must
     exist before anything references it).
  2. `prompts/xuan.md` + `prompts/su.md`: role-prompt references (incl. R-XU-3 restart duty)
     after the canonical section exists.
  3. `templates/requirements.md` (R-TM-1 sentinels/default, R-TM-2 table consistency) +
     `bin/roundtable` (R-ST-1): sentinels first, then the selftest in the same or adjacent
     commit so the test never expects anchors that do not yet exist.
  4. `README.md`, `README.en.md`, and the `front-end-pipeline-final-form.md` annotation
     (R-EX-1): informational mirrors last.

## 8. Panel / review notes

Phase-1 panel already hardened the design (see `decisions.md`). A Phase-2 panel is only needed
if a specific requirement turns out high-risk/cross-node during 素's challenge.

| Requirement id | Lens | Finding | Disposition | Rationale |
|---|---|---|---|---|
| — | — | (none yet) | — | — |

## 9. Open questions

Gate 2 requires this resolved/empty.

| Question | Affected req | Owner | Status |
|---|---|---|---|
| (none yet) | — | — | — |
