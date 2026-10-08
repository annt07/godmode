---
name: requesting-code-review
description: Use when completing tasks, when implementing major features, or before merging. It verifies that the work meets requirements and obeys the coding standards.
---

# Requesting Code Review

Dispatch code reviewer subagents to find issues before they spread. This review runs on **two independent axes** at the same time:

- **Standards axis**: Does the code obey the documented coding standards of this repository and a fixed baseline of code quality smells?
- **Spec axis**: Does the code correctly implement what the source spec or plan asked for?

A change can pass one axis and fail the other. Separate reports prevent one axis from hiding the other.

**Core principle:** Review early, and review often. The Standards axis is also where refactoring opportunities show. They do not show during the TDD implementation loop.

## When to Request Review

**Mandatory:**
- After each task in subagent-driven development
- After you complete a major feature
- Before merge to main

**Optional but valuable:**
- When you are stuck (fresh perspective)
- Before refactoring (baseline check)
- After you fix a complex bug

## How to Request

### 1. Pin the Fixed Point

Get the range:
```bash
BASE_SHA=$(git merge-base origin/main HEAD)  # or git rev-parse HEAD~1 for task reviews
HEAD_SHA=$(git rev-parse HEAD)
```

Before you dispatch, verify that the diff is not empty: `git diff --stat $BASE_SHA..$HEAD_SHA`

### 2. Identify the Spec Source

Look for the source spec in this order:
1. The plan file that subagent-driven-development uses for this task
2. The spec file in `docs/godmode/specs/` that is the source of the plan
3. If you find nothing, give the task text directly to the Spec subagent

### 3. Identify Standards Sources

Use each file in the repository that documents how to write code (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `CONTEXT.md`).

In addition to the documented standards of the repository, the Standards axis always uses the **Fowler smell baseline** below. Two rules control it:

- **The repo overrides.** A documented standard of the repository always wins. If it endorses something that the baseline would flag, do not report the smell.
- **Always a judgement call.** Each smell is a labeled heuristic, never a hard violation. Skip each item that tooling already enforces.

**Fowler Code Smell Baseline**: [`fowler-smells.md`](fowler-smells.md) in this directory gives the full definition. Give its full contents to the Standards subagent. Summary:

- **Mysterious Name**: A function, variable or type whose name does not show what it does or holds. Rename it. If no honest name comes, the design is not clear.
- **Duplicated Code**: The same logic shape occurs in more than one hunk or file. Extract the shared shape, and call it from both.
- **Feature Envy**: A method that uses the data of a different object more than its own data. Move the method to the data that it envies.
- **Data Clumps**: The same few fields or parameters go together again and again (a type that wants to exist). Put them into one type.
- **Primitive Obsession**: A primitive or string that stands in for a domain concept that should have its own type. Give the concept its own small type.
- **Repeated Switches**: The same switch/if-cascade on the same type occurs again in the change. Replace it with polymorphism, or with one map that both sites share.
- **Shotgun Surgery**: One logical change causes scattered edits in many files. Put the parts that change together into one module.
- **Divergent Change**: One file or module gets edits for several unrelated reasons. Split it, so that each module changes for one reason.
- **Speculative Generality**: Abstraction, parameters or hooks for needs that the spec does not have. Remove it. Inline it again until a real need occurs.
- **Message Chains**: Long `a.b().c().d()` navigation that the caller should not depend on. Hide the navigation behind one method on the first object.
- **Middle Man**: A class or function that mostly only sends calls to a different target. Remove it, and call the real target directly.
- **Refused Bequest**: A subclass or implementer that ignores or overrides most of what it inherits. Remove the inheritance, and use composition.

### 4. Spawn Both Sub-Agents in Parallel

Both subagents start from the base template [code-reviewer.md](code-reviewer.md) (read-only review, no sub-dispatch, "the spec is a vision document", "Declined to judge", severity calibration, output format). Each subagent then adds its axis brief below and stays on that axis only. If a review package file exists (subagent-driven-development and executing-plans make one), give its path instead of raw git commands.

**Only one review seat available** (no subagent tool, or a per-task gate that must stay cheap): One reviewer fills code-reviewer.md. It reports the two axes under separate `## Standards` and `## Spec` headings, each with its own verdict. Never merge them into one verdict.

**Standards sub-agent prompt** should include:

- The diff command and commit list (`git log $BASE_SHA..HEAD --oneline`, `git diff -U10 $BASE_SHA HEAD`)
- The list of standards source files from step 3, **and the full Fowler smell baseline pasted in** (the subagent has no other access to it)
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any Fowler smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls. Documented-standard breaches can be hard; baseline smells are always judgement calls. A documented repo standard overrides the baseline. Skip anything tooling enforces. Note any refactoring opportunities for the implementer's next review cycle. Under 500 words."

**Spec sub-agent prompt** should include:

- The diff command and commit list
- The path or contents of the spec/plan
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that was not asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec subagent and write this in the final report.

### 5. Security Pass (required)

**REQUIRED SUB-SKILL:** Run `godmode:vuln-scan` in **review mode** on the same `$BASE_SHA..$HEAD_SHA` range, together with the two axis reviewers. If you have a subagent tool, run it as a third parallel subagent. If not, run it yourself after them. Review mode never stops to ask for authorization or for threat-model refinement. It writes its artifacts under `.godmode/security/`, not into the source tree.

It runs on each review that this skill does. This includes "just a quick review" and changes that do not look related to security. The scan covers only the diff, so it is cheap when there is nothing to find. There is one exception: the per-task gate in `subagent-driven-development` runs it only for tasks that touch security-sensitive code. The final whole-branch review of `subagent-driven-development` and `executing-plans` always runs it.

### 6. Aggregate and Act

Show the three reports under `## Standards`, `## Spec` and `## Security` headings. Do NOT merge findings across them, and do NOT rank them again across headings. Critical and high security findings are blocking (Important or Critical). Medium and low security findings are Minor.

End with:
- A one-line summary: the total findings for each heading, and the worst issue in each
- An overall verdict: Ready / With fixes / Not ready

**Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before you continue
- Write down Minor issues and refactoring suggestions for the next code review cycle
- If the reviewer is wrong, disagree (with reasons)

Write the review report in descriptive STE (`godmode:ste-writing`). Tell each reviewer subagent to do the same.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll just review the diff myself" | You are the coordinator. An inline review uses the context window that you need to continue the work. Dispatch reviewer subagents. |
| "The reviewer needs my whole session history" | Give it a precisely made context, never the history of your session. That keeps the reviewer on the work product. |
| "It's simple, no need for a formal review" | Simple changes grow into complex bugs. Review early. |
| "One reviewer is enough" | One reviewer cannot evaluate both spec and standards independently. The two axes need isolation, so that one does not hide the other. |
| "This change isn't security-related, skip vuln-scan" | Injection, leaked PHI and secrets in logs come in "harmless" changes. The scan covers only the diff and is cheap. It always runs. |
| "The repo is internal, so security findings are Minor" | Internal services also hold credentials and PHI. Grade by the severity from vuln-scan, not by where the code runs. |

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Continue with Important issues that are not fixed
- Merge the findings of both reviewers into one verdict before you show them separately
- Finish a review without the `## Security` section from `godmode:vuln-scan`
