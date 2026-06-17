---
title: Context-aware server-global tmux keybindings safe under concurrent sessions
date: 2026-06-17
category: docs/solutions/design-patterns
module: bin/roundtable
problem_type: design_pattern
component: tooling
severity: low
applies_when:
  - Installing tmux key bindings (which are server-global) from a per-project tool
  - One tool runs many concurrent tmux sessions on one server and each needs its own context
  - You want an install step to be idempotent without clobbering the user's own bindings
  - You need capability/conflict gating to be unit-testable without an attached client
tags: [tmux, keybindings, display-popup, concurrent-sessions, idempotency, session-options, headless-testing, pure-helpers]
---

# Context-aware server-global tmux keybindings safe under concurrent sessions

## Context

`roundtable` installs two `prefix+key` bindings that open `display-popup` overlays
(a tips cheatsheet and a project file view). Two facts collide:

- **tmux key bindings are server-global**, not session-scoped. There is no
  per-session key table you can bind into.
- **roundtable runs many sessions on one server at once** — one per project
  (`roundtable-<name>-<hash>`). Two projects are often live simultaneously.

So a naive binding that bakes in *this* project's directory would open the wrong
project's popup from another session, and a second project's `start` either can't
install its keys or stomps the first's. Add the requirement that `stop` must never
unbind (it would break a still-running sibling session), and a per-session opt-out
(`RT_KEYS=0`), and the binding has to carry **zero project state** itself.

## Guidance

**Bind once, globally, to a context-free command; resolve all per-session context
at invocation time from tmux session options.** The binding is the same string for
every session; what differs is the session it fires in.

1. Store per-session context as **session options** at `start` (not in the binding):

   ```bash
   tmux set-option -t "$sess" @roundtable_dir  "$target"
   tmux set-option -t "$sess" @roundtable_keys  "$keys_enabled"   # 1 or 0, from RT_KEYS
   tmux set-option -t "$sess" @roundtable_tips_key "$RT_TIPS_KEY"
   ```

2. Bind a **global** key to a stateless helper command (absolute path, not PATH-dependent):

   ```bash
   tmux bind-key -T prefix "$key" display-popup -E -w 80% -h 80% \
     "RT_POPUP_SENTINEL=rt-popup:$kind '$abs/bin/roundtable' _popup $kind"
   ```

3. The helper resolves the **invoking** session's context. Read the option through
   `$TMUX_PANE` (the pane that launched the popup), so concurrent sessions each get
   their own project, then **hard no-op** unless the session is genuinely a roundtable
   session *and* not opted out:

   ```bash
   dir="$(tmux display-message -p -t "$TMUX_PANE" '#{@roundtable_dir}')"
   keys="$(tmux display-message -p -t "$TMUX_PANE" '#{@roundtable_keys}')"
   if [ -z "$dir" ] || [ "$keys" != "1" ]; then
     echo "roundtable: popup inactive here (not a roundtable session, or RT_KEYS=0)"; exit 0
   fi
   ```

   This makes `RT_KEYS=0` a real **per-session** opt-out (`@roundtable_keys=0`) even
   though the global binding still exists — and makes the key a clean no-op in any
   non-roundtable session on the same server.

### Idempotency that survives a relocated install: a *path-aware* sentinel

To re-run `start` without clobbering the user's own binding on the same key, classify
the existing binding before touching it. The non-obvious failure: a plain "is it ours?"
sentinel marks the binding ours forever, so a binding left by an **older checkout**
(different absolute path) is kept and silently runs a stale/deleted binary. Match on
**both** the sentinel *and* the current target command:

```bash
_popup_binding_action() {           # pure: (existing, sentinel, command) -> action
  local existing="$1" sentinel="$2" command="$3"
  if   [ -z "$existing" ];                                              then echo bind   # unbound
  elif [[ "$existing" == *"$sentinel"* && "$existing" == *"$command"* ]]; then echo keep   # ours, current
  elif [[ "$existing" == *"$sentinel"* ]];                              then echo bind   # ours, stale path -> refresh
  else                                                                       echo skip   # someone else's -> preserve + warn
  fi
}
```

