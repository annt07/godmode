---
name: grilling
description: Use when clarifying requirements, stress-testing a plan or design, or resolving decision dependencies. Use inside brainstorming's clarifying-questions step, and whenever a design tree needs walking to reach shared understanding.
---

# Grilling

Interview relentlessly until you reach a shared understanding. Map the work as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for your human partner's answers before the next round.

Format a round like this:

```
❓ **Q1** - **<question title>**: <question body>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body>

➡️ <your recommended answer>
```

Each round of answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a *later* round, not this one.

**Finding facts is your job, never your human partner's.** When a frontier question needs a fact from the environment (filesystem, tools, existing code, docs), dispatch a sub-agent to find it via `godmode:research`; don't ask your partner for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The *decisions* are your partner's: put each to them and wait. When a decision needs knowledge neither of you holds (another team, a stakeholder, a vendor), mark it Open in the summary and tell your partner they can run `/to-questionnaire` to get it answered; continue with the rest of the frontier.

**Write the docs as you go.** When an answer pins down a domain term, or settles a decision that is hard to reverse, surprising without context, and the result of a real trade-off, invoke `godmode:domain-modeling` right then: update CONTEXT.md inline and offer the ADR. Do not batch this to the end of the session. When a question is about a module boundary or where a test seam goes, frame the options with `godmode:codebase-design` vocabulary.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until your human partner confirms you have reached a shared understanding.

## Completion Handoff

When the frontier is empty and your human partner confirms shared understanding, produce a **Grilling Summary** before asking what comes next:

```
## Grilling Summary

Settled decisions:
1. [decision]: [what was agreed]
2. [decision]: [what was agreed]
...

Constraints and non-negotiables:
- [constraint]: [reason]

Open items (deferred by mutual agreement):
- [item]: [why deferred]
```

Then ask: "What would you like to do next?" Do not assume the next step — your partner may want to proceed to a spec, a prototype, a plan, or simply record the decisions.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I can guess this answer" | Guesses become bugs. Ask. |
| "This question depends on too many things" | Map the dependencies; ask what you can now, defer the rest. |
| "One question at a time is enough" | The frontier may have three settled questions. Ask all three. |
| "We've covered the main points" | The frontier is empty or it isn't. Check every branch. |
| "I'll resolve this during implementation" | Assumptions resolved during implementation are bugs discovered in review. |
| "My recommended answer is obviously right" | State it, but wait for confirmation. Obvious answers are often wrong. |
| "The user seems sure, so I don't need to grill" | Confidence is not shared understanding. Grill anyway. |
| "I'll just write the spec now and grill later" | Grilling reveals what goes in the spec. Grill first. |
| "This is a small decision, not worth a round" | Small decisions accumulate into large misalignments. Every unsettled branch gets asked. |
| "For anything they skip, I'll take my recommendation" | Silence is not a decision. A skipped question stays open and comes back next round. Only an explicit "go with your recommendations" settles it. |
| "I'll ask everything now to save a round" | A question whose answer depends on another open question (purpose drives scope, scope drives testing) waits for the next round. Asking it now makes your partner answer on a guess. |
