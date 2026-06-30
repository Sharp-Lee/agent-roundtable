# Specialist Role Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an idea-scoped specialist binding layer so 玄/素 read persistent expert overlays before Phase 0.

**Architecture:** Keep the current two-agent relay architecture unchanged. Add `.roundtable/roles/{xuan,su}.expert.md` as runtime role overlays, update kickoff/restart instructions to read those files, and guard the scaffold through `roundtable selftest`.

**Tech Stack:** Bash CLI (`bin/roundtable`), Markdown prompt contracts, Markdown README docs, tmux/Python selftest harness already present in the repo.

---

## File Structure

- Modify `bin/roundtable`: create the runtime roles directory and expert files during `cmd_init`; include expert files in `_kickoff_text`; add selftest assertions.
- Modify `prompts/protocol.md`: add Phase 0a, specialist binding artifacts, startup/restart order, and panel repositioning.
- Modify `prompts/xuan.md`: add 玄's binding proposal, convergence, arbiter confirmation, and decision-record duties.
- Modify `prompts/su.md`: add 素's binding challenge duties.
- Modify `README.md`: document the upgraded Chinese workflow.
- Modify `README.en.md`: document the upgraded English workflow.
- Keep `bin/relay.py` unchanged: specialist files do not add relay participants.

---

### Task 1: Add Failing Selftest Coverage

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Add selftest assertions for role overlays**

In `cmd_selftest`, after the existing prompt-copy assertions:

```bash
  _selftest_assert_file "init creates xuan specialist binding" "$rt/roles/xuan.expert.md" || rc=1
  _selftest_assert_file "init creates su specialist binding" "$rt/roles/su.expert.md" || rc=1
  _selftest_assert_contains "xuan specialist binding names protocol boundary" "$rt/roles/xuan.expert.md" "This specialist overlay never overrides protocol.md, xuan.md, mailbox rules, gate rules, or commit ownership." || rc=1
  _selftest_assert_contains "su specialist binding names protocol boundary" "$rt/roles/su.expert.md" "This specialist overlay never overrides protocol.md, su.md, mailbox rules, gate rules, or commit ownership." || rc=1
```

After the existing protocol lifecycle assertion:

```bash
  _selftest_assert_contains "protocol contains specialist binding phase" "$rt/prompts/protocol.md" "### Phase 0a — Specialist Role Binding" || rc=1
```

Update the kickoff case checks to require `.roundtable/roles/xuan.expert.md` and `.roundtable/roles/su.expert.md`:

```bash
  case "$(_kickoff_text lead)" in
    *".roundtable/prompts/xuan.md"*".roundtable/roles/xuan.expert.md"*docs/design/roundtable/requirements.md*) _selftest_pass "玄 kickoff references xuan contract, specialist binding, and docs baseline" ;;
    *) _selftest_fail "玄 kickoff references xuan contract, specialist binding, and docs baseline" || true; rc=1 ;;
  esac
  case "$(_kickoff_text su)" in
    *".roundtable/prompts/su.md"*".roundtable/roles/su.expert.md"*docs/design/roundtable/requirements.md*) _selftest_pass "su kickoff alias references su contract, specialist binding, and docs baseline" ;;
    *) _selftest_fail "su kickoff alias references su contract, specialist binding, and docs baseline" || true; rc=1 ;;
  esac
```

After the new-worktree runtime state assertion:

```bash
  _selftest_assert_file "new worktree has xuan specialist binding" "$git_wt/.roundtable/roles/xuan.expert.md" || rc=1
  _selftest_assert_file "new worktree has su specialist binding" "$git_wt/.roundtable/roles/su.expert.md" || rc=1
```

- [ ] **Step 2: Run selftest to verify it fails**

Run:

```bash
PATH="/Users/wukong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH" ./bin/roundtable selftest
```

Expected: FAIL on missing specialist binding files, missing Phase 0a heading, and kickoff text not mentioning expert bindings.

- [ ] **Step 3: Commit the red test**

```bash
git add bin/roundtable
git commit -m "test: require specialist role binding scaffold"
```

---

### Task 2: Add Runtime Specialist Binding Scaffold

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Add helper functions before `cmd_init`**

Add:

