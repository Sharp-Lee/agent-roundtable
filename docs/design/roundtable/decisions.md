# Decisions log — roundtable: Phase 2 sequence + requirement status lifecycle

> Resolved disagreements and gate verdicts for this design effort. Keeps the roundtable from
> re-litigating settled points and gives a restarted pane the "why" behind choices.
> **Reset 2026-06-23** for the "Phase 2 internal sequence + requirement status lifecycle"
> project; prior entries (v2 pipeline build) are retired — see git history / `channel.md`.

| # | Question / decision | Decision | Rationale | Decided by | Phase |
|---|---------------------|----------|-----------|------------|-------|
| 1 | Gate 0 — direction lock for "Phase 2 internal sequence + requirement status lifecycle" | **Approved 🔒.** Direction per `.roundtable/_idea.md`: four-state main line `pending→todo→doing→done` + `blocked` as a `doing`-only exception; atomic rows authoritative, group status derived with conservative precedence; Phase 2 as an explicit per-group loop with the hard "素-challenges-before-arbiter-confirms" invariant and panel-before-confirmation; confirmation tracks WHY/WHAT only; canonical lifecycle in `protocol.md`, template carries pointer+diagram. Scope = contract/doc only; P0/P1/P3 behavior frozen. | 玄+素 converged on the full direction in Phase 0; arbiter approved without changes. Closes the two underspecified Phase-2 spots (no written order; status vocab drifted across 3 surfaces with an undefined post-confirmation state). | arbiter | 0 / Gate 0 |
| 2 | Scope-edge call: update the README (中/英) Phase-2 workflow line? | **Yes** — add "challenged/converged before arbiter confirmation" to the Phase-2 line in `README.md` + `README.en.md`. | Low cost; README teaches the workflow, so it should teach the now-clarified order. | arbiter (per 玄 rec) | 0 / Gate 0 |
| 3 | Scope-edge call: the stale `状态:todo→doing→done` diagram in `docs/design/front-end-pipeline-final-form.md` | **Mark historical** — add a one-line note that it is v2-build design evidence, superseded by the canonical lifecycle in `protocol.md`; do not retro-edit the diagram. | Same logic as not retro-editing completed `requirements.md` row statuses: preserve historical design evidence, point forward to the canonical source. | arbiter (per 玄 rec) | 0 / Gate 0 |
| 4 | Scope-edge call: add drift-protection selftest? | **Yes** — add a small `bin/roundtable selftest` template-content assertion (template defaults atomic status to `pending`; template contains the lifecycle pointer). This is the only code touch in an otherwise doc-only change. | This whole project exists to stop status drift; a tiny assertion makes drift protection selftest-backed instead of grep-only. | arbiter (per 玄 rec) | 0 / Gate 0 |
| 5 | Gate 1 — final-form lock (`architecture.md` + `flow.md`) | **Approved 🔒.** Final form per the two docs, including all Phase-1-panel hardenings (non-terminating send-back edge removed; cross-group panel bounded; Gate-2-reopen `done`-revalidation; restart preserves the hard invariant; `protocol.md` Restart Recovery in scope). **Decision #4 confirmed in its stronger form:** the drift selftest asserts stable sentinels (`<!-- rt-lifecycle-pointer/-diagram/-note -->`) + atomic `pending` default + a pointer-target check that `protocol.md` contains the canonical heading — superseding the lighter "pointer present" form. | 玄+素 converged on the final form; mandatory Phase-1 panel run and dispositioned (see below); arbiter approved and adopted the stronger selftest. | arbiter | 1 / Gate 1 |
| 6 | Gate 2 — detailed-requirements baseline lock | **Approved 🔒.** 8 groups / 19 atomic requirements, all arbiter-confirmed (WHY/WHAT) and `todo`; pending = 0; no open questions; no Phase 2 panel needed. `docs/design/roundtable/requirements.md` is the locked input for Phase 3. | 玄+素 converged on the decomposition; arbiter confirmed all 19 WHY/WHAT group-by-group and approved the baseline. | arbiter | 2 / Gate 2 |

## Notes

- The completed v2-build worklist previously at `docs/design/roundtable/requirements.md`
  (G1–G12 `done`) is preserved in git history (commit `37a1727`); this project's Phase-2
  baseline takes over that path. The earlier "align the completed worklist legend" item is
  therefore moot — the new baseline uses the canonical vocabulary from the start, and no row
  statuses were retro-edited.
- `templates/channel.md` is out of scope (names recovery sources only, no status vocabulary).

## Phase 1 panel disposition (2026-06-23)

One-shot internal panel, four lenses (feasibility, scope-creep, coherence/drift,
operational-reliability). Findings dispositioned by 玄; folded into `flow.md` / `architecture.md`.

**Accepted (folded in):**

- **Non-terminating send-back edge removed.** The "no artifact change → re-present to arbiter"
  branch was a ping-pong with no state change and bypassed 素. Removed; a send-back naming no
  actionable change is arbiter clarification, not a flow edge. (feasibility/scope/operational)
- **Cross-group panel bounded.** Repeated WHY/WHAT re-entries (`K→A→…→K`) had no stopping rule.
  Now: K re-runs only for new, undispositioned systemic risk; HOW/acceptance-only revisions go
  `N→L` (Gate 2), not back through K; repeated rediscovery/rejection of the **same** risk uses
  the standard disagreement/escalation guardrail. (operational + 素's churn probe)
- **Gate-2 reopen `done`-row revalidation.** A `done` row invalidated by a sibling `todo` change
  could ride the relock stale. Added a revalidation precondition + a mixed-rollup caveat (inspect
  atomic rows after any reopen). (operational)
- **Restart preserves the hard invariant.** In-flight loop position is not a row status (all read
  `pending`); added the conservative rule that on restart 玄 re-confirms 素's challenge before
  presenting, and put `protocol.md` Restart Recovery (full lifecycle set) in scope. (operational)
- **Selftest hardened and honestly scoped.** Stable sentinels (`<!-- rt-lifecycle-* -->`) + a
  pointer-target-exists check against `protocol.md`; documented that it guards template-presence
  + pointer-resolves, not cross-surface agreement. (feasibility/coherence)
- **Role-prompt state mentions tagged.** Any operationally-named state must carry "per the
  Requirement Status Lifecycle in `protocol.md`"; observation of live rows is information-only.
  (coherence)
- Minor clarity: labeled the send-back state-machine edge; marked "not yet decomposed" as a
  transient display state.

**Rejected:**

- Editing the locked `.roundtable/_idea.md` §C/§D to mirror flow.md's HOW/acceptance shortcut
  (coherence #7). Rationale: `_idea.md` is the locked Gate-0 direction (intentionally
  higher-level); `flow.md` is the authoritative Phase-1 elaboration. Editing a locked artifact to
  mirror downstream detail is exactly what locking exists to prevent. **`flow.md` is authoritative
  over `_idea.md` for Phase-2 loop detail.**

**Needs arbiter confirmation at Gate 1:** Gate 0 decision #4 (drift-protection selftest) is
broadened from "pending default + pointer present" to "sentinel-based template guard +
pointer-target check." In-spirit, but flagged explicitly.

**In-scope additions (no Gate 0 reopen — same already-approved files):** `protocol.md` Restart
Recovery + Phase-2 in-flight rule; the cross-group-panel bound. No new files/surfaces.
