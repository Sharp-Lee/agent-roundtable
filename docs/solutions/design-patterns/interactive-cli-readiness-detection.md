---
title: Detecting interactive-CLI readiness via terminal-output stability
date: 2026-06-17
category: docs/solutions/design-patterns
module: bin/roundtable
problem_type: design_pattern
component: tooling
severity: low
applies_when:
  - Automating keystroke input into an interactive TUI CLI (claude, codex, REPLs)
  - Deciding when a freshly launched CLI pane is ready to receive a prompt
  - Driving panes via tmux send-keys / capture-pane
tags: [tmux, capture-pane, interactive-cli, readiness-detection, tui, automation]
---

# Detecting interactive-CLI readiness via terminal-output stability

## Context

`roundtable start` launches two interactive CLIs (Claude Code as *lead*, Codex as
*impl*) in tmux panes, then wants to auto-send each one its operating-contract
prompt so the user never pastes it by hand. The hard part is *timing*: an
interactive TUI takes a few seconds to boot, and keystrokes sent before it is
ready are silently dropped. There is no portable "I am ready for input" signal,
so readiness has to be inferred from the only thing observable: the pane's
rendered output.

## Guidance

Infer readiness from **output stability**, not from matching a prompt string.
Poll `tmux capture-pane -p` once per second and consider the CLI settled only
after the captured text has held **steady for several consecutive samples** past
a **minimum elapsed floor**:

```bash
_wait_pane_ready() {
  local pane="$1" timeout="$2" prev="" cur="" i=0 stable=0
  local min_elapsed=5 stable_required=3
  while [ "$i" -lt "$timeout" ]; do
    sleep 1; i=$((i + 1))
    cur="$(tmux capture-pane -p -t "$pane" 2>/dev/null)"
    if [ -n "$cur" ] && [ "$cur" = "$prev" ]; then
      stable=$((stable + 1))
      if [ "$i" -ge "$min_elapsed" ] && [ "$stable" -ge "$stable_required" ]; then return 0; fi
    else
      stable=0
    fi
    prev="$cur"
  done
  return 1   # timed out — caller falls back to manual
}
```

Pair it with two things that make the heuristic safe to be wrong:

- An **opt-out** (`AUTO_KICKOFF=0`) that prints a paste-ready prompt instead.
- A **timeout fallback** (`KICKOFF_TIMEOUT`) so a pane that never settles degrades
  to a manual instruction rather than hanging.

## Why This Matters

Output-stability detection is a **convenience heuristic, not a reliable readiness
signal**, and treating it as the latter causes silent, hard-to-debug input loss:

- **False-ready**: a static first-run/login/model-select/trust-folder screen
  *looks* settled before the main input prompt is interactive, so the prompt is
  sent into the wrong context and lost. The `min_elapsed` floor + multiple
  consecutive stable samples reduce, but do not eliminate, this.
- **False-timeout**: a CLI with an animated idle prompt (spinner, blinking
  redraw that changes captured text) never goes "stable" and hits the timeout.
  This is acceptable *only* because the fallback is graceful (manual paste).

The mechanism's one genuine strength: **loading spinners are waited out for free**
— continuous animation keeps resetting the stable counter, so the poll naturally
blocks through "still loading" without any spinner-specific logic.

Because it cannot distinguish these cases, never wire output-stability into
anything that must be correct (e.g. a protocol completion signal). Roundtable's
real handoff/completion signal is a **mailbox file write** (`bin/relay.py`),
which is explicit and unambiguous — output stability is used only as a one-time
startup nicety on top of that.

## When to Apply

- You must inject input into an interactive CLI you do not control and cannot
  modify to emit a ready signal.
- A wrong guess is *recoverable* (manual fallback exists). If it is not, do not
  use this pattern.
- Prefer prompt-string matching only when the target CLI's ready prompt is
  stable across versions; otherwise stability polling is more robust to UI churn.

## Examples

Calling side, with graceful degradation per pane:

```bash
if _wait_pane_ready "$lead_pane" "$KICKOFF_TIMEOUT"; then
  _send_prompt "$lead_pane" "$lead_kick"
else
  echo "  (lead pane did not settle in ${KICKOFF_TIMEOUT}s -- paste its kickoff manually)"
fi
```

Tuning trade-off observed while building this:

- `min_elapsed=2, stable_required=2` → settled an idle shell in ~3s but was prone
  to false-ready on static banners.
- `min_elapsed=5, stable_required=3` → ~5–6s to settle, materially fewer
  false-ready trips. Verified empirically: an idle prompt settles; a pane on a
  `while true; do date; sleep 0.3; done` busy-loop correctly never settles and
  hits the timeout.

## Related

- `bin/roundtable` — `_wait_pane_ready`, `_send_prompt`, `cmd_start`
- `bin/relay.py` — the mailbox-write completion signal this pattern sits on top of
- Commits `b6031c0` (feature) and `83a0dda` (readiness hardening) on `feat/auto-kickoff`
