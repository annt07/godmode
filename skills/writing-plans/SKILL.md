---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before you change code.
---

# Writing Plans

## Overview

Write complete implementation plans. Assume that the engineer has zero context for our codebase and poor taste. Write all that they must know:

- which files each task changes
- the code
- the tests, and how to run them
- the docs that they can need to read

Give them the full plan as small tasks. DRY. YAGNI. TDD. Frequent commits.

Assume that they are a skilled developer who knows almost nothing about our toolset or problem domain. Assume that they do not know good test design well.

**Announce at the start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If you work in an isolated worktree, the `godmode:using-git-worktrees` skill must have made it at execution time.

**Save plans to:** `docs/godmode/plans/YYYY-MM-DD-<feature-name>.md`

## Scope Check

If the spec covers more than one independent subsystem, brainstorming must have divided it into sub-project specs. If brainstorming did not do this, propose separate plans: one plan for each subsystem. Each plan must make software that works and that you can test on its own.

## File Structure

Before you define the tasks, list the files that the plan makes or changes, and the responsibility of each file. Here you lock the decomposition decisions.

**REQUIRED SUB-SKILL:** Invoke `godmode:codebase-design` to assess the module boundaries. Each file must be a deep module: a lot of behavior behind a small interface. Apply the deletion test to each proposed file boundary. Ask: if you remove this module, does the complexity collect in one place, or does it only move? Prefer small, focused files to large files that do too much.

- Design units with clear boundaries and well-defined interfaces (the module, seam and adapter vocabulary from codebase-design).
- Files that change together must stay together. Divide by responsibility, not by technical layer.
- In an existing codebase, follow the existing patterns. If a file that you change became too large, you can add a split to the plan.

This structure informs the task decomposition. Each task must make a self-contained change that has a purpose on its own.

## Task Right-Sizing

A task is the smallest unit that has its own test cycle and that a new reviewer can usefully gate. When you set the task boundaries, put setup, configuration, scaffolding and documentation steps into the task whose result needs them. Divide a task only where a reviewer can reject one part and approve the next part. Each task ends with a result that you can test on its own.

## Slice Vertically: Tracer Bullets, Not Layers

Each task is a **tracer bullet**: a thin but complete path through each layer that the change touches (schema, logic, API, UI, tests). You can show the task on its own when it lands. Never divide the work by layer ("all the schema", then "all the API"). If you do, nothing works until all layers land, and the checks of each task depend on work that a different task owns. Horizontal slicing is the failure that multiplies rework.

- **Demo test.** For each task, answer: "What can I demo when this is done?" The answer must be a behavior, not a layer. A task with no answer is a horizontal slice. Cut it again.
- **Prefactoring first.** Make the change easy, then make the easy change. Sometimes existing code must change its shape before the feature fits (a shallow module becomes deeper, or a new seam). That change of shape is its own task at the start of the order. Never mix it into a feature task.
- **Each acceptance check must fail at the start.** Each acceptance check must be false at the commit where the task starts. A check that is already true at the base grades nothing. A check that only the work of a different task can make true also grades nothing. For each check, name the observation that shows that it is false.
- **Wide-refactor exception: expand, migrate, contract.** Some mechanical changes affect much of the codebase (rename a column, change the type of a shared symbol). Such a change cannot land as one green vertical slice. Do it in this order:
  - **expand**: add the new form next to the old form. Nothing breaks.
  - **migrate**: move the call sites in batches. The size of the affected area sets the batch size. Use one task for each batch. Each batch uses the expand.
  - **contract**: remove the old form when no caller uses it.
- **Size to one new context.** An implementer that never saw the spec must be able to finish the task with only its brief.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use godmode:subagent-driven-development (recommended) or godmode:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Spec:** [path to the spec/design doc this plan implements]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits, naming and copy rules, platform requirements — one line each, with exact values copied verbatim from the spec. Every task's requirements implicitly include this section.]

## Review Focus

