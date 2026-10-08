---
name: to-spec
description: Use when turning a resolved design into a structured written spec. Use it after the user approved the brainstorming design, before you invoke writing-plans. Do NOT interview the user. Make the spec from what you already discussed.
---

# To Spec

Use the context of the current conversation and your understanding of the codebase to write a structured spec. Do NOT interview the user. Make the spec only from what you already know. This skill runs at the end of the architectural path of brainstorming, after the approval of the design. The spec is the last artifact before writing-plans.

## Cold Start

Sometimes no design conversation occurred in this session before (the user invoked this skill directly, with no brainstorm or grilling first). Then do not make a spec from nothing. Do these steps instead:

1. Invoke `godmode:grilling` to reach shared understanding before you write the spec. The grilling session gives a Grilling Summary of the settled decisions.
2. When the grilling frontier is empty and the user approves the summary, go back to Step 1 of the Process below.

If a design conversation or a grilling session already exists, go directly to the Process.

## Process

1. **Explore the repository** to understand the current state of the codebase, if you did not do this already. Use the vocabulary of the project glossary (CONTEXT.md) in all of the spec. Obey each ADR in the area that you change. Before you write, use `godmode:domain-modeling` to make each fuzzy term clear.

2. **Sketch the seams** where you will test the feature. Prefer existing seams to new seams. Use the highest possible seam. If you need new seams, propose them at the highest possible point. Fewer seams across the codebase are better. If you need the seam vocabulary, use `godmode:codebase-design`.

   Ask your human partner whether these seams agree with what they expect. At this point, you and your partner agree the seams. After your partner approves the spec, the plan copies the seams into the "Seam under test" of each task. The execution then uses them without a new question. Record the agreed seams in the Testing Decisions of the spec.

3. **Write the spec** with the template below. Save it to `docs/godmode/specs/YYYY-MM-DD-<topic>-design.md` and commit it.
4. **Lint the spec.** Write the spec in descriptive STE (`godmode:ste-writing`). Run `python <ste-writing>/scripts/ste-lint.py --glossary <ste-writing>/glossary.md <file>`, where `<ste-writing>` is the folder of the `godmode:ste-writing` skill. Fix each hard finding. Then commit the fixes.

---

## Spec Template

```markdown
## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list of user stories. Each in the format:

1. As a <actor>, I want a <feature>, so that <benefit>

This list should be extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built or modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts only.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which seams will be tested
- Prior art for the tests (similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.
```
