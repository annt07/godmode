---
name: using-godmode
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Catalog

This combined skill set merges Superpowers (autonomous pipeline driver) with Matt Pocock's engineering and productivity skills (deep modules, grilling, domain modeling). Every skill is model-invocable unless noted.

### Pipeline Skills (Superpowers core — drive the full lifecycle)

| Situation | Skill |
|-----------|-------|
| Starting any build/feature/change | `godmode:brainstorming` |
| Have approved spec, need implementation plan | `godmode:writing-plans` |
| Executing plan with independent tasks | `godmode:subagent-driven-development` |
| Executing plan inline (no subagent tool) | `godmode:executing-plans` |
| Implementing any feature or bugfix | `godmode:test-driven-development` |
| Encountering any bug, failure, unexpected behavior | `godmode:systematic-debugging` |
| About to claim work is complete | `godmode:verification-before-completion` |
| Requesting a code review | `godmode:requesting-code-review` |
| Receiving a code review | `godmode:receiving-code-review` |
| Finishing a development branch | `godmode:finishing-a-development-branch` |
| Working with git worktrees | `godmode:using-git-worktrees` |
| Dispatching parallel agents | `godmode:dispatching-parallel-agents` |
| Creating or editing skills | `godmode:writing-skills` |
| Diagnosing a godmode session problem | `godmode:diagnosing-godmode` |

### Design and Requirements Skills (Matt Pocock — depth and precision)

| Situation | Skill |
|-----------|-------|
| Stress-testing a plan, design, or decision with relentless questions | `godmode:grilling` |
| Designing or reviewing any module interface, seam, or testability structure | `godmode:codebase-design` |
| Resolving domain terminology, creating/editing CONTEXT.md, recording an ADR | `godmode:domain-modeling` |
| Spike: answering a design or feasibility question with throwaway code | `godmode:prototype` |
| Writing a structured spec from a resolved design | `godmode:to-spec` |
| Researching a factual question against primary sources | `godmode:research` |
| Scanning a codebase for architecture improvement opportunities | `godmode:improve-codebase-architecture` |
| Encountering a git merge or rebase conflict | `godmode:resolving-merge-conflicts` |
| Blocked on a step only a human can do (credentials, CI secrets, a dashboard, a one-off cutover) | `godmode:wizard` |
| Creating or editing a skill, AGENTS.md, CLAUDE.md, or another agent-read document | `godmode:writing-for-agents` |

### Programmer Commands (Matt Pocock, user-invoked only)

These are your human partner's tools. They are never model-invoked and no skill calls them. When one would help, tell your partner it exists; do not run its steps yourself.

| Command | When your partner types it |
|---------|----------------------------|
| `/wait-what` | Your last message did not land: re-pitch it with the missing context, in plain English, using CONTEXT.md terms |
| `/handoff` | The work has to travel (new harness, new directory, a colleague, or a side fork such as a prototype detour) |
| `/grill-me` | A stateless grilling session with no repo under it: writes no files |
| `/to-questionnaire` | A decision needs someone else's knowledge: turns it into a questionnaire for them |
| `/teach` | Learn a concept over several sessions, using the directory as a teaching workspace |

## Skill Priority

When multiple skills apply, process skills come first — they set the approach, then implementation skills carry it out.

- "Let's build X" → `godmode:brainstorming` first, then implementation skills.
- "Fix this bug" → `godmode:systematic-debugging` first, then domain skills.
- "Design this module" → `godmode:codebase-design` + `godmode:domain-modeling` before any code.
- "Grill me on this plan" → `godmode:grilling` immediately.
- "Refactor / clean up / make this more testable" → `godmode:improve-codebase-architecture`.
- Merge or rebase conflict → `godmode:resolving-merge-conflicts` before anything else.

## Lifecycle Map

Superpowers drives the pipeline. At each stage, the Matt Pocock engineering skill listed is not optional: the pipeline skill requires it.

| Stage | Pipeline skill | Engineering skills it must pull in |
|-------|----------------|------------------------------------|
| Understand the request | `godmode:brainstorming` | `godmode:grilling` for every clarifying question; `godmode:domain-modeling` when a term is fuzzy or a decision is ADR-worthy; `godmode:research` for facts |
| Feasibility spike | `godmode:brainstorming` (Spike path) | `godmode:prototype` |
| Design | `godmode:brainstorming` (Architectural path) | `godmode:codebase-design` for every module boundary and seam |
| Written spec | `godmode:brainstorming` | `godmode:to-spec` |
| Plan | `godmode:writing-plans` | `godmode:codebase-design` for file boundaries; a named seam per task |
| Implement | `godmode:subagent-driven-development` or `godmode:executing-plans` | `godmode:test-driven-development` at the task's seam; `godmode:research` on factual gaps |
| Review | `godmode:requesting-code-review` | Two axes (Standards with the Fowler baseline, Spec); refactoring happens here, not in TDD |
| Debug | `godmode:systematic-debugging` | Feedback loop first; no correct seam means recommend `godmode:improve-codebase-architecture` |
| Blocked on a human-only step | `godmode:subagent-driven-development` or `godmode:executing-plans` | `godmode:wizard`, then stop and hand over the script |
| Integrate | `godmode:finishing-a-development-branch` | `godmode:resolving-merge-conflicts` |
| Improve structure | `godmode:improve-codebase-architecture` | `godmode:codebase-design`, `godmode:grilling`, `godmode:domain-modeling`, then back into `godmode:brainstorming` with the Grilling Summary |
| Write skills or agent docs | `godmode:writing-skills` | `godmode:writing-for-agents` |

The precision decisions stay with your human partner and are made while they are present: requirements (grilling), test seams (the Bounded design or the spec's Testing Decisions), and the spec and plan approvals. Everything after the plan is approved runs without stopping and reuses those decisions.

## Red Flags

These thoughts mean STOP — you are rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept is not the same as using the skill. Invoke it. |
| "They gave me the whole spec, so I can skip brainstorming" | A complete spec makes brainstorming fast (empty frontier, a four-line design), not optional. Invoke it: its approval gate still applies before any code. |
| "It's small and clear, I'll go straight to TDD" | TDD comes after the design is approved. Any change to behavior starts in `godmode:brainstorming`. |
| "The design (or plan) is approved, I know TDD, I'll just write the test" | Approval hands off to skills, not to memory. Invoke `godmode:test-driven-development` before the first test and `godmode:verification-before-completion` before saying it's done, including inside `executing-plans` and `subagent-driven-development`. |
| "The grilling will slow things down" | Ungrilled requirements cause rework. Grill first, always. |
| "The design is obvious, no need for codebase-design" | Obvious designs have non-obvious seams. Check. |

## Platform Adaptation

If your harness appears here, read its reference file for special instructions (tool names, subagent dispatch, where skills live):

- Claude Code: `references/claude-code-tools.md`
- Codex: `references/codex-tools.md`
- Gemini CLI: `references/gemini-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`
- Hermes Agent: `references/hermes-tools.md`
- Muse: `references/muse-tools.md`

**Windows:** skills run helper scripts with `bash` (for example `subagent-driven-development/scripts/*`, `executing-plans/scripts/*`). A plain `bash` on Windows may resolve to WSL (`C:\Windows\System32\bash.exe`), which cannot run these scripts from their Windows paths. Run them with Git Bash instead: `& "C:\Program Files\Git\bin\bash.exe" <script> <args>`. If Git Bash is missing, do the script's steps by hand and ledger that you did.

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc., direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.
