---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they do not know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** If working in an isolated worktree, it should have been created via the `godmode:using-git-worktrees` skill at execution time.

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it was not, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

**REQUIRED SUB-SKILL:** Invoke `godmode:codebase-design` to evaluate module boundaries. Each file should be a deep module: a lot of behaviour behind a small interface. Apply the deletion test to every proposed file boundary. Ask: would deleting this module concentrate complexity, or just move it? Prefer smaller, focused files over large ones that do too much.

- Design units with clear boundaries and well-defined interfaces (module, seam, adapter vocabulary from codebase-design).
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If a file you are modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Task Right-Sizing

A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate. When drawing task boundaries: fold setup, configuration, scaffolding, and documentation steps into the task whose deliverable needs them; split only where a reviewer could meaningfully reject one task while approving its neighbor. Each task ends with an independently testable deliverable.

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

Each task must include seam confirmation before any test is written (see `godmode:test-driven-development`). Replace all placeholders with real project commands and syntax — do not leave `[ext]`, `[test framework]`, or `[project test command]` in the final plan:

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.[ext]`
- Modify: `exact/path/to/existing.[ext]:123-145`
- Test: `tests/exact/path/to/test.[ext]`

**Seam under test:** [the public interface this task's tests exercise — module name, method names, or endpoint. Confirm this seam with the reviewer before implementation begins.]

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter and return types]

- [ ] **Step 1: Confirm the seam**

Before writing any test, confirm the seam: "The seam under test is [interface]. Tests will exercise this through its public interface only, not its internals." Get a nod from the implementer.

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

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks?

**4. Seam consistency:** Does each task name its seam? Are the seams at the highest point possible? Are any seams duplicated across tasks (a sign of coupling)?

**5. Review Focus:** For each input class or failure mode the spec implies, is there a task whose tests exercise it?

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving and self-reviewing the plan, link it for your human partner to read. Ask them to review the plan and choose an execution method before implementation.

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Please review the plan. Which execution approach would you prefer?**

- **Subagent-driven** - A fresh subagent implements each task and a fresh reviewer checks it before the next one starts, then a whole-branch review at the end. Most thorough; costs a fresh context per task and per review.
- **Native** - I implement every task myself in this session, then one fresh reviewer on the most capable model checks the whole branch. Cheapest and fastest; no independent review until the end.

**For this plan I recommend <one of the two>, because <one sentence from the plan: how much the tasks depend on each other's interfaces, how many there are, what a shipped mistake would cost>. Does the plan capture what you want, and which approach should we use?"**

**If Subagent-driven chosen:**
- **REQUIRED SUB-SKILL:** Use `godmode:subagent-driven-development`

**If Native chosen:**
- **REQUIRED SUB-SKILL:** Use `godmode:executing-plans`
