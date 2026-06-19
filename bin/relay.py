#!/usr/bin/env python3
"""Roundtable relay watcher.

Turn-based message relay between two interactive CLI panes (lead / impl).

Mechanism (deliberately simple and robust):
  - Each agent hands off by *writing its message to a mailbox file*. That write
    is an explicit, unambiguous "my turn is done" signal -- we never scrape
    terminal output to guess completion.
  - This watcher polls the two mailbox files' mtimes. On change it:
      1. appends the message to channel.md (the durable transcript), and
      2. nudges the *other* pane via `tmux send-keys` to read its inbox.

Mailboxes (inside <project>/.roundtable/):
  - to-impl.md : lead writes here  -> relay nudges the impl pane
  - to-lead.md : impl writes here  -> relay nudges the lead pane

Config via environment:
  ROUNDTABLE_DIR : absolute path to the project's .roundtable directory
  SESSION        : tmux session that owns the lead/impl panes
  LEAD_PANE      : tmux target for the lead pane (usually a unique %N id)
  IMPL_PANE      : tmux target for the impl pane (usually a unique %N id)
  POLL_SECONDS   : poll interval (default 1.0)
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _env(name: str, required: bool = True) -> str:
    value = os.environ.get(name)
    if required and not value:
        sys.stderr.write(f"relay: missing required env {name}\n")
        sys.exit(2)
    return value or ""


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def _tmux(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["tmux", *args], check=False, capture_output=True, text=True)


def _pane_belongs_to_session(session: str, pane: str) -> bool:
    if not session or not pane:
        return False
    if _tmux("has-session", "-t", session).returncode != 0:
        return False
    result = _tmux("display-message", "-p", "-t", pane, "#{session_name}")
    return result.returncode == 0 and result.stdout.strip() == session


def _send_keys(session: str, pane: str, text: str) -> bool:
    if not _pane_belongs_to_session(session, pane):
        sys.stderr.write(
            f"relay: warning: pane {pane!r} is stale or outside session {session!r}; "
            "restart the session\n"
        )
        return False
    # Type the nudge literally, then submit with Enter. Two calls keep the
    # literal text and the Enter key distinct so the TUI submits cleanly.
    _tmux("send-keys", "-t", pane, "-l", text)
    time.sleep(0.2)
    _tmux("send-keys", "-t", pane, "Enter")
    return True


def _append_transcript(channel: Path, *, frm: str, to: str, body: str) -> None:
    block = f"\n\n---\n## {_now()}  {frm} -> {to}\n\n{body.rstrip()}\n"
    with channel.open("a", encoding="utf-8") as handle:
        handle.write(block)


def main() -> int:
    root = Path(_env("ROUNDTABLE_DIR")).expanduser().resolve()
    session = _env("SESSION")
    lead_pane = _env("LEAD_PANE")
    impl_pane = _env("IMPL_PANE")
    poll = float(os.environ.get("POLL_SECONDS", "1.0"))

    channel = root / "channel.md"
    # routes: mailbox file -> (sender, recipient label, recipient pane, inbox rel path)
    routes = {
        root / "to-impl.md": ("lead", "impl", impl_pane, ".roundtable/to-impl.md"),
        root / "to-lead.md": ("impl", "lead", lead_pane, ".roundtable/to-lead.md"),
    }

    # Baseline current mtimes so pre-existing content does not fire on startup.
    last_mtime = {p: (p.stat().st_mtime if p.exists() else 0.0) for p in routes}

    sys.stderr.write(
        f"relay: watching {root} (session={session} lead={lead_pane} impl={impl_pane}); Ctrl-C to stop\n"
    )

    while True:
        try:
            for mailbox, (frm, to, pane, inbox_rel) in routes.items():
                try:
                    mtime = mailbox.stat().st_mtime
                except FileNotFoundError:
                    continue
                if mtime <= last_mtime[mailbox]:
                    continue
                last_mtime[mailbox] = mtime
                body = mailbox.read_text(encoding="utf-8").strip()
                if not body:
                    continue
                _append_transcript(channel, frm=frm, to=to, body=body)
                nudge = (
                    f"[roundtable] New handoff in {inbox_rel}. "
                    f"Read it and act per .roundtable/prompts/{to}.md. "
                    "Do not poll; when done, write your reply to your outbox and stop."
                )
                if _send_keys(session, pane, nudge):
                    sys.stderr.write(f"relay: {frm} -> {to} ({len(body)} chars)\n")
                else:
                    sys.stderr.write(f"relay: {frm} -> {to} ({len(body)} chars, nudge skipped)\n")
            time.sleep(poll)
        except KeyboardInterrupt:
            sys.stderr.write("\nrelay: stopped\n")
            return 0
        except Exception as exc:  # keep the loop alive; transient FS/tmux errors
            sys.stderr.write(f"relay: warning: {exc}\n")
            time.sleep(poll)


if __name__ == "__main__":
    raise SystemExit(main())
