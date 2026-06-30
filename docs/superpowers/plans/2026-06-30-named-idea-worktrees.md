# Named Idea Worktrees Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `rt new <name>` plus named `init/start/stop/kickoff` routing so each idea runs from its own sibling git worktree.

**Architecture:** Keep the existing single-file Bash CLI structure. Add small helper functions for idea-name validation, repo/worktree resolution, branch safety, and tracked-clean checks, then route named commands to the resolved worktree before reusing the existing init/start/stop/kickoff behavior. Preserve legacy path arguments by treating arguments with `/` or existing directory paths as directory targets; safe bare slugs are idea names.

**Tech Stack:** Bash, git worktree, tmux, Python stdlib relay, existing `roundtable selftest`.

---

## File Map

- Modify `bin/roundtable`: add worktree helpers, `cmd_new`, named argument routing for `cmd_init`, `cmd_start`, `cmd_stop`, `cmd_kickoff`, popup/usage text, and selftest coverage.
- Modify `README.md`: document named idea worktrees and update command table.
- Modify `README.en.md`: English version of the same command and lifecycle documentation.
- No new runtime files are required; `rt new <name>` creates sibling worktrees at runtime.

## Compatibility Rule

Use this argument interpretation throughout the implementation:

- No argument: current behavior using `$PWD`.
- Argument containing `/` or resolving to an existing directory: legacy directory target.
- Safe bare slug: named idea worktree.
- Unsafe bare string: error with the slug rule.

This preserves `roundtable start /path/to/project` while enabling `roundtable start foo`.

### Task 1: Add Name And Worktree Helper Tests

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Add selftest assertions for name validation**

In `cmd_selftest`, after the `xuan alias maps to lead wire role` and `su alias maps to impl wire role` assertions, add the planned assertions before implementing the helpers:

```bash
  if _validate_idea_name "alpha-1_ok.name"; then
    _selftest_pass "idea name validation accepts safe slug"
  else
    _selftest_fail "idea name validation accepts safe slug" || true; rc=1
  fi
  if _validate_idea_name ".hidden" || _validate_idea_name "bad/name" || _validate_idea_name "bad name"; then
    _selftest_fail "idea name validation rejects unsafe slugs" || true; rc=1
  else
    _selftest_pass "idea name validation rejects unsafe slugs"
  fi
```

- [ ] **Step 2: Run selftest and verify it fails**

Run:

```bash
./bin/roundtable selftest
```

Expected: FAIL or shell error mentioning `_validate_idea_name` because the helper does not exist yet.

- [ ] **Step 3: Add helper functions after `_session_for`**

Insert these helpers immediately after `_session_for()`:

```bash
_validate_idea_name() {
  local name="${1:-}"
  [[ "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || return 1
  [[ "$name" != .* ]] || return 1
  [[ "$name" != *"/"* ]] || return 1
}

_repo_root() {
  git -C "${1:-$PWD}" rev-parse --show-toplevel 2>/dev/null
}

_source_is_clean() {
  local root="$1"
  [ -z "$(git -C "$root" status --porcelain --untracked-files=no)" ]
}

_branch_exists() {
  local root="$1" branch="$2"
  git -C "$root" show-ref --verify --quiet "refs/heads/$branch"
}

_looks_like_dir_arg() {
  local arg="${1:-}"
  [ -n "$arg" ] || return 1
  [[ "$arg" == */* ]] || [ -d "$arg" ]
}

_worktree_for_name() {
  local name="$1" root base parent
  _validate_idea_name "$name" || die "invalid idea name '$name' (use [A-Za-z0-9][A-Za-z0-9._-]*; no leading dot, spaces, or slashes)"
  root="$(_repo_root "$PWD")" || die "not inside a git worktree"
  base="$(basename "$root")"
  if [[ "$base" == *".$name" ]]; then
    printf '%s\n' "$root"
    return 0
  fi
  parent="$(dirname "$root")"
  printf '%s/%s.%s\n' "$parent" "$base" "$name"
}

_target_from_arg() {
  local arg="${1:-}"
  if [ -z "$arg" ]; then
    printf '%s\n' "$PWD"
  elif _looks_like_dir_arg "$arg"; then
    cd "$arg" && pwd
  else
    _worktree_for_name "$arg"
  fi
}
```

