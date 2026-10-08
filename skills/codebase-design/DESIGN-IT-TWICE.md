# Design It Twice

The user can want to examine alternative interfaces for a selected deepening candidate. In that case, use this pattern of parallel subagents. It uses the idea of "Design It Twice" (Ousterhout). Your first idea is not likely to be the best.

This file uses the vocabulary in [SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**, **leverage**.

## Process

### 1. Frame the problem space

Before you start subagents, write an explanation of the problem space of the selected candidate for the user. Include these items:

- The constraints that any new interface would have to satisfy
- The dependencies that it would use, and the category of each (see [DEEPENING.md](DEEPENING.md))
- A rough code sketch that makes the constraints concrete. It is not a proposal.

Show this to the user. Then go to Step 2 immediately. The user reads and thinks while the subagents work in parallel.

### 2. Spawn sub-agents

Start 3+ subagents in parallel. Each subagent must make a **radically different** interface for the deepened module.

Give each subagent a separate technical brief. The brief contains the file paths, the coupling details, the dependency category from [DEEPENING.md](DEEPENING.md), and what sits behind the seam. The brief is independent of the problem-space explanation for the user in Step 1. Give each agent a different design constraint:

- Agent 1: "Minimize the interface: aim for 1–3 entry points max. Maximise leverage per entry point."
- Agent 2: "Maximise flexibility: support many use cases and extension."
- Agent 3: "Optimise for the most common caller: make the default case trivial."
- Agent 4 (if applicable): "Design around ports & adapters for cross-seam dependencies."

Put the [SKILL.md](SKILL.md) vocabulary and the CONTEXT.md vocabulary in the brief. Then each subagent gives names that agree with the architecture language and the domain language of the project.

Each subagent gives this output:

1. Interface (types, methods, params, and also invariants, order and error modes)
2. A usage example that shows how callers use it
3. What the implementation hides behind the seam
4. Dependency strategy and adapters (see [DEEPENING.md](DEEPENING.md))
5. Trade-offs: where leverage is high and where it is thin

### 3. Present and compare

Show the designs one after the other, so that the user can understand each one. Then compare them in prose. Compare them by **depth** (leverage at the interface), **locality** (where change stays), and **seam placement**.

After the comparison, give your own recommendation. Tell which design you think is the strongest, and why. If parts of different designs would combine well, propose a hybrid. Give a clear opinion. The user wants a strong read, not a menu.
