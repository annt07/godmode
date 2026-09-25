---
name: subagent-driven-development
description: Use when executing implementation plans with independent tasks in the current session
---

# Subagent-Driven Development

Execute a plan by dispatching a fresh implementer subagent per task, a two-axis task review (spec compliance + code quality) after each, and a broad whole-branch review at the end.

**Why subagents:** You delegate tasks to specialized agents with isolated context. By precisely crafting their instructions and context, you ensure they stay focused and succeed at their task. They should never inherit your session's context or history — you construct exactly what they need. This also preserves your own context for coordination work.

**Core principle:** Fresh subagent per task + two-axis task review (spec + standards) + broad final review = high quality, fast iteration.

**Narration:** between tool calls, narrate at most one short line — the ledger and the tool results carry the record.

**Continuous execution:** Do not pause to check in with your human partner between tasks. Execute all tasks from the plan without stopping. The only reasons to stop are the four named below, or all tasks complete.

**Rulings, not stalls.** A running plan does not wait on a human. Conflicts, ambiguities, plan defects — decide them. The spec is the binding authority, the plan is its argument, and your judgment settles what neither answers. Record every decision in the ledger as `Ruling: <what you decided> — <why> — <what it costs if wrong>`, and keep going.

Four things stop you, and only these: an irreversible or destructive operation; a security-sensitive action; a side effect outside this worktree that norms say you ask about first (a merge, a push to a shared branch, a publish); and a plan so broken that every path forward is a guess.

## When to Use

Use when you have an implementation plan with mostly independent tasks. If tasks are tightly coupled, use `godmode:executing-plans` instead.

## Setup

Ensure the work happens in an isolated workspace: use `godmode:using-git-worktrees` to create one or verify the existing one. Never start implementation on a main/master branch without your human partner's explicit consent.

Track progress in a ledger file, not only in todos. Each plan owns a workspace; the ledger is your recovery map. If your context compacts, trust the ledger and `git log` over your own recollection.

Read the plan once, note its context and Global Constraints, and create a todo per task. If the plan names a Spec, read that too: the spec is the authority the plan argues from.

Before dispatching Task 1, scan the plan once for conflicts (tasks that contradict each other, the Global Constraints, or the review rubric). Write the scan as a table in the ledger. Rule on everything you find before execution begins.

## Model Selection

Use the least powerful model that can handle each role to conserve cost and increase speed.

- **Mechanical implementation tasks** (isolated functions, clear specs, 1-2 files): fast, cheap model.
- **Integration and judgment tasks** (multi-file coordination, pattern matching): standard model.
- **Architecture and design tasks**: most capable available model.
- **The final whole-branch review**: most capable available model.
- **Review tasks**: scale to the diff's size, complexity, and risk.
- **Fix-loop escalation (rounds 4-5)**: at least one tier above the implementer that got stuck.

Always specify the model explicitly when dispatching a subagent.

## Implementer Report Contract

Every implementer sub-agent must end with a report written to its report file and returned in its final message. The report file path is passed in the dispatch. The report must contain exactly these sections:

```
STATUS: <one of: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED>

WHAT I DID:
<bullet list of actions taken: files created/modified, tests written, commits made>

TESTS RUN:
<the exact command(s) run and the pass/fail output>

CONCERNS:
<anything that might affect correctness, scope, or downstream tasks — empty if none>
```

**Status definitions:**
- `DONE` — task complete, all tests pass, nothing uncertain.
- `DONE_WITH_CONCERNS` — task complete and tests pass, but something needs the controller's attention (a design decision that felt off, a scope edge that wasn't covered, a dependency assumption).
- `NEEDS_CONTEXT` — task cannot proceed without information the controller holds: a missing interface, an unresolved ambiguity, a fact that needs primary-source research.
- `BLOCKED` — task cannot proceed at all: the plan is wrong, an irreversible operation is required, or the task is larger than one implementer can handle.

The implementer never leaves STATUS blank. The controller acts on STATUS first, then reads the rest of the report.

## The Task Loop

### 1. Dispatch the Implementer

Record BASE (`git rev-parse HEAD`) before dispatching.

Compose the dispatch so a task brief stays the single source of requirements. Your dispatch should contain:
1. One line on where this task fits in the project
2. The brief path, introduced as "read this first — it is your requirements"
3. Interfaces and decisions from earlier tasks that the brief cannot know
4. Your resolution of any ambiguity you noticed in the brief
5. The report-file path and report contract

Hand artifacts over as files. Do not paste accumulated prior-task summaries into later dispatches.

