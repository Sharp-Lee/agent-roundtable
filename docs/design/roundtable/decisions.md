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

## Notes

- The completed `docs/design/roundtable/requirements.md` (v2-build worklist, G1–G12 `done`)
  keeps its row statuses untouched; only its one-line legend wording is aligned to reference
  the canonical lifecycle (treated as in-scope wording alignment, not a separate decision).
- `templates/channel.md` is out of scope (names recovery sources only, no status vocabulary).