```bash
_write_expert_binding() {
  local file="$1" display="$2" contract="$3" focus="$4"
  [ -f "$file" ] && return 0
  cat > "$file" <<EOF
# Specialist Binding - $display

## Source Idea

Unbound. During Phase 0a, summarize the arbiter's raw idea here before Phase 0 starts.

## Selected Specialist Roles

- Unbound
  - Source: agency-agents or local role source
  - Why selected: pending Phase 0a convergence
  - What this changes in $display's work: pending Phase 0a convergence

## Operating Emphasis

$focus

## Boundaries

This specialist overlay never overrides protocol.md, $contract, mailbox rules, gate rules, or commit ownership.
EOF
}

_init_expert_bindings() {
  local rt="$1"
  mkdir -p "$rt/roles"
  _write_expert_binding "$rt/roles/xuan.expert.md" "玄" "xuan.md" "Planning, product, architecture, requirements, review, and decision judgment for this idea."
  _write_expert_binding "$rt/roles/su.expert.md" "素" "su.md" "Engineering, implementation, verification, reliability, and operational judgment for this idea."
}
```

- [ ] **Step 2: Call the helper from `cmd_init`**

After creating `_idea.md` and `channel.md`, add:

```bash
  _init_expert_bindings "$rt"
```

- [ ] **Step 3: Update `.roundtable/.gitignore`**

Add `roles/` to the runtime ignore block:

```text
roles/
```

- [ ] **Step 4: Run selftest**

Run:

```bash
PATH="/Users/wukong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH" ./bin/roundtable selftest
```

Expected: specialist binding file assertions pass; Phase 0a/kickoff assertions still fail.

- [ ] **Step 5: Commit**

```bash
git add bin/roundtable
git commit -m "feat: scaffold specialist role bindings"
```

---

### Task 3: Update Kickoff To Read Expert Bindings

**Files:**
- Modify: `bin/roundtable`

- [ ] **Step 1: Modify `_kickoff_text`**

Change the prompt to read the specialist binding after the fixed role contract:

```bash
  local role="$1" wire contract display expert tail
  wire="$(_role_wire "$role")" || die "unknown role: $role"
  contract="$(_role_contract "$wire")"
  display="$(_role_display "$wire")"
  case "$wire" in
    lead) expert=".roundtable/roles/xuan.expert.md" ;;
    impl) expert=".roundtable/roles/su.expert.md" ;;
  esac
```

Then update the `printf` body so it says:

```text
Read .roundtable/prompts/protocol.md, then .roundtable/prompts/%s, then %s -- that is your full operating contract for this idea.
```

And update the workflow summary to include Phase 0a:

```text
Workflow: Phase 0a specialist role binding -> Phase 0 idea roundtable -> Gate 0; Phase 1 final-form design -> Gate 1; Phase 2 detailed requirements -> Gate 2; Phase 3 build loop.
```

- [ ] **Step 2: Run selftest**

Run:

```bash
PATH="/Users/wukong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH" ./bin/roundtable selftest
```

Expected: kickoff assertions pass; protocol Phase 0a assertion still fails.

- [ ] **Step 3: Commit**

```bash
git add bin/roundtable
git commit -m "feat: include specialist bindings in kickoff"
```

---

### Task 4: Update Protocol And Role Contracts

**Files:**
- Modify: `prompts/protocol.md`
- Modify: `prompts/xuan.md`
- Modify: `prompts/su.md`

- [ ] **Step 1: Update `prompts/protocol.md`**

Add `.roundtable/roles/` to runtime state, add `0a-binding` to the PHASE header list, insert `### Phase 0a — Specialist Role Binding` before Phase 0, reposition panel text, include roles in artifact ownership, and update restart order.

The Phase 0a section should state:

```markdown
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
- If bindings are missing before Phase 0a is complete, ask the arbiter for the idea and start this
  binding step. If bindings are missing after a recorded Phase 0a confirmation, set
  `STATUS: blocked` and ask for recovery rather than inventing expertise from chat memory.
```

Panel positioning should include:

```markdown
- Specialist bindings are the persistent idea-scoped competence layer; panels are temporary
  blind-spot reviews.
```

- [ ] **Step 2: Update `prompts/xuan.md`**

Add a specialist binding duties section:

