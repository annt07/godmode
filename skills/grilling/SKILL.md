---
name: grilling
description: Use when clarifying requirements, stress-testing a plan or design, or resolving decision dependencies. Use it inside the clarifying-questions step of brainstorming. Also use it when you must walk a design tree to reach shared understanding.
---

# Grilling

Ask questions relentlessly until you and your human partner reach a shared understanding. Show the work as a **design tree**: each decision has branches, which are the decisions that depend on it.

Work through the tree in **rounds**. The **frontier** is each decision whose prerequisites are already settled. These are the questions that you can ask *now*, without a guess about answers that you did not hear yet. Ask the full frontier in one round. Give each question a number and your recommended answer. Then wait for the answers of your human partner before the next round.

Use this format for a round:

```
❓ **Q1** - **<question title>**: <question body>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body>

➡️ <your recommended answer>
```

Each round of answers changes the tree. Settled decisions move the frontier out, and the questions that depended on them become open. Find the new frontier and ask the next round. A question can depend on a different question that is still open in this round. That question goes into a *later* round, not this round.

**To find facts is your job, never the job of your human partner.** A frontier question can need a fact from the environment (filesystem, tools, existing code, docs). Then dispatch a subagent to find it with `godmode:research`. Do not ask your partner for anything that you can find yourself. Do not wait for the subagent. A running exploration is a prerequisite that is not settled. Thus only the questions that depend on it wait for the report of the subagent. Ask the remaining questions of the frontier now. The *decisions* belong to your partner. Ask your partner each decision and wait. A decision can need knowledge that neither of you has (a different team, a stakeholder, a vendor). Then mark it Open in the summary. Tell your partner that they can run `/to-questionnaire` to get the answer. Continue with the remaining questions of the frontier.

**Write the docs during the session.** An answer can settle the meaning of a domain term. It can also settle a decision that is hard to reverse, surprising without context and the result of a real trade-off. Then invoke `godmode:domain-modeling` immediately: update CONTEXT.md inline and offer the ADR. Do not keep these updates for the end of the session. When a question is about a module boundary or the location of a test seam, show the options with the vocabulary of `godmode:codebase-design`.

The session is complete when the frontier is empty. Then you visited each branch of the design tree, and you assumed nothing silently. Do not act on the result until your human partner agrees that you reached a shared understanding.

## Completion Handoff

When the frontier is empty and your human partner agrees to the shared understanding, write a **Grilling Summary**. Write it before you ask what comes next:

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

Then ask: "What would you like to do next?" Do not assume the next step. Your partner can want a spec, a prototype, a plan, or only a record of the decisions.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I can guess this answer" | Guesses become bugs. Ask. |
| "This question depends on too many things" | Show the dependencies. Ask what you can ask now, and keep the rest for later. |
| "One question at a time is enough" | The frontier can have three settled questions. Ask all three. |
| "We've covered the main points" | The frontier is empty or it is not. Look at each branch. |
| "I'll resolve this during implementation" | An assumption that you resolve during implementation is a bug that review finds. |
| "My recommended answer is obviously right" | Give it, but wait until your partner approves it. Obvious answers are often wrong. |
| "The user seems sure, so I don't need to grill" | Confidence is not shared understanding. Grill. |
| "I'll just write the spec now and grill later" | Grilling shows what goes in the spec. Grill first. |
| "This is a small decision, not worth a round" | Small decisions add up to large misalignments. Ask each branch that is not settled. |
| "For anything they skip, I'll take my recommendation" | Silence is not a decision. A skipped question stays open and comes back in the next round. Only an explicit "go with your recommendations" settles it. |
| "I'll ask everything now to save a round" | A question can depend on a different open question (purpose drives scope, scope drives testing). That question waits for the next round. If you ask it now, your partner answers from a guess. |
