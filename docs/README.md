# Documentation Map

This repository has four documentation layers. Use this map to avoid confusing current contracts
with historical design evidence or implementation-process notes.

## Current Operating Contract

These files define what Roundtable does now:

- `README.md` / `README.en.md` - user-facing overview, commands, workflow, and recovery model.
- `prompts/protocol.md` - canonical shared protocol for 玄 and 素.
- `prompts/xuan.md` - 玄's fixed process duties.
- `prompts/su.md` - 素's fixed process duties.
- `templates/` - initialized design and runtime templates copied by `roundtable init`.
- `bin/roundtable` and `bin/relay.py` - CLI orchestration and mailbox relay.

## Current Design Baseline

These are the current tracked Roundtable design artifacts:

- `docs/design/roundtable/architecture.md`
- `docs/design/roundtable/flow.md`
- `docs/design/roundtable/requirements.md`
- `docs/design/roundtable/decisions.md`

They are the source to inspect when checking why the current protocol or CLI behavior exists.

## Historical Design Evidence

These files are retained as historical evidence from the 2026-06-22 front-end design pipeline
work. They are not the current authoritative contract:

- `docs/design/front-end-pipeline-final-form.md`
- `docs/design/front-end-pipeline-requirements.md`
- `docs/design/front-end-pipeline-build-worklist.md`

When they disagree with current files, prefer `prompts/protocol.md`,
`prompts/xuan.md`, `prompts/su.md`, and `docs/design/roundtable/*`.

## Implementation Process Notes

These files document how specific changes were designed or implemented. They are useful for audit
and future maintenance, but they are not runtime protocol:

- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

## Durable Learnings

These files capture reusable engineering patterns discovered while building the project:

- `docs/solutions/design-patterns/`

## Runtime State

Runtime state is intentionally ignored by git:

- `.roundtable/`
- `.worktrees/`
- `.understand-anything/`
- Python cache files

Do not treat runtime state as the durable source of truth unless a protocol explicitly says to read
it for restart recovery.