`keep` (silent) only when the sentinel **and** the live command match; ours-but-stale
falls through to `bind` and self-heals; foreign bindings are preserved with a warning.

## Why This Matters

- **The global/per-project mismatch is invisible until two sessions run at once.** A
  single-session test will never catch a binding that hardcodes the project — it only
  fails when a second project is live, which is exactly the real usage. Designing the
  binding to be stateless from the start removes a whole class of "wrong project" bugs.
- **`stop` never unbinds.** Because context lives in session options that die with the
  session, a global binding pointing at a dead session degrades to its hard no-op
  automatically. No teardown bookkeeping, no risk of one `stop` breaking a sibling.
- **A "mark it ours" sentinel is a trap for long-lived servers.** tmux servers outlive
  many tool installs; without the path check, relocating or re-cloning the tool leaves a
  permanently-broken key that no re-run repairs. The path-aware sentinel makes re-runs
  converging rather than sticky.

### Make the gating logic pure so degradation is testable headless

Popups need an attached client, so the *rendering* can't be unit-tested — but every
**decision** can be, if you keep it out of the I/O. Factor capability and conflict
gating into pure functions that take their inputs as arguments, do the one live probe
in the caller, and pass the result in:

```bash
_install_popup_bindings() {
  local supported=0; _tmux_supports_display_popup && supported=1   # the only live probe
  case "$(_popup_install_plan "$supported" "$keys_enabled" "$tips_key" "$file_key")" in
    install) _install_popup_binding "$tips_key" tips; _install_popup_binding "$file_key" file ;;
    skip-unsupported) echo "... display-popup unsupported; popup keys not installed" >&2 ;;
    skip-samekey)     echo "... tips/file keys collide; not installed" >&2 ;;
    # skip-keys / skip-missing-* ...
  esac
}
```

`selftest` then asserts every branch of `_popup_install_plan` and `_popup_binding_action`
with injected inputs — `(1,1,g,e)->install`, `(0,1,g,e)->skip-unsupported`, stale-path
existing `->bind` — with no real tmux popup and no attached client. The capability probe
itself stays parser-free (`tmux list-commands` contains `display-popup`), never a
`tmux -V` version compare (version strings like `3.2a`/`next-3.4` break numeric compares).

## When to Apply

- Any tool that installs **server-global or machine-global** resources (tmux/readline
  bindings, git hooks, shell aliases) but runs in **many concurrent per-project contexts**.
  Push the context out of the global artifact and resolve it at invocation.
- When an install step must be **idempotent across versions/relocations** — include the
  current target (path/version) in the "is it mine?" check, not just an ownership marker.
- When a feature's *effect* needs an interactive surface to observe but its *decisions*
  don't — split the probe (I/O) from the decision (pure) and test the decision.

## Examples

Two concurrent sessions, same global binding, different results (verified headless via
isolated `TMUX_TMPDIR` servers): invoking `prefix+e` in project A's pane opens A's files;
in project B's pane opens B's — because each resolves `@roundtable_dir` through its own
`$TMUX_PANE`. A pre-bound non-roundtable `prefix+g` is preserved with a warning and the
other key still installs. A binding left by `/old/checkout/bin/roundtable` is refreshed to
the current path on the next `start`, with no spurious "already bound" warning.

## Related

- `bin/roundtable` — `_install_popup_bindings`, `_install_popup_binding`,
  `_popup_binding_action`, `_popup_install_plan`, `cmd_popup`, `_popup_option`
- `bin/relay.py` / `bin/roundtable` — the `%N` pane-id capture-at-creation +
  live-and-owned (`#{session_name}` == `$SESSION`) validation that protects the *other*
  cross-session hazard: send-keys to a stale/foreign pane
- [[interactive-cli-readiness-detection]] — the sibling "graceful degradation around an
  unobservable signal" pattern in the same tool
- Commits `77e932f` (popup keybindings), `7f03b2a` (path-aware convergence),
  `e79ddf5` (headless verification of the pure-helper seam)
