# Named Idea Worktree Design

## Purpose

Add named idea support so each idea gets its own git worktree, branch, Roundtable state, design
artifacts, code changes, and tmux session.

This replaces the earlier archive-and-reset concept. A new idea should not overwrite or backup the
current `.roundtable/` and `docs/design/roundtable/` state in the same directory. It should create a
separate sibling worktree, initialize Roundtable there, and run all agent work from that worktree.

The existing no-name commands remain compatible:

```bash
rt init
rt start
rt stop
rt kickoff
```

They continue to operate on the current directory exactly as they do today.

## User Model

`name` is an idea slug chosen by the user.

```bash
rt new foo
rt start foo
rt stop foo
```

For a repo at:

```text
/Users/wukong/mylife/agent-roundtable
```

`rt new foo` creates a sibling worktree by default:

```text
/Users/wukong/mylife/agent-roundtable.foo
```

All work for idea `foo` happens inside that worktree:

- code edits
- commits
- `.roundtable/` runtime state
- `docs/design/roundtable/` design artifacts
- tmux session
- relay mailbox traffic

The base checkout remains untouched except for normal git worktree metadata.

## Commands

### `rt new <name>`

Create a new named idea worktree.

Expected behavior:

1. Validate `name` as a safe slug.
2. Resolve the source repo from the current directory.
3. Refuse if the source worktree has uncommitted tracked changes, because the new idea starts from
   the current `HEAD`, not from dirty working-tree state.
4. Refuse to run if the destination worktree path already exists.
5. Create a new branch for the idea from the current `HEAD`.
6. Create a sibling git worktree at `../<repo>.<name>`.
7. Run `rt init` inside that worktree.
8. Print the worktree path and next step: `rt start <name>`.

The command does not start tmux by default.

### `rt new --start <name>`

Create the worktree, initialize it, then start Roundtable from that worktree.

This is a convenience path only; it must have the same validation and safety checks as `rt new`.

### `rt init [name]`

Without `name`, keep current behavior.

With `name`, initialize the named worktree if it already exists. If the named worktree does not
exist, return a clear error telling the user to run `rt new <name>` first.

### `rt start [name]`

Without `name`, keep current behavior.

With `name`, resolve the named worktree path and start Roundtable from that directory. The tmux
session name should be derived from the worktree path, so concurrent ideas can run independently.

### `rt stop [name]` and `rt kickoff [name]`

Without `name`, keep current behavior.

With `name`, resolve the named worktree path and operate on that worktree's recorded session and
pane state.

## Branch And Path Defaults

Default branch name:

```text
codex/<name>
```

Default worktree path:

```text
../<repo>.<name>
```

Example:

```text
repo:      /Users/wukong/mylife/agent-roundtable
name:      new-command
branch:    codex/new-command
worktree:  /Users/wukong/mylife/agent-roundtable.new-command
```

The first version should not add custom branch or path flags. Keeping the contract narrow makes the
command easier to reason about and test.

## Name Validation

Accept only slugs that are safe for branch and path construction:

```text
[A-Za-z0-9][A-Za-z0-9._-]*
```

Reject names containing path separators, spaces, shell metacharacters, leading dots, or empty
strings.

## Safety Rules

- Do not create a worktree unless the current directory is inside a git worktree.
- Refuse if the target branch already exists.
- Refuse if the target worktree path already exists.
- Refuse `rt start <name>` / `rt stop <name>` / `rt kickoff <name>` if the named worktree cannot be
  resolved.
- Do not delete or modify existing idea worktrees.
- Do not change the semantics of no-name commands.
- Do not add `--force` in the first version.

## Worktree Resolution

For `rt start <name>`, `rt stop <name>`, `rt kickoff <name>`, and `rt init <name>`, resolve the
named worktree deterministically:

1. If the current git worktree path already ends in `.<name>`, use the current worktree.
2. Otherwise resolve the default sibling path from the current worktree root:

```text
../<repo>.<name>
```

This allows both of these to work:

```bash
cd /path/to/repo && rt start foo
cd /path/to/repo.foo && rt start foo
```

A later version can add a registry if users need custom paths or need to resolve names from inside
another named idea worktree.

## Implementation Shape

- Add `cmd_new`.
- Add a small `_validate_idea_name` helper.
- Add a `_repo_root` helper based on `git rev-parse --show-toplevel`.
- Add a `_source_is_clean` helper that checks tracked changes before `rt new`.
- Add a `_worktree_for_name` helper that first recognizes the current `.<name>` worktree, then uses
  the repo root basename plus `.<name>`.
- Reuse `cmd_init` inside the created worktree.
- Update `cmd_start`, `cmd_stop`, and `cmd_kickoff` to accept an optional idea name and resolve it
  to the target worktree before using the existing logic.
- Keep the relay and prompt contracts unchanged; they operate inside whichever worktree started the
  session.
- Update command lists in the script banner, usage output, popup tips, `README.md`, and
  `README.en.md`.

## Verification

Add selftest coverage for:

- name validation accepts safe slugs and rejects unsafe names.
- `rt new <name>` refuses when the source worktree has uncommitted tracked changes.
- `rt new <name>` creates the expected branch and sibling worktree.
- the new worktree contains fresh `.roundtable/` and `docs/design/roundtable/` state.
- the source worktree's existing `.roundtable/` and `docs/design/roundtable/` state are not
  modified.
- `rt init <name>` initializes an existing named worktree.
- `rt start <name>` derives a different session from the named worktree path.
- no-name `rt init`, `rt start`, `rt stop`, and `rt kickoff` behavior remains compatible.

Manual smoke checks:

- `roundtable selftest`
- temporary-repo `rt new sample`
- temporary-repo `rt init sample`
- temporary-repo `CLAUDE_CMD=true CODEX_CMD=true rt new --start sample2`, guarded so real CLIs are
  not launched.

## Out Of Scope

- No custom worktree path flag.
- No custom branch flag.
- No `--force`.
- No automatic cleanup or deletion of idea worktrees.
- No registry of named ideas.
- No change to Roundtable phase, gate, mailbox, or relay semantics.