- [ ] **Step 4: Run selftest and verify helper tests pass**

Run:

```bash
./bin/roundtable selftest
```

Expected: the new validation assertions pass; existing failures are not expected.

- [ ] **Step 5: Commit helper tests and helpers**

Run:

```bash
git add bin/roundtable
git commit -m "feat: add idea worktree helpers"
```

### Task 2: Implement `rt new <name>`

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Add selftest setup for temporary git repo**

In `cmd_selftest`, add local variables near the current local declaration:

```bash
  local git_proj git_wt git_name git_branch git_src_sentinel git_wt_sentinel
```

After `cmd_init "$legacy_proj" >/dev/null`, create a throwaway git repo:

```bash
  git_proj="$(mktemp -d)"
  git -C "$git_proj" init -q
  git -C "$git_proj" config user.email selftest@example.invalid
  git -C "$git_proj" config user.name "Roundtable Selftest"
  printf 'source sentinel\n' > "$git_proj/source.txt"
  git -C "$git_proj" add source.txt
  git -C "$git_proj" commit -q -m "init selftest repo"
  cmd_init "$git_proj" >/dev/null
  printf 'source idea sentinel\n' > "$git_proj/.roundtable/_idea.md"
  printf 'source requirements sentinel\n' > "$git_proj/docs/design/roundtable/requirements.md"
  git_name="sample"
  git_branch="codex/$git_name"
  git_wt="$(dirname "$git_proj")/$(basename "$git_proj").$git_name"
```

- [ ] **Step 2: Add failing selftest assertions for `cmd_new`**

Still in `cmd_selftest`, after the name validation assertions, add:

```bash
  if (cd "$git_proj" && cmd_new "$git_name" >/dev/null); then
    _selftest_pass "new creates named idea worktree"
  else
    _selftest_fail "new creates named idea worktree" || true; rc=1
  fi
  _selftest_assert_file "new worktree has runtime state" "$git_wt/.roundtable/_idea.md" || rc=1
  _selftest_assert_file "new worktree has docs requirements" "$git_wt/docs/design/roundtable/requirements.md" || rc=1
  if git -C "$git_proj" show-ref --verify --quiet "refs/heads/$git_branch"; then
    _selftest_pass "new creates idea branch"
  else
    _selftest_fail "new creates idea branch" || true; rc=1
  fi
  if grep -q "source idea sentinel" "$git_proj/.roundtable/_idea.md" &&
     grep -q "source requirements sentinel" "$git_proj/docs/design/roundtable/requirements.md" &&
     ! grep -q "source idea sentinel" "$git_wt/.roundtable/_idea.md" &&
     ! grep -q "source requirements sentinel" "$git_wt/docs/design/roundtable/requirements.md"; then
    _selftest_pass "new keeps source roundtable state isolated"
  else
    _selftest_fail "new keeps source roundtable state isolated" || true; rc=1
  fi
```

Update the cleanup near the end:

```bash
  git -C "$git_proj" worktree remove --force "$git_wt" >/dev/null 2>&1 || true
  rm -rf "$proj" "$legacy_proj" "$git_proj" "$git_wt"
```

- [ ] **Step 3: Run selftest and verify it fails**

Run:

```bash
./bin/roundtable selftest
```

Expected: FAIL or shell error mentioning `cmd_new`.

- [ ] **Step 4: Implement `cmd_new` before `cmd_init`**

Add:

```bash
cmd_new() {
  local start_after=0 name="${1:-}"
  if [ "$name" = "--start" ]; then
    start_after=1
    shift
    name="${1:-}"
  fi
  [ -n "$name" ] || die "usage: roundtable new [--start] <name>"
  [ "$#" -eq 1 ] || die "usage: roundtable new [--start] <name>"
  _validate_idea_name "$name" || die "invalid idea name '$name' (use [A-Za-z0-9][A-Za-z0-9._-]*; no leading dot, spaces, or slashes)"

  local root branch wt
  root="$(_repo_root "$PWD")" || die "not inside a git worktree"
  _source_is_clean "$root" || die "source worktree has uncommitted tracked changes; commit or stash before 'roundtable new $name'"
  branch="codex/$name"
  _branch_exists "$root" "$branch" && die "branch '$branch' already exists"
  wt="$(_worktree_for_name "$name")"
  [ ! -e "$wt" ] || die "worktree path already exists: $wt"

  git -C "$root" worktree add -b "$branch" "$wt" HEAD
  cmd_init "$wt"
  echo "Created idea '$name'"
  echo "Branch:   $branch"
  echo "Worktree: $wt"
  if [ "$start_after" -eq 1 ]; then
    cmd_start "$wt"
  else
    echo "Next:     roundtable start $name"
  fi
}
```

