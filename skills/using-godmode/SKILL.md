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

## Skill Priority

When multiple skills apply, process skills come first — they set the approach, then implementation skills carry it out.

- "Let's build X" → `godmode:brainstorming` first, then implementation skills.
- "Fix this bug" → `godmode:systematic-debugging` first, then domain skills.
- "Design this module" → `godmode:codebase-design` + `godmode:domain-modeling` before any code.
- "Grill me on this plan" → `godmode:grilling` immediately.

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
| "I know what that means" | Knowing the concept is not the same as using the skill. Invoke it. |
| "The grilling will slow things down" | Ungrilled requirements cause rework. Grill first, always. |
| "The design is obvious, no need for codebase-design" | Obvious designs have non-obvious seams. Check. |

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc., direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.
