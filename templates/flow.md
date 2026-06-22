# Runtime Flow — <project / feature name>

> Produced in Phase 1 by 玄 + 素 after Gate 0 locks the direction.
> Default tracked location: `docs/design/roundtable/flow.md`.
> **节点 = 业务步骤(不是开发步骤)**. These nodes are the source for Phase 2 requirement groups.

**Status:** draft | converged | locked
**Related architecture:** `docs/design/roundtable/architecture.md`
**Gate 1:** pending | approved | sent back

## 1. 流程节点清单

Every business step in the runtime flow should appear here before Phase 2 begins.

| Node id | Business step | Actor / system | Input | Output | Notes |
|---|---|---|---|---|---|
| F-001 | … | … | … | … | … |

## 2. 运行时流程图(必填)

```mermaid
flowchart TD
    Start([trigger]) --> Step1["F-001 business step"]
    Step1 --> Decision{"runtime decision"}
    Decision -->|yes| Step2["F-002 business step"]
    Decision -->|no| Stop([stop / handoff])
```

## 3. 时序图(按需)

Use this when multiple actors or services exchange messages over time.

```mermaid
sequenceDiagram
    participant A as Actor
    participant S as System
    participant F as Files
    A->>S: runtime request
    S->>F: read/write durable state
    S-->>A: result / next action
```

## 4. 状态机(按需)

Use this when phase, lock, approval, or retry state matters.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Converged
    Converged --> Locked
    Locked --> Reopened: explicit gate rollback
    Reopened --> Draft
```

## 5. 数据流(按需)

Use this when durable files, APIs, or derived artifacts carry important data.

```mermaid
flowchart LR
    Input["input artifact"] --> Transform["business step"]
    Transform --> Output["output artifact"]
    Output -. recovery .-> Transform
```

## 6. Phase 2 拆解提示

For each node above, Phase 2 expands one business step into one or more atomic requirements.
Traceability is n:1: many requirements may point back to the same flow node.