- [ ] **Step 5: Wire `new` into command dispatch**

In `main()`, add:

```bash
    new)      cmd_new      "$@" ;;
```

Add `new` to both usage blocks and `_popup_tips_text`:

```text
  rt new <name>          create a named idea worktree
```

- [ ] **Step 6: Run selftest and verify `new` passes**

Run:

```bash
./bin/roundtable selftest
```

Expected: PASS, including `new creates named idea worktree`, `new creates idea branch`, and source isolation assertions.

- [ ] **Step 7: Commit `new` command**

Run:

```bash
git add bin/roundtable
git commit -m "feat: create named idea worktrees"
```

### Task 3: Route Named `init`, `start`, `stop`, And `kickoff`

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Add target resolution tests**

In `cmd_selftest`, after the `new` assertions, add:

```bash
  if (cd "$git_proj" && [ "$(_target_from_arg "$git_name")" = "$git_wt" ]); then
    _selftest_pass "name argument resolves to sibling worktree"
  else
    _selftest_fail "name argument resolves to sibling worktree" || true; rc=1
  fi
  if (cd "$git_wt" && [ "$(_target_from_arg "$git_name")" = "$git_wt" ]); then
    _selftest_pass "name argument resolves to current named worktree"
  else
    _selftest_fail "name argument resolves to current named worktree" || true; rc=1
  fi
  if [ "$(_target_from_arg "$git_wt")" = "$git_wt" ]; then
    _selftest_pass "path argument remains legacy directory target"
  else
    _selftest_fail "path argument remains legacy directory target" || true; rc=1
  fi
```

- [ ] **Step 2: Run selftest and note current behavior**

Run:

```bash
./bin/roundtable selftest
```

Expected: target helper tests pass if Task 1 helpers are correct; command routing is not changed yet.

- [ ] **Step 3: Update `cmd_init` target resolution**

Replace the first two lines of `cmd_init`:

```bash
  local target="${1:-$PWD}"
  target="$(cd "$target" && pwd)" || die "no such directory: ${1:-$PWD}"
```

with:

```bash
  local target
  target="$(_target_from_arg "${1:-}")" || die "no such directory or named worktree: ${1:-$PWD}"
  [ -d "$target" ] || die "no such directory or named worktree: $target"
```

- [ ] **Step 4: Update `cmd_start` target resolution**

Replace the first two lines of `cmd_start`:

```bash
  local target="${1:-$PWD}"
  target="$(cd "$target" && pwd)" || die "no such directory: ${1:-$PWD}"
```

with:

```bash
  local target
  target="$(_target_from_arg "${1:-}")" || die "no such directory or named worktree: ${1:-$PWD}"
  [ -d "$target" ] || die "no such directory or named worktree: $target"
```

- [ ] **Step 5: Update `cmd_stop` target resolution**

Replace:

```bash
  local target="${1:-$PWD}"
  target="$(cd "$target" 2>/dev/null && pwd)" || target="$PWD"
```

with:

```bash
  local target
  target="$(_target_from_arg "${1:-}" 2>/dev/null || true)"
  [ -n "$target" ] || target="$PWD"
```

- [ ] **Step 6: Update `cmd_kickoff` to separate idea name from role**

Replace the beginning of `cmd_kickoff` through `local envfile=...` with:

```bash
cmd_kickoff() {
  local target="$PWD" only="both" first="${1:-}" second="${2:-}"
  if [ -n "$second" ]; then
    target="$(_target_from_arg "$first")" || die "no such named worktree: $first"
    only="$second"
  elif [ -n "$first" ]; then
    case "$first" in
      both|xuan|lead|su|impl) only="$first" ;;
      *) target="$(_target_from_arg "$first")" || die "no such named worktree: $first" ;;
    esac
  fi
  case "$only" in
    both) ;;
    xuan|lead) only="lead" ;;
    su|impl) only="impl" ;;
    *) die "usage: roundtable kickoff [name] [xuan|su|lead|impl]" ;;
  esac
  local envfile="$target/.roundtable/panes.env"
```