[The five input classes or failure modes the spec implies but no task's tests exercise that are most likely to bite a person using this software — one line each, naming the input or condition and the behavior a reasonable person would expect, most likely first.]

---
```

## Task Structure

In each task, the implementer verifies the seam before they write a test (see `godmode:test-driven-development`). Replace all placeholders with real project commands and syntax. Do not leave `[ext]`, `[test framework]` or `[project test command]` in the final plan:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.[ext]`
- Modify: `exact/path/to/existing.[ext]:123-145`
- Test: `tests/exact/path/to/test.[ext]`

**Seam under test:** [the public interface this task's tests exercise — module name, method names, or endpoint. Copy it from the spec's Testing Decisions, where your human partner agreed it. A seam the spec never agreed goes to your partner at plan review, not to the implementer.]

**Demo:** [the behavior you can show when this task lands, not a layer]

**Fails at base:** [the observation that is false at this task's starting commit and true when it is done]

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter and return types]

- [ ] **Step 1: Check the seam reaches the behavior**

Read the code at the agreed seam and confirm a test through its public interface can observe this task's behavior. If it cannot, stop: that is a plan defect (see `godmode:test-driven-development` Step 0), not a reason to test internals.

- [ ] **Step 2: Write the failing test**

Write one test using the project's actual test framework (e.g. pytest, Jest, RSpec, go test). Expected value must be a known-good literal, not a recomputation.

- [ ] **Step 3: Run test to verify it fails**

Run: `[project test command for this file]`
Expected: FAIL — feature missing (not a syntax error or import failure)

- [ ] **Step 4: Write minimal implementation**

Write the simplest code that passes the test. Nothing more.

- [ ] **Step 5: Run test to verify it passes**

Run: `[project test command for this file]`, then run the full suite.
Expected: PASS, full suite green.

- [ ] **Step 6: Commit**

```bash
git add [test file] [implementation file]
git commit -m "feat: [what this task implements]"
```
````

## No Placeholders

Each step must contain the actual content that an engineer needs. These items are **plan failures**. Never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code, because the engineer can read the tasks in a different order)
- Steps that tell what to do but do not show how (code steps need code blocks)
- References to types, functions or methods that no task defines

## Self-Review

After you write the complete plan, read the spec again as a new reader and compare the plan with it. You do this checklist yourself. It is not a subagent dispatch.

**1. Spec coverage:** Read each section and requirement of the spec quickly. Can you point to a task that implements it? List each gap.

**2. Placeholder scan:** Search your plan for red flags: any pattern from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures and property names in later tasks agree with what you defined in earlier tasks?

**4. Seam consistency:** Does each task name its seam? Are the seams at the highest possible point? Do two tasks use the same seam (a sign of coupling)?

**5. Review Focus:** For each input class or failure mode that the spec implies, does a task have tests that exercise it?

**6. Slicing:** Does each task have a behavioral Demo line and a Fails at base line? Is a task only one layer of the change? Is prefactoring at the start, not mixed into feature tasks? Does each wide refactor use the order expand, migrate, contract?

**7. Agent-readable:** Agents with no context read the plan and each task brief. Apply the no-op test of godmode:writing-for-agents to the Global Constraints and the task text. Remove what the implementer does by default. Keep each constraint in one place. Give each step a done-condition that a reader can verify.

If you find problems, fix them in the plan. You do not have to review again. Fix the problems and continue. If you find a spec requirement with no task, add the task.

## Execution Handoff

After you save the plan and review it yourself, give your human partner a link to it. Ask them to review the plan and to select an execution method before implementation.

**"Plan complete and saved to `docs/godmode/plans/<filename>.md`. Please review the plan. Which execution approach would you prefer?**

- **Subagent-driven** - A new subagent implements each task. A new reviewer reviews it before the next task starts. At the end, one review covers the full branch. This is the most thorough method. It costs a new context for each task and each review.
- **Native** - I implement each task myself in this session. Then one new reviewer on the most capable model reviews the full branch. This is the cheapest and fastest method. No independent review occurs until the end.

**For this plan I recommend <one of the two>, because <reason>. Does the plan capture what you want? Which approach should we use?"**

The `<reason>` is one sentence from the plan. It tells how much the tasks depend on the interfaces of other tasks, how many tasks there are, and the cost of a shipped mistake.

**If your partner selects Subagent-driven:**
- **REQUIRED SUB-SKILL:** Use `godmode:subagent-driven-development`

**If your partner selects Native:**
- **REQUIRED SUB-SKILL:** Use `godmode:executing-plans`
