# Requirements — <project / feature name>

> Produced in Phase 2 from the locked `architecture.md` + `flow.md`.
> Default tracked location: `docs/design/roundtable/requirements.md`.
> Runtime handoff state stays in `.roundtable/`.
> Grain: one runtime flow node can expand into many atomic requirements (n:1).

**Version:** v1
**Baseline:** draft | pending review | locked
**Gate 2:** pending | approved | sent back
**Pending count:** <number of requirements whose WHY/WHAT are not arbiter-confirmed>

## 1. Problem & goal

<What are we solving, for whom, and why now. One or two paragraphs.>

## 2. Locked inputs

- **Direction:** `.roundtable/_idea.md` / decisions entry / commit link
- **Architecture:** `docs/design/roundtable/architecture.md`
- **Runtime flow:** `docs/design/roundtable/flow.md`
- **Non-goals / frozen boundaries:** …

If a requirement changes the locked direction, architecture, or flow, stop and reopen the relevant gate.

## 3. Scope

- **In scope:** …
- **Out of scope (explicit non-goals):** …

## 4. 拆解清单

List every runtime flow node before drafting requirements. Gate 2 requires `pending = 0`.

| Group | Flow node | Business step | Requirement ids | Pending | Status |
|---|---|---|---|---:|---|
| G1 | F-001 | … | R-F001-1..n | 0 | todo |
| G2 | F-002 | … | R-F002-1..n | 0 | todo |

## 5. Atomic requirement format

Each atomic requirement must include all seven fields:

1. **编号**
2. **所属节点**
3. **WHY / 作用**
4. **WHAT / 实现什么**
5. **HOW / 怎么实现**
6. **验收**
7. **状态**

Status values for atomic requirements: `pending` / `todo` / `doing` / `done` / `blocked`.
`pending` means the arbiter has not confirmed WHY/WHAT, so Gate 2 cannot be triggered.

## 6. Requirements by flow node

### G1 · <F-001 business step name>

#### R-F001-1 <requirement title>

- **编号:** R-F001-1
- **所属节点:** F-001 <business step name>
- **WHY / 作用:** <Why this matters; arbiter participates in confirming this.>
- **WHAT / 实现什么:** <What must exist or change; arbiter participates in confirming this.>
- **HOW / 怎么实现:** <Implementation approach decided mainly by 玄 + 素.>
- **验收:** <Observable acceptance criteria.>
- **状态:** pending

#### R-F001-2 <requirement title>

- **编号:** R-F001-2
- **所属节点:** F-001 <business step name>
- **WHY / 作用:** …
- **WHAT / 实现什么:** …
- **HOW / 怎么实现:** …
- **验收:** …
- **状态:** pending

### G2 · <F-002 business step name>

#### R-F002-1 <requirement title>

- **编号:** R-F002-1
- **所属节点:** F-002 <business step name>
- **WHY / 作用:** …
- **WHAT / 实现什么:** …
- **HOW / 怎么实现:** …
- **验收:** …
- **状态:** pending

## 7. Constraints & assumptions

<Tech constraints, perf/security needs, environment, things assumed true.>

## 8. Panel / review notes

Use this section when a high-complexity, high-risk, or cross-node requirement needs a panel before Gate 2.

| Requirement id | Lens | Finding | Disposition | Rationale |
|---|---|---|---|---|
| … | feasibility / security / scope / data-flow / operations | … | accepted / rejected | … |

## 9. Open questions

Gate 2 requires this section to be empty or explicitly resolved.

| Question | Affected node / requirement | Owner | Status |
|---|---|---|---|
| … | … | … | pending |