Keep the rest of `cmd_kickoff` unchanged.

- [ ] **Step 7: Run selftest**

Run:

```bash
./bin/roundtable selftest
```

Expected: PASS.

- [ ] **Step 8: Commit named command routing**

Run:

```bash
git add bin/roundtable
git commit -m "feat: route commands to named idea worktrees"
```

### Task 4: Add Running-Session Resolution Coverage

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Add selftest assertion for named session derivation**

In `cmd_selftest`, after target resolution tests, add:

```bash
  if [ "$(_session_for "$git_wt")" != "$(_session_for "$git_proj")" ]; then
    _selftest_pass "named worktree derives separate session"
  else
    _selftest_fail "named worktree derives separate session" || true; rc=1
  fi
```

- [ ] **Step 2: Add selftest assertion for dirty tracked changes refusal**

Before removing the git worktree in cleanup, create a second temporary git repo block after the main `new` assertions:

```bash
  local dirty_proj
  dirty_proj="$(mktemp -d)"
  git -C "$dirty_proj" init -q
  git -C "$dirty_proj" config user.email selftest@example.invalid
  git -C "$dirty_proj" config user.name "Roundtable Selftest"
  printf 'clean\n' > "$dirty_proj/file.txt"
  git -C "$dirty_proj" add file.txt
  git -C "$dirty_proj" commit -q -m "init dirty repo"
  printf 'dirty\n' > "$dirty_proj/file.txt"
  if (cd "$dirty_proj" && cmd_new dirty >/dev/null 2>&1); then
    _selftest_fail "new refuses dirty tracked source" || true; rc=1
  else
    _selftest_pass "new refuses dirty tracked source"
  fi
```

Update cleanup:

```bash
  rm -rf "$proj" "$legacy_proj" "$git_proj" "$git_wt" "$dirty_proj"
```

- [ ] **Step 3: Run selftest**

Run:

```bash
./bin/roundtable selftest
```

Expected: PASS, including separate session and dirty-source refusal assertions.

- [ ] **Step 4: Commit safety coverage**

Run:

```bash
git add bin/roundtable
git commit -m "test: cover named worktree safety"
```

### Task 5: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `bin/roundtable`

- [ ] **Step 1: Update command tables in both READMEs**

In `README.md`, update the command table to include:

```markdown
| `roundtable new <name>` | 为一个新 idea 创建 sibling git worktree，并在其中初始化 roundtable |
| `roundtable init [name\|dir]` | 初始化当前目录、已有 named worktree，或指定目录 |
| `roundtable start [name\|dir]` | 启动当前目录、named worktree，或指定目录的 玄/素/command/relay workbench |
| `roundtable kickoff [name] [xuan\|su]` | 对当前或 named worktree 重发 kickoff；`lead\|impl` 仅作 legacy wire 别名 |
| `roundtable stop [name\|dir]` | 停止当前、named worktree，或指定目录的 tmux 会话 |
```

In `README.en.md`, use:

```markdown
| `roundtable new <name>` | create a sibling git worktree for a new idea and initialize roundtable there |
| `roundtable init [name\|dir]` | initialize the current directory, an existing named worktree, or a directory path |
| `roundtable start [name\|dir]` | start the 玄/素/command/relay workbench for the current directory, named worktree, or directory path |
| `roundtable kickoff [name] [xuan\|su]` | re-send kickoff for the current or named worktree; `lead\|impl` are legacy wire aliases only |
| `roundtable stop [name\|dir]` | stop the tmux session for the current directory, named worktree, or directory path |
```

- [ ] **Step 2: Replace the old same-directory reset section**

In `README.md`, replace the section titled `在同一目录里开一个*不同的*、无关的任务（罕见）。` with text explaining:

````markdown
**开一个新的 idea。** 每个 idea 应该有自己的 git worktree：

```bash
roundtable new my-idea
roundtable start my-idea
```