```markdown
## Specialist Binding Duties

- In Phase 0a, draft the specialist binding for both roles from the arbiter's raw idea.
- Evaluate idea category, core uncertainty, deliverable shape, 玄 expertise needs, 素 expertise
  needs, uncovered risks, and likely later panel triggers.
- Send the draft to 素 for challenge before asking the arbiter to confirm.
- After convergence and arbiter confirmation, write or update `.roundtable/roles/xuan.expert.md`
  and `.roundtable/roles/su.expert.md`.
- Record the confirmed binding, rationale, rejected candidate roles, uncovered risks, and panel
  triggers in `docs/design/roundtable/decisions.md`.
- Treat the specialist binding as an overlay only; it never overrides `protocol.md` or this role
  contract.
```

Add Phase 0a to the phase table.

- [ ] **Step 3: Update `prompts/su.md`**

Add:

```markdown
## Specialist Binding Duties

- In Phase 0a, challenge 玄's specialist binding draft before it reaches the arbiter.
- Check whether the selected roles are specific enough for the idea and whether engineering,
  implementation, testing, deployment, data, security, and operational risks are covered.
- Check whether 玄 and 素 have meaningfully different specialist overlays.
- Name rejected candidate roles that should be restored, and risks that should become later panel
  triggers.
- Treat the specialist binding as an overlay only; it never overrides `protocol.md` or this role
  contract.
```

Add Phase 0a to the phase table and challenge checklist.

- [ ] **Step 4: Run selftest**

Run:

```bash
PATH="/Users/wukong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH" ./bin/roundtable selftest
```

Expected: all selftest assertions pass unless README-only work remains.

- [ ] **Step 5: Commit**

```bash
git add prompts/protocol.md prompts/xuan.md prompts/su.md
git commit -m "docs: define specialist role binding protocol"
```

---

### Task 5: Update User Documentation

**Files:**
- Modify: `README.md`
- Modify: `README.en.md`

- [ ] **Step 1: Update Chinese README workflow**

Add Phase 0a before Phase 0:

```text
Phase 0a 专家绑定        玄提案 -> 素质疑 -> 玄素收敛 -> 你确认
                         -> 写入 .roundtable/roles/{xuan,su}.expert.md
Phase 0  想法圆桌        玄/素带着专家能力打磨方向 -> 方向陈述
```

Update the contract paragraph to mention expert bindings:

```markdown
共享规则（channel、消息格式、提交归属、护栏）在 `prompts/protocol.md`；固定角色职责在
`prompts/xuan.md` 和 `prompts/su.md`；每个 idea 的专业能力绑定在
`.roundtable/roles/xuan.expert.md` 和 `.roundtable/roles/su.expert.md`。
```

Update kickoff text to mention the three-layer role read order.

- [ ] **Step 2: Update English README workflow**

Add Phase 0a before Phase 0:

```text
Phase 0a Specialist binding  玄 proposes -> 素 challenges -> converge -> you confirm
                             -> write .roundtable/roles/{xuan,su}.expert.md
Phase 0  Idea roundtable     玄/素 shape direction with the bound expertise -> direction statement
```

Update the contract paragraph to mention `.roundtable/roles/xuan.expert.md` and
`.roundtable/roles/su.expert.md`.

- [ ] **Step 3: Run selftest and syntax check**

Run:

```bash
bash -n ./bin/roundtable
PATH="/Users/wukong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH" ./bin/roundtable selftest
```

Expected: both commands pass.

- [ ] **Step 4: Commit**

```bash
git add README.md README.en.md
git commit -m "docs: describe specialist role binding workflow"
```

---

### Task 6: Final Verification And Review

**Files:**
- Inspect all changed files.

- [ ] **Step 1: Run full verification**

Run:

```bash
git diff --check HEAD~5..HEAD
bash -n ./bin/roundtable
PATH="/Users/wukong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH" ./bin/roundtable selftest
```

Expected: no whitespace errors, Bash syntax OK, selftest OK.

- [ ] **Step 2: Inspect final diff**

Run:

```bash
git status --short --branch
git log --oneline --max-count=8
git diff --stat main...HEAD
```

Expected: branch contains the spec commit plus implementation commits; worktree has no uncommitted tracked changes.

- [ ] **Step 3: Request code review**

Use `superpowers:requesting-code-review` or a local review pass focused on:

- missing selftest assertions.
- drift between protocol, role prompts, and README.
- accidental resident-agent or relay-route expansion.
- clobbering existing expert binding files during `rt init`.

- [ ] **Step 4: Finish the branch**

Use `superpowers:finishing-a-development-branch` after review and verification pass.