**Research during implementation:** If the implementer reports NEEDS_CONTEXT on a factual question that requires primary-source investigation, invoke `godmode:research` as a background agent to gather the answer before re-dispatching the implementer. Do not ask your human partner for facts that can be looked up.

**The implementer never dispatches subagents** — not helpers, and never a reviewer. Review arrives from you, after the report.

### 2. Handle the Report

Implementer sub-agents report one of four statuses:

- **DONE:** Generate the review package and dispatch the two-axis task reviewer.
- **DONE_WITH_CONCERNS:** Read the concerns before proceeding. If about correctness or scope, address them before review. If observations only, note them and proceed to review.
- **NEEDS_CONTEXT:** Provide the missing context (use `godmode:research` if fact-finding is needed) and re-dispatch.
- **BLOCKED:** Assess the blocker — context problem (re-dispatch with more context), reasoning problem (re-dispatch more capable model), task too large (break into smaller pieces), or plan wrong (rule on the correction, ledger it, re-dispatch with ruling).

Never ignore an escalation or force the same model to retry without changes.

### 3. Review the Task (Two-Axis)

**REQUIRED SUB-SKILL:** Use `godmode:requesting-code-review`'s two-axis model for every task review.

Dispatch **two parallel reviewer sub-agents**:

**Standards sub-agent:** gets the task brief, the diff, the repo's coding standards, and the Fowler smell baseline (read and paste the full contents of `skills/requesting-code-review/fowler-smells.md`). Reports: standards violations and code quality smells. Also notes refactoring opportunities for post-merge review cycles. Under 500 words.

**Spec sub-agent:** gets the task brief, the diff, and the plan's spec/requirements for this task. Reports: missing requirements, scope creep, requirements that look implemented but are wrong. Under 400 words.

Both reviews are required. The task is not complete until both sub-agents report. Neither replaces the other; neither replaces the implementer's self-review.

The two-axis task review gates on: **Spec axis clean** AND **Standards axis has no Critical or Important issues**. Minor standards findings and refactoring suggestions go to the ledger as deferred items.

### 4. The Fix Loop

The loop triggers when either axis reports spec failure, or a Critical or Important finding.

Minor findings: record in the ledger (`Task <N>: minor (deferred): <one-liner>`). They never enter the loop.

Everything else enters the loop. A fix round is one fix dispatch plus one scoped re-review. Five rounds maximum per task:

- **Rounds 1-3:** resume the original implementer with open findings.
- **Rounds 4-5:** dispatch a fresh implementer on a more capable model, carrying the brief path, the report file, and the open findings.

After each round, append to the ledger: `Task <N>: fix round <R>/5 (<X> addressed, <Y> open; commits <a7>..<b7>)`

Never fix findings yourself in the controller session.

**The breaker.** When round 5 still leaves findings open, adjudicate each:
- **Reviewer is wrong:** park it with a ruling. The final review sees both sides.
- **Real but not load-bearing:** park it with a ruling.
- **Real and load-bearing:** rule on the smallest change that unblocks the dependent work; ledger it; carry it into the next task's dispatch.

### 5. Complete the Task

When the review is clean (or every open finding is parked with a ruling at the cap), append to the ledger:

- `Task <N>: complete (commits <base7>..<head7>, review clean)`
- `Task <N>: complete (commits <base7>..<head7>, <K> parked)` after a tripped breaker

Mark the todo complete and move to the next task.

## Final Review

After all tasks, dispatch a final whole-branch review using `godmode:requesting-code-review`'s two-axis model, on the most capable available model. Point it at the ledger's deferred-minor and parked lines so it can triage which must be fixed before merge.

If the final review returns findings, dispatch ONE fix subagent with the complete findings list. Then run exactly one scoped re-review. Adjudicate residual findings as in the task loop's breaker. There is no second fix wave.

## Finish

Collect every ledger line containing `Ruling:` into your final message under "Rulings I made", in order, each with what it costs if wrong.

When the final whole-branch review is clean, delete this plan's workspace. Then use `godmode:finishing-a-development-branch`.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Close enough on spec compliance" | Reviewer found spec gaps = not done. Fix or adjudicate at the cap. |
| "I'll fix it myself, dispatching is overhead" | Controller fixes pollute your context and skip review. Resume the implementer. |
| "One reviewer is enough" | The two axes are deliberately separate. Standards findings mask spec gaps and vice versa when combined. |
| "The research is probably not needed, I know this API" | Confidence is not a source. Use `godmode:research` for any primary-source factual question. |
| "The ledger is overhead" | The ledger is what survives compaction. Controllers without one re-dispatch entire completed task sequences. |
