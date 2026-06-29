# roundtable new Command Design

## Purpose

Add `roundtable new [dir]` as a first-class way to start a new idea round in the same project after
the previous idea has completed. The command productizes the manual backup-and-reset sequence that
is already documented for rare same-directory, unrelated tasks.

The command must preserve the core Roundtable rule: `roundtable start` resumes existing artifacts,
while `roundtable new` explicitly archives the current Roundtable memory and creates fresh Phase 0
state.

## User Experience

Primary command:

```bash
roundtable new [dir]
```

Expected behavior:

1. Resolve `dir`, defaulting to the current working directory.
2. Refuse to run if this project's tmux session is active.
3. Backup existing Roundtable state with a timestamp.
4. Remove the active Roundtable state.
5. Re-run the same initialization path as `roundtable init`.
6. Print the backup paths and the next step: `roundtable start`.

Optional convenience:

```bash
roundtable new --start [dir]
```

This performs the same archive/reset/init flow, then launches the workbench.

## Safety Rules

- Do not silently overwrite or delete state without first creating backups.
- Refuse to run while the derived or recorded session for the project is running; users must stop it
  with `roundtable stop` first.
- If a backup copy fails, abort before deleting anything.
- If no Roundtable state exists yet, `roundtable new` should behave like `roundtable init`, with a
  clear message that there was nothing to archive.
- Do not add a `--force` option in the first version.

## Backup Layout

Use a sortable timestamp, for example `YYYYmmddHHMMSS`.

- `docs/design/roundtable` -> `docs/design/_backup/roundtable.<stamp>`
- `.roundtable` -> `.roundtable-backup/roundtable.<stamp>`

Only backup paths that exist. The command should still initialize fresh state if one side is absent.

## Implementation Shape

- Add `cmd_new` to `bin/roundtable`.
- Reuse `_session_for` and the existing session detection behavior used by `start` and `stop`.
- Reuse `cmd_init` after archive/reset rather than duplicating scaffolding logic.
- Parse `--start` locally inside `cmd_new`; no broad option parser is needed.
- Update command lists in the script banner, usage output, popup tips, `README.md`, and
  `README.en.md`.

## Verification

Add selftest coverage for:

- `roundtable new` archives existing `docs/design/roundtable` and `.roundtable` state.
- `roundtable new` recreates fresh docs/runtime state via init.
- Existing content is present under the timestamped backup paths.
- `roundtable new` behaves like init when there is nothing to archive.
- `roundtable new` refuses to run while the project's session exists.

Manual smoke checks:

- `roundtable selftest`
- A temporary-project run of `roundtable init` and `roundtable new`.
- A guarded `roundtable new --start` smoke only with harmless `CLAUDE_CMD` / `CODEX_CMD` overrides,
  or skipped if that would disturb local CLI state.

## Out Of Scope

- No `--force` mode.
- No automatic deletion of old backups.
- No migration or merging between old and new idea rounds.
- No change to the semantics of `roundtable start`; it must continue to mean resume existing state.
