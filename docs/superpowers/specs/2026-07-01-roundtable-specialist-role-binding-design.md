# Roundtable Specialist Role Binding Design

## Purpose

Upgrade Roundtable from a fixed two-role workflow into a workflow that gives those two roles
idea-scoped professional competence.

The existing 玄 and 素 contracts define process ownership:

- 玄 owns synthesis, design documents, requirements, gate presentation, review, and decisions.
- 素 owns challenge-first review, implementation, verification, and source commits.

That is necessary but not sufficient. Both roles participate in planning, coordination, execution,
and review. If they do not carry the right domain expertise for the user's idea, they can make weak
direction, architecture, requirement, and implementation judgments. They may also be unable to
choose the right one-shot panel reviewers.

This design adds a required specialist binding step before the idea roundtable starts.

## Core Model

Roundtable roles become layered:

```text
玄 = fixed process contract + idea-scoped planning/product/architecture expertise
素 = fixed process contract + idea-scoped engineering/implementation/verification expertise
```

The specialist layer is an overlay. It can strengthen judgment, vocabulary, risks, and review
criteria, but it must not override the shared protocol, mailbox rules, file ownership, gate rules,
or commit ownership.

`agency-agents` is treated as the default specialist role library. Its roles are source material for
the idea-specific overlays, not resident relay participants.

## New Phase

Add a lightweight pre-Phase-0 step:

```text
Phase 0a - Specialist role binding
```

This happens after `rt new <name>` / `rt init [name]` scaffolds the idea state and before Phase 0
idea shaping begins.

The binding decision flow is:

```text
arbiter idea
  -> 玄 drafts specialist binding
  -> 素 challenges the binding
  -> 玄 and 素 converge
  -> arbiter confirms or adjusts
  -> binding is written to files and recorded in decisions.md
```

No specialist binding should silently take effect without arbiter confirmation.

## Decision Rubric

玄 drafts the binding by evaluating:

- idea category: product, tool, agent system, data system, content system, trading system, game,
  infrastructure, or another explicit category.
- core uncertainty: requirements ambiguity, technical feasibility, data quality, user experience,
  compliance, security, reliability, business model, or operational risk.
- deliverable shape: codebase, prototype, workflow automation, analysis report, content system,
  API service, SaaS, or another explicit artifact.
- 玄 expertise need: product strategy, business/domain modeling, systems architecture,
  workflow design, project shepherding, or requirements design.
- 素 expertise need: implementation engineering, system design, testing, validation, data
  engineering, reliability, security, or performance.
- uncovered risks: important domains not suitable as long-running overlays but likely to require a
  later one-shot panel.

素 challenges the draft by checking:

- whether the chosen roles are specific enough for the idea.
- whether implementation, verification, deployment, data, security, and operational risks are
  covered.
- whether 玄 and 素 are bound to meaningfully different expertise.
- whether a rejected candidate role was actually needed.
- whether any risk should be scheduled for a later panel instead of ignored.

The arbiter confirms because the binding defines the project's working cognition for the whole idea.

## Binding Artifacts

Each initialized idea should contain:

```text
.roundtable/roles/xuan.expert.md
.roundtable/roles/su.expert.md
```

The files are runtime state, not durable product design artifacts. They are idea-scoped and copied
or generated inside each worktree. They should be read on every kickoff and restart.

Recommended file structure:

```markdown
# Specialist Binding - 玄

## Source Idea

Short summary of the arbiter's raw idea.

## Selected Specialist Roles

- Role name
  - Source: agency-agents path or local source
  - Why selected
  - What this changes in 玄's work

## Operating Emphasis

Concrete domain heuristics, risk checks, and review criteria for this idea.

## Boundaries

What this specialist overlay must not override.
```

`su.expert.md` uses the same shape, but its "What this changes" section focuses on engineering,
implementation, verification, and operational judgment.

## Decision Record

`docs/design/roundtable/decisions.md` records the confirmed binding:

- idea summary.
- selected 玄 specialist roles.
- selected 素 specialist roles.
- accepted rationale.
- rejected candidate roles and why.
- uncovered risks.
- panel triggers to consider later.
- arbiter confirmation.

The role files carry operational instructions; `decisions.md` carries the durable rationale.

## Startup And Restart Order

Role startup order becomes:

```text
1. .roundtable/prompts/protocol.md
2. .roundtable/prompts/xuan.md or .roundtable/prompts/su.md
3. .roundtable/roles/xuan.expert.md or .roundtable/roles/su.expert.md
4. docs/design/roundtable/architecture.md and flow.md
5. docs/design/roundtable/requirements.md and decisions.md
6. .roundtable/channel.md
7. the role inbox
```

If the expert file is missing in a project that has not completed Phase 0a, the role should ask the
arbiter for the idea and start the specialist binding flow. If the expert file is missing after
Phase 0a was recorded as confirmed, the role should set `STATUS: blocked` and ask for recovery
instead of inventing expertise from chat memory.

## Panel Positioning

Panels remain one-shot internal reviews. They are no longer the primary way to supply professional
competence.

```text
specialist binding = persistent idea-scoped competence
panel = temporary blind-spot review
```

Use panel reviews for risks outside the bound specialist overlays, such as legal/compliance,
security, privacy, data governance, production reliability, and other high-risk blind spots.

The existing non-resident panel boundary remains unchanged:

- no new tmux pane.
- no relay route.
- no mailbox participant.
- findings must be dispositioned as accepted or rejected with rationale.

## Command And Scaffold Impact

`rt init` should create `.roundtable/roles/` and placeholder expert files for both roles.

`rt new <name>` inherits this through `rt init` inside the new idea worktree.

`rt start` / `rt kickoff` should mention the expert binding files in the kickoff prompt so each
agent reads the overlay before restoring project state.

The first implementation should not auto-fetch or vendor `agency-agents`. Role selection can be
manual or model-generated from available context. External role-library integration can be added
later once the local binding contract is stable.

## Documentation Impact

Update:

- `prompts/protocol.md` with Phase 0a, binding artifacts, restart order, and panel repositioning.
- `prompts/xuan.md` with 玄's binding proposal and decision-record duties.
- `prompts/su.md` with 素's binding challenge duties.
- `README.md` and `README.en.md` workflow diagrams and startup explanation.
- `bin/roundtable` selftest to guard role scaffold and kickoff references.

## Verification

Selftest should cover:

- `rt init` creates `.roundtable/roles/xuan.expert.md`.
- `rt init` creates `.roundtable/roles/su.expert.md`.
- kickoff text references the matching expert binding file for 玄.
- kickoff text references the matching expert binding file for 素.
- copied `protocol.md` contains the Phase 0a heading.
- no legacy role filenames or relay participants are introduced.

Manual smoke checks:

- run `roundtable selftest`.
- create a temporary repo and run `rt init`.
- inspect generated kickoff files.
- run `rt new sample` and confirm the new worktree has role binding placeholders.

## Out Of Scope

- No additional resident agents.
- No new relay routes.
- No new tmux panes.
- No automatic dependency on the live `agency-agents` GitHub repository.
- No role marketplace, cache, or sync mechanism.
- No automatic specialist selection without arbiter confirmation.
- No change to 玄/素 file ownership or commit ownership.
