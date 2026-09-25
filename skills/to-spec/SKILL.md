---
name: to-spec
description: Use when turning a resolved design into a structured written spec. Use after brainstorming's design has been approved, before invoking writing-plans. Do NOT interview the user; synthesize what you already discussed.
---

# To Spec

Take the current conversation context and codebase understanding and produce a structured spec. Do NOT interview the user; just synthesize what you already know. This skill runs at the end of the brainstorming architectural path, after design approval, as the final artifact before writing-plans.

## Cold Start

If no prior design conversation exists in this session (the user invoked this skill directly with no preceding brainstorm or grilling), do not synthesize from nothing. Instead:

1. Invoke `godmode:grilling` to reach shared understanding before writing the spec. The grilling session produces a Grilling Summary of settled decisions.
2. Once the grilling frontier is empty and the summary is confirmed, return to Step 1 of the Process below.

If a prior design conversation or grilling session already exists, proceed directly to the Process.

## Process

1. **Explore the repo** to understand the current state of the codebase, if you have not already. Use the project's domain glossary vocabulary (CONTEXT.md) throughout the spec, and respect any ADRs in the area you are touching. Use `godmode:domain-modeling` to sharpen any fuzzy terms before writing.

2. **Sketch out the seams** at which you are going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better. Consult `godmode:codebase-design` for seam vocabulary if needed.

   Check with your human partner that these seams match their expectations.

3. **Write the spec** using the template below. Save it to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and commit.

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
