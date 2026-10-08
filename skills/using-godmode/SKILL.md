---
name: using-godmode
description: Use when starting any conversation. This skill tells you how to find and use skills. It requires skill invocation before ANY response, including a clarifying question.
---

<SUBAGENT-STOP>
If you are a subagent with a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think that there is even a 1% chance that a skill applies to your work, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

You cannot negotiate this rule. You cannot find a reason to avoid it.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke each relevant or requested skill BEFORE any response or action.** This includes a clarifying question, an exploration of the codebase and a look at a file. If the skill is wrong for the situation, you do not have to use it.

**Before you enter plan mode:** if you did not brainstorm yet, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]". Follow the skill exactly. If the skill has a checklist, make one todo for each item.

## Skill Catalog

This skill set joins Superpowers (the autonomous pipeline) with the engineering and productivity skills of Matt Pocock (deep modules, grilling, domain modeling). The model can invoke each skill, unless the table says otherwise.

### Pipeline Skills (Superpowers core: they drive the full lifecycle)

| Situation | Skill |
|-----------|-------|
| The start of any build, feature or change | `godmode:brainstorming` |
| You have an approved spec and need an implementation plan | `godmode:writing-plans` |
| You execute a plan with independent tasks | `godmode:subagent-driven-development` |
| You execute a plan inline (no subagent tool) | `godmode:executing-plans` |
| You implement any feature or bugfix | `godmode:test-driven-development` |
| You find any bug, failure or unexpected behavior | `godmode:systematic-debugging` |
| You are about to say that work is complete | `godmode:verification-before-completion` |
| You request a code review | `godmode:requesting-code-review` |
| You receive a code review | `godmode:receiving-code-review` |
| You finish a development branch | `godmode:finishing-a-development-branch` |
| You work with git worktrees | `godmode:using-git-worktrees` |
| You dispatch parallel agents | `godmode:dispatching-parallel-agents` |
| You make or edit a skill | `godmode:writing-skills` |
| You diagnose a problem in a godmode session | `godmode:diagnosing-godmode` |

### Design and Requirements Skills (Matt Pocock: depth and precision)

| Situation | Skill |
|-----------|-------|
| A stress test of a plan, design or decision with relentless questions | `godmode:grilling` |
| The design or review of any module interface, seam or testability structure | `godmode:codebase-design` |
| Domain terminology, a new or changed CONTEXT.md, or an ADR | `godmode:domain-modeling` |
| Spike: an answer to a design or feasibility question with throwaway code | `godmode:prototype` |
| A structured spec from a resolved design | `godmode:to-spec` |
| Research of a factual question against primary sources | `godmode:research` |
| A scan of a codebase for architecture improvement opportunities | `godmode:improve-codebase-architecture` |
| A git merge or rebase conflict | `godmode:resolving-merge-conflicts` |
| A step that only a human can do (credentials, CI secrets, a dashboard, a one-off cutover) blocks you | `godmode:wizard` |
| You make or edit a skill, an agent instructions file (AGENTS.md or equivalent), or another document that an agent reads | `godmode:writing-for-agents` |
| The security pass of any code review, or a request to scan code for vulnerabilities, secrets or PHI/PII exposure | `godmode:vuln-scan` |
| A request to rewrite a text in STE (all godmode output follows STE by default) | `godmode:ste-writing` |

### Programmer Commands (user-invoked only)

These commands are tools of your human partner. The model never invokes them, and no skill calls them. When a command can help, tell your partner that it exists. Do not do its steps yourself.

| Command | When your partner types it |
|---------|----------------------------|
| `/wait-what` | Your last message was not clear. Explain it again with the missing context, in plain English, with CONTEXT.md terms |
| `/handoff` | The work must move to a new harness, a new directory, a colleague or a side fork (for example, a prototype detour) |
| `/grill-me` | A stateless grilling session with no repository. It writes no files |
| `/to-questionnaire` | A decision needs the knowledge of a different person. The command makes a questionnaire for that person |
| `/teach` | Learn a concept over several sessions. The command uses the directory as a teaching workspace |
| `/mr-full-review` | Only when your partner types the command: a full, read-only MR/PR review that it writes to `.scratch/` as a numbered round. Each other review request invokes `godmode:requesting-code-review`, also when the request names an MR or PR number |
| `/setup-godmode` | Install, update or remove godmode for one repository or for all repositories, and write the bootstrap |

## Skill Priority

When more than one skill applies, the process skills come first. They set the approach. Then the implementation skills do the work.

- "Let's build X" → `godmode:brainstorming` first, then the implementation skills.
- "Fix this bug" → `godmode:systematic-debugging` first, then the domain skills.
- "Design this module" → `godmode:codebase-design` + `godmode:domain-modeling` before any code.
- "Grill me on this plan" → `godmode:grilling` immediately.
- "Refactor / clean up / make this more testable" → `godmode:improve-codebase-architecture`.
- "Review this / review MR 46 / act as an independent reviewer" → invoke `godmode:requesting-code-review` (it runs `godmode:vuln-scan`). Knowledge of the review method does not replace the skill call.
- A merge or rebase conflict → `godmode:resolving-merge-conflicts` before all other work.

