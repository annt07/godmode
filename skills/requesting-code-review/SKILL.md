---
name: requesting-code-review
description: Use when completing tasks, implementing major features, or before merging to verify work meets requirements and follows coding standards
---

# Requesting Code Review

Dispatch code reviewer sub-agents to catch issues before they cascade. This review runs on **two independent axes** simultaneously:

- **Standards axis**: does the code conform to this repo's documented coding standards, plus a fixed baseline of code quality smells?
- **Spec axis**: does the code faithfully implement what the originating spec or plan asked for?

A change can pass one axis and fail the other. Reporting them separately stops one from masking the other.

**Core principle:** Review early, review often. The Standards axis is also where refactoring opportunities surface — not during the TDD implementation loop.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After completing a major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing a complex bug

## How to Request

### 1. Pin the Fixed Point

Get the range:
```bash
BASE_SHA=$(git merge-base origin/main HEAD)  # or git rev-parse HEAD~1 for task reviews
HEAD_SHA=$(git rev-parse HEAD)
```

Confirm the diff is non-empty before dispatching: `git diff --stat $BASE_SHA..$HEAD_SHA`

### 2. Identify the Spec Source

Look for the originating spec, in this order:
1. The plan file used by subagent-driven-development for this task
2. The spec file in `docs/godmode/specs/` that the plan was written from
3. If nothing is found, provide the task text directly to the Spec sub-agent

### 3. Identify Standards Sources

Anything in the repo that documents how code should be written (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `CONTEXT.md`).

On top of repo-documented standards, the Standards axis always carries the **Fowler smell baseline** below. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic, never a hard violation. Skip anything tooling already enforces.

**Fowler Code Smell Baseline** — defined in full in [`fowler-smells.md`](fowler-smells.md) in this same directory. Pass its full contents to the Standards sub-agent. Summary:

- **Mysterious Name**: a function, variable, or type whose name does not reveal what it does or holds. Rename it; if no honest name comes, the design is murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file. Extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. Move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). Bundle them into one type.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. Give the concept its own small type.
- **Repeated Switches**: the same switch/if-cascade on the same type recurs across the change. Replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files. Gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. Split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec does not have. Delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller should not depend on. Hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. Cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. Drop the inheritance, use composition.

### 4. Spawn Both Sub-Agents in Parallel

Both sub-agents start from the base template [code-reviewer.md](code-reviewer.md) (read-only review, no sub-dispatch, "the spec is a vision document", "Declined to judge", severity calibration, output format), then add their axis brief below and restrict themselves to that axis. If a review package file exists (subagent-driven-development and executing-plans produce one), pass its path instead of raw git commands.

**Only one review seat available** (no subagent tool, or a per-task gate that must stay cheap): one reviewer fills code-reviewer.md and reports the two axes under separate `## Standards` and `## Spec` headings, each with its own verdict. Never merge them into one verdict.

**Standards sub-agent prompt** should include:

- The diff command and commit list (`git log $BASE_SHA..HEAD --oneline`, `git diff -U10 $BASE_SHA HEAD`)
- The list of standards-source files found in step 3, **plus the Fowler smell baseline pasted in full** (the sub-agent has no other access to it)
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any Fowler smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls. Documented-standard breaches can be hard; baseline smells are always judgement calls. A documented repo standard overrides the baseline. Skip anything tooling enforces. Note any refactoring opportunities for the implementer's next review cycle. Under 500 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list
- The path or contents of the spec/plan
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that was not asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate and Act

Present the two reports under `## Standards` and `## Spec` headings. Do NOT merge or rerank findings across axes.

End with:
- A one-line summary: total findings per axis, worst issue within each axis
- An overall verdict: Ready / With fixes / Not ready

**Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues and refactoring suggestions for the next code review cycle
- Push back if reviewer is wrong (with reasoning)

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll just review the diff myself" | You are the coordinator — reviewing inline burns the context window you need to keep driving the work. Dispatch reviewer sub-agents. |
| "The reviewer needs my whole session history" | Hand it precisely crafted context, never your session's history. That keeps the reviewer on the work product. |
| "It's simple, no need for a formal review" | Simple changes cascade into complex bugs. Review early. |
| "One reviewer is enough" | One reviewer cannot evaluate both spec and standards independently. The two axes need isolation to avoid masking. |

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Merge both reviewer findings into one verdict before presenting them separately
