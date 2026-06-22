---
title: Evolving a live "files-as-memory" agent protocol — rename and relocate without downtime
date: 2026-06-22
category: docs/solutions/design-patterns
module: bin/roundtable
problem_type: design_pattern
component: tooling
severity: medium
applies_when:
  - Renaming user-facing identities (roles, labels) that also appear in a transport/control plane
  - A concern-sliced work list whose edits converge on one or two physical files
  - Relocating a control-plane file that a running session is actively reading
  - A multi-agent loop edits the very contracts/config it runs under
  - Writing consistency sweeps where a failed command could masquerade as a clean pass
tags: [agent-protocol, rename, migration, files-as-memory, atomic-commit, backward-compat, verification, zsh]
---

# Evolving a live "files-as-memory" agent protocol — rename and relocate without downtime

## Context

`roundtable` is a tiny multi-agent harness: a phase-agnostic relay (`bin/relay.py`)
moves mailbox messages between two CLI panes, a bash orchestrator (`bin/roundtable`)
builds the tmux workbench, and the *actual* workflow lives in prompt contracts
(`prompts/`) + templates. Its design invariants are "files are memory; the engine
stays minimal; the relay is phase-agnostic."

The v2 build had to (a) rename the two roles `lead`/`impl` → `玄`/`素`, (b) relocate
design artifacts (`requirements.md`/`decisions.md`) from a gitignored `.roundtable/`
to a tracked `docs/design/roundtable/`, and (c) rewrite the shared contract — **all
while a live roundtable session was dogfooding the build**. Four reusable patterns
came out of doing this without breaking the running loop. They generalize to any
system where identities span a UI/transport boundary, where work converges on shared
files, or where a live process reads files you are migrating.

## Guidance

### 1. Split "wire/control-plane" labels from "display/contract" labels (the a+ cut)

When a name appears in *both* a user-facing surface and a transport/control plane,
do not pick "rename everything" or "rename nothing." Cut between the two:

- **Wire/control-plane labels** (kept stable): mailbox filenames, message-header
  values, env var names (`LEAD_PANE`/`IMPL_PANE`), relay route keys, transcript
  headers, and legacy CLI arguments. These are an ABI; churning them ripples into
  the parts you promised to keep minimal.
- **Display/contract labels** (renamed): contract filenames, kickoff text, README,
  banners, pane titles — everything a human or an agent reads as *role vocabulary*.

Map between them in one place (`lead→玄`, `impl→素`) and add `xuan|su` as the new
CLI alias with `lead|impl` retained as a legacy alias. Crucially, make the
**consistency check allowlist-based**: it must not demand zero occurrences of the old
token — it must demand the old token appears *only* in annotated wire surfaces.

### 2. Batch by physical sink, not by concern; make rename↔wiring atomic

A work list sliced by *concern* (12 items here) can still converge on one *physical
sink* (`protocol.md` + two role contracts). Editing concern-by-concern rewrites the
same file N times and thrashes. Batch by the file the writes land in: isolated
templates first → the shared contract written whole in one pass → outward docs last.

A rename that the engine references must land **atomically with the engine rewiring**.
`git mv prompts/lead.md prompts/xuan.md` while `cmd_init`/`_kickoff_text` still point
at `prompts/lead.md` leaves every intermediate commit unable to `init`/`start`. One
commit moves the file *and* repoints every reference.

### 3. Relocate a live control-plane file with copy-forward + frozen mirror + recovery fallback

Moving a file a running session is reading is the riskiest step. The safe recipe:

1. **Copy-forward, not move** — when the source is gitignored you cannot `git mv` it
   into tracking; copy its current content (preserving live state) to the new tracked
   path.
2. **Freeze the old copy as a legacy mirror** — stop updating it; the new path becomes
   the single maintained authority. A frozen mirror can never be read as a *stale*
   primary.
3. **Recovery reads new-primary with old-fallback** — restart logic reads the new path
   first and falls back to the legacy path (then migrates) only when the new one is
   absent. New installs follow the new model; old installs don't break on upgrade.

Corollary for self-modifying loops: a running agent operates on its *in-memory*
contract, so a mid-build rewrite of the contract files is safe — the new contract
becomes authoritative only on the next restart (which re-reads the files). Don't
assume the rewrite changes the current session's behavior.

### 4. A sweep that finds nothing must be distinguishable from a sweep that failed to run

A consistency grep used an unquoted `$FILES` variable. **zsh does not word-split
unquoted variables** (unlike bash), so the whole list became one non-existent
filename; paired with `|| echo "clean ✓"`, the failed command printed a false pass.
Verification that can silently no-op is worse than no verification — it manufactures
confidence. Use `${=VAR}`, an array, or a literal file list; and never let a check's
error path render as success.

## Why This Matters

The expensive failures here are silent: a renamed file the relay still nudges toward
(every future handoff points at a missing file), an intermediate commit that bricks
`start`, a restart that reads a stale primary, or a "clean" sweep that never ran. Each
pattern converts a silent failure into either an impossible state (atomic commit) or a
loud, locatable one (allowlist annotation, fallback path, fail-distinct verification).

## When to Apply

- Any rename of an identity that is simultaneously a UI label and a transport token.
- Any multi-item plan where two or more items edit the same file — batch by sink.
- Any relocation of state a live process reads — copy-forward + fallback, never a bare move.
- Any "did we get them all?" sweep — make the empty result provably a real scan.

## Examples

**a+ token split (relay nudge), display-only — routing keys unchanged:**

```python
# wire role stays lead/impl; only the displayed contract filename maps
def _contract_for_wire_role(role: str) -> str:
    return {"lead": "xuan.md", "impl": "su.md"}.get(role, f"{role}.md")
# nudge: f"act per .roundtable/prompts/{_contract_for_wire_role(to)}"
```

**Recovery fallback (new primary, legacy fallback) in the contract:**

```text
Restore state from docs/design/roundtable/requirements.md. If it is missing but
legacy .roundtable/requirements.md exists, use the legacy file once and migrate it
before continuing. After migration, docs are authoritative.
```

**Verification that can't fake a pass (zsh):**

```bash
# WRONG (zsh): $FILES is one arg; grep errors; `|| echo clean` lies
grep -nw 'lead|impl' $FILES || echo "clean ✓"
# RIGHT: literal list (or ${=FILES} / an array); inspect real output
grep -rnEw 'lead|impl' README.md prompts/protocol.md templates/ \
  | grep -vEi 'wire|legacy|to-lead|to-impl|LEAD_PANE|IMPL_PANE|FROM:'
```