## Lifecycle Map

Superpowers drives the pipeline. At each stage, the pipeline skill requires the Matt Pocock engineering skill in the table. The engineering skill is not optional.

| Stage | Pipeline skill | Engineering skills that it must use |
|-------|----------------|------------------------------------|
| Understand the request | `godmode:brainstorming` | `godmode:grilling` for each clarifying question. `godmode:domain-modeling` when a term is fuzzy or a decision needs an ADR. `godmode:research` for facts |
| Feasibility spike | `godmode:brainstorming` (Spike path) | `godmode:prototype` |
| Design | `godmode:brainstorming` (Architectural path) | `godmode:codebase-design` for each module boundary and seam |
| Written spec | `godmode:brainstorming` | `godmode:to-spec` |
| Plan | `godmode:writing-plans` | `godmode:codebase-design` for file boundaries. A named seam for each task |
| Implement | `godmode:subagent-driven-development` or `godmode:executing-plans` | `godmode:test-driven-development` at the seam of the task. `godmode:research` for missing facts |
| Review | `godmode:requesting-code-review` | Two axes (Standards with the Fowler baseline, and Spec) and the `godmode:vuln-scan` security pass. Refactoring occurs here, not in TDD |
| Debug | `godmode:systematic-debugging` | The feedback loop comes first. If no correct seam exists, recommend `godmode:improve-codebase-architecture` |
| A step that only a human can do | `godmode:subagent-driven-development` or `godmode:executing-plans` | `godmode:wizard`. Then stop and give the script to the human |
| Integrate | `godmode:finishing-a-development-branch` | `godmode:resolving-merge-conflicts` |
| Improve structure | `godmode:improve-codebase-architecture` | `godmode:codebase-design`, `godmode:grilling`, `godmode:domain-modeling`. Then go back into `godmode:brainstorming` with the Grilling Summary |
| Write skills or agent docs | `godmode:writing-skills` | `godmode:writing-for-agents` |

Your human partner makes the precision decisions while they are present. These decisions are:

- the requirements (grilling)
- the test seams (the Bounded design or the Testing Decisions of the spec)
- the approvals of the spec and the plan
 After your partner approves the plan, all work continues without a stop and uses those decisions.

## Writing

Write all godmode output in STE (`godmode:ste-writing`): chat replies, reports, reviews, plans and commit messages. Use no semicolons. Keep each sentence at 25 words or fewer, in active voice, with the condition first. Use one command in each step. Keep quotes, code and logs unchanged.

## Red Flags

These thoughts mean STOP. You are looking for a reason to skip a rule:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | A question is a task. Look for a skill that applies. |
| "I need more context first" | Look for a skill BEFORE you ask a clarifying question. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Look for a skill first. |
| "I can check git/files quickly" | Files do not have the context of the conversation. Look for a skill that applies. |
| "Let me gather information first" | Skills tell you HOW to get information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills change. Read the current version. |
| "This doesn't count as a task" | An action is a task. Look for a skill that applies. |
| "The skill is overkill" | Simple work becomes complex. Use the skill. |
| "I'll just do this one thing first" | Look for a skill BEFORE you do anything. |
| "This feels productive" | Action without discipline wastes time. Skills prevent this. |
| "I know what that means" | Knowledge of a concept is not the use of the skill. Invoke the skill. |
| "They gave me the whole spec, so I can skip brainstorming" | A complete spec makes brainstorming fast (an empty frontier, a four-line design). It does not make brainstorming optional. Invoke it. Its approval gate still applies before any code. |
| "It's small and clear, I'll go straight to TDD" | TDD comes after the approval of the design. Each change to behavior starts in `godmode:brainstorming`. |
| "The design (or plan) is approved, I know TDD, I'll just write the test" | After the approval, the skills take the work, not your memory. Invoke `godmode:test-driven-development` before the first test. Invoke `godmode:verification-before-completion` before you say that you finished the work. This also applies inside `executing-plans` and `subagent-driven-development`. |
| "The grilling will slow things down" | Requirements without grilling cause rework. Always grill first. |
| "The design is obvious, no need for codebase-design" | An obvious design has seams that are not obvious. Look at them. |

## Platform Adaptation

Skills name actions, not tools: "read the file", "dispatch a subagent", "track tasks", "invoke the skill". For each action, use the tool that your environment gives. If an action has no equivalent (for example, no subagent tool), use the fallback that the skill gives. Most skills tell you what to do inline instead.

**Windows:** skills run helper scripts with `bash` (for example, `subagent-driven-development/scripts/*` and `executing-plans/scripts/*`). On Windows, a plain `bash` can start WSL (`C:\Windows\System32\bash.exe`). WSL cannot run these scripts from their Windows paths. Run the scripts with Git Bash instead: `& "C:\Program Files\Git\bin\bash.exe" <script> <args>`. If Git Bash is not installed, do the steps of the script by hand and ledger that you did them.

## User Instructions

User instructions have priority over skills, and skills have priority over default behavior. User instructions are the agent instructions files of the repository or the user (for example, AGENTS.md) and direct requests. Skip a skill workflow or an instruction only when your human partner tells you to skip it.