默认会从当前 `HEAD` 创建 `codex/my-idea` 分支和 sibling worktree，例如
`../agent-roundtable.my-idea`。之后所有代码改动、Roundtable 记忆和 tmux session 都在这个 worktree
里。当前目录没有参数的 `roundtable start` 仍然表示恢复当前目录里的已有 Roundtable 状态。
````

In `README.en.md`, replace the corresponding "different unrelated task" section with:

````markdown
**Start a new idea.** Each idea should have its own git worktree:

```bash
roundtable new my-idea
roundtable start my-idea
```

By default this creates branch `codex/my-idea` from the current `HEAD` and a sibling worktree such
as `../agent-roundtable.my-idea`. Code changes, Roundtable memory, and the tmux session for that
idea all live in that worktree. Running `roundtable start` without a name still resumes the
Roundtable state in the current directory.
````

- [ ] **Step 3: Update CLI usage and tips text**

In `bin/roundtable`, update top comments, `_popup_tips_text`, and fallback usage to show:

```text
rt new <name>          create a named idea worktree
rt init [name|dir]     scaffold docs/design/roundtable/ + .roundtable/
rt start [name|dir]    launch the workbench
rt stop [name|dir]     stop this project's session
rt kickoff [name] [xuan|su] re-send kickoff prompts
```

- [ ] **Step 4: Run documentation grep checks**

Run:

```bash
rg -n "roundtable new|rt new|new <name>|start \\[name|init \\[name|kickoff \\[name" README.md README.en.md bin/roundtable
```

Expected: matches in both READMEs and CLI usage/tips.

- [ ] **Step 5: Run selftest**

Run:

```bash
./bin/roundtable selftest
```

Expected: PASS.

- [ ] **Step 6: Commit docs**

Run:

```bash
git add README.md README.en.md bin/roundtable
git commit -m "docs: document named idea worktrees"
```

### Task 6: Manual Smoke Verification

**Files:**
- No code changes expected.

- [ ] **Step 1: Create a temporary repo**

Run:

```bash
tmp="$(mktemp -d)"
git -C "$tmp" init
git -C "$tmp" config user.email smoke@example.invalid
git -C "$tmp" config user.name "Roundtable Smoke"
printf 'smoke\n' > "$tmp/README.md"
git -C "$tmp" add README.md
git -C "$tmp" commit -m "init smoke"
```

Expected: commit succeeds.

- [ ] **Step 2: Smoke `rt new sample`**

Run:

```bash
(cd "$tmp" && /Users/wukong/mylife/agent-roundtable/bin/roundtable new sample)
test -d "$(dirname "$tmp")/$(basename "$tmp").sample/.roundtable"
test -f "$(dirname "$tmp")/$(basename "$tmp").sample/docs/design/roundtable/requirements.md"
```

Expected: both `test` commands exit 0.

- [ ] **Step 3: Smoke named init**

Run:

```bash
(cd "$tmp" && /Users/wukong/mylife/agent-roundtable/bin/roundtable init sample)
```

Expected: output says it initialized the `.roundtable` directory inside the `.sample` worktree.

- [ ] **Step 4: Smoke guarded `new --start`**

Run:

```bash
(cd "$tmp" && AUTO_KICKOFF=0 CLAUDE_CMD=true CODEX_CMD=true /Users/wukong/mylife/agent-roundtable/bin/roundtable new --start sample2)
```

Expected: a tmux session starts for the `.sample2` worktree. Detach or stop it after observing startup:

```bash
/Users/wukong/mylife/agent-roundtable/bin/roundtable stop sample2
```

- [ ] **Step 5: Clean temporary worktrees**

Run:

```bash
git -C "$tmp" worktree remove --force "$(dirname "$tmp")/$(basename "$tmp").sample" || true
git -C "$tmp" worktree remove --force "$(dirname "$tmp")/$(basename "$tmp").sample2" || true
rm -rf "$tmp" "$(dirname "$tmp")/$(basename "$tmp").sample" "$(dirname "$tmp")/$(basename "$tmp").sample2"
```

Expected: temporary directories are removed.

- [ ] **Step 6: Final status check**

Run:

```bash
git status --short
```

Expected: no unexpected tracked changes. Existing unrelated untracked directories may remain untouched.
